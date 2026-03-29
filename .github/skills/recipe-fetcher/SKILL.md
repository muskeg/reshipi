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

<!-- recipe-data
{
  "title": {
    "fr": "French title",
    "ja": "Japanese title",
    "en": "Original title (if applicable)"
  },
  "description": {
    "fr": "Short French description",
    "ja": "Short Japanese description",
    "en": "Short original description (if applicable)"
  },
  "servings": 4,
  "prep_time": "20 min",
  "cook_time": "45 min",
  "tags": {
    "fr": ["tag1", "tag2"],
    "ja": ["タグ1", "タグ2"],
    "en": ["tag1", "tag2"]
  },
  "ingredients": {
    "fr": ["ingredient 1", "ingredient 2"],
    "ja": ["材料1", "材料2"],
    "en": ["ingredient 1", "ingredient 2"]
  },
  "instructions": {
    "fr": ["Step 1.", "Step 2."],
    "ja": ["手順1。", "手順2。"],
    "en": ["Step 1.", "Step 2."]
  },
  "image": "<slug>.jpg",
  "source_url": "https://example.com/original-recipe",
  "source_language": "en"
}
-->

# Recipe Title

A short, one or two sentence description of the dish. Factual and to the point — what it is, where it comes from, what makes it distinctive. No fluff.

| | |
|---|---|
| **Servings label** | value |
| **Prep time label** | value |
| **Cook time label** | value |

![Recipe Title](image-url)

## Ingredients heading

- <span class="qty" data-qty="500" data-unit="g" data-type="flour">500 g</span> de farine
- <span class="qty" data-qty="240" data-unit="ml" data-type="milk">240 ml</span> de lait
- <span class="qty" data-qty="1" data-unit="tsp">1 c. à c.</span> de sel
- 2 œufs

## Instructions heading

1. Step 1.
2. Step 2.
3. ...

---

*Source: [domain.com](original-url)*
```

#### Ingredient unit markup

**CRITICAL — Convertible quantities:**
Every numeric quantity in the ingredients list (and in instructions when relevant) MUST be wrapped in a `<span>` tag with the following attributes:

```html
<span class="qty" data-qty="500" data-unit="g" data-type="flour">500 g</span>
```

- `class="qty"` — required, identifies the element for the conversion engine
- `data-qty` — the numeric value as originally written (e.g. `500`, `1.5`, `0.25`)
- `data-unit` — the unit code. Supported units:
  - **Weight**: `g`, `kg`, `oz`, `lb`
  - **Volume**: `ml`, `l`, `cl`, `dl`, `cup`, `tbsp`, `tsp`, `fl_oz`
  - **Count**: `piece` (not converted, but tagged for consistency)
- `data-type` — the ingredient type for density-based volume↔weight conversion. Use when the ingredient has a known density. Common types:
  `flour`, `bread_flour`, `cake_flour`, `whole_wheat_flour`, `almond_flour`, `coconut_flour`, `cornstarch`, `rice_flour`,
  `sugar`, `brown_sugar`, `powdered_sugar`, `honey`, `maple_syrup`, `molasses`,
  `butter`, `cream`, `milk`, `yogurt`, `sour_cream`, `cream_cheese`, `oil`,
  `rice`, `oats`, `beans`, `lentils`, `quinoa`,
  `almonds`, `walnuts`, `pecans`, `peanuts`, `sesame_seeds`, `chia_seeds`,
  `cocoa_powder`, `chocolate_chips`,
  `salt`, `coarse_salt`,
  `water`, `juice`, `broth`, `vinegar`, `soy_sauce`, `miso`
- The visible text inside the span is the **original** quantity as it appears in the recipe

**Items without measurable quantities** (e.g. "2 eggs", "salt to taste", "a pinch of pepper") should NOT be wrapped in a span. Just write them as plain text.

The conversion engine provides three views via buttons: **Original** (as written), **Métrique** (grams/ml/kg/l), **Impérial** (cups/tbsp/tsp/oz/lb).

#### Language-specific labels

**IMPORTANT — Embedded recipe data:**
Every recipe file (all language variants) MUST include the same `<!-- recipe-data ... -->` HTML comment block immediately after the YAML frontmatter. This block contains a JSON object with ALL translations and structured data for the recipe. The JSON is identical across all locale files for the same recipe. This makes the content portable — the structured data can be parsed and reused independently of MkDocs.

The JSON object fields:
- `title` — recipe title in each language (`fr`, `ja`, and optionally `en`)
- `description` — short description in each language
- `servings` — number (integer)
- `prep_time` — string (e.g. "20 min")
- `cook_time` — string (e.g. "45 min")
- `tags` — array of tags per language
- `ingredients` — array of ingredient strings per language (with quantities)
- `instructions` — array of step strings per language
- `image` — filename only (e.g. `"creme-brulee.jpg"`)
- `source_url` — original recipe URL
- `source_language` — ISO 639-1 code of the source recipe language

If the source language is French or Japanese (no `.en.md` file), omit the `"en"` key from all fields.

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

### Step 5 — Add recipe card to index pages

Add a new recipe card to both `docs/index.md` and `docs/index.ja.md` inside the existing `<div class="recipe-grid">`.

Each card must include:
- `data-tags` — comma-separated list of all tags (in the page's language)
- `data-category` — exactly ONE main category from this fixed list:

**Standard categories (French / Japanese):**
| French | Japanese | Use for |
|---|---|---|
| `entrées` | `前菜` | Starters, appetizers, soups |
| `plats` | `メイン` | Main courses |
| `accompagnements` | `付け合わせ` | Side dishes |
| `salades` | `サラダ` | Salads |
| `desserts` | `デザート` | Desserts, sweets |
| `condiments` | `調味料` | Sauces, condiments, pickles |
| `boissons` | `飲み物` | Drinks |
| `pains` | `パン` | Breads, pastries |
| `bases` | `基本` | Stocks, doughs, base recipes |

Pick the single most fitting category. Each recipe gets exactly one.

Card HTML template:
```html
<div class="recipe-card" data-tags="tag1,tag2,tag3" data-category="category">
<a href="recipes/<slug>/">
<img src="/reshipi/recipes/images/<slug>.jpg" alt="Title" loading="lazy">
<div class="card-body">
<h3>Title</h3>
<p>Short description.</p>
</div>
<div class="card-tags">
<span>tag1</span>
<span>tag2</span>
<span>tag3</span>
</div>
</a>
</div>
```

**Note:** Image `src` must use the absolute path `/reshipi/recipes/images/` (not a relative path) so images work across all locales.

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
