---
ttl: task_bound
title: 深度审查作业簿——加仓资格门
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：加仓资格门（P67）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/pyramiding_rules.py:145`（check_pyramiding_eligibility）/:193（plan_pyramid_addition）
- TDM 节点: TDM-P-P3-01（stage，config/trading_decision_map.yaml:2933，C9 施工回填 MOD-POS-027；同模块覆盖 P3-02 金字塔规则）
- 生产调用方: **零**（header 自认 [MATURITY] design+human_gated+"P 流加仓链（待接线）"——声明诚实）
- 测试文件: tests/position/test_pyramiding_rules.py（63 passed 同批）

## 1 对象快照

- 范围：pyramiding_rules 全文件（241 行）——P3-01 资格四重门（浮盈红线/情绪段/亲和度/熔断禁加，逐门短路带 reason 码）+P3-02 金字塔三规则（递减 1/2 剩余预算/阶梯 2.5%/限次 3/跌破上次加仓价停/重新确认旗标）；Decimal-only 分笔金额。
- 排除项：defensive_asset_whitelist（L2/L3 窄门，分工声明 ：30-32）；position_sizing_engine（首仓 sizing）。
- 测试覆盖概况：四门短路/三规则/Decimal 纪律覆盖好（63 passed）；无 L1 熔断级行为断言（恰为本报告口径发现）。
- 材料包缺项声明：运行时证据包未取（design 态）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **熔断禁加门与 M-36/D112 收口口径冲突（checklist #15 同族）**：TDM-P-P3-01 注释载 M-36 收口（D112）：「全系统'熔断禁加期'统一定义=R1-01 状态机 **L1 及以上**持续期间（P3-01 资格门④消费本节点输出）」；本模块门④只禁 L2/L3/L4（_CIRCUIT_BAN_LEVELS，:79-81,167-168），**L1（日亏≥2% 警戒）放行加仓**——收口裁定的"统一定义"未落码，且模块注释自称"同真源=X-R1-01 熔断五级"却选择了与裁定相反的子集；TDM 正文 gate④ 文本"日亏 4% 熔断触发时全禁"（=L2）与 M-36 新裁（L1 及以上）本身也存在新旧文不一致 | pyramiding_rules.py:79-81,166-168 vs config/trading_decision_map.yaml:2933-2976（gate④ 文本+M-36 注释） | P2 | 读 _CIRCUIT_BAN_LEVELS 对照 M-36 文本；L1 输入跑 check_pyramiding_eligibility 看 ALLOWED |
| A | 金字塔数学与 TDM 逐条对齐（已核）：递减=剩余预算×1/2（首加 50%/次加 25%/三加 12.5%，几何尾差 12.5% 留存=设计内）；阶梯=现价≥上次加仓价×1.025（禁平加）✓；限次 3 ✓；跌破上次加仓价停（调用方传入旗标，纯函数纪律）✓；Decimal ROUND_DOWN 分笔精确 ✓；重新确认旗标仅约束第 2 笔起 ✓ | pyramiding_rules.py:193-241 | —（已核） | — |
| A | 红线门①与 P68 限仓执行器的禁补亏损仓双实现口径冲突：本模块=现价≤成本即拒（**任何亏损**禁补，与 BM-BUY-08 红线字面一致）；position_limit_enforcer=亏损>8% 才 Hard Block（:347 threshold 0.08）——**同一红线两处承载、阈值语义不同（0 亏损 vs 8% 亏损）**，接线后两关卡口结果可矛盾（亏损 5% 仓：P67 拒/P68 放）（checklist #4 双承载漂移） | pyramiding_rules.py:158-159 vs position_limit_enforcer.py:136,345-357 | P2 | 亏损 5% 仓分别跑两件对比裁决 |
| B | 情绪段/亲和度/熔断级全部由调用方注入无来源校验：情绪段判定真源（情绪周期轴）与亲和度计算（28 号）的接入口不在本件——design 态可接受，接线时需锁定数据源防"自由注入" | pyramiding_rules.py:5,113-120 | P3 | 读蓝图数据源登记 |
| A(亮点) | 四门逐门短路留 GateCode（可审计可单测）；浮盈红线门序第一（代价最高的错误最先拦）；Decimal-only 拒 float（金额精度纪律，宪法 §11 同向）；CircuitLevel 复用同域枚举防第二定义（:41-42 自注）；惰性配置工厂零副作用 | pyramiding_rules.py:61-73,104-109,137-142 | — | — |

## 3 SOTA 对照

- 金字塔加仓三规则（递减/阶梯/限次）：**对等已有**——趋势跟随经典教义：只在盈利方向加仓、每次加仓量递减（Livermore 1/4 法则、Turtle 1/2 递减）（TurtleTrader《Average Up, Never Down》turtletrader.com，经典文献持续引用；Traders Second Brain Pyramiding Guide，traderssecondbrain.com，2025-2026；Investopedia Pyramiding 词条，investopedia.com，2026）。本模块 1/2 递减+2.5% 阶梯+3 次限次与教义同构且更保守。
- 禁补亏损仓（averaging down 禁令）：**对等已有**——"Pyramiding scales into strength; averaging down reinforces a losing decision" 为趋势跟随共识（QuantStrategy: Pyramiding vs Averaging Down，quantstrategy.io，2026；同上 TurtleTrader）。**教义是绝对禁令**——本模块（零亏损即拒）符合教义，P68 的 8% 容忍版偏离教义（矛盾归 P67/P68 双承载发现，修 P68）。
- 情绪段权限门（点火/扩张才加仓）：**对等已有（项目内自洽）**——情绪周期五段轴为项目自有体系（28 号），无外部对照必要。

## 4 缺陷清单

1. **[P2] 熔断禁加门漏 L1，违反 M-36/D112 收口"统一定义"**。建议修法：_CIRCUIT_BAN_LEVELS 收入 L1（或 Owner 复核 M-36 后改裁定文本——但收口裁定优先于代码，默认修代码）；补 L1 禁加回归测试。验证法：L1 探针。
2. **[P2] 禁补亏损仓红线双承载双口径（本件 0 亏损 vs P68 8% 亏损）**。建议修法：红线唯一真源落 P67 门①（教义一致），P68 的 loss_add_block 降级为 P4 告警或对齐 0 阈值；两件注释互挂分工。验证法：亏损 5% 对比探针。
3. **[P3] 注入数据源（情绪段/亲和度）无接入口径**。建议修法：接线批次锁定数据源并登记蓝图。验证法：读蓝图 diff。

## 5 挂起疑问

- M-36（L1 及以上禁加）与 TDM gate④ 原文（4%=L2 才禁）的新旧文不一致请 Owner 确认最终口径——本报告按"收口裁定优先"建议修代码收 L1。
- 几何尾差（3 次加仓后剩余 12.5% 预算永久留存）是否符合预算管理预期（vs 用尽式分配）——设计细节待接线时定。

## 6 完备性自评

六轴全查（A 数学四问：递减几何/阶梯乘法/量化精度逐个过、边界=零预算/首加/限额已测；B 上游=注入契约已查（缺口已记）；C 下游=零调用方判孤儿（design 诚实）；D=与 P3-01/P3-02 两节点对账+与 defensive_asset_whitelist/position_sizing_engine 分工核读+与 P68 双承载（主发现）；E 五问：静默失败=无（fail-closed 全面）、假阳性=无、断供=不适用、重复触发=纯函数幂等、时序=无时钟）。长尾：①defensive_asset_whitelist 门④联动（P70 对象）互查；②28 号策略亲和度计算未审；③情绪周期轴判定未审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
