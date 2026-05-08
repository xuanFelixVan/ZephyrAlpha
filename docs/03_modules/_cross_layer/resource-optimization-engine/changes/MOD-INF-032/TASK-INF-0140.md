---
task_id: "TASK-INF-0140"
module_id: "MOD-INF-032"
title: "资源优化引擎 Phase 2 —— I/O 优化层（文件缓存 + 流式读取）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-08"
task_type: implementation
phase: scaffold
blueprint_section: "§3.1 (get_cache_stats) + §12.3 Plan (IO_BATCH/STREAMING_READ/CACHE_WARM) + §14 降级矩阵"
estimated_tokens: 5000
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0139"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\io\\file_utils.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\io\\io_cache.py"
    desc: "文件缓存——基于 mtime 的 YAML/JSON 文件缓存，LRU 淘汰"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\io\\streaming_reader.py"
    desc: "流式读取——tail_jsonl + stream_jsonl，内存友好"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\resource_optimization\\test_io_cache.py"
    desc: "缓存单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\resource_optimization\\test_streaming_reader.py"
    desc: "流式读取单元测试"
acceptance_criteria:
  - "AC-01: FileCache 缓存命中时 0 次 I/O，未命中时自动加载并缓存"
  - "AC-02: 缓存键 = 文件路径 + mtime，文件修改后自动失效"
  - "AC-03: 最大缓存 1000 条目，LRU 淘汰，内存占用可查（get_memory_usage_mb）"
  - "AC-04: CacheStats 返回 total_entries/hit_count/miss_count/hit_rate/memory_usage_mb/evictions"
  - "AC-05: tail_jsonl(path, 100) 内存占用 < 100KB（seek 到文件末尾附近读取）"
  - "AC-06: stream_jsonl(path) 生成器模式逐行读取，不全部加载到内存"
  - "AC-07: ResourceOptimizationEngine.get_cache_stats() 返回 CacheStats"
  - "AC-08: CACHE_WARM 策略可预热指定文件列表"
  - "AC-09: STREAMING_READ 策略对 >1MB 文件自动切换流式读取"
  - "AC-10: IO_BATCH 策略合并多个小 I/O 为批量操作"
rollback_instructions: "删除 io_cache.py 和 streaming_reader.py 及其测试。ResourceOptimizationEngine 中移除缓存相关方法"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L824-L845 (§11 Phase 2)"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\resource-optimization-engine\\blueprint.md#L1342-L1353 (§17.4 自动化优化策略)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\io\\file_utils.py"
assigned_agent: any
tags: [resource-optimization, io-cache, streaming-read, lru, file-cache, scaffold]
---

# TASK-INF-0140: 资源优化引擎 Phase 2 — I/O 优化层

## 1. 任务目标

创建 I/O 优化层——FileCache（基于 mtime 的 YAML/JSON 文件缓存，LRU 淘汰）和 StreamingReader（tail_jsonl + stream_jsonl，内存友好的流式读取）。实现 CACHE_WARM/STREAMING_READ/IO_BATCH 三种优化策略。

## 2. 背景

蓝图 §11 Phase 2 定义了 I/O 优化层。当前系统大量读取 YAML 配置文件和 JSONL 日志文件，每次读取都触发磁盘 I/O。通过缓存和流式读取，减少重复 I/O 和内存占用。

## 3. 实施步骤

### Step 1: 创建 io_cache.py
- FileCache 类：缓存键 = (file_path, mtime)，值 = 解析后的 dict
- get(path) → dict | None：命中返回缓存，未命中则加载+缓存
- invalidate(path)：手动失效
- warm(file_list)：预热指定文件
- get_stats() → CacheStats
- LRU 淘汰：max_entries=1000

### Step 2: 创建 streaming_reader.py
- tail_jsonl(path, n=100) → list[dict]：seek 到文件末尾附近，读取最后 n 行
- stream_jsonl(path) → Generator[dict]：逐行 yield，不全部加载

### Step 3: 集成到 ResourceOptimizationEngine
- get_cache_stats() → CacheStats
- 实现 CACHE_WARM/STREAMING_READ/IO_BATCH 策略

### Step 4: 编写单元测试

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/shared/io/io_cache.py` | 新建 |
| 2 | `src/zephyr/shared/io/streaming_reader.py` | 新建 |
| 3 | `tests/unit/resource_optimization/test_io_cache.py` | 新建 |
| 4 | `tests/unit/resource_optimization/test_streaming_reader.py` | 新建 |

## 5. 验收标准

| # | 验收项 | 验证方法 |
|---|--------|---------|
| 1 | 缓存命中时 0 次 I/O | 重复读取测试 |
| 2 | 文件修改后缓存失效 | 修改文件 → 再次读取 → 验证重新加载 |
| 3 | tail_jsonl 内存 < 100KB | 大文件测试 |
| 4 | stream_jsonl 不全部加载 | 生成器逐行消费测试 |
