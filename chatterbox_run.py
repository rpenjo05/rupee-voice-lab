"""Chatterbox (Resemble AI, MIT) voice takes on CPU.

  python chatterbox_run.py gen   --job jobs/<x>.json --shard K --nshards N --out out/gen
  python chatterbox_run.py merge --job jobs/<x>.json --inp out/all --out results

Job format:
  {"name": ..., "takes": 3, "defaults": {"ref": "heart_punchy", "exaggeration": 0.6, "cfg_weight": 0.4, "temperature": 0.8},
   "lines": [{"id": "hook_0", "text": "...", "ref": "heart_punchy", "exaggeration": 0.7}, ...]}
Each line gets `takes` seeds; Whisper small.en scores each take against the text and the best one is kept as <id>.wav.
"""
import argparse, json, os, re, glob, shutil, time

def _num(m):
    try:
        from num2words import num2words
        return " " + num2words(float(m.group(0)) if "." in m.group(0) else int(m.group(0))) + " "
    except Exception:
        return m.group(0)

def norm_words(s):
    s = re.sub(r"\d+(\.\d+)?", _num, s.replace(",", "").replace("%", " percent"))
    s = s.lower().replace("-", " ").replace(" and ", " ")
    return re.sub(r"[^a-z0-9' ]+", " ", s).split()

def wer(ref, hyp):
    r, h = norm_words(ref), norm_words(hyp)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev, d[j] = d[j], cur
    return d[len(h)] / max(1, len(r))

def load(path):
    return json.load(open(path))

def cmd_gen(a):
    import torch, torchaudio
    from chatterbox.tts import ChatterboxTTS
    from transformers import pipeline
    torch.set_num_threads(os.cpu_count() or 4)
    job = load(a.job); dflt = job.get("defaults", {})
    model = ChatterboxTTS.from_pretrained(device="cpu")
    asr = pipeline("automatic-speech-recognition", model="openai/whisper-small.en", device="cpu")
    os.makedirs(a.out, exist_ok=True)
    mine = [l for k, l in enumerate(job["lines"]) if k % a.nshards == a.shard]
    for line in mine:
        p = {**dflt, **line}
        ref = f"refs/{p['ref']}.wav"
        for t in range(job.get("takes", 3)):
            torch.manual_seed(1000 + t)
            t0 = time.time()
            wav = model.generate(p["text"], audio_prompt_path=ref, exaggeration=p["exaggeration"],
                                 cfg_weight=p["cfg_weight"], temperature=p["temperature"])
            out = os.path.join(a.out, f"{line['id']}__t{t}.wav")
            torchaudio.save(out, wav, model.sr)
            hyp = asr({"raw": wav.squeeze(0).numpy(), "sampling_rate": model.sr})["text"]
            info = dict(id=line["id"], take=t, wer=round(wer(p.get("check", p["text"]), hyp), 3), asr=hyp,
                        dur=round(wav.shape[-1] / model.sr, 2), secs=round(time.time() - t0, 1),
                        ref=p["ref"], exaggeration=p["exaggeration"], cfg_weight=p["cfg_weight"])
            json.dump(info, open(out[:-4] + ".json", "w"))
            print(json.dumps(info), flush=True)

def cmd_merge(a):
    job = load(a.job); os.makedirs(a.out + "/takes", exist_ok=True)
    rows = []
    for line in job["lines"]:
        infos = [json.load(open(f)) for f in glob.glob(f"{a.inp}/**/{line['id']}__t*.json", recursive=True)]
        for i in infos:
            src = glob.glob(f"{a.inp}/**/{i['id']}__t{i['take']}.wav", recursive=True)[0]
            shutil.copy(src, f"{a.out}/takes/{i['id']}__t{i['take']}.wav")
        if not infos:
            rows.append(f"| {line['id']} | MISSING | | | |"); continue
        best = min(infos, key=lambda i: (i["wer"], i["take"]))
        shutil.copy(f"{a.out}/takes/{best['id']}__t{best['take']}.wav", f"{a.out}/{line['id']}.wav")
        rows.append(f"| {line['id']} | t{best['take']} | {best['wer']} | {best['dur']} | {best['asr']} |")
        json.dump(infos, open(f"{a.out}/takes/{line['id']}.json", "w"), indent=1)
    rep = f"# {job['name']}\n\n| line | picked | WER | dur s | Whisper heard |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n"
    open(f"{a.out}/report.md", "w").write(rep); print(rep)

if __name__ == "__main__":
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--job", required=True); g.add_argument("--shard", type=int, default=0)
    g.add_argument("--nshards", type=int, default=1); g.add_argument("--out", default="out/gen")
    m = sub.add_parser("merge"); m.add_argument("--job", required=True); m.add_argument("--inp", default="out/all")
    m.add_argument("--out", default="results")
    a = p.parse_args(); {"gen": cmd_gen, "merge": cmd_merge}[a.cmd](a)
