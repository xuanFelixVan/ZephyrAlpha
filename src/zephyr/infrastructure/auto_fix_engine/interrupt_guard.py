# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.interrupt_guard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS] engine.py;fix_scheduler.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SIGINT/SIGTERM MUST触发WAL恢复;零"半修复"状态
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml engine.wal_enabled
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InterruptGuardError
# [TESTS] tests/auto-fix-engine/test_interrupt_guard.py
# [A_module] module_id=MOD-INF_interrupt_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import json
import logging
import os
import signal
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)


class InterruptGuard:
    def __init__(
        self,
        wal_dir: str = "data/auto_fix/wal",
        db_path: str | Path = DB_PATH,
    ) -> None:
        self._wal_dir = Path(wal_dir)
        self._db_path = db_path
        self._active_fixes: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._original_sigint: Any = None
        self._original_sigterm: Any = None
        self._handlers_installed = False

    def install_handlers(self) -> None:
        if self._handlers_installed:
            return
        try:
            self._original_sigint = signal.getsignal(signal.SIGINT)
            self._original_sigterm = signal.getsignal(signal.SIGTERM)
            signal.signal(signal.SIGINT, self._handle_interrupt)
            signal.signal(signal.SIGTERM, self._handle_interrupt)
            self._handlers_installed = True
            logger.info("Interrupt guard handlers installed")
        except (OSError, ValueError):
            logger.warning("Cannot install signal handlers (not in main thread)")

    def remove_handlers(self) -> None:
        if not self._handlers_installed:
            return
        try:
            if self._original_sigint is not None:
                signal.signal(signal.SIGINT, self._original_sigint)
            if self._original_sigterm is not None:
                signal.signal(signal.SIGTERM, self._original_sigterm)
            self._handlers_installed = False
        except (OSError, ValueError):
            pass

    def begin_fix(self, action_id: str, target: str, before_content: str = "") -> None:
        with self._lock:
            self._active_fixes[action_id] = {
                "target": target,
                "before_content": before_content,
                "started_at": datetime.now(UTC).isoformat(),
                "phase": "started",
            }
            self._write_wal(action_id, "started", {"target": target})

    def update_phase(self, action_id: str, phase: str) -> None:
        with self._lock:
            if action_id in self._active_fixes:
                self._active_fixes[action_id]["phase"] = phase
                self._write_wal(action_id, phase, self._active_fixes[action_id])

    def complete_fix(self, action_id: str) -> None:
        with self._lock:
            self._active_fixes.pop(action_id, None)
            self._remove_wal(action_id)

    def recover(self) -> list[dict[str, Any]]:
        recovered: list[dict[str, Any]] = []
        if not self._wal_dir.exists():
            return recovered
        for wal_file in self._wal_dir.glob("*.wal"):
            try:
                data = json.loads(wal_file.read_text(encoding="utf-8"))
                action_id = wal_file.stem
                phase = data.get("phase", "unknown")
                target = data.get("target", "")
                if phase in ("started", "fixing", "writing"):
                    recovered.append(
                        {
                            "action_id": action_id,
                            "target": target,
                            "phase": phase,
                            "recovery_action": "rollback",
                            "before_content": data.get("before_content", ""),
                        }
                    )
                    self._rollback_fix(action_id, data)
                wal_file.unlink(missing_ok=True)
            except Exception as exc:
                logger.error("WAL recovery failed for %s: %s", wal_file, exc, exc_info=True)
        return recovered

    def _handle_interrupt(self, signum: int, frame: Any) -> None:
        logger.warning("Interrupt signal %d received, initiating WAL recovery", signum)
        with self._lock:
            for action_id, fix_data in list(self._active_fixes.items()):
                self._write_wal(action_id, "interrupted", fix_data)
                self._rollback_fix(action_id, fix_data)
            self._active_fixes.clear()
        if signum == signal.SIGINT and self._original_sigint and callable(self._original_sigint):
            self._original_sigint(signum, frame)
        elif signum == signal.SIGTERM and self._original_sigterm and callable(self._original_sigterm):
            self._original_sigterm(signum, frame)

    def _write_wal(self, action_id: str, phase: str, data: dict[str, Any]) -> None:
        try:
            self._wal_dir.mkdir(parents=True, exist_ok=True)
            wal_data = {**data, "phase": phase, "timestamp": datetime.now(UTC).isoformat()}
            wal_file = self._wal_dir / f"{action_id}.wal"
            tmp_path = str(wal_file) + f".{os.getpid()}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(wal_data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(wal_file))
        except Exception as exc:
            logger.error("WAL write failed for %s: %s", action_id, exc, exc_info=True)

    def _remove_wal(self, action_id: str) -> None:
        try:
            wal_file = self._wal_dir / f"{action_id}.wal"
            wal_file.unlink(missing_ok=True)
        except Exception as e:
            logger.warning("suppressed error in interrupt_guard", exc_info=True)

    def _rollback_fix(self, action_id: str, data: dict[str, Any]) -> None:
        target = data.get("target", "")
        before_content = data.get("before_content", "")
        if not target or not before_content:
            logger.warning("Cannot rollback %s: missing target or before_content", action_id)
            return
        try:
            target_path = Path(target)
            if target_path.exists():
                tmp_path = f"{target}.{os.getpid()}.rollback.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(before_content)
                os.replace(tmp_path, target)
                logger.info("Rolled back %s to pre-fix state", target)
        except Exception as exc:
            logger.error("Rollback failed for %s: %s", target, exc, exc_info=True)