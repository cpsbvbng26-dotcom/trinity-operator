# Preregistration draft: a confirmatory scan of the golden-window conjecture

Status: draft, not registered. The registration on OSF was stopped on 2026-11-12, and
nothing has been filed. While it is unregistered the text can change, and the confirmatory
grid below is not run. No registration DOI exists yet. None is written here that the author
has not given.

This text follows the sections of the OSF Preregistration template, in order, so that each
section can be pasted into the matching part of the form. It continues the repeated-games note
([README.md](README.md)) and its open problem page ([OPEN-PROBLEM.md](OPEN-PROBLEM.md)). It
stays within the scope set out in [SCOPE.md](SCOPE.md): the object `T_δ` is unchanged.

## Title

A confirmatory numerical scan of the golden-window conjecture on a preregistered grid

## Description

The golden-window conjecture concerns the set `T_δ` of payoffs `(2+t, 4−t, 2+t)` that are
pure-strategy equilibrium payoffs of the repeated three-player game `G_3`, for discount
factors δ between `1/φ` and `2/3`. Part (a) says that `T_δ` has Lebesgue measure zero. Part (b)
says that its Hausdorff dimension is less than 1, is continuous and non-decreasing in δ, and
runs from 0 to 1 across the window. Both parts are open. The note proves that the dimension is
positive (Proposition 6).

An exploratory scan was run on 2026-11-12 (`games/scan.py`, output in `games/scan.txt`). It
used 48 values of δ, from 0.619 to 0.666 at step 0.001, and a depth of 30 periods. Its results
agree with both parts. This registration fixes, before it is run, a second grid of values not
in the exploratory grid, the quantities to compute, and what would count against the
conjecture.

A numerical scan cannot prove the conjecture. Agreement on the confirmatory grid will be
reported as evidence, not as proof.

## Hypotheses

Each hypothesis is read at every value of δ on the confirmatory grid, at depth 32. The growth
is the number of surviving intervals per period over the last 5 periods.

- **H1**, from part (a): the growth is below `1/δ`. Equivalently, growth × δ is below 1, so the
  total length of the surviving intervals keeps shrinking.
- **H2**, from part (b): the dimension estimate `log(growth)/log(1/δ)` is below 1.
- **H3**, from part (b): with the values of δ in increasing order, the dimension estimate never
  falls from one value to the next.

The limits of part (b) at the two ends of the window are not tested. Finite-depth estimates
cannot fix a limit. The six probes near the ends are reported descriptively, and they enter H3
through the ordering.

## Design plan

Study type: other. This is a deterministic computation, not an experiment or an observation.
There are no participants, no random numbers and no blinding.

The design is a fixed grid of rational values of δ. For each one, the script refines the
interval `[c, 3]` of player 1's continuation values for 32 periods, keeping the values that
survive. Here `c = 2 + (1 − δ)/δ`, and a value w moves backwards by `w′ = (w − (1 − δ)u)/δ` with
`u ∈ {2, 3}`. Below `2/3` the two branches have disjoint images, so each surviving interval is
one admissible sequence of length 32.

## Sampling plan

Existing data: the exploratory grid has been run and its results have been seen. The
confirmatory grid has not been run.

The confirmatory grid has 54 values of δ:

- the 48 midpoints of the exploratory grid, δ = (2k + 1)/2000 for k = 618, …, 665, that is
  0.6185, 0.6195, …, 0.6655;
- six probes near the ends of the window, δ = 0.6181, 0.6182, 0.6183, 0.6664, 0.6665 and 0.6666.

The grid is fixed in the script as `CONFIRM`, and the depth as `CONFIRM_DEPTH`, which is 32.
`verification/check_docs.py` fails if this page and the script disagree, and if the
confirmatory grid shares a value with the exploratory one.

Every value on the grid is run. There is no stopping rule. If a value cannot be computed, for
instance for lack of memory, it is reported as missing and is not dropped silently.

## Variables

The manipulated variable is δ. For each δ the script reports:

- the number `N` of surviving intervals at depth 32, counted exactly in integer arithmetic;
- their total length;
- the growth over the last 5 periods, and growth × δ;
- the length ratio per period over the last 5 periods;
- the dimension estimate `log(growth)/log(1/δ)`;
- the upper estimate `log N/(32 log(1/δ))`;
- `n₀` and the lower bound of Proposition 6.

## Analysis plan

The command is `python3 games/scan.py --confirmatory`, run on the commit named on the
registration form. Its output is committed as `games/scan-confirmatory.txt`.

Inference criteria. Each of the following counts against the conjecture. None of them is a
disproof, because the grid is finite and the depth is finite.

| result | counts against |
| --- | --- |
| growth × δ is 1 or more at some δ | part (a) at that δ (H1) |
| the length ratio per period is 1 or more at some δ | part (a) at that δ (H1) |
| the dimension estimate is 1 or more at some δ | the bound below 1 in part (b) (H2) |
| the dimension estimate falls between two neighbouring values of δ | monotonicity in part (b) (H3) |

If any of these occurs, the affected values of δ are run again at depth 34, and both results
are reported. The follow-up does not replace the first result.

The following do not count against the conjecture, because the exploratory scan already showed
them as effects of the finite depth:

- an upper estimate of 1 or more close to `2/3`;
- a dimension estimate below the lower bound of Proposition 6.

If every row passes H1, H2 and H3, the result is reported as evidence for both parts on 54 more
values of δ. It is not reported as a proof.

Data exclusion: none. Missing data: reported as missing, as above.

Exploratory analyses. Any quantity not listed above is labelled exploratory when it is
reported. This includes any argument that would turn the upper estimate into an upper bound for
the dimension. That argument is not part of this plan.

## Other

Reporting. The results are added to [README.md](README.md) and [OPEN-PROBLEM.md](OPEN-PROBLEM.md)
whatever they show. Any deviation from this plan is listed there next to the results.

Software. Python 3, the standard library, and NumPy for the lower bound of Proposition 6, which
comes from `games/games.py`. The interval counts use integers only.

## License and use of language models

This page is licensed under CC BY 4.0 ([LICENSE](LICENSE)). It was drafted with Claude Code
(Anthropic) at the author's request. The author is responsible for it. Claude is not an
author.
