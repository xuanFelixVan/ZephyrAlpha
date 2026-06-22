# [A_module] module_id=MOD-UNK_observability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [MODULE] zephyr.observability

import importlib as _importlib

from zephyr.shared.adaptive_sampler import AdaptiveSampler, SamplingDecision
from zephyr.shared.reasoning_spans import ReasoningSpan, ReasoningSpans

from . import feedback_loop

__all__ = [
    "AdaptiveSampler",
    "AttributionEngineBase",
    "ReasoningSpan",
    "ReasoningSpans",
    "SamplingDecision",
    "TCAEngineBase",
    "analytics_base",
    "feedback_loop",
]


def __getattr__(name):
    if name in ("TCAEngineBase", "AttributionEngineBase", "analytics_base"):
        mod = _importlib.import_module(".analytics_base", __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
