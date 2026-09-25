# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.fairness
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator (CompareCheckResult/FairnessReport 基面);
#                zephyr.ai_layer.comparator.policy (load_comparison_policy，公平性词表真源)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (run_preflight fairness_passed 闸);
#             L5 排产（win* 带星降优先级，设计预留）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 三轴+防假胜三条全机检（DESIGN §2.2），字段不等/缺失=拒考且逐字段留 reason（fail-closed）；
#              词表外 compute_class 拒收（防自造档位，词表真源=config/comparison_policy.yaml）；
#              "带星胜"降级是纯函数（win+resource_delta≠0→win*，L5 排产降优先级）；
#              全部纯函数可全枚举单测（零 IO 零时钟）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.2（公平性规则真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 机检字段缺失→该轴 fail（reason=missing:<field>...），绝不默认放行；
#                  verdict 非 win 值传 downgrade→ValueError；词表为空/缺节由 policy 层 ComparePolicyError 前置拦截
# [TESTS] tests/ai_layer/comparator/test_fairness.py（三轴相等/不等/缺失全枚举/champion 历史成绩
#         跨考纲拒/同批判据不一致拒/带星胜降级路径/词表外档位拒）
# [TTL] permanent
"""fairness — 公平性对齐器：防"新候选吃更好资源"的假胜（DESIGN §2.2）。

三轴（全机检字段，对齐器检查不等即拒考）::

    同算力档   compute_class 相等+同互斥组窗口+同配额池（quota_ref）
    同数据窗   window_spec / seed / task_suite_version 逐项相等
    同时间预算 wall_clock_cap / timeout_s / cost_accounting_version 相等

防假胜三条::

    1. champion 必须同场重考：只有考卷版本（task_suite_version）完全相同才允许引用历史成绩
    2. 新资源通道同等开放：resource_delta 非零=记录并降级"带星胜"（win*）
    3. 同批同判据：同批候选共用同一份 frozen 判据卡（batch_criteria_hash 相等）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Sequence

from zephyr.ai_layer.comparator import CompareCheckResult

__all__: Final = [
    "FAIRNESS_AXES",
    "FairnessReport",
    "FairnessSpec",
    "check_fairness",
    "downgrade_verdict",
]

FAIRNESS_AXES: Final = ("compute_class", "data_window", "time_budget")


@dataclass(frozen=True)
class FairnessSpec:
    """单方（challenger/champion）公平性机检字段组（DESIGN §2.2 机检字段列）。"""

    compute_class: str | None = None
    mutex_group: str | None = None
    quota_ref: str | None = None
    window_spec: str | None = None
    seed: int | str | None = None
    task_suite_version: str | None = None
    wall_clock_cap: str | None = None
    timeout_s: int | None = None
    cost_accounting_version: str | None = None
    batch_criteria_hash: str | None = None
    champion_score_source: str = "same_session"   # same_session（同场重考）| history（引历史成绩）
    resource_delta: str = ""                      # 非空=用了 champion 未用的资源通道（免费窗/新算力）


def _pair_equal(
    axis: str, fields: Sequence[tuple[str, object, object]]
) -> CompareCheckResult:
    """同名字段逐项相等机检（缺失与不等都 fail，reason 逐字段留痕）。"""
    bad: list[str] = []
    for name, left, right in fields:
        if left is None or right is None:
            bad.append(f"missing:{name}")
        elif left != right:
            bad.append(f"unequal:{name}({left!r}!={right!r})")
    return CompareCheckResult(name=f"axis:{axis}", passed=not bad, reason=";".join(bad) if bad else "ok")


def _check_compute_axis(
    challenger: FairnessSpec, champion: FairnessSpec, vocab: Sequence[str]
) -> list[CompareCheckResult]:
    """同算力档轴：compute_class 词表校验+互斥组窗口+配额池。"""
    checks = [_pair_equal("compute_class", [
        ("compute_class", challenger.compute_class, champion.compute_class),
        ("mutex_group", challenger.mutex_group, champion.mutex_group),
        ("quota_ref", challenger.quota_ref, champion.quota_ref),
    ])]
    if challenger.compute_class is not None and challenger.compute_class not in vocab:
        checks.append(CompareCheckResult(
            name="axis:compute_class",
            passed=False,
            reason=f"compute_class_out_of_vocab:{challenger.compute_class}",
        ))
    return checks


def check_champion_history_rule(challenger: FairnessSpec, champion: FairnessSpec) -> CompareCheckResult:
    """防假胜 #1：champion 引历史成绩仅限考卷版本完全相同，否则必须同场重考。"""
    same_suite = (
        challenger.task_suite_version is not None
        and challenger.task_suite_version == champion.task_suite_version
    )
    if champion.champion_score_source == "history" and not same_suite:
        return CompareCheckResult(
            name="anti_fake:champion_same_suite",
            passed=False,
            reason="champion_history_cross_suite:考卷版本不同禁引历史成绩，须同场重考",
        )
    return CompareCheckResult(name="anti_fake:champion_same_suite", passed=True)


def check_batch_same_criteria(challenger: FairnessSpec, champion: FairnessSpec) -> CompareCheckResult:
    """防假胜 #3：同批候选共用同一份 frozen 判据卡，禁逐候选微调门槛。"""
    bad = []
    if not challenger.batch_criteria_hash or not champion.batch_criteria_hash:
        bad.append("missing:batch_criteria_hash")
    elif challenger.batch_criteria_hash != champion.batch_criteria_hash:
        bad.append("per_candidate_criteria_tuning:判据 hash 不一致")
    return CompareCheckResult(
        name="anti_fake:same_batch_criteria",
        passed=not bad,
        reason=";".join(bad) if bad else "ok",
    )


@dataclass(frozen=True)
class FairnessReport:
    """公平性对齐报告：passed=可开考；starred=带星胜降级标记；notes 留防假胜 #2 痕。"""

    passed: bool
    starred: bool
    checks: tuple[CompareCheckResult, ...] = ()
    reasons: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    @classmethod
    def assemble(cls, checks: Sequence[CompareCheckResult], starred: bool, notes: Sequence[str]) -> "FairnessReport":
        """聚合机检清单 → 报告（任一不过即拒考；starred 只降级不阻断）。"""
        reasons = tuple(c.reason for c in checks if not c.passed)
        return cls(
            passed=not reasons,
            starred=starred,
            checks=tuple(checks),
            reasons=reasons,
            notes=tuple(notes),
        )


def check_fairness(
    challenger: FairnessSpec,
    champion: FairnessSpec,
    *,
    vocab: Sequence[str],
) -> FairnessReport:
    """三轴+防假胜三条全机检（不等/缺失=拒考且留 reason；resource_delta 非零=带星标记）。

    :param vocab: compute_class 受控词表（真源=config/comparison_policy.yaml fairness 节）
    """
    checks: list[CompareCheckResult] = []
    checks.extend(_check_compute_axis(challenger, champion, vocab))
    checks.append(_pair_equal("data_window", [
        ("window_spec", challenger.window_spec, champion.window_spec),
        ("seed", challenger.seed, champion.seed),
        ("task_suite_version", challenger.task_suite_version, champion.task_suite_version),
    ]))
    checks.append(_pair_equal("time_budget", [
        ("wall_clock_cap", challenger.wall_clock_cap, champion.wall_clock_cap),
        ("timeout_s", challenger.timeout_s, champion.timeout_s),
        ("cost_accounting_version", challenger.cost_accounting_version, champion.cost_accounting_version),
    ]))
    checks.append(check_champion_history_rule(challenger, champion))
    checks.append(check_batch_same_criteria(challenger, champion))
    starred = bool(challenger.resource_delta) or bool(champion.resource_delta)
    notes: tuple[str, ...] = ()
    if starred:
        notes = (
            "resource_delta_nonzero:新资源通道须同等开放，本批成绩降级带星胜(win*)，L5 排产降优先级",
        )
    return FairnessReport.assemble(checks, starred=starred, notes=notes)


def downgrade_verdict(verdict: str, starred: bool) -> str:
    """带星胜降级（纯函数）：win + starred → win_starred；其余原样（未知 verdict 拒绝）。"""
    if verdict not in {"win", "win_starred", "draw", "loss", "rejected_too_good"}:
        raise ValueError(f"unknown_verdict:{verdict}")
    if verdict == "win" and starred:
        return "win_starred"
    return verdict
