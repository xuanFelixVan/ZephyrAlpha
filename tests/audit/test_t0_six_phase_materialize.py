# [BLUEPRINT] MOD-BT-T0SIX | docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md | §2.2 情绪门真源契约
# [MODULE] tests/audit/test_t0_six_phase_materialize.py
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/audit/t0_six_phase_materialize.py; scripts/backtest/auto_mount.py
# [CONSUMERS] pre-commit 自家测试批；红蓝 PIT 断言
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 零 CH（全部合成面板/monkeypatch）；每条断言须能红；禁写生产路径
# [MODIFY-GUARD] 禁为过测试而在物化件内自定阈值
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红，禁 skip
# [TESTS] 本件即测试
# [TTL] task_bound
"""六段相位物化件契约测试：映射零自定 + 不路由不硬塞 + 闭卷标记 + 双写去重（含 auto_mount 修复回归）"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "audit"))
sys.path.insert(0, str(REPO / "scripts" / "backtest"))

import auto_mount as am  # noqa: E402
import t0_six_phase_materialize as m  # noqa: E402


def _panel(dates, doms, euph, dist):
    idx = pd.DatetimeIndex(pd.to_datetime(dates))
    return pd.DataFrame(
        {
            "dom": doms,
            "euphoria": euph,
            "distribution": dist,
            "six": [
                am.resolve_six_phase(
                    pd.Series(doms, index=idx), pd.DataFrame({"euphoria": euph, "distribution": dist}, index=idx)
                ).iloc[i]
                for i in range(len(dates))
            ],
        },
        index=idx,
    )


class TestMappingIsReferenceNotInvention:
    def test_module_defines_no_local_phase_mapping(self) -> None:
        """本包禁自带六段映射字典（真源=auto_mount.R2SIX）。出现字面 'rN'→相位 的赋值即红。"""
        src = (REPO / "scripts" / "audit" / "t0_six_phase_materialize.py").read_text(encoding="utf-8")
        code = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
        assert not re.search(
            r"[\"']r\d+[\"']\s*:\s*[\"'](capitulation|accumulation|ignition|expansion|euphoria|distribution)", code
        )

    def test_leg_macro_matches_auto_mount_r2six_for_every_state(self) -> None:
        for st in ("r1", "r2", "r3", "r4", "r10", "r11", "r12", "r99", "None"):
            assert m._leg_macro(st) == am.R2SIX.get(st, "")

    def test_allow_set_is_the_cards_three_upside_segments(self) -> None:
        assert set(m.EMOTION_GATE_ALLOW) == {"ignition", "expansion", "euphoria"}


class TestRowSemantics:
    def test_unrouted_day_has_empty_phase_not_nearest_neighbor(self) -> None:
        """r1/r2 无六段对应且无微观相位 ⇒ 不路由，six_phase 必为空串（禁硬塞最近邻相位）。"""
        panel = _panel(["2024-01-02", "2024-01-03"], ["r1", "r2"], [False, False], [False, False])
        rows = m.to_rows(panel)
        assert all(r["six_phase"] == "" and r["routed"] == 0 for r in rows)

    def test_expansion_day_is_routed_and_allowed(self) -> None:
        panel = _panel(["2024-01-02"], ["r3"], [False], [False])
        rows = m.to_rows(panel)
        assert rows[0]["six_phase"] == "expansion"
        assert rows[0]["routed"] == 1

    def test_euphoria_overlay_wins_over_unmapped_macro(self) -> None:
        """r1（宏观未映射）但微观亢奋双确认 ⇒ 由微观腿补出 euphoria（SLE-3③ 盲区治本）。"""
        panel = _panel(["2024-01-02"], ["r1"], [True], [False])
        rows = m.to_rows(panel)
        assert rows[0]["six_phase"] == "euphoria"
        assert rows[0]["leg_euphoria"] == 1

    def test_preempt_state_not_overridden_by_micro_leg(self) -> None:
        """地图 v1.2.2 裁定 B：r10 冰点就是冰点，微观退潮读数不得覆盖。"""
        panel = _panel(["2024-01-02"], ["r10"], [False], [True])
        rows = m.to_rows(panel)
        assert rows[0]["six_phase"] == "capitulation"
        assert rows[0]["preempt"] == 1

    def test_closed_book_flag_boundary(self) -> None:
        d = m.CLOSED_BOOK_CUTOFF
        panel = _panel([f"{d}", "2025-09-10"], ["r3", "r3"], [False, False], [False, False])
        rows = m.to_rows(panel)
        assert rows[0]["closed_book_ok"] == 1
        assert rows[1]["closed_book_ok"] == 0

    def test_dates_unique_in_output(self) -> None:
        panel = _panel(["2024-01-02", "2024-01-03"], ["r3", "r4"], [False, False], [False, False])
        rows = m.to_rows(panel)
        assert len({r["trade_date"] for r in rows}) == len(rows)


class TestBuildPanelGuards:
    def test_duplicate_trade_date_raises(self, monkeypatch) -> None:
        """快照表按日双写若不除，下游 30 日地板会在真实 15 日时假通过（实测红证）。"""
        dup = pd.DataFrame(
            {
                "dom": ["r3", "r3"],
                "euphoria": [False, False],
                "distribution": [False, False],
                "six": ["expansion", "expansion"],
            },
            index=pd.DatetimeIndex(["2024-01-02", "2024-01-02"]),
        )
        monkeypatch.setattr(m.am, "load_phase_panel", lambda **_k: dup)
        with pytest.raises(SystemExit):
            m.build_panel("2024-01-01")

    def test_empty_panel_raises_not_silent_empty_artifact(self, monkeypatch) -> None:
        monkeypatch.setattr(m.am, "load_phase_panel", lambda **_k: pd.DataFrame())
        with pytest.raises(SystemExit):
            m.build_panel("2024-01-01")


class TestAutoMountDedupeRegression:
    """本包对 auto_mount.load_phase_panel 的双写修复回归（不依赖 CH）。

    mock 的广度帧/overlay 必须带**唯一日索引**——生产路经 `_breadth_frame` 是
    `GROUP BY trade_date` 取数，天然唯一；若 mock 用重复索引去测，测的就不是产品路。
    """

    @staticmethod
    def _unique_index(dates):
        return pd.DatetimeIndex(pd.to_datetime(sorted(set(dates))))

    def _mocks(self, monkeypatch, raw):
        uniq = self._unique_index(raw.index)
        monkeypatch.setattr(am, "_snapshot_rows", lambda *_a, **_k: raw)
        monkeypatch.setattr(
            am,
            "_breadth_frame",
            lambda *_a, **_k: pd.DataFrame(
                {"close": [1.0] * len(uniq), "adv": [10.0] * len(uniq), "dec": [5.0] * len(uniq)}, index=uniq
            ),
        )
        monkeypatch.setattr(
            am,
            "phase_overlay",
            lambda _b: pd.DataFrame({"euphoria": [False] * len(uniq), "distribution": [False] * len(uniq)}, index=uniq),
        )

    def test_duplicate_rows_collapse_to_unique_days(self, monkeypatch) -> None:
        raw = pd.DataFrame(
            {"dom": ["r3", "r3", "r4", "r4", "r12", "r12"]},
            index=pd.DatetimeIndex(
                ["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03", "2024-01-04", "2024-01-04"]
            ),
        )
        self._mocks(monkeypatch, raw)
        panel = am.load_phase_panel(start="2024-01-01")
        assert not panel.index.has_duplicates
        # 3 唯一日 − PIT_TAIL_LAG(1) = 2；修复前这里是 5 行且含重复日
        assert len(panel) == 2
        assert [str(d.date()) for d in panel.index] == ["2024-01-02", "2024-01-03"]

    def test_pit_tail_drops_a_day_not_a_row(self, monkeypatch) -> None:
        """尾日为双写日时（实测 2026-09-18=2 行），修复前 PIT_TAIL_LAG 只切一行 ⇒ 尾日漏进样本。"""
        raw = pd.DataFrame(
            {"dom": ["r3", "r4", "r4"]}, index=pd.DatetimeIndex(["2024-01-02", "2024-01-03", "2024-01-03"])
        )
        self._mocks(monkeypatch, raw)
        panel = am.load_phase_panel(start="2024-01-01")
        assert max(str(d.date()) for d in panel.index) == "2024-01-02", (
            "尾日（双写日）未被剔除 ⇒ PIT 尾窗语义又退回'切行'口径"
        )

    def test_default_start_unchanged_for_existing_callers(self) -> None:
        import inspect

        assert inspect.signature(am.load_phase_panel).parameters["start"].default == am.IS_WIN_START
