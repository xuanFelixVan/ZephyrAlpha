---
doc_type: audit_report
title: 候选模块清单 — D_EX_SOR
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_EX_SOR 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **84** 条（原有 0 + harvest 84）。
> harvest 去重四态: likely_new=45 / likely_planned=33 / uncertain=6

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0236 | Smart Order Router 智能订单路由 | XS 01 Smart Order Router ✅ 智能订单路由器(简化版A股单市场) | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0237 | Broker Adapter 适配器 | / XS-02 / Broker Adapter / ✅ / 项目内有蓝图编号MOD-L05-001已建设 / 多券商API统一适配 / | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0238 | Market Impact Modeler 模型 | / XS-03 / Market Impact Modeler / ❌ / 门禁：需Level-2实时数据+高频交易环境 / Almgren-Chriss市场冲击建模 / | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0239 | Execution Scheduler 调度器执行 | / XS-04 / Execution Scheduler / ✅ / / TWAP/VWAP/IS算法调度 / | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0240 | Broker API Connector 券商API连接器 | / XS-13 / Broker API Connector / ✅ / / 券商API连接器REST/FIX / | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0656 | C-026 API行为监控 API Behavior Monitor | 监控API行为路由域抽象券商接口 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0707 | Smart Order Router 智能订单路由器 | 智能订单路由多交易所路由最优执行流动性检测路由策略路由回测 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0708 | Execution Algorithm Engine 执行算法引擎 | 执行算法引擎VWAP TWAP POV IS算法选择参数优化算法回测 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0709 | Market Impact Estimator 市场冲击估算器 | 市场冲击估算器Almgren-Chriss参与率临时永久冲击冲击成本预测 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0710 | Liquidity Detector 流动性检测器 | 流动性检测器买卖价差深度参与率流动性评分流动性预测 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1403 | Order Book Simulator 订单簿仿真器 | 订单簿重建+事件回放+仿真引擎+指标计算 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1404 | RL Execution Training Env RL执行训练环境 | 执行策略RL训练环境+奖励函数库+策略训练+评估 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1405 | Low-Latency Data Handler 低延迟数据处理器 | 行情解析+订单簿维护+UDP组播+时间序列缓存 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1406 | Low-Latency Path Optimizer 低延迟路径优化器 | CPU亲和性+NUMA绑定+内存池+无锁队列→<1μs抖动 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1407 | Algo Execution Selector 算法执行选择器 | 订单特征→自动选择最优算法+算法推荐+效果评估 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1408 | Adaptive Routing Optimizer 自适应路由优化器 | 路由决策历史→ML→路由策略持续优化 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1409 | Exchange API Rate Limiter 交易所API限速器 | Token Bucket/Leaky Bucket→API调用限速+排队 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1410 | API Doc Auto Version Syncer API文档自动版本同步器 | API变更检测+Diff+适配器更新 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1411 | API Route & Service Discovery API路由与服务发现 | 端点注册+服务发现+负载均衡+故障转移 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1412 | Slippage Analyzer 滑点分析器 | 滑点分析+滑点归因+滑点预测+基准比较 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1413 | Execution Quality Scorer 执行质量评分器 | 执行质量评分+价格/时间/成本/市场影响多维评估 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1414 | Transaction Cost Optimizer 交易成本优化器 | 交易成本优化+佣金+印花税+冲击成本+机会成本 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1415 | Multi-Framework Strategy Router 多框架策略路由器 | Backtrader/Freqtrade/VeighNa三框架策略执行路由 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1416 | Multi-Exchange Optimal Router 多交易所最优路由器 | 多交易所智能订单路由+自适应路由 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2097 | SOR Agent 路由Agent | 执行层路由Agent智能路由拆单策略滑点控制 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2132 | Smart Routing 智能路由 | 路由Agent技能智能路由ACTIVE | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2133 | Order Splitting 拆单策略 | 路由Agent技能拆单策略ACTIVE | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2971 | Order Routing 订单路由 | 订单路由 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3150 | XS-05 Algo Trading Engine 算法交易引擎 | / XS-05 / Algo Trading Engine / 算法交易引擎：TWAP/VWAP/ICEBERG/POV/Implementation Shortfall/ALT+算法注册表+参数优化器 / P1 / ①可建 / — / | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3151 | XS-06 Venue Selector 交易场所选择器 | 成本/流动性/延迟多维加权评分最优执行场所 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3155 | execution-sor 路由Agent | 智能路由拆单策略滑点控制 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3156 | 路由Agent熔断器 | 路由决策3次/5分钟失败率熔断 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3157 | CB-002 miniQMT下单熔断器 | miniQMT下单>5%持续15s熔断 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3158 | CB-001 iFind数据拉取熔断器 | iFind数据拉取>10%持续30s熔断 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3159 | Close-Only Mode 仅平仓模式 | miniQMT连接中断→仅允许卖出 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3169 | trading_core P3交易核心进程 | 风控检查订单构建miniQMT下单持仓同步 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3170 | xtquant miniQMT接口库 | xtdata行情模块+xttrader交易模块 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3171 | XtMiniQmt.exe 极简模式进程 | 必须运行XtMiniQmt.exe极简模式进程 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3172 | XTP/CTP/OKX 券商API | API版本迁移适配XTP/CTP/OKX | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3173 | FIX 4.2 协议 | 券商对接用FIX协议降低耦合 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3174 | L1全局限流 | 所有外部API合计出站请求滑动窗口50QPS | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3175 | L2外部系统级限流 | miniQMT/iFind/LLM各自令牌桶 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3176 | L3操作级限流 | 分时段+分操作类型令牌桶 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3177 | L4优先级限流 | 交易>风控>行情>因子>通知优先级队列 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3182 | Almgren-Chriss最优执行框架 | 临时冲击η+永久冲击γ+风险厌恶λ+参与率上限 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3183 | TWAP算法 TWAP Algorithm | 时间加权平均价格算法 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3184 | VWAP算法 VWAP Algorithm | 成交量加权平均价格算法 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3185 | ICEBERG算法 ICEBERG Algorithm | 冰山订单算法隐藏大单 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3186 | POV算法 POV Algorithm | 参与率算法Percentage of Volume | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3187 | Implementation Shortfall算法 IS Algorithm | 执行差额算法 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3188 | ALT算法 Aggressive Liquidity Taking | 激进流动性摄取算法 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3189 | VPIN 订单流毒性 | VPIN>阈值→暂停买入执行 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3190 | LOB不平衡度 | 买盘深度vs卖盘深度→短期价格方向 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3191 | LOB恢复速度 | 大单吃掉后多久恢复→恢复慢=冲击成本高 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3192 | Hawkes过程 | 订单到达自我激发和交叉激发→预测短期订单流 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3193 | 做市商行为推断 Market Maker Behavior Inference | 订单簿中大单挂单/撤单模式分析 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3194 | DQN强化学习执行 | DQN离散动作强化学习执行 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3195 | PPO强化学习执行 | PPO连续动作强化学习执行 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3201 | L0 正常降级等级 | 全功能运行全部策略活跃 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3202 | Sniper→ALT 主观交易经验映射 | 主观狙击→量化标准激进流动性摄取 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3203 | HYDRA-EI→HMARL 主观交易经验映射 | 自定义框架名→学术标准分层多智能体强化学习 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3204 | Smart→Optimal/Adaptive 主观交易经验映射 | 语义模糊智能→精确最优/自适应 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3205 | 踏空追高→FOMO Entry 主观交易经验映射 | 主观情绪→行为金融学标准术语 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3206 | 被套补仓→Underwater Averaging Down 主观交易经验映射 | 主观经验→量化标准水下加仓摊薄 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3207 | 亏损报复→Revenge Trading 主观交易经验映射 | 主观情绪→行为金融学标准术语 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3208 | 盈利骄傲→Overconfidence 主观交易经验映射 | 主观情绪→行为金融学标准术语过度自信 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3209 | 做T→Intraday Round-trip Trading 主观交易经验映射 | A股特有术语→量化标准日内往返交易 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3210 | 追跌卖出→Distressed Selling 主观交易经验映射 | 主观经验→量化标准恐慌性卖出 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3211 | 保命轨→Emergency Survival Track 主观交易经验映射 | 口语化→量化标准紧急生存轨道 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3212 | 仅平仓→Close-Only Mode 主观交易经验映射 | 口语化→量化标准仅平仓模式 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3213 | Backtrader框架 | 多框架策略执行路由之一 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3214 | Freqtrade框架 | 多框架策略执行路由之一 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3215 | VeighNa框架 | 多框架策略执行路由之一 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3285 | Fail-Closed 合规规则引擎不可用机制 | > Fail-Closed：合规规则引擎不可用→C-004默认拒绝所有订单→C-002亦不可用→Kill Switch自动触发全系统交易暂停。 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3286 | 先报告后交易铁律 Report Before Trade | 未完成程序化交易报告确认前C-002执行域拒绝发送任何订单 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3287 | Saga超时硬约束 Saga Timeout Hard Constraint | > Saga超时硬约束：整个Saga执行时间≤5s。补偿必须幂等。Saga状态持久化至Redis Stream。 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3288 | Kill-Switch五层防御架构 Kill Switch 5-Layer Defense | 策略层→风控引擎层→执行层→网关层→交易所端控制 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3289 | Level-2数据需求 Level-2 Data Requirement | 逐笔委托+逐笔成交+十档行情需券商额外权限当前未开通 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3290 | 止损减仓允许 Stop Loss Reduction Allowed | > 止损减仓允许(风控减仓)，策略Distressed Selling(追跌卖出)禁止。 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3298 | P2子模块暂不纳入骨架 | - **P2子模块暂不纳入骨架**：XS-07~10/15/16/EXT-01~05，Phase 2+按需建设 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3299 | 路由降级 Route Degradation | > 路由降级：miniQMT连接中断→Close-Only Mode(只允许卖出，不允许买入)，直到连接恢复。 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3300 | 路由Agent反思频率 Reflection Frequency | 执行层低频仅异常时触发正常成交不反思~80%token节省 | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3301 | Hot平面10ms延迟预算 | 覆盖Tick间全部风控+执行需求miniQMT Tick间隔3s | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3302 | miniQMT个人账户限制 | 不可用券商端VWAP/TWAP算法交易+篮子交易+银证转账API+融资融券API | D_EX_SOR | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（84 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0236 | Smart Order Router 智能订单路由 | XS 01 Smart Order Router ✅ 智能订单路由器(简化版A股单市场) | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0237 | Broker Adapter 适配器 | / XS-02 / Broker Adapter / ✅ / 项目内有蓝图编号MOD-L05-001已建设 / 多券商API统一适配 / | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0238 | Market Impact Modeler 模型 | / XS-03 / Market Impact Modeler / ❌ / 门禁：需Level-2实时数据+高频交易环境 / Almgren-Chriss市场冲击建模 / | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0239 | Execution Scheduler 调度器执行 | / XS-04 / Execution Scheduler / ✅ / / TWAP/VWAP/IS算法调度 / | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0240 | Broker API Connector 券商API连接器 | / XS-13 / Broker API Connector / ✅ / / 券商API连接器REST/FIX / | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0656 | C-026 API行为监控 API Behavior Monitor | 监控API行为路由域抽象券商接口 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0707 | Smart Order Router 智能订单路由器 | 智能订单路由多交易所路由最优执行流动性检测路由策略路由回测 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0708 | Execution Algorithm Engine 执行算法引擎 | 执行算法引擎VWAP TWAP POV IS算法选择参数优化算法回测 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0709 | Market Impact Estimator 市场冲击估算器 | 市场冲击估算器Almgren-Chriss参与率临时永久冲击冲击成本预测 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-0710 | Liquidity Detector 流动性检测器 | 流动性检测器买卖价差深度参与率流动性评分流动性预测 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1403 | Order Book Simulator 订单簿仿真器 | 订单簿重建+事件回放+仿真引擎+指标计算 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1404 | RL Execution Training Env RL执行训练环境 | 执行策略RL训练环境+奖励函数库+策略训练+评估 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1405 | Low-Latency Data Handler 低延迟数据处理器 | 行情解析+订单簿维护+UDP组播+时间序列缓存 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-1406 | Low-Latency Path Optimizer 低延迟路径优化器 | CPU亲和性+NUMA绑定+内存池+无锁队列→<1μs抖动 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1407 | Algo Execution Selector 算法执行选择器 | 订单特征→自动选择最优算法+算法推荐+效果评估 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1408 | Adaptive Routing Optimizer 自适应路由优化器 | 路由决策历史→ML→路由策略持续优化 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1409 | Exchange API Rate Limiter 交易所API限速器 | Token Bucket/Leaky Bucket→API调用限速+排队 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1410 | API Doc Auto Version Syncer API文档自动版本同步器 | API变更检测+Diff+适配器更新 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1411 | API Route & Service Discovery API路由与服务发现 | 端点注册+服务发现+负载均衡+故障转移 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1412 | Slippage Analyzer 滑点分析器 | 滑点分析+滑点归因+滑点预测+基准比较 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1413 | Execution Quality Scorer 执行质量评分器 | 执行质量评分+价格/时间/成本/市场影响多维评估 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1414 | Transaction Cost Optimizer 交易成本优化器 | 交易成本优化+佣金+印花税+冲击成本+机会成本 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1415 | Multi-Framework Strategy Router 多框架策略路由器 | Backtrader/Freqtrade/VeighNa三框架策略执行路由 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1416 | Multi-Exchange Optimal Router 多交易所最优路由器 | 多交易所智能订单路由+自适应路由 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2097 | SOR Agent 路由Agent | 执行层路由Agent智能路由拆单策略滑点控制 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2132 | Smart Routing 智能路由 | 路由Agent技能智能路由ACTIVE | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-2133 | Order Splitting 拆单策略 | 路由Agent技能拆单策略ACTIVE | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2971 | Order Routing 订单路由 | 订单路由 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3150 | XS-05 Algo Trading Engine 算法交易引擎 | / XS-05 / Algo Trading Engine / 算法交易引擎：TWAP/VWAP/ICEBERG/POV/Implementation Shortfall/ALT+算法注册表+参数优化器 / P1 / ①可建 / — / | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3151 | XS-06 Venue Selector 交易场所选择器 | 成本/流动性/延迟多维加权评分最优执行场所 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3155 | execution-sor 路由Agent | 智能路由拆单策略滑点控制 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3156 | 路由Agent熔断器 | 路由决策3次/5分钟失败率熔断 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3157 | CB-002 miniQMT下单熔断器 | miniQMT下单>5%持续15s熔断 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3158 | CB-001 iFind数据拉取熔断器 | iFind数据拉取>10%持续30s熔断 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3159 | Close-Only Mode 仅平仓模式 | miniQMT连接中断→仅允许卖出 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3169 | trading_core P3交易核心进程 | 风控检查订单构建miniQMT下单持仓同步 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3170 | xtquant miniQMT接口库 | xtdata行情模块+xttrader交易模块 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3171 | XtMiniQmt.exe 极简模式进程 | 必须运行XtMiniQmt.exe极简模式进程 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3172 | XTP/CTP/OKX 券商API | API版本迁移适配XTP/CTP/OKX | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3173 | FIX 4.2 协议 | 券商对接用FIX协议降低耦合 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3174 | L1全局限流 | 所有外部API合计出站请求滑动窗口50QPS | D_EX_SOR | harvest待评估（uncertain） |  |
| CAND-HARVEST-3175 | L2外部系统级限流 | miniQMT/iFind/LLM各自令牌桶 | D_EX_SOR | harvest待评估（uncertain） |  |
| CAND-HARVEST-3176 | L3操作级限流 | 分时段+分操作类型令牌桶 | D_EX_SOR | harvest待评估（uncertain） |  |
| CAND-HARVEST-3177 | L4优先级限流 | 交易>风控>行情>因子>通知优先级队列 | D_EX_SOR | harvest待评估（uncertain） |  |
| CAND-HARVEST-3182 | Almgren-Chriss最优执行框架 | 临时冲击η+永久冲击γ+风险厌恶λ+参与率上限 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3183 | TWAP算法 TWAP Algorithm | 时间加权平均价格算法 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3184 | VWAP算法 VWAP Algorithm | 成交量加权平均价格算法 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3185 | ICEBERG算法 ICEBERG Algorithm | 冰山订单算法隐藏大单 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3186 | POV算法 POV Algorithm | 参与率算法Percentage of Volume | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3187 | Implementation Shortfall算法 IS Algorithm | 执行差额算法 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3188 | ALT算法 Aggressive Liquidity Taking | 激进流动性摄取算法 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3189 | VPIN 订单流毒性 | VPIN>阈值→暂停买入执行 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3190 | LOB不平衡度 | 买盘深度vs卖盘深度→短期价格方向 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3191 | LOB恢复速度 | 大单吃掉后多久恢复→恢复慢=冲击成本高 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3192 | Hawkes过程 | 订单到达自我激发和交叉激发→预测短期订单流 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3193 | 做市商行为推断 Market Maker Behavior Inference | 订单簿中大单挂单/撤单模式分析 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3194 | DQN强化学习执行 | DQN离散动作强化学习执行 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3195 | PPO强化学习执行 | PPO连续动作强化学习执行 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3201 | L0 正常降级等级 | 全功能运行全部策略活跃 | D_EX_SOR | harvest待评估（uncertain） |  |
| CAND-HARVEST-3202 | Sniper→ALT 主观交易经验映射 | 主观狙击→量化标准激进流动性摄取 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3203 | HYDRA-EI→HMARL 主观交易经验映射 | 自定义框架名→学术标准分层多智能体强化学习 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3204 | Smart→Optimal/Adaptive 主观交易经验映射 | 语义模糊智能→精确最优/自适应 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3205 | 踏空追高→FOMO Entry 主观交易经验映射 | 主观情绪→行为金融学标准术语 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3206 | 被套补仓→Underwater Averaging Down 主观交易经验映射 | 主观经验→量化标准水下加仓摊薄 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3207 | 亏损报复→Revenge Trading 主观交易经验映射 | 主观情绪→行为金融学标准术语 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3208 | 盈利骄傲→Overconfidence 主观交易经验映射 | 主观情绪→行为金融学标准术语过度自信 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3209 | 做T→Intraday Round-trip Trading 主观交易经验映射 | A股特有术语→量化标准日内往返交易 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3210 | 追跌卖出→Distressed Selling 主观交易经验映射 | 主观经验→量化标准恐慌性卖出 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3211 | 保命轨→Emergency Survival Track 主观交易经验映射 | 口语化→量化标准紧急生存轨道 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3212 | 仅平仓→Close-Only Mode 主观交易经验映射 | 口语化→量化标准仅平仓模式 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3213 | Backtrader框架 | 多框架策略执行路由之一 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3214 | Freqtrade框架 | 多框架策略执行路由之一 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3215 | VeighNa框架 | 多框架策略执行路由之一 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3285 | Fail-Closed 合规规则引擎不可用机制 | > Fail-Closed：合规规则引擎不可用→C-004默认拒绝所有订单→C-002亦不可用→Kill Switch自动触发全系统交易暂停。 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3286 | 先报告后交易铁律 Report Before Trade | 未完成程序化交易报告确认前C-002执行域拒绝发送任何订单 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3287 | Saga超时硬约束 Saga Timeout Hard Constraint | > Saga超时硬约束：整个Saga执行时间≤5s。补偿必须幂等。Saga状态持久化至Redis Stream。 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3288 | Kill-Switch五层防御架构 Kill Switch 5-Layer Defense | 策略层→风控引擎层→执行层→网关层→交易所端控制 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3289 | Level-2数据需求 Level-2 Data Requirement | 逐笔委托+逐笔成交+十档行情需券商额外权限当前未开通 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3290 | 止损减仓允许 Stop Loss Reduction Allowed | > 止损减仓允许(风控减仓)，策略Distressed Selling(追跌卖出)禁止。 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3298 | P2子模块暂不纳入骨架 | - **P2子模块暂不纳入骨架**：XS-07~10/15/16/EXT-01~05，Phase 2+按需建设 | D_EX_SOR | harvest待评估（uncertain） |  |
| CAND-HARVEST-3299 | 路由降级 Route Degradation | > 路由降级：miniQMT连接中断→Close-Only Mode(只允许卖出，不允许买入)，直到连接恢复。 | D_EX_SOR | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3300 | 路由Agent反思频率 Reflection Frequency | 执行层低频仅异常时触发正常成交不反思~80%token节省 | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3301 | Hot平面10ms延迟预算 | 覆盖Tick间全部风控+执行需求miniQMT Tick间隔3s | D_EX_SOR | harvest待评估（likely_new） |  |
| CAND-HARVEST-3302 | miniQMT个人账户限制 | 不可用券商端VWAP/TWAP算法交易+篮子交易+银证转账API+融资融券API | D_EX_SOR | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0236 | Smart Order Router 智能订单路由 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0237 | Broker Adapter 适配器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0238 | Market Impact Modeler 模型 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0239 | Execution Scheduler 调度器执行 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0240 | Broker API Connector 券商API连接器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0656 | C-026 API行为监控 API Behavior Monitor | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0707 | Smart Order Router 智能订单路由器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0708 | Execution Algorithm Engine 执行算法引擎 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0709 | Market Impact Estimator 市场冲击估算器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0710 | Liquidity Detector 流动性检测器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1403 | Order Book Simulator 订单簿仿真器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1404 | RL Execution Training Env RL执行训练环境 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1405 | Low-Latency Data Handler 低延迟数据处理器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1406 | Low-Latency Path Optimizer 低延迟路径优化器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1407 | Algo Execution Selector 算法执行选择器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1408 | Adaptive Routing Optimizer 自适应路由优化器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1409 | Exchange API Rate Limiter 交易所API限速器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1410 | API Doc Auto Version Syncer API文档自动版本同步器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1411 | API Route & Service Discovery API路由与服务发现 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1412 | Slippage Analyzer 滑点分析器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1413 | Execution Quality Scorer 执行质量评分器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1414 | Transaction Cost Optimizer 交易成本优化器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1415 | Multi-Framework Strategy Router 多框架策略路由器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1416 | Multi-Exchange Optimal Router 多交易所最优路由器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2097 | SOR Agent 路由Agent | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2132 | Smart Routing 智能路由 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2133 | Order Splitting 拆单策略 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2971 | Order Routing 订单路由 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3150 | XS-05 Algo Trading Engine 算法交易引擎 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3151 | XS-06 Venue Selector 交易场所选择器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3155 | execution-sor 路由Agent | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3156 | 路由Agent熔断器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3157 | CB-002 miniQMT下单熔断器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3158 | CB-001 iFind数据拉取熔断器 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3159 | Close-Only Mode 仅平仓模式 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3169 | trading_core P3交易核心进程 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3170 | xtquant miniQMT接口库 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3171 | XtMiniQmt.exe 极简模式进程 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3172 | XTP/CTP/OKX 券商API | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3173 | FIX 4.2 协议 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3174 | L1全局限流 | D_EX_SOR | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3175 | L2外部系统级限流 | D_EX_SOR | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3176 | L3操作级限流 | D_EX_SOR | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3177 | L4优先级限流 | D_EX_SOR | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3182 | Almgren-Chriss最优执行框架 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3183 | TWAP算法 TWAP Algorithm | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3184 | VWAP算法 VWAP Algorithm | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3185 | ICEBERG算法 ICEBERG Algorithm | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3186 | POV算法 POV Algorithm | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3187 | Implementation Shortfall算法 IS Algorithm | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3188 | ALT算法 Aggressive Liquidity Taking | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3189 | VPIN 订单流毒性 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3190 | LOB不平衡度 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3191 | LOB恢复速度 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3192 | Hawkes过程 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3193 | 做市商行为推断 Market Maker Behavior Inference | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3194 | DQN强化学习执行 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3195 | PPO强化学习执行 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3201 | L0 正常降级等级 | D_EX_SOR | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3202 | Sniper→ALT 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3203 | HYDRA-EI→HMARL 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3204 | Smart→Optimal/Adaptive 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3205 | 踏空追高→FOMO Entry 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3206 | 被套补仓→Underwater Averaging Down 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3207 | 亏损报复→Revenge Trading 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3208 | 盈利骄傲→Overconfidence 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3209 | 做T→Intraday Round-trip Trading 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3210 | 追跌卖出→Distressed Selling 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3211 | 保命轨→Emergency Survival Track 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3212 | 仅平仓→Close-Only Mode 主观交易经验映射 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3213 | Backtrader框架 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3214 | Freqtrade框架 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3215 | VeighNa框架 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3285 | Fail-Closed 合规规则引擎不可用机制 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3286 | 先报告后交易铁律 Report Before Trade | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3287 | Saga超时硬约束 Saga Timeout Hard Constraint | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3288 | Kill-Switch五层防御架构 Kill Switch 5-Layer Defense | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3289 | Level-2数据需求 Level-2 Data Requirement | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3290 | 止损减仓允许 Stop Loss Reduction Allowed | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3298 | P2子模块暂不纳入骨架 | D_EX_SOR | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3299 | 路由降级 Route Degradation | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3300 | 路由Agent反思频率 Reflection Frequency | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3301 | Hot平面10ms延迟预算 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3302 | miniQMT个人账户限制 | D_EX_SOR | 候选待评（candidate） | harvest待评估（likely_new） |
