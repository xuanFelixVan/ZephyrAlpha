# [TTL] permanent
"""flags.py 三态读失败改造测试（st-chiefc-20261009 G-5）。

三态契约：真ON/真OFF=装载成功落闩；读失败（缺册/解析异常）不落闩+点名。
能红证据：①解析瞬断一次→异常传播且不落闩（恢复后重装成功——旧实现此处=整程失明）；
②缺册→点名（caplog error）+返回 0+不落闩；③正常装载落闩幂等。
"""

from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))  # noqa: E402

import zephyr.shared.foundation.flags as flags_mod  # noqa: E402


@pytest.fixture()
def fresh_flags(monkeypatch):
    """原地换空注册表+清落闩（monkeypatch 自动还原，禁 reload——reload 会产生模块实例
    漂移污染同进程后续测试，2026-10-09 组合跑实测）。"""
    fresh_reg = flags_mod.FlagRegistry()
    monkeypatch.setattr(flags_mod, "global_flag_registry", fresh_reg)
    monkeypatch.setattr(flags_mod, "_global_flags_loaded", False)
    yield flags_mod


def test_normal_load_latches_and_is_idempotent(fresh_flags, monkeypatch, tmp_path):
    """真ON 态：装载成功落闩，二次调用幂等。"""
    import yaml

    fm = fresh_flags
    yml = tmp_path / "flags.yaml"
    yml.write_text(
        yaml.safe_dump({"flags": {"my_flag_a": {"enabled": True}, "my_flag_b": {"enabled": False}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(fm, "_default_flags_yaml_path", lambda: yml)
    n = fm.ensure_global_flags_loaded()
    assert n == 2
    assert fm.global_flag_registry.is_enabled("my_flag_a") is True
    assert fm.global_flag_registry.is_enabled("my_flag_b") is False
    # 落闩：二次调用不再读文件（改坏文件也不影响已落闩态）
    yml.write_text("flags: [broken", encoding="utf-8")
    assert fm.ensure_global_flags_loaded() == 2


def test_parse_failure_propagates_and_not_latched(fresh_flags, monkeypatch, tmp_path):
    """读失败三态之三：解析瞬断→异常传播+不落闩；恢复后下次调用重装成功。

    能红对照（旧实现）：先置 loaded=True 再加载→瞬断后本进程永闭（空册失明），
    本测试的「恢复后重装」断言在旧实现下必红。
    """
    import yaml

    fm = fresh_flags
    yml = tmp_path / "flags.yaml"
    yml.write_text("flags: [broken", encoding="utf-8")
    monkeypatch.setattr(fm, "_default_flags_yaml_path", lambda: yml)
    with pytest.raises(yaml.YAMLError):
        fm.ensure_global_flags_loaded()
    assert fm._global_flags_loaded is False, "读失败不得落闩（旧实现此处=True=整程失明根因）"
    # 瞬断恢复：修好文件后重装成功
    yml.write_text(yaml.safe_dump({"flags": {"recovered": {"enabled": True}}}), encoding="utf-8")
    assert fm.ensure_global_flags_loaded() == 1
    assert fm.global_flag_registry.is_enabled("recovered") is True


def test_missing_file_named_loudly_and_not_latched(fresh_flags, monkeypatch, tmp_path, caplog):
    """缺册→error 点名（caplog 可见）+返回 0+不落闩（下次调用重试）。"""
    fm = fresh_flags
    monkeypatch.setattr(fm, "_default_flags_yaml_path", lambda: tmp_path / "nope.yaml")
    with caplog.at_level(logging.ERROR, logger=fm.logger.name):
        n = fm.ensure_global_flags_loaded()
    assert n == 0
    assert fm._global_flags_loaded is False
    assert any("MISSING" in r.message for r in caplog.records), "缺册必须点名（防静默全 OFF）"


def test_missing_then_appears_recovers(fresh_flags, monkeypatch, tmp_path):
    """缺册→出现→自动重装（读失败态可自愈）。"""
    import yaml

    fm = fresh_flags
    yml = tmp_path / "late.yaml"
    monkeypatch.setattr(fm, "_default_flags_yaml_path", lambda: yml)
    assert fm.ensure_global_flags_loaded() == 0
    yml.write_text(yaml.safe_dump({"flags": {"late_flag": {"enabled": True}}}), encoding="utf-8")
    assert fm.ensure_global_flags_loaded() == 1
    assert fm.global_flag_registry.is_enabled("late_flag") is True


def test_real_flags_yaml_loads_and_commit_queue_flag_on(monkeypatch):
    """真册口径：本仓 config/flags.yaml 可装载且 commit_queue_interactive=ON（只钉关键旗不钉数量）。"""
    monkeypatch.setattr(flags_mod, "_global_flags_loaded", False)
    flags_mod.ensure_global_flags_loaded()
    assert flags_mod.global_flag_registry.is_enabled("commit_queue_interactive") is True
