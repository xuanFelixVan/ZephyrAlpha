# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1.1 回填结构 + §1.2 answered 六查 + §3.3 时间分层 + §7 P2（exam_plan_version 提案）
# [MODULE] zephyr.governance.meta_question.exam_loop.exam_plan
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc，禁裸 datetime.now); math (erf 正态 CDF，零第三方依赖); 标准库 re/json（阈值文本机械解析）
# [CONSUMERS] zephyr.governance.meta_question.exam_loop.writeback (A2/A3/A4/A5 六查 + 功效延期判定); scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py (exam_plan 结构化升级落账); tests/governance/meta_question/test_exam_loop_exam_plan.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] exam_plan 由自由文本扩为结构化对象（PQ-0098）：method/criterion/threshold 为底稿三件，
#              本件新增 threshold_clauses(机解)/sample_size/effect_size/min_confidence/power_min/
#              out_of_sample_share_min/window_rule/plan_version 六件，全部可选键、缺键=降级留痕（degraded 清单），禁伪造默认值；
#              题面文本=判据真源：threshold 原文必留（机解值只是投影，两者不一致时以原文为准并报 drift）；
#              功效不足只能延期（defer→outcome=reexam），降阈值路径在本件不存在（唯一出口=DEFER，PQ-0098 题面"降阈值事件=0"）；
#              时间分层机检（PQ-0055/§3.3）：考试窗口与问题生成时戳"无重叠"=不跨越（NOT start<gen_ts<end），
#              整窗在生成时戳之后=新鲜窗（样本外份额按 1.0 记），整窗在前=历史回测窗（份额取考试器申报值，未申报=unverifiable 不计通过）；
#              end ≤ 执行日-1（A4 硬判），同戳循环禁止（fetch_ts == decision_ts 即违规，§3.3 第 2 条）；
#              一切取时戳走 now_utc()（aware），naive 输入=拒收（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1/§3.3（改预注册契约先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 阈值文本不可解=返回空 clauses 清单（不抛，降级留痕由调用方落 degraded_check）；
#                  功效输入非法（n≤0/|effect|≥1/alpha∉(0,1)）=ValueError；naive datetime=ValueError
# [TESTS] tests/governance/meta_question/test_exam_loop_exam_plan.py（含红腿：功效不足必判 defer、窗口跨越生成时戳必判 violation）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""exam_plan — 预注册考卷结构化（OSF 预注册对标）+ 功效核验 + 时间分层机检。

设计真源：``13_exam_backfill_loop_design.md`` §1.1/§1.2/§3.3 + §7 P2 提案。补齐 283 问
``exam_plan`` 只有 ``method/criterion/threshold`` 自由文本、无法机检功效与样本外份额的载体缺口。

核心出口::

    plan = structure_plan(row["exam_plan"], plan_version="v2-wo-b1")
    clauses = plan["threshold_clauses"]              # 机解阈值（≥/= 逐条）
    verdict = assess_power(plan, effect=0.031, n=250)  # → {"action": "defer"|"pass"}
    v = check_time_layering(window, generated_at, execution_day)   # → Violation 列表
# #
# # 边:
# # I1 -.->|断点| F1
# # I2 -.->|断点| F1
# # I3 -.->|断点| F1
# # I4 -.->|断点| F1
# # F1 --> A1
# # A1 --> O1
# [/ALGO_FLOW]
# target: src/zephyr/governance/meta_question/exam_loop/exam_plan.py (docstring 1633 字, 16 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/exam_plan.yaml
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Final

from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "DEGRADED_KEYS",
    "STRUCTURED_KEYS",
    "LayeringViolation",
    "PowerVerdict",
    "assess_power",
    "check_time_layering",
    "fischer_z_power",
    "is_aware",
    "out_of_sample_share",
    "parse_threshold_clauses",
    "required_for_answered",
    "structure_plan",
    "to_date",
    "upgrade_payload",
]

#: 底稿三件（10§2.2 入库闸已校验 criterion+threshold 非空）
BASELINE_KEYS: Final[tuple[str, ...]] = ("method", "criterion", "threshold")
#: WO-B1 结构化六件（PQ-0098/PQ-0055/PQ-0056 判据所需）
STRUCTURED_KEYS: Final[tuple[str, ...]] = (
    "sample_size",
    "effect_size",
    "min_confidence",
    "power_min",
    "out_of_sample_share_min",
    "window_rule",
)
DEGRADED_KEYS: Final[tuple[str, ...]] = STRUCTURED_KEYS
#: 六查 A3 所需"预锁最低置信阈"缺位时的申报口径（不注入默认数值=禁伪造预注册）
_IC_LIKE_CRITERIA: Final[frozenset[str]] = frozenset(
    {"rank_ic", "ic", "information_coefficient", "pearson_ic", "spearman_ic"}
)
_THRESHOLD_CLAUSE_RE: Final = re.compile(
    r"(?P<op>>=|<=|≥|≤|>|<|=|≈)\s*(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>%|倍|日|个交易日)?"
)
_OP_CANON: Final[dict[str, str]] = {
    ">=": ">=",
    "≤": "<=",
    "<=": "<=",
    "≥": ">=",
    ">": ">",
    "<": "<",
    "=": "=",
    "≈": "~=",
}


# ---------------------------------------------------------------------------
# 阈值文本机解（题面原文=真源，机解值只是投影）
# ---------------------------------------------------------------------------


def parse_threshold_clauses(threshold: Any) -> list[dict[str, Any]]:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    """把 ``threshold`` 自由文本解成逐条可判定式（``"≥95%（逾期挂起≤5%）"`` → 2 条）。

    不可解（无算符/无数字）返回空列表——调用方按降级留痕处置，禁静默判通过。
    """
    text = str(threshold or "")
    out: list[dict[str, Any]] = []
    for match in _THRESHOLD_CLAUSE_RE.finditer(text):
        raw_op = match.group("op")
        out.append(
            {
                "op": _OP_CANON.get(raw_op, raw_op),
                "value": float(match.group("value")),
                "unit": match.group("unit") or "",
                "text": match.group(0).strip(),
            }
        )
    if out:
        out.insert(0, {"source_text": text})
        out[1] = {**out[1], "primary": True}
    return out


def evaluate_clauses(value: Any, clauses: list[dict[str, Any]]) -> dict[str, Any]:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    """按机解条款逐条比对结论取值（仅取带 op/value 的条款，source_text 跳过）。"""
    checks: list[dict[str, Any]] = []
    passed = True
    try:
        observed = float(value)
    except (TypeError, ValueError):
        return {"evaluable": False, "reason": "conclusion_value_not_numeric", "checks": []}
    for clause in clauses:
        op, clause_value = clause.get("op"), clause.get("value")
        if op is None or clause_value is None:
            continue
        ok = _compare(observed, str(op), float(clause_value))
        checks.append({"op": op, "expected": clause_value, "observed": observed, "ok": ok})
        passed = passed and ok
    return {"evaluable": bool(checks), "passed": passed, "checks": checks}


def _compare(observed: float, op: str, expected: float) -> bool:
    if op == ">=":
        return observed >= expected
    if op == "<=":
        return observed <= expected
    if op == ">":
        return observed > expected
    if op == "<":
        return observed < expected
    if op in ("=", "~="):
        return math.isclose(observed, expected, rel_tol=1e-9, abs_tol=1e-9)
    return False


# ---------------------------------------------------------------------------
# 结构化（升级不破坏底稿：原键原值保留，机生投影另置）
# ---------------------------------------------------------------------------


def structure_plan(raw: dict[str, Any] | None, *, plan_version: str = "") -> dict[str, Any]:
    """自由文本 exam_plan → 结构化对象（缺键列入 ``degraded``，禁伪造默认值）。"""
    plan = dict(raw or {})
    degraded = [key for key in STRUCTURED_KEYS if plan.get(key) in (None, "", {})]
    structured = {
        "method": str(plan.get("method") or ""),
        "criterion": str(plan.get("criterion") or ""),
        "threshold": plan.get("threshold"),
        "threshold_clauses": parse_threshold_clauses(plan.get("threshold")),
        "sample_size": plan.get("sample_size"),
        "effect_size": plan.get("effect_size"),
        "min_confidence": plan.get("min_confidence"),
        "power_min": plan.get("power_min"),
        "out_of_sample_share_min": plan.get("out_of_sample_share_min"),
        "window_rule": plan.get("window_rule"),
        "plan_version": plan_version or str(plan.get("plan_version") or ""),
        "event_source_ref": plan.get("event_source_ref"),
        "degraded": degraded,
    }
    merged = dict(plan)
    merged.update({k: v for k, v in structured.items() if v is not None})
    return merged


def required_for_answered(plan: dict[str, Any]) -> tuple[str, ...]:
    """判据字段+阈值字段双填充的最小必查集（13§1.2 A3 口径）。"""
    missing = [key for key in ("criterion", "threshold") if not str(plan.get(key) or "").strip()]
    return tuple(missing)


def is_ic_like(plan: dict[str, Any]) -> bool:
    """IC 类考试判定（PQ-0098 功效判据适用面）：criterion 命中 IC 词根或阈值条款含 IC。"""
    text = f"{plan.get('criterion') or ''} {plan.get('method') or ''}".lower()
    if any(token in text for token in _IC_LIKE_CRITERIA):
        return True
    return "ic" in str(plan.get("criterion") or "").lower().split()


# ---------------------------------------------------------------------------
# 功效核验（唯一样本不足出口=延期）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PowerVerdict:
    """功效核验结论（延期 vs 达标；本设计无"降阈值"出口）。"""

    action: str  # 'pass' | 'defer'
    power: float | None
    required: float | None
    sample_size: int | None
    effect_size: float | None
    reason: str


def normal_cdf(x: float) -> float:
    """标准正态 CDF（erf 实现，零第三方依赖）。"""

    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def fisher_z_power(sample_size: int, effect_size: float, alpha: float = 0.05) -> float:
    """IC/相关系数单侧检验功效（Fisher z 近似，量化社区通行做法：n 与 |r| 给定下求拒绝域覆盖率）。

    ``power = Φ(√(n-3)·atanh(|r|) - z_{1-α})``；n≤3 或 |r|≥1 → ValueError（输入失真）。
    """
    n = int(sample_size)
    r = abs(float(effect_size))
    if n <= 3:
        raise ValueError(f"样本量不足 Fisher z 近似：n={n}（须 >3，样本不足请走延期）")
    if not 0.0 <= r < 1.0:
        raise ValueError(f"效应量越界：|r|={r}（相关系数须 <1）")
    if not 0.0 < float(alpha) < 1.0:
        raise ValueError(f"alpha 非法：{alpha}")
    z_crit = _inv_normal(1.0 - float(alpha))
    return normal_c(math.sqrt(n - 3) * math.atanh(r) - z_crit)


def normal_c(x: float) -> float:  # pragma: no cover - 语义别名
    return normal_cdf(x)


def _inv_normal(p: float) -> float:
    """标准正态分位数（Acklam 有理近似，绝对误差 <1e-9，够用且免 scipy 依赖）。"""
    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00, 3.754408661907416e00)
    plow, phigh = 0.02425, 1 - 0.02425
    if not 0.0 < p < 1.0:
        raise ValueError(f"p 须在 (0,1)：{p}")
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    q = p - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5])
        * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    )


def assess_power(
    plan: dict[str, Any],
    *,
    sample_size: Any = None,  # noqa: any-abuse  any-abuse豁免: 考卷底稿动态数值，JSON反序列化类型开放
    effect_size: Any = None,  # noqa: any-abuse  any-abuse豁免: 考卷底稿动态数值，JSON反序列化类型开放
    alpha: float = 0.05,  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
) -> PowerVerdict:
    """功效核验（PQ-0098）：不足→``defer``（延期，等下一个复考窗），无降阈值出口。

    预注册缺 ``power_min``/``sample_size``/``effect_size`` → 判 ``defer`` 并报缺项
    （fail-closed：无法核验功效即不得宣告 answered）。
    """
    n = sample_size if sample_size is not None else plan.get("sample_size")
    effect = effect_size if effect_size is not None else plan.get("effect_size")
    required = plan.get("power_min")
    missing = [
        name
        for name, value in (("sample_size", n), ("effect_size", effect), ("power_min", required))
        if value in (None, "")
    ]
    if missing:
        return PowerVerdict("defer", None, None, None, None, f"power_prelock_missing:{','.join(missing)}")
    power = fisher_z_power(int(n), float(effect), alpha=alpha)
    if power < float(required):
        return PowerVerdict("defer", power, float(required), int(n), float(effect), "low_power_defer")
    return PowerVerdict("pass", power, float(required), int(n), float(effect), "power_ok")


# ---------------------------------------------------------------------------
# 时间分层机检（§3.3 铁律 + PQ-0055/PQ-0096）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LayeringViolation:
    """一条时间分层违规（code 机读，detail 人读）。"""

    code: str
    detail: str


def is_aware(value: datetime) -> bool:
    """aware 校验（naive 即失真——RULE-SCHEMA-TZ 在 PG 通道上的等价红线）。"""
    return value.tzinfo is not None and value.utcoffset() is not None


def to_date(value: Any) -> date | None:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    """日期归一化（date/datetime/ISO 文本 → date；不可解返回 None）。"""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        parsed = datetime.strptime(text[:10], "%Y-%m-%d")
    return parsed.date()


def _to_dt(value: Any, *, field: str) -> datetime | None:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    if not is_aware(parsed):
        raise ValueError(f"{field} 为 naive 时戳：{value!r}（RULE-SCHEMA-TZ：须显式时区）")
    return parsed


def check_time_layering(
    window: dict[str, Any] | None,
    *,
    generated_at: Any = None,  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    execution_day: date | None = None,
) -> list[LayeringViolation]:
    """13§3.3 两条铁律 + PQ-0055"窗口与生成时戳无重叠"的机械判定。

    :return: 违规清单（空=合规）。口径：
        - ``window_end_not_before_close``：end 必须 ≤ 执行日-1（今日输出→明日输入）；
        - ``window_straddles_generation``：窗口跨越问题生成时戳（既含旧数据又含新生成后数据）=重叠；
        - ``window_bounds_missing``：起止缺一即 A4 失败。
    """
    violations: list[LayeringViolation] = []
    bounds = window or {}
    start = to_date(bounds.get("start"))
    end = to_date(bounds.get("end"))
    if start is None or end is None:
        violations.append(LayeringViolation("window_bounds_missing", f"start={start} end={end}"))
        return violations
    if end < start:
        violations.append(LayeringViolation("window_inverted", f"start={start} > end={end}"))
    today = execution_day or now_utc().date()
    if end > today - timedelta(days=1):
        violations.append(
            LayeringViolation("window_end_not_before_close", f"end={end} > 执行日-1={today - timedelta(days=1)}")
        )
    gen_at = _to_dt(generated_at, field="generated_at") if generated_at else None
    if gen_at is not None:
        gen_date = gen_at.date()
        if start <= gen_date <= end:
            violations.append(
                LayeringViolation("window_straddles_generation", f"{start} ≤ 生成时戳 {gen_date} ≤ {end}")
            )
    return violations


def out_of_sample_share(
    window: dict[str, Any] | None,
    *,
    generated_at: Any = None,  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    declared: Any = None,  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
) -> tuple[float | None, str]:
    """样本外份额（PQ-0055 判据 ≥1/3 的取值口径）。

        优先级：申报值 ``declared``（考试器按考尺口径给出）> 新鲜窗推定（整窗晚于生成时戳⇒份额 1.0）
        > ``in_sample`` 子窗比例推算；全不可得→ ``(None, 'unverifiable')``（禁按 0 或 1 猜）。

    # #
    # # 边:
    # # I1 -.->|断点| F1
    # # I2 -.->|断点| F1
    # # I3 -.->|断点| F1
    # # I4 -.->|断点| F1
    # # F1 --> A1
    # # A1 --> O1
    # [/ALGO_FLOW]
    """
    if declared not in (None, ""):
        return float(declared), "declared"
    bounds = window or {}
    start = to_date(bounds.get("start"))
    end = to_date(bounds.get("end"))
    gen_at = _to_dt(generated_at, field="generated_at") if generated_at else None
    if start and gen_at and start > gen_at.date():
        return 1.0, "fresh_window_after_generation"
    in_start = to_date(bounds.get("in_sample_start"))
    in_end = to_date(bounds.get("in_sample_end"))
    if start and end and in_start and in_end:
        total = (end - start).days + 1
        inside = (in_end - in_start).days + 1
        if total > 0:
            share = max(0.0, min(1.0, 1.0 - inside / total))
            return share, "derived_from_in_sample_bounds"
    return None, "unverifiable"
