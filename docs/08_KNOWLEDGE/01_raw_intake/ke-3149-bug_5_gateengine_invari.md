---
module_id: KE-3043------invari-003
status: active
title: Bug #5: GateEngine 自检漏掉 invariants/ 子目录
category: session_log
ttl: permanent
---

# Bug #5: GateEngine 自检漏掉 invariants/ 子目录

Bug #5: GateEngine 自检漏掉 invariants/ 子目录
- **位置**: [gate_engine_selfcheck.py](file:///d:/ZephyrAlpha/scripts/governance/gate_engine_selfcheck.py#L217)
- **现象**: S10 一致性检查报 `EN-001/002/003 的 YAML 文件缺失`（假阳性）
- **修复**: glob 列表增加 `_GATES_DIR.glob("invariants/*.yaml")`
