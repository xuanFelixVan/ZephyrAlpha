---
ttl: task_bound
completes_when: 全流通战役交付后归档
---

---
campaign: fullcirculation_campaign_20261008
stage: 00_skeleton
doc_type: prescription
title: 全流通战役·链间交接面缺口挖矿判定与处方（7 处）
date: 2026-10-08
upstream_pair: skeleton_findings.md §4 交接面账 + chain_inventory.yaml 各链 handoffs 段
method_note: 只读调研（图 yaml 快照+注册表+代码），零 config 改动；TDM 读 HEAD/dev 与工作树（两者内容一致，git diff HEAD 为空）
---

# 全流通战役 00_skeleton·交接面缺口处方

> 输入=skeleton_findings.md §4.3 缺口清单（双侧零 2 + 单侧缺 5）。
> 每缺口三段式：**挖矿判定**（码通 vs 图断）→ **证据链**（yaml 行号/注册表/代码路径）→ **处方**（哪个图哪个键加什么，机械性分级）。
> 术语约定：**图级可解析边**=图 yaml 内存在以对图节点 id（DSC-*/TDM-*/D11-* 等）为端点的边/refs 条目，图游走器可直走；**第三真源中转**=经共享注册表（如 data_asset_registry DS-*）join 才能连通；**散文半记**=note/name/consumers 文本提及对图但无机读键。"码通图未记"=真实链路在代码与注册表成立、仅图际边载体缺失；"真实断链"=代码/数据面本身断。

## 0. 结论速览

| # | 缺口边 | 挖矿判定 | 立即机械闭合 | 需他车道 |
|---|---|---|---|---|
| A | 图12→图7 供料边（双侧零） | **码通、图未记**（图12 侧实为"半记"，图7 侧零记） | 半闭：图12 侧可机械 | 图7 侧须 TDM 车道 |
| B | 图16→图10 立法边（双侧零） | **码通、图未记**（图16 侧实为"机制级已记+boundary 半记"，图10 侧零记） | 全闭：双侧生成器语义层 | 无 |
| C1 | 图9→图7 策略上岗（TDM 侧缺） | 机制衔接真存在（strategy_mounts 186 处），缺图级回引 | 否 | TDM 车道 |
| C2 | 图9→图15 卡生命周期（SPM 侧缺） | 单纯缺记 | 是（手工图直改，附幂等风险注记） | 无 |
| C3 | 图7→图13 时序投影（TDM 侧缺） | 图13 侧载体健在，TDM 侧零真引用 | 否 | TDM 车道 |
| C4 | 图14→图11 Step10 交界（图11 侧缺） | 图14 侧载体健在，图11 侧零引用 | 是（生成器语义层） | 无 |
| C5 | 图10→图11 治理守护（GOMAP 侧缺） | 图11 侧机制面 251 gate 引用健在，GOMAP 侧仅 1 处散文 | 是（生成器语义层） | 无 |

- **可立即机械闭合：4 处全闭（B、C2、C4、C5）+ 1 处半闭（A 的图12 侧）**；3 处 TDM 侧改动（A 图7 侧、C1、C3）挂账 TDM 施工车道（MM 态，随其血肉批落地）。
- 两处附带发现（顺手修，见 §3 附加）：GOMAP `out_of_scope_refs` 死路径；panorama `ssot_note_zh` 过期注记。
- 骨架清点两处口径修正建议（不改骨架件本体，落地时随批更正）：见 §4。

## 1. 双侧零记载 2 条——挖矿判定

### 1.1 缺口 A：图12 DSCMAP-012 → 图7 TDMAP-001（数据供料边）

**判定：码通、图未记——非真实断链。** 真实供料链在任务/代码/注册表三层全部成立；缺的只是"图级可解析边"：两图 yaml 中没有任何以对图节点 id 为端点的边条目，图游走器必须经第三真源（data_asset_registry DS-*）join 才能连通。骨架所记"两侧图内均无互引"在图 12 侧被实测局部推翻（4 处 `TDM:DS-*` consumers 注记 + DSC-HA 交接节点命名），在"可解析边"口径下成立。

**证据链（生产腿→中转真源→消费腿，全代码/注册表级）：**

1. **生产腿（图12）**：DSC-01 盘后批量采集挂 `task:kline_daily_incremental`，`data_refs: c1_market.kline_daily`，freshness_evidence `verdict: fresh`（config/data_supply_chain_map.yaml:227/231/254-261，末开盘 09-24 双版并报 10,108,049/10,108,162 行）。
2. **中转真源（共享注册表）**：data_asset_registry.yaml（REG-DATAFLOW-001）`DS-150 = c1_market.kline_daily`（:6459）、`DS-170 = c1_market.kline_sector`（:7304，`produced_by_job: kline_sector_incremental`）、`DS-104 = event.news_data`（:4618）、`DS-107 = event.news_sentiment_window`（:4661）、`DS-232 = c3_fundamental.financial_derived`（:9778）。
3. **消费腿（图7）**：TDM-E-L1-S1 大盘指数传感器 `data_refs: [DS-150]`、`module_ref: src/zephyr/regime/features/index_sensor.py`（trading_decision_map.yaml:429-430）；E-L2 板块层多节点挂 `[DS-059, DS-170]`（:680/713/781/910/943/1006/1040/1070/1103/1386/1418/1450 等）；TDM-E-L2-09 催化剂识别挂 `[DS-107]`（:1484，`fallback: DS-107 缺失→催化剂维度降权`）。代码面：index_sensor.py 头注"纯函数核，零 IO；指数日线由调用方从 DS-150 算好注入"（:4），实际读表腿=`src/zephyr/regime/regime_feature_builder.py`（ClickHouse kline_daily 惰性加载，:201/:695-696）——**数据链末端环节（DSC-01 采集落库）真正喂给决策链首端环节（E-L1 传感器族）的接线在代码成立**。
4. **图12 侧半记证据**：consumers 字段 4 处显式 TDM 注记——DSC-01 `TDM:DS-150等16表/约64点`（:318）、DSC-02 `TDM:DS-170等6表/15点`（:455）、DSC-03 `TDM:DS-104/DS-107×5`（:600）、DSC-08 `TDM:DS-232`（:1304）；DSC-HA 交接节点名"交接 A：派生表出图（→ TDM 因子 / 工厂 / 图13 消费）"+ consumers `pass-through:派生表经ch_reader出图→TDM/工厂/图13`（:1824-1825/1876）+ `store_refs: 消费端交叉锚 location=data_asset_registry.yaml（DS-*/JOB-* 标识符）`（:1848-1850）。
5. **图7 侧零记证据**：TDM 全文 0 处 `DSC-`/`DSCMAP` 节点引用；唯一图12 提及是 1 处散文——TDM-E-L1-S1 `module_mounts_influence` MOD-MKT-001..007 逐条"编制在图12数据链（伸手供给全传感器族）"（:439）；187 处 `data_refs` 命中（含 1 行 schema 头注，节点级 186）全部指向 DS 注册表、无一指向图12 节点。

**辨析：链上真断点不在此边上。** 供料链自身的断点已由图12 显性化为 gap 件（DSC-GAP-NAV/EXECEP/FFVAL/FFSIG 四张等未产表——`c1_market.account_nav_daily` 三消费方在等、写器零接线；factor_feature_value/factor_signal 表未建）。即：**交接面缺的是"记载"，数据链缺的是"接线"，两病两账**——SPM 侧 FAC-E8 已实证消费 `c1_market.account_nav_daily`（strategy_production_map.yaml:410），恰是 gap 腿的下游受害者。

**处方 A（分两半）：**
- **A-12（图12 侧，可机械，生成器车道）**：在语义层真源 `docs/_working/map_build/fig12_datachain/00_skeleton.md` §2 交接 A 段做目标具体化，再重跑 `generate_data_supply_chain_map.py`：① DSC-HA 的 consumers 由单条 pass-through 散文升格为机读键 `handoff_out_targets: [TDMAP-001(via DS-*, 174 点), strategy_production_map, trading_day_cycle_map]`；② 把既有 4 处 `TDM:DS-*` consumers 注记的口径从口语计数（"等16表/约64点"）规范为可对账的 DS-id 列表（真源=data_asset_registry，分母=11 卷 174 点）。DSC-HA 的 note 已自我声明"保留交叉锚（DS-*/JOB-*）"——本处方是把既有设计意图机读化，非新增语义。
- **A-7（图7 侧，需 TDM 车道协调，挂账随血肉批）**：TDM 为手工图（无 generator）且 MM 态他队施工中，禁本批触碰。建议在 TDM 头部加一行 map 级上游声明（schema 1.2 允许 frontmatter 附近注释约定）：`# 上游供料图: DSCMAP-012（data_refs 经 data_asset_registry DS-* 中转；交接面=DSC-HA）`，并把 :439 散文中的"图12"升格为 `module_mounts_influence` 同键位的规范引用。落入 TDM 车道的 10_hop_mining/07_tdm/ 批次清单。
- **对账腿（可机械，独立于两图）**：DS-* join 本身可验——`TDM 节点 data_refs ∪ data_asset_registry.produced_by_job ∪ DSC 节点 task_family` 三表对账脚本化（只读），作为 A 边的机械验收盘，防止两侧记载各自漂移。

### 1.2 缺口 B：图16 governance_legislation_map → 图10 GOMAP-001（立法供给运行时边，裁定#486 ①激活）

**判定：码通、图未记——非真实断链。** 裁定生效进入治理运行时有四条在代码成立的消费路径；图16 侧其实已有"机制级记载"（D16-N7 消费方索引）与 boundary 半记，但两图均无以对图 map_id/节点 id 为端点的边条目。骨架所记"两侧均无互引"在图16 侧被局部推翻。

**证据链（立法真源→四条消费路径→运行时归属）：**

1. **立法真源**：ruling_registry.yaml（PG 账本 REG-RULING-001 投影，单写者 render）；裁定#486 本身 `status: active`（ruling_registry.yaml:4183-4190），一裁两项：①图16 准入+本边激活、②立项卡呈批制。
2. **消费路径①（授权通道）**：active 条目 `approved_paths`（fnmatch+目录前缀双语义）→ `approval_resolver._ruling_channel()`（src/zephyr/gov_enforcement/commit_gates/approval_resolver.py:266-292，"四值枚举铁律：仅 active 构成授权"；marker 通道同文件堵假号洞）→ 被 `protected_paths_gate`（PROTECTED-PATHS，in_process_gate_registry.yaml:535-540，enabled）、`create_guard.py`、`takeover_pending_gate.py` 三处调用。
3. **消费路径②（引用原子性门74）**：`ruling_reference_gate.py`——新增 裁定#NNN 引用必须同 commit 在册，L2 hard block（gate_registry.yaml:1836 RULING-REFERENCE，已并入 REFERENCE-INTEGRITY）。
4. **消费路径③（提交原子性）**：RULING-COMMIT-VERIFIED（commit-gate priority=109，gate_registry.yaml:1825；in_process_gate_registry.yaml:136）。
5. **消费路径④（生效投影）**：D16-N5 publish 快照/N6 render 投影（baseline.py 单写者）→ 册 yaml 供全部 gate 读取。
6. **运行时归属（=图10 域）**：上述门链运行宿主 git_commit_gateway 在 GOMAP families 机制层 12 处 path 证据挂载（governance_operations_map.yaml:1740/1891/1908/1924/1939/1954/2376/2393/2409/2426/2443/2460）；gate_engine.py 挂 L3 emergency_brake 机制 consumers（:355-360，trigger_facts total=2563）。**即：裁定→审批授权→门禁执行→提交落盘的完整运行时链在图10 域内真实运转。**
7. **图16 侧半记证据**：D16-N7 消费方索引（"审批通道（_ruling_channel：active+expires_at+approved_paths）、reference 类 gates、取号分母、对齐清单挂轴"，source_anchors=approval_resolver.py+next_ruling_id.py，governance_legislation_map.yaml:108-113）；D16-S2 active 态 anchor=approval_resolver.py（:47）；boundary 明文"不含图10 GOMAP 运行时面（治理运行地图管运行进程，本图管立法条目……不并）"（:29）——负面边界陈述亦为图际互引文本。
8. **图10 侧零记证据**：GOMAP 全文 0 处 `ruling_registry`/`governance_legislation_map`/图16 引用（"裁定"字样 3 处均为历史沿革注记，:196/202/233）；立法输入在图10 无任何载体。**附带发现①（死路径）**：GOMAP `out_of_scope_refs` 挂的"提交门禁体系"ref=`docs/01_policies_and_standards/_registry/catalogs/commit_gate_registry.yaml`（:101）**该文件不存在**——实存 catalogs/gate_registry.yaml 与 docs/03_modules/_domain_gov_enforcement/algo_flow/rule_bridge/commit_gate_registry.yaml。

**裁定#486 ③ 的口径提示（防误并）**：裁定明文"GOMAP 运行时章程不含立法（治理运行地图管运行面、本图管立法面，跨域不同对象不并，w5_1 判据）"——故本边的正确形态是**引用边/供料边，绝不可做成 GOMAP 挂载立法节点**（会把两图并域，违裁定）。处方据此选 `out_of_scope_refs`（引用非挂载）形态。

**处方 B（双侧可机械，各自生成器车道）：**
- **B-10（图10 侧，机械）**：GOMAP 的 `out_of_scope_refs` 是生成器保留的人工语义层（ssot_note_zh 明示），直接在该段新增一条（与既有"提交门禁体系"条目同构）：
  ```yaml
  - name_zh: 治理立法真源
    ref: config/governance_legislation_map.yaml
    note_zh: 立法供运行时（裁定#486 ①条件边）——active 裁定经 approval_resolver/_ruling_channel 与 RULING 族 gate 进入运行时门链；图10 管运行面、图16 管立法面（#486 ③ 不并）
  ```
  同批修复附带发现①：`ref` 改指实存路径 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`。改后重跑 `generate_governance_map.py` 验证语义层保留（families 不受影响）。
- **B-16（图16 侧，机械）**：图16 机生自骨架+账本，改动落语义真源 `docs/_working/map_build/fig16_legislation/00_skeleton.md` 机构段 D16-N7：note 补一句运行时归属（"消费方运行宿主=GOMAP-001 域 git_commit_gateway 门链/图11 D11-C05 执行面"），并在该节点加机读键 `feeds_map: GOMAP-001`（骨架 schema 若无此键则等价为 transitions/machinery 段加 `cross_map_edge: {to: GOMAP-001, basis: 裁定#486①}`）；重跑 `generate_governance_legislation_map.py`（counts 一致性判红会拦手改不回生成）。
- **顺手件（附带发现②）**：panorama_master_map.yaml `ssot_note_zh`（:14-15）仍写"图16（治理立法）未立，「治理立法→GOMAP10」条件边暂不入册"——与 nodes 段（图16 已立）和 edges 段（该边已入册，:114-117）自相矛盾，随 B 批更正该句为"图16 已立，条件边已随裁定#486 ①激活入册"。

## 2. 单侧缺 5 条——逐条判定

### 2.1 C1：图9 SPM → 图7 TDM（策略上岗，TDM 侧缺回引）

- **已有侧实测（SPM）**：4 处散文级 TDM 引用——FAC-E8 块"TDM 组合流对接未闭环=partial""TDM-F 地图 module_ref 九件全实证在盘"（strategy_production_map.yaml:401-406）、1 机制 `home_map: 图7 trading_decision_map`（:821）、"AI 舆情分析器（TDM 亦引）"（:1312）。机制面真源=TDM 节点 `strategy_mounts`（186 处节点级字段，TDM :99-...）。
- **缺侧实测（TDM）**：0 处 `FAC-`/`strategy_production_map`/图9 引用（grep=0）。
- **缺侧应记**：TDM map 级一条上游声明（与 A-7 同批同形态）：`# 产品上图: strategy_production_map（工厂 E8 组装产物经 strategy_mounts 挂载；SPM 侧 home_map 机制已互认）`；或在 TDM-E-L3-07 策略专属链节点加 `upstream_map_ref: strategy_production_map`。SPM 侧顺手把 4 处散文中的 2 处（FAC-E8 对接欠账、home_map）升格为节点级 `handoff_out: TDMAP-001` 边注。
- **机械性**：TDM 侧需 TDM 车道（MM 态）；SPM 侧手工图直改可机械（与 C2 同批）。

### 2.2 C2：图9 SPM → 图15 SCARD（卡生命周期，SPM 侧缺回引）

- **已有侧实测（图15）**：3+ 处——轴区分"本图 state_id=D15-S*、对象键=card_id；策略工厂 node_id=FAC-*"（strategy_card_lifecycle_map.yaml:37）、`node_id(FAC-*)`（:47）、"考试权只在 E4 咽喉"两处引 strategy_production_map.yaml:20（:1200/:1214）。
- **缺侧实测（SPM）**：0 处 `SCARD`/`D15`/`card_lifecycle`/图15（grep=0）。
- **缺侧应记**：SPM map 级加 handoffs 段一条入边镜像（或 E4 考试咽喉节点加键）：`product_state_map_ref: strategy_card_lifecycle_map（工厂产物登记为卡→13 态管辖；判绿判红权在 E4，图15 D15-S5..S8）`。语义最小、不复制图15 状态机（防 INV-1 型第二真源）。
- **机械性**：**可机械**。注记：SPM 为手工图（chain_inventory：无 generator 字段），直改无幂等再生保护——建议同批在 chain_inventory 或 90_ledger 记一行"SPM 手工图变更留痕"，并列入三张手工图幂等性风险整治池（skeleton §5-2）。

### 2.3 C3：图7 TDM → 图13 交易日循环（决策时序投影，TDM 侧缺）

- **已有侧实测（图13）**：20 节点 `tdm_refs` 挂 18 个 TDM 节点；laws 让渡二成文"决策内容不进图：任何'怎么判'唯一出路是 tdm_refs 引 TDM 节点"（trading_day_cycle_map.yaml:79）——该边是图13 的结构性字段，载体最重。
- **缺侧实测（TDM）**：0 处真实 D13/图13 引用（grep 唯一命中 :4701 "D7-D13 历史判准率"是数字区间非图引用；`cycle_refs: [CYC-STAT-*]` 经查只存在于 TDM 自身，非图13 轴）。
- **缺侧应记**：TDM map 级一条投影声明：`# 时序投影: trading_day_cycle_map（本图 18 节点被 D13 20 节点 tdm_refs 挂载；时刻值不搬家归图13 laws）`。节点级不加（让渡二反向同理：TDM 不复制时序）。
- **机械性**：需 TDM 车道（MM 态），与 A-7/C1 合并为 TDM 图头部"图际关系三行批"一次落。

### 2.4 C4：图14 施工链 → 图11 交付链（Step10 交界，图11 侧缺）

- **已有侧实测（图14）**：5 节点 `handoff_to` 显式挂 D11 目标（D14-01→D11-S01/S02/S09 等 14 个目标，construction_workflow_map.yaml:99-102 等；skeleton 记 D14-01/14/15/16/17 五节点）。
- **缺侧实测（图11）**：0 处 `D14`（grep=0）。
- **缺侧应记**：D11-S01 会话冷启动（图14 handoff_to 首目标）加 `upstream_map_ref: construction_workflow_map（Step10 交界：D14 五环节 handoff_to 本图 14 环节）`。
- **机械性**：**可机械**——图11 契约真源=docs/_working/map_build/fig11_delivery/00_skeleton.md（map ssot_note_zh 明示骨架人工语义层），改 skeleton 后重跑 `generate_dev_delivery_map.py`（生成器硬失败防空壳）。

### 2.5 C5：图10 GOMAP → 图11 交付链（治理守护交付，GOMAP 侧缺）

- **已有侧实测（图11）**：D11-C05 in-process 门禁链挂 `gate_cluster`（in_process 注册表 105 gates + shell 187 gates 指针，dev_delivery_map.yaml:204-223）+ 全图 37 处 gate_refs/gate_cluster（skeleton 计机制面 gate 引用 251 处）。
- **缺侧实测（GOMAP）**：0 处节点级 D11/dev_delivery 引用；仅 1 处散文（counts 注"DCS/AP/SV/RV 与图11 共挂，编制表一份多处引用"，:83）。
- **缺侧应记**：与 B-10 同段同批——`out_of_scope_refs` 加：`- name_zh: 交付守护面 / ref: config/dev_delivery_map.yaml / note_zh: 门禁机制面被 D11-C05 gate_cluster 挂载（251 处）；本图管运行时、D11 管交付环节`。
- **机械性**：**可机械**（生成器保留语义层，同 B-10 一次编辑两条）。

## 3. 处方执行账

| 处方 | 目标图 | 目标位置（yaml 键/语义层真源） | 改什么 | 车道 | 机械性 |
|---|---|---|---|---|---|
| A-12 | 图12 | fig12_datachain/00_skeleton.md §2 交接 A → DSC-HA `handoff_out_targets` 键 + 4 处 consumers DS-id 规范化 | 目标具体化 | 生成器重跑 | **机械** |
| A-7 | 图7 | TDM 头部注释 + :439 散文升格 | 上游供料声明 | TDM 车道 | 挂账 |
| A-验 | 跨图 | 只读对账脚本（DS-* 三表 join） | 机械验收盘 | 独立 | **机械** |
| B-10 | 图10 | GOMAP `out_of_scope_refs` 段（+死路径修复） | 立法真源 ref 条目 | 生成器保留层 | **机械** |
| B-16 | 图16 | fig16_legislation/00_skeleton.md D16-N7 → `feeds_map`/`cross_map_edge` | 运行时归属边注 | 生成器重跑 | **机械** |
| B-pan | 总图 | panorama `ssot_note_zh` :14-15 | 过期注记更正 | 手改+回生成 | **机械** |
| C1 | 图7+图9 | TDM 图头三行批；SPM FAC-E8 `handoff_out` | 上岗边回引 | TDM 车道+SPM 直改 | 挂账/半机械 |
| C2 | 图9 | SPM map 级 handoffs 或 E4 `product_state_map_ref` | 卡生命周期回引 | SPM 直改 | **机械**（附幂等风险注记） |
| C3 | 图7 | TDM 图头三行批 | 时序投影声明 | TDM 车道 | 挂账 |
| C4 | 图11 | fig11_delivery/00_skeleton.md → D11-S01 `upstream_map_ref` | Step10 入边 | 生成器重跑 | **机械** |
| C5 | 图10 | GOMAP `out_of_scope_refs`（与 B-10 同批） | 交付守护 ref 条目 | 生成器保留层 | **机械** |

**执行序**：第一批（本战役可自闭合，无车道冲突）= B-10+B-16+B-pan+C5（GOMAP/图16/总图一批）、C4（图11）、C2+A-12（手工图+图12 生成器）；第二批（TDM 车道挂账）= A-7+C1(TDM 侧)+C3 合并为 TDM 图头"图际关系三行批"，随 TDM 血肉批（10_hop_mining/07_tdm）落地；A-验 随第一批后跑一次作基线。

**风险与纪律**：
1. 所有机生图（10/11/12/13/16/总图）改动必须走各自语义层真源+重跑生成器，禁直改 yaml 后不回生成（counts 判红）。
2. SPM 手工图直改无幂等保护（C2/C1-SPM 侧）——变更须留痕并进手工图风险池。
3. B 边严禁做成 GOMAP 挂载（裁定#486 ③ w5_1 不并）；A 边严禁把 DSC 管辖延伸到消费端品质判定（DSC-HA note 自我声明"本图不再管其品质判定"）。
4. TDM 三处（A-7/C1/C3）挂账件在 90_ledger 登记待办，防与他队 MM 施工撞车。

## 4. 骨架清点口径修正建议（随批更正，不改骨架件本体）

1. skeleton_findings.md §4.1-1"图12↔图7 两侧图内均无互引"→ 建议修正为"图级可解析边双侧零；图12 侧有 4 处 TDM:DS-* consumers 注记+DSC-HA 交接节点（半记），图7 侧仅 1 处散文"。
2. §4.1-5"图16↔图10 两侧图内均无互引"→ 建议修正为"边载体双侧零；图16 侧 D16-N7 消费方索引已机制级记载+boundary 明文划界（半记），图10 侧零记"。
3. chain_inventory.yaml tdm/dscm/govops/govleg 四链 handoffs.recorded 字段同步上述口径（"缺"→"半记：…"）。

## 5. 内收对审附件（引用不展开）

- **189 个零消费治理机制**：清单真源=chain_inventory.yaml govops 段 `four_field_coverage_node_level`（consumers=261/450，缺 189，按层分布 L0:39 / L1:57 / L2:35 / L3:5 / L4:18 / L5:34 / L6:1）；对审判据=宪法 §4-2（零触发零消费→退役、同域重复簇→收敛唯一）；入口=skeleton_findings.md §5-3。本件不展开明细。
- **图12 ROOR 口径差**：REG-MAP-DSCM-001 称"四字段血肉已满（f2_done）"=结构满配（字段存在）而非语义满配（casebooks 非空仅 8/43）——chain_inventory dscm 段已带勘注，建议 ROOR 描述补口径词（同批内收对审）。

## 6. 本件不做的事（边界）

- 不改任何 config/ 文件（含 MM 态 TDM）；不建对账脚本（A-验仅处方）。
- 不补四字段血肉（挂图批管辖）；不判并/退/留/修（内收对审另批，本件仅附候选池引用）。
- 不动 14 条扇出合规边与 1 条双侧在册边（图12→图9，健康样本）。
