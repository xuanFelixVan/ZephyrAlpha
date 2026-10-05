---
ttl: task_bound
---

# lane_pipe · consensus_daily（一致预期构建链）— 判定：不通 ❌

## 六向台账

### 1 做什么
从研报/分析师预期聚合逐日一致预期，内部 build 落 `c3_fundamental.consensus_daily`，供估值、因子、回测消费。

### 2 依据
- 任务在册：`tasks.yaml` `consensus_daily_build`，source=`internal`，schedule=`research_nightly`。
- 目标表在册：`c3_fundamental.consensus_daily`（实测 6,797,719 行 · max trade_date=**2026-09-14**）。
- 已在册缺口：`known_data_gaps.yaml:1010` `consensus_daily_value_cols_pit_broken` status=**open**。
- 修复旁证：另有 `c3_fundamental.consensus_daily_repaired`（165万行 · max=2026-09-15）——重算换名旁表，主表与 repaired 双面孔。

### 3 改动点（候选，不改）
- build 计算腿崩（见读数）；
- PIT/值列口径 open；主表与 `_repaired` 表并存 → 消费方读哪张需锁真源（病灶 B/D 交叉）。

### 4 判据
`consensus_daily_build` 近一日 SUCCESS；主表 `max(trade_date)` 推进；主/修复表真源方向唯一。

### 5 读数（实测·只读）
- 最近一次运行：2026-09-18T22:30:20Z status=**FAILED** error=`'>' not supported between instances of 'str' and 'datetime.date'`。
- 主表停在 09-14（研究夜档每晚应推进，实测 09-18 后再无成功样本）；repaired 表停在 09-15。

### 6 风险
- 一致预期是估值/因子核心输入，停更=下游集体用旧值，值级不易察觉。

## 自审三态
- **PASS**：FAILED 原文、主/修复表新鲜度、open 缺口条目号均给到锚点。
- **FAIL（未做）**：未确认消费方当前读主表还是 repaired 表（列下一步）。
- **待裁**：主/修复表收敛为唯一真源属结构处置，需 owner 车道。

## 处方与复现命令（全部只读）
```
python -c "import sqlite3;c=sqlite3.connect('file:data/integrator_progress.db?mode=ro',uri=True);print(c.execute(\"SELECT started_at,status,error_msg FROM task_runs WHERE task_id='consensus_daily_build' ORDER BY started_at DESC LIMIT 5\").fetchall())"
python -c "from zephyr.data import ch_writer as c; print('main=',c.query('SELECT max(trade_date) FROM c3_fundamental.consensus_daily FORMAT TSV'),'repaired=',c.query('SELECT max(trade_date) FROM c3_fundamental.consensus_daily_repaired FORMAT TSV'))"
grep -rn "consensus_daily" src/zephyr --include=*.py | grep -iE "FROM|SELECT" | head
```
处方（待授权）：① 与 financial_derived 同修日期比较崩（同错）；② 锁 consensus_daily 与 _repaired 真源方向（RULE-SSOT），避免双写；③ 建后补新鲜度自检尺。
