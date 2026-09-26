# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] zephyr.ai_layer.scheduling.confirm_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.scheduling.scheduling_events (SchedulingJournal——order_confirmed_due 事件账，journal=唯一真源红蓝 R1-B10 同款); zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc); 标准库 msvcrt/fcntl（OS 字节排他锁，复刻 gov_audit/writer.py _cross_process_append_lock 先例，零新三方依赖）；
#                产物（.runtime/ai_scheduling/ 域内）：orders.jsonl（工单快照）、confirm_decisions.jsonl（决策账）、pending_events.jsonl（事件账，journal 件管）、confirm_intents/<receipt>.json（写前意图账=半写自愈凭据，完成即删）、orders.jsonl.gate.lock（串化锁，只创建永不删除）、orders_quarantine.jsonl（快照畸形/重复行留痕，append-only 按 sha 去重）
# [CONSUMERS] zephyr.frontend.dashboard.api_server POST /api/schedulegate-confirm（★待接线一行，见 docs/_working/ai_layer_vision/closure_wave2/AI2_scheduling_host_confirm.md 回执——api_server 属本波禁触热件，本模块只供判定面不代接线；**接线前置三件未齐＝①会话鉴权真源（actor/allow_amend 不得来自请求体）②并发串化（本件已具备）③OrderFileStore 归档语义确认（文件快照 vs PG ai_work_order 谁是长期真源）——判据与理由=docs/_working/fullflow_mining/05_missing_p0/wiring_C_confirm_hardening.md）
# [STARTUP] event_driven
# [MATURITY] hardened（W6-C 消红队三雷，2026-09-26）
# [INVARIANTS] 判定=纯函数可全枚举（evaluate_confirm 零 IO 零取时，now 注入）；幂等=同单同判再请求返回原回执零新事件零重写（判定依据=decision ledger 末行＋快照回执对账，非内存态）；
#              **并发幂等（雷 1 治本）**：decide 全程持同一 state_dir 的串化闸（进程内 RLock＋跨进程 OS 字节排他锁），读→判→三写是一整个临界区，第 2..N 个并发同请求拿锁后必读到已落定 decided 行＋快照回执 ⇒ 走 idempotent_hit，临界区内零重试零轮询（不是"重试到不冲突"）；**半写不假持久化（雷 2 治本）**：三写前先落写前意图账，三写后按落点实读复验，任一条缺失=上抛 ConfirmPersistError(stage=...) 且意图账留盘；后续对同单的 decide 或显式 reconcile() 先自愈（同一 receipt_id 补齐缺腿，不新增事件/决策行）；决策账有 decided 行而快照缺该 receipt ⇒ 判 persist_failed 报红，绝不回幂等成功；
#              **快照零行丢失（雷 3 治本）**：OrderFileStore.upsert 改按行外科式改写——畸形行/非 dict 行/未知行一律原文回写，永不整档重建；写前＋落盘复读后各做一次行集指纹比对，丢失集非空即拒写/报红；畸形行另落 orders_quarantine.jsonl 留痕＋log.error 出声；同 order_id 多行=只替换首行、余行原样保留＋留痕报红（不静默合档）；
#              改判留痕不删（新决策 append，旧行永在——DESIGN C9 "改判留痕" + §2.4 "Owner 拒→作废归档审计链留痕不删"）；拒因可回传（每次拒绝带结构化 codes 清单，拒绝请求同样落审计 outcome=rejected_request）；状态机红线：仅 pending 可拍板（§2.7 七态，dispatched/done/dead 非拍板对象，held_* 归各自解除事件）；仅骨架级（owner_gate=true）走本门（模块级自动派不经 Owner 确认）；
#              confirm→state 保持 pending 加 owner_decision 标记（派工仍走 T1 双预检+E0 拉式闸，确认≠派工，DESIGN §2.4）；reject→state=dead 作废归档（禁删行）；三处落点全写：①事件账 SchedulingJournal(order_confirmed_due) ②决策账 confirm_decisions.jsonl（append-only）③工单快照 orders.jsonl（audit_log 只前缀追加，行内另钉 owner_receipt_id 作半写对账锚）；零定时器零轮询；naive datetime 拒收（RULE-SCHEMA-TZ）；测试全 tmp_path 零生产路径
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L5_schedule_gate/DESIGN.md §2.4/§2.7+C9（确认语义真源）；docs/_working/fullflow_mining/03_promotion_ab/（WIRING_NOTES 落点证据）；docs/_working/fullflow_mining/05_missing_p0/rb2_guard_attacks.md §四/§十 A3-A4（红队实测三雷＝本件回归靶，改这三段语义须同批改测）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 判定不抛错——结构化返回 {ok:false, error, codes}；**落点写失败（含 journal emit / 决策账 append / 快照 upsert / 意图账写）一律上抛 ConfirmPersistError 带 stage**（绝不"假持久化"半截回执，红队 §二.23 修前那条绕过已封）；快照重写丢行=OrdersRowLossError 上抛（雷 3）；锁耗尽=TimeoutError 上抛（fail-closed，丢一次请求好过双写重复派工）；orders.jsonl 畸形行=原文保留＋quarantine 留痕＋出声（不再"跳过计数后被下一次 upsert 抹掉"）；naive datetime→ValueError
# [TESTS] tests/ai_layer/scheduling/test_confirm_gate.py（confirm/reject 正路径+三落点齐/顺序幂等零重复事件/**并发 12 线程同请求=1 行 decided+1 事件+同一 receipt**/改判留痕不删/decision_conflict 拒/非骨架拒/非法 decision 拒/未知单拒/非 pending 态拒/缺 order_id 拒/拒绝请求亦落审计/decided_at tz 断言/**第二写失败桩=ConfirmPersistError(stage=decisions)+撤桩重跑自愈且回执不变**/第三写失败同构+快照回执落定/半写禁当幂等命中/畸形行经无关 upsert 后逐字节仍在盘+quarantine 留痕+出声/16 线程并发 upsert 零丢单/全部 tmp_path）
# [TTL] permanent
"""confirm_gate — L5 骨架级"一键确认"的判定与落点（C9 唯一写路由的后端件）。

背景：前端已在 HEAD 调 ``POST /api/schedulegate-confirm``（commit 6a4124cd8f），api_server 侧
当前为"诚实拒执行"占位。本模块给出 **确认判定与落点** 的可施工实现；api_server 属禁触热件，
待接线一行登记在车道记录册，由总筹在窗口内单点接通。

**今日状态如实登记**：本件**未接线**（零生产调用点＝红队判"装饰件"成立）。W6-C 车道修的
是"一接线就咬资金面"的三颗雷（红队案卷 §四.1/.2/.4），**修雷 ≠ 已生效**。接线前置三件见
头注 ``[CONSUMERS]`` 与 ``wiring_C_confirm_hardening.md`` §二处置 2。

**落点判定（本案卷结论，通道复核=治理/Owner）**：确认态不落 seeds（种子=排班登记面，
塞工单状态即违"排班一张真源"），而是三处同写、各司其职——

1. **事件账**：``order_confirmed_due`` 进 SchedulingJournal（journal=唯一真源，下游 order_daemon
   /派工段事件唤醒消费，零轮询；红蓝 R1-B10"watchdog 降级为补偿读指针"同语义）。
2. **决策账**：``confirm_decisions.jsonl`` append-only（幂等判定依据 + 改判留痕不删 + 拒因审计）。
3. **工单快照**：``orders.jsonl`` 内该单回写——confirm→``owner_decision='confirm'`` 且 state
   保持 ``pending``（确认≠派工：派工仍须过 T1 双预检+E0 拉式问闸，DESIGN §2.4）；
   reject→``state='dead'`` 作废归档（审计链留痕不删，复活仅 Owner 手递新单 §2.7）；
   两路都钉 ``owner_receipt_id``＝半写对账锚（红队 §四.2 点名的修法）。

判定规则（纯函数，任一违例=拒绝并回传 codes）::

    missing_order_id          order_id 空/缺失
    decision_not_vocab        decision ∉ {confirm, reject}
    order_not_found           快照查无此单
    not_skeleton_level        owner_gate 非真（模块级工单走自动派，不进 Owner 门）
    state_not_confirmable     state ≠ pending（§2.7 仅 pending 可拍板）
    decision_conflict         已有相反决策（allow_amend=False 时；=True 改判走新行留痕）
    already_decided           同单同判 → 幂等成功（返回原回执，非拒绝；快照须真带该回执）

持久化次序（雷 1/2 治本骨架）::

    拿串化闸 → 自愈该单遗留意图账 → 读快照+决策账 → 判定
      ├ 拒绝 → 决策账落 rejected_request 行 → 回结构化拒绝
      ├ 幂等命中 → 校验快照回执 → 回原回执（零新事件零重写）
    └ 新决策 → ①意图账(confirm_intents/<receipt>.json) ②事件账 ③决策账 ④工单快照
               → 三处实读复验 → 删意图账 → 回执

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 拍板请求与盘上三落点状态
#   fields: order_id/decision/allow_amend；orders.jsonl/confirm_decisions.jsonl/journal/意图账
#   code: ConfirmGate.decide/decide_from_payload
# 层: 算法
# - id: A1
#   name_zh: 串化闸内自愈→纯函数判定→三路分流
#   name_en: decide
#   intro: _recover_locked 先自愈；evaluate_confirm 全枚举；拒绝落审计行；幂等命中校验快照回执禁判半写
#   inputs: I1
#   outputs: O1
# - id: A2
#   name_zh: 新决策三写与半写自愈
#   name_en: _decide_new/_heal_intent_legs
#   intro: 写前意图账→事件→决策行→快照→实读复验→删意图账；任一腿倒下意图账留盘待复跑
#   inputs: I1
#   outputs: O1
# 层: 输出
# - id: O1
#   name: 前端契约回执/ConfirmPersistError(stage)
#   fields: ok/message/receipt；stage 化持久化异常
#   code: _refusal_response/_idempotent_hit_response/_fresh_success_response
#   downstream: zephyr.frontend.dashboard.api_server POST /api/schedulegate-confirm（待接线）
# 边: I1 --> A1 ; A1 --> O1 ; I1 --> A2 ; A2 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import logging
import os
import re
import threading
import uuid
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Iterator, Mapping

from zephyr.ai_layer.scheduling.scheduling_events import (
    KIND_ORDER_CONFIRMED_DUE,
    SchedulingJournal,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "CONFIRMABLE_STATE",
    "DECISION_CONFIRM",
    "DECISION_REJECT",
    "DECISION_VOCABULARY",
    "ConfirmGate",
    "ConfirmPersistError",
    "ConfirmDecisionRecord",
    "OrderFileStore",
    "OrdersRowLossError",
    "evaluate_confirm",
    "gate_lock_for",
]

DECISION_CONFIRM: Final = "confirm"
DECISION_REJECT: Final = "reject"
DECISION_VOCABULARY: Final = frozenset({DECISION_CONFIRM, DECISION_REJECT})
CONFIRMABLE_STATE: Final = "pending"  # §2.7：仅 pending 可拍板；dead=作废归档终态

DEFAULT_STATE_DIR: Final = REPO_ROOT / ".runtime" / "ai_scheduling"
DECISIONS_NAME: Final = "confirm_decisions.jsonl"
ORDERS_NAME: Final = "orders.jsonl"
RECEIPT_ID_PREFIX: Final = "CFM"

# 雷 1/2/3 加固新增的三个落点件（同属 .runtime/ai_scheduling/ 域，非 .runtime 根直写）
INTENTS_DIR_NAME: Final = "confirm_intents"
QUARANTINE_NAME: Final = "orders_quarantine.jsonl"
GATE_LOCK_SUFFIX: Final = ".gate.lock"
SNAPSHOT_RECEIPT_FIELD: Final = "owner_receipt_id"

LANDING_STAGES: Final = ("intent", "journal", "decisions", "orders")


def _aware(moment: datetime) -> datetime:
    """tz 守卫：naive datetime 拒收（RULE-SCHEMA-TZ）。"""
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）")
    return moment


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ConfirmPersistError(RuntimeError):
    """落点写失败=半写（雷 2）：上抛并留意图账凭据，绝不返回"已持久化"。

    :param stage: 失败发生在哪条腿 ∈ ``LANDING_STAGES``（intent/journal/decisions/orders）
    :param receipt_id: 本次已定形的回执号（自愈后复用同一枚，故调用方可据此对账）
    """

    def __init__(
        self,
        message: str,
        *,
        stage: str,
        order_id: str = "",
        receipt_id: str = "",
        detail: str = "",
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.order_id = order_id
        self.receipt_id = receipt_id
        self.detail = detail


class OrdersRowLossError(RuntimeError):
    """快照重写将丢失/已丢失行（雷 3）：拒写或落盘后报红，历史绝不被静默销毁。"""

    def __init__(
        self,
        message: str,
        *,
        lost_ids: tuple[str, ...] = (),
        lost_lines: tuple[str, ...] = (),
        path: Path | str = "",
        stage: str = "",
    ) -> None:
        super().__init__(message)
        self.lost_ids = lost_ids
        self.lost_lines = lost_lines
        self.path = str(path)
        self.stage = stage


# ── 串化闸（雷 1 治本：一个临界区包住整个 decide）────────────────────────────
@contextlib.contextmanager
def _byte_lock(lock_path: Path) -> Iterator[None]:
    """跨进程 OS 字节排他锁（复刻仓内既有先例 ``gov_audit/writer.py``
    ``_cross_process_append_lock``；零用户态轮询，等待交给 OS）：

    - Windows: ``msvcrt.locking(LK_LOCK)`` 由 OS 每 1s 重试、约 10s 后 OSError
    - POSIX: ``fcntl.flock(LOCK_EX)`` 阻塞直至获取
    - 进程崩溃/被杀 → OS 关句柄自动释放，无 stale 锁；锁文件只创建永不删除（删=拆散互斥域）
    - 拿不到 = ``TimeoutError`` 上抛（fail-closed：丢一次请求好过双写重复派工）
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+b") as fh:
        try:
            fh.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl  # noqa: import-integrity  平台条件分支：fcntl 仅 Unix 存在，Windows 上不可解析属预期

                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        except OSError as exc:
            raise TimeoutError(f"confirm_gate 串化闸未获取：{lock_path}") from exc
        try:
            yield
        finally:
            try:
                fh.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl  # noqa: import-integrity  平台条件分支：fcntl 仅 Unix 存在

                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass


class _DirGateLock:
    """同一 ``state_dir`` 的双层闸：进程内 ``RLock``（同线程可重入）＋跨进程字节锁。

    为什么要两层：msvcrt 的字节锁语义在"同进程多线程各自 open 的 fd"上不作保证，故线程
    互斥交给 RLock；跨进程互斥交给 OS 字节锁。同线程重入只加深度、**不重复抢字节锁**
    （Windows 上对同档二次 LockFile 会自死锁）——decide 持闸期间会再调 ``upsert``，
    正是这条重入路径。
    """

    def __init__(self, state_dir: Path) -> None:
        self._dir = Path(state_dir)
        self._mutex = threading.RLock()
        self._depth = threading.local()

    @contextlib.contextmanager
    def __call__(self) -> Iterator[None]:
        depth = int(getattr(self._depth, "n", 0))
        self._mutex.acquire()
        self._depth.n = depth + 1
        try:
            if depth:
                yield
            else:
                with _byte_lock(self._dir / (ORDERS_NAME + GATE_LOCK_SUFFIX)):
                    yield
        finally:
            self._depth.n = depth
            self._mutex.release()


_GATE_LOCKS: dict[str, _DirGateLock] = {}
_GATE_LOCKS_GUARD: Final = threading.Lock()


def gate_lock_for(state_dir: Path | str) -> _DirGateLock:
    """按 state_dir 取（并缓存）串化闸。键=解析后绝对路径 ⇒ 同一目录的多个
    ``ConfirmGate``/``OrderFileStore`` 实例共享一个互斥域；缓存规模=进程内不同 state_dir 数
    （生产恒 1）。"""
    resolved = str(Path(state_dir).resolve())
    with _GATE_LOCKS_GUARD:
        lock = _GATE_LOCKS.get(resolved)
        if lock is None:
            lock = _DirGateLock(Path(state_dir))
            _GATE_LOCKS[resolved] = lock
        return lock


def _history_verdict(
    decision: str,
    history: list[Mapping[str, Any]],
    *,
    allow_amend: bool,
) -> dict[str, Any]:
    """有史可查时的判定族（evaluate_confirm 尾段）：幂等命中 / 同判冲突拒 / 改判放行 / 新判。"""
    last = history[-1] if history else None
    if last is not None and str(last.get("outcome") or "") == "decided":
        if str(last.get("decision") or "") == decision:
            return {
                "ok": True,
                "kind": "idempotent_hit",  # 幂等：同判再请求=返回原回执，零新事件零重写
                "codes": [],
                "prior": last,
            }
        if not allow_amend:
            return {
                "ok": False,
                "kind": "rejected_request",
                "codes": [f"decision_conflict:已有 {last.get('decision')} 判（改判需 allow_amend=True 留痕）"],
                "prior": last,
            }
        return {"ok": True, "kind": "amend", "codes": [], "prior": last}  # 改判走新行，旧行不删
    return {"ok": True, "kind": "decided", "codes": [], "prior": last}


# ── 纯函数判定（零 IO 零取时，全枚举可测）───────────────────────────────────
def evaluate_confirm(
    order: Mapping[str, Any] | None,
    decision: str,
    history: list[Mapping[str, Any]],
    *,
    allow_amend: bool = False,
) -> dict[str, Any]:
    """纯函数：确认请求判定。返回 {ok, codes, kind, prior}——kind ∈
    {'decided','idempotent_hit','amend','rejected_request','invalid_request'}。

    :param order: 工单快照 dict（None=查无此单）
    :param decision: 'confirm' | 'reject'（词表外=invalid_request）
    :param history: 该单既有决策记录（时间序，末条=最近判）
    :param allow_amend: True 时相反决策走改判留痕路径（旧行永不删除）

    签名与口径一字未动（红队加固在编排层，不污染纯函数面）：``idempotent_hit`` 的
    "快照须真带该回执"半写校验属 IO 对账，由 :meth:`ConfirmGate.decide` 负责（雷 2）。
    """
    if decision not in DECISION_VOCABULARY:
        return {
            "ok": False,
            "kind": "invalid_request",
            "codes": [f"decision_not_vocab:{decision!r}"],
            "prior": None,
        }
    if order is None:
        return {
            "ok": False,
            "kind": "rejected_request",
            "codes": ["order_not_found"],
            "prior": history[-1] if history else None,
        }
    if not bool(order.get("owner_gate")):
        return {
            "ok": False,
            "kind": "rejected_request",
            "codes": ["not_skeleton_level（owner_gate 非真：模块级工单走自动派，不进 Owner 门）"],
            "prior": history[-1] if history else None,
        }
    if str(order.get("state") or "") != CONFIRMABLE_STATE:
        return {
            "ok": False,
            "kind": "rejected_request",
            "codes": [f"state_not_confirmable:{order.get('state')}（§2.7 仅 pending 可拍板）"],
            "prior": history[-1] if history else None,
        }
    return _history_verdict(decision, history, allow_amend=allow_amend)


@dataclass(frozen=True)
class ConfirmDecisionRecord:
    """决策账一行（append-only；拒绝请求同样成行，outcome 区分）。"""

    order_id: str
    decision: str
    outcome: str  # decided / rejected_request
    receipt_id: str = ""
    decided_at: str = ""
    reason: str = ""
    actor: str = ""
    state_before: str = ""
    state_after: str = ""
    amend: bool = False
    codes: list[str] = None  # type: ignore[assignment]

    def to_payload(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "decision": self.decision,
            "outcome": self.outcome,
            "receipt_id": self.receipt_id,
            "decided_at": self.decided_at,
            "reason": self.reason,
            "actor": self.actor,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "amend": self.amend,
            "codes": list(self.codes or []),
        }


def _parse_row(stripped: str) -> dict[str, Any] | None:
    """一行 → dict（非 dict/解析失败=None，原文由调用方负责保留）。"""
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return raw if isinstance(raw, dict) else None


# ── 回执/拒绝回包构造（decide 各分支族的纯形状面，零分支零 IO）───────────────
def _missing_order_id_response() -> dict[str, Any]:
    """缺 order_id 的拒绝回包（decide 门卫分支）。"""
    return {
        "ok": False,
        "error": "missing_order_id",
        "message": "确认请求缺 order_id，未生效",
    }


def _rejection_record(
    order_id: str,
    decision: str,
    reason: str,
    actor: str,
    decided_at: str,
    order: Mapping[str, Any] | None,
    verdict: Mapping[str, Any],
) -> ConfirmDecisionRecord:
    """被拒请求的决策账行（拒绝请求同样落审计——decide 拒绝分支用）。"""
    return ConfirmDecisionRecord(
        order_id=order_id,
        decision=str(decision or ""),
        outcome="rejected_request",
        decided_at=decided_at,
        reason=str(reason or ""),
        actor=str(actor or ""),
        state_before=str((order or {}).get("state") or ""),
        codes=list(verdict["codes"]),
    )


def _refusal_response(verdict: Mapping[str, Any]) -> dict[str, Any]:
    """拍板被拒的前端契约回包（codes 可回传）。"""
    joined = "；".join(verdict["codes"])
    return {
        "ok": False,
        "error": f"schedulegate_confirm_refused: {joined}",
        "codes": verdict["codes"],
        "message": f"拍板被拒：{joined}",
    }


def _idempotent_hit_response(
    verdict: Mapping[str, Any],
    order: Mapping[str, Any] | None,
    order_id: str,
) -> dict[str, Any]:
    """幂等命中回包（零新事件零重写）；快照缺该回执=半写被当幂等命中（雷 2 第二副面孔），报红。"""
    prior = dict(verdict["prior"] or {})
    prior_receipt = str(prior.get("receipt_id") or "")
    if not ConfirmGate._snapshot_has_receipt(order, prior_receipt):
        # 决策账已 decided 而快照没更＝半写被当成幂等命中（雷 2 的第二副面孔，
        # 案卷 §四.2 点名）——意图账自愈没兜住就是真事故，报红绝不回 ok。
        raise ConfirmPersistError(
            f"persist_failed:orders order={order_id} receipt={prior_receipt or '?'}"
            "（决策账有 decided 行而快照缺该回执，禁判幂等命中）",
            stage="orders",
            order_id=order_id,
            receipt_id=prior_receipt,
            detail="idempotent_hit_without_snapshot_receipt",
        )
    return {
        "ok": True,
        "idempotent": True,
        "message": f"已拍板（幂等命中，不重复记账）：{prior.get('decision')}",
        "receipt": {
            "order_id": order_id,
            "decision": prior.get("decision"),
            "receipt_id": prior_receipt,
            "decided_at": prior.get("decided_at"),
            "state_after": prior.get("state_after"),
        },
    }


def _fresh_success_response(
    order_id: str,
    decision: str,
    receipt_id: str,
    decided_at: str,
    merged: Mapping[str, Any],
    amend: bool,
) -> dict[str, Any]:
    """新决策落地成功的前端契约回包（confirm=待派 / reject=作废归档）。"""
    return {
        "ok": True,
        "idempotent": False,
        "amend": amend,
        "message": (
            "已确认：工单待派（仍须过 T1 双预检+E0 问闸）"
            if decision == DECISION_CONFIRM
            else "已驳回：工单作废归档（审计链留痕不删）"
        ),
        "order_id": order_id,
        "state_after": str(merged.get("state") or CONFIRMABLE_STATE),
        "receipt": {
            "order_id": order_id,
            "decision": decision,
            "receipt_id": receipt_id,
            "decided_at": decided_at,
            "state_after": str(merged.get("state") or CONFIRMABLE_STATE),
        },
    }


# ── 工单快照文件仓（雷 3 治本：零行丢失 + 留痕）─────────────────────────────
class OrderFileStore:
    """工单快照文件仓（orders.jsonl，一行一单；**按行外科式改写，永不整档重建**）。

    生产真源目标=PG ``ai_scheduling.ai_work_order``（C2 DDL 已在册）；本文件仓为已建守护链路
    （api 投影/确认落点）提供同形态快照落点，PG sink 接线属 order_daemon 后续工单（如实在册）。
    文件快照究竟是过渡落点还是长期真源**未裁**（接线前置第三件，见车道记录册 §二处置 2）。

    红队 §四.3/.4 两条实测缺陷的封堵口径：

    * **畸形行不得被销毁**：``load_orders`` 仍给"可解析 dict 行"（读端语义零变，
      ``search_orders`` 等消费方无感），但同时把不可解析/非 dict 行原文记进
      ``malformed_lines``，另落 ``orders_quarantine.jsonl`` 留痕＋``log.error`` 出声；
      ``upsert`` 的写路径把这些行**按原文逐行回写** ⇒ 盘上行集只增不减。
    * **并发不丢单**：读-改-写全程持串化闸（与 :class:`ConfirmGate` 同闸），tmp 文件名
      带 pid+uuid 唯一（原固定 ``orders.jsonl.tmp`` 多线程共用＝丢单＋Windows
      ``os.replace`` PermissionError 根因），落盘前 ``flush+fsync``。
    * **零行丢失可证明**：写前用行集指纹（order_id 多重集＋不可寻址行原文多重集）比对
      计划内容与盘上原内容，落盘后再复读复验；丢失集非空 → :exc:`OrdersRowLossError`
      （写前=拒写，写后=报红）。
    """

    def __init__(self, state_dir: Path | str | None = None) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self.orders_path: Final = self.state_dir / ORDERS_NAME
        self.quarantine_path: Final = self.state_dir / QUARANTINE_NAME
        self.skipped_lines = 0  # 畸形行计数（读端兼容旧契约；语义已从"跳过即丢弃"改"保留＋留痕"）
        self.malformed_lines: list[tuple[int, str]] = []  # (行号, 原文)

    # ── 原样读（雷 3 的读侧真源：一行不丢）────────────────────────────────
    def read_raw_lines(self) -> list[str]:
        """物理行原文（含畸形行；空文件=[]）。"""
        if not self.orders_path.exists():
            return []
        return self.orders_path.read_text(encoding="utf-8").splitlines()

    @staticmethod
    def _census(lines: list[str]) -> tuple[Counter[str], Counter[str]]:
        """行集指纹：(可寻址 order_id 计数, 不可寻址行原文计数)。"""
        ids: Counter[str] = Counter()
        opaque: Counter[str] = Counter()
        for raw in lines:
            stripped = raw.strip()
            if not stripped:
                continue
            rec = _parse_row(stripped)
            if rec is not None and str(rec.get("order_id") or ""):
                ids[str(rec["order_id"])] += 1
            else:
                opaque[stripped] += 1
        return ids, opaque

    def _note_malformed(self, lines: list[str]) -> None:
        """畸形/非 dict 行：记 ``malformed_lines``＋quarantine 留痕＋出声（禁静默）。"""
        found = [(i + 1, raw) for i, raw in enumerate(lines) if raw.strip() and _parse_row(raw.strip()) is None]
        self.malformed_lines = found
        self.skipped_lines = len(found)
        if not found:
            return
        log.error(
            "orders.jsonl 畸形/非 dict 行 %s 条（原文保留＋quarantine 留痕，绝不随重写销毁）：%s",
            len(found),
            [ln for ln, _ in found],
        )
        self._record_quarantine([{"reason": "malformed_line", "line_no": ln, "raw": txt} for ln, txt in found])

    def _record_quarantine(self, entries: list[dict[str, Any]]) -> None:
        """畸形/重复行留痕（append-only，按原文 sha 去重 ⇒ 幂等不膨胀）。"""
        if not entries:
            return
        known: set[str] = set()
        if self.quarantine_path.exists():
            for line in self.quarantine_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    rec = json.loads(stripped)
                except json.JSONDecodeError:
                    continue
                if isinstance(rec, dict):
                    known.add(str(rec.get("raw_sha256") or ""))
        fresh: list[dict[str, Any]] = []
        for entry in entries:
            raw = str(entry.get("raw") or "")
            sha = _sha(raw)
            if sha in known:
                continue
            known.add(sha)
            fresh.append({"recorded_at": now_utc().isoformat(), "raw_sha256": sha, **entry})
        if not fresh:
            return
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.quarantine_path.open("a", encoding="utf-8", newline="\n") as handle:
            for rec in fresh:
                handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def load_orders(self) -> list[dict[str, Any]]:
        """可解析 dict 行（读端契约与修前一致）；副产 ``malformed_lines``＋留痕＋出声。"""
        lines = self.read_raw_lines()
        self._note_malformed(lines)
        out: list[dict[str, Any]] = []
        for line in lines:
            rec = _parse_row(line.strip())
            if rec is not None:
                out.append(rec)
        return out

    def get(self, order_id: str) -> dict[str, Any] | None:
        for order in self.load_orders():
            if str(order.get("order_id") or "") == order_id:
                return order
        return None

    def _assert_no_loss(
        self,
        before: tuple[Counter[str], Counter[str]],
        after: tuple[Counter[str], Counter[str]],
        *,
        path: Path,
        stage: str,
    ) -> None:
        """零行丢失证明：before ⊆ after（按多重集），任何 order_id 行或原文行消失即报红。"""
        lost_ids = tuple((before[0] - after[0]).elements())
        lost_lines = tuple((before[1] - after[1]).elements())
        if lost_ids or lost_lines:
            raise OrdersRowLossError(
                f"orders.jsonl 重写将丢失 {len(lost_ids)} 个单行 / {len(lost_lines)} 条原文行"
                f"（雷 3 口径：历史不得被静默销毁）stage={stage} lost_ids={list(lost_ids)}"
                f" lost_lines={len(lost_lines)}",
                lost_ids=lost_ids,
                lost_lines=lost_lines,
                path=path,
                stage=stage,
            )

    def _atomic_write(self, lines: list[str]) -> None:
        """唯一 tmp 名 + fsync + os.replace（治 §四.3 固定 tmp 名共用＝丢单/撞句柄）。"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.orders_path.with_name(f"{self.orders_path.name}.{os.getpid()}-{uuid.uuid4().hex}.tmp")
        try:
            with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
                handle.write("".join(line + "\n" for line in lines))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, self.orders_path)
        except BaseException:
            with contextlib.suppress(OSError):
                tmp.unlink(missing_ok=True)
            raise

    def upsert(self, order: Mapping[str, Any]) -> None:
        """按 order_id **原地替换该行**（无此单才尾部追加）；audit_log 追加由调用方保证只前缀追加。

        雷 3 的关键取舍：其余物理行（含畸形行）**原文回写**，函数内不存在
        "由解析结果重建整档"这一步 ⇒ 任何一次无关 upsert 都不可能再抹掉损坏行。
        """
        order_id = str(order.get("order_id") or "")
        if not order_id:
            raise ValueError("order_missing_order_id（upsert 拒收无主单）")
        with gate_lock_for(self.state_dir)():
            lines = self.read_raw_lines()
            self._note_malformed(lines)
            before = self._census(lines)
            hits = [
                i
                for i, raw in enumerate(lines)
                if (rec := _parse_row(raw.strip())) and str(rec.get("order_id") or "") == order_id
            ]
            planned = list(lines)
            if hits:
                planned[hits[0]] = json.dumps(dict(order), ensure_ascii=False)
                if len(hits) > 1:
                    log.error(
                        "orders.jsonl 同 order_id=%s 出现 %s 行（只替换首行、余行原样保留＝不合档不销毁）",
                        order_id,
                        len(hits),
                    )
                    self._record_quarantine(
                        [
                            {
                                "reason": "duplicate_order_id_rows",
                                "order_id": order_id,
                                "row_count": len(hits),
                                "line_no": hits[1] + 1,
                                "raw": lines[hits[1]],
                            }
                        ]
                    )
            else:
                planned.append(json.dumps(dict(order), ensure_ascii=False))
            self._assert_no_loss(before, self._census(planned), path=self.orders_path, stage="planned")
            self._atomic_write(planned)
            self._assert_no_loss(
                before,
                self._census(self.read_raw_lines()),
                path=self.orders_path,
                stage="committed",
            )


# ── 门（雷 1/2 治本：串化临界区 + 写前意图账 + 落点实读复验）─────────────────
class ConfirmGate:
    """骨架级一键确认的门面：判定→三落点（事件账+决策账+工单快照）→前端契约回执。

    并发口径：``decide`` 整段持 :func:`gate_lock_for` 闸（跨进程＋跨线程），读→判→三写
    之间不得有第二个同目录写者；闸内**零重试**，故并发同请求的第 2..N 次必然读到已落定的
    decided 行 ⇒ 幂等命中返回原回执。快照与 ``state_dir`` 不同目录的 store/journal 注入
    属误配（闸只锁本目录），构造时如实报一条 WARNING。
    """

    def __init__(
        self,
        state_dir: Path | str | None = None,
        *,
        journal: SchedulingJournal | None = None,
        store: OrderFileStore | None = None,
    ) -> None:
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self._store: Final = store or OrderFileStore(self.state_dir)
        self._journal: Final = journal or SchedulingJournal(state_dir=self.state_dir)
        self.decisions_path: Final = self.state_dir / DECISIONS_NAME
        self.intents_dir: Final = self.state_dir / INTENTS_DIR_NAME
        for label, other in (("store", self._store.state_dir), ("journal", self._journal.state_dir)):
            if Path(other).resolve() != self.state_dir.resolve():
                log.warning(
                    "confirm_gate 串化闸只覆盖 state_dir=%s，注入的 %s 指向另一目录=%s"
                    "（闸不覆盖它＝误配，请按同一目录注入）",
                    self.state_dir,
                    label,
                    other,
                )

    # ── 决策账读写 ─────────────────────────────────────────────────────────
    def history(self, order_id: str) -> list[dict[str, Any]]:
        """该单全部决策行（时间序；畸形行原样留在盘上、只跳过读取并报红留痕）。"""
        if not self.decisions_path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line_no, line in enumerate(self.decisions_path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                raw = json.loads(stripped)
            except json.JSONDecodeError:
                log.error("confirm_decisions.jsonl 第 %s 行畸形（原文保留于盘上不删）", line_no)
                continue
            if isinstance(raw, dict) and str(raw.get("order_id") or "") == order_id:
                out.append(raw)
        return out

    def _append(self, record: ConfirmDecisionRecord) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.decisions_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record.to_payload(), ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    # ── 意图账（写前凭据，雷 2 自愈依据）──────────────────────────────────
    def _intent_path(self, receipt_id: str, *, path: Path | None = None) -> Path:
        return path or self.intents_dir / f"{receipt_id}.json"

    def _write_intent(self, intent: dict[str, Any]) -> None:
        receipt_id = str(intent.get("receipt_id") or "")
        if not receipt_id:
            raise ConfirmPersistError(
                "intent_missing_receipt_id", stage="intent", order_id=str(intent.get("order_id") or "")
            )
        self.intents_dir.mkdir(parents=True, exist_ok=True)
        path = self._intent_path(receipt_id)
        try:
            with open(path, "x", encoding="utf-8", newline="\n") as handle:  # x=不覆盖既有意图账
                handle.write(json.dumps(intent, ensure_ascii=False, indent=1) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError as exc:
            raise ConfirmPersistError(
                f"intent_already_exists:{receipt_id}（同回执意图账已在盘，先 reconcile 再重放）",
                stage="intent",
                order_id=str(intent.get("order_id") or ""),
                receipt_id=receipt_id,
            ) from exc
        except OSError as exc:
            raise ConfirmPersistError(
                f"persist_failed:intent order={intent.get('order_id')}（意图账写不下＝不落任何落点）",
                stage="intent",
                order_id=str(intent.get("order_id") or ""),
                receipt_id=receipt_id,
                detail=f"{type(exc).__name__}: {exc}"[:200],
            ) from exc

    def _iter_intents(self) -> list[tuple[Path, dict[str, Any]]]:
        if not self.intents_dir.exists():
            return []
        out: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(self.intents_dir.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                log.error("confirm_intents/%s 不可读（原样保留不删，需人工处置）：%s", path.name, exc)
                continue
            if isinstance(raw, dict):
                out.append((path, raw))
            else:
                log.error("confirm_intents/%s 非 dict（原样保留不删）", path.name)
        return out

    def _forget_intent(self, receipt_id: str, *, path: Path | None = None) -> None:
        """完成即删（重放幂等 ⇒ 删失败留下的 stale 意图账无害，下次自愈再删）。"""
        target = self._intent_path(receipt_id, path=path)
        try:
            target.unlink(missing_ok=True)
        except OSError as exc:
            log.warning("confirm_intents/%s 删除失败（stale 意图账下次自愈再删）：%s", target.name, exc)

    # ── 落点实读（写前判存 / 写后复验 / 自愈对账三用）─────────────────────
    def _journal_has_receipt(self, receipt_id: str) -> bool:
        if not receipt_id:
            return False
        try:
            events = self._journal.pending()
        except (
            OSError,
            ValueError,
        ) as exc:  # journal 半截行会让 pending() 的 json.loads 炸（属 scheduling_events 面，本件不改）
            log.error("journal pending() 失败，退回原文扫描：%s", exc)
            try:
                text = self._journal.journal_path.read_text(encoding="utf-8")
            except OSError:
                return False
            return re.search(r'"receipt_id":\s*"%s"' % re.escape(receipt_id), text) is not None
        return any(str(evt.payload.get("receipt_id") or "") == receipt_id for evt in events)

    def _decision_has_receipt(self, order_id: str, receipt_id: str) -> bool:
        if not receipt_id:
            return False
        return any(str(row.get("receipt_id") or "") == receipt_id for row in self.history(order_id))

    @staticmethod
    def _snapshot_has_receipt(order: Mapping[str, Any] | None, receipt_id: str) -> bool:
        return bool(receipt_id) and str((order or {}).get(SNAPSHOT_RECEIPT_FIELD) or "") == receipt_id

    @staticmethod
    def _decision_fields(intent: Mapping[str, Any], receipt_id: str, decided_at: str) -> dict[str, Any]:
        """意图账 → 须钉进快照的决策字段集（自愈与首写共用一处真源）。"""
        fields: dict[str, Any] = {
            "owner_decision": str(intent.get("decision") or ""),
            "owner_decided_at": decided_at,
            SNAPSHOT_RECEIPT_FIELD: receipt_id,
        }
        if str(intent.get("decision") or "") == DECISION_REJECT:
            fields["state"] = "dead"  # 作废归档（禁删行；复活仅 Owner 手递新单 §2.7）
            fields["held_reason"] = f"owner_rejected:{intent.get('reason') or '未注明'}"
        return fields

    @staticmethod
    def _with_audit(
        order: Mapping[str, Any], receipt_id: str, decided_at: str, intent: Mapping[str, Any]
    ) -> dict[str, Any]:
        audit = list(order.get("audit_log") or [])
        marker = f"receipt={receipt_id}"
        if not any(marker in str(entry.get("detail") or "") for entry in audit if isinstance(entry, Mapping)):
            decision = str(intent.get("decision") or "")
            audit.append(
                {
                    "ts": decided_at,
                    "action": f"owner_{decision}",
                    "detail": (
                        f"{marker} actor={intent.get('actor') or ''}"
                        + (f" reason={intent['reason']}" if intent.get("reason") else "")
                    ),
                }
            )
        merged = dict(order)
        merged["audit_log"] = audit
        return merged

    def _heal_intent_legs(
        self,
        intent: Mapping[str, Any],
        receipt_id: str,
        order_id: str,
        decided_at: str,
        landed: dict[str, bool],
    ) -> None:
        """三落点缺腿补齐（journal/decisions/orders，同一 receipt_id 同一 decided_at ⇒ 零重复）。"""
        if not self._journal_has_receipt(receipt_id):
            payload = dict(intent.get("event_payload") or {})
            payload["receipt_id"] = receipt_id
            payload["decided_at"] = decided_at
            kind = str(payload.pop("kind", "") or KIND_ORDER_CONFIRMED_DUE)
            try:
                self._journal.emit(kind, payload)
            except OSError as exc:
                raise ConfirmPersistError(
                    f"persist_failed:journal order={order_id} receipt={receipt_id}（自愈重放仍失败）",
                    stage="journal",
                    order_id=order_id,
                    receipt_id=receipt_id,
                    detail=f"{type(exc).__name__}: {exc}"[:200],
                ) from exc
            landed["journal"] = True
        if not self._decision_has_receipt(order_id, receipt_id):
            payload = dict(intent.get("decision_payload") or {})
            try:
                self._append(ConfirmDecisionRecord(**payload))
            except OSError as exc:
                raise ConfirmPersistError(
                    f"persist_failed:decisions order={order_id} receipt={receipt_id}（自愈重放仍失败）",
                    stage="decisions",
                    order_id=order_id,
                    receipt_id=receipt_id,
                    detail=f"{type(exc).__name__}: {exc}"[:200],
                ) from exc
            landed["decisions"] = True
        current = self._store.get(order_id)
        if current is None:
            raise ConfirmPersistError(
                f"persist_failed:orders order={order_id} receipt={receipt_id}（快照查无此单行，无法补齐半写）",
                stage="orders",
                order_id=order_id,
                receipt_id=receipt_id,
                detail="order_row_missing",
            )
        if not self._snapshot_has_receipt(current, receipt_id):
            merged = self._with_audit(
                {**current, **self._decision_fields(intent, receipt_id, decided_at)}, receipt_id, decided_at, intent
            )
            try:
                self._store.upsert(merged)
            except ConfirmPersistError:
                raise
            except Exception as exc:  # noqa: BLE001  -- 落点写失败一律转 persist_failed（绝不吞成成功）
                raise ConfirmPersistError(
                    f"persist_failed:orders order={order_id} receipt={receipt_id}（自愈重放仍失败）",
                    stage="orders",
                    order_id=order_id,
                    receipt_id=receipt_id,
                    detail=f"{type(exc).__name__}: {exc}"[:200],
                ) from exc
            landed["orders"] = True

    def _complete_intent(self, intent: Mapping[str, Any]) -> dict[str, bool]:
        """按落点实读补齐一条意图账的缺腿（同一 receipt_id 同一 decided_at ⇒ 零重复事件/决策行）。"""
        receipt_id = str(intent.get("receipt_id") or "")
        oid = str(intent.get("order_id") or "")
        decided_at = str(intent.get("decided_at") or "")
        landed = {"journal": False, "decisions": False, "orders": False}
        self._heal_intent_legs(intent, receipt_id, oid, decided_at, landed)
        missing = [stage for stage in LANDING_STAGES[1:] if not self._landing_present(oid, receipt_id, stage)]
        if missing:
            raise ConfirmPersistError(
                f"persist_failed:{','.join(missing)} order={oid} receipt={receipt_id}（补齐后实读仍缺，拒绝当成功）",
                stage=missing[0],
                order_id=oid,
                receipt_id=receipt_id,
                detail="post_recovery_verify",
            )
        return landed

    def _landing_present(self, order_id: str, receipt_id: str, stage: str) -> bool:
        if stage == "journal":
            return self._journal_has_receipt(receipt_id)
        if stage == "decisions":
            return self._decision_has_receipt(order_id, receipt_id)
        if stage == "orders":
            return self._snapshot_has_receipt(self._store.get(order_id), receipt_id)
        return False

    def _recover_locked(self, order_id: str | None) -> list[str]:
        """自愈：补齐（该单的）遗留意图账，返回已修好的 receipt_id 列表。必须在闸内调用。"""
        healed: list[str] = []
        for path, intent in self._iter_intents():
            oid = str(intent.get("order_id") or "")
            receipt_id = str(intent.get("receipt_id") or "")
            if not oid or not receipt_id:
                log.error("confirm_intents/%s 缺 order_id/receipt_id（原样保留不删）", path.name)
                continue
            if order_id is not None and oid != order_id:
                continue
            landed = self._complete_intent(intent)
            self._forget_intent(receipt_id, path=path)
            healed.append(receipt_id)
            log.warning(
                "confirm_gate 半写自愈：order=%s receipt=%s 本次补写腿=%s",
                oid,
                receipt_id,
                [k for k, v in landed.items() if v],
            )
        return healed

    def reconcile(self, order_id: str | None = None) -> dict[str, Any]:
        """自愈入口（供事件触发型 reconciler 挂，零定时器零轮询）。

        :param order_id: None=扫全部意图账；给定=只处理该单。
        """
        with gate_lock_for(self.state_dir)():
            outstanding = [p.name for p, _ in self._iter_intents() if order_id is None or str(order_id) == ""]
            healed = self._recover_locked(str(order_id) if order_id else None)
            left = [path.name for path, _ in self._iter_intents()]
        return {"checked": len(healed) + len(left), "healed": healed, "outstanding": left}

    def _decide_new(
        self,
        order_id: str,
        decision: str,
        reason: str,
        actor: str,
        moment: datetime,
        order: dict[str, Any],
        amend: bool,
    ) -> dict[str, Any]:
        """新决策路径：回执定形 → 写前意图账 → 三落点 → 实读复验 → 删意图账 → 回执。"""
        receipt_id = f"{RECEIPT_ID_PREFIX}-{moment.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        decided_at = moment.isoformat()
        state_before = str((order or {}).get("state") or "")
        assert order is not None  # evaluate_confirm 保证（ok=True 时 order 必在场）
        decision_payload = ConfirmDecisionRecord(
            order_id=order_id,
            decision=decision,
            outcome="decided",
            receipt_id=receipt_id,
            decided_at=decided_at,
            reason=str(reason or ""),
            actor=str(actor or ""),
            state_before=state_before,
            state_after=CONFIRMABLE_STATE if decision == DECISION_CONFIRM else "dead",
            amend=amend,
        ).to_payload()
        intent: dict[str, Any] = {
            "order_id": order_id,
            "decision": str(decision),
            "reason": str(reason or ""),
            "actor": str(actor or ""),
            "receipt_id": receipt_id,
            "decided_at": decided_at,
            "amend": amend,
            "state_before": state_before,
            "event_payload": {
                "kind": KIND_ORDER_CONFIRMED_DUE,
                "order_id": order_id,
                "decision": str(decision),
                "reason": str(reason or ""),
                "actor": str(actor or ""),
                "amend": amend,
            },
            "decision_payload": decision_payload,
            "written_at": now_utc().isoformat(),
        }
        # 三落点前先落**写前意图账**（雷 2 凭据）：此后任何一腿倒下，盘上都有
        # "这条回执未走完"的凭据，可复跑自愈；意图账自身写不下则一条落点都不写。
        self._write_intent(intent)

        def _stage(stage: str, action: Callable[[], None]) -> None:
            try:
                action()
            except ConfirmPersistError:
                raise
            except Exception as exc:  # noqa: BLE001  -- 落点写失败一律转 persist_failed 上抛（红队 §二.23 那条绕过被封）
                raise ConfirmPersistError(
                    f"persist_failed:{stage} order={order_id} receipt={receipt_id}"
                    "（半写：回执已定形、意图账留盘，可复跑自愈）",
                    stage=stage,
                    order_id=order_id,
                    receipt_id=receipt_id,
                    detail=f"{type(exc).__name__}: {exc}"[:200],
                ) from exc

        event_payload = dict(intent["event_payload"])
        kind = str(event_payload.pop("kind"))
        event_payload.update({"receipt_id": receipt_id, "decided_at": decided_at})
        _stage("journal", lambda: self._journal.emit(kind, event_payload))
        _stage("decisions", lambda: self._append(ConfirmDecisionRecord(**decision_payload)))
        merged = self._with_audit(
            {**order, **self._decision_fields(intent, receipt_id, decided_at)}, receipt_id, decided_at, intent
        )
        _stage("orders", lambda: self._store.upsert(merged))
        missing = [stage for stage in LANDING_STAGES[1:] if not self._landing_present(order_id, receipt_id, stage)]
        if missing:
            raise ConfirmPersistError(
                f"persist_failed:{','.join(missing)} order={order_id} receipt={receipt_id}"
                "（写后实读仍缺腿，绝不报已持久化；意图账留盘待自愈）",
                stage=missing[0],
                order_id=order_id,
                receipt_id=receipt_id,
                detail="post_write_verify",
            )
        self._forget_intent(receipt_id)
        return _fresh_success_response(order_id, decision, receipt_id, decided_at, merged, amend)

    # ── 主入口 ────────────────────────────────────────────────────────────
    def decide(
        self,
        order_id: str,
        decision: str,
        *,
        reason: str = "",
        actor: str = "schedulegate_ui",
        allow_amend: bool = False,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """确认/驳回一次拍板。返回前端契约形状 {ok, message, receipt?, error?}。

        幂等（雷 1 修后）：**并发**与顺序同义——同单同判再请求→ok:true + idempotent:true +
        原 receipt_id（零新事件零重写），依据=闸内读到的已落定 decided 行＋快照回执对账。
        改判：相反 decision 仅当 allow_amend=True 放行——新行 append，旧行永留。
        半写（雷 2 修后）：任一条落点写失败→上抛 :exc:`ConfirmPersistError`（带 stage），
        意图账留盘；下次对同单调用或直调 :meth:`reconcile` 先自愈（同一回执补齐）。

        **鉴权未接（如实）**：``actor``/``allow_amend`` 仍由调用方给，本件零鉴权；
        接线前须由 api 侧接会话鉴权真源，判据见
        ``wiring_C_confirm_hardening.md`` §二处置 1（本车道刻意不造假鉴权函数）。
        """
        oid = str(order_id or "").strip()
        if not oid:
            return _missing_order_id_response()
        moment = _aware(now or now_utc())
        with gate_lock_for(self.state_dir)():
            healed = self._recover_locked(oid)
            order = self._store.get(oid)
            verdict = evaluate_confirm(order, str(decision or ""), self.history(oid), allow_amend=allow_amend)

            if not verdict["ok"]:
                self._append(_rejection_record(oid, decision, reason, actor, moment.isoformat(), order, verdict))
                return _refusal_response(verdict)

            if verdict["kind"] == "idempotent_hit":
                result = _idempotent_hit_response(verdict, order, oid)
            else:
                result = self._decide_new(oid, decision, reason, actor, moment, order, verdict["kind"] == "amend")
            if healed:
                result["repaired"] = True
                result["repaired_receipts"] = healed
            return result

    def decide_from_payload(self, payload: Mapping[str, Any] | None) -> dict[str, Any]:
        """api 直通口：body {order_id, decision, reason?, allow_amend?} → 回执形状。

        待接线一行（api_server 属禁触热件，本车道不改）：
            return ConfirmGate().decide_from_payload(payload)

        **接线前置三件（未齐不得接，见头注 [CONSUMERS] 与车道记录册 §二）**：
        ①会话鉴权真源——``actor``/``allow_amend`` 不得取自 body（现零鉴权＝谁都能自称
        改判、伪造审计主体，案卷 §三.5 实测 actor=['zhangsan','lisi','wangwu']）；
        本车道**刻意未造**假鉴权函数充数，此项由接线方接真源；
        ②并发串化——已具备（雷 1 闸）；③OrderFileStore 归档语义确认——未裁。
        """
        body = dict(payload or {})
        return self.decide(
            str(body.get("order_id") or ""),
            str(body.get("decision") or ""),
            reason=str(body.get("reason") or ""),
            actor=str(body.get("actor") or "schedulegate_ui"),
            allow_amend=bool(body.get("allow_amend")),
        )
