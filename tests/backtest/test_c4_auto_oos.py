# [BLUEPRINT] MOD-BT-076 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_c4_auto_oos
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.c4_batch_screen
# [CONSUMERS] C4 自动 OOS 复测批守卫（MODIFY-GUARD: c4_batch_screen OOS pending/默认窗）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯函数+假 client（不连 CH）；测试不写生产路径；tmp_path/monkeypatch 隔离
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-076 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 自动 OOS 复测批守卫（S06-G1）——pending 名单四象限 + 默认 OOS 窗 + DB 查询侧映射。"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest  # noqa: F401 fixture 命名空间

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

import c4_batch_screen as runner  # noqa: E402

TF = "scripts/backtest/translated/"


class TestOosPendingNames:
    """四象限口径=「IS 批已落账(translated_c4) ∩ 尚无 oos_tested 行」。"""

    def test_quadrants(self):
        """IS有+OOS无=考；IS有+OOS有=跳；IS无(无论OOS)=不归 OOS 批（IS 批先考）。"""
        is_rows = [
            ("S-IS-ONLY", TF + "c4_isonly.py"),  # IS 有, OOS 无 -> 考
            ("S-BOTH", TF + "c4_both.py"),       # IS 有, OOS 有 -> 跳
        ]
        oos_done = {("S-BOTH", "c4_both.py")}
        discovered = ["c4_isonly.py", "c4_both.py", "c4_never.py", "c4_new.py"]
        # c4_never=IS无+OOS无；c4_new=IS无+OOS有（换名重入）——均不归 OOS 批
        got = runner._oos_pending_names(is_rows, oos_done, discovered)
        assert got == ["c4_isonly.py"]

    def test_is_absent_oos_present_excluded(self):
        """第四象限单测：OOS 有但 IS 无 -> 不考（防换名件绕过 IS 冻结窗直考 OOS）。"""
        got = runner._oos_pending_names([], {("S-X", "c4_x.py")}, ["c4_x.py"])
        assert got == []

    def test_same_sid_multiversion_file_keyed(self):
        """同 sid 多版本翻译件按文件名判重：v1 已 OOS、v2 新件 -> v2 需考
        （bothwin 及格集按 (sid, source_file) 对接，fetch_bothwin 同构）。"""
        is_rows = [("S-DUP", TF + "c4_dup_v1.py"), ("S-DUP", TF + "c4_dup_v2.py")]
        oos_done = {("S-DUP", "c4_dup_v1.py")}
        got = runner._oos_pending_names(is_rows, oos_done, ["c4_dup_v1.py", "c4_dup_v2.py"])
        assert got == ["c4_dup_v2.py"]

    def test_backslash_source_file_normalized(self):
        """Windows 反斜杠 source_file 归一为正斜杠再比文件名（CH 行与 discover() 可对接）。"""
        is_rows = [("S-B", "scripts\\backtest\\translated\\c4_b.py")]
        got = runner._oos_pending_names(is_rows, set(), ["c4_b.py"])
        assert got == ["c4_b.py"]

    def test_pilot_and_deleted_files_filtered(self):
        """pilot 特载行/已删翻译件不在 discover() 现存件中 -> 自然过滤（pilot OOS 另批补）。"""
        is_rows = [("P-1", TF + "pilot_002_ma_cross"), ("S-GONE", TF + "c4_gone.py")]
        got = runner._oos_pending_names(is_rows, set(), ["c4_alive.py"])
        assert got == []

    def test_discovered_defaults_to_discover(self, monkeypatch):
        """discovered 缺省取 discover() 现存件（真实发现器对接）。"""
        monkeypatch.setattr(runner, "discover", lambda: [Path("x/c4_z.py")])
        assert runner._oos_pending_names([("S-Z", TF + "c4_z.py")], set()) == ["c4_z.py"]


class TestDefaultOosWindow:
    def test_start_is_day_after_is_freeze(self):
        """OOS 起点恒=IS 冻结窗次日 2024-01-01（IS 2020-2023 冻结不触碰）。"""
        assert runner._default_oos_window(datetime(2026, 9, 15))[0] == "2024-01-01"

    def test_end_snaps_to_most_recent_saturday(self):
        """终点=最近一个周六：周六取当日（周考 14:00 发射，日线按交易日取数无害）。"""
        assert runner._default_oos_window(datetime(2026, 9, 15))[1] == "2026-09-12"  # 周二
        assert runner._default_oos_window(datetime(2026, 9, 13))[1] == "2026-09-12"  # 周日
        assert runner._default_oos_window(datetime(2026, 9, 19))[1] == "2026-09-19"  # 周六


class TestOosPendingFromDb:
    """DB 查询侧映射：假 client 按 SQL 文本分流（不连 CH），验证 verdict 过滤与归一。"""

    def test_query_side_mapping(self, monkeypatch):
        class FakeClient:
            def execute(self, sql):
                if "verdict = 'oos_tested'" in sql:
                    return [("S-1", TF + "c4_a.py"), ("S-2", TF + "c4_b.py")]
                return [("S-1", TF + "c4_a.py"), ("S-3", "scripts\\backtest\\translated\\c4_c.py")]

        import zephyr.data.ch_writer as cw

        monkeypatch.setattr(cw, "get_client_strict", lambda: FakeClient())
        monkeypatch.setattr(runner, "discover",
                            lambda: [Path("c4_a.py"), Path("c4_b.py"), Path("c4_c.py")])
        # S-1: IS有+OOS有=跳；S-3: IS有+OOS无=考（反斜杠归一后命中现存件）
        assert runner._oos_pending_names_from_db() == ["c4_c.py"]


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
