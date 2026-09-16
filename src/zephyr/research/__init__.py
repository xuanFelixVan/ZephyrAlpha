# [BLUEPRINT] MOD-L09-001 | 待统筹登记（研究创新核心包）
# [MODULE] zephyr.research
# [DOMAIN] D_RESEARCH
# [DEPENDENCIES] zephyr.research.evidence（子包，首个真实实现 2026-08-22 落地）; zephyr.research.sell_news_event_study
# [CONSUMERS] 手动 CLI/调度挂点（zephyr.research.evidence.batch_entry）；tests/research/test_evidence_phase0.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 包根不 re-export 子包符号（__all__=[]），消费方显式 import zephyr.research.evidence.*
# [MODIFY-GUARD] tests/research/test_evidence_phase0.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见子包各模块头注（ZA-RE-0001~0031）
# [TESTS] tests/research/test_evidence_phase0.py
# [A_module] module_id=MOD-L09-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MOD-L09-001 Research Innovation Core — 研究创新核心包。

# [ALGO_FLOW] external: docs/03_modules/_domain_research/algo_flow/research__init__.yaml
留痕：2026-08-22 前本包为真空壳占位（[DORMANT] STR-01 标注）；18号清单 §6 波4-11
落地 evidence/ 子包（11号文 §4.2 Phase 0），按 #ARCH-143 R4 纪律作者同步摘除
DORMANT 标注；翻译注册表 build_status dormant→active 回写建议见
.runtime/p3_fragments/w4_11.md（本代理不写注册表 yaml，交统筹）。
"""

__all__ = []

# ORPHAN-MODULE: 引用登记（让 depgraph 发现 import 边；不进 __all__，保持包根不 re-export 约定）
from zephyr.research.sell_news_event_study import run_sell_news_study  # noqa: F401
