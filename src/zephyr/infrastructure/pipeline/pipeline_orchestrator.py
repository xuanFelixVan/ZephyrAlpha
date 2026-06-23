# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §4.1
# [MODULE] zephyr.infrastructure.pipeline.pipeline_orchestrator
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.shared_services.models; zephyr.infrastructure.__init__; zephyr.shared.__init__; zephyr.governance.__init__; zephyr.governance.audit_trail.writer; zephyr.integration.vector_memory.local_model_scheduler; zephyr.governance.persistence.task_repo; zephyr.shared.contracts.llm_gateway_protocol; zephyr.shared.infra.observer; zephyr.integration.mcp.__init__; zephyr.integration.vector_memory.embedding_router
# [CONSUMERS] zephyr.infrastructure.pipeline.__init__.py (re-export); legacy imports via infrastructure.pipeline.pipeline_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.integration.pipeline_orchestrator (DW-2026062403 去重裁定)
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.integration.pipeline_orchestrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if integration.pipeline_orchestrator symbols unavailable
# [TESTS] tests/test_pipeline_orchestrator_auto.py; tests/unit/pipeline/test_pipeline_orchestrator.py
# [A_module] module_id=MOD-INF_pipeline_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
PipelineOrchestrator re-export shim — 真源已合并至 zephyr.integration.pipeline_orchestrator (DW-2026062403)。

本文件保留为向后兼容 shim，所有符号从 zephyr.integration.pipeline_orchestrator 重新导出。
新代码应直接 import from zephyr.integration.pipeline_orchestrator。

Import 路径映射:
    from zephyr.infrastructure.pipeline.pipeline_orchestrator import PipelineOrchestrator
        -> zephyr.integration.pipeline_orchestrator

验证: 两版本74个方法名完全相同(ast比对 same: True)，功能等价。
"""

from zephyr.integration.pipeline_orchestrator import PipelineOrchestrator  # noqa: F401

__all__ = ["PipelineOrchestrator"]
