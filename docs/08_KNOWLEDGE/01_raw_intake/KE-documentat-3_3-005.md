---
module_id: KE-documentat-3_3-005
title: 3.3 层级关系与加载策略
category: documentation
---

# 3.3 层级关系与加载策略

3.3 层级关系与加载策略

```
PS-STD-000 元标准宪法（本文件）
  │ 定义"什么进宪法、什么进登记表"
  │ 加载策略：热记忆（Hot Memory，always loaded）
  │
  ├── PS-STD-003 行为边界标准（宪法内容）
  │     ABS-XX 条目：后果不可逆的禁止行为
  │     加载策略：热记忆（CR-010，P0）——始终在系统提示中
  │
  └── PS-REG-001 规则登记表（登记表内容）
        COND-XX：后果可逆的条件禁止
        REC-XX：推荐做法
        CODE-XX：代码级强制规则
        {域代码}-XX：各领域规则索引
        加载策略：领域触发（CR-005，P1）+ 冷记忆（CR-006，P2）

> 注：宪法层 ABS 编号为全局唯一前缀。领域级操作控制原则使用各自领域前缀（如 GOV-DOC-009 用 DOC-001~DOC-008，PS-STD-011 用 MTH-001），与 ABS 编号全局不冲突。详见 `../meta/behavior-boundaries-standard.md`（PS-STD-003）§3.4 编号注册表。
>
> **三层记忆模型**：本项目的加载策略与 Codified Context（arXiv 2602.20478）三层模型一致——热记忆（宪法，always loaded）→ 领域触发（领域规则，按任务加载）→ 冷记忆（知识库，按需检索摘要）。宪法热记忆稳定在 ~400 行以下（社区验证上限），超过此阈值开始降低 AI 遵循度。加载规则的完整定义见 `../operational/vibe_coding/vibe-coding-session-state-runbook.md`（CR-005/CR-006/CR-010/CR-011）。
```

---
