---
module_id: KE-3137
title: 5.2.1 审计入口速查
category: agent_instruction
ttl: permanent
---

# 5.2.1 审计入口速查

5.2.1 审计入口速查

每次施工后或定期运行以下入口即可覆盖全维度审计：

| 入口 | 完整路径 | 是什么 |
|------|---------|--------|
| **治理审计执行协议**（GOV-CMP-003） | [audit-protocol.md](docs/01_policies_and_standards/governance/compliance/audit-protocol.md) | 审什么 / 用什么审 / 怎么审 / 审到什么程度——任何审计任务的唯一入口 |
| **Vibe Coding 会话门禁检查清单**（OPS-VC-005） | [vibe-coding-gate-runbook.md](docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-gate-runbook.md) | AI session 开始/结束时必须过的自检项 |
| **GATE 门禁登记表**（PS-REG-014） | [gate-registry.md](docs/01_policies_and_standards/_registry/catalogs/gate-registry.md) | 所有 pre-commit / CI 门禁的注册表——19 个 GATE 的总清单 |
| **登记表总索引**（PS-REG-MASTER） | [registry-master-index.yaml](docs/01_policies_and_standards/_registry/catalogs/registry-master-index.yaml) | 46 张登记表/契约/Schema/词汇表的统一索引 |
| **资产盘点系统**（MOD-INF-026） | [asset-inventory/blueprint.md](docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md) | 全项目统一资产索引 SSoT——自动发现+分类+对账+生命周期管理。冷启动 STEP 4.5 读 `unified_asset_index.yaml` 了解项目规模与健康状态 |
| **脚本注册表** | [script-manifest.yaml](scripts/governance/script-manifest.yaml) | 所有治理脚本的注册表——run_all.py 调度依据 |
