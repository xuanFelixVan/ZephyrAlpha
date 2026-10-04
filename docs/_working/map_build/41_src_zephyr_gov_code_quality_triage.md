---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.gov_code_quality（61 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.gov_code_quality（61 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=1，wired=6，wired_by_header=51，wired_dynamic=3；初判汇总：dispute=1，mount=60

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/gov_code_quality/__init__.py` | gov_code_quality domain package — code quality governance (D_GOV_CODE_QUALITY). | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/gov_code_quality/code_dedup/__init__.py` | code-dedup-engine 子包 — 重复代码检测与治理引擎. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/annotations.py` | 共享函数注解引擎 — @shared / @known_dup / @intentional 三注解. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/ast_comparator.py` | Stage 2: AST 级精确比对器. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/atomic_fixer.py` | 原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT -> APPLY -> RECOVER. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/behavioral_sampler.py` | 行为采样验证器 — Stage 0.25 低成本快速验证. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/behavioral_trust_checker.py` | 行为信任检查器 — 行为漂移DIVERGED检测. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/cache_manager.py` | Stage 0: 函数缓存管理器 — 增量扫描的加速核心. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/canary_manager.py` | 金丝雀工厂——生成已知oracle 文件 用于引擎检出+回归测试. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/canary_register.py` | 金丝雀注册表维护器 — 注册/过期/腐败检测. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/code_analyzer_runner.py` | 检查运行器——按照敏感基线运行三阶段+导出 yaml 报告. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/code_simulator.py` | 代码模拟器——播放录制的克隆演化序列，stress-test AST/baseline归一化. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/config.py` | 配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/contract_consistency_checker.py` | API契约一致性检查器 — 存在性·行为·契约三维. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/cross_boundary_detector.py` | 跨边界克隆感知——四大边界差异化检测+独立策略+跨边界保守auto_fix规则. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/dead_module_detector.py` | 死共享模块检测器 — shared/子模块无人使用 -> DEAD. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/debt_projector.py` | 去重债务预测器 — weeks_to_payoff + intake_rate vs fix_rate 蒙特卡洛模拟. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/decision_auditor.py` | 决策审计链 — DecisionFingerprint 不可变追加日志. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/degradation.py` | 降级运行管理器 — 各 Stage 独立 try/except + degradation_level + exit code. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/doom_loop_guard.py` | Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/exit_codes.py` | 退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/extraction_safety.py` | 安全提取适配性评估器 — Suitability Score 0-100 + 不安全提取模式检测. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/false_negative_auditor.py` | 三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Sampling. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/fifteen_dimension_auditor.py` | 15维超综合审计首页 — 逐项证明"做过且做对". | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/file_creator.py` | 文件创建清单执行器 — 验证所有源/测试/数据文件存在性. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/function_discovery.py` | 共享函数主动发现 — 签名+语义双通道从被动到主动. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/grandfather_manager.py` | Grandfather 三定律 — 古老重复管理. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/integration_hub.py` | 集成协调器 — 24集成+19更新+16GitHub整合. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/integrations.py` | 集成管理——预提交钩子+CI-only 扫描+超时边界. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/micro_clone_detector.py` | 微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/mock_duplicate_generator.py` | 可控克隆生产器——零假阳性可期待引擎分子离散 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/monoculture_guard.py` | Monoculture 免疫 — BRS 0-100 + 去重悖论检测. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/observation_window_guard.py` | 提取后稳定观察期守护 — 对标SDP 14天观察. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/path_index_validator.py` | 路径索引验证——验证 config 数据集相对路径表与实际文件系统同步. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/phase_executor.py` | 6Phase施工执行器 — Phase 0~5 执行状态追踪. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/policy_tree_validator.py` | 策略树自动一致性校验器 — 虚线箭头影响分析. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/pre_apply_integrity_gate.py` | Pre-Apply 完整性门 — SHA256重新验证. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/prioritizer.py` | 修复优先级排序器 — 置信度×Impact×适配性 三因子排序. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/recovery_manifest_writer.py` | Recovery Manifest Writer — R2纯文本base64 Manifest. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/report.py` | 报告生成器 — YAML/JSON 输出 + 退出码判定 + Health Score 聚合. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/risk_mitigator.py` | R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + mitigation_tracker.yaml. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/self_scanner.py` | 引擎自扫描器 — Dogfooding 检测引擎自身源码重复. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/sensitivity_sweeper.py` | 敏感性扫荡——threshold扫描->固化成new baseline（零假阳性+触达率保险）. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/shadow_trust_validator.py` | 影子信任验证器 — ImportError 防护回路. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/shadow_verifier.py` | 影子清单验证器 — size sanity check + semantic验证 + 覆盖度报告. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/shared_evolver.py` | 共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/signature_matcher.py` | Stage 0.5: 签名指纹 SHA256[:12] O(1) 精确匹配. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/simplicity_auditor.py` | 引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax 报告. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/ssot_registrar.py` | SSoT注册器 — 提取函数自动注册到 shared API清单. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/stale_shared_detector.py` | 过时共享函数检测器 — 无caller × 30天 -> STALE标记. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/success_validator.py` | 成功验证——判断一次去重操作是否真正消灭了克隆. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/symbol_index.py` | 符号索引 — 全局函数/类/import映射表. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/thematic_clusterer.py` | 主题聚类器 — 噪声信号比·告警疲劳缓解. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/__init__.py` | tracker 族子包 — 风险/盲点/热点跟踪器集合. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/blind_spot_tracker.py` | 盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖. | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/consequence_tracker.py` | 后果追踪——记录每次修复操作对依赖方的影响. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/hotspot_tracker.py` | 热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新项目预热清单. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/import_surface_tracker.py` | Import表面积负债追踪 — SBS 0-100 + shared burden score. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/question_tracker.py` | 问题追踪——扫描中发现需要人工处理的问题. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/trackers/risk_mitigation_tracker.py` | 风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/gov_code_quality/code_dedup/verifier.py` | 修复验证器 — import + 类型 + 行为采样验证. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
