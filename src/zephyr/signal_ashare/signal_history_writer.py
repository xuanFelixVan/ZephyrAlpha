# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.signal_history_writer
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] schemas.categories.market_signal_history(DDL/INSERT_COLUMNS 真源); zephyr.data.ch_writer(client,延迟加载)
# [CONSUMERS] scripts/run_backtest.py(管道A strategy_weight); scripts/compute_signals.py(管道B factor_synth)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 列序以 schemas INSERT_COLUMNS 为唯一真源; DEC-INV-002 本模块只写表不触发任何 order; meta 必须携带血缘(DLG-001)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 缺必需列->ValueError; direction 非法->ValueError(CTR-INJ-003); CH client 不可得->RuntimeError
# [TESTS] scripts/compute_signals.py --verify(落表往返)
# [A_module] module_id=MOD-SIG-SH-WRITER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #BT-PIPELINE-001 阶段三（Owner 2026-09-01 批准调研报告）
"""
信号历史写入管道（c1_market.market_signal_history，一张窄表两管道）。

管道 A（strategy_weight）：BTRUN 回测最新一期权重面板——策略视角（系统想不想持有）。
管道 B（factor_synth）：日频多因子合成截面——个股视角（股票本身强不强）。
未来 signal_ashare 计算器族接入同表（MappedSignal 三字段 1:1 映射）。

归属：signal_ashare 包（D_SIGNAL 域 A 股代码家；表 c1_market 属 A 股分片，
币圈按市场分片三闸规则独立，不共用本表）。

设计对齐（feature_store_writer 同构裁定）：
  - 输入为行 dict 列表（与两管道产物天然形态一致）；列序以 schemas/categories/
    market_signal_history.py 的 INSERT_COLUMNS 为唯一真源（禁硬编码表结构）。
  - 注入式 client（测试不触库）；幂等靠 ReplacingMergeTree(computed_at)——
    同 (source,signal_id,symbol,trade_date) 重算取最新，天然支持回算覆盖。
  - direction 枚举 buy|sell|hold|neutral 强校验（CTR-INJ-003：方向必须带
    置信度，confidence 由调用方给出，本层只做 [0,1] 裁剪）。
  - DEC-INV-002：本模块只写表，不触发任何下单路径。
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date as _date
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_FULL_TABLE = "c1_market.market_signal_history"
_REQUIRED_FIELDS = ("trade_date", "symbol", "source", "signal_id", "direction", "score")
_VALID_DIRECTIONS = ("buy", "sell", "hold", "neutral")


def _insert_columns() -> str:
    """列序真源导入（schemas 包居仓根，非 src/——调用方 sys.path 不含仓根时自适应）。"""
    try:
        from schemas.categories.market_signal_history import INSERT_COLUMNS

        return INSERT_COLUMNS
    except ImportError:
        repo_root = Path(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from schemas.categories.market_signal_history import INSERT_COLUMNS

        return INSERT_COLUMNS


def _get_ch_client():
    """延迟取 clickhouse-driver Client（与 feature_store_writer 同款）。"""
    from zephyr.data.ch_writer import get_client

    return get_client()


def build_signal_rows(signals: list[dict[str, Any]], *, data_source: str) -> list[tuple]:
    """行 dict 列表 → 对齐 INSERT_COLUMNS 的行 tuple 列表。

    Args:
        signals: 每行含 trade_date(YYYY-MM-DD)/symbol(纯数字)/source/signal_id/
                 direction/score，可选 confidence/rank_in_universe/meta(dict 自动转 JSON)
        data_source: 生产方标识（btrun / compute_signals / ...）

    Raises:
        ValueError: 缺必需字段 / direction 非法
    """
    rows: list[tuple] = []
    for i, s in enumerate(signals):
        missing = [f for f in _REQUIRED_FIELDS if s.get(f) in (None, "")]
        if missing:
            raise ValueError(f"信号行 {i} 缺必需字段: {missing}")
        direction = str(s["direction"]).lower()
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(f"信号行 {i} direction 非法: {direction}（合法: {_VALID_DIRECTIONS}）")
        meta = s.get("meta") or {}
        if not isinstance(meta, str):
            meta = json.dumps(meta, ensure_ascii=False)
        confidence = float(s.get("confidence") or 0.0)
        td = str(s["trade_date"])[:10]
        try:
            td = _date.fromisoformat(td)  # clickhouse-driver Date 列要 date 对象（str 会炸 'year'）
        except ValueError:
            pass
        rows.append(
            (
                td,
                str(s["symbol"]).split(".")[0],
                str(s["source"]),
                str(s["signal_id"]),
                direction,
                float(s["score"]),
                max(0.0, min(1.0, confidence)),
                int(s.get("rank_in_universe") or 0),
                meta,
                data_source,
            )
        )
    return rows


def write_signals(
    signals: list[dict[str, Any]],
    *,
    data_source: str,
    client=None,
    chunk_size: int = 50_000,
) -> int:
    """信号行写入 c1_market.market_signal_history（分块 INSERT，幂等靠引擎）。

    Returns: 写入行数（空输入短路 0，不触库）。
    Raises: RuntimeError: client 未注入且 ch_writer 不可得。
    """
    if not signals:
        return 0
    rows = build_signal_rows(signals, data_source=data_source)
    if client is None:
        client = _get_ch_client()
    if client is None:
        raise RuntimeError("clickhouse-driver 不可用（client 未注入且 get_client 返回 None）")
    sql = f"INSERT INTO {_FULL_TABLE} {_insert_columns()} VALUES"
    for i in range(0, len(rows), chunk_size):
        client.execute(sql, rows[i : i + chunk_size])
    log.info("信号写入 %s: %d 行（data_source=%s）", _FULL_TABLE, len(rows), data_source)
    return len(rows)


__all__ = ["build_signal_rows", "write_signals"]
