---
ttl: task_bound
doc_type: report
title: 深度审查报告——TF04 auction_highfreq竞价族(2任务·A'方案落点)
object: TF04 auction_highfreq 竞价任务族（A' 方案落点）
target: src/zephyr/data/config/tasks.yaml:1745-1767（auction_data_snapshot/auction_book_snapshot）；schedule.yaml:179-183；src/zephyr/data/implementations/qmt_bridge_provider.py:186-190；ch_auction_derive.py
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF04 auction_highfreq竞价族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **2 任务**：auction_data_snapshot（1745）、auction_book_snapshot（1757），9/17 已切 `source: qmt_bridge`（原 miniqmt get_full_tick 通道随 9/18 miniQMT 退役，tasks.yaml:1755）。时段 auction_highfreq：6 段 cron `*/10 15-25 9 * * 0-4`（秒/分/时…，10 秒间隔，schedule.yaml:179-183），executor=realtime，时段在交易日守卫集（trading_calendar.py:161）。
- A' 方案：桥 tick_depth_5 竞价窗口 CH 内派生（ch_auction_derive.py，窗口 [09:15,09:26) 含撮合打印行），消费端/表 schema/调度名零改动。旧通道方法已标 [RETIRED-2026-09-18] 保留至清理批（miniqmt_provider.py:4796,4931）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | **A' 落地质量核（通过项）**：①6 段 cron 秒级触发被 scheduler 显式支持（scheduler.py:2121-2140）②桥 meta 显式声明 auction_data/auction_book 双 capability（qmt_bridge_provider.py:186-190）③派生模块头部自述"源表必须滤市（不滤市=指数行情灌进竞价表的事故）"——历史事故已修④open/high/low=0 与 miniqmt 竞价时段原产语义一致（9/16 平银实证，ch_auction_derive.py:13-15）⑤快照幂等=(symbol,trade_date) 最后插入胜出=终态随竞价进程自然演进（ch_auction_derive.py:49） | ch_auction_derive.py:10-15,49；qmt_bridge_provider.py:186-190 | 已查无（主链） | 竞价日 09:26 后查两表当日行数与 09:15 分桶 |
| B | 单点上游=tick_depth_5（桥沙箱 TICKDUMP3 产出）——竞价 10 分钟为**不可回填窗口**（过了就没了），沙箱/大QMT 宕机=当日竞价数据永久缺失。缓解已备：scripts/backfill_auction_snapshot_history.py 回补 2026-06 起空窗日（qmt_bridge meta known_issues 自述）；tick_data 一档源兜底回补路径在派生模块注释中（ch_auction_derive.py:68） | qmt_bridge_provider.py meta.known_issues；ch_auction_derive.py:68 | P2 | 沙箱停机日检查次日 06:50 哨兵/23:00 对账是否报 auction 表缺口 |
| D | tasks.yaml:1760 注释"3秒高频层（9:15-9:25 interval trigger）"为**过时注释**（现=10 秒 6 段 cron，schedule.yaml:174-183 记载 3 秒→10 秒的 collapse 事故换算）——注释漂移易误导后人调回 interval trigger 重蹈 collapse 覆辙 | tasks.yaml:1760 vs schedule.yaml:174-183 | P3 | 对照两处文本 |
| E | 告警链=任务失败 ERROR failure 文件+23:00 对账聚合；无推送（alerter.py:28-29，系统发现 S1）。竞价任务失败发生在 09:15-09:25，最早可见点=当日 23:00（对账聚合）——**延迟近 14 小时**，属盘中任务告警时效的结构性弱点 | integrity_checker.py:302-317；alerter.py:28-29 | P2 | 注入一次失败，测从失败到 failures 文件/对账告警的时延 |
| C | 消费端=主力挂撤单行为分析/打板引擎（schedule.yaml:174-183 描述）；快照缺失时消费端行为（NaN 处理/跳过）未在本族配置层声明 | schedule.yaml:174-183 | P3 | grep auction_snapshot 消费方看空日处理 |
| F | 受阻（未检索）。10 秒节拍 vs 3 秒 collapse 的处理（coalesce+节拍>单轮耗时）与 APScheduler 最佳实践对等（训练记忆） | schedule.yaml:174-178 | 受阻 | — |

## 3 SOTA 对照
- 见上表 F 行：受阻。集合竞价微观结构数据采集无公开标准做法可对照（项目自研口径为主）。

## 4 缺陷清单
1. P2 竞价窗口失败→告警时延 14h：建议 auction_highfreq 时段结束时（09:26）加一次性"当日行数>0"即时哨兵（或复用 breadth_freshness_alerts 模式）→验证法=停沙箱跑一个竞价日，测告警时延。
2. P3 过时注释修正（tasks.yaml:1760）。
3. P3 旧通道 [RETIRED] 方法块列入清理批（miniqmt_provider.py:4796,4931 自留清理承诺）——防止孤儿死码（checklist #8）。

## 5 挂起疑问
- A' 方案文档原文（裁定⑤方案 b/A' 命名出处）未定位到独立裁定条目——命名链完整性待收口方核（ruling_registry 检索未做）。

## 6 完备性自评
六轴全查（F 受阻）。长尾：auction_book 五档推导规则（昨收/涨跌停规则推导）与 stk_limit 真源一致性未逐字段核；backfill_auction_snapshot_history.py 未实测。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
