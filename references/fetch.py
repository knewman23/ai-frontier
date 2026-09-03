#!/usr/bin/env python3
"""Fetch the reference notebooks that can't be committed here.

Some of the material listed on the references page is either unlicensed or
licensed in a way that doesn't sit well inside an MIT repo, so it isn't
vendored. This pulls it into references/external/, which is gitignored.

    python references/fetch.py            # list what's available
    python references/fetch.py --all      # fetch everything
    python references/fetch.py fastai-nla mml-book
    python references/fetch.py --workspace  # copy vendor/ into run/ to work in

vendor/ is kept pristine so the site renders it and so that running a notebook
doesn't leave a huge diff — the animations in the Hands-On ML calculus notebook
alone take it from 0.6 MB to 80 MB once executed. Work in run/ instead, which
is gitignored.

Anything already fetched is updated in place rather than re-cloned.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTERNAL = HERE / "external"
VENDOR = HERE / "vendor"
RUN = HERE / "run"

# name -> (description, licence, how to get it)
#   git:  shallow clone of a repo, optionally sparse-checked out to one subdir
#   raw:  a handful of files pulled straight from raw.githubusercontent.com
SOURCES = {
    "landlinear": {
        "desc": "Land on Vector Spaces — Engineers Code (GWU)",
        "licence": "none declared",
        "git": "https://github.com/engineersCode/EngComp4_landlinear.git",
        "subdir": "notebook_en",
    },
    "fastai-nla": {
        "desc": "Computational Linear Algebra — fast.ai / Rachel Thomas",
        "licence": "none declared",
        "git": "https://github.com/fastai/numerical-linear-algebra.git",
        "subdir": "nbs",
    },
    "ml-refined": {
        "desc": "Machine Learning Refined — Watt, Borhani & Katsaggelos",
        "licence": "CC BY-NC-SA 4.0",
        "git": "https://github.com/neonwatty/machine-learning-refined.git",
        "subdir": "notes",
    },
    "mml-book": {
        "desc": "Mathematics for Machine Learning tutorials — Deisenroth et al.",
        "licence": "none declared",
        "raw": [
            "https://raw.githubusercontent.com/mml-book/mml-book.github.io/master/tutorials/tutorial_pca.ipynb",
            "https://raw.githubusercontent.com/mml-book/mml-book.github.io/master/tutorials/tutorial_linear_regression.ipynb",
            "https://raw.githubusercontent.com/mml-book/mml-book.github.io/master/tutorials/tutorial_gmm.ipynb",
        ],
    },
    "d2l": {
        "desc": "Dive into Deep Learning — maths chapters (PyTorch notebooks)",
        "licence": "CC BY-SA 4.0 text / MIT code",
        "zip": "https://d2l.ai/d2l-en.zip",
        "keep": ("chapter_preliminaries", "chapter_appendix-mathematics-for-deep-learning"),
    },
}


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def fetch_git(name: str, spec: dict) -> Path:
    dest = EXTERNAL / name
    if (dest / ".git").exists():
        print(f"  updating {dest.relative_to(EXTERNAL.parent.parent)}")
        run(["git", "-C", str(dest), "pull", "--ff-only", "--quiet"])
        return dest

    subdir = spec.get("subdir")
    cmd = ["git", "clone", "--depth", "1", "--quiet"]
    if subdir:
        cmd += ["--filter=blob:none", "--sparse"]
    cmd += [spec["git"], str(dest)]
    run(cmd)
    if subdir:
        run(["git", "-C", str(dest), "sparse-checkout", "set", subdir])
    return dest


def fetch_raw(name: str, spec: dict) -> Path:
    dest = EXTERNAL / name
    dest.mkdir(parents=True, exist_ok=True)
    for url in spec["raw"]:
        out = dest / url.rsplit("/", 1)[-1]
        print(f"  {out.name}")
        urllib.request.urlretrieve(url, out)
    return dest


def fetch_zip(name: str, spec: dict) -> Path:
    import io
    import zipfile

    dest = EXTERNAL / name
    dest.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {spec['zip']} (large — a few hundred MB)")
    with urllib.request.urlopen(spec["zip"]) as r:
        blob = io.BytesIO(r.read())
    keep = spec.get("keep")
    with zipfile.ZipFile(blob) as z:
        members = [m for m in z.namelist()
                   if not keep or any(f"/{k}/" in f"/{m}" for k in keep)]
        z.extractall(dest, members)
        print(f"  extracted {len(members)} file(s)")
    return dest


def fetch(name: str) -> None:
    spec = SOURCES[name]
    print(f"{name}: {spec['desc']}  [licence: {spec['licence']}]")
    if "git" in spec:
        if not shutil.which("git"):
            sys.exit("git is not on PATH")
        dest = fetch_git(name, spec)
    elif "raw" in spec:
        dest = fetch_raw(name, spec)
    else:
        dest = fetch_zip(name, spec)
    print(f"  -> {dest}\n")


def workspace() -> None:
    """Copy the vendored notebooks into run/, without clobbering existing work."""
    RUN.mkdir(parents=True, exist_ok=True)
    for src in sorted(VENDOR.glob("*/*.ipynb")):
        dest = RUN / src.name
        if dest.exists():
            print(f"  skip  {dest.name} (already in run/)")
            continue
        shutil.copy2(src, dest)
        print(f"  copy  {dest.name}")
    print(f"\n  -> {RUN}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("names", nargs="*", choices=sorted(SOURCES) + [], metavar="NAME")
    p.add_argument("--all", action="store_true", help="fetch every source")
    p.add_argument("--workspace", action="store_true",
                   help="copy references/vendor/ into references/run/ to work in")
    args = p.parse_args()

    if args.workspace:
        workspace()
        if not (args.all or args.names):
            return

    names = sorted(SOURCES) if args.all else args.names
    if not names:
        print("Available sources (fetched into references/external/):\n")
        for name, spec in sorted(SOURCES.items()):
            print(f"  {name:<12} {spec['desc']}")
            print(f"  {'':<12} licence: {spec['licence']}")
        print("\nFetch with:      python references/fetch.py --all")
        print("Work in run/ with: python references/fetch.py --workspace")
        return

    EXTERNAL.mkdir(parents=True, exist_ok=True)
    for name in names:
        fetch(name)


if __name__ == "__main__":
    main()
