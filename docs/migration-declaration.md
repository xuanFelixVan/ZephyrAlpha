---
doc_type: declaration
module_id: ROOT-DECL-001
layer: cross_layer
status: Active
version: "1.0.0"
date: "2026-05-02"
owner: ZephyrAlpha-Owner
ttl: permanent
summary: "文档体系双轨终止声明——老树只读，新树为唯一活跃文档体系"
depends_on:
  - target: GOV-DOC-002
    at: "§5.3"
    why: "架构合并说明——blueprints/construction_plans/delivery → modules/"
---

# 文档体系双轨终止声明

## 一、双轨已终止

ZephyrAlpha 项目历史上存在两套并行的文档体系：

| 体系 | 路径 | 状态 |
|------|------|:--:|
| **老树** | `_DO_NOT_USE_old_tree/` | 归档只读 |
| **新树** | `docs/` | **唯一活跃体系** |

自 2026-05-01 起，老树已物理归档到 `_DO_NOT_USE_old_tree/`。所有新的文档创建、修改、引用均以新树为唯一真源。

## 二、合并说明

新树已完成以下架构合并（详见 GOV-DOC-002 v3.0.0 §5.3）：

| 旧（v2.x） | 新（v3.0.0+） |
|-----------|-------------|
| `03_blueprints/`（蓝图） | → 合并为 `03_modules/` |
| `04_construction_plans/`（施工图） | → 合并为 `03_modules/` |
| `05_delivery_and_construction/`（交付） | → 合并为 `03_modules/` |

**设计原则**：同一模块的所有生命周期产物（蓝图 → 施工图 → 交付）在同一模块子目录下。Google Monorepo / Linux FHS 风格——按主体分目录，不按文档类型分目录。

## 三、对 AI 的约束

1. **新文件**：只在新树 `docs/` 下创建。老树禁止写入
2. **找文件**：以新树的 `index.md` 体系为唯一导航入口
3. **引路径**：所有文档内路径引用指向新树
4. **老树文件**：仅供历史参考，不作为当前规则来源（见 AGENTS.md §2-3）

## 四、例外

- `AGENTS.md`（项目根）同时存在于两套体系中，但以新树版本的规则为准
- 老树中的 ADR 原稿保留作历史审计证据，不做迁移
