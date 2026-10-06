---
ttl: task_bound
title: "新闻评分链恢复报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-2b 新闻评分链恢复报告（P0 第二甲止血）

## 1. 断点根因（探针已核，非猜测）

- `c3_fundamental.news_sentiment_score`：7,733,898 行，`max(publish_time)=2025-09-09`，
  `max(scored_at)=2026-09-24 07:48 UTC`——该表是 st-metaq-gc-20260924 会话于 2026-09-24
  用 `scripts/governance/meta_question/wo_a2legs/backfill_news_sentiment.py` 一次性回填建成
  （存量窗口 2010-01-01 → **CUT=2025-09-09 硬编码**，任务件 `[TTL] task_bound` 冻结）。
- **根因=表建成即无日更生产者**：全仓唯一写入口是上述一次性回填件，其 CUT 硬编码使它
  结构性无法越界；调度器（`src/zephyr/data/scheduler.py`）无任何槽位接该表。
  不是模型丢失、不是 LLM 通道变更、不是词典损坏——`RuleBasedSentimentScorer` 及其词典
  全部在位可跑（首批验证 1.7s 得分 14k 行）。
- 原料 `c3_fundamental.news_data`（FINAL）鲜至 2026-10-04，采集腿健康。
- 关联面：`c1_market.news_sentiment_window` market 窗已自愈（194 行至 10-03，nightly_sentiment
  08:20 槽 09-10 接线生效）；**symbol 窗止于 08-21**——`run_nightly_sentiment_batch` 调
  `compute_nightly_sentiment` 未注入 linker（linker=None→仅 market 级聚合），symbol 腿
  无生产者，属另一独立断点（本次不动，见 §5）。

## 2. 修复面（最小修复，四文件+一册）

| 文件 | 变更 |
|------|------|
| `src/zephyr/intelligence/news_score_daily.py`（新） | 日更+回补唯一生产者：口径单源 `RuleBasedSentimentScorer`；`caliber_version` 经 analyzer 指纹单点；日粒度分片；ProgressStore 断点续传；reader/client/store 全注入可测 |
| `src/zephyr/intelligence/news_sentiment_analyzer.py` | 新增 `caliber_fingerprint()` 模块级单点（指纹=词典+反转/ST 正则 SHA256 截断；与 wo_a2legs 原件逐字节同式，现网 7.7M 行全为 `rule-a0e3f2b6d3` 已探针核实） |
| `src/zephyr/data/scheduler.py` | 新槽 `nightly_news_score`（惰性导入+总闸旗标+fetch_perf+alerter 降级，全抄 nightly_sentiment 既有模式） |
| `src/zephyr/data/config/schedule.yaml` | 注册 `nightly_news_score: cron "50 8 * * *"`（晚于 nightly_sentiment 20 分槽，给 news_data flush 留缓冲；全周运行） |
| `docs/03_modules/_cross_layer/database/business_data_categories.yaml` | 补注册品类 `news_sentiment_score`（原回填件因品类缺席被迫硬编码表名；本登记走 TableRegistry 正门，producer/schedule 字段挂接） |

纪律留痕：capability_lookup 反查（真源 MOD-INT-AISA）、depgraph 设计节点
node_id=16131697、add_module_translation 登记、batch_creation_tokens 登记、
lock_files claim 全部先行；wo_a2legs 原回填件零触碰（他件 task_bound 冻结）。

## 3. 口径与幂等契约

- 打分一律经在册 `RuleBasedSentimentScorer`（规则法；LLM 轨**不**接入本表——
  `nightly_sentiment_llm` 旗标对照期仅作用于 news_sentiment_window，逐条分表切 LLM
  须 Owner 门位+口径评审）；`method='rule'` 与存量 7.7M 行同法。
- `caliber_version='rule-a0e3f2b6d3'`（指纹单点自动续版本，换词典即新版不覆写旧行）。
- 幂等：ReplacingMergeTree(ingest_ts) 同键 `(caliber_version,news_id,publish_time)` 替换，
  重跑/补跑/重扫零重复（首批实测 dup=0）；只读 news_data 零改写母表。
- 自愈双轮：近 30 日缺口补跑（覆盖差集）+ 近 2 日增量重扫（吸收 SCD 晚到版本）。
- 断点续传：ProgressStore 统一范式（task_id=`news_sentiment_score_daily`/`_backfill`，
  last_key=最后完成日；中断重启自动续跑）。

## 4. 回补进度（实测读数）

- **首批验证（最近 7 天窗）**：`run_news_score_batch(lookback=7)` → 8 天
  2026-09-27..10-04 全成，14,158 行，1.7s，零失败；CH 复核非零率 13.5%~24.1%/日
  （label 分布：positive 1537 / negative 1089 / neutral 11532），dup=0，
  表 max(publish_time) 推进到 2026-10-04。
- **全量回补**：缺口实测 213,375 行（2025-09-10..2026-10-03，`news_data FINAL` 探针）；
  以 `python -m zephyr.intelligence.news_score_daily --backfill --start 2025-09-10
  --end 2026-10-03` 后台执行（断点续传可中断重跑；日志
  `.runtime/sessions/st-datasop-20260930/staging/news_score_backfill_full.log`；
  reaper keep 已登记 `news_score_daily` 防误杀）。终态读数见 §4.1。
- 长期防再断：`nightly_news_score` 槽 08:50 日频自动接管，断供哨兵
  （data_supply_sentinel/calendar_coverage_check）既有层覆盖本表。

### §4.1 全量回补终态（2026-10-04 实测）

- `--backfill --start 2025-09-10 --end 2026-10-03`：exit=0，`ok=true`，逐日零失败，
  覆盖差集探针=**0 缺日**（2025-09-10..2026-10-04 与母表 FINAL 逐日对齐）；
  月度量与母表逐月 1:1（202510=1883/202511=1568/.../202609=61659）。
- 表终态：**7,947,273 行**（断供前 7,733,898 + 回补 213,375），`max(publish_time)=2026-10-04`，
  非零 2,966,478（37.3%），全键 FINAL 去重=0。
- 全键查重口径备注：`(caliber_version,news_id)` 二元组有 20,673 例复用——系**母表
  news_data FINAL 自身 news_id 复用特性**（同 news_id 多发布时戳，20,673 例），评分表
  忠实镜像，非重复缺陷；真幂等键=三元组（FINAL 去重=0）。
- 收敛语义（诚实留痕）：`toDate>2025-09-09` 窗评分行 213,841 vs 母表 FINAL 213,376
  （+465，0.2%）——母表 SCD 版本修正（发布时戳更正型）的 as-of 残影：评分表按
  "打分时刻所见"留版本（与原回填件 PIT 哲学一致），晨批 retrail 近 2 日自动收敛增量，
  更早修正残留由消费侧按 PIT join 母表裁决；非缺陷。

## 5. 移交与边界（诚实降级项）

- **symbol 窗断腿（未修，独立断点）**：symbol 窗止 2026-08-21，根因=夜间批未注入
  `NewsSymbolLinker`（market 窗链路 09-10 接线时只接了 market 级）。修复面在
  `run_nightly_sentiment_batch`（注入 linker+symbol 级聚合落表），涉及 window 表
  scope=symbol 写路径——超出本单修复面（新闻逐条分表），建议另开单
  （P1，消费方=regime/情绪线 symbol 级特征）。
- LLM 轨对照期（ollama 11434 存亡）为既有 OWNER-GATE 事项，与本表无关。
- 品类册中 `market_news_sentiment_window` 条目在册内出现两处（line 3585/5479 疑似
  追加段重复）——非本单引入，移交册务班核（本单未动该两条）。

## 6. 验证

- 单测：`tests/intelligence/test_news_score_daily.py` 5 passed（注入式，tmp_path/零真实 CH）；
  既有 `test_news_llm_scorer.py` 3 passed（无回归）；scheduler.py 语法核过。
- 生产验证：§4 首批读数 + 全量回补终态（CH 探针：总行数/月度覆盖/零重复）。
