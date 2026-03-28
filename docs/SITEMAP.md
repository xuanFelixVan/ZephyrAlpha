---
module_id: SITEMAP_001
version: 1.0
status: Active
last_updated: 2026-03-28
---

# 文档地图 (SITEMAP)

> 清风量化系统 v4.0 的完整文档导航地图

---

## 📍 文档位置导航

### 一级导航

```
docs/
├── 核心文档 (5个)
│   ├── System_Manifest.md
│   ├── API_Contract.md
│   ├── Strategy_Spec_S001.md
│   ├── AI_Permissions.md
│   └── VERSIONING.md
│
├── 索引文件 (4个)
│   ├── INDEX.md
│   ├── BLUEPRINTS.md
│   ├── DELIVERABLES.md
│   └── SITEMAP.md (本文档)
│
├── 蓝图文件 (4个)
│   ├── ARCHITECTURE_BLUEPRINT.md
│   ├── MODULE_BLUEPRINT.md
│   ├── DEPLOYMENT_BLUEPRINT.md
│   └── SECURITY_BLUEPRINT.md
│
├── 参考文档 (3个)
│   ├── FAQ.md
│   ├── CHANGELOG.md
│   └── CODE_STATUS.md
│
├── 00_OVERVIEW/ (系统总览)
├── 01_FRAMEWORK/ (框架说明)
├── 02_FACTOR_LIBRARY/ (因子库)
├── 03_TRADING_TACTICS/ (策略池)
├── 05_IMPLEMENTATION/ (实施指南)
└── 06_ARCHIVE/ (归档)
```

---

## 🗺️ 按用途查找

### 我是新手

**快速上手路线** (30分钟):
1. 阅读 [INDEX.md](./INDEX.md) - 快速入口 (5分钟)
2. 阅读 [00_OVERVIEW/README.md](./00_OVERVIEW/README.md) - 系统总览 (10分钟)
3. 阅读 [05_IMPLEMENTATION/01_QUICKSTART/README.md](./05_IMPLEMENTATION/01_QUICKSTART/README.md) - 快速开始 (15分钟)

---

### 我要理解架构

**架构学习路线** (2小时):
1. 阅读 [System_Manifest.md](./System_Manifest.md) - 系统清单 (20分钟)
2. 阅读 [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) - 架构蓝图 (30分钟)
3. 阅读 [01_FRAMEWORK/README.md](./01_FRAMEWORK/README.md) - Layer 0-7框架 (30分钟)
4. 阅读 [MODULE_BLUEPRINT.md](./MODULE_BLUEPRINT.md) - 模块蓝图 (40分钟)

---

### 我要开发策略

**策略开发路线** (4小时):
1. 阅读 [Strategy_Spec_S001.md](./Strategy_Spec_S001.md) - 策略模板 (30分钟)
2. 阅读 [03_TRADING_TACTICS/INDEX.md](./03_TRADING_TACTICS/INDEX.md) - 策略索引 (20分钟)
3. 阅读 [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](./02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md) - 因子库 (30分钟)
4. 阅读 [05_IMPLEMENTATION/02_DEVELOPMENT/](./05_IMPLEMENTATION/02_DEVELOPMENT/) - 开发规范 (1小时)
5. 实践编写策略代码 (1.5小时)

---

### 我要部署系统

**部署路线** (3小时):
1. 阅读 [DEPLOYMENT_BLUEPRINT.md](./DEPLOYMENT_BLUEPRINT.md) - 部署蓝图 (30分钟)
2. 阅读 [05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md](./05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md) - 部署方案 (30分钟)
3. 阅读 [05_IMPLEMENTATION/03_DEPLOYMENT/one-click-deploy.md](./05_IMPLEMENTATION/03_DEPLOYMENT/one-click-deploy.md) - 一键部署 (20分钟)
4. 执行部署脚本 (1.5小时)

---

### 我要理解安全

**安全学习路线** (1.5小时):
1. 阅读 [SECURITY_BLUEPRINT.md](./SECURITY_BLUEPRINT.md) - 安全蓝图 (45分钟)
2. 阅读 [AI_Permissions.md](./AI_Permissions.md) - AI权限清单 (20分钟)
3. 阅读 [05_IMPLEMENTATION/02_DEVELOPMENT/](./05_IMPLEMENTATION/02_DEVELOPMENT/) - 安全规范 (25分钟)

---

### 我遇到问题

**故障排查路线** (30分钟):
1. 查看 [FAQ.md](./FAQ.md) - 常见问题 (10分钟)
2. 查看 [05_IMPLEMENTATION/04_OPERATIONS/faq.md](./05_IMPLEMENTATION/04_OPERATIONS/faq.md) - 运维FAQ (10分钟)
3. 查看 [CHANGELOG.md](./CHANGELOG.md) - 版本变更 (5分钟)
4. 查看系统日志 (5分钟)

---

## 📂 按目录查找

### 00_OVERVIEW/ - 系统总览

| 文件 | 说明 | 阅读时间 |
|------|------|----------|
| README.md | 系统简介 | 10分钟 |
| DATA_FLOW.md | 数据流与模块依赖 | 15分钟 |
| VERSION_HISTORY.md | 版本演进 | 5分钟 |

---

### 01_FRAMEWORK/ - 框架说明

| 文件 | 说明 | 阅读时间 |
|------|------|----------|
| README.md | Layer 0-7架构说明 | 30分钟 |

---

### 02_FACTOR_LIBRARY/ - 因子库

| 目录 | 说明 |
|------|------|
| 00_INDEX/ | 因子分类导航 |
| 01_METHODOLOGY/ | 因子研究方法论 |
| 02_ALPHA_FACTORS_INDEX.md | 87个Alpha因子索引 |
| 03_RISK_FACTORS/ | 46个风险因子 |
| 04_DATA_SOURCE/ | 数据源说明 |
| 05_BACKTEST/ | 回测报告 |

---

### 03_TRADING_TACTICS/ - 策略池

| 文件 | 说明 |
|------|------|
| INDEX.md | 120个策略导航 |
| 01_STRATEGY_FRAMEWORK/ | 策略框架 |
| 02_TACTICS_MERGED/ | 战术实现 |
| 03_ADVANCED_TACTICS/ | 高级战术 |
| 04_YOUZI_STRATEGIES/ | 游资策略 |

---

### 05_IMPLEMENTATION/ - 实施指南

| 目录 | 说明 |
|------|------|
| 01_QUICKSTART/ | 快速开始 |
| 02_DEVELOPMENT/ | 开发规范 |
| 03_DEPLOYMENT/ | 部署指南 |
| 04_OPERATIONS/ | 运维手册 |

---

### 06_ARCHIVE/ - 归档

| 目录 | 说明 |
|------|------|
| factor-library/ | 因子库历史版本 |
| main/ | 旧版框架 |

---

## 🔍 按关键词查找

### 架构相关

- System_Manifest.md - 系统清单
- ARCHITECTURE_BLUEPRINT.md - 架构蓝图
- 01_FRAMEWORK/README.md - 框架定义
- 00_OVERVIEW/DATA_FLOW.md - 数据流

### 模块相关

- MODULE_BLUEPRINT.md - 模块蓝图
- API_Contract.md - 接口契约
- 00_OVERVIEW/README.md - 模块列表

### 策略相关

- Strategy_Spec_S001.md - 策略模板
- 03_TRADING_TACTICS/INDEX.md - 策略索引
- 02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md - 因子库

### 因子相关

- 02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md - Alpha因子
- 02_FACTOR_LIBRARY/03_RISK_FACTORS/ - 风险因子
- 02_FACTOR_LIBRARY/01_METHODOLOGY/ - 因子方法论

### 部署相关

- DEPLOYMENT_BLUEPRINT.md - 部署蓝图
- 05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md - 部署方案
- 05_IMPLEMENTATION/03_DEPLOYMENT/one-click-deploy.md - 一键部署

### 开发相关

- 05_IMPLEMENTATION/02_DEVELOPMENT/ - 开发规范
- CODE_STATUS.md - 代码状态
- VERSIONING.md - 版本管理

### 安全相关

- SECURITY_BLUEPRINT.md - 安全蓝图
- AI_Permissions.md - AI权限清单
- 05_IMPLEMENTATION/02_DEVELOPMENT/ - 安全规范

### 运维相关

- 05_IMPLEMENTATION/04_OPERATIONS/ - 运维手册
- DEPLOYMENT_BLUEPRINT.md - 部署蓝图
- FAQ.md - 常见问题

---

## 📊 文档统计

| 类型 | 数量 | 说明 |
|------|------|------|
| 核心文档 | 5个 | 必读 |
| 索引文件 | 4个 | 导航 |
| 蓝图文件 | 4个 | 设计 |
| 参考文档 | 3个 | 参考 |
| 目录 | 6个 | 分类 |
| **总计** | **22个** | - |

---

## 🎯 推荐阅读顺序

### 第1天 (2小时)

1. INDEX.md (5分钟)
2. 00_OVERVIEW/README.md (10分钟)
3. System_Manifest.md (20分钟)
4. ARCHITECTURE_BLUEPRINT.md (30分钟)
5. 05_IMPLEMENTATION/01_QUICKSTART/README.md (15分钟)

### 第2天 (2小时)

1. MODULE_BLUEPRINT.md (40分钟)
2. API_Contract.md (15分钟)
3. Strategy_Spec_S001.md (30分钟)
4. 03_TRADING_TACTICS/INDEX.md (20分钟)
5. FAQ.md (15分钟)

### 第3天 (2小时)

1. DEPLOYMENT_BLUEPRINT.md (30分钟)
2. 05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md (30分钟)
3. SECURITY_BLUEPRINT.md (45分钟)
4. VERSIONING.md (15分钟)

---

## 🔗 文档关系图

```
INDEX.md (主入口)
    ↓
    ├→ 00_OVERVIEW/ (系统总览)
    │   ↓
    │   └→ System_Manifest.md (系统清单)
    │       ↓
    │       ├→ ARCHITECTURE_BLUEPRINT.md (架构蓝图)
    │       │   ↓
    │       │   └→ MODULE_BLUEPRINT.md (模块蓝图)
    │       │       ↓
    │       │       └→ API_Contract.md (接口契约)
    │       │
    │       ├→ DEPLOYMENT_BLUEPRINT.md (部署蓝图)
    │       │   ↓
    │       │   └→ 05_IMPLEMENTATION/03_DEPLOYMENT/ (部署指南)
    │       │
    │       └→ SECURITY_BLUEPRINT.md (安全蓝图)
    │           ↓
    │           └→ AI_Permissions.md (权限���单)
    │
    ├→ 01_FRAMEWORK/ (框架说明)
    │   ↓
    │   └→ Strategy_Spec_S001.md (策略模板)
    │       ↓
    │       └→ 03_TRADING_TACTICS/INDEX.md (策略索引)
    │
    ├→ 02_FACTOR_LIBRARY/ (因子库)
    │   ↓
    │   └→ 02_ALPHA_FACTORS_INDEX.md (因子索引)
    │
    ├→ 05_IMPLEMENTATION/ (实施指南)
    │   ├→ 01_QUICKSTART/ (快速开始)
    │   ├→ 02_DEVELOPMENT/ (开发规范)
    │   ├→ 03_DEPLOYMENT/ (部署指南)
    │   └→ 04_OPERATIONS/ (运维手册)
    │
    └→ FAQ.md (常见问题)
```

---

## 📱 移动端访问

所有文档均支持Markdown格式，可在以下平台查看:
- GitHub (在线查看)
- GitLab (在线查看)
- 本地编辑器 (VS Code、Sublime等)
- Markdown阅读器 (Typora、Obsidian等)

---

**最后更新**: 2026-03-28  
**维护者**: 清风量化系统
