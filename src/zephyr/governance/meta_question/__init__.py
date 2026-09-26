# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/30_blindspot_audit.md | §C（schema 冻结口径）+ 10_intake_gate_design.md §7（写入 API 契约）
# [MODULE] zephyr.governance.meta_question
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.meta_question_registry; zephyr.governance.meta_question.snapshot
# [CONSUMERS] 四件套姊妹件（模板生成器/未答看板/考试回填闭环，后续接线批）; tests/governance/meta_question/
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本包=meta_question_registry（原问题中央登记表）基建 src 入口：registry 写入 API+snapshot 机生快照；
#              公共接口只经本 __init__ 导出（禁深路径 import 漂移）；DDL 真源=scripts/governance/apply_meta_question_ddl.py
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md §7
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 透传子模块异常（QuestionValidationError/VersionConflictError）
# [TESTS] tests/governance/meta_question/test_registry.py
# [TTL] permanent
"""meta_question — 原问题中央登记表（meta_question_registry）基建包。

定桩战役（st-chainpile-20260922）四件套之一"入库闸"的落点：把"值得问的问题"
变成受治理资产（对标 AEA 注册中心 / OSF 预注册 / 图书馆馆员蓝图）。

- :class:`MetaQuestionRegistry`：写入 API（登记/状态流转/认领/考试记账，审计 PG+JSONL 双轨）
- :func:`export_snapshot`：YAML 机生快照（DB 真源→只读镜像，禁手改）
- 设计真源：``docs/_working/chain_piling_campaign/infra_mining/``（10 入库闸 / 13 考试回填 / 20 管理办法总册 / 30 盲点专项）
# target: src/zephyr/governance/meta_question/__init__.py (docstring 371 字, 0 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/meta_question__init__.yaml
"""

from typing import Final  # noqa: E402

from zephyr.governance.meta_question.meta_question_registry import (
    AUDIT_WHAT_VOCAB,
    BYPASS_ACTORS,
    LEGAL_TRANSITIONS,
    VALID_FREQUENCIES,
    VALID_LAYERS,
    VALID_OUTCOMES,
    VALID_STATUSES,
    MetaQuestionRegistry,
    QuestionValidationError,
    VersionConflictError,
    normalize_title,
)
from zephyr.governance.meta_question.snapshot import (
    DEFAULT_SNAPSHOT_PATH,
    export_snapshot,
    export_snapshot_from_json,
)

__all__: Final = [
    "AUDIT_WHAT_VOCAB",
    "BYPASS_ACTORS",
    "DEFAULT_SNAPSHOT_PATH",
    "LEGAL_TRANSITIONS",
    "VALID_FREQUENCIES",
    "VALID_LAYERS",
    "VALID_OUTCOMES",
    "VALID_STATUSES",
    "MetaQuestionRegistry",
    "QuestionValidationError",
    "VersionConflictError",
    "export_snapshot",
    "export_snapshot_from_json",
    "normalize_title",
]
