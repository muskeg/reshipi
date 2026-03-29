"""MkDocs hook — pre-render unit conversions with locale-aware unit names.

For each <span class="qty" data-qty="N" data-unit="U" data-type="T">text</span>,
this hook outputs three hidden variants (original / metric / imperial) so the
client-side JS only has to toggle visibility.
"""

import re

# ── Ingredient densities (grams per 240 ml cup) ─────────────────────────────

DENSITY = {
    # Flours & starches
    "flour": 120, "bread_flour": 130, "cake_flour": 115,
    "whole_wheat_flour": 128, "almond_flour": 96, "coconut_flour": 128,
    "cornstarch": 128, "rice_flour": 160,
    # Sugars
    "sugar": 200, "brown_sugar": 220, "powdered_sugar": 120,
    "honey": 340, "maple_syrup": 315, "molasses": 328,
    # Dairy & fats
    "butter": 227, "cream": 240, "milk": 245, "yogurt": 245,
    "sour_cream": 230, "cream_cheese": 232, "oil": 218,
    # Grains & legumes
    "rice": 185, "oats": 80, "beans": 180, "lentils": 190, "quinoa": 170,
    # Nuts & seeds
    "almonds": 140, "walnuts": 120, "pecans": 110, "peanuts": 145,
    "sesame_seeds": 144, "chia_seeds": 162,
    # Cocoa & chocolate
    "cocoa_powder": 85, "chocolate_chips": 170,
    # Salt & spices
    "salt": 288, "coarse_salt": 240,
    # Liquids
    "water": 240, "juice": 240, "broth": 240, "vinegar": 240,
    "soy_sauce": 255, "miso": 275,
}

# Ingredient types that should stay as volume in metric mode (not convert to weight)
LIQUID_TYPES = {
    "water", "juice", "broth", "vinegar", "soy_sauce",
    "milk", "cream", "oil", "honey", "maple_syrup", "molasses",
    "yogurt", "sour_cream",
}

# ── Unit conversion factors ──────────────────────────────────────────────────

WEIGHT_TO_G = {"g": 1, "kg": 1000, "oz": 28.3495, "lb": 453.592}
VOLUME_TO_ML = {
    "ml": 1, "l": 1000, "cl": 10, "dl": 100,
    "cup": 240, "tbsp": 15, "tsp": 5, "fl_oz": 29.5735,
}

# ── Translated unit names ────────────────────────────────────────────────────
# Tuple = (singular, plural).  String = invariable.

UNIT_NAMES = {
    "fr": {
        "g": "g", "kg": "kg", "ml": "ml", "l": "l", "cl": "cl", "dl": "dl",
        "cup": ("tasse", "tasses"), "tbsp": "c. à soupe", "tsp": "c. à thé",
        "oz": "oz", "lb": "lb", "fl_oz": "oz liq.",
    },
    "ja": {
        "g": "g", "kg": "kg", "ml": "ml", "l": "リットル", "cl": "cl", "dl": "dl",
        "cup": "カップ", "tbsp": "大さじ", "tsp": "小さじ",
        "oz": "オンス", "lb": "ポンド", "fl_oz": "fl oz",
    },
    "en": {
        "g": "g", "kg": "kg", "ml": "ml", "l": "L", "cl": "cl", "dl": "dl",
        "cup": ("cup", "cups"), "tbsp": "tbsp", "tsp": "tsp",
        "oz": "oz", "lb": "lb", "fl_oz": "fl oz",
    },
}

# Units where Japanese puts the unit name BEFORE the number (大さじ1, 小さじ½)
_JA_UNIT_FIRST = {"tbsp", "tsp"}


def _is_weight(unit):
    return unit in WEIGHT_TO_G


def _is_volume(unit):
    return unit in VOLUME_TO_ML


# ── Number formatting ────────────────────────────────────────────────────────

_FRACTIONS = [
    (1 / 8, "⅛"), (1 / 4, "¼"), (1 / 3, "⅓"), (3 / 8, "⅜"),
    (1 / 2, "½"), (5 / 8, "⅝"), (2 / 3, "⅔"), (3 / 4, "¾"), (7 / 8, "⅞"),
]


def _fmt_num(n):
    whole = int(n)
    frac = n - whole
    frac_sym = None
    for val, sym in _FRACTIONS:
        if abs(frac - val) < 0.06:
            frac_sym = sym
            break
    if frac_sym:
        return f"{whole}{frac_sym}" if whole else frac_sym
    if n >= 100:
        return str(round(n))
    if n >= 10:
        v = round(n, 1)
        return str(int(v)) if v == int(v) else str(v)
    v = round(n, 2)
    return str(int(v)) if v == int(v) else str(v)


# ── Unit name lookup (with pluralisation) ────────────────────────────────────

def _unit_name(unit_code, value, locale):
    names = UNIT_NAMES.get(locale, UNIT_NAMES["en"])
    entry = names.get(unit_code, unit_code)
    if isinstance(entry, tuple):
        return entry[0] if abs(value) <= 1 else entry[1]
    return entry


# ── Locale-aware formatting of "number + unit" ──────────────────────────────

def _format(value, unit_code, locale):
    num = _fmt_num(value)
    name = _unit_name(unit_code, value, locale)
    if locale == "ja":
        if unit_code in _JA_UNIT_FIRST:
            return f"{name}{num}"
        if unit_code in ("g", "kg", "ml", "l", "cl", "dl"):
            return f"{num}\u202f{name}"          # thin space
        return f"{num}\u00a0{name}"
    return f"{num}\u00a0{name}"                  # non-breaking space


# ── Best-unit selectors ─────────────────────────────────────────────────────

def _best_metric_weight(g):
    if g >= 1000:
        return g / 1000, "kg"
    return g, "g"


def _best_metric_volume(ml):
    if ml >= 1000:
        return ml / 1000, "l"
    return ml, "ml"


def _best_imperial_weight(g):
    oz = g / WEIGHT_TO_G["oz"]
    if oz >= 16:
        return oz / 16, "lb"
    return oz, "oz"


def _best_imperial_volume(ml):
    cups = ml / VOLUME_TO_ML["cup"]
    if cups >= 0.2:
        return cups, "cup"
    tbsp = ml / VOLUME_TO_ML["tbsp"]
    if tbsp >= 1:
        return tbsp, "tbsp"
    return ml / VOLUME_TO_ML["tsp"], "tsp"


# ── Core conversion ─────────────────────────────────────────────────────────

def _convert(qty, unit, dtype, mode, locale):
    """Return the display string for *mode* in the given *locale*."""
    if mode == "original":
        return None  # keep original text as-is

    if not _is_weight(unit) and not _is_volume(unit):
        return None  # non-convertible

    if mode == "metric":
        if _is_weight(unit):
            g = qty * WEIGHT_TO_G[unit]
            val, u = _best_metric_weight(g)
            return _format(val, u, locale)
        if _is_volume(unit):
            ml = qty * VOLUME_TO_ML[unit]
            if dtype and dtype in DENSITY and dtype not in LIQUID_TYPES:
                g = ml * DENSITY[dtype] / 240
                val, u = _best_metric_weight(g)
                return _format(val, u, locale)
            val, u = _best_metric_volume(ml)
            return _format(val, u, locale)

    if mode == "imperial":
        if _is_weight(unit):
            g = qty * WEIGHT_TO_G[unit]
            if dtype and dtype in DENSITY:
                ml = (g / DENSITY[dtype]) * 240
                val, u = _best_imperial_volume(ml)
                return _format(val, u, locale)
            val, u = _best_imperial_weight(g)
            return _format(val, u, locale)
        if _is_volume(unit):
            ml = qty * VOLUME_TO_ML[unit]
            val, u = _best_imperial_volume(ml)
            return _format(val, u, locale)

    return None


# ── Regex to find qty spans in markdown ──────────────────────────────────────

_QTY_RE = re.compile(
    r'<span\s+class="qty"\s+'
    r'data-qty="([^"]+)"\s+'
    r'data-unit="([^"]+)"'
    r'(?:\s+data-type="([^"]*)")?'
    r'\s*>([^<]*)</span>'
)


def _detect_locale(page):
    src = page.file.src_path
    m = re.search(r"\.(\w{2})\.md$", src)
    return m.group(1) if m else "fr"


def _replace_qty(match, locale):
    qty_str, unit, dtype, original_text = match.groups()
    try:
        qty = float(qty_str)
    except ValueError:
        return match.group(0)

    dtype = dtype or ""
    metric_text = _convert(qty, unit, dtype, "metric", locale)
    imperial_text = _convert(qty, unit, dtype, "imperial", locale)

    # If conversion produced nothing, keep original only
    if not metric_text and not imperial_text:
        return match.group(0)

    parts = [
        f'<span class="qty-val" data-mode="original">{original_text}</span>',
    ]
    parts.append(
        f'<span class="qty-val" data-mode="metric">'
        f'{metric_text or original_text}</span>'
    )
    parts.append(
        f'<span class="qty-val" data-mode="imperial">'
        f'{imperial_text or original_text}</span>'
    )
    return f'<span class="qty-group">{"".join(parts)}</span>'


# ── MkDocs hook entry point ─────────────────────────────────────────────────

def on_page_markdown(markdown, page, config, files):
    locale = _detect_locale(page)
    return _QTY_RE.sub(lambda m: _replace_qty(m, locale), markdown)
