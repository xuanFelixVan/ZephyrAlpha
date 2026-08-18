---
module_id: MOD-REGIME-006
title: "时间周期分析蓝图 — A股日历效应统计+周年日效应两件套（变盘时间窗口辅助参考信号）"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: design
build_status: generated
ttl: permanent
layer: L2_domain
layer_name: regime
functional_domain: regime
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-18"
last_updated: "2026-08-18"
priority: P2
blueprint_level: module
responsibility_domain: 
related_issues:
  - "#ARCH-122"
related_candidates:
  - CAND-CYCLE-001
related_registries:
  - REG-CYCLE-001
---

# MOD-REGIME-006 RegimeCycleAnalyzer — 时间周期分析 蓝图

> **module_id**: MOD-REGIME-006 | **域**: D_REGIME | **层**: L2 业务域
> **优先级**: P2 | **成熟度**: design | **建设标记**: 🟡 MVP 已施工待 WFA 验证
> **SSoT 注册表**: [regime_cycle_registry.yaml](../../../01_policies_and_standards/_registry/catalogs/regime_cycle_registry.yaml)（REG-CYCLE-001，12 条周期条目唯一真源）
> **候选立项**: candidate_module_registry.yaml CAND-CYCLE-001 | **架构议题**: #ARCH-122
> **日历纪律参照**: [17_special_trading_days_data_assets.md](../../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/17_special_trading_days_data_assets.md)

## 0. 本蓝图存在理由（第一性原理）

regime 层节流目前只看价格与波动状态（MOD-REGIME-001/002），无时间维度前瞻——
变盘窗口盲视。A 股存在可统计实证的日历结构（月末/节后效应）与行为金融锚定节点
（周年日效应），这些"何时可能变盘"的时间窗口是 regime 节流参数调整的正交增强维度。

本模块把"时间窗口识别"钉死成机器可读契约：**统计不显著=零置信=下游禁止消费**，
防止 Gann 类弱证据方法被滥用为交易信号。

## 1. 定位与边界声明（防滥用，硬性）

| 项 | 裁定 |
|---|---|
| 模块定位 | **辅助参考信号，非独立交易信号**——输出"何时可能变盘"的时间窗口 |
| 消费方 | 仅限 regime 层节流参数调整参考（变盘窗口前降仓/收紧）；**禁止直接触发开仓/买卖** |
| 方向语义 | risk_on/risk_off=日历效应统计方向；neutral=方向中性（周年日变盘=波动抬升）或不显著 |
| 置信纪律 | 统计不显著（p_adj>0.05 或 n<8）→ confidence=0.0 且 direction=neutral，下游禁止消费 |
| 挂接纪律 | 未通过严格 OOS/WFA 验证前**禁止挂接 regime 节流**（CAND-CYCLE-001 risks 裁定） |
| 正交边界 | regime=市场状态（多谨慎，MOD-REGIME-001）；emotion_cycle=sleeve 内择时（买卖什么）；本模块=时间窗口（何时可能变盘）。三者正交不重复 |
| is_advisory_only | 输出契约字段恒 True，代码层钉死 |

## 2. MVP 范围（两件套）

### ① 日历效应统计（对齐 CYC-STAT-013）

| 效应 | 事件定义 | 检验 |
|---|---|---|
| 月末效应 | 每月最后 2 个交易日 | Welch t：事件组日收益 vs 基准组 |
| 月初效应 | 每月前 2 个交易日 | 同上 |
| 节后效应 | 长假（相邻交易日历间隔 ≥5 自然日，春节/国庆）后首个交易日 | 同上 |

- 日历结构**纯日历派生**（自输入数据的交易日序列），不依赖 c1_market.calendar_event
  表（该表当前为空表缺口，见 17 号 memo §3.3）——零新增数据依赖（DS-002 日线已有）。
- 显著性自证：Welch t 检验 + Bonferroni 校正（检验族=4：3 日历假设+1 周年假设）。

### ② 周年日效应（对齐 CYC-TIME-004）

- 显著高低点识别：±20 交易日局部极值 + 波段幅度 ≥20% 过滤 + **右窗确认制**
  （极值确认需 lookback 日后数据，未确认不采信——PIT 无泄漏）。
- 周年窗口：每个显著高低点每年周年日 ±5 自然日（对齐注册表 params.tolerance=5），回溯 10 年。
- 显著性自证：周年窗口内 |日收益| vs 基准 |日收益|（变盘=波动聚集，方向中性），同款 t 检验+校正。

## 3. 输入 / 输出

### 3.1 输入

| 输入 | 类型 | 说明 |
|---|---|---|
| ohlc | DataFrame[close]，DatetimeIndex 或含 date 列 | 日线收盘价序列（≥60 交易日，不足抛 ZA-REGIME-0030） |
| as_of | str/Timestamp | 分析基准日（PIT 截断点，只用 ≤as_of 数据） |
| horizon_days | int=10 | upcoming 窗口前视自然日数 |

### 3.2 输出（CycleAnalysisResult）

| 字段 | 说明 |
|---|---|
| active_windows | as_of 落入的时间窗口（CycleWindow 元组） |
| upcoming_windows | horizon 内将开启的时间窗口 |
| evidence_table | {month_end, month_start, post_holiday, anniversary} → CycleEvidence |
| is_advisory_only | 恒 True（边界钉死） |

CycleWindow：cycle_id（库锚点 CYC-STAT-013/CYC-TIME-004）/ window_kind / start / end /
direction / confidence / evidence。
CycleEvidence：n_events / mean_event / mean_benchmark / t_stat / p_value / p_adj / significant / confidence。

## 4. 文件清单（file_manifest）

| 文件 | 角色 |
|---|---|
| src/zephyr/regime/regime_cycle_analyzer.py | 模块实现（纯函数层+编排器，零 CH 依赖） |
| tests/regime/test_regime_cycle_analyzer.py | 单测（24 用例，纯合成数据零外部依赖） |

## 5. 参数表（与代码常量一一对应，唯一真源）

| 参数 | 值 | 依据 |
|---|---|---|
| MIN_OBSERVATIONS | 60 | 统计有效性最低序列长 |
| MIN_EVENTS | 8 | 事件研究最少事件样本（周年日天然低频） |
| ALPHA_STRONG / MEDIUM / WEAK | 0.01 / 0.05 / 0.10 | confidence 三档映射（1.0/0.6/0.3），significant 线=0.05 |
| N_HYPOTHESES | 4 | Bonferroni 检验族：月末/月初/节后/周年日 |
| MONTH_EDGE_K | 2 | 对齐 CYC-STAT-013 "月末最后两个交易日" |
| POST_HOLIDAY_MIN_GAP_DAYS | 5 | 春节/国庆长假间隔下限（自然日） |
| ANNIVERSARY_TOLERANCE | 5 | 对齐 CYC-TIME-004 params.tolerance=5 |
| ANNIVERSARY_MAX_YEARS | 10 | 周年回溯上限 |
| SWING_LOOKBACK / SWING_MIN_MOVE_PCT | 20 / 0.20 | 显著高低点确认窗+幅度阈值 |
| DEFAULT_HORIZON_DAYS | 10 | upcoming 前视窗 |

## 6. PIT 纪律

- analyze(as_of=t) 输入截断 ≤t；日历前视（月末/周年窗口在未来日历上的位置）是
  **确定性信息**，非未来数据泄漏（与 17 号 memo 日历资产同理）。
- 周年显著性统计只用 ≤as_of 已发生的周年窗口；显著高低点识别右窗确认制
  （t 点极值需 t+20 数据确认，末端未确认极值不采信）。
- 测试桩：test_pit_no_future_leak（as_of=t 全量 vs 截断结果一致）。

## 7. 扩展口（登记不落码——证据强度不足不过度工程）

| 扩展口 | 对齐条目 | 不落码理由 | 启动条件 |
|---|---|---|---|
| EXT-G Gann 固定间隔 30/60/90 日 | CYC-TIME-001~003 | 学术证据弱（subjectivity=medium） | 两件套 WFA 达标+参数敏感性扫描后 |
| EXT-GEO Gann 角度线/九方图 | CYC-GEO-001/002 | subjectivity=high，证据最弱 | 同 EXT-G 且 MUST 参数敏感性扫描防过拟合 |
| EXT-FFT 统计周期（FFT/自相关/聚类/机制切换） | CYC-STAT-001~004 | 谱分析对非平稳金融序列稳健性待验 | 两件套上线运行 6 个月后 |
| EXT-PRICE 波段对称/50% 回调带 | CYC-PRICE-001/002 | 属价格维度非时间窗口 | 需求驱动 |

扩展接口预留：window_kind → cycle_id 映射表（`_CYCLE_ID_MAP`）+ CycleWindow 契约
对新 window_kind 零改动兼容；事件研究 `event_study()` 纯函数可直接复用。

## 8. 测试

tests/regime/test_regime_cycle_analyzer.py（24 用例）：
日历标记 5 / 事件研究+Bonferroni 5 / 高低点+周年窗口 4 / 编排器 10
（显著性自证、边界钉死、PIT、确定性、序列化、异常路径）。
纯合成数据零外部依赖（不连 ClickHouse）；显著性用例以人造效应自证，
**不断言 A 股真实效应存在**（那是 WFA 回测阶段的任务）。

## 9. 后续（非 MVP）

1. **真数据实证**：DS-002 日线全历史跑两件套，回填 regime_cycle_registry 条目
   evidence 字段 + algorithm_status。
2. **WFA 验证**：walk-forward 样本外验证达标后，才评估挂接 regime 节流（§1 挂接纪律）。
3. **接线**：RegimeFeatureBuilder/regime 节流参数调整消费本模块输出（届时登记
   [CONSUMERS] + contracts）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-REGIME-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-REGIME-006` 的 1 个 file 节点 | design | `extract_depgraph.py --modules MOD-REGIME-006` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-REGIME-006 | MOD-REGIME-006 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
