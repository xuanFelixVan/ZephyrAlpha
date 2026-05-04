---
module_id: ADR-0014
doc_type: adr
title: 模块准入铁律
version: 1.0.0
status: active
date: '2026-04-22'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0013
- ADR-0021
- ADR-0022
priority: P0
phase: Phase-0
layer: cross_layer
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-22'
superseded_by: null
supersedes: null
related_rationale: ""
related_open_questions: []
tags: [adr, vibe-coding]
summary: "模块准入铁律（MOD-P1~P4 四级筛选 + INJ-001~006 六条铁律）"
---

# ADR-0014: 模块准入铁律

**状态**：Accepted
**日期**：2026-04-22
**决策者**：ZephyrAlpha-Owner

---

## 背景

ZephyrAlpha 2.0 的候选池中有 1,000+ 个候选模块，如果没有明确的准入标准，AI 模型会将所有候选模块全部注入到 architecture-model/，导致：

1. 架构图爆炸（老树教训：候选池 1,356 个全塞进去）
2. AI 决策 paralysis（模块太多，AI 无法判断优先级）
3. 依赖图复杂度指数级增长
4. 接口契约无法全部定义，导致幻觉补全

## 决策

采用 **MOD-P1~P4 四级筛选标准**，只有通过所有四级筛选的模块才能注入 architecture-model/。

## 四级筛选标准

### MOD-P1：架构必要性

**问题**：该模块是否在 architecture-model/ 的 14 层中有明确的层归属？

- **通过条件**：是，且层归属唯一（不跨层）
- **失败处理**：拒绝，该模块不属于当前架构范围，放入候选池等待架构扩展

### MOD-P2：Phase 相关性

**问题**：该模块是否在当前 Phase 中需要注入？

- **通过条件**：是，且在 P0/P1 优先级列表中（P2/P3 模块延迟注入）
- **失败处理**：延迟，放入候选池等待后续 Phase

### MOD-P3：依赖完整性

**问题**：该模块的所有依赖模块是否已注入或已在注入计划中？

- **通过条件**：是，依赖链完整，不存在"依赖一个尚未存在的模块"的情况
- **失败处理**：延迟，等待依赖模块先注入

### MOD-P4：接口可定义性

**问题**：该模块的接口是否可以被明确定义（不需要幻觉补全）？

- **通过条件**：是，接口来源于已有文档、老树蓝图或 Owner 明确说明
- **失败处理**：暂停，等待接口定义完成后再注入

## 注入前的 6 条铁律

通过四级筛选后，注入前还必须通过 6 条铁律检查（详见 `governance/module/module-injection-rules.yaml`，GOV-MOD-005）：

1. **INJ-001**：模块 ID 在 module-id-registry.yaml 中唯一注册
2. **INJ-002**：depends_on 中的所有模块 ID 存在
3. **INJ-003**：P0 模块的接口契约已在 cross-layer-contracts.yaml 中定义且 frozen
4. **INJ-004**：模块 status 字段是合法值
5. **INJ-005**：模块有 runtime_plane 归属
6. **INJ-006**：P0 模块已关联至少一个 ADR

## 后果

**正面影响**：
- 防止候选池全量注入导致架构爆炸
- 确保每个注入的模块都有明确的层归属和接口定义
- 减少 AI 幻觉补全的机会

**负面影响**：
- 部分有价值的模块可能被延迟注入
- 需要维护候选池和注入计划的同步

**缓解措施**：
- 候选池中的延迟模块保留完整的设计信息，不丢失
- 每个 Phase 结束后重新评估候选池中的延迟模块

## 相关文件

- `governance/module/module-injection-rules.yaml`（GOV-MOD-005）：6 条铁律的详细定义
- `module-id-registry.yaml`：模块 ID 注册表
- `cross-layer-contracts.yaml`：跨层契约定义
