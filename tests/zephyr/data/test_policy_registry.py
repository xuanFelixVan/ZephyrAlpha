"""policy_registry 单测（MOD-L00-004 阶段1）。

测试内容：
- SourcePolicy.from_dict（忽略未知字段）
- PolicyRegistry 默认策略加载
- PolicyRegistry.get_policy（已注册/未注册）
- PolicyRegistry.register（编程式注册）
- PolicyRegistry.list_sources
"""
import pytest

from src.zephyr.data.policy_registry import (
    SourcePolicy,
    PolicyRegistry,
    DEFAULT_POLICIES,
)


class TestSourcePolicy:
    def test_defaults(self):
        p = SourcePolicy()
        assert p.rpm == 0
        assert p.concurrency == 1
        assert p.max_retries == 3
        assert p.backoff == "exponential"
        assert p.retry_on == []
        assert p.extra == {}

    def test_from_dict_ignores_unknown(self):
        d = {
            "rpm": 60,
            "unknown_field": "should be ignored",
            "max_retries": 5,
        }
        p = SourcePolicy.from_dict(d)
        assert p.rpm == 60
        assert p.max_retries == 5

    def test_from_dict_all_fields(self):
        d = {
            "rpm": 60, "concurrency": 4, "max_retries": 5,
            "backoff": "jittered", "initial_wait_sec": 2.0,
            "retry_on": ["HTTPError"], "disconnect_vpn": True,
            "extra": {"key": "val"},
        }
        p = SourcePolicy.from_dict(d)
        assert p.concurrency == 4
        assert p.disconnect_vpn is True
        assert p.extra == {"key": "val"}


class TestPolicyRegistry:
    def test_defaults_loaded(self):
        """构造时自动加载 DEFAULT_POLICIES 的 8 个源。"""
        r = PolicyRegistry()
        for src in ["ifind", "miniqmt", "akshare", "baostock",
                     "tushare", "tickflow", "tdx", "rss"]:
            assert src in r.list_sources()

    def test_get_policy_ifind(self):
        r = PolicyRegistry()
        p = r.get_policy("ifind")
        assert p.concurrency == 1
        assert p.relogin_on_auth_error is True
        assert "-4318" in p.extra.get("quota_error_codes", [])

    def test_get_policy_akshare(self):
        r = PolicyRegistry()
        p = r.get_policy("akshare")
        assert p.rpm == 60
        assert p.concurrency == 4
        assert p.disconnect_vpn is True

    def test_get_policy_baostock(self):
        r = PolicyRegistry()
        p = r.get_policy("baostock")
        assert p.concurrency == 8
        assert p.extra.get("thread_local_login") is True
        assert p.extra.get("data_lag_days") == 7

    def test_get_unknown_source(self):
        """未注册源返回默认保守策略。"""
        r = PolicyRegistry()
        p = r.get_policy("nonexistent")
        assert p.rpm == 0
        assert p.max_retries == 3

    def test_register(self):
        """编程式注册覆盖。"""
        r = PolicyRegistry()
        custom = SourcePolicy(rpm=999, max_retries=1)
        r.register("custom_src", custom)
        assert "custom_src" in r.list_sources()
        assert r.get_policy("custom_src").rpm == 999

    def test_list_sources_sorted(self):
        r = PolicyRegistry()
        sources = r.list_sources()
        assert sources == sorted(sources)

    def test_maybe_reload_no_yaml(self):
        """未加载 yaml 时 maybe_reload 返回 False。"""
        r = PolicyRegistry()
        assert r.maybe_reload() is False


class TestDefaultPoliciesCompleteness:
    """确保 DEFAULT_POLICIES 覆盖蓝图 §5.2 的 8 个数据源。"""

    def test_all_8_sources_present(self):
        expected = {"ifind", "miniqmt", "akshare", "baostock",
                    "tushare", "tickflow", "tdx", "rss"}
        assert expected == set(DEFAULT_POLICIES.keys())

    def test_ifind_quota_codes(self):
        p = SourcePolicy.from_dict(DEFAULT_POLICIES["ifind"])
        assert "-4318" in p.extra["quota_error_codes"]
        assert "-4309" in p.extra["quota_error_codes"]

    def test_akshare_dongfang_skip(self):
        p = SourcePolicy.from_dict(DEFAULT_POLICIES["akshare"])
        assert "dongfang_caizhang_skip_after" in p.extra
