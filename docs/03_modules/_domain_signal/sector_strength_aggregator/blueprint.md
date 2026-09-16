---
module_id: MOD-SIG-142
title: "板块强度四路合分蓝图 — 等权先验+Top15%候选池"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: design
ttl: permanent
layer: L01_market
layer_name: market
functional_domain: signal_ashare
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-12"
last_updated: "2026-09-12"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-142 Sector Strength Aggregator — 板块强度四路合分 蓝图

> **module_id**: MOD-SIG-142 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L2-01；下游=L2-06 强度传导/L3 候选池（待接线）
> **出身**：晨审定性"聚合公式需权重裁定"；Owner 2026-09-12 授权架构师自行裁定令后落地。

## 1. 权重裁定（架构师分析过程，2026-09-12）

四路子分（结构强度/动量活跃/多周期动量/资金流）尚无独立 IC 证据链，此时任何非对称
权重都是无证据的先验注入。量化社区标准做法（Barra 风格因子初始等权、WorldQuant
Alpha101 未加权合成、QLib Alpha158 等权基线）：**无证据时等权是最大熵先验**。
据此裁定：w = 0.25×4 等权起步，weights 参数显式可注入；IC 数据积累后按
multifactor_synthesis（L3-07-2）的 IC 加权惯例重校。市场级调节（L2-01-5 产出）
为加法 delta ∈[-10,+10]，合成后 clamp [0,100]。

## 2. 候选池

composite 降序 Top-ceil(N×15%)（节点真源"总分进前 15%"），保底 1 个；
平分按板块名稳定序（确定性）。

## 3. 查重分工

四个子分产出件（L2-01-1~5）各自已锚定；本件为纯聚合核（零 IO、等权+clamp+Top 池），
不重复任何子件逻辑。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-142`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-142` 的 11 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-142` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-142 | MOD-SIG-142 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 11 文件 | N/A | — |

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
| `src/zephyr/signal_ashare/core/analysis_utils.py` | ✅ 已实现 | |
| `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py` | ✅ 已实现 | |

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


## 4. 研究依据（2026-09-12 全网调研，架构师复核）

- **等权 vs 优化的样本外证据**：DeMiguel/Garlappi/Uppal《Optimal Versus Naive Diversification》(RFS 2009，引用 5300+)——14 个优化模型在 7 个数据集上无一稳定跑赢 1/N 等权（误差估算是优化法的死穴）；Quantpedia 五种加权方案对比研究——忽略价格的方案样本外表现惊人地接近。**等权先验=学术最优稳健起点**。
- **IC/ICIR 加权**：样本内常胜但受估计误差污染；ICIR 优于裸 IC（稳定性加权）。North Trust"Factor Momentum within Factors"提出机器学习动态权重作为第三条路。
- **开源实践**：Microsoft Qlib（Alpha158/360 为中/美市场标准特征集，组合信号为一等公民），板块轮动在其管线之上自建（无内置）。

## 5. 升级路线（生产接线时实施）

1. **rank-based 跨截面归一**（Quantpedia rank 方案，抗离群）：生产接线时将四路子分先按当日全池跨截面排名归一到 0-100 再加权（mode 参数切换，默认 raw 保持已落库行为）。
2. **ICIR 加权重校**（≥60 交易日样本后）：对齐 multifactor_synthesis IC 加权惯例，按 ICIR 稳定性加权。
3. 触发条件：模块获得首个生产消费者（L2-06/L3 接线）时同步实施 1+2。
