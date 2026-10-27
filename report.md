# Market Minute 27 Oct 2026: fixes for variant C (no laughter tag on the answer, plain 'lakh'): OmniVoice takes

Pick = lowest Whisper word error rate, then closest to the median length.


## Variant C: Directed clone of Heart: per-line reference energy (punchy / curious / calm) + consistent instruct + non-verbal tags + CMU pronunciation

- **reveal_0** pick C__reveal_0_t3.wav · text: `Answer? C! Media stocks, up over three and a half percent.`
  - t1: 3.35 s (gen 135.7 s), WER 0.091: Answer, see media stocks, up over three and a half percent.
  - t2: 3.28 s (gen 136.7 s), WER 0.091: Answer? See media stocks up over three and a half percent.
  - t3: 3.36 s (gen 136.1 s), WER 0.0: Answer C media stocks up over three and a half percent
- **you_0** pick C__you_0_t1.wav · text: `In rupees? One lakh in a Nifty fund: down about fifteen rupees. One lakh tracking small caps? Up about two thousand seven hundred!`
  - t1: 7.54 s (gen 155.2 s), WER 0.136: In rupees, one lakh and a nifty fund, down about 15 rupees. One lakh tracking small caps, up about 2,700.
  - t2: 7.59 s (gen 155.3 s), WER 0.136: In rupees, one lakh and a nifty fund. Down about 15 rupees. One lakh tracking small caps. Up about 2,700.
  - t3: 7.45 s (gen 155.2 s), WER 0.136: In rupees, one lakh and a nifty fund. Down about 15 rupees. One lakh tracking small caps, up about 2,700.
