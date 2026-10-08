---
ttl: task_bound
completes_when: 全流通战役交付后归档
---

---
campaign: fullcirculation_campaign_20261008
stage: 00_skeleton
doc_type: findings
title: 全流通战役·骨架清点发现（全链路环节清单）
date: 2026-10-08
machine_readable_pair: chain_inventory.yaml
tdm_source_note: config/trading_decision_map.yaml 为 git MM 态（他队施工中）——本清点读 git dev 版快照，未读工作树版
---

# 全流通战役 00_skeleton 发现——全链路环节清点

> 机读真源=同目录 [chain_inventory.yaml](chain_inventory.yaml)（10 链 398 hop 逐环节五行记录）。
> 判据：四字段=挂图 SOP §4（purpose_tag/casebooks/trigger_facts/consumers）；`four_fields_ok`=四字段在该环节（或其直属机制）全部非空。
> 图族真源=config/panorama_master_map.yaml（图之图：16 图+22 语义边）；注册发现真源=docs/registry_of_registries.yaml（ROOR）。

## 1. 总数字

| 口径 | 数值 |
|---|---|
| 清点链数 | **10**（9 条环节链 + 1 册序列表[宏观序列映射，非环节链]） |
| 环节总数（hop 口径，9 链） | **382** |
| 环节总数（含宏观 16 序列） | 398 |
| 四字段空白环节（hop 口径） | **347 / 382（90.8%）** |
| 四字段空白环节（含序列册） | 363 / 398 |
| 在册机制总量（machinery_total 合计） | 1311（含 SPM 324 机制、govops 450 机制、TDM 311 挂载） |
| 交接面（全景总图语义边） | **22**（8 条异构语义边 + 14 条同关系扇出边[图11→各图"施工变更唯一入口"]） |
| 交接面缺口 | 双侧全无互引 **2** 条；单侧载体 **5** 条 |
| 生成器在册（幂等可再生） | 7/10 链；**TDM、策略工厂、宏观序列册 3 件为手工图（无 generator 字段）** |

## 2. 每链速览

| 图 | 链 | 环节数 | stage-only 口径 | 四字段空白 | 机制数 | 生成器 | ROOR 登记 |
|---|---|---:|---:|---:|---:|---|---|
| 图7 | 交易决策链 trading_decision_map（TDMAP-001） | 186 | 186 | 186 | 311 | 无（手工） | —（挂 alignment_checklist 家族） |
| 图13 | 交易日循环链 trading_day_cycle_map | 52 | 48 | 27 | 98 | generate_trading_day_cycle_map.py | — |
| 图12 | 数据供给链 data_supply_chain_map（DSCMAP-012） | 43 | 22 stage（另结构/分面/缺口件） | 38 | 25 | generate_data_supply_chain_map.py | REG-MAP-DSCM-001 |
| 图11 | 交付链 dev_delivery_map | 30 | 28 | 25 | 28 | generate_dev_delivery_map.py | REG-MAP-DEVDELIVERY-001 |
| 图14 | 施工链 construction_workflow_map | 28 | 17 | 28 | 10 | generate_construction_workflow_map.py | — |
| 图9 | 策略工厂链 strategy_production_map | 17（10 stage+7 lane） | 10 | 17 | 324 机制 | 无（手工） | — |
| 图15 | 卡生命周期链 strategy_card_lifecycle_map | 13 态 | 13 | 13 | 56 卡 | generate_strategy_card_lifecycle_map.py | — |
| 图10 | 治理运行时链 governance_operations_map（GOMAP-001） | 7 层 | 7 | 7 | 450 机制 | generate_governance_map.py | — |
| 图16 | 立法链 governance_legislation_map | 6 态 | 6 | 6 | 9 台机械 | generate_governance_legislation_map.py（自 pg_ledger） | — |
| — | 宏观序列册 macro_indicator_series_map | 16 序列 | — | 16 | 0 | 无（手工） | — |

注：hop=各图主序列单元（TDM=全节点；含 gap 显性化件者为全节点口径；SPM 环节=stage+lane，机制为挂载物；scard/govleg=状态机态）。逐链计数规则见 chain_inventory.yaml `method` 段。

## 3. 四字段空白环节清单（按链分组）

结构性缺失（schema 无字段）与"字段在册但空"是两类病，分列。明细 id 全量在 chain_inventory.yaml。

### 3.1 结构性缺失——四字段根本没上 schema（250 hop）

- **图7 TDM：186/186 全空白**。仅 purpose_tag 在册（186/186，PT-01..12 图例 12 条）；casebooks/trigger_facts/consumers **三字段 schema 未定义**。按流分组：entry_flow 133 / exit_flow 19 / position_flow 18 / portfolio_flow 16；按型：stage 123 / sensor 37 / aggregation 17 / cross_cutting 5 / gate 4。**核心决策链是全家族血肉最大空白区**。
- **图14 施工链：28/28 全空白**（D14-01..17 + D14-G01..G12 共 11 个 gap 件）。四字段 L1 菜单字段全缺。
- **图15 卡生命周期：13/13 态空白**（D15-S1..S13）。证据承载=card_ledger 56 卡+counts，非四字段形态。
- **图16 立法链：6/6 态空白**（D16-S1..S6）。9 台机械全局挂册不挂态。
- 宏观序列册 16 条（非环节链，列此备查）。

### 3.2 字段在册但未满（97 hop）

- **图13 交易日循环：27/52 空白**（在册最健康）。空白：D13-03/04/06/08/10/11/13/17/18/20/22/23/25/27/29/31/33/34/40/45/46/47/48 + 4 个 gap 件（D13-G01..G04）。缺项主因=casebooks 仅 25/52 节点挂（purpose_tag 48/52、trigger_facts 48/52、consumers 48/52 基本满）。
- **图12 数据供给链：38/43 空白**。全非空仅 5 环节（DSC-07/08/13/19/20——恰好是有 casebooks 病历的环节）。purpose_tag 28/43、trigger_facts 42/43、consumers 36/43、**casebooks 仅 8/43**。
- **图11 交付链：25/30 空白**。全非空仅 5 环节（D11-C01/C04..C07——提交 lane 门禁簇环节）。**purpose_tags 仅 5/30 节点挂**（标签挂机制不挂环节：C05 一格聚 12 标签 131 钉）；casebooks 28/30、trigger_facts 28/30、consumers 28/30 结构满。
- **图9 策略工厂：17/17 环节空白（机制层部分在册）**。四字段挂 324 机制层：purpose_tag 324/324 满、trigger_facts 112/324、consumers 56/324、**casebooks 26/324**；机制级四项全非空仅 5/324。环节层（FAC-E0..E9+七车道）无字段。
- **图10 治理运行时：7/7 层空白**。机制层 purpose_tag/trigger_facts 450/450 满、consumers 261/450（**189 个零消费机制=内收对审候选池**）；casebooks 挂层不挂机制（6/7 层有，GOM-L3 熔断层无病历）。

### 3.3 空白根因归纳

1. **casebooks 是全家族最短板**：TDM 0/186、SPM 机制 26/324、govops 机制 0/450（仅层 6/7）、dscm 8/43——病历挂载（挂图 SOP §3 完备性铁律）在全家族普遍未达标；对照 casebook_registry 仅 8 册在册（ROOR：CASEBOOK-006/007/008 号段缺口未授号）。
2. **两种血肉形态割裂**：图11/12/13 是"环节挂四字段"；图9/10 是"机制挂四字段、环节只是分组壳"。挖矿作业须按形态分型，不能一刀切。
3. ROOR 口径差：REG-MAP-DSCM-001 称图12"四字段血肉已满（f2_done）"——实测为**结构满配**（字段存在）而非**语义满配**（casebooks 非空仅 8/43）。建议 ROOR 描述补口径词。

## 4. 交接面账（全景总图 22 语义边 + 图内载体）

### 4.1 异构语义边 8 条（数据→决策→交付主流向）

| # | 边 | 关系 | 双侧记载状态 |
|---|---|---|---|
| 1 | 图12→图7（DSCMAP-012→TDMAP-001） | 数据供给（供料） | **缺口：两侧图内均无互引**，仅总图语义边 |
| 2 | 图12→图9（→strategy_production_map） | 数据供给（供料） | 双侧在册：图12 有 2 处 SPM 引用 + 图内 9 条 handoff_out 出域载体（经 DSC-HA 交图13/图9、DSC-HB 冷备、DSC-HC 恢复）；SPM 侧 1 处 DSC-GAP-NEWSGHOST 防再引 |
| 3 | 图9→图7（策略上岗） | 工厂产品挂载决策 | 半缺口：机制衔接=TDM 节点 strategy_mounts 挂策略产物；图级仅 SPM 1 处 TDM-F 文字引用，TDM 侧无 E 段回引 |
| 4 | 图9→图15（卡生命周期） | 产品形态承接 | 半缺口：图15 有 3 处 SPM 引用（轴区分/E4 考试权）；SPM 侧无 SCARD 回引 |
| 5 | 图16→图10（立法供给运行时，裁定#486 ①条件边） | 立法真源供运行时 | **缺口：两侧图内均无互引**，仅总图边 |
| 6 | 图7→图13（决策时序投影） | 决策流的时序投影 | 单侧载体：图13 有 20 节点 tdm_refs 挂 18 个 TDM 节点；TDM 侧无 D13 引用 |
| 7 | 图14→图11（Step10 交界） | 施工流终点接交付 | 单侧载体：图14 有 5 节点 handoff_to 显式挂 14 个 D11 环节（D14-01/14/15/16/17）；图11 侧无 D14 引用 |
| 8 | 图10→图11（治理守护交付） | 运行时守护提交链 | 半衔接：图11 有 251 处 gate 引用（机制面）；govops 图侧无 D11 引用 |

### 4.2 扇出面 1 类（14 边，合规不缺口）

- 图11→14 图"施工变更唯一入口"：全景总图机生展开边 + 宪法 §2 政策记载（提交一律走 git_commit.py=队列正门）。各目标图内不重复记载——政策级正门，属设计如此。

### 4.3 缺口清单（挖矿须补）

1. **图12↔图7 供料边零记载**：数据链最上游到决策链最核心的边，两图 YAML 互引为零。建议在 TDM 血肉批补 data_refs↔DSC 节点指针（或在 dscm 补 handoff_out 目标具体化，目前 DSC-HA 是聚合占位）。
2. **图16↔图10 立法边零记载**：裁定#486 ①已激活该边，但两图互引为零；GOMAP 的 families 机制清单应回指其立法依据（ruling 号）。
3. 5 条单侧边建议在"全流通"收口时补对侧回指（低成本：各加 1 个 refs 字段）。

## 5. 关键发现

1. **血肉覆盖两极分化**：图13/11/12（f2_done 三图）有四字段形态且部分填实；图7/14/15/16 四链完全无血肉形态；图9/10 血肉挂在机制粒度。全流通战役的工作量大头在 TDM（186 环节×3 缺字段）。
2. **3 张手工图幂等性风险**：TDM、策略工厂、宏观序列册无 generator 字段——与宪法运维红线 §5"静态清单禁手工维护"存在张力；TDM 正被他队施工（MM 态），本清点基于 dev 快照，落地时须重对。
3. **189 个零消费治理机制**（govops consumers 缺失）+ 图12 ROOR 口径差（§3.3-3）——两处直接可进内收对审（宪法 §4 判据）的候选池。
4. **gap 件是正规环节**：图12 有 15 个、图14 有 11 个、图11 有 2 个、图13 有 4 个 gap 显性化件——缺口显性化本身是该图的纪律成果，挖矿时 gap 件按"空白有主"处理（挂图 SOP §4 v1.1.0-2：gap 格四字段合法）。
5. 图14 环节数口径：全景总图称"17 环节闭环"=stage-only 口径；全节点 28（含 11 gap）+ AGENTS 所指 policy 真源（construction_workflow_policy.md）另立 15 步——三口径并存，战役内统一用 chain_inventory.yaml `hop_count_stage_only` 字段。

## 6. 10_hop_mining 子文件夹划分建议（每链一夹）

| 文件夹 | 链 | 预计环节量 | 分卷建议 |
|---|---|---:|---|
| 10_hop_mining/07_tdm/ | 交易决策链 | 186 | 按 flow 四卷：entry 133 / exit 19 / position 18 / portfolio 16（entry 卷过大可再按 layer 切） |
| 10_hop_mining/09_strategy_production/ | 策略工厂链 | 17 环节（携 324 机制） | 按 E 段归卷；机制大户：E4 考试 81 / E3 构造 79 / E1 进货 58 / E8 组装 34 |
| 10_hop_mining/10_govops/ | 治理运行时链 | 7 层（携 450 机制） | 按 family 七卷：L1_monitor 141 / L5_selfheal 98 / L0_lifecycle 77 / L2_resource 66 / L4_reap 42 / L3_fuse 22 / L6_audit 4 |
| 10_hop_mining/11_dev_delivery/ | 交付链 | 30 | 按 lane 三卷：C 提交 15 / S 会话 9 / D 死信 6 |
| 10_hop_mining/12_dscm/ | 数据供给链 | 43 | 按段五卷：S1 采集 7 / S2 入库 6 / S3 衍生 10 / S4 冷备 9 / S5 对账 11（+15 gap 件随段归卷） |
| 10_hop_mining/13_day_cycle/ | 交易日循环链 | 52 | 按段四卷：A 盘前 13 / B 盘中 16 / C 盘后 13 / D 夜间 10 |
| 10_hop_mining/14_construction/ | 施工链 | 28 | 八段归卷：前置 6 / 设计登记 6 / 判定 3 / 施工 1 / 验收 2 / 落地收尾 7 / 文档 1 / 文档转正 2 |
| 10_hop_mining/15_scard/ | 卡生命周期链 | 13 态 | 态即卷；另携 17 迁移边 + 13 禁边 + 6 gap 件 + 56 卡台账 |
| 10_hop_mining/16_govleg/ | 立法链 | 6 态 | 态即卷；9 台机械单列一卷 |
| （不设） | 宏观序列册 | 16 序列 | registry 型序列映射非环节链——归数据域挖矿管辖，不占环节文件夹 |

> 优先序建议：07_tdm（186 空白、核心链、正施工中须对表）→ 14_construction（全空白且是其余图变更入口）→ 12_dscm/13_day_cycle 的 casebooks 补挂 → 09/10 机制层 casebooks/consumers 双补。

## 7. 本件不做的事（边界）

- 不改任何 config/ 文件（含 MM 态 trading_decision_map.yaml，只读 git dev 快照）。
- 不判并/退/留/修（内收对审=挂图 SOP §5 步 7，另批）。
- 不补四字段数据（本件只清点空白；血肉填充按图走各自生成器/挂图批）。
