---
module_id: KE-1224
status: active
title: 特别条款：临时文件（session garbage）
category: governance_rule
---

# 特别条款：临时文件（session garbage）

特别条款：临时文件（session garbage）

以下前缀文件在每次删除前也 MUST 执行 STEP 3：
- `_temp*` / `_check*` / `_phase_*` / `_audit*`
- 规则：即使它们看起来是"临时"文件，也必须在删除前确认每一行内容不是仅存在于此文件中的有价值数据。
