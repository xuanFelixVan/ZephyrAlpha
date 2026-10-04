---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.gov_drift（46 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.gov_drift（46 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=1，wired=35，wired_by_header=4，wired_dynamic=6；初判汇总：dispute=1，mount=45

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/gov_drift/detector_core/__init__.py` | MOD-INF-023 drift_detector core module. | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/gov_drift/absence_manager.py` | Owner Absence Manager — Owner缺席模式 §6.32。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/ai_construction_detectors.py` | [BLUEPRINT] MOD-INF-023 \| docs/03_modules/_domain_governance/drift_detector/blueprint.md \| § | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/ai_context_injector.py` | AI Context Injector — 施工前预检D-023-16 · §6.8。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/alert_router.py` | Alert Router — alert_router.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/artifact_scanner.py` | ArtifactScanner — SSRF / Path Traversal / Credential / Token 防御扫描器 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/autonomy_regressor.py` | Autonomy Regressor — v0.10.0 渐进自治可逆性管理器: confidence<阈值->自动regress自治级别。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/backcompat_checker.py` | Backward Compatibility Checker — 向后兼容策略漂移检测 D-023-31 · §6.23。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/baseline_manager.py` | Baseline Manager — baseline_manager.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/bootstrapping_calibrator.py` | （无文档头，按文件名语义：bootstrapping_calibrator） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/canary_controller.py` | Detector Canary Controller — 检测器金丝雀部署 §6.11。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/cascade_detector.py` | Cascade Failure Detector — 级联故障检测 D-023-22 · §6.15。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/config_consistency.py` | Config Consistency Checker — 配置多源一致性 D-023-29 · §6.21。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/contract_drift_detector.py` | contract_drift_detector — 契约漂移检测器。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/correlation_engine.py` | Correlation Engine — correlation_engine.py | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/credibility_engine.py` | Credibility Engine — credibility_engine.py | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/cross_module_score.py` | Cross Module Score — cross_module_score.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/dashboard.py` | Coverage Dashboard — dashboard.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/detector_core/benchmark_integrity.py` | （无文档头，按文件名语义：benchmark_integrity） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/detector_core/ml_engineering.py` | （无文档头，按文件名语义：ml_engineering） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/detector_core/performance_baseline.py` | （无文档头，按文件名语义：performance_baseline） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/detector_core/regime_detector.py` | （无文档头，按文件名语义：regime_detector） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/detector_dispatcher.py` | Detector Dispatcher — detector_dispatcher.py | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/drift_models.py` | Drift Detector 数据模型 — drift_models.py | 2026-09-16（18天） | in=18/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/drift_training.py` | Drift Detector AI 训练闭环 + 跨语言检测 — drift_training.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/events.py` | G-CT-005 — ManagedDriftEvent Pydantic V2 BaseModel 漂移事件定义. | 2026-09-16（18天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/file_attr_checker.py` | File Attribute Integrity — 文件底层属性完整性 §6.30。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/gate_persistence.py` | Gate Persistence — gate_persistence.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/gitignore_auditor.py` | .gitignore Integrity Auditor — gitignore完整性审计 D-023-32 · §6.24。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/handoff_manager.py` | Cross-Session Handoff Manager — 跨Session修复上下文交接 §6.14。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/naming_magic_checker.py` | Naming Magic Checker — 命名魔数与隐式约定检测 §6.27。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/python_compat.py` | Python Compatibility Checker — Python版本兼容性漂移 D-023-30 · §6.22。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/reward_hacking_rebound_detector.py` | Reward Hacking Rebound Detector — v0.14.0 §2.37-D. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/roi_engine.py` | ROI Engine — roi_engine.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/rollback_bridge.py` | G-CT-006 契约：Drift -> Rollback 漂移触发回滚. | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/runbook_generator.py` | Drift Runbook Generator — 漂移演练手册自动生成。 | 2026-09-05（29天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/self_check.py` | Self-Drift Check — self_check.py | 2026-09-16（18天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/self_test_verifier.py` | Self Test Verifier — self_test_verifier.py | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/silence_detector.py` | Silence Detector — v0.8.0 静默窗口检测器: agent无响应超时+heartbeat缺失检测。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/spiral_ews.py` | （无文档头，按文件名语义：spiral_ews） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/state_machine.py` | [BLUEPRINT] MOD-INF-023 \| docs/03_modules/_domain_governance/drift_detector/blueprint.md \| § | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/suppression_learner.py` | Suppression Learner — suppression_learner.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/symlink_checker.py` | Symlink Integrity Checker — 软链接完整性检测 §6.29。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/test_fixture_checker.py` | Test Fixture Checker — 测试夹具漂移检测 D-023-28 · §6.20。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/trend_analyzer.py` | Trend Analyzer — trend_analyzer.py | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_drift/vigil_runtime.py` | Vigil Runtime — v0.6.0 VIGIL维护运行时: 运维token预算+手动override窗口。 | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
