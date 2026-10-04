---
ttl: permanent
doc_type: blueprint
module_id: MOD-POS-030
session: st-c9-f42
responsibility_domain: 
---

# blueprint — position_checkup_orchestrator（MOD-POS-030）

> 挖干真源: [docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md](file:///d:/ZephyrAlpha/docs/_working/fullconnect_campaign/e_decision_chain/06_f42_p1_position_checkup.md)（G42-1 处方）
> depgraph 设计节点：module_id=MOD-POS-030（2026-09-29，st-c9-f42 登记，granularity=file；物理 node_id 易变不落文档，需要时按 module_id 查 depgraph）。

## 一句话

把建成未接线的持仓体检五件（P1-01 对账快照/P1-02 分级/P1-03 逻辑存活/P1-04 风险否决/P1-05 组合级漂移）
按 TDM-P-P1 边序串成一条盘前链，动作过裁决中心（MOD-POS-024）+审计，挂 dloop premarket 段
（`daily_loop_master_switch._stage_position_checkup`，dloop_post 16:45 自动圈，事件驱动无 cron）。

## 不做什么

- 不重造五件判定逻辑（全委托既有件）；不下单（观察/记录面，#305 同族安全态）；
- 不伪造持仓数据（上游对账取数面未接线，inputs 缺席=skipped 留痕）；
- 不做盘中持续监控节拍（P1-02/P1-05 的 continuous 语义归既有事件入口，本件=盘前单拍编排）。

## 真源与面

| 面 | 位置 |
|---|---|
| 实现 | src/zephyr/position/core/position_checkup_orchestrator.py |
| 测试 | tests/position/test_position_checkup_orchestrator.py |
| 算法图 | docs/03_modules/_domain_position/algo_flow/position_checkup_orchestrator.yaml |
| 地图节点 | TDM-P-P1（module_ref 本件）+ TDM-P-P1-01..06 |
| 消费者 | zephyr.plan_engine.daily_loop_master_switch（MOD-PLAN-033） |

---

## 1. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/position_checkup_orchestrator.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/position/test_position_checkup_orchestrator.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-030`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-030` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-030` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-030 | MOD-POS-030 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
