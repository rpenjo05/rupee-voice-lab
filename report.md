# Market Minute 27 Oct 2026 (u_kf846TY8k): OmniVoice takes

Pick = lowest Whisper word error rate, then closest to the median length.


## Designed voice D: pick D_t2.wav

- D_t1.wav: 7.08 s, WER 1.0: Thanks for watching!
- D_t2.wav: 7.08 s, WER 0.056: Wait, the market barely moved today? But smaller companies? Up almost 3%! Here's the thing, that's huge!
- D_t3.wav: 7.08 s, WER 1.0: Boop. Boop.

## Variant B: Plain clone of Heart (punchy reference), original script, no instruct/tags

- **hook_0** pick B__hook_0_t1.wav · text: `The Nifty today? Down zero point zero two percent. Basically flat!`
  - t1: 3.87 s (gen 119.7 s), WER 0.364: The Nifty today, down 0.02%, basically flat.
  - t2: 3.79 s (gen 120.7 s), WER 0.364: The Nifty today, down 0.02%, basically flat.
- **hook_1** pick B__hook_1_t1.wav · text: `But smaller companies? Up two point seven percent!`
  - t1: 3.04 s (gen 129.2 s), WER 0.375: but smaller companies up 2.7%.
  - t2: 3.0 s (gen 128.4 s), WER 0.375: but smaller companies, up 2.7%.
- **hook_2** pick B__hook_2_t2.wav · text: `Quick guess: which sector jumped the most today? Answer at the end!`
  - t1: 3.84 s (gen 153.2 s), WER 0.0: Quick guess, which sector jumped the most today? Answer at the end.
  - t2: 3.89 s (gen 152.7 s), WER 0.0: Quick guess, which sector jumped the most today? Answer at the end.
- **broad_0** pick B__broad_0_t1.wav · text: `Midcaps? Up one percent. Smallcaps? Two point seven! The smaller the company, the bigger the jump.`
  - t1: 5.67 s (gen 142.0 s), WER 0.438: Mid caps? Up 1%. Small caps? 2.7. The smaller the company, the bigger the jump.
  - t2: 5.68 s (gen 141.5 s), WER 0.438: Mid caps, up 1%. Small caps, 2.7. The smaller the company, the bigger the jump.
- **trigger_0** pick B__trigger_0_t1.wav · text: `So why was the Nifty stuck? Banks! The Bank Nifty fell zero point seven percent. HDFC Bank and SBI pulled hardest.`
  - t1: 6.5 s (gen 179.4 s), WER 0.238: So why was the NFTY stuck banks? The bank NFTY fell 0.7%, HDFC bank and SBI pulled hardest.
  - t2: 6.52 s (gen 180.5 s), WER 0.238: So why was the NFTY stuck banks? The bank NFTY fell 0.7 percent. HDFC bank and SBI pulled hardest.
- **you_0** pick B__you_0_t2.wav · text: `In rupees? One lakh in a Nifty fund: down about fifteen rupees. One lakh tracking smallcaps? Up about two thousand seven hundred!`
  - t1: 7.38 s (gen 208.3 s), WER 0.409: In rupees, 1 lakh in a nifty fund, down about 15 rupees. 1 lakh tracking small caps, up about 2,700.
  - t2: 7.34 s (gen 208.1 s), WER 0.364: In rupees, one lakh and a nifty fund, down about 15 rupees. One lakh tracking small caps, up about 2,700.
- **reveal_0** pick B__reveal_0_t1.wav · text: `Answer? C! Media stocks, up over three and a half percent.`
  - t1: 3.35 s (gen 113.7 s), WER 0.0: Answer C media stocks up over three and a half percent
  - t2: 3.34 s (gen 112.9 s), WER 0.091: Answer? See media stocks up over three and a half percent.
- **reveal_1** pick B__reveal_1_t2.wav · text: `So remember... a flat Nifty isn't a flat market.`
  - t1: 2.73 s (gen 126.2 s), WER 0.222: So remember, a flat Nifty is in a flat market.
  - t2: 2.63 s (gen 125.8 s), WER 0.222: So remember a flat Nifty is in a flat market.

## Variant C: Directed clone of Heart: per-line reference energy (punchy / curious / calm) + consistent instruct + non-verbal tags + CMU pronunciation

- **hook_0** pick C__hook_0_t1.wav · text: `The Nifty today? Down zero point zero two percent. Basically flat!`
  - t1: 3.85 s (gen 143.6 s), WER 0.364: The Nifty today, down 0.02%, basically flat.
  - t2: 3.86 s (gen 143.4 s), WER 0.364: The Nifty today, down 0.02%, basically flat.
- **hook_1** pick C__hook_1_t1.wav · text: `But smaller companies? [surprise-oh] Up two point seven percent!`
  - t1: 3.71 s (gen 146.3 s), WER 0.5: But smaller companies? Oh, up 2.7%.
  - t2: 3.7 s (gen 146.7 s), WER 0.5: But smaller companies owe up 2.7%.
- **hook_2** pick C__hook_2_t1.wav · text: `Quick guess: which sector jumped the most today? Answer at the end!`
  - t1: 3.94 s (gen 130.0 s), WER 0.0: Quick guess, which sector jumped the most today? Answer at the end.
  - t2: 3.68 s (gen 131.4 s), WER 0.0: Quick guess, which sector jumped the most today? Answer at the end.
- **broad_0** pick C__broad_0_t1.wav · text: `Mid caps? Up one percent. Small caps? [surprise-wa] Two point seven! The smaller the company, the bigger the jump.`
  - t1: 6.47 s (gen 183.3 s), WER 0.5: Mid caps, up 1%. Small caps? What, 2.7? The smaller the company, the bigger the jump.
  - t2: 6.36 s (gen 183.9 s), WER 0.5: Mid caps? Up 1%. Small caps? WA 2.7. The smaller the company, the bigger the jump.
- **trigger_0** pick C__trigger_0_t2.wav · text: `[question-en] So why was the Nifty stuck? Banks! The Bank Nifty fell zero point seven percent. H D F C Bank and S B I pulled hardest.`
  - t1: 7.52 s (gen 185.3 s), WER 0.286: N. So why was the NFTY stuck? Banks. The bank NFTY fell 0.7%. HDFC bank and SBI pulled hardest.
  - t2: 7.45 s (gen 185.4 s), WER 0.286: N. So why was the NFTY stuck? Banks. The bank NFTY fell 0.7%. HDFC bank and SBI pulled hardest.
- **you_0** pick C__you_0_t1.wav · text: `In rupees? One [L AA1 K] in a Nifty fund: down about fifteen rupees. One [L AA1 K] tracking small caps? Up about two thousand seven hundred!`
  - t1: 8.13 s (gen 196.4 s), WER 0.455: In rupees, one lock and a nifty fund. Down about 15 rupees. One lock tracking small caps. Up about 2,700.
  - t2: 8.2 s (gen 196.6 s), WER 0.455: In rupees, one lock in a difty fund, down about 15 rupees. One lock tracking small caps, up about 2,700.
- **reveal_0** pick C__reveal_0_t2.wav · text: `Answer? C! [laughter] Media stocks, up over three and a half percent.`
  - t1: 3.74 s (gen 147.1 s), WER 0.091: Answer? Media stocks up over three and a half percent.
  - t2: 3.82 s (gen 146.8 s), WER 0.091: Answer? See media stocks up over three and a half percent
- **reveal_1** pick C__reveal_1_t2.wav · text: `So remember... a flat Nifty isn't a flat market.`
  - t1: 2.5 s (gen 101.6 s), WER 0.222: So remember, a flat Nifty is in a flat market.
  - t2: 2.56 s (gen 102.1 s), WER 0.222: So remember, a flat Nifty is in a flat market.

## Variant D: Designed Indian-English voice (instruct only), then cloned for consistency + same tags/pronunciation as C

- **hook_0** pick D__hook_0_t1.wav · text: `The Nifty today? Down zero point zero two percent. Basically flat!`
  - t1: 4.28 s (gen 92.3 s), WER 0.364: The Nifty today? Down 0.02%, basically flat.
  - t2: 4.28 s (gen 91.9 s), WER 0.364: The Nifty today down 0.02%, basically flat.
- **hook_1** pick D__hook_1_t1.wav · text: `But smaller companies? [surprise-oh] Up two point seven percent!`
  - t1: 4.2 s (gen 160.7 s), WER 0.5: But smaller companies? Oh, up 2.7%!
  - t2: 4.2 s (gen 160.5 s), WER 0.5: But smaller companies? Oh, up 2.7%!
- **hook_2** pick D__hook_2_t1.wav · text: `Quick guess: which sector jumped the most today? Answer at the end!`
  - t1: 4.32 s (gen 162.2 s), WER 0.0: Quick guess, which sector jumped the most today? Answer at the end.
  - t2: 4.3 s (gen 162.2 s), WER 0.0: Quick guess, which sector jumped the most today? Answer at the end.
- **broad_0** pick D__broad_0_t1.wav · text: `Mid caps? Up one percent. Small caps? [surprise-wa] Two point seven! The smaller the company, the bigger the jump.`
  - t1: 7.08 s (gen 115.7 s), WER 0.5: Mid caps? Up 1%. Small caps? 2.7%. The smaller the company, the bigger the jump.
  - t2: 7.08 s (gen 115.2 s), WER 0.5: Mid caps? Up 1%. Small caps? What? 2.7. The smaller the company, the bigger the jump.
- **trigger_0** pick D__trigger_0_t1.wav · text: `[question-en] So why was the Nifty stuck? Banks! The Bank Nifty fell zero point seven percent. H D F C Bank and S B I pulled hardest.`
  - t1: 8.08 s (gen 214.8 s), WER 0.143: So why was the Nifty stuck? Banks! The bank Nifty fell 0.7%, HDFC bank and SBI pulled hardest.
  - t2: 8.04 s (gen 215.5 s), WER 0.333: Mmm, so why was the Nifty stuck? Banks! The bank Nifty fell 0.7%. HDFC Bank in SB. I pulled hardest.
- **you_0** pick D__you_0_t2.wav · text: `In rupees? One [L AA1 K] in a Nifty fund: down about fifteen rupees. One [L AA1 K] tracking small caps? Up about two thousand seven hundred!`
  - t1: 8.78 s (gen 228.6 s), WER 0.409: In rupees? One lock in a nifty fund. Down about 15 rupees. One lock tracking small caps? Up about 2,700.
  - t2: 8.86 s (gen 229.5 s), WER 0.409: In rupees, one lock in a nifty fund, down about 15 rupees. One lock tracking small caps, up about 2,700.
- **reveal_0** pick D__reveal_0_t1.wav · text: `Answer? C! [laughter] Media stocks, up over three and a half percent.`
  - t1: 4.32 s (gen 91.8 s), WER 0.0: Answer? C. Media stocks up over three and a half percent.
  - t2: 4.32 s (gen 91.2 s), WER 0.091: Answer? Media stocks up over three and a half percent.
- **reveal_1** pick D__reveal_1_t1.wav · text: `So remember... a flat Nifty isn't a flat market.`
  - t1: 3.01 s (gen 141.7 s), WER 0.0: So remember, a flat nifty isn't a flat market.
  - t2: 3.04 s (gen 141.6 s), WER 0.0: So remember, a flat nifty isn't a flat market.
