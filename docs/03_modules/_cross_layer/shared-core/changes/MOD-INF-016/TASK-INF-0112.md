---
task_id: "TASK-INF-0112"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 20 + §14 盲点 B54-B56"

title: "Phase 20 施工——AI 校验护盾：工具调用参数护栏(B54) + Prompt缓存策略(B55) + 多Provider语义降级(B56)"
description: |
  实现 AI 工具调用的参数校验、缓存优化与多 Provider 降级。
  B54：Tool Call Parameter Validation——工具调用参数护栏。AI agent 调用工具时，
  参数需在调用前被校验，防止注入或越权调用。
  需实现：ToolCallGuard——@validate_tool_params 装饰器 + parameter_schema + input_sanitization。
  对标 agent_rbac input_guard。
  B55：Prompt Caching Strategy——上下文缓存策略。重复的 system prompt / 工具定义等
  应在 LLM API 层面利用 prompt caching 减少 token 消耗。
  需实现：PromptCacheStrategy——cache_key 生成 + 命中率追踪 + break_even 分析。
  对标 Anthropic/OpenAI prompt caching。
  B56：Multi-Provider Semantic Equivalence Fallback——多 Provider 语义等价降级。
  当主 provider 返回的结果不符合语义要求时，自动降级到语义等价的替代 provider。
  需实现：SemanticFallback——output_equivalence_check() + provider_rank() + fallback_chain()。
  对标 LiteLLM / OpenRouter。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\input_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\tool_call_guard.py"
    description: "ToolCallGuard——@validate_tool_params + parameter_schema"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\prompt_cache.py"
    description: "PromptCacheStrategy——cache_key + 命中率 + break_even"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\semantic_fallback.py"
    description: "SemanticFallback——output_equivalence + provider_rank + fallback_chain"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_tool_call_guard.py"
    description: "单元测试——验证参数校验、注入预防"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_prompt_cache.py"
    description: "单元测试——验证缓存命中、break_even"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_semantic_fallback.py"
    description: "单元测试——验证等价判断、降级链"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\tool_call_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\prompt_cache.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\semantic_fallback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_tool_call_guard.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_prompt_cache.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_semantic_fallback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\input_guard.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §4/§14——Phase 20 + B54-B56 盲点详情"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\input_guard.py"
    reason: "agent_rbac/input_guard——B54 共享层工具调用护栏的参照基"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 15000
timeout_minutes: 40

acceptance_criteria:
  - "tool_call_guard.py: ToolCallGuard——@validate_tool_params 装饰器"
  - "tool_call_guard.py: parameter_schema——Pydantic model 对每个工具调用的参数定义"
  - "tool_call_guard.py: input_sanitization——清理参数中的注入模式"
  - "prompt_cache.py: PromptCacheStrategy——compute_cache_key(prompt_text) → cache_key"
  - "prompt_cache.py: track_hit_rate()——命中率统计 + break_even 分析（省 token 数 vs 缓存开销）"
  - "semantic_fallback.py: output_equivalence_check(a, b)——判断两 provider 输出是否语义等价"
  - "semantic_fallback.py: provider_rank()——按 semantic_accuracy / cost / latency 排序"
  - "semantic_fallback.py: fallback_chain()——按序尝试 providers 直到语义等价"
  - "pytest tests/unit/test_tool_call_guard.py -v 全部通过"
  - "pytest tests/unit/test_prompt_cache.py -v 全部通过"
  - "pytest tests/unit/test_semantic_fallback.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 3 个模块入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\tool_call_guard.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\prompt_cache.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\shared\semantic_fallback.py
  4. 删除 3 个对应测试文件
  5. 还原 __init__.py 对应导出
  6. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0111"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
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
