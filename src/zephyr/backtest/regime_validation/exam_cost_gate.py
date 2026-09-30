# [BLUEPRINT] MOD-BT-IBT-COSTGATE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.exam_cost_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] scripts/backtest/f06_e4_wfa_exam.py（E4 正考档位扫描+换手门）；scripts/backtest/exam_cost_reexam.py（存活池重过成本门/批D 新鲜窗）；批F 三路搜索轨（F06Grid/E1C/LLM）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯函数零 IO 零重跑：净值档位序列由调用方注入（_c4_engine.daily_net_returns slippage_bp 档覆盖），本件只做判定；五档单调性=逐档 sharpe 非增（容差 tol）；全成本档存活=最高档 sharpe>=survival_floor；E7 换手上限门=年化单边换手<=cap（预注册默认 8x/年，Owner 通宵令批C 预注册档冻结后禁改）；规模调整存活门（裁-4 item5 2026-09-28）=participation_rate 显式传入时有效档 tiers[-1]×开方律乘数判 survival_floor（缺省 None=规模维禁用行为零变化，40bp 锚=ref 处 m=1 判定逐字一致）；fail-closed：证据缺失（档位<3/天数<min_days）判不通过非跳过，participation 非正=ValueError；裁定#325 口径：出证禁"全绿"，逐条如实判档；扫描/判定两面分离（2026-09-24 方案①）：run_cost_tier_scan tiers_bp 子集覆盖仅供 T1 轻档粗筛扫描（validate_scan_tiers 两档合法），三门判定仍恒全档证据（<3 档 fail-closed 不通过）；nets_by_tier 预算档注入（st-ddup-20260925）：缺省 None=逐档 net_fn 行为零变化，注入缺档=ValueError fail-closed
# [MODIFY-GUARD] tests/backtest/test_exam_cost_gate.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(配置非法：档位不含0/未升序/cap<=0/规模锚非正/规模律指数出界/乘数上限<1；participation 非正)；判定函数不抛异常（证据缺失=fail-closed 不通过）
# [TESTS] tests/backtest/test_exam_cost_gate.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-IBT-COSTGATE | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""E4 考尺成本门（批C 成本焊进考尺，Max 整改方案 §2-C；MOD-BT-IBT-COSTGATE）。

三门+可选规模维（预注册默认档冻结后禁改，参数面见 config/exam_scale_cost_gate.yaml）:
  1. 档位单调性: 五档滑点(0/5/10/20/40bp，冻结土规口径)下 sharpe 逐档非增
     （成本越高收益越低的市场常识=无前视套利的必要条件，首跑敏感性框架同款）;
  2. 全成本档存活: 最高档(40bp) sharpe >= survival_floor(预注册 0.0)——
     纸面亮实盘死的勤快策略在此现形;
  3. E7 换手上限门: 年化单边换手 <= turnover_cap_annual_x（预注册 8x/年，
     推导: 38.6pct/4.75 年 ÷39x ≈ 0.21pct/换手·年，8x→成本拖累 ≈1.7pct/年，
     OOS 零成本超额 +18pct 保留一半即过 C 门线）;
  4. 规模调整存活（裁-4 item5 2026-09-28，可选）: 调用方注入格点自身参与率
     （成交额/ADV）时，有效档=tiers[-1]×开方律乘数（(participation/5%ADV)^0.5，
     单边只罚不奖，上限 2×），档位曲线在该有效档取值判 survival_floor——
     旧门对成交规模恒盲（40bp 锚任何规模一刀切）=验收门恒过橡皮图章，本轮可 fail。
     participation<=锚 时 m=1，判定与缺省逐字一致=40bp 锚语义不动。

照妖镜语义: 4440（超短频繁交易）必须被本门拦截；E4 存活池重过产"成本合格名单"。
裁定#325 口径: 判定结果逐条如实（PASS/FAIL+数字证据），禁"全绿"表述。
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/exam_cost_gate.yaml
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final

import numpy as np
import pandas as pd

#: 预注册默认档（Owner 通宵令批C；冻结后禁改，调整=裁定通道）
DEFAULT_COST_TIERS_BP: tuple[float, ...] = (0.0, 5.0, 10.0, 20.0, 40.0)
DEFAULT_SURVIVAL_FLOOR: float = 0.0
DEFAULT_TURNOVER_CAP_ANNUAL_X: float = 8.0
DEFAULT_TURNOVER_DAYS_BASIS: int = 244
DEFAULT_MONOTONIC_TOL: float = 1e-9
#: 换手/单调性证据的最低样本天数（低于此 fail-closed 判不通过）
DEFAULT_MIN_DAYS: int = 60
#: 规模维（裁-4 item5 2026-09-28：成本档不带规模参数=验收门恒过/橡皮图章）——
#: 档位 bp 视为在参与率锚 scale_participation_ref 处校准（5% ADV 机构级分界）；
#: 开方律冲击模型（square_root，cost_model_registry impact_model 枚举既有，见 CST-ASTOCK-002）：
#: m=(participation/ref)^exponent，单边只罚不奖（participation<=ref 时 m=1，保 40bp 锚语义）；
#: 上限 cap 防测量档外无限外推（40bp 锚最深 2×=80bp 有效档）。
DEFAULT_SCALE_PARTICIPATION_REF: float = 0.05
DEFAULT_SCALE_EXPONENT: float = 0.5
DEFAULT_SCALE_MULTIPLIER_CAP: float = 2.0

__all__: Final = [
    "CostGateConfig",
    "CostGateVerdict",
    "validate_scan_tiers",
    "run_cost_tier_scan",
    "evaluate_exam_cost_gate",
    "cost_scale_multiplier",
    "BreakevenGateConfig",
    "BreakevenGateVerdict",
    "breakeven_cost_star_from_net_line",
    "solve_breakeven_cost_star",
    "evaluate_breakeven_cost_gate",
]

# ---------------------------------------------------------------------------
# ⚑-2② B案机器门 v2（G-COST-BREAKEVEN-40BP；裁定#435 声明通道落册件
# docs/_working/night_sweep/c_exam/flag2_declaration_b.md 的消费面）。
# 判据对象=盈亏平衡成本 c*（Sharpe(c)=0 的单边成本，逐格确定量，不抽样）；
# 五道门 P1-P5 + 三态 PASS/INDETERM/FAIL（禁二值，INDETERM 必须补数据/补跑）。
# 40bp 锚与"Sharpe≥0"语义一字不动；v1 三门判定（上方 evaluate_exam_cost_gate）
# 保留原样=回退面（config/exam_scale_cost_gate.yaml cost_gate_active 指针缺席时行为零变化）。
DEFAULT_BREAKEVEN_REF_BP: Final[float] = 5.0  # 引擎冻结土规缺省滑点档（_c4_engine.SLIPPAGE_BP 同源）
DEFAULT_BREAKEVEN_HI_BP: Final[float] = 200.0
DEFAULT_BREAKEVEN_OVER_LABEL: Final[str] = ">200"
DEFAULT_P3_RATIO_MIN: Final[float] = 0.80
DEFAULT_P3_LAYER_MIN_N: Final[int] = 30
DEFAULT_P4_SCALE_SENSITIVITY_MAX: Final[float] = 0.20
#: P5 成绩单必含四字段（案卷 S-05：缺一即尺红）
P5_REQUIRED_FIELDS: Final[tuple[str, ...]] = ("adjustment_basis", "snapshot_date", "snapshot_sha256", "n_trials")


@dataclass(frozen=True)
class BreakevenGateConfig:
    """B案五道门预注册参数（不可变；YAML breakeven_cost_gate 块载入后构造）。"""

    p1_median_bp_min: float = 40.0
    p2_p10_bp_min: float = 0.0
    p3_ratio_min: float = DEFAULT_P3_RATIO_MIN
    p3_layer_min_n: int = DEFAULT_P3_LAYER_MIN_N
    p4_scale_sensitivity_max: float = DEFAULT_P4_SCALE_SENSITIVITY_MAX
    #: c* 求解面：ref=净值序列成本档（闭式解锚），hi=外推上界（越界单列不进分位数）
    ref_bp: float = DEFAULT_BREAKEVEN_REF_BP
    hi_bp: float = DEFAULT_BREAKEVEN_HI_BP
    over_hi_label: str = DEFAULT_BREAKEVEN_OVER_LABEL
    #: 二分面（非线性成本模型/T2 成绩单复算用；线性成本线上与闭式解等价，测试钉死）
    bisect_tol_bp: float = 0.1

    def __post_init__(self) -> None:
        if float(self.p1_median_bp_min) < 0 or float(self.p2_p10_bp_min) < 0:
            raise ValueError("P1/P2 门槛必须非负（40bp 锚语义）")
        if not 0 <= float(self.ref_bp) < float(self.hi_bp):
            raise ValueError(f"须 0<=ref_bp<hi_bp: {self.ref_bp}/{self.hi_bp}")
        if not 0 < float(self.p3_ratio_min) <= 1:
            raise ValueError(f"P3 达标层占比须在 (0,1]: {self.p3_ratio_min}")
        if int(self.p3_layer_min_n) < 1:
            raise ValueError(f"P3 层最小样本须 >=1: {self.p3_layer_min_n}")
        if not 0 < float(self.p4_scale_sensitivity_max) <= 1:
            raise ValueError(f"P4 相对变化上限须在 (0,1]: {self.p4_scale_sensitivity_max}")
        if float(self.bisect_tol_bp) <= 0:
            raise ValueError(f"二分容差须为正: {self.bisect_tol_bp}")


@dataclass(frozen=True)
class BreakevenGateVerdict:
    """B案五道门判定——逐门三态+数字证据（案卷 §3.2 五：禁二值/禁默认降级 PASS）。"""

    #: 聚合三态：FAIL(P1-P4 任一不满足) > INDETERM(任一门证据不足/层 n<30) > PASS(五门全过)
    tri_state: str
    p1_median: dict
    p2_p10: dict
    p3_stratified: dict
    p4_scale: dict
    p5_data_version: dict
    #: 报告面（案卷 §3.2 六：c* 分位数/幸存者 K 与全体候选 N/单列池，禁只报中位数）
    quantiles: dict
    survivors_k: int
    candidates_n: int
    quantiles_all_defined: dict | None = None
    over_hi_pool: tuple[str, ...] = ()
    degenerate_pool: tuple[str, ...] = ()
    non_survivors_clamped0: int = 0
    reasons: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.tri_state == "PASS"


def breakeven_cost_star_from_net_line(
    mean_net_at_ref: float,
    avg_turnover_1side: float,
    config: BreakevenGateConfig | None = None,
) -> float:
    """闭式解原始 c*（bp；引擎线性成本线下与二分解逐位等价，测试钉死）。

    引擎冻结成本线（_c4_engine._net_line）: net(c)=gross−turnover·(COMM·2+STAMP+c·2)/1e4，
    mean(net(c)) 对 c 严格线性且斜率=−2·mean(turnover)/1e4；而 Sharpe(c)=0 ⟺ mean(net(c))=0
    （std>0 恒成立），故零交叉与年化口径（√244/ddof/Lo 修正）无关=对 A 股四条强制稳健：
        c*_raw = ref_bp + mean(net(ref))·1e4 / (2·mean(turnover))
    本函数只解零交叉原始值；分池语义（案卷 §3.2 一）由 evaluate_breakeven_cost_gate 统一执行：
    c*_raw<0（零成本即亏）→钳 0（Sharpe(0)≤0 ⇒ c*=0，非幸存者）；c*_raw>hi_bp→'>200'
    越界单列（不计入分位数）；turnover≤0→NaN（零方差退化格=单列池，禁混入分布）。
    avg_turnover_1side 口径=引擎 stats 同源均值（4 位舍入，c* 误差 <0.2bp 量级，
    远小于 40bp 判据粒度）。
    """
    cfg = config or BreakevenGateConfig()
    to = float(avg_turnover_1side)
    if not to > 0:  # 覆盖 0/负/NaN（NaN 比较恒 False）→退化池
        return float("nan")
    return float(cfg.ref_bp) + float(mean_net_at_ref) * 1e4 / (2.0 * to)


def monotonic_grid_violations(sharpe_fn, config: BreakevenGateConfig | None = None) -> list[float]:
    """成本-Sharpe 单调性网格校验（案卷 §3.2 二"必做"；违反格 c*=NaN 单列禁混入中位数）。

    返回违例档位清单（空=单调非增成立）。线性成本线上结构性恒空（mean(net(c)) 严格
    递减且 std 有界→Sharpe 单峰不回增违例仅可能来自引擎涨跌停/停牌填充缺陷）。
    """
    cfg = config or BreakevenGateConfig()
    grid = [0.0, 5.0, 10.0, 20.0, 40.0, 60.0, 80.0, 100.0, 150.0, float(cfg.hi_bp)]
    srs = [float(sharpe_fn(bp)) for bp in grid]
    return [grid[i + 1] for i in range(len(srs) - 1) if srs[i + 1] > srs[i]]


def solve_breakeven_cost_star(
    sharpe_fn,
    config: BreakevenGateConfig | None = None,
) -> float:
    """通用二分解 c*（案卷 §3.2 二伪代码逐行；非线性成本模型/T2 成绩单复算面）。

    sharpe_fn: callable(bp_bp)->float（单边成本 bp→年化 Sharpe）。前提=单调非增
    （调用方须先过 monotonic_grid_violations，违反格=NaN 单列禁入本解算器）。
    线性成本线上与 breakeven_cost_star_from_net_line 等价（容差 bisect_tol_bp 内）。
    """
    cfg = config or BreakevenGateConfig()
    lo, hi = 0.0, float(cfg.hi_bp)
    if float(sharpe_fn(hi)) > 0:
        return float("inf")  # 上界不足（案卷：扩界/单列由调用方处置）
    while hi - lo > float(cfg.bisect_tol_bp):
        mid = (lo + hi) / 2
        if float(sharpe_fn(mid)) > 0:
            lo = mid
        else:
            hi = mid
    return lo


def _be_gate_line(name: str, state: str, measured, threshold: str, note: str = "") -> dict:
    return {"gate": name, "state": state, "measured": measured, "threshold": threshold, "note": note}


def evaluate_breakeven_cost_gate(
    c_star_by_cell: dict[str, float | str],
    *,
    layer_keys: dict[str, object] | None = None,
    scale_c_star: dict[str, dict[float, float]] | None = None,
    data_version: dict | None = None,
    candidates_n: int | None = None,
    config: BreakevenGateConfig | None = None,
) -> BreakevenGateVerdict:
    """五道门判定（不抽样；population=幸存者∪有效 c*，案卷 §3.2 四）。

    Args:
        c_star_by_cell: 每格 c*（bp）原始解（breakeven_cost_star_from_net_line 产出）。
            float>hi_bp → 越界单列池（over_hi_label，不计入分位数）；float<=0 → 钳 0
            非幸存者（计入 N 与 K/N 披露，不入分位数）；NaN → 退化/非单调单列池；
            0<c<=hi → 幸存者有效解；str → 调用方显式越界标签（同越界池）。
        layer_keys: 格→层键（换手三分位×策略族×市场状态）。None/缺格=P3 证据不足
            （INDETERM，禁默认降级 PASS）；层内 n<layer_min_n 判 INSUFFICIENT-N。
        scale_c_star: 格→{scale: c*}（1x/5x/10x 目标仓位重放面）。None=P4 证据不足
            （INDETERM——线性模型下 c* 结构性尺度不变，禁以恒零读数充当测量=橡皮图章）。
        data_version: P5 成绩单四字段。缺字段=P5 INDETERM（案卷 FAIL 枚举=P1-P4，
            成绩单字段缺失=报告面未闭合须补做，不与判据 FAIL 混池）。
        candidates_n: 全体候选数 N（缺省=len(c_star_by_cell)）。
    """
    cfg = config or BreakevenGateConfig()
    reasons: list[str] = []
    over_pool: list[str] = []
    nan_pool: list[str] = []
    valid: dict[str, float] = {}
    non_survivor_n = 0
    for g, c in c_star_by_cell.items():
        gs = str(g)
        if isinstance(c, str):  # 调用方显式越界标签
            over_pool.append(gs)
            continue
        cf = float(c)
        if math.isnan(cf):
            nan_pool.append(gs)  # 退化/非单调单列
        elif cf <= 0.0:
            non_survivor_n += 1  # Sharpe(0)≤0 ⇒ c*=0，非幸存者（K/N 披露，不入分布）
        elif cf > float(cfg.hi_bp):
            over_pool.append(gs)
        else:
            valid[gs] = cf
    n_all = int(candidates_n if candidates_n is not None else len(c_star_by_cell))
    k = len(valid)
    vals = np.asarray(sorted(valid.values()), dtype=float)
    if len(vals):
        p10, p25, med, p75, p90 = (float(x) for x in np.percentile(vals, [10, 25, 50, 75, 90]))
    else:
        p10 = p25 = med = p75 = p90 = float("nan")
    quantiles = {"p10": p10, "p25": p25, "median": med, "p75": p75, "p90": p90}
    #: P2 域=案卷 §一"定义的 c* 分布"（钳 0 非幸存者并入；越界/退化单列不入）——
    #: "Sharpe≥0 语义一字不动"的锚门，最差 10% 候选不得上线即亏
    defined_dist = (
        np.sort(np.concatenate([vals, np.zeros(non_survivor_n)])) if (len(vals) or non_survivor_n) else np.asarray([])
    )
    p10_defined = float(np.percentile(defined_dist, 10)) if len(defined_dist) else float("nan")

    # P1 中位数门（population=幸存者∩有效，案卷 §3.2 四 P1 原文 "g ∈ 幸存者, c*_g 有效"）
    p1_ok = bool(len(vals) and med >= float(cfg.p1_median_bp_min))
    p1 = _be_gate_line("p1_median", "PASS" if p1_ok else "FAIL", med, f">={cfg.p1_median_bp_min:g}bp")
    if not p1_ok:
        reasons.append(f"P1 中位数 {med:.2f}bp < {cfg.p1_median_bp_min:g}bp（幸存者有效 c* n={k}）")

    # P2 尾部门（定义分布 P10>=0bp；钳 0 并入=零成本即亏格按 §一 c*=0 入分布）
    p2_ok = bool(len(defined_dist) and p10_defined >= float(cfg.p2_p10_bp_min))
    p2 = _be_gate_line("p2_p10", "PASS" if p2_ok else "FAIL", p10_defined, f">={cfg.p2_p10_bp_min:g}bp")
    if not p2_ok:
        reasons.append(f"P2 P10(定义分布含钳零) {p10_defined:.2f}bp < {cfg.p2_p10_bp_min:g}bp")

    # P3 分层门（层键缺席=P3 INDETERM；层 n<min 判 INSUFFICIENT-N=任一层命中即 INDETERM）
    if layer_keys is None:
        p3_state = "INDETERM"
        p3_measured = "layer_keys 未提供（换手三分位×策略族×市场状态证据面未闭合）"
        reasons.append("P3 层键缺席（T2 判定书/成绩单波次证据面）→ INDETERM 须补数据")
        p3_layers: dict = {}
    else:
        p3_layers = {}
        for g, c in valid.items():
            key = layer_keys.get(g)
            if key is None:
                continue
            p3_layers.setdefault(tuple(key) if isinstance(key, (list, tuple)) else key, []).append(c)
        insuf = {k3: v for k3, v in p3_layers.items() if len(v) < int(cfg.p3_layer_min_n)}
        judged = {k3: float(np.median(v)) for k3, v in p3_layers.items() if len(v) >= int(cfg.p3_layer_min_n)}
        ratio = (
            (sum(1 for m in judged.values() if m >= float(cfg.p1_median_bp_min)) / len(p3_layers)) if p3_layers else 0.0
        )
        missing = len(valid) - sum(len(v) for v in p3_layers.values())
        if missing:
            p3_state = "INDETERM"
            reasons.append(f"P3 层键缺格 {missing}（禁默认降级）")
        elif insuf or not p3_layers:
            p3_state = "INDETERM"
            reasons.append(f"P3 INSUFFICIENT-N 层 {len(insuf)}/{len(p3_layers)}（n<{cfg.p3_layer_min_n} 判灰不算绿）")
        elif ratio >= float(cfg.p3_ratio_min):
            p3_state = "PASS"
        else:
            p3_state = "FAIL"
            reasons.append(f"P3 达标层占比 {ratio:.3f} < {cfg.p3_ratio_min:g}")
        p3_measured = {
            "layers_total": len(p3_layers),
            "layers_insufficient_n": len(insuf),
            "pass_ratio": round(ratio, 6),
            "layer_medians_head": {str(k3): round(m, 2) for k3, m in sorted(judged.items())[:10]},
        }
    p3 = _be_gate_line("p3_stratified", p3_state, p3_measured, f">={cfg.p3_ratio_min:g} 且层 n>={cfg.p3_layer_min_n}")

    # P4 规模门（1x/5x/10x 重放面缺席=INDETERM；线性模型恒零读数禁充测量）
    if scale_c_star is None:
        p4_state, p4_measured = "INDETERM", "scale replay 未提供（1x/5x/10x 目标仓位 c* 重放=T2 成绩单波次）"
        reasons.append("P4 规模重放缺席 → INDETERM 须补跑")
    else:
        worst = 0.0
        for _g, rows in scale_c_star.items():
            base = rows.get(1.0)
            if base is None or base <= 0 or isinstance(base, str):
                continue
            for s, c in rows.items():
                if s == 1.0 or c is None or isinstance(c, str) or c <= 0:
                    continue
                worst = max(worst, abs(float(c) / float(base) - 1.0))
        p4_state = "PASS" if worst <= float(cfg.p4_scale_sensitivity_max) else "FAIL"
        if p4_state == "FAIL":
            reasons.append(f"P4 规模敏感度 {worst:.3f} > {cfg.p4_scale_sensitivity_max:g}")
        p4_measured = round(worst, 6)
    p4 = _be_gate_line("p4_scale", p4_state, p4_measured, f"<={cfg.p4_scale_sensitivity_max:g}")

    # P5 数据版本门（成绩单四字段；缺=报告面未闭合 INDETERM 须补，不冒充判据 FAIL）
    dv = dict(data_version or {})
    missing_fields = [f for f in P5_REQUIRED_FIELDS if dv.get(f) in (None, "")]
    p5_state = "PASS" if not missing_fields else "INDETERM"
    if missing_fields:
        reasons.append(f"P5 数据版本字段缺失 {missing_fields}（成绩单指纹管线未接线=补数据项）")
    p5 = _be_gate_line("p5_data_version", p5_state, {f: dv.get(f) for f in P5_REQUIRED_FIELDS}, "四字段齐备")

    states = [p1["state"], p2["state"], p3["state"], p4["state"], p5["state"]]
    if any(s == "FAIL" for s in states[:4]):  # 案卷 FAIL 枚举=P1/P2/P3/P4
        tri = "FAIL"
    elif any(s == "INDETERM" for s in states):
        tri = "INDETERM"
    else:
        tri = "PASS"
    return BreakevenGateVerdict(
        tri_state=tri,
        p1_median=p1,
        p2_p10=p2,
        p3_stratified=p3,
        p4_scale=p4,
        p5_data_version=p5,
        quantiles=quantiles,
        survivors_k=k,
        candidates_n=n_all,
        quantiles_all_defined={
            kq: (round(float(x), 6) if x == x else None)
            for kq, x in zip(
                ("p10", "p25", "median", "p75", "p90"),
                np.percentile(defined_dist, [10, 25, 50, 75, 90]) if len(defined_dist) else [float("nan")] * 5,
                strict=True,
            )
        },
        over_hi_pool=tuple(sorted(over_pool)),
        degenerate_pool=tuple(sorted(nan_pool)),
        non_survivors_clamped0=non_survivor_n,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True)
class CostGateConfig:
    """考尺成本门预注册参数（不可变；YAML 载入后构造）。"""

    tiers_bp: tuple[float, ...] = DEFAULT_COST_TIERS_BP
    survival_floor: float = DEFAULT_SURVIVAL_FLOOR
    turnover_cap_annual_x: float = DEFAULT_TURNOVER_CAP_ANNUAL_X
    turnover_days_basis: int = DEFAULT_TURNOVER_DAYS_BASIS
    monotonic_tol: float = DEFAULT_MONOTONIC_TOL
    min_days: int = DEFAULT_MIN_DAYS
    #: 规模维三参（预注册，config/exam_scale_cost_gate.yaml scale_gate 同源；冻结后禁改）
    scale_participation_ref: float = DEFAULT_SCALE_PARTICIPATION_REF
    scale_exponent: float = DEFAULT_SCALE_EXPONENT
    scale_multiplier_cap: float = DEFAULT_SCALE_MULTIPLIER_CAP

    def __post_init__(self) -> None:
        tiers = tuple(float(t) for t in self.tiers_bp)
        if len(tiers) < 3:
            raise ValueError(f"档位数 {len(tiers)} < 3，单调性证据不足（fail-closed 设计）")
        if any(tiers[i + 1] <= tiers[i] for i in range(len(tiers) - 1)):
            raise ValueError(f"档位必须严格升序: {tiers}")
        if tiers[0] != 0.0:
            raise ValueError(f"首档必须为 0bp（零成本对照）: {tiers}")
        if float(self.turnover_cap_annual_x) <= 0:
            raise ValueError(f"换手上限必须为正: {self.turnover_cap_annual_x}")
        if not float(self.scale_participation_ref) > 0:
            raise ValueError(f"规模锚参与率必须为正: {self.scale_participation_ref}")
        if not 0 < float(self.scale_exponent) <= 1:
            raise ValueError(f"规模律指数须在 (0,1]: {self.scale_exponent}")
        if float(self.scale_multiplier_cap) < 1.0:
            raise ValueError(f"规模乘数上限须 >=1: {self.scale_multiplier_cap}")


@dataclass(frozen=True)
class CostGateVerdict:
    """成本门判定——不可变，逐条带数字证据（裁定#325 口径禁"全绿"表述）。"""

    passed: bool
    monotonic: bool
    full_cost_survived: bool
    turnover_within_cap: bool
    annual_turnover_x: float
    tier_sharpes: dict[float, float] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()
    #: 规模维证据（裁-4 item5）：None=未启用（participation_rate 缺省，行为零变化）
    scale_adjusted_survived: bool | None = None
    scale_multiplier: float | None = None
    effective_top_bp: float | None = None


def _sharpe(net: pd.Series) -> float:
    std = float(net.std())
    return float(net.mean() / std * np.sqrt(244)) if std > 0 else 0.0


def cost_scale_multiplier(participation_rate: float, config: CostGateConfig | None = None) -> float:
    """规模乘数（裁-4 item5，开方律单边只罚不奖）: m=(participation/ref)^exponent, [1, cap]。

    participation<=ref（≤校准锚规模）→ m=1.0：40bp 锚语义原样（档位 bp 按冻结口径适用）；
    participation>ref → m>1：测量档曲线按末段斜率外推至 tiers[-1]×m 有效档判存活。
    participation 非正（含 NaN）=ValueError fail-closed。
    """
    cfg = config or CostGateConfig()
    p = float(participation_rate)
    if not p > 0:  # 覆盖 0/负数/NaN（NaN 比较恒 False）
        raise ValueError(f"参与率必须为正数: {participation_rate!r}")
    if p <= cfg.scale_participation_ref:
        return 1.0
    m = (p / cfg.scale_participation_ref) ** cfg.scale_exponent
    return float(min(m, cfg.scale_multiplier_cap))


def _sharpe_at_effective_bp(tiers: list[float], sharpes: list[float], bp: float) -> float:
    """档位曲线在 bp 处取值：测量档内线性插值；越过最高测量档按末段斜率线性外推。

    外推即规模门的"能fail"机制：策略在 40bp 锚勉强存活（末段斜率向下）时，
    规模上调的有效档（>40bp）把 sharpe 推穿 survival_floor——旧门对此恒盲。
    """
    if bp <= tiers[0]:
        return sharpes[0]
    if bp <= tiers[-1]:
        return float(np.interp(bp, tiers, sharpes))
    slope = (sharpes[-1] - sharpes[-2]) / (tiers[-1] - tiers[-2])
    return float(sharpes[-1] + slope * (bp - tiers[-1]))


def validate_scan_tiers(tiers_bp) -> tuple[float, ...]:
    """扫描档位集校验（扫描面，非判定面）: 非空、严格升序、首档=0bp 零成本对照。

    与 CostGateConfig 的判定不变量（≥3 档）分离：方案①两轮制 T1 轻档两档 [0,5]
    只做粗筛扫描，不做三门判定（终审仍在 T2 全档 evaluate_exam_cost_gate）。
    非法=ValueError（调用方 decide 去向；执行器预算闸侧转 SystemExit fail-closed）。
    """
    try:
        tiers = tuple(float(t) for t in tiers_bp)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"档位集非法（须为数值序列）: {tiers_bp!r}") from exc
    if not tiers:
        raise ValueError("档位集为空——零成本对照档缺失（fail-closed）")
    if any(tiers[i + 1] <= tiers[i] for i in range(len(tiers) - 1)):
        raise ValueError(f"档位必须严格升序: {tiers}")
    if tiers[0] != 0.0:
        raise ValueError(f"首档必须为 0bp（零成本对照）: {tiers}")
    return tiers


def run_cost_tier_scan(
    weights: pd.DataFrame,
    px_close: pd.DataFrame,
    net_fn,
    config: CostGateConfig | None = None,
    *,
    tiers_bp=None,
    nets_by_tier=None,
) -> dict[str, float]:
    """档位滑点净值扫描（引擎口径唯一性由 net_fn 保证，本件零重实现）。

    Args:
        weights/px_close: 与引擎同构的权重/收盘价宽表。
        net_fn: callable(weights, px_close, *, slippage_bp) -> pd.Series——**必须以关键字传**
            滑点档。引擎真身签名是 (weights, px_close, gate_limits=True, slippage_bp=None)
            （scripts/backtest/translated/_c4_engine.py），位置传参会把 bp 绑进 gate_limits：
            五档 Sharpe 逐位相同=门形同虚设，且 0bp 档顺带关掉涨跌停可成交闸
            （gate_limits 收到假值 0.0）。2026-09-23 st-e2e-20260924 实测复现：
            位置传参 {0,5,10,20,40}bp→Sharpe 恒 10.6211；显式 kwargs→11.63/10.62/9.56/7.45/3.83。
            传 _c4_engine.daily_net_returns 即冻结土规口径档位覆盖。
        config: 档位等参数。
        tiers_bp: 档位子集覆盖（方案①两轮制 2026-09-24，裁定#413 下一窗口升级案）——
            None=用 config 档位（缺省，全档，行为零变化）；否则须过 validate_scan_tiers
            （T1 轻档两档合法）。档位子集只影响扫描面；三门判定仍以 config 全档证据计。
        nets_by_tier: 预算档净值注入（st-ddup-20260925 去重改造①，与本件"净值档位序列
            由调用方注入"不变量同构）——None（缺省）=现行路径逐档调 net_fn（行为零变化）；
            传入 {float(bp): net} 时跳过 net_fn，逐档 sharpe 只对注入序列计（引擎侧
            net_returns_by_tiers 一趟派生，与逐档 daily_net_returns 逐位一致）。
            缺档=ValueError（fail-closed，禁静默跳档）。

    Returns:
        {slippage_bp: sharpe}（含 0bp 零成本对照档）。
    """
    cfg = config or CostGateConfig()
    tiers = validate_scan_tiers(cfg.tiers_bp if tiers_bp is None else tiers_bp)
    if nets_by_tier is None:
        return {float(bp): round(_sharpe(net_fn(weights, px_close, slippage_bp=bp)), 4) for bp in tiers}
    missing = [bp for bp in tiers if float(bp) not in nets_by_tier]
    if missing:
        raise ValueError(f"nets_by_tier 缺档: {missing}（fail-closed，禁静默跳档）")
    return {float(bp): round(_sharpe(nets_by_tier[float(bp)]), 4) for bp in tiers}


def evaluate_exam_cost_gate(
    tier_sharpes: dict[float, float],
    mean_daily_turnover_1side: float,
    days: int,
    config: CostGateConfig | None = None,
    *,
    participation_rate: float | None = None,
) -> CostGateVerdict:
    """三门判定+可选规模维（裁-4 item5），fail-closed。

    Args:
        tier_sharpes: run_cost_tier_scan 产出 {slippage_bp: sharpe}。
        mean_daily_turnover_1side: 冻结土规口径日均单边换手
            （_c4_engine run_backtest 输出 avg_turnover_1side 同源）。
        days: 样本交易日数（< min_days 判不通过——证据不足非跳过）。
        config: 预注册参数。
        participation_rate: 格点自身规模（成交额/ADV 参与率）——None（缺省）=规模维
            禁用=行为零变化（三门判定原样）；传入时新增门4"规模调整存活"：以
            tiers[-1]×cost_scale_multiplier 为有效档取档位曲线值判 survival_floor，
            规模把成本推穿地板即拦截（旧门对成交规模恒盲=橡皮图章，本轮可fail）。
            40bp 锚语义不动：锚=校准参与率 ref 处 m=1，判定与缺省逐字一致。
    """
    cfg = config or CostGateConfig()
    tiers = sorted(float(k) for k in tier_sharpes)
    sharpes = [float(tier_sharpes[k]) for k in tiers]
    reasons: list[str] = []

    # 证据充分性（fail-closed：缺证据=不通过，非跳过）
    if len(tiers) != len(cfg.tiers_bp) or days < cfg.min_days:
        reasons.append(f"证据不足(fail-closed): 档位数={len(tiers)}/{len(cfg.tiers_bp)}, 天数={days}<{cfg.min_days}")
        return CostGateVerdict(
            passed=False,
            monotonic=False,
            full_cost_survived=False,
            turnover_within_cap=False,
            annual_turnover_x=float("nan"),
            tier_sharpes=dict(tier_sharpes),
            reasons=tuple(reasons),
        )

    # 门1: 五档单调性（成本升 sharpe 非增，容差 tol）
    monotonic = all(sharpes[i] >= sharpes[i + 1] - cfg.monotonic_tol for i in range(len(sharpes) - 1))
    if not monotonic:
        reasons.append(f"档位单调性破缺: {[round(s, 3) for s in sharpes]} @ {tiers}bp——成本升收益反升=口径或前视嫌疑")

    # 门2: 全成本档存活
    full_sharpe = sharpes[-1]
    full_cost_survived = full_sharpe >= cfg.survival_floor
    if not full_cost_survived:
        reasons.append(
            f"全成本档({tiers[-1]:g}bp) sharpe={full_sharpe:.3f} < 存活地板 {cfg.survival_floor:.2f}——纸面亮实盘死"
        )

    # 门3: E7 换手上限门（年化单边换手 = 日均单边换手 × 年交易日基准）
    annual_turnover_x = float(mean_daily_turnover_1side) * cfg.turnover_days_basis
    turnover_within_cap = annual_turnover_x <= cfg.turnover_cap_annual_x
    if not turnover_within_cap:
        reasons.append(
            f"E7 换手门: 年化单边换手 {annual_turnover_x:.1f}x > 上限 {cfg.turnover_cap_annual_x:g}x"
            f"（日均 {mean_daily_turnover_1side:.4f} × {cfg.turnover_days_basis}）——成本拖累超预注册预算"
        )

    # 门4: 规模调整存活（裁-4 item5 2026-09-28）——仅 participation_rate 显式传入时启用
    scale_adjusted_survived: bool | None = None
    scale_multiplier: float | None = None
    effective_top_bp: float | None = None
    if participation_rate is not None:
        scale_multiplier = cost_scale_multiplier(participation_rate, cfg)
        effective_top_bp = tiers[-1] * scale_multiplier
        scaled_sharpe = _sharpe_at_effective_bp(tiers, sharpes, effective_top_bp)
        scale_adjusted_survived = scaled_sharpe >= cfg.survival_floor
        if not scale_adjusted_survived:
            reasons.append(
                f"规模存活门: 参与率 {float(participation_rate):.2%} → 乘数 {scale_multiplier:.2f}，"
                f"有效档 {effective_top_bp:g}bp 处 sharpe={scaled_sharpe:.3f} < 存活地板 "
                f"{cfg.survival_floor:.2f}——旧门按 40bp 锚判存活但该格点规模下成本已穿地板（开方律）"
            )

    passed = monotonic and full_cost_survived and turnover_within_cap and (scale_adjusted_survived is not False)
    if passed:
        scale_note = (
            f"，规模维 参与率 {float(participation_rate):.2%}×乘数 {scale_multiplier:.2f}→有效档 "
            f"{effective_top_bp:g}bp 存活(sharpe={_sharpe_at_effective_bp(tiers, sharpes, effective_top_bp):.3f})"
            if participation_rate is not None
            else ""
        )
        reasons.append(
            f"成本门通过: 档位 sharpe {[round(s, 3) for s in sharpes]} 单调且全成本档存活"
            f"（{tiers[-1]:g}bp={full_sharpe:.3f}），年化换手 {annual_turnover_x:.1f}x<={cfg.turnover_cap_annual_x:g}x"
            f"{scale_note}"
        )
    return CostGateVerdict(
        passed=passed,
        monotonic=monotonic,
        full_cost_survived=full_cost_survived,
        turnover_within_cap=turnover_within_cap,
        annual_turnover_x=annual_turnover_x,
        tier_sharpes=dict(tier_sharpes),
        reasons=tuple(reasons),
        scale_adjusted_survived=scale_adjusted_survived,
        scale_multiplier=scale_multiplier,
        effective_top_bp=effective_top_bp,
    )
