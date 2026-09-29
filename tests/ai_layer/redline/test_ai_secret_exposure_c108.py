# [BLUEPRINT] MOD-INF-037 | tests/ai_layer/redline/test_ai_secret_exposure_c108.py | §C108
# [MODULE] tests.ai_layer.redline.test_ai_secret_exposure_c108
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.redline.ai_secret_exposure; zephyr.shared.security.secrets
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] tmp_path 隔离（registry/ledger 显式传参禁写生产路径）；registry monkeypatch 不触真注册表；env 变量用 monkeypatch 恢复
# [MODIFY-GUARD] 测试函数名与 current_session_is_ai_side / assert_key_not_forbidden_ai_side / get_secret_fail_closed 语义对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-INF-037 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""C108 通电测试——AI/生产会话判别器 + 读取面 AI 侧断言 + 判别器三态。

覆盖：
  1. current_session_is_ai_side：无 sid/未在册=非 AI（owner 放）；在册=AI（拦）；
     registry 故障保守非 AI；显式参优先于 env
  2. assert_key_not_forbidden_ai_side：AI 侧命中 forbidden 抛、owner 侧同键放行
  3. get_secret_fail_closed 接线：AI 侧 forbidden 键拒读；owner 侧同键可读
"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.redline.ai_secret_exposure import (
    AiExposureError,
    assert_key_not_forbidden_ai_side,
    current_session_is_ai_side,
)
from zephyr.shared.security.secrets import get_secret_fail_closed

_FORBIDDEN_KEY = "QMT_LIVE_TEST_KEY"


def _forbidden_registry(tmp_path):
    """构造单条 ai_exposure: forbidden 的临时秘钥册（QMT 前缀族）。"""
    reg = tmp_path / "secret_registry.yaml"
    reg.write_text(
        "secrets:\n  - key: QMT_LIVE_*\n    ai_exposure: forbidden\n",
        encoding="utf-8",
    )
    return reg


def _registered_session(monkeypatch, sid="st-c108-ai"):
    """monkeypatch SessionRegistry：sid 在册（AI 施工会话）。"""
    from zephyr.security.access_control import session_concurrency as sc

    class _FakeRegistry:
        def __init__(self, *a, **k):
            pass

        def get_session(self, s):
            return {"session_id": s, "logical": False} if s == sid else None

    monkeypatch.setattr(sc, "SessionRegistry", _FakeRegistry)
    return sid


def test_no_session_id_is_non_ai(monkeypatch) -> None:
    monkeypatch.delenv("ZEPHYR_SESSION_ID", raising=False)
    assert current_session_is_ai_side(None) is False
    assert current_session_is_ai_side("") is False


def test_registered_session_is_ai_side(monkeypatch) -> None:
    sid = _registered_session(monkeypatch)
    assert current_session_is_ai_side(sid) is True


def test_unregistered_session_is_non_ai(monkeypatch) -> None:
    _registered_session(monkeypatch, sid="other-session")
    assert current_session_is_ai_side("st-c108-nobody") is False


def test_registry_failure_is_conservative_non_ai(monkeypatch) -> None:
    from zephyr.security.access_control import session_concurrency as sc

    class _BoomRegistry:
        def __init__(self, *a, **k):
            raise RuntimeError("registry db down")

    monkeypatch.setattr(sc, "SessionRegistry", _BoomRegistry)
    assert current_session_is_ai_side("st-c108-x") is False


def test_explicit_sid_beats_env(monkeypatch) -> None:
    sid = _registered_session(monkeypatch)
    monkeypatch.setenv("ZEPHYR_SESSION_ID", sid)
    # env 在册 sid → AI；显式未在册参 → 非 AI（显式参优先）
    assert current_session_is_ai_side() is True
    assert current_session_is_ai_side("st-c108-nobody") is False


def test_ai_side_assert_raises_on_forbidden(tmp_path, monkeypatch) -> None:
    sid = _registered_session(monkeypatch)
    reg = _forbidden_registry(tmp_path)
    with pytest.raises(AiExposureError):
        assert_key_not_forbidden_ai_side(_FORBIDDEN_KEY, session_id=sid, registry_path=reg, ledger_path=None)


def test_owner_side_same_key_passes(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ZEPHYR_SESSION_ID", raising=False)
    reg = _forbidden_registry(tmp_path)
    out = assert_key_not_forbidden_ai_side(_FORBIDDEN_KEY, session_id=None, registry_path=reg, ledger_path=None)
    assert out == _FORBIDDEN_KEY


def test_get_secret_fail_closed_blocks_ai_side(tmp_path, monkeypatch) -> None:
    sid = _registered_session(monkeypatch)
    monkeypatch.setenv("ZEPHYR_SESSION_ID", sid)  # 读取面无显式参 → 走 env 惯例
    reg = _forbidden_registry(tmp_path)
    # 读取面钩子走模块缺省册——monkeypatch 缺省真源到 tmp（禁写生产路径/册）
    import zephyr.ai_layer.redline.ai_secret_exposure as mod

    monkeypatch.setattr(mod, "DEFAULT_REGISTRY_PATH", reg)
    monkeypatch.setattr(mod, "DEFAULT_FORBIDDEN_LEDGER", tmp_path / "ledger.jsonl")
    monkeypatch.setenv(_FORBIDDEN_KEY, "real-secret-value")
    with pytest.raises(AiExposureError):
        get_secret_fail_closed(_FORBIDDEN_KEY)  # env sid 在册 → AI 侧 → 拒
    assert sid  # 占位防 unused


def test_get_secret_fail_closed_owner_side_reads(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ZEPHYR_SESSION_ID", raising=False)
    reg = _forbidden_registry(tmp_path)
    monkeypatch.setenv(_FORBIDDEN_KEY, "real-secret-value")
    # owner 通道（无 sid 且未在册）→ 放行读取；断言面经默认注册表（在册判定不受
    # tmp registry 影响，本测试 monkeypatch 掉注册表查询恒 None）
    from zephyr.security.access_control import session_concurrency as sc

    class _NoneRegistry:
        def __init__(self, *a, **k):
            pass

        def get_session(self, s):
            return None

    monkeypatch.setattr(sc, "SessionRegistry", _NoneRegistry)
    value = get_secret_fail_closed(_FORBIDDEN_KEY)
    assert value == "real-secret-value"
    assert reg.exists()  # 占位：临时册构造未被裁剪
