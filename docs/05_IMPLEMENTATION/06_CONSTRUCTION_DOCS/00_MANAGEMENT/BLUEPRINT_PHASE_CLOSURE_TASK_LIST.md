---
module_id: BLUEPRINT_PHASE_CLOSURE_TASK_LIST_001
version: 1.0.8
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 全库蓝图终稿阶段任务清单（人类与 AI 共用）
standard_type: 任务清单
applicable_scope: 蓝图阶段收尾与终稿验收前
---

# 全库蓝图终稿 — 任务清单

> **用途**：把「蓝图终稿」要办的事写成可勾选、可复查的条目；后续对话或排期可直接打开本文件对照进度。  
> **机构目标态**：与 [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) 对照时，本清单为**任务分解真源**，该标准为**合并视角与门禁映射**。  
> **摆放规则真源**：正式图纸柜里什么能放、什么不能放，以 [01_BLUEPRINTS 图纸柜文件治理规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) 为准。  
> **与卫生计划的关系**：执行本清单时，应同步遵守 [蓝图阶段文档卫生总计划](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md)；不必重复发明流程。  
> **维护**：在 `00_MANAGEMENT/` 新增规章类文档时，请同步更新 [项目办公室 README](./README.md) 与本节表格。  
> **任务 3 状态**：2026-04-10 已完成 — 过程报告已迁入 `01_BLUEPRINTS/REPORTS/`，`INDEX.md` 已重生成；防幻觉执行协议见 [BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md)。

## 推荐阅读入口

| 说明 | 路径 |
|------|------|
| **01_BLUEPRINTS 摆放与导航规则（真源）** | [`01_BLUEPRINTS_REPOSITORY_RULES.md`](./01_BLUEPRINTS_REPOSITORY_RULES.md) |
| **蓝图终稿定义与认可** | [`BLUEPRINT_FINAL_SIGNOFF.md`](./BLUEPRINT_FINAL_SIGNOFF.md) |
| **蓝图交付标准（机构精华版，目标态）** | [`BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md`](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) |
| **文档治理架构（L0～L5）** | [`DOCUMENT_GOVERNANCE_ARCHITECTURE.md`](./DOCUMENT_GOVERNANCE_ARCHITECTURE.md) |
| **受控文档登记表（按需填写）** | [`CONTROLLED_DOCUMENTS_REGISTER.md`](./CONTROLLED_DOCUMENTS_REGISTER.md) |
| **项目办公室总入口** | [`README.md`](./README.md) |
| **AI / 协作者交接说明** | [`PROJECT_OFFICE_AI_HANDOFF.md`](./PROJECT_OFFICE_AI_HANDOFF.md) |
| **图纸柜执行协议（防幻觉）** | [`BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md`](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md) |
| **全库治理文档导航** | [`GOVERNANCE_DOCUMENTS_NAVIGATION.md`](./GOVERNANCE_DOCUMENTS_NAVIGATION.md) |
| **孤儿与重复 / 重叠治理（Playbook）** | [`DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md`](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) |
| **重复文档处理标准（canonical）** | [`DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) |
| **重复簇指针台账（归档区）** | [`CANONICAL_POINTERS.md`](../../../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md) |
| 蓝图阶段总结与内容口径 | [`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md) |
| 建设文档总索引（需与真实文件夹一致） | [`../INDEX.md`](../INDEX.md) |
| `01_BLUEPRINTS` 机器生成列表 | [`../01_BLUEPRINTS/INDEX.md`](../01_BLUEPRINTS/INDEX.md) |
| TODO/TBD 类清理台账（若仍存在） | [`../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md`](../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md) |

---

## 任务 1：全楼地图（唯一总清单）

**目标**：在仓库里选定**唯一一份**「全库蓝图总清单」，并约定每个能力/模块只对应**一份**正式蓝图文件。

**注意**：蓝图不仅存在于 `01_BLUEPRINTS`，还分散在 `01_FRAMEWORK`、`11_STRATEGIC_DECISION`、`10_AI_WORKFLOW`、`02_FACTOR_LIBRARY` 等目录；总清单必须能覆盖这些位置或明确它们如何汇入 canonical。

**链接验证：本仓库默认「全量核对」（100%）**

> **严格路径脚本（2026-04-10）**：[`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md) 已由 `scripts/verify_manifest_paths_strict.py` 核对 **唯一路径项 N_path = 24**（标准 Markdown 内链 + 表格/正文中 `docs/` 字面路径去重，缺失则脚本 exit 1）；人读报告：`docs/09_AUDIT/STATE/MANIFEST_PATH_AUDIT_BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`。**注意**：`N_path` 仅为「总清单内可机读路径」真子集；**全库「应有蓝图条目」** 仍须 Owner 按本任务正文逐条闭环，完成后在下方 **N** 填写全量条目数（≥ `N_path`）。

- **Owner 要求**：对总清单中每一个「应有蓝图」条目，须**逐条**确认链接可解析、指向**唯一 canonical**；完成后在本任务下备注「已全检，共 N 条」。
- **机构常见例外**（仅当 Owner **书面豁免**时适用）：体量极大时可采用**统计抽检**（如随机 10 条）+ 说明样本量与豁免理由；**本仓库不设默认抽检**，豁免须写入登记表、commit 说明或本文件备注，避免无记录的「口头打折」。

**同题多稿与下面「重复文档治理」的关系**：若总清单暴露「同一主题两份正式稿」，须按 [孤儿与重复治理 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) + [重复文档处理标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) 做 canonical 裁决（重定向、登记表、`CANONICAL_POINTERS` 等），不能只改链接不裁决。

- [x] 已选定「总清单」主文档（或主文档 + 明确子索引的组合）— **主入口**：[`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md)；**图纸柜机器列表**：[`01_BLUEPRINTS/INDEX.md`](../01_BLUEPRINTS/INDEX.md)（2026-04-10）
- [ ] 每个「该有蓝图的条目」在总清单中均有记录
- [ ] 每条目可点击跳转到**唯一认定的正式蓝图**（无「同一主题两份正式稿各写各的」）
- [ ] **链接验证（全量）**：已对总清单中**每一条**「应有蓝图」做链接与 canonical 核对（备注：已全检，N = ___ 条）。若已获 Owner **书面抽检豁免**，改为完成抽检并在此写明豁免依据与样本
- [ ] **重复文档口径**：已确认不存在未裁决的同题多稿，或已按上述 Playbook / 重复标准完成处置并在登记表 / `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md` 等处可追溯

---

## 任务 2：两套档案室（路径统一）

**目标**：消除 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` 与 `docs/06_CONSTRUCTION_DOCS/` 混用带来的改错文件风险。

**与重复治理的关系**：若「两套路径」下存在**同题双份正文**，除写明哪条路径为权威外，还须按任务 1 所链的 **Playbook / 重复标准** 做副本处置（重定向、归档、登记表），避免「只认路径不认稿」留下两套真源。

- [x] 在「全楼地图」中用一句话写明：**以哪条路径为权威（canonical）** — 已写入 [`06_CONSTRUCTION_DOCS/INDEX.md`](../INDEX.md)「目录概要」与 [`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md)（2026-04-10）
- [x] 对非权威一侧：已标为只读副本 / 已迁出 / 已删除（三选一，且与地图一致）— `docs/06_CONSTRUCTION_DOCS/` 在 INDEX「遗留路径」中声明为非权威副本入口（2026-04-10）
- [x] 所有对外链接与脚本默认指向 canonical 路径 — **新建与治理默认**以 `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/` 为准；`09_AUDIT` 等历史 JSON/报告内旧路径为**记录快照**，不强制整库改写（2026-04-10）

---

## 任务 3：正式图纸柜只放正式蓝图

**目标**：执行 [01_BLUEPRINTS 图纸柜文件治理规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) 第 3、4 节：根目录仅 `*BLUEPRINT.md` 与 `INDEX.md`；过程记录进 `REPORTS/` 或 `00_MANAGEMENT/`。

- [x] 已建立或确认 `01_BLUEPRINTS/REPORTS/`（或等价名称）
- [x] 已将 `*_202604*.md` 等过程/报告类文件移入该文件夹（或等价归档位置）
- [x] 打开 `01_BLUEPRINTS` 根目录时，视觉上以正式蓝图为主、无杂物感

---

## 任务 4：门口指示牌与真实房间一致

**目标**：`06_CONSTRUCTION_DOCS/INDEX.md`（及必要的 `README.md`）中的子目录名称、数量、职责描述与磁盘上真实文件夹一致。

- [x] 已核对当前子目录（含 `00_MANAGEMENT`、`02_IMPLEMENTATION_GUIDES` 等）— 磁盘 8 顶层目录，2026-04-10
- [x] 已更新 `INDEX.md` 中的表格与说明（或已改文件夹命名以匹配旧索引，二选一）— 已重写子目录表与目录说明
- [x] 统计数字（子目录个数、文档数等）已复核或改为「见各目录 INDEX / 脚本生成」等可维护表述 — 子目录数 8；篇数指向下级 INDEX

---

## 任务 5：活跃蓝图中的「空白格子」

**目标**：对**仍在使用、非归档**的蓝图正文，清理悬而未决占位；归档区与模板中的 TBD 可保留但须标明性质。

- [ ] 已对活跃蓝图检索「待定 / TBD / 以后再说」等，能补的已补成明确结论或明确排期（如「第二期」）
- [ ] 已区分：代码/配置里的状态名（如 `DRAFT = "draft"`）≠ 文档未完成，未误删
- [ ] 归档与过程稿中的占位已标注「非终稿」或归入归档口径

---

## 任务 6：与卫生 / 审计文档对齐

**目标**：本清单第 1～5 项的执行结果，能在卫生计划与审计台账中找到对应记录或关闭说明。

- [x] 已对照 [蓝图阶段文档卫生总计划](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) 检查是否有遗漏批次 — 2026-04-10：INDEX 大门与任务 4 对齐属目录卫生/P0 相关入口整理（细项批次仍可按卫生总案 P1～P3 推进）
- [x] 若仍存在 TODO/TBD 清理台账，已更新状态或注明「仅归档范围保留」— 已在 [`TODO_CLEANUP_INVENTORY_20260406.md`](../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md) 文首增加 **2026-04-10 治理衔接备注**（与任务 5 联动；原 30 文件统计未重算）

---

## 执行备忘 · 任务 5 扫描（2026-04-10）

**递归全树（2026-04-10 续 · 严）**：已对 `01_BLUEPRINTS/**/*.md`（含 `REPORTS/`）检索 `| TBD |`、`（待补充）`、`### 待补充`、`集成验收.*待`：**0 命中**。另对根目录 `*BLUEPRINT.md` 检索 `待补充`：**0 命中**。扩词表或新增正文后须重跑并更新本段。

**历史批次（归档备忘）**：2026-04-10 多批已将「### 待补充项」改为「### 可选增强（第二期）」、去掉 `| TBD |` 与集成验收「待补充」等；细目见本文件版本记录与 git 历史，不再逐文件列举以免与当前扫描结果冲突。

---

## 建议推进顺序（可当本周节奏）

| 顺序 | 任务 | 完成判据（摘要） |
|------|------|------------------|
| ① | 任务 1 | 总清单 + 唯一正式链接 + **全量**链接验证（默认 100%，见上文豁免条款）+ 重复口径闭环 |
| ② | 任务 2 | 地图中 canonical 写明 + 副本处理完毕 |
| ③ | 任务 3 | 报告类文件已离开 `01_BLUEPRINTS` 根目录 |
| ④ | 任务 4 | `INDEX.md` 与真实目录一致 |
| ⑤ | 任务 5 | 活跃蓝图无悬空置位（按上文口径） |
| ⑥ | 任务 6 | 与卫生计划 / 台账对齐 |

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.8 | 2026-04-10 | 任务 1：`verify_manifest_paths_strict.py` + 总清单 §3.1.2 磁盘路径对齐；任务 5 备忘改为与递归扫描一致 |
| 1.0.7 | 2026-04-10 | 任务 5：8 份蓝图小节标题「待补充项」→「可选增强（第二期）」 |
| 1.0.6 | 2026-04-10 | 任务 5 续：多份蓝图去「待补充/TBD」与集成验收占位；任务清单备忘更新 |
| 1.0.5 | 2026-04-10 | 任务 6 台账衔接备注；任务 5 扫描备忘（命中列表）；git commit 已提交 INDEX/总清单/本清单三文件 |
| 1.0.4 | 2026-04-10 | 执行任务 2、4 勾选；任务 1 选定总清单；任务 6 卫生对照（部分）；INDEX 与磁盘对齐 |
| 1.0.3 | 2026-04-10 | 推荐阅读增文档治理架构 |
| 1.0.2 | 2026-04-10 | 任务 1：Owner 默认全量链接验证（100%）；抽检仅书面豁免 |
| 1.0.1 | 2026-04-10 | 任务 1：抽检/全检说明、重复文档治理勾选与推荐阅读链；任务 2：与重复治理交叉说明 |
| 1.0.0 | 2026-04-10 | 首版 |

---

## 维护说明

- 每完成一项，将上方 `- [ ]` 改为 `- [x]`，并可在该任务下补一行「完成日期 / 备注」。
- 若总清单主文档路径变更，请更新本文「推荐阅读入口」表格中的链接。
- AI 或协作者在后续会话中：**优先打开本文件**核对勾选状态，再决定下一步具体改哪些文件。
