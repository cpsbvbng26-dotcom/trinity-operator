# Lesson 5 — Switching: when the sufficient condition earns its keep

*The Friedkin–Johnsen model with a cyclic influence matrix — one operator, five lessons.* Draft. The author has not yet reviewed this lesson.

**Time:** about 50 minutes.
**You need:** Lessons 2 and 4.
**Run:** `python3 lessons/lesson5.py` from the root of this repository.
Every number on this page comes from that script. `verification/check_lessons.py`
fails if the page and the script disagree.

## What you will be able to do

1. Give an example of two maps that each converge while their alternation diverges.
2. Explain why a spectral radius below one for each map says nothing about the
   switched system, while a single common norm in which every map contracts settles it.
3. Show that the Friedkin–Johnsen model with susceptibilities below one has such a
   common norm, so switching its influence network can never make it diverge.

## Two stable maps that diverge together

Take

```
A₁ = 0.7 [[1, 1],        A₂ = 0.7 [[1, 0],
          [0, 1]],                 [1, 1]].
```

Each has `ρ = 0.7`, so each on its own converges. Start from `(1, 1)`. After 40 steps
of `A₁` alone the vector has length 2.61e-05. After 40 steps alternating `A₁` and
`A₂` it has length 200.5.

The reason is the product. Two steps of the alternation apply `A₂A₁`, and
`ρ(A₂A₁) = 1.282837`. Each map shears the vector in a direction the other one
stretches. Lessons 2 and 4 said that the spectral radius decides convergence. That is
true for one map applied again and again. With switching, the relevant quantity is the
joint spectral radius of the set of maps (Jungers 2009), and deciding whether it is at
most one is, in general, undecidable (Blondel and Tsitsiklis 2000).

Note also that `‖A₁‖₂ = 1.132624`. Neither map is a contraction in the Euclidean norm.

## The rescue: one norm for all maps

Suppose there is a single norm in which every map in the set is a contraction with
constant at most `q < 1`. Then any product of `k` of them has norm at most `qᵏ`,
whatever the order. Switching cannot break convergence.

This is exactly the condition that Lesson 2 called redundant. For one map, requiring
`‖A‖ < 1` in a fixed norm was stronger than needed. For a family of maps applied in
any order, a common norm is what makes the argument work. The same condition can be
too strong for one question and just right for another.

## The papers' setting is switching-safe

In the papers' setting every map is `DQ` with `Q` a permutation, and its Euclidean
norm is the largest rate (Lesson 3). Switch at random between the forward shift with
rates `(0.5, 0.7, 0.3)` and the backward shift with rates `(0.9, 0.2, 0.6)`. Their norms
are `0.7 and 0.9`. Over 1000 random switching sequences of 40 steps, the largest norm
of the product is 8.79e-09. The common-norm bound `0.9⁴⁰` is 1.48e-02. It holds, and
it holds for every sequence, not just the ones sampled.

## So is the Friedkin–Johnsen model

The same is true well beyond permutations. In the Friedkin–Johnsen model, `W` is
row-stochastic, so every row of `ΛW` has non-negative entries summing to `λᵢ`. In the
maximum-row-sum norm this gives

```
‖ΛW‖∞ = maxᵢ λᵢ.
```

If every susceptibility is at most `λmax < 1`, every such map is a contraction in the
same norm with the same constant, whatever `W` is. The script draws 1000 random runs
of 40 steps, with a fresh random row-stochastic `W` and fresh susceptibilities below
0.9 at every step. The largest `∞`-norm of any product is 8.49e-13, again inside the
bound 1.48e-02.

The shear pair above is not a Friedkin–Johnsen system. Its rows do not sum to one.
Divergence under switching needs maps that leave the model.

## Where the original papers went wrong

The papers did not consider switching, so there is no error to correct here. There is
something to take back instead. Earlier lessons treated the papers' norm argument as
the weaker, cruder tool. For a single fixed map it is. But the papers' own setting,
and the model it belongs to, is one where the norm argument extends to time-varying
networks for free, and the spectral argument does not extend at all. **Which condition
is "the right one" depends on the question being asked.**

## Exercises

1. Compute `A₂A₁` for the shear pair and verify that its spectral radius exceeds one.
2. Prove that `‖ABx‖ ≤ ‖A‖‖B‖‖x‖` for any induced norm, and use it to bound a product
   of `k` maps that are each contractions with constant `q` in the same norm.
3. Show that `‖ΛW‖∞ = maxᵢ λᵢ` when `W` is row-stochastic and `Λ` is diagonal with
   non-negative entries.
4. Give a pair of maps, each of the form `DQ` with `Q` a permutation, whose alternation
   diverges, or explain why no such pair exists when every rate is below one.

<details>
<summary>Answers</summary>

1. `A₂A₁ = 0.49 [[1, 1], [1, 2]]`. The eigenvalues of `[[1, 1], [1, 2]]` are
   `(3 ± √5)/2`, the larger about 2.618, and `0.49 × 2.618 ≈ 1.283`.
2. By definition of the induced norm, `‖ABx‖ ≤ ‖A‖‖Bx‖ ≤ ‖A‖‖B‖‖x‖`. By induction a
   product of `k` such maps has norm at most `qᵏ`.
3. The `i`-th row of `ΛW` is `λᵢ` times the `i`-th row of `W`. Its entries are
   non-negative and sum to `λᵢ`. The `∞`-norm is the largest absolute row sum.
4. None exists. Each such map has Euclidean norm equal to its largest rate, below one,
   so the Euclidean norm is a common norm and every product contracts.

</details>

## References

- Blondel, V. D., and Tsitsiklis, J. N. (2000). The boundedness of all products of a
  pair of matrices is undecidable. *Systems & Control Letters*, 41(2), 135–140.
- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206. doi:10.1080/0022250X.1990.9990069
- Jungers, R. M. (2009). *The Joint Spectral Radius: Theory and Applications*.
  Springer.

## License and use of AI

This lesson text is licensed under CC BY 4.0. The code is MIT. See `lessons/README.md`.
The lesson was drafted with Claude Code (Anthropic) at the author's request. The
author is responsible for it. Claude is not an author.
