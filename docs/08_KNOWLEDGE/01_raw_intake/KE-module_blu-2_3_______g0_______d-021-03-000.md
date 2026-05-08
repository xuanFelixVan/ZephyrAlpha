---
module_id: KE-module_blu-2_3_______g0_______d-021-03-000
title: 2.3 回滚后仅跑 G0 门禁（决策 D-021-03）
category: module_blueprint
---

# 2.3 回滚后仅跑 G0 门禁（决策 D-021-03）

2.3 回滚后仅跑 G0 门禁（决策 D-021-03）

> **决策 D-021-03（不变）**：回滚后只跑 G0 门禁（文件存在性 + YAML 语法），不跑全量门禁（G1-G7）。补充：回滚后额外清理 `__pycache__` 避免 bytecode 缓存不一致（B16）。v0.5.0 追加：Differential Check 逐行比较回滚前后的 DB 状态，检测非对称差异（B53）。

```yaml
post_rollback_verification:
  gate_level: "G0 only"
  pre_gate_cleanup:
    - "find {project} -name '__pycache__' -type d -exec rm -rf {} +"
  checks:
    - "文件存在性——回滚后的文件是否都在"
    - "YAML 语法——关键 YAML 文件是否可解析"
    - "import 可达性——Python 文件是否可 import"
    - "DB 一致性——tasks 表状态与文件状态是否对齐"
  skip:
    - "G1-G7 门禁——留给下一次正常 commit"
    - "pytest——留给下一次正常 commit"
    - "ruff——留给下一次正常 commit"
  rationale: "回滚到上一次成功 commit = 恢复到已验证状态，G0 足以确认完整性"
```
