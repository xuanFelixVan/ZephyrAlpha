---
module_id: KE-1035
status: active
title: 5.3 `03_modules/` (C 轨镜像)
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 5.3 `03_modules/` (C 轨镜像)

5.3 `03_modules/` (C 轨镜像)

**用途**：14 层模块生命周期文档。每个模块一个子目录，所有生命周期产物（蓝图含施工指引 → 交付记录）放在同一模块目录下（Google Monorepo / Linux FHS 风格：按主体分目录，不按文档类型分目录）。

> **2026-05-02 更新**：蓝图和施工指引已合并为一份 2026-05-26 升级：施工细节职责从蓝图转移到任务卡（详见 GOV-TASK-001 6），蓝图只写设计，任务卡写施工。 `blueprint.md`（§1-§11 架构设计 + §12 施工指引）。不再需要独立的 `construction-plan.md`。历史施工图保留在 `delivery/` 下作为审计证据。

**内部结构**：
```
03_modules/
├── data/          # L00 层
│   ├── <module-name>/        # 每个模块一个子目录
│   │   ├── blueprint.md      # 蓝图：模块架构设计
│   │   ├── construction-plan.md  # 施工图：实施步骤与验收标准
│   │   └── delivery/         # 交付记录（按版本）
│   │       └── v1.0.0.md
│   └── ...
├── infra_ops/       # L01 层
└── ...（共 14 层 L00-L13）
```

**准入规则**：
- ✅ `l<NN>_*/` 模块目录
- ✅ 模块目录下 `blueprint.md` / `delivery/`
- ❌ 非 C 轨业务层的文档
- ❌ 5 大 AI 服务的接口文档（→ `03_modules/_b_track_interfaces/`）
- ❌ 项目级元计划（→ `01_policies_and_standards/operational/devops/`）

**与 GOV-DOC-002 v2.x 的变化**：

| v2.x（旧） | v3.0.0（新） |
|-----------|-------------|
| `03_blueprints/` 只有蓝图、`04_construction_plans/`、`05_delivery_and_construction/` | 合并为 `03_modules/`；蓝图和施工指引统一为一份 `blueprint.md` |
| 蓝图+施工图分为两份文件 | 一份 `blueprint.md` 覆盖全流程（§1-§11 架构 + §12 施工指引） |
| 平铺施工图目录（1500 个文件不可行） | 模块子目录隔离（每个目录 3-5 个文件） |
