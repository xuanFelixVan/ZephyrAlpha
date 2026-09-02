---
module_id: MOD-RK-39
title: "Manipulation Avoidance Detector 庄股操纵回避检测器蓝图 — 五类统计特征→操纵风险评分→回避名单"
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
priority: P1
blueprint_level: module
design_maturity: production
build_status: production
responsibility_domain: 
---

# MOD-RK-39 Manipulation Avoidance Detector — 庄股操纵回避检测器 蓝图

> **module_id**: MOD-RK-39 | **域**: D_RISK | **层**: L01 盘前/L02 实时监控
> **优先级**: P1 | **来源**: CAND-RSK-043（B13-04455，模块54，AUD-DRAFT-001 裁定=做，A4 §6.1）
> **SSoT**: depgraph MOD-RK-39

## 0. 查重裁定（RULE-EIGHT 探查结论）

候选 spec：庄股操纵**回避**检测——对倒放量/尾盘异动/价量背离/换手异常/筹码高度
集中五类统计特征 → 操纵风险评分 → 回避名单输出（风控禁开仓 + 信号域降权）；
仅用免费日线/分钟行情（GNN/联邦学习档放弃）；检测日志落盘可审计。

场内既有件逐一探查：

- MOD-CMP-007 trading_compliance_detector / MOD-CMP-011 intraday_manipulation_detector
  （compliance 族，production）：**自我操纵自证**——检测自身订单行为
  （Spoofing/Layering/WashTrade）以自证清白，TSV 已明示"方向相反"；
- MOD-SIG-088 capital_behavior_orchestrator（D_ASHARE_SIGNAL）：主力七类画像 +
  六阶段推演 + 合力方向（信号域资金行为分析）——非操纵评分/回避名单；
- audit 族（D_GOV_AUDIT writer）：审计落账执行面，非判定核心。

**裁定：无一覆盖"他人（庄股）操纵行为统计特征检测→回避名单"判定核心，
独立缺口成立，按补充层施工。**

## 1. 定位

庄股回避判定核心：五类行情统计特征（调用方注入预计算观测，免费日线/分钟可得）
→ 各映射 [0,1] 子分 → 加权合成操纵风险评分 → CLEAR/WATCH/AVOID 三级 →
回避名单（AVOID 集合）。纯函数无 IO；禁开仓/信号降权仅产信号（执行委托
MOD-RK-02 Pre-Trade / 信号域装配批）；检测日志经 audit_sink 委托 D_GOV_AUDIT 落账。

## 2. 输入 / 输出

- 输入（ManipulationFeatures，frozen；统计量由调用方注入）：
  volume_spike_ratio（当日量/N日均量，对倒放量代理）、tail_move_ratio
  （|尾盘30min收益|/全日振幅，尾盘异动）、price_volume_corr（近N日价量相关，背离）、
  turnover_spike_ratio（当日换手/N日换手中位数，换手异常）、chip_concentration
  （筹码集中度代理∈[0,1]，控盘特征）。
- 输出：ManipulationVerdict（symbol/score∈[0,1]/level/feature_scores/notes，frozen）；
  assess_batch → AvoidanceReport（verdicts + avoid_list + watch_list）。
- 审计：WATCH/AVOID 判定经 audit_sink 回调留痕。

## 3. 核心规则

1. 子分映射（线性截断，阈值 C 类可调）：
   wash=min(1, volume_spike_ratio/wash_ref=5)；tail=min(1, tail_move_ratio/tail_ref=0.5)；
   divergence=max(0, −price_volume_corr)；turnover=min(1, turnover_spike_ratio/
   turnover_ref=3)；chip=chip_concentration（已[0,1]）。
2. 总分 = Σw_i·s_i/Σw_i（默认五类等权）；level：score≥avoid_threshold(0.6)→AVOID；
   ≥watch_threshold(0.4)→WATCH；否则 CLEAR。
3. 回避名单：AVOID 才入 avoid_list；WATCH 入 watch_list；名单按 score 降序。
4. Fail-Closed：统计量负值/非有限、corr∉[−1,1]、chip∉[0,1]、权重/阈值配置非法、
   空 symbol → InvalidManipulationInputError。
5. verdict/report frozen 不可变。

## 4. 依赖前置

- 免费日线/分钟行情统计量（调用方注入，本模块不越域取数）
- 分工边：MOD-CMP-007（自我操纵自证，方向相反）/ MOD-SIG-088（主力画像）/
  D_GOV_AUDIT writer（日志落账）

## 5. 验收标准

- 单测全绿：五类子分映射与截断、加权总分、CLEAR/WATCH/AVOID 分级、回避名单
  降序、audit_sink 触发、非法输入 Fail-Closed；tests/risk 域零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-39`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-39` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-39` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-39 | MOD-RK-39 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


