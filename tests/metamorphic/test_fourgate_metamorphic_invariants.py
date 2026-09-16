# [BLUEPRINT] MOD-SIG-148 | tests/metamorphic/test_fourgate_metamorphic_invariants.py
# [MODULE] tests.metamorphic.test_fourgate_metamorphic_invariants
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] metamorphic 双不变式（真源 docs/_working/sop_review_nodes/subnode_mining_round1.md §47 子节点3）：
#   INV-3 样本置换不变——输入行/切片顺序置换，四闸统计量(p/q/shrunk/wilson/edge)与判定 state 不变；
#   INV-4 效应量单调——固定 (n, p0) 下 hits↑ -> p 值单调不增（含 certify_family 端到端 p/q/shrunk/wilson 链）。
#   合成数据，不触库不触网。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/metamorphic/test_fourgate_metamorphic_invariants.py
# [TTL] permanent
"""四闸 metamorphic 不变式（立卡首批 4 条中的后两条）。

被测真源（file:line 以 2026-09-16 工作区为准）：
- certify_family          src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py:182
- within_regime_edge      同文件:129
- binomial_ge_pvalue      同文件:79
- shrunk_rate             同文件:116

红蓝对抗退化情形（全零/空/NaN）一并钉扎为特征化测试；已知边界缺陷
（p0∈{0,1} 经校验后 math domain error）只记录不断言，见
docs/_working/metamorphic_mutation_pilot_report.md 发现 F-1。
"""

from __future__ import annotations

import random

import pytest

from zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier import (
    binomial_ge_pvalue,
    certify_family,
    effective_n,
    shrunk_rate,
    within_regime_edge,
)

# 容差口径：置换引起的浮点求和顺序误差（<=1e-12 量级）；单行独立计算路径为精确相等
_PERM_TOL = 1e-12
# 单调链跨 BH 重排序的浮点松弛
_MONO_TOL = 1e-9


def _family_pooled() -> list[dict]:
    """四形态池化行（p 值互异防 BH 排序平手；delta 刻意 n_eff<30 走闸B 失败）。"""
    return [
        {"pattern_id": "alpha-strong", "hit_rate": 0.62, "n_events": 30000},
        {"pattern_id": "beta-mid", "hit_rate": 0.55, "n_events": 20000},
        {"pattern_id": "gamma-weak", "hit_rate": 0.52, "n_events": 40000},
        {"pattern_id": "delta-lucky", "hit_rate": 0.90, "n_events": 250},
    ]


def _regime_rows() -> dict[str, list[dict]]:
    """每形态 3 个 regime 切片（强形态 regime 间有分化，触发闸C 集中度路径）。"""
    return {
        "alpha-strong": [
            {"regime_tag": "r1", "hit_rate": 0.66, "n_events": 18000},
            {"regime_tag": "r2", "hit_rate": 0.55, "n_events": 9000},
            {"regime_tag": "r3", "hit_rate": 0.58, "n_events": 3000},
        ],
        "beta-mid": [
            {"regime_tag": "r1", "hit_rate": 0.56, "n_events": 12000},
            {"regime_tag": "r2", "hit_rate": 0.54, "n_events": 8000},
        ],
        "gamma-weak": [
            {"regime_tag": "r1", "hit_rate": 0.51, "n_events": 25000},
            {"regime_tag": "r3", "hit_rate": 0.53, "n_events": 15000},
        ],
    }


_BASELINES = (0.50, {"__pooled__": 0.50, "r1": 0.50, "r2": 0.50, "r3": 0.50})


def _run_family(pooled=None, regime=None):
    return certify_family(
        pooled if pooled is not None else _family_pooled(),
        regime if regime is not None else _regime_rows(),
        _BASELINES[0],
        _BASELINES[1],
        fwd_window=10,
        timeframe="day",
        direction="向上",
    )


# ── INV-3：样本置换不变 ───────────────────────────────────────────────────────


@pytest.mark.parametrize("seed", [7, 42, 2026])
def test_certify_family_row_permutation_invariant(seed):
    """池化行顺序置换 -> 认证记录逐字段完全一致（单行独立计算，精确相等）。"""
    base = _run_family()
    assert len(base) == 4  # 场景自检：4 形态全部进入认定（Fail-Closed 未剔除）

    rows = _family_pooled()
    random.Random(seed).shuffle(rows)
    permuted = certify_family(
        rows, _regime_rows(), _BASELINES[0], _BASELINES[1],
        fwd_window=10, timeframe="day", direction="向上",
    )
    assert permuted == base  # frozen dataclass 逐字段相等（输出已按 pattern_id 排序）


@pytest.mark.parametrize("seed", [3, 99])
def test_certify_family_state_verdict_permutation_invariant(seed):
    """四闸判定（state 字段）对输入行顺序置换不变。"""
    base_states = {r.pattern_id: r.state for r in _run_family()}
    assert set(base_states.values()) & {"certified", "probation"} != set()  # 场景非全败自检

    rows = _family_pooled()
    random.Random(seed).shuffle(rows)
    perm_states = {
        r.pattern_id: r.state
        for r in certify_family(
            rows, _regime_rows(), _BASELINES[0], _BASELINES[1],
            fwd_window=10, timeframe="day", direction="向上",
        )
    }
    assert perm_states == base_states


@pytest.mark.parametrize("seed", [5, 17, 777])
def test_within_regime_edge_slice_permutation_invariant(seed):
    """闸C regime 切片顺序置换 -> (weighted_edge, share) 不变（浮点和序误差容差）。"""
    slices = _regime_rows()["alpha-strong"]
    base_edge, base_share = within_regime_edge(slices, _BASELINES[1])
    assert base_edge > 0  # 场景自检：正 edge 路径

    perm = list(slices)
    random.Random(seed).shuffle(perm)
    edge, share = within_regime_edge(perm, _BASELINES[1])
    assert edge == pytest.approx(base_edge, abs=_PERM_TOL)
    assert share == pytest.approx(base_share, abs=_PERM_TOL)


def test_within_regime_edge_weight_permutation_invariant():
    """加权 edge 对切片权重顺序不变：按任意切法重排 n_events 权重，加权和一致。

    数学事实：weighted_edge = Σ(n_i·edge_i)/Σn_i 与求和顺序无关；share 只依赖
    max/sum，与顺序无关。用逆序（最坏浮点序）验证。
    """
    slices = [
        {"regime_tag": f"r{i}", "hit_rate": 0.50 + 0.01 * i, "n_events": 1000 + 137 * i}
        for i in range(9)
    ]
    base_edge, base_share = within_regime_edge(slices, _BASELINES[1])
    rev_edge, rev_share = within_regime_edge(list(reversed(slices)), _BASELINES[1])
    assert rev_edge == pytest.approx(base_edge, abs=_PERM_TOL)
    assert rev_share == pytest.approx(base_share, abs=_PERM_TOL)


# ── INV-4：效应量↑ -> p 值单调不增 ────────────────────────────────────────────


@pytest.mark.parametrize("n", [30, 100, 300.5, 999])
@pytest.mark.parametrize("p0", [0.3, 0.5, 0.55])
def test_binomial_pvalue_monotone_in_hits(n, p0):
    """固定 (n, p0)，hits 递增 -> P(X≥hits) 单调不增（二项尾概率数学事实）。"""
    hits_grid = [n * f for f in (0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.90, 1.0)]
    p_values = [binomial_ge_pvalue(h, n, p0) for h in hits_grid]
    for lo, hi in zip(p_values, p_values[1:]):
        assert hi <= lo + 1e-12, f"p 值随效应量上升: {lo} -> {hi} (n={n}, p0={p0})"


@pytest.mark.parametrize("hits,n", [(70, 100), (32.5, 50), (110, 300)])
def test_binomial_pvalue_monotone_in_baseline(hits, n):
    """固定 (hits, n)，基线 p0 递增 -> p 值单调不减（效应量=hits−baseline 的镜像面）。"""
    p0_grid = [0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60]
    p_values = [binomial_ge_pvalue(hits, n, p0) for p0 in p0_grid]
    for lo, hi in zip(p_values, p_values[1:]):
        assert hi >= lo - 1e-12


def test_certify_family_effect_size_monotone_chain():
    """端到端效应量阶梯：单形态 hit_rate 递升（其余固定）->
    p_value/q_value 单调不增；shrunk/wilson 单调不减。

    注意不断言 state 单调：闸C 集中度是正 edge 质量占比（比值型判据），
    单形态效应量↑可推高自身占比越 0.9 上限 -> certified→probation 属设计语义，
    非缺陷（红蓝对抗记录）。
    """
    ladder = [0.50, 0.51, 0.52, 0.54, 0.56, 0.58, 0.60, 0.63, 0.66]
    records = []
    for rate in ladder:
        pooled = [
            {"pattern_id": "alpha-strong", "hit_rate": 0.62, "n_events": 30000},
            {"pattern_id": "beta-mid", "hit_rate": rate, "n_events": 20000},
        ]
        regime = {
            "alpha-strong": _regime_rows()["alpha-strong"],
            "beta-mid": [{"regime_tag": "r1", "hit_rate": rate + 0.01, "n_events": 12000},
                         {"regime_tag": "r2", "hit_rate": rate - 0.01, "n_events": 8000}],
        }
        rec = {r.pattern_id: r for r in _run_family(pooled, regime)}["beta-mid"]
        records.append(rec)

    for lo, hi in zip(records, records[1:]):
        assert hi.p_value <= lo.p_value + _MONO_TOL
        assert hi.q_value <= lo.q_value + _MONO_TOL
        assert hi.shrunk >= lo.shrunk - _MONO_TOL
        assert hi.wilson >= lo.wilson - _MONO_TOL

    # 锚点：阶梯两端 p 值必须实质拉开（防"全相等=恒 1.0"的假通过）
    assert records[-1].p_value < records[0].p_value
    assert records[0].p_value >= 0.5  # rate=baseline 时无效应，p 不应小
    assert records[-1].p_value < 1e-4  # 顶部效应显著


def test_effective_n_monotone_in_window():
    """闸B：重叠窗折扣 n_eff 对 fwd_window 单调不增（同 n_events）。"""
    for w1, w2 in [(1, 2), (2, 5), (5, 10), (10, 100)]:
        assert effective_n(1000, w2) <= effective_n(1000, w1)


# ── 红蓝对抗：退化情形特征化（全零/空/NaN） ───────────────────────────────────


@pytest.mark.parametrize(
    ("hits", "n", "p0", "expected"),
    [
        (0, 100, 0.5, 1.0),   # 零命中=必然事件
        (110, 100, 0.5, 0.0),  # 不可能事件（钳位前短路）
        (0, 0, 0.5, 1.0),     # n=0 无信息
        (0, 100, 0.0, 1.0),   # p0=0 且零命中=必然事件（短路在浮点累积前）
        (100, 100, 0.5, 0.5 ** 100),  # hits=n：P(X≥n)=p0^n（单点尾项）
    ],
)
def test_binomial_degenerate_known_values(hits, n, p0, expected):
    assert binomial_ge_pvalue(hits, n, p0) == pytest.approx(expected)


@pytest.mark.parametrize(("p0", "ref"), [(1.0, "log1p"), (0.0, "log")])
def test_binomial_boundary_p0_domain_error_characterized(p0, ref):
    """特征化（缺陷 F-1，不修复——生产代码本试点禁改）：

    p0∈{0,1} 且 hits∈(0,n) 通过入参校验（0<=p0<=1）却在 math.log/log1p(0)
    抛 ValueError(domain)——校验承诺与实现边界不一致。钉扎现状防静默漂移，
    修复属裁定事项（报告 F-1）。
    """
    with pytest.raises(ValueError, match="domain"):
        binomial_ge_pvalue(50, 100, p0)


@pytest.mark.parametrize("args", [(-1, 100, 0.5), (50, -100, 0.5), (50, 100, 1.5), (50, 100, -0.1)])
def test_binomial_invalid_inputs_raise(args):
    with pytest.raises(ValueError):
        binomial_ge_pvalue(*args)


@pytest.mark.parametrize("fn_args", [(float("nan"), 100, 0.5), (50, float("nan"), 0.5), (50, 100, float("nan"))])
def test_binomial_nan_fail_closed(fn_args):
    """NaN 输入被入参校验/int 转换拦下（ValueError），不静默传播——fail-closed 钉扎。"""
    with pytest.raises(ValueError):
        binomial_ge_pvalue(*fn_args)


def test_binomial_inf_hits_treated_impossible():
    """hits=inf 走 hits>n 短路返回 0.0（有界输入假设下的特征化，见报告 F-2）。"""
    assert binomial_ge_pvalue(float("inf"), 100, 0.5) == 0.0


def test_shrunk_rate_degenerate():
    """闸D 收缩读数退化：rate=baseline -> baseline；n_eff=0 -> baseline；n_eff 极大 -> 贴 rate。"""
    assert shrunk_rate(0.55, 0.0, 0.5) == 0.5
    assert shrunk_rate(0.5, 1000.0, 0.5) == 0.5
    assert shrunk_rate(0.9, 1e12, 0.5) == pytest.approx(0.9, abs=1e-9)


def test_within_regime_edge_degenerate():
    """闸C 退化：空切片/全零 n -> (0,0) 无反证放行；缺基线 regime 回退 __pooled__。"""
    assert within_regime_edge([], _BASELINES[1]) == (0.0, 0.0)
    assert within_regime_edge([{"regime_tag": "r1", "hit_rate": 0.6, "n_events": 0}], _BASELINES[1]) == (0.0, 0.0)
    edge, share = within_regime_edge(
        [{"regime_tag": "rX", "hit_rate": 0.6, "n_events": 100}], {"__pooled__": 0.5}
    )
    assert edge == pytest.approx(0.1)
    assert share == 1.0


def test_certify_family_empty_and_fail_closed():
    """空族 -> 空表（BH 空族契约）；无 n/无 rate/__baseline__ 行不进认定。"""
    assert _run_family(pooled=[], regime={}) == []
    pooled = [
        {"pattern_id": "__baseline__", "hit_rate": 0.5, "n_events": 999},
        {"pattern_id": "no-rate", "hit_rate": None, "n_events": 100},
        {"pattern_id": "no-events", "hit_rate": 0.6, "n_events": 0},
        {"pattern_id": "keep-me", "hit_rate": 0.60, "n_events": 5000},
    ]
    records = _run_family(pooled=pooled, regime={})
    assert [r.pattern_id for r in records] == ["keep-me"]


# ── 门位边界语义钉扎（mutation 试点第一轮盲区整改，见试点报告 §3） ─────────────
# 背景：置换/单调不变式对"阈值恰等"与"常数漂移"类变异天然钝感，需显式钉扎
# fail-closed 边界语义：q==q_thr 判 failed、n_eff==min 放行闸B、w_edge==0 判
# probation、conc==conc_max 放行。锚点值全部取二进制可精确表示的构造。


def _boundary_family_pool(n_events: float, hit_rate: float) -> list[dict]:
    return [{"pattern_id": "edge-probe", "hit_rate": hit_rate, "n_events": n_events}]


def _boundary_family_regime() -> dict[str, list[dict]]:
    # 两片对称正 edge：conc=0.5<=0.9，w_edge>0（闸C 放行路径）
    return {
        "edge-probe": [
            {"regime_tag": "r1", "hit_rate": 0.80, "n_events": 150},
            {"regime_tag": "r2", "hit_rate": 0.80, "n_events": 150},
        ]
    }


def test_gate_a_q_threshold_boundary_inclusive():
    """闸A：q 恰等于阈值 -> failed（>= 闭边界，fail-closed）。"""
    rec = _run_family(
        pooled=_boundary_family_pool(300, 0.80), regime=_boundary_family_regime()
    )[0]
    assert rec.q_value < 0.05  # 场景自检：默认阈值下通过闸A（P(X>=24|30,.5)≈7e-4）

    at_thr = certify_family(
        _boundary_family_pool(300, 0.80), _boundary_family_regime(),
        _BASELINES[0], _BASELINES[1],
        fwd_window=10, timeframe="day", direction="向上", q_threshold=rec.q_value,
    )[0]
    assert at_thr.state == "failed"  # q==q_thr 必须判失败（阈值含等号）


def test_gate_b_n_eff_boundary_inclusive_pass():
    """闸B：n_eff 恰等于下限 -> 放行（< 严格小于，min 值含边界内）。"""
    # 300 事件 / 10 日窗 = n_eff 30.0 == N_EFF_MIN（二进制精确）
    rec = _run_family(
        pooled=_boundary_family_pool(300, 0.80), regime=_boundary_family_regime()
    )[0]
    assert rec.n_eff == 30.0
    assert rec.state == "certified"  # A/B/C/D 全过：恰在下限不放闸B 失败


def test_gate_c_zero_weighted_edge_is_probation():
    """闸C：加权 edge 恰为 0（正负抵消，二进制精确构造）-> probation 非 certified。"""
    pooled = [{"pattern_id": "zero-edge", "hit_rate": 0.75, "n_events": 1000000}]
    regime = {
        "zero-edge": [
            {"regime_tag": "r1", "hit_rate": 0.75, "n_events": 200},   # +0.25×200=+50
            {"regime_tag": "r2", "hit_rate": 0.75, "n_events": 200},   # +0.25×200=+50
            {"regime_tag": "r3", "hit_rate": 0.25, "n_events": 400},   # −0.25×400=−100
        ]
    }
    rec = _run_family(pooled=pooled, regime=regime)[0]
    assert rec.within_regime_edge == 0.0  # 50+50−100 精确为零
    assert rec.state == "probation"  # 零 edge=无优势证据，不得 certified


def test_gate_c_concentration_at_cap_is_certified():
    """闸C：集中度恰等于上限 0.9 -> 放行（> 严格大于，cap 值含边界内）。"""
    pooled = [{"pattern_id": "conc-cap", "hit_rate": 0.55, "n_events": 1000000}]
    regime = {
        "conc-cap": [
            {"regime_tag": "r1", "hit_rate": 0.75, "n_events": 360},   # +0.25×360=90
            {"regime_tag": "r2", "hit_rate": 0.75, "n_events": 40},    # +0.25×40=10
            {"regime_tag": "r3", "hit_rate": 0.50, "n_events": 1000000},  # 零 edge 大盘
        ]
    }
    rec = _run_family(pooled=pooled, regime=regime)[0]
    assert rec.edge_concentration == 0.9  # 90/100 精确等于 cap
    assert rec.state == "certified"


def test_certify_family_shrunk_absolute_anchor():
    """闸D 绝对值锚点：shrunk == (rate·n_eff + PRIOR_K·base)/(n_eff+PRIOR_K) 手算式。

    探测 certify_family 先验强度常数漂移（默认参数失真）——单调/置换类
    断言对此类变异天然钝感。
    """
    from zephyr.signal_ashare.strategy_signal.pattern_evidence_certifier import PRIOR_K

    rec = _run_family()[0]  # alpha-strong: rate .62 n=30000 fwd=10 -> n_eff 3000
    expected = (0.62 * 3000 + PRIOR_K * 0.5) / (3000 + PRIOR_K)
    assert rec.shrunk == pytest.approx(expected, rel=1e-12)
    assert rec.n_eff == 3000.0  # 折扣绝对值锚点（探测 fwd_window 折扣失效）
