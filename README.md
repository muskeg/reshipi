# Reshipi 🍳

A multilingual recipe website built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and deployed to GitHub Pages.

## Languages

- **Original** — the recipe in its source language
- **Français** — French translation
- **日本語** — Japanese translation

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Serve locally with live reload
mkdocs serve

# Build the site
mkdocs build
```

## Adding a recipe

Place recipe files in `docs/recipes/` using the suffix convention:

| File | Language |
|---|---|
| `my-recipe.md` | Original (default) |
| `my-recipe.fr.md` | Français |
| `my-recipe.ja.md` | 日本語 |

Then add an entry to the `nav` section in `mkdocs.yml`.

## Deployment

Pushing to `main` automatically builds and deploys to GitHub Pages via the workflow in `.github/workflows/deploy.yml`.

Make sure **GitHub Pages** is configured to deploy from **GitHub Actions** in your repository settings (Settings → Pages → Source → GitHub Actions).
