---
ttl: task_bound
doc_type: report
title: 深度审查报告——TF06 news_slow慢新闻族(2任务)
object: TF06 news_slow 慢新闻任务族
target: src/zephyr/data/config/tasks.yaml:1226-1237(news_stock_em)、1323-1334(research_report)；schedule.yaml:64-67
reviewer: GLM-5.3-Flash / st-deeprev-20260918
baseline: 2fa92002c3（HEAD=b80084c0df；按工作区现状审）
date: 2026-09-18
status: 已审
---

# 深度审查报告：TF06 news_slow慢新闻族（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照
- 实测 **2 任务**：news_stock_em_incremental（ak.stock_news_em，capability=stock_news_em）、research_report_incremental（ak.stock_research_report_em，capability=research_report），共写 c3_fundamental.news_data。时段 `17,47 * * * *` 每 30 分钟触发 + 全局 job_defaults max_instances=1 + coalesce（schedule.yaml:64-67；scheduler.py:2202-2206）——注释自证"跑完才再跑，实际 ~90-180min/轮"。
- 两任务 2026-07 从 event_driven 挪出（tasks.yaml:1229,1326 注释）：5523 只串行限流不堵快新闻队列。

## 2 六轴审查日志表
| 轴 | 发现 | 锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | 时段设计核对通过：max_instances=1 下 30 分钟 cron 触发→上一轮未完则 collapse 为跳过（APScheduler misfire/coalesce 语义），"独立队列不堵 event_driven"目标达成；akshare 单例 60 次/分限流为瓶颈的论证（并行总时间≈串行）成立 | schedule.yaml:61-67 | 已查无 | 看 task_runs 相邻 started_at 间隔≈90-180min |
| B | 主备同源同限流：两任务主源+族内 fallback 均走 akshare 单例（news_stock_em 无 fallback 字段但 capability=stock_news_em 仅 akshare 实现；research_report 同）——akshare 被封/升级断接口=全族停，无跨源退路。akshare meta 声明两 capability（akshare_provider.py:781-782）配对合法 | akshare_provider.py:781-782；tasks.yaml:1226-1237,1323-1334 | P3 | 停 akshare 通道跑两任务看失败告警 |
| C | research_report 是 consensus 管线的旁系输入（research_report_detail 才是 C1.5 真源）——本任务的个股研报流与 detail 任务的字段重叠度未声明，下游若误用本任务行做一致预期聚合会踩 PIT 快照冒充历史前科（checklist #7：56e9183b73 同表前科） | tasks.yaml:1323-1334 vs 606-617 | P3 | grep consensus 管线读 news_data 的路径 |
| E | **0 行 WARN 噪声主力**：两任务单轮 90-180min、5023 只逐股，任何一只无新闻≠全 0 行，0 行告警触发率低——本族告警面干净；失败时 task 级 ERROR + 23:00 对账兜底（integrity 对 news_data 表第一任务=news_data_incremental 的口径，本族失败不影响表级阈值判定——对账任务级 missing 列表会含本族） | scheduler.py:1749-1756；integrity_checker.py:302-317 | 已查无 | 注入失败看 23:00 missing 列表 |
| D | 与 TF05 快新闻共写 news_data+共享 buffer_max_seconds=300——parts 产生节拍一致（裁定 #ARCH-CH-013 Phase 4 统一），无双口径 | tasks.yaml:1232,1329 | 已查无 | — |
| F | 受阻（未检索）。 | — | 受阻 | — |

## 3 SOTA 对照
- 受阻。慢频全市场轮询+限流共存设计（与快新闻分队列）属爬虫工程惯例（训练记忆）。

## 4 缺陷清单
1. P3 akshare 单点：两任务无跨源 fallback（天然无副源可如实留痕——当前配置未显式 `fallback_sources: []`，与"规范化 AI-04 显式空列表"惯例不一致，DATA-TASK-COMPLETENESS gate 每次扫过都会 warn）→建议补显式置空注释。

## 5 挂起疑问
- stock_news_em 与 stock_news_global_em（news_stock_incremental 用）两接口的覆盖差（国内个股 vs 全球）未文档化——news_data 表内来源去重是否充分。

## 6 完备性自评
六轴全查（F 受阻）。长尾：两 akshare 接口的实际限流命中率/轮询周期实测未做（需运行数据）；research_report 与 research_report_detail 字段重叠矩阵未建。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
