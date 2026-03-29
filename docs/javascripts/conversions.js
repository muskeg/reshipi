/**
 * Reshipi — Unit toggle (display only, conversions are pre-rendered by hooks/conversions.py)
 *
 * The build hook outputs three variants per quantity:
 *   <span class="qty-group">
 *     <span class="qty-val" data-mode="original">...</span>
 *     <span class="qty-val" data-mode="metric">...</span>
 *     <span class="qty-val" data-mode="imperial">...</span>
 *   </span>
 *
 * This script injects toggle buttons and switches visibility via a body attribute.
 */

(function () {
  "use strict";

  var LABELS = {
    fr: [
      { mode: "original", label: "Original" },
      { mode: "metric",   label: "Métrique" },
      { mode: "imperial", label: "Impérial" },
    ],
    ja: [
      { mode: "original", label: "オリジナル" },
      { mode: "metric",   label: "メートル法" },
      { mode: "imperial", label: "ヤード・ポンド法" },
    ],
    en: [
      { mode: "original", label: "Original" },
      { mode: "metric",   label: "Metric" },
      { mode: "imperial", label: "Imperial" },
    ],
  };

  function getLocale() {
    var lang = document.documentElement.lang || "fr";
    return lang.substring(0, 2);
  }

  function applyMode(mode) {
    document.body.setAttribute("data-units", mode);
    document.querySelectorAll(".unit-toggle-btn").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-mode") === mode);
    });
    try { localStorage.setItem("reshipi-units", mode); } catch (e) { /* ok */ }
  }

  function injectButtons() {
    // Find the ingredients heading (h2)
    var headings = document.querySelectorAll("h2");
    var ingredientH2 = null;
    var keywords = ["ingrédients", "ingredients", "材料"];
    for (var i = 0; i < headings.length; i++) {
      var text = headings[i].textContent.toLowerCase().trim();
      for (var k = 0; k < keywords.length; k++) {
        if (text === keywords[k]) { ingredientH2 = headings[i]; break; }
      }
      if (ingredientH2) break;
    }
    if (!ingredientH2) return;

    // Don't inject twice
    if (ingredientH2.parentNode.querySelector(".unit-toggle")) return;

    // Only inject if there are pre-rendered qty groups on the page
    if (!document.querySelector(".qty-group")) return;

    var locale = getLocale();
    var modes = LABELS[locale] || LABELS.en;

    var bar = document.createElement("div");
    bar.className = "unit-toggle";

    modes.forEach(function (m) {
      var btn = document.createElement("button");
      btn.className = "unit-toggle-btn";
      btn.setAttribute("data-mode", m.mode);
      btn.textContent = m.label;
      btn.addEventListener("click", function () { applyMode(m.mode); });
      bar.appendChild(btn);
    });

    ingredientH2.insertAdjacentElement("afterend", bar);
  }

  function init() {
    injectButtons();
    var saved = "original";
    try { saved = localStorage.getItem("reshipi-units") || "original"; } catch (e) { /* ok */ }
    applyMode(saved);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () { init(); });
  }
})();
