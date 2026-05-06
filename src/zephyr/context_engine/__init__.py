"""Context Engine (CE)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一

职责
----
上下文的四阶段流水线：build → compress → validate → inject

压缩方式 : 本地 LLM（Qwen2.5-3B-Instruct ONNX int8）
          + 规则基摘要 + 截断三级回退

降级路径 (§3.3)
  DEGRADE-001: VMS 挂 → 文件系统 grep
  DEGRADE-002: LLM 压缩失败 → 规则基
  DEGRADE-003: MCP 通道不可用 → 切换备用通道

beta a 新增（2026-05-05）
  - ContextRotModel  : n² 注意力衰减数学模型
  - ContextEvictor   : 三维排序上下文逐出器
  - context_injector : Provenance 溯源字段

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理 + ADR-0015 CE
架构真源：docs/02_enterprise_architecture/target-architecture/
         vibe-coding-infrastructure-architecture.md §3.3

依赖
----
- VMS（vector_memory/）：检索
- LSG（llm_security/）：注入前验证

组合根（根因修复）
----------------
四段流水线的**单一编排入口**：``context_pipeline.run_context_four_stage``（见文末 re-export）。
"""
from __future__ import annotations

from zephyr.context_engine.architecture_context_loader import (
    DEFAULT_ARCH_CONTEXT_PATH,
    format_architecture_context_excerpt,
    load_architecture_context_dict,
)
from zephyr.context_engine.context_pipeline import (
    ContextFourStageResult,
    run_context_four_stage,
    run_context_four_stage_or_raise,
)

__all__ = [
    "ContextFourStageResult",
    "DEFAULT_ARCH_CONTEXT_PATH",
    "format_architecture_context_excerpt",
    "load_architecture_context_dict",
    "run_context_four_stage",
    "run_context_four_stage_or_raise",
]
