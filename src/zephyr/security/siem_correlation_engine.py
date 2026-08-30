# [BLUEPRINT] MOD-SEC-025 | docs/03_modules/_domain_security/siem_correlation_engine/blueprint.md
# [MODULE] zephyr.security.siem_correlation_engine
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] 无（纯内存；时钟/立即路由/汇总sink 全注入，复用 security_event_bus 语义不导入）
# [CONSUMERS] 运行时装配批（安全事件总线订阅端装配关联引擎与分级路由回调）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 规则集闭合(Sigma风格序列+滑窗+分组); 关联仅同主体/同会话内按序匹配; 命中即提升严重度至规则级; P0/P1立即路由语义, P2/P3每日汇总语义; 命中后消费掉已匹配事件不重复告警; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_security/siem_correlation_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SiemError(占位 ZA-SEC-UNREGISTERED-SIEM)——空规则集/规则字段非法/重复rule_id/事件字段非法时抛
# [TESTS] tests/security/test_siem_correlation_engine.py
# [A_module] module_id=MOD-SEC-025 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
SiemCorrelationEngine — SIEM 跨域关联引擎（MOD-SEC-025）。

B12-03820（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SEC-006，B12）：Sigma 风
格规则注册（同主体/同会话**滑动时间窗**内多域**事件序列**聚合，如 注入→
越权→数据导出 攻击链）+ 命中**提升严重度** + 告警**分级路由**（P0/P1 立
即通知语义，P2/P3 每日汇总语义，时钟与路由回调全注入）。

查重分工（蓝图 §0）：security_event_bus=事件分发总线（本件=其上关联规则
引擎，复用路由语义不重建总线）；ML 异常检测不建（纯确定性序列匹配）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rules 参数
#   fields: 参数 rules（无注解）
#   code: siem_correlation_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: siem_correlation_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: immediate_router 参数
#   fields: 参数 immediate_router（无注解）
#   code: siem_correlation_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: summary_sink 参数
#   fields: 参数 summary_sink（无注解）
#   code: siem_correlation_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SiemCorrelationEngine
#   name_en: SiemCorrelationEngine
#   intro: SIEM 关联规则引擎（滑窗序列聚合 + 提级 + 分级路由）。
#   desc: SIEM 关联规则引擎（滑窗序列聚合 + 提级 + 分级路由）。；公共方法（定义序）: ingest, flush_summary；源码 L156-L293
#   inputs: rules clock immediate_router summary_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: SiemCorrelationEngine
#   downstream: 运行时装配批（安全事件总线订阅端装配关联引擎与分级路由回调）
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
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "CorrelationAlert",
    "GroupBy",
    "SecurityEvent",
    "Severity",
    "SiemCorrelationEngine",
    "SiemError",
    "SigmaRule",
]


class SiemError(Exception):
    """SIEM 关联引擎输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SEC-UNREGISTERED-SIEM。
    """


class Severity(str, Enum):
    """告警严重度（词表闭合）。"""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


#: 立即路由语义严重度（P0/P1/系统级）；其余（P2/P3）走每日汇总语义
_IMMEDIATE_SEVERITIES: Final = frozenset({Severity.P0, Severity.P1})


class GroupBy(str, Enum):
    """关联分组维度（同主体 / 同会话）。"""

    SUBJECT = "subject"
    SESSION = "session"


@dataclass(frozen=True)
class SigmaRule:
    """Sigma 风格关联规则（序列 + 滑窗 + 分组 + 提级，frozen）。"""

    rule_id: str
    title: str
    sequence: tuple[str, ...]
    window_seconds: float
    group_by: GroupBy
    escalate_to: Severity


@dataclass(frozen=True)
class SecurityEvent:
    """安全事件（总线载荷，frozen）。"""

    event_type: str
    subject: str
    session_id: str
    severity: Severity
    occurred_at: datetime.datetime
    details: dict


@dataclass(frozen=True)
class CorrelationAlert:
    """关联命中告警（提级后载荷，frozen）。"""

    rule_id: str
    group_key: str
    matched_types: tuple[str, ...]
    severity: Severity
    first_seen: datetime.datetime
    last_seen: datetime.datetime
    raised_at: datetime.datetime


class SiemCorrelationEngine:
    """SIEM 关联规则引擎（滑窗序列聚合 + 提级 + 分级路由）。"""

    def __init__(
        self,
        *,
        rules: Iterable[SigmaRule],
        clock: Callable[[], datetime.datetime] | None = None,
        immediate_router: Callable[[CorrelationAlert], None] | None = None,
        summary_sink: Callable[[list[CorrelationAlert]], None] | None = None,
    ) -> None:
        rule_list = list(rules) if rules is not None else []
        if not rule_list:
            raise SiemError("rules 为空（无关联规则声明）")
        seen: set[str] = set()
        for rule in rule_list:
            if not isinstance(rule, SigmaRule):
                raise SiemError(f"非法规则类型: {type(rule)!r}")
            if not rule.rule_id:
                raise SiemError("rule_id 为空")
            if rule.rule_id in seen:
                raise SiemError(f"rule_id 重复: {rule.rule_id!r}")
            seen.add(rule.rule_id)
            if not rule.title:
                raise SiemError(f"规则 {rule.rule_id} title 为空")
            if len(rule.sequence) < 2:
                raise SiemError(f"规则 {rule.rule_id} 序列长度须 >= 2")
            if any(not t for t in rule.sequence):
                raise SiemError(f"规则 {rule.rule_id} 序列含空事件类型")
            if rule.window_seconds <= 0:
                raise SiemError(f"规则 {rule.rule_id} 滑窗须为正数")
            if not isinstance(rule.group_by, GroupBy):
                raise SiemError(f"规则 {rule.rule_id} 非法分组维度")
            if not isinstance(rule.escalate_to, Severity):
                raise SiemError(f"规则 {rule.rule_id} 非法提级严重度")
        self._rules: tuple[SigmaRule, ...] = tuple(rule_list)
        self._clock = clock or datetime.datetime.now
        self._immediate_router = immediate_router
        self._summary_sink = summary_sink
        self._buffers: dict[tuple[str, str], list[SecurityEvent]] = {}
        self._summary_buffer: list[CorrelationAlert] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _group_key(self, rule: SigmaRule, event: SecurityEvent) -> str:
        return event.subject if rule.group_by is GroupBy.SUBJECT else event.session_id

    def _prune(self, rule: SigmaRule, buf: list[SecurityEvent]) -> None:
        """滑动时间窗裁剪：以缓冲内最新事件时刻为参照。"""
        if not buf:
            return
        newest = buf[-1].occurred_at
        horizon = newest - datetime.timedelta(seconds=rule.window_seconds)
        buf[:] = [e for e in buf if e.occurred_at >= horizon]

    def _match(self, rule: SigmaRule, buf: list[SecurityEvent]) -> list[int] | None:
        """按序子序列滑窗匹配（最早起点贪心，确定性）；命中返回索引列表。"""
        seq = rule.sequence
        n = len(buf)
        window = datetime.timedelta(seconds=rule.window_seconds)
        for i in range(n):
            if buf[i].event_type != seq[0]:
                continue
            idxs = [i]
            k = 1
            j = i
            while k < len(seq):
                j += 1
                if j >= n or buf[j].occurred_at - buf[i].occurred_at > window:
                    break
                if buf[j].event_type == seq[k]:
                    idxs.append(j)
                    k += 1
            if k == len(seq):
                return idxs
        return None

    def _dispatch(self, alert: CorrelationAlert) -> None:
        """分级路由：P0/P1 立即通知；P2/P3 入每日汇总缓冲。"""
        if alert.severity in _IMMEDIATE_SEVERITIES:
            _log.warning("SIEM 立即告警: %s (%s)", alert.rule_id, alert.severity.value)
            if self._immediate_router is not None:
                self._immediate_router(alert)
        else:
            _log.info("SIEM 汇总告警: %s (%s)", alert.rule_id, alert.severity.value)
            self._summary_buffer.append(alert)

    # ── 事件接入 ─────────────────────────────────────────────────────────

    def ingest(self, event: SecurityEvent) -> tuple[CorrelationAlert, ...]:
        """接入事件：分组缓冲 → 滑窗裁剪 → 序列匹配 → 提级路由。

        返回本次接入触发的全部告警（确定性规则序）。
        """
        if not isinstance(event, SecurityEvent):
            raise SiemError(f"非法事件类型: {type(event)!r}")
        if not event.event_type or not event.subject or not event.session_id:
            raise SiemError("事件 event_type/subject/session_id 为空")
        if not isinstance(event.severity, Severity):
            raise SiemError(f"非法事件严重度: {event.severity!r}")
        if not isinstance(event.occurred_at, datetime.datetime):
            raise SiemError("事件 occurred_at 非法")

        raised: list[CorrelationAlert] = []
        for rule in self._rules:
            key = (rule.rule_id, self._group_key(rule, event))
            buf = self._buffers.setdefault(key, [])
            buf.append(event)
            buf.sort(key=lambda e: e.occurred_at)
            self._prune(rule, buf)
            idxs = self._match(rule, buf)
            if idxs is None:
                continue
            matched = [buf[i] for i in idxs]
            # 命中后消费掉已匹配事件（不重复告警）
            self._buffers[key] = [e for i, e in enumerate(buf) if i not in set(idxs)]
            alert = CorrelationAlert(
                rule_id=rule.rule_id,
                group_key=key[1],
                matched_types=tuple(e.event_type for e in matched),
                severity=rule.escalate_to,  # 命中提升严重度
                first_seen=matched[0].occurred_at,
                last_seen=matched[-1].occurred_at,
                raised_at=self._clock(),
            )
            self._dispatch(alert)
            raised.append(alert)
        return tuple(raised)

    # ── 每日汇总 ─────────────────────────────────────────────────────────

    def flush_summary(self) -> tuple[CorrelationAlert, ...]:
        """每日汇总冲刷：P2/P3 缓冲推送 summary_sink（注入）并清空。"""
        out = tuple(self._summary_buffer)
        self._summary_buffer.clear()
        if out and self._summary_sink is not None:
            self._summary_sink(list(out))
        return out
