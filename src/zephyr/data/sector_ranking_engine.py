# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §sector_ranking
# [MODULE] zephyr.data.sector_ranking_engine
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.sector_snapshot_collector (push_pool selection)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 5因子复合排名动态调整99只推送池；每日盘前重算一次；sector_snapshot表无数据时回退到成分股数量Top99；百分位排名消除量纲差异；权重之和=1.0
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse查询失败->回退默认推送池+log; 快照数据不足->回退默认推送池+log
# [TESTS] tests/zephyr/data/test_sector_ranking_engine.py
# [TTL] task_bound
"""880xxx 板块动态排名引擎——5因子复合排名调整99只推送池。

5因子复合排名（权重之和=1.0）：
  1. 成交额（amount）30% — 反映板块活跃度
  2. 涨跌幅绝对值（abs((now_price - last_close) / last_close)）25% — 反映板块波动
  3. 主动交投量（outside + inside）20% — 反映交投活跃度（volume恒为0的替代方案）
  4. 5分钟动量（(now_price - before_5min_now) / before_5min_now）15% — 反映短期动量
  5. 板块-大盘强弱差（板块涨跌幅 - 大盘涨跌幅）10% — 反映相对强度

大盘基准：880001.SH（上证指数）；缺失时用全板块涨跌幅均值。

启动:
    python -m zephyr.data.sector_ranking_engine              # 重算推送池并输出
    python -m zephyr.data.sector_ranking_engine --top 99     # 指定Top N
    python -m zephyr.data.sector_ranking_engine --json       # JSON格式输出
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime

log = logging.getLogger(__name__)

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024）
_TBL_SECTOR_SNAPSHOT = get_registry().table("market_sector_snapshot_880")
_TBL_SECTOR_CONSTITUENT = get_registry().table("market_sector_constituent_880")

_MKT_INDEX_CODES = [f"88000{i}.SH" for i in range(1, 10)]
_MKT_BENCHMARK = "880001.SH"
_DEFAULT_TOP_N = 99

# 5因子权重（之和=1.0）
_W_AMOUNT = 0.30
_W_CHANGE = 0.25
_W_ACTIVITY = 0.20
_W_MOMENTUM = 0.15
_W_RELATIVE = 0.10

# SQL 集中化（NO-BARE-SQL gate 豁免 SQL_ 前缀）
SQL_LATEST_SNAPSHOT = (
    f"SELECT sector_code, now_price, last_close, before_5min_now, "
    f"amount, outside, inside "
    f"FROM {_TBL_SECTOR_SNAPSHOT} "
    f"WHERE timestamp = (SELECT max(timestamp) FROM {_TBL_SECTOR_SNAPSHOT})"
)
SQL_DEFAULT_POOL = (
    f"SELECT sector_code FROM ("
    f"  SELECT sector_code, count() as cnt"
    f"  FROM {_TBL_SECTOR_CONSTITUENT}"
    f"  WHERE sector_code NOT LIKE '88000%'"
    f"  GROUP BY sector_code ORDER BY cnt DESC LIMIT {{limit}}"
    f") ORDER BY sector_code"
)


def _query_rows(sql: str) -> list[tuple]:
    """通过 ch_reader 只读路径执行 SELECT，返回行元组列表。

    治本（2026-08-17 AI-04 审计）：原实现裸 clickhouse_driver.Client 直连
    硬编码 IP（172.24.30.100）、无凭据、无 readonly=1，违反裁定 #ARCH-CH-017
    （禁硬编码 IP）与 read_only 安全约束（业务查询 MUST 只读连接）。
    ch_reader 自动注入 FINAL（ReplacingMergeTree 去重），reader 账号 SELECT-only。
    """
    tsv = ch_reader.query(sql)
    if not tsv or not tsv.strip():
        return []
    return [tuple(line.split("\t")) for line in tsv.strip().split("\n") if line.strip()]


def _pct_rank(values: list[float]) -> list[float]:
    """计算百分位排名（0~1），消除量纲差异。

    Args:
        values: 原始值列表。

    Returns:
        百分位排名列表（0~1），同长度。
    """
    n = len(values)
    if n <= 1:
        return [0.5] * n
    sorted_idx = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    for rank_pos, idx in enumerate(sorted_idx):
        ranks[idx] = rank_pos / (n - 1)
    return ranks


def _calc_change_pct(now_price: float, last_close: float) -> float:
    """计算涨跌幅（百分比小数，如0.02=2%）。"""
    if last_close == 0:
        return 0.0
    return (now_price - last_close) / last_close


def _calc_momentum(now_price: float, before_5min: float) -> float:
    """计算5分钟动量（百分比小数）。"""
    if before_5min == 0:
        return 0.0
    return (now_price - before_5min) / before_5min


def _compute_factors(rows: list[tuple]) -> dict[str, list[float]]:
    """从快照行提取5因子原始值。

    Args:
        rows: ClickHouse 查询结果，每行 (sector_code, now_price, last_close,
              before_5min_now, amount, outside, inside)。

    Returns:
        dict: sector_codes + 5个因子列表。
    """
    codes = [r[0] for r in rows]
    amounts = [float(r[4]) for r in rows]
    changes = [abs(_calc_change_pct(float(r[1]), float(r[2]))) for r in rows]
    activities = [float(r[5]) + float(r[6]) for r in rows]
    momenta = [_calc_momentum(float(r[1]), float(r[3])) for r in rows]

    # 大盘涨跌幅基准
    benchmark_change = _get_benchmark_change(rows)
    relatives = [abs(_calc_change_pct(float(r[1]), float(r[2])) - benchmark_change) for r in rows]

    return {
        "codes": codes,
        "amount": amounts,
        "change": changes,
        "activity": activities,
        "momentum": momenta,
        "relative": relatives,
    }


def _get_benchmark_change(rows: list[tuple]) -> float:
    """获取大盘涨跌幅基准（880001.SH 或全板块均值）。"""
    for r in rows:
        if r[0] == _MKT_BENCHMARK:
            return _calc_change_pct(float(r[1]), float(r[2]))
    # 回退：全板块涨跌幅均值
    changes = [_calc_change_pct(float(r[1]), float(r[2])) for r in rows]
    return sum(changes) / len(changes) if changes else 0.0


def compute_ranking(rows: list[tuple]) -> list[tuple[str, float]]:
    """计算5因子复合排名。

    Args:
        rows: ClickHouse 快照行列表。

    Returns:
        [(sector_code, score), ...] 按分数降序排列。
    """
    if not rows:
        return []

    factors = _compute_factors(rows)
    r_amount = _pct_rank(factors["amount"])
    r_change = _pct_rank(factors["change"])
    r_activity = _pct_rank(factors["activity"])
    r_momentum = _pct_rank(factors["momentum"])
    r_relative = _pct_rank(factors["relative"])

    codes = factors["codes"]
    scores = []
    for i in range(len(codes)):
        score = (
            r_amount[i] * _W_AMOUNT
            + r_change[i] * _W_CHANGE
            + r_activity[i] * _W_ACTIVITY
            + r_momentum[i] * _W_MOMENTUM
            + r_relative[i] * _W_RELATIVE
        )
        scores.append((codes[i], round(score, 4)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def get_push_pool(top_n: int = _DEFAULT_TOP_N) -> list[str]:
    """获取推送池（动态排名 Top N 或默认回退）。

    Args:
        top_n: 推送池上限（默认99）。

    Returns:
        推送池 sector_code 列表（9只mkt_index + top_n-9只动态排名sector）。
    """
    try:
        rows = _query_rows(SQL_LATEST_SNAPSHOT)

        if not rows:
            log.warning("sector_snapshot 表无数据，回退到成分股数量Top%d", top_n)
            return _get_default_pool(top_n)

        ranking = compute_ranking(rows)
        sector_scores = [(c, s) for c, s in ranking if c not in _MKT_INDEX_CODES]
        selected = [c for c, _ in sector_scores[: top_n - len(_MKT_INDEX_CODES)]]

        pool = _MKT_INDEX_CODES[:]
        for code in selected:
            if code not in pool:
                pool.append(code)
            if len(pool) >= top_n:
                break

        log.info("动态推送池: %d 只 (9 mkt_index + %d sector)", len(pool), len(pool) - 9)
        return pool

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.error("动态排名失败，回退默认推送池: %s", e)
        return _get_default_pool(top_n)


def _get_default_pool(top_n: int) -> list[str]:
    """默认推送池（基于成分股数量Top N）。"""
    try:
        limit = top_n - len(_MKT_INDEX_CODES)
        sql = SQL_DEFAULT_POOL.format(limit=limit)
        rows = _query_rows(sql)
        pool = _MKT_INDEX_CODES[:]
        pool.extend([r[0] for r in rows])
        return pool
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        log.error("默认推送池获取失败: %s", e)
        return _MKT_INDEX_CODES[:]


def main() -> int:
    """盘前重算推送池入口。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="880xxx 板块动态排名引擎")
    parser.add_argument("--top", type=int, default=_DEFAULT_TOP_N, help="推送池上限（默认99）")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    args = parser.parse_args()

    log.info("=== 880xxx 板块动态排名引擎启动 ===")
    pool = get_push_pool(top_n=args.top)

    if args.json:
        print(
            json.dumps(
                {"push_pool": pool, "count": len(pool), "time": datetime.now(UTC).isoformat()}, ensure_ascii=False
            )
        )
    else:
        print(f"\n推送池 ({len(pool)} 只):")
        for i, code in enumerate(pool, 1):
            print(f"  {i:3d}. {code}")

    log.info("=== 完成: %d 只 ===", len(pool))
    return 0


if __name__ == "__main__":
    sys.exit(main())
