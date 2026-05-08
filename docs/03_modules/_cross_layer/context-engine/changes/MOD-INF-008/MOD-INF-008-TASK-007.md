---
task_id: "MOD-INF-008-TASK-007"
task_title: "三级降级策略 + 风险缓解 R1-R5 + 已知限制 R6"
module_id: "MOD-INF-008"
blueprint_section: "§3 三级降级策略 + §9 风险与缓解 R1-R5"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 6
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-002"
    why: "Build 失败触发 VMS 不可用降级"
  - task_id: "MOD-INF-008-TASK-004"
    why: "LSG 拒绝触发 validate 降级"
  - task_id: "MOD-INF-008-TASK-005"
    why: "注入验证触发超时降级"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
tags: ["context-engine", "degradation", "fallback", "risk-mitigation", "resilience"]
acceptance_criteria:
  - "AC-001: VMS 不可用降级：仅注入 AGENTS.md + 当前模块蓝图，session.degraded=true"
  - "AC-002: LSG 拒绝 ≥3 次降级：移除被拒绝块，注入剩余，injection_blocks_removed=N"
  - "AC-003: CE 10s 超时降级：仅硬编码规则，CE_timeout_metric += 1"
  - "AC-004: R1 缓解 (恶意内容进入 LLM): CT-CE-LSG-001 fail-closed, LSG 不可用→拒绝注入"
  - "AC-005: R2 缓解 (Token 预算耗尽): L1→L2→L3 渐进 + DocCompressor 压缩"
  - "AC-006: R3 缓解 (过时 KE 主导): Freshness Decay + TTL=90 天标记 legacy"
  - "AC-007: R4 缓解 (VMS 不可用): embedded_defaults→硬编码基础上下文"
  - "AC-008: R5 记录 (3 核心文件未实现): construction_progress=phase_1_partial 正确标注"
  - "AC-009: R6 标注 (AI 评估 AI 评分回声室): 在 risk_register 中记录为跨供应商治理问题"
rollback_instructions: "恢复 context_assembler.py/context_injector.py 中降级相关代码，还原 risk_register 条目"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §3, §9"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-007: 三级降级策略 + 风险缓解

## 1. Purpose

实现 Context Engine 的三级降级策略和风险缓解机制，确保在任何故障模式下 CE 不会完全失败——总能向 Agent 提供最少可用的上下文。

## 2. Three-Tier Degradation Strategy (§3)

| 情况 | 降级行为 | 标记 |
|------|------|------|
| **VMS 不可用** | 仅注入 AGENTS.md + 当前模块蓝图 | `session.degraded=true` |
| **LSG 拒绝 ≥3 次** | 移除被拒绝块，注入剩余 | `injection_blocks_removed=N` |
| **CE 10s 超时** | 降级注入—仅硬编码规则 | `CE_timeout_metric += 1` |

## 3. Risk Mitigation (§9)

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | 恶意内容通过 CE 进入 LLM | 中 | 极高 | CT-CE-LSG-001 fail-closed: LSG 不可用→拒绝注入 |
| R2 | Token 预算耗尽→模型截断 | 中 | 高 | L1→L2→L3 渐进 + DocCompressor 压缩 |
| R3 | 过时 KE 主导最新经验 | 中 | 高 | Freshness Decay + TTL=90 天标记 legacy |
| R4 | VMS 不可用→上下文空洞 | 低 | 高 | embedded_defaults→硬编码基础上下文 |
| R5 | 3 核心文件未实现 (vector_bridge 等) | 已知 | — | construction_progress=phase_1_partial, beta 补 |

## 4. Known Limitation: R6

AI 评估 AI 的评分回声室——CEEval 的 LLM-as-judge 与 Compressor LLM 共享架构偏见。终极解法需异源评估模型（如 Claude 评 Qwen 的输出），属跨供应商治理。

## 5. Acceptance Criteria

- VMS 不可用时：build() 返回仅含 embedded_defaults 的 RawContext
- LSG 3 次拒绝后：validate() 返回 ValidatedContext(blocks_removed=N)
- CE 处理超 10s：inject() 返回仅 hardcoded_rules 的 InjectionResult
- 所有降级场景记录到 events 表
- risk_register.yaml 包含 R1-R6 条目
