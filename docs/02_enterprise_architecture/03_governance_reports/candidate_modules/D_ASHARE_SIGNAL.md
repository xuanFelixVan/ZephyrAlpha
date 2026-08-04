---
doc_type: audit_report
title: 候选模块清单 — D_ASHARE_SIGNAL
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_ASHARE_SIGNAL 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **2** 条（原有 1 + harvest 1）。
> harvest 去重四态: likely_new=1

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0368 | 模块19 市场体制转换模型（Regime-Switching Model） | 模块19 市场体制转换模型（Regime Switching Model） | D_ASHARE_SIGNAL | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-TESTB-001 | test_trigger_B(测试触发器误登记) | (无)测试触发器,非业务决策模块,无实际功能 | D_ASHARE_SIGNAL | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-04 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### q1 已实现/重复（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-TESTB-001 | test_trigger_B(测试触发器误登记) | (无)测试触发器,非业务决策模块,无实际功能 | D_ASHARE_SIGNAL | 测试触发器非业务功能,无需实现。该节点为错误登记(无blueprint_id+文件不存在) | 无(测试触发器不应为depgraph业务节点) |

### 待评估（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0368 | 模块19 市场体制转换模型（Regime-Switching Model） | 模块19 市场体制转换模型（Regime Switching Model） | D_ASHARE_SIGNAL | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0368 | 模块19 市场体制转换模型（Regime-Switching Model） | D_ASHARE_SIGNAL | 候选待评（candidate） | harvest待评估（likely_new） |
| 2027-08-04 | yearly | CAND-TESTB-001 | test_trigger_B(测试触发器误登记) | D_ASHARE_SIGNAL | 否决（rejected） | rejected,确认测试触发器误登记。test_trigger_B无blueprint_id+文件不存在,非业务模块,不应为depgraph业务节点.与CAND-TESTA-001同类,除非有明确测试需求,否则不再评估 |
