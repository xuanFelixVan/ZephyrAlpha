"""
V-15 TruthSourceCascadeValidator — 真源连锁回溯校验器
======================================================
任务编号 : T-V2-012（Phase 1a-parallel）
权限层级 : AI-Modifiable + Human-Gated
  - 影响追踪报告输出 = AI-Modifiable
  - 阈值告警触发 = Human-Gated（warn-only，Phase 1 不阻塞）
真源声明 : ai-autonomy-authority-registry.md §2.11 (V-15)
关联决策 : rationale-log R82（兜底需求）、R86（任务卡下发）
创建日期 : 2026-04-27
版本     : v1.0.0

功能说明
--------
扫描 architecture-rationale-log.md 中 R-86 起的 R-XXX 决策：

1. 解析每条 R-XXX 决策的 decision_id / decision_date /
   decision_summary / affected_files 字段（Pydantic v2 frozen）
2. 构建反向链表：文件 → 影响它的所有 R-XXX 决策（按时间排序）
3. 对比每个文件的 frontmatter last_updated 与最新 R-XXX 日期
4. 真源 last_updated < 最新 R-XXX 日期时输出 CASCADE-WARN
5. 生成影响追踪报告：.runtime/reports/truth_source_cascade_<date>.md

Phase 1 约束
-----------
- 仅扫描 R-86 起（MIN_R_NUMBER = 86），向前不追溯历史
- warn-only 模式：exit code = 0，不阻塞流程
- 真源 frontmatter 缺少 last_updated 时降级为 INFO（不视为错误）
- R-87 起要求在决策行中嵌入 affected_files 字段（两种格式均支持）

affected_files 嵌入格式（在 rationale-log 表格行内）：
  格式 A（内联 YAML 列表）：
    affected_files: [docs/file1.md, src/file2.py]
  格式 B（markdown 代码块）：
    ```affected_files
    - docs/file1.md
    - src/file2.py
    ```
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import REPO_ROOT
from _shared.frontmatter import parse_frontmatter_from_file

RATIONALE_LOG_PATH: Path = (
    REPO_ROOT / "docs" / "19_development_workspace" / "structure-and-mapping" / "architecture-rationale-log.md"
)
REPORTS_DIR: Path = REPO_ROOT / ".runtime" / "reports"

# Phase 1：仅扫描 R-86 起
MIN_R_NUMBER: int = 86

# ---------------------------------------------------------------------------
# Pydantic 模型
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RationaleDecision:
    """单条 R-XXX 架构决策记录。"""

    decision_id: str
    decision_date: date
    decision_summary: str
    affected_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TruthSourceCascadeResult:
    """影响追踪全局结果。"""

    report_date: datetime
    decisions_scanned: int
    files_impacted: int
    warnings: list[str]
    cascade_rows: list[dict]


# ---------------------------------------------------------------------------
# 解析层
# ---------------------------------------------------------------------------

# 匹配 rationale-log 表格中 R-XXX 开头的行
# 格式: | R86 | ... | ... |
_ROW_PATTERN = re.compile(r"^\|\s*(R-?(\d+)(?:-[A-Z])?)\s*\|(.+?)(?:\|[^|]*)?$", re.DOTALL)

# 从单元格内容提取日期（格式 YYYY-MM-DD）
_DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")

# affected_files 内联格式：affected_files: [path1, path2]
_AF_INLINE_PATTERN = re.compile(r"affected_files:\s*\[([^\]]*)\]")

# affected_files 代码块格式
_AF_BLOCK_PATTERN = re.compile(r"```affected_files\s*\n(.*?)```", re.DOTALL)

# affected_files 块级 YAML 格式（在 cell 内）
_AF_YAML_BLOCK_PATTERN = re.compile(r"affected_files:\s*\n((?:[ \t]*[-*]\s+\S[^\n]*\n?)+)")

# 表格行分隔符（跳过）
_SEPARATOR_PATTERN = re.compile(r"^\s*\|[-\s|:]+\|\s*$")


def _extract_affected_files(cell_text: str) -> list[str]:
    """从 rationale-log 单元格文本中提取 affected_files 列表。

    优先级：代码块格式 > 内联列表格式 > YAML 块格式。
    """
    # 格式 B：```affected_files ... ``` 代码块
    block_m = _AF_BLOCK_PATTERN.search(cell_text)
    if block_m:
        items = re.findall(r"[-*]\s+(\S[^\n]*)", block_m.group(1))
        return [f.strip() for f in items if f.strip()]

    # 格式 A：affected_files: [path1, path2]
    inline_m = _AF_INLINE_PATTERN.search(cell_text)
    if inline_m:
        raw = inline_m.group(1)
        return [f.strip().strip("\"'") for f in raw.split(",") if f.strip()]

    # 格式 C：YAML 块（多行，带 - 前缀）
    yaml_m = _AF_YAML_BLOCK_PATTERN.search(cell_text)
    if yaml_m:
        items = re.findall(r"[-*]\s+(\S[^\n]*)", yaml_m.group(1))
        return [f.strip() for f in items if f.strip()]

    return []


def _extract_date(cell_text: str) -> date | None:
    """从单元格文本中提取最早出现的 YYYY-MM-DD 日期。"""
    matches = _DATE_PATTERN.findall(cell_text)
    for raw in matches:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            continue
    return None


def _parse_row(line: str) -> RationaleDecision | None:
    """将 rationale-log 中的一行解析为 RationaleDecision。

    返回 None 表示不是有效 R-XXX 行，或 R 号 < MIN_R_NUMBER，
    或该行无 affected_files（Phase 1 跳过无影响文件的行）。
    """
    if _SEPARATOR_PATTERN.match(line):
        return None

    m = _ROW_PATTERN.match(line.strip())
    if not m:
        return None

    raw_id: str = m.group(1)  # e.g. "R86" or "R-87" or "R59-F"
    r_number: int = int(m.group(2))  # 纯数字部分

    if r_number < MIN_R_NUMBER:
        return None

    rest: str = m.group(3)  # 第二列及后续全部内容

    # 提取 affected_files
    affected = _extract_affected_files(rest)

    # 未标注 affected_files 的行在 Phase 1 跳过（不生成虚假告警）
    if not affected:
        return None

    # 提取日期
    decision_date = _extract_date(rest) or date.today()

    # 摘要取第二列前 120 字符（去掉 markdown 强调符号）
    summary_raw = rest.split("|")[0] if "|" in rest else rest
    summary = re.sub(r"\*{1,2}|_{1,2}", "", summary_raw).strip()[:120]

    return RationaleDecision(
        decision_id=raw_id,
        decision_date=decision_date,
        decision_summary=summary,
        affected_files=affected,
    )


def parse_rationale_log(
    path: Path | None = None,
) -> list[RationaleDecision]:
    """解析 architecture-rationale-log.md，返回所有 R-XXX 决策列表。

    仅返回满足以下条件的记录：
    - R 号 >= MIN_R_NUMBER（Phase 1 约束）
    - 包含 affected_files 字段（空列表的行被忽略）

    参数
    ----
    path
        rationale log 文件路径；默认 RATIONALE_LOG_PATH。

    返回
    ----
    list[RationaleDecision]
        按文件顺序排列（不额外排序，调用方自行排序）。
    """
    resolved = path or RATIONALE_LOG_PATH
    if not resolved.exists():
        return []

    decisions: list[RationaleDecision] = []
    with resolved.open(encoding="utf-8") as fh:
        for line in fh:
            decision = _parse_row(line)
            if decision is not None:
                decisions.append(decision)

    return decisions


# ---------------------------------------------------------------------------
# 反向链表构建
# ---------------------------------------------------------------------------


def build_cascade_map(
    decisions: list[RationaleDecision],
) -> dict[str, list[RationaleDecision]]:
    """构建文件 → 影响它的所有 R-XXX 决策列表（按 decision_date 升序）。

    参数
    ----
    decisions
        由 parse_rationale_log() 返回的决策列表。

    返回
    ----
    dict[str, list[RationaleDecision]]
        键为仓库相对路径（str），值为按时间升序排列的决策列表。
    """
    cascade: dict[str, list[RationaleDecision]] = defaultdict(list)
    for d in decisions:
        for f in d.affected_files:
            cascade[f].append(d)

    # 每个文件的决策列表按日期升序排列
    for key in cascade:
        cascade[key].sort(key=lambda d: d.decision_date)

    return dict(cascade)


# ---------------------------------------------------------------------------
# 真源 frontmatter 解析
# ---------------------------------------------------------------------------


def _parse_frontmatter_date(file_path: Path) -> date | None:
    """读取文件 frontmatter 中的 last_updated 字段。

    支持 ISO 8601 格式（YYYY-MM-DD）。
    文件不存在或 frontmatter 解析失败时返回 None。
    """
    if not file_path.exists():
        return None

    fm = parse_frontmatter_from_file(file_path)
    if not fm:
        return None

    raw = fm.get("last_updated")
    if raw is None:
        return None

    if isinstance(raw, date):
        return raw

    try:
        return date.fromisoformat(str(raw)[:10])
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# 过时真源检测
# ---------------------------------------------------------------------------


def detect_outdated_truth_sources(
    cascade: dict[str, list[RationaleDecision]],
    repo_root: Path | None = None,
) -> tuple[list[str], list[dict]]:
    """对反向链表中每个文件检查 last_updated 与最新 R-XXX 日期。

    参数
    ----
    cascade
        build_cascade_map() 的输出。
    repo_root
        仓库根目录（相对路径解析用）；默认 REPO_ROOT。

    返回
    ----
    (warnings, rows)
        warnings : 每条 CASCADE-WARN 字符串列表
        rows     : 报告表格行 list[dict]，含 file/decisions/latest_date/
                   last_updated/status 字段
    """
    root = repo_root or REPO_ROOT
    warnings: list[str] = []
    rows: list[dict] = []

    for relative_path, decisions in sorted(cascade.items()):
        latest_decision = max(decisions, key=lambda d: d.decision_date)
        latest_date = latest_decision.decision_date

        file_path = root / relative_path.replace("\\", "/")
        last_updated = _parse_frontmatter_date(file_path)

        if last_updated is None:
            status = "INFO（缺少 last_updated）"
        elif last_updated < latest_date:
            warn = (
                f"[CASCADE-WARN] 真源 {relative_path} 受 "
                f"{latest_decision.decision_id} 影响但未更新"
                f"（{last_updated} < {latest_date}）"
            )
            warnings.append(warn)
            status = "⚠️ OUTDATED"
        else:
            status = "✅ OK"

        decision_ids = ", ".join(d.decision_id for d in decisions)
        rows.append(
            {
                "file": relative_path,
                "decisions": decision_ids,
                "latest_date": str(latest_date),
                "last_updated": str(last_updated) if last_updated else "—",
                "status": status,
            }
        )

    return warnings, rows


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------


def generate_report(
    result: TruthSourceCascadeResult,
    output_dir: Path | None = None,
) -> Path:
    """将影响追踪结果输出为 markdown 报告文件。

    文件名格式：truth_source_cascade_<YYYY-MM-DD>.md
    已存在同名文件时追加时间戳后缀（精确到秒），防止覆盖。

    参数
    ----
    result
        TruthSourceCascadeResult 对象。
    output_dir
        输出目录；默认 REPORTS_DIR（.runtime/reports/）。

    返回
    ----
    Path
        实际写入的报告文件路径。
    """
    resolved_dir = output_dir or REPORTS_DIR
    resolved_dir.mkdir(parents=True, exist_ok=True)

    date_str = result.report_date.strftime("%Y-%m-%d")
    candidate = resolved_dir / f"truth_source_cascade_{date_str}.md"
    if candidate.exists():
        ts = result.report_date.strftime("%Y-%m-%dT%H%M%S")
        candidate = resolved_dir / f"truth_source_cascade_{ts}.md"

    lines: list[str] = [
        "# TruthSource Cascade Impact Report",
        "",
        f"**生成时间**：{result.report_date.isoformat()}",
        f"**扫描范围**：R-{MIN_R_NUMBER} 起（向前不追溯）",
        "",
        "## 汇总",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| 扫描决策数 | {result.decisions_scanned} |",
        f"| 受影响文件数 | {result.files_impacted} |",
        f"| CASCADE-WARN 数 | {len(result.warnings)} |",
        "",
    ]

    if result.cascade_rows:
        lines += [
            "## 级联影响矩阵",
            "",
            "| 文件 | 影响决策 | 最新决策日期 | 文件 last_updated | 状态 |",
            "|------|----------|-------------|------------------|------|",
        ]
        for row in result.cascade_rows:
            lines.append(
                f"| `{row['file']}` | {row['decisions']} | "
                f"{row['latest_date']} | {row['last_updated']} | {row['status']} |"
            )
        lines.append("")

    if result.warnings:
        lines += [
            "## 告警详情",
            "",
        ]
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")
    else:
        lines += [
            "## 告警详情",
            "",
            "_无 CASCADE-WARN（所有受影响真源均已更新，或暂无 affected_files 标注）_",
            "",
        ]

    lines += [
        "---",
        "",
        "> Phase 1 warn-only 模式：本报告不阻塞流程。",
        "> 相关决策：R82（V-15 兜底需求）/ R86（T-V2-012 任务卡）",
        "",
    ]

    report_text = "\n".join(lines)
    candidate.write_text(report_text, encoding="utf-8", newline="\n")
    return candidate


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def run(
    rationale_log_path: Path | None = None,
    reports_dir: Path | None = None,
    repo_root: Path | None = None,
    *,
    quiet: bool = False,
) -> TruthSourceCascadeResult:
    """执行完整的真源级联校验流程。

    参数
    ----
    rationale_log_path
        rationale log 路径；默认 RATIONALE_LOG_PATH。
    reports_dir
        报告输出目录；默认 REPORTS_DIR。
    repo_root
        仓库根目录；默认 REPO_ROOT。
    quiet
        为 True 时不打印 stdout 输出（测试场景用）。

    返回
    ----
    TruthSourceCascadeResult
        包含全部警告和级联矩阵行的结果对象。
    """
    decisions = parse_rationale_log(rationale_log_path)
    cascade = build_cascade_map(decisions)
    warnings, rows = detect_outdated_truth_sources(cascade, repo_root)

    now = datetime.now(tz=UTC)
    result = TruthSourceCascadeResult(
        report_date=now,
        decisions_scanned=len(decisions),
        files_impacted=len(cascade),
        warnings=warnings,
        cascade_rows=rows,
    )

    report_path = generate_report(result, reports_dir)

    if not quiet:
        print(
            f"[V-15] TruthSourceCascadeValidator 完成\n"
            f"  决策已扫描：{result.decisions_scanned}\n"
            f"  受影响文件：{result.files_impacted}\n"
            f"  CASCADE-WARN：{len(result.warnings)}\n"
            f"  报告输出：{report_path}",
            file=sys.stderr,
        )
        for w in result.warnings:
            print(f"  {w}", file=sys.stderr)

    return result


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="V-15 真源级联验证器")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()

    result = run()
    if args.warn_only:
        sys.exit(0)
    if result.warnings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
