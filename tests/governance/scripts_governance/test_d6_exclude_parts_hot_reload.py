# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_git_dangerous.py | §
# [TTL] permanent
"""W9（st-regfix-laneB-20260922）：d6 双探测器 EXCLUDE_PATH_PARTS 热加载契约。

失效键=模块自身文件 (mtime_ns, size)；import 态文件变更即 reload；`__main__`
形态（CLI/runpy）禁 reload（reload(__main__) 会重入 main()）。本测试不写生产
文件——文件变更以假 Path.stat + 假 importlib.reload 模拟，只验访问器契约。
"""

from __future__ import annotations

import importlib
import types
from pathlib import Path as _RealPath

import pytest

_DETECTOR_MODULES = [
    "scripts.governance.d6_security.detect_git_dangerous",
    "scripts.governance.d6_security.detect_shell_dangerous",
]


@pytest.fixture(params=_DETECTOR_MODULES)
def detector(request):
    return importlib.import_module(request.param)


def test_first_call_records_sig_and_returns_constant(detector):
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS
    assert detector._EXCLUDE_PARTS_SIG is not None


def test_unchanged_sig_returns_constant_without_reload(detector, monkeypatch):
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS
    sig = detector._EXCLUDE_PARTS_SIG

    def _fail_reload(_mod):  # pragma: no cover - 命中即失败
        raise AssertionError("sig 未变不得 reload")

    monkeypatch.setattr(detector.importlib, "reload", _fail_reload)
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS
    assert sig == detector._EXCLUDE_PARTS_SIG


def test_changed_sig_triggers_reload_in_import_mode(detector, monkeypatch):
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS
    old_sig = detector._EXCLUDE_PARTS_SIG
    new_sig = (old_sig[0] + 1_000_000, old_sig[1] + 7)

    class _FakePath:
        def __init__(self, *_a, **_k):
            pass

        def stat(self):
            return types.SimpleNamespace(st_mtime_ns=new_sig[0], st_size=new_sig[1])

    reloaded = []

    def _fake_reload(_mod):
        reloaded.append(True)
        return types.SimpleNamespace(EXCLUDE_PATH_PARTS=detector.EXCLUDE_PATH_PARTS + ("zzz/injected/by/test/",))

    monkeypatch.setattr(detector, "Path", _FakePath)
    monkeypatch.setattr(detector.importlib, "reload", _fake_reload)
    got = detector._get_exclude_path_parts()
    assert reloaded == [True]
    assert got[-1] == "zzz/injected/by/test/"
    assert new_sig == detector._EXCLUDE_PARTS_SIG


def test_main_mode_never_reloads(detector, monkeypatch):
    """runpy/CLI 形态（__name__=='__main__'）禁 reload——reload(__main__) 会重入 main()。"""
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS
    old_sig = detector._EXCLUDE_PARTS_SIG

    class _FakePath:
        def __init__(self, *_a, **_k):
            pass

        def stat(self):
            return types.SimpleNamespace(st_mtime_ns=old_sig[0] + 1, st_size=old_sig[1])

    def _fail_reload(_mod):  # pragma: no cover - 命中即失败
        raise AssertionError("__main__ 形态不得 reload")

    monkeypatch.setattr(detector, "__name__", "__main__")
    monkeypatch.setattr(detector, "Path", _FakePath)
    monkeypatch.setattr(detector.importlib, "reload", _fail_reload)
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS


def test_stat_failure_fails_open_to_current_list(detector, monkeypatch):
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS

    class _BoomPath:
        def __init__(self, *_a, **_k):
            pass

        def stat(self):
            raise OSError("no such file")

    monkeypatch.setattr(detector, "Path", _BoomPath)
    # 宁可多扫不漏扫：stat 失败返回当前清单（红线语义不变）
    assert detector._get_exclude_path_parts() == detector.EXCLUDE_PATH_PARTS


def test_accessors_are_wired_into_scan_paths(detector):
    """scan_files/scan_repo 必须走热加载访问器，不得直引冻结常量。"""
    import inspect

    for fn_name in ("scan_files", "scan_repo"):
        src = inspect.getsource(getattr(detector, fn_name))
        assert "_get_exclude_path_parts()" in src, f"{detector.__name__}.{fn_name} 未接热加载访问器"
        assert "EXCLUDE_PATH_PARTS" not in src.replace("_get_exclude_path_parts", "")
