# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记（18号清单 §6 波4-11 / 11号文 §4.2 Phase 0 / apply_depgraph 设计态登记建议见 .runtime/p3_fragments/w4_11.md）
# [MODULE] zephyr.research.evidence
# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定：D_RESEARCH 不在 depgraph domains 表，归属 D_KNOWLEDGE（知识管理——假设/证据=知识资产）
# [DEPENDENCIES] zephyr.research.evidence.hypothesis_registry; zephyr.research.evidence.evidence_chain; zephyr.research.evidence.iteration_guide; zephyr.research.evidence.batch_entry
# [CONSUMERS] 手动 CLI/调度挂点（batch_entry.main）；tests/research/test_evidence_phase0.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 包子包公共 API 面=本文件 __all__；三件套单向依赖 hypothesis_registry → evidence_chain → iteration_guide → batch_entry（无环）
# [MODIFY-GUARD] tests/research/test_evidence_phase0.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见各子模块头注（ZA-RE-0001~0031）
# [TESTS] tests/research/test_evidence_phase0.py
# [A_module] module_id=MOD-EVIDENCE_CHAIN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""研究证据关联组件（Evidence Chain 三件套+批量入口）——11号文 §4.2 Phase 0。

子模块：
- hypothesis_registry：假设注册表（CRUD + 状态机 proposed→testing→
  supported/refuted→archived，JSON 落盘）
- evidence_chain：证据链（三态 support/contradict/neutral + 假设外键 +
  SHA-256 固化防篡改，append-only jsonl 落盘）
- iteration_guide：迭代引导器（显式规则集 → 继续/转向/放弃建议，规则表
  config 化 config/iteration_guide_rules.yaml，建议可追溯命中规则）
- batch_entry：日/周频批量入口（手动 CLI + 计划任务挂点；盘中工作日
  09:30-15:00 CST 拒绝执行守卫——盘中零调用）

落盘根：data/research/evidence/（选择理由见 hypothesis_registry docstring）。
设计真源：docs/02_enterprise_architecture/09_ai_architecture/
implementation_plans/11_evidence_skill_router.md §3.1/§4.2。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发）
#   code: import zephyr.research.evidence
# 层: 算法
# - id: A1
#   name_zh: ① 子包公共 API 面聚合
#   name_en: __init__ re-export
#   desc: 从四个子模块（hypothesis_registry/evidence_chain/iteration_guide/batch_entry）re-export 公共符号，__all__ 声明 27 项
#   inputs: I1
#   outputs: 子包公共命名空间
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面 __all__
#   name_en: __all__
#   downstream: 手动 CLI/调度挂点（batch_entry.main）；tests/research/test_evidence_phase0.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.research.evidence.batch_entry import (
    BatchEntryError,
    BatchReport,
    IntradayExecutionForbiddenError,
    is_intraday,
    run_batch,
)
from zephyr.research.evidence.evidence_chain import (
    EvidenceChain,
    EvidenceChainError,
    EvidenceEntry,
    EvidenceIntegrityError,
    EvidencePolarity,
    EvidenceSummary,
    InvalidPolarityError,
    UnknownHypothesisError,
)
from zephyr.research.evidence.hypothesis_registry import (
    ALLOWED_TRANSITIONS,
    Hypothesis,
    HypothesisNotFoundError,
    HypothesisRegistry,
    HypothesisRegistryError,
    HypothesisStatus,
    InvalidTransitionError,
)
from zephyr.research.evidence.iteration_guide import (
    Guidance,
    GuideRule,
    IterationGuide,
    IterationGuideConfigError,
    IterationGuideError,
    Recommendation,
    load_rules,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "BatchEntryError",
    "BatchReport",
    "EvidenceChain",
    "EvidenceChainError",
    "EvidenceEntry",
    "EvidenceIntegrityError",
    "EvidencePolarity",
    "EvidenceSummary",
    "GuideRule",
    "Guidance",
    "Hypothesis",
    "HypothesisNotFoundError",
    "HypothesisRegistry",
    "HypothesisRegistryError",
    "HypothesisStatus",
    "InvalidPolarityError",
    "InvalidTransitionError",
    "IntradayExecutionForbiddenError",
    "IterationGuide",
    "IterationGuideConfigError",
    "IterationGuideError",
    "Recommendation",
    "UnknownHypothesisError",
    "is_intraday",
    "load_rules",
    "run_batch",
]
