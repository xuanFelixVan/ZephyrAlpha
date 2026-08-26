---
module_id: MOD-XS-008
submodule_path: src/zephyr/ex_sor/core/rl_exec_env.py
title: "RL 执行训练环境蓝图 — P-4 裁定组件骨架（环境+硬边界+契约，不真训）"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
build_status: stable
ttl: permanent
layer: L2_domain
layer_name: execution_routing
functional_domain: execution
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-24"
last_updated: "2026-08-24"
priority: P2
blueprint_level: module
responsibility_domain: 
---

# MOD-XS-008 RL Execution Training Env — RL 执行训练环境 蓝图

> **module_id**: MOD-XS-008 | **域**: D_EX_SOR | **层**: L2 执行路由
> **优先级**: P2 | **成熟度**: design（骨架） | **建设标记**: ②受限（GATE-XS08） | **设计标签**: XS-08
> **SSoT**: depgraph MOD-XS-008 | **设计真源**: docs/_working/依赖图/09-D-EX-SOR-执行路由域.md §2.1 XS-08
> **代码**: src/zephyr/ex_sor/core/rl_exec_{contract,boundary,env}.py | **测试**: tests/ex_sor/test_rl_exec_env.py

## 1. 定位

P-4 裁定组件（90 号文档待定问题 P-4「RL 执行是否实施」的工程留痕）：RL 执行层**骨架**——gym 风格训练环境 + 硬边界包裹层 + 执行参数契约三件套。**不真训**：真训练（PPO/TD3）属宪章 §4.2 **B-007** 人工审批闸门（禁止 AI 在无人工审批下上线新策略模块），本骨架仅提供环境/约束/契约，无任何学习逻辑。

大白话：将来若 Owner 批准用强化学习学"怎么拆单下单更省钱"，得先有一个安全的练兵场。本模块就是这个练兵场的骨架——环境管回合推进，硬边界管"无论如何不许违规"（价格不许出涨跌停带、单步量不许超 POV 上限、禁市价时市价动作直接拒），契约把约束参数冻结成一份文件，训练和生产共用。现在只搭架子不练兵。

## 2. 三件套与文件清单

| # | 组件 | 文件 | 职责 |
|---|------|------|------|
| ① | 训练环境 | `src/zephyr/ex_sor/core/rl_exec_env.py` | gym 风格自约定接口 `reset(seed)->state` / `step(action)->(state, reward, done, info)`；回合=单笔母单执行切片；状态=盘口/持仓(已成交)/剩余量快照；奖励=-实现短缺（成交滑价成本） |
| ② | 硬边界包裹层（核心） | `src/zephyr/ex_sor/core/rl_exec_boundary.py` | 限价（偏移换算后不得越涨跌停带，越界 clip 到带边界）、限量（单步 ≤ POV 上限×对方五档总量，整手对齐，尾单全清）、禁市价拒绝（本步不成交）；**独立于策略层，环境 step 必经，策略不可绕过** |
| ③ | 执行参数契约 | `src/zephyr/ex_sor/core/rl_exec_contract.py` | frozen dataclass：symbol/side/total_quantity/slice_count/pov_limit/forbid_market/offset_levels/prev_close/arrival_price/price_limit_pct/lot_size；真训练与生产执行共用同一约束口径 |

## 3. 动作与奖励口径（自约定）

- **动作** `RlExecAction`：`price_offset_idx`（档位索引→contract.offset_levels）+ `quantity_ratio`（对剩余量的比例）+ `is_market`（市价标志）。
- **限价换算**：基准=盘口中间价 mid=(ask1+bid1)/2，限价=mid×(1+offset)，量化到 0.01 tick。
- **涨跌停带**：[prev_close×(1−price_limit_pct), prev_close×(1+price_limit_pct)]（默认 ±10%，复用 MatchingConfig.price_limit_pct）。
- **奖励**：`reward = −is_step`；BUY `is_step=(成交价−arrival_price)×量`，SELL `(arrival_price−成交价)×量`；未成交/被拒步=0.0；`info["cum_is"]` 暴露回合累计 IS。

## 4. 复用件（禁止另立口径）

| 复用件 | 来源 | 用途 |
|--------|------|------|
| `MatchingConfig.price_limit_pct / lot_size` | zephyr.backtest.core.matching_logic（MOD-BT-001） | 涨跌停幅度 0.10 / 整手 100 默认值（#233 费率口径同一真源） |
| `MatchingLogic.match_limit_order / match_market_order` | 同上 | 切片撮合（回测=实盘一致性），含 1bps 滑点 |
| `OrderBookSnapshot` | 同上 | 五档盘口值对象（合成数据源注入形态） |
| `PRICE_TICK` | zephyr.ex_core.price_cage（MOD-L06-001） | 0.01 元最小价格变动单位 |
| `round_buy_qty` | zephyr.ex_core.board_lot（MOD-L06-001） | 买入整手板块差异化对齐 |

**取舍说明**：`check_price_cage`（±2% 申报价格笼子）属券商申报层合规约束，由生产执行路径（broker 适配层）承载；训练环境硬边界取更外层的涨跌停带（±10%），两者不重复嵌入。

## 5. 硬边界不变量

1. 裁剪后价格必在涨跌停带内（clip 不废单，对齐 price_cage 夹边语义）。
2. 单步数量 ≤ POV 上限×对方五档总量；≤ 剩余量；整手对齐（尾单豁免）。
3. forbid_market=True 时市价类动作必被拒绝（rejected=True，本步不成交）。
4. 环境 step 内部固定流水线 `boundary.enforce → matching`，策略侧无直挂撮合通道。
5. 数量守恒：filled + remaining = total_quantity，全程成立。
6. reset(seed) 确定性：同种子+同数据源 → 完全相同初始状态与轨迹。

## 6. B-007 闸门留痕

- 本骨架**不含训练逻辑**（无策略网络/无梯度更新/无经验回放）。
- 真训练管线（PPO/TD3 + L2 数据 + 仿真环境）= GATE-XS08（RL 训练基础设施+仿真环境+L2 数据）∩ 宪章 B-007（新策略模块上线须人工审批：回测通过→QMT 模拟盘→实盘小资金→实盘部署，每阶段人工审批）。
- 90 号文档 P-4 方向①为「放弃 41 号阶段 7 执行 RL（个人系统过度工程）」，仍待 Owner 裁定；本骨架仅作工程留痕，不预成立项。

## 7. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|------|------|------|------|
| 2026-08-24 | 0.1.0 | 初版骨架：契约+硬边界+环境三件套，15 单测全绿 | P-4 裁定组件施工（任务 P4_rlexec） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-XS-008`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-XS-008` 的 4 个 file 节点 | production | `extract_depgraph.py --modules MOD-XS-008` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-XS-008 | MOD-XS-008 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 4 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/ex_sor/core/rl_exec_boundary.py` | ✅ 已实现 | |
| `src/zephyr/ex_sor/core/rl_exec_contract.py` | ✅ 已实现 | |
| `src/zephyr/ex_sor/core/rl_exec_env.py` | ✅ 已实现 | |

### 8.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/ex_sor/test_rl_exec_env.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
