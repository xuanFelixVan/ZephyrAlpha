---
module_id: KE-1211
status: active
title: 二、`docs/` 目录结构
category: governance
---

# 二、`docs/` 目录结构

二、`docs/` 目录结构

```
docs/
├── migration-declaration.md             # 文档体系双轨终止声明
├── index.md                             # 文档体系根索引（抽屉式导航入口）
├── 01_policies_and_standards/           # C/B 轨共享：治理规范 / 标准 / 协议
│   ├── governance/                      # 声明式治理规则（document/、ai/、task/、security/、architecture/、compliance/、data/、module/）
│   ├── operational/                     # 过程式操作手册（vibe_coding/、devops/、migration/）
│   ├── meta/                            # 元规则（关于规则体系的规则）
│   ├── _registry/                       # 注册表+契约（catalogs/、contracts/、schemas/、vocabularies/）
│   ├── domains/                         # 层域特定规则（L00/、L02/、L04/、L07/）
│   └── templates/                       # 文档模板
├── 02_enterprise_architecture/          # C/B 轨共享：企业架构（TOGAF 视图 + 架构模型）
│   ├── target-architecture/             # 目标架构视图（00-overview.md 等）
│   │   └── architecture-model/          # 架构模型 YAML（layers/、contracts/、events/ 等）
│   ├── architecture-rationale-log.md     # 架构决策推导链权威真源（ADR 已迁入 KB:decisions namespace）
│   └── snapshots/                       # 架构快照（architecture-snapshot-*.yaml）
├── 03_modules/                          # C 轨镜像：14 层模块生命周期文档（按层→模块两级组织）
│   ├── _b_track_interfaces/              # B 轨接口合同（原 07_ai_engineering 已合并）
│   ├── _sys-master/                      # 系统级主蓝图（整体架构全貌）
│   ├── _master-blueprint/                 # 系统级聚合蓝图（跨层视图）
│   ├── data/                 #   ├── <module>/blueprint.md + delivery/
│   ├── infra_ops/              #   每个模块一个子目录，所有生命周期产物放在一起
│   ├── factor/                #   （Google Monorepo / Linux FHS 风格：按主体分目录）
│   ├── signal/
│   ├── risk/
│   ├── pf_core/
│   ├── ex_core/
│   ├── reporting/
│   ├── frontend/
│   ├── research/
│   ├── compliance/
│   ├── ml_train/
│   ├── infra_ops/
│   └── simulation/
├── 08_knowledge/                        # 知识管理：项目经验教训（KE）、最佳实践、知识资产
│   └── index.md                         #   知识库抽屉索引入口（planned — M2 KMS 建成后填充）
├── 09_audit/                            # 审计报告（LATEST 覆盖写入）
│   └── reports/                         # 审计报告（全小写）
└── 99_archive/                          # 终态归档（retired-blueprints/ 等）
```

**目录编号保留策略**：04、05（已合并至 03_modules）、06（预留）、07（已合并至 03_modules/_b_track_interfaces/）、11-18（预留）、19（已移出项目至外部工作区）、20-98（预留）的编号**不被允许**临时占用。需新增目录必须走 §七 的 KB 决策记录审批流程。

---
