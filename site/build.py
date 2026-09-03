#!/usr/bin/env python3
"""Generate the ai-frontier site from the notebooks in ../notebooks.

Each notebook becomes a page; the index is derived from each notebook's H1,
lead paragraph, and H2 section headings, so adding a notebook needs no edits
here. Output goes to ../_site.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"
VENDOR = ROOT / "references" / "vendor"
OUT = ROOT / "_site"
SITE = Path(__file__).resolve().parent

TITLE = "AI Frontier"
TAGLINE = ("Notebooks from a self-study path through neural networks and "
           "machine learning — built from scratch, in order.")
REPO = "https://github.com/knewman23/ai-frontier"
CURRICULUM = "https://knewman23.github.io/backprop-to-frontier/"
PORTFOLIO = "https://knewman23.github.io/"
REFERENCES = SITE / "references.json"

# Lifted from knewman23.github.io so both sites share one theme component.
THEME_BOOT = """<script>
try {
  var t = localStorage.getItem("theme");
  if (t === "dark" || t === "light") document.documentElement.dataset.theme = t;
} catch (e) { /* private mode: fall through to prefers-color-scheme */ }
</script>"""

TOGGLE_BUTTON = """<button class="theme keep" id="theme" type="button" aria-live="polite">
<svg class="i-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
<svg class="i-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7"/></svg>
<span id="theme-text">Dark</span>
</button>"""


MATHJAX = """<script>
window.MathJax = {
  tex: { inlineMath: [['$','$'],['\\\\(','\\\\)']],
         displayMath: [['$$','$$'],['\\\\[','\\\\]']] },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code'] },
  svg: { fontCache: 'global' }
};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>"""


def strip_md(text: str) -> str:
    """Markdown inline syntax -> plain text."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\$+([^$]*)\$+", r"\1", text)
    return " ".join(text.split())


def slug_of(path: Path) -> str:
    return path.stem


def shell(body: str, *, title: str, description: str, base: str,
          crumbs: str, extra_head: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="icon" href="{base}favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="{base}favicon.png">
<link rel="apple-touch-icon" href="{base}favicon.png">
<link rel="stylesheet" href="{base}style.css">
{THEME_BOOT}
{extra_head}
</head>
<body>
<div class="band"><div class="wrap">
<span class="crumbs">{crumbs}</span>
{TOGGLE_BUTTON}
</div></div>
{body}
<footer class="page"><div class="wrap">
<span>Krys Newman</span>
<a href="{REPO}">Source on GitHub</a>
<a href="{CURRICULUM}">Curriculum</a>
</div></footer>
<script src="{base}theme.js"></script>
</body>
</html>
"""


def parse(nb) -> dict:
    """Pull title, lede, and section headings out of a notebook."""
    title, lede, sections = "", "", []
    for cell in nb.cells:
        if cell.cell_type != "markdown":
            continue
        src = "".join(cell.source)
        for line in src.split("\n"):
            m = re.match(r"^##\s+(.+)$", line)
            if m:
                sections.append(strip_md(m.group(1)))
        if not title:
            m = re.search(r"^#\s+(.+)$", src, re.M)
            if m:
                title = strip_md(m.group(1))
                after = src[m.end():].strip()
                for block in after.split("\n\n"):
                    block = block.strip()
                    if block and not block.startswith((">", "#", "-", "*")):
                        lede = strip_md(block)
                        break
    return {"title": title, "lede": lede, "sections": sections}


def render_notebook(path: Path, *, strip_h1: bool = True) -> tuple[dict, str]:
    nb = nbformat.read(path, as_version=4)
    meta = parse(nb)
    body, _ = HTMLExporter(template_name="basic").from_notebook_node(nb)
    if strip_h1:
        # The H1 and its lead paragraph become the page header instead.
        body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, count=1, flags=re.S)
    return meta, body


def sections_from_body(body: str) -> list[tuple[str, str]]:
    """Real (id, text) pairs for each h2, read back out of the rendered HTML.

    nbconvert keeps punctuation such as commas and em-dashes in its heading
    ids, so reusing them verbatim is the only reliable way to link to them.
    """
    out = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S):
        text = re.sub(r'<a class="anchor-link".*?</a>', "", m.group(2), flags=re.S)
        text = re.sub(r"<[^>]+>", "", text)
        out.append((m.group(1), html.unescape(text).strip()))
    return out


def headings_from_body(body: str, levels: str = "2") -> list[tuple[str, str]]:
    """(id, text) pairs for the given heading levels, read out of the HTML."""
    out = []
    for m in re.finditer(rf'<h([{levels}]) id="([^"]+)">(.*?)</h\1>', body, re.S):
        text = re.sub(r'<a class="anchor-link".*?</a>', "", m.group(3), flags=re.S)
        text = re.sub(r"<[^>]+>", "", text)
        out.append((m.group(2), html.unescape(text).strip()))
    return out


def toc_html(sections: list[tuple[str, str]]) -> str:
    if len(sections) < 3:
        return ""
    items = "\n".join(
        f'<li><a href="#{html.escape(i, quote=True)}">{html.escape(t)}</a></li>'
        for i, t in sections
    )
    return ('<aside class="toc"><p class="toc-label">On this page</p>'
            f"<ul>{items}</ul></aside>")


def reference_notebook_pages(data: dict) -> dict[str, dict]:
    """Render every vendored notebook to its own page under /references/.

    Returns slug -> metadata, so the references index can link to them.
    """
    rendered = {}
    for rel, meta in data.get("vendored", {}).items():
        path = VENDOR / rel
        if not path.exists():
            raise SystemExit(f"references.json points at a missing notebook: {path}")

        # Reference notebooks keep their own H1s — those are their sections.
        _, body = render_notebook(path, strip_h1=False)
        headings = headings_from_body(body, levels="12")

        nav = ('<nav class="nb-nav"><a href="../">&larr; All references</a>'
               f'<a href="{meta["upstream"]}">View the original &rarr;</a></nav>')

        page = f"""<main class="wrap">
<div class="nb-head measure">
<p class="num">Reference &middot; {html.escape(meta["author"])}</p>
<h1>{html.escape(meta["title"])}</h1>
<p class="lede">{html.escape(meta["lede"])}</p>
<div class="nb-meta">
<span>{len(headings)} sections</span>
<a href="{meta["upstream"]}">Original notebook</a>
<a href="{meta["colab"]}">Open in Colab</a>
<a href="{REPO}/blob/main/references/vendor/{rel}">Copy in this repo</a>
</div>
</div>
<p class="callout measure">
Not my work. Written by {html.escape(meta["author"])} for
<em>{html.escape(meta["work"])}</em> and reproduced here unmodified under the
<a href="{meta["licence_url"]}">{html.escape(meta["licence"])}</a> licence.
The <a href="{meta["upstream"]}">original</a> is the version to cite, fork or
report problems against.
</p>
<div class="nb-layout">
<article class="nb-body">{body}
{nav}
</article>
{toc_html(headings)}
</div>
</main>"""

        crumbs = (f'<a href="{PORTFOLIO}"><b>Krys Newman</b></a>'
                  '<span class="sep">/</span>'
                  '<a href="../../">AI Frontier</a>'
                  '<span class="sep">/</span>'
                  '<a href="../">Reference</a>'
                  '<span class="sep">/</span>'
                  f'<span class="here">{html.escape(meta["title"])}</span>')

        dest = OUT / "references" / meta["slug"]
        dest.mkdir(parents=True)
        (dest / "index.html").write_text(shell(
            page, title=f'{meta["title"]} — {meta["author"]}',
            description=meta["lede"], base="../../", crumbs=crumbs,
            extra_head=MATHJAX))
        rendered[rel] = meta
    return rendered


def references_page() -> str:
    """The reference-notebook page, rendered from site/references.json."""
    data = json.loads(REFERENCES.read_text())

    vendored = data.get("vendored", {})

    def item_html(item: dict) -> str:
        chips = "".join(f"<span>{html.escape(t)}</span>"
                        for t in item.get("topics", []))
        here = "".join(
            f'<a class="here-link" href="{vendored[rel]["slug"]}/">'
            f'Read: {html.escape(vendored[rel]["title"])}</a>'
            for rel in item.get("pages", []) if rel in vendored)
        links = here + "".join(
            f'<a href="{html.escape(l["url"], quote=True)}">{html.escape(l["label"])}</a>'
            for l in item["links"])

        avail = item.get("availability", {})
        kind = avail.get("kind", "link")
        if kind == "vendored":
            where = ("Rendered in full below &mdash; runnable copy at "
                     f'<code>{html.escape(avail["path"])}</code>')
        elif kind == "fetch":
            where = ("Fetch locally &mdash; "
                     f'<code>python references/fetch.py {html.escape(avail["name"])}</code>')
        else:
            where = "Read at the source"

        return f"""<li class="ref">
<h3>{html.escape(item["title"])}</h3>
<p class="ref-source">{html.escape(item["source"])}</p>
<p class="ref-why">{html.escape(item["why"])}</p>
<div class="topics">{chips}</div>
<p class="ref-where"><span class="tag tag-{kind}">{kind}</span> {where}</p>
<p class="ref-links">{links}<span class="ref-licence">{html.escape(item["licence"])}</span></p>
</li>"""

    groups = []
    for g in data["groups"]:
        items = "".join(item_html(i) for i in g["items"])
        groups.append(f"""<p class="section-label">{html.escape(g["name"])}</p>
<p class="group-blurb measure">{html.escape(g["blurb"])}</p>
<ul class="refs">{items}</ul>""")

    return f"""<main class="wrap">
<div class="hero measure">
<p class="kicker">{html.escape(data["kicker"])}</p>
<h1>{html.escape(data["title"])}</h1>
<p class="lede">{html.escape(data["lede"])}</p>
</div>
<p class="callout measure">{data["note"]}</p>
{"".join(groups)}
<div class="measure" style="margin-top:3rem">
<p style="color:var(--soft);font-size:.9688rem">
Running them locally is covered in
<a href="{REPO}/blob/main/references/README.md" style="color:var(--accent)">references/README.md</a>.
</p>
</div>
</main>"""


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # stylesheet + syntax highlighting
    css = (SITE / "style.css").read_text()
    def defs(style: str, prefix: str) -> str:
        return HtmlFormatter(style=style).get_style_defs(prefix)

    dark_style = "github-dark"
    try:
        HtmlFormatter(style=dark_style)
    except Exception:
        dark_style = "monokai"

    css += (
        "\n\n/* ---- syntax highlighting ---- */\n"
        + defs("friendly", ".highlight")
        + "\n@media (prefers-color-scheme: dark){\n"
        + defs(dark_style, ':root:not([data-theme="light"]) .highlight')
        + "\n}\n"
        + defs(dark_style, ':root[data-theme="dark"] .highlight')
        + "\n"
    )
    (OUT / "style.css").write_text(css)

    paths = sorted(p for p in NOTEBOOKS.glob("*.ipynb") if not p.name.startswith("."))
    entries = []
    for path in paths:
        meta, body = render_notebook(path)
        entries.append({"path": path, "slug": slug_of(path),
                        "sections_r": sections_from_body(body), **meta})

    for i, e in enumerate(entries):
        meta, body = render_notebook(e["path"])
        num = re.match(r"^(\d+)", e["slug"])
        label = f"Notebook {num.group(1)}" if num else "Notebook"

        prev_ = entries[i - 1] if i else None
        next_ = entries[i + 1] if i + 1 < len(entries) else None
        nav = ['<nav class="nb-nav">']
        nav.append(f'<a href="../{prev_["slug"]}/">&larr; {html.escape(prev_["title"])}</a>'
                   if prev_ else '<a href="../">&larr; All notebooks</a>')
        if next_:
            nav.append(f'<a href="../{next_["slug"]}/">{html.escape(next_["title"])} &rarr;</a>')
        nav.append("</nav>")

        page = f"""<main class="wrap">
<div class="nb-head measure">
<p class="num">{label}</p>
<h1>{html.escape(e["title"])}</h1>
<p class="lede">{html.escape(e["lede"])}</p>
<div class="nb-meta">
<span>{len(e["sections_r"])} sections</span>
<a href="{REPO}/blob/main/notebooks/{e["path"].name}">View notebook source</a>
<a href="{REPO}/raw/main/notebooks/{e["path"].name}">Download .ipynb</a>
</div>
</div>
<div class="nb-layout">
<article class="nb-body">{body}
{''.join(nav)}
</article>
{toc_html(e["sections_r"])}
</div>
</main>"""

        crumbs = (
            f'<a href="{PORTFOLIO}"><b>Krys Newman</b></a>'
            '<span class="sep">/</span>'
            '<a href="../">AI Frontier</a>'
            '<span class="sep">/</span>'
            f'<span class="here">{html.escape(e["title"])}</span>'
        )
        dest = OUT / e["slug"]
        dest.mkdir()
        (dest / "index.html").write_text(shell(
            page, title=f'{e["title"]} — {TITLE}', description=e["lede"],
            base="../", crumbs=crumbs, extra_head=MATHJAX))

    # index
    refs = json.loads(REFERENCES.read_text())
    REF_CHIPS = "".join(f"<span>{html.escape(g['name'])}</span>"
                        for g in refs["groups"])
    cards = []
    for e in entries:
        num = re.match(r"^(\d+)", e["slug"])
        secs = [t for _, t in e["sections_r"] if t.lower() != "setup"]
        shown = secs[:5]
        chips = "".join(f"<span>{html.escape(s)}</span>" for s in shown)
        if len(secs) > len(shown):
            chips += f"<span>+{len(secs) - len(shown)} more</span>"
        cards.append(f"""<li class="entry"><a href="{e["slug"]}/">
<div class="num">{num.group(1) if num else "&mdash;"}</div>
<div>
<h2>{html.escape(e["title"])}</h2>
<p>{html.escape(e["lede"])}</p>
<div class="topics">{chips}</div>
</div>
</a></li>""")

    index = f"""<main class="wrap">
<div class="hero measure">
<p class="kicker">Self-study &middot; Machine learning</p>
<h1>{TITLE}</h1>
<p class="lede">{TAGLINE}</p>
</div>
<p class="section-label">Notebooks</p>
<ul class="entries">
{''.join(cards)}
</ul>
<p class="section-label">Reference</p>
<ul class="entries">
<li class="entry"><a href="references/">
<div class="num">&rarr;</div>
<div>
<h2>Reference notebooks</h2>
<p>Public calculus and linear algebra notebooks worth keeping open alongside
these — diagram-heavy, notation-first, and happy to use numpy, matplotlib and
autodiff rather than rebuild them. Six are committed to the repo and runnable
locally; the rest are one fetch away.</p>
<div class="topics">{REF_CHIPS}</div>
</div>
</a></li>
</ul>
<div class="measure" style="margin-top:3rem">
<p style="color:var(--muted);font-size:.9688rem">
Each notebook builds its tools by hand before reaching for a library. The
curriculum they follow is tracked separately at
<a href="{CURRICULUM}" style="color:var(--accent)">Backprop to Frontier</a>.
</p>
</div>
</main>"""

    (OUT / "index.html").write_text(shell(
        index, title=f"{TITLE} — Krys Newman", description=TAGLINE,
        base="",
        crumbs=(f'<a href="{PORTFOLIO}"><b>Krys Newman</b></a>'
                '<span class="sep">/</span>'
                f'<span class="here">{TITLE}</span>')))

    refs_dir = OUT / "references"
    refs_dir.mkdir()
    refs_data = json.loads(REFERENCES.read_text())
    vendored = reference_notebook_pages(refs_data)
    (refs_dir / "index.html").write_text(shell(
        references_page(), title=f'{refs_data["title"]} — {TITLE}',
        description=refs_data["lede"], base="../",
        crumbs=(f'<a href="{PORTFOLIO}"><b>Krys Newman</b></a>'
                '<span class="sep">/</span>'
                '<a href="../">AI Frontier</a>'
                '<span class="sep">/</span>'
                f'<span class="here">{html.escape(refs_data["title"])}</span>')))

    for name in ("favicon.ico", "favicon.png", "theme.js"):
        shutil.copy2(SITE / "assets" / name, OUT / name)

    (OUT / ".nojekyll").write_text("")
    print(f"built {len(entries)} notebook page(s) + {len(vendored)} reference "
          f"page(s) + index -> {OUT}")
    for meta in vendored.values():
        print(f"  /references/{meta['slug']}/  {meta['title']}")
    for e in entries:
        print(f"  /{e['slug']}/  {e['title']}  ({len(e['sections'])} sections)")


if __name__ == "__main__":
    main()
