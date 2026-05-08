"""L00 Data Source
=====================================

14 层量化架构 · L00 数据接入层

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
  - CTR-001  NormalizedMarketData      → L02, L03, L09
  - CTR-TRACE-001  TraceContext        → L02~L07, L11（链头——trace_id 由本层创建）
  - CTR-ERR-001  DataQualityError      → L02（质量门禁不通过时抛出）

作为消费者（Consumer）：
  - CTR-BP-001~003  Backpressure       ← L02（背压信号——暂停/降速/恢复数据推送）

SSoT: cross-layer-contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

from __future__ import annotations

from zephyr.l00_data_source.provider_base import DataSourceBase, DataSourceMeta
from zephyr.l00_data_source.quality_gate import DataQualityGate

__all__ = ['DataQualityGate', 'DataSourceBase', 'DataSourceMeta', 'provider_base', 'quality_gate']
