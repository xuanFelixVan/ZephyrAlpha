# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.secondary_alert_channel
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Secondary Alert Channel — v0.37.0 R461

Blindspot: Primary notification channel failure (SMS down, email blocked)
leaves operator blind to critical FLE actions.

Risk: R461 — Single-channel alerting creates single point of failure in human-FLE loop.

Mitigation: Multi-channel fallback chain (primary -> secondary -> tertiary).
Health-check each channel with heartbeat pings. Auto-failover when primary
loses connectivity for >heartbeat_interval. Log all channel transitions.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 告警发送请求与通道心跳
#   fields: send_alert(message, severity)；heartbeat(channel) 心跳
#   code: SecondaryAlertChannel.send_alert / heartbeat
# 层: 算法
# - id: A1
#   name_zh: 通道健康判定
#   name_en: channel_health_check
#   intro: 超 3×heartbeat_interval 未心跳的通道标记为 DOWN
#   code: SecondaryAlertChannel.check_channels
# - id: A2
#   name_zh: 故障转移选路
#   name_en: channel_failover
#   intro: 主通道 DOWN 时按 channels 顺序切到首个 HEALTHY 通道并累计 failover_count
#   code: SecondaryAlertChannel.check_channels
# 层: 输出
# - id: O1
#   name_zh: 告警投递结果
#   name_en: alert_dispatch_result
#   intro: {"channel": 当前活跃通道, "message", "severity", "failover_count"} dict
#   downstream: 负责人通知终端（sms / email / push）
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ChannelState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"


@dataclass
class SecondaryAlertChannel:
    channels: list[str] = field(default_factory=lambda: ["sms", "email", "push"])
    heartbeat_interval: float = 60.0

    active_channel: str = ""
    channel_health: dict[str, ChannelState] = field(default_factory=dict)
    last_heartbeat: dict[str, float] = field(default_factory=dict)
    failover_count: int = 0

    def __post_init__(self):
        self.active_channel = self.channels[0] if self.channels else ""
        for ch in self.channels:
            self.channel_health[ch] = ChannelState.HEALTHY
            self.last_heartbeat[ch] = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示

    def heartbeat(self, channel: str) -> None:
        self.last_heartbeat[channel] = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        self.channel_health[channel] = ChannelState.HEALTHY

    def check_channels(self) -> str:
        now = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        for ch in self.channels:
            if now - self.last_heartbeat.get(ch, 0) > self.heartbeat_interval * 3:
                self.channel_health[ch] = ChannelState.DOWN

        if self.channel_health.get(self.active_channel) is ChannelState.DOWN:
            for ch in self.channels:
                if self.channel_health.get(ch) is ChannelState.HEALTHY:
                    self.active_channel = ch
                    self.failover_count += 1
                    return ch

        return self.active_channel

    def send_alert(self, message: str, severity: str) -> dict:
        active = self.check_channels()
        return {
            "channel": active,
            "message": message,
            "severity": severity,
            "failover_count": self.failover_count,
        }
