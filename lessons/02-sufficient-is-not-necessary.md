# Lesson 2 — A sufficient condition is not a necessary one

*One operator, five lessons.* Draft. The author has not yet reviewed this lesson.

**Time:** about 45 minutes.
**You need:** eigenvalues, matrix norms, and enough Python to run a script.
**Run:** `python3 lessons/lesson2.py` from the root of this repository.
Every number on this page comes from that script. `verification/check_lessons.py`
fails if the page and the script disagree.

## What you will be able to do

1. State the difference between "the operator norm is below one" and "the spectral
   radius is below one", and say which one decides convergence.
2. Compute both quantities for the operator used throughout this module, by hand.
3. Recognise when a proof has used the stronger condition where the weaker one was
   the true boundary.

## The operator

Throughout the module we iterate

```
x ← A x + b,     A = D Q,     b = (I − D) p
```

where `D = diag(a)` holds a rate `aᵢ` for each coordinate, `Q` moves the coordinates
around, and `p` is a fixed anchor. If `x*` is the fixed point and `eₖ = xₖ − x*` is
the error after `k` steps, the anchor drops out:

```
eₖ₊₁ = A eₖ,     so     eₖ = Aᵏ e₀.
```

Everything about convergence is therefore a question about the powers of `A`.

## Two conditions

**The norm condition.** If `‖A‖ < 1` in some norm, the map is a contraction in that
norm. Banach's fixed-point theorem then gives a unique fixed point and

```
‖eₖ‖ ≤ ‖A‖ᵏ ‖e₀‖.
```

**The spectral condition.** The iteration converges from every starting point if and
only if `ρ(A) < 1`, where `ρ(A)` is the largest absolute value of an eigenvalue.
This is a standard result (Varga 2000; Horn and Johnson 2013, §5.6).

For every induced norm, `ρ(A) ≤ ‖A‖`. So the norm condition implies the spectral one.
The converse fails. **The norm condition is sufficient, and only the spectral condition
is necessary.**

## Worked example 1 — inside the original setting

The papers this module grew out of (the *Trinity-Infinity* series) take `Q` to be the
cyclic shift on three coordinates. Series II uses the rates `a = (0.5, 0.7, 0.3)`.
The script reports:

| quantity | value |
| --- | --- |
| `‖A‖₂` | 0.700000 |
| `ρ(A)` | 0.471769 |
| `a₁a₂a₃` | 0.105 |

The two numbers already differ. Here is why, by hand. Shifting three times returns
every coordinate to its place, and each shift multiplies by one of the rates on the
way. So

```
A³ = (a₁ a₂ a₃) I = 0.105 I.
```

The script confirms that the largest entry of `A³ − 0.105 I` is 0.0e+00. The
characteristic polynomial is `λ³ − a₁a₂a₃`. Every eigenvalue therefore has absolute
value `(a₁a₂a₃)^(1/3)`, the geometric mean of the rates. That is 0.471769, the
spectral radius.

The identity says more than the eigenvalues do. Every three steps, **from any starting
point**, the error is multiplied by exactly 0.105. The script measures the ratio after
three steps as 0.105000.

Now compare the two bounds after 30 steps.

| | error after 30 steps, relative to the start |
| --- | --- |
| actual | 1.63e-10 |
| the norm bound `‖A‖₂³⁰` | 2.25e-05 |

The norm bound is true. It is also five orders of magnitude too pessimistic, because
it uses the largest rate where the geometric mean is what governs.

## Worked example 2 — outside the original setting

Let `Q` stop being a permutation. With

```
A = [[0.5, 2.0],
     [0.0, 0.5]]
```

the script reports `‖A‖₂ = 2.118034` and `ρ(A) = 0.500000`. The norm condition fails
badly. In the Euclidean norm this map is not a contraction, and the Banach argument
cannot even start. Yet the spectral radius is one half, so the iteration must converge.

It does, but not the way the norm picture suggests. Starting from `(0, 1)`, the errors
for the first five steps are

```
1.4142, 1.5811, 1.7678, 1.3807, 0.9396
```

The error grows for two steps, reaching 1.25 times its starting value, and only then
decays. After 40 steps it is 1.45e-10. Lesson 4 explains the growth. Such matrices
are called non-normal, and Lesson 4 builds a different norm in which the map is a
contraction after all.

## Where the original papers went wrong

The three papers proved `‖A‖₂ < 1` and wrote as if that settled both whether the
iteration converges and how fast. In Series I (all rates equal) nothing visibly goes
wrong, because there `A` is a multiple of an orthogonal matrix and the two conditions
coincide. Series II made the rates unequal and kept the norm argument. The stated
rate, the largest `aᵢ`, was then loose by five orders of magnitude after 30 steps, as
worked example 1 shows. The identity `A³ = (a₁a₂a₃) I` that exposes this was later
derived independently by an automated reviewer. It is recorded as N9 in the errata of
the `trinity-infinity` repository.

The error is common and worth naming. **A proof that goes through a sufficient
condition tells you that something happens. It does not tell you where the boundary
is.**

## Exercises

1. Show by multiplying out the matrices that `(DQ)³ = (a₁a₂a₃) I` when `Q` is the
   cyclic shift on three coordinates. Does the same hold for `n` coordinates with
   `n` steps?
2. Take `a = (0.9, 0.9, 0.1)` with the same `Q`. Compute `‖A‖₂` and `ρ(A)` by hand,
   then check them with `TrinityOperator` from `trinity.py`.
3. Find another 2 × 2 matrix with `‖A‖₂ ≥ 1` and `ρ(A) < 1`. Explain, using `Aᵏ`,
   why the error must eventually shrink.
4. True or false: "If the iteration converges from every starting point, then
   `‖A‖₂ < 1`."

<details>
<summary>Answers</summary>

1. Each application of `DQ` moves every coordinate one place and multiplies it by one
   rate. After three applications each coordinate is back in place and has been
   multiplied by all three rates once. For `n` coordinates, `(DQ)ⁿ = (a₁⋯aₙ) I`.
2. `‖A‖₂ = 0.900000`, the largest rate. `ρ(A) = 0.432675`, the cube root of
   `0.9 × 0.9 × 0.1 = 0.081`.
3. Any upper-triangular matrix with diagonal entries of absolute value below one and a
   large enough off-diagonal entry will do. Since `ρ(A) < 1`, `Aᵏ → 0`, so
   `eₖ = Aᵏ e₀ → 0` whatever the norm of `A`.
4. False. Worked example 2 converges from every starting point with `‖A‖₂ = 2.118034`.

</details>

## References

- Horn, R. A., and Johnson, C. R. (2013). *Matrix Analysis* (2nd ed.). Cambridge
  University Press. §5.6.
- Varga, R. S. (2000). *Matrix Iterative Analysis* (2nd ed.). Springer.

## License and use of AI

This lesson text is licensed under CC BY 4.0. The code is MIT. See `lessons/README.md`.
The lesson was drafted with Claude Code (Anthropic) at the author's request. The
author is responsible for it. Claude is not an author.
