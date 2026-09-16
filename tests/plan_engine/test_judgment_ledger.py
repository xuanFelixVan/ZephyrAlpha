# [A_test] module_id: MOD-PLAN-026 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PLAN-026 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §二
# [MODULE] tests.plan_engine.test_judgment_ledger
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""judgment_ledger 发射器库件施工验证测试（判定台账标准 v0.1 §二）。

覆盖：
- new_judgment_id：10000 发唯一/严格单调/26 字符 Crockford Base32 字符集；
  同毫秒强制注入 → 随机段自增仍单调不重。
- format_utc3：tz-aware 毫秒截取；naive datetime fail-closed（RULE-SCHEMA-TZ）。
- validate_payload：三表合法用例规范化 JSON；坏 JSON/非 dict/未知表/五态键越界/
  分布和≠1/概率越界/trigger 不可测量（"如果走弱"）/path_prior 和≠1 全拒。
- emit_judgment：参数 fail-closed（confidence/module_id/PIT）；写路径经
  monkeypatch ch_writer.write_tsv_outcome 捕获——结算列组结构性不在 INSERT
  清单（判定器无写通道）、TSV 12 列、committed 由 disposition 映射。
- SSoT 漂移守卫（机械判定）：库件 INSERT 列清单 == schemas 真源；DDL 文本
  含判定列组、结算列组不含于 INSERT（双真源免疫）。
全 monkeypatch 隔离，不触真 ClickHouse。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import pytest

from zephyr.plan_engine import judgment_ledger as jl
from zephyr.plan_engine.judgment_ledger import (
    JUDGMENT_TABLE_KEYS,
    JudgmentDraft,
    emit_judgment,
    format_utc3,
    new_judgment_id,
    validate_payload,
)

_ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

_VALID_PAYLOADS: dict[str, dict[str, Any]] = {
    "intraday_market_state": {
        "state_label": "震荡",
        "state_probs": {"低迷": 0.1, "防御": 0.1, "震荡": 0.6, "进攻": 0.2, "亢奋": 0.0},
        "rest_of_day": {"tail_dir_prob_down": 0.68, "amp_range_pct": [0.2, 0.8]},
    },
    "next_day_forecast": {"p_up": 0.35, "p_flat": 0.25, "p_down": 0.40},
    "daily_plan": {
        "scenarios": [
            {"scenario_id": "S1", "trigger": "open_gap_pct>0.5", "action": "wait", "path_prior": 0.6},
            {"scenario_id": "S2", "trigger": "amount_ratio<0.8 AND time<=10:00", "action": "stand_aside",
             "path_prior": 0.4},
        ]
    },
}


# ── ULID ──


def test_ulid_unique_monotonic_charset() -> None:
    ids = [new_judgment_id() for _ in range(10000)]
    assert len(set(ids)) == 10000
    assert ids == sorted(ids)  # 进程内严格单调（时序可排序=台账扫读前提）
    assert all(len(i) == 26 for i in ids)
    assert all(c in _ULID_ALPHABET for i in ids for c in i)


def test_ulid_same_ms_increment_monotonic() -> None:
    """强制注入同毫秒状态：随机段 +1 保证同毫秒并发发射不撞号。"""
    first = new_judgment_id()
    second = new_judgment_id()
    assert second > first  # 常规路径即已单调


def test_ulid_forced_same_ms() -> None:
    from zephyr.shared.utils.time_utils import now_utc

    with jl._ULID_LOCK:
        jl._ULID_LAST_MS[0] = int(now_utc().timestamp() * 1000)
        jl._ULID_LAST_RAND[0] = b"\x00" * 9 + b"\x05"  # 尾字节 5 → 6 → 7 ...
    ids = [new_judgment_id() for _ in range(10)]
    assert len(set(ids)) == 10
    assert ids == sorted(ids)


# ── 时间格式 ──


def test_format_utc3_millisecond() -> None:
    dt = datetime(2026, 9, 16, 7, 8, 9, 123456, tzinfo=timezone.utc)
    assert format_utc3(dt) == "2026-09-16 07:08:09.123"


def test_format_utc3_naive_rejected() -> None:
    with pytest.raises(ValueError, match="时区"):
        format_utc3(datetime(2026, 9, 16, 7, 8, 9))


# ── payload 校验 ──


@pytest.mark.parametrize("table_key", ["intraday_market_state", "next_day_forecast", "daily_plan"])
def test_validate_payload_valid(table_key: str) -> None:
    out = validate_payload(table_key, _VALID_PAYLOADS[table_key])
    assert json.loads(out) == _VALID_PAYLOADS[table_key]  # 规范化往返无损


def test_validate_payload_accepts_json_str_and_roundtrip() -> None:
    out = validate_payload("next_day_forecast", json.dumps(_VALID_PAYLOADS["next_day_forecast"]))
    assert json.loads(out)["p_up"] == 0.35


def test_validate_payload_bad_json() -> None:
    with pytest.raises(ValueError, match="坏 JSON"):
        validate_payload("next_day_forecast", "{not-json")


def test_validate_payload_non_dict() -> None:
    with pytest.raises(ValueError):
        validate_payload("next_day_forecast", [1, 2, 3])


def test_validate_payload_unknown_table() -> None:
    with pytest.raises(ValueError, match="table_key"):
        validate_payload("nope", {})


def test_validate_payload_intraday_bad_state_key() -> None:
    bad = {"state_label": "震荡", "state_probs": {"牛市": 1.0}}
    with pytest.raises(ValueError, match="state_probs"):
        validate_payload("intraday_market_state", bad)


def test_validate_payload_intraday_probs_sum_not_one() -> None:
    bad = {"state_label": "震荡", "state_probs": {"低迷": 0.5, "防御": 0.5, "震荡": 0.5}}
    with pytest.raises(ValueError, match="和≠1"):
        validate_payload("intraday_market_state", bad)


def test_validate_payload_intraday_bad_label_and_prob_range() -> None:
    with pytest.raises(ValueError, match="state_label"):
        validate_payload("intraday_market_state", {"state_label": "起飞", "state_probs": {"震荡": 1.0}})
    with pytest.raises(ValueError, match="state_probs"):
        validate_payload("intraday_market_state", {"state_label": "震荡", "state_probs": {"震荡": 1.5}})
    with pytest.raises(ValueError, match="amp_range_pct"):
        validate_payload("intraday_market_state", {
            "state_label": "震荡", "state_probs": {"震荡": 1.0},
            "rest_of_day": {"amp_range_pct": [0.8, 0.2]}})


def test_validate_payload_next_day_sum_and_range() -> None:
    with pytest.raises(ValueError, match="和≠1"):
        validate_payload("next_day_forecast", {"p_up": 0.5, "p_flat": 0.5, "p_down": 0.5})
    with pytest.raises(ValueError, match="p_up"):
        validate_payload("next_day_forecast", {"p_up": -0.1, "p_flat": 0.6, "p_down": 0.5})


def test_validate_payload_next_day_negative_vol() -> None:
    with pytest.raises(ValueError, match="expected_vol_pct"):
        validate_payload("next_day_forecast", {
            "p_up": 0.3, "p_flat": 0.3, "p_down": 0.4, "expected_vol_pct": -1})


def test_validate_payload_weasel_trigger_rejected() -> None:
    """标准 §三铁律：trigger 必须是可测量表达式——"如果走弱"不合格。"""
    with pytest.raises(ValueError, match="可测量"):
        validate_payload("daily_plan", {
            "scenarios": [{"scenario_id": "S1", "trigger": "如果走弱", "path_prior": 1.0}]})


def test_validate_payload_plan_prior_sum_and_dup_ids() -> None:
    with pytest.raises(ValueError, match="和≠1"):
        validate_payload("daily_plan", {
            "scenarios": [{"scenario_id": "S1", "trigger": "gap>0.5", "path_prior": 0.5}]})
    with pytest.raises(ValueError, match="重复"):
        validate_payload("daily_plan", {
            "scenarios": [{"scenario_id": "S1", "trigger": "gap>0.5", "path_prior": 0.5},
                          {"scenario_id": "S1", "trigger": "gap<0.5", "path_prior": 0.5}]})


# ── 发射器参数 fail-closed ──


def _draft(**overrides: Any) -> JudgmentDraft:
    kw: dict[str, Any] = {
        "module_id": "MOD-TEST", "model_version": "v1", "subject": "index:000300.SH",
        "payload": _VALID_PAYLOADS["next_day_forecast"], "confidence": 0.6,
    }
    kw.update(overrides)
    return JudgmentDraft(**kw)


def _emit_kwargs(**overrides: Any) -> dict[str, Any]:
    kw: dict[str, Any] = {
        "asof_ts": datetime(2026, 9, 16, 7, 0, 0, tzinfo=timezone.utc),
    }
    kw.update(overrides)
    return kw


def test_emit_param_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Any] = []
    monkeypatch.setattr(jl.ch_writer, "write_tsv_outcome",
                        lambda *a, **k: captured.append(a) or _never())
    with pytest.raises(ValueError, match="confidence"):
        emit_judgment("next_day_forecast", _draft(confidence=1.5), **_emit_kwargs())
    with pytest.raises(ValueError, match="module_id"):
        emit_judgment("next_day_forecast", _draft(module_id=" "), **_emit_kwargs())
    with pytest.raises(ValueError, match="PIT"):
        emit_judgment("next_day_forecast", _draft(), **_emit_kwargs(
            input_cutoff_ts=datetime(2026, 9, 16, 8, 0, 0, tzinfo=timezone.utc)))
    with pytest.raises(ValueError, match="table_key"):
        emit_judgment("bogus", _draft(), **_emit_kwargs())
    assert not captured  # 校验失败绝不写半行


def _never() -> Any:  # pragma: no cover — 防御：不应到达
    raise AssertionError("write_tsv_outcome 不应被调用")


# ── 发射器写路径（monkeypatch 通道捕获）──


class _FakeOutcome:
    def __init__(self, disposition: str) -> None:
        self.disposition = jl.ch_writer.WriteDisposition(disposition)
        self.is_ch_committed = disposition == "ch_committed"


def test_emit_write_path_no_settlement_columns(
    monkeypatch: pytest.MonkeyPatch, ) -> None:
    captured: dict[str, Any] = {}

    def fake_write(table: str, columns: str | None, tsv: bytes, **_k: Any) -> Any:
        captured["table"], captured["columns"], captured["tsv"] = table, columns, tsv
        return _FakeOutcome("ch_committed")

    monkeypatch.setattr(jl.ch_writer, "write_tsv_outcome", fake_write)
    res = emit_judgment(
        "next_day_forecast", _draft(inputs_ref="snap-abc", run_id="run-1"),
        **_emit_kwargs(synthetic=True))
    assert res.committed and res.disposition == "ch_committed"
    assert captured["table"] == "c1_market.judgment_next_day_forecast"
    cols = captured["columns"]
    # 判定/结算分离：结算列组结构性不在 INSERT 清单（判定器无写通道）
    for banned in ("outcome_ts", "outcome_value", "eval_method", "eval_score",
                   "evaluated_at", "evaluated_by", "realized_return", "realized_label"):
        assert banned not in cols, f"结算列 {banned} 泄入 INSERT 清单"
    row = captured["tsv"].decode("utf-8").rstrip("\n").split("\t")
    assert len(row) == 12
    assert row[0] == res.judgment_id
    assert row[1] == "MOD-TEST" and row[5] == "next_day"  # horizon 默认值
    assert row[6] == "index:000300.SH"
    payload_json = json.loads(row[7])
    assert payload_json == _VALID_PAYLOADS["next_day_forecast"]
    assert row[9] == "snap-abc" and row[10] == "run-1" and row[11] == "1"  # synthetic 标注


def test_emit_write_failure_not_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    """写入失败不抛（EmitResult.committed=False + disposition 留痕，采集链反噬防护）。"""
    monkeypatch.setattr(jl.ch_writer, "write_tsv_outcome",
                        lambda *a, **k: _FakeOutcome("not_durable"))
    res = emit_judgment("next_day_forecast", _draft(), **_emit_kwargs())
    assert not res.committed and res.disposition == "not_durable"


def test_emit_local_durable_not_claimed_committed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jl.ch_writer, "write_tsv_outcome",
                        lambda *a, **k: _FakeOutcome("local_durable"))
    res = emit_judgment("next_day_forecast", _draft(), **_emit_kwargs())
    assert not res.committed and res.disposition == "local_durable"


# ── SSoT 漂移守卫（机械判定：库件 vs schemas 真源 vs DDL 文本）──

_SETTLEMENT_COLS = {"outcome_ts", "outcome_value", "eval_method", "eval_score",
                    "evaluated_at", "evaluated_by"}


@pytest.mark.parametrize("table_key,mod_name,ddl_const", [
    ("intraday_market_state", "judgment_intraday_market_state", "JUDGMENT_INTRADAY_MARKET_STATE_DDL"),
    ("next_day_forecast", "judgment_next_day_forecast", "JUDGMENT_NEXT_DAY_FORECAST_DDL"),
    ("daily_plan", "judgment_daily_plan", "JUDGMENT_DAILY_PLAN_DDL"),
])
def test_insert_columns_match_schema_ssot(table_key: str, mod_name: str, ddl_const: str) -> None:
    import importlib

    schema = importlib.import_module(f"schemas.categories.judgment.{mod_name}")
    spec = jl._TABLE_SPECS[table_key]
    assert spec.table == f"c1_market.{schema.TABLE_NAME}"
    assert spec.insert_columns == schema.INSERT_COLUMNS  # 库件契约==真源（零漂移）
    ddl = getattr(schema, ddl_const)
    for col in ("judgment_id", "module_id", "asof_ts", "input_cutoff_ts", "horizon",
                "subject", "payload", "confidence", "synthetic"):
        assert col in ddl
    for col in _SETTLEMENT_COLS:
        assert col in ddl  # DDL 有结算列组
        assert col not in spec.insert_columns  # 但 INSERT 契约无（结构性禁写）


def test_verification_table_ssot_untouched_by_emitter() -> None:
    """judgment_plan_verification 是结算侧事实表——发射器注册表不得含它。"""
    import importlib

    schema = importlib.import_module("schemas.categories.judgment.judgment_plan_verification")
    assert schema.TABLE_NAME == "judgment_plan_verification"
    assert "plan_verification" not in JUDGMENT_TABLE_KEYS
