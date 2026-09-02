# [BLUEPRINT] MOD-RK-41 | docs/03_modules/_domain_risk/risk_signal_sequencer/blueprint.md
# [MODULE] zephyr.risk.risk_signal_sequencer
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 调用方按事件到达序逐条 ingest(运行时装配批); MOD-L06-001(风控层执行编排分工); MOD-SIG-088(风险事件消费处置分工); D_GOV_AUDIT(顺序违规留痕)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 风控恒胜:活跃阻断期内信号永不ADMITTED; 乱序必检出必REVOKE必留痕; 幂等去重同id不重复处置; CLEAR后信号放行; 判定核心纯内存无IO(audit_sink注入); 非法输入Fail-Closed到条; 同输入序列必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_risk/risk_signal_sequencer/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 字段空白/时间非法/SYMBOL缺symbol→InvalidSequencerEventError; audit_sink非callable→InvalidSequencerConfigError; audit_sink运行期异常→sink_errors计数不阻断
# [TESTS] tests/risk/test_risk_signal_sequencer.py
# [A_module] module_id=MOD-RK-41 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""Risk-Signal Interaction Sequencer — 风险-信号交互排序器 (MOD-RK-41, CAND-RSK-045, B14-04732)

A9 运维架构 §8.3.13（D-SIGNAL-72）落码：风控 veto/降级/解除事件优先于新信号
生效的全序规则 + 乱序检测 + 冲突仲裁——风控不可被信号绕过，顺序违规写审计链。

与既有件分工（W-P1-14 探查结论）：risk_layer_orchestrator（MOD-L06-001）为
风控层**运行时执行编排**（回撤/VaR/熔断/清算）；risk_event_consumer
（MOD-SIG-088）为 E-RK-01 风险事件→信号域降级处置的**消费处理器**
（幂等/DLQ/回执）。本模块为**全序定序判定核心**（谁先谁后/乱序仲裁），
口径不重复。

纪律：纯内存无 IO；事件由调用方按到达序注入（不做消息传输）；降级/清算
执行面委托既有风控族，本件只产仲裁记录；SUPPRESSED/REVOKED/ORDER_VIOLATION
经 audit_sink 回调留痕（委托 D_GOV_AUDIT，装配批接线）；audit_sink 异常
不阻断判定。

依据: blueprint.md（MOD-RK-41）§1 全序规则；construction_backlog_dig.tsv B14-04732
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 风控事件 RiskEvent
#   fields: event_id + kind(VETO/DOWNGRADE/CLEAR) + scope(GLOBAL/SYMBOL) + symbol + occurred_at + seq
#   code: ingest_risk() 参数
# - id: I2
#   name: 信号事件 SignalEvent
#   fields: signal_id + symbol + occurred_at + seq
#   code: ingest_signal() 参数
# 层: 算法
# - id: A1
#   name_zh: ① 全序判定：活跃阻断期内信号 SUPPRESSED
#   name_en: _admit_or_suppress
#   intro: 覆盖范围(GLOBAL 全覆盖/SYMBOL 同标的)存在未解除 VETO/DOWNGRADE(occurred_at≤信号)→SUPPRESSED 留痕，否则 ADMITTED
# - id: A2
#   name_zh: ② 乱序检测+仲裁：后到更早风控事件→已生效信号 REVOKED
#   name_en: _revoke_violated
#   intro: 风控事件到达时发现同范围已 ADMITTED 且 (occurred_at,seq) 晚于本事件的信号→ORDER_VIOLATION+REVOKE_SIGNAL+审计
# - id: A3
#   name_zh: ③ CLEAR 解除：同范围最新阻断被 CLEAR 关闭
#   name_en: _apply_clear
#   intro: CLEAR 关闭覆盖范围内活跃阻断；解除后新信号 ADMITTED
# 层: 输出
# - id: O1
#   name: ArbitrationRecord
#   fields: subject_id/action(ADMITTED/SUPPRESSED/REVOKED)/reason/violation/deduped/risk_event_id（frozen）
# 边:
# I1 --> A2
# I1 --> A3
# I2 --> A1
# A1 --> O1
# A2 --> O1
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import datetime
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ArbitrationAction",
    "ArbitrationRecord",
    "InvalidSequencerConfigError",
    "InvalidSequencerEventError",
    "RiskEvent",
    "RiskEventKind",
    "RiskScope",
    "RiskSignalSequencer",
    "SignalEvent",
]


class InvalidSequencerEventError(ZephyrBaseError):
    """定序事件字段非法（Fail-Closed 到条）。"""


class InvalidSequencerConfigError(ZephyrBaseError):
    """定序器配置非法（构造期 Fail-Closed）。"""


class RiskEventKind(str, Enum):
    """风控事件类型。"""

    VETO = "VETO"  # 否决（禁止生效）
    DOWNGRADE = "DOWNGRADE"  # 降级（限权生效）
    CLEAR = "CLEAR"  # 解除（关闭活跃阻断）


class RiskScope(str, Enum):
    """风控事件覆盖范围。"""

    GLOBAL = "GLOBAL"  # 全市场/全标的
    SYMBOL = "SYMBOL"  # 单标的（必带 symbol）


class ArbitrationAction(str, Enum):
    """仲裁动作（仅定序语义；执行面委托既有风控族）。"""

    ADMITTED = "ADMITTED"  # 信号获准生效
    SUPPRESSED = "SUPPRESSED"  # 信号被活跃阻断压制（不可绕过风控）
    REVOKED = "REVOKED"  # 已生效信号因乱序风控事件被撤销


def _require_text(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidSequencerEventError(f"{name} 不能为空: {value!r}")
    return value.strip()


def _require_time(name: str, value: datetime.datetime) -> datetime.datetime:
    if not isinstance(value, datetime.datetime):
        raise InvalidSequencerEventError(f"{name} 必须为 datetime: {type(value).__name__}")
    return value


def _require_seq(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidSequencerEventError(f"seq 必须为 int: {type(value).__name__}")
    return value


@dataclass(frozen=True)
class RiskEvent:
    """风控事件（frozen；occurred_at=事件发生时刻，seq=同源全序序号）。"""

    event_id: str
    kind: RiskEventKind
    scope: RiskScope
    symbol: str  # scope=SYMBOL 必填；GLOBAL 可为空串
    occurred_at: datetime.datetime
    seq: int

    def __post_init__(self) -> None:
        _require_text("event_id", self.event_id)
        if not isinstance(self.kind, RiskEventKind):
            raise InvalidSequencerEventError(f"kind 类型非法: {type(self.kind).__name__}")
        if not isinstance(self.scope, RiskScope):
            raise InvalidSequencerEventError(f"scope 类型非法: {type(self.scope).__name__}")
        if self.scope is RiskScope.SYMBOL:
            _require_text("symbol", self.symbol)
        _require_time("occurred_at", self.occurred_at)
        _require_seq(self.seq)

    @property
    def order_key(self) -> tuple[datetime.datetime, int]:
        return (self.occurred_at, self.seq)


@dataclass(frozen=True)
class SignalEvent:
    """新信号事件（frozen）。"""

    signal_id: str
    symbol: str
    occurred_at: datetime.datetime
    seq: int

    def __post_init__(self) -> None:
        _require_text("signal_id", self.signal_id)
        _require_text("symbol", self.symbol)
        _require_time("occurred_at", self.occurred_at)
        _require_seq(self.seq)

    @property
    def order_key(self) -> tuple[datetime.datetime, int]:
        return (self.occurred_at, self.seq)


@dataclass(frozen=True)
class ArbitrationRecord:
    """单事件仲裁记录（frozen；violation=True 即顺序违规已写审计）。"""

    subject_id: str  # 信号 id 或风控事件 id
    action: ArbitrationAction
    reason: str
    violation: bool
    deduped: bool
    risk_event_id: str  # 关联风控事件（无则空串）


class RiskSignalSequencer:
    """风险-信号交互定序器（全序规则+乱序检测+冲突仲裁判定核心）。

    Args:
        audit_sink: SUPPRESSED/REVOKED/风控侧违规记录回调（委托 D_GOV_AUDIT；
            None=仅返回不留痕）。回调异常不阻断判定，sink_errors 如实计数。
    """

    def __init__(self, audit_sink: Callable[[ArbitrationRecord], None] | None = None) -> None:
        if audit_sink is not None and not callable(audit_sink):
            raise InvalidSequencerConfigError(f"audit_sink 必须为 callable 或 None: {type(audit_sink).__name__}")
        self._audit_sink = audit_sink
        self._risk_seen: dict[str, ArbitrationAction] = {}  # event_id → 处置（幂等）
        self._risk_events: dict[str, RiskEvent] = {}
        self._signal_seen: dict[str, ArbitrationRecord] = {}  # signal_id → 首判（幂等）
        self._admitted: dict[str, SignalEvent] = {}  # 当前生效中的信号
        self._blocks: list[RiskEvent] = []  # 活跃阻断（VETO/DOWNGRADE，未 CLEAR）
        self._sink_errors = 0

    @property
    def sink_errors(self) -> int:
        return self._sink_errors

    def _emit(self, record: ArbitrationRecord) -> None:
        if self._audit_sink is None:
            return
        try:
            self._audit_sink(record)
        except Exception:  # noqa: BLE001 —— 留痕失败不阻断判定
            self._sink_errors += 1

    @staticmethod
    def _covers(block: RiskEvent, symbol: str) -> bool:
        return block.scope is RiskScope.GLOBAL or block.symbol == symbol

    def _active_block_for(self, symbol: str, order_key: tuple[datetime.datetime, int]) -> RiskEvent | None:
        """覆盖 symbol 且发生于 order_key 之前/同时的最新活跃阻断。"""
        candidates = [b for b in self._blocks if self._covers(b, symbol) and b.order_key <= order_key]
        if not candidates:
            return None
        return max(candidates, key=lambda b: b.order_key)

    def active_blocks(self, symbol: str | None = None) -> tuple[RiskEvent, ...]:
        """活跃阻断快照（symbol=None 全量；否则仅覆盖该标的者）。"""
        if symbol is None:
            return tuple(self._blocks)
        return tuple(b for b in self._blocks if self._covers(b, symbol))

    def ingest_signal(self, event: SignalEvent) -> ArbitrationRecord:
        """按全序规则判定新信号：活跃阻断期内 SUPPRESSED，否则 ADMITTED。"""
        if not isinstance(event, SignalEvent):
            raise InvalidSequencerEventError(f"event 类型非法: {type(event).__name__}")
        if event.signal_id in self._signal_seen:
            first = self._signal_seen[event.signal_id]
            return ArbitrationRecord(
                subject_id=first.subject_id,
                action=first.action,
                reason=first.reason + "（重复到达，返回首判）",
                violation=first.violation,
                deduped=True,
                risk_event_id=first.risk_event_id,
            )
        block = self._active_block_for(event.symbol, event.order_key)
        if block is not None:
            record = ArbitrationRecord(
                subject_id=event.signal_id,
                action=ArbitrationAction.SUPPRESSED,
                reason=(
                    f"覆盖范围内活跃阻断 {block.event_id}({block.kind.value},"
                    f"{block.occurred_at.isoformat()}#{block.seq}) 先生效→信号不可绕过风控"
                ),
                violation=False,
                deduped=False,
                risk_event_id=block.event_id,
            )
            self._emit(record)
        else:
            record = ArbitrationRecord(
                subject_id=event.signal_id,
                action=ArbitrationAction.ADMITTED,
                reason="覆盖范围无活跃阻断→信号生效",
                violation=False,
                deduped=False,
                risk_event_id="",
            )
            self._admitted[event.signal_id] = event
        self._signal_seen[event.signal_id] = record
        return record

    def ingest_risk(self, event: RiskEvent) -> list[ArbitrationRecord]:
        """处置风控事件：幂等去重；CLEAR 关阻断；VETO/DOWNGRADE 开阻断并乱序仲裁。"""
        if not isinstance(event, RiskEvent):
            raise InvalidSequencerEventError(f"event 类型非法: {type(event).__name__}")
        if event.event_id in self._risk_seen:
            return [
                ArbitrationRecord(
                    subject_id=event.event_id,
                    action=self._risk_seen[event.event_id],
                    reason="重复风控事件→不重复处置",
                    violation=False,
                    deduped=True,
                    risk_event_id=event.event_id,
                )
            ]
        records: list[ArbitrationRecord] = []
        if event.kind is RiskEventKind.CLEAR:
            before = len(self._blocks)
            self._blocks = [b for b in self._blocks if not self._same_scope(event, b)]
            closed = before - len(self._blocks)
            records.append(
                ArbitrationRecord(
                    subject_id=event.event_id,
                    action=ArbitrationAction.ADMITTED,
                    reason=f"CLEAR 解除覆盖范围内活跃阻断 {closed} 条",
                    violation=False,
                    deduped=False,
                    risk_event_id=event.event_id,
                )
            )
        else:
            self._blocks.append(event)
            records.append(
                ArbitrationRecord(
                    subject_id=event.event_id,
                    action=ArbitrationAction.ADMITTED,
                    reason=f"{event.kind.value} 阻断登记（覆盖 {event.scope.value}）",
                    violation=False,
                    deduped=False,
                    risk_event_id=event.event_id,
                )
            )
            # 乱序检测：已生效且 (occurred_at,seq) 晚于本事件的同范围信号→撤销
            for signal_id, sig in list(self._admitted.items()):
                if not self._covers(event, sig.symbol):
                    continue
                if sig.order_key > event.order_key:
                    del self._admitted[signal_id]
                    revoked = ArbitrationRecord(
                        subject_id=signal_id,
                        action=ArbitrationAction.REVOKED,
                        reason=(
                            f"ORDER_VIOLATION：风控事件 {event.event_id}"
                            f"({event.occurred_at.isoformat()}#{event.seq}) 先于信号"
                            f"({sig.occurred_at.isoformat()}#{sig.seq}) 却后到达→撤销信号生效"
                        ),
                        violation=True,
                        deduped=False,
                        risk_event_id=event.event_id,
                    )
                    self._signal_seen[signal_id] = revoked
                    self._emit(revoked)
                    records.append(revoked)
        self._risk_seen[event.event_id] = records[0].action
        self._risk_events[event.event_id] = event
        return records

    @staticmethod
    def _same_scope(clear: RiskEvent, block: RiskEvent) -> bool:
        """CLEAR 仅解除同范围阻断（GLOBAL 解除全部；SYMBOL 解除同标的）。"""
        if clear.scope is RiskScope.GLOBAL:
            return True
        return block.scope is RiskScope.SYMBOL and block.symbol == clear.symbol
