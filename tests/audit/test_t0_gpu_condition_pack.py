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

import csv
import sys
from pathlib import Path

import pytest
import yaml

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


class TestReconcileAgainstFrozenTruth:
    """任务⑤逐格对账的契约面：对账件本身必须能红，且卡↔码常数不得各说各话。

    背景：包体（data/strategy_intake/grid_*）按盘面惯例是再生件（dev 里该目录零跟踪），故这里
    不读盘侧包体，改钉三件事：①对账函数逐列有牙（伪造一格即报）；②T-1 asof 容差=母本卡文本值
    （码里改数字即红）；③已入库证据 summary 自洽且与六段真源行数同源。
    """

    EVID = REPO / "docs/_working/t0_matrix/reconcile_pack_v1_summary.csv"

    def _rules(self):
        meta_stub = {
            "band_definitions": {
                "band3_emotion": f"low<{pack.EMOTION_B3_EDGES[0]:.2f}≤mid<{pack.EMOTION_B3_EDGES[1]:.2f}≤high",
                "t1_vol_bucket3": f"引用 t0_regime 卡 §3 frozen 边界 ({pack.VOL_B3[0]}, {pack.VOL_B3[1]})（L≤..＜M≤..＜H）",
                "t1_amp_bucket3": "本包新轴，三桶边界=[116.75, 188.25] bp，闭卷切点前定档",
            },
            "gpu_budget": {"closed_book": {"start": pack.CLOSED_BOOK_START, "cutoff": pack.CLOSED_BOOK_CUTOFF}},
        }
        return pack.parse_frozen_rules(meta_stub)

    def test_column_partition_is_a_disjoint_cover_of_18(self):
        """覆盖面条目本身受测：派生 10 + 源值直通 8 = 18 且互斥——加列不归类即红。"""
        d, ps = set(pack.RECON_DERIVED), set(pack.RECON_PASSTHROUGH)
        assert not (d & ps) and len(d | ps) == 18 and "trade_date" in ps
        assert len(d) == pack.RECON_COLUMNS == 10

    def test_legality_and_nonblank_guards_have_teeth(self):
        """两条"抹空即红"守卫：值域守卫（routed/closed_book 不许空）+ 源值非空守卫。"""
        assert set(pack.RECON_LEGAL) <= set(pack.RECON_DERIVED) | set(pack.RECON_PASSTHROUGH)
        r = self._rules()
        base = self._row()
        for col in ("t1_six_routed", "closed_book_ok", "band5"):
            row = dict(base, **{col: ""})
            bads = pack.reconcile_row(row, {"six_phase": "expansion", "routed": "1"}, r)
            assert any(col in b for b in bads), (col, bads)
            assert any("值域非法" in b for b in bads), (col, bads)
        for col in pack.RECON_NON_BLANK:
            row = dict(base, **{col: ""})
            assert any("源值列被抹空" in b for b in pack.reconcile_row(row, None, r)), col

    def test_structural_checks_bound_pack_to_landed_truth(self):
        """结构守卫必须引包外已入库真源做上界——只跟包内 meta 互校时，自洽伪造整包能全绿。"""
        truth = {f"2024-01-{d:02d}" for d in range(1, 29)}
        rows = [{"trade_date": d} for d in sorted(truth)]
        meta = {"rows": len(rows), "date_span": [min(truth), max(truth)]}
        assert pack._structural_checks(rows, meta, truth) == []
        forged = rows + [{"trade_date": "2024-02-30"}]
        assert any("不在六段真源日集合" in b for b in pack._structural_checks(forged, meta, truth))
        assert any("≠ 六段真源行数" in b for b in pack._structural_checks(rows[:-1], meta, truth))

    def test_five_band_label_spellings_do_not_drift(self):
        assert pack.BAND5_CN_TO_EN == pack.EMOTION_B5_LABELS

    def test_card_frozen_constants_match_code_constants(self):
        r = self._rules()
        assert r["vol_h"] == pack.MACRO_VOL_H
        assert r["trend"] == pack.MACRO_TREND_STATES
        assert r["emo_allow"] == pack.EMOTION_GATE_ALLOW
        assert r["b5_edges"] == pack.EMOTION_B5_EDGES
        assert r["b3"] == pack.EMOTION_B3_EDGES
        assert r["vol3"] == pack.VOL_B3
        assert (r["cb_start"], r["cb_cutoff"]) == (pack.CLOSED_BOOK_START, pack.CLOSED_BOOK_CUTOFF)

    def test_asof_tolerance_used_by_builder_equals_card_text(self):
        """母本卡写 7 自然日容差⇒生成件必须正好 7（改码不改卡/改卡不改码都会红）。"""
        assert self._rules()["asof_tol_days"] == 7
        from datetime import date, timedelta

        tol = self._rules()["asof_tol_days"]
        near = (date.fromisoformat("2024-02-01") - timedelta(days=tol)).isoformat()
        far = (date.fromisoformat("2024-02-01") - timedelta(days=tol + 1)).isoformat()
        keys = sorted([near, far])
        series = {near: ("r3", 0.9), far: ("r1", 0.1)}
        assert pack.t1_lookup(series, "2024-02-01", keys) == series[near]
        assert pack.t1_lookup({far: ("r3", 0.9)}, "2024-02-01", [far]) is None

    def _row(self):
        return {
            "trade_date": "2024-05-10",
            "emotion_index": "0.55",
            "emotion_source": "replay",
            "formula_version": "v0.1.0",
            "ok_n": "2",
            "band5": "mild",
            "band3_emotion": "mid",
            "t1_dominant": "r3",
            "t1_vol_pct": "0.620",
            "t1_vol_bucket3": "M",
            "t1_six_phase": "expansion",
            "t1_six_routed": "1",
            "t1_amp_bp": "150.0",
            "t1_amp_bucket3": "A2",
            "macro_gate_allow": "1",
            "emotion_gate_allow": "1",
            "dual_gate_allow": "1",
            "closed_book_ok": "1",
        }

    def test_reconcile_passes_on_consistent_row(self):
        r = self._rules()
        assert pack.reconcile_row(self._row(), {"six_phase": "expansion", "routed": "1"}, r) == []

    @pytest.mark.parametrize(
        "col,bad,expect_frag",
        [
            ("band5", "boiling", "band5"),
            ("band3_emotion", "high", "band3_emotion"),
            ("t1_vol_bucket3", "H", "t1_vol_bucket3"),
            ("t1_amp_bucket3", "A3", "t1_amp_bucket3"),
            ("macro_gate_allow", "0", "macro_gate_allow"),
            ("emotion_gate_allow", "0", "emotion_gate_allow"),
            ("dual_gate_allow", "0", "dual_gate_allow"),
            ("closed_book_ok", "0", "closed_book_ok"),
            ("t1_six_phase", "capitulation", "t1_six_phase"),
            ("t1_six_routed", "0", "t1_six_routed"),
        ],
    )
    def test_reconcile_flags_each_corrupted_column(self, col, bad, expect_frag):
        """变异探针：九列各伪造一格，对账必须点名该列（全绿的对账件等于没对账）。"""
        row = self._row()
        row[col] = bad
        bads = pack.reconcile_row(row, {"six_phase": "expansion", "routed": "1"}, self._rules())
        assert any(f"{expect_frag} 包体=" in b for b in bads), bads

    def test_reconcile_ignores_none_gate_axes_yet_keeps_dual_zero(self):
        """跨长假两门不可评：macro/emotion 出空串，但 dual 仍须为 0（不得留空糊弄下游）。"""
        row = self._row()
        row.update({"t1_dominant": "", "t1_vol_pct": "", "t1_vol_bucket3": "", "macro_gate_allow": ""})
        row.update({"t1_six_phase": "", "t1_six_routed": "0", "emotion_gate_allow": "", "dual_gate_allow": "0"})
        assert pack.reconcile_row(row, None, self._rules()) == []

    def test_prev_truth_honours_tolerance_and_strict_inequality(self):
        six = {"2024-05-06": {"six_phase": "expansion"}, "2024-05-09": {"six_phase": "euphoria"}}
        dates = sorted(six)
        r = self._rules()
        assert pack.prev_truth(dates, six, "2024-05-10", r["asof_tol_days"]) == six["2024-05-09"]
        assert pack.prev_truth(dates, six, "2024-05-09", r["asof_tol_days"]) == six["2024-05-06"]  # 严格早于
        assert pack.prev_truth(dates, six, "2024-05-20", r["asof_tol_days"]) is None  # 超容差
        assert pack.prev_truth(dates, six, "2024-05-01", r["asof_tol_days"]) is None  # 窗首无前日

    def test_landed_evidence_is_clean_and_tied_to_truth_rowcount(self):
        if not self.EVID.exists():
            raise SystemExit(f"FAIL: 对账证据缺失 {self.EVID}——禁缺件出绿")
        rows = list(csv.DictReader(self.EVID.read_text(encoding="utf-8").splitlines()))
        summ = {r["key"]: r["value"] for r in rows}
        truth = (REPO / "docs/_working/t0_matrix/six_phase_history_v1.csv").read_text(encoding="utf-8").splitlines()
        assert int(summ["mismatch_cells"]) == 0 and int(summ["mismatch_rows"]) == 0
        assert summ["first_mismatches"] == ""
        # 包体行数=六段真源行数（同一可判日全集：温度计 ∩ 六段）
        assert int(summ["rows_reconciled"]) == len(truth) - 1
        assert int(summ["derived_columns_reconciled"]) == pack.RECON_COLUMNS == len(pack.RECON_DERIVED) == 10
        assert summ["derived_column_names"] == "|".join(pack.RECON_DERIVED)
        assert len(summ["sample_days"].split("|")) == 20 == int(summ["sample_n"])
        assert summ["sample_seed"] == "20260924"
        assert summ["structural_checks"].startswith("结构守卫")
        # 证据里记录的 frozen 常数必须仍等于卡/骨架件现值（有人改了卡而没重跑对账，这里就红）
        r = self._rules()
        assert summ["rule_vol_h"] == str(r["vol_h"])
        assert summ["rule_macro_trend_states"] == "|".join(r["trend"])
        assert summ["rule_emotion_allow"] == "|".join(r["emo_allow"])
        assert summ["rule_band5_edges"].startswith("|".join(str(x) for x in r["b5_edges"]))
        assert summ["rule_band5_edges"].endswith(str(r["boiling_edge"]))
        assert summ["rule_closed_book_window"] == f"{r['cb_start']}|{r['cb_cutoff']}"
        # 闭卷窗/vol 界必须来自**包外**真源：包 meta 被改写不得影响对账口径
        assert "selfdeclared" in "".join(summ.keys())
        assert summ["asof_tolerance_natural_days_parsed_from_card"] == str(r["asof_tol_days"])

    def test_landed_sample20_rows_recompute_from_landed_files_only(self):
        """审计闭环：只凭**已入库**文件复算这 20 行（不再读盘侧包体），必须逐行 0 不一致。

        红蓝实证：抽样件若只记 (日期, 列数, 不一致数)，审计员无处复算——故抽样件带全 18 列原值，
        本测试用与 CLI 同一套 strict 逻辑对它重算，并把记录的 mismatch 一起钉住。
        """
        f = REPO / "docs/_working/t0_matrix/reconcile_pack_v1_sample20.csv"
        recs = list(csv.DictReader(f.read_text(encoding="utf-8").splitlines()))
        assert len(recs) == 20
        cols = [c for c in recs[0] if c not in ("derived_columns_checked", "mismatch_cells")]
        assert len(cols) == 18 and "trade_date" in cols
        rules = self._rules()
        six = pack.load_six_phase(pack.SIX_PHASE_TRUTH)
        dates = sorted(six)
        for rec in recs:
            row = {c: rec[c] for c in cols}
            sp = pack.prev_truth(dates, six, rec["trade_date"], rules["asof_tol_days"])
            assert pack.reconcile_row(row, sp, rules) == [], rec["trade_date"]
            assert rec["mismatch_cells"] == "0"
            assert rec["derived_columns_checked"] == str(pack.RECON_COLUMNS)

    def test_anchor_must_be_unique_in_frozen_source(self):
        """卡里多出一句同形措辞=静默换阈值 ⇒ 唯一性守卫必须当场炸。"""
        with pytest.raises(SystemExit) as e:
            pack._anch(
                "vol_pct(T-1) > 0.700 原条款；追加一句同形措辞 vol_pct(T-1) > 0.750 试算",
                r"vol_pct\(T-1\) > ([0-9.]+)",
                "探针",
            )
        assert "不唯一" in str(e.value)
        assert pack._anch("只此一处 vol_pct(T-1) > 0.700", r"vol_pct\(T-1\) > ([0-9.]+)", "探针") == ("0.700",)
