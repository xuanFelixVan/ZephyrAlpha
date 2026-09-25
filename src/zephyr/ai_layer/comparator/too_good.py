# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.too_good
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator.policy (触发线 G1-G5/ε/归因词表真源，config/comparison_policy.yaml);
#                zephyr.factor.analysis.bhy_fdr (查③多重比较复算的 BHY 计算真源，由调用方注入结果)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (裁定卡 too_good_exit/attribution 字段供源);
#             L6 观察期（E2 加严监控消费方，设计预留）；L2 阴性库（E3 rejected_too_good，设计预留）
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] 触发线检测+三查+出口路由全部纯函数（可全枚举单测，零 IO 零时钟）；
#              G1-G5 触发线可配置（读常量层 config/comparison_policy.yaml，禁硬编码线值）；
#              三查结论三值枚举 found/cleared/inconclusive（证据缺失=inconclusive，诚实条款，
#              绝不虚构结论）；出口路由只产**建议**（E1/E2/E3 裁定权=评估者会话，本件不越权定裁）；
#              好到反常与坏到反常同一条 anomalous 路线（README 待挖清单 #6）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.5（触发线/三查/三出口真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知触发组/查 id/条目 id→ValueError（fail-closed，防拼错静默漏查）；
#                  触发线组缺键→ValueError（尺子残缺宁可拒判不可错判）；metrics 缺键=该规则跳过
#                  （诚实条款：缺证据不判 found 也不判 cleared）
# [TESTS] tests/ai_layer/comparator/test_too_good.py（G1-G5 触发线全枚举含边界/ε 压线带/
#         三查三值全枚举/未知条目拒/出口路由全路径/引文常量在档）
# [TTL] permanent
"""too_good — "好得不像真"三查执行器：触发线检测 + 三查 checklist + 三出口流转建议。

设计真源：``docs/_working/ai_layer_vision/L4_compare/DESIGN.md`` §2.5。

**EX-R1 销账（引文补核完成，2026-09-23 实网核验）**：specification gaming 思想锚引文=
Krakovna, V., Kramár, J., & Eccles, T. (2020-04-21). "Specification gaming: the flip side
of AI ingenuity." DeepMind 博客
（https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/），
定义="satisfies the literal specification of an objective without achieving the intended
outcome"。DESIGN 挖矿日志 EX-R1 的 429 受阻挂单在此销账，未编引文。

三出口（裁定写进 experiment 卡，全部留痕；本件只产建议，评估者签发）::

    E1 改考场重跑（可修复泄漏的唯一出路，新 experiment_id）
    E2 接受但加监控（L6 观察期顶格 3 个月+回切线收紧两档+月度体检）
    E3 驳回（verdict=rejected_too_good+归因三选一→阴性库）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

__all__: Final = [
    "CHECK_ITEM_CATALOG",
    "CHECK_IDS",
    "CONCLUSIONS",
    "EXITS",
    "CheckConclusion",
    "SPEC_GAMING_CITATION",
    "TRIGGER_GROUP_IDS",
    "TooGoodChecklistItem",
    "ExitRoute",
    "TriggerHit",
    "TriggerReport",
    "borderline_value",
    "detect_triggers",
    "max_borderline_run",
    "route_exit",
    "run_check",
]

TRIGGER_GROUP_IDS: Final = ("G1_algo", "G2_model", "G3_tool", "G4_replay", "G5_generic")
CHECK_IDS: Final = ("leakage", "hidden_risk", "luck_or_gaming")
CONCLUSIONS: Final = ("found", "cleared", "inconclusive")
EXITS: Final = ("E1", "E2", "E3")
ATTRIBUTIONS: Final = ("leakage", "hidden_risk", "luck_or_gaming")

# Kapoor & Narayanan (Patterns 2023) 八类泄漏分类学的本仓 checklist 落点（DESIGN §2.5 查①）
LEAKAGE_ITEMS: Final = (
    "window_overlap",          # 时序窗重叠
    "preprocessing_leak",      # 预处理泄漏（全量归一化后再切窗）
    "overlapping_windows",     # 重叠加窗
    "non_independent_samples",  # 非独立样本
    "question_contamination",  # 考题污染（模型类：考题/变体进候选清洗语料，MCE RISK-3.4 同源）
    "exam_hash_consistent",    # 机检：考卷 sha256 vs 候选接触记录比对
)
HIDDEN_RISK_ITEMS: Final = (
    "tail_review",             # 收益分布尾部（偏度/最大回撤/tail ratio，卖保险形态）
    "param_perturbation_stable",  # 参数扰动敏感性（overfitting_adjudicator 检验器③复用）
    "capacity_assumptions",    # 容量/滑点/手续费假设敏感性
    "win_case_diversity",      # 胜例定性抽检（胜例同质化=只会一种题，模型类）
)
LUCK_GAMING_ITEMS: Final = (
    "multiple_comparison_cleared",  # 多重比较复算（同批 N 与 BHY 校正后 q——赢在没校正前=运气）
    "seed_window_stable",           # 种子/窗口敏感性（换 3 种子+滚动窗，排序不稳=过拟合考纲）
    "inbreeding_cleared",           # 近亲繁殖（候选与考卷同源同作者，L2 simhash+L7 先验）
    "benchmark_memory_cleared",     # 基准记忆（模型类=变体题冒烟重考）
    "spec_gaming_reviewed",         # specification gaming 自问：候选在优化考卷还是优化目标？
)
CHECK_ITEM_CATALOG: Final[dict[str, tuple[str, ...]]] = {
    "leakage": LEAKAGE_ITEMS,
    "hidden_risk": HIDDEN_RISK_ITEMS,
    "luck_or_gaming": LUCK_GAMING_ITEMS,
}

# EX-R1 销账：补核完成的思想锚引文（机器可读；核对日期 2026-09-23，实网命中 DeepMind 官方域）
SPEC_GAMING_CITATION: Final = (
    "Krakovna, V., Kramar, J., Eccles, T. (2020-04-21). Specification gaming: the flip side "
    "of AI ingenuity. DeepMind blog. "
    "https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/"
)


@dataclass(frozen=True)
class TriggerHit:
    """单条触发线命中。"""

    group_id: str
    rule: str
    detail: str


@dataclass(frozen=True)
class TriggerReport:
    """触发线检测报告（tripped=任一组命中）。"""

    tripped: bool
    hits: tuple[TriggerHit, ...] = ()
    skipped_rules: tuple[str, ...] = ()   # 证据缺失跳过的规则（诚实条款留痕）


def _f(metrics: Mapping[str, Any], key: str) -> float | None:
    """metrics 取浮点（缺键/None=None；坏值=None 按缺证据处置，不炸批）。"""
    value = metrics.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _require_triggers(group_id: str, triggers: Mapping[str, Any], keys: Sequence[str]) -> dict[str, Any]:
    """触发线组取键（缺键=ValueError：尺子残缺拒判，绝不静默默认）。"""
    group = triggers.get(group_id)
    if not isinstance(group, Mapping):
        raise ValueError(f"trigger_group_missing:{group_id}")
    missing = [k for k in keys if k not in group]
    if missing:
        raise ValueError(f"trigger_group_missing_keys:{group_id}:{','.join(missing)}")
    return dict(group)


def _detect_g1(metrics: Mapping[str, Any], group: Mapping[str, Any]) -> tuple[list[TriggerHit], list[str]]:
    """G1 算法/策略（DESIGN §2.5）：OOS 优于 IS / 超 IS+3σ / 超同批均值+3σ / DSR≥0.99。"""
    hits: list[TriggerHit] = []
    skipped: list[str] = []
    if bool(group.get("oos_is_decay_negative")):
        decay = _f(metrics, "oos_is_decay")
        if decay is None:
            skipped.append("G1.oos_is_decay")
        elif decay < 0:
            hits.append(TriggerHit("G1_algo", "oos_better_than_is", f"oos_is_decay={decay}"))
    line = _f(group, "oos_sharpe_sigma")
    oos, iss, sig = _f(metrics, "oos_sharpe"), _f(metrics, "is_sharpe"), _f(metrics, "is_sharpe_sigma")
    if line is not None:
        if None in (oos, iss, sig):
            skipped.append("G1.oos_sharpe_sigma")
        elif oos > iss + sig * line:
            hits.append(TriggerHit("G1_algo", "oos_sharpe_exceeds_is_sigma", f"{oos}>{iss}+{sig}*{line}"))
    line = _f(group, "batch_sigma")
    score, mean, sigma = _f(metrics, "score"), _f(metrics, "batch_mean"), _f(metrics, "batch_sigma")
    if line is not None:
        if None in (score, mean, sigma):
            skipped.append("G1.batch_sigma")
        elif score > mean + sigma * line:
            hits.append(TriggerHit("G1_algo", "batch_outlier", f"{score}>{mean}+{sigma}*{line}"))
    line = _f(group, "dsr_line")
    dsr = _f(metrics, "dsr")
    if line is not None:
        if dsr is None:
            skipped.append("G1.dsr_line")
        elif dsr >= line:
            hits.append(TriggerHit("G1_algo", "dsr_too_high", f"dsr={dsr}>={line}"))
    return hits, skipped


def _detect_g2(metrics: Mapping[str, Any], group: Mapping[str, Any]) -> tuple[list[TriggerHit], list[str]]:
    """G2 模型（DESIGN §2.5）：成功率≥champion+20pp / 幻觉率=0 / 单价降幅≥50% 且非劣。"""
    hits: list[TriggerHit] = []
    skipped: list[str] = []
    line = _f(group, "success_gain_pp")
    rate, champ = _f(metrics, "success_rate"), _f(metrics, "champion_success_rate")
    if line is not None:
        if None in (rate, champ):
            skipped.append("G2.success_gain_pp")
        elif (rate - champ) * 100.0 >= line:
            hits.append(TriggerHit("G2_model", "success_gain_pp", f"+{(rate - champ) * 100.0:.2f}pp>={line}pp"))
    if bool(group.get("hallucination_zero")):
        hall = _f(metrics, "hallucination_rate")
        if hall is None:
            skipped.append("G2.hallucination_zero")
        elif hall == 0.0:
            hits.append(TriggerHit("G2_model", "hallucination_zero", "hallucination_rate=0"))
    line = _f(group, "price_cut")
    cut, noninf = _f(metrics, "price_cut_ratio"), metrics.get("success_noninferior")
    if line is not None:
        if cut is None or noninf is None:
            skipped.append("G2.price_cut")
        elif cut <= line and bool(noninf):
            hits.append(TriggerHit("G2_model", "price_cut_noninferior", f"{cut}<={line} and noninferior"))
    return hits, skipped


def _detect_g3(metrics: Mapping[str, Any], group: Mapping[str, Any]) -> tuple[list[TriggerHit], list[str]]:
    """G3 工具（DESIGN §2.5）：100% 全对 **且** 任务集含已知陷阱题（两条件同时成立）。"""
    hits: list[TriggerHit] = []
    skipped: list[str] = []
    line = _f(group, "pass_rate_perfect")
    rate = _f(metrics, "pass_rate")
    if line is None:
        return hits, skipped
    require_trap = bool(group.get("require_trap_items"))
    has_trap = metrics.get("has_trap_items")
    if rate is None or (require_trap and has_trap is None):
        return hits, ["G3.pass_rate_perfect"]
    if rate >= line and (not require_trap or bool(has_trap)):
        hits.append(TriggerHit("G3_tool", "perfect_with_traps", f"pass_rate={rate} with trap items"))
    return hits, skipped


def _detect_g4(metrics: Mapping[str, Any], group: Mapping[str, Any]) -> tuple[list[TriggerHit], list[str]]:
    """G4 重放（DESIGN §2.5）：delta 全零完美——stub 失真嫌疑优先于庆祝。"""
    hits: list[TriggerHit] = []
    skipped: list[str] = []
    line = _f(group, "jaccard_perfect")
    jac = _f(metrics, "jaccard")
    nb, np_ = metrics.get("new_block"), metrics.get("new_pass")
    if line is not None:
        if jac is None or nb is None or np_ is None:
            skipped.append("G4.perfect_delta")
        elif jac >= line and int(nb) == int(group.get("new_block_zero", 0)) and int(np_) == int(group.get("new_pass_zero", 0)):
            hits.append(TriggerHit("G4_replay", "perfect_delta", f"jaccard={jac},new_block=0,new_pass=0"))
    return hits, skipped


def _detect_g5(metrics: Mapping[str, Any], group: Mapping[str, Any]) -> tuple[list[TriggerHit], list[str]]:
    """G5 通用（DESIGN §2.5）：连续≥3 场恰好压线胜（钻营预警）。"""
    hits: list[TriggerHit] = []
    skipped: list[str] = []
    streak_min = group.get("borderline_streak")
    streak = metrics.get("borderline_streak")
    if streak_min is None:
        skipped.append("G5.borderline_streak")
    elif streak is None:
        skipped.append("G5.borderline_streak")
    elif int(streak) >= int(streak_min):
        hits.append(TriggerHit("G5_generic", "borderline_streak", f"streak={streak}>={streak_min}"))
    return hits, skipped


_DETECTORS: Final = {
    "G1_algo": _detect_g1,
    "G2_model": _detect_g2,
    "G3_tool": _detect_g3,
    "G4_replay": _detect_g4,
    "G5_generic": _detect_g5,
}


# 触发线各组必需键（缺任一键=尺子残缺拒判，fail-closed）
REQUIRED_TRIGGER_KEYS: Final[dict[str, tuple[str, ...]]] = {
    "G1_algo": ("oos_is_decay_negative", "oos_sharpe_sigma", "batch_sigma", "dsr_line"),
    "G2_model": ("success_gain_pp", "hallucination_zero", "price_cut"),
    "G3_tool": ("pass_rate_perfect", "require_trap_items"),
    "G4_replay": ("jaccard_perfect", "new_block_zero", "new_pass_zero"),
    "G5_generic": ("borderline_streak", "epsilon"),
}


def detect_triggers(group_id: str, metrics: Mapping[str, Any], triggers: Mapping[str, Any]) -> TriggerReport:
    """触发线检测（纯函数）：group_id∈G1-G5，triggers=常量层 too_good_triggers 节。

    :param metrics: 本场成绩指标（缺键的规则跳过并记 skipped_rules——诚实条款）
    :param triggers: 常量层触发线（config/comparison_policy.yaml too_good_triggers 节）
    """
    if group_id not in TRIGGER_GROUP_IDS:
        raise ValueError(f"unknown_trigger_group:{group_id}")
    group = _require_triggers(group_id, triggers, REQUIRED_TRIGGER_KEYS[group_id])
    hits, skipped = _DETECTORS[group_id](metrics, group)
    return TriggerReport(tripped=bool(hits), hits=tuple(hits), skipped_rules=tuple(skipped))


def borderline_value(value: float, threshold: float, epsilon: float) -> bool:
    """恰好压线判定（G5）：|value - threshold| < epsilon（[0,1] 归一量纲）。"""
    return abs(value - threshold) < epsilon


def max_borderline_run(margins: Sequence[float], epsilon: float) -> int:
    """最长连续压线场次（G5 streak 计算纯函数）。"""
    longest = run = 0
    for margin in margins:
        run = run + 1 if abs(margin) < epsilon else 0
        longest = max(longest, run)
    return longest


@dataclass(frozen=True)
class TooGoodChecklistItem:
    """三查 checklist 单条目：flag 三值 True=检过且干净 / False=查实问题 / None=证据不足。"""

    item_id: str
    state: str      # found / cleared / inconclusive
    note: str = ""


@dataclass(frozen=True)
class CheckConclusion:
    """单查结论（三值枚举）：any False→found；elif any None→inconclusive；else cleared。"""

    check_id: str
    conclusion: str
    items: tuple[TooGoodChecklistItem, ...] = ()
    notes: tuple[str, ...] = ()


def run_check(check_id: str, flags: Mapping[str, bool | None], notes: Sequence[str] = ()) -> CheckConclusion:
    """三查单查执行（纯函数）：item 状态从 flags 三值映射，未知条目 id 拒绝（防拼错漏查）。

    :param flags: {条目 id: True/False/None}——缺键条目按 None（inconclusive）处置，诚实条款
    """
    if check_id not in CHECK_IDS:
        raise ValueError(f"unknown_check_id:{check_id}")
    catalog = CHECK_ITEM_CATALOG[check_id]
    unknown = [k for k in flags if k not in catalog]
    if unknown:
        raise ValueError(f"unknown_check_items:{check_id}:{','.join(sorted(unknown))}")
    items = tuple(
        TooGoodChecklistItem(
            item_id=item_id,
            state="found" if flags.get(item_id) is False
            else ("cleared" if flags.get(item_id) is True else "inconclusive"),
        )
        for item_id in catalog
    )
    if any(item.state == "found" for item in items):
        conclusion = "found"
    elif any(item.state == "inconclusive" for item in items):
        conclusion = "inconclusive"
    else:
        conclusion = "cleared"
    return CheckConclusion(check_id=check_id, conclusion=conclusion, items=items, notes=tuple(notes))


@dataclass(frozen=True)
class ExitRoute:
    """三出口路由建议（裁定权=评估者会话，本件只产建议+归因留痕）。"""

    recommended_exit: str | None   # E1/E2/E3；None=三查全 cleared 无需走出口
    attribution: str | None
    rationale: str


def route_exit(conclusions: Mapping[str, CheckConclusion]) -> ExitRoute:
    """三出口流转建议（确定性映射，DESIGN §2.5 三出口表）::

        leakage found       → E1（可修复泄漏唯一出路=改考场重跑，新 experiment_id）
        luck_or_gaming found → E3（驳回+归因 luck_or_gaming→阴性库）
        hidden_risk found    → E2（接受但加监控：L6 顶格 3 个月+回切收紧两档+月度体检）
        仅 inconclusive      → E2（证据不足不硬判，加监控观察——诚实条款的出口形态）
        全 cleared           → None（正常流转，不走 anomalous 出口）
    """
    by_id = {cid: conclusions.get(cid) for cid in CHECK_IDS}
    if by_id["leakage"] is not None and by_id["leakage"].conclusion == "found":
        return ExitRoute("E1", "leakage", "发现泄漏：可修复泄漏唯一出路=换考卷/种子/数据窗重考(E1)")
    if by_id["luck_or_gaming"] is not None and by_id["luck_or_gaming"].conclusion == "found":
        return ExitRoute("E3", "luck_or_gaming", "查实运气/钻营：驳回 rejected_too_good 入阴性库(E3)")
    if by_id["hidden_risk"] is not None and by_id["hidden_risk"].conclusion == "found":
        return ExitRoute("E2", "hidden_risk", "隐性风险（卖保险形态/参数脆弱）：接受但加监控(E2)")
    if any(c is not None and c.conclusion == "inconclusive" for c in by_id.values()):
        return ExitRoute("E2", None, "三查存在证据不足项：不硬判，接受但加监控(E2)——诚实条款")
    return ExitRoute(None, None, "三查全 cleared：无反常，正常流转")
