/* Search across every notebook and reference page.

   The index is one record per heading, built by site/build.py. Scoring is
   deliberately plain: a term in a title or heading counts for more than the
   same term in the body, and every term has to appear somewhere in the record,
   so a two-word query narrows instead of widening. */
(function () {
  var input = document.getElementById("q");
  var results = document.getElementById("results");
  var status = document.getElementById("status");
  var form = document.getElementById("search-form");
  if (!input || !results) return;

  var index = null;
  var pending = null;

  function load() {
    if (index) return Promise.resolve(index);
    if (!pending) {
      pending = fetch("../search-index.json")
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.json();
        })
        .then(function (data) { index = data; return index; });
    }
    return pending;
  }

  function terms(query) {
    return query.toLowerCase().split(/\s+/).filter(Boolean);
  }

  function count(haystack, needle) {
    var n = 0, i = haystack.indexOf(needle);
    while (i !== -1) { n++; i = haystack.indexOf(needle, i + needle.length); }
    return n;
  }

  function score(record, words) {
    var title = record.t.toLowerCase();
    var heading = (record.h || "").toLowerCase();
    var body = record.x.toLowerCase();
    var total = 0;

    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      var inTitle = count(title, w);
      var inHeading = count(heading, w);
      var inBody = count(body, w);
      if (!inTitle && !inHeading && !inBody) return 0;  // every term must hit
      total += inTitle * 12 + inHeading * 8 + Math.min(inBody, 6);
    }
    // A heading that starts with the query is almost always the thing wanted.
    if (heading.indexOf(words.join(" ")) === 0) total += 15;
    return total;
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function snippet(text, words) {
    var lower = text.toLowerCase();
    var at = -1;
    for (var i = 0; i < words.length && at === -1; i++) at = lower.indexOf(words[i]);
    if (at === -1) at = 0;

    // Snap both ends to word boundaries: cutting mid-word reads as a typo.
    var start = Math.max(0, at - 90);
    if (start > 0) {
      var space = text.indexOf(" ", start);
      start = space === -1 || space - start > 25 ? start : space + 1;
    }
    var end = Math.min(text.length, start + 260);
    if (end < text.length) {
      var tail = text.lastIndexOf(" ", end);
      if (tail > start + 120) end = tail;
    }
    var cut = text.slice(start, end).replace(/^[^\w(“"']+/, "");
    if (start > 0) cut = "…" + cut;
    if (end < text.length) cut += "…";

    var out = escapeHtml(cut);
    words.forEach(function (w) {
      var re = new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }

  function render(query) {
    var words = terms(query);
    if (!words.length) {
      results.innerHTML = "";
      status.textContent = "";
      return;
    }
    var hits = [];
    for (var i = 0; i < index.length; i++) {
      var s = score(index[i], words);
      if (s > 0) hits.push({ r: index[i], s: s });
    }
    hits.sort(function (a, b) { return b.s - a.s; });

    status.textContent = hits.length
      ? hits.length + (hits.length === 1 ? " section" : " sections")
      : "Nothing matched “" + query + "”";

    results.innerHTML = hits.slice(0, 40).map(function (hit) {
      var r = hit.r;
      // A notebook whose H1 is its title would otherwise read "X → X".
      var same = r.h && r.h.toLowerCase() === r.t.toLowerCase();
      var where = r.h && !same
        ? escapeHtml(r.t) + ' <span class="result-sep">→</span> ' + escapeHtml(r.h)
        : escapeHtml(r.t);
      return '<li class="result"><a href="../' + r.u + '">' +
        '<p class="result-where"><span class="kind kind-' + r.k + '">' + r.k +
        "</span>" + where + "</p>" +
        '<p class="result-text">' + snippet(r.x, words) + "</p>" +
        '<p class="result-source">' + escapeHtml(r.s) + "</p>" +
        "</a></li>";
    }).join("");
  }

  function run() {
    var query = input.value.trim();
    var url = new URL(window.location);
    if (query) url.searchParams.set("q", query); else url.searchParams.delete("q");
    window.history.replaceState(null, "", url);

    if (!query) { render(""); return; }
    status.textContent = "Searching…";
    load().then(function () { render(query); }).catch(function () {
      status.textContent = "Could not load the search index.";
    });
  }

  var timer;
  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(run, 120);
  });
  form.addEventListener("submit", function (e) { e.preventDefault(); run(); });

  var initial = new URL(window.location).searchParams.get("q");
  if (initial) { input.value = initial; run(); }
  load();
})();
