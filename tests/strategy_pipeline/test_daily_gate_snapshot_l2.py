# [BLUEPRINT] MOD-BT-213 | docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md
# [MODULE] tests.strategy_pipeline.test_daily_gate_snapshot_l2
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.daily_gate_snapshot; zephyr.signal_ashare.sector.sector_gate
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试隔离：零生产路径写入（CH 读走注入式路由 reader，供料走 admission 注入/
#   _load_l2_admission monkeypatch，异常走 monkeypatch）——宪法 §9.6；
#   覆盖=L2 甲档桥接三分支（映射正确/缺数据 absent/异常 absent）+六段映射表全格+未映射 dominant
#   +gate_level 三态（三原料齐=evaluated/缺一=insufficient/无供料=not_evaluated，L03-C02 batch2）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-213 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] test-daily-gate-snapshot-l2-mod-bt-213-20260922
"""daily_gate_snapshot L2 甲档桥接+三原料三态单测（方案甲验收+L03-C02 batch2 接线验收）。

三分支（施工验收口径）：
    ①映射正确：regime dominant → WaterTemp → water_temp_response 响应面载荷逐字段核对
    ②缺数据 absent：regime 无行（L1 absent）/ dominant 未映射 → L2 absent 如实留痕
    ③异常 absent：water_temp_response 抛错 → L2 absent（fail-open 不炸拍板）
三态（L03-C02 batch2 接线验收口径）：
    三原料齐（top/retained_sectors/score）→ evaluated；
    缺一（score=None/空集）→ insufficient（score=0.0 合法值非缺）；
    无供料（absent/供料异常）→ not_evaluated。
"""

from __future__ import annotations

import pytest

from zephyr.strategy_pipeline import daily_gate_snapshot as snap
from zephyr.strategy_pipeline.daily_gate_snapshot import collect_gate_snapshot

D = "2026-09-15"  # 数据日（格式合法即可，全部走注入 reader，零生产读取）
_REGIME_COLS = 15  # SQL_LATEST_REGIME_SNAPSHOT 列数（对齐 test_decision_orchestrator 口径）

# HMM 七态 dominant（regime_snapshot_history 真实值域 r1~r12）→ water_temp_response 响应面
# 实值（_WATER_TEMP_TABLE v2.1 基表）。红队修正：dominant 是 HMM 七态不是情绪六段（C1 撞轴教训）。
_EXPECTED_RESPONSE: dict[str, tuple[str, float, list[float], str]] = {
    "r1": ("NEUTRAL", 1.0, [0.60, 0.80], "ALL"),
    "r2": ("NEUTRAL", 1.0, [0.60, 0.80], "ALL"),
    "r3": ("RISK_ON", 0.5, [0.60, 0.80], "ALL"),
    "r4": ("RISK_OFF", 0.3, [0.80, 0.90], "LEADING_ONLY"),
    "r10": ("CRASH", 0.0, [1.01, 1.01], "NONE"),
    "r11": ("PANIC_REPAIR", 0.5, [0.50, 0.70], "IMPROVING_ONLY"),
    "r12": ("RISK_ON", 0.5, [0.60, 0.80], "ALL"),
}


def _regime_row(dominant: str) -> tuple:
    row = ("VAL-P0-TEST", D, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, dominant, 0.9, 0.75, 0.8, 0.9, "{}")
    assert len(row) == _REGIME_COLS
    return row


class _RouteReader:
    """注入式只读通道：regime SQL 返回可编排行，其余表返回空（零生产路径）。"""

    def __init__(self, regime_rows: list[tuple]) -> None:
        self.regime_rows = regime_rows

    def __call__(self, sql: str) -> list[tuple]:
        if "regime_snapshot_history" in sql:
            return list(self.regime_rows)
        return []


# 三原料齐的供料面（batch2 契约形态：load_l2_admission 返回值采样——top5/retained/score+偏好随附）
_FULL_ADMISSION: dict = {
    "status": "ok",
    "top": ["881319", "880301", "880326", "880352", "880464"],
    "retained_sectors": ["881386", "880310"],
    "score": 57.0,
    "preference_label": "OFFENSIVE",
    "banned_quadrant": "lagging",
    "tilt": 1.2,
    "asof": "2026-09-23",
}


class TestL2WaterTempBridge:
    """L2 甲档桥接（_collect_l2 + collect_gate_snapshot 接线）三分支验收。"""

    # 无供料缺席面（直接调用 _collect_l2 时显式注入，禁触生产 CH——宪法 §9.6）
    _ABSENT: dict = {"status": "absent", "error": "no_sector_state_rows"}

    def test_mapping_all_seven_dominants(self) -> None:
        """①映射正确：HMM 七态全格逐字段核对（水温档/权重/阈值/RRG 过滤+proposed 注记）。"""
        for dominant, (temp, weight, thresholds, rrg) in _EXPECTED_RESPONSE.items():
            out = snap._collect_l2(dominant, admission=self._ABSENT)
            assert out["status"] == "ok", dominant
            assert out["water_temp"] == temp
            assert out["signal_weight"] == weight
            assert out["gate_thresholds"] == thresholds
            assert out["rrg_filter"] == rrg
            assert out["gate_level"] == "not_evaluated"  # 无供料，不伪造放行门态
            assert out["threshold_provenance"] == "v2.1_proposed_pending_G05"

    def test_risk_on_consensus_climax_double_suppression(self) -> None:
        """RISK_ON 叠加 CONSENSUS_CLIMAX：signal_weight 0.5×0.5=0.25（双重抑制过热追高）。"""
        out = snap._collect_l2("r12", consensus_climax=True, admission=self._ABSENT)
        assert out["status"] == "ok"
        assert out["signal_weight"] == 0.25

    def test_bridge_wired_via_collect_gate_snapshot(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """接线：collect_gate_snapshot 复用 L1 dominant（桥接零新读）→ L2 ok 出 absent_layers。"""
        monkeypatch.setattr(snap, "_load_l2_admission", lambda: dict(_FULL_ADMISSION))
        out = collect_gate_snapshot(D, reader=_RouteReader([_regime_row("r11")]))
        l2 = out["l2"]
        assert l2["status"] == "ok"
        assert l2["water_temp"] == "PANIC_REPAIR"  # r11 修复段
        assert "L2" not in out["absent_layers"]

    def test_missing_regime_row_absent(self) -> None:
        """②缺数据 absent：regime 无行 → L1 absent → 桥接无入参 → L2 absent 如实（D2 接管）。"""
        out = collect_gate_snapshot(D, reader=_RouteReader([]))
        l2 = out["l2"]
        assert l2["status"] == "absent"
        assert l2["error"] == "no_persisted_gate_state_v1"
        assert "L2" in out["absent_layers"]

    def test_unmapped_dominant_absent(self) -> None:
        """②映射缺 absent：dominant 不在六段映射表 → absent（保守侧按门关）。"""
        out = snap._collect_l2("r99_unmapped_state")
        assert out["status"] == "absent"
        assert out["error"] == "dominant_unmapped"
        assert snap._collect_l2(None)["status"] == "absent"

    def test_response_raise_absent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """③异常 absent：water_temp_response 抛错 → L2 absent+异常类型留痕（fail-open）。"""

        def _boom(*_args: object, **_kw: object) -> None:
            raise ValueError("水温通道故障")

        monkeypatch.setattr("zephyr.signal_ashare.sector.sector_gate.water_temp_response", _boom)
        out = collect_gate_snapshot(D, reader=_RouteReader([_regime_row("r3")]))
        l2 = out["l2"]
        assert l2["status"] == "absent"
        assert l2["error"] == "ValueError"
        assert "L2" in out["absent_layers"]


class TestL2GateLevelThreeStates:
    """gate_level 三态求值（L03-C02 batch2 接线验收：齐=evaluated/缺一=insufficient/无=not_evaluated）。"""

    def test_evaluated_all_three_materials(self) -> None:
        """三原料齐 → evaluated；偏好标签/tilt/banned 随 admission 原样透传。"""
        out = snap._collect_l2("r1", admission=dict(_FULL_ADMISSION))
        assert out["status"] == "ok"
        assert out["gate_level"] == "evaluated"
        adm = out["admission"]
        assert adm["top"] == _FULL_ADMISSION["top"]
        assert adm["retained_sectors"] == _FULL_ADMISSION["retained_sectors"]
        assert adm["score"] == 57.0
        assert adm["preference_label"] == "OFFENSIVE"
        assert adm["tilt"] == 1.2
        assert adm["banned_quadrant"] == "lagging"

    def test_evaluated_zero_score_is_a_value_not_a_gap(self) -> None:
        """score=0.0 合法值（falsy 但非缺）→ evaluated（禁真值判断误判缺）。"""
        admission = dict(_FULL_ADMISSION, score=0.0)
        assert snap._collect_l2("r1", admission=admission)["gate_level"] == "evaluated"

    def test_insufficient_missing_score(self) -> None:
        """缺一（score=None）→ insufficient（strength 早期原料缺实录形态）。"""
        admission = dict(_FULL_ADMISSION, score=None)
        out = snap._collect_l2("r1", admission=admission)
        assert out["gate_level"] == "insufficient"
        assert out["status"] == "ok"

    def test_insufficient_missing_top_or_retained(self) -> None:
        """缺一（top/retained 空集）→ insufficient（status 仍 ok=供料通道在原料缺）。"""
        assert snap._collect_l2("r1", admission=dict(_FULL_ADMISSION, top=[]))["gate_level"] == "insufficient"
        assert (
            snap._collect_l2("r1", admission=dict(_FULL_ADMISSION, retained_sectors=[]))["gate_level"]
            == "insufficient"
        )

    def test_not_evaluated_no_supply(self) -> None:
        """无供料（absent）→ not_evaluated，响应面照常出（水温桥不因断供缺席）。"""
        out = snap._collect_l2("r1", admission={"status": "absent", "error": "no_sector_state_rows"})
        assert out["status"] == "ok"
        assert out["gate_level"] == "not_evaluated"
        assert out["signal_weight"] == 1.0  # r1→NEUTRAL 响应面在

    def test_not_evaluated_default_loader_fail_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """无注入时走 _load_l2_admission（默认供料通道）：供料异常→absent→not_evaluated（fail-open）。"""

        def _boom() -> dict:
            raise RuntimeError("供料通道故障")

        monkeypatch.setattr(snap, "_load_l2_admission", _boom)
        out = snap._collect_l2("r1")
        assert out["gate_level"] == "not_evaluated"
        assert out["admission"] == {"status": "absent"}

    def test_evaluated_wired_via_collect_gate_snapshot(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """端到端：L1 dominant + 供料齐 → collect_gate_snapshot 产出 evaluated 门态（接线验收）。"""
        monkeypatch.setattr(snap, "_load_l2_admission", lambda: dict(_FULL_ADMISSION))
        out = collect_gate_snapshot(D, reader=_RouteReader([_regime_row("r3")]))
        l2 = out["l2"]
        assert l2["gate_level"] == "evaluated"
        assert l2["water_temp"] == "RISK_ON"
        assert l2["admission"]["asof"] == _FULL_ADMISSION["asof"]
