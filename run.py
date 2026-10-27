"""OmniVoice runner for Rupee Math narration tests (CPU, GitHub Actions).

  python run.py plan   --job jobs/X.json                      -> prints the shard matrix (JSON)
  python run.py design --job jobs/X.json --out out/design      -> designed reference voices (if a variant has "design")
  python run.py gen    --job jobs/X.json --variant C --shard 0 --nshards 3 --out out/gen [--design out/design]
  python run.py merge  --job jobs/X.json --inp out/all --out results

Every line gets `takes` generations (seeds 1..N). Whisper transcribes each take; the take with the lowest
word error rate wins (ties: the one closest to the median duration of the takes). All takes are kept so a
human can overrule the pick.
"""
import argparse, json, os, re, sys, time, glob, shutil

TAG_RE = re.compile(r"\[[^\[\]]*\]")


def plain(text):
    """Text without non-verbal tags / CMU overrides, for the ASR check."""
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", text)).strip()


def norm_words(s):
    s = s.lower().replace("%", " percent").replace("-", " ")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    return s.split()


def wer(ref, hyp):
    import jiwer
    r, h = " ".join(norm_words(ref)), " ".join(norm_words(hyp))
    return jiwer.wer(r, h) if r else 0.0


def load_job(path):
    job = json.load(open(path))
    job.setdefault("takes", 2); job.setdefault("gen", {})
    return job


def line_text(line, var):
    """A line's text for a variant: per-variant override, else the variant's text_key, else plain."""
    t = line.get("text", {})
    if isinstance(t, str): return t
    return t.get(var["name"]) or t.get(var.get("text_key", "plain")) or line["plain"]


# ---------------------------------------------------------------- model
_model = None
def model():
    global _model
    if _model is None:
        import torch
        from omnivoice import OmniVoice
        torch.set_num_threads(os.cpu_count() or 4)
        t0 = time.time()
        _model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
        print(f"model loaded in {time.time()-t0:.0f}s", flush=True)
    return _model

_asr = None
def asr(wav, sr):
    global _asr
    if _asr is None:
        from transformers import pipeline
        _asr = pipeline("automatic-speech-recognition", model="openai/whisper-small.en", device="cpu")
    import numpy as np, librosa
    y = librosa.resample(np.asarray(wav, dtype=np.float32), orig_sr=sr, target_sr=16000)
    return _asr({"raw": y, "sampling_rate": 16000})["text"].strip()


def seed(n):
    from omnivoice.utils.common import fix_random_seed
    fix_random_seed(n)


def best_of(takes):
    """takes: list of dicts with wer, dur. Lowest WER, then closest to median duration."""
    import statistics
    med = statistics.median(t["dur"] for t in takes)
    return min(takes, key=lambda t: (round(t["wer"], 3), abs(t["dur"] - med)))


def generate_takes(text, n, out_stub, check_text, **kw):
    import soundfile as sf
    m = model(); sr = m.sampling_rate; takes = []
    for k in range(1, n + 1):
        seed(1000 * k + 7)
        t0 = time.time()
        y = m.generate(text=text, language="English", **kw)[0]
        el = time.time() - t0
        f = f"{out_stub}_t{k}.wav"; sf.write(f, y, sr)
        hyp = asr(y, sr)
        tk = dict(file=os.path.basename(f), take=k, dur=round(len(y) / sr, 2), secs=round(el, 1), asr=hyp, wer=round(wer(check_text, hyp), 3))
        print(f"  take {k}: {tk['dur']}s audio in {el:.0f}s  WER {tk['wer']}  | {hyp}", flush=True)
        takes.append(tk)
    return takes


def gen_kwargs(job, var, line=None):
    g = dict(job["gen"]); g.update(var.get("gen", {}))
    if line and line.get("speed", {}).get(var["name"]) is not None: g["speed"] = line["speed"][var["name"]]
    if var.get("instruct"): g["instruct"] = var["instruct"]
    return g


# ---------------------------------------------------------------- commands
def variants(job):
    out = []
    for name, v in job["variants"].items():
        v = dict(v); v["name"] = name; out.append(v)
    return out


def cmd_plan(a):
    job = load_job(a.job)
    want = [x.strip() for x in (a.variants or "").split(",") if x.strip()]
    mat = [{"variant": v["name"], "shard": s, "nshards": a.nshards}
           for v in variants(job) if not want or v["name"] in want for s in range(a.nshards)]
    print(json.dumps({"include": mat}))


def cmd_design(a):
    """Variants with "design": make the speaker from the instruct alone, keep the best take as the clone reference."""
    job = load_job(a.job); os.makedirs(a.out, exist_ok=True); report = {}
    for v in variants(job):
        d = v.get("design")
        if not d: continue
        print(f"design {v['name']}: {d['instruct']}", flush=True)
        takes = generate_takes(d["text"], d.get("takes", 3), os.path.join(a.out, v["name"]), d["text"],
                               instruct=d["instruct"], **job["gen"])
        b = best_of(takes)
        shutil.copy(os.path.join(a.out, b["file"]), os.path.join(a.out, f"{v['name']}_ref.wav"))
        report[v["name"]] = dict(text=d["text"], pick=b["file"], takes=takes)
    json.dump(report, open(os.path.join(a.out, "design.json"), "w"), indent=1)


def ref_for(job, var, line, design_dir):
    refs = json.load(open("refs/refs.json"))
    if var.get("design"):
        rep = json.load(open(os.path.join(design_dir, "design.json")))
        return os.path.join(design_dir, f"{var['name']}_ref.wav"), rep[var["name"]]["text"]
    r = var.get("ref")
    if r == "per_line": r = line["ref"]
    if not r: return None, None
    return f"refs/{r}.wav", refs[r]


def cmd_gen(a):
    job = load_job(a.job); var = next(v for v in variants(job) if v["name"] == a.variant)
    lines = job["lines"][a.shard::a.nshards]
    os.makedirs(a.out, exist_ok=True); m = model(); prompts = {}; res = []
    for line in lines:
        text = line_text(line, var)
        ref, rtext = ref_for(job, var, line, a.design)
        kw = gen_kwargs(job, var, line)
        if ref:
            if ref not in prompts: prompts[ref] = m.create_voice_clone_prompt(ref_audio=ref, ref_text=rtext)
            kw["voice_clone_prompt"] = prompts[ref]
        print(f"[{var['name']}] {line['id']}  ref={ref}  text={text}", flush=True)
        takes = generate_takes(text, job["takes"], os.path.join(a.out, f"{var['name']}__{line['id']}"), line["plain"], **kw)
        b = best_of(takes)
        res.append(dict(variant=var["name"], id=line["id"], text=text, ref=ref, pick=b["file"], takes=takes))
    json.dump(res, open(os.path.join(a.out, f"report_{var['name']}_{a.shard}.json"), "w"), indent=1)


def cmd_merge(a):
    """Collect every shard: results/<variant>/<line id>.wav (the pick) + takes/ + report.md + concatenated preview per variant."""
    import numpy as np, soundfile as sf
    job = load_job(a.job); os.makedirs(a.out, exist_ok=True)
    reps = []
    for f in glob.glob(os.path.join(a.inp, "**", "report_*.json"), recursive=True): reps += json.load(open(f))
    files = {os.path.basename(f): f for f in glob.glob(os.path.join(a.inp, "**", "*.wav"), recursive=True)}
    order = [l["id"] for l in job["lines"]]
    md = [f"# {job['name']}: OmniVoice takes\n", "Pick = lowest Whisper word error rate, then closest to the median length.\n"]
    for d in glob.glob(os.path.join(a.inp, "**", "design.json"), recursive=True):
        for vn, r in json.load(open(d)).items():
            md.append(f"\n## Designed voice {vn}: pick {r['pick']}\n")
            for t in r["takes"]: md.append(f"- {t['file']}: {t['dur']} s, WER {t['wer']}: {t['asr']}")
            os.makedirs(os.path.join(a.out, "design"), exist_ok=True)
            for t in r["takes"]: shutil.copy(files[t["file"]], os.path.join(a.out, "design", t["file"]))
    for v in variants(job):
        rows = sorted([r for r in reps if r["variant"] == v["name"]], key=lambda r: order.index(r["id"]))
        if not rows: continue
        vd = os.path.join(a.out, v["name"]); os.makedirs(os.path.join(vd, "takes"), exist_ok=True)
        md.append(f"\n## Variant {v['name']}: {v.get('label', '')}\n")
        prev, sr = [], None
        for r in rows:
            for t in r["takes"]: shutil.copy(files[t["file"]], os.path.join(vd, "takes", t["file"]))
            shutil.copy(files[r["pick"]], os.path.join(vd, f"{r['id']}.wav"))
            y, sr = sf.read(files[r["pick"]]); prev += [y, np.zeros(int(0.3 * sr))]
            md.append(f"- **{r['id']}** pick {r['pick']} · text: `{r['text']}`")
            for t in r["takes"]: md.append(f"  - t{t['take']}: {t['dur']} s (gen {t['secs']} s), WER {t['wer']}: {t['asr']}")
        sf.write(os.path.join(a.out, f"preview_{v['name']}.wav"), np.concatenate(prev), sr)
    open(os.path.join(a.out, "report.md"), "w").write("\n".join(md) + "\n")
    json.dump(reps, open(os.path.join(a.out, "report.json"), "w"), indent=1)
    print("\n".join(md))


if __name__ == "__main__":
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    for name in ["plan", "design", "gen", "merge"]:
        s = sub.add_parser(name); s.add_argument("--job", required=True)
        if name == "plan": s.add_argument("--variants", default=""); s.add_argument("--nshards", type=int, default=3)
        if name == "design": s.add_argument("--out", default="out/design")
        if name == "gen":
            s.add_argument("--variant", required=True); s.add_argument("--shard", type=int, default=0)
            s.add_argument("--nshards", type=int, default=1); s.add_argument("--out", default="out/gen"); s.add_argument("--design", default="out/design")
        if name == "merge": s.add_argument("--inp", default="out/all"); s.add_argument("--out", default="results")
    a = p.parse_args()
    {"plan": cmd_plan, "design": cmd_design, "gen": cmd_gen, "merge": cmd_merge}[a.cmd](a)
