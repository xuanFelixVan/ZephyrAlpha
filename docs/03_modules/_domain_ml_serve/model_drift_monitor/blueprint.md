---
blueprint_id: MOD-MLS-001
module_name: model_drift_monitor
domain: D_ML_SERVE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ML_SERVE
path: src/zephyr/ml_serve/core/model_drift_monitor.py
granularity: file
---

# MOD-MLS-001 model_drift_monitor 蓝图（D-ML-SERVE MS-03 E-OP-02 漂移检测）

> **module_id**: MOD-MLS-001 | **域**: D_ML_SERVE | **优先级**: P1
> **来源**: B4-06990（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-MLS-001，D-ML-SERVE §0/§1 MS-03）
> 代码：`src/zephyr/ml_serve/core/model_drift_monitor.py`

## 0. 定位

推理域（Warm 平面）**MS-03 DriftMonitor**：serving 模型四维漂移检测
（PSI 输入特征 / JS 散度输出分布 / 性能衰减 / IC 衰减）+ **E-OP-02
ModelDriftDetected 域事件**生产（model_id, drift_type, drift_score,
threshold, detected_at），经 event_sink 外发（INV-019 Warm→Cold 异步
语义，sink DI 注入）。

查重裁定（W-P1-25 铁律④：域级泛条目，细读 TSV 论证独立缺口）：

| min_build_spec 条目 | 场内现状 | 裁定 |
|---|---|---|
| 模型生命周期管理（active版本唯一+approval_ts不变量） | **MOD-ML-012 model_version_registry 已建**（W-P1-21，D_ML_TRAIN；TRAINED→…→ACTIVATED 阶段机+单激活约束+approved_by 人工闸门+activated_at 时间戳） | 重复，不重建（设计边分工） |
| 影子验证门禁（INV-011） | **MOD-ML-012 已建**（仅 SHADOW_VERIFIED→ACTIVATED）+ MOD-ML-004 影子部署器 | 重复，不重建 |
| LLM 网关 | **MOD-INF-051 llm_runtime_gateway 已建**（D_INTEGRATION，五级降级+预算门） | 重复，不重建 |
| **E-OP-02 漂移检测** | **全仓无 ModelDriftDetected 生产者**（grep E-OP-02 仅文档）；ml_serve 包 DORMANT 空壳 | **独立缺口→施工本件** |

| 相近既有件 | module_id | 与本模块边界 |
|---|---|---|
| distribution_drift_monitor | MOD-FBL-001（W-P1-24） | 因子/标签**分布三路**事前预警（语义响应 ALERT/DEGRADE/RETRAIN，不产域事件）；本件=**serving 模型四维**漂移→E-OP-02 域事件（model_id 键），域与产出物均不同 |
| concept_drift 等 drift 族 stub | MOD-FEEDBACK_LOOP | R4x 阈值桩，非模型 serving 面 |
| C-007 IC 衰减 | D_FACTOR | 因子绩效事后监控；本件=模型推理面四维含 IC 维但按 model_id 聚合产事件 |

## 1. 规则（确定性，纯 numpy 内存计算）

- **四维度量**（reference vs current 一维/配对样本）：
  - `psi(reference, current, buckets=10)`：输入特征漂移（分位分箱
    Σ(a%−e%)·ln(a%/e%)，比例裁剪 eps=1e-4）。
  - `js_divergence(reference, current, buckets=10)`：输出分布漂移
    （JSD=0.5·KL(p‖m)+0.5·KL(q‖m)，m=0.5(p+q)，自然对数）。
  - `performance_decay(reference_metric, current_metric)`：
    （ref−cur)/|ref|（|ref|<eps → 按绝对差口径留痕）。
  - `ic_decay(reference_ic, current_ic)`：同性能衰减口径（概念漂移）。
- **四维独立阈值** DriftThresholds（psi/performance/js/ic 各持
  warn/critical，默认对齐域文档 §7.1：psi warn=0.15/crit=0.25，
  performance warn=0.05/crit=0.10，js warn=0.10/crit=0.20，
  ic warn=0.30/crit=0.50）。
- **事件**：任一维越 warn → 产 ModelDriftEvent（event_id=E-OP-02/
  model_id/drift_type(PSI|PERFORMANCE|JS|IC)/drift_score/threshold/
  severity/detected_at(注入时钟)）；越 critical → severity=critical。
  事件经 `event_sink` 回调外发；sink 异常不阻断判定（log+计数）。
- **逐模型聚合**：`evaluate(model_id, ...)` 返回 DriftEvaluation
  （四维 metric_values + events 元组，确定性顺序 PSI→PERFORMANCE→JS→IC）。
- Fail-Closed：空 model_id/样本空/非有限值/阈值非正 → ModelDriftError；
  同输入必同输出。

## 2. 接口

```python
class DriftType(str, Enum): PSI/PERFORMANCE/JS/IC
class DriftSeverity(str, Enum): NONE/WARN/CRITICAL
@dataclass(frozen=True) class DriftThresholds: psi_warn/psi_critical/js_warn/js_critical/perf_warn/perf_critical/ic_warn/ic_critical
@dataclass(frozen=True) class ModelDriftEvent: event_id/model_id/drift_type/drift_score/threshold/severity/detected_at
@dataclass(frozen=True) class DriftEvaluation: model_id/metric_values/events

psi(reference, current, buckets=10) -> float
js_divergence(reference, current, buckets=10) -> float
class ModelDriftMonitor:
    __init__(*, thresholds=DriftThresholds(), clock=None, event_sink=None)
    evaluate(model_id, *, feature_ref, feature_cur, output_ref, output_cur, perf_ref, perf_cur, ic_ref, ic_cur) -> DriftEvaluation
ModelDriftError(ZephyrBaseError)  # 占位 ZA-MLS-UNREGISTERED-MODEL-DRIFT（纪律⑦）
```

## 3. 依赖

- 设计边：`model_version_registry`（node 10631554，生命周期/INV-011 分工）、
  `distribution_drift_monitor`（node 10631563，因子分布三路 vs 模型四维分工）。
- 运行时装配（非本件）：推理时特征/输出样本供给（MS-02）、事件总线
  sink 绑定（D-OPS/MT-05/F09 消费方）、阈值入 config。

## 4. 测试

`tests/ml_serve/test_model_drift_monitor.py`（[TTL] permanent）。
