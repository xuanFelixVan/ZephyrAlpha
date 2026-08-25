---
blueprint_id: MOD-DAT-AUTO-BACKFILLER
module_name: auto_backfiller
domain: D_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_DATA
path: src/zephyr/data/auto_backfiller.py
granularity: file
---

# MOD-DAT-AUTO-BACKFILLER auto_backfiller 蓝图（自动回填器）

> **module_id**: MOD-DAT-AUTO-BACKFILLER | **域**: D_DATA | **优先级**: P1
> **来源**: B10-01815（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，§29.2-7）
> 代码：`src/zephyr/data/auto_backfiller.py`

## 0. 定位

事件驱动的自动回填器：输入触发事件（新因子上线 new_factor / 公式升级
formula_upgrade / 数据源修复 data_source_fix），按日期分片规划回填，经注入
执行体逐分片执行，10% 随机抽样验证，完成后更新血缘并触发 auto-retrain。

与既有族分工（查重裁定）：
- MOD-L00-004 backfill_checker（10603308，stable）：L10 周末缺口检测器——
  查 CH 实际行数发现**行情数据缺口**并精准补下载（定时/数据面向）。
  本模块为**因子/公式/数据源修复事件**触发的回填编排（事件面向），不复制
  其缺口检测与下载通道逻辑；缺口语义对齐走设计边，不 import。
- MOD-L00-004 scheduler（10603338）：任务调度器；本模块的触发事件装配与
  定时挂接留运行时装配批。

## 1. 判定核心（纯内存，无 IO）

- `plan(trigger)`：`BackfillTrigger`（frozen：trigger_type/target/start_date/
  end_date）非法（未知触发类型、start>end、空 target）→ ValueError 族
  Fail-Closed；按 `shard_days` 切日期分片（可选 `trading_days_provider`
  注入交易日历过滤，缺省按自然日）。
- `run(trigger)`：逐分片经注入 `executor(shard)` 执行（执行体=因子重算/
  数据重拉，运行时装配）；executor 异常 → 该分片 failed 不中断其余。
- 抽样验证：完成分片中按 `sample_ratio`（默认 0.10，最少 1 片）经注入
  `rng` 确定性抽样，`sample_validator(shard, result)` 校验（缺省=rows_written>0）；
  任一样本不过 → sample_passed=False。
- 血缘+重训：全分片成功且样本通过 → `lineage_sink(record)` 更新血缘并
  `retrain_sink(trigger)` 触发 auto-retrain；否则两者均不触发（fail-closed
  不污染血缘）。sink 异常不阻断报告产出（留痕 sink_errors）。

## 2. 接口

```python
@dataclass(frozen=True) BackfillTrigger: trigger_type/target/start_date/end_date
@dataclass(frozen=True) BackfillShard: shard_id/start_date/end_date
@dataclass(frozen=True) ShardResult: shard_id/rows_written/success/error
@dataclass(frozen=True) BackfillPlan: trigger/shards/sample_ratio/max_workers
@dataclass(frozen=True) BackfillReport: trigger/total_shards/succeeded/failed/sampled/sample_passed/lineage_updated/retrain_triggered/sink_errors
@dataclass(frozen=True) AutoBackfillConfig: shard_days=7/sample_ratio=0.10/max_workers=4
class AutoBackfiller(config=None, executor=None, trading_days_provider=None, sample_validator=None, lineage_sink=None, retrain_sink=None, rng=None):
    plan(trigger) / run(trigger)
```

## 3. 不变量

- 判定核心纯内存无 IO；executor/sink 全注入式（单测不触库不触网）。
- 抽样确定性：同种子 rng 同输入必同样本集。
- 血缘与重训只在全成功+样本通过时触发；部分失败留痕不触发。
- 多进程并行（max_workers）为计划声明位，真实并行执行留运行时装配批。

## 4. 依赖

- MOD-L00-004 backfill_checker（设计边：缺口回填语义对齐，不 import）
- MOD-L00-004 scheduler（设计边：触发事件调度装配位）

## 5. MVP 边界

- 运行时接线（executor 接因子重算/数据重拉、lineage_sink 接血缘真源、
  retrain_sink 接 auto-retrain、多进程池装配）留运行时装配批；本模块交付
  触发校验 + 分片规划 + 抽样验证 + 血缘/重训触发契约。
