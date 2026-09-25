---
ttl: task_bound
title: F50 C3 绩效归因反馈——TDM 组合流 C3 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F50 C3 绩效归因反馈（TDM-F-C3 + C3-01..05）

> **一句话**：系统自我进化的发动机：多维归因（钱从哪赚亏到哪）→升降级退役评审→sleeve 调权→参数校准→传感器可靠度反馈 L1；全部凭数据不凭感觉。
> **上游**：F49/F28 归因供料、P2-03 做T统计、S2-06 卖出闭环、E-L4-13/E-L3-08 feed。**下游**：回灌 F37/E-L1-AGG/E-L2（feedback T-1）、E-L0（当日 feed）、F21 假说先验、C1 调权。

## 一、环节定义与边界
- 五节点：C3-01 多维归因（aggregation）四路分发→{C3-02 升降级评审、C3-03 调权、C3-04 参数校准、C3-05 可靠度养成}；C3-02→C3-03。
- D50 三欠账（交易/持仓盈亏二分、P&L Explain、逐笔 TCA）已由 C3-01 承接落位（D74 轮）。

## 二、状态机血肉
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| C3-01 多维归因引擎 | 几何 Brinson+二分+三分解 | 8 sleeve=8 板块（配置/选股/交互三效应，免多期 linking）+因子/风险归因+策略降级检测（IC 衰减>50% 权重归 0 建议）+拥挤检测（ρ>0.8 减半/0.9 归零建议）；交易 vs 持仓盈亏二分（vn.py 范式）+IS 三分解（延迟/冲击/机会成本）。D84 正确性必改五件：①T+1 隔夜漂移切账（delay cost 不进 PerfScore 不进执行考核）②收益基准双轨（sleeve=TWR 几何链接/账户=XIRR）③复权口径（账本存不复权价+复权因子，禁前复权快照）④孤儿成交 suspense（house account+中签独立打新 sleeve+手工单次日强制补标签）⑤现金贡献行（GC001，涨/跌月分开） |
| C3-02 升降级管线与退役评审 | 月度评审+季度 verdict | 四选一（维持/减半/清退/重审，每 sleeve 恰好一个输出；阈值未触发=no change）；THD-RETIRE 三线（滚动 20 日跑输基准 5%/60 日 Sharpe<0/回撤漂移 1.5×）；**sleeve 回撤 5% 自动减半/7.5% 冻结不等评审**（M-22 收口：收盘核算触发防盘中假摔；盘中例外=触 7.5% 即时禁新开仓可逆）；DSR 门禁（退役=滚动 DSR<0 连续 8 周）；D86：composite 60+120 日双窗口对自身历史分布取分位+0.05 硬线 2 连月（单月≥0.05 清零重计 D96）+三类一票否决+观察名单半仓缓刑 3 个月（恢复=50+ 笔 forward+PF>1.1-1.2+Sharpe>0.5-0.8）+滞回带（恢复线高于降权线一档+5 交易日锁定+单次±10pp 上限）+fail-safe（数据质量门未过=当月不调权记"未归因月份"）；清退归零=系统自动产出评审提案+Owner 签字（D96） |
| C3-03 sleeve 权重调权 | 月度公式+三层仲裁 | 新权重=normalize(基准×PerfScore×Shrinkage)，floor 5%/cap 40%；危机覆盖（WO-2a）：is_crisis 或 crisis_floor_active（θ 真源 config/crisis_gate.yaml）→floor 0.09 降至 0.05；三纪律：≤±10pp/调整后 5 交易日锁定/未触发 no-change；D86：no-trade band（只调偏离>25% 的 sleeve，频率≤每周）+成本闸（双边成本>改善 50% 缓调）+三层仲裁（回撤 Protocol/KillSwitch 即时覆盖>budget 资格>C3-03 动多少；减权立即执行、加仓等资格）+Component VaR 边际检查（252 日协方差 8 sleeve 边际贡献表）；D87 月报错配双列表+归因有效期标注（协方差窗口观测数+波动状态两行元数据） |
| C3-04 参数校准闭环 | 四道 gate | CPCV+DSR+PBO<30%+参数平台期全过才准改参；WFE>60% 可用/<40% 禁上线；purge 窗=持仓半衰期+embargo≥5 日；DSR 只做门禁不做优化目标；底座建议 purgedcv/skfolio。D86 小样本防线：3 月<15 笔 forward="数据不足"沿用缓刑；归因结论带置信区间（30 笔 60% 胜率 95%CI≈[42%,78%]）；打板类只做计数型检验；8 sleeve×环境切片 BH-FDR 校正。D87：sleeve 内信号级归因并入 G04+SHARP 纪律单参数原子改；冷启动=30% 仓位起步+三条件转正常评审 |
| C3-05 可靠度养成与信号健康 | 三档递进 | 等权起步（Fed 实证简单平均最稳）→月度判准率加权（下限 10%）→粒子滤波时变（远期）；滚动 IC+半衰期 hyperbolic 拟合+三选二衰减报警；权重下限 10% 月度更新禁日级追权重（D93），主线倾斜通道例外（当日生效上限 60%）。D87 四扩展：L2 板块命中表/选股漏斗影子对照（未入选 paper T+5）/反馈边治理三档（自动执行/预授权/纯人工）/币圈 schema 预留（funding/basis 独立行 A 股恒 0+UTC 时间轴，不预建引擎） |

## 三、六向台账
- **上游输入**：C2 sequence、P2-03/S2-06/E-L4-13/E-L3-08 feed（edge 实测 6 条入边）、E-L9-E2 证伪回传。
- **下游消费**：C3-05→E-L1-AGG+E-L2（feedback T-1）、C3-03→C1（feedback）、C3-01/04→E-L0（当日 feed）、C3-02→F21 回灌。
- **自动化触发**：C3-01/02 靠日链（daily_decision/attribution 阶段）；**C3-03 装配体夜批已运行**（allocation_orchestrator 内 RegimeMetaAllocator 实例化实测 :1081）——TDM 注记"编排未接线（裁定#257②，PFA-1 实证）"已过时，接线随 MOD-PA-030 落地（G15→G14 挂起条件已触发），**地图 note 待回填**。
- **真源与注册表**：trading_decision_map.yaml:3780-4170；54/55 号备忘录在档；THD-RETIRE×3/BMK-INDEX-003/BMK-ABSOLUTE-001。
- **门禁与质量尺**：五节点全 auto；crisis_gate.yaml θ 真源。
- **当前运行状态**：**黄（paper 域部分运行）**——C3-01 归因引擎（702 行）在盘、被 factor_exposure_manager/降级 monitor 消费；C3-02 lifecycle_state_machine（121 行）在盘、红节点（评审编排面）；C3-03 夜批在跑；C3-04 红节点（G04 闭环未转起来，tracker #48）；C3-05 红节点（D7-D13 判准率加权 src 零实现）。

## 四、子模块清单
| 模块 | 行数 | 消费方 | 状态 |
|------|------|--------|------|
| pf_core/core/performance_attribution_engine.py（MOD-PF-007） | 702 | factor_exposure_manager/performance_attribution_degradation | 在盘 |
| factor/governance/lifecycle_state_machine.py（MOD-L02-013） | 121 | 红节点编排面 | 在盘 |
| pf_alloc/core/regime_meta_allocator.py（MOD-PA-007） | 804 | allocation_orchestrator 等 pf_alloc 族 | **wired（注记滞后）** |
| backtest/core/walk_forward.py（MOD-BT-001） | 332 | G04 容器 | 在盘 |
| signal_quality/signal_degradation_monitor.py（MOD-SIGQC-004） | 332 | 红节点承载 | 在盘 |

## 五、堵点与病灶
1. **C3-04 校准闭环未转起来**（四道 gate 容器在、G04 工单在、无人串环；修法=C3-01→C3-04→参数 registry 工单链立项；2-3 天；本车道可修）。
2. **C3-05 判准率加权零实现**（传感器可靠度只有监控件无加权器；修法=与 E-L1-AGG 反馈边一起立项）。
3. **C3-02 评审编排面红**（月度/季度评审无调度体发起；需 M5 登记月度任务）。
4. **地图 C3-03 注记滞后**（"未接线"vs 实测 wired——按 S4 场景须 D 裁定留痕刷新 note_confirmed）。
5. **验证欠账**：BT-P3-043..047 五对象 plan=null；portfolio_attribution（归因分解残差<1bp 对账）未跑——归因引擎自己没被验证。

## 六、提速与合并机会
C3-01 与 F28 E9 归因（MOD-PF-007 同族）共享 Brinson 引擎禁双算；C3-05 可靠度框架与 L2 板块命中表复用同一判准器（D87 已声明同构）。

## 七、自审闸三态
**挖干可施工**（红节点三处均有真源+修法；地图注记滞后已登记回填项）。

## 八、复核命令
```bash
grep -n "node_id: TDM-F-C3" config/trading_decision_map.yaml
grep -n "RegimeMetaAllocator" src/zephyr/pf_alloc/allocation_orchestrator.py   # C3-03 已接线证据
wc -l src/zephyr/pf_core/core/performance_attribution_engine.py
```
