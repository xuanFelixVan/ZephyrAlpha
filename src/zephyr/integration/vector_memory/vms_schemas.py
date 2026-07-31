# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.vms_schemas
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-011 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VMS 共享数据模型 — MOD-INF-011 · 蓝图 §6.1 接口契约
======================================================
全部 Pydantic V2 BaseModel（ADR-0040 强制——禁止 dataclass）

模型清单
--------
  ScoredHit          — 检索命中结果
  RetrievalTrace     — 检索链完整追溯
  HealthReport       — 索引健康报告
  Chunk              — 分块片段
  WriteTrace         — 写入溯源记录
  CollectionMetadata — Collection 元数据快照
  Provenance         — CBAC 三字段溯源
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG


class Provenance(BaseModel):
    model_config = BASE_CONFIG

    origin: str = ""
    audit_chain: list[str] = Field(default_factory=list)
    arbitration: str = ""


class ScoredHit(BaseModel):
    model_config = BASE_CONFIG

    content: str = ""
    score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    why_top: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance | None = None
    partial: bool = False


class RetrievalTrace(BaseModel):
    model_config = BASE_CONFIG

    query: str = ""
    hits: list[ScoredHit] = Field(default_factory=list)
    source_collection: str = ""
    rerank_info: dict[str, Any] = Field(default_factory=dict)
    embedding_model_version: str = ""


class HealthReport(BaseModel):
    model_config = BASE_CONFIG

    collection_name: str = ""
    status: str = "unknown"
    issue_count: int = 0
    recommendations: list[str] = Field(default_factory=list)
    last_check: str = ""


class Chunk(BaseModel):
    model_config = BASE_CONFIG

    text: str = ""
    start_pos: int = 0
    end_pos: int = 0
    overlap_with_prev: bool = False
    overlap_with_next: bool = False


# WriteTrace 已合并至 unified_memory_api（#ARCH-VMS-WRITETRACE-CONSOLIDATE-001）
# 依赖方向裁定：unified_memory_api→vms_schemas 路径已存在（经 vms_memory_backend 链），
# 直接 import 会闭合循环导入。故用 __getattr__ 懒加载——运行时访问 WriteTrace 时才 import，
# 模块加载期无循环依赖。depgraph 不登记此边（君子协定：lazy import 破环，非真架构依赖）。


class CollectionMetadata(BaseModel):
    model_config = BASE_CONFIG

    name: str = ""
    dimension: int = 0
    embedding_model: str = ""
    chunk_strategy: str = ""
    ttl_days: int = 0
    ai_autonomy_level: str = ""


# WriteTrace 懒加载实现（PEP 562 module __getattr__）
# `from zephyr.integration.vector_memory.vms_schemas import WriteTrace` 在运行时
# 触发本函数，从 unified_memory_api 拿到 WriteTrace 并缓存到 globals()——后续访问
# 直接 __dict__ 命中，无重复 import 开销。模块加载期不触发，避免循环导入。


def __getattr__(name: str):
    """模块级懒加载（PEP 562）— #ARCH-VMS-WRITETRACE-CONSOLIDATE-001。

    WriteTrace 已合并至 ``unified_memory_api``（SSoT）。本模块不顶层 import
    以避免循环依赖（vms_memory_backend→unified_memory_api→vms_schemas 边
    已存在，反向会闭环）。运行时 ``from vms_schemas import WriteTrace``
    经此函数转发至 unified_memory_api.WriteTrace。
    """
    if name == "WriteTrace":
        from zephyr.intelligence.model_evaluation.unified_memory_api import (
            WriteTrace as _WriteTrace,
        )

        globals()["WriteTrace"] = _WriteTrace  # cache：后续直接 __dict__ 命中
        return _WriteTrace
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
