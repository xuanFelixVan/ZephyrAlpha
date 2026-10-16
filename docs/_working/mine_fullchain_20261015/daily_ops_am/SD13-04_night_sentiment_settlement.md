---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-04
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-04 夜间情绪窗结算（窗口 [T-1 18:00, T 08:00)）

## 1. 定义

每日 08:20（全周）特殊槽 `nightly_sentiment` 驱动夜间情绪窗结算：对 [T-1 18:00, T 08:00) 新闻情绪窗闭合结算并落情绪窗口表。采集腿落夜窗、结算腿在盘前（spans_segments=[A,D] 两腿跨段）。决策问题：08:20 结算的窗闭合了吗？窗内有没有产物行落到情绪窗口表？

地图在册态：wiring=wired、build=built、skeleton ✅（本段 4 个 ✅ 之一）、tdm_refs 五挂（TDM-E-L0-04/L1-S3/L2-09/L9-A09/P1-03）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 窗内新闻/情绪事件流（快新闻 D13-17 供料 + 夜窗采集腿） | `src/zephyr/intelligence/news_llm_scorer.py:48`；`src/zephyr/alt_data/emotion_index_builder.py:322` |
| 输出面 | c1_market.news_sentiment_window（max(window_ts) 与全表行数读数在案，骨架 §7 C 组） | 地图 evidence 引 `docs/_working/map_build/fig13_daycycle/00_skeleton.md` §2 D13-04 行 |
| SSOT 真源 | 图13 节点契约（行 383-464）+ 调度配置槽声明 | `config/trading_day_cycle_map.yaml#D13-04`；`src/zephyr/data/config/schedule.yaml` |
| 代码模块 | 调度器特殊槽分支 + 结算批执行体（服务总闸 flag 惯例：`data/runtime/nightly_sentiment.disabled` 存在=停用） | `src/zephyr/data/scheduler.py:377-420`（实核分支+flag+run_nightly_sentiment_batch 导入）；`src/zephyr/intelligence/nightly_sentiment_window.py` |
| 门禁约束 | 服务总闸 flag 语义；LLM 评分腿须走 LSGSecurityGateway（裸调被 GATE-20+运行时拦截器双捕）；RULE-SCHEMA-TZ（窗口时戳列显式时区） | `src/zephyr/data/scheduler.py:378-394`（flag 检查实核）；`AGENTS.md` §9.2/§1 规则 10 |
| 自动化触发 | mechanism=A_apscheduler，每日 08:20 全周；observed 每日 1 拍；special_branch_exists=true | `config/trading_day_cycle_map.yaml#D13-04` cadence_zh/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 上游 D13-17 快新闻 7×24 在产供料（30d 61,335 拍） |
| 输出面 | pass | 情绪窗口表读数在案（骨架 §7 C 组），verified_scope=production |
| SSOT 真源 | pass | 节点契约完整、五 TDM 挂点在册 |
| 代码模块 | pass | 分支/flag/执行体三层实存实核 |
| 门禁约束 | pass | 总闸 flag 惯例在位；LLM 腿 LSG 门槛在册 |
| 自动化触发 | pass | 每日 1 拍 firing 在案 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无（本格为段内健康样板；唯一结构性注记=采集腿落夜窗跨段，段归属已用 spans_segments 显式声明）。
- gap_refs 空。fallback=「窗不闭合则该拍产物缺」无兜底器，miss_policy=absorb——属已知取舍非缺口登记。
- 建议：本格可作为段内 alert/execute 分工与 flag 总闸的参照模板（D13-03 检出即蒸发问题可对照本格的产物表面补齐）。
