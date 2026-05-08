"""
ZephyrAlpha 知识库子包
======================

职责：知识生命周期管理——从文档/代码中摄取结构化和非结构化知识，
经分析、提取、验证后激活，供 AI Agent 查询与决策使用。

子模块：
  - activate.py              知识激活（暂存 → 正式索引）
  - analyze.py               语义分析 + 关系抽取
  - batch_ingest.py          批量知识摄入
  - bootstrap.py             冷启动引导 + 文档扫描
  - chromadb_init.py         ChromaDB 向量数据库初始化
  - embedding_migrate.py     嵌入向量迁移
  - extract.py               结构化/非结构化知识提取
  - freeze.py                紧急冻结断路器
  - graph_validator.py       知识图谱校验
  - ingest.py                单条知识摄入
  - integrity.py              SHA256源码完整性防篡改
  - kb_gate_task.py          门控任务调度
  - kb_repo.py               知识库 CRUD 仓库
  - ke_tombstone.py          SQLite墓碑表
  - load_bearing.py          承重KE不可变性
  - quiet_period_monitor.py  静默期检测
  - reranker.py              混合检索重排序
  - safety_brake.py          冷静期+魔鬼代言人
  - self_test.py             13项一键体检
  - triage.py                知识分诊（优先级排序）
  - unified_memory_api.py    统一内存 API
  - verify.py                确定性事实核查

架构归属：B-track 独立能力，全系统主向量后端已迁至 VMS (MOD-INF-011 · blueprint v0.7.0)。
本包保留 4 个 KB-legacy ChromaDB Collection，通过 VectorBridge 与 VMS 双相同步。

注意：本包当前 bounded_context: false——直接暴露所有模块供
orchestrator/ + l12/ 消费，不设受限边界。
"""

from __future__ import annotations

from zephyr.kb.bootstrap import Bootstrap
from zephyr.kb.freeze import FreezeCircuitBreaker
from zephyr.kb.integrity import IntegrityGuard
from zephyr.kb.ke_tombstone import TombstoneManager
from zephyr.kb.load_bearing import LoadBearingWall
from zephyr.kb.quiet_period_monitor import QuietPeriodMonitor
from zephyr.kb.reranker import Reranker
from zephyr.kb.safety_brake import SafetyBrake
from zephyr.kb.self_test import SelfTest
from zephyr.kb.verify import FactChecker

__all__ = [
    "activate",
    "analyze",
    "batch_ingest",
    "bootstrap",
    "chromadb_init",
    "embedding_migrate",
    "extract",
    "freeze",
    "graph_validator",
    "ingest",
    "integrity",
    "kb_gate_task",
    "kb_repo",
    "ke_tombstone",
    "load_bearing",
    "quiet_period_monitor",
    "reranker",
    "safety_brake",
    "self_test",
    "triage",
    "unified_memory_api",
    "verify",
    "vms_memory_backend",
    "Bootstrap",
    "FreezeCircuitBreaker",
    "IntegrityGuard",
    "TombstoneManager",
    "LoadBearingWall",
    "QuietPeriodMonitor",
    "Reranker",
    "SafetyBrake",
    "SelfTest",
    "FactChecker",
]
