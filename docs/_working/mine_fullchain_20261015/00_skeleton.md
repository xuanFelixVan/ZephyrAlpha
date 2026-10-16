---
doc_type: skeleton_map
title: 全链路环节骨架总纲（挖矿地图）
created: 2026-10-15
session: mine-fullchain-skel-20261015
ttl: task_bound
ssot_note: 环节定义全部取自 config/ 地图 YAML 实读（对齐键=module_id/step_id/node_id/state_id），代码仅做包/文件存在性验证；未在地图在册的环节一律不发明，只进"缺口清单"。
map_lineage: 本件=挖矿工程地图总纲；子文档（每环节一本）均派生于本目录。
---

# 00 全链路环节骨架总纲

## 0. 读法与数据真源（本批实读清单）

- config/ 地图类 22 件实读：10 张图族全景/链路图（panorama_master_map + 图11/12/13/14/15/16 + TDM + FACTORY + GOMAP）+ nav_table_mapping 七段 + 11 件辅件/参数册（position_recipe_grid_schema v2/v3、resource_profile_registry、exam_scale_cost_gate、macro_indicator_series_map、blueprint_routing、chainmap_cluster_names、sector_attribute_mapping、degradation_chain、ibt_pool_bridge）。数量以本批实读为准，勿背数。
- docs/registry_of_registries.yaml（ROOR v1.1.0）：11 张图族注册表登记（REG-MAP-DEVDELIVERY-001 等）+ 94 注册表总账。
- docs/01_policies_and_standards/sop/README.md：方法论十三族索引；construction_sop/construction_workflow_policy.md：端到端 17 段施工闭环（Step 0-12 含小数步，"07"=07_trading_decision_architecture 域目录编号）。
- docs/library/FRONT_DOOR.md（机生门牌）+ src/zephyr/ 顶层 ls（57 个业务包，实读）+ module_translation_registry.yaml（REG-MODULE-TRANSLATION-001，四族条目账本）。
- 代码指针存在性已核：zephyr.trading（process_reaper 实跑存活）、data/、regime/、strategy_factory/、sell_decision/、pf_core/、pf_alloc/、gov_enforcement/（含 rule_bridge/git_commit_gateway.py）、shared/io/file_utils.py、scripts/{git_commit,commit_queue,session_worktree}.py 等均实存。

## 1. 链路全景 ASCII 图

```
【治理链】立法流(图16): 裁定→[草案draft]→[生效active]→[superseded/deprecated/void/decided]
          nav七段: ①想法→②草稿→③审计裁定→④蓝图→⑤施工→⑥验收→⑦持续审计   ──┐(规则/门禁输出)
【交付链】图14施工17段: 冷启动→文档审查→创建前搜索→架构评审门→方案挖矿→全景图登记→全图对齐   │
          →拆件判定→施工编码→单测循环验收→长清单审查→施工文档→全景图转正                     │
          →文件完整性→提交网关落地→临时文件清理→worktree合并清理                              │
          图11交付28段: S会话9段(冷启动→claim→worktree提交→merge回主区→handoff)               │
          →C提交13段(正门→门禁链→入队→排队→真落盘→post-commit对账)→D死信6段(甄别→requeue) ←──┘
【数据链】图12供给链22段: S1采集(盘后/盘中/事件)→S2入库(CH写入/WAL排空/幂等判重)
          →S3衍生(指标重采样/财务PIT/形态情绪)→S4冷备(归档/双链备份/冷热分层)
          →S5对账修复(完整性巡检/缺口回补/三账核对/坏数据修复/CH维护/自愈)
          资源轴: resource_profile_registry 109实体(排班互斥/泳道) ← 支撑全部调度
【业务主链·策略生产段】FACTORY十层341节点:
   E0算力16→E1想法66→E2假说8→E3构造80→E4考试82→E5去重5→E6入库15→E7模拟23→E8组装35→E9归因9
   产物5类: strategy/factor/portfolio/evidence_chain/negative_archive
【业务主链·卡生命周期段】图15十三态: draft→candidate→frozen(±amended)→executing→green/red/insufficient
   →suspended/SEALED/condemned/graduated/void（17迁移边+13禁边执法）
【业务主链·交易决策段】TDM四flow186节点:
   entry: L0盘前计划→L1大盘总闸(传感器S0-S5+状态判定AGG)→L2板块选择→L3个股选择→L4买卖点执行
   position: P1持仓体检→P2做T加减仓→P3加仓决策    exit: S1卖出信号评分→S2离场执行→R1应急保命
   portfolio: C1预算切分→C2组合聚合→C3绩效归因反馈(回流E9/L0)
   状态矩阵6态×24格 + 组合计划PP-001(16 sleeve)
【业务主链·当日运营段】图13交易日48段: A盘前12段(就绪门D13-09★)→B盘中14段(实时层/竞价/模拟盘)
   →C盘后12段(结算/三账核对/日K落库/日度拍板)→D夜窗10段(研报/财务批/守护三路/日界交接)
```

四链交汇点：数据链是业务主链的 L9 源线（TDM-E-L9 45 个源线节点即数据链挂点面）；治理链经门禁/立法流入交付链执法面；交付链图14 D14-15 提交网关=图11 C 车道正门（两图同域衔接）。

## 2. 全链路环节总表（172 环节）

优先级口径：P0=挖矿产能咽喉（先挖先出子文档）；P1=图已满配血肉、按图细分即可；P2=账务缺口收口导向；P3=状态机小件半日可清。

### 2.1 业务主链·策略生产段（FACTORY，10 环节｜SSOT=config/strategy_production_map.yaml｜REG-MAP-FACTORY-001）

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| FAC-E0 | 算力调度（16 节点） | 业务主链 | 资源画像/排班 | E1 | config/strategy_production_map.yaml + config/resource_profile_registry.yaml（e0_mapping 生成器映射） | src/zephyr/data/scheduler.py、src/zephyr/trading/process_reaper.py | 图内层+节点在册；e0 映射在生成器 | P0 |
| FAC-E1 | 想法进货（66） | 业务主链 | 挖矿SOP/全网调研 | E2 | 同上+config/factor_mining_whitelist.yaml | src/zephyr/research、strategy_factory | 层在册 | P0 |
| FAC-E2 | 假说预审（8） | 业务主链 | E1 | E3 | 同上 | src/zephyr/strategy_factory | 层在册 | P0 |
| FAC-E3 | 构造代码（80） | 业务主链 | E2 | E4 | 同上 | src/zephyr/factor、strategy_pipeline、backtest | 层在册 | P0 |
| FAC-E4 | 考试咽喉（82） | 业务主链 | E3 | E5、图15-D15-S5..S8 | 同上+config/exam_scale_cost_gate.yaml（考尺/成本门/DSR 全参数） | src/zephyr/backtest、scripts/backtest/ | 层在册+专参数册 | P0 |
| FAC-E5 | 协同去重（5） | 业务主链 | E4 | E6 | 同上+config/synergy_dedup.yaml | src/zephyr/strategy_factory | 层在册 | P1 |
| FAC-E6 | 入库监控（15） | 业务主链 | E5 | 图15-S2 candidate | 同上+catalogs/{factor,strategy}_registry.yaml | src/zephyr/experiment_tracking | 层在册 | P1 |
| FAC-E7 | 模拟盘前哨（23） | 业务主链 | E6 | E8 | 同上 | src/zephyr/simulation、execution_simulation、digital_twin | 层在册 | P1 |
| FAC-E8 | 组装与资金分配（35） | 业务主链 | E7、图15-S12 graduated | TDM-F-C1 | 同上+catalogs/portfolio_model_registry.yaml+position_recipe_grid_schema.yaml（仓位配方 17 维） | src/zephyr/pf_alloc、pf_core | 层在册 | P0 |
| FAC-E9 | 实盘归因（9） | 业务主链 | TDM-F-C3 回流 | E1（迭代回灌） | 同上 | src/zephyr/feedback_loop、reporting | 层在册 | P1 |

覆盖缺口（图自报）：341 节点仅 17 边、counts 块空——层间边未接线（ROOR 注记，chief_fullchain_campaign/01 §3 在案）。

### 2.2 业务主链·卡生命周期段（图15 状态机，13 状态环节｜SSOT=config/strategy_card_lifecycle_map.yaml←card_state_vocabulary.yaml，宿主册=experiment_registry.yaml｜REG-MAP-SCLC-001）

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| D15-S1 | 草案 draft | 业务主链 | E1-E3 构造 | S2 | config/strategy_card_lifecycle_map.yaml#D15-S1 | 宿主册 experiment_registry.yaml | 17 迁移边+13 禁边在册 | P3 |
| D15-S2 | 候选卡 candidate | 业务主链 | S1/E6 | S3 | 同上#D15-S2 | 同上 | 同上 | P3 |
| D15-S3 | 冻结 frozen | 业务主链 | S2 | S5 | 同上#D15-S3 | 同上 | 同上 | P3 |
| D15-S4 | 冻结带附录 frozen-amended | 业务主链 | S3 | S5 | 同上#D15-S4 | 同上 | 同上 | P3 |
| D15-S5 | 在测 executing | 业务主链 | S3/S4 | S6/S7/S8 | 同上#D15-S5（=E4 考试执行态） | src/zephyr/backtest | 同上 | P0 |
| D15-S6 | 判绿 green | 业务主链 | S5 | S12/挂图 | 同上#D15-S6 | 同上 | 同上 | P0 |
| D15-S7 | 判红 red | 业务主链 | S5 | S11/负结果台账 | 同上#D15-S7 | 同上 | 同上 | P0 |
| D15-S8 | 不可判 insufficient | 业务主链 | S5 | S9/重考 | 同上#D15-S8 | 同上 | 同上 | P0 |
| D15-S9 | 挂起 suspended | 业务主链 | S5/S8 | 复活授权 | 同上#D15-S9 | 同上 | 同上 | P3 |
| D15-S10 | 封卡 SEALED（终态） | 业务主链 | 判读定版 | 证据定版 | 同上#D15-S10 | 同上 | 同上 | P3 |
| D15-S11 | 判死归档 condemned | 业务主链 | S7 | 复活窗裁定 | 同上#D15-S11 | 同上 | 同上 | P3 |
| D15-S12 | 毕业出卡 graduated | 业务主链 | S6 | E8 组装/TDM 挂图 | 同上#D15-S12 | 同上 | 同上 | P0 |
| D15-S13 | 作废 void | 业务主链 | 任态禁边外 | 墓碑 | 同上#D15-S13 | 同上 | 同上 | P3 |

覆盖缺口（图自报）：state_undeclared_headless=42 卡未登记态、needs_adjudication=3、gaps=6。

### 2.3 业务主链·交易决策段（TDM 四 flow，14 个一级环节=186 节点｜SSOT=config/trading_decision_map.yaml｜REG-MAP-TDM-001；决策算法=REG-DAL-001，验证方法=REG-VALM-001，回测对象=REG-BTB-001）

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| TDM-E-L0 | 盘前作战计划（5 节点） | 业务主链 | 图13-A 段、E9 归因回流 | L1 | config/trading_decision_map.yaml#TDM-E-L0 | src/zephyr/plan_engine | 133 节点 entry_flow 在册 | P0 |
| TDM-E-L1 | 大盘总闸/市场状态判定（10） | 业务主链 | L0、L9 源线、图12-S3 | L2 | 同上#TDM-E-L1（S0-S5 传感器+AGG） | src/zephyr/regime、market_data、intelligence | 同上；宏观序列翻译=config/macro_indicator_series_map.yaml | P0 |
| TDM-E-L2 | 板块选择（30） | 业务主链 | L1 | L3 | 同上#TDM-E-L2 | src/zephyr/market_data、cross_asset | 同上 | P0 |
| TDM-E-L3 | 个股选择（26） | 业务主链 | L2 | L4 | 同上#TDM-E-L3 | src/zephyr/signal_ashare、signal_fundamental、signal_quality、factor | 同上 | P0 |
| TDM-E-L4 | 买卖点与执行（16） | 业务主链 | L3 | P1、图13-B 模拟/实盘通道 | 同上#TDM-E-L4 | src/zephyr/ex_core、ex_sor、position、trading | 同上 | P0 |
| TDM-P-P1 | 持仓体检（7） | 业务主链 | L4 | P2/P3/X-S1 | 同上#TDM-P-P1 | src/zephyr/position、risk | 18 节点 position_flow | P0 |
| TDM-P-P2 | 做T与加减仓（5） | 业务主链 | P1 | X-S1/S2 | 同上#TDM-P-P2 | src/zephyr/position | 同上 | P0 |
| TDM-P-P3 | 加仓决策（5） | 业务主链 | P1 | L4 | 同上#TDM-P-P3 | src/zephyr/position、risk | 同上 | P0 |
| TDM-X-S1 | 卖出信号收集评分（7） | 业务主链 | P1、行情 | X-S2/R1 | 同上#TDM-X-S1 | src/zephyr/sell_decision | 19 节点 exit_flow | P0 |
| TDM-X-S2 | 离场执行（7） | 业务主链 | S1 | C3 归因 | 同上#TDM-X-S2 | src/zephyr/ex_core、sell_decision | 同上 | P0 |
| TDM-X-R1 | 应急保命/熔断（4） | 业务主链 | 风控事件 | 全域降级 | 同上#TDM-X-R1 + config/crisis_gate.yaml、risk_params.yaml | src/zephyr/risk | 同上 | P1 |
| TDM-F-C1 | 预算切分（4） | 业务主链 | E8 组装 | C2/L0 | 同上#TDM-F-C1 | src/zephyr/pf_alloc | 16 节点 portfolio_flow | P0 |
| TDM-F-C2 | 组合聚合（6） | 业务主链 | C1、各 sleeve | L4 下单面 | 同上#TDM-F-C2（PP-001 16 sleeve） | src/zephyr/pf_core | 同上 | P0 |
| TDM-F-C3 | 绩效归因反馈（6） | 业务主链 | S2/C2 | E9/E1 回流 | 同上#TDM-F-C3 | src/zephyr/feedback_loop、reporting | 同上 | P0 |

注：TDM-E-L9（45 个源线节点）=数据链在 TDM 的挂点面，环节本体归 2.5 数据链，不在本段重复计数。

### 2.4 业务主链·当日运营段（图13 交易日循环，48 段环节｜SSOT=config/trading_day_cycle_map.yaml←docs/_working/map_build/fig13_daycycle/00_skeleton.md §2｜图13 无 ROOR 独立行，挂图族账本）

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| D13-01 | 调度对账补跑 | 业务主链 | 排班三表 | 当日各档 | config/trading_day_cycle_map.yaml#D13-01 | src/zephyr/data/scheduler.py | A 段在册 | P1 |
| D13-02 | 数据断供哨兵 | 业务主链 | S1 采集 | 告警/回补 | #D13-02 | src/zephyr/data/integrity_checker | A 段 | P1 |
| D13-03 | 交易日历逐日覆盖 diff | 业务主链 | 日历 | 调度 | #D13-03 | src/zephyr/data/calendar | A 段 | P1 |
| D13-04 | 夜间情绪窗结算 | 业务主链 | 情绪环 | E-L1-S0 | #D13-04 | src/zephyr/intelligence | A 段 | P1 |
| D13-05 | 币圈日线（UTC 日界） | 业务主链 | crypto 源 | crypto 总闸 | #D13-05 | src/zephyr/data.connectors、cross_asset | A 段 | P2 |
| D13-06 | L0.5 盘前元数据 | 业务主链 | universe 册 | 决策链 | #D13-06 | catalogs/universe_registry.yaml+src/zephyr/data | A 段 | P1 |
| D13-07 | QMT 终端看门狗 | 业务主链 | 券商终端 | 执行通道 | #D13-07 | src/zephyr/data（qmt 桥）+config/qmt_environments.yaml | A 段 | P2 |
| D13-08 | 十源健康探针 | 业务主链 | 外部源 | 就绪门 | #D13-08 | src/zephyr/data.connectors | A 段 | P1 |
| D13-09 | 开盘前就绪门★ | 业务主链 | C1+C2+C3 合成 | 当日准入 | #D13-09 | src/zephyr/data（readiness 聚合器） | A 段一等门 | P0 |
| D13-10 | 板块状态盘前复制 | 业务主链 | C 段定格 | 盘中 | #D13-10 | src/zephyr/data | A 段 | P1 |
| D13-11 | 集合竞价高频五档采集 | 业务主链 | 交易所 | B 段竞价 | #D13-11 | src/zephyr/data.connectors、market_data | A 段 | P1 |
| D13-12 | 模拟盘会话拉起+日历闸 | 业务主链 | 就绪门 | B 段模拟 | #D13-12 | src/zephyr/simulation | A 段 | P1 |
| D13-13 | 竞价后档位一次性聚合 | 业务主链 | D13-11 | 情绪指数 | #D13-13 | src/zephyr/market_data | B 段 | P1 |
| D13-14 | 盘中实时层（Tick/L2 等） | 业务主链 | 实时源 | 决策/入库 | #D13-14 | src/zephyr/market_data、data | B 段 | P1 |
| D13-15 | 盘中分钟K滚动层 | 业务主链 | 实时源 | 决策 | #D13-15 | src/zephyr/data/kline_resampler | B 段 | P1 |
| D13-16 | 盘中板块分钟K层 | 业务主链 | 实时源 | 板块域 | #D13-16 | src/zephyr/market_data | B 段 | P2 |
| D13-17 | 事件驱动快新闻+EDB 轮询 | 业务主链 | 事件源 | 情绪/宏观 | #D13-17 | src/zephyr/data/news_collector、nlp | B 段 | P1 |
| D13-18 | 慢新闻/研报独立队列 | 业务主链 | 研报源 | 夜窗批 | #D13-18 | src/zephyr/data、alt_data | B 段 | P2 |
| D13-19 | 板块资金流日内五快照 | 业务主链 | 资金流源 | L2 板块 | #D13-19 | src/zephyr/data（资金流采集） | B 段 | P1 |
| D13-20 | 竞价命中判定（墙钟窗闸） | 业务主链 | D13-13 | 挂单面 | #D13-20 | src/zephyr/trading | B 段 | P1 |
| D13-21 | 盘中 L1 市场状态跟踪 | 业务主链 | E-L1-AGG | 全域 regime | #D13-21 | src/zephyr/regime | B 段 | P0 |
| D13-22 | 盘中情景归类 | 业务主链 | D13-21 | 决策 | #D13-22 | src/zephyr/regime | B 段 | P1 |
| D13-23 | 盘中情绪环单拍 | 业务主链 | 情绪采集 | 决策 | #D13-23 | src/zephyr/intelligence | B 段 | P1 |
| D13-24 | 模拟盘保活与成交回路 | 业务主链 | D13-12 | 对账 | #D13-24 | src/zephyr/simulation | B 段 | P1 |
| D13-45 | 盘中模拟盘桥（做T双拍） | 业务主链 | D13-24 | P2 做T | #D13-45 | src/zephyr/simulation | B 段 | P2 |
| D13-46 | 盘初决策链哨兵（09:40） | 业务主链 | L0-L4 决策链 | 告警 | #D13-46 | src/zephyr/trading | B 段 | P1 |
| D13-25 | 板块状态盘后定格 | 业务主链 | 盘中板块 | 次日 A 段 | #D13-25 | src/zephyr/data | C 段 | P1 |
| D13-26 | 指数分钟K日终补拉 | 业务主链 | 交易所 | 探测器供料 | #D13-26 | src/zephyr/data | C 段 | P2 |
| D13-27 | 盘中持仓对账事件入口 | 业务主链 | 持仓事件 | D13-29 | #D13-27 | src/zephyr/position | C 段 | P1 |
| D13-28 | 盘后结算管线（T+1 硬时点） | 业务主链 | 成交 | 三账核对 | #D13-28 | src/zephyr/trading、data | C 段 | P0 |
| D13-29 | 日终三账核对（L1/L2/L3） | 业务主链 | D13-27/28 | 拍板 | #D13-29 + 图12-DSC-15 对账 | src/zephyr/data（reconciliation） | C 段 | P0 |
| D13-30 | 盘后日K线层（下游就绪门） | 业务主链 | 交易所日K | 全链供料 | #D13-30 + 图12-S2 | src/zephyr/data.ch_writer | C 段 | P0 |
| D13-31 | 当日回测跑批（对账 L1 基准） | 业务主链 | 日K | 归因 | #D13-31 | src/zephyr/backtest | C 段 | P1 |
| D13-32 | 日循环总扳手★（全链编排） | 业务主链 | 全段 | 全段 | #D13-32 + scripts/ops/schedule_overview.py | src/zephyr/data/scheduler.py | C 段最大节点 | P0 |
| D13-33 | 收盘验证→三表结算 | 业务主链 | 盘后数据 | 台账 | #D13-33 | src/zephyr/data | C 段 | P1 |
| D13-34 | 日度拍板（毕业包恒空→无实盘） | 业务主链 | 三账核对 | 次日边界 | #D13-34 | src/zephyr/trading | C 段 | P0 |
| D13-35 | 盘后数据批次群 | 业务主链 | 各源 | 库 | #D13-35 + 图12-S1 | src/zephyr/data | C 段 | P1 |
| D13-48 | 盘后板块K等权撮合 | 业务主链 | tdx 断供收敛 | 板块域 | #D13-48 | src/zephyr/data | C 段 | P2 |
| D13-36 | 研报明细增量层 | 业务主链 | 研报源 | 库 | #D13-36 | src/zephyr/alt_data、data | D 段 | P2 |
| D13-37 | 夜间财务层（财报/两融） | 业务主链 | 财务源 | 库/PIT | #D13-37 + 图12-S3 | src/zephyr/data/financial_parser | D 段 | P1 |
| D13-38 | 每日完整性巡检 | 业务主链 | 库 | 告警 | #D13-38 + 图12-S5 | src/zephyr/data/integrity_checker | D 段 | P1 |
| D13-39 | 一致预期管线双向验证 | 业务主链 | 预期源 | 库 | #D13-39 + 图12-DSC-17 | src/zephyr/data/consensus_crosscheck | D 段 | P2 |
| D13-40 | 另类宏观日频 | 业务主链 | 宏观源 | L1-S0 | #D13-40 | src/zephyr/data/macro_vintage | D 段 | P2 |
| D13-41 | 周批与月批 | 业务主链 | 各源 | 库 | #D13-41 | src/zephyr/data | D 段 | P2 |
| D13-42 | 常驻守护三路（reaper/deadman/guard） | 业务主链 | — | 全域 | #D13-42 | src/zephyr/trading/process_reaper | D 段 | P1 |
| D13-43 | 交易日历闸门（事件触发不变量） | 业务主链 | — | 全调度 | #D13-43 | src/zephyr/data/calendar | D 段 | P1 |
| D13-44 | 日界交接（T→T+1 状态移交） | 业务主链 | C 段 | 次日 A 段 | #D13-44 | src/zephyr/data/scheduler.py | D 段 | P1 |
| D13-47 | tick 双源一致性比对 | 业务主链 | QMT/TDX | 告警 | #D13-47 | src/zephyr/data/dual_source_guard | D 段 | P2 |

覆盖缺口（图自报）：gap 4 节点、unwired_no_caller=6、unwired_slot_hollow=5。注：本段与图12 是同两批数据的"运营态视角 vs 生命周期视角"，裁定#482 先例=正交不并。

### 2.5 数据链（图12 供给链，22 段环节=43 节点含 15 gap｜SSOT=config/data_supply_chain_map.yaml←docs/_archive/_working_cleared/map_build/fig12_datachain/00_skeleton.md §1｜REG-MAP-DSCM-001）

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| DSC-01 | 盘后批量采集 | 数据链 | 外部源 18 个 | S2 | config/data_supply_chain_map.yaml#DSC-01 | src/zephyr/data.connectors | S1 在册 | P1 |
| DSC-02 | 盘中实时/竞价采集 | 数据链 | 实时源 | S2/S4 WAL | #DSC-02 | src/zephyr/market_data、data | S1 | P1 |
| DSC-03 | 事件驱动采集（新闻/宏观/研报/加密） | 数据链 | 事件源 | S2/S3 | #DSC-03 | src/zephyr/data（news/macro/alt 采集）、alt_data | S1 | P1 |
| DSC-04 | ClickHouse 写入通道（两级降级） | 数据链 | S1 | 库 | #DSC-04 | src/zephyr/data/ch_writer、infrastructure（DatabaseService 唯一真源） | S2 | P1 |
| DSC-05 | 实时 WAL 落盘排空 | 数据链 | DSC-02 | 库 | #DSC-05 | src/zephyr/data/local_replay、buffered_writer | S2 | P1 |
| DSC-06 | 幂等写与判重 | 数据链 | S2 | 库 | #DSC-06 + RULE-DATA-OPS | src/zephyr/data（判重引擎） | S2 | P1 |
| DSC-07 | 技术指标/多周期重采样 | 数据链 | 库 | TDM-L3/因子 | #DSC-07 | src/zephyr/data/kline_resampler、multi_timeframe_fusion | S3 | P1 |
| DSC-08 | 财务/一致预期派生（PIT 双守卫） | 数据链 | 库 | 因子/决策 | #DSC-08 | src/zephyr/data/financial_parser | S3 | P1 |
| DSC-09 | 形态/情绪/板块状态衍生 | 数据链 | 库 | L1/L2 传感器 | #DSC-09 | src/zephyr/data（cleaning/衍生引擎）、intelligence | S3 | P1 |
| DSC-21 | 表外进程内派生（工厂/回测/组合直写 CH） | 数据链 | E3/回测 | CH | #DSC-21 | src/zephyr/backtest、strategy_factory | S3 | P2 |
| DSC-10A | 手动 CLI 归档（export→verify→drop） | 数据链 | 库 | 冷库 | #DSC-10A | src/zephyr/data/data_compression_archiver | S4 | P2 |
| DSC-10B | 滚动归档事件触发器（五重安全阀） | 数据链 | 备份成功事件 | 冷库 | #DSC-10B | 同上 | S4 | P2 |
| DSC-11 | 灾备双链备份（F→G 镜像） | 数据链 | 库/CH | G:/backup | #DSC-11 + INFRA-STORE-003 存储地图 | infrastructure | S4 | P2 |
| DSC-12 | 冷热分层/压缩决策 | 数据链 | 库 | 冷库 | #DSC-12 + config/compression_policy.yaml | src/zephyr/data | S4 | P2 |
| DSC-13 | 完整性巡检+新鲜度哨兵 | 数据链 | 库 | 告警/S5 | #DSC-13 | src/zephyr/data/integrity_checker | S5 | P1 |
| DSC-14 | 缺口回补三通道 | 数据链 | 巡检 | 库 | #DSC-14 | src/zephyr/data/auto_backfiller、backfill_checker | S5 | P1 |
| DSC-15 | 日终三账对账——未接线 | 数据链 | 结算 | 台账 | #DSC-15 | src/zephyr/data（reconciliation 面） | S5（显式未接线） | P0 |
| DSC-16 | 坏数据修复与回补器族 | 数据链 | 差异 | 库 | #DSC-16 + data_ops_sop | src/zephyr/data/c4_history_repair | S5 | P1 |
| DSC-17 | 一致预期双向互验 | 数据链 | 自建聚合 | 告警 | #DSC-17 | src/zephyr/data/consensus_crosscheck | S5 | P2 |
| DSC-18 | CH 存储维护 OPTIMIZE | 数据链 | 周窗 | CH | #DSC-18 | src/zephyr/data（CH 维护） | S5 | P2 |
| DSC-19 | 破损 part 自愈探测器 | 数据链 | CHECKSUM | 隔离环 | #DSC-19 | src/zephyr/data/ch_parts_monitor | S5 | P2 |
| DSC-20 | 任务级对账（应跑 vs 打卡差四计数） | 数据链 | 调度 | 台账 | #DSC-20 | src/zephyr/data（task 对账） | S5 | P1 |

覆盖缺口（图自报）：gaps_registered=71、gap_nodes=15、DSC-GAP-TERMINUS 终点缺口、waiting_table_gaps 5 张表（nav_daily/execution_report/factor_feature_value/factor_signal/reconciliation_differences）、news_data 幽灵引用。

### 2.6 治理链（20 环节：立法流 6 态 + GOMAP 七族 + nav 七段）

立法流（图16，6 态｜SSOT=config/governance_legislation_map.yaml←骨架 §1-§3+PG 账本 ruling_registry.yaml｜REG-MAP-GLM-001，裁定#486 准入）：

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| D16-S1 | 草案 draft | 治理链 | 裁定#/议题 | S2 | config/governance_legislation_map.yaml#D16-S1 | catalogs/ruling_registry.yaml | 9 迁移边+7 禁边 | P3 |
| D16-S2 | 生效中 active（291 条） | 治理链 | S1 | S3/S4/S5/S6 | #D16-S2 | 规则 YAML→gate：src/zephyr/gov_rule、gov_enforcement | 同上 | P3 |
| D16-S3 | 被取代 superseded | 治理链 | S2 | 归档 | #D16-S3 | 同上 | 同上 | P3 |
| D16-S4 | 已废弃 deprecated | 治理链 | S2 | 墓碑 | #D16-S4 | 同上 | 同上 | P3 |
| D16-S5 | 撞号墓碑 void | 治理链 | S2 | 墓碑 | #D16-S5 | 同上 | 同上 | P3 |
| D16-S6 | 已决归档 decided | 治理链 | 审判台 | 账本 | #D16-S6 | 同上 | 同上 | P3 |

治理运行七族（GOMAP，429 模块｜SSOT=config/governance_operations_map.yaml，families 生成器全量重建禁手改）：

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| GOMAP-L0 | 生命周期族（64 模块） | 治理链 | 会话/任务起止 | L1-L6 | config/governance_operations_map.yaml#L0_lifecycle | src/zephyr/autonomy_core、runtime | 七族挂载在册 | P3 |
| GOMAP-L1 | 监控族（143） | 治理链 | 运行面 | L3 熔断 | 同上#L1_monitor | src/zephyr/gov_audit、infra_ops | 同上 | P3 |
| GOMAP-L2 | 资源族（63） | 治理链 | 资源画像 | 排班闸 | 同上#L2_resource | src/zephyr/data/scheduler.py、trading/process_reaper | 同上 | P3 |
| GOMAP-L3 | 熔断族（21） | 治理链 | L1 告警 | L4 收割 | 同上#L3_fuse | src/zephyr/security（kill_switch） | 同上 | P3 |
| GOMAP-L4 | 收割族（39） | 治理链 | L3 | L5 自愈 | 同上#L4_reap | src/zephyr/trading/process_reaper | 同上 | P3 |
| GOMAP-L5 | 自愈族（95） | 治理链 | L4 | 恢复 | 同上#L5_selfheal | src/zephyr/infrastructure（auto_fix_engine 11 修复器） | 同上 | P3 |
| GOMAP-L6 | 审计族（4） | 治理链 | 全族 | 台账/复盘 | 同上#L6_audit | src/zephyr/gov_audit | 同上 | P3 |

nav 七段导航（治理文档管线，7 环节｜SSOT=config/nav_table_mapping.yaml，MOD-INF-002）：

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| NAV-1 | 想法（问题→目标→约束） | 治理链 | Owner/提案 | NAV-2 | config/nav_table_mapping.yaml#seven_stages① | 人工+PS-STD-011 | 七段+10 审计维在册 | P3 |
| NAV-2 | 草稿（结构化+查重） | 治理链 | NAV-1 | NAV-3 | 同上② | scripts/governance/d3_metadata/scan_deep_content.py | 同上 | P3 |
| NAV-3 | 审计裁定（多模型→Final Judge） | 治理链 | NAV-2 | NAV-4 | 同上③+裁定路由政策 | d12_ai_hallucination 校验器 | 同上 | P3 |
| NAV-4 | 蓝图（YAML canonical+MD 视图） | 治理链 | NAV-3 | NAV-5 | 同上④ | d5_architecture/validators 蓝图三件 | 同上 | P3 |
| NAV-5 | 施工（双面门禁：pre-commit+CI） | 治理链 | NAV-4 | NAV-6 | 同上⑤ | pre-commit 全量+CI governance.yml | 同上 | P3 |
| NAV-6 | 验收（零失败+四级准入） | 治理链 | NAV-5 | NAV-7 | 同上⑥ | run_all.py、validate_manifest_admission.py | 同上 | P3 |
| NAV-7 | 持续审计（漂移→追问根源） | 治理链 | NAV-6 | NAV-1 闭环 | 同上⑦ | run_all.py、CI | 同上 | P3 |

### 2.7 交付链（45 环节：图11 交付流水线 28 + 图14 施工流 17）

图11 交付流水线（28 段+2 gap｜SSOT=config/dev_delivery_map.yaml←骨架人工语义层契约真源（docs/_archive/_working_cleared/commitmap_cure/）｜REG-MAP-DEVDELIVERY-001；门禁双册=in_process_gate_registry 107 台+gate_registry 191 台）：

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| D11-S01 | 会话冷启动与开班检查 | 交付链 | — | S02 | config/dev_delivery_map.yaml#D11-S01 | AGENTS.md 冷启动序列 | S 车道在册 | P2 |
| D11-S02 | worktree 分配与池化 | 交付链 | S01 | S04 | #D11-S02 | scripts/session_worktree.py | 同上 | P2 |
| D11-S03 | 会话心跳与活性判定 | 交付链 | S02 | S08 | #D11-S03 | 同上 | 同上 | P2 |
| D11-S04 | 改前 claim（文件锁+基线） | 交付链 | S02 | S05 | #D11-S04 | scripts/lock_files.py | 同上 | P2 |
| D11-S05 | 在途编辑与暂存晋升 | 交付链 | S04 | S06 | #D11-S05 | staging 面 | 同上 | P2 |
| D11-S06 | 会话内 worktree 提交 | 交付链 | S05 | S07 | #D11-S06 | git_commit.py | 同上 | P2 |
| D11-S07 | 合并回主区（merge 正门） | 交付链 | S06 | C01 | #D11-S07 | session_worktree.py | 同上 | P2 |
| D11-S08 | 放弃与死会话回收 | 交付链 | S03 | 归档 | #D11-S08 | session_worktree.py（abort/archive） | 同上 | P2 |
| D11-S09 | 收尾注销与 handoff 交接 | 交付链 | S07/S08 | 下一班 | #D11-S09 | handoff 交接包 | 同上 | P2 |
| D11-C01 | 提交正门 CLI 与危险命令外壳 | 交付链 | S06/S07 | C05 | #D11-C01 | scripts/git_commit.py + git_safety_wrapper.ps1 | C 车道在册 | P2 |
| D11-C02 | 失败指引锚点递送 | 交付链 | C01 | 提交人 | #D11-C02 | git_commit.py | 同上 | P2 |
| D11-C03 | claim 结算与失败重试语义 | 交付链 | C01 | C06 | #D11-C03 | git_commit.py（--adopt-prior-work） | 同上 | P2 |
| D11-C04 | 全局串行锁与锁争用改道 | 交付链 | C01 | C08 | #D11-C04 | commit_queue.py（auto-enqueue） | 同上 | P2 |
| D11-C05 | in-process 门禁链执行 | 交付链 | C01 | C06 | #D11-C05 | src/zephyr/gov_enforcement/rule_enforcement（91 门） | 同上 | P2 |
| D11-C06 | 暂存与提交本体 | 交付链 | C05 | C11 | #D11-C06 | git_commit.py | 同上 | P2 |
| D11-C07 | pre-commit shell 门禁通道 | 交付链 | C01 | C06 | #D11-C07 | src/zephyr/gov_enforcement/commit_gates（191 台） | 同上 | P2 |
| D11-C08 | 入队即转活（快照入袋） | 交付链 | C04 | C09 | #D11-C08 | scripts/commit_queue.py（enqueue） | 同上 | P2 |
| D11-C09 | 排空调度与消费端 | 交付链 | C08 | C10 | #D11-C09 | commit_queue.py（drain） | 同上 | P2 |
| D11-C10 | 真落盘（worktree+CAS+收敛） | 交付链 | C09 | C11 | #D11-C10 | commit_queue.py | 同上 | P2 |
| D11-C11 | post-commit 对账与守卫 | 交付链 | C10 | C13 | #D11-C11 | POST-COMMIT-GUARD | 同上 | P2 |
| D11-C12 | 机器车道与紧急通道 | 交付链 | C10 | C13 | #D11-C12 | emergency_commit | 同上 | P2 |
| D11-C13 | 队列台账与运维观测 | 交付链 | C11/C12 | 观测面 | #D11-C13 | commit_queue.py（status/health） | 同上 | P2 |
| D11-D01 | 死信产生（不卡队） | 交付链 | C10 失败 | D02 | #D11-D01 | commit_queue.py | D 车道在册 | P2 |
| D11-D02 | 死因三分类甄别 | 交付链 | D01 | D03/D04 | #D11-D02 | dead-archive --content-level | 同上 | P2 |
| D11-D03 | 死信台账联动与告警 | 交付链 | D02 | task_board | #D11-D03 | 台账面 | 同上 | P2 |
| D11-D04 | requeue 复活链路 | 交付链 | D02 | C08 | #D11-D04 | commit_queue.py（requeue） | 同上 | P2 |
| D11-D05 | 级联失效判定 | 交付链 | D02 | D06 | #D11-D05 | cascade_stale | 同上 | P2 |
| D11-D06 | 死信归档轮换与清零战役 | 交付链 | D05 | 终态 | #D11-D06 | dead-archive | 同上 | P2 |

覆盖缺口（图自报）：D11-G01/G02 两个骨架外 gap 节点。wired=22/partial=4。

图14 施工升级流（17 段+11 gap｜SSOT=construction_workflow_policy.md 内嵌机读锚块（政策为真源，图 YAML 为派生件）｜REG-MAP-CWF-001）：

| 环节ID | 环节名 | 所属链 | 上游 | 下游 | SSOT 真源路径 | 代码模块指针 | 已有地图覆盖 | 挖矿优先级 |
|---|---|---|---|---|---|---|---|---|
| D14-01 | Session 冷启动 | 交付链 | 任务令 | D14-02 | policy Step 0 + config/construction_workflow_map.yaml#D14-01 | AGENTS.md §0 | 17 段在册（8 分段） | P2 |
| D14-02 | 文档审查 | 交付链 | D14-01 | D14-03 | policy Step 1 | sop/construction_sop | 同上 | P2 |
| D14-03 | 创建前搜索 | 交付链 | D14-02 | D14-04 | policy Step 1.5 | capability_lookup | 同上 | P2 |
| D14-04 | 架构评审门控判定 | 交付链 | D14-03 | D14-05/09 | policy Step 1.8 | 4 类变更触发器 | 同上 | P2 |
| D14-05 | 方案挖矿 | 交付链 | D14-04 | D14-06 | policy Step 1.9 | mining_sop | 同上 | P2 |
| D14-06 | 全景图登记（设计态先行） | 交付链 | D14-05 | D14-07 | policy Step 2 + RULE-DEPGRAPH | apply_depgraph.py | 同上 | P2 |
| D14-07 | 全图全库对齐 | 交付链 | D14-06 | D14-08 | policy Step 3 | align_all.py + alignment_checklist.md | 同上 | P2 |
| D14-08 | 后端盘点与拆件判定 | 交付链 | D14-07 | D14-09 | policy Step 3.5 | frontend_map.yaml | 同上 | P2 |
| D14-09 | 施工编码 | 交付链 | D14-08 | D14-10 | policy Step 4 | src/zephyr/*（全域） | 同上 | P2 |
| D14-10 | 单元测试与循环验收 | 交付链 | D14-09 | D14-11 | policy Step 5 | 测试体系 | 同上 | P2 |
| D14-11 | 长清单审查 | 交付链 | D14-10 | D14-12 | policy Step 6（12 节对抗审查） | review_sop | 同上 | P2 |
| D14-12 | 更新施工文档 | 交付链 | D14-11 | D14-13 | policy Step 7 | 文档体系 | 同上 | P2 |
| D14-13 | 全景图状态流转（design→production） | 交付链 | D14-12 | D14-14 | policy Step 8 | apply_depgraph.py（单调推进链） | 同上 | P2 |
| D14-14 | 文件完整性检查 | 交付链 | D14-13 | D14-15 | policy Step 9 | lock_files.py/lock 巡检 | 同上 | P2 |
| D14-15 | 提交网关落地 | 交付链 | D14-14 | D14-16 | policy Step 10 | scripts/git_commit.py（=图11-C 正门） | 同上 | P2 |
| D14-16 | 临时文件清理 | 交付链 | D14-15 | D14-17 | policy Step 11 | trae_071 清扫三步法 | 同上 | P2 |
| D14-17 | worktree 合并与清理 | 交付链 | D14-16 | 收班 | policy Step 12 | session_worktree.py（archive --execute） | 同上 | P2 |

覆盖缺口（图自报）：unwired_no_caller=15、build_status pending=15、by_verifiability manual=20。

## 3. 地图未覆盖环节——缺口清单（只登记实证，不发明环节）

图内已自报的账务缺口（各图 counts/boundary 块原文）：
1. FACTORY：341 节点仅 17 边、counts 块空——层间边未接线（ROOR 注记在案）。
2. 图14：15 环节 unwired_no_caller、15 pending。
3. 图13：4 gap 节点、6 unwired_no_caller、5 unwired_slot_hollow。
4. 图12：71 缺口在册、15 gap 节点、DSC-GAP-TERMINUS（可证终点=归档清单+任务级对账案卷）、5 张待供表（account_nav_daily/execution_report/factor_feature_value/factor_signal/reconciliation_differences）、news_data 幽灵引用。
5. 图11：D11-G01/G02 骨架外缺口件（无运行代码可挂）。
6. 图15：42 卡 headless 未登记态、3 needs_adjudication、6 gaps。
7. GOMAP：suspect_orphans=64（实读）——ROOR 仍写 94/total_modules=450，两处漂移待对账（本批实读=429 模块/64 孤儿）。

链路尚未成图的结构性缺口（有入口无环节图）：
8. 安全治理链：LSG 网关（zephyr.security.llm_defense）、KillSwitch、红蓝对抗（red_blue_validator）——宪法 §7 有入口、ROOR 有注册表，但无链路图覆盖其环节。
9. research 双管线：blueprint_routing.yaml 仅 primary/research 路由声明；全自动研究生产线（research_production_line_policy 13 岗位卡）无链路图。
10. 前端/仪表盘链：src/zephyr/frontend/dashboard/api_server.py + frontend_map.yaml 是静态盘点面，无环节链图。
11. 实盘执行出域通道：QMT 券商接口的"指令出域→柜台回执"环节仅由 TDM-E-L4/X-S2 节点与图13 D13-07/28 承载，无独立执行链图（监管合规 8 字段在 REG-EXA-001 在册）。
12. 裁定路由全半程：adjudication_routing_policy 八类路由+生死两轨未成图；图16 立法流只覆盖"裁定→规则→gate"半程。
13. 考核↔决策两图交界：E4 考试（FACTORY）与 TDM 挂图之间靠图15-D15-S12 graduated + FACTORY handoffs 声明衔接，无机械对账件（毕业包→挂图→生产的闭环对账缺失）。
14. 宏观指标供给：macro_indicator_series_map.yaml 只是"指标 ID→序列码"翻译层（16 条），宏观指标自身的采集→入库环节散挂图12-DSC-03/图13-D13-40，无专段。

## 4. 挖矿工程建议切片（每环节一本子文档的分组）

- P0 批（先挖，共 22 环节）：TDM 14 段 + FACTORY E1/E3/E4/E8 + 图15 S5-S8/S12 + 图13 五个一等节点（D13-09/21/28/29/30/32/34）+ 图12 DSC-15。
- P1 批：图13/图12 其余段（图已满配血肉，子文档=按图细分+核对 machine facts）。
- P2 批：图11/图14 全 45 段——挖矿动作=缺口收口（把 unwired/pending 清成 wired）。
- P3 批：立法流 6 态 + GOMAP 七族 + nav 七段（状态机小件，半日可清）。
- 缺口批：§3 的 14 条，逐条立 issue/议题，不经本骨架发明环节。

## 勘误 2026-10-15 封矿时点

> 封矿书记员追加（只记勘误不动正文）。两处计数漂移=矿工回报+书记员机械复核双证，索引与证据=00_INDEX.md。

1. **TDM 四 flow 一级环节节点计数漂移（疑流根重复计入）**：本骨架 §2.3 行内节点数 L1=10/L2=30/L3=26/L4=16/C2=6；地图实读（config/trading_decision_map.yaml nodes 逐 node_id 前缀机械计数，2026-10-15 复核）=L1=9/L2=29/L3=25/L4=15/C2=5——五处各整多 1，特征与"流根节点重复计入"吻合；L0=5/C1=4/C3=6 与骨架一致。矿工回报与书记员复核一致。
2. **"in-process 91 台"过期**：§2.7 D11-C05 行代码指针"src/zephyr/gov_enforcement/rule_enforcement（91 门）"过期——in_process_gate_registry.yaml 册面 total_gates=107 且 gate_id 逐行实数=107（2026-10-15 机械数）；§2.7 头注"107 台"与行内"91 门"自相矛盾，行内应更新为 107。D11-C05 子文档同记此发现。
