# [BLUEPRINT] MOD-SIG-157 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-SIG-157 sector_rotation_criterion 单元测试（st-fg-srcline1-20261005）。

红蓝对抗手法覆盖：
- 红-边界：基准非法/板块族空/全板块过短 fail-closed；单板块过短跳过记 notes
- 红-前视：纯函数确定性（同输入必同输出）
- 红-契约：RS 分位有序性、streak 手算对拍、LEAD/WATCH/NONE 三档边界
- 红-故障：build_from_index_rows 缺陷行跳过、乱序重排
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.source_line.sector_rotation_criterion import (
    DEFAULT_WINDOW,
    RS_LEAD_MIN,
    RS_WATCH_MIN,
    STREAK_LEAD_MIN,
    BoardRotationCriterion,
    LeadTier,
    SectorRotationInputError,
    SectorRotationSnapshot,
    build_from_index_rows,
    build_sector_rotation_snapshot,
    classify_lead_tier,
    streak_vs_benchmark,
)

# ── 构造辅助 ────────────────────────────────────────────────────────────────

N = DEFAULT_WINDOW + 1


def _series(base: float, daily_ret: float, n: int = N):
    """等比收益合成序列。"""
    return [base * (1.0 + daily_ret) ** i for i in range(n)]


def _bench(n: int = N, daily_ret: float = 0.002):
    """市场基准序列。"""
    return _series(3000.0, daily_ret, n)


@pytest.fixture()
def three_boards():
    """强/中/弱三板块合成（强板块日日跑赢基准）。"""
    return {
        "STRONG": _series(1000.0, 0.02),
        "MID": _series(1000.0, 0.003),
        "WEAK": _series(1000.0, -0.01),
    }


# ── 档位分类 ────────────────────────────────────────────────────────────────


class TestLeadTier:
    def test_three_tiers(self):
        assert classify_lead_tier(RS_LEAD_MIN, STREAK_LEAD_MIN) == LeadTier.LEAD
        assert classify_lead_tier(RS_LEAD_MIN, 1) == LeadTier.WATCH  # streak 不足
        assert classify_lead_tier(RS_WATCH_MIN, 10) == LeadTier.WATCH
        assert classify_lead_tier(0.3, 10) == LeadTier.NONE


class TestStreak:
    def test_perfect_streak(self):
        s = _series(100.0, 0.02)
        b = _bench()
        assert streak_vs_benchmark(s, b) == N - 1

    def test_never_outperform(self):
        s = _series(100.0, -0.01)
        b = _bench()
        assert streak_vs_benchmark(s, b) == 0

    def test_break_then_resume_counts_only_tail(self):
        # 末日恢复跑赢只计 1 天：倒数第二天大跌跑输（断），末日大涨跑赢 → streak=1
        s = [100.0 * (1.02**i) for i in range(N)]
        s[-2] = s[-3] * 0.9  # 倒数第二天大跌（跑输基准）
        b = _bench()
        assert streak_vs_benchmark(s, b) == 1


# ── 主入口契约 ──────────────────────────────────────────────────────────────


class TestBuildSnapshot:
    def test_ranking_and_lead(self, three_boards):
        snap = build_sector_rotation_snapshot(three_boards, _bench())
        assert snap.boards[0].board == "STRONG"
        assert snap.boards[-1].board == "WEAK"
        assert snap.boards[0].rs_rank_pct == pytest.approx(1.0)
        assert snap.boards[0].streak == N - 1
        assert snap.boards[0].lead_tier == LeadTier.LEAD
        assert snap.lead_boards == ("STRONG",)

    def test_rs_rank_range(self, three_boards):
        snap = build_sector_rotation_snapshot(three_boards, _bench())
        for b in snap.boards:
            assert 0.0 <= b.rs_rank_pct <= 1.0

    def test_single_board_rank_neutral(self):
        # 单板块：分位取 0.0（无可比横截面），streak 正常
        snap = build_sector_rotation_snapshot({"ONLY": _series(100.0, 0.02)}, _bench())
        assert snap.boards[0].rs_rank_pct == 0.0

    def test_to_dict_json_serializable(self, three_boards):
        snap = build_sector_rotation_snapshot(three_boards, _bench())
        d = snap.to_dict()
        assert json.dumps(d, ensure_ascii=False)
        assert set(d) == {"window", "boards", "lead_boards", "notes"}

    def test_deterministic(self, three_boards):
        a = build_sector_rotation_snapshot(three_boards, _bench())
        b = build_sector_rotation_snapshot(three_boards, _bench())
        assert a == b


# ── fail-closed 与跳过契约 ──────────────────────────────────────────────────


class TestFailClosed:
    def test_benchmark_too_short(self, three_boards):
        with pytest.raises(SectorRotationInputError, match="基准"):
            build_sector_rotation_snapshot(three_boards, [3000.0] * 5)

    def test_empty_boards(self):
        with pytest.raises(SectorRotationInputError, match="板块族为空"):
            build_sector_rotation_snapshot({}, _bench())

    def test_short_board_skipped_with_notes(self, three_boards):
        boards = dict(three_boards)
        boards["SHORT"] = [100.0] * 5  # 过短板块
        snap = build_sector_rotation_snapshot(boards, _bench())
        assert all(b.board != "SHORT" for b in snap.boards)
        assert any("SHORT" in n for n in snap.notes)

    def test_all_short_fails_closed(self):
        with pytest.raises(SectorRotationInputError, match="过短"):
            build_sector_rotation_snapshot({"A": [1.0] * 3, "B": [1.0] * 3}, _bench())

    def test_nonpositive_close_skipped_with_notes(self):
        # 非法值板块被跳过记 notes，正常板块照常输出（记录级缺陷不整体 fail）
        boards = {
            "GOOD": _series(100.0, 0.02),
            "BAD": [100.0] * (N - 1) + [0.0],  # 末日 0.0 非法
        }
        snap = build_sector_rotation_snapshot(boards, _bench())
        assert [b.board for b in snap.boards] == ["GOOD"]
        assert any("非法" in n for n in snap.notes)


# ── DS 读入形态（build_from_index_rows） ────────────────────────────────────


class TestBuildFromIndexRows:
    def test_unsorted_rows_resorted(self, three_boards):
        rows = []
        for board, closes in three_boards.items():
            for i, c in enumerate(closes):
                rows.append({"board": board, "date": f"2026-09-{i + 1:02d}", "close": c})
        rows.reverse()
        snap = build_from_index_rows(rows, _bench())
        assert snap.boards[0].board == "STRONG"
        assert not any("跳过" in n for n in snap.notes)

    def test_defective_rows_skipped_with_notes(self, three_boards):
        rows = []
        for board, closes in three_boards.items():
            for i, c in enumerate(closes):
                rows.append({"board": board, "date": f"2026-09-{i + 1:02d}", "close": c})
        rows.append({"board": "STRONG", "date": "2026-09-99"})  # 缺 close
        rows.append({"board": "X", "date": "2026-09-98", "close": "abc"})  # 非法值
        snap = build_from_index_rows(rows, _bench())
        assert any("跳过缺陷指数行 2" in n for n in snap.notes)
