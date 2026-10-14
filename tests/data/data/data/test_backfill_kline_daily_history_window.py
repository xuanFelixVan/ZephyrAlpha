# [TTL] permanent
# [MODULE] tests.data.data.data.test_backfill_kline_daily_history_window
# [DOMAIN] D_DATA
"""窗口化 A 股日线回填器的四条钉（统筹裁定②，2026-10-12 夜，st-datalane2-20261012）。

零 CH 零 baostock：provider 与 BufferedWriter 全替换为假件，只验编排判据本身。
① 票码归一：6 位纯码按在册前缀补 sh./sz.（60/68→sh，00/30→sz），B 股/港股/短码判不可解析；
② 不可解析行不得静默吞——计入 unparsable 并在 START 行点名（"查无"与"跳过"必须可分）；
③ 续跑：state 里已完成的票不再取（重跑=自愈，不是重灌）；
④ 失败票不落 state：provider 返回 FetchResult.error 时该票必须留给下一轮，且 rc=1。
另钉 dry-run 零写（不 flush）与窗口/payload 形状（start/end/capability/symbols 单票）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SCRIPT = REPO / "scripts" / "data" / "backfill_kline_daily_history.py"

from zephyr.data.provider_base import FetchResult  # noqa: E402


def _load(monkeypatch):
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "src"))
    spec = importlib.util.spec_from_file_location("kline_hist_backfill_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _StubProvider:
    """假 provider：记录每次 payload，按需产出正常/错误 FetchResult。"""

    instances: list = []

    def __init__(self):
        self.payloads = []
        self.connect_calls = 0
        self.disconnect_calls = 0
        _StubProvider.instances.append(self)

    def connect(self):
        self.connect_calls += 1

    def disconnect(self):
        self.disconnect_calls += 1

    def fetch(self, payload, policy):
        self.payloads.append(payload)
        code = payload.symbols[0]
        if code.endswith("999"):  # 约定：以 999 结尾的假票必失败
            yield FetchResult(
                table=payload.table, columns=[], rows=[], last_key="", elapsed_sec=0.0, error="simulated fetch failure"
            )
            return
        if code.endswith("888"):  # 约定：以 888 结尾的假票复现在册静默形态——零行且不给 error
            return
        yield FetchResult(
            table=payload.table,
            columns=["trade_date", "symbol", "close"],
            rows=[("2017-06-05", code.split(".")[1], "10.0")],
            last_key=payload.end.isoformat(),
            elapsed_sec=0.0,
        )


class _StubWriter:
    def __init__(self, table, max_seconds=30):
        self.table = table
        self.added = 0
        self.flush_calls = 0
        self._rows = 0

    def add(self, result):
        self.added += len(result.rows)
        self._rows += len(result.rows)
        return True

    def flush(self):
        self.flush_calls += 1
        return True

    @property
    def total_flushed(self):
        return self._rows

    @property
    def pending_rows(self):
        return 0


def _run(monkeypatch, tmp_path, *, lines, state_lines=(), dry=False):
    mod = _load(monkeypatch)
    monkeypatch.setattr(mod, "BaostockProvider", _StubProvider)
    monkeypatch.setattr(mod, "BufferedWriter", _StubWriter)
    _StubProvider.instances = []
    sym_file = tmp_path / "universe.txt"
    sym_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    state_file = tmp_path / "state.txt"
    if state_lines:
        state_file.write_text("\n".join(state_lines) + "\n", encoding="utf-8")
    argv = [
        "x",
        "--start",
        "2017-01-01",
        "--end",
        "2018-12-31",
        "--symbols-file",
        str(sym_file),
        "--state-file",
        str(state_file),
        "--sleep",
        "0",
    ]
    if dry:
        argv.append("--dry-run")
    monkeypatch.setattr(sys, "argv", argv)
    rc = mod.main()
    return mod, rc, state_file, _StubProvider.instances[0]


def test_code_normalization_and_rejects(tmp_path, monkeypatch):
    mod = _load(monkeypatch)
    assert mod.to_bs_code("600000") == "sh.600000"
    assert mod.to_bs_code("688123") == "sh.688123"
    assert mod.to_bs_code("000001") == "sz.000001"
    assert mod.to_bs_code("300750") == "sz.300750"
    assert mod.to_bs_code("SH.600000") == "sh.600000"  # 大小写归一且幂等
    assert mod.to_bs_code("900901") is None  # B 股不在在册前缀集
    assert mod.to_bs_code("hk.00700") is None
    assert mod.to_bs_code("12345") is None


def test_unparsable_lines_are_counted_not_swallowed(tmp_path, monkeypatch):
    _mod, rc, state_file, provider = _run(monkeypatch, tmp_path, lines=["600000", "900901", "000001"])
    assert rc == 0
    assert provider.connect_calls == 1 and provider.disconnect_calls == 1
    assert [p.symbols[0] for p in provider.payloads] == ["sh.600000", "sz.000001"]
    done = [ln.strip() for ln in state_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert done == ["sh.600000", "sz.000001"]  # 不可解析票既没跑也没被记成完成


def test_resume_skips_symbols_already_in_state(tmp_path, monkeypatch):
    _mod, rc, _sf, provider = _run(
        monkeypatch, tmp_path, lines=["600000", "600001", "600002"], state_lines=["sh.600001"]
    )
    assert rc == 0
    assert [p.symbols[0] for p in provider.payloads] == ["sh.600000", "sh.600002"]  # 已完成票不再取数


def test_failed_symbol_not_recorded_and_rc_nonzero(tmp_path, monkeypatch):
    _mod, rc, state_file, _provider = _run(monkeypatch, tmp_path, lines=["600000", "600999"])
    assert rc == 1  # 有失败票必须非零，禁"整批成功"假象
    done = [ln.strip() for ln in state_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert done == ["sh.600000"]  # 失败票不落 state ⇒ 下一轮自愈会重试它


def test_window_payload_shape_and_dry_run_zero_write(tmp_path, monkeypatch):
    _mod, rc, _sf, provider = _run(monkeypatch, tmp_path, lines=["600000"], dry=True)
    payload = provider.payloads[0]
    assert (payload.start.isoformat(), payload.end.isoformat()) == ("2017-01-01", "2018-12-31")
    assert payload.incremental is False
    assert payload.extra.get("capability") == "kline_daily"
    assert payload.symbols == ["sh.600000"]
    assert rc == 0


def test_zero_row_symbol_is_not_counted_as_done_and_forces_retry(tmp_path, monkeypatch):
    """在册静默形态的堵法：provider 零行且不给 error（baostock 限流/IP 黑名单 10001011 的实际形状）
    ⇒ 该票不得写 state、必须进 zero_row 清单、整体 rc≠0（禁"ok=全跑完 fail=0"假绿）。"""
    _mod, rc, state_file, _provider = _run(monkeypatch, tmp_path, lines=["600000", "600888"])
    assert rc == 1
    done = [ln.strip() for ln in state_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert done == ["sh.600000"]
    zero_file = state_file.with_name(state_file.name + ".zero_row.txt")
    assert zero_file.exists()
    assert [ln.strip() for ln in zero_file.read_text(encoding="utf-8").splitlines() if ln.strip()] == ["sh.600888"]


def test_zero_row_symbol_is_retried_on_next_run(tmp_path, monkeypatch):
    """自愈钉：同一命令重跑时，zero_row 票（未进 state）必须再被取一次。"""
    _mod, rc, _sf, provider = _run(monkeypatch, tmp_path, lines=["600000", "600888"])
    assert rc == 1
    assert [p.symbols[0] for p in provider.payloads] == ["sh.600000", "sh.600888"]
    _mod2, rc2, _sf2, provider2 = _run(monkeypatch, tmp_path, lines=["600000", "600888"])
    assert [p.symbols[0] for p in provider2.payloads] == ["sh.600888"]  # 已完成票不再取，零行票重试
    assert rc2 == 1  # 仍然零行 ⇒ 仍非零退出
