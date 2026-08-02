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
    scripts_governance_d3_metadata_check_pure_assertion_py["检查pureassertion<br/>GOV-DOC-016 纯陈述原则检测真源（SSoT）。<br/>check_pure_assertion<br/>文件: d3_metadata/check_pure_assertion.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_module_id_consistency_py["检查模块id一致性<br/>module_id 全仓一致性扫描（--scan-existing<br/>模式）.<br/>check_module_id_consistency<br/>文件: d7_code/check_module_id_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_yaml_anchor_consistency_py["d7_code/check_yaml_anchor_consistency<br/>check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描.<br/>文件: d7_code/check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_init_py["zephyr/gov_code_quality 包入口<br/>包入口。gov_code_quality domain package — code<br/>quality governance (D_GOV_CODE_QUALITY).<br/>文件: gov_code_quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_init_py["gov_code_quality/code_dedup 包入口<br/>code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: code_dedup/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py["共享函数注解引擎 — @shared / @knowndup / @inten<br/>共享函数注解引擎 — @shared / @known_dup /<br/>@intentional 三注解.<br/>annotations<br/>文件: code_dedup/annotations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["ast比较器<br/>- AST 子树归一化哈希<br/>ast_comparator<br/>文件: code_dedup/ast_comparator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT<br/>> APPLY -> RECOVER<br/>atomic_fixer<br/>文件: code_dedup/atomic_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["behavioral采样器<br/>行为采样验证器 — Stage 0.25 低成本快速验证.<br/>behavioral_sampler<br/>文件: code_dedup/behavioral_sampler.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["行为信任检查器 — 行为漂移DIVERGED检测.<br/>行为正确性检查.<br/>behavioral_trust_checker<br/>文件: code_dedup/behavioral_trust_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["金丝雀管理器<br/>金丝雀工厂——生成已知oracle 文件<br/>用于引擎检出+回归测试.<br/>canary_manager<br/>文件: code_dedup/canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>金丝雀函数注册表.<br/>canary_register<br/>文件: code_dedup/canary_register.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["code_dedup/cli<br/>code-dedup-engine<br/>CLI——子命令映射+退出码+扫描入口.<br/>文件: code_dedup/cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["代码分析器运行器<br/>检查运行器——按照敏感基线运行三阶段+导出 yaml<br/>报告.<br/>code_analyzer_runner<br/>文件: code_dedup/code_analyzer_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["代码模拟器<br/>播放录制的克隆演化序列，stress-test AST<br/>/baseline归一化<br/>code_simulator<br/>文件: code_dedup/code_simulator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["API契约一致性检查器 — 存在性·行为·契约三维.<br/>三维API契约检查.<br/>contract_consistency_checker<br/>文件: code_dedup/contract_consistency_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["跨boundary检测器<br/>跨边界克隆感知——四大边界差异化检测+独立策略+跨边<br/>界保守auto_fix规则.<br/>cross_boundary_detector<br/>文件: code_dedup/cross_boundary_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["deadmodule检测器<br/>死共享模块检测器 — shared/子模块无人使用 -><br/>DEAD.<br/>dead_module_detector<br/>文件: code_dedup/dead_module_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["debt投影器<br/>去重债务预测器 — weeks_to_payoff + intake_rate<br/>vs fix_rate 蒙特卡洛模拟.<br/>debt_projector<br/>文件: code_dedup/debt_projector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["决策审计器<br/>决策审计链 — DecisionFingerprint 不可变追加日志.<br/>decision_auditor<br/>文件: code_dedup/decision_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["退化<br/>降级运行管理器 — 各 Stage 独立 try/except +<br/>degradation_level + exit code.<br/>文件: code_dedup/degradation.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["差异检测器<br/>Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>diff_detector<br/>文件: code_dedup/diff_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["doom循环守卫<br/>Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>doom_loop_guard<br/>文件: code_dedup/doom_loop_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["extraction安全<br/>安全提取适配性评估器 — Suitability Score 0-100<br/>+ 不安全提取模式检测.<br/>extraction_safety<br/>文件: code_dedup/extraction_safety.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["falsenegative审计器<br/>- L1 Sweep：增量扫描漏过的去重对（全量 vs 增量<br/>diff）<br/>false_negative_auditor<br/>文件: code_dedup/false_negative_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["15维超综合审计首页 — 逐项证明'做过且做对'.<br/>- 15维审计刹车：每一项给出 PASS/FAIL/WAIVED +<br/>证据<br/>fifteen_dimension_auditor<br/>文件: code_dedup/fifteen_dimension_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["文件创建清单执行器 — 验证所有源/测试<br/>/数据文件存在性.<br/>文件创建清单验证器.<br/>file_creator<br/>文件: code_dedup/file_creator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>主动发现未注册的共享函数.<br/>function_discovery<br/>文件: code_dedup/function_discovery.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["grandfather管理器<br/>Grandfather 三定律 — 古老重复管理.<br/>grandfather_manager<br/>文件: code_dedup/grandfather_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["健康监控<br/>健康仪表盘 — Dedup Health Score 0-100 + 趋势 +<br/>Session Log 写入.<br/>health_monitor<br/>文件: code_dedup/health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["集成hub<br/>集成协调器 — 24集成+19更新+16GitHub整合.<br/>integration_hub<br/>文件: code_dedup/integration_hub.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>code dedup包的integrations模块<br/>文件: code_dedup/integrations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["microclone检测器<br/>微型克隆检测器 — n-gram频率计数,<br/>1-2行高频模式聚合.<br/>micro_clone_detector<br/>文件: code_dedup/micro_clone_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["可控克隆生产器——零假阳性可期待引擎分子离散<br/>code dedup包的mock_duplicate_generator模块<br/>文件: code_dedup/mock_duplicate_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["monoculture守卫<br/>Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>monoculture_guard<br/>文件: code_dedup/monoculture_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["提取后稳定观察期守护 — 对标SDP 14天观察.<br/>14天稳定观察期.<br/>observation_window_guard<br/>文件: code_dedup/observation_window_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["路径索引校验器<br/>路径索引验证——验证 config<br/>数据集相对路径表与实际文件系统同步.<br/>path_index_validator<br/>文件: code_dedup/path_index_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["阶段执行器<br/>6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>phase_executor<br/>文件: code_dedup/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["策略树自动一致性校验器 — 虚线箭头影响分析.<br/>策略树一致性 + 影响分析.<br/>policy_tree_validator<br/>文件: code_dedup/policy_tree_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["预应用完整性门禁<br/>Pre-Apply 完整性门 — SHA256重新验证.<br/>pre_apply_integrity_gate<br/>文件: code_dedup/pre_apply_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["修复优先级排序器 — 置信度×Impact×适配性<br/>三因子排序.<br/>三因子修复优先级排序.<br/>prioritizer<br/>文件: code_dedup/prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["恢复清单写入器<br/>Recovery Manifest Writer — R2纯文本base64<br/>Manifest.<br/>recovery_manifest_writer<br/>文件: code_dedup/recovery_manifest_writer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["风险mitigator<br/>R1-R45全量风险缓解执行器 — 逐条检查缓解措施 +<br/>mitigation_tracker.yaml.<br/>risk_mitigator<br/>文件: code_dedup/risk_mitigator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["自扫描器<br/>引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>self_scanner<br/>文件: code_dedup/self_scanner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["sensitivity清扫器<br/>敏感性扫荡——threshold扫描->固化成new baseline<br/>（零假阳性+触达率保险）.<br/>sensitivity_sweeper<br/>文件: code_dedup/sensitivity_sweeper.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["影子信任校验器<br/>影子信任验证器 — ImportError 防护回路.<br/>shadow_trust_validator<br/>文件: code_dedup/shadow_trust_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["影子验证器<br/>影子清单验证器 — size sanity check +<br/>semantic验证 + 覆盖度报告.<br/>shadow_verifier<br/>文件: code_dedup/shadow_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["共享函数自我进化引擎 — 自动升降级 +<br/>行为漂移锁定.<br/>- shared函数被频繁使用(>50次) -><br/>自动晋升为(*A)autonomous<br/>shared_evolver<br/>文件: code_dedup/shared_evolver.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["共享生命周期管理器<br/>共享函数生命周期管理 —<br/>Active->Deprecated->Grace->Sunset->Retired<br/>五阶段状态机.<br/>shared_lifecycle_manager<br/>文件: code_dedup/shared_lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["signature匹配器<br/>5: 签名指纹 SHA256(:12) O(1) 精确匹配<br/>signature_matcher<br/>文件: code_dedup/signature_matcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax<br/>报告.<br/>- NET_NEGATIVE -> 自动退役建议<br/>simplicity_auditor<br/>文件: code_dedup/simplicity_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>共享函数 SSoT 注册器.<br/>ssot_registrar<br/>文件: code_dedup/ssot_registrar.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["stale共享检测器<br/>过时共享函数检测器 — 无caller × 30天 -><br/>STALE标记.<br/>stale_shared_detector<br/>文件: code_dedup/stale_shared_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["成功验证——判断一次去重操作是否真正消灭了克隆.<br/>code dedup包的success_validator模块<br/>文件: code_dedup/success_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["symbol索引<br/>符号索引 — 全局函数/类/import映射表.<br/>symbol_index<br/>文件: code_dedup/symbol_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>重复组主题聚类——将50组重复归约到3-5个主题.<br/>thematic_clusterer<br/>文件: code_dedup/thematic_clusterer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["code_dedup/trackers 包入口<br/>tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: trackers/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["后果追踪——记录每次修复操作对依赖方的影响.<br/>trackers包的consequence_tracker模块<br/>文件: trackers/consequence_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["热点追踪器 — 90天滑动窗口 + 高频变动检测 +<br/>新项目预热清单.<br/>热点追踪——90天滑动窗口.<br/>hotspot_tracker<br/>文件: trackers/hotspot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["importsurface追踪器<br/>Import表面积 (SBS) 负债追踪.<br/>import_surface_tracker<br/>文件: trackers/import_surface_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["问题追踪——扫描中发现需要人工处理的问题.<br/>trackers包的question_tracker模块<br/>文件: trackers/question_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍<br/>未fix.<br/>trackers包的risk_mitigation_tracker模块<br/>文件: trackers/risk_mitigation_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["验证器<br/>修复验证器 — import + 类型 + 行为采样验证.<br/>verifier<br/>文件: code_dedup/verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_init_py["gov_enforcement/commit_gates 包入口<br/>每个 gate 一个文件 + ``make_*_gate()``<br/>工厂函数，返回 ``GateSpec``。<br/>文件: commit_gates/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["archreference门禁<br/>#ARCH-NNN / #ARCH-DOMAIN-NNN<br/>悬空引用自动检测门禁<br/>arch_reference_gate<br/>文件: commit_gates/arch_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["asynciorunin上下文门禁<br/>异步上下文误用硬阻断门禁<br/>asyncio_run_in_context_gate<br/>文件: commit_gates<br/>/asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["baregetenv门禁<br/>裸 os.getenv 读密钥阻断门禁<br/>（NO-BARE-GETENV，§5.17.10 治本）<br/>bare_getenv_gate<br/>文件: commit_gates/bare_getenv_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["baresql门禁<br/>裸SQL字面量阻断门禁（NO-BARE-SQL，§5.160.2<br/>防复发）<br/>bare_sql_gate<br/>文件: commit_gates/bare_sql_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["baresubprocess门禁<br/>裸 subprocess 调用硬阻断门禁<br/>bare_subprocess_gate<br/>文件: commit_gates/bare_subprocess_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["蓝图amoduleconsistency门禁<br/>(A_module) 头部 module_id 格式一致性门禁<br/>blueprint_amodule_consistency_gate<br/>文件: commit_gates<br/>/blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["蓝图amodule跨check门禁<br/>- module_id_consistency_gate（prio=88）：跨文件<br/>(A_*) 唯一性，显式排除<br/>blueprint_amodule_cross_check_gate<br/>文件: commit_gates<br/>/blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["蓝图format门禁<br/>(BLUEPRINT) 头部 module_id 格式阻断门禁<br/>（BLUEPRINT-FORMAT，裁定#214 Phase 0 防蔓延）<br/>blueprint_format_gate<br/>文件: commit_gates/blueprint_format_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["能力一致性门禁<br/>Provider 路由-meta 一致性门禁<br/>（CAP-CONSISTENCY，裁定 #ARCH-CH-022 Phase 4.4）<br/>capability_consistency_gate<br/>文件: commit_gates<br/>/capability_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["capabilitylookuprequired门禁<br/>检测 commit 含 ``src/zephyr/**/*.py``<br/>业务代码变更时，当前 session 是否调用了<br/>capability_lookup_required_gate<br/>文件: commit_gates<br/>/capability_lookup_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["capabilityoverlap门禁<br/>新建 .py 文件 CapabilityLookup 提示门禁<br/>（warn-only，2026-06-30 治本）<br/>capability_overlap_gate<br/>文件: commit_gates/capability_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["ch批次大小门禁<br/>CH 批量写入防回退门禁（CH-BATCH-SIZE，§18.4<br/>防复发）<br/>ch_batch_size_gate<br/>文件: commit_gates/ch_batch_size_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["ch最终门禁<br/>query() 直接调用阻断门禁（CH-FINAL-GATE，裁定<br/>#ARCH-CH-007 B5）<br/>ch_final_gate<br/>文件: commit_gates/ch_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["ch版本col门禁<br/>CH version 列语义误用阻断门禁<br/>（CH-VERSION-COL，裁定 #ARCH-CH-009）<br/>ch_version_col_gate<br/>文件: commit_gates/ch_version_col_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["claimrequired门禁<br/>claim_files 前置检查门禁<br/>（CLAIM-REQUIRED，2026-06-30 治本）<br/>claim_required_gate<br/>文件: commit_gates/claim_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["consumersaccuracy门禁<br/>CONSUMERS 字段准确性 warn-only 门禁<br/>（CONSUMERS-ACCURACY）<br/>consumers_accuracy_gate<br/>文件: commit_gates/consumers_accuracy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["创建守卫<br/>新建 .py / 非 rules/ .yaml 文件 creation_token<br/>阻断门禁（CREATE-GUARD，2026-06-30 治本）<br/>create_guard<br/>文件: commit_gates/create_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["danglingreference门禁<br/>md §X.Y 悬空引用自动检测门禁<br/>dangling_reference_gate<br/>文件: commit_gates/dangling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["数据taskcompleteness门禁<br/>数据任务完整性门禁（warn 级，提醒型）<br/>data_task_completeness_gate<br/>文件: commit_gates<br/>/data_task_completeness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["datetimenowforbidden门禁<br/>时间戳约定硬阻断门禁<br/>datetime_now_forbidden_gate<br/>文件: commit_gates<br/>/datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["depgraphfreshness门禁<br/>治本目标（fail-silent 三要素之「可阻断」补强）：<br/>depgraph_freshness_gate<br/>文件: commit_gates/depgraph_freshness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["depgraphwritepath门禁<br/>depgraph 写入路径白名单门禁<br/>depgraph_write_path_gate<br/>文件: commit_gates/depgraph_write_path_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["derivationannotation门禁<br/>派生关系声明真实性校验门禁<br/>derivation_annotation_gate<br/>文件: commit_gates/derivation_annotation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["directorycontract门禁<br/>DCR-001~007 等效校验门禁（治本：弥补<br/>--no-verify 绕过 pre-commit 的缺口）<br/>directory_contract_gate<br/>文件: commit_gates/directory_contract_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["docrefbroken门禁<br/>文档相对路径断裂引用阻断门禁<br/>doc_ref_broken_gate<br/>文件: commit_gates/doc_ref_broken_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["域fk门禁<br/>(DOMAIN) 头部域注册表 FK 校验门禁<br/>domain_fk_gate<br/>文件: commit_gates/domain_fk_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["domainnamezhdirect访问门禁<br/>DOMAIN_NAME_ZH 字典直接访问硬阻断门禁<br/>domain_name_zh_direct_access_gate<br/>文件: commit_gates<br/>/domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["empty处理器门禁<br/>空事件 handler 函数阻断门禁<br/>empty_handler_gate<br/>文件: commit_gates/empty_handler_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["encoding门禁<br/>编码安全校验门禁（治本：弥补 --no-verify 绕过<br/>pre-commit GATE-ENCODING 的缺口）<br/>encoding_gate<br/>文件: commit_gates/encoding_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["exemptzonefrontmatter门禁<br/>从 make_exempt_zone_frontmatter_reconciler<br/>（post-commit warn）升级为 pre-commit 阻断<br/>gate。<br/>exempt_zone_frontmatter_gate<br/>文件: commit_gates<br/>/exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["filecopy门禁<br/>新增 .py 文件复制检测阻断门禁<br/>（FILE-COPY，2026-07-03 Phase 1 sub-task 3）<br/>file_copy_gate<br/>文件: commit_gates/file_copy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["fileplacementttl门禁<br/>文件放置与 TTL 一致性门禁（治本<br/>#ARCH-049：防止临时文件乱放根目录）<br/>file_placement_ttl_gate<br/>文件: commit_gates/file_placement_ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["folder容量hardlimit门禁<br/>文件夹容量硬上限门禁<br/>folder_capacity_hard_limit_gate<br/>文件: commit_gates<br/>/folder_capacity_hard_limit_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["foreignchange门禁<br/>外来变更检测门禁<br/>（FOREIGN-CHANGE-DETECTION，ARCH-054 治本）<br/>foreign_change_gate<br/>文件: commit_gates/foreign_change_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["forgedgwmarker门禁<br/>Forged GW Marker 前置检测门禁<br/>（FORGED-GW-MARKER， Phase 2）<br/>forged_gw_marker_gate<br/>文件: commit_gates/forged_gw_marker_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["函数dup门禁<br/>重复函数实现阻断门禁<br/>function_dup_gate<br/>文件: commit_gates/function_dup_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["门禁repo<br/>gates 表持久化仓库（AUDIT-07 P1-5: 从<br/>gate_engine.py 提取）<br/>gate_repo<br/>文件: commit_gates/gate_repo.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["Gitcall预算门禁<br/>检测 staged .py 文件中 ``subprocess.run(('git',<br/>...))`` 在 for/while 循环内直接调用<br/>git_call_budget_gate<br/>文件: commit_gates/git_call_budget_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["god类门禁<br/>检测 staged .py 文件中**新增**类的方法数 > 20。<br/>god_class_gate<br/>文件: commit_gates/god_class_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["hardcodedurl门禁<br/>硬编码 localhost URL 阻断门禁<br/>（NO-HARDCODED-URL，§5.160.9 防复发）<br/>hardcoded_url_gate<br/>文件: commit_gates/hardcoded_url_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["heldoverlap门禁<br/>搭便车防护门禁（HELD-OVERLAP，2026-06-30 治本）<br/>held_overlap_gate<br/>文件: commit_gates/held_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["highcomplexity门禁<br/>高循环复杂度阻断门禁<br/>（NO-HIGH-COMPLEXITY，§5.158 防复发）<br/>high_complexity_gate<br/>文件: commit_gates/high_complexity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["iduniqueness门禁<br/>从 make_precommit_id_uniqueness_reconciler<br/>（post-commit warn）升级为 pre-commit 阻断<br/>gate。<br/>id_uniqueness_gate<br/>文件: commit_gates/id_uniqueness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["importdirection门禁<br/>shared 层向上依赖阻断门禁<br/>（NO-UPWARD-IMPORT，§5.152 防复发）<br/>import_direction_gate<br/>文件: commit_gates/import_direction_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["导入完整性门禁<br/>病根（第一性原理）<br/>import_integrity_gate<br/>文件: commit_gates/import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["issueresolved完整性门禁<br/>'Resolved but incomplete' 系统性风险——AI<br/>倾向于在主体工作完成后立即标记<br/>issue_resolved_integrity_gate<br/>文件: commit_gates<br/>/issue_resolved_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["longparamlist门禁<br/>长参数列表阻断门禁（NO-LONG-PARAM-LIST，§5.150<br/>防复发）<br/>long_param_list_gate<br/>文件: commit_gates/long_param_list_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["手册onlypermanent门禁<br/>永久系统脚本 manual 触发无事件订阅阻断门禁<br/>（MANUAL-ONLY-PERMANENT，#ARCH-GOV-CONVERGENCE-M<br/>ETA Phase 3.6 补齐<br/>manual_only_permanent_gate<br/>文件: commit_gates/manual_only_permanent_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["MCP版本字段门禁<br/>MCP version 字段缺失硬阻断门禁<br/>mcp_version_field_gate<br/>文件: commit_gates/mcp_version_field_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["模块id一致性门禁<br/>module_id 三声明轨道一致性 + count 派生 +<br/>跨文件唯一性门禁（Phase 3 reconciler->gate<br/>收敛）<br/>module_id_consistency_gate<br/>文件: commit_gates/module_id_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["msg敞口门禁<br/>错误消息暴露敏感信息阻断门禁<br/>msg_exposure_gate<br/>文件: commit_gates/msg_exposure_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["msgstyle门禁<br/>错误消息标点/箭头风格阻断门禁<br/>msg_style_gate<br/>文件: commit_gates/msg_style_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["mutableconstwithoutfinal门禁<br/>可变常量缺 Final 标注硬阻断门禁<br/>mutable_const_without_final_gate<br/>文件: commit_gates<br/>/mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["新文件依赖图门禁<br/>新建 .py 文件 depgraph 未登记硬阻断门禁<br/>new_file_depgraph_gate<br/>文件: commit_gates/new_file_depgraph_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["noimportsideeffect门禁<br/>模块导入零副作用门禁<br/>no_import_side_effect_gate<br/>文件: commit_gates/no_import_side_effect_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["noqa验证门禁<br/>自定义 noqa 标记合规性门禁<br/>（NOQA-VALIDATION，ARCH-NOQA-GOV-001 治本）<br/>noqa_validation_gate<br/>文件: commit_gates/noqa_validation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["openwithoutwith门禁<br/>() 未在 with 内硬阻断门禁<br/>open_without_with_gate<br/>文件: commit_gates/open_without_with_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["孤儿module门禁<br/>孤儿模块（无 import 引用）阻断门禁<br/>orphan_module_gate<br/>文件: commit_gates/orphan_module_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["panorama对齐门禁<br/>三图模块对齐门禁（四图模块对齐 Step 4，ARCH-056<br/>升级）<br/>panorama_alignment_gate<br/>文件: commit_gates/panorama_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["precommitoffline门禁<br/>pre-commit 配置离线可运行检测门禁<br/>precommit_offline_gate<br/>文件: commit_gates/precommit_offline_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["pureassertion门禁<br/>纯陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016<br/>治本）<br/>pure_assertion_gate<br/>文件: commit_gates/pure_assertion_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["pureshim门禁<br/>（GATE-SSOT-CODE 三合一之一），``git commit<br/>--no-verify`` 绕过所有 pre-commit hooks。<br/>pure_shim_gate<br/>文件: commit_gates/pure_shim_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["r5digitsuffix门禁<br/>R5 数字后缀目录禁止门禁（治本：弥补 --no-verify<br/>绕过 pre-commit 的缺口）<br/>r5_digit_suffix_gate<br/>文件: commit_gates/r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["协调器健康门禁<br/>直接在 GitCommitGateway.commit<br/>中调用）提升为正式 CommitGateRegistry gate。<br/>reconciler_health_gate<br/>文件: commit_gates/reconciler_health_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["relativepathliteral门禁<br/>相对路径字面量硬阻断门禁<br/>relative_path_literal_gate<br/>文件: commit_gates/relative_path_literal_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["renamedepgraphsync门禁<br/>文件重命名后 depgraph 未同步阻断门禁<br/>rename_depgraph_sync_gate<br/>文件: commit_gates/rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["规则执行pairing门禁<br/>规则-执行配对门禁<br/>（RULE-EXECUTION-PAIRING，Phase 3.5）<br/>rule_execution_pairing_gate<br/>文件: commit_gates<br/>/rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["规则fourway对齐门禁<br/>规则四方对齐门禁<br/>rule_four_way_alignment_gate<br/>文件: commit_gates<br/>/rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["rulingcommitverified门禁<br/>文档'已完成'声明 commit hash 真实性硬验证门禁<br/>ruling_commit_verified_gate<br/>文件: commit_gates<br/>/ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["rulingreference门禁<br/>裁定#NNN 悬空引用自动检测门禁<br/>ruling_reference_gate<br/>文件: commit_gates/ruling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["结构fileexists门禁<br/>裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase<br/>1：SSoT 存在性强制。<br/>schema_file_exists_gate<br/>文件: commit_gates/schema_file_exists_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["脚本导入完整性门禁<br/>constants 符号导入完整性门禁<br/>scripts_import_integrity_gate<br/>文件: commit_gates<br/>/scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["会话required门禁<br/>会话 注册强制门禁（SESSION-REQUIRED，2026-07-01<br/>治本 FP-ISO.4B 件1改）<br/>session_required_gate<br/>文件: commit_gates/session_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["快照漂移门禁<br/>运行时违规快照漂移阻断门禁<br/>（SNAPSHOT-DRIFT，#ARCH-GOV-CONVERGENCE-META<br/>Phase 3.6 补齐 rc1 enforceability）<br/>snapshot_drift_gate<br/>文件: commit_gates/snapshot_drift_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["ssotredefinition门禁<br/>SSoT 符号重复定义硬阻断门禁<br/>ssot_redefinition_gate<br/>文件: commit_gates/ssot_redefinition_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["tablename注册表门禁<br/>裁定 # Phase 4：SSoT 真源强制闭环。<br/>table_name_registry_gate<br/>文件: commit_gates/table_name_registry_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["测试源一致性门禁<br/>测试-源码符号一致性门禁<br/>（TEST-SOURCE-CONSISTENCY，§5.178 防复发）<br/>test_source_consistency_gate<br/>文件: commit_gates<br/>/test_source_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["testscoverage门禁<br/>Gate 测试覆盖率校验 meta-gate<br/>（META-TESTS-COVERAGE，）<br/>tests_coverage_gate<br/>文件: commit_gates/tests_coverage_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["存活时间门禁<br/>ttl 字段校验门禁（治本：弥补 --no-verify 绕过<br/>pre-commit GATE-15 的缺口）<br/>ttl_gate<br/>文件: commit_gates/ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["undefinedname门禁<br/>UNDEFINED-NAME 门禁（F821 未定义符号硬阻断）<br/>undefined_name_gate<br/>文件: commit_gates/undefined_name_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["unsafedictspread门禁<br/>``**data`` 直接展开模式 warn 级门禁<br/>unsafe_dict_spread_gate<br/>文件: commit_gates/unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["vocabchain门禁<br/>SSoT 引用硬编码阻断门禁<br/>（VOCAB-CHAIN，#ARCH-GOV-CONVERGENCE-META Phase<br/>3.6 补齐 rc2 enforceability）<br/>vocab_chain_gate<br/>文件: commit_gates/vocab_chain_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["vocabhardcode门禁<br/>新增 .py 文件词表硬编码阻断门禁<br/>（VOCAB-HARDCODE，2026-07-03 Phase 1）<br/>vocab_hardcode_gate<br/>文件: commit_gates/vocab_hardcode_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["zephyrenvdirect访问门禁<br/>ZEPHYR_ENV 直访硬阻断门禁<br/>（ZEPHYR-ENV-DIRECT-ACCESS）<br/>zephyr_env_direct_access_gate<br/>文件: commit_gates<br/>/zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["门禁自动registrar<br/>YAML 驱动的 in-process gate 自动注册器<br/>（#ARCH-GATE-REGISTRY-AUTO-001 Phase 3）<br/>gate_auto_registrar<br/>文件: rule_bridge/gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_data_test_symbol_normalizer_py["测试symbol归一化器<br/>symbol 标准化模块测试。<br/>test_symbol_normalizer<br/>文件: data/test_symbol_normalizer.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_check_yaml_anchor_consistency_py["commit_gates/test_check_yaml_anchor_consistency<br/>test_check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描 smoke test.<br/>文件: commit_gates<br/>/test_check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    tests_governance_test_apply_dataflowgraph_smoke_py["测试applydataflowgraphsmoke<br/>治理包的test_apply_dataflowgraph_smoke模块<br/>文件: governance<br/>/test_apply_dataflowgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_decisiongraph_smoke_py["测试applydecisiongraphsmoke<br/>治理包的test_apply_decisiongraph_smoke模块<br/>文件: governance<br/>/test_apply_decisiongraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_depgraph_smoke_py["测试applydepgraphsmoke<br/>#ARCH-TOOL-HEALTH-V1 Phase 4<br/>治本：核心治理工具必须有 e2e smoke test。<br/>文件: governance/test_apply_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_audit_return_contract_usage_py["测试审计returncontractusage<br/>返回契约 ok 键审计脚本单元测试<br/>test_audit_return_contract_usage<br/>文件: governance<br/>/test_audit_return_contract_usage.py<br/>(生产态 / production)"]
    tests_governance_test_audit_worktree_ops_telemetry_py["测试审计worktree运维遥测<br/>worktree_ops_log 遥测完整性审计测试<br/>test_audit_worktree_ops_telemetry<br/>文件: governance<br/>/test_audit_worktree_ops_telemetry.py<br/>(生产态 / production)"]
    tests_governance_test_generate_project_depgraph_smoke_py["测试generateprojectdepgraphsmoke<br/>治理包的test_generate_project_depgraph_smoke模块<br/>文件: governance<br/>/test_generate_project_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["测试提交提交守卫no校验阈值<br/>高基数 --no-verify 阈值阻断 e2e 测试<br/>文件: governance<br/>/test_post_commit_guard_no_verify_threshold.py<br/>(生产态 / production)"]
    tests_governance_test_run_silent_failure_regression_py["测试runsilent故障regression<br/>silent-failure 回归 runner 单元测试（P3-2）<br/>test_run_silent_failure_regression<br/>文件: governance<br/>/test_run_silent_failure_regression.py<br/>(生产态 / production)"]
    tests_governance_test_session_startup_health_check_py["测试会话启动健康检查<br/>AI session 启动健康度自检单元测试<br/>test_session_startup_health_check<br/>文件: governance<br/>/test_session_startup_health_check.py<br/>(生产态 / production)"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["测试syncyamltodepgraphsmoke<br/>治理包的test_sync_yaml_to_depgraph_smoke模块<br/>文件: governance<br/>/test_sync_yaml_to_depgraph_smoke.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ scripts_governance_d7_code_check_yaml_anchor_consistency_py
    scripts_governance_d7_code_check_yaml_anchor_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py ~~~ src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_manager_py
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
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["安全自动修复引擎——五直接开关+五间接约束.<br/>code dedup包的auto_fixer模块<br/>文件: code_dedup/auto_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["缓存管理器<br/>Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>cache_manager<br/>文件: code_dedup/cache_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_config_py["code_dedup/config<br/>配置管理 — 策略树 YAML 加载 + 项目规模感知四<br/>Tier 自适应阈值.<br/>文件: code_dedup/config.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["退出codes<br/>退出码定义模块——五档exit code<br/>0-4枚举+描述+判定逻辑.<br/>exit_codes<br/>文件: code_dedup/exit_codes.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_report_py["报告<br/>生成器 — YAML/JSON 输出 + 退出码判定 + Health<br/>Score 聚合<br/>report<br/>文件: code_dedup/report.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>盲点关闭追踪器.<br/>blind_spot_tracker<br/>文件: trackers/blind_spot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["差异辅助<br/>门禁 共享 diff 解析工具模块<br/>_diff_helpers<br/>文件: commit_gates/_diff_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["reference辅助<br/>引用检测门禁共享工具函数<br/>_reference_helpers<br/>文件: commit_gates/_reference_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["capabilitylookup绕过策略<br/>（CAPABILITY-LOOKUP-HEALTH,<br/>priority=220）的唯一共享入口。<br/>capability_lookup_bypass_policy<br/>文件: commit_gates<br/>/capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["permtrigger门禁<br/>永久系统脚本时间触发模式无事件订阅阻断门禁<br/>perm_trigger_gate<br/>文件: commit_gates/perm_trigger_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
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
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    tests_governance_test_audit_worktree_ops_telemetry_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
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
    class D_GOV_ENFORCEMENT,D_SHARED,D_GOV_AUDIT,D_GOVERNANCE,D_GOV_SCRIPTS external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 171 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["检查pureassertion<br/>GOV-DOC-016 纯陈述原则检测真源（SSoT）。<br/>check_pure_assertion<br/>文件: d3_metadata/check_pure_assertion.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_module_id_consistency_py["检查模块id一致性<br/>module_id 全仓一致性扫描（--scan-existing<br/>模式）.<br/>check_module_id_consistency<br/>文件: d7_code/check_module_id_consistency.py<br/>(生产态 / production)"]
    scripts_governance_d7_code_check_yaml_anchor_consistency_py["d7_code/check_yaml_anchor_consistency<br/>check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描.<br/>文件: d7_code/check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_init_py["zephyr/gov_code_quality 包入口<br/>包入口。gov_code_quality domain package — code<br/>quality governance (D_GOV_CODE_QUALITY).<br/>文件: gov_code_quality/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_init_py["gov_code_quality/code_dedup 包入口<br/>code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: code_dedup/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py["共享函数注解引擎 — @shared / @knowndup / @inten<br/>共享函数注解引擎 — @shared / @known_dup /<br/>@intentional 三注解.<br/>annotations<br/>文件: code_dedup/annotations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["ast比较器<br/>- AST 子树归一化哈希<br/>ast_comparator<br/>文件: code_dedup/ast_comparator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOINT<br/>> APPLY -> RECOVER<br/>atomic_fixer<br/>文件: code_dedup/atomic_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["behavioral采样器<br/>行为采样验证器 — Stage 0.25 低成本快速验证.<br/>behavioral_sampler<br/>文件: code_dedup/behavioral_sampler.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["行为信任检查器 — 行为漂移DIVERGED检测.<br/>行为正确性检查.<br/>behavioral_trust_checker<br/>文件: code_dedup/behavioral_trust_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["金丝雀管理器<br/>金丝雀工厂——生成已知oracle 文件<br/>用于引擎检出+回归测试.<br/>canary_manager<br/>文件: code_dedup/canary_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>金丝雀函数注册表.<br/>canary_register<br/>文件: code_dedup/canary_register.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["code_dedup/cli<br/>code-dedup-engine<br/>CLI——子命令映射+退出码+扫描入口.<br/>文件: code_dedup/cli.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["代码分析器运行器<br/>检查运行器——按照敏感基线运行三阶段+导出 yaml<br/>报告.<br/>code_analyzer_runner<br/>文件: code_dedup/code_analyzer_runner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["代码模拟器<br/>播放录制的克隆演化序列，stress-test AST<br/>/baseline归一化<br/>code_simulator<br/>文件: code_dedup/code_simulator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["API契约一致性检查器 — 存在性·行为·契约三维.<br/>三维API契约检查.<br/>contract_consistency_checker<br/>文件: code_dedup/contract_consistency_checker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["跨boundary检测器<br/>跨边界克隆感知——四大边界差异化检测+独立策略+跨边<br/>界保守auto_fix规则.<br/>cross_boundary_detector<br/>文件: code_dedup/cross_boundary_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["deadmodule检测器<br/>死共享模块检测器 — shared/子模块无人使用 -><br/>DEAD.<br/>dead_module_detector<br/>文件: code_dedup/dead_module_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["debt投影器<br/>去重债务预测器 — weeks_to_payoff + intake_rate<br/>vs fix_rate 蒙特卡洛模拟.<br/>debt_projector<br/>文件: code_dedup/debt_projector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["决策审计器<br/>决策审计链 — DecisionFingerprint 不可变追加日志.<br/>decision_auditor<br/>文件: code_dedup/decision_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["退化<br/>降级运行管理器 — 各 Stage 独立 try/except +<br/>degradation_level + exit code.<br/>文件: code_dedup/degradation.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["差异检测器<br/>Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>diff_detector<br/>文件: code_dedup/diff_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["doom循环守卫<br/>Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>doom_loop_guard<br/>文件: code_dedup/doom_loop_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["extraction安全<br/>安全提取适配性评估器 — Suitability Score 0-100<br/>+ 不安全提取模式检测.<br/>extraction_safety<br/>文件: code_dedup/extraction_safety.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["falsenegative审计器<br/>- L1 Sweep：增量扫描漏过的去重对（全量 vs 增量<br/>diff）<br/>false_negative_auditor<br/>文件: code_dedup/false_negative_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["15维超综合审计首页 — 逐项证明'做过且做对'.<br/>- 15维审计刹车：每一项给出 PASS/FAIL/WAIVED +<br/>证据<br/>fifteen_dimension_auditor<br/>文件: code_dedup/fifteen_dimension_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["文件创建清单执行器 — 验证所有源/测试<br/>/数据文件存在性.<br/>文件创建清单验证器.<br/>file_creator<br/>文件: code_dedup/file_creator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>主动发现未注册的共享函数.<br/>function_discovery<br/>文件: code_dedup/function_discovery.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["grandfather管理器<br/>Grandfather 三定律 — 古老重复管理.<br/>grandfather_manager<br/>文件: code_dedup/grandfather_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["健康监控<br/>健康仪表盘 — Dedup Health Score 0-100 + 趋势 +<br/>Session Log 写入.<br/>health_monitor<br/>文件: code_dedup/health_monitor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["集成hub<br/>集成协调器 — 24集成+19更新+16GitHub整合.<br/>integration_hub<br/>文件: code_dedup/integration_hub.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>code dedup包的integrations模块<br/>文件: code_dedup/integrations.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["microclone检测器<br/>微型克隆检测器 — n-gram频率计数,<br/>1-2行高频模式聚合.<br/>micro_clone_detector<br/>文件: code_dedup/micro_clone_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["可控克隆生产器——零假阳性可期待引擎分子离散<br/>code dedup包的mock_duplicate_generator模块<br/>文件: code_dedup/mock_duplicate_generator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["monoculture守卫<br/>Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>monoculture_guard<br/>文件: code_dedup/monoculture_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["提取后稳定观察期守护 — 对标SDP 14天观察.<br/>14天稳定观察期.<br/>observation_window_guard<br/>文件: code_dedup/observation_window_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["路径索引校验器<br/>路径索引验证——验证 config<br/>数据集相对路径表与实际文件系统同步.<br/>path_index_validator<br/>文件: code_dedup/path_index_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["阶段执行器<br/>6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>phase_executor<br/>文件: code_dedup/phase_executor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["策略树自动一致性校验器 — 虚线箭头影响分析.<br/>策略树一致性 + 影响分析.<br/>policy_tree_validator<br/>文件: code_dedup/policy_tree_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["预应用完整性门禁<br/>Pre-Apply 完整性门 — SHA256重新验证.<br/>pre_apply_integrity_gate<br/>文件: code_dedup/pre_apply_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["修复优先级排序器 — 置信度×Impact×适配性<br/>三因子排序.<br/>三因子修复优先级排序.<br/>prioritizer<br/>文件: code_dedup/prioritizer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["恢复清单写入器<br/>Recovery Manifest Writer — R2纯文本base64<br/>Manifest.<br/>recovery_manifest_writer<br/>文件: code_dedup/recovery_manifest_writer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["风险mitigator<br/>R1-R45全量风险缓解执行器 — 逐条检查缓解措施 +<br/>mitigation_tracker.yaml.<br/>risk_mitigator<br/>文件: code_dedup/risk_mitigator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["自扫描器<br/>引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>self_scanner<br/>文件: code_dedup/self_scanner.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["sensitivity清扫器<br/>敏感性扫荡——threshold扫描->固化成new baseline<br/>（零假阳性+触达率保险）.<br/>sensitivity_sweeper<br/>文件: code_dedup/sensitivity_sweeper.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["影子信任校验器<br/>影子信任验证器 — ImportError 防护回路.<br/>shadow_trust_validator<br/>文件: code_dedup/shadow_trust_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["影子验证器<br/>影子清单验证器 — size sanity check +<br/>semantic验证 + 覆盖度报告.<br/>shadow_verifier<br/>文件: code_dedup/shadow_verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["共享函数自我进化引擎 — 自动升降级 +<br/>行为漂移锁定.<br/>- shared函数被频繁使用(>50次) -><br/>自动晋升为(*A)autonomous<br/>shared_evolver<br/>文件: code_dedup/shared_evolver.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["共享生命周期管理器<br/>共享函数生命周期管理 —<br/>Active->Deprecated->Grace->Sunset->Retired<br/>五阶段状态机.<br/>shared_lifecycle_manager<br/>文件: code_dedup/shared_lifecycle_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["signature匹配器<br/>5: 签名指纹 SHA256(:12) O(1) 精确匹配<br/>signature_matcher<br/>文件: code_dedup/signature_matcher.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["引擎成本效益自审计器 — SAS 0-100 月度审计 + Tax<br/>报告.<br/>- NET_NEGATIVE -> 自动退役建议<br/>simplicity_auditor<br/>文件: code_dedup/simplicity_auditor.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>共享函数 SSoT 注册器.<br/>ssot_registrar<br/>文件: code_dedup/ssot_registrar.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["stale共享检测器<br/>过时共享函数检测器 — 无caller × 30天 -><br/>STALE标记.<br/>stale_shared_detector<br/>文件: code_dedup/stale_shared_detector.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["成功验证——判断一次去重操作是否真正消灭了克隆.<br/>code dedup包的success_validator模块<br/>文件: code_dedup/success_validator.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["symbol索引<br/>符号索引 — 全局函数/类/import映射表.<br/>symbol_index<br/>文件: code_dedup/symbol_index.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>重复组主题聚类——将50组重复归约到3-5个主题.<br/>thematic_clusterer<br/>文件: code_dedup/thematic_clusterer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["code_dedup/trackers 包入口<br/>tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: trackers/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["后果追踪——记录每次修复操作对依赖方的影响.<br/>trackers包的consequence_tracker模块<br/>文件: trackers/consequence_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["热点追踪器 — 90天滑动窗口 + 高频变动检测 +<br/>新项目预热清单.<br/>热点追踪——90天滑动窗口.<br/>hotspot_tracker<br/>文件: trackers/hotspot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["importsurface追踪器<br/>Import表面积 (SBS) 负债追踪.<br/>import_surface_tracker<br/>文件: trackers/import_surface_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["问题追踪——扫描中发现需要人工处理的问题.<br/>trackers包的question_tracker模块<br/>文件: trackers/question_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["风险缓解追踪——捕获哪些克隆报告了但在N次扫描后仍<br/>未fix.<br/>trackers包的risk_mitigation_tracker模块<br/>文件: trackers/risk_mitigation_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["验证器<br/>修复验证器 — import + 类型 + 行为采样验证.<br/>verifier<br/>文件: code_dedup/verifier.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_init_py["gov_enforcement/commit_gates 包入口<br/>每个 gate 一个文件 + ``make_*_gate()``<br/>工厂函数，返回 ``GateSpec``。<br/>文件: commit_gates/__init__.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["archreference门禁<br/>#ARCH-NNN / #ARCH-DOMAIN-NNN<br/>悬空引用自动检测门禁<br/>arch_reference_gate<br/>文件: commit_gates/arch_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["asynciorunin上下文门禁<br/>异步上下文误用硬阻断门禁<br/>asyncio_run_in_context_gate<br/>文件: commit_gates<br/>/asyncio_run_in_context_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["baregetenv门禁<br/>裸 os.getenv 读密钥阻断门禁<br/>（NO-BARE-GETENV，§5.17.10 治本）<br/>bare_getenv_gate<br/>文件: commit_gates/bare_getenv_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["baresql门禁<br/>裸SQL字面量阻断门禁（NO-BARE-SQL，§5.160.2<br/>防复发）<br/>bare_sql_gate<br/>文件: commit_gates/bare_sql_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["baresubprocess门禁<br/>裸 subprocess 调用硬阻断门禁<br/>bare_subprocess_gate<br/>文件: commit_gates/bare_subprocess_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["蓝图amoduleconsistency门禁<br/>(A_module) 头部 module_id 格式一致性门禁<br/>blueprint_amodule_consistency_gate<br/>文件: commit_gates<br/>/blueprint_amodule_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["蓝图amodule跨check门禁<br/>- module_id_consistency_gate（prio=88）：跨文件<br/>(A_*) 唯一性，显式排除<br/>blueprint_amodule_cross_check_gate<br/>文件: commit_gates<br/>/blueprint_amodule_cross_check_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["蓝图format门禁<br/>(BLUEPRINT) 头部 module_id 格式阻断门禁<br/>（BLUEPRINT-FORMAT，裁定#214 Phase 0 防蔓延）<br/>blueprint_format_gate<br/>文件: commit_gates/blueprint_format_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["能力一致性门禁<br/>Provider 路由-meta 一致性门禁<br/>（CAP-CONSISTENCY，裁定 #ARCH-CH-022 Phase 4.4）<br/>capability_consistency_gate<br/>文件: commit_gates<br/>/capability_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["capabilitylookuprequired门禁<br/>检测 commit 含 ``src/zephyr/**/*.py``<br/>业务代码变更时，当前 session 是否调用了<br/>capability_lookup_required_gate<br/>文件: commit_gates<br/>/capability_lookup_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["capabilityoverlap门禁<br/>新建 .py 文件 CapabilityLookup 提示门禁<br/>（warn-only，2026-06-30 治本）<br/>capability_overlap_gate<br/>文件: commit_gates/capability_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["ch批次大小门禁<br/>CH 批量写入防回退门禁（CH-BATCH-SIZE，§18.4<br/>防复发）<br/>ch_batch_size_gate<br/>文件: commit_gates/ch_batch_size_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["ch最终门禁<br/>query() 直接调用阻断门禁（CH-FINAL-GATE，裁定<br/>#ARCH-CH-007 B5）<br/>ch_final_gate<br/>文件: commit_gates/ch_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["ch版本col门禁<br/>CH version 列语义误用阻断门禁<br/>（CH-VERSION-COL，裁定 #ARCH-CH-009）<br/>ch_version_col_gate<br/>文件: commit_gates/ch_version_col_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["claimrequired门禁<br/>claim_files 前置检查门禁<br/>（CLAIM-REQUIRED，2026-06-30 治本）<br/>claim_required_gate<br/>文件: commit_gates/claim_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["consumersaccuracy门禁<br/>CONSUMERS 字段准确性 warn-only 门禁<br/>（CONSUMERS-ACCURACY）<br/>consumers_accuracy_gate<br/>文件: commit_gates/consumers_accuracy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["创建守卫<br/>新建 .py / 非 rules/ .yaml 文件 creation_token<br/>阻断门禁（CREATE-GUARD，2026-06-30 治本）<br/>create_guard<br/>文件: commit_gates/create_guard.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["danglingreference门禁<br/>md §X.Y 悬空引用自动检测门禁<br/>dangling_reference_gate<br/>文件: commit_gates/dangling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["数据taskcompleteness门禁<br/>数据任务完整性门禁（warn 级，提醒型）<br/>data_task_completeness_gate<br/>文件: commit_gates<br/>/data_task_completeness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["datetimenowforbidden门禁<br/>时间戳约定硬阻断门禁<br/>datetime_now_forbidden_gate<br/>文件: commit_gates<br/>/datetime_now_forbidden_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["depgraphfreshness门禁<br/>治本目标（fail-silent 三要素之「可阻断」补强）：<br/>depgraph_freshness_gate<br/>文件: commit_gates/depgraph_freshness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["depgraphwritepath门禁<br/>depgraph 写入路径白名单门禁<br/>depgraph_write_path_gate<br/>文件: commit_gates/depgraph_write_path_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["derivationannotation门禁<br/>派生关系声明真实性校验门禁<br/>derivation_annotation_gate<br/>文件: commit_gates/derivation_annotation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["directorycontract门禁<br/>DCR-001~007 等效校验门禁（治本：弥补<br/>--no-verify 绕过 pre-commit 的缺口）<br/>directory_contract_gate<br/>文件: commit_gates/directory_contract_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["docrefbroken门禁<br/>文档相对路径断裂引用阻断门禁<br/>doc_ref_broken_gate<br/>文件: commit_gates/doc_ref_broken_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["域fk门禁<br/>(DOMAIN) 头部域注册表 FK 校验门禁<br/>domain_fk_gate<br/>文件: commit_gates/domain_fk_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["domainnamezhdirect访问门禁<br/>DOMAIN_NAME_ZH 字典直接访问硬阻断门禁<br/>domain_name_zh_direct_access_gate<br/>文件: commit_gates<br/>/domain_name_zh_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["empty处理器门禁<br/>空事件 handler 函数阻断门禁<br/>empty_handler_gate<br/>文件: commit_gates/empty_handler_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["encoding门禁<br/>编码安全校验门禁（治本：弥补 --no-verify 绕过<br/>pre-commit GATE-ENCODING 的缺口）<br/>encoding_gate<br/>文件: commit_gates/encoding_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["exemptzonefrontmatter门禁<br/>从 make_exempt_zone_frontmatter_reconciler<br/>（post-commit warn）升级为 pre-commit 阻断<br/>gate。<br/>exempt_zone_frontmatter_gate<br/>文件: commit_gates<br/>/exempt_zone_frontmatter_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["filecopy门禁<br/>新增 .py 文件复制检测阻断门禁<br/>（FILE-COPY，2026-07-03 Phase 1 sub-task 3）<br/>file_copy_gate<br/>文件: commit_gates/file_copy_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["fileplacementttl门禁<br/>文件放置与 TTL 一致性门禁（治本<br/>#ARCH-049：防止临时文件乱放根目录）<br/>file_placement_ttl_gate<br/>文件: commit_gates/file_placement_ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["folder容量hardlimit门禁<br/>文件夹容量硬上限门禁<br/>folder_capacity_hard_limit_gate<br/>文件: commit_gates<br/>/folder_capacity_hard_limit_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["foreignchange门禁<br/>外来变更检测门禁<br/>（FOREIGN-CHANGE-DETECTION，ARCH-054 治本）<br/>foreign_change_gate<br/>文件: commit_gates/foreign_change_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["forgedgwmarker门禁<br/>Forged GW Marker 前置检测门禁<br/>（FORGED-GW-MARKER， Phase 2）<br/>forged_gw_marker_gate<br/>文件: commit_gates/forged_gw_marker_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["函数dup门禁<br/>重复函数实现阻断门禁<br/>function_dup_gate<br/>文件: commit_gates/function_dup_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["门禁repo<br/>gates 表持久化仓库（AUDIT-07 P1-5: 从<br/>gate_engine.py 提取）<br/>gate_repo<br/>文件: commit_gates/gate_repo.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["Gitcall预算门禁<br/>检测 staged .py 文件中 ``subprocess.run(('git',<br/>...))`` 在 for/while 循环内直接调用<br/>git_call_budget_gate<br/>文件: commit_gates/git_call_budget_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["god类门禁<br/>检测 staged .py 文件中**新增**类的方法数 > 20。<br/>god_class_gate<br/>文件: commit_gates/god_class_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["hardcodedurl门禁<br/>硬编码 localhost URL 阻断门禁<br/>（NO-HARDCODED-URL，§5.160.9 防复发）<br/>hardcoded_url_gate<br/>文件: commit_gates/hardcoded_url_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["heldoverlap门禁<br/>搭便车防护门禁（HELD-OVERLAP，2026-06-30 治本）<br/>held_overlap_gate<br/>文件: commit_gates/held_overlap_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["highcomplexity门禁<br/>高循环复杂度阻断门禁<br/>（NO-HIGH-COMPLEXITY，§5.158 防复发）<br/>high_complexity_gate<br/>文件: commit_gates/high_complexity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["iduniqueness门禁<br/>从 make_precommit_id_uniqueness_reconciler<br/>（post-commit warn）升级为 pre-commit 阻断<br/>gate。<br/>id_uniqueness_gate<br/>文件: commit_gates/id_uniqueness_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["importdirection门禁<br/>shared 层向上依赖阻断门禁<br/>（NO-UPWARD-IMPORT，§5.152 防复发）<br/>import_direction_gate<br/>文件: commit_gates/import_direction_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["导入完整性门禁<br/>病根（第一性原理）<br/>import_integrity_gate<br/>文件: commit_gates/import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["issueresolved完整性门禁<br/>'Resolved but incomplete' 系统性风险——AI<br/>倾向于在主体工作完成后立即标记<br/>issue_resolved_integrity_gate<br/>文件: commit_gates<br/>/issue_resolved_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["longparamlist门禁<br/>长参数列表阻断门禁（NO-LONG-PARAM-LIST，§5.150<br/>防复发）<br/>long_param_list_gate<br/>文件: commit_gates/long_param_list_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["手册onlypermanent门禁<br/>永久系统脚本 manual 触发无事件订阅阻断门禁<br/>（MANUAL-ONLY-PERMANENT，#ARCH-GOV-CONVERGENCE-M<br/>ETA Phase 3.6 补齐<br/>manual_only_permanent_gate<br/>文件: commit_gates/manual_only_permanent_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["MCP版本字段门禁<br/>MCP version 字段缺失硬阻断门禁<br/>mcp_version_field_gate<br/>文件: commit_gates/mcp_version_field_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["模块id一致性门禁<br/>module_id 三声明轨道一致性 + count 派生 +<br/>跨文件唯一性门禁（Phase 3 reconciler->gate<br/>收敛）<br/>module_id_consistency_gate<br/>文件: commit_gates/module_id_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["msg敞口门禁<br/>错误消息暴露敏感信息阻断门禁<br/>msg_exposure_gate<br/>文件: commit_gates/msg_exposure_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["msgstyle门禁<br/>错误消息标点/箭头风格阻断门禁<br/>msg_style_gate<br/>文件: commit_gates/msg_style_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["mutableconstwithoutfinal门禁<br/>可变常量缺 Final 标注硬阻断门禁<br/>mutable_const_without_final_gate<br/>文件: commit_gates<br/>/mutable_const_without_final_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["新文件依赖图门禁<br/>新建 .py 文件 depgraph 未登记硬阻断门禁<br/>new_file_depgraph_gate<br/>文件: commit_gates/new_file_depgraph_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["noimportsideeffect门禁<br/>模块导入零副作用门禁<br/>no_import_side_effect_gate<br/>文件: commit_gates/no_import_side_effect_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["noqa验证门禁<br/>自定义 noqa 标记合规性门禁<br/>（NOQA-VALIDATION，ARCH-NOQA-GOV-001 治本）<br/>noqa_validation_gate<br/>文件: commit_gates/noqa_validation_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["openwithoutwith门禁<br/>() 未在 with 内硬阻断门禁<br/>open_without_with_gate<br/>文件: commit_gates/open_without_with_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["孤儿module门禁<br/>孤儿模块（无 import 引用）阻断门禁<br/>orphan_module_gate<br/>文件: commit_gates/orphan_module_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["panorama对齐门禁<br/>三图模块对齐门禁（四图模块对齐 Step 4，ARCH-056<br/>升级）<br/>panorama_alignment_gate<br/>文件: commit_gates/panorama_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["precommitoffline门禁<br/>pre-commit 配置离线可运行检测门禁<br/>precommit_offline_gate<br/>文件: commit_gates/precommit_offline_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["pureassertion门禁<br/>纯陈述原则阻断门禁（PURE-ASSERTION，GOV-DOC-016<br/>治本）<br/>pure_assertion_gate<br/>文件: commit_gates/pure_assertion_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["pureshim门禁<br/>（GATE-SSOT-CODE 三合一之一），``git commit<br/>--no-verify`` 绕过所有 pre-commit hooks。<br/>pure_shim_gate<br/>文件: commit_gates/pure_shim_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["r5digitsuffix门禁<br/>R5 数字后缀目录禁止门禁（治本：弥补 --no-verify<br/>绕过 pre-commit 的缺口）<br/>r5_digit_suffix_gate<br/>文件: commit_gates/r5_digit_suffix_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["协调器健康门禁<br/>直接在 GitCommitGateway.commit<br/>中调用）提升为正式 CommitGateRegistry gate。<br/>reconciler_health_gate<br/>文件: commit_gates/reconciler_health_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["relativepathliteral门禁<br/>相对路径字面量硬阻断门禁<br/>relative_path_literal_gate<br/>文件: commit_gates/relative_path_literal_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["renamedepgraphsync门禁<br/>文件重命名后 depgraph 未同步阻断门禁<br/>rename_depgraph_sync_gate<br/>文件: commit_gates/rename_depgraph_sync_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["规则执行pairing门禁<br/>规则-执行配对门禁<br/>（RULE-EXECUTION-PAIRING，Phase 3.5）<br/>rule_execution_pairing_gate<br/>文件: commit_gates<br/>/rule_execution_pairing_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["规则fourway对齐门禁<br/>规则四方对齐门禁<br/>rule_four_way_alignment_gate<br/>文件: commit_gates<br/>/rule_four_way_alignment_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["rulingcommitverified门禁<br/>文档'已完成'声明 commit hash 真实性硬验证门禁<br/>ruling_commit_verified_gate<br/>文件: commit_gates<br/>/ruling_commit_verified_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["rulingreference门禁<br/>裁定#NNN 悬空引用自动检测门禁<br/>ruling_reference_gate<br/>文件: commit_gates/ruling_reference_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["结构fileexists门禁<br/>裁定 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase<br/>1：SSoT 存在性强制。<br/>schema_file_exists_gate<br/>文件: commit_gates/schema_file_exists_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["脚本导入完整性门禁<br/>constants 符号导入完整性门禁<br/>scripts_import_integrity_gate<br/>文件: commit_gates<br/>/scripts_import_integrity_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["会话required门禁<br/>会话 注册强制门禁（SESSION-REQUIRED，2026-07-01<br/>治本 FP-ISO.4B 件1改）<br/>session_required_gate<br/>文件: commit_gates/session_required_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["快照漂移门禁<br/>运行时违规快照漂移阻断门禁<br/>（SNAPSHOT-DRIFT，#ARCH-GOV-CONVERGENCE-META<br/>Phase 3.6 补齐 rc1 enforceability）<br/>snapshot_drift_gate<br/>文件: commit_gates/snapshot_drift_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["ssotredefinition门禁<br/>SSoT 符号重复定义硬阻断门禁<br/>ssot_redefinition_gate<br/>文件: commit_gates/ssot_redefinition_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["tablename注册表门禁<br/>裁定 # Phase 4：SSoT 真源强制闭环。<br/>table_name_registry_gate<br/>文件: commit_gates/table_name_registry_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["测试源一致性门禁<br/>测试-源码符号一致性门禁<br/>（TEST-SOURCE-CONSISTENCY，§5.178 防复发）<br/>test_source_consistency_gate<br/>文件: commit_gates<br/>/test_source_consistency_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["testscoverage门禁<br/>Gate 测试覆盖率校验 meta-gate<br/>（META-TESTS-COVERAGE，）<br/>tests_coverage_gate<br/>文件: commit_gates/tests_coverage_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["存活时间门禁<br/>ttl 字段校验门禁（治本：弥补 --no-verify 绕过<br/>pre-commit GATE-15 的缺口）<br/>ttl_gate<br/>文件: commit_gates/ttl_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["undefinedname门禁<br/>UNDEFINED-NAME 门禁（F821 未定义符号硬阻断）<br/>undefined_name_gate<br/>文件: commit_gates/undefined_name_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["unsafedictspread门禁<br/>``**data`` 直接展开模式 warn 级门禁<br/>unsafe_dict_spread_gate<br/>文件: commit_gates/unsafe_dict_spread_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["vocabchain门禁<br/>SSoT 引用硬编码阻断门禁<br/>（VOCAB-CHAIN，#ARCH-GOV-CONVERGENCE-META Phase<br/>3.6 补齐 rc2 enforceability）<br/>vocab_chain_gate<br/>文件: commit_gates/vocab_chain_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["vocabhardcode门禁<br/>新增 .py 文件词表硬编码阻断门禁<br/>（VOCAB-HARDCODE，2026-07-03 Phase 1）<br/>vocab_hardcode_gate<br/>文件: commit_gates/vocab_hardcode_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["zephyrenvdirect访问门禁<br/>ZEPHYR_ENV 直访硬阻断门禁<br/>（ZEPHYR-ENV-DIRECT-ACCESS）<br/>zephyr_env_direct_access_gate<br/>文件: commit_gates<br/>/zephyr_env_direct_access_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["门禁自动registrar<br/>YAML 驱动的 in-process gate 自动注册器<br/>（#ARCH-GATE-REGISTRY-AUTO-001 Phase 3）<br/>gate_auto_registrar<br/>文件: rule_bridge/gate_auto_registrar.py<br/>(生产态 / production)"]
    tests_data_test_symbol_normalizer_py["测试symbol归一化器<br/>symbol 标准化模块测试。<br/>test_symbol_normalizer<br/>文件: data/test_symbol_normalizer.py<br/>(生产态 / production)"]
    tests_governance_commit_gates_test_check_yaml_anchor_consistency_py["commit_gates/test_check_yaml_anchor_consistency<br/>test_check_yaml_anchor_consistency.py — YAML<br/>治理锚定一致性扫描 smoke test.<br/>文件: commit_gates<br/>/test_check_yaml_anchor_consistency.py<br/>(生产态 / production)"]
    tests_governance_test_apply_dataflowgraph_smoke_py["测试applydataflowgraphsmoke<br/>治理包的test_apply_dataflowgraph_smoke模块<br/>文件: governance<br/>/test_apply_dataflowgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_decisiongraph_smoke_py["测试applydecisiongraphsmoke<br/>治理包的test_apply_decisiongraph_smoke模块<br/>文件: governance<br/>/test_apply_decisiongraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_apply_depgraph_smoke_py["测试applydepgraphsmoke<br/>#ARCH-TOOL-HEALTH-V1 Phase 4<br/>治本：核心治理工具必须有 e2e smoke test。<br/>文件: governance/test_apply_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_audit_return_contract_usage_py["测试审计returncontractusage<br/>返回契约 ok 键审计脚本单元测试<br/>test_audit_return_contract_usage<br/>文件: governance<br/>/test_audit_return_contract_usage.py<br/>(生产态 / production)"]
    tests_governance_test_audit_worktree_ops_telemetry_py["测试审计worktree运维遥测<br/>worktree_ops_log 遥测完整性审计测试<br/>test_audit_worktree_ops_telemetry<br/>文件: governance<br/>/test_audit_worktree_ops_telemetry.py<br/>(生产态 / production)"]
    tests_governance_test_generate_project_depgraph_smoke_py["测试generateprojectdepgraphsmoke<br/>治理包的test_generate_project_depgraph_smoke模块<br/>文件: governance<br/>/test_generate_project_depgraph_smoke.py<br/>(生产态 / production)"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["测试提交提交守卫no校验阈值<br/>高基数 --no-verify 阈值阻断 e2e 测试<br/>文件: governance<br/>/test_post_commit_guard_no_verify_threshold.py<br/>(生产态 / production)"]
    tests_governance_test_run_silent_failure_regression_py["测试runsilent故障regression<br/>silent-failure 回归 runner 单元测试（P3-2）<br/>test_run_silent_failure_regression<br/>文件: governance<br/>/test_run_silent_failure_regression.py<br/>(生产态 / production)"]
    tests_governance_test_session_startup_health_check_py["测试会话启动健康检查<br/>AI session 启动健康度自检单元测试<br/>test_session_startup_health_check<br/>文件: governance<br/>/test_session_startup_health_check.py<br/>(生产态 / production)"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["测试syncyamltodepgraphsmoke<br/>治理包的test_sync_yaml_to_depgraph_smoke模块<br/>文件: governance<br/>/test_sync_yaml_to_depgraph_smoke.py<br/>(生产态 / production)"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ scripts_governance_d7_code_check_yaml_anchor_consistency_py
    scripts_governance_d7_code_check_yaml_anchor_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py ~~~ src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_manager_py
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
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["安全自动修复引擎——五直接开关+五间接约束.<br/>code dedup包的auto_fixer模块<br/>文件: code_dedup/auto_fixer.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["缓存管理器<br/>Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>cache_manager<br/>文件: code_dedup/cache_manager.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_config_py["code_dedup/config<br/>配置管理 — 策略树 YAML 加载 + 项目规模感知四<br/>Tier 自适应阈值.<br/>文件: code_dedup/config.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["退出codes<br/>退出码定义模块——五档exit code<br/>0-4枚举+描述+判定逻辑.<br/>exit_codes<br/>文件: code_dedup/exit_codes.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_report_py["报告<br/>生成器 — YAML/JSON 输出 + 退出码判定 + Health<br/>Score 聚合<br/>report<br/>文件: code_dedup/report.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>盲点关闭追踪器.<br/>blind_spot_tracker<br/>文件: trackers/blind_spot_tracker.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["差异辅助<br/>门禁 共享 diff 解析工具模块<br/>_diff_helpers<br/>文件: commit_gates/_diff_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["reference辅助<br/>引用检测门禁共享工具函数<br/>_reference_helpers<br/>文件: commit_gates/_reference_helpers.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["capabilitylookup绕过策略<br/>（CAPABILITY-LOOKUP-HEALTH,<br/>priority=220）的唯一共享入口。<br/>capability_lookup_bypass_policy<br/>文件: commit_gates<br/>/capability_lookup_bypass_policy.py<br/>(生产态 / production)"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["permtrigger门禁<br/>永久系统脚本时间触发模式无事件订阅阻断门禁<br/>perm_trigger_gate<br/>文件: commit_gates/perm_trigger_gate.py<br/>(生产态 / production)"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
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
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
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
| 1 | 集成hub / integration_hub (code_dedup/integration_hub.py) | → | D_AUTONOMY_CORE 自治核心: 上下文规则注册表 / context_rule_registry (context/context... | 导入依赖 / import_depends |
| 2 | 能力一致性门禁 / capability_consistency_gate (commit_gate... | → | D_DATA 数据接入层: 能力校验器 / capability_validator (data/capability_valida... | 导入依赖 / import_depends |
| 3 | tablename注册表门禁 / table_name_registry_gate (commit_ga... | → | D_DATA 数据接入层: table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 4 | 测试symbol归一化器 / test_symbol_normalizer (data/test_sy... | → | D_DATA 数据接入层: 包入口 / __init__ (symbol_normalizer/__init__.py) | 测试依赖 / test_depends |
| 5 | 命令行 / cli (code_dedup/cli.py) | → | D_GOVERNANCE 生命周期管理: 自基准 / self_benchmark (intelligence_governance/self_ben... | 导入依赖 / import_depends |
| 6 | capabilityoverlap门禁 / capability_overlap_gate (commit_g... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 7 | 创建守卫 / create_guard (commit_gates/create_guard.py) | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 8 | 创建守卫 / create_guard (commit_gates/create_guard.py) | → | D_GOVERNANCE 生命周期管理: 规则模式 / rule_patterns (governance/rule_patterns.py) | 导入依赖 / import_depends |
| 9 | 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 10 | renamedepgraphsync门禁 / rename_depgraph_sync_gate (commi... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 导入依赖 / import_depends |
| 11 | ssotredefinition门禁 / ssot_redefinition_gate (commit_gat... | → | D_GOVERNANCE 生命周期管理: 能力lookup / capability_lookup (governance/capability_loo... | 导入依赖 / import_depends |
| 12 | 测试syncyamltodepgraphsmoke / test_sync_yaml_to_depgraph_... | → | D_GOVERNANCE 生命周期管理: 依赖图模式 / depgraph_schema (governance/depgraph_schema.py) | 测试依赖 / test_depends |
| 13 | panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 14 | 协调器健康门禁 / reconciler_health_gate (commit_gates/rec... | → | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | 导入依赖 / import_depends |
| 15 | reference辅助 / _reference_helpers (commit_gates/_referen... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 16 | archreference门禁 / arch_reference_gate (commit_gates/arc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 17 | asynciorunin上下文门禁 / asyncio_run_in_context_gate (com... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 18 | baregetenv门禁 / bare_getenv_gate (commit_gates/bare_gete... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 19 | baresql门禁 / bare_sql_gate (commit_gates/bare_sql_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 20 | baresubprocess门禁 / bare_subprocess_gate (commit_gates/b... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 21 | 蓝图amoduleconsistency门禁 / blueprint_amodule_consistenc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 22 | 蓝图amodule跨check门禁 / blueprint_amodule_cross_check_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 23 | 蓝图format门禁 / blueprint_format_gate (commit_gates/blue... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 24 | 能力一致性门禁 / capability_consistency_gate (commit_gate... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 25 | capabilitylookuprequired门禁 / capability_lookup_required... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 26 | capabilityoverlap门禁 / capability_overlap_gate (commit_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 27 | ch批次大小门禁 / ch_batch_size_gate (commit_gates/ch_batc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 28 | ch最终门禁 / ch_final_gate (commit_gates/ch_final_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 29 | ch版本col门禁 / ch_version_col_gate (commit_gates/ch_vers... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 30 | claimrequired门禁 / claim_required_gate (commit_gates/cla... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 31 | consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 32 | 创建守卫 / create_guard (commit_gates/create_guard.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 33 | danglingreference门禁 / dangling_reference_gate (commit_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 34 | 数据taskcompleteness门禁 / data_task_completeness_gate (c... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 35 | datetimenowforbidden门禁 / datetime_now_forbidden_gate (c... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 36 | depgraphfreshness门禁 / depgraph_freshness_gate (commit_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 37 | depgraphwritepath门禁 / depgraph_write_path_gate (commit_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 38 | derivationannotation门禁 / derivation_annotation_gate (co... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 39 | directorycontract门禁 / directory_contract_gate (commit_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 40 | docrefbroken门禁 / doc_ref_broken_gate (commit_gates/doc_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 41 | 域fk门禁 / domain_fk_gate (commit_gates/domain_fk_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 42 | domainnamezhdirect访问门禁 / domain_name_zh_direct_access... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 43 | empty处理器门禁 / empty_handler_gate (commit_gates/empty_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 44 | encoding门禁 / encoding_gate (commit_gates/encoding_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 45 | exemptzonefrontmatter门禁 / exempt_zone_frontmatter_gate ... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 46 | filecopy门禁 / file_copy_gate (commit_gates/file_copy_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 47 | fileplacementttl门禁 / file_placement_ttl_gate (commit_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 48 | folder容量hardlimit门禁 / folder_capacity_hard_limit_gate... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 49 | foreignchange门禁 / foreign_change_gate (commit_gates/for... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 50 | forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 51 | 函数dup门禁 / function_dup_gate (commit_gates/function_du... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 52 | Gitcall预算门禁 / git_call_budget_gate (commit_gates/git_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 53 | god类门禁 / god_class_gate (commit_gates/god_class_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 54 | hardcodedurl门禁 / hardcoded_url_gate (commit_gates/hardc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 55 | heldoverlap门禁 / held_overlap_gate (commit_gates/held_ov... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 56 | highcomplexity门禁 / high_complexity_gate (commit_gates/h... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 57 | iduniqueness门禁 / id_uniqueness_gate (commit_gates/id_un... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 58 | importdirection门禁 / import_direction_gate (commit_gates... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 59 | 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 60 | issueresolved完整性门禁 / issue_resolved_integrity_gate (... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 61 | longparamlist门禁 / long_param_list_gate (commit_gates/lo... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 62 | 手册onlypermanent门禁 / manual_only_permanent_gate (commi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 63 | MCP版本字段门禁 / mcp_version_field_gate (commit_gates/mc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 64 | 模块id一致性门禁 / module_id_consistency_gate (commit_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 65 | msg敞口门禁 / msg_exposure_gate (commit_gates/msg_exposur... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 66 | msgstyle门禁 / msg_style_gate (commit_gates/msg_style_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 67 | mutableconstwithoutfinal门禁 / mutable_const_without_fina... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 68 | 新文件依赖图门禁 / new_file_depgraph_gate (commit_gates/n... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 69 | noimportsideeffect门禁 / no_import_side_effect_gate (comm... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 70 | noqa验证门禁 / noqa_validation_gate (commit_gates/noqa_va... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 71 | openwithoutwith门禁 / open_without_with_gate (commit_gate... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 72 | 孤儿module门禁 / orphan_module_gate (commit_gates/orphan_... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 73 | panorama对齐门禁 / panorama_alignment_gate (commit_gates/... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 74 | permtrigger门禁 / perm_trigger_gate (commit_gates/perm_tr... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 75 | precommitoffline门禁 / precommit_offline_gate (commit_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 76 | pureassertion门禁 / pure_assertion_gate (commit_gates/pur... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 77 | pureshim门禁 / pure_shim_gate (commit_gates/pure_shim_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 78 | r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 79 | 协调器健康门禁 / reconciler_health_gate (commit_gates/rec... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 80 | relativepathliteral门禁 / relative_path_literal_gate (com... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 81 | renamedepgraphsync门禁 / rename_depgraph_sync_gate (commi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 82 | 规则执行pairing门禁 / rule_execution_pairing_gate (commit... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 83 | 规则fourway对齐门禁 / rule_four_way_alignment_gate (commi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 84 | rulingcommitverified门禁 / ruling_commit_verified_gate (c... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 85 | rulingreference门禁 / ruling_reference_gate (commit_gates... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 86 | 结构fileexists门禁 / schema_file_exists_gate (commit_gate... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 87 | 脚本导入完整性门禁 / scripts_import_integrity_gate (commi... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 88 | 会话required门禁 / session_required_gate (commit_gates/se... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 89 | 快照漂移门禁 / snapshot_drift_gate (commit_gates/snapshot... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 90 | ssotredefinition门禁 / ssot_redefinition_gate (commit_gat... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 91 | tablename注册表门禁 / table_name_registry_gate (commit_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 92 | 测试源一致性门禁 / test_source_consistency_gate (commit_g... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 93 | testscoverage门禁 / tests_coverage_gate (commit_gates/tes... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 94 | 存活时间门禁 / ttl_gate (commit_gates/ttl_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 95 | undefinedname门禁 / undefined_name_gate (commit_gates/und... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 96 | unsafedictspread门禁 / unsafe_dict_spread_gate (commit_ga... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 97 | vocabchain门禁 / vocab_chain_gate (commit_gates/vocab_cha... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 98 | vocabhardcode门禁 / vocab_hardcode_gate (commit_gates/voc... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 99 | zephyrenvdirect访问门禁 / zephyr_env_direct_access_gate (... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 100 | 门禁自动registrar / gate_auto_registrar (rule_bridge/gate... | → | D_GOV_ENFORCEMENT 规则执行: 提交门禁注册表 / commit_gate_registry (rule_bridge/commit... | 导入依赖 / import_depends |
| 101 | 测试审计worktree运维遥测 / test_audit_worktree_ops_teleme... | → | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | 测试依赖 / test_depends |
| 102 | 检查模块id一致性 / check_module_id_consistency (d7_code/c... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 导入依赖 / import_depends |
| 103 | 配置 / config (code_dedup/config.py) | → | D_INFRASTRUCTURE 跨层契约基础设施: 应用配置 / app_config (config/app_config.py) | 导入依赖 / import_depends |
| 104 | 命令行 / cli (code_dedup/cli.py) | → | D_INFRA_RUNTIME 运行时集成: 扫描器 / scanner (asset_inventory/scanner.py) | 导入依赖 / import_depends |
| 105 | forgedgwmarker门禁 / forged_gw_marker_gate (commit_gates/... | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 106 | 导入完整性门禁 / import_integrity_gate (commit_gates/impo... | → | D_SECURITY 对抗验证: 会话并发 / session_concurrency (access_control/session_co... | 导入依赖 / import_depends |
| 107 | 缓存管理器 / cache_manager (code_dedup/cache_manager.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 108 | 差异检测器 / diff_detector (code_dedup/diff_detector.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 109 | reference辅助 / _reference_helpers (commit_gates/_referen... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 110 | baregetenv门禁 / bare_getenv_gate (commit_gates/bare_gete... | → | D_SHARED 共享服务: 密钥 / secrets (security/secrets.py) | 导入依赖 / import_depends |
| 111 | 蓝图format门禁 / blueprint_format_gate (commit_gates/blue... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 112 | capabilitylookuprequired门禁 / capability_lookup_required... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 113 | 创建守卫 / create_guard (commit_gates/create_guard.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 114 | 数据taskcompleteness门禁 / data_task_completeness_gate (c... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 115 | encoding门禁 / encoding_gate (commit_gates/encoding_gate.py) | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 116 | exemptzonefrontmatter门禁 / exempt_zone_frontmatter_gate ... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 117 | 门禁repo / gate_repo (commit_gates/gate_repo.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 118 | 门禁repo / gate_repo (commit_gates/gate_repo.py) | → | D_SHARED 共享服务: 数据库工具 / db_utils (utils/db_utils.py) | 导入依赖 / import_depends |
| 119 | pureassertion门禁 / pure_assertion_gate (commit_gates/pur... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 120 | pureshim门禁 / pure_shim_gate (commit_gates/pure_shim_gat... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 121 | r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 122 | rulingcommitverified门禁 / ruling_commit_verified_gate (c... | → | D_SHARED 共享服务: 进程池 / process_pool.py - Shared process pool for MCP se... | 导入依赖 / import_depends |
| 123 | 脚本导入完整性门禁 / scripts_import_integrity_gate (commi... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 124 | 测试源一致性门禁 / test_source_consistency_gate (commit_g... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 125 | 门禁自动registrar / gate_auto_registrar (rule_bridge/gate... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: 自基准 / self_benchmark (intelligence_governance/self_ben... | → | ast比较器 / ast_comparator (code_dedup/ast_comparator.py) | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: 自基准 / self_benchmark (intelligence_governance/self_ben... | → | behavioral采样器 / behavioral_sampler (code_dedup/behavio... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: 自基准 / self_benchmark (intelligence_governance/self_ben... | → | microclone检测器 / micro_clone_detector (code_dedup/micro... | 导入依赖 / import_depends |
| 4 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | reference辅助 / _reference_helpers (commit_gates/_referen... | 导入依赖 / import_depends |
| 5 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | capabilitylookup绕过策略 / capability_lookup_bypass_polic... | 导入依赖 / import_depends |
| 6 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | 脚本导入完整性门禁 / scripts_import_integrity_gate (commi... | 导入依赖 / import_depends |
| 8 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | undefinedname门禁 / undefined_name_gate (commit_gates/und... | 导入依赖 / import_depends |
| 9 | D_GOV_AUDIT 审计追踪: 对账注册表 / reconciliation_registry (audit/reconciliatio... | → | 门禁自动registrar / gate_auto_registrar (rule_bridge/gate... | 导入依赖 / import_depends |
| 10 | D_GOV_ENFORCEMENT 规则执行: Git提交网关 / git_commit_gateway (rule_bridge/git_commit_... | → | 门禁自动registrar / gate_auto_registrar (rule_bridge/gate... | 导入依赖 / import_depends |
| 11 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | 包入口 / __init__ (commit_gates/__init__.py) | 导入依赖 / import_depends |
| 12 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | capabilitylookuprequired门禁 / capability_lookup_required... | 导入依赖 / import_depends |
| 13 | D_GOV_ENFORCEMENT 规则执行: 会话worktree / session_worktree (rule_bridge/session_work... | → | 测试源一致性门禁 / test_source_consistency_gate (commit_g... | 导入依赖 / import_depends |
| 14 | D_GOV_ENFORCEMENT 规则执行: 测试创建守卫 / test_create_guard (commit_gates/test_creat... | → | 创建守卫 / create_guard (commit_gates/create_guard.py) | 测试依赖 / test_depends |
| 15 | D_GOV_ENFORCEMENT 规则执行: 测试r5digitsuffix门禁 / test_r5_digit_suffix_gate (commit... | → | r5digitsuffix门禁 / r5_digit_suffix_gate (commit_gates/r5... | 测试依赖 / test_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: 扫描消费者accuracy / scan_consumers_accuracy (d7_code/sca... | → | 差异辅助 / _diff_helpers (commit_gates/_diff_helpers.py) | 导入依赖 / import_depends |
| 17 | D_GOV_SCRIPTS 脚本治理: 扫描消费者accuracy / scan_consumers_accuracy (d7_code/sca... | → | consumersaccuracy门禁 / consumers_accuracy_gate (commit_g... | 导入依赖 / import_depends |

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
