# Scope: continuing the golden-window conjecture

This page sets out how far the golden-window conjecture may be continued under rule 15 of
this group of repositories. A Japanese version is [SCOPE.ja.md](SCOPE.ja.md). Rule 15 is in
the common section of each repository's `CLAUDE.md`. The sentence that applies reads, in
the original Japanese:

> 学部二年次以降に進めるのは、学部一年次の成果の続きか修正に限る（黄金比の窓の予想を含む）。

In English: from the second undergraduate year on, work may only continue or correct the
work of the first year, and this includes the golden-window conjecture.

## What it continues

The three Trinity-Infinity papers are first-year undergraduate self-study, and they are
frozen. The repeated-games note ([README.md](README.md)) was first written on 2026-10-04.
That date falls in the author's second undergraduate year. The note is kept as a
continuation of the three papers.

The object of the conjecture is the set `T_δ` defined in [OPEN-PROBLEM.md](OPEN-PROBLEM.md):
the stage game `G_3` of Series I, Table 1, and the values of `t` for which
`(2+t, 4−t, 2+t)` is a pure-strategy equilibrium payoff without a public randomization
device.

## What counts as continuation

Continuation answers a part that the note and the open problem page have already opened.
Each open part has one issue label. The table lists them in the order of the labels.

| label | open part | work that continues it |
| --- | --- | --- |
| `conjecture (a)` | Golden-window conjecture (a) | a proof, or a counterexample, that `T_δ` has length zero inside the window |
| `conjecture (b)` | Golden-window conjecture (b) | a proof, or a counterexample, about the dimension of `T_δ`, monotonicity included |
| `why 1/φ twice` | An open question: why 1/φ twice | why Propositions 1 and 5 both come from the polynomial `δ² + δ − 1` |
| `literature check` | The literature check | checking Propositions 1–7 against the literature, so that they can be counted |

The following also count as continuation.

- Correcting Propositions 1–7 or their proofs. The correction goes into the note and its
  script. The Figshare preprint is frozen.
- Extending the numerical evidence on the same object. This means more values of δ inside
  the window, a deeper refinement, or a search for counterexamples. The open problem page
  records that none of these has been run.
- Using the tools that the note names as a starting point, for this problem only. These are
  expansions in the non-integer base `β = 1/δ` with a hole.

## What would be a new theme

Work that changes the object `T_δ` is not continuation. It is a new theme.

- A stage game that Propositions 1–7 do not treat.
- A monitoring assumption other than the perfect monitoring of the note.
- The golden example of the roadmap, stage 2, where the joint spectral radius is exactly 1
  at `γ = 1/φ`. The open problem page records it as a different object.
- Expansions in a non-integer base with a hole, studied for their own sake and apart from
  this problem.

A new theme is not added to the self-study series. Rule 15 names the routes for it: JOSS,
diamond open access venues, conference talks and joint research.

## How continuation is published

- Results go into the note and its script. A proof is added before the status table moves.
- The conjecture is not rewritten as proved. It does not take a person's name.
- Rule 14 applies: only diamond open access venues, which charge neither readers nor
  authors. Rule 15 limits Figshare to work of the level that researchmap lists under MISC.

## A test for unclear cases

Two questions decide it.

1. Does the work treat `T_δ` of the open problem page, or Propositions 1–7 of the note,
   without changing their definitions?
2. Does it answer one of the labels in the table above, or correct a proposition?

Work that passes both is continuation. Work that fails either is a new theme.

## License and use of language models

This page is licensed under CC BY 4.0 ([LICENSE](LICENSE)). It was written with Claude Code
(Anthropic) at the author's request. The author is responsible for it. Claude is not an
author.
