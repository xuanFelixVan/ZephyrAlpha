# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] tests.ai_layer.intake.test_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.gate; zephyr.ai_layer.intake.dedup (content_fingerprint); zephyr.governance.depgraph_schema (PG 可达性自探测)
# [CONSUMERS] pytest tests/ai_layer/intake/test_gate.py
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 只读用例不写生产 ai_intake（写用例一律落 test_schema 临时 schema，session 末 DROP）；
#              PG 不可达=skip 而非假绿（自带 needs_pg，不 import 在途 conftest 符号）；
#              纯判据（check_*/candidate_from_mapping/run_ingest refused 路）零 DB 全枚举；
#              近似层换皮漏检已有 known-gap 钉在 test_dedup，本件换皮用例走精确层 sha256（稳定可断言）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红；DESIGN 施工项 4 验收四类样本（缺 labor_killed/单来源/超配额/换皮）逐一落用例
# [TESTS] tests/ai_layer/intake/test_gate.py
# [TTL] permanent
"""test_gate - L2 入库闸判据全枚举 + 四类样本拒因验收（DESIGN 施工项 4）。"""

from __future__ import annotations

import json

import pytest

from zephyr.ai_layer.intake.dedup import content_fingerprint
from zephyr.ai_layer.intake.gate import (
    AdmissionVerdict,
    IntakeCandidate,
    IntakeGate,
    candidate_from_mapping,
    check_four_gates,
    check_injection_probe,
    check_labor_killed,
    check_license,
    check_source_year,
    run_ingest,
)


def _pg_reachable() -> bool:
    """真连一次 PG；任何异常=不可达（据此 skip，而非假绿）。连接归池不 close。"""
    conn = None
    try:
        from zephyr.governance.depgraph_schema import (
            get_depgraph_pg_connection,
            release_depgraph_pg_connection,
        )

        conn = get_depgraph_pg_connection(read_only=True)
        conn.cursor().execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001 - 可达性探测面，任何异常一律判不可达
        return False
    finally:
        if conn is not None:
            from zephyr.governance.depgraph_schema import release_depgraph_pg_connection

            release_depgraph_pg_connection(conn)


needs_pg = pytest.mark.skipif(not _pg_reachable(), reason="PostgreSQL 不可达（skip 而非假绿）")

VALID_LABOR = "消灭人工筛选论文、人工判重与人工建档三段重复劳动，全部转机检"
VALID_PROBE = "这份材料想让我相信行为格保优比单目标寻优更抗局部最优"


def _four_gates(sources: int = 2, status: str = "已验证") -> dict:
    """四闸合法形态（provenance pass / 交叉验证 / ashare 判词 / 可回测）。"""
    return {
        "provenance": {"status": "pass"},
        "cross_validation": {"independent_sources": sources, "status": status},
        "ashare_adaptation": {"verdict": "改造方案：适配 A 股 T+1 与涨跌停约束后重验"},
        "backtestable": {"verdict": "可得且可用", "data_fields": ["open", "close", "volume"]},
    }


def _candidate(**overrides: object) -> IntakeCandidate:
    """合法候选基线（过闸形态），用例按需覆写单字段构造坏样本。"""
    base: dict = {
        "card_id": "CC-arxiv-20260921-0001",
        "domain_id": "governance",
        "title": "MAP-Elites 行为格多样性保底机制",
        "novelty": "以行为描述子网格取代单目标最优解",
        "mechanism": "逐格保留最高适应度个体，变异体入格竞争胜出者留档",
        "source_name": "arxiv",
        "source_url": "https://arxiv.org/abs/1504.04909",
        "source_year": 2015,
        "license": "mit",
        "labor_killed": VALID_LABOR,
        "four_gates": _four_gates(),
        "injection_probe": VALID_PROBE,
    }
    base.update(overrides)
    return IntakeCandidate(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------- 纯判据（零 DB）


def test_check_labor_killed_paths() -> None:
    ok, why = check_labor_killed(VALID_LABOR)
    assert ok and why == ""
    assert check_labor_killed(None) == (False, "labor_killed_missing")
    assert check_labor_killed("  ") == (False, "labor_killed_missing")
    assert check_labor_killed("待填")[1] == "labor_killed_placeholder"
    assert check_labor_killed("短")[1] == "labor_killed_placeholder"
    short = check_labor_killed("不足二十字的占位说明文本")
    assert short[0] is False and short[1].startswith("labor_killed_too_short")


def test_check_injection_probe_paths() -> None:
    assert check_injection_probe(VALID_PROBE) == (True, "")
    assert check_injection_probe("")[1] == "injection_probe_missing"
    assert check_injection_probe("略")[1] == "injection_probe_missing"
    assert check_injection_probe(None)[0] is False


def test_check_four_gates_missing_keys_and_provenance() -> None:
    ok, reasons, capped = check_four_gates({}, "governance")
    assert not ok and not capped
    for key in ("provenance", "cross_validation", "ashare_adaptation", "backtestable"):
        assert f"four_gates_missing_key:{key}" in reasons
    gates = _four_gates()
    gates["provenance"] = {"status": "fail"}
    ok, reasons, _ = check_four_gates(gates, "governance")
    assert not ok and "provenance_not_pass" in reasons
    ok, reasons, _ = check_four_gates("not-a-dict", "governance")
    assert not ok and "four_gates_missing" in reasons


def test_check_four_gates_single_source_caps_l1() -> None:
    ok, reasons, capped = check_four_gates(_four_gates(sources=1, status="待验证"), "governance")
    assert ok and not reasons and capped, "单来源+待验证=封顶 L1（非拒绝）"
    ok, reasons, capped = check_four_gates(_four_gates(sources=1, status="已验证"), "governance")
    assert not ok and "cross_validation_insufficient_sources" in reasons and not capped
    ok, reasons, capped = check_four_gates(_four_gates(sources="abc"), "governance")
    assert not ok and "cross_validation_sources_not_int" in reasons


def test_check_four_gates_backtestable_and_data_eng() -> None:
    gates = _four_gates()
    gates["backtestable"] = {"verdict": "", "data_fields": ["x"]}
    assert "backtestable_verdict_missing" in check_four_gates(gates, "governance")[1]
    gates["backtestable"] = {"verdict": "可得", "data_fields": []}
    assert "backtestable_data_fields_missing" in check_four_gates(gates, "governance")[1]
    gates["backtestable"] = {"verdict": "可得", "data_fields": ["x"]}
    assert "quality_gaps_missing" in check_four_gates(gates, "data_eng")[1], "data_eng 域须 quality_gaps 画像"
    ext = {"quality_gaps": ["字段缺失画像"]}
    assert check_four_gates(gates, "data_eng", ext)[0] is True
    assert check_four_gates(gates, "governance")[0] is True, "非 data_eng 域不强制 quality_gaps"


def test_check_license_denylist_and_limited() -> None:
    assert check_license("mit") == (True, "", False)
    ok, why, limited = check_license("lgpl-3.0")
    assert ok and limited, "弱传染=放行但标 read_only_limited"
    assert check_license("gpl-3.0") == (False, "license_denied:gpl-3.0", False)
    assert check_license("")[1] == "license_missing"
    assert check_license("待填")[1] == "license_missing"


def test_check_source_year_bounds() -> None:
    assert check_source_year(2015) == (True, "")
    assert check_source_year(2000) == (True, "")
    assert check_source_year(1999)[1].startswith("source_year_out_of_range")
    future = check_source_year(2999, current_year=2026)
    assert not future[0] and future[1].startswith("source_year_out_of_range")
    assert check_source_year("not-a-year")[1] == "source_year_not_int"
    assert check_source_year(None)[0] is False


def test_candidate_from_mapping_ignores_unknown_keys() -> None:
    raw = {
        "card_id": "CC-x-1",
        "domain_id": "governance",
        "title": "t",
        "novelty": "n",
        "mechanism": "m",
        "source_name": "s",
        "source_url": "https://example.org/x",
        "unknown_future_field": 1,
        "labor_killed": VALID_LABOR,
    }
    cand = candidate_from_mapping(raw)
    assert isinstance(cand, IntakeCandidate)
    assert cand.card_id == "CC-x-1"
    assert cand.license == "" and cand.four_gates == {}, "缺键走 dataclass 默认"
    assert not hasattr(cand, "unknown_future_field"), "未知键必须被忽略"


def test_candidate_fingerprints_derived() -> None:
    cand = _candidate()
    assert cand.text_for_fingerprint().startswith("MAP-Elites")
    assert cand.content_sha256() == content_fingerprint(cand.source_url, cand.title)
    assert 0 <= cand.fingerprint() < (1 << 64)


def test_admission_verdict_primary_reason() -> None:
    verdict = AdmissionVerdict(passed=False, reject_reasons=("license_missing", "quota_exceeded:x"))
    assert verdict.primary_reason == "license_missing"
    assert AdmissionVerdict(passed=True).primary_reason == ""


def test_run_ingest_refused_paths(tmp_path: object) -> None:
    """零副作用失败三分支：staging 缺失 / 非 JSON / 非列表（不构造 gate、不触 DB）。"""
    missing = run_ingest(str(tmp_path) + "/no_such_staging.json")  # type: ignore[attr-defined]
    assert set(missing) == {"refused"} and missing["refused"].startswith("staging_missing")
    bad_json = tmp_path / "bad.json"  # type: ignore[operator]
    bad_json.write_text("not-json{{", encoding="utf-8")
    assert run_ingest(str(bad_json))["refused"].startswith("staging_unreadable")
    not_list = tmp_path / "obj.json"  # type: ignore[operator]
    not_list.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert run_ingest(str(not_list))["refused"] == "staging_not_a_list"


# ---------------------------------------------------------------- admit 全闸（PG 临时 schema）


def test_admit_rejects_missing_labor_killed(test_schema: str) -> None:
    gate = IntakeGate(schema=test_schema)
    verdict = gate.admit(
        _candidate(
            title="缺进货费问一样本唯一标题", source_url="https://arxiv.org/abs/gate-missing-labor", labor_killed=""
        )
    )
    assert not verdict.passed and verdict.primary_reason == "labor_killed_missing"


def test_admit_single_source_caps_l1_not_rejected(test_schema: str) -> None:
    gate = IntakeGate(schema=test_schema)
    verdict = gate.admit(
        _candidate(
            title="单来源封顶样本唯一标题",
            source_url="https://arxiv.org/abs/gate-single-source",
            four_gates=_four_gates(sources=1, status="待验证"),
        )
    )
    assert verdict.passed, f"单来源非拒因：{verdict.reject_reasons}"
    assert verdict.cap_stage == "L1", "单来源封顶 L1 不许进 E2"


def test_admit_quota_exceeded(test_schema: str) -> None:
    gate = IntakeGate(schema=test_schema)
    conn = gate._store.write_conn()  # noqa: SLF001 - 测试预置配额行（同包写路径）
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {test_schema}.ai_intake_source_quota (source_slug, daily_quota) VALUES (%s, %s)",
        ("quota-src", 1),
    )
    conn.commit()
    first_cand = _candidate(
        card_id="CC-q-0001",
        source_name="quota-src",
        title="配额首卡唯一标题",
        source_url="https://arxiv.org/abs/quota-first",
    )
    first = gate.admit_and_store(first_cand)
    assert first[1] == "CC-q-0001", f"配额内首卡应入库：{first[0].reject_reasons}"
    second = gate.admit(
        _candidate(
            card_id="CC-q-0002",
            source_name="quota-src",
            title="配额次卡唯一标题",
            source_url="https://arxiv.org/abs/quota-second",
        )
    )
    assert not second.passed
    assert any(r.startswith("quota_exceeded:quota-src:") for r in second.reject_reasons)


def test_admit_rejects_exact_duplicate_sha(test_schema: str) -> None:
    gate = IntakeGate(schema=test_schema)
    kept_cand = _candidate(
        card_id="CC-d-0001",
        title="换皮防护基线卡唯一标题",
        source_url="https://arxiv.org/abs/reskin-base",
    )
    kept = gate.admit_and_store(kept_cand)
    assert kept[1] == "CC-d-0001", f"基线卡应入库：{kept[0].reject_reasons}"
    reskin = gate.admit(
        _candidate(card_id="CC-d-0002", title="换皮防护基线卡唯一标题", source_url="https://arxiv.org/abs/reskin-base")
    )
    assert not reskin.passed, "同 url+title 换皮（精确层）必须被拒"
    assert any(r.startswith("duplicate_sha:CC-d-0001") for r in reskin.reject_reasons)


def test_admit_and_store_happy_path_roundtrip(test_schema: str) -> None:
    gate = IntakeGate(schema=test_schema)
    cand = _candidate(
        card_id="CC-h-0001", title="过闸入库往返样本唯一标题", source_url="https://arxiv.org/abs/happy-path"
    )
    verdict, card_id = gate.admit_and_store(cand)
    assert verdict.passed and card_id == "CC-h-0001", f"合法卡应过闸：{verdict.reject_reasons}"
    card = gate._store.get("CC-h-0001")  # noqa: SLF001 - 读回验证落库形态
    assert card is not None
    assert card.funnel_stage == "L0" and card.elite_cell == "governance|unclassified"
    assert card.simhash == cand.fingerprint()
