# [BLUEPRINT] MOD-BT-087 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_paper_ledger
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_paper_ledger
# [CONSUMERS] 模拟盘方案C质量守卫（MODIFY-GUARD: sim_paper_ledger/sim_trade_log）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读断言基于已落库事实；重建等价性=事件溯源设计的核心验收线
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-087 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim_paper_ledger 质量守卫——钱包日账/事件流水/重建等价性三断言（真实台账只读）。"""

from __future__ import annotations

import importlib.util
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_paper_ledger", _REPO / "scripts" / "backtest" / "sim_paper_ledger.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_paper_ledger"] = mod
spec.loader.exec_module(mod)


def _run_replay() -> str:
    buf = StringIO()
    orig = sys.stdout
    sys.stdout = buf
    try:
        res = mod.run("replay_demo", "2026-07-01", "2026-09-11")
    finally:
        sys.stdout = orig
    assert res["rows"] and res["events"]
    return json.dumps({"final_equity": res["final_equity"], "rows": len(res["rows"]),
                       "events": len(res["events"])})


def test_replay_pipeline_consistent():
    """回放：钱包行=窗口交易日数（>=52 下限，随指数源日历漂移容忍），事件=2（一进一出），权益>初始。

    2026-09-14：行数硬等值 52 放宽为下限断言——指数源在窗口内回补/新增交易日
    会使回放行数自然增长（钱包行=交易日数由实现结构性保证），硬编码天数会
    随数据漂移误报；一进一出事件数与权益增长才是本守卫的核心不变量。
    """
    out = json.loads(_run_replay())
    assert out["rows"] >= 52
    assert out["events"] == 2
    assert out["final_equity"] > mod.INITIAL_CAPITAL


def test_rebuild_matches_pocket():
    """事件流重建的钱包日账与落库快照逐字段一致（容差 0.01 元）。"""
    rows = mod.rebuild(mod.STRATEGY_ID, "replay_demo", "2026-07-01", "2026-09-11")
    orig = mod._q(
        "SELECT trade_date, argMax(cash, ingest_ts), argMax(shares, ingest_ts),"
        " argMax(position_value, ingest_ts), argMax(equity, ingest_ts)"
        " FROM c1_backtest.sim_pocket_daily WHERE strategy_id = 'STR-VREV-025'"
        " GROUP BY trade_date ORDER BY trade_date")
    assert len(orig) >= 50 and len(rows) >= len(orig)
    # 按日期对齐比较（源指数回补使重建比落库快照多出新交易日时不误报；
    # 交集内逐字段等值=事件溯源重建等价性的核心验收线，不容差漂移）
    orig_by_date = {str(r[0]): r for r in orig}
    mismatch = 0
    compared = 0
    for rebuilt in rows:
        landed = orig_by_date.get(str(rebuilt[0]))
        if landed is None:
            continue
        compared += 1
        for a, b in [(rebuilt[3], landed[1]), (rebuilt[5], landed[2]),
                     (rebuilt[6], landed[3]), (rebuilt[7], landed[4])]:
            if abs(float(a) - float(b)) > 0.01:
                mismatch += 1
    assert compared >= 50, "重建与落库快照交集日期不足（覆盖漂移）"
    assert mismatch == 0


def test_events_have_reason_snapshot():
    """每个事件必带触发判据快照（AI 复核需求的最低保障）。"""
    ev = mod._q("SELECT signal_reason FROM c1_backtest.sim_trade_log FINAL "
                "WHERE strategy_id = 'STR-VREV-025'")
    assert ev and all(r[0] and len(str(r[0])) > 5 for r in ev)


# ---------- S08 C1 多策略开户（全离线：CH/intake 注册表全 mock，零生产 IO） ----------
class TestC1MultiStrategyWallet:
    """ensure_wallet 幂等开户 / --from-registry 多策略 / CLI 参数化（C1 验收）。"""

    @pytest.fixture()
    def offline(self, tmp_path, monkeypatch):
        """离线环境：存在性查询=[(0,)]（无钱包行）、run=假单日行、write_tsv 捕获不落库。"""
        from zephyr.data import ch_writer

        calls = {"writes": []}
        monkeypatch.setattr(mod, "_q", lambda sql: [(0,)])
        monkeypatch.setattr(
            mod, "run",
            lambda mode, start, end, run_id=None, strategy_id=None: {
                "rows": [[start, strategy_id or mod.STRATEGY_ID, mod.INITIAL_CAPITAL,
                          mod.INITIAL_CAPITAL, "", 0.0, 0.0, mod.INITIAL_CAPITAL, 0.0,
                          "cash", mode, run_id, ""]],
                "events": [], "final_equity": mod.INITIAL_CAPITAL, "days": 1,
                "entry_px_last": 0.0})

        def fake_write(table, cols, tsv_bytes):
            calls["writes"].append(table)
            return True

        monkeypatch.setattr(ch_writer, "write_tsv", fake_write)
        return calls

    def test_ensure_wallet_idempotent_repeat_zero_side_effect(self, offline, monkeypatch):
        """同策略+日已有行=跳过且零副作用（重复调用零写库）。"""
        r1 = mod.ensure_wallet(mod.STRATEGY_ID, day="2026-09-15")
        assert r1["created"] is True
        assert offline["writes"] == ["c1_backtest.sim_pocket_daily"]  # run() 假事件=仅日账表
        monkeypatch.setattr(mod, "_q", lambda sql: [(1,)])  # 第二次调用前：行已存在
        offline["writes"].clear()
        r2 = mod.ensure_wallet(mod.STRATEGY_ID, day="2026-09-15")
        assert r2["created"] is False and r2["why"] == "row_exists"
        assert offline["writes"] == []  # 零副作用

    def test_ensure_wallet_builtin_uses_engine_row(self, offline):
        """内置引擎策略走 run() 全口径（行 strategy_id=STR-VREV-025，既有行为等值）。"""
        r = mod.ensure_wallet(mod.STRATEGY_ID, day="2026-09-15")
        assert r["created"] is True
        # 行内容经 _write_rows 序列化，此处以写入表序断言（日账表；无事件）
        assert offline["writes"] == ["c1_backtest.sim_pocket_daily"]

    def test_ensure_wallet_foreign_strategy_open_row(self, offline, monkeypatch):
        """非内置引擎策略=开户行（signal=open 初始资金现金仓，不伪造信号/收益）。"""
        monkeypatch.setattr(mod, "run",
                            lambda *a, **k: (_ for _ in ()).throw(
                                AssertionError("非内置引擎策略不得走内置引擎")))
        r = mod.ensure_wallet("STR-E-TIMING-001", day="2026-09-15", code_path="x/y.py")
        assert r["created"] is True
        # 开户行+开户事件=两张表都写
        assert offline["writes"] == ["c1_backtest.sim_pocket_daily", "c1_backtest.sim_trade_log"]

    def test_open_wallets_from_registry_multi(self, offline, tmp_path, monkeypatch):
        """--from-registry 多策略：只服务 lifecycle==sim 条目，逐个幂等开户。"""
        from zephyr.strategy_pipeline import intake as intake_mod

        reg = tmp_path / "strategy_registry.yaml"
        reg.write_text(
            "strategies:\n"
            "  - strategy_id: STR-SIM-A-001\n    lifecycle_status: sim\n    code_path: a.py\n"
            "  - strategy_id: STR-SIM-B-002\n    lifecycle_status: sim\n    code_path: \"\"\n"
            "  - strategy_id: STR-CAND-001\n    lifecycle_status: candidate\n"
            "  - strategy_id: STR-PAP-001\n    lifecycle_status: paper\n",
            encoding="utf-8")
        monkeypatch.setattr(intake_mod, "REGISTRY", reg)
        seen = []
        monkeypatch.setattr(mod, "ensure_wallet",
                            lambda sid, day=None, mode="sim_daily", code_path="":
                            seen.append((sid, day)) or {"created": True})
        out = mod.open_wallets_from_registry(day="2026-09-15")
        assert [s for s, _ in seen] == ["STR-SIM-A-001", "STR-SIM-B-002"]
        assert all(d == "2026-09-15" for _, d in seen)
        assert out["opened"] == ["STR-SIM-A-001", "STR-SIM-B-002"] and out["errors"] == []

    def test_open_wallets_fail_closed_collects_then_raises(self, offline, tmp_path, monkeypatch):
        """单条失败不阻断其余条目，循环结束统一 fail-closed 抛错。"""
        from zephyr.strategy_pipeline import intake as intake_mod

        reg = tmp_path / "strategy_registry.yaml"
        reg.write_text(
            "strategies:\n"
            "  - strategy_id: STR-SIM-A-001\n    lifecycle_status: sim\n"
            "  - strategy_id: STR-SIM-B-002\n    lifecycle_status: sim\n",
            encoding="utf-8")
        monkeypatch.setattr(intake_mod, "REGISTRY", reg)

        def ensure(sid, day=None, mode="sim_daily", code_path=""):
            if sid == "STR-SIM-A-001":
                raise RuntimeError("CH down")
            return {"created": True}

        monkeypatch.setattr(mod, "ensure_wallet", ensure)
        with pytest.raises(RuntimeError, match="fail-closed"):
            mod.open_wallets_from_registry()

    def test_registry_sim_entries_reads_intake_loader(self, tmp_path, monkeypatch):
        """注册表读取复用 intake loader（monkeypatch intake.REGISTRY→tmp）。"""
        from zephyr.strategy_pipeline import intake as intake_mod

        reg = tmp_path / "strategy_registry.yaml"
        reg.write_text(
            "strategies:\n"
            "  - strategy_id: STR-SIM-A-001\n    lifecycle_status: sim\n    code_path: a.py\n"
            "  - strategy_id: STR-CAND-001\n    lifecycle_status: candidate\n",
            encoding="utf-8")
        monkeypatch.setattr(intake_mod, "REGISTRY", reg)
        entries = mod.registry_sim_entries()
        assert entries == [{"strategy_id": "STR-SIM-A-001", "code_path": "a.py"}]

    def test_cli_guards_and_from_registry(self, monkeypatch):
        """CLI：--from-registry 拒绝 replay_demo；sim_daily 走 open_wallets_from_registry。"""
        called = {}

        def fake_open(day=None):
            called["day"] = day
            return {"opened": ["STR-SIM-A-001"], "skipped": ["STR-VREV-025"], "errors": []}

        monkeypatch.setattr(mod, "open_wallets_from_registry", fake_open)
        monkeypatch.setattr(sys, "argv",
                            ["sim_paper_ledger.py", "--mode", "sim_daily", "--from-registry",
                             "--start", "2026-09-15"])
        mod.main()
        assert called["day"] == "2026-09-15"
        monkeypatch.setattr(sys, "argv",
                            ["sim_paper_ledger.py", "--mode", "replay_demo", "--from-registry"])
        with pytest.raises(SystemExit):
            mod.main()
        # 非 VREV 策略禁入 replay_demo/rebuild（无内联引擎）
        monkeypatch.setattr(sys, "argv",
                            ["sim_paper_ledger.py", "--mode", "replay_demo",
                             "--strategy-id", "STR-E-TIMING-001"])
        with pytest.raises(SystemExit):
            mod.main()
