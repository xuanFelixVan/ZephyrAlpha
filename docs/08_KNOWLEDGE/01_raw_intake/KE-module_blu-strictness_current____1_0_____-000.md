---
module_id: KE-module_blu-strictness_current____1_0_____-000
title: strictness.current <  1.0（开发时放松）：警告 + allow=True + 记审计
category: module_blueprint
---

# strictness.current <  1.0（开发时放松）：警告 + allow=True + 记审计

strictness.current <  1.0（开发时放松）：警告 + allow=True + 记审计
```

**默认走 fail-closed**。宽松模式（`strictness=0.8`）只在本地开发且调用方显式 opt-in。

**DEGRADE-SEC-003：secret 扫描器挂**

触发场景：`detect-secrets` 库异常 / OOM

降级动作：**fail-closed**，`validate_output` 返回 `allow=False, reason='secret_scanner_failed'`。
