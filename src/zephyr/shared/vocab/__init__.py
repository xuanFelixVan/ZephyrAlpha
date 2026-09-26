# [BLUEPRINT] SH-VOCAB-001 | docs/_working/daily_loop_campaign/02_state_vocabulary_unification.md（立法真源） | §
# [MODULE] zephyr.shared.vocab
# [DOMAIN] D_SHARED
# [TTL] permanent
"""官方状态词表包（zephyr.shared.vocab）——市场状态与情绪阶段官方常量的命名空间。
# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/vocab__init__.py.yaml
"""

from typing import Final

from zephyr.shared.vocab.market_state import (
    ANCHORED_R1,
    ANCHORED_R2,
    ANCHORED_R3,
    ANCHORED_R4,
    EXTREME_STATE_ALIASES,
    INTRADAY_TO_SIX,
    AnchoredTierVocab,
    EmotionCycleSixVocab,
    IntradayFiveVocab,
    MacroRegimeVocab,
)

__all__: Final[list[str]] = [
    "ANCHORED_R1",
    "ANCHORED_R2",
    "ANCHORED_R3",
    "ANCHORED_R4",
    "EXTREME_STATE_ALIASES",
    "INTRADAY_TO_SIX",
    "AnchoredTierVocab",
    "EmotionCycleSixVocab",
    "IntradayFiveVocab",
    "MacroRegimeVocab",
]
