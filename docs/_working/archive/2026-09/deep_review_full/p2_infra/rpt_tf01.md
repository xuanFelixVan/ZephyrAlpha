---
ttl: task_bound
title: 深度审查报告——TF01 intraday_realtime盘中实时族(16任务)
object: TF01 intraday_realtime 盘中实时任务族
target: "src/zephyr/data/config/tasks.yaml（schedule: intraday_realtime 共16条，主锚 143/215/885/896/908/923/941/968/1364/1730/1745/1757/1769/1787/1802/2266/3096）；schedule.yaml:34-37"
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审，行号=现状）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF01 intraday_realtime盘中实时族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测族内 **16 任务**（grep `schedule: intraday_realtime`=16 行），其中 disabled 1（l2_tick_snapshot，tasks.yaml:1743）。时段=`*/5 9-15 * * 0-4`，executor=realtime(4线程)（schedule.yaml:34-36；scheduler.py:2198）。时段在 TRADING_DAY_GUARDED_SCHEDULES（trading_calendar.py:153）节假日自动跳过。
- 任务盘点（源）：miniqmt×9（kline_hk_daily/futures_position 由 akshare fallback？——实际 futures_position 主源 akshare；miniqmt 主源=kline_hk_daily、option_iv_surface、convertible_bond_iv、tick_data_snapshot、index_quote_snapshot、l2(停)、futures_kline_qmt、hk_kline、futures_tick_intraday）、akshare×4、qmt_bridge×2（auction 双件，9/17 已切）、tushare×1（futures_term_structure）、tqcenter×1（sector_snapshot）。
- 材料缺项声明：未取运行时证据包（近 N 天 failure json/日志）、未做数据画像；本报告为配置+代码静态审查+调度链路核对。轴 F 检索受阻（预算集中于调度链与 provider 路由核验，未做外部 SOTA 检索，如实记）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| E | **S1【系统级】9/18 miniQMT 退役 vs 本族 8 个 miniqmt 主源任务无可用退路**：option_iv_surface/convertible_bond_iv/index_quote_snapshot/futures_kline_qmt/hk_kline/futures_tick_intraday 无 fallback；tick_data_snapshot fallback=bdpan 但 bdpan 未注册于 create_provider（死fallback）；l2 停用。迁移台账自认"档2断流=真损失"（台账 §2.2/§2.3），截至现状 tasks.yaml 无主源切换痕迹 | tasks.yaml:885-907/923-940/941-951/1769-1786/1802-1813/3096-3107；scheduler.py:1234-1338（无 bdpan 分支）；docs/_working/2026-09-08-qmt-bridge-migration-ledger.md §2.2-B/§2.2-D/§2.3 | P1 | 停 QMT 客户端跑 `run_task("index_quote_snapshot")` 复演；grep create_provider 分支清单 |
| E | **S2【系统级】健康检查跳过路径静默**：主源 health=test_fail（miniqmt 9/18 后自然转 test_fail，source_health_check.py:290-297 注释自认）时 run_task 走 `continue`（scheduler.py:1543-1551），循环终了仅 `tq.mark_failed`（scheduler.py:1588-1591）**无 alerter.notify**→不写 failure 文件；fallback 转换才 notify（scheduler.py:1562-1568）。唯一兜底=23:00 integrity_check 任务级对账聚合 ERROR（integrity_checker.py:302-317） | scheduler.py:1543-1551,1588-1591 | P1 | mock get_source_health 返回 connect_fail，断言 failures/ 目录无新文件 |
| B | futures_position/futures_term_structure（intraday_realtime）依赖 kline_futures_incremental（daily_capital 18:00）——跨时段 DAG 边是**名义边**：task_queue 对不在本批队列的依赖视为已满足（task_queue.py:150-164 注释自认），无任何跨时段校验/告警 | tasks.yaml:221,914；task_queue.py:147-169 | P3 | 单测：构造跨批依赖看 get_ready_tasks 放行 |
| A | auction 双件已切 qmt_bridge（9/17），桥 meta 显式声明 auction_data/auction_book capability，CH 内派生窗口 [09:15,09:26)（ch_auction_derive.py:10）——A' 方案落地质量核对通过；旧 get_full_tick 通道标 [RETIRED-2026-09-18] 不再路由 | tasks.yaml:1747,1759；qmt_bridge_provider.py:186-190；miniqmt_provider.py:4796,4931 | 已查无 | 对照 meta.capabilities 与 task.capability |
| C | us_futures_intraday_snapshot 主源连续3次失败自动切东财快照（degraded=1 留痕）——任务内双源，爆炸半径小 | tasks.yaml:1787-1800 | 已查无 | mock 新浪失败看东财兜底 |
| D | tick_data_snapshot 的 fallback_sources 指向 bdpan（tasks.yaml:938-940）——bdpan 非注册 source，属"假fallback"复发（同 2026-09-10 已清理的 akshare/kline_us_daily 同型缺陷）；l2_tick_snapshot 循环自引用已清（tasks.yaml:1739 留痕） | tasks.yaml:938-940；scheduler.py:1333-1335 | P2 | 断 QMT 后 run_task tick_data_snapshot 看第二源"未知数据源: bdpan" |
| B | realtime_snapshot akshare 新浪源 `stock_zh_a_spot` 单点、盘后 -4001 自动跳过（tasks.yaml:971 注释）——返回-4001 被判"合法空转"还是失败未在配置层区分，0 行交易日 WARN 兜底（scheduler.py:1749-1756） | tasks.yaml:971；scheduler.py:1735-1756 | P3 | 盘后手动跑看 WARN 噪声率 |
| E | 告警触达=被动：飞书/SMTP 已于 2026-09-15 按 Owner 裁定裁撤（alerter.py:8,28-29），本族盘中任务失败仅落 logs+data/failures/*.json+前端 datasrc 页（api_server.py 消费）——无人打开页面=无人知道盘中断流 | alerter.py:8,28-29 | P2 | 查 data/failures 近3日文件数 vs 前端访问记录 |

## 3 SOTA 对照
- 受阻：本报告未做外部检索（预算用于调度链/provider 路由核验）。盘中快照采集的多源冗余+熔断器（CircuitBreakerRegistry，scheduler.py:525）设计与业内行情采集惯例对等（凭训练记忆陈述，不作实证断言）。

## 4 缺陷清单
1. **P1 退役窗口断流风险（8 任务）**：现状→证据（上表 E 行）→影响=9/18 后盘中 tick/指数/期权IV/期货/港股K 全停，宽度快照、竞价派生的上游 tick 同断→建议=9/17 窗口主源切换集中落地（auction 已示范）或临时给每任务补可用 fallback→验证法=逐任务 `run_task` 于 QMT 关闭环境。
2. **P1 健康跳过静默**：建议在 run_task 全源失败出口补 `alerter.notify(LEVEL_ERROR)`（1 行级修复）→验证法=mock health 断言 failure 文件生成。
3. **P2 bdpan 死fallback**：改 `fallback_sources: []` 显式置空留痕（照 l2 先例 tasks.yaml:1739）。
4. **P2 告警无推送**：恢复任一推送通道或将 integrity 23:00 聚合接 Owner 门位。

## 5 挂起疑问
- sector_snapshot（tqcenter，requires_process=True 依赖通达信客户端）在客户端未运行时的失败路径未见实测记录。
- futures_kline_qmt symbols 若 00 主力连续不被支撑回退具体合约的"首个交易日盘中复测"结论未见回填（tasks.yaml:1781-1783 留痕悬置）。

## 6 完备性自评
六轴全查（F 受阻如实记）。长尾：16 任务逐个 provider 实现深查未做（抽 4 个：auction×2、tick_data、us_futures）；运行时失败率数据画像缺（收口方建议跑近 7 日 fetch_perf JSONL 统计）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
