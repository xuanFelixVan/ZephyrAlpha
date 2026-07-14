# [TTL] task_bound
"""test_error_classifier.py — 数据源错误分类器单元测试。

测试组：
- TestClassifyUnrecoverable: 不可恢复错误（配额/认证）分类
- TestClassifyRecoverable: 可恢复错误（超时/网络）分类
- TestClassifyUnknown: 未知错误分类
- TestIsUnrecoverable: is_unrecoverable 便捷函数
- TestIsRecoverable: is_recoverable 便捷函数
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.data.error_classifier import (  # noqa: E402
    classify_error,
    is_unrecoverable,
    is_recoverable,
)


class TestClassifyUnrecoverable:
    """不可恢复错误——配额耗尽/接口废弃/认证失败。"""

    def test_ifind_quota_exhausted(self):
        assert classify_error("iFind error -4318: 配额耗尽") == "unrecoverable"

    def test_ifind_interface_deprecated(self):
        assert classify_error("error -4309: 接口已废弃") == "unrecoverable"

    def test_auth_failure(self):
        assert classify_error("认证失败: unauthorized") == "unrecoverable"

    def test_http_401(self):
        assert classify_error("HTTP 401 Unauthorized") == "unrecoverable"

    def test_http_403(self):
        assert classify_error("HTTP 403 Forbidden") == "unrecoverable"

    def test_license_error(self):
        assert classify_error("license expired") == "unrecoverable"

    def test_quota_english(self):
        assert classify_error("quota exceeded") == "unrecoverable"


class TestClassifyRecoverable:
    """可恢复错误——超时/网络波动。"""

    def test_timeout(self):
        assert classify_error("ConnectionTimeout: timed out") == "recoverable"

    def test_connection_error(self):
        assert classify_error("ConnectionError: ConnectionRefused") == "recoverable"

    def test_http_503(self):
        assert classify_error("HTTPError 503 ServiceUnavailable") == "recoverable"

    def test_http_502(self):
        assert classify_error("HTTPError 502 Bad Gateway") == "recoverable"

    def test_json_decode_error(self):
        assert classify_error("JSONDecodeError: invalid json") == "recoverable"

    def test_remote_disconnected(self):
        assert classify_error("RemoteDisconnected: connection closed") == "recoverable"


class TestClassifyUnknown:
    """未知错误——无匹配关键词。"""

    def test_empty_string(self):
        assert classify_error("") == "unknown"

    def test_none(self):
        assert classify_error(None) == "unknown"

    def test_no_match(self):
        assert classify_error("some weird error xyz123") == "unknown"


class TestIsUnrecoverable:
    """is_unrecoverable 便捷函数。"""

    def test_true_for_quota(self):
        assert is_unrecoverable("配额耗尽") is True

    def test_false_for_timeout(self):
        assert is_unrecoverable("timeout") is False

    def test_false_for_unknown(self):
        assert is_unrecoverable("weird error") is False

    def test_false_for_none(self):
        assert is_unrecoverable(None) is False


class TestIsRecoverable:
    """is_recoverable 便捷函数。"""

    def test_true_for_timeout(self):
        assert is_recoverable("ConnectionError") is True

    def test_false_for_quota(self):
        assert is_recoverable("配额") is False

    def test_false_for_unknown(self):
        assert is_recoverable("weird error") is False

    def test_false_for_none(self):
        assert is_recoverable(None) is False
