# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_locking
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_locking | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Locking (Production Hardening)
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0

Skill 并发安全锁 —— 多 Session/多 Agent 并发读写保护.
基于文件锁 + 内存锁双层保护，防 registry/skill-file 竞争条件.
"""

from __future__ import annotations

import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, final


class SkillLock:
    """Skill 读写锁 —— 并发安全."""

    _LOCKS: dict[str, threading.RLock] = {}
    _LOCK_FACTORY = threading.Lock()

    LOCK_DIR = Path("_locks")
    DEFAULT_TIMEOUT_S = 30.0

    @classmethod
    def _get_lock(cls, key: str) -> threading.RLock:
        with cls._LOCK_FACTORY:
            if key not in cls._LOCKS:
                cls._LOCKS[key] = threading.RLock()
            return cls._LOCKS[key]

    @classmethod
    @contextmanager
    def read_lock(cls, skill_id: str):
        lock = cls._get_lock(f"r:{skill_id}")
        acquired = lock.acquire(timeout=cls.DEFAULT_TIMEOUT_S)
        if not acquired:
            raise TimeoutError(f"Read lock timeout for {skill_id}")
        try:
            yield
        finally:
            lock.release()

    @classmethod
    @contextmanager
    def write_lock(cls, skill_id: str):
        lock = cls._get_lock(f"w:{skill_id}")
        acquired = lock.acquire(timeout=cls.DEFAULT_TIMEOUT_S)
        if not acquired:
            raise TimeoutError(f"Write lock timeout for {skill_id}")
        try:
            yield
        finally:
            lock.release()

    @classmethod
    @contextmanager
    def registry_lock(cls):
        lock = cls._get_lock("registry")
        acquired = lock.acquire(timeout=cls.DEFAULT_TIMEOUT_S)
        if not acquired:
            raise TimeoutError("Registry lock timeout")
        try:
            yield
        finally:
            lock.release()

    @classmethod
    def lock_stats(cls) -> dict[str, Any]:
        return {"active_locks": len(cls._LOCKS)}


@final
class SkillFileLock:
    """基于文件的跨进程锁."""

    LOCK_DIR = Path("_locks")

    @classmethod
    def _lock_path(cls, name: str) -> Path:
        cls.LOCK_DIR.mkdir(parents=True, exist_ok=True)
        return cls.LOCK_DIR / f"{name}.lock"

    @classmethod
    @contextmanager
    def acquire(cls, name: str, timeout_s: float = 30.0):
        path = cls._lock_path(name)
        deadline = time.time() + timeout_s
        fd = None
        while time.time() < deadline:
            try:
                fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(fd, str(os.getpid()).encode())
                break
            except FileExistsError:
                time.sleep(0.05)
            except BaseException:
                # 5.128.3 修复: os.write 等失败时 fd 已打开但未关闭,异常传播导致 fd 泄漏。
                # FileExistsError 时 fd 为 None(os.open 失败),无需 close;其他异常时 close fd。
                if fd is not None:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
                    fd = None
                raise
        if fd is None:
            raise TimeoutError(f"File lock timeout: {name}")
        try:
            yield
        finally:
            # 5.73.3 修复：原 os.close(fd) 未被 try/except 包裹。若 os.close 抛出 OSError，后续 path.unlink 不会执行，留下僵尸锁文件。
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass


__all__ = ["SkillFileLock", "SkillLock"]
