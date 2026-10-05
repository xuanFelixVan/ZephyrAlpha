# [MODULE] tests.zephyr.data.test_cleaning_rules_hosting
# [DOMAIN] D_DATA
"""清洗规则引擎托管腿测试（R-M1-06 接线反证三件）。

判"已防护"的标准（本役反"装饰性护栏"口径，90 波实证册 §三）：
  ①谁调它 —— test_wired_into_supply_sentinel_leg / test_host_leg_delegates_to_real_gate
  ②能否改变行为 —— test_red_changing_yaml_threshold_changes_behavior（改 YAML 即改判定，
    判据值不在代码里）
  ③故障时是否 fail-closed —— test_red_missing_yaml_* / test_unparseable_yaml_* / 参数化畸形案
"""
# [TTL] permanent
# [STARTUP] manual

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.data import cleaning_rules_hosting as crh
from zephyr.data.cleaning_rules_hosting import (
    CleaningGateConfigError,
    load_rulebook,
    run_cleaning_gate,
    run_hosted_cleaning_gate,
)

REF = date(2026, 9, 26)
TABLE = "c1_market.daily_valuation"


class FakeExecutor:
    """CH 只读假执行器：按 SELECT 列面回行（测试禁触生产库，宪法 §9.1/§9.6）。"""

    def __init__(self, rows: list[dict[str, Any]], *, fail: bool = False) -> None:
        self._rows = rows
        self._fail = fail
        self.queries: list[str] = []

    def execute(self, sql: str) -> list:
        self.queries.append(sql)
        if self._fail:
            raise RuntimeError("CH 不可达（测试注入）")
        cols = sql.split(" FROM ")[0].replace("SELECT ", "", 1).split(", ")
        return [[row.get(col) for col in cols] for row in self._rows]


class RecordingAlerter:
    """告警假通道（禁写生产 data/ 告警目录）。"""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def notify(
        self, task_id: str, error: str, level: str = "ERROR", source: str | None = None, extra: dict | None = None
    ) -> bool:
        self.messages.append((level, error))
        return True


def write_carrier(tmp_path: Path, **overrides: Any) -> Path:
    """生成承载册 fixture（键集与真册同构；wiring 必填项一个不漏）。"""
    wiring: dict[str, Any] = {
        "enabled": True,
        "host_schedule": "data_supply_sentinel",
        "cadence_days": 7,
        "read_limit_rows": 500,
        "alert_level": "warn",
        "report_dir": str(tmp_path / "reports"),
        "disabled_flag": str(tmp_path / "cleaning_gate.disabled"),
    }
    tables: list[dict[str, Any]] = overrides.pop(
        "tables",
        [
            {
                "table": TABLE,
                "date_col": "trade_date",
                "lookback_days": 5,
                "rules": [
                    {
                        "name": "pct_in_band",
                        "field": "pct_change",
                        "op": "between",
                        "lower": -20,
                        "upper": 20,
                        "action": "flag",
                    },
                ],
            }
        ],
    )
    wiring.update(overrides.pop("wiring", {}) or {})
    doc = {"schema_version": 1, "wiring": wiring, "tables": tables}
    path = tmp_path / "cleaning_rules.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def _rows() -> list[dict[str, Any]]:
    return [
        {"trade_date": REF, "close": 10.0, "pct_change": 12.0},
        {"trade_date": REF - timedelta(days=1), "close": 11.0, "pct_change": -3.0},
    ]


# ---------------------------------------------------------------------------
# 红测①：改 YAML 能改变行为（判据值唯一真源=承载册）
# ---------------------------------------------------------------------------


def test_red_changing_yaml_threshold_changes_behavior(tmp_path: Path) -> None:
    """同一段数据、同一个执行器，只改 YAML 的 upper —— 判定结果必须跟着变。

    这条是本役反"装饰性护栏"的标准判据：YAML 自称真源而代码硬编码时，此测必红。
    """
    loose = write_carrier(tmp_path)
    executor = FakeExecutor(_rows())
    wiring, books = load_rulebook(loose)
    report = run_cleaning_gate(
        wiring, books, executor=executor, alerter=None, ref_date=REF, report_dir=tmp_path / "r1", notify=False
    )
    assert report["findings_count"] == 0, "±20% 区间内不应有命中（基线）"

    tight_doc = yaml.safe_load(loose.read_text(encoding="utf-8"))
    tight_doc["tables"][0]["rules"][0]["upper"] = 5
    tight = tmp_path / "cleaning_rules_tight.yaml"
    tight.write_text(yaml.safe_dump(tight_doc, allow_unicode=True, sort_keys=False), encoding="utf-8")

    wiring2, books2 = load_rulebook(tight)
    report2 = run_cleaning_gate(
        wiring2,
        books2,
        executor=FakeExecutor(_rows()),
        alerter=None,
        ref_date=REF,
        report_dir=tmp_path / "r2",
        notify=False,
    )
    assert report2["findings_count"] == 1, "YAML 阈值收紧后同一行必须被判违规"
    assert report2["results"][0]["stats"]["by_rule"] == {"pct_in_band": 1}


def test_red_changing_yaml_action_changes_behavior(tmp_path: Path) -> None:
    """只改 YAML 的 action（flag→block）：flagged 与 intercepted 的归属必须换边。"""
    doc = yaml.safe_load(
        write_carrier(
            tmp_path,
            tables=[
                {
                    "table": TABLE,
                    "date_col": "trade_date",
                    "lookback_days": 5,
                    "rules": [
                        {"name": "close_positive", "field": "close", "op": "gt", "value": 10.5, "action": "flag"}
                    ],
                }
            ],
        ).read_text(encoding="utf-8")
    )
    report = run_cleaning_gate(
        *load_rulebook_from(doc, tmp_path, "flag"),
        executor=FakeExecutor(_rows()),
        alerter=None,
        ref_date=REF,
        report_dir=tmp_path / "a1",
        notify=False,
    )
    assert (report["flagged_rows"], report["intercepted_rows"]) == (1, 0)

    doc["tables"][0]["rules"][0]["action"] = "block"
    blocky = tmp_path / "carrier_block.yaml"
    blocky.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    wiring, books = load_rulebook(blocky)
    report2 = run_cleaning_gate(
        wiring,
        books,
        executor=FakeExecutor(_rows()),
        alerter=None,
        ref_date=REF,
        report_dir=tmp_path / "a2",
        notify=False,
    )
    assert (report2["flagged_rows"], report2["intercepted_rows"]) == (0, 1)
    # 读侧 flag 档出厂承诺：即便 block 命中，本腿也只计数，报告须自证未改生产
    assert report2["read_side_only"] is True


def load_rulebook_from(doc: dict, tmp_path: Path, tag: str):
    path = tmp_path / f"carrier_{tag}.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return load_rulebook(path)


# ---------------------------------------------------------------------------
# 红测②：谁调它（唯一调用点=L13 data_supply_sentinel 托管腿第二段）
# ---------------------------------------------------------------------------


def test_wired_into_supply_sentinel_leg(monkeypatch: pytest.MonkeyPatch) -> None:
    """宿主 run_supply_sentinel 必须真的调用本腿（不接=又一枚"建了没接"）。"""
    from zephyr.data import supply_sentinel as ss

    calls: list[str] = []
    monkeypatch.setattr(
        ss, "check_tables", lambda: {"checked": 0, "breached": 0, "heartbeat_blind": 0, "ok": True, "blind_spots": []}
    )
    monkeypatch.setattr(ss, "_alert_breaches", lambda alerter, summary: None)
    monkeypatch.setattr(ss, "_run_hosted_quality_sweep", lambda alerter: {"ok": True})
    monkeypatch.setattr(
        ss, "_run_hosted_cleaning_gate", lambda alerter: calls.append("called") or {"ok": True, "skipped": "stub"}
    )
    # 2026-09-28 st-c9-purify：宿主新增托管第三段（cleaning_anomaly_hosting），本件测试
    # 只验清洗腿接线——异常腿必须同样打桩，否则真腿会连 CH/写生产 data/（宪法 §9.6 测试隔离）
    monkeypatch.setattr(ss, "_run_hosted_anomaly_gate", lambda alerter: {"ok": True, "skipped": "stub"})

    summary = ss.run_supply_sentinel(alerter=RecordingAlerter())
    assert calls == ["called"], "清洗门控未接到宿主排班腿=接线未成立"
    assert summary["cleaning_gate"]["ok"] is True


def test_host_leg_delegates_to_real_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    """宿主托管函数必须把实调宿主槽位名交给承载册（host 不符即配置错，防册里挂空宿主）。"""
    from zephyr.data import supply_sentinel as ss

    seen: dict[str, Any] = {}

    def fake_gate(alerter=None, *, host_schedule=None, **kwargs):
        seen["host_schedule"] = host_schedule
        return {"ok": True, "skipped": "stub"}

    monkeypatch.setattr(crh, "run_hosted_cleaning_gate", fake_gate)
    out = ss._run_hosted_cleaning_gate(RecordingAlerter())
    assert seen["host_schedule"] == "data_supply_sentinel"
    assert out["ok"] is True


def test_host_mismatch_is_config_error(tmp_path: Path) -> None:
    """承载册声明宿主 ≠ 实调宿主 → fail-closed（不许"册里挂了别的宿主"蒙混上岗）。"""
    carrier = write_carrier(tmp_path, wiring={"host_schedule": "some_other_slot"})
    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter, config_path=carrier, executor=FakeExecutor(_rows()), ref_date=REF, force=True
    )
    assert out["ok"] is False and "config_error" in out
    assert any("宿主" in msg or "host" in msg for _, msg in alerter.messages)


# ---------------------------------------------------------------------------
# 红测③：YAML 缺失/解析失败/畸形 = fail-closed（绝不静默当已覆盖）
# ---------------------------------------------------------------------------


def test_red_missing_yaml_fail_closed(tmp_path: Path) -> None:
    missing = tmp_path / "no_such_carrier.yaml"
    with pytest.raises(CleaningGateConfigError) as exc:
        load_rulebook(missing)
    assert exc.value.details["path"] == str(missing)

    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter, config_path=missing, executor=FakeExecutor(_rows()), ref_date=REF, force=True
    )
    assert out["ok"] is False, "承载册缺失绝不能回 ok=True（假绿母型）"
    assert "config_error" in out
    assert alerter.messages, "配置故障必须出声"
    assert alerter.messages[0][0] == "ERROR"


def test_red_unparseable_yaml_fail_closed(tmp_path: Path) -> None:
    broken = tmp_path / "broken.yaml"
    broken.write_text("schema_version: 1\nwiring: [unclosed\n", encoding="utf-8")
    with pytest.raises(CleaningGateConfigError) as exc:
        load_rulebook(broken)
    assert "解析失败" in str(exc.value)


def test_non_mapping_carrier_fail_closed(tmp_path: Path) -> None:
    root_list = tmp_path / "list.yaml"
    root_list.write_text("- 1\n- 2\n", encoding="utf-8")
    with pytest.raises(CleaningGateConfigError):
        load_rulebook(root_list)


def _set_in(doc: dict, dotted: str, value: Any) -> None:
    """按点路径改 fixture（'tables.0.rules' 形态）——只为造畸形册，不碰真册。"""
    parts = dotted.split(".")
    node: Any = doc
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    key = parts[-1]
    if isinstance(node, list):
        node[int(key)] = value
    else:
        node[key] = value


@pytest.mark.parametrize(
    "dotted,value,needle",
    [
        # 未知键：拼错一个阈值名会让该检查静默空转却看起来在岗
        ("wiring.cadence_dayz", 7, "未知键"),
        ("tables.0.lookbak_days", 5, "未知键"),
        # 必填缺失：无默认判据兜底
        ("wiring.cadence_days", None, "缺必填键"),
        # 非法值：0/负=静默空转（比报错更危险）
        ("wiring.cadence_days", 0, ">=1"),
        ("wiring.read_limit_rows", -1, ">=1"),
        ("tables.0.lookback_days", 0, ">=1"),
        ("wiring.alert_level", "silent", "alert_level 非法"),
        # 表清单/规则清单为空 = 有接线无对象（假覆盖形态）
        ("tables", [], "tables 为空"),
        ("tables.0.rules", [], "rules 为空"),
        # 非法 op（DSL 校验前移到加载期）
        ("tables.0.rules.0.op", "approx", "DSL 非法"),
        # 标识符白名单：YAML 值不得当 SQL 片段
        ("tables.0.table", "c1_market.t; DROP TABLE x", "标识符"),
        ("tables.0.rules.0.field", "1=1", "标识符"),
        # schema_version 漂移
        ("schema_version", 2, "schema_version"),
    ],
)
def test_malformed_carrier_fail_closed(tmp_path: Path, dotted: str, value: Any, needle: str) -> None:
    carrier = write_carrier(tmp_path)
    doc = yaml.safe_load(carrier.read_text(encoding="utf-8"))
    if dotted == "wiring.cadence_days" and value is None:
        doc["wiring"].pop("cadence_days")
    else:
        _set_in(doc, dotted, value)
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    with pytest.raises(CleaningGateConfigError) as exc:
        load_rulebook(bad)
    text = str(exc.value) + str(getattr(exc.value, "details", {}))
    assert needle in text, f"{dotted}={value!r} 应判 [{needle}]，实得 [{text}]"


def test_bool_poisoning_rejected(tmp_path: Path) -> None:
    """true 被 int() 吞成 1 = 最严档被静默放宽，必须炸（quality_sentinel 同族口径）。"""
    carrier = write_carrier(tmp_path)
    doc = yaml.safe_load(carrier.read_text(encoding="utf-8"))
    doc["wiring"]["cadence_days"] = True
    bad = tmp_path / "bool.yaml"
    bad.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    with pytest.raises(CleaningGateConfigError):
        load_rulebook(bad)


# ---------------------------------------------------------------------------
# 读侧承诺与降级纪律
# ---------------------------------------------------------------------------


def test_leg_only_reads(tmp_path: Path) -> None:
    carrier = write_carrier(tmp_path)
    executor = FakeExecutor(_rows())
    wiring, books = load_rulebook(carrier)
    run_cleaning_gate(
        wiring, books, executor=executor, alerter=None, ref_date=REF, report_dir=tmp_path / "r", notify=False
    )
    assert len(executor.queries) == 1
    for sql in executor.queries:
        assert sql.lstrip().upper().startswith("SELECT"), "本腿只读，禁 INSERT/DELETE/DROP"
        assert "LIMIT 500" in sql, "行数上限须来自承载册 wiring.read_limit_rows"
        assert "BETWEEN toDate('2026-09-22') AND toDate('2026-09-26')" in sql, "窗口须来自 lookback_days"


def test_all_degraded_never_reports_clean(tmp_path: Path) -> None:
    carrier = write_carrier(tmp_path)
    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter,
        config_path=carrier,
        executor=FakeExecutor([], fail=True),
        report_dir=tmp_path / "r",
        ref_date=REF,
        force=True,
    )
    assert out["ok"] is False and out["all_degraded"] is True
    assert any("未生效" in msg or "取数失败" in msg for _, msg in alerter.messages)


def test_findings_alert_at_yaml_level(tmp_path: Path) -> None:
    """命中时按 YAML 的 alert_level 出声（级别真源也在册，不在代码）。"""
    doc = yaml.safe_load(write_carrier(tmp_path).read_text(encoding="utf-8"))
    doc["tables"][0]["rules"][0]["upper"] = 1
    doc["wiring"]["alert_level"] = "error"
    carrier = tmp_path / "loud.yaml"
    carrier.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter,
        config_path=carrier,
        executor=FakeExecutor(_rows()),
        report_dir=tmp_path / "r",
        ref_date=REF,
        force=True,
    )
    assert out["ok"] is False and out["findings_count"] == 1
    assert alerter.messages and alerter.messages[0][0] == "ERROR"


def test_cadence_and_switch_gates(tmp_path: Path) -> None:
    """节奏闸（报告文件名即状态真源）与停用标记各挡一次，且都报 skipped 不报假绿。"""
    carrier = write_carrier(tmp_path)
    first = run_hosted_cleaning_gate(
        RecordingAlerter(),
        config_path=carrier,
        executor=FakeExecutor(_rows()),
        report_dir=tmp_path / "reports",
        ref_date=REF,
        force=True,
    )
    assert first["ok"] is True and Path(first["report_path"]).exists()

    # 同册 cadence=7：报告日=今日 → 第二次按节奏跳过
    second = run_hosted_cleaning_gate(
        RecordingAlerter(),
        config_path=carrier,
        executor=FakeExecutor(_rows()),
        report_dir=tmp_path / "reports",
        ref_date=REF,
    )
    assert second.get("skipped", "").startswith("cadence_7d")

    # 停用标记存在 → 跳过（自动关闭四要素之一）
    (tmp_path / "cleaning_gate.disabled").write_text("stop", encoding="utf-8")
    third = run_hosted_cleaning_gate(
        RecordingAlerter(),
        config_path=carrier,
        executor=FakeExecutor(_rows()),
        report_dir=tmp_path / "reports",
        ref_date=REF,
    )
    assert third.get("skipped") == "master_switch_off"


def test_wiring_disabled_switch(tmp_path: Path) -> None:
    carrier = write_carrier(tmp_path, wiring={"enabled": False})
    out = run_hosted_cleaning_gate(
        RecordingAlerter(), config_path=carrier, executor=FakeExecutor(_rows()), report_dir=tmp_path / "r", ref_date=REF
    )
    assert out.get("skipped") == "wiring_disabled"


class RoutingExecutor:
    """按表名路由的假执行器：造"两表之一恒失败"的稀释案（rb2 §二.9 原形态）。"""

    def __init__(self, rows_by_table: dict[str, list[dict[str, Any]]], fail_tables: tuple[str, ...] = ()) -> None:
        self._rows = rows_by_table
        self._fail = set(fail_tables)
        self.queries: list[str] = []

    def execute(self, sql: str) -> list:
        self.queries.append(sql)
        for table, rows in self._rows.items():
            if table in sql:
                if table in self._fail:
                    raise RuntimeError(f"{table} 不可达（测试注入）")
                cols = sql.split(" FROM ")[0].replace("SELECT ", "", 1).split(", ")
                return [[row.get(col) for col in cols] for row in rows]
        raise AssertionError(f"未预期的表查询: {sql[:80]}")


def _two_table_carrier(tmp_path: Path) -> Path:
    """两表承载册（判据值仍全在册，代码零阈值）——只为造"一张瞎一张亮"的稀释形态。"""

    def book(table: str) -> dict[str, Any]:
        return {
            "table": table,
            "date_col": "trade_date",
            "lookback_days": 5,
            "rules": [
                {
                    "name": "pct_in_band",
                    "field": "pct_change",
                    "op": "between",
                    "lower": -20,
                    "upper": 20,
                    "action": "flag",
                }
            ],
        }

    doc = {
        "schema_version": 1,
        "wiring": {
            "enabled": True,
            "host_schedule": "data_supply_sentinel",
            "cadence_days": 7,
            "read_limit_rows": 500,
            "alert_level": "warn",
            "report_dir": str(tmp_path / "reports"),
            "disabled_flag": str(tmp_path / "cleaning_gate.disabled"),
        },
        "tables": [book("c1_market.t_one"), book("c1_market.t_two")],
    }
    path = tmp_path / "two_tables.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def _rows_two() -> dict[str, list[dict[str, Any]]]:
    return {
        "c1_market.t_one": [{"trade_date": REF, "pct_change": 3.0}],
        "c1_market.t_two": [{"trade_date": REF, "pct_change": -2.0}],
    }


# ---------------------------------------------------------------------------
# W6-H 诚实读数面：ok=True 只能表示"跑过且判干净"（四条绕过的配对红测）
# ---------------------------------------------------------------------------


def test_one_degraded_table_never_dilutes_to_ok(tmp_path: Path) -> None:
    """rb2 §二.9（绕过①）：两表之一恒失败 → degraded_partial，禁冒 ok=True。"""
    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter,
        config_path=_two_table_carrier(tmp_path),
        executor=RoutingExecutor(_rows_two(), fail_tables=("c1_market.t_two",)),
        report_dir=tmp_path / "r",
        ref_date=REF,
        force=True,
    )
    assert out["ok"] is False, "单表降级曾被「全表 degraded 才算红」的口径稀释成绿"
    assert out["status"] == crh.STATUS_DEGRADED_PARTIAL
    assert "not_run_reason" not in out, "降级≠没跑：另一张表确实判完了，读数须分得清这两件事"
    assert out["degraded_tables"] == ["c1_market.t_two"]
    assert Path(out["report_path"]).exists(), "降级读数同样要落报告（台账面不得只留日志）"
    # 刻意口径：degraded_partial 不占节奏闸（inspection_ran=False），否则一次 CH 抖动
    # 就把本腿催眠成"7 天内不必再试"——降级必须下一班重跑，而不是睡着装干净
    assert out["inspection_ran"] is False
    assert any("degraded_partial" in m or "未生效" in m for _, m in alerter.messages), "降级必出声"


def test_zero_row_sample_is_not_inspected_clean(tmp_path: Path) -> None:
    """rb2 §二.10（绕过②）：查询回 0 行=无对象可判，禁当"已巡检且干净"。"""
    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter,
        config_path=write_carrier(tmp_path),
        executor=FakeExecutor([]),
        report_dir=tmp_path / "r",
        ref_date=REF,
        force=True,
    )
    assert out["ok"] is False
    assert out["status"] == crh.STATUS_DEGRADED_PARTIAL
    assert out["no_sample_tables"] == [TABLE]
    assert any("零样本" in m for _, m in alerter.messages), "零样本必打 WARNING（本项目既有家法）"
    assert all(lvl == "WARN" for lvl, msg in alerter.messages if "零样本" in msg), "家法口径=WARNING 不是 INFO"


#: 三把"根本没跑"的闸各自的原因前缀（诚实读数须分得清是谁按住了电闸）
EXPECTED_REASON_PREFIX = {
    "wiring_disabled": "wiring_disabled",
    "master_switch_off": "master_switch_off",
    "cadence": "cadence_7d",
}


@pytest.mark.parametrize("case", ["wiring_disabled", "master_switch_off", "cadence"])
def test_not_run_paths_are_honest(tmp_path: Path, case: str) -> None:
    """rb2 §三.3（绕过③）：三种"根本没跑"一律 ok=False + status=not_run + 出声 + 台账。"""
    carrier = write_carrier(tmp_path)
    report_dir = tmp_path / "reports"
    alerter = RecordingAlerter()
    if case == "wiring_disabled":
        carrier = write_carrier(tmp_path, wiring={"enabled": False})
    elif case == "master_switch_off":
        (tmp_path / "cleaning_gate.disabled").write_text("stop", encoding="utf-8")
    else:
        first = run_hosted_cleaning_gate(
            RecordingAlerter(),
            config_path=carrier,
            executor=FakeExecutor(_rows()),
            report_dir=report_dir,
            ref_date=REF,
            force=True,
        )
        assert first["ok"] is True, "节奏闸红测的前置：先有一次真巡检"

    out = run_hosted_cleaning_gate(
        alerter, config_path=carrier, executor=FakeExecutor(_rows()), report_dir=report_dir, ref_date=REF
    )
    assert out["ok"] is False, f"{case} 路径禁再冒 ok=True"
    assert out["status"] == crh.STATUS_NOT_RUN
    assert out["not_run_reason"].startswith(EXPECTED_REASON_PREFIX[case])
    assert out["inspection_ran"] is False
    assert any(lvl == "WARN" and "not_run" in m for lvl, m in alerter.messages), "停用/跳过必出声"
    ledgers = list(report_dir.glob(f"*{crh._LEDGER_SUFFIX}"))
    assert ledgers, "未跑必落台账（禁只留一行 info 日志）"
    body = json.loads(ledgers[0].read_text(encoding="utf-8"))
    assert body["status"] == crh.STATUS_NOT_RUN and body["inspection_ran"] is False
    assert body["enforcement_state"] == crh.ENFORCEMENT_STATE
    if case != "cadence":
        assert not list(report_dir.glob(f"*{crh._REPORT_SUFFIX}")), (
            "未跑不得产出巡检报告（否则节奏闸把「没跑」记成「跑过」）"
        )


def test_forged_report_cannot_hypnotise_cadence(tmp_path: Path) -> None:
    """rb2 §二.13（投毒面）：空手套一份当天命名的报告文件，不能再让本腿睡 7 天。"""
    carrier = write_carrier(tmp_path)
    report_dir = tmp_path / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"{REF.isoformat()}_cleaning_report.json").write_text(
        json.dumps({"whatever": True}), encoding="utf-8"
    )

    out = run_hosted_cleaning_gate(
        RecordingAlerter(), config_path=carrier, executor=FakeExecutor(_rows()), report_dir=report_dir, ref_date=REF
    )
    assert out.get("skipped") is None, "命名投毒不能把本腿催眠成「已巡检」"
    assert out["status"] == crh.STATUS_RAN_CLEAN

    # 真报告（gate 自对 + inspection_ran）才占节奏闸
    real = json.loads(Path(out["report_path"]).read_text(encoding="utf-8"))
    assert real["gate"] == "cleaning_rules_hosting" and real["inspection_ran"] is True
    again = run_hosted_cleaning_gate(
        RecordingAlerter(), config_path=carrier, executor=FakeExecutor(_rows()), report_dir=report_dir, ref_date=REF
    )
    assert again["status"] == crh.STATUS_NOT_RUN and again["not_run_reason"].startswith("cadence_7d")


def test_illegal_bytes_raise_declared_error_type(tmp_path: Path) -> None:
    """rb2 §二.14（绕过④）：非法编码须归 CleaningGateConfigError，禁裸 UnicodeDecodeError 外溢。"""
    bad = tmp_path / "broken_encoding.yaml"
    bad.write_bytes(b"schema_version: 1\n\xff\xfe\x00 wiring:\n")
    with pytest.raises(CleaningGateConfigError) as exc:
        load_rulebook(bad)
    assert "非法编码" in str(exc.value) + str(getattr(exc.value, "details", {}))

    alerter = RecordingAlerter()
    out = run_hosted_cleaning_gate(
        alerter, config_path=bad, executor=FakeExecutor(_rows()), report_dir=tmp_path / "r", ref_date=REF, force=True
    )
    assert out["ok"] is False and out["status"] == crh.STATUS_NOT_RUN
    assert alerter.messages, "错型收口后仍要出声"


def test_ok_true_implies_ran_and_clean(tmp_path: Path) -> None:
    """闸的口径本身：ok=True 的唯一来源=ran_and_clean（三态互斥，禁"跑了一部分"冒绿）。"""
    out = run_hosted_cleaning_gate(
        RecordingAlerter(),
        config_path=write_carrier(tmp_path),
        executor=FakeExecutor(_rows()),
        report_dir=tmp_path / "r",
        ref_date=REF,
        force=True,
    )
    assert out["status"] == crh.STATUS_RAN_CLEAN and out["ok"] is True
    assert crh.gate_status([]) == crh.STATUS_NOT_RUN
    assert crh.gate_status([{"degraded": False, "no_samples": True, "stats": {}}]) == crh.STATUS_DEGRADED_PARTIAL
    assert (
        crh.gate_status([{"degraded": False, "no_samples": False, "stats": {"flagged": 1}}]) == crh.STATUS_RAN_FINDINGS
    )
    assert crh.status_exit_code(crh.STATUS_DEGRADED_PARTIAL) == 252
    assert crh.status_exit_code(crh.STATUS_RAN_CLEAN) == 0


def test_host_stores_conclusion_but_scheduling_reads_it_not(monkeypatch: pytest.MonkeyPatch) -> None:
    """钉住**半接线**事实（禁把"能跑"写成"已执法"）：宿主只把本腿结论塞进 summary，
    本腿 ok=False 既不改动断供结论、也不进任何排班判定——红队 rb2 §一.2 原话。
    接线一行由总筹落地后，本用例须同批改（改成"结论能改变行为"）。
    """
    from zephyr.data import supply_sentinel as ss

    monkeypatch.setattr(
        ss, "check_tables", lambda: {"checked": 1, "breached": 0, "heartbeat_blind": 0, "ok": True, "blind_spots": []}
    )
    monkeypatch.setattr(ss, "_alert_breaches", lambda alerter, summary: None)
    monkeypatch.setattr(ss, "_run_hosted_quality_sweep", lambda alerter: {"ok": True})
    monkeypatch.setattr(ss, "_run_hosted_cleaning_gate", lambda alerter: {"ok": False, "status": "degraded_partial"})
    # 2026-09-28 st-c9-purify：宿主新增托管第三段（cleaning_anomaly_hosting），本件测试打桩隔离
    monkeypatch.setattr(ss, "_run_hosted_anomaly_gate", lambda alerter: {"ok": True, "skipped": "stub"})

    summary = ss.run_supply_sentinel(alerter=RecordingAlerter())
    assert summary["cleaning_gate"]["status"] == "degraded_partial", "结论至少要在台账面留痕"
    assert summary["ok"] is True, "宿主结论完全不受本腿影响＝无人消费（半接线，非缺陷伪装成缺陷，也非执法成立）"
    assert crh.ENFORCEMENT_STATE == "advisory_only_half_wired"


# ---------------------------------------------------------------------------
# 出厂真册自检：真 YAML 必须被真代码消费（防 fixture 绿而出厂册坏）
# ---------------------------------------------------------------------------


def test_shipped_carrier_loads_and_runs(tmp_path: Path) -> None:
    shipped = Path(crh.__file__).resolve().parents[3] / "config" / "cleaning_rules.yaml"
    assert shipped.exists(), "config/cleaning_rules.yaml 必须随批落盘（DSL 承载真源）"
    wiring, books = load_rulebook(shipped)
    assert wiring.host_schedule == "data_supply_sentinel"
    assert [b.table for b in books] == [TABLE]
    executor = FakeExecutor([{"trade_date": REF, "close": 0.0, "amount": 0.0, "volume": 1200000, "pct_change": 25.0}])
    report = run_cleaning_gate(
        wiring, books, executor=executor, alerter=None, ref_date=REF, report_dir=tmp_path / "shipped", notify=False
    )
    assert report["tables_checked"] == [TABLE]
    by_rule = report["results"][0]["stats"]["by_rule"]
    assert by_rule["close_positive"] == 1 and by_rule["amount_positive"] == 1
    assert by_rule["pct_change_within_bounds"] == 1, "出厂册须对零价/越界涨跌幅出声（09-18 病灶同型）"
    assert report["read_side_only"] is True
