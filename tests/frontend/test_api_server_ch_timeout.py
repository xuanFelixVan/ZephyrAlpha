# [MODULE] tests.frontend.test_api_server_ch_timeout
# [DOMAIN] D_FRONTEND
# [TTL] permanent
"""T6 验收单测：_ch_exec 必须向 clickhouse Client.execute 传递查询级超时 settings。

背景：09-03 socket 级 send_receive_timeout 在"服务端慢查询但连接未断"场景失效，
线程池被慢查询占满——补 settings.max_execution_time 服务端主动中断（legacy-clear T6）。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import zephyr.frontend.dashboard.api_server as api_server  # noqa: E402


def test_ch_exec_passes_max_execution_time(monkeypatch):
    """_ch_exec 必须传 settings={'max_execution_time': N}，N 为正整数。"""
    captured = {}

    fake_client = MagicMock()

    def _execute(sql, params=None, settings=None):
        captured["sql"] = sql
        captured["params"] = params
        captured["settings"] = settings
        return []

    fake_client.execute = _execute
    monkeypatch.setattr(api_server, "_client", fake_client)

    rows = api_server._ch_exec("SELECT 1", {"k": "v"})
    assert rows == []
    assert captured["sql"] == "SELECT 1"
    assert captured["params"] == {"k": "v"}
    settings = captured["settings"] or {}
    n = settings.get("max_execution_time")
    assert isinstance(n, int) and 5 <= n <= 30, f"max_execution_time 异常: {n!r}"


def test_ch_exec_discards_client_on_error(monkeypatch):
    """查询异常必须弃连（_client 置 None）触发下一位调用者重建自愈。"""
    fake_client = MagicMock()

    def _execute(*a, **k):
        raise RuntimeError("simulated hang/timeout")

    fake_client.execute = _execute
    monkeypatch.setattr(api_server, "_client", fake_client)

    try:
        api_server._ch_exec("SELECT 1")
    except RuntimeError:
        pass
    else:
        raise AssertionError("异常应向上抛（端点级降级 ok:false 依赖）")
    assert api_server._client is None  # 弃连自愈
