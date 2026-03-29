# 多级存储架构

> 热存储、温存储、冷存储的三级架构

**版本**: v1.0
**更新**: 2026-03-29
**Layer**: Layer 1 (数据层)
**优先级**: P1 - 20年全量回测必需

---

## 1. 为什么1人+AI需要多级存储

| 回测需求 | 数据量 | 需要存储类型 |
|----------|--------|--------------|
| 当日实时交易 | ~实时 | 热存储 (Redis) |
| 近1年策略 | ~5000万行 | 温存储 (SSD) |
| 5年策略 | ~2亿行 | 温/冷过渡 |
| **20年全量回测** | **~10亿+行** | **必须冷存储** |

---

## 2. 三级存储架构

```
┌─────────────────────────────────────────────────────────────┐
│                      数据存储架构                             │
├─────────────────────────────────────────────────────────────┤
│  热存储 (Hot)     │  温存储 (Warm)    │  冷存储 (Cold)      │
│  ┌─────────────┐  │  ┌─────────────┐  │  ┌─────────────┐   │
│  │   Redis     │  │  │  SSD +      │  │  │  HDD +     │   │
│  │   内存      │  │  │  Parquet    │  │  │  Parquet   │   │
│  └─────────────┘  │  └─────────────┘  │  └─────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  延迟: <10ms       │  延迟: <1s        │  延迟: <30s        │
│  成本: 最高        │  成本: 中等        │  成本: 最低        │
│  容量: 64GB        │  容量: 1TB        │  容量: 4TB        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 存储内容定义

### 热存储 (Redis)

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

### 温存储 (SSD + Parquet)

```python
WARM_STORAGE_CONFIG = {
    'ssd_parquet': {
        'data': [
            '近1年日线数据',
            '近3年因子数据',
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

### 冷存储 (HDD + Parquet)

```python
COLD_STORAGE_CONFIG = {
    'hdd_parquet': {
        'data': [
            '1年前历史日线',
            '3年前分钟线(可选)',
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
    """存储层级管理器"""

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
        """获取数据（自动从对应层级读取）"""
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

## 5. 20年数据存储规划

```python
STORAGE_PLAN_20Y = {
    '日线数据 (20年)': {
        'total_rows': 5000 * 5000 * 20,  # ~5亿行
        'columns': ['date', 'open', 'high', 'low', 'close', 'volume'],
        'storage_tier': 'warm',  # 近5年
        'cold_tier': 'cold',     # 5年前
        'estimated_size': '50GB'
    },

    '分钟线数据 (可选)': {
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
        'estimated_size': '1GB/日'
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
        """保存实时数据 → 热存储"""
        self.tier_manager.hot_store.write(f"realtime_{symbol}", data)

    def save_daily(self, symbol: str, date: str, data: pd.DataFrame) -> None:
        """保存日线数据 → 自动分层"""
        tier = self.tier_manager.auto_tier(symbol, date, access_count=0)
        self.tier_manager.write(symbol, data, tier)

    def load_for_backtest(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """加载回测数据 → 自动跨层级读取"""
        result = []

        # 加载冷存储数据
        cold_data = self.tier_manager.cold_store.range_read(symbol, start, end)
        result.append(cold_data)

        # 补充温存储数据
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
        'frequency': '每日一次',
        'retention': '1年'
    },
    'cold': {
        'method': '每周快照',
        'frequency': '每周一次',
        'retention': '永久'
    }
}
```

---

## 8. 硬件建议

| 层级 | 推荐配置 | 预算参考 |
|------|----------|----------|
| 热存储 | 64GB DDR4 + 500GB NVMe SSD | ¥2000-3000 |
| 温存储 | 2TB SATA SSD | ¥1000-1500 |
| 冷存储 | 4TB HDD (7200转) | ¥500-800 |

**总预算参考**: ¥3500-5500

---

## 9. 层级关系

```
Layer 1 (数据层)
    ↓
热存储 (实时) → 温存储 (近1年) → 冷存储 (1-20年)
    ↓              ↓                ↓
策略执行      近期回测          全量回测
```

---

## 索引

- 父目录: [04_INFRASTRUCTURE/README.md](./README.md)
- 相关: [DATA_LINEAGE.md](./DATA_LINEAGE.md)
