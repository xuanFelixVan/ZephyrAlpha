---
module_id: MOD-INF-064
title: "P3 交易核心进程规格 SSOT 蓝图 — 核 8-11 独占/8GB 禁 swap/心跳 2s/10s/HC-01 不自动重启"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L00_infrastructure
layer_name: infrastructure_runtime
functional_domain: infrastructure_runtime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: production
build_status: stable
responsibility_domain: 
---

# MOD-INF-064 Trading Core Process Spec — P3 交易核心进程规格 蓝图

> **module_id**: MOD-INF-064 | **域**: D_INFRA_RUNTIME | **层**: L00 基础设施运行时
> **优先级**: P0 | **来源**: CAND-H1FS-003（B14-04524，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-INF-064

## 1. 定位

A9 运维架构 §1.1 五进程架构中 P3（trading_core，pri=15）是交易生命线：
风控检查 / 订单构建 / miniQMT 下单 / 持仓同步四职责。交易运行时散件
（MOD-INF-035 auto_runtime_core / 订单 / 执行）齐备，但**独立进程规格
（独占核 / 禁 swap / HC-01 约束）未收口**。本模块收口 P3 进程规格为唯一真源：

- 核 8-11 独占绑定（避免其他进程 CPU 抖动）；
- 内存 8GB 峰值上限 + 禁止 swap（避免 GC 停顿与页面换入）；
- 风控 NN 常驻显存 2GB（GPU OOM 紧急卸载时保留不卸载）；
- 分级心跳 hb:trading_core 2s 间隔 / 10s 超时（TTL=超时+30s 缓冲，
  动态计算真源委托 MOD-INF-063 hb 命名空间）；
- HC-01：任何时段**不自动重启**，仅告警 + 人工介入。

## 2. 输入 / 输出

- 输入：无运行时输入（纯声明）；校验入口接受规格字段。
- 输出：`TRADING_CORE_SPEC` 单例声明；`heartbeat_key()`/`heartbeat_ttl_seconds()`
  心跳契约；`render_process_spec_declaration()` 配置就绪件声明 dict
  （YAML 可序列化，**仅声明不执行**——核亲和/禁 swap 等系统级设置属 Owner 窗口）。

## 3. 核心规则

1. 规格字段唯一真源=A9 §1.1 进程矩阵（P3 行）+ §2.2 Hot 平面资源表。
2. Fail-Closed：规格畸形（空职责/心跳间隔≥超时/核号重复或越界/内存非正）→
   抛 TradingCoreSpecError。
3. 硬边界：本模块只产出配置声明；SetProcessAffinityMask / 禁 swap / 显存常驻
   等系统级应用属 Owner 窗口，AI 不执行。
4. HC-01 不可降级：restart_policy=alert_only_always，任何字段不得将其放宽。

## 4. 依赖前置

- MOD-INF-063 redis_state_layer_ssot（hb 命名空间 dynamic_ttl 复用，不重造 +30s 缓冲规则）。
- 契约对齐：A9 §1.1/§2.2（设计真源）、MOD-INF-035（auto_runtime_core 运行时散件边界）。

## 5. 验收标准

- 单测全绿（规格常量真源值/畸形 Fail-Closed/心跳键与 TTL/声明 dict 含
  Owner 窗口标注/HC-01 不可放宽）；相关域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-064`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-064` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-064` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-064 | MOD-INF-064 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/trading/trading_core_process_spec.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_trading_core_process_spec.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
