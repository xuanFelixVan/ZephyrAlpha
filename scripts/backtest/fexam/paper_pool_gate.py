# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | paper池进池判据门（裁定#489③）
# [MODULE] scripts.backtest.fexam.paper_pool_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.simulation.deflated_sharpe_calculator（DSR/剪发/erfcinv 全仓唯一真源，禁重写第二份公式）
# [CONSUMERS] campaign_report.py（进池建议接线点）; 后续重考批次进池环节
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 判据=裁定#489③冻结v1（IC>0.02/ICIR>0.3/retain≥0.5 三线AND + 进池环节叠Bonferroni/DSR聚合层校正 + v1临时·3个月paper实测回调）；
#              DSR/剪发数学一律委托 zephyr.simulation.deflated_sharpe_calculator（SSOT），本件零公式只有判据组合；
#              退化态fail-closed（DSR degenerate/矩不可估/非有限输入=不进池，禁把"判不了"翻译成"放行"）；
#              num_candidates=聚合层校正试验数须如实（Bailey-LdP：未披露试验数的回测一文不值；默认=分数册内实测候选数）；
#              本模块只做进池判定，禁改单指标考试本身（ic_exam.judge 三态判定不受影响——分工边界）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] num_candidates<1/非int、n_obs<2、method 非法 → SimulationError 上抛（fail-closed）；
#                  非有限 ic/icir/retain → 不抛、判不进池并带 reason（"成绩非法"是合法测量结果）
# [TESTS] tests/backtest/fexam/test_paper_pool_gate.py
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（v1 判据冻结=裁定#489③，改动须新裁定）
# [TTL] permanent
# create-guard-not-dup: paper池进池判据门（裁定#489③护栏落地）——factor_pool_manager 管活跃池内生命周期替换、
#                       bhy_fdr/decay_monitor 管 registry 入池 FDR 门禁，均非 paper 池进池判据组合；DSR 数学全委托 SSOT
"""paper_pool_gate — paper 池进池判据门（裁定#489③：及格线 v1 冻结 + 聚合层校正护栏）。

裁定#489③（2026-10-07，真源=docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml）::

    【③及格线 v1】IC>0.02/ICIR>0.3/retain≥0.5 冻结为 v1；护栏两条：进池环节叠
    Bonferroni/DSR 多重检验校正（143 候选×运气=必然假阳，单指标阈值挡不住聚合层）；
    v1 定位临时，3 个月 paper 池实测命中率回调。

分工边界（进池环节 ≠ 考试环节）：ic_exam.judge 三态机判（考试层）不动——本门在其后，
只对"考试 pass 候选"做进池再判；单指标过线只证明窗内表现（prereg lookahead_note），
聚合层校正后才构成进池建议，进池≠上线（晋升另走门）。

复用面（全仓 DSR 唯一真源 zephyr.simulation.deflated_sharpe_calculator，本件零数学公式）：
- Bonferroni 硬门 + 剪发读数 → ``haircut_sharpe_harvey_liu(method="bonferroni")``：
  t_single = ICIR·√T（均值 IC>0 的 t 统计量，与 SR·√T 同构），剪发后 ICIR=选择效应扣除读数
- DSR 概率面 → 摘要矩路径 ``deflated_sharpe_from_moments``（分数册只有 ic_mean/icir/n_obs
  摘要时）/ 全序列路径 ``DeflatedSharpeCalculator.calculate``（有原始 IC 序列时，矩自估最忠实）
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from zephyr.simulation.deflated_sharpe_calculator import (
    DSR_SIGNIFICANCE_THRESHOLD,
    DSR_UNDECIDABLE,
    DeflatedSharpeCalculator,
    SimulationError,
    deflated_sharpe_from_moments,
    haircut_sharpe_harvey_liu,
)

#: 裁定#489③ 冻结 v1 三线（与 roster.PREREG_V1["factor_pass_line"] 同值——单测交叉核对防漂移；
#: 比较语义对齐 ic_exam.judge 既有实现：|ic|>=线 且 icir>=线 且 retain>=线）
PAPER_POOL_PASS_LINE: dict[str, float] = {
    "abs_ic_min": 0.02,
    "icir_min": 0.3,
    "ic_retain_min": 0.5,
}

#: Bonferroni 家族错误率 alpha（聚合层校正硬门；非 #489③ 冻结项，参数化留 Owner 调节位）
BONFERRONI_ALPHA: float = 0.05

#: 校正方法闭合集（"both"=默认 fail-closed 最严：Bonferroni 与 DSR 双过才进池）
CORRECTION_METHODS: tuple[str, ...] = ("bonferroni", "dsr", "both")
DEFAULT_METHOD = "both"

_RULING_REF = "裁定#489③"


@dataclass(frozen=True)
class PaperPoolGateResult:
    """单对象进池判定回执（frozen，全字段可落册审计）。"""

    object_id: str
    decision: bool  # True=进池建议（三线AND + 所选校正全过）
    three_lines_pass: bool
    bonferroni_pass: bool | None  # method 不含 bonferroni 时为 None
    dsr_pass: bool | None  # method 不含 dsr 时为 None
    dsr: float
    dsr_degenerate: bool
    p_single: float | None
    p_bonferroni: float | None
    t_single: float | None
    haircut_fraction: float | None
    corrected_icir: float | None  # 剪发后 ICIR（选择效应扣除读数）
    num_candidates: int
    n_obs: int
    reasons: tuple[str, ...] = field(default_factory=tuple)
    ruling_ref: str = _RULING_REF


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def three_lines_and(
    *,
    ic: float,
    icir: float,
    retain: float,
    pass_line: dict[str, float] | None = None,
) -> tuple[bool, list[str]]:
    """三线 AND 判定（裁定#489③ 冻结 v1；比较语义对齐 ic_exam.judge 既有实现）。

    入参为**方向调整后**的有效值（direction=short 的对象由调用方先取负，同 ic_exam.judge）。

    Returns:
        (是否三线全过, 逐线明细 reasons——失败线带实测值与线值，全过时为 ["三线全过"])
    """
    line = dict(PAPER_POOL_PASS_LINE if pass_line is None else pass_line)
    ic_min = float(line["abs_ic_min"])
    icir_min = float(line["icir_min"])
    retain_min = float(line["ic_retain_min"])
    reasons: list[str] = []
    ok = True
    if not _finite(ic):
        ok = False
        reasons.append(f"ic 非有限: {ic!r}（线 |ic|>={ic_min}）")
    elif abs(float(ic)) < ic_min:
        ok = False
        reasons.append(f"|ic|={abs(float(ic)):.4f}<线{ic_min}")
    if not _finite(icir):
        ok = False
        reasons.append(f"icir 非有限: {icir!r}（线 icir>={icir_min}）")
    elif float(icir) < icir_min:
        ok = False
        reasons.append(f"icir={float(icir):.4f}<线{icir_min}")
    if not _finite(retain):
        ok = False
        reasons.append(f"retain 非有限: {retain!r}（线 retain>={retain_min}）")
    elif float(retain) < retain_min:
        ok = False
        reasons.append(f"retain={float(retain):.4f}<线{retain_min}")
    if ok:
        reasons = ["三线全过"]
    return ok, reasons


def aggregate_correction(
    *,
    icir: float,
    n_obs: int,
    num_candidates: int,
    method: str = DEFAULT_METHOD,
) -> dict[str, Any]:
    """聚合层 Bonferroni/DSR 多重检验校正（裁定#489③ 护栏；数学全委托 DSR SSOT）。

    校正对象 = "均值 IC>0" 的 t 统计量 ``t_single = ICIR·√T``（T=n_obs 为 IC 序列样本数）。
    num_candidates = 本批应考候选数（聚合层试验数 N，如实披露，默认调用方给分数册实测数）：
    N 名候选里挑最好，单指标阈值挡不住"运气过线"——Bonferroni 把家族错误率压回 alpha，
    DSR 把 E[max(Z_N)] 期望最大值从 z 里扣掉（Bailey & López de Prado 2014）。

    DSR 走摘要矩路径（γ=κ超额=0 缺省：分数册只落 ic_mean/icir/n_obs 摘要，IC 序列近正态
    是一阶近似）；有原始 IC 序列时用 ``dsr_from_ic_series``（矩自估，更忠实）。

    Fail-closed：DSR 退化态（V[SR] 非正等）→ dsr_pass=False 且 dsr_degenerate=True
    （"判不了"绝不翻译成"放行"，对齐 SDC-4）。

    Raises:
        SimulationError: num_candidates 非 int 或 <1 / n_obs<2 / icir 非有限 / method 非法。
    """
    if not isinstance(num_candidates, int) or isinstance(num_candidates, bool) or num_candidates < 1:
        raise SimulationError(
            f"num_candidates 必须 int>=1（聚合层试验数如实披露）, 收到 {num_candidates!r}",
            details={"num_candidates": num_candidates},
        )
    if not isinstance(n_obs, int) or isinstance(n_obs, bool) or n_obs < 2:
        raise SimulationError(f"n_obs 必须 int>=2（t 统计量可估下限）, 收到 {n_obs!r}", details={"n_obs": n_obs})
    if not _finite(icir):
        raise SimulationError(f"icir 非有限: {icir!r}", details={"icir": icir})
    if method not in CORRECTION_METHODS:
        raise SimulationError(f"method 非法 {method!r}（合法集={CORRECTION_METHODS}）", details={"method": method})

    icir_f = float(icir)
    # 剪发机器（SSOT 复用）：t_single=ICIR·√T 与 SR·√T 同构；erfcinv 远尾精度随件继承
    hc = haircut_sharpe_harvey_liu(sharpe=icir_f, num_trials=num_candidates, num_obs=n_obs, method="bonferroni")
    # 两端 p 值走 erfc（无消去，与 SSOT 同一精度路径）；Bonferroni 家族错误率 = min(1, p·N)
    p_single = math.erfc(abs(hc.t_stat_single) / math.sqrt(2.0))
    p_bonferroni = min(1.0, p_single * float(num_candidates))
    bonferroni_pass = p_bonferroni < BONFERRONI_ALPHA

    out: dict[str, Any] = {
        "method": method,
        "num_candidates": int(num_candidates),
        "n_obs": int(n_obs),
        "icir": icir_f,
        "t_single": hc.t_stat_single,
        "p_single": p_single,
        "p_bonferroni": p_bonferroni,
        "bonferroni_pass": bonferroni_pass,
        "haircut_fraction": hc.haircut_fraction,
        "corrected_icir": hc.haircut_sharpe,
        "alpha": BONFERRONI_ALPHA,
        "ruling_ref": _RULING_REF,
    }
    if method == "bonferroni":
        out.update({"dsr": None, "dsr_pass": None, "dsr_degenerate": False})
        return out

    _, dsr, _expected_max, degenerate = deflated_sharpe_from_moments(
        icir_f, num_candidates, n_obs, skewness=0.0, excess_kurtosis=0.0
    )
    dsr_pass = bool(not degenerate and dsr >= DSR_SIGNIFICANCE_THRESHOLD)
    out.update({"dsr": float(dsr), "dsr_pass": dsr_pass, "dsr_degenerate": bool(degenerate)})
    return out


def dsr_from_ic_series(ic_series: Sequence[float], *, num_candidates: int) -> dict[str, Any]:
    """全序列 DSR 路径：原始 IC 序列直喂 DSR 计算器（矩自估，最忠实）。

    有原始 IC 序列的调用方（重考集成/在线进池）优先走本路径；
    分数册摘要场景走 ``aggregate_correction``（矩缺省路径）。

    Fail-closed：样本 <3 / 零方差 → degenerate=True、dsr=DSR_UNDECIDABLE、不判显著
    （DSR 计算器对 <3 抛 SimulationError，此处按"判不了"收敛为退化态而非外抛——
    进池门语义里"样本不足"是候选的属性不是调用方的错误）。

    Raises:
        SimulationError: num_candidates 非 int 或 <1。
    """
    if not isinstance(num_candidates, int) or isinstance(num_candidates, bool) or num_candidates < 1:
        raise SimulationError(
            f"num_candidates 必须 int>=1, 收到 {num_candidates!r}", details={"num_candidates": num_candidates}
        )
    series = [float(x) for x in ic_series]
    if len(series) < 3 or not all(math.isfinite(x) for x in series):
        return {"dsr": DSR_UNDECIDABLE, "dsr_degenerate": True, "dsr_pass": False, "n_obs": len(series)}
    result = DeflatedSharpeCalculator().calculate(series, num_trials=num_candidates)
    return {
        "dsr": float(result.dsr),
        "dsr_degenerate": bool(result.degenerate),
        "dsr_pass": bool(result.is_significant),
        "n_obs": int(result.num_obs),
    }


def paper_pool_entry(
    *,
    ic: float,
    icir: float,
    retain: float,
    n_obs: int,
    num_candidates: int,
    object_id: str = "",
    method: str = DEFAULT_METHOD,
    pass_line: dict[str, float] | None = None,
    ic_series: Sequence[float] | None = None,
) -> PaperPoolGateResult:
    """单对象 paper 池进池判定（裁定#489③：三线 AND + 聚合层校正）。

    Args:
        ic/icir/retain: 方向调整后的有效值（direction=short 先取负，同 ic_exam.judge 口径）
        n_obs: HOLDOUT 窗 IC 序列样本数
        num_candidates: 本批应考候选数（聚合层校正试验数 N，如实）
        method: "both"（默认，双校正全过）| "bonferroni" | "dsr"
        pass_line: 缺省用冻结 v1 三线（PAPER_POOL_PASS_LINE）
        ic_series: 原始 IC 序列（可选；给了就走全序列 DSR 路径，矩自估）

    Returns:
        PaperPoolGateResult（frozen，decision/逐项 pass/逐线 reasons 全可落册）

    Raises:
        SimulationError: num_candidates 非 int 或 <1 / n_obs 非 int 或 <2 / method 非法
        （经 aggregate_correction 统一校验；非有限 ic/icir/retain 不抛——见 ERROR_CONTRACT）。
    """
    if method not in CORRECTION_METHODS:
        raise SimulationError(f"method 非法 {method!r}（合法集={CORRECTION_METHODS}）", details={"method": method})
    if not isinstance(num_candidates, int) or isinstance(num_candidates, bool) or num_candidates < 1:
        raise SimulationError(
            f"num_candidates 必须 int>=1, 收到 {num_candidates!r}", details={"num_candidates": num_candidates}
        )
    if not isinstance(n_obs, int) or isinstance(n_obs, bool) or n_obs < 2:
        raise SimulationError(f"n_obs 必须 int>=2, 收到 {n_obs!r}", details={"n_obs": n_obs})
    lines_ok, reasons = three_lines_and(ic=ic, icir=icir, retain=retain, pass_line=pass_line)
    corr: dict[str, Any]
    if not _finite(icir) or not _finite(retain) or not _finite(ic):
        # 非有限输入：三线已 fail；校正层无合法输入可算——fail-closed 不抛（ERROR_CONTRACT）
        corr = {
            "method": method,
            "num_candidates": int(num_candidates) if _finite(num_candidates) else -1,
            "n_obs": int(n_obs) if _finite(n_obs) else -1,
            "bonferroni_pass": False,
            "dsr_pass": False,
            "dsr": DSR_UNDECIDABLE,
            "dsr_degenerate": True,
            "p_single": None,
            "p_bonferroni": None,
            "t_single": None,
            "haircut_fraction": None,
            "corrected_icir": None,
        }
    else:
        corr = aggregate_correction(
            icir=float(icir), n_obs=int(n_obs), num_candidates=int(num_candidates), method=method
        )
        if ic_series is not None and method in ("dsr", "both"):
            series_res = dsr_from_ic_series(ic_series, num_candidates=int(num_candidates))
            corr["dsr"] = series_res["dsr"]
            corr["dsr_pass"] = series_res["dsr_pass"]
            corr["dsr_degenerate"] = series_res["dsr_degenerate"]
            reasons.append(f"DSR 走全序列路径（T={series_res['n_obs']}）")

    checks = [lines_ok]
    if corr.get("bonferroni_pass") is not None:
        checks.append(bool(corr["bonferroni_pass"]))
        if not corr["bonferroni_pass"]:
            if corr.get("p_bonferroni") is not None:
                reasons.append(
                    f"Bonferroni 不过: p_mult={corr['p_bonferroni']:.3g}>=alpha{BONFERRONI_ALPHA}"
                    f"（N={corr['num_candidates']} 候选聚合层运气折减）"
                )
            else:
                reasons.append("Bonferroni 不过: 校正层输入非法（非有限 ic/icir/retain，fail-closed 不出 p 值）")
    if corr.get("dsr_pass") is not None:
        checks.append(bool(corr["dsr_pass"]))
        if not corr["dsr_pass"]:
            tag = "退化态不可判定" if corr.get("dsr_degenerate") else "未达显著性线"
            reasons.append(f"DSR 不过({tag}): dsr={corr['dsr']:.4f}")
    decision = all(checks) and int(num_candidates) >= 1 and int(n_obs) >= 2
    return PaperPoolGateResult(
        object_id=str(object_id),
        decision=bool(decision),
        three_lines_pass=bool(lines_ok),
        bonferroni_pass=corr.get("bonferroni_pass"),
        dsr_pass=corr.get("dsr_pass"),
        dsr=float(corr.get("dsr") or 0.0),
        dsr_degenerate=bool(corr.get("dsr_degenerate")),
        p_single=corr.get("p_single"),
        p_bonferroni=corr.get("p_bonferroni"),
        t_single=corr.get("t_single"),
        haircut_fraction=corr.get("haircut_fraction"),
        corrected_icir=corr.get("corrected_icir"),
        num_candidates=int(corr.get("num_candidates") or 0),
        n_obs=int(corr.get("n_obs") or 0),
        reasons=tuple(reasons),
    )


def paper_pool_from_factor_book(
    book: dict[str, Any],
    *,
    method: str = DEFAULT_METHOD,
    num_candidates: int | None = None,
) -> dict[str, Any]:
    """批1因子分数册 → paper 池进池建议单（机生；campaign_report 进池环节接线用）。

    只对 verdict=="pass" 的候选再判（考试层三态不动）；num_candidates 缺省=册内实测
    候选数（有 headline 度量者，含 rework——聚合层 N 应如实覆盖全部应试试探）。
    判定输入=方向调整后 headline holdout 摘要（ic_mean/icir/n_obs/retain，同 judge 口径）。

    Fail-closed：pass 但 metrics 缺失/不可判 → 不进池并留痕（禁把"没数据"当"过线"）。
    """
    results = book.get("results") or []
    horizon = str((book.get("prereg_v1") or {}).get("headline_horizon", 5))
    measured_n = sum(1 for r in results if ((r.get("metrics") or {}).get("per_horizon") or {}).get(horizon))
    if num_candidates is None:
        num_candidates = measured_n
    admitted: list[str] = []
    rejected: list[dict[str, Any]] = []
    for r in results:
        if r.get("verdict") != "pass":
            continue
        oid = str(r.get("object_id") or "")
        ph = ((r.get("metrics") or {}).get("per_horizon") or {}).get(horizon) or {}
        holdout = ph.get("holdout") or {}
        ic_raw = holdout.get("ic_mean")
        icir_raw = holdout.get("icir")
        retain = ph.get("retain")
        n_obs = holdout.get("n_obs")
        if ic_raw is None or icir_raw is None or retain is None or not _finite(n_obs) or int(n_obs) < 2:
            rejected.append({"object_id": oid, "reasons": ("pass 但 headline 度量缺失/不可判——fail-closed 不进池",)})
            continue
        direction = r.get("direction")
        sign = -1.0 if str(direction).lower() == "short" else 1.0
        gate = paper_pool_entry(
            ic=sign * float(ic_raw),
            icir=sign * float(icir_raw),
            retain=float(retain),
            n_obs=int(n_obs),
            num_candidates=int(num_candidates),
            object_id=oid,
            method=method,
        )
        if gate.decision:
            admitted.append(oid)
        else:
            rejected.append({"object_id": oid, "reasons": gate.reasons})
    return {
        "doc_type": "fexam_paper_pool_gate",
        "ruling_ref": _RULING_REF,
        "method": method,
        "num_candidates": int(num_candidates),
        "measured_candidates": measured_n,
        "alpha": BONFERRONI_ALPHA,
        "pass_line": dict(PAPER_POOL_PASS_LINE),
        "exam_pass_total": sum(1 for r in results if r.get("verdict") == "pass"),
        "admitted": admitted,
        "rejected": rejected,
        "note": "进池≠上线（晋升另走门）；v1 临时——3 个月 paper 池实测命中率回调（裁定#489③）",
    }


__all__ = [
    "BONFERRONI_ALPHA",
    "CORRECTION_METHODS",
    "DEFAULT_METHOD",
    "PAPER_POOL_PASS_LINE",
    "PaperPoolGateResult",
    "aggregate_correction",
    "dsr_from_ic_series",
    "paper_pool_entry",
    "paper_pool_from_factor_book",
    "three_lines_and",
]
