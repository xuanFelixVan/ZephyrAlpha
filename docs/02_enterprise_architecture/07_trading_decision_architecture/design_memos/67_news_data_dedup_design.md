---
ttl: permanent
doc_type: architecture_view
title: news_data 引擎级去重设计
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "1.0.0"
date: 2026-08-27
topic: news_data_dedup_design
scope: 07_trading_decision_architecture
---

# news\_data 引擎级去重设计

> CAND-DAT-025（candidate\_module\_registry.yaml）。治理/清理类备忘：实证 → 根因 → 裁定 → 施工 → 关联发现 → 开放问题。

## 1. 背景与实证

### 1.1 问题

`c3_fundamental.news_data` 的 `research_report` 类别存在稳定 2.0x 物理冗余：290,433 行实际只有 146,519 个唯一 news\_id（2026-08-27 实测）。其余类别（news/announcement/macro\_data）无冗余。

### 1.2 根因（已锁定，非假设）

表引擎：`ReplacingMergeTree(ingest_ts) PARTITION BY toYYYYMM(publish_time) ORDER BY (news_id, publish_time)`。

同一新闻被两批写入，**publish\_time 时区语义不同**：

| 批次 | ingest\_ts   | publish\_time 特征     | 业务含义                                       |
| -- | ------------ | -------------------- | ------------------------------------------ |
| 老批 | 2026-08-01 前 | `D-1 16:00:00`（北京显示） | 正确日期 D 偏早 8 小时                             |
| 新批 | 2026-08-01 后 | `D 00:00:00`（北京显示）   | 正确（naive 北京串按列时区解析，#ARCH-CH-022 时区防线迁移后语义） |

量化（2026-08-27 实测）：

* 143,914 个 id 双版本（一行老批 16:00 指纹 + 一行新批 00:00）；`news_id+publish_time` 完全相同的重复 = **0 行**——冗余 100% 由"同 id 不同 publish\_time"构成

* 单行 id 共 2,605 个：老批单行 1,400 个 + 新批单行 1,205 个

* ch\_reader 自动注入的 FINAL 对现有冗余**一行都折不掉**（ORDER BY 键不同）

因果链：news\_id = MD5(source+title+publish\_time字符串)，两批 MD5 输入串相同（幂等设计生效，id 一致），但**落列 epoch 不同**（老批 = 正确值 -8h）→ ORDER BY 组合键不同 → 引擎永不折叠 → 冗余随每次全量重跑线性累积。

### 1.3 消费侧当前防线（冗余暂无实际污染）

* 评级提取轨（run\_research\_rating\_batch）与情感回填轨均已按 news\_id 去重（三层去重：采集层/批次内/聚合层，2026-08-26 落地）

* 日级归日按 `toDate(publish_time)`：老批行被归到 D-1，双版本期间日级计数若不经 news\_id 去重会虚高且归日撕裂——消费方绕开了，但**任何新消费方若直接 group by 日期就会踩坑**

## 2. 决策（三件套）

### ① 键审查结论：不改表结构

ORDER BY `(news_id, publish_time)` 设计本身合理（同 id 同时间折叠、时间局部性保住分区裁剪）；问题在写入侧 publish\_time 语义漂移，不在键。改键（如单 news\_id）需重建 8M 行表且跨分区仍不折叠——不改。

### ② 历史冗余清扫（research\_report 范围，一次性）

* **双版本 id（143,914 个）**：删老留新——`ALTER TABLE news_data DELETE WHERE category='research_report' AND news_id IN (双版本集合) AND ingest_ts < '2026-08-01'`（mutation，预计影响 \~14.4 万行）

* **老批单行 id（1,400 个）**：不能直删（数据会丢）——先按 +8h 修正 publish\_time 重插修正行，确认落库后再删老行

* 执行约束（沿用 apply\_timezone\_migration.py 防线先例）：dry-run 先行（只输出对账不写）→ 近 24h 备份存在性检查 → 正式执行 → 行数对账自验证（清扫后 rows == uniqExact(news\_id)）

* 幂等断点：双版本集合与老批单行集合由查询现算，重跑安全（已删的查不到）

### ③ 写入侧统一规约（防复发）

* **publish\_time 规范化唯一真源**：`news_dedup._parse_datetime` 语义固化为"纯日期/naive 串一律按 Asia/Shanghai 墙钟；带时区串先转 Asia/Shanghai 再落地"。新增写入路径必须走 `build_news_row`，禁止旁路构造 publish\_time

* **写前预检公共化**：backfill\_research\_report\_2025.py 的 `load_existing_news_ids` 模式（写前查库内已存在 id 集合）沉淀为 news\_dedup 公共助手，供一切批量回填脚本复用

* 增量常态流（collect\_news）已有采集层去重，不受本规约影响

## 3. 考虑过的替代方案

| 方案                                          | 拒绝理由                                                                                   |
| ------------------------------------------- | -------------------------------------------------------------------------------------- |
| `OPTIMIZE TABLE ... DEDUPLICATE BY news_id` | ①跨分区不生效（月末边界双版本分属相邻两月分区，必残留）②DEDUPLICATE BY 保留哪行无版本列语义保证（可能留错 16:00 老行）③物理优化语义，非数据修正语义 |
| 全表重建（argMax 换表 RENAME）                      | 8M 行全量拷贝过重；news/announcement 6.7M+0.98M 行无需动；停写窗口成本高。research\_report 定点 mutation 即可解决 |
| 改 ORDER BY 为单 news\_id 键                    | 键列修改=重建表（同上过重）；跨分区折叠仍不保证；且不解决老批单行 publish\_time 本身偏 8h 的正确性问题                          |
| 只清扫不修写入侧                                    | 下一次全量回填复发（本次冗余正是 7-15 批与 8-26 批语义漂移叠加的产物）                                              |

## 4. 关联发现（超出本备忘施工范围，另立项）

**news 类别 98.4%（6,619,975/6,727,116 行）、announcement 类别 100%（982,538 行）带同款 16:00:00 指纹**——publish\_time 系统性偏早 8 小时。这些类别无冗余只是因为只有老批、没有新语义重写作对照。

业务后果（按严重度）：

1. **回测前视偏差风险**：北京日期 D 的新闻/公告在库内记为 D-1 16:00——按库内时间的回测会在 D-1 收盘后"看到"D 日信息，信号前移一日，IC/收益虚高。look\_ahead\_bias\_detector 无法检出（它查代码层未来函数，不查库内时间戳语义）
2. 日级归日错误：D 日新闻被归入 D-1（情感日聚合、公告事件日历、研报日级指标的老批部分均受影响）

该坑量级 \~760 万行，需走时区防线重建路径（衔接 #ARCH-CH-022 apply\_timezone\_migration.py 既有框架：键列重建 + dry-run + 备份前置），**另立 CAND 专项**，不在本备忘施工。本备忘清扫 research\_report 后，消费方读到的研报时间全部正确；news/announcement 修正前，依赖 publish\_time 归日的消费方需知悉该 8h 偏移。

## 5. 施工清单

| # | 项                                                                           | 验收                                                                                         |
| - | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1 | news\_dedup 新增公共助手：existing\_news\_ids(where) + publish\_time 规范化测试固化       | 单测绿（naive/tz-aware/纯日期三态）                                                                  |
| 2 | 清扫脚本 scripts/ch/purge\_news\_data\_rr\_dup.py（dry-run/execute 两档，备份前置，断点幂等） | dry-run 对账输出 = 143,914 双版本 + 1,400 修正重插                                                    |
| 3 | 正式执行清扫 + 自验证                                                                | 执行后 research\_report 类别 count() == uniqExact(news\_id)，且双版本 id 的 publish\_time 全部 00:00:00 |
| 4 | CAND-DAT-025 登记状态更新 + news/announcement 8h 偏移另立 CAND                        | registry 两条目可查                                                                             |

## 6. 不做（负空间）

* 不改 news\_data 表结构（ORDER BY/PARTITION/版本列全保留）

* 不动 news/announcement/macro\_data 类别数据（关联发现另立项）

* 不做跨分区月末边界的特殊处理（ALTER DELETE 按谓词执行，天然覆盖所有分区，无此问题——该问题仅存在于 OPTIMIZE DEDUPLICATE 方案）

* 不追溯考古 7-15 老批的具体写入代码路径（无论哪条路径，现状处置相同；写入侧规约防的是未来）

## 7. 开放问题

| 问题                                     | 建议                                                    | 决策状态 |
| -------------------------------------- | ----------------------------------------------------- | ---- |
| 老批单行 1,400 个 id 的 +8h 修正重插是否随本轨做       | 做——量小且同脚本一次完成，留著则研报时间长期残留 1,400 条错行                   | 待人裁定 |
| news/announcement \~760 万行 8h 偏移专项的优先级 | 建议 P0——前视偏差直接污染回测结论，先于一切依赖新闻时间戳的策略开发                  | 待人裁定 |
| 清扫执行窗口                                 | 常态采集为增量小流量，ALTER DELETE mutation 与其可并行；无需停写，但建议避开备份窗口 | 待人裁定 |

## 8. 修订记录

| 日期         | 版本    | 改动        | 理由                                                                                           |
| ---------- | ----- | --------- | -------------------------------------------------------------------------------------------- |
| 2026-08-27 | 1.0.0 | 初稿（draft） | CAND-DAT-025 立项设计：冗余根因锁定为 publish\_time 时区语义漂移（非键设计缺陷）；三件套方案 + news/announcement 8h 偏移关联发现登记 |

