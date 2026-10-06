---
ttl: task_bound
completes_when: W1-W4 全交付+红蓝两轮零+GW 落地+晨报呈报，随晨报归档
title: TDM 2.0 扩容+排班表对齐班 台账（st-tdm20-20260923）
owner: st-tdm20-20260923
session: st-tdm20-20260923
date: 2026-09-23
---

# TDM 2.0 扩容+排班表对齐班 · 台账

> 总包令=Owner 通宵总攻令 2026-09-23（对话内原文）；使命=把定桩成果长到图上，让周五 E2E 有"两面验收"的载体。
> 写域=本目录+config/trading_decision_map.yaml+TDM 交叉轴（decision_map.py/生成器/图表册）+W4 两脚本及其目录注册。
> 纪律：热册避让基建大队修复窗；自裁框架=通宵令原文；两轮零+红蓝；GW 落地；清临时。

## §0 直改主区登记（RULE-WORKTREE 降级申请）

登记原因（三条件并存）：
1. 写域窄且与在飞 844 脏文件近零交集（唯一交叠=config/trading_decision_map.yaml 上他会话遗留 5 行纯注释改动，见 §4-1）；
2. 基建大队修复窗内有 staged 热册（gate_registry/capability_canonical_file_registry 等），新开 worktree 的 merge-back 必撞其 staged 批；
3. 通宵令要求 GW 落地+队列正门，直改+claim+`--enqueue` 是既有验证路径（st-ulib3b/st-chainpile 同款）。
GW 计数+周审计照常生效。commit 后必做 `git log -1 --name-only` 核实归属。

## §1 输入真源与挖掘底账（W1）

| 输入 | 路径 | 用途 |
|---|---|---|
| 七层定稿 | docs/_working/chain_piling_campaign/01_layer_charter.md | L0-L6 层职责/时间分层铁律（今日输出→明日输入，同一时戳禁循环） |
| 源线谱 29 条 | 同目录 02_source_line_registry.md | L1 源线节点的 U1-U6 肉（母问/频率/PIT/考法） |
| 图谱 5 张+GRF1-18 | 同目录 03_graph_registry.md | L2 图谱节点+chain_refs 吸收锚 |
| 283 问施工映射 | worktree `.worktrees/st-chainpile-20260922/.../04_construction_map.md`（**只读引用，未合 dev，禁代改**；R1-R15 机械映射+85建/170接/28考三清单） | 节点 absorb 的问题面 |
| 283 问在库镜像 | 同目录 snapshots/registry_latest.yaml（row_count=283，PG 机生镜像） | 逐问回溯 |
| 传导链 583/873 | PG depgraph 库 ig_chain/ig_edge；口径真源=docs/_working/archive/2026-09/final3_campaign/w4_1_conduction_triage.md（583=链内存在≥1 传导边的链，canonical SQL 在案） | W4 吸收对齐（禁重画=复用该判据，不另立口径） |
| TDM 现状 | config/trading_decision_map.yaml（138 节点/194 边/schema v1.2） | 扩容基底 |
| 四层判定表 | CH c1_market.judgment_* 四表（DDL 真源 schemas/categories/judgment/） | W3 排班对齐 |

## §2 设计定案（自裁留痕，逐条可回溯）

- **D-1 层命名**：chainpile 七层（L0 元问题…L6 治理）≠TDM 内部漏斗层（L0 预案…L4 执行）。扩容轴落位 **entry_flow+layer=L9「知识供给层」**，避开漏斗 L0-L4 语义；L9 前缀满足 R1（entry→L*）。
- **D-2 不改 schema_version**：边语义四元组走 v1.2 内可选字段演进（payload_zh 2026-09-09 先例），不触发 MODIFY-GUARD 全家桶；新流程/新 flow 枚举同样不加（_FLOWS 保持 4 值）。
- **D-3 节点账**：新增 44=汇聚 1+源线 29（A16/B10/C3）+图谱 5+状态变量快照 3（V1 大盘/V2 情绪/V3 板块，对应宪章 L3 三件；V2 情绪聚合器=独立对话未建→红节点如实）+决策 2（D1 因子组合挖掘 E1C/D2 假设与考试方案登记）+验证 2（E1 一问一考考试链/E2 结论回传修正）+治理 2（Z1 问题治理与状态机/Z2 净零与资产对账）。138+44=**182 ∈ [150,250]** ✓。
- **D-4 边四元组**：`payload_type/frequency/lag/pit_proof`。新规则 R43：触及 L9 节点的边四元组全必填+payload_type/frequency 走封闭词表（error）；存量边缺失=pit_proof 显式 `legacy-unaudited`（194 条旧边脚本机械回填：frequency←to_node.point、payload_type←edge_type×from 节点型、lag←feedback=T-1 否则 0d、pit=legacy-unaudited）→欠账可探测不糊弄。lag 语义=**数据时点相对消费时点**（T-1=昨日数据今日用），时间分层铁律（01_layer_charter L88-93）在边上机械化。
- **D-5 传导链吸收（禁重画）**：不把 583 链画进 TDM；W4 以 `_XREF_SPECS` 新增 `chain_refs` 轴（R45 存在性校验）让节点引用 ig_chain；chain_registry.yaml 由新生成器从 PG 机生（生成物禁手改），判据 SQL 复用 w4_1 triage canonical。
- **D-6 W3「按图补齐该有的行」边界**：判定/结算分离铁律优先于补行——**禁向判定台账写入非实跑产出的行**（把 proposed 冒充实跑=造假）。交付=节点↔判定表↔档位契约对照表+实测行数+缺口读数（该有而没有=接线缺口，报而不造）；真补行=周五集成窗日转实跑产出（与"不日转，日转=集成窗"一致）。
- **D-7 PP-001 档位**：activation 字段（D32 门禁包枚举）按 point 机械映射补齐 PP-001 sleeve 决策链在图节点（盘前→premarket/盘中→intraday/盘后→postmarket/持续→continuous）。
- **D-8 板块反查盲区**：capability_canonical_file_registry.yaml 属基建修复窗 staged 热册——执行时该文件若仍未落地则**不直接编辑**，改为交付待应用补丁+移交记录；若已落地则同批补注册（16 个 sector 模块中英别名）。（执行时点复查：该册已 clean=基建批已落地→按后半句执行，CAS 原子写 2 条目。）

## §2b 执行期增补定案（D-9..D-12，同框架自裁）

- **D-9 library_tag_vocabulary.yaml 代登记豁免**：TDM 双测试套件 4 红传染（k1/k5/k6+主套件 1）根因=ulib3b 批(bb9777873f)落词表未同步 tests/trading/test_decision_map.py 的 _GOVERNANCE_EXEMPT（HEAD 级既有红，非本班引入）。处置=本班代登记豁免（治理类：图书馆标签词表 SSOT，MOD-LIB-003 lookup.py 消费，同 io_sector_sws_map 词表先例），**ulib 线复审可翻案改挂轴**。
- **D-10 图表册生成器断因修复**：generate_trading_map_diagram.py 的 FILE_PLAN 自 L0 预案批起即断（HEAD 实证 TDM-E-FLOW+L0 组 6 节点无归档，trading_map 册为陈旧生成物）。修复=流根+L0 归 00 总览册，L9 新开 08 册；重渲染 9 册对账 182=182 ✓。
- **D-11 framework_plans.yaml 重刷披露**：生成器重刷发现**既有漂移**——HEAD 派生计划权重自 C5 等权批(2026-09-14)起未重刷（0.140/0.105/0.070…旧值 vs TDM 现值 0.126/0.0945/0.063…），fw_backtest 指纹消费方一直用旧权重。本次重刷=sha 刷新+漂移闭合（sleeves 集合零变化，纯权重对齐真源）。**建议晨报呈报：消费框架计划权重的回测预检结果如涉 09-14 后区间需复核。**
- **D-12 折叠标量教训**：对 config/trading_decision_map.yaml 做文本级插入时，`decision_question: "…` 跨行折叠引号串内部插入会吞键（L1-AGG/F-C1 两处，已修复）——热文件文本手术锚点必须取标量闭合行之后的字段行，或先 yaml 实解析再定位。

## §4 风险与在飞件避让账（执行期更新）

1. （保持）TDM yaml 内他会话 5 行注释遗留随本班提交披露带走。
2. （保持）基建修复窗 staged 热册：执行时点复查 capability_canonical_file_registry 已 clean→sector 注册照做；**module_translation_registry.yaml 工作树含他会话在飞条目（library/tag_vocab_gate，未暂存）**——本班提交该册时披露吸收或延后（落位前复查）。
3. （保持）B7v2 尾批在飞（worktree）：未代落。
4. （保持）batch_creation_tokens.py.tmp CAS 残留：未清理，移交晨报。
5. **新增**：trading_map 图表册既有陈旧（D-10）+framework_plans 既有漂移（D-11）均非本班引入、随本班闭合，均已披露。

## §3 工作包账（终态）

| 包 | 交付物 | 状态 |
|---|---|---|
| W1 | 01_node_expansion_list.md（44 节点+60 边全字段设计+PQ 吸收计数） | 完成 |
| W2 | trading_decision_map.yaml 138→182 节点+194→254 边+R43+chain 轴+测试+图表册 9 册重渲染 | 完成 |
| W3 | 03_pp001_slot_alignment.md+activation 72 缺档补齐（182/182）+判定表实测+sector 反查 2 条目 | 完成 |
| W4 | generate_chain_registry.py+reconcile_chain_refs.py+chain_registry.yaml（873 链机生）+04 号首跑读数 | 完成 |
| 收尾 | 红蓝两轮+GW 落地+晨报六要素 | 完成（13fb043689/9c9b1276a8/24384af100/4590c975a9 四批落 HEAD；翻译册 2 条在 q-0026 随合并器环境债修复落地） |

## §3b 增补令·AGG 消费切换终批（Owner production 翻转确认，2026-09-23）

- **范围**：TDM-E-L1-AGG module_ref 改指 anchored_state_machine.py（module_id=MOD-REGIME-001 同族不变）；pf_alloc 运行时消费接线锚定四档 cap；L1 总闸 shrinkage 轴不动（两套各管各的）；旧 HMM 链全量保留一个月回滚窗（至 2026-10-23）。
- **判据复核**：①夜批连续 5 交易日零缺勤+当日更新=机械复核**通过**（09-14..09-22 七日全在，最新 09-22；首查误报断供系输出截断误读，已纠正）；②并行期无事故；③Owner 签字=本令。
- **实现**（agg-switch-design §2 方案A 已签数字）：allocation_inputs 新增 ④ 锚定 cap 供件（连续灰度曲线 cap=1−0.70×clamp((vol_pct−0.30)/0.70,0,1)，PIT 读最新行，旁路/无行/陈旧>7 日=applied False 留痕不盲用）；orchestrator 组合层新增 ANCHORED_CAP 裁剪（_LayerFacts.anchored_cap，与总暴露取 min 只减不加，违规标签可归因）；策略路由阈值未冻结**不接线**（设计稿原文随双轨证据定稿）。
- **一键切回**：创建 data/runtime/anchored_cap.disabled 空文件即整段旁路（下一次分配日生效，零代码零重启）；预案=06_agg_switch_rollback_plan.md。
- **测试**：新增 tests/pf_alloc/test_anchored_cap.py 13 例（曲线边界/PIT 三态/组合层裁剪链）；既有 pf_alloc 套件基线对照=crisis_gate 10F/sim_ledger 6F/event_wiring 挂死均为**基线既有红**（stash 对照实证，非本批引入）。
- **地图**：L1-AGG algo_note 追加切换史+note_confirmed=2026-09-23（ALGO-NOTE-SYNC 同批）；dq 精简至 67 字（R17 ≤100）；run_checks fails=0。

## §4a 旧版风险账（初稿留档）

1. **他会话遗留**：config/trading_decision_map.yaml 未暂存 5 行（note_confirmed 注释语 WO-14→B09 确认语，算法零变化，B09 批遗留）——非本会话所改；本班提交同文件时将一并带走并在 commit message 显式披露（吸收+披露制）。
2. **基建修复窗 staged 热册**（gate_registry/capability_canonical_file_registry/module_translation_registry 等）：提交前逐一复查 git status，仍在 staged 则避让（D-8）。
3. **B7v2 尾批在飞**（worktree 分支 chain-piling）：meta_question registry 代码未合 dev——本班节点 module_ref 如实记 null+structural，绝不代落他人尾批。
4. **batch_creation_tokens.py.tmp 残留**（scripts/governance/d3_metadata/ 下 CAS tmp 残留，非本班产物）：不清理，移交晨报呈报。
