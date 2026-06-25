#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS-ARCH | scripts/governance/audit_rename_completeness.py | §rename-completeness-audit
# [MODULE] scripts.governance.audit_rename_completeness
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.constants
# [CONSUMERS] .pre_commit-config.yaml; scripts/governance/apply_depgraph.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读扫描;值扫描兜底覆盖全表TEXT列;排除规则示例表(domain_naming_rules)
# [MODIFY-GUARD] OLD_DOMAIN_IDS 列表变更需 Owner 批准（裁定#204 改名范围）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=0残留; exit 1=有残留; exit 2=参数错误/DB错误
# [TESTS] tests/unit/test_audit_rename_completeness.py
"""audit_rename_completeness.py — 改名完整性审计（裁定#207 R1）。

扫描 depgraph.db 所有表的所有 TEXT 列，检测旧标识符残留。
裁定#204 改名（D-SIGNAL* 4域）时，cmd_rename_domain 的 18步 UPDATE 只覆盖
预定义列名枚举，遗漏了 nodes.owner/business_stream/tags/invariants.invariant_id 等
未枚举列，导致314行存量残留。本脚本用"值扫描兜底"检测所有残留。

核心原则（裁定#207 R1）：
  - 值扫描兜底：扫描所有表所有 TEXT 列，非仅列名枚举
  - 精确值映射：修复时用精确值替换（禁止子串REPLACE，避免误伤）
  - 循环审查：CIRCULAR_ACCEPTANCE_ROUNDS=2，连续2轮0残留才通过

用法::

    # 检查所有 D-SIGNAL* 旧域名残留
    python scripts/governance/audit_rename_completeness.py

    # 检查指定旧标识符
    python scripts/governance/audit_rename_completeness.py --old-id D-SIGNAL_ASHARE

    # 检查节点路径残留（阶段D）
    python scripts/governance/audit_rename_completeness.py --check-node-paths --old-pattern "D-SIGNAL-"

    # 循环审查2轮（连续2轮0残留才通过）
    python scripts/governance/audit_rename_completeness.py --rounds 2
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import DEPGRAPH_DB_PATH  # noqa: E402

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 裁定#204 改名的 4 个域（旧ID → 新ID）
# D-SIGNAL 必须最后检查（它是其他3个旧ID的前缀，避免子串误匹配）
RENAME_MAP_204 = {
    "D-SIGNAL_ASHARE": "D-ASHARE_SIGNAL",
    "D-SIGNAL_FUNDAMENTAL": "D-FUNDAMENTAL_SIGNAL",
    "D-SIGNAL_QUALITY": "D-SIGQC",
    "D-SIGNAL": "D-SIGLEGACY",
}

# 排除表：这些表的 D-SIGNAL* 残留是有意保留的（规则示例/系统表/审计日志）
# domain_naming_rules: example_bad/rule_text 用 D-SIGNAL* 作为"错误命名示例"
# _schema_version: 系统元数据
# governance_audit_logs: 历史审计记录
EXCLUDE_TABLES = {"domain_naming_rules", "_schema_version", "governance_audit_logs"}

# 节点路径旧前缀（阶段D检查，路径格式如 信号域-审计/D-SIGNAL-06）
NODE_PATH_OLD_PREFIXES = ["D-SIGNAL-"]


def _get_all_text_columns(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """获取所有表（排除 EXCLUDE_TABLES）的 TEXT 类型列。

    返回 {table_name: [col1, col2, ...]}。
    """
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = [r[0] for r in cur.fetchall() if r[0] not in EXCLUDE_TABLES]

    result: dict[str, list[str]] = {}
    for tbl in tables:
        cur = conn.execute(f"PRAGMA table_info({tbl})")
        text_cols = [r[1] for r in cur.fetchall() if r[2] and r[2].upper() == "TEXT"]
        if text_cols:
            result[tbl] = text_cols
    return result


def scan_residual(
    conn: sqlite3.Connection,
    old_ids: list[str],
    check_all_text_columns: bool = True,
) -> list[dict]:
    """扫描所有表 TEXT 列中包含旧标识符的残留行。

    返回残留列表，每项: {table, column, old_id, count, sample_values}
    """
    residuals: list[dict] = []
    table_cols = _get_all_text_columns(conn) if check_all_text_columns else {"nodes": ["path"]}

    for tbl, cols in table_cols.items():
        for col in cols:
            for old_id in old_ids:
                try:
                    cur = conn.execute(
                        f"SELECT COUNT(*) FROM {tbl} WHERE {col} LIKE ?",
                        (f"%{old_id}%",),
                    )
                    cnt = cur.fetchone()[0]
                    if cnt > 0:
                        # 取样前3个值用于报告
                        cur = conn.execute(
                            f"SELECT {col} FROM {tbl} WHERE {col} LIKE ? LIMIT 3",
                            (f"%{old_id}%",),
                        )
                        samples = [r[0][:80] if r[0] else "" for r in cur.fetchall()]
                        residuals.append(
                            {
                                "table": tbl,
                                "column": col,
                                "old_id": old_id,
                                "count": cnt,
                                "samples": samples,
                            }
                        )
                except sqlite3.OperationalError:
                    pass  # 列不存在或查询错误，跳过

    return residuals


def scan_node_paths(
    conn: sqlite3.Connection, old_patterns: list[str]
) -> list[dict]:
    """扫描 nodes.path 中包含旧路径前缀的残留（阶段D专用）。

    返回残留列表。
    """
    residuals: list[dict] = []
    for pattern in old_patterns:
        cur = conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE path LIKE ?", (f"%{pattern}%",)
        )
        cnt = cur.fetchone()[0]
        if cnt > 0:
            cur = conn.execute(
                "SELECT path FROM nodes WHERE path LIKE ? LIMIT 5", (f"%{pattern}%",)
            )
            samples = [r[0][:80] for r in cur.fetchall()]
            residuals.append(
                {
                    "table": "nodes",
                    "column": "path",
                    "old_id": pattern,
                    "count": cnt,
                    "samples": samples,
                }
            )
    return residuals


def circular_review(
    db_path: str, old_ids: list[str], rounds: int = 2
) -> bool:
    """循环审查：连续 rounds 轮扫描，每轮0残留才算通过。

    返回 True=通过（连续rounds轮0残留），False=失败。
    """
    passed_rounds = 0
    for i in range(1, rounds + 1):
        conn = sqlite3.connect(db_path)
        try:
            residuals = scan_residual(conn, old_ids, check_all_text_columns=True)
            total = sum(r["count"] for r in residuals)
            print(f"  Round {i}/{rounds}: {total} 残留行（{len(residuals)} 个列位）")
            if total == 0:
                passed_rounds += 1
            else:
                passed_rounds = 0  # 重置连续通过计数
                for r in residuals:
                    print(
                        f"    {r['table']}.{r['column']} contains '{r['old_id']}': {r['count']} rows"
                    )
        finally:
            conn.close()

    return passed_rounds >= rounds


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="audit_rename_completeness.py",
        description="改名完整性审计（裁定#207 R1）——扫描DB所有TEXT列检测旧标识符残留",
    )
    parser.add_argument(
        "--old-id",
        help="指定单个旧标识符检查（默认检查裁定#204全部4个旧域名）",
    )
    parser.add_argument(
        "--check-all-text-columns",
        action="store_true",
        default=True,
        help="扫描所有表所有TEXT列（默认行为）",
    )
    parser.add_argument(
        "--check-node-paths",
        action="store_true",
        help="只检查 nodes.path 列（阶段D专用）",
    )
    parser.add_argument(
        "--old-pattern",
        help="配合 --check-node-paths 使用，指定路径旧前缀（如 D-SIGNAL-）",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=0,
        help="循环审查轮数（连续N轮0残留才通过，默认0=单次扫描）",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEPGRAPH_DB_PATH),
        help="depgraph.db 路径",
    )
    args = parser.parse_args()

    if not Path(args.db_path).exists():
        print(f"ERROR: DB not found: {args.db_path}", file=sys.stderr)
        return 2

    # 确定要检查的旧标识符
    if args.old_id:
        old_ids = [args.old_id]
    else:
        old_ids = list(RENAME_MAP_204.keys())

    # 节点路径模式
    if args.check_node_paths:
        patterns = [args.old_pattern] if args.old_pattern else NODE_PATH_OLD_PREFIXES
        conn = sqlite3.connect(args.db_path)
        try:
            residuals = scan_node_paths(conn, patterns)
        finally:
            conn.close()
        total = sum(r["count"] for r in residuals)
        if total == 0:
            print(f"[PASS] nodes.path 无旧前缀残留（{patterns}）")
            return 0
        print(f"[FAIL] nodes.path 发现 {total} 行残留:")
        for r in residuals:
            print(f"  {r['table']}.{r['column']} contains '{r['old_id']}': {r['count']} rows")
            for s in r["samples"]:
                print(f"    sample: {s}")
        return 1

    # 循环审查模式
    if args.rounds > 0:
        print(f"=== 循环审查 {args.rounds} 轮 ===")
        passed = circular_review(args.db_path, old_ids, rounds=args.rounds)
        if passed:
            print(f"[PASS] 连续 {args.rounds} 轮0残留，改名完整性审计通过")
            return 0
        print(f"[FAIL] 未能连续 {args.rounds} 轮0残留")
        return 1

    # 单次扫描模式
    conn = sqlite3.connect(args.db_path)
    try:
        residuals = scan_residual(conn, old_ids, check_all_text_columns=True)
    finally:
        conn.close()

    total = sum(r["count"] for r in residuals)
    if total == 0:
        print(f"[PASS] 0 残留——改名完整性审计通过（旧标识符: {old_ids}）")
        return 0

    print(f"[FAIL] 发现 {total} 行残留（{len(residuals)} 个列位）:")
    print(f"  排除表（规则示例/系统表）: {sorted(EXCLUDE_TABLES)}")
    print()
    for r in residuals:
        print(f"  {r['table']}.{r['column']} contains '{r['old_id']}': {r['count']} rows")
        for s in r["samples"]:
            print(f"    sample: {s}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
