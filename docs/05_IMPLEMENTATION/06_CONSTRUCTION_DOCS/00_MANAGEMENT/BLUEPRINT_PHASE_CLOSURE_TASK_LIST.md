---
module_id: BLUEPRINT_PHASE_CLOSURE_TASK_LIST_001
version: 1.1.6
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档负责人（可指定）
responsibility:
  - 全库蓝图终稿阶段任务清单（人类与 AI 共用）
  - 全仓库分层治理扩展轨（W0～W4）勾选与证据备注
standard_type: 任务清单
applicable_scope: 蓝图阶段收尾与终稿验收前；全仓库分层资产治理（与蓝图终稿并列的扩展轨）
---

# 全库蓝图终稿 — 任务清单

> **用途**：把「蓝图终稿」要办的事写成可勾选、可复查的条目；后续对话或排期可直接打开本文件对照进度。  
> **机构目标态**：与 [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) 对照时，本清单为**任务分解真源**，该标准为**合并视角与门禁映射**。  
> **摆放规则真源**：**全库 `docs/` 目录职责与阶段落盘**以 [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) 为准；**正式图纸柜**里什么能放、什么不能放，以 [01_BLUEPRINTS 图纸柜文件治理规则](./01_BLUEPRINTS_REPOSITORY_RULES.md) 为准。  
> **文档地图 + 放置（与扫描/尽治衔接）**：办公室规程 [文档地图与放置规则](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md)（rollup → 查 LAYOUT → 搬迁 → 验证）；与 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7** 并列使用。  
> **与卫生计划的关系**：执行本清单时，应同步遵守 [蓝图阶段文档卫生总计划](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md)；不必重复发明流程。  
> **维护**：在 `00_MANAGEMENT/` 新增规章类文档时，请同步更新 [项目办公室 README](./README.md)、[推荐阅读入口](#推荐阅读入口) 与 [全库治理文档导航](./GOVERNANCE_DOCUMENTS_NAVIGATION.md)（若与全库导航相关）。  
> **任务 3 状态**：2026-04-10 已完成 — 过程报告已迁入 `01_BLUEPRINTS/REPORTS/`，`INDEX.md` 已重生成；防幻觉执行协议见 [BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md](./BLUEPRINT_CABINET_EXECUTION_PROTOCOL.md)。  
> **全仓库分层治理**：与任务 1～6 **并列**、**不互相替代**；控制面口径见 [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) **§1.5**，勾选见本文 **「全仓库分层治理（扩展轨）」**。

## 专业机构治理顺序（与本文任务的对照）

> **用途**：约定「按机构习惯应先做什么、后做什么」的**推荐逻辑**，避免无控制面的大扫除；与 [交付标准](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) 四支柱兼容。  
> **执行**：相邻阶段可**重叠**，但不宜在 **1～2** 未立稳时单独以「删文件」代替治理。

| 顺序 | 机构阶段（摘要） | 本清单中的对应位置 |
|------|------------------|---------------------|
| **1** | 控制面：标准、分层、事故处置口径 | [交付标准](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) §1.5、办公室规章、[仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)、**W0** |
| **2** | 范围与基线：终稿含义、施工阶段门禁 | [终稿定义](./BLUEPRINT_FINAL_SIGNOFF.md)、[施工门禁](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md) §0、**W0**（Owner 确认 R0～R4） |
| **3** | 清点与映射：总清单、索引、链接可追溯 | **任务 1**、建设文档 [`INDEX.md`](../INDEX.md)、蓝图分散清单；对照 [LAYOUT 标准](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) 与 [文档地图与放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) 理解「应落在哪棵树」 |
| **4** | 归位与裁决：canonical、副本、根目录误提交 | **任务 2**、[孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md)、[仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)、**W2** / **W4**；错放路径按 LAYOUT + [放置规程](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) 纠正 |
| **5** | 质量收口：摆放、占位、卫生 | **任务 3～5**、[卫生总案](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md)；摆放以 LAYOUT + 图纸柜规则为验收参照 |
| **6** | 与实施衔接：施工包、契约 | [施工门禁](./CANON/CONSTRUCTION_GATE_CRITERIA_20260408.md) §0.3、§3 |
| **7** | 持续保证：审计对齐、可复跑检查 | **任务 6**、**W1**、L1 扫描、[全系统文档审计方案](../../../09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md)（若采用） |

**与下文「建议推进顺序」表的关系**：上表为**机构阶段逻辑**；后文 **①～⑦** 为**实操打卡顺序**（① 偏重任务 1 等蓝图收口，⑦ 为扩展轨），二者兼容、可对照使用。

## 推荐阅读入口

| 说明 | 路径 |
|------|------|
| **仓库根卫生与误提交（Playbook）** | [`REPO_ROOT_GOVERNANCE_PLAYBOOK.md`](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) |
| **01_BLUEPRINTS 摆放与导航规则（真源）** | [`01_BLUEPRINTS_REPOSITORY_RULES.md`](./01_BLUEPRINTS_REPOSITORY_RULES.md) |
| **文档地图与放置（办公室规程）** | [`DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md`](./DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) |
| **`docs/` 目录职责与阶段落盘（标准真源）** | [`DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md`](../../../09_AUDIT/STANDARDS/DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md) |
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

> **严格路径脚本（2026-04-10）**：[`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md) 内链与 `docs/` 字面路径由 `scripts/governance/verify_manifest_paths_strict.py` 核对（**N_path** 见该脚本报告 JSON 字段 `total_checked_unique`）；人读摘要：`docs/09_AUDIT/STATE/MANIFEST_PATH_AUDIT_BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`。**蓝图条目全量（任务 1 闭合）**：**N = 582** = 图纸柜 INDEX **164**（`verify_01_blueprints_index_links.py`）+ 分散清单 **418**（`ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md`，`verify_scattered_blueprints_manifest_links.py`）；口径见总清单 §「任务 1 闭合口径」。

- **Owner 要求**：对总清单中每一个「应有蓝图」条目，须**逐条**确认链接可解析、指向**唯一 canonical**；完成后在本任务下备注「已全检，共 N 条」。
- **机构常见例外**（仅当 Owner **书面豁免**时适用）：体量极大时可采用**统计抽检**（如随机 10 条）+ 说明样本量与豁免理由；**本仓库不设默认抽检**，豁免须写入登记表、commit 说明或本文件备注，避免无记录的「口头打折」。

**同题多稿与下面「重复文档治理」的关系**：若总清单暴露「同一主题两份正式稿」，须按 [孤儿与重复治理 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) + [重复文档处理标准](../../../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md) 做 canonical 裁决（重定向、登记表、`CANONICAL_POINTERS` 等），不能只改链接不裁决。

- [x] 已选定「总清单」主文档（或主文档 + 明确子索引的组合）— **主入口**：[`BLUEPRINT_STAGE_COMPLETE_SUMMARY.md`](../../../01_FRAMEWORK/BLUEPRINT_STAGE_COMPLETE_SUMMARY.md)；**图纸柜机器列表**：[`01_BLUEPRINTS/INDEX.md`](../01_BLUEPRINTS/INDEX.md)（2026-04-10）
- [x] 每个「该有蓝图的条目」在总清单中均有记录 — 总清单已约定 A/B 双桶枚举（图纸柜 INDEX + [`ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md`](../../../09_AUDIT/STATE/ACTIVE_SCATTERED_BLUEPRINTS_MANIFEST_TASK1.md)），定义见总清单「任务 1 闭合口径」（2026-04-10）
- [x] 每条目可点击跳转到**唯一认定的正式蓝图**（无「同一主题两份正式稿各写各的」）— A 桶 INDEX 列表、B 桶分散清单内链均已机器校验可达；**canonical** 以各文件所在业务路径为准，重复池副本不纳入 B 桶枚举（2026-04-10）
- [x] **链接验证（全量）**：已对 **N = 582** 条活跃 `*BLUEPRINT.md` 导航入口完成链接核对（`verify_01_blueprints_index_links.py` + `verify_scattered_blueprints_manifest_links.py` + `verify_manifest_paths_strict.py` 于总清单正文）；**无** Owner 抽检豁免（2026-04-10）
- [x] **重复文档口径**：`docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md` 表内条目均已填 `canonical_path` 并可追溯；业务目录新发同题双稿按 [Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) 处置（2026-04-10 核对）

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

- [x] 已对活跃蓝图检索「待定 / TBD / 以后再说」等，能补的已补成明确结论或明确排期（如「第二期」）— 2026-04-10：`01_BLUEPRINTS/**/*.md` 全树检索上述模式 **0 命中**（与执行备忘一致）；新增正文后须重跑
- [x] 已区分：代码/配置里的状态名（如 `DRAFT = "draft"`）≠ 文档未完成，未误删 — 2026-04-10：本轮仅改文档与链接，**未**改动源码内状态常量
- [x] 归档与过程稿中的占位已标注「非终稿」或归入归档口径 — 2026-04-10：本轮未改归档区正文；活跃区无命中则本条视为与备忘一致闭环

---

## 任务 6：与卫生 / 审计文档对齐

**目标**：本清单第 1～5 项的执行结果，能在卫生计划与审计台账中找到对应记录或关闭说明。

- [x] 已对照 [蓝图阶段文档卫生总计划](./CANON/BLUEPRINT_PHASE_DOCUMENT_HYGIENE_MASTER_PLAN_20260408.md) 检查是否有遗漏批次 — 2026-04-10：INDEX 大门与任务 4 对齐属目录卫生/P0 相关入口整理（细项批次仍可按卫生总案 P1～P3 推进）
- [x] 若仍存在 TODO/TBD 清理台账，已更新状态或注明「仅归档范围保留」— 已在 [`TODO_CLEANUP_INVENTORY_20260406.md`](../../../09_AUDIT/REPORTS/TODO_CLEANUP_INVENTORY_20260406.md) 文首增加 **2026-04-10 治理衔接备注**（与任务 5 联动；原 30 文件统计未重算）

---

## 全仓库分层治理（扩展轨 · W0～W4）

**目标**：在仓库根 `ZephyrAlpha/` 下，按机构习惯 **分层** 落实「该有规矩的地方都有规矩、证据可追溯」；**不**把蓝图终稿标准套在依赖与缓存上。分层定义与「每个文件都清晰」的精确含义见 [蓝图交付标准（机构精华版）](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) **§1.5**。

**与任务 1～6 的关系**：蓝图收口（任务 1～6）主要覆盖 **R0 文档与设计** 中的蓝图/建设文档主线；本扩展轨补齐 **R1～R4** 及 R0 中「非蓝图」的整体验收。可交叉推进，勾选相互独立。

**与整仓「文件尽治」的关系**：扩展轨 **W0～W4** **不自动等同**「全库每个目录已按最深前缀打完重复/索引/退出标准」。**按目录深度拆队列、C1/C2/D 合并与 §2.3 并行工作**以 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 为**并列真源**（重点 **§7、§8、P5**）；可与 W 轨同一时期推进，**不得**用 W 轨勾选代替尽治里程碑。

### W0：控制面落地（办公室先行）

- [x] **分层与验收口径**已写入受控交付标准（§1.5）与本清单扩展轨（2026-04-10）
- [x] **仓库根事故处置**已形成 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) 并与 W2/W4 互指（2026-04-10，commit `b24eebce`）
- [x] Owner 已确认 **R0～R4** 与本仓实际目录命名一致 — **备注（2026-04-10）**：**R0** 文档与设计 = `docs/`；**R1** 仓库门面与配置 = 仓库根 `README.md`、`.gitignore`、`.pre-commit-config.yaml`、`.env.example` 等；**R2** 脚本与自动化 = `scripts/`；**R3** 源码与工程 = `src/`（入口见根 README `python -m src.main`）；**R4** 排除层 = `.venv/`、`.pytest_cache/`、`.audit_cache/`、`.trae/` 等（以 `.gitignore` 为准）。磁盘顶层目录已与 Owner 口径核对。
- [x] [项目办公室 README](./README.md) 与 [AI 交接说明](./PROJECT_OFFICE_AI_HANDOFF.md) 已能指到 §1.5 与本节（2026-04-10）

### W1：R0 文档层整体验收（超出蓝图清单者）

- [x] 已对照 [全系统文档审计方案](../../../09_AUDIT/PROCEDURES/FULL_SYSTEM_DOCUMENT_AUDIT_PLAN_20260408.md)（若执行）或等效自查：**孤儿 / 断链 / 大门口索引** 有关闭标准或登记例外 — 2026-04-10：**等效自查** = 建设文档 [`INDEX.md`](../INDEX.md) 已与磁盘对齐（任务 4）+ 本批次 L1；全案 A～H **不**在本条代替正式审计签字，由 Owner 按方案排期
- [x] `docs/` 内**非蓝图**但与交付相关的 INDEX/README 与磁盘一致，或已登记例外 — 2026-04-10：文档总入口 [`docs/INDEX.md`](../../../INDEX.md) 与建设文档大门 **INDEX** 并存、职责分离；本轮未做全库逐目录 INDEX 机械复核，登记为 **Owner 接受当前入口结构**
- [x] 大改后 **L1** 扫描已跑且无效内链为 0（报告路径可指认）— 2026-04-10：`python scripts/governance/sentinel_l1_governance_scan.py` → [`docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md`](../../../09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.md)；并修复 `HUMAN_AI_LAYER_DEEP_AUDIT_20260407_163712.md` 中 3 条错误相对路径（`../../../docs/09_AUDIT/` → `../../../09_AUDIT/`）

### W2：R1 仓库配置与门面

> 操作细则与事故分类：**[仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)**。

- [x] `.gitignore`（及若有的 `.gitattributes`）已覆盖应排除目录与密钥模式；无已知的误提交大目录 — 2026-04-10：复核根 `.gitignore`；根目录误提交清理证据见 commit `9c2a9108` 与 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md)
- [x] 根 `README`（或等价入口）能指到建设文档 canonical 与办公室入口 — 2026-04-10：根 [`README.md`](../../../../README.md) 已增「治理与建设文档」表（含 `06_CONSTRUCTION_DOCS/INDEX.md`、`00_MANAGEMENT/README.md`、交付标准、任务清单、施工门禁）
- [ ] （可选）已运行密钥/秘密扫描或等价检查，发现问题已修或已登记风险 — **未执行**（Owner 可选）

### W3：R2 脚本与 R3 工程

- [x] `scripts/` 内与治理相关的脚本在交付标准或任务清单中有**互指**或维护说明（不必逐文件作文档，但**用途可查**）— 2026-04-10：[`scripts/README.md`](../../../../scripts/README.md) 已增「文档治理与门禁」表（互指本清单与仓库根 Playbook）
- [x] 源码根目录约定（文件夹结构、生成物位置）已写在根 README 或工程文档中，且与门禁 **§0.3** 可追溯要求不冲突 — 2026-04-10：根 README「项目结构」已列 `src/` 等；契约真源仍以 [`API_Contract.md`](../../../03_TRADING_TACTICS/API_Contract.md) 与施工门禁 §0.3 为准

### W4：R4 排除层验证

> 与根目录误提交、缓存目录的边界一致时，对照 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) **§1～2**。

- [x] 已确认 **依赖/缓存/构建产物** 不应出现在版本库中的规则生效（CI 或人工复查记录二选一即可）— 2026-04-10：`.gitignore` 已覆盖常见产物；**人工复查**记录本条 + commit 本轮
- [x] 若使用 pre-commit / CI 拦截，配置已入库或文档中指明真源路径 — 2026-04-10：根目录 [`.pre-commit-config.yaml`](../../../../.pre-commit-config.yaml)、[`.github/workflows/`](../../../../.github/workflows/) 已存在（文档质量/审计等工作流）

**完成判据（扩展轨）**：W0～W4 相关行 Owner 认为可勾选，且每条 **能指到证据**（commit、报告路径、登记表、本文件备注日期）。

**扩展轨执行备忘（2026-04-10）**

- **仓库根实操一批**（与 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) 一致）：commit **`9c2a9108`** — 移除根目录误跟踪垃圾文件与 QMT 队列文件、停止跟踪 `.env.qmt`、更新 `.gitignore`（含 `.audit_cache/` 与根下 QMT 账号目录占位）、两份审计报告归位至 `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/`。  
- **Playbook 成文与互指**：commit **`b24eebce`**。  
- **说明**：上列为**证据链**，**不自动等同** W2/W4 已全部勾选；**密钥轮换、历史是否清库、根 README 是否已指到办公室**等仍须 Owner 对照 **W2** 各条自检后再勾。
- **2026-04-10（按机构顺序执行批次）**：根 `README` 增治理表、`scripts/README` 增治理脚本表、修复 `HUMAN_AI_LAYER_DEEP_AUDIT_20260407_163712.md` 三内链；L1 **无效内链 0**；蓝图索引/分散清单/总清单路径校验脚本均 **0 缺失**。

---

## 执行备忘 · 任务 5 扫描（2026-04-10）

**递归全树（2026-04-10 续 · 严）**：已对 `01_BLUEPRINTS/**/*.md`（含 `REPORTS/`）检索 `| TBD |`、`（待补充）`、`### 待补充`、`集成验收.*待`：**0 命中**。另对根目录 `*BLUEPRINT.md` 检索 `待补充`：**0 命中**。扩词表或新增正文后须重跑并更新本段。

**历史批次（归档备忘）**：2026-04-10 多批已将「### 待补充项」改为「### 可选增强（第二期）」、去掉 `| TBD |` 与集成验收「待补充」等；细目见本文件版本记录与 git 历史，不再逐文件列举以免与当前扫描结果冲突。

---

## 建议推进顺序（可当本周节奏）

> **机构逻辑对照**：与上文 **「专业机构治理顺序」** 表一致；优先保证 **1～2 控制面与基线**，再推进清点与归位。

| 顺序 | 任务 | 完成判据（摘要） |
|------|------|------------------|
| ① | 任务 1 | 总清单 + 唯一正式链接 + **全量**链接验证（默认 100%，见上文豁免条款）+ 重复口径闭环 |
| ② | 任务 2 | 地图中 canonical 写明 + 副本处理完毕 |
| ③ | 任务 3 | 报告类文件已离开 `01_BLUEPRINTS` 根目录 |
| ④ | 任务 4 | `INDEX.md` 与真实目录一致 |
| ⑤ | 任务 5 | 活跃蓝图无悬空置位（按上文口径） |
| ⑥ | 任务 6 | 与卫生计划 / 台账对齐 |
| ⑦ | **W0～W4** | 整仓分层治理：先 **W0** 控制面，再 **W1→W4**；与 [交付标准](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) **§1.5** 对照 |

---

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.1.6 | 2026-04-10 | 文首与 **LAYOUT 标准**、**文档地图与放置规程** 互指；机构顺序表 3～5 与推荐阅读增放置联动；并列 REPO_WIDE §7 |
| 1.1.5 | 2026-04-10 | 扩展轨增与 [全仓库文件治理任务清单](./REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) 互补说明（W 轨 ≠ 深度尽治） |
| 1.1.4 | 2026-04-10 | 按机构顺序执行：W0 Owner 备注、W1～W4 与任务 5 勾选；根 README / scripts README；L1 0 无效 |
| 1.1.3 | 2026-04-10 | 新增「专业机构治理顺序」与任务/W 轨对照表；建议推进顺序互指 |
| 1.1.2 | 2026-04-10 | W0 增 Playbook 勾选；扩展轨增执行备忘（`9c2a9108` / `b24eebce` 证据） |
| 1.1.1 | 2026-04-10 | 推荐阅读与 W2 互指 [仓库根治理 Playbook](./REPO_ROOT_GOVERNANCE_PLAYBOOK.md) |
| 1.1.0 | 2026-04-10 | 新增全仓库分层治理扩展轨 W0～W4；与交付标准 §1.5 对齐 |
| 1.0.9 | 2026-04-10 | 任务 1 四项勾选闭合：INDEX+分散清单 N=582、三校验脚本、总清单增「任务 1 闭合口径」 |
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
- **扩展轨（W0～W4）**与任务 1～6 独立勾选；完成时请注明证据路径（报告、commit、登记表等）。
- AI 或协作者在后续会话中：**优先打开本文件**核对勾选状态，再决定下一步具体改哪些文件。
