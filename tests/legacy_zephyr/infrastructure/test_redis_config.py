# [TTL] task_bound
# [TESTS] zephyr.infrastructure.redis_config
"""redis_config 单元测试——验证 socket_timeout 注入（CP-02 软故障治本）。

背景（治本，2026-08-03 实地演练发现）：
    无 socket_timeout 时 Redis 暂停/卡顿 → redis-py 无限阻塞 →
    try/except 永不触发 → CP-02 优雅降级失效。
    load_redis_config() 必须返回含 socket_timeout / socket_connect_timeout 的字典。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import pytest

from zephyr.infrastructure.redis_config import (
    RedisConfigError,
    ensure_redis_env_loaded,
    load_redis_config,
)


def _set_env(monkeypatch, **kwargs):
    """设置环境变量并重置 redis_config 模块加载状态（保证 hermetic）。"""
    import zephyr.infrastructure.redis_config as rc

    # 重置幂等加载标志，强制重新读 env
    monkeypatch.setattr(rc, "_loaded", False)
    # ensure_redis_env_loaded 读真源文件，测试用 env 隔离——跳过文件加载
    monkeypatch.setattr(rc, "ensure_redis_env_loaded", lambda: None)
    # 生产跟进（#ARCH-SECRETS-GOV-001 S-2）：get_secret_from_file_or_default 已退役，
    # 切换为 get_service_secret(key, "redis", required=False)——stub 目标同步替换：
    # env 非空 → 用 env 值；env 空/缺失 → 返回空串（模拟"文件也没有"→走默认值）
    monkeypatch.setattr(
        rc,
        "get_service_secret",
        lambda key, service, required=True: os.environ.get(key, ""),
    )
    # 提供所有 load_redis_config 读取的键的默认值（避免空字符串破坏 int() 等）
    defaults = {
        "REDIS_HOST": "",
        "REDIS_PORT": "6379",
        "REDIS_PASSWORD": "",
        "REDIS_DB": "0",
        "REDIS_DECODE_RESPONSES": "true",
        "REDIS_SOCKET_TIMEOUT": "",
        "REDIS_SOCKET_CONNECT_TIMEOUT": "",
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        monkeypatch.setenv(k, v)


class TestLoadRedisConfigTimeouts:
    """socket_timeout / socket_connect_timeout 注入（CP-02 治本）。"""

    def test_has_socket_timeout(self, monkeypatch):
        _set_env(
            monkeypatch,
            REDIS_HOST="127.0.0.1",
            REDIS_PORT="6379",
            REDIS_PASSWORD="pw",
            REDIS_SOCKET_TIMEOUT="2",
            REDIS_SOCKET_CONNECT_TIMEOUT="2",
        )
        cfg = load_redis_config()
        assert cfg["socket_timeout"] == 2.0
        assert cfg["socket_connect_timeout"] == 2.0
        assert isinstance(cfg["socket_timeout"], float)
        assert isinstance(cfg["socket_connect_timeout"], float)

    def test_custom_timeout_values(self, monkeypatch):
        """自定义超时值（如 0.5s）正确解析。"""
        _set_env(
            monkeypatch,
            REDIS_HOST="127.0.0.1",
            REDIS_PORT="6379",
            REDIS_PASSWORD="pw",
            REDIS_SOCKET_TIMEOUT="0.5",
            REDIS_SOCKET_CONNECT_TIMEOUT="1.5",
        )
        cfg = load_redis_config()
        assert cfg["socket_timeout"] == pytest.approx(0.5)
        assert cfg["socket_connect_timeout"] == pytest.approx(1.5)

    def test_default_socket_timeout_2_seconds(self, monkeypatch):
        """未设置时默认 2 秒（治本 CP-02 软故障兜底）。"""
        _set_env(
            monkeypatch,
            REDIS_HOST="127.0.0.1",
            REDIS_PORT="6379",
            REDIS_PASSWORD="pw",
            REDIS_SOCKET_TIMEOUT="",
            REDIS_SOCKET_CONNECT_TIMEOUT="",
        )
        # env 空字符串 → os.environ.get 返回 "" → falsy → 走默认值 "2"
        cfg = load_redis_config()
        assert cfg["socket_timeout"] == 2.0
        assert cfg["socket_connect_timeout"] == 2.0


class TestLoadRedisConfigFailClosed:
    """fail-closed：缺关键配置抛 RedisConfigError。"""

    def test_fail_closed_without_host(self, monkeypatch):
        _set_env(monkeypatch, REDIS_HOST="", REDIS_PASSWORD="pw")
        with pytest.raises(RedisConfigError):
            load_redis_config()

    def test_fail_closed_without_password(self, monkeypatch):
        _set_env(monkeypatch, REDIS_HOST="127.0.0.1", REDIS_PASSWORD="")
        with pytest.raises(RedisConfigError):
            load_redis_config()
