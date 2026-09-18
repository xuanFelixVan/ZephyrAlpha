---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——执行方式路由
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：执行方式路由（P74）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/sell_decision/core/sell_execution_planner.py:177`（SellExecutionPlanner.schedule_sell_order:181）
- TDM 节点: TDM-X-S2-01（stage，config/trading_decision_map.yaml:3437，materiality: critical，ai_autonomy: paper）
- 生产调用方: **零**——SellExecutionPlanner 仅包导出（sell_decision/core/__init__.py:43,143）；schedule_sell_order/rank_* 全仓零调用；header 声明的 D-EX-CORE 40 号执行层/MOD-SELL-009 零实际接线
- 测试文件: tests/sell_decision/test_sell_execution_planner.py（114 passed 同批）

## 1 对象快照

- 范围：SellExecutionPlanner 全文件（333 行）——信号类型→执行动作静态映射（强制清仓 3 类=市价绕过融合/止损 3 类=盘中限价/止盈换仓退潮 3 类=尾盘 14:50 集中）+T+1 硬约束+跌停不提交排队次日+跌停排队三级排序+KillSwitch 清仓三级排序。
- 排除项：MOD-SELL-009 紧迫度评分（输入方）；分批执行（S2-05 归 MOD-SELL-017 scaling_out）；券商接口（40 号执行层）。
- 测试覆盖概况：三桶映射/T+1/跌停/排序覆盖（114 passed）；**无做T 卖底仓（混合仓 lot）场景、无紧迫度路由场景（模块无紧迫度路由）**。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **节点路由核心键（紧迫度×仓位×流动性三维）零承载，模块退化为信号类型静态查表**（对账主发现）：TDM-X-S2-01 声明「紧迫度>0.8 或小仓(<2%)→一次性市价；**中等紧迫+大仓→分批（3 批×1/3 间隔 5 分钟）**；不急+流动性差→尾盘集中；隔夜风险单→竞价挂跌停价」——schedule_sell_order 无紧迫度/仓位大小/流动性任何参数（:181-187 签名即证），路由=9 信号枚举三桶静态映射；分批分支不存在（TDM 注明分批归 S2-05/MOD-SELL-017，但本路由**连"分批"动作项都不产**，中等紧迫大仓场景无处可去）；**卖出前三查（单笔≤买一档挂单量/日量×10% 参与率/持仓市值÷20日均额>1% 禁市价）零承载**（模块无任何量能/流动性输入）；D70 IS 急卖 preset/ICEBERG/保护价/枯竭检测、D71 队列重排、**D72 恐慌拦截（低开<-3% 30min 等待窗）+D95 竞价豁免、R2-05 四路输入仲裁——全部零代码** | config/trading_decision_map.yaml:3437-3500（含 D70/D71/D72/D95/R2-05 注释） vs sell_execution_planner.py:180-275；grep 紧迫度/参与率/恐慌/等待窗 于模块零命中 | P1 | 对照路由表+前三查逐条 grep；读 schedule_sell_order 签名 |
| A | **T+1 校验粒度误杀做T 卖底仓**：buy_date 单值 per 调用（:213-221），buy_date>=today 即 BLOCKED_T1——A 股按**仓**（lot）判 T+1：底仓（旧仓）+当日加仓混合时，卖旧底仓合法；做T 正T（当日低位买新、卖出用原可卖底仓，MOD-SELL-018 :23-24 明文）若调用方传当日买入日→底仓卖出被误杀；传底仓旧日→当日加仓部分漏拦。单 buy_date 契约无法表达 lot 级可卖，隐式契约未文档化 | sell_execution_planner.py:212-221；t_trade_coordinator.py:23-24（正T 卖原底仓语义） | P2 | 正T 场景传 buy_date=today 看底仓卖单被 BLOCKED_T1 |
| A | 排序键实现（已核，与 docstring 一致）：跌停排队=紧迫度降序→亏损升序（最亏先排）→金额降序；KillSwitch 清仓=流动性升序（差的先卖防封死）→金额降序→亏损升序——"先保成交后保价格"的清仓哲学自洽；跌停挂价建议表（P0/P1/P2 跌停价、P3 开盘价-0.5%）仅 docstring 承载无结构化输出 | sell_execution_planner.py:297-333 | —（已核） | — |
| B | date.today() 墙钟依赖：today=None 时取 date.today()（:214）——T+1 判定依赖本地日历日，时区/夜间批处理跑昨日信号会误判"当日"；模块其余为纯函数（可测性破口一处） | sell_execution_planner.py:214 | P3 | 固定 today 参数对比 None 行为 |
| C | 孤儿死码（checklist #8，materiality: critical 节点）：全链（收集→评分→融合→路由→执行）X 流在 S2-01 一环零在网 | sell_execution_planner.py:5-6；grep 证据见上 | P2 | grep 三连 |
| A(亮点) | 9 类执行信号与收集器 8 类正交（:79-89 自注执行编排层分类）；三桶信号集 frozenset 常量清晰；上交所 14:57 竞价分界落地（:67-68,246-259）；跌停/清仓两排序的经济学理由写足 | sell_execution_planner.py:64-70,149-174 | — | — |

## 3 SOTA 对照

- 卖出执行路由（紧迫度/规模/流动性三维选通道）：**对等已有**——执行算法选型三维（urgency/size/liquidity）是 SOR 标准输入（Optimal Execution Algorithms TWAP/VWAP/IS 综述 mbrenndoerfer.com，2026；IBKR 算法族 interactivebrokers.com，2026，同 P51 引）；**参与率上限（日量 10%）与单笔≤盘口档位**是执行合规常规（同上 TWAP 执行指南 medium.com/@cmsfinancial2004，2026）——TDM 前三查有据、实现缺位。
- 分批退出（3×1/3 间隔 5min）：**对等已有**——分批 2-4 点最优（TDM-X-S2-05 已引社区共识；TradersPost scaling 指南 blog.traderspost.io，2026，同 P67 引）；本项目分批承载在 MOD-SELL-017（P72 报告已注两件皆孤儿）。
- 跌停排队优先级（流动性差先卖）：**立卡候选（项目特色，教义内自洽）**——A 股跌停封板排队先来先得是制度现实，"流动性差的先卖"与主流"先卖能卖的"直觉相反但论证成立（防后卖者封死）；无外部文献可引（A 股特有），建议回测/模拟批验证排序收益。

## 4 缺陷清单

1. **[P1] 三维路由/分批分支/前三查/D72 恐慌拦截/R2-05 仲裁全零承载**——critical 级节点的"路由"实为静态查表。建议修法：施工批次补紧迫度/仓位/流动性入参与三维路由+前三查前置检查（量能数据源依赖 DS 登记）；D72 恐慌拦截窗（含 D95 豁免清单）单独成门；节点补红量化缺口。验证法：§2 轴 D grep。
2. **[P2] T+1 校验 lot 粒度缺失（误杀正T 卖底仓/漏拦当日加仓）**。建议修法：入参改 lots 列表（buy_date×quantity）或拆两调用（底仓/今仓分别判）；文档铁律"调用方须按 lot 拆分"。验证法：正T 场景探针。
3. **[P2] 孤儿死码**。建议修法：X 流 S1→S2 全链接线批次统一（P71/P72/P74 三件同批）；接线前降 draft。验证法：grep。
4. **[P3] date.today() 墙钟依赖+跌停挂价建议无结构化输出**。建议修法：today 必填化；挂价建议进 SellOrderPlan 字段。验证法：读签名。

## 5 挂起疑问

- 三桶静态映射（止损立即/止盈尾盘）与 D72 恐慌拦截窗的关系（拦截窗优先于桶映射？）——D72 修复时一并裁定时序。
- KillSwitch 清仓排序"流动性差先卖"在真机上的收益无实证——建议列入模拟批对照（流动性优先 vs 亏损优先两组）。

## 6 完备性自评

六轴全查（A 数学四问：两排序键方向/时序比较/T+1 比较逐个过、边界=T+1 边界日/14:57 分界/空仓列表已测；B 上游=urgency_score/liquidity_score 来源契约已查（评分器 MOD-SELL-009 亦未审——长尾）；C 下游=零调用方判孤儿；D=与 TDM 路由表逐项对账（主发现）；E 五问：静默失败=无（动作显式）、假阳性=T+1 粒度、断供=无、重复触发=纯函数幂等、时序=date.today 破口。长尾：①MOD-SELL-009 紧迫度评分未审；②40 号执行层订单分解未审；③MOD-SELL-017 分批件未审（P72 已注）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
