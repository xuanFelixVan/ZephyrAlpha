# [A_test] module_id: SRC-TST-1539 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_secret_rotation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.security.secret_rotation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_secret_rotation.py
# [TTL] task_bound

import time

import pytest

from zephyr.feedback_loop.security.secret_rotation import (
    SecretEntry,
    SecretRotation,
)


class TestSecretRotationInstantiation:
    def test_default_instantiation(self):
        sr = SecretRotation()
        assert sr.secrets == {}


class TestRegister:
    def test_register_secret(self):
        sr = SecretRotation()
        entry = sr.register("db-password", "postgres", interval_days=30)
        assert entry.secret_id == "db-password"
        assert entry.service_name == "postgres"
        assert entry.rotation_interval_days == 30
        assert "db-password" in sr.secrets

    def test_register_default_interval(self):
        sr = SecretRotation()
        entry = sr.register("api-key", "external-api")
        assert entry.rotation_interval_days == 90


class TestRotate:
    def test_rotate_existing_secret(self):
        sr = SecretRotation()
        sr.register("db-password", "postgres")
        new_secret = sr.rotate("db-password")
        assert isinstance(new_secret, str)
        assert len(new_secret) == 64

    def test_rotate_updates_hash(self):
        sr = SecretRotation()
        sr.register("db-password", "postgres")
        sr.rotate("db-password")
        assert sr.secrets["db-password"].current_hash != ""

    def test_rotate_unknown_raises_keyerror(self):
        sr = SecretRotation()
        with pytest.raises(KeyError):
            sr.rotate("nonexistent")


class TestPendingRotations:
    def test_no_pending(self):
        sr = SecretRotation()
        sr.register("fresh-key", "svc", interval_days=9999)
        assert sr.pending_rotations() == []

    def test_pending_rotation(self):
        sr = SecretRotation()
        entry = sr.register("old-key", "svc", interval_days=0)
        entry.last_rotated = 0
        pending = sr.pending_rotations()
        assert "old-key" in pending


class TestSecretEntry:
    def test_days_since_rotation(self):
        entry = SecretEntry(
            secret_id="s1",
            service_name="svc",
            last_rotated=time.time() - 86400,
        )
        assert entry.days_since_rotation >= 1.0

    def test_needs_rotation(self):
        entry = SecretEntry(
            secret_id="s1",
            service_name="svc",
            last_rotated=0,
            rotation_interval_days=1,
        )
        assert entry.needs_rotation is True

    def test_no_rotation_needed(self):
        entry = SecretEntry(
            secret_id="s1",
            service_name="svc",
            last_rotated=time.time(),
            rotation_interval_days=90,
        )
        assert entry.needs_rotation is False
