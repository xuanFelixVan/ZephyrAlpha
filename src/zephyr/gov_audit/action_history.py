# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.gov_audit.action_history
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_action_history | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ActionHistory — 操作历史持久化审计 + 去重 + 循环检测
=====================================================
蓝图 §2.5 · 环形缓冲区(50条) + 5级去重规则 + action_ttl=300s

去重规则
--------
  identical_3x  -> WARN  + 写入 loop_events
  identical_5x  -> BLOCK + 拒绝执行
  no_effect_3x  -> WARN  + 检测无效果动作链
  spiral_5x     -> HALT  + 系统介入（自修复螺旋）
  semantic_10x  -> KILL_SWITCH（疑似 runaway agent）
"""

from __future__ import annotations

import hashlib
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class DedupAction(Enum):
    ALLOW = auto()
    WARN = auto()
    BLOCK = auto()
    HALT = auto()
    TRIGGER_KILL_SWITCH = auto()


@dataclass
class ActionSignature:
    tool_name: str
    tool_params_hash: str
    tool_params_semantic_hash: str = ""
    output_effect_hash: str = ""
    timestamp: float = field(default_factory=time.time)
    cost_incurred: float = 0.0

    @property
    def fingerprint(self) -> str:
        raw = f"{self.tool_name}:{self.tool_params_hash}:{self.tool_params_semantic_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class DedupResult:
    action: DedupAction
    reason: str = ""
    identical_count: int = 0
    fingerprint: str = ""


@dataclass
class LoopEvent:
    fingerprint: str
    tool_name: str
    count: int
    action: DedupAction
    reason: str
    timestamp: float = field(default_factory=time.time)


_RING_BUFFER_SIZE = 50
_ACTION_TTL = 300.0
_IDENTICAL_WARN_THRESHOLD = 3
_IDENTICAL_BLOCK_THRESHOLD = 5
_NO_EFFECT_THRESHOLD = 3
_SPIRAL_THRESHOLD = 5
_SEMANTIC_KILL_THRESHOLD = 10


class ActionHistory:
    def __init__(self, buffer_size: int = _RING_BUFFER_SIZE, ttl: float = _ACTION_TTL) -> None:
        self._buffer: deque[ActionSignature] = deque(maxlen=buffer_size)
        self._loop_events: list[LoopEvent] = []
        self._lock = threading.Lock()
        self._ttl = ttl
        self._file_region_counts: dict[str, int] = {}

    def record(
        self,
        tool_name: str,
        tool_params: str = "",
        tool_params_semantic: str = "",
        output_effect: str = "",
        cost: float = 0.0,
        target_file_region: str = "",
    ) -> DedupResult:
        params_hash = hashlib.sha256(tool_params.encode("utf-8")).hexdigest() if tool_params else ""
        semantic_hash = hashlib.sha256(tool_params_semantic.encode("utf-8")).hexdigest() if tool_params_semantic else ""
        effect_hash = hashlib.sha256(output_effect.encode("utf-8")).hexdigest() if output_effect else ""

        sig = ActionSignature(
            tool_name=tool_name,
            tool_params_hash=params_hash,
            tool_params_semantic_hash=semantic_hash,
            output_effect_hash=effect_hash,
            cost_incurred=cost,
        )

        with self._lock:
            self._purge_expired()
            result = self._check_dedup(sig, target_file_region)
            self._buffer.append(sig)
            if result.action in (
                DedupAction.WARN,
                DedupAction.BLOCK,
                DedupAction.HALT,
                DedupAction.TRIGGER_KILL_SWITCH,
            ):
                self._loop_events.append(
                    LoopEvent(
                        fingerprint=sig.fingerprint,
                        tool_name=tool_name,
                        count=result.identical_count,
                        action=result.action,
                        reason=result.reason,
                    )
                )
            if target_file_region:
                self._file_region_counts[target_file_region] = self._file_region_counts.get(target_file_region, 0) + 1

        return result

    def _check_dedup(self, sig: ActionSignature, target_file_region: str = "") -> DedupResult:
        identical_count = sum(1 for s in self._buffer if s.fingerprint == sig.fingerprint)
        semantic_count = sum(
            1
            for s in self._buffer
            if s.tool_params_semantic_hash and s.tool_params_semantic_hash == sig.tool_params_semantic_hash
        )

        if semantic_count >= _SEMANTIC_KILL_THRESHOLD:
            return DedupResult(
                action=DedupAction.TRIGGER_KILL_SWITCH,
                reason=f"语义重复 {semantic_count}x — 疑似 runaway agent",
                identical_count=semantic_count,
                fingerprint=sig.fingerprint,
            )

        if target_file_region and self._file_region_counts.get(target_file_region, 0) >= _SPIRAL_THRESHOLD:
            return DedupResult(
                action=DedupAction.HALT,
                reason=f"自修复螺旋 — {target_file_region} 被修改 {self._file_region_counts[target_file_region]}x",
                identical_count=self._file_region_counts[target_file_region],
                fingerprint=sig.fingerprint,
            )

        no_effect_count = sum(
            1
            for s in self._buffer
            if s.tool_name == sig.tool_name
            and s.output_effect_hash == sig.output_effect_hash
            and sig.output_effect_hash
        )
        if no_effect_count >= _NO_EFFECT_THRESHOLD:
            return DedupResult(
                action=DedupAction.WARN,
                reason=f"无效果动作链 — {sig.tool_name} 连续 {no_effect_count}x 无输出变化",
                identical_count=no_effect_count,
                fingerprint=sig.fingerprint,
            )

        if identical_count >= _IDENTICAL_BLOCK_THRESHOLD:
            return DedupResult(
                action=DedupAction.BLOCK,
                reason=f"重复动作循环 — {sig.tool_name} 重复 {identical_count}x",
                identical_count=identical_count,
                fingerprint=sig.fingerprint,
            )

        if identical_count >= _IDENTICAL_WARN_THRESHOLD:
            return DedupResult(
                action=DedupAction.WARN,
                reason=f"重复动作警告 — {sig.tool_name} 重复 {identical_count}x",
                identical_count=identical_count,
                fingerprint=sig.fingerprint,
            )

        return DedupResult(action=DedupAction.ALLOW, identical_count=identical_count, fingerprint=sig.fingerprint)

    def _purge_expired(self) -> None:
        cutoff = time.time() - self._ttl
        while self._buffer and self._buffer[0].timestamp < cutoff:
            self._buffer.popleft()

    def get_loop_events(self) -> list[LoopEvent]:
        with self._lock:
            return list(self._loop_events)

    def get_recent_actions(self, limit: int = 20) -> list[ActionSignature]:
        with self._lock:
            return list(self._buffer)[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()
            self._loop_events.clear()
            self._file_region_counts.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._buffer)

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "buffer_size": len(self._buffer),
                "loop_events_count": len(self._loop_events),
                "file_regions_tracked": len(self._file_region_counts),
                "ttl_seconds": self._ttl,
            }


ActionRecord = ActionSignature


__all__ = [
    "ActionHistory",
    "ActionSignature",
    "DedupAction",
    "DedupResult",
    "LoopEvent",
]
