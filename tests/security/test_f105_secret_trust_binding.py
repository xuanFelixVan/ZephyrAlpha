"""F105 密钥信任绑定测试。

覆盖：feishu service 登记 _SERVICE_ENV_FILES（裸 os.environ 降级根因）；
FeishuAlertChannel._resolve_webhook 全路径经 secrets 模块（源级回归守卫）；
get_secret_fail_closed 拦截非密钥形态键 / 缺失 / 空 / 占位符值（monkeypatch env）。
"""

from __future__ import annotations

import inspect

import pytest

from zephyr.security import security_event_bus
from zephyr.security.security_event_bus import FeishuAlertChannel
from zephyr.shared.security import secrets as secrets_module
from zephyr.shared.security.secrets import (
    SECRET_INDICATOR_PATTERNS,
    SecretsError,
    get_secret_fail_closed,
    get_service_secret,
)


def test_webhook_pattern_in_indicator_wordlist() -> None:
    """F105：WEBHOOK 型 URL 属凭据面（含访问 token），入 SECRET_INDICATOR_PATTERNS 词表。"""
    assert "WEBHOOK" in SECRET_INDICATOR_PATTERNS


def test_feishu_service_registered_in_service_env_files() -> None:
    """F105 根因：service="feishu" 未登记时 get_service_secret 必抛 unknown service，
    调用方永远降级裸 os.environ 读取——信任绑定失效。"""
    assert secrets_module._SERVICE_ENV_FILES.get("feishu") == "config/.env.feishu"


def test_get_service_secret_feishu_reads_env_through_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """feishu 登记后 required=False 路径经模块读取 env（rotation 检查生效），不再抛 unknown service。"""
    monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://open.feishu.cn/hook/abc-123")
    url = get_service_secret("ZEPHYR_FEISHU_WEBHOOK", "feishu", required=False)
    assert url == "https://open.feishu.cn/hook/abc-123"


def test_get_service_secret_feishu_missing_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """缺省（无 env 无文件）返回空串不抛——告警通道降级语义保持。"""
    monkeypatch.delenv("ZEPHYR_FEISHU_WEBHOOK", raising=False)
    assert get_service_secret("ZEPHYR_FEISHU_WEBHOOK", "feishu", required=False) == ""


def test_resolve_webhook_returns_override(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """显式 override 优先，不经 secret 通道。"""
    monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://open.feishu.cn/hook/from-env")
    channel = FeishuAlertChannel(pending_path=tmp_path / "alerts_pending.jsonl")
    channel._webhook_override = "https://example.com/hook/override"
    assert channel._resolve_webhook() == "https://example.com/hook/override"


def test_resolve_webhook_env_value_via_module(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """env 配置的 webhook 经 get_service_secret（模块通道）返回。"""
    monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://open.feishu.cn/hook/xyz")
    channel = FeishuAlertChannel(pending_path=tmp_path / "alerts_pending.jsonl")
    channel._webhook_override = None
    assert channel._resolve_webhook() == "https://open.feishu.cn/hook/xyz"


def test_resolve_webhook_has_no_raw_env_read() -> None:
    """源级回归守卫：_resolve_webhook 不得裸读环境变量（F105 复发拦截）。"""
    source = inspect.getsource(FeishuAlertChannel._resolve_webhook)
    assert "os.environ" not in source
    assert "get_secret_or_default" in source


def test_module_has_no_bare_secret_env_read() -> None:
    """模块级守卫：security_event_bus 全文件不得出现字面量密钥型裸读。"""
    source = inspect.getsource(security_event_bus)
    assert 'os.environ.get("ZEPHYR_FEISHU_WEBHOOK"' not in source
    assert 'os.getenv("ZEPHYR_FEISHU_WEBHOOK"' not in source


# ============ get_secret_fail_closed（fail-closed 语义） ============


def test_fail_closed_rejects_non_secret_shaped_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """非密钥形态键名（如 PATH/DEBUG）一律拒绝——secrets 通道不当通用配置读取器。"""
    monkeypatch.setenv("ZEPHYR_DEBUG_FLAG", "1")
    with pytest.raises(SecretsError, match="not secret-shaped"):
        get_secret_fail_closed("ZEPHYR_DEBUG_FLAG")


def test_fail_closed_rejects_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZEPHYR_TEST_API_KEY", raising=False)
    with pytest.raises(SecretsError, match="not set"):
        get_secret_fail_closed("ZEPHYR_TEST_API_KEY")


def test_fail_closed_rejects_empty_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEPHYR_TEST_API_KEY", "")
    with pytest.raises(SecretsError, match="not set"):
        get_secret_fail_closed("ZEPHYR_TEST_API_KEY")


@pytest.mark.parametrize(
    "placeholder",
    ["changeme", "your-api-key-here", "<token>", "PLACEHOLDER_VALUE", "dummy_key", "****"],
)
def test_fail_closed_rejects_placeholder_values(monkeypatch: pytest.MonkeyPatch, placeholder: str) -> None:
    """占位值被当真密钥消费=静默安全事故——fail-closed 拦截（直接 env 投毒场景）。"""
    monkeypatch.setenv("ZEPHYR_TEST_API_KEY", placeholder)
    with pytest.raises(SecretsError, match="placeholder"):
        get_secret_fail_closed("ZEPHYR_TEST_API_KEY")


def test_fail_closed_returns_valid_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEPHYR_TEST_API_KEY", "sk-real-value-9823hfjs")
    assert get_secret_fail_closed("ZEPHYR_TEST_API_KEY") == "sk-real-value-9823hfjs"


def test_fail_closed_webhook_shaped_key_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    """WEBHOOK 入词表后，fail-closed 可读取 webhook 型密钥（回归 WEBHOOK 形态判定）。"""
    monkeypatch.setenv("ZEPHYR_OPS_WEBHOOK_URL", "https://open.feishu.cn/hook/ok-1")
    assert get_secret_fail_closed("ZEPHYR_OPS_WEBHOOK_URL") == "https://open.feishu.cn/hook/ok-1"
