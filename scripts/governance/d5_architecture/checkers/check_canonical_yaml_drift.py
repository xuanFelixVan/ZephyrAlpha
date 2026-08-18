# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_canonical_yaml_drift.py | §canonical-yaml-drift
# [MODULE] scripts.governance.d5_architecture.checkers.check_canonical_yaml_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 5 项断言只读 canonical YAML + pyproject.toml + 文件系统；--ci 模式有 issue 即 exit 1；不修改任何文件
# [MODIFY-GUARD] 5 个 assert_* 函数的断言规则与 stale 子串清单
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 1 (EXIT_FINDINGS) 当 --ci 且有 issue；exit 0 (EXIT_PASS) 当干净或 --warn-only
# [TESTS] tests/governance/scripts_governance/test_check_canonical_yaml_drift.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_canonical_yaml_drift.py — GATE-CANONICAL-YAML-DRIFT

防止 canonical YAML SSoT 漂移回陈旧状态（Phase B 治本，2026-07-24）。

病根：Phase A（commit d747ae3251）修了 13 份 *_principles.md 的 markdown 叙事，但未把修正
同步到对应的 canonical YAML SSoT。这 4 个 YAML 均 [A_config] human_gated——无 reconciler 自动重生，
下一个 AI 可能"修复"回陈旧值。本门禁把 5 项修正固化成自动校验。

5 项断言（A1-A5），每项返回 list[str] issue（空=通过）：
  A1 Python 版本对齐：technology_landscape.yaml T-A03.version == pyproject.toml requires-python
  A2 G0.5 条目存在：technology_landscape.yaml technologies 中 name 含 G0.5 关键字 ≥ 5 条
  A3 路径存在：cross_layer_contracts.yaml acl_landing + technology_landscape.yaml physical_path，
      以 src/ 开头则目录必须存在（frontend/ 等规划前缀放行）
  A4 runtime_plane_tag 路径：runtime_planes.yaml 中 runtime_plane_tag.py 必须用全限定路径
      src/zephyr/shared/contracts/core/runtime_plane_tag.py，且该文件存在
  A5 治理配置路径：governance_systems_registry.yaml 不得含 .cursorignore/.cursorrules，
      且 .trae/rules/ 目录存在

模式：
  --ci (默认): 有 issue → exit 1
  --warn-only: 全部 exit 0 (仅报告)
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import re

import yaml
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

__manifest__ = """
args:
- --ci
- --warn-only
description: GATE-CANONICAL-YAML-DRIFT - 防止 canonical YAML SSoT 漂移回陈旧状态（Phase B 5 项断言）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

# canonical 路径（相对 REPO_ROOT）
TECH_YAML = Path("architecture_model/technology/technology_landscape.yaml")
CONTRACTS_YAML = Path("architecture_model/contracts/cross_layer_contracts.yaml")
RUNTIME_PLANES_YAML = Path("architecture_model/cross_cutting/runtime_planes.yaml")
GOV_REGISTRY_YAML = Path("architecture_model/governance_systems_registry.yaml")
PYPROJECT_TOML = Path("pyproject.toml")

# G0.5 关键字（覆盖 chart_factory.py 的 5 个核心 import）
_G05_KEYWORDS = (
    "Panel", "HoloViz", "HoloViews", "Datashader", "hvPlot",
    "Plotly", "plotly_resampler", "TradingView", "Lightweight",
)

# runtime_plane_tag.py 的全限定真源路径
_RUNTIME_TAG_FULL = "src/zephyr/shared/contracts/core/runtime_plane_tag.py"

# 陈旧治理配置子串
_STALE_GOV_PATTERNS = (".cursorignore", ".cursorrules")


def _load_yaml(path: Path) -> object:
    """安全加载 YAML，返回解析对象（dict/list）。"""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _extract_requires_python(pyproject_path: Path) -> str | None:
    """从 pyproject.toml 提取 requires-python 值（regex，避免 tomllib 依赖）。"""
    if not pyproject_path.exists():
        return None
    text = pyproject_path.read_text(encoding="utf-8")
    m = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', text)
    return m.group(1) if m else None


def assert_a1_python_version(tech_yaml: Path, pyproject: Path) -> list[str]:
    """A1: technology_landscape.yaml T-A03.version == pyproject.toml requires-python。"""
    issues: list[str] = []
    req = _extract_requires_python(pyproject)
    if req is None:
        return [f"A1: 无法从 {pyproject} 提取 requires-python，跳过"]
    data = _load_yaml(tech_yaml)
    techs = data.get("technologies", []) if isinstance(data, dict) else []
    ta03 = next((t for t in techs if isinstance(t, dict) and t.get("id") == "T-A03"), None)
    if ta03 is None:
        return [f"A1: {tech_yaml} 未找到 T-A03 条目"]
    actual = ta03.get("version", "")
    if actual != req:
        issues.append(
            f"A1: T-A03 Python version='{actual}' 与 pyproject.toml requires-python='{req}' 不一致"
        )
    return issues


def assert_a2_g05_presence(tech_yaml: Path) -> list[str]:
    """A2: technology_landscape.yaml 至少 5 条 G0.5 可视化技术条目。"""
    issues: list[str] = []
    data = _load_yaml(tech_yaml)
    techs = data.get("technologies", []) if isinstance(data, dict) else []
    hits = [
        t for t in techs
        if isinstance(t, dict)
        and any(kw.lower() in str(t.get("name", "")).lower() for kw in _G05_KEYWORDS)
    ]
    if len(hits) < 5:
        issues.append(
            f"A2: G0.5 可视化技术条目仅 {len(hits)} 条（需 ≥5），"
            f"关键字 {_G05_KEYWORDS}。真源 src/zephyr/frontend/dashboard/components/chart_factory.py"
        )
    return issues


def _check_src_path_exists(label: str, field: str, value: str, repo_root: Path) -> list[str]:
    """检查单个 src/ 开头路径字段对应目录是否存在。

    只检查目录路径（以 / 结尾）——重命名/迁移类漂移（如 data/connectors/ → data/implementations/）
    表现为目录不存在。.py 文件路径视为 planned codegen 目标，放行（可能尚未生成）。
    非 src/ 前缀（frontend/ 等规划分区）也放行。
    """
    issues: list[str] = []
    if not value or not str(value).startswith("src/"):
        return issues
    if not str(value).endswith("/"):
        return issues  # .py 或无尾斜杠路径：planned codegen 目标，放行
    target = repo_root / str(value)
    if not target.exists():
        issues.append(f"{label}: {field}='{value}' 目录不存在")
    return issues


def assert_a3_path_existence(contracts_yaml: Path, tech_yaml: Path, repo_root: Path) -> list[str]:
    """A3: acl_landing（contracts）+ physical_path（tech）以 src/ 开头则必须存在。"""
    issues: list[str] = []
    cdata = _load_yaml(contracts_yaml)
    exts = cdata.get("external_contracts", []) if isinstance(cdata, dict) else []
    for ctr in exts:
        if not isinstance(ctr, dict):
            continue
        issues += _check_src_path_exists(
            f"A3 {ctr.get('id', '?')}", "acl_landing", ctr.get("acl_landing", ""), repo_root
        )
    tdata = _load_yaml(tech_yaml)
    techs = tdata.get("technologies", []) if isinstance(tdata, dict) else []
    for t in techs:
        if not isinstance(t, dict):
            continue
        issues += _check_src_path_exists(
            f"A3 {t.get('id', '?')}", "physical_path", t.get("physical_path", ""), repo_root
        )
    return issues


def assert_a4_runtime_plane_tag(runtime_planes_yaml: Path, repo_root: Path) -> list[str]:
    """A4: runtime_planes.yaml 中 runtime_plane_tag.py 必须用全限定路径，且文件存在。"""
    issues: list[str] = []
    if not (repo_root / _RUNTIME_TAG_FULL).exists():
        issues.append(f"A4: 真源文件 {_RUNTIME_TAG_FULL} 不存在")
    text = runtime_planes_yaml.read_text(encoding="utf-8")
    # 找所有 runtime_plane_tag.py 引用，检查前缀是否全限定
    for m in re.finditer(r"([\w/.-]*runtime_plane_tag\.py)", text):
        ref = m.group(1)
        if not ref.endswith(_RUNTIME_TAG_FULL):
            issues.append(
                f"A4: runtime_planes.yaml 引用 '{ref}' 非全限定路径，应为 {_RUNTIME_TAG_FULL}"
            )
    return issues


def assert_a5_governance_config(gov_yaml: Path, repo_root: Path) -> list[str]:
    """A5: governance_systems_registry.yaml 不得含 .cursorignore/.cursorrules，且 .trae/rules/ 存在。"""
    issues: list[str] = []
    if not (repo_root / ".trae/rules").is_dir():
        issues.append("A5: .trae/rules/ 目录不存在")
    text = gov_yaml.read_text(encoding="utf-8")
    for pat in _STALE_GOV_PATTERNS:
        if pat in text:
            issues.append(
                f"A5: governance_systems_registry.yaml 含陈旧子串 '{pat}'，应为 .trae/rules/"
            )
    return issues


def run_all(repo_root: Path) -> list[str]:
    """运行全部 5 项断言，返回合并 issue 列表。"""
    issues: list[str] = []
    issues += assert_a1_python_version(repo_root / TECH_YAML, repo_root / PYPROJECT_TOML)
    issues += assert_a2_g05_presence(repo_root / TECH_YAML)
    issues += assert_a3_path_existence(
        repo_root / CONTRACTS_YAML, repo_root / TECH_YAML, repo_root
    )
    issues += assert_a4_runtime_plane_tag(repo_root / RUNTIME_PLANES_YAML, repo_root)
    issues += assert_a5_governance_config(repo_root / GOV_REGISTRY_YAML, repo_root)
    return issues


def main() -> int:
    """Entry point: parse args, run all assertions, return exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="硬阻断模式 (发现 issue exit 1)")
    parser.add_argument("--warn-only", action="store_true", help="仅告警不阻断")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    issues = run_all(REPO_ROOT)
    print(f"[GATE-CANONICAL-YAML-DRIFT] 扫描 5 项断言: issue={len(issues)}")

    if not issues:
        print("OK: 所有 canonical YAML SSoT 断言通过 (无漂移)")
        return EXIT_PASS

    print("FAIL: 发现 canonical YAML SSoT 漂移:")
    for issue in issues:
        print(f"  {issue}")

    print("\n修复方式: 按 issue 提示把 YAML 改回 canonical 真源值（见各自 rationale / 真源指针）。")

    if args.warn_only:
        print("WARN: 跳过 (warn-only 模式)")
        return EXIT_PASS
    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
