---
module_id: KE-2428-------------must-002
title: 7.2 核心条款速查（本蓝图仅列MUST项）
category: module_blueprint
ttl: permanent
---

# 7.2 核心条款速查（本蓝图仅列MUST项）

7.2 核心条款速查（本蓝图仅列MUST项）

| 条款ID | 维度 | 要求 | 类型 |
|--------|------|------|:--:|
| ENC-001 | 编码安全 | 脚本文件必须是 UTF-8 | MUST |
| ENC-002 | 编码安全 | `sys.stdout.reconfigure(encoding='utf-8')` | MUST |
| ENC-003 | 编码安全 | Python `open()` 必须 `encoding='utf-8'` | MUST |
| SC-001 | 自身一致 | 脚本内部路径必须绝对路径 | MUST |
| SC-002 | 自身一致 | docstring 覆盖"参数/返回值/副作用" | MUST |
| SC-007 | 自身一致 | shebang `#!/usr/bin/env python3`（Unix兼容） | MUST |
| SC-005 | 自身一致 | 脚本不能自己修改自己的源码 | MUST |
| INT-001 | 集成接口 | 遵守四档退出码约定（0/1/2/3） | MUST |
| INT-002 | 集成接口 | 捕获所有异常，转为 exit 3 | MUST |
| INT-003 | 集成接口 | `--warn-only` 参数 → exit 0/1 | MUST |

完整条款列表见 `quality-standard.md`。
