---
ttl: task_bound
title: 深度审查报告——卖出信号融合引擎（E01）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：卖出信号融合引擎（E01）

- 状态: **已审**
- 级别: P1｜类型: 卖出族信号融合
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- **裁定#309 约束声明**：ruling_registry.yaml:3833-3839（2026-09-17）"卖出族 12 件待裁定整族挂起"——本审查照常进行（产出=数据），任何施工修复受裁定约束（MVP 三件套 ATR+移动止损/移动止盈/一次性退出维持生产；密度感知/分批/时间加权等依赖就绪前不启用）。
- 入口锚点: `src/zephyr/sell_decision/core/sell_signal_fusion_engine.py:278(fuse)/:314(_fuse_one)/:210(WeightedAverageFusion)`
- 接线现状（grep 实证）：**包外零导入**——全仓 `SellSignalFusionEngine` 引用仅 core 自身+`sell_decision/core/__init__.py` 再出口；无 scheduler/pipeline/api/orchestrator 消费。包内链路=collector(SELL-01)→本件(007)→仲裁器(008)/紧迫度(009)（头注声明的 D-POSITION/D-SIGNAL 消费方均"规划中"）。挂起态=结构性空转，与裁定#309 一致。
- 测试文件: tests/sell_decision/test_sell_signal_fusion_engine.py
- 材料包缺项: 运行时证据不适用（生产无调用=无运行痕迹可查，本身就是发现）

## 1 对象快照

- 范围：融合主流程（分组→加权融合→共振增强→一致性→事件发布）、WeightedAverageFusion 策略、FusionStrategy 注入协议。排除：sell_signal_collector（上游 SELL-01）。
- 测试覆盖概况：专测文件在位；用例映射见 §2 A.3。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **单信号即 HIGH 一致性**：单标的仅 1 条信号时 max_ratio=1.0>0.8→HIGH→因子 1.0，无佐证不折减置信度——"孤立强信号"与"多框共振"在置信度上同权，与"一致性检查"的本意（多信号互证）相悖 | sell_signal_fusion_engine.py:384-398, :325 | **P2** | fuse 单信号 confidence=0.9 → confidence 输出 0.9 无折减 |
| A | `confidence = willingness × consistency_factor`：置信度是意愿的确定性缩放（:325），两者强相关非独立维度——下游若按"高意愿+高置信"双条件筛选，条件实为同一个数×档位系数；策略 fuse 返回的 raw_conf 被丢弃（:319 `_raw_conf`） | sell_signal_fusion_engine.py:319, :325-326 | P3 | 读 fuse 返回值消费链 |
| A | 加权平均分母 Σweights 已含共振 boost（:355-360 权重先行增强），与 docstring 公式一致（:26）；空表/Σw≤0 返回 (0,0) 静默零意愿（:221-225）——空表在 fuse 主入口已抛 InvalidFusionInputError（:294-295），双入口行为不一致但主入口 fail-loud | sell_signal_fusion_engine.py:220-229, :294-295 | 已查无 | — |
| A | 输入 confidence 假设 [0,1] 未在本件 clamp（SellSignal 契约在上游 collector）——越界值经加权平均+clamp 兜住（:227），方向安全 | sell_signal_fusion_engine.py:227 | P3 | 上游契约依赖，建议本件断言 |
| A | 共振判定：同方向+不同 timeframe+双方非 UNKNOWN（:370-380）；`s is not sig` 身份比较——同 timeframe 重复信号不共振（正确）；timeframe 缺失（UNKNOWN）永远不增强（保守） | sell_signal_fusion_engine.py:369-380 | 已查无 | — |
| A.3 | 专测文件在位（tests/sell_decision/test_sell_signal_fusion_engine.py）；断言覆盖度抽读见长尾——挂起态下测试仅验证孤儿正确性 | tests/sell_decision/ | P3 | pytest 该文件观察 |
| B | 上游 SellSignal（collector SELL-01）confidence/direction/timeframe 语义契约：本件未校验，信任上游；上游错→本件静默带病融合（无 per-signal sanity check） | sell_signal_fusion_engine.py:298-300 | P3 | 构造 direction=None 观察行为 |
| C | **爆炸半径=零（结构性孤儿）**：包外零调用方（见头注接线现状）；头注 CONSUMERS（MOD-SELL-008/009、D-POSITION、D-SIGNAL）在包内可指认（sell_urgency_scorer.py:57 消费仲裁器；仲裁器消费 collector），但整链无生产入口——checklist #8 孤儿死码模式，空转时长与 #309 挂起一致 | grep 全仓实证 | **P1（族级结构性）** | `grep -rln "sell_decision" --include="*.py" src scripts \| grep -v sell_decision` 零命中 |
| C | 单标的融合异常=该标的静默从结果消失（:308-309 仅 log），调用方无法区分"无信号"vs"融合失败"——若未来接电，此为静默吞掉点 | sell_signal_fusion_engine.py:302-310 | P3 | 接电前需返回失败标记 |
| D | 兄弟实现：紧迫度 scorer（sell_urgency_scorer.py:317 行）独立对信号再打分——两套打分语义（fusion 意愿 vs urgency 紧迫度）分工声明在 blueprint；一致性因子表/类型权重表仅此一份，无双承载 | 全仓 grep 权重表 | 已查无 | — |
| D | `_method_of_strategy` 自定义策略恒归 WEIGHTED_AVG（:402-406）——方法枚举与实际策略可漂移（BAYESIAN/D-S 注入后仍标 WEIGHTED_AVG），审计字段失真 | sell_signal_fusion_engine.py:402-406 | P3 | 注入自定义 strategy 看输出枚举 |
| E | 重放/重入：无状态纯函数+clock 注入（:263-267），同输入同输出；事件回调异常隔离（:422-426）——回调失败仅 log，订阅方无重试通道（接电前须知） | sell_signal_fusion_engine.py:410-426 | P3 | — |
| E | A 股口径：跌停日卖出意愿照常融合——"跌停无法成交"的执行面约束不在本层（执行规划器域），接电后若意愿驱动下单需下游兜口（T+1/跌停流动性）；本件无时区问题（UTC clock，仅时间戳） | 设计边界 | P3（接电前置项登记） | — |

## 3 SOTA 对照

1. **信号融合（对等已有）**：置信度加权平均+多源一致性折扣是证据融合基线做法；贝叶斯/D-S 证据理论为教科书升级路径（本件已预留协议位，FusionStrategy :159-175）。对照：Dempster-Shafer 证据理论在多传感器融合的标准地位（经典文献；工程实现参考 scipy/statsfeeds 无单一权威 URL，此处按"对等已有"登记不另立卡）。
2. **多时间框架共振（对等已有）**：MTF confluence 加权是技术分析交易系统常见做法（多时间框架确认，QuantStart 技术分析系列口径，https://www.quantstart.com/articles/）；×1.5 线性 boost 为项目自定参数（proposed 面声明于 blueprint）。
3. 结论：**对等已有**，无立卡项；真问题是接线性不是算法。

## 4 缺陷清单

1. **[P1-族级] 整族结构性孤儿（接线现状，非本件代码缺陷）**——现状：包外零导入，生产零调用；证据：全仓 grep（见头注）；影响：算法再对也不产生决策，#309 挂起态的机械印证；建议：依赖裁定#309 的依赖达成评审队列决定接电或退役清点；验证法：grep 复现。
2. **[P2] 单信号 HIGH 一致性无佐证折减**——证据 ：384-398, :325；影响：接电后孤立信号全权驱动意愿；建议：n==1 时封顶 MEDIUM（0.8 因子）或 Owner 裁定单信号语义；验证法：单信号 fuse 用例。
3. **[P3] confidence 与 willingness 非独立维度**（:319, :325）——建议：docstring 明示置信度=意愿×档位，下游双条件筛选改单条件+档位；验证法：数值演示。
4. **[P3] 单标的融合失败静默短列表**（:308-309）——建议：失败标记进结果或事件；验证法：注入异常信号。
5. **[P3] 融合方法枚举对自定义策略失真**（:402-406）；验证法：注入策略看输出。
6. **[P3] 跌停/T+1 执行面约束不在本层**——接电前置项登记（执行规划器 E 族兄弟域）；验证法：读 sell_execution_planner 职责。

## 5 挂起疑问

1. 接电路径归裁定#309：本件属"MVP 三件套"还是"待依赖"档？裁定文本未逐件点名（12 件清单载体在别处），需 Owner 在依赖评审时对号。
2. 类型权重表（:184-193）的数值依据（1.5/1.2/1.0/0.8/0.6）无出处锚——蓝图断言 or 拍脑袋，接电前应给依据或标 proposed。
3. resonance_boost=1.5 与一致性因子 0.8/0.5 的乘积效应未做敏感性分析。

## 6 完备性自评

- 六轴全查：是（C 轴以全仓 grep 实证替代运行时证据——生产无调用即证据本身）。
- 长尾：①sell_signal_collector 上游契约细节（另一对象）；②tests 断言逐条强度未全读（挂起态下优先级降）；③blueprint.md 文档面未逐条反查（#309 挂起态文档冻结）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
