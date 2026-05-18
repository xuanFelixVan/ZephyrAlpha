# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §
"""
代码去重引擎（Code Dedup Engine）— MOD-INF-017 · v0.10.0

全生命周期 · 七维模型 · 46 模块 · 二十五维闭环

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

全生命周期七维模型
━━━━━━━━━━━━━━━━━━━
  ① Prevent   — 生成时预防：Context Engine 注入共享API影子清单 + 渐进式三层记忆注入
  ② Block     — 提交时拦截：Pre-commit 增量扫描变更文件 → 命中已知重复模式 → BLOCKED
  ③ Audit     — 定期扫描：全量 MinHash + AST 深度扫描，发现累积的语义重复
  ④ Fix       — 自动修复：高置信度+高适配性重复→安全提取到 shared+替换引用+Doom Loop检测
  ⑤ Register  — SSoT注册：提取的函数自动注册到 shared + 更新 AGENTS.md + KB持久化
  ⑥ Evolve    — 进化沉淀：重复模式→FLE→evolve()→EvolutionProposal→KB存储
  ⑦ Health    — 健康监控：去重健康仪表盘（Health Score+引入速率+债务预测+引擎自观指标）

扩展阶段：
  ⑧ Self-Protect   — 引擎自保护：扫描自身源码 + Codegen覆盖检测 + Dogfooding
  ⑨ Lifecycle      — 生命周期管理：共享函数Deprecation→Grace Period→Sunset→Retirement
  ⑩ Anti-Degrade   — 防退化：Doom Loop日志 + 设计模式白名单 + 幂等性自校验

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

二十五维闭环（§1.4）
━━━━━━━━━━━━━━━━━━━
  01. 生成时预防  — AI写代码前就知道哪些函数已存在
  02. 提交时拦截  — Pre-commit增量扫描，阻止新重复引入
  03. 定期扫描    — 全量深度扫描，发现累积的语义重复
  04. 安全提取评估 — 修复前评估Suitability Score+影响范围+部分提取适配
  05. 自动修复    — 高置信度重复→安全提取+替换引用+Doom Loop检测
  06. SSoT注册    — 提取函数自动注册到shared API清单+KB持久化
  07. 进化沉淀    — 重复模式反馈给FLE→evolve()→KB存储
  08. 健康监控    — Dedup Health Score+引入速率+债务预测+引擎自观指标
  09. 自保护      — 引擎Dogfooding+Codegen覆盖防护+冷启动性能预期
  10. 防退化      — 共享函数生命周期管理+Import表面积负债追踪+设计模式白名单
  11. Monoculture免疫 — BRS 0-100+去重成功悖论（消除重复=单点故障爆炸半径增大）
  12. 原子修复+漏报可视 — WAL式修复原子性+崩溃恢复+三层漏报盲审（Sweep+Canary+抽样）
  13. 引擎自审计  — Simplicity Audit月度自审·SAS 0-100·NET_NEGATIVE→自动退役建议
  14. 死共享模块检测 — 整个shared/子模块退役→DEAD→自动标记删除
  15. 提取后稳定观察期 — 对标Microsoft SDP/Netflix Staged Rollout·提取→14天观察→验证稳定
  16. 恢复失败的恢复 — R0-R3四层递归恢复安全网·R2纯文本Recovery Manifest
  17. 噪声信号比·主题聚类 — 50组重复→3个主题·IEEE TSE告警疲劳研究落地
  18. 影子清单行为正确性 — behavior_signature+全量扫描重新采样验证+行为漂移DIVERGED告警
  19. 并发修改防护  — Pre-Apply Integrity Gate·SHA256重验证+ABORT冲突报告
  20. 微型克隆检测 — n-gram频率计数·1-2行高频模式聚合·Vibe Coding微克隆密度3.8x
  21. 提取后自动测试生成 — 类型驱动+金丝雀录制+契约测试·对标Google Mozart
  22. API契约一致性验证 — 存在性·行为正确性·契约一致性三维信任模型
  23. 跨边界克隆感知 — SRC_TEST_BRIDGE/SRC_SCRIPTS_DIVERGENCE/CROSS_LAYER_REDUNDANCY/VENDORED_REIMPLEMENTATION
  24. 去重决策审计链 — DecisionFingerprint不可变追加日志+证据包+可回滚
  25. 共享函数主动发现 — 签名驱动+语义驱动双通道·从被动拦截→主动赋能

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

五阶段检测流水线（增强版）
━━━━━━━━━━━━━━━━━━━━━━━━━
  Stage 0    — 缓存预热+变更检测（毫秒级）·function_cache.json·原子写入
  Stage 0.5  — 签名指纹碰撞检测（毫秒级）·O(1)精确匹配·路径感知阈值
  Stage 0.25 — 行为采样快速验证（秒级）·低测试覆盖安全网·纯函数判定
  Stage 1    — 词法级Type-1检测（秒级）·Token序列归一化+MD5哈希+归一化名称匹配
  Stage 2    — AST结构级Type-2/3检测（秒级）·子树归一化哈希+变量名归一化
  Stage 3    — 语义级Type-4检测（分钟级）·MinHash+LSH+嵌入相似度+LLM裁决
  Stage 4    — 策略树裁决（秒级）·置信度聚合+策略树YAML评估+输出决策

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

46 模块清单
━━━━━━━━━━━
  Wave 1 基础检测流水线（13模块）：
    W1-01  cli.py                      — CLI入口·五档退出码·dry-run/check/fix/audit
    W1-02  scanner.py                  — 文件扫描器·增量/全量·Git变更检测
    W1-03  cache_manager.py            — 缓存管理器·签名指纹·原子写入·完整性校验
    W1-04  fingerprint.py              — 签名指纹引擎·SHA256+AST子树哈希+MinHash
    W1-05  lexical_detector.py         — 词法级Type-1检测·Token序列归一化
    W1-06  ast_detector.py             — AST结构级Type-2/3检测·子树归一化哈希
    W1-07  semantic_detector.py        — 语义级Type-4检测·MinHash+嵌入+LLM
    W1-08  policy_tree.py              — 策略树裁决·置信度聚合·YAML策略配置
    W1-09  health_reporter.py          — 健康报告·Health Score 0-100·趋势仪表盘
    W1-10  gate_integrator.py          — 门禁集成·GATE-DEDUP pre-commit钩子
    W1-11  session_logger.py           — Session Log落地·Wave 1即落地交接
    W1-12  manifest_manager.py         — Manifest管理·共享API清单维护
    W1-13  config.py                   — 配置管理·策略树YAML加载·规模感知阈值

  Wave 2 自保护+自动修复+生命周期（20模块）：
    W2-14  auto_fixer.py               — 自动修复引擎·提取到shared+替换引用
    W2-15  doom_loop_detector.py       — Doom Loop检测·3次失败→停止+Owner告警
    W2-16  extraction_safety.py        — 安全提取评估·Suitability Score·影响范围
    W2-17  suitability_scorer.py       — 适配性评分器·0-100多维评估
    W2-18  scale_aware_threshold.py    — 规模感知阈值·5000行魔咒自适应
    W2-19  verifier.py                 — 修复验证器·import+类型+行为采样
    W2-20  dedup_debt_planner.py       — 去重债务规划·还本付息计划·ROI排序
    W2-21  self_scanner.py             — 引擎自扫描·Dogfooding·引擎源码去重
    W2-22  codegen_guard.py            — Codegen覆盖防护·BLIND-CODGEN-INIT-OVERWRITE
    W2-23  lifecycle_manager.py        — 共享函数生命周期·Deprecation→Retirement
    W2-24  import_surface_tracker.py   — Import表面积负债追踪·SBS 0-100
    W2-25  pattern_whitelist.py        — 设计模式白名单·Strategy/Adapter/Factory
    W2-26  cold_start_manager.py       — 冷启动管理器·预期性能基线
    W2-27  idempotency_guard.py        — 幂等性保证·确定性哈希+版本锁定
    W2-28  multi_session_state.py      — 多Session状态机·Session A→B→C一致性
    W2-29  cross_tool_adapter.py       — 跨AI工具适配·Claude/GPT-5/Gemini格式
    W2-30  partial_extractor.py        — 部分共享提取·LCS核心+差异保留
    W2-31  impact_analyzer.py          — 提取影响预分析·调用方影响评估
    W2-32  behavioral_sampler.py       — 行为采样验证·Stage 0.25·采样输入生成
    W2-33  engine_metrics.py           — 引擎自观指标·FPR/检测延迟/修复成功率

  Wave 3 闭环生态+整合+盲点关闭（13模块）：
    W3-34  monoculture_monitor.py      — Monoculture免疫监控·BRS 0-100追踪
    W3-35  atomic_fixer.py             — 原子性修复·WAL式fix_plan+崩溃恢复
    W3-36  grandfather_laws.py         — Grandfather三定律·古老重复管理
    W3-37  false_negative_audit.py     — 漏报盲审·Sweep+Canary+抽样·FNR追踪
    W3-38  shadow_trust.py             — Shadow Manifest信任链·ImportError防护回路
    W3-39  temporal_drift.py           — 时态签名漂移追踪·渐进类型化检测
    W3-40  simplicity_audit.py         — 引擎成本效益自审计·SAS 0-100
    W3-41  dead_module_detector.py     — 死共享模块检测·模块级DEAD标记
    W3-42  observation_window.py       — 提取后稳定观察期·14天验证
    W3-43  recovery_recovery.py        — 恢复失败的恢复·R0-R3四层安全网
    W3-44  thematic_clustering.py      — 主题聚类·噪声信号比·告警疲劳缓解
    W3-45  concurrency_guard.py        — 并发修改检测·Pre-Apply Integrity Gate
    W3-46  micro_clone_detector.py     — 微型克隆检测·n-gram频率计数·1-2行聚合
    W3-47  auto_test_generator.py      — 提取后自动测试生成·类型驱动+金丝雀+契约
    W3-48  contract_verifier.py        — API契约一致性验证·三维信任模型
    W3-49  cross_boundary.py           — 跨边界克隆感知·四大边界差异化策略
    W3-50  decision_auditor.py         — 决策审计链·DecisionFingerprint不可变日志
    W3-51  function_discovery.py       — 共享函数主动发现·签名+语义双通道
    W3-52  risk_mitigator.py           — 45项风险全量缓解任务执行器
    W3-53  integration_hub.py          — 24集成+19更新+16GitHub整合协调器
    W3-54  phase_executor.py           — 6Phase施工执行器·从包初始化到全量基线
    W3-55  file_creator.py             — 文件创建清单执行器·75文件创建
    W3-56  blind_spot_tracker.py       — 盲点关闭追踪·自动验证覆盖

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

模块职责总计：66模块 = Wave1(13) + Wave2(20) + Wave3(23) + 扩展模块(10)
核心主题：Monoculture免疫·原子修复·决策审计链·主动发现·漏报可视·微克隆感知·测试生成·契约验证·跨边界·全生命周期治理·自审计闭环

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

借鉴来源：Google Kythe+Tricorder · Meta Glean+Pyre · SonarQube · PMD CPD · JetBrains IntelliJ ·
         CodeAnt AI · ASE 2025 · ACL 2025 RPG · CCFinder · Deckard · Sourcegraph Cody ·
         Google Mozart · Microsoft SDP · Netflix Staged Rollout · ACM MSR 2024 · IEEE ICPC 2023
"""
from . import annotations
from . import atomic_fixer
from . import auto_test_generator
from . import behavioral_trust_checker
from . import blind_spot_tracker
from . import cache_manager
from . import canary_manager
from . import canary_register
from . import cli
from . import code_analyzer_runner
from . import code_simulator
from . import consequence_tracker
from . import contract_consistency_checker
from . import cross_boundary_detector
from . import dead_module_detector
from . import debt_projector
from . import doom_loop_guard
from . import extraction_safety
from . import fifteen_dimension_auditor
from . import file_creator
from . import function_discovery
from . import grandfather_manager
from . import health_monitor
from . import hotspot_tracker
from . import import_surface_tracker
from . import integrations
from . import mock_duplicate_generator
from . import observation_window_guard
from . import path_index_validator
from . import phase_executor
from . import policy_tree_validator
from . import pre_apply_integrity_gate
from . import prioritizer
from . import question_tracker
from . import recovery_manifest_writer
from . import risk_mitigation_tracker
from . import risk_mitigator
from . import shadow_trust_validator
from . import shadow_verifier
from . import shared_evolver
from . import shared_lifecycle_manager
from . import ssot_registrar
from . import stale_shared_detector
from . import success_validator
from . import symbol_index
from . import temporal_drift_tracker
from . import thematic_clusterer
from . import verifier

__all__ = ['annotations', 'ast_comparator', 'atomic_fixer', 'auto_fixer', 'auto_test_generator', 'behavioral_sampler', 'behavioral_trust_checker', 'blind_spot_tracker', 'cache_manager', 'canary_manager', 'canary_register', 'cli', 'code_analyzer_runner', 'code_simulator', 'config', 'consequence_tracker', 'contract_consistency_checker', 'cross_boundary_detector', 'dead_module_detector', 'debt_projector', 'decision_auditor', 'degradation', 'diff_detector', 'doom_loop_guard', 'exit_codes', 'extraction_safety', 'false_negative_auditor', 'fifteen_dimension_auditor', 'file_creator', 'function_discovery', 'grandfather_manager', 'health_monitor', 'hotspot_tracker', 'import_surface_tracker', 'integration_hub', 'integrations', 'micro_clone_detector', 'mock_duplicate_generator', 'monoculture_guard', 'observation_window_guard', 'path_index_validator', 'phase_executor', 'policy_tree_validator', 'pre_apply_integrity_gate', 'prioritizer', 'question_tracker', 'recovery_manifest_writer', 'report', 'risk_mitigation_tracker', 'risk_mitigator', 'scanner', 'self_benchmark', 'self_scanner', 'sensitivity_sweeper', 'shadow_trust_validator', 'shadow_verifier', 'shared_evolver', 'shared_lifecycle_manager', 'signature_matcher', 'simplicity_auditor', 'ssot_registrar', 'stale_shared_detector', 'success_validator', 'symbol_index', 'temporal_drift_tracker', 'thematic_clusterer', 'verifier']  # 66 模块（全生命周期治理）


__version__ = "0.15.0"
__module_id__ = "MOD-INF-017"
__layer__ = "l01_infrastructure"
__status__ = "construction"
__owner__ = "ZephyrAlpha-Owner"
