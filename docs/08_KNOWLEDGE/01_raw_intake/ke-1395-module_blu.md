---
module_id: KE-1306
status: active
title: 1.1 缺口 → 原因 → 解法
category: module_blueprint
---

# 1.1 缺口 → 原因 → 解法

1.1 缺口 → 原因 → 解法

**缺口（SEC-01）**：AI IDE（Cursor / Trae / Claude-Desktop）直接暴露给外部文档、网页、邮件等不可信输入，存在 Prompt Injection 风险，可能劫持 Agent 执行危险动作（删代码、泄凭据、访问外部 URL）。

**原因**：
1. 老方案把"Prompt 安全"交给 LLM 本身防御——LLM 的对齐训练在适应性攻击面前胜率 < 50%
2. 没有系统 Prompt 与用户输入的显式隔离，LLM 无法分辨"指令"与"数据"
3. 输出没有 Schema 约束，攻击者能让 LLM 生成意外结构（调用未授权工具）
4. 供应链（pip 包、git-secrets）扫描缺失

**解法**（四层防护 + 双层与沙箱）：
- **L1 输入分类**：MCP 前置拦截，按来源打标（trusted/untrusted），分类喂给 LLM
- **L2 System Prompt 隔离**：Trusted system prompt 与 untrusted user data 强分离格式（XML/JSON 包裹）
- **L3 输出 Schema 验证**：Pydantic v2 强制校验 LLM 工具调用参数
- **L4 异常模式检测**：运行时扫描响应中的异常模式（外部 URL / 高危命令 / 凭据形式）
- **与 Agent Sandbox（KBG-0018）双层**：L1-L4 失守后沙箱兜底，反之亦然
