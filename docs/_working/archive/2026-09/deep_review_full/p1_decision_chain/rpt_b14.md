---
ttl: task_bound
title: 深度审查作业簿——回测预检器
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：回测预检器（B14）

- 状态: **已审**
- 级别: P2｜类型: 闸门
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/preflight_checker.py:50`（run_backtest_preflight）
- 生产调用方: **零（by design）**——[CONSUMERS] 明示"调用方显式接线预留（重评条件触发前不接线回测引擎）"；grep src+scripts 仅本件与测试命中
- 测试文件: tests/backtest/test_preflight_checker.py（6 用例实跑全绿）
- 变更热力: 7 commits/3.5 月——未接线却有持续改动，投入产出比存疑
- 备注: 小件（87 行），六轴从简但全查

## 1 对象快照

- 审查范围：全文件 87 行——结构检查（symbols/窗口）+DQ 检查注入执行+PreflightReport。
- 排除项：governance data_quality run_dq_check 的检查函数本体（注入侧，另域）。
- 材料包缺项声明：无运行时证据（零调用方）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 无数学对象；结构检查完备：空 symbols/窗口倒置 Fail-Closed ✓；DQ 未注入→skipped 标记（防"无检查假绿"）✓——核心设计意图落地 | :68-80 | 通过 | 读码+单测 |
| A.3 | 6 用例断言强（skipped 语义/violations 前缀/空表）——**信任** | tests/backtest/test_preflight_checker.py | 通过 | 实跑全绿 |
| B | dq_checks 契约（(table,where)->violations）与 governance 同签名，无文档化单位/时区契约——注入函数内部自查，本件不做二次校验（信任注入侧） | :52-56 | 通过 | — |
| B | **required_tables=() 显式传空时假绿**：dq_checks 注入但零表被查，violations 与 skipped 双空 → passed=True，且无"零表"标记——注入了检查却全跳过的静默路径（默认值非空，需显式传 () 才触发，前瞻登记） | :73-78,55 | P3 | `run_backtest_preflight(["x"], d1, d2, dq_checks={"a": f}, required_tables=())` → passed=True |
| C | 零调用方（by design，头部已声明）；爆炸半径=0（未接线）。**但 [MATURITY]=production 与零接线矛盾**（对齐 B10 同款问题，此处声明在案故降 P3） | :5,7 | P3 | grep 全仓 |
| D | REQUIRED_TABLES 仅 kline_daily 一表：15 号规格 §要点③ 口径是否应含 tick/深度表未在本件层判定（规格符合性不在本件证据内） | :37 | P3 | 对照 15_data_feature_layer_spec |
| D | 与 B13 的 holdout 检查、与 B12 的数据量纲检查无重叠无冲突（各管一段）✓ | 全文件 | 通过 | — |
| E | 五问：无静默失败（violations 全出声）✓；无时序/重入面 ✓；where 子句 f-string 拼 date 对象（datetime.date 格式化无注入面）✓；`checked_at=date.today` 默认值使 Report 非确定（重放比对时字段漂移，轻） | :47,74 | P3 | 构造两次调用比对 checked_at |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 回测前数据预检（pre-flight data quality gate） | **对等已有**：业界回测平台通行"跑前 DQ 检查"实践；注入式 DQ 函数+skipped 透明化设计不劣于常见做法 | Palomar Portfolio Optimization §8.3（portfoliooptimizationbook.com, 2023，回测基础设施章节泛指）；项目内 15_data_feature_layer_spec BM-BT-02-D |

## 4 缺陷清单

1. **P3｜[MATURITY]=production 与零接线矛盾**：头部声明"预留"，production 标签超前（应 design/testing，或写明"production-ready 未接线"）。7 commits 持续投入一个无调用方小件，热力与产出不匹配（模式 #8 孤儿变体，声明在案故轻于 B10）。
2. **P3｜required_tables=() 假绿边缘**：建议空表校验（required_tables 为空且 dq_checks 注入 → 违规或 skipped 标记）。
3. **P3｜checked_at=date.today 非确定默认值**：重放/幂等比对时字段漂移；建议显式传参或注入 clock。
4. **P3｜必需表清单与 15 号规格的符合性无锚**（仅 1 表）：接线前应复核规格 §要点③ 完整清单。

## 5 挂起疑问

- "重评条件触发前不接线"的触发条件定义在哪个注册表（15 号/BM-BT-02-D）——收口方确认接线计划是否仍存活（防永久预留）。

## 6 完备性自评

- 六轴全查：A（结构检查逐条）✓ B（注入契约）✓ C（零调用方实锤）✓ D（规格符合性登记）✓ E（五问+注入面）✓ F（1 条对照）✓。
- 长尾：governance run_dq_check 检查函数质量（注入侧他域）；REQUIRED_TABLES 与 15 号规格逐条对照（规格文本未逐条核）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P3 零接线+MATURITY 失实+required_tables=() 假绿: 挂起登记。
- 修复提交: q-0024（B11 冲击腿）。
