---
ttl: task_bound
---

# lane_pipe · news_sentiment_score（新闻情绪打分链）— 判定：不通 ❌

## 六向台账

### 1 做什么
对 `c3_fundamental.news_data` 逐条新闻打情绪分，落 `c1_market.news_sentiment_score`，供仪表盘情绪页、每日门闸快照、预测日志消费。

### 2 依据
- 消费方在册（grep 读点，`src` 命中）：`frontend/dashboard/api_server.py`、`frontend/dashboard/web/pages/sentiment.html`、`strategy_pipeline/daily_gate_snapshot.py`、`reporting/prediction_log_writer.py`。
- 触发在册：计划任务 `ZephyrAlpha_NightlySentiment`（`scripts/data/run_nightly_sentiment.py`），LastRun=2026-09-25 22:30，Next=2026-09-26 22:30，State=Ready。
- 上游 `news_data` 新鲜（实测 max publish_time=2026-09-26）。

### 3 改动点
- 打分产出面：news_sentiment_score 停更（详见读数），疑似 LLM 后端(Ollama)失效连带（见 `lane_pipe_llm_backend.md`）或写腿改名后旧表停写（换名旧口径）。
- 需辨：夜间任务现写的是 `news_sentiment_window`（新鲜，09-24）还是本表；若已换表而本表无退役处置 = 表族换名残留（病灶 D 类）。

### 4 判据
`max(publish_time) FROM c1_market.news_sentiment_score` 应 ≤T-1 日；消费方读到近窗分值。

### 5 读数（实测·只读）
- `SELECT count(),max(publish_time) FROM c1_market.news_sentiment_score` → 7,733,898 行 · max=**2025-09-09 00:00:00+08:00**（冻结约 **一整年**）。
- 兄弟表 `news_sentiment_window` max window_ts=2026-09-24（新鲜）→ 高度疑似"打分换面到 window，score 成僵尸壳仍被消费"。
- 上游 `news_data` max=2026-09-26（新鲜）→ 断点在打分腿，非采集腿。

### 6 风险
- 仪表盘/门闸读一年前情绪 = **值级看不出**（有行数、只是不更新），下游据此决策失真。

## 自审三态
- **PASS**：冻结日期由 SELECT 实测确证；消费方 grep 命中给到文件级锚点；区分了采集腿(新鲜)与打分腿(停更)。
- **FAIL（未做）**：未打开 `run_nightly_sentiment.py` 确认它当前写 score 还是 window（需读脚本，本轮按只读可继续但已近上下文上限，列下一步）。
- **待裁**：若确认 window 为唯一正解、score 应退役 → 退役需 Owner 门位（注册表净删/生产流转，§5）；本轮不自裁。

## 处方与复现命令（全部只读）
```
# 5.1 冻结确证
python -c "from zephyr.data import ch_writer as c; print('score_max=',c.query('SELECT max(publish_time) FROM c1_market.news_sentiment_score FORMAT TSV'))"
python -c "from zephyr.data import ch_writer as c; print('window_max=',c.query('SELECT max(window_ts) FROM c1_market.news_sentiment_window FORMAT TSV'))"
# 5.2 确认夜间任务现写哪张（读脚本，不执行）
grep -nE "news_sentiment_score|news_sentiment_window|INSERT" scripts/data/run_nightly_sentiment.py
# 5.3 确认消费方读旧表（读点）
grep -rn "news_sentiment_score" src/zephyr/strategy_pipeline/daily_gate_snapshot.py src/zephyr/frontend/dashboard/api_server.py
```
处方（待授权）：① 若 window 为真源：把 `daily_gate_snapshot`/`api_server`/`prediction_log_writer` 读点切 window，再走退役流程处置 score（登记 known_data_gaps 或退役，Owner 门位）；② 若 score 应续写：修打分腿（多半依赖 LLM 后端，见 llm 本）。二选一均需实跑打分一次带插桩确认落库（要授权）。
