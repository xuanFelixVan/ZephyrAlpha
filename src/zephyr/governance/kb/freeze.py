# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.freeze
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.kb.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_freeze | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""紧急冻结/解冻/安全模式断路器
==================================
蓝图: MOD-KB-001 7.10.1
任务: KB-INF-0047

三层模式:
  NORMAL  - 全功能运行
  SAFE    - 只读模式 (high-risk时自动触发)
  FROZEN  - 完全锁定 (紧急情况)

自动触发条件:
  1. 任意 gate 连续失败 >= 3 次
  2. G3 ghost scan 发现 ghost vector ratio > 20%
  3. 任意检查发现安全漏洞 (XSS/SQLi/路径遍历)

用法:
    python -m zephyr.knowledge.kb --freeze           # 手动冻结
    python -m zephyr.knowledge.kb --unfreeze         # 手动解冻
    python -m zephyr.knowledge.kb --safe-mode        # 切换到安全模式
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class FreezeMode(str, Enum):
    NORMAL = "normal"
    SAFE = "safe"
    FROZEN = "frozen"


class FreezeReason(str, Enum):
    MANUAL = "manual"
    GATE_CASCADE_FAILURE = "gate_cascade_failure"
    GHOST_VECTOR_BREACH = "ghost_vector_breach"
    SECURITY_BREACH = "security_breach"
    INTEGRITY_FAILURE = "integrity_failure"
    UNKNOWN = "unknown"


@dataclass
class FreezeRecord:
    mode: FreezeMode
    reason: FreezeReason
    since: str
    triggered_by: str
    details: str = ""


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


def _lock_path(root: Path) -> Path:
    snap_dir = root / "data" / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    return snap_dir / "kb_lock.json"


class FreezeCircuitBreaker:
    _GATE_FAILURE_THRESHOLD = 3
    _GHOST_RATIO_THRESHOLD = 0.20

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()
        self._failures: dict[str, int] = {}

    @property
    def state_path(self) -> Path:
        return _lock_path(self._root)

    def current_state(self) -> FreezeRecord | None:
        if not self.state_path.exists():
            return None
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return FreezeRecord(
                mode=FreezeMode(data["mode"]),
                reason=FreezeReason(data.get("reason", "unknown")),
                since=data.get("since", ""),
                triggered_by=data.get("triggered_by", "unknown"),
                details=data.get("details", ""),
            )
        except Exception:
            return None

    def is_frozen(self) -> bool:
        state = self.current_state()
        if state is None:
            return False
        return state.mode in (FreezeMode.SAFE, FreezeMode.FROZEN)

    def can_write(self) -> bool:
        state = self.current_state()
        if state is None:
            return True
        return state.mode is FreezeMode.NORMAL

    def can_read(self) -> bool:
        state = self.current_state()
        if state is None:
            return True
        return state.mode is not FreezeMode.FROZEN

    def freeze(
        self,
        reason: FreezeReason = FreezeReason.MANUAL,
        triggered_by: str = "manual",
        details: str = "",
    ) -> FreezeRecord:
        record = FreezeRecord(
            mode=FreezeMode.FROZEN,
            reason=reason,
            since=datetime.now(UTC).isoformat(),
            triggered_by=triggered_by,
            details=details,
        )
        self._write_state(record)
        logger.warning("KB FROZEN: reason=%s by=%s details=%s", reason.value, triggered_by, details)
        return record

    def safe_mode(
        self,
        reason: FreezeReason = FreezeReason.MANUAL,
        triggered_by: str = "manual",
        details: str = "",
    ) -> FreezeRecord:
        record = FreezeRecord(
            mode=FreezeMode.SAFE,
            reason=reason,
            since=datetime.now(UTC).isoformat(),
            triggered_by=triggered_by,
            details=details,
        )
        self._write_state(record)
        logger.warning("KB SAFE MODE: reason=%s by=%s", reason.value, triggered_by)
        return record

    def unfreeze(self, triggered_by: str = "manual") -> FreezeRecord:
        record = FreezeRecord(
            mode=FreezeMode.NORMAL,
            reason=FreezeReason.MANUAL,
            since=datetime.now(UTC).isoformat(),
            triggered_by=triggered_by,
            details="Unfrozen by " + triggered_by,
        )
        self._write_state(record)
        logger.info("KB UNFROZEN: by=%s", triggered_by)
        return record

    def _write_state(self, record: FreezeRecord) -> None:
        data = {
            "mode": record.mode.value,
            "reason": record.reason.value,
            "since": record.since,
            "triggered_by": record.triggered_by,
            "details": record.details,
        }
        self.state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def record_gate_failure(self, gate_name: str) -> bool:
        self._failures[gate_name] = self._failures.get(gate_name, 0) + 1
        if self._failures[gate_name] >= self._GATE_FAILURE_THRESHOLD:
            self.safe_mode(
                reason=FreezeReason.GATE_CASCADE_FAILURE,
                triggered_by=f"gate:{gate_name}",
                details=f"Gate {gate_name} failed {self._failures[gate_name]} consecutive times",
            )
            return True
        return False

    def reset_gate_failures(self, gate_name: str) -> None:
        self._failures.pop(gate_name, None)

    def evaluate_ghost_ratio(self, md_count: int, chroma_count: int) -> bool:
        if md_count == 0:
            return False
        ghost_ratio = abs(md_count - chroma_count) / md_count
        if ghost_ratio > self._GHOST_RATIO_THRESHOLD:
            self.safe_mode(
                reason=FreezeReason.GHOST_VECTOR_BREACH,
                triggered_by="ghost_scan",
                details=f"Ghost ratio {ghost_ratio:.1%} > {self._GHOST_RATIO_THRESHOLD:.0%} threshold "
                f"(MD={md_count}, ChromaDB={chroma_count})",
            )
            return True
        return False

    def security_breach_detected(self, breach_type: str) -> FreezeRecord:
        return self.freeze(
            reason=FreezeReason.SECURITY_BREACH,
            triggered_by="security_scanner",
            details=f"Security breach detected: {breach_type}",
        )

    def integrity_breach_detected(self, file_path: str, expected: str, actual: str) -> FreezeRecord:
        return self.freeze(
            reason=FreezeReason.INTEGRITY_FAILURE,
            triggered_by="integrity_checker",
            details=f"Integrity breach: {file_path} (expected={expected[:12]}..., actual={actual[:12]}...)",
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Emergency Freeze/Safe Mode Circuit Breaker")
    parser.add_argument("--freeze", action="store_true", help="Manually freeze KB (complete lockdown)")
    parser.add_argument("--safe-mode", action="store_true", help="Switch to safe mode (read-only)")
    parser.add_argument("--unfreeze", action="store_true", help="Unfreeze and restore normal mode")
    parser.add_argument("--status", action="store_true", help="Print current state")
    parser.add_argument("--json", action="store_true", help="JSON output for --status")
    args = parser.parse_args()

    cb = FreezeCircuitBreaker()

    if args.status:
        state = cb.current_state()
        if args.json:
            if state:
                print(
                    json.dumps(
                        {
                            "mode": state.mode.value,
                            "reason": state.reason.value,
                            "since": state.since,
                            "triggered_by": state.triggered_by,
                            "details": state.details,
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                print(json.dumps({"mode": "normal", "reason": "none"}, ensure_ascii=False))
        else:
            if state:
                print(f"KB State: {state.mode.value.upper()}")
                print(f"  Reason:  {state.reason.value}")
                print(f"  Since:   {state.since}")
                print(f"  By:      {state.triggered_by}")
                if state.details:
                    print(f"  Details: {state.details}")
            else:
                print("KB State: NORMAL (no lock file)")
        return

    if args.freeze:
        cb.freeze(reason=FreezeReason.MANUAL, triggered_by="cli")
        print("KB is now FROZEN. No reads or writes allowed.")
        return

    if args.safe_mode:
        cb.safe_mode(reason=FreezeReason.MANUAL, triggered_by="cli")
        print("KB is now in SAFE MODE. Read-only; writes rejected.")
        return

    if args.unfreeze:
        cb.unfreeze(triggered_by="cli")
        print("KB is now UNFROZEN. Normal operations restored.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
