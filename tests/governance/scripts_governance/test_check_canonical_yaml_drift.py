# [BLUEPRINT] MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | tests/governance/scripts_governance/test_check_canonical_yaml_drift.py | §gate-canonical-yaml-drift-tests
# [MODULE] tests.governance.scripts_governance.test_check_canonical_yaml_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.check_canonical_yaml_drift
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——全部用 tmp_path 合成 YAML，不读真实仓库；A3/A4/A5 用 tmp_path 作 repo_root
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_check_canonical_yaml_drift.py — GATE-CANONICAL-YAML-DRIFT 单元测试（Phase B，2026-07-24）

覆盖 5 项断言（A1-A5）的核心场景，每项测 clean（通过）+ stale（检出）两路：
  A1 Python 版本对齐 / 不一致
  A2 G0.5 条目存在 / 缺失
  A3 src/ 目录存在 / 不存在 / .py 与 frontend 放行
  A4 runtime_plane_tag 全限定 / 陈旧路径 / 真源文件缺失
  A5 .trae/rules 存在且无 .cursor / 含 .cursorrules / .trae 目录缺失
  run_all 集成：合成干净 repo → 0 issue

测试隔离：全部用 tmp_path 合成 YAML，不读真实仓库文件。
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_CHECKER_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d5_architecture" / "checkers"
if str(_CHECKER_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECKER_DIR))

import check_canonical_yaml_drift as g  # noqa: E402
import yaml  # noqa: E402


def _dump(path: Path, data: object) -> None:
    """mkdir parents + 写 YAML（避免文件句柄泄漏）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")


def _write_tech_yaml(
    path: Path,
    ta03_version: str = ">=3.12",
    g05_count: int = 5,
    tb03_physical: str = "src/zephyr/data/implementations/",
) -> None:
    """合成 technology_landscape.yaml。"""
    techs = [
        {
            "id": "T-A03",
            "name": "Python / 主语言",
            "quadrant": "adopt",
            "category": "language",
            "version": ta03_version,
        },
    ]
    g05_names = [
        "Panel",
        "HoloViz",
        "Plotly",
        "plotly_resampler",
        "TradingView Lightweight Charts",
        "HoloViews",
        "Datashader",
    ]
    for i in range(g05_count):
        techs.append(
            {
                "id": f"T-A1{i + 3}",
                "name": g05_names[i % len(g05_names)],
                "quadrant": "adopt",
                "category": "g0.5-visualization",
            }
        )
    techs.append(
        {
            "id": "T-B03",
            "name": "Vendor Registry",
            "quadrant": "build",
            "category": "core-engine",
            "physical_path": tb03_physical,
        }
    )
    _dump(path, {"technologies": techs})


def _write_pyproject(path: Path, req: str = ">=3.12") -> None:
    path.write_text(f'requires-python = "{req}"\n', encoding="utf-8")


# ─── A1 ───
def test_a1_python_version_match(tmp_path):
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech, ta03_version=">=3.12")
    pp = tmp_path / "pyproject.toml"
    _write_pyproject(pp, ">=3.12")
    assert g.assert_a1_python_version(tech, pp) == []


def test_a1_python_version_mismatch(tmp_path):
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech, ta03_version=">=3.11")
    pp = tmp_path / "pyproject.toml"
    _write_pyproject(pp, ">=3.12")
    issues = g.assert_a1_python_version(tech, pp)
    assert len(issues) == 1 and ">=3.11" in issues[0] and ">=3.12" in issues[0]


# ─── A2 ───
def test_a2_g05_present(tmp_path):
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech, g05_count=5)
    assert g.assert_a2_g05_presence(tech) == []


def test_a2_g05_absent(tmp_path):
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech, g05_count=0)
    issues = g.assert_a2_g05_presence(tech)
    assert len(issues) == 1 and "G0.5" in issues[0]


# ─── A3 ───
def test_a3_path_exists(tmp_path):
    (tmp_path / "src/zephyr/data/implementations").mkdir(parents=True)
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech)
    _dump(
        tmp_path / "c.yaml",
        {
            "external_contracts": [
                {"id": "EXT-002", "acl_landing": "src/zephyr/data/implementations/"},
            ]
        },
    )
    assert g.assert_a3_path_existence(tmp_path / "c.yaml", tech, tmp_path) == []


def test_a3_path_missing(tmp_path):
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech, tb03_physical="src/zephyr/data/connectors/")
    _dump(
        tmp_path / "c.yaml",
        {
            "external_contracts": [
                {"id": "EXT-002", "acl_landing": "src/zephyr/data/connectors/"},
            ]
        },
    )
    issues = g.assert_a3_path_existence(tmp_path / "c.yaml", tech, tmp_path)
    assert len(issues) == 2 and all("data/connectors/" in i for i in issues)


def test_a3_skips_py_and_frontend(tmp_path):
    tech = tmp_path / "tech.yaml"
    _write_tech_yaml(tech, tb03_physical="src/zephyr/planned.py")
    _dump(
        tmp_path / "c.yaml",
        {
            "external_contracts": [
                {"id": "EXT-003", "acl_landing": "frontend/"},
                {"id": "EXT-005", "acl_landing": "src/zephyr/not_built.py"},
            ]
        },
    )
    assert g.assert_a3_path_existence(tmp_path / "c.yaml", tech, tmp_path) == []


# ─── A4 ───
def test_a4_full_path(tmp_path):
    (tmp_path / g._RUNTIME_TAG_FULL).mkdir(parents=True)
    (tmp_path / g._RUNTIME_TAG_FULL).touch()
    rp = tmp_path / "rp.yaml"
    rp.write_text(f"submodule: {g._RUNTIME_TAG_FULL}\n", encoding="utf-8")
    assert g.assert_a4_runtime_plane_tag(rp, tmp_path) == []


def test_a4_stale_path(tmp_path):
    (tmp_path / g._RUNTIME_TAG_FULL).mkdir(parents=True)
    (tmp_path / g._RUNTIME_TAG_FULL).touch()
    rp = tmp_path / "rp.yaml"
    rp.write_text("note: 跨层契约（除 shared/contracts/runtime_plane_tag.py 外）\n", encoding="utf-8")
    issues = g.assert_a4_runtime_plane_tag(rp, tmp_path)
    assert len(issues) == 1 and "非全限定" in issues[0]


def test_a4_missing_file(tmp_path):
    rp = tmp_path / "rp.yaml"
    rp.write_text(f"submodule: {g._RUNTIME_TAG_FULL}\n", encoding="utf-8")
    issues = g.assert_a4_runtime_plane_tag(rp, tmp_path)
    assert any("不存在" in i for i in issues)


# ─── A5 ───
def test_a5_clean(tmp_path):
    (tmp_path / ".trae/rules").mkdir(parents=True)
    gov = tmp_path / "gov.yaml"
    gov.write_text("note: .trae/rules/\n", encoding="utf-8")
    assert g.assert_a5_governance_config(gov, tmp_path) == []


def test_a5_stale_cursor(tmp_path):
    (tmp_path / ".trae/rules").mkdir(parents=True)
    gov = tmp_path / "gov.yaml"
    gov.write_text('location: ".cursorrules"\n', encoding="utf-8")
    issues = g.assert_a5_governance_config(gov, tmp_path)
    assert len(issues) == 1 and ".cursorrules" in issues[0]


def test_a5_missing_trae_dir(tmp_path):
    gov = tmp_path / "gov.yaml"
    gov.write_text("note: ok\n", encoding="utf-8")
    issues = g.assert_a5_governance_config(gov, tmp_path)
    assert any(".trae/rules" in i for i in issues)


# ─── 集成 ───
def test_run_all_clean_synthetic_repo(tmp_path, monkeypatch):
    """合成干净 repo，run_all 应返回 0 issue。"""
    (tmp_path / g._RUNTIME_TAG_FULL).mkdir(parents=True)
    (tmp_path / g._RUNTIME_TAG_FULL).touch()
    (tmp_path / "src/zephyr/data/implementations").mkdir(parents=True)
    (tmp_path / ".trae/rules").mkdir(parents=True)
    _write_tech_yaml(tmp_path / g.TECH_YAML)
    _write_pyproject(tmp_path / g.PYPROJECT_TOML)
    _dump(
        tmp_path / g.CONTRACTS_YAML,
        {
            "external_contracts": [
                {"id": "EXT-002", "acl_landing": "src/zephyr/data/implementations/"},
            ]
        },
    )
    (tmp_path / g.RUNTIME_PLANES_YAML).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / g.RUNTIME_PLANES_YAML).write_text(f"submodule: {g._RUNTIME_TAG_FULL}\n", encoding="utf-8")
    (tmp_path / g.GOV_REGISTRY_YAML).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / g.GOV_REGISTRY_YAML).write_text("note: .trae/rules/\n", encoding="utf-8")
    monkeypatch.setattr(g, "REPO_ROOT", tmp_path)
    assert g.run_all(tmp_path) == []
