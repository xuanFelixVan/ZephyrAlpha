---
blueprint_id: MOD-DATA_GOV-008
module_name: record_lineage_tracker
domain: D_DATA_GOV
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
domain_id: D_DATA_GOV
path: src/zephyr/data_governance/core/record_lineage_tracker.py
granularity: file
---

# MOD-DATA_GOV-008 record_lineage_tracker 蓝图（M8-NEW-09 Metaxy Record-Level Tracker）

> **module_id**: MOD-DATA_GOV-008 | **域**: D_DATA_GOV | **优先级**: P1
> **来源**: B13-04278（AUD-DRAFT-001-DIGEST P1 波 W-P1-18，CAND-DATGOV-005，A3 数据架构 §17.2）
> 代码：`src/zephyr/data_governance/core/record_lineage_tracker.py`

## 0. 定位

M8-NEW-09 Metaxy 记录级追踪器——特征值**记录级**血缘
（source_file + transform + code_version + computed_at）：列级血缘（B13-04276）
覆盖 SQL 变换，特征值记录级血缘未建，因子审计追溯断链（TSV 现状）。
每特征批次登记溯源元数据写 **sidecar 元数据表**，支持单条因子值反查原始行情行，
与 B13-04144 离线仓 7 列 Schema 联动。

查重分工（W-P1-18 探查结论，**粒度分工**不复制）：

| 既有件 | module_id | 粒度/职责 | 与本模块边界 |
|---|---|---|---|
| lineage_tracker | MOD-DATA_GOV-002 | 表/文件级 DAG 边 | 本模块管**批次溯源台账**（非 DAG 边）；幂等哲学对齐（同键重放幂等）不建第二套图算法 |
| column_lineage_analyzer | MOD-DATA_GOV-007 | 列级（SQL 变换列依赖） | 列级=变换逻辑；本模块=**记录级批次 provenance**（哪批数据、哪版代码、何时算出），粒度互补 |
| offline_store | MOD-L02-001 | 离线仓 7 列因子值（Parquet 批量分析面） | 本模块**不重复存因子值**，只存批次溯源 sidecar；batch_id 对齐其内容寻址批文件名（batch_<sha256[:16]>）联动反查 |

不做什么：不重复建因子值仓（offline_store 职责）、不建 DAG 图算法
（lineage_tracker 职责）、批次落盘 Parquet 原子写不归本模块（写方=OfflineStore；
本模块只管 sidecar 元数据原子写 tmp+os.replace）。

## 1. 登记与反查规则

- **溯源记录** `FeatureBatchProvenance`（frozen）：batch_id（对齐离线仓批文件名
  batch_<sha256[:16]>，去 .parquet）/factor_name/source_files/transform/
  code_version/computed_at/trade_dates/row_count——必填字段空 Fail-Closed。
- **登记幂等** `register`：同 batch_id 同内容重放幂等（返回 False 不重复计）；
  同 batch_id **异内容** Fail-Closed（RecordLineageError，防溯源漂移）。
- **反查** `backtrack(factor_name, trade_date)`：(factor, trade_date) 索引 →
  批次 provenance 列表 → source_files 即原始行情行来源（单条因子值反查）。
- **sidecar 持久化**：JSONL sidecar 表（注入式路径），flush 原子写
  （tmp+os.replace，对齐离线仓原子写哲学）；load 读回重建索引；
  坏行 Fail-Closed（溯源台账不容静默错读）。

## 2. 接口

```python
class RecordLineageError(ValueError)
@dataclass(frozen=True)
class FeatureBatchProvenance: batch_id / factor_name / source_files / transform / code_version / computed_at / trade_dates / row_count
class RecordLineageTracker:
    __init__(sidecar_path: Path | None = None)
    register(provenance) -> bool
    get(batch_id) -> FeatureBatchProvenance | None
    backtrack(factor_name, trade_date) -> list[FeatureBatchProvenance]
    flush() -> int
    @classmethod load(sidecar_path) -> RecordLineageTracker
```

## 3. 依赖前置

- MOD-L02-001 offline_store（batch_id 内容寻址批文件名约定联动，只引用不重算）。
- 标准库 json/pathlib/os（sidecar JSONL + 原子写）。

## 4. 验收标准

- 单测全绿（必填校验 Fail-Closed、同内容重放幂等、异内容冲突 Fail-Closed、
  反查索引、sidecar flush/load 往返、坏行 Fail-Closed）；相关域集成零回归。
