# Repeated games through the cyclic operator

*A golden-ratio threshold, a proved family, and two conjectures.* Draft. The author has
not yet reviewed this note.

**Run:** `python3 games/games.py` from the root of this repository. Every number on this
page comes from that script. `python3 verification/check_games.py` fails if the page and
the script disagree, and checks each proposition by a separate computation.

## Status

| | statement | status |
| --- | --- | --- |
| Lemma 1 | continuation values of a cyclic path are the fixed point of the papers' operator | proved; textbook |
| Proposition 1 | the three-player rotation is an equilibrium exactly when δ ≥ 1/φ | proved |
| Proposition 2 | the n-player rotation threshold lies just below 1/(n − 2) | proved |
| Proposition 3 | the example `(2,4,2)` printed in Series II §4 is never sustainable | proved |
| Proposition 4 | with public randomization, `(2+t, 4−t, 2+t)` is sustainable exactly when δ ≥ max(1/2, 1 − t) | proved |
| Proposition 5 | without randomization, the same holds for δ ≥ 2/3, and only two points survive for 1/2 ≤ δ < 1/φ | proved |
| Conjecture 1 | for 1/φ < δ < 2/3, the sustainable set has length zero | **conjecture** |
| Conjecture 2 | its dimension rises from 0 to 1 across that interval | **conjecture** |

A conjecture here means a statement that this note does not prove and has not found
proved elsewhere. The evidence for each is numerical and is reported with it.

None of the propositions has been checked against the literature. Some may be known
exercises. The model underneath is the Friedkin–Johnsen model with a cyclic influence
matrix (Friedkin and Johnsen 1990). The papers did not say so. See `E8` in the
Trinity-Infinity errata.

## Setting

The stage game `G_n` has `n` players who each choose C or D. If `k` of a player's
co-players choose C, the payoffs are

```
πC(k) = k + 1,     πD(k) = k + 2.
```

`G_3` is Table 1 of Series I. D strictly dominates, all-D is the unique stage
equilibrium, and it gives every player 2. Two is also every player's minmax payoff,
because D is a best reply to anything. The game is repeated for ever with common
discount factor δ and perfect monitoring. Payoffs are normalised as `(1 − δ) Σ δᵗ uₜ`.

Because the minmax payoff is a stage equilibrium payoff, reverting to all-D for ever is
the harshest credible punishment (Abreu 1988). A path of play is a subgame-perfect
equilibrium path exactly when, at every period, every player's continuation value is at
least

```
(1 − δ) · (best one-period deviation payoff) + 2δ.
```

## Lemma 1 — the bridge

Take a path that repeats with period `m`, and let `p_k` be one player's stage payoff at
phase `k`. The player's continuation values satisfy `V_k = (1 − δ) p_k + δ V_{k+1}`, that is

```
V = (1 − δ)(I − δS)⁻¹ p,     (S V)_k = V_{k+1}.
```

This is the fixed point of the papers' operator `x ← DQx + (I − D)p` with `D = δI` and
`Q = S`. The equilibrium test is a componentwise inequality on that fixed point. The
discount factor plays the part of the blend parameter.

For the rotation below with δ = 0.7, the fixed point is `(2.913242, 2.447489, 2.639269)`.
A direct sum of 2000 periods agrees with it, the largest difference being below 1e-14.

The identity is the standard formula for a discounted value. What it adds is a reading.
The Trinity-Infinity papers placed the operator and the repeated game side by side as a
"conceptual lens". Here the same fixed point decides the game.

## Proposition 1 — the golden ratio in three players

In the rotation, one player defects each period and the role passes round the cycle:
`(D,C,C) → (C,D,C) → (C,C,D) → …`. Its payoff vector for one player is `p = (4, 2, 2)`
by phase.

**Proposition 1.** In `G_3` the rotation is a subgame-perfect equilibrium path exactly when

```
δ ≥ (√5 − 1)/2 = 1/φ.
```

*Proof.* The defector already plays a best reply. A cooperator could switch to D and
get 3 for one period. The tightest constraint is on the player whose own defection is
furthest away, with value `(2 + 2δ + 4δ²)/(1 + δ + δ²)`. Requiring it to be at least
`3(1 − δ) + 2δ = 3 − δ` gives

```
δ³ + 2δ² − 1 = (δ + 1)(δ² + δ − 1) ≥ 0.
```

The positive root of `δ² + δ − 1` is `1/φ`. ∎

The script finds the threshold by bisection on Lemma 1, without using the polynomial:
0.618034. The value of `1/φ` is 0.618034.

## Proposition 2 — n players

Rotate a single defector among `n` players. A cooperator gets `n − 1`, the defector gets
`n + 1`, and a deviating cooperator gets `n`.

**Proposition 2.** For `n ≥ 3` there is a unique `δ_n` in (0, 1) such that the rotation
is an equilibrium path exactly when δ ≥ `δ_n`. It satisfies

```
1/(n − 2) − 2/(n − 2)ⁿ  <  δ_n  <  1/(n − 2).
```

*Proof.* A player `j` periods before their own defection has value
`n − 1 + 2h_j(δ)` with `h_j(δ) = (1 − δ)δʲ/(1 − δⁿ)`. The constraint binds at
`j = n − 1`, so the rotation is an equilibrium exactly when

```
f_n(δ) = (n − 2)δ − 1 + 2h(δ) ≥ 0,     h(δ) = δⁿ⁻¹/(1 + δ + … + δⁿ⁻¹).
```

`h` is increasing, because `1/h = δ^{−(n−1)} + … + δ⁻¹ + 1` is a sum of decreasing
terms. So `f_n` is strictly increasing, with `f_n(0) = −1` and `f_n(1) = n − 3 + 2/n > 0`.
Its root is `δ_n`. Since `h > 0`, `δ_n < 1/(n − 2)`. Since `h(δ) ≤ δⁿ⁻¹`,
`1 − (n − 2)δ_n < 2(n − 2)^{−(n−1)}`, which is the lower bound. ∎

| n | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `δ_n` | 0.618034 | 0.448223 | 0.328121 | 0.249636 | 0.199980 | 0.166666 | 0.142857 | 0.125000 |

The gap to `1/(n − 2)` closes faster than any power of `1/n`.

## Proposition 3 — the printed example

Series II §4 says that `(2,4,2)` is "eventually sustainable", at a higher discount
threshold.

**Proposition 3.** For no δ < 1 is `(2,4,2)` an equilibrium payoff of the repeated
`G_3`, subgame-perfect or Nash, with or without mixed strategies or public
randomization.

*Proof.* Four is the largest stage payoff in the table, and only `(C,D,C)` gives it to
player 2. An average of 4 therefore requires `(C,D,C)` in every period on the path.
There player 1 gets 2. Switching to D gives 3 at once, and never less than 2 afterwards,
because D always guarantees 2. The deviation is worth at least `3(1 − δ) + 2δ > 2`. ∎

This corrects the Series II example. It also corrects `E7` of the Trinity-Infinity
errata, which describes the example as correct on its own.

## Proposition 4 — the segment, with public randomization

The point `(2+t, 4−t, 2+t)` with `0 < t ≤ 1` lies between `(2,4,2)` and `(3,3,3)`.

**Proposition 4.** With a public randomization device, `(2+t, 4−t, 2+t)` is a
subgame-perfect equilibrium payoff exactly when

```
δ ≥ max(1/2, 1 − t).
```

At `t = 1` this is the threshold δ* = 1/2 of Series I. As `t → 0` it tends to 1. This is
the precise sense in which `(2,4,2)` is approached and never reached.

*Proof.* Every stage outcome satisfies `v₂ + (v₁ + v₃)/2 ≤ 6`, with equality only at
`(C,C,C)` and `(C,D,C)`. The target point attains 6, so the path uses only these two
outcomes. In both, player 1 cooperates and gains exactly 1 by deviating. The constraint
is that player 1's expected continuation value is at least `c = 2 + (1 − δ)/δ`. Continuation
values never exceed 3, so `c ≤ 3`, which is δ ≥ 1/2. Player 1's value today is then at least
`2(1 − δ) + δc = 3 − δ`, which is `t ≥ 1 − δ`. The argument does not use purity, so
it also holds for mixed strategies.

Conversely, every value in `[3 − δ, 3]` is a lottery between `(C,C,C)` followed by 3 and
`(C,D,C)` followed by `c`. Both continuations lie in the same interval, so the interval
generates itself (Abreu, Pearce and Stacchetti 1990). Player 2's constraint in `(C,C,C)`
needs the continuation `6 − w ≥ 3 ≥ c`, which holds. ∎

## Proposition 5 — without randomization

Now restrict to pure strategies and no randomization device. As in Proposition 4, the
path uses only `(C,C,C)` and `(C,D,C)`. The continuation value of player 1 must stay in
`[c, 3]`, and moves by

```
w′ = (w − (1 − δ)u)/δ,     u ∈ {2, 3}.
```

This is the scalar operator `w = (1 − δ)u + δw′` run backwards. Write `T_δ` for the set of
`t` in (0, 1] for which `(2+t, 4−t, 2+t)` is a pure-strategy equilibrium payoff.

**Proposition 5.**

1. For δ < 1/2, `T_δ` is empty.
2. For 1/2 ≤ δ < 1/φ, `T_δ = {δ, 1}`.
3. For δ ≥ 2/3, `T_δ = [1 − δ, 1]`.

*Proof.* (1) is Proposition 4. From `w`, the branch `u = 2` stays in `[c, 3]` exactly for
`w ≤ 2 + δ`, and `u = 3` exactly for `w ≥ 4 − 2δ`. The first range is non-empty exactly
when `c ≤ 2 + δ`, that is `δ² + δ − 1 ≥ 0`. This is the polynomial of Proposition 1
again. Below `1/φ` only `u = 3` is available, and it pushes every `w < 3` away from 3,
so only `w = 3` survives. Starting values are then `2 + δ` and `3`. This is (2). For
δ ≥ 2/3 the two ranges cover `[c, 3]`, so every value in it continues for ever. Read
from `[3 − δ, 3]`, the same two branches reach `[c, 3]` from every starting value. This
is (3). ∎

The script searches 40 periods ahead on the grid `t = 0.01, …, 1`. It finds
`{0.5, 1}` at δ = 0.5, `{0.55, 1}` at δ = 0.55, and `{0.6, 1}` at δ = 0.6.

## Two conjectures

Between `1/φ` and `2/3` both branches are available, but they leave a hole
`(2 + δ, 4 − 2δ)` between them. A value that falls into the hole cannot be continued.
The survivors form the set of points whose orbit never meets the hole.

**Conjecture 1.** For 1/φ < δ < 2/3, `T_δ` has Lebesgue measure zero.

**Conjecture 2.** For 1/φ < δ < 2/3, the Hausdorff dimension of `T_δ` is strictly between
0 and 1, is continuous and non-decreasing in δ, and tends to 0 as δ ↓ 1/φ and to 1 as
δ ↑ 2/3.

Evidence. The script refines `[c, 3]` for 22 periods. Below 2/3 the two branches have
disjoint images, so the surviving intervals do not overlap. The growth rate is the
number of intervals per period over the last five periods. The dimension estimate is
`log(growth)/log(1/δ)`.

| δ | intervals | total length | growth | dimension |
| --- | --- | --- | --- | --- |
| 0.62 | 134 | 5.16e-04 | 1.199 | 0.38 |
| 0.63 | 756 | 6.49e-03 | 1.325 | 0.61 |
| 0.64 | 1728 | 2.64e-02 | 1.380 | 0.72 |
| 0.65 | 3691 | 8.49e-02 | 1.427 | 0.83 |
| 0.66 | 5896 | 2.32e-01 | 1.466 | 0.92 |

In every row the growth rate is below `1/δ`, so the total length keeps shrinking. That
is the content of Conjecture 1. The dimension column rises with δ, which is the content of
Conjecture 2. Neither is a proof. The estimates come from a finite depth, and the limit
at either end is extrapolated.

Berg and Kitti (2014) study exactly this kind of object. They show that pure-strategy
equilibrium payoff sets of discounted repeated games can be fractals, and measure them
by Hausdorff dimension. Their methods may settle both conjectures for this game. That has
not been checked.

## What this does and does not say about Trinity-Infinity

It does not make the papers' operator new. The operator is a special case of the
Friedkin–Johnsen model, and the bridge in Lemma 1 is the textbook formula for a
discounted value.

What it does is give the papers' juxtaposition of an operator and a repeated game a
single equation. It replaces a false example with a proved family that passes through
Series I's δ* = 1/2. It also leaves two questions that this note cannot answer.

## References

- Abreu, D. (1988). On the theory of infinitely repeated games with discounting.
  *Econometrica*, 56(2), 383–396.
- Abreu, D., Pearce, D., and Stacchetti, E. (1990). Toward a theory of discounted
  repeated games with imperfect monitoring. *Econometrica*, 58(5), 1041–1063.
- Berg, K., and Kitti, M. (2014). Fractal geometry of equilibrium payoffs in discounted
  supergames. *Fractals*, 22(4).
- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206. doi:10.1080/0022250X.1990.9990069
- Fudenberg, D., and Maskin, E. (1986). The folk theorem in repeated games with
  discounting or with incomplete information. *Econometrica*, 54(3), 533–554.
- Nemoto, T. (2026). Trinity-Infinity Series I (revised). doi:10.5281/zenodo.22058624
- Nemoto, T. (2026). Trinity-Infinity Series II (revised). doi:10.5281/zenodo.22058777

## License and use of AI

This note is licensed under CC BY 4.0. The code is MIT. The note was drafted with
Claude Code (Anthropic) at the author's request, including the propositions, their
proofs and the conjectures. The author is responsible for it. Claude is not an author.
