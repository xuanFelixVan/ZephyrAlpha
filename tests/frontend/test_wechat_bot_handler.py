# [BLUEPRINT] MOD-FE-013 | docs/03_modules/_domain_frontend/wechat_bot_handler/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_wechat_bot_handler
# [TESTS] src/zephyr/frontend/wechat_bot_handler.py
"""MOD-FE-013 单元测试：wechat_bot_handler 企业微信机器人处理器。

蓝图验收（B9-10706/CAND-FE-014，B9 D-FRONTEND-25）：回调消息 schema 校验 +
指令鉴权（白名单主体 + 注入鉴权器）+ 指令解析词表闭合（盯盘/查询/下单/
确认/取消）+ 回复渲染（文本/卡片）+ 下单二次确认硬约束（超时拒绝）。
鉴权器/数据源/执行器/时钟全内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.frontend.implementations.wechat_bot_handler",
    reason="wechat_bot_handler not importable",
)

from zephyr.frontend.implementations.wechat_bot_handler import (  # noqa: E402
    CallbackMessage,
    Command,
    OrderSide,
    ReplyKind,
    WeChatBotError,
    WeChatBotHandler,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_TIMEOUT = datetime.timedelta(seconds=60)


class _Clock:
    """可推进内存时钟。"""

    def __init__(self, t: datetime.datetime = _T0) -> None:
        self.t = t

    def __call__(self) -> datetime.datetime:
        return self.t

    def advance(self, **kwargs) -> None:
        self.t = self.t + datetime.timedelta(**kwargs)


def _handler(
    clock: _Clock | None = None,
    authenticator=None,
    watch: dict | None | object = ...,
    query: dict | None | object = ...,
    executed: list | None = None,
    with_executor: bool = True,
) -> WeChatBotHandler:
    watch_provider = (lambda: {"上证": "3210.5", "持仓": "3"}) if watch is ... else (
        (lambda: watch) if watch is not None else None
    )
    query_provider = (lambda key: {"标的": key, "现价": "10.24"}) if query is ... else (
        (lambda key: query) if query is not None else None
    )
    executor = None
    if with_executor:
        sink = executed if executed is not None else []
        executor = lambda ticket: sink.append(ticket) or "exec-001"  # noqa: E731
    return WeChatBotHandler(
        whitelist=frozenset({"alice", "bob"}),
        authenticator=authenticator or (lambda user, command: True),
        watch_provider=watch_provider,
        query_provider=query_provider,
        order_executor=executor,
        confirm_timeout=_TIMEOUT,
        clock=clock or _Clock(),
    )


def _msg(content: str, user: str = "alice", msg_id: str = "m-1", msg_type: str = "text") -> CallbackMessage:
    return CallbackMessage(
        msg_id=msg_id, from_user=user, content=content, received_at=_T0, msg_type=msg_type
    )


# ──────────────────────────────────────────────────────────────────────────────
# 消息 schema 校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestSchema:
    def test_empty_msg_id_raises(self) -> None:
        with pytest.raises(WeChatBotError):
            _handler().handle(_msg("盯盘", msg_id=""))

    def test_empty_user_raises(self) -> None:
        with pytest.raises(WeChatBotError):
            _handler().handle(_msg("盯盘", user=""))

    def test_empty_content_raises(self) -> None:
        with pytest.raises(WeChatBotError):
            _handler().handle(_msg(""))

    def test_non_text_msg_type_raises(self) -> None:
        with pytest.raises(WeChatBotError):
            _handler().handle(_msg("盯盘", msg_type="image"))


# ──────────────────────────────────────────────────────────────────────────────
# 指令鉴权
# ──────────────────────────────────────────────────────────────────────────────


class TestAuth:
    def test_non_whitelist_user_denied(self) -> None:
        reply = _handler().handle(_msg("盯盘", user="mallory"))
        assert reply.kind is ReplyKind.TEXT
        assert "无权限" in reply.text

    def test_authenticator_denies(self) -> None:
        handler = _handler(authenticator=lambda user, command: command is not Command.ORDER)
        reply = handler.handle(_msg("下单 买入 600000 100"))
        assert "无权限" in reply.text

    def test_authenticator_exception_denied(self) -> None:
        def _boom(user, command):
            raise RuntimeError("auth service down")

        reply = _handler(authenticator=_boom).handle(_msg("盯盘"))
        assert "无权限" in reply.text

    def test_missing_authenticator_raises(self) -> None:
        with pytest.raises(WeChatBotError):
            WeChatBotHandler(whitelist=frozenset({"alice"}), authenticator=None)

    def test_empty_whitelist_raises(self) -> None:
        with pytest.raises(WeChatBotError):
            WeChatBotHandler(whitelist=frozenset(), authenticator=lambda u, c: True)


# ──────────────────────────────────────────────────────────────────────────────
# 指令解析（词表闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestParse:
    def test_unknown_keyword_replies_vocab(self) -> None:
        reply = _handler().handle(_msg("重启"))
        assert reply.kind is ReplyKind.TEXT
        assert "未知指令" in reply.text

    def test_watch_card_reply(self) -> None:
        reply = _handler().handle(_msg("盯盘"))
        assert reply.kind is ReplyKind.CARD
        assert reply.card["title"] == "盯盘快照"
        assert {f["label"]: f["value"] for f in reply.card["fields"]} == {"上证": "3210.5", "持仓": "3"}

    def test_watch_provider_missing(self) -> None:
        reply = _handler(watch=None).handle(_msg("盯盘"))
        assert "未配置" in reply.text

    def test_query_ok(self) -> None:
        reply = _handler().handle(_msg("查询 600000"))
        assert reply.kind is ReplyKind.CARD
        assert "600000" in reply.card["title"]

    def test_query_missing_arg_usage(self) -> None:
        reply = _handler().handle(_msg("查询"))
        assert "用法" in reply.text


# ──────────────────────────────────────────────────────────────────────────────
# 下单二次确认（硬约束）
# ──────────────────────────────────────────────────────────────────────────────


class TestOrderConfirm:
    def test_order_creates_pending_with_card(self) -> None:
        handler = _handler()
        reply = handler.handle(_msg("下单 买入 600000 100"))
        assert reply.kind is ReplyKind.CARD
        assert "二次确认" in reply.card["title"]
        assert "60 秒" in reply.card["footer"]
        pending = handler.pending_orders()
        assert len(pending) == 1
        assert pending[0].order_id == "ord-000001"
        assert pending[0].side is OrderSide.BUY
        assert pending[0].quantity == 100
        assert pending[0].state == "pending_confirm"

    def test_order_bad_usage(self) -> None:
        assert "用法" in _handler().handle(_msg("下单 买入")).text

    def test_order_bad_side(self) -> None:
        assert "非法方向" in _handler().handle(_msg("下单 抄底 600000 100")).text

    def test_order_bad_quantity(self) -> None:
        handler = _handler()
        assert "数量非法" in handler.handle(_msg("下单 买入 600000 abc")).text
        assert "数量非法" in handler.handle(_msg("下单 买入 600000 -1")).text

    def test_order_executor_missing_rejected(self) -> None:
        reply = _handler(with_executor=False).handle(_msg("下单 买入 600000 100"))
        assert "下单通道未配置" in reply.text

    def test_second_order_while_pending_rejected(self) -> None:
        handler = _handler()
        handler.handle(_msg("下单 买入 600000 100"))
        reply = handler.handle(_msg("下单 卖出 600000 50"))
        assert "待确认" in reply.text
        assert len(handler.pending_orders()) == 1

    def test_confirm_within_timeout_executes(self) -> None:
        clock = _Clock()
        executed = []
        handler = _handler(clock=clock, executed=executed)
        handler.handle(_msg("下单 买入 600000 100"))
        clock.advance(seconds=30)
        reply = handler.handle(_msg("确认"))
        assert "已确认并下发" in reply.text
        assert "exec-001" in reply.text
        assert len(executed) == 1
        assert handler.settled_orders()[0].state == "confirmed"

    def test_confirm_after_timeout_rejected(self) -> None:
        clock = _Clock()
        executed = []
        handler = _handler(clock=clock, executed=executed)
        handler.handle(_msg("下单 买入 600000 100"))
        clock.advance(seconds=61)  # 超过 60s 确认窗
        reply = handler.handle(_msg("确认"))
        assert "超时" in reply.text
        assert "已拒绝" in reply.text
        assert executed == []  # 硬约束：超时不下发
        assert handler.settled_orders()[0].state == "expired"

    def test_confirm_without_pending(self) -> None:
        assert "无待确认订单" in _handler().handle(_msg("确认")).text

    def test_cancel_ok(self) -> None:
        handler = _handler()
        handler.handle(_msg("下单 买入 600000 100"))
        reply = handler.handle(_msg("取消"))
        assert "已取消" in reply.text
        assert handler.pending_orders() == ()
        assert handler.settled_orders()[0].state == "cancelled"

    def test_cancel_without_pending(self) -> None:
        assert "无待确认订单" in _handler().handle(_msg("取消")).text

    def test_executor_exception_rejects(self) -> None:
        handler = WeChatBotHandler(
            whitelist=frozenset({"alice"}),
            authenticator=lambda u, c: True,
            order_executor=lambda ticket: (_ for _ in ()).throw(RuntimeError("broker down")),
            confirm_timeout=_TIMEOUT,
            clock=_Clock(),
        )
        handler.handle(_msg("下单 买入 600000 100"))
        reply = handler.handle(_msg("确认"))
        assert "执行异常" in reply.text
        assert handler.settled_orders()[0].state == "failed"


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_flow_same_replies(self) -> None:
        h1, h2 = _handler(), _handler()
        for content in ("盯盘", "查询 600000", "下单 买入 600000 100", "确认"):
            r1 = h1.handle(_msg(content))
            r2 = h2.handle(_msg(content))
            assert r1 == r2
        assert h1.settled_orders() == h2.settled_orders()
