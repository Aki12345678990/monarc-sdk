"""Vendored config_v2.py constants must match the ported module (ast only)."""

import ast

from analyzer_core import v2_constants
from analyzer_core.config import reference_dir

_NAMES = (
    "TOOLCHAIN_PREFIXES",
    "FRAMEWORK_PREFIXES",
    "FRAMEWORK_NATIVE_LIBS",
    "HOST_DENYLIST",
    "SERVICE_SDK_CATEGORIES",
    "SDK_CATEGORY_VOCABULARY",
)


def test_ported_constants_equal_vendored_config_v2():
    source = (reference_dir() / "config_v2.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    vendored = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in _NAMES:
                vendored[target.id] = ast.literal_eval(node.value)
    assert set(vendored) == set(_NAMES)
    for name in _NAMES:
        assert vendored[name] == getattr(v2_constants, name), name
