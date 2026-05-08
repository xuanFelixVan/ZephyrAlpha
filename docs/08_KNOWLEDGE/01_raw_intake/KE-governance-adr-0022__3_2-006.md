---
module_id: KE-governance-adr-0022__3_2-006
title: 四、新模块归属判别决策树（锚定 ADR-0022 §3.2）
category: governance
---

# 四、新模块归属判别决策树（锚定 ADR-0022 §3.2）

四、新模块归属判别决策树（锚定 ADR-0022 §3.2）

每个**新**模块按以下决策树自顶而下判断。若某一步的答案不确定，在 `docs/02_enterprise_architecture/open-questions-register.md` 登记后**不实施**，直到仲裁完成。

```
┌─ Q1：此模块的核心职责是"某条业务流水线的某一阶段"吗？
│    （例如"数据清洗"、"因子计算"、"信号生成"、"风控阈值检查"）
│    ├─ YES → 归入对应 l<NN>_*/ 层（C 轨）
│    └─ NO  → 进入 Q2
├─ Q2：此模块是"服务所有业务层的跨层平台能力"吗？
│    （例如 LLM 安全、向量检索、任务编排、反馈闭环）
│    ├─ NO  → 回到 Q1 重新审视业务归属
│    └─ YES → 进入 Q3
├─ Q3：此能力有"明确、稳定、文档化的业务边界（Bounded Context）"吗？
│    ├─ YES → 创建独立顶级包（B 轨，无 l<NN>_ 前缀，风格如 llm_security/）
│    │         → 同步创建 docs/03_modules/_b_track_interfaces/<name>-interface.md 接口合同
│    │         → 同步创建 KB 决策记录 决策记录（若为跨任务可复用能力）
│    └─ NO  → 进入 Q4
└─ Q4：此能力是"若干业务层共享的小工具、常量、契约、Schema"吗？
     ├─ YES → 归入 shared/ 子目录
     └─ NO  → 在 open-questions-register.md 登记，不实施
```

**关键规则**：
- **前缀 `l<NN>_` 是 C 轨的语法标识**。看到它就意味着"属于 14 层业务脊柱"，反之亦然。
- **B 轨新包创建门槛**：独立顶级包 = BC 边界明确 + 至少 1 份 ADR + 至少 1 份接口合同 + 至少 1 个 Phase 路线。
- **过渡期实现**：某能力 experimental 可先在 C 轨实现（如当前 `kb/`），beta 升级为 B 轨独立包。升级动作需 ADR 记录。

---
