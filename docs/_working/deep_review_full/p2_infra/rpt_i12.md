---
ttl: task_bound
doc_type: report
title: 深度审查报告——I12 自动补下载器（auto_backfiller）
object: I12 自动补下载器
target: src/zephyr/data/auto_backfiller.py:118（class AutoBackfiller，全文 255 行）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I12 AutoBackfiller（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：事件触发式回填编排核（new_factor/formula_upgrade/data_source_fix → 日期分片 → 注入 executor → 10% 抽样 → 血缘/retrain 触发）。判定核心纯内存、executor/sink 全注入。
- 消费方：头注=运行时装配批（grep src/ 未见生产装配点——**孤儿嫌疑**，checklist #8 审查问句适用）。
- 测试：tests/zephyr/data/test_auto_backfiller.py 存在。
- 变更热力：4 commits（MATURITY=testing）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| C | **P2 生产调用方=0（孤儿死码嫌疑）**：grep src/ 仅测试引用；头注声称消费方为"运行时装配批"但仓库内无装配代码——当前无任何生产事件能触发本编排（空转中） | auto_backfiller.py:5（CONSUMERS）+ grep | P2 | grep -rn "AutoBackfiller" src/ scripts/ 排除 tests |
| A | 无 trading_days_provider 时按自然日分片：周末分片交 executor 大概率 rows=0 → _default_validator 判 failed → 全程 all_ok=False → 血缘/重训永不触发（fail-closed 但=功能性死锁，取决于装配方是否必传 provider） | auto_backfiller.py:160-167,184-186 | P3 | 不注入 provider 跑含周末区间 |
| A | 抽样验证只对成功分片抽样（ok_results）——失败分片永不被抽验，若 executor 谎报 success 且 0 行、装配方未自定义 validator，则全错通过 | auto_backfiller.py:204-208 | P3 | executor 全返 success+0 行看 report |
| A | plan.max_workers 字段声明但 run() 串行执行——配置承诺与实现不符 | auto_backfiller.py:115,194-199 | P3 | 读码对照 |
| E | fail-closed 三断言（未知触发类型/日期倒挂/空 target→ValueError）+ sink 异常留痕不阻断——错误契约干净 | auto_backfiller.py:146-152,226-244 | 已查无 | 单测 |
| D | 与 backfill_checker 查重裁定（L25-27：事件触发 vs 定时缺口，不复制）——分工声明清晰 | auto_backfiller.py:25-27 | 已查无 | 对读 rpt_i11 |

## 3 SOTA 对照
- 回填分片+抽样验收+血缘联动与数据平台 backfill 编排（分片/验证/门控）惯例对等；抽样仅限成功分片是常见盲区。**对等已有（带盲区）**。来源：数据回填编排工程通识（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08）。

## 4 缺陷清单
1. P2 孤儿死码嫌疑：要么接线装配批（触发事件源落地），要么登记退役/挂起（checklist #8：空转多久没人发现）。定级前提=确认装配批是否在仓外/在途。
2. P3 组：无 provider 时的周末分片死锁、成功分片偏抽样、max_workers 未实现。

## 5 挂起疑问
- "运行时装配批"是否指 strategy_pipeline/B10 战役的在途工作——收口方确认后本对象或转"挂起等接线"而非缺陷施工。

## 6 完备性自评
六轴全查。长尾：test_auto_backfiller.py 断言强度未逐条审；executor 真实实现（若存在于装配批）未审。
