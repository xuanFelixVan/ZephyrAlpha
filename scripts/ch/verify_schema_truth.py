# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c3_fundamental_clickhouse.md
# [MODULE] scripts.ch.verify_schema_truth
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(pip); schemas.categories.*
# [CONSUMERS] apply_market_tables_ddl; apply_fundamental_tables_ddl; 人工审查
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 对比 schemas/categories/*.py 的 DDL-as-Code 真源与 ClickHouse 实际表结构；发现列/类型/引擎/排序键漂移即报告；只读 SELECT 不改 DB
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 真源文件import失败->WARN跳过; 发现漂移->退出码1; 零漂移->退出码0
# [TESTS] python scripts/ch/verify_schema_truth.py (smoke: 全量真源 vs DB 漂移报告)
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DDL-as-Code 真源 vs ClickHouse 实际表结构 漂移校验器（治本工具）。

病根（第一性原理，#ARCH-CH-025 Schema 真源体系收口）：
    audit_01 实测 101 张表中 87 张"无代码侧真源（仅存在于 CH 实例）"。
    P0-8 八表迁移等变更直接 ALTER 了 DB 却未回写 schemas/categories/ 真源，
    制造"DB 改了、真源没改"的漂移债务——100% AI 开发场景下 AI 无法可靠维护
    不在代码里的 schema，是幻觉/漂移根源。

治本：
    本脚本对比 schemas/categories/*.py 的 *_DDL 真源与 system.tables/system.columns，
    把"DB vs 真源"漂移全量暴露。零漂移=退出码0；有漂移=退出码1（可接入 CI 门禁）。

用法：
    python scripts/ch/verify_schema_truth.py                # 全量校验，打印报告
    python scripts/ch/verify_schema_truth.py --table NAME   # 只校验指定表
    python scripts/ch/verify_schema_truth.py --quiet        # 只输出摘要
    python scripts/ch/verify_schema_truth.py --output PATH  # 额外把报告写到 markdown 文件
    python scripts/ch/verify_schema_truth.py --ci           # CI 门禁模式（CH 不可达不阻断，有漂移才阻断）

CI 模式语义（接入 pre-commit 门禁用）：
    - 零漂移      → exit 0（通过）
    - 有漂移      → exit 1（阻断提交）
    - CH 不可达    → exit 0 + 显式 WARN（不阻断无关提交；防止本地基建故障卡死所有工作）
    非 --ci 模式下 CH 不可达仍返回 exit 2（便于人工诊断时区分"基建故障"与"通过"）。
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent
_SRC_DIR = _REPO_ROOT / "src"
_SCHEMA_DIR = _REPO_ROOT / "schemas" / "categories"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


# ==================== 真源加载 ====================


def _discover_truth_files() -> list[Path]:
    """枚举 schemas/categories/*.py 真源文件。"""
    return sorted(_SCHEMA_DIR.glob("*.py"))


def _load_module(path: Path):
    """按文件路径加载真源模块（避免包导入副作用）。"""
    name = f"_truth_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _find_ddl_constant(mod) -> str | None:
    """在模块中找 *_DDL 字符串常量（每文件恰好一个）。"""
    for attr in dir(mod):
        if attr.endswith("_DDL"):
            val = getattr(mod, attr)
            if isinstance(val, str) and "CREATE TABLE" in val:
                return val
    return None


# ==================== DDL 解析 ====================


def _split_top_level(s: str, sep: str = ",") -> list[str]:
    """按 sep 切分，忽略括号内嵌套的 sep。"""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def _norm(s: str | None) -> str:
    """类型/键表达式归一化：去所有空白，便于跨来源比对。"""
    if not s:
        return ""
    return re.sub(r"\s+", "", s).strip("`")


def _engine_token(engine_full: str) -> str:
    """从 engine_full 提取引擎词（含版本列），截断于第一个顶层空白。

    engine_full 形如 'ReplacingMergeTree(ingest_ts) PARTITION BY ... SETTINGS ...'，
    只取 'ReplacingMergeTree(ingest_ts)' 部分。
    """
    depth, chars = 0, []
    for ch in engine_full.strip():
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and ch.isspace():
            break
        chars.append(ch)
    return "".join(chars)


def _norm_key(expr: str | None) -> str:
    """排序键/分区键归一化：去空白 + 去外层括号（DB sorting_key 无括号，真源 DDL 有括号）。"""
    n = _norm(expr)
    if n.startswith("(") and n.endswith(")"):
        n = n[1:-1]
    return n


def _parse_column_def(seg: str) -> tuple[str, str] | None:
    """解析单列定义 -> (name, type)；跳过 INDEX/CONSTRAINT 行。

    注意：关键字后必须跟空白或括号，避免把 ``index_code`` 等以 INDEX/CONSTRAINT/CHECK
    开头的列名误判为约束行（Wave 2 #ARCH-CH-025 修复）。
    """
    seg = seg.strip()
    if not seg:
        return None
    if re.match(r"^(INDEX|CONSTRAINT|CHECK)(\s|\()", seg, re.IGNORECASE):
        return None
    # name = 第一个 token（去反引号）
    m = re.match(r"^`?(\w+)`?\s+(.+)$", seg, re.DOTALL)
    if not m:
        return None
    name = m.group(1)
    rest = m.group(2).strip()
    # type = rest 中第一个顶层 DEFAULT/MATERIALIZED/ALIAS/COMMENT 之前的部分
    # MATERIALIZED/ALIAS 是列修饰符（与 DEFAULT 同级），不属于数据类型；
    # DB system.columns.type 只存纯类型（如 LowCardinality(String)），不含 MATERIALIZED 子句，
    # 故解析真源 DDL 时也须在 MATERIALIZED/ALIAS 处截断，否则类型比对会误报漂移。
    # （TRAE-082 1.1.0 #ARCH-DATA-SYMBOL-002：exchange/symbol_canonical 为 MATERIALIZED 列）
    depth, type_chars, i = 0, [], 0
    upper = rest.upper()
    while i < len(rest):
        ch = rest[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and upper[i : i + 7] == "DEFAULT":
            break
        if depth == 0 and upper[i : i + 12] == "MATERIALIZED":
            break
        if depth == 0 and upper[i : i + 5] == "ALIAS" and (i == 0 or not (rest[i - 1].isalnum() or rest[i - 1] == "_")):
            break
        if depth == 0 and upper[i : i + 7] == "COMMENT":
            break
        type_chars.append(ch)
        i += 1
    return name, "".join(type_chars).strip()


def _parse_truth_table(ddl: str) -> dict:
    """解析 DDL 真源字符串 -> {db, table, columns, engine, partition, order}。"""
    # database.table
    m = re.search(r"CREATE TABLE(?:\s+IF NOT EXISTS)?\s+(\w+)\.(\w+)", ddl, re.IGNORECASE)
    db, table = (m.group(1), m.group(2)) if m else ("", "")
    # 列块（最外层括号）
    cols: dict[str, str] = {}
    bm = re.search(r"\((.*)\)\s*ENGINE", ddl, re.DOTALL | re.IGNORECASE)
    if bm:
        for seg in _split_top_level(bm.group(1)):
            parsed = _parse_column_def(seg)
            if parsed:
                cols[parsed[0]] = parsed[1]
    em = re.search(r"ENGINE\s*=\s*([^\n]+)", ddl, re.IGNORECASE)
    engine = em.group(1).strip() if em else ""
    pm = re.search(r"PARTITION\s+BY\s+([^\n]+)", ddl, re.IGNORECASE)
    partition = pm.group(1).strip() if pm else ""
    om = re.search(r"ORDER\s+BY\s+([^\n]+)", ddl, re.IGNORECASE)
    order = om.group(1).strip() if om else ""
    return {"db": db, "table": table, "columns": cols, "engine": engine, "partition": partition, "order": order}


def _load_truth_schemas() -> list[dict]:
    """加载所有真源文件 -> 真源表清单。"""
    truths: list[dict] = []
    for path in _discover_truth_files():
        try:
            mod = _load_module(path)
            ddl = _find_ddl_constant(mod)
            if not ddl:
                continue
            t = _parse_truth_table(ddl)
            t["source_file"] = path.name
            truths.append(t)
        except Exception as e:  # noqa: BLE001 — 单文件失败不阻断全量校验
            print(f"[WARN] 真源 {path.name} 导入失败: {e}")
    return truths


# ==================== DB 加载 ====================


def _make_client():
    """构建只读 ClickHouse 客户端（过滤 native driver 不支持的键）。"""
    import clickhouse_driver

    from zephyr.data.ch_config import load_ch_reader_config

    c = load_ch_reader_config()
    return clickhouse_driver.Client(
        host=c["host"],
        port=int(c["port"]),
        user=c["user"],
        password=c["password"],
        database=c["database"],
    )


def _load_db_schema(client, db: str, table: str) -> dict | None:
    """查 CH 实际表结构 -> {columns, engine, engine_full, partition, order} 或 None。"""
    exists = client.execute(
        "SELECT name, engine, engine_full, partition_key, sorting_key "
        "FROM system.tables WHERE database='{d}' AND name='{t}'".format(d=db, t=table)
    )
    if not exists:
        return None
    row = exists[0]
    cols_rows = client.execute(
        "SELECT name, type FROM system.columns WHERE database='{d}' AND table='{t}' ORDER BY position".format(
            d=db, t=table
        )
    )
    return {
        "columns": {r[0]: r[1] for r in cols_rows},
        "engine": row[1],
        "engine_full": row[2],
        "partition": row[3] or "",
        "order": row[4] or "",
    }


# ==================== 比对 ====================


def _compare(truth: dict, db: dict | None) -> list[str]:
    """返回该表的漂移条目列表（空=零漂移）。"""
    drifts: list[str] = []
    table = truth["table"]
    if db is None:
        return [f"[{table}] 真源有定义但 DB 中不存在（{truth['db']}.{table}）"]
    # 列集合
    t_cols, d_cols = set(truth["columns"]), set(db["columns"])
    for c in sorted(t_cols - d_cols):
        drifts.append(f"[{table}] 列 '{c}' 真源有但 DB 无")
    for c in sorted(d_cols - t_cols):
        drifts.append(f"[{table}] 列 '{c}' DB 有但真源无")
    # 列类型
    for c in sorted(t_cols & d_cols):
        if _norm(truth["columns"][c]) != _norm(db["columns"][c]):
            drifts.append(f"[{table}] 列 '{c}' 类型漂移: 真源={truth['columns'][c]} vs DB={db['columns'][c]}")
    # 引擎（用 engine_full 提取引擎词比对，含版本列）
    db_engine_tok = _engine_token(db["engine_full"]) or db["engine"]
    if _norm(truth["engine"]) != _norm(db_engine_tok):
        drifts.append(f"[{table}] 引擎漂移: 真源={truth['engine']} vs DB={db_engine_tok}")
    # 排序键
    if _norm_key(truth["order"]) and _norm_key(truth["order"]) != _norm_key(db["order"]):
        drifts.append(f"[{table}] 排序键漂移: 真源={truth['order']} vs DB={db['order']}")
    return drifts


# ==================== 主流程 ====================


def _write_markdown_report(
    path: Path,
    per_table: list[tuple[dict, list[str]]],
    all_drifts: list[str],
) -> None:
    """把校验结果写到 markdown 报告（供 CI/审计留证）。

    Args:
        path: 报告输出路径
        per_table: [(truth_dict, drifts), ...] 每表结果
        all_drifts: 全量漂移条目（用于明细）
    """
    import datetime as _dt

    checked = len(per_table)
    lines = [
        "---",
        "ttl: task_bound",
        "---",
        "# Schema Truth Drift Report",
        "",
        f"- 生成时间: {_dt.datetime.now(_dt.timezone.utc).isoformat()}",
        f"- 校验表数: {checked}",
        f"- 漂移条目: {len(all_drifts)}",
        f"- 退出码: {'1 (有漂移)' if all_drifts else '0 (零漂移)'}",
        "",
        "## 逐表结果",
        "",
        "| 状态 | 库.表 | 真源文件 |",
        "|------|-------|----------|",
    ]
    for t, drifts in per_table:
        status = "DRIFT" if drifts else "OK"
        lines.append(f"| {status} | {t['db']}.{t['table']} | {t['source_file']} |")
    lines.extend(["", "## 漂移明细", ""])
    if all_drifts:
        for d in all_drifts:
            lines.append(f"- {d}")
    else:
        lines.append("零漂移：所有 DDL-as-Code 真源与 ClickHouse 实际表结构一致。")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="DDL-as-Code 真源 vs DB 漂移校验")
    ap.add_argument("--table", help="只校验指定表名")
    ap.add_argument("--quiet", action="store_true", help="只输出摘要")
    ap.add_argument("--output", help="把 markdown 报告写到指定路径")
    ap.add_argument(
        "--ci",
        action="store_true",
        help="CI 门禁模式：CH 不可达不阻断（exit 0 + WARN），有漂移才阻断（exit 1）",
    )
    args = ap.parse_args()

    truths = _load_truth_schemas()
    if args.table:
        truths = [t for t in truths if t["table"] == args.table]
    if not truths:
        print("未发现任何 DDL 真源文件")
        return 2

    try:
        client = _make_client()
    except Exception as e:  # noqa: BLE001
        if args.ci:
            # CI 模式：基建故障不阻断无关提交（漂移检测本身无法运行，但不卡工作流）
            print(f"[WARN] GATE-SCHEMA-TRUTH 跳过：ClickHouse 连接失败（{e}）")
            print("[WARN] 请在 CH 恢复后手动运行 verify_schema_truth.py 确认零漂移")
            return 0
        print(f"[ERROR] ClickHouse 连接失败: {e}")
        return 2

    all_drifts: list[str] = []
    per_table: list[tuple[dict, list[str]]] = []
    for t in truths:
        db = _load_db_schema(client, t["db"], t["table"])
        drifts = _compare(t, db)
        per_table.append((t, drifts))
        status = "OK" if not drifts else "DRIFT"
        if not args.quiet or drifts:
            print(f"  {status:5s} {t['db']}.{t['table']:30s} <- {t['source_file']}")
        all_drifts.extend(drifts)

    checked = len(per_table)
    print(f"\n校验 {checked} 张表真源，发现 {len(all_drifts)} 处漂移。")
    if all_drifts:
        print("\n=== 漂移明细 ===")
        for d in all_drifts:
            print(f"  - {d}")
    else:
        print("零漂移：所有 DDL-as-Code 真源与 ClickHouse 实际表结构一致。")

    if args.output:
        _write_markdown_report(Path(args.output), per_table, all_drifts)
        print(f"\n报告已写入: {args.output}")

    return 1 if all_drifts else 0


if __name__ == "__main__":
    sys.exit(main())
