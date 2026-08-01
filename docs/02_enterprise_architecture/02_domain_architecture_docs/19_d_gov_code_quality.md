---
doc_type: architecture_view
title: D_GOV_CODE_QUALITY 代码质量治理架构文档
version: "1.0"
status: active
date: 2026-08-01
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
| 模块数 | 169 | Module Count | 169 |
| 域内依赖 | 44 | Internal Dependencies | 44 |
| 跨域入边 | 16 | Cross-domain Incoming | 16 |
| 跨域出边 | 125 | Cross-domain Outgoing | 125 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 169 | Production Modules | 169 |
| 容量 | 169/150 (超容) | Capacity | 169/150 (超容) |
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

> 展示全部 169 个模块（生产态 169 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["(生产态 / production) 检查pureassertion.py — GOV-DOC-016 纯陈 / check_pure_assertion<br/>GOV-DOC-016 纯陈述原则检测真源（SSoT）。<br/>文件: d3_metadata/check_pure_assertion.py"]
    scripts_governance_d7_code_check_module_id_consistency_py["(生产态 / production) 检查模块idconsistency.py — module / check_module_id_consistency<br/>module_id 全仓一致性扫描（--scan-existing 模式）.<br/>文件: d7_code/check_module_id_consistency.py"]
    src_zephyr_gov_code_quality_init_py["(生产态 / production) 包入口 / gov_code_quality domain package — code quality governance (D<br/>包入口。gov_code_quality domain package — code quality governance (D_GOV_CODE_QUALITY).<br/>文件: gov_code_quality/__init__.py"]
    src_zephyr_gov_code_quality_code_dedup_init_py["(生产态 / production) code-dedup-engine 子包 — 重复代码检测与治理引擎. / __init__<br/>code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: code_dedup/__init__.py"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py["(生产态 / production) 共享函数注解引擎 — @shared / @knowndup / @inten / annotations<br/>共享函数注解引擎 — @shared / @known_dup / @intentional 三注解.<br/>文件: code_dedup/annotations.py"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["(生产态 / production) Stage 2: AST 级精确比对器. / ast_comparator<br/>Stage 2: AST 级精确比对器.<br/>文件: code_dedup/ast_comparator.py"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["(生产态 / production) 原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT  / atomic_fixer<br/>原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT -> APPLY -> RECOVER.<br/>文件: code_dedup/atomic_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["(生产态 / production) 行为采样验证器 — Stage 0.25 低成本快速验证. / behavioral_sampler<br/>行为采样验证器 — Stage 0.25 低成本快速验证.<br/>文件: code_dedup/behavioral_sampler.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["(生产态 / production) 行为信任检查器 — 行为漂移DIVERGED检测. / behavioral_trust_checker<br/>行为信任检查器 — 行为漂移DIVERGED检测.<br/>文件: code_dedup/behavioral_trust_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["(生产态 / production) Stage 0: 函数缓存管理器 — 增量扫描的加速核心. / cache_manager<br/>Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>文件: code_dedup/cache_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["(生产态 / production) 金丝雀工厂——生成已知oracle 文件 用于引擎检出+回归测试. / canary_manager<br/>金丝雀工厂——生成已知oracle 文件 用于引擎检出+回归测试.<br/>文件: code_dedup/canary_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["(生产态 / production) 金丝雀注册表维护器 — 注册/过期/腐败检测. / canary_register<br/>金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>文件: code_dedup/canary_register.py"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["(生产态 / production) code-dedup-engine CLI——子命令映射+退出码+扫描入口. / cli<br/>code-dedup-engine CLI——子命令映射+退出码+扫描入口.<br/>文件: code_dedup/cli.py"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["(生产态 / production) 检查运行器——按照敏感基线运行三阶段+导出 yaml 报告. / code_analyzer_runner<br/>检查运行器——按照敏感基线运行三阶段+导出 yaml 报告.<br/>文件: code_dedup/code_analyzer_runner.py"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["(生产态 / production) 代码模拟器——播放录制的克隆演化序列，stress-test AST/basel / code_simulator<br/>代码模拟器——播放录制的克隆演化序列，stress-test AST/baseline归一化.<br/>文件: code_dedup/code_simulator.py"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["(生产态 / production) API契约一致性检查器 — 存在性·行为·契约三维. / contract_consistency_checker<br/>API契约一致性检查器 — 存在性·行为·契约三维.<br/>文件: code_dedup/contract_consistency_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["(生产态 / production) 跨边界克隆感知——四大边界差异化检测+独立策略+跨边界保守autofix规则. / cross_boundary_detector<br/>跨边界克隆感知——四大边界差异化检测+独立策略+跨边界保守auto_fix规则.<br/>文件: code_dedup/cross_boundary_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["(生产态 / production) 死共享模块检测器 — shared/子模块无人使用 -> DEAD. / dead_module_detector<br/>死共享模块检测器 — shared/子模块无人使用 -> DEAD.<br/>文件: code_dedup/dead_module_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["(生产态 / production) 去重债务预测器 — weekstopayoff + intakerate  / debt_projector<br/>去重债务预测器 — weeks_to_payoff + intake_rate vs fix_rate 蒙特卡洛模拟.<br/>文件: code_dedup/debt_projector.py"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["(生产态 / production) 决策审计链 — DecisionFingerprint 不可变追加日志. / decision_auditor<br/>决策审计链 — DecisionFingerprint 不可变追加日志.<br/>文件: code_dedup/decision_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["(生产态 / production) 降级运行管理器 — 各 Stage 独立 try/except + degrad / degradation<br/>降级运行管理器 — 各 Stage 独立 try/except + degradation_level + exit code.<br/>文件: code_dedup/degradation.py"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["(生产态 / production) Stage 0: Git diff 变更检测器 — 函数粒度增量. / diff_detector<br/>Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>文件: code_dedup/diff_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["(生产态 / production) Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机. / doom_loop_guard<br/>Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>文件: code_dedup/doom_loop_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["(生产态 / production) 安全提取适配性评估器 — Suitability Score 0-100 + 不 / extraction_safety<br/>安全提取适配性评估器 — Suitability Score 0-100 + 不安全提取模式检测.<br/>文件: code_dedup/extraction_safety.py"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["(生产态 / production) 三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Samp / false_negative_auditor<br/>三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Sampling.<br/>文件: code_dedup/false_negative_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["(生产态 / production) 15维超综合审计首页 — 逐项证明'做过且做对'. / fifteen_dimension_auditor<br/>15维超综合审计首页 — 逐项证明'做过且做对'.<br/>文件: code_dedup/fifteen_dimension_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["(生产态 / production) 文件创建清单执行器 — 验证所有源/测试/数据文件存在性. / file_creator<br/>文件创建清单执行器 — 验证所有源/测试/数据文件存在性.<br/>文件: code_dedup/file_creator.py"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["(生产态 / production) 共享函数主动发现 — 签名+语义双通道从被动到主动. / function_discovery<br/>共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>文件: code_dedup/function_discovery.py"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["(生产态 / production) Grandfather 三定律 — 古老重复管理. / grandfather_manager<br/>Grandfather 三定律 — 古老重复管理.<br/>文件: code_dedup/grandfather_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["(生产态 / production) 健康仪表盘 — Dedup Health Score 0-100 + 趋势 +  / health_monitor<br/>健康仪表盘 — Dedup Health Score 0-100 + 趋势 + Session Log 写入.<br/>文件: code_dedup/health_monitor.py"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["(生产态 / production) 集成协调器 — 24集成+19更新+16GitHub整合. / integration_hub<br/>集成协调器 — 24集成+19更新+16GitHub整合.<br/>文件: code_dedup/integration_hub.py"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["(生产态 / production) 集成管理——预提交钩子+CI-only 扫描+超时边界. / integrations<br/>集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>文件: code_dedup/integrations.py"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["(生产态 / production) 微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合. / micro_clone_detector<br/>微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合.<br/>文件: code_dedup/micro_clone_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["(生产态 / production) 可控克隆生产器——零假阳性可期待引擎分子离散 / mock_duplicate_generator<br/>可控克隆生产器——零假阳性可期待引擎分子离散<br/>文件: code_dedup/mock_duplicate_generator.py"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["(生产态 / production) Monoculture 免疫 — BRS 0-100 + 去重悖论检测. / monoculture_guard<br/>Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>文件: code_dedup/monoculture_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["(生产态 / production) 提取后稳定观察期守护 — 对标SDP 14天观察. / observation_window_guard<br/>提取后稳定观察期守护 — 对标SDP 14天观察.<br/>文件: code_dedup/observation_window_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["(生产态 / production) 路径索引验证——验证 config 数据集相对路径表与实际文件系统同步. / path_index_validator<br/>路径索引验证——验证 config 数据集相对路径表与实际文件系统同步.<br/>文件: code_dedup/path_index_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["(生产态 / production) 6Phase施工执行器 — Phase 0~5 执行状态追踪. / phase_executor<br/>6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>文件: code_dedup/phase_executor.py"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["(生产态 / production) 策略树自动一致性校验器 — 虚线箭头影响分析. / policy_tree_validator<br/>策略树自动一致性校验器 — 虚线箭头影响分析.<br/>文件: code_dedup/policy_tree_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["(生产态 / production) Pre-Apply 完整性门 — SHA256重新验证. / pre_apply_integrity_gate<br/>Pre-Apply 完整性门 — SHA256重新验证.<br/>文件: code_dedup/pre_apply_integrity_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["(生产态 / production) 修复优先级排序器 — 置信度×Impact×适配性 三因子排序. / prioritizer<br/>修复优先级排序器 — 置信度×Impact×适配性 三因子排序.<br/>文件: code_dedup/prioritizer.py"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["(生产态 / production) Recovery Manifest Writer — R2纯文本base64 M / recovery_manifest_writer<br/>Recovery Manifest Writer — R2纯文本base64 Manifest.<br/>文件: code_dedup/recovery_manifest_writer.py"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["(生产态 / production) R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + mitigation / risk_mitigator<br/>R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + mitigation_tracker.yaml.<br/>文件: code_dedup/risk_mitigator.py"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["(生产态 / production) 引擎自扫描器 — Dogfooding 检测引擎自身源码重复. / self_scanner<br/>引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>文件: code_dedup/self_scanner.py"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["(生产态 / production) 敏感性扫荡——threshold扫描->固化成new baseline（零假阳性 / sensitivity_sweeper<br/>敏感性扫荡——threshold扫描->固化成new baseline（零假阳性+触达率保险）.<br/>文件: code_dedup/sensitivity_sweeper.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["(生产态 / production) 影子信任验证器 — ImportError 防护回路. / shadow_trust_validator<br/>影子信任验证器 — ImportError 防护回路.<br/>文件: code_dedup/shadow_trust_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["(生产态 / production) 影子清单验证器 — size sanity check + semantic验证 / shadow_verifier<br/>影子清单验证器 — size sanity check + semantic验证 + 覆盖度报告.<br/>文件: code_dedup/shadow_verifier.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["(生产态 / production) 共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定. / shared_evolver<br/>共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定.<br/>文件: code_dedup/shared_evolver.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["(生产态 / production) 共享函数生命周期管理 — Active->Deprecated->Grace-> / shared_lifecycle_manager<br/>共享函数生命周期管理 — Active->Deprecated->Grace->Sunset->Retired 五阶段状态机.<br/>文件: code_dedup/shared_lifecycle_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["(生产态 / production) Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配. / signature_matcher<br/>Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配.<br/>文件: code_dedup/signature_matcher.py"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["(生产态 / production) 引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax 报告. / simplicity_auditor<br/>引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax 报告.<br/>文件: code_dedup/simplicity_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["(生产态 / production) SSoT注册器 — 提取函数自动注册到 shared API清单. / ssot_registrar<br/>SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>文件: code_dedup/ssot_registrar.py"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["(生产态 / production) 过时共享函数检测器 — 无caller × 30天 -> STALE标记. / stale_shared_detector<br/>过时共享函数检测器 — 无caller × 30天 -> STALE标记.<br/>文件: code_dedup/stale_shared_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["(生产态 / production) 成功验证——判断一次去重操作是否真正消灭了克隆. / success_validator<br/>成功验证——判断一次去重操作是否真正消灭了克隆.<br/>文件: code_dedup/success_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["(生产态 / production) 符号索引 — 全局函数/类/import映射表. / symbol_index<br/>符号索引 — 全局函数/类/import映射表.<br/>文件: code_dedup/symbol_index.py"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["(生产态 / production) 主题聚类器 — 噪声信号比·告警疲劳缓解. / thematic_clusterer<br/>主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>文件: code_dedup/thematic_clusterer.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["(生产态 / production) tracker 族子包 — 风险/盲点/热点跟踪器集合. / __init__<br/>tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: trackers/__init__.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["(生产态 / production) 盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖. / blind_spot_tracker<br/>盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>文件: trackers/blind_spot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["(生产态 / production) 热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新项目预热清单. / hotspot_tracker<br/>热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新项目预热清单.<br/>文件: trackers/hotspot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["(生产态 / production) Import表面积负债追踪 — SBS 0-100 + shared burde / import_surface_tracker<br/>Import表面积负债追踪 — SBS 0-100 + shared burden score.<br/>文件: trackers/import_surface_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["(生产态 / production) 问题追踪——扫描中发现需要人工处理的问题. / question_tracker<br/>问题追踪——扫描中发现需要人工处理的问题.<br/>文件: trackers/question_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["(生产态 / production) 风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix. / risk_mitigation_tracker<br/>风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix.<br/>文件: trackers/risk_mitigation_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["(生产态 / production) 修复验证器 — import + 类型 + 行为采样验证. / verifier<br/>修复验证器 — import + 类型 + 行为采样验证.<br/>文件: code_dedup/verifier.py"]
    src_zephyr_gov_enforcement_commit_gates_init_py["(生产态 / production) 提交gates — GitCommitGateway pre-comm / __init__<br/>commit_gates — GitCommitGateway pre-commit 门禁实现包。<br/>文件: commit_gates/__init__.py"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["(生产态 / production) 架构referencegate.py — #ARCH-NNN / #AR / arch_reference_gate<br/>#ARCH-NNN / #ARCH-DOMAIN-NNN 悬空引用自动检测门禁<br/>文件: commit_gates/arch_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["(生产态 / production) asyncio运行入上下文gate.py — 异步上下文误用 / asyncio_run_in_context_gate<br/>异步上下文误用硬阻断门禁<br/>文件: commit_gates/asyncio_run_in_context_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["(生产态 / production) baregetenvgate.py — 裸 os.getenv 读密钥阻断门 / bare_getenv_gate<br/>裸 os.getenv 读密钥阻断门禁（NO-BARE-GETENV，§5.17.10 治本）<br/>文件: commit_gates/bare_getenv_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["(生产态 / production) baresqlgate.py — 裸SQL字面量阻断门禁（NO-BARE-S / bare_sql_gate<br/>裸SQL字面量阻断门禁（NO-BARE-SQL，§5.160.2 防复发）<br/>文件: commit_gates/bare_sql_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["(生产态 / production) baresubprocessgate.py — 裸 subprocess 调 / bare_subprocess_gate<br/>裸 subprocess 调用硬阻断门禁<br/>文件: commit_gates/bare_subprocess_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["(生产态 / production) 蓝图amodule一致性gate.py —  / blueprint_amodule_consistency_gate<br/>(A_module) 头部 module_id 格式一致性门禁<br/>文件: commit_gates/blueprint_amodule_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["(生产态 / production) 蓝图amodule跨检查gate.py —  / blueprint_amodule_cross_check_gate<br/>(BLUEPRINT) vs (A_module) 交叉校验门禁<br/>文件: commit_gates/blueprint_amodule_cross_check_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["(生产态 / production) 蓝图formatgate.py — (BLUEPRINT) 头 / blueprint_format_gate<br/>(BLUEPRINT) 头部 module_id 格式阻断门禁（BLUEPRINT-FORMAT，裁定#214 Phase 0 防蔓延）<br/>文件: commit_gates/blueprint_format_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["(生产态 / production) 能力一致性gate.py — Provide / capability_consistency_gate<br/>Provider 路由-meta 一致性门禁（CAP-CONSISTENCY，裁定 #ARCH-CH-022 Phase 4.4）<br/>文件: commit_gates/capability_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["(生产态 / production) 能力lookuprequiredgate.py — Cap / capability_lookup_required_gate<br/>Capability Lookup 强制门禁（CAPABILITY-LOOKUP-REQUIRED，#ARCH-GOV-CONVERGENCE-META Phase<br/>文件: commit_gates/capability_lookup_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["(生产态 / production) 能力overlapgate.py — 新建 .py 文件 C / capability_overlap_gate<br/>新建 .py 文件 CapabilityLookup 提示门禁（warn-only，2026-06-30 治本）<br/>文件: commit_gates/capability_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["(生产态 / production) ch批次大小gate.py — CH 批量写入防回退门禁（CH- / ch_batch_size_gate<br/>CH 批量写入防回退门禁（CH-BATCH-SIZE，§18.4 防复发）<br/>文件: commit_gates/ch_batch_size_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["(生产态 / production) ch最终gate.py — chwriter.query() 直接调 / ch_final_gate<br/>ch_writer.query() 直接调用阻断门禁（CH-FINAL-GATE，裁定 #ARCH-CH-007 B5）<br/>文件: commit_gates/ch_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["(生产态 / production) ch版本colgate.py — CH version 列语义误 / ch_version_col_gate<br/>CH version 列语义误用阻断门禁（CH-VERSION-COL，裁定 #ARCH-CH-009）<br/>文件: commit_gates/ch_version_col_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["(生产态 / production) claimrequiredgate.py — claimfiles 前置检 / claim_required_gate<br/>claim_files 前置检查门禁（CLAIM-REQUIRED，2026-06-30 治本）<br/>文件: commit_gates/claim_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["(生产态 / production) 消费者accuracygate.py — CONSUMERS 字 / consumers_accuracy_gate<br/>CONSUMERS 字段准确性 warn-only 门禁<br/>文件: commit_gates/consumers_accuracy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["(生产态 / production) 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard<br/>新建 .py / 非 rules/ .yaml 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本）<br/>文件: commit_gates/create_guard.py"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["(生产态 / production) dangling_reference_gate.py — AGENTS.md § / dangling_reference_gate<br/>AGENTS.md §X.Y 悬空引用自动检测门禁<br/>文件: commit_gates/dangling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["(生产态 / production) 数据任务completenessgate.py — 数据任务完整性 / data_task_completeness_gate<br/>数据任务完整性门禁（warn 级，提醒型）<br/>文件: commit_gates/data_task_completeness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["(生产态 / production) datetimenowforbiddengate.py — 时间戳约定硬阻 / datetime_now_forbidden_gate<br/>时间戳约定硬阻断门禁<br/>文件: commit_gates/datetime_now_forbidden_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["(生产态 / production) 依赖图freshnessgate.py — depgraph 新鲜 / depgraph_freshness_gate<br/>depgraph 新鲜度门禁（dual-threshold，#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.1）<br/>文件: commit_gates/depgraph_freshness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["(生产态 / production) 依赖图write路径gate.py — depgraph 写 / depgraph_write_path_gate<br/>depgraph 写入路径白名单门禁<br/>文件: commit_gates/depgraph_write_path_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["(生产态 / production) derivationannotationgate.py — 派生关系声明真实 / derivation_annotation_gate<br/>派生关系声明真实性校验门禁<br/>文件: commit_gates/derivation_annotation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["(生产态 / production) directory契约gate.py — DCR-001~007 / directory_contract_gate<br/>DCR-001~007 等效校验门禁（治本：弥补 --no-verify 绕过 pre-commit 的缺口）<br/>文件: commit_gates/directory_contract_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["(生产态 / production) docrefbrokengate.py — 文档相对路径断裂引用阻断门禁（ / doc_ref_broken_gate<br/>文档相对路径断裂引用阻断门禁<br/>文件: commit_gates/doc_ref_broken_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["(生产态 / production) 域fkgate.py — (DOMAIN) 头部域注册表 FK 校 / domain_fk_gate<br/>(DOMAIN) 头部域注册表 FK 校验门禁<br/>文件: commit_gates/domain_fk_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["(生产态 / production) 域namezhdirectaccessgate.py — D / domain_name_zh_direct_access_gate<br/>DOMAIN_NAME_ZH 字典直接访问硬阻断门禁<br/>文件: commit_gates/domain_name_zh_direct_access_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["(生产态 / production) empty处理器gate.py — 空事件 handler 函数阻断 / empty_handler_gate<br/>空事件 handler 函数阻断门禁<br/>文件: commit_gates/empty_handler_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["(生产态 / production) encodinggate.py — 编码安全校验门禁（治本：弥补 --no-v / encoding_gate<br/>编码安全校验门禁（治本：弥补 --no-verify 绕过 pre-commit GATE-ENCODING 的缺口）<br/>文件: commit_gates/encoding_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["(生产态 / production) exemptzonefrontmattergate.py — 豁免区 fr / exempt_zone_frontmatter_gate<br/>豁免区 frontmatter 门禁（Phase 3 reconciler->gate 收敛）<br/>文件: commit_gates/exempt_zone_frontmatter_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["(生产态 / production) 文件copygate.py — 新增 .py 文件复制检测阻断门禁（FI / file_copy_gate<br/>新增 .py 文件复制检测阻断门禁（FILE-COPY，2026-07-03 Phase 1 sub-task 3）<br/>文件: commit_gates/file_copy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["(生产态 / production) 文件placement存活时间gate.py — 文件放置与 TTL 一 / file_placement_ttl_gate<br/>文件放置与 TTL 一致性门禁（治本 #ARCH-049：防止临时文件乱放根目录）<br/>文件: commit_gates/file_placement_ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["(生产态 / production) folder容量hard限制gate.py — 文件夹 / folder_capacity_hard_limit_gate<br/>文件夹容量硬上限门禁<br/>文件: commit_gates/folder_capacity_hard_limit_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["(生产态 / production) foreign变更gate.py — 外来变更检测门禁（FOREIG / foreign_change_gate<br/>外来变更检测门禁（FOREIGN-CHANGE-DETECTION，ARCH-054 治本）<br/>文件: commit_gates/foreign_change_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["(生产态 / production) forged_gw_marker_gate.py — Forged GW Mar / forged_gw_marker_gate<br/>Forged GW Marker 前置检测门禁（FORGED-GW-MARKER，#ARCH-PREVENTABILITY-LAYER-001 Phase 2）<br/>文件: commit_gates/forged_gw_marker_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["(生产态 / production) 函数dupgate.py — 重复函数实现阻断门禁（FUNCTI / function_dup_gate<br/>重复函数实现阻断门禁<br/>文件: commit_gates/function_dup_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["(生产态 / production) 门禁repo.py — gates 表持久化仓库（AUDIT-07 P1- / gate_repo<br/>gates 表持久化仓库（AUDIT-07 P1-5: 从 gate_engine.py 提取）<br/>文件: commit_gates/gate_repo.py"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["(生产态 / production) gitcall预算gate.py — Git 调用预算 warn- / git_call_budget_gate<br/>Git 调用预算 warn-only 门禁（GIT-CALL-BUDGET，§ARCH-GIT-CALL-BUDGET P2.2）<br/>文件: commit_gates/git_call_budget_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["(生产态 / production) god类gate.py — God Class 阻断门禁（NO-GO / god_class_gate<br/>God Class 阻断门禁（NO-GOD-CLASS，§5.150 防复发）<br/>文件: commit_gates/god_class_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["(生产态 / production) hardcodedurlgate.py — 硬编码 localhost UR / hardcoded_url_gate<br/>硬编码 localhost URL 阻断门禁（NO-HARDCODED-URL，§5.160.9 防复发）<br/>文件: commit_gates/hardcoded_url_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["(生产态 / production) heldoverlapgate.py — 搭便车防护门禁（HELD-OVER / held_overlap_gate<br/>搭便车防护门禁（HELD-OVERLAP，2026-06-30 治本）<br/>文件: commit_gates/held_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["(生产态 / production) highcomplexitygate.py — 高循环复杂度阻断门禁（NO- / high_complexity_gate<br/>高循环复杂度阻断门禁（NO-HIGH-COMPLEXITY，§5.158 防复发）<br/>文件: commit_gates/high_complexity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["(生产态 / production) id_uniqueness_gate.py — pre-commit hook  / id_uniqueness_gate<br/>pre-commit hook ID 唯一性门禁（Phase 3 reconciler->gate 收敛）<br/>文件: commit_gates/id_uniqueness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["(生产态 / production) 导入directiongate.py — shared 层向上依赖阻 / import_direction_gate<br/>shared 层向上依赖阻断门禁（NO-UPWARD-IMPORT，§5.152 防复发）<br/>文件: commit_gates/import_direction_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["(生产态 / production) 导入完整性gate.py — IMPORT-INTEGR / import_integrity_gate<br/>IMPORT-INTEGRITY 门禁（悬空 import 硬阻断）<br/>文件: commit_gates/import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["(生产态 / production) issueresolved完整性gate.py — ISSUE / issue_resolved_integrity_gate<br/>ISSUE-RESOLVED-INTEGRITY warn-only 门禁<br/>文件: commit_gates/issue_resolved_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["(生产态 / production) 多param列表gate.py — 长参数列表阻断门禁（NO-L / long_param_list_gate<br/>长参数列表阻断门禁（NO-LONG-PARAM-LIST，§5.150 防复发）<br/>文件: commit_gates/long_param_list_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["(生产态 / production) manualonlypermanentgate.py — 永久系统脚本 m / manual_only_permanent_gate<br/>永久系统脚本 manual 触发无事件订阅阻断门禁（MANUAL-ONLY-PERMANENT，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐<br/>文件: commit_gates/manual_only_permanent_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["(生产态 / production) MCP版本字段gate.py — MCP version  / mcp_version_field_gate<br/>MCP version 字段缺失硬阻断门禁<br/>文件: commit_gates/mcp_version_field_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["(生产态 / production) 模块id一致性gate.py — modulei / module_id_consistency_gate<br/>module_id 三声明轨道一致性 + count 派生 + 跨文件唯一性门禁（Phase 3 reconciler->gate 收敛）<br/>文件: commit_gates/module_id_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["(生产态 / production) msg敞口gate.py — 错误消息暴露敏感信息阻断门禁（MS / msg_exposure_gate<br/>错误消息暴露敏感信息阻断门禁<br/>文件: commit_gates/msg_exposure_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["(生产态 / production) msgstylegate.py — 错误消息标点/箭头风格阻断门禁（MSG- / msg_style_gate<br/>错误消息标点/箭头风格阻断门禁<br/>文件: commit_gates/msg_style_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["(生产态 / production) 可变常量without最终gate.py — 可变 / mutable_const_without_final_gate<br/>可变常量缺 Final 标注硬阻断门禁<br/>文件: commit_gates/mutable_const_without_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["(生产态 / production) 新文件依赖图gate.py — 新建 .py 文件 de / new_file_depgraph_gate<br/>新建 .py 文件 depgraph 未登记硬阻断门禁<br/>文件: commit_gates/new_file_depgraph_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["(生产态 / production) no导入sideeffectgate.py — 模块导入零副作用 / no_import_side_effect_gate<br/>模块导入零副作用门禁<br/>文件: commit_gates/no_import_side_effect_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["(生产态 / production) noqa验证gate.py — 自定义 noqa 标记合规性 / noqa_validation_gate<br/>自定义 noqa 标记合规性门禁（NOQA-VALIDATION，ARCH-NOQA-GOV-001 治本）<br/>文件: commit_gates/noqa_validation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["(生产态 / production) openwithoutwithgate.py — open() 未在 wi / open_without_with_gate<br/>open() 未在 with 内硬阻断门禁<br/>文件: commit_gates/open_without_with_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["(生产态 / production) orphan模块gate.py — 孤儿模块（无 import 引用 / orphan_module_gate<br/>孤儿模块（无 import 引用）阻断门禁<br/>文件: commit_gates/orphan_module_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["(生产态 / production) panoramaalignmentgate.py — 三图模块对齐门禁（四图 / panorama_alignment_gate<br/>三图模块对齐门禁（四图模块对齐 Step 4，ARCH-056 升级）<br/>文件: commit_gates/panorama_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["(生产态 / production) precommit离线gate.py — pre-commit 配 / precommit_offline_gate<br/>pre-commit 配置离线可运行检测门禁<br/>文件: commit_gates/precommit_offline_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["(生产态 / production) pureassertiongate.py — 纯陈述原则阻断门禁（PURE- / pure_assertion_gate<br/>纯陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016 治本）<br/>文件: commit_gates/pure_assertion_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["(生产态 / production) pureshimgate.py — 纯 re-export shim 阻断门 / pure_shim_gate<br/>纯 re-export shim 阻断门禁（PURE-SHIM，P6 治本 2026-07-09）<br/>文件: commit_gates/pure_shim_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["(生产态 / production) r5digitsuffixgate.py — R5 数字后缀目录禁止门禁（ / r5_digit_suffix_gate<br/>R5 数字后缀目录禁止门禁（治本：弥补 --no-verify 绕过 pre-commit 的缺口）<br/>文件: commit_gates/r5_digit_suffix_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["(生产态 / production) 协调器健康gate.py — reconciler 健 / reconciler_health_gate<br/>reconciler 健康度门禁（#ARCH-DATAQUALITY-V1.7）<br/>文件: commit_gates/reconciler_health_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["(生产态 / production) relative路径literalgate.py — 相对路径字面量硬 / relative_path_literal_gate<br/>相对路径字面量硬阻断门禁<br/>文件: commit_gates/relative_path_literal_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["(生产态 / production) rename依赖图同步gate.py — 文件重命名后 de / rename_depgraph_sync_gate<br/>文件重命名后 depgraph 未同步阻断门禁<br/>文件: commit_gates/rename_depgraph_sync_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["(生产态 / production) 规则执行pairinggate.py — 规则-执行配对 / rule_execution_pairing_gate<br/>规则-执行配对门禁（RULE-EXECUTION-PAIRING，Phase 3.5）<br/>文件: commit_gates/rule_execution_pairing_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["(生产态 / production) 规则fourwayalignmentgate.py — 规则四方对齐 / rule_four_way_alignment_gate<br/>规则四方对齐门禁<br/>文件: commit_gates/rule_four_way_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["(生产态 / production) ruling提交verifiedgate.py — 文档'已完成' / ruling_commit_verified_gate<br/>文档'已完成'声明 commit hash 真实性硬验证门禁<br/>文件: commit_gates/ruling_commit_verified_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["(生产态 / production) rulingreferencegate.py — 裁定#NNN 悬空引用自动 / ruling_reference_gate<br/>裁定#NNN 悬空引用自动检测门禁<br/>文件: commit_gates/ruling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["(生产态 / production) 结构文件existsgate.py — SCHEMA-FILE / schema_file_exists_gate<br/>SCHEMA-FILE-EXISTS block 门禁<br/>文件: commit_gates/schema_file_exists_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["(生产态 / production) scripts导入完整性gate.py — shar / scripts_import_integrity_gate<br/>_shared.constants 符号导入完整性门禁<br/>文件: commit_gates/scripts_import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["(生产态 / production) 会话requiredgate.py — session 注册强制门 / session_required_gate<br/>session 注册强制门禁（SESSION-REQUIRED，2026-07-01 治本 FP-ISO.4B 件1改）<br/>文件: commit_gates/session_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["(生产态 / production) 快照漂移gate.py — 运行时违规快照漂移阻断门禁（S / snapshot_drift_gate<br/>运行时违规快照漂移阻断门禁（SNAPSHOT-DRIFT，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc1 enforceability）<br/>文件: commit_gates/snapshot_drift_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["(生产态 / production) ssotredefinitiongate.py — SSoT 符号重复定义硬 / ssot_redefinition_gate<br/>SSoT 符号重复定义硬阻断门禁<br/>文件: commit_gates/ssot_redefinition_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["(生产态 / production) tablename注册表gate.py — TABLE-NAME / table_name_registry_gate<br/>TABLE-NAME-REGISTRY block 门禁<br/>文件: commit_gates/table_name_registry_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["(生产态 / production) 测试源一致性gate.py — 测试-源码符 / test_source_consistency_gate<br/>测试-源码符号一致性门禁（TEST-SOURCE-CONSISTENCY，§5.178 防复发）<br/>文件: commit_gates/test_source_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["(生产态 / production) testscoveragegate.py — Gate 测试覆盖率校验 me / tests_coverage_gate<br/>Gate 测试覆盖率校验 meta-gate（META-TESTS-COVERAGE，#ARCH-057）<br/>文件: commit_gates/tests_coverage_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["(生产态 / production) 存活时间gate.py — ttl 字段校验门禁（治本：弥补 --no-veri / ttl_gate<br/>ttl 字段校验门禁（治本：弥补 --no-verify 绕过 pre-commit GATE-15 的缺口）<br/>文件: commit_gates/ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["(生产态 / production) undefined_name_gate.py — UNDEFINED-NAME  / undefined_name_gate<br/>UNDEFINED-NAME 门禁（F821 未定义符号硬阻断）<br/>文件: commit_gates/undefined_name_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["(生产态 / production) unsafedict价差gate.py — ``**data``  / unsafe_dict_spread_gate<br/>``**data`` 直接展开模式 warn 级门禁<br/>文件: commit_gates/unsafe_dict_spread_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["(生产态 / production) vocab链gate.py — SSoT 引用硬编码阻断门禁（VOC / vocab_chain_gate<br/>SSoT 引用硬编码阻断门禁（VOCAB-CHAIN，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc2 enforceability）<br/>文件: commit_gates/vocab_chain_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["(生产态 / production) vocabhardcodegate.py — 新增 .py 文件词表硬编码阻 / vocab_hardcode_gate<br/>新增 .py 文件词表硬编码阻断门禁（VOCAB-HARDCODE，2026-07-03 Phase 1）<br/>文件: commit_gates/vocab_hardcode_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["(生产态 / production) zephyr环境directaccessgate.py — ZEPHY / zephyr_env_direct_access_gate<br/>ZEPHYR_ENV 直访硬阻断门禁<br/>文件: commit_gates/zephyr_env_direct_access_gate.py"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["(生产态 / production) 门禁自动registrar.py — YAML 驱动的 in-pro / gate_auto_registrar<br/>YAML 驱动的 in-process gate 自动注册器（#ARCH-GATE-REGISTRY-AUTO-001 Phase 3）<br/>文件: rule_bridge/gate_auto_registrar.py"]
    tests_data_test_symbol_normalizer_py["(生产态 / production) 测试symbolnormalizer.py — TRAE-082 sym / test_symbol_normalizer<br/>TRAE-082 symbol 标准化模块测试。<br/>文件: data/test_symbol_normalizer.py"]
    tests_governance_test_apply_dataflowgraph_smoke_py["(生产态 / production) 测试应用dataflowgraphsmoke / test_apply_dataflowgraph_smoke.py — apply_dataflowgraph.py e<br/>测试应用dataflowgraphsmoke。test_apply_dataflowgraph_smoke.py — apply_dataflowgraph.py end-to-end smoke test<br/>文件: governance/test_apply_dataflowgraph_smoke.py"]
    tests_governance_test_apply_decisiongraph_smoke_py["(生产态 / production) 测试应用decisiongraphsmoke / test_apply_decisiongraph_smoke.py — apply_decisiongraph.py e<br/>测试应用decisiongraphsmoke。test_apply_decisiongraph_smoke.py — apply_decisiongraph.py end-to-end smoke test<br/>文件: governance/test_apply_decisiongraph_smoke.py"]
    tests_governance_test_apply_depgraph_smoke_py["(生产态 / production) 测试应用依赖图smoke / test_apply_depgraph_smoke.py — apply_depgraph.py end-to-end <br/>测试应用依赖图smoke。test_apply_depgraph_smoke.py — apply_depgraph.py end-to-end smoke test<br/>文件: governance/test_apply_depgraph_smoke.py"]
    tests_governance_test_audit_return_contract_usage_py["(生产态 / production) 测试审计return契约usage.py — 返回 / test_audit_return_contract_usage<br/>返回契约 ok 键审计脚本单元测试<br/>文件: governance/test_audit_return_contract_usage.py"]
    tests_governance_test_audit_worktree_ops_telemetry_py["(生产态 / production) 测试审计worktree运维telemetry.py — w / test_audit_worktree_ops_telemetry<br/>worktree_ops_log 遥测完整性审计测试<br/>文件: governance/test_audit_worktree_ops_telemetry.py"]
    tests_governance_test_generate_project_depgraph_smoke_py["(生产态 / production) 测试生成project依赖图smoke / test_generate_project_depgraph_smoke.py — generate_project_d<br/>测试生成project依赖图smoke。test_generate_project_depgraph_smoke.py — generate_project_depgraph.py e2e smoke test<br/>文件: governance/test_generate_project_depgraph_smoke.py"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["(生产态 / production) 测试提交提交守卫no验证thresho / test_post_commit_guard_no_verify_threshold<br/>高基数 --no-verify 阈值阻断 e2e 测试<br/>文件: governance/test_post_commit_guard_no_verify_threshold.py"]
    tests_governance_test_run_silent_failure_regression_py["(生产态 / production) 测试运行silentfailureregression.py —  / test_run_silent_failure_regression<br/>silent-failure 回归 runner 单元测试<br/>文件: governance/test_run_silent_failure_regression.py"]
    tests_governance_test_session_startup_health_check_py["(生产态 / production) 测试会话启动健康check.py — A / test_session_startup_health_check<br/>AI session 启动健康度自检单元测试<br/>文件: governance/test_session_startup_health_check.py"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["(生产态 / production) 测试同步yamlto依赖图smoke / test_sync_yaml_to_depgraph_smoke.py — sync_yaml_to_depgraph.<br/>测试同步yamlto依赖图smoke。test_sync_yaml_to_depgraph_smoke.py — sync_yaml_to_depgraph.py e2e smoke test<br/>文件: governance/test_sync_yaml_to_depgraph_smoke.py"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
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
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py
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
    tests_data_test_symbol_normalizer_py ~~~ tests_governance_test_apply_dataflowgraph_smoke_py
    tests_governance_test_apply_dataflowgraph_smoke_py ~~~ tests_governance_test_apply_decisiongraph_smoke_py
    tests_governance_test_apply_decisiongraph_smoke_py ~~~ tests_governance_test_apply_depgraph_smoke_py
    tests_governance_test_apply_depgraph_smoke_py ~~~ tests_governance_test_audit_return_contract_usage_py
    tests_governance_test_audit_return_contract_usage_py ~~~ tests_governance_test_audit_worktree_ops_telemetry_py
    tests_governance_test_audit_worktree_ops_telemetry_py ~~~ tests_governance_test_generate_project_depgraph_smoke_py
    tests_governance_test_generate_project_depgraph_smoke_py ~~~ tests_governance_test_post_commit_guard_no_verify_threshold_py
    tests_governance_test_post_commit_guard_no_verify_threshold_py ~~~ tests_governance_test_run_silent_failure_regression_py
    tests_governance_test_run_silent_failure_regression_py ~~~ tests_governance_test_session_startup_health_check_py
    tests_governance_test_session_startup_health_check_py ~~~ tests_governance_test_sync_yaml_to_depgraph_smoke_py
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["(生产态 / production) 安全自动修复引擎——五直接开关+五间接约束. / auto_fixer<br/>安全自动修复引擎——五直接开关+五间接约束.<br/>文件: code_dedup/auto_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_config_py["(生产态 / production) 配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值. / config<br/>配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值.<br/>文件: code_dedup/config.py"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["(生产态 / production) 退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑. / exit_codes<br/>退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑.<br/>文件: code_dedup/exit_codes.py"]
    src_zephyr_gov_code_quality_code_dedup_report_py["(生产态 / production) 报告生成器 — YAML/JSON 输出 + 退出码判定 + Health Sc / report<br/>报告生成器 — YAML/JSON 输出 + 退出码判定 + Health Score 聚合.<br/>文件: code_dedup/report.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["(生产态 / production) 后果追踪——记录每次修复操作对依赖方的影响. / consequence_tracker<br/>后果追踪——记录每次修复操作对依赖方的影响.<br/>文件: trackers/consequence_tracker.py"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["(生产态 / production) 差异helpers.py — gate 共享 diff 解析工具模块 / _diff_helpers<br/>gate 共享 diff 解析工具模块<br/>文件: commit_gates/_diff_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["(生产态 / production) referencehelpers.py — 引用检测门禁共享工具函数（ARC / _reference_helpers<br/>引用检测门禁共享工具函数<br/>文件: commit_gates/_reference_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["(生产态 / production) 能力lookupbypasspolicy.py — CAP / capability_lookup_bypass_policy<br/>CAPABILITY-LOOKUP bypass 策略共享模块<br/>文件: commit_gates/capability_lookup_bypass_policy.py"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["(生产态 / production) perm触发器gate.py — 永久系统脚本时间触发模式无事件订阅 / perm_trigger_gate<br/>永久系统脚本时间触发模式无事件订阅阻断门禁<br/>文件: commit_gates/perm_trigger_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_config_py ~~~ src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py ~~~ src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_report_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py ~~~ src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py ~~~ src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) 规则执行 / Rule Enforcement<br/>规则执行，负责治理规则执行和门禁拦截<br/>跨域节点 / cross-domain"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    tests_governance_test_audit_worktree_ops_telemetry_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_SCRIPTS["(生产态 / production) 脚本治理 / Script Governance<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>跨域节点 / cross-domain"]
    scripts_governance_d7_code_check_module_id_consistency_py -->|导入依赖 / import_depends| D_GOV_SCRIPTS
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_init_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_create_guard_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_d3_metadata_check_pure_assertion_py,scripts_governance_d7_code_check_module_id_consistency_py,src_zephyr_gov_code_quality_init_py,src_zephyr_gov_code_quality_code_dedup_init_py,src_zephyr_gov_code_quality_code_dedup_annotations_py,src_zephyr_gov_code_quality_code_dedup_ast_comparator_py,src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py,src_zephyr_gov_code_quality_code_dedup_auto_fixer_py,src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py,src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py,src_zephyr_gov_code_quality_code_dedup_cache_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_register_py,src_zephyr_gov_code_quality_code_dedup_cli_py,src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py,src_zephyr_gov_code_quality_code_dedup_code_simulator_py,src_zephyr_gov_code_quality_code_dedup_config_py,src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py,src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py,src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py,src_zephyr_gov_code_quality_code_dedup_debt_projector_py,src_zephyr_gov_code_quality_code_dedup_decision_auditor_py,src_zephyr_gov_code_quality_code_dedup_degradation_py,src_zephyr_gov_code_quality_code_dedup_diff_detector_py,src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py,src_zephyr_gov_code_quality_code_dedup_exit_codes_py,src_zephyr_gov_code_quality_code_dedup_extraction_safety_py,src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py,src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py,src_zephyr_gov_code_quality_code_dedup_file_creator_py,src_zephyr_gov_code_quality_code_dedup_function_discovery_py,src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py,src_zephyr_gov_code_quality_code_dedup_health_monitor_py,src_zephyr_gov_code_quality_code_dedup_integration_hub_py,src_zephyr_gov_code_quality_code_dedup_integrations_py,src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py,src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py,src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py,src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py,src_zephyr_gov_code_quality_code_dedup_path_index_validator_py,src_zephyr_gov_code_quality_code_dedup_phase_executor_py,src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py,src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py,src_zephyr_gov_code_quality_code_dedup_prioritizer_py,src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py,src_zephyr_gov_code_quality_code_dedup_report_py,src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py,src_zephyr_gov_code_quality_code_dedup_self_scanner_py,src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py,src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py,src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py,src_zephyr_gov_code_quality_code_dedup_shared_evolver_py,src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py,src_zephyr_gov_code_quality_code_dedup_signature_matcher_py,src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py,src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py,src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py,src_zephyr_gov_code_quality_code_dedup_success_validator_py,src_zephyr_gov_code_quality_code_dedup_symbol_index_py,src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py,src_zephyr_gov_code_quality_code_dedup_trackers_init_py,src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py,src_zephyr_gov_code_quality_code_dedup_verifier_py,src_zephyr_gov_enforcement_commit_gates_init_py,src_zephyr_gov_enforcement_commit_gates_diff_helpers_py,src_zephyr_gov_enforcement_commit_gates_reference_helpers_py,src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py,src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py,src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py,src_zephyr_gov_enforcement_commit_gates_create_guard_py,src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py,src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py,src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py,src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py,src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py,src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py,src_zephyr_gov_enforcement_commit_gates_encoding_gate_py,src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py,src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py,src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py,src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py,src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py,src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py,src_zephyr_gov_enforcement_commit_gates_gate_repo_py,src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py,src_zephyr_gov_enforcement_commit_gates_god_class_gate_py,src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py,src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py,src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py,src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py,src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py,src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py,src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py,src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py,src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py,src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py,src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py,src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py,src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py,src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py,src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py,src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py,src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py,src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py,src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py,src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py,src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_session_required_gate_py,src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py,src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py,src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py,src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py,src_zephyr_gov_enforcement_commit_gates_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py,src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py,src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py,src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py,tests_data_test_symbol_normalizer_py,tests_governance_test_apply_dataflowgraph_smoke_py,tests_governance_test_apply_decisiongraph_smoke_py,tests_governance_test_apply_depgraph_smoke_py,tests_governance_test_audit_return_contract_usage_py,tests_governance_test_audit_worktree_ops_telemetry_py,tests_governance_test_generate_project_depgraph_smoke_py,tests_governance_test_post_commit_guard_no_verify_threshold_py,tests_governance_test_run_silent_failure_regression_py,tests_governance_test_session_startup_health_check_py,tests_governance_test_sync_yaml_to_depgraph_smoke_py production
    class D_SHARED,D_GOV_ENFORCEMENT,D_GOV_SCRIPTS,D_GOV_AUDIT,D_GOVERNANCE external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 169 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["(生产态 / production) 检查pureassertion.py — GOV-DOC-016 纯陈 / check_pure_assertion<br/>GOV-DOC-016 纯陈述原则检测真源（SSoT）。<br/>文件: d3_metadata/check_pure_assertion.py"]
    scripts_governance_d7_code_check_module_id_consistency_py["(生产态 / production) 检查模块idconsistency.py — module / check_module_id_consistency<br/>module_id 全仓一致性扫描（--scan-existing 模式）.<br/>文件: d7_code/check_module_id_consistency.py"]
    src_zephyr_gov_code_quality_init_py["(生产态 / production) 包入口 / gov_code_quality domain package — code quality governance (D<br/>包入口。gov_code_quality domain package — code quality governance (D_GOV_CODE_QUALITY).<br/>文件: gov_code_quality/__init__.py"]
    src_zephyr_gov_code_quality_code_dedup_init_py["(生产态 / production) code-dedup-engine 子包 — 重复代码检测与治理引擎. / __init__<br/>code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: code_dedup/__init__.py"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py["(生产态 / production) 共享函数注解引擎 — @shared / @knowndup / @inten / annotations<br/>共享函数注解引擎 — @shared / @known_dup / @intentional 三注解.<br/>文件: code_dedup/annotations.py"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["(生产态 / production) Stage 2: AST 级精确比对器. / ast_comparator<br/>Stage 2: AST 级精确比对器.<br/>文件: code_dedup/ast_comparator.py"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["(生产态 / production) 原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT  / atomic_fixer<br/>原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT -> APPLY -> RECOVER.<br/>文件: code_dedup/atomic_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["(生产态 / production) 行为采样验证器 — Stage 0.25 低成本快速验证. / behavioral_sampler<br/>行为采样验证器 — Stage 0.25 低成本快速验证.<br/>文件: code_dedup/behavioral_sampler.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["(生产态 / production) 行为信任检查器 — 行为漂移DIVERGED检测. / behavioral_trust_checker<br/>行为信任检查器 — 行为漂移DIVERGED检测.<br/>文件: code_dedup/behavioral_trust_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["(生产态 / production) Stage 0: 函数缓存管理器 — 增量扫描的加速核心. / cache_manager<br/>Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>文件: code_dedup/cache_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["(生产态 / production) 金丝雀工厂——生成已知oracle 文件 用于引擎检出+回归测试. / canary_manager<br/>金丝雀工厂——生成已知oracle 文件 用于引擎检出+回归测试.<br/>文件: code_dedup/canary_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["(生产态 / production) 金丝雀注册表维护器 — 注册/过期/腐败检测. / canary_register<br/>金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>文件: code_dedup/canary_register.py"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["(生产态 / production) code-dedup-engine CLI——子命令映射+退出码+扫描入口. / cli<br/>code-dedup-engine CLI——子命令映射+退出码+扫描入口.<br/>文件: code_dedup/cli.py"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["(生产态 / production) 检查运行器——按照敏感基线运行三阶段+导出 yaml 报告. / code_analyzer_runner<br/>检查运行器——按照敏感基线运行三阶段+导出 yaml 报告.<br/>文件: code_dedup/code_analyzer_runner.py"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["(生产态 / production) 代码模拟器——播放录制的克隆演化序列，stress-test AST/basel / code_simulator<br/>代码模拟器——播放录制的克隆演化序列，stress-test AST/baseline归一化.<br/>文件: code_dedup/code_simulator.py"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["(生产态 / production) API契约一致性检查器 — 存在性·行为·契约三维. / contract_consistency_checker<br/>API契约一致性检查器 — 存在性·行为·契约三维.<br/>文件: code_dedup/contract_consistency_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["(生产态 / production) 跨边界克隆感知——四大边界差异化检测+独立策略+跨边界保守autofix规则. / cross_boundary_detector<br/>跨边界克隆感知——四大边界差异化检测+独立策略+跨边界保守auto_fix规则.<br/>文件: code_dedup/cross_boundary_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["(生产态 / production) 死共享模块检测器 — shared/子模块无人使用 -> DEAD. / dead_module_detector<br/>死共享模块检测器 — shared/子模块无人使用 -> DEAD.<br/>文件: code_dedup/dead_module_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["(生产态 / production) 去重债务预测器 — weekstopayoff + intakerate  / debt_projector<br/>去重债务预测器 — weeks_to_payoff + intake_rate vs fix_rate 蒙特卡洛模拟.<br/>文件: code_dedup/debt_projector.py"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["(生产态 / production) 决策审计链 — DecisionFingerprint 不可变追加日志. / decision_auditor<br/>决策审计链 — DecisionFingerprint 不可变追加日志.<br/>文件: code_dedup/decision_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["(生产态 / production) 降级运行管理器 — 各 Stage 独立 try/except + degrad / degradation<br/>降级运行管理器 — 各 Stage 独立 try/except + degradation_level + exit code.<br/>文件: code_dedup/degradation.py"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["(生产态 / production) Stage 0: Git diff 变更检测器 — 函数粒度增量. / diff_detector<br/>Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>文件: code_dedup/diff_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["(生产态 / production) Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机. / doom_loop_guard<br/>Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>文件: code_dedup/doom_loop_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["(生产态 / production) 安全提取适配性评估器 — Suitability Score 0-100 + 不 / extraction_safety<br/>安全提取适配性评估器 — Suitability Score 0-100 + 不安全提取模式检测.<br/>文件: code_dedup/extraction_safety.py"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["(生产态 / production) 三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Samp / false_negative_auditor<br/>三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Sampling.<br/>文件: code_dedup/false_negative_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["(生产态 / production) 15维超综合审计首页 — 逐项证明'做过且做对'. / fifteen_dimension_auditor<br/>15维超综合审计首页 — 逐项证明'做过且做对'.<br/>文件: code_dedup/fifteen_dimension_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["(生产态 / production) 文件创建清单执行器 — 验证所有源/测试/数据文件存在性. / file_creator<br/>文件创建清单执行器 — 验证所有源/测试/数据文件存在性.<br/>文件: code_dedup/file_creator.py"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["(生产态 / production) 共享函数主动发现 — 签名+语义双通道从被动到主动. / function_discovery<br/>共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>文件: code_dedup/function_discovery.py"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["(生产态 / production) Grandfather 三定律 — 古老重复管理. / grandfather_manager<br/>Grandfather 三定律 — 古老重复管理.<br/>文件: code_dedup/grandfather_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["(生产态 / production) 健康仪表盘 — Dedup Health Score 0-100 + 趋势 +  / health_monitor<br/>健康仪表盘 — Dedup Health Score 0-100 + 趋势 + Session Log 写入.<br/>文件: code_dedup/health_monitor.py"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["(生产态 / production) 集成协调器 — 24集成+19更新+16GitHub整合. / integration_hub<br/>集成协调器 — 24集成+19更新+16GitHub整合.<br/>文件: code_dedup/integration_hub.py"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["(生产态 / production) 集成管理——预提交钩子+CI-only 扫描+超时边界. / integrations<br/>集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>文件: code_dedup/integrations.py"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["(生产态 / production) 微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合. / micro_clone_detector<br/>微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合.<br/>文件: code_dedup/micro_clone_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["(生产态 / production) 可控克隆生产器——零假阳性可期待引擎分子离散 / mock_duplicate_generator<br/>可控克隆生产器——零假阳性可期待引擎分子离散<br/>文件: code_dedup/mock_duplicate_generator.py"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["(生产态 / production) Monoculture 免疫 — BRS 0-100 + 去重悖论检测. / monoculture_guard<br/>Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>文件: code_dedup/monoculture_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["(生产态 / production) 提取后稳定观察期守护 — 对标SDP 14天观察. / observation_window_guard<br/>提取后稳定观察期守护 — 对标SDP 14天观察.<br/>文件: code_dedup/observation_window_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["(生产态 / production) 路径索引验证——验证 config 数据集相对路径表与实际文件系统同步. / path_index_validator<br/>路径索引验证——验证 config 数据集相对路径表与实际文件系统同步.<br/>文件: code_dedup/path_index_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["(生产态 / production) 6Phase施工执行器 — Phase 0~5 执行状态追踪. / phase_executor<br/>6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>文件: code_dedup/phase_executor.py"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["(生产态 / production) 策略树自动一致性校验器 — 虚线箭头影响分析. / policy_tree_validator<br/>策略树自动一致性校验器 — 虚线箭头影响分析.<br/>文件: code_dedup/policy_tree_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["(生产态 / production) Pre-Apply 完整性门 — SHA256重新验证. / pre_apply_integrity_gate<br/>Pre-Apply 完整性门 — SHA256重新验证.<br/>文件: code_dedup/pre_apply_integrity_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["(生产态 / production) 修复优先级排序器 — 置信度×Impact×适配性 三因子排序. / prioritizer<br/>修复优先级排序器 — 置信度×Impact×适配性 三因子排序.<br/>文件: code_dedup/prioritizer.py"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["(生产态 / production) Recovery Manifest Writer — R2纯文本base64 M / recovery_manifest_writer<br/>Recovery Manifest Writer — R2纯文本base64 Manifest.<br/>文件: code_dedup/recovery_manifest_writer.py"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["(生产态 / production) R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + mitigation / risk_mitigator<br/>R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + mitigation_tracker.yaml.<br/>文件: code_dedup/risk_mitigator.py"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["(生产态 / production) 引擎自扫描器 — Dogfooding 检测引擎自身源码重复. / self_scanner<br/>引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>文件: code_dedup/self_scanner.py"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["(生产态 / production) 敏感性扫荡——threshold扫描->固化成new baseline（零假阳性 / sensitivity_sweeper<br/>敏感性扫荡——threshold扫描->固化成new baseline（零假阳性+触达率保险）.<br/>文件: code_dedup/sensitivity_sweeper.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["(生产态 / production) 影子信任验证器 — ImportError 防护回路. / shadow_trust_validator<br/>影子信任验证器 — ImportError 防护回路.<br/>文件: code_dedup/shadow_trust_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["(生产态 / production) 影子清单验证器 — size sanity check + semantic验证 / shadow_verifier<br/>影子清单验证器 — size sanity check + semantic验证 + 覆盖度报告.<br/>文件: code_dedup/shadow_verifier.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["(生产态 / production) 共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定. / shared_evolver<br/>共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定.<br/>文件: code_dedup/shared_evolver.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["(生产态 / production) 共享函数生命周期管理 — Active->Deprecated->Grace-> / shared_lifecycle_manager<br/>共享函数生命周期管理 — Active->Deprecated->Grace->Sunset->Retired 五阶段状态机.<br/>文件: code_dedup/shared_lifecycle_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["(生产态 / production) Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配. / signature_matcher<br/>Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配.<br/>文件: code_dedup/signature_matcher.py"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["(生产态 / production) 引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax 报告. / simplicity_auditor<br/>引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax 报告.<br/>文件: code_dedup/simplicity_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["(生产态 / production) SSoT注册器 — 提取函数自动注册到 shared API清单. / ssot_registrar<br/>SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>文件: code_dedup/ssot_registrar.py"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["(生产态 / production) 过时共享函数检测器 — 无caller × 30天 -> STALE标记. / stale_shared_detector<br/>过时共享函数检测器 — 无caller × 30天 -> STALE标记.<br/>文件: code_dedup/stale_shared_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["(生产态 / production) 成功验证——判断一次去重操作是否真正消灭了克隆. / success_validator<br/>成功验证——判断一次去重操作是否真正消灭了克隆.<br/>文件: code_dedup/success_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["(生产态 / production) 符号索引 — 全局函数/类/import映射表. / symbol_index<br/>符号索引 — 全局函数/类/import映射表.<br/>文件: code_dedup/symbol_index.py"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["(生产态 / production) 主题聚类器 — 噪声信号比·告警疲劳缓解. / thematic_clusterer<br/>主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>文件: code_dedup/thematic_clusterer.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["(生产态 / production) tracker 族子包 — 风险/盲点/热点跟踪器集合. / __init__<br/>tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: trackers/__init__.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["(生产态 / production) 盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖. / blind_spot_tracker<br/>盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>文件: trackers/blind_spot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["(生产态 / production) 热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新项目预热清单. / hotspot_tracker<br/>热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新项目预热清单.<br/>文件: trackers/hotspot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["(生产态 / production) Import表面积负债追踪 — SBS 0-100 + shared burde / import_surface_tracker<br/>Import表面积负债追踪 — SBS 0-100 + shared burden score.<br/>文件: trackers/import_surface_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["(生产态 / production) 问题追踪——扫描中发现需要人工处理的问题. / question_tracker<br/>问题追踪——扫描中发现需要人工处理的问题.<br/>文件: trackers/question_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["(生产态 / production) 风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix. / risk_mitigation_tracker<br/>风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍未fix.<br/>文件: trackers/risk_mitigation_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["(生产态 / production) 修复验证器 — import + 类型 + 行为采样验证. / verifier<br/>修复验证器 — import + 类型 + 行为采样验证.<br/>文件: code_dedup/verifier.py"]
    src_zephyr_gov_enforcement_commit_gates_init_py["(生产态 / production) 提交gates — GitCommitGateway pre-comm / __init__<br/>commit_gates — GitCommitGateway pre-commit 门禁实现包。<br/>文件: commit_gates/__init__.py"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["(生产态 / production) 架构referencegate.py — #ARCH-NNN / #AR / arch_reference_gate<br/>#ARCH-NNN / #ARCH-DOMAIN-NNN 悬空引用自动检测门禁<br/>文件: commit_gates/arch_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["(生产态 / production) asyncio运行入上下文gate.py — 异步上下文误用 / asyncio_run_in_context_gate<br/>异步上下文误用硬阻断门禁<br/>文件: commit_gates/asyncio_run_in_context_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["(生产态 / production) baregetenvgate.py — 裸 os.getenv 读密钥阻断门 / bare_getenv_gate<br/>裸 os.getenv 读密钥阻断门禁（NO-BARE-GETENV，§5.17.10 治本）<br/>文件: commit_gates/bare_getenv_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["(生产态 / production) baresqlgate.py — 裸SQL字面量阻断门禁（NO-BARE-S / bare_sql_gate<br/>裸SQL字面量阻断门禁（NO-BARE-SQL，§5.160.2 防复发）<br/>文件: commit_gates/bare_sql_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["(生产态 / production) baresubprocessgate.py — 裸 subprocess 调 / bare_subprocess_gate<br/>裸 subprocess 调用硬阻断门禁<br/>文件: commit_gates/bare_subprocess_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["(生产态 / production) 蓝图amodule一致性gate.py —  / blueprint_amodule_consistency_gate<br/>(A_module) 头部 module_id 格式一致性门禁<br/>文件: commit_gates/blueprint_amodule_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["(生产态 / production) 蓝图amodule跨检查gate.py —  / blueprint_amodule_cross_check_gate<br/>(BLUEPRINT) vs (A_module) 交叉校验门禁<br/>文件: commit_gates/blueprint_amodule_cross_check_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["(生产态 / production) 蓝图formatgate.py — (BLUEPRINT) 头 / blueprint_format_gate<br/>(BLUEPRINT) 头部 module_id 格式阻断门禁（BLUEPRINT-FORMAT，裁定#214 Phase 0 防蔓延）<br/>文件: commit_gates/blueprint_format_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["(生产态 / production) 能力一致性gate.py — Provide / capability_consistency_gate<br/>Provider 路由-meta 一致性门禁（CAP-CONSISTENCY，裁定 #ARCH-CH-022 Phase 4.4）<br/>文件: commit_gates/capability_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["(生产态 / production) 能力lookuprequiredgate.py — Cap / capability_lookup_required_gate<br/>Capability Lookup 强制门禁（CAPABILITY-LOOKUP-REQUIRED，#ARCH-GOV-CONVERGENCE-META Phase<br/>文件: commit_gates/capability_lookup_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["(生产态 / production) 能力overlapgate.py — 新建 .py 文件 C / capability_overlap_gate<br/>新建 .py 文件 CapabilityLookup 提示门禁（warn-only，2026-06-30 治本）<br/>文件: commit_gates/capability_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["(生产态 / production) ch批次大小gate.py — CH 批量写入防回退门禁（CH- / ch_batch_size_gate<br/>CH 批量写入防回退门禁（CH-BATCH-SIZE，§18.4 防复发）<br/>文件: commit_gates/ch_batch_size_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["(生产态 / production) ch最终gate.py — chwriter.query() 直接调 / ch_final_gate<br/>ch_writer.query() 直接调用阻断门禁（CH-FINAL-GATE，裁定 #ARCH-CH-007 B5）<br/>文件: commit_gates/ch_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["(生产态 / production) ch版本colgate.py — CH version 列语义误 / ch_version_col_gate<br/>CH version 列语义误用阻断门禁（CH-VERSION-COL，裁定 #ARCH-CH-009）<br/>文件: commit_gates/ch_version_col_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["(生产态 / production) claimrequiredgate.py — claimfiles 前置检 / claim_required_gate<br/>claim_files 前置检查门禁（CLAIM-REQUIRED，2026-06-30 治本）<br/>文件: commit_gates/claim_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["(生产态 / production) 消费者accuracygate.py — CONSUMERS 字 / consumers_accuracy_gate<br/>CONSUMERS 字段准确性 warn-only 门禁<br/>文件: commit_gates/consumers_accuracy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["(生产态 / production) 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard<br/>新建 .py / 非 rules/ .yaml 文件 creation_token 阻断门禁（CREATE-GUARD，2026-06-30 治本）<br/>文件: commit_gates/create_guard.py"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["(生产态 / production) dangling_reference_gate.py — AGENTS.md § / dangling_reference_gate<br/>AGENTS.md §X.Y 悬空引用自动检测门禁<br/>文件: commit_gates/dangling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["(生产态 / production) 数据任务completenessgate.py — 数据任务完整性 / data_task_completeness_gate<br/>数据任务完整性门禁（warn 级，提醒型）<br/>文件: commit_gates/data_task_completeness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["(生产态 / production) datetimenowforbiddengate.py — 时间戳约定硬阻 / datetime_now_forbidden_gate<br/>时间戳约定硬阻断门禁<br/>文件: commit_gates/datetime_now_forbidden_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["(生产态 / production) 依赖图freshnessgate.py — depgraph 新鲜 / depgraph_freshness_gate<br/>depgraph 新鲜度门禁（dual-threshold，#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.1）<br/>文件: commit_gates/depgraph_freshness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["(生产态 / production) 依赖图write路径gate.py — depgraph 写 / depgraph_write_path_gate<br/>depgraph 写入路径白名单门禁<br/>文件: commit_gates/depgraph_write_path_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["(生产态 / production) derivationannotationgate.py — 派生关系声明真实 / derivation_annotation_gate<br/>派生关系声明真实性校验门禁<br/>文件: commit_gates/derivation_annotation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["(生产态 / production) directory契约gate.py — DCR-001~007 / directory_contract_gate<br/>DCR-001~007 等效校验门禁（治本：弥补 --no-verify 绕过 pre-commit 的缺口）<br/>文件: commit_gates/directory_contract_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["(生产态 / production) docrefbrokengate.py — 文档相对路径断裂引用阻断门禁（ / doc_ref_broken_gate<br/>文档相对路径断裂引用阻断门禁<br/>文件: commit_gates/doc_ref_broken_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["(生产态 / production) 域fkgate.py — (DOMAIN) 头部域注册表 FK 校 / domain_fk_gate<br/>(DOMAIN) 头部域注册表 FK 校验门禁<br/>文件: commit_gates/domain_fk_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["(生产态 / production) 域namezhdirectaccessgate.py — D / domain_name_zh_direct_access_gate<br/>DOMAIN_NAME_ZH 字典直接访问硬阻断门禁<br/>文件: commit_gates/domain_name_zh_direct_access_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["(生产态 / production) empty处理器gate.py — 空事件 handler 函数阻断 / empty_handler_gate<br/>空事件 handler 函数阻断门禁<br/>文件: commit_gates/empty_handler_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["(生产态 / production) encodinggate.py — 编码安全校验门禁（治本：弥补 --no-v / encoding_gate<br/>编码安全校验门禁（治本：弥补 --no-verify 绕过 pre-commit GATE-ENCODING 的缺口）<br/>文件: commit_gates/encoding_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["(生产态 / production) exemptzonefrontmattergate.py — 豁免区 fr / exempt_zone_frontmatter_gate<br/>豁免区 frontmatter 门禁（Phase 3 reconciler->gate 收敛）<br/>文件: commit_gates/exempt_zone_frontmatter_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["(生产态 / production) 文件copygate.py — 新增 .py 文件复制检测阻断门禁（FI / file_copy_gate<br/>新增 .py 文件复制检测阻断门禁（FILE-COPY，2026-07-03 Phase 1 sub-task 3）<br/>文件: commit_gates/file_copy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["(生产态 / production) 文件placement存活时间gate.py — 文件放置与 TTL 一 / file_placement_ttl_gate<br/>文件放置与 TTL 一致性门禁（治本 #ARCH-049：防止临时文件乱放根目录）<br/>文件: commit_gates/file_placement_ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["(生产态 / production) folder容量hard限制gate.py — 文件夹 / folder_capacity_hard_limit_gate<br/>文件夹容量硬上限门禁<br/>文件: commit_gates/folder_capacity_hard_limit_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["(生产态 / production) foreign变更gate.py — 外来变更检测门禁（FOREIG / foreign_change_gate<br/>外来变更检测门禁（FOREIGN-CHANGE-DETECTION，ARCH-054 治本）<br/>文件: commit_gates/foreign_change_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["(生产态 / production) forged_gw_marker_gate.py — Forged GW Mar / forged_gw_marker_gate<br/>Forged GW Marker 前置检测门禁（FORGED-GW-MARKER，#ARCH-PREVENTABILITY-LAYER-001 Phase 2）<br/>文件: commit_gates/forged_gw_marker_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["(生产态 / production) 函数dupgate.py — 重复函数实现阻断门禁（FUNCTI / function_dup_gate<br/>重复函数实现阻断门禁<br/>文件: commit_gates/function_dup_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["(生产态 / production) 门禁repo.py — gates 表持久化仓库（AUDIT-07 P1- / gate_repo<br/>gates 表持久化仓库（AUDIT-07 P1-5: 从 gate_engine.py 提取）<br/>文件: commit_gates/gate_repo.py"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["(生产态 / production) gitcall预算gate.py — Git 调用预算 warn- / git_call_budget_gate<br/>Git 调用预算 warn-only 门禁（GIT-CALL-BUDGET，§ARCH-GIT-CALL-BUDGET P2.2）<br/>文件: commit_gates/git_call_budget_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["(生产态 / production) god类gate.py — God Class 阻断门禁（NO-GO / god_class_gate<br/>God Class 阻断门禁（NO-GOD-CLASS，§5.150 防复发）<br/>文件: commit_gates/god_class_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["(生产态 / production) hardcodedurlgate.py — 硬编码 localhost UR / hardcoded_url_gate<br/>硬编码 localhost URL 阻断门禁（NO-HARDCODED-URL，§5.160.9 防复发）<br/>文件: commit_gates/hardcoded_url_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["(生产态 / production) heldoverlapgate.py — 搭便车防护门禁（HELD-OVER / held_overlap_gate<br/>搭便车防护门禁（HELD-OVERLAP，2026-06-30 治本）<br/>文件: commit_gates/held_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["(生产态 / production) highcomplexitygate.py — 高循环复杂度阻断门禁（NO- / high_complexity_gate<br/>高循环复杂度阻断门禁（NO-HIGH-COMPLEXITY，§5.158 防复发）<br/>文件: commit_gates/high_complexity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["(生产态 / production) id_uniqueness_gate.py — pre-commit hook  / id_uniqueness_gate<br/>pre-commit hook ID 唯一性门禁（Phase 3 reconciler->gate 收敛）<br/>文件: commit_gates/id_uniqueness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["(生产态 / production) 导入directiongate.py — shared 层向上依赖阻 / import_direction_gate<br/>shared 层向上依赖阻断门禁（NO-UPWARD-IMPORT，§5.152 防复发）<br/>文件: commit_gates/import_direction_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["(生产态 / production) 导入完整性gate.py — IMPORT-INTEGR / import_integrity_gate<br/>IMPORT-INTEGRITY 门禁（悬空 import 硬阻断）<br/>文件: commit_gates/import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["(生产态 / production) issueresolved完整性gate.py — ISSUE / issue_resolved_integrity_gate<br/>ISSUE-RESOLVED-INTEGRITY warn-only 门禁<br/>文件: commit_gates/issue_resolved_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["(生产态 / production) 多param列表gate.py — 长参数列表阻断门禁（NO-L / long_param_list_gate<br/>长参数列表阻断门禁（NO-LONG-PARAM-LIST，§5.150 防复发）<br/>文件: commit_gates/long_param_list_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["(生产态 / production) manualonlypermanentgate.py — 永久系统脚本 m / manual_only_permanent_gate<br/>永久系统脚本 manual 触发无事件订阅阻断门禁（MANUAL-ONLY-PERMANENT，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐<br/>文件: commit_gates/manual_only_permanent_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["(生产态 / production) MCP版本字段gate.py — MCP version  / mcp_version_field_gate<br/>MCP version 字段缺失硬阻断门禁<br/>文件: commit_gates/mcp_version_field_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["(生产态 / production) 模块id一致性gate.py — modulei / module_id_consistency_gate<br/>module_id 三声明轨道一致性 + count 派生 + 跨文件唯一性门禁（Phase 3 reconciler->gate 收敛）<br/>文件: commit_gates/module_id_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["(生产态 / production) msg敞口gate.py — 错误消息暴露敏感信息阻断门禁（MS / msg_exposure_gate<br/>错误消息暴露敏感信息阻断门禁<br/>文件: commit_gates/msg_exposure_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["(生产态 / production) msgstylegate.py — 错误消息标点/箭头风格阻断门禁（MSG- / msg_style_gate<br/>错误消息标点/箭头风格阻断门禁<br/>文件: commit_gates/msg_style_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["(生产态 / production) 可变常量without最终gate.py — 可变 / mutable_const_without_final_gate<br/>可变常量缺 Final 标注硬阻断门禁<br/>文件: commit_gates/mutable_const_without_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["(生产态 / production) 新文件依赖图gate.py — 新建 .py 文件 de / new_file_depgraph_gate<br/>新建 .py 文件 depgraph 未登记硬阻断门禁<br/>文件: commit_gates/new_file_depgraph_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["(生产态 / production) no导入sideeffectgate.py — 模块导入零副作用 / no_import_side_effect_gate<br/>模块导入零副作用门禁<br/>文件: commit_gates/no_import_side_effect_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["(生产态 / production) noqa验证gate.py — 自定义 noqa 标记合规性 / noqa_validation_gate<br/>自定义 noqa 标记合规性门禁（NOQA-VALIDATION，ARCH-NOQA-GOV-001 治本）<br/>文件: commit_gates/noqa_validation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["(生产态 / production) openwithoutwithgate.py — open() 未在 wi / open_without_with_gate<br/>open() 未在 with 内硬阻断门禁<br/>文件: commit_gates/open_without_with_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["(生产态 / production) orphan模块gate.py — 孤儿模块（无 import 引用 / orphan_module_gate<br/>孤儿模块（无 import 引用）阻断门禁<br/>文件: commit_gates/orphan_module_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["(生产态 / production) panoramaalignmentgate.py — 三图模块对齐门禁（四图 / panorama_alignment_gate<br/>三图模块对齐门禁（四图模块对齐 Step 4，ARCH-056 升级）<br/>文件: commit_gates/panorama_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["(生产态 / production) precommit离线gate.py — pre-commit 配 / precommit_offline_gate<br/>pre-commit 配置离线可运行检测门禁<br/>文件: commit_gates/precommit_offline_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["(生产态 / production) pureassertiongate.py — 纯陈述原则阻断门禁（PURE- / pure_assertion_gate<br/>纯陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016 治本）<br/>文件: commit_gates/pure_assertion_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["(生产态 / production) pureshimgate.py — 纯 re-export shim 阻断门 / pure_shim_gate<br/>纯 re-export shim 阻断门禁（PURE-SHIM，P6 治本 2026-07-09）<br/>文件: commit_gates/pure_shim_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["(生产态 / production) r5digitsuffixgate.py — R5 数字后缀目录禁止门禁（ / r5_digit_suffix_gate<br/>R5 数字后缀目录禁止门禁（治本：弥补 --no-verify 绕过 pre-commit 的缺口）<br/>文件: commit_gates/r5_digit_suffix_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["(生产态 / production) 协调器健康gate.py — reconciler 健 / reconciler_health_gate<br/>reconciler 健康度门禁（#ARCH-DATAQUALITY-V1.7）<br/>文件: commit_gates/reconciler_health_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["(生产态 / production) relative路径literalgate.py — 相对路径字面量硬 / relative_path_literal_gate<br/>相对路径字面量硬阻断门禁<br/>文件: commit_gates/relative_path_literal_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["(生产态 / production) rename依赖图同步gate.py — 文件重命名后 de / rename_depgraph_sync_gate<br/>文件重命名后 depgraph 未同步阻断门禁<br/>文件: commit_gates/rename_depgraph_sync_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["(生产态 / production) 规则执行pairinggate.py — 规则-执行配对 / rule_execution_pairing_gate<br/>规则-执行配对门禁（RULE-EXECUTION-PAIRING，Phase 3.5）<br/>文件: commit_gates/rule_execution_pairing_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["(生产态 / production) 规则fourwayalignmentgate.py — 规则四方对齐 / rule_four_way_alignment_gate<br/>规则四方对齐门禁<br/>文件: commit_gates/rule_four_way_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["(生产态 / production) ruling提交verifiedgate.py — 文档'已完成' / ruling_commit_verified_gate<br/>文档'已完成'声明 commit hash 真实性硬验证门禁<br/>文件: commit_gates/ruling_commit_verified_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["(生产态 / production) rulingreferencegate.py — 裁定#NNN 悬空引用自动 / ruling_reference_gate<br/>裁定#NNN 悬空引用自动检测门禁<br/>文件: commit_gates/ruling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["(生产态 / production) 结构文件existsgate.py — SCHEMA-FILE / schema_file_exists_gate<br/>SCHEMA-FILE-EXISTS block 门禁<br/>文件: commit_gates/schema_file_exists_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["(生产态 / production) scripts导入完整性gate.py — shar / scripts_import_integrity_gate<br/>_shared.constants 符号导入完整性门禁<br/>文件: commit_gates/scripts_import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["(生产态 / production) 会话requiredgate.py — session 注册强制门 / session_required_gate<br/>session 注册强制门禁（SESSION-REQUIRED，2026-07-01 治本 FP-ISO.4B 件1改）<br/>文件: commit_gates/session_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["(生产态 / production) 快照漂移gate.py — 运行时违规快照漂移阻断门禁（S / snapshot_drift_gate<br/>运行时违规快照漂移阻断门禁（SNAPSHOT-DRIFT，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc1 enforceability）<br/>文件: commit_gates/snapshot_drift_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["(生产态 / production) ssotredefinitiongate.py — SSoT 符号重复定义硬 / ssot_redefinition_gate<br/>SSoT 符号重复定义硬阻断门禁<br/>文件: commit_gates/ssot_redefinition_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["(生产态 / production) tablename注册表gate.py — TABLE-NAME / table_name_registry_gate<br/>TABLE-NAME-REGISTRY block 门禁<br/>文件: commit_gates/table_name_registry_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["(生产态 / production) 测试源一致性gate.py — 测试-源码符 / test_source_consistency_gate<br/>测试-源码符号一致性门禁（TEST-SOURCE-CONSISTENCY，§5.178 防复发）<br/>文件: commit_gates/test_source_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["(生产态 / production) testscoveragegate.py — Gate 测试覆盖率校验 me / tests_coverage_gate<br/>Gate 测试覆盖率校验 meta-gate（META-TESTS-COVERAGE，#ARCH-057）<br/>文件: commit_gates/tests_coverage_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["(生产态 / production) 存活时间gate.py — ttl 字段校验门禁（治本：弥补 --no-veri / ttl_gate<br/>ttl 字段校验门禁（治本：弥补 --no-verify 绕过 pre-commit GATE-15 的缺口）<br/>文件: commit_gates/ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["(生产态 / production) undefined_name_gate.py — UNDEFINED-NAME  / undefined_name_gate<br/>UNDEFINED-NAME 门禁（F821 未定义符号硬阻断）<br/>文件: commit_gates/undefined_name_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["(生产态 / production) unsafedict价差gate.py — ``**data``  / unsafe_dict_spread_gate<br/>``**data`` 直接展开模式 warn 级门禁<br/>文件: commit_gates/unsafe_dict_spread_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["(生产态 / production) vocab链gate.py — SSoT 引用硬编码阻断门禁（VOC / vocab_chain_gate<br/>SSoT 引用硬编码阻断门禁（VOCAB-CHAIN，#ARCH-GOV-CONVERGENCE-META Phase 3.6 补齐 rc2 enforceability）<br/>文件: commit_gates/vocab_chain_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["(生产态 / production) vocabhardcodegate.py — 新增 .py 文件词表硬编码阻 / vocab_hardcode_gate<br/>新增 .py 文件词表硬编码阻断门禁（VOCAB-HARDCODE，2026-07-03 Phase 1）<br/>文件: commit_gates/vocab_hardcode_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["(生产态 / production) zephyr环境directaccessgate.py — ZEPHY / zephyr_env_direct_access_gate<br/>ZEPHYR_ENV 直访硬阻断门禁<br/>文件: commit_gates/zephyr_env_direct_access_gate.py"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["(生产态 / production) 门禁自动registrar.py — YAML 驱动的 in-pro / gate_auto_registrar<br/>YAML 驱动的 in-process gate 自动注册器（#ARCH-GATE-REGISTRY-AUTO-001 Phase 3）<br/>文件: rule_bridge/gate_auto_registrar.py"]
    tests_data_test_symbol_normalizer_py["(生产态 / production) 测试symbolnormalizer.py — TRAE-082 sym / test_symbol_normalizer<br/>TRAE-082 symbol 标准化模块测试。<br/>文件: data/test_symbol_normalizer.py"]
    tests_governance_test_apply_dataflowgraph_smoke_py["(生产态 / production) 测试应用dataflowgraphsmoke / test_apply_dataflowgraph_smoke.py — apply_dataflowgraph.py e<br/>测试应用dataflowgraphsmoke。test_apply_dataflowgraph_smoke.py — apply_dataflowgraph.py end-to-end smoke test<br/>文件: governance/test_apply_dataflowgraph_smoke.py"]
    tests_governance_test_apply_decisiongraph_smoke_py["(生产态 / production) 测试应用decisiongraphsmoke / test_apply_decisiongraph_smoke.py — apply_decisiongraph.py e<br/>测试应用decisiongraphsmoke。test_apply_decisiongraph_smoke.py — apply_decisiongraph.py end-to-end smoke test<br/>文件: governance/test_apply_decisiongraph_smoke.py"]
    tests_governance_test_apply_depgraph_smoke_py["(生产态 / production) 测试应用依赖图smoke / test_apply_depgraph_smoke.py — apply_depgraph.py end-to-end <br/>测试应用依赖图smoke。test_apply_depgraph_smoke.py — apply_depgraph.py end-to-end smoke test<br/>文件: governance/test_apply_depgraph_smoke.py"]
    tests_governance_test_audit_return_contract_usage_py["(生产态 / production) 测试审计return契约usage.py — 返回 / test_audit_return_contract_usage<br/>返回契约 ok 键审计脚本单元测试<br/>文件: governance/test_audit_return_contract_usage.py"]
    tests_governance_test_audit_worktree_ops_telemetry_py["(生产态 / production) 测试审计worktree运维telemetry.py — w / test_audit_worktree_ops_telemetry<br/>worktree_ops_log 遥测完整性审计测试<br/>文件: governance/test_audit_worktree_ops_telemetry.py"]
    tests_governance_test_generate_project_depgraph_smoke_py["(生产态 / production) 测试生成project依赖图smoke / test_generate_project_depgraph_smoke.py — generate_project_d<br/>测试生成project依赖图smoke。test_generate_project_depgraph_smoke.py — generate_project_depgraph.py e2e smoke test<br/>文件: governance/test_generate_project_depgraph_smoke.py"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["(生产态 / production) 测试提交提交守卫no验证thresho / test_post_commit_guard_no_verify_threshold<br/>高基数 --no-verify 阈值阻断 e2e 测试<br/>文件: governance/test_post_commit_guard_no_verify_threshold.py"]
    tests_governance_test_run_silent_failure_regression_py["(生产态 / production) 测试运行silentfailureregression.py —  / test_run_silent_failure_regression<br/>silent-failure 回归 runner 单元测试<br/>文件: governance/test_run_silent_failure_regression.py"]
    tests_governance_test_session_startup_health_check_py["(生产态 / production) 测试会话启动健康check.py — A / test_session_startup_health_check<br/>AI session 启动健康度自检单元测试<br/>文件: governance/test_session_startup_health_check.py"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["(生产态 / production) 测试同步yamlto依赖图smoke / test_sync_yaml_to_depgraph_smoke.py — sync_yaml_to_depgraph.<br/>测试同步yamlto依赖图smoke。test_sync_yaml_to_depgraph_smoke.py — sync_yaml_to_depgraph.py e2e smoke test<br/>文件: governance/test_sync_yaml_to_depgraph_smoke.py"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
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
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py
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
    tests_data_test_symbol_normalizer_py ~~~ tests_governance_test_apply_dataflowgraph_smoke_py
    tests_governance_test_apply_dataflowgraph_smoke_py ~~~ tests_governance_test_apply_decisiongraph_smoke_py
    tests_governance_test_apply_decisiongraph_smoke_py ~~~ tests_governance_test_apply_depgraph_smoke_py
    tests_governance_test_apply_depgraph_smoke_py ~~~ tests_governance_test_audit_return_contract_usage_py
    tests_governance_test_audit_return_contract_usage_py ~~~ tests_governance_test_audit_worktree_ops_telemetry_py
    tests_governance_test_audit_worktree_ops_telemetry_py ~~~ tests_governance_test_generate_project_depgraph_smoke_py
    tests_governance_test_generate_project_depgraph_smoke_py ~~~ tests_governance_test_post_commit_guard_no_verify_threshold_py
    tests_governance_test_post_commit_guard_no_verify_threshold_py ~~~ tests_governance_test_run_silent_failure_regression_py
    tests_governance_test_run_silent_failure_regression_py ~~~ tests_governance_test_session_startup_health_check_py
    tests_governance_test_session_startup_health_check_py ~~~ tests_governance_test_sync_yaml_to_depgraph_smoke_py
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["(生产态 / production) 安全自动修复引擎——五直接开关+五间接约束. / auto_fixer<br/>安全自动修复引擎——五直接开关+五间接约束.<br/>文件: code_dedup/auto_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_config_py["(生产态 / production) 配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值. / config<br/>配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应阈值.<br/>文件: code_dedup/config.py"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["(生产态 / production) 退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑. / exit_codes<br/>退出码定义模块——五档exit code 0-4枚举+描述+判定逻辑.<br/>文件: code_dedup/exit_codes.py"]
    src_zephyr_gov_code_quality_code_dedup_report_py["(生产态 / production) 报告生成器 — YAML/JSON 输出 + 退出码判定 + Health Sc / report<br/>报告生成器 — YAML/JSON 输出 + 退出码判定 + Health Score 聚合.<br/>文件: code_dedup/report.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["(生产态 / production) 后果追踪——记录每次修复操作对依赖方的影响. / consequence_tracker<br/>后果追踪——记录每次修复操作对依赖方的影响.<br/>文件: trackers/consequence_tracker.py"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["(生产态 / production) 差异helpers.py — gate 共享 diff 解析工具模块 / _diff_helpers<br/>gate 共享 diff 解析工具模块<br/>文件: commit_gates/_diff_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["(生产态 / production) referencehelpers.py — 引用检测门禁共享工具函数（ARC / _reference_helpers<br/>引用检测门禁共享工具函数<br/>文件: commit_gates/_reference_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["(生产态 / production) 能力lookupbypasspolicy.py — CAP / capability_lookup_bypass_policy<br/>CAPABILITY-LOOKUP bypass 策略共享模块<br/>文件: commit_gates/capability_lookup_bypass_policy.py"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["(生产态 / production) perm触发器gate.py — 永久系统脚本时间触发模式无事件订阅 / perm_trigger_gate<br/>永久系统脚本时间触发模式无事件订阅阻断门禁<br/>文件: commit_gates/perm_trigger_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_config_py ~~~ src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py ~~~ src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_report_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py ~~~ src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py ~~~ src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class scripts_governance_d3_metadata_check_pure_assertion_py,scripts_governance_d7_code_check_module_id_consistency_py,src_zephyr_gov_code_quality_init_py,src_zephyr_gov_code_quality_code_dedup_init_py,src_zephyr_gov_code_quality_code_dedup_annotations_py,src_zephyr_gov_code_quality_code_dedup_ast_comparator_py,src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py,src_zephyr_gov_code_quality_code_dedup_auto_fixer_py,src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py,src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py,src_zephyr_gov_code_quality_code_dedup_cache_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_register_py,src_zephyr_gov_code_quality_code_dedup_cli_py,src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py,src_zephyr_gov_code_quality_code_dedup_code_simulator_py,src_zephyr_gov_code_quality_code_dedup_config_py,src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py,src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py,src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py,src_zephyr_gov_code_quality_code_dedup_debt_projector_py,src_zephyr_gov_code_quality_code_dedup_decision_auditor_py,src_zephyr_gov_code_quality_code_dedup_degradation_py,src_zephyr_gov_code_quality_code_dedup_diff_detector_py,src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py,src_zephyr_gov_code_quality_code_dedup_exit_codes_py,src_zephyr_gov_code_quality_code_dedup_extraction_safety_py,src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py,src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py,src_zephyr_gov_code_quality_code_dedup_file_creator_py,src_zephyr_gov_code_quality_code_dedup_function_discovery_py,src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py,src_zephyr_gov_code_quality_code_dedup_health_monitor_py,src_zephyr_gov_code_quality_code_dedup_integration_hub_py,src_zephyr_gov_code_quality_code_dedup_integrations_py,src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py,src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py,src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py,src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py,src_zephyr_gov_code_quality_code_dedup_path_index_validator_py,src_zephyr_gov_code_quality_code_dedup_phase_executor_py,src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py,src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py,src_zephyr_gov_code_quality_code_dedup_prioritizer_py,src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py,src_zephyr_gov_code_quality_code_dedup_report_py,src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py,src_zephyr_gov_code_quality_code_dedup_self_scanner_py,src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py,src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py,src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py,src_zephyr_gov_code_quality_code_dedup_shared_evolver_py,src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py,src_zephyr_gov_code_quality_code_dedup_signature_matcher_py,src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py,src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py,src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py,src_zephyr_gov_code_quality_code_dedup_success_validator_py,src_zephyr_gov_code_quality_code_dedup_symbol_index_py,src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py,src_zephyr_gov_code_quality_code_dedup_trackers_init_py,src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py,src_zephyr_gov_code_quality_code_dedup_verifier_py,src_zephyr_gov_enforcement_commit_gates_init_py,src_zephyr_gov_enforcement_commit_gates_diff_helpers_py,src_zephyr_gov_enforcement_commit_gates_reference_helpers_py,src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py,src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py,src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py,src_zephyr_gov_enforcement_commit_gates_create_guard_py,src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py,src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py,src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py,src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py,src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py,src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py,src_zephyr_gov_enforcement_commit_gates_encoding_gate_py,src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py,src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py,src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py,src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py,src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py,src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py,src_zephyr_gov_enforcement_commit_gates_gate_repo_py,src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py,src_zephyr_gov_enforcement_commit_gates_god_class_gate_py,src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py,src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py,src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py,src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py,src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py,src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py,src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py,src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py,src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py,src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py,src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py,src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py,src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py,src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py,src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py,src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py,src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py,src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py,src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py,src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py,src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_session_required_gate_py,src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py,src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py,src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py,src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py,src_zephyr_gov_enforcement_commit_gates_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py,src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py,src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py,src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py,tests_data_test_symbol_normalizer_py,tests_governance_test_apply_dataflowgraph_smoke_py,tests_governance_test_apply_decisiongraph_smoke_py,tests_governance_test_apply_depgraph_smoke_py,tests_governance_test_audit_return_contract_usage_py,tests_governance_test_audit_worktree_ops_telemetry_py,tests_governance_test_generate_project_depgraph_smoke_py,tests_governance_test_post_commit_guard_no_verify_threshold_py,tests_governance_test_run_silent_failure_regression_py,tests_governance_test_session_startup_health_check_py,tests_governance_test_sync_yaml_to_depgraph_smoke_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 集成协调器 — 24集成+19更新+16GitHub整合. / integration_h... | → | D_AUTONOMY_CORE 自治核心: 上下文规则注册表 / context_rule_registry (context/context... | 导入依赖 / import_depends |
| 2 | 能力一致性gate.py — Provide / capability_consistency_gat... | → | D_DATA 数据接入层: Provider Capability 行为契约校验器（裁定 #ARCH-CH- / capa... | 导入依赖 / import_depends |
| 3 | tablename注册表gate.py — TABLE-NAME / table_name_registr... | → | D_DATA 数据接入层: 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase 2）。 / ta... | 导入依赖 / import_depends |
| 4 | 测试symbolnormalizer.py — TRAE-082 sym / test_symbol_nor... | → | D_DATA 数据接入层: Symbol 标准化模块——TRAE-082 symbol 约定铁律的实现真源。... | 测试依赖 / test_depends |
| 5 | code-dedup-engine CLI——子命令映射+退出码+扫描入口. / cl... | → | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化 / se... | 导入依赖 / import_depends |
| 6 | 能力overlapgate.py — 新建 .py 文件 C / capability_overla... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API  /... | 导入依赖 / import_depends |
| 7 | 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard ... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API  /... | 导入依赖 / import_depends |
| 8 | 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard ... | → | D_GOVERNANCE 生命周期管理: 规则patterns.py — 治理规则正则 + 安全审计模式唯一真源 ( ... | 导入依赖 / import_depends |
| 9 | 新文件依赖图gate.py — 新建 .py 文件 de / new_file_depgra... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 / depgraph_schema (g... | 导入依赖 / import_depends |
| 10 | rename依赖图同步gate.py — 文件重命名后 de / rename_depgr... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 / depgraph_schema (g... | 导入依赖 / import_depends |
| 11 | ssotredefinitiongate.py — SSoT 符号重复定义硬 / ssot_red... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的查询 API  /... | 导入依赖 / import_depends |
| 12 | 测试同步yamlto依赖图smoke / test_sync_yaml_to_depgraph_sm... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 / depgraph_schema (g... | 测试依赖 / test_depends |
| 13 | panoramaalignmentgate.py — 三图模块对齐门禁（四图 / pano... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | 导入依赖 / import_depends |
| 14 | 协调器健康gate.py — reconciler 健 / reconciler_health_ga... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | 导入依赖 / import_depends |
| 15 | referencehelpers.py — 引用检测门禁共享工具函数（ARC / _r... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 16 | 架构referencegate.py — #ARCH-NNN / #AR / arch_reference_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 17 | asyncio运行入上下文gate.py — 异步上下文误用 / asyncio_ru... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 18 | baregetenvgate.py — 裸 os.getenv 读密钥阻断门 / bare_get... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 19 | baresqlgate.py — 裸SQL字面量阻断门禁（NO-BARE-S / bare_s... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 20 | baresubprocessgate.py — 裸 subprocess 调 / bare_subproce... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 21 | 蓝图amodule一致性gate.py —  / blueprint_amodule_consiste... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 22 | 蓝图amodule跨检查gate.py —  / blueprint_amodule_cross_ch... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 23 | 蓝图formatgate.py — [BLUEPRINT] 头 / blueprint_format_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 24 | 能力一致性gate.py — Provide / capability_consistency_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 25 | 能力lookuprequiredgate.py — Cap / capability_lookup_requ... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 26 | 能力overlapgate.py — 新建 .py 文件 C / capability_overla... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 27 | ch批次大小gate.py — CH 批量写入防回退门禁（CH- / ch_batc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 28 | ch最终gate.py — chwriter.query() 直接调 / ch_final_gate ... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 29 | ch版本colgate.py — CH version 列语义误 / ch_version_col_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 30 | claimrequiredgate.py — claimfiles 前置检 / claim_require... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 31 | 消费者accuracygate.py — CONSUMERS 字 / consumers_accurac... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 32 | 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard ... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 33 | dangling_reference_gate.py — AGENTS.md § / dangling_ref... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 34 | 数据任务completenessgate.py — 数据任务完整性 / data_task... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 35 | datetimenowforbiddengate.py — 时间戳约定硬阻 / datetime_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 36 | 依赖图freshnessgate.py — depgraph 新鲜 / depgraph_freshn... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 37 | 依赖图write路径gate.py — depgraph 写 / depgraph_write_pa... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 38 | derivationannotationgate.py — 派生关系声明真实 / derivat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 39 | directory契约gate.py — DCR-001~007 / directory_contract_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 40 | docrefbrokengate.py — 文档相对路径断裂引用阻断门禁（ / d... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 41 | 域fkgate.py — [DOMAIN] 头部域注册表 FK 校 / domain_fk_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 42 | 域namezhdirectaccessgate.py — D / domain_name_zh_direct_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 43 | empty处理器gate.py — 空事件 handler 函数阻断 / empty_han... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 44 | encodinggate.py — 编码安全校验门禁（治本：弥补 --no-v / ... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 45 | exemptzonefrontmattergate.py — 豁免区 fr / exempt_zone_f... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 46 | 文件copygate.py — 新增 .py 文件复制检测阻断门禁（FI / fi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 47 | 文件placement存活时间gate.py — 文件放置与 TTL 一 / file_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 48 | folder容量hard限制gate.py — 文件夹 / folder_capacity_har... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 49 | foreign变更gate.py — 外来变更检测门禁（FOREIG / foreign_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 50 | forged_gw_marker_gate.py — Forged GW Mar / forged_gw_mar... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 51 | 函数dupgate.py — 重复函数实现阻断门禁（FUNCTI / function... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 52 | gitcall预算gate.py — Git 调用预算 warn- / git_call_budge... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 53 | god类gate.py — God Class 阻断门禁（NO-GO / god_class_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 54 | hardcodedurlgate.py — 硬编码 localhost UR / hardcoded_ur... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 55 | heldoverlapgate.py — 搭便车防护门禁（HELD-OVER / held_ov... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 56 | highcomplexitygate.py — 高循环复杂度阻断门禁（NO- / high... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 57 | id_uniqueness_gate.py — pre-commit hook  / id_uniqueness... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 58 | 导入directiongate.py — shared 层向上依赖阻 / import_dire... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 59 | 导入完整性gate.py — IMPORT-INTEGR / import_integrity_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 60 | issueresolved完整性gate.py — ISSUE / issue_resolved_inte... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 61 | 多param列表gate.py — 长参数列表阻断门禁（NO-L / long_par... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 62 | manualonlypermanentgate.py — 永久系统脚本 m / manual_onl... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 63 | MCP版本字段gate.py — MCP version  / mcp_version_field_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 64 | 模块id一致性gate.py — modulei / module_id_consistency_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 65 | msg敞口gate.py — 错误消息暴露敏感信息阻断门禁（MS / msg_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 66 | msgstylegate.py — 错误消息标点/箭头风格阻断门禁（MSG- / ... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 67 | 可变常量without最终gate.py — 可变 / mutable_const_withou... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 68 | 新文件依赖图gate.py — 新建 .py 文件 de / new_file_depgra... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 69 | no导入sideeffectgate.py — 模块导入零副作用 / no_import_s... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 70 | noqa验证gate.py — 自定义 noqa 标记合规性 / noqa_validati... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 71 | openwithoutwithgate.py — open() 未在 wi / open_without_w... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 72 | orphan模块gate.py — 孤儿模块（无 import 引用 / orphan_mo... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 73 | panoramaalignmentgate.py — 三图模块对齐门禁（四图 / pano... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 74 | perm触发器gate.py — 永久系统脚本时间触发模式无事件订阅 /... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 75 | precommit离线gate.py — pre-commit 配 / precommit_offline... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 76 | pureassertiongate.py — 纯陈述原则阻断门禁（PURE- / pure_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 77 | pureshimgate.py — 纯 re-export shim 阻断门 / pure_shim_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 78 | r5digitsuffixgate.py — R5 数字后缀目录禁止门禁（ / r5_di... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 79 | 协调器健康gate.py — reconciler 健 / reconciler_health_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 80 | relative路径literalgate.py — 相对路径字面量硬 / relative... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 81 | rename依赖图同步gate.py — 文件重命名后 de / rename_depgr... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 82 | 规则执行pairinggate.py — 规则-执行配对 / rule_execution_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 83 | 规则fourwayalignmentgate.py — 规则四方对齐 / rule_four_w... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 84 | ruling提交verifiedgate.py — 文档"已完成" / ruling_commit... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 85 | rulingreferencegate.py — 裁定#NNN 悬空引用自动 / ruling_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 86 | 结构文件existsgate.py — SCHEMA-FILE / schema_file_exists... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 87 | scripts导入完整性gate.py — shar / scripts_import_integri... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 88 | 会话requiredgate.py — session 注册强制门 / session_requi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 89 | 快照漂移gate.py — 运行时违规快照漂移阻断门禁（S / snapsh... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 90 | ssotredefinitiongate.py — SSoT 符号重复定义硬 / ssot_red... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 91 | tablename注册表gate.py — TABLE-NAME / table_name_registr... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 92 | 测试源一致性gate.py — 测试-源码符 / test_source_consiste... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 93 | testscoveragegate.py — Gate 测试覆盖率校验 me / tests_co... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 94 | 存活时间gate.py — ttl 字段校验门禁（治本：弥补 --no-veri... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 95 | undefined_name_gate.py — UNDEFINED-NAME  / undefined_nam... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 96 | unsafedict价差gate.py — ``**data``  / unsafe_dict_spread... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 97 | vocab链gate.py — SSoT 引用硬编码阻断门禁（VOC / vocab_ch... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 98 | vocabhardcodegate.py — 新增 .py 文件词表硬编码阻 / vocab... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 99 | zephyr环境directaccessgate.py — ZEPHY / zephyr_env_direc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 100 | 门禁自动registrar.py — YAML 驱动的 in-pro / gate_auto_re... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁registry.py — GitCommitGatew / commit_gate_regis... | 导入依赖 / import_depends |
| 101 | 测试审计worktree运维telemetry.py — w / test_audit_worktr... | → | D_GOV_ENFORCEMENT 规则执行: 会话worktree.py — AI 对话 worktree 物理隔 / session_work... | 测试依赖 / test_depends |
| 102 | 检查模块idconsistency.py — module / check_module_id_cons... | → | D_GOV_SCRIPTS 脚本治理: constants.py — 审计脚本共享常量 / constants (_shared/con... | 导入依赖 / import_depends |
| 103 | 配置管理 — 策略树 YAML 加载 + 项目规模感知四 Tier 自适应... | → | D_INFRASTRUCTURE 跨层契约基础设施: appconfig.py — 应用配置数据类与加载/热重载逻辑 / app_con... | 导入依赖 / import_depends |
| 104 | code-dedup-engine CLI——子命令映射+退出码+扫描入口. / cl... | → | D_INFRA_RUNTIME 运行时集成: AssetDiscoveryScanner — MOD-INF-026 L1 全 / scanner (ass... | 导入依赖 / import_depends |
| 105 | forged_gw_marker_gate.py — Forged GW Mar / forged_gw_mar... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 / session_concurr... | 导入依赖 / import_depends |
| 106 | 导入完整性gate.py — IMPORT-INTEGR / import_integrity_gat... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 / session_concurr... | 导入依赖 / import_depends |
| 107 | Stage 0: 函数缓存管理器 — 增量扫描的加速核心. / cache_ma... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 108 | Stage 0: Git diff 变更检测器 — 函数粒度增量. / diff_dete... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 109 | referencehelpers.py — 引用检测门禁共享工具函数（ARC / _r... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 110 | baregetenvgate.py — 裸 os.getenv 读密钥阻断门 / bare_get... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 |  / secre... | 导入依赖 / import_depends |
| 111 | 蓝图formatgate.py — [BLUEPRINT] 头 / blueprint_format_ga... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 112 | 能力lookuprequiredgate.py — Cap / capability_lookup_requ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 113 | 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 114 | 数据任务completenessgate.py — 数据任务完整性 / data_task... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 115 | encodinggate.py — 编码安全校验门禁（治本：弥补 --no-v / ... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 116 | exemptzonefrontmattergate.py — 豁免区 fr / exempt_zone_f... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 117 | 门禁repo.py — gates 表持久化仓库（AUDIT-07 P1- / gate_re... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 118 | 门禁repo.py — gates 表持久化仓库（AUDIT-07 P1- / gate_re... | → | D_SHARED 共享服务: 数据库utils.py — SQLite 连接公共 API（SSoT: zeph / db_ut... | 导入依赖 / import_depends |
| 119 | pureassertiongate.py — 纯陈述原则阻断门禁（PURE- / pure_... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 120 | pureshimgate.py — 纯 re-export shim 阻断门 / pure_shim_g... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 121 | r5digitsuffixgate.py — R5 数字后缀目录禁止门禁（ / r5_di... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 122 | ruling提交verifiedgate.py — 文档"已完成" / ruling_commit... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 123 | scripts导入完整性gate.py — shar / scripts_import_integri... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 124 | 测试源一致性gate.py — 测试-源码符 / test_source_consiste... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 125 | 门禁自动registrar.py — YAML 驱动的 in-pro / gate_auto_re... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化 / se... | → | Stage 2: AST 级精确比对器. / ast_comparator (code_dedup/a... | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化 / se... | → | 行为采样验证器 — Stage 0.25 低成本快速验证. / behavioral... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引擎退化 / se... | → | 微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合. / mi... | 导入依赖 / import_depends |
| 4 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | → | 能力lookupbypasspolicy.py — CAP / capability_lookup_bypa... | 导入依赖 / import_depends |
| 5 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | → | 消费者accuracygate.py — CONSUMERS 字 / consumers_accurac... | 导入依赖 / import_depends |
| 6 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | → | scripts导入完整性gate.py — shar / scripts_import_integri... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | → | undefined_name_gate.py — UNDEFINED-NAME  / undefined_nam... | 导入依赖 / import_depends |
| 8 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGa / reconciliatio... | → | 门禁自动registrar.py — YAML 驱动的 in-pro / gate_auto_re... | 导入依赖 / import_depends |
| 9 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit 入口 / git_... | → | 门禁自动registrar.py — YAML 驱动的 in-pro / gate_auto_re... | 导入依赖 / import_depends |
| 10 | D_GOV_ENFORCEMENT 规则执行: 会话worktree.py — AI 对话 worktree 物理隔 / session_work... | → | 提交gates — GitCommitGateway pre-comm / __init__ (commit... | 导入依赖 / import_depends |
| 11 | D_GOV_ENFORCEMENT 规则执行: 会话worktree.py — AI 对话 worktree 物理隔 / session_work... | → | 能力lookuprequiredgate.py — Cap / capability_lookup_requ... | 导入依赖 / import_depends |
| 12 | D_GOV_ENFORCEMENT 规则执行: 会话worktree.py — AI 对话 worktree 物理隔 / session_work... | → | 测试源一致性gate.py — 测试-源码符 / test_source_consiste... | 导入依赖 / import_depends |
| 13 | D_GOV_ENFORCEMENT 规则执行: 测试创建guard.py — CREATE-GUARD 门禁单元 / test_create_g... | → | 创建guard.py — 新建 .py / 非 rules/ .yam / create_guard ... | 测试依赖 / test_depends |
| 14 | D_GOV_ENFORCEMENT 规则执行: 测试r5digitsuffixgate.py — R5-DIGIT- / test_r5_digit_suf... | → | r5digitsuffixgate.py — R5 数字后缀目录禁止门禁（ / r5_di... | 测试依赖 / test_depends |
| 15 | D_GOV_SCRIPTS 脚本治理: 扫描消费者accuracy.py — CONSUMERS 字 / scan_consumers_ac... | → | 差异helpers.py — gate 共享 diff 解析工具模块 / _diff_hel... | 导入依赖 / import_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: 扫描消费者accuracy.py — CONSUMERS 字 / scan_consumers_ac... | → | 消费者accuracygate.py — CONSUMERS 字 / consumers_accurac... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 10 个外部域直接连接（出边 125 条 + 入边 16 条 = 141 条）。只显示直接连接的域，不展开具体节点。

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
    D_GOV_ENFORCEMENT -->|6条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_CODE_QUALITY
    D_GOV_AUDIT -->|5条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
    D_GOV_SCRIPTS -->|2条 导入依赖 / import_depends| D_GOV_CODE_QUALITY
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
