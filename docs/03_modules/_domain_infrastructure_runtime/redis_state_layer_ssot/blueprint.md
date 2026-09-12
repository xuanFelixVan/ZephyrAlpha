---
module_id: MOD-INF-063
title: "Redis 共享状态层 SSOT 蓝图 — 13 命名空间三层结构/TTL 矩阵/混合持久化参数/恢复 runbook"
doc_type: blueprint
status: Active
version: "0.1.2"
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
build_status: production
responsibility_domain: 
---

# MOD-INF-063 Redis State Layer SSOT — Redis 共享状态层收口 蓝图

> **module_id**: MOD-INF-063 | **域**: D_INFRA_RUNTIME | **层**: L00 基础设施运行时
> **优先级**: P0 | **来源**: CAND-H1FS-004（B14-04531，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-INF-063

## 1. 定位

A9 运维架构 §1.2 的 Redis 7.x 单实例共享状态层是持仓/订单状态恢复根基。
现状散件：MOD-H1_REDIS_HOT（H1 业务热缓存 7 类 Key）+ MOD-INF-002 redis_config
（连接配置单真源）+ MOD-INF-016 state_store_redis（通用状态原语）齐备，但
**13 命名空间三层结构 / TTL 矩阵 / 混合持久化参数 / 8GB 硬限 / AOF 重放优先
恢复流程未收口为 SSOT**。本模块只收口声明与校验，不替代既有散件：

- 连接建连仍归 MOD-INF-002（config/.env.redis 单真源，fail-closed）；
- H1 业务 Key 构造仍归 MOD-H1_REDIS_HOT h1_redis_schema；
- 本模块是 A9 五进程架构（P1~P5）共享状态平面的**参数与契约真源**。

## 2. 输入 / 输出

- 输入：无运行时输入（纯声明）；校验入口接受 Key 字符串 / 命名空间名。
- 输出：
  - `REDIS_NAMESPACE_REGISTRY`：13 命名空间声明（三层归属/Key 模式/生产者/
    消费者/TTL/数据结构/用途）；
  - `REDIS_PERSISTENCE_PROFILE`：RDB 每小时基线 + AOF everysec 增量 +
    maxmemory 8GB 硬限 + volatile-ttl 淘汰 + AOF 重放优先混合恢复（<15s 目标）；
  - `render_redis_conf_draft()`：redis.conf 配置就绪件草稿（**仅草稿文本，
    不执行任何系统级写入**——实际应用属 Owner 窗口）；
  - `recovery_runbook()`：AOF 重放优先混合恢复 runbook 步骤（声明）；
  - `validate_key()` / `ttl_for()` / `check_registry_consistency()`：契约校验。

## 3. 核心规则

1. 三层结构（A9 §1.2 唯一真源图）：
   - 实时数据层（TTL 驱动）：tick/signal/factor/market_state；
   - 状态协调层（持久化）：position/order/strategy/hb；
   - 运维控制层（Pub/Sub+配置）：cmd/alert/config/degrade/gpu。
2. TTL 矩阵：tick=5s / signal=60s / factor=300s / cmd=60s / alert=3600s /
   hb={process} 各进程超时阈值+30s 缓冲；其余永不过期（position/order/
   strategy/market_state/config/degrade/gpu）。
3. 持久化参数：RDB 每小时基线（save 3600 1）+ AOF everysec（交易时段）混合；
   恢复=AOF 重放优先、RDB 基线加速（纯 AOF ~3min → 混合 <15s）。
4. 内存：maxmemory 8GB 硬限（OOM 防护，稳态≈4GB），淘汰策略 volatile-ttl。
5. Fail-Closed：未知命名空间/Key 模式不匹配/TTL 矩阵缺项 → 抛
   RedisStateLayerSotError，禁止静默放行。
6. 配置就绪件边界：本模块只产出 redis.conf 草稿文本与参数声明；系统级
   应用（写 redis.conf / CONFIG SET / 服务重启）属 Owner 窗口，AI 不执行。

## 4. 依赖前置

- 无代码依赖（纯声明零 import 重依赖）。
- 契约对齐：MOD-H1_REDIS_HOT h1_redis_schema（业务 Key 前缀不冲突校验）、
  MOD-INF-002 redis_config（连接层职责边界）、运维架构.md §1.2（设计真源）。

## 5. 验收标准

- 单测全绿（13 命名空间完整性/三层归属/TTL 矩阵值/草稿含 RDB 3600 1 与
  everysec/未知命名空间 Fail-Closed/一致性校验）；相关域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-063`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-063` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-063` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-063 | MOD-INF-063 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/infrastructure/test_redis_state_layer_ssot.py` | ✅ 已实现 | |

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


