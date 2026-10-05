---
ttl: task_bound
---

# lane_pipe · financial_derived（衍生财务构建链）— 判定：不通 ❌

## 六向台账

### 1 做什么
从三表+指标衍生财务字段，内部 build 任务落 `c3_fundamental.financial_derived`，供估值/因子消费。

### 2 依据
- 任务在册：`tasks.yaml` `financial_derived_build`，source=`internal`，schedule=`nightly_financial`，`incr=True`。
- 目标表在册：`c3_fundamental.financial_derived`（实测 306,526 行 · max report_period=2026-06-30）。

### 3 改动点（候选，不改）
- build 计算腿：`task_runs` 报 `'<' not supported between instances of 'str' and 'datetime.date'` → 构建器内 str 与 date 直接比较崩（同类崩也命中 consensus_daily，见对应 lane，提示公共日期规整缺一道）。

### 4 判据
`financial_derived_build` 近一日 SUCCESS 且 `max(report_period)` 推进到最新披露季。

### 5 读数（实测·只读）
- 最近一次运行：2026-09-24T23:26:42Z status=**FAILED** error=`'<' not supported between instances of 'str' and 'datetime.date'`。
- 近 24h 状态分布（`task_runs`）：SUCCESS 3958 / FAILED 107 / STALE 32 / DEFERRED_PERSISTENCE 14 / RUNNING 3；financial_derived 命中 FAILED。
- 表数据 report_period 停在 2026-06-30（可能受 build 崩拖累未推 Q3）。

### 6 风险
- 衍生财务停更 → 下游估值/因子读到旧季；build 每晚失败但非致命告警易被忽略。

## 自审三态
- **PASS**：失败原文与时间戳取自 `task_runs`（只读 SQLite）；表读数取自 CH SELECT。
- **FAIL（未做）**：未定位到抛异常的具体行号（未读 build 实现，近上下文上限）。
- **待裁**：修复属代码改动，越只读红线，本轮不开方执行；登记给 owner 车道。

## 处方与复现命令（全部只读）
```
# 5.1 崩态原文
python -c "import sqlite3;c=sqlite3.connect('file:data/integrator_progress.db?mode=ro',uri=True);print(c.execute(\"SELECT started_at,status,error_msg FROM task_runs WHERE task_id='financial_derived_build' ORDER BY started_at DESC LIMIT 5\").fetchall())"
# 5.2 新鲜度
python -c "from zephyr.data import ch_writer as c; print(c.query('SELECT max(report_period),count() FROM c3_fundamental.financial_derived FORMAT TSV'))"
# 5.3 定位构建器（读点，不执行）
grep -rn "financial_derived" src/zephyr/data --include=*.py | grep -iE "build|def |INSERT"
```
处方（待授权）：修 build 腿日期比较（统一 `datetime.date` 或在比较前 `_norm_date_str`），并补一条"build 失败即 critical 告警"的自检尺；修后需带插桩实跑一次确认 report_period 推进（要授权）。同族 consensus_daily_build 同错，建议一并。
