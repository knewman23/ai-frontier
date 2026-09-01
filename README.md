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
| 01 | [Derivatives and the Numerical Gradient](notebooks/01-derivatives-and-the-numerical-gradient.ipynb) | What a derivative is, estimated numerically from the limit definition — and why that estimate is never quite exact |

## Running locally

```sh
git clone https://github.com/knewman23/ai-frontier.git
cd ai-frontier

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

jupyter lab
```

## Layout

```
notebooks/    numbered, in the order they were worked through
```

Notebooks are committed **with their outputs intact**, so the plots and printed
values render on GitHub without anyone needing to run a kernel.

## License

MIT — see [LICENSE](LICENSE).
