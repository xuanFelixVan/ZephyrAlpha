---
ttl: task_bound
title: F38 L1 大盘总闸+六传感器——环节册（TD-A 前半）
session: st-ailayer-fullflow-td-a
creation_token: f38-l1-gate-book-tda-20260925
date: 2026-09-25
status: mined
---

# F38 L1 大盘总闸+六传感器——环节册

> **一句话**：全流唯一开闸裁定点（materiality=critical）——消费 RegimeSnapshot 概率当谨慎度、查六段情绪预算带、受日级水温微调，输出当日总仓位上限+六段状态+策略路由三件套，一次判定 broadcast 全图；自己不算宏观。
> 节点组：TDM-E-L1（gate）+ S0 宏观 / S0-1 新闻情绪 / S1 指数 / S2 内部结构 / S3 赚钱效应 / S4 波动率 / S5 日级条件 / AGG 市场状态判定，共 9 节点。总册三态标 built｜P1｜T2。

## 一、环节定义与边界

- **供料方**：F33 L9 三快照（DS-150 指数/DS-082 涨停池/DS-098 宏观/DS-059/DS-107/DS-108）；新闻流水线（S0-1，数据底座不进图）。
- **消费方**：L0（计划参考，无裁定权）、L1-AGG→全流（六段状态）、C1（预算带）、L2-05-1（月级封顶）、L3-06（环境开关查六段表）、daily_decision_orchestrator S2（regime_snapshot_history PIT 读）、X 流 S2（情绪退潮加权，地图：3405 行）。

## 二、判定输入 / 输出

| 节点 | 判定输入 | 判定输出 |
|------|---------|---------|
| L1 gate | RegimeSnapshot 7 态概率（越分裂越谨慎）+六段情绪预算带+日级水温微调 | 当日总仓位上限；叠加波动率目标化系数（vol_target_allocator，MOD-BT-082，凯利简版已建成；Phase 2 完整凯利待 E 分布预测） |
| S1 | 均线排列与位置（MA20/MA60、距 60 日高点） | 指数趋势分 -2~+2（破 MA20 减一档/破 MA60 减两档） |
| S2 | 涨停/跌停家数、炸板率、连板梯队 | 广度参与度分（涨跌停比>3 且炸板率<30%=强势；5 板断崖到 2 板=退潮预警） |
| S3 | 昨日涨停今日溢价、晋级率 | 投机情绪分（溢价>2% 且晋级率>50%=健康；连续两天负溢价=退潮确认；短线最领先） |
| S4 | 双路径：期权 IV 曲面主路径（ATM 筛子 \|abs(delta)-0.5\|<0.15，CBOE 简化 VIX→250 日分位）+下行半偏差合成 VIX 后备 | vix_pct∈[0,1]；两路均败→None→消费侧回退 vol_pct（C1 不退化） |
| S0 | 四维：货币（Shibor 骤升）/流动性（两融连降）/海外（纳指跌>2%）/政策（人工录入） | 宏观支撑/压制分 |
| S0-1 | 新闻采集→本地推理池+SFT 情感模型→实体链接 | 市场级+板块级情绪读数（喂 S0 与 L2-09） |
| S5 | 当日 11 信号环比三值计票（9:35 首算，盘中可更新，唯一盘中可变 L1 输入） | S0-S4 五档水温（可用信号<6→tier=None fail-closed INSUFFICIENT_DATA） |
| AGG | 双轴：宏观 RegimeSnapshot 概率（月级 7 态）×情绪六段分布（周级）；日级水温受月/周档位封顶 | 三件套：预算带（给 C1）+六段状态（给全流）+策略路由（哪些 sleeve 今天开）；指向分裂=熵高"就低不就高"仲裁（D90：听弱的降一档机械执行，废除人工接管） |

## 三、判定用离散状态集合（全组最密，7 套）

| 状态集 | 离散值与阈值 | 真源 file:line | 备注 |
|--------|-------------|---------------|------|
| 宏观 7 态 | r1/r2/r3/r4（HMM，裁定#304 跨季锚定：r4 槽=训练窗负斜率、r1-r3=波动率升序）+ r10/r11/r12（CRISIS/RECOVERY/BREAKOUT overlay） | regime_detector.py:107 `REGIME_STATES` | r4/r10/r1 无稳定方向信息——按风险分档口径读，方向判别归因子层 |
| 锚定风险四档 | 低(r3)/中(r2)/中高(r1)/高(r4)，vol_pct 锚定阈值 0.30/0.60/0.80，纯锚定零拟合 | anchored_state_machine.py:77,101；表 c1_backtest.regime_state_anchored:84 | **AGG 消费切换终批 2026-09-23 Owner production 翻转**：状态输入源已切 regime_state_anchored；夜批连续零缺勤+当日更新判据①机械复核通过 |
| 情绪六段（列轴） | capitulation/accumulation/ignition/expansion/euphoria/distribution | 地图 state_matrix 列轴；environment_switch.py:40 六段封闭集 | 与 SentimentPhase 五阶段（冰点/反核/主升/疯狂/退潮）的归并由调用方负责（accumulation+ignition↔反核、ignition/expansion↔主升） |
| 情绪五阶段 enum | FREEZING 冰点/STARTING 反核/FERMENTING 主升/CONSENSUS 疯狂/EBING 退潮 | sentiment_cycle.py:52-65 | PHASE_DISCIPLINE:575 每阶段 position_scale∈[0,1] 买卖纪律表 |
| 六段预算带 | capitulation 0-10%（只试错）/吸筹 30-50%/点火 50-70%/扩张 60-80%/亢奋封顶 30% 只卖不买 | 地图:3735 起；orchestrator 引 TDM-F-C1 注释值 | 全 proposed（机构+A 股多源收敛） |
| 日级水温五档 | S0_ICE 只看不动 → S4_HOT 当日可激进 | daily_condition_sensor.py:45-52 WaterTempTier | 11 信号三值(+1/0/-1)计票合成；昨日基数=0 环比按缺数防除零；net→五档映射单调闭区间确定 |
| 总暴露熔断曲线 | cap = 1 − 0.70×clamp((vol_pct−0.30)/0.70, 0, 1) | 地图 L1-AGG 注（2026-09-23 终批） | 连续灰度非离散，唯一灰度插值件（D108"程度用灰度插值"先例） |

**fail-closed 铁律（R-055a 2026-09-18，方向=加严）**：RiskSignal 缺供数（整包缺/params 空壳/主腿 #1 NULL）不再取 1.0（原 fail-open 把"没数"读成"没风险"），改落地板值 0.30+risk_signal_source 溯源（neutral_fail_closed 可与 13 参数全正常区分）；主腿未报平静时不得清零覆盖层危机概率。实测：危机断一腿 Shrinkage 0.255→0.255（改前放量 3.137 倍）。
**量×轮动二维状态机（D90）**：成交额 250 日滚动分位<25%=存量博弈（小盘题材加权/主线降权/持仓≤2-3 天）；>60%=主线放行；轮动强度>80% 分位=电风扇市=无主线不推大板块。二值权限门滞回：进段连续 2 日隶属度>60%、退出<40%。

## 四、子模块清单与实件校验

9/9 module_ref 在盘（零缺件）：regime_detector.py（MOD-REGIME-001，2026-09-15 ALGO_FLOW 外迁至 docs/03_modules/_domain_regime/algo_flow/regime_detector.yaml）/ anchored_state_machine.py（v2 定稿=波动率风险四档）/ index_sensor / limit_up_followthrough / lhb_premium_analyzer（DEDUP 抽至 core/analysis_utils）/ synthetic_vix（SVX-1-P0 治理：delta 列反解+池空必 WARNING，区分"进料口事故"与"当日确无平值档"）/ policy_expectation_analyzer / news_sentiment_analyzer / daily_condition_sensor。

## 五、触发链与当日闭环证据

- **regime 刷新**：daily_kline SUCCESS 事件链（dloop 序：regime 刷新→判定台账结算/验证→pf_alloc→模拟盘日件→drain→编排器末棒）；新鲜度消费方口径 D1：滞后>1 交易日=缺（供给方阈值 2026-09-21 Owner 批对齐为 1，原 3 错位是 09-15~09-18 断供根因，对账总账 §4）。
- **S5 水温**：9:35 首算，盘中可更新（唯一盘中可变 L1 输入）。
- **orchestrator S2**：读 regime 昨收 PIT（regime_snapshot_history；r1/r2 不路由）；daily_gate_snapshot（MOD-BT-213）采 L1 门态一行 JSON（缺席=absent 三态，不伪造）。
- AGG 判据锚定消费切换有实证批号（regime_state_anchored 表，tasks.yaml:648 引用）。

## 六、验证欠账清单（命中 9 件：P0×2 + 传感器×7）

| object_id | 对象 | 状态 | 欠什么/已有 |
|-----------|------|------|------------|
| **BT-P0-001** | L1 gate（生死线三件套之一） | untested；plan **已冻结** 2026-09-12（agg_discrimination；每档≥20 触发且总≥30；p<0.05 且高低档差≥2.0%→valid，方向反→noise；frozen_by=st-backtest-20260912） | 判据冻结、**考卷未考**——待批次决策点开跑 |
| **BT-P0-002** | L1-AGG（生死线三件套之一） | untested；plan 冻结+裁定#230 修订（判据对象 fwd20 收益→fwd20 maxdd 风险判别） | **全组唯一已跑验证的 P0**：first_valid_run=VAL-P0-20260914-004029-002；verdict 正式翻转未回填（confidence 仍 untested） |
| BT-P1-001 | S1 指数 | **valid** | — |
| BT-P1-002 | S2 内部结构 | untested | 阈值未预注册 |
| BT-P1-003 | S3 赚钱效应 | untested | 同上 |
| BT-P1-004 | S4 波动率 | untested | 同上 |
| BT-P1-005 | S0 宏观 | **pending** | 政策维人工录入是半自动件 |
| BT-P1-006 | S0-1 新闻情绪 | **valid** | — |
| BT-P1-007 | S5 日级条件 | untested | 同上 |

## 七、堵点与病灶

1. **BT-P0-001 冻结未考**：总闸谨慎度分档区分度从未出 verdict——谨慎度数值轴（全组最高风险权重件）仍在"判据未验证"状态运行｜修法：按已冻结 plan 直接开考（数据与判据俱在，零新施工）｜0.5 天｜可修。
2. **BT-P0-002 verdict 回填欠账**：已有 first_valid_run 但 confidence 未翻转｜修法：runner 台账行核查后回填（S7 场景：追溯更新置信度）｜0.5 天｜可修。
3. **六段×五阶段双词汇**：environment_switch 只认六段封闭集、sentiment_cycle 输出五阶段，归并靠调用方——无单一映射真源函数时易漂移（framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE=六段映射唯一真源，2026-09-25 附录C 已切，orchestrator 依赖它）｜修法：把六段↔五阶段↔regime 三方映射钉进唯一真源件｜1 天｜可修。
4. **S0 政策维人工录入**：半自动传感器的最后人工口——自动化替代属 KS 组另类源线（F31 交界），不在本册施工。
5. **六段预算带全 proposed**：数值轴从未回测（C1 域交界，本册只登记）。

## 八、三态自审

**挖干可施工**（状态机血肉七套全数落码实证；两件 P0 欠账路径清晰：001 开考、002 回填，均零新施工）。

## 九、复核命令

```bash
grep -n "REGIME_STATES" src/zephyr/regime/core/regime_detector.py        # :107 7态
sed -n '77,110p' src/zephyr/regime/core/anchored_state_machine.py        # 四档锚定
sed -n '45,60p' src/zephyr/signal_ashare/core/daily_condition_sensor.py  # 水温五档
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml',encoding='utf-8'));print([o['object_id'] for o in d['objects'] if o['object_id'] in ('BT-P0-001','BT-P0-002')])"
```
