# [A_module] module_id=MOD-UNK_observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [MODULE] zephyr.observability

from . import feedback_loop

from zephyr.shared.adaptive_sampler import AdaptiveSampler, SamplingDecision
from zephyr.shared.reasoning_spans import ReasoningSpans, ReasoningSpan

import importlib as _importlib

__all__ = ["feedback_loop", "AdaptiveSampler", "SamplingDecision", "ReasoningSpans", "ReasoningSpan", "TCAEngineBase", "AttributionEngineBase", "analytics_base"]


def __getattr__(name):
    if name in ("TCAEngineBase", "AttributionEngineBase", "analytics_base"):
        mod = _importlib.import_module(".analytics_base", __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
