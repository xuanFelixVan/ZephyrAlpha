---
blueprint_id: MOD-INF-005
ttl: permanent
doc_type: index
---

# 蓝图读取遥测（`blueprint_reads.jsonl`）

本目录下的 `blueprint_reads.jsonl` 为 **G6 蓝图合规与遥测门禁**所用：每行一条 JSON，`event` 为 `blueprint_read` 时需含 `blueprint_id` 等字段。

仓库中仅保留 **少量示意行**，避免把完整仿真产出拖入版本库。

需要完整或追加数据时，运行：

```bash
python scripts/governance/session_simulator.py
```

（参数以该脚本 `--help` 为准；写入模式为追加。）
