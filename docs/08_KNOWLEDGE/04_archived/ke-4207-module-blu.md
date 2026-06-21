---
module_id: KE-4050
title: 3. 漂移维度完整清单
category: module_blueprint
---

# 3. 漂移维度完整清单

3. 漂移维度完整清单

检测器覆盖矩阵——每个维度至少一个检测器。📋 = 待实现。

| 维度 ID | 漂移维度 | 检测器 | 严重度 | 状态 |
|---------|---------|--------|:---:|:---:|
| D5-BP-SYNC | 蓝图-代码路径同步 | validate_blueprint_code_sync | HIGH | ✅ |
| D5-YAML-DISK | YAML 注册表 vs 磁盘 | validate_code_yaml_alignment | MEDIUM | ✅ |
| D5-MANIFEST | 静态清单生成器一致性 | validate_static_manifest_drift | HIGH | ✅ |
| D3-D5-NUM | MD vs YAML 数字漂移 | validate_md_yaml_number_drift | HIGH | ✅ |
| D5-IMPL-DOC | 蓝图实现文档合规 | validate_blueprint_implementation_docs | HIGH | ✅ |
| D5-THREE-WAY | 三向一致性（蓝图-YAML-代码） | validate_three_way_consistency | HIGH | ✅ |
| D5-SSOT | SSoT 权威性 | validate_ssot | HIGH | ✅ |
| D5-LIFECYCLE | 模块生命周期状态 | validate_module_lifecycle | MEDIUM | ✅ |
| D4-LAYER | 层级依赖合规 | validate_layer_deps | HIGH | ✅ |
| D5-XREF | 交叉引用完整性 | validate_cross_references | MEDIUM | ✅ |
| D5-DEPS-FMT | depends_on 格式合规 | validate_depends_on_format | MEDIUM | ✅ |
| D5-CONTRACTS | 接口契约对齐 | validate_interface_contracts | HIGH | ✅ |
| D5-DIR | 目录结构规范 | validate_directory_structure | MEDIUM | ✅ |
| D5-DEPRECATED | 废弃路径依赖检测 | validate_deprecated_dependents | HIGH | ✅ |
| D5-GATE-YAML | 门禁 YAML 合规 | validate_gate_yaml | HIGH | ✅ |
| D5-P0-CONTRACTS | P0 模块契约 | validate_p0_module_contracts | HIGH | ✅ |
| D5-ARCH-CONTRACTS | 架构内部契约 | validate_architecture_contract_internal | HIGH | ✅ |
| D5-HANDOFF | 交接包完整性 | validate_handoff_package | MEDIUM | ✅ |
| D5-CONTRACT-IMPL | 蓝图接口 vs 代码实现 | contract_implementation_detector | HIGH | 📋 |
| D5-SEMANTIC | YAML 间语义一致性 | semantic_drift | HIGH | 📋 |
| D5-DB-SCHEMA | DB Schema 三方对账 | db_schema_drift | HIGH | 📋 |
| D5-DEP-VER | 依赖版本一致性 | dep_version_drift | MEDIUM | 📋 |
| D5-SECURITY | 安全策略漂移 | security_policy_drift | HIGH | 📋 |
| D5-DOC-COEVOL | 文档-代码共演化 | doc_code_coevolution | MEDIUM | 📋 |
| D5-TEST-COV | 测试覆盖漂移 | test_coverage_drift | MEDIUM | 📋 |
| AI-IMPORT | AI 幻觉 import | ai_hallucination_import | HIGH | 📋 |
| AI-DEAD-CODE | AI 死码积累 | ai_dead_code | MEDIUM | 📋 |
| AI-BROKEN-LOGIC | AI 逻辑断裂 | ai_broken_logic | HIGH | 📋 |
| AI-DUP-FUNC | AI 重复功能 | ai_duplicate_functionality | MEDIUM | 📋 |
| AI-STYLE | AI 跨 session 风格漂移 | ai_session_style_drift | LOW | 📋 |
| AI-DEPRECATED-API | AI 知识污染 | ai_knowledge_pollution | MEDIUM | 📋 |

---
