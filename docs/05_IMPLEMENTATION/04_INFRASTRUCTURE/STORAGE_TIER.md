---
module_id: STORAGE_TIER
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 多级存储架构文档
---

﻿---
module_id: IMPL_INFRA_STORAGE_TIER_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?---


# 多级存储架构
> **核心职责**: 架构设计和模块关系
> **职责边界**: 
> - ✅ 本文档负责：架构设计和模块关系相关内容
> - ❌ 本文档不负责：其他模块内容


> 热存储、温存储、冷存储的三级架?

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 1 (数据?
**优先?*: P1 - 20年全量回测必需

---

## 1. 为什??AI需要多级存?

| 回测需?| 数据?| 需要存储类?|
|----------|--------|--------------|
| 当日实时交易 | ~实时 | 热存?(Redis) |
| ?年策?| ~5000万行 | 温存?(SSD) |
| 5年策?| ~2亿行 | ?冷过?|
| **20年全量回?* | **~10??* | **必须冷存?* |

---

## 2. 三级存储架构

```
┌─────────────────────────────────────────────────────────────?
?                     数据存储架构                             ?
├─────────────────────────────────────────────────────────────?
? 热存?(Hot)     ? 温存?(Warm)    ? 冷存?(Cold)      ?
? ┌─────────────? ? ┌─────────────? ? ┌─────────────?  ?
? ?  Redis     ? ? ? SSD +      ? ? ? HDD +     ?  ?
? ?  内存      ? ? ? Parquet    ? ? ? Parquet   ?  ?
? └─────────────? ? └─────────────? ? └─────────────?  ?
├─────────────────────────────────────────────────────────────?
? 延迟: <10ms       ? 延迟: <1s        ? 延迟: <30s        ?
? 成本: 最?       ? 成本: 中等        ? 成本: 最?       ?
? 容量: 64GB        ? 容量: 1TB        ? 容量: 4TB        ?
└─────────────────────────────────────────────────────────────?
```

---

## 3. 存储内容定义

### 热存?(Redis)

```python
HOT_STORAGE_CONFIG = {
    'redis': {
        'data': [
            '当日实时行情 (tick/1min)',
            '当前持仓快照',
            '策略信号缓存',
            '实时计算因子'
        ],
        'ttl': {
            'realtime_quote': 86400,      # 当日有效
            'signal_cache': 3600,          # 1小时
            'intraday_factor': 300         # 5分钟
        },
        'memory': '64GB',
        'persistence': True  # RDB + AOF
    }
}
```

### 温存?(SSD + Parquet)

```python
WARM_STORAGE_CONFIG = {
    'ssd_parquet': {
        'data': [
            '?年日线数?,
            '?年因子数?,
            '当前持仓历史',
            '策略回测结果'
        ],
        'partition': {
            'by': ['year', 'asset_type'],
            'format': 'parquet'
        },
        'volume': '1TB SSD',
        'compression': 'snappy'
    }
}
```

### 冷存?(HDD + Parquet)

```python
COLD_STORAGE_CONFIG = {
    'hdd_parquet': {
        'data': [
            '1年前历史日线',
            '3年前分钟?可?',
            '历史因子数据',
            '归档研究结果'
        ],
        'partition': {
            'by': ['year', 'month'],
            'format': 'parquet'
        },
        'volume': '4TB HDD',
        'compression': 'gzip'
    }
}
```

---

## 4. 数据流转策略

```python
class StorageTierManager:
    """存储层级管理?""

    def __init__(self):
        self.hot_store = RedisClient()
        self.warm_store = ParquetStore('warm/')
        self.cold_store = ParquetStore('cold/')

    def auto_tier(self, data_id: str, data_date: str, access_count: int) -> str:
        """自动决定数据存储层级"""
        days_old = (datetime.now() - parse_date(data_date)).days

        if days_old == 0:
            return 'hot'
        elif days_old <= 365:
            return 'warm'
        else:
            return 'cold'

    def move_data(self, data_id: str, from_tier: str, to_tier: str) -> None:
        """数据迁移"""
        data = self._read_from_tier(data_id, from_tier)
        self._write_to_tier(data_id, to_tier, data)

    def get_data(self, data_id: str) -> pd.DataFrame:
        """获取数据（自动从对应层级读取?""
        # 优先从热存储读取
        if self.hot_store.exists(data_id):
            return self.hot_store.read(data_id)

        # 检查温存储
        if self.warm_store.exists(data_id):
            return self.warm_store.read(data_id)

        # 从冷存储读取
        return self.cold_store.read(data_id)
```

---

## 5. 20年数据存储规?

```python
STORAGE_PLAN_20Y = {
    '日线数据 (20?': {
        'total_rows': 5000 * 5000 * 20,  # ~5亿行
        'columns': ['date', 'open', 'high', 'low', 'close', 'volume'],
        'storage_tier': 'warm',  # ??
        'cold_tier': 'cold',     # 5年前
        'estimated_size': '50GB'
    },

    '分钟线数?(可?': {
        'total_rows': 5000 * 240 * 20,  # ~120亿行
        'storage_tier': 'cold',
        'note': '按需加载，不常驻内存',
        'estimated_size': '500GB'
    },

    '因子数据': {
        'storage_tier': 'warm',
        'cold_tier': 'cold',
        'estimated_size': '200GB'
    },

    '实时行情缓存': {
        'storage_tier': 'hot',
        'estimated_size': '1GB/?
    }
}
```

---

## 6. 层级访问接口

```python
class StorageInterface:
    """统一存储接口"""

    def __init__(self):
        self.tier_manager = StorageTierManager()

    def save_realtime(self, symbol: str, data: pd.DataFrame) -> None:
        """保存实时数据 ?热存?""
        self.tier_manager.hot_store.write(f"realtime_{symbol}", data)

    def save_daily(self, symbol: str, date: str, data: pd.DataFrame) -> None:
        """保存日线数据 ?自动分层"""
        tier = self.tier_manager.auto_tier(symbol, date, access_count=0)
        self.tier_manager.write(symbol, data, tier)

    def load_for_backtest(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """加载回测数据 ?自动跨层级读?""
        result = []

        # 加载冷存储数?
        cold_data = self.tier_manager.cold_store.range_read(symbol, start, end)
        result.append(cold_data)

        # 补充温存储数?
        warm_data = self.tier_manager.warm_store.range_read(symbol, start, end)
        result.append(warm_data)

        return pd.concat(result).sort_index()
```

---

## 7. 备份策略

```python
BACKUP_STRATEGY = {
    'hot': {
        'method': 'Redis RDB + AOF',
        'frequency': '每秒增量',
        'retention': '当日'
    },
    'warm': {
        'method': '每日快照',
        'frequency': '每日一?,
        'retention': '1?
    },
    'cold': {
        'method': '每周快照',
        'frequency': '每周一?,
        'retention': '永久'
    }
}
```

---

## 8. 硬件建议

| 层级 | 推荐配置 | 预算参?|
|------|----------|----------|
| 热存?| 64GB DDR4 + 500GB NVMe SSD | 2000-3000 |
| 温存?| 2TB SATA SSD | 1000-1500 |
| 冷存?| 4TB HDD (7200? | 500-800 |

**总预算参?*: 3500-5500

---

## 9. 层级关系

```
Layer 1 (数据?
    ?
热存?(实时) ?温存?(?? ?冷存?(1-20?
    ?             ?               ?
策略执行      近期回测          全量回测
```

---

## 10. 数据备份规划（未来议题）

> **状?*: 暂不实施，先记录在文档中
> **触发条件**: 系统稳定运行3个月?

### 10.1 备份需求分?

| 数据类型 | 备份频率 | 备份方式 | 优先?|
|----------|----------|----------|--------|
| K线数?| 每日增量 | 本地+云端 | ?|
| 因子数据 | 每周全量 | 本地 | ?|
| 舆情数据 | 每日增量 | 云端 | ?|
| 配置/代码 | 实时 | Git仓库 | ?|

### 10.2 备份阶段规划

```
┌─────────────────────────────────────────────────────────────────────?
?                   备份策略实施路线?                                ?
├─────────────────────────────────────────────────────────────────────?
?                                                                    ?
? ══════════════════════════════════════════════════════════════?  ?
? Phase 1: 短期 (系统稳定?                                       ══?
? ══════════════════════════════════════════════════════════════?  ?
? ├── 记录备份需求到文档                                           ?
? ├── 设计备份架构                                                  ?
? ├── 定时备份脚本 ?本地外部硬盘                                  ?
? └── 每日增量 + 每周全量                                          ?
?                             ?                                     ?
? ══════════════════════════════════════════════════════════════?  ?
? Phase 2: 中期 (有条件时)                                         ══?
? ══════════════════════════════════════════════════════════════?  ?
? ├── 云端备份 ?阿里云OSS / 腾讯云COS                            ?
? ├── 异地容灾 ?不同城市数据中心                                  ?
? └── 加密传输 + 加密存储                                          ?
?                             ?                                     ?
? ══════════════════════════════════════════════════════════════?  ?
? Phase 3: 长期 (数据量大?                                       ══?
? ══════════════════════════════════════════════════════════════?  ?
? ├── 分级备份 ?热数据多副本，冷数据归档                          ?
? ├── 增量备份 ?只备份变化部?                                   ?
? └── 合规要求 ?根据监管要求保留审计日志                          ?
?                                                                    ?
└─────────────────────────────────────────────────────────────────────?
```

### 10.3 备份架构设计

```python
BACKUP_ARCHITECTURE = {
    'local': {
        'destination': '外部硬盘 / NAS',
        'frequency': '每日增量 + 每周全量',
        'retention': '30天增?+ 1年全?,
        'automated': True
    },
    'cloud': {
        'provider': '阿里云OSS / 腾讯云COS',
        'frequency': '每日增量',
        'retention': '永久',
'cost_estimate': '50-100/?(100GB)'
    },
    'cross_region': {
        'provider': '阿里?+ 腾讯云双?,
        'frequency': '每周全量',
        'retention': '永久',
        'rto': '<4小时'  # Recovery Time Objective
    }
}
```

### 10.4 备份优先?

| 优先?| 数据类型 | 说明 |
|--------|----------|------|
| P0 | 代码/Git | 版本控制，实时备?|
| P1 | K线数?| 核心数据，每日备?|
| P2 | 因子数据 | 可重新计算，每周备份 |
| P3 | 舆情数据 | 可重新获取，按需备份 |
| P4 | 临时缓存 | 不需要备?|

---

## 索引

- 父目? 04_INFRASTRUCTURE/README.md
- 相关: DATA_LINEAGE.md
