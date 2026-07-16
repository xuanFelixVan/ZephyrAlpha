# [BLUEPRINT] MOD-INF-005 | scripts/governance/d8_doc_sync/validate_document_ttl.py | §
# [MODULE] scripts.governance.d8_doc_sync.validate_document_ttl
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d8_doc_sync.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
validate_document_ttl.py — 文档 TTL 过期检测



对标：GOV-DOC-006 §一（TTL 合法值从 ttl_vocabulary.yaml 动态加载）/ §三（LATEST 命名规范）

检测内容：
- TTL 合法值检查（v2.0.0 二元：permanent / task_bound，从词表动态加载）
- 状态快照文件应使用 LATEST 命名

扫描模式（v1.1.0 新增，只输出清单不删除）：
- --list-by-ttl <value>          按 ttl 值列出文件清单
- --list-time-expired            列出已到期文件（v2.0.0 废弃时间阈值，结果恒为空）
- --list-all-non-permanent       列出所有 ttl != permanent 的文件（一键扫描）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 文档 TTL 过期检测（GOV-DOC-006 §一/§三 — TTL合法值+过期文件+LATEST命名）
dimensions:
- D8
priority: P1
timeout_seconds: 30
warn_only: false
"""


import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files
from _shared.yaml_utils import load_vocabulary_values  # noqa: E402  # D-D-05：词表加载收敛到 SSoT

ensure_utf8_stdout()
import argparse
from datetime import datetime


def _load_ttl_values() -> set[str]:
    """从 ttl_vocabulary.yaml 加载合法 ttl 值集合（v2.0.0 仅 permanent/task_bound）。

    D-D-05 治本（2026-06-30）：收敛到 SSoT ``load_vocabulary_values``。
    词表是规则数据唯一真源，直接消费不复制（trae_060 §2）。
    """
    return load_vocabulary_values("ttl_vocabulary.yaml")


VALID_TTL_VALUES: set[str] = _load_ttl_values()
DATED_SNAPSHOT_PATTERN = re.compile("-\\d{4}-\\d{2}-\\d{2}\\.(json|yaml|yml|md)$", re.IGNORECASE)


def scan_ttl_violations() -> list[dict]:
    """扫描文档 TTL 违规"""
    findings = []
    "扫描文档 TTL 违规."
    docs_dir = REPO_ROOT / "" / "docs"
    "扫描并返回发现列表."
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    now = datetime.now()
    for filepath in iter_files(docs_dir, extensions=frozenset({".md", ".yaml", ".yml"})):
        fm, _body = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        ttl = fm.get("ttl", "")
        date_str = fm.get("date", "")
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        if ttl and ttl not in VALID_TTL_VALUES:
            findings.append(
                {
                    "file": rel,
                    "type": "INVALID_TTL",
                    "detail": f"ttl='{ttl}' 不在合法枚举中（合法值: {', '.join(sorted(VALID_TTL_VALUES))}）",
                    "severity": "MEDIUM",
                }
            )
        if ttl == "30d" and date_str:
            try:
                file_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                if (now - file_date).days > 30:
                    if "archive" not in rel.lower() and "_working/audit" not in rel:
                        findings.append(
                            {
                                "file": rel,
                                "type": "TTL_30D_EXPIRED",
                                "detail": f"ttl=30d 文件已过期 {(now - file_date).days} 天，应归档",
                                "severity": "MEDIUM",
                            }
                        )
            except ValueError:
                pass
        if ttl == "7d" and date_str:
            try:
                file_date = datetime.strptime(str(date_str), "%Y-%m-%d")
                if (now - file_date).days > 7:
                    findings.append(
                        {
                            "file": rel,
                            "type": "TTL_7D_EXPIRED",
                            "detail": f"ttl=7d 文件已过期 {(now - file_date).days} 天，应删除",
                            "severity": "HIGH",
                        }
                    )
            except ValueError:
                pass
        if ttl == "session":
            findings.append(
                {
                    "file": rel,
                    "type": "TTL_SESSION_IN_REPO",
                    "detail": "ttl=session 文件不应提交到 git",
                    "severity": "MEDIUM",
                }
            )
    return findings
    "扫描文档 TTL 违规."


def scan_dated_snapshots() -> list[dict]:
    """扫描过期快照."""
    findings = []
    "扫描并返回发现列表."
    scan_dirs = [REPO_ROOT / "" / "docs" / "_working" / "audit", REPO_ROOT / "" / "docs" / "02_enterprise_architecture"]
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for filepath in iter_files(scan_dir, extensions=frozenset({".json", ".yaml", ".yml", ".md"})):
            if DATED_SNAPSHOT_PATTERN.search(filepath.name):
                rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                findings.append(
                    {
                        "file": rel,
                        "type": "DATED_SNAPSHOT",
                        "detail": f"状态快照应使用 LATEST 命名（当前: {filepath.name}）",
                        "severity": "LOW",
                    }
                )
    return findings
    "扫描过期快照."


def _iter_md_files_with_frontmatter():
    """迭代所有有 frontmatter 的 .md 文件（docs/**/*.md）。

    返回 (filepath, fm) 元组迭代器，fm 为 frontmatter dict（空 dict 表示无 frontmatter）。
    """
    docs_dir = REPO_ROOT / "docs"
    if not docs_dir.exists():
        return
    for filepath in iter_files(docs_dir, extensions=frozenset({".md"})):
        fm, _body = parse_frontmatter_from_file(filepath)
        yield filepath, fm


def list_files_by_ttl(value: str) -> list[dict]:
    """按 ttl 值列出文件清单（不删除，仅输出）。

    Args:
        value: ttl 枚举值（permanent/periodic_review_90d/30d/7d/session/task_bound）

    Returns:
        [{path, ttl, mtime, age_days, dir}] 列表，按 path 排序。
    """
    if value not in VALID_TTL_VALUES:
        raise ValueError(f"非法 ttl 值: {value}（合法值: {sorted(VALID_TTL_VALUES)}）")
    now = datetime.now()
    results = []
    for filepath, fm in _iter_md_files_with_frontmatter():
        ttl = fm.get("ttl", "")
        if ttl != value:
            continue
        stat = filepath.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        results.append({
            "path": rel,
            "ttl": ttl or "(空)",
            "mtime": mtime.strftime("%Y-%m-%d"),
            "age_days": (now - mtime).days,
            "dir": str(filepath.parent.relative_to(REPO_ROOT)).replace("\\", "/"),
        })
    results.sort(key=lambda x: x["path"])
    return results


def list_time_expired_files() -> list[dict]:
    """列出 ttl=7d/30d/periodic_review_90d 中已到期文件（mtime + 当前日期算术判定）。

    判定口径：文件 mtime 距今天数 > ttl 阈值。
    与 scan_ttl_violations() 的 date 字段判定互补——date 是文档声明日期，
    mtime 是文件实际修改时间，取两者中较早的过期判定更保守。

    Returns:
        [{path, ttl, mtime, age_days, threshold_days, dir}] 列表。
    """
    # v2.0.0 已废弃时间阈值 ttl（7d/30d/periodic_review_90d），
    # 二元判定只有 permanent（永不过期）和 task_bound（完成即删）。
    # 保留函数骨架供 --list-time-expired 参数兼容，但结果恒为空。
    ttl_thresholds: dict[str, int] = {}
    now = datetime.now()
    results = []
    for filepath, fm in _iter_md_files_with_frontmatter():
        ttl = fm.get("ttl", "")
        if ttl not in ttl_thresholds:
            continue
        stat = filepath.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        age_days = (now - mtime).days
        if age_days <= ttl_thresholds[ttl]:
            continue
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        results.append({
            "path": rel,
            "ttl": ttl,
            "mtime": mtime.strftime("%Y-%m-%d"),
            "age_days": age_days,
            "threshold_days": ttl_thresholds[ttl],
            "dir": str(filepath.parent.relative_to(REPO_ROOT)).replace("\\", "/"),
        })
    results.sort(key=lambda x: x["path"])
    return results


def list_all_non_permanent() -> list[dict]:
    """列出所有 ttl != permanent 的文件（一键扫描，含缺失 ttl 字段的文件）。

    用于人工判定清理清单。ttl 为空的文件也列出（强制要求 .md 全量有 ttl 后，
    缺失即违规，需补填）。

    Returns:
        [{path, ttl, mtime, age_days, dir}] 列表。
    """
    now = datetime.now()
    results = []
    for filepath, fm in _iter_md_files_with_frontmatter():
        ttl = fm.get("ttl", "")
        if ttl == "permanent":  # RENAME_REVIEW: 业务分支，词表改名时需人工复核
            continue
        stat = filepath.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        results.append({
            "path": rel,
            "ttl": ttl or "(缺失)",
            "mtime": mtime.strftime("%Y-%m-%d"),
            "age_days": (now - mtime).days,
            "dir": str(filepath.parent.relative_to(REPO_ROOT)).replace("\\", "/"),
        })
    results.sort(key=lambda x: x["path"])
    return results


def _print_table(results: list[dict], title: str) -> None:
    """表格输出到 stdout（中文宽度友好，便于 AI 后续解析）。"""
    print(f"\n{title}")
    print(f"共 {len(results)} 条记录")
    if not results:
        print("（无匹配文件）")
        return
    import unicodedata

    def _w(s: object) -> int:
        return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))

    cols = list(results[0].keys())
    widths = {c: max(_w(c), *(_w(str(r.get(c, ""))) for r in results)) for c in cols}

    def _pad(s: object, w: int) -> str:
        text = str(s)
        return text + " " * (w - _w(text))

    print("  ".join(_pad(c, widths[c]) for c in cols))
    print("-" * (sum(widths.values()) + 2 * (len(cols) - 1)))
    for r in results:
        print("  ".join(_pad(r.get(c, ""), widths[c]) for c in cols))


def main() -> None:
    """入口函数.

    模式：
      默认                    TTL/快照违规检测（阻断式，原行为）
      --list-by-ttl <value>   按 ttl 值列出文件清单（stdout 表格，exit 1 if 有结果）
      --list-time-expired     列出已到期文件（v2.0.0 废弃时间阈值，结果恒为空）
      --list-all-non-permanent  列出所有 ttl != permanent 的文件（一键扫描）
      --warn-only             警告模式（不阻断 exit 0）

    exit codes: 0=pass, 1=findings, 2=error
    """
    parser = argparse.ArgumentParser(description="文档 TTL 过期检测（GOV-DOC-006 §一/§三）+ ttl 扫描清单")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    parser.add_argument("--list-by-ttl", choices=sorted(VALID_TTL_VALUES),
                        help="按 ttl 值列出文件清单（不删除，仅输出 stdout）")
    parser.add_argument("--list-time-expired", action="store_true",
                        help="列出已到期文件（v2.0.0 废弃时间阈值，结果恒为空）")
    parser.add_argument("--list-all-non-permanent", action="store_true",
                        help="列出所有 ttl != permanent 的文件（一键扫描，含缺失 ttl 的文件）")
    args = parser.parse_args()

    # 扫描模式分支（只输出清单，不删除）
    try:
        if args.list_by_ttl:
            results = list_files_by_ttl(args.list_by_ttl)
            _print_table(results, f"ttl={args.list_by_ttl} 文件清单")
            sys.exit(EXIT_FINDINGS if results else EXIT_PASS)
        if args.list_time_expired:
            results = list_time_expired_files()
            _print_table(results, "时间到期文件清单（v2.0.0 废弃时间阈值，结果恒为空）")
            sys.exit(EXIT_FINDINGS if results else EXIT_PASS)
        if args.list_all_non_permanent:
            results = list_all_non_permanent()
            _print_table(results, "所有非 permanent 文件清单（含缺失 ttl）")
            sys.exit(EXIT_FINDINGS if results else EXIT_PASS)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # 默认模式：TTL/快照违规检测（原行为）
    ttl_findings = scan_ttl_violations()
    snapshot_findings = scan_dated_snapshots()
    all_findings = ttl_findings + snapshot_findings
    if all_findings:
        print(f"\n[DOC-TTL] {len(all_findings)} 个 TTL/快照违规:", file=sys.stderr)
        for f in all_findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    {f['detail']}", file=sys.stderr)
    else:
        print("[DOC-TTL] 文档 TTL 合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if all_findings else 0)


if __name__ == "__main__":
    main()
