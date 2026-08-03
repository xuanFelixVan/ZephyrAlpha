# [A_test] module_id: MOD-GOV_alternative_path_blocker | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_alternative_path_blocker
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_alternative_path_blocker.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.alternative_path_blocker import BLOCKED_ALTERNATIVES, AlternativePathBlocker


class TestAlternativePathBlockerInit:
    def test_blocked_alternatives_contains_write_file(self):
        assert "write_file" in BLOCKED_ALTERNATIVES
        assert "tee" in BLOCKED_ALTERNATIVES["write_file"]

    def test_blocked_alternatives_contains_execute(self):
        assert "execute" in BLOCKED_ALTERNATIVES
        assert "source" in BLOCKED_ALTERNATIVES["execute"]


class TestDetectAlternative:
    def test_detect_tee_for_write_file(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "tee output.txt") is True

    def test_detect_cat_redirect_for_write_file(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "cat > file.txt") is True

    def test_detect_dd_for_write_file(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "dd of=output.bin") is True

    def test_detect_source_for_execute(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("execute", "source script.sh") is True

    def test_detect_dot_for_execute(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("execute", ". script.sh") is True

    def test_no_alternative_detected_for_clean_command(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "write_file content") is False

    def test_no_alternative_for_unknown_primary(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("unknown_command", "tee file") is False

    def test_case_insensitive_detection(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "TEE output.txt") is True

    def test_partial_match_in_longer_command(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "echo hello | tee /tmp/log") is True


class TestBlockIfDetected:
    def test_block_returns_false_with_message_when_detected(self):
        blocker = AlternativePathBlocker()
        allowed, msg = blocker.block_if_detected("write_file", "tee out.txt")
        assert allowed is False
        assert "Alternative path detected" in msg
        assert "tee out.txt" in msg

    def test_block_returns_true_ok_when_clean(self):
        blocker = AlternativePathBlocker()
        allowed, msg = blocker.block_if_detected("write_file", "write_file data")
        assert allowed is True
        assert msg == "OK"

    def test_block_for_execute_source(self):
        blocker = AlternativePathBlocker()
        allowed, msg = blocker.block_if_detected("execute", "source env.sh")
        assert allowed is False
        assert "source env.sh" in msg

    def test_block_for_unknown_primary_returns_ok(self):
        blocker = AlternativePathBlocker()
        allowed, msg = blocker.block_if_detected("read_file", "cat file.txt")
        assert allowed is True
        assert msg == "OK"


class TestAlternativePathBlockerBoundary:
    def test_empty_actual_command(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "") is False

    def test_empty_primary_command(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("", "tee file") is False

    def test_unicode_in_command(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "tee 数据.txt") is True

    def test_very_long_command_string(self):
        blocker = AlternativePathBlocker()
        long_cmd = "echo " + "x" * 10000 + " | tee output.log"
        assert blocker.detect_alternative("write_file", long_cmd) is True

    def test_dd_of_exact_match(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("write_file", "dd of=disk.img bs=4M") is True

    def test_dot_space_in_execute(self):
        blocker = AlternativePathBlocker()
        assert blocker.detect_alternative("execute", ". ~/.bashrc") is True
