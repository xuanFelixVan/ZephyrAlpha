---
module_id: IMPL_README_001
version: 1.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-03
owner: 首席文档架构师
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部署
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 基础设施 (INFRASTRUCTURE)

> 数据流水线、多级存储

**版本**: v1.1
**更新**: 2026-04-03
**Layer**: Layer 1 (数据层)
**Owner**: AI + 运维

---

## 目录结构

```
04_INFRASTRUCTURE/
├── DAILY_PIPELINE.md     # 每日数据流水线
├── STORAGE_TIER.md       # 多级存储架构 ⭐ 20年回测必需
└── README.md             # 本文档
```

**⚠️ 归档说明**:
- `DATA_CLEANING.md` 已归档至 `docs/06_ARCHIVE/duplicate_documents/20260403_layer1_infrastructure_audit/`
- `DATA_LINEAGE.md` 已归档至 `docs/06_ARCHIVE/duplicate_documents/20260403_layer1_infrastructure_audit/`
- 数据清洗相关内容请参考: [DATACLEANER_TECHNICAL_SPECIFICATION.md](../05_TECHNICAL_SPECIFICATIONS/DATACLEANER_TECHNICAL_SPECIFICATION.md)
- 数据血缘相关内容请参考: [DATA_LINEAGE_TRACKING_BLUEPRINT.md](../06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DATA_LINEAGE_TRACKING_BLUEPRINT.md)

---

## 核心模块

### 1. DAILY_PIPELINE.md - 每日流水线

**用途**：自动化数据采集、清洗、存储

**流水线阶段**：
- 盘前准备 (06:00-09:00)
- 交易时段 (09:00-15:00)
- 盘后处理 (15:00-20:00)
- 夜间处理 (20:00-06:00)

**层级**：Layer 1

### 2. STORAGE_TIER.md - 多级存储

**用途**：20年全量回测必需

**存储分层**：
| 层级 | 存储 | 延迟 | 用途 |
|------|------|------|------|
| 热存储 | Redis | <10ms | 当日实时行情 |
| 温存储 | SSD+Parquet | <1s | 近3年日线 |
| 冷存储 | HDD+Parquet | <30s | 1-20年历史数据 |

**层级**：Layer 1

---

## 层级关系

```
Layer 1 (数据层)
    ↑ 上游
数据源(API/爬虫)
    ↓
数据清洗 → 数据血缘 → 多级存储
    ↓
因子计算 → 策略信号 → 订单执行
```

---

## 索引

- 父目录: [05_IMPLEMENTATION/README.md](../README.md)
- 相关: [04_DATA_SOURCE/README.md](../../02_FACTOR_LIBRARY/04_DATA_SOURCE/README.md)
- 归档: [20260403_layer1_infrastructure_audit](../../06_ARCHIVE/duplicate_documents/20260403_layer1_infrastructure_audit/README.md)
