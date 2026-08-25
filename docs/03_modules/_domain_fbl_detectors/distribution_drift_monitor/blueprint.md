---
blueprint_id: MOD-FBL-001
module_name: distribution_drift_monitor
domain: D_FBL_DETECTORS
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_FBL_DETECTORS
path: src/zephyr/feedback_loop/detectors/drift/distribution_drift_monitor.py
granularity: file
---

# MOD-FBL-001 distribution_drift_monitor 蓝图（§29.5 特征漂移与概念漂移检测）

> **module_id**: MOD-FBL-001 | **域**: D_FBL_DETECTORS | **优先级**: P1
> **来源**: B10-01824（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-FBLDETEC-001，A1交易决策架构 §29.5）
> 代码：`src/zephyr/feedback_loop/detectors/drift/distribution_drift_monitor.py`

## 0. 定位

特征漂移（feature drift）+ 概念漂移（concept drift）+ 标签漂移（label drift）
**三路独立阈值**检测（PSI / KL / MDD 三度量）+ **差异化响应矩阵**
（降级 / 重训 / 告警）的**事前预警**件。

查重分工（W-P1-24 铁律②探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| concept_drift | MOD-FEEDBACK_LOOP | R42 EMA 基线漂移 stub（check 恒返 0.0） | 本件=三路 PSI/KL/MDD 分布度量+响应矩阵，非 stub 扩展 |
| ensemble_drift | MOD-FEEDBACK_LOOP | R43 集成一致率漂移 stub | 集成度口径，非特征/标签分布 |
| config_drift 等 drift 族 | MOD-FEEDBACK_LOOP | 配置/上下文污染/中毒等专项 stub | 均非特征/概念/标签三路分布漂移 |
| C-007 IC 衰减（factor ic_decay） | MOD-L02-001 族 | 因子 IC 衰减**事后**绩效监控 | **职责切分写入契约**：本件=事前分布漂移预警（模型输入/输出分布），C-007=事后因子绩效衰减；本件不消费 IC 序列 |
| correlation_drift_monitor | D_FACTOR | 因子相关性漂移（PSI 用于相关矩阵） | 相关性结构口径，非特征分布 |

TSV 裁定原文："已有概念漂移检测器族（偏事后），缺特征漂移检测与三漂移
事前预警独立响应矩阵"——施工形态=扩展 drift 检测器族 1 个新模块。

## 1. 规则（确定性，纯 numpy 内存计算）

- **三度量**（全部闭式确定性，reference vs current 一维样本）：
  - `psi(reference, current, buckets=10)`：总体稳定性指数，分位分箱
    Σ(a%−e%)·ln(a%/e%)（比例裁剪 eps=1e-4 防 0 除）。
  - `kl_divergence(reference, current, buckets=10)`：同分箱直方图
    Σp·ln(p/q)（裁剪同上，自然对数 nats）。
  - `mdd(reference, current)`：均值差异距离（线性核 MMD² 口径）
    =‖μ_ref−μ_cur‖₂，标准化到 reference 标准差量纲（σ=0 → 原量纲）。
- **三路独立阈值**：ChannelThresholds(feature/concept/label 各持
  psi_warn/psi_critical + kl_warn/kl_critical + mdd_warn/mdd_critical)；
  任一度量越 warn → drift_detected；越 critical → severity=critical。
- **差异化响应矩阵**（ResponseMatrix，可配置覆盖默认）：
  - feature：warn→ALERT，critical→DEGRADE（特征降级/降权）
  - concept：warn→ALERT，critical→RETRAIN（触发重训）
  - label：warn→ALERT，critical→RETRAIN（标签分布变更触发重训）
- **输出** DriftReport：channel/metric_values{psi,kl,mdd}/drift_detected/
  severity(none|warn|critical)/response/n_detail。
- Fail-Closed：样本为空/长度不足 min_samples/含非有限值/阈值非正 →
  DistributionDriftError；分箱数 <2 → 同上。
- 与 C-007 切分契约：本件接口只接受**分布样本**（特征值/预测值/标签值
  序列），不接受 IC/绩效时间序列；响应只产**语义信号**（不直接执行降级/
  重训，执行归运行时装配）。

## 2. 接口

```python
class DriftChannel(str, Enum): FEATURE/CONCEPT/LABEL
class DriftSeverity(str, Enum): NONE/WARN/CRITICAL
class DriftResponse(str, Enum): NONE/ALERT/DEGRADE/RETRAIN
@dataclass(frozen=True) class ChannelThresholds: psi_warn/psi_critical/kl_warn/kl_critical/mdd_warn/mdd_critical
@dataclass(frozen=True) class DriftReport: channel/metric_values/drift_detected/severity/response/detail

psi(reference, current, buckets=10) -> float
kl_divergence(reference, current, buckets=10) -> float
mdd(reference, current) -> float

class DistributionDriftMonitor:  # thresholds: dict[DriftChannel, ChannelThresholds] 注入（缺省用默认）
    check(channel, reference, current) -> DriftReport
    check_feature/check_concept/check_label(reference, current) -> DriftReport
    response_matrix: dict[(DriftChannel, DriftSeverity) -> DriftResponse]
class DistributionDriftError(Exception): 占位 ZA-FBL-UNREGISTERED-DRIFT-MONITOR
```

## 3. 错误契约

- `DistributionDriftError`（未登记错误码-申请中，占位
  ZA-FBL-UNREGISTERED-DRIFT-MONITOR，建议号段见 W-P1-24 fragment）

## 4. 测试

- `tests/drift/test_distribution_drift_monitor.py`
- 覆盖：三度量已知答案（同分布≈0/平移放大）、三路独立阈值触发、
  响应矩阵默认映射与自定义覆盖、check_* 便捷路、输入校验 Fail-Closed

## 5. 依赖

- 标准库 + numpy；无 zephyr 内部 import（检测器族自洽）
- 下游（运行时装配，不 import）：D_FACTOR 特征降级执行 / D_ML_TRAIN 重训
  触发 / 告警路由（B13-04267 MOD-DATENG-001）汇入
