# [BLUEPRINT] MOD-INF-049 | docs/03_modules/MOD-INF-049/
# [MODULE] zephyr.intelligence.venra_double_lock_anchor
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（纯标准库）
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 关键状态变更必须两名不同操作者双锁确认才生效；锚定记录只追加不修改；哈希链可离线校验
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VenraDoubleLockError(ZA-IT-0009)——空字段/重复提案/同人双锁/未知变更/终态后操作
# [TESTS] tests/intelligence/test_venra_double_lock_anchor.py
# [A_module] module_id=MOD-INF-049 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VENRA 双锁锚定器（MOD-INF-049）。

蓝图核查结论（2026-08-23）：docs/03_modules/ 全库无 venra/double_lock 专设蓝图，
depgraph 仅存设计态节点（MOD-INF-049 → 本文件）。按派单最小语义施工：
**关键状态变更双锁确认 + 锚定留痕**。

- 双锁确认：提案（propose）后须两名不同操作者依次 lock 才 confirmed；
  任一操作者 approve=False 即 rejected；终态后禁止再操作（fail-closed）。
- 锚定留痕：每次终态裁定追加一条 AnchorRecord，prev_hash 串成 sha256 哈希链，
  verify_chain() 可检测事后篡改。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: venra_double_lock_anchor.py
# 层: 算法
# - id: A1
#   name_zh: ① VenraDoubleLockAnchor
#   name_en: VenraDoubleLockAnchor
#   intro: 关键状态变更双锁确认 + 锚定留痕。
#   desc: 关键状态变更双锁确认 + 锚定留痕。；公共方法（定义序）: propose, lock, is_confirmed, anchor_chain, verify_chain；源码 L125-L214
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: VenraDoubleLockAnchor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Final

__all__: Final = [
    "AnchorRecord",
    "StateChange",
    "VenraDoubleLockAnchor",
    "VenraDoubleLockError",
]

_GENESIS_HASH: Final[str] = "0" * 64


class VenraDoubleLockError(Exception):
    """ZA-IT-0009: VENRA 双锁锚定操作非法。"""

    error_code = "ZA-IT-0009"


@dataclass(frozen=True)
class StateChange:
    """一次关键状态变更提案。"""

    change_id: str
    target: str
    payload_hash: str
    proposer: str


@dataclass(frozen=True)
class AnchorRecord:
    """锚定留痕记录（只追加，prev_hash 链式防篡改）。"""

    seq: int
    change_id: str
    target: str
    lockers: tuple[str, ...]
    decision: str  # "confirmed" | "rejected"
    prev_hash: str
    record_hash: str


def _hash_payload(payload: object) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _record_hash(seq: int, change_id: str, target: str, lockers: tuple[str, ...], decision: str, prev_hash: str) -> str:
    blob = json.dumps(
        {
            "seq": seq,
            "change_id": change_id,
            "target": target,
            "lockers": list(lockers),
            "decision": decision,
            "prev_hash": prev_hash,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class VenraDoubleLockAnchor:
    """关键状态变更双锁确认 + 锚定留痕。"""

    def __init__(self) -> None:
        self._changes: dict[str, StateChange] = {}
        self._locks: dict[str, list[str]] = {}
        self._terminal: dict[str, str] = {}
        self._records: list[AnchorRecord] = []

    # ── 提案 ─────────────────────────────────────────────────────────

    def propose(self, change_id: str, *, target: str, payload: object, proposer: str) -> StateChange:
        """登记一次关键状态变更提案。空字段/重复 change_id → VenraDoubleLockError。"""
        if not change_id or not target or not proposer:
            raise VenraDoubleLockError("change_id/target/proposer 均不得为空")
        if change_id in self._changes:
            raise VenraDoubleLockError(f"变更 {change_id!r} 已提案（禁止重复登记）")
        change = StateChange(
            change_id=change_id,
            target=target,
            payload_hash=_hash_payload(payload),
            proposer=proposer,
        )
        self._changes[change_id] = change
        self._locks[change_id] = []
        return change

    # ── 双锁 ─────────────────────────────────────────────────────────

    def lock(self, change_id: str, *, actor: str, approve: bool = True) -> str:
        """对变更加锁。两名不同 actor 均 approve 才 confirmed；任一 approve=False 即 rejected。"""
        if change_id not in self._changes:
            raise VenraDoubleLockError(f"未知变更 {change_id!r}（先 propose 再 lock）")
        if change_id in self._terminal:
            raise VenraDoubleLockError(f"变更 {change_id!r} 已终态（{self._terminal[change_id]}），禁止再操作")
        if not actor:
            raise VenraDoubleLockError("actor 不得为空")
        lockers = self._locks[change_id]
        if actor in lockers:
            raise VenraDoubleLockError("双锁必须两名不同操作者（同人重复加锁被拒绝）")

        if not approve:
            lockers.append(actor)
            return self._finalize(change_id, "rejected")

        lockers.append(actor)
        if len(lockers) >= 2:
            return self._finalize(change_id, "confirmed")
        return "pending"

    def is_confirmed(self, change_id: str) -> bool:
        return self._terminal.get(change_id) == "confirmed"

    # ── 锚定链 ───────────────────────────────────────────────────────

    def anchor_chain(self) -> list[AnchorRecord]:
        return list(self._records)

    def verify_chain(self) -> bool:
        """离线校验哈希链完整性（任一记录被篡改即 False）。"""
        prev = _GENESIS_HASH
        for rec in self._records:
            if rec.prev_hash != prev:
                return False
            if rec.record_hash != _record_hash(
                rec.seq, rec.change_id, rec.target, rec.lockers, rec.decision, rec.prev_hash
            ):
                return False
            prev = rec.record_hash
        return True

    # ── 内部 ─────────────────────────────────────────────────────────

    def _finalize(self, change_id: str, decision: str) -> str:
        change = self._changes[change_id]
        prev_hash = self._records[-1].record_hash if self._records else _GENESIS_HASH
        seq = len(self._records) + 1
        lockers = tuple(self._locks[change_id])
        rec = AnchorRecord(
            seq=seq,
            change_id=change_id,
            target=change.target,
            lockers=lockers,
            decision=decision,
            prev_hash=prev_hash,
            record_hash=_record_hash(seq, change_id, change.target, lockers, decision, prev_hash),
        )
        self._records.append(rec)
        self._terminal[change_id] = decision
        return decision
