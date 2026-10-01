---
ttl: task_bound
title: 端到端全流通环节骨架总册（S2）——132 环节 / 13 段 / 四红叉翻绿复测
session: st-ffchief-20261001
date: 2026-10-01
status: skeleton
---

# 端到端全流通环节骨架总册（S2·st-ffchief-20261001）

> **一句话**：在昨夜 storageswap 总包底册（链路面六线）之上，把全仓端到端环节骨架收敛为 **132 环节 / 13 段**（F01-F122 既有 + F123-F132 定版未落册），逐环节给上游/下游/代码入口/自动化态/三态，并复测 09-26 骨架的 7 处红叉位（**4 处已翻绿**）。
> **方法**：七真源互证，禁臆造，全部数字本文写作时实跑复核（命令见 §0.2）：
> ①`docs/_working/night_totalflow_chief/00_skeleton.md`（底册，六线+链路面终态，增量不推倒）
> ②`config/trading_decision_map.yaml`（TDM，182 节点四流，实跑 `grep -c "^- node_id:"`=182）
> ③`docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（**旧 122 环节/13 段骨架真身**，F01-F122 全表+DAG+断链点——任务线索指向 total_circulation_night/ 为错位，勘误见 §4-11）
> ④`docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（定版卷：Z=132、30 行 partial 细目、四方映射、口径漂移钉死）
> ⑤config 九图：`strategy_production_map`(16 FAC 节点)/`data_supply_chain_map`(图12：5 段43节点62边)/`trading_day_cycle_map`(图13：4 段48节点64边)/`dev_delivery_map`(图11：3 层30节点)/`construction_workflow_map`(图14：8 层29节点)/`strategy_card_lifecycle_map`(图15：13 态17 迁移)/`governance_operations_map`(GOMAP 机生：446 模块 wired246+15)/`macro_indicator_series_map`/`chainmap_cluster_names`
> ⑥`docs/registry_of_registries.yaml`（ROOR）+`docs/02_enterprise_architecture/00_overview_entry/navigation_index.md`（77 域文档机生，43 域集成拓扑）
> ⑦`docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md`（**规则型真源**：三层对齐规则+16 表挂轴义务，本身不含逐环节行——环节对齐键真源=TDM node_id/depgraph module_id，勘误见 §4-10）
> ⑧`src/zephyr` 顶层域实扫 57 目录（域覆盖核对见 §4-4）。

## 0.1 三态判读口径（承总册 §0 并收敛为挖矿三态）

- **挖干**=built：证据表明建成在跑（含本次复测翻绿的 4 环，注记"翻绿"）。
- **存疑**=partial/design：有实件但声明未闭环，或设计 done 未施工。
- **盲区**=missing/登记态/新号未挖：module_ref=null、零实件、或 F123-F132 新号仅有定位无六向台账。

## 0.2 复核命令（本轮实跑读数）

```bash
grep -c "^- node_id:" config/trading_decision_map.yaml          # 182（E128/P18/X19/F13/C4+crypto4）
grep -c "module_ref: null" config/trading_decision_map.yaml     # 37（09-27 定版卷测 38，AGG 已接线，见 §4-8）
grep -c "node_id: FAC-" config/strategy_production_map.yaml     # 16（E0-E9+E1A-E1G）
ls src/zephyr/strategy_pipeline/promotion_advisory.py           # 存在，895 行（F74 翻绿证据）
grep -n "trigger_lane_g_intake" src/zephyr/data/scheduler.py    # :537-544 事件沿（F20 翻绿证据）
find src/zephyr -maxdepth 1 -type d | grep -v __pycache__ | tail -n +2 | wc -l   # 57
```

## §1 段表（13 段 / 132 环节）

链路健康判据：红=段内存在断链级 P0 或 missing 主链环节；黄=存在 partial/design/待裁注记；绿=全 built 无断链注记。

| 段id | 名称 | 环节计数 | 链路健康 | 依据 |
|------|------|---------|---------|------|
| A | 数据供给链 | 16（F01-F12+F123/F125/F126/F127） | **红** | 底册链路面：tick✅/板块分钟✅/cffex✅/元数据✅，但 TI 派生链⚖️回填中；F04 清洗三引擎零接线、F02 串接空地（总册 §二红叉位×2） |
| B | 策略供给链＝策略工厂 | 18（F13-F29+F129） | 黄 | FAC 图 build_status：built 5（E4/E5/E6/E7/E1A）/partial 11；无 missing；F20 事件接线已翻绿 |
| C | 知识供给线（TDM L9） | 8（F30-F36+F131） | **红** | F30/F31 两登记态 missing；L9 null 节点 37 个（含段头）；F34 AGG 翻绿待深核 |
| D | 交易决策消费链（TDM 四流） | 16（F37-F52） | 黄 | 主链 F37-F50 全 built；F51 币圈 V0 空壳（P2 设计内）；TDM 182 节点与总册 D 段口径吻合 |
| E | 执行基建链 | 6（F53-F58） | 黄 | 主链 built；F58 成本反馈 partial；F56 SimBridge 取证线索在案 |
| F | 风控合规链 | 5（F59-F63） | **红** | 全 built 但 F62 合规门"码成闸空零注入"=断链级 P0（M7 在案）；F61 持久化待裁 |
| G | 回测模拟链 | 8（F64-F71） | 绿 | 全 built；F68 GPU T1 在跑禁中动（注记不降级） |
| H | 模拟盘→转正链 | 4（F72-F75） | **红** | F72 SimBridge 断链嫌疑、F73 晋升判据执行器未写（design）、F74 翻绿待核、F75 partial——转正主门四环无一干净 |
| I | 运行时调度常驻链 | 11（F76-F85+F132） | 黄 | 7 built+3 partial（F82 order_daemon 未接线/F84/F85）；reaper 链✅（底册 RULE-GUARDIAN 面） |
| J | AI 层链 | 13（F86-F96+F130） | 黄 | 网关 F88 built（拦截面 4 库注记）；F86/F87/F92 partial、F94/F95 design 面；F92 entry_count=0 空转 |
| K | 治理门禁链 | 16（F97-F110+F124/F125 交界/F128） | 绿 | 全 built；commit 侧 23 环节引用不重挖；GOMAP suspect_orphans=94 为待挖面非断链 |
| L | 前端报告链 | 5（F111-F115） | 黄 | F112 红点（AI 层两新页三层三断点）、F115 partial，余 built |
| M | 全局横切段 | 6（F116-F122，F121 Owner 门挂起） | 黄 | F120/F121 design、F122 partial（M4/M5 边界），余 built |

合计：绿 2 ｜ 黄 7 ｜ 红 4（A/C/F/H）。

## §2 环节总表（132 环节）

列说明：环节id=段-序(F号)｜上游/下游用 F 号｜代码入口=主锚点（全锚点见 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md` 对应行，不复制）｜自动化态=自动触发/定时/常驻/手动/断链/无消费｜数据进出=主输入→主输出｜三态=挖干/存疑/盲区。

### A 段·数据供给链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| A-01(F01) | 多源采集调度 | 外部源 | F04/F06/F10 | `python -m zephyr.data`；resource_profile_registry(96 实体) | 定时（交易日历 271 任务/252 CH 表） | 外部 10 源→CH 热库/PG/冷库 | 挖干 |
| A-02(F02) | 数据源接入生命周期 | F31/F96 | F01 | sop/data_ops_sop/data_source_onboarding_sop.md | 手动（SOP 流程，工段串接空地） | 源申请→建表→验收三查→路由 | 存疑(P0) |
| A-03(F03) | Provider 实现与源路由 | F02 | F01 | src/zephyr/data/implementations/（miniqmt_provider 等 10 源） | 定时（随采集槽） | 源 API→标准化行 | 挖干 |
| A-04(F04) | 清洗校验与坏数修复 | F01 | F06 备用库 | src/zephyr/data/cross_source_validator.py、backfill_checker.py | **断链**（清洗三引擎零接线，M1 在案） | CH 行→校验报告/回补 | 存疑(P0) |
| A-05(F05) | 判重与数据审计 | F01 | F12 | scripts/.../check_tick_duplication.py；data_audit_sop | 定时 | tick 全量→判重/审计结论 | 挖干 |
| A-06(F06) | CH 热库落库 | F04 | 全部消费端 | src/zephyr/data/ch_config.py；scripts/ch/apply_*_ddl.py | 定时 | 行→CH 252 表（板块分钟链✅0930=171,351 行） | 挖干 |
| A-07(F07) | PG 架构库 | 生成器 | 全部治理端 | scripts/governance/.../generate_project_depgraph.py | 事件（生成器触发） | 源码扫描→depgraph 9148 节点 | 挖干 |
| A-08(F08) | 冷库归档运维 | F06 | 长周期回测 | scripts/ch/archiver.py | 定时 | CH→F:/zephyr_cold Parquet | 挖干(待深挖) |
| A-09(F09) | 备份 3-2-1 双链 | 全库 | 灾备 | scripts/backup/backup.ps1、backup_ch_vm.ps1 | 定时（夜镜像+月度离场） | D 项目+F 冷库→G 总仓 | 挖干 |
| A-10(F10) | 行情订阅分发 | F01/券商 | 盘中决策链 | src/zephyr/data/scheduler.py；sch_tick_subscriber | 常驻（tick 订阅，0929/0930 双日 57M+ 行✅） | 券商 tick→盘中槽位 | 挖干 |
| A-11(F11) | TDM 交叉轴挂接 | 各注册表 | TDM 全图 | src/zephyr/trading/decision_map.py:100（_XREF_SPECS） | 事件（注册表加载） | 16 表(宪法口径)/13 轴(代码口径)→TDM | 挖干(漂移待核) |
| A-12(F12) | 产业链图谱 | F05 | F18/F32 | docs/.../catalogs/chain_registry.yaml（机生） | 机生 | 审计后数据→873 条图谱 | 挖干 |
| A-13(F123) | DB schema 迁移通道 | B-9 迁移册 | A 段全库面 | migration_registry.yaml（册在 HEAD，13 条 pending 退役议题=Owner 门） | 未建 | schema 变更→受控迁移 | 盲区(P0 新号) |
| A-14(F125) | data_governance 数据治理本体 | A/K 交界 | 治理层 | src/zephyr/data_governance/（21 py） | 未挖 | 数据面→治理动作 | 盲区(P0 新号) |
| A-15(F126) | 字段字典 REG-FLD-001 | A/K 交界 | schema 治理面 | 字段字典册（8280 行 schema v2.0） | 静态册 | 全库字段→字典条目 | 盲区(P1 新号) |
| A-16(F127) | data_eng 数据工程域 | A 段 | 冷储/湖 | src/zephyr/data_eng/（16 py，与 F08 冷储交叠=勘误点） | 未挖 | 湖/冷储工程件 | 盲区(P1 新号) |

段内链路面增量（底册）：TI 派生链⚖️ ti_minute_recalc.py 锚 09-01 全分钟主跑中（~20-25h，L-B 翻案回填）；板块分钟生产者更替=internal_eqw 唯一生产者（10-09 接产，J 腿 dry-run 留观，tdx 五任务退役留观，resample 判死）。

### B 段·策略供给链＝策略工厂

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| B-01(F13) | E0 算力调度心跳 | 日历/数据到达 | 全工厂重任务 | MOD-BT-151 拉式闸门 | 事件（四枚理由码闸） | 日历+资源→放行/拒 | 存疑 |
| B-02(F14) | E1 想法进货编排 | F15-F20 | F21 | MOD-BT-154 factory_intake_pipeline | 事件（六车道并发） | 各车道→strategy_intake 台账+出生证 | 存疑(E1C 待施工) |
| B-03(F15) | 车道A·社区货源 | 社区源 | F14 | MOD-BT-035；data/strategy_intake/normalized/ | 定时（爬取批次） | 聚宽/掘金→597 条入库 | 挖干 |
| B-04(F16) | 车道B·AI 生成 | 本地/LLM | F14 | MOD-BT-150；lane_b_candidates.csv | 手动/LLM 批 | 自然语言→策略假说 | 存疑 |
| B-05(F17) | 车道C·公式挖掘机 | F21 反哺种子 | F14 | MOD-BT-155+158；factor_mining_whitelist.yaml | 事件+手动（双轨分期已裁定） | DSL→增量 IC 验收 | 存疑 |
| B-06(F18) | 车道D·产业链三高 | F12 | F14 | MOD-BT-090；three_high_candidates.csv | 事件（图谱驱动） | BOM 拆解→三高候选 | 存疑(LLM 增补未建) |
| B-07(F19) | 车道E·模型基线 | 行情库 | F14/F22 | MOD-BT-084+194+195 | 定时 | 行情→分位回归/Kronos 基线 | 存疑 |
| B-08(F20) | 车道G·全网搜索进货 | F96 胃 | F14 | MOD-AUTO-E1G-001；lane_g_stomach_intake.py | **事件（翻绿）**：scheduler.py:537-544 intel_harvester.trigger_lane_g_intake（st-chief4x-gut-20260927） | inbox 情报→0-2 假说/篇 | 挖干(翻绿) |
| B-09(F21) | E2 假说预审逻辑门 | F14/F28/F50 | F22 | MOD-BT-091；c1_backtest.hypothesis_precheck | 事件 | 假说→过/死（经济学门） | 存疑 |
| B-10(F22) | E3 构造与翻译 | F21 | F23 | MOD-BT-041..075+159+190 | 事件 | 外来策略→标准考卷件 | 存疑 |
| B-11(F23) | E4 考试咽喉 | F22 | F24 | MOD-BT-039；c1_backtest.strategy_screen | 事件 | 考卷件→IS/DSR/OOS 判定 | 挖干 |
| B-12(F24) | E5 协同去重 | F23 | F25 | MOD-BT-086 | 事件 | 及格件→正交化+增量 IC | 挖干 |
| B-13(F25) | E6 入库监控 | F24 | F26/F14 反馈 | MOD-BT-078；data/backtest_artifacts/runs/ | 事件+定时监控 | 幸存者→台账只增+判死行 | 挖干 |
| B-14(F26) | E7 模拟盘前哨 | F25 | F27/F72 | **MOD-BT-225（翻绿）**：src/zephyr/strategy_pipeline/paper_outpost.py（[STARTUP] manual） | 手动启动+日跑（触发链待核） | live 数据→逐日对账报告 | 挖干(翻绿，STARTUP=manual 待核) |
| B-15(F27) | E8 组装与资金分配 | F26 | F74/F48 | MOD-PA-002..024 | 事件 | 幸存者→sleeve+regime 分配 | 存疑(P0：sleeve 落库/再平衡调度/TDM 对接未闭环) |
| B-16(F28) | E9 实盘归因 | 实盘账本 | F50/F21 | MOD-PF-007 | 定时 | 实盘账本→Brinson/因子归因 | 存疑(P0：IS 分解 FIELD-GAP/影子组合未建) |
| B-17(F29) | 工厂进货台账与出生证 | F14-F22 | 全工厂 | data/strategy_intake/*；factory_intake_pipeline.py | 事件 | 各阶段件→manifest 族 | 存疑 |
| B-18(F129) | ml_train 训练线 | B/J 交界 | F19 | src/zephyr/ml_train/（43 py） | 未挖 | 数据→模型训练 | 盲区(P1 新号) |

### C 段·知识供给线（TDM L9）

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| C-01(F30) | L9 源线·行情基本面族 | A 段 | F34 | TDM-E-L9-A01..A16（module_ref 全 null） | **无消费**（登记态） | 16 源线→汇聚点 | 盲区 |
| C-02(F31) | L9 源线·另类数据族 | 外部 | F34/F96 | TDM-E-L9-B01..B10、C01..C03（null）；alt_data/ 28 py | **无消费**（登记态） | 另类源→汇聚点 | 盲区 |
| C-03(F32) | L9 图谱谱系 | F12 | F34/F18 | TDM-E-L9-G1..G5；equity_penetration.py（G3 有码，余 null） | 机生+手动 | 图谱→5 谱系 | 存疑 |
| C-04(F33) | L9 状态变量快照 | F38 | F34 | TDM-E-L9-V1..V3；plan_engine/judgment_ledger.py | 事件（盘中） | 盘面→三快照判断账本 | 存疑 |
| C-05(F34) | L9 知识供给汇聚 | F30-F33 | F35/D 段 | TDM-E-L9-AGG（**翻绿**：module_ref 已非 null，yaml:5139） | 事件 | 全源线→知识层 | 挖干(翻绿待深核) |
| C-06(F35) | L9 决策假设与一问一考 | F34 | F23/回灌 | TDM-E-L9-D1/D2/E1/E2（D2/E2 null）；mcts_expression_search.py、validation/runner.py | 事件 | 知识→因子组合→考试方案 | 存疑 |
| C-07(F36) | L9 治理横切 | 全 L9 | 治理层 | TDM-E-L9-Z1/Z2（Z1 null）；reconcile_chain_refs.py | 事件 | L9 面→治理状态机 | 存疑 |
| C-08(F131) | nlp 文本情报处理线 | C 段 | F96/F16 | src/zephyr/nlp/（7 py：news/sentiment） | 未挖 | 文本→情感/事件 | 盲区(P2 新号) |

### D 段·交易决策消费链（TDM 四流）

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| D-01(F37) | L0 盘前作战计划 | F33/F50 | F38-F41 | TDM-E-L0-01..04；plan_engine/daily_warroom_pipeline.py 等 4 件 | 定时（盘前）+事件 | 快照+归因→今日计划 | 挖干 |
| D-02(F38) | L1 大盘总闸+六传感器 | A 段行情 | F39-F41 | TDM-E-L1-*；regime/core/regime_detector.py、anchored_state_machine.py | 定时（盘中判定） | 指数/结构/情绪/波动/宏观→7 态 | 挖干 |
| D-03(F39) | L2 板块选择 | F38 | F40/F41 | TDM-E-L2-*；signal_ashare/sector/ 全族 | 定时（盘中） | 板块行情→10 组 30 节点评分 | 挖干 |
| D-04(F40) | L3 个股选择 | F39 | F41 | TDM-E-L3-*；selection_funnel.py、negative_veto.py 等 | 定时（盘中） | 板块→九阶段选票→候选池 | 挖干 |
| D-05(F41) | L4 买卖点与执行 | F40 | F53-F58 | TDM-E-L4-*；ex_core/、ex_sor/ | 事件（信号→订单） | 候选→买卖点→订单指令 | 挖干(P0) |
| D-06(F42) | P1 持仓体检 | F57 对账 | F43/F45 | TDM-P-P1-*；position/core/ 全族 | 定时（对账驱动） | 持仓+行情→体检/动作清单 | 挖干 |
| D-07(F43) | P2 做T与加减仓 | F42 | F44/F46 | t_trade_coordinator.py、rebalance_engine.py | 事件 | 体检→做T/减仓动作 | 挖干 |
| D-08(F44) | P3 加仓决策 | F42 | F41 | pyramiding_rules.py、position_sizing_engine.py | 事件 | 体检→金字塔加仓 | 挖干 |
| D-09(F45) | S1 卖出信号收集评分 | F42/F38 | F46 | TDM-X-S1-*；sell_signal_* | 事件 | 行情+持仓→六桶融合紧迫度 | 挖干(P0) |
| D-10(F46) | S2 离场执行 | F45 | F53-F57 | sell_execution_planner.py、sell_session_router.py | 事件 | 卖出信号→路由/分批/约束 | 挖干(P0) |
| D-11(F47) | R1 应急保命 | F59/F60 回撤 | 全流（横切） | kill_switch.py、drawdown_state_machine.py | 事件（熔断触发） | 回撤分级→熔断/白名单 | 挖干(P0) |
| D-12(F48) | C1 预算切分 | F27/F71 | F49 | TDM-F-C1；multi_strategy_capital_allocator.py | 事件 | 组合→预算切分 | 挖干(P0) |
| D-13(F49) | C2 组合聚合 | F48 | F50 | TDM-F-C2-*；firm_risk_aggregator.py、correlation_regime_monitor.py | 事件 | 预算→净额轧平/约束栈 | 挖干 |
| D-14(F50) | C3 绩效归因反馈 | F49/F28 | F37/F21 回灌 | performance_attribution_engine.py、lifecycle_state_machine.py | 定时（评审周期） | 绩效→升降级/调权/回灌 | 挖干 |
| D-15(F51) | 币圈决策骨架 | — | — | TDM-C-L1..L4（module_ref 全空） | **无**（V0 空壳，markets 声明第二实例） | — | 盲区(P2 设计内) |
| D-16(F52) | 验证方法学与决策算法库 | — | F23/F35/F66 | REG-VALM-001、REG-DAL-001（+B-1/B-2 并入：REG-TECHNICAL-INDICATOR/PAT） | 静态册（引用态） | 方法学/算法条目→消费节点 | 挖干 |

### E 段·执行基建链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| E-01(F53) | 订单生命周期与预检 | F41/F46 | F56/F57 | order_manager.py、pre_execution_checker.py、price_cage.py | 事件 | 订单指令→状态机流转 | 挖干(P0) |
| E-02(F54) | 打板执行族 | F41 | F53 | ex_core/daban_*.py 六件套 | 事件 | 打板信号→瞬时执行 | 挖干 |
| E-03(F55) | 执行算法路由 SOR | F41/F46 | F53 | algo_execution_selector.py、broker_adapter_manager.py | 事件 | 订单→拆单/场所选择 | 挖干 |
| E-04(F56) | QMT/miniQMT 桥 | F53 | 券商→F57 | miniqmt_broker.py、qmt_trading_session.py、broker_link_probe.py | 常驻（会话） | 订单↔券商通道 | 挖干(SimBridge 取证线索在案) |
| E-05(F57) | 结算对账与三方核对 | F56 | F42/F63 | settlement_reconciliation.py、three_way_reconciliation.py、eod_reconciliation.py | 定时（盘后/EOD 四步） | 券商流水→对账报告 | 挖干(P0) |
| E-06(F58) | 执行成本反馈 | F57 | F55/F28 | execution_quality_scorer.py（TDM-E-L4-14） | 事件 | 成交质量→选型回写 | 存疑 |

### F 段·风控合规链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| F-01(F59) | 风控限额与止损引擎 | REG-RLM-001(117 条) | F47/F41 | risk_manager.py、atr_stop_engine.py、ashare_stop_loss_engine.py | 事件 | 持仓+行情→限额/止损 | 挖干(P0) |
| F-02(F60) | 回撤状态机与熔断 | F63 NAV | F47 | drawdown_state_machine.py、drawdown_liquidation_guard.py、drawdown_broker_side_stop.py | 事件 | NAV→回撤分级/双保险 | 挖干(P0) |
| F-03(F61) | KillSwitch 三实例族 | F47/F59 | 全交易面 | trading_kill_switch.py、capacity kill_switch.py、access_control/kill_switch.py | 事件 | 熔断信号→全交易面闸 | 挖干(持久化待裁) |
| F-04(F62) | 合规门与程序化交易报告 | REG-CMP-REPORT-001 | F53 拒单 | src/zephyr/compliance/ | **断链**（码成闸空零注入=M7 在案 P0；broker_ack 人工回填） | 报备单→先报告后交易闸 | 存疑(P0 断链级) |
| F-05(F63) | 仓位管理与对账 | F57 | F42/F60 | position_state_machine.py、position_reconciler.py、live_nav_recorder.py | 定时+事件 | 成交→持仓状态/NAV | 挖干(P0) |

### G 段·回测模拟链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| G-01(F64) | 回测三件套 | REG 三册 | F65/F66 | universe/benchmark/cost_model_registry.yaml | 静态册（MUST 引用） | 三册条目→每次回测 | 挖干 |
| G-02(F65) | 回测引擎族 | F06/F64 | F66 | matching_engine.py、ch_tick_replay.py | 事件（跑批） | CH tick→撮合/组合核算 | 挖干 |
| G-03(F66) | 回测预注册与七步循环 | F64 | F25/F67 | generate_backtest_backlog.py；sop_a/sop_b | 手动（预注册门，无注册不归档） | 137 对象→跑前写死阈值 | 挖干 |
| G-04(F67) | 实验登记与档案 | F66 | F50 | experiment_registry.yaml | 手动登记 | 实验→11 条档案 | 挖干 |
| G-05(F68) | GPU 矩阵/工厂格子 | F13 | F66 | gpu_consensus_scheduler.py、factory_grid_executor.py | 定时（35.33s/格×4640 格） | 任务→GPU 共识矩阵 | 挖干(T1 在跑禁中动) |
| G-06(F69) | T0/成本门/IBT | F64 | F66 | exam_cost_gate.py | 事件（考试内嵌） | 成本双口径→门判定 | 挖干 |
| G-07(F70) | 模拟撮合与偏差检测 | F65 | F72 | look_ahead_bias_detector.py、overfitting_protection_gate.py、deflated_sharpe_calculator.py | 事件 | 回测→偏差/过拟合/DSR | 挖干 |
| G-08(F71) | AutoRuntime Core | 全链 | 全链 | `python -m zephyr.trading`→auto_runtime_core.py | 常驻（系统大脑：三层路由/work DAG） | 全链状态→节律调度 | 挖干(P0) |

### H 段·模拟盘→转正链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| H-01(F72) | 模拟盘日跑四件 | F25/F70 | F73/F74 | live_strategy_adapter.py；sch_paper_session、sch_sim_bridge_execute | 定时（日跑）——**SimBridge 09-24 静默断链嫌疑（M5 在案）** | registry 幸存者→模拟盘对账 | 存疑(P0) |
| H-02(F73) | A/B 联赛与分仓 | F72 | F74 | automation 骨架 §7；exam_policy.md | **未施工**（晋升判据执行器未写，design） | 模拟盘→champion/challenger | 存疑(P0 design) |
| H-03(F74) | 转正建议书汇总器 | F72/F73 | **Owner 门位→实盘（全链唯一人工门）** | **MOD-BT-199（翻绿）**：promotion_advisory.py 895 行+pipeline_events 消费+api_server POST /api/promotion-decide；ZEPHYR_OWNER_APPROVAL_TOKEN fail-closed | 事件（advisory_due）+**人工拍板 decide** | 四件产出→建议包→Owner 决策台账 | 挖干(翻绿；Owner 门设计内人工) |
| H-04(F75) | 策略生命周期状态机 | F23-F27 | REG-STR-001 | lifecycle_fsm.py、intake.py、registry_writer.py、screen_source.py | 事件 | 考试/模拟结果→FSM 流转 | 存疑 |

### I 段·运行时调度常驻链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| I-01(F76) | Windows 计划任务群 | — | 全链 | resource_profile_registry.yaml(96 实体)；register_*.ps1 | 定时（sch_*/ops_* 族） | 日历→任务触发 | 挖干 |
| I-02(F77) | 数据调度常驻 | F76 | F01 | src/zephyr/data/scheduler.py | 常驻 | 日历→采集/订阅槽位 | 挖干 |
| I-03(F78) | belt daemon | F76 | 提交链 | commit_belt_daemon.py | 常驻 | 提交带→心跳 | 挖干 |
| I-04(F79) | reaper 与水位监控 | F76 | 全链安全 | process_reaper.py | 定时+常驻（keep 白名单） | 进程/内存→收割 | 挖干 |
| I-05(F80) | 资源画像与排班 | F76 | 全链 | MOD-RESCHED-PROFILE/SAMPLER/GATE/ALERT/VIEW | 定时（晨报/周历） | 96 实体 18 字段→排班 | 挖干 |
| I-06(F81) | 监控告警 | 全链 | 值守 | health_monitor.py；REG-ATH-001(38 条) | 常驻+定时 | 健康/阈值→告警 | 挖干 |
| I-07(F82) | 订单与结算常驻 | F57 | F63 | post_settlement_pipeline.py、night_shift_queue.py；ai_layer/scheduling/order_daemon.py（件在） | **断链**（order_daemon 建成未接线=M5 在案 P0） | 盘后→夜班队列/recon | 存疑(P0) |
| I-08(F83) | 自动化班底 | F76 | 全链 | automation_crew_policy.md；automation_master_plan.md | 定时（双引擎两班制夜班 9 席） | 任务卡→夜班执行 | 挖干 |
| I-09(F84) | 反馈循环 FBL | F81 | 治理/演进 | src/zephyr/feedback_loop/（core/evolution_engine/error_budget） | 事件 | 告警→诊断→自动回滚 | 存疑(M5 补挖) |
| I-10(F85) | 环境与启动链 | F76 | 全链 | windows_service.py、register_desktop_shell_startup.ps1 | 定时（冷启动三步） | 开机→服务/shell/AI wrapper | 存疑(M5 补挖) |
| I-11(F132) | infra_ops 运维工程域 | I 段 | 运维面 | src/zephyr/infra_ops/（6 py：loki/storage_cost/wal_monitor） | 未挖 | 运行面→运维指标 | 盲区(P1 新号) |

### J 段·AI 层链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| J-01(F86) | AI 六族管线 | F96 | 演进闭环 | src/zephyr/ai_layer/{perceive..heritage}/ | 事件 | 情报→六族处理 | 存疑(M4 DDL 未部署) |
| J-02(F87) | AI 红线 | 治理层 | F86 | ai_layer/redline/ | 事件 | 行为→红线裁决 | 存疑 |
| J-03(F88) | LSG 安全网关 | — | 全部 LLM 面 | security/llm_defense/llm_security/gateway.py | 常驻（横切） | LLM 调用→五层防御审计 | 挖干(拦截仅 4 库注记) |
| J-04(F89) | 本地模型与嵌入 | 模型源 | F86/F16 | capability_cards/{ollama_chat,embedding_router,...}.yaml | 定时（24/7 排程） | prompt→本地推理/嵌入 | 挖干 |
| J-05(F90) | Agent 编排与 A2A | F90 | 全链 | orchestrator/、autonomy_core/、integration/mcp/ | 事件 | 任务→skills 60+ 编排 | 挖干 |
| J-06(F91) | 能力反查渐进披露 | — | 施工前置 | governance/capability_lookup.py；capability_cards/ | 手动（施工时反查） | 关键词→378 能力条目 | 挖干 |
| J-07(F92) | 原问题账本 | F35 | 研究闭环 | governance/meta_question/（snapshot.py 机生） | 事件——**entry_count=0 空转** | 问题→PG 三表生命周期 | 存疑(P2) |
| J-08(F93) | PG 图书馆 | F92 | 知识面 | library/librarian.py、lookup.py | 事件+手动 | 资产→编目/检索 | 挖干 |
| J-09(F94) | AI 层七段循环设计面 | — | F86 施工 | ai_layer_vision/L1..L7/DESIGN.md | **无**（design_done 未施工） | — | 存疑(design) |
| J-10(F95) | OBJ 四对象线设计面 | F94 | 施工批次 | ai_layer_vision/OBJ_{M,T,S,R}/DESIGN.md | **无**（31 项待 Owner 处置） | — | 存疑(design) |
| J-11(F96) | 胃·全网搜索消化设备 | F31 | F20/F02 | docs/_working/automation/inbox/；搜索设备 v0 | 事件（业务线 v0，升级归 AI 层） | 全网→清洗→intel-*.md | 存疑 |
| J-12(F130) | ml_serve 模型服务 | J 段 | F19 数值族 | src/zephyr/ml_serve/（11 py，与 F89 分界=数值 ML vs LLM） | 未挖 | 模型→服务 | 盲区(P1 新号) |
| 注 | knowledge 域（Owner 门） | — | — | src/zephyr/knowledge/（15 py） | 未定 | 裁-6 vs F93 边界未裁 | 盲区(Owner 门挂起) |

### K 段·治理门禁链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| K-01(F97) | commit 侧门禁链 | — | 提交链 | commit_gate_registry.yaml（23 环节引用不重挖） | 事件（提交时） | diff→23 环节门禁 | 挖干 |
| K-02(F98) | GateEngine 运行时门禁 | 规则 | 全链 | gov_enforcement/rule_enforcement/（91 门 canonical） | 事件 | 动作→GatePipeline | 挖干 |
| K-03(F99) | 漂移检测 | F98 | 告警 | src/zephyr/gov_drift/（30 检测器） | 常驻（双 watchdog） | 基线→漂移告警 | 挖干 |
| K-04(F100) | 红蓝对抗 | — | F98 | security/adversarial_validation/ | 定时（对抗批次） | 攻击场景 53→宪法 44 | 挖干 |
| K-05(F101) | 规则与裁定体系 | Owner 门 | 全链 | docs/01_policies_and_standards/rules/（86 trae_*.yaml） | 事件（裁定登记） | 议题→ruling_registry 原子 | 挖干 |
| K-06(F102) | 审计体系 | 全链 | 报告 | src/zephyr/gov_audit/ | 定时（Merkle 小时链） | 全链→审计/语义/供应链 | 挖干 |
| K-07(F103) | 代码质量与克隆守卫 | F98 | 施工 | gov_code_quality/、clone_guard/ | 事件（写前预查） | 代码→克隆判定 | 挖干 |
| K-08(F104) | 会话并发治理 | — | 提交链 | session_concurrency.py；git_commit.py | 事件（claim/release） | 会话→锁/worktree 四证 | 挖干 |
| K-09(F105) | 密钥治理 | — | 全链 | shared/security/secrets.py；SECRETS.md | 事件（调用时三 gate） | 密钥→唯一通道 | 挖干(信任绑定待裁) |
| K-10(F106) | 术语三层翻译体系 | 模块册 | 生成器 | module_translation_registry.yaml（7686 条） | 机生+gate | 三册→i18n loader | 挖干(UNKNOWN 26.9% 注记) |
| K-11(F107) | 回滚恢复 | F84 | 全链 | infrastructure/rollback/ | 事件 | 故障→双轨 checkpoint 四级回滚 | 挖干 |
| K-12(F108) | 人机门位 | REG-RISK-TIER-001 | 全链门位 | risk_tier_registry.yaml | 事件（high 域拦截） | 域风险→四类 Owner 门 | 挖干 |
| K-13(F109) | 注册表族治理 | 全注册表 | 全链 | docs/registry_of_registries.yaml（77 册） | 定时（一致性审计） | 各册→ROOR 账本 | 挖干 |
| K-14(F110) | 契约冻结与错误码 | — | 全链 | shared/contracts/freeze_manifest.yaml（38 契约+error_code 788） | 静态册+gate | 契约→全链引用 | 挖干 |
| K-15(F124) | 状态词表册生命周期 | GATE-VOCAB | K 段 | REG-STATE-VOCAB-001（门在拦、册无主） | 未建 | 状态词→受控词表 | 盲区(P0 新号) |
| K-16(F128) | data_security 数据安全 | K 段 | A 段数据面 | src/zephyr/data_security/（10 py：masking/access_auditor） | 未挖 | 数据→脱敏/访问审计 | 盲区(P1 新号) |

### L 段·前端报告链

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|----------|------|
| L-01(F111) | Panel 仪表盘 | F112 | Owner 值守 | frontend/dashboard/app_panel.py | 常驻 | 台账→主面板 | 挖干(退役时点待裁) |
| L-02(F112) | API server | 全台账 | F111 | frontend/dashboard/api_server.py | 常驻 | 全台账→REST | 挖干(AI 层两新页三层三断点=红点) |
| L-03(F113) | 可视化渲染器 | F112 | F111 | graph_view_renderer.py 等 5 件 | 事件 | 图数据→五视图 | 挖干 |
| L-04(F114) | 通知路由 | F81 | F111 | frontend/notification_router.py | 事件 | 告警→前端分发 | 挖干 |
| L-05(F115) | 报告生成 | F102/F50 | Owner | src/zephyr/reporting/（attribution/ashare_performance_audit） | 定时/手动 | 归因/审计→三类报告 | 存疑(M6 补挖) |

### M 段·全局横切段

| 环节id | 名称 | 上游 | 下游 | 代码入口 | 自动化态 | 数据进出 | 三态 |
|--------|------|------|------|----------|----------|------|------|
| M-01(F116) | SOP 方法论族 | — | 全链方法论 | docs/01_policies_and_standards/sop/（12 目录） | 静态 | — | 挖干 |
| M-02(F117) | 文档资产体系 | — | 治理面 | directory_registry.yaml；unified-asset-index.yaml（+B-14 五册并入） | 机生 | 全文档→索引 | 挖干 |
| M-03(F118) | 四盘存储地图 | — | F08/F09 | storage_map.md（INFRA-STORE-003） | 静态 | — | 挖干 |
| M-04(F119) | 双引擎自动化总计划 | F83 | 排班 | cmd_ledger/automation_master_plan.md | 静态（L0-L6 唯一真源） | — | 挖干 |
| M-05(F120) | 业务层四轴+底板骨架 | — | F72-F75 | 20260917_fullauto_skeleton_v1.md | **无**（design，工单队列在案） | — | 存疑(design) |
| M-06(F121) | 研究性三域+研究域 | — | 待裁 | digital_twin/cross_asset/execution_simulation/research/ | **无**（M0 待裁挂起） | — | 存疑(design Owner 门) |
| M-07(F122) | 管线路由 M1-M11 | — | Agent 编排 | blueprint_routing.yaml(30 条)、pipeline_orchestrator.py | 事件 | 任务→三层编排 | 存疑(M4/M5 边界) |

## §3 P0 断链清单（上游在/下游断·消费者缺失·空壳级）

| # | 环节 | 断链描述 | 证据锚点 | 态 |
|---|------|----------|----------|----|
| 1 | A-04(F04) | 清洗三引擎零接线：跨源校验/回补检查/AI 判净建成未接 F01→F06 主链 | 总册 §二红叉位；M1 在案 | 断链 |
| 2 | F-04(F62) | 合规门零注入：ReportGate 码成闸空，先报告后交易铁律无注入面 | M7 在案"零注入=P0 接线前置"；broker_ack 人工回填 | 断链 |
| 3 | I-07(F82) | order_daemon 建成未接线：夜班订单常驻缺触发 | 件在 src/zephyr/ai_layer/scheduling/order_daemon.py；M5 在案 | 断链 |
| 4 | H-01(F72) | SimBridge 09-24 静默断链嫌疑：sch_sim_bridge_execute 产物断供 | 总册 F72 注记；M5 在案 | 存疑(嫌疑) |
| 5 | H-02(F73) | A/B 联赛晋升判据执行器未写：champion/challenger 无执行体 | 总册 F73 design；automation 骨架 §7 | 断链(未施工) |
| 6 | A-02(F02) | 数据源接入工段串接空地：发现→报批→建表→验收→路由 SOP 无流水线承载 | 总册 F02 partial"工段③最大空地" | 断链(人工串接) |
| 7 | B-15(F27) | E8 组装未闭环：sleeve 落库+再平衡调度+TDM 对接三缺 | FAC-E8 build_status=partial；总册 F27 | 断链(P0) |
| 8 | B-16(F28) | E9 实盘归因未闭环：IS 分解时间戳 FIELD-GAP 未落+影子组合未建→FL1 回灌腿弱 | MOD-PF-007 partial；总册 F28 | 断链(P0) |
| 9 | C-01/C-02(F30/F31) | L9 两族源线登记态无消费：37 个 TDM 节点 module_ref=null（含 L9 段头） | 本轮实跑 null=37（yaml 字面口径）；定版卷 38→AGG 翻绿 | 无消费 |
| 10 | A 段 TI 派生链 | 技术指标分钟派生 09-21 起梯次停产，回填主跑中（~20-25h） | 底册 L-B：full_refresh 三杀+死信回灌必败根因 | 回填中(黄) |
| 11 | E-06(F58) | 执行成本反馈未闭环：G4 增长批回写选型缺 | 总册 F58 partial | 断链 |
| 12 | J-07(F92) | 原问题账本 entry_count=0 空转：PG 三表建成零入量 | 总册 F92 注记 | 无消费 |
| 13 | L-02(F112) | 前端 AI 层两新页三层三断点 | 总册 F112 注记=红 | 断链 |
| 14 | K 面 | 40 册 ROOR 登记面 REG 号批注欠账（环节在、册内未点名=机检不可达） | 定版卷 §三 | 欠账 |
| 15 | GOMAP 面 | suspect_orphans=94/446 模块未归 wired | config/governance_operations_map.yaml:11-15（机生 2026-10-01） | 待挖 |
| 16 | L-F T5 | 折入机制 DB 哈希停 09-30 21:56，10-02 死线在途（他队 G2） | 底册 L-F/CEF_mine | 在途 |
| 17 | A-13/A-14/K-15(F123/F125/F124) | 三 P0 新号仅有定位无施工（迁移通道/数据治理本体/状态词表） | 定版卷 §二 | 未施工 |

已翻绿（原红叉位复测）：F20 事件接线（scheduler.py:537-544）、F26 E7 前哨（MOD-BT-225=paper_outpost.py）、F34 L9-AGG（module_ref 非 null）、F74 转正汇总器（MOD-BT-199 实件+事件+API）——**4/7 翻绿，3/7 仍断**（#1/#2/#3）。

## §4 口径漂移登记（两说并记）

| # | 漂移 | 说法甲 | 说法乙 | 处置建议 |
|---|------|--------|--------|----------|
| 1 | TDM 节点数 | 138（00_skeleton_fullflow.md:33/146、09_link_skeletons.md:26/748 共 4 处旧数） | **182**（本轮实跑 grep，定版卷同） | 旧 4 处过期数待刷 |
| 2 | entry 流节点数 | 132（总册 00_全环节总册.md:73） | **128**（grep TDM-E- 前缀；132=128+4 crypto 混计） | 计数口径加 market 过滤 |
| 3 | ROOR 册数 | summary.total_registries=**76**（registry_of_registries.yaml:881） | grep registry_id=**77**（REG-METAQ-001 双计/新增未刷） | 刷 summary=77（注册表面 Owner 门） |
| 4 | src 顶层包数 | 56（总册 :12） | **57**（本轮实跑） | 以实跑为准，56 为过期数 |
| 5 | 模块册条目 | 7686（总册 regex 口径） | 7776（M0 册 safe_load 口径） | 以 yaml.safe_load 为准；UNKNOWN 域 ~27-30% 待收编 |
| 6 | TDM 交叉轴 | 16 表（宪法 AGENTS §8"业务资产库 16 表挂交叉轴"） | 13 轴（decision_map.py:100 _XREF_SPECS declared） | M1/M3 深挖确认口径 |
| 7 | SOP 族数 | 九族（AGENTS §6） | 12 目录（总册 F116 实测 11+1） | 沿用 M0 册指认 |
| 8 | **TDM null 节点**（新） | 字面 null 38（定版卷 09-27）/37（本轮） | yaml.safe_load 空引用面 59（含 LROOT/段头 22 个空串结构节点，本轮机读） | null 三口径（字面/机读/含结构节点）须在生成器工单定一 |
| 9 | **环节状态**（新） | 总册 09-26：F26/F34/F74=missing、F20=partial（4 红叉位） | 本轮实查：F26=MOD-BT-225 built、F34=AGG 已接线、F74=MOD-BT-199 895 行、F20=事件沿已挂 | **状态漂移**：工厂图/代码已演进，总册未回写；本册按实查翻绿并留证 |
| 10 | alignment_checklist 性质（新） | 任务口径"对齐键=module_id/step_id，step 即环节" | 该文件实为三层对齐**规则册**（无逐环节行）；环节键真源=TDM node_id+depgraph module_id | 检索环节以 TDM/depgraph 为准，checklist 供规则 |
| 11 | 122 骨架位置（新） | 任务线索指向 docs/_working/total_circulation_night/ | 真身在 docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md（total_circulation_night/ 无"环节/122"字样） | 线索勘误登记 |
| 12 | 链路面健康时差（新） | 总册 F01 数据采集 built（无时点限定） | 底册 10-01：TI 派生链⚖️回填中、J 腿 dry-run 留观、tdx 退役留观 | 以底册链路面为最新时点态 |

## §5 与 122 环节旧骨架（F01-F122/13 段）的增量对照

**编号增量：+10（F123-F132，定版卷 §二裁定，尚未落总册正文——落笔=裁-5 改写授权，Owner 门）**

| 新号 | 对象 | 段归属 | 优先 | 定版理由锚点 |
|------|------|--------|------|--------------|
| F123 | B-9 迁移通道（REG-MIGRATION-001） | A | P0 | 定版卷 §二 B-9；册本体已在 HEAD，13 条 pending 退役议题=Owner 门 |
| F124 | B-12 状态词表（REG-STATE-VOCAB-001） | K | P0 | GATE-VOCAB 实拦无主 |
| F125 | data_governance（21 py） | A/K 交界 | P0 | 数据治理本体 |
| F126 | B-7 字段字典（REG-FLD-001，8280 行） | A/K 交界 | P1 | schema v2.0 治理面 |
| F127 | data_eng（16 py） | A | P1 | 与 F08 冷储交叠=勘误点 |
| F128 | data_security（10 py） | K | P1 | 与 F88/F105 异域 |
| F129 | ml_train（43 py） | B/J 交界 | P1 | F19 仅基线对台 |
| F130 | ml_serve（11 py） | J | P1 | 与 F89 分界=数值 ML vs LLM |
| F131 | nlp（7 py） | C | P2 | 文本情报处理线 |
| F132 | infra_ops（6 py） | I | P1 | 运维工程域 |

**并入增量（18 行零新号，定版卷 §二）**：state_matrix→F38、portfolio_plan→F48、REG-TECHNICAL-INDICATOR/PAT→F52、REG-EXA→F55、REG-SEAT/EVT→F30、REG-MAC→F38、REG-DATAFLOW→F11、REG-ARCH-ISSUE/gov_rule 域→F101、REG-INTF→F110、REG-TASK-META→F83、REG-TEMPLATE 等 5 册→F117、CROSS-002→F07、CATALOG-001→F109、SM-001→F110、alt_data→F31、market_data→F03/F10、intelligence→F96。

**状态增量（翻绿 4，§3 末注）**：F20（partial→事件接线）、F26（missing→MOD-BT-225）、F34（missing→AGG 接线）、F74（missing→MOD-BT-199）。另：F26/F74 的翻绿使"H 段全链唯一人工门"从缺位变为**有门无拍板流量**态（advisory 事件链在、Owner decide 待实测流量）。

**退役增量（链路面，非环节号）**：tdx 五任务退役留观、resample 判死（kline_sector_880 全表仅 1d）——板块分钟生产者收敛为 internal_eqw（10-09 接产）；J 腿 dry-run 留观（底册 L-A 裁定甲）。**环节级零退役**（F01-F122 无废号）。

**改名增量**：零已执行；在册待改=D23"作战预案引擎"→"每日作战计划引擎（Game Plan Engine）"（TDM yaml:36-38 正名登记，未执行）。

**Owner 门挂起（不计号不入表）**：knowledge 域↔F93 边界（裁-6）、infra_runtime 域↔F71 同物性（裁-6）、ROOR summary 76→77（裁-1 族）、F123 册内 13 条 pending 退役议题。

## §6 域覆盖核对（src/zephyr 57 目录 ↔ 132 环节）

实扫 57 目录（§0.2）全部有宿主环节：显性映射见 §2 各行；定版卷判定"语义已覆盖"4 域（experiment_tracking→G-04、red_blue_validator→K-04、signal_quality→D-04、strategy_factory→B 段）+13 域并入/新号（§5）。**未匹配残留=2 个 Owner 门域**（knowledge、infra_runtime）挂 §5 末行，无盲目录。
