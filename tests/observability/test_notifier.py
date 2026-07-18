# [A_test] module_id: SRC-TST-1315 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-410 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_notifier
# [INVARIANTS] Notifier.notify返回Notification; disabled config→no file write; critical always saved
# [MODIFY-GUARD] 仅当notifier公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_notifier.py -q
# [TTL] task_bound

import json

from zephyr.infrastructure.observability.notifier import (
    Notification,
    NotificationChannel,
    NotificationLevel,
    Notifier,
    NotifyConfig,
)


class TestNotifierInstantiation:
    def test_default_instantiation(self):
        n = Notifier()
        assert n is not None

    def test_instantiation_with_output_dir(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        assert n is not None

    def test_instantiation_with_none_dir(self):
        n = Notifier(output_dir=None)
        assert n is not None


class TestNotifierNotify:
    def test_notify_returns_notification(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.INFO, "Test Title", "Test message")
        assert isinstance(result, Notification)

    def test_notify_sets_level(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.WARNING, "Warn Title", "Warn msg")
        assert result.level == NotificationLevel.WARNING

    def test_notify_sets_title(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.INFO, "My Title", "msg")
        assert result.title == "My Title"

    def test_notify_sets_message(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.INFO, "Title", "My message content")
        assert result.message == "My message content"

    def test_notify_sets_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.INFO, "Title", "msg", task_id="TASK-001")
        assert result.task_id == "TASK-001"

    def test_notify_default_task_id_empty(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.INFO, "Title", "msg")
        assert result.task_id == ""

    def test_notify_generates_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify(NotificationLevel.INFO, "Title", "msg")
        assert result.notification_id.startswith("NOTIF-")

    def test_notify_saves_file(self, tmp_path):
        output_dir = tmp_path / "notifs"
        n = Notifier(output_dir=output_dir)
        result = n.notify(NotificationLevel.INFO, "Title", "msg")
        file_path = output_dir / f"{result.notification_id}.json"
        assert file_path.exists()

    def test_notify_file_content(self, tmp_path):
        output_dir = tmp_path / "notifs"
        n = Notifier(output_dir=output_dir)
        result = n.notify(NotificationLevel.CRITICAL, "Alert", "Something bad", task_id="T-001")
        file_path = output_dir / f"{result.notification_id}.json"
        data = json.loads(file_path.read_text(encoding="utf-8"))
        assert data["level"] == "critical"
        assert data["title"] == "Alert"
        assert data["message"] == "Something bad"
        assert data["task_id"] == "T-001"

    def test_notify_disabled_config(self, tmp_path):
        output_dir = tmp_path / "notifs"
        n = Notifier(output_dir=output_dir)
        n._config.enabled = False
        result = n.notify(NotificationLevel.INFO, "Title", "msg")
        assert isinstance(result, Notification)
        assert not output_dir.exists()

    def test_notify_increment_count(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        n.notify(NotificationLevel.INFO, "T1", "m1")
        n.notify(NotificationLevel.INFO, "T2", "m2")
        assert n._notification_count == 2

    def test_notify_creates_output_dir(self, tmp_path):
        output_dir = tmp_path / "deep" / "nested" / "notifs"
        n = Notifier(output_dir=output_dir)
        n.notify(NotificationLevel.INFO, "Title", "msg")
        assert output_dir.exists()


class TestNotifierNotifyCompletion:
    def test_notify_completion_returns_notification(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_completion("TASK-001", "All done")
        assert isinstance(result, Notification)

    def test_notify_completion_level_is_info(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_completion("TASK-001", "All done")
        assert result.level == NotificationLevel.INFO

    def test_notify_completion_title_contains_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_completion("TASK-042", "Summary")
        assert "TASK-042" in result.title

    def test_notify_completion_message_is_summary(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_completion("TASK-001", "Build completed successfully")
        assert result.message == "Build completed successfully"

    def test_notify_completion_sets_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_completion("TASK-001", "Done")
        assert result.task_id == "TASK-001"


class TestNotifierNotifyFailure:
    def test_notify_failure_returns_notification(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_failure("TASK-001", "Build failed")
        assert isinstance(result, Notification)

    def test_notify_failure_level_is_critical(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_failure("TASK-001", "Error")
        assert result.level == NotificationLevel.CRITICAL

    def test_notify_failure_title_contains_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_failure("TASK-099", "Error msg")
        assert "TASK-099" in result.title

    def test_notify_failure_message_is_error(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_failure("TASK-001", "SyntaxError on line 42")
        assert result.message == "SyntaxError on line 42"

    def test_notify_failure_sets_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_failure("TASK-001", "Error")
        assert result.task_id == "TASK-001"


class TestNotifierNotifyOwnerAttention:
    def test_notify_owner_attention_returns_notification(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_owner_attention("TASK-001", "Needs review")
        assert isinstance(result, Notification)

    def test_notify_owner_attention_level_is_warning(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_owner_attention("TASK-001", "Needs review")
        assert result.level == NotificationLevel.WARNING

    def test_notify_owner_attention_title_contains_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_owner_attention("TASK-007", "Check this")
        assert "TASK-007" in result.title

    def test_notify_owner_attention_message_contains_reason(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_owner_attention("TASK-001", "Budget exceeded")
        assert "Budget exceeded" in result.message

    def test_notify_owner_attention_sets_task_id(self, tmp_path):
        n = Notifier(output_dir=tmp_path / "notifs")
        result = n.notify_owner_attention("TASK-001", "Reason")
        assert result.task_id == "TASK-001"


class TestNotification:
    def test_construction(self):
        n = Notification(
            notification_id="NOTIF-001",
            level=NotificationLevel.INFO,
            title="Test",
            message="Test message",
        )
        assert n.notification_id == "NOTIF-001"
        assert n.level == NotificationLevel.INFO
        assert n.title == "Test"
        assert n.message == "Test message"
        assert n.task_id == ""
        assert n.channel == NotificationChannel.CONSOLE

    def test_with_task_id(self):
        n = Notification(
            notification_id="NOTIF-002",
            level=NotificationLevel.CRITICAL,
            title="Alert",
            message="msg",
            task_id="T-001",
        )
        assert n.task_id == "T-001"

    def test_timestamp_auto_generated(self):
        n = Notification(
            notification_id="NOTIF-003",
            level=NotificationLevel.INFO,
            title="T",
            message="m",
        )
        assert len(n.timestamp_utc) > 0


class TestNotifyConfig:
    def test_default_construction(self):
        config = NotifyConfig()
        assert config.enabled is True
        assert config.min_level == NotificationLevel.INFO
        assert config.rate_limit_per_minute == 30

    def test_custom_construction(self):
        config = NotifyConfig(enabled=False, min_level=NotificationLevel.CRITICAL, rate_limit_per_minute=10)
        assert config.enabled is False
        assert config.min_level == NotificationLevel.CRITICAL
        assert config.rate_limit_per_minute == 10


class TestNotificationLevel:
    def test_values(self):
        assert NotificationLevel.INFO.value == "info"
        assert NotificationLevel.WARNING.value == "warning"
        assert NotificationLevel.CRITICAL.value == "critical"


class TestNotificationChannel:
    def test_values(self):
        assert NotificationChannel.FILE.value == "file"
        assert NotificationChannel.CONSOLE.value == "console"
