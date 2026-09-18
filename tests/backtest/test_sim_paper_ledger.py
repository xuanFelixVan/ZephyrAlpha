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
import sys
from datetime import date
from io import StringIO
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "sim_paper_ledger", _REPO / "scripts" / "backtest" / "sim_paper_ledger.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["sim_paper_ledger"] = mod
spec.loader.exec_module(mod)


def _replay(**kwargs) -> dict:
    """跑一次内置引擎回放（吞 stdout，返回值交调用方逐条断言）。

    断言一律放在用例里而非本 helper：同一句 `assert res["rows"] and res["events"]`
    写在 helper 里会让"危机日正确拦单"与"管线真的坏了"两种病塌缩成同一条红、
    且无法归因（本役 #273 反例形态）。
    """
    buf = StringIO()
    orig = sys.stdout
    sys.stdout = buf
    try:
        return mod.run("replay_demo", "2026-07-01", "2026-09-11", **kwargs)
    finally:
        sys.stdout = orig


def _crisis_state(day: str, *, state: str, p_r10: float, dominant: str):
    """造 CrisisState 判据（run() 文档明示 crisis_resolver 注入缝=测试用假件）。"""
    from zephyr.pf_alloc.crisis_gate import CrisisState

    return CrisisState(state=state, p_r10=p_r10, dominant=dominant,
                       source_date=date.fromisoformat(day), lag_days=0)


_NORMAL = lambda d: _crisis_state(d, state="normal", p_r10=0.02, dominant="r1")  # noqa: E731
_CRISIS = lambda d: _crisis_state(d, state="crisis", p_r10=0.60, dominant="r10")  # noqa: E731
_PANIC_ENTRY_DAY = "2026-07-17"   # 窗口内唯一 panic 信号日（2026-09-19 实测）
_FORCED_EXIT_DAY = "2026-08-13"   # 入场后满 HOLD_N 交易日强平日


def test_replay_pipeline_consistent():
    """危机闸放行日的一进一出全链：行数=窗口交易日数（>=52 下限，随指数源日历漂移容忍）、
    事件=2（一进一出）、权益>初始。

    2026-09-14：行数硬等值 52 放宽为下限断言——指数源在窗口内回补/新增交易日
    会使回放行数自然增长（钱包行=交易日数由实现结构性保证），硬编码天数会随数据漂移误报。
    2026-09-19（本车道）：**判据显式受控**——原用例现读 CH regime 快照，而 e1a975b158
    （WO-2a L3 危机闸，2026-09-18）落地后"危机日拦单不出事件"成为设计语义，于是
    "events==2" 从不变量退化为"取决于当日 regime 快照"的偶发事实。此处改用 run()
    既有的 crisis_resolver 注入缝钉住"放行"这一前提，让这条守卫重新只测它想测的东西
    （钱包/事件/权益的账实一致），而不是替 CH 数据状态背锅。断言只增不减。
    """
    res = _replay(crisis_resolver=_NORMAL)
    assert res["rows"] and res["events"]
    assert len(res["rows"]) >= 52
    assert len(res["events"]) == 2
    assert [e[3] for e in res["events"]] == ["entry", "exit"]
    assert [e[0] for e in res["events"]] == [_PANIC_ENTRY_DAY, _FORCED_EXIT_DAY]
    assert res["final_equity"] > mod.INITIAL_CAPITAL
    assert res["crisis_blocked_days"] == []


def test_replay_crisis_day_blocks_entry_with_trace():
    """WO-2a L3 新腿（加严方向，裁定 #321 允许）：crisis 日 panic 入场必须
    ① 不产生成交事件（0 事件，且不是"静默吞单"）、② 当日 signal=cash、
    ③ 行 note 留痕 crisis_gate:entry_blocked、④ 权益不动（存量不强平）。

    本车道 2026-09-19 实测：窗口内唯一 panic 日 2026-07-17 的 regime 快照
    dominant=r10 / p_r10=0.600 ⇒ 现读链当日正是此态，故上一用例的"2 事件"
    在现读口径下不成立——那不是我掰尺子，是尺子量的是两个东西。
    """
    res = _replay(crisis_resolver=_CRISIS)
    assert len(res["rows"]) >= 52
    assert res["events"] == []
    assert res["crisis_blocked_days"] == [_PANIC_ENTRY_DAY]
    row = next(r for r in res["rows"] if r[0] == _PANIC_ENTRY_DAY)
    assert row[9] == "cash"
    assert "crisis_gate:entry_blocked" in row[12]
    assert res["final_equity"] == pytest.approx(mod.INITIAL_CAPITAL)


def test_replay_crisis_resolver_error_fails_closed():
    """resolver 抛异常=读不到判据≠安全：必须 fail-closed 拦 entry 并在行 note 留原因。

    牙齿由变异证明：把该 except 腿改成 return False（fail-open）⇒ 本件红。
    """
    def _boom(day):
        raise RuntimeError("CH 不可读")

    res = _replay(crisis_resolver=_boom)
    assert res["events"] == []
    assert res["crisis_blocked_days"] == [_PANIC_ENTRY_DAY]
    row = next(r for r in res["rows"] if r[0] == _PANIC_ENTRY_DAY)
    assert "crisis_gate:resolver_error" in row[12]


def test_replay_live_chain_never_swallows_tradesilently():
    """现读 CH 的真链（无注入）必须落在可解释的两档之一，禁"既无事件又无留痕"。

    保留原 `assert res["rows"] and res["events"]` 的守门语义（管线不得空转），
    但把它从"必须 2 事件"改写成"必须要么成交、要么拦单留痕"——危机闸在 crisis 日
    正确地不成交，若仍钉死 2 事件就等于要求危机闸失效（放松方向，#321 禁）。
    """
    res = _replay()
    assert len(res["rows"]) >= 52
    assert res["events"] or res["crisis_blocked_days"], \
        "回放既无成交也无拦截留痕=静默空转（panic 信号或危机闸判据已失联）"
    noted = {r[0] for r in res["rows"] if r[12].startswith("crisis_gate:")}
    assert noted == set(res["crisis_blocked_days"]), "拦单日与留痕日不一致（审计缺口）"
    traded_days = {e[0] for e in res["events"]}
    assert not (traded_days & set(res["crisis_blocked_days"])), "被拦日仍出事件=闸漏了"


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
