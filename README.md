# rupee-voice-lab

Test bench for narration voices for the Rupee Math YouTube channel, using
[OmniVoice](https://github.com/k2-fsa/OmniVoice) (Apache-2.0) on CPU GitHub Actions runners.

- `refs/`: reference clips of our current narrator voice (Kokoro `af_heart`, Apache-2.0) in three energies:
  punchy, curious and calm. `refs/refs.json` holds their transcripts.
- `jobs/*.json`: a script split into lines, plus the variants to try (plain clone, directed clone with per-line
  reference energy, non-verbal tags and CMU pronunciation, or a designed voice).
- `run.py`: generates N takes per line, transcribes each with Whisper (small.en) and picks the take with the lowest
  word error rate. All takes are kept.
- Workflow **OmniVoice takes** (manual): `plan` → `design` → `gen` (variants × shards in parallel) → `merge`.
  The `results` artifact has `<variant>/<line>.wav` (the picks), `<variant>/takes/`, `preview_<variant>.wav` and `report.md`.

```
gh workflow run omnivoice.yml -R rpenjo05/rupee-voice-lab -f job=jobs/mm_20261027.json -f variants=B,C,D -f shards=3
```

This repo holds no channel code, keys or videos.
