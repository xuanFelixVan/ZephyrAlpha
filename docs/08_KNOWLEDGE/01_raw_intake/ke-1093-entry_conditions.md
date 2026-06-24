---
module_id: KE-1008----------002
status: active
title: 7.2 `entry_conditions` 数组项（每条 check）
category: governance
---

# 7.2 `entry_conditions` 数组项（每条 check）

7.2 `entry_conditions` 数组项（每条 check）

```yaml
- id: G1-C00                           # 必填，格式 /^G[1-5]-C\d{2}$/
  name: no_deprecated_path             # 必填，snake_case 机读 slug（在同 gate 内唯一）
  type: path_blacklist                 # 必填，must ∈ gate_engine 支持的 check_type 列表
  description: "..."                   # 必填，≤ 300 字
  check: "描述性校验逻辑"               # 可选，人类可读检查语义
  severity: error                      # 必填，{error, critical, warning, warn, info}
  on_failure: reject                   # 必填，{reject, auto_fix, flag, defer, auto_assign,
                                       #        auto_register, auto_fill, auto_scope}
  verifiable: true                     # 必填，本检查是否可自动化验证
  verification_method: "..."           # 可选，单元测试说明
  params: {...}                        # 可选，传给 check handler 的参数字典
```
