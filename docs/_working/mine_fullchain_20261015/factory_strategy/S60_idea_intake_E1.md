---
ttl: task_bound
---
# S60 FAC-E1 想法进货（骨架行 60）

> 挖矿工程=mine_fullchain_20261015；本件=FACTORY 段子文档（E1）。所有数字为 2026-10-15 实读。

## 1. 定义

想法进货·六车道（FAC-E1，stage，partial）：多车道并发进货（节点 A-E+G；F=F06 网格仅代码车道），所有货统一卸到策略入库台账并带出生证（渠道+批次+原文指针）。车道：A 社区货源（built）/B AI 生成/C 公式挖掘机/D 产业链三高/E 模型基线/F 网格仅代码/G 全网搜索，B-G 六道 partial。66 节点=1 stage+7 lane+58 mechanism，59 built/7 partial。

## 2. 六向台账

| 向 | 实证（文件路径证据） |
|---|---|
| 输入面 | `data/strategy_intake/raw_manifest.csv`（车道 A，人工版已收 597 条=图 E1A 注）；`data/strategy_intake/lane_b_candidates.csv`、`lane_g_candidates.csv`、`three_high_candidates.csv`（实存）；车道 C 算子真源=`config/factor_mining_whitelist.yaml`（approved 15 算子：arithmetic 4+nonlinear_safe 4+order_stat 2+ts_cs 4+conditional 1；forbidden 4；种群 1000×50 代，Owner 2026-09-14 批，status=active） |
| 输出面 | 候选想法清单 `data/strategy_intake/`（key=md5_12，retention 永久，图 E1 store_refs）；`data/strategy_intake/normalized/` 实存 |
| SSOT 真源 | `config/strategy_production_map.yaml` E1 组 66 节点（行 92-255+机制层）；进货出生证字段=birth_source/url seen log（E1G 图注）；`config/blueprint_routing.yaml` 实存（research 双管线路由声明，骨架缺口 §3.9 关联） |
| 代码模块 | `scripts/backtest/strategy_intake_inventory.py`（151 行）；`scripts/backtest/factory_intake_pipeline.py`（460 行，子命令 run/race/construct——行 431-438 实读，E1D 进货→E1B 可选→E2 幂等预审自动接续编排=MOD-BT-154）；`scripts/backtest/factory_grid_executor.py`+`lane_f_grid_adapter.py`（车道 F 两机制件）；`src/zephyr/research`（14 py）、`src/zephyr/strategy_factory`（17 py）实存 |
| 门禁约束 | 白名单双向交集 fail-closed（factor_mining_whitelist.yaml 行 4-5：白名单有引擎无=版本漂移拒开工；引擎有白名单无=禁用）；"只搜不入册、进货不打分"红线（E1G 图注，判定权归 E2/E4）；battle_map 互挂 BM-RES-06 族（裁定#483/#487） |
| 自动化触发 | 调度槽 `lane_g_intake_sweep`（`src/zephyr/data/scheduler.py` 行 569-581，F20 胃收件箱兜底扫描，总闸 data/runtime/lane_g_intake_sweep.disabled，增量消化禁全量）；生产侧事件沿 intel_harvester.trigger_lane_g_intake |

## 3. 自审闸三态（逐向）

| 向 | 态 | 理由 |
|---|---|---|
| 输入面 | pass | 六车道货源件与 597 条台账实证在盘 |
| 输出面 | pass | 卸货位+键+retention 三要素齐 |
| SSOT 真源 | warn | E1 data_refs 沿用幽灵名 news_data（图注：真身 c3_fundamental.news_data，图12 DSC-GAP-NEWSGHOST 防再引）；车道 F 节点补挂自注"2.4 接线跨线欠账" |
| 代码模块 | pass | 编排层/盘点器/网格件全实存；残件 `scripts/backtest/factory_grid_executor.py.tmp.21772.*` 在盘（临时残留，见缺口 5） |
| 门禁约束 | warn | 白名单 fail-closed 语义完整，但 strategy_intake 进货面无专守 gate（gate_registry 零命中） |
| 自动化触发 | warn | lane_g 兜底扫描槽已挂，但图自报"事件接线（收件箱落新班自动触发）未挂=partial"；C 车道重算力闸点"已声明待 E1C 施工"（E1 图注） |

小计：3 pass / 3 warn / 0 fail。

## 4. 缺口与建议

1. 边分布：E1 是全图边最多的层（9 条：E0→E1、E1→E2、E1→E1A/B/C/D/E/G/F 七扇出），但 58 个 mechanism 节点零边。
2. 反馈环缺口：feedback_loops 声明 E6→E1（衰减结论回灌进货方向），但 edges 块 17 条里**没有**这条边——声明的环未落边（校验器十项有"未声明反馈环"检查，反向"已声明未落边"未见检查项，建议补）。
3. 六车道 6/7 partial：B（NL→策略生成）、C（LLM 辅助生成 GP 替代）、D（LLM 图谱增补管线未建）、E（Kronos 接入=MOD-BT-195 登记跳过，GitHub/HF 双通道不可达）、F（跨线欠账）、G（事件接线未挂）。
4. 幽灵名 news_data 建议随图12 DSC-GAP-NEWSGHOST 一并退役。
5. 清理 `scripts/backtest/factory_grid_executor.py.tmp.21772.*` 残件（项目根零临时文件红线的 scripts 侧同类问题，本席不代清）。
