---
module_id: MOD-INF-069
title: "GPU 上岗热交换模型蓝图 — 两档显存画像/热交换契约/四件套收口引用"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L00_infrastructure
layer_name: infrastructure_operations
functional_domain: infrastructure_operations
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: design
build_status: testing
responsibility_domain: 
---

# MOD-INF-069 GPU Hot Swap Model — GPU 上岗热交换模型契约收口 蓝图

> **module_id**: MOD-INF-069 | **域**: D_INFRA_OPS | **层**: L00 基础设施
> **优先级**: P0 | **来源**: CAND-INFRAOPS-001（B14-04517，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-INF-069

## 1. 定位

A9 运维架构 §0.3 横切层四件套的 GPU 件契约收口。派单边界（W3 裁定）：
**只补 GPU 上岗热交换新内容 + 引用既有 SSOT，禁止重复建 Redis SSOT**。

四件套分工与既有归属：

| 件 | SSOT 归属 | 状态 |
|---|---|---|
| Redis 共享状态（13 命名空间/AOF+RDB） | MOD-INF-063 redis_state_layer_ssot | W2b 已建成 |
| GPU 上岗热交换 | **本模块 MOD-INF-069** | 本批新建 |
| 监控（RED+USE+SLO/4 级告警） | MOD-INF-015 system_telemetry | 既有 |
| 灾备（3-2-1-1-0/RTO<5min/RPO≤1s） | MOD-INF-043 disaster_recovery_backup | 既有 |

## 2. 输入 / 输出

- 输入：上岗会话标识（intraday_inference/postmarket_training）、显存申请量（GB）。
- 输出：
  - `GPU_DUTY_PROFILES`：两档上岗画像真源（盘中推理 8-10GB / 盘后训练 16-18GB）；
  - `HOT_SWAP_CONTRACT`：热备恢复 <5s（取值 4.0s 留 1s 余量）/drain 30s/校验重试 3；
  - `validate_allocation()`：显存预算 Fail-Closed 校验；
  - `plan_swap()`：热交换计划（release → load → verify 有序三步）；
  - `render_gpu_allocation_state()`：gpu:allocation Hash 状态草稿（**仅草稿文本，
    不写 Redis**；key/structure/TTL 引用 MOD-INF-063 gpu 命名空间契约）；
  - `check_four_piece_closure()`：四件套 SSOT 锚点存在性自检。

## 3. 核心规则

1. 两档画像硬边界：盘中推理 8-10GB（交易时段 09:15-15:00）；盘后训练 16-18GB
   （盘后 15:30-次日 08:30）。申请超上限 → GpuHotSwapContractError（Fail-Closed）。
2. 热交换步骤不可乱序：先 release（排空旧画像）→ 再 load（加载目标画像）→
   末 verify（就绪校验，重试上限 3）。同会话交换非法。
3. gpu:allocation 状态契约唯一真源=MOD-INF-063 gpu 命名空间（ops_control 层，
   Hash，永不过期，P5 生产/P4 消费）；本模块只补字段草稿（session/allocated_gb/
   budget_max_gb），不重复建 Redis SSOT。
4. 采集归 trading/gpu_monitor.py（nvidia-smi 快照，MOD-RESOURCE_OPTIMIZATION_ENGINE）；
   本模块不采集，只做契约与校验。
5. 硬边界：系统级显存分配/进程重启/redis 写入全部零执行，留 Owner 窗口。

## 4. 依赖

- `zephyr.infrastructure.redis_state_layer_ssot`（MOD-INF-063，get_namespace("gpu")
  命名空间契约引用）。

## 5. 测试

- `tests/infrastructure/test_gpu_hot_swap_model.py`（14 测：画像真源值/预算
  Fail-Closed/交换计划序/状态草稿与 MOD-INF-063 契约一致/四件套收口自检）。

## 6. 依据

- A9 运维架构 §0.3（docs/_working/架构图/运维架构.md）；
- CAND-INFRAOPS-001（construction_backlog_dig.tsv B14-04517，裁定=做 P0）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-069`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-069` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-INF-069` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-069 | MOD-INF-069 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | testing | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/infrastructure/gpu_hot_swap_model.py` | ✅ 已实现 | |
| `tests/infrastructure/test_gpu_hot_swap_model.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
