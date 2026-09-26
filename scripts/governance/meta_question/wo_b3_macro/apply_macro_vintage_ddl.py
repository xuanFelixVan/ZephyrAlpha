# [BLUEPRINT] MOD-CHAINPILE-METAQ | 工单 WO-B3 §簇3-2/3（vintage schema 落地：建新表+视图兼容层，零 ALTER 业务表）
# [MODULE] scripts.governance.meta_question.wo_b3_macro.apply_macro_vintage_ddl
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta_question.wo_b3_macro.macro_vintage（DDL 真源常量）;
#                 zephyr.data.ch_writer.get_client_strict（CH 写通道，禁裸 Client/duckdb）
# [CONSUMERS] 手工运维部署；audit_macro_vintage.py（依赖本件建成的表/视图）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] DDL-as-Code：全部语句 CREATE ... IF NOT EXISTS / CREATE OR REPLACE VIEW，幂等可重跑；
#              时间列一律 DateTime64(3,'UTC')、发布时戳 Nullable（RULE-SCHEMA-TZ + 零伪造历史 pub_ts）；
#              对业务现值表 c1_market.macro_data 零 ALTER 零 UPDATE（只新增并行表与视图）；
#              --verify 只读，输出"载体建成"机械判据三元组（存在性/字段齐备度/结构可存证性）。
# [MODIFY-GUARD] none（新建文件；本件不改任何既有文件）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达->ch_writer 抛 RuntimeError 退出码 2；DDL 单语句失败->打印语句+退出码 1；
#                  --verify 缺件->退出码 3 并列缺失清单。
# [TESTS] python scripts/governance/meta_question/wo_b3_macro/apply_macro_vintage_ddl.py --verify
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=script | stability=new | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""部署/核验宏观数据 vintage 存证 schema（c1_market.macro_data_vintage + 三视图）。

用法::

    python scripts/governance/meta_question/wo_b3_macro/apply_macro_vintage_ddl.py           # 幂等部署
    python scripts/governance/meta_question/wo_b3_macro/apply_macro_vintage_ddl.py --verify   # 只核验不部署
    ... --structure-proof                                                                   # PQ-0191 结构证明

"载体建成"机械判据（本件 --verify 输出）：
  V1 表存在 & 7 个存证字段齐备（vintage/pub_ts/pub_ts_basis/source_series_id/pub_ref/first_seen_ts/ingest_ts）
  V2 排序键含 vintage（同键多版可共存）且现值表排序键不含 vintage（现值表不可共存=旧机制证明）
  V3 视图齐备（latest/compat，PIT 视图按 CH 参数支持度记录可用性）
  V4 pub_ts 类型=Nullable(DateTime64(3,'UTC'))（时区显式 + 不可知可表达）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Final

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))  # 同目录 macro_vintage.py（落地件=src/zephyr/data/macro_vintage.py）
sys.path.insert(0, str(_HERE.parents[4] / "src"))

import macro_vintage as mv  # noqa: E402

_EVIDENCE_TABLE: Final = "c1_market.macro_data"

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。mv.TABLE_VINTAGE 为模块常量、import 期解析；
# _SQL_SORTING_KEY 的 database/name 为运行期入参（表名拆分），以 %s 占位由调用处传入。
_SQL_SORTING_KEY = "SELECT sorting_key FROM system.tables WHERE database='%s' AND name='%s'"
_SQL_VIEWS = "SELECT name FROM system.tables WHERE database='c1_market' AND engine='View'"
_SQL_LEGACY_ENGINE = "SELECT engine FROM system.tables WHERE database='c1_market' AND name='macro_data'"
_SQL_ROW_COUNT = f"SELECT count() FROM {mv.TABLE_VINTAGE}"


def _statements() -> list[tuple[str, str]]:
    return list(mv.DDL_STATEMENTS)


def _client():
    from zephyr.data import ch_writer

    return ch_writer.get_client_strict()


def apply_ddl() -> int:
    client = _client()
    failed = 0
    for label, sql in _statements():
        try:
            client.execute(sql)
            print(f"[ok] {label}")
        except Exception as exc:  # noqa: BLE001 — 单语句失败不阻断其余语句（幂等重跑即恢复）
            failed += 1
            print(f"[fail] {label}: {type(exc).__name__}: {str(exc)[:200]}")
    client.disconnect()
    return 1 if failed else 0


def _columns(client, table: str) -> dict[str, str]:
    return {str(r[0]): str(r[1]) for r in client.execute(f"DESCRIBE TABLE {table}")}


def _sorting_key(client, table: str) -> str:
    db, _, name = table.partition(".")
    # 值来源=模块常量（表名），非外部输入；CH 驱动查询参数在此链路不可用（Code 62/未替换）
    rows = client.execute(_SQL_SORTING_KEY % (db, name))
    return str(rows[0][0]) if rows else ""


def verify() -> int:
    client = _client()
    missing: list[str] = []
    report: dict[str, Any] = {}
    cols = _columns(client, mv.TABLE_VINTAGE)
    need = {c for c in mv.ALL_COLUMNS} | {"report_date", "indicator_name", "indicator_value"}
    absent = sorted(need - set(cols))
    report["v1_columns"] = {"total": len(cols), "absent": absent}
    if absent:
        missing.append(f"vintage 表缺列 {absent}")
    report["v2_sorting_key_vintage"] = _sorting_key(client, mv.TABLE_VINTAGE)
    if "vintage" not in report["v2_sorting_key_vintage"]:
        missing.append("排序键未含 vintage（同键多版无法共存）")
    report["v2_sorting_key_legacy"] = _sorting_key(client, _EVIDENCE_TABLE)
    if "vintage" in report["v2_sorting_key_legacy"]:
        missing.append("现值表被改结构（本工单要求零 ALTER）")
    views = {str(r[0]) for r in client.execute(_SQL_VIEWS)}
    report["v3_views"] = sorted(views & {"macro_data_latest", "macro_data_compat"})
    for v in ("macro_data_latest", "macro_data_compat"):
        if v not in views:
            missing.append(f"视图缺失 {v}")
    if "macro_data_pit_view" in views:
        missing.append("残留不可查参数化视图 macro_data_pit_view（应已清理，PIT 走 pit_latest()）")
    report["v3_pit_view_dropped"] = "macro_data_pit_view" not in views
    pt = cols.get("pub_ts", "")
    report["v4_pub_ts_type"] = pt
    if not (pt.startswith("Nullable(DateTime64(3") and "'UTC'" in pt):
        missing.append(f"pub_ts 类型不合规：{pt}")
    basis = cols.get("pub_ts_basis", "")
    report["v4_pub_ts_basis_type"] = basis
    report["row_count"] = int(client.execute(_SQL_ROW_COUNT)[0][0])
    client.disconnect()
    print(__import__("json").dumps(report, ensure_ascii=False, indent=1))
    if missing:
        print("[VERIFY-FAIL] " + "；".join(missing))
        return 3
    print(
        "[VERIFY-OK] vintage 存证载体字段齐备度 "
        f"{len(need)}/{len(need)}，排序键={report['v2_sorting_key_vintage']}，行数={report['row_count']}"
    )
    return 0


def structure_proof() -> int:
    """PQ-0191 实证：值冲突组=0 只证回补幂等，不构成分版存证（结构层面判死）。"""
    client = _client()
    legacy_key = _sorting_key(client, _EVIDENCE_TABLE)
    legacy_engine = client.execute(_SQL_LEGACY_ENGINE)[0][0]
    vintage_key = _sorting_key(client, mv.TABLE_VINTAGE)
    client.disconnect()
    print("PQ-0191 结构证明（可复算，只读）：")
    print(f"  现值表 {_EVIDENCE_TABLE}: engine={legacy_engine} sorting_key=({legacy_key})")
    print("    → 主键不含版次：同 (indicator_name, report_date) 的修订值与初值在 ReplacingMergeTree 合并时")
    print("      互相覆盖，最终只剩一行。故『值冲突组=0』=重复灌同一终值的幂等结果（回补脚本不产生冲突），")
    print("      与『每个观测值有发布时戳、修订前后两版共存』是两件事——后者才叫发布时戳存证。")
    print(f"  存证表 {mv.TABLE_VINTAGE}: sorting_key=({vintage_key})")
    print("    → 版次入主键后同键多版共存，PIT 取数（pub_ts<=as_of 取最新）才有对象可查。")
    print("  结论：冲突扫描判据不可迁移为 pub_ts 存证判据；两判据分别由 PQ-0191/PQ-0185 独立复考。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="宏观 vintage 存证 schema 部署/核验")
    parser.add_argument("--verify", action="store_true", help="只核验不部署")
    parser.add_argument("--structure-proof", action="store_true", help="输出 PQ-0191 结构证明")
    args = parser.parse_args(argv)
    if args.verify:
        return verify()
    if args.structure_proof:
        return structure_proof()
    return apply_ddl()


if __name__ == "__main__":
    raise SystemExit(main())
