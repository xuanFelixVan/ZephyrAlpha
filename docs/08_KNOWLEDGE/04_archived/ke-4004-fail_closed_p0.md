---
module_id: KE-3851
title: 12.5 Fail-closed P0（**关键**）
category: module_blueprint
---

# 12.5 Fail-closed P0（**关键**）

12.5 Fail-closed P0（**关键**）

| # | 用例 | 预期 |
|:-:|------|------|
| P0-FC-1 | 规则文件损坏启动 | mode=fail_closed，所有 validate_input allow=False |
| P0-FC-2 | schema 未注册 | validate_output allow=False（默认） |
| P0-FC-3 | secret 扫描器异常 | validate_output allow=False，DEGRADE-SEC-003 |
| P0-FC-4 | fail-closed 下 bypass 尝试 | 任何请求拒绝，不存在放水 |
