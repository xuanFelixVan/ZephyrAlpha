---
ttl: task_bound
completes_when: BM-RC-12 环节在 depgraph 有 production 锚点且危机快照有 src 侧消费者
---

# 施工包 · BRK-072 极端事件与黑天鹅（BM-RC-12）

> 风控 50 环节中唯一无锚点者（`battle_map_steps` LEFT JOIN `battle_map_anchors` 实测
> `NO-ANCHOR ['BM-RC-12','极端事件与黑天鹅','risk_control']`）。本车道做了**消费端的一半**，
> 另一半是新建类大件，故出包。

## 1. 本车道已接（勿重做）

- **危机快照的 src 侧首个消费者已存在**：
  `src/zephyr/governance/resilience_governance/emergency_track_guardian.py`
  （`crisis_snapshot_age_days()` + evaluate 的 `crisis_snapshot_stale/absent` breach），
  口径真源 `config/emergency_track.yaml` §crisis_snapshot
  （`dir: data/backtest_artifacts/drills`、`report_file: casualty_report.json`、`max_age_days: 60`）。
  它读的是 `scripts/backtest/crisis_drill_monthly.py` 的产物（该脚本 **归 z-land/landA 车道**，
  实测其落盘口径：脚本头 `# [INVARIANTS]` + `:51` 注记"演练产物只落
  `data/backtest_artifacts/drills/<run_id>/{casualty_report.json,casualty_report.md}`"，
  `DRILL_DIR: Final` 在 `:83`，落盘在 `:603-609`，`.last_run` 指针在 `:641-643`）。
- **诚实边界**：快照在本车道判定里是**加重证据**（逾期只报 breach），**不是**熔断必要条件——
  避免"演练还没跑"变成"系统判定黑天鹅"。若 Owner 要它参与必要条件，见 §3 判据须先补。

## 2. 还缺哪三件

1. **锚点登记**（机械件，最先做）：BM-RC-12 现在 0 锚点。登记入口=
   `scripts/governance/apply_depgraph.py`（RULE-SSOT：架构数据直写 DB，`battle_map_anchors` 实测 588 行）；
   锚定目标 = `zephyr.governance.resilience_governance.emergency_track_guardian`（消费端已实存）
   + 后续压力测试件。注意 `battle_map_domain_policy.yaml:396` 已把 `BM-RC-12` 列进
   `risk_control.allowed` 域白名单，且 `:410-411` 有 `BM-RC-12-B/C`（parent=BM-RC-12 孤儿，
   跨市场传导 / 流动性危机模拟）——**B/C 一并处理**，否则母环节有锚点子环节仍挂 NO-ANCHOR，
   `dg_bm.py` 复测不干净。`candidate_module_registry.yaml:3470-3484` 已有 BM-RC-12 候选条目
   （承载 acquisition 决策），先读它再决定是否新建模块。
2. **压力测试体系**（真新建）：现有可复用件
   `src/zephyr/risk/core/liquidity_crisis_scenarios.py`（candidate_module_registry 记
   `promoted_to: ...（MOD-RK-047，22 测）`）、`config/crisis_gate.yaml`（θ=0.5 warning 档，
   读取方 `src/zephyr/pf_alloc/crisis_gate.py`，**归 z-land 禁改**）、
   `src/zephyr/risk/core/var_intraday_recalc.py` / `var_backtester.py`（本批他道在改）。
   缺的是"把 scenario → 组合冲击 → 生存线判定"串成日频/周频链，并让 `crisis_drill_monthly`
   的 casualty_report 成为其输入之一（当前方向相反：演练是产出方）。
3. **哨兵行**：黑天鹅侧现只有"演练逾期"一条 breach。需补
   `data_supply_sentinel.yaml` 或 `alert_rules.yaml` 的 `kpi.crisis_snapshot.status` 型规则
   （形态参照 ALERT-KPI-001/002 的 `kpi.survival_line.status` == 状态型规则，
   由 `ops_alert_feed.tick_survival` 生产；本仓**状态型规则只认 `==`/`!=`**，
   见 `ops_alert_feed.py:_check_status` 的"不认识的条件下绝不触发"注释）。

## 3. 验收判据

- `python .runtime/tmp/ff-mine0/dg_bm.py`（元挖矿复现脚本）→ `risk_control` 阶段 NO-ANCHOR
  由 1 件变 0 件（含 B/C 则 3→0）。
- 注入：把 `data/backtest_artifacts/drills/<run_id>/casualty_report.json` mtime 改到 90 天前 →
  `python -m zephyr.trading.process_reaper --status` 的 `safety_wires.emergency_track.breaches`
  必含 `crisis_snapshot_stale:`；恢复 mtime → breach 消失（防恒真）。
- 反证：删掉 `crisis_snapshot` 配置块（用缺省）仍须能报 absent；把 `max_age_days` 写成 0 必须
  `EmergencyTrackConfigError`（越界硬错，不许静默当"永不逾期"）。

## 4. 风险与回滚

- 演练产物目录在 `data/` 下：测试**禁写生产路径**，一律 `tmp_path` 造 drills 树 +
  `EmergencyTrackGuardian(repo_root=tmp)`（本车道测试已示范）。
- 误把快照当必要条件 → 一次演练失败即拉资金闸（验收规范 §6"crisis 误报代价"）。§1 的
  "加重证据非必要条件"边界不得在无 Owner 裁定下改。
- 回滚=revert 锚点登记批（DB 面走 `apply_depgraph` 的反向），代码侧无耦合。
