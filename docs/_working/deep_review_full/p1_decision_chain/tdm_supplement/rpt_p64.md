---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——做T策略调度
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：做T策略调度（P64）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/sell_decision/core/t_trade_coordinator.py:122`（plan_t_trade）
- TDM 节点: TDM-P-P2-02（stage，config/trading_decision_map.yaml:2818，strategy_mounts 三策略 proposed，ai_autonomy: paper）
- 生产调用方: **零**——plan_t_trade 全仓无调用（core_satellite_allocator.py:46 仅文档列举）；TDM 注释已自认"身份=proposed 假说，回测验证通过前不生效（D5 管道）"
- 测试文件: tests/sell_decision/test_t_trade_coordinator.py（40 passed 同批）

## 1 对象快照

- 范围：plan_t_trade 纯函数全文件（166 行）——做T 单标规划：卖出腿≤T+1 可卖（截断留痕）、买回腿=卖出腿（日终复原）、净价差=预期价差−往返成本>viable 门槛。
- 排除项：三策略信号产生（冲高回落/盘口失衡/VWAP 回归，strategy_mounts 声明侧）；执行面（executor/异常兜底归 strategy_abnormal_exit）。
- 测试覆盖概况：方向/输入校验/截断/viable 覆盖；无负价差场景断言缺口小。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点三策略调度语义与模块一对一规划器错位**：TDM-P-P2-02 声明「三策略并发扫描（冲高回落/盘口失衡/VWAP 回归）+同标的多信号按策略适配度仲裁+单次做T量≤底仓 30%」——本模块是**单信号单标规划器**：无策略枚举、无多信号仲裁、无 30% 仓位帽（截断锚=可卖底仓 100%，非 30%）；三策略 strategy_mounts 全部 proposed 无落码。D58 四欠账中仅"复原"在本模块有承载（buyback=sell），双轨止损/连败熔断/主策略优先归执行与风控面（未审） | config/trading_decision_map.yaml:2818-2858 vs t_trade_coordinator.py:122-166；grep 冲高/VWAP 回归/仲裁/30% 于模块零命中 | P1 | 对照 TDM 三策略+仲裁+30% 逐条 grep |
| A | 数学核：net_edge=spread−cost 线性、viable=sell_weight>0 且 net_edge>min_edge、截断比较带 1e-12 容差——正确；边界 sellable=0→viable=False ✓、负 spread→viable=False ✓、planned=0→sell_weight=0→viable=False ✓（无除零）；round_trip_cost 含做T 额外成本的对齐（宪章 §3 约束一）已声明 | t_trade_coordinator.py:128-166 | —（已核） | — |
| B | 预期价差/成本由调用方注入无来源契约：expected_spread_pct 的估计方法（ATR? 分时形态?）与 round_trip_cost_pct 的构成（费率真源 CST-ASTOCK-001）无锚——proposed 身份下尚可，接线时即成"自由心证"入口 | t_trade_coordinator.py:81-83 | P3 | 读蓝图是否补数据源锚 |
| C | 孤儿（proposed 已声明）：零调用方；与 P65 t0_trading_pipeline（独立做T管线）和 t0_trader_agent 的三件关系未收口——TDM-P-P2-02/P2-03/MOD-SIG-090 三个做T 承载并存，蓝图自注"独立做T信号管线与盘中即时反应决策引擎未收口（深挖裁定理由）"（t0_trading_pipeline.py:20-22）——**同一节点语义三处平行承载是双（三）承载漂移的温床**（checklist #4） | t_trade_coordinator.py:7；t0_trading_pipeline.py:20-22；grep 证据 | P2 | 三件签名并排比对做T 语义覆盖面 |
| E | 纯函数无 IO 无时钟——对抗面极小；唯一风险=调用方把 viable=False 计划仍下发（无防御，纯数据输出）——接线时消费方必须尊重 viable | t_trade_coordinator.py:154 | P3 | 接线评审检查 viable 消费纪律 |

## 3 SOTA 对照

- 底仓做T 两腿规划（卖旧买新/买新卖旧+日终复原）：**对等已有**——A 股变相 T+0 的社区标准玩法（知乎/雪球做T 教程 zhihu.com/xueqiu.com，2023-2026；BigQuant 半仓滚动做T，bigquant.com；百度百科"日内回转交易"，baike.baidu.com）；本模块"卖出腿≤昨仓可卖+买回=卖出"与该范式一致，且是三件做T 承载中唯一显式编码 T+1 截断的。
- 多信号仲裁（策略适配度加权）：**对等已有（声明侧）**——多策略信号融合属常规组合管理（与本项目 L1-AGG 同构思想），实现缺位同红节点族。
- 成本前置 viable 门槛：**对等已有**——"振幅/价差盖不住双边成本不做"是做T 社区共识第一纪律（雪球/知乎教程均列为前提，xueqiu.com，2024-2026）；模块的 min_edge 机制正确承载该纪律（值待校准）。

## 4 缺陷清单

1. **[P1] 三策略+仲裁+30% 帽零承载，节点语义=单信号规划器**。建议修法：节点声明收敛为"单标规划器已建（proposed）/三策略与仲裁未建"，或施工批次补调度层；接线前维持 paper。验证法：§2 轴 D grep。
2. **[P2] 做T 三承载件（MOD-SELL-018/MOD-SIG-090/t0_trader_agent）平行未收口**。建议修法：收口裁定（蓝图自注在案）落一个真源+两个退役或分工铁律（建议：资格门=P2-01 待建件、规划=本件、盘中执行编排=MOD-SIG-090、即时裁决=t0_trader_agent，写进 TDM 注释防三写）。验证法：三件签名比对。
3. **[P3] 价差/成本注入无来源锚+viable 消费纪律**。建议修法：蓝图补 CST 费率锚与估计方法登记；接线评审检查 viable 门。验证法：读蓝图 diff。

## 5 挂起疑问

- min_edge_pct/round_trip_cost_pct 的校准数据（CST-T0-001 保守档）与"单次≤底仓 30%"帽的归属层（本件入参 vs 上游调度）待接线设计回答。
- 与 P65 的 14:50 强平/EOD 平衡语义重叠面（复原铁律两处各写一半：本件管计划复原、MOD-SIG-090 管执行复原）——收口时明确边界防双写。

## 6 完备性自评

六轴全查（A 数学四问：net_edge 线性/截断容差/边界全探/无分布假设；B 上游=注入参数契约已查；C 下游=零调用方判孤儿（proposed 已声明）；D=与 TDM 三策略对账+三承载件并行核查（主发现）；E 五问：静默失败=viable 误用面、假阳性=无、断供=不适用、重复触发=纯函数幂等、时序=无时钟）。长尾：①MOD-SIG-068 信号点算法归 signal_ashare 对象；②执行面双轨止损/熔断归 X 流对象；③40 测试逐断言抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
