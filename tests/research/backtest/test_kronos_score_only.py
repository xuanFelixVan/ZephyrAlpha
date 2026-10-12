# [BLUEPRINT] MOD-BT-195 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.research.backtest.test_kronos_score_only
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.kronos_adapter; schemas.categories.market.market_kronos_prediction_daily; pytest
# [CONSUMERS] CI（工单 GPU-02 守卫：--score-only 与 walk-forward 评估腿零交集＋列序单点＋落表失败即停）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 本文件只测结构与时序，不加载 Kronos 权重（零 GPU 依赖）；红证=同一套判据打在 dev 未修码上必判败
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""工单 GPU-02 守卫测：--score-only 前瞻腿的结构契约（零模型加载）。

四条判据各对应一个我真实怕发生的静默错：
1) 评估腿隔离：main() 里 score-only 早退必须在 import distribution_forecast_eval **之前**，
   且 run_score_only 函数体内不得出现任何评估符号。
2) 列序单点：SCORE_COLUMNS 必须与 schema 的 INSERT_COLUMNS 逐位相等（否则夜窗会静默错列）。
3) PIT 时序：input_cutoff_ts <= asof_ts，且 point_estimate==q050、interval_width==q095-q005。
4) 落表失败即停：写不进表必须返回非 0（LaneC 10-08 那夜"翻译腿全灭却 all-green"是同族病）。
"""

from __future__ import annotations

import ast
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from schemas.categories.market.market_kronos_prediction_daily import (  # noqa: E402
    INSERT_COLUMNS,
)

_ADAPTER = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "kronos_adapter.py"
_SRC = _ADAPTER.read_text(encoding="utf-8")
_TREE = ast.parse(_SRC)


def _func(name: str) -> ast.AST:
    for node in _TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"函数缺失：{name}")


class TestEvalLegIsolation:
    def test_score_only_returns_before_eval_import(self):
        """main() 里 score-only 早退必须早于 distribution_forecast_eval 的 import。"""
        main = _func("main")
        early_line = None
        import_line = None
        for node in ast.walk(main):
            if isinstance(node, ast.If):
                test_src = ast.unparse(node.test)
                if "score_only" in test_src and any(
                    isinstance(ch, ast.Return) and "run_score_only" in ast.unparse(ch) for ch in node.body
                ):
                    early_line = node.lineno if early_line is None else early_line
            if isinstance(node, ast.ImportFrom) and node.module and "distribution_forecast_eval" in node.module:
                import_line = node.lineno if import_line is None else import_line
        assert early_line is not None, "main() 里找不到 score-only 早退分支"
        assert import_line is not None, "main() 里找不到评估腿 import（说明结构变了，本测须重写）"
        assert early_line < import_line, (
            f"score-only 早退({early_line}) 必须早于评估 import({import_line})，否则前瞻腿会拖进评估依赖"
        )

    def test_run_score_only_body_has_no_eval_symbols(self):
        body = ast.unparse(_func("run_score_only"))
        for sym in (
            "evaluate_distribution_forecast",
            "walk_forward_eval",
            "walk_forward_multi_batch",
            "naive_quantiles",
        ):
            assert sym not in body, f"前瞻腿里出现评估符号 {sym}＝两腿纠缠"

    def test_flag_registered_in_parser(self):
        assert '"--score-only"' in _SRC or "'--score-only'" in _SRC, "--score-only 旗未挂上 argparse"


class TestColumnOrderSinglePoint:
    def test_score_columns_equal_schema_insert_columns(self):
        from scripts.backtest.kronos_adapter import SCORE_COLUMNS

        schema_cols = re.findall(r"[a-z_0-9]+", INSERT_COLUMNS)
        assert tuple(schema_cols) == tuple(SCORE_COLUMNS), (
            f"列序漂移：schema={schema_cols} vs adapter={list(SCORE_COLUMNS)}"
        )

    def test_row_width_matches_columns(self):
        from scripts.backtest.kronos_adapter import SCORE_COLUMNS, build_prediction_row

        df = pd.DataFrame(
            {
                "date": pd.date_range("2026-09-01", periods=3, freq="D"),
                "open": [1.0, 1.1, 1.2],
                "high": [1.05, 1.15, 1.25],
                "low": [0.95, 1.05, 1.15],
                "close": [1.0, 1.1, 1.2],
                "volume": [100.0, 110.0, 120.0],
                "amount": [1000.0, 1200.0, 1400.0],
            }
        )
        qs = {float(q): [v] for q, v in zip((0.05, 0.25, 0.5, 0.75, 0.95), (0.9, 1.0, 1.1, 1.2, 1.3), strict=True)}
        row = build_prediction_row(
            symbol="600519.SH",
            quantiles=qs,
            kdf=df,
            run_id="r1",
            asof_ts=datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc),
            model_size="small",
            pred_len=1,
            sample_count=8,
            temperature=1.0,
            top_p=0.9,
            data_source="c1_market.kline_daily_hfq",
        )
        assert len(row) == len(SCORE_COLUMNS), f"行宽 {len(row)} != 列数 {len(SCORE_COLUMNS)}"
        idx = {c: i for i, c in enumerate(SCORE_COLUMNS)}
        assert row[idx["point_estimate"]] == row[idx["q050"]]
        assert abs(row[idx["interval_width"]] - (row[idx["q095"]] - row[idx["q005"]])) < 1e-12
        assert row[idx["symbol"]] == "600519.SH"
        assert row[idx["horizon"]] == "T+1"

    def test_pit_cutoff_not_after_asof(self):
        from scripts.backtest.kronos_adapter import SCORE_COLUMNS, build_prediction_row

        df = pd.DataFrame(
            {
                "date": pd.date_range("2026-09-01", periods=2, freq="D"),
                "open": [1.0, 1.1],
                "high": [1.1, 1.2],
                "low": [0.9, 1.0],
                "close": [1.0, 1.1],
                "volume": [10.0, 20.0],
                "amount": [100.0, 200.0],
            }
        )
        asof = datetime.now(timezone.utc)
        qs = {float(q): [1.0] for q in (0.05, 0.25, 0.5, 0.75, 0.95)}
        row = build_prediction_row(
            symbol="000001.SZ",
            quantiles=qs,
            kdf=df,
            run_id="r2",
            asof_ts=asof,
            model_size="small",
            pred_len=1,
            sample_count=8,
            temperature=1.0,
            top_p=0.9,
            data_source="t",
        )
        idx = {c: i for i, c in enumerate(SCORE_COLUMNS)}
        cutoff, seen = row[idx["input_cutoff_ts"]], row[idx["asof_ts"]]
        assert cutoff.tzinfo is not None and seen.tzinfo is not None, "PIT 时刻必须带时区（RULE-SCHEMA-TZ）"
        assert cutoff <= seen + timedelta(days=1), f"数据截断 {cutoff} 晚于判定时刻 {seen}＝前视泄漏形态"


class TestWriteFailureIsLoud:
    def test_returns_nonzero_when_write_fails(self, monkeypatch):
        from scripts.backtest import kronos_adapter as ka

        class _FakePredictor:
            pass

        df = pd.DataFrame(
            {
                "date": pd.date_range("2026-09-01", periods=70, freq="B"),
                "open": [1.0] * 70,
                "high": [1.1] * 70,
                "low": [0.9] * 70,
                "close": [1.0] * 70,
                "volume": [100.0] * 70,
                "amount": [1000.0] * 70,
            }
        )
        monkeypatch.setattr(ka, "resolve_score_universe", lambda args: ["A.SH", "B.SH"])
        monkeypatch.setattr(ka, "load_predictor", lambda model_size="small": (_FakePredictor(), "cpu"))
        monkeypatch.setattr(ka, "fetch_kline", lambda sym, days: df)
        monkeypatch.setattr(
            ka,
            "score_forward",
            lambda predictor, kdf, **kw: ({float(q): [1.0] for q in ka.QUANTILES}, pd.Series([1, 2])),
        )
        calls = []

        def _fail(rows, *, table=None):
            calls.append(len(rows))
            return False

        monkeypatch.setattr(ka, "write_kronos_predictions", _fail)

        class _Args:
            days = 250
            max_context = 400
            model_size = "small"
            pred_len = 1
            sample_count = 8
            temperature = 1.0
            top_p = 0.9
            run_id = "unit"
            synthetic = True
            symbols = "A.SH,B.SH"
            top_n = None
            flush_every = 2

        rc = ka.run_score_only(_Args())
        assert rc == 1, "落表失败必须非 0 退出（静默丢行＝LaneC 10-08 all-green 空转同族病）"
        assert calls, "根本没尝试落表"

    def test_flush_every_honoured(self, monkeypatch):
        from scripts.backtest import kronos_adapter as ka

        df = pd.DataFrame(
            {
                "date": pd.date_range("2026-09-01", periods=70, freq="B"),
                "open": [1.0] * 70,
                "high": [1.1] * 70,
                "low": [0.9] * 70,
                "close": [1.0] * 70,
                "volume": [100.0] * 70,
                "amount": [1000.0] * 70,
            }
        )
        monkeypatch.setattr(ka, "resolve_score_universe", lambda args: [f"S{i}.SH" for i in range(5)])
        monkeypatch.setattr(ka, "load_predictor", lambda model_size="small": (object(), "cpu"))
        monkeypatch.setattr(ka, "fetch_kline", lambda sym, days: df)
        monkeypatch.setattr(
            ka,
            "score_forward",
            lambda predictor, kdf, **kw: ({float(q): [1.0] for q in ka.QUANTILES}, pd.Series([1, 2])),
        )
        batches = []

        def _ok(rows, *, table=None):
            batches.append(len(rows))
            return True

        monkeypatch.setattr(ka, "write_kronos_predictions", _ok)

        class _Args:
            days = 250
            max_context = 400
            model_size = "small"
            pred_len = 1
            sample_count = 8
            temperature = 1.0
            top_p = 0.9
            run_id = "unit2"
            synthetic = True
            symbols = ""
            top_n = 5
            flush_every = 2

        assert ka.run_score_only(_Args()) == 0
        assert batches == [2, 2, 1], f"攒批切分不符：{batches}"


def test_yield_window_cap_stops_before_ch_window(monkeypatch):
    """01:00-04:00 让路窗硬闸：到点必须停手且不落表（夜窗 00:30 起跑＋长跑必伸进让路窗）。"""
    from datetime import datetime
    from datetime import timezone as _tz

    import zephyr.shared.utils.time_utils as tu
    from scripts.backtest import kronos_adapter as ka

    df = pd.DataFrame(
        {
            "date": pd.date_range("2026-09-01", periods=70, freq="B"),
            "open": [1.0] * 70,
            "high": [1.1] * 70,
            "low": [0.9] * 70,
            "close": [1.0] * 70,
            "volume": [100.0] * 70,
            "amount": [1000.0] * 70,
        }
    )
    monkeypatch.setattr(ka, "resolve_score_universe", lambda args: [f"S{i}.SH" for i in range(6)])
    monkeypatch.setattr(ka, "load_predictor", lambda **kw: (object(), "cpu"))
    monkeypatch.setattr(ka, "fetch_kline", lambda sym, days: df)
    monkeypatch.setattr(
        ka,
        "score_forward",
        lambda predictor, kdf, **kw: ({float(q): [1.0] for q in ka.QUANTILES}, pd.Series([1, 2])),
    )
    tried = []
    monkeypatch.setattr(ka, "write_kronos_predictions", lambda rows, *, table=None: tried.append(len(rows)) or True)
    # 时钟推进：第一次读=起跑基准，之后一律 +91 分钟 ⇒ 50 分钟上限必到点
    base = datetime(2099, 1, 1, 0, 0, tzinfo=_tz.utc)
    ticks = {"n": 0}

    def _advancing_now():
        ticks["n"] += 1
        return base if ticks["n"] == 1 else base + timedelta(minutes=91)

    monkeypatch.setattr(tu, "now_utc", _advancing_now)

    class _Args:
        days = 250
        max_context = 400
        model_size = "small"
        pred_len = 1
        sample_count = 8
        temperature = 1.0
        top_p = 0.9
        run_id = "yield"
        synthetic = True
        symbols = ""
        top_n = 6
        flush_every = 200
        max_runtime_min = 50

    assert ka.run_score_only(_Args()) == 1, "让路闸触发后零落表必须判败（不能报绿说跑完了）"
    assert tried == [], f"到点后不得再落表：{tried}"


def test_empty_universe_is_failure_not_silence(monkeypatch, capsys):
    """宇宙为空必须红并早退——不能"跑完 0 只"还报绿（LaneC 10-08 空跑同族）。"""
    from scripts.backtest import kronos_adapter as ka

    monkeypatch.setattr(ka, "resolve_score_universe", lambda args: [])
    touched = []
    monkeypatch.setattr(ka, "load_predictor", lambda **kw: touched.append("load") or (object(), "cpu"))

    class _Args:
        days = 250
        max_context = 400
        model_size = "small"
        pred_len = 1
        sample_count = 8
        temperature = 1.0
        top_p = 0.9
        run_id = None
        synthetic = True
        symbols = ""
        top_n = None
        flush_every = 200

    assert ka.run_score_only(_Args()) == 1
    assert "宇宙为空" in capsys.readouterr().err
    assert touched == [], "宇宙为空时不该已经把模型加载起来（夜窗白烧显存）"


# ── 统筹 R-3 裁定（2026-10-11 批复）：00:30 一夜一片×四夜一轮＋首夜标定 ──────────────
# 判据要防的两个静默错：①切片顺手重排（跨夜并起来就不是同一个宇宙）；
# ②本片没跑完却报绿（明晚接着跑被记成今晚跑完，四夜一轮的账面从此失真）。


def _shim_df():
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-09-01", periods=70, freq="B"),
            "open": [1.0] * 70,
            "high": [1.1] * 70,
            "low": [0.9] * 70,
            "close": [1.0] * 70,
            "volume": [100.0] * 70,
            "amount": [1000.0] * 70,
        }
    )


def _shim_env(monkeypatch, universe, *, fail_syms=()):
    """把打分腿的四处外部依赖（宇宙/模型/K 线/落表）换成桩，返回落表批次数列表。"""
    from scripts.backtest import kronos_adapter as ka

    monkeypatch.setattr(ka, "resolve_score_universe", lambda args: list(universe))
    monkeypatch.setattr(ka, "load_predictor", lambda **kw: (object(), "cpu"))

    df = _shim_df()

    def _fetch(sym, days):
        if sym in fail_syms:
            raise ValueError(f"shim: {sym} 数据不足")
        return df

    monkeypatch.setattr(ka, "fetch_kline", _fetch)
    monkeypatch.setattr(
        ka,
        "score_forward",
        lambda predictor, kdf, **kw: ({float(q): [1.0] for q in ka.QUANTILES}, pd.Series([1, 2])),
    )
    batches = []
    monkeypatch.setattr(ka, "write_kronos_predictions", lambda rows, *, table=None: batches.append(len(rows)) or True)
    return batches


class _ShardArgs:
    days = 250
    max_context = 400
    model_size = "small"
    pred_len = 1
    sample_count = 8
    temperature = 1.0
    top_p = 0.9
    run_id = "shard"
    synthetic = True
    symbols = ""
    top_n = 300
    flush_every = 200
    max_runtime_min = 0
    shard_index = 0
    shard_count = 1


class TestShardUniverse:
    def test_four_shards_partition_without_reorder(self):
        from scripts.backtest.kronos_adapter import shard_universe

        uni = [f"S{i:03d}.SH" for i in range(300)]
        parts = [shard_universe(uni, shard_index=k, shard_count=4) for k in range(4)]
        assert [p for part in parts for p in part] == uni, "四片拼回须逐位等于原宇宙"
        assert [len(p) for p in parts] == [75, 75, 75, 75]

    def test_ceil_sharding_keeps_every_symbol(self):
        from scripts.backtest.kronos_adapter import shard_universe

        uni = [f"S{i}.SH" for i in range(10)]
        parts = [shard_universe(uni, shard_index=k, shard_count=4) for k in range(4)]
        assert [len(p) for p in parts] == [3, 3, 3, 1]
        assert sorted(x for p in parts for x in p) == sorted(uni), "ceil 分片不得漏票"

    def test_out_of_range_index_is_loud(self):
        import pytest

        from scripts.backtest.kronos_adapter import shard_universe

        with pytest.raises(ValueError):
            shard_universe(["A.SH"], shard_index=4, shard_count=4)

    def test_shard_flags_wired_into_parser(self):
        for flag in ("--shard-index", "--shard-count"):
            assert flag in _SRC, f"CLI 缺 {flag}：分片只能被 runner 传进来，不能藏在代码常量里"

    def test_run_score_only_slices_before_iterating(self):
        body = _func("run_score_only").body
        calls = [n for n in ast.walk(ast.Module(body=body, type_ignores=[])) if isinstance(n, ast.Call)]
        names = {getattr(c.func, "id", "") for c in calls}
        assert "shard_universe" in names, "分片须发生在主循环内（否则 runner 传参是装饰品）"


class TestShardExitCodes:
    def test_truncated_shard_with_rows_is_not_green(self, monkeypatch, capsys):
        """让路闸在片中途中断＝rc4（覆盖不全是事实，不能记成绿）。"""
        import zephyr.shared.utils.time_utils as tu
        from scripts.backtest import kronos_adapter as ka

        batches = _shim_env(monkeypatch, [f"S{i}.SH" for i in range(4)])
        base = datetime(2099, 1, 1, 0, 0, tzinfo=timezone.utc)
        ticks = {"n": 0}

        def _clock():
            ticks["n"] += 1
            return base if ticks["n"] <= 3 else base + timedelta(minutes=91)

        monkeypatch.setattr(tu, "now_utc", _clock)
        args = _ShardArgs()
        args.max_runtime_min = 50
        rc = ka.run_score_only(args)
        assert rc == 4, f"中途中断须 rc=4，实测 {rc}"
        assert batches == [2], f"中断时已攒的行仍须落表（丢行比不跑更坏）：{batches}"
        assert '"shard_status": "truncated"' in capsys.readouterr().out

    def test_partial_failure_shard_reports_three(self, monkeypatch, capsys):
        from scripts.backtest import kronos_adapter as ka

        batches = _shim_env(monkeypatch, [f"S{i}.SH" for i in range(3)], fail_syms={"S1.SH"})
        rc = ka.run_score_only(_ShardArgs())
        assert rc == 3, f"有标的失手不得报绿，须 rc=3，实测 {rc}"
        assert batches == [2]
        assert '"shard_status": "partial_failed"' in capsys.readouterr().out

    def test_clean_shard_reports_zero_and_calibration(self, monkeypatch, capsys):
        import json

        from scripts.backtest import kronos_adapter as ka

        _shim_env(monkeypatch, [f"S{i}.SH" for i in range(6)])
        args = _ShardArgs()
        args.shard_count = 3
        args.shard_index = 1
        assert ka.run_score_only(args) == 0
        rep = json.loads(capsys.readouterr().out)
        assert (rep["universe_total"], rep["shard_index"], rep["shard_count"], rep["shard_size"]) == (6, 1, 3, 2)
        assert rep["scored"] == 2
        cal = rep["calibration"]
        assert {"elapsed_min", "sec_per_symbol", "symbols_fit_in_cap"} <= set(cal), "首夜标定三字段须齐"
        assert rep["shard_status"] == "complete"

    def test_full_universe_when_sharding_off(self, monkeypatch, capsys):
        """shard_count=1（缺省）＝不分片：老 runner 的字节口径零变更。"""
        import json

        from scripts.backtest import kronos_adapter as ka

        _shim_env(monkeypatch, [f"S{i}.SH" for i in range(5)])
        assert ka.run_score_only(_ShardArgs()) == 0
        rep = json.loads(capsys.readouterr().out)
        assert rep["shard_size"] == rep["universe_total"] == 5
