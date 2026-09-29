# Lesson 4 — Errors that grow before they shrink

*The Friedkin–Johnsen model with a cyclic influence matrix — one operator, five lessons.* Draft. The author has not yet reviewed this lesson.

**Time:** about 60 minutes.
**You need:** Lesson 2, and the idea of a positive definite matrix.
**Run:** `python3 lessons/lesson4.py` from the root of this repository.
Every number on this page comes from that script. `verification/check_lessons.py`
fails if the page and the script disagree.

## What you will be able to do

1. Explain why a spectral radius below one guarantees that the error eventually
   decays, but not that it decays from the first step.
2. Compute the powers of a non-normal matrix by hand and locate the hump.
3. Build a norm in which the map is a contraction, so that Banach's argument works
   after all, and read off what that costs.

## The example

Lesson 2 ended with a matrix whose norm was above one and whose spectral radius was
one half. Take a sharper version of the same thing:

```
A = [[0.5, 20.0],
     [0.0,  0.5]]
```

The script reports `‖A‖₂ = 20.012492` and `ρ(A) = 0.500000`. By Lesson 2 the
iteration converges from every starting point. The question here is how.

## Powers by hand

Write `A = 0.5 I + 20 N` with `N = [[0, 1], [0, 0]]`. Then `N² = 0`, and `I` commutes
with `N`, so the binomial expansion stops after two terms:

```
Aᵏ = 0.5ᵏ I + 20 k 0.5ᵏ⁻¹ N.
```

The diagonal shrinks geometrically. The off-diagonal entry is a geometric factor
multiplied by `k`, and for small `k` the factor `k` wins. For `k = 1, …, 5` the
off-diagonal entries are

```
20, 20, 15, 10, 6.25
```

and the norms `‖Aᵏ‖₂` are `20.01, 20.00, 15.00, 10.00, 6.25`. The norms rise from
the size of the diagonal to about twenty, stay there for two steps, and only then
fall. The worst case over all starting points is `maxₖ ‖Aᵏ‖₂ = 20.01`.

## What an error actually does

Start from `(5, −3)`. The fixed point is `(1, 0)`, so the initial error has length 5.
The errors for the first five steps are

```
5.000, 58.019, 59.005, 44.502, 29.751
```

The error peaks at step 2, at 11.8 times its starting value, before the geometric
factor takes over.

Nothing like this happens in the setting of the original papers. There `A = DQ` with
`Q` a permutation, so every power of `A` is again a permutation with rates attached.
Its norm is a product of rates, each below one. For the Series II rates the norms of
the first four powers are `0.7000, 0.3500, 0.1050, 0.0735`. They only ever fall.

## Rescuing Banach's argument

In the Euclidean norm this `A` is not a contraction, so Banach's theorem cannot be
applied as it stands. The standard remedy is to change the norm. For any `ρ(A) < γ < 1`
there is a norm in which `A` shrinks every vector by a factor below `γ` (Householder
1964; Horn and Johnson 2013, §5.6). One way to build it is to solve the Stein
equation

```
P − Bᵀ P B = I,     B = A / γ,
```

and use `‖x‖_P = √(xᵀ P x)`. `certificate.py` does this with NumPy alone.
With `γ = 0.75` it returns a contraction constant `κ = 0.749937`. In the Euclidean
norm this gives

```
‖eₖ‖ ≤ 69.35 · κᵏ · ‖e₀‖.
```

The factor 69.35 is the price of changing norms. It is `√(λmax(P) / λmin(P))`, and it
must be at least as large as the hump, because the bound has to cover step 2 as well.
The script checks the bound against the actual error and finds that it holds for all 60 steps.

In the `P` norm the map is a contraction. Banach's theorem applies there as written,
and the conclusion carries over to the Euclidean norm because the two norms are
equivalent.

## The trade-off

`γ` is a dial. Moving it towards `ρ(A)` gives a faster rate and a larger constant.
The bound at step 20 is where the two meet:

| γ | κ | amplification | bound at step 20 |
| --- | --- | --- | --- |
| 0.55 | 0.549999 | 382.69 | 1.23e-02 |
| 0.60 | 0.599995 | 184.85 | 3.38e-02 |
| 0.75 | 0.749937 | 69.35 | 1.10e+00 |
| 0.90 | 0.899770 | 42.08 | 2.55e+01 |
| 0.99 | 0.989601 | 34.06 | 1.38e+02 |

The actual error at step 20 is 2.29e-03. Every row is a true bound, and none is
tight. Choosing the right-hand side of the Stein equation more cleverly than `I`
lowers the amplification further. The roadmap in this repository (stage 1) measures
how much.

## Where the original papers went wrong

The papers never looked outside permutations, and inside them nothing on this page
happens. The mistake is narrower. The papers gave `‖A‖ < 1` as the reason the
iteration converges. That makes the argument stop at the edge of their assumptions,
while the conclusion does not. Convergence continues all the way to `ρ(A) < 1`. So
does Banach's theorem, once the norm is chosen to fit the matrix instead of fixed in
advance. **An argument can fail where its conclusion still holds, and the repair is
often to change what you measure with, not what you claim.**

## Exercises

1. Prove the formula for `Aᵏ` above. For which `k` is the off-diagonal entry
   largest?
2. Show that if `A = DQ` with `Q` a permutation matrix, then `Aᵏ` is a permutation
   matrix with rates attached, and `‖Aᵏ‖₂` is the largest product of the rates met
   along `k` steps. Conclude that the error in the papers' setting never grows.
3. Using the trade-off table, which `γ` gives the smallest bound at step 20? Why does
   the smallest `γ` not always win at every step?
4. Why can `γ` not be taken equal to `ρ(A)`?

<details>
<summary>Answers</summary>

1. Expand `(0.5 I + 20 N)ᵏ` with the binomial theorem and use `N² = 0`. The entry
   `20 k 0.5ᵏ⁻¹` is the same for `k = 1` and `k = 2` and decreases after that.
2. A product of permutation matrices with rates is a permutation matrix with rates.
   Its singular values are the absolute values of those rates, so the norm is the
   largest of them, a product of numbers below one.
3. `γ = 0.55` among the rows shown. The bound is `amplification · κ²⁰ · ‖e₀‖`. A small
   `γ` pays a large amplification up front and recovers it only after enough steps.
   At small `k` a larger `γ` gives the smaller bound.
4. Then `ρ(B) = 1`, the Stein equation has no positive definite solution, and the
   amplification grows without bound as `γ` approaches `ρ(A)`.

</details>

## References

- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206. doi:10.1080/0022250X.1990.9990069
- Horn, R. A., and Johnson, C. R. (2013). *Matrix Analysis* (2nd ed.). Cambridge
  University Press. §5.6.
- Householder, A. S. (1964). *The Theory of Matrices in Numerical Analysis*.
  Blaisdell.
- Trefethen, L. N., and Embree, M. (2005). *Spectra and Pseudospectra: The Behavior
  of Nonnormal Matrices and Operators*. Princeton University Press.

## License and use of AI

This lesson text is licensed under CC BY 4.0. The code is MIT. See `lessons/README.md`.
The lesson was drafted with Claude Code (Anthropic) at the author's request. The
author is responsible for it. Claude is not an author.
