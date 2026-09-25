---
ttl: task_bound
title: TD-A 前半总览——TDM 消费端 F37-F42 六环节（entry L0-L4 + position P1）
session: st-ailayer-fullflow-td-a
creation_token: tda-front-overview-20260925
date: 2026-09-25
status: mined
---

# TD-A 前半总览（F37-F42）

> **一句话**：六环节全部"实件 built"——77/77 module_ref 在盘零缺件、当日闭环触发链可证；真正的矿是**验证欠账（98 件 backlog 关联，80 untested，P0 生死线三件套两件未考）+ 6 处判据-码面离散状态集差异 + P1 体检编排悬空**。分工册 TD 组细则（每环节判定输入/输出/离散状态集合/验证欠账清单）已逐册兑现。
> TD-B（F43-F52：P2/P3/S1/S2/R1/C1-C3/L9/币圈）另册；本目录 00_overview.md 留给 TD-B 或合并时改建。

## 一、册清单与三态（每册一行）

| 册 | 环节 | 节点数 | 三态结论（一行） |
|----|------|--------|-----------------|
| f37_l0_premarket_plan.md | F37 L0 盘前作战计划 | 5 | **挖干可施工**——5/5 实件在盘；欠账=6 件 backlog 全 plan=None（阈值预注册是瓶颈工序）+两拍板体（warroom/orchestrator）主从未钉死 |
| f38_l1_market_gate.md | F38 L1 大盘总闸+六传感器 | 9 | **挖干可施工**——状态机血肉七套全落码；两件 P0：BT-P0-001 冻结未考（可径开考）、BT-P0-002 有 first_valid_run 待回填 verdict；六段预算带全 proposed |
| f39_l2_sector_selection.md | F39 L2 板块选择 | 32 | **挖干可施工**——唯一缺口节点 L2-05（pending_gate，水温响应枢纽无专件）；两处判据-码面差异（生命周期四段/缩量维）；29 件验证零运行；G05 admission_gate 未激活 |
| f40_l3_stock_selection.md | F40 L3 个股选择 | 25 | **挖干可施工**——两处判据-码面差异（六顺位无枚举/筹码"获利盘"语义 trial 挂起）+两处登记欠账（M-41 池持久化/聚合器 MOD id）；25 件验证零运行；6/8 sleeve 挂载 proposed 无 evidence |
| f41_l4_execution.md | F41 L4 买卖执行（P0） | 15 | **挖干可施工**——验证状态全组最佳（16 valid）；三件结构性欠账：订单"九态"判据 vs 码面 7 态、trade_log 归因字段缺（分桶考死穴）、L4-14 反馈环最后一米断链（节点注自认）；EX 组交界引用 M7 不重挖 |
| f42_p1_position_checkup.md | F42 P1 持仓体检 | 7 | **待挖（窄口）**——状态机血肉与 7 件验证欠账已挖干，但体检五件日循环编排入口零命中（件 built 链未证）；裁决中心已证经 pf_alloc 装配体接入（分配语义非体检语义）；补证后翻挖干 |

## 二、全局发现（供总筹回填与派工）

### 2.1 实件存在性（绿）
- 本半 96 节点中 77 个唯一 module_ref **全部在盘**（ls 批量校验 2026-09-25）；module_ref=null 的判定节点仅 TDM-E-L2-05（red_reason=pending_gate）——全半唯一真缺口节点。

### 2.2 验证欠账结构（REG-BTB 命中 98 件：TD-A 六环节本体约 90 + LROOT/PFLOW 根 4 + 币圈镜像 4）
- 分布：**untested 80 / valid 16 / pending 2**（conf 口径）；plan 冻结者仅 6 件（BT-P0-001/002、BT-P2-045/046、BT-P0-003、cross）。
- **P0 生死线三件套**：BT-P0-001 总闸（frozen 2026-09-12，考卷未考）、BT-P0-002 AGG（frozen+裁定#230 修订，first_valid_run=VAL-P0-20260914-004029-002，全组唯一已跑，verdict 回填欠账）、BT-P0-003 成本模型（frozen，pending）。
- 病根不是"跑不动"是"阈值未预注册"：80 件 plan_note 同文="验收阈值未预注册——批次决策点填写并冻结前禁跑（SOP-B 护栏③）"。**瓶颈工序=批量冻结**：传感器类走 sensor_monotonicity、聚合类走 agg_discrimination（五法注册表俱在）、执行类走 exec_quality 土规 20/40bp——可按 BT-P0-001 夜班自裁先例批量推进。
- 异常态：BT-P2-047~053（L4 家族 7 件）confidence=valid 但 plan=None——标记-判据不对齐，须核 c1_backtest.node_verdict 台账。

### 2.3 判定用离散状态机血肉（已挖实，六环节共 25+ 套状态集，各册 §三 有 file:line）
代表集：宏观 7 态（r1-r4+r10/r11/r12）/锚定风险四档（0.30/0.60/80，AGG 2026-09-23 production 翻转）/情绪六段列轴与五阶段 enum（双词汇归并由调用方——漂移风险点）/水温 S0-S4/轮动五分类/生态三态/RRG 四象限/回踩 ABC（取最弱档）/环境开关六段×四开关/订单 7 态+VALID_TRANSITIONS/持仓 7 态+灰度 4 阶段/存活三态/止损 7 触发类型×4 严重级×3 限额/裁决四意图。

### 2.4 判据-码面离散状态集差异清单（6 处，S4 场景欠账）
1. L4-10 订单"九态"（QMT 风格）vs 码面 OrderStatus 7 态——**唯一 P0 级**，缺券商态映射桥（EX/F53 交界）。
2. P1-01 持仓"六态" vs 码面 7 值（含 NONE）——散文未更新。
3. P1-04 四类否决 vs 码面 7 触发类型（"时间止损/事件禁区"无码面对应；码面多出竞价/分时/支撑破位）。
4. P1-06 "五动作+人工确认" vs IntendedAction 四意图。
5. L3-05 六顺位（妖>龙>中军>核心>趋势>跟风）无码面枚举（码面=三类置信分）。
6. L2-08 生命周期四段（启动/发酵/高潮/熄火）无码面枚举（码面=持续分+市场宽度态）。

### 2.5 当日闭环触发链（已证）
- **16:45 dloop_post**（daily_loop_master_switch，Owner 2026-09-21 批）：数据就绪门（fail-closed）→regime 新鲜度体检→warroom scenario_plan→晨间预案→次日概率→pf_alloc 分配（内含裁决中心装配体）。
- **daily_kline SUCCESS 事件链末棒**：daily_decision_orchestrator（MOD-BT-214）拍板 c1_backtest.decision_daily=当日唯一放行凭证（v1 留痕+仪表盘零实盘变更，裁定#305）。
- **板块两槽**：sector_close_final 15:10 定格 / sector_pre_open 09:15 消费（总闸=disabled 文件）；旁路 SectorSnapshot 16:40 + IntradayFundFlow 五时点。
- **盘中**：S5 水温 9:35 首算；L3-11 竞价 9:26-9:28/涨速 9:30-10:30；L4 执行窗 14:50-15:00。
- 断点：G05 选股引擎 admission_gate 未激活；P1 体检五件无编排棒（F42 堵点 1）。

### 2.6 矿脉增补（分工册未列，回填总筹）
1. **c1_backtest.decision_daily"无快照行=无新开仓令"**——全流通当日闭环的机械锚点，T1 晨判拍板体（MOD-BT-214，experimental）的转正/观察属 PR 组交界。
2. **daily_gate_snapshot（MOD-BT-213）五层门采集横切件**——L1-L5 门态一行 JSON，是本半各层消费面的只读采集真源。
3. **framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE=六段映射唯一真源**（2026-09-25 附录C 切源）——双词汇归并问题的现成解法挂点。
4. **六指数分位数回归板块优先序**（UP-4，DAL-SECTOR-DIST，MOD-PA-023，2026-09-20 接线）——L2-01 的第二排序通道。
5. **known_data_gaps bt_trade_log_attribution_fields_missing**——卡 L4-05/046 分桶考的数据面死穴，建议列 M1/BT 补挖波。

## 三、待裁项（一行一案，供总筹）
1. L4-05/046 分桶考：trade_log 归因字段落地前按"全量代理口径+披露受限"出数，还是冻结待字段？（现 plan 已按代理口径冻结——建议维持，字段落地后复核）。
2. L2-08/L3-05 判据-码面差异：补码面枚举（施工）还是 S4 改判据（D 裁定）？（建议：六顺位补枚举、四段改判据为持续分区间——各自成本最低路径）。
3. P1 体检棒缺位：立施工单挂 dloop（建议），总筹派工定序。
4. BT-P3-007~012（P1 族）验证优先级提级：止损引擎实为 P0 消费件（F59 交界）——建议晨报列 Owner。

## 四、复核路径（10 分钟）
```bash
ls docs/_working/fullflow_mining/02_tdm_decision/                       # 7 册在盘
python - <<'EOF'  # 实件校验复跑
import yaml,os
d=yaml.safe_load(open('config/trading_decision_map.yaml',encoding='utf-8'))
T={'entry_flow':['L0','L1','L2','L3','L4','LROOT'],'position_flow':['P1','PFLOW']}
miss=[n['module_ref'] for n in d['nodes'] if n.get('flow') in T and n.get('layer') in T[n.get('flow')] and n.get('module_ref') and not os.path.isfile(n['module_ref'])]
print('missing:',miss)
EOF
grep -c "untested" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml   # 欠账口径复核
```
