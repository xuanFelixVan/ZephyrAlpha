# [BLUEPRINT] MOD-REGIME_VAL-002 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/12_regime_phase2_validation.md §2.2
# [MODULE] zephyr.regime.validation.phase2.b4_transition_accuracy
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; pyyaml; zephyr.regime.core.regime_detector
# [CONSUMERS] scripts.tests.run_phase2_validation; phase2_runner; BM-BT-05
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] B4只读 detector._last_transitions, 不改其状态; 事件库 YAML 为唯一真源; ±5 交易日窗口用实际交易日历
# [MODIFY-GUARD] 12_regime_phase2_validation.md §2.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] B4ValidationError(ZA-REGIME-0025)
# [TESTS] tests/regime/phase2/test_b4_transition_accuracy.py
# [TTL] permanent
# [ARCH-REF] #12_regime_phase2_validation §2.2 #12_regime_phase2_validation §4.2 B4
"""
B4 转换触发准确性验证器（12_regime_phase2_validation §2.2，Phase 2 第一批 MVP）.

验证问题: HMM 8 转换（T1-T6/S1/S2）触发时点与历史事件吻合吗？

算法:
  1. 接收 phase2_runner 收集的全历史逐日 _last_transitions
     （每日 detect() 后从 detector._last_transitions 读取）
  2. 加载历史事件库 YAML（historical_events.yaml）
  3. 对每个事件: 在事件日 ±5 交易日内查找对应 transition_type 的触发记录
  4. 触发记录的 stage ∈ expected_stage → 命中
  5. 统计命中数 / 总事件数（仅 in_data_range=True 的事件计入分母）

判定: ≥6/8 命中 → PASS

依据: 12_regime_phase2_validation §2.2
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: b4_transition_accuracy.py
# 层: 算法
# - id: A1
#   name_zh: ① B4EventMatch
#   name_en: B4EventMatch
#   intro: 单事件匹配结果。
#   desc: 单事件匹配结果。；公共方法（定义序）: label；源码 L147-L166
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② B4Report
#   name_en: B4Report
#   intro: B4 验证报告。
#   desc: B4 验证报告。；公共方法（定义序）: hit_rate, to_dict；源码 L170-L207
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ B4TransitionAccuracy
#   name_en: B4TransitionAccuracy
#   intro: B4 转换触发准确性验证器。
#   desc: B4 转换触发准确性验证器。 Usage: b4 = B4TransitionAccuracy() events = b4.load_events() # 从默认 YAML #…；公共方法（定义序）: load_eve…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A3 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: B4EventMatch, B4Report, B4TransitionAccuracy
#   downstream: scripts.tests.run_phase2_validation; phase2_runner; BM-BT-05
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment,misc]

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# 8 转换类型（与 regime_detector.TRANSITIONS 对齐）
TRANSITION_TYPES: list[str] = ["T1", "T2", "T3", "T4", "T5", "T6", "S1", "S2"]

# ±5 交易日的窗口宽度（向前/向后各 5 个交易日）
MATCH_WINDOW_DAYS = 5

# 命中门槛（12_regime_phase2_validation §2.2: 8 事件中 ≥6 命中 → PASS）
# 采用比率制（6/8=0.75）以适配任意事件数；total_evaluated=0 时为 INSUFFICIENT_DATA
PASS_RATIO = 0.75

# 历史事件库默认路径（与本文同目录的包内嵌数据——治本迁移：自 docs/02 文档区迁入，
# 消灭"文档归类"误移风险与 parents[N] 长链硬编码，#ARCH-117）
DEFAULT_EVENTS_PATH = Path(__file__).resolve().parent / "historical_events.yaml"


class B4ValidationError(ZephyrBaseError):
    """ZA-REGIME-0025: B4 验证器错误（事件库缺失/格式错/无交易日历）。"""

    error_code = "ZA-REGIME-0025"


class B4Verdict(str, Enum):
    """B4 判定结果。"""

    PASS = "PASS"  # ≥6/8 命中
    FAIL = "FAIL"  # <6/8 命中
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"  # 无可用事件 / 无交易日历


@dataclass(frozen=True)
class HistoricalEvent:
    """历史事件（从 YAML 加载）。"""

    id: str
    date: pd.Timestamp
    transition_type: str  # T1-T6 / S1 / S2
    expected_stage: list[str]  # [trigger, confirm, ...] 任一命中即算
    desc: str
    in_data_range: bool = True  # 是否在 ClickHouse 数据范围内（2008 事件=False）
    data_ready: bool = True  # 触发条件所需维度是否就绪（S2 需 NLP+high/low，未就绪=False，不计 B4 分母）
    design_match: bool = True  # 事件类型是否在当前模型设计域内（S2 Wyckoff 吸筹模板不匹配 A 股 V/政策型复苏=False）


@dataclass(frozen=True)
class B4EventMatch:
    """单事件匹配结果。"""

    event: HistoricalEvent
    hit: bool  # 是否命中
    triggered_at: pd.Timestamp | None  # 实际触发日（None=未触发）
    delta_days: int | None  # 触发日 - 事件日的交易日偏移（+ = 滞后，- = 提前）
    matched_stage: str | None  # 命中的阶段
    total_score: float | None  # 命中转换的总分

    @property
    def label(self) -> str:
        """人类可读标签。"""
        if not self.hit:
            return f"{self.event.id} ✗ 未命中"
        sign = "+" if (self.delta_days or 0) >= 0 else ""
        return (
            f"{self.event.id} ✓ 命中 @ {self.triggered_at.date()} "
            f"({sign}{self.delta_days}d, stage={self.matched_stage})"
        )


@dataclass(frozen=True)
class B4Report:
    """B4 验证报告。"""

    matches: list[B4EventMatch]
    hit_count: int
    total_evaluated: int  # 实际参与判定的事件数（in_data_range=True）
    verdict: B4Verdict
    summary: str
    per_transition_hits: dict[str, dict[str, int]]  # {T_id: {hit, total}}

    @property
    def hit_rate(self) -> float:
        """命中率。"""
        return self.hit_count / self.total_evaluated if self.total_evaluated > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """转 dict（供 JSON 序列化）。"""
        return {
            "matches": [
                {
                    "event_id": m.event.id,
                    "event_date": str(m.event.date.date()),
                    "transition_type": m.event.transition_type,
                    "hit": m.hit,
                    "triggered_at": str(m.triggered_at.date()) if m.triggered_at else None,
                    "delta_days": m.delta_days,
                    "matched_stage": m.matched_stage,
                    "total_score": round(m.total_score, 4) if m.total_score is not None else None,
                }
                for m in self.matches
            ],
            "hit_count": self.hit_count,
            "total_evaluated": self.total_evaluated,
            "verdict": self.verdict.value,
            "summary": self.summary,
            "hit_rate": round(self.hit_rate, 4),
            "per_transition_hits": self.per_transition_hits,
        }


class B4TransitionAccuracy:
    """B4 转换触发准确性验证器。

    Usage:
        b4 = B4TransitionAccuracy()
        events = b4.load_events()  # 从默认 YAML
        # daily_transitions 由 phase2_runner 收集:
        #   {datetime: list[TransitionTriggered]}
        report = b4.validate(daily_transitions, events)

    或直接传 events_path:
        report = b4.validate(daily_transitions, events_path="path/to/events.yaml")
    """

    def load_events(self, events_path: str | Path | None = None) -> list[HistoricalEvent]:
        """从 YAML 加载历史事件库。

        Args:
            events_path: YAML 路径，None 用默认路径（DEFAULT_EVENTS_PATH）。

        Returns:
            HistoricalEvent 列表。
        """
        if yaml is None:
            raise B4ValidationError("PyYAML 未安装，无法加载事件库")
        path = Path(events_path) if events_path else DEFAULT_EVENTS_PATH
        if not path.exists():
            raise B4ValidationError(f"历史事件库不存在: {path}")
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise B4ValidationError(f"事件库 YAML 解析失败: {exc}") from exc
        if not isinstance(data, dict) or "events" not in data:
            raise B4ValidationError(f"事件库格式错误: 缺少 'events' 键: {path}")
        events: list[HistoricalEvent] = []
        for raw in data["events"]:
            events.append(
                HistoricalEvent(
                    id=str(raw["id"]),
                    date=pd.Timestamp(raw["date"]),
                    transition_type=str(raw["transition_type"]),
                    expected_stage=list(raw.get("expected_stage", ["trigger", "confirm"])),
                    desc=str(raw.get("desc", "")),
                    in_data_range=bool(raw.get("in_data_range", True)),
                    data_ready=bool(raw.get("data_ready", True)),
                    design_match=bool(raw.get("design_match", True)),
                )
            )
        _logger.info("B4: 加载 %d 个历史事件 (%s)", len(events), path.name)
        return events

    def validate(
        self,
        daily_transitions: dict[Any, list[Any]],
        events: list[HistoricalEvent] | str | Path | None = None,
        trading_dates: list[Any] | pd.DatetimeIndex | None = None,
    ) -> B4Report:
        """验证转换触发准确性。

        Args:
            daily_transitions: {date: list[TransitionTriggered]}，由 phase2_runner 收集。
                date 可为 datetime / pd.Timestamp / str（内部统一转 Timestamp）。
                TransitionTriggered 需有 transition_type/stage/total_score/triggered 属性。
            events: HistoricalEvent 列表 / YAML 路径 / None（用默认路径加载）。
            trading_dates: 实际交易日历（用于 ±5 交易日窗口）。
                None 时从 daily_transitions 的 keys 排序推导。

        Returns:
            B4Report。
        """
        if isinstance(events, (str, Path)):
            events = self.load_events(events)
        elif events is None:
            events = self.load_events()
        if not events:
            return B4Report(
                matches=[],
                hit_count=0,
                total_evaluated=0,
                verdict=B4Verdict.INSUFFICIENT_DATA,
                summary="B4: 无可用历史事件",
                per_transition_hits={},
            )

        # 统一日期索引
        sorted_dates = self._sorted_dates(daily_transitions, trading_dates)
        if len(sorted_dates) < 1:
            return B4Report(
                matches=[],
                hit_count=0,
                total_evaluated=0,
                verdict=B4Verdict.INSUFFICIENT_DATA,
                summary="B4: 无可用交易日历（daily_transitions 为空）",
                per_transition_hits={},
            )

        # 触发索引: {transition_type: {date: [TransitionTriggered, ...]}}
        trigger_index = self._build_trigger_index(daily_transitions)

        matches: list[B4EventMatch] = []
        for event in events:
            if not event.in_data_range:
                # 超出数据范围的事件不计入分母（仅作标注）
                matches.append(
                    B4EventMatch(
                        event=event,
                        hit=False,
                        triggered_at=None,
                        delta_days=None,
                        matched_stage=None,
                        total_score=None,
                    )
                )
                continue
            if not event.data_ready:
                # 数据未就绪（触发条件依赖的维度缺失）→ 不计入分母，标注"待数据就绪"
                matches.append(
                    B4EventMatch(
                        event=event,
                        hit=False,
                        triggered_at=None,
                        delta_days=None,
                        matched_stage=None,
                        total_score=None,
                    )
                )
                continue
            if not event.design_match:
                # 数据已就绪但事件类型超出当前模型设计域 → 不计入分母，标注"超出设计域"
                # （S2 Wyckoff 吸筹模板不匹配 A 股 V 反转/政策驱动型复苏，待重设计后激活）
                matches.append(
                    B4EventMatch(
                        event=event,
                        hit=False,
                        triggered_at=None,
                        delta_days=None,
                        matched_stage=None,
                        total_score=None,
                    )
                )
                continue
            match = self._match_event(event, sorted_dates, trigger_index)
            matches.append(match)

        # data_ready=False / design_match=False 的事件不计入分母
        # （data_ready: S2 需 NLP+high/low 未就绪；design_match: S2 Wyckoff 模板不匹配 A 股 V/政策型复苏）
        # （HistoricalEvent docstring + historical_events.yaml 注释一致）
        total_evaluated = sum(
            1 for m in matches if m.event.in_data_range and m.event.data_ready and m.event.design_match
        )
        hit_count = sum(1 for m in matches if m.hit)
        per_transition = self._per_transition_stats(matches)

        if total_evaluated == 0:
            verdict = B4Verdict.INSUFFICIENT_DATA
        elif hit_count / total_evaluated >= PASS_RATIO:
            verdict = B4Verdict.PASS
        else:
            verdict = B4Verdict.FAIL
        summary = (
            f"B4 转换触发准确性: {hit_count}/{total_evaluated} 命中 "
            f"({100 * hit_count / max(total_evaluated, 1):.1f}%) → {verdict.value}"
        )
        _logger.info("B4 完成: %s", summary)
        return B4Report(
            matches=matches,
            hit_count=hit_count,
            total_evaluated=total_evaluated,
            verdict=verdict,
            summary=summary,
            per_transition_hits=per_transition,
        )

    # ── 内部 ──────────────────────────────────────────────────────────

    @staticmethod
    def _sorted_dates(
        daily_transitions: dict[Any, list[Any]],
        trading_dates: list[Any] | pd.DatetimeIndex | None,
    ) -> list[pd.Timestamp]:
        """统一日期索引为排序的 Timestamp 列表。"""
        if trading_dates is not None:
            dates = [pd.Timestamp(d) for d in trading_dates]
        else:
            dates = [pd.Timestamp(d) for d in daily_transitions.keys()]
        return sorted(set(dates))

    @staticmethod
    def _build_trigger_index(
        daily_transitions: dict[Any, list[Any]],
    ) -> dict[str, dict[pd.Timestamp, list[Any]]]:
        """构建 {transition_type: {date: [TransitionTriggered]}} 索引。"""
        index: dict[str, dict[pd.Timestamp, list[Any]]] = {tid: {} for tid in TRANSITION_TYPES}
        for raw_date, triggers in daily_transitions.items():
            if not triggers:
                continue
            ts = pd.Timestamp(raw_date)
            for trig in triggers:
                tid = getattr(trig, "transition_type", None)
                if tid in index:
                    index[tid].setdefault(ts, []).append(trig)
        return index

    def _match_event(
        self,
        event: HistoricalEvent,
        sorted_dates: list[pd.Timestamp],
        trigger_index: dict[str, dict[pd.Timestamp, list[Any]]],
    ) -> B4EventMatch:
        """单事件匹配: ±5 交易日内找对应 transition_type 的触发。"""
        # 找事件日附近的交易日窗口
        window_dates = self._trading_window(event.date, sorted_dates, MATCH_WINDOW_DAYS)
        if not window_dates:
            return B4EventMatch(
                event=event,
                hit=False,
                triggered_at=None,
                delta_days=None,
                matched_stage=None,
                total_score=None,
            )

        type_index = trigger_index.get(event.transition_type, {})
        best_match: tuple[pd.Timestamp, Any, int] | None = None  # (date, trig, delta_idx)
        for wd in window_dates:
            trigs = type_index.get(wd)
            if not trigs:
                continue
            # 取 stage ∈ expected_stage 且 triggered=True 的最高分触发
            for trig in trigs:
                stage = getattr(trig, "stage", "none")
                triggered = getattr(trig, "triggered", False)
                if not triggered or stage not in event.expected_stage:
                    continue
                delta_idx = self._delta_trading_days(event.date, wd, sorted_dates)
                if best_match is None:
                    best_match = (wd, trig, delta_idx)
                else:
                    # 取 |delta| 最小的（最接近事件日）
                    if abs(delta_idx) < abs(best_match[2]):
                        best_match = (wd, trig, delta_idx)

        if best_match is None:
            return B4EventMatch(
                event=event,
                hit=False,
                triggered_at=None,
                delta_days=None,
                matched_stage=None,
                total_score=None,
            )
        wd, trig, delta_idx = best_match
        return B4EventMatch(
            event=event,
            hit=True,
            triggered_at=wd,
            delta_days=delta_idx,
            matched_stage=getattr(trig, "stage", None),
            total_score=getattr(trig, "total_score", None),
        )

    @staticmethod
    def _trading_window(
        event_date: pd.Timestamp,
        sorted_dates: list[pd.Timestamp],
        n_days: int,
    ) -> list[pd.Timestamp]:
        """取事件日前后各 n_days 个交易日（共 2*n_days+1）。"""
        if not sorted_dates:
            return []
        # 二分查找事件日位置
        import bisect

        idx = bisect.bisect_left(sorted_dates, event_date)
        start = max(0, idx - n_days)
        end = min(len(sorted_dates), idx + n_days + 1)
        return sorted_dates[start:end]

    @staticmethod
    def _delta_trading_days(
        event_date: pd.Timestamp,
        target_date: pd.Timestamp,
        sorted_dates: list[pd.Timestamp],
    ) -> int:
        """事件日到目标日的交易日偏移（+ = 滞后，- = 提前）。"""
        import bisect

        i_event = bisect.bisect_left(sorted_dates, event_date)
        i_target = bisect.bisect_left(sorted_dates, target_date)
        return i_target - i_event

    @staticmethod
    def _per_transition_stats(
        matches: list[B4EventMatch],
    ) -> dict[str, dict[str, int]]:
        """按 transition_type 统计命中。"""
        stats: dict[str, dict[str, int]] = {tid: {"hit": 0, "total": 0} for tid in TRANSITION_TYPES}
        for m in matches:
            if not m.event.in_data_range or not m.event.data_ready or not m.event.design_match:
                continue
            tid = m.event.transition_type
            if tid in stats:
                stats[tid]["total"] += 1
                if m.hit:
                    stats[tid]["hit"] += 1
        return stats
