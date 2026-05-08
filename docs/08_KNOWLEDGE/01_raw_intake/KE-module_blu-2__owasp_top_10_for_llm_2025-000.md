---
module_id: KE-module_blu-2__owasp_top_10_for_llm_2025-000
title: 2. OWASP Top 10 for LLM 2025 完整覆盖矩阵
category: module_blueprint
---

# 2. OWASP Top 10 for LLM 2025 完整覆盖矩阵

2. OWASP Top 10 for LLM 2025 完整覆盖矩阵

| OWASP 风险 | 风险名称 | LSG覆层 | 覆盖策略 |
|:---|------|:---:|------|
| LLM01:2025 | Prompt Injection | L1 + L2 | 直接注入正则检测 + 间接注入RAG/文件检测 + System Prompt隔离 |
| LLM02:2025 | Sensitive Information Disclosure | L2 + L3 + L6 | PII脱敏 + 输出Secret扫描 + 日志脱敏 + 训练数据泄露检测 |
| LLM03:2025 | Supply Chain | L0 | 模型哈希校验 + 依赖安全扫描 + MCP服务器身份验证 + 来源追溯 |
| LLM04:2025 | Data & Model Poisoning | L0 + L7 | 训练数据审计 + 模型完整性校验 + canary输入检测 |
| LLM05:2025 | Improper Output Handling | L3 | Schema验证 + 沙箱代码执行 + XSS/SSRF检测 + 参数化查询 |
| LLM06:2025 | Excessive Agency | L4 | 权限最小化 + Human-in-Loop + 工具参数注入防护 + 操作审计 |
| LLM07:2025 | System Prompt Leakage | L2 | Prompt隔离标记 + 输出echo检测 + 结构试探检测 |
| LLM08:2025 | Vector & Embedding Weaknesses | L1 + L0 | RAG检索内容安全扫描 + 向量库权限隔离 + embedding投毒检测 |
| LLM09:2025 | Misinformation | L3 | 幻觉检测 + 事实核查 + 来源归因 + 不确定性标记 |
| LLM10:2025 | Unbounded Consumption | L5 | Token预算 + 速率限制 + API成本熔断 + Agent执行时长限制 |

---
