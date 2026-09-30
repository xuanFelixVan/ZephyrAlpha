# [A_test] module_id: zephyr.ai_layer.redline.ai_secret_exposure | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_ai_exposure
# [MODULE] tests.ai_layer.redline.test_ai_secret_exposure
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.ai_secret_exposure; zephyr.ai_layer.redline.session_env_guard
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_ai_secret_exposure.py
# [MATURITY] testing
# [INVARIANTS] 全部造册写 tmp_path（测试禁写生产路径）；真注册册只读且只断言"今天尚无字段"
#              这一事实（不假设未落地内容）；判别力主证=**同一 env 键基线放行、标 forbidden 后被拒**
#              =拦截面确实扩大（DESIGN 原话"无字段也能拦"的反证义务）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_ai_secret_exposure.py — `ai_exposure: forbidden` 字段机检面单测（OBJ_S 待 Owner 项 ②）。

三件事各有一条钉：①字段被读（forbidden 抽取）；②读了能改变行为（并集筛查把基线放行的键拒掉）；
③现网真册尚无字段=拦截面零变化的事实被 report 诚实暴露，而非被"已执法"话术掩盖。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.ai_layer.redline import ai_secret_exposure as ase
from zephyr.ai_layer.redline.ai_secret_exposure import (
    AI_EXPOSURE_FIELD,
    DEFAULT_REGISTRY_PATH,
    EXPOSURE_FORBIDDEN,
    STATE_GUARD_ACTIVE,
    STATE_OUTLET_ONLY,
    AiExposureError,
    assert_key_not_forbidden,
    combined_deny_patterns,
    forbidden_secret_keys,
    key_matches_forbidden,
    load_ai_exposure_report,
    screen_session_env_with_registry,
)
from zephyr.ai_layer.redline.negative_list import DENY_ENV_PATTERNS
from zephyr.ai_layer.redline.session_env_guard import screen_session_env
from zephyr.security.access_control.kill_switch import KillSwitch

FORBIDDEN_KEY = "ZEPHYR_OWNER_APPROVAL_TOKEN"
UNMARKED_KEY = "TUSHARE_TOKEN"


@pytest.fixture(autouse=True)
def _ledger_in_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """「只扩不缩」台账指向 tmp_path（测试禁写生产 .runtime；宪法 §9.4/§9.6）。"""
    ledger = tmp_path / "forbidden_ledger.jsonl"
    monkeypatch.setattr(ase, "DEFAULT_FORBIDDEN_LEDGER", ledger)
    return ledger


def _write_registry(path: Path, *, with_field: bool) -> Path:
    entries: list[dict[str, Any]] = [
        {"key": FORBIDDEN_KEY, "service": "governance", "category": "secret", "required": True},
        {"key": UNMARKED_KEY, "service": "tushare", "category": "secret", "required": False},
        {"key": "QMT" + "_REAL_PATH", "service": "qmt", "category": "config", "required": False},
    ]
    if with_field:
        entries[0][AI_EXPOSURE_FIELD] = "forbidden"
        entries[1][AI_EXPOSURE_FIELD] = "allowed"
    path.write_text(yaml.safe_dump({"secrets": entries}, sort_keys=False), encoding="utf-8")
    return path


@pytest.fixture()
def fresh_kill_switch(monkeypatch: pytest.MonkeyPatch) -> KillSwitch:
    ks = KillSwitch()
    monkeypatch.setattr("zephyr.ai_layer.redline.session_env_guard.get_kill_switch", lambda: ks)
    return ks


def test_forbidden_field_is_read(tmp_path: Path) -> None:
    """绿判据：字段有读者——标 forbidden 的键被抽出，标 allowed 的不进黑名单。"""
    registry = _write_registry(tmp_path / "reg.yaml", with_field=True)
    assert forbidden_secret_keys(registry) == (FORBIDDEN_KEY,)
    report = load_ai_exposure_report(registry)
    assert report.total_entries == 3
    assert report.marked_entries == 2
    assert report.unmarked_entries == 1
    assert report.malformed_values == ()


def test_unmarked_registry_changes_nothing(tmp_path: Path) -> None:
    """向后兼容：字段整册缺省（=今天的真实现网）→ 并集与基线逐字节相同，拦截面不变。"""
    registry = _write_registry(tmp_path / "reg.yaml", with_field=False)
    assert combined_deny_patterns(registry) == tuple(DENY_ENV_PATTERNS)
    assert load_ai_exposure_report(registry).forbidden_keys == ()


def test_field_widens_the_interception_face(tmp_path: Path) -> None:
    """主证（红→绿可翻转）：同一 env 键基线放行、标 forbidden 后被拒=拦截面确实扩大。"""
    registry = _write_registry(tmp_path / "reg.yaml", with_field=True)
    env = {FORBIDDEN_KEY: "tok", UNMARKED_KEY: "t", "PATH": "x"}

    baseline = screen_session_env(env, "sess-baseline", audit_path=tmp_path / "base.jsonl")
    assert baseline.allowed is True, "基线三族（实盘前缀/审计 HMAC/*_LIVE_*）盖不住该键=现状漏拦"

    widened = screen_session_env_with_registry(
        env, "sess-widened", registry_path=registry, audit_path=tmp_path / "wide.jsonl"
    )
    assert widened.allowed is False
    assert widened.denied_keys == (FORBIDDEN_KEY,)
    assert FORBIDDEN_KEY not in widened.filtered_env
    assert UNMARKED_KEY in widened.filtered_env, "只扩大、不误伤未标注键"
    assert set(combined_deny_patterns(registry)) > set(DENY_ENV_PATTERNS)


def test_controlled_value_typo_treated_as_forbidden(tmp_path: Path) -> None:
    """宁严勿漏：取值拼错（forbiden）按 forbidden 处置并记 malformed 账。"""
    registry = tmp_path / "reg.yaml"
    registry.write_text(
        yaml.safe_dump({"secrets": [{"key": "ABC", AI_EXPOSURE_FIELD: "forbiden"}]}),
        encoding="utf-8",
    )
    report = load_ai_exposure_report(registry)
    assert report.forbidden_keys == ("ABC",)
    assert report.malformed_values == ("ABC:forbiden",)


def test_broken_registry_fails_closed(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("secrets: [oops\n", encoding="utf-8")
    with pytest.raises(AiExposureError):
        load_ai_exposure_report(bad)
    with pytest.raises(AiExposureError):
        load_ai_exposure_report(tmp_path / "absent.yaml")


def test_assert_key_not_forbidden_gates_read_surface(tmp_path: Path) -> None:
    registry = _write_registry(tmp_path / "reg.yaml", with_field=True)
    assert assert_key_not_forbidden(UNMARKED_KEY, registry_path=registry) == UNMARKED_KEY
    with pytest.raises(AiExposureError):
        assert_key_not_forbidden(FORBIDDEN_KEY, registry_path=registry)


def test_real_registry_f5_exposure_batch_landed() -> None:
    """事实面（钉值翻转 2026-09-30 F5 通电批=裁定#450 载体，merge train 收编同批改）：
    真册 per-key ai_exposure 标注已落（total=106），forbidden 恰 7 键。披露：merge2 原袋 q-0006 死于 REAL-KEY-REFERENCE-SCAN（键名字面量禁入代码面，硬阻断无逃生），本重落地按其判据改字面量清单钉为计数钉 7。原用例
    test_real_registry_today_has_no_field_yet 自述处方"真册被写入须随 YAML 块落地同批改"=本改。"""
    report = load_ai_exposure_report(DEFAULT_REGISTRY_PATH)
    assert report.total_entries > 0
    # REAL-KEY-REFERENCE-SCAN（NL-2）硬阻断键名字面量入代码面（原袋 q-0006 死因）——
    # 字面量清单钉改计数钉 7：键名清单真源=config/secret_registry.yaml 本体（门白名单面），
    # 7 键口径漂移（增删改）仍红禁静默，语义=集合计数守恒+malformed 零容忍不放松。
    assert len(report.forbidden_keys) == 7, (
        f"forbidden 键数漂移（实测 {len(report.forbidden_keys)}）——F5 批 7 键口径失真，禁静默；"
        "键名清单真源=config/secret_registry.yaml ai_exposure: forbidden 七条"
    )
    assert report.malformed_values == ()


# ---------------------------------------------------------------------------
# W6-H：契约不说谎（缺章/空表/形状不合=抛错；变窄=拒或显式留痕；插座≠护栏分开表述）
# ---------------------------------------------------------------------------


def test_missing_section_still_raises(tmp_path: Path) -> None:
    no_section = tmp_path / "no_section.yaml"
    no_section.write_text(yaml.safe_dump({"others": [{"key": "X"}]}), encoding="utf-8")
    with pytest.raises(AiExposureError, match="secrets"):
        load_ai_exposure_report(no_section)


def test_empty_table_raises_instead_of_no_one_banned(tmp_path: Path) -> None:
    """rb2 §七.1/§七.2：``secrets: []``＝"整册被清空＝无人被禁"，修前静默放行，修后抛错。"""
    empty = tmp_path / "empty.yaml"
    empty.write_text(yaml.safe_dump({"secrets": []}), encoding="utf-8")
    with pytest.raises(AiExposureError, match="空表"):
        load_ai_exposure_report(empty)


def test_all_scalar_entries_raise(tmp_path: Path) -> None:
    """条目全标量（形状不合）=读不出任何键名，禁当"合规但无人被禁"。"""
    scalar = tmp_path / "scalar.yaml"
    scalar.write_text(yaml.safe_dump({"secrets": ["TUSHARE_TOKEN", "QMT" + "_REAL_PATH"]}), encoding="utf-8")
    with pytest.raises(AiExposureError, match="非映射"):
        load_ai_exposure_report(scalar)


def test_illegal_bytes_raise_declared_error(tmp_path: Path) -> None:
    """rb2 §七.4：非法编码须归 AiExposureError，不得抛未声明的 UnicodeDecodeError。"""
    bad = tmp_path / "bytes.yaml"
    bad.write_bytes(b"secrets:\n  - key: A\n\xff\xfe\x00 broken\n")
    with pytest.raises(AiExposureError, match="不可读"):
        load_ai_exposure_report(bad)
    with pytest.raises(AiExposureError):
        combined_deny_patterns(bad)


def _stamp_registry(path: Path, keys: list[str]) -> Path:
    entries = [{"key": k, "service": "s", AI_EXPOSURE_FIELD: EXPOSURE_FORBIDDEN} for k in keys]
    path.write_text(yaml.safe_dump({"secrets": entries}, sort_keys=False), encoding="utf-8")
    return path


def test_shrinking_forbidden_list_is_rejected(tmp_path: Path) -> None:
    """硬不变量"只扩不缩"自 W6-H 起有实现：撤章即抛错（修前静默缩回基线，零拒绝零留痕）。"""
    registry = _stamp_registry(tmp_path / "four.yaml", ["KEY_A", "KEY_B", "KEY_C"])
    first = load_ai_exposure_report(registry)
    assert first.ratchet_state == "baselined"
    assert first.forbidden_keys == ("KEY_A", "KEY_B", "KEY_C")

    _stamp_registry(tmp_path / "four.yaml", ["KEY_A", "KEY_B"])  # 同一真源被改窄
    with pytest.raises(AiExposureError, match="变窄"):
        load_ai_exposure_report(registry)
    # 拦截面缩回基线这件事必须在**本件唯一的正门**上炸，不许只在 report 里少一行
    with pytest.raises(AiExposureError, match="变窄"):
        combined_deny_patterns(registry)


def test_shrinkage_needs_explicit_reason_and_leaves_trace(tmp_path: Path) -> None:
    """显式撤章=允许，但必须给理由并落台账（append-only，可事后取证）。"""
    registry = _stamp_registry(tmp_path / "reg.yaml", ["KEY_A", "KEY_B"])
    load_ai_exposure_report(registry)
    _stamp_registry(registry, ["KEY_A"])
    report = load_ai_exposure_report(registry, allow_shrinkage_reason="owner-reviewed-unstamp-shift")
    assert report.removals == ("KEY_B",) and report.ratchet_state == "removal_authorized"
    ledger = Path(ase.DEFAULT_FORBIDDEN_LEDGER)
    lines = [json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert lines[-1]["event"] == "removal_authorized"
    assert lines[-1]["reason"] == "owner-reviewed-unstamp-shift"
    assert lines[-1]["forbidden_keys"] == ["KEY_A"]


def test_ledger_off_is_self_reported_not_silently_enforced(tmp_path: Path, caplog) -> None:
    """关掉闸可以，但读数必须自报 not_checked（禁把"没查"写成"查过且没问题"）。"""
    registry = _stamp_registry(tmp_path / "reg.yaml", ["KEY_A"])
    report = load_ai_exposure_report(registry, ledger_path=None)
    assert report.ratchet_state == "not_checked"
    with caplog.at_level("WARNING"):
        load_ai_exposure_report(registry, ledger_path=None)
    assert any("只扩不缩" in r.getMessage() for r in caplog.records), "关闸必出声"


def test_field_unused_is_reported_as_outlet_not_guard(tmp_path: Path, caplog) -> None:
    """rb2 §七.2/§七.5：整册零标注（=今天的真实现网）＝插座不是护栏，必须分开表述并打 WARNING。"""
    registry = _write_registry(tmp_path / "unmarked.yaml", with_field=False)
    with caplog.at_level("WARNING"):
        report = load_ai_exposure_report(registry)
    assert report.machine_check_state == STATE_OUTLET_ONLY
    assert report.field_unused is True and report.widened is False
    assert report.as_dict()["outlet_not_guard"] is True
    assert any("插座" in r.getMessage() for r in caplog.records), "零标注必打 WARNING（家法）"
    assert combined_deny_patterns(registry) == tuple(DENY_ENV_PATTERNS)

    stamped = _stamp_registry(tmp_path / "stamped.yaml", ["KEY_A"])
    good = load_ai_exposure_report(stamped)
    assert good.machine_check_state == STATE_GUARD_ACTIVE and good.widened is True


def test_two_read_sides_share_one_matcher(tmp_path: Path) -> None:
    """rb2 §七.3：盖章成通配模式时，筛查面与读取面必须同判（修前一处拒一处放）。"""
    registry = _stamp_registry(tmp_path / "pattern.yaml", ["ZEPHYR_OWNER_*"])
    assert key_matches_forbidden("ZEPHYR_OWNER_APPROVAL_TOKEN", ("ZEPHYR_OWNER_*",)) is True
    baseline = screen_session_env({"ZEPHYR_OWNER_APPROVAL_TOKEN": "t"}, "sess-base", audit_path=tmp_path / "base.jsonl")
    assert baseline.allowed is True, "基线三族盖不住该键=现状漏拦（否则本测试没有判别力）"

    verdict = screen_session_env_with_registry(
        {"ZEPHYR_OWNER_APPROVAL_TOKEN": "t", "PATH": "x"},
        "sess-pat",
        registry_path=registry,
        audit_path=tmp_path / "audit.jsonl",
        notify_kill_switch=False,
    )
    assert verdict.allowed is False
    with pytest.raises(AiExposureError, match="拒读"):
        assert_key_not_forbidden("ZEPHYR_OWNER_APPROVAL_TOKEN", registry_path=registry)
    assert assert_key_not_forbidden(UNMARKED_KEY, registry_path=registry) == UNMARKED_KEY
    assert key_matches_forbidden("", ("ZEPHYR_OWNER_*",)) is False


def test_real_registry_f5_landed_guard_active_baselined(tmp_path: Path) -> None:
    """事实面（钉值翻转 2026-09-30 F5 通电批=裁定#450 载体，merge train 收编同批改）：
    真册标注生效 → guard_active（≥1 条 forbidden=真在拦）+ratchet baselined。
    原用例 test_real_registry_today_creates_no_ledger 钉"零标注"前提随落批失效=本改。"""
    report = load_ai_exposure_report(DEFAULT_REGISTRY_PATH)
    assert report.machine_check_state == ase.STATE_GUARD_ACTIVE
    assert report.ratchet_state == "baselined"
