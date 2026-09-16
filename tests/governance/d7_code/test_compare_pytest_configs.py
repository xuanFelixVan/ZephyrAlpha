# [BLUEPRINT] MOD-GOV_CHECK_ALGO_FLOW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [A_module] module_id=MOD-GOV_CHECK_ALGO_FLOW | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""compare_pytest_configs 行为锚点测试（2026-09-15 外审遗留②配套）。

覆盖：对齐通过 / markers 漂移检出 / 单行分号 markers（pytest linelist 只注册第一个，
历史失效写法）检出 / timeout 漂移检出 / cache_dir 禁入检出 / ini 缺失检出
（精简跑法寄居根目录既有纳管件 py.ini 的 [pytest] 段，裁定#275→#278：
DCR-005 禁 config/*.ini，独立件需 .gitignore 放行=撞 PROTECTED-PATHS Owner 闸）/
误段名 [tool:pytest] 检出（.ini 中该段被 pytest 整体忽略=configfile 照打而零配置，
2026-09-16 移植当日探针实证）/ addopts 缺 --strict-markers 检出 / 非法 TOML 降级 exit 2。
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
markers =
    slow: marks slow tests
    financial: marks financial calculation tests
"""


def _make_repo(tmp_path: Path, pyproject: str, ini: str | None) -> Path:
    (tmp_path / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if ini is not None:
        (tmp_path / "py.ini").write_text(ini, encoding="utf-8")
    return tmp_path


def test_aligned_configs_pass(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, _ALIGNED_INI)
    findings, _ = cpc.compare(root)
    assert findings == []


def test_marker_set_drift_detected(tmp_path: Path) -> None:
    ini = _ALIGNED_INI.replace("    financial: marks financial calculation tests\n", "")
    assert "financial" not in ini  # 前置自证：确已删掉该 marker 行
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, _ = cpc.compare(root)
    assert any("financial" in f and "pyproject" in f for f in findings)


def test_ini_single_line_semicolon_markers_detected(tmp_path: Path) -> None:
    """历史失效写法钉扎：pytest markers 是 linelist，单行分号只注册第一个→必判漂移。"""
    ini = (
        "[pytest]\naddopts = -q --strict-markers\ntimeout = 120\n"
        "markers = slow: marks slow tests; financial: marks financial calculation tests\n"
    )
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, detail = cpc.compare(root)
    assert detail["markers_ini"] == ["slow"]
    assert any("financial" in f and "pyproject" in f for f in findings)


def test_timeout_drift_detected(tmp_path: Path) -> None:
    ini = _ALIGNED_INI.replace("timeout = 120", "timeout = 60")
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, _ = cpc.compare(root)
    assert any("timeout" in f for f in findings)
    # markers 集合同值→timeout 是唯一漂移源（防空断言：另一类漂移不得混进来）
    assert len(findings) == 1


def test_cache_dir_in_ini_rejected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, _ALIGNED_INI + "\ncache_dir = .runtime/tmp/pytest_cache\n")
    findings, _ = cpc.compare(root)
    assert any("cache_dir" in f for f in findings)


def test_missing_ini_detected(tmp_path: Path) -> None:
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, None)
    findings, _ = cpc.compare(root)
    hit = [f for f in findings if "py.ini 缺失" in f]
    assert hit, findings
    assert not any("pytest_min.ini" in f for f in hit), hit


def test_inert_tool_pytest_section_detected(tmp_path: Path) -> None:
    """钉扎 2026-09-16 实测缺陷：.ini 里写 [tool:pytest] 被 pytest 整体忽略。

    pytest 按后缀分支——.ini 只读 [pytest]，[tool:pytest] 仅 .cfg 生效。误段名时
    pytest 仍打印 `configfile: py.ini`，但 markers/--strict-markers/timeout/
    norecursedirs 全部零生效："看着有配置、实则无任何配置"的静默放宽，
    必须判漂移（否则精简跑法比缺失更危险——缺失至少会报，误段名什么都不报）。
    """
    ini = _ALIGNED_INI.replace("[pytest]", "[tool:pytest]")
    assert "[pytest]" not in ini
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, detail = cpc.compare(root)
    assert detail["ini_section"] == "tool:pytest"
    assert any("[tool:pytest]" in f for f in findings), findings
    # 早退语义：段无效时不再叠加 markers/timeout 比对噪声
    assert len(findings) == 1, findings


def test_ini_without_strict_markers_detected(tmp_path: Path) -> None:
    """精简跑法丢 --strict-markers = A 类漂移不可见（收窄语义被悄悄放宽）。"""
    ini = _ALIGNED_INI.replace("addopts = -q --strict-markers", "addopts = -q")
    root = _make_repo(tmp_path, _ALIGNED_PYPROJECT, ini)
    findings, detail = cpc.compare(root)
    assert detail["strict_markers_in_ini"] is False
    assert any("strict-markers" in f for f in findings), findings


def test_repo_py_ini_actually_aligned() -> None:
    """真仓 py.ini vs pyproject 必须零漂移（防"测试全用 tmp fixture、真配置烂了没人知道"）。"""
    root = Path(__file__).resolve().parents[3]
    if not (root / "py.ini").is_file():
        pytest.skip("py.ini 缺失=检出破损（根目录既有纳管件）")
    findings, detail = cpc.compare(root)
    assert findings == [], findings
    assert "slow" in detail["markers_ini"] and detail["ini_section"] == "pytest"


def test_main_never_raises_on_garbage(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "pyproject.toml").write_text("not [valid toml", encoding="utf-8")
    rc = cpc.main([], repo_root=tmp_path)
    assert rc in (cpc.EXIT_FINDINGS, cpc.EXIT_ERROR)
    assert rc != cpc.EXIT_PASS
