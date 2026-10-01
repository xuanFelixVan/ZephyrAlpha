# [BLUEPRINT] MOD-BT-COND-PACKAGE | docs/03_modules/_domain_backtest/blueprint.md（G-A.3 同包胞物化面）
# [MODULE] zephyr.backtest.regime_validation.chart_cell_materializer
# noqa: m11-perm-manual-legitimate  合法 manual CLI 物化器（ARCH-051 裁定口径）：宿主 scripts/data/* 为 gitignore 在盘袋，本件为库函数+CLI 薄壳双面，人工/按需调用非永久自动运行器
# create-guard-not-dup: 本件是图形条件包物化器(判据全委托条件包零自设),与LLM探测/清单漂移等命中能力无职责重叠,关键词命中系领域语文巧合
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.backtest.regime_validation.chart_condition_package; zephyr.data.table_registry; zephyr.infrastructure.database_service; zephyr.data.ch_writer(lazy); schemas.categories.market.market_pattern_win_rate(INSERT_COLUMNS 真源)
# [CONSUMERS] c1_market.market_pattern_win_rate（regime_tag=胞 id 行，PatternWinRateProvider/REG-PAT-001 读）;
#             scripts/data/pattern_win_rate_materialize.py --chart-cells（薄壳委托，宿主 scripts/data/* 为 gitignore 在盘袋）;
#             tests/backtest/test_chart_cell_materializer.py
# [STARTUP] manual（CLI: python -m zephyr.backtest.regime_validation.chart_cell_materializer --start --end）
# [MATURITY] testing
# [TTL] permanent
# [INVARIANTS] 图形信号=考试条件轴禁独立信号（沿用 chart_condition_package 立法，本件零判据零下单）；
#   全量重算重放（ReplacingMergeTree(updated_at) 同键取最新，重复物化幂等）；
#   判据全数委托 chart_condition_package（轴口径/30 日地板/None 语义单一真源，本件零判据）；
#   regime_tag=胞 id（c<图形档>|g<灰度>|s<状态>|f<族>），market_pattern_win_rate schema 零改动；
#   写侧单线：唯一写通道=ch_writer.get_client（禁第二 INSERT 路径）；读侧唯一通道=DatabaseService
#   reader 角色（禁 ch_reader.query TSV 下标直取，W-180）；
#   禁内建时钟：--start/--end 显式传参，缺任一=退出码 2（生成器纪律）；
#   表名真源=TableRegistry（market_kline_daily/market_pattern_win_rate，禁表名字面量）
# [MODIFY-GUARD] tests/backtest/test_chart_cell_materializer.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] --start/--end 缺失->SystemExit(2); kline/事件读数空->RuntimeError（不留半批）;
#   CH writer 不可得->RuntimeError（调用方 CLI 退出码 2）; 统计零达标行->RuntimeError（build_cell_stats_rows 契约透传）
# [TESTS] tests/backtest/test_chart_cell_materializer.py（mock conn/base_pack/fake insert，零 CH）
"""图形条件胞物化 writer（G-A.3 落库面·总筹宿主裁定执行件 2026-09-29）。

裁定（总筹 st-nightsweep-chief-20260929 预裁定）：writer 属考试统计面，应落 tracked 区。
SW10 的 --chart-cells writer 扩展原宿主 scripts/data/pattern_win_rate_materialize.py 位于
gitignore 在盘袋（.gitignore scripts/data/* 刻意隔离=data supply 域惯例），故库函数+CLI
入口落本件（tracked），盘面件降薄壳委托（CLI 面兼容不变）。

管线（判据全数委托 chart_condition_package，本件只做读→装→写）：

    事件窗 load_market_pattern_events
      → 三轴包 load_chart_condition_pack（真源=ChartPackRequest，两轴包缺轴 fail-closed）
      → attach_cell_ids（胞 id 贴装，窗外/未达地板=None 下沉）
      → 前视收益（kline_daily 收盘面板 shift(-w)，fwd 键=make_fwd_key 同构）
      → build_cell_stats_rows（形态行+胞级 __baseline__ 行，混频抛）
      → INSERT_COLUMNS 定序 → ch_writer 单线落 c1_market.market_pattern_win_rate

SW10 盘面版遗留缺陷在本件修正：原 run_chart_cells 引
condition_package.load_condition_pack（两轴 ConditionPack，无 family/cell_id 列）喂
attach_cell_ids，实弹必 KeyError('family')——本件改 ChartPackRequest 真源
（load_chart_condition_pack），READY_NOT_FIRED 袋转可点火。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/chart_cell_materializer.yaml
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

import pandas as pd

from zephyr.data.table_registry import get_registry

if TYPE_CHECKING:  # F821 落地整改：注解名经 TYPE_CHECKING 导入（运行时惰性导入语义不变）
    from zephyr.backtest.regime_validation.chart_condition_package import ChartConditionPack, ChartPackRequest

logger = logging.getLogger(__name__)

_DEFAULT_WINDOWS: tuple[int, ...] = (1, 5, 10, 20)
_KLINE_TABLE = get_registry().table("market_kline_daily")
_STATS_TABLE = get_registry().table("market_pattern_win_rate")
# G-A.3 胞物化前视收益源（纯 format 模板常量，禁内联 f-string 裸 SQL）
SQL_KLINE_WINDOW = (
    "SELECT symbol, trade_date, close FROM {table} "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end_buf}') AND close > 0"
)
# 写侧 INSERT 模板（NO-BARE-SQL §5.160.2 集中化：列片段真源=schema INSERT_COLUMNS 字符串）
_SQL_INSERT_STATS = "INSERT INTO {table} {columns} VALUES"
_INSERT_CHUNK = 50_000
# 窗口缓冲（自然日）：保 20 交易日窗成熟（长假+停牌余量，与盘面版同口径 45）
_END_BUFFER_DAYS = 45


def load_kline_close_panel(
    start: str,
    end: str,
    *,
    conn: Any | None = None,  # noqa: any-abuse -- DI 读通道缝位（DatabaseService reader，测试注入替身；同 chart_condition_package 惯用法）
) -> pd.DataFrame:
    """kline_daily 收盘面板（index=trade_date 升序 DatetimeIndex，columns=symbol）。

    唯一读通道=DatabaseService reader（DI conn 缝位，测试注 fake 零 CH）。
    读数空=RuntimeError（查询失败与无数据不可混判）。
    """
    if conn is None:
        from zephyr.infrastructure.database_service import DatabaseService

        conn = DatabaseService().get_clickhouse_conn(role="reader")
    end_buf = (pd.Timestamp(end) + pd.Timedelta(days=_END_BUFFER_DAYS)).date().isoformat()
    rows = conn.execute(SQL_KLINE_WINDOW.format(table=_KLINE_TABLE, start=start, end_buf=end_buf))
    if not rows:
        raise RuntimeError("kline_daily 读数空——前视收益不可得，禁造证据")
    kdf = pd.DataFrame(rows, columns=["symbol", "trade_date", "close"])
    close = kdf.pivot_table(index="trade_date", columns="symbol", values="close", aggfunc="last").sort_index()
    close.index = pd.to_datetime(close.index)
    return close


def build_fwd_series(close: pd.DataFrame, windows: Iterable[int]) -> dict[int, pd.Series]:
    """收盘面板 → {窗口: 前视收益 Series（键=symbol|date，与 make_fwd_key 同构）}。

    纯函数零 IO；末 N 日未成熟自然 NaN（事件查不到即弃，禁补 0）。
    stack() 后 MultiIndex 级序=(trade_date, symbol)（pivot index=trade_date 在前）——
    解包级序必须与之对应，SW10 盘面版按 (symbol, trade_date) 解包系在盘雷（READY_NOT_FIRED
    未实弹故未炸），本件修正。
    """
    from zephyr.backtest.regime_validation.chart_condition_package import make_fwd_key

    out: dict[int, pd.Series] = {}
    for w in windows:
        stacked = close.shift(-w).div(close).sub(1).stack()
        out[int(w)] = pd.Series({make_fwd_key(sym, d): v for (d, sym), v in stacked.items()})
    return out


def materialize_chart_cells(
    start: str,
    end: str,
    windows: Iterable[int] = _DEFAULT_WINDOWS,
    *,
    conn: Any | None = None,  # noqa: any-abuse -- DI 读通道缝位（同 load_kline_close_panel）
    base_pack: Any | None = None,  # noqa: any-abuse -- 两轴包测试合成注入位（None=生产真源装配）
    insert_rows: Any | None = None,  # noqa: any-abuse -- 写通道注入位（测试 fake 收集 payload；None=ch_writer 真写）
) -> int:
    """G-A.3 图形条件胞物化主入口：事件×三轴包→胞级统计→同表落库。返回落库行数。

    Args:
        start/end: 事件窗（显式传参，禁内建时钟）。
        windows: 前视窗口（默认 1,5,10,20 与 market_pattern_win_rate 同口径）。
        conn: DatabaseService reader 替身（测试注入，None=真 reader）。
        base_pack: 两轴 ConditionPack 注入位（测试合成包零 CH；None=生产路径经
            ChartPackRequest 真源自装）。
        insert_rows: 写通道注入位（测试 fake 收集 payload；None=ch_writer 单线真写）。

    Returns:
        落库行数（全量重放语义，重复物化幂等）。
    Raises:
        RuntimeError: 事件/kline 读数空、统计零达标、writer 不可得（不留半批）。
    """
    from zephyr.backtest.regime_validation import chart_condition_package as ccp
    from zephyr.backtest.regime_validation.chart_condition_package import (
        ChartPackRequest,
        load_chart_condition_pack,
    )

    wins = [int(w) for w in windows]
    events = ccp.load_market_pattern_events(start, end, conn=conn)
    req = ChartPackRequest(start=start, end=end)
    if base_pack is None:
        pack = load_chart_condition_pack(req, conn=conn)
    else:
        pack = _pack_with_base(req, base_pack, conn)
    attached = ccp.attach_cell_ids(events, pack)
    close = load_kline_close_panel(start, end, conn=conn)
    fwd_by_key = build_fwd_series(close, wins)
    attached["fwd_ret_key"] = [
        ccp.make_fwd_key(sym, d) for sym, d in zip(attached["symbol"], attached["anchor_trade_date"], strict=True)
    ]
    rows = ccp.build_cell_stats_rows(attached, fwd_by_key)
    payload = _rows_to_payload(rows)
    if insert_rows is not None:
        return int(insert_rows(payload))
    return _insert_rows_default(payload)


def _pack_with_base(
    req: ChartPackRequest,
    base_pack: Any,  # noqa: any-abuse -- 测试合成包注入缝（None 路径走生产真源装配）
    conn: Any,  # noqa: any-abuse -- DI 读通道缝位（同 load_kline_close_panel）
) -> ChartConditionPack:
    """base_pack 注入路径（测试缝位）：req.base_pack 承载合成包，其余走真源装配。"""
    from dataclasses import replace

    from zephyr.backtest.regime_validation.chart_condition_package import load_chart_condition_pack

    return load_chart_condition_pack(replace(req, base_pack=base_pack), conn=conn)


def _rows_to_payload(rows: list[dict[str, Any]]) -> list[tuple]:
    """统计行 dict → 落库定序 tuple（low_sample bool→UInt8 0/1）。

    列序真源=chart_condition_package._STATS_COLUMNS（writer 对齐清单，禁增删列）。
    schema 模块的 INSERT_COLUMNS 是 SQL 字符串片段（"(a, b, ...)"），迭代它产出
    单字符列名——SW10 盘面版 `for col in INSERT_COLUMNS` 系第三颗在盘雷，本件修正。
    """
    from zephyr.backtest.regime_validation.chart_condition_package import _STATS_COLUMNS

    payload = []
    for r in rows:
        vals = []
        for col in _STATS_COLUMNS:
            v = r[col]
            if col == "low_sample":
                v = int(bool(v))
            vals.append(v)
        payload.append(tuple(vals))
    return payload


def _insert_rows_default(payload: list[tuple]) -> int:
    """默认写通道：ch_writer 单线分块 INSERT（50k/批，ReplacingMergeTree 幂等）。"""
    from schemas.categories.market.market_pattern_win_rate import INSERT_COLUMNS
    from zephyr.data.ch_writer import get_client

    client = get_client()
    if client is None:
        raise RuntimeError("clickhouse writer client 不可得（冷却期）——物化中止不留半批")
    insert_sql = _SQL_INSERT_STATS.format(table=_STATS_TABLE, columns=INSERT_COLUMNS)
    for i in range(0, len(payload), _INSERT_CHUNK):
        client.execute(insert_sql, payload[i : i + _INSERT_CHUNK])
    return len(payload)


def main(argv: list[str] | None = None) -> int:
    """CLI 入口（python -m zephyr.backtest.regime_validation.chart_cell_materializer）。"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="G-A.3 图形条件胞物化（regime_tag=胞 id，零 schema 改动）")
    ap.add_argument("--start", required=True, help="事件窗起（显式传参，生成器禁内建时钟）")
    ap.add_argument("--end", required=True, help="事件窗止")
    ap.add_argument("--windows", default=",".join(str(w) for w in _DEFAULT_WINDOWS))
    args = ap.parse_args(argv)
    windows = [int(w) for w in str(args.windows).split(",") if w.strip()]
    n = materialize_chart_cells(args.start, args.end, windows)
    print(f"OK: 图形条件胞物化 {n} 行 -> {_STATS_TABLE}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        logger.error("%s", exc)
        sys.exit(2)
