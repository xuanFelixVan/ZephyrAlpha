---
created: 2026-09-28
ttl: task_bound
volume: 05_f116_sop_methodology_family
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-f116-sop-family-book-20260926
---

# 05 · F116 SOP 方法论族（`sop/` 真源地图：目录族 × 索引 × 命名闸 × 生成器）

> 车道 W4-B｜worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`｜零提交零入队｜只读取证。
> 派单=`00_skeleton/92_coverage_triage_20260926.md` §三（F116 判"真缺簿·全六向缺：横切元层，无专册"）。
> 本册状态：**六向齐证**，§一 挂 F116 认领锚。核心发现＝**"族数"三处口径互斥（九族 / "12 目录实测" / 实测 11 目录）**，且**九族措辞已写进宪法 §6.2**（病灶 1）；**GATE-NAMING 真跑（非装饰）但 README 引的"N-11 命名闸"在 gate_registry 里查无**（引用为规则号而非 gate_id，病灶 2）；**README 自称的"capability_lookup 双通道可达"其中一条通道实测零消费**（病灶 3）。

## 一、环节定义与边界

总册口径（`00_skeleton/00_全环节总册.md:201`）：F116 SOP 方法论族｜九族真源（挖矿/施工/数据操作/回测/治理/图书馆/自动化/运维/审查+TDM 族）｜上游 —｜下游 全链方法论｜真源=`docs/01_policies_and_standards/sop/`（**12 目录实测**：automation/backtest_system/construction/data_audit/data_ops/governance/library/mining/ops/review/trading_decision_map）｜总册标 built、P1、M 段横切（X1）。

本册覆盖 F116
> 机生对账尺认领锚，机生对账尺认领锚）。实证面=`sop/` 目录族 11 个（ls 实测）＋族内 44 个 .md（逐族计数实测）＋`README.md`（module_id `SOP-INDEX-001`）＋生成器 3 件＋门禁 2 条（GATE-NAMING / GATE-NAMING-AUDIT）。

边界：F116 = **族的组织与真源地图层**（谁归哪族、族内唯一真源是谁、索引与命名是否合规），不含各族方法论本体内容（那是各族格的事，如 F119 自动化计划本体、SOP-A/B/C/D 回测四卷、mining_sop 六向寻路法本身）。与 F106（术语三层翻译）、F97/F98（门禁链）不并。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | ①**新会话冷启动序**：`sop/README.md:14` "新 AI 入职第二读（第一读=仓库根 `AGENTS.md` 冷启动序列）"；②**IDE 注入面**：`.trae/rules/project_rules.md:57` "## PRE-OP：任何操作前必须通过的强制检查" → :68 行直读 `sop/mining_sop/mining_sop_policy.md`（写方案/建策略/调研类任务）→ 族选择的**上游驱动**是任务类型；③**宪法索引指令**：`AGENTS.md` §6.2 "方法论真源地图=sop/README.md（九族索引）：调研=mining_sop/ 施工=construction_sop/ 数据操作=data_ops_sop/ 对齐改图=governance_sop/"；④**新方法论入驻申请**（README §使用纪律 2）："新 SOP 按功能归族＋命名遵循 `*_policy.md`（doc_type=policy 时，N-11 命名闸）＋新建文件须登记 creation_token" |
| 下游消费 | ①**各族 index.md**（10/11 族有，`library_sop/` 实测缺）；②**机读目录**：`rule_catalog_registry.yaml`（ROOR REG-DOC-001 :271-279 登记为文档元数据真源）——`sop/README.md` §使用纪律 3 自称"本表由 capability_lookup 与 rule_catalog_registry.yaml（生成器产出）双通道冗余可达"；③**capability_cards 渐进披露层**（宪法 §6.2 检索序第一站 `data/capability_cards/` → 44 张卡内 `capability: automation_sop` 等族名直挂 sop 族，如 `capability_canonical_file_registry.yaml:50541-50544` 的 `capability: automation_sop`＋token）；④**作业簿引用面**：本战役 `m5_scheduling/补挖波_20260925/06_f83_automation_crew.md`、`m3_governance/0*_f10*.md` 等以族路径为真源指针；⑤**跨族引用**：`sop/audit_prompts_20_ai.md`（22 域定义唯一真源，被 crew_policy §4.2 消费）、`backtest_system_sop/sop_c_strategy_library_intake.md` |
| 自动化触发 | 三条生成/巡检通道（均**非**计划任务，属 commit/派生同步触发）：①`scripts/governance/d3_metadata/generate_rule_catalog.py`（rule_catalog_registry 生成器，README"生成器产出"口径对应件）；②`scripts/governance/d1_structure/batch_create_index_md.py`（**族内 index.md 批量生成器**——正是 `library_sop/index.md` 缺失的现成修法，零重造）；③`scripts/governance/d1_structure/sync_policies_index.py`（policies 索引同步）；④提交面触发=`commit_derived_sync.py` 与 `commit_queue_landing.py` 两处引用 `rule_catalog_registry`（grep 实测）→ 派生册在 commit/落地时重生成；⑤门禁触发=`gate_registry.yaml:68-74 GATE-NAMING`（`files_trigger` 型，staged 新增才跑）。**族本体（44 个 .md）无 daemon/无事件件**——族是静态真源层，符合其定位。 |
| 真源与注册表 | ①**地图真源**=`sop/README.md`，frontmatter `module_id: SOP-INDEX-001 / doc_type: index / ttl: permanent / version: 1.6.0 / status: active / owner: ZephyrAlpha-Owner`（实测 :1-9）；②**ROOR 条目**=`docs/registry_of_registries.yaml:271-279` REG-DOC-001（physical_path=`_registry/catalogs/rule_catalog_registry.yaml`，`maintenance: manual`，`entry_count: 256`，description "153 个文档的元数据（与 PS-REG-018 同源；2026-06-26 P2-1 向内收——document_metadata_index_registry.yaml 已删除，REG-DOC-001 重定向至真源）"）——⚠ **`sop/` 目录族本身在 ROOR 无独立 registry_id**（族清单的真源只有 README 表格＋ls，无机读册）；③**PS-REG-018**＝rule_catalog 的另一个名字（ROOR :272/:279 双称）；④宪法 §6.2＝地图的宪法级指针；⑤`.trae/rules/project_rules.md:57-68`＝PRE-OP 强制读族声明面 |
| 门禁与质量尺 | **两条真跑的门（非装饰）**＋**一条引用悬空**：①`gate_registry.yaml:68-74` **GATE-NAMING**"命名增量守门（--check-new，只拦 staged 新增重名 #ARCH-PRECOMMIT-INCREMENTAL）"，entry=`python scripts/governance/d3_metadata/check_naming_convention.py --check-new`，:72 口径"warn-only 违规走 gate-naming-audit（CI/manual）清零"；②:79 **GATE-NAMING-AUDIT**"全仓命名审计+SSOT一致性（不阻断）"；③被引规则确实实现：`check_naming_convention.py:32`"N-11 文件名后缀与 doc_type 一致性检测"、:660 实现块、:714 上报 `rule="N-11"` → **README 引的"N-11"是规则号、不是 gate_id**（`grep -n "N-11" gate_registry.yaml` = 0 命中）→ 人读可解、机读不可解析（病灶 2）；④命名闸之外**没有"族归属正确性/索引齐备性"尺**：`library_sop/index.md` 缺失无人拦（§七第 3 条实测 10/11），README 表格条目数与实盘目录数无对账尺（病灶 1 之所以能同时存在三套口径）；⑤`SOP-INDEX-001` 在 src/scripts 的 .py 里**零消费**（`grep -rn "SOP-INDEX-001" --include=*.py src/ scripts/` = 0）→ 双通道中的 capability 通道未成立（病灶 3） |
| 当前运行状态 | **黄**：①地图在盘且在用（v1.6.0、ttl permanent、README 表格 12 行＝11 族＋根件，实测定位可用）；②**族数三口径互斥**＝ls 实测 **11 目录**（`ls -d sop/*/ \| wc -l`=11）；总册 :201 同格既写"九族"又写"12 目录实测"并列 11 个名字；宪法 §6.2 写"九族索引" → 账面自相矛盾（文档矛盾=事故，宪法 §4.3）；③索引齐备度 10/11（`library_sop/` 缺 index.md，而 README:31 恰记该族"2026-09-24 补登，此前未入索引"→ 补登只补了父表未补族索引）；④族内文件实测 44 件（automation 2／backtest_system 7／construction 5／data_audit 2／data_ops 3／governance 7／library 1／mining 6／ops 4／review 4／trading_decision_map 3）。可复跑命令=§七第 1/2/3 条。 |

## 三、子模块清单（`ls`＋`grep`＋注册表三源交叉）

**3.1 族目录（11，ls 实测，含每族 .md 数与索引态）**

| 族目录 | .md | index.md | 一句话职责（README 表格 :20-31 口径） |
|---|---|---|---|
| `automation_sop/` | 2 | 有 | 自动化班底族（crew_policy，双引擎两班制）→ 详见 F83 册 |
| `backtest_system_sop/` | 7 | 有 | 回测体系族：SOP-A/B/C/D 四卷＋exam_policy |
| `construction_sop/` | 5 | 有 | 施工族：15 步闭环＋前端拆件＋文档七轮审＋车道纪律一页册 |
| `data_audit_sop/` | 2 | 有 | 数据审计族（产业链审计修复循环） |
| `data_ops_sop/` | 3 | 有 | 数据操作族（回灌/修复/判重/PIT/探针＋数据源全生命周期） |
| `governance_sop/` | 7 | 有 | 宪法与对齐族（宪法 L0 真源＋对齐清单＋施工台账方法论＋深度裁定方法论） |
| `library_sop/` | 1 | **缺** | 图书馆族（血肉编目 SOP）——README:31 自记"2026-09-24 补登" |
| `mining_sop/` | 6 | 有 | 挖矿研究方法论族（六向寻路＋骨架＋因子＋指标＋TDM 寻路） |
| `ops_sop/` | 4 | 有 | 运维协作与应急族（冲突三分法＋worktree 四证清理＋保命 Runbook） |
| `review_sop/` | 4 | 有 | 深度审查族（六轴法＋15 条缺陷模式库＋规则处置程序法六道闸） |
| `trading_decision_map_sop/` | 3 | 有 | TDM 地图族（逐层六步法＋S1-S9 九场消费规程） |
| **合计** | **44** | **10/11** | 根层另有 `README.md`、`index.md`、`audit_prompts_20_ai.md`（22 域方法论，受只读保护） |

**3.2 承载件（族组织层，非方法论本体）**：`sop/README.md`（SOP-INDEX-001，地图真源）｜`sop/index.md`（根索引件，与 README 并存 → §五 内收候选）｜`scripts/governance/d3_metadata/generate_rule_catalog.py`｜`scripts/governance/d1_structure/batch_create_index_md.py`｜`scripts/governance/d1_structure/sync_policies_index.py`｜`scripts/governance/d3_metadata/check_naming_convention.py`（N-11 实现，1953 行）｜`scripts/check_naming_convention.py`（29 行 shim，见病灶 4）

**3.3 注册表交叉**：ROOR 仅 REG-DOC-001 一条（指向 rule_catalog，非族目录）；`rule_catalog_registry.yaml` 有 per-file 条目（实测 crew_policy 那条 :4797-4800 带 `doc_type: policy`、`module_id: ''`）→ **族级注册表缺位**（病灶 5）。

**3.4 三源交叉结论**：ls 11 族/44 件穷尽；grep 得消费面（PRE-OP、README、ROOR、作业簿）；注册表得文件级但不含族级 → 交叉缺口=族清单无机读真源（=病灶 5，本环节最硬的一条）。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | **族数三套口径**：宪法 §6.2"九族索引"／总册 :201 标题"九族"＋同格"12 目录实测"（列 11 名）／ls 实测 11 目录 | 2026-09-14 七族重分类（README:15 记"11 个根层散文件归入五族"）＋ 09-24 library_sop 补登，散文计数未随目录事实重算；违宪法 §9.5（静态清单禁手工） | 计数一律改**字段/机生**：族清单由生成器产（复用 `generate_rule_catalog.py` 增加 by-family 汇总，或 `batch_create_index_md.py --audit`），宪法与总册引用字段不写数（§4.3"计数用字段勿写死在散文"） | 0.5 | 否（宪法/总册=热文件） |
| 2 | README 引"N-11 命名闸"在 `gate_registry.yaml` **查无**（grep 0）；闸实为 GATE-NAMING（:68）内的规则号（check 脚本 :32/:660/:714） | 规则号（N-xx）与 gate_id 两套命名体系，无交叉映射册 | 在 gate_registry 的 GATE-NAMING 条目加 `covers_rules: [N-01..N-05, N-08, N-11..N-13]` 字段（脚本 :1381 已按这套号分类），并让 README 引"规则 N-11（经 GATE-NAMING 执法）" | 0.3 | 可（只出判据，本车道不改 gate_registry） |
| 3 | README §使用纪律 3 宣称"双通道冗余可达"，实测其中 `capability_lookup` 通道**零消费**（`SOP-INDEX-001` 在 src/scripts .py 内 grep=0；capability_canonical_file_registry 里是 per-file token，不是族地图条目） | 单通道（rule_catalog）被写成双通道＝账面冗余度虚高；若 rule_catalog 生成失败则族地图**无机读可达面** | 把 11 族登记为 capability 卡（每族一张，或一张 `sop-family-map` 卡指向 README）→ 第二通道成立 | 0.4 | 可（判据）/1（落地） |
| 4 | 同名脚本两份：`scripts/check_naming_convention.py`(29 行) 与 `scripts/governance/d3_metadata/check_naming_convention.py`(1953 行真身)；且 `audit_directory_integrity.py:86` 与 `audit_broken_links.py:616` 以**裸文件名**引用（无包路径），`audit_precommit_incremental_baseline.py:62` 却写全路径 | 脚本搬迁后 shim 保留＋注释未带路径 → 三处引用不可机械解析；另有 `d1_structure/check_naming_convention.py` 被注释暗示但**实测不存在** | 注释引用一律改全相对路径；shim 加 `[DEPRECATED-PATH]` 指向真身（**只出判据不删**） | 0.3 | 否（涉多车道脚本面） |
| 5 | **族级注册表缺位**：ROOR 无"族清单"条目，族数只能靠 ls＋人读 README（本病灶是 1/3 的上游根因） | 目录组织层从未被当作注册表对象 | 新增 `sop_family_registry.yaml`（族名/路径/entry_count/index 态/generated_by）并挂 ROOR；由生成器产出，**MUST 声明替代的散文面**（§4.1 全资产净零） | 1 | 可（判据＋清单，登记交总筹） |

## 五、内收与合并机会（四判据）

- **同真源可派生→必并**：①`sop/README.md` 表格 ↔ 实盘目录 ↔ rule_catalog by-family 计数三者同源，应单向派生（病灶 1/5）；②`sop/index.md` 与 `sop/README.md` 同处根层、同为索引导航——**同域同对象候选并册**（须先读 index.md 确认非不同受众；本车道未读，列候选不并判）。
- **零触发零消费→退役**：候选=第二通道虚设面（病灶 3 若补则不退）；`scripts/check_naming_convention.py` shim 若实测零调用者可退役（**只登记，不删不改名**）。
- **同域重复簇→收敛唯一**：`governance_sop/`（7 件，含宪法 L0 真源）与仓库根 `AGENTS.md`＋`agents.md` 的关系＝"宪法正文 vs 宪法族索引"，当前宪法 v1 归档已入 governance_sop（宪法头部指针）→ 保持唯一入口在根，族内只放归档与方法论，**不再增第三份宪法副本**。
- **跨域不同对象→不并**：F116（族组织层）与各族本体（如 mining_sop 六向寻路法、backtest SOP-A/B/C/D）不并——后者各有自己的 F 格；F116 与 F106（术语三层翻译）不并（翻译层 vs 方法论层）。

## 六、自审闸三态

**判：待挖（部分）**——本册的 §二 六向与 §三 清单为实证齐备（每向 file:line/命令输出），可支撑施工判据；但**不宜据此宣称整格挖干**，理由=本环节是"元层"，其完备性依赖各族本体册，而以下三项未取：

1. `sop/index.md` 与 `sop/README.md` 的职责差（未读 → §五第 1 条判不了）。
2. `generate_rule_catalog.py` 是否真把 44 个族内 .md 全收入（未跑生成器对账；ROOR :276 `entry_count: 256` 与 :279 description"153 个文档"本身还互相矛盾 → 需以生成器实跑为准）。
3. 各族"唯一真源"声明与族内文件是否一致（例：automation_sop 族 README 称 crew_policy 为唯一真源，但 `cmd_ledger/automation_master_plan.md` 自称"调度唯一真源"＝两册互斥，已在 F83 册 §五第 3 条立案）。

**缺什么、要装什么最小观测量**：跑一次 `python scripts/governance/d3_metadata/generate_rule_catalog.py`（或其 --check 模式）取"族内文件覆盖数 vs ls 44"的差集；读 `sop/index.md` 首 20 行定受众。

**待裁**（已写入 `05_missing_p0/pending_rulings.md`）：病灶 1（计数改字段——涉宪法与总册两处热文件）、病灶 5（新增族级注册表的净零声明）、§五第 1 条（README/index 并册）。

**回写总册建议**：`00_全环节总册.md:201` ①删"九族""12 目录实测"两处写死计数，改"族数以 `sop/README.md` 表格为准（当前实测 11 目录，勿抄本行）"；②真源列补 `sop/README.md`（SOP-INDEX-001，现只写目录）；③`built` 改 **`partial`**，备注"族清单无机读真源、双通道宣称有一项未成立、library_sop 缺 index"。

## 七、复核命令

```bash
# 1) 族数三口径对照（本册最硬发现，一条命令出实盘数）
ls -d docs/01_policies_and_standards/sop/*/ | wc -l
grep -n "九族\|12 目录实测" docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md AGENTS.md | head

# 2) 逐族文件数（本册 §3.1 表全量复算，合计应=44）
for d in docs/01_policies_and_standards/sop/*/; do printf "%s " "$(basename $d)"; ls $d*.md | wc -l; done

# 3) 索引齐备度（预期 10/11，缺 library_sop）
for d in docs/01_policies_and_standards/sop/*/; do [ -f "$d/index.md" ] || echo "NO INDEX: $d"; done

# 4) N-11 与 GATE-NAMING 的引用断裂自证（预期：registry 0 命中，脚本 3 命中）
grep -c "N-11" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
grep -n "N-11" scripts/governance/d3_metadata/check_naming_convention.py | head -3
sed -n '68,82p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml

# 5) 第二通道未成立自证（SOP 地图 module_id 的机读消费，预期 0）
grep -rn "SOP-INDEX-001" --include=*.py src/ scripts/ | wc -l

# 6) ROOR 口径内部矛盾（256 vs 153）
sed -n '271,279p' docs/registry_of_registries.yaml
```
