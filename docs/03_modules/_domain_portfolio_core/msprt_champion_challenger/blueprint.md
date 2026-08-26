---
module_id: MOD-PF-008
title: "mSPRT Champion-Challenger 序贯晋升组件蓝图 — 高斯 mixture 闭式解 + Ville 边界"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_portfolio_core
layer_name: portfolio_core
functional_domain: portfolio_core
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-24"
last_updated: "2026-08-24"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-PF-008 mSPRT Champion-Challenger — 序贯晋升组件 蓝图

> **module_id**: MOD-PF-008 | **域**: D_PF_CORE | **层**: L02 组合构建核心
> **优先级**: P1 | **成熟度**: design | **SSoT**: depgraph nodes（planned）
> **设计真源**: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md §3.3 纪律 1（mSPRT 施工伪代码）

## 1. 定位

Champion-Challenger 序贯晋升统计组件（BM-MT-02 通道的统计内核）——新模型不直接全量上线，
逐笔累加 challenger−champion 收益差的高斯 mixture 边际似然比（e-process），
达 Ville 边界即判定晋升/淘汰，证据不足默认保留 Champion。
anytime-valid：可任意频次查看无"偷看惩罚"（Type I ≤ α 在所有停时成立）。

属 A 类纯统计基础设施（无策略决策、无 MLflow 载体耦合——MLflow 已退役，alias 路由层另行裁定）。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 逐笔 delta 序列（challenger_pnl − champion_pnl，float） | 合成源（BM-REC-02-B 阻塞期） |
| 输入预留 | ChampionChallengerDeltaExtractor Protocol（ExecutionReport 对接位，不实现） | 未来 ExecutionReport 契约 |
| 输出 | 晋升 PROMOTE_CHALLENGER / 维持 RETAIN_CHAMPION / 淘汰 ELIMINATE_CHALLENGER + 似然比轨迹 | 内部 → 晋升编排层（未建） |

## 3. 核心规则

### 3.1 算法规格（61 号 memo §3.3 + 统计第一性原理裁定）

| 要素 | 规格 | 来源 |
|------|------|------|
| 假设 | H0: δ≤0（无改善） vs H1: δ>0（有改善） | memo + 任务裁定 |
| 混合先验 | H0 = 0 点质量；H1 混合 = N(0, τ²) | Johari et al. 2022 |
| 闭式边际似然比 | log M_n = ½·log(σ²/(σ²+nτ²)) + n²τ²x̄²/(2σ²(σ²+nτ²))，逐步累加 log（累乘等价） | 标准形裁定（memo 公式维度不一致，见 §3.2 裁定 1） |
| x̄ | 全历史 delta 均值 | memo |
| σ | 最近 30 笔滚动窗标准差（ddof=0），下限 1e-6 | memo |
| τ 标定 | std(历史 OOS 效应量)，≥5 点；冷启动 <5 点兜底 0.2；下限 max(τ, 0.1·median) | memo（mlflow 依赖剔除，改为注入） |
| 晋升边界 | M ≥ 1/α = 20（Ville 不等式，α=0.05）且 x̄>0 | memo + 裁定 3（单侧符号门控） |
| 淘汰边界 | (M ≥ 20 且 x̄<0) 或 (M ≤ α=0.05)，均须满窗 | 裁定 2/3 |
| 默认动作 | 证据不足 → RETAIN_CHAMPION（吸收 memo 的 CONTINUE） | memo 纪律 1 |
| 最小样本 | n < window_size（30）不做任何终局判定（σ 窗未满不可估） | 裁定 2 |

### 3.2 裁定留痕（memo 歧义 → 第一性原理裁定）

| # | memo 歧义 | 裁定 | 理由 |
|---|-----------|------|------|
| 1 | 伪代码 lr 公式 `sqrt(τ²/(τ²+nσ²))·exp(x̄²nτ²/(2σ²(nσ²+τ²)))` 维度不一致：n→∞ 时指数收敛常数、前置因子→0，M 永不越界 | 采用 Johari 2022 标准闭式 `sqrt(σ²/(σ²+nτ²))·exp(n²τ²x̄²/(2σ²(σ²+nτ²)))` | 标准形在 H1 下 log M ≈ nδ²/2σ² 线性增长、H0 下 -½log n 衰减，满足 e-process 性质 |
| 2 | `max_sample_size` 未定义（属性从未赋值）；n<30 时滚动 σ 未满窗，2-3 笔插值 σ 可使指数爆炸（实证：δ=+0.5σ 合成序列 n=2 即误晋升） | 终局判定（晋升/淘汰）最小样本 := window_size=30，窗满前一律 RETAIN | 对齐 memo §3.3 纪律 2"至少 30-50 笔影子交易才具备统计意义"（SR 26-02 金融业 4-12 周并行验证）；plug-in σ 满窗才可估 |
| 3 | 统计量含 x̄²（双侧）但假设为单侧 H0:δ≤0 vs H1:δ>0 | 决策层符号门控：晋升须 x̄>0；M≥20 且 x̄<0 → 淘汰（强有害证据） | 防止"显著为负"被双侧统计量误判为晋升；M≤α → 无效应证据淘汰 |

### 3.3 不变量

- threshold 恰为 1/α（α=0.05 → 20.0）；下边界恰为 α（0.05）
- log M 轨迹逐步累加：log_m_n = Σ Δlog M_i（闭式逐步重算，增量望远镜求和恒等）
- 滚动窗语义：n>30 后 σ 仅依赖最近 30 笔 delta
- 空序列/不足窗 → RETAIN_CHAMPION，M=1.0，轨迹为空

## 4. 接口契约

| 类/方法 | 签名 | 说明 |
|---------|------|------|
| `MSPRTChampionChallenger.__init__` | `(*, alpha=0.05, tau=None, historical_effects=None, window_size=30)` | tau 显式 > 由 historical_effects 标定 > 冷启动 0.2 |
| `MSPRTChampionChallenger.calibrate_tau` | `(historical_effects: Sequence[float]) -> float`（staticmethod） | memo 标定流程（≥5 点 std + 下限保护；<5 → 0.2） |
| `MSPRTChampionChallenger.update` | `(delta: float) -> MSPRTStepResult` | 逐笔更新，返回当步判定 |
| `MSPRTChampionChallenger.evaluate` | `(deltas: Iterable[float]) -> MSPRTStepResult` | 批量馈入，终局判定后早停（序贯语义） |
| `MSPRTStepResult` | frozen dataclass：n / delta / mean_delta / sigma / log_lr_increment / log_m / m / decision | 似然比轨迹步 |
| `ChampionChallengerDecision` | str Enum：PROMOTE_CHALLENGER / RETAIN_CHAMPION / ELIMINATE_CHALLENGER | is_terminal：晋升/淘汰为终局 |
| `ChampionChallengerDeltaExtractor` | Protocol：`extract_delta(champion_report, challenger_report) -> float` | ExecutionReport 对接位（BM-REC-02-B 阻塞，不实现） |

## 5. 测试策略

| # | 用例 | 通过标准 |
|---|------|---------|
| 1 | 阈值恰为 20 | threshold == 20.0（α=0.05） |
| 2 | δ=0 零效应长窗 | 300 笔合成序列不误晋升（终局非 PROMOTE） |
| 3 | δ>0 | 正确晋升，终局 M ≥ 20，早停 |
| 4 | δ<0 | 正确淘汰，轨迹全程无 PROMOTE |
| 5 | 30 笔滚动窗 | n=45 时 σ 仅由最近 30 笔决定 |
| 6 | 空序列/单笔 | RETAIN，n=0/1，M=1.0 |
| 7 | τ 标定 | <5 点 → 0.2；≥5 点 → std + 0.1·median 下限 |
| 8 | 轨迹 log 累加 | Σ increment == 终局 log_m；m == exp(log_m) |

> **测试路径**：`D:\ZephyrAlpha\tests\pf_core\test_msprt_champion_challenger.py`

## 6. 阻塞与遗留

| # | 项 | 状态 |
|---|----|------|
| 1 | ExecutionReport 契约（BM-REC-02-B）未建成 → delta 来源为合成/外部计算序列；DeltaExtractor Protocol 仅预留对接位 | 阻塞链登记于 architecture_issue_registry（fragment A8） |
| 2 | MLflow alias 路由层（@champion/@challenger/@archived）随 MLflow 退役需另行裁定载体 | 61 号 memo §0 已标注，非本组件范围 |
| 3 | 流量切分（95/5 blast-radius）与双指标纪律（业务+ML 指标、ECE 门控）属晋升编排层 | 61 号 memo §3.3 纪律 1 外围，非本统计组件范围 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-PF-008`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-PF-008` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-PF-008` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-PF-008 | MOD-PF-008 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 7. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pf_core/core/msprt_champion_challenger.py` | ✅ 已实现 | |

### 7.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/pf_core/test_msprt_champion_challenger.py` | ✅ 已实现 | |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
