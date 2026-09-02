#!/usr/bin/env python3
"""Generate the ai-frontier site from the notebooks in ../notebooks.

Each notebook becomes a page; the index is derived from each notebook's H1,
lead paragraph, and H2 section headings, so adding a notebook needs no edits
here. Output goes to ../_site.
"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"
OUT = ROOT / "_site"
SITE = Path(__file__).resolve().parent

TITLE = "AI Frontier"
TAGLINE = ("Notebooks from a self-study path through neural networks and "
           "machine learning — built from scratch, in order.")
REPO = "https://github.com/knewman23/ai-frontier"
CURRICULUM = "https://knewman23.github.io/backprop-to-frontier/"
PORTFOLIO = "https://knewman23.github.io/"

THEME_BOOT = """<script>
(function () {
  try {
    var t = localStorage.getItem('theme');
    if (t === 'light' || t === 'dark') {
      document.documentElement.setAttribute('data-theme', t);
    }
  } catch (e) {}
})();
</script>"""

TOGGLE_BUTTON = """<button class="theme-toggle" type="button"
        aria-label="Switch between light and dark theme" title="Switch theme">
<svg class="i-moon" width="15" height="15" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="1.7" stroke-linecap="round"
     stroke-linejoin="round" aria-hidden="true">
<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
</svg>
<svg class="i-sun" width="15" height="15" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="1.7" stroke-linecap="round"
     stroke-linejoin="round" aria-hidden="true">
<circle cx="12" cy="12" r="4.2"/>
<path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>
</svg>
</button>"""

TOGGLE_SCRIPT = """<script>
(function () {
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var root = document.documentElement;
    var cur = root.getAttribute('data-theme');
    if (cur !== 'light' && cur !== 'dark') {
      cur = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    var next = cur === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) {}
  });
})();
</script>"""


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
<header class="masthead"><div>
{crumbs}
<span class="spacer"></span>
<a href="{PORTFOLIO}">Krys Newman's portfolio</a>
{TOGGLE_BUTTON}
</div></header>
{body}
<footer class="page"><div>
<span>Krys Newman</span>
<a href="{REPO}">Source on GitHub</a>
<a href="{CURRICULUM}">Curriculum</a>
<a href="{PORTFOLIO}">Portfolio</a>
</div></footer>
{TOGGLE_SCRIPT}
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


def render_notebook(path: Path) -> tuple[dict, str]:
    nb = nbformat.read(path, as_version=4)
    meta = parse(nb)
    body, _ = HTMLExporter(template_name="basic").from_notebook_node(nb)
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


def toc_html(sections: list[tuple[str, str]]) -> str:
    if len(sections) < 3:
        return ""
    items = "\n".join(
        f'<li><a href="#{html.escape(i, quote=True)}">{html.escape(t)}</a></li>'
        for i, t in sections
    )
    return ('<aside class="toc"><p class="toc-label">On this page</p>'
            f"<ul>{items}</ul></aside>")


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

        crumbs = (f'<a href="../">{TITLE}</a><span class="sep">/</span>'
                  f'<span>{html.escape(e["title"])}</span>')
        dest = OUT / e["slug"]
        dest.mkdir()
        (dest / "index.html").write_text(shell(
            page, title=f'{e["title"]} — {TITLE}', description=e["lede"],
            base="../", crumbs=crumbs, extra_head=MATHJAX))

    # index
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
        crumbs=f'<span>{TITLE}</span>'))

    for name in ("favicon.ico", "favicon.png"):
        shutil.copy2(SITE / "assets" / name, OUT / name)

    (OUT / ".nojekyll").write_text("")
    print(f"built {len(entries)} notebook page(s) + index -> {OUT}")
    for e in entries:
        print(f"  /{e['slug']}/  {e['title']}  ({len(e['sections'])} sections)")


if __name__ == "__main__":
    main()
