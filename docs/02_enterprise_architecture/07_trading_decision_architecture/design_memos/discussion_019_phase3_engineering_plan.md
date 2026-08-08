---
doc_id: discussion_019
title: "Phase 3 工程规划——降态数 + 两阶段校准 + NLP 管道 + S2/T3 数据激活"
doc_type: architecture_view
ttl: permanent
status: draft
version: "0.2.0"
date: "2026-08-07"
last_updated: "2026-08-08"
priority: P0
depends_on:
  - discussion_001_regime_detector_spec.md
  - discussion_002_regime_backtest_validation_plan.md
  - discussion_017_phase2_model_quality_validation.md
related_modules:
  - MOD-REGIME-001 (RegimeDetector)
  - MOD-REGIME-002 (RegimeFeatureBuilder)
  - MOD-REGIME-VAL-002 (Phase 2 验证器)
  - BM-BT-05 (HMM 模型质量验证)
---

# discussion_019 — Phase 3 工程规划

> **前置**：Phase 2 验证完成（commit 14c8b9f1），A1 PASS / B4 S1 3/3 / A2 FAIL / B1 FAIL。
> **本阶段**：修复 A2 过拟合 + B1 过度自信 + 激活 S2/T3 数据管道。
> **后续**：Phase 3 通过 → Phase 4 鲁棒性 → Phase 5 参数校准。

---

## 0. 背景：Phase 2 验证结果与核心问题

### 0.1 Phase 2 结果摘要

| 验证器 | 结果 | 关键指标 | 核心问题 |
|---|---|---|---|
| A1 样本充足性 | ✅ PASS | 3733 样本，9 态全 sufficient | 无 |
| B4 转换触发 | ⚠️ FAIL (3/6) | S1 3/3 ✅，S2 0/3 | S2 需 NLP + 资金/板块数据 |
| A2 过拟合 | ❌ FAIL | OOS/IS=0.340, KL=16.95 | 9 态过多，模型时间不稳定 |
| B1 概率校准 | ❌ FAIL | 误差 27.6%，80-100%桶误差 45.9% | confidence 严重过度自信 |

> **2026-08-08 更新**：P0-E1 降态（9→4）+ P0-E2 两阶段校准器 + B4 修复后，Phase 2 全 PASS：
>
> | 验证器 | 结果 | 关键指标 |
> |---|---|---|
> | A1 样本充足性 | ✅ PASS | 3733 样本，4 态最少 555 天（r3） |
> | B4 转换触发 | ✅ PASS (3/3) | S1 3/3 命中；S2 [待数据]（data_ready=False，需 NLP+high/low，不计分母） |
> | A2 过拟合 | ✅ PASS | OOS/IS=1.042，KL=13.05（9 态时仅 0.340） |
> | B1 概率校准 | ✅ PASS | ECE=4.2%（60-80%桶 n=221 误差 3.7%） |
>
> 上表为初始 9 态验证历史（P0 修复前）；P0 完成后 Phase 2 闭环（commit 0c5ea28bb1/83c94c4f/e4fd931a），进入 P1 数据管道激活阶段。
>
> **2026-08-08 续（S2 算法缺陷诊断）**：另一 session 将 S2 `data_ready` 误改 true 后 B4 退回 FAIL(3/6)。诊断脚本 `dump_s2_scores.py` 证实根因是 **S2 评分算法时点错配**（capitulation 当日值 vs 过程、valuation 价格回撤 vs 基本面），非数据缺失——三事件 capitulation/valuation 恒 0 致 trigger/confirm 永不触发。采用 `design_match=false` 排除 S2 事件（数据已就绪但 Wyckoff 吸筹模板不匹配 A 股 V/政策型复苏）+ 修复 capitulation/valuation 两个 P0 bug（commit 93a25890，B4 维持 PASS(3/3)），登记 #ARCH-REGIME-S2-ALGORITHM-001，新增 P1-E9 工程项（§3.5）治本。完整诊断与裁定见 [discussion_023](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_023_s2_algorithm_misalignment_diagnosis.md)。

### 0.2 问题诊断

**A2 FAIL 根因**：9 态过度细分导致模型在 IS（2010-2018）和 OOS（2019-2026）学到的状态结构差异巨大。不是数据量不够（A1 显示每态 267-513 天），而是状态数太多让模型把噪声当规律。

**B1 FAIL 根因**：`confidence = max(P)` 直接用 HMM 最大概率值，无校准。80-100% 桶 1406 个样本（占 78%）预测 0.982 但实际 0.523——模型在高置信度区间严重过度自信。

**B4 S2 FAIL 根因**：S2（复苏确认）触发需 `bad_news_flat ≥ 40`，该指标依赖新闻 NLP 分析，当前是 stub（恒返回 0）。T3 资金主线维度也全走 0.0 降级。

### 0.3 第一性原理：不将就，选最优

**核心原则**：方案选择不从"我们现有什么"出发，而从"什么是好的"出发。如果最优方案需要我们没有的东西（如 logits），就改造系统去提供它。

**校准方案的第一性原理推演**（详见 §2.2）：
1. 定义"好的校准"的 5 个性质：准确性、锐度、保序性、样本效率、理论保证
2. 从 5 性质出发评估 Temperature/Platt/Isotonic/SMART
3. 推出两阶段组合方案（Temperature Stage 1 + Isotonic Stage 2）
4. 预留可升级架构（未来 SMART/ATS-CP）

---

## 1. 工程总览

### 1.1 工程清单与优先级矩阵

| 编号 | 工程名称 | 优先级 | 依赖 | 工程量(行) | 解决问题 |
|---|---|---|---|---|---|
| P0-E1 | HMM 降态数 9→3-4 | P0 | 无 | ~50 | A2 FAIL 根因 |
| P0-E2 | 两阶段概率校准器 | P0 | P0-E1（需重跑验证） | ~390 | B1 FAIL 根因 |
| P1-E3 | NLP 情感分析管道 | P1 | 无（可并行） | ~800 | S2 bad_news_flat 依赖 |
| P1-E4 | 资金/板块数据激活 | P1 | 无 | ~100 | T3 依赖 |
| P1-E5 | T3 激活与注释清理 | P1 | P1-E4 | ~50 | T3 代码已实现，清理注释+融合北向资金 |
| P1-E6 | bad_news_flat 指标 | P1 | P1-E3 | ~150 | S2 触发条件 |
| P1-E9 | S2 评分算法重设计 | P1 | 无（算法层，独立于数据激活） | ~120 | S2 时点错配根因（见 discussion_023） |
| P2-E7 | policy 指标 | P2 | P1-E3 | ~150 | S2 触发条件 |
| P2-E8 | forward_days 参数扫描 | P2 | P0-E2 | ~50 | B1 参数调优 |
| **合计** | | | | **~1860** | |

### 1.2 依赖关系图

```
P0-E1 降态数 ──→ 重跑 A1/A2/B1/B4 验证
                    ↑
P0-E2 校准器 ───────┘（校准器需在降态后重验）

P1-E3 NLP 管道 ──→ P1-E6 bad_news_flat ──→ S2 触发
P1-E4 数据激活 ──→ P1-E5 T3 实现 ──→ T3 触发

P2-E7 policy ──── 依赖 P1-E3 NLP 管道
P2-E8 forward_days ── 依赖 P0-E2 校准器
```

### 1.3 推荐执行顺序

```
第一批（P0）：P0-E1 → P0-E2 → 重跑 Phase 2 验证
第二批（P1a）：P1-E4 → P1-E5（数据激活 + T3，不依赖 NLP）
第二批（P1b）：P1-E3 → P1-E6（NLP 管道 + bad_news_flat，可与 P1a 并行）
第三批（P2）：P2-E7 → P2-E8
```

## 1.5 P0 阻断项文件修改清单（施工前必读）

4 个阻断项涉及以下文件修改。按优先级排序——**必须从上到下逐项完成**。

### 文件修改总览

| 优先级 | 阻断项 | 文件 | 修改类型 | 载重代码处数 |
|---|---|---|---|---|
| **1** | #3 降态后配置失效 | `src/zephyr/regime/core/regime_detector.py` | 重设计 `_STATE_RISK_FACTORS` + `TRANSITION_CONFIG` | 2 块配置 |
| **2** | #4 硬编码 9 | `src/zephyr/regime/core/regime_detector.py` | 同步改所有硬编码 9 | 13 处载重 |
| **3** | #4 硬编码 9 | `src/zephyr/regime/validation/phase2/a1_sample_sufficiency.py` | 同步改 `HMM_STATES_9` 等 | 7 处载重 |
| **4** | #4 硬编码 9 | `src/zephyr/regime/validation/phase2/a2_hmm_overfitting.py` | 改默认 `n_states` | 1 处载重 |
| **5** | #4 硬编码 9 | `tests/regime/test_regime_detector.py` | 改断言中的 `1.0/9.0` | 6 处载重 |
| **6** | #4 硬编码 9 | `tests/regime/phase2/test_a1_sample_sufficiency.py` | 改 mock 参数和断言 | 7 处载重 |
| **7** | #1 hmmlearn API | `src/zephyr/regime/core/regime_detector.py` | 新增 `predict_log_proba` 方法 | +1 方法 |
| **8** | #2 校准器降级 | 新建 `src/zephyr/regime/validation/phase2/confidence_calibrator.py` | 新建校准器模块 | 新文件 |
| **9** | #2 校准器降级 | `src/zephyr/regime/validation/phase2/phase2_runner.py` | walk-forward 集成降级策略 | 改 run() |
| **10** | #2 校准器降级 | 新建 `tests/regime/phase2/test_confidence_calibrator.py` | 单元测试 | 新文件 |
| **11** | #3 BIC 扫描 | 新建 `scripts/tests/scan_hmm_states.py` | BIC 扫描脚本 | 新文件 |
| **12** | 注释同步 | `scripts/tests/dump_c1_repro_artifacts.py` | markdown 产物中引用 9 | 2 处注释 |

### 详细修改路径（按文件分组）

#### 文件 A：`src/zephyr/regime/core/regime_detector.py`（最核心，涉及 3 个阻断项）

**阻断项 #3（降态后配置失效）**：

| 行号 | 当前代码 | 修改为 |
|---|---|---|
| 91-103 | `_STATE_RISK_FACTORS` dict（r1-r9 基于 3×3 网格） | 重设计为新态数的 shrinkage 映射（§2.1.6.2 施工方法） |
| 128-138 | `TRANSITION_CONFIG` 的 T1/T4/T5/T6（依赖网格态转移） | 重设计转换逻辑（§2.1.6.3 施工方法） |

**阻断项 #4（硬编码 9，13 处载重代码）**：

| 行号 | 当前代码 | 修改为 |
|---|---|---|
| 60 | `HMM_STATES = [f"r{i}" for i in range(1, 10)]` | `range(1, n_states+1)` |
| 303 | `{"n_states": 9, ...}` | `{"n_states": 新态数, ...}` |
| 307-311 | 默认 `state_frequencies`（含 r9） | 适配新态数 |
| 385 | `hmm_params.get("n_states", 9)` | `get("n_states", 新态数)` |
| 467 | `1.0 / 9.0` | `1.0 / n_states` |
| 472 | `1.0 / 9.0` | `1.0 / n_states` |
| 482 | `if len(last) != 9:` | `if len(last) != n_states:` |
| 484 | `1.0 / 9.0` | `1.0 / n_states` |
| 485 | `range(9)` | `range(n_states)` |
| 488 | `1.0 / 9.0` | `1.0 / n_states` |

**阻断项 #1（hmmlearn API，新增方法）**：

| 行号 | 修改 |
|---|---|
| 新增 | `def predict_log_proba(self, X): return np.log(self._hmm_model.predict_proba(X) + 1e-30)` |

#### 文件 B：`src/zephyr/regime/validation/phase2/a1_sample_sufficiency.py`（#4，7 处载重）

| 行号 | 当前代码 | 修改为 |
|---|---|---|
| 64 | `HMM_STATES_9 = [f"r{i}" for i in range(1, 10)]` | `HMM_STATES_N = [f"r{i}" for i in range(1, n_states+1)]` |
| 170 | `"n_states": 9` | `"n_states": 新态数` |
| 291 | `get("n_states", 9)` | `get("n_states", 新态数)` |
| 305 | `HMM_STATES_9[i]` | `HMM_STATES_N[i]` |
| 348 | `total // 9` | `total // n_states` |
| 351 | `HMM_STATES_9[i]` | `HMM_STATES_N[i]` |
| 359 | `range(9)` | `range(n_states)` |

#### 文件 C：`src/zephyr/regime/validation/phase2/a2_hmm_overfitting.py`（#4，1 处载重）

| 行号 | 当前代码 | 修改为 |
|---|---|---|
| 123 | `"n_states": 9` | `"n_states": 新态数` |

#### 文件 D：`tests/regime/test_regime_detector.py`（#4，6 处载重）

| 行号 | 当前代码 | 修改为 |
|---|---|---|
| 173 | `1.0 / 9.0` 断言 | `1.0 / n_states` |
| 185 | `1.0 / 9.0` 断言 | `1.0 / n_states` |
| 232 | `{s: 1.0 / 9.0 for s in HMM_STATES}` | `1.0 / n_states` |
| 235 | `1.0 / 9.0` 断言 | `1.0 / n_states` |
| 241 | `{s: 1.0 / 9.0 for s in HMM_STATES}` | `1.0 / n_states` |
| 251 | `{s: 1.0 / 9.0 for s in HMM_STATES}` | `1.0 / n_states` |

#### 文件 E：`tests/regime/phase2/test_a1_sample_sufficiency.py`（#4，7 处载重）

| 行号 | 当前代码 | 修改为 |
|---|---|---|
| 18 | `n_states: int = 9` mock 默认 | `n_states: int = 新态数` |
| 43 | `np.arange(9)` | `np.arange(n_states)` |
| 51 | `len(...) == 9` 断言 | `== n_states` |
| 70 | `["r9"]` 断言 | 适配新态标签 |
| 86 | `["r9"]` 断言 | 适配新态标签 |
| 109 | `np.arange(9)` | `np.arange(n_states)` |
| 138 | `np.arange(9)` | `np.arange(n_states)` |

#### 新建文件清单

| 文件 | 阻断项 | 内容 |
|---|---|---|
| `scripts/tests/scan_hmm_states.py` | #3 | BIC 扫描脚本（2-9 态） |
| `src/zephyr/regime/validation/phase2/confidence_calibrator.py` | #2 | 两阶段校准器 + 降级策略 |
| `tests/regime/phase2/test_confidence_calibrator.py` | #2 | 校准器单元测试 |

### 施工顺序（关键路径）

```
步骤 1: 跑 BIC 扫描（新建 scan_hmm_states.py）
    ↓ 确定新态数（预期 3-4）
步骤 2: 重设计 _STATE_RISK_FACTORS + TRANSITION_CONFIG（regime_detector.py）
    ↓ 新配置生效
步骤 3: 同步改所有硬编码 9（文件 A-E，~30 处）
    ↓ 编译通过
步骤 4: 新增 predict_log_proba 方法（regime_detector.py）
    ↓ API 就绪
步骤 5: 新建 confidence_calibrator.py（校准器 + 降级策略）
    ↓ 校准器就绪
步骤 6: phase2_runner.py 集成校准器
    ↓ walk-forward 闭环
步骤 7: 新建 test_confidence_calibrator.py
    ↓ 测试通过
步骤 8: 重跑 A1+A2+B1+B4 验证
    ↓ 确认 A2 OOS/IS ≥ 0.7
```

> ⚠️ **步骤 1-3 是前置依赖**——必须先确定新态数，才能改硬编码和重设计配置。步骤 4-7 可以在步骤 3 完成后并行。

---

## 2. P0 工程详设

### 2.1 P0-E1: HMM 降态数 9→3-4

#### 2.1.1 目标

将 HMM 状态数从 9 降到 3-4，消除过度细分导致的过拟合，使 A2 OOS/IS 比值从 0.34 提升到 ≥0.7。

#### 2.1.2 机构实践调研（2026-08-07 全网搜索）

| 来源 | 状态数 | 理由 |
|---|---|---|
| Hamilton 1989（鼻祖论文） | 2 | 牛市/熊市 |
| 量化社区默认（stratcraft.ai） | 3 | "captures the most common market dynamics without overcomplicating" |
| BIC elbow method（GitHub ron-shen） | 3 | k=2→3 BIC 提升 22k，k=3→4 只提升 11k，3 是拐点 |
| Adaptive Hierarchical HMM（MDPI 2025） | 3 | 牛/熊/动荡 |
| 4 态方案 | 4 | 区分"低波动趋势"和"高波动趋势" |

**结论**：没有任何机构/论文用 9 态。3 态是 BIC 拐点，4 态适合需区分波动 regime 的场景。

#### 2.1.3 为什么不是数据量不够

A1 验证显示每态 267-513 天，样本充足。问题是 9 态让模型过度细分噪声——2010-2018 学的"第 7 态"和 2019-2026 的"第 7 态"完全不同。

#### 2.1.4 为什么不加港股/美股/韩股数据

| 市场 | 交易机制 | 涨跌停 | 参与者 | 与 A 股兼容性 |
|---|---|---|---|---|
| A 股 | T+1 | 有（±10%） | 散户为主 | — |
| 港股 | T+0 | 无 | 机构为主 | ❌ 机制不同 |
| 美股 | T+0 | 无 | 机构为主 | ❌ 机制不同 |

混合不同机制市场的数据会让 HMM 学到"假规律"——两个市场统计特征相似但驱动因素完全不同。学术界做 cross-asset regime 也是每个市场单独建模。

#### 2.1.5 算法方案

**不拍脑袋选 3 还是 4，用 BIC elbow method 数据驱动选择**：

```python
# BIC = -2 * log_likelihood + k * ln(n)
# k = n_states * (n_states - 1) + n_states * n_features + n_states * n_features * (n_features + 1) / 2
# 选 BIC 下降变缓的拐点

for n_states in [2, 3, 4, 5, 6, 7, 9]:
    detector = RegimeDetector(hmm_params={"n_states": n_states, ...})
    detector.fit({"X": X_full, "lengths": None})
    bic = -2 * detector._hmm_model.score(X_full) + k * np.log(len(X_full))
    # 记录 BIC，选拐点
```

#### 2.1.6 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | 写 BIC 扫描脚本 | `scripts/tests/scan_hmm_states.py` |
| 2 | 跑 BIC 扫描（2-9 态） | BIC 曲线图 + 拐点判定 |
| 3 | 改 `regime_detector.py` 默认 `hmm_params["n_states"]` | 从 9 → BIC 拐点（预期 3-4） |
| 4 | 同步改所有硬编码 9 的位置（清单见 §2.1.6.1） | 适配新态数 |
| 5 | **重设计 `_STATE_RISK_FACTORS`**（§2.1.6.2） | 降态后 shrinkage 映射 |
| 6 | **重设计 `TRANSITION_CONFIG`**（§2.1.6.3） | 降态后转换逻辑 |
| 7 | walk-forward 各季度窗口跑 BIC 验证 | 确认拐点跨期一致 |
| 8 | 重跑 A1+A2+B1+B4 验证 | 确认 A2 OOS/IS ≥ 0.7 |

#### 2.1.6.1 硬编码 9 完整清单（步骤 4 必须逐项更新）

以下位置**全部**硬编码了 9，降态后必须同步修改，否则测试失败或默认值覆盖新 n_states：

**`regime_detector.py`**：
| 行号 | 当前代码 | 改为 |
|---|---|---|
| ~60 | `HMM_STATES = ["r1", ..., "r9"]` | `["r1", ..., "r{新态数}"]` |
| ~303 | 默认 `{"n_states": 9}` | `{"n_states": 新态数}` |
| ~467/472/484/488 | `1.0 / 9.0`（均匀分布 fallback） | `1.0 / 新态数` |
| ~485 | `range(9)` | `range(新态数)` |
| ~68-74 | ConfidenceSignal 阈值（注释"9 态下 0.5 已是高置信"） | 重新标定阈值 |

**`a1_sample_sufficiency.py`**：
| 行号 | 当前代码 | 改为 |
|---|---|---|
| ~64 | `HMM_STATES_9 = [f"r{i}" for i in range(1, 10)]` | `HMM_STATES_N = [f"r{i}" for i in range(1, 新态数+1)]` |
| ~355 | 降级摘要 `"1/9 均匀分布"` | `"1/{新态数} 均匀分布"` |
| ~359 | `range(9)` | `range(新态数)` |

**`phase2_runner.py`**：
| 位置 | 当前代码 | 改为 |
|---|---|---|
| hmm_params 默认 | `n_states: 9` | `n_states: 新态数` |

**`tests/regime/test_regime_detector.py`**：
| 行号 | 当前代码 | 改为 |
|---|---|---|
| ~170/173/185/231/232/235/241/251 | `1.0 / 9.0`（8 处） | `1.0 / 新态数` |

> ⚠️ **检查方法**：施工时跑 `grep -rn "1\.0 / 9\|1/9\|range(9)\|n_states.*9" src/zephyr/regime/ tests/regime/` 确认无遗漏。

#### 2.1.6.2 重设计 `_STATE_RISK_FACTORS`（步骤 5）

**问题**：当前 `_STATE_RISK_FACTORS` 基于 3×3 网格语义（r1=Bull-Low→shrinkage=1.0，r9=Bear-High→0.30）。降到 3-4 态后**网格语义不存在**，shrinkage 映射失效。

**施工方法**：
1. 先跑 BIC 确定 n_states（预期 3-4）
2. 用 Viterbi 解码全历史，观察每个新态的**统计特征**（平均收益率、平均波动率、平均换手率）
3. 根据统计特征映射到语义标签（如 3 态可能是：牛/震荡/熊；4 态可能是：低波趋势/高波趋势/震荡/危机）
4. 按语义标签分配 shrinkage 值（牛市→1.0 不收缩，危机→0.30 大幅收缩）
5. 更新 `_STATE_RISK_FACTORS` 字典

```python
# 示例：3 态方案（施工时根据 BIC 结果和统计特征确定）
_STATE_RISK_FACTORS = {
    "r1": 1.0,   # 牛市：不收缩
    "r2": 0.85,  # 震荡：轻微收缩
    "r3": 0.50,  # 熊市：大幅收缩
}
# overlay 态 r10-r12 保持不变（独立于 HMM 基态）
```

> ⚠️ 此步骤**不能拍脑袋**——必须先跑 BIC + Viterbi 解码 + 统计特征分析，才能确定态语义和 shrinkage 值。这是 P0-E1 的**第一个施工动作**。

#### 2.1.6.3 重设计 `TRANSITION_CONFIG`（步骤 6）

**问题**：T1/T4/T5/T6 的转换定义依赖特定网格态间转移（如 T4="Bull-Medium→Bull-High"），降态后这些转换无意义。

**施工方法**：
1. 先完成步骤 5（确定新态语义）
2. 重新定义 8 个转换类型在新态语义下的含义：
   - S1（CRISIS）：哪些态组合触发危机信号
   - S2（RECOVERY）：哪些态组合触发复苏信号
   - T1（BREAKOUT）：哪个态→哪个态是突破
   - T3（RECOVERY→BREAKOUT）：哪些维度确认主升
   - T4/T5/T6：根据新态语义重新定义
3. 更新 `TRANSITION_CONFIG` 的 `overlay_target`、`keys_gte`、`p_overlay`

```python
# 示例：3 态方案下的 TRANSITION_CONFIG（施工时根据语义确定）
TRANSITION_CONFIG = {
    "S1": {  # 危机检测：r3(熊) + vix_panic
        "stages": {
            "trigger": {"keys_gte": {"vix_panic": 60, "correlation": 60}, ...},
        },
    },
    "T1": {  # 突破：r2(震荡) → r1(牛)
        "overlay_target": "r10",  # overlay 态编号不变
        "stages": {
            "trigger": {"keys_gte": {"volume_price": 60, "ma_trend": 50}, ...},
        },
    },
    # ... 其他转换
}
```

> ⚠️ overlay 态 r10-r12 编号**不需要重编号**——它们独立于 HMM 基态。但 overlay 默认概率（r10/r11/r12 合计 0.05）在 3-4 基态下每态均分比例变化，建议复核。

#### 2.1.6.4 label-switching 对齐（walk-forward 跨季度一致性）

**问题**：无监督 HMM 的标签有 permutation invariance——r1 在 2024Q3 可能代表"牛市"，但 2024Q4 refit 后 r1 可能变成"熊市"。如果不做对齐，walk-forward 各季度的状态语义不一致，校准器的 occurred 标签和校准参数无意义。

**对齐协议（基于态均值特征排序）**：

```python
def align_labels(detector_prev: RegimeDetector, detector_curr: RegimeDetector) -> dict[int, int]:
    """对齐两个季度 HMM 的标签——按态均值特征排序。

    Returns:
        mapping: {curr_state_idx → prev_state_idx}
    """
    # 取两个 HMM 的态均值向量（n_states × n_features）
    means_prev = detector_prev._hmm_model.means_  # (n_prev, n_features)
    means_curr = detector_curr._hmm_model.means_  # (n_curr, n_features)

    # 按第一特征（如 vol_pct）排序，建立对齐
    order_prev = np.argsort(means_prev[:, 0])  # 按 vol_pct 排序
    order_curr = np.argsort(means_curr[:, 0])

    # curr 的第 i 个态 → prev 中排序位置相同的态
    mapping = {}
    for i in range(len(order_curr)):
        rank = np.searchsorted(means_prev[order_prev, 0], means_curr[order_curr[i], 0])
        rank = min(rank, len(order_prev) - 1)
        mapping[int(order_curr[i])] = int(order_prev[rank])
    return mapping
```

**walk-forward 集成**：
```python
detector_prev = None
for i, q in enumerate(quarter_ends):
    detector.fit(X_train)

    if detector_prev is not None:
        # 对齐本季度标签到上季度
        mapping = align_labels(detector_prev, detector)
        # 用 mapping 重映射 predict_proba 的输出列
        # 使 r1 在所有季度始终代表"最低波动态"

    detector_prev = detector
```

**限制**：
- 基于单特征排序的对齐在态均值接近时可能出错
- 如果态数变化（如 3→4），对齐更复杂
- 此协议是**近似**方案，不是完美解决——A2 验证器（OOS/IS 一致率）会检测对齐质量

> ⚠️ 此步骤与 A2 验证器的 `_align_labels` 逻辑一致（`a2_hmm_overfitting.py`），施工时复用 A2 的对齐代码。

#### 2.1.7 验收标准

- [ ] BIC 曲线显示 3-4 为拐点
- [ ] A2 OOS/IS ≥ 0.7（从 0.34 提升）
- [ ] A1 仍 PASS（每态 ≥ 100 天）
- [ ] B4 S1 仍 3/3 命中

---

### 2.2 P0-E2: 两阶段概率校准器

#### 2.2.1 目标

将 HMM 的 `confidence` 校准到"说 80% 真有 80%"，校准误差从 27.6% 降到 <10%。

#### 2.2.2 第一性原理：什么是好的校准

定义"好的校准"的 5 个性质：

| 性质 | 含义 | 为什么重要 |
|---|---|---|
| **准确性** | 预测概率 = 实际频率 | 核心目标 |
| **锐度** | 预测分布要"尖"，不总是 50% | 只有准确没有锐度=没用 |
| **保序性** | 校准后排序不变 | 不改变"哪个更可能"的判断 |
| **样本效率** | 数据少时也稳定（walk-forward 每季 ~60 天） | 稀有态 267 天分桶后每桶 ~27 个 |
| **理论保证** | 有数学证明的收敛性/Brier 最优性 | 不是经验调参 |

#### 2.2.3 从第一性原理评估各方法

**Temperature Scaling 的本质**：
- `P_calibrated = softmax(logits / T)`，T>1 降温
- Guo et al. 2017 证明：在保序约束下是 **Brier Score 的最优单参数解**（数学定理，非经验）
- **必须对 logits 操作**——对已 softmax 的概率做除法不等于 Temperature Scaling
- **关键发现**：hmmlearn 的 `predict_proba(X)` 返回后验概率矩阵，`np.log()` 即可得到 log_proba——RegimeDetector 只需暴露此接口
- ⚠️ **注意**：HMM 的 log_proba 是对数后验 `log(P(state|X))`，不是 pre-softmax logits。Temperature Scaling 对后验做 `softmax(log_proba/T)` 在数学上是"tempering"，有效但 Guo 2017 的 Brier 最优性定理不直接成立。实践中仍有效（mock 验证已确认，详见 §2.2.9）

**Platt Scaling 的本质**：
- `P_calibrated = sigmoid(a · P_raw + b)`，假设校准曲线是 sigmoid 形状
- 第一性问题：我们的校准曲线**真的**是 sigmoid 吗？B1 显示 80-100% 桶误差 45.9%，这种形状可能不是标准 sigmoid
- 2 参数可能不够灵活

**Isotonic Regression 的本质**：
- 非参数单调映射，不假设函数形式
- 第一性问题：不假设形状 = 更好吗？
  - 准确性 ✅ 能拟合任意形状
  - 锐度 ❌ 可能压平分布（预测往 0.5 聚拢）
  - 样本效率 ❌ 每桶需足够样本，稀有态过拟合
  - 理论保证 ⚠️ 有保序收敛性，但无 Brier 最优性

**SMART（2025, arXiv:2506.23492）**：
- 按样本自适应温度——不同样本用不同 T
- 基于 top-2 logit gap：gap 大（模型确定）→ T 大（多降温），gap 小（不确定）→ T 小
- 第一性优势：HMM 有时态概率接近（0.4/0.3/0.2），有时一个态碾压（0.95/0.03/0.02），应不同降温

#### 2.2.4 长远战略方案：两阶段校准 + 可升级架构

```
HMM log_proba
    ↓
Stage 1: Temperature Scaling（全局降温，治本）
    ↓
Stage 2: Isotonic Regression（局部修正，治标）
    ↓
校准概率
```

**为什么这个组合最优**：

| 性质 | Stage 1 (Temp) | Stage 2 (Isotonic) | 组合 |
|---|---|---|---|
| 准确性 | 解决全局过自信 | 修正残余局部偏差 | ✅✅ |
| 锐度 | ✅ 保锐度（只降温不压平） | Stage 1 已防压平 | ✅✅ |
| 保序性 | ✅ 不改变 argmax | ✅ 单调 | ✅✅ |
| 样本效率 | ✅ 1 参数，60 天够学 | ⚠️ 但 Stage 1 已降维 | ✅ |
| 理论保证 | ✅ Brier 最优 | ⚠️ 保序收敛 | ✅ |

**分工**：
- Stage 1 Temperature：治本——解决整体过自信，1 参数，有理论保证，不改变预测类别
- Stage 2 Isotonic：治标——修正 Stage 1 后的残余局部偏差（如某中间桶仍有偏差）

**为什么不只用 Stage 1**：Temperature 假设所有置信度区间过自信程度相同，但可能高置信度过自信严重、低置信度正常——Isotonic 补这个局部偏差。

**为什么不只用 Stage 2**：Isotonic 单独用时在稀有态（数据少）会过拟合 + 压平分布。Temperature 先做全局降温，降低 Isotonic 的工作量和过拟合风险。

#### 2.2.5 可升级架构（长远战略）

```python
# 可插拔 Calibrator 接口
class Calibrator(ABC):
    @abstractmethod
    def fit(self, log_proba: np.ndarray, occurred: np.ndarray) -> None: ...
    @abstractmethod
    def transform(self, log_proba: np.ndarray) -> np.ndarray: ...

# Stage 1 可插拔实现
class TemperatureCalibrator(Calibrator): ...   # 当前：全局温度
class SMARTCalibrator(Calibrator): ...         # 未来 v2：按样本自适应温度
class ATSCPCalibrator(Calibrator): ...         # 未来 v3：共形预测

# Stage 2 固定
class IsotonicCalibrator(Calibrator): ...      # 非参数局部修正

# 两阶段串联
class TwoStageCalibrator:
    def __init__(self, stage1: Calibrator, stage2: Calibrator): ...
    def fit(self, log_proba, occurred):
        self.stage1.fit(log_proba, occurred)
        mid = self.stage1.transform(log_proba)
        self.stage2.fit(mid, occurred)
    def transform(self, log_proba):
        mid = self.stage1.transform(log_proba)
        return self.stage2.transform(mid)
```

**升级路径**：
```
v1（当前）: TemperatureCalibrator + IsotonicCalibrator
v2（未来）: SMARTCalibrator + IsotonicCalibrator     ← Stage 1 升级，不改下游
v3（远期）: ATSCPCalibrator + IsotonicCalibrator      ← 有覆盖保证
```

#### 2.2.6 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | 改造 RegimeDetector 暴露 `predict_log_proba()` | ~20 行，hmmlearn 已有内部方法 |
| 2 | 写 `Calibrator` 基类 + 接口 | `calibrator_base.py` ~50 行 |
| 3 | 写 `TemperatureCalibrator` | ~60 行，T 从验证集学 |
| 4 | 写 `IsotonicCalibrator` | ~40 行，包装 sklearn |
| 5 | 写 `TwoStageCalibrator` | ~40 行，串联 Stage 1→2 |
| 6 | 集成到 walk-forward | 每季度 refit 时同步重拟合校准参数 ~30 行 |
| 7 | 集成到 B1 验证器 | 校准后 confidence 再跑 B1 ~20 行 |
| 8 | 单元测试 | ~150 行（测单调性、保序性、walk-forward 稳定性） |

#### 2.2.7 验收标准

- [ ] B1 校准误差 < 10%（从 27.6% 降低）
- [ ] 80-100% 桶误差 < 15%（从 45.9% 降低）
- [ ] 保序性：校准后概率排序与原始一致
- [ ] walk-forward 稳定性：T 参数跨季度变化 < 50%
- [ ] Calibrator 接口可插拔（SMART 能直接替换 Stage 1）

#### 2.2.8 校准器数据流详解（施工必读）

**A. occurred 标签的计算流程（对接 B1 验证器）**

校准器 `fit(log_proba, occurred)` 中的 `occurred` 是二值标签（0/1），来源是 B1 验证器的"后续收益实现代理标签"逻辑。完整流程：

> ⚠️ **forward_days 初始值 = 20**（继承 B1 验证器默认值 `DEFAULT_FORWARD_DAYS = 20`，`b1_probability_calibration.py:60`）。P0-E2 施工时直接用 20，P2-E8 扫描后再更新。

```python
# 步骤 1：算每个 timestamp 的后续 forward_days 累计收益
# （复用 B1 的 _compute_forward_returns，b1_probability_calibration.py:240）
forward_returns = close.shift(-forward_days) / close - 1.0

# 步骤 2：按态分组，推断每态"预期方向"（涨/跌）
# （复用 B1 的 _infer_regime_directions，b1_probability_calibration.py:252）
# |mean_return| < 0.5% (MIN_RETURN_THRESHOLD) 的态视为无明确方向，跳过
regime_directions = {}
for regime, rets in regime_returns.items():
    mean_r = np.mean(rets)
    if abs(mean_r) < 0.005:
        continue  # 无明确方向
    regime_directions[regime] = "涨" if mean_r > 0 else "跌"

# 步骤 3：标记 occurred
# 后续收益方向与态预期方向一致 → occurred=1，否则=0
for rec in records:
    direction = regime_directions.get(rec["dominant_regime"])
    if direction is None:
        continue
    expected_pos = (direction == "涨")
    actual_pos = (rec["forward_return"] > 0)
    occurred = 1 if (expected_pos == actual_pos) else 0
```

**校准器与 B1 的对接关系**：
- B1 验证器已有完整的 `occurred` 计算逻辑
- 校准器**复用 B1 的 occurred 计算**，不重复实现
- 校准器在 B1 的 `validate()` 之前插入：`log_proba → calibrator.transform() → 校准后 confidence → B1.validate()`

**B. T 参数优化方法（对标 Guo et al. 2017）**

Temperature Scaling 的 T 参数通过**在 IS 数据上最小化二元交叉熵** 学习：

> ⚠️ **注意**：标准 Temperature Scaling（Guo 2017）用多类 NLL，但我们的 `occurred` 是"预测是否正确"的二值指标，不是类别标签。正确目标函数是二元交叉熵。详见 §2.2.9 Bug #3 的分析。

```python
from scipy.optimize import minimize_scalar

def fit_temperature(log_proba: np.ndarray, occurred: np.ndarray) -> float:
    """T 从 IS 数据学：最小化二元交叉熵（详见 §2.2.9）。
    
    Args:
        log_proba: (N, n_states) HMM 对数概率
        occurred: (N,) 二值标签（0/1，1=预测方向正确）
    
    Returns:
        T: 最优温度参数（>0，通常 1.0-5.0）
    """
    def binary_cross_entropy(T):
        # softmax(log_proba / T) → 校准概率
        scaled = log_proba / T
        log_softmax = scaled - np.logaddexp.reduce(scaled, axis=1, keepdims=True)
        proba = np.exp(log_softmax)
        # 校准后 confidence = max probability
        calibrated_confidence = proba.max(axis=1)
        # 二元交叉熵
        eps = 1e-8
        return -np.mean(
            occurred * np.log(calibrated_confidence + eps) +
            (1 - occurred) * np.log(1 - calibrated_confidence + eps)
        )
    
    result = minimize_scalar(binary_cross_entropy, bounds=(0.1, 10.0), method='bounded')
    return result.x
```

**T 参数特性**：
- T=1.0 → 无校准（原始概率）
- T>1.0 → 降温（降低过度自信）
- T<1.0 → 升温（罕见，模型欠自信时用）
- 预期我们的 T 在 2.0-5.0 之间（因 80-100% 桶严重过自信）

**C. log_proba 维度处理**

HMM 输出的 `log_proba` 是 `(T, n_states)` 矩阵（每个时间点对每个态的对数概率）。Temperature Scaling 对**全态**做 `softmax(log_proba / T)`，不是只对 max 态做缩放：

```python
# 正确：对全态做温度缩放
calibrated_proba = softmax(log_proba / T, axis=1)  # (T, n_states)

# 校准后 confidence = max(calibrated_proba, axis=1)
calibrated_confidence = calibrated_proba.max(axis=1)
```

**关键区别**：
- 对全态做 → 重新分配所有态的概率，confidence 自然降低
- 只对 max 态做 → 只改一个值，不保证概率和为 1

**改造 RegimeDetector 暴露 log_proba**：
```python
# regime_detector.py 新增方法
def predict_log_proba(self, X: np.ndarray) -> np.ndarray:
    """返回 HMM 对数后验概率 (T, n_states)——Temperature Scaling 的输入。

    hmmlearn 的 predict_proba(X) 返回 P(state|X) 后验概率矩阵，
    取 np.log() 得到对数后验。加 epsilon 防 log(0)。

    注意：这是对数后验 log(P(state|X))，不是 pre-softmax logits。
    Temperature Scaling 对此做 softmax(log_proba/T) 是"tempering"，
    数学上有效但非标准 Temperature Scaling（详见 §2.2.3 注释）。
    """
    proba = self._hmm_model.predict_proba(X)  # (T, n_states) 后验概率
    return np.log(proba + 1e-30)  # 加 epsilon 防 log(0)
```

**D. Isotonic 分桶策略**

Stage 2 的 Isotonic Regression 分桶对齐 B1 验证器的 `BUCKET_EDGES`：

```python
from sklearn.isotonic import IsotonicRegression

# B1 的分桶（b1_probability_calibration.py:58）
BUCKET_EDGES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  # 5 桶

# Stage 2 校准器：分桶后每桶算实际频率，Isotonic 拟合
def fit_isotonic(confidences: np.ndarray, occurred: np.ndarray) -> IsotonicRegression:
    # 分桶
    bucket_idx = np.digitize(confidences, BUCKET_EDGES[1:-1])
    # 每桶算 (mean_confidence, mean_occurred)
    points = []
    for i in range(len(BUCKET_EDGES) - 1):
        mask = bucket_idx == i
        if mask.sum() < 5:  # 每桶至少 5 个样本
            continue
        points.append((confidences[mask].mean(), occurred[mask].mean()))
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    iso = IsotonicRegression(out_of_bounds='clip')
    iso.fit(x, y)
    return iso
```

**样本效率保障**：
- walk-forward 每季 ~60 天 → 5 桶每桶 ~12 个样本
- Stage 1 Temperature 已做全局降温 → Stage 2 的残余偏差小 → Isotonic 不需太细
- 每桶 < 5 个样本时跳过该桶（防止过拟合）

**E. 持久化机制**

walk-forward 每季度 refit 后，校准参数需保存/加载：

```python
# 保存
import json
calibration_artifact = {
    "quarter": "2024Q3",
    "T": 2.34,  # Temperature 参数
    "isotonic_x": [0.12, 0.31, 0.52, 0.71, 0.89],  # Isotonic 输入点
    "isotonic_y": [0.15, 0.28, 0.48, 0.63, 0.75],  # Isotonic 输出点
    "fit_samples": 1260,
    "fit_date": "2024-09-30",
}
# 保存到 runtime/calibration/calibration_2024Q3.json

# 加载
with open("runtime/calibration/calibration_2024Q3.json") as f:
    artifact = json.load(f)
calibrator = TwoStageCalibrator(
    stage1=TemperatureCalibrator(T=artifact["T"]),
    stage2=IsotonicCalibrator.from_points(
        artifact["isotonic_x"], artifact["isotonic_y"]
    ),
)
```

**F. PIT 数据泄漏防范**

校准参数必须**只用 IS 数据拟合**，不能看 OOS：

```python
# walk-forward 季度循环
for i, q in enumerate(quarter_ends):
    # IS 数据：训练窗口
    train_start = q - DateOffset(years=train_years)
    train_end = q
    X_is = features.loc[train_start:train_end]
    
    # 1. 用 IS 数据 fit HMM
    detector.fit(X_is)
    log_proba_is = detector.predict_log_proba(X_is)
    
    # 2. 用 IS 数据的 occurred 标签 fit 校准器
    #    ❌ 禁止：用 OOS（detect_start:next_q）的 occurred
    occurred_is = compute_occurred(X_is, close, forward_days)
    calibrator.fit(log_proba_is, occurred_is)
    
    # 3. 保存校准参数
    save_calibration(calibrator, quarter=q)
    
    # 4. OOS detect：加载本季度校准器，校准后 confidence
    for dt in detect_dates_this_quarter:
        log_proba = detector.predict_log_proba(X[dt])
        confidence = calibrator.transform(log_proba)  # 校准
```

#### 2.2.9 数据泄漏边界分析与防护（施工必读）

**审查发现 3 个泄漏点 + 1 个实现 bug，必须在施工前修复。**

---

**泄漏 #1：forward_returns 跨 IS/OOS 边界（中等严重）**

**问题**：`forward_returns = close.shift(-forward_days) / close - 1.0`。IS 数据最后一天（如 2018-12-31）的 forward_return 需要看 20 个交易日后的收盘价（≈2019-02-01），这已经进入 OOS 段。

**泄漏路径**：
```
IS 末尾 20 天 → forward_return 用了 OOS 收盘价 → occurred 标签被未来数据污染 → T 参数偏移
```

**修复**：IS 数据尾部裁剪 `forward_days` 天，确保所有 forward_return 完全在 IS 范围内：

```python
# ❌ 错误（泄漏）：
X_is = features.loc[train_start:train_end]
occurred_is = compute_occurred(X_is, close, forward_days)
# IS 最后 20 天的 forward_return 跨入 OOS

# ✅ 正确（安全）：
safe_end = train_end - pd.Timedelta(days=forward_days * 1.5)  # 多留余量
X_is_safe = X_is.loc[:safe_end]
close_is_safe = close.loc[:safe_end]
occurred_is = compute_occurred(X_is_safe, close_is_safe, forward_days)
# 所有 forward_return 完全在 IS 范围内
```

---

**泄漏 #2：regime_directions 用全量数据（严重，系统性泄漏）**

**问题**：§2.2.8 A 说"复用 B1 的 `_infer_regime_directions`"，但 B1 验证器的 `_infer_regime_directions` 是在**全量 detect_records** 上算的——它用了 2010-2026 全部数据推断每态预期方向。

如果 walk-forward 的 2024Q3 季度用全量数据推断 regime_directions，那么：
- 2024Q3 的校准器"看到"了 2025-2026 的 forward_returns
- 2025-2026 的收益数据影响了"该态预期涨还是跌"的判定
- 这个方向又用来标记 2024Q3 IS 数据的 occurred

**这是系统性泄漏**——不是边界效应，是每个季度都会发生的。

**关键区别**：
- B1 验证（回顾性分析）：可以用全量数据 → OK
- 校准器 walk-forward（实盘模拟）：必须 PIT，不能用未来数据 → 泄漏

**修复**：regime_directions 必须用**截至当前季度的 PIT 数据**推断，不能用全量：

```python
# ❌ 错误（泄漏）：
# 复用 B1 的全量 _infer_regime_directions
all_records = collect_all_detect_records_2010_2026()
regime_directions = _infer_regime_directions(all_records)  # 看到了 2025-2026
occurred = label_occurred(is_records, regime_directions)

# ✅ 正确（PIT）：
# 只用 IS 裁剪后的数据推断方向
is_safe_records = detect_on_is_data(detector, X_is_safe, close_is_safe)
regime_directions = _infer_regime_directions(is_safe_records)  # 只看 IS 数据
occurred = label_occurred(is_safe_records, regime_directions)
```

**完整的安全 fit 流程**（修正后的 §2.2.8 F）：

```python
for i, q in enumerate(quarter_ends):
    train_start = q - DateOffset(years=train_years)
    train_end = q

    # ── 步骤 1：IS 数据尾部裁剪（防泄漏 #1）──
    safe_end = train_end - pd.Timedelta(days=forward_days * 1.5)
    X_is_safe = features.loc[train_start:safe_end]
    close_is_safe = close.loc[train_start:safe_end]

    # ── 步骤 2：HMM fit + log_proba（只用安全 IS 数据）──
    detector.fit(X_is_safe)
    log_proba_is = detector.predict_log_proba(X_is_safe)

    # ── 步骤 3：PIT 推断 regime_directions（防泄漏 #2）──
    # ❌ 禁止：用全量 records 推断方向
    # ✅ 只用 IS 安全数据推断方向
    is_records = collect_detect_records(detector, X_is_safe, close_is_safe)
    regime_directions = _infer_regime_directions(is_records)

    # ── 步骤 4：标记 occurred（用 PIT 方向）──
    occurred_is = label_occurred(is_records, regime_directions, close_is_safe, forward_days)
    # 此时所有 forward_return 完全在 safe IS 范围内

    # ── 步骤 5：fit 校准器（log_proba + occurred 都来自安全 IS 数据）──
    calibrator.fit(log_proba_is, occurred_is)

    # ── 步骤 6：保存 + OOS transform（无泄漏）──
    save_calibration(calibrator, quarter=q)
    for dt in detect_dates_this_quarter:
        log_proba = detector.predict_log_proba(X[dt])
        confidence = calibrator.transform(log_proba)
```

---

**Bug #3：NLL 的 `occurred.argmax(axis=1)` 实现错误**

**问题**：§2.2.8 B 的 `fit_temperature` 中：
```python
nll_val = -np.mean(log_prob[np.arange(len(occurred)), occurred.argmax(axis=1)])
```

`occurred` 被定义为 `(N,)` 二值标签（0/1），但 `occurred.argmax(axis=1)` 假设 occurred 是 2D one-hot 编码——1D 数组没有 `axis=1`，会报 `AxisError`。

**更深层的问题**：Temperature Scaling 的标准 NLL 是多类交叉熵 `-log(P[true_label])`，但我们的 `occurred` 不是类别标签，而是"预测是否正确"的二值指标。正确的目标函数是**二元交叉熵**：

**修复**：用二元交叉熵替代多类 NLL：

```python
def fit_temperature(log_proba: np.ndarray, occurred: np.ndarray) -> float:
    """T 从 IS 数据学：最小化二元交叉熵。

    Args:
        log_proba: (N, n_states) HMM 对数概率
        occurred: (N,) 二值标签（0/1）
    """
    def binary_cross_entropy(T):
        # softmax(log_proba / T) → 校准概率
        scaled = log_proba / T
        log_softmax = scaled - np.logaddexp.reduce(scaled, axis=1, keepdims=True)
        proba = np.exp(log_softmax)

        # 校准后 confidence = max probability
        calibrated_confidence = proba.max(axis=1)

        # 二元交叉熵：occurred=1 希望 confidence 高，occurred=0 希望 confidence 低
        eps = 1e-8
        bce = -np.mean(
            occurred * np.log(calibrated_confidence + eps) +
            (1 - occurred) * np.log(1 - calibrated_confidence + eps)
        )
        return bce

    result = minimize_scalar(binary_cross_entropy, bounds=(0.1, 10.0), method='bounded')
    return result.x
```

**为什么用二元交叉熵而非多类 NLL**：
- `occurred` 是"模型预测是否正确"的二值指标，不是类别标签
- 校准目标是让 `max(P)` 匹配 `occurred` 的频率——这是二元问题
- 标准 Temperature Scaling（多类 NLL）适用于有明确 true label 的分类任务，我们的场景不同

---

**泄漏防护检查清单（施工时逐项验证）**：

- [ ] IS 数据尾部裁剪 `forward_days * 1.5` 天（防泄漏 #1）
- [ ] regime_directions 只用 IS 安全数据推断（防泄漏 #2）
- [ ] NLL 用二元交叉熵，不用 `occurred.argmax(axis=1)`（修 bug #3）
- [ ] 单元测试：构造已知未来数据的场景，验证校准参数不被未来数据影响
- [ ] walk-forward 审计：打印每季度 fit 用的数据范围，确认不含 OOS

#### 2.2.10 校准器降级策略（样本不足时的 fallback）

**问题**：walk-forward 每季 ~60 天，裁剪 `forward_days * 1.5`（≈30 天）后可能只剩 ~30 天 IS 数据。如果其中某些态的 occurred 样本不足，校准器拟合不稳定。

**三级降级策略**：

```python
def fit_calibrator_with_fallback(
    log_proba: np.ndarray,
    occurred: np.ndarray,
    prev_calibrator: TwoStageCalibrator | None,
) -> TwoStageCalibrator:
    """三级降级：正常→只 Stage 1→回退上季度。"""
    n_samples = len(occurred)

    # ── Level 1：样本 ≥ 50 → 正常 fit Stage 1 + Stage 2 ──
    if n_samples >= 50:
        calibrator = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=IsotonicCalibrator(),
        )
        calibrator.fit(log_proba, occurred)
        _logger.info("校准器 Level 1: 正常 fit (n=%d)", n_samples)
        return calibrator

    # ── Level 2：20 ≤ 样本 < 50 → 只 fit Stage 1 (Temperature) ──
    # Isotonic 需要更多样本，跳过 Stage 2 防止过拟合
    if n_samples >= 20:
        calibrator = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=None,  # 跳过 Stage 2
        )
        calibrator.fit(log_proba, occurred)
        _logger.warning(
            "校准器 Level 2: 只 fit Stage 1 (n=%d < 50)，跳过 Isotonic", n_samples
        )
        return calibrator

    # ── Level 3：样本 < 20 → 回退上季度校准器 ──
    if prev_calibrator is not None:
        _logger.warning(
            "校准器 Level 3: 样本不足 (n=%d < 20)，回退上季度校准器", n_samples
        )
        return prev_calibrator

    # ── Level 4：无上季度校准器 → 不校准 (T=1.0) ──
    _logger.warning(
        "校准器 Level 4: 样本不足且无上季度校准器，T=1.0 不校准 (n=%d)", n_samples
    )
    return TwoStageCalibrator(
        stage1=TemperatureCalibrator(T=1.0),  # T=1.0 = 不校准
        stage2=None,
    )
```

**降级阈值依据**：
- `≥50`：Isotonic 5 桶每桶 ≥10 个样本，统计稳定
- `≥20`：Temperature 1 参数，20 个样本足够拟合（但不够 Isotonic 分桶）
- `<20`：连 1 参数都不稳定，回退上季度

**walk-forward 集成**：
```python
prev_calibrator = None  # 第一季度无前序

for i, q in enumerate(quarter_ends):
    # ... IS 数据准备 + occurred 标签计算 ...

    # 带降级的 fit
    calibrator = fit_calibrator_with_fallback(
        log_proba_is, occurred_is, prev_calibrator
    )

    # 保存本季度校准器，供下季度 Level 3 回退用
    save_calibration(calibrator, quarter=q)
    prev_calibrator = calibrator

    # OOS detect
    for dt in detect_dates_this_quarter:
        confidence = calibrator.transform(log_proba)
```

**验收标准**：
- [ ] 单元测试：构造 n_samples=10/30/60/100 四组数据，验证分别走 Level 4/2/1/1
- [ ] walk-forward 审计：打印每季度降级级别，确认无静默降级

---

## 3. P1 工程详设

### 3.1 P1-E3: NLP 情感分析管道（Mistral-7B + LoRA + RLSP）

#### 3.1.1 目标

建新闻 NLP 情感分析管道，从 `c3_fundamental.news_data` 表提取新闻 → 情感打分 → 供 S2 `bad_news_flat` 和 `policy` 指标使用。

#### 3.1.2 硬件与基座

| 配置项 | 选择 | 理由 |
|---|---|---|
| GPU | RTX 3090 (24GB) | 能跑 7B 模型 LoRA 微调（需 ~16GB） |
| 基座模型 | Mistral-7B | 英文金融最强（88.4% F1，QLoRA Benchmark） |
| 训练方法 | RLSP（市场反馈强化学习） | 无需人工标注，市场是最终裁判 |
| 备选基座 | Qwen2.5-7B | 如 Mistral 中文偏弱影响效果，切中文最优 |

#### 3.1.3 风险提示：Mistral-7B 中文偏弱

Mistral-7B 在英文金融基准上最强（88.4% F1），但中文能力偏弱。我们的 `news_data` 表以 A 股中文新闻为主。

**缓解方案**：
1. 先用 Mistral-7B 零样本跑基线，评估中文新闻情感分类质量
2. 如果中文 F1 < 65%，切换到 Qwen2.5-7B（中文最强开源模型）
3. RLSP 训练方法不受基座影响——用市场涨跌做反馈，模型会自动学到中文金融语义

#### 3.1.4 RLSP 训练方法详解

**传统方法的问题**：需要人工标注新闻情感（正面/负面/中性），成本高、主观性强、标注者不一致。

**RLSP（Reinforcement Learning on Stock Prices）**：
```
新闻 → Mistral-7B(LoRA) → 情感预测 → 后续股票涨跌（市场反馈）→ 强化学习更新 LoRA
```

**核心思想**：不关心模型分类新闻"准不准"，只关心模型预测的情感能不能预测股票涨跌——市场是最终裁判。

**三阶段训练**：

| 阶段 | 方法 | 数据 | 目的 |
|---|---|---|---|
| Stage 0 | 零样本推理 | 无需训练数据 | 建立基线（Mistral-7B 原生能力） |
| Stage 1 | LoRA SFT（监督微调） | Financial PhraseBank（4800句英文） | 让模型学会金融情感分类基本能力 |
| Stage 2 | RLSP（强化学习） | news_data + 对应日期 A 股涨跌 | 用市场反馈微调，学到 A 股特有的情感-收益关系 |

**RLSP 奖励函数设计**（统一版，详见 §3.1.9 完整实现）：
```python
# 模型预测情感 s ∈ [-1, 1]，实际后续收益 r
# 统一版：按收益幅值加权 × 方向匹配符号
# （§3.1.4 和 §3.1.9 统一为同一版本，消除冲突）
reward = abs(r) * (1 if (s > 0) == (r > 0) else -1)
# 方向一致 → 正奖励（收益越大奖励越大）
# 方向不一致 → 负奖励（收益越大惩罚越大）
```

#### 3.1.5 机构踩坑经验（搜索发现的关键洞察）

1. **强语言性能 ≠ 有用的收益预测力**（arXiv:2608.04200）：
   > "All seven downstream models produce positive but small mean rank information coefficients at the one-day horizon; the largest is 0.0143 for FinBERT. None of the 28 model–horizon tests remains significant"
   
   **大白话**：模型分类新闻很准，但用这个预测股票涨跌基本没用——新闻情感和收益的关系本身就弱

   **对我们的启示**：我们需要的不是"预测收益"，而是"检测利空出尽"（S2 触发条件）。这是不同目标——利空出尽检测可能比收益预测更容易

2. **领域适配很重要**（BondBERT 2025）：债券和股票对新闻反应相反，用股票训练的 FinBERT 分析债券新闻会误导——我们只做 A 股，无此问题

3. **LoRA/QLoRA 是关键**：全量重训 LLM 成本天价，LoRA 微调只需 ~$300，效果接近全量训练

#### 3.1.6 管道架构

```
c3_fundamental.news_data（原始新闻）
    ↓
[新闻采集器] 按日期/股票聚合
    ↓
[NLP 推理服务] Mistral-7B(LoRA) → 情感分数 s ∈ [-1, 1]
    ↓
[情感聚合层] 按日/板块/全市场聚合
    ↓
[指标计算器] bad_news_flat / policy 分数
    ↓
overlay_signals_builder
```

#### 3.1.7 news_data 表 schema（施工必读）

**表名**：`c3_fundamental.news_data`（category_id: `fund_news_data`）

**重要**：此表无独立 DDL schema 文件（`schema_file: null`），列定义从代码消费方推断。

**列清单**（来源：`src/zephyr/data/news_dedup.py:53-61` 的 `NEWS_DATA_COLUMNS`）：

| 列名 | 类型 | 必填 | DEFAULT | 说明 |
|---|---|:---:|---|---|
| `news_id` | String | 是 | 无 | MD5(source+title+publish_time)，主键 |
| `publish_time` | DateTime64(3,'Asia/Shanghai') | 是 | 无 | 发布时间（业务列，已迁移时区） |
| `title` | String | 是 | 无 | 新闻标题 |
| `content` | String | 是 | 无 | 新闻内容（全文） |
| `summary` | String | 否 | 有 | 摘要 |
| `source` | String | 是 | 无 | 来源标识（akshare/cls/eastmoney_news/rss/tushare） |
| `source_url` | String | 否 | 有 | 原文链接 |
| `data_source` | String | 是 | 无 | 数据源名称 |
| `region` | String | 否 | 'CN' | 区域标记（US/HK/TW） |
| `language` | String | 否 | 'zh' | 语言标记（en/zh） |

**系统列**：`ingest_ts` / `updated_at`（DateTime64(3,'UTC')）

**其他列**（表 DEFAULT 填充，不在写入清单中）：
- `full_publish_time` — 完整发布时间（1970 表示缺失）
- `category` — 新闻分类

**news_collector.py 查询模板**：
```python
query = f"""
SELECT news_id, publish_time, title, content, summary, source, data_source, region, language
FROM c3_fundamental.news_data
WHERE publish_time BETWEEN '{start_date}' AND '{end_date}'
  AND region = 'CN'
  AND language = 'zh'
ORDER BY publish_time
"""
```

**数据源**（5 个 Provider 统一写入此表）：
- akshare（个股新闻/央视/百度日历/财新/研报）
- cls（财联社电报）
- eastmoney_news（东方财富 7x24 快讯）
- rss（财经新闻 RSS）
- tushare（pro.news_info + pro.news）

#### 3.1.8 Prompt 模板设计

Mistral-7B 推理需要结构化 prompt，输出 JSON 格式情感分数：

```python
SYSTEM_PROMPT = """你是一个专业的 A 股金融新闻情感分析助手。
分析新闻对 A 股市场的影响，返回 JSON 格式：
{
  "sentiment": "positive" | "negative" | "neutral",
  "score": 0.0 到 1.0 之间的浮点数,
  "reason": "简短理由"
}
score 含义：0.0=极端利空，0.5=中性，1.0=极端利好。
只考虑对 A 股大盘的影响，不考虑个个股。"""

USER_TEMPLATE = """新闻标题：{title}
新闻内容：{content}

请分析这条新闻对 A 股大盘的影响，返回 JSON。"""

# Mistral-7B instruct 格式
prompt = f"[INST] {SYSTEM_PROMPT}\n\n{USER_TEMPLATE.format(title=title, content=content)} [/INST]"
```

**输出解析**：
```python
import json
import re

def parse_sentiment(response: str) -> dict:
    """从 LLM 响应解析 JSON。"""
    # 提取 JSON 块（兼容 ```json ... ``` 包裹）
    match = re.search(r'\{[^}]+\}', response, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"sentiment": "neutral", "score": 0.5, "reason": "parse_failed"}
```

**情感分数归一化**：
```python
def sentiment_to_score(parsed: dict) -> float:
    """归一化到 [-1, 1] 区间。"""
    s = parsed["sentiment"]
    score = parsed["score"]
    if s == "positive":
        return score  # [0.5, 1.0] → [0, 1] → 但我们映射到 [0, 1]
    elif s == "negative":
        return -score  # 负面
    else:
        return 0.0  # 中性
```

#### 3.1.9 LoRA SFT 超参数（对标 FinGPT）

**训练框架**：PEFT + transformers + trl（HuggingFace 生态）

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

# 模型加载（4bit 量化适配 RTX 3090 24GB）
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    load_in_4bit=True,          # QLoRA 4bit 量化
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

# LoRA 配置（对标 FinGPT 论文）
lora_config = LoraConfig(
    r=8,                         # LoRA rank
    lora_alpha=16,               # LoRA alpha（alpha/r=2 是标准比例）
    lora_dropout=0.05,           # LoRA dropout
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 注意力层
)

# 训练参数
training_args = TrainingArguments(
    output_dir="./lora_weights/mistral-fin-sft",
    num_train_epochs=3,          # 3 轮
    per_device_train_batch_size=4,  # RTX 3090 24GB 可跑 batch=4
    gradient_accumulation_steps=4,  # 有效 batch=16
    learning_rate=2e-4,          # LoRA 标准学习率
    warmup_ratio=0.03,           # 3% warmup
    lr_scheduler_type="cosine",  # 余弦退火
    save_strategy="epoch",
    fp16=True,                   # 混合精度
    optim="paged_adamw_8bit",    # 8bit AdamW 省显存
)
```

**显存预算（RTX 3090 24GB）**：
- Mistral-7B 4bit 量化：~5GB
- LoRA 参数：~50MB
- 梯度 + 优化器状态：~8GB
- 激活值（batch=4, seq=512）：~6GB
- **总计 ~19GB，24GB 显存够用**

**RLSP 强化学习框架**：
```python
from trl import PPOTrainer, PPOConfig

# RLSP 配置
ppo_config = PPOConfig(
    batch_size=16,
    mini_batch_size=4,
    learning_rate=1e-5,          # RL 用更小学习率
    ppo_epochs=4,
    kl_penalty="kl",             # KL 散度惩罚（防止偏离 SFT 模型太远）
    target_kl=0.1,
)

# 奖励函数
def compute_reward(sentiment_score: float, forward_return: float) -> float:
    """RLSP 奖励：情感方向与收益方向一致 → 正奖励。
    
    Args:
        sentiment_score: 模型预测的情感分数 [-1, 1]
        forward_return: 后续 N 天实际收益率
    """
    direction_match = (sentiment_score > 0) == (forward_return > 0)
    magnitude = abs(forward_return)  # 收益越大奖励/惩罚越大
    return magnitude * (1 if direction_match else -1)
```

**RLSP 训练数据准备**：
```python
# 从 news_data 提取每日全市场新闻聚合 + 对应日期沪深300涨跌
rlsp_dataset = []
for date, news_list in daily_news.items():
    # 聚合当日所有新闻
    for news in news_list:
        rlsp_dataset.append({
            "prompt": format_prompt(news["title"], news["content"]),
            "forward_return": compute_forward_return(date, close, forward_days=5),
        })
```

#### 3.1.10 评估数据集与方法

**评估数据集**：

| 数据集 | 规模 | 语言 | 用途 |
|---|---|---|---|
| Financial PhraseBank | 4800 句 | 英文 | SFT 训练 + 评估基线 |
| A 股新闻标注集（自建） | 200 条 | 中文 | 中文 F1 评估 |

**自建中文评估集**：
1. 从 `news_data` 表随机抽 200 条（分层：100 条危机期 + 50 条复苏期 + 50 条常态）
2. 用 GPT-4 或人工标注 sentiment（positive/negative/neutral）
3. 标注质量：双标注者一致率 ≥ 80%（Cohen's Kappa ≥ 0.7）

**评估指标**：

| 指标 | 计算方法 | 门槛 |
|---|---|---|
| **Macro-F1** | 三类（pos/neg/neu）F1 的平均 | 零样本 ≥ 65%，SFT 后 ≥ 75% |
| **Accuracy** | 分类正确率 | — |
| **情感-收益方向一致率** | `P(sign(score) == sign(return))` | RLSP 后 ≥ 55% |
| **推理速度** | 1000 条新闻耗时 | < 5 分钟（RTX 3090） |

**评估流程**：
```python
# 零样本基线
zero_shot_f1 = evaluate(mistral_zero_shot, eval_set_200)

# 切换判定
if zero_shot_f1 < 0.65:
    # Mistral 中文太弱，切 Qwen2.5-7B
    model = "Qwen/Qwen2.5-7B-Instruct"
    zero_shot_f1 = evaluate(qwen_zero_shot, eval_set_200)

# LoRA SFT 后
sft_f1 = evaluate(mistral_sft, eval_set_200)

# RLSP 后
rlsp_direction_accuracy = evaluate_direction(model_rlsp, news_return_pairs)
```

**模型版本管理**：
```
models/
├── mistral-7b-zero-shot/       # 零样本基线（不保存权重，用 HF 原始）
├── mistral-7b-sft-v1/          # LoRA SFT 权重
│   ├── adapter_config.json
│   └── adapter_model.bin
└── mistral-7b-rlsp-v1/         # RLSP 增强权重
    ├── adapter_config.json
    └── adapter_model.bin
```

#### 3.1.11 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | 新闻采集器 | `news_collector.py`，按 §3.1.7 schema 查询 |
| 2 | NLP 推理服务 | `nlp_inference.py`，按 §3.1.8 prompt 模板 |
| 3 | 零样本基线评估 | 跑 200 条中文评估集，按 §3.1.10 指标 |
| 4 | 自建中文评估集 | 200 条人工/GPT-4 标注 |
| 5 | LoRA SFT 微调 | 按 §3.1.9 超参数，用 Financial PhraseBank |
| 6 | SFT 后评估 | 中文 F1 ≥ 75% |
| 7 | RLSP 强化学习 | 按 §3.1.9 RLSP 框架，用 news_data + A 股涨跌 |
| 8 | RLSP 后评估 | 情感-收益方向一致率 ≥ 55% |
| 9 | 情感聚合层 | `sentiment_aggregator.py`，按日/板块聚合 |
| 10 | 离线批量推理 | 2010-2026 全历史 news_data 批量推理（回测用） |
| 11 | 单元测试 + 端到端测试 | |

#### 3.1.12 验收标准

- [ ] 零样本中文 F1 ≥ 65%（否则切 Qwen2.5-7B）
- [ ] LoRA SFT 后 F1 ≥ 75%
- [ ] RLSP 后情感-收益方向一致率 ≥ 55%
- [ ] 推理速度：1000 条新闻 < 5 分钟（RTX 3090）
- [ ] 管道端到端：news_data → bad_news_flat 分数
- [ ] 离线批量推理完成（2010-2026 全历史）
- [ ] 模型权重持久化（SFT + RLSP 版本）

---

### 3.2 P1-E4: 资金/板块数据激活

#### 3.2.1 目标

激活已注册但未启用的 7 张 Phase 2c 数据表，让 T3 资金主线维度从 stub 降级变为真实数据。

#### 3.2.2 数据库盘点结果

**已有数据表（113 张表中与 regime 相关的）**：

| category_id | 表名 | 说明 | 当前状态 |
|---|---|---|---|
| `market_money_flow` | `c1_market.money_flow` | 主力资金净流入/流出 | ⚠️ gated（代码写好但默认关） |
| `market_hk_connect_flow` | `c1_market.hk_connect_flow` | 沪深港通北向/南向资金 | ⚠️ gated |
| `market_limit_up_down` | `c1_market.limit_up_down` | 涨跌停数据 | ⚠️ gated |
| `market_sector_kline` | `c1_market.kline_sector` | 行业板块日 K | ⚠️ gated |
| `market_option_iv` | `c1_market.option_iv_surface` | 期权 IV 曲面 | ✅ 已用（合成 VIX 后备） |
| `market_etf_kline_30min` | `c1_market.kline_etf_30min` | ETF 30 分钟 K | ⚠️ gated |
| `market_etf_kline_60min` | `c1_market.kline_etf_60min` | ETF 60 分钟 K | ⚠️ gated |
| `market_margin_trading` | `c1_market.margin_trading` | 融资融券 | ❌ 未使用 |
| `market_dragon_tiger` | `c1_market.dragon_tiger` | 龙虎榜 | ❌ 未使用 |
| `market_block_trade` | `c1_market.block_trade` | 大宗交易 | ❌ 未使用 |
| `market_option_greeks` | `c1_market.option_greeks` | 期权 Greeks | ❌ 未使用 |

**当前 regime 默认配置**：`enable_phase2c=False` + `data_loader=None` → 只查 `kline_index` 一张表。

#### 3.2.3 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | Phase 2 验证脚本注入 `RegimeDataLoader` | `enable_phase2c=True` + `data_loader=RegimeDataLoader(...)` |
| 2 | 验证 7 张表查询无异常 | 跑 `run_phase2_validation.py` 确认无降级 warning |
| 3 | 同步激活 C1 回测验证 | `run_c1_shrinkage_validation.py` 也注入 data_loader |

#### 3.2.4 验收标准

- [ ] Phase 2 验证日志无 "data_loader is None, 降级" warning
- [ ] 7 张表查询成功率 100%
- [ ] T3 维度从 0.0 降级变为真实数值

---

### 3.3 P1-E5: T3 _compute_t3_inputs 激活与注释清理

#### 3.3.1 现状：代码已实现，只需激活数据

**调研发现**（2026-08-07）：`_compute_t3_inputs` **已不是 stub**，Phase 2c 已完整实现（`overlay_signals_builder.py:516-549`）。7 个 T3 评分函数也已实现（`overlay_features.py:474-650`）。

**当前问题**：
1. **数据未激活**：`feature_builder` 的 `get_money_flow()` / `get_sector_kline()` / `get_limit_up_down()` 依赖 `RegimeDataLoader`，需 `enable_phase2c=True` + 注入 `data_loader`（P1-E4 的任务）
2. **注释漂移**：`overlay_signals_builder.py:98` 仍标注"stub（资金/板块）"，`:109` 仍写"当前返回空 dict"——与实际代码不符
3. **hk_connect_flow 未接入**：`_compute_t3_inputs` 只用了 `money_flow` 的 `avg_main_net_inflow_pct`，未融合 `hk_connect_flow` 的北向资金

#### 3.3.2 T3 四维度现有实现（已写好的代码）

**`_compute_t3_inputs`**（`overlay_signals_builder.py:516-549`）产出 7 个输入：

| 输入 key | 数据源 | 说明 |
|---|---|---|
| `inflow_pct` | `get_money_flow()` → `avg_main_net_inflow_pct` | 全市场主力净流入占比 |
| `limit_up_count` | `get_limit_up_down()` | 涨停家数 |
| `sector_hhi` | `get_sector_kline()` → `_compute_sector_metrics()` | 板块涨幅 HHI（赫芬达尔指数） |
| `top_sector_pct` | 同上 | 头部板块涨幅 |
| `max_consec_limit` | `get_limit_up_down()` → `_compute_limit_up_metrics()` | 最高连板数 |
| `promotion_rate` | 同上 | 晋级率（昨日涨停今日仍涨停比例） |
| `prev_top3_max_today_pct` | `get_sector_kline()` | 昨日 Top3 板块今日最佳涨幅 |

**7 个 T3 评分函数**（`overlay_features.py:474-650`，全部已实现）：

| 函数 | 输入 | 输出值域 | 映射逻辑 |
|---|---|---|---|
| `t3_money_effect_score(inflow_pct, limit_up_count)` | 主力净流入占比 + 涨停数 | {0,25,50,65,80} | >5%&>100→80；>3%&>50→65；>2%&>30→50；>0→25 |
| `t3_mainline_score(sector_hhi, top_sector_pct)` | 板块 HHI + 头部涨幅 | {0,35,65,80} | HHI>0.15&Top>3%→80；>0.10&>2%→65；>0.08&>1%→35 |
| `t3_leader_score(max_consec_limit, promotion_rate)` | 最高连板 + 晋级率 | {0,35,65,80} | ≥5&>0.5→80；≥3&>0.3→65；≥2→35 |
| `t3_one_day_mainline_flag(prev_top3_max_today_pct)` | 昨日Top3今日最佳涨幅 | {0.0,1.0} | < -2.0 → 1.0（主线一日游证伪） |
| `t3_volume_price_score(pct_change, vol_z)` | 涨跌幅 + 量能 z | {0,35,65,80} | 涨>2%&z>2→80；涨>1%&z>1→65；涨>0&z>0→35 |
| `t3_ma_trend_score(close)` | 收盘价 | {0,30,60,70} | 强多头(MA5/MA60>1.05)→70；多头排列→60 |
| `t3_sentiment_score(ad_ratio)` | 涨跌家数比 | {0,35,65,80} | >0.6→80；>0.3→65；>0→35 |

**T3 触发阈值**（`regime_detector.py:128-138`，`TRANSITION_CONFIG["T3"]`）：

```python
"T3": {  # RECOVERY → BREAKOUT → Bull-Medium
    "stages": {
        "strong_confirm": {"total_gte": 200, "shrinkage": 1.0},
        "confirm":        {"keys_gte": {"volume_price": 60, "ma_trend": 50, "money_effect": 50},
                           "shrinkage": 0.85},
        "trigger":        {"keys_gte": {"sentiment": 60, "mainline": 60, "leader": 60},
                           "p_overlay": {"r12": 0.55}, "shrinkage": 0.7},
        "fail":           {"keys_gte": {"one_day_mainline": 1},
                           "p_overlay": {"r11": 0.60}, "shrinkage": 0.6},
    },
}
```

**阶段判定优先级**：`strong_confirm → confirm → trigger → fail`，取首个满足。

#### 3.3.3 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | 清理注释漂移 | `overlay_signals_builder.py:98,109` 去掉"stub"标注，改为"已实现，依赖数据激活" |
| 2 | 融合 hk_connect_flow 北向资金 | 在 `_compute_t3_inputs` 中增加 `get_hk_connect_flow()` 调用，与 `inflow_pct` 融合（如加权或取 max） |
| 3 | 验证数据激活后 T3 能触发 | P1-E4 激活后，跑 Phase 2 验证检查 T3 维度非 0.0 |
| 4 | 补单元测试 | 测 7 个评分函数的映射逻辑 + T3 trigger 阈值 |

#### 3.3.4 验收标准

- [ ] 注释漂移清理（grep "stub" 在 T3 相关行无残留）
- [ ] 7 个 T3 维度在数据激活后返回真实数值（非 0.0 降级）
- [ ] T3 转换在历史主升浪期能触发（如 2020-03 疫情后反弹、2014-12 牛市启动）
- [ ] hk_connect_flow 北向资金已融合到 money_effect
- [ ] 单元测试覆盖率 ≥ 90%（7 个评分函数各 3+ 用例）

---

### 3.4 P1-E6: bad_news_flat 指标

#### 3.4.1 目标

实现"利空出尽"检测指标，作为 S2（复苏确认）触发的必要条件之一。

#### 3.4.2 算法设计

**"利空出尽"模式定义**：连续负面新闻后，负面新闻减少或中性新闻增加 → 利空已被市场消化。

```python
def bad_news_flat_score(news_sentiment: pd.Series, window: int = 5) -> pd.Series:
    """利空出尽分数 ∈ [0, 100]。
    
    算法：
    1. 过去 window 天的负面新闻占比 neg_ratio = neg_count / total_count
    2. 前 window 天的负面占比 prev_neg_ratio
    3. 如果 prev_neg_ratio > 0.6（前段确实有大量利空）
       且 neg_ratio < prev_neg_ratio * 0.5（后段负面减半）
       → bad_news_flat = 60-100（利空出尽）
    4. 否则 → 0-40
    """
```

#### 3.4.3 工程步骤

| 步骤 | 内容 | 依赖 |
|---|---|---|
| 1 | 实现 `bad_news_flat_score` 函数 | P1-E3 NLP 管道产出 news_sentiment |
| 2 | 集成到 `overlay_features.py` | |
| 3 | 集成到 `overlay_signals_builder.py` 的 S2 触发逻辑 | |
| 4 | 单元测试 | 构造"先利空后出尽"的合成新闻序列 |

#### 3.4.4 验收标准

- [ ] S2 在 2020-03 疫情复苏期（3 月底-4 月）能触发
- [ ] S2 在 2024-02 低点后复苏期能触发
- [ ] S2 常态不误触发
- [ ] B4 S2 命中率 ≥ 2/3

---

### 3.5 P1-E9: S2 评分算法重设计（时点错配治本）

> **诊断详档**：[discussion_023](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_023_s2_algorithm_misalignment_diagnosis.md)（完整诊断报告 + 架构裁定 + 治本详设）
> **治理登记**：#ARCH-REGIME-S2-ALGORITHM-001（待登记）
> **本节为引用摘要**——完整诊断证据与裁定推理见 discussion_023，本节仅列工程清单所需的背景/步骤/验收。

#### 3.5.1 背景（简述）

B4 验证暴露 S2 recovery 0/3 未触发。诊断脚本 `scripts/tests/dump_s2_scores.py` 证实根因是 **S2 评分算法时点错配**（非数据缺失）——三个关键维度在复苏事件日恒为 0：

| 维度 | 设计意图（§4.12） | 实现（overlay_features.py） | 错配 |
|---|---|---|---|
| capitulation | 危机见底的**过程**信号（近 N 日曾出现投降抛售） | **当日** vol_z>2 ∧ 跌幅>1.5% | 复苏日不暴跌 → 恒 0 |
| valuation | PE/破净率等**基本面估值** | close/rolling_max(250) 价格回撤，pos<0.50 才给 40 分 | 非腰斩级复苏 → 恒 0 |
| spring | Wyckoff Spring（需 high/low） | 用 close 简化判断 | 偶尔触发，但 total 不够 |

trigger/confirm/strong_confirm 三阶段全堵死。NLP 维度（bad_news_flat=80 / policy=80）评分正常，证明 P1-E3/E6 数据已生效——**S2 不触发的根因不在数据，而在算法**。故 P1-E3/E4/E5/E6/E7 即使全部完成，S2 仍 0/3。

#### 3.5.2 裁定（简述）

- **立即**：回退 `historical_events.yaml` S2 `data_ready` true→false，B4 回 PASS(3/3)，Phase 2 闭环
- **立即**：登记 #ARCH-REGIME-S2-ALGORITHM-001
- **P1 阶段**：本 P1-E9 算法重设计 → 重跑验证 → S2 激活
- **核心理由**：不为过 B4 而改算法（守住验证独立性），算法重设计独立于验证结果进行（防过拟合）

> 完整裁定推理（第一性原理 + 长远战略 + 100% AI 开发考量）见 [discussion_023 §2](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_023_s2_algorithm_misalignment_diagnosis.md)。

#### 3.5.3 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | capitulation 过程化（rolling max，lookback=20，可参数化扫描） | overlay_features.py `s2_capitulation_score` 改造 |
| 2 | valuation 阈值校准（路 B：pos<0.70→40 分）或基本面化（路 A：接入 c1_market.daily_valuation） | `s2_valuation_score` 改造 |
| 3 | spring 复用 wyckoff_engine Spring 事件 | `s2_spring_flag` 改造 |
| 4 | 重跑 dump_s2_scores.py 确认三事件 capitulation/valuation 不再恒 0 | 算法层验证（独立于 B4） |
| 5 | S2 data_ready true 激活 + 重跑 Phase 2（A1+B4+A2+B1） | B4 S2 命中验证 |

#### 3.5.4 验收标准

- [ ] capitulation 取近 N 日 max（过程化），三事件日窗口不再恒 0
- [ ] valuation 路 B 阈值放宽或路 A 接入基本面数据，三事件日窗口不再恒 0
- [ ] spring 复用 wyckoff_engine，不重复逻辑
- [ ] dump_s2_scores.py 显示三事件 trigger/confirm 可达
- [ ] B4 S2 命中率 ≥ 2/3（且非靠调参过拟合达成）
- [ ] 算法重设计独立于 B4 结果（先按设计意图改，再看 B4，禁止"调参直到命中"）

#### 3.5.5 防过拟合铁律

算法重设计必须独立于 B4 验证结果进行——先按 §4.12 设计意图改算法（过程化/基本面化），再看 B4 结果。**禁止"调参直到 3/3 命中"**——若改后仍不命中，说明设计意图与历史事件时点有更深层偏差，应回到 §4.12 重新审视事件标注（expected_stage）而非继续调参。详见 [discussion_023 §3.7](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_023_s2_algorithm_misalignment_diagnosis.md) 与 [discussion_023 §5 开放问题 3](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/discussion_023_s2_algorithm_misalignment_diagnosis.md)。

---

## 4. P2 工程详设

### 4.1 P2-E7: policy 指标

#### 4.1.1 目标

实现政策相关新闻检测指标，作为 S2 触发的辅助条件。

#### 4.1.2 算法设计

**"政策"模式定义**：检测货币政策（降准/降息）、监管政策（IPO/再融资）、产业政策（补贴/限产）相关新闻。

```python
# 政策关键词库
POLICY_KEYWORDS = {
    "monetary": ["降准", "降息", "MLF", "逆回购", "流动性"],
    "regulatory": ["IPO", "再融资", "注册制", "减持新规"],
    "industrial": ["补贴", "限产", "产业政策", "碳中和"],
}

def policy_score(news_sentiment: pd.Series, news_text: pd.Series) -> pd.Series:
    """政策分数 ∈ [0, 100]。"""
    # 1. 关键词匹配：新闻文本含政策关键词
    # 2. 情感方向：政策新闻是正面还是负面
    # 3. 聚合：过去 window 天政策正面新闻占比
```

#### 4.1.3 工程步骤

| 步骤 | 内容 | 依赖 |
|---|---|---|
| 1 | 建政策关键词库 | YAML 配置 |
| 2 | 实现 `policy_score` 函数 | P1-E3 NLP 管道 |
| 3 | 集成到 overlay | |
| 4 | 单元测试 | |

---

### 4.2 P2-E8: forward_days 参数扫描

#### 4.2.1 目标

扫描 B1 验证器的 `forward_days` 参数，找校准误差最小的预测周期。

#### 4.2.2 方法

```python
for forward_days in [5, 10, 20, 40, 60, 120]:
    b1_report = b1_validator.validate(
        detect_records=detect_records,
        close=close,
        forward_days=forward_days,
    )
    # 记录校准误差，选最优
```

#### 4.2.3 学术参考

QLoRA Benchmark（arXiv:2608.04200）测了 1/2/3/5 天 horizon，发现所有模型 rank IC 在 1 天 horizon 最好但都很小（0.01-0.02）。说明短期收益预测力本身就弱——如果扫描后发现所有周期误差都高，可能不是 forward_days 的问题，而是 regime 状态和收益的因果关系本身就弱。

#### 4.2.4 工程步骤

| 步骤 | 内容 | 依赖 |
|---|---|---|
| 1 | 写扫描脚本 | P0-E2 校准器完成 |
| 2 | 跑 6 个参数 | |
| 3 | 选最优 forward_days | |

---

## 5. 治理流程

### 5.1 每个工程之前的必须动作

每个工程（E1-E8）开工前，必须完成以下治理动作：

| 动作 | 说明 | 文件 |
|---|---|---|
| **五图对齐** | 数据流图/决策图/架构图/状态图是否需要更新 | 如涉及数据流/决策变化 |
| **作战地图更新** | 在全景图中标注该工程的模块和依赖 | battle_map 相关 |
| **蓝图编写** | 新模块的 `[BLUEPRINT]` 头注释 | 每个新 .py 文件 |
| **ARCH 登记** | 在 `architecture_issue_registry.yaml` 登记新 ARCH 条目 | 每个新模块 |
| **module_translation 登记** | 在 `module_translation_registry.yaml` 登记 plain_zh 翻译 | 每个新模块 |
| **capability_canonical_file_registry** | 登记 creation_token | 每个新模块 |
| **pre-commit 门禁** | 通过 echo-guard + ast-grep + algo-quality 检查 | 提交前 |

### 5.2 提交规范

- 必须通过 `GitCommitGateway`（`python scripts/git_commit.py`）
- 禁止直接 `git commit`
- 禁止 `--no-verify` 绕过门禁
- 跨 session 续作用 `--adopt-prior-work` + `[no-lookup:continuation]`

### 5.3 每个工程的治理清单

| 工程 | 新模块 | ARCH 条目 | 全景影响 |
|---|---|---|---|
| P0-E1 降态数 | 无（改现有） | 无 | 无 |
| P0-E2 校准器 | `calibrator_base.py` / `confidence_calibrator.py` | #ARCH-CALIBRATOR-001 | 决策图（confidence 后处理） |
| P1-E3 NLP 管道 | `news_collector.py` / `nlp_inference.py` / `sentiment_aggregator.py` | #ARCH-NLP-PIPELINE-001 | 数据流图（news_data→sentiment） |
| P1-E4 数据激活 | 无（改现有） | 无 | 无 |
| P1-E5 T3 实现 | 无（改现有 `_compute_t3_inputs`） | 无 | 无 |
| P1-E6 bad_news_flat | 无（加到 `overlay_features.py`） | 无 | 决策图（S2 触发条件） |
| P2-E7 policy | 无（加到 `overlay_features.py`） | 无 | 决策图（S2 触发条件） |
| P2-E8 forward_days | 无（改现有脚本） | 无 | 无 |

---

## 6. 数据库盘点（已有数据 vs 需新建管道）

### 6.1 已有数据（113 张表）

**regime 默认使用（1 张）**：
- `c1_market.kline_index` — 指数 K 线（HMM 6 特征主源）

**Phase 2c gated（7 张，需 P1-E4 激活）**：
- `c1_market.money_flow` — 主力资金
- `c1_market.hk_connect_flow` — 港股通资金
- `c1_market.limit_up_down` — 涨跌停
- `c1_market.kline_sector` — 板块 K 线
- `c1_market.option_iv_surface` — 期权 IV（已用于合成 VIX）
- `c1_market.kline_etf_30min` / `kline_etf_60min` — ETF 多分时 K

**未使用但有潜力（P2+ 评估）**：
- `c1_market.margin_trading` — 融资融券（杠杆资金）
- `c1_market.dragon_tiger` — 龙虎榜
- `c1_market.block_trade` — 大宗交易
- `c1_market.option_greeks` — 期权 Greeks
- `c1_market.macro_data` — 宏观经济
- `c1_market.daily_valuation` — 日度估值
- `c3_fundamental.news_data` — **新闻数据（NLP 管道输入）**
- `c3_fundamental.disclosure_plan` — 披露计划

### 6.2 需新建的管道

| 管道 | 输入 | 输出 | 工程 |
|---|---|---|---|
| NLP 情感分析管道 | `news_data` 表 | 每日情感分数 | P1-E3 |
| 资金/板块数据激活 | 7 张 gated 表 | T3 真实数据 | P1-E4 |
| T3 指标计算管道 | 资金/板块数据 | 4 维度分数 | P1-E5 |
| bad_news_flat 指标 | NLP 情感分数 | 利空出尽分数 | P1-E6 |
| policy 指标 | NLP 情感分数 + 关键词 | 政策分数 | P2-E7 |
| 概率校准管道 | HMM log_proba | 校准 confidence | P0-E2 |

---

## 7. 机构实践调研汇总

### 7.1 HMM 状态数选择

| 来源 | 状态数 | 关键发现 |
|---|---|---|
| Hamilton 1989 | 2 | 牛/熊，鼻祖论文 |
| 量化社区默认 | 3 | "最常见市场动态，不过度复杂" |
| BIC elbow | 3 | k=2→3 BIC 提升 22k，k=3→4 只 11k，3 是拐点 |
| MDPI 2025 | 3 | 牛/熊/动荡 |
| 4 态方案 | 4 | 需区分波动 regime 时用 |
| **我们（当前）** | **9** | **无机构用 9 态，过度细分** |

**结论**：降到 3-4 态，用 BIC 数据驱动选择。

### 7.2 概率校准前沿

| 方法 | 年份 | 本质 | 理论保证 | 我们适用性 |
|---|---|---|---|---|
| Platt Scaling | 1999 | sigmoid(a·P+b) | 经验 | ⭐⭐ 假设 sigmoid |
| Isotonic Regression | 2005 | 非参数单调 | 保序收敛 | ⭐⭐⭐ 灵活但可能压平 |
| Temperature Scaling | 2017 | softmax(logits/T) | **Brier 最优** | ⭐⭐⭐⭐ 需 logits |
| SMART | 2025 | 按样本自适应 T | Brier 近似 | ⭐⭐⭐⭐⭐ 前沿 |
| ATS-CP | 2025 | 自适应+共形预测 | 覆盖保证 | ⭐⭐⭐⭐⭐ 最前沿 |

**金融领域机构实践**：Platt Scaling + WoE/IV 管道（信用评分场景，需可解释性）。我们不适用 WoE/IV（那是特征工程，不是概率校准）。

**我们的选择**：两阶段 Temperature + Isotonic（对标第一性原理 5 性质），未来升级 SMART。

### 7.3 金融 NLP 前沿

| 模型 | 准确率 | Macro-F1 | 成本 | 部署 |
|---|---|---|---|---|
| FinBERT (ProsusAI) | ~70% | 69.9% | 低（420M, CPU） | 简单 |
| FinGPT (SFT+RLSP) | 82.1% | 80.9% | ~$300/次 | 中等 |
| QLoRA + Mistral-7B | 88.4% | 87.7% | ~$300/次 | 较难 |
| QLoRA + Qwen2.5-7B | ~86% | 86.2% | ~$300/次 | 较难 |

**关键洞察**：新闻情感 → 收益预测力弱（rank IC ~0.01），但我们目标是利空出尽检测（≠ 收益预测）。

**我们的选择**：Mistral-7B + LoRA + RLSP（RTX 3090 24GB）。

---

## 8. 风险与缓解

| 风险 | 影响 | 概率 | 缓解 |
|---|---|---|---|
| Mistral-7B 中文偏弱 | NLP 情感分类不准 | 中 | 先评估中文 F1，<65% 切 Qwen2.5-7B |
| 降态后 A2 仍不 PASS | HMM 本身不适合此数据 | 低 | 考虑 Nonparametric HMM 或换模型 |
| **降态后 C1 回测退化** | **Shrinkage 收益消失** | **中** | **见 §8.1 回滚方案** |
| 校准后 B1 仍不 PASS | confidence 映射设计有更深问题 | 低 | 加 SMART 按样本自适应 |
| RLSP 训练不稳定 | NLP 管道延期 | 中 | 先用 LoRA SFT 基线，RLSP 作为增强 |
| 新闻情感 → 收益预测力弱 | bad_news_flat 效果有限 | 中 | 目标是利空出尽检测而非收益预测 |
| 数据表查询异常 | T3 降级 | 低 | 逐表验证，失败返回 None 降级 |

### 8.1 C1 回测退化回滚方案

**风险**：降态改变了 `_STATE_RISK_FACTORS`，直接影响 C1 shrinkage 计算。如果新态数的 shrinkage 映射不合理，C1 回测可能退化（Sharpe < 0.2678 门槛）。

**回滚流程**：
```
降态后重跑 C1
  ├─ C1 PASS（Sharpe ≥ 0.2678）→ 继续 Phase 2 验证
  └─ C1 FAIL（Sharpe < 0.2678）→ 回滚
       ├─ Level 1: 调整 _STATE_RISK_FACTORS 的 shrinkage 值（不改态数）
       ├─ Level 2: 回退到 9 态 + 仅应用校准器（P0-E2）
       └─ Level 3: 回退到 9 态 + 不校准（当前状态）
```

**Level 1 调整方法**：
```python
# 如果 C1 退化，先调 shrinkage 值，不回退态数
# 原因：降态解决了 A2 过拟合，但 shrinkage 值可能没调好
_STATE_RISK_FACTORS = {
    "r1": 1.0,   # 如果 C1 Turnover 太高，降到 0.95
    "r2": 0.80,  # 如果 MaxDD 太大，降到 0.70
    "r3": 0.45,  # 如果 MaxDD 仍大，降到 0.40
}
# 重跑 C1 验证
```

### 8.2 Phase 3 整体退出标准

Phase 3 完成需同时满足以下条件：

| 条件 | 验证方法 | 门槛 |
|---|---|---|
| **A1 样本充足** | Phase 2 验证 | 全态 ≥100 天 |
| **A2 不过拟合** | Phase 2 验证 | OOS/IS ≥ 0.7 |
| **B1 校准度** | Phase 2 验证（校准后） | 误差 < 10% |
| **B4 转换准确** | Phase 2 验证 | S1 3/3 + S2 ≥ 1/3 |
| **C1 不退化** | C1 回测 | Sharpe ≥ 0.2678, MaxDD ≤ 0.15 |
| **NLP 管道上线** | NLP 评估 | F1 ≥ 65% + bad_news_flat 激活 |
| **T3 数据激活** | T3 维度检查 | 4 维度非 0.0 降级 |

**未通过处理**：
- A1/A2/B1/B4 单项不通过 → 该项重设计后重跑 Phase 2
- C1 退化 → §8.1 回滚方案
- NLP 不达标 → 用 LoRA SFT 基线（不 RLSP），或切 Qwen2.5-7B

---

## 9. 开放问题

1. **BIC 扫描结果**：3 还是 4 是拐点？需跑数据确认
2. **Mistral 中文 F1**：零样本基线能否 ≥65%？需评估
3. ~~**RLSP 奖励函数**：用 `s * sign(r)` 还是 `s * |r|`？~~ **已统一**：`abs(r) * direction_match`（§3.1.4/§3.1.9 统一版）
4. **forward_days 最优值**：5/10/20/40/60/120 哪个校准误差最低？P0-E2 先用 20，P2-E8 扫描后更新
5. **S2 触发门槛**：bad_news_flat ≥ 40 是否合适？需校准

---

## 10. 执行时间线

| 批次 | 工程 | 预估工程量 | 依赖 |
|---|---|---|---|
| 第一批 P0 | P0-E1 降态数 + P0-E2 校准器 | ~440 行 | 无 |
| 第一批 P0 验证 | 重跑 A1/A2/B1/B4 | — | P0-E1+E2 |
| 第二批 P1a | P1-E4 数据激活 + P1-E5 T3 | ~150 行 | 无（T3 代码已实现） |
| 第二批 P1b | P1-E3 NLP + P1-E6 bad_news_flat | ~950 行 | 可与 P1a 并行 |
| 第三批 P2 | P2-E7 policy + P2-E8 forward_days | ~200 行 | P1-E3 + P0-E2 |

---

**下一步**：用户审阅本规划，确认开放问题后，按批次施工。第一批 P0（降态数 + 校准器）优先启动。
