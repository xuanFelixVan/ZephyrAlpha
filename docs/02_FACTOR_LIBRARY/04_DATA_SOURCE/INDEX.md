---
module_id: INDEX_DATA_SOURCE_001
version: 1.0.3
status: Active
created_date: 2026-04-03
last_updated: 2026-04-06
owner: 首席文档架构师
standard_type: 专业量化机构索引
applicable_scope: 数据源目录
compliance_level: 专业标准
parent_document: ../../INDEX.md
implementation_status: 已完成
---

# 数据源目录索引

## 文档职责说明

**本文档职责**: 数据源层索引与导航
- 提供数据源层所有文档的统一入口
- 组织数据源接口、数据管理、数据处理模块
- 维护文档间的引用关系

**职责边界**:
- ✅ 本文档负责: 数据源层文档导航和索引
- ❌ 本文档不负责: 具体数据源实现（由各CONNECTOR文档负责）

> **目录职责**: 数据源接口、数据获取、数据质量管理

## 📁 目录结构

| 子目录/文件 | 职责 | 状态 |
|-------------|------|------|
| [NEWS_SENTIMENT_DATA_SOURCE.md](NEWS_SENTIMENT_DATA_SOURCE.md) | 新闻舆情数据源 | Active |
| [IFIND_CONNECTOR.md](IFIND_CONNECTOR.md) | iFind数据源接口 | Active |
| [BAOSTOCK_CONNECTOR.md](BAOSTOCK_CONNECTOR.md) | Baostock数据源接口 | Active |
| [QMT_INTERFACE.md](QMT_INTERFACE.md) | QMT接口 | Active |
| [SUPERCMD_CONNECTOR.md](SUPERCMD_CONNECTOR.md) | SuperCommand接口 | Active |
| [DATA_ACQUISITION.md](DATA_ACQUISITION.md) | 数据获取方案 | Active |
| [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md) | 数据需求规格 | Active |
| [DATA_SOURCE_ADAPTERS.md](DATA_SOURCE_ADAPTERS.md) | 数据源适配器 | Active |
| [MACRO_DATA.md](MACRO_DATA.md) | 宏观数据 | Active |
| [CORRELATION_ANALYSIS.md](CORRELATION_ANALYSIS.md) | 相关性分析 | Active |
| [STATISTICAL_TOOLS.md](STATISTICAL_TOOLS.md) | 统计工具 | Active |
| [FREE_DATA_SOURCES.md](FREE_DATA_SOURCES.md) | 免费数据源整合 | Active |
| [A_SHARE_HISTORICAL_DATA_PROCESSING_BLUEPRINT.md](A_SHARE_HISTORICAL_DATA_PROCESSING_BLUEPRINT.md) | A股历史数据处理蓝图 | Active |
| [IFIND/](IFIND/) | iFind数据源详细配置 | Active |
| [02_SCHEDULER/](02_SCHEDULER/) | 数据调度 | Active |
| [03_CLEANING/](03_CLEANING/) | 数据清洗 | Active |
| [07_DATA_PIPELINE/](07_DATA_PIPELINE/) | 数据管道 | Active |
| [QUALITY_MANAGEMENT/](QUALITY_MANAGEMENT/) | 数据质量管理 | Active |
| [DATA_SOURCE_LAYER_GAP_ANALYSIS.md](DATA_SOURCE_LAYER_GAP_ANALYSIS.md) | 数据源层架构缺失分析 | Active |
| [DATA_LINEAGE_TRACKING/](DATA_LINEAGE_TRACKING/) | 数据血缘追踪系统 | Blueprint |
| [DATA_VERSION_CONTROL/](DATA_VERSION_CONTROL/) | 数据版本控制系统 | Blueprint |
| [DATA_MONITORING_ENHANCED/](DATA_MONITORING_ENHANCED/) | 数据监控系统（增强） | Blueprint |
| [DATA_CATALOG/](DATA_CATALOG/) | 数据目录系统 | Blueprint |
| [DATA_PERMISSION_MANAGEMENT/](DATA_PERMISSION_MANAGEMENT/) | 数据权限管理系统 | Blueprint |
| [DATA_BACKUP_RECOVERY/](DATA_BACKUP_RECOVERY/) | 数据备份恢复系统 | Blueprint |
| [DATA_API_GATEWAY/](DATA_API_GATEWAY/) | 数据API网关 | Blueprint |
| [DATA_STANDARDIZATION/](DATA_STANDARDIZATION/) | 数据标准化系统 | Blueprint |
| [DATA_SYNC_REPLICATION/](DATA_SYNC_REPLICATION/) | 数据同步复制系统 | Blueprint |
| [DATA_COMPRESSION_ARCHIVE/](DATA_COMPRESSION_ARCHIVE/) | 数据压缩归档系统 | Blueprint |

## 📖 核心文档

### 数据源接口
- [IFIND_CONNECTOR.md](IFIND_CONNECTOR.md) - iFind主数据源
- [BAOSTOCK_CONNECTOR.md](BAOSTOCK_CONNECTOR.md) - Baostock免费数据源
- [NEWS_SENTIMENT_DATA_SOURCE.md](NEWS_SENTIMENT_DATA_SOURCE.md) - 新闻舆情数据源
- [FREE_DATA_SOURCES.md](FREE_DATA_SOURCES.md) - 免费数据源整合

### 数据管理
- [DATA_ACQUISITION.md](DATA_ACQUISITION.md) - 数据获取方案
- [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md) - 数据需求规格
- [DATA_SOURCE_ADAPTERS.md](DATA_SOURCE_ADAPTERS.md) - 数据源适配器
- [QUALITY_MANAGEMENT/](QUALITY_MANAGEMENT/) - 数据质量管理系统
- [DATA_SOURCE_LAYER_GAP_ANALYSIS.md](DATA_SOURCE_LAYER_GAP_ANALYSIS.md) - 架构缺失分析与补充方案

### 增强模块（专业机构标准）
- [DATA_LINEAGE_TRACKING/](DATA_LINEAGE_TRACKING/) - 数据血缘追踪（OpenLineage+Marquez）
- [DATA_VERSION_CONTROL/](DATA_VERSION_CONTROL/) - 数据版本控制（DVC+Delta Lake）
- [DATA_MONITORING_ENHANCED/](DATA_MONITORING_ENHANCED/) - 数据监控增强（Great Expectations）
- [DATA_CATALOG/](DATA_CATALOG/) - 数据目录（DataHub）

## 🔧 补充模块（开源方案）

### P0级模块（立即实施）
| 模块 | 开源方案 | 实施周期 |
|------|----------|----------|
| 数据血缘追踪 | OpenLineage + Marquez | 1周 |
| 数据版本控制 | DVC + Delta Lake | 1周 |
| 数据监控增强 | Great Expectations | 1周 |

### P1级模块（短期实施）
| 模块 | 开源方案 | 实施周期 |
|------|----------|----------|
| 数据目录系统 | DataHub | 2周 |
| 数据API网关 | FastAPI + Redis | 1周 |
| 数据备份恢复 | 自研 | 1周 |

---

**索引版本**: v1.0.3 | **创建日期**: 2026-04-03 | **维护者**: 首席文档架构师
