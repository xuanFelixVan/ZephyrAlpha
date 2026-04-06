---
module_id: INDEX_DATA_SOURCE_001
version: 1.0.2
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

---

**索引版本**: v1.0.2 | **创建日期**: 2026-04-03 | **维护者**: 首席文档架构师
