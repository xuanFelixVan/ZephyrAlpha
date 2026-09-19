---
module_id: MOD-INF-PROC-INCUBATOR
submodule_path: src/zephyr/shared/infra/process_incubator.py
title: "统一进程孵化入口蓝图 — 孵化即登记（父PID/预期寿命/进程树）+水位门禁+收割协同"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.0.4"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-09-16"
ttl: permanent
actual_disk_path: "src/zephyr/shared/infra/process_incubator.py"
last_updated: "2026-09-16"
last_verified: "2026-09-16"
generation: 3
functional_domain: operations
summary: "统一进程孵化入口（治理战役 M1+M2）——9-15 事故（9 孤儿 llama-server ≈12GB）结构性缺口治本：孵化即登记（child_pid/parent_pid/祖先链/expected_lifetime_s 落盘 .runtime/process_incubator/ledger.jsonl），spawn 前水位门禁（≥85% 有界等待、≥reject 线拒绝，reject 线引用 resource_optimization.yaml emergency 阈值勿收编），登记表=reaper（M3）收割依据替代 cmdline 猜测；兼容迁移面 spawn_registered 同 spawn_python_hidden 签名。"
tags: [process-spawn, incubation-ledger, water-gate, orphan-prevention, process-pool, reaper, m1, m2]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: MOD-INF-016
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-016
    at: "全篇"
    why: "Shared Infrastructure——复用 process_pool.spawn_python_hidden 孵化原语"
  - target: MOD-INF-002
    at: "§3"
    why: "resource_optimization.yaml 水位阈值真源（引用不收编）"
references: []
codification_level: L1
codification_at: "2026-09-16"
responsibility_domain: 
build_status: stable
design_maturity: production
---

# 统一进程孵化入口蓝图（MOD-INF-PROC-INCUBATOR）

> module_id: MOD-INF-PROC-INCUBATOR | version: 1.0.4 | status: active | layer: L0_infrastructure
> actual_disk_path: src/zephyr/shared/infra/process_incubator.py | generation: 3 | construction_progress: completed

## 1. 背景与动因（治理战役 M1+M2，2026-09-16）

- 挖矿地图 §4 发现 2：process_pool（孵化，60+ 消费方）与 ProcessLifecycleGateway 双轨并存，
  孵化不收割；§4 发现 3：无人做系统级内存看护——"水位高时照样启动重任务"。
- 9-15 事故直接动因：boot detached spawn ollama serve → 9 孤儿 llama-server ≈12GB → commit 触顶。

## 2. 架构（三件）

1. **孵化即登记（M1）**：`ProcessIncubator.spawn()` 每次孵化落盘
   `IncubationRecord`（record_id/child_pid/parent_pid/root_pid/ancestor_chain/name/cmd/
   spawned_at/expected_lifetime_s/owner）到 `.runtime/process_incubator/ledger.jsonl`
   （safe_write_text CAS）。登记=reaper（M3）收割依据，替代 cmdline 特征猜测。
2. **水位门禁（M2）**：`SpawnWaterGate.check_or_wait()`——Windows 水位=commit charge
   percent（psutil.swap_memory，即事故口径）；≥queue_at(85) 有界等待（默认 30s）重试；
   ≥reject_at（引用 config/resource_optimization.yaml `pressure_thresholds.memory_emergency_percent`
   ——仅引用不收编，缺席兜底 90）抛 `WaterLevelRejected`。fail-open：探测异常按 0 放行
   （门禁不误杀）；登记 IO 失败不回滚 spawn 但告警（进程已出，回滚无意义）。
3. **兼容迁移面**：spawn() 与 process_pool.spawn_python_hidden 同签名（登记参数全缺省），
   消费方改 import 行即迁移；60+ 消费方渐进迁移（首批判=auto_runtime_core ollama serve、
   services_registry 服务孵化、reconcile_runner、write_audit_daemon、worktree_drift_watchdog）。

## 3. 协同与收割（M3）

- reaper（process_reaper.py，零 zephyr import 隔离）以 stdlib 读 ledger.jsonl：
  超预期寿命且仍存活的进程 → 树杀 + 回写 reaped 戳（cmdline 兜底矩阵仍并存）。
- ledger 目录经环境变量 `ZEPHYR_INCUBATOR_LEDGER_DIR` 重定向（测试隔离主通道）。

## 4. 边界（不做什么）

- 不替代 MCPProcessPool 池化复用语义；不改 ProcessLifecycleGateway（渐进迁移对象）；
- 不做进程优先级/亲和（NSSM 件已裁，见裁定#256）；门禁 fail-open 不误杀短命轻进程。

## 5. 测试与验收

- `tests/shared/test_process_incubator.py`：登记读写/水位门禁三态（放行/排队等待/拒绝）/
  sweep 对账/mark_reaped/stats/真实 spawn 端到端（python -c sleep 子进程，tmp ledger）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-PROC-INCUBATOR`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-PROC-INCUBATOR` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-PROC-INCUBATOR` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-PROC-INCUBATOR | MOD-INF-PROC-INCUBATOR | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/shared/infra/process_incubator.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


