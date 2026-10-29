# Jiten & Alicia's family recipes

Live site: https://jvaidya-personal.github.io/recipes/

A small static site. Each recipe is one JSON file in `content/recipes/`. `build.py` (plain Python 3, no dependencies) turns them into HTML in `dist/`, and the GitHub Actions workflow in `.github/workflows/pages.yml` publishes it to GitHub Pages on every push to `main`.

The recipes were imported from the 2017 app at https://github.com/jvaidya/recipes (`src/data/rw`, falling back to `src/data/ro`). The text was kept exactly as written.

## Editing a recipe

1. Open `content/recipes/recipe-NN.json` (on GitHub, click the pencil icon).
2. Change the text and commit to `main`. The site updates in a minute or two.

## Adding a recipe

Copy an existing file to a new number, such as `recipe-43.json`, and fill it in:

```json
{
  "id": 43,
  "title": "My new recipe",
  "coming_soon": false,
  "ingredients": [
    {"section": "For the sauce"},
    {"amount": "2", "measure": "Cup", "ingredient": "Tomatoes", "comment": "chopped"}
  ],
  "steps": ["First step.", "Second step."],
  "notes": ["Optional notes, one paragraph per entry."]
}
```

- `ingredients`: a list of items. `{"section": "..."}` starts a sub-heading. `amount`, `measure` and `comment` can be `null`. A measure of `Count` is hidden, so "2 Count garlic cloves" displays as "2 garlic cloves".
- `coming_soon: true` shows a "Coming soon" badge.
- `notes` is optional.
- Categories (Dal, Chai, Chicken, Vegan, Sauces/Chutneys, Desserts, Other) are worked out from words in the title. See `CATS` in `build.py`.

## Preview locally

```sh
BASE_PATH=/ python3 build.py && python3 -m http.server -d dist 8000
```
