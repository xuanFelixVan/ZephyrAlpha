---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——加仓时点与执行
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：加仓时点与执行（P68）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/position/core/position_limit_enforcer.py:218`（PositionLimitEnforcer.check:247）
- TDM 节点: TDM-P-P3-04（stage，config/trading_decision_map.yaml:3033；注释"硬约束预检=MOD-POS-010+cash_manager"——本模块承载预检半边）
- 生产调用方: **零**——PositionLimitEnforcer( 全仓仅自身 docstring（:222）；header 声明的 MOD-POS-001/D-RISK/D-GOVERNANCE 零实际调用
- 测试文件: tests/position/test_position_limit_enforcer.py（63 passed 同批）

## 1 对象快照

- 范围：PositionLimitEnforcer 全文件（387 行）——仓位方案硬约束检查：单票 5%/行业 30%+基准±10%/总仓位/亏损加仓 8% 禁加/压测 15% 告警，5 级否决裁决（P0 KillSwitch 短路>P1 强减>P2 禁新开>P3 禁单笔>P4 告警）。
- 排除项：时点选择与下单执行（TDM 声明的另一半：缩量回调/尾盘窗口/复用建仓执行件——零代码且无其他承载件，见轴 D）；cash_manager（MOD-POS-006）。
- 测试覆盖概况：五级裁决/各约束/短路覆盖（63 passed）；无"未提供基准的行业"场景、无单票上限跨模块一致性场景。
- 材料包缺项声明：运行时证据包未取；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| D | **单票上限三处默认值互相矛盾（checklist #4 双承载漂移，跨对象）**：本模块 single_instrument_cap=**5%**；firm_risk_aggregator SINGLE_NAME_CAP=**8%**（P54）；TDM D94 终裁/RLM-CONCENTRATION-001=**10%**（P3-01 注释"单票默认≤10%已落值"）——同一"单票硬上限"三个默认值，任意接线两件即出矛盾裁决（7% 仓：P68 拒/P54 放/图面 10% 内合规） | position_limit_enforcer.py:132 vs firm_risk_aggregator.py:50 vs config/trading_decision_map.yaml:2964-2966（D94） | P2 | 三处常量并排读；7% 方案分别跑两件 |
| D | **禁补亏损仓红线第二处冲突承载**：本模块 loss_add_block_threshold=8%（亏损>8% 才 P3 Hard Block）vs P67 门①（任何亏损即拒，BM-BUY-08 红线字面+趋势跟随教义）——同一红线两件两口径（详见 P67 报告 §2），接线后亏损 5% 仓加仓两关一拒一放 | position_limit_enforcer.py:136,345-357 vs pyramiding_rules.py:157-159 | P2 | 亏损 5% ADD 分别跑两件 |
| D | **节点"时点+执行"半边零承载**：TDM-P-P3-04 声明「时点二选一（缩量回调守支撑/尾盘窗口 BM-PLAN-02 明日高开概率>70%）+下单复用建仓执行件（分批+限价+硬约束预检）+未成交不追价」——本模块只有硬约束预检；时点判定（BM-PLAN-02 高开概率）与下单编排全仓无承载（grep 缩量回调/尾盘窗口/高开概率 零命中），"未成交不追价"语义归执行层未见声明 | config/trading_decision_map.yaml:3033-3060 vs 模块全文；grep 全仓 | P2 | 对照 TDM 半边逐条 grep |
| A | 行业基准缺省→双侧偏离误报：sector_baselines 缺省空 dict，未提供基准的行业 baseline=0.0 → 任何权重>10% 的行业触发 sector_baseline_deviation 违规（P2 级）；且 abs() 双侧——低配行业（weight 2% vs baseline 8%）同样出 P2_BLOCK_NEW，而裁决语义"否决新开仓"对低配无意义（低配该买入不该被拦） | position_limit_enforcer.py:332-343,173 | P2 | 无 baselines 输入跑 check 看行业违规遍地；低配行业看违规 |
| A | 压测"收紧上限"只出 P4 告警：docstring 声明"压力测试：情景最大亏损>15% → 收紧上限"（:34），代码只 P4_WARN（:359-369）无任何上限收紧动作/参数输出——声明过 claim（checklist #3 轻症） | position_limit_enforcer.py:34,359-369 | P3 | stress_loss=0.2 跑 check 看仅 P4 |
| A | 总仓位>上限→P1 强减合理；但 P1_FORCE_REDUCE 只标记不产出减仓清单（无"减多少"输出）——消费方拿到 P1 后自行决定，模块职责声明止于裁决（可接受，记录语义边界） | position_limit_enforcer.py:289-300 | P3 | 读 LimitCheckResult 字段确认无 reduce 指令 |
| A(亮点) | KillSwitch 短路（P0 最高级优先且不再检查其余，语义干净）；verdict.severity 数值化 worst-of 裁决；配置 (0,1] 域校验；权重/动作验证完备 | position_limit_enforcer.py:84-109,270-287,139-149 | — | — |

## 3 SOTA 对照

- 多级风控否决（KillSwitch>强减>禁开>禁单笔>告警）：**对等已有**——交易风控的五级响应阶梯与机构风控分级一致（30 号 §2.5 drawdown_controller 5 级响应为项目内同构；机构侧 soft-deleveraging 阶梯见 P56 引 breakingalpha/TDM 注）；结构无争议。
- 单票集中度上限：**对等已有**——multi-strategy 单票帽 5-10% 常见（CAIS multi-strategy 框架 caisgroup.com，2025-2026，同 P54/P62 引）；**项目内三值并存（5/8/10）才是缺陷**（轴 D 主发现），外部无单一定值可裁。
- 亏损加仓禁令：**对等已有**——averaging down 禁令是趋势跟随绝对教义（TurtleTrader turtletrader.com；quantstrategy.io，2026，同 P67 引）——8% 容忍版偏离教义，修法见 P67。

## 4 缺陷清单

1. **[P2] 单票上限默认值 5%/8%/10% 三处矛盾**。建议修法：Owner 按 RLM-CONCENTRATION-001（D94=10%）终裁唯一值，三处默认值统一引用同一常量/配置真源（静态清单禁手工维护红线同向）。验证法：三常量并排。
2. **[P2] 禁补亏损仓与 P67 双口径**。建议修法：本件 loss_add_block 阈值对齐 0（或降 P4 告警），红线真源归 P67 门①（详见 P67 §4.2）。验证法：亏损 5% 对比。
3. **[P2] 行业基准缺省误报+低配误拦**。建议修法：baselines 缺失的行业跳过偏离检查（记 baseline_missing，对齐 P54 退化路径先例）；偏离检查单侧化（只查超配）或低配改 P4。验证法：无 baselines 探针。
4. **[P2] 节点时点+执行半边零承载**。建议修法：TDM-P-P3-04 补红注（时点编排未建），或施工批次补 BM-PLAN-02 时点件；"未成交不追价"写入执行层契约。验证法：grep。
5. **[P3] 压测收紧上限过 claim+P1 无减仓清单**。建议修法：改 docstring 为"告警"；P1 输出建议减仓标的列表（按超限幅度排序）。验证法：压测探针。

## 5 挂起疑问

- 单票上限唯一真值（5/8/10%）请 Owner 终裁——本报告倾向 10%（D94 已终裁且 P3-01 注释声明"已落值"），5%/8% 两处属旧默认未同步。
- 时点半边（BM-PLAN-02 高开概率>70% 触发）依赖的"明日高开概率"预测件是否存在（plan_engine 域）——若不存在则该半边是双欠账（时点编排+预测件），宜合并立项。

## 6 完备性自评

六轴全查（A 数学四问：五级阈值/偏离 abs/总仓位求和逐个过、边界=无基准行业/亏损阈/压测已测；B 上游=PositionPlan 契约+baselines 注入已查；C 下游=零调用方判孤儿；D=三处单票上限+两处亏损禁加双承载对账（主发现）+与 cash_manager 分工声明核读；E 五问：静默失败=无（裁决显式）、假阳性=压测过 claim+基准缺省误报、断供=KillSwitch 参数由调用方注入（真源接线未审）、重复触发=check 幂等、时序=clock 注入）。长尾：①cash_manager（MOD-POS-006）未审；②BM-PLAN-02 预测件存在性未证实；③63 测试逐断言抽查级。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
