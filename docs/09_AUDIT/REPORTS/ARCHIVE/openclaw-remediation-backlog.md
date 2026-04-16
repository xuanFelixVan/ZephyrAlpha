---
module_id: OPENCLAW_REMEDIATION_BACKLOG
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: REPORTS
---









# OpenClaw 整改 Backlog（仅建议，不执行改库）



> **run_id**: OPENCLAW_20260408_033500

> **生成时间**: 2026-04-08

> **说明**: 本文件仅列出建议动作，不执行任何修改。所有修改须在 Git 备份后执行。



```
```---
```



## P0 — 必须立即处理



| # | 问题 | 影响范围 | 建议动作 | 涉及路径 |

|---|------|----------|----------|----------|

| P0-1 | 根目录 16 个 temp_*.md 编码损坏 | 16 篇 | 编码修复后归档至 `docs/06_ARCHIVE/temp_pending/` 或确认正式路径已有替代后删除 | `temp_*.md` |

| P0-2 | 双 YAML 头 | 1964 篇 (70%) | 编写脚本合并双 YAML 头，保留最新/最完整的块，删除重复字段 | 全库 |

| P0-3 | `[模块ID]` 占位符未替换 | 10 篇 | 逐一替换为实际 module_id | 见 module_id_duplicates_detail.md |

| P0-4 | audit_state 双副本 | 345 篇 | 合并 04_OPERATIONS/audit_state 与 07_OPERATIONS/audit_state 为统一位置 | `docs/05_IMPLEMENTATION/*/audit_state/` |

| P0-5 | 蓝图无效链接（双重路径） | 5 篇蓝图 | 修正链接从 `05_IMPLEMENTATION/...` 改为 `./...` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` |



## P1 — 应在下一轮整改中处理



| # | 问题 | 影响范围 | 建议动作 | 涉及路径 |

|---|------|----------|----------|----------|

| P1-1 | module_id 重复（238 组） | ~500 篇 | 审计报告分配唯一 ID（加时间戳）；归档副本加 `_ARCHIVED` 后缀 | 全库 |

| P1-2 | audit_state INDEX.md 裸文件名链接 | 22 条 | 统一加 `./` 前缀 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/INDEX.md` |

| P1-3 | LAYER8 缺失目标文件 | 7 条链接 | 确认是否应创建或已归档，更新引用 | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/` |

| P1-4 | README.md 链接指向错误目录 | 1 篇 | 核心文档链接从 03_TRADING_TACTICS 改为 docs/INDEX.md | `README.md` |

| P1-5 | 06_ARCHIVE 根散落 236 篇 | 236 篇 | 按主题/日期分入子目录，维护 archive 根 INDEX.md | `docs/06_ARCHIVE/` |

| P1-6 | 09_ARCHIVE/duplicates 与 06_ARCHIVE 交叉 | 53 篇 | 统一归档策略，合并或互链 | `docs/09_ARCHIVE/duplicates/` |

| P1-7 | 缺失 module_id | 59 篇 | 补充 YAML front matter 或标注为非标准文档 | 分散 |

| P1-8 | review_materials_package 路径错误 | 7 条 | 修正相对路径或标注为外部材料不参与内部链接检查 | `review_materials_package/` |

| P1-9 | 版本链未收敛（FINAL/V2…V8） | ~50 篇 | 保留最新综述，其余归档 | `docs/09_AUDIT/REPORTS/` |



## P2 — 可在季度复审中处理



| # | 问题 | 影响范围 | 建议动作 | 涉及路径 |

|---|------|----------|----------|----------|

| P2-1 | 伪链接（代码变量误识别） | 4 条 | 标注为代码片段，不参与链接检查 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` |

| P2-2 | notebooks .py 链接 | 4 条 | 可保留但标注为非 md 目标 | `notebooks/` |

| P2-3 | 目录编号体系不一致 | 4 组 | 长期规划重编号 | `docs/06_`, `docs/07_`, `docs/08_`, `docs/09_` |

| P2-4 | README.md 与 INDEX.md 并存 | ~100+ 目录 | 明确分工：README=简介，INDEX=导航 | 全库 |

| P2-5 | CHANGELOG.md 内容模板化 | 1 篇 | 持续更新实际变更记录 | `CHANGELOG.md` |



```
```---
```



## 执行优先级建议



1. **第一轮（1-2天）**：P0-2（双YAML合并脚本）+ P0-1（temp文件清理）

2. **第二轮（3-5天）**：P0-4（audit_state合并）+ P1-1（module_id去重）+ P1-2/P1-3（链接修复）

3. **第三轮（1周）**：P1-5（归档整理）+ P1-7（补充module_id）

4. **季度复审**：P2 全部

