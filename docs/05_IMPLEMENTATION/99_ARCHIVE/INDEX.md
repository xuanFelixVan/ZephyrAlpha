---

module_id: 99_ARCHIVE_INDEX_001

version: 1.0.1

status: Active

created_date: 2026-04-07

last_updated: '2026-04-11'

owner: 文档管理团队

responsibility:

  - 提供 99_ARCHIVE 目录索引

standard_type: 专业量化机构索引

applicable_scope: 99_ARCHIVE

layer: layer_05
---




# 99_ARCHIVE 索引



> **目录职责**: 实施层历史文档与已下线材料的只读归档入口

> **文档数量**: 4 个 Markdown（本目录无单独 `README.md`）

> **最后更新**: 2026-04-11



```
```---
```



## 上级与接力



- [05_IMPLEMENTATION 索引](../INDEX.md)

- 全仓库文件治理任务清单 §7

- 治理工具总索引

- [09_AUDIT STATE 索引](../../09_AUDIT/STATE/INDEX.md)



### 索引健全性与目录体量（P5 §7）



- **零入链扫描（最新）**：../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260502.md（`scan_index_health.py --prefix docs/05_IMPLEMENTATION/99_ARCHIVE --date 20260502`；**zero_inbound=0**；候选 md **4**；首轮 **`INDEX.md`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../INDEX.md) 显式补链后复跑归零）

- **rollup（深度 3 前缀条数）**：../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md（检索 `docs/05_IMPLEMENTATION/99_ARCHIVE` **4** 条）



```
```---
```



## 📋 文档列表



| 文档 | 说明 | 状态 |

|------|------|------|

| migration_guide_v1.md | 迁移指南（v1） | Active |

| MODULE_ARCHIVE.md | 模块归档说明 | Active |

| SECURITY_BLUEPRINT.md | 安全蓝图（归档稿） | Active |



```
```---
```



## 📝 维护记录



| 日期 | 操作 | 操作人 | 备注 |

|------|------|--------|------|

| 2026-04-07 | 创建索引 | Round2 Fixer | 自动生成索引 |

| 2026-04-11 | P5 §7 门面与入链 | 文档治理 | 双 YAML、机器产出互指、父级 `05_IMPLEMENTATION/INDEX` 挂载 |

<!-- orphan-link -->
- [migration-guide-v1](migration-guide-v1.md)

<!-- orphan-link -->
- [module-archive](module-archive.md)

<!-- orphan-link -->
- [security-blueprint](security-blueprint.md)
