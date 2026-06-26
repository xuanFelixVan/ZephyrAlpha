---
module_id: KE-2267
title: 5. OWASP LLM Top 10（2026.03）对齐矩阵
category: module_blueprint
ttl: permanent
---

# 5. OWASP LLM Top 10（2026.03）对齐矩阵

5. OWASP LLM Top 10（2026.03）对齐矩阵

| OWASP 项 | 描述 | LSG 应对手段 | 配套组件 |
|---------|------|-------------|---------|
| LLM01 Prompt Injection | 恶意输入劫持指令 | **L1 分类 + L2 隔离 + L3 Schema** | Agent Sandbox（双层） |
| LLM02 Sensitive Info Disclosure | 凭据/PII 泄漏 | **L4 secret 扫描 + redact** | detect-secrets / git-secrets |
| LLM03 Supply Chain | 恶意依赖 / 模型 | pre-commit `pip-audit` + `safety` | 供应链 Hook |
| LLM04 Data/Model Poisoning | 训练/检索数据污染 | VMS 入库需经 LSG `validate_input`（trusted）；签名校验 | VMS |
| LLM05 Improper Output Handling | 输出执行 | **L3 Pydantic + L4 命令/URL 扫描** | Orchestrator Sandbox |
| LLM06 Excessive Agency | Agent 越权 | **L3 工具调用 schema**（extra='forbid'）+ Sandbox 白名单 | Orchestrator |
| LLM07 System Prompt Leakage | 系统提示泄漏 | L4 `secret_hints` 扩展 system prompt 特征识别 + 拒绝回显 | L4 |
| LLM08 Vector/Embedding Weakness | 向量库中毒 | VMS 写入需 LSG 过滤 + Collection 隔离 + quarantine | VMS / FLE |
| LLM09 Misinformation | 幻觉 | 不由 LSG 独治，由 Feedback Loop + 人工 review | FLE |
| LLM10 Unbounded Consumption | 资源耗尽 | Orchestrator 沙箱 max_memory/max_cpu + LSG token rate-limit | Orchestrator |

---
