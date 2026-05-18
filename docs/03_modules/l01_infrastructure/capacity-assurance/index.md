---

doc_type: index
status: active
generated: '2026-05-03'
blueprint_id: DOM-GOV-001
---


# Capacity Assurance — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**l01_infrastructure 层模块 — capacity assurance**。

## 文件清单

| 文件 | 说明 | 版本 |
|------|------|------|
| blueprint.md | 模块蓝图（唯一真源） | v2.1.0 |
| delivery/construction-plan-v3.1-archived.md | 历史施工图档案（已归档，内容已合并至 blueprint.md） | v3.1 |
| delivery/index.md | delivery 目录索引 | — |

## 蓝图核心能力（v2.1.0）

| # | 能力 | 对标 |
|---|------|------|
| 1 | SSoT 校验 | — |
| 2 | 容量 SLO + Error Budget（五级） | Google SRE Workbook |
| 3 | AI 审计守卫 | — |
| 4 | 多级 Token Budget | AI Agent Rate Limiting |
| 5 | Kill Switch + Sandbox | AI Agent Observability |
| 6 | Graceful Degradation + 语义缓存 | AI Agent Cost Crisis |
| 7 | 灾难恢复（DR）策略 | ITIL Service Continuity |
| 8 | 容量预测模型 | ITIL Capacity Management |
| 9 | 跨模块集成设计 | ITIL Service Integration |

## 排除规则（不应放入本目录的内容）

- ❌ 其他模块文档 → `../`

## 父级目录

- 父级：[l01_infrastructure](../index.md)