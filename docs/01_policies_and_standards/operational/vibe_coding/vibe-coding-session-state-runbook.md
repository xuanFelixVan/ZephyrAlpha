---
module_id: OPS-VC-002
title: "Vibe Coding Session 状态机规则"
doc_type: operational_rule
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "定义 Vibe Coding Session 的状态机——从启动到结束的完整状态流转规则。"
tags: [vibe-coding, session, state-machine, operational]
rule_form: procedural
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
depends_on:
  - target: PS-STD-009
    at: "§4"
    why: "规则变更门禁——修改本文档的审批流程"
---

# Vibe Coding Session 状态机规则

> module_id: OPS-VC-002 | version: 1.0.0 | status: active | layer: cross_layer
>
> 定义 AI Agent Session 的生命周期状态机，确保所有 Session 遵循统一的状态转换规则。

## 一、状态定义

| 状态 | 说明 | 入口动作 | 出口动作 |
|------|------|---------|---------|
| INIT | Session 已创建，等待任务分配 | 初始化上下文，清空工作记忆 | 记录 Session 启动时间 |
| ACTIVE | Session 正在处理任务 | 获取任务锁，启动 token 计数器 | 保存进度检查点 |
| PAUSED | Session 暂停（用户干预或依赖等待） | 保存上下文快照，释放任务锁 | 重新加载上下文快照 |
| COMPLETED | Session 已成功完成所有任务 | 写入 Session Log，更新流水线追踪器 | 归档 Session 产物 |
| FAILED | Session 因不可恢复错误终止 | 写入错误日志，标记失败原因 | 保留错误上下文供诊断 |

## 二、合法状态转换

| 从 | 到 | 触发条件 | 执行动作 | 优先级 |
|----|-----|---------|---------|--------|
| INIT | ACTIVE | 任务已分配且前置条件满足 | 加载任务上下文，开始处理 | P0 |
| ACTIVE | PAUSED | 用户暂停命令 / 依赖不可用 / token 预算耗尽 | 保存状态，释放资源 | P0 |
| ACTIVE | COMPLETED | 所有任务成功完成 | 写入 Session Log，更新追踪器 | P0 |
| ACTIVE | FAILED | 不可恢复错误发生 | 记录错误，标记 Session 失败 | P0 |
| PAUSED | ACTIVE | 用户恢复命令且依赖可用且 token 预算剩余 | 重新加载上下文，恢复处理 | P1 |
| PAUSED | COMPLETED | 用户取消剩余任务 | 写入部分 Session Log，标注取消 | P1 |
| PAUSED | FAILED | 暂停超时且无法恢复 | 自动标记失败 | P2 |

## 三、禁止的状态转换

| 禁止转换 | 原因 | 替代方案 |
|---------|------|---------|
| COMPLETED → ACTIVE | 已完成的 Session 不可重启 | 创建新 Session |
| FAILED → ACTIVE | 失败的 Session 不可自动恢复 | 创建新 Session 并从错误中学习 |
| COMPLETED → PAUSED | 已完成状态不可回退 | 无需回退 |
| FAILED → PAUSED | 失败状态不可降级 | 无需降级 |

## 四、超时规则

| 状态 | 最大持续时间 | 超时动作 | 优先级 |
|------|------------|---------|--------|
| ACTIVE | 4 小时 | 自动转为 PAUSED，通知用户 | P0 |
| PAUSED | 72 小时 | 自动转为 COMPLETED（部分结果），标记 timed_out | P1 |
| INIT | 30 分钟 | 自动转为 FAILED，报告初始化超时 | P1 |

## 五、异常处理

| 异常类型 | 动作 | 恢复策略 | 优先级 |
|---------|------|---------|--------|
| encoding_error | 暂停 Session，记录错误，通知用户 | 用户必须修复编码后才能恢复 | P0 |
| dependency_not_found | 暂停 Session，加入延迟队列 | 依赖可用时自动恢复 | P1 |
| token_budget_exceeded | 暂停 Session，保存进度检查点 | 用户必须批准额外 token 预算 | P0 |
| unrecoverable_error | 强制转为 FAILED | 无自动恢复，需人工干预 | P0 |

## 六、状态不变量

1. Session 在任意时刻恰好处于一个状态
2. 每个 Session 有唯一的 session_id
3. Session Log 在状态变更后 5 分钟内写入
4. ACTIVE 状态的 Session 持有任务锁
5. PAUSED 状态的 Session 已释放任务锁

## 七、与 YAML 规则的对应

本 Markdown 文档是 `D:\ZephyrAlpha\src\zephyr\rules\session_state_machine.yaml` 的人类可读版本。
YAML 文件是机器可执行的权威来源，本文档是解释性参考。

差异说明：
- YAML 中使用 `idle` 状态，本文档使用 `INIT`（语义相同，命名对齐 ADR-0035 三阶段模型）
- YAML 中有 `archived` 状态，本文档将其归入 `COMPLETED` 的出口动作（归档是完成后的自动行为，非独立状态）

## 八、修改条件

修改本文档需要同时更新以下文件：
1. `D:\ZephyrAlpha\src\zephyr\rules\session_state_machine.yaml`（机器可读版本）
2. `../../_registry/catalogs/document-metadata-index.yaml`（注册表）
3. 任何引用状态机的 ADR 文档

修改通过 `../../meta/rule-lifecycle-and-change-standard.md` 定义的变更门禁。
