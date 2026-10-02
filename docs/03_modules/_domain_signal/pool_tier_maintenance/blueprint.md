---
module_id: MOD-SIG-139
title: "股票池分层维护蓝图 — 三层就绪度池日更状态机"
doc_type: blueprint
status: Active
version: "0.1.4"
design_maturity: production
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-11"
last_updated: "2026-09-11"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-139 Pool Tier Maintenance — 股票池分层维护 蓝图

> **module_id**: MOD-SIG-139 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L3-09；下游=L3-08 候选池 Tier 标签/L3-02 主链 T1 直通（待接线）
> **出身**：晨审 st-tdm-review-20260911 §7.1 "确认查无，立缺口"（universe 域候选）；Owner 2026-09-11 夜班令"除币圈外开工"立项。

## 1. 状态机语义（节点 TDM-E-L3-09 algo_note 逐条对码）

持久池三层就绪度（与 L3-03 双池正交：双池按风格、Tier 按就绪度——D29 注释）：

- **Tier1 当日精选 / Tier2 观察池 / Tier3 备选池**；
- 日更规则（节点真源 2/5/10）：
  1. 连续 **2** 日进漏斗达标集 → 升一档（T1 封顶），升档后连击清零防连跳；
  2. 连续 **5** 日不达标 → 降一档（T3 再降=降无可降→**剔除**），降档后 miss 连击清零；
  3. **10** 日陈旧（持续无产出贡献）→ 剔除；
  4. 一次一事：降级触发日不做陈旧剔除（结果 notes 留痕）。
- 新标的经 `admit()` T3 起步；达标日 stale 清零（有贡献即保鲜）。

## 2. 边界与契约

- 纯函数状态机：entries 进、entries 出；**持久化由调用方落治理状态表/新 DS**
  （外审 M-41 欠账，待登记施工——本件不落库）；
- 同码重复条目/负计数/未知档位 → PoolTierInputError（fail-closed）；
- 输出按 (tier, code) 确定序；as_of 仅审计透传（无墙钟=无前视通道）。

## 3. 查重分工

晨审实证查无现成模块：market_cap_tier=流通市值 6 级分层（市值调子，90 号 §15），
universe_registry=池登记 SSoT（声明层）——均不承载就绪度升降级状态机。本件为运行层补位。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-139`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-139` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-139` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-139 | MOD-SIG-139 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/core/pool_tier_maintenance.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


