---
blueprint_id: MOD-L02-LIFECYCLE
module_id: MOD-L02-LIFECYCLE
module_name: factor_lifecycle_runner
domain: D_FACTOR
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-09-15
last_updated: 2026-09-15
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-L02-LIFECYCLE factor_lifecycle_runner 蓝图

> 设计真源：生命周期协议 v2.0 三域落地（docs/_working/archive/2026-09/pattern_line/
> lifecycle-rollout-three-domains.md）。补齐 factor_decay_monitor_weekly 任务块的
> runner 缺口（该块 disabled 原因自述施工后启用）。

## 0. 定位
遍历 factor_registry→judge_factor 三级判定（域内预注册）∧BHY 族校正→
联合认证（certified/probation/failed）→连周计数→retired/复活（149 台账语义）
→decay_state 行级回写（零格式漂移）。单写手：retired/resurrected 覆盖当日三态。

## 1. 阈值（预注册：90 号 §2 + 本蓝图）
BHY q=0.10（任意依赖稳健）｜淘汰连 RETIRED_AFTER_WEEKLY=20 周扫→retired｜
复活=ic 回合格以上且族拒绝｜无 lookback 因子封顶 probation（Fail-Closed）。

## 2. 边界
不做 IC 回测管线（ic/lookback 由域内既有评估供给，缺口另批）；
不接油门（因子权重消费归因子域裁定）。

---

## 3. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 3.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/factor/analysis/factor_lifecycle_runner.py` | ✅ 已实现 | |

### 3.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/factor/test_factor_lifecycle_runner.py` | ✅ 已实现 | |

### 3.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §3（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
