# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_locking
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Locking (Production Hardening)
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0

Skill 并发安全锁 —— 多 Session/多 Agent 并发读写保护.
基于文件锁 + 内存锁双层保护，防 registry/skill-file 竞争条件.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_locking.py
# 层: 算法
# - id: A1
#   name_zh: ① SkillLock
#   name_en: SkillLock
#   intro: Skill 读写锁 —— 并发安全.
#   desc: Skill 读写锁 —— 并发安全.；公共方法（定义序）: get_locks, get_lock_factory, get_lock, is_lock_owned, read_lock, write_lock, re…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② SkillFileLock
#   name_en: SkillFileLock
#   intro: 基于文件的跨进程锁.
#   desc: 基于文件的跨进程锁.；公共方法（定义序）: lock_path, acquire；源码 L152-L203
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SkillLock, SkillFileLock
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
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

    # ── Stage 4 公共化属性 + 方法 ──

    @classmethod
    def get_locks(cls) -> dict[str, threading.RLock]:
        """获取锁字典（public API, Stage 4）."""
        return cls._LOCKS

    @classmethod
    def get_lock_factory(cls) -> threading.Lock:
        """获取锁工厂（public API, Stage 4）."""
        return cls._LOCK_FACTORY

    @classmethod
    def get_lock(cls, key: str) -> threading.RLock:
        """获取指定 key 的锁（public API, Stage 4）."""
        return cls._get_lock(key)

    @classmethod
    def is_lock_owned(cls, key: str) -> bool:
        """检查指定 key 的锁是否被当前线程持有（public API, Stage 4）."""
        return cls._get_lock(key)._is_owned()

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
    def lock_path(cls, name: str) -> Path:
        """获取锁文件路径（public API, Stage 4）."""
        return cls._lock_path(name)

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
            except BaseException:  # noqa: BLE001 — 5.135治标: broad exception catch
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
