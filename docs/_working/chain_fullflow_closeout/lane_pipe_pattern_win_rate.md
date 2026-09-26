---
ttl: task_bound
---

# lane_pipe · pattern_win_rate（图形胜率物化链）— 判定：不通 ❌

## 六向台账

### 1 做什么
把 `c1_market.market_pattern_event`（3479 万行，新鲜 09-24）按 pattern×timeframe×regime×direction×fwd_window 物化成胜率汇总 `market_pattern_win_rate`，供图形信号可考性/做T矩阵消费。

### 2 依据
- 任务在册：`pattern_win_rate_materialize`（`--help`/list 面在 271 任务集内；透传退出码物化）。
- 目标表在册：`c1_market.market_pattern_win_rate`（列 pattern_id/timeframe/regime_tag/direction/fwd_window/n_events/hit_rate/avg_fwd_ret/low_sample/updated_at）。

### 3 改动点（候选，不改）
- 物化腿崩（`task_runs` 记 exit 1），汇总不再推进；
- 该表**无 trade_date/日期主键**（仅 updated_at），故新鲜度只能靠 `updated_at` 判——骨架探针误判 datecol=None 即源于此（病灶 C 类：探针选列失败≠表无数据）。

### 4 判据
`pattern_win_rate_materialize` 近一日 SUCCESS 且 `max(updated_at)` 落在 T-1；下游读到最新胜率。

### 5 读数（实测·只读）
- 最近一次运行：2026-09-24T09:43:13Z status=**FAILED** error=`pattern_win_rate_materialize 退出码 1（物化失败，透传）`。
- 表实测 4,239 行（非空），但物化停摆 → 汇总陈旧（updated_at 未随事件表推进）。

### 6 风险
- 图形胜率是"可考性三态"门输入，陈旧→误放行/误否决图形信号。

## 自审三态
- **PASS**：FAILED 原文取自 task_runs；表非空但停摆由 count+物化失败共证；探针列选择误判根因写清。
- **FAIL（未做）**：未跑物化取 exit-1 栈顶（属执行+写）。
- **待裁**：物化脚本报错定位与修复越只读红线，交 owner 车道。

## 处方与复现命令（全部只读）
```
python -c "import sqlite3;c=sqlite3.connect('file:data/integrator_progress.db?mode=ro',uri=True);print(c.execute(\"SELECT started_at,status,error_msg FROM task_runs WHERE task_id='pattern_win_rate_materialize' ORDER BY started_at DESC LIMIT 5\").fetchall())"
python -c "from zephyr.data import ch_writer as c; print('rows/maxupd=',c.query('SELECT count(),max(updated_at) FROM c1_market.market_pattern_win_rate FORMAT TSV'))"
grep -rn "pattern_win_rate_materialize\|market_pattern_win_rate" scripts src --include=*.py | head
```
处方（待授权）：查物化脚本 exit 1 根因（多半同日期/类型比较或除零样本），修后跑一次并校验 `max(updated_at)` 推进；同时给该表加 `updated_at` 新鲜度自检尺。
