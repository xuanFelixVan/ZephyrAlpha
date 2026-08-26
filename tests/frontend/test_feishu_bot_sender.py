# [BLUEPRINT] MOD-FE-012 | docs/03_modules/_domain_frontend/feishu_bot_sender/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-012 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_feishu_bot_sender
# [TESTS] src/zephyr/frontend/feishu_bot_sender.py
"""MOD-FE-012 单元测试：feishu_bot_sender 飞书机器人推送器。

蓝图验收（B9-10705/CAND-FE-013，B9 D-FRONTEND-24）：webhook sender（client
注入不真发，密钥仅 secrets 引用）+ 审批通知模板 schema（标题/字段/按钮）+
告警推送（wechat_fallback 微信备选通道路由标记）+ 发送回执记录（确定性 id）。
client/时钟全内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.frontend.feishu_bot_sender",
    reason="feishu_bot_sender not importable",
)

from zephyr.frontend.feishu_bot_sender import (  # noqa: E402
    AlertLevel,
    AlertPush,
    ApprovalAction,
    ApprovalButton,
    ApprovalTemplate,
    FeishuBotError,
    FeishuBotSender,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _sender(sent: list | None = None, response: dict | None = None):
    sent = sent if sent is not None else []
    response = {"code": 0, "msg": "success"} if response is None else response

    def _client(webhook_ref: str, payload: dict):
        sent.append((webhook_ref, payload))
        return response

    bot = FeishuBotSender(
        webhook_ref="secrets://feishu/bot-webhook",
        client=_client,
        clock=lambda: _T0,
    )
    return bot, sent


def _template(**kwargs) -> ApprovalTemplate:
    payload = {
        "approval_id": "ap-1",
        "title": "新策略上线审批",
        "fields": (("策略", "t0_meanrev"), ("申请人", "alice")),
        "buttons": (
            ApprovalButton("批准", ApprovalAction.APPROVE),
            ApprovalButton("驳回", ApprovalAction.REJECT),
        ),
    }
    payload.update(kwargs)
    return ApprovalTemplate(**payload)


def _alert(**kwargs) -> AlertPush:
    payload = {
        "alert_id": "al-1",
        "level": AlertLevel.WARNING,
        "title": "回撤告警",
        "content": "组合回撤超 5%",
    }
    payload.update(kwargs)
    return AlertPush(**payload)


# ──────────────────────────────────────────────────────────────────────────────
# 构造配置（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_plaintext_webhook_raises(self) -> None:
        with pytest.raises(FeishuBotError):
            FeishuBotSender(
                webhook_ref="https://open.feishu.cn/open-apis/bot/v2/hook/abc",
                client=lambda ref, payload: {"code": 0},
            )

    def test_empty_webhook_ref_raises(self) -> None:
        with pytest.raises(FeishuBotError):
            FeishuBotSender(webhook_ref="", client=lambda ref, payload: {"code": 0})

    def test_missing_client_raises(self) -> None:
        with pytest.raises(FeishuBotError):
            FeishuBotSender(webhook_ref="secrets://feishu/bot", client=None)


# ──────────────────────────────────────────────────────────────────────────────
# 审批通知模板
# ──────────────────────────────────────────────────────────────────────────────


class TestApproval:
    def test_send_approval_ok_card_payload(self) -> None:
        bot, sent = _sender()
        receipt = bot.send_approval(_template())
        assert receipt.ok is True
        assert receipt.kind == "approval"
        assert receipt.target_id == "ap-1"
        webhook_ref, payload = sent[0]
        assert webhook_ref == "secrets://feishu/bot-webhook"
        assert payload["msg_type"] == "interactive"
        card = payload["card"]
        assert card["header"]["title"]["content"] == "新策略上线审批"
        actions = card["elements"][1]["actions"]
        assert [a["text"]["content"] for a in actions] == ["批准", "驳回"]
        assert actions[0]["type"] == "primary"
        assert actions[1]["type"] == "danger"
        assert actions[0]["value"] == {"approval_id": "ap-1", "action": "approve", "extra": ""}

    def test_approval_without_buttons_omits_action_element(self) -> None:
        bot, sent = _sender()
        bot.send_approval(_template(buttons=()))
        elements = sent[0][1]["card"]["elements"]
        assert len(elements) == 1
        assert elements[0]["tag"] == "div"

    def test_empty_title_raises(self) -> None:
        bot, _ = _sender()
        with pytest.raises(FeishuBotError):
            bot.send_approval(_template(title=""))

    def test_empty_fields_raises(self) -> None:
        bot, _ = _sender()
        with pytest.raises(FeishuBotError):
            bot.send_approval(_template(fields=()))

    def test_bad_field_pair_raises(self) -> None:
        bot, _ = _sender()
        with pytest.raises(FeishuBotError):
            bot.send_approval(_template(fields=(("仅标签",),)))

    def test_invalid_button_action_raises(self) -> None:
        bot, _ = _sender()
        with pytest.raises(FeishuBotError):
            bot.send_approval(_template(buttons=(ApprovalButton("查看", "goto"),)))

    def test_too_many_buttons_raises(self) -> None:
        bot, _ = _sender()
        buttons = tuple(ApprovalButton(f"b{i}", ApprovalAction.VIEW) for i in range(4))
        with pytest.raises(FeishuBotError):
            bot.send_approval(_template(buttons=buttons))


# ──────────────────────────────────────────────────────────────────────────────
# 告警推送
# ──────────────────────────────────────────────────────────────────────────────


class TestAlert:
    def test_send_alert_ok_text_payload(self) -> None:
        bot, sent = _sender()
        receipt = bot.send_alert(_alert())
        assert receipt.ok is True
        assert receipt.kind == "alert"
        payload = sent[0][1]
        assert payload["msg_type"] == "text"
        assert payload["content"]["text"] == "[WARNING] 回撤告警\n组合回撤超 5%"

    def test_wechat_fallback_mark(self) -> None:
        bot, sent = _sender()
        bot.send_alert(_alert(wechat_fallback=True))
        assert sent[0][1]["za_route"] == {"wechat_fallback": True}

    def test_invalid_level_raises(self) -> None:
        bot, _ = _sender()
        with pytest.raises(FeishuBotError):
            bot.send_alert(_alert(level="P1"))

    def test_empty_content_raises(self) -> None:
        bot, _ = _sender()
        with pytest.raises(FeishuBotError):
            bot.send_alert(_alert(content=""))


# ──────────────────────────────────────────────────────────────────────────────
# 回执与 best-effort
# ──────────────────────────────────────────────────────────────────────────────


class TestReceipts:
    def test_client_exception_best_effort(self) -> None:
        def _boom(ref, payload):
            raise RuntimeError("network down")

        bot = FeishuBotSender(
            webhook_ref="secrets://feishu/bot-webhook", client=_boom, clock=lambda: _T0
        )
        receipt = bot.send_alert(_alert())
        assert receipt.ok is False
        assert receipt.detail == "client_exception"

    def test_rejected_by_webhook(self) -> None:
        bot, _ = _sender(response={"code": 19001, "msg": "param invalid"})
        receipt = bot.send_alert(_alert())
        assert receipt.ok is False
        assert receipt.detail == "rejected_by_webhook"

    def test_malformed_response_not_ok(self) -> None:
        bot = FeishuBotSender(
            webhook_ref="secrets://feishu/bot-webhook",
            client=lambda ref, payload: "ok-string",
            clock=lambda: _T0,
        )
        assert bot.send_alert(_alert()).ok is False

    def test_receipts_recorded_with_deterministic_ids(self) -> None:
        bot, _ = _sender()
        r1 = bot.send_approval(_template())
        r2 = bot.send_alert(_alert())
        assert (r1.receipt_id, r2.receipt_id) == ("fs-000001", "fs-000002")
        receipts = bot.receipts()
        assert len(receipts) == 2
        assert receipts[0].sent_at == _T0
        assert receipts[0].webhook_ref == "secrets://feishu/bot-webhook"  # 引用非明文

    def test_determinism_same_ops_same_receipts(self) -> None:
        bot1, _ = _sender()
        bot2, _ = _sender()
        for b in (bot1, bot2):
            b.send_approval(_template())
            b.send_alert(_alert())
        assert bot1.receipts() == bot2.receipts()
