# [BLUEPRINT] MOD-L09-001 | 待统筹登记（研究创新核心包）
# [MODULE] zephyr.research
# [DOMAIN] D_RESEARCH
# [DEPENDENCIES] zephyr.research.evidence（子包，首个真实实现 2026-08-22 落地）
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.research
# 层: 算法
# - id: A1
#   name_zh: ① 研究创新核心包命名空间声明
#   name_en: __init__（模块级 __all__）
#   intro: 声明 MOD-L09-001 研究域包入口；子包 evidence/ 为包内首个真实实现
#   desc: 全头注（domain=D_RESEARCH）+ __all__ = []，包根不 re-export 子包符号；
#         子包 evidence/（MOD-EVIDENCE_CHAIN，11号文 §4.2 Phase 0，2026-08-22 落地）：
#         假设注册表/证据链/迭代引导器/日周频批量入口四件套
#   inputs: I1
#   outputs: 空命名空间包对象
#   invariant: __all__ 恒为空列表（消费方显式 import 子包）
# 层: 输出
# - id: O1
#   name_zh: 空导出列表 __all__
#   name_en: __all__
#   intro: 包根导出 0 个符号；evidence 子包公共 API 见其 __init__ __all__
#   invariant: len(__all__) == 0
#   downstream: 无下游/内部使用（全仓无 src 模块 import zephyr.research）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1

留痕：2026-08-22 前本包为真空壳占位（[DORMANT] STR-01 标注）；18号清单 §6 波4-11
落地 evidence/ 子包（11号文 §4.2 Phase 0），按 #ARCH-143 R4 纪律作者同步摘除
DORMANT 标注；翻译注册表 build_status dormant→active 回写建议见
.runtime/p3_fragments/w4_11.md（本代理不写注册表 yaml，交统筹）。
"""

__all__ = []

# ORPHAN-MODULE: 引用登记（让 depgraph 发现 import 边；不进 __all__，保持包根不 re-export 约定）
from zephyr.research.sell_news_event_study import run_sell_news_study  # noqa: F401
