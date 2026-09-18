---
ttl: task_bound
doc_type: report
title: 深度审查报告——TF05 event_driven事件族(11任务)
object: TF05 event_driven 事件驱动任务族
target: src/zephyr/data/config/tasks.yaml:158-168(macro_data)、529-544(news_data)、1178-1304(news_cls/eastmoney/rss/cctv/baidu×2/stock/tushare)、2962-2976(macro_fred)；schedule.yaml:56-59
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF05 event_driven事件族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **11 任务**（news_tushare disabled）：8 路新闻（rss/cls/eastmoney_news 直连 + akshare 5 路）共写 c3_fundamental.news_data + macro_data(akshare) + macro_fred(fred)。时段 `*/3 * * * *` 7×24，executor=default(8线程)（schedule.yaml:56-59）。buffer_max_seconds=300 统一（裁定 #ARCH-CH-013 Phase 4）。
- 写入前去重：标题 MD5（tasks.yaml:1176-1177 注释，scheduler 自动调 news_dedup）。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| B | **新闻 8 源冗余=本族静默死亡风险被结构性压低**：单源断供（RSSHub 挂/东财反爬）→该任务失败告警，但 news_data 表仍被其余源喂数，integrity 表级阈值不触发——单源死亡靠任务级告警（fallback 转换 notify，scheduler.py:1562-1568），RSS/cls/eastmoney 均配了 akshare/news_stock fallback（tasks.yaml:542-544,1191-1193,1207-1209,1223-1225）——注意该 fallback 是"同写 news_data 表"语义，不填本任务信息域（财经快讯≠个股新闻），失败切换会静默改变新闻构成 | tasks.yaml:542-544,1191-1225 | P3 | 停 RSSHub 看 news_data 中 rss 标记条目占比下降是否有告警 |
| B | macro_fred：FRED_API_KEY 缺失→health=env_missing→run_task 跳过该源（scheduler.py:1536-1551）**且循环终了无 notify（系统发现 S2）**——FRED 任务属 17 源中无运行时 meta 校验的成员（scheduler.py:1150-1156 只挂 akshare/miniqmt/qmt_bridge）；叠加"海外站点需 VPN，scheduler 探测关闭时跳过"（tasks.yaml:2946）——key+VPN 双前置，任一失效=任务静默 missing，兜底仅 23:00 对账聚合 | tasks.yaml:2946,2974；scheduler.py:1150-1156,1543-1551 | P2 | 清 FRED_API_KEY 跑一轮看 failures/ 是否零新增 |
| A | event_driven */3 全天候含周末——news/宏观 7×24 语义正确（schedule.yaml:52-55 注释自证提速 */5→*/3 的权衡与"盘后多跑无害"论证） | schedule.yaml:52-59 | 已查无 | — |
| C | 宏观 macro_data 共表三写入方（akshare macro_data/FRED/世界银行 经 indicator_name 前缀区分，tasks.yaml:2940-2946 注释）——共表多任务在 backfill_checker 发现逻辑"同表取第一个非 disabled 任务"下只按第一个任务（macro_data_incremental，akshare）的口径做日频检测——FRED/WB 断供不被表级行数哨兵感知（checklist #6 邻接） | backfill_checker.py（_discover_backfill_tables 同表去重注释）；tasks.yaml:2940-2992 | P2 | 停 FRED 一周看 integrity 是否报 macro_data 缺口（预期不报） |
| D | news fallback 全部指向 akshare/news_stock capability——akshare meta 确有 news_stock（akshare_provider.py:812），配对合法；但 4 个任务共享同一 fallback，akshare 个股新闻限流时=主备同时退化（同源同限流族，failover 语义弱） | akshare_provider.py:812；tasks.yaml:1191-1225 | P3 | akshare 60次/分 限流窗口观察 |
| E | 0 行成功语义：新闻源节假日/深夜低频正常，0 行 WARN 交易日 notify 会产生噪声（如 news_cctv 每晚才更新）——噪声→告警疲劳风险（与 S6 永久红灯叠加） | scheduler.py:1749-1756 | P3 | 统计一周 0 行 WARN 的任务分布 |
| F | 受阻（未检索）。RSS 多源冗余+去重共表属新闻管道惯例（训练记忆陈述） | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。8 源新闻聚合+标题 MD5 去重与业内 news aggregation 惯例对等（凭训练记忆，未检索实证）。

## 4 缺陷清单
1. P2 FRED 双前置静默跳过：建议 env_missing/VPN 跳过时降级为显式 WARN notify（或 daily 对账单列"配置性跳过"桶，与真失败区分）→验证法=清 key 复跑看告警。
2. P2 共表多写入方的哨兵盲区：macro_data 表级检测只覆盖第一任务口径——建议 supply_sentinel（config/data_supply_sentinel.yaml 现无 macro_data）按 indicator_name 前缀加 FRED_* 子序列停更检测。
3. P3 新闻 fallback 的信息域漂移留痕（快讯 fallback≠原域补充）。

## 5 挂起疑问
- news_dedup 去重口径（标题 MD5）对 8 源跨源重复的合并策略（保留谁的时间戳/来源优先级）未见配置——影响下游情绪窗（nightly_sentiment 消费 news_data）的窗口归属。

## 6 完备性自评
六轴全查（F 受阻）。长尾：cls/eastmoney/rss 三 provider 逐行深查未做（抽验配置+路由声明）；RSSHub 2 直连+10 路由的可用率画像缺运行数据。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
