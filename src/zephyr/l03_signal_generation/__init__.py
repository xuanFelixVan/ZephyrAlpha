"""L03 Signal Generation
=====================================

14 层量化架构 · L03 信号生成层

职责
----
Alpha 因子融合为交易信号：因子加权组合 → 信号打分 → 信号过滤/去重。

子模块
------
- aggregator_base.py     : 信号聚合器基类 (SignalAggregatorBase) — 通用聚合
- signal_synthesizer.py  : 信号合成器基类 (SignalSynthesizerBase) — Phase B 骨架已生成
- capital_allocator.py   : 资本配置器基类 (CapitalAllocatorBase) — Phase B 骨架已生成

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-001  NormalizedMarketData      ← L00
  - CTR-002  FactorSignal              ← L02
  - CTR-ERR-002  FactorComputationError ← L02
  - CTR-P1-001  FactorMonitorReport    ← L02
  - CTR-P1-002  MacroFactorSignal      ← L02
  - CTR-P1-004  ModelServingRequest    ← L11
  - CTR-P1-005  ModelServingResponse   ← L11

作为生产者（Producer）：
  - CTR-P1-003  CapitalAllocationResult       → L05
  - CTR-P1-015  SynthesizedSignal              → L04, L05
  - CTR-ERR-003  SignalDegradationWarning  → L04, L05（信号质量下降时触发）

SSoT: cross-layer-contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

from __future__ import annotations

from zephyr.l03_signal_generation.aggregator_base import (
    DegradationMonitorBase,
    SignalAggregatorBase,
)
from zephyr.l03_signal_generation.capital_allocator import (
    CapitalAllocationResult,
    CapitalAllocatorBase,
)
from zephyr.l03_signal_generation.signal_synthesizer import SignalSynthesizerBase
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal

__all__ = [
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "DegradationMonitorBase",
    "SignalAggregatorBase",
    "SignalSynthesizerBase",
    "SynthesizedSignal",
]
