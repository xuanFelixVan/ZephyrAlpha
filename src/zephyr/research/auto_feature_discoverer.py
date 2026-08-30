# [BLUEPRINT] MOD-FAC-001 | docs/03_modules/_domain_factor/auto_feature_discoverer/blueprint.md
# [MODULE] zephyr.research.auto_feature_discoverer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（协议核心纯内存；ic_calculator/clock 全注入）
# [CONSUMERS] 运行时装配批（研究轨特征发现入口 / 因子库草稿治理串行合并）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 算子模板词表闭合（基础序列 open|high|low|close|volume；算术 add|sub|mul|div；滚动 mean|std|max|min|sum；窗口词表闭合）；表达式集合=词表笛卡尔组合，排序后枚举 feature_id 确定性；IC/IR 初筛仅经注入 ic_calculator（未注入 Fail-Closed）；TopN 截断按 (-|ic|,-|ir|,expression) 确定性排序；候选先入人工确认队列，confirm 方可入库，未确认不入库；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_factor/auto_feature_discoverer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AutoFeatureError(占位 ZA-FAC-UNREGISTERED-AUTO-FEATURE)——词表外基础序列/非法窗口/阈值越界/ic_calculator 缺失或返回非法/未知 feature_id 确认或拒绝时抛
# [TESTS] tests/research/test_auto_feature_discoverer.py
# [A_module] module_id=MOD-FAC-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
AutoFeatureDiscoverer — AI 自动特征发现器（MOD-FAC-001）。

B1-00630（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-016，C2 74）：价量算子
模板库（算术/滚动统计算子词表闭合）**笛卡尔组合**批量生成特征 + IC/IR 初筛
（注入 ic 计算器）+ TopN **人工确认队列**（未确认不入库）。

查重分工（蓝图 §0）：factor_mining_pipeline=论文→LLM 假说→沙箱五段链（外部知
识驱动）；本件=价量算子模板**组合枚举**驱动（无 LLM、无论文），产出仅入内存
确认队列，禁直改 factor_registry（同候选草稿治理口径，由运行时装配批串行合并）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ic_calculator 参数
#   fields: 参数 ic_calculator（无注解）
#   code: auto_feature_discoverer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: min_ic 参数
#   fields: 参数 min_ic（无注解）
#   code: auto_feature_discoverer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: min_ir 参数
#   fields: 参数 min_ir（无注解）
#   code: auto_feature_discoverer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: top_n 参数
#   fields: 参数 top_n（无注解）
#   code: auto_feature_discoverer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AutoFeatureDiscoverer
#   name_en: AutoFeatureDiscoverer
#   intro: 价量算子模板组合特征发现器（生成 + IC/IR 初筛 + TopN 人工确认队列）。
#   desc: 价量算子模板组合特征发现器（生成 + IC/IR 初筛 + TopN 人工确认队列）。 Args: ic_calculator: 注入 IC/IR 计算器，签名 ``expres…；公共方法（定义序）: generat…
#   inputs: ic_calculator min_ic min_ir top_n base_series windows clock
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: AutoFeatureDiscoverer
#   downstream: 运行时装配批（研究轨特征发现入口 / 因子库草稿治理串行合并）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "ARITH_OPS",
    "BASE_SERIES",
    "DEFAULT_WINDOWS",
    "ROLLING_OPS",
    "AutoFeatureDiscoverer",
    "AutoFeatureError",
    "FeatureCandidate",
    "FeatureFamily",
    "QueuedFeature",
]

#: 价量基础序列词表（闭合）
BASE_SERIES: Final = ("open", "high", "low", "close", "volume")
#: 算术算子词表（闭合，二元）
ARITH_OPS: Final = ("add", "sub", "mul", "div")
#: 滚动统计算子词表（闭合，一元+窗口）
ROLLING_OPS: Final = ("mean", "std", "max", "min", "sum")
#: 默认滚动窗口词表（闭合）
DEFAULT_WINDOWS: Final = (5, 10, 20)


class AutoFeatureError(Exception):
    """特征发现输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-AUTO-FEATURE。
    """


class FeatureFamily(str, Enum):
    """特征族（词表闭合）。"""

    ROLLING = "rolling"
    ARITH = "arith"


@dataclass(frozen=True)
class FeatureCandidate:
    """初筛入围特征候选（frozen）。"""

    feature_id: str
    expression: str
    family: FeatureFamily
    ic: float
    ir: float


@dataclass(frozen=True)
class QueuedFeature:
    """人工确认队列条目（frozen）。"""

    candidate: FeatureCandidate
    queued_at: datetime.datetime


class AutoFeatureDiscoverer:
    """价量算子模板组合特征发现器（生成 + IC/IR 初筛 + TopN 人工确认队列）。

    Args:
        ic_calculator: 注入 IC/IR 计算器，签名 ``expression -> (ic, ir)``。
        min_ic: |IC| 初筛下限（∈ [0,1)）。
        min_ir: |IR| 初筛下限（≥ 0）。
        top_n: 每批发现入队上限（≥1）。
        base_series: 基础序列词表（None=默认五档价量；词表外即拒）。
        windows: 滚动窗口词表（None=默认 5/10/20；正整数，词表外即拒）。
        clock: 注入时钟（队列留痕用）。
    """

    def __init__(
        self,
        *,
        ic_calculator: Callable[[str], tuple[float, float]] | None,
        min_ic: float = 0.02,
        min_ir: float = 0.0,
        top_n: int = 10,
        base_series: Sequence[str] | None = None,
        windows: Sequence[int] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if ic_calculator is None:
            raise AutoFeatureError("ic_calculator 未注入（IC/IR 初筛强制注入，Fail-Closed）")
        if not (0.0 <= float(min_ic) < 1.0):
            raise AutoFeatureError(f"min_ic 非法（须 ∈ [0,1)）: {min_ic!r}")
        if float(min_ir) < 0.0:
            raise AutoFeatureError(f"min_ir 非法（须 ≥ 0）: {min_ir!r}")
        if isinstance(top_n, bool) or int(top_n) < 1:
            raise AutoFeatureError(f"top_n 非法（须 ≥1）: {top_n!r}")
        series = tuple(base_series) if base_series is not None else BASE_SERIES
        if not series:
            raise AutoFeatureError("base_series 为空（无基础序列可组合）")
        unknown = sorted({s for s in series if s not in BASE_SERIES})
        if unknown:
            raise AutoFeatureError(f"base_series 含词表外序列: {unknown}（词表：{list(BASE_SERIES)}）")
        if len(set(series)) != len(series):
            raise AutoFeatureError("base_series 含重复序列")
        wins = tuple(int(w) for w in (windows if windows is not None else DEFAULT_WINDOWS))
        if not wins:
            raise AutoFeatureError("windows 为空（无滚动窗口可组合）")
        if any(w < 2 for w in wins):
            raise AutoFeatureError(f"windows 含非法窗口（须 ≥2）: {wins!r}")
        if len(set(wins)) != len(wins):
            raise AutoFeatureError("windows 含重复窗口")
        self._ic_calculator = ic_calculator
        self._min_ic = float(min_ic)
        self._min_ir = float(min_ir)
        self._top_n = int(top_n)
        self._series = series
        self._windows = tuple(sorted(wins))
        self._clock = clock or datetime.datetime.now
        self._queue: dict[str, QueuedFeature] = {}
        self._confirmed: dict[str, FeatureCandidate] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _family_of(self, expression: str) -> FeatureFamily:
        return FeatureFamily.ROLLING if expression.startswith("roll_") else FeatureFamily.ARITH

    def _calc_ic_ir(self, expression: str) -> tuple[float, float]:
        try:
            ic, ir = self._ic_calculator(expression)
        except AutoFeatureError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise AutoFeatureError(f"ic_calculator 异常: {expression!r}（{type(exc).__name__}）") from exc
        if not isinstance(ic, (int, float)) or isinstance(ic, bool):
            raise AutoFeatureError(f"ic_calculator 返回非法 ic: {ic!r}（expression={expression!r}）")
        if not isinstance(ir, (int, float)) or isinstance(ir, bool):
            raise AutoFeatureError(f"ic_calculator 返回非法 ir: {ir!r}（expression={expression!r}）")
        return float(ic), float(ir)

    # ── 生成（词表闭合笛卡尔组合） ─────────────────────────────────────────

    def generate_expressions(self) -> tuple[str, ...]:
        """笛卡尔组合批量生成表达式（排序去重，确定性）。"""
        out: list[str] = []
        for op in ROLLING_OPS:
            for base in self._series:
                for w in self._windows:
                    out.append(f"roll_{op}({base},{w})")
        for op in ARITH_OPS:
            for a in self._series:
                for b in self._series:
                    if a != b:
                        out.append(f"{op}({a},{b})")
        return tuple(sorted(set(out)))

    # ── 初筛（IC/IR 注入） ────────────────────────────────────────────────

    def screen(self, expressions: Sequence[str] | None = None) -> tuple[FeatureCandidate, ...]:
        """IC/IR 初筛 + 确定性排序（(-|ic|,-|ir|,expression)）+ feature_id 枚举。"""
        exprs = tuple(expressions) if expressions is not None else self.generate_expressions()
        if not exprs:
            raise AutoFeatureError("expressions 为空（无候选可筛）")
        for expr in exprs:
            if not isinstance(expr, str) or not expr.strip():
                raise AutoFeatureError(f"表达式非法（须非空字符串）: {expr!r}")
        scored: list[tuple[float, float, str]] = []
        for expr in dict.fromkeys(e.strip() for e in exprs):
            ic, ir = self._calc_ic_ir(expr)
            if abs(ic) >= self._min_ic and abs(ir) >= self._min_ir:
                scored.append((ic, ir, expr))
        scored.sort(key=lambda t: (-abs(t[0]), -abs(t[1]), t[2]))
        return tuple(
            FeatureCandidate(
                feature_id=f"AF-{i + 1:04d}",
                expression=expr,
                family=self._family_of(expr),
                ic=ic,
                ir=ir,
            )
            for i, (ic, ir, expr) in enumerate(scored)
        )

    # ── 发现（TopN → 人工确认队列） ────────────────────────────────────────

    def discover(self) -> tuple[FeatureCandidate, ...]:
        """生成 + 初筛 + TopN 截断 → 入人工确认队列（已确认者不再入队，幂等）。"""
        top = self.screen()[: self._top_n]
        now = self._clock()
        for cand in top:
            if cand.feature_id in self._confirmed:
                continue
            if cand.feature_id not in self._queue:
                self._queue[cand.feature_id] = QueuedFeature(candidate=cand, queued_at=now)
        _log.info("特征发现入队: %d 候选（TopN=%d）", len(top), self._top_n)
        return top

    # ── 人工确认（未确认不入库硬约束） ─────────────────────────────────────

    def pending_queue(self) -> tuple[QueuedFeature, ...]:
        """待确认队列（入队顺序，确定性）。"""
        return tuple(self._queue.values())

    def confirm(self, feature_id: str) -> FeatureCandidate:
        """人工确认：队列 → 已确认库（未知/已处理 id Fail-Closed）。"""
        entry = self._queue.pop(feature_id, None)
        if entry is None:
            raise AutoFeatureError(f"未知或已处理 feature_id: {feature_id!r}（仅待确认条目可确认）")
        self._confirmed[feature_id] = entry.candidate
        _log.info("特征人工确认入库: %s %s", feature_id, entry.candidate.expression)
        return entry.candidate

    def reject(self, feature_id: str) -> FeatureCandidate:
        """人工拒绝：移出队列（未知/已处理 id Fail-Closed）。"""
        entry = self._queue.pop(feature_id, None)
        if entry is None:
            raise AutoFeatureError(f"未知或已处理 feature_id: {feature_id!r}（仅待确认条目可拒绝）")
        _log.info("特征人工拒绝: %s %s", feature_id, entry.candidate.expression)
        return entry.candidate

    def confirmed_features(self) -> tuple[FeatureCandidate, ...]:
        """已确认入库视图（按 feature_id 确定性排序）。"""
        return tuple(self._confirmed[k] for k in sorted(self._confirmed))
