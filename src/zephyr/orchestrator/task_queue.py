"""
ActiveTaskQueue — 后台任务轮询与自动分发
==========================================
Blueprint: MOD-INF-006 盲点#9

线程安全的后台调度器：定期扫描 READY 任务，自动 dispatch。

NOTE: 此模块已迁移至 zephyr.orchestrator.core.task_queue，
      本文件仅保留向后兼容的 re-export。
      修复: 消除双重 TaskQueue 实例导致的重复轮询问题。
"""
from __future__ import annotations

from zephyr.orchestrator.core.task_queue import (  # noqa: F401
    PipelineDispatcher,
    TaskQueue,
    get_queue,
)
