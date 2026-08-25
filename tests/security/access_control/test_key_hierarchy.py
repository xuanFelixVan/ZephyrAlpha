# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md
# [TTL] permanent
"""三层密钥层级测试（B12-03842 / CAND-SEC-004）。

测试内容（假时钟 + 内存审计 sink，不依赖真实环境变量与文件）：
- 主密钥缺失 fail-closed / 显式主密钥注入 / 环境变量读取
- KEK 派生：同 purpose 确定性、异 purpose 无关性、非主密钥本身
- DEK 按域派发：按域隔离、同域缓存、落盘态无明文（wrapped）
- 信封加解密：seal/open 回环、跨域不可开、篡改即拒
- 90 天轮换：needs_rotation 到期判定、rotate_dek 换钥、轮换审计
- 密钥使用审计落哈希链：dispatch/rotate/self_check 事件入 sink
- 启动完整性自检：全项通过 / 注册表缺失与损坏检出
- 轮换到期清单：registry rotation_days 到期报告
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from zephyr.security.access_control.key_hierarchy import (
    KeyHierarchy,
    KeyHierarchyError,
)

_MASTER_HEX = "ab" * 32  # 64 hex chars = 32 bytes


class _Clock:
    """可推进的假时钟。"""

    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, days: float) -> None:
        self.now += timedelta(days=days)


@pytest.fixture
def clock():
    return _Clock()


@pytest.fixture
def audit_events():
    return []


@pytest.fixture
def hierarchy(clock, audit_events):
    return KeyHierarchy(
        master_key=bytes.fromhex(_MASTER_HEX),
        audit_sink=audit_events.append,
        clock=clock,
        registry_path=Path("nonexistent_registry.yaml"),  # 缺注册表不阻断运行
    )


# ── 主密钥层 ──────────────────────────────────────────────


def test_missing_master_key_fail_closed(monkeypatch):
    """主密钥未配置（显式与环境变量均无）→ fail-closed 抛 KeyHierarchyError。"""
    monkeypatch.delenv(KeyHierarchy.MASTER_KEY_ENV, raising=False)
    with pytest.raises(KeyHierarchyError):
        KeyHierarchy()


def test_master_key_from_env(monkeypatch):
    """主密钥走环境变量（系统密钥环/环境变量层），hex 编码。"""
    monkeypatch.setenv(KeyHierarchy.MASTER_KEY_ENV, _MASTER_HEX)
    kh = KeyHierarchy()
    assert kh.derive_kek("audit")


def test_master_key_invalid_hex_rejected():
    with pytest.raises(KeyHierarchyError):
        KeyHierarchy(master_key="not-hex-zz")


# ── KEK 层 ────────────────────────────────────────────────


def test_kek_derivation_deterministic_and_purpose_isolated(hierarchy):
    kek_a1 = hierarchy.derive_kek("domain_wrap")
    kek_a2 = hierarchy.derive_kek("domain_wrap")
    kek_b = hierarchy.derive_kek("audit_hmac")
    assert kek_a1 == kek_a2  # 同 purpose 确定性
    assert kek_a1 != kek_b  # 异 purpose 密码学隔离
    assert len(kek_a1) == 32


# ── DEK 按域派发 ──────────────────────────────────────────


def test_dispatch_dek_domain_isolation_and_cache(hierarchy):
    dek_trading = hierarchy.dispatch_dek("trading")
    dek_data = hierarchy.dispatch_dek("data")
    assert dek_trading.domain == "trading"
    assert dek_trading.key_id != dek_data.key_id  # 按域派发不同 DEK
    again = hierarchy.dispatch_dek("trading")
    assert again.key_id == dek_trading.key_id  # 同域缓存复用


def test_dispatched_dek_no_plaintext_at_rest(hierarchy):
    """内存记录仅持 wrapped 形态：对象状态与 repr 均不含明文 DEK。"""
    hierarchy.dispatch_dek("trading")
    state = hierarchy.export_state()
    assert "wrapped_dek" in state["trading"]
    raw = state["trading"]["wrapped_dek"]
    assert isinstance(raw, bytes)
    # 32 字节明文 DEK 不得以原样出现在任何状态字段
    for dek in hierarchy._deks.values():
        assert dek.plaintext is None  # noqa: SLF001 — 测试内部不变量


# ── 信封加解密 ────────────────────────────────────────────


def test_seal_open_roundtrip(hierarchy):
    token = hierarchy.seal("trading", b"broker-credential")
    assert token != b"broker-credential"
    assert hierarchy.open("trading", token) == b"broker-credential"


def test_open_with_wrong_domain_denied(hierarchy):
    token = hierarchy.seal("trading", b"secret")
    with pytest.raises(KeyHierarchyError):
        hierarchy.open("data", token)  # 跨域解密必须失败


def test_open_tampered_token_denied(hierarchy):
    token = bytearray(hierarchy.seal("trading", b"secret"))
    token[-5] ^= 0xFF
    with pytest.raises(KeyHierarchyError):
        hierarchy.open("trading", bytes(token))


# ── 90 天轮换 ─────────────────────────────────────────────


def test_rotation_due_after_90_days(hierarchy, clock):
    hierarchy.dispatch_dek("trading")
    assert hierarchy.needs_rotation("trading") is False
    clock.advance(91)
    assert hierarchy.needs_rotation("trading") is True


def test_rotate_dek_rotates_material_and_resets_age(hierarchy, clock):
    first = hierarchy.dispatch_dek("trading")
    clock.advance(100)
    second = hierarchy.rotate_dek("trading")
    assert second.key_id != first.key_id
    assert hierarchy.needs_rotation("trading") is False
    # 新钥密封回环正常
    token = hierarchy.seal("trading", b"after-rotation")
    assert hierarchy.open("trading", token) == b"after-rotation"


# ── 审计落哈希链（sink 由 AiAuditLogger 哈希链承担）───────


def test_audit_events_for_dispatch_rotate_self_check(hierarchy, audit_events):
    hierarchy.dispatch_dek("trading")
    hierarchy.rotate_dek("trading")
    hierarchy.startup_self_check()
    kinds = [e["event"] for e in audit_events]
    assert "key.dispatch" in kinds
    assert "key.rotate" in kinds
    assert "key.self_check" in kinds
    dispatch = next(e for e in audit_events if e["event"] == "key.dispatch")
    assert dispatch["domain"] == "trading"
    assert "key_id" in dispatch
    # 审计事件不得含任何密钥材料
    for event in audit_events:
        assert "dek" not in str(event.values()).lower() or "wrapped" in str(event.values()).lower()


# ── 启动完整性自检 ────────────────────────────────────────


def test_startup_self_check_all_pass(hierarchy):
    hierarchy.dispatch_dek("trading")
    results = hierarchy.startup_self_check()
    by_name = {r.name: r for r in results}
    assert by_name["master_configured"].passed
    assert by_name["kek_derivable"].passed
    assert by_name["dek_wrap_roundtrip"].passed
    assert all(r.passed for r in results if r.name != "registry_present")


def test_startup_self_check_detects_broken_registry(tmp_path, clock, audit_events):
    bad = tmp_path / "bad_registry.yaml"
    bad.write_text(":\n  - [broken", encoding="utf-8")
    kh = KeyHierarchy(
        master_key=bytes.fromhex(_MASTER_HEX),
        audit_sink=audit_events.append,
        clock=clock,
        registry_path=bad,
    )
    results = {r.name: r for r in kh.startup_self_check()}
    assert not results["registry_present"].passed


# ── 轮换到期清单（secret_registry.yaml 真源）───────────────


def test_rotation_report_from_registry(tmp_path, clock, audit_events):
    registry = tmp_path / "secret_registry.yaml"
    registry.write_text(
        "secrets:\n"
        "  - key: DEEPSEEK_API_KEY\n"
        "    service: deepseek\n"
        "    rotation_days: 90\n"
        '    since: "2025-09-01"\n'
        "  - key: TUSHARE_TOKEN\n"
        "    service: tushare\n"
        "    rotation_days: 365\n"
        '    since: "2026-08-04"\n'
        "  - key: SOME_CONFIG\n"
        "    service: misc\n"
        "    rotation_days: null\n"
        '    since: "2026-01-01"\n',
        encoding="utf-8",
    )
    kh = KeyHierarchy(
        master_key=bytes.fromhex(_MASTER_HEX),
        audit_sink=audit_events.append,
        clock=clock,  # 2026-01-01
        registry_path=registry,
    )
    report = kh.rotation_report()
    assert report["DEEPSEEK_API_KEY"]["due"] is True  # 2025-09-01 + 90d < 2026-01-01
    assert report["TUSHARE_TOKEN"]["due"] is False
    assert "SOME_CONFIG" not in report  # rotation_days=null 不强制轮换
