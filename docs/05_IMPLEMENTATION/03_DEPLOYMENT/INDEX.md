---
module_id: IMPL_INDEX_DEPLOYMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-04
last_updated: 2026-04-04
owner: 首席文档架构师
responsibility:
  - 系统架构
  - 文档治理
  - 审计系统
standard_type: 专业量化机构索引文档
applicable_scope: 03_DEPLOYMENT目录
compliance_level: 专业标准
parent_document: ../INDEX.md---


# 03_DEPLOYMENT 部署指南索引
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录导航和文档索引相关内容
> - ❌ 本文档不负责：其他模块内容


> **目录职责**: 系统部署与发布管理
> **文档数量**: 2个
> **最后更新**: 2026-04-04

---

## 📋 文档清单

| 文档 | 职责 | 状态 |
|------|------|------|
| [README.md](./README.md) | 部署指南概述 | Active |
| [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) | 部署计划 | Active |

---

## 🎯 快速导航

### 部署流程

1. **阅读概述**: [README.md](./README.md)
2. **制定计划**: [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)

### 部署命令

```powershell
# Windows部署
.\scripts\deploy.ps1

# 验证部署
python scripts/health_check.py

# 启动服务
python scripts/start_server.py
```

---

## 📊 目录统计

| 指标 | 数值 |
|------|------|
| 总文档数 | 2 |
| Active状态 | 2 |
| 索引覆盖率 | 100% |

---

**维护者**: 部署负责人
**创建日期**: 2026-04-04
