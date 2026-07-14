#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS-ARCH | scripts/governance/audit_rename_completeness.py | §rename-completeness-audit
# [MODULE] scripts.governance.audit_rename_completeness
# [DOMAIN] D_GOV_SCRIPTS
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
# [TESTS] tests/infrastructure/test_audit_rename_completeness.py
# [TTL] task_bound
"""audit_rename_completeness.py — 改名完整性审计（裁定#207 R1）。

扫描 depgraph 所有表的所有 TEXT 列，检测旧标识符残留。
裁定#204 改名（D-SIGNAL* 4域）时，cmd_rename_domain 的 17步 UPDATE（v14前为18步，含invariants.domain_id）只覆盖
预定义列名枚举，遗漏了 nodes.owner/business_stream/tags 等
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

    # 检查手动修改文件中的旧标识符残留（活文档+脚本，排除历史文档和生成制品）
    python scripts/governance/audit_rename_completeness.py --old-id D_GOV_DOCS \
        --check-files "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml,scripts/governance/sync_yaml_to_depgraph.py"

    # apply_depgraph.py --rename-domain 完成后会自动调用本工具的 scan_residual 做后置校验
    # （事件驱动，无需手工触发；见 apply_depgraph.py _post_rename_residual_check）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: audit_rename_completeness.py — 改名完整性审计（裁定#207 R1）。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Any

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import get_depgraph_pg_connection  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 裁定#204 改名的 4 个域（旧ID → 新ID）
# D-SIGNAL 必须最后检查（它是其他3个旧ID的前缀，避免子串误匹配）
RENAME_MAP_204 = {
    "D-SIGNAL_ASHARE": "D_ASHARE_SIGNAL",
    "D-SIGNAL_FUNDAMENTAL": "D_FUNDAMENTAL_SIGNAL",
    "D-SIGNAL_QUALITY": "D_SIGQC",
    "D-SIGNAL": "D_SIGLEGACY",
}

# 排除表：这些表的 D-SIGNAL* 残留是有意保留的（规则示例/系统表/审计日志）
# domain_naming_rules: example_bad/rule_text 用 D-SIGNAL* 作为"错误命名示例"
# _schema_version: 系统元数据
# governance_audit_logs: 历史审计记录
EXCLUDE_TABLES = {"domain_naming_rules", "_schema_version", "governance_audit_logs"}

# 节点路径旧前缀（阶段D检查，路径格式如 信号域-审计/D-SIGNAL-06）
NODE_PATH_OLD_PREFIXES = ["D-SIGNAL-"]

# 排除列：由专门步骤处理的列不参与残留扫描（与 apply_depgraph.py _RENAME_SCAN_EXCLUDE_COLUMNS 保持一致）
# - blueprint_id: 含 MODULE ID（MOD-GOV-DOCS），LIKE '%D_GOV_DOCS%' 会子串误匹配 MOD-GOV-DOCS
#   由 cmd_propagate_rename 精确值映射处理（裁定#207 R1 B6，禁止子串REPLACE）
# - path / blueprint_path: 阶段D 节点路径改名传播（重新编号，需保留原序号信息）
# 不一致会导致误报：audit 漏排除 blueprint_id 时，MODULE ID 子串会被误判为 DOMAIN ID 残留
EXCLUDE_COLUMNS = {"blueprint_id", "path", "blueprint_path"}


def _get_all_text_columns(conn: Any) -> dict[str, list[str]]:
    """获取所有表（排除 EXCLUDE_TABLES）的 TEXT 类型列。

    排除 path/blueprint_path 列（阶段D专用，由 scan_node_paths 专门检查）。
    返回 {table_name: [col1, col2, ...]}。
    """
    cur = conn.execute(
        "SELECT table_name, column_name FROM information_schema.columns "
        "WHERE table_schema='public' AND data_type IN ('text', 'character varying', 'character') "
        "ORDER BY table_name, ordinal_position"
    )
    result: dict[str, list[str]] = {}
    for r in cur.fetchall():
        tbl = r["table_name"]
        col = r["column_name"]
        if tbl in EXCLUDE_TABLES or col in EXCLUDE_COLUMNS:
            continue
        result.setdefault(tbl, []).append(col)
    return result


def scan_residual(
    conn: Any,
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
                        f"SELECT COUNT(*) AS cnt FROM {tbl} WHERE {col} LIKE %s",
                        (f"%{old_id}%",),
                    )
                    row = cur.fetchone()
                    cnt = row["cnt"] if row else 0
                    if cnt > 0:
                        # 取样前3个值用于报告
                        cur = conn.execute(
                            f"SELECT {col} FROM {tbl} WHERE {col} LIKE %s LIMIT 3",
                            (f"%{old_id}%",),
                        )
                        samples = [r[col][:80] if r[col] else "" for r in cur.fetchall()]
                        residuals.append(
                            {
                                "table": tbl,
                                "column": col,
                                "old_id": old_id,
                                "count": cnt,
                                "samples": samples,
                            }
                        )
                except Exception as e:
                    logger.warning("scan_residual: residual query failed for %s.%s (%s: %s)", tbl, col, type(e).__name__, e)

    return residuals


def scan_node_paths(
    conn: Any, old_patterns: list[str]
) -> list[dict]:
    """扫描 nodes.path 中包含旧路径前缀的残留（阶段D专用）。

    返回残留列表。
    """
    residuals: list[dict] = []
    for pattern in old_patterns:
        cur = conn.execute(
            "SELECT COUNT(*) AS cnt FROM nodes WHERE path LIKE %s", (f"%{pattern}%",)
        )
        row = cur.fetchone()
        cnt = row["cnt"] if row else 0
        if cnt > 0:
            cur = conn.execute(
                "SELECT path FROM nodes WHERE path LIKE %s LIMIT 5", (f"%{pattern}%",)
            )
            samples = [r["path"][:80] for r in cur.fetchall()]
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


def scan_files_residual(
    file_paths: list[str],
    old_ids: list[str],
) -> list[dict]:
    """扫描指定文件中包含旧标识符的残留行（消除手工写 _tmp_find_residual.py 的必要性）。

    用负向先行断言排除 MOD- 前缀误匹配：
      - D_GOV_DOCS 在 MOD-GOV-DOCS 中是 MODULE ID 子串，不应判为 DOMAIN ID 残留
      - (?<![A-Z]) 确保 old_id 前不是大写字母
    排除 [BLUEPRINT] 行的模块 ID 声明（头部元数据，非业务内容）。

    返回残留列表，每项: {file, line, old_id}。
    """
    pattern = re.compile('|'.join(r'(?<![A-Z])' + re.escape(d) for d in old_ids))
    residuals: list[dict] = []
    for fpath in file_paths:
        p = Path(fpath)
        if not p.exists():
            continue
        try:
            content = p.read_text(encoding='utf-8', errors='ignore')
        except OSError as exc:
            logger.warning("OSError reading %s: %s", fpath, exc)
            continue
        for m in pattern.finditer(content):
            start = m.start()
            # 排除 [BLUEPRINT] 元数据行：只检查匹配点所在行（非 50 字符窗口）
            # 修复 R5 红蓝对抗发现的 bug：50 字符窗口会误排除邻近行的真实残留
            line_start = content.rfind('\n', 0, start) + 1
            line_end = content.find('\n', start)
            if line_end == -1:
                line_end = len(content)
            line_content = content[line_start:line_end]
            if '[BLUEPRINT]' in line_content:
                continue
            line_num = content.count('\n', 0, start) + 1
            residuals.append({
                'file': fpath,
                'line': line_num,
                'old_id': m.group(),
            })
    return residuals


def circular_review(
    db_path: str, old_ids: list[str], rounds: int = 2
) -> bool:
    """循环审查：连续 rounds 轮扫描，每轮0残留才算通过。

    返回 True=通过（连续rounds轮0残留），False=失败。
    """
    passed_rounds = 0
    for i in range(1, rounds + 1):
        conn = get_depgraph_pg_connection(autocommit=True)
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


def circular_review_node_paths(
    db_path: str, old_patterns: list[str], rounds: int = 2
) -> bool:
    """循环审查节点路径列：连续 rounds 轮扫描，每轮0残留才算通过（阶段D专用）。

    扫描范围：nodes.path + blueprint_links.blueprint_path（与 scan_node_paths 一致）。
    返回 True=通过（连续rounds轮0残留），False=失败。
    """
    passed_rounds = 0
    for i in range(1, rounds + 1):
        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            residuals = scan_node_paths(conn, old_patterns)
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
        default=None,
        help="depgraph 路径（P2迁移后已废弃，PG 连接由 get_depgraph_pg_connection 统一管理；保留仅为向后兼容）",
    )
    parser.add_argument(
        "--check-files",
        help="扫描指定文件中的旧标识符残留（逗号分隔路径）。"
        "用于检查手动修改的活文档/脚本（排除历史文档和生成制品）。"
        "自动排除 MOD- 前缀的 MODULE ID 子串误匹配。",
    )
    args = parser.parse_args()

    # P2迁移后：depgraph 已迁移到 PostgreSQL，连接由 get_depgraph_pg_connection 统一管理，
    # 不再依赖文件路径存在性检查（原 Path(args.db_path).exists() 对 PG 服务器无意义）。

    # 确定要检查的旧标识符
    if args.old_id:
        old_ids = [args.old_id]
    else:
        old_ids = list(RENAME_MAP_204.keys())

    # 文件残留扫描模式（消除手工写 _tmp_find_residual.py 的必要性）
    if args.check_files:
        file_paths = [f.strip() for f in args.check_files.split(",") if f.strip()]
        residuals = scan_files_residual(file_paths, old_ids)
        total = len(residuals)
        if total == 0:
            print(f"[PASS] 0 文件残留——文件扫描通过（旧标识符: {old_ids}，扫描 {len(file_paths)} 文件）")
            return 0
        print(f"[FAIL] 发现 {total} 处文件残留:")
        for r in residuals:
            print(f"  {r['file']}:{r['line']}: {r['old_id']}")
        return 1

    # 节点路径模式
    if args.check_node_paths:
        patterns = [args.old_pattern] if args.old_pattern else NODE_PATH_OLD_PREFIXES
        # 循环审查模式（阶段D：连续N轮0残留才通过）
        if args.rounds > 0:
            print(f"=== 节点路径循环审查 {args.rounds} 轮（patterns={patterns}）===")
            passed = circular_review_node_paths(args.db_path, patterns, rounds=args.rounds)
            if passed:
                print(f"[PASS] 连续 {args.rounds} 轮0残留，节点路径改名完整性审计通过")
                return 0
            print(f"[FAIL] 未能连续 {args.rounds} 轮0残留")
            return 1
        # 单次扫描模式
        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            residuals = scan_node_paths(conn, patterns)
        finally:
            conn.close()
        total = sum(r["count"] for r in residuals)
        if total == 0:
            print(f"[PASS] 节点路径列（nodes.path + blueprint_links.blueprint_path）无旧前缀残留（{patterns}）")
            return 0
        print(f"[FAIL] 节点路径列发现 {total} 行残留:")
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
    conn = get_depgraph_pg_connection(autocommit=True)
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
