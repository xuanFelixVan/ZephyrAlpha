---
module_id: GOVERNANCE_DECISIONS_LOCKED_20260408
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: STATE
---









# 文档治理裁决书（已锁定）



> **效力**: 本文件为整改与自动化脚本的**唯一权威规则源**；与本文冲突的旧叙述以本文为准。  

> **生效日期**: 2026-04-08  

> **裁决人**: 仓库 Owner（个人维护场景下即本人）  

> **依据审计**: OpenClaw `OPENCLAW_20260408_033500`



```
```---
```



## ADR-OC-001 — 双 YAML front matter 合并规则



| 项目 | 裁决 |

|------|------|

| **问题** | 全库大量 Markdown 存在连续两个 `---...---` YAML 块，解析器只认第一块，导致治理字段失真。 |

| **备选方案** | A. 以第一块为准；B. 以第二块为准，第一块仅用于补缺键。 |

| **决定** | **采用 B**。理由：与 OpenClaw 审计结论一致——首块多为后追加的「壳」，第二块常含较完整的 `module_id` / `responsibility`。 |

| **合并算法（执行时必须遵守）** | 1）**主块** = 第二个 YAML 块。2）对 `module_id`、`version`、`status`、`owner`、`responsibility`、`standard_type`、`applicable_scope`、`compliance_level` 等键：**以主块为准**。3）若主块**缺少**某键而第一块有，则从第一块**补入该键**，不覆盖主块已有键。4）`last_updated`：若两块均有，取**较新日期**；否则取存在的那个；皆无时填执行当日。5）正文：第二个 YAML 结束 `---` **之后**至文件末尾**原样保留**（除另有单行链接修复任务）。 |

| **生效日期** | 2026-04-08 |



```
```---
```



## ADR-OC-002 — `audit_state` 目录唯一权威路径



| 项目 | 裁决 |

|------|------|

| **问题** | `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state` 与 `.../07_OPERATIONS/audit_state` 双栈并存，职责重叠。 |

| **数据** | 截至 2026-04-08：`04_OPERATIONS/audit_state` 约 **289** 个文件，`07_OPERATIONS/audit_state` 约 **110** 个文件。 |

| **决定** | **唯一权威工作目录**定为：`docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state`。 |

| **对 `07_OPERATIONS/audit_state` 的处置** | **合并迁入**至上述权威目录（按文件名去重；同名则人工或 AI 比对后保留较新/较完整版本），迁完后将 `07_OPERATIONS/audit_state` 内保留 **INDEX.md** 或 **README.md**，内容仅含一行说明：「内容已统一至 `../04_OPERATIONS/audit_state`」，并修正全库指向 `07_.../audit_state` 的链接。 |

| **生效日期** | 2026-04-08 |

|| ⚠️ **修订说明（2026-04-16）** | **本 ADR 路径决定已被治理重构废止。** 审计报告唯一权威路径已由 docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/ **迁移至 docs/09_AUDIT/STATE/**（见 AGENTS.md v1.0.0、.cursor/rules/*.mdc、subsystem-registry.yaml）。旧路径全库已标注为 Deprecated。**执行时以 docs/09_AUDIT/STATE/ 为准，本条仅供历史溯源。** |



```
```---
```



## ADR-OC-003 — 重复 `module_id` 与归档命名



| 项目 | 裁决 |

|------|------|

| **问题** | 多文共用一个 `module_id`，破坏台账与检索唯一性。 |

| **决定** | 1）每组重复中指定 **一篇为 canonical**（以 `OPENCLAW_L3_CONFLICTS.md` / `module_id_duplicates_detail` 及人工判断为准：通常取路径最符合职责、或最新维护的一篇）。2）**非 canonical** 文档：`module_id` 改为 **`原ID_ARCHIVED`** 或 **`原ID_YYYYMMDD`**（二选一，同一批内统一）；并在正文或 YAML 增加 `supersedes_note` / 首段说明指向 canonical 路径。3）若存在 `docs/09_AUDIT/STATE/MODULE_ID_REGISTRY.md`（或等价注册表），**每批改完后同步更新**一行，避免注册表与文件再次漂移。 |

| **生效日期** | 2026-04-08 |



```
```---
```



## ADR-OC-004 — pre-commit 与批量整改的关系



| 项目 | 裁决 |

|------|------|

| **问题** | 批量改文档时 hook 可能失败，长期 `--no-verify` 不可接受。 |

| **决定** | 1）**每一批**合并进主分支前，在分支上执行 `git commit` **尽量不带** `--no-verify`；若失败，将 **完整报错** 复制到 `docs/09_AUDIT/STATE/PRECOMMIT_FAILURE_LOG_20260408.md`（可追加）。2）**本轮整改结束后一周内**，单独安排一次「修钩子或收窄规则」任务（不与大文件机械合并混在同一 PR）。3）整改执行期间允许临时 `--no-verify`** 仅限**单批超大 diff**，且该批 PR 描述中必须写明「pre-commit 失败原因摘要 + 后续跟踪项」。 |

| **生效日期** | 2026-04-08 |



```
```---
```



## ADR-OC-005 — 重复/多版本正文文档（非 YAML）



| 项目 | 裁决 |

|------|------|

| **问题** | 同一主题多份 md，或 V1/V2/FINAL 链，不知合并还是删除。 |

| **决定** | 1）**大段复制、同一主题**：合并为 **一篇 canonical**，其余改为短跳转页或移入 `docs/06_ARCHIVE/` 并在篇首写 **Superseded by / 已合并至** + 路径；更新内链。2）**版本链**：**不合并正文**；保留当前有效版为入口，旧版只归档并标注被替代。3）**删除**仅在不存独有信息且 Git 可恢复的前提下采用；**默认优先归档**。 |

| **生效日期** | 2026-04-08 |



```
```---
```



## 修订



| 版本 | 日期 | 说明 |

|------|------|------|

| 1.0.0 | 2026-04-08 | 初始锁定 |

