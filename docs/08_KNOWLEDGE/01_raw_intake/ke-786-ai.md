---
module_id: KE-709
status: active
title: 10. AI 可消费性声明
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 10. AI 可消费性声明

10. AI 可消费性声明

> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档。

**AI 可直接执行的状态机规则**：
- MLC-001 转换表（§5）→ 8×8 状态转换矩阵，可机械化检查
- MLC-002 反向转换限制 → 除 suspended→active 和 testing→in_dev 外，所有反向禁止
- MLC-003 退役步骤 → 7 步流程，每步可检查和记录
- status 受控枚举值 → 8 个合法值（planned/in_design/in_dev/testing/active/suspended/deprecated/archived）

**需人类判断的规则**：
- planned→in_design：需 Owner 审批模块设计可行性
- testing→active：需 Owner 审批 + 集成测试通过
- 退役延期：需 Owner 书面批准，最长再延 90 天

**最小必读路径**（全新 AI session）：
1. §1 目的与范围 → 知道管辖范围
2. §2 SSoT 声明 → 知道本文档权威边界
3. §3 受控枚举 → 知道 `status` 的 8 个合法值
4. §5 生命周期阶段 → 知道 8 个阶段和 MLC-001 转换表
5. §7 退役流程 → 知道 MLC-003 7 步步骤

**Token 预算**：本文档约 1700 字（含 frontmatter），单次读取 ≤ 2500 tokens。
