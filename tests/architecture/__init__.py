# [A_test] module_id: SRC-TST-0061 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
# [BLUEPRINT] MOD-TEST-219 | tests/architecture/__init__.py | §
# [TTL] task_bound
"""
tests/architecture/ — 架构适应度函数（Architectural Fitness Functions）

本目录包含系统级的架构不变式测试。与单元测试不同，这些测试不验证业务逻辑，
而是验证**架构属性本身是否仍然成立**。它们是防止架构腐烂的最后防线。

在 100% AI 开发语境下，AI 可能在不经意间违反架构约束——本测试套件
是自动化监理。任何失败都意味着架构退化，必须在合并前修复。

不变式清单
----------
- test_layer_isolation           — 域只从合法来源导入，依赖方向正确
- test_no_upward_dependencies    — 低层不依赖高层（架构方向不变式）
- test_cross_layer_via_contracts — 跨层数据交换必须走 shared/contracts/
- test_no_import_cycles          — 模块间不存在循环依赖
- test_contract_yaml_python_consistency — Python dataclass 与 YAML SSoT 一致
- test_no_float_in_money_paths   — 热路径上不使用 float（必须 Decimal）
- test_document_frontmatter_completeness — 所有模块文件有完整的 frontmatter 元数据
- test_governance_document_links  — 治理文档之间的交叉引用不存在死链

SSoT: ADR-0009, cross_layer_contracts.yaml, 架构盲点补全分析
"""

from __future__ import annotations
