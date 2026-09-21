---
ttl: task_bound
title: 深度审查报告——TF12 nightly_financial夜间财务族(10任务)
object: TF12 nightly_financial 夜间财务任务族
target: src/zephyr/data/config/tasks.yaml:95-105(margin_trading)、646-658(financial_derived_build)、763-833(三表+indicator+main_business)、1859-1869(placeholder停)、1900-1922(十大股东×2)、2064-2074(northbound)；schedule.yaml:108-112
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF12 nightly_financial夜间财务族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **10 任务**（无 disabled；margin_trading_qmt_placeholder 实测归 daily_capital 侧）：margin_trading(akshare)、balance_sheet/income_statement/cashflow_statement/financial_indicator（miniqmt 主+akshare fb）、main_business（miniqmt **无 fb**）、top10_shareholders×2（akshare）、financial_derived_build（internal，依赖三表）、northbound_hold_snapshot_refresh（tushare hk_hold）。22:00 heavy(2线程)，交易日守卫（schedule.yaml:108-112；trading_calendar.py:158）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **S-TF12 main_business（miniqmt 独有，209 万行）无 fallback**：迁移台账 §2.2-C 列明"akshare 同类字段口径不同，逐表评估"未完成——9/18 后断流=真损失。四张三表类任务有 akshare fallback（meta 配对合法：akshare_provider.py:873-876），fallback 接管后字段口径差异（QMT Capital/Statement vs akshare 接口）未做对拍留痕 | tasks.yaml:823-833；akshare_provider.py:873-876；migration-ledger §2.2-C | P1 | 9/19 查 c3_fundamental.main_business 断更；fallback 接管日抽 10 股对比单季营收口径 |
| A | financial_derived_build DAG（三表同时段依赖）强约束有效；trading_day_only: false（纯 CH 派生，tasks.yaml:658）+PIT=三方公告日齐+哨兵守卫（tasks.yaml:657 注释）——派生层"PIT=公告日齐"的机械判定依赖三表 announce_date 一致性，上游任一表 fallback 接管后 announce_date 口径漂移会静默改变 PIT 语义（B 轴隐式契约未文档化） | tasks.yaml:646-658 | P2 | 构造一表 announce_date 漂移看派生行是否异常 |
| B | northbound_hold_snapshot_refresh：tushare hk_hold 全量覆盖+provider 内 PIT 守卫（季度末+20 自然日才采新季度）；无 fallback（交易所官网预案未施工，DATA-TASK-COMPLETENESS warn 已知接受，tasks.yaml:2074）——tushare 单点+权限依赖，断供=北向持仓快照停更，与 hk_connect_flow 北向退役前科（checklist #6）同域——**该表未入 data_supply_sentinel 16 表清单** | tasks.yaml:2064-2074；data_supply_sentinel.yaml:28-124 | P2 | 查 sentinel yaml 无 northbound_hold_snapshot；建议补 |
| A | margin_trading（akshare SSE/SZSE 两接口）：融资融券 T+1 发布语义与 22:00 时点匹配（schedule.yaml:108 注释）——时点设计正确 | tasks.yaml:95-105；schedule.yaml:108 | 已查无 | 对比交易所当日两融发布时间 |
| C | top10×2 逐股逐季度拉取（_get_all_a_symbols 5200+股）在 heavy 池 2 线程串行——22:00 批次时长约 2-4h（scheduler.py:785 注释自认），与 22:00 池内 9 任务共存——池饱和时 Northbound/derived 顺延，misfire 不适用（同时段排队非错过）——批次完成时刻画像缺 | scheduler.py:784-786 | P3 | 统计近一周 nightly_financial 完成时刻分布 |
| E | 告警链同系统发现 S1/S2：heavy 池任务失败 ERROR 文件+23:00 对账（nightly_financial 在 integrity daily 口径内且 catchup daily 桶含之——错过有 05:30 补跑，兜底完备） | catchup_guard.py:45-47；integrity_checker.py:61-67 | 已查无 | 停跑一日看 05:30 catchup 补跑 |
| F | 受阻（未检索）。财报三表+单季拆分+TTM+应计比率的派生口径属 F1-M1/DS-230 设计文档域，数学轴移交 p1 班次 | tasks.yaml:657 | 受阻 | — |

## 3 SOTA 对照
- 受阻。

## 4 缺陷清单
1. P1 main_business 断流风险：按 §2.2-C 评估 akshare 主营业务接口（东财 stock_zygc_em 族）切源或显式 disabled 留痕——当前"活着但将死"状态最危险。
2. P2 northbound_hold_snapshot 入哨兵清单（季度频表，阈值=季度末+20 自然日窗口内 max(trade_date) 推进）。
3. P2 三表 fallback 接管后的 announce_date 口径对拍。

## 5 挂起疑问
- akshare fallback 三表接口是否含金融/保险等特殊报表模板（QMT 与东财模板差）——接管期数据质量未画像。

## 6 完备性自评
六轴全查（F 受阻）。长尾：financial_derived 单季拆分/TTM 数学正确性属 p1；top10 接口的季度窗口推进逻辑未逐行查。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
