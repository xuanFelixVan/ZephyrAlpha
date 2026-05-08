---
task_id: "TASK-INF-0111"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 19 + §14 盲点 B51-B53"

title: "Phase 19 施工——AI 安全纵深：Prompt注入防御(B51) + 结构化输出强制保障(B52) + LLM API专属限流(B53)"
description: |
  实现三层 AI 安全纵深防御。
  B51：Prompt Injection Defense——标签式信任传播。用户输入需用 IFC（Information Flow Control）
  标签标记信任级别，防止低信任数据污染高信任 prompt。
  需实现：IFCLabel——trust_level (untrusted/user/system/privileged) + taint propagation。
  对标 Microsoft FIDES (2026.4) / Entra AI Gateway。
  B52：Structured Output Guarantee——LLM 输出强制校验 + 自动重试。当 LLM 输出不符合 Pydantic schema
  时自动重试（最多 3 次），每次重试追加校验错误到 prompt。
  需实现：StructuredOutputGuarantor——validate_output() + retry_with_error_context()。
  对标 Instructor / PydanticAI。
  B53：LLM API 专属速率限制 + Provider 降级。当主 LLM provider 速率限制触发时，
  自动降级到备用 provider（按 pricing/capability 优先级）。
  需实现：LLMRateLimiter——per-provider token bucket + provider_degradation()。
  对标 OpenAI tiers / LiteLLM router。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\limiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ifc_guard.py"
    description: "IFCLabel——trust_level + taint propagation（FIDES 对齐）"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\structured_output.py"
    description: "StructuredOutputGuarantor——validate + 自动重试(最多3次)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\llm_rate_limiter.py"
    description: "LLMRateLimiter——per-provider token bucket + provider降级"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_ifc_guard.py"
    description: "单元测试——验证信任标签传播"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_structured_output.py"
    description: "单元测试——验证校验失败重试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_llm_rate_limiter.py"
    description: "单元测试——验证限流触发降级"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ifc_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\structured_output.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\llm_rate_limiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_ifc_guard.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_structured_output.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_llm_rate_limiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\limiter.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §4/§14——Phase 19 + B51-B53 盲点详情"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\limiter.py"
    reason: "limiter.py——B53 需基于 TokenBucket 扩展 per-provider 限流"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 20000
timeout_minutes: 50

acceptance_criteria:
  - "ifc_guard.py: IFCLabel——trust_level 枚举：untrusted/user/system/privileged"
  - "ifc_guard.py: taint_propagate()——低信任数据混入高信任 context → taint level 下降"
  - "structured_output.py: StructuredOutputGuarantor——validate(output, model_cls) → model instance or ValidationError"
  - "structured_output.py: retry 最多 3 次——每次追加校验错误到 next prompt"
  - "llm_rate_limiter.py: PerProviderTokenBucket——每 provider 独立 bucket"
  - "llm_rate_limiter.py: provider_degradation()——主 provider 限流 → 次优 provider"
  - "pytest tests/unit/test_ifc_guard.py -v 全部通过"
  - "pytest tests/unit/test_structured_output.py -v 全部通过"
  - "pytest tests/unit/test_llm_rate_limiter.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 3 个模块入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\ifc_guard.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\structured_output.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\shared\llm_rate_limiter.py
  4. 删除 3 个对应测试文件
  5. 还原 __init__.py 对应导出
  6. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0109"]
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
