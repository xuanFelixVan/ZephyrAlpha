# [A_module] module_id=MOD-L03-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
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

D_SIGNAL Signal Domain

Signal域统一包。聚合信号生成、策略、合成、组合、资本配置和管线。

子模块:
  gen/       — 信号生成 (SignalAggregatorBase, CapitalAllocatorBase)
  strategy/  — 资本配置策略 (CapitalAllocatorBase re-export, DefaultCapitalAllocator)
  synth/     — 信号合成 (SignalSynthesizerBase)
  combiner/  — 信号合成组合器 (SynthesizedSignal)
  capital/   — 多策略资本配置 (CapitalAllocationResult, DefaultCapitalAllocator)
  pipeline/  — Alpha信号管线 (AlphaSignalPipeline)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包属性访问 请求
#   fields: name 属性名（10个公开符号之一）
#   code: __getattr__(name) L44
# 层: 算法
# - id: A1
#   name_zh: ① 信号域符号懒加载聚合
#   name_en: __getattr__ + _lazy 映射
#   intro: 按需加载信号生成/合成/资本配置/管线的基类与默认实现
#   desc: _lazy 映射 10 符号到 gen/strategy/synth/combiner/capital/pipeline 子模块，命中即 importlib.import_module 取符号；DegradationMonitorBase 真源已迁 D_SIGQC 域（L44-63）
#   inputs: I1
#   outputs: SignalAggregatorBase/DefaultSignalAggregator/DefaultCapitalAllocator/AlphaSignalPipeline 等
# 层: 输出
# - id: O1
#   name_zh: 信号域公共API面
#   name_en: signal_fundamental 公共符号集
#   intro: 对外暴露信号聚合、合成、资本配置与Alpha管线的核心抽象
#   downstream: 无下游/内部使用（# [CONSUMERS] 头为空）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

__all__ = [
    "AllocationMethod",
    "AlphaSignalPipeline",
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "DefaultCapitalAllocator",
    "DefaultSignalAggregator",
    "DegradationMonitorBase",
    "SignalAggregatorBase",
    "SignalSynthesizerBase",
    "SynthesizedSignal",
    "pipeline",
]


def __getattr__(name):
    _lazy = {
        "SignalAggregatorBase": ".gen.aggregator_base",
        "CapitalAllocatorBase": ".gen.aggregator_base",
        # DegradationMonitorBase 真源已迁移至 D_SIGQC 域（2026-07-06 域边界修正）。
        "DegradationMonitorBase": "zephyr.signal_quality.degradation_monitor_base",
        "SignalSynthesizerBase": ".synth.signal_synthesizer",
        "AlphaSignalPipeline": ".pipeline",
        # SynthesizedSignal 真源在 shared/contracts（CTR-P1-015 契约 SSoT），
        # combiner/synthesized_signal.py 不存在——原指向悬空模块会 ModuleNotFoundError。
        "SynthesizedSignal": "zephyr.shared.contracts.synthesized_signal",
        "CapitalAllocationResult": ".capital.capital_allocation_result",
        "DefaultSignalAggregator": ".gen.implementations.default_signal_aggregator",
        "DefaultCapitalAllocator": ".strategy.implementations.default_capital_allocator",
        "AllocationMethod": ".strategy.implementations.default_capital_allocator",
    }
    if name in _lazy:
        import importlib

        mod = importlib.import_module(_lazy[name], __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
