# [A_module] module_id=MOD-DAT_satellite_geospatial_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain-data/datasource-core/blueprint.md
# [MODULE] zephyr.data.satellite_geospatial_engine
# [DOMAIN] D_DATA
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_DATA Data Source
=====================================

域量化架构 · D_DATA 数据接入层

职责
----
外部数据源适配接入：行情、基本面、另类数据等原始数据摄取与标准化。

子模块
------
- provider_base.py : 数据源适配基类 (DataSourceBase) + 自动注册 (OCP 扩展点)
- quality_gate.py  : 数据质量门禁 (DataQualityGate) — Phase B 骨架已生成

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为生产者（Producer）：
  - CTR-001  NormalizedMarketData      -> D_FACTOR, D_SIGNAL, D_RESEARCH
  - CTR-TRACE-001  TraceContext        -> D_FACTOR~D_REPORTING, D_ML_TRAIN（链头——trace_id 由本层创建）
  - CTR-ERR-001  DataQualityError      -> D_FACTOR（质量门禁不通过时抛出）

作为消费者（Consumer）：
  - CTR-BP-001~003  Backpressure       ← D_FACTOR（背压信号——暂停/降速/恢复数据推送）

SSoT: cross_layer_contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

from __future__ import annotations

from zephyr.data.provider_base import DataSourceBase, DataSourceMeta
from zephyr.gov_enforcement.rule_enforcement.quality_gate import DataQualityGate

__all__ = ["DataQualityGate", "DataSourceBase", "DataSourceMeta", "provider_base", "quality_gate"]
