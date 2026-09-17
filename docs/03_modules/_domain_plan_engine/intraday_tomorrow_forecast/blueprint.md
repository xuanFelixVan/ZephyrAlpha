---
module_id: MOD-PLAN-025
title: "明日情绪盘中滚动预测蓝图 — 三零件合成+悲观降档预警"
doc_type: blueprint
status: Active
version: "0.1.3"
design_maturity: production
ttl: permanent
layer: L07_plan
layer_name: plan
functional_domain: plan
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-11"
last_updated: "2026-09-11"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-PLAN-025 Intraday Tomorrow Forecast — 明日情绪盘中滚动预测 蓝图

> **module_id**: MOD-PLAN-025 | **域**: D_PLAN | **消费节点**: TDM-E-L0-04（组合器本体）；下游=L0-02 偏离监控（明日降档预警）/ L3-06 环境开关（情绪档输入，待接线）
> **出身**：施工清单 C13（晨审 st-tdm-review-20260911 D6 批准升施工批，R39 随批实测）；增长蓝图 G1 六向寻路四关已过（c8f678d8 落图）。

## 1. 组合语义（地图节点 algo_note 逐条对码）

盘中 10:00/11:00/13:30/14:30 四时点用最新盘面重算明天情绪概率：

1. **昨晚 8 态转移先验打底**——`next_day_8state_forecast.forecast_next_day`（MOD-SIG-037）产出 8 态概率分布，由调用方注入；
2. **相似日推理修正**——`similar_day_inference.infer_remaining_session`（MOD-SIG-063）产出今日尾盘三档情景（走强/持平/转弱），映射为悲观档位倾斜（转弱→明日档位调悲观）；
3. **Brier 校准连错降权**——`brier_calibration.compute_calibration`（MOD-PLAN-010）产出两源历史 Brier，Brier 越差权重越低（连错的输入自动降权）；
4. **合成**——先验分布+倾斜后分布按有效权重凸组合；融合期望悲观档比先验期望悲观档高 ≥1.0 档 → `downgrade_warning=True`（明日降档预警，喂 L0-02 偏离监控提前减仓）。

## 2. 关键口径（proposed，待实盘标定——对齐 ForecastConfig"阈值为初拟"先例）

- **悲观档位序**（8 态全序，越大越悲观）：GAP_UP_UP(0) < GAP_DOWN_UP(1) < FLAT_UP(2) < FLAT_CLOSE(3) < VIOLENT(4) < FLAT_DOWN(5) < GAP_UP_DOWN(6) < GAP_DOWN_DOWN(7)。高开低走（诱多套人）比平开低走更伤情绪，故排 6。
- **基础权重**：先验 0.7 / 相似日 0.3，各乘自身可靠度后归一。
- **可靠度**：`clamp(1 − brier/0.5, 0.1, 1)`（0.5=二值瞎猜参考）；无校准数据=1.0 中性（降权需证据，无罪推定）。
- **相似日倾斜**：tilt = (P弱 − P强) × 2.0 档；非 KNN 真路径（`enabled=False` 或 `fallback_used=True`）不参与合成——fallback 分支用的转移先验与第 1 步同源，参与即先验双计。
- **预警阈值**：融合**最可能态**悲观档 − 先验**最可能态**悲观档 ≥ 1（argmax 平票偏悲观）。不用期望档差作判据——凸组合下期望档最大移动 w×tilt≈0.6 档，"≥1 档"永不可达（2026-09-11 夜班自审修正，期望档差保留为诊断字段）。

## 3. 查重分工（三重反查留痕 2026-09-11）

CapabilityLookup forecast/next_day 零命中；Grep 无既有组合器；`tomorrow_boundary_planner` 不变量明文"不读盘中实时数据"（断链实证=本件存在理由）。三零件各自 IO 自持，本件纯函数核零 IO（对齐 thesis_survival "证据由调用方注入"模式）。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO；相似日非真路径不参与（防先验双计）；Brier 缺数据权重中性；融合分布恒归一非负；悲观档位表固定序；预警判据=融合期望档−先验期望档 ≥ 1.0；输入非法 fail-closed（TomorrowForecastInputError）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PLAN-025`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PLAN-025` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-PLAN-025` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PLAN-025 | MOD-PLAN-025 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
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
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


