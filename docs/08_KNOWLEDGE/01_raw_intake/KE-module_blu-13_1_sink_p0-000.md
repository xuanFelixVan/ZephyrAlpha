---
module_id: KE-module_blu-13_1_sink_p0-000
title: 13.1 Sink P0
category: module_blueprint
---

# 13.1 Sink P0

13.1 Sink P0

| # | 用例 | 预期 |
|:-:|------|------|
| P0-S1 | record_metric 单条写入 | 可 query_timeseries 查到 |
| P0-S2 | record_batch 原子性 | 批内一条失败整批回滚 |
| P0-S3 | 吞吐 ≥ 1000 metric/s | WAL 批提，连续 10 秒压测 |
