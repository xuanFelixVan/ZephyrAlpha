---
module_id: KE-3585
title: 4.2 Step 2：临时文件清除
category: governance
---

# 4.2 Step 2：临时文件清除

4.2 Step 2：临时文件清除

以下模式的文件必须在同一 session 内删除：

| 模式 | 示例 | 处置 |
|------|------|------|
| `temp_*` | `temp_scan_result.json` | 删除 |
| `*.backup` | `schemas.py.backup` | 删除 |
| `*-v2.*` / `*-v3.*` / `*-round2.*` | `config-v2.yaml` | 删除（版本历史用 git） |
| `__pycache__/` | 任何 `__pycache__/` 目录 | 删除 |
| `*.pyc` | 编译缓存 | 删除 |
| `tmp_*` 脚本 | `tmp_replace_composer.py` | 删除 |
| `ttl: session` 的文件 | session 内临时工具 | 删除 |
