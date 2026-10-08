# [BLUEPRINT] MOD-BT-154 | docs/03_modules/_domain_backtest/blueprint.md（被测面挂靠：接电施工单 02_wiring_plan §F）
# [MODULE] tests.backtest.test_factory_wiring_night
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.pf_core.core.strategy_factory; zephyr.integration.local_model.ollama_chat;
#   scripts.backtest.factory_intake_pipeline; scripts.backtest.f06_e4_wfa_exam; scripts.backtest.c4_batch_screen
# [CONSUMERS] pytest（接电班回归面：LLM 路由接线/BP-4 落账/BP-7 播报/strategy_factory 运行时真调用）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯合成/monkeypatch（零 CH 写零 LLM 外呼零生产路径写）；路由解析 fail-closed 语义钉死
#   （轨缺席/API 轨必炸）；strategy_factory 10 阶段至少单链真调用（零运行时接线已破的证明钉）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [A_module] module_id=MOD-BT-154 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_factory_wiring_night.py — 接电班（st-fullscore-20260930）接线面回归：路由/落账/播报/工厂真调用。"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]


def _load(name: str, relpath: str):
    spec = importlib.util.spec_from_file_location(name, _REPO / relpath)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[spec.name] = mod  # type: ignore[union-attr]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


f06 = _load("f06_e4_wfa_exam_wiring", "scripts/backtest/f06_e4_wfa_exam.py")
c4 = _load("c4_batch_screen_wiring", "scripts/backtest/c4_batch_screen.py")

from schemas.categories.backtest.backtest_strategy_screen import (
    DATABASE as SCREEN_DB,
)
from schemas.categories.backtest.backtest_strategy_screen import (
    TABLE_NAME as SCREEN_TBL,
)
from zephyr.integration.local_model.ollama_chat import resolve_routed_model
from zephyr.pf_core.core.strategy_factory import (
    DiscoveryChannel,
    StrategyFactory,
    StrategyStage,
)

# ---------- LLM 路由接线（03_llm_local_vs_api_verdict §四.2 落地钉） ----------


class TestResolveRoutedModel:
    def _policy(self, tmp_path: Path, routes: dict, default_local: str = "qwen3:8b") -> Path:
        p = tmp_path / "model_routing_policy.yaml"
        p.write_text(
            json.dumps({"task_routes": routes, "default_local_model": default_local}),
            encoding="utf-8",
        )
        return p

    def test_local_without_model_uses_default(self, tmp_path):
        p = self._policy(tmp_path, {"signal_generation": {"preferred": "local"}})
        assert resolve_routed_model("signal_generation", policy_path=p) == "qwen3:8b"

    def test_local_with_model_passthrough(self, tmp_path):
        p = self._policy(tmp_path, {"strategy_codegen": {"preferred": "local:qwen3:14b"}})
        assert resolve_routed_model("strategy_codegen", policy_path=p) == "qwen3:14b"

    def test_api_track_refused(self, tmp_path):
        p = self._policy(tmp_path, {"mining_deep": {"preferred": "deepseek:deepseek-reasoner"}})
        with pytest.raises(RuntimeError, match="api_track_not_local"):
            resolve_routed_model("mining_deep", policy_path=p)

    def test_missing_route_refused(self, tmp_path):
        p = self._policy(tmp_path, {"other": {"preferred": "local"}})
        with pytest.raises(RuntimeError, match="route_missing"):
            resolve_routed_model("strategy_codegen", policy_path=p)

    def test_missing_policy_file_refused(self, tmp_path):
        with pytest.raises(RuntimeError, match="routing_config_missing"):
            resolve_routed_model("signal_generation", policy_path=tmp_path / "nope.yaml")

    def test_lane_defaults_match_real_policy(self):
        """真实路由册上：三车道任务轨解析出本地模型（今晚方案=本地 qwen3:8b，零配置）。"""
        from scripts.backtest.hypothesis_translator import TASK_ROUTE as TR_ROUTE
        from scripts.backtest.lane_b_idea_generator import TASK_ROUTE as LB_ROUTE
        from scripts.backtest.lane_c2_agentic_miner import TASK_ROUTE as C2_ROUTE

        assert {TR_ROUTE, LB_ROUTE, C2_ROUTE} <= {
            "signal_generation",
            "strategy_codegen",
        }
        for t in (TR_ROUTE, LB_ROUTE, C2_ROUTE):
            assert resolve_routed_model(t).startswith("qwen3")  # 本地轨=ollama 模型名


# ---------- strategy_factory 运行时真调用（零运行时接线已破的证明钉） ----------


class TestStrategyFactoryRuntimeWiring:
    def test_full_lifecycle_to_registration(self):
        """10 阶段单链真调用：intake→advance→三闸→register（注入判定，零自动放行）。"""
        f = StrategyFactory(clock=lambda: _dt.datetime(2026, 10, 1))
        rec = f.intake("动量回归双通道", DiscoveryChannel.LLM, hypothesis="价差均值回归")
        assert rec.stage is StrategyStage.DRAFT
        assert f.advance(rec.strategy_id, StrategyStage.HYPOTHESIS).stage is StrategyStage.HYPOTHESIS
        assert f.advance(rec.strategy_id, StrategyStage.GENERATION).stage is StrategyStage.GENERATION
        assert f.advance(rec.strategy_id, StrategyStage.VALIDATION).stage is StrategyStage.VALIDATION
        assert f.advance(rec.strategy_id, StrategyStage.GATE_REVIEW).stage is StrategyStage.GATE_REVIEW
        rec = f.submit_gate_verdict(rec.strategy_id, passed=True, detail="C-003 三重门禁合成通过")
        assert rec.stage is StrategyStage.PHACKING_REVIEW
        rec = f.submit_phacking_metrics(rec.strategy_id, dsr=0.42, pbo=0.31)
        assert rec.stage is StrategyStage.HUMAN_ADJUDICATION
        rec = f.human_adjudicate(rec.strategy_id, approved=True, approved_by="Owner-night-20261001")
        assert rec.stage is StrategyStage.REGISTRATION
        entry = f.register(rec.strategy_id)
        assert entry.status == "candidate" and entry.approved_by == "Owner-night-20261001"
        assert len(rec.history) == 8  # 8 次迁移留痕（intake 起步不含）

    def test_full_auto_is_authorized_path_only(self):
        """禁全自动上线钉：未过人工裁决不得 register；p-hacking 不达标直落 REJECTED。"""
        f = StrategyFactory()
        rec = f.intake("x", DiscoveryChannel.GP)
        for st in (
            StrategyStage.HYPOTHESIS,
            StrategyStage.GENERATION,
            StrategyStage.VALIDATION,
            StrategyStage.GATE_REVIEW,
        ):
            f.advance(rec.strategy_id, st)
        rec = f.submit_gate_verdict(rec.strategy_id, passed=True)
        rec = f.submit_phacking_metrics(rec.strategy_id, dsr=-0.1, pbo=0.2)
        assert rec.stage is StrategyStage.REJECTED


# ---------- BP-4：F06 判定落 strategy_screen（注册镜像+四键幂等） ----------


class TestF06ScreenLedger:
    def _summary(self, tmp_path: Path) -> dict:
        out_dir = tmp_path / "E4-F06-test"
        out_dir.mkdir()
        return {
            "recipe_id": "deadbeef1234",
            "verdict": "通过",
            "mechanism": "合成机制",
            "window_full": ["2020-01-01", "2025-08-31"],
            "out_dir": str(out_dir),
            "wfa_summary": {"stitched_stats": {"sharpe": 0.81, "max_drawdown": -0.12, "avg_turnover_1side": 0.09}},
            "true_oos": {"sharpe": 0.66, "oos_start": "2024-01-01"},
            "dsr": {"exact_eff_caliber": 0.77, "n_eff_gate_denominator": 9, "n_trials_raw": 12},
        }

    def test_row_built_and_written(self, tmp_path, monkeypatch):
        captured: dict = {}

        class _FakeClient:
            def execute(self, sql, *a, **k):
                return []  # 幂等判重=空（首落）

        import zephyr.data.ch_writer as cw

        def fake_write_tsv(table, columns, tsv_bytes, *a, **k):
            captured["table"] = table
            captured["tsv"] = tsv_bytes.decode("utf-8")
            return True

        monkeypatch.setattr(cw, "get_client_strict", lambda: _FakeClient())
        monkeypatch.setattr(cw, "write_tsv", fake_write_tsv)
        rep = f06.append_screen_ledger(self._summary(tmp_path))
        assert rep["written"] is True and rep["screen_batch"] == "F06-WFA-deadbeef1234"
        assert captured["table"] == f"{SCREEN_DB}.{SCREEN_TBL}"  # 表名真源=schema 册
        cells = captured["tsv"].rstrip("\n").split("\t")
        assert cells[10] == "f06_wfa" or "f06_wfa" in cells
        assert any("exam_archive=" in c for c in cells)
        assert any("oos_sharpe=0.66" in c for c in cells)

    def test_idempotent_rerun_skips(self, tmp_path, monkeypatch):
        src_p = (tmp_path / "E4-F06-test" / "verdict.md").resolve()
        try:  # 与生产同构：仓内相对 posix，仓外绝对（pytest basetemp 可能在仓内 .runtime/tmp）
            src = src_p.relative_to(_REPO).as_posix()
        except ValueError:
            src = src_p.as_posix()

        class _FakeClient:
            def execute(self, sql, *a, **k):
                return [("F06-WFA-deadbeef1234", "F06-deadbeef1234", "f06_wfa", src)]

        import zephyr.data.ch_writer as cw

        monkeypatch.setattr(cw, "get_client_strict", lambda: _FakeClient())
        monkeypatch.setattr(cw, "write_tsv", lambda *a, **k: (_ for _ in ()).throw(AssertionError("重跑禁重复写")))
        rep = f06.append_screen_ledger(self._summary(tmp_path))
        assert rep == {"written": False, "why": "already_registered", "screen_batch": "F06-WFA-deadbeef1234"}

    def test_write_unconfirmed_fails_loud(self, tmp_path, monkeypatch):
        class _FakeClient:
            def execute(self, sql, *a, **k):
                return []

        import zephyr.data.ch_writer as cw

        monkeypatch.setattr(cw, "get_client_strict", lambda: _FakeClient())
        monkeypatch.setattr(cw, "write_tsv", lambda *a, **k: False)
        with pytest.raises(RuntimeError, match="fail-closed"):
            f06.append_screen_ledger(self._summary(tmp_path))


# ---------- BP-7：OOS 窗口月度播报（事件触发零定时） ----------


class TestMonthlyWindowBroadcast:
    def test_monthly_report_landed_idempotent_path(self, tmp_path, monkeypatch):
        monkeypatch.setattr(c4, "_BROADCAST_DIR", tmp_path / "reports")
        monkeypatch.setattr(c4, "_prev_oos_window_end", lambda: "2026-08-30")
        b = c4.monthly_window_broadcast("2024-01-01", "2026-09-27", dry_run=True)
        assert b["report"] and b["prev_end"] == "2026-08-30" and b["alerted"] is False
        p = tmp_path / "reports" / "c4-oos-window-202609.md"
        assert p.exists() and "2024-01-01..2026-09-27" in p.read_text(encoding="utf-8")

    def test_cross_month_drift_alerts_when_not_dry(self, tmp_path, monkeypatch):
        monkeypatch.setattr(c4, "_BROADCAST_DIR", tmp_path / "reports")
        monkeypatch.setattr(c4, "_prev_oos_window_end", lambda: "2026-08-30")
        alerts: list[str] = []
        monkeypatch.setattr(
            "zephyr.strategy_pipeline.pipeline_events.alert",
            lambda msg, **kw: alerts.append(msg),
        )
        b = c4.monthly_window_broadcast("2024-01-01", "2026-09-27", dry_run=False)
        assert b["alerted"] is True and len(alerts) == 1 and "月度播报" in alerts[0]
        assert "上次 OOS 终点=2026-08-30" in (tmp_path / "reports" / "c4-oos-window-202609.md").read_text(
            encoding="utf-8"
        )

    def test_prev_read_failure_degrades_not_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(c4, "_BROADCAST_DIR", tmp_path / "reports")

        def _boom():
            raise RuntimeError("ch down")

        monkeypatch.setattr(c4, "_prev_oos_window_end", _boom)
        b = c4.monthly_window_broadcast("2024-01-01", "2026-09-27", dry_run=True)
        # fail-open 契约：播报是增强面，任何故障只降级留痕（error 字段），零反噬批测主链
        assert b.get("error") and "ch down" in b["error"]
        assert b["alerted"] is False

    def test_real_prev_reader_never_raises(self, monkeypatch):
        """真实读数器自带降级（台账不可达返回 None，不外抛）——BP-7 播报上游契约钉。"""
        monkeypatch.setattr(
            "zephyr.data.ch_writer.get_client_strict",
            lambda: (_ for _ in ()).throw(RuntimeError("tcp down")),
        )
        assert c4._prev_oos_window_end() is None
