---
ttl: task_bound
---

# M2 车道总索引：离场族（X）13 节点 + 板块族（L2）29 节点接线规格卡

- 车道: 挖矿车道 M2 | 日期: 2026-10-06 | 性质: 只读挖矿产物（仅本目录新文件）
- 真源: `docs/_working/fullcirc_closeout_chief/t3_fullflow_exam_mining.md` §1.7/§1.3；
  `config/trading_decision_map.yaml`；CH 实测见 L2-00 卡数据底座表
- 分级口径（沿 t3 挖矿 §2）：**S**=参数/数据接线复用在册模块（纯向量化，0.53s/格口径可沿用）；
  **M**=模块补写（新逻辑日频可表达；**凡路径依赖行循环激活，T3b-T0 强制重标定 per_point_seconds，
  fail-closed**——每张 M 级 X 卡 §5 已内嵌此条）；**L**=只登记（无诚实可考代理/门位未开/tick 级）。
- 引擎能力底册: `scripts/backtest/factory_grid_executor.py` T6 头注（J 总闸/exec_caliber/
  估值财务因子面/护盘白名单登记/成本归因/t3 stage 六件已接线）、`scripts/backtest/translated/_c4_engine.py`
  （权重路径回测核+封板闸+fillability 行循环模式）、`docs/_working/gpu_rewrite/p1_wiring_benchmark.md`。

## 一、X 族（离场，13 节点；真源 t3_fullflow_exam_mining.md §1.7 计 19 节点，本索引缩圈剔除 6 枚：S2-02 已近似实现、S1-06/S2-06 非回测域、X-R1/R1-01/R1-02 熔断族 3 枚（登记型节点，规格卡不适用——留 Owner/风控门位），均不在清单）

| node_id | 机制名 | 级别 | 规格卡 | 依赖数据 |
|---|---|---|---|---|
| TDM-X-FLOW | 输出离场信号（聚合） | S | spec_x_TDM-X-FLOW.md | 无（导出列） |
| TDM-X-R1-03 | 护盘资产白名单 | S | spec_x_TDM-X-R1-03.md | ETF 日线（load_etf）；MOD-POS-026 常量 |
| TDM-X-S1 | 卖出信号收集评分（组） | L | spec_x_TDM-X-S1.md | —（组节点） |
| TDM-X-S1-01 | 信号收集与六桶分类 | M | spec_x_TDM-X-S1-01.md | close/high/low（kline_daily） |
| TDM-X-S1-02 | 止损族判定 | M | spec_x_TDM-X-S1-02.md | close/high/low（ATR 自算） |
| TDM-X-S1-03 | 止盈族判定 | M | spec_x_TDM-X-S1-03.md | 同上 + stk_limit（目标位"次日不板走"档） |
| TDM-X-S1-04 | 破位与情绪退潮 | M | spec_x_TDM-X-S1-04.md | close/amount + stk_limit；LHB 不可考 |
| TDM-X-S1-05 | 信号融合与紧迫度 | M | spec_x_TDM-X-S1-05.md | close/amount |
| TDM-X-S2 | 离场执行（组） | L | spec_x_TDM-X-S2.md | —（组节点） |
| TDM-X-S2-01 | 执行方式路由 | M | spec_x_TDM-X-S2-01.md | volume/amount（参与率同纲 INV-UNIT-001） |
| TDM-X-S2-03 | 执行时段路由 | S | spec_x_TDM-X-S2-03.md | open/vwap（exec_caliber 已接线） |
| TDM-X-S2-04 | 本地条件单管理 | L | spec_x_TDM-X-S2-04.md | —（tick 级，99 负结果 #3） |
| TDM-X-S2-05 | 分批止盈执行 | M | spec_x_TDM-X-S2-05.md | close（entry/stop 状态数组） |

X 族小计: **S=3 / M=7 / L=3**。

## 二、L2 族（板块选择，29 节点；数据底座 CH 实测见 L2-00 卡）

| node_id | 机制名 | 级别 | 规格卡 | 依赖数据 |
|---|---|---|---|---|
| TDM-E-L2 | 板块选择（组骨架+数据底座） | L | spec_l2_TDM-E-L2.md | 底座总表在本卡 |
| TDM-E-L2-01 | 板块强度综合 | M | spec_l2_TDM-E-L2-01_strength.md | 行业聚合宽表（industry_class×kline_daily）+stk_limit |
| TDM-E-L2-01-1 | 结构强度评估 | M | spec_l2_TDM-E-L2-01_strength.md | 封板掩码（stk_limit）；梯队代理（负结果 #6） |
| TDM-E-L2-01-2 | 动量活跃度排名 | M | spec_l2_TDM-E-L2-01_strength.md | amount 聚合 |
| TDM-E-L2-01-3 | 多周期动量加权 | M | spec_l2_TDM-E-L2-01_strength.md | 行业指数 close |
| TDM-E-L2-01-4 | 板块资金流聚合 | M | spec_l2_TDM-E-L2-01-4_flow.md | money_flow（2021 起实测） |
| TDM-E-L2-01-5 | 市场级调节注入 | M | spec_l2_TDM-E-L2-04_state.md | L2-01 score 面 |
| TDM-E-L2-02 | 轮动序列追踪 | M | spec_l2_TDM-E-L2-02_rotation.md | 行业聚合宽表（D90 速度计口径在册） |
| TDM-E-L2-02-1 | RRG 轮动序列 | M | spec_l2_TDM-E-L2-02_rotation.md | 同上；880 指数仅对照窗（负结果 #9） |
| TDM-E-L2-02-2 | 单板块轮动预警 | M | spec_l2_TDM-E-L2-02_rotation.md | 行业指数+龙头代理 |
| TDM-E-L2-03 | 调整周期进度 | M | spec_l2_TDM-E-L2-03_cycle.md | 行业聚合宽表+个股 close（扩散） |
| TDM-E-L2-03-1 | 扩散指标进度追踪 | M | spec_l2_TDM-E-L2-03_cycle.md | close>MA20 行业占比 |
| TDM-E-L2-04 | 板块级市场状态 | M | spec_l2_TDM-E-L2-04_state.md | L2-01 面（涨停家数/集中度） |
| TDM-E-L2-04-1 | 轮动状态五分类 | M | spec_l2_TDM-E-L2-04_state.md | 同上 |
| TDM-E-L2-04-2 | 虹吸态识别 | M | spec_l2_TDM-E-L2-04_state.md | amount 集中度 |
| TDM-E-L2-05 | 水温响应 | L | spec_l2_TDM-E-L2-05_water.md | —（pending_owner 门位，负结果 #11） |
| TDM-E-L2-05-1 | 水温档推导 | L | spec_l2_TDM-E-L2-05_water.md | —（S5 温度计缺口） |
| TDM-E-L2-05-2 | 信号响应三件套 | L | spec_l2_TDM-E-L2-05_water.md | —（同上） |
| TDM-E-L2-06 | 板块个股传导 | M | spec_l2_TDM-E-L2-06_conduction.md | industry one-hot+sector_score |
| TDM-E-L2-06-1 | 三级放行门槛 | M | spec_l2_TDM-E-L2-06_conduction.md | close/amount（gate 三布尔） |
| TDM-E-L2-06-2 | 龙头识别定位 | L | spec_l2_TDM-E-L2-06-2_leader.md | tick 语义不可考；M 降级代理档在卡内 |
| TDM-E-L2-06-3 | 强度加权传导 | M | spec_l2_TDM-E-L2-06_conduction.md | 查表乘性系数（TDM 冻结口径） |
| TDM-E-L2-07 | 回踩质量分级 | M | spec_l2_TDM-E-L2-07_pullback.md | 行业 OHLCV 高点+Fib |
| TDM-E-L2-07-1 | 回踩ABC判定 | M | spec_l2_TDM-E-L2-07_pullback.md | 四因子（Fib/量能/强度/时间窗） |
| TDM-E-L2-08 | 板块生命周期判定 | M | spec_l2_TDM-E-L2-08_lifecycle.md | 封板掩码聚合；炸板率不可考（负结果 #8） |
| TDM-E-L2-09 | 催化剂识别 | L | spec_l2_TDM-E-L2-09_catalyst.md | —（文本域，负结果 #10） |
| TDM-E-L2-09-1 | 事件图谱传导 | L | spec_l2_TDM-E-L2-09_catalyst.md | ig_* 图谱（live 件在册，考卷化=新数据线） |
| TDM-E-L2-09-2 | 冲击标的生成 | L | spec_l2_TDM-E-L2-09_catalyst.md | 同上 |
| TDM-E-L2-10 | 同源补涨比价 | M | spec_l2_TDM-E-L2-10_catchup.md | fallback 横向比价（close 分位）；图谱版 L |

L2 族小计: **M=21 / L=8（S=0）**。

## 三、总计与最快落地序

**42 节点: S=3 / M=28 / L=11**（逐行指针见上两表，零遗漏）。

最快可落地 5 张卡（依赖最少+复用最高）:
1. **X-S2-03（S）**——exec_caliber 已接线（T6 ②），只差 prereg 开维对照。
2. **X-R1-03（S）**——T6 ④ 已登记 `defensive_whitelist_assets()`，剩余属 Owner 门位翻转。
3. **L2-06（M）**——传导=合成因子后的乘性后处理，零新数据线零新回测语义，L2 族首件。
4. **X-S1-02（M）**——止损族 M1 核心：ATR 研究样板在册（indicator_consumption_demo），
   vectorbt 成熟口径可译；落地即激活整条离场族。
5. **L2-01（M）**——板块强度主干（t3 挖矿 M3 完整化）：行业锚与 load_px 全在册。

共同前置（施工批义务，非本车道可完成）: ①schema 增维（X_stop/X_tp/X_sector 等）须裁定；
②所有 M 级路径依赖格点 T3b-T0 重标定 per_point_seconds（fail-closed）后才能定 T1/T2 点数；
③新 .py 模块走 CREATE-GUARD/capability_lookup/GATE-SELFDOC 既有门。

负结果与不可行项: 见 `99_negative_results.md`（13 条台账）。
