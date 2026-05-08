---
task_id: "TASK-INF-0107"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 15 + §12 盲点 B35-B40"

title: "Phase 15 施工——AI 架构可控：Provider抽象(B35) + 上下文压缩(B36) + 输出评分(B37) + 配置链(B38) + DI容器(B39) + 沙箱(B40)"
description: |
  实现 6 项 AI 架构可控能力——从 Model Provider 抽象到代码生成沙箱。
  B35：`api_client.py` 有 HTTP 层统一 client，缺模型语义层（pricing-aware provider、自动 fallback、capability 查询）。
  需实现：ModelProvider 抽象层——provider registry + pricing-aware routing + auto-fallback。
  B36：当上下文接近模型上限时需智能压缩（摘要旧消息、保留关键决策）。
  需实现：TruncationStrategy 接口 + 摘要/保留 key decisions/优先最近消息三种策略。
  B37：结构化 Agent 输出质量评分——Relevance/Accuracy/Completeness 三维 + 自动回归。
  需实现：QualityScorer——三维评分 rubrics + 批量回归检测。
  B38：配置覆盖链——环境变量 > YAML 配置 > 默认值优先级。
  需实现：ConfigOverrideChain——三级合并 + Pydantic 校验。
  B39：依赖注入容器——AI agent 组件化：constructor injection → 组件可替换 → 测试可隔离。
  需实现：DIContainer——constructor injection + scope (singleton/transient/scoped)。
  B40：AI 代码生成沙箱——`process_sandbox.py` 在 `llm_security/`，shared/ 应有沙箱接口抽象。
  需实现：SandboxInterface Protocol——execute/validate/sanitize 三方法。
  专业对标：PydanticAI model-agnostic providers / LiteLLM / LangChain summarization / Spring DI / FastAPI Depends / LLMCore sandboxed execution。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\api_client.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config\\loader.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\model_provider.py"
    description: "ModelProvider 抽象——provider registry + pricing-aware routing + auto-fallback"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\truncation_strategy.py"
    description: "TruncationStrategy 接口——摘要/保留key decisions/优先最近消息"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\quality_scorer.py"
    description: "QualityScorer——Relevance/Accuracy/Completeness 三维评分 + 批量回归"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config_chain.py"
    description: "ConfigOverrideChain——环境>YAML>默认 三级合并 + Pydantic 校验"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\di_container.py"
    description: "DIContainer——constructor injection + singleton/transient/scoped scope"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\sandbox_interface.py"
    description: "SandboxInterface Protocol——execute/validate/sanitize"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_model_provider.py"
    description: "单元测试——验证 provider routing + fallback 逻辑"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_truncation_strategy.py"
    description: "单元测试——验证三种截断策略正确性"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_quality_scorer.py"
    description: "单元测试——验证评分一致性、回归检测"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_config_chain.py"
    description: "单元测试——验证三级合并优先级"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_di_container.py"
    description: "单元测试——验证 injection + scope"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_sandbox_interface.py"
    description: "单元测试——验证 Protocol 签名"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\model_provider.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\truncation_strategy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\quality_scorer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config_chain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\di_container.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\sandbox_interface.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_model_provider.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_truncation_strategy.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_quality_scorer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_config_chain.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_di_container.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_sandbox_interface.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\api_client.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\process_sandbox.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——新增模块被 ≥2 个 L01 模块消费"
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "所有新模型 MUST 为 Pydantic V2 BaseModel"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §4/§12——Phase 15 + B35-B40 盲点详情"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\api_client.py"
    reason: "api_client.py——B35 需在此之上构建模型语义层"

assigned_model: "claude-opus-4.7"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 45000
timeout_minutes: 120

acceptance_criteria:
  - "model_provider.py: ModelProviderRegistry——register/get/list 含 pricing 数据"
  - "model_provider.py: auto_fallback()——主 provider 不可用时按 pricing/capability 优先级切换"
  - "truncation_strategy.py: TruncationStrategy Protocol——truncate(messages, budget) → truncated_messages"
  - "truncation_strategy.py: 三种内置策略——SummarizeOldest / KeepKeyDecisions / PrioritizeRecent"
  - "quality_scorer.py: QualityReport 模型——relevance_score/accuracy_score/completeness_score + overall"
  - "quality_scorer.py: batch_evaluate()——批量评分 + 回归对比"
  - "config_chain.py: ConfigOverrideChain——merge(env_vars, yaml_config, defaults) → validated_config"
  - "di_container.py: DIContainer——register(type, factory, scope) + resolve(type)"
  - "di_container.py: 三种 scope——singleton / transient / scoped（per request）"
  - "sandbox_interface.py: SandboxInterface Protocol——execute(code, timeout) / validate(code) / sanitize(code)"
  - "pytest tests/unit/test_model_provider.py -v 全部通过"
  - "pytest tests/unit/test_truncation_strategy.py -v 全部通过"
  - "pytest tests/unit/test_quality_scorer.py -v 全部通过"
  - "pytest tests/unit/test_config_chain.py -v 全部通过"
  - "pytest tests/unit/test_di_container.py -v 全部通过"
  - "pytest tests/unit/test_sandbox_interface.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 6 个模块入口"

rollback_instructions: |
  1. 删除 6 个 src/zephyr/shared/ 新文件
  2. 删除 6 个 tests/unit/ 对应测试文件
  3. 还原 __init__.py 对应导出
  4. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0101"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-opus-4.7"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
