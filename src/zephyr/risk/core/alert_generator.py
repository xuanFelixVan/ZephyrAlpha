# [BLUEPRINT] MOD-RK-06 | docs/03_modules/_domain_risk/alert_generator/blueprint.md
# [MODULE] zephyr.risk.core.alert_generator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager_base; zephyr.shared.alerts.threshold_loader
# [CONSUMERS] MOD-L04-001(DefaultRiskManagerOrchestrator,告警统一出口)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分级纯机制零参数;日志通道必达;邮件/微信best-effort不阻断;去重窗口内同源同消息只派发一次;去重窗口真源=alert_threshold_registry(THD-ALERT-001,fail-closed)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/risk/core/test_alert_generator.py
# [A_module] module_id=MOD-RK-06 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

D_RISK — Alert Generator (MOD-RK-06)

告警生成器——消费 RiskReport，将原始违规项按严重程度分为三级
（黄/橙/红），按级别路由到不同通道（日志/邮件/微信），并对同源
告警在时间窗口内去重。

属 A 类基础设施：分级规则基于 RiskReport 字段判定，路由规则基于
级别映射，均为纯机制无业务参数。

核心流程:
  classify(report) → list[Alert]    # 分级
  deduplicate(alerts) → list[Alert] # 去重
  route(alert) → None               # 多通道路由

日志埋点策略（非过度工程，关键决策点可观测）:
  - INFO:    告警派发成功（level + source + channel）
  - WARNING: 去重抑制 / 通道返回失败（best-effort 不阻断）
  - ERROR:   通道异常（best-effort 不阻断）
  - DEBUG:   分级推理过程 + 通道未配置跳过

CTR 契约:
  消费者 — RiskReport ← D_RISK (risk_manager_base)
  生产者 — Alert → 日志/邮件/微信通道

SSoT: depgraph MOD-RK-06 | blueprint.md §3 核心规则

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 风控报告 RiskReport
#   fields: portfolio_id/kill_switch_active/failed_checks(含severity与limit/actual)/active_alerts字符串列表
#   code: process() report L374 / risk_manager_base.RiskReport
# - id: I2
#   name: 去重窗口与通道配置 参数
#   fields: dedup_window默认5分钟 + channels{log/email/wechat}(邮件微信默认no-op可注入sender)
#   code: __init__() L191-202
# 层: 算法
# - id: A1
#   name_zh: ① 三级告警分级
#   name_en: classify
#   intro: 按报告字段把原始违规项分成黄橙红三级告警
#   desc: RED=kill_switch_active或有HALT级违规; ORANGE=非HALT级违规(同源已有RED跳过); YELLOW=active_alerts(取冒号前缀为source); 每source取最高适用级别
#   inputs: I1
#   outputs: list[Alert]三级告警列表
# - id: A2
#   name_zh: ② 时间窗去重
#   name_en: deduplicate
#   intro: 去重窗口内同源同消息的告警只派发一次
#   desc: key=source:message; (alert.timestamp−last_seen)<dedup_window→抑制(WARNING日志); 顺带清理过期缓存防无限增长
#   inputs: A1 I2
#   outputs: 去重后list[Alert]
#   invariant: 去重窗口内同源同消息只派发一次
# - id: A3
#   name_zh: ③ 多通道路由
#   name_en: route
#   intro: 按级别硬编码映射把告警推到日志/邮件/微信通道
#   desc: RED→log+email+wechat; ORANGE→log+email; YELLOW→log; 日志通道必达; 邮件/微信best-effort失败仅WARNING/ERROR不阻断
#   inputs: A2 I2
#   outputs: 各通道派发结果
#   invariant: 日志通道必达; 邮件/微信best-effort不阻断
# 层: 输出
# - id: O1
#   name_zh: 派发告警列表
#   name_en: list[Alert]
#   intro: process返回的实际派发告警(去重后, 含溯源幂等键)
#   downstream: DefaultRiskManagerOrchestrator MOD-L04-001(告警统一出口)
# - id: O2
#   name_zh: 通道告警外发
#   name_en: channel dispatch
#   intro: 经Log/Email/WeChat三通道外发的告警(日志必达, 邮件微信注入sender后生效)
#   downstream: 无下游/内部使用(外部日志/邮件/微信通道)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> A3
# I2 --> A3
# A2 --> O1
# A3 --> O2
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Final, Protocol

from zephyr.risk.risk_manager_base import RiskReport
from zephyr.shared.alerts.threshold_loader import load_alert_thresholds

_logger = logging.getLogger(__name__)

__all__ = [
    "Alert",
    "AlertChannel",
    "AlertGenerator",
    "AlertLevel",
    "EmailChannel",
    "LogChannel",
    "WeChatChannel",
]


# ── 数据模型 ──────────────────────────────────────────────────────────


class AlertLevel(Enum):
    """告警三级（黄/橙/红），严重程度递增。"""

    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


@dataclass(frozen=True)
class Alert:
    """单条告警（不可变，含溯源字段）。

    Attributes:
        level: 告警级别（YELLOW/ORANGE/RED）
        source: 来源监控器/规则名（concentration/tail_risk/kill_switch...）
        message: 告警内容
        timestamp: 生成时间（UTC）
        idempotency_key: 幂等键（溯源用，非去重键）
    """

    level: AlertLevel
    source: str
    message: str
    timestamp: datetime
    idempotency_key: str


# ── 通道抽象 ──────────────────────────────────────────────────────────


class AlertChannel(Protocol):
    """告警通道协议（可注入实现，默认 log 通道必达）。"""

    def send(self, alert: Alert) -> bool:
        """派发告警到通道。返回 True=成功，False=未配置/软失败。"""
        ...


class LogChannel:
    """日志通道——始终可用，必达。"""

    _LEVEL_MAP: dict[AlertLevel, int] = {
        AlertLevel.RED: logging.CRITICAL,
        AlertLevel.ORANGE: logging.WARNING,
        AlertLevel.YELLOW: logging.INFO,
    }

    def send(self, alert: Alert) -> bool:
        level = self._LEVEL_MAP.get(alert.level, logging.INFO)
        _logger.log(
            level,
            "[ALERT:%s] %s: %s",
            alert.level.value.upper(),
            alert.source,
            alert.message,
        )
        return True


class EmailChannel:
    """邮件通道——默认 no-op，注入 sender 可调用对象后生效。

    Args:
        sender: callable(alert: Alert) -> bool，None 时返回 False（未配置）。
    """

    def __init__(self, sender: "callable | None" = None):  # type: ignore[valid-type]
        self._sender = sender

    def send(self, alert: Alert) -> bool:
        if self._sender is None:
            _logger.debug(
                "Email channel not configured, skipping: source=%s level=%s",
                alert.source,
                alert.level.value,
            )
            return False
        return self._sender(alert)


class WeChatChannel:
    """微信通道——默认 no-op，注入 sender 可调用对象后生效。"""

    def __init__(self, sender: "callable | None" = None):  # type: ignore[valid-type]
        self._sender = sender

    def send(self, alert: Alert) -> bool:
        if self._sender is None:
            _logger.debug(
                "WeChat channel not configured, skipping: source=%s level=%s",
                alert.source,
                alert.level.value,
            )
            return False
        return self._sender(alert)


# ── 告警生成器 ────────────────────────────────────────────────────────

#: 去重窗口 ↔ 注册表条目映射（55 号 §3.3 统读：THD-ALERT-001，单位秒）
_DEDUP_WINDOW_SPEC: Final[dict[str, str]] = {"THD-ALERT-001": "dedup_window_seconds"}


def _load_dedup_window_seconds(registry_path: Path | None = None) -> float:
    """从告警阈值注册表加载去重窗口秒数（fail-closed；registry_path 为测试逃生门）。"""
    return load_alert_thresholds(_DEDUP_WINDOW_SPEC, registry_path=registry_path)["dedup_window_seconds"]


class AlertGenerator:
    """告警生成器——分级 → 去重 → 多通道路由。

    纯机制零参数：分级规则基于 RiskReport 字段判定，路由规则基于
    级别映射。唯一可调参数为去重窗口（默认 5 分钟，C 类参数）。

    Usage:
        gen = AlertGenerator()
        alerts = gen.process(report)  # classify → deduplicate → route
    """

    #: 级别 → 通道集合（硬编码映射，纯机制）
    _CHANNEL_MAP: dict[AlertLevel, set[str]] = {
        AlertLevel.RED: {"log", "email", "wechat"},
        AlertLevel.ORANGE: {"log", "email"},
        AlertLevel.YELLOW: {"log"},
    }

    def __init__(
        self,
        dedup_window: timedelta | None = None,
        channels: dict[str, AlertChannel] | None = None,
        registry_path: Path | None = None,
    ):
        """初始化告警生成器。

        Args:
            dedup_window: 去重窗口；None 时从告警阈值注册表 fail-closed 加载
                （THD-ALERT-001，默认 300 秒）。显式传参可覆盖注册表默认（逃生门）。
            channels: 通道注入（默认 log/email/wechat 三通道）。
            registry_path: 注册表路径注入（测试逃生门；默认全仓唯一真源）。
        """
        self._dedup_window = (
            dedup_window if dedup_window is not None else timedelta(seconds=_load_dedup_window_seconds(registry_path))
        )
        self._dedup_cache: dict[str, datetime] = {}
        self._channels: dict[str, AlertChannel] = channels or {
            "log": LogChannel(),
            "email": EmailChannel(),
            "wechat": WeChatChannel(),
        }

    # ── 分级 ──

    def classify(self, report: RiskReport) -> list[Alert]:
        """将 RiskReport 分类为三级告警列表。

        规则（蓝图 §3.1，纯机制零参数）:
          RED    — kill_switch_active=True 或 failed_checks 中有 HALT 级违规
          ORANGE — failed_checks 非空但无 HALT 级违规
          YELLOW — active_alerts 非空

        每个 source 取其最高适用级别，避免同源重复告警。
        """
        alerts: list[Alert] = []
        now = datetime.now(UTC)
        _logger.debug(
            "Classifying report: portfolio=%s kill_switch=%s overall_pass=%s failed_checks=%d active_alerts=%d",
            report.portfolio_id,
            report.kill_switch_active,
            report.overall_pass,
            len(report.failed_checks),
            len(report.active_alerts),
        )

        # RED: kill switch 触发
        if report.kill_switch_active:
            alerts.append(
                self._make_alert(
                    level=AlertLevel.RED,
                    source="kill_switch",
                    message=f"Kill switch activated for portfolio {report.portfolio_id}",
                    timestamp=now,
                )
            )

        # RED: HALT 级违规
        halt_checks = [c for c in report.failed_checks if c.severity == "HALT"]
        for check in halt_checks:
            msg = check.message or (
                f"HALT: {check.rule_name} violated (limit={check.limit_value}, actual={check.actual_value})"
            )
            alerts.append(
                self._make_alert(
                    level=AlertLevel.RED,
                    source=check.rule_name,
                    message=msg,
                    timestamp=now,
                )
            )

        # ORANGE: 非 HALT 级违规（同源已有 RED 则跳过）
        red_sources = {a.source for a in alerts if a.level == AlertLevel.RED}
        non_halt_failures = [c for c in report.failed_checks if c.severity != "HALT"]
        for check in non_halt_failures:
            if check.rule_name in red_sources:
                continue
            msg = check.message or (
                f"WARNING: {check.rule_name} violated (limit={check.limit_value}, actual={check.actual_value})"
            )
            alerts.append(
                self._make_alert(
                    level=AlertLevel.ORANGE,
                    source=check.rule_name,
                    message=msg,
                    timestamp=now,
                )
            )

        # YELLOW: active_alerts 字符串
        for raw_msg in report.active_alerts:
            source = self._extract_source(raw_msg)
            alerts.append(
                self._make_alert(
                    level=AlertLevel.YELLOW,
                    source=source,
                    message=raw_msg,
                    timestamp=now,
                )
            )

        _logger.info(
            "Classification complete: portfolio=%s total_alerts=%d red=%d orange=%d yellow=%d",
            report.portfolio_id,
            len(alerts),
            sum(1 for a in alerts if a.level == AlertLevel.RED),
            sum(1 for a in alerts if a.level == AlertLevel.ORANGE),
            sum(1 for a in alerts if a.level == AlertLevel.YELLOW),
        )
        return alerts

    # ── 去重 ──

    def deduplicate(self, alerts: list[Alert]) -> list[Alert]:
        """时间窗口内同源同消息去重。

        Key = (source, message)。窗口内重复 → 抑制（WARNING 日志）。
        窗口过期后自动允许重新派发。
        """
        if not alerts:
            return []

        result: list[Alert] = []
        now = datetime.now(UTC)

        for alert in alerts:
            key = f"{alert.source}:{alert.message}"
            last_seen = self._dedup_cache.get(key)

            if last_seen is not None and (alert.timestamp - last_seen) < self._dedup_window:
                _logger.warning(
                    "Alert suppressed (dedup): source=%s message=%s within window=%ss",
                    alert.source,
                    alert.message,
                    self._dedup_window.total_seconds(),
                )
                continue

            self._dedup_cache[key] = alert.timestamp
            result.append(alert)

        # 清理过期缓存（防止无限增长）
        self._cleanup_expired(now)

        _logger.info(
            "Deduplication complete: input=%d output=%d suppressed=%d",
            len(alerts),
            len(result),
            len(alerts) - len(result),
        )
        return result

    # ── 路由 ──

    def route(self, alert: Alert) -> None:
        """按级别路由到对应通道（蓝图 §3.2 硬编码映射）。

        日志通道必达，邮件/微信 best-effort 不阻断。
        """
        channels = self._CHANNEL_MAP.get(alert.level, set())

        for channel_name in sorted(channels):
            channel = self._channels.get(channel_name)
            if channel is None:
                continue

            try:
                success = channel.send(alert)
                if success:
                    _logger.info(
                        "Alert dispatched: level=%s source=%s channel=%s",
                        alert.level.value,
                        alert.source,
                        channel_name,
                    )
                else:
                    _logger.warning(
                        "Channel returned failure (best-effort): channel=%s level=%s source=%s",
                        channel_name,
                        alert.level.value,
                        alert.source,
                    )
            except Exception as exc:  # noqa: BLE001 — best-effort, 不阻断
                _logger.error(
                    "Channel dispatch failed (best-effort): channel=%s error=%s",
                    channel_name,
                    exc,
                )

    # ── 全流程入口 ──

    def process(self, report: RiskReport) -> list[Alert]:
        """全流程: classify → deduplicate → route。

        返回实际派发的告警列表（去重后）。
        """
        alerts = self.classify(report)
        alerts = self.deduplicate(alerts)
        for alert in alerts:
            self.route(alert)
        return alerts

    # ── 内部工具 ──

    @staticmethod
    def _make_alert(
        level: AlertLevel,
        source: str,
        message: str,
        timestamp: datetime,
    ) -> Alert:
        """构造 Alert，生成幂等键。"""
        msg_hash = hashlib.md5(message.encode()).hexdigest()[:8]  # noqa: S324
        return Alert(
            level=level,
            source=source,
            message=message,
            timestamp=timestamp,
            idempotency_key=f"alert-{source}-{msg_hash}-{uuid.uuid4().hex[:8]}",
        )

    @staticmethod
    def _extract_source(raw_msg: str) -> str:
        """从 active_alerts 字符串中提取 source，格式 'source: detail' 时取前缀。"""
        if ":" in raw_msg:
            return raw_msg.split(":", 1)[0].strip()
        return "general"

    def _cleanup_expired(self, now: datetime) -> None:
        """清理去重缓存中过期的条目。"""
        expired_keys = [key for key, ts in self._dedup_cache.items() if (now - ts) >= self._dedup_window]
        for key in expired_keys:
            del self._dedup_cache[key]
        if expired_keys:
            _logger.debug("Dedup cache cleanup: removed %d expired entries", len(expired_keys))
