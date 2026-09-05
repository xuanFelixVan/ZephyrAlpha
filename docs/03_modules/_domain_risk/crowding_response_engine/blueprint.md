---
module_id: MOD-RK-32
title: "C-045 拥挤度响应引擎蓝图 — 策略逻辑指纹相似度+超阈降杠杆/降仓+拥挤-回撤悖论防护 MVP"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
blueprint_id: MOD-RK-32
domain_id: D_RISK
path: src/zephyr/risk/core/crowding_response_engine.py
design_maturity: production
build_status: production
granularity: file
ai_autonomy: ai_modifiable
safety: H
stability: evolving
responsibility_domain: 
---

# MOD-RK-32 C-045 拥挤度响应引擎（Crowding Response Engine）蓝图

> **module_id**: MOD-RK-32 | **域**: D_RISK | **来源**: CAND-RSK-033（B1-00178，P0 波 W1c）

## 1. 定位

MOD-RK-13 CrowdingMonitor（跨参与者拥挤度**度量**）的深度增强**响应**层：

1. **策略逻辑指纹相似度**：策略 PnL 形态序列 z-归一化后两两 DTW（复用
   clone_guard.strategy_fingerprint.dtw_distance），`sim=1/(1+dtw)`；
   最大成对相似度超阈 → 判拥挤（与 crowding_score 超阈任一即拥挤）。
2. **拥挤超阈自动降杠杆/降仓**：leverage_scale / position_scale 收紧 +
   weight_penalty（漏斗第六层降权系数，纯数据供漏斗消费）。
3. **拥挤-回撤正反馈悖论防护**：拥挤 AND 回撤超阈 AND 回撤斜率恶化 →
   熔断式退出（forced_exit=True, position_scale=0）——打断"拥挤踩踏→回撤→
   更多抛售→更拥挤"正反馈回路。

**不复制裁定**：拥挤度度量本身在 MOD-RK-13（不重算），本引擎消费其
crowding_score 并补逻辑指纹维 + 响应动作；DTW 唯一真源 = clone_guard。

## 2. 输入 / 输出

| 方向 | 内容 | 契约 |
|------|------|------|
| 输入 | crowding_score（MOD-RK-13 产出）+ fingerprints {sid: pnl_series} + drawdown_pct/slope | — |
| 输出 | CrowdingResponseAction(is_crowded/logic_similarity_max/leverage_scale/position_scale/weight_penalty/paradox_guard_triggered/forced_exit/reasons) | frozen dataclass |

## 3. 核心规则

1. 拥挤判定：crowding_score ≥ crowded_threshold OR logic_similarity_max ≥ similarity_threshold。
2. 响应：拥挤 → leverage/position 缩放 + weight_penalty（默认均 0.5）。
3. 悖论防护：拥挤 AND drawdown_pct ≥ paradox_drawdown_threshold AND slope>0 →
   forced_exit + position_scale=0。
4. 指纹 <2 个 → logic_similarity_max=None（不参与拥挤判定）。
5. 纯函数无 IO；Fail-Closed 校验（InvalidCrowdingResponseConfigError /
   InvalidCrowdingResponseInputError）。

## 4. 依赖

| 依赖 | 模块 | 类型 |
|------|------|------|
| DTW 指纹 | clone_guard strategy_fingerprint | import_depends |
| 拥挤度契约 | MOD-RK-13 crowding_monitor | 设计契约（crowding_score 标量对齐，非 import） |
| 回撤状态 | MOD-RK-011 drawdown_tracker | 设计契约（drawdown_pct/slope 标量对齐，非 import） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-32`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-32` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-32` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-32 | MOD-RK-32 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


