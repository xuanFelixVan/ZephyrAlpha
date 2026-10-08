---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_17_e0_e9_chain.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-17 策略生产闭环（E0→E9） 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案
- 锚件：config/strategy_production_map.yaml（FACTORY，schema 0.3，effective 2026-09-13）：nodes 341＋edges 17＋feedback_loops 2＋layers 10。切片核数 E0=18/E1=66/E2=8/E3=80/E4=82/E5=5/E6=15/E7=23/E8=35/E9=9，合计 341✓。
- 已知命题「counts 块空＋仅 17 边」验证：**counts 块不是空、是整键缺失**（top-level 无 counts 键；GOMAP 同级有 6 字段 counts）——两图 schema 不对称；17 条边构成已挖明（§1 行 1）。
- build_status 全景：built 315/partial 12/pending 14。stage 级 weak 点：E0 partial（MOD-BT-151 拉式闸门）、E1 partial、E2 partial、E3 partial、E8 partial（33b/1p/1pend）、E9 partial；E4/E5/E6/E7 stage=built。
- 七车道 identity：E1A 社区货源 built（scripts/backtest/strategy_intake_inventory.py）｜E1B AI 生成 partial（MOD-BT-150）｜E1C 公式挖掘机 partial（MOD-BT-155）｜E1D 产业链三高 partial（MOD-BT-090）｜E1E 模型基线 partial（MOD-BT-084）｜E1F 网格仅代码 partial（code:scripts/backtest/factory_grid_executor.py）｜E1G 全网搜索进货 partial（MOD-AUTO-E1G-001）——built 仅 1/7。

## §1 六向台账（向/内部反查发现带路径/外部/判定）
| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 图谱本体（17 边构成） | edges 全量枚举＝**9 条主链** E0→E1→E2→E3→E4→E5→E6→E7→E8→E9＋**1 条反馈边** E9→E2（feedback_loops[0] RD-Agent 式归因回灌）＋**7 条车道扇出** E1→E1A/B/C/D/E/G/F（yaml 内序 G 在 F 前）；边为裸二元 list，无 edge_id/触发条件/载荷元数据 | RD-Agent 式闭环（feedback_loops 注） | 构成挖明✅；边无语义🔬 |
| 断点一：车道悬空 | E1A..E1G 七节点**零出边**——车道产物汇入 E2 全靠隐式约定，图上无一条 lane→E2 边；配合 built 仅 1/7，进货→预审是全链最宽断口 | 六车道分进合击（E1 algo_note） | 图断🌑（车道→E2 未入图） |
| 断点二：有环无边 | feedback_loops[1] E6→E1（衰减/失效结论反馈进货方向）**只在环表声明、edges 无此边**；校验器 scripts/governance/d5_architecture/validators/validate_strategy_production_map.py:249 只单向查「反向边必须声明环」（边→环），「环必须有边」不查→17≠18 静默缺口 | — | 校验器盲区🌑 |
| counts/派生计数 | strategy_production_map 无 counts 键（GOMAP=config/governance_operations_map.yaml 有 total/wired/wired_dynamic/wired_by_header/suspect_orphans/untagged 六字段）；本图计数只能切片派生（本簿 §0 即派生结果） | GOMAP schema 对面 | schema 不对称🔨 |
| 图表达方式 | 341 节点**内部零边**：子结构靠 parent_node 树表达（E4 81 子/E3 79 子/E8 34 子/E7 22 子/E1 系 12+10+10+9…）；consumers 字段仅 56/341 节点填写——本图=主干树＋17 条装饰边，非可执行数据流图 | — | 文档图✅；执行图⬜ |
| 消费面 | 引用 map 的 12 个 py（scripts/governance/d5_architecture/validators/validate_strategy_production_map.py、generators/align_all.py、generate_data_supply_chain_map.py、generate_strategy_card_lifecycle_map.py、generate_map_coverage_attribution.py、check_decision_map.py、fullflow/generate_fullflow_crosscheck.py、ai_layer/gen_search_veins.py 等）**全部是治理校验/生成面，无一按 edges 驱动业务执行** | — | 边=文档约定非编排真源🌑 |

## §2 挖干自评
- 已挖干：17 条边逐条枚举归类（9+1+7）；两大断点（车道悬空、有环无边）定位到 yaml 键与校验器行号；counts 缺失定性为 schema 不对称而非数据丢失；消费面证明 edges 现阶段零业务执行消费。
- 未挖透（点名留档）：341 节点 consumers 字段 285 个空缺的补全工程量未估；E2 预审逻辑门（MOD-BT-091）到 E3 构造（MOD-BT-041..075）之间的工件交接格式未挖（图上无边无从挖起）；products 五类与 stages 的映射未展开。

## §3 挖后自审闸三态裁定
- **裁定：挂起排期**（两小件随 map 再生成窗口同批，不单开施工）。
- 理由：①补 counts 块与②修「有环无边」都须改 config/strategy_production_map.yaml 及其生成/校验链——此图是架构真源（RULE-SSOT：架构数据走机生链，禁手工补丁），单独改一次=两次全图再生成成本＋无业务消费方等待（§1 行 6 证明 edges 暂无执行面读者，不构成在烧的断点）。车道→E2 显式入图属图语义变更（合流口径），须 Owner 定口径。
- 解锁条件：①FACTORY map 下次机生窗口排入「counts 块补齐＋validator 双向环校验（或补 E6→E1 边）」；②Owner 对「七车道汇流 E2 是否显式入图」表态；③任一编排器要按 edges 驱动执行时本断口升紧急级。

## §4 挖矿日志
- R1（切片与边表）：python 切层核数 341✓、build_status 三态分布、E1A-G 七车道 identity 与 built 率；edges 全量打印得 9+1+7 构成。
- R2（断点与消费面反查）：grep counts 键缺失→对照 GOMAP counts；grep feedback_loops 边差集（E6→E1 有环无边）；读 validate_strategy_production_map.py:223-256 证实单向校验；grep strategy_production_map 全仓得 12 个 py 消费者逐一归类=全治理面。
