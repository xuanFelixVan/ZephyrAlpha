---
module_id: KE-980
title: 6.2 脚本退出码
category: governance
---

# 6.2 脚本退出码

6.2 脚本退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 扫描通过，无残留 |
| 1 | 存在可自动清理的残留（需 `--clean`） |
| 2 | 存在需人工判定的 VALID_FILE 残留 |
| 3 | 产出物不在 deliverables 内 |
