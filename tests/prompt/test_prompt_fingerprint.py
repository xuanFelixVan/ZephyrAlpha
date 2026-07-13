# [A_test] module_id: SRC-TST-1405 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_prompt_fingerprint
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.prompt_fingerprint
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_prompt_fingerprint.py
# [TTL] task_bound

import hashlib

import pytest

from zephyr.feedback_loop.diagnosers.reliability.prompt_fingerprint import PromptFingerprint


class TestPromptFingerprintInstantiation:
    def test_default_instantiation(self):
        fp = PromptFingerprint(prompt_id="p-001")
        assert fp.prompt_id == "p-001"
        assert fp.content_hash == ""

    def test_instantiation_with_hash(self):
        fp = PromptFingerprint(prompt_id="p-002", content_hash="abc123")
        assert fp.content_hash == "abc123"


class TestFromContent:
    def test_from_content_produces_sha256(self):
        content = "hello world"
        expected = hashlib.sha256(content.encode()).hexdigest()
        fp = PromptFingerprint.from_content(prompt_id="p-003", content=content)
        assert fp.prompt_id == "p-003"
        assert fp.content_hash == expected

    def test_from_content_deterministic(self):
        fp1 = PromptFingerprint.from_content(prompt_id="p-004", content="same text")
        fp2 = PromptFingerprint.from_content(prompt_id="p-005", content="same text")
        assert fp1.content_hash == fp2.content_hash

    def test_from_content_different_content_different_hash(self):
        fp_a = PromptFingerprint.from_content(prompt_id="p-006", content="alpha")
        fp_b = PromptFingerprint.from_content(prompt_id="p-007", content="beta")
        assert fp_a.content_hash != fp_b.content_hash

    def test_from_content_empty_string(self):
        fp = PromptFingerprint.from_content(prompt_id="p-008", content="")
        expected = hashlib.sha256(b"").hexdigest()
        assert fp.content_hash == expected

    def test_from_content_unicode(self):
        content = "中文测试 🚀"
        expected = hashlib.sha256(content.encode()).hexdigest()
        fp = PromptFingerprint.from_content(prompt_id="p-009", content=content)
        assert fp.content_hash == expected


class TestPromptFingerprintBoundaries:
    def test_none_prompt_id_accepted_by_dataclass(self):
        fp = PromptFingerprint(prompt_id=None)
        assert fp.prompt_id is None

    def test_from_content_none_content_raises(self):
        with pytest.raises(AttributeError):
            PromptFingerprint.from_content(prompt_id="p-010", content=None)

    def test_hash_length_is_64_chars(self):
        fp = PromptFingerprint.from_content(prompt_id="p-011", content="x")
        assert len(fp.content_hash) == 64
