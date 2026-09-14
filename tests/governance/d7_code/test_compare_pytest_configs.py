# [BLUEPRINT] MOD-GOV_CHECK_ALGO_FLOW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [A_module] module_id=MOD-GOV_CHECK_ALGO_FLOW | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""compare_pytest_configs 行为锚点测试（2026-09-15 外审遗留②配套）。

覆盖：对齐通过 / markers 漂移检出 / timeout 漂移检出 / cache_dir 禁入检出 /
ini 缺失检出 / 非法 TOML 降级 exit 2。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "governance" / "d7_code" / "compare_pytest_configs.py"
_spec = importlib.util.spec_from_file_location("compare_pytest_configs", _SCRIPT)
cpc = importlib.util.module_from_spec(_spec)
sys.modules["compare_pytest_configs"] = cpc
_spec.loader.exec_module(cpc)

_ALIGNED_PYPROJECT = """
[tool.pytest.ini_options]
addopts = ["-v"]
timeout = 120
markers = [
    "slow: marks slow tests",
    "financial: marks financial calculation tests",
]
"""

_ALIGNED_INI = """
[pytest]
addopts = -q --strict-markers
timeout = 120
markers = slow: marks slow tests; financial: marks financial calculation tests
"""


def _make_repo(tmp_path: Path, pyproject: str, ini: str | None) -> Path:
    (tmp_path / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if ini is not None:
        p = tmp_path / ".runtime" / "tmp"
        p.mkdir(parents=True)
        (p / "pytest_min.ini").write_text(ini, encoding="utf-8")
    return tmp_path


def test_aligned_configs_pass(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, _ALIGNED_INI)
    findings, _ = cpc.compare(root)
    assert findings == []


def test_marker_set_drift_detected(tmp_path: Path) -> None:
    ini = _ALIGNED_INI.replace("financial: marks financial calculation tests", "").strip()
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, "[pytest]\nmarkers = slow: marks slow tests\n")
    findings, _ = cpc.compare(root)
    assert any("financial" in f and "pyproject" in f for f in findings)


def test_timeout_drift_detected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, "[pytest]\ntimeout = 60\nmarkers = slow: a; financial: b\n")
    findings, _ = cpc.compare(root)
    assert any("timeout" in f for f in findings)


def test_cache_dir_in_ini_rejected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, _ALIGNED_INI + "\ncache_dir = .runtime/tmp/pytest_cache\n")
    findings, _ = cpc.compare(root)
    assert any("cache_dir" in f for f in findings)


def test_missing_ini_detected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, None)
    findings, _ = cpc.compare(root)
    assert any("pytest_min.ini" in f for f in findings)


def test_main_never_raises_on_garbage(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pyproject.toml").write_text("not [valid toml", encoding="utf-8")
    rc = cpc.main([], repo_root=tmp_path)
    assert rc in (cpc.EXIT_FINDINGS, cpc.EXIT_ERROR)
    assert rc != cpc.EXIT_PASS
