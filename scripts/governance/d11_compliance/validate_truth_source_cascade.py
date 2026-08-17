# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.d11_compliance.validate_truth_source_cascade
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
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
validate_truth_source_cascade.py — 真源级联一致性校验

扫描 architecture-rationale-log.md 中的决策记录，提取 affected_files，
对比每个受影响文件的 last_updated frontmatter 字段与最新决策日期，
检测真源级联滞后（CASCADE-WARN）。

exit codes: 0=pass（warn-only 模式）
"""
from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path

__manifest__ = """
args: []
description: 真源级联一致性校验（决策日期 vs 文件 last_updated，CASCADE-WARN 告警）。
dimensions:
- D11
priority: P2
timeout_seconds: 60
warn_only: true
"""

# bootstrap sys.path so `from _shared.xxx import ...` works regardless of CWD
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402

# 真源决策日志路径（默认）
RATIONALE_LOG_PATH = (
    REPO_ROOT / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"
)

# 报告输出目录（默认）
DEFAULT_REPORTS_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports"

# 最小跟踪 R 编号（R50 及以下视为历史决策，不参与级联校验）
MIN_R_NUMBER = 51

# Date pattern: （2026-04-28） or (2026-04-28)
_DATE_PATTERN = re.compile(r"[（(](\d{4}-\d{2}-\d{2})[）)]")

# R-number pattern: R87, R-87, R087
_R_ID_PATTERN = re.compile(r"R-?(\d+)")

# Inline list pattern: affected_files: [docs/a.md, src/b.py]
_INLINE_LIST_PATTERN = re.compile(r"affected_files:\s*\[([^\]]+)\]", re.DOTALL)

# Code block pattern: ```affected_files ... ```
_CODE_BLOCK_PATTERN = re.compile(
    r"```affected_files\s*\n(.*?)\n```", re.DOTALL
)

# YAML block pattern: affected_files:\n  - x\n  - y
_YAML_BLOCK_PATTERN = re.compile(
    r"affected_files:\s*\n((?:\s*-\s+.+\n?)+)", re.MULTILINE
)

# Markdown table row pattern (3+ columns)
_TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|\s*$")

# Table separator pattern: |------|------|------|
_TABLE_SEP_PATTERN = re.compile(r"^\|[\s:|-]+\|\s*$")


class RationaleDecision:
    """单条决策记录。

    Fields:
        decision_id: 决策 ID（如 "R87"）
        decision_date: 决策日期（date 对象）
        decision_summary: 决策摘要
        affected_files: 受影响文件路径列表
    """

    def __init__(
        self,
        decision_id: str = "",
        decision_date=None,
        decision_summary: str = "",
        affected_files: list[str] | None = None,
    ) -> None:
        """__init__ implementation."""
        self.decision_id = decision_id
        self.decision_date = decision_date
        self.decision_summary = decision_summary
        self.affected_files = list(affected_files) if affected_files else []


class TruthSourceCascadeResult:
    """真源级联校验结果。

    Fields:
        report_date: 报告生成时间（datetime）
        decisions_scanned: 扫描到的决策数（仅含 affected_files 的）
        files_impacted: 受影响文件数
        warnings: CASCADE-WARN 告警字符串列表
        cascade_rows: 级联表行列表（dict: file/decisions/latest_date/last_updated/status）
    """

    def __init__(
        self,
        report_date: datetime | None = None,
        decisions_scanned: int = 0,
        files_impacted: int = 0,
        warnings: list[str] | None = None,
        cascade_rows: list[dict] | None = None,
    ) -> None:
        """__init__ implementation."""
        self.report_date = report_date or datetime.now()
        self.decisions_scanned = decisions_scanned
        self.files_impacted = files_impacted
        self.warnings = warnings or []
        self.cascade_rows = cascade_rows or []


def _extract_affected_files(cell: str) -> list[str]:
    """从决策描述单元格提取 affected_files 列表。

    支持四种格式：
    1. inline list: `affected_files: [docs/a.md, src/b.py]`
    2. inline list with quotes: `affected_files: ["docs/a.md", "src/b.py"]`
    3. code block: ````affected_files\n- docs/a.md\n- src/b.py\n````
    4. YAML block: `affected_files:\n  - docs/c.md\n  - config/d.yaml`
    """
    if not cell or "affected_files" not in cell:
        return []

    # 1. Try inline list format
    m = _INLINE_LIST_PATTERN.search(cell)
    if m:
        items = m.group(1).split(",")
        result = []
        for item in items:
            cleaned = item.strip().strip("\"' ")
            if cleaned:
                result.append(cleaned)
        return result

    # 2. Try code block format
    m = _CODE_BLOCK_PATTERN.search(cell)
    if m:
        block = m.group(1)
        result = []
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("- "):
                cleaned = line[2:].strip().strip("\"' ")
                if cleaned:
                    result.append(cleaned)
        return result

    # 3. Try YAML block format
    m = _YAML_BLOCK_PATTERN.search(cell)
    if m:
        block = m.group(1)
        result = []
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("- "):
                cleaned = line[2:].strip().strip("\"' ")
                if cleaned:
                    result.append(cleaned)
        return result

    return []


def _parse_r_number(decision_id: str) -> int:
    """从 decision_id 提取 R 编号数字。返回 -1 if 无法解析。"""
    m = _R_ID_PATTERN.search(decision_id)
    if m:
        return int(m.group(1))
    return -1


def parse_rationale_log(path) -> list[RationaleDecision]:
    """解析 rationale-log.md，提取决策记录。

    表格行格式：`| R87 | col2 | col3（含日期和 affected_files） |`
    - 跳过分隔行（|------|------|------|）
    - 跳过 R 编号 < MIN_R_NUMBER 的条目
    - 跳过无 affected_files 的条目
    - 文件不存在或为空 → []
    """
    p = Path(path)
    if not p.is_file():
        return []
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    if not text.strip():
        return []

    decisions: list[RationaleDecision] = []
    for line in text.splitlines():
        if not _TABLE_ROW_PATTERN.match(line):
            continue
        if _TABLE_SEP_PATTERN.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        decision_id_raw = cells[0].strip()
        if not decision_id_raw:
            continue
        # Extract R-id (may be embedded in **bold** or plain)
        r_match = _R_ID_PATTERN.search(decision_id_raw)
        if not r_match:
            continue
        r_num = int(r_match.group(1))
        if r_num < MIN_R_NUMBER:
            continue
        decision_id = f"R{r_num}"
        # Col 3 (index 2) contains date and affected_files
        desc_cell = cells[2] if len(cells) >= 3 else ""
        # Extract date
        date_match = _DATE_PATTERN.search(desc_cell)
        if not date_match:
            continue
        try:
            decision_date = date.fromisoformat(date_match.group(1))
        except ValueError:
            continue
        # Extract affected_files
        affected = _extract_affected_files(desc_cell)
        if not affected:
            continue
        decisions.append(RationaleDecision(
            decision_id=decision_id,
            decision_date=decision_date,
            decision_summary=desc_cell.strip(),
            affected_files=affected,
        ))
    return decisions


def build_cascade_map(decisions: list[RationaleDecision]) -> dict[str, list[RationaleDecision]]:
    """构建级联映射：{file_path: [decisions sorted by date ascending]}。

    - 空决策列表 → {}
    - 多条决策影响同一文件 → 按 decision_date 升序排列
    """
    cascade: dict[str, list[RationaleDecision]] = {}
    for d in decisions:
        for f in d.affected_files:
            cascade.setdefault(f, []).append(d)
    # Sort each list by decision_date ascending
    for f in cascade:
        cascade[f].sort(key=lambda d: d.decision_date)
    return cascade


def _parse_frontmatter_date(path) -> date | None:
    """从 markdown 文件 frontmatter 提取 last_updated 日期。

    - 文件不存在 → None
    - 无 frontmatter → None
    - 无 last_updated 字段 → None
    - 解析失败 → None
    """
    from scripts.governance._shared.frontmatter import parse_frontmatter_from_file

    p = Path(path)
    if not p.is_file():
        return None
    fm = parse_frontmatter_from_file(p)
    if fm is None:
        return None
    if "last_updated" not in fm:
        return None
    value = fm["last_updated"]
    if value is None:
        return None
    # value may be date, datetime, or str
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def detect_outdated_truth_sources(
    cascade_map: dict[str, list[RationaleDecision]],
    repo_root=None,
) -> tuple[list[str], list[dict]]:
    """检测真源级联滞后。

    Args:
        cascade_map: {file_path: [decisions]} 来自 build_cascade_map
        repo_root: 仓库根目录（用于定位文件）

    Returns:
        (warnings, rows) 元组：
        - warnings: CASCADE-WARN 告警字符串列表
        - rows: 级联表行列表，每项为 dict
          {"file", "decisions", "latest_date", "last_updated", "status"}
    """
    if not cascade_map:
        return [], []
    root = Path(repo_root) if repo_root else REPO_ROOT

    warnings: list[str] = []
    rows: list[dict] = []
    for file_path in sorted(cascade_map.keys()):
        decisions = cascade_map[file_path]
        latest = decisions[-1]  # sorted ascending
        latest_date = latest.decision_date
        # Locate file under repo_root
        abs_path = root / file_path
        last_updated = _parse_frontmatter_date(abs_path)
        # Format decisions list as comma-separated IDs
        decisions_str = ", ".join(d.decision_id for d in decisions)
        latest_date_str = latest_date.isoformat()

        if last_updated is None:
            status = "ℹ️ INFO: 无 last_updated"
            last_updated_str = "N/A"
        elif last_updated < latest_date:
            status = "⚠️ OUTDATED"
            last_updated_str = last_updated.isoformat()
            warnings.append(
                f"[CASCADE-WARN] 真源 {file_path} 受 {latest.decision_id} 影响但未更新"
                f"（{last_updated_str} < {latest_date_str}）"
            )
        else:
            status = "✅ OK"
            last_updated_str = last_updated.isoformat()

        rows.append({
            "file": file_path,
            "decisions": decisions_str,
            "latest_date": latest_date_str,
            "last_updated": last_updated_str,
            "status": status,
        })
    return warnings, rows


def generate_report(result: TruthSourceCascadeResult, output_path) -> Path:
    """生成 markdown 报告文件。

    Args:
        result: TruthSourceCascadeResult 实例
        output_path: 输出目录路径

    Returns:
        生成的报告文件 Path
    """
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Filename: truth_source_cascade_<timestamp>.md
    # 同一秒内多次调用时，若文件已存在则追加计数器后缀确保唯一性
    # （test_duplicate_date_gets_timestamp_suffix 期望两次调用返回不同路径）。
    # 不依赖 time.time_ns() —— Windows 上连续两次调用可能返回相同值。
    base_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"truth_source_cascade_{base_timestamp}.md"
    report_path = out_dir / filename
    counter = 1
    while report_path.exists():
        filename = f"truth_source_cascade_{base_timestamp}_{counter}.md"
        report_path = out_dir / filename
        counter += 1

    lines: list[str] = []
    lines.append("# 真源级联一致性报告\n")
    if result.report_date:
        lines.append(f"**报告时间**: {result.report_date.isoformat()}\n")
    lines.append("## 摘要\n")
    lines.append(f"- 扫描决策数: {result.decisions_scanned}")
    lines.append(f"- 受影响文件数: {result.files_impacted}")
    lines.append(f"- 告警数: {len(result.warnings)}\n")

    lines.append("## 告警\n")
    if result.warnings:
        for w in result.warnings:
            lines.append(f"- {w}")
    else:
        lines.append("无 CASCADE-WARN\n")

    lines.append("## 级联表\n")
    if result.cascade_rows:
        lines.append("| 文件 | 决策 | 最新决策日期 | last_updated | 状态 |")
        lines.append("|------|------|-------------|--------------|------|")
        for row in result.cascade_rows:
            lines.append(
                f"| {row['file']} | {row['decisions']} | {row['latest_date']} | "
                f"{row['last_updated']} | {row['status']} |"
            )
    else:
        lines.append("无级联记录\n")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def run(log, reports, repo_root=None, quiet: bool = True) -> TruthSourceCascadeResult:
    """运行真源级联校验（集成入口）。

    Args:
        log: rationale-log.md 路径
        reports: 报告输出目录
        repo_root: 仓库根目录（用于定位文件）
        quiet: 静默模式（不输出到 stdout）

    Returns:
        TruthSourceCascadeResult
    """
    decisions = parse_rationale_log(log)
    # decisions_scanned: count of decisions with affected_files
    decisions_scanned = len(decisions)
    cascade_map = build_cascade_map(decisions)
    files_impacted = len(cascade_map)
    warnings, rows = detect_outdated_truth_sources(cascade_map, repo_root)
    result = TruthSourceCascadeResult(
        report_date=datetime.now(),
        decisions_scanned=decisions_scanned,
        files_impacted=files_impacted,
        warnings=warnings,
        cascade_rows=rows,
    )
    generate_report(result, reports)
    return result
