---
module_id: KE-038----------audit-script-enco-005
status: active
title: 6.7 审计脚本编码铁律（Audit Script Encoding Rule）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 6.7 审计脚本编码铁律（Audit Script Encoding Rule）

6.7 审计脚本编码铁律（Audit Script Encoding Rule）

所有审计/校验脚本必须在文件开头添加 UTF-8 输出强制声明，防止 Windows 下 GBK 编码导致 emoji/中文写入 crash。

```python
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

- **影响范围**：所有 `scripts/governance/` 下的新脚本
- **专业参考**：PEP 540 → UTF-8 Mode / Python Windows 编码地狱 → 默认 GBK 输出导致 `UnicodeEncodeError`
- **通俗解释**：Windows 终端默认编码是 GBK，遇到 emoji 就直接崩溃。加这 2 行代码强制输出 UTF-8，跟修水管一样——活不大但不修就漏水
