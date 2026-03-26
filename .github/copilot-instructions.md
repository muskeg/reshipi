---
applyTo: "**"
---

# Reshipi — Project Instructions

This is a multilingual recipe website built with MkDocs Material and mkdocs-static-i18n.

## Project Structure

- `docs/` — Source markdown files
- `docs/recipes/` — Recipe files
- `docs/recipes/<slug>.md` — Default language (French)
- `docs/recipes/<slug>.en.md` — Original (only when source is not French or Japanese)
- `docs/recipes/<slug>.ja.md` — Japanese
- `mkdocs.yml` — MkDocs configuration
- `tests/` — Pytest test suite

## Languages

- **French (fr)** — Default. Unsuffixed `.md` files. Always present.
- **Japanese (ja)** — `.ja.md` suffix. Always present.
- **Original (en)** — `.en.md` suffix. Optional. Only created when the source recipe is in a language other than French or Japanese.

## Recipe File Convention

Each recipe produces 2 or 3 files in `docs/recipes/`:
- `<slug>.md` — French version (always present, this is the default language)
- `<slug>.ja.md` — Japanese version (always present)
- `<slug>.en.md` — Original version (only if the source recipe is NOT French or Japanese)

If the original recipe is in French, only 2 files are needed (`.md` and `.ja.md`).
If the original recipe is in Japanese, only 2 files are needed (`.md` and `.ja.md` becomes the original).
If the original recipe is in any other language, 3 files are needed (`.md`, `.ja.md`, and `.en.md` for the original).

## After Adding a Recipe

1. Add a nav entry in `mkdocs.yml` under the `Recettes` section
2. Run `pytest tests/ -v` to verify the build

## Adding Recipes from URLs

Use the `recipe-fetcher` agent (or invoke the `recipe-fetcher` skill) to fetch, extract, translate, and create recipe files from a URL. It handles the full workflow: fetch → extract → translate → create files → download image → update nav → run tests.

