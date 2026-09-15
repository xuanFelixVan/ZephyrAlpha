---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓 批6 报告：risk 域（st-btfix-p15-20260915）

## 概要

| 项 | 值 |
|----|----|
| 域 | risk → `docs/03_modules/_domain_risk/algo_flow/` |
| 出仓文件 | 76 src（内联块 → 单行 external 锚点），3835 行机器块外迁 |
| yaml 产物 | 76 本批新建 |
| 测试 | tests/risk = **1813 passed + 1 skipped**（39.2s，隔离 cache_dir） |
| 提交 | `a220de4662`（155 文件，零吸收已核实） |
| 幂等 | 复扫 0 待出仓（59 skipped + 19 already） |

## 配套登记

- **创建令牌**：capability_canonical_file_registry.yaml +111 条（capability `btfix_p1p2`，created_by st-btfix-p15-20260915；76 本批 + 35 该域先前未登记已跟踪 yaml 补登）。
- **TDM 注解**：3 节点（较批5 零注解恢复常态）——
  1. TDM-P-P1-04（MOD-RK-09 ashare_stop_loss_engine）：新插 note_confirmed + algo_note 出仓注记
  2. TDM-X-R1-01（MOD-RK-049 drawdown_state_machine）：既有 note_confirmed 2026-09-11 → 2026-09-15 + 出仓注记
  3. TDM-X-R1-02（MOD-RK-050 drawdown_liquidation_guard）：同上
- **CloneGuard**：9 对既有克隆暴露（3 对为同文件内样板同构：alert_generator.send ×2、drawdown_session_persistence 读/写载荷 ×3），均核实 HEAD 既有，echo-guard.yml acknowledged（19 条累计）。

## 过程发现

1. **全局提交锁竞态常态化**：`--wait 900` 后台等待落地（LOCK_TIMEOUT exit=2 按网关指引指数退避而非盲轮询）。本批提交前后共 5 次尝试，2 次锁忙、1 次 CloneGuard 暴露、最终 900s 等待窗口内一次成功——多会话并发下大批次提交应默认 `--wait`。
2. **出仓后立即 claim 有效**：批5 的 watchdog（task:SRC-081）竞态本批未复现——出仓完成后秒级 claim 76/76 全成。
3. **TDM 既有 note_confirmed 节点**：本次改动 algo_note 后将原日期（2026-09-11）更新为改动确认日（2026-09-15），语义=注记确认日随最新算法注记变化。

## 战役进度

- 已出仓累计：批1-2（72）+ 批3 regime（42）+ 批4 ex_core（59）+ 批5 ml_train（43）+ 批6 risk（76）= **292 文件（8.8% / 3302）**
- 剩余大域：feedback_loop(340) / infrastructure(336) / governance(296) / shared(243) / gov_enforcement(188) / security(188) 需独立立项；中小域：autonomy_core(138) / signal_ashare(128) / data(116) / trading(92) / factor(83) / orchestrator(75) 等可继续逐批。
- 遗留（非本批义务）：pytest_min.ini markers bug；TDM note 归因窗口重设计；GATE-PANORAMA-ALIGNMENT UnicodeDecodeError 检测器失效（reconcile 日志 critical_warn，见提交前告警）。
