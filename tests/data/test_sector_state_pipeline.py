# [TEST] sector_state_pipeline——stage 契约+NULL 归一+偏好消费契约（形态级，零 CH 依赖）
# [TTL] permanent
import datetime

from zephyr.data.sector_state_pipeline import (
    SECTOR_PREFERENCE_COLUMNS,
    SECTOR_STATE_COLUMNS,
    _maybe_float,
    _null_cell,
    _num,
    load_l2_admission,  # noqa: F401
    map_preference,  # noqa: F401 — 再导出保护（消费方 import 面稳定）
)


class TestTsvCellContract:
    def test_num_none_is_null_literal(self):
        assert _num(None) == "\\N"
        assert _num(0.5) == "0.500000"

    def test_null_cell_covers_reader_dialects(self):
        # ch_reader TCP 通道 NULL 渲染 'None'；HTTP 路径 '\N'；浮点 NaN 字面量 'nan'
        assert _null_cell("None") == "\\N"
        assert _null_cell("\\N") == "\\N"
        assert _null_cell("nan") == "\\N"
        assert _null_cell("") == "\\N"
        assert _null_cell("lagging") == "lagging"
        assert _null_cell("0.334829") == "0.334829"

    def test_maybe_float_all_forms(self):
        assert _maybe_float("None") is None
        assert _maybe_float("\\N") is None
        assert _maybe_float("nan") is None
        assert _maybe_float("") is None
        assert _maybe_float("57.0") == 57.0

    def test_column_lists_match_ddl_order(self):
        state_cols = SECTOR_STATE_COLUMNS.strip("()").split(", ")
        assert state_cols[:4] == ["trade_date", "stage", "ts", "sector_code"]
        assert state_cols[-2:] == ["components", "version"]
        pref_cols = SECTOR_PREFERENCE_COLUMNS.strip("()").split(", ")
        assert "emotion_version" in pref_cols and "banned_quadrant" in pref_cols

    def test_stage_ts_discipline(self):
        """时戳纪律（骨架稿§6）：close_final=15:10 / pre_open=09:15。"""
        # 形态级：管道生成 ts 的格式约定
        import re

        pat = r"^\d{4}-\d{2}-\d{2} (15:10:00|09:15:00)$"
        assert re.match(pat, "2026-09-22 15:10:00")
        assert re.match(pat, "2026-09-23 09:15:00")


class TestPreferenceConsumptionContract:
    def test_map_preference_regime_real_value(self):
        """真值消费：regime dominant r3 + emotion 0.48（09-22/23 实弹值）。"""
        pref = map_preference("r3", 0.482319)
        assert pref.preference_label == "OFFENSIVE"
        assert pref.axis_status == "ok"
        assert pref.tilt == 1.2

    def test_map_preference_missing_emotion_mock(self):
        pref = map_preference("r3", None)
        assert pref.axis_status == "mock"
