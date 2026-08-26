# [BLUEPRINT] MOD-FE-013 | docs/03_modules/_domain_frontend/wechat_bot_handler/blueprint.md
# [MODULE] zephyr.frontend.wechat_bot_handler
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（协议核心纯内存；鉴权器/盯盘·查询数据源/下单执行器/时钟全注入）
# [CONSUMERS] 运行时装配批（企业微信回调入口 / 盯盘·查询·下单适配器装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 消息schema校验(msg_type仅text); 指令词表闭合(盯盘|查询|下单|确认|取消); 白名单+注入鉴权器双重鉴权(鉴权器未注入Fail-Closed); 下单强制二次确认(超时拒绝硬约束, 待确认期间禁止新下单); 回复渲染JSON可序列化; 时钟全注入; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/wechat_bot_handler/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] WeChatBotError(占位 ZA-FE-UNREGISTERED-WECHAT-BOT)——消息schema非法/白名单空/鉴权器未注入/确认超时参数非法/数据源返回非法时抛
# [TESTS] tests/frontend/test_wechat_bot_handler.py
# [A_module] module_id=MOD-FE-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""WeChatBotHandler — 企业微信机器人处理器（MOD-FE-013）。

B9-10706（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-014，B9 D-FRONTEND-25）：
企业微信**回调接收**（消息 schema 校验）+ **指令鉴权**（白名单主体 + 注入
鉴权器双重判定）+ 盯盘/查询**指令解析**（指令词表闭合：盯盘/查询/下单/
确认/取消）+ **回复渲染**（文本/卡片模板，JSON 可序列化）+ **下单指令
二次确认硬约束**（确认超时拒绝，待确认期间禁止新下单）。

查重分工：feishu_bot_sender=飞书出站推送（本件=企业微信入站回调处理，
方向相反零交集）；alert_senders=企业微信出站实发（本件不发送，仅渲染
回复载荷交由装配层回写）。
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "CallbackMessage",
    "Command",
    "OrderSide",
    "OrderTicket",
    "Reply",
    "ReplyKind",
    "WeChatBotError",
    "WeChatBotHandler",
]

#: 指令关键词词表（闭合）
_KEYWORDS: Final[dict[str, "Command"]] = {}

#: 下单方向词表（闭合）
_SIDES: Final[dict[str, "OrderSide"]] = {}


class WeChatBotError(Exception):
    """企业微信回调输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-WECHAT-BOT。
    """


class Command(str, Enum):
    """指令词表（闭合）。"""

    WATCH = "watch"
    QUERY = "query"
    ORDER = "order"
    CONFIRM = "confirm"
    CANCEL = "cancel"


_KEYWORDS.update({
    "盯盘": Command.WATCH,
    "查询": Command.QUERY,
    "下单": Command.ORDER,
    "确认": Command.CONFIRM,
    "取消": Command.CANCEL,
})


class OrderSide(str, Enum):
    """下单方向（词表闭合）。"""

    BUY = "buy"
    SELL = "sell"


_SIDES.update({
    "买入": OrderSide.BUY,
    "卖出": OrderSide.SELL,
})


class ReplyKind(str, Enum):
    """回复形态（词表闭合）。"""

    TEXT = "text"
    CARD = "card"


@dataclass(frozen=True)
class CallbackMessage:
    """企业微信回调消息（入站载荷，frozen）。"""

    msg_id: str
    from_user: str
    content: str
    received_at: datetime.datetime
    msg_type: str = "text"


@dataclass(frozen=True)
class Reply:
    """回复渲染载荷（JSON 可序列化；card 为 None 时纯文本）。"""

    kind: ReplyKind
    to_user: str
    text: str
    card: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class OrderTicket:
    """下单工单（二次确认状态机载体）。"""

    order_id: str
    user: str
    symbol: str
    side: OrderSide
    quantity: int
    created_at: datetime.datetime
    expires_at: datetime.datetime
    state: str  # pending_confirm | confirmed | cancelled | expired | failed


class WeChatBotHandler:
    """企业微信机器人处理器（回调校验 + 鉴权 + 解析 + 渲染 + 二次确认）。

    Args:
        whitelist: 白名单主体（from_user 集合，非空）。
        authenticator: 指令鉴权器注入（(user, command) → bool；未注入 Fail-Closed）。
        watch_provider: 盯盘数据源注入（() → Mapping）。
        query_provider: 查询数据源注入（(key) → Mapping）。
        order_executor: 下单执行器注入（OrderTicket → 执行回执号 str；未注入禁止下单）。
        confirm_timeout: 二次确认超时（正 timedelta，超时拒绝硬约束）。
        clock: 时钟注入（超时判定确定性）。
    """

    def __init__(
        self,
        *,
        whitelist: frozenset[str] | set[str] | tuple[str, ...],
        authenticator: Callable[[str, Command], bool],
        watch_provider: Callable[[], Mapping[str, Any]] | None = None,
        query_provider: Callable[[str], Mapping[str, Any]] | None = None,
        order_executor: Callable[[OrderTicket], str] | None = None,
        confirm_timeout: datetime.timedelta = datetime.timedelta(seconds=60),
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if isinstance(whitelist, (str, bytes)) or not whitelist:
            raise WeChatBotError("whitelist 为空（鉴权 Fail-Closed）")
        for user in whitelist:
            if not isinstance(user, str) or not user:
                raise WeChatBotError(f"白名单主体非法: {user!r}")
        if not callable(authenticator):
            raise WeChatBotError("authenticator 未注入（鉴权 Fail-Closed）")
        for name, provider in (
            ("watch_provider", watch_provider),
            ("query_provider", query_provider),
            ("order_executor", order_executor),
        ):
            if provider is not None and not callable(provider):
                raise WeChatBotError(f"{name} 不可调用")
        if not isinstance(confirm_timeout, datetime.timedelta) or confirm_timeout <= datetime.timedelta(0):
            raise WeChatBotError("confirm_timeout 非法（须为正 timedelta）")
        self._whitelist = frozenset(whitelist)
        self._authenticator = authenticator
        self._watch_provider = watch_provider
        self._query_provider = query_provider
        self._order_executor = order_executor
        self._confirm_timeout = confirm_timeout
        self._clock = clock or datetime.datetime.now
        self._counter = 0
        self._pending: dict[str, OrderTicket] = {}  # user -> 待确认工单
        self._orders: list[OrderTicket] = []  # 终态工单留痕

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _text(user: str, text: str) -> Reply:
        return Reply(kind=ReplyKind.TEXT, to_user=user, text=text)

    @staticmethod
    def _card(user: str, title: str, fields: Mapping[str, Any], footer: str = "") -> Reply:
        card = {
            "title": title,
            "fields": [{"label": str(k), "value": str(v)} for k, v in fields.items()],
            "footer": footer,
        }
        return Reply(kind=ReplyKind.CARD, to_user=user, text=title, card=card)

    def _settle(self, ticket: OrderTicket, state: str) -> OrderTicket:
        settled = replace(ticket, state=state)
        self._pending.pop(ticket.user, None)
        self._orders.append(settled)
        return settled

    # ── 回调主流程 ────────────────────────────────────────────────────────

    def handle(self, message: CallbackMessage) -> Reply:
        """回调处理：schema 校验 → 解析 → 双重鉴权 → 指令分发 → 回复渲染。"""
        if not isinstance(message, CallbackMessage):
            raise WeChatBotError(f"消息类型非法: {message!r}")
        if message.msg_type != "text":
            raise WeChatBotError(f"msg_type 非法: {message.msg_type!r}（仅支持 text）")
        for field_name, value in (
            ("msg_id", message.msg_id),
            ("from_user", message.from_user),
            ("content", message.content),
        ):
            if not isinstance(value, str) or not value:
                raise WeChatBotError(f"消息字段 {field_name} 为空")
        if not isinstance(message.received_at, datetime.datetime):
            raise WeChatBotError(f"received_at 类型非法: {message.received_at!r}")

        user = message.from_user
        parts = message.content.split()
        keyword = parts[0]
        command = _KEYWORDS.get(keyword)
        if command is None:
            return self._text(user, f"未知指令：{keyword}（支持 盯盘/查询/下单/确认/取消）")

        if user not in self._whitelist:
            _log.warning("非白名单主体拒绝: %s %s", user, command.value)
            return self._text(user, "无权限：主体不在白名单")
        try:
            allowed = bool(self._authenticator(user, command))
        except Exception:  # noqa: BLE001 — 鉴权器异常按拒绝处理
            _log.exception("authenticator 异常: %s %s", user, command.value)
            allowed = False
        if not allowed:
            return self._text(user, f"无权限：指令 {keyword} 被鉴权器拒绝")

        if command is Command.WATCH:
            return self._handle_watch(user)
        if command is Command.QUERY:
            return self._handle_query(user, parts)
        if command is Command.ORDER:
            return self._handle_order(user, parts)
        if command is Command.CONFIRM:
            return self._handle_confirm(user)
        return self._handle_cancel(user)

    # ── 指令处理 ──────────────────────────────────────────────────────────

    def _handle_watch(self, user: str) -> Reply:
        if self._watch_provider is None:
            return self._text(user, "盯盘数据未配置")
        data = self._watch_provider()
        if not isinstance(data, Mapping):
            raise WeChatBotError(f"盯盘数据源返回非法: {type(data)!r}")
        return self._card(user, "盯盘快照", dict(data))

    def _handle_query(self, user: str, parts: list[str]) -> Reply:
        if len(parts) < 2 or not parts[1]:
            return self._text(user, "用法：查询 <标的/事项>")
        if self._query_provider is None:
            return self._text(user, "查询通道未配置")
        key = parts[1]
        data = self._query_provider(key)
        if not isinstance(data, Mapping):
            raise WeChatBotError(f"查询数据源返回非法: {type(data)!r}")
        return self._card(user, f"查询结果：{key}", dict(data))

    def _handle_order(self, user: str, parts: list[str]) -> Reply:
        if len(parts) != 4:
            return self._text(user, "用法：下单 <买入|卖出> <标的> <数量>")
        side = _SIDES.get(parts[1])
        if side is None:
            return self._text(user, f"非法方向：{parts[1]}（仅 买入/卖出）")
        symbol = parts[2]
        if not symbol.isalnum():
            return self._text(user, f"非法标的：{symbol!r}")
        try:
            quantity = int(parts[3])
        except ValueError:
            return self._text(user, f"数量非法：{parts[3]!r}")
        if quantity <= 0:
            return self._text(user, f"数量非法：{quantity}（须为正整数）")
        if self._order_executor is None:
            return self._text(user, "下单通道未配置（硬约束：未装配执行器禁止下单）")
        if user in self._pending:
            return self._text(user, "存在待确认订单，请先 确认 或 取消")
        now = self._clock()
        self._counter += 1
        ticket = OrderTicket(
            order_id=f"ord-{self._counter:06d}",
            user=user,
            symbol=symbol,
            side=side,
            quantity=quantity,
            created_at=now,
            expires_at=now + self._confirm_timeout,
            state="pending_confirm",
        )
        self._pending[user] = ticket
        seconds = int(self._confirm_timeout.total_seconds())
        return self._card(
            user,
            "下单二次确认",
            {
                "订单号": ticket.order_id,
                "方向": parts[1],
                "标的": symbol,
                "数量": quantity,
            },
            footer=f"请在 {seconds} 秒内回复 确认 / 取消，超时自动拒绝",
        )

    def _handle_confirm(self, user: str) -> Reply:
        ticket = self._pending.get(user)
        if ticket is None:
            return self._text(user, "无待确认订单")
        now = self._clock()
        if now > ticket.expires_at:
            self._settle(ticket, "expired")
            _log.warning("下单确认超时拒绝: %s %s", user, ticket.order_id)
            return self._text(user, f"确认超时，订单 {ticket.order_id} 已拒绝（超时硬约束）")
        try:
            exec_ref = self._order_executor(ticket)
        except Exception:  # noqa: BLE001 — 执行异常按未下发处理
            _log.exception("order_executor 异常: %s", ticket.order_id)
            self._settle(ticket, "failed")
            return self._text(user, f"订单 {ticket.order_id} 执行异常，未下发")
        if not isinstance(exec_ref, str) or not exec_ref:
            self._settle(ticket, "failed")
            return self._text(user, f"订单 {ticket.order_id} 执行回执非法，未下发")
        self._settle(ticket, "confirmed")
        return self._text(user, f"订单 {ticket.order_id} 已确认并下发，执行回执 {exec_ref}")

    def _handle_cancel(self, user: str) -> Reply:
        ticket = self._pending.get(user)
        if ticket is None:
            return self._text(user, "无待确认订单")
        self._settle(ticket, "cancelled")
        return self._text(user, f"订单 {ticket.order_id} 已取消")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def pending_orders(self) -> tuple[OrderTicket, ...]:
        """待确认工单（按 order_id 确定性排序）。"""
        return tuple(sorted(self._pending.values(), key=lambda t: t.order_id))

    def settled_orders(self) -> tuple[OrderTicket, ...]:
        """终态工单留痕（按终态化先后）。"""
        return tuple(self._orders)
