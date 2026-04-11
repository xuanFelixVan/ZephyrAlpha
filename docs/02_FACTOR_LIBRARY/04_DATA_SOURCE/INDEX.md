---
module_id: FACTOR_LIBRARY_04_DATA_SOURCE_INDEX
version: 1.0.1
status: Active
created_date: 2026-04-07
last_updated: '2026-04-11'
owner: 文档管理团队
responsibility:
  - 目录导航
  - 模块索引
  - 职责协调
standard_type: 索引文档
applicable_scope: 因子库数据源层
compliance_level: 专业标准
parent_document: ../INDEX.md
---
# 04_DATA_SOURCE 数据源目录索引

> **核心职责**: 数据源目录导航、模块索引、数据治理协调
> **职责边界**: 
> - ✅ 本文档负责：目录导航、模块索引、数据治理协调
> - ❌ 本文档不负责：具体数据源实现、数据处理逻辑、其他模块内容

---

## 📋 概述

数据源层负责因子计算所需的所有数据获取、清洗、存储和治理工作，是因子库的基础设施层。

## 上级与接力

- [02_FACTOR_LIBRARY 索引](../INDEX.md)
- [全仓库文件治理任务清单 §7](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md#7-一次性深度治理目录队列与退出标准)
- [治理工具总索引](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)
- [09_AUDIT STATE 索引](../../09_AUDIT/STATE/INDEX.md)

### 索引健全性与目录体量（P5 §7）

- **零入链扫描（最新）**：[../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260420.md](../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260420.md)（`scan_index_health.py --prefix docs/02_FACTOR_LIBRARY/04_DATA_SOURCE --date 20260420`；**zero_inbound=0**；候选 md **81**）
- **rollup（深度 3 前缀条数）**：[../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md](../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md)（检索 `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE` **83** 条）

## 📂 目录结构

### 本目录文档

- [README](./README.md) - 数据源层整体说明
- [OVERVIEW](./FACTOR_LIB_DATA_SOURCE_OVERVIEW.md) - 数据源层概览
- [INDEX](./INDEX.md) - 本文档，数据源目录索引

### 核心数据模块

- [02_SCHEDULER](./02_SCHEDULER/) - 数据调度器
- [03_CLEANING](./03_CLEANING/) - 数据清洗
- [07_DATA_PIPELINE](./07_DATA_PIPELINE/) - 数据流水线

### 数据治理模块

- [CONFIG_MANAGEMENT](./CONFIG_MANAGEMENT/) - 配置管理
- [DATA_CATALOG](./DATA_CATALOG/) - 数据目录
- [DATA_CONTRACT](./DATA_CONTRACT/) - 数据契约
- [DATA_LINEAGE_TRACKING](./DATA_LINEAGE_TRACKING/) - 数据血缘追踪
- [DATA_STANDARDIZATION](./DATA_STANDARDIZATION/) - 数据标准化

### 数据质量模块

- [DATA_ANOMALY_DETECTION](./DATA_ANOMALY_DETECTION/) - 数据异常检测
- [DATA_MONITORING_ENHANCED](./DATA_MONITORING_ENHANCED/) - 增强数据监控
- [DATA_OBSERVABILITY](./DATA_OBSERVABILITY/) - 数据可观测性
- [DATA_PROFILING](./DATA_PROFILING/) - 数据画像
- [DATA_TESTING_FRAMEWORK](./DATA_TESTING_FRAMEWORK/) - 数据测试框架

### 数据存储模块

- [TIME_SERIES_STORAGE](./TIME_SERIES_STORAGE/) - 时序存储
- [DATA_COMPRESSION_ARCHIVE](./DATA_COMPRESSION_ARCHIVE/) - 数据压缩归档
- [DATA_BACKUP_RECOVERY](./DATA_BACKUP_RECOVERY/) - 数据备份恢复
- [DATA_SYNC_REPLICATION](./DATA_SYNC_REPLICATION/) - 数据同步复制
- [DATA_VERSION_CONTROL](./DATA_VERSION_CONTROL/) - 数据版本控制

### 数据服务模块

- [DATA_API_GATEWAY](./DATA_API_GATEWAY/) - 数据API网关
- [DATA_FEDERATION](./DATA_FEDERATION/) - 数据联邦
- [DATA_ORCHESTRATION_ENHANCED](./DATA_ORCHESTRATION_ENHANCED/) - 增强数据编排
- [REALTIME_DATA_STREAMING](./REALTIME_DATA_STREAMING/) - 实时数据流

### 数据安全模块

- [DATA_PERMISSION_MANAGEMENT](./DATA_PERMISSION_MANAGEMENT/) - 数据权限管理
- [DATA_SECURITY_PRIVACY](./DATA_SECURITY_PRIVACY/) - 数据安全隐私

### 数据生命周期模块

- [DATA_LIFECYCLE_MANAGEMENT](./DATA_LIFECYCLE_MANAGEMENT/) - 数据生命周期管理

### 外部数据源

- [IFIND](./IFIND/) - iFind数据源
  - factor_list.csv - 因子列表
  - factor_master_index.csv - 因子主索引

---

## 🎯 模块职责矩阵

| 模块类型 | 模块名称 | 核心职责 | 状态 |
|---------|---------|---------|------|
| **核心数据** | 02_SCHEDULER | 数据调度与任务编排 | 规划中 |
| **核心数据** | 03_CLEANING | 数据清洗与质量控制 | 规划中 |
| **核心数据** | 07_DATA_PIPELINE | 数据流水线管理 | 规划中 |
| **数据治理** | CONFIG_MANAGEMENT | 配置管理与版本控制 | 规划中 |
| **数据治理** | DATA_CATALOG | 数据目录与元数据管理 | 规划中 |
| **数据治理** | DATA_CONTRACT | 数据契约与接口定义 | 规划中 |
| **数据治理** | DATA_LINEAGE_TRACKING | 数据血缘追踪 | 规划中 |
| **数据治理** | DATA_STANDARDIZATION | 数据标准化与规范 | 规划中 |
| **数据质量** | DATA_ANOMALY_DETECTION | 数据异常检测 | 规划中 |
| **数据质量** | DATA_MONITORING_ENHANCED | 增强数据监控 | 规划中 |
| **数据质量** | DATA_OBSERVABILITY | 数据可观测性 | 规划中 |
| **数据质量** | DATA_PROFILING | 数据画像与分析 | 规划中 |
| **数据质量** | DATA_TESTING_FRAMEWORK | 数据测试框架 | 规划中 |
| **数据存储** | TIME_SERIES_STORAGE | 时序数据存储 | 规划中 |
| **数据存储** | DATA_COMPRESSION_ARCHIVE | 数据压缩归档 | 规划中 |
| **数据存储** | DATA_BACKUP_RECOVERY | 数据备份恢复 | 规划中 |
| **数据存储** | DATA_SYNC_REPLICATION | 数据同步复制 | 规划中 |
| **数据存储** | DATA_VERSION_CONTROL | 数据版本控制 | 规划中 |
| **数据服务** | DATA_API_GATEWAY | 数据API网关 | 规划中 |
| **数据服务** | DATA_FEDERATION | 数据联邦查询 | 规划中 |
| **数据服务** | DATA_ORCHESTRATION_ENHANCED | 增强数据编排 | 规划中 |
| **数据服务** | REALTIME_DATA_STREAMING | 实时数据流处理 | 规划中 |
| **数据安全** | DATA_PERMISSION_MANAGEMENT | 数据权限管理 | 规划中 |
| **数据安全** | DATA_SECURITY_PRIVACY | 数据安全隐私保护 | 规划中 |
| **数据生命周期** | DATA_LIFECYCLE_MANAGEMENT | 数据生命周期管理 | 规划中 |
| **外部数据源** | IFIND | iFind数据源集成 | 活跃 |

---

## 🔗 依赖关系

```
外部数据源 (IFIND)
    ↓
数据获取 (02_SCHEDULER)
    ↓
数据清洗 (03_CLEANING)
    ↓
数据存储 (TIME_SERIES_STORAGE)
    ↓
数据治理 (DATA_CATALOG, DATA_CONTRACT, DATA_STANDARDIZATION)
    ↓
数据质量 (DATA_MONITORING_ENHANCED, DATA_ANOMALY_DETECTION)
    ↓
数据服务 (DATA_API_GATEWAY, REALTIME_DATA_STREAMING)
    ↓
因子计算层
```

---

## 📊 统计信息

| 统计项 | 数量 |
|--------|------|
| 子目录总数 | 26 |
| 活跃模块 | 1 (IFIND) |
| 规划中模块 | 25 |
| CSV数据文件 | 2 |

---

## 🚀 实施优先级

### P0 - 核心模块（立即实施）
1. IFIND - iFind数据源集成
2. 02_SCHEDULER - 数据调度器
3. 03_CLEANING - 数据清洗
4. TIME_SERIES_STORAGE - 时序存储

### P1 - 治理模块（短期实施）
1. DATA_CATALOG - 数据目录
2. DATA_CONTRACT - 数据契约
3. DATA_MONITORING_ENHANCED - 数据监控
4. DATA_API_GATEWAY - API网关

### P2 - 扩展模块（中期实施）
1. DATA_ANOMALY_DETECTION - 异常检测
2. DATA_LINEAGE_TRACKING - 血缘追踪
3. DATA_OBSERVABILITY - 可观测性
4. REALTIME_DATA_STREAMING - 实时流

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.1 | 2026-04-11 | P5 §7：门面互指 `INDEX_HEALTH_20260420`（零入链 0）+ `rollup_20260414`（本前缀 83 条）；上级与治理工具链 | 文档管理团队 |
| v1.0.0 | 2026-04-07 | 初始版本，建立数据源目录索引体系 | 文档管理团队 |
