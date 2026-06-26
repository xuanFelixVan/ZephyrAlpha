---
module_id: KE-3423
title: 4.2 P0 级：编码损坏 + BOM + 重复 frontmatter（3 个文件）
category: documentation
ttl: permanent
---

# 4.2 P0 级：编码损坏 + BOM + 重复 frontmatter（3 个文件）

4.2 P0 级：编码损坏 + BOM + 重复 frontmatter（3 个文件）

| 文件 | 问题 | 修复方式 |
|------|------|---------|
| `docs/03_blueprints/ex_core/order-management-system-blueprint.md` | BOM 字符 `﻿---` + 双重 frontmatter 块 | `git checkout HEAD -- <file>` 恢复后重写 |
| `docs/03_blueprints/data/market-data-management-blueprint.md` | BOM 字符 `﻿---` + 双重 frontmatter 块 | `git checkout HEAD -- <file>` 恢复后重写 |
| `docs/03_blueprints/risk/volatility-prediction-blueprint.md` | 编码损坏（`standard_type: 楂樺眰鏋舵瀯钃濊浘`） | `git checkout HEAD -- <file>` 恢复 |
