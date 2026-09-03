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

Seventeen notebooks whose licence permits redistribution are committed here
verbatim and rendered in full on the site, each carrying its author, licence and
a link back to the original:

| Notebooks | Source | Licence |
|-----------|--------|---------|
| [Linear algebra, differential calculus](references/vendor/handson-ml3/) | Aurélien Géron, Hands-On ML 3e | Apache-2.0 |
| [Linear Algebra I–II, Calculus I–II](references/vendor/ml-foundations/) | Jon Krohn, ML Foundations | MIT |
| [Transformations, matrices, eigenvectors, SVD](references/vendor/landlinear/) | Land on Vector Spaces (GWU) | CC BY 4.0 · BSD-3 |
| [First- and second-order optimisation, norms](references/vendor/ml-refined/) | Machine Learning Refined | CC BY-NC-SA 4.0 |

Two sources — fast.ai's Computational Linear Algebra and the MML book tutorials
— ship no licence file at all. A public repo grants the right to view and fork
it on GitHub, not to republish it elsewhere, so those stay linked rather than
mirrored. D2L is licensed to redistribute but is already a website, so it stays
linked too. All of them are one command away locally:

```sh
pip install -r references/requirements.txt
python references/fetch.py --all

python references/fetch.py --workspace   # copies vendor/ into references/run/
jupyter lab references/run/
```

Run them from `references/run/` rather than `references/vendor/` — the vendored
copies stay pristine so the site renders them, and executing one in place adds
tens of megabytes of embedded animation frames to the diff.

See [references/README.md](references/README.md) for the full breakdown.

## Search

Every section of every notebook — mine and the references, code included — is
indexed at build time into `search-index.json` and searched client-side from
[/search/](https://knewman23.github.io/ai-frontier/search/). No service, no
dependency: one JSON file and 150 lines of JavaScript.

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
  vendor/     committed verbatim, licence included — what the site renders
  run/        working copies for actually running them (gitignored)
  external/   fetched on demand, never committed (gitignored)
site/         the static-site generator behind knewman23.github.io/ai-frontier
```

Notebooks are committed **with their outputs intact**, so the plots and printed
values render on GitHub without anyone needing to run a kernel.

## License

MIT — see [LICENSE](LICENSE).
