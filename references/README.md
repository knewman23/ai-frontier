# Reference notebooks

Other people's notebooks, kept here so the calculus and linear algebra behind
the curriculum is one directory away instead of one search away. Nothing in
here is mine, and nothing in here is modified.

The vendored ones are also rendered in full on the site, each with its author,
licence and a link back to the original, and every section of every one of them
is in the site's search index.

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
| `vendor/handson-ml3/` (2 notebooks) | [Aurélien Géron, Hands-On ML 3e](https://github.com/ageron/handson-ml3) | Apache-2.0 |
| `vendor/ml-foundations/` (4 notebooks) | [Jon Krohn, ML Foundations](https://github.com/jonkrohn/ML-foundations) | MIT |
| `vendor/landlinear/` (4 notebooks + images) | [Land on Vector Spaces](https://github.com/engineersCode/EngComp4_landlinear) | CC BY 4.0 text, [BSD-3 code](https://github.com/engineersCode/EngComp#license) |
| `vendor/ml-refined/` (7 notebooks) | [Machine Learning Refined](https://github.com/neonwatty/machine-learning-refined) | CC BY-NC-SA 4.0 |

Land on Vector Spaces carries no licence file of its own; it's module 4 of the
[Engineering Computations](https://github.com/engineersCode/EngComp) series,
whose repository licenses the whole collection — "all content is under CC-BY
4.0, and all code is under BSD-3 clause."

Machine Learning Refined is non-commercial and share-alike. It's reproduced
verbatim, which the licence permits with attribution; this site carries no
advertising and sells nothing.

Only a subset of the two larger courses is vendored — the chapters that bear on
the curriculum. `fetch.py` pulls the rest.

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
| `landlinear` | [Land on Vector Spaces](https://github.com/engineersCode/EngComp4_landlinear) | the full module, beyond the 4 vendored lessons |
| `ml-refined` | [Machine Learning Refined](https://github.com/neonwatty/machine-learning-refined) | the whole course, beyond the 7 vendored notebooks |
| `fastai-nla` | [Computational Linear Algebra](https://github.com/fastai/numerical-linear-algebra) | **no licence declared** |
| `mml-book` | [Mathematics for Machine Learning tutorials](https://github.com/mml-book/mml-book.github.io) | **no licence declared** |
| `d2l` | [Dive into Deep Learning](https://d2l.ai/) | CC BY-SA 4.0 / MIT |

`fastai-nla` and `mml-book` ship no licence file. A public repository grants
the right to view and fork it on GitHub, not to republish it elsewhere, so
those two are linked and fetchable but never rendered here. `d2l` is licensed
to redistribute but is already a polished website whose notebooks carry no
saved outputs, so it stays linked as well.

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
