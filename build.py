#!/usr/bin/env python3
"""Generate the static recipe site from content/recipes/*.json into dist/."""
import json, glob, os, re, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist")
BASE = os.environ.get("BASE_PATH", "/recipes/")
FOOTER = "Jiten &amp; Alicia's recipes"

CATS = [  # (name, title keywords) - inferred only from obvious title words
    ("Dal", ["dal"]),
    ("Chai", ["chai"]),
    ("Chicken", ["chicken"]),
    ("Vegan", ["vegan"]),
    ("Sauces/Chutneys", ["sauce", "chutney"]),
    ("Desserts", ["cake", "flan", "frosting", "icing", "ice cream"]),
]
HIDDEN_MEASURES = {"Count"}  # "2 Count garlic cloves" reads as "2 garlic cloves"

def e(s): return html.escape(str(s))
def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]

def categories(title):
    t = title.lower()
    c = [n for n, kws in CATS if any(re.search(r"\b" + re.escape(k) + r"\b", t) for k in kws)]
    return c or ["Other"]

def page(title, body, desc=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<link rel="stylesheet" href="{BASE}style.css">
<link rel="stylesheet" href="{BASE}print.css" media="print">
</head><body>
<header class="site"><a href="{BASE}" class="brand">Jiten &amp; Alicia's Kitchen</a></header>
<main>{body}</main>
<footer>{FOOTER}</footer>
</body></html>"""

def load():
    rs = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content/recipes/*.json"))):
        r = json.load(open(f, encoding="utf-8"))
        r["slug"] = f"{r['id']:02d}-{slug(r['title'])}"
        r["cats"] = categories(r["title"])
        rs.append(r)
    return sorted(rs, key=lambda r: r["title"].lower())

def ingredient_html(items):
    out, open_ul = [], False
    for i in items:
        if "section" in i:
            if open_ul: out.append("</ul>"); open_ul = False
            out.append(f"<h3>{e(i['section'])}</h3>")
            continue
        if not open_ul: out.append('<ul class="ing">'); open_ul = True
        qty = " ".join(e(x) for x in (i.get("amount"), i.get("measure")) if x and x not in HIDDEN_MEASURES)
        name = e(i.get("ingredient") or "")
        if i.get("comment"): name += f", <span class='c'>{e(i['comment'])}</span>"
        out.append(f"<li><span class='q'>{qty}</span><span class='n'>{name}</span></li>")
    if open_ul: out.append("</ul>")
    return "\n".join(out)

def recipe_page(r):
    soon = '<p class="soon">Coming soon &mdash; this recipe hasn\'t been fully written down yet.</p>' if r["coming_soon"] else ""
    tags = "".join(f"<span class='tag'>{e(c)}</span>" for c in r["cats"])
    body = f"<article class='recipe'><p class='back'><a href='{BASE}'>&larr; All recipes</a></p><h1>{e(r['title'])}</h1><div class='tags'>{tags}</div>{soon}"
    if r["ingredients"]:
        body += f"<section><h2>Ingredients</h2>{ingredient_html(r['ingredients'])}</section>"
    if r["steps"]:
        body += "<section><h2>Steps</h2><ol class='steps'>" + "".join(f"<li>{e(s)}</li>" for s in r["steps"]) + "</ol></section>"
    if r.get("notes"):
        body += "<section><h2>Notes</h2>" + "".join(f"<p>{e(n)}</p>" for n in r["notes"]) + "</section>"
    body += "<p class='print'><button onclick='window.print()'>Print this recipe</button></p></article>"
    return page(r["title"], body)

def index_page(rs):
    names = [n for n, _ in CATS] + ["Other"]
    used = [n for n in names if any(n in r["cats"] for r in rs)]
    chips = "<button class='chip on' data-cat=''>All</button>" + "".join(f"<button class='chip' data-cat='{e(n)}'>{e(n)}</button>" for n in used)
    cards = []
    for r in rs:
        soon = "<span class='badge'>Coming soon</span>" if r["coming_soon"] else ""
        cards.append(f"<li class='card' data-cats='{e('|'.join(r['cats']))}' data-text='{e(r['title'].lower())}'><a href='{BASE}{r['slug']}/'><span class='t'>{e(r['title'])}</span>{soon}<span class='cs'>{e(' · '.join(r['cats']))}</span></a></li>")
    body = f"""<h1>Family Recipes</h1>
<input id="q" type="search" placeholder="Search recipes…" aria-label="Search recipes" autocomplete="off">
<div class="chips">{chips}</div>
<ul class="cards" id="list">{''.join(cards)}</ul>
<p id="none" hidden>No recipes match.</p>
<script>
const q=document.getElementById('q'),cards=[...document.querySelectorAll('.card')];let cat='';
function f(){{const s=q.value.trim().toLowerCase();let n=0;cards.forEach(c=>{{const ok=(!s||c.dataset.text.includes(s))&&(!cat||c.dataset.cats.split('|').includes(cat));c.hidden=!ok;n+=ok}});document.getElementById('none').hidden=n>0}}
q.addEventListener('input',f);
document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));b.classList.add('on');cat=b.dataset.cat;f()}});
</script>"""
    return page("Jiten & Alicia's Family Recipes", body)

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "static"), OUT)
    rs = load()
    open(os.path.join(OUT, "index.html"), "w").write(index_page(rs))
    for r in rs:
        d = os.path.join(OUT, r["slug"]); os.makedirs(d)
        open(os.path.join(d, "index.html"), "w").write(recipe_page(r))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"Built {len(rs)} recipes into {OUT}")

if __name__ == "__main__":
    main()
