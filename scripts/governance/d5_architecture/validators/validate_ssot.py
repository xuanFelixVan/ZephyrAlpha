"""SSoT 矛盾扫描器 (SSoT Contradiction Validator)
任务 ID : T-2-33
safety_level : M（治理脚本）

功能
----
主动扫描 docs/ 目录下所有 Markdown 文件的 YAML frontmatter，
检测跨文件的受保护字段矛盾，生成 Markdown 报告。

检查项（按严重性）
-----------------
P0-1  layer 字段值不在有效集合中（L00-L13 / cross_layer）
P0-2  同一 module_id 同时存在于多个 Active 状态文件（重复真源）
P0-3  [--ci 附加] docs/09_audit/findings/index.md、docs/09_audit/index.md 中对 findings/
      的引用、architecture-model/SCOPE.yaml 落点（双树口径）
P1-1  status 字段值不在有效集合中
P1-2  同一 module_id 在多文件中 layer 字段不一致
P1-3  同一 module_id 在多文件中 status 字段矛盾（一Active一Deprecated）
P2-1  priority 字段值不在有效集合中
P2-2  version 字段格式不符合 MAJOR.MINOR.PATCH

相关路径（门禁引用，非 frontmatter 扫描）
---------------------------------------
- 层合法值：docs/02_enterprise_architecture/ssot-authority-map.md §一 valid_values
- 双树：architecture-model/SCOPE.yaml
- Finding 落盘：docs/09_audit/findings/index.md

用法
----
正常扫描（生成报告）：
    python scripts/governance/d5_architecture/validate_ssot.py

CI 模式（P0 或导航检查失败时 exit(1)）：
    python scripts/governance/d5_architecture/validate_ssot.py --ci

指定扫描目录：
    python scripts/governance/d5_architecture/validate_ssot.py --scan-dir docs/02_enterprise_architecture

指定报告输出路径：
    python scripts/governance/d5_architecture/validate_ssot.py --report docs/09_audit/reports/ssot-validation-LATEST.md
"""

from __future__ import annotations

import os

__manifest__ = """
args: []
description: SSoT单一真源一致性校验
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT, EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter

ensure_utf8_stdout()
from dataclasses import dataclass, field
from datetime import datetime

DEFAULT_SCAN_DIR = REPO_ROOT / "docs"
DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "09_audit" / "reports" / "ssot-validation-LATEST.md"
AUTHORITY_MAP_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "ssot-authority-map.md"
SCOPE_YAML_PATH = REPO_ROOT / "architecture-model" / "SCOPE.yaml"
AUDIT_FINDINGS_INDEX_MD = REPO_ROOT / "docs" / "09_audit" / "findings" / "index.md"
AUDIT_CONTROL_INDEX_MD = REPO_ROOT / "docs" / "09_audit" / "INDEX.md"


def check_audit_navigation_wiring(repo_root: Path = REPO_ROOT) -> list[str]:
    """CI：审计 Finding 导航 + 双树 SCOPE 物理落点。"""
    errs: list[str] = []
    if not SCOPE_YAML_PATH.exists():
        errs.append(f"缺失 {SCOPE_YAML_PATH.relative_to(repo_root)}（architecture-model 双树边界真源）")
    if not AUDIT_FINDINGS_INDEX_MD.exists():
        errs.append(f"缺失 {AUDIT_FINDINGS_INDEX_MD.relative_to(repo_root)}（安全 Finding Markdown 入口）")
    if AUDIT_CONTROL_INDEX_MD.exists():
        txt = AUDIT_CONTROL_INDEX_MD.read_text(encoding="utf-8", errors="replace")
        if "findings/" not in txt and "findings/index" not in txt:
            errs.append(f"{AUDIT_CONTROL_INDEX_MD.relative_to(repo_root)} 未引用 findings/（导航断裂）")
    else:
        errs.append(f"缺失 {AUDIT_CONTROL_INDEX_MD.relative_to(repo_root)}")
    return errs


_HISTORICAL_TYPOS: frozenset[str] = frozenset(
    {
        "layer_00",
        "layer_01",
        "layer_02",
        "layer_03",
        "layer_04",
        "layer_05",
        "layer_06",
        "layer_07",
        "layer_08",
        "layer_09",
        "layer_10",
        "layer_11",
        "layer_12",
        "layer_13",
    }
)
_TEMPLATE_PLACEHOLDERS: frozenset[str] = frozenset({"layer_XX"})


def _load_valid_layers_from_authority_map() -> frozenset[str]:
    """_load_valid_layers_from_authority_map implementation."""
    canonical: set[str] = set()
    if AUTHORITY_MAP_PATH.exists():
        with open(AUTHORITY_MAP_PATH, encoding="utf-8") as f:
            in_layer_section = False
            in_valid_values = False
            for line in f:
                stripped = line.strip()
                if stripped == "protected_field: layer":
                    in_layer_section = True
                    continue
                if in_layer_section and "valid_values:" in stripped:
                    in_valid_values = True
                    continue
                if in_valid_values:
                    if stripped.startswith("- "):
                        value = stripped[2:].strip()
                        if "#" in value:
                            value = value[: value.index("#")].strip()
                        if value:
                            canonical.add(value)
                    else:
                        in_valid_values = False
                        in_layer_section = False
    return frozenset(canonical | _HISTORICAL_TYPOS | _TEMPLATE_PLACEHOLDERS)


_VALID_LAYERS_CACHE: frozenset[str] | None = None


def _get_valid_layers() -> frozenset[str]:
    """_get_valid_layers implementation."""
    global _VALID_LAYERS_CACHE
    if _VALID_LAYERS_CACHE is None:
        _VALID_LAYERS_CACHE = _load_valid_layers_from_authority_map()
    return _VALID_LAYERS_CACHE


VALID_DOCUMENT_STATUSES: frozenset[str] = frozenset(
    {"Draft", "Review", "Active", "Superseded", "Deprecated", "Retired", "Frozen", "Accepted", "Proposed", "Created"}
)
VALID_PRIORITIES: frozenset[str] = frozenset({"P0", "P1", "P2", "P3"})
VERSION_PATTERN = re.compile("^'?\\d+\\.\\d+\\.\\d+'?$|^N/A$|^1\\.0$")
LEGACY_LAYERS: frozenset[str] = frozenset({"layer_01"})
SEVERITY_P0_STATUS_CONFLICT = frozenset(
    {("Active", "Deprecated"), ("Active", "Retired"), ("Deprecated", "Active"), ("Retired", "Active")}
)


@dataclass
class FileMeta:
    path: Path
    rel_path: str
    module_id: str | None = None
    layer: str | None = None
    status: str | None = None
    priority: str | None = None
    version: str | None = None
    owner: str | None = None


@dataclass
class Contradiction:
    severity: str
    check_id: str
    description: str
    files: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    suggestion: str = ""


@dataclass
class ScanReport:
    scanned_files: int = 0
    parsed_files: int = 0
    contradictions: list[Contradiction] = field(default_factory=list)
    scan_dir: str = ""
    scan_time: str = ""

    @property
    def p0_count(self) -> int:
        """P0 级别计数"""
        return sum(1 for c in self.contradictions if c.severity == "P0")

    @property
    def p1_count(self) -> int:
        """P1 级别计数"""
        return sum(1 for c in self.contradictions if c.severity == "P1")

    @property
    def p2_count(self) -> int:
        """P2 级别计数"""
        return sum(1 for c in self.contradictions if c.severity == "P2")

    @property
    def total_count(self) -> int:
        """总计计数"""
        return len(self.contradictions)

    @property
    def has_p0(self) -> bool:
        """判断是否有 P0 级别发现"""
        return self.p0_count > 0


def parse_file(path: Path, repo_root: Path) -> FileMeta | None:
    """
    解析单个 Markdown 文件，返回 FileMeta；若无 frontmatter 则返回 None。
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    fm = parse_frontmatter(text)
    if not fm:
        return None
    try:
        rel = path.relative_to(repo_root).as_posix()
    except ValueError:
        rel = str(path)
    return FileMeta(
        path=path,
        rel_path=rel,
        module_id=fm.get("module_id"),
        layer=fm.get("layer"),
        status=fm.get("status"),
        priority=fm.get("priority"),
        version=fm.get("version"),
        owner=fm.get("owner"),
    )


def scan_directory(scan_dir: Path, repo_root: Path) -> list[FileMeta]:
    """scan directory"""
    metas: list[FileMeta] = []
    for md_path in scan_dir.rglob("*.md"):
        meta = parse_file(md_path, repo_root)
        if meta is not None:
            metas.append(meta)
    return metas


def check_p0_layer_invalid(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P0 层级违规"""
    result: list[Contradiction] = []
    for m in metas:
        if m.layer is None:
            continue
        if m.layer not in _get_valid_layers():
            result.append(
                Contradiction(
                    severity="P0",
                    check_id="P0-1",
                    description=f"layer 字段值 `{m.layer}` 不在有效层 ID 集合（L00-L13/cross_layer）中",
                    files=[m.rel_path],
                    values=[m.layer],
                    suggestion=f"将 `layer: {m.layer}` 修改为有效的层 ID（参见 ssot-authority-map.md §一）",
                )
            )
    return result


def check_p0_duplicate_active_module_id(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P0 重复活跃 module_id"""
    from collections import defaultdict

    active_by_id: dict[str, list[str]] = defaultdict(list)
    for m in metas:
        if m.module_id and m.status and (m.status.lower() in ("active",)):
            active_by_id[m.module_id].append(m.rel_path)
    result: list[Contradiction] = []
    for mid, paths in active_by_id.items():
        if len(paths) > 1:
            result.append(
                Contradiction(
                    severity="P0",
                    check_id="P0-2",
                    description=f"module_id `{mid}` 在 {len(paths)} 个 Active 文件中重复声明（违反零冗余原则）",
                    files=paths,
                    values=[mid] * len(paths),
                    suggestion=f"保留唯一真源，其余文件改为引用或删除。module_id: {mid}",
                )
            )
    return result


def check_p1_status_invalid(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P1 状态违规"""
    result: list[Contradiction] = []
    for m in metas:
        if m.status is None:
            continue
        if m.status not in VALID_DOCUMENT_STATUSES:
            result.append(
                Contradiction(
                    severity="P1",
                    check_id="P1-1",
                    description=f"status 字段值 `{m.status}` 不在有效状态集合中",
                    files=[m.rel_path],
                    values=[m.status],
                    suggestion="将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired",
                )
            )
    return result


def check_p1_module_id_layer_conflict(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P1 module_id 层级冲突"""
    from collections import defaultdict

    layer_by_id: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for m in metas:
        if m.module_id and m.layer:
            layer_by_id[m.module_id][m.layer].append(m.rel_path)
    result: list[Contradiction] = []
    for mid, layer_map in layer_by_id.items():
        if len(layer_map) > 1:
            all_files = [f for files in layer_map.values() for f in files]
            conflict_desc = "; ".join((f"`{layer}` in {files}" for layer, files in layer_map.items()))
            result.append(
                Contradiction(
                    severity="P1",
                    check_id="P1-2",
                    description=f"module_id `{mid}` 在不同文件中 layer 字段不一致：{conflict_desc}",
                    files=all_files,
                    values=list(layer_map.keys()),
                    suggestion="以 docs/02_enterprise_architecture/target-architecture/architecture-model/_index.yaml + layers/l*.yaml 中的层归属为准，统一修正",
                )
            )
    return result


def check_p1_module_id_status_conflict(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P1 module_id 状态冲突"""
    from collections import defaultdict

    status_by_id: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for m in metas:
        if m.module_id and m.status:
            status_by_id[m.module_id][m.status].append(m.rel_path)
    result: list[Contradiction] = []
    for mid, status_map in status_by_id.items():
        if len(status_map) <= 1:
            continue
        statuses = set(status_map.keys())
        is_conflict = any((a, b) in SEVERITY_P0_STATUS_CONFLICT for a in statuses for b in statuses if a != b)
        if is_conflict:
            all_files = [f for files in status_map.values() for f in files]
            conflict_desc = "; ".join((f"`{s}` in {fs}" for s, fs in status_map.items()))
            result.append(
                Contradiction(
                    severity="P1",
                    check_id="P1-3",
                    description=f"module_id `{mid}` 在不同文件中 status 字段矛盾：{conflict_desc}",
                    files=all_files,
                    values=list(statuses),
                    suggestion="以权威来源为准，废弃版本改为 Deprecated 或 Retired",
                )
            )
    return result


def check_p2_priority_invalid(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P2 优先级违规"""
    result: list[Contradiction] = []
    for m in metas:
        if m.priority is None:
            continue
        if m.priority not in VALID_PRIORITIES:
            result.append(
                Contradiction(
                    severity="P2",
                    check_id="P2-1",
                    description=f"priority 字段值 `{m.priority}` 不在有效集合 (P0/P1/P2/P3) 中",
                    files=[m.rel_path],
                    values=[m.priority],
                    suggestion="将 priority 修改为 P0/P1/P2/P3 之一",
                )
            )
    return result


def check_p2_version_format(metas: list[FileMeta]) -> list[Contradiction]:
    """检查 P2 版本格式违规"""
    result: list[Contradiction] = []
    for m in metas:
        if m.version is None:
            continue
        if not VERSION_PATTERN.match(m.version):
            result.append(
                Contradiction(
                    severity="P2",
                    check_id="P2-2",
                    description=f"version 字段值 `{m.version}` 格式不符合语义版本规范",
                    files=[m.rel_path],
                    values=[m.version],
                    suggestion="将 version 修改为 MAJOR.MINOR.PATCH 格式（如 1.0.0）",
                )
            )
    return result


class SsotValidator:
    """
    SSoT 矛盾扫描器。

    参数
    ----
    scan_dir   : 要扫描的目录（默认 docs/）
    repo_root  : 仓库根目录（默认自动探测）
    """

    def __init__(self, scan_dir: Path | None = None, repo_root: Path | None = None) -> None:
        """__init__ implementation."""
        self._repo_root = repo_root or REPO_ROOT
        self._scan_dir = (scan_dir or DEFAULT_SCAN_DIR).resolve()

    def run(self) -> ScanReport:
        """执行扫描"""
        report = ScanReport(
            scan_dir=str(self._scan_dir.relative_to(self._repo_root)),
            scan_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        all_md = list(self._scan_dir.rglob("*.md"))
        report.scanned_files = len(all_md)
        metas = scan_directory(self._scan_dir, self._repo_root)
        report.parsed_files = len(metas)
        checks = [
            check_p0_layer_invalid,
            check_p0_duplicate_active_module_id,
            check_p1_status_invalid,
            check_p1_module_id_layer_conflict,
            check_p1_module_id_status_conflict,
            check_p2_priority_invalid,
            check_p2_version_format,
        ]
        for check_fn in checks:
            report.contradictions.extend(check_fn(metas))
        return report


_SEVERITY_ICON = {"P0": "🔴", "P1": "🟡", "P2": "🔵"}


def render_report(report: ScanReport) -> str:
    """渲染报告"""
    lines: list[str] = []
    lines += [
        "---",
        "type: generated",
        "ttl: 7d",
        "generated_by: scripts/governance/validate_ssot.py",
        f"scan_time: {report.scan_time}",
        "---",
        "",
        "# SSoT 矛盾扫描报告",
        "",
        f"> **扫描目录**：`{report.scan_dir}`  ",
        f"> **扫描时间**：{report.scan_time}  ",
        f"> **扫描文件**：{report.scanned_files} 个 .md 文件，{report.parsed_files} 个含 frontmatter  ",
        "",
        "---",
        "",
        "## 摘要",
        "",
        "| 严重级别 | 数量 | 处置要求 |",
        "|---------|------|---------|",
        f"| 🔴 P0（严重）| {report.p0_count} | 必须立即修复，阻塞 beta 完成门禁 |",
        f"| 🟡 P1（重要）| {report.p1_count} | 需尽快修复，影响可信度 |",
        f"| 🔵 P2（建议）| {report.p2_count} | 低优先级，可按计划处理 |",
        f"| **合计** | **{report.total_count}** | |",
        "",
    ]
    if report.total_count == 0:
        lines += ["✅ **无矛盾** — 扫描通过，所有受保护字段一致。", ""]
        return "\n".join(lines)
    for severity in ("P0", "P1", "P2"):
        items = [c for c in report.contradictions if c.severity == severity]
        if not items:
            continue
        icon = _SEVERITY_ICON[severity]
        lines += ["---", "", f"## {icon} {severity} 矛盾（{len(items)} 条）", ""]
        for i, c in enumerate(items, 1):
            lines += [
                f"### {severity}-{i}：{c.description[:80]}",
                "",
                f"- **检查 ID**：`{c.check_id}`",
                "- **涉及文件**：",
            ]
            for f in c.files[:10]:
                lines.append(f"  - `{f}`")
            if len(c.files) > 10:
                lines.append(f"  - _（还有 {len(c.files) - 10} 个文件…）_")
            if c.values:
                lines.append(f'- **矛盾值**：{', '.join(f'`{v}`' for v in c.values[:5])}')
            if c.suggestion:
                lines += [f"- **建议**：{c.suggestion}", ""]
            else:
                lines.append("")
    lines += ["---", "", "## 下一步行动", ""]
    if report.p0_count > 0:
        lines.append(f"1. **立即修复 {report.p0_count} 条 P0 矛盾**（阻塞 beta 完成门禁）")
    if report.p1_count > 0:
        lines.append(f"2. 安排修复 {report.p1_count} 条 P1 矛盾（本 sprint 内完成）")
    if report.p2_count > 0:
        lines.append(f"3. 记录 {report.p2_count} 条 P2 建议（下 sprint 处理）")
    return "\n".join(lines)


def write_report(report: ScanReport, output_path: Path) -> None:
    """写入报告"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = render_report(report)
    tmp_path = f"{output_path}.{os.getpid()}.tmp"

    try:

        Path(tmp_path).write_text(content, encoding="utf-8")

        os.replace(tmp_path, output_path)

    except PermissionError:

        try:

            os.remove(tmp_path)

        except OSError:

            pass


def _build_parser() -> argparse.ArgumentParser:
    """_build_parser implementation."""
    parser = argparse.ArgumentParser(description="SSoT 矛盾扫描器（ZephyrAlpha T-2-33）")
    parser.add_argument("--scan-dir", type=Path, default=None, help="要扫描的目录（默认：docs/）")
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"报告输出路径（默认：{DEFAULT_REPORT_PATH.relative_to(REPO_ROOT)}）",
    )
    parser.add_argument(
        "--ci", action="store_true", help="CI：P0 frontmatter 矛盾或审计导航(findings/SCOPE)失败则 exit(1)"
    )
    parser.add_argument("--no-report", action="store_true", help="跳过写入报告文件（仅输出到 stdout）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：发现不阻塞（exit 0）")
    return parser


def main() -> None:
    """入口函数"""
    parser = _build_parser()
    args = parser.parse_args()
    scan_dir = args.scan_dir or DEFAULT_SCAN_DIR
    validator = SsotValidator(scan_dir=scan_dir)
    print("🔍 SSoT 矛盾扫描器启动...", file=sys.stderr)
    print(f"   扫描目录：{scan_dir}", file=sys.stderr)
    report = validator.run()
    print(f"   扫描完成：{report.scanned_files} 个文件，{report.parsed_files} 个含 frontmatter", file=sys.stderr)
    print(f"   矛盾统计：P0={report.p0_count}  P1={report.p1_count}  P2={report.p2_count}", file=sys.stderr)
    nav_issues: list[str] = []
    if args.ci:
        nav_issues = check_audit_navigation_wiring()
        for msg in nav_issues:
            print(f"   🔴 CI（导航）: {msg}", file=sys.stderr)
    if not args.no_report:
        write_report(report, args.report)
        print(f"   报告写入：{args.report}", file=sys.stderr)
    if args.warn_only:
        print(f"\n⚠ warn-only 模式：{report.total_count} 条矛盾未阻塞。", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if args.ci and (report.has_p0 or nav_issues):
        if report.has_p0:
            print(
                f"\n❌ CI 门禁阻塞：发现 {report.p0_count} 条 P0 矛盾，必须修复后才能通过 beta 完成门禁。",
                file=sys.stderr,
            )
        if nav_issues:
            print("\n❌ CI 门禁阻塞：审计/findings 或 SCOPE 导航检查失败。", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)
    if report.total_count == 0:
        print("✅ 扫描通过：未发现 SSoT 矛盾。", file=sys.stderr)
    else:
        print(f"⚠️  发现 {report.total_count} 条矛盾，详见报告。", file=sys.stderr)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
