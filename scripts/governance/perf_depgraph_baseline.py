# [BLUEPRINT]
# [MODULE] scripts.governance.perf_depgraph_baseline
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""
[BLUEPRINT] | scripts/governance/perf_depgraph_baseline.py | §1
[MODULE] scripts.governance.perf_depgraph_baseline
[INVARIANTS] 只读访问 depgraph.db（mode=ro）；禁止任何写操作；测试结果可重复
[MODIFY-GUARD] project_rules.md(RULE-SIXTEEN); scripts/governance/extract_depgraph.py
[CONSUMERS] 架构治理；性能回归监控；AI session 判断 depgraph 查询时效
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] DB不存在→exit 1; 查询失败→exit 2; 无表→exit 3
[TESTS] python scripts/governance/perf_depgraph_baseline.py --runs 3
[DOMAIN] D-GOVERNANCE

depgraph.db 查询性能基线测试（RULE-SIXTEEN 配套）

测试 depgraph.db 在万级节点规模下的查询延迟，建立性能基线供未来回归对比。
只读访问，不获取文件锁（只读连接不触发写锁）。

用法:
  python scripts/governance/perf_depgraph_baseline.py              # 默认 5 次取平均
  python scripts/governance/perf_depgraph_baseline.py --runs 10     # 指定运行次数
  python scripts/governance/perf_depgraph_baseline.py --output baseline.json  # 输出到文件
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sqlite3
import statistics
import sys
import time
from pathlib import Path

DEPGRAPH_PATH = Path("D:/ZephyrAlpha/data/databases/depgraph.db")


def _connect_ro(db_path: Path) -> sqlite3.Connection:
    """以只读模式连接 depgraph.db（避免触发写锁，支持并发测试）。"""
    if not db_path.exists():
        print(f"ERROR: depgraph.db not found at {db_path}", file=sys.stderr)
        sys.exit(1)
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _discover_tables(conn: sqlite3.Connection) -> list[str]:
    """自动发现所有表名。"""
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [r[0] for r in rows]


def _time_query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> float:
    """计时单次查询，返回秒数。"""
    start = time.perf_counter()
    conn.execute(sql, params).fetchall()
    return time.perf_counter() - start


def _run_scenario(conn: sqlite3.Connection, name: str, sql: str, params: tuple, runs: int) -> dict:
    """运行单个测试场景 N 次，返回统计结果。"""
    latencies: list[float] = []
    row_count = 0
    last_error = None
    for i in range(runs):
        try:
            start = time.perf_counter()
            cur = conn.execute(sql, params)
            rows = cur.fetchall()
            elapsed = time.perf_counter() - start
            latencies.append(elapsed)
            if i == 0:
                row_count = len(rows)
        except Exception as e:
            last_error = str(e)
            break
    if last_error:
        return {"scenario": name, "status": "ERROR", "error": last_error, "sql": sql}
    avg = statistics.mean(latencies) if latencies else 0.0
    med = statistics.median(latencies) if latencies else 0.0
    mn = min(latencies) if latencies else 0.0
    mx = max(latencies) if latencies else 0.0
    return {
        "scenario": name,
        "status": "OK",
        "row_count": row_count,
        "runs": runs,
        "avg_ms": round(avg * 1000, 3),
        "median_ms": round(med * 1000, 3),
        "min_ms": round(mn * 1000, 3),
        "max_ms": round(mx * 1000, 3),
        "sql": sql,
    }


def _explain_plan(conn: sqlite3.Connection, sql: str) -> list[str]:
    """获取查询计划，检查索引使用。捕获异常避免中断。"""
    try:
        rows = conn.execute(f"EXPLAIN QUERY PLAN {sql}").fetchall()
        return [r[3] for r in rows]
    except Exception as e:
        return [f"EXPLAIN ERROR: {e}"]


def run_baseline(db_path: Path, runs: int) -> dict:
    """运行完整性能基线测试。"""
    conn = _connect_ro(db_path)
    try:
        tables = _discover_tables(conn)

        # 基本统计
        node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        domain_count = conn.execute("SELECT COUNT(*) FROM domains").fetchone()[0]

        # 取一个真实 domain_id 用于按域过滤测试
        sample_domain = conn.execute("SELECT domain_id FROM domains ORDER BY rowid LIMIT 1").fetchone()[0]
        # 取一个真实 node_id 用于递归测试
        sample_node = conn.execute("SELECT node_id FROM nodes ORDER BY rowid LIMIT 1").fetchone()[0]

        scenarios: list[dict] = []

        # T1: 全表 COUNT nodes（基线扫描）
        scenarios.append(_run_scenario(conn, "T1_count_nodes", "SELECT COUNT(*) FROM nodes", (), runs))

        # T2: 全表 COUNT edges
        scenarios.append(_run_scenario(conn, "T2_count_edges", "SELECT COUNT(*) FROM edges", (), runs))

        # T3: 跨域 JOIN（nodes JOIN edges JOIN domains）— 核心测试
        scenarios.append(
            _run_scenario(
                conn,
                "T3_cross_domain_join",
                """SELECT n.domain_id AS from_domain, d2.domain_id AS to_domain, COUNT(*) AS edge_cnt
               FROM edges e
               JOIN nodes n ON e.from_node_id = n.node_id
               JOIN nodes n2 ON e.to_node_id = n2.node_id
               JOIN domains d2 ON n2.domain_id = d2.domain_id
               GROUP BY n.domain_id, d2.domain_id""",
                (),
                runs,
            )
        )

        # T4: 按域过滤节点
        scenarios.append(
            _run_scenario(
                conn, "T4_filter_by_domain", "SELECT * FROM nodes WHERE domain_id = ?", (sample_domain,), runs
            )
        )

        # T5: 节点出度统计（JOIN nodes + edges + GROUP BY）
        scenarios.append(
            _run_scenario(
                conn,
                "T5_outdegree_stats",
                """SELECT n.node_id, n.path, COUNT(e.edge_id) AS out_deg
               FROM nodes n LEFT JOIN edges e ON n.node_id = e.from_node_id
               GROUP BY n.node_id ORDER BY out_deg DESC LIMIT 50""",
                (),
                runs,
            )
        )

        # T6: 递归依赖路径（WITH RECURSIVE CTE，深度 5）
        scenarios.append(
            _run_scenario(
                conn,
                "T6_recursive_deps_depth5",
                """WITH RECURSIVE dep_chain AS (
                 SELECT from_node_id, to_node_id, 1 AS depth
                 FROM edges WHERE from_node_id = ?
                 UNION ALL
                 SELECT e.from_node_id, e.to_node_id, dc.depth + 1
                 FROM edges e JOIN dep_chain dc ON e.from_node_id = dc.to_node_id
                 WHERE dc.depth < 5
               )
               SELECT COUNT(*) FROM dep_chain""",
                (sample_node,),
                runs,
            )
        )

        # T7: 全量节点+域信息 JOIN
        scenarios.append(
            _run_scenario(
                conn,
                "T7_nodes_with_domain",
                """SELECT n.*, d.domain_name, d.layer_id
               FROM nodes n LEFT JOIN domains d ON n.domain_id = d.domain_id""",
                (),
                runs,
            )
        )

        # T8: 跨域依赖统计（仅跨域边）
        scenarios.append(
            _run_scenario(
                conn,
                "T8_cross_domain_edges_only",
                """SELECT COUNT(*) FROM edges e
               JOIN nodes n1 ON e.from_node_id = n1.node_id
               JOIN nodes n2 ON e.to_node_id = n2.node_id
               WHERE n1.domain_id != n2.domain_id""",
                (),
                runs,
            )
        )

        # 查询计划检查（T3 的索引使用情况）
        t3_plan = _explain_plan(conn, scenarios[2]["sql"])

        result = {
            "test_time": datetime.datetime.now().isoformat(),
            "db_path": str(db_path),
            "db_size_mb": round(os.path.getsize(db_path) / 1024 / 1024, 2),
            "tables": tables,
            "node_count": node_count,
            "edge_count": edge_count,
            "domain_count": domain_count,
            "sample_domain": sample_domain,
            "sample_node": sample_node,
            "runs_per_scenario": runs,
            "scenarios": scenarios,
            "t3_explain_plan": t3_plan,
        }
        return result
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="depgraph.db 查询性能基线测试（只读，万级节点跨域JOIN延迟）")
    parser.add_argument("--runs", type=int, default=5, help="每个场景运行次数（默认5）")
    parser.add_argument("--output", type=str, help="输出到 JSON 文件（默认 stdout）")
    args = parser.parse_args()

    if args.runs < 1:
        print("ERROR: --runs must be >= 1", file=sys.stderr)
        sys.exit(3)

    result = run_baseline(DEPGRAPH_PATH, args.runs)

    content = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        tmp = f"{args.output}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, args.output)
            print(f"Output written to: {args.output}", file=sys.stderr)
        except PermissionError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise
    else:
        print(content)

    # 控制台摘要
    print("\n=== 性能基线摘要 ===", file=sys.stderr)
    print(
        f"DB: {result['db_size_mb']}MB | nodes={result['node_count']} | edges={result['edge_count']} | domains={result['domain_count']}",
        file=sys.stderr,
    )
    print(f"{'场景':<30} {'行数':>8} {'平均ms':>10} {'中位ms':>10} {'最大ms':>10}", file=sys.stderr)
    print("-" * 75, file=sys.stderr)
    for s in result["scenarios"]:
        if s["status"] == "OK":
            print(
                f"{s['scenario']:<30} {s['row_count']:>8} {s['avg_ms']:>10.3f} {s['median_ms']:>10.3f} {s['max_ms']:>10.3f}",
                file=sys.stderr,
            )
        else:
            print(f"{s['scenario']:<30} {'ERR':>8} {s.get('error', '')}", file=sys.stderr)


if __name__ == "__main__":
    main()
