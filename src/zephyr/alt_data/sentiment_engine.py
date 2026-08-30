# [BLUEPRINT] MOD-ALT-004 | docs/03_modules/_domain_alt_data/sentiment_engine/blueprint.md
# [MODULE] zephyr.alt_data.sentiment_engine
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors（判定核心纯内存；历史序列 history_provider 注入）
# [CONSUMERS] 运行时装配批（价量情绪分接 sentiment_cycle 产出 / 社媒分接 social_sentiment_collector 日频聚合 / 新闻分接 news_sentiment_analyzer；输出入 C-014 大盘预测与筛选漏斗）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 判定核心纯内存无IO；单条非法Fail-Closed到条；composite恒∈[-1,1]、percentile恒∈[0,1]（clip保证）；PIT严格（历史仅取<trade_date且在window_days内）；样本<min_history→INSUFFICIENT_HISTORY不出伪判定；冰点/过热阈值严格小于/大于（恰等不命中）；frozen dataclass asdict JSON可序列化；同输入必同输出；仅信号输入语义无下单含义
# [MODIFY-GUARD] docs/03_modules/_domain_alt_data/sentiment_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] trade_date非法/symbol空白/分越界→InvalidSentimentInputError（单条Fail-Closed）；权重负/窗口非正/min_history负/阈值越界/ice_pct≥overheat_pct/history_provider非callable→InvalidSentimentConfigError（构造期Fail-Closed）；history_provider运行期异常→该条rejected留痕不阻断
# [TESTS] tests/alt_data/test_sentiment_engine.py
# [A_module] module_id=MOD-ALT-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



SentimentEngine — 统一情绪引擎（MOD-ALT-004）

B1-00112（AUD-DRAFT-001-DIGEST P1 波 W-P1-14，D-ALT-02）：聚合价量情绪（复用
sentiment_cycle 产出口径）+ 社媒/新闻情感分（采集/打分面产物注入）→ 复合
情绪分 → 252 日滚动历史分位数 → 冰点（<10 分位）/过热（>90 分位）统一判定，
输出入 C-014 大盘预测与筛选漏斗。

查重裁定：sentiment_cycle=价量情绪五阶段周期定位（价量面产出）；
social_sentiment_collector（MOD-ALT-001）=帖子级社媒文本**采集**+日频聚合；
news_sentiment_analyzer（MOD-INT-AISA）=新闻情感**打分**；sentiment_aggregator
（MOD-NLP-AGGREGATOR-001）=跨**新闻源**一致性投票；extreme_sentiment_reversal_
detector（MOD-SIG-099）=极端情绪**反转事件检测**。本模块为跨**类别**聚合
+历史分位状态判定引擎，与采集/打分/投票/检测各面正交不重复。LLM 能力不内嵌，
分数一律注入；仅信号输入语义，无下单含义。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: sentiment_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: history_provider 参数
#   fields: 参数 history_provider（无注解）
#   code: sentiment_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SentimentEngine
#   name_en: SentimentEngine
#   intro: 统一情绪引擎（跨类别聚合 + 历史分位状态判定核心）。
#   desc: 统一情绪引擎（跨类别聚合 + 历史分位状态判定核心）。 Args: config: SentimentEngineConfig（None=默认） history_provider…；公共方法（定义序）: config,…
#   inputs: config history_provider
#   outputs: 返回值
#   （注：A1 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: SentimentEngine
#   downstream: 运行时装配批（价量情绪分接 sentiment_cycle 产出 / 社媒分接 social_sentiment_collector 日频聚合 / 新闻分接…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Final, Optional

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "HistoryPoint",
    "InvalidSentimentConfigError",
    "InvalidSentimentInputError",
    "SentimentDaily",
    "SentimentEngine",
    "SentimentEngineConfig",
    "SentimentEngineReport",
    "SentimentInput",
    "SentimentState",
]


class InvalidSentimentInputError(ZephyrBaseError):
    """情绪输入行非法（Fail-Closed 到条）。"""


class InvalidSentimentConfigError(ZephyrBaseError):
    """情绪引擎配置非法（构造期 Fail-Closed）。"""


class SentimentState(str, Enum):
    """情绪状态（历史分位判定）。"""

    ICE = "ICE"  # 冰点（percentile < ice_pct）
    NORMAL = "NORMAL"  # 常态
    OVERHEAT = "OVERHEAT"  # 过热（percentile > overheat_pct）
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"  # 样本不足不出判定


def _score_or_none(name: str, value: float | None) -> float | None:
    if value is None:
        return None
    v = float(value)
    if not math.isfinite(v) or v < -1.0 or v > 1.0:
        raise InvalidSentimentInputError(f"{name} 必须 ∈ [-1,1] 有限值: {value}")
    return v


def _clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class SentimentInput:
    """单日单标的三路情绪分输入（frozen；至少一路非 None）。"""

    trade_date: datetime.date
    symbol: str
    price_volume_score: float | None = None  # 价量情绪分（sentiment_cycle 产出口径）
    social_score: float | None = None  # 社媒情感分（MOD-ALT-001 日频聚合）
    news_score: float | None = None  # 新闻情感分（MOD-INT-AISA 打分面）

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, datetime.date) or isinstance(self.trade_date, datetime.datetime):
            raise InvalidSentimentInputError(f"trade_date 必须为 date: {type(self.trade_date).__name__}")
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise InvalidSentimentInputError(f"symbol 不能为空: {self.symbol!r}")
        pv = _score_or_none("price_volume_score", self.price_volume_score)
        sc = _score_or_none("social_score", self.social_score)
        nw = _score_or_none("news_score", self.news_score)
        if pv is None and sc is None and nw is None:
            raise InvalidSentimentInputError("三路分至少一路非 None")
        object.__setattr__(self, "price_volume_score", pv)
        object.__setattr__(self, "social_score", sc)
        object.__setattr__(self, "news_score", nw)
        object.__setattr__(self, "symbol", self.symbol.strip())


@dataclass(frozen=True)
class HistoryPoint:
    """历史复合分点（frozen；history_provider 注入口径）。"""

    trade_date: datetime.date
    composite: float

    def __post_init__(self) -> None:
        if not isinstance(self.trade_date, datetime.date) or isinstance(self.trade_date, datetime.datetime):
            raise InvalidSentimentInputError(f"history trade_date 必须为 date: {type(self.trade_date).__name__}")
        v = float(self.composite)
        if not math.isfinite(v):
            raise InvalidSentimentInputError(f"history composite 必须为有限值: {self.composite}")
        object.__setattr__(self, "composite", v)


@dataclass(frozen=True)
class SentimentDaily:
    """单日单标情绪判定输出（frozen）。"""

    trade_date: datetime.date
    symbol: str
    composite: float
    percentile: float | None  # 样本不足为 None
    state: SentimentState
    components_present: int  # 在场分路数（1~3）


@dataclass(frozen=True)
class SentimentEngineReport:
    """批量判定报告（frozen；errors 为 (索引, 原因) 留痕）。"""

    rows_in: int
    accepted: int
    rejected: int
    records: tuple[SentimentDaily, ...]
    ice_count: int
    overheat_count: int
    errors: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class SentimentEngineConfig:
    """引擎配置（C 类可调；默认值=候选 spec 真源）。"""

    weight_price_volume: float = 0.4
    weight_social: float = 0.3
    weight_news: float = 0.3
    window_days: int = 252  # 历史窗（日历日口径，对应 252 交易日滚动的注入面）
    min_history: int = 20  # 最小历史样本数
    ice_pct: float = 0.10  # 冰点线（严格小于）
    overheat_pct: float = 0.90  # 过热线（严格大于）

    def __post_init__(self) -> None:
        for name in ("weight_price_volume", "weight_social", "weight_news"):
            w = float(getattr(self, name))
            if not math.isfinite(w) or w < 0:
                raise InvalidSentimentConfigError(f"{name} 必须为非负有限值: {getattr(self, name)}")
        if self.weight_price_volume + self.weight_social + self.weight_news <= 0:
            raise InvalidSentimentConfigError("三路权重和必须为正")
        if isinstance(self.window_days, bool) or not isinstance(self.window_days, int) or self.window_days <= 0:
            raise InvalidSentimentConfigError(f"window_days 必须为正 int: {self.window_days}")
        if isinstance(self.min_history, bool) or not isinstance(self.min_history, int) or self.min_history < 0:
            raise InvalidSentimentConfigError(f"min_history 必须为非负 int: {self.min_history}")
        for name in ("ice_pct", "overheat_pct"):
            p = float(getattr(self, name))
            if not math.isfinite(p) or p < 0.0 or p > 1.0:
                raise InvalidSentimentConfigError(f"{name} 必须 ∈ [0,1]: {getattr(self, name)}")
        if self.ice_pct >= self.overheat_pct:
            raise InvalidSentimentConfigError(f"ice_pct({self.ice_pct}) 必须 < overheat_pct({self.overheat_pct})")


class SentimentEngine:
    """统一情绪引擎（跨类别聚合 + 历史分位状态判定核心）。

    Args:
        config: SentimentEngineConfig（None=默认）
        history_provider: (symbol, trade_date) -> Sequence[HistoryPoint] 注入
            历史复合分序列（PIT 由本引擎过滤：仅取 < trade_date 且 window_days
            内）；None=空历史（全部 INSUFFICIENT_HISTORY）。运行期异常 →
            该条 rejected 留痕不阻断。
    """

    def __init__(
        self,
        config: SentimentEngineConfig | None = None,
        history_provider: Callable[[str, datetime.date], Sequence[HistoryPoint]] | None = None,
    ) -> None:
        if config is not None and not isinstance(config, SentimentEngineConfig):
            raise InvalidSentimentConfigError(f"config 类型非法: {type(config).__name__}")
        if history_provider is not None and not callable(history_provider):
            raise InvalidSentimentConfigError(
                f"history_provider 必须为 callable 或 None: {type(history_provider).__name__}"
            )
        self._config = config or SentimentEngineConfig()
        self._history_provider = history_provider

    @property
    def config(self) -> SentimentEngineConfig:
        return self._config

    def _composite(self, row: SentimentInput) -> tuple[float, int]:
        pairs: list[tuple[float, float]] = []
        if row.price_volume_score is not None:
            pairs.append((row.price_volume_score, self._config.weight_price_volume))
        if row.social_score is not None:
            pairs.append((row.social_score, self._config.weight_social))
        if row.news_score is not None:
            pairs.append((row.news_score, self._config.weight_news))
        w_sum = sum(w for _, w in pairs)
        if w_sum <= 0:
            # 在场路权重全 0 → 等权兜底（如实按在场路等权）
            composite = sum(s for s, _ in pairs) / len(pairs)
        else:
            composite = sum(s * w for s, w in pairs) / w_sum
        return _clip(composite, -1.0, 1.0), len(pairs)

    def _window_history(self, symbol: str, trade_date: datetime.date) -> list[float]:
        if self._history_provider is None:
            return []
        raw = self._history_provider(symbol, trade_date)
        earliest = trade_date - datetime.timedelta(days=self._config.window_days)
        out: list[float] = []
        for point in raw or []:
            hp = point if isinstance(point, HistoryPoint) else HistoryPoint(*point)  # type: ignore[arg-type]
            if hp.trade_date < trade_date and hp.trade_date >= earliest:  # PIT 严格 < 当日
                out.append(hp.composite)
        return out

    def evaluate_one(self, row: SentimentInput) -> SentimentDaily:
        """单条判定（输入非法→InvalidSentimentInputError；provider 异常→上抛由 evaluate 兜底）。"""
        if not isinstance(row, SentimentInput):
            raise InvalidSentimentInputError(f"row 类型非法: {type(row).__name__}")
        composite, present = self._composite(row)
        history = self._window_history(row.symbol, row.trade_date)
        if len(history) < self._config.min_history:
            return SentimentDaily(
                trade_date=row.trade_date,
                symbol=row.symbol,
                composite=composite,
                percentile=None,
                state=SentimentState.INSUFFICIENT_HISTORY,
                components_present=present,
            )
        percentile = _clip(sum(1 for h in history if h <= composite) / len(history), 0.0, 1.0)
        if percentile < self._config.ice_pct:
            state = SentimentState.ICE
        elif percentile > self._config.overheat_pct:
            state = SentimentState.OVERHEAT
        else:
            state = SentimentState.NORMAL
        return SentimentDaily(
            trade_date=row.trade_date,
            symbol=row.symbol,
            composite=composite,
            percentile=percentile,
            state=state,
            components_present=present,
        )

    def evaluate(self, rows: Sequence[SentimentInput | Mapping[str, object]]) -> SentimentEngineReport:
        """批量判定：非法行 rejected 留痕不阻断；records 按 (trade_date, symbol) 排序。"""
        records: list[SentimentDaily] = []
        errors: list[tuple[int, str]] = []
        for idx, raw in enumerate(rows or []):
            try:
                row = (
                    raw if isinstance(raw, SentimentInput) else SentimentInput(**raw)  # type: ignore[arg-type]
                )
                records.append(self.evaluate_one(row))
            except Exception as exc:  # noqa: BLE001 —— 单条 Fail-Closed 到条
                errors.append((idx, f"{type(exc).__name__}: {exc}"))
        records.sort(key=lambda r: (r.trade_date, r.symbol))
        return SentimentEngineReport(
            rows_in=len(rows or []),
            accepted=len(records),
            rejected=len(errors),
            records=tuple(records),
            ice_count=sum(1 for r in records if r.state is SentimentState.ICE),
            overheat_count=sum(1 for r in records if r.state is SentimentState.OVERHEAT),
            errors=tuple(errors),
        )
