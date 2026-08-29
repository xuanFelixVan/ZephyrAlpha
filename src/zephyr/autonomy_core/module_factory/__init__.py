# [BLUEPRINT] MOD-FACTORY-001/MOD-FACTORY-002 | docs/03_modules/_domain_autonomy_core/knowledge_classifier/blueprint.md + docs/03_modules/_domain_autonomy_core/module_mapper/blueprint.md | §
# [MODULE] zephyr.autonomy_core.module_factory
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.llm_runtime_gateway（仅消费既有 infer 签名）；pyyaml；sqlite3 FTS5
# [CONSUMERS] 模块工厂流水线人工编排（Phase 1 手动触发）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 包导出=纯模块名条目（无导入无初始化逻辑，同 autonomy_core 根包 ARCH-033 约定）；子模块产出 100% human_gated，不写注册表 YAML
# [MODIFY-GUARD] 变更须同步 13号文 §3.2/§3.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none（无运行逻辑）
# [TESTS] tests/autonomy/test_knowledge_classifier.py; tests/autonomy/test_module_mapper.py
# [A_module] module_id=MOD-FACTORY-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""module_factory — 模块工厂子包（13号文 Phase 1，#ARCH-286 归域 D_AUTONOMY_CORE）。

成员：
- knowledge_classifier（MOD-FACTORY-001）：LLM 受控词表知识分类器（§3.2）
- module_mapper（MOD-FACTORY-002）：知识→模块三段映射引擎（§3.3）

导出约定：纯模块名 __all__（无 eager import，同 autonomy_core 根包 ARCH-033 纪律），
消费方显式 ``from zephyr.autonomy_core.module_factory import knowledge_classifier``。
"""

__all__ = [
    "knowledge_classifier",
    "module_mapper",
]
