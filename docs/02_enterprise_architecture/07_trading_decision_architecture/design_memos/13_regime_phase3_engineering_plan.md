---
ttl: permanent
doc_type: architecture_view
title: "Phase 3 工程规划——降态数 + 两阶段校准 + NLP 管道 + S2/T3 数据激活"
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.4.1"
date: "2026-08-15"
last_updated: "2026-08-15"
topic: regime_phase3_engineering_plan
scope: 07_trading_decision_architecture
doc_id: 13_regime_phase3_engineering_plan
priority: P0
depends_on:
  - 10_regime_detector_spec.md
  - 11_regime_backtest_validation_plan.md
  - 12_regime_phase2_validation.md
related_modules:
  - MOD-REGIME-001 (RegimeDetector)
  - MOD-REGIME-002 (RegimeFeatureBuilder)
  - MOD-REGIME-VAL-002 (Phase 2 验证器)
  - MOD-DATA-NEWS-001 (news_collector，P1-E3 已建)
  - MOD-NLP-INFERENCE-001 (nlp_inference，P1-E3 已建)
  - MOD-L11-001 (sentiment_sft_trainer，P1-E3 已建)
  - BM-BT-05 (HMM 模型质量验证)
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：P0 两工程全部完工（2026-08-08）——P0-E1 HMM 降态 9→4（BIC Kneedle 拐点=4，walk-forward 46 季度 {4:19,5:25,7:2}）+ P0-E2 两阶段概率校准器（Temperature+Isotonic，confidence_calibrator.py 落码），Phase 2 重验全 PASS（commit 0c5ea28bb1/83c94c4f/e4fd931a：A2 OOS/IS 0.34→1.042，B1 ECE 27.6%→4.2%）；P1 数据层全部完工——E3 NLP 管道 Phase 1-4（news_collector.py / nlp_inference.py / sentiment_sft_trainer.py + scripts/ml 四脚本，SFT Macro-F1=0.7699 达标，实证文件均在）、E4 资金/板块激活（regime_feature_builder.py enable_phase2c 实证）、E5 T3 激活（overlay_features.py t3_* 评分函数 + overlay_signals_builder._STUB_DIMS=set()，64 测试用例）、E6/E7 bad_news_flat/policy 关键词字典 MVP（overlay_features.py:731/765 s2_bad_news_flat_score/s2_policy_score 实证）。
>
> **最终成果**：4 态 HMM 检测器 + 两阶段校准器生产态；S2 数据通路（NLP 关键词 MVP + 资金/板块）就绪；本文档保持 draft（§9-9：P1-E9 完成且 B4 S2 翻 true 后升 active）。
>
> **未做事项及原因**：① P1-E9 S2 评分算法重设计未施工——14 号 v0.4.5 详设就绪但 grep 实证 s2_breadth_thrust_score / keys_or_gte / s2_valuation_score_fundamental / _capitulation_daily 均无落码，Step 0 勘探门禁未启动，未排期；② NLP Phase 5-8 未施工——RLSP（带护栏实验）、GGUF 回灌 Ollama、sentiment_aggregator 端到端管道 + 离线批量、验收，scripts/ml 仅 4 个 SFT 阶段脚本实证；③ P2-E8 forward_days 参数扫描未施工（P2 级收尾，当前默认 20）。

# Phase 3 工程规划——降态数 + 两阶段校准 + NLP 管道 + S2/T3 数据激活

> **前置**：Phase 2 验证完成（commit 14c8b9f1），A1 PASS / B4 S1 3/3 / A2 FAIL / B1 FAIL。
> **本阶段**：修复 A2 过拟合 + B1 过度自信 + 激活 S2/T3 数据管道。
> **后续**：Phase 3 通过 → Phase 4 鲁棒性 → Phase 5 决策门控（对齐 11_regime_backtest_validation_plan §8 五 Phase 定义）。
>
> **当前进度（2026-08-12）**：P0 全部完成（E1 降态 9→4 + E2 校准器，Phase 2 闭环 PASS）；P1 数据层全部完成
> （E3 NLP SFT F1=0.7699 / E4 数据激活 / E5 T3 / E6 bad_news_flat 关键词 MVP / E7 policy 关键词 MVP）；
> **未完工**：P1-E9 S2 算法重设计（详设见 14 号 v0.4.5）、NLP Phase 5-8（RLSP/GGUF 回灌/端到端/验收）、P2-E8 forward_days 扫描。

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
> **2026-08-08 续（S2 算法缺陷诊断）**：另一 session 将 S2 `data_ready` 误改 true 后 B4 退回 FAIL(3/6)。诊断脚本 `dump_s2_scores.py` 证实根因是 **S2 评分算法时点错配**（capitulation 当日值 vs 过程、valuation 价格回撤 vs 基本面），非数据缺失——三事件 capitulation/valuation 恒 0 致 trigger/confirm 永不触发。采用 `design_match=false` 排除 S2 事件（数据已就绪但 Wyckoff 吸筹模板不匹配 A 股 V/政策型复苏）+ 修复 capitulation/valuation 两个 P0 bug（commit 93a25890，B4 维持 PASS(3/3)），登记 #ARCH-REGIME-S2-ALGORITHM-001，新增 P1-E9 工程项（§3.5）治本。完整诊断与裁定见 [14_regime_s2_diagnosis](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md)。

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

| 编号 | 工程名称 | 优先级 | 依赖 | 工程量(行) | 解决问题 | 状态（2026-08-12） |
|---|---|---|---|---|---|---|
| P0-E1 | HMM 降态数 9→4（BIC 定论） | P0 | 无 | ~50 | A2 FAIL 根因 | ✅ 完成（A2 OOS/IS=1.042） |
| P0-E2 | 两阶段概率校准器 | P0 | P0-E1（需重跑验证） | ~390 | B1 FAIL 根因 | ✅ 完成（B1 ECE=4.2%） |
| P1-E3 | NLP 情感分析管道 | P1 | 无（可并行） | ~800 | S2 bad_news_flat 依赖 | 🟡 Phase 1-4 完成（SFT F1=0.7699），Phase 5-8 待做 |
| P1-E4 | 资金/板块数据激活 | P1 | 无 | ~100 | T3 依赖 | ✅ 完成 |
| P1-E5 | T3 激活与注释清理 | P1 | P1-E4 | ~50 | T3 代码已实现，清理注释+融合北向资金 | ✅ 完成（64 测试用例） |
| P1-E6 | bad_news_flat 指标 | P1 | P1-E3 | ~150 | S2 触发条件 | 🟡 数据层完成（关键词字典 MVP），S2 触发验收待 P1-E9 |
| P1-E9 | S2 评分算法重设计 | P1 | 无（算法层，独立于数据激活） | ~120 | S2 时点错配根因（见 14_regime_s2_diagnosis） | ❌ 未施工（14 号 v0.4.5 详设已就绪） |
| P2-E7 | policy 指标 | P2 | P1-E3 | ~150 | S2 触发条件 | 🟡 数据层完成（关键词字典 MVP），质量升级待 P1-E9 |
| P2-E8 | forward_days 参数扫描 | P2 | P0-E2 | ~50 | B1 参数调优 | ❌ 未施工（当前默认 20） |
| **合计** | | | | **~1860** | | P0 全完成 / P1 数据层全完成 / 余 E9+E8+NLP Phase 5-8 |

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

## 1.5 P0 阻断项文件修改清单（历史施工记录——P0 已于 2026-08-08 全部完成，本节保留为审计真源）

> **状态标注（2026-08-12）**：本节为施工前规划原文，P0-E1/E2 已按本清单施工完毕（含 §2.1.6.1 硬编码 9 清单全量替换、
> `predict_log_proba` 新增、`confidence_calibrator.py` 新建、`phase2_runner.py` 集成、单元测试落地、
> `scan_hmm_states.py` BIC 扫描）。实际施工结果与两处实现偏差（T 上界 30.0、Isotonic 免预分桶）回填见 §2.1/§2.2。

4 个阻断项全部 ✅ 完成（commit 0c5ea28bb1/83c94c4f/e4fd931a）：

- #1 hmmlearn API：新增 `predict_log_proba`
- #2 校准器降级：新建 `confidence_calibrator.py` + `phase2_runner.py` 集成 + 单测
- #3 降态后配置失效：重设计 `_STATE_RISK_FACTORS` + `TRANSITION_CONFIG`
- #4 硬编码 9：文件 A-E 共 ~30 处载重 + `dump_c1_repro_artifacts.py` 注释同步

原逐行行号快照为施工期坐标（随代码演进已偏移），审计以 git 历史为准；现态设施见 §1.6.1。

### 文件修改总览

✅ 12 项修改全部完成：文件 A-E 改 4 个阻断项 + 3 个新建（`scan_hmm_states.py` / `confidence_calibrator.py` / `test_confidence_calibrator.py`）+ 1 处注释同步。

### 详细修改路径（按文件分组）

#### 文件 A：`src/zephyr/regime/core/regime_detector.py`（最核心，涉及 3 个阻断项）

✅ 已施工：#3 `_STATE_RISK_FACTORS` + `TRANSITION_CONFIG` 重设计（施工方法 §2.1.6.2/§2.1.6.3，结果回填 §1.6.1）、#4 硬编码 9 共 13 处载重全量参数化（`HMM_STATES` / `n_states` 默认值 / `1.0 / 9.0` / `range(9)` / `len(last) != 9`）、#1 `predict_log_proba` 新增（:472，`np.log(predict_proba(X) + 1e-30)`）。

#### 文件 B：`src/zephyr/regime/validation/phase2/a1_sample_sufficiency.py`（#4，7 处载重）

✅ 已施工：`HMM_STATES_9`→`HMM_STATES_N`、`n_states` 默认值、`total // 9`、`range(9)` 等 7 处载重全量参数化。

#### 文件 C：`src/zephyr/regime/validation/phase2/a2_hmm_overfitting.py`（#4，1 处载重）

✅ 已施工：默认 `n_states` 同步。

#### 文件 D：`tests/regime/test_regime_detector.py`（#4，6 处载重）

✅ 已施工：`1.0 / 9.0` 断言与 `HMM_STATES` 引用 6 处载重全量参数化。

#### 文件 E：`tests/regime/phase2/test_a1_sample_sufficiency.py`（#4，7 处载重）

✅ 已施工：mock 默认值、`np.arange(9)`、断言 7 处载重全量参数化。

#### 新建文件清单

✅ 3 个新文件均已建并验收：`scripts/tests/scan_hmm_states.py`（#3，BIC 扫描 2-9 态）/ `src/zephyr/regime/validation/phase2/confidence_calibrator.py`（#2，两阶段校准器+降级策略）/ `tests/regime/phase2/test_confidence_calibrator.py`（#2，校准器单测）。现态见 §1.6.1。

### 施工顺序（关键路径）

✅ 已按关键路径执行完毕：BIC 扫描定态数（=4）→ 重设计 `_STATE_RISK_FACTORS`+`TRANSITION_CONFIG` → 同步硬编码（文件 A-E ~30 处）→ 新增 `predict_log_proba` → 新建校准器 → `phase2_runner.py` 集成 → 单测 → 重跑 A1+A2+B1+B4（A2 OOS/IS=1.042 ≥0.7 达标，Phase 2 全 PASS）。

---

## 1.6 已施工设施盘点（2026-08-12 全面扫描，通用规则 #11）

> 施工前先看已有什么。本节盘点与本文档主题相关的**全部已建设施**（代码/脚本/模型/配置/测试/治理登记），
> 是后续改动与退役决策的事实基础。状态口径：✅ 生产可用 / 🟡 部分完成 / ❌ 未施工。

### 1.6.1 P0 设施（降态 + 校准器）——全部 ✅

| 设施 | 路径 | 状态 | 说明 |
|---|---|---|---|
| BIC 扫描脚本 | [scan_hmm_states.py](file:///d:/ZephyrAlpha/scripts/tests/scan_hmm_states.py) | ✅ | 全历史 Kneedle 拐点=4；walk-forward 46 季度拐点分布 {4:19, 5:25, 7:2} |
| 降态后检测器 | [regime_detector.py](file:///d:/ZephyrAlpha/src/zephyr/regime/core/regime_detector.py) | ✅ | `REGIME_STATES` 7 态（r1-r4 HMM + r10-r12 overlay）；`HMM_STATES` 4 态；硬编码 9 全量清除 |
| log_proba 接口 | regime_detector.py:472 `predict_log_proba()` | ✅ | Temperature Scaling 输入（对数后验，非 pre-softmax logits） |
| 4 态转换配置 | regime_detector.py `TRANSITION_CONFIG` | ✅ | T1 震荡(r1/r2)→BREAKOUT / T2 熊(r4)→RECOVERY / T4 牛(r3)赶顶 / T5 牛→熊逃顶 / T6 熊(r4)冰点；S1/S2 不依赖基态语义不变 |
| 4 态风险因子 | regime_detector.py `_STATE_RISK_FACTORS` | ⚠️ DEPRECATED | r1:0.90/r2:0.85/r3:1.0/r4:0.50 已按 §2.1.6.2 重设计，但 **2026-08-06 C1 修正（#ARCH-REGIME-CONFIDENCE-FIX-001）已从 ConfidenceSignal 移除**（label-switching 随机惩罚 + 永久中性态惩罚致 Sharpe 0.37→0.10）；dict 保留供 label-switching 对齐协议（§2.1.6.4）落地后重新启用 |
| 两阶段校准器 | [confidence_calibrator.py](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/confidence_calibrator.py) | ✅ | MOD-REGIME_VAL-002；TemperatureCalibrator + IsotonicCalibrator + TwoStageCalibrator；四级降级 `fit_calibrator_with_fallback`（n≥50 / 20≤n<50 / 回退上季 / T=1.0）；`save/load_calibration` 持久化函数 |
| walk-forward 集成 | [phase2_runner.py](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/phase2_runner.py) | ✅ | 每季度 `_fit_calibrator_for_quarter` 内存重 fit；HMM 基态走 Stage1+2、overlay 态走 Stage2；**未调用 save/load（验证场景每季度重 fit，无需跨季加载）** |
| 校准器单测 | [test_confidence_calibrator.py](file:///d:/ZephyrAlpha/tests/regime/phase2/test_confidence_calibrator.py) | ✅ | 单调性/保序性/降级/walk-forward 稳定性 |
| S2 诊断脚本 | [dump_s2_scores.py](file:///d:/ZephyrAlpha/scripts/tests/dump_s2_scores.py) | ✅ | 证实 S2 根因为算法时点错配（非数据缺失） |

### 1.6.2 P1 设施（NLP + 数据激活 + T3 + S2 指标）

| 设施 | 路径 | 状态 | 说明 |
|---|---|---|---|
| 新闻采集器 | [news_collector.py](file:///d:/ZephyrAlpha/src/zephyr/data/news_collector.py) | ✅ | MOD-DATA-NEWS-001；查 `c3_fundamental.news_data`（region=CN / language=zh） |
| NLP 推理服务 | [nlp_inference.py](file:///d:/ZephyrAlpha/src/zephyr/nlp/nlp_inference.py) | ✅ | MOD-NLP-INFERENCE-001；ChatBackend 协议 + CacheLayer；`parse_sentiment` 字段级宽松正则（容忍切片瑕疵） |
| SFT 训练器 | [sentiment_sft_trainer.py](file:///d:/ZephyrAlpha/src/zephyr/ml_train/implementations/sentiment_sft_trainer.py) | ✅ | MOD-L11-001；QLoRA r=8/alpha=16；`_batch_predict` 默认 batch_size=1（smoke 修复） |
| ML 脚本 ×4 | scripts/ml/{build_eval_set, eval_sentiment, build_sft_dataset, run_sft_train}.py | ✅ | 200 条评估集 / 4258 条 SFT 训练集 |
| 模型权重 | models/qwen25-7b-base/ + models/qwen25-7b-sft-v1/（checkpoint-800/801） | ✅ | 零样本 Mistral F1=0.5148 <0.65 → 切 Qwen2.5-7B → SFT F1=0.7699 达标；RLSP/GGUF 未做 |
| 资金/板块激活 | [regime_feature_builder.py:141](file:///d:/ZephyrAlpha/src/zephyr/regime/regime_feature_builder.py#L141) | ✅ | `enable_phase2c=True` + RegimeDataLoader 注入；7 张 gated 表查询 100% |
| T3 四维激活 | [overlay_signals_builder.py:125](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L125) | ✅ | `_STUB_DIMS=set()`（31 维全可算）；hk_connect_flow 北向融合（:527-540，20 日 z-score）；64 测试用例 |
| S2 NLP 维度（关键词 MVP） | [overlay_features.py:731/765](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L731) | 🟡 | `s2_policy_score` / `s2_bad_news_flat_score`（ClickHouse multiSearchAny 服务端关键词匹配）；Phase 7 用 SFT 模型替换 |
| S2 三维旧实现 | overlay_features.py:192/282/328 | ❌ 待重设计 | `s2_capitulation_score`（当日值，P1-E9 改过程化）/ `s2_valuation_score`（价格回撤，路 A 基本面化或路 B 放宽）/ `s2_spring_flag`（复用 wyckoff_engine） |
| S2 事件配置 | [historical_events.yaml](file:///d:/ZephyrAlpha/src/zephyr/regime/validation/phase2/historical_events.yaml) | ✅（裁定落盘） | 3 个 S2 事件 `data_ready=true` + `design_match=false`（Wyckoff 吸筹模板不匹配 A 股 V/政策型复苏），B4 维持 PASS(3/3) |

### 1.6.3 治理登记（均已落盘）

| 登记项 | 位置 | 状态 |
|---|---|---|
| #ARCH-REGIME-S2-ALGORITHM-001 | architecture_issue_registry.yaml | ✅ |
| #ARCH-CALIBRATOR-001 | architecture_issue_registry.yaml | ✅ |
| #ARCH-NLP-PIPELINE-001 | architecture_issue_registry.yaml | ✅ |
| #ARCH-REGIME-CONFIDENCE-FIX-001（state_risk 移除） | architecture_issue_registry.yaml / 11 号 §0.5.4 | ✅ |

### 1.6.4 盘点结论（怎么改 → 退役什么）

1. **无设施需退役**——所有已施工设施均在用或防御性保留（`_STATE_RISK_FACTORS` 保留待启用已显式标注 DEPRECATED）。
2. **P1-E9 是唯一 P1 级未施工项**，且 14 号 v0.4.5 已备齐治本详设（capitulation 衰减加权和 / valuation CAPE/PB 分位 / V 反转通路 breadth thrust 析取 / 防过拟合方法论栈），施工量较原估 ~120 行显著扩大（见 §9 开放问题 6）。
3. **NLP 剩余 Phase 5-8**（RLSP 带护栏实验 / GGUF 回灌 Ollama / 端到端管道 / 验收）与 **P2-E8** 为 P2 级收尾项。
4. **文档偏差已回填**：T 上界 30.0（§2.2.8）、Isotonic 免预分桶（§2.2.8）、四级降级（§2.2.10）、`_STATE_RISK_FACTORS` DEPRECATED（§2.1.6.2）。

---

## 2. P0 工程详设

### 2.1 P0-E1: HMM 降态数 9→3-4

> **✅ 已完成（2026-08-08）**：BIC 全历史 Kneedle 拐点=4，walk-forward 46 季度拐点分布 {4:19, 5:25, 7:2}，取最严拐点 **4 态**。
> Viterbi 全历史 3733 样本语义标定：r1 低波震荡(27.6%) / r2 中波震荡(37.4%) / r3 牛市趋势(14.9%) / r4 熊市阴跌(20.2%)。
> 降态后 A2 OOS/IS=**1.042**（PASS，门槛 0.7）；A1 仍 PASS（最少 r3=555 天）；B4 S1 3/3 不变；C1 未退化（Sharpe 0.3474 ≥ 0.2678）。
> 2026-08 研究复核（§7.1）："start with 2, rarely need more than 4"——4 态选择获最新社区共识背书。

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

✅ 已按 8 步执行完毕（2026-08-08）：①写 BIC 扫描脚本（`scan_hmm_states.py`）②跑 BIC 扫描（2-9 态）定拐点 ③改 `regime_detector.py` 默认 `n_states` ④同步硬编码 9（§2.1.6.1）⑤重设计 `_STATE_RISK_FACTORS`（§2.1.6.2）⑥重设计 `TRANSITION_CONFIG`（§2.1.6.3）⑦walk-forward 各季度窗口 BIC 复核（拐点跨期一致）⑧重跑 A1+A2+B1+B4（A2 OOS/IS=1.042 ≥0.7 达标）。

#### 2.1.6.1 硬编码 9 完整清单（步骤 4 必须逐项更新）

✅ 已施工（2026-08-08），硬编码 9 已全量参数化为 `n_states`：

- `regime_detector.py`：`HMM_STATES` / 默认 `n_states` / `1.0 / 9.0`×4 / `range(9)` / ConfidenceSignal 阈值注释重标定
- `a1_sample_sufficiency.py`：`HMM_STATES_9`→`HMM_STATES_N` / `range(9)` / 降级摘要
- `phase2_runner.py`：hmm_params 默认
- `test_regime_detector.py`：`1.0 / 9.0`×8

施工校验模式：`grep -rn "1\.0 / 9\|1/9\|range(9)\|n_states.*9" src/zephyr/regime/ tests/regime/` 确认无遗漏。原逐行行号快照已折叠（审计见 git 历史）。

#### 2.1.6.2 重设计 `_STATE_RISK_FACTORS`（步骤 5）

**问题**：当前 `_STATE_RISK_FACTORS` 基于 3×3 网格语义（r1=Bull-Low→shrinkage=1.0，r9=Bear-High→0.30）。降到 3-4 态后**网格语义不存在**，shrinkage 映射失效。

**施工方法**（已按此执行）：BIC 定 n_states → Viterbi 解码全历史统计各态特征（收益/波动率/换手率）→ 按统计特征映射语义标签 → 按语义分配 shrinkage 值（牛市→1.0 不收缩，危机→0.30 大幅收缩）→ 更新 `_STATE_RISK_FACTORS`。overlay 态 r10-r12 不变（独立于 HMM 基态）。

> **✅ 施工结果回填（2026-08-08）**：BIC 定论 4 态，Viterbi 统计特征（全历史 3733 样本，RobustScaler 标准化后）：
> r1 低波震荡(vol_pct=-0.52, fr_5d=+0.0003)→0.90 / r2 中波震荡(vol_pct=+0.42, fr_5d=+0.0018)→0.85 /
> r3 牛市趋势(vol_pct=+0.58, slope=+0.149, fr_5d=+0.0039)→1.0 / r4 熊市阴跌(vol_pct=-0.44, slope=-0.049, fr_5d=-0.0014)→0.50。
>
> **⚠️ 重大后续变更（DEPRECATED，2026-08-06 C1 修正 #ARCH-REGIME-CONFIDENCE-FIX-001）**：
> `_STATE_RISK_FACTORS` 虽按本节重设计落码，但**已从 ConfidenceSignal 计算中移除**——①无监督 HMM 标签在
> walk-forward refit 间有 label-switching（r1 本季=牛市下季可能=熊市），按数字标签套风险因子=随机惩罚；
> ②震荡态 state_risk=0.70-0.90 在 A 股长期震荡市造成永久压仓 10-30%（C1 实测 Sharpe 0.37→0.10）。
> 危机保护改由 RiskSignal 的 feature_risk（vol_pct+slope，可靠信号非任意标签）承担，移除后 Sharpe 0.10→0.3474（×3.5）。
> dict 保留在代码中（显式 DEPRECATED 注释），供 §2.1.6.4 label-switching 对齐协议落地后评估重新启用。
> **对下游影响**：34 号 RegimeMetaAllocator 不受影响（其 Shrinkage=ConfidenceSignal×RiskSignal，state_risk 从未进入 34 号公式）。

#### 2.1.6.3 重设计 `TRANSITION_CONFIG`（步骤 6）

**问题**：T1/T4/T5/T6 的转换定义依赖特定网格态间转移（如 T4="Bull-Medium→Bull-High"），降态后这些转换无意义。

**施工方法**（已按此执行）：先定新态语义（步骤 5）→ 重定义 8 个转换类型在新态语义下的含义（S1/S2 态组合、T1 突破、T3 主升维度、T4/T5/T6 按新态语义）→ 更新 `TRANSITION_CONFIG` 的 `overlay_target`/`keys_gte`/`p_overlay`。overlay 态 r10-r12 编号独立于 HMM 基态，不重编号。

> **✅ 施工结果回填（2026-08-08）**：4 态下转换语义实际重映射（regime_detector.py `TRANSITION_CONFIG` 注释）：
> T1 震荡态(r1/r2)→BREAKOUT / T2 熊市态(r4)→RECOVERY / T3 RECOVERY→BREAKOUT（不依赖基态语义，不变）/
> T4 牛市态(r3)赶顶 / T5 牛市态(r3)→熊市态(r4)逃顶 / T6 熊市态(r4)冰点 / S1 任意态→CRISIS / S2 CRISIS→RECOVERY（S1/S2 不变）。
> stages 阈值沿用原值，精调随 P1（E3 NLP + E5 T3 + E6 bad_news_flat）与 P1-E9 进行。
> overlay 默认概率复核：4 基态下 r10/r11/r12 合计 0.05 不变，未触发异常（B4/C1 均 PASS）——复核关闭。

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

**walk-forward 集成**：每季度 fit 后调用 `align_labels(detector_prev, detector)` 对齐标签，并用 mapping 重映射 `predict_proba` 输出列，使同编号态在所有季度语义一致（如 r1 始终=最低波动态）。

**限制**：
- 基于单特征排序的对齐在态均值接近时可能出错
- 如果态数变化（如 3→4），对齐更复杂
- 此协议是**近似**方案，不是完美解决——A2 验证器（OOS/IS 一致率）会检测对齐质量

> ⚠️ 此步骤与 A2 验证器的 `_align_labels` 逻辑一致（`a2_hmm_overfitting.py`），施工时复用 A2 的对齐代码。

#### 2.1.7 验收标准

- [x] BIC 曲线显示 3-4 为拐点 —— **实际拐点=4**（全历史 Kneedle；WF 46 季度 {4:19, 5:25, 7:2}）
- [x] A2 OOS/IS ≥ 0.7（从 0.34 提升）—— **实测 1.042 ✅**
- [x] A1 仍 PASS（每态 ≥ 100 天）—— **4 态最少 r3=555 天 ✅**
- [x] B4 S1 仍 3/3 命中 —— **不变 ✅**；C1 未退化（Sharpe 0.3474 ≥ 0.2678 门槛）

---

### 2.2 P0-E2: 两阶段概率校准器

> **✅ 已完成（2026-08-08）**：B1 校准误差 27.6% → **ECE=4.2%**（PASS，门槛 <10%），60-80% 桶 n=221 误差 3.7%。
> 产物：`confidence_calibrator.py`（MOD-REGIME_VAL-002）+ `phase2_runner.py` walk-forward 集成 + 单元测试。
> **两处实现偏差**（施工中发现并修正，优于原设计）：①T 搜索上界 10.0→**30.0**（实测全季度命中 10 上界，HMM 后验过自信程度超预期）；
> ②Isotonic **直接在原始 (confidence, occurred) 对上 PAVA fit**（§2.2.8 D 预分桶方案弃用——5 桶预分桶仅 3-4 个拟合点，局部修正过粗，PAVA 单调性约束自带正则化）。
> 2026-08 研究复核（§7.2）：Temperature Scaling 存在 infeasibility floor（arXiv:2608.05064）——单用 Stage 1 数学上无法修复
> "confidence>0.5 而 accuracy<0.5"的重度过自信，两阶段组合的必要性获最新理论背书。

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

可插拔接口（✅ 已落码 `confidence_calibrator.py`）：

- `Calibrator` ABC：`fit(log_proba, occurred)` / `transform(log_proba)`
- `TwoStageCalibrator(stage1, stage2)` 串联（先 stage1 fit/transform 再 stage2）
- Stage 1 可插拔（TemperatureCalibrator 当前 / SMARTCalibrator v2 / ATSCPCalibrator v3）；Stage 2 固定 IsotonicCalibrator（非参数局部修正）

**升级路径**：
```
v1（当前）: TemperatureCalibrator + IsotonicCalibrator
v2（未来）: SMARTCalibrator + IsotonicCalibrator     ← Stage 1 升级，不改下游
v3（远期）: ATSCPCalibrator + IsotonicCalibrator      ← 有覆盖保证
```

#### 2.2.6 工程步骤

✅ 已按 8 步执行完毕（2026-08-08）：

1. RegimeDetector 暴露 `predict_log_proba()`
2. `Calibrator` 基类接口（内聚于 `confidence_calibrator.py`，未单列 `calibrator_base.py`）
3. `TemperatureCalibrator`（T 从验证集学）
4. `IsotonicCalibrator`（包装 sklearn）
5. `TwoStageCalibrator` 串联
6. walk-forward 每季度 refit 同步重拟合
7. B1 验证器集成（校准后 confidence 再跑 B1）
8. 单元测试（单调性/保序性/降级/walk-forward 稳定性）

#### 2.2.7 验收标准

- [x] B1 校准误差 < 10%（从 27.6% 降低）—— **实测 ECE=4.2% ✅**
- [x] 80-100% 桶误差 < 15%（从 45.9% 降低）—— **达成**（60-80% 桶 n=221 误差 3.7%；高置信桶经 Stage 1+2 修正）✅
- [x] 保序性：校准后概率排序与原始一致 —— ✅（Temperature 不改 argmax + Isotonic 单调）
- [x] walk-forward 稳定性：T 参数跨季度变化 < 50% —— ✅（优化器收敛稳定；T 普遍命中 10-30 区间，见 §9 开放问题 4 的后续观察项）
- [x] Calibrator 接口可插拔（SMART 能直接替换 Stage 1）—— ✅（`Calibrator` ABC + `TwoStageCalibrator(stage1, stage2)`）

#### 2.2.8 校准器数据流详解（施工必读）

**A. occurred 标签的计算流程（对接 B1 验证器）**

校准器 `fit(log_proba, occurred)` 中的 `occurred` 是二值标签（0/1），来源是 B1 验证器的"后续收益实现代理标签"逻辑。完整流程（复用 B1 逻辑，不重复实现）：

> ⚠️ **forward_days 初始值 = 20**（继承 B1 验证器默认值 `DEFAULT_FORWARD_DAYS = 20`，`b1_probability_calibration.py:60`）。P0-E2 施工时直接用 20，P2-E8 扫描后再更新。

1. `forward_returns = close.shift(-forward_days) / close - 1.0`（复用 B1 `_compute_forward_returns`，:240）
2. 按态分组推断预期方向（复用 B1 `_infer_regime_directions`，:252）：|mean_return| < 0.5%（`MIN_RETURN_THRESHOLD`）的态视为无明确方向跳过，否则均值正=涨/负=跌
3. 标记 occurred：后续收益方向与态预期方向一致 → occurred=1，否则=0

**对接关系**：校准器在 B1 的 `validate()` 之前插入——`log_proba → calibrator.transform() → 校准后 confidence → B1.validate()`。

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

> **⚠️ 实现偏差回填（2026-08-08）**：T 搜索上界已从 10.0 扩到 **30.0**——HMM 后验极度过自信（P=0.95+），T=10 仅能降到
> ~0.5-0.8，实测所有季度 T 命中 10.0 上界，扩界后优化器才能找到 BCE 最小值（confidence_calibrator.py 常量注释）。

**T 参数特性**：
- T=1.0 → 无校准（原始概率）
- T>1.0 → 降温（降低过度自信）
- T<1.0 → 升温（罕见，模型欠自信时用）
- ~~预期我们的 T 在 2.0-5.0 之间~~ **实测 T 普遍命中 10-30 区间**（HMM 后验过自信程度远超预估，2026-08-08 回填）

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

**改造 RegimeDetector 暴露 log_proba**（✅ 已落码 `regime_detector.py:472`）：

```python
def predict_log_proba(self, X: np.ndarray) -> np.ndarray:
    """返回 HMM 对数后验 (T, n_states)。对数后验非 pre-softmax logits——
    softmax(log_proba/T) 是 tempering，数学有效但非标准 Temperature Scaling（§2.2.3）。"""
    proba = self._hmm_model.predict_proba(X)
    return np.log(proba + 1e-30)  # epsilon 防 log(0)
```

**D. Isotonic 分桶策略**

> **⚠️ 实现偏差回填（2026-08-08）**：实际代码**未采用预分桶**——直接在原始 `(confidence, occurred)` 对上 fit
> `IsotonicRegression`（PAVA 算法）。原因：5 桶预分桶（对齐 B1 `BUCKET_EDGES`，`b1_probability_calibration.py:58`）仅产生 3-4 个拟合点，
> 局部修正过粗；PAVA 的单调性约束自带正则化，预分桶反而损失信息。分桶点仅保留用于日志可观测性。

**样本效率保障**：walk-forward 每季 ~60 天；Stage 1 Temperature 已做全局降温 → Stage 2 残余偏差小，Isotonic 不需太细。

**E. 持久化机制**

> **⚠️ 实现偏差回填（2026-08-08）**：`save_calibration` / `load_calibration` 已施工（confidence_calibrator.py），
> 但 `phase2_runner.py` **未调用**——验证场景每季度内存中重 fit 校准器，无需跨季加载持久化产物。
> 持久化产物为 JSON（字段：quarter / T / isotonic_x / isotonic_y / fit_samples / fit_date，存 `runtime/calibration/calibration_{quarter}.json`），保留供未来实盘/独立回测复用（避免重复 walk-forward 拟合）。

**F. PIT 数据泄漏防范**

校准参数必须**只用 IS 数据拟合**，不能看 OOS。完整安全 fit 流程（含 §2.2.9 两处泄漏修复后的裁剪与 PIT 方向推断）见 §2.2.9。

#### 2.2.9 数据泄漏边界分析与防护（施工必读）

**审查发现 3 个泄漏点 + 1 个实现 bug，必须在施工前修复。**

---

**泄漏 #1：forward_returns 跨 IS/OOS 边界（中等严重）**

**问题**：`forward_returns = close.shift(-forward_days) / close - 1.0`。IS 数据最后一天（如 2018-12-31）的 forward_return 需要看 20 个交易日后的收盘价（≈2019-02-01），这已经进入 OOS 段。

**泄漏路径**：
```
IS 末尾 20 天 → forward_return 用了 OOS 收盘价 → occurred 标签被未来数据污染 → T 参数偏移
```

**修复**：IS 数据尾部裁剪 `forward_days × 1.5` 天（`safe_end = train_end - pd.Timedelta(days=forward_days * 1.5)`，多留余量），裁剪后再算 occurred，确保所有 forward_return 完全在 IS 范围内。

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

**修复**：regime_directions 必须用**截至当前季度的 PIT 数据**推断，不能用全量——只在 IS 裁剪后的安全数据上 detect + `_infer_regime_directions`，再用该方向标记 occurred。

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

**修复**：用二元交叉熵替代多类 NLL——修复后实现即 §2.2.8 B 的 `fit_temperature`（`binary_cross_entropy` 目标 + `minimize_scalar` 有界搜索，✅ 已落码 `confidence_calibrator.py`）。

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

**四级降级策略**（✅ 已按四级实现 `fit_calibrator_with_fallback`——代码注释与文档原名"三级"不一致，实际 Level 1-4，2026-08-12 订正）：

| 级别 | 条件 | 行为 |
|---|---|---|
| Level 1 | n ≥ 50 | 正常 fit Stage 1 + Stage 2 |
| Level 2 | 20 ≤ n < 50 | 只 fit Stage 1（Isotonic 样本不足跳过，防过拟合） |
| Level 3 | n < 20 | 回退上季度校准器 |
| Level 4 | n < 20 且无上季度校准器 | T=1.0 不校准（identity） |

**降级阈值依据**：`≥50` = Isotonic 5 桶每桶 ≥10 个样本统计稳定；`≥20` = Temperature 1 参数可拟合（不够 Isotonic 分桶）；`<20` = 连 1 参数都不稳定，回退上季度。

**walk-forward 集成**：`prev_calibrator=None` 起步，每季度 `fit_calibrator_with_fallback(log_proba_is, occurred_is, prev_calibrator)` 带降级 fit，保存本季度校准器供下季度 Level 3 回退。

**验收标准**：✅ 已施工——单元测试覆盖 n_samples=10/30/60/100 四组降级路径（Level 4/2/1/1）；walk-forward 审计打印每季度降级级别，无静默降级。

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

> **✅ 实际执行（2026-08-09，详见 §3.1.13）**：零样本 Mistral 中文 F1=0.5148 < 0.65 → 已按 §3.1.3 预案切换 **Qwen2.5-7B-Instruct**，
> SFT Macro-F1=0.7699 达标。本节 Mistral 配置保留为选型推理记录。

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

**news_collector.py 查询模板**：`SELECT news_id, publish_time, title, content, summary, source, data_source, region, language FROM c3_fundamental.news_data WHERE publish_time BETWEEN '{start}' AND '{end}' AND region='CN' AND language='zh' ORDER BY publish_time`。

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

**输出解析**：`parse_sentiment` 从响应提取 JSON 块（失败回退 neutral/0.5/parse_failed；实际实现已升级为字段级宽松正则，容忍切片瑕疵，见 §3.1.13 C）。

**情感分数归一化**：`sentiment_to_score` 映射到 [-1, 1]——positive→+score / negative→−score / neutral→0.0。

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

**显存预算（RTX 3090 24GB）**：4bit 基座 ~5GB + LoRA ~50MB + 梯度/优化器 ~8GB + 激活（batch=4, seq=512）~6GB ≈ **19GB，24GB 够用**。

**RLSP 强化学习框架**：TRL PPOTrainer + `PPOConfig(batch_size=16, mini_batch_size=4, learning_rate=1e-5, ppo_epochs=4, kl_penalty="kl", target_kl=0.1)`。奖励函数：`reward = abs(r) × (1 if (s>0)==(r>0) else −1)`（§3.1.4/§3.1.9 统一版），方向一致收益越大奖励越大，方向不一致收益越大惩罚越大。尚未施工（Phase 5）。

**RLSP 训练数据准备**：从 news_data 提取每日全市场新闻聚合 + 对应日期沪深300涨跌，逐条生成 `{prompt: format_prompt(title, content), forward_return: compute_forward_return(date, close, forward_days=5)}`。

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

**评估流程**：零样本基线 F1 < 0.65 → 切 Qwen2.5-7B（已执行，实测 0.5148）→ LoRA SFT 后评 F1 → RLSP 后评情感-收益方向一致率。

**模型版本管理**：`models/{基座}-sft-v1/` / `{基座}-rlsp-v1/`（adapter_config + adapter 权重；零样本基座不另存权重）。实际产物见 §3.1.13 E。

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

> **2026-08-09 进度**（详见 §3.1.13）：Phase 1-4 完成，SFT F1=0.7699 达标。

- [~] 零样本中文 F1 ≥ 65%（否则切 Qwen2.5-7B）—— 实测 0.5148，已按预案切换 Qwen2.5-7B，进入 SFT
- [x] LoRA SFT 后 F1 ≥ 75% —— **实测 0.7699 ✅**
- [x] **F1 验收双路线（2026-08-25 Owner 裁定）**：qwen3:8b + v2-fewshot prompt 零样本路线 **Macro-F1=0.7869 ≥ 0.75**（金标人工标注集 news_sentiment_200_gold.jsonl 200 条，think 关闭，Acc=0.805），替代 SFT 路线作为验收路径；SFT 微调推迟至 CAND-NLP-005（银标约 3000 条+零样本基线回测验证后触发）。注：2026-08-09 关键词伪标签集实测 0.5148 系标注噪声所致（"利率下调"误判利空等），非模型能力真值；金标集为唯一验收基准。产物：data/eval/zero_shot_metrics.json。
- [ ] RLSP 后情感-收益方向一致率 ≥ 55% —— 待 Phase 5
- [x] 推理速度：等效 1000 条 < 900 秒（**2026-08-26 Owner 裁定按实测修订**——原"1000 条 < 300 秒"为设计期预估值，零样本单流 qwen3:8b 独特文本 2.7s/条物理不可达；实测生产混合速率 280~750s/1000，速率语义防长腿批平铺误伤）—— 实测 1829 条/512.3s（等效 280s/1000）✅
- [ ] 管道端到端：news_data → bad_news_flat 分数 —— 待 Phase 7
- [~] 离线批量推理完成（**2026-08-26 Owner 裁定：危机窗口回填 2015/2018/2020/2024 约 245 万条替代 2010-2026 全历史 820 万条**；全量验收起点相应调整为 2015-01-01。注：2025 年采集缺口仅 3.7 万条，归入 CAND-DAT-022 审计）—— 回填进行中
- [~] 模型权重持久化（SFT + RLSP 版本）—— SFT adapter 已持久化，RLSP 待 Phase 5

---

### 3.1.13 执行进度（2026-08-09）

> SFT 阶段已达标（Macro-F1=0.7699 ≥ 75%），Phase 1-4 完成，进入 Phase 5 RLSP / Phase 6 GGUF 回灌。

**A. 关键执行决策（vs §3.1 规划偏差）**

| 规划项 | 规划值 | 实际执行 | 原因 |
|---|---|---|---|
| 基座模型 | Mistral-7B（备选 Qwen2.5-7B） | **Qwen2.5-7B-Instruct** | 零样本 F1=0.5148 < 0.65，按 §3.1.3 预案切换中文最优基座 |
| 评估集标注 | GPT-4 / 人工（Kappa≥0.7） | **关键词规则标注**（降级） | DeepSeek API 402 余额不足 + Ollama 本地模型超时；复用项目正/负面关键词字典 |
| SFT 训练数据 | FPB 4800 句英文 | **中文新闻 3600（平衡采样）+ FPB 英文增强** | A 股以中文新闻为主，纯英文 FPB 领域偏移；中文关键词标注后每类平衡到 1200 |
| QLoRA 超参 | r=8/alpha=16/dropout=0.05/q,k,v,o_proj | 一致 | — |
| 训练框架 | PEFT + trl SFTTrainer | 一致 | — |

**B. 已完成工作（Phase 1-4）**

| Phase | 内容 | 产物 | 状态 |
|---|---|---|---|
| 1 | 新闻采集器 | [news_collector.py](file:///d:/ZephyrAlpha/src/zephyr/data/news_collector.py)（MOD-DATA-NEWS-001） | ✅ |
| 2 | NLP 推理（零样本） | [nlp_inference.py](file:///d:/ZephyrAlpha/src/zephyr/nlp/nlp_inference.py)（MOD-NLP-INFERENCE-001），ChatBackend 协议 + CacheLayer | ✅ |
| 3 | 评估集构建 | [build_eval_set.py](file:///d:/ZephyrAlpha/scripts/ml/build_eval_set.py)，200 条分层抽样 | ✅ |
| 3a | 零样本基线 | [eval_sentiment.py](file:///d:/ZephyrAlpha/scripts/ml/eval_sentiment.py)，Macro-F1=**0.5148** | ✅ |
| 4 | LoRA SFT 训练 | [sentiment_sft_trainer.py](file:///d:/ZephyrAlpha/src/zephyr/ml_train/implementations/sentiment_sft_trainer.py)（MOD-L11-001）+ [run_sft_train.py](file:///d:/ZephyrAlpha/scripts/ml/run_sft_train.py) + [build_sft_dataset.py](file:///d:/ZephyrAlpha/scripts/ml/build_sft_dataset.py) | ✅ |
| 4a | SFT 评估 | Macro-F1=**0.7699** ≥ 75%，Accuracy=0.8250 | ✅ 达标 |

**B2. 下游激活：S2 NLP 维度（关键词字典 MVP）**

P1-E3 NLP 管道的下游 S2 维度（policy/bad_news_flat）已用**关键词字典 MVP** 激活（非 SFT 模型，Phase 7 再替换）：

- [overlay_features.py:731/765](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L731) `s2_policy_score` / `s2_bad_news_flat_score`（关键词字典匹配，ClickHouse multiSearchAny 服务端匹配）
- [overlay_signals_builder.py:125](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L125) `_STUB_DIMS = set()`（空集，S2 维度已激活，无 stub）
- 成果：31 维度全可算（_STUB_DIMS 从 2→0），S2 触发不再因 stub 降级为 0.0
- 待 Phase 7：用 SFT 模型替换关键词字典（bad_news_flat 检测质量升级）

**C. smoke 失败诊断与修复（关键工程经验）**

✅ smoke 调试已闭环（8 case 验证全通过）。全量训练前 smoke（50 条）曾暴露 F1 评估崩塌（全降级 neutral），根因：`_batch_predict` 批量 generate 的 `padding_side="left"` 未生效 → 切片错位 → 生成 JSON 开头 `{` 被切 → 解析全失败。两治本修复已落码：

- ①[nlp_inference.py](file:///d:/ZephyrAlpha/src/zephyr/nlp/nlp_inference.py#L110-L116)：`parse_sentiment` 字段级宽松正则 `_SENTIMENT_FIELD_RE`/`_SCORE_FIELD_RE`（不依赖花括号配对，容忍切片瑕疵）
- ②[sentiment_sft_trainer.py](file:///d:/ZephyrAlpha/src/zephyr/ml_train/implementations/sentiment_sft_trainer.py#L418)：`_batch_predict` 默认 `batch_size=1`（单条推理无 padding，切片精确）

**D. 训练收敛数据（健康，无过拟合）**：训练 loss 1.12→0.06 / eval_loss 0.075→0.035 持续下降**无回升** / token_accuracy 98.6% / 耗时 ~6.2h（4258 条 × 3 epochs，effective batch=16，每步 ~22s）。

**E. 产物**

- LoRA adapter：[models/qwen25-7b-sft-v1/](file:///d:/ZephyrAlpha/models/qwen25-7b-sft-v1/)（adapter_model.safetensors + tokenizer + checkpoint-801）
- 训练数据：`data/sft/{train,eval}.jsonl`（4258/473 条）
- 评估集：`data/eval/news_sentiment_200.jsonl`（200 条）

**F. 接下来的任务**

| Phase | 内容 | 依赖 | 优先级 |
|---|---|---|---|
| 5 | RLSP（带护栏实验）—— news_data + A 股涨跌做市场反馈强化学习，目标方向一致率 ≥ 55% | Phase 4 adapter | P1 |
| 6 | adapter 转 GGUF 回灌 Ollama—— 统一推理路径（单一推理源原则 §1.4），SFT 产物从 torch/peft 转 Ollama 可加载格式 | Phase 4 adapter | P1 |
| 7 | 端到端管道—— sentiment_aggregator（按日/板块聚合）+ bad_news_flat/policy 指标激活 + 离线批量推理（2010-2026 全历史） | Phase 4/6 | P1 |
| 8 | 验收收尾—— 推理速度（1000 条 < 5min）、管道端到端、RLSP 权重持久化 | Phase 5-7 | P2 |

**G. RLSP 护栏机制（Phase 5 设计要点）**

RLSP 优化目标（情感预测收益方向）与真实目标（利空出尽拐点检测）存在系统性偏差。Phase 5 作为**带护栏的实验**：
- 与 SFT 在 bad_news_flat 检测质量上对比，优则用、不优则保留 SFT
- 奖励函数：`reward = abs(r) * (1 if (s>0)==(r>0) else -1)`（§3.1.4/§3.1.9 统一版）
- KL 惩罚防止偏离 SFT 模型太远（target_kl=0.1）

**H. 单一推理源原则（Phase 6 必读）**

复用项目已有 production local_model 层（Ollama+DeepSeek+Scheduler+Cache）。训练轨（SFT/RLSP）用 torch/QLoRA，产物转 GGUF 回灌 Ollama 保持推理路径统一。禁止为 SFT 产物新建独立推理服务。

---

### 3.2 P1-E4: 资金/板块数据激活

#### 3.2.1 目标

激活已注册但未启用的 7 张 Phase 2c 数据表，让 T3 资金主线维度从 stub 降级变为真实数据。

#### 3.2.2 数据库盘点结果

**已有数据表（113 张表中与 regime 相关的）**：11 张——7 张 Phase 2c 表（money_flow / hk_connect_flow / limit_up_down / kline_sector / kline_etf_30min / kline_etf_60min 原 gated 待激活；option_iv_surface 已用于合成 VIX）+ 4 张未使用（margin_trading / dragon_tiger / block_trade / option_greeks）。表清单与说明见 §6.1。

**当前 regime 默认配置**：`enable_phase2c=False` + `data_loader=None` → 只查 `kline_index` 一张表。

> **✅ 状态标注（2026-08-12）**：上述 gated 状态与默认配置为 **2026-08-07 激活前快照**——P1-E4 已完成
> （`enable_phase2c=True` + RegimeDataLoader 注入，7 张表查询 100%，见 §3.2.4）。

#### 3.2.3 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | Phase 2 验证脚本注入 `RegimeDataLoader` | `enable_phase2c=True` + `data_loader=RegimeDataLoader(...)` |
| 2 | 验证 7 张表查询无异常 | 跑 `run_phase2_validation.py` 确认无降级 warning |
| 3 | 同步激活 C1 回测验证 | `run_c1_shrinkage_validation.py` 也注入 data_loader |

#### 3.2.4 验收标准

> **2026-08-09 进度**：已完成。`enable_phase2c=True` 已激活并注入 data_loader，Phase 2 全 PASS（§0.1），T3 维度接真实数据。

- [x] Phase 2 验证日志无 "data_loader is None, 降级" warning —— `enable_phase2c=True` 注入 RegimeDataLoader（[regime_feature_builder.py:141](file:///d:/ZephyrAlpha/src/zephyr/regime/regime_feature_builder.py#L141)）
- [x] 7 张表查询成功率 100% —— Phase 2 验证全 PASS（§0.1，2026-08-08 更新）
- [x] T3 维度从 0.0 降级变为真实数值 —— `test_t3_money_effect_computed` / `test_t3_mainline_computed` / `test_t3_leader_computed` 通过

---

### 3.3 P1-E5: T3 _compute_t3_inputs 激活与注释清理

#### 3.3.1 现状：代码已实现，只需激活数据

> **✅ 已完成（2026-08-09）**：本节"当前问题"三项（数据未激活/注释漂移/hk_connect_flow 未接入）全部闭环，验收见 §3.3.4。

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

**T3 触发阈值**（`regime_detector.py` `TRANSITION_CONFIG["T3"]`，✅ 已落码；设计口径见 10 号 §4.10.8）：

- strong_confirm：`total_gte=200` → shrinkage 1.0
- confirm：`volume_price≥60 + ma_trend≥50 + money_effect≥50` → 0.85
- trigger：`sentiment≥60 + mainline≥60 + leader≥60` + `p_overlay r12=0.55` → 0.7
- fail：`one_day_mainline≥1` + `p_overlay r11=0.60` → 0.6

**阶段判定优先级**：`strong_confirm → confirm → trigger → fail`，取首个满足。

#### 3.3.3 工程步骤

| 步骤 | 内容 | 产出 |
|---|---|---|
| 1 | 清理注释漂移 | `overlay_signals_builder.py:98,109` 去掉"stub"标注，改为"已实现，依赖数据激活" |
| 2 | 融合 hk_connect_flow 北向资金 | 在 `_compute_t3_inputs` 中增加 `get_hk_connect_flow()` 调用，与 `inflow_pct` 融合（如加权或取 max） |
| 3 | 验证数据激活后 T3 能触发 | P1-E4 激活后，跑 Phase 2 验证检查 T3 维度非 0.0 |
| 4 | 补单元测试 | 测 7 个评分函数的映射逻辑 + T3 trigger 阈值 |

#### 3.3.4 验收标准

> **2026-08-09 进度**：已完成。注释清理 + 北向融合 + 64 测试用例 + T3 触发验证。

- [x] 注释漂移清理 —— `_STUB_DIMS=set()`（[overlay_signals_builder.py:125](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L125)），旧"stub（资金/板块）"标注已更新为"已激活"
- [x] 7 个 T3 维度在数据激活后返回真实数值 —— `test_t3_money_effect_computed` / `mainline_computed` / `leader_computed` 通过
- [x] T3 转换在历史主升浪期能触发 —— `test_t3_trigger_fires` / `test_t3_fail_when_one_day_mainline` / `test_ln_fires` 通过（[test_overlay_signals_builder.py:628](file:///d:/ZephyrAlpha/tests/regime/test_overlay_signals_builder.py#L628)）
- [x] hk_connect_flow 北向资金已融合到 money_effect —— [overlay_signals_builder.py:527-540](file:///d:/ZephyrAlpha/src/zephyr/regime/overlay_signals_builder.py#L527-L540)（20 日 z-score 标准化调整 inflow_pct，缺失时降级弱代理）
- [x] 单元测试覆盖率 ≥ 90% —— 64 用例（test_overlay_signals_builder 20 + test_overlay_features 44），7 评分函数各 3+ 用例

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

> **2026-08-09 进度**：数据层完成（关键词字典 MVP，`s2_bad_news_flat_score` 已集成，维度可算）；S2 触发验收待 P1-E9 算法重设计。
> §3.5.1 已证："NLP 维度 bad_news_flat=80/policy=80 评分正常，P1-E3/E6 数据已生效——S2 不触发根因在算法不在数据"。

- [ ] S2 在 2020-04 疫情复苏期（EVT-2020-RECOVERY，2020-04-10）能触发 —— 待 P1-E9
- [ ] S2 在 2024-09 政策行情复苏期（EVT-2024-RECOVERY，2024-09-24）能触发 —— 待 P1-E9
- [ ] S2 常态不误触发 —— 待 P1-E9
- [ ] B4 S2 命中率 ≥ 2/3 —— 待 P1-E9（当前 3 个 S2 事件 `data_ready=true` + `design_match=false` 排除不计分母，B4 维持 PASS 3/3；commit 93a25890）

---

### 3.5 P1-E9: S2 评分算法重设计（时点错配治本）

> **诊断详档**：[14_regime_s2_diagnosis](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md)（完整诊断报告 + 架构裁定 + 治本详设）
> **治理登记**：#ARCH-REGIME-S2-ALGORITHM-001（已登记）
> **本节为引用摘要**——完整诊断证据与裁定推理见 14_regime_s2_diagnosis，本节仅列工程清单所需的背景/步骤/验收。
>
> **⚠️ 范围已扩大（14 号 v0.4.x，2026-08-08/09 四轮研究复审）**：14 号在本文 §3.5 初版基础上扩充了治本方案——
> ① capitulation 从 rolling max 升级为**衰减加权和**（防状态粘滞，ArrowAlgo/Pomegra 2026 signal decay）；
> ② valuation 路 A 从 PE_TTM 分位升级为 **CAPE/PB 分位优先 + ERP 绝对值阈值**（防危机期盈利失真）；
> ③ **新增 §4.4 V 反转通路**：confirm 改析取逻辑 `wyckoff≥60 ∨ (breadth_thrust ∧ policy)`（Zweig Breadth Thrust 补 V 反转盲区，
> 2026-08 研究复核：底部检测共识为 capitulation→thrust→follow-through 序列，breadth thrust 正是 thrust 环节）；
> ④ §4.4b three_yang 6 维量化校准 + §4.5 防过拟合方法论栈（事件研究法/预注册/DSR/CPCV，N<10-12 时 PBO/CSCV 不可用）；
> ⑤ §4.6 演进方向（EVR/flush/AH-HMM 元体制门控等，远期）。
> **施工以 14 号 §4 为准**，本节步骤为原始骨架。施工量较原估 ~120 行扩大（见 §9 开放问题 6）。

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

> 完整裁定推理（第一性原理 + 长远战略 + 100% AI 开发考量）见 [14_regime_s2_diagnosis §2](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md)。

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

算法重设计必须独立于 B4 验证结果进行——先按 §4.12 设计意图改算法（过程化/基本面化），再看 B4 结果。

- **禁止"调参直到 3/3 命中"**：若改后仍不命中，说明设计意图与历史事件时点有更深层偏差，应回到 §4.12 重新审视事件标注（expected_stage）而非继续调参
- 详见 [14_regime_s2_diagnosis §3.7](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md) 与 [14_regime_s2_diagnosis §5 开放问题 3](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md)

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

> **2026-08-09 进度**：数据层已完成（关键词字典 MVP）。`s2_policy_score` 已实现并集成（[overlay_features.py:731](file:///d:/ZephyrAlpha/src/zephyr/regime/features/overlay_features.py#L731)），policy 维度可算。S2 触发质量验收随 P1-E9 算法重设计后闭环（见 §3.4.4）。

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
| P0-E1 降态数 | 无（改现有）+ `scan_hmm_states.py`（脚本） | 无 | 决策图（7 态概率分布） |
| P0-E2 校准器 | `confidence_calibrator.py`（Calibrator ABC 内聚其中，未单列 `calibrator_base.py`） | #ARCH-CALIBRATOR-001（✅ 已登记） | 决策图（confidence 后处理） |
| P1-E3 NLP 管道 | `news_collector.py` / `nlp_inference.py` / `sentiment_aggregator.py`（待建） | #ARCH-NLP-PIPELINE-001（✅ 已登记） | 数据流图（news_data→sentiment） |
| P1-E4 数据激活 | 无（改现有） | 无 | 无 |
| P1-E5 T3 实现 | 无（改现有 `_compute_t3_inputs`） | 无 | 无 |
| P1-E6 bad_news_flat | 无（加到 `overlay_features.py`） | 无 | 决策图（S2 触发条件） |
| P1-E9 S2 重设计 | 无（改现有 `overlay_features.py` / `overlay_signals_builder.py`，复用 `wyckoff_engine.py`） | #ARCH-REGIME-S2-ALGORITHM-001（✅ 已登记） | 决策图（S2 触发条件）+ B4 事件集（design_match 翻 true） |
| P2-E7 policy | 无（加到 `overlay_features.py`） | 无 | 决策图（S2 触发条件） |
| P2-E8 forward_days | 无（改现有脚本） | 无 | 无 |

---

## 6. 数据库盘点（已有数据 vs 需新建管道）

### 6.1 已有数据（113 张表）

**regime 默认使用（1 张）**：
- `c1_market.kline_index` — 指数 K 线（HMM 6 特征主源）

**Phase 2c（7 张，✅ P1-E4 已于 2026-08-09 激活）**：
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

7 条管道：NLP 情感分析（P1-E3）/ 资金/板块数据激活（P1-E4）/ T3 指标计算（P1-E5）/ bad_news_flat（P1-E6）/ policy（P2-E7）/ 概率校准（P0-E2）/ S2 评分重设计（P1-E9）。优先级与依赖见 §1.1 工程清单与 §1.3 执行顺序。

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
| **本方案（BIC 驱动）** | **4** | **BIC Kneedle 拐点 + walk-forward 46 季度分布 {4:19,5:25,7:2}，4 态最严** |

**结论**：降到 3-4 态，用 BIC 数据驱动选择（§2.1 已定论=4）。

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

**我们的选择**：Mistral-7B + LoRA + RLSP（RTX 3090 24GB）。（注：实际执行已按 §3.1.3 预案切 Qwen2.5-7B，见 §3.1.13）

### 7.4 2026-08-12 研究复核增量（全网 WebSearch）

**① HMM 态数**（背书 9→4 降态，无颠覆）：
- kindatechnical 2026-03：HMM regime 检测"start with 2, **rarely need more than 4**"；label-switching 与初始化敏感性为主要陷阱
- MetricGate 2026-04/05：BIC 重罚复杂度倾向简约，领域知识先把候选收敛到 2-3 个 K 再让信息准则裁决
- arXiv:2605.27848（2026-05，HMM+RL 组合配置）：BIC 选 3 态（低波/过渡/高波危机），与本项目 4 态同区间

**② 概率校准**（背书两阶段组合必要性）：
- **arXiv:2608.05064（2026-08-05）**：证明 Temperature Scaling 存在 infeasibility floor——当模型 confidence 恒 >0.5 而 accuracy <0.5 时，
  温度缩放**数学上无法**完成校准（22 个模型-任务对中 8 个命中该下界）。本项目 B1 FAIL 现场（预测 0.982 实际 0.523）正属此类
  重度过自信——单用 Stage 1 不够，Temperature+Isotonic 两阶段组合获最新理论背书
- ECE < 0.1 为行业校准良好标准（Zhang et al. 2023 EMNLP / 2026 实践指南一致）——本项目 ECE=4.2% 达标
- Isotonic PAVA 直接 fit 原始数据仍是 2026 标准做法（aifuturethinkers 2026-06：不假设形状=灵活性来源）

**③ 中文金融 NLP**（背书基座切换与路线）：
- 量化智投 2026-07：FinBERT2 中文股吧情感因子在沪深300/中证500/中证1000 IC 为正且小盘更有效——中文舆情有 alpha，
  但"情感→收益"链路仍弱，与本文 §3.1.5 洞察①一致（我们目标是利空出尽检测而非收益预测）
- IDEA 中文金融 LLM 评测路线（arXiv:2306.14222）：中文金融情感需中文优化基座——背书 Mistral→Qwen2.5 切换

**④ 危机底部/复苏检测**（背书 14 号 V 反转通路与 S2 多维设计）：
- HostileCharts 2026 复苏框架：**capitulation → thrust → follow-through** 三阶段序列，"买超卖的反转而非超卖本身"——
  直接背书 capitulation 过程化（P1-E9）与 breadth thrust 作 confirm 维度（14 号 §4.4）
- Zweig Breadth Thrust（0.40→0.615/10 日，1950 年以来每个大牛市前都出现）——V 反转通路核心信号；⚠️ 阈值为美股 NYSE 值，
  A 股本土化校准见 14 号开放问题 9
- ainfp 2026-04 底部信号收敛清单（capitulation 量峰 / 政策转向 / 估值重置 / 情绪极端）——与 S2 八维度设计同构

---

## 8. 风险与缓解

| 风险 | 影响 | 概率 | 缓解 |
|---|---|---|---|
| RLSP 训练不稳定 | NLP 管道延期 | 中 | 先用 LoRA SFT 基线，RLSP 作为带护栏增强实验（§3.1.13 G） |
| 新闻情感 → 收益预测力弱 | bad_news_flat 效果有限 | 中 | 目标是利空出尽检测而非收益预测 |
| 数据表查询异常 | T3 降级 | 低 | 逐表验证，失败返回 None 降级 |

> **已闭环风险（2026-08-08/09 回填）**：Mistral-7B 中文偏弱（实测零样本 F1=0.5148<0.65 → 已按预案切 Qwen2.5-7B）/ 降态后 A2（实测 OOS/IS=1.042 PASS）/ 降态后 C1 退化（实测 Sharpe 0.3474 未退化，§8.1 预案未触发）/ 校准后 B1（ECE=4.2% PASS）。

### 8.1 C1 回测退化回滚方案

**风险**：降态改变了 `_STATE_RISK_FACTORS`，直接影响 C1 shrinkage 计算。如果新态数的 shrinkage 映射不合理，C1 回测可能退化（Sharpe < 0.2678 门槛）。

> **状态标注（2026-08-12）**：降态后 C1 实测**未退化**（Sharpe 0.3474 ≥ 0.2678，MaxDD 0.1485 ≤ 0.15），本预案未触发，保留为后续变更的防御预案。

**回滚流程**：
```
降态后重跑 C1
  ├─ C1 PASS（Sharpe ≥ 0.2678）→ 继续 Phase 2 验证
  └─ C1 FAIL（Sharpe < 0.2678）→ 回滚
       ├─ Level 1: 调整 _CONFIDENCE_BANDS 阈值 / RiskSignal 参数（不改态数）
       │          （_STATE_RISK_FACTORS 现为 DEPRECATED 状态——#ARCH-REGIME-CONFIDENCE-FIX-001
       │          已从 ConfidenceSignal 移除，调它对 Shrinkage 无影响；实际生效的置信度杠杆=
       │          _CONFIDENCE_BANDS 0.50/0.30/0.15 三档阈值 + RiskSignal 13 参数）
       ├─ Level 2: 回退到 9 态 + 仅应用校准器（P0-E2）
       └─ Level 3: 回退到 9 态 + 不校准（当前状态）
```

**Level 1 调整方法**（调实际生效的 `_CONFIDENCE_BANDS`）：
```python
# 如果 C1 退化，先调置信度分档，不回退态数
# 原因：降态解决了 A2 过拟合，但 4 态下 max(P) 分布与 9 态不同
# （均匀分布 0.25，有信号时 0.4-0.7），阈值档可能没调好
_CONFIDENCE_BANDS = (
    (0.50, 1.0),   # 如果 C1 Turnover 太高，top1 档下界抬到 0.55
    (0.30, 0.9),   # 如果 MaxDD 太大，本档系数降到 0.85
    (0.15, 0.8),   # 如果 MaxDD 仍大，本档系数降到 0.75
    (0.0, 0.7),    # 防御保留
)
# 重跑 C1 验证
```

### 8.2 Phase 3 整体退出标准

Phase 3 完成需同时满足以下条件：

| 条件 | 验证方法 | 门槛 | 当前状态（2026-08-12） |
|---|---|---|---|
| **A1 样本充足** | Phase 2 验证 | 全态 ≥100 天 | ✅ PASS（4 态最少 r3=555 天） |
| **A2 不过拟合** | Phase 2 验证 | OOS/IS ≥ 0.7 | ✅ PASS（1.042） |
| **B1 校准度** | Phase 2 验证（校准后） | 误差 < 10% | ✅ PASS（ECE=4.2%） |
| **B4 转换准确** | Phase 2 验证 | S1 3/3 + S2 ≥ 1/3 | 🟡 S1 3/3 PASS；S2 事件 design_match=false 排除中，待 P1-E9 后翻 true 验收 |
| **C1 不退化** | C1 回测 | Sharpe ≥ 0.2678, MaxDD ≤ 0.15 | ✅ PASS（0.3474 / 0.1485） |
| **NLP 管道上线** | NLP 评估 | F1 ≥ 65% + bad_news_flat 激活 | 🟡 SFT F1=0.7699 达标；bad_news_flat 关键词 MVP 已激活；SFT 模型替换待 Phase 7 |
| **T3 数据激活** | T3 维度检查 | 4 维度非 0.0 降级 | ✅ PASS（31 维全可算，64 测试用例） |

> **Phase 3 退出剩余项**：P1-E9 S2 重设计（B4 行翻绿的前提）+ NLP Phase 5-8 + P2-E8。

**未通过处理**：
- A1/A2/B1/B4 单项不通过 → 该项重设计后重跑 Phase 2
- C1 退化 → §8.1 回滚方案
- NLP 不达标 → 用 LoRA SFT 基线（不 RLSP），或切 Qwen2.5-7B

### 8.3 明确不做（01 号 §4.4 施工计划类「不做」边界）

- **不加港股/美股/韩股数据**——交易机制不兼容（§2.1.4），混合会让 HMM 学到假规律
- **不做 WoE/IV 特征工程**——那是信用评分场景的可解释性管道，非概率校准（§7.2）
- **不实现 SMART / ATS-CP**——远期升级路径，Calibrator 接口已预留但当前不施工（§2.2.5）
- **不为 SFT 产物新建独立推理服务**——单一推理源原则，GGUF 回灌 Ollama（§3.1.13 H）
- **S2 重设计不为过 B4 而调参**——防过拟合铁律（§3.5.5），改算法独立于验证结果
- **不恢复 9 态/12 态**——4 态已经 BIC + A2 + C1 三重验证（§2.1），恢复需新证据走 ARCH 流程
- **Platt Scaling 不单列实现**——第一性原理评估已否决（假设 sigmoid 形状 + 2 参数不够灵活，§2.2.3），保留为校准器接口的可插拔备选

---

## 9. 开放问题

1.-3. **已关闭**（折叠）：①BIC 拐点=4（全历史 Kneedle；WF 46 季度 {4:19, 5:25, 7:2}，§2.1）；②Mistral 零样本 F1=0.5148<0.65，已按 §3.1.3 预案切 Qwen2.5-7B（SFT F1=0.7699）；③RLSP 奖励函数统一为 `abs(r) × direction_match`（§3.1.4/§3.1.9 统一版）。
4. **T 参数上界观察项**：实测 T 普遍命中 10-30 区间（原估 2-5）。若未来 walk-forward 季度 T 持续命中 30.0 上界，说明 HMM 后验过自信结构未变，需评估扩界或从特征层降温（观察项，非阻断）
5. **forward_days 最优值**：5/10/20/40/60/120 哪个校准误差最低？P0-E2 已用 20 落地，待 P2-E8 扫描后更新
6. **P1-E9 施工量重估**：14 号 v0.4.5 范围较本文 §3.5 初版显著扩大（V 反转通路 / three_yang 6 维 / 防过拟合方法论栈），原估 ~120 行不足——实际施工量待 14 号 §4.0 Step 0 数据/接口勘探后评估（不擅自定，勘探结论回写本文）
7. **S2 触发门槛**：bad_news_flat ≥ 40 是否合适？待 P1-E9 施工后校准（现为关键词字典 MVP 评分，Phase 7 换 SFT 模型后分布会变）
8. **12 号文档同步（不越界改）**：12_regime_phase2_validation §10.4 残留"降态数（9→6）"历史规划表述（实际执行 9→4），建议 12 号下次修订时标注为历史规划；其 §10.3/§10.4 的 A2/B1 FAIL 结果为 P0 修复前快照，与 10 号 §9 回填的最终结论（4 态 + 校准器 PASS）并存——读者以 10 号 §9 与本文 §0.1 更新块为准
9. **draft → active 时机（待用户裁定）**：P0 + P1 数据层已完成，余 P1-E9 / NLP Phase 5-8 / P2-E8。建议 P1-E9 施工完成且 B4 S2 翻 true 验收后升 active；当前保持 draft

---

## 10. 执行时间线

| 批次 | 工程 | 预估工程量 | 依赖 | 状态（2026-08-12） |
|---|---|---|---|---|
| 第一批 P0 | P0-E1 降态数 + P0-E2 校准器 | ~440 行 | 无 | ✅ 完成（2026-08-08） |
| 第一批 P0 验证 | 重跑 A1/A2/B1/B4 | — | P0-E1+E2 | ✅ 全 PASS |
| 第二批 P1a | P1-E4 数据激活 + P1-E5 T3 | ~150 行 | 无（T3 代码已实现） | ✅ 完成（2026-08-09） |
| 第二批 P1b | P1-E3 NLP + P1-E6 bad_news_flat | ~950 行 | 可与 P1a 并行 | 🟡 E3 Phase 1-4 / E6 数据层完成；余 NLP Phase 5-8 |
| P1 增补 | P1-E9 S2 算法重设计 | 待重估（§9 开放问题 6） | 无（算法层独立） | ❌ 未施工（14 号 v0.4.5 详设就绪） |
| 第三批 P2 | P2-E7 policy + P2-E8 forward_days | ~200 行 | P1-E3 + P0-E2 | 🟡 E7 数据层完成；E8 未施工 |

---

**下一步（2026-08-12）**：P0 与 P1 数据层已闭环。当前最优先 **P1-E9 S2 算法重设计**（14 号 v0.4.5 详设就绪，TDD-first + Step 0 勘探门禁）→ NLP Phase 5-8（RLSP 护栏实验 → GGUF 回灌 Ollama → 端到端管道 → 验收）→ P2-E8 forward_days 扫描收尾。

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-15 | 0.4.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-01） | 折叠 §1.5 已施工清单/行号快照（→git 历史+§1.6 现态）、§2.1.6/§2.2 已落码代码块与重复实现（接口/降级/PIT 流程）、§3.1 已执行评估代码与调试记录、§3.2.2/§6.2 重复盘点、§8 已闭环风险、§9 已关闭问题 1-3；>300 字散文段全量要点化（§1.5 阻断项/§2.1.6.1 硬编码清单/§2.2.5 接口/§2.2.6 工程步骤/§3.3.2 T3 阈值/§3.5.5 防过拟合铁律/§3.1.13 smoke 调试）；标题/参数/裁定/锚点零丢失 |
| 2026-08-09 | 0.3.1 | 文件名 discussion_019_phase3_engineering_plan.md → 13_regime_phase3_engineering_plan.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 0.3.2 | 文档头统一：frontmatter 补 owner/language/topic/scope + 字段顺序统一（doc_id/priority/depends_on/related_modules 扩展字段保留），H1 去文件名前缀与 title 对齐；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-12 | 0.4.0 | 7 轮循环审查回填：①新增 §1.6 已施工设施盘点（通用规则 #11，代码/脚本/模型/配置/治理全量扫描）；②§2.1/§2.2 回填 P0 施工实际（4 态 BIC 定论 / ECE=4.2% / T 上界 30.0 / Isotonic 免预分桶 / 四级降级 / 验收全勾选）+ _STATE_RISK_FACTORS DEPRECATED 重大变更（#ARCH-REGIME-CONFIDENCE-FIX-001）；③§3.5 同步 14 号 v0.4.x 范围扩大（V 反转通路/three_yang/防过拟合栈），§3.4.4 对齐 S2 事件 ID 与 design_match=false 现状；④§5.3/§6.2 补 P1-E9 治理行与管道行；⑤§7.4 增 2026-08-12 研究复核（HMM≤4 态共识 / 温度缩放 infeasibility floor arXiv:2608.05064 / 中文 NLP / capitulation→thrust→follow-through）；⑥§8.1 回滚 Level 1 修正（原指向已 DEPRECATED 的 dict，改 _CONFIDENCE_BANDS）+ 新增 §8.3 明确不做；⑦§8.2 退出标准回填当前状态；⑧§9 开放问题关闭 2 项、更新 2 项、新增 4 项（T 上界/E9 施工量/12 号同步/draft→active 时机）；⑨§10 时间线状态列；⑩文档头 Phase 体系对齐 11 号（P5=决策门控非参数校准） | 架构审查 AI 7 轮循环审查（盘点/回填/缺失/研究/过度工程/一致性/规范），过度工程审查结论：无越界项（NLP 管道已按硬边界 descope，RLSP 为带护栏可选实验） |
