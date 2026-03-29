/**
 * Reshipi — Category/tag filter injected into Material's primary sidebar.
 *
 * Reads data-category and data-tags from .recipe-card elements,
 * builds filter items using Material's nav markup (md-nav__item / md-nav__link),
 * and appends them into the primary sidebar.
 */

(function () {
  "use strict";

  var LABELS = {
    fr: { all: "Toutes les recettes" },
    ja: { all: "すべてのレシピ" },
    en: { all: "All recipes" },
  };

  function getLocale() {
    var lang = document.documentElement.lang || "fr";
    return lang.substring(0, 2);
  }

  function buildSidebar() {
    // Find Material's primary sidebar nav list
    var primaryNav = document.querySelector(
      ".md-sidebar--primary .md-nav--primary > .md-nav__list"
    );
    if (!primaryNav) return;

    // Don't inject twice
    if (primaryNav.querySelector(".filter-section")) return;

    var cards = document.querySelectorAll(".recipe-card[data-tags]");
    if (!cards.length) return;

    var locale = getLocale();
    var labels = LABELS[locale] || LABELS.en;

    // Collect categories and their associated tags
    var categoryTags = {};
    cards.forEach(function (card) {
      var cats = (card.getAttribute("data-category") || "").split(",").filter(Boolean);
      var tags = (card.getAttribute("data-tags") || "").split(",").filter(Boolean);
      cats.forEach(function (cat) {
        if (!categoryTags[cat]) categoryTags[cat] = new Set();
        tags.forEach(function (t) { categoryTags[cat].add(t); });
      });
    });

    // Separator
    var sep = document.createElement("li");
    sep.className = "md-nav__item filter-section";
    sep.innerHTML = '<hr class="filter-divider">';
    primaryNav.appendChild(sep);

    // "All" item
    var allItem = document.createElement("li");
    allItem.className = "md-nav__item filter-section";
    var allLink = document.createElement("a");
    allLink.className = "md-nav__link filter-link filter-all active";
    allLink.href = "#";
    allLink.textContent = labels.all;
    allLink.addEventListener("click", function (e) { e.preventDefault(); filterCards(null); });
    allItem.appendChild(allLink);
    primaryNav.appendChild(allItem);

    // Categories with sub-tags
    var catKeys = Object.keys(categoryTags);
    catKeys.sort();

    catKeys.forEach(function (cat) {
      var catItem = document.createElement("li");
      catItem.className = "md-nav__item filter-section";

      var catLink = document.createElement("a");
      catLink.className = "md-nav__link filter-link filter-category";
      catLink.href = "#";
      catLink.textContent = cat;
      catLink.addEventListener("click", function (e) { e.preventDefault(); filterCards(cat); });
      catItem.appendChild(catLink);

      // Sub-tags: skip tags that match or are near-duplicates of any category name
      var catLower = cat.toLowerCase();
      var allCatLower = catKeys.map(function (c) { return c.toLowerCase(); });
      var subTags = [];
      categoryTags[cat].forEach(function (t) {
        if (categoryTags[t]) return; // exact category match
        var tLower = t.toLowerCase();
        // Skip if tag is a substring of a category or vice-versa (catches dessert/desserts, condiment/condiments)
        var dominated = allCatLower.some(function (cl) {
          return cl.indexOf(tLower) !== -1 || tLower.indexOf(cl) !== -1;
        });
        if (!dominated) subTags.push(t);
      });
      subTags.sort();

      if (subTags.length) {
        var subNav = document.createElement("nav");
        subNav.className = "md-nav";
        var subList = document.createElement("ul");
        subList.className = "md-nav__list";

        subTags.forEach(function (tag) {
          var tagItem = document.createElement("li");
          tagItem.className = "md-nav__item";
          var tagLink = document.createElement("a");
          tagLink.className = "md-nav__link filter-link filter-tag";
          tagLink.href = "#";
          tagLink.textContent = tag;
          tagLink.addEventListener("click", function (e) { e.preventDefault(); filterCards(tag); });
          tagItem.appendChild(tagLink);
          subList.appendChild(tagItem);
        });

        subNav.appendChild(subList);
        catItem.appendChild(subNav);
      }

      primaryNav.appendChild(catItem);
    });
  }

  function filterCards(filter) {
    var cards = document.querySelectorAll(".recipe-card[data-tags]");
    var count = 0;

    cards.forEach(function (card) {
      if (!filter) {
        card.style.display = "";
        count++;
        return;
      }
      var tags = (card.getAttribute("data-tags") || "").split(",");
      var cats = (card.getAttribute("data-category") || "").split(",");
      var all = tags.concat(cats);
      if (all.indexOf(filter) !== -1) {
        card.style.display = "";
        count++;
      } else {
        card.style.display = "none";
      }
    });

    // Update active state
    document.querySelectorAll(".filter-link").forEach(function (link) {
      if (link.classList.contains("filter-all")) {
        link.classList.toggle("active", !filter);
      } else {
        link.classList.toggle("active", link.textContent === filter);
      }
    });
  }

  function init() {
    buildSidebar();
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
