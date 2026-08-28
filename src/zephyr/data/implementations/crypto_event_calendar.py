# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.crypto_event_calendar
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.provider_base
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] planned
# [INVARIANTS] 只读公开数据（无需密钥）；事件表为静态公开日程快照+规则展开，确定性输出（同输入恒同输出）；返回 FetchResult 不写 CH
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-010
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未连接->FetchResult(error="crypto_event_calendar 未连接")；不支持 capability->FetchResult(error="unsupported capability")
# [TESTS] tests/zephyr/data/test_crypto_event_calendar.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""币版事件日历 Provider（CAND-CRYPTO-010，94号 §5/§9：减半与解锁事件日历）。

event_calendar 币版实例——采集三类影响币价的中观/宏观事件，统一稀疏事件表输出：
- 减半事件（halving）：BTC/LTC/BCH/ETC/ZEC/DASH 等 PoW 币减半日期。
  历史减半为公开事实；未来减半按 210,000 块周期（ETC=5,000,000 块减产）外推的估计值。
  注：ETH 转 PoS 后无挖矿减半机制，不列入（发行削减由 EIP-1559/Merge 完成）。
- 大额解锁事件（token_unlock）：Token Unlocks 类公开数据快照。
  一次性 cliff 解锁用固定日期表；月度线性解锁按规则在请求区间内展开（有界）。
- 宏观事件（macro_event）：美联储 FOMC 议息决议日 + 美国 CPI 发布日
  （federalreserve.gov / bls.gov 提前公布的官方日程，无需密钥）。

统一行格式：(event_date, event_type, symbol, impact, source)。
- event_date: ISO 日期（YYYY-MM-DD）
- event_type: halving / token_unlock / macro_fomc / macro_cpi
- symbol: 币种代码（BTC/LTC/...）或 MACRO（市场级宏观事件）
- impact: high / medium / low（对价格潜在冲击分级）
- source: 数据来源标识（static_halving_schedule / token_unlocks_public_snapshot /
  federal_reserve / bls）

全部数据为公开静态快照，无网络依赖、无密钥需求；输出确定性（同输入恒同输出），
测试与下游管道可重复。事件日历定位=风险节流输入（sit_out_list/regime），非 alpha 择时。
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Final, Iterator

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.shared.utils.time_utils import now_utc

if TYPE_CHECKING:
    from zephyr.data.policy_registry import SourcePolicy

# 统一事件列名（94号 §5 CAND-CRYPTO-010 事件日历输出契约）
_EVENT_COLUMNS: Final = [
    "event_date",
    "event_type",
    "symbol",
    "impact",
    "source",
]

# ---- 减半事件静态表（公开事实 + 周期外推估计）----
# (symbol, event_date, impact)；source 统一为 static_halving_schedule
# BTC: 每 210,000 块减半（2012-11-28 / 2016-07-09 / 2020-05-11 / 2024-04-20 为事实，2028-03 为外推估计）
# LTC: 每 840,000 块减半（2015-08-25 / 2019-08-05 / 2023-08-02 为事实，2027-07 为外推估计）
# BCH: 随 BTC 块高减半（2020-04-08 / 2024-04-04 为事实，2028-04 为外推估计）
# ETC: 每 5,000,000 块减产 20%（2020-03-17 / 2022-04-25 / 2024-06-01 为事实，2026-08 为外推估计）
# ZEC: 随 BTC 周期减半（2020-11-18 / 2024-11-22 为事实，2028-11 为外推估计）
# DASH: 每年约 -7.1% 发行削减（近似年度事件）
_HALVING_EVENTS: Final[tuple[tuple[str, str, str], ...]] = (
    ("BTC", "2012-11-28", "high"),
    ("BTC", "2016-07-09", "high"),
    ("BTC", "2020-05-11", "high"),
    ("BTC", "2024-04-20", "high"),
    ("BTC", "2028-03-26", "high"),
    ("LTC", "2015-08-25", "medium"),
    ("LTC", "2019-08-05", "medium"),
    ("LTC", "2023-08-02", "medium"),
    ("LTC", "2027-07-30", "medium"),
    ("BCH", "2020-04-08", "medium"),
    ("BCH", "2024-04-04", "medium"),
    ("BCH", "2028-04-01", "medium"),
    ("ETC", "2020-03-17", "low"),
    ("ETC", "2022-04-25", "low"),
    ("ETC", "2024-06-01", "low"),
    ("ETC", "2026-08-15", "low"),
    ("ZEC", "2020-11-18", "low"),
    ("ZEC", "2024-11-22", "low"),
    ("ZEC", "2028-11-20", "low"),
    ("DASH", "2025-06-27", "low"),
    ("DASH", "2026-06-12", "low"),
    ("DASH", "2027-05-28", "low"),
)

# ---- 一次性大额 cliff 解锁（Token Unlocks 公开数据快照）----
# (symbol, event_date, impact)；source 统一为 token_unlocks_public_snapshot
_TOKEN_UNLOCK_ONESHOT: Final[tuple[tuple[str, str, str], ...]] = (
    ("ARB", "2024-03-16", "high"),   # 团队/投资人 cliff（约 11.1 亿枚，公开报道）
    ("APT", "2024-11-12", "high"),   # 投资人/基金会 cliff
    ("SUI", "2024-09-01", "high"),   # 大额 cliff 解锁
    ("SEI", "2024-08-15", "medium"),
    ("STRK", "2024-04-15", "medium"),
    ("IMX", "2024-10-22", "medium"),
    ("OP", "2024-05-31", "medium"),
)

# ---- 月度规则型解锁（公开 vesting 计划，按规则在请求区间内有界展开）----
# (symbol, day_of_month, impact)
_TOKEN_UNLOCK_MONTHLY: Final[tuple[tuple[str, int, str], ...]] = (
    ("APT", 11, "medium"),   # 每月 11 日解锁（社区/基金会月度份额）
    ("SUI", 1, "medium"),    # 每月 1 日解锁
    ("OP", 30, "low"),       # 每月末解锁
    ("STRK", 15, "medium"),  # 每月 15 日解锁
    ("WLD", 25, "low"),      # 每月线性解锁批次
)

# ---- 宏观事件静态表（官方提前公布日程，无需密钥）----
# FOMC 议息决议公布日（federalreserve.gov 公布的 2026 会议日程，决议=会议第二日）
_FOMC_DATES_2026: Final = (
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
    "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-09",
)
# 美国 CPI 发布日（bls.gov 公布的 2026 发布日程）
_CPI_DATES_2026: Final = (
    "2026-01-13", "2026-02-11", "2026-03-11", "2026-04-10",
    "2026-05-12", "2026-06-10", "2026-07-14", "2026-08-12",
    "2026-09-11", "2026-10-13", "2026-11-10", "2026-12-10",
)
# (event_date, event_type, impact, source)；symbol 统一为 MACRO
_MACRO_EVENTS: Final[tuple[tuple[str, str, str, str], ...]] = tuple(
    [(d, "macro_fomc", "high", "federal_reserve") for d in _FOMC_DATES_2026]
    + [(d, "macro_cpi", "high", "bls") for d in _CPI_DATES_2026]
)

# 月度解锁展开的默认窗口（start/end 未传时）：前 1 年 ~ 后 2 年（事件日历前瞻属性）
_DEFAULT_WINDOW_PAST_DAYS: Final = 365
_DEFAULT_WINDOW_FUTURE_DAYS: Final = 730


class CryptoEventCalendarProvider(IngestProviderBase):
    """币版事件日历 Provider（减半/大额解锁/宏观事件）。

    全部数据为公开静态快照，无需密钥、无网络依赖；输出确定性。
    shared 线程安全模型（无状态）。
    """

    source_name: str = "crypto_event_calendar"
    meta: IngestProviderMeta = IngestProviderMeta(
        name="crypto_event_calendar",
        display_name="币版事件日历(减半/解锁/宏观)",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,  # 纯静态数据，无外部调用，不限频
        capabilities=[
            CapabilityContract(
                "crypto_halving",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,
                expected_market="crypto",
                expected_variety="calendar",
            ),
            CapabilityContract(
                "crypto_token_unlock",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,
                expected_market="crypto",
                expected_variety="calendar",
            ),
            CapabilityContract(
                "crypto_macro_event",
                supports_symbols_null=True,
                supports_incremental=True,
                supports_full_refresh=True,
                requires_date_range=False,
                expected_market="crypto",
                expected_variety="calendar",
            ),
        ],
        known_issues=[
            "未来减半日期为区块周期外推估计（实际受算力波动影响）",
            "Token 解锁为公开快照+月度规则展开，项目方可能临时调整解锁计划",
            "宏观事件表按年度官方日程维护，跨年需滚动更新静态表",
            "ETH 无 PoW 减半机制（PoS），其发行削减不列入 halving 事件",
        ],
    )

    # ---- 生命周期 ----

    def connect(self) -> None:
        """建立连接：纯静态公开数据，无需密钥/网络，直接标记连接。"""
        self._connected = True
        self._log.info("币版事件日历已连接（静态公开数据，无外部依赖）")

    def health_check(self) -> bool:
        """探活：静态数据恒可用，连接态即健康。"""
        return self._connected

    def disconnect(self) -> None:
        """断开连接：无状态，直接标记断开。"""
        self._connected = False
        self._log.info("币版事件日历已断开")

    # ---- 拉取入口 ----

    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """按 capability 路由到减半/解锁/宏观事件采集。"""
        if not self._connected:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error="crypto_event_calendar 未连接",
            )
            return

        capability = (payload.extra or {}).get("capability", "")
        if capability == "crypto_halving":
            yield from self._fetch_halving(payload)
        elif capability == "crypto_token_unlock":
            yield from self._fetch_token_unlock(payload)
        elif capability == "crypto_macro_event":
            yield from self._fetch_macro_event(payload)
        else:
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=0.0,
                error=f"unsupported capability: {capability}",
            )

    # ---- capability 拉取入口（CAP-CONSISTENCY：每 capability 一个 _fetch_<cap> 方法） ----

    def _fetch_halving(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """减半事件：静态表按日期+symbols 过滤。"""
        t0 = now_utc()
        symbols = {s.upper() for s in payload.symbols} if payload.symbols else None
        rows = []
        for symbol, event_date, impact in _HALVING_EVENTS:
            if symbols is not None and symbol not in symbols:
                continue
            if not _in_range(event_date, payload.start, payload.end):
                continue
            rows.append((event_date, "halving", symbol, impact, "static_halving_schedule"))
        rows.sort(key=lambda r: r[0])
        yield FetchResult(
            table=payload.table,
            columns=_EVENT_COLUMNS,
            rows=rows,
            last_key=rows[-1][0] if rows else "",
            elapsed_sec=(now_utc() - t0).total_seconds(),
        )

    def _fetch_token_unlock(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """大额解锁事件：一次性 cliff 静态表 + 月度规则有界展开。"""
        t0 = now_utc()
        symbols = {s.upper() for s in payload.symbols} if payload.symbols else None
        rows = []
        for symbol, event_date, impact in _TOKEN_UNLOCK_ONESHOT:
            if symbols is not None and symbol not in symbols:
                continue
            if not _in_range(event_date, payload.start, payload.end):
                continue
            rows.append((event_date, "token_unlock", symbol, impact, "token_unlocks_public_snapshot"))
        for event_date, symbol, impact in _expand_monthly_unlocks(payload, symbols):
            rows.append((event_date, "token_unlock", symbol, impact, "token_unlocks_public_snapshot"))
        rows.sort(key=lambda r: r[0])
        yield FetchResult(
            table=payload.table,
            columns=_EVENT_COLUMNS,
            rows=rows,
            last_key=rows[-1][0] if rows else "",
            elapsed_sec=(now_utc() - t0).total_seconds(),
        )

    def _fetch_macro_event(self, payload: FetchPayload) -> Iterator[FetchResult]:
        """宏观事件：FOMC 议息决议日 + CPI 发布日（官方日程静态表）。"""
        t0 = now_utc()
        rows = []
        for event_date, event_type, impact, source in _MACRO_EVENTS:
            if not _in_range(event_date, payload.start, payload.end):
                continue
            rows.append((event_date, event_type, "MACRO", impact, source))
        rows.sort(key=lambda r: r[0])
        yield FetchResult(
            table=payload.table,
            columns=_EVENT_COLUMNS,
            rows=rows,
            last_key=rows[-1][0] if rows else "",
            elapsed_sec=(now_utc() - t0).total_seconds(),
        )


def _in_range(event_date: str, start: datetime.date | None, end: datetime.date | None) -> bool:
    """ISO 日期字符串是否在 [start, end] 闭区间内（None=该端不限）。"""
    day = datetime.date.fromisoformat(event_date)
    if start is not None and day < start:
        return False
    if end is not None and day > end:
        return False
    return True


def _expand_monthly_unlocks(
    payload: FetchPayload,
    symbols: set[str] | None,
) -> Iterator[tuple[str, str, str]]:
    """月度规则解锁在请求区间内有界展开为 (event_date, symbol, impact)。

    start/end 未传时使用默认窗口（今天-365d ~ 今天+730d），保证展开有界。
    月末日期合法性处理：day_of_month 超过当月天数时取当月最后一天
    （如 OP=30 在 2 月落到 02-28/02-29）。
    """
    today = datetime.date.today()
    start = payload.start or (today - datetime.timedelta(days=_DEFAULT_WINDOW_PAST_DAYS))
    end = payload.end or (today + datetime.timedelta(days=_DEFAULT_WINDOW_FUTURE_DAYS))

    for symbol, day_of_month, impact in _TOKEN_UNLOCK_MONTHLY:
        if symbols is not None and symbol not in symbols:
            continue
        year, month = start.year, start.month
        while datetime.date(year, month, 1) <= end:
            # 月末钳制：day_of_month 超当月天数时取当月最后一天
            if month == 12:
                next_month_first = datetime.date(year + 1, 1, 1)
            else:
                next_month_first = datetime.date(year, month + 1, 1)
            month_last_day = (next_month_first - datetime.timedelta(days=1)).day
            day = datetime.date(year, month, min(day_of_month, month_last_day))
            if start <= day <= end:
                yield (day.isoformat(), symbol, impact)
            if month == 12:
                year, month = year + 1, 1
            else:
                month += 1
