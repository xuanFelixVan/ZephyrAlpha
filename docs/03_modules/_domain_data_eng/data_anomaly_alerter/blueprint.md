---
blueprint_id: MOD-DATENG-001
module_name: data_anomaly_alerter
domain: D_DATA_ENG
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
domain_id: D_DATA_ENG
path: src/zephyr/data_eng/data_anomaly_alerter.py
granularity: file
---

# MOD-DATENG-001 data_anomaly_alerter 蓝图（D-DATA-112 Data Anomaly Alerter 数据异常告警器）

> **module_id**: MOD-DATENG-001 | **域**: D_DATA_ENG | **优先级**: P1
> **来源**: B13-04267（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-DATENG-004，A3数据架构 §17.1）
> 代码：`src/zephyr/data_eng/data_anomaly_alerter.py`

## 0. 定位

多维度数据异常检测 + 告警分级 + 路由 + 抑制的**告警中心件**：
跳变 z-score / 缺失率 / 量价背离 / 跨源偏差四路检测 → AL-P1~P4 分级 →
同源同因合并 + 维护窗口静默抑制 → 路由复用 `zephyr.data.alerter`（DI 注入）→
质量门控事件输出。

查重分工（W-P1-24 铁律①探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| cleaning_anomaly_engine | MOD-DATA_ENG | OHLCV 帧内五维异常**检测+自动修复闭环**（跨源仲裁/前值填充/剔除标记+审计+人工审核队列） | 本件**不做修复**，检出即告警；检测维度不同（跳变 z-score 用对数收益滚动 z、缺失率、量价背离、跨源偏差），输出走告警路由+质量门控事件 |
| alerter | MOD-GOV-alerter | 任务失败分级告警通道（飞书/SMTP/failure 文件） | 本件经 alert_sink 依赖注入复用其通道，不重建通道 |
| integrity_checker | MOD-GOV-integrity_checker | 行数完整性巡检（7 天日均×0.5） | 只检测行数健康，无多维异常与抑制 |
| cross_source_validator | MOD-L00-004 | 跨源比对（字段级一致性） | 本件跨源偏差=价格偏差 bps 阈值告警，维度不同 |
| quality_gate | MOD-GOV-quality_gate | 字段级校验门控（阻断/降级/告警三档） | 本件输出质量门控**事件**供其消费，不替代门控本体 |

TSV 裁定原文："已有任务失败分级告警与 integrity_checker/cross_source_validator，
缺多维度数据异常检测与告警抑制"——施工形态=1 个新模块。

## 1. 规则（确定性，纯内存判定核心）

- **四路检测**（全部纯函数，numpy/pandas 内存计算，不触网不触库）：
  - `detect_price_jumps(closes, z_threshold=4.0, window=20)`：对数收益滚动 z-score，
    |z|≥阈值 → price_jump 信号（附 z 值与收益）。
  - `detect_missing_rate(expected, actual, warn=0.05, critical=0.20)`：缺失率
    =1−actual/expected 分档告警。
  - `detect_volume_price_divergence(closes, volumes, window=20, corr_threshold=0.0)`：
    滚动窗口价量相关系数 < 阈值（价涨量缩/背离）→ volume_price_divergence。
  - `detect_cross_source_deviation(primary, secondary, tolerance_bps=30.0)`：
    同源双通道价格偏差 |Δ|/ref×10⁴ bps 超容差 → cross_source_deviation（附最大偏差）。
- **告警分级**：超出比 ratio=value/threshold 映射 AL-P4(≥1)/AL-P3(≥2)/AL-P2(≥5)/
  AL-P1(≥10)（severity 枚举 AlertGrade.P1~P4；路由时 P1/P2→CRITICAL/ERROR，
  P3→WARN，P4→INFO 对齐 Alerter 通道阈值）。
- **抑制规则**：①同源同因合并——dedup_key=(source,kind,symbol) 在
  merge_window_sec 内重复信号合并（计数累加不重复路由）；②维护窗口静默——
  maintenance_windows 内信号标记 silenced=True 不路由仅留痕。
- **输出**：AnomalyAlert（分级+抑制标记）列表 + QualityGateEvent（kind/
  severity/symbol/metric 摘要）列表；路由经 alert_sink(task_id,error,level,
  source,extra) 回调（默认惰性 zephyr.data.alerter.Alerter().notify，可注入）。
- Fail-Closed：输入为空/长度不齐/阈值非正 → DataAnomalyAlerterError；通道异常
  不阻断判定（吞掉留痕，与 alerter 不变式对齐）。

## 2. 接口

```python
class AnomalyKind(str, Enum): PRICE_JUMP/MISSING_RATE/VOLUME_PRICE_DIVERGENCE/CROSS_SOURCE_DEVIATION
class AlertGrade(str, Enum): P1/P2/P3/P4
@dataclass(frozen=True) class AnomalySignal: kind/symbol/metric_value/threshold/detail
@dataclass(frozen=True) class AnomalyAlert: signal+grade+silenced+merged_count+dedup_key
@dataclass(frozen=True) class QualityGateEvent: kind/severity/symbol/metric_value/message
@dataclass(frozen=True) class MaintenanceWindow: start_utc/end_utc/reason

class DataAnomalyAlerter:  # alert_sink/merge_window_sec/maintenance_windows 注入
    evaluate(signals, now_utc) -> (list[AnomalyAlert], list[QualityGateEvent])  # 分级+抑制+路由
    detect_and_evaluate(closes=..., volumes=..., expected=..., actual=...,
                        primary=..., secondary=..., symbol=..., source=...,
                        now_utc=...) -> 同上  # 四路检测+评估一站式
class DataAnomalyAlerterError(Exception): 占位 ZA-DATENG-UNREGISTERED-ANOMALY-ALERTER
```

## 3. 错误契约

- `DataAnomalyAlerterError`（未登记错误码-申请中，占位
  ZA-DATENG-UNREGISTERED-ANOMALY-ALERTER，建议号段见 W-P1-24 fragment）

## 4. 测试

- `tests/zephyr/data/test_data_anomaly_alerter.py`
- 覆盖：四路检测触发/不触发、分级映射、同源同因合并、维护窗口静默、
  质量门控事件形态、alert_sink 注入与异常吞掉、输入校验 Fail-Closed

## 5. 依赖

- 标准库 + numpy/pandas（内存计算）；`zephyr.data.alerter`（惰性，可注入替代）
- 下游（运行时装配，不 import）：质量门控/信号退化监控（B13-04305/04309
  复用本件路由）、D_FBL_DETECTORS 漂移件告警汇入
