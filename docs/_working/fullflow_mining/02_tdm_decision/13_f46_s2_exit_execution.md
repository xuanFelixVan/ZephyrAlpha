---
ttl: task_bound
title: F46 S2 离场执行——TDM 离场流 S2 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F46 S2 离场执行（TDM-X-S2 + S2-01..06）

> **一句话**：'卖不卖'定了之后管'怎么卖'：方式路由→T+1/涨跌停约束→时段路由→本地条件单→分批止盈→闭环三率复盘。
> **上游**：S1-05/S1-06、P2-03/P2-04、F-C2-01 强裁、X-R1 broadcast。**下游**：F53-F57 执行基建（订单/打板/SOR/对账）、F-C3-01 归因。

## 一、环节定义与边界
- 树 6 节点：S2-01 路由为枢（五路输入仲裁），S2-02..05 四路执行通道，S2-06 盘后闭环。
- 输入仲裁序（外审 R2-05，D95 确认）：X-R1/S1-06 强清中断 ≥ F-C2-01 组合强裁 > P2-03/P2-04 纪律强平减仓 > S1-05 常规融合。

## 二、状态机血肉
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| S2-01 执行方式路由 | 紧迫度×仓位×流动性 | >0.8 或小仓<2%→一次性市价；中等+大仓→3 批×1/3 间隔 5min；不急+流动性差→尾盘集中；隔夜风险→竞价跌停价逃命。卖出前三查：单笔≤买一档挂单量/日量×10% 参与率/市值÷20日均额>1% 禁市价。D70：IS 急卖 preset（首 1/3 窗完成≥50%）+ICEBERG 随机化±10-20%+市价保护价=基准×97-98% 与笼子交集+枯竭检测。D72 恐慌拦截：低开<-3% 开盘 30min 等待窗禁市价，绕过清单（D95 终裁）=KillSwitch/黑天鹅/跌停封死/K≥3/主力弃庄/利空公告仓+竞价段 9:20-9:25 限价排队豁免 |
| S2-02 T+1 与涨跌停约束 | 跌停三步+可卖额度 | 17:30 夜市委托挂跌停价排队→封单骤减>20% 撤旧改买一价（撤单重挂重置位次禁忌）→次日竞价处理残余；t1_sellable 核对当日买入不可卖。D71 特殊标的四分支：新股首日状态机（分板块参数表）/临停复牌子状态机（盘中±10% vs 长停 D105 默认转人工）/风险警示板（ST 主板 2026-07-06 起 ±10%，#ARCH-DATA-020 修表已清偿：246406 行重算+基线测试锁死）/碎股+科创板 200 股基准；多日连续跌停：基本面暴雷全力跑 vs 情绪错杀放量开板分批（43% 第 3 日开板） |
| S2-03 执行时段路由 | 沪深分裂+竞价即决 | 深市/创业板/科创板 14:57-15:00 集合竞价不可撤 vs 沪市主板可撤（按市场分流）；竞价逃命单 9:15 后挂跌停价；D67 竞价即决十行矩阵（隔夜仓 9:25 定格 30 秒出动作；量能三口径 5-10% 健康/<3% 诱多/>15% 看承接）；D116 新股排除（矩阵无法计算→默认观察）；M-24 跳空分档预案挂载本节点（施工归 position 隔夜批次） |
| S2-04 本地条件单 | vn.py 范式 | 止损/止盈触发器存本地不预占仓位（QMT 预挂会冻结仓位），tick 触发才发限价单；每根 K 线收盘 cancel 重挂刷新；本地 OCO 双停止单。D71：SellChase 状态机（挂单→计时→撤→追 1 tick→15-20 轮耗尽转最优五档即成剩撤；Escape 检查）+快照龄>1 tick 强制刷新；QMT 三坑（business_id 幂等/price=保护限价/on_cancel_error 兜底） |
| S2-05 分批止盈 | Exit Ladder 阶梯 | +1R 减 50% 保本→+2R 再减 25%→尾仓 25% 跟踪止盈；弱信号一次走完/强信号留 runner；MFE 捕获率<50%=卖太早反馈校准 S1 权重；分批 2-4 点最优 |
| S2-06 卖出闭环 | 三率+六分类 | 卖飞率（>30%=止损太紧）/避损率/MFE 捕获率 N 日跟踪；卖出理由六分类封闭枚举（STOP_LOSS/TAKE_PROFIT/TIME_STOP/LOGIC_FAIL/REPLACE/PANIC，每笔必填），PANIC 滚动占比>10%=纪律失效告警（禁先调参数）；D72：信号 N 日前瞻分桶归因（T+5 回填，任一桶 30 日避损率斜率降 30%→该桶权重自动降档）+IS 三分解；D106 终裁冷却=迟滞带+连败阶梯+regime 开关（废日历天数），状态持久化=sleeve 治理状态表（待施工 M-39）；入边分工互斥（R2-06：同一笔成交只经其执行通道上报一次） |

## 三、六向台账
- **上游输入**：S1-05 sequence、S1-06/P2-04/P2-03/F-C2-01 feed、X-R1 broadcast、E-L4-08 signal。
- **下游消费**：S2-06→F-C3-01（daily）+→E-L4-12（冷却清单）；各执行通道→F53 订单生命周期。
- **自动化触发**：**零编排**——sell_execution_planner/scale_out/quality_tracker 均无包外调用（S1 同族根因）；t1_sellable 与 sell_session_router 例外（前者 6 消费方；后者属 ex_sor 族待 M7/EX 组核对其调度面）。
- **真源与注册表**：trading_decision_map.yaml:3500-3722；42 号 §3.7/3.8/3.11+§3.8.1（ST 校准宇宙逐项表）；CST-ASTOCK-001。
- **门禁与质量尺**：ai_autonomy S2-01/02/04/05=paper、S2-03/06=auto；materiality S2-01=critical+monthly。
- **当前运行状态**：**黄（库成、编排缺、唯一 P0 验证已过）**——BT-P0-003 中 X-S2-01 **过**（858 笔滑点 2.65bp≤20bp，成本项逐笔零偏差）；其余 X 流 17 节点 pending。

## 四、子模块清单
| 模块 | 行数 | 状态 |
|------|------|------|
| sell_decision/core/sell_execution_planner.py（MOD-SELL-019） | 333 | 纯库（包外零调用） |
| position/core/t1_sellable.py（MOD-POS-028，S2-02 复用） | 66 | wired（6 消费方） |
| ex_sor/core/sell_session_router.py（MOD-XS-016） | 339 | 在盘（ex_sor 族内；调度面归 M7/EX 核） |
| ex_core/local_order_queue.py（MOD-L06-001） | 271 | 在盘（ex_core 族内） |
| sell_decision/core/scaling_out.py（MOD-SELL-017） | 165 | 纯库 |
| sell_decision/core/sell_execution_quality_tracker.py（MOD-SELL-012） | 210 | 纯库 |

## 五、堵点与病灶
1. **执行链编排缺位与 S1 同根**：路由/约束/条件单/分批全库成无调用；修法=S1 扫描编排下游直接接 S2-01 路由器（同一工单两段）；量级 3-5 天。
2. **S2-06 状态持久化载体缺位**（M-39 sleeve 治理状态表待施工）——冷却迟滞带/连败阶梯无处落盘。
3. **M-24 跳空分档预案、节前决策表**挂本节点但施工归 position 隔夜风险批次（跨车道依赖，登记勿代修）。
4. **验证欠账**：S2-02..06 五对象（BT-P3-031..035）plan=null 阈值未预注册；exit_counterfactual 真结论待窗口前移。

## 六、提速与合并机会
S2-06 三率统计与 F-C3-01 归因共用卖出流水（IS 三分解已并入执行成本轴）——防两套跟踪器；S2-02 与 S2-03 共用 stk_limit 切片管道（#ARCH-DATA-020 已清偿）禁再写涨跌幅判断。

## 七、自审闸三态
**挖干可施工**。

## 八、复核命令
```bash
grep -n "node_id: TDM-X-S2" config/trading_decision_map.yaml
grep -A16 "object_id: BT-P0-003" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml | tail -4   # X-S2-01 过/P2 双节点存疑
ls tests/sell_decision/ && wc -l src/zephyr/ex_sor/core/sell_session_router.py
```
