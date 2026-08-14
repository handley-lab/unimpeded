"""Tests that the declared packaging metadata matches what the code needs."""

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = REPO_ROOT / "unimpeded"

#: Import name -> distribution name, where the two differ.
IMPORT_TO_DISTRIBUTION = {"yaml": "pyyaml"}


def _third_party_imports():
    """Collect every non-stdlib module imported at top level by the package."""
    modules = set()
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                # level > 0 is a relative import, which is our own package.
                if node.level == 0 and node.module:
                    modules.add(node.module.split(".")[0])
    return {m for m in modules if m not in sys.stdlib_module_names and m != "unimpeded"}


def _declared_dependencies():
    """Parse the runtime dependency names out of pyproject.toml."""
    text = (REPO_ROOT / "pyproject.toml").read_text()
    block = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.MULTILINE | re.DOTALL)
    assert block, "no [project] dependencies array found in pyproject.toml"
    # Names only: strip any version specifier, extras or environment marker.
    return {
        re.split(r"[<>=!~\[; ]", item)[0].strip().lower()
        for item in re.findall(r'"([^"]+)"', block.group(1))
    }


def test_every_imported_package_is_declared():
    """Each third-party import has a matching runtime dependency.

    unimpeded.tension imports numpy and scipy directly. Both previously
    resolved only because anesthetic happens to require them, so the package
    would have broken with an ImportError for a dependency it never declared
    had anesthetic ever dropped or reorganised them.
    """
    declared = _declared_dependencies()
    missing = sorted(
        m
        for m in _third_party_imports()
        if IMPORT_TO_DISTRIBUTION.get(m, m).lower() not in declared
    )
    assert not missing, (
        f"imported but not declared in pyproject.toml: {missing}. "
        f"Declared: {sorted(declared)}"
    )


def test_declared_dependencies_are_all_used():
    """No runtime dependency is declared without being imported.

    Catches the reverse drift, where a dependency is removed from the code but
    left in the metadata, making installs heavier than they need to be.
    """
    imported = {
        IMPORT_TO_DISTRIBUTION.get(m, m).lower() for m in _third_party_imports()
    }
    unused = sorted(d for d in _declared_dependencies() if d not in imported)
    assert not unused, f"declared in pyproject.toml but never imported: {unused}"
