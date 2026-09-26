# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §0 骨架总览（回写/仲裁/复考/判据四件）
# [MODULE] zephyr.governance.meta_question.exam_loop
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] .writeback; .ledger; .exam_lifecycle; .exam_plan; .arbitration; .reexam_scheduler; .event_codes
# [CONSUMERS] scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py; scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py; tests/governance/meta_question/
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 本包=WO-B1 考试循环簇（复考机器）src 入口：公共接口只经本 __init__ 导出（禁深路径 import 漂移）；
#              对上游冻结件（registry/exam_ops/snapshot）只 import 不修改——回填唯一合法入口是本包的 writeback
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md（改契约先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 透传子模块异常（QuestionValidationError/VersionConflictError/ValueError）
# [TESTS] tests/governance/meta_question/test_exam_loop_writeback.py 等 4 件
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""exam_loop — 考试循环机制与回填 API（WO-B1，B 类载体簇 1 的复考机器）。

283 问战役的"考试"已由临时通道完成，本包把那条临时通道收口为唯一合法入口，并把
"前置建成后能否真复考"变成可机检的机器：回写鉴权（PQ-0103）/双时戳落账（PQ-0056/0096）/
状态机拦截痕（PQ-0060/0051/0055）/冲突重放留痕（PQ-0061）/新鲜窗复考调度（PQ-0054/0057/0108）/
预注册考卷结构化与功效核验（PQ-0098）。

- :class:`ExamLoopWriteback`：回填唯一合法入口 ``writeback(q_id, exam_result)``
- :class:`ExamLoopStateMachine`：合法边拦截 + 拒收落账 + 乐观锁重放留痕
- :class:`ReexamScheduler`：拉取式到期/逾期对账（事件触发，禁 sleep-loop）
- :mod:`.exam_plan`：预注册考卷结构化（method/criterion/threshold/样本量/效应量/最低置信阈）
- :mod:`.arbitration`：C1-C3 矛盾检测与三取二裁定（纯计算）
- :mod:`.event_codes`：审计事件码扩展册（待总包并入 SSOT，过渡载体自动切换）
# target: src/zephyr/governance/meta_question/exam_loop/__init__.py (docstring 593 字, 0 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/exam_loop__init__.yaml
"""

from __future__ import annotations

from typing import Final

# 子模块显式重导出（公共接口只经本 __init__，禁深路径 import 漂移；冗余别名=PEP 484 再导出约定）
from . import arbitration as arbitration  # noqa: F401
from . import exam_lifecycle as exam_lifecycle  # noqa: F401
from . import exam_plan as exam_plan  # noqa: F401
from . import ledger as ledger  # noqa: F401
from . import reexam_scheduler as reexam_scheduler  # noqa: F401
from . import writeback as writeback  # noqa: F401
from .arbitration import detect_contradiction, resolve_majority
from .event_codes import (
    CODE_CLAIM_MISMATCH,
    CODE_CLAIM_MISSING,
    CODE_ILLEGAL_TRANSITION,
    CODE_SUPPLEMENT,
    CODE_THRESHOLD_LOWERED,
    CODE_VERSION_CONFLICT,
    extension_codes,
)
from .exam_lifecycle import ExamLoopStateMachine
from .exam_plan import (
    assess_power,
    check_time_layering,
    fisher_z_power,
    out_of_sample_share,
    structure_plan,
)
from .ledger import ExamLoopLedger
from .reexam_scheduler import ReexamScheduler, due_state, load_window_rules
from .writeback import ExamLoopWriteback, six_check

__all__: Final = [
    "CODE_CLAIM_MISMATCH",
    "CODE_CLAIM_MISSING",
    "CODE_ILLEGAL_TRANSITION",
    "CODE_SUPPLEMENT",
    "CODE_THRESHOLD_LOWERED",
    "CODE_VERSION_CONFLICT",
    "ExamLoopLedger",
    "ExamLoopStateMachine",
    "ExamLoopWriteback",
    "ReexamScheduler",
    "assess_power",
    "check_time_layering",
    "detect_contradiction",
    "due_state",
    "extension_codes",
    "fisher_z_power",
    "load_window_rules",
    "out_of_sample_share",
    "resolve_majority",
    "six_check",
    "structure_plan",
]
