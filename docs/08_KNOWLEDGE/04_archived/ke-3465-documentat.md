---
module_id: KE-3330
title: 5.1 选型矩阵
category: documentation
---

# 5.1 选型矩阵

5.1 选型矩阵

| 维度 | Hot Path 🔥 | Warm Path 🌡️ | Cold Path ❄️ |
|---|---|---|---|
| **语言** | C++20 / Rust (stable) / C (kernel modules) | Python >=3.11 / Rust CPython extensions (热点函数) | Python / Scala (Spark) / SQL |
| **运行时** | 裸金属 / 物理机 / DPDK userspace | Linux VM / 容器（K8s Pod）| Spark cluster / Dask cluster / Airflow workers |
| **通信中间件** | Aeron / LMAX Disruptor / ZeroMQ (IPC) / RDMA | Redis Streams / Kafka / FastAPI HTTP / WebSocket | Parquet + S3 / MinIO / Airflow XCom |
| **存储** | Shared Memory Ring Buffer / mmap files | Redis / PostgreSQL / Parquet (hot/warm border) | Parquet (columnar) / DuckDB / S3 object storage |
| **并发模型** | Lock-free ring buffers / SPSC queue / LMAX-style | asyncio event loop / actor model (trio / anyio) | Spark DataFrame / Dask delayed / Ray |
| **GC** | 🚫 禁止（预分配 / arena allocator）| 🟡 Python 默认 GC（acceptable） | 🟢 无所谓 |
| **调度** | CPU 亲和 / NUMA 感知 / 大页内存 | Gunicorn workers + asyncio event loop | Airflow DAG / Prefect Flow / cron |
| **日志** | 零分配结构化日志（lock-free + post-process flush）| `structlog` + OpenTelemetry | 常规 logging，批量写 |
| **监控** | eBPF + 硬件计数器 + 零拷贝 trace | OpenTelemetry SDK + Prometheus exporter | Spark UI + Airflow UI + 基础 metric |
| **部署** | 独立物理机 + NIC bypass（目标 T1 后）| K8s 容器 + HPA | Spark cluster / Ray cluster + object storage |
| **测试** | 硬实时基准 (criterion.rs / google-benchmark) + 延迟直方图 | pytest-asyncio + hypothesis | Spark local mode + dbt test |
