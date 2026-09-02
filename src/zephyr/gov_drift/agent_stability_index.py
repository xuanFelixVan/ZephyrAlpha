# [BLUEPRINT] MOD-GOV-055 | docs/03_modules/_domain_gov_drift/agent_stability_index/blueprint.md
# [MODULE] zephyr.gov_drift.agent_stability_index
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] 无（协议核心纯内存；embedder/event_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（Agent 交互流接入 / gov_drift 事件路由 / 周频盘后语义批）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 50交互滚动窗(deque定长滑窗); ASI=组件加权均值(缺组件权重归一化); ASI<阈值连续N窗告警且每 streak 仅告警一次; embedder 缺失/零向量/维度不符 Fail-Closed 不旁路; 告警回调异常不阻断评估; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_gov_drift/agent_stability_index/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AgentStabilityError(占位 ZA-GOVDRIFT-UNREGISTERED-AGENT-STABILITY)——非法record/未知agent/窗未满强制评估/embedder异常或零向量/非法构造参数时抛
# [TESTS] tests/gov_drift/test_agent_stability_index.py
# [A_module] module_id=MOD-GOV-055 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""AgentStabilityIndex — Agent 稳定度指数检查器（MOD-GOV-055）。

B11-03056（AUD-DRAFT-001-DIGEST P2 波 P2-W12，CAND-GOVDRIFT-003，A7）：
ASI 可落子集——响应**语义一致性**（embedding 余弦，embedder 注入）+
工具调用序列 **Levenshtein 稳定性** + 推理路径**编辑距离** + 多 Agent
**一致率**，50 交互滚动窗，ASI<0.75 连续 3 窗告警 + 落 gov_drift 事件
回调 + 周频盘后语义。canonical 承接 GOVDRIFT-002 归并（调用模式/工具
分布基线语义并入工具序列与推理路径分量）。

查重分工（蓝图 §0）：drift_engine=数据/概念漂移检测（本件=Agent 行为
漂移，不碰数据分布）；alert_router=告警路由实现（本件仅经注入事件回
调落事件，不实现路由）。
"""

from __future__ import annotations

import datetime
import logging
import math
from collections import deque
from dataclasses import dataclass
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AgentStabilityError",
    "AgentStabilityIndex",
    "DriftEvent",
    "InteractionRecord",
    "StabilityReport",
]

#: ASI 组件默认权重（缺组件时按在场组件归一化）
_DEFAULT_WEIGHTS: Final[dict[str, float]] = {
    "semantic": 0.4,
    "tool": 0.2,
    "path": 0.2,
    "agreement": 0.2,
}

_COMPONENT_KEYS: Final = frozenset(_DEFAULT_WEIGHTS)


class AgentStabilityError(Exception):
    """Agent 稳定度评估输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-GOVDRIFT-UNREGISTERED-AGENT-STABILITY。
    """


@dataclass(frozen=True)
class InteractionRecord:
    """单条 Agent 交互记录（滚动窗元素，frozen）。

    agreed：多 Agent 一致标记；None 表示本交互无一致率语义（该组件
    在窗内无样本时从 ASI 加权中剔除并归一化）。
    """

    agent_id: str
    response_text: str
    tool_sequence: tuple[str, ...]
    reasoning_path: tuple[str, ...]
    agreed: bool | None
    ts: datetime.datetime


@dataclass(frozen=True)
class StabilityReport:
    """单窗 ASI 评估报告（留痕载体，frozen）。"""

    agent_id: str
    window_size: int
    semantic_score: float
    tool_score: float
    path_score: float
    agreement_rate: float | None
    asi: float
    consecutive_low: int
    alerted: bool
    evaluated_at: datetime.datetime


@dataclass(frozen=True)
class DriftEvent:
    """gov_drift 漂移事件（告警载荷，连续低窗触发）。"""

    agent_id: str
    asi: float
    consecutive_low: int
    reason: str
    raised_at: datetime.datetime


def _levenshtein(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    """两序列编辑距离（纯内存 DP，确定性）。"""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[lb]


def _sequence_stability(seqs: list[tuple[str, ...]]) -> float:
    """相邻序列稳定度均值：1 - 归一化编辑距离；空-空对视为完全一致。"""
    scores: list[float] = []
    for prev, cur in zip(seqs, seqs[1:]):
        denom = max(len(prev), len(cur))
        scores.append(1.0 if denom == 0 else 1.0 - _levenshtein(prev, cur) / denom)
    return sum(scores) / len(scores) if scores else 1.0


class AgentStabilityIndex:
    """Agent 稳定度指数件（滚动窗 + 四分量 ASI + 连续低窗告警）。"""

    def __init__(
        self,
        *,
        embedder: Callable[[str], tuple[float, ...]] | None,
        clock: Callable[[], datetime.datetime] | None = None,
        event_sink: Callable[[DriftEvent], None] | None = None,
        window_size: int = 50,
        asi_threshold: float = 0.75,
        alert_consecutive: int = 3,
        weights: Mapping[str, float] | None = None,
    ) -> None:
        if embedder is None:
            # 语义一致性为 ASI 核心分量：embedder 未注入 Fail-Closed，不旁路
            raise AgentStabilityError("embedder 未注入（语义一致性分量强制，禁止旁路）")
        if window_size < 2:
            raise AgentStabilityError(f"window_size 须 >= 2: {window_size!r}")
        if not 0.0 < asi_threshold <= 1.0:
            raise AgentStabilityError(f"asi_threshold 须在 (0, 1]: {asi_threshold!r}")
        if alert_consecutive < 1:
            raise AgentStabilityError(f"alert_consecutive 须 >= 1: {alert_consecutive!r}")
        merged = dict(_DEFAULT_WEIGHTS)
        if weights is not None:
            for key, value in weights.items():
                if key not in _COMPONENT_KEYS:
                    raise AgentStabilityError(f"未知 ASI 组件权重: {key!r}")
                if value <= 0.0:
                    raise AgentStabilityError(f"组件权重须为正: {key}={value!r}")
            merged.update(weights)
        self._embedder = embedder
        self._clock = clock or datetime.datetime.now
        self._event_sink = event_sink
        self._window_size = window_size
        self._threshold = asi_threshold
        self._alert_consecutive = alert_consecutive
        self._weights = merged
        self._buffers: dict[str, deque[InteractionRecord]] = {}
        self._reports: dict[str, list[StabilityReport]] = {}
        self._consecutive_low: dict[str, int] = {}
        self._events: list[DriftEvent] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> tuple[float, ...]:
        try:
            vec = tuple(float(x) for x in self._embedder(text))
        except AgentStabilityError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入 embedder 异常按 Fail-Closed 包装
            raise AgentStabilityError(f"embedder 调用异常: {exc!r}") from exc
        if not vec:
            raise AgentStabilityError("embedder 返回空向量")
        return vec

    @staticmethod
    def _cosine(u: tuple[float, ...], v: tuple[float, ...]) -> float:
        if len(u) != len(v):
            raise AgentStabilityError(f"embedding 维度不符: {len(u)} vs {len(v)}")
        dot = sum(a * b for a, b in zip(u, v))
        nu = math.sqrt(sum(a * a for a in u))
        nv = math.sqrt(sum(b * b for b in v))
        if nu == 0.0 or nv == 0.0:
            raise AgentStabilityError("embedder 返回零向量（余弦无定义）")
        return dot / (nu * nv)

    def _semantic_score(self, texts: list[str]) -> float:
        vecs = [self._embed(t) for t in texts]
        scores = [self._cosine(u, v) for u, v in zip(vecs, vecs[1:])]
        return sum(scores) / len(scores) if scores else 1.0

    def _validate_record(self, record: InteractionRecord) -> None:
        if not isinstance(record, InteractionRecord):
            raise AgentStabilityError(f"非法 record 类型: {type(record).__name__}")
        if not record.agent_id:
            raise AgentStabilityError("agent_id 为空")
        if not isinstance(record.response_text, str):
            raise AgentStabilityError("response_text 须为 str")
        for name, seq in (("tool_sequence", record.tool_sequence), ("reasoning_path", record.reasoning_path)):
            if not isinstance(seq, tuple) or any(not isinstance(s, str) for s in seq):
                raise AgentStabilityError(f"{name} 须为 tuple[str, ...]")
        if record.agreed is not None and not isinstance(record.agreed, bool):
            raise AgentStabilityError(f"agreed 须为 bool|None: {record.agreed!r}")

    def _evaluate_records(self, agent_id: str, records: list[InteractionRecord]) -> StabilityReport:
        semantic = self._semantic_score([r.response_text for r in records])
        tool = _sequence_stability([r.tool_sequence for r in records])
        path = _sequence_stability([r.reasoning_path for r in records])
        agreed_samples = [r.agreed for r in records if r.agreed is not None]
        agreement = (sum(1 for a in agreed_samples if a) / len(agreed_samples)) if agreed_samples else None

        components = {"semantic": semantic, "tool": tool, "path": path}
        if agreement is not None:
            components["agreement"] = agreement
        total_w = sum(self._weights[k] for k in components)
        asi = sum(self._weights[k] * v for k, v in components.items()) / total_w

        low = self._consecutive_low.get(agent_id, 0)
        low = low + 1 if asi < self._threshold else 0
        self._consecutive_low[agent_id] = low
        alerted = low == self._alert_consecutive
        report = StabilityReport(
            agent_id=agent_id,
            window_size=len(records),
            semantic_score=semantic,
            tool_score=tool,
            path_score=path,
            agreement_rate=agreement,
            asi=asi,
            consecutive_low=low,
            alerted=alerted,
            evaluated_at=self._clock(),
        )
        self._reports.setdefault(agent_id, []).append(report)
        if alerted:
            self._emit(report)
        return report

    def _emit(self, report: StabilityReport) -> None:
        event = DriftEvent(
            agent_id=report.agent_id,
            asi=report.asi,
            consecutive_low=report.consecutive_low,
            reason=(
                f"ASI={report.asi:.4f} < 阈值 {self._threshold} 连续 {report.consecutive_low} 窗（Agent 行为漂移）"
            ),
            raised_at=self._clock(),
        )
        self._events.append(event)
        _log.warning("Agent 稳定度告警: %s (%s)", event.agent_id, event.reason)
        if self._event_sink is not None:
            try:
                self._event_sink(event)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("event_sink 告警失败")

    # ── 交互接入 ──────────────────────────────────────────────────────────

    def record_interaction(self, record: InteractionRecord) -> StabilityReport | None:
        """接入交互：校验 → 入滚动窗；窗满即评估并返回报告，否则返回 None。"""
        self._validate_record(record)
        buf = self._buffers.setdefault(record.agent_id, deque(maxlen=self._window_size))
        buf.append(record)
        if len(buf) < self._window_size:
            return None
        return self._evaluate_records(record.agent_id, list(buf))

    def evaluate(self, agent_id: str) -> StabilityReport:
        """强制评估当前缓冲（>=2 条即可；未知 agent/样本不足 Fail-Closed）。"""
        if not agent_id:
            raise AgentStabilityError("agent_id 为空")
        buf = self._buffers.get(agent_id)
        if buf is None:
            raise AgentStabilityError(f"未知 agent: {agent_id!r}（无交互记录）")
        if len(buf) < 2:
            raise AgentStabilityError(f"样本不足: {agent_id!r} 当前 {len(buf)} 条，须 >= 2")
        return self._evaluate_records(agent_id, list(buf))

    # ── 查询 ─────────────────────────────────────────────────────────────

    def reports(self, agent_id: str) -> tuple[StabilityReport, ...]:
        """单 agent 评估留痕（按评估序，确定性）。"""
        if not agent_id:
            raise AgentStabilityError("agent_id 为空")
        return tuple(self._reports.get(agent_id, ()))

    def buffered(self, agent_id: str) -> int:
        """当前滚动窗内样本数。"""
        if not agent_id:
            raise AgentStabilityError("agent_id 为空")
        buf = self._buffers.get(agent_id)
        return len(buf) if buf is not None else 0

    def consecutive_low(self, agent_id: str) -> int:
        """当前连续低窗计数。"""
        if not agent_id:
            raise AgentStabilityError("agent_id 为空")
        return self._consecutive_low.get(agent_id, 0)

    @property
    def events(self) -> tuple[DriftEvent, ...]:
        """已落 gov_drift 事件（按触发序，确定性）。"""
        return tuple(self._events)
