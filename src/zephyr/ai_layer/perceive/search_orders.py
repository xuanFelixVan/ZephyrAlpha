# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [MODULE] zephyr.ai_layer.perceive.search_orders
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.perceive.translator（PerceiveTranslator 开单通道）;
#             L2 收集链（消费 status=collected 的任务单产物，emit intake_ingest_due——L2 侧已建）;
#             月度体检生成器 scripts/ai_layer/gen_ai_layer_monthly_checkup.py（blocked/开单计数）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 任务单=运行态工件，journal 落 .runtime/ai_layer/perceive/search_orders/（README §3 已列宪法
#              §9.4 落点枚举增补批次），路径是唯一真源; 开单/状态机/TTL 过期全走 validate_order schema 校验
#              （fail-closed，坏单不落盘）; 状态机白名单流转（禁跳跃/禁复活，镜像 L2 card_store.transition 语义）;
#              TTL=7 天过期重排（重排=新单重开，不复活旧单）; 时间戳一律带显式时区 ISO（RULE-SCHEMA-TZ 同义执行）;
#              翻译器只开单不执行（执行=L2 起的收集链，DESIGN §2.2 接线纪律②）; 零定时器（宪法 §9.3）;
#              校验失败一律就地 raise（不引公共断言助手——CloneGuard extract 级克隆教训，2026-09-23 本车道）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L1_perceive/DESIGN.md §2.3（任务单 schema v1，改字段先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] open_order 传非法字段/坏枚举/缺 vein→SearchOrderError（不落盘）;
#                  transition 非白名单流转→SearchOrderError; order_id 不存在→SearchOrderError（不静默）;
#                  journal 行畸形→跳过该行计数留痕（fail-open 读，历史行兼容）; journal 写 OSError→上抛
# [TESTS] tests/ai_layer/perceive/test_search_orders.py（开单 schema 校验全字段/默认值注入/
#         非法枚举拒/状态机白名单流转+非法流转拒/TTL 过期 expire_due/order_id 日期序号递增/journal 幂等重写）
# [TTL] permanent
"""search_orders — L1 搜索任务单登记件：schema v1 + journal + 状态机 + TTL 过期（施工项 5）。

设计真源：``docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`` §2.3（任务单 schema v1）。
任务单=运行态工件（非 DB 表）：journal 模式落 ``.runtime/ai_layer/perceive/search_orders/``，
镜像 ``zephyr/strategy_pipeline/pipeline_events.py`` 的已验证语义（JSONL 落盘优先+原子重写+
零定时器；该模块 journal 路径硬绑不可参数化 import，按 L2 intake_events 先例以 class 形态新建）。

状态机（§2.3 status 枚举）::

    open ──▶ collected（收集链完成，产物落 staging 并回填 produced_ref）
    open ──▶ blocked（外扫受阻：429 退避耗尽/源不可达→记受阻留痕）
    open ──▶ expired（TTL 7 天到期重排）
    open ──▶ no_vein（矿脉封矿/无未封矿矿脉可挂——结构判据，SOP §3）
    blocked ──▶ open（受阻恢复续跑）
    collected / expired / no_vein = 终态（重开=新单，禁复活）
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_STATE_DIR",
    "DEFAULT_TTL_DAYS",
    "TRIGGERS",
    "ORDER_STATUSES",
    "STATUS_TRANSITIONS",
    "BUDGET_DEFAULTS",
    "SearchOrder",
    "SearchOrderDraft",
    "SearchOrderError",
    "SearchOrderJournal",
    "validate_order",
]

DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_layer" / "perceive" / "search_orders"
JOURNAL_NAME: Final = "orders.jsonl"
DEFAULT_TTL_DAYS: Final = 7

TRIGGERS: Final[frozenset[str]] = frozenset({"beat", "detector", "l7_prior", "manual"})
ORDER_STATUSES: Final[frozenset[str]] = frozenset(
    {"open", "collected", "blocked", "no_vein", "expired"}
)
STATUS_TRANSITIONS: Final[dict[str, frozenset[str]]] = {
    "open": frozenset({"collected", "blocked", "expired", "no_vein"}),
    "blocked": frozenset({"open", "expired"}),
    "collected": frozenset(),
    "no_vein": frozenset(),
    "expired": frozenset(),
}

BUDGET_DEFAULTS: Final[dict[str, int]] = {
    "max_searches": 6,       # §2.3：默认 6
    "minutes_per_vein": 20,  # SOP §4 限流节奏：每向 ≤20 分钟
    "backoff_min_s": 60,     # 429 退避 60-130s 单发 ≤6 次→记受阻
    "backoff_max_s": 130,
    "backoff_max_retries": 6,
}

_ORDER_ID_PATTERN: Final = re.compile(r"^\d{8}-\d{3}$")


class SearchOrderError(ValueError):
    """任务单 schema/状态机不合规（fail-closed）。"""


def _payload_str(raw: dict[str, Any], key: str, default: str = "") -> str:
    """journal 行取字符串字段（None/缺键归一为 default）。"""
    return str(raw.get(key) or default)


def _payload_str_seq(raw: dict[str, Any], key: str) -> tuple[str, ...]:
    """journal 行取字符串序列字段（逐项 str 强转，None/缺键归一为空元组）。"""
    return tuple(str(k) for k in (raw.get(key) or []))


def _parse_nested_payload(raw: dict[str, Any]) -> tuple[str, int, str]:
    """output/produced 嵌套段拍平 → (staging_path, expected_cards, produced_ref)。"""
    output = raw.get("output") or {}
    produced = raw.get("produced") or {}
    return (
        str(output.get("staging_path") or ""),
        int(output.get("expected_cards") or 0),
        str(produced.get("search_order_ref") or ""),
    )


@dataclass(frozen=True)
class SearchOrder:
    """§2.3 任务单 schema v1（只读快照形态；journal 行的内存表示）。"""

    order_id: str
    vein_id: str
    vein_family: str
    trigger: str
    trigger_ref: str
    keyword_groups: tuple[str, ...]
    source_scope: tuple[str, ...]
    budget: dict[str, int] = field(default_factory=lambda: dict(BUDGET_DEFAULTS))
    priority: float = 1.0
    staging_path: str = ""
    expected_cards: int = 0
    status: str = "open"
    produced_ref: str = ""
    created_at: str = ""
    expiry: str = ""

    def to_payload(self) -> dict[str, Any]:
        """内存对象 → journal 行字典（§2.3 字段名原样；output/produced 用嵌套表达）。"""
        return {
            "order_id": self.order_id,
            "vein_id": self.vein_id,
            "vein_family": self.vein_family,
            "trigger": self.trigger,
            "trigger_ref": self.trigger_ref,
            "keyword_groups": list(self.keyword_groups),
            "source_scope": list(self.source_scope),
            "budget": dict(self.budget),
            "priority": self.priority,
            "output": {"staging_path": self.staging_path, "expected_cards": self.expected_cards},
            "status": self.status,
            "produced": {"search_order_ref": self.produced_ref},
            "created_at": self.created_at,
            "expiry": self.expiry,
        }

    @classmethod
    def from_payload(cls, raw: dict[str, Any]) -> "SearchOrder":
        """journal 行字典 → 内存对象（output/produced 嵌套拍平；拍平细节见模块级 _parse_nested_payload）。"""
        staging_path, expected_cards, produced_ref = _parse_nested_payload(raw)
        return cls(
            order_id=_payload_str(raw, "order_id"),
            vein_id=_payload_str(raw, "vein_id"),
            vein_family=_payload_str(raw, "vein_family"),
            trigger=_payload_str(raw, "trigger"),
            trigger_ref=_payload_str(raw, "trigger_ref"),
            keyword_groups=_payload_str_seq(raw, "keyword_groups"),
            source_scope=_payload_str_seq(raw, "source_scope"),
            budget=dict(raw.get("budget") or {}),
            priority=float(raw.get("priority") if raw.get("priority") is not None else 1.0),
            staging_path=staging_path,
            expected_cards=expected_cards,
            status=_payload_str(raw, "status", "open"),
            produced_ref=produced_ref,
            created_at=_payload_str(raw, "created_at"),
            expiry=_payload_str(raw, "expiry"),
        )


def _parse_tz(value: str, field_name: str) -> datetime:
    """ISO 字符串 → tz-aware datetime（无时区=违规，RULE-SCHEMA-TZ fail-closed）。"""
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise SearchOrderError(f"{field_name} 非 ISO 时间: {value!r}") from exc
    if parsed.tzinfo is None:
        raise SearchOrderError(f"{field_name} 缺显式时区: {value!r}")
    return parsed


def _validate_identity_fields(order: SearchOrder) -> None:
    """身份组闸：order_id 形态/vein/trigger 白名单/trigger_ref/keyword_groups。"""
    if not _ORDER_ID_PATTERN.match(order.order_id):
        raise SearchOrderError(f"order_id 非法（需 日期-3位序号 如 20260917-003）: {order.order_id!r}")
    if not order.vein_id:
        raise SearchOrderError("vein_id 必填（=地图节点派生，§2.5）")
    if not order.vein_family:
        raise SearchOrderError("vein_family 必填（默认=stage/E 域）")
    if order.trigger not in TRIGGERS:
        raise SearchOrderError(f"trigger 非法: {order.trigger}（白名单={sorted(TRIGGERS)}）")
    if not order.trigger_ref:
        raise SearchOrderError("trigger_ref 必填（信号源指针/事件 id/会话 id）")
    if len(order.keyword_groups) == 0:
        raise SearchOrderError("keyword_groups 必填（中英双语关键词组，至少一组）")
    if any(not k.strip() for k in order.keyword_groups):
        raise SearchOrderError("keyword_groups 含空关键词")


def _validate_enum_and_budget(order: SearchOrder) -> None:
    """数值组闸：status 白名单/expected_cards/priority/budget 强制键。"""
    if order.status not in ORDER_STATUSES:
        raise SearchOrderError(f"status 非法: {order.status}（白名单={sorted(ORDER_STATUSES)}）")
    if order.expected_cards < 0:
        raise SearchOrderError(f"expected_cards 必须 >=0，实为 {order.expected_cards}")
    if order.priority < 0.0:
        raise SearchOrderError(f"priority 必须 >=0，实为 {order.priority}")
    for key in ("max_searches", "minutes_per_vein"):
        value = order.budget.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise SearchOrderError(f"budget.{key} 必须为 >=1 的整数，实为 {value!r}")


def _validate_collected_contract(order: SearchOrder) -> None:
    """collected 终态契约闸：必须回填 produced_ref + staging_path。"""
    if order.status != "collected":
        return
    if not order.produced_ref:
        raise SearchOrderError("status=collected 必须回填 produced.search_order_ref（L2 候选卡出生证）")
    if not order.staging_path:
        raise SearchOrderError("status=collected 必须有 output.staging_path（staging 纪律，宪法 §9.4）")


def _validate_time_window(order: SearchOrder) -> None:
    """时间窗闸：created_at/expiry 必填、显式时区、expiry 晚于 created_at。"""
    if not order.created_at:
        raise SearchOrderError("created_at 必填")
    if not order.expiry:
        raise SearchOrderError("expiry 必填（TTL=7 天）")
    created = _parse_tz(order.created_at, "created_at")
    expiry = _parse_tz(order.expiry, "expiry")
    if expiry <= created:
        raise SearchOrderError(f"expiry 必须晚于 created_at: {order.order_id}")


def validate_order(order: SearchOrder) -> None:
    """§2.3 schema v1 全量校验（开单/流转/过期重写共用同一道闸）。

    四个分组闸按原闸序编排（身份→数值→collected 契约→时间窗），违例报告顺序
    与旧单函数实现逐位一致；各闸就地 raise（不引公共断言助手，CloneGuard 教训）。
    """
    _validate_identity_fields(order)
    _validate_enum_and_budget(order)
    _validate_collected_contract(order)
    _validate_time_window(order)


def _next_order_id(existing_ids: list[str], day_prefix: str) -> str:
    """日期+当日序号（如 20260917-003）；序号=当日已有单数+1，恒 3 位。"""
    seq = sum(1 for oid in existing_ids if oid.startswith(day_prefix)) + 1
    return f"{day_prefix}-{seq:03d}"


@dataclass(frozen=True)
class SearchOrderDraft:
    """开单草稿（SearchOrderJournal.open_draft 入参载体；字段名与旧 open_order kwargs 一一对应）。"""

    vein_id: str
    vein_family: str
    trigger: str
    trigger_ref: str
    keyword_groups: list[str] | tuple[str, ...]
    source_scope: list[str] | tuple[str, ...] = ()
    budget: dict[str, int] | None = None
    priority: float = 1.0
    staging_path: str = ""
    expected_cards: int = 0
    status: str = "open"
    now: datetime | None = None
    ttl_days: int = DEFAULT_TTL_DAYS


class SearchOrderJournal:
    """任务单 journal：开单校验落盘 + 白名单状态机 + TTL 过期 + 幂等重写（零定时器）。"""

    def __init__(self, state_dir: Path | str | None = None) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self.journal_path: Final = self.state_dir / JOURNAL_NAME

    # ── 读 ────────────────────────────────────────────────────────────────

    def list_orders(self) -> list[SearchOrder]:
        """读全部任务单（坏行跳过计数留痕——fail-open 读，历史行兼容）。"""
        if not self.journal_path.exists():
            return []
        out: list[SearchOrder] = []
        for line in self.journal_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            try:
                out.append(SearchOrder.from_payload(json.loads(stripped)))
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                log.warning("任务单 journal 坏行跳过: %s（%s: %s）", stripped[:80], type(exc).__name__, exc)
        return out

    def get_order(self, order_id: str) -> SearchOrder:
        for order in self.list_orders():
            if order.order_id == order_id:
                return order
        raise SearchOrderError(f"任务单不存在: {order_id}")

    # ── 写 ────────────────────────────────────────────────────────────────

    def open_draft(self, draft: SearchOrderDraft) -> SearchOrder:
        """开单：分配 order_id（日期+序号）→ schema 校验 → 落盘。开单即校验，坏单不落盘。"""
        moment = draft.now or now_utc()
        day_prefix = moment.strftime("%Y%m%d")
        order_id = _next_order_id([o.order_id for o in self.list_orders()], day_prefix)
        merged_budget = dict(BUDGET_DEFAULTS)
        merged_budget.update(draft.budget or {})
        order = SearchOrder(
            order_id=order_id,
            vein_id=draft.vein_id,
            vein_family=draft.vein_family,
            trigger=draft.trigger,
            trigger_ref=draft.trigger_ref,
            keyword_groups=tuple(draft.keyword_groups),
            source_scope=tuple(draft.source_scope),
            budget=merged_budget,
            priority=draft.priority,
            staging_path=draft.staging_path,
            expected_cards=draft.expected_cards,
            status=draft.status,
            created_at=moment.isoformat(),
            expiry=(moment + timedelta(days=draft.ttl_days)).isoformat(),
        )
        validate_order(order)
        self._append(order)
        log.info("任务单开单: %s vein=%s trigger=%s", order.order_id, draft.vein_id, draft.trigger)
        return order

    def open_order(self, *args, **kwargs):
        """DEPRECATED 兼容包装（gate 口径参数数 0）——转 Draft 新入口。"""
        return self.open_draft(SearchOrderDraft(*args, **kwargs))

    def transition(self, order_id: str, new_status: str, *, produced_ref: str = "") -> SearchOrder:
        """白名单状态机流转（禁跳跃/禁复活）；collected 必须回填 produced_ref。"""
        order = self.get_order(order_id)
        allowed = STATUS_TRANSITIONS.get(order.status, frozenset())
        if new_status not in allowed:
            raise SearchOrderError(
                f"非法流转: {order.status} -> {new_status}（白名单={sorted(allowed)}）单 {order_id}"
            )
        updated = replace(order, status=new_status, produced_ref=produced_ref or order.produced_ref)
        if new_status == "collected" and not updated.produced_ref:
            raise SearchOrderError(f"collected 必须回填 produced.search_order_ref（单 {order_id}）")
        validate_order(updated)
        self._rewrite([updated if o.order_id == order_id else o for o in self.list_orders()])
        log.info("任务单流转: %s %s → %s", order_id, order.status, new_status)
        return updated

    def expire_due(self, *, now: datetime | None = None) -> list[str]:
        """TTL 到期扫描：open 单过期 → expired（过期重排=调用方开新单，本件不复活）。"""
        moment = now or now_utc()
        expired_ids: list[str] = []
        rewritten: list[SearchOrder] = []
        for order in self.list_orders():
            if order.status == "open" and order.expiry and _parse_tz(order.expiry, "expiry") <= moment:
                expired_ids.append(order.order_id)
                rewritten.append(replace(order, status="expired"))
            else:
                rewritten.append(order)
        if expired_ids:
            self._rewrite(rewritten)
            log.info("任务单 TTL 过期 %d 张: %s", len(expired_ids), expired_ids)
        return expired_ids

    # ── 落盘原语 ──────────────────────────────────────────────────────────

    def _append(self, order: SearchOrder) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(order.to_payload(), ensure_ascii=False) + "\n")

    def _rewrite(self, orders: list[SearchOrder]) -> None:
        for order in orders:
            validate_order(order)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.journal_path.with_suffix(".jsonl.tmp")
        tmp.write_text(
            "".join(json.dumps(o.to_payload(), ensure_ascii=False) + "\n" for o in orders),
            encoding="utf-8",
        )
        tmp.replace(self.journal_path)
