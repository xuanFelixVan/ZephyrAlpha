---
module_id: OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408_7864
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: PROCEDURES
---









# OpenClaw 文档整改 — 执行手册（机构流程 · 单人可用）



> **你要做的事**：按下面**顺序**做完每一阶段；每阶段有**完成标准**。  

> **你不用做的事**：再填「选项表」——所有裁决已在 `docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md` 锁定。  

> **AI 的角色**：按该裁决书执行批量编辑、生成脚本、跑检查；你负责 **Git 分支、合并、抽查**。  

> **修订日期**: 2026-04-08



```
```---
```



## 0. 验收定义（什么叫「审计闭环执行完成」）



同时满足下列 **Exit Criteria**，即视为本轮回整改**执行闭环完成**（不要求「永远零警告」，但 P0 必须清零或可解释豁免）：



| # | 标准 |

|---|------|

| EC-1 | 根目录 **损坏不可读** 的 `temp_*.md`：**已修复编码并归档**或 **已删除**（且正式稿已存在或无独有信息），清单与 `OPENCLAW_AUDIT_SUMMARY` 中 P0 一致。 |

| EC-2 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` 下 **双重路径** 等 P0 死链：**已按 Backlog 修完**或 L1 报告中该项为 0。 |

| EC-3 | **双 YAML**：全库 `*.md` 抽样 + 全量扫描确认**不再存在**「两个连续完整 YAML 头」模式，或仅剩登记在 `docs/09_AUDIT/STATE/DOUBLE_YAML_EXCEPTIONS.md` 的**明示豁免**（若无豁免文件即视为不允许例外）。 |

| EC-4 | **重复 `module_id`**：L1 / OpenClaw 台账中 **重复组为 0**（或仅剩带 `_ARCHIVED` / `_YYYYMMDD` 后缀且注册表已更新）。 |

| EC-5 | **权威 `audit_state`**：仅保留 `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state` 为工作主目录；`07_OPERATIONS/audit_state` 已按裁决书 **ADR-OC-002** 处理完毕。 |

| EC-6 | **回归**：对仓库根执行 `python scripts/sentinel_l1_governance_scan.py`（或你当前等价命令），**保存**输出到 `docs/09_AUDIT/STATE/SENTINEL_L1_POST_REMEDIATION_20260408.md`（或带日期的新文件）；报告中 **无效内链、双 YAML、重复 module_id** 三类指标不劣于整改前基线，且 P0 类问题为 0。 |

| EC-7 | **Git**：所有改动在**独立分支**上、以**可 review 的批量 commit** 进入主分支；关键节点有 **tag**（例如 `remediation-p0-complete`、`remediation-yaml-complete`）。 |



```
```---
```



## 1. 阶段划分（顺序不可乱）



理由：先低语义风险项，再结构大改，最后搬迁与归档，避免同一 PR 混多种风险。



| 顺序 | 阶段代号 | 内容 | 裁决依据 |

|------|----------|------|----------|

| 1 | **P0-A** | 根目录 `temp_*.md` + 蓝图死链 + `[模块ID]` 占位符 | Backlog P0 |

| 2 | **P0-B** | 双 YAML 合并（算法见 ADR-OC-001） | ADR-OC-001 |

| 3 | **P1-A** | 重复 `module_id` 去重 + 缺 `module_id` 补全 | ADR-OC-003、Backlog |

| 4 | **P1-B** | `audit_state` 双目录合并 | ADR-OC-002 |

| 5 | **P1-C** | 其余无效内链、INDEX 裸链等（按 `OPENCLAW_REMEDIATION_BACKLOG`） | Backlog |

| 6 | **P2** | 归档整理、README/INDEX 分工等 | 可延期；不阻塞 EC-1～EC-6 |



```
```---
```



## 2. 每阶段通用动作（机构称「质量门」）



每个阶段结束**必须**做：



1. `python scripts/sentinel_l1_governance_scan.py`（路径以你仓库为准）。  

2. 将 JSON/MD 报告**复制或生成**到 `docs/09_AUDIT/STATE/`，文件名带阶段代号与日期。  

3. **抽查**：随机打开 3～5 个被改文件，确认 front matter 与正文未错位。  

4. **Git**：`commit`；若 pre-commit 失败，按 **ADR-OC-004** 记录。  

5. 再打 **tag**（可选但推荐）。



```
```---
```



## 3. 阶段 P0-A — 操作清单



1. 列出根目录所有 `temp_*.md`，按 `OPENCLAW_AUDIT_SUMMARY` / Backlog 处理编码与去留。  

2. 修正蓝图目录内 **双重 `docs/` 路径** 链接（见 Backlog P0-5）。  

3. 替换 `[模块ID]` 占位符（见 Backlog P0-3）。  

4. **完成标准**：满足 **EC-1、EC-2**；并满足 §2 质量门。



```
```---
```



## 4. 阶段 P0-B — 双 YAML（核心批量）



1. 向 AI 下达任务时**必须附带**完整路径：`GOVERNANCE_DECISIONS_LOCKED_20260408.md` 中 **ADR-OC-001** 全文。  

2. **先 dry-run**：任选 **50 个** 双 YAML 文件，输出 unified diff 到**本批专用目录**（建议 `docs/09_AUDIT/STATE/double_yaml_dryrun_<YYYYMMDD>/`）；**历史 2026-04-08 样本**已归档至 [`docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample/`](../../../10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md)，你肉眼确认无误后再全量写回。  

3. **再分批**：每批建议 **100～200** 个文件，避免单 PR 无法 review。  

4. **完成标准**：**EC-3** + §2 质量门。



```
```---
```



## 5. 阶段 P1-A — module_id



1. 以 `OPENCLAW` 产出的重复清单为准，按 **ADR-OC-003** 逐组处理。  

2. 每批更新 `MODULE_ID_REGISTRY`（若存在）。  

3. **完成标准**：**EC-4** + §2 质量门。



```
```---
```



## 6. 阶段 P1-B — audit_state



1. 严格按 **ADR-OC-002**：以 `04_OPERATIONS/audit_state` 为唯一权威目录。  

2. 将 `07_OPERATIONS/audit_state` 内容迁入并去重，修正链接与 INDEX。  

3. **完成标准**：**EC-5** + §2 质量门。



```
```---
```



## 7. 阶段 P1-C 与 P2



1. **P1-C**：按 `OPENCLAW_REMEDIATION_BACKLOG.md` 剩余 P1 行逐项勾选。  

2. **P2**：按季度或空闲执行；**不阻塞**你宣布「本轮回闭环完成」（只要 EC-1～EC-6 满足）。



```
```---
```



## 8. 最终收口



1. 生成一篇短报告：`docs/09_AUDIT/REPORTS/REMEDIATION_EXECUTION_CLOSURE_20260408.md`，逐条勾选 EC-1～EC-7。  

2. 将 `OPENCLAW_REMEDIATION_PLAN_DRAFT_20260408.md` 首行状态改为 **Active** 或新增一行注明「执行以本 PLAYBOOK 与 LOCKED 裁决为准」。



```
```---
```



## 9. 相关文件



| 文件 | 用途 |

|------|------|

| `docs/09_AUDIT/STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md` | **规则源** |

| `docs/09_AUDIT/PROCEDURES/OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md` | **本执行手册** |

| `docs/09_AUDIT/REPORTS/OPENCLAW_REMEDIATION_BACKLOG.md` | 任务明细 |

| `docs/09_AUDIT/REPORTS/OPENCLAW_AUDIT_SUMMARY_20260408.md` | 审计基线数字 |



```
```---
```



**一句话**：你只需打开 **裁决书** 给 AI，再按本手册 **P0-A → P0-B → P1-A → P1-B → P1-C** 顺序做，最后用 **§0 Exit Criteria** 自检打勾，即机构意义上的「审计驱动整改」闭环。

