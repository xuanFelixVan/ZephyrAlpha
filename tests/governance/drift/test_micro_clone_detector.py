# [A_test] module_id: SRC-TST-1274 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_micro_clone_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_micro_clone_detector.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.micro_clone_detector import MicroCloneDetector


class TestMicroCloneDetector:
    def test_instantiation(self):
        mcd = MicroCloneDetector()
        assert mcd._NGRAM_SIZE == 3
        assert mcd._MIN_FREQ == 2

    def test_detect_empty(self):
        mcd = MicroCloneDetector()
        assert mcd.detect([]) == []

    def test_detect_too_few_lines(self):
        mcd = MicroCloneDetector()
        assert mcd.detect(["line1", "line2"]) == []

    def test_detect_no_clones(self):
        mcd = MicroCloneDetector()
        lines = [f"unique_line_{i}" for i in range(10)]
        result = mcd.detect(lines)
        assert result == []

    def test_detect_with_clones(self):
        mcd = MicroCloneDetector()
        block = ["    x = 1", "    y = 2", "    z = 3"]
        lines = block + block + ["    a = 4"]
        result = mcd.detect(lines)
        assert len(result) > 0
        assert result[0][1] >= 2

    def test_detect_sorted_by_frequency(self):
        mcd = MicroCloneDetector()
        block_a = ["    x = 1", "    y = 2", "    z = 3"]
        block_b = ["    a = 4", "    b = 5", "    c = 6"]
        lines = block_a + block_a + block_a + block_b + block_b + ["unique"]
        result = mcd.detect(lines)
        if len(result) >= 2:
            assert result[0][1] >= result[1][1]

    def test_detect_max_20_results(self):
        mcd = MicroCloneDetector()
        lines = []
        for i in range(50):
            lines.extend([f"    v = {i % 3}", f"    w = {i % 3}", f"    z = {i % 3}"])
        result = mcd.detect(lines)
        assert len(result) <= 20

    def test_compute_density_zero(self):
        mcd = MicroCloneDetector()
        source = "\n".join([f"unique_line_{i}" for i in range(10)])
        density = mcd.compute_density(source)
        assert density == 0.0

    def test_compute_density_with_clones(self):
        mcd = MicroCloneDetector()
        block = "    x = 1\n    y = 2\n    z = 3"
        source = block + "\n" + block + "\n" + block
        density = mcd.compute_density(source)
        assert density > 0.0

    def test_compute_density_short_source(self):
        mcd = MicroCloneDetector()
        density = mcd.compute_density("x = 1\n")
        assert density == 0.0

    def test_compute_density_empty(self):
        mcd = MicroCloneDetector()
        density = mcd.compute_density("")
        assert density == 0.0
