---
module_id: MOD-CD-001
submodule_path: scripts/ops/shadow_canary_deploy.py
title: "CD Pipeline 蓝图 — Shadow Canary 灰度发布基建（簇C，满足 EX-021 门禁 CI/CD 半）"
doc_type: blueprint
template_for: blueprint
status: Draft
version: "0.1.3"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-08-03"
valid_from: "2026-08-03"
ttl: permanent
actual_disk_path: "scripts/ops/shadow_canary_deploy.py + .github/workflows/deploy.yml"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: "MOD-MASTER_BLUEPRINT"
last_updated: "2026-08-03"
last_verified: "2026-08-03"
generation: 1
functional_domain: governance
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
codification_level: L1
summary: "CI/CD 灰度发布基建——Can-I-Deploy 预检+Shadow Canary 影子比对+灰度状态机编排，激活 GATE-CDC-1/CT-CDC-001/CT-CANARY-001 设计契约，满足 EX-021 门禁的 CI/CD 半"
tags: [cd_pipeline, shadow_canary, canary_release, can_i_deploy, cdc, gray_release, ci_cd, simulation_broker, ex021_gate, cluster_c]
priority: P1
runtime_plane: hot
depends_on:
  - {target: "MOD-GATE_ENGINE", at: "can_i_deploy.py", why: "GATE-CDC-1 四项预部署检查原语（consumer_expectations/schema_version/contract_consistency/health）"}
  - {target: "MOD-INF-018", at: "canary_rollout_manager.py", why: "灰度状态机 DRAFT→SAMPLING→ROLLOUT/ROLLED_BACK"}
  - {target: "MOD-CONTEXT_ENGINE", at: "shadow_canary.py", why: "影子生成+promote 语义复用（CT-CANARY-001 输出一致性比对）"}
  - {target: "MOD-L06-001", at: "simulation_broker.py", why: "影子进程走模拟券商不下真单（实盘安全硬底线）"}
  - {target: "MOD-INF-016", at: "process_pool.py", why: "子进程隐藏启动+管道管理（run_subprocess_hidden/spawn_python_hidden），影子进程 spawn 基建"}
  - {target: "MOD-EX-021", at: "deployment_consistency_manager.py", why: "本基建满足其门禁的 CI/CD 半（实盘环境半仍待 Owner 决策）"}
references:
  - {path: "d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md", section: "§16 CT-CDC-001", why: "GATE-CDC-1 Can-I-Deploy 预部署门禁 + CDC 设计契约真源"}
  - {path: "d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md", section: "§23.2 CT-CANARY-001", why: "金丝雀发布策略——阶段化部署 + 回滚触发条件真源"}
  - {path: "d:/ZephyrAlpha/.trae/documents/cicd-shadow-canary-infra-ex021.md", section: "全篇", why: "簇C CI/CD 灰度发布基建实施计划（本蓝图的设计依据）"}
ssot_claims:
  - {claim: "Shadow Canary 部署运行器编排逻辑SSoT", scope: "module"}
  - {claim: "CD 流水线 job 依赖图SSoT", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: generated
---

# CD Pipeline 蓝图 — Shadow Canary 灰度发布基建（MOD-CD-001）

## 概述
<!-- temporal_type: permanent -->

簇C CI/CD 灰度发布基建，把 4 个已有 stable 原语（`can_i_deploy` / `canary_rollout_manager` / `shadow_canary` / `simulation_broker`）编排成一条命令 + 一条 CD 流水线，激活 master blueprint §16 CT-CDC-001（GATE-CDC-1 Can-I-Deploy 预部署门禁）与 §23.2 CT-CANARY-001（金丝雀发布）两个长期 `DO_NOT_CALL`/`规划` 的设计契约。

**为什么做**：EX-021（`deployment_consistency_manager.py`）门禁 = 「实盘环境 + CI/CD 灰度发布基础设施」。CI 已成熟（governance.yml 7 层门禁 + 构建），但**完全没有 CD**——构建完就停。本蓝图补齐 CD 半，EX-021 实盘环境半仍待 Owner 决策。

**Shadow Canary 模式**：新版本并行跑、吸相同输入、**不下真单**（走 `simulation_broker`），比对输出一致性后再切——契合单机+实盘安全。shadow 必须在生产机（Windows 单机）本地跑（要比对真实生产输出），不能在 GitHub Actions 托管 runner 上跑。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CD-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CD-001` 的 8 个 file 节点 | production | `extract_depgraph.py --modules MOD-CD-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CD-001 | MOD-CD-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 8 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标

| 目标 | 度量 |
|---|---|
| 激活 GATE-CDC-1 预部署门禁 | CD 流水线 `can-i-deploy-gate` job 4 项检查全部生效 |
| 激活 CT-CANARY-001 金丝雀发布 | shadow 比对 + 分歧阈值 + 状态机流转 |
| 满足 EX-021 门禁 CI/CD 半 | EX-021 `gate_reason` 标注「CI/CD 灰度发布基础设施✅已就绪」 |
| 不下真单安全底线 | 影子进程强制 `--broker simulation`，走 `simulation_broker` |
| 阶段感知 | Windows 单机 CD 当前激活，容器化结构预留（post-activation #ARCH-065） |

## §2 模块边界

- **真源**：`scripts/ops/shadow_canary_deploy.py`（Shadow Canary 部署运行器，新能力模块）
- **配套**：`.github/workflows/deploy.yml`（CD 流水线，.yml 配置无需 depgraph 登记）
- **不做**：EX-021 本体实现（`deployment_consistency_manager.py`）——留待实盘环境就绪后
- **不做**：容器化部署激活——`ContainerDeployer` 为 stub，post-activation #ARCH-065

## §3 架构设计

```
CD 流水线 (.github/workflows/deploy.yml)
  │
  ├─ can-i-deploy-gate (windows-latest, GATE-CDC-1)
  │     ├─ consumer_expectations: pytest tests/contracts/
  │     ├─ schema_version: validate_static_manifest_drift.py --check
  │     ├─ contract_consistency: validate_ssot.py --ci
  │     └─ health: ch_health_probe --once / import zephyr
  │         (任一 FAIL → 阻断部署)
  │
  ├─ build-artifact (ubuntu-latest)
  │     └─ python -m build → upload wheel
  │
  ├─ shadow-canary (self-hosted: production-windows, if ENABLE_SHADOW_CANARY)
  │     └─ python scripts/ops/shadow_canary_deploy.py --duration 600
  │         │
  │         ├─ 预检 (CanIDeploy.check)
  │         ├─ 影子部署 (WindowsProcessDeployer, --broker simulation)
  │         ├─ 比对 (compare_decisions, 分歧率)
  │         ├─ 状态机 (CanaryRolloutManager: DRAFT→SAMPLING→ROLLOUT/ROLLED_BACK)
  │         └─ report.json + 退出码 (0=promote/1=rollback/2=预检失败)
  │
  ├─ promote (environment: production, 手动审批门)
  │     └─ shadow promote=true → release tag；(post-activation) 触发容器部署
  │
  └─ container-deploy (if: false, post-activation 占位)
```

## §9 依赖关系

| 依赖 | 路径 | 用途 |
|---|---|---|
| CanIDeploy | `src/zephyr/gov_enforcement/rule_enforcement/can_i_deploy.py` | 预检 4 项 pydantic 模型 |
| CanaryRolloutManager / CanaryState | `src/zephyr/security/access_control/canary_rollout_manager.py` | 灰度状态机 |
| ShadowCanary / CanaryResult | `src/zephyr/autonomy_core/context/shadow_canary.py` | 影子→promote 语义复用 |
| SimulationBroker | `src/zephyr/governance/adapters/simulation_broker.py` | shadow 不下真单（依赖可加载性预检） |
| run_subprocess_hidden / spawn_python_hidden | `src/zephyr/shared/infra/process_pool.py` | 无窗口 subprocess（预检 + 影子进程） |

## §13 已知风险与缓解

| 风险 | 缓解 |
|---|---|
| 影子进程误下真单 | INVARIANTS：影子命令须含 `simulation` token（缺失 warn）；预检验证 `simulation_broker` 可加载 |
| 生产决策日志缺失 | `load_decisions` 文件缺失→空列表；aligned=0 且有单侧差异→divergence=1.0 fail-safe rollback |
| shlex 切分吃 Windows 反斜杠 | 文档要求 `--shadow-cmd` 用正斜杠或双反斜杠（POSIX shlex 规则） |
| self-hosted runner 未配置 | `shadow-canary` job `if: vars.ENABLE_SHADOW_CANARY`；无 runner 时跳过，文档注明改在生产机手动执行 |
| 容器化未激活 | `ContainerDeployer` raise NotImplementedError；`container-deploy` job `if: false` |

## 必备链接

- 设计契约：[blueprint_baseline.md §16 CT-CDC-001](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md)、[§23.2 CT-CANARY-001](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md)
- 实施计划：[cicd-shadow-canary-infra-ex021.md](file:///d:/ZephyrAlpha/.trae/documents/cicd-shadow-canary-infra-ex021.md)
- 运行器实现：[shadow_canary_deploy.py](file:///d:/ZephyrAlpha/scripts/ops/shadow_canary_deploy.py)
- CD 流水线：[deploy.yml](file:///d:/ZephyrAlpha/.github/workflows/deploy.yml)

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ops/test_shadow_canary_deploy.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


---

## 治理信息

- **设计态登记**：depgraph 节点 MOD-CD-001（build_status=planned, domain=D_GOV_ENFORCEMENT, can_build=1）
- **依赖边**：5 条 import_depends 出边（can_i_deploy / simulation_broker / shadow_canary / canary_rollout_manager / process_pool）
- **门禁关联**：满足 MOD-EX-021 门禁的 CI/CD 半（实盘环境半待 Owner 决策）
- **post-activation**：容器化部署（#ARCH-065）激活 `ContainerDeployer` + `container-deploy` job
