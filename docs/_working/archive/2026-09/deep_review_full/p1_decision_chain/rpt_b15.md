---
ttl: task_bound
title: 深度审查作业簿——策略验证管线
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：策略验证管线（B15）

- 状态: **已审**
- 级别: P1｜类型: 管线
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/strategy_validation_pipeline.py:67`（StrategyValidationRequest）/:115（run_strategy_validation）
- 生产调用方: src 内零调用；脚本消费=scripts/backtest/eval_f2_narrow_backtest.py、f06_e4_wfa_exam.py（作业簿所记"decision_gate/双引擎"实为**依赖**非调用方：decision_gate.py:5 明示 vectorized/event_driven 引擎内的 evaluate_decision_gate 包装器"实测全仓零调用"）
- 测试文件: tests/backtest/test_strategy_validation_pipeline.py（18 用例实跑全绿）
- 变更热力: 6 commits/3.5 月
- 备注: 薄编排件；本轮主发现=DSR 语义文档漂移（依赖 2026-09-16 车道 L 翻转未回灌）

## 1 对象快照

- 审查范围：全文件 180 行——过拟合三维检测编排、三阶段门控编排、综合裁决。
- 排除项：DecisionGate/OverfittingDetector 内部数学（他件；本轮只核衔接面与默认值语义）。
- 材料包缺项声明：两个脚本消费方的实跑行为未复跑（读码级）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 编排逻辑正确：can_deploy = gate.can_deploy ∧ ¬overfitting.is_overfitting（SIM-56 语义）✓；reasons 汇聚可读 ✓；request 类型/strategy_id 非空校验 ✓ | :135-141,163-171 | 通过 | 读码+单测 |
| A | **DSR 语义文档漂移（主发现）**：本件三处声明"DSR 可选判定器注入（默认关闭）"（:24,80-81,152"gate 未配置阈值时忽略"），但依赖 decision_gate 的 DecisionGateConfig.dsr_threshold **默认=DSR_SIGNIFICANCE_THRESHOLD=0.95 fail-closed**（2026-09-16 车道 L 接线：dsr 未注入→OOS 判不通过）→ **默认参数调用 run_strategy_validation 的 can_deploy 恒 False**，与文档承诺行为相反 | strategy_validation_pipeline.py:24,80-81,152 vs decision_gate.py:404-436（dsr_threshold 默认 0.95 注释）,decision_gate.py:8,98-121（evaluate_dsr fail-closed） | **P2** | 读 decision_gate.py:404-436 默认值与 :114-121 unavailable→passed=False；grep B15 三处"默认关闭" |
| A.3 | 18 用例断言强（编排组合/异常/DSR 分支）——**信任**；但测试是否覆盖"默认 gate+dsr=None → can_deploy=False"这一现实主路径未逐条核（若有断言则文档漂移早该暴露） | tests/backtest/test_strategy_validation_pipeline.py | 通过（带备注） | 实跑全绿 |
| B | 上游注入面：is/oos Sharpe、WFA folds、参数敏感性全部调用方供给——**上游错了本件无发现能力**（纯编排的固有边界）；is_sharpe 非有限值等由 Gate/Detector 抛错（DecisionGateError 向上传递，契约声明一致） | :132-134,143-161 | 说明 | 契约 docstring 对照 |
| B | **三段门控窗口切分前视问题（任务指定问）**：本件输入注入式，IS/WFA/OOS 切分全在调用方——**本模块无窗口时序字段、无从校验 OOS 晚于 IS/WFA**；前视防线=0（结构性盲区）。现实缓解：真实消费走 fw_backtest 的"该次实测净值的时间切片"（decision_gate.py:5 声明），切分由整装回测承担且经其自身审查；但直接构造 StrategyValidationRequest 的脚本路径无防线 | :66-93; decision_gate.py:5 | P2（结构性登记） | 读 Request 字段（无任何窗口/时间戳字段） |
| C | 输出消费方：scripts/backtest/eval_f2_narrow_backtest.py、f06_e4_wfa_exam.py（裁决展示/验收参考）；can_deploy 明示"仍需人工审批"（52 号 §4）——技术裁决未直连资金路径，爆炸半径=脚本结论误导人审 | :26-27; grep 脚本消费 | 说明 | grep run_strategy_validation 调用点 |
| D | 兄弟件：与 evaluate_strategy_risk_admission（decision_gate.py:172）的准入谓词分工——本件是"技术门控∧过拟合"组合，后者是"过拟合∧DSR"实盘准入谓词；两轨判定源已声明禁各算各的，本件经 DecisionGate 复用 evaluate_dsr ✓ 无第二套 DSR 判定 | decision_gate.py:8,172-197 | 通过 | 两函数对照 |
| E | 五问：无静默失败（异常上抛）✓；无状态无并发 ✓；重复运行幂等 ✓；**时序攻击面=注入伪造 OOS Sharpe**（见 B 轴）——本件信任边界内无法防，登记 | 全文件 | 说明 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| IS→WFA→OOS 三阶段不可跳级门控 | **对等已有**：walk-forward analysis + 阶段化放行是量化策略验证标准结构；不可跳级=fail-closed 编排，业界同构 | Palomar Portfolio Optimization §8.3（portfoliooptimizationbook.com, 2023） |
| 过拟合多维检测（WFA 衰减+参数扰动+跨期稳定性+样本内外对比）作为上线前置 | **对等已有**：与 LdP deflation 思想、Harvey et al. 多重检验纪律同族；DSR 门槛 0.95 对齐 p<0.05 惯例 | Bailey & López de Prado 2014（davidhbailey.com/dhbpapers/deflated-sharpe.pdf, JPM 2014）；ML4 Trading DSR 文档（ml4trading.io, 2020s） |

## 4 缺陷清单

1. **P2｜DSR"默认关闭"文档与"默认开启 fail-closed"现实相反**：三处 stale 声明（:24,80-81,152）会误导调用方以为不注入 DSR 只影响"加分项"，实际默认参数下门恒关（can_deploy 恒 False）。2026-09-16 车道 L 接线后未回灌本件文档。
   - 现状→证据：见六轴表 A 行锚点。
   - 影响与爆炸半径：脚本消费方（eval_f2/f06）与人审读者按旧文档理解裁决结果；若脚本未注入 dsr，其输出 can_deploy=False 会被误读为"策略不行"而非"DSR 未喂"。
   - 建议修法：三处文档改为"默认 dsr_threshold=0.95 fail-closed，须预计算注入；回退需显式 dsr_threshold=None"。
   - 验证法：构造最小 Request（无 dsr）调 run_strategy_validation，断言 gate 结果含 unavailable/fail-closed 字样。
2. **P2（结构性登记）｜窗口切分前视防线在本件为零**：输入注入式无时序字段可校验；建议 Request 增加 is/oos 窗口区间字段并断言 oos_start >= is_end（或至少 docstring 强制调用方自证）。
3. **P3｜src 生产调用方为零**：仅脚本消费；[CONSUMERS]"首批策略上线验证编排入口"是流程性声称，代码接线薄。与 B10/B14 同族（程度较轻：脚本确在用）。

## 5 挂起疑问

- 两个脚本消费方（eval_f2_narrow_backtest/f06_e4_wfa_exam）是否已注入 dsr——若未注入，其产出的 can_deploy 语义需重估（本轮未复跑脚本）。
- OverfittingDetector 三维默认阈值的深审归属（他件对象，本轮只核编排衔接）。

## 6 完备性自评

- 六轴全查：A（编排+DSR 语义翻转核对）✓ B（注入面+前视盲区=任务指定问已答：切分不在本件、本件无防线）✓ C（脚本消费方）✓ D（与准入谓词分工）✓ E（五问+伪造注入面）✓ F（2 条对照）✓。
- 长尾：DecisionGate/OverfittingDetector 内部数学深审（对象归属他件）；两脚本实跑复现。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2 文档 vs 现实相反（DSR 默认）: 挂起登记。
- 修复提交: q-0024（B11 冲击腿）。
