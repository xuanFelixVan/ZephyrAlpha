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


# ── 表名 SSoT 注册闭环守卫（2026-09-18 判定链注册迁移 st-ff-judgment-20260918）──
# 病根：判定四表 DDL-as-Code 真源 2026-09-16 即建，但品类条目从未登记
# business_data_categories.yaml → get_registry().table() 查不到 = 判定链没有表名真源，
# 消费方只能硬编码字面量，且 TABLE-NAME-REGISTRY 门（按"已注册表名"匹配 added 行）
# 对本族结构性失明——改表即断链且无人知晓。本组测试机械钉死三向一致，把"无人知晓"
# 变成"CI 红"。

_JUDGMENT_REGISTRY_CATEGORIES = (
    "judgment_intraday_market_state",
    "judgment_next_day_forecast",
    "judgment_daily_plan",
    "judgment_plan_verification",
)


@pytest.mark.parametrize("category_id", _JUDGMENT_REGISTRY_CATEGORIES)
def test_judgment_tables_registered_in_category_yaml(category_id: str) -> None:
    """四表品类 MUST 在 TableRegistry 可见（缺席=判定链表名无真源，本测即红）。"""
    from zephyr.data.table_registry import get_registry

    full = get_registry().table(category_id)  # 未注册 → KeyError fail-closed
    db, _, tbl = full.partition(".")
    assert db == "c1_market"
    assert tbl == category_id  # category_id==table 名（判定族自带前缀，不另造第二命名）


def test_judgment_derived_names_match_ddl_truth() -> None:
    """三向一致：TableRegistry 派生名 == 库件常量 == schemas DDL 真源 TABLE_NAME。"""
    import importlib

    derived = {**jl.JUDGMENT_TABLES, "plan_verification": jl.VERIFICATION_TABLE}
    assert set(derived) == {
        "intraday_market_state", "next_day_forecast", "daily_plan", "plan_verification",
    }
    registry_tables = {f"c1_market.{c}" for c in _JUDGMENT_REGISTRY_CATEGORIES}
    assert set(derived.values()) == registry_tables  # 库件无第二真源
    for key, full in derived.items():
        schema = importlib.import_module(f"schemas.categories.judgment.judgment_{key}")
        assert full == f"c1_market.{schema.TABLE_NAME}"


def test_missing_judgment_category_fails_closed() -> None:
    """能红证据：品类缺席时 table() MUST 抛 KeyError（绝不静默编表名）。"""
    from zephyr.data.table_registry import TableRegistry

    with pytest.raises(KeyError):
        TableRegistry(categories=[]).table("judgment_daily_plan")


# ══════════════════════ 判定发射钩子 merge 守卫（R-002 同原则治本）══════════════════════════
#
# 死信 q-20260918-st-ff-judgment-20260918-0001：daily_plan.maybe_emit_daily_plan 与
# next_day_forecaster.maybe_emit_next_day_forecast 被 CloneGuard 判 100% extract 级克隆
# （reDUP 组 06c56c3a9d5495e5，两份都在 HEAD，本批改表名派生即触出）。处置=merge：
# 骨架单点于 judgment_ledger.run_judgment_emit_hook，公开入口由 make_judgment_emit_hook
# 生成。本组测试钉住"改造前后发出的记录逐字段一致"——金样本取自 **merge 之前**的工作树
# 实测（.runtime/tmp/st-ff-judgment2-20260918/golden_pre_merge.json，16 例字节全等）。

_HOOK_DAY: str = "2026-09-16"
_HOOK_OK: str = "J-GOLDEN-1"
_HOOK_NOTCOMMITTED: str = "J-GOLDEN-2"


def _hook_legs() -> list[dict[str, Any]]:
    """两条腿的表侧参数（值全部来自真源派生，禁在测试里另编表名字面量）。"""
    from zephyr.plan_engine import daily_plan as dp
    from zephyr.plan_engine import next_day_forecaster as nf

    return [
        {"entry": dp.maybe_emit_daily_plan, "module": dp, "mid": dp.MODULE_ID,
         "table": jl.JUDGMENT_TABLES["daily_plan"], "key": "plan_date"},
        {"entry": nf.maybe_emit_next_day_forecast, "module": nf, "mid": nf.MODULE_ID,
         "table": jl.JUDGMENT_TABLES["next_day_forecast"], "key": "trade_date"},
    ]


def _hook_branches() -> list[tuple[str, list[tuple], Any, str, bool, list[tuple[str, Any]], int]]:
    """八条分支：(名称, reader 返回, emit 抛出的异常, task_id, success, 期望有序键值, 期望查询次数)。

    期望序列里的 "@date_key"/"" 是腿侧键名占位（P2b=plan_date、P2a=trade_date）——
    顺序即改造前实测顺序（金样本），emit_not_committed 的 disposition 在业务日**之前**。
    """
    return [
        ("wrong_wake_point", [], None, "kline_etf_60min_incremental", True,
         [("action", "skipped_wake_point")], 0),
        ("task_failed", [], None, "daily_kline", False,
         [("action", "skipped_wake_point")], 0),
        ("already_emitted", [(1,)], None, "daily_kline_incremental", True,
         [("action", "already_emitted"), ("@date_key", "@day")], 1),
        ("emitted", [(0,)], None, "daily_kline_incremental", True,
         [("action", "emitted"), ("@date_key", "@day"), ("judgment_id", _HOOK_OK)], 1),
        ("emit_not_committed", [(0,)], None, "daily_kline_incremental", True,
         [("action", "emit_not_committed"), ("disposition", "local_durable"),
          ("@date_key", "@day"), ("judgment_id", _HOOK_NOTCOMMITTED)], 1),
        ("data_insufficient", [(0,)], ValueError("T 日线未齐"), "daily_kline_incremental", True,
         [("action", "data_insufficient"), ("@date_key", "@day"), ("reason", "T 日线未齐")], 1),
        ("emit_raises_error", [], RuntimeError("ch down"), "daily_kline_incremental", True,
         [("action", "error"), ("@date_key", "@day"), ("error", "RuntimeError: ch down")], 1),
        ("resolve_raises_error", [], None, "daily_kline_incremental", True,
         [("action", "error"), ("@date_key", ""), ("error", "RuntimeError: resolve boom")], 0),
    ]


@pytest.mark.parametrize("leg_idx", [0, 1])
@pytest.mark.parametrize(
    "branch,rows,raises,task_id,success,expected,n_sql",
    _hook_branches(),
)
def test_emit_hook_golden_matches_pre_merge(
    monkeypatch: pytest.MonkeyPatch, leg_idx: int, branch: str, rows: list[tuple],
    raises: BaseException | None, task_id: str, success: bool,
    expected: list[tuple[str, Any]], n_sql: int,
) -> None:
    """金样本比对：merge 后两腿八分支的返回记录（键+序+值）与改造前逐字段一致。"""
    import zephyr.strategy_pipeline.pipeline_events as pe

    leg = _hook_legs()[leg_idx]
    seen: dict[str, Any] = {"sqls": [], "days": []}

    def _reader(sql: str) -> list[tuple]:
        seen["sqls"].append(sql)
        return rows

    def _emit(day: str) -> jl.EmitResult:
        seen["days"].append(day)
        if raises is not None:
            raise raises
        jid = _HOOK_OK if branch != "emit_not_committed" else _HOOK_NOTCOMMITTED
        committed = branch != "emit_not_committed"
        return jl.EmitResult(judgment_id=jid, table=leg["table"], committed=committed,
                             disposition="ch_committed" if committed else "local_durable")

    def _resolve() -> str:
        if branch == "resolve_raises_error":
            raise RuntimeError("resolve boom")
        return _HOOK_DAY

    monkeypatch.setattr(leg["module"], "_reader_execute", _reader)
    monkeypatch.setattr(leg["module"], "emit_for_trade_date", _emit)
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", _resolve, raising=False)

    out = leg["entry"](task_id=task_id, success=success)

    date_key = leg["key"]
    want = [(date_key if k == "@date_key" else k,
             (_HOOK_DAY if k == "@date_key" and v == "@day" else v)) for k, v in expected]
    assert list(out.items()) == want  # 键名/键序/值三项全钉（消费方可见面）
    assert len(seen["sqls"]) == n_sql
    assert seen["days"] == ([_HOOK_DAY] if branch in {
        "emitted", "emit_not_committed", "data_insufficient", "emit_raises_error"} else [])
    for sql in seen["sqls"]:
        assert sql == (
            "SELECT count() FROM {t} WHERE module_id = '{m}' AND inputs_ref LIKE '%{k}:{d}|%'"
        ).format(t=leg["table"], m=leg["mid"], k=date_key, d=_HOOK_DAY)


def test_emit_hook_entries_are_single_sourced() -> None:
    """反回退钉：两条公开入口的执行体 MUST 同源于 judgment_ledger，两模块内 MUST 无第二实现。

    合并前两份 25 行骨架逐行重复（reDUP 判 1.0 extract 级）；任何把骨架再抄回模块内的
    "revert 式修复" 都会被本测红。
    """
    import ast
    import inspect
    import os
    from pathlib import Path

    legs = _hook_legs()
    files = {inspect.getsourcefile(leg["entry"]) for leg in legs}
    assert len(files) == 1, f"两腿入口源码文件必须唯一，实测 {files}"
    skeleton = os.path.normpath(next(iter(files)))
    assert skeleton.endswith(os.path.join("zephyr", "plan_engine", "judgment_ledger.py"))
    for leg in legs:
        mod_file = os.path.normpath(str(leg["module"].__file__))
        tree = ast.parse(Path(mod_file).read_text(encoding="utf-8"))
        dup = [n.name for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name.startswith("maybe_emit_")]
        assert not dup, f"{leg['module'].__name__} 内又出现本地实现 {dup}——骨架必须单点"
