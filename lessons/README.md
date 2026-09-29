# The Friedkin–Johnsen model with a cyclic influence matrix

*One operator, five lessons: when a sufficient condition is mistaken for a necessary one.*

A short self-study module in linear iteration, built around one standard model and one
real mistake.

The model is the Friedkin–Johnsen model of opinion dynamics (Friedkin and Johnsen 1990).
In the form now standard in the literature (Proskurnikov and Tempo 2017) it reads

```
x(k + 1) = Λ W x(k) + (I − Λ) u,
```

with `W` a row-stochastic influence matrix, `Λ` a diagonal matrix of susceptibilities
and `u` the agents' initial opinions. The lessons restrict `W` to a cyclic permutation,
and write the model as

```
x ← D Q x + (I − D) p,     D = Λ,  Q = W,  p = u.
```

The restriction is where the module came from. The author reached this special case
independently, in a series of preprints (the *Trinity-Infinity* papers), without knowing
the model, and identified it only afterwards. The papers proved convergence through the
operator norm. The spectral radius is what
actually decides it. Each lesson takes one step from what the papers assumed towards
what is true, and ends by saying exactly what the original author got wrong at that
step. The author of the papers and of this module is the same person. The mistakes are
kept because they are the material.

This is not new mathematics. The model is from 1990 and every fact used here is in
standard textbooks. The question the module asks is narrow: **with the influence matrix
restricted to a cyclic permutation, what remains of the model, and which of the
stability conditions used in the papers were redundant?** It offers one concrete object
on which the standard facts can be run and checked.

## Lessons

| | lesson | status |
| --- | --- | --- |
| 1 | Contractions and Banach's theorem: what the papers did | planned |
| 2 | [A sufficient condition is not a necessary one](02-sufficient-is-not-necessary.md) | draft |
| 3 | Permutations can be solved by hand: `(DQ)ⁿ = (∏aᵢ) I` | planned |
| 4 | [Errors that grow before they shrink](04-errors-that-grow.md) | draft |
| 5 | Switching: two stable maps whose alternation diverges | planned |

## How to use it

Each lesson is a page and a script. Run the script from the root of the repository:

```
pip install numpy
python3 lessons/lesson2.py
```

Every number printed on a page comes from its script.
`python3 verification/check_lessons.py` fails if a page and its script disagree.

## License

The lesson text in this directory is licensed under
[CC BY 4.0](LICENSE). The code (the `lessonN.py` scripts and everything outside this
directory) is licensed under the MIT License in the repository root.

## References

- Friedkin, N. E., and Johnsen, E. C. (1990). Social influence and opinions. *Journal
  of Mathematical Sociology*, 15(3–4), 193–206. doi:10.1080/0022250X.1990.9990069
- Proskurnikov, A. V., and Tempo, R. (2017). A tutorial on modeling and analysis of
  dynamic social networks. Part I. *Annual Reviews in Control*, 43, 65–79.
  doi:10.1016/j.arcontrol.2017.03.002

## Use of AI

The lessons are drafted with Claude Code (Anthropic) at the author's request. Every
number is produced by code and checked mechanically. The author is responsible for the
content. Claude is not an author. A lesson marked *draft* has not yet been reviewed by
the author.
