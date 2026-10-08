---
ttl: task_bound
completes_when: 线C施工（C3 生成器手术+validator+对抗测试）与 C4 首报落地并经 Owner 复核后，本簿转归档参考；口径变更须先改本簿再改码
title: C1 trigger_facts 实数化方案簿（st-fig13-followup-20261006 线C 挖矿件）
owner: st-fig13-followup-20261006
---

# C1 trigger_facts 实数化方案簿（st-fig13-followup-20261006 · 线C挖矿件1）

> 状态：**封矿**（挖矿完成，施工=C3）。生成器手术按本簿执行；口径变更须先改本簿再改码。
> 输入考古：图12 F2 血肉批 `dd686019c25`（observed_runs 静态语义层硬编码+as_of 标注+zero_trigger_verdict）；
> 图9 F4 `85808465c93`（trigger_facts.observed 三态值域 int/float/str/null）；图13 现状=obs 文本投影 44 格（生成器 :2891-2899）。

## 1. 图12 配方考古结论（为什么图13 要再升一级）

| 维度 | 图12 配方（dd686019c25） | 图13 v2 目标（本簿） |
|------|--------------------------|----------------------|
| 计数方式 | 离线挖矿（车道人工跑 DB）→ 数值硬编码进生成器语义层 | **生成器活查**：每次重生成实时查询 |
| 刷新语义 | 重生成不刷新（as_of 冻结在挖矿日，DSC-20 fallback 里已出现 stale_as_of 症状） | **重扫即刷**（as_of=生成时刻） |
| 失败面 | 无（挖矿时已保证） | **降级不崩**：查询失败→count=null+no_count_reason，图照出 |
| 结构 | as_of/evidence/expected_runs_window/observed_runs/zero_trigger_verdict | as_of/metric/count/source(+evidence+last_run+no_count_reason) |

学费吸收：图12 stale_as_of 实证"静态数会撒谎"；本簿全部计数面改为生成时实查，静态文本只留 evidence 注记。

## 2. 图13 口径（逐机制类，六向台账：真源/窗口/计数语义/降级/消费/边界）

### 机制A · APScheduler 槽（26 节点，src=schedule）
- **真源**：`data/integrator_progress.db` task_runs 表（SQLite **ro-uri 只读**，图12 同款 `sqlite_ro_uri` 惯例；非 CH，不走 DatabaseService）。
- **join 面**：生成器既有 `scan_task_mounts()` 的 `tasks_by_slot`（tasks.yaml×schedule join，已滤 disabled）→ 节点 slot 声明 → task_id 集。
- **窗口**：近 30 自然日（`started_at >= as_of-30d`，as_of=生成时刻 UTC）。
- **计数语义**：`count = Σ task_runs(该节点全部 slot 的全部 task_id, 30日窗)`；**主指标**=task_runs_30d。
- **降级**：DB 文件缺失/只读打开失败 → count=null + no_count_reason="integrator_progress.db 不可读（ro-uri 打开失败）"。
- **消费**：validator（production A 节点 count 必在）、季度账本红3 旁证、Owner 阅图。
- **边界**：计数含假日零自然（假日无行=0 是真相，不伪造）；退役史格 D13-16 计数为历史残行，evidence 注记"退役史格计数=退役前残迹"。

### 机制B · Windows 计划任务（10 节点，src=schtasks）
- **真源**：`Get-ScheduledTaskInfo`（**只读查询**，与既有 `scan_registered_schtasks` 同通道同降级；`--skip-schtasks` 时同跳过）。
- **计数语义**：`metric=schtasks_lastrun_in_window`；`count = 1 if LastRunTime ∈ 预期节拍窗 else 0`；`last_run`=LastRunTime 原值。
  - 节拍窗判定：每日类槽窗=72h（容忍一个休市日+时区漂移）；周类=10d；D13-42 守护族=72h。判据写死在 TRIGGER_CADENCE 常量表，逐节点可覆盖。
- **产物面旁证**：run[] 日志/表**不进 count**（实证：六份运行日志五种格式、fundflow 进度条乱码、sim_bridge 空文件——异构面正则机读=假绿温床，自裁弃；日志证据留在 evidence/EXEC 文本）。
- **降级**：查询失败/任务不在册 → count=null + no_count_reason="schtasks 查询面不可用"（禁把"查不到"读成"没注册"，沿用 scan_registered_schtasks 口径）。
- **边界**：改名批（B1）后 tn=新名，查询面按 tn 逐个查；任务在册但从未跑（LastRunTime 空）→ count=0（真零触发）。

### 机制C · 进程内段/事件（9 节点：dloop_stage×7 + event×2）
- **真源**：CH 产物表（`DatabaseService.get_clickhouse_conn(role='reader')`，**只读**；表名真源=TableRegistry，图内/簿内一律裸逻辑名）。
- **逐节点产物表**（挖矿钉死，施工按此表）：
  - D13-21 → `judgment_intraday_market_state`（按 `toDate(asof_ts,'Asia/Shanghai')` 最新上海日行数；骨架 §2 :104 实证 09-24=2 行在产）
  - D13-34 → `decision_daily`（全表行数+max(trade_date)；骨架 §2 :124 实证 69 行/max=09-24）
  - 其余 C 节点（D13-20/22/23/33/44/27/43）无独立产物表 → count=null + no_count_reason="进程内段无独立产物表面（产物归上游槽节点计数）"，evidence 保留 obs 文本。
- **窗口**：当日（上海日）；count=当日行数。
- **降级**：CH 不可达/超时(10s) → count=null + no_count_reason="CH reader 不可达"。

### 机制D · 无调度（3 节点：D13-08/09/31）
- D13-08：`logs/source_health_YYYYMMDD.log` 文件数（30 日窗内）= count，source=glob 面EXEC 口径同源。
- D13-09/31：无产物面 → count=null + no_count_reason。

### gap 四格（D13-G01..G04）
- 维持家族先例：trigger_facts=None 不灌（F4/图12 先例，validator 同判）。

## 3. trigger_facts 结构 v2（生成器输出 schema）

```yaml
trigger_facts:
  as_of: '2026-10-08T…'          # 生成时刻（head_commit_time 或 --as-of 覆盖）
  metric: task_runs_30d | schtasks_lastrun_in_window | table_rows_latest_shanghai_date | source_health_logs_30d | none
  count: <int|null>              # null=不可数（必伴 no_count_reason）
  source: <真源指针字符串>        # integrator_progress.db:task_runs(ro-uri) / Get-ScheduledTaskInfo(只读) / DatabaseService CH reader(表名) / logs glob
  evidence: <obs 文本投影（保留，口径注记）>
  last_run: <ISO|仅B类>          # LastRunTime 原值
  no_count_reason: <仅不可数节点>
```
- 兼容：map9 validator 已裁定 observed 三态值域（int/float/str/null）——图13 不用 observed 键名（图12 家族键），用 count；validator CV-BLOOD 判据面只认 count/no_count_reason，不跨图污染。

## 4. validator 口径同步（CV-BLOOD 增补腿）

production 节点 trigger_facts **必带 count 或 no_count_reason 二选一**（双缺=硬红；count=null 且无 reason=硬红；reason 为空串=硬红）。
- production 15 台逐台预演：A×5 全 countable；B×7 全 countable（schtasks 在窗判定）；C×2 countable（产物表）；D×1 countable（日志 glob）→ **15/15 必有 count**，no_count_reason 逃生面只对非 production 结构节点开放。
- 非 production：trigger_facts 在图（f2_done 四字段硬判不变），count 可空但 reason 必填。

## 5. 对抗测试新增用例（tests/gov/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py）

| 用例 | 红/绿 | 断言 |
|------|-------|------|
| production 无 count 无 reason | 红 | validator 报 CV-BLOOD 硬红 |
| count=null 且无 reason | 红 | 同上 |
| no_count_reason 空串 | 红 | 同上 |
| A 类正常计数 {metric,count,source} | 绿 | validator PASS 且 count==预期整数 |
| 查询失败降级 | 绿 | count=null+reason 在图、生成不炸、validator PASS（非 production） |
| gap 格 trigger_facts=None | 绿 | 家族先例保持 |

## 6. 施工面清单（C3 执行单）

1. 生成器：新增 `scan_trigger_counts(root, *, skip_schtasks)`（SQLite ro-uri + schtasks Info + CH reader 三通道，各自独立降级）；`build_nodes` 的 trigger_facts 装配点换源（:2891-2899）。
2. validator：CV-BLOOD 节点级增补腿（§4 判据）。
3. 对抗测试：§5 六用例。
4. 重生成+validator PASS+全套件绿 → 随 C 批落地。

## 7. 自审闸（封矿三态裁定）

- 增量趋零判据：图12 配方/图9 observed 值域/图13 现状 obs 投影三处考古均已落簿；产物表面 15 production 逐台钉死（骨架 §2 行号在案）；无未决考古项 → **趋零成立**。
- 三态裁定：GO（封矿，转 C3 施工）。
- 遗留不进本批：decision_daily 全表 69 行 max=09-24 的"停更疑"归 D13-34 车道（本批只装计数面，不判停更——假日窗 09-25..10-07 全假在案，09-24 后无交易日，非断供证据）。
