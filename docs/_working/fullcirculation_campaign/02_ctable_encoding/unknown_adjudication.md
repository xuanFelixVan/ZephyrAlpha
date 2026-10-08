---
ttl: task_bound
completes_when: 全流通战役交付后归档
---

# 八图病历挂载编码归一——20 unknown 判读草案（附 DSC 裸册号补章 + 编码形态建议）

- 日期：2026-10-08｜班次：fullcirculation_campaign_20261008 / 02_ctable_encoding
- 性质：判读**草案**（判读权归 chief；本文件零改图零改册零改码，仅此一份交付）
- 输入真源：
  - `docs/_working/map_census/casebooks_family/encoding_normalize_map.yaml`（已落 dev，2026-10-05 机械盘点）
  - `config/strategy_production_map.yaml`（SP 图 341 节点；unknown 各节点行号随文标注）
  - `config/data_supply_chain_map.yaml`（DSC 图；DSC-13=L2603 / DSC-19=L3354 / DSC-20=L3424）
  - `docs/01_policies_and_standards/_registry/catalogs/casebook_registry.yaml`（八正典册+outside_registry 唯一反查册）
  - `config/governance_operations_map.yaml` casebooks_legend_zh（六册语义正典源）
- 补证材料（本次新增机械证据）：`docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`、`strategy_registry.yaml`、`config/league_registry.yaml`、`src/zephyr/factor/casebook/casebook.py`（L30/L60）、`docs/01_policies_and_standards/policies/c3_translation_pipeline_ruling.md`（§24）、`data/failures/` 文件族统计、`data/backtest_artifacts/runs/` 实测。

---

## §1 判读基准（正典反查面）

八册全表见 casebook_registry（勿背数）。与本案相关的判定锚：

| 册 | 身份 | 与本案关系 |
|---|---|---|
| CASEBOOK-001 | 数据对账案卷库 `data/failures/`（D_DATA） | DSC 图 8 挂载唯一宿主；唯一在位章码=#outage（E-8 约定） |
| CASEBOOK-004 | 审查发现两卷（D_GOV） | SP 候选行「预审判定台账」去向（非本班 unknown） |
| CASEBOOK-005 | 记忆索引 MEMORY.md | 字母码 MEM 宿主（形态节涉及） |
| CASEBOOK-006 | **已知数据缺口台账** `src/zephyr/data/config/known_data_gaps.yaml` | supply_sentinel 断供检测 gap_id 绑定台账；registry 记挂载建议 **DSC-14/DSC-16**（图面实挂 0） |
| CASEBOOK-007 | **采集打卡账本** `data/integrator_progress.db` task_runs | 逐任务执行留痕=应跑/打卡分母正门；registry 记挂载建议 **DSC-20**（图面实挂 0） |
| CASEBOOK-008 | **归档清单** `data/archive_manifest.jsonl` | 冷备归档逐表回执（含 compress_ratio）；registry 记挂载建议 **DSC-10A/DSC-10B**（图面实挂 0） |
| outside_registry | 提交撞墙死因案例册（module_id=CFG-COMMIT-DEATH-CASES-001，即 DCS）；data/sla/ 退役册（永久不授） | 「持 module_id/裁定身份者不入册（禁双重身份）」先例 |

**006/007/008 是不是 SP unknown 的答案：不是。** 三册皆 D_DATA 域，2026-10-07 补授（E-12 处方原件随 f2z §六配方遗失，按 chief 会话记录重建），挂载建议全部指向图12 DSC 节点——它们回答的是 encoding_normalize_map `fact_side_notes[0]` 记档的 DSC 图「建议面 vs 实挂面」差，不是策略生产域的 20 个 unknown。唯一词根近义陷阱：「回测run档案图书馆」vs CASEBOOK-008「归档清单」——对象不同（run 产物批目录 vs DB 表冷备归档回执），按 w5_1 铁律「跨域不同对象→不并」。

**判读口径**（本草案自设，chief 可推翻）：
- **可对位**＝语义与八册或 outside_registry 某条目同源，指针可直接改写为正典形态；
- **新章/新册候选**＝真病历语义但八册无宿主（多为域缺位），按 GOMAP L170 在案先例（「资源域专属病历册缺位=候选缺口，随上户口批呈批」）走呈批，不硬塞异域册；
- **不配挂**＝非病历语义（户籍/在制品/成绩册/产物档案），建议从 casebooks 字段摘除、由 module_ref/data_refs/真源文件承载。

---

## §2 SP 图 20 unknown 判读表（11 种自由名）

| # | 自由名（行数） | 节点（行号） | 挂载点语义（该机制翻什么账/犯什么病） | 判读 | 依据 |
|---|---|---|---|---|---|
| 1 | 模型版本注册表（1） | FAC-E1E-M-008（L1234，dir:_domain_machine_learning_train/model_version_registry） | ML 模型版本出生登记/版本台账：哪个版本何时出生、被谁引用 | **不配挂**（出生登记=户籍册，非病历） | 节点自述「版本台账」；无失败/教训记录面；八册无版本域；为登记册造章无内收对象（净零）。版本引用关系由 module_ref 承载即可 |
| 2 | 翻译件台账（1） | FAC-E3-M-076（L2595，MOD-BT-190 管线事件持久化） | C3 翻译管线：外来策略经翻译成标准件落盘（scripts/backtest/translated/）→积压扫描→auto 批测→及格件自动晋级；台账=到达/积压/批测流转记录 | **不配挂**（在制品流水台账，记「还有什么没跑」非「犯过什么病」） | c3_translation_pipeline_ruling.md §24 全链机械环节自述；八册无翻译域；回测对象预注册另有 REG-BTB-001（backtest_backlog.yaml）持身份承载，台账身份不缺 |
| 3 | 回测run档案图书馆（1） | FAC-E4-M-007（L2774，MOD-BT-022 ⑤报告聚合判定） | 回测 run 批目录档案库（data/backtest_artifacts/runs/，实测 191 批），聚合判定从此取 run 产物 | **不配挂**（产物档案馆=资产库非病历册；「图书馆」自述即档案语义） | trigger_facts source 即该目录；与 CASEBOOK-008 词根近义但对象不同（§1），w5_1 不并；档案路径属 store_refs/data_refs 语义 |
| 4 | 试验台账红证（4） | FAC-E4-M-011（L2838 印教材）/ M-012（L2853 双轨对照器）/ M-013（L2868 成本验证件）/ M-023（L3071 批末记账红证（病历页）） | P0 试验链证据件：regime 历史印证、新旧状态对照、成本验证、批末记账红证页（审计留痕） | **新册候选**：收编 `trial_ledger_registry.yaml` 为正典册（CASEBOOK-009 候选），红证=其「批末记账」章 | 物理宿主 trial_ledger_registry.yaml（ttl:permanent、doc_type:register、题名「全局累计试验数账本（N 账本，MOD-BT-200）」）；M-023 节点名自述「病历页」；八册皆 D_DATA/D_GOV 域无试验域；trial_ledger 无 module_id 头→授册路径开放（对比 DCS 因持 module_id 只能留 outside_registry）。旁注：M-012/M-013 fac9_03 实测零触发零消费，若随内收退役则该两行挂载随之消解 |
| 5 | N试次账本（1） | FAC-E4-M-020（L3014，MOD-BT-200，节点名自述「FDR 预算证据位，病历册」） | 全局累计试验数（FDR 预算分母）的计数面 | **新册候选**：与 #4 同宿主同一册——trial 册的计数面（#N试次 章）与红证面（#红证 章）= 一册两章 | trigger_facts source 直指 trial_ledger_registry.yaml（entries=8）；节点名自证「病历册」；同册两面避免册碎片化 |
| 6 | 过拟合裁定档案（1） | FAC-E4-M-050（L3403，dir:_domain_simulation/overfitting_protection_gate 过拟合防护门） | 防护门裁定记录：哪个策略被拦、凭什么证据判过拟合（判定书） | **新章候选**（宿主=#4/#5 之 trial 册——裁定对象=策略试验，同域同源；章候选 #过拟合裁定） | 真·病历语义（裁定=判定书）；八册无裁定类（RV=治理域审查发现，对象域不同；ruling_registry=治理裁定亦不同物）；与因子/试验域同源宜并册不另立 |
| 7 | 因子研究案例库（1） | FAC-E4-M-053（L3440，MOD-L02-027，data/databases/factor_casebook.db） | 因子研究成功/失败→修复病历本（自持案例库） | **新册候选**：授正典册号收编（CASEBOOK-010 候选），或按 DCS 先例走 outside_registry（锚=「92 号清单 D2 裁定授权新库」） | `src/zephyr/factor/casebook/casebook.py` L30「92 号清单 D2 裁定授权新库」+ L60 DEFAULT_DB_PATH——裁定授权身份在案；节点自述「成功/失败→修复病历本」=最标准的案例册形态。**事实旁注**：主区 data/databases/ 当前无 factor_casebook.db 文件（授册前应核实初始化状态；身份由裁定+代码锚定，不依赖文件在位） |
| 8 | 复现演练档案（2） | FAC-E4-M-063（L3557，scripts/backtest/replay_drill.py，节点名自述「病历/质量」）/ FAC-E7-M-022（L4327，crisis_drill_monthly.py 月度危机演练件） | 历史日复现演练与月度危机演练留档（故障响应彩排记录与发现） | **新章候选**（trial/策略域册「演练」章） | 两节点皆自证病历语义；演练记录含翻车彩排发现=病历价值在；八册无演练类；单独立册过细（净零），并入策略域册作章最省 |
| 9 | 考试成绩+判定书台账（1） | FAC-E6-M-001（L3836，MOD-BT-078 策略台账查询器） | 策略考试成绩与判定书查询位：candidate151/backtest8/sim2 生命周期状态+判定 | **可对位 → outside_registry（REG-STR-001）** | 物理宿主 `strategy_registry.yaml` 持 module_id=REG-STR-001 身份；按 outside_registry 先例（DCS=CFG-COMMIT-DEATH-CASES-001 同款「持身份者禁双重身份不入册」）；trigger_facts source 直指该册。落地形态=outside_registry 增列 REG-STR-001 条目（或指针语法 CASEBOOK-EXT:REG-STR-001，随 §4 形态裁定定） |
| 10 | 模拟盘病历族（3） | FAC-E7-M-003（L4082，sim 治理建议生成器，SIMGOV 53 批）/ M-007（L4151，判定台账表结构（病历册））/ M-020（L4304，平台日刊生成器（病历）） | 模拟盘运行病历族：治理建议、判定台账、日刊三件（策略上岗实习期病历） | **新章候选**（策略域册「模拟盘」章） | M-007/M-020 节点名自证病历册/病历；八册无模拟盘类；三件物理载体分散（SCR-SIMGOV* runs、判定表、日刊）恰需统摄章。备注：E6「衰减死因册→DCS」候选行若 chief 采信，衰减判定件归 DCS 与模拟盘病历族整体不拆挂并不矛盾（对象域各异） |
| 11 | 联赛档案（4） | FAC-E7-M-015（L4245 联赛注册表·赛马计分板）/ M-016（L4257 打包器（病历册））/ M-017（L4269 月度快照）/ M-018（L4281 复原器） | A/B 联赛注册/计分/月度快照/档案打包复原（champion-challenger 赛马档案） | **双口径，主判=新章候选**（策略域册「联赛」章）；备选=不配挂 | 主判依据：M-016 节点名自述「病历册」、四节点 purpose_tag 均病历有人翻；备选依据（窄口径）：赛马计分板本体=成绩档案非病历经，且真源 `config/league_registry.yaml` 已是 ttl:permanent 唯一登记真源（组席位/参赛档案路径/判定窗挂单+review_policy 内嵌 snapshot_dir/archive_root=data/backtest_artifacts/league），自持无需册号。若采备选：casebooks 摘除、档案路径由 league_registry 真源承载 |

**分布汇总**：可对位 **1 行/1 种**（#9）｜新章/新册候选 **16 行/7 种**（#4–#8、#10、#11）｜不配挂 **3 行/3 种**（#1–#3）。
**收敛观察**：#4–#8、#10、#11 共 16 行可收敛为**至多两个新册**（trial/策略域病历册 + 因子案例册），不必一自由名一册——净零友好路径。

---

## §3 DSC 图 3 裸册号行补章判读

章码现状：八册无章码枚举真源，唯一在位章码=#outage（E-8 约定：断供事故案必落 CASEBOOK-001，文件名前缀 outage_）。`data/failures/` 盘面主体族=YYYYMMDD_\<check\>_HHMMSS.json 逐任务告警案卷（1.5 万件级；outage_ 前缀件主区当前 0 件——E-8 为前瞻约定或案卷在冷库，落地核实归落地批）。

| 节点 | 现指针 | 判读 | 依据 |
|---|---|---|---|
| DSC-13（L2603 完整性巡检+新鲜度哨兵，purpose_tag=break_detect） | CASEBOOK-001（裸） | **补章候选 #alert**（新章：巡检告警案卷族） | 该节点 store_refs 第一项=告警件 data/failures/*.json（key=yyyymmdd+check+time）——正是 CASEBOOK-001 的盘面主体族，却无章可指；#outage 是特族（断供事故），主体族反缺章。补 #alert 使「主体族有章、特族有章」对偶完整 |
| DSC-19（L3354 破损 part 自愈探测器，purpose_tag=break_detect） | CASEBOOK-001（裸） | **归 #outage 章**（不新造章） | 破损 part 事故=供给断伤族，E-8 语义（断供事故案）覆盖 part 级破损（09-25 0-byte parts 事故即族内案型）；一事故族一章=净零。备选：若 Owner 认定破损≠断供需分案族，再立 #corrupt_part 章（留 chief） |
| DSC-20（L3424 任务级对账，purpose_tag=schedule_complete） | CASEBOOK-001（裸） | **双判读**：① 补章候选 **#task_reconcile**；② **增挂 CASEBOOK-007** | ① 案卷文件名 *_integrity_check_task_reconcile_* = 册 scope_zh 主体名（task_reconcile 族 JSON），DSC-20 是该族唯一生产者（store_refs 第一项）；② registry CASEBOOK-007 scope_zh 明记「图12 挂载 DSC-20」，且 DSC-20 store_refs 第二项=打卡台账 integrator_progress.db task_runs（分母真源）——「建议面 vs 实挂面」差在本节点闭合 |

**顺带呈批**（非本班判读义务，但同差同批最省）：registry 记 CASEBOOK-006→DSC-14/DSC-16、CASEBOOK-008→DSC-10A/DSC-10B 挂载建议，图面实挂均 0——建议随本次编码归一落地批一并闭合或显式废止建议行（建议面与实挂面长期分叉=文档矛盾事故温床，宪法 §4.3）。

---

## §4 家族正典编码形态建议：正典册号 vs 字母册码

**现状机械事实**：
- 字母册码#章：dev_delivery_map 81 指针（AP#域一、MEM#1…）＋ trading_day_cycle_map 35 指针（MEM-F13#断供补数…）＋ GOMAP 图例（AP#域三、RV2#缺口(R2-F2)、MM#全册）——已达标两图+图例真源全用此形态，存量 116+ 指针；
- 正典册号#章：DSC 图 8 指针（CASEBOOK-001#outage）——新落图用此形态；
- casebook_registry（唯一反查册）主键=CASEBOOK-NNN；字母码九组映射目前仅是草案表（letter_code_map_draft），非结构化真源；
- 字母码体系已实证会引用未授号册：MM 挂载 28+ 处但八册+outside_registry 均无对应（pending_unregistered）。

**建议：CASEBOOK-NNN#章 为家族统一指针键；字母码降级为 registry 条目显示字段（display_code），不作指针语法。**

理由：
1. **反查零跳转**：registry 主键=指针键，「指针可解析」变成单表机判（cv/gate 工具链最短路径）；字母码键则每图每次反查都要过一道字母码→NNN 映射。
2. **未登记不可引用成为机械约束**：MM 案例证明字母码可脱离 registry 漂移（引用未授号册无人拦）；NNN 主键下不存在「编了码但没上户口」的指针。
3. **扩容零语义成本**：新册自增 NNN 即可；字母码需造新字母（语义记忆负担+词表膨胀）。
4. **净零内收**：letter_code_map_draft 九组映射表收敛为 registry 字段（草案表退役并入正典），一套键不是两套——避免 L0 层刚废止同义异名字段（dev_delivery_map L284 先例）之后又在编码层再造双键。

**成本与阻塞项（如实呈报）**：
- 已达标两图 116+ 指针需批量改写（机生面可脚本化；dev_delivery/GOMAP 的 casebooks 属人工语义层，改写批须 chief 排批）；
- **阻塞项①**：MM 未授册号——不授号则图13 的 28 个 MEM-F13 指针无 NNN 可写，上户口批是前置；
- **阻塞项②**：RV/RV1/RV2→CASEBOOK-004 的卷级分派（册级映射已 high，章级「卷一/卷二」分派语义留 chief）；
- MEM-F13 的 9 主题簇章系（12_casebook_matrix_d13.yaml chapter_system）需随改写映射为 CASEBOOK-005#\<章\> 形态。

---

## §5 落地清单提示（chief 用）

1. SP 图改码批：可对位 1 行改写 + 不配挂 3 行摘除 + 新章/新册候选 16 行挂起待授册呈批（勿在授册前改写为自由名别名）；
2. DSC 图补章批：DSC-13 #alert、DSC-19 #outage、DSC-20 #task_reconcile+增挂 007；#alert/#task_reconcile 为新章，需在 E-8 章码约定真源同步登记（章码枚举键目前缺位=本班发现的真源缺口）；
3. 新册呈批（净零声明模板）：CASEBOOK-009（trial 册）声明收编 trial_ledger_registry.yaml 路径身份+SP 图 16 unknown 挂载；CASEBOOK-010（因子案例册）声明收编 92 号清单 D2 裁定授权库；均须先核实 factor_casebook.db 与 trial 台账在产状态；
4. CREATE-GUARD：本文件为新建 .md，落地批须随批登记 creation_token（本班只写此一份，未动其他文件）。

## §6 本班未做（边界重申）

零改图、零改册、零改码、零 commit；MM 上户口/RV 分派/新册授号/两图指针改写均为 chief 裁定后的落地批事项，本草案仅提供判读依据。
