---
ttl: task_bound
title: F39 L2 板块选择——环节册（TD-A 前半）
session: st-ailayer-fullflow-td-a
creation_token: f39-l2-sector-book-tda-20260925
date: 2026-09-25
status: mined
---

# F39 L2 板块选择——环节册

> **一句话**：板块层总枢纽——10 子环节（强度综合/轮动/调整进度/市场状态/水温响应/传导/回踩/生命周期/催化剂/补涨比价）产出当日板块候选池（3-5 个主攻板块）排序喂 L3。
> 节点组：TDM-E-L2 + 01 组六节点 + 02~10 组，共 32 节点。总册三态标 built｜P1｜T4。红节点 2 处：TDM-E-L2、L2-01、L2-04（red_reason=structural 汇聚容器）、**L2-05（red_reason=pending_gate，module_ref=null——全层唯一缺口节点）**。

## 一、环节定义与边界

- **供料方**：F38 L1（六段/水温/市场级调节）；DS-059 板块行情、DS-170 板块指数、DS-082 涨停池、DS-181/DS-186 资金流、DS-107 事件、DS-224/225 产业链图谱。
- **消费方**：L3（只传"板块强度调节分+龙头定位"两个字段，层级隔离防越权——L3 不得直接引用板块买卖结论）；daily_gate_snapshot L2 门（水温桥+三原料）；P1-04（板块退潮否决）。

## 二、判定输入 / 输出

| 子环节 | 判定输入 | 判定输出 |
|--------|---------|---------|
| 01 强度综合 | 四路子分（结构/动量活跃/多周期/资金流各 0-100）等权 0.25 + 市场级调节 ±10 | 板块总分 clamp[0,100]，**前 15% 进候选池**；UP-4 叠加通道：六指数分位数回归（PIT q05/q50/q95）按预测收益-风险比出优先序（DAL-SECTOR-DIST，MOD-PA-023，2026-09-20 final3 P5） |
| 01-1~4 四路子分 | 涨停占比>8%/梯队完整/趋势；成交额占比+环比；q20/q5/q3 谁主导；3 日净流入+大单净额 | 各 0-100 子分；q3 主导=刚点火、q20 主导=谨慎追 |
| 01-5 市场级调节 | 轮动五分类 | 主线态头部 +10% / 派发态全体 −15%（外部预测分布 NaN/Inf 拒收 fail-closed，rpt_d04） |
| 02 轮动 | 板块指数与资金移动方向 | 接棒榜单/撤离区；02-2 单板块见顶预警三信号命中 2 个=降级 |
| 03 调整进度 | 回撤天数+回撤深度+扩散指标 | 三维进度（时间 0.4+回撤 0.3+扩散 0.3）**≥80% LATE 才放行动作门控**；**量能缩量维=设计语言待扩展** |
| 04 板块级市场状态 | 梯队连击/Top2 集中度/高潮分 | 三态封闭判定（优先级 CLIMAX>MAINLINE_CLEAR>CHAOS）；04-2 虹吸：前 3 板块成交占比>40%→只做头部、其余候选池清空 |
| 05 水温响应 | L1 水温档 | 放行比例（水烫=全放行+门槛降一档；水冰=只放前 5%+门槛升一档）；05-2 三件套联动（权重×0.5~1.2 系数/门槛/象限过滤） |
| 06 传导 | 板块强度+龙头定位 | 封闭乘数：10 分→+15% / 6 分→+5% / <6 分→−10%（只调分不重排名）；三级放行门槛（板块>6/个股>5/日成交>2 亿，先 gate 后 weight）；龙头四定位 |
| 07 回踩 | Fib×量能×强度×时间窗 | **A/B/C 三级取最弱档**（_GRADE_ORDER worst）：A=满额优先建仓/B=半仓分批/C=观望或突破失败降级 |
| 08 生命周期 | 动量持续性+市场宽度 | 节点判据=启动/发酵/高潮/熄火四段（只做启动发酵；高潮只持有；熄火清仓）——**码面无四段枚举，见堵点 2** |
| 09 催化剂 | 政策/业绩/事件扫描+产业链图谱 | 有催化剂板块加权 20%；09-1 图谱传导（W3 交付：55 单测，24h 窗 800 新闻→图谱命中 10，5.5s）；09-2 冲击标的（W4：BFS 2 跳×置信 0.6 衰减，polarity ±0.15 死区外映射利好/利空；利空喂 L3-04 否决、冲击流喂 L0-02） |
| 10 补涨比价 | 同链条涨幅<20% 未涨股+产业链上下游 | 补涨候选（启动滞后 3-5 天，胜率低但位置安全） |

## 三、判定用离散状态集合

| 状态集 | 离散值与阈值 | 真源 file:line |
|--------|-------------|---------------|
| RRG 四象限 | LEADING 领先/WEAKENING 疲软/LAGGING 滞后/IMPROVING 改善（RS-Ratio×RS-Momentum 各 100 线） | sector_rrg.py:70-78 |
| 象限→信号映射 | BUY_CANDIDATE/WATCH_EARLY/HOLD_REDUCE/AVOID；强度调整 +0.05/+0.02/−0.03/−0.08 | sector_rrg.py:54-67 |
| 轮动五分类 | CONSENSUS_CLIMAX（HHI>0.30+普涨>0.70）/DISAGREEMENT_PULLBACK（集中>0.20+涨跌<0.40）/HEALTHY_MAINLINE（HHI<0.20+领涨连击≥3）/DISTRIBUTION_RISK（放量滞涨+集中>0.25）/NEUTRAL_MIXED 默认态 | sector_rotation_state.py:40-59 |
| 生态三态 | MAINLINE_CLEAR（连击≥2 且 Top2 集中度≥30%）/CLIMAX（高潮分≥90）/CHAOS；判定优先级 CLIMAX>MAINLINE>CHAOS（风险方向优先） | sector_ecology_judge.py:8,38-42（阈值全取自已锚定模块文档值零自创，标 proposed 待实盘标定） |
| 回踩三级 | A/B/C 四因子各 0-1 分加权，取最弱档定级 | sector_pullback.py:60-63,148-149 |
| 水温档响应 | S0-S4 → 放行比例/门槛升降/象限过滤三件套查表 | sector_gate.py（WaterTemp 响应侧；daily_condition_sensor 自认"本件输出可映射为其入参"） |
| 龙头四定位 | 龙头（榜首+最先涨停）/中军（跟涨大盘）/跟风（后涨小票）/中位股；定位决定止损宽度（龙头宽/跟风窄） | sector_leader.py（DEDUP 后共享原语） |
| 调整进度三档 | EARLY/MID/LATE（≥80% 放行门控）；量能维缺失 | sector_adjustment.py 节点注 |

## 四、子模块清单与实件校验

31 个 module_ref（30 节点+1 共享 sector_gate 重复挂两节点、sector_conduction/sector_analyzer/sector_pullback 各挂两节点）**全部在盘，零缺件**。编排件：data/sector_state_pipeline.py（纯编排层，算法全委托 sector_state_aggregator 纯函数）——kline_sector_880 70 日面板+limit_up_pool×sector_constituent+money_flow → c1_market.sector_state（rrg_quadrant/strength/net_inflow_pct/capital_score/watch_score）+ c1_market.sector_preference（preference_label/tilt/banned_quadrant）。

## 五、触发链与当日闭环证据

- **sector_close_final 15:10**：T 日定格态落库（schedule.yaml:258 特殊槽，总闸 data/runtime/sector_state_pipeline.disabled 即时生效）。
- **sector_pre_open 09:15**：T+1 消费=T 日定格复制+偏好重映射（SQL FINAL 按 stage='pre_open' 取行）。
- **旁路供给**：ZephyrAlpha_SectorSnapshot 16:40（Windows 任务，sector_constituent→snapshot）；ZephyrAlpha_IntradayFundFlow 10:05/11:05/13:35/14:35/15:05 五时点（collect_sector_fund_flow.py，M5 册实测 09-24 末班 0 退出码）。
- **消费接线**：daily_gate_snapshot.load_l2_admission 供 L2 门三原料；但 **admission_gate 放行判定不激活（三原料判定归 G05 选股引擎）——G05 未激活，gate_level 如实三态不伪造**（daily_gate_snapshot.py:18）。

## 六、验证欠账清单（命中 29 件，全 untested——全组零验证运行）

| object_id | 对象 | 状态 |
|-----------|------|------|
| BT-P1-008~013 | 01 组六节点（强度综合+四路子分+市场级调节） | untested，plan=None（013 testable=True 待冻结） |
| BT-P2-007 | L2 枢纽 | untested，testable=False（容器不单独考） |
| BT-P2-008~029 | 02~10 组 22 节点（轮动/调整/生态/水温/传导/回踩/生命周期/催化剂/补涨） | untested，plan=None；其中 016（L2-05 水温响应）module_ref=null 且 testable=False |

结构性欠账：等权 0.25 先验"待 IC 重校"（L2-01 节点注自认）；生态三态阈值 proposed 待实盘标定；**节点级验证元数据（last_validated_at）属 TDM v1.3 施工批未落地**（consumption_policy §3）。

## 七、堵点与病灶

1. **L2-05 枢纽 module_ref=null（pending_gate）**：水温→放行比例的"总开关"无专件；响应面三件套在 L2-05-2 sector_gate 有，但"比例总开关"语义（水冰只放前 5%）无实现锚｜修法：最小施工=sector_gate 增放行比例查表行（半天）；或把 L2-05 降格语义并入 05-2 并改图注｜本车道可修（先 D 裁定改注）。
2. **L2-08 判据-码面差异**：节点判据"四段生命周期（启动/发酵/高潮/熄火）"，码面 sector_momentum_persistence 输出 SectorPersistenceScore+MarketBreadthRegime，**无四段枚举**——四段动作映射（只做启动发酵/高潮不开新/熄火清仓）无承载件｜修法：a) 码面补四段分级函数（1 天）或 b) 改节点判据为持续分区间语义走 S4 场景（D 裁定+台账留痕）。
3. **G05 选股引擎 admission_gate 未激活**：L2 门三原料采集齐但放行判定悬空——板块候选池到 L3 的"闸"语义由谁承载未闭合｜修法：G05 施工批（PR/工程交界）或临时由 candidate_pool_aggregator 承载并在图注声明。
4. **L2-03 量能缩量维缺**：三维进度只有时间/回撤/扩散，节点散文的"缩量到高峰 1/3"未实现——调整近尾声判据缺最关键一维｜修法：补量能维（0.5 天，纯函数）。
5. **29 件零验证**：整层 untested 且 plan=None——按 BT-P0-001 先例批量推导冻结阈值是瓶颈工序｜修法：传感器类用 sensor_monotonicity 批量冻结｜1-2 天｜可修。

## 八、三态自审

**挖干可施工**（实件零缺+状态集全落码；两处判据-码面差异（L2-08 四段、L2-05 枢纽）已列修法，属小施工而非重挖）。

## 九、复核命令

```bash
sed -n '40,78p' src/zephyr/signal_ashare/sector/sector_rrg.py            # 四象限+映射
sed -n '40,59p' src/zephyr/signal_ashare/sector/sector_rotation_state.py # 五分类阈值
sed -n '8,42p' src/zephyr/signal_ashare/core/sector_ecology_judge.py     # 三态判定
grep -n "sector_close_final\|sector_pre_open" src/zephyr/data/config/schedule.yaml
sed -n '14,45p' src/zephyr/data/sector_state_pipeline.py                 # 数据流图
grep -n "lifecycle\|启动\|熄火" src/zephyr/signal_ashare/sector/sector_momentum_persistence.py  # 验证堵点2
```
