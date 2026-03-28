# 分布式计算架构

> 分布式计算架构设计
>
> **配套文档**：
> - 主文档：[SPEC.md](../SPEC.md)
> - 低延迟架构：[architecture/low-latency.md](./architecture/low-latency.md)

***

## 1. 架构概述

```
┌─────────────────────────────────────────────────────────────┐
│                     主控节点 (Master Node)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 任务调度器  │  │  结果汇总器 │  │  健康监控   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                     计算节点 (Worker Nodes)                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │  │ Node N  │       │
│  │ 因子计算 │  │ 因子计算 │  │ 因子计算 │  │ 因子计算 │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
```

***

## 2. 任务分配策略

| 分配方式 | 适用场景 | 负载均衡 |
|----------|----------|----------|
| 按股票池分配 | 选股任务 | ⭐⭐⭐⭐⭐ |
| 按时间周期分配 | 回测任务 | ⭐⭐⭐⭐ |
| 按因子类型分配 | 因子计算 | ⭐⭐⭐⭐⭐ |

***

## 3. Python实现

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from typing import List, Callable, Any

class DistributedCalculator:
    """分布式计算"""

    def __init__(self, n_workers: int = 4):
        self.n_workers = n_workers

    def parallel_apply(self,
                     data: pd.DataFrame,
                     func: Callable,
                     groupby_col: str = None,
                     n_chunks: int = None) -> pd.DataFrame:
        """
        并行计算

        Parameters:
        -----------
        data : pd.DataFrame
            输入数据
        func : Callable
            计算函数
        groupby_col : str
            分组列
        n_chunks : int
            分片数量
        """
        if groupby_col:
            groups = data.groupby(groupby_col)
            group_keys = list(groups.groups.keys())
        else:
            n_chunks = n_chunks or self.n_workers
            chunks = np.array_split(data, n_chunks)
            group_keys = range(len(chunks))

        results = []

        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            futures = {}

            for key in group_keys:
                if groupby_col:
                    chunk = groups.get_group(key)
                else:
                    chunk = chunks[key]

                future = executor.submit(self._process_chunk, chunk, func, key)
                futures[future] = key

            for future in as_completed(futures):
                key = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Task {key} failed: {e}")

        return pd.concat(results, ignore_index=True)

    @staticmethod
    def _process_chunk(chunk: pd.DataFrame, func: Callable, key: Any) -> pd.DataFrame:
        """处理单个数据块"""
        result = func(chunk)
        result['_chunk_id'] = key
        return result
```

***

## 4. Tick数据仓库架构

| 组件 | 功能 | 技术选型 |
|------|------|----------|
| 数据存储 | Tick数据持久化 | ClickHouse |
| 数据压缩 | 压缩存储 | ZSTD算法 |
| 查询加速 | 快速检索 | 分区+索引 |
| 数据归档 | 历史数据管理 | 分层存储 |

***

## 5. Tick数据Schema

```sql
CREATE TABLE tick_data (
    timestamp DateTime,
    code String,
    last_price Decimal(10, 3),
    last_volume Int32,
    bid_price1 Array(Decimal(10, 3)),
    ask_price1 Array(Decimal(10, 3)),
    bid_volume1 Array(Int32),
    ask_volume1 Array(Int32),
    INDEX idx_code (code) TYPE bloom_filter,
    INDEX idx_time (timestamp) TYPE minmax
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (code, timestamp);
```

***

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-26 | 整合附录AL内容 |
