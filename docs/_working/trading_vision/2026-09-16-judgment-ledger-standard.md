---
ttl: task_bound
completes_when: 判定台账标准 v0.1 全仓推广——每个产出判定的模块接电时必接台账发射器；三张首批表已建并产出结算数据；meta-回测 harness 出具首份逐层归因报告。
---

# 判定台账标准 v0.1（Forecast Ledger Standard）

> 2026-09-16，st-overseer-20260916。本标准=Owner 洞察的全仓制度化："每一个产出判定的模块，都必须把判定写进数据库表"——没有台账的判定无法回测，无法回测的判定=自欺。全仓已有三处雏形（regime_snapshot_history/prediction_log/brier_calibration.py），本标准将其定形并推广。

## 一、核心铁律：判定与结算分离

1. 判定时刻写死判定内容（PIT 锚：asof_ts+input_cutoff_ts）。
2. 真实结果（outcome 列组）**只能由结算器事后回填**——判定模块无权写结算列。
3. 表引擎 MergeTree 只增不改；修订=新 judgment_id 追加（禁 UPDATE 既有行）。
4. 任何"预测准确率"统计必须可由 judgment_id 联结 outcome 独立复算。

## 二、通用列（所有判定台账表的公共骨架）

```sql
judgment_id String,          -- ULID
module_id String,            -- MOD-xxx
model_version String,        -- 判定算法版本
asof_ts DateTime64(3,'UTC'), -- 判定时刻（PIT 锚）
input_cutoff_ts DateTime64(3,'UTC'), -- 数据截断时刻
horizon String,              -- 预测时段：intraday_rest/next_day/intraday_session 等
subject String,              -- 判定对象：index:000300.SH / sector:880-xxx / stock:600519.SH
payload String,              -- JSON：模块自定义判定内容
confidence Float64,          -- 置信度 [0,1]
inputs_ref String,           -- 输入快照指纹/引用清单
run_id String,               -- 血缘
-- 结算列组（判定器禁写，结算器回填）：
outcome_ts Nullable(DateTime64(3,'UTC')), outcome_value Nullable(String),
eval_method Nullable(String), eval_score Nullable(Float64),
evaluated_at Nullable(DateTime64(3,'UTC')), evaluated_by String DEFAULT 'settlement_agent'
```

## 三、首批三表 DDL 草案（作战室三任务，库=c1_market，DDL-as-Code 走 apply_market_tables_ddl 正道）

### 表 1 `judgment_intraday_market_state`（盘中大盘状态，分钟级）
通用列 + payload JSON 结构：
```json
{"state_label":"低迷|防御|震荡|进攻|亢奋","state_probs":{"低迷":0.7,"防御":0.1,"震荡":0.15,"进攻":0.05,"亢奋":0.0},
 "evidence":{"volume_ratio":0.82,"breadth_ratio":0.41,"attack_sector_count":0,"attack_sectors":[],"gap_pct":-0.3,
 "overnight_ref":{"us":"down","futures":"down"}},"rest_of_day":{"tail_dir_prob_down":0.68,"amp_range_pct":[0.2,0.8]}}
```
outcome：realized_tail_return / realized_close_vs_open / state_realized / brier_contrib。

### 表 2 `judgment_next_day_forecast`（次日概率，T 日盘后）
通用列 + payload：
```json
{"p_up":0.35,"p_flat":0.25,"p_down":0.40,"quantiles":{"q10":-1.2,"q25":-0.5,"q50":0.05,"q75":0.6,"q90":1.3},
 "expected_vol_pct":0.9,"expected_range_pct":1.4}
```
outcome（T+1 收盘回填）：realized_return / realized_label / brier_score / log_loss / calibration_bucket。

### 表 3 `judgment_daily_plan` + `judgment_plan_verification`（晨间预案+盘中验证）
daily_plan payload：
```json
{"scenarios":[{"scenario_id":"S1","trigger":"open_gap_pct>0.5 AND broker_sector_chg>1.0","action":"no_chase_wait_pullback","path_prior":0.3},
 {"scenario_id":"S2","trigger":"10:00前跌破昨收-0.5% AND amount_ratio<0.8","action":"stand_aside","path_prior":0.45},
 {"scenario_id":"S3","trigger":"...","action":"...","path_prior":0.25}],
 "inputs_scope":["昨收全量","美股夜盘","股指期货","隔夜新闻情绪","宏观日历"]}
```
plan_verification：scenario_hits[{scenario_id,trigger_ts,trigger_price}] / actual_scenario_id / plan_followed Bool / deviations[]（对接作战室既有"执行不一致"记账）/ plan_quality_score。
**铁律：trigger 必须是可测量表达式**——"如果走弱"不合格。

## 四、结算器规范（共享组件，扩展 brier_calibration.py）

- 结算方法：brier_score（概率判定）/ log_loss / hit_rate / reliability 曲线 / Diebold-Mariano（预测者对比）。
- 触发：事件驱动（收盘数据入库事件→按 horizon 扫描到期未结算行→回填），禁 cron/sleep-loop。
- 输出：逐 judgment 结算行 + 聚合报告（按 module_id/model_version/时间窗聚合）——这份聚合报告=逐层归因报告的数据源（Phase 5）。
- 不可结算（上游断供等）→ status=unresolvable+原因，禁跳过式静默。

## 五、推广政策（Phase 5 制度化）

1. **接电即接台账**：骨架任一模块从"覆盖未接电"转"已接电"时，必须同时具备台账发射器（本标准 schema）——纳入施工验收项。
2. **新模块出厂必带发射器**：施工 SOP 验收清单加一行"判定输出接台账？"。
3. **meta-回测**：结算器聚合报告自动生成逐层归因（L1-L5 各自贡献账本），支撑"每层加不加分数据说话"。
4. 老模块补接：按黄灯接电顺序逐个补，不专项（避免过度工程）。

## 六、作战室三任务=首批三实例

| 任务 | 台账表 | 模块 |
|---|---|---|
| 任务 1 盘中实时走势 | judgment_intraday_market_state | 盘中 L1 跟踪件（新增，挂编排器 T3 接口）|
| 任务 2 明日概率 | judgment_next_day_forecast | 盘后概率件（接 brier 日常闭环）|
| 任务 3 验证昨日计划 | judgment_daily_plan+judgment_plan_verification | 场景引擎（对接作战室 MOD-PLAN-018 场景样本+执行不一致记账）|

与编排器蓝图（会话分支待合并）关系：作战室=计划与验证载体，编排器=晨判拍板分发；盘中 L1 跟踪件=两者共同缺口的新增件，挂蓝图 T3 接口签名（intraday_revoke）。蓝图合并回 dev 后补录"作战室三任务产品需求"附录（随本标准执行）。

## 七、情感维度关联（待查登记）

情绪周期模块（G07 五阶段候选，挂起中）与表 1 state_label 的映射关系待核查：G07 情绪阶段可作 L1 状态判定的证据维度之一。登记入待查清单，不阻塞施工。
