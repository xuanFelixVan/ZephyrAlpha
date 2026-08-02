---
doc_type: architecture_view
title: D_GOV_CODE_QUALITY 代码质量治理架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 19_d_gov_code_quality / 代码质量治理域 / Code Quality Governance

> **功能简介 / Overview**: 代码质量治理，负责代码去重引擎、函数重复检测、AST语义分析和提交门禁引擎

> **文档作用 / Purpose**: 展示 代码质量治理（D_GOV_CODE_QUALITY）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/19_d_gov_code_quality.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 19 | Number | 19 |
| 域ID | D_GOV_CODE_QUALITY | Domain ID | D_GOV_CODE_QUALITY |
| 域名称 | 代码质量治理 | Domain Name | Code Quality Governance |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 171 | Module Count | 171 |
| 域内依赖 | 44 | Internal Dependencies | 44 |
| 跨域入边 | 17 | Cross-domain Incoming | 17 |
| 跨域出边 | 125 | Cross-domain Outgoing | 125 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 171 | Production Modules | 171 |
| 容量 | 171/150 (超容) | Capacity | 171/150 (超容) |
| 描述 | 代码去重引擎(code_dedup) | Description | 代码去重引擎(code_dedup) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 171 个模块（生产态 171 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["d3_metadata/check_pure_assertion<br/>check_pure_assertion.py — GOV-DOC-016<br/>纯陈述原则检测真源（SSoT）。<br/>文件: d3_metadata/check_pure_assertion.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_module_id_consistency_py["d7_code/check_module_id_consistency<br/>check_module_id_consistency.py — module_id<br/>全仓一致性扫描（--scan-existing ...<br/>文件: d7_code/check_module_id_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_yaml_anchor_consistency_py["d7_code/check_yaml_anchor_consistency<br/>check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描.<br/>文件: d7_code/check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_init_py["zephyr/gov_code_quality 包入口<br/>gov_code_quality domain package — code quality<br/>governance (D_GOV_CODE_QUALITY).<br/>文件: gov_code_quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_init_py["gov_code_quality/code_dedup 包入口<br/>code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: code_dedup/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["code_dedup/ast_comparator<br/>Stage 2: AST 级精确比对器.<br/>文件: code_dedup/ast_comparator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["code_dedup/atomic_fixer<br/>原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT<br/>-> APPLY -> RECOVER.<br/>文件: code_dedup/atomic_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["code_dedup/behavioral_sampler<br/>行为采样验证器 — Stage 0.25 低成本快速验证.<br/>文件: code_dedup/behavioral_sampler.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["code_dedup/behavioral_trust_checker<br/>行为信任检查器 — 行为漂移DIVERGED检测.<br/>文件: code_dedup/behavioral_trust_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["code_dedup/cache_manager<br/>Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>文件: code_dedup/cache_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["code_dedup/canary_manager<br/>金丝雀工厂——生成已知oracle 文件<br/>用于引擎检出+回归测试.<br/>文件: code_dedup/canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["code_dedup/canary_register<br/>金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>文件: code_dedup/canary_register.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["code_dedup/cli<br/>code-dedup-engine<br/>CLI——子命令映射+退出码+扫描入口.<br/>文件: code_dedup/cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["code_dedup/code_analyzer_runner<br/>检查运行器——按照敏感基线运行三阶段+导出 yaml<br/>报告.<br/>文件: code_dedup/code_analyzer_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["code_dedup/code_simulator<br/>代码模拟器——播放录制的克隆演化序列，stress-test<br/>AST/baseline归一化.<br/>文件: code_dedup/code_simulator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["code_dedup/contract_consistency_checker<br/>API契约一致性检查器 — 存在性·行为·契约三维.<br/>文件: code_dedup/contract_consistency_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["code_dedup/cross_boundary_detector<br/>跨边界克隆感知——四大边界差异化检测+独立策略+跨边<br/>界保守auto_fix规则.<br/>文件: code_dedup/cross_boundary_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["code_dedup/dead_module_detector<br/>死共享模块检测器 — shared/子模块无人使用 -><br/>DEAD.<br/>文件: code_dedup/dead_module_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["code_dedup/debt_projector<br/>去重债务预测器 — weeks_to_payoff + intake_rate<br/>vs fix_rate 蒙特卡洛模拟.<br/>文件: code_dedup/debt_projector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["code_dedup/decision_auditor<br/>决策审计链 — DecisionFingerprint 不可变追加日志.<br/>文件: code_dedup/decision_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["code_dedup/degradation<br/>降级运行管理器 — 各 Stage 独立 try/except +<br/>degradation_level + exit code.<br/>文件: code_dedup/degradation.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["code_dedup/diff_detector<br/>Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>文件: code_dedup/diff_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["code_dedup/doom_loop_guard<br/>Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>文件: code_dedup/doom_loop_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["code_dedup/extraction_safety<br/>安全提取适配性评估器 — Suitability Score 0-100<br/>+ 不安全提取模式检测.<br/>文件: code_dedup/extraction_safety.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["code_dedup/false_negative_auditor<br/>三层漏报盲审器 — L1 Sweep + L2 Canary + L3<br/>Sampling.<br/>文件: code_dedup/false_negative_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["code_dedup/fifteen_dimension_auditor<br/>15维超综合审计首页 — 逐项证明'做过且做对'.<br/>文件: code_dedup/fifteen_dimension_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["code_dedup/file_creator<br/>文件创建清单执行器 — 验证所有源/测试<br/>/数据文件存在性.<br/>文件: code_dedup/file_creator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["code_dedup/function_discovery<br/>共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>文件: code_dedup/function_discovery.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["code_dedup/grandfather_manager<br/>Grandfather 三定律 — 古老重复管理.<br/>文件: code_dedup/grandfather_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["code_dedup/health_monitor<br/>健康仪表盘 — Dedup Health Score 0-100 + 趋势 +<br/>Session Log 写入.<br/>文件: code_dedup/health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["code_dedup/integration_hub<br/>集成协调器 — 24集成+19更新+16GitHub整合.<br/>文件: code_dedup/integration_hub.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["code_dedup/integrations<br/>集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>文件: code_dedup/integrations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["code_dedup/micro_clone_detector<br/>微型克隆检测器 — n-gram频率计数,<br/>1-2行高频模式聚合.<br/>文件: code_dedup/micro_clone_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["code_dedup/mock_duplicate_generator<br/>可控克隆生产器——零假阳性可期待引擎分子离散<br/>文件: code_dedup/mock_duplicate_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["code_dedup/monoculture_guard<br/>Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>文件: code_dedup/monoculture_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["code_dedup/observation_window_guard<br/>提取后稳定观察期守护 — 对标SDP 14天观察.<br/>文件: code_dedup/observation_window_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["code_dedup/path_index_validator<br/>路径索引验证——验证 config<br/>数据集相对路径表与实际文件系统同步.<br/>文件: code_dedup/path_index_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["code_dedup/phase_executor<br/>6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>文件: code_dedup/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["code_dedup/policy_tree_validator<br/>策略树自动一致性校验器 — 虚线箭头影响分析.<br/>文件: code_dedup/policy_tree_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["code_dedup/pre_apply_integrity_gate<br/>Pre-Apply 完整性门 — SHA256重新验证.<br/>文件: code_dedup/pre_apply_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["code_dedup/prioritizer<br/>修复优先级排序器 — 置信度×Impact×适配性<br/>三因子排序.<br/>文件: code_dedup/prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["code_dedup/recovery_manifest_writer<br/>Recovery Manifest Writer — R2纯文本base64<br/>Manifest.<br/>文件: code_dedup/recovery_manifest_writer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["code_dedup/risk_mitigator<br/>R1-R45全量风险缓解执行器 — 逐条检查缓解措施 +<br/>mitigation_tracker.yaml.<br/>文件: code_dedup/risk_mitigator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["code_dedup/self_scanner<br/>引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>文件: code_dedup/self_scanner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["code_dedup/sensitivity_sweeper<br/>敏感性扫荡——threshold扫描->固化成new baseline<br/>（零假阳性+触达率保险）.<br/>文件: code_dedup/sensitivity_sweeper.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["code_dedup/shadow_trust_validator<br/>影子信任验证器 — ImportError 防护回路.<br/>文件: code_dedup/shadow_trust_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["code_dedup/shadow_verifier<br/>影子清单验证器 — size sanity check +<br/>semantic验证 + 覆盖度报告.<br/>文件: code_dedup/shadow_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["code_dedup/shared_evolver<br/>共享函数自我进化引擎 — 自动升降级 +<br/>行为漂移锁定.<br/>文件: code_dedup/shared_evolver.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["code_dedup/shared_lifecycle_manager<br/>共享函数生命周期管理 —<br/>Active->Deprecated->Grace->Sunset->Retired<br/>五阶段状态机.<br/>文件: code_dedup/shared_lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["code_dedup/signature_matcher<br/>Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配.<br/>文件: code_dedup/signature_matcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["code_dedup/simplicity_auditor<br/>引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax<br/>报告.<br/>文件: code_dedup/simplicity_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["code_dedup/ssot_registrar<br/>SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>文件: code_dedup/ssot_registrar.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["code_dedup/stale_shared_detector<br/>过时共享函数检测器 — 无caller × 30天 -><br/>STALE标记.<br/>文件: code_dedup/stale_shared_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["code_dedup/success_validator<br/>成功验证——判断一次去重操作是否真正消灭了克隆.<br/>文件: code_dedup/success_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["code_dedup/symbol_index<br/>符号索引 — 全局函数/类/import映射表.<br/>文件: code_dedup/symbol_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["code_dedup/thematic_clusterer<br/>主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>文件: code_dedup/thematic_clusterer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["code_dedup/trackers 包入口<br/>tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: trackers/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["trackers/consequence_tracker<br/>后果追踪——记录每次修复操作对依赖方的影响.<br/>文件: trackers/consequence_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["trackers/hotspot_tracker<br/>热点追踪器 — 90天滑动窗口 + 高频变动检测 +<br/>新项目预热清单.<br/>文件: trackers/hotspot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["trackers/import_surface_tracker<br/>Import表面积负债追踪 — SBS 0-100 + shared<br/>burden score.<br/>文件: trackers/import_surface_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["trackers/question_tracker<br/>问题追踪——扫描中发现需要人工处理的问题.<br/>文件: trackers/question_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["trackers/risk_mitigation_tracker<br/>风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍<br/>未fix.<br/>文件: trackers/risk_mitigation_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["code_dedup/verifier<br/>修复验证器 — import + 类型 + 行为采样验证.<br/>文件: code_dedup/verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_init_py["gov_enforcement/commit_gates 包入口<br/>commit_gates — GitCommitGateway pre-commit<br/>门禁实现包。<br/>文件: commit_gates/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["commit_gates/arch_reference_gate<br/>arch_reference_gate.py — #ARCH-NNN /<br/>#ARCH-DOMAIN-NNN 悬空引用自动检测门禁（...<br/>文件: commit_gates/arch_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["commit_gates/asyncio_run_in_context_gate<br/>asyncio_run_in_context_gate.py —<br/>异步上下文误用硬阻断门禁（ASYNCIO-RUN-IN-CO...<br/>文件: commit_gates<br/>/asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["commit_gates/bare_getenv_gate<br/>bare_getenv_gate.py — 裸 os.getenv<br/>读密钥阻断门禁（NO-BARE-GETENV，§5.17.10...<br/>文件: commit_gates/bare_getenv_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["commit_gates/bare_sql_gate<br/>bare_sql_gate.py — 裸SQL字面量阻断门禁<br/>（NO-BARE-SQL，§5.160.2 防复发）<br/>文件: commit_gates/bare_sql_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["commit_gates/bare_subprocess_gate<br/>bare_subprocess_gate.py — 裸 subprocess<br/>调用硬阻断门禁（BARE-SUBPROCESS）<br/>文件: commit_gates/bare_subprocess_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["commit_gates/blueprint_amodule_consistency_gate<br/>blueprint_amodule_consistency_gate.py —<br/>(A_module) 头部 module_id 格式一致性门禁<br/>文件: commit_gates<br/>/blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["commit_gates/blueprint_amodule_cross_check_gate<br/>blueprint_amodule_cross_check_gate.py —<br/>(BLUEPRINT) vs (A_module) 交叉校验门禁<br/>文件: commit_gates<br/>/blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["commit_gates/blueprint_format_gate<br/>blueprint_format_gate.py — (BLUEPRINT) 头部<br/>module_id 格式阻断门禁（BLUEPRIN...<br/>文件: commit_gates/blueprint_format_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["commit_gates/capability_consistency_gate<br/>capability_consistency_gate.py — Provider<br/>路由-meta 一致性门禁（CAP-CONSISTE...<br/>文件: commit_gates<br/>/capability_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["commit_gates/capability_lookup_required_gate<br/>capability_lookup_required_gate.py — Capability<br/>Lookup 强制门禁（CAPABILITY-...<br/>文件: commit_gates<br/>/capability_lookup_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["commit_gates/capability_overlap_gate<br/>capability_overlap_gate.py — 新建 .py 文件<br/>CapabilityLookup 提示门禁（warn-o...<br/>文件: commit_gates/capability_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["commit_gates/ch_batch_size_gate<br/>ch_batch_size_gate.py — CH 批量写入防回退门禁<br/>（CH-BATCH-SIZE，§18.4 防复发）<br/>文件: commit_gates/ch_batch_size_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["commit_gates/ch_final_gate<br/>ch_final_gate.py — ch_writer.query()<br/>直接调用阻断门禁（CH-FINAL-GATE，裁定 #...<br/>文件: commit_gates/ch_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["commit_gates/ch_version_col_gate<br/>ch_version_col_gate.py — CH version<br/>列语义误用阻断门禁（CH-VERSION-COL，裁定...<br/>文件: commit_gates/ch_version_col_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["commit_gates/claim_required_gate<br/>claim_required_gate.py — claim_files<br/>前置检查门禁（CLAIM-REQUIRED，2026-06-3...<br/>文件: commit_gates/claim_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["commit_gates/consumers_accuracy_gate<br/>consumers_accuracy_gate.py — CONSUMERS<br/>字段准确性 warn-only 门禁（CONSUMERS-...<br/>文件: commit_gates/consumers_accuracy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["commit_gates/create_guard<br/>create_guard.py — 新建 .py / 非 rules/ .yaml<br/>文件 creation_token 阻断门禁（C...<br/>文件: commit_gates/create_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["commit_gates/dangling_reference_gate<br/>dangling_reference_gate.py — AGENTS.md §X.Y<br/>悬空引用自动检测门禁（DANGLING-...<br/>文件: commit_gates/dangling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["commit_gates/data_task_completeness_gate<br/>data_task_completeness_gate.py —<br/>数据任务完整性门禁（warn 级，提醒型）<br/>文件: commit_gates<br/>/data_task_completeness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["commit_gates/datetime_now_forbidden_gate<br/>datetime_now_forbidden_gate.py —<br/>时间戳约定硬阻断门禁（DATETIME-NOW-FORBIDDEN）<br/>文件: commit_gates<br/>/datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["commit_gates/depgraph_freshness_gate<br/>depgraph_freshness_gate.py — depgraph<br/>新鲜度门禁（dual-threshold，...<br/>文件: commit_gates/depgraph_freshness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["commit_gates/depgraph_write_path_gate<br/>depgraph_write_path_gate.py — depgraph<br/>写入路径白名单门禁（DEPGRAPH-WRITE-PATH）<br/>文件: commit_gates/depgraph_write_path_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["commit_gates/derivation_annotation_gate<br/>derivation_annotation_gate.py —<br/>派生关系声明真实性校验门禁（DERIVATION-ANNOT...<br/>文件: commit_gates/derivation_annotation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["commit_gates/directory_contract_gate<br/>directory_contract_gate.py — DCR-001~007<br/>等效校验门禁（治本：弥补 --no-verif...<br/>文件: commit_gates/directory_contract_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["commit_gates/doc_ref_broken_gate<br/>doc_ref_broken_gate.py —<br/>文档相对路径断裂引用阻断门禁（DOC-REF-BROKEN）<br/>文件: commit_gates/doc_ref_broken_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["commit_gates/domain_fk_gate<br/>domain_fk_gate.py — (DOMAIN) 头部域注册表 FK<br/>校验门禁（GATE-DOMAIN-FK）<br/>文件: commit_gates/domain_fk_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["commit_gates/domain_name_zh_direct_access_gate<br/>domain_name_zh_direct_access_gate.py —<br/>DOMAIN_NAME_ZH 字典直接访问硬阻断门禁<br/>文件: commit_gates<br/>/domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["commit_gates/empty_handler_gate<br/>empty_handler_gate.py — 空事件 handler<br/>函数阻断门禁（EMPTY-HANDLER）<br/>文件: commit_gates/empty_handler_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["commit_gates/encoding_gate<br/>encoding_gate.py — 编码安全校验门禁（治本：弥补<br/>--no-verify 绕过 pre-commit ...<br/>文件: commit_gates/encoding_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["commit_gates/exempt_zone_frontmatter_gate<br/>exempt_zone_frontmatter_gate.py — 豁免区<br/>frontmatter 门禁（Phase 3 reconcile...<br/>文件: commit_gates<br/>/exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["commit_gates/file_copy_gate<br/>file_copy_gate.py — 新增 .py<br/>文件复制检测阻断门禁（FILE-COPY，2026-07-03<br/>Pha...<br/>文件: commit_gates/file_copy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["commit_gates/file_placement_ttl_gate<br/>file_placement_ttl_gate.py — 文件放置与 TTL<br/>一致性门禁（治本 #ARCH-049：防止...<br/>文件: commit_gates/file_placement_ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["commit_gates/folder_capacity_hard_limit_gate<br/>folder_capacity_hard_limit_gate.py —<br/>文件夹容量硬上限门禁（FOLDER-CAPACITY-H...<br/>文件: commit_gates<br/>/folder_capacity_hard_limit_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["commit_gates/foreign_change_gate<br/>foreign_change_gate.py — 外来变更检测门禁<br/>（FOREIGN-CHANGE-DETECTION，ARCH-05...<br/>文件: commit_gates/foreign_change_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["commit_gates/forged_gw_marker_gate<br/>forged_gw_marker_gate.py — Forged GW Marker<br/>前置检测门禁（FORGED-GW-MARKER，...<br/>文件: commit_gates/forged_gw_marker_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["commit_gates/function_dup_gate<br/>function_dup_gate.py — 重复函数实现阻断门禁<br/>（FUNCTION-DUP）<br/>文件: commit_gates/function_dup_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["commit_gates/gate_repo<br/>gate_repo.py — gates 表持久化仓库（AUDIT-07<br/>P1-5: 从 gate_engine.py 提取）<br/>文件: commit_gates/gate_repo.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["commit_gates/git_call_budget_gate<br/>git_call_budget_gate.py — Git 调用预算<br/>warn-only 门禁（GIT-CALL-BUDGET，§AR...<br/>文件: commit_gates/git_call_budget_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["commit_gates/god_class_gate<br/>god_class_gate.py — God Class 阻断门禁<br/>（NO-GOD-CLASS，§5.150 防复发）<br/>文件: commit_gates/god_class_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["commit_gates/hardcoded_url_gate<br/>hardcoded_url_gate.py — 硬编码 localhost URL<br/>阻断门禁（NO-HARDCODED-URL，§5...<br/>文件: commit_gates/hardcoded_url_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["commit_gates/held_overlap_gate<br/>held_overlap_gate.py — 搭便车防护门禁<br/>（HELD-OVERLAP，2026-06-30 治本）<br/>文件: commit_gates/held_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["commit_gates/high_complexity_gate<br/>high_complexity_gate.py — 高循环复杂度阻断门禁<br/>（NO-HIGH-COMPLEXITY，§5.158 ...<br/>文件: commit_gates/high_complexity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["commit_gates/id_uniqueness_gate<br/>id_uniqueness_gate.py — pre-commit hook ID<br/>唯一性门禁（Phase 3 reconciler->g...<br/>文件: commit_gates/id_uniqueness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["commit_gates/import_direction_gate<br/>import_direction_gate.py — shared<br/>层向上依赖阻断门禁（NO-UPWARD-IMPORT，§5....<br/>文件: commit_gates/import_direction_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["commit_gates/import_integrity_gate<br/>import_integrity_gate.py — IMPORT-INTEGRITY<br/>门禁（悬空 import 硬阻断）<br/>文件: commit_gates/import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["commit_gates/issue_resolved_integrity_gate<br/>issue_resolved_integrity_gate.py —<br/>ISSUE-RESOLVED-INTEGRITY warn-only 门禁<br/>文件: commit_gates<br/>/issue_resolved_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["commit_gates/long_param_list_gate<br/>long_param_list_gate.py — 长参数列表阻断门禁<br/>（NO-LONG-PARAM-LIST，§5.150 防...<br/>文件: commit_gates/long_param_list_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["commit_gates/manual_only_permanent_gate<br/>manual_only_permanent_gate.py — 永久系统脚本<br/>manual 触发无事件订阅阻断门禁（...<br/>文件: commit_gates/manual_only_permanent_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["commit_gates/mcp_version_field_gate<br/>mcp_version_field_gate.py — MCP version<br/>字段缺失硬阻断门禁（MCP-VERSION-FIELD）<br/>文件: commit_gates/mcp_version_field_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["commit_gates/module_id_consistency_gate<br/>module_id_consistency_gate.py — module_id<br/>三声明轨道一致性 + count 派生 + 跨...<br/>文件: commit_gates/module_id_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["commit_gates/msg_exposure_gate<br/>msg_exposure_gate.py —<br/>错误消息暴露敏感信息阻断门禁（MSG-EXPOSURE）<br/>文件: commit_gates/msg_exposure_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["commit_gates/msg_style_gate<br/>msg_style_gate.py — 错误消息标点<br/>/箭头风格阻断门禁（MSG-STYLE）<br/>文件: commit_gates/msg_style_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["commit_gates/mutable_const_without_final_gate<br/>mutable_const_without_final_gate.py —<br/>可变常量缺 Final 标注硬阻断门禁（MUTAB...<br/>文件: commit_gates<br/>/mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["commit_gates/new_file_depgraph_gate<br/>new_file_depgraph_gate.py — 新建 .py 文件<br/>depgraph 未登记硬阻断门禁（NEW-FIL...<br/>文件: commit_gates/new_file_depgraph_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["commit_gates/no_import_side_effect_gate<br/>no_import_side_effect_gate.py —<br/>模块导入零副作用门禁（NO-IMPORT-SIDE-EFFECT...<br/>文件: commit_gates/no_import_side_effect_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["commit_gates/noqa_validation_gate<br/>noqa_validation_gate.py — 自定义 noqa<br/>标记合规性门禁（NOQA-VALIDATION，ARCH-...<br/>文件: commit_gates/noqa_validation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["commit_gates/open_without_with_gate<br/>open_without_with_gate.py — open() 未在 with<br/>内硬阻断门禁（OPEN-WITHOUT-WITH）<br/>文件: commit_gates/open_without_with_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["commit_gates/orphan_module_gate<br/>orphan_module_gate.py — 孤儿模块（无 import<br/>引用）阻断门禁（ORPHAN-MODULE）<br/>文件: commit_gates/orphan_module_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["commit_gates/panorama_alignment_gate<br/>panorama_alignment_gate.py — 三图模块对齐门禁<br/>（四图模块对齐 Step 4，ARCH-056...<br/>文件: commit_gates/panorama_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["commit_gates/precommit_offline_gate<br/>precommit_offline_gate.py — pre-commit<br/>配置离线可运行检测门禁（GATE-PRECOMMI...<br/>文件: commit_gates/precommit_offline_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["commit_gates/pure_assertion_gate<br/>pure_assertion_gate.py — 纯陈述原则阻断门禁<br/>（PURE-ASSERTION，GOV-DOC-016 治本）<br/>文件: commit_gates/pure_assertion_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["commit_gates/pure_shim_gate<br/>pure_shim_gate.py — 纯 re-export shim 阻断门禁<br/>（PURE-SHIM，P6 治本 2026-07-09）<br/>文件: commit_gates/pure_shim_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["commit_gates/r5_digit_suffix_gate<br/>r5_digit_suffix_gate.py — R5<br/>数字后缀目录禁止门禁（治本：弥补 --no-verify<br/>绕...<br/>文件: commit_gates/r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["commit_gates/reconciler_health_gate<br/>reconciler_health_gate.py — reconciler<br/>健康度门禁（#ARCH-DATAQUALITY-V1.7）<br/>文件: commit_gates/reconciler_health_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["commit_gates/relative_path_literal_gate<br/>relative_path_literal_gate.py —<br/>相对路径字面量硬阻断门禁（RELATIVE-PATH-LITE...<br/>文件: commit_gates/relative_path_literal_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["commit_gates/rename_depgraph_sync_gate<br/>rename_depgraph_sync_gate.py — 文件重命名后<br/>depgraph 未同步阻断门禁（RENAME-...<br/>文件: commit_gates/rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["commit_gates/rule_execution_pairing_gate<br/>rule_execution_pairing_gate.py —<br/>规则-执行配对门禁（RULE-EXECUTION-PAIRING，...<br/>文件: commit_gates<br/>/rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["commit_gates/rule_four_way_alignment_gate<br/>rule_four_way_alignment_gate.py —<br/>规则四方对齐门禁（RULE-FOUR-WAY-ALIGN）<br/>文件: commit_gates<br/>/rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["commit_gates/ruling_commit_verified_gate<br/>ruling_commit_verified_gate.py —<br/>文档'已完成'声明 commit hash 真实性硬验证门...<br/>文件: commit_gates<br/>/ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["commit_gates/ruling_reference_gate<br/>ruling_reference_gate.py — 裁定#NNN<br/>悬空引用自动检测门禁（RULING-REFERENCE）<br/>文件: commit_gates/ruling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["commit_gates/schema_file_exists_gate<br/>schema_file_exists_gate.py — SCHEMA-FILE-EXISTS<br/>block 门禁<br/>文件: commit_gates/schema_file_exists_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["commit_gates/scripts_import_integrity_gate<br/>scripts_import_integrity_gate.py —<br/>_shared.constants 符号导入完整性门禁<br/>文件: commit_gates<br/>/scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["commit_gates/session_required_gate<br/>session_required_gate.py — session<br/>注册强制门禁（SESSION-REQUIRED，2026-07-0...<br/>文件: commit_gates/session_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["commit_gates/snapshot_drift_gate<br/>snapshot_drift_gate.py —<br/>运行时违规快照漂移阻断门禁（SNAPSHOT-DRIFT，...<br/>文件: commit_gates/snapshot_drift_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["commit_gates/ssot_redefinition_gate<br/>ssot_redefinition_gate.py — SSoT<br/>符号重复定义硬阻断门禁<br/>文件: commit_gates/ssot_redefinition_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["commit_gates/table_name_registry_gate<br/>table_name_registry_gate.py —<br/>TABLE-NAME-REGISTRY block 门禁<br/>文件: commit_gates/table_name_registry_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["commit_gates/test_source_consistency_gate<br/>test_source_consistency_gate.py —<br/>测试-源码符号一致性门禁（TEST-SOURCE-CONSI...<br/>文件: commit_gates<br/>/test_source_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["commit_gates/tests_coverage_gate<br/>tests_coverage_gate.py — Gate 测试覆盖率校验<br/>meta-gate（META-TESTS-COVERAGE...<br/>文件: commit_gates/tests_coverage_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["commit_gates/ttl_gate<br/>ttl_gate.py — ttl 字段校验门禁（治本：弥补<br/>--no-verify 绕过 pre-commit GATE-...<br/>文件: commit_gates/ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["commit_gates/undefined_name_gate<br/>undefined_name_gate.py — UNDEFINED-NAME 门禁<br/>（F821 未定义符号硬阻断）<br/>文件: commit_gates/undefined_name_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["commit_gates/unsafe_dict_spread_gate<br/>unsafe_dict_spread_gate.py — ``**data``<br/>直接展开模式 warn 级门禁<br/>文件: commit_gates/unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["commit_gates/vocab_chain_gate<br/>vocab_chain_gate.py — SSoT 引用硬编码阻断门禁<br/>（VOCAB-CHAIN，...<br/>文件: commit_gates/vocab_chain_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["commit_gates/vocab_hardcode_gate<br/>vocab_hardcode_gate.py — 新增 .py<br/>文件词表硬编码阻断门禁（VOCAB-HARDCODE，20...<br/>文件: commit_gates/vocab_hardcode_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["commit_gates/zephyr_env_direct_access_gate<br/>zephyr_env_direct_access_gate.py — ZEPHYR_ENV<br/>直访硬阻断门禁（ZEPHYR-ENV-DIR...<br/>文件: commit_gates<br/>/zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["rule_bridge/gate_auto_registrar<br/>gate_auto_registrar.py — YAML 驱动的 in-process<br/>gate 自动注册器（...<br/>文件: rule_bridge/gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_data_test_symbol_normalizer_py["data/test_symbol_normalizer<br/>test_symbol_normalizer.py — TRAE-082 symbol<br/>标准化模块测试。<br/>文件: data/test_symbol_normalizer.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_check_yaml_anchor_consistency_py["commit_gates/test_check_yaml_anchor_consistency<br/>test_check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描 smoke test.<br/>文件: commit_gates<br/>/test_check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    tests_governance_test_apply_dataflowgraph_smoke_py["governance/test_apply_dataflowgraph_smoke<br/>test_apply_dataflowgraph_smoke.py —<br/>apply_dataflowgraph.py end-to-end smoke test<br/>文件: governance<br/>/test_apply_dataflowgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_decisiongraph_smoke_py["governance/test_apply_decisiongraph_smoke<br/>test_apply_decisiongraph_smoke.py —<br/>apply_decisiongraph.py end-to-end smoke test<br/>文件: governance<br/>/test_apply_decisiongraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_depgraph_smoke_py["governance/test_apply_depgraph_smoke<br/>test_apply_depgraph_smoke.py —<br/>apply_depgraph.py end-to-end smoke test<br/>文件: governance/test_apply_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_audit_return_contract_usage_py["governance/test_audit_return_contract_usage<br/>test_audit_return_contract_usage.py — 返回契约<br/>ok 键审计脚本单元测试<br/>文件: governance<br/>/test_audit_return_contract_usage.py<br/>(生产态 / production)"]
    tests_governance_test_audit_worktree_ops_telemetry_py["governance/test_audit_worktree_ops_telemetry<br/>test_audit_worktree_ops_telemetry.py —<br/>worktree_ops_log 遥测完整性审计测试<br/>文件: governance<br/>/test_audit_worktree_ops_telemetry.py<br/>(生产态 / production)"]
    tests_governance_test_generate_project_depgraph_smoke_py["governance/test_generate_project_depgraph_smoke<br/>test_generate_project_depgraph_smoke.py —<br/>generate_project_depgraph.py e2e s...<br/>文件: governance<br/>/test_generate_project_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["governance<br/>/test_post_commit_guard_no_verify_threshold<br/>test_post_commit_guard_no_verify_threshold.py —<br/>高基数 --no-verify 阈值阻断 ...<br/>文件: governance<br/>/test_post_commit_guard_no_verify_threshold.py<br/>(生产态 / production)"]
    tests_governance_test_run_silent_failure_regression_py["governance/test_run_silent_failure_regression<br/>test_run_silent_failure_regression.py —<br/>silent-failure 回归 runner 单元测试...<br/>文件: governance<br/>/test_run_silent_failure_regression.py<br/>(生产态 / production)"]
    tests_governance_test_session_startup_health_check_py["governance/test_session_startup_health_check<br/>test_session_startup_health_check.py — AI<br/>session 启动健康度自检单元测试<br/>文件: governance<br/>/test_session_startup_health_check.py<br/>(生产态 / production)"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["governance/test_sync_yaml_to_depgraph_smoke<br/>test_sync_yaml_to_depgraph_smoke.py —<br/>sync_yaml_to_depgraph.py e2e smoke test<br/>文件: governance<br/>/test_sync_yaml_to_depgraph_smoke.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ scripts_governance_d7_code_check_yaml_anchor_consistency_py
    scripts_governance_d7_code_check_yaml_anchor_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py ~~~ src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_manager_py
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_register_py
    src_zephyr_gov_code_quality_code_dedup_canary_register_py ~~~ src_zephyr_gov_code_quality_code_dedup_cli_py
    src_zephyr_gov_code_quality_code_dedup_cli_py ~~~ src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py ~~~ src_zephyr_gov_code_quality_code_dedup_code_simulator_py
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py ~~~ src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_debt_projector_py
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py ~~~ src_zephyr_gov_code_quality_code_dedup_decision_auditor_py
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_degradation_py
    src_zephyr_gov_code_quality_code_dedup_degradation_py ~~~ src_zephyr_gov_code_quality_code_dedup_diff_detector_py
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py ~~~ src_zephyr_gov_code_quality_code_dedup_extraction_safety_py
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py ~~~ src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_file_creator_py
    src_zephyr_gov_code_quality_code_dedup_file_creator_py ~~~ src_zephyr_gov_code_quality_code_dedup_function_discovery_py
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py ~~~ src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_health_monitor_py
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py ~~~ src_zephyr_gov_code_quality_code_dedup_integration_hub_py
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py ~~~ src_zephyr_gov_code_quality_code_dedup_integrations_py
    src_zephyr_gov_code_quality_code_dedup_integrations_py ~~~ src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py ~~~ src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py ~~~ src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py ~~~ src_zephyr_gov_code_quality_code_dedup_path_index_validator_py
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_phase_executor_py
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py ~~~ src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py ~~~ src_zephyr_gov_code_quality_code_dedup_prioritizer_py
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py ~~~ src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py ~~~ src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py ~~~ src_zephyr_gov_code_quality_code_dedup_self_scanner_py
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py ~~~ src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py ~~~ src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py ~~~ src_zephyr_gov_code_quality_code_dedup_shared_evolver_py
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py ~~~ src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_signature_matcher_py
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py ~~~ src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py ~~~ src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_success_validator_py
    src_zephyr_gov_code_quality_code_dedup_success_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_symbol_index_py
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py ~~~ src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_init_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_verifier_py
    src_zephyr_gov_code_quality_code_dedup_verifier_py ~~~ src_zephyr_gov_enforcement_commit_gates_init_py
    src_zephyr_gov_enforcement_commit_gates_init_py ~~~ src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_create_guard_py
    src_zephyr_gov_enforcement_commit_gates_create_guard_py ~~~ src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_encoding_gate_py
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_gate_repo_py
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py ~~~ src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_god_class_gate_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_session_required_gate_py
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ttl_gate_py
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py ~~~ src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py ~~~ tests_data_test_symbol_normalizer_py
    tests_data_test_symbol_normalizer_py ~~~ tests_governance_commit_gates_test_check_yaml_anchor_consistency_py
    tests_governance_commit_gates_test_check_yaml_anchor_consistency_py ~~~ tests_governance_test_apply_dataflowgraph_smoke_py
    tests_governance_test_apply_dataflowgraph_smoke_py ~~~ tests_governance_test_apply_decisiongraph_smoke_py
    tests_governance_test_apply_decisiongraph_smoke_py ~~~ tests_governance_test_apply_depgraph_smoke_py
    tests_governance_test_apply_depgraph_smoke_py ~~~ tests_governance_test_audit_return_contract_usage_py
    tests_governance_test_audit_return_contract_usage_py ~~~ tests_governance_test_audit_worktree_ops_telemetry_py
    tests_governance_test_audit_worktree_ops_telemetry_py ~~~ tests_governance_test_generate_project_depgraph_smoke_py
    tests_governance_test_generate_project_depgraph_smoke_py ~~~ tests_governance_test_post_commit_guard_no_verify_threshold_py
    tests_governance_test_post_commit_guard_no_verify_threshold_py ~~~ tests_governance_test_run_silent_failure_regression_py
    tests_governance_test_run_silent_failure_regression_py ~~~ tests_governance_test_session_startup_health_check_py
    tests_governance_test_session_startup_health_check_py ~~~ tests_governance_test_sync_yaml_to_depgraph_smoke_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py["code_dedup/annotations<br/>共享函数注解引擎 — @shared / @known_dup /<br/>@intentional 三注解.<br/>文件: code_dedup/annotations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["code_dedup/auto_fixer<br/>安全自动修复引擎——五直接开关+五间接约束.<br/>文件: code_dedup/auto_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_config_py["code_dedup/config<br/>配置管理 — 策略树 YAML 加载 + 项目规模感知四<br/>Tier 自适应阈值.<br/>文件: code_dedup/config.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["code_dedup/exit_codes<br/>退出码定义模块——五档exit code<br/>0-4枚举+描述+判定逻辑.<br/>文件: code_dedup/exit_codes.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_report_py["code_dedup/report<br/>报告生成器 — YAML/JSON 输出 + 退出码判定 +<br/>Health Score 聚合.<br/>文件: code_dedup/report.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["trackers/blind_spot_tracker<br/>盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>文件: trackers/blind_spot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["commit_gates/_diff_helpers<br/>_diff_helpers.py — gate 共享 diff 解析工具模块<br/>文件: commit_gates/_diff_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["commit_gates/_reference_helpers<br/>_reference_helpers.py —<br/>引用检测门禁共享工具函数（ARCH-REFERENCE /<br/>RULING-RE...<br/>文件: commit_gates/_reference_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["commit_gates/capability_lookup_bypass_policy<br/>capability_lookup_bypass_policy.py —<br/>CAPABILITY-LOOKUP bypass 策略共享模块<br/>文件: commit_gates<br/>/capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["commit_gates/perm_trigger_gate<br/>perm_trigger_gate.py —<br/>永久系统脚本时间触发模式无事件订阅阻断门禁<br/>（PERM-TRIG...<br/>文件: commit_gates/perm_trigger_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_config_py ~~~ src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py ~~~ src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_report_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py ~~~ src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py ~~~ src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    tests_governance_test_audit_worktree_ops_telemetry_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT["审计追踪<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>Audit Trail<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_init_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_d3_metadata_check_pure_assertion_py,scripts_governance_d7_code_check_module_id_consistency_py,scripts_governance_d7_code_check_yaml_anchor_consistency_py,src_zephyr_gov_code_quality_init_py,src_zephyr_gov_code_quality_code_dedup_init_py,src_zephyr_gov_code_quality_code_dedup_annotations_py,src_zephyr_gov_code_quality_code_dedup_ast_comparator_py,src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py,src_zephyr_gov_code_quality_code_dedup_auto_fixer_py,src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py,src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py,src_zephyr_gov_code_quality_code_dedup_cache_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_register_py,src_zephyr_gov_code_quality_code_dedup_cli_py,src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py,src_zephyr_gov_code_quality_code_dedup_code_simulator_py,src_zephyr_gov_code_quality_code_dedup_config_py,src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py,src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py,src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py,src_zephyr_gov_code_quality_code_dedup_debt_projector_py,src_zephyr_gov_code_quality_code_dedup_decision_auditor_py,src_zephyr_gov_code_quality_code_dedup_degradation_py,src_zephyr_gov_code_quality_code_dedup_diff_detector_py,src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py,src_zephyr_gov_code_quality_code_dedup_exit_codes_py,src_zephyr_gov_code_quality_code_dedup_extraction_safety_py,src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py,src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py,src_zephyr_gov_code_quality_code_dedup_file_creator_py,src_zephyr_gov_code_quality_code_dedup_function_discovery_py,src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py,src_zephyr_gov_code_quality_code_dedup_health_monitor_py,src_zephyr_gov_code_quality_code_dedup_integration_hub_py,src_zephyr_gov_code_quality_code_dedup_integrations_py,src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py,src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py,src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py,src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py,src_zephyr_gov_code_quality_code_dedup_path_index_validator_py,src_zephyr_gov_code_quality_code_dedup_phase_executor_py,src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py,src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py,src_zephyr_gov_code_quality_code_dedup_prioritizer_py,src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py,src_zephyr_gov_code_quality_code_dedup_report_py,src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py,src_zephyr_gov_code_quality_code_dedup_self_scanner_py,src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py,src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py,src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py,src_zephyr_gov_code_quality_code_dedup_shared_evolver_py,src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py,src_zephyr_gov_code_quality_code_dedup_signature_matcher_py,src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py,src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py,src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py,src_zephyr_gov_code_quality_code_dedup_success_validator_py,src_zephyr_gov_code_quality_code_dedup_symbol_index_py,src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py,src_zephyr_gov_code_quality_code_dedup_trackers_init_py,src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py,src_zephyr_gov_code_quality_code_dedup_verifier_py,src_zephyr_gov_enforcement_commit_gates_init_py,src_zephyr_gov_enforcement_commit_gates_diff_helpers_py,src_zephyr_gov_enforcement_commit_gates_reference_helpers_py,src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py,src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py,src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py,src_zephyr_gov_enforcement_commit_gates_create_guard_py,src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py,src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py,src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py,src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py,src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py,src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py,src_zephyr_gov_enforcement_commit_gates_encoding_gate_py,src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py,src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py,src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py,src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py,src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py,src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py,src_zephyr_gov_enforcement_commit_gates_gate_repo_py,src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py,src_zephyr_gov_enforcement_commit_gates_god_class_gate_py,src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py,src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py,src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py,src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py,src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py,src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py,src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py,src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py,src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py,src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py,src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py,src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py,src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py,src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py,src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py,src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py,src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py,src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py,src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py,src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py,src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_session_required_gate_py,src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py,src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py,src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py,src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py,src_zephyr_gov_enforcement_commit_gates_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py,src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py,src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py,src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py,tests_data_test_symbol_normalizer_py,tests_governance_commit_gates_test_check_yaml_anchor_consistency_py,tests_governance_test_apply_dataflowgraph_smoke_py,tests_governance_test_apply_decisiongraph_smoke_py,tests_governance_test_apply_depgraph_smoke_py,tests_governance_test_audit_return_contract_usage_py,tests_governance_test_audit_worktree_ops_telemetry_py,tests_governance_test_generate_project_depgraph_smoke_py,tests_governance_test_post_commit_guard_no_verify_threshold_py,tests_governance_test_run_silent_failure_regression_py,tests_governance_test_session_startup_health_check_py,tests_governance_test_sync_yaml_to_depgraph_smoke_py production
    class D_SHARED,D_GOV_ENFORCEMENT,D_GOV_AUDIT,D_GOVERNANCE,D_GOV_SCRIPTS external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 171 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["d3_metadata/check_pure_assertion<br/>check_pure_assertion.py — GOV-DOC-016<br/>纯陈述原则检测真源（SSoT）。<br/>文件: d3_metadata/check_pure_assertion.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_module_id_consistency_py["d7_code/check_module_id_consistency<br/>check_module_id_consistency.py — module_id<br/>全仓一致性扫描（--scan-existing ...<br/>文件: d7_code/check_module_id_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_yaml_anchor_consistency_py["d7_code/check_yaml_anchor_consistency<br/>check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描.<br/>文件: d7_code/check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_init_py["zephyr/gov_code_quality 包入口<br/>gov_code_quality domain package — code quality<br/>governance (D_GOV_CODE_QUALITY).<br/>文件: gov_code_quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_init_py["gov_code_quality/code_dedup 包入口<br/>code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: code_dedup/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["code_dedup/ast_comparator<br/>Stage 2: AST 级精确比对器.<br/>文件: code_dedup/ast_comparator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["code_dedup/atomic_fixer<br/>原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT<br/>-> APPLY -> RECOVER.<br/>文件: code_dedup/atomic_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["code_dedup/behavioral_sampler<br/>行为采样验证器 — Stage 0.25 低成本快速验证.<br/>文件: code_dedup/behavioral_sampler.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["code_dedup/behavioral_trust_checker<br/>行为信任检查器 — 行为漂移DIVERGED检测.<br/>文件: code_dedup/behavioral_trust_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["code_dedup/cache_manager<br/>Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>文件: code_dedup/cache_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["code_dedup/canary_manager<br/>金丝雀工厂——生成已知oracle 文件<br/>用于引擎检出+回归测试.<br/>文件: code_dedup/canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["code_dedup/canary_register<br/>金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>文件: code_dedup/canary_register.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["code_dedup/cli<br/>code-dedup-engine<br/>CLI——子命令映射+退出码+扫描入口.<br/>文件: code_dedup/cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["code_dedup/code_analyzer_runner<br/>检查运行器——按照敏感基线运行三阶段+导出 yaml<br/>报告.<br/>文件: code_dedup/code_analyzer_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["code_dedup/code_simulator<br/>代码模拟器——播放录制的克隆演化序列，stress-test<br/>AST/baseline归一化.<br/>文件: code_dedup/code_simulator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["code_dedup/contract_consistency_checker<br/>API契约一致性检查器 — 存在性·行为·契约三维.<br/>文件: code_dedup/contract_consistency_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["code_dedup/cross_boundary_detector<br/>跨边界克隆感知——四大边界差异化检测+独立策略+跨边<br/>界保守auto_fix规则.<br/>文件: code_dedup/cross_boundary_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["code_dedup/dead_module_detector<br/>死共享模块检测器 — shared/子模块无人使用 -><br/>DEAD.<br/>文件: code_dedup/dead_module_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["code_dedup/debt_projector<br/>去重债务预测器 — weeks_to_payoff + intake_rate<br/>vs fix_rate 蒙特卡洛模拟.<br/>文件: code_dedup/debt_projector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["code_dedup/decision_auditor<br/>决策审计链 — DecisionFingerprint 不可变追加日志.<br/>文件: code_dedup/decision_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["code_dedup/degradation<br/>降级运行管理器 — 各 Stage 独立 try/except +<br/>degradation_level + exit code.<br/>文件: code_dedup/degradation.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["code_dedup/diff_detector<br/>Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>文件: code_dedup/diff_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["code_dedup/doom_loop_guard<br/>Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>文件: code_dedup/doom_loop_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["code_dedup/extraction_safety<br/>安全提取适配性评估器 — Suitability Score 0-100<br/>+ 不安全提取模式检测.<br/>文件: code_dedup/extraction_safety.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["code_dedup/false_negative_auditor<br/>三层漏报盲审器 — L1 Sweep + L2 Canary + L3<br/>Sampling.<br/>文件: code_dedup/false_negative_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["code_dedup/fifteen_dimension_auditor<br/>15维超综合审计首页 — 逐项证明'做过且做对'.<br/>文件: code_dedup/fifteen_dimension_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["code_dedup/file_creator<br/>文件创建清单执行器 — 验证所有源/测试<br/>/数据文件存在性.<br/>文件: code_dedup/file_creator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["code_dedup/function_discovery<br/>共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>文件: code_dedup/function_discovery.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["code_dedup/grandfather_manager<br/>Grandfather 三定律 — 古老重复管理.<br/>文件: code_dedup/grandfather_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["code_dedup/health_monitor<br/>健康仪表盘 — Dedup Health Score 0-100 + 趋势 +<br/>Session Log 写入.<br/>文件: code_dedup/health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["code_dedup/integration_hub<br/>集成协调器 — 24集成+19更新+16GitHub整合.<br/>文件: code_dedup/integration_hub.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["code_dedup/integrations<br/>集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>文件: code_dedup/integrations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["code_dedup/micro_clone_detector<br/>微型克隆检测器 — n-gram频率计数,<br/>1-2行高频模式聚合.<br/>文件: code_dedup/micro_clone_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["code_dedup/mock_duplicate_generator<br/>可控克隆生产器——零假阳性可期待引擎分子离散<br/>文件: code_dedup/mock_duplicate_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["code_dedup/monoculture_guard<br/>Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>文件: code_dedup/monoculture_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["code_dedup/observation_window_guard<br/>提取后稳定观察期守护 — 对标SDP 14天观察.<br/>文件: code_dedup/observation_window_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["code_dedup/path_index_validator<br/>路径索引验证——验证 config<br/>数据集相对路径表与实际文件系统同步.<br/>文件: code_dedup/path_index_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["code_dedup/phase_executor<br/>6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>文件: code_dedup/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["code_dedup/policy_tree_validator<br/>策略树自动一致性校验器 — 虚线箭头影响分析.<br/>文件: code_dedup/policy_tree_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["code_dedup/pre_apply_integrity_gate<br/>Pre-Apply 完整性门 — SHA256重新验证.<br/>文件: code_dedup/pre_apply_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["code_dedup/prioritizer<br/>修复优先级排序器 — 置信度×Impact×适配性<br/>三因子排序.<br/>文件: code_dedup/prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["code_dedup/recovery_manifest_writer<br/>Recovery Manifest Writer — R2纯文本base64<br/>Manifest.<br/>文件: code_dedup/recovery_manifest_writer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["code_dedup/risk_mitigator<br/>R1-R45全量风险缓解执行器 — 逐条检查缓解措施 +<br/>mitigation_tracker.yaml.<br/>文件: code_dedup/risk_mitigator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["code_dedup/self_scanner<br/>引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>文件: code_dedup/self_scanner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["code_dedup/sensitivity_sweeper<br/>敏感性扫荡——threshold扫描->固化成new baseline<br/>（零假阳性+触达率保险）.<br/>文件: code_dedup/sensitivity_sweeper.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["code_dedup/shadow_trust_validator<br/>影子信任验证器 — ImportError 防护回路.<br/>文件: code_dedup/shadow_trust_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["code_dedup/shadow_verifier<br/>影子清单验证器 — size sanity check +<br/>semantic验证 + 覆盖度报告.<br/>文件: code_dedup/shadow_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["code_dedup/shared_evolver<br/>共享函数自我进化引擎 — 自动升降级 +<br/>行为漂移锁定.<br/>文件: code_dedup/shared_evolver.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["code_dedup/shared_lifecycle_manager<br/>共享函数生命周期管理 —<br/>Active->Deprecated->Grace->Sunset->Retired<br/>五阶段状态机.<br/>文件: code_dedup/shared_lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["code_dedup/signature_matcher<br/>Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配.<br/>文件: code_dedup/signature_matcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["code_dedup/simplicity_auditor<br/>引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax<br/>报告.<br/>文件: code_dedup/simplicity_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["code_dedup/ssot_registrar<br/>SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>文件: code_dedup/ssot_registrar.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["code_dedup/stale_shared_detector<br/>过时共享函数检测器 — 无caller × 30天 -><br/>STALE标记.<br/>文件: code_dedup/stale_shared_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["code_dedup/success_validator<br/>成功验证——判断一次去重操作是否真正消灭了克隆.<br/>文件: code_dedup/success_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["code_dedup/symbol_index<br/>符号索引 — 全局函数/类/import映射表.<br/>文件: code_dedup/symbol_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["code_dedup/thematic_clusterer<br/>主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>文件: code_dedup/thematic_clusterer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["code_dedup/trackers 包入口<br/>tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: trackers/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["trackers/consequence_tracker<br/>后果追踪——记录每次修复操作对依赖方的影响.<br/>文件: trackers/consequence_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["trackers/hotspot_tracker<br/>热点追踪器 — 90天滑动窗口 + 高频变动检测 +<br/>新项目预热清单.<br/>文件: trackers/hotspot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["trackers/import_surface_tracker<br/>Import表面积负债追踪 — SBS 0-100 + shared<br/>burden score.<br/>文件: trackers/import_surface_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["trackers/question_tracker<br/>问题追踪——扫描中发现需要人工处理的问题.<br/>文件: trackers/question_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["trackers/risk_mitigation_tracker<br/>风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍<br/>未fix.<br/>文件: trackers/risk_mitigation_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["code_dedup/verifier<br/>修复验证器 — import + 类型 + 行为采样验证.<br/>文件: code_dedup/verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_init_py["gov_enforcement/commit_gates 包入口<br/>commit_gates — GitCommitGateway pre-commit<br/>门禁实现包。<br/>文件: commit_gates/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["commit_gates/arch_reference_gate<br/>arch_reference_gate.py — #ARCH-NNN /<br/>#ARCH-DOMAIN-NNN 悬空引用自动检测门禁（...<br/>文件: commit_gates/arch_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["commit_gates/asyncio_run_in_context_gate<br/>asyncio_run_in_context_gate.py —<br/>异步上下文误用硬阻断门禁（ASYNCIO-RUN-IN-CO...<br/>文件: commit_gates<br/>/asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["commit_gates/bare_getenv_gate<br/>bare_getenv_gate.py — 裸 os.getenv<br/>读密钥阻断门禁（NO-BARE-GETENV，§5.17.10...<br/>文件: commit_gates/bare_getenv_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["commit_gates/bare_sql_gate<br/>bare_sql_gate.py — 裸SQL字面量阻断门禁<br/>（NO-BARE-SQL，§5.160.2 防复发）<br/>文件: commit_gates/bare_sql_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["commit_gates/bare_subprocess_gate<br/>bare_subprocess_gate.py — 裸 subprocess<br/>调用硬阻断门禁（BARE-SUBPROCESS）<br/>文件: commit_gates/bare_subprocess_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["commit_gates/blueprint_amodule_consistency_gate<br/>blueprint_amodule_consistency_gate.py —<br/>(A_module) 头部 module_id 格式一致性门禁<br/>文件: commit_gates<br/>/blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["commit_gates/blueprint_amodule_cross_check_gate<br/>blueprint_amodule_cross_check_gate.py —<br/>(BLUEPRINT) vs (A_module) 交叉校验门禁<br/>文件: commit_gates<br/>/blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["commit_gates/blueprint_format_gate<br/>blueprint_format_gate.py — (BLUEPRINT) 头部<br/>module_id 格式阻断门禁（BLUEPRIN...<br/>文件: commit_gates/blueprint_format_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["commit_gates/capability_consistency_gate<br/>capability_consistency_gate.py — Provider<br/>路由-meta 一致性门禁（CAP-CONSISTE...<br/>文件: commit_gates<br/>/capability_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["commit_gates/capability_lookup_required_gate<br/>capability_lookup_required_gate.py — Capability<br/>Lookup 强制门禁（CAPABILITY-...<br/>文件: commit_gates<br/>/capability_lookup_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["commit_gates/capability_overlap_gate<br/>capability_overlap_gate.py — 新建 .py 文件<br/>CapabilityLookup 提示门禁（warn-o...<br/>文件: commit_gates/capability_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["commit_gates/ch_batch_size_gate<br/>ch_batch_size_gate.py — CH 批量写入防回退门禁<br/>（CH-BATCH-SIZE，§18.4 防复发）<br/>文件: commit_gates/ch_batch_size_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["commit_gates/ch_final_gate<br/>ch_final_gate.py — ch_writer.query()<br/>直接调用阻断门禁（CH-FINAL-GATE，裁定 #...<br/>文件: commit_gates/ch_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["commit_gates/ch_version_col_gate<br/>ch_version_col_gate.py — CH version<br/>列语义误用阻断门禁（CH-VERSION-COL，裁定...<br/>文件: commit_gates/ch_version_col_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["commit_gates/claim_required_gate<br/>claim_required_gate.py — claim_files<br/>前置检查门禁（CLAIM-REQUIRED，2026-06-3...<br/>文件: commit_gates/claim_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["commit_gates/consumers_accuracy_gate<br/>consumers_accuracy_gate.py — CONSUMERS<br/>字段准确性 warn-only 门禁（CONSUMERS-...<br/>文件: commit_gates/consumers_accuracy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["commit_gates/create_guard<br/>create_guard.py — 新建 .py / 非 rules/ .yaml<br/>文件 creation_token 阻断门禁（C...<br/>文件: commit_gates/create_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["commit_gates/dangling_reference_gate<br/>dangling_reference_gate.py — AGENTS.md §X.Y<br/>悬空引用自动检测门禁（DANGLING-...<br/>文件: commit_gates/dangling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["commit_gates/data_task_completeness_gate<br/>data_task_completeness_gate.py —<br/>数据任务完整性门禁（warn 级，提醒型）<br/>文件: commit_gates<br/>/data_task_completeness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["commit_gates/datetime_now_forbidden_gate<br/>datetime_now_forbidden_gate.py —<br/>时间戳约定硬阻断门禁（DATETIME-NOW-FORBIDDEN）<br/>文件: commit_gates<br/>/datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["commit_gates/depgraph_freshness_gate<br/>depgraph_freshness_gate.py — depgraph<br/>新鲜度门禁（dual-threshold，...<br/>文件: commit_gates/depgraph_freshness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["commit_gates/depgraph_write_path_gate<br/>depgraph_write_path_gate.py — depgraph<br/>写入路径白名单门禁（DEPGRAPH-WRITE-PATH）<br/>文件: commit_gates/depgraph_write_path_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["commit_gates/derivation_annotation_gate<br/>derivation_annotation_gate.py —<br/>派生关系声明真实性校验门禁（DERIVATION-ANNOT...<br/>文件: commit_gates/derivation_annotation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["commit_gates/directory_contract_gate<br/>directory_contract_gate.py — DCR-001~007<br/>等效校验门禁（治本：弥补 --no-verif...<br/>文件: commit_gates/directory_contract_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["commit_gates/doc_ref_broken_gate<br/>doc_ref_broken_gate.py —<br/>文档相对路径断裂引用阻断门禁（DOC-REF-BROKEN）<br/>文件: commit_gates/doc_ref_broken_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["commit_gates/domain_fk_gate<br/>domain_fk_gate.py — (DOMAIN) 头部域注册表 FK<br/>校验门禁（GATE-DOMAIN-FK）<br/>文件: commit_gates/domain_fk_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["commit_gates/domain_name_zh_direct_access_gate<br/>domain_name_zh_direct_access_gate.py —<br/>DOMAIN_NAME_ZH 字典直接访问硬阻断门禁<br/>文件: commit_gates<br/>/domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["commit_gates/empty_handler_gate<br/>empty_handler_gate.py — 空事件 handler<br/>函数阻断门禁（EMPTY-HANDLER）<br/>文件: commit_gates/empty_handler_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["commit_gates/encoding_gate<br/>encoding_gate.py — 编码安全校验门禁（治本：弥补<br/>--no-verify 绕过 pre-commit ...<br/>文件: commit_gates/encoding_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["commit_gates/exempt_zone_frontmatter_gate<br/>exempt_zone_frontmatter_gate.py — 豁免区<br/>frontmatter 门禁（Phase 3 reconcile...<br/>文件: commit_gates<br/>/exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["commit_gates/file_copy_gate<br/>file_copy_gate.py — 新增 .py<br/>文件复制检测阻断门禁（FILE-COPY，2026-07-03<br/>Pha...<br/>文件: commit_gates/file_copy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["commit_gates/file_placement_ttl_gate<br/>file_placement_ttl_gate.py — 文件放置与 TTL<br/>一致性门禁（治本 #ARCH-049：防止...<br/>文件: commit_gates/file_placement_ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["commit_gates/folder_capacity_hard_limit_gate<br/>folder_capacity_hard_limit_gate.py —<br/>文件夹容量硬上限门禁（FOLDER-CAPACITY-H...<br/>文件: commit_gates<br/>/folder_capacity_hard_limit_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["commit_gates/foreign_change_gate<br/>foreign_change_gate.py — 外来变更检测门禁<br/>（FOREIGN-CHANGE-DETECTION，ARCH-05...<br/>文件: commit_gates/foreign_change_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["commit_gates/forged_gw_marker_gate<br/>forged_gw_marker_gate.py — Forged GW Marker<br/>前置检测门禁（FORGED-GW-MARKER，...<br/>文件: commit_gates/forged_gw_marker_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["commit_gates/function_dup_gate<br/>function_dup_gate.py — 重复函数实现阻断门禁<br/>（FUNCTION-DUP）<br/>文件: commit_gates/function_dup_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["commit_gates/gate_repo<br/>gate_repo.py — gates 表持久化仓库（AUDIT-07<br/>P1-5: 从 gate_engine.py 提取）<br/>文件: commit_gates/gate_repo.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["commit_gates/git_call_budget_gate<br/>git_call_budget_gate.py — Git 调用预算<br/>warn-only 门禁（GIT-CALL-BUDGET，§AR...<br/>文件: commit_gates/git_call_budget_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["commit_gates/god_class_gate<br/>god_class_gate.py — God Class 阻断门禁<br/>（NO-GOD-CLASS，§5.150 防复发）<br/>文件: commit_gates/god_class_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["commit_gates/hardcoded_url_gate<br/>hardcoded_url_gate.py — 硬编码 localhost URL<br/>阻断门禁（NO-HARDCODED-URL，§5...<br/>文件: commit_gates/hardcoded_url_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["commit_gates/held_overlap_gate<br/>held_overlap_gate.py — 搭便车防护门禁<br/>（HELD-OVERLAP，2026-06-30 治本）<br/>文件: commit_gates/held_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["commit_gates/high_complexity_gate<br/>high_complexity_gate.py — 高循环复杂度阻断门禁<br/>（NO-HIGH-COMPLEXITY，§5.158 ...<br/>文件: commit_gates/high_complexity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["commit_gates/id_uniqueness_gate<br/>id_uniqueness_gate.py — pre-commit hook ID<br/>唯一性门禁（Phase 3 reconciler->g...<br/>文件: commit_gates/id_uniqueness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["commit_gates/import_direction_gate<br/>import_direction_gate.py — shared<br/>层向上依赖阻断门禁（NO-UPWARD-IMPORT，§5....<br/>文件: commit_gates/import_direction_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["commit_gates/import_integrity_gate<br/>import_integrity_gate.py — IMPORT-INTEGRITY<br/>门禁（悬空 import 硬阻断）<br/>文件: commit_gates/import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["commit_gates/issue_resolved_integrity_gate<br/>issue_resolved_integrity_gate.py —<br/>ISSUE-RESOLVED-INTEGRITY warn-only 门禁<br/>文件: commit_gates<br/>/issue_resolved_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["commit_gates/long_param_list_gate<br/>long_param_list_gate.py — 长参数列表阻断门禁<br/>（NO-LONG-PARAM-LIST，§5.150 防...<br/>文件: commit_gates/long_param_list_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["commit_gates/manual_only_permanent_gate<br/>manual_only_permanent_gate.py — 永久系统脚本<br/>manual 触发无事件订阅阻断门禁（...<br/>文件: commit_gates/manual_only_permanent_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["commit_gates/mcp_version_field_gate<br/>mcp_version_field_gate.py — MCP version<br/>字段缺失硬阻断门禁（MCP-VERSION-FIELD）<br/>文件: commit_gates/mcp_version_field_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["commit_gates/module_id_consistency_gate<br/>module_id_consistency_gate.py — module_id<br/>三声明轨道一致性 + count 派生 + 跨...<br/>文件: commit_gates/module_id_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["commit_gates/msg_exposure_gate<br/>msg_exposure_gate.py —<br/>错误消息暴露敏感信息阻断门禁（MSG-EXPOSURE）<br/>文件: commit_gates/msg_exposure_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["commit_gates/msg_style_gate<br/>msg_style_gate.py — 错误消息标点<br/>/箭头风格阻断门禁（MSG-STYLE）<br/>文件: commit_gates/msg_style_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["commit_gates/mutable_const_without_final_gate<br/>mutable_const_without_final_gate.py —<br/>可变常量缺 Final 标注硬阻断门禁（MUTAB...<br/>文件: commit_gates<br/>/mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["commit_gates/new_file_depgraph_gate<br/>new_file_depgraph_gate.py — 新建 .py 文件<br/>depgraph 未登记硬阻断门禁（NEW-FIL...<br/>文件: commit_gates/new_file_depgraph_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["commit_gates/no_import_side_effect_gate<br/>no_import_side_effect_gate.py —<br/>模块导入零副作用门禁（NO-IMPORT-SIDE-EFFECT...<br/>文件: commit_gates/no_import_side_effect_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["commit_gates/noqa_validation_gate<br/>noqa_validation_gate.py — 自定义 noqa<br/>标记合规性门禁（NOQA-VALIDATION，ARCH-...<br/>文件: commit_gates/noqa_validation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["commit_gates/open_without_with_gate<br/>open_without_with_gate.py — open() 未在 with<br/>内硬阻断门禁（OPEN-WITHOUT-WITH）<br/>文件: commit_gates/open_without_with_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["commit_gates/orphan_module_gate<br/>orphan_module_gate.py — 孤儿模块（无 import<br/>引用）阻断门禁（ORPHAN-MODULE）<br/>文件: commit_gates/orphan_module_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["commit_gates/panorama_alignment_gate<br/>panorama_alignment_gate.py — 三图模块对齐门禁<br/>（四图模块对齐 Step 4，ARCH-056...<br/>文件: commit_gates/panorama_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["commit_gates/precommit_offline_gate<br/>precommit_offline_gate.py — pre-commit<br/>配置离线可运行检测门禁（GATE-PRECOMMI...<br/>文件: commit_gates/precommit_offline_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["commit_gates/pure_assertion_gate<br/>pure_assertion_gate.py — 纯陈述原则阻断门禁<br/>（PURE-ASSERTION，GOV-DOC-016 治本）<br/>文件: commit_gates/pure_assertion_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["commit_gates/pure_shim_gate<br/>pure_shim_gate.py — 纯 re-export shim 阻断门禁<br/>（PURE-SHIM，P6 治本 2026-07-09）<br/>文件: commit_gates/pure_shim_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["commit_gates/r5_digit_suffix_gate<br/>r5_digit_suffix_gate.py — R5<br/>数字后缀目录禁止门禁（治本：弥补 --no-verify<br/>绕...<br/>文件: commit_gates/r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["commit_gates/reconciler_health_gate<br/>reconciler_health_gate.py — reconciler<br/>健康度门禁（#ARCH-DATAQUALITY-V1.7）<br/>文件: commit_gates/reconciler_health_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["commit_gates/relative_path_literal_gate<br/>relative_path_literal_gate.py —<br/>相对路径字面量硬阻断门禁（RELATIVE-PATH-LITE...<br/>文件: commit_gates/relative_path_literal_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["commit_gates/rename_depgraph_sync_gate<br/>rename_depgraph_sync_gate.py — 文件重命名后<br/>depgraph 未同步阻断门禁（RENAME-...<br/>文件: commit_gates/rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["commit_gates/rule_execution_pairing_gate<br/>rule_execution_pairing_gate.py —<br/>规则-执行配对门禁（RULE-EXECUTION-PAIRING，...<br/>文件: commit_gates<br/>/rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["commit_gates/rule_four_way_alignment_gate<br/>rule_four_way_alignment_gate.py —<br/>规则四方对齐门禁（RULE-FOUR-WAY-ALIGN）<br/>文件: commit_gates<br/>/rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["commit_gates/ruling_commit_verified_gate<br/>ruling_commit_verified_gate.py —<br/>文档'已完成'声明 commit hash 真实性硬验证门...<br/>文件: commit_gates<br/>/ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["commit_gates/ruling_reference_gate<br/>ruling_reference_gate.py — 裁定#NNN<br/>悬空引用自动检测门禁（RULING-REFERENCE）<br/>文件: commit_gates/ruling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["commit_gates/schema_file_exists_gate<br/>schema_file_exists_gate.py — SCHEMA-FILE-EXISTS<br/>block 门禁<br/>文件: commit_gates/schema_file_exists_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["commit_gates/scripts_import_integrity_gate<br/>scripts_import_integrity_gate.py —<br/>_shared.constants 符号导入完整性门禁<br/>文件: commit_gates<br/>/scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["commit_gates/session_required_gate<br/>session_required_gate.py — session<br/>注册强制门禁（SESSION-REQUIRED，2026-07-0...<br/>文件: commit_gates/session_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["commit_gates/snapshot_drift_gate<br/>snapshot_drift_gate.py —<br/>运行时违规快照漂移阻断门禁（SNAPSHOT-DRIFT，...<br/>文件: commit_gates/snapshot_drift_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["commit_gates/ssot_redefinition_gate<br/>ssot_redefinition_gate.py — SSoT<br/>符号重复定义硬阻断门禁<br/>文件: commit_gates/ssot_redefinition_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["commit_gates/table_name_registry_gate<br/>table_name_registry_gate.py —<br/>TABLE-NAME-REGISTRY block 门禁<br/>文件: commit_gates/table_name_registry_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["commit_gates/test_source_consistency_gate<br/>test_source_consistency_gate.py —<br/>测试-源码符号一致性门禁（TEST-SOURCE-CONSI...<br/>文件: commit_gates<br/>/test_source_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["commit_gates/tests_coverage_gate<br/>tests_coverage_gate.py — Gate 测试覆盖率校验<br/>meta-gate（META-TESTS-COVERAGE...<br/>文件: commit_gates/tests_coverage_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["commit_gates/ttl_gate<br/>ttl_gate.py — ttl 字段校验门禁（治本：弥补<br/>--no-verify 绕过 pre-commit GATE-...<br/>文件: commit_gates/ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["commit_gates/undefined_name_gate<br/>undefined_name_gate.py — UNDEFINED-NAME 门禁<br/>（F821 未定义符号硬阻断）<br/>文件: commit_gates/undefined_name_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["commit_gates/unsafe_dict_spread_gate<br/>unsafe_dict_spread_gate.py — ``**data``<br/>直接展开模式 warn 级门禁<br/>文件: commit_gates/unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["commit_gates/vocab_chain_gate<br/>vocab_chain_gate.py — SSoT 引用硬编码阻断门禁<br/>（VOCAB-CHAIN，...<br/>文件: commit_gates/vocab_chain_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["commit_gates/vocab_hardcode_gate<br/>vocab_hardcode_gate.py — 新增 .py<br/>文件词表硬编码阻断门禁（VOCAB-HARDCODE，20...<br/>文件: commit_gates/vocab_hardcode_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["commit_gates/zephyr_env_direct_access_gate<br/>zephyr_env_direct_access_gate.py — ZEPHYR_ENV<br/>直访硬阻断门禁（ZEPHYR-ENV-DIR...<br/>文件: commit_gates<br/>/zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["rule_bridge/gate_auto_registrar<br/>gate_auto_registrar.py — YAML 驱动的 in-process<br/>gate 自动注册器（...<br/>文件: rule_bridge/gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_data_test_symbol_normalizer_py["data/test_symbol_normalizer<br/>test_symbol_normalizer.py — TRAE-082 symbol<br/>标准化模块测试。<br/>文件: data/test_symbol_normalizer.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_check_yaml_anchor_consistency_py["commit_gates/test_check_yaml_anchor_consistency<br/>test_check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描 smoke test.<br/>文件: commit_gates<br/>/test_check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    tests_governance_test_apply_dataflowgraph_smoke_py["governance/test_apply_dataflowgraph_smoke<br/>test_apply_dataflowgraph_smoke.py —<br/>apply_dataflowgraph.py end-to-end smoke test<br/>文件: governance<br/>/test_apply_dataflowgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_decisiongraph_smoke_py["governance/test_apply_decisiongraph_smoke<br/>test_apply_decisiongraph_smoke.py —<br/>apply_decisiongraph.py end-to-end smoke test<br/>文件: governance<br/>/test_apply_decisiongraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_depgraph_smoke_py["governance/test_apply_depgraph_smoke<br/>test_apply_depgraph_smoke.py —<br/>apply_depgraph.py end-to-end smoke test<br/>文件: governance/test_apply_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_audit_return_contract_usage_py["governance/test_audit_return_contract_usage<br/>test_audit_return_contract_usage.py — 返回契约<br/>ok 键审计脚本单元测试<br/>文件: governance<br/>/test_audit_return_contract_usage.py<br/>(生产态 / production)"]
    tests_governance_test_audit_worktree_ops_telemetry_py["governance/test_audit_worktree_ops_telemetry<br/>test_audit_worktree_ops_telemetry.py —<br/>worktree_ops_log 遥测完整性审计测试<br/>文件: governance<br/>/test_audit_worktree_ops_telemetry.py<br/>(生产态 / production)"]
    tests_governance_test_generate_project_depgraph_smoke_py["governance/test_generate_project_depgraph_smoke<br/>test_generate_project_depgraph_smoke.py —<br/>generate_project_depgraph.py e2e s...<br/>文件: governance<br/>/test_generate_project_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["governance<br/>/test_post_commit_guard_no_verify_threshold<br/>test_post_commit_guard_no_verify_threshold.py —<br/>高基数 --no-verify 阈值阻断 ...<br/>文件: governance<br/>/test_post_commit_guard_no_verify_threshold.py<br/>(生产态 / production)"]
    tests_governance_test_run_silent_failure_regression_py["governance/test_run_silent_failure_regression<br/>test_run_silent_failure_regression.py —<br/>silent-failure 回归 runner 单元测试...<br/>文件: governance<br/>/test_run_silent_failure_regression.py<br/>(生产态 / production)"]
    tests_governance_test_session_startup_health_check_py["governance/test_session_startup_health_check<br/>test_session_startup_health_check.py — AI<br/>session 启动健康度自检单元测试<br/>文件: governance<br/>/test_session_startup_health_check.py<br/>(生产态 / production)"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["governance/test_sync_yaml_to_depgraph_smoke<br/>test_sync_yaml_to_depgraph_smoke.py —<br/>sync_yaml_to_depgraph.py e2e smoke test<br/>文件: governance<br/>/test_sync_yaml_to_depgraph_smoke.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ scripts_governance_d7_code_check_yaml_anchor_consistency_py
    scripts_governance_d7_code_check_yaml_anchor_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py ~~~ src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_manager_py
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_register_py
    src_zephyr_gov_code_quality_code_dedup_canary_register_py ~~~ src_zephyr_gov_code_quality_code_dedup_cli_py
    src_zephyr_gov_code_quality_code_dedup_cli_py ~~~ src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py ~~~ src_zephyr_gov_code_quality_code_dedup_code_simulator_py
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py ~~~ src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_debt_projector_py
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py ~~~ src_zephyr_gov_code_quality_code_dedup_decision_auditor_py
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_degradation_py
    src_zephyr_gov_code_quality_code_dedup_degradation_py ~~~ src_zephyr_gov_code_quality_code_dedup_diff_detector_py
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py ~~~ src_zephyr_gov_code_quality_code_dedup_extraction_safety_py
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py ~~~ src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_file_creator_py
    src_zephyr_gov_code_quality_code_dedup_file_creator_py ~~~ src_zephyr_gov_code_quality_code_dedup_function_discovery_py
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py ~~~ src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_health_monitor_py
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py ~~~ src_zephyr_gov_code_quality_code_dedup_integration_hub_py
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py ~~~ src_zephyr_gov_code_quality_code_dedup_integrations_py
    src_zephyr_gov_code_quality_code_dedup_integrations_py ~~~ src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py ~~~ src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py ~~~ src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py ~~~ src_zephyr_gov_code_quality_code_dedup_path_index_validator_py
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_phase_executor_py
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py ~~~ src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py ~~~ src_zephyr_gov_code_quality_code_dedup_prioritizer_py
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py ~~~ src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py ~~~ src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py ~~~ src_zephyr_gov_code_quality_code_dedup_self_scanner_py
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py ~~~ src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py ~~~ src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py ~~~ src_zephyr_gov_code_quality_code_dedup_shared_evolver_py
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py ~~~ src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_signature_matcher_py
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py ~~~ src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py ~~~ src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py ~~~ src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py ~~~ src_zephyr_gov_code_quality_code_dedup_success_validator_py
    src_zephyr_gov_code_quality_code_dedup_success_validator_py ~~~ src_zephyr_gov_code_quality_code_dedup_symbol_index_py
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py ~~~ src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_init_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_verifier_py
    src_zephyr_gov_code_quality_code_dedup_verifier_py ~~~ src_zephyr_gov_enforcement_commit_gates_init_py
    src_zephyr_gov_enforcement_commit_gates_init_py ~~~ src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_create_guard_py
    src_zephyr_gov_enforcement_commit_gates_create_guard_py ~~~ src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_encoding_gate_py
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_gate_repo_py
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py ~~~ src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_god_class_gate_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_session_required_gate_py
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_ttl_gate_py
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py ~~~ src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py ~~~ tests_data_test_symbol_normalizer_py
    tests_data_test_symbol_normalizer_py ~~~ tests_governance_commit_gates_test_check_yaml_anchor_consistency_py
    tests_governance_commit_gates_test_check_yaml_anchor_consistency_py ~~~ tests_governance_test_apply_dataflowgraph_smoke_py
    tests_governance_test_apply_dataflowgraph_smoke_py ~~~ tests_governance_test_apply_decisiongraph_smoke_py
    tests_governance_test_apply_decisiongraph_smoke_py ~~~ tests_governance_test_apply_depgraph_smoke_py
    tests_governance_test_apply_depgraph_smoke_py ~~~ tests_governance_test_audit_return_contract_usage_py
    tests_governance_test_audit_return_contract_usage_py ~~~ tests_governance_test_audit_worktree_ops_telemetry_py
    tests_governance_test_audit_worktree_ops_telemetry_py ~~~ tests_governance_test_generate_project_depgraph_smoke_py
    tests_governance_test_generate_project_depgraph_smoke_py ~~~ tests_governance_test_post_commit_guard_no_verify_threshold_py
    tests_governance_test_post_commit_guard_no_verify_threshold_py ~~~ tests_governance_test_run_silent_failure_regression_py
    tests_governance_test_run_silent_failure_regression_py ~~~ tests_governance_test_session_startup_health_check_py
    tests_governance_test_session_startup_health_check_py ~~~ tests_governance_test_sync_yaml_to_depgraph_smoke_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py["code_dedup/annotations<br/>共享函数注解引擎 — @shared / @known_dup /<br/>@intentional 三注解.<br/>文件: code_dedup/annotations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["code_dedup/auto_fixer<br/>安全自动修复引擎——五直接开关+五间接约束.<br/>文件: code_dedup/auto_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_config_py["code_dedup/config<br/>配置管理 — 策略树 YAML 加载 + 项目规模感知四<br/>Tier 自适应阈值.<br/>文件: code_dedup/config.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["code_dedup/exit_codes<br/>退出码定义模块——五档exit code<br/>0-4枚举+描述+判定逻辑.<br/>文件: code_dedup/exit_codes.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_report_py["code_dedup/report<br/>报告生成器 — YAML/JSON 输出 + 退出码判定 +<br/>Health Score 聚合.<br/>文件: code_dedup/report.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["trackers/blind_spot_tracker<br/>盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>文件: trackers/blind_spot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["commit_gates/_diff_helpers<br/>_diff_helpers.py — gate 共享 diff 解析工具模块<br/>文件: commit_gates/_diff_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["commit_gates/_reference_helpers<br/>_reference_helpers.py —<br/>引用检测门禁共享工具函数（ARCH-REFERENCE /<br/>RULING-RE...<br/>文件: commit_gates/_reference_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["commit_gates/capability_lookup_bypass_policy<br/>capability_lookup_bypass_policy.py —<br/>CAPABILITY-LOOKUP bypass 策略共享模块<br/>文件: commit_gates<br/>/capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["commit_gates/perm_trigger_gate<br/>perm_trigger_gate.py —<br/>永久系统脚本时间触发模式无事件订阅阻断门禁<br/>（PERM-TRIG...<br/>文件: commit_gates/perm_trigger_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_config_py ~~~ src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py ~~~ src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_report_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py ~~~ src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py ~~~ src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_d3_metadata_check_pure_assertion_py,scripts_governance_d7_code_check_module_id_consistency_py,scripts_governance_d7_code_check_yaml_anchor_consistency_py,src_zephyr_gov_code_quality_init_py,src_zephyr_gov_code_quality_code_dedup_init_py,src_zephyr_gov_code_quality_code_dedup_annotations_py,src_zephyr_gov_code_quality_code_dedup_ast_comparator_py,src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py,src_zephyr_gov_code_quality_code_dedup_auto_fixer_py,src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py,src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py,src_zephyr_gov_code_quality_code_dedup_cache_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_register_py,src_zephyr_gov_code_quality_code_dedup_cli_py,src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py,src_zephyr_gov_code_quality_code_dedup_code_simulator_py,src_zephyr_gov_code_quality_code_dedup_config_py,src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py,src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py,src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py,src_zephyr_gov_code_quality_code_dedup_debt_projector_py,src_zephyr_gov_code_quality_code_dedup_decision_auditor_py,src_zephyr_gov_code_quality_code_dedup_degradation_py,src_zephyr_gov_code_quality_code_dedup_diff_detector_py,src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py,src_zephyr_gov_code_quality_code_dedup_exit_codes_py,src_zephyr_gov_code_quality_code_dedup_extraction_safety_py,src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py,src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py,src_zephyr_gov_code_quality_code_dedup_file_creator_py,src_zephyr_gov_code_quality_code_dedup_function_discovery_py,src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py,src_zephyr_gov_code_quality_code_dedup_health_monitor_py,src_zephyr_gov_code_quality_code_dedup_integration_hub_py,src_zephyr_gov_code_quality_code_dedup_integrations_py,src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py,src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py,src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py,src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py,src_zephyr_gov_code_quality_code_dedup_path_index_validator_py,src_zephyr_gov_code_quality_code_dedup_phase_executor_py,src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py,src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py,src_zephyr_gov_code_quality_code_dedup_prioritizer_py,src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py,src_zephyr_gov_code_quality_code_dedup_report_py,src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py,src_zephyr_gov_code_quality_code_dedup_self_scanner_py,src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py,src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py,src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py,src_zephyr_gov_code_quality_code_dedup_shared_evolver_py,src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py,src_zephyr_gov_code_quality_code_dedup_signature_matcher_py,src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py,src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py,src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py,src_zephyr_gov_code_quality_code_dedup_success_validator_py,src_zephyr_gov_code_quality_code_dedup_symbol_index_py,src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py,src_zephyr_gov_code_quality_code_dedup_trackers_init_py,src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py,src_zephyr_gov_code_quality_code_dedup_verifier_py,src_zephyr_gov_enforcement_commit_gates_init_py,src_zephyr_gov_enforcement_commit_gates_diff_helpers_py,src_zephyr_gov_enforcement_commit_gates_reference_helpers_py,src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py,src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py,src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py,src_zephyr_gov_enforcement_commit_gates_create_guard_py,src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py,src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py,src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py,src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py,src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py,src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py,src_zephyr_gov_enforcement_commit_gates_encoding_gate_py,src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py,src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py,src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py,src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py,src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py,src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py,src_zephyr_gov_enforcement_commit_gates_gate_repo_py,src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py,src_zephyr_gov_enforcement_commit_gates_god_class_gate_py,src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py,src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py,src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py,src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py,src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py,src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py,src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py,src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py,src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py,src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py,src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py,src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py,src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py,src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py,src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py,src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py,src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py,src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py,src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py,src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py,src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_session_required_gate_py,src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py,src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py,src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py,src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py,src_zephyr_gov_enforcement_commit_gates_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py,src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py,src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py,src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py,tests_data_test_symbol_normalizer_py,tests_governance_commit_gates_test_check_yaml_anchor_consistency_py,tests_governance_test_apply_dataflowgraph_smoke_py,tests_governance_test_apply_decisiongraph_smoke_py,tests_governance_test_apply_depgraph_smoke_py,tests_governance_test_audit_return_contract_usage_py,tests_governance_test_audit_worktree_ops_telemetry_py,tests_governance_test_generate_project_depgraph_smoke_py,tests_governance_test_post_commit_guard_no_verify_threshold_py,tests_governance_test_run_silent_failure_regression_py,tests_governance_test_session_startup_health_check_py,tests_governance_test_sync_yaml_to_depgraph_smoke_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 集成协调器 — 24集成+19更新+16GitHub整合. (code_dedup/int... | → | D_AUTONOMY_CORE 自治核心: context/context_rule_registry.py | 导入依赖 / import_depends |
| 2 | capability_consistency_gate.py — Provider 路由-meta 一致... | → | D_DATA 数据接入层: Provider Capability 行为契约校验器（裁定 #ARCH-CH-022）。... | 导入依赖 / import_depends |
| 3 | table_name_registry_gate.py — TABLE-NAME-REGISTRY block ... | → | D_DATA 数据接入层: 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase 2）。 (dat... | 导入依赖 / import_depends |
| 4 | test_symbol_normalizer.py — TRAE-082 symbol 标准化模块测... | → | D_DATA 数据接入层: Symbol 标准化模块——TRAE-082 symbol 约定铁律的实现真源。... | 测试依赖 / test_depends |
| 5 | code-dedup-engine CLI——子命令映射+退出码+扫描入口. (cod... | → | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化告警.... | 导入依赖 / import_depends |
| 6 | capability_overlap_gate.py — 新建 .py 文件 CapabilityLoo... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API + ... | 导入依赖 / import_depends |
| 7 | create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API + ... | 导入依赖 / import_depends |
| 8 | create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式唯一真源 (... | 导入依赖 / import_depends |
| 9 | new_file_depgraph_gate.py — 新建 .py 文件 depgraph 未登... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (governance/depgraph... | 导入依赖 / import_depends |
| 10 | rename_depgraph_sync_gate.py — 文件重命名后 depgraph 未... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (governance/depgraph... | 导入依赖 / import_depends |
| 11 | ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁 ... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API + ... | 导入依赖 / import_depends |
| 12 | test_sync_yaml_to_depgraph_smoke.py — sync_yaml_to_depgr... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (governance/depgraph... | 测试依赖 / test_depends |
| 13 | panorama_alignment_gate.py — 三图模块对齐门禁（四图模块... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 14 | reconciler_health_gate.py — reconciler 健康度门禁（#ARCH... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | 导入依赖 / import_depends |
| 15 | _reference_helpers.py — 引用检测门禁共享工具函数（ARCH-R... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 16 | arch_reference_gate.py — #ARCH-NNN / #ARCH-DOMAIN-NNN 悬... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 17 | asyncio_run_in_context_gate.py — 异步上下文误用硬阻断门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 18 | bare_getenv_gate.py — 裸 os.getenv 读密钥阻断门禁（NO-BA... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 19 | bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BARE-SQL，§5... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 20 | bare_subprocess_gate.py — 裸 subprocess 调用硬阻断门禁（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 21 | blueprint_amodule_consistency_gate.py — [A_module] 头部 ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 22 | blueprint_amodule_cross_check_gate.py — [BLUEPRINT] vs [... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 23 | blueprint_format_gate.py — [BLUEPRINT] 头部 module_id 格... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 24 | capability_consistency_gate.py — Provider 路由-meta 一致... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 25 | capability_lookup_required_gate.py — Capability Lookup ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 26 | capability_overlap_gate.py — 新建 .py 文件 CapabilityLoo... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 27 | ch_batch_size_gate.py — CH 批量写入防回退门禁（CH-BATCH-... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 28 | ch_final_gate.py — ch_writer.query() 直接调用阻断门禁（C... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 29 | ch_version_col_gate.py — CH version 列语义误用阻断门禁（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 30 | claim_required_gate.py — claim_files 前置检查门禁（CLAIM... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 31 | consumers_accuracy_gate.py — CONSUMERS 字段准确性 warn-o... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 32 | create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 33 | dangling_reference_gate.py — AGENTS.md §X.Y 悬空引用自... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 34 | data_task_completeness_gate.py — 数据任务完整性门禁（war... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 35 | datetime_now_forbidden_gate.py — 时间戳约定硬阻断门禁（D... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 36 | depgraph_freshness_gate.py — depgraph 新鲜度门禁（dual-t... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 37 | depgraph_write_path_gate.py — depgraph 写入路径白名单门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 38 | derivation_annotation_gate.py — 派生关系声明真实性校验门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 39 | directory_contract_gate.py — DCR-001~007 等效校验门禁（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 40 | doc_ref_broken_gate.py — 文档相对路径断裂引用阻断门禁（D... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 41 | domain_fk_gate.py — [DOMAIN] 头部域注册表 FK 校验门禁（G... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 42 | domain_name_zh_direct_access_gate.py — DOMAIN_NAME_ZH 字... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 43 | empty_handler_gate.py — 空事件 handler 函数阻断门禁（EMP... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 44 | encoding_gate.py — 编码安全校验门禁（治本：弥补 --no-ver... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 45 | exempt_zone_frontmatter_gate.py — 豁免区 frontmatter 门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 46 | file_copy_gate.py — 新增 .py 文件复制检测阻断门禁（FILE-... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 47 | file_placement_ttl_gate.py — 文件放置与 TTL 一致性门禁（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 48 | folder_capacity_hard_limit_gate.py — 文件夹容量硬上限门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 49 | foreign_change_gate.py — 外来变更检测门禁（FOREIGN-CHANG... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 50 | forged_gw_marker_gate.py — Forged GW Marker 前置检测门禁... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 51 | function_dup_gate.py — 重复函数实现阻断门禁（FUNCTION-DU... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 52 | git_call_budget_gate.py — Git 调用预算 warn-only 门禁（G... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 53 | god_class_gate.py — God Class 阻断门禁（NO-GOD-CLASS，§... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 54 | hardcoded_url_gate.py — 硬编码 localhost URL 阻断门禁（N... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 55 | held_overlap_gate.py — 搭便车防护门禁（HELD-OVERLAP，202... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 56 | high_complexity_gate.py — 高循环复杂度阻断门禁（NO-HIGH-... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 57 | id_uniqueness_gate.py — pre-commit hook ID 唯一性门禁（P... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 58 | import_direction_gate.py — shared 层向上依赖阻断门禁（NO... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 59 | import_integrity_gate.py — IMPORT-INTEGRITY 门禁（悬空 i... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 60 | issue_resolved_integrity_gate.py — ISSUE-RESOLVED-INTEGR... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 61 | long_param_list_gate.py — 长参数列表阻断门禁（NO-LONG-PA... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 62 | manual_only_permanent_gate.py — 永久系统脚本 manual 触发... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 63 | mcp_version_field_gate.py — MCP version 字段缺失硬阻断门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 64 | module_id_consistency_gate.py — module_id 三声明轨道一致... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 65 | msg_exposure_gate.py — 错误消息暴露敏感信息阻断门禁（MSG... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 66 | msg_style_gate.py — 错误消息标点/箭头风格阻断门禁（MSG-S... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 67 | mutable_const_without_final_gate.py — 可变常量缺 Final ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 68 | new_file_depgraph_gate.py — 新建 .py 文件 depgraph 未登... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 69 | no_import_side_effect_gate.py — 模块导入零副作用门禁（NO... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 70 | noqa_validation_gate.py — 自定义 noqa 标记合规性门禁（NO... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 71 | open_without_with_gate.py — open() 未在 with 内硬阻断门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 72 | orphan_module_gate.py — 孤儿模块（无 import 引用）阻断门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 73 | panorama_alignment_gate.py — 三图模块对齐门禁（四图模块... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 74 | perm_trigger_gate.py — 永久系统脚本时间触发模式无事件订... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 75 | precommit_offline_gate.py — pre-commit 配置离线可运行检... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 76 | pure_assertion_gate.py — 纯陈述原则阻断门禁（PURE-ASSERT... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 77 | pure_shim_gate.py — 纯 re-export shim 阻断门禁（PURE-SHI... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 78 | r5_digit_suffix_gate.py — R5 数字后缀目录禁止门禁（治本... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 79 | reconciler_health_gate.py — reconciler 健康度门禁（#ARCH... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 80 | relative_path_literal_gate.py — 相对路径字面量硬阻断门禁... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 81 | rename_depgraph_sync_gate.py — 文件重命名后 depgraph 未... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 82 | rule_execution_pairing_gate.py — 规则-执行配对门禁（RULE... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 83 | rule_four_way_alignment_gate.py — 规则四方对齐门禁（RULE... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 84 | ruling_commit_verified_gate.py — 文档"已完成"声明 commit... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 85 | ruling_reference_gate.py — 裁定#NNN 悬空引用自动检测门禁... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 86 | schema_file_exists_gate.py — SCHEMA-FILE-EXISTS block 门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 87 | scripts_import_integrity_gate.py — _shared.constants 符... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 88 | session_required_gate.py — session 注册强制门禁（SESSION... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 89 | snapshot_drift_gate.py — 运行时违规快照漂移阻断门禁（SNA... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 90 | ssot_redefinition_gate.py — SSoT 符号重复定义硬阻断门禁 ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 91 | table_name_registry_gate.py — TABLE-NAME-REGISTRY block ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 92 | test_source_consistency_gate.py — 测试-源码符号一致性门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 93 | tests_coverage_gate.py — Gate 测试覆盖率校验 meta-gate（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 94 | ttl_gate.py — ttl 字段校验门禁（治本：弥补 --no-verify ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 95 | undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 96 | unsafe_dict_spread_gate.py — ``**data`` 直接展开模式 war... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 97 | vocab_chain_gate.py — SSoT 引用硬编码阻断门禁（VOCAB-CHA... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 98 | vocab_hardcode_gate.py — 新增 .py 文件词表硬编码阻断门禁... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 99 | zephyr_env_direct_access_gate.py — ZEPHYR_ENV 直访硬阻断... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 100 | gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre-commit 门... | 导入依赖 / import_depends |
| 101 | test_audit_worktree_ops_telemetry.py — worktree_ops_log ... | → | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | 测试依赖 / test_depends |
| 102 | check_module_id_consistency.py — module_id 全仓一致性扫... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 (_shared/constants.py) | 导入依赖 / import_depends |
| 103 | 配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应... | → | D_INFRASTRUCTURE 跨层契约基础设施: app_config.py — 应用配置数据类与加载/热重载逻辑 (config/... | 导入依赖 / import_depends |
| 104 | code-dedup-engine CLI——子命令映射+退出码+扫描入口. (cod... | → | D_INFRA_RUNTIME 运行时集成: AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描... | 导入依赖 / import_depends |
| 105 | forged_gw_marker_gate.py — Forged GW Marker 前置检测门禁... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 106 | import_integrity_gate.py — IMPORT-INTEGRITY 门禁（悬空 i... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (access_control/s... | 导入依赖 / import_depends |
| 107 | Stage 0: 函数缓存管理器 — 增量扫描的加速核心. (code_dedu... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 108 | Stage 0: Git diff 变更检测器 — 函数粒度增量. (code_dedup... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 109 | _reference_helpers.py — 引用检测门禁共享工具函数（ARCH-R... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 110 | bare_getenv_gate.py — 裸 os.getenv 读密钥阻断门禁（NO-BA... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 | 盲点 B12... | 导入依赖 / import_depends |
| 111 | blueprint_format_gate.py — [BLUEPRINT] 头部 module_id 格... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 112 | capability_lookup_required_gate.py — Capability Lookup ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 113 | create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 114 | data_task_completeness_gate.py — 数据任务完整性门禁（war... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 115 | encoding_gate.py — 编码安全校验门禁（治本：弥补 --no-ver... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 116 | exempt_zone_frontmatter_gate.py — 豁免区 frontmatter 门... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 117 | gate_repo.py — gates 表持久化仓库（AUDIT-07 P1-5: 从 gat... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 118 | gate_repo.py — gates 表持久化仓库（AUDIT-07 P1-5: 从 gat... | → | D_SHARED 共享服务: db_utils.py — SQLite 连接公共 API（SSoT: zephyr.governan... | 导入依赖 / import_depends |
| 119 | pure_assertion_gate.py — 纯陈述原则阻断门禁（PURE-ASSERT... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 120 | pure_shim_gate.py — 纯 re-export shim 阻断门禁（PURE-SHI... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 121 | r5_digit_suffix_gate.py — R5 数字后缀目录禁止门禁（治本... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 122 | ruling_commit_verified_gate.py — 文档"已完成"声明 commit... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP servers and... | 导入依赖 / import_depends |
| 123 | scripts_import_integrity_gate.py — _shared.constants 符... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 124 | test_source_consistency_gate.py — 测试-源码符号一致性门... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |
| 125 | gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of Truth） (... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化告警.... | → | Stage 2: AST 级精确比对器. (code_dedup/ast_comparator.py) | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化告警.... | → | 行为采样验证器 — Stage 0.25 低成本快速验证. (code_dedup/... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化告警.... | → | 微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合. (cod... | 导入依赖 / import_depends |
| 4 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | _reference_helpers.py — 引用检测门禁共享工具函数（ARCH-R... | 导入依赖 / import_depends |
| 5 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | capability_lookup_bypass_policy.py — CAPABILITY-LOOKUP b... | 导入依赖 / import_depends |
| 6 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | consumers_accuracy_gate.py — CONSUMERS 字段准确性 warn-o... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | scripts_import_integrity_gate.py — _shared.constants 符... | 导入依赖 / import_depends |
| 8 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | undefined_name_gate.py — UNDEFINED-NAME 门禁（F821 未定... | 导入依赖 / import_depends |
| 9 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway post-commi... | → | gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | 导入依赖 / import_depends |
| 10 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口（OPS-2... | → | gate_auto_registrar.py — YAML 驱动的 in-process gate 自... | 导入依赖 / import_depends |
| 11 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | commit_gates — GitCommitGateway pre-commit 门禁实现包。 ... | 导入依赖 / import_depends |
| 12 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | capability_lookup_required_gate.py — Capability Lookup ... | 导入依赖 / import_depends |
| 13 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔离 helper（... | → | test_source_consistency_gate.py — 测试-源码符号一致性门... | 导入依赖 / import_depends |
| 14 | D_GOV_ENFORCEMENT 规则执行: test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-0... | → | create_guard.py — 新建 .py / 非 rules/ .yaml 文件 creati... | 测试依赖 / test_depends |
| 15 | D_GOV_ENFORCEMENT 规则执行: test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX 门禁单元... | → | r5_digit_suffix_gate.py — R5 数字后缀目录禁止门禁（治本... | 测试依赖 / test_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: scan_consumers_accuracy.py — CONSUMERS 字段准确性 baseli... | → | _diff_helpers.py — gate 共享 diff 解析工具模块 (commit_g... | 导入依赖 / import_depends |
| 17 | D_GOV_SCRIPTS 脚本治理: scan_consumers_accuracy.py — CONSUMERS 字段准确性 baseli... | → | consumers_accuracy_gate.py — CONSUMERS 字段准确性 warn-o... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 10 个外部域直接连接（出边 125 条 + 入边 17 条 = 142 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_DATA["D_DATA<br/>数据接入层"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_CODE_QUALITY -->|87条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_CODE_QUALITY -->|19条 导入依赖 / import_depends| D_SHARED
    D_GOV_CODE_QUALITY -->|8条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_CODE_QUALITY -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_GOV_CODE_QUALITY -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_CODE_QUALITY -->|2条 导入依赖 / import_depends| D_SECURITY
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_GOV_SCRIPTS
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT -->|6条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_ENFORCEMENT -->|6条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_SCRIPTS -->|2条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
