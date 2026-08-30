# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §9/§17a
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l6_feishu_alert
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.security_event_bus; zephyr.shared.io.paths
# [CONSUMERS] tests.llm_security.test_l6_feishu_alert
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 告警不丢——webhook 未配置/不可达 MUST 本地持久化不丢事件
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/llm_security/test_l6_feishu_alert.py
# [A_module] module_id=MOD-LLM_SECURITY | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
L6 飞书高危告警——复用 MOD-SEC-EVENTBUS FeishuAlertChannel（委托，不自建）。

裁定记录（09 号文 §4.3 P1-1 前置裁定）
--------------------------------------
诉求：LSG 高危安全事件实时推送飞书 Webhook；不可达时本地持久化不丢事件。
MOD-SEC-EVENTBUS ``FeishuAlertChannel``（16 号文 §4.2 P0-3）已覆盖全部诉求：
webhook 发送、未配置/不可达/非 200 写 ``alerts_pending.jsonl`` 本地持久化、
``retry_pending()`` 重试 + 超 MAX_ALERT_RETRY 死信保留、dry_run 演练留痕。
结论：**复用（委托）**——LSG 层内不重建 webhook/持久化设施，本模块只做
LSG 事件语义 → 统一 SecurityEvent schema 的转换与通道委托。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: pending_path 参数
#   fields: 参数 pending_path（无注解）
#   code: l6_feishu_alert.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: webhook_url 参数
#   fields: 参数 webhook_url（无注解）
#   code: l6_feishu_alert.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: dry_run 参数
#   fields: 参数 dry_run（无注解）
#   code: l6_feishu_alert.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: timeout_sec 参数
#   fields: 参数 timeout_sec（无注解）
#   code: l6_feishu_alert.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LsgFeishuAlerter
#   name_en: LsgFeishuAlerter
#   intro: LSG 高危事件飞书告警器（L6 层内件，委托 FeishuAlertChannel）。
#   desc: LSG 高危事件飞书告警器（L6 层内件，委托 FeishuAlertChannel）。 用法:: alerter = LsgFeishuAlerter() delivered…；公共方法（定义序）: send_hig…
#   inputs: pending_path webhook_url dry_run timeout_sec channel
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: LsgFeishuAlerter
#   downstream: tests.llm_security.test_l6_feishu_alert
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

import logging
from pathlib import Path
from typing import Any, Final

from zephyr.security.security_event_bus import (
    ALERT_TIMEOUT_SEC,
    ALERTS_PENDING_FILENAME,
    DEFAULT_EVENT_DIR,
    FeishuAlertChannel,
    LsgSecurityStackAdapter,
    SecurityEvent,
)

logger = logging.getLogger(__name__)

__all__ = ["DEFAULT_LSG_ALERT_PENDING_PATH", "LsgFeishuAlerter"]

DEFAULT_LSG_ALERT_PENDING_PATH: Final[Path] = DEFAULT_EVENT_DIR / ALERTS_PENDING_FILENAME


class LsgFeishuAlerter:
    """LSG 高危事件飞书告警器（L6 层内件，委托 FeishuAlertChannel）。

    用法::

        alerter = LsgFeishuAlerter()
        delivered = alerter.send_high_risk_alert(
            layer="l1_input", rule="direct_injection", result="block",
        )

    返回 True=已送达（含 dry_run 留痕）；False=已降级本地持久化（不丢）。
    """

    def __init__(
        self,
        *,
        pending_path: Path = DEFAULT_LSG_ALERT_PENDING_PATH,
        webhook_url: str | None = None,
        dry_run: bool = False,
        timeout_sec: float = ALERT_TIMEOUT_SEC,
        channel: FeishuAlertChannel | None = None,
    ) -> None:
        self._channel = channel or FeishuAlertChannel(
            pending_path=pending_path,
            webhook_url=webhook_url,
            dry_run=dry_run,
            timeout_sec=timeout_sec,
        )
        self._adapter = LsgSecurityStackAdapter()

    def send_high_risk_alert(
        self,
        *,
        layer: str,
        rule: str,
        target: str = "",
        result: str = "block",
        severity: str = "high",
        threat_category: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> bool:
        """发送 LSG 高危告警；失败/未配置持久化不丢。返回 True=已送达。"""
        raw: dict[str, Any] = {
            "layer": layer,
            "rule": rule,
            "target": target,
            "result": result,
            "severity": severity,
        }
        if threat_category is not None:
            raw["threat_category"] = threat_category
        if detail:
            raw["detail"] = dict(detail)
        event = self._adapter.adapt(raw)
        return self.send_event(event)

    def send_event(self, event: SecurityEvent) -> bool:
        """直接发送统一 schema 事件（委托通道；异常不阻断调用方，降级持久化由通道保证）。"""
        try:
            return self._channel.send(event)
        except Exception:  # noqa: BLE001 — 告警通道自身异常不得阻断 LSG 主链路
            logger.warning("飞书告警发送异常，事件由通道本地队列兜底", exc_info=True)
            return False

    def pending_count(self) -> int:
        """本地持久化队列待送达条数。"""
        return self._channel.pending_count()

    def retry_pending(self) -> dict[str, int]:
        """重试本地队列（成功出队、失败累计、超限死信保留——语义同通道）。"""
        return self._channel.retry_pending()
