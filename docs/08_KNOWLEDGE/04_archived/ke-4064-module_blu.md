---
module_id: KE-3911
title: 14.5 关键优化建议（针对当前实现）
category: module_blueprint
ttl: permanent
---

# 14.5 关键优化建议（针对当前实现）

14.5 关键优化建议（针对当前实现）

| # | 优化点 | 当前状态 | 建议 |
|---|--------|---------|------|
| 1 | **`registry_of_registries.yaml`** | 24 个注册表分布在 3 层，无资产盘点域 | 新增 REG-INV-001 域——让注册表总纲直接指向盘点系统 |
| 2 | **冷启动序列** | STEP 1-5 无盘点步骤 | 新增 STEP 4.5：读 `unified_asset_index.yaml`——让 AI 第一眼就看到资产全貌 |
| 3 | **Phase Manager** | Phase 1 15 检查缺 `gate_asset_inventory` | 新增为第 16 检查——让门控体系自动校验盘点健康 |
| 4 | **SessionContinuity** | `print_restore_summary()` 不含资产信息 | 追加资产摘要行——让 AI session 恢复时自动获得"项目规模认知" |
| 5 | **`risk-register.yaml`** | 无盘点相关风险 | 新增 R17~R19——让风险体系覆盖"盘点系统自身失效" |
| 6 | **MCP Server** | 无资产查询 MCP 服务 | Phase 2：暴露 `query_asset_inventory` MCP 工具——让 IDE 直接查询资产 |
| 7 | **`scaffold.py`** | 不支持蓝图 .md 创建 | 扩展 scaffold 支持 `docs` 类型——让蓝图文件也能走"创建即注册" |
| 8 | **审计协议** | GOV-CMP-003 未显式引用盘点输出 | 在 12 维度审计清单中加入 §DIM-INV: "资产盘点完整性" |

---
