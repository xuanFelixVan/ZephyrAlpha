---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# BRK-054 施工包 · schema 校验 strict_mode + 死信队列（数据腐败的结构性根因）

> 优先级：**本簇最高**。车道 `st-ff-failopen-20260918` 只出包**不翻 flag**
> （`config/flags.yaml` 翻转 = Owner 门位，宪法 §5）。

## 1. 现状（精确位置）

`config/flags.yaml` §`flags.schema_validation`：
`{"enabled": true, "description": "Schema校验 (YAML 加载可用，runtime drift 检测未实现)", "strict_mode": false, "dlq_enabled": false}`
—— `enabled=true` 而两个真正决定行为的开关都是 `false`，description 自认"runtime drift 检测未实现"。
即"flag 在册 → 看起来有校验，实际坏数据直接入库"。

## 2. 缺哪几件实现（缺一翻 flag 即假通道）

| # | 缺件 | 落点 | 判据 |
|---|---|---|---|
| I-1 | 写入前 schema 断言（列名/类型/可空/枚举域） | 唯一写入咽喉 `zephyr.data.ch_writer.write_tsv_outcome` 前置 hook；禁各 provider 自查 | `WriteOutcome` 新增 `schema_violations: int`，>0 整批不进 CH |
| I-2 | 死信队列 DLQ | 经 `DatabaseService` 建 `c1_governance.dlq_schema_violation`（`DateTime64(3)`+显式时区，RULE-SCHEMA-TZ）+ CH 不可达时本地兜底 `.runtime/dlq/<batch>.jsonl` | 违规批次必须**同时**在 DLQ 可回读（读盘逐位对比），不得只 log |
| I-3 | runtime drift 检测（实际表结构 vs 声明 schema） | **事件触发** reconciler（DDL 应用事件 / `system.columns` 变更事件；宪法 §9.3 禁 cron/Timer） | drift=0；有 drift 即产 breach 并进与 I-2 同一条审计链 |
| I-4 | 失败会响闭环（六向⑥） | 复用本车道新增 `_deliver_alert_with_latch` 口径 | DLQ 非空 → `Alerter` 返回值被检查；未落盘不得置"已告警" |

## 3. 为何它是 BRK-034/035 的根因（同一因果链）

- BRK-034 `index_valuation_daily` 同键双行 = 写入无键约束/schema 级校验；
- BRK-035 `northbound_hold_snapshot` 243 组假 `ts_code` 被映射成合法码 = 枚举域/格式校验缺失；
- 两者能落库的**结构条件**正是 `strict_mode=false` + `dlq_enabled=false`：
  没有任何一格能把不合 schema 的行挡下来并让它响。
- **施工顺序硬约束：I-2（DLQ）必须先于 I-1（strict）**。没有死信兜底就打开 strict，
  等于把坏数据从"静默入库"换成"静默丢弃"——假象换了方向，没修好。

## 4. 验收判据

1. 注入 1 行非法 ts_code → `strict_mode=true` 下该批不进 CH、DLQ 行数 +1、`Alerter` 落盘 1 件；
2. 断 DLQ 写盘（`tmp_path` 造真 IO 故障）→ 必须 fail-closed 拒批，不得降级放行；
3. `generate_fail_open_register.py --check` 无漂移；
4. 同批重放两次 DLQ 只 1 条（与 z-land 幂等键语义对齐）；
5. 回归：`tests/zephyr/data/` 逐目录跑；**禁把因加严转红的测试改成宽容**（有则写裁定书交总包）。

## 5. 风险与回滚 / 翻 flag 前置

- 风险：strict 首开把历史"能入库的脏行"全推 DLQ → 观测面短暂爆量。
  缓解：I-1 先以 `shadow` 模式跑（只记不挡）满 3 个交易日，比对 DLQ 量级再切挡。
- 回滚：`strict_mode=false` 单点回退（DLQ 与 drift 代码保留不删，避免二次建设）。
- 前置：I-1..I-4 全有实现 + §4 五条实测证据 + shadow 期量级经 Owner 确认。
  **`flags.yaml` 任何一位翻转均由 Owner 执行。**
