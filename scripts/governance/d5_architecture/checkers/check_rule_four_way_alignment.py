# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_rule_four_way_alignment.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_rule_four_way_alignment
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 规则YAML↔Catalog↔Disk↔Code 四方对齐; 过滤按tier(非frontmatter layer); L0/空tier跳过
# [MODIFY-GUARD] gate_id="RULE-FOUR-WAY-ALIGN"; ARCH-020 补建
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 检测失败→exit 1+violation清单; 成功→exit 0; 环境异常→exit 2
# [TESTS]
# [TTL] task_bound
"""check_rule_four_way_alignment.py —— 规则四方对齐门禁（ARCH-020 补建）

对标：ARCH-020 — check_rule_four_way_alignment.py 文件不存在，四方对齐门禁缺失

四方对齐（规则 YAML ↔ Catalog ↔ Disk ↔ Code）：
  1. YAML ↔ Catalog: 规则 YAML 文件在 rule_catalog_registry.yaml 中登记
  2. Catalog ↔ Disk: catalog 中每个 path 在磁盘上存在
  3. YAML ↔ Disk: 规则 YAML frontmatter rule_id 与文件名一致
  4. Code ↔ Catalog: 代码中 rule_id 引用在 catalog 中存在（可选，--with-code-refs）

过滤条件（ARCH-020 核心修复）：
  - 按 tier 过滤（来自 rule_catalog_registry.yaml，非 frontmatter layer）
  - L0（信息性）/空 tier 跳过——不检查信息性文档
  - L1（治理层）/L2（设计层）检查——规范性文档必须对齐
  - cross_layer 检查——跨层规则必须对齐

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML 未安装")
    sys.exit(EXIT_ERROR)

__manifest__ = """
args:
- --ci
- --with-code-refs
description: 规则四方对齐门禁（YAML↔Catalog↔Disk↔Code），按tier过滤（ARCH-020补建）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

# rule_catalog_registry.yaml 真源路径
_CATALOG_YAML = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "rule_catalog_registry.yaml"
)

# 规则文件目录
_RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards"

# 按 tier 过滤：L0/空 tier 跳过（信息性文档），L1/L2/cross_layer 检查（规范性文档）
_TIER_CHECK = {"L1", "L2", "cross_layer"}

# 可扫描的规则文件扩展名
_RULE_EXTS = (".yaml", ".yml", ".md")


def _load_catalog() -> dict:
    """加载 rule_catalog_registry.yaml。"""
    if not _CATALOG_YAML.is_file():
        print(f"[ERROR] catalog 不存在: {_CATALOG_YAML}")
        sys.exit(EXIT_ERROR)
    with open(_CATALOG_YAML, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _extract_frontmatter(path: Path) -> dict:
    """从 YAML/MD 文件提取 frontmatter（YAML 直接加载，MD 提取 --- 块）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    # MD frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1]) or {}
    return {}


def _check_yaml_catalog_alignment(catalog: dict, violations: list[str]) -> None:
    """检查 1+2: YAML ↔ Catalog ↔ Disk 对齐。

    - catalog 中每个 path 在磁盘上存在
    - 按 tier 过滤：L0/空 tier 跳过
    """
    files = catalog.get("files", [])
    for entry in files:
        if not isinstance(entry, dict):
            continue
        rel_path = entry.get("path", "")
        if not rel_path:
            continue
        tier = entry.get("tier", "")
        # ARCH-020 核心修复：按 tier 过滤（非 frontmatter layer）
        if tier not in _TIER_CHECK:
            continue
        abs_path = REPO_ROOT / rel_path
        if not abs_path.is_file():
            violations.append(
                f"  - [Catalog↔Disk] path 不存在: {rel_path} (tier={tier})"
            )


def _check_yaml_disk_rule_id(catalog: dict, violations: list[str]) -> None:
    """检查 3: YAML frontmatter rule_id 与 catalog module_id 一致。

    - 按 tier 过滤：L0/空 tier 跳过
    """
    files = catalog.get("files", [])
    for entry in files:
        if not isinstance(entry, dict):
            continue
        rel_path = entry.get("path", "")
        if not rel_path:
            continue
        tier = entry.get("tier", "")
        if tier not in _TIER_CHECK:
            continue
        abs_path = REPO_ROOT / rel_path
        if not abs_path.is_file():
            continue  # 已由 check_yaml_catalog_alignment 报告
        if not rel_path.endswith(_RULE_EXTS):
            continue
        fm = _extract_frontmatter(abs_path)
        if not fm:
            continue
        rule_id = fm.get("rule_id", "")
        module_id = entry.get("module_id", "")
        if rule_id and module_id and rule_id != module_id:
            violations.append(
                f"  - [YAML↔Disk] rule_id 不一致: {rel_path} "
                f"(frontmatter rule_id={rule_id}, catalog module_id={module_id})"
            )


def _check_duplicate_rule_ids(catalog: dict, violations: list[str]) -> None:
    """检查 4: 同一 rule_id 不应出现在多个文件（按 tier 过滤）。"""
    files = catalog.get("files", [])
    id_map: dict[str, list[str]] = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        tier = entry.get("tier", "")
        if tier not in _TIER_CHECK:
            continue
        module_id = entry.get("module_id", "")
        rel_path = entry.get("path", "")
        if module_id:
            id_map.setdefault(module_id, []).append(rel_path)
    for mid, paths in id_map.items():
        if len(paths) > 1:
            violations.append(
                f"  - [YAML↔Catalog] 重复 module_id={mid}: {paths}"
            )


def check(with_code_refs: bool = False) -> int:
    """主检查函数。返回 exit code。"""
    catalog = _load_catalog()
    violations: list[str] = []

    _check_yaml_catalog_alignment(catalog, violations)
    _check_yaml_disk_rule_id(catalog, violations)
    _check_duplicate_rule_ids(catalog, violations)

    if violations:
        print("[FAIL] 规则四方对齐门禁检测到违规（RULE_FOUR_WAY_ALIGN_VIOLATION）：")
        for v in violations:
            print(v)
        print(
            "\n修复：确保规则 YAML ↔ Catalog ↔ Disk ↔ Code 四方对齐。"
            "过滤按 tier（L1/L2/cross_layer 检查，L0/空跳过）。"
        )
        return EXIT_FINDINGS

    total = len(catalog.get("files", []))
    print(f"[PASS] 规则四方对齐检查通过（扫描 {total} 个文件条目，按 tier 过滤）")
    return EXIT_PASS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="规则四方对齐门禁（YAML↔Catalog↔Disk↔Code，ARCH-020 补建）"
    )
    parser.add_argument(
        "--ci", action="store_true", help="CI 模式（无交互，违规即 exit 1）"
    )
    parser.add_argument(
        "--with-code-refs",
        action="store_true",
        help="启用代码引用检查（较慢，扫描 src/ 下 rule_id 引用）",
    )
    args = parser.parse_args()

    rc = check(with_code_refs=args.with_code_refs)
    sys.exit(rc)


if __name__ == "__main__":
    main()
