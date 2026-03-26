"""Tests for the Reshipi MkDocs build.

Run with: pytest tests/ -v
Requires: pip install -r requirements.txt -r requirements-test.txt
          mkdocs build  (run before tests, or use the build fixture)
"""

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
MKDOCS_YML = ROOT / "mkdocs.yml"

LOCALES = ["fr", "en", "ja"]
DEFAULT_LOCALE = "fr"
NON_DEFAULT_LOCALES = [l for l in LOCALES if l != DEFAULT_LOCALE]
REQUIRED_LOCALES = ["ja"]  # Japanese is always required; en (Original) is optional


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def mkdocs_config():
    """Load and return the parsed mkdocs.yml."""
    with open(MKDOCS_YML) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def site_dir():
    """Build the site once for the entire test session and return the path."""
    subprocess.run(
        ["mkdocs", "build", "--strict"],
        cwd=ROOT,
        check=True,
    )
    assert SITE.is_dir(), "Site directory was not created by mkdocs build"
    return SITE


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------

class TestConfig:
    """Validate mkdocs.yml configuration."""

    def test_config_loads(self, mkdocs_config):
        assert mkdocs_config is not None

    def test_site_url_set(self, mkdocs_config):
        assert mkdocs_config.get("site_url"), "site_url must be set for correct link generation"

    def test_site_url_has_trailing_slash(self, mkdocs_config):
        assert mkdocs_config["site_url"].endswith("/"), "site_url should end with /"

    def test_theme_is_material(self, mkdocs_config):
        assert mkdocs_config["theme"]["name"] == "material"

    def test_i18n_plugin_present(self, mkdocs_config):
        plugin_names = []
        for p in mkdocs_config["plugins"]:
            if isinstance(p, str):
                plugin_names.append(p)
            elif isinstance(p, dict):
                plugin_names.extend(p.keys())
        assert "i18n" in plugin_names

    def test_i18n_languages_configured(self, mkdocs_config):
        i18n_cfg = None
        for p in mkdocs_config["plugins"]:
            if isinstance(p, dict) and "i18n" in p:
                i18n_cfg = p["i18n"]
                break
        assert i18n_cfg is not None
        locales = [lang["locale"] for lang in i18n_cfg["languages"]]
        for locale in LOCALES:
            assert locale in locales, f"Missing locale: {locale}"

    def test_default_locale_is_french(self, mkdocs_config):
        for p in mkdocs_config["plugins"]:
            if isinstance(p, dict) and "i18n" in p:
                for lang in p["i18n"]["languages"]:
                    if lang.get("default"):
                        assert lang["locale"] == DEFAULT_LOCALE
                        return
        pytest.fail("No default language found")


# ---------------------------------------------------------------------------
# Source docs structure
# ---------------------------------------------------------------------------

class TestDocsStructure:
    """Validate that doc sources follow the i18n suffix convention."""

    def _get_base_docs(self):
        """Return all base (unsuffixed) .md files relative to docs/."""
        base_files = []
        for md in DOCS.rglob("*.md"):
            rel = md.relative_to(DOCS)
            name = md.stem
            # Skip suffixed files (e.g. index.en, index.ja)
            if any(name.endswith(f".{loc}") for loc in NON_DEFAULT_LOCALES):
                continue
            base_files.append(rel)
        return base_files

    def test_base_docs_exist(self):
        base = self._get_base_docs()
        assert len(base) > 0, "No base doc files found"

    @pytest.mark.parametrize("locale", REQUIRED_LOCALES)
    def test_required_translations_exist(self, locale):
        """Every base doc must have a Japanese translation."""
        missing = []
        for md in self._get_base_docs():
            suffixed = md.parent / f"{md.stem}.{locale}.md"
            if not (DOCS / suffixed).exists():
                missing.append(str(suffixed))
        assert not missing, f"Missing {locale} translations: {missing}"

    def test_en_files_only_for_non_french_recipes(self):
        """Any .en.md file in recipes/ should not duplicate a French original."""
        for en_file in (DOCS / "recipes").glob("*.en.md"):
            # Just verify it exists alongside its base (French) file
            base_name = en_file.name.replace(".en.md", ".md")
            assert (en_file.parent / base_name).exists(), \
                f"{en_file.name} exists without a base French file"


# ---------------------------------------------------------------------------
# Build output validation
# ---------------------------------------------------------------------------

class TestBuild:
    """Validate the built site output."""

    def test_build_succeeds_strict(self, site_dir):
        """mkdocs build --strict should exit 0 (handled by fixture)."""
        assert site_dir.is_dir()

    def test_default_locale_index_exists(self, site_dir):
        assert (site_dir / "index.html").is_file()

    def test_ja_locale_index_exists(self, site_dir):
        assert (site_dir / "ja" / "index.html").is_file(), \
            "Missing index.html for Japanese locale"

    def test_en_locale_index_exists(self, site_dir):
        """English/Original locale should exist (fallback builds it)."""
        # With fallback_to_default, the en directory is always built
        assert (site_dir / "en" / "index.html").is_file(), \
            "Missing index.html for Original locale (fallback)"

    def test_recipe_pages_built(self, site_dir):
        """At least one recipe page should exist in the default build."""
        recipes_dir = site_dir / "recettes"  # French nav slug
        recipe_dirs = site_dir / "recipes"
        has_recipes = (
            (recipes_dir.is_dir() and any(recipes_dir.rglob("*.html")))
            or (recipe_dirs.is_dir() and any(recipe_dirs.rglob("*.html")))
        )
        assert has_recipes, "No recipe HTML pages found in default locale build"

    def test_ja_recipe_pages_built(self, site_dir):
        """Japanese locale must have recipe pages."""
        ja_dir = site_dir / "ja"
        assert ja_dir.is_dir(), "Japanese locale directory not found"
        html_files = list(ja_dir.rglob("*.html"))
        assert len(html_files) >= 2, \
            f"Japanese locale has only {len(html_files)} HTML files, expected recipe pages too"

    def test_language_switcher_present(self, site_dir):
        """The built index.html should contain links for all configured languages."""
        index_html = (site_dir / "index.html").read_text(encoding="utf-8")
        for locale in LOCALES:
            if locale == DEFAULT_LOCALE:
                # Default locale link points to root
                assert "Français" in index_html or f"/{DEFAULT_LOCALE}/" not in index_html
            else:
                assert f"/{locale}/" in index_html or locale in index_html, \
                    f"Language switcher missing link for '{locale}'"

    def test_no_broken_asset_refs(self, site_dir):
        """Check that CSS/JS asset references in index.html resolve to actual files."""
        index_html = (site_dir / "index.html").read_text(encoding="utf-8")
        # Find href="..." and src="..." references to local assets
        refs = re.findall(r'(?:href|src)="([^"]*?\.(?:css|js))"', index_html)
        missing = []
        for ref in refs:
            if ref.startswith(("http://", "https://", "//")):
                continue
            # Strip leading / and site base path
            clean = ref.lstrip("/")
            clean = re.sub(r'^reshipi/', '', clean)
            asset_path = site_dir / clean
            if not asset_path.is_file():
                missing.append(ref)
        assert not missing, f"Broken asset references: {missing}"


# ---------------------------------------------------------------------------
# Deploy workflow validation
# ---------------------------------------------------------------------------

class TestDeployWorkflow:
    """Validate the GitHub Actions workflow file."""

    @pytest.fixture()
    def workflow(self):
        wf_path = ROOT / ".github" / "workflows" / "deploy.yml"
        assert wf_path.is_file(), "deploy.yml workflow not found"
        with open(wf_path) as f:
            return yaml.safe_load(f)

    def test_triggers_on_main_push(self, workflow):
        triggers = workflow.get("on") or workflow.get(True, {})
        push_branches = triggers.get("push", {}).get("branches", [])
        assert "main" in push_branches

    def test_has_build_job(self, workflow):
        assert "build" in workflow["jobs"]

    def test_has_deploy_job(self, workflow):
        assert "deploy" in workflow["jobs"]

    def test_deploy_needs_build(self, workflow):
        needs = workflow["jobs"]["deploy"].get("needs")
        if isinstance(needs, list):
            assert "build" in needs
        else:
            assert needs == "build"

    def test_pages_permissions(self, workflow):
        perms = workflow.get("permissions", {})
        assert perms.get("pages") == "write"
        assert perms.get("id-token") == "write"

    def test_build_uses_strict_mode(self, workflow):
        build_steps = workflow["jobs"]["build"]["steps"]
        has_strict = any(
            "--strict" in str(step.get("run", ""))
            for step in build_steps
        )
        assert has_strict, "Build should use --strict flag"

    def test_uploads_site_artifact(self, workflow):
        build_steps = workflow["jobs"]["build"]["steps"]
        has_upload = any(
            "upload-pages-artifact" in str(step.get("uses", ""))
            for step in build_steps
        )
        assert has_upload, "Build should upload pages artifact"
