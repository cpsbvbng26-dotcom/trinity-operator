# Repeated games through the cyclic operator

*A golden-ratio threshold, a proved family, and the golden-window conjecture.* Draft, first
written on 2026-10-04, before the preprint below. The repository records no review of this
note by the author.

**Preprint.** An English paper version of Propositions 1–7 and the conjecture is on Figshare:
[`10.6084/m9.figshare.34419198`](https://doi.org/10.6084/m9.figshare.34419198) (2026-10-13).
The preprint is frozen. This page and its script remain the maintained version. The preprint
states both parts of the conjecture as conjectures, and it stays that way. Propositions 8 and
9, which prove them, are in this note and in the resolution paper below.

**Resolution paper.** A paper that resolves the conjecture is on Figshare:
[`10.6084/m9.figshare.35050300`](https://doi.org/10.6084/m9.figshare.35050300). The DOI was
received from the owner on 2026-11-18. It is a separate item, not a new version of the
preprint above. It contains Propositions 8 and 9 with their proofs, and further results. Its
source, PDF and scripts are in
[golden-window-resolution](https://github.com/cpsbvbng26-dotcom/golden-window-resolution).
It is a preprint and has not been peer-reviewed.

**Run:** `python3 games/games.py` from the root of this repository. Every number on this
page comes from that script, except the wider scan of the window, which comes from
`python3 games/scan.py`. `python3 verification/check_games.py` fails if the page and
the scripts disagree, and checks each proposition by a separate computation.

## Status

| | statement | status |
| --- | --- | --- |
| Lemma 1 | continuation values of a cyclic path are the fixed point of the papers' operator | proved; textbook |
| Proposition 1 | the three-player rotation is an equilibrium exactly when δ ≥ 1/φ | proved |
| Proposition 2 | the n-player rotation threshold lies just below 1/(n − 2) | proved |
| Proposition 3 | the example `(2,4,2)` printed in Series II §4 is never sustainable | proved |
| Proposition 4 | with public randomization, `(2+t, 4−t, 2+t)` is sustainable exactly when δ ≥ max(1/2, 1 − t) | proved |
| Proposition 5 | without randomization, the same holds for δ ≥ 2/3; only two points survive for 1/2 ≤ δ < 1/φ, and a countable set at δ = 1/φ | proved |
| Proposition 6 | inside the window 1/φ < δ < 2/3, the sustainable set has positive Hausdorff dimension | proved |
| Proposition 7 | with benefit b and cost c, the rotation is possible exactly when cooperation is efficient, and always needs more patience than full cooperation | proved |
| Proposition 8 | inside the window 1/φ < δ < 2/3, the sustainable set has length zero | proved |
| Proposition 9 | inside the window, the dimension of the sustainable set is the root `s` of `Σ_{n ∈ A_δ} δ^(ns) = 1`; it is below 1, continuous and strictly increasing, and runs from 0 to 1 across the interval | proved |
| Golden-window conjecture (a) | for 1/φ < δ < 2/3, the sustainable set has length zero | resolved (Proposition 8); a special case of known theorems |
| Golden-window conjecture (b) | its dimension is below 1, continuous and non-decreasing, and runs from 0 to 1 across the interval | resolved (Proposition 9); the formula is a special case of known theorems; continuity, strict increase and the end limits were not found in the texts read |

A conjecture here means a statement that this note does not prove and has not found
proved elsewhere. The evidence for each is numerical and is reported with it. Parts (a) and
(b) were conjectures until 2026-11-18. They are now proved as Propositions 8 and 9, and their
rows keep their names. The name golden-window conjecture stays as the name of the problem,
because it is already in published DOIs and in issue labels. Its status is resolved (part (a) and the formula of part (b) are special cases of known theorems; continuity and strict increase in δ and the limits at both ends were not found in the texts read).
The literature check of 2026-11-18 is recorded below, in the section of that name.

Propositions 1–7 have not been checked against the literature. Some may be known
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

Its first-order size is now known (added on 2026-11-19). Write `m = n − 2`. As `n → ∞`,

```
1/m − δ_n  =  2(m − 1)/m^(n+1) · (1 + O(n m^(−(n−1)))).
```

So the lower bound of Proposition 2 is sharp up to the factor `(m − 1)/m`. This is the case
`r = 1` of Proposition 8.10 of the resolution paper
([`10.6084/m9.figshare.35050300`](https://doi.org/10.6084/m9.figshare.35050300)), which gives
the first-order term for every `r` in the setting of Proposition 7. It is proved there, not on
this page. The paper is a preprint and has not been peer-reviewed.
`python3 verification/check_games.py` compares the formula with a bisection at high
precision.

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
3. At δ = 1/φ, `T_δ` is countably infinite.
4. For δ ≥ 2/3, `T_δ = [1 − δ, 1]`.

*Proof.* (1) is Proposition 4. From `w`, the branch `u = 2` stays in `[c, 3]` exactly for
`w ≤ 2 + δ`, and `u = 3` exactly for `w ≥ 4 − 2δ`. The first range is non-empty exactly
when `c ≤ 2 + δ`, that is `δ² + δ − 1 ≥ 0`. This is the polynomial of Proposition 1
again. Below `1/φ` only `u = 3` is available, and it pushes every `w < 3` away from 3,
so only `w = 3` survives. Starting values are then `2 + δ` and `3`. This is (2). At
δ = 1/φ exactly, `c = 2 + δ`, so the branch `u = 2` is available only at `w = c`, and it
sends `c` to 3. Every other value is pushed away from 3 by `u = 3`. The survivors are 3 and
the points `3 − (3 − c)δⁿ`, which reach `c` after `n` periods. The starting values are their
images under the two branches, a countably infinite set. This is (3). For δ ≥ 2/3 the two
ranges cover `[c, 3]`, so every value in it continues for ever. Read from `[3 − δ, 3]`,
the same two branches reach `[c, 3]` from every starting value. This is (4). ∎

The script searches 40 periods ahead on the grid `t = 0.01, …, 1`. It finds
`{0.5, 1}` at δ = 0.5, `{0.55, 1}` at δ = 0.55, and `{0.6, 1}` at δ = 0.6.
At δ = 1/φ it follows the first eight points `3 − (3 − c)δⁿ`, and 8 of them reach 3.

## Proposition 6 — positive dimension inside the window

Change variables to `x = (3 − w)/(1 − δ)`. The recursion `w = (1 − δ)u + δw′` becomes

```
x = a + δx′,     a = 3 − u ∈ {0, 1},
```

on the interval `[0, X]` with `X = (2δ − 1)/(δ(1 − δ))`. Read backwards, `x′ = (x − a)/δ`.
The branch `a = 0` keeps `x′` in `[0, X]` exactly when `x ≤ δX`, and `a = 1` exactly when
`x ≥ 1`. This is an expansion in the non-integer base `β = 1/δ` with the hole `(δX, 1)`.
Inside the window `δX < 1 < X`, and `β` lies between 3/2 and φ.

**Proposition 6.** For 1/φ < δ < 2/3, the Hausdorff dimension of `T_δ` is at least the
positive solution `s` of

```
δ^((n₀+1)s) = 1 − δ^s,     n₀ = the least n with δ^(−(n+1)) ≥ X/(X − 1).
```

In particular it is positive.

*Proof.* Take `x` in `[1, X]`, apply `a = 1`, then `a = 0` for `n` periods. The result is
`δ^(−(n+1))(x − 1)`. It lands in `[1, X]` exactly for `x` in
`J_n = [1 + δ^(n+1), 1 + Xδ^(n+1)]`. Every intermediate value lies in `[0, δX]`, so the
orbit never meets the hole. `J_n` lies inside `[1, X]` exactly when
`δ^(−(n+1)) ≥ X/(X − 1)`, that is `n ≥ n₀`. `J_(n+1)` and `J_n` are disjoint because
`Xδ < 1`. Each branch maps `J_n` onto `[1, X]` linearly with ratio `δ^(−(n+1))`. The limit
set of the inverse maps is self-similar and satisfies the open set condition, so its
dimension `s` solves `Σ_(n ≥ n₀) δ^((n+1)s) = 1`, which sums to the equation above. That
set lies in the survivor set, and `T_δ` is a union of affine images of the survivor set, so
its dimension is at least `s`. ∎

The values of `n₀` and of the lower bound are the last two columns of the table below.

## Proposition 7 — general benefit and cost

Replace the payoffs by a linear dilemma. A cooperator pays `c > 0` and gives `b > 0` to every
co-player, so `πC(k) = bk − c` and `πD(k) = bk`. Up to the constant 2, `G_n` is the case
`b = c = 1`. Write `r = c/b`. D is still a best reply to everything, the minmax payoff is 0,
and all-D for ever is still the harshest punishment. In biological terms δ is read as the
probability of meeting again.

**Proposition 7.**

1. The `n`-player rotation is a subgame-perfect equilibrium path for some δ < 1 exactly when
   `r < n − 1`, that is, when cooperation is efficient: `(n − 1)b > c`. Then there is a unique
   threshold `δ_n(r)`, and

   ```
   r/(n − 2) − (1 + r) r^(n−1)/(n − 2)ⁿ  <  δ_n(r)  <  r/(n − 2).
   ```

2. For three players, `δ_3(r) = (√(1 + 4r) − 1)/2`. At `r = 1` this is `1/φ`.
3. `δ_n(r) > r/(n − 1)`, the threshold at which everyone cooperating in every period is an
   equilibrium.

*Proof.* Repeat Proposition 2 with these payoffs. The cooperator furthest from their own
defection binds, and the condition becomes

```
g(δ) = (n − 2)δ − r + (1 + r)h(δ) ≥ 0,     h as in Proposition 2.
```

`g` is strictly increasing, with `g(0) = −r` and `g(1) = n − 2 − r + (1 + r)/n`. The last is
positive exactly when `(n − 1)² > r(n − 1)`, that is `r < n − 1`. The bounds follow as in
Proposition 2. This is (1). For `n = 3`, multiplying by `1 + δ + δ²` gives
`(δ + 1)(δ² + δ − r) ≥ 0`. This is (2). Everyone cooperating is an equilibrium exactly when
`b(n − 1) − c ≥ (1 − δ)b(n − 1)`, that is `δ ≥ r/(n − 1)`. At that δ, `g(δ) = (1 + r)h(δ) − δ`.
Here `(1 + r)δ^(n−2) = δ^(n−2) + (n − 1)δ^(n−1)`, which is less than `1 + δ + … + δ^(n−1)`,
because each of the `n − 2` terms `1, …, δ^(n−3)` exceeds `δ^(n−1)`. So `g < 0` there, and
`δ_n(r)` is larger. This is (3). ∎

The script finds `δ_3(r)` by bisection on Lemma 1. It gives 0.366025 at `r = 1/2` and
0.822876 at `r = 3/2`, which agree with the closed form. At `r = 1` the rotation needs
δ ≥ 0.618034, and everyone cooperating needs only δ ≥ 0.5.

In this linear game, taking turns is never the easier way to cooperate. It needs more
patience than everyone cooperating, and it pays less on average. So the game does not
explain turn-taking. Turn-taking can only pay where the benefits are not linear, for
instance where one contributor is enough and a second is wasted. Such games are not
studied here. The literature on turn-taking has not been checked.

## Proposition 8 — length zero inside the window

This proposition is part (a) of the golden-window conjecture below. The proof was written by
Claude Code at the author's request on 2026-11-18. The author is responsible for it. The
literature was checked on the same day. Proposition 8 is known. It is an immediate special
case of Lu, Steiner and Zou (2026), Proposition 2.5 and its proof, which give a dimension
below 1 when the two cylinders are separated, as they are here. It also follows from the
ergodicity of the greedy β-transformation (Rényi 1957; Parry 1960); that statement is
recalled, not read. The elementary proof below is kept. Under the counting of this note,
Proposition 8 is zero: checked, and not new.

Fix δ with 1/φ < δ < 2/3, and keep the variables of Proposition 6: `β = 1/δ`,
`X = (2δ − 1)/(δ(1 − δ))`, and `δX < 1 < X`. On `[0, X]` put

```
L = [0, δX],     R = [1, X],     H = (δX, 1),
T(x) = βx on L,     T(x) = β(x − 1) on R.
```

`H` is the hole, of length `1 − δX > 0`. `T(L) = [0, X]`. `T(R) = [0, β(X − 1)]` lies in
`[0, X]`, because `β(X − 1) ≤ X` is the same as `X(1 − δ) ≤ 1`, that is `(2δ − 1)/δ ≤ 1`.

Because `δX < 1`, a point of `[0, X]` has at most one branch. In Proposition 5, `u = 2` needs
`w ≤ 2 + δ`, which is `x ≥ 1`, and `u = 3` needs `w ≥ 4 − 2δ`, which is `x ≤ δX`. So the
backward recursion of Proposition 6 is the single map `T`, and the survivor set is

```
S = { x in [0, X] : Tⁿx lies in L ∪ R for every n ≥ 0 }.
```

`S` is closed, and `T(S) ⊂ S`.

**Proposition 8.** For 1/φ < δ < 2/3, `S` has Lebesgue measure zero, and so does `T_δ`.

*Proof.* Write `m` for Lebesgue measure and `|I|` for the length of an interval.

Step 1 (cylinders). Fix `x` in `S`. Define intervals `Iₙ ∋ x` and `Jₙ = [0, bₙ] ∋ Tⁿx` such
that `Tⁿ` maps `Iₙ` onto `Jₙ` as an increasing affine map of slope `βⁿ`. Start with
`I₀ = J₀ = [0, X]`. Given `n`, let `P` be the piece, `L` or `R`, that contains `Tⁿx`. Put
`Iₙ₊₁ = (Tⁿ on Iₙ)⁻¹(Jₙ ∩ P)` and `Jₙ₊₁ = T(Jₙ ∩ P)`. If `P = L`, then
`Jₙ ∩ L = [0, min(bₙ, δX)]`, so `Jₙ₊₁ = [0, β·min(bₙ, δX)]`. If `P = R`, then
`bₙ ≥ Tⁿx ≥ 1`, so `Jₙ ∩ R = [1, bₙ]` and `Jₙ₊₁ = [0, β(bₙ − 1)]`. Either way `Jₙ₊₁` starts
at 0 and contains `Tⁿ⁺¹x`, and `Tⁿ⁺¹` is affine of slope `βⁿ⁺¹` on `Iₙ₊₁`. Every `Jₙ` lies in
`[0, X]`, so `|Iₙ| = β⁻ⁿ|Jₙ| ≤ Xβ⁻ⁿ → 0`.

Step 2 (density transfers). `Tⁿ` maps `S ∩ Iₙ` into `S ∩ Jₙ`, because `T(S) ⊂ S`, and on
`Iₙ` it multiplies measure by `βⁿ`. Hence, whenever `|Jₙ| > 0`,

```
m(S ∩ Iₙ)/|Iₙ| ≤ m(S ∩ Jₙ)/|Jₙ|.
```

Step 3 (returns to R). If `Tⁿx` lies in `L` for every `n ≥ N`, then `T^(N+k)x = βᵏT^N x ≤ δX`
for every `k`, so `T^N x = 0`. The points that reach 0 form a countable set, because each `Tⁿ`
is at most `2ⁿ`-to-one. Take any other `x` in `S`. Then `Tⁿx > 0`, so every `Jₙ` has positive
length, and `Tⁿx` lies in `R`, so `bₙ ≥ Tⁿx ≥ 1`, for infinitely many `n`.

Step 4 (contradiction). Suppose `m(S) > 0`. Take `x` in `S` that is a Lebesgue density point of
`S` and does not reach 0. Almost every point of `S` is such a point. For intervals `I ∋ x` with
`|I| → 0`, centred at `x` or not, `m(I \ S)/|I| → 0`, because `I` lies in the interval of
radius `|I|` centred at `x`. By Step 2, `m(Jₙ \ S)/|Jₙ| ≤ m(Iₙ \ S)/|Iₙ| → 0`, and
`|Jₙ| ≤ X`, so `m(Jₙ \ S) → 0`. But for the infinitely many `n` with `bₙ ≥ 1`,
`Jₙ = [0, bₙ]` contains `[0, 1]`, which contains `H`, and `H` does not meet `S`. So
`m(Jₙ \ S) ≥ 1 − δX > 0` for those `n`. This is a contradiction, so `m(S) = 0`.

Step 5 (back to `T_δ`). In `w = 3 − (1 − δ)x` the surviving continuation values form
`W = 3 − (1 − δ)S`, which has measure zero. A starting value is `(1 − δ)u + δw′` with `u` in
{2, 3} and `w′` in `W` (Proposition 5), and `t` is that value minus 2. So `T_δ` lies in the
union of two affine images of `W`, and has measure zero. ∎

The proof uses no ergodic theory, only the Lebesgue density theorem. In `y = δx` the map `T`
is the greedy β-transformation `y ↦ βy − ⌊βy⌋` with a hole added. The literature check
found the result as a special case of a known theorem, as recorded at the start of this
section.

The script checks Step 1 in exact arithmetic. It refines `[0, X]` with fractions
for 16 periods at δ = 0.62, 0.64 and 0.66, and stops if an image `Jₙ` does not start at 0.
None does. The total length of the cylinders, in `x`, after one period and after the last,
goes from 0.65 to 0.00695 at δ = 0.62, from 0.993 to 0.154 at δ = 0.64, and
from 1.37 to 0.834 at δ = 0.66. This checks the construction. It is not part of the proof.

## Proposition 9 — the dimension inside the window

This proposition is part (b) of the golden-window conjecture below. The proof was written by
Claude Code at the author's request on 2026-11-18. The author is responsible for it. The
literature was checked on the same day. The formula of Proposition 9 is a special case of Lu,
Steiner and Zou (2026), Theorem 1.2 with Lemma 2.7. Its entropy part is also a special case
of Kuang, Li and Xiao (2026), Theorem 4.3 with `t = 0^∞`. That the dimension is below 1 is
Lu, Steiner and Zou (2026), Proposition 2.5. These parts are zero: checked, and not new.
Continuity along the curve `t(β) = (2 − β)/(β − 1)`, strict increase in δ, and the limits 0
at `1/φ` and 1 at `2/3` were not found in the texts read. They are not yet counted. The
argument of Theorem 1.5 of Lu, Steiner and Zou (2026) may transfer to the continuity. That is
the inference of the literature check, not a statement of the paper. Joint continuity in β
and the hole is not known to fail: Allaart and Kong withdrew that claim in Remark 1.10 of
arXiv 2109.10012v2. That the box dimension equals the Hausdorff dimension was not stated in
the papers read. With Proposition 8, Proposition 9 resolves the conjecture.

Keep the notation of Proposition 8. Step 1 of its proof shows that the image of every
cylinder is an interval `[0, b]` with `b ≤ X`. Call `[0, X]` the full state. From a state
`b`, the step `L` is always possible and leads to `β·min(b, δX)`. It leads back to the full
state exactly when `b ≥ δX`. The step `R` is possible when `b ≥ 1` and leads to `β(b − 1)`.

**The forced path.** Put `s₀ = X`. If `s_k ≥ 1`, put `s_(k+1) = β(s_k − 1)`. If `s_k < δX`,
put `s_(k+1) = βs_k`. If `δX ≤ s_k < 1`, the path stops. Let

```
A_δ = { k + 1 : s_k ≥ δX }.
```

`1` lies in `A_δ`, because `s₀ = X ≥ δX`.

A word that starts from the full state and does not return to it must take `R` at every state
of at least 1 and `L` at every state below `δX`, and it cannot pass a state in `[δX, 1)`. So it
follows the forced path. A word returns to the full state for the first time after `n` steps
exactly when it follows the forced path for `n − 1` steps and then takes `L` at a state of at
least `δX`. So there is exactly one first-return word of each length in `A_δ`, and none of any
other length.

**Proposition 9.** For 1/φ < δ < 2/3, the Hausdorff dimension of `T_δ` equals its box
dimension and is the unique `s` in (0, 1) with

```
Σ_{n ∈ A_δ} δ^(ns) = 1.
```

As a function of δ it is less than 1, continuous and strictly increasing, and it tends to 0
as δ ↓ 1/φ and to 1 as δ ↑ 2/3.

Strictly increasing is stronger than the "non-decreasing" of conjecture (b).

*Proof.* Step 1 (counting). Every word from the full state splits in one way into
first-return words followed by a prefix of the forced path. Let `N_n` be the number of
cylinders of depth `n`, `G_δ(z) = Σ_{n ∈ A_δ} zⁿ`, and `Q(z) = Σ q_m z^m`, where `q_m` is 1 if
the forced path has `m` steps and 0 otherwise. Then

```
Σ_n N_n zⁿ = Q(z) · Σ_{j ≥ 0} G_δ(z)^j.
```

`G_δ` is increasing and continuous on [0, 1), and `q₀ = 1`. So for `z < 1` the series
converges when `G_δ(z) < 1` and diverges when `G_δ(z) ≥ 1`. Let `h(δ) = lim sup (1/n) log N_n`.
If `G_δ(z*) = 1` for some `z*` in (0, 1), then `h(δ) = log(1/z*)`. Otherwise `h(δ) = 0`.

Every cylinder contains a point of `S`: the point that `Tⁿ` sends to 0, because `T0 = 0` and 0
lies in `L`. So `N_n` is also the number of words of length `n` that occur in the itineraries
of points of `S`. Write the letters as `e = 1 − a`, so that `e = u − 2`. The itineraries form
the shift space

```
Ω_δ = { e in {0, 1}^ℕ : Σ_{i ≥ 0} e_(k+i) δ^(i+1) ≥ 1 for every k ≥ 0 },
```

which is the incentive constraint `w_k ≥ c` written out. Points and itineraries correspond one
to one, because in the window every point has at most one branch. So `h(δ)` is the
topological entropy of `Ω_δ`.

Step 2 (the formula). The `N_n` cylinders of depth `n` cover `S`, and each has length at most
`Xδⁿ`. So the upper box dimension of `S` is at most `h(δ)/log β`. For the lower bound, take
`s < h(δ)/log β` and `z = δ^s`. Then `z > z*`, so `G_δ(z) > 1`, and some finite set
`F ⊂ A_δ` has `Σ_{n ∈ F} δ^(ns) > 1`. For `n` in `F`, the inverse of `Tⁿ` on the
first-return cylinder of length `n` is a similarity of ratio `δⁿ` from `[0, X]` onto that
cylinder. Take `n < m` in `A_δ`. The forced path continues past step `n − 1`, so
`s_(n−1) ≥ 1`, and the word of length `m` takes `R` there, where the word of length `n` takes
`L`. `L` and `R` are separated by `H`, so the two cylinders are disjoint closed intervals. The
limit set of these similarities therefore satisfies the strong separation condition. By the
standard theorem on self-similar sets under the strong separation condition, its Hausdorff
dimension is the `s′` with `Σ_{n ∈ F} δ^(ns′) = 1`, and `s′ > s`. Each of its points follows
first-return words for ever, so the limit set lies in `S`. Hence

```
dim_H S = dim_B S = h(δ)/log β = the s with Σ_{n ∈ A_δ} δ^(ns) = 1.
```

Proposition 6 gives `h(δ) > 0`, so `G_δ` reaches 1 below `z = 1`, and the root exists.
`T_δ` lies in two affine images of `W = 3 − (1 − δ)S` and contains one of them whole. With
`u = 3` first, `t = 1 − δ(3 − w′)` for `w′` in `W`, which lies in `[2 − 2δ, 1]`. So `T_δ` has
the same dimension as `S`.

Step 3 (below 1). `X·G_δ(δ)` is the total length of the first-return cylinders. They are
disjoint, and none meets `H`, because each lies inside `L` or inside `R`. So
`G_δ(δ) ≤ 1 − |H|/X < 1`. Hence `z* > δ`, `h(δ) < log β`, and the dimension is below 1.

Step 4 (strictly increasing). Each sum `Σ e_(k+i) δ^(i+1)` is non-decreasing in δ, so
`Ω_δ ⊂ Ω_δ′` for `δ < δ′`, and `h` is non-decreasing. Since `h(δ) > 0` and `log(1/δ)` is
strictly decreasing,

```
dim(δ) = h(δ)/log(1/δ) ≤ h(δ′)/log(1/δ) < h(δ′)/log(1/δ′) = dim(δ′).
```

Step 5 (continuous). It is enough that `h` is continuous. From the right: `Ω_δ` is the
intersection of the `Ω_δ′` for `δ′ > δ`, because each constraint is closed and continuous in
δ. For a decreasing sequence of shift spaces, the number of words of each length in the
intersection is the limit of the numbers, by compactness. Since `h = inf_n (1/n) log N_n`, the
entropy of the intersection is the limit of the entropies. So `h(δ+) = h(δ)`.

From the left, `h(δ−) ≤ h(δ)` by monotonicity. Fix `z` in `(z*, 1)`. It is enough that
`G_δ′(z) > 1` for every `δ′ < δ` close to δ, because then `z*(δ′) < z`. There are two cases.

(A) No `s_k` equals `δX`. Before the last element of `A_δ`, no `s_k` equals 1 either, because
from 1 the path goes to 0 and stays there. So for each `n` in `A_δ`, the path up to step
`n − 1` is decided by strict inequalities. The `s_k` move continuously with δ. So for any
finite `N`, every `n ≤ N` in `A_δ` is also in `A_δ′` once `δ′` is close enough. Choose `N`
with `Σ_{n ∈ A_δ, n ≤ N} zⁿ > 1`.

(B) `s_(n*−1) = δX` for some `n*`. Then the path stops there, `n* = max A_δ`, and `A_δ` is
finite. Put `P(z) = G_δ(z) − z^(n*)`. For `δ′` close to δ, the path at `δ′` copies the path at
δ for `n* − 1` steps and arrives near `δ′X′`. If it arrives at or above `δ′X′`, then `n*` lies
in `A_δ′`, and `G_δ′(z) ≥ G_δ(z) > 1`. If it arrives below, the step `L` sends it near `X′`,
and the next `n*` steps repeat the pattern, shifted by `n*`. The error grows by at most a
factor `β^(n*)` per block, so the closer `δ′` is to δ, the more blocks are repeated. If a
block after `j` repeated blocks arrives at or above `δ′X′`, then
`G_δ′(z) ≥ P(z) Σ_{i ≤ j} z^(in*) + z^((j+1)n*)`, and this is more than 1, because each
repeated block adds `z^(jn*)(G_δ(z) − 1) > 0` to `G_δ(z)`. Otherwise, after `r` repeated blocks,
`G_δ′(z) ≥ P(z) Σ_{i<r} z^(in*)`, and this is more than 1 for large `r`, because
`P(z)/(1 − z^(n*)) > 1` is the same as `G_δ(z) > 1`.

Step 6 (limits). As δ ↓ 1/φ, `X → 1`, because at δ = 1/φ, `2δ − 1 = δ³ = δ(1 − δ)`. After any
step `R` the path is at most `β(X − 1)`, which tends to 0. It then needs `m(δ)` steps of `L` to
reach `δX`, and `m(δ) → ∞`. So after 1, the elements of `A_δ` are more than `m` and at least
`m` apart. If the dimension stayed at least `s₀ > 0` along a sequence of δ, then
`z* = δ^dim ≤ (2/3)^(s₀) = z₀ < 1`, and `1 = G_δ(z*) ≤ z₀ + z₀^m/(1 − z₀^m)`, which fails for
large `m`. So the dimension tends to 0.

As δ ↑ 2/3, `X → 3/2` and `δX → 1`. Apart from at most one point, a point of `[0, X]` that never
returns to the full state falls into `H` while it follows the forced path. Those points have
total length at most `Σ_k δ^k |H| = (1 − δX)/(1 − δ)`, which tends to 0. So
`G_δ(δ) ≥ 1 − (1 − δX)/((1 − δ)X) → 1`. For `η > 0` and `M` large,
`G_δ(δ^(1−η)) ≥ δ^(−η)(G_δ(δ) − δ^(M+1)/(1 − δ)) > 1` for δ close to 2/3. Then
`z* < δ^(1−η)`, so the dimension is more than `1 − η`. So the dimension tends to 1. ∎

The proof uses the Lebesgue density theorem (through Step 1 of Proposition 8), the standard
theorem on self-similar sets under the strong separation condition, and the entropy of shift
spaces. Nothing else is used.

The script computes `A_δ` in exact arithmetic, following the forced path for up to 400
steps, and solves `Σ_{n ∈ A_δ} δ^(ns) = 1` by bisection. The last column is the lower bound of
Proposition 6.

| δ | A_δ | dimension | lower bound |
| --- | --- | --- | --- |
| 0.6181 | {1, 16} | 0.272410 | 0.272 |
| 0.62 | {1, 9} | 0.404196 | 0.404 |
| 0.63 | {1, 5} | 0.608610 | 0.609 |
| 0.64 | {1, 4} | 0.722146 | 0.722 |
| 0.65 | {1, 4, 8} | 0.825510 | 0.748 |
| 0.66 | {1, 3} | 0.919930 | 0.920 |
| 0.6666 | {1, 3, 9, 12, …} | 0.999233 | 0.942 |

On the 486 values δ = 0.6181, 0.6182, …, 0.6666: the dimension rises at 485 of the 485 steps,
and it is below the lower bound of Proposition 6 at 0 of them and equal to it, to 9 decimals, at 255.
It runs from 0.2724 to 0.999233. Where `A_δ = {1, n₀ + 1}`, the self-similar set of
Proposition 6 is the whole first-return system, and the bound is the dimension. The
finite-depth estimates below agree in direction. At δ = 0.6666 the confirmatory scan
estimated 0.999247. These computations check the formula. They are not part of the proof.

## The golden-window conjecture

Between `1/φ` and `2/3` both branches are available, but they leave a hole
`(2 + δ, 4 − 2δ)` between them. A value that falls into the hole cannot be continued.
The survivors form the set of points whose orbit never meets the hole.

The window is the interval from `1/φ` to `2/3`. Below it only two points survive, at `1/φ`
itself a countable set does, and above it the whole segment does (Proposition 5). Inside it
the set has positive dimension (Proposition 6) and length zero (Proposition 8), and its
dimension is given by Proposition 9. The conjecture was about the rest. The name describes the
statement. It is not named after a person.

**Golden-window conjecture (a).** For 1/φ < δ < 2/3, `T_δ` has Lebesgue measure zero.

Part (a) is proved. It is Proposition 8, written on 2026-11-18. The statement stays here under
its old name, so that its issue label and the earlier records still point to it.

**Golden-window conjecture (b).** For 1/φ < δ < 2/3, the Hausdorff dimension of `T_δ` is
less than 1, is continuous and non-decreasing in δ, and tends to 0 as δ ↓ 1/φ and to 1 as
δ ↑ 2/3. That it is positive is Proposition 6.

Part (b) is proved. It is Proposition 9, written on 2026-11-18. Measure zero does not settle
it: a set of measure zero can still have Hausdorff dimension 1, and Proposition 8 says nothing
about continuity, monotonicity or the limits. Proposition 9 is a separate proof.

Both parts are proved, so the conjecture is resolved. Its status is resolved (part (a) and the formula of part (b) are special cases of known theorems; continuity and strict increase in δ and the limits at both ends were not found in the texts read). The
name stays as the name of the problem. It is already in published DOIs and in issue labels.

Evidence. The script refines `[c, 3]` for 22 periods. Below 2/3 the two branches have
disjoint images, so the surviving intervals do not overlap. The growth rate is the
number of intervals per period over the last five periods. The dimension estimate is
`log(growth)/log(1/δ)`. The last two columns are Proposition 6.

| δ | intervals | total length | growth | dimension estimate | n₀ | lower bound |
| --- | --- | --- | --- | --- | --- | --- |
| 0.62 | 134 | 5.16e-04 | 1.199 | 0.38 | 8 | 0.404 |
| 0.63 | 756 | 6.49e-03 | 1.325 | 0.61 | 4 | 0.609 |
| 0.64 | 1728 | 2.64e-02 | 1.380 | 0.72 | 3 | 0.722 |
| 0.65 | 3691 | 8.49e-02 | 1.427 | 0.83 | 3 | 0.748 |
| 0.66 | 5896 | 2.32e-01 | 1.466 | 0.92 | 2 | 0.920 |

In every row the growth rate is below `1/δ`, so the total length keeps shrinking. That
was the evidence for part (a), which Proposition 8 now proves. The dimension estimate rises
with δ, which was the evidence for part (b), which Proposition 9 now proves. Neither
computation is a proof. The estimates come
from a finite depth, and the limit at either end is extrapolated. At δ = 0.62 the estimate 0.38 is below the proved lower
bound 0.404, so the finite-depth estimate is too low there.

Monotonicity was the least supported part. As δ changes, the base and the hole move
together, and dimension functions of maps with holes often behave like a devil's
staircase. Five values cannot settle it, and the 48 values of the wider scan below cannot
either. Proposition 9 settles it: the dimension is strictly increasing, so it has no flat
steps.

Berg and Kitti (2014) study exactly this kind of object. They show that pure-strategy
equilibrium payoff sets of discounted repeated games can be fractals, and measure them
by Hausdorff dimension. Per their abstract, which is all that was read, they give a method
to estimate the dimension.

The change of variables above places the problem among expansions in non-integer bases
and expanding maps with holes. Part (a) is proved directly by Proposition 8, and part
(b) by Proposition 9. The literature check of 2026-11-18, below, says how much of each is
known. Three leads were first recalled from memory and not checked: Glendinning
and Sidorov (2001) on unique expansions in non-integer bases; Kalle, Kong, Langeveld and
Li (around 2020) on the β-transformation with a hole; Urbański (1986) on the continuity
of dimension for expanding maps with holes. Of these, the first remains unchecked.

### A wider scan

The scan was run on 2026-11-12 with `python3 games/scan.py`. Its output is
[`scan.txt`](scan.txt). It takes δ = 0.619, …, 0.666, which is 48 values at step 0.001
across the whole window, and refines for 30 periods. The interval counts are exact,
because δ is a fraction and every endpoint is kept as an integer. A separate floating-point
computation in the check gives the same counts.

- Growth is below `1/δ` in 48 of 48 rows, so the total length keeps shrinking at every δ
  scanned. The largest value of growth × δ is 0.997, at δ = 0.666. Close to 2/3 the
  shrinking is slow, and the depth matters most there.
- The dimension estimate never falls from one δ to the next. The scan counts 0 decreases.
  The estimate runs from 0.39 at the first δ to 0.99 at the last.
- In 16 rows the estimate is below the lower bound of Proposition 6, so the finite-depth
  estimate is too low there. This is the same effect as at δ = 0.62 in the table above.
- The upper estimate is `log N/(n log(1/δ))` for `N` intervals at depth `n`. It is below 1
  in 45 of 48 rows, for every δ up to 0.663.

A standard covering argument may make the upper estimate an upper bound for the dimension
at each δ scanned. That argument is not written out here and has not been checked, so the
column is reported as evidence only. Even if it holds, it says nothing about the values of
δ between the grid points.

None of this is a proof. A grid of 48 values cannot rule out a δ between its points at which
the length stops shrinking, and a finite depth cannot fix a dimension. A second grid, and
what would count against the conjecture on it, was fixed in advance in the
[preregistration](PREREGISTRATION.md). The next section reports it.

### The confirmatory scan

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

## What this does and does not say about Trinity-Infinity

It does not make the papers' operator new. The operator is a special case of the
Friedkin–Johnsen model, and the bridge in Lemma 1 is the textbook formula for a
discounted value.

What it does is give the papers' juxtaposition of an operator and a repeated game a
single equation. It replaces a false example with a proved family that passes through
Series I's δ* = 1/2. It also posed the golden-window conjecture, which Propositions 8 and 9
now resolve. Part (a) and the formula of part (b) are special cases of known theorems. It leaves the question of why `1/φ` appears
twice.

## What this means for mathematics, and for the philosophy of science

Everything in the first half of this section is conditional on the literature check.
If the same statements are found elsewhere, their mathematical significance belongs to
that earlier work, and this note becomes a worked reading of it.

**Mathematics.** The note offers an explicit example with four features.

- One simple game shows three regimes as δ grows: two isolated points below `1/φ`, a set
  of positive dimension and length zero inside the window (Propositions 6 and 8), and the
  whole segment from `2/3`.
  The boundaries are exact. Examples of fractal equilibrium sets that can be computed this
  far by hand are useful as test cases for general theories such as Berg and Kitti (2014).
- The discounting recursion, read backwards, is a pair of affine maps with a hole between
  their ranges. That places this repeated game inside the study of interval maps with
  holes. The note makes the translation explicit for one game.
- Propositions 4 and 5 measure what a public randomization device adds in this game. With
  it, every point from `1 − δ` upward can be sustained once δ ≥ 1/2. Without it, inside the
  window, almost none can (Proposition 8). The question of what public randomization
  adds is a known theme in the theory of repeated games. The note gives exact thresholds
  for one case.
- The same polynomial `δ² + δ − 1` decides both the rotation threshold and the lower end
  of the window. If that is not a coincidence, it points to a link between equilibrium
  thresholds of rotation schemes and the point at which the value dynamics start to branch.

None of this makes the operator new, and none of it is a new theory.

**Philosophy of science.** The significance recorded elsewhere stays as it was. A triadic
intuition was formalized, the number three dissolved, and a known model remained. That
route is the case studied in Machine-mediated Rediscovery (SSRN
`10.2139/ssrn.7537983`). This note adds one step to it. Pushing the rediscovered model
further, into a setting the original papers had only placed beside it, produced a
well-posed question. On 2026-11-18 it was answered (Propositions 8 and 9). Most of the
answer turned out to be special cases of known theorems. A rediscovery that contributes nothing as a
result can still lead to a question that was not answered when it was posed. The note also keeps three states apart and
has them checked by machine: known, proved but not yet counted, and conjectured. That
bookkeeping is itself part of the case.

## If the conjecture is proved

How far a proof would go depends on what the proof is.

| proof | what it reaches | where it could go |
| --- | --- | --- |
| general results such as Berg and Kitti (2014) apply directly | a worked instance of a known theory; a section of a master's thesis | an update of this note, a short preprint |
| parts (a) and (b) are proved with a new argument | one small paper | a specialist journal in dynamical systems or repeated games |
| the dimension is found in closed form as a function of δ, and the double appearance of `1/φ` is explained | a full paper; the game could become a standard example | a specialist journal |

Both parts were proved on 2026-11-18 (Propositions 8 and 9). The proofs use the Lebesgue
density theorem, the standard theorem on self-similar sets under the strong separation
condition, and the entropy of shift spaces. The literature check found Proposition 8 and the
formula of Proposition 9 to be special cases of known theorems, so the first row applies to
them. For continuity, strict increase and the end limits along the curve of this game, no
source was found in the texts read. The dimension is the root of an equation in δ, not a closed form, and the double
appearance of `1/φ` is not explained, so the third row is not reached.

Some things do not change. The operator remains a special case of the Friedkin–Johnsen
model. What moves up is one statement about this game, this payoff table and this window.
The framework does not become a new theory. The proved statement could be called the
golden-window theorem. This note keeps the name golden-window conjecture as the name of the
problem, because the name is already in published DOIs and in issue labels. Whether another
name is used depends on others citing it.

The order of work would be this. First, check the literature, including Berg and Kitti
(2014) and work on survivor sets of interval maps with holes, for a result that already
settles the question. Both parts were proved first, on 2026-11-18, because their proofs
needed only standard theorems (Propositions 8 and 9). The literature check followed on the
same day. Most of the result is special cases of known theorems, so it is not counted as a
paper of its own.

### An open question: why 1/φ twice

The threshold of the three-player rotation (Proposition 1) and the lower end of the
window (Proposition 5) both come from the same polynomial `δ² + δ − 1`. This note
does not know whether that is a coincidence. It is recorded as a question, not as a
conjecture. Explaining it would be the step from a computed example to a statement about
structure.

Algebraically the two conditions meet. When `δ² = 1 − δ`, also `1 − δ³ = 2δ²`, so the
condition of Proposition 1, `2δ² ≥ 1 − δ³`, and that of Proposition 5, `δ² ≥ 1 − δ`,
change sign at the same point. At δ = 1/φ both sides of the first equal 0.763932. This
may depend on the defector's bonus being 2 in the payoff table. Changing the payoffs and
checking whether the two thresholds separate would decide whether there is more to it.

## Contributions claimed, and their conditions

This is not a theory. The proofs have not been checked against the literature, and no
third party has recognised them. Under those conditions, the following contributions are
claimed. Propositions 8 and 9 are the exception to the first condition: they were checked on
2026-11-18.

| contribution | content | condition |
| --- | --- | --- |
| a mathematical contribution as mathematical proof | Propositions 1–7, and the continuity, strict increase and end limits of Proposition 9, such as the threshold `1/φ` for the three-player rotation | not checked against the literature and not recognised by any third party; moves to zero if an earlier statement is found |
| a mathematical contribution as a mathematical conjecture | the golden-window conjecture; its two parts are now Propositions 8 and 9 | the contribution of posing the question; the answer is counted with the propositions |
| a contribution as a case study in the philosophy of science | the route of rediscovery (Machine-mediated Rediscovery, SSRN `10.2139/ssrn.7537983`) | passed SSRN's screening; not peer-reviewed |

Claiming a contribution and having the field count it are different things. The field's
count is in the next section.

## Zero, and not yet counted

The contribution of the three Trinity-Infinity papers to mathematics is zero. That was
settled when the operator was identified. Everything in them is a known model or a
textbook fact.

Propositions 1–7 of this note are in a different state. They are proved, but they have
not been checked against the literature. Until they are, they are not counted as new
results. That is not the same as zero. Zero means the check was made and nothing new was
found. Not yet counted means the check has not been made.

| | state | counted as |
| --- | --- | --- |
| the three papers | a special case of a known model | zero |
| Propositions 1–7 | proved; literature not checked | not yet counted |
| Proposition 8 | proved; a special case of known theorems | zero |
| Proposition 9 | proved; the formula and the bound below 1 are special cases of known theorems; continuity, strict increase and the end limits were not found in the texts read | the formula: zero; the rest: not yet counted |
| golden-window conjecture | resolved (part (a) and the formula of part (b) are special cases of known theorems; continuity and strict increase in δ and the limits at both ends were not found in the texts read) | part (a) zero; part (b) partly zero, partly not yet counted |

Only a literature check can move the row of Propositions 1–7. If no earlier statement is found for the
rotation thresholds, they become small new results. If one is found, the row moves to
zero, and the earlier source is cited here. The search terms to start with are
"rotation scheme", "golden ratio", "discount factor" and "three-player prisoner's
dilemma". For Proposition 6, "beta-expansion with a hole" and "open dynamical system" are
likely to be faster. The environment this note was written in cannot reach the literature
databases, so the check of Propositions 1–7 has not been made.

## The literature check of 2026-11-18

Claude checked the literature for Propositions 8 and 9 on 2026-11-18. The search ran through
Crossref and DataCite. Some arXiv papers were then read in the parts named below. Every DOI and
arXiv id below is the one that Crossref, DataCite or the arXiv API returned. Each source is
marked "read in part", "abstract read" or "recalled, not read".

**A reduction.** Write `y = δx` and `t(β) = (2 − β)/(β − 1)`, which equals `δX`. Then `S` is
`δ⁻¹K`, where `K` is the set of `y` in [0, 1) whose orbit under the greedy β-transformation
`y ↦ βy − ⌊βy⌋` never enters the hole `(t(β), 1)`. In the digit coding, the itineraries are
`{ u : σⁿu ≼ w for all n }`, where `w` is the quasi-greedy β-expansion of `t(β)`. With this, the
theorems below apply. The check confirmed the reduction numerically. It is not part of the
proofs.

**Flat stretches of the entropy.** The entropy `h = log(1/z*)` depends on δ only through
`A_δ`, and `A_δ` can stay the same while δ moves. The dimension `h/log β` still rises strictly,
because β moves. The script finds this at every δ = 0.6400, 0.6401, …, 0.6450: `A_δ = {1, 4}`,
the entropy is 0.322285 throughout, and the dimension rises from 0.722146 to 0.734962. The same
mechanism, a locally constant entropy over a moving base, is known for univoque sets
(Komornik, Kong and Li 2017).

**Proposition 8.** Known. It is an immediate special case of Lu, Steiner and Zou (2026),
Proposition 2.5 and its proof. It also follows from the ergodicity of the greedy
β-transformation (Rényi 1957; Parry 1960), recalled, not read. It is counted as zero.

**Proposition 9.** The formula is a special case of Lu, Steiner and Zou (2026), Theorem 1.2
with Lemma 2.7, for `q0 = q1 = β`. The entropy part is also Kuang, Li and Xiao (2026), Theorem
4.3 with `t = 0^∞`. The bound below 1 is Lu, Steiner and Zou (2026), Proposition 2.5. These
parts are zero. For a fixed base, continuity in the symbolic hole is Lu, Steiner and Zou (2026),
Theorem 1.4, and continuity in the base for a fixed symbolic hole is their Lemma 3.16. For a
fixed β with one end of the hole moving, the dimension is a devil's staircase (Sun, Li and
Ding 2024, Corollary 1.5, for the left end fixed). For the right end fixed, which is the case
here, that paper asserts the same without proof. Joint continuity in β and the hole is open: Allaart and Kong (2023), in
Remark 1.10 of arXiv 2109.10012v2, withdraw the published claim that it fails. Continuity along
the curve of this game, strict increase in δ, and the limits 0 at `1/φ` and 1 at `2/3` were not
found in the texts read, and are not yet counted. The argument of Theorem 1.5 of Lu, Steiner
and Zou (2026) may transfer to the continuity. That is the inference of the check, not a
statement of the paper. That the box dimension equals the Hausdorff dimension was not stated in
the papers read.

**The game.** Berg and Kitti (2014) and Mailath, Obara and Sekiguchi (2002) were read at
abstract level only. Their full texts are not on arXiv. No exact dimension, and no
measure-zero result, for this segment was found. The nearest are Berg and Kitti (2014), who
give a method to estimate the dimension, and Mailath, Obara and Sekiguchi (2002), who study the
maximum efficient payoff.

Sources of the check:

- Allaart, P., and Kong, D. (2023). Critical values for the β-transformation with a hole at 0.
  *Ergodic Theory and Dynamical Systems*. doi:10.1017/etds.2022.24. Read in part: Proposition
  1.9 and Remark 1.10 of arXiv 2109.10012v2 (doi:10.48550/arxiv.2109.10012).
- Berg, K., and Kitti, M. (2014). Fractal geometry of equilibrium payoffs in discounted
  supergames. *Fractals*, 22(4), 1450016. doi:10.1142/s0218348x14500169. Abstract read.
- Komornik, V., Kong, D., and Li, W. (2017). Hausdorff dimension of univoque sets and Devil's
  staircase. *Advances in Mathematics*. doi:10.1016/j.aim.2016.03.047. Abstract read.
- Kuang, R., Li, B., and Xiao, Y. (2026). The Hausdorff dimension of the survivor set. arXiv
  2604.23737v1. doi:10.48550/arxiv.2604.23737. Read in part: Introduction, Theorems 1.1, 1.2
  and 4.3.
- Lu, J., Steiner, W., and Zou, Y. (2026). Hausdorff dimension of double-base expansions and
  binary shifts with a hole. *Bulletin of the London Mathematical Society*.
  doi:10.1112/blms.70344. Read in part: Sections 1–3 of arXiv 2509.04227v2, in full
  (doi:10.48550/arxiv.2509.04227).
- Mailath, G. J., Obara, I., and Sekiguchi, T. (2002). The maximum efficient equilibrium payoff
  in the repeated Prisoners' Dilemma. *Games and Economic Behavior*. doi:10.1006/game.2001.0901.
  Abstract read.
- Parry, W. (1960). On the β-expansions of real numbers. *Acta Mathematica Academiae
  Scientiarum Hungaricae*. doi:10.1007/bf02020954. Recalled, not read.
- Rényi, A. (1957). Representations for real numbers and their ergodic properties. *Acta
  Mathematica Academiae Scientiarum Hungaricae*. doi:10.1007/bf02020331. Recalled, not read.
- Sun, Y., Li, B., and Ding, Y. (2024). Topological expansive Lorenz maps with a hole at
  critical point. *Journal of Statistical Physics*. doi:10.1007/s10955-024-03265-0. Read in
  part: Introduction, and the statements of Theorems 1.1, 1.3 and 1.4, Corollary 1.5 and
  Remark 1.2 of arXiv
  2311.02465v1 (doi:10.48550/arxiv.2311.02465).

## References

- Abreu, D. (1988). On the theory of infinitely repeated games with discounting.
  *Econometrica*, 56(2), 383–396.
- Abreu, D., Pearce, D., and Stacchetti, E. (1990). Toward a theory of discounted
  repeated games with imperfect monitoring. *Econometrica*, 58(5), 1041–1063.
- Berg, K., and Kitti, M. (2014). Fractal geometry of equilibrium payoffs in discounted
  supergames. *Fractals*, 22(4).
- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206 (the title page gives 193–205). doi:10.1080/0022250X.1990.9990069
- Fudenberg, D., and Maskin, E. (1986). The folk theorem in repeated games with
  discounting or with incomplete information. *Econometrica*, 54(3), 533–554.
- Nemoto, T. (2026). Trinity-Infinity Series I (revised). doi:10.5281/zenodo.22058624
- Nemoto, T. (2026). Trinity-Infinity Series II (revised). doi:10.5281/zenodo.22058777

## License and use of language models

This note is licensed under CC BY 4.0 ([LICENSE](LICENSE)). The code is MIT. The note was drafted with
Claude Code (Anthropic) at the author's request, including the propositions, their
proofs and the conjectures. The author is responsible for it. Claude is not an author.
