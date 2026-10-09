# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] scripts.data_ops.audit_ti_row_versions
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib(json/argparse/datetime/http/pathlib/sys)
# [CONSUMERS] Owner/A-B 定案会话手动触发（technical_indicator 行版本重复尺，裁定#380④ 派生）；日序列文件 data/audit-trail/ti_row_versions_series.jsonl
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] fail-loud：任何分片查询失败或零读数 exit 3 永不假绿；按 (period,单日) 分片——整表 GROUP BY 会撞 CH 默认 max_memory_usage（2026-10-09 实测 5.33 GiB 上限）；三把尺同时出（重复率/值分叉率/ingest_ts 可裁决率），只报"重复"不报"值是否不同"=判据不完整；追加式序列不覆写历史
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 退出码 0=全窗零重复/2=存在重复键/3=查询失败或零样本(含 '' 空返回，本仓 CH 包装出错返回 '' 不抛，两态不可分故一律判故障)
# [TESTS] 自证双向：2026-10-09 对 period=daily 2026-09-15 必判红（实测 54% 重复、38% 值分叉），对 15min/120min 同日必判绿（实测 0 重复）
# [A_module] module_id=scripts-data-ti-row-versions-audit | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# create-guard-not-dup: 本模块只做 ClickHouse 存储层行版本重复的只读测量，不实现也永不 import 任何指标计算，非 indicator_base.py 的第二实现
"""technical_indicator 行版本重复尺（只读，零风险，A/B 定案前置）。

背景：技术指标宽表（表名经 TableRegistry 取，本文件不写字面量）是 ReplacingMergeTree，ORDER BY=(symbol, period, trade_time) **无版本列**
（DDL 真源=schemas/categories/market/market_technical_indicator.py:296-298）。
合并未发生时，非 FINAL 读同一键会返回多行；若多行值不同，则读到哪一版是不确定的。

三把尺（缺一就把缺陷读小）：
  dup_ratio        = 同键多行占比（体积/行数问题）
  divergence_ratio = 同键但指标值不同的占比（**读数正确性问题**）
  ts_resolvable    = 值分叉的键里，ingest_ts 能否区分各版本（决定"读取侧按最新入库去重"
                     是否等价于确定性正确答案；本表已有 ingest_ts 列可当版本锚）

用法：
    python scripts/data_ops/audit_ti_row_versions.py --date 2026-09-15
    python scripts/data_ops/audit_ti_row_versions.py --days 2026-09-01,2026-09-15,2026-09-30 --json
"""

import argparse
import http.client
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# 仅引导用：路径真源=src/zephyr/shared/io/paths.py 的 REPO_ROOT（SSOT-REDEFINITION 硬规）
_BOOT = Path(__file__).resolve().parents[2]
_SRC = _BOOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

SERIES_FILE = REPO_ROOT / "data" / "audit-trail" / "ti_row_versions_series.jsonl"
CH_BASE_PATH = "/"
VALUE_COLS = ("ma_5", "ma_20", "rsi_6", "macd_hist", "atr_14", "kdj_j", "boll_upper")
PERIODS = ("1min", "5min", "15min", "30min", "60min", "120min", "daily", "weekly", "monthly")


def _endpoint() -> tuple[str, int]:
    """host/port 走真源解析，禁码内第二真源（与 rolling_archive_reconciler 同通道）。"""
    try:
        from zephyr.data.ch_config import ensure_ch_env_loaded
        from zephyr.shared.security.secrets import get_secret_or_default

        ensure_ch_env_loaded()
        host = get_secret_or_default("CLICKHOUSE_HOST", "")
        port = int(get_secret_or_default("CLICKHOUSE_HTTP_PORT", "8123"))
    except Exception:  # noqa: BLE001 — 解析不到则退本机，但仍会显式报错
        host, port = "172.24.30.100", 8123
    if not host:
        host = "172.24.30.100"
    return host, port


def run_sql(sql: str, timeout: int = 180) -> str:
    """返回 TSV 首行；查询失败/空返回一律以异常抛出（本仓包装出错返回 '' 不抛=静默）。"""
    host, port = _endpoint()
    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    conn.request("POST", CH_BASE_PATH, body=sql + " FORMAT TSV")
    resp = conn.getresponse()
    body = resp.read().decode("utf-8", "replace").strip()
    status = getattr(resp, "status", 200)
    conn.close()
    if status != 200:
        raise RuntimeError(f"HTTP {status}: {body[:200]}")
    if not body:
        # 关键：'' 既可能是零行也可能是故障，本尺一律当故障（宁可红不可假绿）
        raise RuntimeError("空返回（零行或故障，两态不可分 -> 判故障）")
    if "Exception" in body or "Code:" in body:
        raise RuntimeError(f"CH 报错: {body[:200]}")
    return body.splitlines()[0]


def _table() -> str:
    """表名走 TableRegistry 真源（#ARCH-CH-024 Phase 5：禁硬编码字符串，含注释/文档面）。"""
    from zephyr.data.table_registry import get_registry

    return get_registry().table("market_technical_indicator")


def probe_cell(period: str, day: str) -> dict:
    """单个 (period, 单日) 分片的三把尺。"""
    table = _table()
    tup = ", ".join(VALUE_COLS)
    sql = (
        "SELECT count() AS keys, countIf(cnt>1) AS dup_keys, max(cnt) AS max_rows, "
        "countIf(cnt>1 AND nv>1) AS divergent_keys, max(nv) AS max_values, "
        "countIf(cnt>1 AND nv>1 AND nt>1) AS ts_resolvable_keys, sum(cnt) AS rows_total "
        f"FROM (SELECT symbol, trade_time, count() AS cnt, "
        f"countDistinct(({tup})) AS nv, countDistinct(ingest_ts) AS nt "
        f"FROM {table} WHERE period='{period}' AND trade_date='{day}' "
        "GROUP BY symbol, trade_time)"
    )
    keys, dup, mx, div, maxv, tsr, rows_total = (x.strip() for x in run_sql(sql).split("\t"))
    keys_i, dup_i = int(keys), int(dup)
    return {
        "period": period,
        "day": day,
        "keys": keys_i,
        "rows": int(rows_total),
        "dup_keys": dup_i,
        "dup_ratio": round(dup_i / keys_i, 4) if keys_i else 0.0,
        "max_rows_per_key": int(mx),
        "divergent_keys": int(div),
        "divergence_ratio": round(int(div) / dup_i, 4) if dup_i else 0.0,
        "max_value_versions": int(maxv),
        "ts_resolvable_keys": int(tsr),
        "ts_resolvability": round(int(tsr) / int(div), 4) if int(div) else None,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="technical_indicator 行版本重复尺（只读）")
    p.add_argument("--days", default="", help="逗号分隔日期；缺省=昨天")
    p.add_argument("--periods", default=",".join(PERIODS))
    p.add_argument("--json", action="store_true", help="仅输出 JSON（机读）")
    p.add_argument("--no-series", action="store_true", help="不追加日序列（红蓝演练用）")
    args = p.parse_args(argv)

    days = [x.strip() for x in args.days.split(",") if x.strip()]
    if not days:
        from datetime import timedelta

        days = [(datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")]
    periods = [x.strip() for x in args.periods.split(",") if x.strip()]

    cells: list[dict] = []
    failures: list[str] = []
    for day in days:
        for per in periods:
            try:
                c = probe_cell(per, day)
            except Exception as e:  # noqa: BLE001 — fail-loud：采集故障绝不静默跳过
                failures.append(f"{day}/{per}: {e.__class__.__name__}: {str(e)[:140]}")
                continue
            cells.append(c)
            if not args.json:
                print(
                    f"{day} {per:7} keys={c['keys']:>10,} dup={c['dup_keys']:>10,}"
                    f"({c['dup_ratio']:.3f}) 值分叉={c['divergent_keys']:>10,}"
                    f"({c['divergence_ratio']:.3f}) max行={c['max_rows_per_key']} "
                    f"max版={c['max_value_versions']} ts可裁决="
                    f"{c['ts_resolvability']}",
                    flush=True,
                )

    summary = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        "cells_ok": len(cells),
        "cells_failed": len(failures),
        "failures": failures[:20],
        "total_keys": sum(c["keys"] for c in cells),
        "total_dup_keys": sum(c["dup_keys"] for c in cells),
        "total_divergent_keys": sum(c["divergent_keys"] for c in cells),
        "total_rows": sum(c["rows"] for c in cells),
        "row_inflation_ratio": round(sum(c["rows"] for c in cells) / max(sum(c["keys"] for c in cells), 1), 3),
        "periods_with_divergence": sorted({c["period"] for c in cells if c["divergent_keys"]}),
        "worst_cell": max(cells, key=lambda c: c["divergent_keys"]) if cells else None,
    }
    if not args.no_series:
        SERIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SERIES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"summary": summary, "cells": cells}, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))

    if failures:
        print(f"[FAIL-LOUD] {len(failures)} 个分片采集失败——本尺拒绝判绿", file=sys.stderr)
        return 3
    if summary["total_dup_keys"] > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
