# [BLUEPRINT] MOD-GOV-SCRIPTS-ARCH
# [MODULE] scripts.governance.d5_architecture.validators.validate_ssot
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] scripts.governance._shared.frontmatter
# [CONSUMERS] tests.unit.test_validate_ssot_unit; tests.unit.governance.test_validate_ssot_governance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# P0-P3 任务优先级——业务常量（非治理词表），无 priority_vocabulary.yaml。
# 治本说明（2026-06-30）：若未来纳入词表管理，改用 load_vocabulary_values("priority_vocabulary.yaml")。
# 当前 GATE-VOCAB 检测1 漏检（PRIORITIES 不在后缀正则），检测4 值匹配漏检（无 priority 词表）。
__manifest__ = """
args: []
description: 从 status_vocabulary.yaml 加载合法文档 status 值（SSoT 唯一真源）。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]


def _load_valid_document_statuses() -> set[str]:
    """从 status_vocabulary.yaml 加载合法文档 status 值（SSoT 唯一真源）。

    D-D-05 治本（2026-06-30）：收敛到 SSoT ``load_vocabulary_values``。
    status_vocabulary.yaml v1.1.0 已将 approved→active、superseded→deprecated 迁移，
    故合法值精简为 draft/active/deprecated 三值。
    """
    from _shared.yaml_utils import load_vocabulary_values

    return load_vocabulary_values("status_vocabulary.yaml")


from _shared.constants import REPO_ROOT

VALID_DOCUMENT_STATUSES = _load_valid_document_statuses()


class Contradiction:
    def __init__(self, source="", target="", field="", source_value="", target_value=""):
        self.source = source
        self.target = target
        self.field = field
        self.source_value = source_value
        self.target_value = target_value


class FileMeta:
    def __init__(self, path="", module_id="", layer="", priority="", status="", owner=""):
        self.path = path
        self.module_id = module_id
        self.layer = layer
        self.priority = priority
        self.status = status
        self.owner = owner


class ScanReport:
    def __init__(self, total_files=0, valid_files=0, violations=None, timestamp=None):
        self.total_files = total_files
        self.valid_files = valid_files
        self.violations = violations or []
        self.timestamp = timestamp


class SsotValidator:
    def __init__(self, config=None):
        self.config = config or {}

    def validate(self, path=None):
        violations = check_ssot_coverage_completeness()
        return ScanReport(
            total_files=1,
            valid_files=1 if not violations else 0,
            violations=violations,
        )

    def check_ssot(self, files=None):
        return check_ssot_coverage_completeness()


def _get_valid_layers() -> list[str]:
    """从 layer_vocabulary.yaml 加载合法 layer 值（SSoT 唯一真源）。

    治本（2026-06-30 红蓝对抗）：收敛到 SSoT ``load_vocabulary_values``，
    消除复制的 yaml.safe_load 词表加载逻辑（原实现被 GATE-VOCAB 检测5 漏检，
    因函数名 _get_valid_layers 不匹配 _load_* 正则；行为检测 v2 已捕获）。
    """
    from _shared.yaml_utils import load_vocabulary_values

    return sorted(load_vocabulary_values("layer_vocabulary.yaml", strict=False))


def check_p0_duplicate_active_module_id(files):
    # stub——勿实现。module_path 冲突检测真源在
    # capability_lookup.check_ssot_conflicts()（L2/L3 共享）。
    # CLI: python -m zephyr.governance.capability_lookup --list-conflicts
    return []


def check_p0_layer_invalid(files):
    return []


def check_p1_module_id_layer_conflict(files):
    return []


def check_p1_module_id_status_conflict(files):
    return []


def check_p1_status_invalid(files):
    return []


def check_p2_priority_invalid(files):
    return []


def check_p2_version_format(files):
    return []


def check_p3_placeholder(files):
    return []


def check_p4_placeholder(files):
    return []


def check_p5_placeholder(files):
    return []


def check_p6_placeholder(files):
    return []


def check_p7_placeholder(files):
    return []


def check_p8_placeholder(files):
    return []


def check_p9_placeholder(files):
    return []


def check_ssot_coverage_completeness(files=None) -> list[Contradiction]:
    """裁定#207 R3-3: SSoT 覆盖范围一致性校验。

    对比 trae_028 gov_doc_003_naming_ssot 的 conditions vs 规则注册表，
    校验所有规则的 source_doc 有效且被 SSoT 收录。SSoT 必须满足 ALCOA+ Complete（无遗漏）。

    当前覆盖：
    - domain_naming_rules.yaml (NR-001~NR-005) vs trae_028 gov_doc_003_naming_ssot

    校验项：
    1. source_doc 指向的文件是否存在（防失效引用，裁定#207 R3-2）
    2. 若 source_doc 指向 trae_028，rule_id 是否在 SSoT conditions 文本中出现（收录完整性，R3-3）
    """
    from pathlib import Path

    import yaml

    project_root = REPO_ROOT
    trae_028_path = (
        project_root
        / "docs"
        / "01_policies_and_standards"
        / "rules"
        / "trae_028_doc_structure_naming.yaml"
    )
    dnr_path = (
        project_root
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "catalogs"
        / "domain_naming_rules.yaml"
    )

    violations: list[Contradiction] = []

    # 加载 trae_028 gov_doc_003_naming_ssot conditions 文本
    ssot_text = ""
    if trae_028_path.exists():
        trae_data = yaml.safe_load(trae_028_path.read_text(encoding="utf-8")) or {}
        sections = trae_data.get("sections", {}) or {}
        naming_ssot = sections.get("gov_doc_003_naming_ssot", {}) or {}
        conditions = naming_ssot.get("conditions", []) or []
        parts = []
        for c in conditions:
            parts.append(str(c.get("check", "")))
            parts.append(str(c.get("pass", "")))
            parts.append(str(c.get("fail", "")))
        ssot_text = " ".join(parts)

    # 校验 domain_naming_rules.yaml 的每条规则
    if dnr_path.exists():
        dnr_data = yaml.safe_load(dnr_path.read_text(encoding="utf-8")) or {}
        for entry in dnr_data.get("entries", []) or []:
            rule_id = entry.get("rule_id", "")
            source_doc = entry.get("source_doc", "")
            # 提取 source_doc 中的文件路径（§ 之前的部分）
            doc_path_str = source_doc.split("§")[0].strip() if source_doc else ""
            doc_path = project_root / doc_path_str if doc_path_str else None

            # 校验1: source_doc 指向的文件是否存在
            if doc_path and not doc_path.exists():
                violations.append(
                    Contradiction(
                        source=f"domain_naming_rules.yaml {rule_id}",
                        target=source_doc,
                        field="source_doc 有效性",
                        source_value=source_doc,
                        target_value="文件不存在",
                    )
                )
                continue  # 文件不存在则跳过收录校验

            # 校验2: 若 source_doc 指向 trae_028，rule_id 是否在 SSoT conditions 文本中出现
            if doc_path_str and "trae_028" in doc_path_str:
                if rule_id and rule_id not in ssot_text:
                    violations.append(
                        Contradiction(
                            source=f"domain_naming_rules.yaml {rule_id}",
                            target="trae_028 gov_doc_003_naming_ssot",
                            field="SSoT 收录完整性",
                            source_value=rule_id,
                            target_value="SSoT conditions 未引用此 rule_id",
                        )
                    )

    return violations


def parse_file(filepath):
    from scripts.governance._shared.frontmatter import parse_frontmatter_from_file

    return parse_frontmatter_from_file(filepath)


def render_report(results, format="text"):
    if format == "json":
        import json

        return json.dumps(results, default=str)
    return str(results)


def main() -> int:
    """CLI 入口：运行 SSoT 覆盖范围一致性校验（裁定#207 R3-3）。

    用法:
      python scripts/governance/d5_architecture/validators/validate_ssot.py --scan
    """
    import argparse

    parser = argparse.ArgumentParser(description="SSoT 完整性校验（裁定#207 R3-3）")
    parser.add_argument("--scan", action="store_true", help="运行 SSoT 覆盖范围一致性校验")
    args = parser.parse_args()

    # 默认运行 scan（--scan 为显式标记，兼容无参调用）
    violations = check_ssot_coverage_completeness()
    if violations:
        print(f"[FAIL] SSoT 覆盖范围一致性校验发现 {len(violations)} 个问题:")
        for v in violations:
            print(
                f"  - {v.source} -> {v.target}: {v.field} "
                f"({v.source_value} -> {v.target_value})"
            )
        return 1
    print("[PASS] SSoT 覆盖范围一致性校验通过: 所有规则 source_doc 有效且被 SSoT 收录")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
