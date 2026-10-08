# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_fire_grid_gates.py | fire_grid G1 日志收卷门回归（合成目录零 GPU 零 CH）
"""fire_grid._t3series_logs_stale 语义重定性回归（st-govfix-g1-20261007 / F1）。

治 6b3426c398 引入的 fail-open：旧实现探 _HERE.parent 恒不存在→恒判收卷。
本册钉死真源常量 + 全分支语义（真清场/疑似路径漂移 fail-closed/新鲜日志/静默收卷/
零日志/探测异常 fail-closed）+ 注册表 last_activity 交叉判据。
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

GRID_ADAPTER = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam" / "grid_adapter"
if str(GRID_ADAPTER) not in sys.path:
    sys.path.insert(0, str(GRID_ADAPTER))

import fire_grid  # noqa: E402

_REPO = Path(__file__).resolve().parents[3]


def test_true_source_path_pinned():
    """对拍回归核心：日志真源常量钉死 .runtime/tmp/st-t3series-20261006——防路径漂移复发。"""
    assert fire_grid.T3SERIES_LOG_DIR == _REPO / ".runtime" / "tmp" / "st-t3series-20261006"
    assert fire_grid.T3SERIES_STALE_SECONDS == 1800


def test_dir_missing_true_cleanup(monkeypatch, tmp_path):
    """目录缺失 @ 真源 + 会话无近窗活动 = 真清场/从未开工 → stale=True。"""
    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: False)
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path / "nonexistent") is True


def test_dir_missing_but_session_active_fail_closed(monkeypatch, tmp_path):
    """目录缺失但注册表显示会话近窗有真实活动 = 疑似路径漂移/刚起未落日志 → fail-closed。"""
    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: True)
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path / "nonexistent") is False


def test_fresh_log_busy(monkeypatch, tmp_path):
    """日志 30 分钟内有更新（未收卷）→ stale=False，与注册表状态无关。"""
    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: False)
    lg = tmp_path / "t1r_probe.log"
    lg.write_text("x", encoding="utf-8")
    now = time.time()
    os.utime(lg, (now - 60, now - 60))  # 1 分钟前
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path, now=now) is False


def test_silent_log_wrapped(monkeypatch, tmp_path):
    """日志静默 >30 分钟 = 收卷 → stale=True（mtime 主判据，含 keeper.stop 收官形态）。"""
    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: False)
    lg = tmp_path / "t1r_probe.log"
    lg.write_text("x", encoding="utf-8")
    (tmp_path / "keeper.stop").write_text("", encoding="utf-8")
    old = time.time() - 1801
    os.utime(lg, (old, old))
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path, now=time.time()) is True


def test_dir_exists_zero_logs(monkeypatch, tmp_path):
    """目录在但零日志：无近窗活动=stale（无事可等）；有近窗活动=fail-closed。"""
    now = time.time()
    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: False)
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path, now=now) is True
    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: True)
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path, now=now) is False


def test_probe_exception_fail_closed(monkeypatch, tmp_path):
    """探测链任何异常（glob 炸）→ stale=False（fail-closed，沿用原契约）。"""

    def _boom(_self, _pattern):
        raise OSError("boom")

    monkeypatch.setattr(fire_grid, "_t3series_session_recently_active", lambda *a, **k: False)
    import pathlib

    monkeypatch.setattr(pathlib.Path, "glob", _boom)
    assert fire_grid._t3series_logs_stale(log_dir=tmp_path) is False


def test_session_active_uses_last_activity_not_heartbeat(monkeypatch):
    """交叉判据用 last_activity（heartbeat daemon 可孤儿存活不反映真实工作）。"""

    class _Info:
        last_activity = time.time() - 60  # 1 分钟前有真实活动

    class _Reg:
        def __init__(self, project_root=None):
            pass

        def get_session(self, _sid):
            return _Info()

    import zephyr.security.access_control.session_concurrency as sc_mod

    monkeypatch.setattr(sc_mod, "SessionRegistry", _Reg)
    assert fire_grid._t3series_session_recently_active() is True

    _Info.last_activity = time.time() - 3600  # 1 小时前（heartbeat 再新鲜也不算）
    assert fire_grid._t3series_session_recently_active() is False


def test_session_registry_failure_fail_closed(monkeypatch):
    """注册表不可达 → 按在跑（fail-closed，与门语义一致）。"""

    def _boom(*a, **k):
        raise RuntimeError("registry down")

    import zephyr.security.access_control.session_concurrency as sc_mod

    monkeypatch.setattr(sc_mod, "SessionRegistry", _boom)
    assert fire_grid._t3series_session_recently_active() is True


def test_session_unknown_means_inactive(monkeypatch):
    """注册表查无此会话 = 从未开工/已注销 → 非在跑。"""

    class _Reg:
        def __init__(self, project_root=None):
            pass

        def get_session(self, _sid):
            return None

    import zephyr.security.access_control.session_concurrency as sc_mod

    monkeypatch.setattr(sc_mod, "SessionRegistry", _Reg)
    assert fire_grid._t3series_session_recently_active() is False
