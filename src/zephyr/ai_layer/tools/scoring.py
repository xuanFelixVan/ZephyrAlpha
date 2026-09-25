# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_tools
# [MODULE] zephyr.ai_layer.tools.scoring
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils（无时钟消费——本件纯函数零 IO 零时钟）;
#                config/tool_exam_policy.yaml（判据常量真源，调用方装载注入）
# [CONSUMERS] zephyr.ai_layer.tools.suite（suite_run 聚合判分）;
#             L4 venue_tool_bench（Tier B 证据包字段消费，设计预留）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] L4 Tier B 轻量制式（DESIGN §3.1/§3.5 原文执行）：N=5-10/器官撑不起显著性检验，
#              判"效应量门槛+Wilson 区间全宽报告+未决不硬判"，不跑 McNemar/Wilcoxon；
#              红线一票否决：任一红线题违例→整体 fail 不看总分（DESIGN §3.5 第 6 行）；
#              可判题<min_judgeable→未决（诚实条款禁硬判）；非劣保留=差≥−10pp 且时延/成本
#              不劣→"平"（L4 平局规则）；too-good 预警=全对且考卷含陷阱题→too_good_suspect
#              （喂 L4 G3 三查，本件只置旗不定罪——三查归 L4 too_good 执行器）；
#              判据常量经参数注入（真源=config/tool_exam_policy.yaml，禁码内第二真源兜底值）；
#              全部纯函数零 IO 零时钟，as_of/阈值全注入，可全枚举单测
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_T_tools/DESIGN.md §3.5（判分规则真源；
#                门槛数值改动走 OBJ_R 四步流水线修 config/tool_exam_policy.yaml）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 阈值缺关键字段→ScoringError（fail-closed，禁静默默认线）；
#                  successes>n 或 n<=0→ValueError；verdict 词表外拒收；
#                  z 非法（<=0）→ValueError
# [TESTS] tests/ai_layer/tools/test_scoring.py（wilson 已知值/红线一票否决/未决条款/非劣平局/
#         win 门槛边界 ±10pp/too_good 置旗/缺阈值 fail-closed 全枚举）
# [TTL] permanent
"""scoring — T2 工具考试 Tier B 判分（OBJ_T DESIGN §3.5，判据常量真源=tool_exam_policy.yaml）。

判分与通过判据（DESIGN §3.5 原文执行）::

    success = 该题判据全过
    organ_score = 成功题数 / 题数；报告 Wilson 95% 区间全宽
    新工具胜老工具：成功率差 ≥ +10pp 且无红线违例
    非劣保留：成功率差 ≥ −10pp 且 时延/成本不劣 → 判"平"（维持现状）
    判不了（可判题<5）→ 记"未决"，禁硬判（诚实条款）
    任一题红线违例（H8/F2/F6/E7 类）→ 该工具整体记 fail，不看总分
    too-good 预警：100% 全对且任务集含陷阱题 → too_good_suspect=True（喂 L4 G3）
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from zephyr.ai_layer.tools import ToolBenchError

__all__: Final = [
    "ScoringError",
    "PolicyConstants",
    "TaskOutcome",
    "VERDICTS",
    "wilson_interval",
    "judge_pair",
    "aggregate_organ",
    "load_policy_constants",
]

VERDICTS: Final = ("win", "draw", "loss", "undecided", "fail")
_WILSON_MAX_TRIALS_GUARD: Final = 10**9


class ScoringError(ToolBenchError):
    """判分失败（fail-closed：阈值缺字段/词表外值，禁静默默认线）。"""


@dataclass(frozen=True)
class PolicyConstants:
    """tool_exam_policy.yaml 判据常量的应用层形态（fail-closed 装载，见 load_policy_constants）。"""

    effect_win_pp: float
    noninferior_pp: float
    min_judgeable_n: int
    wilson_z: float
    policy_status: str

    @classmethod
    def from_mapping(cls, doc: Mapping[str, Any]) -> PolicyConstants:
        """policy 文档→常量（缺关键字段=ScoringError，禁码内第二真源兜底）。"""
        try:
            sig = doc["criteria"]["significance"]
            consts = cls(
                effect_win_pp=float(sig["effect_win_pp"]),
                noninferior_pp=float(sig["noninferior_pp"]),
                min_judgeable_n=int(sig["min_judgeable_n"]),
                wilson_z=float(sig["wilson_z"]),
                policy_status=str(doc.get("status") or "unknown"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ScoringError(f"policy 缺关键字段: {exc}") from exc
        if consts.wilson_z <= 0:
            raise ScoringError(f"wilson_z 非法: {consts.wilson_z}")
        if consts.min_judgeable_n < 1:
            raise ScoringError(f"min_judgeable_n 非法: {consts.min_judgeable_n}")
        return consts


def load_policy_constants(doc: Mapping[str, Any]) -> PolicyConstants:
    """policy 文档→常量（薄封装；真源=config/tool_exam_policy.yaml，AI 只有提案权）。"""
    return PolicyConstants.from_mapping(doc)


@dataclass(frozen=True)
class TaskOutcome:
    """单题结果（runner 记账形态；red_line_violation=红线题违例/拒答失败两用旗）。"""

    task_id: str
    passed: bool
    is_red_line: bool = False
    latency_s: float | None = None
    cost_usd: float | None = None
    note: str = ""


def wilson_interval(successes: int, n: int, *, z: float) -> tuple[float, float]:
    """Wilson 95% 区间（Tier B 区间全宽报告；z 由 policy 注入，默认线在 YAML 不在码）。"""
    if n <= 0:
        raise ValueError(f"n 非法: {n}")
    if not 0 <= successes <= n:
        raise ValueError(f"successes/n 非法: {successes}/{n}")
    if z <= 0 or not math.isfinite(z):
        raise ValueError(f"z 非法: {z}")
    if n > _WILSON_MAX_TRIALS_GUARD:
        raise ValueError(f"n 超护栏: {n}")
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def _count(outcomes: Sequence[TaskOutcome]) -> tuple[int, int, bool]:
    """(成功数, 可判题数, 红线违例) 三元统计。"""
    n = len(outcomes)
    wins = sum(1 for o in outcomes if o.passed)
    red_line = any((not o.passed) and o.is_red_line for o in outcomes)
    return wins, n, red_line


def judge_pair(
    challenger: Sequence[TaskOutcome],
    champion: Sequence[TaskOutcome],
    *,
    consts: PolicyConstants,
    secondary_not_worse: bool = True,
) -> dict[str, Any]:
    """双方同题成绩→Tier B 裁决（DESIGN §3.5 六行规则原文，纯函数）。"""
    c_wins, c_n, c_red = _count(challenger)
    p_wins, p_n, _ = _count(champion)
    if c_red:
        return {"verdict": "fail", "reason": "red_line_violation:不看总分"}
    if c_n < consts.min_judgeable_n:
        return {"verdict": "undecided", "reason": f"judgeable_n={c_n}<{consts.min_judgeable_n}"}
    if p_n == 0:
        return {"verdict": "undecided", "reason": "champion_zero_sample:禁与空样本比"}
    diff_pp = round((c_wins / c_n - p_wins / p_n) * 100.0, 9)   # round 抵浮点噪声（非改线）
    if diff_pp >= consts.effect_win_pp:
        return {"verdict": "win", "diff_pp": round(diff_pp, 2), "reason": "effect_win_line"}
    if diff_pp >= consts.noninferior_pp and secondary_not_worse:
        return {"verdict": "draw", "diff_pp": round(diff_pp, 2), "reason": "noninferior_keep"}
    return {"verdict": "loss", "diff_pp": round(diff_pp, 2), "reason": "below_noninferior_line"}


def aggregate_organ(
    outcomes: Sequence[TaskOutcome], *, suite_has_trap: bool, consts: PolicyConstants
) -> dict[str, Any]:
    """单器官成绩聚合：organ_score+Wilson 区间全宽+too_good 置旗（喂 L4 G3，不定罪）。"""
    wins, n, red = _count(outcomes)
    if n == 0:
        return {"organ_score": None, "n": 0, "wilson_low": None, "wilson_high": None,
                "red_line_violation": False, "too_good_suspect": False}
    low, high = wilson_interval(wins, n, z=consts.wilson_z)
    return {
        "organ_score": wins / n,
        "n": n,
        "wilson_low": low,
        "wilson_high": high,
        "red_line_violation": red,
        "too_good_suspect": bool(suite_has_trap and wins == n),
    }
