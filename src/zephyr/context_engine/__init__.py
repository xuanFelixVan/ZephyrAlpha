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

bounded_context = True

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

__all__ = ['ContextFourStageResult', 'ContextHealthScore', 'DEFAULT_ARCH_CONTEXT_PATH', 'adversarial_robustness', 'alignment_scorer', 'architecture_context_loader', 'atomic_injector', 'bounded_context', 'budget_forecaster', 'cache_invalidation', 'ce_bootstrap', 'ce_explain_cli', 'ce_playground_v2', 'ce_vibe_shortcuts', 'checkpoint_manager', 'citation_walker', 'cold_start_booster', 'complexity_budget', 'config_safety_guard', 'context_assembler', 'context_budget_tracker', 'context_debt_score', 'context_evaluator', 'context_evictor', 'context_injector', 'context_model_strategy', 'context_outcome_tracker', 'context_pipeline', 'context_playground', 'context_rot_model', 'context_value_attribution', 'contextual_fetch_api', 'curation_loop', 'dependency_tracker', 'diff_injector', 'dispatch_table', 'diversity_constraint', 'doc_compressor', 'domain_decay_config', 'embedding_version_lock', 'fallback_staleness_gate', 'format_architecture_context_excerpt', 'fragmentation_index', 'host_resource_governor', 'integrity_check', 'intent_keyword_mapper', 'intent_parser', 'kill_switch', 'knowledge_distiller', 'list_ce_files', 'load_architecture_context_dict', 'lsg_pattern_tracker', 'mcp_adapter', 'memory_bank', 'mode_manager', 'otel_instrumentation', 'pattern_library', 'pipeline_orchestrator', 'poisoning_monitor', 'position_optimizer', 'progressive_disclosure_injector', 'prompt_registry', 'rational', 'run_context_four_stage', 'run_context_four_stage_or_raise', 'self_diagnosis', 'sensitivity_classifier', 'session_learner', 'shadow_canary', 'solo_dev_safety_net', 'staleness_manager', 'system_snapshot', 'token_budget', 'vector_bridge', 'verify_paths']
