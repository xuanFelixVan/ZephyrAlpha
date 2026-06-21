---
module_id: "GOV-AI-002"
title: "模型路由策略 — DeepSeek V4 Pro 主力 + GLM 审查 + Claude 特种"
doc_type: policy
status: active
version: "2.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: periodic_review_90d
summary: "ZephyrAlpha AI 模型路由策略 v2.0.0。核心变更：① 取消 Claude 终审角色（drafts-audits-arbitration-protocol.md 已于2026-05-01废除）；② DeepSeek V4 Pro 升为主力施工模型；③ GLM 承担深度审查职责；④ Claude 降格为特种救援——仅用于 DeepSeek+GLM 都搞不定的极难任务和关键代码审查。路由决策基于 REG-LLM-001 基准排名数据。"
supersedes: ["GOV-AI-002 v1.0.0"]
tags: [model-routing, strategy, deepseek-v4-pro, glm, claude, cost-optimization, task-assignment]
depends_on:
  - {target: REG-LLM-001, at: "全篇", why: "模型基准排名——路由策略的数据依据"}
references:
  - {id: "MOD-INF-006", at: "§12.3", why: "M模块分工与任务模型对齐（语义引用，不设为 depends_on DAG 上游）"}
  - {id: "TEMPLATE-TASK-001", at: "全篇", why: "assigned_model 字段定义"}
---

# 模型路由策略 v2.0.0

> module_id: GOV-AI-002 | version: 2.0.0 | status: active

> ⚠️ v2.0.0 重大变更：Claude 不再是终审法官——改为特种救援。DeepSeek V4 Pro 入列为主力。

---

## 一、模型角色分配

| 角色 | 模型 | API 成本 | 场景 |
|------|:---:|:---:|------|
| **主力施工** | DeepSeek V4 Pro | $1.74/$3.48 per M | 日常编码、代码生成、架构实现——A区 M1-M4、B区 M6/M8/M9/M10/M11 |
| **深度审查** | GLM-5.1 | Trae CN 免费 | B区 M7——逐个文件深度审查逻辑/合规/质量；A区 M5——产出物打包 |
| **特种救援** | Claude Opus 4.7 | $5/$25 per M | ① DeepSeek + GLM 都搞不定时；② Owner 标记为"关键"的任务的最后审查 |

### 角色决策依据（基于 REG-LLM-001 基准数据）

| 维度 | DeepSeek V4 Pro | GLM-5.1 | Claude Opus 4.7 | 结论 |
|------|:---:|:---:|:---:|------|
| 代码能力 | 9.0 | 8.2 | 10 | DeepSeek 主力生产——能力强、性价比高 |
| 幻觉控制 | **4.5** | 8.5 | **10** | DeepSeek 不可信——必须 GLM 审查其产出 |
| 中文能力 | 9.0 | 9.0 | 7.5 | 中文场景 DeepSeek+GLM 双保险 |
| 性价比 | 8.5 | 8.5 | 3.0 | Claude 太贵——不能日常使用 |
| 综合 | 7.8 | 7.7 | 8.4 | Claude 最强但最贵——只能在刀刃上用 |

> **核心逻辑**：DeepSeek 能力强但不可信（幻觉率 94%）→ 需要 GLM 审查纠错（幻觉率 ~4%）→ 最关键部分再请 Claude 兜底（幻觉率 ~0.8%）。三层防御，逐级递增成本与可信度。

---

## 二、任务分配决策树

```
收到一张任务卡
     ↓
① assigned_pipeline = "C"（横切）？
  └─ 是 → 分配给脚本系统（MOD-INF-005，不在本策略范围）
     ↓ 否
② task_id 在 Claude 关键任务清单中？
  └─ 是 → assigned_model = "claude"
     ↓ 否
③ assigned_pipeline = "A"（生产）？
  ├─ M1-M4（代码/文档生成）→ assigned_model = "deepseek"
  └─ M5（格式化打包）       → assigned_model = "glm"
     ↓
④ assigned_pipeline = "B"（审计）？
  ├─ M7（深度审查）         → assigned_model = "glm"
  └─ M6/M8/M9/M10/M11      → assigned_model = "deepseek"
     ↓
⑤ DeepSeek 执行失败 → 自动触发 Claude 救援
   └─ 原因："模型能力不足" / "产出物连续3次未通过审计"
```

---

## 三、Claude 特种救援触发条件

Claude 在以下任一条件满足时被触发——**不是每个任务都用 Claude**：

| 触发条件 | 判定标准 | 示例 |
|---------|---------|------|
| **DeepSeek 执行失败** | `execute_pipeline()` 返回 `MODULE_TIMEOUT` 或 `ARTIFACT_FORMAT_ERROR` 连续 3 次 | DeepSeek 反复改不对一个核心算法 |
| **GLM 审查连续驳回** | G7 门禁不通过 ≥ 2 次——GLM 审查发现 DeepSeek 产出有结构性缺陷 | DeepSeek 生成的代码存在架构级错误 |
| **Owner 标记为"关键"** | 任务卡 `priority = "P0"` 且 title 含 "核心" / "关键" / "架构" / "安全" | "实现数据库迁移脚本——涉及不可逆 Schema 变更" |
| **安全敏感任务** | `tags_fn` 含 "security" 或 `tags_mo` 含安全相关模块 | "实现用户认证中间件" |
| **新领域探索** | `tags_st = "experimental"` ——全新领域，DeepSeek 可能缺乏相关知识 | "集成第三方支付 SDK——项目首次使用" |

---

## 四、降级与容灾

| 场景 | 操作 | 备注 |
|------|------|------|
| DeepSeek V4 Pro API 不可用 | 降级到 GLM-5.1（全部任务） | GLM 在 Trae CN 上免费——作为 fallback |
| GLM-5.1 不可用（Trae CN 故障） | 降级到 DeepSeek V4 Pro + 追加 Claude 审查 | 降级链路：GLM审查→DeepSeek自行审查→Claude兜底 |
| Claude API 不可用 | 跳过 Claude 环节——Owner 人工审查 | Claude 不可用时不阻塞任务——标记需要人工复查 |
| 所有模型不可用 | 暂停任务管线 + 通知 Owner | 极端情况——任务卡全部标记 blocked |

---

## 五、变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-02 | 2.0.0 | **重大重写**：① Claude 终审角色取消——降格为特种救援；② DeepSeek V4 Pro 从"未开通"升为主力施工；③ GLM 承担深度审查职责（B区 M7）；④ 基于 REG-LLM-001 基准数据重新验证分工合理性；⑤ 新增 Claude 触发条件清单与降级容灾方案 |
| 2026-04-23 | 1.0.0 | 初始版本——Claude 终审 + Composer 2 主力 + GLM/Kimi/Qwen 免费批量 |
