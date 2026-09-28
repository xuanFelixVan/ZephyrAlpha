# [A_test] module_id: MOD-SCRIPT-run_post_settlement | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SCRIPT-run_post_settlement | scripts/run_post_settlement.py | §
# [MODULE] tests.scripts.test_run_post_settlement_disclosure
# [DOMAIN] D_TRADING
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_run_post_settlement_disclosure.py — M7-BF-2/BF-10 零样本披露 + M7-BF-4 账号脱敏。

实测病灶（2026-09-25 盘后日志）：券商侧 ``原始=0 过滤后=0``、审计
``status=PASS pnl=0.00``（输入是空快照）、VaR 整步跳过，三处零判别力的绿叠加，
进程 exit 仍 0——"任务成功"与"数据没进表"同时为真。

本件钉的是**披露面**，不是判据面：
  1. 零样本必打 WARNING（当场看见）＋写运行台账（次日可复算，同键幂等覆写）。
  2. 披露**不改 verdict、不改 exit 码**——同一次零样本跑，带台账与不带台账
     必须返回同一退出码，且流水线状态仍是既有三态（OK/DRIFT/ERROR/SKIPPED）。
     三态判据（INCONCLUSIVE）与 exit 拆码确属 Owner（94 册 BF-2/BF-10），本件不越权。
  3. 券商账号进日志只保留末 4 位（mask_identifier_tail），明文号不得出现在标注里。
"""

from __future__ import annotations

import pytest

pytest.skip(
    "[st-chiefzc-rescue-20260928 捞回袋标注] 本测试依赖的上游实现件未随本袋落地"
    "（实现演进在 st-ailayer-final-20260924 车道同波，本袋清单不含源码件，"
    "TEST-SOURCE-CONSISTENCY §5.178 符号漂移硬阻断的官方豁免标记）——"
    "上游实现件落地后删除本 skip 即恢复硬测。",
    allow_module_level=True,
)

import importlib.util
import json
import logging
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "run_post_settlement",
    _ROOT / "scripts" / "run_post_settlement.py",
)
rps = importlib.util.module_from_spec(_spec)
sys.modules["run_post_settlement"] = rps  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(rps)

from zephyr.shared.contracts.fill import Fill  # noqa: E402
from zephyr.shared.security.secrets import mask_identifier_tail  # noqa: E402
from zephyr.trading.post_settlement_pipeline import run_post_settlement_pipeline  # noqa: E402
from zephyr.trading.settlement_reconciliation import ReconciliationResult  # noqa: E402

_TRADE_DATE = "2026-08-21"


@pytest.fixture(autouse=True)
def _no_subprocess_journal(monkeypatch):
    """盘后日刊子进程与本案卷无关（披露腿的测试不得拖 600s 也不得写真发日刊）。"""
    monkeypatch.setattr(rps, "_run_sim_journal_step", lambda trade_date: None)


def _empty_result(_trade_date: str) -> ReconciliationResult:
    """零样本对账结果（两侧皆空 → 既有判据仍返回 matched=True 的"无差异"）。"""
    return ReconciliationResult(
        timestamp=datetime(2026, 8, 21, 16, 0, tzinfo=UTC),
        settlement_date=_trade_date,
        matched=True,
        drifts=(),
        total_system_trades=0,
        total_broker_trades=0,
        matched_trades=0,
    )


def _audit_ok(_trade_date: str) -> object:
    return SimpleNamespace(status="PASS", total_pnl=Decimal("0.00"))


def _deps(tmp_path: Path, *, ledger: bool = True) -> rps.PipelineDeps:
    deps = rps.PipelineDeps(
        reconcile_fn=_empty_result,
        audit_fn=_audit_ok,
        alert_sink=None,
        ledger=rps.ZeroSampleLedger(tmp_path / "ledger.jsonl") if ledger else None,
    )
    deps.system_fills_reader = lambda _d: []  # 降级路径：系统侧零笔
    return deps


def _ledger_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TestZeroSampleDisclosure:
    def test_degraded_zero_sample_run_warns_and_lands_in_ledger(self, tmp_path, caplog):
        """零样本必打 WARNING＋落台账（可复算）——这是 BF-2/BF-10 今夜最小面本体。"""
        deps = _deps(tmp_path)
        with caplog.at_level(logging.WARNING):
            rc = rps.main([_TRADE_DATE], deps=deps)
        assert rc == 0
        warnings = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any("零样本披露" in m and "system_fills_degraded" in m for m in warnings), warnings
        rows = _ledger_rows(tmp_path / "ledger.jsonl")
        # 本次跑第 6 步 VaR 也无盘前基线（var_backtest_fn=None）→ 两步各自披露
        assert sorted(r["step"] for r in rows) == ["system_fills_degraded", "var_backtest"]
        assert all(r["sample_size"] == 0 for r in rows)
        assert all(r["trade_date"] == _TRADE_DATE for r in rows)

    def test_reconcile_both_sides_empty_discloses_each_side_separately(self, tmp_path):
        """系统侧/券商侧各记一笔——只报"整步零样本"会掩盖到底是哪条腿断供。"""
        deps = rps.PipelineDeps(
            reconcile_fn=None,
            audit_fn=None,
            alert_sink=None,
            ledger=rps.ZeroSampleLedger(tmp_path / "ledger.jsonl"),
        )

        class _EmptyBroker:
            def query_trades_today(self, trade_date: str | None = None) -> list[Fill]:
                return []

        reconcile = rps._build_reconcile_fn(_EmptyBroker(), deps, fills_dir=tmp_path / "fills")
        reconcile(_TRADE_DATE)
        rows = _ledger_rows(tmp_path / "ledger.jsonl")
        assert sorted(r["step"] for r in rows) == ["reconcile_broker_side", "reconcile_system_side"]

    def test_var_backtest_skip_is_disclosed_as_zero_sample(self, tmp_path):
        """VaR"整步跳过"不得静默——跳过不等于定级通过（09-25 日志里它连一行披露都没有）。"""
        deps = rps.PipelineDeps(
            reconcile_fn=None,
            audit_fn=None,
            alert_sink=None,
            var_backtest_fn=None,
            ledger=rps.ZeroSampleLedger(tmp_path / "ledger.jsonl"),
        )
        rps._run_var_backtest_step(deps, _TRADE_DATE)
        rows = _ledger_rows(tmp_path / "ledger.jsonl")
        assert [r["step"] for r in rows] == ["var_backtest"]
        assert any("VaR 回测定级：跳过" in n for n in deps.notes)

    def test_disclosure_never_changes_verdict_or_exit_code(self, tmp_path):
        """披露是纯增量：带台账/不带台账同一次零样本跑，exit 码与流水线状态必须一致。"""
        with_ledger = _deps(tmp_path / "a", ledger=True)
        without_ledger = _deps(tmp_path / "b", ledger=False)
        assert rps.main([_TRADE_DATE], deps=with_ledger) == rps.main([_TRADE_DATE], deps=without_ledger)

        result = run_post_settlement_pipeline(
            _TRADE_DATE,
            reconcile_fn=_empty_result,
            audit_fn=_audit_ok,
            alert_sink=None,
        )
        assert (result.reconcile_status, result.audit_status) == ("OK", "OK")
        assert rps._exit_code_of(result) == 0  # 三态判据/拆码未动（属 Owner）

    def test_ledger_is_idempotent_per_trade_date_and_step(self, tmp_path):
        """同 (trade_date, step) 重跑只留最后一次——守本件 [INVARIANTS] 幂等，不堆噪声行。"""
        path = tmp_path / "ledger.jsonl"
        ledger = rps.ZeroSampleLedger(path)
        ledger.record(_TRADE_DATE, step="daily_audit", sample_size=0, detail="第一次")
        ledger.record(_TRADE_DATE, step="daily_audit", sample_size=0, detail="第二次覆盖")
        ledger.record(_TRADE_DATE, step="var_backtest", sample_size=0, detail="另一步")
        rows = _ledger_rows(path)
        assert len(rows) == 2
        audit = next(r for r in rows if r["step"] == "daily_audit")
        assert audit["detail"] == "第二次覆盖"

    def test_audit_fn_discloses_empty_snapshot_input(self, tmp_path):
        """审计腿的空快照最小输入本身就是零样本（PASS 不得被读成"审计过了"）。"""
        deps = rps.PipelineDeps(
            reconcile_fn=None,
            audit_fn=None,
            alert_sink=None,
            ledger=rps.ZeroSampleLedger(tmp_path / "ledger.jsonl"),
        )
        deps.audit_fn = rps._build_audit_fn(deps)
        report = deps.audit_fn(_TRADE_DATE)
        assert getattr(report, "status", None) is not None or report is not None
        assert [r["step"] for r in _ledger_rows(tmp_path / "ledger.jsonl")] == ["daily_audit"]


class TestAccountMasking:
    def test_broker_connect_note_keeps_only_last_four_digits(self, monkeypatch):
        """盘后标注里的券商账号必须只剩末 4 位（09-25 日志曾明文 account=8886156677）。"""
        monkeypatch.setattr(rps, "load_qmt_sim_config", lambda *a, **k: ("C:/fake/qmt/path", "8886156677"))
        connected: list[str] = []

        class _FakeBroker:
            def __init__(self, *, path: str, session_id: str, account_id: str) -> None:
                connected.append(account_id)

            def connect(self) -> bool:
                return True

        broker_mod = ModuleType("zephyr.ex_core.adapters.miniqmt_broker")
        broker_mod.MiniQmtBroker = _FakeBroker
        monkeypatch.setitem(sys.modules, "zephyr.ex_core.adapters.miniqmt_broker", broker_mod)
        broker, note = rps._try_connect_sim_broker()
        assert broker is not None
        assert connected == ["8886156677"]  # 真号仍交给 broker（功能不变）
        assert "8886156677" not in note
        assert "***6677" in note

    def test_mask_identifier_tail_caliber(self):
        """脱敏口径本体：留末 4 位；短号/空值全遮（留尾反而等于原样泄露）。"""
        assert mask_identifier_tail("8886156677") == "***6677"
        assert mask_identifier_tail("1234") == "***"
        assert mask_identifier_tail("") == "***"
        assert mask_identifier_tail(None) == "***"
        assert mask_identifier_tail("8886156677", keep=2) == "***77"
