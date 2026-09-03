# AI Frontier

Notebooks from a self-study path through neural networks and machine learning —
built from scratch, in order, starting at the derivative and working toward
frontier LLM research.

Each notebook is standalone and readable straight on GitHub: narration, code,
and outputs together. Nothing is imported from a library that the notebook
hasn't already built by hand.

The curriculum these follow is tracked separately at
**[backprop-to-frontier](https://github.com/knewman23/backprop-to-frontier)**
([live](https://knewman23.github.io/backprop-to-frontier/)).

## Notebooks

| # | Notebook | What it covers |
|---|----------|----------------|
| 01 | [From Derivatives to a Backprop Graph](notebooks/01-derivatives-and-the-numerical-gradient.ipynb) | Numerical derivatives and their error; a `Value` scalar that records its own operations; graph visualization with graphviz; a backward pass worked out by hand |

## Reference notebooks

`references/` holds public calculus and linear algebra notebooks by other
people — the counterweight to the from-scratch notebooks above. They lean on
numpy, matplotlib and autodiff and spend their effort on diagrams and notation
instead, which makes them the right thing to have open while working through a
course. The annotated list is on the
[references page](https://knewman23.github.io/ai-frontier/references/).

Six of them are permissively licensed and committed here verbatim, licence
included:

| Notebook | Source | Licence |
|----------|--------|---------|
| [Math: Linear Algebra](references/vendor/handson-ml3/math_linear_algebra.ipynb) | Aurélien Géron, Hands-On ML 3e | Apache-2.0 |
| [Math: Differential Calculus](references/vendor/handson-ml3/math_differential_calculus.ipynb) | Aurélien Géron, Hands-On ML 3e | Apache-2.0 |
| [Linear Algebra I & II](references/vendor/ml-foundations/) | Jon Krohn, ML Foundations | MIT |
| [Calculus I & II](references/vendor/ml-foundations/) | Jon Krohn, ML Foundations | MIT |

The rest — fast.ai's Computational Linear Algebra, Land on Vector Spaces, the
MML book tutorials, Machine Learning Refined, and the D2L maths chapters — are
unlicensed or share-alike, so they're pulled down on demand instead of
committed:

```sh
pip install -r references/requirements.txt
python references/fetch.py --all
```

See [references/README.md](references/README.md) for the full breakdown.

## Running locally

```sh
git clone https://github.com/knewman23/ai-frontier.git
cd ai-frontier

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

jupyter lab
```

Graph drawing also needs the graphviz **system binary**, which pip can't
install — `brew install graphviz` on macOS, `apt install graphviz` on Debian.

## Layout

```
notebooks/    numbered, in the order they were worked through
references/   other people's calculus and linear algebra notebooks
site/         the static-site generator behind knewman23.github.io/ai-frontier
```

Notebooks are committed **with their outputs intact**, so the plots and printed
values render on GitHub without anyone needing to run a kernel.

## License

MIT — see [LICENSE](LICENSE).
