# Reference notebooks

Other people's notebooks, kept here so the calculus and linear algebra behind
the curriculum is one directory away instead of one search away. Nothing in
here is mine, and nothing in here is modified.

The six vendored ones are also rendered in full on the site, each with its
author, licence and a link back to the original.

These are the counterweight to `notebooks/`: those build everything from
scratch, these use numpy, matplotlib and autodiff freely and spend their effort
on diagrams and notation instead.

The annotated list — what each one covers and why it's worth the time — is on
the [references page](https://knewman23.github.io/ai-frontier/references/) of
the site, generated from `site/references.json`.

## What's committed

Vendored verbatim, with the upstream licence beside it:

| Path | Source | Licence |
|------|--------|---------|
| `vendor/handson-ml3/math_linear_algebra.ipynb` | [Aurélien Géron, Hands-On ML 3e](https://github.com/ageron/handson-ml3) | Apache-2.0 |
| `vendor/handson-ml3/math_differential_calculus.ipynb` | [Aurélien Géron, Hands-On ML 3e](https://github.com/ageron/handson-ml3) | Apache-2.0 |
| `vendor/ml-foundations/1-intro-to-linear-algebra.ipynb` | [Jon Krohn, ML Foundations](https://github.com/jonkrohn/ML-foundations) | MIT |
| `vendor/ml-foundations/2-linear-algebra-ii.ipynb` | [Jon Krohn, ML Foundations](https://github.com/jonkrohn/ML-foundations) | MIT |
| `vendor/ml-foundations/3-calculus-i.ipynb` | [Jon Krohn, ML Foundations](https://github.com/jonkrohn/ML-foundations) | MIT |
| `vendor/ml-foundations/4-calculus-ii.ipynb` | [Jon Krohn, ML Foundations](https://github.com/jonkrohn/ML-foundations) | MIT |

## What isn't

The rest is either unlicensed or licensed in a way that doesn't belong inside
an MIT repo, so it's fetched on demand into `external/`, which is gitignored:

```sh
python references/fetch.py            # list the sources
python references/fetch.py --all      # fetch all of them
python references/fetch.py mml-book   # or just one
```

| Name | Source | Licence |
|------|--------|---------|
| `landlinear` | [Land on Vector Spaces](https://github.com/engineersCode/EngComp4_landlinear) | none declared |
| `fastai-nla` | [Computational Linear Algebra](https://github.com/fastai/numerical-linear-algebra) | none declared |
| `mml-book` | [Mathematics for Machine Learning tutorials](https://github.com/mml-book/mml-book.github.io) | none declared |
| `ml-refined` | [Machine Learning Refined](https://github.com/neonwatty/machine-learning-refined) | CC BY-NC-SA 4.0 |
| `d2l` | [Dive into Deep Learning](https://d2l.ai/) | CC BY-SA 4.0 / MIT |

These are linked from the references page but not rendered on the site — an
undeclared licence isn't permission to republish, and the share-alike ones
would pull their terms onto the site.

`d2l` downloads the full book archive (a few hundred MB) and keeps only the
preliminaries and mathematics appendix; the others are shallow, sparse clones
or single files.

## Running them

`vendor/` is the pristine copy — it's what the site renders, so running a
notebook in place leaves an enormous diff. The Hands-On ML calculus notebook
goes from 0.6 MB to 80 MB once its animations have been drawn. Work in `run/`
instead, which is gitignored:

```sh
source .venv/bin/activate
pip install -r references/requirements.txt

python references/fetch.py --workspace   # copies vendor/ into run/
jupyter lab references/run/
```

`--workspace` never overwrites a notebook already in `run/`, so re-running it
just picks up anything new.

PyTorch is included because the ML Foundations notebooks take every derivative
twice — once by hand and once with autodiff. TensorFlow shows up in 29 cells
across `1-intro-to-linear-algebra` and `3-calculus-i` — always as a second
opinion next to the numpy or PyTorch version of the same thing — so it's
commented out of the requirements rather than pulled in for that; uncomment it
if you want those cells to run.

The two Hands-On ML notebooks need nothing beyond numpy and matplotlib, and
both run clean end to end on matplotlib 3.11 (their animations use the `jshtml`
writer, so no ffmpeg). Run them in Jupyter rather than under a headless `Agg`
backend — several cells rely on the inline backend closing the figure between
cells.
