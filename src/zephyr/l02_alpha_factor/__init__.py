# [BLUEPRINT] MOD-L02-001 | 03_modules/l02_alpha_factor/alpha-factor-core/blueprint.md | §
"""ZephyrAlpha — L02 Alpha Factor Layer

SSoT: cross-layer-contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理

Phase B 骨架 — 因子基类 / 元类 / 注册表 / 自动发现

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标。任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-001  NormalizedMarketData    ← L00
  - CTR-ERR-001  DataQualityError    ← L00

作为生产者（Producer）：
  - CTR-002  FactorSignal            → L03, L04, L05
  - CTR-BP-001~003  Backpressure     → L00（背压信号——暂停/降速/恢复数据推送）
  - CTR-ERR-002  FactorComputationError → L03

"""
from __future__ import annotations

from .factor_base import (
    FactorBase,
    FactorMeta,
    FactorRegistry,
    autodiscover_factors,
)

__all__ = ['FactorBase', 'FactorMeta', 'FactorRegistry', 'autodiscover_factors', 'base', 'factor_base']

# CODEGEN-GUARD: __init__-manual-exports
# 包级导出以 factor_base 为 SSoT（base.py 为 codegen 占位；禁止混用两套 FactorBase）
# CODEGEN-GUARD: CTR-declarations-manual
# DO NOT regenerate: CTR declarations are manually curated SSoT annotations