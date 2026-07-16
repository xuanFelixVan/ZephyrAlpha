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
    """测试_trigger的重要文件检测逻辑"""

    def test_important_prefix_src_triggers(self, reconciler_module, tmp_path):
        """src/下文件变更应触发"""
        committed = [str(tmp_path / "src" / "zephyr" / "foo.py")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            with patch.object(reconciler_module, "_load_state", return_value={}):
                assert reconciler_module._trigger(committed) is True

    def test_important_prefix_config_triggers(self, reconciler_module, tmp_path):
        """config/下文件变更应触发"""
        committed = [str(tmp_path / "config" / "sla_targets.yaml")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            with patch.object(reconciler_module, "_load_state", return_value={}):
                assert reconciler_module._trigger(committed) is True

    def test_important_file_AGENTS_md_triggers(self, reconciler_module, tmp_path):
        """AGENTS.md变更应触发"""
        committed = [str(tmp_path / "AGENTS.md")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            with patch.object(reconciler_module, "_load_state", return_value={}):
                assert reconciler_module._trigger(committed) is True

    def test_non_important_file_does_not_trigger(self, reconciler_module, tmp_path):
        """logs/下文件变更不应触发"""
        committed = [str(tmp_path / "logs" / "app.log")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            assert reconciler_module._trigger(committed) is False

    def test_aidrafts_does_not_trigger(self, reconciler_module, tmp_path):
        """.aidrafts/下文件变更不应触发（临时草稿）"""
        committed = [str(tmp_path / ".aidrafts" / "sess-123" / "foo.py")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            assert reconciler_module._trigger(committed) is False


class TestTriggerIntervalProtection:
    """测试_trigger的8小时间隔保护逻辑"""

    def test_recent_backup_blocks_trigger(self, reconciler_module, tmp_path):
        """距上次备份<8h应阻断触发"""
        recent_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        state = {"last_backup_time": recent_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            with patch.object(reconciler_module, "_load_state", return_value=state):
                assert reconciler_module._trigger(committed) is False

    def test_old_backup_allows_trigger(self, reconciler_module, tmp_path):
        """距上次备份≥8h应允许触发"""
        old_time = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        state = {"last_backup_time": old_time}
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            with patch.object(reconciler_module, "_load_state", return_value=state):
                assert reconciler_module._trigger(committed) is True

    def test_no_state_allows_trigger(self, reconciler_module, tmp_path):
        """无状态文件（首次备份）应允许触发"""
        committed = [str(tmp_path / "src" / "foo.py")]
        with patch.object(reconciler_module, "_project_root", tmp_path):
            with patch.object(reconciler_module, "_load_state", return_value={}):
                assert reconciler_module._trigger(committed) is True


class TestStatePersistence:
    """测试状态文件持久化（INV-10）"""

    def test_load_state_returns_empty_when_no_file(self, reconciler_module, tmp_path):
        """状态文件不存在时返回空dict"""
        with patch.object(reconciler_module, "_STATE_FILE", tmp_path / "nonexistent.json"):
            assert reconciler_module._load_state() == {}

    def test_load_state_returns_dict_when_file_exists(self, reconciler_module, tmp_path):
        """状态文件存在时返回解析后的dict"""
        state_file = tmp_path / "backup_state.json"
        state_file.write_text(json.dumps({"last_backup_time": "2026-07-09T10:00:00+00:00"}), encoding="utf-8")
        with patch.object(reconciler_module, "_STATE_FILE", state_file):
            state = reconciler_module._load_state()
            assert state["last_backup_time"] == "2026-07-09T10:00:00+00:00"

    def test_update_state_writes_file(self, reconciler_module, tmp_path):
        """_update_state应写入状态文件"""
        state_file = tmp_path / "backup_state.json"
        with patch.object(reconciler_module, "_STATE_FILE", state_file):
            reconciler_module._update_state(last_backup_time="2026-07-09T10:00:00+00:00")
            state = json.loads(state_file.read_text(encoding="utf-8"))
            assert state["last_backup_time"] == "2026-07-09T10:00:00+00:00"
