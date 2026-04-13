---
module_id: IMPL_INDEX_DEPLOYMENT_001
version: 1.0.1
status: Active
created_date: 2026-04-04
last_updated: '2026-04-11'
owner: 首席文档架构师
responsibility:
- 目录导航与文档索引管理与优化维护
standard_type: 专业量化机构索引文档
applicable_scope: 03_DEPLOYMENT目录
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 活跃维护
layer: layer_05
---


# 03_DEPLOYMENT 部署指南索引

> **核心职责**: 目录导航和文档索引
> **职责边界**:
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容

> **目录职责**: 系统部署与发布管理
> **文档数量**: 6 个 Markdown
> **最后更新**: 2026-04-11

```
```---
```

## 上级与接力

- [05_IMPLEMENTATION 索引](../INDEX.md)
- ~~[本目录 README（概述）]~~
- 全仓库文件治理任务清单 §7
- 治理工具总索引
- [09_AUDIT STATE 索引](../../09_AUDIT/STATE/INDEX.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260429.md（`scan_index_health.py --prefix docs/05_IMPLEMENTATION/03_DEPLOYMENT --date 20260429`；**zero_inbound=0**；候选 md **6**；首轮 **`INDEX`/`README`** 零入链，已由 [`05_IMPLEMENTATION/INDEX.md`](../INDEX.md) 显式补链 + 本页链 `README` 后复跑归零）
- **rollup（深度 3 前缀条数）**：../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md（检索 `docs/05_IMPLEMENTATION/03_DEPLOYMENT` **6** 条）

```
```---
```

## 📋 文档清单

| 文档 | 职责 | 状态 |
|------|------|------|
| ~~[README.md]~~ | 部署指南概述 | Active |
| DEPLOYMENT_PLAN.md | 部署计划 | Active |
| DEPLOYMENT_GUIDE.md | 部署操作指南 | Active |
| DATA_MIGRATION_GUIDE.md | 数据迁移指南 | Active |
| ENVIRONMENT_CONFIG_GUIDE.md | 环境配置指南 | Active |

```
```---
```

## 🎯 快速导航

### 部署流程

1. **阅读概述**: ~~[README.md]~~
2. **制定计划**: DEPLOYMENT_PLAN.md
3. **执行部署**: DEPLOYMENT_GUIDE.md

### 部署命令

```powershell
# Windows部署
.\scripts\deploy.ps1

# 验证部署
python scripts/health_check.py

# 启动服务
python scripts/start_server.py
```

```
```---
```

## 📊 目录统计

| 指标 | 数值 |
|------|------|
| 总文档数 | 6 |
| Active状态 | 6 |
| 索引覆盖率 | 100% |

```
```---
```

**维护者**: 部署负责人
**创建日期**: 2026-04-04
