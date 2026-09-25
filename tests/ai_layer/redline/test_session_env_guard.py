# [A_test] module_id: zephyr.ai_layer.redline.session_env_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_session_env_guard
# [MODULE] tests.ai_layer.redline.test_session_env_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.session_env_guard
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_session_env_guard.py
# [MATURITY] testing
# [INVARIANTS] 审计路径一律显式注入 tmp_path（禁写生产路径）；KillSwitch 经 monkeypatch
#              session_env_guard.get_kill_switch 换 fresh 实例（不污染进程级单例）
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_session_env_guard.py — S1 会话 env 白名单启动器单测。

验收标准（DESIGN 红蓝 R1-F4）：含 QMT" "_REAL_* 的环境在代理会话被拒且留证。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from zephyr.ai_layer.redline.session_env_guard import (
    EnvScreenVerdict,
    filter_env,
    screen_session_env,
)
from zephyr.security.access_control.kill_switch import KillSwitch


@pytest.fixture()
def fresh_kill_switch(monkeypatch: pytest.MonkeyPatch) -> KillSwitch:
    ks = KillSwitch()
    monkeypatch.setattr(
        "zephyr.ai_layer.redline.session_env_guard.get_kill_switch", lambda: ks
    )
    return ks


def test_qmt_real_env_rejected_with_evidence(tmp_path: Path, fresh_kill_switch: KillSwitch):
    """验收主样例：QMT" "_REAL_PATH 环境被拒且留证（键名留证、值零落盘）。"""
    audit = tmp_path / "audit" / "env_denial.jsonl"
    verdict = screen_session_env(
        {"QMT" "_REAL_PATH": "D:/qmt", "PATH": "whatever"},
        session_id="sess-1",
        audit_path=audit,
    )
    assert verdict.allowed is False
    assert verdict.denied_keys == ("QMT" "_REAL_PATH",)
    assert "QMT" "_REAL_PATH" not in verdict.filtered_env
    assert verdict.leak_suspected is True, "非空值命中=泄密事故候选"
    records = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
    assert len(records) == 1
    record = records[0]
    assert record["action"] == "deny_spawn"
    assert record["denied_keys"] == ["QMT" "_REAL_PATH"]
    assert record["rule_id"] == "NL-2"
    assert "D:/qmt" not in json.dumps(records), "值本体零落盘（***REDACTED*** 形状留痕）"
    assert fresh_kill_switch.is_agent_blocked("sess-1") is False, "单次未达 threshold=3 不阻断（信号已记录）"


def test_audit_hmac_secret_and_live_wildcard_denied(tmp_path: Path, fresh_kill_switch: KillSwitch):
    audit = tmp_path / "audit.jsonl"
    env = {
        "ZEPHYR_AUDIT_HMAC_SECRET": "s3cret",
        "DEEPSEEK_LIVE_KEY": "sk-live",
        "QMT_SIM_PATH": "ok",
    }
    verdict = screen_session_env(env, session_id="sess-2", audit_path=audit)
    assert verdict.allowed is False
    assert verdict.denied_keys == ("DEEPSEEK_LIVE_KEY", "ZEPHYR_AUDIT_HMAC_SECRET")
    assert verdict.filtered_env == {"QMT_SIM_PATH": "ok"}


def test_clean_env_allowed(tmp_path: Path, fresh_kill_switch: KillSwitch):
    audit = tmp_path / "audit.jsonl"
    env = {"QMT_SIM_PATH": "sim", "QMT_SIM_ACCOUNT": "0001", "LANG": "zh_CN"}
    verdict = screen_session_env(env, session_id="sess-3", audit_path=audit)
    assert isinstance(verdict, EnvScreenVerdict)
    assert verdict.allowed is True
    assert verdict.denied_keys == ()
    assert verdict.leak_suspected is False
    assert verdict.filtered_env == env
    assert not audit.exists(), "放行零审计（只拒时留证）"


def test_empty_value_hit_not_leak_suspected(tmp_path: Path, fresh_kill_switch: KillSwitch):
    verdict = screen_session_env(
        {"QMT" "_REAL_ACCOUNT": ""}, session_id="sess-4", audit_path=tmp_path / "a.jsonl"
    )
    assert verdict.allowed is False
    assert verdict.leak_suspected is False, "键名命中但值为空=未泄密，拒绝但不升级"


def test_audit_write_failure_does_not_mask_denial(
    tmp_path: Path, fresh_kill_switch: KillSwitch, caplog: pytest.LogCaptureFixture
):
    """审计写失败 → 判定仍=拒绝（fail-open 留证，不掩盖红线判定）。"""
    bad_dir = tmp_path / "file.txt"  # 用文件路径当目录 → mkdir 必失败
    bad_dir.write_text("x", encoding="utf-8")
    with caplog.at_level(logging.WARNING):
        verdict = screen_session_env(
            {"QMT" "_REAL_PATH": "v"},
            session_id="sess-5",
            audit_path=bad_dir / "sub" / "a.jsonl",
        )
    assert verdict.allowed is False
    assert any("审计写失败" in rec.message for rec in caplog.records)


def test_filter_env_pure_split():
    allowed, denied = filter_env({"A": "1", "QMT" "_REAL_X": "2", "ANY_LIVE_Y": "3"})
    assert allowed == {"A": "1"}
    assert denied == ["QMT" "_REAL_X", "ANY_LIVE_Y"]
