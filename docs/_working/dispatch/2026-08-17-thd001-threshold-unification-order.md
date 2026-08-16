---
ttl: task_bound
---

施工会话 AI-THD-001。任务：存量模块码内阈值统读改造（tracker 遗留 #87，55 号 §3.3 既定后续治理项，Owner 2026-08-17 裁定派单，与四路并发文件级零交集实证——你域=下列 9 个存量模块+1 个对账测试，禁碰四路施工面）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-THD-001（分支 ai/AI-THD-001/task-threshold-unification，自 dev 776d4a2eaa 切出）。进入后 `. .\activate_env.ps1`。

背景：
- [alert_threshold_registry.yaml](../../../docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml)（REG-ATH-001，11 类 35 条）已建成且全部 active 条目带 source_code 代码锚点；MON-001 批新建模块（strategy_deviation_monitor.py / strategy_retirement_evaluator.py）已 fail-closed 直读注册表；存量 9 模块仍码内硬编码常量——散落等于不可评审（55 号 §3.3 裁定）。
- 双向一致性已由 tests/governance/test_alert_threshold_consistency.py 机器锁定（32 active 全量对账），统读改造期间该测试是安全网不是阻碍——改造完成后它自然演化（见范围 3）。

范围（两项，逐项真源引用）：
1. **存量 9 模块码内阈值常量 → fail-closed 注册表统读改造**（真源=alert_threshold_registry.yaml 各条目 source_code 锚点 + 加载范式先例 src/zephyr/risk/core/strategy_deviation_monitor.py L90-168 `_load_deviation_thresholds`）：
   - src/zephyr/risk/core/drawdown_tracker.py（THD-DRAWDOWN-001/002/003：DrawdownTrackerConfig warning/critical/emergency 0.05/0.10/0.15）
   - src/zephyr/trading/health_monitor.py（THD-HEALTH-001~004：_MEM_PRESSURE_ELEVATED/HIGH/CRITICAL 70/80/90 + _DISK_PRESSURE_CRITICAL 90）
   - src/zephyr/backtest/core/decision_gate.py（THD-DEVIATION-001/002：DecisionGateConfig backtest_live_deviation_warn 0.30 / retire 0.50）
   - src/zephyr/governance/lifecycle_governance/post_live_verification.py（THD-PLV-001~005：PLV_CHECKS 五项规约字符串阈值）
   - src/zephyr/risk/core/alert_generator.py（THD-ALERT-001：dedup_window timedelta(minutes=5)）
   - src/zephyr/shared/alerts/alert_escalation.py（THD-ALERT-002：auto_escalate_after_seconds=300）
   - src/zephyr/risk/core/daily_auditor.py（THD-AUDIT-001/002/003：AuditConfig pnl_tolerance 0.001 / warn_ratio 0.8 / bias_threshold 0.1）
   - src/zephyr/reporting/risk_report_engine.py（THD-REPORT-001~004：_RISK_THRESHOLDS 0.3/0.6/0.8 + _TREND_THRESHOLD 0.05）
   - src/zephyr/risk/core/operational_risk_monitor.py（THD-OPRISK-001/002/003：DEFAULT_FAILURE_RATE_THRESHOLD 0.05 / DEFAULT_LATENCY_P95_THRESHOLD_MS 500.0 / _SEVERE_MULTIPLIER 2.0）
   - 加载口径（裁定，逐模块遵循）：①默认值改从注册表 fail-closed 加载（缺文件/缺条目/类型畸形→import 期或构造期 raise，对齐 strategy_deviation_monitor 范式；禁止静默回退硬编码）；②字符串规约值（PLV "±1%" 等）保持字符串语义加载，不强行数值化；③THD-DRIFT-004（model_drift_monitor.py 静态登记表）与 GPU（无码内常量）不在本批；④每模块保留"显式传参覆盖注册表默认"的构造注入通道（测试与特殊场景逃生门）；⑤加载函数可提取为共享小工具（如 9 处重复超 3 处则提取到 src/zephyr/shared/ 合适位置，否则各模块内联——三相似行优于早抽象）。
2. **对账测试演化 + 红队实证**：
   - tests/governance/test_alert_threshold_consistency.py 同步演化：统读后"注册表值=代码默认值"断言对象从码内常量改为加载结果；新增红队用例——注册表缺条目/畸形 YAML/类型错误时目标模块 fail-closed 报错（每类至少 1 例，可参数化）。
   - 数值零漂移断言：改造后 9 模块全部默认值与注册表逐条相等（既有 32 条对账断言全保留语义）。
   - 复跑各模块既有单测零回归（重点：drawdown_tracker / health_monitor / decision_gate / daily_auditor 既有套件）。

避让（四路并发施工面，零触碰）：
- AI-GOVA-001：gov_enforcement/rule_bridge/heartbeat_daemon.py、~20 治理脚本、regime/core/regime_detector.py、tests/governance/{data_layer,depgraph,rule_bridge} 及 test_sel_unreachable_5_linkage.py、Task Scheduler XML
- AI-LVL3-001：risk/core/ashare_systemic_risk_detector.py、risk/core/risk_layer_orchestrator.py、ex_core/、37 号 memo
- AI-REDIS-001：shared/state_store.py、tests/shared/、Redis 配置
- AI-DGR-001：governance/lifecycle_governance/ 下新增 rollback_state_machine.py、paper_live_transition.py、53 号 memo、对应新测试
- 例外说明：post_live_verification.py 与 DGR 同目录不同文件（实证零交集），drawdown_tracker.py 是 #87 登记项（RFIX 改的是 drawdown_controller.py，不同文件，勿混淆）

验收：①9 模块默认值全量=注册表逐条相等+红队 fail-closed 用例 2 轮全绿 ②各模块既有单测零回归 ③test_alert_threshold_consistency.py 全绿（32 条断言语义保留） ④tracker #87 行更新留痕（改"已统读"） ⑤Step 1+Step 6（14 节版）双 PASS ⑥全走 GitCommitGateway（[GW:AI-THD-001]）
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。
