---
module_id: KE-899
status: active
title: 4.2 禁止的导入
category: governance
ttl: permanent
---

# 4.2 禁止的导入

4.2 禁止的导入

- `import *` — 破坏静态分析，永远禁止
- 下层导入上层 — 违反分层架构（L02 不可 `from zephyr.L03 import ...`）
- 循环导入 — 在 CI 阶段由 `import-linter` 检测
- 裸 `dict[str, Any]` 作为跨模块参数 — 使用冻结 dataclass/Pydantic 替代

---
