# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.index_eqw_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider (capability=kline_index_calc 路由)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 内部计算 Provider——读 CH kline_daily 全量→本地计算自算指数→返回 FetchResult；恒全量重算（幂等，忽略 payload.start，ReplacingMergeTree 去重）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 读取/计算失败→返回 FetchResult(error=...) 不抛异常
# [TESTS] 手动冒烟：python -c 调 _compute_eqw_alla 对拍 SQL 直算
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""自算指数内部计算 Provider（全A等权 EQW_ALLA，Owner 2026-09-04 立项 MVP）。

与外部数据源 Provider（拉官方指数）区别：纯本地计算，读 c1_market.kline_daily
（5200+ 只全A日线），输出写入 c1_market.kline_index_calc（与官方指数真源 kline_index
分表——真源唯一/责任唯一：衍生指标不得混入官方表）。

等权口径（严格复权版，Owner 选定 MVP 推荐）：
    个股复权收益：ret_i(t) = close_i(t)×adj_i(t) / (close_i(t-1)×adj_i(t-1)) − 1
      （adj_factor=kline_daily 后复权因子，全表零 NULL 已实测）
    日等权收益：ret_eqw(t) = mean(ret_i(t))，当日有前收的股票全体（停牌股自然剔除，
      新股上市首日无前收自然剔除；ST/涨跌停不剔除=全A口径）
    指数链乘：close(t) = close(t-1) × (1 + ret_eqw(t))，基期 2019-01-03 = 1000
      （kline_daily 实测 2018 及以前仅 237 只样本覆盖，幸存者偏差会污染等权口径，
      故基期取全量覆盖起点 2019-01-03；覆盖缺口回补后可改锚重算——改 _EQW_INDEXES 即可）
    宽度：advance/decline = 当日 ret_i>0 / <0 家数

幂等语义：每次运行全量重算 [基期, today]（~5300 行，秒级），ReplacingMergeTree
按 (symbol, trade_date) 去重——scheduler incremental:false 传月初 start 亦被忽略，
无断点续传状态，增量/全量行为统一。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: kline_daily 全A日线
#   fields: trade_date, symbol, close, adj_factor
#   code: c1_market.kline_daily
# 层: 算法
# - id: A1
#   name_zh: CH 端聚合（lagIn 组内复权收益→日等权 mean/宽度计数）
#   name_en: SQL-side aggregation
#   desc: 单条 SQL 完成万行级重活，pandas 只收 ~5300 行日聚合结果
# - id: A2
#   name_zh: 基期锚定+链乘（pandas）
#   name_en: chained multiplication
# 层: 输出
# - id: O1
#   name: kline_index_calc 行元组序列
#   code: c1_market.kline_index_calc
# [/ALGO_FLOW]
# 边: I1 --> A1 --> A2 --> O1
"""

from __future__ import annotations

import logging
import time
from typing import Final, Iterator

from zephyr.data.provider_base import (
    FetchPayload,
    FetchResult,
    IngestProviderBase,
)

log = logging.getLogger(__name__)

# 自算指数注册表（symbol → (中文名, 基期日, 基期点位)）——新口径在此追加
# 基期=2019-01-03（非原计划 2005-01-04）：kline_daily 实测 2018 及以前仅 237 只样本覆盖
# （幸存者偏差会污染等权口径），2019-01-02 起才全量 3771+ 只；01-03 基期日已是全量日，
# 01-02 及以前仅作链乘热身窗。
_EQW_INDEXES: Final[dict[str, tuple[str, str, float]]] = {
    "EQW_ALLA": ("全A等权", "2019-01-03", 1000.0),
}

# 覆盖度防御阈值：n_stocks 低于此值视为数据管道异常日（实证 2026-08-26 kline_daily
# 断档仅 1 只有数），该日 ret 按 0 处理、点位延续前值——防单股收益冒充全A等权污染序列。
# 2019 基期后实测最小正常覆盖 3563，阈值 1000 留足安全边际。
_MIN_COVERAGE: Final = 1000

# CH 端聚合 SQL：组内前一复权收盘（窗口 lag 按 symbol 分窗、trade_date 排序）→复权收益→日等权聚合。
# 组首行 lag 默认 0 → ret=inf，由 isFinite 滤除（等价"无前收不计"：新股首日/停牌跨段自然剔除，
# 复牌首日相对停牌前收盘的跳空计入——窗口按行偏移不受停牌天数影响，口径见模块 docstring）。
# 注：本机 CH 无 lagIn 简写、neighbor 已 deprecated 禁用（均实测 2026-09-04），用标准窗口语法。
_SQL_EQW_AGG: Final = (
    "SELECT trade_date, count() AS n, avg(ret) AS eqw_ret, "
    "countIf(ret > 0) AS adv, countIf(ret < 0) AS dec "
    "FROM ("
    "  SELECT trade_date, ret FROM ("
    "    SELECT trade_date, symbol, "
    "           adj_close / lag(adj_close, 1) OVER (PARTITION BY symbol ORDER BY trade_date) - 1 AS ret "
    "    FROM ("
    "      SELECT trade_date, symbol, toFloat64(close) * toFloat64(adj_factor) AS adj_close "
    "      FROM c1_market.kline_daily "
    "      WHERE market_type = 'A_share' AND trade_date >= '{warm_start}'"
    "    )"
    "  ) "
    "  WHERE isFinite(ret) AND isNotNull(ret)"   # 组首行 lag 默认 0 → ret=inf 在此滤除
    ") "
    "GROUP BY trade_date ORDER BY trade_date FORMAT TSV"
)


class IndexEqwComputeProvider(IngestProviderBase):
    """自算指数内部计算 Provider（EQW_ALLA 全A等权）。

    用法（由 scheduler 自动调用，source=internal, capability=kline_index_calc）：
        provider = IndexEqwComputeProvider()
        provider.connect()
        for result in provider.fetch(payload, policy):
            # result.rows = (trade_date, symbol, name, close, ret, n, adv, dec, 'internal')
        provider.disconnect()
    """

    source_name = "internal"

    # 输出行列顺序（与 schemas/categories/market_kline_index_calc.py INSERT_COLUMNS 对齐）
    _COLUMNS: Final = [
        "trade_date",
        "symbol",
        "name",
        "close",
        "ret",
        "n_stocks",
        "advance_count",
        "decline_count",
        "data_source",
    ]

    def connect(self) -> None:
        self._connected = True
        self._log.info("IndexEqwComputeProvider 已就绪（本地计算，无需外部连接）")

    def health_check(self) -> bool:
        if not self._connected:
            return False
        try:
            from zephyr.data import ch_reader

            return ch_reader.count("c1_market.kline_daily", limit=1) >= 0
        except Exception as e:  # noqa: BLE001
            self._log.warning("健康检查失败: %s", e)
            return False

    def disconnect(self) -> None:
        self._connected = False

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """计算全部注册自算指数→返回 FetchResult。

        恒全量重算：payload.start/end 仅作参考（scheduler 全量模式传月初，忽略），
        每次从基期重算整条曲线，ReplacingMergeTree 幂等去重。
        """
        start_time = time.monotonic()
        table = payload.table
        rows: list[tuple] = []
        try:
            agg = self._load_daily_agg()
            for symbol, (name, base_date, base_value) in _EQW_INDEXES.items():
                rows.extend(self._chain_multiply(symbol, name, base_date, base_value, agg))
        except Exception as e:  # noqa: BLE001 — [ERROR_CONTRACT] 失败不抛
            log.error("自算指数计算失败: %s", e)
            yield FetchResult(
                table=table,
                columns=self._COLUMNS,
                rows=[],
                last_key=payload.end.isoformat(),
                elapsed_sec=time.monotonic() - start_time,
                error=str(e),
            )
            return
        yield FetchResult(
            table=table,
            columns=self._COLUMNS,
            rows=rows,
            last_key=payload.end.isoformat(),
            elapsed_sec=time.monotonic() - start_time,
            rows_fetched=len(rows),
            error=None,
        )

    def _load_daily_agg(self) -> list[tuple[str, int, float, int, int]]:
        """CH 端聚合 → [(trade_date, n, eqw_ret, adv, dec), ...] 按 date 升序。"""
        from zephyr.data import ch_reader

        warm_start = min(base for _, (_, base, _) in _EQW_INDEXES.items())
        # 基期前留 20 个交易日热身窗（估 2004-12 初起足够覆盖 A 股最短月度间休市）
        y, m, d = map(int, warm_start.split("-"))
        import datetime as _dt

        warm_dt = _dt.date(y, m, d) - _dt.timedelta(days=40)
        tsv = ch_reader.query(_SQL_EQW_AGG.format(warm_start=warm_dt.isoformat()))
        out: list[tuple[str, int, float, int, int]] = []
        for line in tsv.strip().split("\n"):
            if not line:
                continue
            p = line.split("\t")
            out.append((p[0], int(p[1]), float(p[2]), int(p[3]), int(p[4])))
        if not out:
            raise ValueError(f"kline_daily 聚合空（warm_start={warm_dt}）——数据管道异常")
        return out

    def _chain_multiply(
        self,
        symbol: str,
        name: str,
        base_date: str,
        base_value: float,
        agg: list[tuple[str, int, float, int, int]],
    ) -> list[tuple]:
        """基期锚定 + 逐日链乘 → 输出行元组（仅 trade_date >= base_date）。

        基期日：close=base_value、ret=0（当日涨跌宽度照写）；此后 close 前复权链乘。
        """
        out: list[tuple] = []
        close = base_value
        anchored = False
        for d, n, ret, adv, dec in agg:
            if d < base_date:
                continue
            if not anchored:
                # 基期日锚定：首个 >= base_date 的聚合日点位=base_value，当日 ret 归零
                out.append((d, symbol, name, round(close, 4), 0.0, n, adv, dec, "internal"))
                anchored = True
                continue
            # 覆盖度防御：n 低于阈值=数据管道异常日，ret 按 0 处理、点位延续（防污染）
            if n < _MIN_COVERAGE:
                log.warning("覆盖度防御触发 %s: n_stocks=%d < %d，ret 按零处理", d, n, _MIN_COVERAGE)
                ret = 0.0
            close = close * (1.0 + ret)
            out.append((d, symbol, name, round(close, 4), round(ret, 8), n, adv, dec, "internal"))
        if not anchored:
            raise ValueError(f"聚合序列早于基期 {base_date} 无数据（agg 首日={agg[0][0]}）")
        return out
