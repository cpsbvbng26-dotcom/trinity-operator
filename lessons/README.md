# One operator, five lessons

*When a sufficient condition is mistaken for a necessary one.*

A short self-study module in linear iteration, built around one operator and one real
mistake. The operator is the one studied in the *Trinity-Infinity* papers:

```
x ← D Q x + (I − D) p,     D = diag(a),  Q a permutation (at first)
```

Those papers proved convergence through the operator norm. The spectral radius is what
actually decides it. Each lesson takes one step from what the papers assumed towards
what is true, and ends by saying exactly what the original author got wrong at that
step. The author of the papers and of this module is the same person. The mistakes are
kept because they are the material.

This is not new mathematics. Everything here is in standard textbooks. What the module
offers is one concrete object on which the standard facts can be run and checked.

## Lessons

| | lesson | status |
| --- | --- | --- |
| 1 | Contractions and Banach's theorem: what the papers did | planned |
| 2 | [A sufficient condition is not a necessary one](02-sufficient-is-not-necessary.md) | draft |
| 3 | Permutations can be solved by hand: `(DQ)ⁿ = (∏aᵢ) I` | planned |
| 4 | Non-normal matrices: errors that grow before they shrink | planned |
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

## Use of AI

The lessons are drafted with Claude Code (Anthropic) at the author's request. Every
number is produced by code and checked mechanically. The author is responsible for the
content. Claude is not an author. A lesson marked *draft* has not yet been reviewed by
the author.
