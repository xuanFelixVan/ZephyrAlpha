---
ttl: task_bound
doc_type: mined_segment
parent_map: config/trading_day_cycle_map.yaml
segment: fig13-D (夜窗段)
node_id: D13-39
miner_lane: mine_fullchain_20261015/daily_ops_pm
created: 2026-10-15
---

# SD13-39 一致预期管线双向验证

## 1. 定义

交易日 00:30（跨午夜移窗后；APScheduler 特殊槽 consensus_crosscheck，单实例）：一致预期管线
双向验证——自建聚合 vs 同花顺快照每日对答案（独立真源互查，非数据下载层），四查=秩相关/新鲜度/
结构断言/PIT 零修正率，产物落交叉验证日志表（c1_market.cross_validation_log）。
源污染事件（2026-09-14）治本配套（设计档案=
docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §9）。
图内决策问题："00:30 双向对答案了吗？不一致时谁被通知？总闸开着吗？"——总闸实存扫=不存在
（开着）；已知留裁：双向验证落日志表即止，不一致不外发分级告警（freshness_severity 一档实测）。

## 2. 六向台账

### 2.1 输入面
- 自建聚合侧+外部快照侧（两侧均已落库为前置，no_ready_gate_reason 承载）。
- 入边：D13-38→D13-39（夜窗链）；依赖序：19:00 同花顺快照+20:30 研报增量+consensus_daily_build
  全部完成后跑（schedule.yaml:109——研报腿已移 20:00，序注记同步漂移）。

### 2.2 输出面
- 产物：c1_market.cross_validation_log（落表即止，无第二消费者——failure_visibility 在册）。
- consumers=count:22（doc=18 为主：capability_canonical_file_registry.yaml:13489、
  data_asset_registry.yaml:10837、module_translation_registry.yaml:53815、
  ruling_registry.yaml:3015；code=1）。
- downstream_action=detect_only。

### 2.3 SSOT 真源
- config/trading_day_cycle_map.yaml#D13-39（wired/partial/🔨）。
- 设计档案：docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §9
  （实存，本批核验）。
- 槽契约：src/zephyr/data/config/schedule.yaml:106-117（cron "30 0 * * 1-5"，2026-10-02 后移
  1h 跨午夜，窗峰值 13.5GB>10GB→9.5GB）；资源册 dow=2-6 与 schedule.yaml=1-5 的 dow 分歧
  另在案待排班班（图 cadence 注记原文）。

### 2.4 代码模块
- module_id=MOD-L00-004；module_ref=src/zephyr/data/consensus_crosscheck.py:62（本批实读：
  :62 命中 _DISABLED_FLAG 总闸旗面定义、:14 命中停用惯例注释——精确锚）。
- 总闸旗面：data/runtime/consensus_crosscheck.disabled（实存扫=不存在，机生层 service_flags）。

### 2.5 门禁约束
- 服务总闸惯例（disabled 旗存在=停用，每次触发实查即时生效）。
- freshness_severity_zh（一档实测）："双向验证落日志表即止，不一致不外发分级告警"。
- gap_refs：benchmark:A2 两级未接线、C4 分级归告警系统还是图侧声明（留裁）。
- casebooks=MEM-F13#移窗与口径。

### 2.6 自动化触发
- 机制=A_apscheduler 特殊槽；slot=consensus_crosscheck cron "30 0 * * 1-5" max_instances=1；
  machine_facts：effective_task_count=0+special_branch_exists=true、calendar_guarded=false。
- trigger_facts：task_runs_30d=0（特殊槽无独立计数面）；节拍证据=交叉验证日志表落表面。

## 3. 自审闸三态（逐向）

| 向 | 态 | 判据 |
|---|---|---|
| 输入面 | pass | 双侧源前置+依赖序在册（序注记随研报移窗漂移，warn 级以下） |
| 输出面 | warn | cross_validation_log 落表即止、无第二消费者；不一致无分级外发 |
| SSOT 真源 | pass | 设计档案 §9+槽契约+图节点三层齐；dow 分歧已显式在案待裁 |
| 代码模块 | pass | consensus_crosscheck.py 双锚精确命中（:14/:62） |
| 门禁约束 | pass | 总闸惯例在码+在册；detect_only 边界如实登记 |
| 自动化触发 | warn | 特殊槽无计数面；节拍靠日志表复核 |

## 4. 缺口与建议

- 本段 4 gap+11 未接线归属：不在主清单（wired）；A2 两级未接线（不一致不外发）是其门禁向实质缺口。
- 建议：cross_validation_log 的 fail 行接 Alerter 低级通道（哪怕只日报聚合）——"对答案"的产出
  若无人被通知，双向验证的治理价值只剩事后审计。
