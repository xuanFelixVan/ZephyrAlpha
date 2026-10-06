---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_l2_sector —— TDM 板块选择（L2 cn_a，29 节点，全 C——最大缺口带之一）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.3（全族缺口，统一证据=考卷九维无板块维、行业数据只作 A1 中性化分组，H9 §1.3）。
- 计数: 29 全 C；接线级: L3 live 在岗 27 / L4 组骨架 2（E-L2、E-L2-05）。crypto C-L2 归 st_crypto。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 接线级 | 模块（module_ref/mounts） | 行 |
|---|---|---|---|---|
| TDM-E-L2 | 板块选择（组骨架） | L4 | 无 module_ref | TDM:L657 |
| TDM-E-L2-01 | 板块强度综合 | L3 | sector_strength_aggregator；MOD-SIG-144 | TDM:L686 |
| TDM-E-L2-01-1 | 结构强度评估 | L3 | sector/sector_analyzer；MOD-SIG-058/095/097/100/101/120；strat STR-DABAN-003 | TDM:L721 |
| TDM-E-L2-01-2 | 动量活跃度排名 | L3 | data/sector_ranking_engine | TDM:L754 |
| TDM-E-L2-01-3 | 多周期动量加权 | L3 | sector/sector_momentum | TDM:L786 |
| TDM-E-L2-01-4 | 板块资金流聚合 | L3 | sector/sector_breadth；MOD-SIG-088；strat STR-DABAN-002 | TDM:L817 |
| TDM-E-L2-01-5 | 市场级调节注入 | L3 | regime/market_forecast_fusion；MOD-SIG-063/147 | TDM:L850 |
| TDM-E-L2-02 | 轮动序列追踪 | L3 | sector/sector_divergence；BM-SEL-08 已映射（H9 §1.9） | TDM:L883 |
| TDM-E-L2-02-1 | RRG 轮动序列 | L3 | sector/sector_rrg | TDM:L915 |
| TDM-E-L2-02-2 | 单板块轮动预警 | L3 | sector/sector_analyzer；MOD-SIG-119/121 | TDM:L946 |
| TDM-E-L2-03 | 调整周期进度 | L3 | sector/sector_adjustment；BM-SEL-09 已映射 | TDM:L979 |
| TDM-E-L2-03-1 | 扩散指标进度追踪 | L3 | adjustment_cycle_tracker | TDM:L1009 |
| TDM-E-L2-04 | 板块级市场状态 | L3 | core/sector_ecology_judge；MOD-SIG-061 | TDM:L1043 |
| TDM-E-L2-04-1 | 轮动状态五分类 | L3 | sector/sector_rotation_state | TDM:L1075 |
| TDM-E-L2-04-2 | 虹吸态识别 | L3 | sector/sector_siphon；MOD-SIG-113 | TDM:L1105 |
| TDM-E-L2-05 | 水温响应（组骨架） | L4 | 无 module_ref | TDM:L1138 |
| TDM-E-L2-05-1 | 水温档推导 | L3 | sentiment/sentiment_cycle | TDM:L1166 |
| TDM-E-L2-05-2 | 信号响应三件套 | L3 | sector/sector_gate；MOD-SIG-059/094/107/131 | TDM:L1197 |
| TDM-E-L2-06 | 板块个股传导 | L3 | core/sector_conduction | TDM:L1230 |
| TDM-E-L2-06-1 | 三级放行门槛 | L3 | sector/sector_gate；MOD-SIG-104 | TDM:L1260 |
| TDM-E-L2-06-2 | 龙头识别定位 | L3 | sector/sector_leader | TDM:L1292 |
| TDM-E-L2-06-3 | 强度加权传导 | L3 | core/sector_conduction | TDM:L1324 |
| TDM-E-L2-07 | 回踩质量分级 | L3 | sector/sector_pullback；MOD-SIG-116 | TDM:L1356 |
| TDM-E-L2-07-1 | 回踩ABC判定 | L3 | sector/sector_pullback | TDM:L1389 |
| TDM-E-L2-08 | 板块生命周期判定 | L3 | sector/sector_momentum_persistence；strat STR-MOMTREND-003 | TDM:L1423 |
| TDM-E-L2-09 | 催化剂识别 | L3 | screening/event_driven_screener；MOD-SIG-106 | TDM:L1454 |
| TDM-E-L2-09-1 | 事件图谱传导 | L3 | intelligence/news_chain_node_linker；6 mounts | TDM:L1487 |
| TDM-E-L2-09-2 | 冲击标的生成 | L3 | intelligence/chain_impact_resolver | TDM:L1518 |
| TDM-E-L2-10 | 同源补涨比价 | L3 | supply_chain_momentum | TDM:L1549 |

## 2. 缺口与可考性判定

- 全族 C：考卷维度空间（因子标准化/合成/Top-N/定尺寸/调仓/单票帽/宇宙/换手 λ 九维）无板块维；sws2021_l1 行业锚在考卷只用于 A1 中性化 demean（H9 §1.3 统一证据）。
- live 面厚（27/29 有在岗模块）而考卷面零——"补考"路径明确：M3 建议的 sws2021_l1 行业动量 Top-K × 板块内个股两层排序是最小可考核（H9 §2 M 级 M3，行业锚已在 schema:84-91）。
- 可考性分级：M3 主干=S 级偏上（行业锚在册）；轮动五分类/虹吸/水温/回踩 ABC/传导等=逐个 M 级；事件图谱传导（依赖 L9 G 系图谱）=L 级。

## 3. 一句话修复建议

先落 M3 最简板块主干考卷核（行业动量两层排序），再按 BM 映射位（SEL-08/09）优先补轮动与调整周期两支。

## 4. 交叉验证

- H9 §0"大缺口族=L2 板块 29"对本册全族判定负责；本册补充=逐节点 live 模块在岗面（27/29），H9 未列。
- chief B1 ENV-09（TDM L2=30，含 C-L2）计数一致；battle_map_steps 已映射 BM-SEL-08→L2-02、BM-SEL-09→L2-03（H9 §1.9，PG 快照 2026-10-05）。
- SPN 层面对应：SPM E1D 板块盘中聚合/板块报告构建（SPM:L1056/1069）与 E8-M-033 板块分布比较选优（SPM:L4739）是本族的工厂侧邻居——板块能力分散在三图，矩阵考试宜合并命题。
