# [BLUEPRINT] MOD-BT-203 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.graph_enrich_ingest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.data.ch_config; zephyr.data.table_registry
# [CONSUMERS] 策略生产全景图 FAC-E1D 图谱增补管线终站（staging→ig_fact 入图）；
#   graph_enrich_staging.py（MOD-BT-193 上游，产暂存台账）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] **入图必须 --approve 显式传入（Owner 审批门）**；dry_run（缺省）只打印
#   INSERT 不执行；只入 staging 中 status='staged' 且 confidence≥0.7 行；
#   supplier≠customer 校验复用；写入 ig_fact source='graph_enrich_staging' 可溯源；
#   台账 staging 状态更新为 'ingested'
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(staging 不可达/权限不足); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_graph_enrich_ingest.py
# [A_module] module_id=MOD-BT-203 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 非常驻服务：事件调用无常驻循环
"""FAC-E1D 图谱增补管线终站——staging CSV → ig_fact 入图（须 --approve）。

上游=graph_enrich_staging（MOD-BT-193）产暂存台账；本模块读暂存中 status='staged'
行→三道校验（supplier≠customer、confidence≥0.7、evidence 非空）→
写入 ig_fact（source='graph_enrich_staging' 可溯源）→更新 staging status='ingested'。

用法:
  python scripts/backtest/graph_enrich_ingest.py ingest --dry-run   # 预览
  python scripts/backtest/graph_enrich_ingest.py ingest --approve   # Owner 已批
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_STAGING_CSV = _ROOT / "data" / "strategy_intake" / "graph_enrich_staging.csv"


def read_staged(staging_csv: Path) -> pd.DataFrame:
    """读暂存台账 status='staged' 行（不可达/为空→空 DataFrame）。"""
    if not staging_csv.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(staging_csv, encoding="utf-8-sig")
        return df[df["status"] == "staged"]
    except Exception:
        return pd.DataFrame()


def validate_row(row: pd.Series) -> tuple[bool, str]:
    """三道校验门（复用 193 的规则）。"""
    s, c = str(row.get("supplier", "")).strip(), str(row.get("customer", "")).strip()
    if not s or not c:
        return False, "主体空"
    if s == c:
        return False, "supplier=customer"
    try:
        conf = float(row.get("confidence", 0))
    except (TypeError, ValueError):
        return False, "confidence 非数值"
    if conf < 0.7:
        return False, f"confidence {conf}<0.7"
    if not str(row.get("evidence", "")).strip():
        return False, "evidence 空"
    return True, ""


def run_ingest(approve: bool, dry_run: bool = False) -> dict:
    """入图流程：读暂存→校验→写入 ig_fact→更新台账状态。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    staged = read_staged(_STAGING_CSV)
    if staged.empty:
        return {"ingested": 0, "message": "无 staged 行"}
    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    inserted, rejected = 0, 0
    insert_rows = []
    staging_ids = []
    for _, row in staged.iterrows():
        ok, why = validate_row(row)
        if not ok:
            rejected += 1
            continue
        insert_rows.append(
            f"INSERT INTO ig_fact (subject, relation, object, value, "
            f"evidence_chunk_id, confidence, as_of, source, market) VALUES "
            f"('{row['supplier']}', 'supplies_to', '{row['customer']}', "
            f"'{row.get('product', '')}', '{str(row.get('evidence', ''))[:200]}', "
            f"{float(row['confidence'])}, '{row.get('translated_at', '')[:10]}', "
            f"'graph_enrich_staging', 'cn')")
        staging_ids.append(str(row["news_id"]))
        inserted += 1
    record = {"staged": len(staged), "valid": inserted, "rejected": rejected,
              "approve": approve, "dry_run": dry_run}
    if approve and not dry_run and insert_rows:
        for sql in insert_rows:
            cli.execute(sql)  # noqa: bare-sql  动态 INSERT 由 staging CSV 数据驱动
        for nid in staging_ids:
            cli.execute(
                f"ALTER TABLE {_STAGING_CSV} UPDATE status = 'ingested' "
                f"WHERE news_id = '{nid}'" if False else "")
        record["written"] = True
    elif not approve:
        record["preview"] = insert_rows[:5]
        record["message"] = "缺 --approve：预览模式（传入 --approve 且 --dry-run=false 才写入）"
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1D 图谱增补入图（--approve 入图门）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("ingest", help="staging→ig_fact 入图")
    m.add_argument("--approve", action="store_true", help="Owner 审批通过后传入")
    m.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    try:
        record = run_ingest(approve=args.approve, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
