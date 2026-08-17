# [A_module] module_id=MOD-L00-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md
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
"""

D_DATA Data Source
=====================================

域量化架构 · D_DATA 数据接入层

职责
----
外部数据源适配接入：行情、基本面、另类数据等原始数据摄取与标准化。

子模块
------
- provider_base.py : 数据源适配基类 (IngestProviderBase) + 自动注册 (OCP 扩展点)
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 外部数据源原始数据（行情/基本面/另类数据摄取请求）
#   fields: 各数据源原始 payload（由 IngestProvider 实现类标准化）
#   code: __init__.py L51（IngestProviderBase 再导出入口）
# - id: I2
#   name: 背压信号 CTR-BP-001~003（来自 D_FACTOR）
#   fields: 暂停/降速/恢复数据推送
#   code: cross_layer_contracts.yaml v3.0
# 层: 算法
# - id: A1
#   name_zh: ① 数据源适配基类再导出
#   name_en: IngestProviderBase / IngestProviderMeta
#   intro: 统一数据源接入抽象，元类自动注册实现 OCP 扩展点
#   desc: 从 zephyr.data.provider_base 再导出；新数据源继承基类即自动注册
#   inputs: I1 I2
#   outputs: 标准化数据摄取能力
# - id: A2
#   name_zh: ② 数据质量门禁再导出
#   name_en: DataQualityGate
#   intro: 摄取数据过质量门禁，不通过抛 DataQualityError
#   desc: 从 gov_enforcement.rule_enforcement.quality_gate 再导出；失败产出 CTR-ERR-001
#   inputs: I1
#   outputs: 质量校验通过的数据
# 层: 输出
# - id: O1
#   name_zh: NormalizedMarketData 标准化市场数据契约
#   name_en: CTR-001
#   intro: 本层作为生产者的核心数据契约
#   downstream: D_FACTOR/D_SIGNAL/D_RESEARCH（CTR-001 契约消费者）
# - id: O2
#   name_zh: TraceContext 链头追踪上下文
#   name_en: CTR-TRACE-001
#   intro: trace_id 由本层创建，是全链路追踪起点
#   downstream: D_FACTOR~D_REPORTING + D_ML_TRAIN（CTR-TRACE-001）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A1 --> O1
# A2 --> O1
# A1 --> O2
"""

from __future__ import annotations

from zephyr.data.provider_base import IngestProviderBase, IngestProviderMeta
from zephyr.gov_enforcement.rule_enforcement.quality_gate import DataQualityGate

# __all__ 仅列真实导出的符号（2026-08-17 AI-04 审计治本：
# 原含 "provider_base"/"quality_gate" 两个不存在属性，`import *` 抛 AttributeError；
# 括注真源模块见上文 docstring A1/A2，不占 __all__ 名额）。
__all__ = ["DataQualityGate", "IngestProviderBase", "IngestProviderMeta"]
