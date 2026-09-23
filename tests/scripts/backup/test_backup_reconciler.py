# tests/scripts/backup/test_backup_reconciler.py
"""backup_reconciler单元测试——验证触发条件与间隔保护逻辑。

测试覆盖蓝图INV-08/INV-09/INV-10：
- INV-08: post-commit reconciler触发，非时间触发
- INV-09: 双条件触发（重要文件变更 + 8h间隔）
- INV-10: 状态持久化到backup_state.json
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def temp_state_file(tmp_path):
    """临时状态文件fixture"""
    state_file = tmp_path / "backup_state.json"
    return state_file


@pytest.fixture
def reconciler_module(tmp_path, monkeypatch):
    """导入backup_reconciler模块，patch项目根路径"""
    import sys

    # 将scripts/backup加入sys.path
    backup_dir = Path(__file__).parent.parent.parent.parent / "scripts" / "backup"
    monkeypatch.syspath_prepend(str(backup_dir))
    import backup_reconciler

    return backup_reconciler


class TestTriggerImportantFiles:
    """测试trigger的重要文件检测逻辑"""

    def test_important_prefix_src_triggers(self, reconciler_module, tmp_path):
        """src/下文件变更应触发"""
        committed = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_important_prefix_config_triggers(self, reconciler_module, tmp_path):
        """config/下文件变更应触发"""
        committed = [str(tmp_path / "config" / "sla_targets.yaml")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_important_file_AGENTS_md_triggers(self, reconciler_module, tmp_path):
        """AGENTS.md变更应触发"""
        committed = [str(tmp_path / "AGENTS.md")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True

    def test_non_important_file_does_not_trigger(self, reconciler_module, tmp_path):
        """logs/下文件变更不应触发"""
        committed = [str(tmp_path / "logs" / "app.log")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            assert reconciler_module.trigger(committed) is False

    def test_aidrafts_does_not_trigger(self, reconciler_module, tmp_path):
        """.aidrafts/下文件变更不应触发（临时草稿）"""
        committed = [str(tmp_path / ".aidrafts" / "sess-123" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            assert reconciler_module.trigger(committed) is False


class TestTriggerIntervalProtection:
    """测试trigger的8小时间隔保护逻辑"""

    def test_recent_backup_blocks_trigger(self, reconciler_module, tmp_path):
        """距上次备份<8h应阻断触发"""
        recent_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state = {"last_backup_time": recent_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value=state):
                assert reconciler_module.trigger(committed) is False

    def test_old_backup_allows_trigger(self, reconciler_module, tmp_path):
        """距上次备份≥8h应允许触发"""
        old_time = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        state = {"last_backup_time": old_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value=state):
                assert reconciler_module.trigger(committed) is True

    def test_no_state_allows_trigger(self, reconciler_module, tmp_path):
        """无状态文件（首次备份）应允许触发"""
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
            with patch.object(reconciler_module, "load_state", return_value={}):
                assert reconciler_module.trigger(committed) is True


class TestTriggerYamlWiring:
    """测试 trigger() 从 YAML 读取触发参数（F-06 Track A 治本）

    验证 trigger 调用 load_config() 读取 trigger.important_prefixes /
    trigger.important_files / trigger.min_interval_seconds，而非硬编码常量。
    """

    def test_trigger_reads_custom_prefixes_from_yaml(self, reconciler_module, tmp_path):
        """trigger 应从 YAML 读取自定义 important_prefixes"""
        # YAML 配置自定义前缀（不含 src/，含 custom/）
        fake_config = {"trigger": {"important_prefixes": ["custom/"], "important_files": []}}
        committed_custom = [str(tmp_path / "custom" / "foo.py")]
        committed_src = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "load_config", return_value=fake_config):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                with patch.object(reconciler_module, "load_state", return_value={}):
                    # custom/ 在 YAML 中 -> 触发
                    assert reconciler_module.trigger(committed_custom) is True
                    # src/ 不在 YAML 中 -> 不触发
                    assert reconciler_module.trigger(committed_src) is False

    def test_trigger_reads_custom_min_interval_from_yaml(self, reconciler_module, tmp_path):
        """trigger 应从 YAML 读取自定义 min_interval_seconds"""
        # YAML 配置 1 秒间隔（远小于默认 8 小时）
        fake_config = {"trigger": {"min_interval_seconds": 1}}
        recent_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state = {"last_backup_time": recent_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "load_config", return_value=fake_config):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                with patch.object(reconciler_module, "load_state", return_value=state):
                    # 2 小前备份，但 YAML 设 1 秒间隔 -> 允许触发
                    assert reconciler_module.trigger(committed) is True

    def test_trigger_falls_back_to_defaults_when_yaml_empty(self, reconciler_module, tmp_path):
        """YAML 为空时 fallback 到硬编码常量"""
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "load_config", return_value={}):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                with patch.object(reconciler_module, "load_state", return_value={}):
                    # 硬编码 IMPORTANT_PREFIXES 含 src/ -> 触发
                    assert reconciler_module.trigger(committed) is True


class TestStatePersistence:
    """测试状态文件持久化（INV-10）

    F-06 Track A（2026-07-17）：load_state/update_state 通过 get_state_file() 读取
    backup_config.yaml §trigger.state_file，fallback 到 STATE_FILE。测试 patch
    get_state_file 以隔离 YAML 依赖。
    """

    def test_load_state_returns_empty_when_no_file(self, reconciler_module, tmp_path):
        """状态文件不存在时返回空dict"""
        with patch.object(reconciler_module, "get_state_file", return_value=tmp_path / "nonexistent.json"):
            assert reconciler_module.load_state() == {}

    def test_load_state_returns_dict_when_file_exists(self, reconciler_module, tmp_path):
        """状态文件存在时返回解析后的dict"""
        state_file = tmp_path / "backup_state.json"
        state_file.write_text(json.dumps({"last_backup_time": "2026-07-09T10:00:00+00:00"}), encoding="utf-8")
        with patch.object(reconciler_module, "get_state_file", return_value=state_file):
            state = reconciler_module.load_state()
            assert state["last_backup_time"] == "2026-07-09T10:00:00+00:00"

    def test_update_state_writes_file(self, reconciler_module, tmp_path):
        """update_state应写入状态文件"""
        state_file = tmp_path / "backup_state.json"
        with patch.object(reconciler_module, "get_state_file", return_value=state_file):
            reconciler_module.update_state(last_backup_time="2026-07-09T10:00:00+00:00")
            state = json.loads(state_file.read_text(encoding="utf-8"))
            assert state["last_backup_time"] == "2026-07-09T10:00:00+00:00"


class TestGetStateFileYamlWiring:
    """测试 get_state_file() 从 YAML 读取 state_file（F-06 Track A 治本）"""

    def test_get_state_file_reads_from_yaml(self, reconciler_module, tmp_path):
        """get_state_file 应从 YAML trigger.state_file 读取路径"""
        fake_config = {"trigger": {"state_file": "custom/path/state.json"}}
        with patch.object(reconciler_module, "load_config", return_value=fake_config):
            with patch.object(reconciler_module, "PROJECT_ROOT", tmp_path):
                result = reconciler_module.get_state_file()
                assert result == tmp_path / "custom" / "path" / "state.json"

    def test_get_state_file_falls_back_to_constant(self, reconciler_module, tmp_path):
        """YAML 缺失 state_file 时 fallback 到 STATE_FILE"""
        with patch.object(reconciler_module, "load_config", return_value={}):
            with patch.object(reconciler_module, "STATE_FILE", tmp_path / "fallback.json"):
                result = reconciler_module.get_state_file()
                assert result == tmp_path / "fallback.json"

    def test_get_state_file_falls_back_when_config_none(self, reconciler_module, tmp_path):
        """load_config 返回 None 时 fallback 到 STATE_FILE"""
        with patch.object(reconciler_module, "load_config", return_value=None):
            with patch.object(reconciler_module, "STATE_FILE", tmp_path / "fallback.json"):
                result = reconciler_module.get_state_file()
                assert result == tmp_path / "fallback.json"
