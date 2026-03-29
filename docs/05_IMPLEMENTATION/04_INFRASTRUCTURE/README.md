# 基础设施 (INFRASTRUCTURE)

> 数据流水线、数据血缘、多级存储

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 1 (数据层)
**Owner**: AI + 运维

---

## 目录结构

```
04_INFRASTRUCTURE/
├── DAILY_PIPELINE.md     # 每日数据流水线
├── DATA_CLEANING.md      # 数据清洗规则
├── DATA_LINEAGE.md       # 数据血缘追踪 ⭐ AI必需
└── STORAGE_TIER.md       # 多级存储架构 ⭐ 20年回测必需
```

---

## 核心模块

### 1. DATA_LINEAGE.md - 数据血缘

**用途**：AI需要追踪数据来源保证可解释性

**AI用途**：
- 自动记录数据来源
- 追踪数据转换过程
- 生成质量报告
- 解释因子计算过程

**层级**：Layer 1

### 2. STORAGE_TIER.md - 多级存储

**用途**：20年全量回测必需

**存储分层**：
| 层级 | 存储 | 延迟 | 用途 |
|------|------|------|------|
| 热存储 | Redis | <10ms | 当日实时行情 |
| 温存储 | SSD+Parquet | <1s | 近1年日线 |
| 冷存储 | HDD+Parquet | <30s | 1-20年历史数据 |

**层级**：Layer 1

### 3. DAILY_PIPELINE.md - 每日流水线

**用途**：自动化数据采集、清洗、存储

**流水线阶段**：
- 盘前准备 (06:00-09:00)
- 交易时段 (09:00-15:00)
- 盘后处理 (15:00-20:00)
- 夜间处理 (20:00-06:00)

**层级**：Layer 1

### 4. DATA_CLEANING.md - 数据清洗

**用途**：保证数据质量

**清洗规则**：
- 去重
- 缺失值填充
- 异常值处理
- 数据类型转换

**层级**：Layer 1

---

## 层级关系

```
Layer 1 (数据层)
    ↓ 上游
数据源 (API/爬虫)
    ↓
数据清洗 → 数据血缘 → 多级存储
    ↓
因子计算 → 策略信号 → 订单执行
```

---

## 索引

- 父目录: [05_IMPLEMENTATION/README.md](../README.md)
- 相关: [04_DATA_SOURCE/README.md](../../02_FACTOR_LIBRARY/04_DATA_SOURCE/README.md)
