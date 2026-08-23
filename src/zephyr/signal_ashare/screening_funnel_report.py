# [BLUEPRINT] MOD-SIG-067 | 待统筹登记（缺口总账 GAP-F-11 + 21号 memo §3.6 漏斗容量链）
# [MODULE] zephyr.signal_ashare.screening_funnel_report
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.tiered_screening_filter（MOD-SIG-046 消费）; zephyr.signal_ashare.coarse_screening_funnel（MOD-SIG-047 消费）; zephyr.signal_ashare.fine_scoring_engine（MOD-SIG-048 消费）; zephyr.signal_ashare.event_driven_screener（MOD-SIG-049 消费）
# [CONSUMERS] 盘中实时页决策链漏斗（L1-L6 每层命中明细）; （候选：作战室 W1 作战池层 L6 链接入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只计数不改筛选（四层 Result 只读消费，本模块零筛选逻辑）；排除原因按"前缀:维度"分桶（参数化部分归并）；in_count 缺省=len(kept)+len(excluded)（截断层须显式注入）；非单调链留痕不炸；L5/L6=扩展位（组合/风控层、作战池层以自定义 FunnelStageStat 注入，本模块不实现）；纯函数无副作用；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-11 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] in_count<0/trade_date 非法/stage_from_fine 缺 in_count→ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_screening_funnel_report.py
# [A_module] module_id=MOD-SIG-067 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""ScreeningFunnelReport — 筛选漏斗 L1-L6 全链计数器 (MOD-SIG-067)

缺口总账 GAP-F-11 落码：盘中实时页决策链漏斗（宇宙→1200→300→50→…→作战池
每层命中明细结构化）。消费批2 漏斗四件产出（只读适配，筛选逻辑零改动）：

    | 层 | 模块 | 语义（21号 §3.6 容量链） |
    |---|---|---|
    | L1 | MOD-SIG-046 tiered_screening_filter | 分级指标过滤（四排除机制，~7000→~1200） |
    | L2 | MOD-SIG-047 coarse_screening_funnel | 五维初筛+容量截断（~1200→~300） |
    | L3 | MOD-SIG-048 fine_scoring_engine | 六要素精筛 Top-N（~300→~50） |
    | L4 | MOD-SIG-049 event_driven_screener | 事件驱动筛选（~50→~30） |
    | L5/L6 | 扩展位 | 组合/风控层、作战池层（GAP-F-06），自定义 stage 注入 |

每层产出：入数/出数/通过率/保留清单/排除原因分桶计数/truncated/degraded/
skipped 标记。全链 chain=[宇宙数]+各层出数；非单调（出>入）留痕 note
（数据质量观察，不炸）。

不做什么：不重算筛选（适配器只读 Result）/不实现 L5/L6 筛选（扩展位注入）/
         不落库（输出契约供前端/编排层消费，落库属后续波次）。

依据: 缺口总账 GAP-F-11；21_stock_selection_engine §3.6；CAND-SIG-013/018 语义
SSoT: depgraph MOD-SIG-067（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 四层筛选 Result（046/047/048/049）+ universe_count + 扩展 stage（L5/L6 注入位）
# 特征: 入数/出数/通过率/排除原因分桶（"前缀:维度"归并参数化）
# 算法: 四层适配器 → FunnelStageStat；build 合成全链 chain + 非单调留痕
# 输出: ScreeningFunnelReport（stages/chain/notes，纯 frozen dataclass JSON 可序列化）
"""

from __future__ import annotations

import datetime
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Final

from zephyr.signal_ashare.coarse_screening_funnel import CoarseScreenResult
from zephyr.signal_ashare.event_driven_screener import EventScreenResult
from zephyr.signal_ashare.fine_scoring_engine import FineScoreResult
from zephyr.signal_ashare.tiered_screening_filter import TieredFilterResult

__all__: Final = [
    "FunnelStageStat",
    "ScreeningFunnelReport",
    "build_funnel_report",
    "stage_from_coarse",
    "stage_from_event",
    "stage_from_fine",
    "stage_from_tiered",
]

#: 排除原因分桶正则（"dim:volume_ratio(1.20<=1.5)"→"dim:volume_ratio"）
_REASON_BUCKET_RE: Final = re.compile(r"^([a-z_]+:[a-z_0-9]+)")

_DATE_RE: Final = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_trade_date(trade_date: object) -> str:
    """交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(trade_date, str) or not _DATE_RE.fullmatch(trade_date):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD）: {trade_date!r}")
    try:
        datetime.date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    return trade_date


def _bucket_reasons(excluded: dict[str, str]) -> dict[str, int]:
    """排除原因分桶计数：参数化部分归并到"前缀:维度"桶（无匹配桶原样计数）。"""
    buckets: dict[str, int] = {}
    for reason in excluded.values():
        m = _REASON_BUCKET_RE.match(str(reason))
        bucket = m.group(1) if m else str(reason)
        buckets[bucket] = buckets.get(bucket, 0) + 1
    return buckets


@dataclass(frozen=True, slots=True)
class FunnelStageStat:
    """漏斗单层命中明细（结构化，前端每层直读）。

    Attributes:
        stage_id: 层号（L1~L6；扩展层自定义语义）
        name_zh: 层名（中文可审计）
        in_count: 入数（本层输入标的数）
        out_count: 出数（本层保留标的数）
        kept: 保留标的清单（输入顺序；大层由调用方截断注入）
        excluded_reasons: 排除原因分桶计数 {桶: 数}
        truncated: 容量截断标记（047/049 透传）
        degraded: 降级标记（各层透传）
        skipped: 跳过标记（049 无事件源直通）
        notes: 留痕（出>入等数据质量观察）
    """

    stage_id: str
    name_zh: str
    in_count: int
    out_count: int
    kept: tuple[str, ...] = ()
    excluded_reasons: dict[str, int] = field(default_factory=dict)
    truncated: bool = False
    degraded: bool = False
    skipped: bool = False
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.in_count < 0:
            raise ValueError(f"in_count 非法（须非负）: {self.in_count}")
        if self.out_count < 0:
            raise ValueError(f"out_count 非法（须非负）: {self.out_count}")
        if not isinstance(self.stage_id, str) or not self.stage_id.strip():
            raise ValueError(f"stage_id 非法（须非空字符串）: {self.stage_id!r}")


# ------------------------------------------------------------------
# 四层适配器（只读消费批2产出，筛选逻辑零改动）
# ------------------------------------------------------------------


def _infer_in_count(kept: tuple[str, ...], excluded: dict[str, str], in_count: int | None) -> int:
    """in_count 缺省推导 = len(kept)+len(excluded)（截断层须显式注入）。"""
    if in_count is not None:
        if in_count < 0:
            raise ValueError(f"in_count 非法（须非负）: {in_count}")
        return in_count
    return len(kept) + len(excluded)


def _out_exceeds_note(stage_id: str, in_count: int, out_count: int) -> list[str]:
    """出>入数据质量留痕（不炸，非单调由 build 层二次观察）。"""
    if out_count > in_count:
        return [f"{stage_id} 出>入（in_count={in_count} < out_count={out_count}），in_count 可能未含截断/直通部分"]
    return []


def stage_from_tiered(
    result: TieredFilterResult,
    *,
    in_count: int | None = None,
    stage_id: str = "L1",
) -> FunnelStageStat:
    """L1 适配：MOD-SIG-046 分级指标过滤产出 → FunnelStageStat。"""
    n_in = _infer_in_count(result.kept, result.excluded, in_count)
    return FunnelStageStat(
        stage_id=stage_id,
        name_zh="分级指标过滤（物理/门禁/分级/概率四排除）",
        in_count=n_in,
        out_count=len(result.kept),
        kept=result.kept,
        excluded_reasons=_bucket_reasons(result.excluded),
        degraded=result.degraded,
        notes=_out_exceeds_note(stage_id, n_in, len(result.kept)),
    )


def stage_from_coarse(
    result: CoarseScreenResult,
    *,
    in_count: int | None = None,
    stage_id: str = "L2",
) -> FunnelStageStat:
    """L2 适配：MOD-SIG-047 五维初筛产出 → FunnelStageStat（truncated 透传）。"""
    n_in = _infer_in_count(result.kept, result.excluded, in_count)
    notes = _out_exceeds_note(stage_id, n_in, len(result.kept))
    if result.truncated and in_count is None:
        notes.append("容量截断层未显式注入 in_count（截断部分不计入排除），入数为下限口径")
    return FunnelStageStat(
        stage_id=stage_id,
        name_zh="五维初筛+容量截断",
        in_count=n_in,
        out_count=len(result.kept),
        kept=result.kept,
        excluded_reasons=_bucket_reasons(result.excluded),
        truncated=result.truncated,
        degraded=result.degraded,
        notes=notes,
    )


def stage_from_fine(
    result: FineScoreResult,
    *,
    in_count: int | None = None,
    stage_id: str = "L3",
) -> FunnelStageStat:
    """L3 适配：MOD-SIG-048 精筛 Top-N 产出 → FunnelStageStat。

    精筛产出只含 Top-N（kept），无排除清单——in_count 必须由调用方显式注入
    （=L2 出数），被截断部分计入 "rank:below_top_n" 语义桶。

    Raises:
        ValueError: in_count 缺失/非负校验失败（fail-closed）。
    """
    if in_count is None:
        raise ValueError("stage_from_fine 必须显式注入 in_count（精筛产出无排除清单，=L2 出数）")
    if in_count < 0:
        raise ValueError(f"in_count 非法（须非负）: {in_count}")
    out = len(result.top)
    excluded = {"rank:below_top_n": in_count - out} if in_count > out else {}
    return FunnelStageStat(
        stage_id=stage_id,
        name_zh="六要素精筛 Top-N",
        in_count=in_count,
        out_count=out,
        kept=tuple(e.symbol for e in result.top),
        excluded_reasons=excluded,
        degraded=result.degraded,
        notes=_out_exceeds_note(stage_id, in_count, out),
    )


def stage_from_event(
    result: EventScreenResult,
    *,
    in_count: int | None = None,
    stage_id: str = "L4",
) -> FunnelStageStat:
    """L4 适配：MOD-SIG-049 事件驱动筛选产出 → FunnelStageStat（skipped 透传）。"""
    n_in = _infer_in_count(result.kept, result.excluded, in_count)
    return FunnelStageStat(
        stage_id=stage_id,
        name_zh="事件驱动筛选（利空/极端反应/传导风险三剔除）",
        in_count=n_in,
        out_count=len(result.kept),
        kept=result.kept,
        excluded_reasons=_bucket_reasons(result.excluded),
        truncated=result.truncated,
        degraded=result.degraded,
        skipped=result.skipped,
        notes=_out_exceeds_note(stage_id, n_in, len(result.kept)),
    )


# ------------------------------------------------------------------
# 全链报告
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScreeningFunnelReport:
    """筛选漏斗全链计数报告（盘中实时页决策链消费契约，JSON 可序列化）。"""

    trade_date: str
    stages: tuple[FunnelStageStat, ...] = ()
    chain: tuple[int, ...] = ()  # [宇宙数（若给）]+ 各层出数
    universe_count: int | None = None  # L0 宇宙数（全市场/候选宇宙）
    annotations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（pass_rate 派生计算）。"""
        payload = asdict(self)
        payload["stages"] = [
            {
                **stage_dict,
                "kept": list(stage_dict["kept"]),
                "pass_rate": (round(s.out_count / s.in_count, 6) if s.in_count > 0 else None),
            }
            for s, stage_dict in zip(self.stages, payload["stages"], strict=True)
        ]
        payload["chain"] = list(self.chain)
        return payload


def build_funnel_report(
    trade_date: str,
    stages: list[FunnelStageStat] | tuple[FunnelStageStat, ...],
    *,
    universe_count: int | None = None,
    annotations: list[str] | tuple[str, ...] = (),
) -> ScreeningFunnelReport:
    """全链报告合成：chain=[universe]+各层出数；非单调留痕（不炸）。

    Args:
        trade_date: 交易日 YYYY-MM-DD（fail-closed）。
        stages: 各层命中明细（四层适配器产出 + L5/L6 扩展位注入）；空合法。
        universe_count: L0 宇宙数（None=chain 从 L1 出数起）。
        annotations: 附加注解链。

    Returns:
        ScreeningFunnelReport。

    Raises:
        ValueError: trade_date / universe_count 非法（fail-closed）。
    """
    v_date = _validate_trade_date(trade_date)
    if universe_count is not None and universe_count < 0:
        raise ValueError(f"universe_count 非法（须非负）: {universe_count}")

    stage_list = list(stages)
    chain: list[int] = ([universe_count] if universe_count is not None else []) + [
        s.out_count for s in stage_list
    ]
    notes: list[str] = []
    for prev, cur in zip(chain, chain[1:], strict=False):
        if cur > prev:
            notes.append(f"漏斗链非单调（{prev}→{cur}），数据质量观察留痕")
    degraded_layers = [s.stage_id for s in stage_list if s.degraded]
    if degraded_layers:
        notes.append(f"降级层: {degraded_layers}（对应层按降级口径产出，消费方注意）")
    skipped_layers = [s.stage_id for s in stage_list if s.skipped]
    if skipped_layers:
        notes.append(f"跳过层（直通不筛）: {skipped_layers}")

    ann = list(annotations)
    if stage_list:
        ann.append(f"筛选漏斗 {len(stage_list)} 层全链计数已出（{chain[0] if chain else 0}→…→{chain[-1] if chain else 0}）")

    return ScreeningFunnelReport(
        trade_date=v_date,
        stages=tuple(stage_list),
        chain=tuple(chain),
        universe_count=universe_count,
        annotations=ann,
        notes=notes,
    )
