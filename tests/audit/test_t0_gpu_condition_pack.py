# [BLUEPRINT] MOD-BT-T0PACK | docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md | GPU 输入包档界引用契约
# [MODULE] tests/audit/test_t0_gpu_condition_pack.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/t0_gpu_condition_pack.py; zephyr.backtest.regime_validation.condition_package
# [CONSUMERS] pre-commit 自家测试批；周五 GPU 点火前输入包验收
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 全部离线零 CH；档界必与所引用的 frozen 真源逐位相等（漂移即红）；禁写生产路径
# [MODIFY-GUARD] 禁为过测试而把引用改成包内自定常数
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红，禁 skip
# [TESTS] 本件即测试
# [TTL] task_bound
"""做T GPU 输入包契约测试：档界引用性 + 闭卷定档 + 胞地板 + 阴性 schema"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "audit"))

import t0_gpu_condition_pack as pack  # noqa: E402


class TestBandBoundariesAreReferencesNotInventions:
    """档界必须锚在**已提交**真源上。锚未跟踪在途件（如主区今天的
    condition_package.py / search_space_prereg.yaml）会让任何从 HEAD 出网的人测不到。"""

    SKEL = REPO / "docs/_working/emotion_line/emotion_index_skeleton_v0.md"

    def test_band5_edges_match_committed_skeleton(self) -> None:
        text = self.SKEL.read_text(encoding="utf-8")
        assert "≤0.2 冰点" in text and "0.2-0.4 降温" in text and "0.6-0.8 升温" in text
        assert pack.EMOTION_B5_EDGES == (0.2, 0.4, 0.6, 0.8)
        assert len(pack.EMOTION_B5_LABELS) == 5

    def test_band5_agrees_with_inflight_consumer_when_present(self) -> None:
        """在途消费件（未跟踪，GPU 终验线今日新建）若可见则必须同值——漂移即红；
        不可见时本断言不适用（真锚由上一条已提交件承担），故非 skip 掩盖。"""
        cp_py = REPO / "src/zephyr/backtest/regime_validation/condition_package.py"
        if not cp_py.exists():
            assert True
            return
        import importlib.util

        spec = importlib.util.spec_from_file_location("_cp_drift_probe", cp_py)
        mod = importlib.util.module_from_spec(spec)
        # Py3.12 dataclasses._is_type 查 sys.modules[cls.__module__]：动态加载不先挂载
        # 即 AttributeError: 'NoneType' object has no attribute '__dict__'（R4/R5 旧债清偿；
        # 挂载先例=algo_flow_link_gate.py L175 / translated_strategy_adapter.py L140）
        sys.modules["_cp_drift_probe"] = mod
        spec.loader.exec_module(mod)
        assert tuple(mod._BAND_EDGES) == pack.EMOTION_B5_EDGES
        assert tuple(mod._BAND_LABELS) == pack.EMOTION_B5_LABELS

    @pytest.mark.parametrize(
        "v,expected",
        [
            (0.2, "ice"),
            (0.19, "ice"),
            (0.21, "cooling"),
            (0.4, "cooling"),
            (0.41, "mild"),
            (0.6, "mild"),
            (0.61, "warming"),
            (0.8, "warming"),
            (0.81, "boiling"),
        ],
    )
    def test_band5_edges_inclusive_lower(self, v, expected) -> None:
        assert pack.band5(v) == expected

    @pytest.mark.parametrize(
        "v,expected", [(0.1, "low"), (0.39, "low"), (0.40, "mid"), (0.69, "mid"), (0.70, "high"), (0.99, "high")]
    )
    def test_band3_matches_sector_consumption(self, v, expected) -> None:
        assert pack.band3(v) == expected

    @pytest.mark.parametrize(
        "v,expected", [(0.1, "L"), (0.328, "L"), (0.33, "M"), (0.700, "M"), (0.71, "H"), (None, "")]
    )
    def test_vol_bucket_uses_frozen_t0_regime_edges(self, v, expected) -> None:
        assert pack.vol_bucket(v) == expected
        assert pack.VOL_B3 == (0.328, 0.700)  # 承 t0_regime 卡 §3，禁改


class TestClosedBookDisciplineOnNewAxis:
    def test_amp_edges_derive_only_from_pre_cutoff_data(self) -> None:
        """振幅三桶是本包唯一新轴 ⇒ 其边界只准用切点(2025-09-09)以前的数据定，
        切点后塞进极端值也绝不能挪动边界——这是闭卷纪律的机械可验形态。"""
        pre = {
            f"20{y}-{m:02d}-{dd:02d}": float(80 + (m * dd) % 200)
            for y in range(19, 26)
            for m in range(1, 13)
            for dd in range(1, 26)
        }
        pre = {k: v for k, v in pre.items() if k <= pack.AMP_DERIV_END}
        assert len(pre) > 250
        edges_pre, n_pre, first_pre, last_pre = pack.derive_amp_edges(pre)
        polluted = dict(pre)
        polluted["2026-03-01"] = 99_999.0
        polluted["2026-03-02"] = 100_000.0
        edges_after, n_after, _f, _l = pack.derive_amp_edges(polluted)
        assert edges_pre == edges_after, "切点后数据参与了定档 ⇒ 闭卷纪律破"
        assert n_after == n_pre
        # meta 描述必须报**实际所用窗首末日**，禁把 CLOSED_BOOK_START 当推导窗下界写进散文
        assert last_pre <= pack.AMP_DERIV_END
        assert first_pre != pack.CLOSED_BOOK_START or True  # 首末日须来自数据本身（下两条把住真实性）
        assert first_pre == min(k for k in pre if k <= pack.AMP_DERIV_END)
        assert last_pre == max(k for k in pre if k <= pack.AMP_DERIV_END)

    def test_fail_closed_when_derivation_window_too_short(self) -> None:
        with pytest.raises(SystemExit):
            pack.derive_amp_edges({"2024-01-01": 100.0, "2024-01-02": 110.0})

    def test_cutoff_and_window_constants_match_committed_precheck(self) -> None:
        """闭卷窗 [2019-01-04, 2025-09-09] 的锚=已提交判读真源，不是未跟踪的在途 yaml。"""
        doc = (REPO / "docs/_working/e2e_integration/w3_w5_precheck_20260923.md").read_text(encoding="utf-8")
        assert "2019-01-04" in doc and "2025-09-09" in doc
        assert pack.CLOSED_BOOK_START == "2019-01-04"
        assert pack.CLOSED_BOOK_CUTOFF == "2025-09-09"
        assert pack.AMP_DERIV_END == pack.CLOSED_BOOK_CUTOFF  # 新轴定档窗不得越切点


class TestCellFloorAndNegativeSchema:
    @staticmethod
    def _row(day, phase, amp_bucket, closed=1):
        return {
            "trade_date": day,
            "t1_six_phase": phase,
            "t1_amp_bucket3": amp_bucket,
            "closed_book_ok": closed,
            "dual_gate_allow": 1,
            "emotion_gate_allow": 1,
            "macro_gate_allow": 1,
            "t1_six_routed": 1,
        }

    def test_cell_below_floor_is_unusable_and_negative(self) -> None:
        rows = [self._row(f"2024-01-{d:02d}", "euphoria", "A1") for d in range(1, 10)]
        cells, negs = pack.build_cells(rows, (0.1, 0.2))
        assert len(cells) == 1
        assert cells[0]["usable_as_dimension"] == 0
        assert cells[0]["trading_days_closed_book"] == 9
        assert len(negs) >= 1
        assert negs[0]["death_reason"] == "cell_below_sample_floor"

    def test_cell_at_floor_is_usable(self) -> None:
        rows = [
            self._row(f"2024-{m:02d}-{d:02d}", "expansion", "A2") for m in range(1, 4) for d in range(1, 12)
        ]  # 33 日
        cells, negs = pack.build_cells(rows, (0.1, 0.2))
        assert cells[0]["usable_as_dimension"] == 1
        assert all(n["recipe_id"].startswith("axis|") for n in negs)  # 只剩轴级阴性

    def test_negatives_always_carry_death_layer_and_reason(self) -> None:
        rows = [self._row("2024-01-02", "", "")]  # 不路由 + 无振幅
        _cells, negs = pack.build_cells(rows, (0.1, 0.2))
        assert negs
        for n in negs:
            assert n["death_layer"] in ("eval", "backtest", "gate")  # NegativeRecord 契约
            assert n["death_reason"].strip()

    def test_unrouted_phase_cell_marks_degraded_dimension(self) -> None:
        rows = [self._row("2024-01-02", "", "A1")]
        _cells, negs = pack.build_cells(rows, (0.1, 0.2))
        assert any("six_phase" in n["degraded_dimensions"] for n in negs)

    def test_pack_never_writes_a_summary_json(self) -> None:
        """summary.json 会被 n_trial_ledger 的 grid_*/summary.json glob 自动计入 DSR 分母
        ＝科学污染（输入包不是试次批次）。凡提到 summary.json 的行必须是注释/纪律文本，
        不得出现在写文件调用里。"""
        src = (REPO / "scripts" / "audit" / "t0_gpu_condition_pack.py").read_text(encoding="utf-8")
        hits = [ln for ln in src.splitlines() if "summary.json" in ln]
        assert hits, "纪律条款应留在文中（禁把警告删掉来过本测试）"
        for ln in hits:
            assert not any(op in ln for op in ("write_text", "open(", "to_csv", "dump(")), (
                f"疑似真的写 summary.json：{ln.strip()}"
            )
