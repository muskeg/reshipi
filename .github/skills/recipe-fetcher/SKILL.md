---
description: "Fetch a recipe from a URL, extract the essential content (ingredients, steps, one photo), discard life stories and verbose filler, and output properly formatted recipe files for the Reshipi multilingual MkDocs site in French, Japanese, and optionally Original."
---

# Recipe Fetcher Skill

## Purpose

Given a recipe URL, this skill:
1. Fetches the web page content
2. Extracts ONLY the essential recipe data (title, servings, prep time, cook time, ingredients, instructions, one image)
3. Discards all life stories, SEO filler, ads, and overly verbose context
4. Outputs the recipe as properly formatted markdown files for the Reshipi project
5. Translates into the required languages

## Workflow

### Step 1 — Fetch & Extract

Use the `fetch_webpage` tool to retrieve the page content from the provided URL.

From the fetched content, identify and extract:
- **Title** of the recipe
- **Servings** (number of portions)
- **Prep time**
- **Cook time**
- **Ingredients** — list with quantities and units
- **Instructions** — numbered steps, concise and actionable
- **One image URL** — the primary/hero photo of the finished dish
- **Source language** — detect what language the original recipe is in
- **Tags** — infer 3–5 relevant tags (cuisine type, main ingredient, meal type, etc.)

**CRITICAL:** Ignore all narrative content, personal stories, tips about the author's life, "jump to recipe" filler, SEO paragraphs, and ad-related content. Extract ONLY the recipe itself.

### Step 2 — Determine Languages & File Slug

Determine the file slug from the recipe title (lowercase, hyphenated, no accents for the filename).
Example: "Crème Brûlée" → `creme-brulee`

Determine which files to create based on the source language:
- If source is **French**: create `<slug>.md` (French/default) + `<slug>.ja.md` (Japanese)
- If source is **Japanese**: create `<slug>.md` (French) + `<slug>.ja.md` (Japanese original)
- If source is **any other language**: create `<slug>.md` (French) + `<slug>.en.md` (Original) + `<slug>.ja.md` (Japanese)

### Step 3 — Generate Recipe Files

Each recipe file MUST follow this exact format:

```markdown
---
tags:
  - tag1
  - tag2
  - tag3
---

# Recipe Title

A short, one or two sentence description of the dish. Factual and to the point — what it is, where it comes from, what makes it distinctive. No fluff.

| | |
|---|---|
| **Servings label** | value |
| **Prep time label** | value |
| **Cook time label** | value |

![Recipe Title](image-url)

## Ingredients heading

- ingredient 1
- ingredient 2
- ...

## Instructions heading

1. Step 1.
2. Step 2.
3. ...

---

*Source: [domain.com](original-url)*
```

#### Language-specific labels

**French (.md — default):**
- Tags: in French
- Headings: `## Ingrédients`, `## Instructions`
- Table labels: `**Portions**`, `**Préparation**`, `**Cuisson**`
- Image alt text: French title

**Original (.en.md):**
- Tags: in the original language (English if source is English, etc.)
- Headings: `## Ingredients`, `## Instructions`
- Table labels: `**Servings**`, `**Prep time**`, `**Cook time**`
- Image alt text: original title
- Keep original measurements/units as-is

**Japanese (.ja.md):**
- Tags: in Japanese
- Headings: `## 材料`, `## 作り方`
- Table labels: `**人数**`, `**準備時間**`, `**調理時間**`
- Image alt text: Japanese title
- Convert measurements to metric where appropriate

### Step 4 — Create the files

Use file creation tools to write each file to `docs/recipes/<slug>.<locale>.md`.

### Step 5 — Update mkdocs.yml

Add the new recipe to the `nav` section in `mkdocs.yml` under `Recettes`, using the **French title**:

```yaml
nav:
  - Accueil: index.md
  - Recettes:
      - recipes/index.md
      - French Title: recipes/<slug>.md
  - Tags: tags.md
```

### Step 6 — Download the image

Download the recipe image and save it to `docs/recipes/images/<slug>.jpg` (or `.png`/`.webp` depending on the source format). Update the image references in all recipe files to use the local path: `images/<slug>.jpg`.

### Step 7 — Verify

Run `pytest tests/ -v` to confirm the build still passes with the new recipe.

## Example Invocation

User: "Add this recipe: https://example.com/best-chocolate-cake"

The skill fetches the page, extracts the chocolate cake recipe, creates:
- `docs/recipes/chocolate-cake.md` (French translation)
- `docs/recipes/chocolate-cake.en.md` (Original English)
- `docs/recipes/chocolate-cake.ja.md` (Japanese translation)
- `docs/recipes/images/chocolate-cake.jpg` (downloaded image)

Updates `mkdocs.yml` nav, then runs tests to verify.
