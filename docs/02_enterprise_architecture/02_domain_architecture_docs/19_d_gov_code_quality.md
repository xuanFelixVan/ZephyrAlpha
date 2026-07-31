---
doc_type: architecture_view
title: D_GOV_CODE_QUALITY 代码质量治理架构文档
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 19_d_gov_code_quality / 代码质量治理 / Code Quality Governance

> **功能简介 / Overview**: 代码质量治理，负责代码去重引擎、函数重复检测、AST语义分析和提交门禁引擎

> **文档作用 / Purpose**: 展示 代码质量治理（D_GOV_CODE_QUALITY）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

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
| 跨域出边 | 124 | Cross-domain Outgoing | 124 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 169 | Production Modules | 169 |
| 容量 | 169/150 (超容) | Capacity | 169/150 (超容) |
| 描述 | 代码去重引擎(code_dedup) | Description | 代码去重引擎(code_dedup) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 169 个模块 / 169 modules）。

### L1 基础层 / Foundation Layer (169 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | scripts/governance/d3_metadata/check_pure_assertion.py | check_pure_assertion.py — GOV-DOC-016 纯陈述原... | 生产态 / production |  |
| 2 | scripts/governance/d7_code/check_module_id_consistency.py | check_module_id_consistency.py — module_id 全... | 生产态 / production |  |
| 3 | src/zephyr/gov_code_quality/__init__.py | gov_code_quality domain package — code quality... | 生产态 / production |  |
| 4 | src/zephyr/gov_code_quality/code_dedup/__init__.py | code-dedup-engine 子包 — 重复代码检测与治理引擎. | 生产态 / production |  |
| 5 | src/zephyr/gov_code_quality/code_dedup/annotations.py | 共享函数注解引擎 — @shared / @known_dup / @int... | 生产态 / production |  |
| 6 | src/zephyr/gov_code_quality/code_dedup/ast_comparator.py | Stage 2: AST 级精确比对器. | 生产态 / production |  |
| 7 | src/zephyr/gov_code_quality/code_dedup/atomic_fixer.py | 原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOIN... | 生产态 / production |  |
| 8 | src/zephyr/gov_code_quality/code_dedup/auto_fixer.py | 安全自动修复引擎——五直接开关+五间接约束. | 生产态 / production |  |
| 9 | src/zephyr/gov_code_quality/code_dedup/behavioral_sampler.py | 行为采样验证器 — Stage 0.25 低成本快速验证. | 生产态 / production |  |
| 10 | src/zephyr/gov_code_quality/code_dedup/behavioral_trust_c... | 行为信任检查器 — 行为漂移DIVERGED检测. | 生产态 / production |  |
| 11 | src/zephyr/gov_code_quality/code_dedup/cache_manager.py | Stage 0: 函数缓存管理器 — 增量扫描的加速核心. | 生产态 / production |  |
| 12 | src/zephyr/gov_code_quality/code_dedup/canary_manager.py | 金丝雀工厂——生成已知oracle 文件 用于引擎检出+... | 生产态 / production |  |
| 13 | src/zephyr/gov_code_quality/code_dedup/canary_register.py | 金丝雀注册表维护器 — 注册/过期/腐败检测. | 生产态 / production |  |
| 14 | src/zephyr/gov_code_quality/code_dedup/cli.py | code-dedup-engine CLI——子命令映射+退出码+扫描入口. | 生产态 / production |  |
| 15 | src/zephyr/gov_code_quality/code_dedup/code_analyzer_runn... | 检查运行器——按照敏感基线运行三阶段+导出 yaml 报告. | 生产态 / production |  |
| 16 | src/zephyr/gov_code_quality/code_dedup/code_simulator.py | 代码模拟器——播放录制的克隆演化序列，stress-te... | 生产态 / production |  |
| 17 | src/zephyr/gov_code_quality/code_dedup/config.py | 配置管理 — 策略树 YAML 加载 + 项目规模感知四 T... | 生产态 / production |  |
| 18 | src/zephyr/gov_code_quality/code_dedup/contract_consisten... | API契约一致性检查器 — 存在性·行为·契约三维. | 生产态 / production |  |
| 19 | src/zephyr/gov_code_quality/code_dedup/cross_boundary_det... | 跨边界克隆感知——四大边界差异化检测+独立策略+... | 生产态 / production |  |
| 20 | src/zephyr/gov_code_quality/code_dedup/dead_module_detect... | 死共享模块检测器 — shared/子模块无人使用 -> DEAD. | 生产态 / production |  |
| 21 | src/zephyr/gov_code_quality/code_dedup/debt_projector.py | 去重债务预测器 — weeks_to_payoff + intake_rate... | 生产态 / production |  |
| 22 | src/zephyr/gov_code_quality/code_dedup/decision_auditor.py | 决策审计链 — DecisionFingerprint 不可变追加日志. | 生产态 / production |  |
| 23 | src/zephyr/gov_code_quality/code_dedup/degradation.py | 降级运行管理器 — 各 Stage 独立 try/except + de... | 生产态 / production |  |
| 24 | src/zephyr/gov_code_quality/code_dedup/diff_detector.py | Stage 0: Git diff 变更检测器 — 函数粒度增量. | 生产态 / production |  |
| 25 | src/zephyr/gov_code_quality/code_dedup/doom_loop_guard.py | Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机. | 生产态 / production |  |
| 26 | src/zephyr/gov_code_quality/code_dedup/exit_codes.py | 退出码定义模块——五档exit code 0-4枚举+描述+判... | 生产态 / production |  |
| 27 | src/zephyr/gov_code_quality/code_dedup/extraction_safety.py | 安全提取适配性评估器 — Suitability Score 0-100... | 生产态 / production |  |
| 28 | src/zephyr/gov_code_quality/code_dedup/false_negative_aud... | 三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Sam... | 生产态 / production |  |
| 29 | src/zephyr/gov_code_quality/code_dedup/fifteen_dimension_... | 15维超综合审计首页 — 逐项证明"做过且做对". | 生产态 / production |  |
| 30 | src/zephyr/gov_code_quality/code_dedup/file_creator.py | 文件创建清单执行器 — 验证所有源/测试/数据文件... | 生产态 / production |  |
| 31 | src/zephyr/gov_code_quality/code_dedup/function_discovery.py | 共享函数主动发现 — 签名+语义双通道从被动到主动. | 生产态 / production |  |
| 32 | src/zephyr/gov_code_quality/code_dedup/grandfather_manage... | Grandfather 三定律 — 古老重复管理. | 生产态 / production |  |
| 33 | src/zephyr/gov_code_quality/code_dedup/health_monitor.py | 健康仪表盘 — Dedup Health Score 0-100 + 趋势 +... | 生产态 / production |  |
| 34 | src/zephyr/gov_code_quality/code_dedup/integration_hub.py | 集成协调器 — 24集成+19更新+16GitHub整合. | 生产态 / production |  |
| 35 | src/zephyr/gov_code_quality/code_dedup/integrations.py | 集成管理——预提交钩子+CI-only 扫描+超时边界. | 生产态 / production |  |
| 36 | src/zephyr/gov_code_quality/code_dedup/micro_clone_detect... | 微型克隆检测器 — n-gram频率计数, 1-2行高频模式... | 生产态 / production |  |
| 37 | src/zephyr/gov_code_quality/code_dedup/mock_duplicate_gen... | 可控克隆生产器——零假阳性可期待引擎分子离散 | 生产态 / production |  |
| 38 | src/zephyr/gov_code_quality/code_dedup/monoculture_guard.py | Monoculture 免疫 — BRS 0-100 + 去重悖论检测. | 生产态 / production |  |
| 39 | src/zephyr/gov_code_quality/code_dedup/observation_window... | 提取后稳定观察期守护 — 对标SDP 14天观察. | 生产态 / production |  |
| 40 | src/zephyr/gov_code_quality/code_dedup/path_index_validat... | 路径索引验证——验证 config 数据集相对路径表与... | 生产态 / production |  |
| 41 | src/zephyr/gov_code_quality/code_dedup/phase_executor.py | 6Phase施工执行器 — Phase 0~5 执行状态追踪. | 生产态 / production |  |
| 42 | src/zephyr/gov_code_quality/code_dedup/policy_tree_valida... | 策略树自动一致性校验器 — 虚线箭头影响分析. | 生产态 / production |  |
| 43 | src/zephyr/gov_code_quality/code_dedup/pre_apply_integrit... | Pre-Apply 完整性门 — SHA256重新验证. | 生产态 / production |  |
| 44 | src/zephyr/gov_code_quality/code_dedup/prioritizer.py | 修复优先级排序器 — 置信度×Impact×适配性 三因... | 生产态 / production |  |
| 45 | src/zephyr/gov_code_quality/code_dedup/recovery_manifest_... | Recovery Manifest Writer — R2纯文本base64 Mani... | 生产态 / production |  |
| 46 | src/zephyr/gov_code_quality/code_dedup/report.py | 报告生成器 — YAML/JSON 输出 + 退出码判定 + Hea... | 生产态 / production |  |
| 47 | src/zephyr/gov_code_quality/code_dedup/risk_mitigator.py | R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + ... | 生产态 / production |  |
| 48 | src/zephyr/gov_code_quality/code_dedup/self_scanner.py | 引擎自扫描器 — Dogfooding 检测引擎自身源码重复. | 生产态 / production |  |
| 49 | src/zephyr/gov_code_quality/code_dedup/sensitivity_sweepe... | 敏感性扫荡——threshold扫描->固化成new baseline... | 生产态 / production |  |
| 50 | src/zephyr/gov_code_quality/code_dedup/shadow_trust_valid... | 影子信任验证器 — ImportError 防护回路. | 生产态 / production |  |
| 51 | src/zephyr/gov_code_quality/code_dedup/shadow_verifier.py | 影子清单验证器 — size sanity check + semantic... | 生产态 / production |  |
| 52 | src/zephyr/gov_code_quality/code_dedup/shared_evolver.py | 共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定. | 生产态 / production |  |
| 53 | src/zephyr/gov_code_quality/code_dedup/shared_lifecycle_m... | 共享函数生命周期管理 — Active->Deprecated->Gra... | 生产态 / production |  |
| 54 | src/zephyr/gov_code_quality/code_dedup/signature_matcher.py | Stage 0.5: 签名指纹 SHA256[:12] O(1) 精确匹配. | 生产态 / production |  |
| 55 | src/zephyr/gov_code_quality/code_dedup/simplicity_auditor.py | 引擎成本效益自审计器 — SAS 0-100 月度审计 + Ta... | 生产态 / production |  |
| 56 | src/zephyr/gov_code_quality/code_dedup/ssot_registrar.py | SSoT注册器 — 提取函数自动注册到 shared API清单. | 生产态 / production |  |
| 57 | src/zephyr/gov_code_quality/code_dedup/stale_shared_detec... | 过时共享函数检测器 — 无caller × 30天 -> STALE标记. | 生产态 / production |  |
| 58 | src/zephyr/gov_code_quality/code_dedup/success_validator.py | 成功验证——判断一次去重操作是否真正消灭了克隆. | 生产态 / production |  |
| 59 | src/zephyr/gov_code_quality/code_dedup/symbol_index.py | 符号索引 — 全局函数/类/import映射表. | 生产态 / production |  |
| 60 | src/zephyr/gov_code_quality/code_dedup/thematic_clusterer.py | 主题聚类器 — 噪声信号比·告警疲劳缓解. | 生产态 / production |  |
| 61 | src/zephyr/gov_code_quality/code_dedup/trackers/__init__.py | tracker 族子包 — 风险/盲点/热点跟踪器集合. | 生产态 / production |  |
| 62 | src/zephyr/gov_code_quality/code_dedup/trackers/blind_spo... | 盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖. | 生产态 / production |  |
| 63 | src/zephyr/gov_code_quality/code_dedup/trackers/consequen... | 后果追踪——记录每次修复操作对依赖方的影响. | 生产态 / production |  |
| 64 | src/zephyr/gov_code_quality/code_dedup/trackers/hotspot_t... | 热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新... | 生产态 / production |  |
| 65 | src/zephyr/gov_code_quality/code_dedup/trackers/import_su... | Import表面积负债追踪 — SBS 0-100 + shared burd... | 生产态 / production |  |
| 66 | src/zephyr/gov_code_quality/code_dedup/trackers/question_... | 问题追踪——扫描中发现需要人工处理的问题. | 生产态 / production |  |
| 67 | src/zephyr/gov_code_quality/code_dedup/trackers/risk_miti... | 风险缓解追踪——捕获哪些克隆报告了但在N次扫描后... | 生产态 / production |  |
| 68 | src/zephyr/gov_code_quality/code_dedup/verifier.py | 修复验证器 — import + 类型 + 行为采样验证. | 生产态 / production |  |
| 69 | src/zephyr/gov_enforcement/commit_gates/__init__.py | commit_gates — GitCommitGateway pre-commit 门... | 生产态 / production |  |
| 70 | src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py | _diff_helpers.py — gate 共享 diff 解析工具模块 | 生产态 / production |  |
| 71 | src/zephyr/gov_enforcement/commit_gates/_reference_helper... | _reference_helpers.py — 引用检测门禁共享工具函... | 生产态 / production |  |
| 72 | src/zephyr/gov_enforcement/commit_gates/arch_reference_ga... | arch_reference_gate.py — #ARCH-NNN /... | 生产态 / production |  |
| 73 | src/zephyr/gov_enforcement/commit_gates/asyncio_run_in_co... | asyncio_run_in_context_gate.py — 异步上下文误... | 生产态 / production |  |
| 74 | src/zephyr/gov_enforcement/commit_gates/bare_getenv_gate.py | bare_getenv_gate.py — 裸 os.getenv 读密钥阻断... | 生产态 / production |  |
| 75 | src/zephyr/gov_enforcement/commit_gates/bare_sql_gate.py | bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BAR... | 生产态 / production |  |
| 76 | src/zephyr/gov_enforcement/commit_gates/bare_subprocess_g... | bare_subprocess_gate.py — 裸 subprocess 调用硬... | 生产态 / production |  |
| 77 | src/zephyr/gov_enforcement/commit_gates/blueprint_amodule... | blueprint_amodule_consistency_gate.py — [A_mod... | 生产态 / production |  |
| 78 | src/zephyr/gov_enforcement/commit_gates/blueprint_amodule... | blueprint_amodule_cross_check_gate.py — [BLUEP... | 生产态 / production |  |
| 79 | src/zephyr/gov_enforcement/commit_gates/blueprint_format_... | blueprint_format_gate.py — [BLUEPRINT] 头部 mo... | 生产态 / production |  |
| 80 | src/zephyr/gov_enforcement/commit_gates/capability_consis... | capability_consistency_gate.py — Provider 路由... | 生产态 / production |  |
| 81 | src/zephyr/gov_enforcement/commit_gates/capability_lookup... | capability_lookup_bypass_policy.py — CAPABILIT... | 生产态 / production |  |
| 82 | src/zephyr/gov_enforcement/commit_gates/capability_lookup... | capability_lookup_required_gate.py — Capabilit... | 生产态 / production |  |
| 83 | src/zephyr/gov_enforcement/commit_gates/capability_overla... | capability_overlap_gate.py — 新建 .py 文件 Cap... | 生产态 / production |  |
| 84 | src/zephyr/gov_enforcement/commit_gates/ch_batch_size_gat... | ch_batch_size_gate.py — CH 批量写入防回退门禁... | 生产态 / production |  |
| 85 | src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py | ch_final_gate.py — ch_writer.query() 直接调用... | 生产态 / production |  |
| 86 | src/zephyr/gov_enforcement/commit_gates/ch_version_col_ga... | ch_version_col_gate.py — CH version 列语义误用... | 生产态 / production |  |
| 87 | src/zephyr/gov_enforcement/commit_gates/claim_required_ga... | claim_required_gate.py — claim_files 前置检查... | 生产态 / production |  |
| 88 | src/zephyr/gov_enforcement/commit_gates/consumers_accurac... | consumers_accuracy_gate.py — CONSUMERS 字段准... | 生产态 / production |  |
| 89 | src/zephyr/gov_enforcement/commit_gates/create_guard.py | create_guard.py — 新建 .py / 非 rules/ .yaml ... | 生产态 / production |  |
| 90 | src/zephyr/gov_enforcement/commit_gates/dangling_referenc... | dangling_reference_gate.py — AGENTS.md §X.Y ... | 生产态 / production |  |
| 91 | src/zephyr/gov_enforcement/commit_gates/data_task_complet... | data_task_completeness_gate.py — 数据任务完整... | 生产态 / production |  |
| 92 | src/zephyr/gov_enforcement/commit_gates/datetime_now_forb... | datetime_now_forbidden_gate.py — 时间戳约定硬... | 生产态 / production |  |
| 93 | src/zephyr/gov_enforcement/commit_gates/depgraph_freshnes... | depgraph_freshness_gate.py — depgraph 新鲜度门... | 生产态 / production |  |
| 94 | src/zephyr/gov_enforcement/commit_gates/depgraph_write_pa... | depgraph_write_path_gate.py — depgraph 写入路... | 生产态 / production |  |
| 95 | src/zephyr/gov_enforcement/commit_gates/derivation_annota... | derivation_annotation_gate.py — 派生关系声明真... | 生产态 / production |  |
| 96 | src/zephyr/gov_enforcement/commit_gates/directory_contrac... | directory_contract_gate.py — DCR-001~007 等效... | 生产态 / production |  |
| 97 | src/zephyr/gov_enforcement/commit_gates/doc_ref_broken_ga... | doc_ref_broken_gate.py — 文档相对路径断裂引用... | 生产态 / production |  |
| 98 | src/zephyr/gov_enforcement/commit_gates/domain_fk_gate.py | domain_fk_gate.py — [DOMAIN] 头部域注册表 FK ... | 生产态 / production |  |
| 99 | src/zephyr/gov_enforcement/commit_gates/domain_name_zh_di... | domain_name_zh_direct_access_gate.py — DOMAIN_... | 生产态 / production |  |
| 100 | src/zephyr/gov_enforcement/commit_gates/empty_handler_gat... | empty_handler_gate.py — 空事件 handler 函数阻... | 生产态 / production |  |
| 101 | src/zephyr/gov_enforcement/commit_gates/encoding_gate.py | encoding_gate.py — 编码安全校验门禁（治本：弥... | 生产态 / production |  |
| 102 | src/zephyr/gov_enforcement/commit_gates/exempt_zone_front... | exempt_zone_frontmatter_gate.py — 豁免区 front... | 生产态 / production |  |
| 103 | src/zephyr/gov_enforcement/commit_gates/file_copy_gate.py | file_copy_gate.py — 新增 .py 文件复制检测阻断... | 生产态 / production |  |
| 104 | src/zephyr/gov_enforcement/commit_gates/file_placement_tt... | file_placement_ttl_gate.py — 文件放置与 TTL 一... | 生产态 / production |  |
| 105 | src/zephyr/gov_enforcement/commit_gates/folder_capacity_h... | folder_capacity_hard_limit_gate.py — 文件夹容... | 生产态 / production |  |
| 106 | src/zephyr/gov_enforcement/commit_gates/foreign_change_ga... | foreign_change_gate.py — 外来变更检测门禁（FOR... | 生产态 / production |  |
| 107 | src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_... | forged_gw_marker_gate.py — Forged GW Marker 前... | 生产态 / production |  |
| 108 | src/zephyr/gov_enforcement/commit_gates/function_dup_gate.py | function_dup_gate.py — 重复函数实现阻断门禁（F... | 生产态 / production |  |
| 109 | src/zephyr/gov_enforcement/commit_gates/gate_repo.py | gate_repo.py — gates 表持久化仓库（AUDIT-07 P1... | 生产态 / production |  |
| 110 | src/zephyr/gov_enforcement/commit_gates/git_call_budget_g... | git_call_budget_gate.py — Git 调用预算 warn-on... | 生产态 / production |  |
| 111 | src/zephyr/gov_enforcement/commit_gates/god_class_gate.py | god_class_gate.py — God Class 阻断门禁（NO-GOD... | 生产态 / production |  |
| 112 | src/zephyr/gov_enforcement/commit_gates/hardcoded_url_gat... | hardcoded_url_gate.py — 硬编码 localhost URL ... | 生产态 / production |  |
| 113 | src/zephyr/gov_enforcement/commit_gates/held_overlap_gate.py | held_overlap_gate.py — 搭便车防护门禁（HELD-OV... | 生产态 / production |  |
| 114 | src/zephyr/gov_enforcement/commit_gates/high_complexity_g... | high_complexity_gate.py — 高循环复杂度阻断门禁... | 生产态 / production |  |
| 115 | src/zephyr/gov_enforcement/commit_gates/id_uniqueness_gat... | id_uniqueness_gate.py — pre-commit hook ID 唯... | 生产态 / production |  |
| 116 | src/zephyr/gov_enforcement/commit_gates/import_direction_... | import_direction_gate.py — shared 层向上依赖阻... | 生产态 / production |  |
| 117 | src/zephyr/gov_enforcement/commit_gates/import_integrity_... | import_integrity_gate.py — IMPORT-INTEGRITY 门... | 生产态 / production |  |
| 118 | src/zephyr/gov_enforcement/commit_gates/issue_resolved_in... | issue_resolved_integrity_gate.py — ISSUE-RESOL... | 生产态 / production |  |
| 119 | src/zephyr/gov_enforcement/commit_gates/long_param_list_g... | long_param_list_gate.py — 长参数列表阻断门禁（... | 生产态 / production |  |
| 120 | src/zephyr/gov_enforcement/commit_gates/manual_only_perma... | manual_only_permanent_gate.py — 永久系统脚本 m... | 生产态 / production |  |
| 121 | src/zephyr/gov_enforcement/commit_gates/mcp_version_field... | mcp_version_field_gate.py — MCP version 字段缺... | 生产态 / production |  |
| 122 | src/zephyr/gov_enforcement/commit_gates/module_id_consist... | module_id_consistency_gate.py — module_id 三声... | 生产态 / production |  |
| 123 | src/zephyr/gov_enforcement/commit_gates/msg_exposure_gate.py | msg_exposure_gate.py — 错误消息暴露敏感信息阻... | 生产态 / production |  |
| 124 | src/zephyr/gov_enforcement/commit_gates/msg_style_gate.py | msg_style_gate.py — 错误消息标点/箭头风格阻断... | 生产态 / production |  |
| 125 | src/zephyr/gov_enforcement/commit_gates/mutable_const_wit... | mutable_const_without_final_gate.py — 可变常量... | 生产态 / production |  |
| 126 | src/zephyr/gov_enforcement/commit_gates/new_file_depgraph... | new_file_depgraph_gate.py — 新建 .py 文件 depg... | 生产态 / production |  |
| 127 | src/zephyr/gov_enforcement/commit_gates/no_import_side_ef... | no_import_side_effect_gate.py — 模块导入零副作... | 生产态 / production |  |
| 128 | src/zephyr/gov_enforcement/commit_gates/noqa_validation_g... | noqa_validation_gate.py — 自定义 noqa 标记合规... | 生产态 / production |  |
| 129 | src/zephyr/gov_enforcement/commit_gates/open_without_with... | open_without_with_gate.py — open() 未在 with ... | 生产态 / production |  |
| 130 | src/zephyr/gov_enforcement/commit_gates/orphan_module_gat... | orphan_module_gate.py — 孤儿模块（无 import 引... | 生产态 / production |  |
| 131 | src/zephyr/gov_enforcement/commit_gates/panorama_alignmen... | panorama_alignment_gate.py — 三图模块对齐门禁... | 生产态 / production |  |
| 132 | src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py | perm_trigger_gate.py — 永久系统脚本时间触发模... | 生产态 / production |  |
| 133 | src/zephyr/gov_enforcement/commit_gates/precommit_offline... | precommit_offline_gate.py — pre-commit 配置离... | 生产态 / production |  |
| 134 | src/zephyr/gov_enforcement/commit_gates/pure_assertion_ga... | pure_assertion_gate.py — 纯陈述原则阻断门禁（P... | 生产态 / production |  |
| 135 | src/zephyr/gov_enforcement/commit_gates/pure_shim_gate.py | pure_shim_gate.py — 纯 re-export shim 阻断门禁... | 生产态 / production |  |
| 136 | src/zephyr/gov_enforcement/commit_gates/r5_digit_suffix_g... | r5_digit_suffix_gate.py — R5 数字后缀目录禁止... | 生产态 / production |  |
| 137 | src/zephyr/gov_enforcement/commit_gates/reconciler_health... | reconciler_health_gate.py — reconciler 健康度... | 生产态 / production |  |
| 138 | src/zephyr/gov_enforcement/commit_gates/relative_path_lit... | relative_path_literal_gate.py — 相对路径字面量... | 生产态 / production |  |
| 139 | src/zephyr/gov_enforcement/commit_gates/rename_depgraph_s... | rename_depgraph_sync_gate.py — 文件重命名后 de... | 生产态 / production |  |
| 140 | src/zephyr/gov_enforcement/commit_gates/rule_execution_pa... | rule_execution_pairing_gate.py — 规则-执行配对... | 生产态 / production |  |
| 141 | src/zephyr/gov_enforcement/commit_gates/rule_four_way_ali... | rule_four_way_alignment_gate.py — 规则四方对齐... | 生产态 / production |  |
| 142 | src/zephyr/gov_enforcement/commit_gates/ruling_commit_ver... | ruling_commit_verified_gate.py — 文档"已完成"... | 生产态 / production |  |
| 143 | src/zephyr/gov_enforcement/commit_gates/ruling_reference_... | ruling_reference_gate.py — 裁定#NNN 悬空引用自... | 生产态 / production |  |
| 144 | src/zephyr/gov_enforcement/commit_gates/schema_file_exist... | schema_file_exists_gate.py — SCHEMA-FILE-EXIST... | 生产态 / production |  |
| 145 | src/zephyr/gov_enforcement/commit_gates/scripts_import_in... | scripts_import_integrity_gate.py — _shared.con... | 生产态 / production |  |
| 146 | src/zephyr/gov_enforcement/commit_gates/session_required_... | session_required_gate.py — session 注册强制门... | 生产态 / production |  |
| 147 | src/zephyr/gov_enforcement/commit_gates/snapshot_drift_ga... | snapshot_drift_gate.py — 运行时违规快照漂移阻... | 生产态 / production |  |
| 148 | src/zephyr/gov_enforcement/commit_gates/ssot_redefinition... | ssot_redefinition_gate.py — SSoT 符号重复定义... | 生产态 / production |  |
| 149 | src/zephyr/gov_enforcement/commit_gates/table_name_regist... | table_name_registry_gate.py — TABLE-NAME-REGIS... | 生产态 / production |  |
| 150 | src/zephyr/gov_enforcement/commit_gates/test_source_consi... | test_source_consistency_gate.py — 测试-源码符... | 生产态 / production |  |
| 151 | src/zephyr/gov_enforcement/commit_gates/tests_coverage_ga... | tests_coverage_gate.py — Gate 测试覆盖率校验 m... | 生产态 / production |  |
| 152 | src/zephyr/gov_enforcement/commit_gates/ttl_gate.py | ttl_gate.py — ttl 字段校验门禁（治本：弥补 --n... | 生产态 / production |  |
| 153 | src/zephyr/gov_enforcement/commit_gates/undefined_name_ga... | undefined_name_gate.py — UNDEFINED-NAME 门禁（... | 生产态 / production |  |
| 154 | src/zephyr/gov_enforcement/commit_gates/unsafe_dict_sprea... | unsafe_dict_spread_gate.py — ``**data`` 直接展... | 生产态 / production |  |
| 155 | src/zephyr/gov_enforcement/commit_gates/vocab_chain_gate.py | vocab_chain_gate.py — SSoT 引用硬编码阻断门禁... | 生产态 / production |  |
| 156 | src/zephyr/gov_enforcement/commit_gates/vocab_hardcode_ga... | vocab_hardcode_gate.py — 新增 .py 文件词表硬编... | 生产态 / production |  |
| 157 | src/zephyr/gov_enforcement/commit_gates/zephyr_env_direct... | zephyr_env_direct_access_gate.py — ZEPHYR_ENV ... | 生产态 / production |  |
| 158 | src/zephyr/gov_enforcement/rule_bridge/gate_auto_registra... | gate_auto_registrar.py — YAML 驱动的 in-proces... | 生产态 / production |  |
| 159 | tests/data/test_symbol_normalizer.py | test_symbol_normalizer.py — TRAE-082 symbol 标... | 生产态 / production |  |
| 160 | tests/governance/test_apply_dataflowgraph_smoke.py | test_apply_dataflowgraph_smoke.py — apply_data... | 生产态 / production |  |
| 161 | tests/governance/test_apply_decisiongraph_smoke.py | test_apply_decisiongraph_smoke.py — apply_deci... | 生产态 / production |  |
| 162 | tests/governance/test_apply_depgraph_smoke.py | test_apply_depgraph_smoke.py — apply_depgraph.... | 生产态 / production |  |
| 163 | tests/governance/test_audit_return_contract_usage.py | test_audit_return_contract_usage.py — 返回契约... | 生产态 / production |  |
| 164 | tests/governance/test_audit_worktree_ops_telemetry.py | test_audit_worktree_ops_telemetry.py — worktre... | 生产态 / production |  |
| 165 | tests/governance/test_generate_project_depgraph_smoke.py | test_generate_project_depgraph_smoke.py — gene... | 生产态 / production |  |
| 166 | tests/governance/test_post_commit_guard_no_verify_thresho... | test_post_commit_guard_no_verify_threshold.py ... | 生产态 / production |  |
| 167 | tests/governance/test_run_silent_failure_regression.py | test_run_silent_failure_regression.py — silent... | 生产态 / production |  |
| 168 | tests/governance/test_session_startup_health_check.py | test_session_startup_health_check.py — AI sess... | 生产态 / production |  |
| 169 | tests/governance/test_sync_yaml_to_depgraph_smoke.py | test_sync_yaml_to_depgraph_smoke.py — sync_yam... | 生产态 / production |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 169 个模块（生产态 169 + 设计态 0），标签标注成熟度。

#### 第 1 页 / 共 6 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["(生产态 / production) check_pure_assertion.py — GOV-DOC-016 纯陈述原...<br/>文件: check_pure_assertion.py"]
    scripts_governance_d7_code_check_module_id_consistency_py["(生产态 / production) check_module_id_consistency.py — module_id 全...<br/>文件: check_module_id_consistency.py"]
    src_zephyr_gov_code_quality_init_py["(生产态 / production) gov_code_quality domain package — code quality...<br/>文件: __init__.py"]
    src_zephyr_gov_code_quality_code_dedup_init_py["(生产态 / production) code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: __init__.py"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py["(生产态 / production) 共享函数注解引擎 — @shared / @known_dup / @int...<br/>文件: annotations.py"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["(生产态 / production) Stage 2: AST 级精确比对器.<br/>文件: ast_comparator.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["(生产态 / production) 行为采样验证器 — Stage 0.25 低成本快速验证.<br/>文件: behavioral_sampler.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["(生产态 / production) 行为信任检查器 — 行为漂移DIVERGED检测.<br/>文件: behavioral_trust_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["(生产态 / production) Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>文件: cache_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["(生产态 / production) 金丝雀工厂——生成已知oracle 文件 用于引擎检出+...<br/>文件: canary_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["(生产态 / production) 金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>文件: canary_register.py"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["(生产态 / production) code-dedup-engine CLI——子命令映射+退出码+扫描入口.<br/>文件: cli.py"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["(生产态 / production) 检查运行器——按照敏感基线运行三阶段+导出 yaml 报告.<br/>文件: code_analyzer_runner.py"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["(生产态 / production) 代码模拟器——播放录制的克隆演化序列，stress-te...<br/>文件: code_simulator.py"]
    src_zephyr_gov_code_quality_code_dedup_config_py["(生产态 / production) 配置管理 — 策略树 YAML 加载 + 项目规模感知四 T...<br/>文件: config.py"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["(生产态 / production) API契约一致性检查器 — 存在性·行为·契约三维.<br/>文件: contract_consistency_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["(生产态 / production) 跨边界克隆感知——四大边界差异化检测+独立策略+...<br/>文件: cross_boundary_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["(生产态 / production) 死共享模块检测器 — shared/子模块无人使用 -> DEAD.<br/>文件: dead_module_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["(生产态 / production) 去重债务预测器 — weeks_to_payoff + intake_rate...<br/>文件: debt_projector.py"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["(生产态 / production) 决策审计链 — DecisionFingerprint 不可变追加日志.<br/>文件: decision_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["(生产态 / production) 降级运行管理器 — 各 Stage 独立 try/except + de...<br/>文件: degradation.py"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["(生产态 / production) Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>文件: diff_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["(生产态 / production) Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>文件: doom_loop_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["(生产态 / production) 安全提取适配性评估器 — Suitability Score 0-100...<br/>文件: extraction_safety.py"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["(生产态 / production) 三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Sam...<br/>文件: false_negative_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["(生产态 / production) 15维超综合审计首页 — 逐项证明'做过且做对'.<br/>文件: fifteen_dimension_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["(生产态 / production) 文件创建清单执行器 — 验证所有源/测试/数据文件...<br/>文件: file_creator.py"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py ~~~ src_zephyr_gov_code_quality_code_dedup_cache_manager_py
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_manager_py
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py ~~~ src_zephyr_gov_code_quality_code_dedup_canary_register_py
    src_zephyr_gov_code_quality_code_dedup_canary_register_py ~~~ src_zephyr_gov_code_quality_code_dedup_cli_py
    src_zephyr_gov_code_quality_code_dedup_cli_py ~~~ src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py ~~~ src_zephyr_gov_code_quality_code_dedup_code_simulator_py
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_config_py ~~~ src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py
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
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["(生产态 / production) 原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOIN...<br/>文件: atomic_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["(生产态 / production) 安全自动修复引擎——五直接开关+五间接约束.<br/>文件: auto_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["(生产态 / production) 退出码定义模块——五档exit code 0-4枚举+描述+判...<br/>文件: exit_codes.py"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py
    D_INFRASTRUCTURE["(生产态 / production) D_INFRASTRUCTURE"]
    src_zephyr_gov_code_quality_code_dedup_config_py -->|导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class scripts_governance_d3_metadata_check_pure_assertion_py,scripts_governance_d7_code_check_module_id_consistency_py,src_zephyr_gov_code_quality_init_py,src_zephyr_gov_code_quality_code_dedup_init_py,src_zephyr_gov_code_quality_code_dedup_annotations_py,src_zephyr_gov_code_quality_code_dedup_ast_comparator_py,src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py,src_zephyr_gov_code_quality_code_dedup_auto_fixer_py,src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py,src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py,src_zephyr_gov_code_quality_code_dedup_cache_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_register_py,src_zephyr_gov_code_quality_code_dedup_cli_py,src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py,src_zephyr_gov_code_quality_code_dedup_code_simulator_py,src_zephyr_gov_code_quality_code_dedup_config_py,src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py,src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py,src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py,src_zephyr_gov_code_quality_code_dedup_debt_projector_py,src_zephyr_gov_code_quality_code_dedup_decision_auditor_py,src_zephyr_gov_code_quality_code_dedup_degradation_py,src_zephyr_gov_code_quality_code_dedup_diff_detector_py,src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py,src_zephyr_gov_code_quality_code_dedup_exit_codes_py,src_zephyr_gov_code_quality_code_dedup_extraction_safety_py,src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py,src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py,src_zephyr_gov_code_quality_code_dedup_file_creator_py production
    class D_INFRASTRUCTURE,D_GOVERNANCE,D_INFRA_RUNTIME,D_SHARED external_prod
```

#### 第 2 页 / 共 6 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["(生产态 / production) 共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>文件: function_discovery.py"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["(生产态 / production) Grandfather 三定律 — 古老重复管理.<br/>文件: grandfather_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["(生产态 / production) 健康仪表盘 — Dedup Health Score 0-100 + 趋势 +...<br/>文件: health_monitor.py"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["(生产态 / production) 集成协调器 — 24集成+19更新+16GitHub整合.<br/>文件: integration_hub.py"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["(生产态 / production) 集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>文件: integrations.py"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["(生产态 / production) 微型克隆检测器 — n-gram频率计数, 1-2行高频模式...<br/>文件: micro_clone_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["(生产态 / production) 可控克隆生产器——零假阳性可期待引擎分子离散<br/>文件: mock_duplicate_generator.py"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["(生产态 / production) Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>文件: monoculture_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["(生产态 / production) 提取后稳定观察期守护 — 对标SDP 14天观察.<br/>文件: observation_window_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["(生产态 / production) 路径索引验证——验证 config 数据集相对路径表与...<br/>文件: path_index_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["(生产态 / production) 6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>文件: phase_executor.py"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["(生产态 / production) 策略树自动一致性校验器 — 虚线箭头影响分析.<br/>文件: policy_tree_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["(生产态 / production) Pre-Apply 完整性门 — SHA256重新验证.<br/>文件: pre_apply_integrity_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["(生产态 / production) 修复优先级排序器 — 置信度×Impact×适配性 三因...<br/>文件: prioritizer.py"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["(生产态 / production) Recovery Manifest Writer — R2纯文本base64 Mani...<br/>文件: recovery_manifest_writer.py"]
    src_zephyr_gov_code_quality_code_dedup_report_py["(生产态 / production) 报告生成器 — YAML/JSON 输出 + 退出码判定 + Hea...<br/>文件: report.py"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["(生产态 / production) R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + ...<br/>文件: risk_mitigator.py"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["(生产态 / production) 引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>文件: self_scanner.py"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["(生产态 / production) 敏感性扫荡——threshold扫描->固化成new baseline...<br/>文件: sensitivity_sweeper.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["(生产态 / production) 影子信任验证器 — ImportError 防护回路.<br/>文件: shadow_trust_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["(生产态 / production) 影子清单验证器 — size sanity check + semantic...<br/>文件: shadow_verifier.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["(生产态 / production) 共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定.<br/>文件: shared_evolver.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["(生产态 / production) 共享函数生命周期管理 — Active->Deprecated->Gra...<br/>文件: shared_lifecycle_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["(生产态 / production) Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配.<br/>文件: signature_matcher.py"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["(生产态 / production) 引擎成本效益自审计器 — SAS 0-100 月度审计 + Ta...<br/>文件: simplicity_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["(生产态 / production) SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>文件: ssot_registrar.py"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["(生产态 / production) 过时共享函数检测器 — 无caller × 30天 -> STALE标记.<br/>文件: stale_shared_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["(生产态 / production) 成功验证——判断一次去重操作是否真正消灭了克隆.<br/>文件: success_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["(生产态 / production) 符号索引 — 全局函数/类/import映射表.<br/>文件: symbol_index.py"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["(生产态 / production) 主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>文件: thematic_clusterer.py"]
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
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py ~~~ src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_report_py ~~~ src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py
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
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_gov_code_quality_code_dedup_function_discovery_py,src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py,src_zephyr_gov_code_quality_code_dedup_health_monitor_py,src_zephyr_gov_code_quality_code_dedup_integration_hub_py,src_zephyr_gov_code_quality_code_dedup_integrations_py,src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py,src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py,src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py,src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py,src_zephyr_gov_code_quality_code_dedup_path_index_validator_py,src_zephyr_gov_code_quality_code_dedup_phase_executor_py,src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py,src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py,src_zephyr_gov_code_quality_code_dedup_prioritizer_py,src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py,src_zephyr_gov_code_quality_code_dedup_report_py,src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py,src_zephyr_gov_code_quality_code_dedup_self_scanner_py,src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py,src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py,src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py,src_zephyr_gov_code_quality_code_dedup_shared_evolver_py,src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py,src_zephyr_gov_code_quality_code_dedup_signature_matcher_py,src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py,src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py,src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py,src_zephyr_gov_code_quality_code_dedup_success_validator_py,src_zephyr_gov_code_quality_code_dedup_symbol_index_py,src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py production
    class D_AUTONOMY_CORE,D_GOVERNANCE external_prod
```

#### 第 3 页 / 共 6 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["(生产态 / production) tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: __init__.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["(生产态 / production) 盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>文件: blind_spot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["(生产态 / production) 后果追踪——记录每次修复操作对依赖方的影响.<br/>文件: consequence_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["(生产态 / production) 热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新...<br/>文件: hotspot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["(生产态 / production) Import表面积负债追踪 — SBS 0-100 + shared burd...<br/>文件: import_surface_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["(生产态 / production) 风险缓解追踪——捕获哪些克隆报告了但在N次扫描后...<br/>文件: risk_mitigation_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["(生产态 / production) 修复验证器 — import + 类型 + 行为采样验证.<br/>文件: verifier.py"]
    src_zephyr_gov_enforcement_commit_gates_init_py["(生产态 / production) commit_gates — GitCommitGateway pre-commit 门...<br/>文件: __init__.py"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["(生产态 / production) arch_reference_gate.py — #ARCH-NNN /...<br/>文件: arch_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["(生产态 / production) asyncio_run_in_context_gate.py — 异步上下文误...<br/>文件: asyncio_run_in_context_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["(生产态 / production) bare_getenv_gate.py — 裸 os.getenv 读密钥阻断...<br/>文件: bare_getenv_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["(生产态 / production) bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BAR...<br/>文件: bare_sql_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["(生产态 / production) bare_subprocess_gate.py — 裸 subprocess 调用硬...<br/>文件: bare_subprocess_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["(生产态 / production) blueprint_amodule_consistency_gate.py — (A_mod...<br/>文件: blueprint_amodule_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["(生产态 / production) blueprint_amodule_cross_check_gate.py — (BLUEP...<br/>文件: blueprint_amodule_cross_check_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["(生产态 / production) blueprint_format_gate.py — (BLUEPRINT) 头部 mo...<br/>文件: blueprint_format_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["(生产态 / production) capability_consistency_gate.py — Provider 路由...<br/>文件: capability_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["(生产态 / production) capability_lookup_required_gate.py — Capabilit...<br/>文件: capability_lookup_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["(生产态 / production) capability_overlap_gate.py — 新建 .py 文件 Cap...<br/>文件: capability_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["(生产态 / production) ch_batch_size_gate.py — CH 批量写入防回退门禁...<br/>文件: ch_batch_size_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["(生产态 / production) ch_final_gate.py — ch_writer.query() 直接调用...<br/>文件: ch_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["(生产态 / production) ch_version_col_gate.py — CH version 列语义误用...<br/>文件: ch_version_col_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["(生产态 / production) claim_required_gate.py — claim_files 前置检查...<br/>文件: claim_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["(生产态 / production) consumers_accuracy_gate.py — CONSUMERS 字段准...<br/>文件: consumers_accuracy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["(生产态 / production) create_guard.py — 新建 .py / 非 rules/ .yaml ...<br/>文件: create_guard.py"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["(生产态 / production) dangling_reference_gate.py — AGENTS.md §X.Y ...<br/>文件: dangling_reference_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py
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
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["(生产态 / production) 问题追踪——扫描中发现需要人工处理的问题.<br/>文件: question_tracker.py"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["(生产态 / production) _diff_helpers.py — gate 共享 diff 解析工具模块<br/>文件: _diff_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["(生产态 / production) _reference_helpers.py — 引用检测门禁共享工具函...<br/>文件: _reference_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["(生产态 / production) capability_lookup_bypass_policy.py — CAPABILIT...<br/>文件: capability_lookup_bypass_policy.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py ~~~ src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_DATA["(生产态 / production) D_DATA"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| D_DATA
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_init_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_create_guard_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_gov_code_quality_code_dedup_trackers_init_py,src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py,src_zephyr_gov_code_quality_code_dedup_verifier_py,src_zephyr_gov_enforcement_commit_gates_init_py,src_zephyr_gov_enforcement_commit_gates_diff_helpers_py,src_zephyr_gov_enforcement_commit_gates_reference_helpers_py,src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py,src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py,src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py,src_zephyr_gov_enforcement_commit_gates_create_guard_py,src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py production
    class D_GOV_ENFORCEMENT,D_DATA,D_SHARED,D_GOVERNANCE,D_GOV_AUDIT,D_GOV_SCRIPTS external_prod
```

#### 第 4 页 / 共 6 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["(生产态 / production) data_task_completeness_gate.py — 数据任务完整...<br/>文件: data_task_completeness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["(生产态 / production) datetime_now_forbidden_gate.py — 时间戳约定硬...<br/>文件: datetime_now_forbidden_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["(生产态 / production) depgraph_freshness_gate.py — depgraph 新鲜度门...<br/>文件: depgraph_freshness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["(生产态 / production) depgraph_write_path_gate.py — depgraph 写入路...<br/>文件: depgraph_write_path_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["(生产态 / production) derivation_annotation_gate.py — 派生关系声明真...<br/>文件: derivation_annotation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["(生产态 / production) directory_contract_gate.py — DCR-001~007 等效...<br/>文件: directory_contract_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["(生产态 / production) doc_ref_broken_gate.py — 文档相对路径断裂引用...<br/>文件: doc_ref_broken_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["(生产态 / production) domain_fk_gate.py — (DOMAIN) 头部域注册表 FK ...<br/>文件: domain_fk_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["(生产态 / production) domain_name_zh_direct_access_gate.py — DOMAIN_...<br/>文件: domain_name_zh_direct_access_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["(生产态 / production) empty_handler_gate.py — 空事件 handler 函数阻...<br/>文件: empty_handler_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["(生产态 / production) encoding_gate.py — 编码安全校验门禁（治本：弥...<br/>文件: encoding_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["(生产态 / production) exempt_zone_frontmatter_gate.py — 豁免区 front...<br/>文件: exempt_zone_frontmatter_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["(生产态 / production) file_copy_gate.py — 新增 .py 文件复制检测阻断...<br/>文件: file_copy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["(生产态 / production) file_placement_ttl_gate.py — 文件放置与 TTL 一...<br/>文件: file_placement_ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["(生产态 / production) folder_capacity_hard_limit_gate.py — 文件夹容...<br/>文件: folder_capacity_hard_limit_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["(生产态 / production) foreign_change_gate.py — 外来变更检测门禁（FOR...<br/>文件: foreign_change_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["(生产态 / production) forged_gw_marker_gate.py — Forged GW Marker 前...<br/>文件: forged_gw_marker_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["(生产态 / production) function_dup_gate.py — 重复函数实现阻断门禁（F...<br/>文件: function_dup_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["(生产态 / production) gate_repo.py — gates 表持久化仓库（AUDIT-07 P1...<br/>文件: gate_repo.py"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["(生产态 / production) git_call_budget_gate.py — Git 调用预算 warn-on...<br/>文件: git_call_budget_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["(生产态 / production) god_class_gate.py — God Class 阻断门禁（NO-GOD...<br/>文件: god_class_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["(生产态 / production) hardcoded_url_gate.py — 硬编码 localhost URL ...<br/>文件: hardcoded_url_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["(生产态 / production) held_overlap_gate.py — 搭便车防护门禁（HELD-OV...<br/>文件: held_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["(生产态 / production) high_complexity_gate.py — 高循环复杂度阻断门禁...<br/>文件: high_complexity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["(生产态 / production) id_uniqueness_gate.py — pre-commit hook ID 唯...<br/>文件: id_uniqueness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["(生产态 / production) import_direction_gate.py — shared 层向上依赖阻...<br/>文件: import_direction_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["(生产态 / production) import_integrity_gate.py — IMPORT-INTEGRITY 门...<br/>文件: import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["(生产态 / production) issue_resolved_integrity_gate.py — ISSUE-RESOL...<br/>文件: issue_resolved_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["(生产态 / production) long_param_list_gate.py — 长参数列表阻断门禁（...<br/>文件: long_param_list_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["(生产态 / production) manual_only_permanent_gate.py — 永久系统脚本 m...<br/>文件: manual_only_permanent_gate.py"]
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
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py,src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py,src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py,src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py,src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py,src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py,src_zephyr_gov_enforcement_commit_gates_encoding_gate_py,src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py,src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py,src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py,src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py,src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py,src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py,src_zephyr_gov_enforcement_commit_gates_gate_repo_py,src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py,src_zephyr_gov_enforcement_commit_gates_god_class_gate_py,src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py,src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py,src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py,src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py,src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py,src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py production
    class D_GOV_ENFORCEMENT,D_SHARED,D_SECURITY external_prod
```

#### 第 5 页 / 共 6 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["(生产态 / production) mcp_version_field_gate.py — MCP version 字段缺...<br/>文件: mcp_version_field_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["(生产态 / production) module_id_consistency_gate.py — module_id 三声...<br/>文件: module_id_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["(生产态 / production) msg_exposure_gate.py — 错误消息暴露敏感信息阻...<br/>文件: msg_exposure_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["(生产态 / production) msg_style_gate.py — 错误消息标点/箭头风格阻断...<br/>文件: msg_style_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["(生产态 / production) mutable_const_without_final_gate.py — 可变常量...<br/>文件: mutable_const_without_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["(生产态 / production) new_file_depgraph_gate.py — 新建 .py 文件 depg...<br/>文件: new_file_depgraph_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["(生产态 / production) no_import_side_effect_gate.py — 模块导入零副作...<br/>文件: no_import_side_effect_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["(生产态 / production) noqa_validation_gate.py — 自定义 noqa 标记合规...<br/>文件: noqa_validation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["(生产态 / production) open_without_with_gate.py — open() 未在 with ...<br/>文件: open_without_with_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["(生产态 / production) orphan_module_gate.py — 孤儿模块（无 import 引...<br/>文件: orphan_module_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["(生产态 / production) panorama_alignment_gate.py — 三图模块对齐门禁...<br/>文件: panorama_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["(生产态 / production) perm_trigger_gate.py — 永久系统脚本时间触发模...<br/>文件: perm_trigger_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["(生产态 / production) precommit_offline_gate.py — pre-commit 配置离...<br/>文件: precommit_offline_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["(生产态 / production) pure_assertion_gate.py — 纯陈述原则阻断门禁（P...<br/>文件: pure_assertion_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["(生产态 / production) pure_shim_gate.py — 纯 re-export shim 阻断门禁...<br/>文件: pure_shim_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["(生产态 / production) r5_digit_suffix_gate.py — R5 数字后缀目录禁止...<br/>文件: r5_digit_suffix_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["(生产态 / production) reconciler_health_gate.py — reconciler 健康度...<br/>文件: reconciler_health_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["(生产态 / production) relative_path_literal_gate.py — 相对路径字面量...<br/>文件: relative_path_literal_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["(生产态 / production) rename_depgraph_sync_gate.py — 文件重命名后 de...<br/>文件: rename_depgraph_sync_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["(生产态 / production) rule_execution_pairing_gate.py — 规则-执行配对...<br/>文件: rule_execution_pairing_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["(生产态 / production) rule_four_way_alignment_gate.py — 规则四方对齐...<br/>文件: rule_four_way_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["(生产态 / production) ruling_commit_verified_gate.py — 文档'已完成'...<br/>文件: ruling_commit_verified_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["(生产态 / production) ruling_reference_gate.py — 裁定#NNN 悬空引用自...<br/>文件: ruling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["(生产态 / production) schema_file_exists_gate.py — SCHEMA-FILE-EXIST...<br/>文件: schema_file_exists_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["(生产态 / production) scripts_import_integrity_gate.py — _shared.con...<br/>文件: scripts_import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["(生产态 / production) session_required_gate.py — session 注册强制门...<br/>文件: session_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["(生产态 / production) snapshot_drift_gate.py — 运行时违规快照漂移阻...<br/>文件: snapshot_drift_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["(生产态 / production) ssot_redefinition_gate.py — SSoT 符号重复定义...<br/>文件: ssot_redefinition_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["(生产态 / production) table_name_registry_gate.py — TABLE-NAME-REGIS...<br/>文件: table_name_registry_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["(生产态 / production) test_source_consistency_gate.py — 测试-源码符...<br/>文件: test_source_consistency_gate.py"]
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
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py ~~~ src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py
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
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py,src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py,src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py,src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py,src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py,src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py,src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py,src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py,src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py,src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py,src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py,src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py,src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py,src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py,src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_session_required_gate_py,src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py,src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py,src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py,src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py production
    class D_GOV_ENFORCEMENT,D_SHARED,D_GOV_AUDIT external_prod
```

#### 第 6 页 / 共 6 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["(生产态 / production) tests_coverage_gate.py — Gate 测试覆盖率校验 m...<br/>文件: tests_coverage_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["(生产态 / production) ttl_gate.py — ttl 字段校验门禁（治本：弥补 --n...<br/>文件: ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["(生产态 / production) undefined_name_gate.py — UNDEFINED-NAME 门禁（...<br/>文件: undefined_name_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["(生产态 / production) unsafe_dict_spread_gate.py — ``**data`` 直接展...<br/>文件: unsafe_dict_spread_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["(生产态 / production) vocab_chain_gate.py — SSoT 引用硬编码阻断门禁...<br/>文件: vocab_chain_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["(生产态 / production) vocab_hardcode_gate.py — 新增 .py 文件词表硬编...<br/>文件: vocab_hardcode_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["(生产态 / production) zephyr_env_direct_access_gate.py — ZEPHYR_ENV ...<br/>文件: zephyr_env_direct_access_gate.py"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["(生产态 / production) gate_auto_registrar.py — YAML 驱动的 in-proces...<br/>文件: gate_auto_registrar.py"]
    tests_data_test_symbol_normalizer_py["(生产态 / production) test_symbol_normalizer.py — TRAE-082 symbol 标...<br/>文件: test_symbol_normalizer.py"]
    tests_governance_test_apply_dataflowgraph_smoke_py["(生产态 / production) test_apply_dataflowgraph_smoke.py — apply_data...<br/>文件: test_apply_dataflowgraph_smoke.py"]
    tests_governance_test_apply_decisiongraph_smoke_py["(生产态 / production) test_apply_decisiongraph_smoke.py — apply_deci...<br/>文件: test_apply_decisiongraph_smoke.py"]
    tests_governance_test_apply_depgraph_smoke_py["(生产态 / production) test_apply_depgraph_smoke.py — apply_depgraph....<br/>文件: test_apply_depgraph_smoke.py"]
    tests_governance_test_audit_return_contract_usage_py["(生产态 / production) test_audit_return_contract_usage.py — 返回契约...<br/>文件: test_audit_return_contract_usage.py"]
    tests_governance_test_audit_worktree_ops_telemetry_py["(生产态 / production) test_audit_worktree_ops_telemetry.py — worktre...<br/>文件: test_audit_worktree_ops_telemetry.py"]
    tests_governance_test_generate_project_depgraph_smoke_py["(生产态 / production) test_generate_project_depgraph_smoke.py — gene...<br/>文件: test_generate_project_depgraph_smoke.py"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["(生产态 / production) test_post_commit_guard_no_verify_threshold.py ...<br/>文件: test_post_commit_guard_no_verify_threshold.py"]
    tests_governance_test_run_silent_failure_regression_py["(生产态 / production) test_run_silent_failure_regression.py — silent...<br/>文件: test_run_silent_failure_regression.py"]
    tests_governance_test_session_startup_health_check_py["(生产态 / production) test_session_startup_health_check.py — AI sess...<br/>文件: test_session_startup_health_check.py"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["(生产态 / production) test_sync_yaml_to_depgraph_smoke.py — sync_yam...<br/>文件: test_sync_yaml_to_depgraph_smoke.py"]
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
    D_DATA["(生产态 / production) D_DATA"]
    tests_data_test_symbol_normalizer_py -->|测试依赖 / test_depends| D_DATA
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    tests_governance_test_audit_worktree_ops_telemetry_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py -->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py,src_zephyr_gov_enforcement_commit_gates_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py,src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py,src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py,src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py,tests_data_test_symbol_normalizer_py,tests_governance_test_apply_dataflowgraph_smoke_py,tests_governance_test_apply_decisiongraph_smoke_py,tests_governance_test_apply_depgraph_smoke_py,tests_governance_test_audit_return_contract_usage_py,tests_governance_test_audit_worktree_ops_telemetry_py,tests_governance_test_generate_project_depgraph_smoke_py,tests_governance_test_post_commit_guard_no_verify_threshold_py,tests_governance_test_run_silent_failure_regression_py,tests_governance_test_session_startup_health_check_py,tests_governance_test_sync_yaml_to_depgraph_smoke_py production
    class D_DATA,D_GOV_ENFORCEMENT,D_SHARED,D_GOVERNANCE,D_GOV_AUDIT external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 169 个，44 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    scripts_governance_d3_metadata_check_pure_assertion_py["(生产态 / production) check_pure_assertion.py — GOV-DOC-016 纯陈述原...<br/>文件: check_pure_assertion.py"]
    scripts_governance_d7_code_check_module_id_consistency_py["(生产态 / production) check_module_id_consistency.py — module_id 全...<br/>文件: check_module_id_consistency.py"]
    src_zephyr_gov_code_quality_init_py["(生产态 / production) gov_code_quality domain package — code quality...<br/>文件: __init__.py"]
    src_zephyr_gov_code_quality_code_dedup_init_py["(生产态 / production) code-dedup-engine 子包 — 重复代码检测与治理引擎.<br/>文件: __init__.py"]
    src_zephyr_gov_code_quality_code_dedup_annotations_py["(生产态 / production) 共享函数注解引擎 — @shared / @known_dup / @int...<br/>文件: annotations.py"]
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py["(生产态 / production) Stage 2: AST 级精确比对器.<br/>文件: ast_comparator.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py["(生产态 / production) 行为采样验证器 — Stage 0.25 低成本快速验证.<br/>文件: behavioral_sampler.py"]
    src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py["(生产态 / production) 行为信任检查器 — 行为漂移DIVERGED检测.<br/>文件: behavioral_trust_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cache_manager_py["(生产态 / production) Stage 0: 函数缓存管理器 — 增量扫描的加速核心.<br/>文件: cache_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_manager_py["(生产态 / production) 金丝雀工厂——生成已知oracle 文件 用于引擎检出+...<br/>文件: canary_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_canary_register_py["(生产态 / production) 金丝雀注册表维护器 — 注册/过期/腐败检测.<br/>文件: canary_register.py"]
    src_zephyr_gov_code_quality_code_dedup_cli_py["(生产态 / production) code-dedup-engine CLI——子命令映射+退出码+扫描入口.<br/>文件: cli.py"]
    src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py["(生产态 / production) 检查运行器——按照敏感基线运行三阶段+导出 yaml 报告.<br/>文件: code_analyzer_runner.py"]
    src_zephyr_gov_code_quality_code_dedup_code_simulator_py["(生产态 / production) 代码模拟器——播放录制的克隆演化序列，stress-te...<br/>文件: code_simulator.py"]
    src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py["(生产态 / production) API契约一致性检查器 — 存在性·行为·契约三维.<br/>文件: contract_consistency_checker.py"]
    src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py["(生产态 / production) 跨边界克隆感知——四大边界差异化检测+独立策略+...<br/>文件: cross_boundary_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py["(生产态 / production) 死共享模块检测器 — shared/子模块无人使用 -> DEAD.<br/>文件: dead_module_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_debt_projector_py["(生产态 / production) 去重债务预测器 — weeks_to_payoff + intake_rate...<br/>文件: debt_projector.py"]
    src_zephyr_gov_code_quality_code_dedup_decision_auditor_py["(生产态 / production) 决策审计链 — DecisionFingerprint 不可变追加日志.<br/>文件: decision_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_degradation_py["(生产态 / production) 降级运行管理器 — 各 Stage 独立 try/except + de...<br/>文件: degradation.py"]
    src_zephyr_gov_code_quality_code_dedup_diff_detector_py["(生产态 / production) Stage 0: Git diff 变更检测器 — 函数粒度增量.<br/>文件: diff_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py["(生产态 / production) Doom Loop 防护 — 修复升级阶梯 L0-L4 状态机.<br/>文件: doom_loop_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_extraction_safety_py["(生产态 / production) 安全提取适配性评估器 — Suitability Score 0-100...<br/>文件: extraction_safety.py"]
    src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py["(生产态 / production) 三层漏报盲审器 — L1 Sweep + L2 Canary + L3 Sam...<br/>文件: false_negative_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py["(生产态 / production) 15维超综合审计首页 — 逐项证明'做过且做对'.<br/>文件: fifteen_dimension_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_file_creator_py["(生产态 / production) 文件创建清单执行器 — 验证所有源/测试/数据文件...<br/>文件: file_creator.py"]
    src_zephyr_gov_code_quality_code_dedup_function_discovery_py["(生产态 / production) 共享函数主动发现 — 签名+语义双通道从被动到主动.<br/>文件: function_discovery.py"]
    src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py["(生产态 / production) Grandfather 三定律 — 古老重复管理.<br/>文件: grandfather_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_health_monitor_py["(生产态 / production) 健康仪表盘 — Dedup Health Score 0-100 + 趋势 +...<br/>文件: health_monitor.py"]
    src_zephyr_gov_code_quality_code_dedup_integration_hub_py["(生产态 / production) 集成协调器 — 24集成+19更新+16GitHub整合.<br/>文件: integration_hub.py"]
    src_zephyr_gov_code_quality_code_dedup_integrations_py["(生产态 / production) 集成管理——预提交钩子+CI-only 扫描+超时边界.<br/>文件: integrations.py"]
    src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py["(生产态 / production) 微型克隆检测器 — n-gram频率计数, 1-2行高频模式...<br/>文件: micro_clone_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py["(生产态 / production) 可控克隆生产器——零假阳性可期待引擎分子离散<br/>文件: mock_duplicate_generator.py"]
    src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py["(生产态 / production) Monoculture 免疫 — BRS 0-100 + 去重悖论检测.<br/>文件: monoculture_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py["(生产态 / production) 提取后稳定观察期守护 — 对标SDP 14天观察.<br/>文件: observation_window_guard.py"]
    src_zephyr_gov_code_quality_code_dedup_path_index_validator_py["(生产态 / production) 路径索引验证——验证 config 数据集相对路径表与...<br/>文件: path_index_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_phase_executor_py["(生产态 / production) 6Phase施工执行器 — Phase 0~5 执行状态追踪.<br/>文件: phase_executor.py"]
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py["(生产态 / production) 策略树自动一致性校验器 — 虚线箭头影响分析.<br/>文件: policy_tree_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py["(生产态 / production) Pre-Apply 完整性门 — SHA256重新验证.<br/>文件: pre_apply_integrity_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_prioritizer_py["(生产态 / production) 修复优先级排序器 — 置信度×Impact×适配性 三因...<br/>文件: prioritizer.py"]
    src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py["(生产态 / production) Recovery Manifest Writer — R2纯文本base64 Mani...<br/>文件: recovery_manifest_writer.py"]
    src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py["(生产态 / production) R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + ...<br/>文件: risk_mitigator.py"]
    src_zephyr_gov_code_quality_code_dedup_self_scanner_py["(生产态 / production) 引擎自扫描器 — Dogfooding 检测引擎自身源码重复.<br/>文件: self_scanner.py"]
    src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py["(生产态 / production) 敏感性扫荡——threshold扫描->固化成new baseline...<br/>文件: sensitivity_sweeper.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py["(生产态 / production) 影子信任验证器 — ImportError 防护回路.<br/>文件: shadow_trust_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py["(生产态 / production) 影子清单验证器 — size sanity check + semantic...<br/>文件: shadow_verifier.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_evolver_py["(生产态 / production) 共享函数自我进化引擎 — 自动升降级 + 行为漂移锁定.<br/>文件: shared_evolver.py"]
    src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py["(生产态 / production) 共享函数生命周期管理 — Active->Deprecated->Gra...<br/>文件: shared_lifecycle_manager.py"]
    src_zephyr_gov_code_quality_code_dedup_signature_matcher_py["(生产态 / production) Stage 0.5: 签名指纹 SHA256(:12) O(1) 精确匹配.<br/>文件: signature_matcher.py"]
    src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py["(生产态 / production) 引擎成本效益自审计器 — SAS 0-100 月度审计 + Ta...<br/>文件: simplicity_auditor.py"]
    src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py["(生产态 / production) SSoT注册器 — 提取函数自动注册到 shared API清单.<br/>文件: ssot_registrar.py"]
    src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py["(生产态 / production) 过时共享函数检测器 — 无caller × 30天 -> STALE标记.<br/>文件: stale_shared_detector.py"]
    src_zephyr_gov_code_quality_code_dedup_success_validator_py["(生产态 / production) 成功验证——判断一次去重操作是否真正消灭了克隆.<br/>文件: success_validator.py"]
    src_zephyr_gov_code_quality_code_dedup_symbol_index_py["(生产态 / production) 符号索引 — 全局函数/类/import映射表.<br/>文件: symbol_index.py"]
    src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py["(生产态 / production) 主题聚类器 — 噪声信号比·告警疲劳缓解.<br/>文件: thematic_clusterer.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py["(生产态 / production) tracker 族子包 — 风险/盲点/热点跟踪器集合.<br/>文件: __init__.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py["(生产态 / production) 盲点关闭追踪器 — 自动验证各轮盲点是否已覆盖.<br/>文件: blind_spot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py["(生产态 / production) 后果追踪——记录每次修复操作对依赖方的影响.<br/>文件: consequence_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py["(生产态 / production) 热点追踪器 — 90天滑动窗口 + 高频变动检测 + 新...<br/>文件: hotspot_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py["(生产态 / production) Import表面积负债追踪 — SBS 0-100 + shared burd...<br/>文件: import_surface_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py["(生产态 / production) 风险缓解追踪——捕获哪些克隆报告了但在N次扫描后...<br/>文件: risk_mitigation_tracker.py"]
    src_zephyr_gov_code_quality_code_dedup_verifier_py["(生产态 / production) 修复验证器 — import + 类型 + 行为采样验证.<br/>文件: verifier.py"]
    src_zephyr_gov_enforcement_commit_gates_init_py["(生产态 / production) commit_gates — GitCommitGateway pre-commit 门...<br/>文件: __init__.py"]
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py["(生产态 / production) arch_reference_gate.py — #ARCH-NNN /...<br/>文件: arch_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py["(生产态 / production) asyncio_run_in_context_gate.py — 异步上下文误...<br/>文件: asyncio_run_in_context_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py["(生产态 / production) bare_getenv_gate.py — 裸 os.getenv 读密钥阻断...<br/>文件: bare_getenv_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py["(生产态 / production) bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BAR...<br/>文件: bare_sql_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py["(生产态 / production) bare_subprocess_gate.py — 裸 subprocess 调用硬...<br/>文件: bare_subprocess_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py["(生产态 / production) blueprint_amodule_consistency_gate.py — (A_mod...<br/>文件: blueprint_amodule_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py["(生产态 / production) blueprint_amodule_cross_check_gate.py — (BLUEP...<br/>文件: blueprint_amodule_cross_check_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py["(生产态 / production) blueprint_format_gate.py — (BLUEPRINT) 头部 mo...<br/>文件: blueprint_format_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py["(生产态 / production) capability_consistency_gate.py — Provider 路由...<br/>文件: capability_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py["(生产态 / production) capability_lookup_required_gate.py — Capabilit...<br/>文件: capability_lookup_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py["(生产态 / production) capability_overlap_gate.py — 新建 .py 文件 Cap...<br/>文件: capability_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py["(生产态 / production) ch_batch_size_gate.py — CH 批量写入防回退门禁...<br/>文件: ch_batch_size_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py["(生产态 / production) ch_final_gate.py — ch_writer.query() 直接调用...<br/>文件: ch_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py["(生产态 / production) ch_version_col_gate.py — CH version 列语义误用...<br/>文件: ch_version_col_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py["(生产态 / production) claim_required_gate.py — claim_files 前置检查...<br/>文件: claim_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py["(生产态 / production) consumers_accuracy_gate.py — CONSUMERS 字段准...<br/>文件: consumers_accuracy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_create_guard_py["(生产态 / production) create_guard.py — 新建 .py / 非 rules/ .yaml ...<br/>文件: create_guard.py"]
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py["(生产态 / production) dangling_reference_gate.py — AGENTS.md §X.Y ...<br/>文件: dangling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py["(生产态 / production) data_task_completeness_gate.py — 数据任务完整...<br/>文件: data_task_completeness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py["(生产态 / production) datetime_now_forbidden_gate.py — 时间戳约定硬...<br/>文件: datetime_now_forbidden_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py["(生产态 / production) depgraph_freshness_gate.py — depgraph 新鲜度门...<br/>文件: depgraph_freshness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py["(生产态 / production) depgraph_write_path_gate.py — depgraph 写入路...<br/>文件: depgraph_write_path_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py["(生产态 / production) derivation_annotation_gate.py — 派生关系声明真...<br/>文件: derivation_annotation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py["(生产态 / production) directory_contract_gate.py — DCR-001~007 等效...<br/>文件: directory_contract_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py["(生产态 / production) doc_ref_broken_gate.py — 文档相对路径断裂引用...<br/>文件: doc_ref_broken_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py["(生产态 / production) domain_fk_gate.py — (DOMAIN) 头部域注册表 FK ...<br/>文件: domain_fk_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py["(生产态 / production) domain_name_zh_direct_access_gate.py — DOMAIN_...<br/>文件: domain_name_zh_direct_access_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py["(生产态 / production) empty_handler_gate.py — 空事件 handler 函数阻...<br/>文件: empty_handler_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py["(生产态 / production) encoding_gate.py — 编码安全校验门禁（治本：弥...<br/>文件: encoding_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py["(生产态 / production) exempt_zone_frontmatter_gate.py — 豁免区 front...<br/>文件: exempt_zone_frontmatter_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py["(生产态 / production) file_copy_gate.py — 新增 .py 文件复制检测阻断...<br/>文件: file_copy_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py["(生产态 / production) file_placement_ttl_gate.py — 文件放置与 TTL 一...<br/>文件: file_placement_ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py["(生产态 / production) folder_capacity_hard_limit_gate.py — 文件夹容...<br/>文件: folder_capacity_hard_limit_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py["(生产态 / production) foreign_change_gate.py — 外来变更检测门禁（FOR...<br/>文件: foreign_change_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py["(生产态 / production) forged_gw_marker_gate.py — Forged GW Marker 前...<br/>文件: forged_gw_marker_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py["(生产态 / production) function_dup_gate.py — 重复函数实现阻断门禁（F...<br/>文件: function_dup_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_gate_repo_py["(生产态 / production) gate_repo.py — gates 表持久化仓库（AUDIT-07 P1...<br/>文件: gate_repo.py"]
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py["(生产态 / production) git_call_budget_gate.py — Git 调用预算 warn-on...<br/>文件: git_call_budget_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py["(生产态 / production) god_class_gate.py — God Class 阻断门禁（NO-GOD...<br/>文件: god_class_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py["(生产态 / production) hardcoded_url_gate.py — 硬编码 localhost URL ...<br/>文件: hardcoded_url_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py["(生产态 / production) held_overlap_gate.py — 搭便车防护门禁（HELD-OV...<br/>文件: held_overlap_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py["(生产态 / production) high_complexity_gate.py — 高循环复杂度阻断门禁...<br/>文件: high_complexity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py["(生产态 / production) id_uniqueness_gate.py — pre-commit hook ID 唯...<br/>文件: id_uniqueness_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py["(生产态 / production) import_direction_gate.py — shared 层向上依赖阻...<br/>文件: import_direction_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py["(生产态 / production) import_integrity_gate.py — IMPORT-INTEGRITY 门...<br/>文件: import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py["(生产态 / production) issue_resolved_integrity_gate.py — ISSUE-RESOL...<br/>文件: issue_resolved_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py["(生产态 / production) long_param_list_gate.py — 长参数列表阻断门禁（...<br/>文件: long_param_list_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py["(生产态 / production) manual_only_permanent_gate.py — 永久系统脚本 m...<br/>文件: manual_only_permanent_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py["(生产态 / production) mcp_version_field_gate.py — MCP version 字段缺...<br/>文件: mcp_version_field_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py["(生产态 / production) module_id_consistency_gate.py — module_id 三声...<br/>文件: module_id_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py["(生产态 / production) msg_exposure_gate.py — 错误消息暴露敏感信息阻...<br/>文件: msg_exposure_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py["(生产态 / production) msg_style_gate.py — 错误消息标点/箭头风格阻断...<br/>文件: msg_style_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py["(生产态 / production) mutable_const_without_final_gate.py — 可变常量...<br/>文件: mutable_const_without_final_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py["(生产态 / production) new_file_depgraph_gate.py — 新建 .py 文件 depg...<br/>文件: new_file_depgraph_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py["(生产态 / production) no_import_side_effect_gate.py — 模块导入零副作...<br/>文件: no_import_side_effect_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py["(生产态 / production) noqa_validation_gate.py — 自定义 noqa 标记合规...<br/>文件: noqa_validation_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py["(生产态 / production) open_without_with_gate.py — open() 未在 with ...<br/>文件: open_without_with_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py["(生产态 / production) orphan_module_gate.py — 孤儿模块（无 import 引...<br/>文件: orphan_module_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py["(生产态 / production) panorama_alignment_gate.py — 三图模块对齐门禁...<br/>文件: panorama_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py["(生产态 / production) precommit_offline_gate.py — pre-commit 配置离...<br/>文件: precommit_offline_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py["(生产态 / production) pure_assertion_gate.py — 纯陈述原则阻断门禁（P...<br/>文件: pure_assertion_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py["(生产态 / production) pure_shim_gate.py — 纯 re-export shim 阻断门禁...<br/>文件: pure_shim_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py["(生产态 / production) r5_digit_suffix_gate.py — R5 数字后缀目录禁止...<br/>文件: r5_digit_suffix_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py["(生产态 / production) reconciler_health_gate.py — reconciler 健康度...<br/>文件: reconciler_health_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py["(生产态 / production) relative_path_literal_gate.py — 相对路径字面量...<br/>文件: relative_path_literal_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py["(生产态 / production) rename_depgraph_sync_gate.py — 文件重命名后 de...<br/>文件: rename_depgraph_sync_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py["(生产态 / production) rule_execution_pairing_gate.py — 规则-执行配对...<br/>文件: rule_execution_pairing_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py["(生产态 / production) rule_four_way_alignment_gate.py — 规则四方对齐...<br/>文件: rule_four_way_alignment_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py["(生产态 / production) ruling_commit_verified_gate.py — 文档'已完成'...<br/>文件: ruling_commit_verified_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py["(生产态 / production) ruling_reference_gate.py — 裁定#NNN 悬空引用自...<br/>文件: ruling_reference_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py["(生产态 / production) schema_file_exists_gate.py — SCHEMA-FILE-EXIST...<br/>文件: schema_file_exists_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py["(生产态 / production) scripts_import_integrity_gate.py — _shared.con...<br/>文件: scripts_import_integrity_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_session_required_gate_py["(生产态 / production) session_required_gate.py — session 注册强制门...<br/>文件: session_required_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py["(生产态 / production) snapshot_drift_gate.py — 运行时违规快照漂移阻...<br/>文件: snapshot_drift_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py["(生产态 / production) ssot_redefinition_gate.py — SSoT 符号重复定义...<br/>文件: ssot_redefinition_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py["(生产态 / production) table_name_registry_gate.py — TABLE-NAME-REGIS...<br/>文件: table_name_registry_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py["(生产态 / production) test_source_consistency_gate.py — 测试-源码符...<br/>文件: test_source_consistency_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py["(生产态 / production) tests_coverage_gate.py — Gate 测试覆盖率校验 m...<br/>文件: tests_coverage_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_ttl_gate_py["(生产态 / production) ttl_gate.py — ttl 字段校验门禁（治本：弥补 --n...<br/>文件: ttl_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py["(生产态 / production) undefined_name_gate.py — UNDEFINED-NAME 门禁（...<br/>文件: undefined_name_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py["(生产态 / production) unsafe_dict_spread_gate.py — ``**data`` 直接展...<br/>文件: unsafe_dict_spread_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py["(生产态 / production) vocab_chain_gate.py — SSoT 引用硬编码阻断门禁...<br/>文件: vocab_chain_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py["(生产态 / production) vocab_hardcode_gate.py — 新增 .py 文件词表硬编...<br/>文件: vocab_hardcode_gate.py"]
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py["(生产态 / production) zephyr_env_direct_access_gate.py — ZEPHYR_ENV ...<br/>文件: zephyr_env_direct_access_gate.py"]
    src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py["(生产态 / production) gate_auto_registrar.py — YAML 驱动的 in-proces...<br/>文件: gate_auto_registrar.py"]
    tests_data_test_symbol_normalizer_py["(生产态 / production) test_symbol_normalizer.py — TRAE-082 symbol 标...<br/>文件: test_symbol_normalizer.py"]
    tests_governance_test_apply_dataflowgraph_smoke_py["(生产态 / production) test_apply_dataflowgraph_smoke.py — apply_data...<br/>文件: test_apply_dataflowgraph_smoke.py"]
    tests_governance_test_apply_decisiongraph_smoke_py["(生产态 / production) test_apply_decisiongraph_smoke.py — apply_deci...<br/>文件: test_apply_decisiongraph_smoke.py"]
    tests_governance_test_apply_depgraph_smoke_py["(生产态 / production) test_apply_depgraph_smoke.py — apply_depgraph....<br/>文件: test_apply_depgraph_smoke.py"]
    tests_governance_test_audit_return_contract_usage_py["(生产态 / production) test_audit_return_contract_usage.py — 返回契约...<br/>文件: test_audit_return_contract_usage.py"]
    tests_governance_test_audit_worktree_ops_telemetry_py["(生产态 / production) test_audit_worktree_ops_telemetry.py — worktre...<br/>文件: test_audit_worktree_ops_telemetry.py"]
    tests_governance_test_generate_project_depgraph_smoke_py["(生产态 / production) test_generate_project_depgraph_smoke.py — gene...<br/>文件: test_generate_project_depgraph_smoke.py"]
    tests_governance_test_post_commit_guard_no_verify_threshold_py["(生产态 / production) test_post_commit_guard_no_verify_threshold.py ...<br/>文件: test_post_commit_guard_no_verify_threshold.py"]
    tests_governance_test_run_silent_failure_regression_py["(生产态 / production) test_run_silent_failure_regression.py — silent...<br/>文件: test_run_silent_failure_regression.py"]
    tests_governance_test_session_startup_health_check_py["(生产态 / production) test_session_startup_health_check.py — AI sess...<br/>文件: test_session_startup_health_check.py"]
    tests_governance_test_sync_yaml_to_depgraph_smoke_py["(生产态 / production) test_sync_yaml_to_depgraph_smoke.py — sync_yam...<br/>文件: test_sync_yaml_to_depgraph_smoke.py"]
    scripts_governance_d3_metadata_check_pure_assertion_py ~~~ scripts_governance_d7_code_check_module_id_consistency_py
    scripts_governance_d7_code_check_module_id_consistency_py ~~~ src_zephyr_gov_code_quality_init_py
    src_zephyr_gov_code_quality_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_init_py
    src_zephyr_gov_code_quality_code_dedup_init_py ~~~ src_zephyr_gov_code_quality_code_dedup_annotations_py
    src_zephyr_gov_code_quality_code_dedup_annotations_py ~~~ src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    src_zephyr_gov_code_quality_code_dedup_ast_comparator_py ~~~ src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
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
    src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py
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
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py["(生产态 / production) 原子性修复引擎 — WAL 式 PREFLIGHT -> CHECKPOIN...<br/>文件: atomic_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py["(生产态 / production) 安全自动修复引擎——五直接开关+五间接约束.<br/>文件: auto_fixer.py"]
    src_zephyr_gov_code_quality_code_dedup_config_py["(生产态 / production) 配置管理 — 策略树 YAML 加载 + 项目规模感知四 T...<br/>文件: config.py"]
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py["(生产态 / production) 退出码定义模块——五档exit code 0-4枚举+描述+判...<br/>文件: exit_codes.py"]
    src_zephyr_gov_code_quality_code_dedup_report_py["(生产态 / production) 报告生成器 — YAML/JSON 输出 + 退出码判定 + Hea...<br/>文件: report.py"]
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py["(生产态 / production) 问题追踪——扫描中发现需要人工处理的问题.<br/>文件: question_tracker.py"]
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py["(生产态 / production) _diff_helpers.py — gate 共享 diff 解析工具模块<br/>文件: _diff_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py["(生产态 / production) _reference_helpers.py — 引用检测门禁共享工具函...<br/>文件: _reference_helpers.py"]
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py["(生产态 / production) capability_lookup_bypass_policy.py — CAPABILIT...<br/>文件: capability_lookup_bypass_policy.py"]
    src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py["(生产态 / production) perm_trigger_gate.py — 永久系统脚本时间触发模...<br/>文件: perm_trigger_gate.py"]
    src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_auto_fixer_py ~~~ src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_config_py ~~~ src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_exit_codes_py ~~~ src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_report_py ~~~ src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py
    src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py ~~~ src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_diff_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_reference_helpers_py ~~~ src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py ~~~ src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_auto_fixer_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_exit_codes_py
    src_zephyr_gov_code_quality_code_dedup_cli_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_report_py
    src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_config_py
    src_zephyr_gov_code_quality_code_dedup_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py
    src_zephyr_gov_code_quality_code_dedup_trackers_init_py -->|config_depends / config_depends| src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py
    src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_god_class_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_reference_helpers_py
    src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_encoding_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_DATA["(生产态 / production) D_DATA"]
    tests_data_test_symbol_normalizer_py -->|测试依赖 / test_depends| D_DATA
    src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_diff_helpers_py
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_init_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_ast_comparator_py
    D_GOV_ENFORCEMENT -->|导入依赖 / import_depends| src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py
    D_GOV_ENFORCEMENT -->|测试依赖 / test_depends| src_zephyr_gov_enforcement_commit_gates_create_guard_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class scripts_governance_d3_metadata_check_pure_assertion_py,scripts_governance_d7_code_check_module_id_consistency_py,src_zephyr_gov_code_quality_init_py,src_zephyr_gov_code_quality_code_dedup_init_py,src_zephyr_gov_code_quality_code_dedup_annotations_py,src_zephyr_gov_code_quality_code_dedup_ast_comparator_py,src_zephyr_gov_code_quality_code_dedup_atomic_fixer_py,src_zephyr_gov_code_quality_code_dedup_auto_fixer_py,src_zephyr_gov_code_quality_code_dedup_behavioral_sampler_py,src_zephyr_gov_code_quality_code_dedup_behavioral_trust_checker_py,src_zephyr_gov_code_quality_code_dedup_cache_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_manager_py,src_zephyr_gov_code_quality_code_dedup_canary_register_py,src_zephyr_gov_code_quality_code_dedup_cli_py,src_zephyr_gov_code_quality_code_dedup_code_analyzer_runner_py,src_zephyr_gov_code_quality_code_dedup_code_simulator_py,src_zephyr_gov_code_quality_code_dedup_config_py,src_zephyr_gov_code_quality_code_dedup_contract_consistency_checker_py,src_zephyr_gov_code_quality_code_dedup_cross_boundary_detector_py,src_zephyr_gov_code_quality_code_dedup_dead_module_detector_py,src_zephyr_gov_code_quality_code_dedup_debt_projector_py,src_zephyr_gov_code_quality_code_dedup_decision_auditor_py,src_zephyr_gov_code_quality_code_dedup_degradation_py,src_zephyr_gov_code_quality_code_dedup_diff_detector_py,src_zephyr_gov_code_quality_code_dedup_doom_loop_guard_py,src_zephyr_gov_code_quality_code_dedup_exit_codes_py,src_zephyr_gov_code_quality_code_dedup_extraction_safety_py,src_zephyr_gov_code_quality_code_dedup_false_negative_auditor_py,src_zephyr_gov_code_quality_code_dedup_fifteen_dimension_auditor_py,src_zephyr_gov_code_quality_code_dedup_file_creator_py,src_zephyr_gov_code_quality_code_dedup_function_discovery_py,src_zephyr_gov_code_quality_code_dedup_grandfather_manager_py,src_zephyr_gov_code_quality_code_dedup_health_monitor_py,src_zephyr_gov_code_quality_code_dedup_integration_hub_py,src_zephyr_gov_code_quality_code_dedup_integrations_py,src_zephyr_gov_code_quality_code_dedup_micro_clone_detector_py,src_zephyr_gov_code_quality_code_dedup_mock_duplicate_generator_py,src_zephyr_gov_code_quality_code_dedup_monoculture_guard_py,src_zephyr_gov_code_quality_code_dedup_observation_window_guard_py,src_zephyr_gov_code_quality_code_dedup_path_index_validator_py,src_zephyr_gov_code_quality_code_dedup_phase_executor_py,src_zephyr_gov_code_quality_code_dedup_policy_tree_validator_py,src_zephyr_gov_code_quality_code_dedup_pre_apply_integrity_gate_py,src_zephyr_gov_code_quality_code_dedup_prioritizer_py,src_zephyr_gov_code_quality_code_dedup_recovery_manifest_writer_py,src_zephyr_gov_code_quality_code_dedup_report_py,src_zephyr_gov_code_quality_code_dedup_risk_mitigator_py,src_zephyr_gov_code_quality_code_dedup_self_scanner_py,src_zephyr_gov_code_quality_code_dedup_sensitivity_sweeper_py,src_zephyr_gov_code_quality_code_dedup_shadow_trust_validator_py,src_zephyr_gov_code_quality_code_dedup_shadow_verifier_py,src_zephyr_gov_code_quality_code_dedup_shared_evolver_py,src_zephyr_gov_code_quality_code_dedup_shared_lifecycle_manager_py,src_zephyr_gov_code_quality_code_dedup_signature_matcher_py,src_zephyr_gov_code_quality_code_dedup_simplicity_auditor_py,src_zephyr_gov_code_quality_code_dedup_ssot_registrar_py,src_zephyr_gov_code_quality_code_dedup_stale_shared_detector_py,src_zephyr_gov_code_quality_code_dedup_success_validator_py,src_zephyr_gov_code_quality_code_dedup_symbol_index_py,src_zephyr_gov_code_quality_code_dedup_thematic_clusterer_py,src_zephyr_gov_code_quality_code_dedup_trackers_init_py,src_zephyr_gov_code_quality_code_dedup_trackers_blind_spot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_consequence_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_hotspot_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_import_surface_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_question_tracker_py,src_zephyr_gov_code_quality_code_dedup_trackers_risk_mitigation_tracker_py,src_zephyr_gov_code_quality_code_dedup_verifier_py,src_zephyr_gov_enforcement_commit_gates_init_py,src_zephyr_gov_enforcement_commit_gates_diff_helpers_py,src_zephyr_gov_enforcement_commit_gates_reference_helpers_py,src_zephyr_gov_enforcement_commit_gates_arch_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_asyncio_run_in_context_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_getenv_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_sql_gate_py,src_zephyr_gov_enforcement_commit_gates_bare_subprocess_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_amodule_cross_check_gate_py,src_zephyr_gov_enforcement_commit_gates_blueprint_format_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_bypass_policy_py,src_zephyr_gov_enforcement_commit_gates_capability_lookup_required_gate_py,src_zephyr_gov_enforcement_commit_gates_capability_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_batch_size_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_final_gate_py,src_zephyr_gov_enforcement_commit_gates_ch_version_col_gate_py,src_zephyr_gov_enforcement_commit_gates_claim_required_gate_py,src_zephyr_gov_enforcement_commit_gates_consumers_accuracy_gate_py,src_zephyr_gov_enforcement_commit_gates_create_guard_py,src_zephyr_gov_enforcement_commit_gates_dangling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_data_task_completeness_gate_py,src_zephyr_gov_enforcement_commit_gates_datetime_now_forbidden_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_freshness_gate_py,src_zephyr_gov_enforcement_commit_gates_depgraph_write_path_gate_py,src_zephyr_gov_enforcement_commit_gates_derivation_annotation_gate_py,src_zephyr_gov_enforcement_commit_gates_directory_contract_gate_py,src_zephyr_gov_enforcement_commit_gates_doc_ref_broken_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_fk_gate_py,src_zephyr_gov_enforcement_commit_gates_domain_name_zh_direct_access_gate_py,src_zephyr_gov_enforcement_commit_gates_empty_handler_gate_py,src_zephyr_gov_enforcement_commit_gates_encoding_gate_py,src_zephyr_gov_enforcement_commit_gates_exempt_zone_frontmatter_gate_py,src_zephyr_gov_enforcement_commit_gates_file_copy_gate_py,src_zephyr_gov_enforcement_commit_gates_file_placement_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_folder_capacity_hard_limit_gate_py,src_zephyr_gov_enforcement_commit_gates_foreign_change_gate_py,src_zephyr_gov_enforcement_commit_gates_forged_gw_marker_gate_py,src_zephyr_gov_enforcement_commit_gates_function_dup_gate_py,src_zephyr_gov_enforcement_commit_gates_gate_repo_py,src_zephyr_gov_enforcement_commit_gates_git_call_budget_gate_py,src_zephyr_gov_enforcement_commit_gates_god_class_gate_py,src_zephyr_gov_enforcement_commit_gates_hardcoded_url_gate_py,src_zephyr_gov_enforcement_commit_gates_held_overlap_gate_py,src_zephyr_gov_enforcement_commit_gates_high_complexity_gate_py,src_zephyr_gov_enforcement_commit_gates_id_uniqueness_gate_py,src_zephyr_gov_enforcement_commit_gates_import_direction_gate_py,src_zephyr_gov_enforcement_commit_gates_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_issue_resolved_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_long_param_list_gate_py,src_zephyr_gov_enforcement_commit_gates_manual_only_permanent_gate_py,src_zephyr_gov_enforcement_commit_gates_mcp_version_field_gate_py,src_zephyr_gov_enforcement_commit_gates_module_id_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_exposure_gate_py,src_zephyr_gov_enforcement_commit_gates_msg_style_gate_py,src_zephyr_gov_enforcement_commit_gates_mutable_const_without_final_gate_py,src_zephyr_gov_enforcement_commit_gates_new_file_depgraph_gate_py,src_zephyr_gov_enforcement_commit_gates_no_import_side_effect_gate_py,src_zephyr_gov_enforcement_commit_gates_noqa_validation_gate_py,src_zephyr_gov_enforcement_commit_gates_open_without_with_gate_py,src_zephyr_gov_enforcement_commit_gates_orphan_module_gate_py,src_zephyr_gov_enforcement_commit_gates_panorama_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_perm_trigger_gate_py,src_zephyr_gov_enforcement_commit_gates_precommit_offline_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_assertion_gate_py,src_zephyr_gov_enforcement_commit_gates_pure_shim_gate_py,src_zephyr_gov_enforcement_commit_gates_r5_digit_suffix_gate_py,src_zephyr_gov_enforcement_commit_gates_reconciler_health_gate_py,src_zephyr_gov_enforcement_commit_gates_relative_path_literal_gate_py,src_zephyr_gov_enforcement_commit_gates_rename_depgraph_sync_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_execution_pairing_gate_py,src_zephyr_gov_enforcement_commit_gates_rule_four_way_alignment_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_commit_verified_gate_py,src_zephyr_gov_enforcement_commit_gates_ruling_reference_gate_py,src_zephyr_gov_enforcement_commit_gates_schema_file_exists_gate_py,src_zephyr_gov_enforcement_commit_gates_scripts_import_integrity_gate_py,src_zephyr_gov_enforcement_commit_gates_session_required_gate_py,src_zephyr_gov_enforcement_commit_gates_snapshot_drift_gate_py,src_zephyr_gov_enforcement_commit_gates_ssot_redefinition_gate_py,src_zephyr_gov_enforcement_commit_gates_table_name_registry_gate_py,src_zephyr_gov_enforcement_commit_gates_test_source_consistency_gate_py,src_zephyr_gov_enforcement_commit_gates_tests_coverage_gate_py,src_zephyr_gov_enforcement_commit_gates_ttl_gate_py,src_zephyr_gov_enforcement_commit_gates_undefined_name_gate_py,src_zephyr_gov_enforcement_commit_gates_unsafe_dict_spread_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_chain_gate_py,src_zephyr_gov_enforcement_commit_gates_vocab_hardcode_gate_py,src_zephyr_gov_enforcement_commit_gates_zephyr_env_direct_access_gate_py,src_zephyr_gov_enforcement_rule_bridge_gate_auto_registrar_py,tests_data_test_symbol_normalizer_py,tests_governance_test_apply_dataflowgraph_smoke_py,tests_governance_test_apply_decisiongraph_smoke_py,tests_governance_test_apply_depgraph_smoke_py,tests_governance_test_audit_return_contract_usage_py,tests_governance_test_audit_worktree_ops_telemetry_py,tests_governance_test_generate_project_depgraph_smoke_py,tests_governance_test_post_commit_guard_no_verify_threshold_py,tests_governance_test_run_silent_failure_regression_py,tests_governance_test_session_startup_health_check_py,tests_governance_test_sync_yaml_to_depgraph_smoke_py production
    class D_GOV_ENFORCEMENT,D_SHARED,D_DATA,D_GOV_AUDIT,D_GOV_SCRIPTS,D_GOVERNANCE external_prod
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 集成协调器 — 24集成+19更新+16GitHub整合. (inte... | → | D_AUTONOMY_CORE 自治核心: context_rule_registry.py | 导入依赖 / import_depends |
| 2 | capability_consistency_gate.py — Provider 路由... | → | D_DATA 数据接入层: Provider Capability 行为契约校验器（裁定... (ca... | 导入依赖 / import_depends |
| 3 | table_name_registry_gate.py — TABLE-NAME-REGIS... | → | D_DATA 数据接入层: 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 导入依赖 / import_depends |
| 4 | test_symbol_normalizer.py — TRAE-082 symbol 标... | → | D_DATA 数据接入层: Symbol 标准化模块——TRAE-082 symbol 约定铁律的... | 测试依赖 / test_depends |
| 5 | code-dedup-engine CLI——子命令映射+退出码+扫描... | → | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引.... | 导入依赖 / import_depends |
| 6 | capability_overlap_gate.py — 新建 .py 文件 Cap... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的.... | 导入依赖 / import_depends |
| 7 | create_guard.py — 新建 .py / 非 rules/ .yaml .... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的.... | 导入依赖 / import_depends |
| 8 | create_guard.py — 新建 .py / 非 rules/ .yaml .... | → | D_GOVERNANCE 生命周期管理: rule_patterns.py — 治理规则正则 + 安全审计模式... | 导入依赖 / import_depends |
| 9 | new_file_depgraph_gate.py — 新建 .py 文件 depg... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (depgraph_... | 导入依赖 / import_depends |
| 10 | rename_depgraph_sync_gate.py — 文件重命名后 de... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (depgraph_... | 导入依赖 / import_depends |
| 11 | ssot_redefinition_gate.py — SSoT 符号重复定义.... | → | D_GOVERNANCE 生命周期管理: CapabilityLookup — 能力->真源文件反查注册表的.... | 导入依赖 / import_depends |
| 12 | test_sync_yaml_to_depgraph_smoke.py — sync_yam... | → | D_GOVERNANCE 生命周期管理: depgraph Schema DDL + 版本化迁移框架 (depgraph_... | 测试依赖 / test_depends |
| 13 | panorama_alignment_gate.py — 三图模块对齐门禁.... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 14 | reconciler_health_gate.py — reconciler 健康度.... | → | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | 导入依赖 / import_depends |
| 15 | _reference_helpers.py — 引用检测门禁共享工具函... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 16 | arch_reference_gate.py — #ARCH-NNN /... (arch_... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 17 | asyncio_run_in_context_gate.py — 异步上下文误.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 18 | bare_getenv_gate.py — 裸 os.getenv 读密钥阻断.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 19 | bare_sql_gate.py — 裸SQL字面量阻断门禁（NO-BAR... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 20 | bare_subprocess_gate.py — 裸 subprocess 调用硬... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 21 | blueprint_amodule_consistency_gate.py — [A_mod... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 22 | blueprint_amodule_cross_check_gate.py — [BLUEP... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 23 | blueprint_format_gate.py — [BLUEPRINT] 头部 mo... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 24 | capability_consistency_gate.py — Provider 路由... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 25 | capability_lookup_required_gate.py — Capabilit... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 26 | capability_overlap_gate.py — 新建 .py 文件 Cap... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 27 | ch_batch_size_gate.py — CH 批量写入防回退门禁.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 28 | ch_final_gate.py — ch_writer.query() 直接调用.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 29 | ch_version_col_gate.py — CH version 列语义误用... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 30 | claim_required_gate.py — claim_files 前置检查.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 31 | consumers_accuracy_gate.py — CONSUMERS 字段准.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 32 | create_guard.py — 新建 .py / 非 rules/ .yaml .... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 33 | dangling_reference_gate.py — AGENTS.md §X.Y .... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 34 | data_task_completeness_gate.py — 数据任务完整.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 35 | datetime_now_forbidden_gate.py — 时间戳约定硬.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 36 | depgraph_freshness_gate.py — depgraph 新鲜度门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 37 | depgraph_write_path_gate.py — depgraph 写入路.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 38 | derivation_annotation_gate.py — 派生关系声明真... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 39 | directory_contract_gate.py — DCR-001~007 等效.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 40 | doc_ref_broken_gate.py — 文档相对路径断裂引用.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 41 | domain_fk_gate.py — [DOMAIN] 头部域注册表 FK .... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 42 | domain_name_zh_direct_access_gate.py — DOMAIN_... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 43 | empty_handler_gate.py — 空事件 handler 函数阻.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 44 | encoding_gate.py — 编码安全校验门禁（治本：弥.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 45 | exempt_zone_frontmatter_gate.py — 豁免区 front... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 46 | file_copy_gate.py — 新增 .py 文件复制检测阻断.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 47 | file_placement_ttl_gate.py — 文件放置与 TTL 一... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 48 | folder_capacity_hard_limit_gate.py — 文件夹容.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 49 | foreign_change_gate.py — 外来变更检测门禁（FOR... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 50 | forged_gw_marker_gate.py — Forged GW Marker 前... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 51 | function_dup_gate.py — 重复函数实现阻断门禁（F... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 52 | git_call_budget_gate.py — Git 调用预算 warn-on... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 53 | god_class_gate.py — God Class 阻断门禁（NO-GOD... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 54 | hardcoded_url_gate.py — 硬编码 localhost URL .... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 55 | held_overlap_gate.py — 搭便车防护门禁（HELD-OV... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 56 | high_complexity_gate.py — 高循环复杂度阻断门禁... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 57 | id_uniqueness_gate.py — pre-commit hook ID 唯.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 58 | import_direction_gate.py — shared 层向上依赖阻... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 59 | import_integrity_gate.py — IMPORT-INTEGRITY 门... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 60 | issue_resolved_integrity_gate.py — ISSUE-RESOL... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 61 | long_param_list_gate.py — 长参数列表阻断门禁（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 62 | manual_only_permanent_gate.py — 永久系统脚本 m... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 63 | mcp_version_field_gate.py — MCP version 字段缺... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 64 | module_id_consistency_gate.py — module_id 三声... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 65 | msg_exposure_gate.py — 错误消息暴露敏感信息阻.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 66 | msg_style_gate.py — 错误消息标点/箭头风格阻断.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 67 | mutable_const_without_final_gate.py — 可变常量... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 68 | new_file_depgraph_gate.py — 新建 .py 文件 depg... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 69 | no_import_side_effect_gate.py — 模块导入零副作... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 70 | noqa_validation_gate.py — 自定义 noqa 标记合规... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 71 | open_without_with_gate.py — open() 未在 with .... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 72 | orphan_module_gate.py — 孤儿模块（无 import 引... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 73 | panorama_alignment_gate.py — 三图模块对齐门禁.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 74 | perm_trigger_gate.py — 永久系统脚本时间触发模.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 75 | precommit_offline_gate.py — pre-commit 配置离.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 76 | pure_assertion_gate.py — 纯陈述原则阻断门禁（P... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 77 | pure_shim_gate.py — 纯 re-export shim 阻断门禁... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 78 | r5_digit_suffix_gate.py — R5 数字后缀目录禁止.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 79 | reconciler_health_gate.py — reconciler 健康度.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 80 | relative_path_literal_gate.py — 相对路径字面量... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 81 | rename_depgraph_sync_gate.py — 文件重命名后 de... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 82 | rule_execution_pairing_gate.py — 规则-执行配对... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 83 | rule_four_way_alignment_gate.py — 规则四方对齐... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 84 | ruling_commit_verified_gate.py — 文档"已完成".... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 85 | ruling_reference_gate.py — 裁定#NNN 悬空引用自... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 86 | schema_file_exists_gate.py — SCHEMA-FILE-EXIST... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 87 | scripts_import_integrity_gate.py — _shared.con... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 88 | session_required_gate.py — session 注册强制门.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 89 | snapshot_drift_gate.py — 运行时违规快照漂移阻.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 90 | ssot_redefinition_gate.py — SSoT 符号重复定义.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 91 | table_name_registry_gate.py — TABLE-NAME-REGIS... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 92 | test_source_consistency_gate.py — 测试-源码符.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 93 | tests_coverage_gate.py — Gate 测试覆盖率校验 m... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 94 | ttl_gate.py — ttl 字段校验门禁（治本：弥补 --n... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 95 | undefined_name_gate.py — UNDEFINED-NAME 门禁（... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 96 | unsafe_dict_spread_gate.py — ``**data`` 直接展... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 97 | vocab_chain_gate.py — SSoT 引用硬编码阻断门禁.... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 98 | vocab_hardcode_gate.py — 新增 .py 文件词表硬编... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 99 | zephyr_env_direct_access_gate.py — ZEPHYR_ENV ... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 100 | gate_auto_registrar.py — YAML 驱动的 in-proces... | → | D_GOV_ENFORCEMENT 规则执行: commit_gate_registry.py — GitCommitGateway pre... | 导入依赖 / import_depends |
| 101 | test_audit_worktree_ops_telemetry.py — worktre... | → | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔.... | 测试依赖 / test_depends |
| 102 | 配置管理 — 策略树 YAML 加载 + 项目规模感知四 T... | → | D_INFRASTRUCTURE 跨层契约基础设施: app_config.py — 应用配置数据类与加载/热重载逻... | 导入依赖 / import_depends |
| 103 | code-dedup-engine CLI——子命令映射+退出码+扫描... | → | D_INFRA_RUNTIME 运行时集成: AssetDiscoveryScanner — MOD-INF-026 L1 全量文.... | 导入依赖 / import_depends |
| 104 | forged_gw_marker_gate.py — Forged GW Marker 前... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (sessio... | 导入依赖 / import_depends |
| 105 | import_integrity_gate.py — IMPORT-INTEGRITY 门... | → | D_SECURITY 对抗验证: Session 级并发协调模块（P2-SES 落地）。 (sessio... | 导入依赖 / import_depends |
| 106 | Stage 0: 函数缓存管理器 — 增量扫描的加速核心. ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 107 | Stage 0: Git diff 变更检测器 — 函数粒度增量. (... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 108 | _reference_helpers.py — 引用检测门禁共享工具函... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 109 | bare_getenv_gate.py — 裸 os.getenv 读密钥阻断.... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 110 | blueprint_format_gate.py — [BLUEPRINT] 头部 mo... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 111 | capability_lookup_required_gate.py — Capabilit... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 112 | create_guard.py — 新建 .py / 非 rules/ .yaml .... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 113 | data_task_completeness_gate.py — 数据任务完整.... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 114 | encoding_gate.py — 编码安全校验门禁（治本：弥.... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 115 | exempt_zone_frontmatter_gate.py — 豁免区 front... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 116 | gate_repo.py — gates 表持久化仓库（AUDIT-07 P1... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 117 | gate_repo.py — gates 表持久化仓库（AUDIT-07 P1... | → | D_SHARED 共享服务: db_utils.py — SQLite 连接公共 API（SSoT: zephy... | 导入依赖 / import_depends |
| 118 | pure_assertion_gate.py — 纯陈述原则阻断门禁（P... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 119 | pure_shim_gate.py — 纯 re-export shim 阻断门禁... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 120 | r5_digit_suffix_gate.py — R5 数字后缀目录禁止.... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 121 | ruling_commit_verified_gate.py — 文档"已完成".... | → | D_SHARED 共享服务: process_pool.py - Shared process pool for MCP s... | 导入依赖 / import_depends |
| 122 | scripts_import_integrity_gate.py — _shared.con... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 123 | test_source_consistency_gate.py — 测试-源码符.... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 124 | gate_auto_registrar.py — YAML 驱动的 in-proces... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引.... | → | Stage 2: AST 级精确比对器. (ast_comparator.py) | 导入依赖 / import_depends |
| 2 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引.... | → | 行为采样验证器 — Stage 0.25 低成本快速验证. (b... | 导入依赖 / import_depends |
| 3 | D_GOVERNANCE 生命周期管理: Self-Benchmark (W3-7) — 5 组已知对自验证 + 引.... | → | 微型克隆检测器 — n-gram频率计数, 1-2行高频模式... | 导入依赖 / import_depends |
| 4 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | → | capability_lookup_bypass_policy.py — CAPABILIT... | 导入依赖 / import_depends |
| 5 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | → | consumers_accuracy_gate.py — CONSUMERS 字段准.... | 导入依赖 / import_depends |
| 6 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | → | scripts_import_integrity_gate.py — _shared.con... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | → | undefined_name_gate.py — UNDEFINED-NAME 门禁（... | 导入依赖 / import_depends |
| 8 | D_GOV_AUDIT 审计追踪: reconciliation_registry.py — GitCommitGateway ... | → | gate_auto_registrar.py — YAML 驱动的 in-proces... | 导入依赖 / import_depends |
| 9 | D_GOV_ENFORCEMENT 规则执行: GitCommitGateway — 全项目唯一合法 git commit .... | → | gate_auto_registrar.py — YAML 驱动的 in-proces... | 导入依赖 / import_depends |
| 10 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔.... | → | commit_gates — GitCommitGateway pre-commit 门.... | 导入依赖 / import_depends |
| 11 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔.... | → | capability_lookup_required_gate.py — Capabilit... | 导入依赖 / import_depends |
| 12 | D_GOV_ENFORCEMENT 规则执行: session_worktree.py — AI 对话 worktree 物理隔.... | → | test_source_consistency_gate.py — 测试-源码符.... | 导入依赖 / import_depends |
| 13 | D_GOV_ENFORCEMENT 规则执行: test_create_guard.py — CREATE-GUARD 门禁单元测... | → | create_guard.py — 新建 .py / 非 rules/ .yaml .... | 测试依赖 / test_depends |
| 14 | D_GOV_ENFORCEMENT 规则执行: test_r5_digit_suffix_gate.py — R5-DIGIT-SUFFIX... | → | r5_digit_suffix_gate.py — R5 数字后缀目录禁止.... | 测试依赖 / test_depends |
| 15 | D_GOV_SCRIPTS 脚本治理: scan_consumers_accuracy.py — CONSUMERS 字段准.... | → | _diff_helpers.py — gate 共享 diff 解析工具模块... | 导入依赖 / import_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: scan_consumers_accuracy.py — CONSUMERS 字段准.... | → | consumers_accuracy_gate.py — CONSUMERS 字段准.... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 10 个外部域直接连接（出边 124 条 + 入边 16 条 = 140 条）。只显示直接连接的域，不展开具体节点。

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
    D_INFRASTRUCTURE["D_INFRASTRUCTURE<br/>跨层契约基础设施"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_CODE_QUALITY -->|87条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_CODE_QUALITY -->|19条 导入依赖 / import_depends| D_SHARED
    D_GOV_CODE_QUALITY -->|8条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_CODE_QUALITY -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_GOV_CODE_QUALITY -->|2条 导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_CODE_QUALITY -->|2条 导入依赖 / import_depends| D_SECURITY
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_INFRASTRUCTURE
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
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
