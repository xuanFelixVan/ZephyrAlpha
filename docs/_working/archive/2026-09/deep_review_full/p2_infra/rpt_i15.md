---
ttl: task_bound
title: 深度审查报告——I15 一致预期交叉验证（consensus_crosscheck）
object: I15 一致预期交叉验证
target: src/zephyr/data/consensus_crosscheck.py:275（run_consensus_crosscheck 入口；检查族 L124-243）
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=73d1d045；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：I15 consensus_crosscheck（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 范围：双独立真源互查（自建 consensus_daily vs 同花顺 analyst_forecast）五检查族（对账/新鲜度/结构/PIT/体量）+ 落表 cross_validation_log + --selftest 火警演习。23:30 交易日 cron 经 _run_special_schedule 分发。
- 前科背景：2026-09-14 源污染事件（research_report 快照冒充历史，checklist #7 PIT 项）治本配套；_CLEAN_ERA_START=2026-09-12 清洁窗锚定。
- 测试：头注自证 test_consensus_crosscheck.py 从未入库（2026-09-17 据实更正）——独立单测缺口；selftest 仅覆盖 _classify+反相关构造，未覆盖五检查族任一真实分支。
- 变更热力：2 commits。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **P2 探针时间炸弹：forecast_year=2026 硬编码**——_SQL_PROBE_MOUTAI 固定 `forecast_year = 2026` 且阈值带 (20,120) 按fy1 校准；2027 年起 fy1=2027，探针查 2026 年（将变历史年，终将无行/出带）→ probe_ok 恒 False → pit_semantics 恒 fail → 每日 ERROR 假火警直至有人想起改码 | consensus_crosscheck.py:59,89-92,240-243 | P2 | 拨 day 至 2027-01 复演 SQL 返回 |
| A | 新鲜度体量阈值耦合：ths_min_daily_rows=1000 判定日行数，但 _SQL_THS_FRESH 统计的是 `report_date >= day` 的**区间累计行数**而非"日行数"——阈值语义与变量名不符（区间 3 天 3000 行=日均 1000 恰过，1 天拖更则累计偏小误警；口径漂移型隐患 checklist #1 邻接） | consensus_crosscheck.py:76-81,178-186 | P3 | 对照区间行数与单日行数 |
| A | 相对差分母=自建值 ours（`max(abs(b),1e-6)`）——"自建为准"的单向口径：若污染发生在自建侧，中位差以被污染值为基准可能钝化；双源互查的双向对称性未实现 | consensus_crosscheck.py:155-156 | P3 | 构造自建侧污染看 med 响应 |
| B | 任一源 CH 不可达→_last_trading_day 返空→RuntimeError→ERROR 告警（fail-visible 正确）；trade_calendar 表本身停更时 day=旧交易日，全部检查对旧日跑=检查静默失效（依赖 data_supply_sentinel 兜底——跨层依赖无本地断言） | consensus_crosscheck.py:117-121,288-290 | P3 | 停更日历表观察静默 |
| E | 落表 _persist 经 write_result（含质量门禁路径，非 BufferedWriter 旁路）；落表失败仅 warning 不影响告警——降级语义正确 | consensus_crosscheck.py:246-272 | 已查无 | mock 失败 |
| D | 阈值预注册 _THRESHOLDS 禁漂移声明+--selftest 火警演习设计=对"报警系统从不被测试"风险的正面回答；但演习覆盖面（2/5 检查族弱覆盖）与声明强度有差 | consensus_crosscheck.py:50-60,331-347 | P3 | 对照 selftest 分支覆盖 |
| A | spearmanr 对并列值/小样本（n<30 提前拦截）、ZeroDivisionError 吞没解析行——边界处理基本完备 | consensus_crosscheck.py:133-151 | 已查无 | 单测 |

## 3 SOTA 对照
- 双独立真源互查（two-source verification）与数据质量管理的 record matching/cross-source validation 惯例一致；秩相关+覆盖+分位差组合阈值属合理预注册实践。**对等已有**。来源：数据质量交叉验证工程通识（未单独检索 URL=受阻如实记，检索预算已用于 I01/I08 的 ClickHouse 与调度两题）。
- PIT 零修正率探针（uniq>=2 判活数据 vs 快照回放 uniq=1）为项目原创性自动化检测，挖矿价值正向。**立卡候选（方法面推广到其他 PIT 表）**。

## 4 缺陷清单
1. P2 时间炸弹（2026 硬编码）：修法=forecast_year 改"动态最大预测年"（SELECT max(forecast_year)）或阈值带按年配置化；2026-12 前不修则 2027-01 起每日假 ERROR。
2. P3 组：新鲜度行数口径、相对差单向分母、日历停更静默依赖、selftest 覆盖面。

## 5 挂起疑问
- cross_validation_log 的下游消费方（前端/策略侧是否有人读 fail 记录）未普查——若无人消费，落表仅存档价值。

## 6 完备性自评
六轴全查。长尾：scipy spearmanr 版本行为差异未锁定运行库版本（运行环境锁定材料缺项=如实记）；五检查族在真实两源数据上的假阳/假阴率未做数据画像（需 CH 查询权限，收口方建议跑 30 天回放）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P3 探针时间炸弹: 确认→治本（跨年自愈 SQL）。专项测试从未入库与报告一致（测试缺口挂起）。
- 修复提交: q-0027（M03/M04/I15）。
