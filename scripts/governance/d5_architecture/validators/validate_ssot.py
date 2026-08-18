# [BLUEPRINT] MOD-GOV_SCRIPTS_ARCH
# [MODULE] scripts.governance.d5_architecture.validators.validate_ssot
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] scripts.governance._shared.frontmatter
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_SCRIPTS_ARCH | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SSoT 文件头一致性校验器.

校验 markdown 文件 frontmatter 中的 module_id / layer / status / priority / version
字段的有效性和跨文件一致性。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args: []
description: SSoT 文件头一致性校验器。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]

_VERSION_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?$")
_LEGACY_LAYER_PATTERN = re.compile(r"^L\d")


def _load_valid_document_statuses() -> set[str]:
    """_load_valid_document_statuses implementation."""
    from _shared.yaml_utils import load_vocabulary_values

    return load_vocabulary_values("status_vocabulary.yaml")


VALID_DOCUMENT_STATUSES = _load_valid_document_statuses()


class Contradiction:
    """SSoT 矛盾条目."""

    def __init__(self, severity="", check_id="", description="", files=None, values=None):
        """__init__ implementation."""
        self.severity = severity
        self.check_id = check_id
        self.description = description
        self.files = files or []
        self.values = values or []


class FileMeta:
    """文件元数据."""

    def __init__(self, path=None, rel_path=None, module_id=None, layer=None,
                 status=None, priority=None, version=None):
        """__init__ implementation."""
        self.path = path
        self.rel_path = rel_path
        self.module_id = module_id
        self.layer = layer
        self.status = status
        self.priority = priority
        self.version = version


class ScanReport:
    """扫描报告."""

    def __init__(self, scanned_files=0, parsed_files=0, scan_time=None, contradictions=None):
        """__init__ implementation."""
        self.scanned_files = scanned_files
        self.parsed_files = parsed_files
        self.scan_time = scan_time
        self.contradictions = contradictions if contradictions is not None else []

    @property
    def p0_count(self) -> int:
        """p0_count implementation."""
        return sum(1 for c in self.contradictions if c.severity == "P0")

    @property
    def p1_count(self) -> int:
        """p1_count implementation."""
        return sum(1 for c in self.contradictions if c.severity == "P1")

    @property
    def p2_count(self) -> int:
        """p2_count implementation."""
        return sum(1 for c in self.contradictions if c.severity == "P2")

    @property
    def total_count(self) -> int:
        """total_count implementation."""
        return len(self.contradictions)

    @property
    def has_p0(self) -> bool:
        """has_p0 implementation."""
        return self.p0_count > 0


class SsotValidator:
    """SSoT 校验器."""

    def __init__(self, scan_dir=None, repo_root=None, config=None):
        """__init__ implementation."""
        self.scan_dir = Path(scan_dir) if scan_dir else None
        self.repo_root = Path(repo_root) if repo_root else None
        self.config = config or {}

    def run(self) -> ScanReport:
        """run implementation."""
        if self.scan_dir is None:
            return ScanReport()
        metas: list[FileMeta] = []
        scanned = 0
        parsed = 0
        for md_file in sorted(self.scan_dir.rglob("*.md")):
            scanned += 1
            meta = parse_file(md_file, self.repo_root)
            if meta is not None:
                parsed += 1
                metas.append(meta)
        contradictions: list[Contradiction] = []
        contradictions.extend(check_p0_layer_invalid(metas))
        contradictions.extend(check_p0_duplicate_active_module_id(metas))
        contradictions.extend(check_p1_status_invalid(metas))
        contradictions.extend(check_p1_module_id_layer_conflict(metas))
        contradictions.extend(check_p1_module_id_status_conflict(metas))
        contradictions.extend(check_p2_priority_invalid(metas))
        contradictions.extend(check_p2_version_format(metas))
        return ScanReport(
            scanned_files=scanned,
            parsed_files=parsed,
            contradictions=contradictions,
        )

    def validate(self, path=None):
        """validate implementation."""
        violations = check_ssot_coverage_completeness()
        return ScanReport(
            scanned_files=1,
            parsed_files=1 if not violations else 0,
            contradictions=violations,
        )

    def check_ssot(self, files=None):
        """Check compliance and report findings."""
        return check_ssot_coverage_completeness()


def _get_valid_layers() -> list[str]:
    """_get_valid_layers implementation."""
    from _shared.yaml_utils import load_vocabulary_values

    return sorted(load_vocabulary_values("layer_vocabulary.yaml", strict=False))


def check_p0_layer_invalid(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    valid_layers = set(_get_valid_layers())
    contradictions: list[Contradiction] = []
    for meta in files:
        layer = meta.layer
        if layer is None:
            continue
        if layer in valid_layers:
            continue
        if _LEGACY_LAYER_PATTERN.match(layer):
            continue
        contradictions.append(
            Contradiction(
                "P0", "P0-1", f"无效 layer: {layer}",
                files=[meta.rel_path], values=[layer],
            )
        )
    return contradictions


def check_p0_duplicate_active_module_id(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    by_module: dict[str, list] = {}
    for meta in files:
        if not meta.module_id or not meta.status:
            continue
        if meta.status.lower() != "active":
            continue
        by_module.setdefault(meta.module_id, []).append(meta)
    contradictions: list[Contradiction] = []
    for module_id, group in by_module.items():
        if len(group) < 2:
            continue
        file_list = [m.rel_path for m in group]
        contradictions.append(
            Contradiction(
                "P0", "P0-2", f"module_id {module_id} 重复 Active",
                files=file_list, values=[module_id],
            )
        )
    return contradictions


def check_p1_status_invalid(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    contradictions: list[Contradiction] = []
    for meta in files:
        status = meta.status
        if not status:
            continue
        if status not in VALID_DOCUMENT_STATUSES:
            contradictions.append(
                Contradiction(
                    "P1", "P1-1", f"无效 status: {status}",
                    files=[meta.rel_path], values=[status],
                )
            )
    return contradictions


def check_p1_module_id_layer_conflict(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    by_module: dict[str, list] = {}
    for meta in files:
        if not meta.module_id or not meta.layer:
            continue
        by_module.setdefault(meta.module_id, []).append(meta)
    contradictions: list[Contradiction] = []
    for module_id, group in by_module.items():
        if len(group) < 2:
            continue
        layers = set(m.layer for m in group if m.layer)
        if len(layers) > 1:
            file_list = [m.rel_path for m in group]
            value_list = list(layers)
            contradictions.append(
                Contradiction(
                    "P1", "P1-2", f"module_id {module_id} layer 冲突",
                    files=file_list, values=value_list,
                )
            )
    return contradictions


def check_p1_module_id_status_conflict(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    by_module: dict[str, list] = {}
    for meta in files:
        if not meta.module_id or not meta.status:
            continue
        by_module.setdefault(meta.module_id, []).append(meta)
    contradictions: list[Contradiction] = []
    for module_id, group in by_module.items():
        if len(group) < 2:
            continue
        statuses = [m.status.lower() for m in group if m.status]
        has_active = any(s == "active" for s in statuses)
        has_deprecated = any(s == "deprecated" for s in statuses)
        has_retired = any(s == "retired" for s in statuses)
        if has_active and (has_deprecated or has_retired):
            file_list = [m.rel_path for m in group]
            value_list = [m.status for m in group]
            contradictions.append(
                Contradiction(
                    "P1", "P1-3", f"module_id {module_id} status 冲突",
                    files=file_list, values=value_list,
                )
            )
    return contradictions


def check_p2_priority_invalid(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    contradictions: list[Contradiction] = []
    for meta in files:
        priority = meta.priority
        if not priority:
            continue
        if priority not in VALID_PRIORITIES:
            contradictions.append(
                Contradiction(
                    "P2", "P2-1", f"无效 priority: {priority}",
                    files=[meta.rel_path], values=[priority],
                )
            )
    return contradictions


def check_p2_version_format(files) -> list[Contradiction]:
    """Check compliance and report findings."""
    contradictions: list[Contradiction] = []
    for meta in files:
        version = meta.version
        if not version:
            continue
        v = version.strip("\'\"")
        if v == "N/A":
            continue
        if not _VERSION_PATTERN.match(v):
            contradictions.append(
                Contradiction(
                    "P2", "P2-2", f"无效 version: {version}",
                    files=[meta.rel_path], values=[version],
                )
            )
    return contradictions


def check_p3_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_p4_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_p5_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_p6_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_p7_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_p8_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_p9_placeholder(files):
    """Check compliance and report findings."""
    return []


def check_ssot_coverage_completeness(files=None) -> list[Contradiction]:
    """裁定#207 R3-3: SSoT 覆盖范围一致性校验."""
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

    if dnr_path.exists():
        dnr_data = yaml.safe_load(dnr_path.read_text(encoding="utf-8")) or {}
        for entry in dnr_data.get("entries", []) or []:
            rule_id = entry.get("rule_id", "")
            source_doc = entry.get("source_doc", "")
            doc_path_str = source_doc.split("§")[0].strip() if source_doc else ""
            doc_path = project_root / doc_path_str if doc_path_str else None

            if doc_path and not doc_path.exists():
                violations.append(
                    Contradiction(
                        "P0", "SSOT-COV",
                        f"{rule_id} source_doc 有效性: {source_doc} -> 文件不存在",
                        files=[source_doc], values=[source_doc],
                    )
                )
                continue

            if doc_path_str and "trae_028" in doc_path_str:
                if rule_id and rule_id not in ssot_text:
                    violations.append(
                        Contradiction(
                            "P0", "SSOT-COV",
                            f"{rule_id} SSoT 收录完整性: 未在 conditions 中引用",
                            files=[rule_id], values=[rule_id],
                        )
                    )

    return violations


def parse_file(filepath, root_path=None):
    """解析 markdown 文件 frontmatter，返回 FileMeta 或 None."""
    from scripts.governance._shared.frontmatter import parse_frontmatter_from_file

    fp = Path(filepath)
    if not fp.exists():
        return None
    fm = parse_frontmatter_from_file(fp)
    if fm is None:
        return None
    if root_path:
        try:
            rel = fp.relative_to(root_path)
            rel_path = str(rel).replace("\\", "/")
        except (ValueError, TypeError):
            rel_path = str(fp)
    else:
        rel_path = str(fp)
    return FileMeta(
        path=fp,
        rel_path=rel_path,
        module_id=fm.get("module_id"),
        layer=fm.get("layer"),
        status=fm.get("status"),
        priority=fm.get("priority"),
        version=fm.get("version"),
    )


def render_report(report, format="text") -> str:
    """渲染扫描报告."""
    if format == "json":
        import json
        return json.dumps(
            {
                "scanned_files": report.scanned_files,
                "parsed_files": report.parsed_files,
                "p0_count": report.p0_count,
                "p1_count": report.p1_count,
                "p2_count": report.p2_count,
                "total_count": report.total_count,
                "contradictions": [
                    {
                        "severity": c.severity,
                        "check_id": c.check_id,
                        "description": c.description,
                        "files": c.files,
                        "values": c.values,
                    }
                    for c in report.contradictions
                ],
            },
            default=str,
            ensure_ascii=False,
        )
    lines = [
        "---",
        "type: generated",
        "ttl: 7d",
        "---",
        "",
        "# SSoT 扫描报告",
        f"- 扫描文件: {report.scanned_files}",
        f"- 解析文件: {report.parsed_files}",
        f"- P0: {report.p0_count}",
        f"- P1: {report.p1_count}",
        f"- P2: {report.p2_count}",
        f"- 总计: {report.total_count}",
        "",
    ]
    if not report.contradictions:
        lines.append("无矛盾")
    else:
        for c in report.contradictions:
            lines.append(f"## {c.severity}: {c.check_id}")
            lines.append(c.description)
            if c.files:
                lines.append(f"文件: {', '.join(c.files)}")
            if c.values:
                lines.append(f"值: {', '.join(str(v) for v in c.values)}")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="SSoT 完整性校验（裁定#207 R3-3）")
    parser.add_argument("--ci", action="store_true", help="CI 硬阻断模式（默认即硬阻断，与 governance.yml --ci 对齐）")
    parser.add_argument("--scan", action="store_true", help="运行 SSoT 覆盖范围一致性校验（--ci 兼容别名）")
    args = parser.parse_args()

    violations = check_ssot_coverage_completeness()
    if violations:
        print(f"[FAIL] SSoT 覆盖范围一致性校验发现 {len(violations)} 个问题:")
        for v in violations:
            print(f"  - [{v.severity}] {v.check_id}: {v.description}")
        return EXIT_FINDINGS
    print("[PASS] SSoT 覆盖范围一致性校验通过")
    return EXIT_PASS
if __name__ == "__main__":
    raise SystemExit(main())
