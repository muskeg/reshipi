---
description: "Scan all recipes and find/download images from the web for any recipe that is missing one. Updates all language variants of the recipe with the image reference."
---

# Recipe Image Finder Skill

## Purpose

Scans all recipe files in `docs/recipes/`, identifies recipes without images, searches the web for a suitable photo, downloads it, and updates the recipe markdown files.

## Workflow

### Step 1 — Identify recipes missing images

Scan all base (unsuffixed) `.md` files in `docs/recipes/` (excluding `index.md`).

For each recipe, check if:
- The file contains an image reference (`![`)
- The referenced image file exists in `docs/recipes/images/`

Collect a list of recipes that are missing images.

### Step 2 — For each recipe missing an image

For each recipe without an image:

1. **Read the recipe** to get the title and key ingredients (needed for search).

2. **Search for an image** using `fetch_webpage` to find a suitable photo. Search for `"<recipe title> recipe photo"` or similar queries. The image should be:
   - A photo of the finished dish (not ingredients, not a person)
   - High quality, appetizing
   - Landscape orientation preferred (at least 800px wide)
   - From a source that allows hotlinking or download

3. **Download the image** to `docs/recipes/images/<slug>.jpg` (or `.png`/`.webp`). Use `curl` via the terminal to download. Verify the file is a valid image.

4. **Update all language variants** of the recipe to include the image. Insert the image reference after the metadata table and before the ingredients heading:

   ```markdown
   | **Cook time label** | value |

   ![Recipe Title](images/<slug>.jpg)

   ## Ingredients heading
   ```

   Update each language variant:
   - `<slug>.md` — French alt text
   - `<slug>.ja.md` — Japanese alt text
   - `<slug>.en.md` — Original alt text (if file exists)

### Step 3 — Verify

Run `pytest tests/ -v` to confirm the build still passes.

## Important Rules

- Only download images for recipes that don't already have one
- Use the recipe slug for the image filename (e.g., `creme-brulee.jpg`)
- Store all images in `docs/recipes/images/`
- Use relative paths in markdown: `images/<slug>.jpg`
- Alt text should be the recipe title in the appropriate language
- Prefer JPEG format for photos
- Do not download copyrighted images with restrictive licenses — prefer Creative Commons or freely available recipe photos
