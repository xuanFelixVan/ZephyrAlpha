---
ttl: task_bound
title: 深度审查作业簿——C1收缩对比runner
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：C1收缩对比runner（B16）

- 状态: **已审**
- 级别: P1｜类型: 管线
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/regime_validation/c1_runner.py:96`（build_volatility_schedule）/:173（run_c1_with_provider）
- 生产调用方: **src 内零调用**；运维脚本调用=scripts/tests/repro_c1.py、repro_c1_deadzone.py、run_c1_shrinkage_validation.py、validate_overlay_gated.py、dump_c1_repro_artifacts.py。头部 [CONSUMERS] 指向 `scripts/regime/run_c1.py`——**该路径不存在**（scripts/regime/ 目录无）
- 测试文件: tests/backtest/test_c1_runner.py（18 用例实跑全绿）
- 变更热力: 8 commits/3.5 月（8 对象中第二高）——mock/regime 双模式+落盘+tracking 多轮演进
- 备注: 11 号 memo Phase 1 C1 一票否决执行层；mock 模式防误用警示已内置

## 1 对象快照

- 审查范围：全文件 533 行——波动率调度构造、三入口（provider/mock/regime）、端到端、报告落盘、空结果构造。
- 排除项：C1ShrinkageComparator.compare 四项一票否决数学（c1_comparator 另件）；MockShrinkageProvider/ScheduleShrinkageProvider 内部（shrinkage_provider 另件）；RegimeSeriesOrchestrator（MOD-REGIME-002 未接）。
- 材料包缺项声明：真实 C1 报告产物分布未拉（scripts/tests 产物在 data 侧，本轮以代码审为主）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | build_volatility_schedule 数学正确：等权截面日收益→rolling(20).std()（pandas 默认 ddof=1，后视窗口）×√252 年化——**无前视**；dropna+isfinite 过滤 ✓；空 data/缺 close 列→空 dict ✓ | :116-136 | 通过 | 读码+单测；rolling 后视语义为 pandas 默认 |
| A | unstack 三分支兼容（symbol/trade_date/末级 level）：重复 (symbol,date) 索引会抛 ValueError（fail-visible 非静默）✓；但 `unstack(level=-1)` 兜底分支对既无 symbol 又无 trade_date 的索引语义含糊（可能把日期当 symbol 展开成错误面板）——当前调用链来自 StrategyRunner（MultiIndex 规整），实际不触发 | :119-126 | P3 | 构造无 MultiIndex 名的 close 测 |
| A | 空 vol_schedule→告警"实验组退化满部署（C1 无意义）"仍跑对比——流程跑通但结论无意义，靠日志+mock 报告头警示兜底（mock 警示 #ARCH-REGIME-C1-RUNNER-001 裁定②已落地）✓ 诚实 | :256-258; :413-422 | 通过 | 读码 |
| A | 空数据→passed=False 空结果不抛（与 ERROR_CONTRACT"数据/信号为空->返回空 C1ComparisonResult(不抛)"一致）✓ | :206-208,482-521 | 通过 | 对照 :13 契约 |
| A.3 | 18 用例断言强——**信任** | tests/backtest/test_c1_runner.py | 通过 | 实跑全绿 |
| B | regime 模式输入=预计算 [(date, ShrinkageResult)]，PIT as-of join 声明由 ScheduleShrinkageProvider 承担（本件只编排）——**本件对 regime_results 的时序合法性零校验**（乱序/未来日期序列直接进 provider）；PIT 责任全压给兄弟件，登记跨件契约 | :277-315 | P3 | 读 build_schedule_from_results 调用（内部归 provider 件） |
| C | 消费方全列见头部；C1ComparisonResult→报告 md+experiment_tracking（失败不崩业务，:157-165 双层 try）✓；爆炸半径=Phase 1 裁定依据（regime 模式）+冒烟验证（mock 模式） | :144-165 | 说明 | — |
| C | **孤儿裁定：无 src 生产调用方**；运维/repro 脚本真实调用中；头部声称的 `scripts/regime/run_c1.py` 是死指针（路径不存在）。与 [MATURITY]=production 组合后，"Phase 1 裁决依据"的执行入口实际是手工脚本 | scripts/tests/* 实存；scripts/regime/ 不存在 | P3 | `ls scripts/regime/` 空；`ls scripts/tests/run_c1_shrinkage_validation.py` 存在 |
| D | 兄弟分工：依赖方向 backtest→regime 单向（#ARCH-REGIME-VALIDATION-001）经 lazy import 落实 ✓；tracking 循环依赖用函数内 import 破环 ✓ | :151-165,352-353 | 通过 | — |
| D | **"报告落盘幂等"与 now() 矛盾**：save_c1_report 写入 `datetime.now()` 生成时间（:411），同输入两次落盘字节不同——头部不变量"报告落盘幂等：同输入同输出"（:8,41）在字节层面不成立（数值层面成立：C1ComparisonResult 不可变）。语义歧义非实质漂移 | :8,41 vs :411,472 | P3 | 两次 save_c1_report diff |
| E | 五问：无 except 吞点（tracking 双层 try 是"失败不崩业务"显式声明+warning 出声）✓；报告写文本无原子性（write_text 直写，中途崩留半文件——低危）；重复落盘覆盖同名文件（幂等语义自洽）✓；无时序状态机 ✓ | :157-165,472 | 通过 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| regime/vol 状态驱动收缩（防御期降杠杆） | **对等已有（mock 变体）**：波动率分档映射是 regime gating 的最简代理；真实裁决依赖 HMM 概率（本件已声明 mock 无部署决策价值）——业界 regime-switching 资产配置通行做法 | Guidolin & Timmermann regime-switching allocation 系（J. Econometrics 2007 系）；项目内 11 号 memo §4.3 |
| 实现波动率年化（rolling std × √252） | **对等已有**：标准已实现波动率年化口径，无异议 | 常规金融计量口径 |

## 4 缺陷清单

1. **P3｜头部 [CONSUMERS] 死指针**：`scripts/regime/run_c1.py` 不存在，实际调用在 scripts/tests/*；接线地图失真（模式 #14 重构丢路由的温和形态——脚本曾迁移未回头改头）。
2. **P3｜[MATURITY]=production + 零 src 调用方**：当前价值=手工验证执行入口（真实被脚本用，轻于 B10）；Phase 1 真裁决前建议维持 testing 或注明"手工触发"。
3. **P3｜"报告落盘幂等"与 now() 字段矛盾**：建议生成时间改 meta 注入或移出正文。
4. **P3｜unstack 兜底分支语义含糊**（:126）：建议收窄为显式报错。
5. **P3｜regime_results 时序合法性零校验**（:302-304 仅判空）：乱序/未来日期依赖 provider 内 as-of join 兜底，跨件契约宜在本件入口加最小断言（monotonic date）。

## 5 挂起疑问

- C1 四项一票否决的门槛数学在 c1_comparator（他件）——本轮未深查，Phase 1 裁决效力最终取决于该件。
- regime 模式至今是否真跑过（ModRegime002 未接的声明 vs scripts/tests 产物），需拉 data 侧 C1 报告核实。

## 6 完备性自评

- 六轴全查：A（vol 调度逐式+边界）✓ B（provider 供给契约）✓ C（调用方 grep 实锤+死指针）✓ D（依赖方向/幂等声明）✓ E（五问）✓ F（2 条对照）✓。
- 长尾：c1_comparator 四闸数学、shrinkage_provider as-of join 实现（他件对象）；真实报告产物画像。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P3 [CONSUMERS] 死指针: 挂起登记。
- 修复提交: q-0024（B11 冲击腿）。
