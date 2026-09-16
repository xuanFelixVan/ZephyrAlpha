# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_auto_mount
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.auto_mount
# [CONSUMERS] MOD-BT-171 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离（tmp_path fixture，禁写生产路径）；手术函数纯文本测试零 IO；
#   红蓝门测试=伪造删行必被拒
# [MODIFY-GUARD] scripts/backtest/auto_mount.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-171 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""auto_mount 单元测试——文本手术引擎+only-add 红蓝门+映射表规则+SLE-1/SLE-4 分配链（MOD-BT-171）。

③ 段覆盖面：等权起步档（sleeve_plan）+ SLE-4 最大余数法 Σ 闭合（_apportion）+ SLE-1 证据
分配提案（sleeve_weights）与调权语义门（weight_adjust_assert）+ --rebalance 只读提案契约。
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from backtest.auto_mount import (  # noqa: E402
    CLASS_CANDIDATE_STATES,
    DEFAULT_SINGLE_SLEEVE_CAP,
    FAMILY_DEFAULT_ROUTE,
    IS_WIN_START,
    MIN_SEG_DAYS,
    NEW_SLEEVE_WEIGHT,
    OBSERVATION_CONF_FACTOR,
    PIT_TAIL_LAG,
    R2SIX,
    VOL_FLOOR,
    WEIGHT_GRID,
    WEIGHT_STEP_LIMIT,
    _apportion,
    insert_cell,
    insert_node_mount,
    insert_sleeve,
    mount_audit,
    only_add_assert,
    sleeve_plan,
    sleeve_weights,
    weight_adjust_assert,
    write_report,
)

# ---------- fixtures：最小地图片段（真实格式的等价样本） ----------
NODE_BLOCK = """- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
  materiality: critical
  decay_scan_frequency: monthly
"""

CELLS = """  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}
  - {node_id: TDM-E-L1, state: accumulation, mounted: [], confidence: proposed}
"""

SLEEVES = """  sleeves:
  - {strategy_ref: default-equity, weight: 0.14, activation_state: null}
  - {strategy_ref: STR-VREV-025, weight: 0.05, activation_state: [capitulation]}
  # 注释行
"""


# ---------- ① 映射表规则 ----------
class TestMappingRules:
    def test_family_fallback_route_whitelisted(self):
        # 2026-09-16 双层分离批：路由真源=注册表 mount_route 字段；代码兜底表只收无歧义家族。
        # multifactor=打分链（S07-G2 derive_class 兜底）；其余家族同族路由异构（value_reversal
        # 既有个股反转也有指数择时），设兜底必误挂——白名单外新增须先过架构评审。
        assert set(FAMILY_DEFAULT_ROUTE) == {"multifactor"}
        assert FAMILY_DEFAULT_ROUTE["multifactor"] == "TDM-E-L3-07-2"

    def test_candidate_states_keyed_by_family(self):
        # 候选态按分类家族键：择时类家族必须有候选态；选股/打分类 None 或缺省（缺省=不挂状态格）
        # 原断言 value_reversal=={capitulation,accumulation}、daban=={accumulation,expansion}
        # 因 SLE-3③ 盲区补映射改为下述集合：微观相位 overlay 让 euphoria/distribution
        # 自此可在判定窗出现（value_reversal=L1 防御腿主体四态全候选；daban=地图 L4
        # euphoria 格早已预登记，候选态据此补 euphoria；distribution 对 daban 按图注"不进"封闭）。
        assert CLASS_CANDIDATE_STATES["value_reversal"] == {"capitulation", "accumulation",
                                                            "euphoria", "distribution"}
        assert CLASS_CANDIDATE_STATES["momentum_trend"] == {"expansion", "ignition"}
        assert CLASS_CANDIDATE_STATES["daban"] == {"accumulation", "expansion", "euphoria"}
        assert CLASS_CANDIDATE_STATES["multifactor"] is None
        assert CLASS_CANDIDATE_STATES.get("sector_rotation", set()) == set()
        # 禁全态海选：任何候选态必须是六段词表子集
        for cands in CLASS_CANDIDATE_STATES.values():
            assert cands is None or cands <= {"capitulation", "accumulation", "ignition",
                                              "expansion", "euphoria", "distribution"}

    def test_route_resolution_prefers_explicit(self):
        # 显式 mount_route 优先于家族兜底（TSMALL/VAL 虽归 multifactor，路由仍走 L3-07-3 选股链）
        e = {"route": "TDM-E-L3-07-3", "cls": "multifactor"}
        assert (e.get("route") or FAMILY_DEFAULT_ROUTE.get(e["cls"])) == "TDM-E-L3-07-3"
        e2 = {"route": None, "cls": "multifactor"}
        assert (e2.get("route") or FAMILY_DEFAULT_ROUTE.get(e2["cls"])) == "TDM-E-L3-07-2"

    def test_r2six_states_are_six_phase(self):
        valid = {"capitulation", "accumulation", "ignition", "expansion", "euphoria", "distribution"}
        assert set(R2SIX.values()) <= valid
        assert "r1" not in R2SIX and "r2" not in R2SIX  # 低波/中波保守不路由（宁漏勿误）


# ---------- ② 文本级手术 ----------
class TestTextSurgery:
    def test_insert_node_mount_appends_and_idempotent(self):
        once = insert_node_mount(NODE_BLOCK, "TDM-E-L1", "STR-TEST-001", "evidence run=y")
        assert "strategy_ref: STR-TEST-001" in once
        assert "STR-VREV-025" in once  # 既有挂载保留（only-add）
        with pytest.raises(AssertionError):  # 幂等：已挂再插必拒
            insert_node_mount(once, "TDM-E-L1", "STR-TEST-001", "again")

    def test_insert_node_mount_bad_anchor(self):
        with pytest.raises(AssertionError):
            insert_node_mount("- node_id: TDM-X\n  name_zh: 无挂载区\n", "TDM-X", "STR-A", "e")

    def test_insert_cell_state_aware(self):
        # 2026-09-16 治本：一格一插，兄弟格子零扰动（旧实现向全部格子扩散，VREV-027 曾被污染四格）
        out = insert_cell(CELLS, "TDM-E-L1", "capitulation", "STR-TEST-001")
        assert "state: capitulation, mounted: [STR-VREV-025, STR-TEST-001]" in out
        assert "state: accumulation, mounted: []" in out  # 兄弟格零扰动
        assert out.count("confidence: proposed") == CELLS.count("confidence: proposed")
        with pytest.raises(AssertionError):  # 幂等：已在该格再插必拒
            insert_cell(out, "TDM-E-L1", "capitulation", "STR-TEST-001")
        out2 = insert_cell(CELLS, "TDM-E-L1", "accumulation", "STR-TEST-002")
        assert "state: accumulation, mounted: [STR-TEST-002]" in out2
        assert "state: capitulation, mounted: [STR-VREV-025]" in out2

    def test_insert_cell_unknown_state_rejected(self):
        with pytest.raises(AssertionError):
            insert_cell(CELLS, "TDM-E-L1", "nonexistent_state", "STR-TEST-001")

    def test_insert_sleeve_appends_after_last_str(self):
        out = insert_sleeve(SLEEVES, "STR-TEST-001", ["capitulation"])
        assert "strategy_ref: STR-TEST-001, weight: 0.05, activation_state: [capitulation]" in out
        lines = [l for l in out.splitlines() if "strategy_ref:" in l]
        assert lines[-1].startswith("  - {strategy_ref: STR-TEST-001")  # 追加在最后一条 STR 后
        null_case = insert_sleeve(SLEEVES, "STR-TEST-002", None)
        assert "activation_state: null" in null_case

    def test_insert_sleeve_anchor_not_unique(self):
        dup = SLEEVES + "  sleeves:\n"
        with pytest.raises(AssertionError):
            insert_sleeve(dup, "STR-A", None)


# ---------- ③ only-add 红蓝门（语义级） ----------
MAP_MIN = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 0.14, activation_state: null}
  - {strategy_ref: topn-momentum, weight: 0.07, activation_state: null}
"""


class TestOnlyAddGate:
    def test_semantic_additions_pass(self):
        added = MAP_MIN + """  - {strategy_ref: STR-NEW-001, weight: 0.05, activation_state: null}
"""
        only_add_assert(MAP_MIN, added)  # 新增 sleeve+等比缩水=立项设计行为，放行

    def test_forged_mount_deletion_rejected(self):
        tampered = MAP_MIN.replace("  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}\n", "")
        with pytest.raises(AssertionError, match="only-add"):
            only_add_assert(MAP_MIN, tampered)

    def test_modified_evidence_rejected(self):
        tampered = MAP_MIN.replace("run=x", "run=mutated")
        with pytest.raises(AssertionError):
            only_add_assert(MAP_MIN, tampered)

    def test_cell_deletion_rejected(self):
        tampered = MAP_MIN.replace("  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}\n", "")
        with pytest.raises(AssertionError):
            only_add_assert(MAP_MIN, tampered)

    def test_cell_mount_shrink_rejected(self):
        tampered = MAP_MIN.replace("mounted: [STR-VREV-025]", "mounted: []")
        with pytest.raises(AssertionError):
            only_add_assert(MAP_MIN, tampered)

    def test_non_proportional_weight_change_rejected(self):
        tampered = MAP_MIN.replace("weight: 0.14", "weight: 0.20")
        with pytest.raises(AssertionError, match="非等比"):
            only_add_assert(MAP_MIN, tampered)

    def test_new_sleeve_wrong_starter_rejected(self):
        tampered = MAP_MIN + "  - {strategy_ref: STR-NEW-001, weight: 0.08, activation_state: null}\n"
        with pytest.raises(AssertionError, match="起步档"):
            only_add_assert(MAP_MIN, tampered)


# ---------- ④ 等权起步档 ----------
class TestSleevePlan:
    def test_scale_preserves_total(self):
        old = [{"strategy_ref": "a", "weight": 0.14}, {"strategy_ref": "b", "weight": 0.105},
               {"strategy_ref": "c", "weight": 0.07}]
        plan = sleeve_plan(["STR-X", "STR-Y"], old)
        assert plan["STR-X"] == plan["STR-Y"] == NEW_SLEEVE_WEIGHT
        assert abs(sum(plan.values()) - 1.0) < 1e-9

    def test_old_weights_shrink_not_reorder(self):
        old = [{"strategy_ref": "a", "weight": 0.2}, {"strategy_ref": "b", "weight": 0.1}]
        plan = sleeve_plan(["STR-Z"], old)
        assert plan["a"] > plan["b"]  # 等比缩水保序
        assert abs(plan["a"] - round(0.2 * (0.95 / 0.3), 6)) < 1e-9  # 与实现同口径 6 位舍入


# ---------- ④' SLE-4 最大余数法：Σ 精确闭合（auto_mount.py:390） ----------
class TestApportionSLE4:
    @staticmethod
    def _units(out: dict[str, float], grid: int = WEIGHT_GRID) -> int:
        return sum(int(round(v * 10 ** grid)) for v in out.values())

    def test_thirds_close_exactly_where_naive_rounding_drifts(self):
        # SLE-4 立项病因：老实现逐权 round(,6) → 1/3 三等分得 0.999999（漂移 1e-6·n）。
        # 最大余数法先量化成整数份额再补余数，Σ 与目标在格点上恒等。
        out = _apportion(1.0, {"a": 1.0, "b": 1.0, "c": 1.0})
        assert out == {"a": 0.333334, "b": 0.333333, "c": 0.333333}  # 余数给首个（确定性）
        assert sum(out.values()) == 1.0, "Σ 闭合必须是精确 1.0，不是 1±1e-16"
        assert self._units(out) == 10 ** WEIGHT_GRID
        assert sum(round(1 / 3, 6) for _ in range(3)) < 1.0  # 反证：旧口径确实漂移

    def test_sevenths_and_partial_budget(self):
        out = _apportion(1.0, {f"s{i}": 1.0 for i in range(7)})  # 1/7 除不尽
        assert self._units(out) == 10 ** WEIGHT_GRID
        assert abs(sum(out.values()) - 1.0) < 1e-12
        assert max(out.values()) - min(out.values()) <= 10 ** -WEIGHT_GRID + 1e-15  # 只差一格
        part = _apportion(1.0 - NEW_SLEEVE_WEIGHT, {"a": 0.2, "b": 0.1})  # sleeve_plan 用的残预算
        assert self._units(part) == int(round((1.0 - NEW_SLEEVE_WEIGHT) * 10 ** WEIGHT_GRID))
        assert abs(sum(part.values()) - 0.95) < 1e-12

    def test_coarser_grid_and_negative_clamp(self):
        assert _apportion(1.0, {"a": 1.0, "b": 1.0, "c": 1.0}, grid=2) == {"a": 0.34, "b": 0.33, "c": 0.33}
        neg = _apportion(1.0, {"a": -1.0, "b": 3.0})  # 负权=0 参与（不产生负份额）
        assert neg == {"a": 0.0, "b": 1.0} and all(v >= 0.0 for v in neg.values())

    def test_degenerate_inputs_do_not_raise(self):
        assert _apportion(1.0, {}) == {}  # 空输入=空输出（不抛）
        assert _apportion(1.0, {"a": 0.0, "b": 0.0}) == {"a": 0.5, "b": 0.5}  # 全零退化等分
        assert _apportion(1.0, {"a": 1e-18, "b": 0.0}) == {"a": 1.0, "b": 0.0}  # 和低于格宽
        nan = _apportion(1.0, {"a": float("nan"), "b": 1.0})  # NaN 视作 0，不外泄
        assert nan == {"a": 0.0, "b": 1.0} and all(math.isfinite(v) for v in nan.values())

    def test_deterministic_and_replayable(self):
        w = {"a": 0.37, "b": 1 / 3, "c": 0.1234567891, "d": 7.5}
        assert _apportion(1.0, w) == _apportion(1.0, dict(reversed(list(w.items()))))  # 与键序无关

    def test_randomized_sweep_always_closes(self):
        # 性质测试：任意权重/任意总预算/任意格宽 → 整数格恒等 + 无负无 NaN + 浮点和偏差 <1e-12
        rng = random.Random(20260916)
        for _ in range(400):
            grid = rng.choice([2, 4, WEIGHT_GRID])
            total = rng.choice([1.0, 0.95, 0.5, 0.05])
            w = {f"r{i}": rng.choice([0.0, rng.random(), rng.random() * 1e3]) for i in range(rng.randint(1, 9))}
            out = _apportion(total, w, grid)
            assert all(math.isfinite(v) and v >= 0.0 for v in out.values())
            assert self._units(out, grid) == int(round(total * 10 ** grid))
            assert abs(sum(out.values()) - total) < 1e-12


# ---------- ④'' SLE-1 证据分配提案 sleeve_weights（auto_mount.py:459） ----------
def _ev(sr, vol, conf="verified", retired=False):
    return {"sr": sr, "vol": vol, "confidence": conf, "retired": retired}


class TestSleeveWeights:
    def test_monotone_in_sharpe(self):
        # 同波动同置信：SR 高者权高（分配分数 = SR×置信/波动）
        out = sleeve_weights([], {"A": _ev(1.0, 0.2), "B": _ev(3.0, 0.2)},
                             cap=0.9, step=1.0)
        assert out["B"] > out["A"] > 0.0
        assert abs(sum(out.values()) - 1.0) < 1e-12

    def test_monotone_inverse_in_vol(self):
        out = sleeve_weights([], {"A": _ev(2.0, 0.10), "B": _ev(2.0, 0.40)}, cap=0.9, step=1.0)
        assert out["A"] > out["B"]  # 逆波动=风险平价口径，非收益追逐
        # 分配分数 SR/vol 之比 4:1；先扣观察期下限再按比例水填 → 超下限部分严格按分数比
        assert abs((out["A"] - NEW_SLEEVE_WEIGHT) / (out["B"] - NEW_SLEEVE_WEIGHT) - 4.0) < 1e-9
        strict = sleeve_weights([], {"A": _ev(2.0, 0.10), "B": _ev(2.0, 0.40)},
                                cap=0.9, floor=0.0, step=1.0)
        assert abs(strict["A"] / strict["B"] - 4.0) < 1e-5  # 无下限时整体即严格 4:1

    def test_confidence_multiplier_on_score(self):
        # floor=0 去掉保底干扰 → verified/proposed 权重比 = 1/OBSERVATION_CONF_FACTOR
        out = sleeve_weights([], {"V": _ev(2.0, 0.2, "verified"), "P": _ev(2.0, 0.2, "proposed")},
                             cap=1.0, floor=0.0, step=1.0)
        assert out["V"] == pytest.approx(out["P"] / OBSERVATION_CONF_FACTOR, rel=1e-5)
        out2 = sleeve_weights([], {"V": _ev(2.0, 0.2, "verified"), "P": _ev(2.0, 0.2, "proposed")},
                              cap=1.0, step=1.0)  # 默认观察期下限抬高弱者 → 比值收敛
        assert out2["P"] >= NEW_SLEEVE_WEIGHT - 1e-12 and out2["V"] > out2["P"]

    def test_vol_floor_prevents_division_blowup(self):
        # vol=0/缺失 → VOL_FLOOR 兜底（防除零与近零波动爆炸分配）；同分必等分
        for ev in ({"A": _ev(1.0, 0.0), "B": _ev(1.0, 0.0)},
                   {"A": {"sr": 1.0, "confidence": "verified"}, "B": {"sr": 1.0, "confidence": "verified"}}):
            out = sleeve_weights([], ev, cap=0.9, step=1.0)
            assert out == {"A": 0.5, "B": 0.5} and abs(sum(out.values()) - 1.0) < 1e-12
        low = sleeve_weights([], {"A": _ev(1.0, 1e-9), "B": _ev(1.0, VOL_FLOOR)}, cap=0.9, step=1.0)
        assert low["A"] == pytest.approx(low["B"], abs=1e-12)  # 亚阈值波动被抬到同一地板

    def test_ties_split_evenly_within_grid(self):
        out = sleeve_weights([], {f"S{i}": _ev(2.0, 0.2) for i in range(3)}, cap=0.9, step=1.0)
        assert abs(sum(out.values()) - 1.0) < 1e-12
        assert max(out.values()) - min(out.values()) <= 10 ** -WEIGHT_GRID + 1e-15  # 只差一格（余数分配）

    def test_all_nonpositive_sharpe_freezes_old_weights(self):
        # 无正超额：候选全出局 → 老 sleeve 等比承接（Σ=1 恒等式），不抛不产生负权
        old = [{"strategy_ref": "a", "weight": 0.6}, {"strategy_ref": "b", "weight": 0.3}]
        out = sleeve_weights(old, {"a": _ev(-1.0, 0.2), "b": _ev(0.0, 0.2)})
        assert out == {"a": 0.666667, "b": 0.333333}
        assert abs(sum(out.values()) - 1.0) < 1e-12

    def test_empty_universe_returns_empty_without_crash(self):
        # 图上无 sleeve 且无正超额证据：无可分配对象 → 空提案（Σ=1 恒等式空真；调用方按"不动图"处理）
        assert sleeve_weights([], {"a": _ev(-1.0, 0.2)}) == {}
        assert sleeve_weights([], {}) == {}

    def test_single_candidate_takes_whole_budget(self):
        # 单候选+无冻结组：cap 水填后被 _apportion 归一化抬回 1.0（Σ=1 恒等式优先于上限）
        # 越界不由本件裁，由调权门拒（TestWeightAdjustGate::test_over_cap_rejected
        # + TestRebalanceProposalReadOnly::test_gate_rejects_infeasible_proposal_without_writing）
        out = sleeve_weights([], {"A": _ev(2.0, 0.2)})
        assert out == {"A": 1.0} and DEFAULT_SINGLE_SLEEVE_CAP < 1.0

    def test_step_band_limits_single_move(self):
        old = [{"strategy_ref": "A", "weight": 0.5}, {"strategy_ref": "B", "weight": 0.5}]
        out = sleeve_weights(old, {"A": _ev(3.0, 0.1), "B": _ev(0.5, 0.5)}, cap=1.0)  # 默认 step=0.25
        assert out["A"] == pytest.approx(0.5 + WEIGHT_STEP_LIMIT, abs=1e-9)
        assert out["B"] == pytest.approx(0.5 - WEIGHT_STEP_LIMIT, abs=1e-9)
        assert abs(sum(out.values()) - 1.0) < 1e-12

    def test_new_ref_gets_observation_floor_when_budget_allows(self):
        old = [{"strategy_ref": "A", "weight": 0.6}, {"strategy_ref": "B", "weight": 0.4}]
        out = sleeve_weights(old, {"A": _ev(0.5, 0.5), "B": _ev(0.4, 0.5), "N": _ev(4.0, 0.1)},
                             cap=0.9, step=1.0)
        assert "N" in out and out["N"] >= NEW_SLEEVE_WEIGHT - 1e-12
        assert abs(sum(out.values()) - 1.0) < 1e-12

    def test_retired_ref_frozen_not_silently_zeroed(self):
        # 退役件无分配分数，但老权重进冻结组承接残差——置 0 是 SLE-2 退役通道的职责，不在本件
        out = sleeve_weights([{"strategy_ref": "R", "weight": 0.5}, {"strategy_ref": "K", "weight": 0.5}],
                             {"R": _ev(9.0, 0.1, retired=True), "K": _ev(1.0, 0.2)}, cap=0.9, step=1.0)
        assert out["R"] == pytest.approx(0.5, abs=1e-9) and abs(sum(out.values()) - 1.0) < 1e-12

    def test_frozen_group_absorbs_residual_for_sigma_identity(self):
        # 底仓 0.9 无证据（冻结）→ 候选只在余下 0.1 预算内竞争，Σ 仍精确=1
        out = sleeve_weights([{"strategy_ref": "F", "weight": 0.9}], {"A": _ev(2.0, 0.2)}, cap=0.9, step=1.0)
        assert out["A"] == pytest.approx(0.1, abs=1e-9) and abs(sum(out.values()) - 1.0) < 1e-12

    def test_garbage_evidence_never_yields_nan_or_negative(self):
        old = [{"strategy_ref": "A", "weight": 0.5}, {"strategy_ref": "B", "weight": 0.5}]
        for ev in ({"A": _ev(float("nan"), 0.2), "B": _ev(1.0, 0.2)},
                   {"A": _ev(float("inf"), 0.2), "B": _ev(1.0, float("nan"))},
                   {"A": _ev(1.0, -3.0), "B": {"sr": None, "vol": None}},
                   {"A": _ev(1.0, 0.2, conf="_verified_"), "B": _ev(1.0, 0.2, retired=True)}):
            out = sleeve_weights(old, ev)
            assert all(math.isfinite(v) and v >= 0.0 for v in out.values()), f"{ev} -> {out}"
            assert abs(sum(out.values()) - 1.0) < 1e-12

    def test_infeasibility_guard_rejects_when_budget_cannot_pay_floors(self):
        # 预算 0.05 发不出 3×观察下限 0.05 → 显式拒。旧判据 len×min(floor,pool/len)>pool 恒假，
        # 会把下限静默降格为 0（高分优先吃光预算，低分员挂名零权重）——比不出提案更坏。
        with pytest.raises(ValueError, match="不可行"):
            sleeve_weights([{"strategy_ref": "F", "weight": 0.95}],
                           {f"A{i}": _ev(2.0, 0.2) for i in range(3)})

    def test_infeasibility_guard_boundary_pays_every_floor(self):
        # 判据是严格 len×floor > pool：恰好发得齐（2×0.05 == 预算 0.10）不得拒
        out = sleeve_weights([{"strategy_ref": "F", "weight": 0.90}],
                             {"A0": _ev(2.0, 0.2), "A1": _ev(1.0, 0.2)})
        assert out["A0"] >= NEW_SLEEVE_WEIGHT - 1e-12
        assert out["A1"] >= NEW_SLEEVE_WEIGHT - 1e-12
        assert abs(out["F"] - 0.90) < 1e-9
        assert abs(sum(out.values()) - 1.0) < 1e-12

    def test_output_is_gate_clean_for_healthy_map(self):
        # 集成：健康输入下 sleeve_weights 的提案必过自家调权门（提案面自证伪）
        old = [{"strategy_ref": "A", "weight": 0.5}, {"strategy_ref": "B", "weight": 0.5}]
        after = sleeve_weights(old, {"A": _ev(2.0, 0.2), "B": _ev(1.0, 0.2)}, cap=0.6)
        weight_adjust_assert({x["strategy_ref"]: x["weight"] for x in old}, after, cap=0.6)


# ---------- ④''' SLE-1 调权语义门 weight_adjust_assert（auto_mount.py:510） ----------
class TestWeightAdjustGate:
    BEFORE = {"a": 0.4, "b": 0.35, "c": 0.25}

    def test_well_formed_proposal_passes(self):
        weight_adjust_assert(self.BEFORE, {"a": 0.3, "b": 0.45, "c": 0.25}, cap=0.5)

    def test_new_ref_at_observation_floor_passes(self):
        weight_adjust_assert({"a": 1.0}, {"a": 0.95, "n": NEW_SLEEVE_WEIGHT}, cap=1.0)

    def test_sigma_not_one_rejected(self):
        with pytest.raises(AssertionError, match="Σw"):
            weight_adjust_assert(self.BEFORE, {"a": 0.4, "b": 0.35, "c": 0.2}, cap=0.5)

    def test_nan_weight_rejected(self):
        # NaN 与 Σ 恒等式同生俱灭：容差比较对 NaN 恒假 → 不可能蒙混过门
        with pytest.raises(AssertionError, match="Σw"):
            weight_adjust_assert(self.BEFORE, {"a": float("nan"), "b": 0.6, "c": 0.4}, cap=0.5)

    def test_over_cap_rejected(self):
        with pytest.raises(AssertionError, match="越界"):
            weight_adjust_assert(self.BEFORE, {"a": 0.5, "b": 0.4, "c": 0.1}, cap=0.45)

    def test_negative_weight_rejected(self):
        with pytest.raises(AssertionError, match="越界"):
            weight_adjust_assert({"a": 0.5, "b": 0.3, "c": 0.2}, {"a": 0.5, "b": 0.6, "c": -0.1}, cap=0.9)

    def test_member_set_shrink_rejected(self):
        # ref 只增不减：静默消失=伪造退役（须走 SLE-2 显式置 0）
        with pytest.raises(AssertionError, match="静默移除"):
            weight_adjust_assert(self.BEFORE, {"a": 0.5, "b": 0.5}, cap=1.0)

    def test_step_band_violation_rejected(self):
        with pytest.raises(AssertionError, match="超带宽"):
            weight_adjust_assert(self.BEFORE, {"a": 0.75, "b": 0.0, "c": 0.25}, cap=1.0,
                                 step=WEIGHT_STEP_LIMIT)

    def test_new_ref_below_observation_floor_rejected(self):
        with pytest.raises(AssertionError, match="观察期下限"):
            weight_adjust_assert({"a": 1.0}, {"a": 0.97, "n": 0.03}, cap=1.0)

    def test_tolerance_boundaries(self):
        # 区间 [0-tol, cap+tol] 的边界方向可预测：容差 1e-6 内的浮点噪声放行，越出即拒。
        up = {"a": 0.4, "b": 0.35, "c": 0.25}
        weight_adjust_assert(up, {"a": 0.4 + 9e-7, "b": 0.35, "c": 0.25 - 9e-7}, cap=0.4, step=1.0)
        with pytest.raises(AssertionError, match="越界"):
            weight_adjust_assert(up, {"a": 0.4 + 1e-5, "b": 0.35, "c": 0.25 - 1e-5}, cap=0.4, step=1.0)
        # 下界：cap=0.4 + 第四条零权 sleeve（退役件），使 Σ=1 与"微小负权"可同时成立
        low = {"a": 0.4, "b": 0.4, "c": 0.3, "d": 0.0}
        weight_adjust_assert(low, {"a": -9e-7, "b": 0.4, "c": 0.3, "d": 0.3000009}, cap=0.4, step=1.0)
        with pytest.raises(AssertionError, match="越界"):
            weight_adjust_assert(low, {"a": -1e-5, "b": 0.4, "c": 0.3, "d": 0.30001}, cap=0.4, step=1.0)

    def test_zeroed_retired_ref_passes(self):
        # 退役件显式置 0 是本门认可的合法形态（不违反只增不减：ref 仍在，权为 0）
        weight_adjust_assert({"a": 0.5, "b": 0.5}, {"a": 1.0, "b": 0.0}, cap=1.0, step=0.5)


# ---------- ④'''' --rebalance 只出提案不写图（rebalance_proposal auto_mount.py:915） ----------
class _ReadOnlyMap(Path):
    """写操作即炸的地图路径替身：为"提案永不写图"装硬闸（不靠事后比字节）。"""

    def write_text(self, *a, **k):
        raise AssertionError("rebalance_proposal 不得写地图（只出提案，落图须 Owner 门位）")

    def open(self, *a, **k):
        if a and any(m in str(a[0]) for m in ("w", "a", "x", "+")):
            raise AssertionError("rebalance_proposal 不得以写模式打开地图")
        return super().open(*a, **k)


MAP_RP = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-A, confidence: verified, evidence: 'run=x'}
  - {strategy_ref: STR-B, confidence: verified, evidence: 'run=y'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: distribution, mounted: [STR-A], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  aggregator:
    max_single_sleeve: 0.6
  sleeves:
  - {strategy_ref: STR-A, weight: 0.5, activation_state: [distribution]}
  - {strategy_ref: STR-B, weight: 0.5, activation_state: [accumulation]}
"""

ENTRIES_RP = [{"sid": "STR-A", "cls": "value_reversal", "code_path": "scripts/backtest/translated/c4_a.py",
               "lifecycle": "active", "route": "TDM-E-L1"},
              {"sid": "STR-B", "cls": "value_reversal", "code_path": "scripts/backtest/translated/c4_b.py",
               "lifecycle": "active", "route": "TDM-E-L1"}]


def _judge_stub(srs: dict[str, float]):
    """假 ②：按 sid 给全窗 SR/波动，并让 distribution 相位过门（判定缓存与 code mtime 皆不碰）。"""

    def _fake(e, panel):
        sr = srs[e["sid"]]
        seg = {"n": 61, "sr": sr, "vol": 0.2, "t": 4.0, "p": 1e-5, "oos_n": 0, "oos_sr": 0.0,
               "qvalue": 1e-5, "fdr_rejected": True, "accepted": True, "reject_reason": ""}
        return {"sid": e["sid"], "activated": ["distribution"], "segments": {"distribution": seg},
                "full": {"n": 300, "sr": sr, "vol": 0.2, "t": 4.0, "p": 1e-5}}

    return _fake


def _panel_rp():
    import pandas as pd
    idx = pd.bdate_range("2025-01-02", periods=300)
    six = pd.Series("accumulation", index=idx, dtype=object)
    six[100:161] = "distribution"
    return pd.DataFrame({"dom": "r2", "euphoria": False, "distribution": six == "distribution", "six": six})


def _no_write_primitives(*_a, **_k):
    raise AssertionError("rebalance 禁走写图原语 apply_ops")


def _rp_env(tmp_path, monkeypatch, map_text=MAP_RP, srs=None, entries=None):
    import backtest.auto_mount as am
    fake = tmp_path / "map.yaml"
    fake.write_text(map_text, encoding="utf-8")
    monkeypatch.setattr(am, "MAP_YAML", _ReadOnlyMap(fake))
    monkeypatch.setattr(am, "_cached_judge", _judge_stub(srs or {"STR-A": 2.0, "STR-B": 1.0}))
    monkeypatch.setattr(am, "apply_ops", _no_write_primitives)
    return am, fake, (entries if entries is not None else ENTRIES_RP)


class TestRebalanceProposalReadOnly:
    def test_proposal_never_touches_map_or_plan_file(self, tmp_path, monkeypatch):
        am, fake, entries = _rp_env(tmp_path, monkeypatch)
        before = fake.read_bytes()
        out = am.rebalance_proposal(entries, _panel_rp())
        assert fake.read_bytes() == before, "提案落地前后地图字节必须完全一致（只读契约）"
        assert sorted(x.name for x in tmp_path.iterdir()) == ["map.yaml"]  # 未旁生新文件
        assert out.get("diff"), "提案应给出可读 diff（0.5→0.6/0.4）"
        assert "-  - {strategy_ref: STR-A, weight: 0.5" in out["diff"]
        assert "+  - {strategy_ref: STR-A, weight: 0.6" in out["diff"]

    def test_proposal_shape_and_gate_field(self, tmp_path, monkeypatch):
        am, _fake, entries = _rp_env(tmp_path, monkeypatch)
        out = am.rebalance_proposal(entries, _panel_rp(), only={"STR-A", "STR-B"})
        assert set(out) == {"window", "cap", "fdr", "gate", "evidence", "before", "after",
                            "diff", "unmounted_new_refs", "requests"}
        # 提案里的 ref 全部在地图有块 → diff 可完整表达；有未挂 ref 时本键必须点名
        # （rescale_sleeves 只能动存量，否则读者会把"diff 只动存量"误读成"提案只动存量"）
        assert out["unmounted_new_refs"] == sorted(k for k in out["after"] if k not in out["before"])
        assert out["cap"] == 0.6  # 上限真源=地图 aggregator.max_single_sleeve（非兜底常量）
        assert out["gate"] == "pass"
        assert out["before"] == {"STR-A": 0.5, "STR-B": 0.5}
        assert out["after"] == {"STR-A": 0.6, "STR-B": 0.4}
        assert abs(sum(out["after"].values()) - 1.0) < 1e-12
        assert [r["strategy_ref"] for r in out["requests"]] == ["STR-A", "STR-B"]
        assert all(r["stage"] == "proven" and r["source"].endswith(".py") for r in out["requests"])

    def test_proposal_is_pure_deterministic(self, tmp_path, monkeypatch):
        am, _fake, entries = _rp_env(tmp_path, monkeypatch)
        panel = _panel_rp()
        first, second = am.rebalance_proposal(entries, panel), am.rebalance_proposal(entries, panel)
        assert first["after"] == second["after"] and first["diff"] == second["diff"]

    def test_gate_rejects_infeasible_proposal_without_writing(self, tmp_path, monkeypatch):
        # 底仓 0.9 无证据且上限 0.25 → 提案天然越界：门必须自证伪并仍不落笔
        tight = MAP_RP.replace("max_single_sleeve: 0.6", "max_single_sleeve: 0.25").replace(
            "  - {strategy_ref: STR-A, weight: 0.5, activation_state: [distribution]}\n"
            "  - {strategy_ref: STR-B, weight: 0.5, activation_state: [accumulation]}\n",
            "  - {strategy_ref: STR-A, weight: 0.9, activation_state: [distribution]}\n"
            "  - {strategy_ref: STR-B, weight: 0.1, activation_state: [accumulation]}\n")
        am, fake, entries = _rp_env(tmp_path, monkeypatch, map_text=tight,
                                    srs={"STR-A": 2.0, "STR-B": 1.0}, entries=ENTRIES_RP[:1])
        out = am.rebalance_proposal(entries, _panel_rp())
        assert out["gate"].startswith("reject:") and "越界" in out["gate"]
        assert fake.read_text(encoding="utf-8") == tight  # 被拒不写=与通过时同样只读

    def test_cli_rebalance_prints_proposal_only(self, tmp_path, monkeypatch, capsys):
        am, fake, entries = _rp_env(tmp_path, monkeypatch)
        monkeypatch.setattr(am, "load_registry_entries", lambda: entries)
        monkeypatch.setattr(am, "load_dominant", _panel_rp)
        monkeypatch.setattr(am, "CACHE", tmp_path / "never_written_judge_cache.json")
        monkeypatch.setattr(sys, "argv", ["auto_mount.py", "--rebalance"])
        am.main()
        printed = capsys.readouterr().out
        assert "[REBALANCE] 只出提案不写图" in printed
        assert '"gate": "pass"' in printed and "STR-A" in printed
        assert fake.read_text(encoding="utf-8") == MAP_RP
        assert not (tmp_path / "never_written_judge_cache.json").exists()  # 判定缓存亦不写盘


# ---------- ⑥ 钩子②③：月度审计+报告落盘 ----------
class TestMountAudit:
    def test_audit_detects_cell_drift(self, tmp_path, monkeypatch):
        """格子 mounted 里的 STR-* 不在节点挂载区 = 漂移必报（审计核心职责）。"""
        import backtest.auto_mount as am
        map_drift = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-GHOST-999], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 1.0, activation_state: null}
"""
        fake_map = tmp_path / "map.yaml"
        fake_map.write_text(map_drift, encoding="utf-8")
        monkeypatch.setattr(am, "MAP_YAML", fake_map)
        monkeypatch.setattr(am, "validate_map", lambda: [])
        out = am.mount_audit(scan_frequency=None)
        assert out["audit"] == "fails"
        assert out["drift"] and "STR-GHOST-999" in out["drift"][0]

    def test_audit_shape_clean(self, tmp_path, monkeypatch):
        """无漂移+无 fails 时 audit=ok；decay 档失败降级为 error 字段不阻断。"""
        import backtest.auto_mount as am
        map_clean = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 1.0, activation_state: null}
"""
        fake_map = tmp_path / "map.yaml"
        fake_map.write_text(map_clean, encoding="utf-8")
        monkeypatch.setattr(am, "MAP_YAML", fake_map)
        monkeypatch.setattr(am, "validate_map", lambda: [])
        out = mount_audit(scan_frequency=None)
        assert out["audit"] == "ok" and out["drift"] == [] and out["mounted_count"] == 1


class TestWriteReport:
    def test_report_written_with_three_sections(self, tmp_path):
        # 原断言 "+3.72(73d)"（segments 值=(n,sr) 二元组）因 SLE-3①② 改为逐相位证据 dict
        # （sr/t/p/n/oos + FDR 回执 accepted/reject_reason），报告口径随新 schema 渲染。
        seg = {"n": 73, "sr": 3.72, "t": 4.1, "p": 3.1e-5, "vol": 0.18,
               "oos_n": 40, "oos_sr": 1.2, "qvalue": 3.1e-5, "fdr_rejected": True,
               "accepted": True, "reject_reason": ""}
        payload = {
            "diff": "+++ map.after\n+mount line",
            "judgements": [{"sid": "STR-X-001", "cls": "value_reversal", "node": "TDM-E-L1",
                             "activated": ["capitulation"],
                             "segments": {"capitulation": seg}}],
            "fails": [],
            "weights": "{\"STR-X-001\": 0.05}",
            "window": "2020-01-01..2026-09-10",
            "fdr": {"m": 1, "q": 0.10, "threshold": 0.01, "n_rejected": 1, "hlz": False},
        }
        rp = write_report(payload, "STR-X-001", out_dir=tmp_path)
        text = rp.read_text(encoding="utf-8")
        assert "## 挂了哪" in text and "## 为什么" in text and "## 证据指针" in text
        assert "STR-X-001" in text and "SR=+3.72" in text and "n=73d" in text and "TDM-E-L1" in text
        assert "BHY-FDR q=0.1" in text  # 多重检验回执进报告（SLE-3①）

    def test_report_replay_zero_diff_shape(self, tmp_path):
        payload = {"diff": None, "judgements": [], "fails": [], "weights": "{}"}
        rp = write_report(payload, "", out_dir=tmp_path)
        assert "零 diff" in rp.read_text(encoding="utf-8")


# ---------- ⑤ 常量契约 ----------
class TestConstants:
    def test_window_frozen(self):
        # 原断言 IS_WIN == ("2020-01-01", "2023-12-31") 因 SLE-3② 解冻改为：起点锚保留
        # 2020-01-01（与 C4 冻结口径可比），终点禁写死——由快照表最新可用日回退
        # PIT_TAIL_LAG 行动态派生（见 load_phase_panel / window_of）。
        assert IS_WIN_START == "2020-01-01"
        assert PIT_TAIL_LAG >= 1  # PIT 尾窗：尾日证据未定不入样

    def test_min_seg_days(self):
        assert MIN_SEG_DAYS == 30

    def test_starter_weight(self):
        assert NEW_SLEEVE_WEIGHT == 0.05
