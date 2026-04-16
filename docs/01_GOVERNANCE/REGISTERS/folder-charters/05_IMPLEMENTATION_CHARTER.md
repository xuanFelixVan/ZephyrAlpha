---
charter_id: 05_IMPLEMENTATION_CHARTER
version: 1.0.0
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
review_cycle: monthly
owner: 实施负责人
---

# 05_IMPLEMENTATION 文件夹宪章

> **定位**: 施工阶段文档与实施规格
> **当前规模**: ~487个文件，结构复杂
> **负责人**: 实施负责人
> **核心挑战**: 蓝图混杂（163个蓝图图纸柜），需区分设计与实施

---

## 1. 核心职责

本目录存储 **施工阶段的实施文档**，包括：

- **施工计划**: MASTER_DEVELOPMENT_PLAN、CONSTRUCTION_PLAN_* 等
- **技术规格**: 模块级技术实现细节
- **运维文档**: 部署、监控、故障处理
- **蓝图图纸柜**（临时）: `06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`（163个，计划迁移至 `03_BLUEPRINTS/`）

**关键边界**: 本目录存储"如何做"，而非"设计什么"（设计在 `01_FRAMEWORK/`）。

---

## 2. 内容边界

### 允许存放的文件类型

| 类型 | 模式 | 示例 | 存放子目录 |
|------|------|------|------------|
| 施工计划 | `CONSTRUCTION_PLAN_*.md` | `CONSTRUCTION_PLAN_L04_ML.md` | 根目录或 `00_MANAGEMENT/` |
| 技术规格 | `*_technical_spec.md` | `portfolio-optimization-spec.md` | `05_TECHNICAL_SPECIFICATIONS/` |
| 实现指南 | `*_guide.md` | `deployment-guide.md` | `02_DEVELOPMENT/` |
| 运维文档 | `*_ops.md` | `monitoring-ops.md` | `07_OPERATIONS/` |
| 蓝图图纸 | `*_blueprint.md` | `config-center-blueprint.md` | `06_CONSTRUCTION_DOCS/01_BLUEPRINTS/`（临时） |

### 禁止存放的文件类型

| 类型 | 原因 | 应放置位置 |
|------|------|------------|
| 架构设计蓝图 | 属于设计阶段 | `01_FRAMEWORK/` |
| 高层系统决策 | 属于治理 | `01_GOVERNANCE/` |
| 审计报告 | 属于审计 | `09_AUDIT/` |
| 知识案例 | 属于知识库 | `08_KNOWLEDGE/` |
| 个人笔记 | 非正式文档 | `08_KNOWLEDGE/` 或删除 |

---

## 3. 二级目录结构

```
docs/05_IMPLEMENTATION/
├── 00_MANAGEMENT/              # 施工管理文档
│   ├── MASTER_DEVELOPMENT_PLAN.md
│   ├── construction-phase-task-list.md
│   └── CONSTRUCTION_PLAN_*.md  # 各层施工计划
├── 01_ARCHITECTURE/            # 架构实施文档（如有）
├── 02_DEVELOPMENT/             # 开发指南
│   ├── SECURITY.md
│   └── *_guide.md
├── 03_TESTING/                 # 测试文档
├── 04_DEPLOYMENT/              # 部署文档
├── 05_TECHNICAL_SPECIFICATIONS/ # 技术规格
│   └── portfolio-performance-evaluation-technical-specification.md
├── 06_CONSTRUCTION_DOCS/       # 施工图纸（含蓝图临时存放）
│   ├── 00_MANAGEMENT/
│   ├── 01_BLUEPRINTS/          # ⚠️ 163个蓝图，计划迁移至 03_BLUEPRINTS/
│   └── 02_IMPLEMENTATION_GUIDES/
└── 07_OPERATIONS/              # 运维文档
    ├── improvements/
    ├── knowledge_base/
    └── standards/
```

---

## 4. 容量限制

| 指标 | 当前值 | 上限 | 状态 |
|------|--------|------|------|
| 总文件数 | ~487 | 500 | 🟡 接近上限 |
| 06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ | 163 | 0（计划清空）| 🔴 需迁移 |
| 子目录数 | 8 | 15 | 🟢 正常 |
| 最大深度 | 4 | 4 | 🟢 达标（但偏深）|

**关键行动**: 
- Phase D 将 `06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` 迁移至 `03_BLUEPRINTS/`
- 预计可减少163个文件，降至~324个

---

## 5. 保留策略

| 内容类型 | TTL | 备注 |
|----------|-----|------|
| 施工计划（活跃） | 永久 | MASTER_DEVELOPMENT_PLAN 等 |
| 施工计划（过时） | 90天 | 价值提取后归档 |
| 技术规格 | 永久 | 除非技术栈变更 |
| 实现指南 | 永久 | 持续更新 |
| 蓝图图纸（临时） | 立即迁移 | 按编号体系规划迁移至 03_BLUEPRINTS/ |

---

## 6. 自动化检查

```bash
# 蓝图混杂检测（识别应迁移的蓝图）
python scripts/governance/diagnose_blueprint_layer_mismatch.py \
  --path docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/

# 目录深度检查
python scripts/hooks/check_directory_naming.py docs/05_IMPLEMENTATION/

# 文档放置位置合规性
python scripts/hooks/check_document_placement.py
```

---

## 7. 与其他目录的关系

- **上游设计输入**: `01_FRAMEWORK/`（蓝图设计）
- **上游治理要求**: `01_GOVERNANCE/`（标准与规范）
- **下游审计**: `09_AUDIT/`（施工质量审计）
- **知识沉淀**: `08_KNOWLEDGE/`（施工经验提炼）

**蓝图流向**:
```
01_FRAMEWORK/ (设计蓝图) 
  ↓ 设计冻结
05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ (施工图纸，临时)
  ↓ Phase D 迁移
03_BLUEPRINTS/ (按层组织的最终蓝图库)
```

---

## 8. 已知问题与改进计划

| 问题 | 优先级 | 计划解决时间 | 解决方案 |
|------|--------|--------------|----------|
| 蓝图混杂（163个在施工中）| P1 | Phase D | 迁移至 `03_BLUEPRINTS/` |
| 目录深度偏深（4层）| P2 | Phase D | 扁平化结构调整 |
| 文件数接近上限 | P2 | Phase D | 蓝图迁移后降至324 |
| 与 06_CONSTRUCTION_DOCS（空壳）重复 | P0 | 已完成 | 空壳已删除 |

---

## 9. 变更历史

| 版本 | 日期 | 变更 | 变更人 |
|------|------|------|--------|
| v1.0.0 | 2026-04-16 | 初始创建 | AI Assistant |

---

**相关链接**:
- [MASTER_DEVELOPMENT_PLAN](../../05_IMPLEMENTATION/00_MANAGEMENT/MASTER_DEVELOPMENT_PLAN.md)
- [subsystem-registry.yaml](../../subsystem-registry.yaml)
- [目录编号重设计划](../11_STRATEGIC_DECISION/directory-numbering-redesign-plan.md)
