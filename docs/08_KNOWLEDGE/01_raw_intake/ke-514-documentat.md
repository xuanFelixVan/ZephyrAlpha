---
module_id: KE-463
status: active
title: 6.3 具体实施
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 6.3 具体实施

6.3 具体实施

**L1（已有）**：

- `.env` 在根目录 `.gitignore`（5 行规则）
- `docs/.env.example` 提供占位模板
- `.cursor/rules/encoding-tool-guard.mdc` 禁止 agent 写 `.env` 文件

**L2（P0 待建）**：

- `scripts/hooks/git-secrets-setup.sh`（experimental 新增）
- 规则模式：`AKIA[0-9A-Z]{16}` / `sk-ant-*` / `sk-proj-*` / 自定义 `ZEPHYR_SECRET_*`
- CI 侧 `trufflehog` 扫描 git 全历史

**L3（已有 → LSG 接口）**：

- LSG Output Validator 内置 25+ 正则（LLM API Key / JWT / Private Key 等）
- 触发立即返回 `degraded=True` + 拒绝输出 + FLE 上报 anomaly

**L3-Audit（experimental 每周）**：

- `scripts/governance/scan_secret_leak.py` — 全库扫描 + 对比历史快照
- Finding 写 `docs/09_audit/findings/secret-leak-*.md`
