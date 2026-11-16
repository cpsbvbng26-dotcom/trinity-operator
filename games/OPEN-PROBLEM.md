# Open problem: the golden-window conjecture

This page collects, on one sheet, what is proved and what is open about the golden-window
conjecture. Everything here is taken from [the repeated-games note](README.md) and from
[the roadmap](../roadmap/README.md). Nothing is added. The note remains the maintained
version, with the proofs and the evidence in full.

## The object

The stage game `G_3` is Table 1 of Series I. Three players each choose C or D, and the
repeated game has common discount factor δ and perfect monitoring. The point
`(2+t, 4−t, 2+t)` with `0 < t ≤ 1` lies between `(2,4,2)` and `(3,3,3)`. Write `T_δ` for the
set of `t` in (0, 1] for which `(2+t, 4−t, 2+t)` is a pure-strategy equilibrium payoff,
without a public randomization device.

The window is the interval from `1/φ` to `2/3`.

## What is proved

| | statement | status |
| --- | --- | --- |
| Proposition 4 | with public randomization, `(2+t, 4−t, 2+t)` is sustainable exactly when δ ≥ max(1/2, 1 − t) | proved |
| Proposition 5 | without randomization, the same holds for δ ≥ 2/3; only two points survive for 1/2 ≤ δ < 1/φ, and a countable set at δ = 1/φ | proved |
| Proposition 6 | inside the window 1/φ < δ < 2/3, the sustainable set has positive Hausdorff dimension | proved |

The rows are copied from the status table of the note. Proposition 1 gives the same
polynomial `δ² + δ − 1` for the three-player rotation. None of the propositions has been
checked against the literature. Some may be known exercises.

## What is open

**Golden-window conjecture (a).** For 1/φ < δ < 2/3, `T_δ` has Lebesgue measure zero.

**Golden-window conjecture (b).** For 1/φ < δ < 2/3, the Hausdorff dimension of `T_δ` is
less than 1, is continuous and non-decreasing in δ, and tends to 0 as δ ↓ 1/φ and to 1 as
δ ↑ 2/3. That it is positive is Proposition 6.

**An open question: why 1/φ twice.** The threshold of the three-player rotation
(Proposition 1) and the lower end of the window (Proposition 5) both come from the same
polynomial `δ² + δ − 1`. The note records this as a question, not as a conjecture.

**The literature check.** Propositions 1–7 are proved but not yet counted. Only a
literature check can move them. The environment the note was written in cannot reach the
literature databases, so the check has not been made.

Monotonicity is the least supported part of (b). The note says that five values cannot
settle it, nor can the 48 values of the wider scan, and that dimension functions of maps
with holes often behave like a devil's staircase.

## What was computed, and what was not

The evidence for both parts is numerical. The ranges below are the ones the scripts
`games/games.py` and `games/scan.py` use. The numbers on this page are checked against
those scripts by `verification/check_docs.py`.

| computation | parameters | recorded in |
| --- | --- | --- |
| refinement of the surviving intervals | δ = 0.62, 0.63, 0.64, 0.65, 0.66; depth 22 periods | `GAP` and `DEPTH` in `games/games.py` |
| pure-strategy search below the window | δ = 0.5, 0.55, 0.6; grid t = 0.01, …, 1; 40 periods ahead | `pure_ok` and `values` in `games/games.py` |
| wider scan of the window, 2026-11-12 | δ = 0.619, 0.620, …, 0.666, 48 values; depth 30 periods; exact counts | `SCAN` and `SCAN_DEPTH` in `games/scan.py` |
| confirmatory scan of the window, 2026-11-17 | δ = 0.6185, 0.6195, …, 0.6655 and the probes 0.6181, 0.6182, 0.6183, 0.6664, 0.6665, 0.6666, 54 values; depth 32 periods; exact counts | `CONFIRM` and `CONFIRM_DEPTH` in `games/scan.py` |

The wider scan is the first recorded search for counterexamples. At each of its 48 values
it looks for a δ at which the total length stops shrinking, and between neighbouring values
it looks for a fall in the dimension estimate. It found neither. In that scan, no δ between its grid
points, and no depth beyond 30 periods, is recorded. A grid cannot exclude a δ between its
points. The pure-strategy search lies below the window, so it does not test either part of
the conjecture.

A second grid was fixed in advance in the [preregistration](PREREGISTRATION.md),
together with what would count against the conjecture on it. The section below reports it.

The note reports what the five rows show. In every row the growth rate is below `1/δ`, so
the total length keeps shrinking. The dimension estimate rises with δ. At δ = 0.62 the
estimate 0.38 is below the proved lower bound 0.404, so the finite-depth estimate is too low
there. The wider scan shows the same on all 48 rows: the total length shrinks in 48 of 48,
and the dimension estimate has 0 decreases. Neither observation is a proof.

## The confirmatory scan

The second grid was fixed in the [preregistration](PREREGISTRATION.md) before it was run.
The author filed the registration on OSF on 2026-11-16 and approved it on 2026-11-17. Its DOI
is [10.17605/OSF.IO/6EW38](https://doi.org/10.17605/OSF.IO/6EW38), and the text on OSF governs.
The grid has 54 values of δ: the 48 midpoints of the exploratory grid and six probes near the
ends of the window. The depth is 32 periods.

The grid was run once, on 2026-11-17 from 06:12:29 to 06:12:42 JST, after the registration
was filed. The command was `python3 games/scan.py --confirmatory`, in a fresh clone checked
out at the registered commit `addf684d4b3165af37cbc3ac94763608b7b6d2bf` with a clean tree,
under Python 3.11.18 and NumPy 2.4.6. It exited with status 0 and wrote nothing to stderr.
Its output is [`scan-confirmatory.txt`](scan-confirmatory.txt), committed byte for byte
(SHA-256 `f3c40d4beb0c41137fd14f8a2f7ba4a2809d28a4a957097bea2ba9813ea71a51`). A first
invocation in the same minute failed before Python started, because the shell's
`/usr/bin/time` was missing. It computed nothing.

The table rounds to three decimals. The values below were read at full precision by calling
`scan.row` from the same commit, unmodified.

- H1 holds. Growth × δ is below 1 at 54 of 54 values, and the length ratio per period is
  below 1 at 54 of 54. The largest growth × δ is 0.999695, at δ = 0.6666. The largest length
  ratio per period is 0.999689, at δ = 0.6666.
- H2 holds. The dimension estimate is below 1 at 54 of 54 values. The largest is 0.999247, at
  δ = 0.6666.
- H3 holds. With δ in increasing order, the dimension estimate never falls. The scan counts
  0 decreases, and no two neighbouring values are equal.

Nothing counts against the conjecture, so the follow-up at depth 34 was not run. The plan
runs it only if a criterion is met. Two results do not count, as the plan says. The upper
estimate is 1 or more at 6 values close to 2/3 (δ = 0.6635, 0.6645, 0.6655, 0.6664, 0.6665,
0.6666). The dimension estimate is below the lower bound of Proposition 6 at 17 values.
No value is missing, and none is excluded.

The δ column of the table is the display of the registered script, which was not changed. It
prints the 48 midpoints rounded to three decimals, so 0.6185 appears as 0.619, and 0.6245 and
0.6255 both appear as 0.625. The rows are in grid order: the 48 midpoints in increasing order,
then the six probes.

There is no deviation from the plan in the analysis. The failed first invocation is the only
other event, and it computed nothing.

This is evidence on 54 more values of δ, not a proof. Near 2/3 the margin is small. At
δ = 0.6666, growth × δ falls short of 1 by about 3 × 10⁻⁴. A grid cannot rule out a δ
between its points, and a finite depth cannot fix a dimension.

## Where a proof might start

The note gives the order of work. First, check the literature, including Berg and Kitti
(2014) and work on survivor sets of interval maps with holes. If nothing there settles the
question, start with part (a).

The change of variables `x = (3 − w)/(1 − δ)` turns the recursion into `x = a + δx′` with
`a ∈ {0, 1}`. This is an expansion in the non-integer base `β = 1/δ` with a hole. The note
names three leads, recalled from memory and not checked: Glendinning and Sidorov (2001),
Kalle, Kong, Langeveld and Li (around 2020), and Urbański (1986).

## Not part of this problem

The roadmap has its own golden example. In stage 2, at `γ = 1/φ`, the joint spectral radius
is squeezed to exactly 1 and the bounds do not move. That is a different object. The
roadmap records that deciding `JSR ≤ 1` is undecidable in general (Blondel and Tsitsiklis
2000). It is not one of the open parts listed here.

## Issue labels

Each open part has an issue label. The labels are defined in
[`.github/workflows/labels.yml`](../.github/workflows/labels.yml), which creates them on
GitHub when it runs.

| label | open part |
| --- | --- |
| `conjecture (a)` | Golden-window conjecture (a) |
| `conjecture (b)` | Golden-window conjecture (b) |
| `why 1/φ twice` | An open question: why 1/φ twice |
| `literature check` | The literature check |

## Place in the series

The three Trinity-Infinity papers are first-year undergraduate self-study, and they are
frozen. This problem continues that work. It does not start a new theme.

## License and use of language models

This page is licensed under CC BY 4.0. It was compiled from the note with Claude Code
(Anthropic) at the author's request. The author is responsible for it. Claude is not an
author.
