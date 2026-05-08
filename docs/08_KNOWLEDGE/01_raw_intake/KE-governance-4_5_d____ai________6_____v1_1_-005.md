---
module_id: KE-governance-4_5_d____ai________6_____v1_1_-005
title: 4.5 D 家族：AI 治理基础设施（6 个）· v1.1.0 新增（J0-sync）
category: governance
---

# 4.5 D 家族：AI 治理基础设施（6 个）· v1.1.0 新增（J0-sync）

4.5 D 家族：AI 治理基础设施（6 个）· v1.1.0 新增（J0-sync）

> D = Defense / Data-Intelligence / Decision。6 个**超越 A/B/C/VB 分类**的 AI 治理新系统——"给 AI 员工准备的办公场所 + 保密室 + 情报部 + 决策核心"。与原 39 系统不冲突、不重叠。
>
> **Runtime Plane 列**（R69/J1 批次）：09-GOV 治理维度（主层/次层）与 04bis 执行维度（Plane）正交独立，详见 §1.2bis。

| ID | 系统名 | 主层 | 次层 | Runtime Plane | 激活 | 源 OQ | 代码归属 |
|---|---|---|---|---|---|---|---|
| **D-01** | **AISG 防泄密（AI Security Gateway）** | **全三层** | — | Warm 主 + `security_gateway` Hot-adj + Factory Cold | **OQ-081 硬闸门（Sprint 0 前 P0）** | OQ-076 | `l10_compliance/ai_security/` |
| **D-02** | **Scout Agent（AI 情报员）** | Runtime | (Policy 白名单 / Factory scraper) | Cold（每日 cron） | Sprint 9 简易→11+ 完整 | OQ-079 | `l11_ml_platform/scout/` |
| **D-03** | **Decision Engine**（占位）| Runtime | — | Warm | K2 批次 | OQ-080 | `l08_human_ai_interface/` |
| **D-04** | **Capital Allocation Engine**（占位，G2 最高）| Runtime | — | Warm 主 + Cold 回测 | K2 批次 | OQ-080 | `l05_portfolio_construction/` |
| **D-05** | **Failure Learning Engine**（占位，G3 最后）| Runtime | — | Cold 主 | K2 批次 | OQ-080 | `l10_compliance/` + KMS L5 |
| **D-06** | **Market Regime Engine**（占位，G4 第二）| Runtime | — | Warm 主 + Cold 训练 | K2 批次 | OQ-080 | `l09_research_innovation/` |

**D 家族与原 39 系统关系**：独立分类（AI 治理基建层 vs 业务治理）；共享三层边界方法论；D-01 与 B-01 正交（B-01=治理治理 vs D-01=防泄密）；D-01 是 VIB-03 上游（先脱敏再调度）；D-01 audit ≠ VIB-14（数据流审计 vs 业务决策审计）。

**D-01 AISG 全三层展开**：Policy（`ai_security_gateway_policy.md` + `.cursorignore` + `.cursorrules`）→ Factory（`compile_desensitize_rules.py`）→ Runtime（`l10_compliance/ai_security/` 六大模块 + `aisg/audit_log.jsonl`）。

**D-02 Scout 全三层展开**：Policy（`scout_agent_whitelist.md`）→ Factory（`compile_scraper.py`）→ Runtime（`l11_ml_platform/scout/` + `kms/daily_digest/` + **强制走 AISG**）。
