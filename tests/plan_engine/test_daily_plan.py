# [A_test] module_id: MOD-PLAN-030 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-030 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六任务3
# [MODULE] tests.plan_engine.test_daily_plan
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""daily_plan 晨间预案生成器施工验证测试（判定台账标准 v0.1 §三表3 上半）。

覆盖：
- 触发表达式文法：词法/文法/词表/安全上限；**表达式注入红蓝**（dunder import/分号
  SQL/引号/下划线开头标识符/深度爆栈 全部 TriggerSyntaxError——白名单 AST 无 eval/exec）。
- 求值边界：比较符含等与不含等（>0.3 在 0.3 处为假）；四则优先级；AND/OR/NOT；
  特征缺席=(False, missing)（禁编造）；除零=不可满足。
- v0 三分支：参数→trigger 文本拼装；**互斥双校验红蓝**（结构网格探针 + 历史重放；
  手工构造重叠场景必 ValueError）。
- 历史先验：Laplace 手算对账；无场景日不计分母（口径测试）；样本不足退化均匀先验
  （fallback=True，和恒 1——红蓝项）。
- 特征装配：daily_features_of 手算对账；历史不足/前收非正→空 dict（禁 0 值冒充）。
- 发射：payload 过发射器 fail-closed 校验（真 emit_judgment + canned ch_writer 捕获
  TSV）；inputs_ref 首键 plan_date（幂等格式）；confidence 缺席折乘口径。
- 幂等（事件重放）：同 plan_date 已发射 → already_emitted 零发射；非 daily_kline 任务
  /失败任务 → skipped_wake_point；G 日线不在库 → data_insufficient；异常 → error 不反噬。
- 与 P1 发射器/结算器联测：发射行 12 列完备 → judgment_settler._settle_daily_plan
  （纯函数）联结 canned verification → scenario_brier 手算对账；无 verification 当日宽限
  not_matured / 隔日 unresolvable(verification_missing)（P1 宽限期惯例）。
全 monkeypatch/canned 隔离，不触真 ClickHouse（真库冒烟走 synthetic=1 标注+清理通道）。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.plan_engine import daily_plan as dp
from zephyr.plan_engine import judgment_settler as js
from zephyr.plan_engine.daily_plan import (
    NO_SCENARIO,
    RULE_PARAMS,
    TriggerSyntaxError,
    build_v0_scenarios,
    daily_features_of,
    eval_trigger_measurable,
    inputs_hash_of,
    maybe_emit_daily_plan,
    parse_trigger,
    validate_scenarios,
)


# ── 夹具（synthetic 日线——LCG 确定性伪随机，结构对齐 kline_index 行元组）──


def _kline_rows(n: int = 260, seed: int = 11) -> list[tuple]:
    """合成 n 日 OHLCV（确定性——循环同余生成器，零外部依赖）。"""
    rows: list[tuple] = []
    px = 4000.0
    state = seed
    for i in range(n):
        state = (state * 1103515245 + 12345) % (2**31)
        drift = ((state >> 16) % 200 - 100) / 10000.0  # ±1%
        o = px
        c = px * (1 + drift)
        h = max(o, c) * 1.004
        low = min(o, c) * 0.996
        vol = 1.0e8 + (state % 40) * 1.0e6
        rows.append((f"2026-{1 + i // 28:02d}-{1 + i % 28:02d}", round(o, 2), round(h, 2),
                     round(low, 2), round(c, 2), vol))
        px = c
    return rows


@pytest.fixture()
def canned_emit(monkeypatch):
    """真 emit_judgment + canned ch_writer 捕获（发射→TSV→行解析全链联测）。"""
    captured: dict[str, Any] = {}

    def _fake_write(table, columns, tsv_bytes, *a, **k):
        captured["table"] = table
        captured["columns"] = columns
        captured["tsv"] = tsv_bytes.decode("utf-8")
        from zephyr.data.ch_writer import WriteDisposition, WriteOutcome

        return WriteOutcome(WriteDisposition.CH_COMMITTED, "canned")

    import zephyr.data.ch_writer as cw

    monkeypatch.setattr(cw, "write_tsv_outcome", _fake_write)
    return captured


# ── 触发表达式文法（解析与注入红蓝）──


def test_parse_valid_expressions() -> None:
    for expr in (
        "open_gap_pct > 0.3",
        "open_gap_pct > 0.3 AND amount_ratio > 1.2",
        "open_gap_pct <= 0.3 AND open_gap_pct >= -0.3",
        "NOT (ret_intraday_pct < 0) OR amount_ratio >= 2",
        "open_gap_pct * 2 + 1 > 0.5",
        "amount_ratio / 2 == 0.6",
        "ret_intraday_pct != 0",
    ):
        assert parse_trigger(expr) is not None


def test_parse_injection_red_blue() -> None:
    """红蓝：表达式注入面（白名单文法结构性关闭 eval/exec）。"""
    bad = [
        "", "   ",
        "__import__('os').system(1)",
        "open_gap_pct; DROP TABLE judgment_daily_plan",
        "open_gap_pct > 0.3 OR '1'='1'",
        "exec('pass')",
        "open_gap_pct.__class__",
        "_hidden > 1",
        "os.getcwd() > 1",
        "open_gap_pct > 0.3 # comment",
        "open_gap_pct > (0.3",
        "open_gap_pct > 0.3 AND",
        "AND open_gap_pct > 0.3",
        "open_gap_pct >",
        "中文 > 0.3",
        "a" * 600,
        "(" * 30 + "1" + ")" * 30,
        "unknown_feature > 1",
    ]
    for expr in bad:
        with pytest.raises(TriggerSyntaxError):
            parse_trigger(expr)


def test_eval_comparison_boundaries() -> None:
    feats = {"open_gap_pct": 0.3, "amount_ratio": 1.2, "ret_intraday_pct": -0.1}
    assert eval_trigger_measurable(parse_trigger("open_gap_pct > 0.3"), feats) == (False, None)
    assert eval_trigger_measurable(parse_trigger("open_gap_pct >= 0.3"), feats) == (True, None)
    assert eval_trigger_measurable(parse_trigger("open_gap_pct >= -0.3 AND open_gap_pct <= 0.3"),
                                   feats) == (True, None)
    assert eval_trigger_measurable(parse_trigger("ret_intraday_pct < 0"), feats) == (True, None)


def test_eval_arithmetic_and_logic() -> None:
    feats = {"open_gap_pct": 0.4, "amount_ratio": 1.0, "ret_intraday_pct": -0.5}
    assert eval_trigger_measurable(parse_trigger("open_gap_pct * 2 > 0.7"), feats)[0] is True
    assert eval_trigger_measurable(parse_trigger("open_gap_pct - 0.2 > 0.3"), feats)[0] is False
    assert eval_trigger_measurable(parse_trigger("NOT ret_intraday_pct < 0"), feats)[0] is False
    assert eval_trigger_measurable(
        parse_trigger("ret_intraday_pct < 0 OR amount_ratio > 2"), feats)[0] is True
    # 除零=不可满足（不触发，非崩溃）
    ok, miss = eval_trigger_measurable(parse_trigger("amount_ratio / 0 > 1"), feats)
    assert ok is False and miss is not None


def test_eval_missing_feature_not_fabricated() -> None:
    """红蓝：特征缺席=(False, missing)——禁编造 0 值（0 是合法测量值，缺席是另一回事）。"""
    ok, miss = eval_trigger_measurable(
        parse_trigger("amount_ratio > 1.2"), {"open_gap_pct": 0.5})
    assert ok is False and miss == "missing:amount_ratio"


# ── v0 三分支与互斥双校验 ─--


def test_v0_scenarios_parseable_and_disjoint_grid() -> None:
    scs = build_v0_scenarios()
    assert [s["scenario_id"] for s in scs] == ["S1_attack", "S2_defense", "S3_oscillation"]
    for s in scs:
        parse_trigger(s["trigger"])  # 词表内标识符+文法合法（fail-closed 保证）
    validate_scenarios(scs)  # 结构网格探针不抛=互斥成立


def test_overlap_scenario_rejected_red_blue() -> None:
    """红蓝：条件重叠多场景同触发 → 发射拒绝（fail-closed）。"""
    overlap = [
        {"scenario_id": "A", "trigger": "open_gap_pct > 0.3", "path_prior": 0.5},
        {"scenario_id": "B", "trigger": "open_gap_pct > 0.3 AND amount_ratio > 0.5", "path_prior": 0.5},
    ]
    with pytest.raises(ValueError, match="互斥违例"):
        validate_scenarios(overlap)


def test_v0_trio_boundary_vectors_exactly_one_match() -> None:
    """缺口轴边界：±gap_band 严格归属单一分支（等值归 S3；S2 需 ret<0、S1 需放量）。"""
    scs = build_v0_scenarios()
    asts = [parse_trigger(s["trigger"]) for s in scs]
    for og in (-0.3001, -0.3, -0.2999, 0.0, 0.2999, 0.3, 0.3001):
        feats = {"open_gap_pct": og, "amount_ratio": 2.0, "ret_intraday_pct": -1.0}
        matched = [s["scenario_id"] for s, a in zip(scs, asts)
                   if eval_trigger_measurable(a, feats)[0]]
        assert len(matched) == 1, f"gap={og} 命中 {matched}"


def test_dead_scenario_detection_via_grid_red_blue() -> None:
    """红蓝：触发条件不可满足的死场景（词表特征永假式）在历史重放探针中现形。"""
    dead = [
        {"scenario_id": "IMPOSSIBLE", "trigger": "open_gap_pct > 9999", "path_prior": 1.0},
    ]
    # 死场景互斥合法（永不与别人重叠）但先验历史归类 n=0 → 均匀 fallback 路径可见
    rows = _kline_rows()
    prior, n, fallback = dp._history_priors(rows, dead, [parse_trigger(dead[0]["trigger"])],
                                            RULE_PARAMS)
    assert n == 0 and fallback is True
    assert abs(sum(prior.values()) - 1.0) < 1e-9


# ── 历史先验（Laplace 手算对账）──


def test_history_priors_laplace_handcheck() -> None:
    rows = _kline_rows(260)
    scs = build_v0_scenarios()
    asts = [parse_trigger(s["trigger"]) for s in scs]
    prior, n, fallback = dp._history_priors(rows, scs, asts, RULE_PARAMS)
    assert n > 0
    assert fallback is (n < int(RULE_PARAMS["min_classified_n"]))
    assert abs(sum(prior.values()) - 1.0) < 1e-9
    # 手算对账：按同口径逐日独立归类计数
    lookback = int(RULE_PARAMS["vol_lookback"])
    counts = {s["scenario_id"]: 0 for s in scs}
    for i in range(1, len(rows)):
        vol_hist = [float(r[5]) for r in rows[max(0, i - lookback):i]]
        feats = daily_features_of(rows[i - 1], rows[i], vol_hist)
        if not feats:
            continue
        for s, a in zip(scs, asts):
            if eval_trigger_measurable(a, feats)[0]:
                counts[s["scenario_id"]] += 1
                break
    alpha = float(RULE_PARAMS["prior_alpha"])
    denom = n + len(scs) * alpha
    if not fallback:
        for s in scs:
            assert prior[s["scenario_id"]] == pytest.approx(
                (counts[s["scenario_id"]] + alpha) / denom)


def test_no_scenario_day_excluded_from_denominator() -> None:
    """口径测试：无场景日不计分母（P(分支|场景日) 条件分布）。"""
    rows = [
        # (date, open, high, low, close, volume)——构造 2 个高开放量日（S1）+1 个平开日（无场景）
        # lookback=1 下 amount_ratio(i)=vol_i/vol_{i-1}：50→100→300 链保证 S1 两次触发
        ("2026-01-01", 100.0, 101.0, 99.0, 100.0, 100.0),
        ("2026-01-02", 100.0, 101.0, 99.0, 100.0, 50.0),   # 平开基期（缩量）
        ("2026-01-03", 102.0, 103.0, 101.0, 101.0, 100.0),  # 高开 +2% 量比 2 → S1
        ("2026-01-04", 102.5, 103.5, 101.5, 102.8, 300.0),  # 高开 +1.49% 量比 3 → S1
        ("2026-01-05", 102.8, 103.0, 102.0, 102.6, 100.0),  # 平开 → 无场景
    ]
    scs = [
        {"scenario_id": "S1", "trigger": "open_gap_pct > 1.0 AND amount_ratio > 1.5", "path_prior": 0.0},
    ]
    prior, n, fallback = dp._history_priors(rows, scs, [parse_trigger(scs[0]["trigger"])],
                                            {**RULE_PARAMS, "min_classified_n": 1,
                                             "vol_lookback": 1})
    assert n == 2  # 平开日不计 n
    alpha = float(RULE_PARAMS["prior_alpha"])
    assert prior["S1"] == pytest.approx((2 + alpha) / (2 + alpha))


# ── 特征装配 ─--


def test_daily_features_handcheck() -> None:
    prev = ("2026-01-01", 100.0, 101.0, 99.0, 100.0, 100.0)
    cur = ("2026-01-02", 101.0, 102.0, 100.5, 101.5, 150.0)
    vol_hist = [100.0] * 20
    f = daily_features_of(prev, cur, vol_hist)
    assert f["open_gap_pct"] == pytest.approx(1.0)
    assert f["ret_intraday_pct"] == pytest.approx(1.5)
    assert f["amount_ratio"] == pytest.approx(1.5)


def test_daily_features_insufficient_history_empty() -> None:
    prev = ("2026-01-01", 100.0, 101.0, 99.0, 100.0, 100.0)
    cur = ("2026-01-02", 101.0, 102.0, 100.5, 101.5, 150.0)
    assert daily_features_of(prev, cur, [100.0] * 5) == {}  # 历史不足
    assert daily_features_of(None, cur, [100.0] * 20) == {}  # 无前日
    assert daily_features_of(("d", 100, 101, 99, 0, 100), cur, [100.0] * 20) == {}  # 前收非正
    assert daily_features_of(prev, cur, [0.0] * 20) == {}  # 均量非正


# ── 发射（真 emit_judgment + canned ch_writer）──


def _canned_reader(rows_map: dict[str, list[tuple]]):
    def _rd(sql: str) -> list[tuple]:
        for key, rows in rows_map.items():
            if key in sql:
                return rows
        return []

    return _rd


def test_emit_full_chain_and_12_columns(canned_emit) -> None:
    rows = _kline_rows(260)
    rd = _canned_reader({"kline_index": rows})
    day = str(rows[-1][0])
    res = dp.emit_for_trade_date(day, reader=rd, asof_ts=datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc))
    assert res.committed is True
    assert canned_emit["table"].endswith("judgment_daily_plan")
    # INSERT 列清单=schemas 真源（12 列，结算列结构性缺席——判定/结算分离）
    from schemas.categories.judgment.judgment_daily_plan import INSERT_COLUMNS

    assert canned_emit["columns"] == INSERT_COLUMNS
    # TSV 行解析对账
    line = canned_emit["tsv"].strip().split("\n")[0]
    fields = line.split("\t")
    assert len(fields) == 12
    payload = json.loads(fields[7])
    assert len(payload["scenarios"]) == 3
    priors = [s["path_prior"] for s in payload["scenarios"]]
    assert abs(sum(priors) - 1.0) < 1e-6
    for s in payload["scenarios"]:
        parse_trigger(s["trigger"])  # 落库 trigger 必过文法（可测量表达式铁律）
    # inputs_ref 首键=plan_date（幂等格式——P2a 首键事故同款修法）；列序=INSERT 清单
    # (judgment_id, module_id, model_version, asof_ts, input_cutoff_ts, horizon, subject,
    #  payload, confidence, inputs_ref, run_id, synthetic)
    assert fields[9].startswith(f"plan_date:{day}|")
    assert fields[10] == f"daily-plan:{day}"
    assert fields[11] == "0"


def test_emit_confidence_missing_inputs_degrade(canned_emit) -> None:
    rows = _kline_rows(260)
    rd = _canned_reader({"kline_index": rows})  # 可选输入全缺
    day = str(rows[-1][0])
    dp.emit_for_trade_date(day, reader=rd, asof_ts=datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc))
    payload = json.loads(canned_emit["tsv"].strip().split("\n")[0].split("\t")[7])
    assert "next_day_forecast" in payload["evidence"]["missing_inputs"]
    assert any("absent" in s for s in payload["inputs_scope"])


def test_inputs_hash_deterministic() -> None:
    row = ("2026-01-02", 101.0, 102.0, 100.5, 101.5, 150.0)
    prior = {"S1_attack": 0.4, "S2_defense": 0.3, "S3_oscillation": 0.3}
    h1 = inputs_hash_of("2026-01-02", row, prior, 50, "abc")
    h2 = inputs_hash_of("2026-01-02", row, prior, 50, "abc")
    h3 = inputs_hash_of("2026-01-02", row, prior, 51, "abc")
    assert h1 == h2 and h1 != h3 and len(h1) == 16


def test_emit_g_day_missing_fail_closed(canned_emit) -> None:
    rows = _kline_rows(260)
    rd = _canned_reader({"kline_index": rows})
    with pytest.raises(ValueError, match="不在库"):
        dp.emit_for_trade_date("2099-01-01", reader=rd)


# ── 幂等与唤醒点 ─--


def _patch_resolve(monkeypatch, day: str) -> None:
    """钩子内 `from pipeline_events import resolve_pf_alloc_trade_date` 的确定性注入点。"""
    import zephyr.strategy_pipeline.pipeline_events as pe

    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: day, raising=False)


def test_hook_wake_filter(monkeypatch) -> None:
    assert maybe_emit_daily_plan(task_id="kline_etf_60min_incremental")["action"] == "skipped_wake_point"
    assert maybe_emit_daily_plan(task_id="daily_kline", success=False)["action"] == "skipped_wake_point"


def test_hook_already_emitted_zero_side_effect(monkeypatch) -> None:
    called = {"n": 0}

    def _boom(*a, **k):
        called["n"] += 1
        raise AssertionError("已发射后不得再 emit")

    monkeypatch.setattr(dp, "emit_for_trade_date", _boom)
    monkeypatch.setattr(dp, "_reader_execute",
                        lambda sql: [(1,)] if "count()" in sql else [])
    _patch_resolve(monkeypatch, "2026-09-16")
    out = maybe_emit_daily_plan(task_id="daily_kline_incremental", success=True)
    assert out["action"] == "already_emitted"
    assert out["plan_date"] == "2026-09-16"
    assert called["n"] == 0


def test_hook_resolve_day(monkeypatch) -> None:
    monkeypatch.setattr(dp, "_reader_execute",
                        lambda sql: [(0,)] if "count()" in sql else [])
    _patch_resolve(monkeypatch, "2026-09-16")
    out = maybe_emit_daily_plan(task_id="daily_kline_incremental", success=True)
    assert out["action"] == "data_insufficient"
    assert out["plan_date"] == "2026-09-16"


def test_hook_error_swallowed_never_throws(monkeypatch) -> None:
    def _boom(*a, **k):
        raise RuntimeError("ch down")

    monkeypatch.setattr(dp, "_reader_execute", _boom)
    _patch_resolve(monkeypatch, "2026-09-16")
    out = maybe_emit_daily_plan(task_id="daily_kline_incremental", success=True)
    assert out["action"] in ("error", "data_insufficient")


# ── 与 P1 结算器联测（发射行 → _settle_daily_plan 纯函数）──--


def _settler_row(judgment_id: str, payload: dict, asof_day: str) -> dict[str, Any]:
    return {
        "judgment_id": judgment_id, "module_id": dp.MODULE_ID, "model_version": dp.MODEL_VERSION,
        "asof_ts": f"{asof_day} 07:05:00.000", "subject": dp.SUBJECT,
        "payload": json.dumps(payload, ensure_ascii=False), "confidence": 0.5,
    }


def test_settler_joint_verification_missing_grace() -> None:
    """P1 宽限期惯例：当日（asof≥latest）无验证=not_matured；隔日=unresolvable。"""
    payload = {"scenarios": build_v0_scenarios()}
    for s in payload["scenarios"]:
        s["path_prior"] = round(1.0 / 3, 6)
    row = _settler_row("J1", payload, "2026-09-16")
    bf, res, perm = js._settle_daily_plan(row, {}, "2026-09-16")
    assert res.action == "not_matured" and perm is False
    bf, res, perm = js._settle_daily_plan(row, {}, "2026-09-17")
    assert res.action == "unresolvable" and res.reason == "verification_missing"


def test_settler_joint_brier_handcheck() -> None:
    scs = build_v0_scenarios()
    for i, s in enumerate(scs):
        s["path_prior"] = [0.5, 0.3, 0.2][i]
    payload = {"scenarios": scs}
    ver = {"actual_scenario_id": "S2_defense", "plan_followed": 0,
           "scenario_hits": json.dumps([{"scenario_id": "S2_defense",
                                         "trigger_ts": "2026-09-17 10:30:00.000",
                                         "trigger_price": 4000.0}])}
    row = _settler_row("J2", payload, "2026-09-16")
    bf, res, perm = js._settle_daily_plan(row, {"J2": ver}, "2026-09-17")
    assert res.action == "settled" and bf["actual_scenario_id"] == "S2_defense"
    # 多分类 Brier 手算：one-hot(S2)=(0,1,0)，Σ(p_i-y_i)²=0.25+0.49+0.04=0.78
    assert bf["scenario_brier"] == pytest.approx(0.78)
    assert json.loads(bf["outcome_value"])["hit"] is False  # argmax=S1≠S2


def test_no_scenario_sentinel_settler_unresolvable() -> None:
    """红蓝口径：无场景日 actual=no_scenario → 结算侧 unresolvable(actual_scenario_unknown)
    =预案覆盖缺口如实可见（禁硬凑全覆盖的既定口径）。"""
    payload = {"scenarios": build_v0_scenarios()}
    for s in payload["scenarios"]:
        s["path_prior"] = round(1.0 / 3, 6)
    row = _settler_row("J3", payload, "2026-09-16")
    ver = {"actual_scenario_id": NO_SCENARIO, "plan_followed": 0, "scenario_hits": "[]"}
    bf, res, perm = js._settle_daily_plan(row, {"J3": ver}, "2026-09-17")
    assert res.action == "unresolvable" and res.reason == "actual_scenario_unknown"


def test_hook_emitted_end_to_end(monkeypatch, canned_emit) -> None:
    """钩子全链：daily_kline 唤醒 → 查重 0 → 发射（canned CH）→ emitted。"""
    rows = _kline_rows(260)
    day = str(rows[-1][0])

    def _rd(sql: str) -> list[tuple]:
        if "count()" in sql:
            return [(0,)]
        if "kline_index" in sql:
            return rows
        return []

    monkeypatch.setattr(dp, "_reader_execute", _rd)
    import zephyr.strategy_pipeline.pipeline_events as pe

    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: day, raising=False)
    out = maybe_emit_daily_plan(task_id="kline_daily_incremental", success=True)
    assert out["action"] == "emitted" and out["plan_date"] == day
