---
task_id: "TASK-INF-0208"
source_blueprint: "MOD-INF-014"
source_section: "§8 L5 + §25.4 盲点四 + §40 性能预算 + §50 模型提取 + §54 成本不对称 + §58 语义缓存"
title: "L5 资源保护层完整实现——Token预算+速率限制+成本熔断+Agent执行保护+AI递归+性能SLO+模型提取+成本不对称+语义缓存防御"
description: |
  实现 ResourceProtectionLayer: Token预算管控(TokenBudget)、滑动窗口速率限制(SlidingWindowRateLimiter)、
  成本熔断(LLMCostCircuitBreaker)、Agent递归执行保护(AIRecursionGuard)、
  Agent最大步数/存活时间/内存限制(AgentExecutionProtector)、LSG自身性能SLO(P50<10ms/P95<50ms)、
  模型提取防御(输出扰动+MVI策略)、成本不对称攻击防御(攻击成本升级+免费情报消耗拦截)、
  语义缓存键冲突防御(Key Salting+缓存完整性HMAC验证)。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l5_resource_protection.py"
    description: "L5 ResourceProtectionLayer——Token+速率+成本+递归+Agent保护+性能+模型提取+成本不对称+缓存"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l5_resource_protection.py"
    description: "L5 资源保护单元测试——15条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l5_resource_protection.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l5_resource_protection.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§8+§25.4+§40+§50+§54+§58"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 15000
timeout_minutes: 90
acceptance_criteria:
  - "ResourceProtectionLayer 含 check_token_budget/check_rate_limit/check_cost_budget/enforce_agent_limits/record_usage 5个方法"
  - "TokenBudget(CostBudget) Pydantic V2 model(session_id, max_tokens, current_usage, limit)"
  - "SlidingWindowRateLimiter: N=100, W=60s"
  - "LLMCostCircuitBreaker: 预算阈值+三级熔断 HALF_OPEN/OPEN/CLOSED"
  - "AIRecursionGuard: 递归深度限制+循环检测"
  - "AgentExecutionProtector: max_steps/max_wall_time/max_memory_mb"
  - "LSGPerformanceBudget: 每层延迟分布(P50<10ms/P95<50ms/P99<100ms) + Github Actions runner 2core 16GB约束"
  - "ModelExtractionDefender: entropy check + output perturbation + MVI监管策略 + 最低IP保护方案"
  - "CostAsymmetryDefender: free intelligence consumption拦截 + 评估类prompt拦截 + reflective_prompt拦截"
  - "SemanticCacheCollisionDefender: Key Salting + HMAC integrity verification"
  - "15条单元测试全部通过"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l5_resource_protection.py
  2. 删除 D:\ZephyrAlpha\tests\llm_security\test_l5_resource_protection.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","resource"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 L5 资源保护层——防止 LLM 资源的滥用、耗尽和成本失控。保护计算资源、API 配额和财务预算不被恶意消耗。

## 触发条件
- TASK-INF-0201 已通过

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §8+§25.4+§40+§50+§54+§58

### 做
1. 实现 `ResourceProtectionLayer` 5个核心方法
2. 实现 Token/速率/成本/递归/Agent执行5个保护器
3. 实现 LSG 性能预算监控 + 模型提取防御 + 成本不对称防御 + 语义缓存防御
4. 编写 15 条单元测试

### 产
- `l5_resource_protection.py` / `test_l5_resource_protection.py`

### 检
```bash
pytest tests/llm_security/test_l5_resource_protection.py -v
```
