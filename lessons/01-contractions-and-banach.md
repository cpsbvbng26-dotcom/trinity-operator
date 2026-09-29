# Lesson 1 — Contractions and Banach's theorem

*The Friedkin–Johnsen model with a cyclic influence matrix — one operator, five lessons.* Draft. The author has not yet reviewed this lesson.

**Time:** about 40 minutes.
**You need:** vectors, matrices, and the idea of a limit.
**Run:** `python3 lessons/lesson1.py` from the root of this repository.
Every number on this page comes from that script. `verification/check_lessons.py`
fails if the page and the script disagree.

## What you will be able to do

1. State Banach's fixed-point theorem and check its hypothesis for a linear map.
2. Compute the fixed point of the model in closed form.
3. Say exactly why the norm argument is sharp in this lesson's setting, and why that
   will stop being true in Lesson 2.

## The simplest case

Three agents sit in a ring. Each listens to the one before it, keeps a share `α` of
what it hears, and holds on to its own initial opinion with the rest:

```
x ← α Q x + (1 − α) p,
```

where `Q` is the cyclic shift `(Qx)ᵢ = xᵢ₋₁` (indices mod 3). In the notation of the
Friedkin–Johnsen model this is `Λ = αI` and `W = Q`: every agent is equally
susceptible, and the influence network is a directed cycle. This is the setting of
the first *Trinity-Infinity* paper (Series I), with `α = 0.6` and `p = (1, 0, 0)`.

## Banach's theorem

Let `(X, d)` be a complete metric space and `f : X → X` a contraction, meaning
`d(f(x), f(y)) ≤ q d(x, y)` for some `q < 1` and all `x, y`. Then `f` has exactly one
fixed point `x*`, the iteration `xₖ₊₁ = f(xₖ)` converges to it from every start, and

```
d(xₖ, x*) ≤ qᵏ / (1 − q) · d(x₁, x₀).
```

For our map, `f(x) − f(y) = αQ(x − y)`. The shift only reorders coordinates, so it
preserves Euclidean length, and therefore

```
‖f(x) − f(y)‖ = α ‖x − y‖.
```

This is a contraction with `q = α`, and the equality is exact: the map shrinks every
difference by exactly `α`, in every direction.

## The fixed point

Setting `x* = αQx* + (1 − α)p` and solving gives

```
x* = (1 − α)(I − αQ)⁻¹ p.
```

The script finds the fixed point `(0.510204, 0.306122, 0.183673)` by iteration. The
closed form differs from it by 0.0e+00. The opinion of the first agent, whose own
anchor is 1, is pulled down by the chain of listeners. The others, whose anchors are
0, are pulled up by the one agent upstream of them.

## Watching it converge

Start from `(0.2, 0.9, 0.5)`. The ratios of successive errors for the first three
steps are `0.600000, 0.600000, 0.600000`, exactly `α` each time, as the equality above
says they must be. After 20 steps the error is 2.71e-05. Banach's a priori bound
predicts at most 8.48e-05. The bound holds. It is loose only by the constant
`1 / (1 − q)`, which Banach pays in order to need nothing but the first step.

## Why this case is special

The script also reports `‖A‖₂ = 0.600000` and `ρ(A) = 0.600000`. The operator norm and
the spectral radius coincide. That is because `A = αQ` is a multiple of an orthogonal
matrix, which is normal, and for normal matrices the two are always equal. So in this
setting the norm argument loses nothing: the contraction constant is the true rate.

This is the part the original papers got right, and it is worth being clear about.
Series I proved a correct theorem with the right tool. The trouble begins in Lesson 2,
where the rates are allowed to differ, `A` stops being a multiple of an orthogonal
matrix, and the same argument quietly becomes an overestimate.

## Exercises

1. Show that `‖Qx‖ = ‖x‖` for the cyclic shift, and conclude that `‖αQ‖₂ = α`.
2. Verify the closed form for `x*` by substituting it into the fixed-point equation.
3. Why does the a priori bound use `d(x₁, x₀)` and not `d(x₀, x*)`?
4. For `n = 2` the cyclic shift is its own inverse. For `n = 3` it is not. Does
   anything in this lesson depend on `n`?

<details>
<summary>Answers</summary>

1. `Qx` has the same entries as `x` in a different order, so the sum of squares is
   unchanged. Hence `‖αQx‖ = α‖x‖` for every `x`, and the norm is exactly `α`.
2. `αQx* + (1 − α)p = αQ(1 − α)(I − αQ)⁻¹p + (1 − α)(I − αQ)(I − αQ)⁻¹p
   = (1 − α)(I − αQ)⁻¹p = x*`.
3. Because `x*` is unknown when the bound is used. `x₁` and `x₀` are computed, so
   the bound can be evaluated before the limit is known.
4. No. The argument used only that `Q` preserves length. It holds for every `n ≥ 2`,
   which is what Series III found, and in fact for every permutation matrix.

</details>

## References

- Banach, S. (1922). Sur les opérations dans les ensembles abstraits et leur
  application aux équations intégrales. *Fundamenta Mathematicae*, 3, 133–181.
- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206. doi:10.1080/0022250X.1990.9990069
- Horn, R. A., and Johnson, C. R. (2013). *Matrix Analysis* (2nd ed.). Cambridge
  University Press.

## License and use of AI

This lesson text is licensed under CC BY 4.0. The code is MIT. See `lessons/README.md`.
The lesson was drafted with Claude Code (Anthropic) at the author's request. The
author is responsible for it. Claude is not an author.
