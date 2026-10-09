---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/01_skeleton_environments.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# 全链环节骨架（MECE 21 环节 × 九图真源）——st-workingchief-20261006 挖矿批次 B1

> 挖矿方法：skeleton_mining_policy（骨架三律：路由表/计分板/防腐）+ mining_sop 六向寻路（内部反查已完成：九图+ROOR+蓝图+功能域册；全网向在分环节作业簿补）。
> 状态标记沿用骨架 SOP：✅活跃管线 / 🔨在建 / ⬜空白 / 💰花钱可解 / 🌑不可得。计数全部来自字段实查（禁凭印象）。
> 分环节深度挖矿作业簿 = `env_mining/env_01..env_21`（六向台账+自审闸三态）。

## §1 真源地图清单（九图）

| # | 图 | 路径 | 顶层结构 | 字段实查计数 | 机生时间 |
|---|----|------|---------|-------------|---------|
| 1 | GOMAP 治理运行图 | config/governance_operations_map.yaml | pipeline.layers(7)+families(7族)+counts | total_modules=450, wired=246+15+95, suspect_orphans=94 | 2026-10-04 |
| 2 | TDM 交易决策图 | config/trading_decision_map.yaml | nodes/edges/state_matrix/portfolio_plan | 182 节点（entry132/position18/exit19/portfolio13）/257 边/state_matrix 24 cells | mtime 10-06（他队域边缘在动） |
| 3 | FACTORY 策略生产图 | config/strategy_production_map.yaml | layers(10)/nodes/edges/products | 341 节点（E0..E9）/仅17边/build: 315 built, 12 partial, 14 pending；**counts 块空** | effective 2026-09-13（最老） |
| 4 | 图11 交付流水线 | config/dev_delivery_map.yaml | nodes/edges/counts/exit_codes | 30 节点/31 边；wired 22/partial 4/unwired 4 | 2026-10-04 |
| 5 | 图12 数据供给链 | config/data_supply_chain_map.yaml | segments(5)/nodes/edges/counts | 43 节点/62 边；gaps_registered=69, unwired_or_hollow=9, verified_semantics=42 | 2026-10-04（fig13 队 claim） |
| 6 | 图13 交易日循环 | config/trading_day_cycle_map.yaml | segments(4)/nodes/edges/counts | 52 节点/64 边；wired 25/partial 16/unwired 11；骨架 ✅15 🔨30 ⬜3 | 2026-10-06T01:08（他队机生中） |
| 7 | 图14 施工升级流 | config/construction_workflow_map.yaml | segments/nodes/counts | 28 节点/33 边；**pending 15 / unwired_no_caller 15** | 2026-10-02 |
| 8 | 图15 策略卡生命周期 | config/strategy_card_lifecycle_map.yaml | states/transitions | 0 nodes/17 transitions（状态机型） | 2026-09-26 |
| 9 | 治理立法流 | config/governance_legislation_map.yaml | states/machinery/transitions | 0 nodes/9 transitions | 2026-10-05 |
| — | 架构底座 | architecture_model/index.yaml | v3.0.3 74 域+12 分区+b_track 13 模块 | last_updated 2026-10-06 | 机生 |
| — | ROOR | docs/registry_of_registries.yaml | tier/status | total_registries=88（active 78/draft 7/archived 2/deprecated 1）；**broken=1 (REG-CASEBOOK-001)** | mtime 10-06 |

## §2 全链环节 MECE（21 环节 × 5 域）

### 甲、数据供给域（图12 五段）
| env_id | 环节 | 真源锚 | 节点 | 状态 | 作业簿 |
|---|---|---|---|---|---|
| ENV-01 | 采集（23 家源×三通道） | FIG12 S1_collect | 7 | built3 partial1 pending3 | env_01_collect |
| ENV-02 | 集成入库（CH 双级+WAL+判重） | FIG12 S2_ingest | 6 | built4 partial1 pending1 | env_02_ingest |
| ENV-03 | 衍生（因子/指标原料 DAG） | FIG12 S3_derive | 10 | partial5 pending5 | env_03_derive |
| ENV-04 | 冷备灾备 | FIG12 S4_coldstore | 9 | built5 partial3 pending1 | env_04_coldstore |
| ENV-05 | 数据对账修复 | FIG12 S5_recon | 11 | built4 partial5 pending2 | env_05_recon |

### 乙、日循环编排域（图13 四段——他队 fig13 挖掘中，本役只读借力）
| env_id | 环节 | 真源锚 | 节点 | 状态 | 作业簿 |
|---|---|---|---|---|---|
| ENV-06a | 盘前段 05:30–09:30 | FIG13 seg[A] | 13 | ✅5 🔨7 ⬜1 | env_06a_premarket |
| ENV-06b | 盘中段 09:30–15:00 | FIG13 seg[B] | 16 | ✅6 🔨8 ⬜2 | env_06b_intraday |
| ENV-06c | 盘后段 15:00–20:00 | FIG13 seg[C] | 13 | ✅7 🔨5 ⬜1 | env_06c_postmarket |
| ENV-06d | 夜窗与贯穿段 | FIG13 seg[D] | 10 | ✅1 🔨8 ⬜1 | env_06d_nightwindow |

### 丙、交易决策域（TDM 四 flow）
| env_id | 环节 | 真源锚 | 节点 | 作业簿 |
|---|---|---|---|---|
| ENV-07 | 源线与知识供给 | TDM entry_flow L9 | 44 | env_07_source_lines |
| ENV-08 | 市场感知与状态判定 | TDM L0+L1（state_matrix 24 cells proposed） | 15 | env_08_market_state |
| ENV-09 | 板块选择 | TDM L2 | 30 | env_09_sector_select |
| ENV-10 | 个股选择 | TDM L3 | 26 | env_10_stock_select |
| ENV-11 | 买卖点与执行 | TDM L4（critical 11 集中带） | 16 | env_11_trade_exec |
| ENV-12 | 持仓管理 | TDM position_flow | 18 | env_12_pflow_holdings |
| ENV-13 | 离场与应急风控 | TDM exit_flow（X1 保命红线） | 19 | env_13_x_legs |
| ENV-14 | 组合与预算 | TDM portfolio_flow+PP-001(proposed) | 6 | env_14_pp_plan |

### 丁、对账/复盘/生产闭环域
| env_id | 环节 | 真源锚 | 节点 | 状态 | 作业簿 |
|---|---|---|---|---|---|
| ENV-15 | 账务对账（三账+当日回测基准） | FIG13 D13-29/31+FIG12 DSC-15/20 | 4 | **全 unwired/hollow——全链最薄** | env_15_recon_ledger |
| ENV-16 | 复盘回测与归因 | TDM C3+FACTORY E9+REG-EXP/BTB | 15 | sim 腿仅钩子 | env_16_e9_retro_loop |
| ENV-17 | 策略生产闭环 E0-E9 | FACTORY layers | 341 | built315/12/14；仅17边 | env_17_e0_e9_chain |

### 戊、系统运维与 AI 治理域
| env_id | 环节 | 真源锚 | 节点 | 状态 | 作业簿 |
|---|---|---|---|---|---|
| ENV-18 | 系统运维七族 | GOMAP families L0-L6 | 450 模块 | suspect_orphans 94 | env_18_sysops |
| ENV-19 | AI 立法与门禁 | 立法流图+ROOR(88 册) | 9 边 | 10-05 新生 | env_19_ai_legislation |
| ENV-20 | 开发交付流水线 | 图11+图14+图15 | 30+28+17边 | 图14 一半 unwired | env_20_dev_delivery |
| ENV-21 | 架构资产底座 | index.yaml+蓝图 §0.2(88 任务域)+功能域册(94) | 74 域 | 当日机生 | env_21_arch_base |

MECE 校验：Owner 任务书十二链要素（数据供给/集成入库/因子指标/信号/决策/风控/执行/对账/复盘回测/反馈迭代/系统运维/AI治理）全部落位；"因子/指标"拆 ENV-03+ENV-07+登记册；"执行"拆 ENV-11+ENV-13。

## §3 结构性缺口（B1 挖矿批次发现，施工候选）

1. **七图未入 ROOR**（TDM/图13/FACTORY/GOMAP/图14/图15/立法流；ROOR 只注册了图11、图12）——ROOR 作为发现唯一真源存在注册滞后 → 线3 施工。
2. FACTORY 无 counts 块（九图唯一）且 341 节点仅 17 边；effective_from 全场最老。
3. 对账链（ENV-15）全链空转：三账核对/当日回测/execution_report 等未产表——全链最薄环节。
4. 图14 一半环节无调用者（15/28 unwired_no_caller，pending 15/28）；图15 卡生命周期 0 节点。
5. GOMAP 94 个 suspect_orphans 未入任何图。
6. 跨图互链：TDM→其它图 0 回链（全链汇聚点只出不进）；六图机械对账器 `_MAP_IDS` 只认六图，图14/15/立法流在覆盖账本之外。
7. ROOR broken=1（REG-CASEBOOK-001）。
8. 图13 骨架 48 环节 vs 图上 52 节点（D13-45~48 骨架外新增）——他队领地，只登记不代修。

## §4 封矿声明（B1 批次）

环节层（21）与图源层（9 图）已三扫收敛（任务书十二要素反查+ROOR 反查+蓝图反查均无新增环节）；**环节层封顶**：此后增长=作业簿内子类目/叶层细化，增环节须过 skeleton_mining_policy §3 三问并留理由。分环节作业簿的六向台账与封矿由各簿自审闸裁定（挖干判据=六向台账+自审闸三态）。
