"""Voice check: score voiceover takes so voices can be compared by numbers, not only by ear.

  python voice_check.py score  --tool prosody|utmos|aesthetics|emotion --inp eval --out out/<tool>.json
  python voice_check.py report --inp out/all --out results

Input: eval/<set>/<line>.wav (one folder per voice, one wav per narration line).
Every file is first loudness-matched (-20 LUFS, mono 16 kHz) so loudness doesn't sway the models.

Tools (all free, CPU, no keys):
  prosody    Praat via parselmouth: pitch median, pitch variation (st, semitones), pitch range p5-p95 (st),
             loudness variation (dB), pause share; Whisper small.en: words per minute.  "Flat" = low pitch variation/range.
  utmos      UTMOSv2 (VoiceMOS 2024 winner): predicted naturalness MOS 1-5.
  aesthetics Meta Audiobox Aesthetics: CE content enjoyment, CU content usefulness, PC production complexity,
             PQ production quality (1-10).
  emotion    emotion2vec+ base: top emotion and the share of non-neutral emotion.
  mix        Full mixes eval/<set>/_mix.wav (voice + music + SFX, from pipeline/audio/mix_v2.py): Audiobox Aesthetics on the
             whole track, plus timing from eval/<set>/_cues.json (length, voice share, mean pause, pause before reveals).
             Sets without line wavs (e.g. a v1 baseline mix only) appear in this table only.
"""
import argparse, glob, json, os, subprocess, tempfile, statistics as st

def files(inp):
    return sorted(f for f in glob.glob(f"{inp}/*/*.wav") if not os.path.basename(f).startswith("_"))

def key(f):
    return f"{os.path.basename(os.path.dirname(f))}/{os.path.basename(f)[:-4]}"

def prep(f, tmp):
    o = os.path.join(tmp, key(f).replace("/", "__") + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-af", "loudnorm=I=-20:TP=-2:LRA=11", "-ac", "1", "-ar", "16000", o], check=True)
    return o

def t_prosody(fs):
    import numpy as np, parselmouth
    from transformers import pipeline
    asr = pipeline("automatic-speech-recognition", model="openai/whisper-small.en", device="cpu")
    out = {}
    for k, p in fs.items():
        snd = parselmouth.Sound(p); dur = snd.get_total_duration()
        f0 = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=500).selected_array["frequency"]
        v = f0[f0 > 0]; stv = 12 * np.log2(v / np.median(v)) if len(v) > 10 else np.array([0.0])
        inten = snd.to_intensity(minimum_pitch=75).values[0]; inten = inten[inten > inten.max() - 40]
        frames = snd.to_intensity(minimum_pitch=75).values[0]
        pause = float((frames < frames.max() - 30).mean())
        txt = asr(p)["text"].strip()
        out[k] = dict(f0_hz=round(float(np.median(v)), 1) if len(v) else 0, f0_sd_st=round(float(stv.std()), 2),
                      f0_range_st=round(float(np.percentile(stv, 95) - np.percentile(stv, 5)), 2),
                      loud_sd_db=round(float(inten.std()), 2), pause=round(pause, 3), dur=round(dur, 2),
                      wpm=round(len(txt.split()) / dur * 60, 1), asr=txt)
        print(k, out[k], flush=True)
    return out

def t_utmos(fs):
    import utmosv2
    m = utmosv2.create_model(pretrained=True, device="cpu")
    out = {}
    for k, p in fs.items():
        out[k] = dict(mos=round(float(m.predict(input_path=p, device="cpu", verbose=False)), 3)); print(k, out[k], flush=True)
    return out

def t_aesthetics(fs):
    from audiobox_aesthetics.infer import initialize_predictor
    pr = initialize_predictor(); out = {}
    ks = list(fs)
    for i in range(0, len(ks), 8):
        res = pr.forward([{"path": fs[k]} for k in ks[i:i + 8]])
        for k, r in zip(ks[i:i + 8], res):
            out[k] = {x: round(float(r[x]), 2) for x in ("CE", "CU", "PC", "PQ")}; print(k, out[k], flush=True)
    return out

def t_emotion(fs):
    from funasr import AutoModel
    m = AutoModel(model="emotion2vec/emotion2vec_plus_base", hub="hf", disable_update=True)
    out = {}
    for k, p in fs.items():
        r = m.generate(p, granularity="utterance", extract_embedding=False)[0]
        lab = [l.split("/")[-1] for l in r["labels"]]; sc = dict(zip(lab, [float(s) for s in r["scores"]]))
        top = max(sc, key=sc.get)
        out[k] = dict(emotion=top, conf=round(sc[top], 2), non_neutral=round(1 - sc.get("neutral", 0), 2),
                      happy=round(sc.get("happy", 0), 2), surprised=round(sc.get("surprised", 0), 2), sad=round(sc.get("sad", 0), 2))
        print(k, out[k], flush=True)
    return out

def t_speaker(fs):
    """Heart likeness: cosine similarity of ECAPA speaker embeddings (speechbrain, VoxCeleb) between each line and
    the mean of the Kokoro Heart references in refs/heart_*.wav (same voice the clones copy). ~0.7+ = same speaker."""
    import torch, torchaudio, glob as g
    from speechbrain.inference.speaker import EncoderClassifier
    enc = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="/tmp/ecapa")
    def emb(p):
        y, sr = torchaudio.load(p); y = y.mean(0, keepdim=True)
        if sr != 16000: y = torchaudio.functional.resample(y, sr, 16000)
        e = enc.encode_batch(y).squeeze(); return e / e.norm()
    ref = torch.stack([emb(r) for r in sorted(g.glob("refs/heart_*.wav"))]).mean(0); ref = ref / ref.norm()
    out = {}
    for k, p in fs.items():
        out[k] = dict(sim=round(float(emb(p) @ ref), 3)); print(k, out[k], flush=True)
    return out

def t_mix(inp):
    """Full mix (voice + music + sound effects): Audiobox Aesthetics on eval/<set>/_mix.wav, timing from _cues.json."""
    tmp = tempfile.mkdtemp(); out = {}
    mixes = {os.path.basename(os.path.dirname(f)): f for f in sorted(glob.glob(f"{inp}/*/_mix.wav"))}
    aes = t_aesthetics({k: prep(f, tmp) for k, f in mixes.items()}) if mixes else {}
    for k in mixes:
        r = dict(aes.get(k, {})); cf = os.path.join(os.path.dirname(mixes[k]), "_cues.json")
        if os.path.exists(cf):
            c = json.load(open(cf)); L = c["lines"]; gaps = [l["pause_before"] for l in L[1:]]
            rev = [l["pause_before"] for l in L[1:] if l.get("reveal")]
            r.update(total_s=c["total"], voice_share=round(c["voice_s"] / c["total"], 2),
                     pause_mean=round(st.mean(gaps), 2) if gaps else None, pause_reveal=round(st.mean(rev), 2) if rev else None)
        out[k] = r; print(k, r, flush=True)
    return out

def cmd_score(a):
    if a.tool == "mix":
        res = t_mix(a.inp); os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); json.dump(res, open(a.out, "w"), indent=1); return
    tmp = tempfile.mkdtemp(); fs = {key(f): prep(f, tmp) for f in files(a.inp)}
    res = {"prosody": t_prosody, "utmos": t_utmos, "aesthetics": t_aesthetics, "emotion": t_emotion, "speaker": t_speaker}[a.tool](fs)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); json.dump(res, open(a.out, "w"), indent=1)

COLS = [("speaker", "sim", "Heart likeness (0-1)"), ("utmos", "mos", "Naturalness MOS (1-5)"), ("aesthetics", "CE", "Enjoyment CE (1-10)"),
        ("aesthetics", "PQ", "Prod. quality PQ (1-10)"), ("emotion", "non_neutral", "Non-neutral emotion (0-1)"),
        ("prosody", "f0_sd_st", "Pitch variation (st)"), ("prosody", "f0_range_st", "Pitch range p5-p95 (st)"),
        ("prosody", "loud_sd_db", "Loudness variation (dB)"), ("prosody", "wpm", "Words / min"), ("prosody", "dur", "Voice total s")]

def cmd_report(a):
    data = {}
    for f in glob.glob(f"{a.inp}/**/*.json", recursive=True):
        data[os.path.basename(f)[:-5]] = json.load(open(f))
    sets = sorted({k.split("/")[0] for n, t in data.items() if n != "mix" for k in t})
    md = ["# Voice check\n", "Per-voice means over all narration lines (loudness-matched first). Higher = better for "
          "MOS, CE, PQ; pitch variation/range and loudness variation measure liveliness (flat voices score low). "
          "Missing column = that tool failed (see the run log).\n"]
    md += ["| voice | " + " | ".join(c[2] for c in COLS) + " |", "|---" * (len(COLS) + 1) + "|"]
    summ = {}
    for s in sets:
        row = []
        for t, c, _ in COLS:
            vals = [v[c] for k, v in data.get(t, {}).items() if k.startswith(s + "/") and c in v]
            x = (round(sum(vals), 1) if c == "dur" else round(st.mean(vals), 2)) if vals else None
            row.append("" if x is None else str(x)); summ.setdefault(s, {})[f"{t}.{c}"] = x
        md.append(f"| {s} | " + " | ".join(row) + " |")
    if data.get("mix"):
        md += ["\n## Full mix (voice + music + sound effects)\n",
               "| set | Enjoyment CE | Prod. quality PQ | Complexity PC | Length s | Voice share | Mean pause s | Pause before reveals s |",
               "|---|---|---|---|---|---|---|---|"]
        for k, v in sorted(data["mix"].items()):
            md.append(f"| {k} | " + " | ".join(str(v.get(c, "")) for c in ("CE", "PQ", "PC", "total_s", "voice_share", "pause_mean", "pause_reveal")) + " |")
    md.append("\n## Per line\n")
    for s in sets:
        md.append(f"\n### {s}\n\n| line | Heart | MOS | CE | PQ | emotion | pitch var st | range st | wpm |\n|---|---|---|---|---|---|---|---|---|")
        lines = sorted({k for t in data.values() for k in t if k.startswith(s + "/")})
        for k in lines:
            g = lambda t, c: data.get(t, {}).get(k, {}).get(c, "")
            md.append(f"| {k.split('/')[1]} | {g('speaker','sim')} | {g('utmos','mos')} | {g('aesthetics','CE')} | {g('aesthetics','PQ')} | "
                      f"{g('emotion','emotion')} {g('emotion','conf')} | {g('prosody','f0_sd_st')} | {g('prosody','f0_range_st')} | {g('prosody','wpm')} |")
    os.makedirs(a.out, exist_ok=True)
    open(f"{a.out}/report.md", "w").write("\n".join(md) + "\n")
    json.dump(dict(summary=summ, lines=data), open(f"{a.out}/scores.json", "w"), indent=1)
    print("\n".join(md[:len(sets) + 5]))

if __name__ == "__main__":
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score"); s.add_argument("--tool", required=True); s.add_argument("--inp", default="eval"); s.add_argument("--out", required=True)
    r = sub.add_parser("report"); r.add_argument("--inp", default="out/all"); r.add_argument("--out", default="results")
    a = p.parse_args(); {"score": cmd_score, "report": cmd_report}[a.cmd](a)
