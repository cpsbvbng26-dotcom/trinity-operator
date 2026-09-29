# Lesson 3 — Permutations can be solved by hand

*The Friedkin–Johnsen model with a cyclic influence matrix — one operator, five lessons.* Draft. The author has not yet reviewed this lesson.

**Time:** about 45 minutes.
**You need:** Lessons 1 and 2, and the cycle decomposition of a permutation.
**Run:** `python3 lessons/lesson3.py` from the root of this repository.
Every number on this page comes from that script. `verification/check_lessons.py`
fails if the page and the script disagree.

## What you will be able to do

1. Read off the spectral radius and the operator norm of `DQ` from the rates and the
   cycles of `Q`, without computing eigenvalues.
2. Write the fixed point of the cyclic model as a finite sum.
3. Say what restricting the influence matrix to a permutation keeps of the
   Friedkin–Johnsen model, and what it throws away.

## What a permutation does to the model

In the Friedkin–Johnsen model each agent mixes the opinions of the agents it listens
to, with weights given by a row of `W`. When `W` is a permutation matrix, each row has
a single 1: **every agent listens to exactly one other agent**, and every agent is
listened to by exactly one. The influence network falls apart into disjoint directed
cycles. Everything in this lesson follows from that picture.

## Two formulas

Let `Q` be a permutation matrix with cycles `c₁, c₂, …`, and `D = diag(a)` with every
`aᵢ` in `[0, 1)`.

**Norm.** `DQ` sends each coordinate to one place and multiplies it by one rate. Its
singular values are therefore the rates themselves, and

```
‖DQ‖₂ = maxᵢ aᵢ.
```

**Spectral radius.** Going once round a cycle `c` of length `m` multiplies a
coordinate by every rate on the cycle. On that cycle `(DQ)ᵐ` is `(∏_{i∈c} aᵢ) I`, so

```
ρ(DQ) = max over cycles c of ( ∏_{i∈c} aᵢ )^(1/|c|),
```

the largest geometric mean of the rates along a cycle. `trinity.py` implements both
formulas as `closed_form_norm` and `closed_form_radius`.

## Worked example 1 — two pairs

Four agents in two pairs, each listening only to its partner, with rates
`a = (0.9, 0.4, 0.5, 0.8)`. The script finds the cycles `{1, 2} and {3, 4}` and their
geometric means `0.600000 and 0.632456`.

| quantity | formula | eigenvalues / singular values |
| --- | --- | --- |
| `ρ(A)` | 0.632456 | 0.632456 |
| `‖A‖₂` | 0.900000 | 0.900000 |

The radius comes from the second pair, although the largest single rate, 0.9, sits
in the first. The norm sees only that largest rate. It cannot see that agent 1's
partner has rate 0.4 and damps everything agent 1 passes on.

## Worked example 2 — the fixed point as a finite sum

For the cyclic shift on `n` coordinates, `(DQ)ⁿ = c I` with `c = a₁⋯aₙ` (Lesson 2).
The Neumann series for `(I − DQ)⁻¹` then folds up after `n` terms:

```
x* = (I − DQ)⁻¹ b = ( b + (DQ) b + ⋯ + (DQ)ⁿ⁻¹ b ) / (1 − c),     b = (I − D) p.
```

For the Series II rates and anchor, the script finds the fixed point
`(0.754190, 0.527933, 0.508380)` by solving the linear system. The three-term formula
differs from it by 0.0e+00.

## What the restriction keeps, and what it loses

It keeps the two ingredients of the model that the papers cared about. One is the pull
of each agent's own initial opinion, through `I − D`. The other is the pull of others,
through `DQ`.
With a permutation every question about convergence has a closed-form answer, which is
why the papers could prove everything by hand.

It loses what makes the model interesting in social science. An agent cannot weigh
several others at once, influence cannot spread from one cycle to another, and nobody
can be more influential than anybody else. A general row-stochastic `W` can do all of
these. Roadmap stage 6 in this repository measures, by dimension, how small a part of
the Friedkin–Johnsen operators the papers' setting reaches.

## Where the original papers went wrong

Series II and III had every ingredient of the formulas above. They used the cyclic
shift and let the rates differ. They reported `maxᵢ aᵢ` as the rate, which is the
norm, and did not take the product round the cycle, which is the radius. The step
from the norm to the radius here is one line of algebra, `(DQ)ⁿ = (∏aᵢ) I`. **When a
problem can be solved exactly, a bound is the wrong thing to report.**

## Exercises

1. Show that the singular values of `DQ` are the absolute values of the rates, for any
   permutation matrix `Q`.
2. For `a = (0.9, 0.4, 0.5, 0.8)`, which single rate would you lower, and by how much,
   to make the two pairs equally fast?
3. Derive the finite-sum formula for `x*` from `(DQ)ⁿ = cI`.
4. Give an example of a row-stochastic `W` that is not a permutation, and explain in
   words one thing the resulting model can express that no permutation can.

<details>
<summary>Answers</summary>

1. `(DQ)(DQ)ᵀ = D Q Qᵀ D = D²`, because `QQᵀ = I`. The singular values are the square
   roots of the eigenvalues of `D²`, which are `|aᵢ|`.
2. The pairs have geometric means `√(0.9 × 0.4) = 0.6` and `√(0.5 × 0.8) ≈ 0.632`, so
   the second pair is the slower one. Lowering its rate 0.8 to 0.72 gives
   `√(0.5 × 0.72) = 0.6`. Lowering 0.5 to 0.45 works too.
3. `(I − A)(I + A + ⋯ + Aⁿ⁻¹) = I − Aⁿ = (1 − c) I`, so
   `(I − A)⁻¹ = (I + A + ⋯ + Aⁿ⁻¹) / (1 − c)`.
4. For example `W = [[0.5, 0.5], [0.5, 0.5]]`. Each agent weighs both opinions equally.
   With a permutation an agent can listen to only one other.

</details>

## References

- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206. doi:10.1080/0022250X.1990.9990069
- Horn, R. A., and Johnson, C. R. (2013). *Matrix Analysis* (2nd ed.). Cambridge
  University Press.
- Proskurnikov, A. V., and Tempo, R. (2017). A tutorial on modeling and analysis of
  dynamic social networks. Part I. *Annual Reviews in Control*, 43, 65–79.
  doi:10.1016/j.arcontrol.2017.03.002

## License and use of AI

This lesson text is licensed under CC BY 4.0. The code is MIT. See `lessons/README.md`.
The lesson was drafted with Claude Code (Anthropic) at the author's request. The
author is responsible for it. Claude is not an author.
