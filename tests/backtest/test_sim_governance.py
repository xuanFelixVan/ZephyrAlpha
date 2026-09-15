# [BLUEPRINT] MOD-BT-095 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_governance
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_governance
# [CONSUMERS] 治理建议生成器质量守卫（MODIFY-GUARD）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] recommend() 纯函数合成史测试（不依赖 CH）；流转建议只产不改册
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-141 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_governance 质量守卫——流转建议规则的纯函数断言。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_governance", _REPO / "scripts" / "backtest" / "sim_governance.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_governance"] = mod
spec.loader.exec_module(mod)


def _hist(*reasons: str) -> list[dict]:
    return [{"batch": f"SIM-DEV-2026-{i:02d}", "reason": r, "notes": ""}
            for i, r in enumerate(reasons, 1)]


def test_two_pass_promotes():
    rec, why = mod.recommend(_hist("monthly_pass", "monthly_pass"))
    assert rec == "promote_paper" and "连续 2 月" in why


def test_two_breach_demotes():
    rec, _ = mod.recommend(_hist("monthly_pass", "monthly_breach", "monthly_breach"))
    assert rec == "demote_decayed"


def test_single_month_no_action():
    rec, _ = mod.recommend(_hist("monthly_pass"))
    assert rec is None


def test_consecutive_flag_demotes():
    rec, _ = mod.recommend(_hist("monthly_breach_consecutive"))
    assert rec == "demote_decayed"


# ---------- S10 C2 治理收尾：alerter 推送（降级不抛）+ run 档案 + dry-run（全 mock 零生产 IO） ----------
class TestC2GovernanceWiring:
    @staticmethod
    def _rec(sid: str, rec: str | None) -> dict:
        return {"strategy_id": sid, "lifecycle_status": "sim", "code_path": "", "name_zh": "",
                "months_evaluated": 2, "recommendation": rec,
                "why": "连续 2 月月度通过（SOP-C §8 偏离门槛）" if rec else "观察期"}

    def test_alert_recommendations_no_actionable_is_silent(self, monkeypatch):
        pushed = []
        import zephyr.data.alerter as al

        class FakeAlerter:
            def notify(self, *a, **k):
                pushed.append(a)

        monkeypatch.setattr(al, "Alerter", FakeAlerter)
        assert mod.alert_recommendations([self._rec("S1", None)]) is False
        assert pushed == []  # 无建议不推送

    def test_alert_recommendations_pushes_error_level(self, monkeypatch):
        pushed = []
        import zephyr.data.alerter as al

        class FakeAlerter:
            def notify(self, task_id, error, level="ERROR", source=None, extra=None):
                pushed.append((task_id, error, level, source))

        monkeypatch.setattr(al, "Alerter", FakeAlerter)
        assert mod.alert_recommendations([self._rec("S1", "promote_paper")]) is True
        assert pushed and pushed[0][0] == "sim_governance"
        assert "promote_paper" in pushed[0][1] and pushed[0][2] == "ERROR"

    def test_alert_recommendations_degrades_without_raise(self, monkeypatch):
        """告警通道任何故障=降级（本地告警文件由 Alerter 内部落；Alerter 不可达也不抛）。"""
        import zephyr.data.alerter as al

        class BoomAlerter:
            def __init__(self):
                raise RuntimeError("no webhook, no dir")

        monkeypatch.setattr(al, "Alerter", BoomAlerter)
        assert mod.alert_recommendations([self._rec("S1", "demote_decayed")]) is False

    def test_write_run_archive_screen_kind(self, tmp_path, monkeypatch):
        """run 档案（照 lifecycle_advisor 先例）：SCREEN kind+advice JSON+verdict 归档。"""
        import zephyr.backtest.run_archive as ra

        calls = []
        monkeypatch.setattr(ra, "create_run",
                            lambda run_id, object_id, kind, **k:
                            calls.append(("create", run_id, object_id, kind, k)) or tmp_path / run_id)
        monkeypatch.setattr(ra, "write_step",
                            lambda run_id, step, content, **k:
                            calls.append(("step", run_id, step, k.get("filename"))))
        monkeypatch.setattr(ra, "finalize_run",
                            lambda run_id, **k: calls.append(("finalize", run_id)))
        run_id = mod.write_run_archive([self._rec("S1", None)], [self._rec("S1", "promote_paper")])
        assert run_id.startswith("SCR-SIMGOV-")
        assert calls[0][:4] == ("create", run_id, "", "SCREEN")
        assert any(c[0] == "step" and c[2] == "04" and c[3] == "sim_governance_advice.json"
                   for c in calls)
        assert calls[-1] == ("finalize", run_id)

    @staticmethod
    def _run_main(monkeypatch, entries, hist, extra_args):
        monkeypatch.setattr(mod, "sim_lifecycle_entries", lambda: entries)
        monkeypatch.setattr(mod, "month_history", lambda sid: hist)
        monkeypatch.setattr(sys, "argv", ["sim_governance.py", *extra_args])

    def test_main_dry_run_writes_nothing_and_pushes_nothing(self, monkeypatch, capsys):
        import zephyr.backtest.run_archive as ra
        import zephyr.data.alerter as al

        def forbidden(*_a, **_k):
            raise AssertionError("dry-run 禁写/禁推")

        for name in ("create_run", "write_step", "finalize_run"):
            monkeypatch.setattr(ra, name, forbidden)

        class FakeAlerter:
            def notify(self, *a, **k):
                raise AssertionError("dry-run 禁推送")

        monkeypatch.setattr(al, "Alerter", FakeAlerter)
        self._run_main(monkeypatch, [self._rec("S1", None)], _hist("monthly_pass"), ["--dry-run"])
        mod.main()
        out = capsys.readouterr().out
        assert "S1" in out

    def test_main_full_writes_archive_and_pushes(self, monkeypatch, capsys):
        import zephyr.backtest.run_archive as ra
        import zephyr.data.alerter as al

        calls = []
        monkeypatch.setattr(ra, "create_run",
                            lambda run_id, object_id, kind, **k:
                            calls.append(("create", kind)) or f"{run_id}-dir")
        monkeypatch.setattr(ra, "write_step", lambda run_id, step, content, **k: None)
        monkeypatch.setattr(ra, "finalize_run", lambda run_id, **k: calls.append(("finalize",)))
        pushed = []

        class FakeAlerter:
            def notify(self, task_id, error, level="ERROR", source=None, extra=None):
                pushed.append((task_id, level))

        monkeypatch.setattr(al, "Alerter", FakeAlerter)
        # 连续 2 月 pass → promote_paper（有建议→推送+档案）
        self._run_main(monkeypatch, [self._rec("S1", None)],
                       _hist("monthly_pass", "monthly_pass"), ["--json"])
        mod.main()
        assert ("create", "SCREEN") in calls and ("finalize",) in calls
        assert pushed and pushed[0] == ("sim_governance", "ERROR")
        out = capsys.readouterr().out
        assert "promote_paper" in out
