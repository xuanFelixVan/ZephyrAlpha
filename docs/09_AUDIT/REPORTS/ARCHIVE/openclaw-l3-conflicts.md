---
module_id: OPENCLAW_L3_CONFLICTS
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: REPORTS
---









# OpenClaw L3 专业标准层冲突报告



> **run_id**: OPENCLAW_20260408_033500

> **生成时间**: 2026-04-08

> **数据来源**: LEDGER.csv + SENTINEL_L1_SCAN + L2 分批报告



```
```---
```



## 一、YAML 元数据冲突



### 1.1 双/多 YAML 头（1964 篇，占全库 70%）



这是全库最严重的系统性问题。在文档治理修复过程中，脚本在原有 YAML 前追加了新的 YAML 块，导致大量文件包含 2 个甚至更多 `---` 分隔的 YAML 头。



| 严重度 | 影响范围 | 说明 |

|--------|----------|------|

| P1 | 1964 篇 (70%) | 双 YAML 头导致解析器取第一个块，后续块中的 `module_id`、`responsibility` 等字段被忽略 |



**按一级目录分布**：



| 目录 | 双YAML文件数 | 占该目录比 |

|------|-------------|-----------|

| `docs/01_FRAMEWORK` | ~290 | ~86% |

| `docs/02_FACTOR_LIBRARY` | ~130 | ~92% |

| `docs/03_TRADING_TACTICS` | ~50 | ~89% |

| `docs/04_EXECUTION` | ~28 | ~93% |

| `docs/05_IMPLEMENTATION` | ~700 | ~88% |

| `docs/08_HUMAN_AI_INTERFACE` | ~100 | ~93% |

| `docs/09_AUDIT/STANDARDS` | ~25 | ~83% |

| `docs/09_AUDIT/TEMPLATES` | ~14 | ~88% |

| `docs/10_AI_WORKFLOW` | ~60 | ~87% |

| `docs/11_STRATEGIC_DECISION` | ~45 | ~88% |



### 1.2 module_id 重复（238 组）



详见 L1 报告。L3 补充：重复 ID 中 **10 篇文件仍含字面 `[模块ID]` 占位符**，属于模板未替换问题。



| 重复组 | 文件数 | 类型 | 处置建议 |

|--------|--------|------|----------|

| `05_IMPLEMENTATION_07_OPERATIONS_AUDIT_STATE_001` | 29 | 审计报告批量共享 | 每篇分配唯一 ID（加时间戳后缀） |

| `05_IMPLEMENTATION_04_OPERATIONS_AUDIT_STATE_001` | 18 | 同上 | 同上 |

| `02_FACTOR_LIBRARY_01_STANDARDS_001` | 18 | 归档副本冲突 | 归档文件 ID 加 `_ARCHIVED` 后缀 |

| `[模块ID]` | 10 | 模板占位符未替换 | 替换为实际 ID |

| `09_AUDIT_REPORTS_001` | 11 | 报告共享 | 分配唯一 ID |



### 1.3 缺失 module_id（59 篇）



这些文件在前 200 行扫描中未检出 `module_id` 字段。主要原因：

- 无 YAML front matter（如部分 temp_*.md、data/ 下的报告）

- YAML 格式损坏（双头导致第二个块被忽略）

- 非标准文档（README、CHANGELOG、中文命名文件）



```
```---
```



## 二、分类与编号冲突



### 2.1 目录编号体系不一致



| 冲突 | 说明 |

|------|------|

| `docs/09_AUDIT` vs `docs/09_ARCHIVE` vs `docs/09_RESEARCH_INNOVATION` | 同一 `09` 前缀下三个不同主题目录 |

| `docs/06_ARCHIVE` vs `docs/06_CONSTRUCTION_DOCS` | `06` 前缀含义冲突 |

| `docs/08_HUMAN_AI_INTERFACE` vs `docs/08_KNOWLEDGE` vs `docs/08_KNOWLEDGE_BASE` | `08` 前缀三义 |

| `docs/07_RESEARCH` vs `docs/07_AI_REPORTING` | `07` 前缀二义 |



### 2.2 文件命名冲突



| 模式 | 数量 | 说明 |

|------|------|------|

| `INDEX.md` 多义 | ~293 | 每个子目录都有 INDEX.md，但职责从导航到内容摘要不等 |

| `README.md` 与 `INDEX.md` 并存 | ~100+ | 同一目录下两篇入口文档，职责不清 |

| `BLUEPRINT.md` 与 `*_BLUEPRINT.md` 并存 | ~30 | 同一目录下既有通用蓝图又有专题蓝图 |



```
```---
```



## 三、五大原则合规



| 原则 | 合规率 | 主要违规 |

|------|--------|----------|

| 职责单一 | ~60% | audit_state 下大量过程报告与正式文档混放；README/INDEX 职责重叠 |

| 不越界 | ~70% | 05_IMPLEMENTATION 蓝图与 01_FRAMEWORK 蓝图内容重叠 |

| 索引一致 | ~55% | 1964 篇双 YAML 头导致 INDEX 中声明的 module_id 与实际不一致 |

| 无重复 | ~50% | 238 组 module_id 重复；audit_state 两处副本（04_OPERATIONS + 07_OPERATIONS） |

| 版本收敛 | ~40% | FINAL/V2/V3/V4…V8 多版本并存于活跃目录；temp_*.md 版本链未收敛 |



```
```---
```



## 四、结构性冲突



### 4.1 audit_state 双副本



`docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/`（238 篇）与 `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/`（107 篇）存在大量同名/同主题报告，构成全库最大的重复源。



### 4.2 06_ARCHIVE 根散落



`docs/06_ARCHIVE/` 根目录下散落 236 篇文件，无子目录分类，导航成本极高。



### 4.3 09_ARCHIVE/duplicates 与 06_ARCHIVE 交叉



`docs/09_ARCHIVE/duplicates/`（53 篇）与 `docs/06_ARCHIVE/` 存在大量重叠，归档策略不统一。
