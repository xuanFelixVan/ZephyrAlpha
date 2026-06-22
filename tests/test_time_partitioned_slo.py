# [A_test] module_id: SRC-TST-1742 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md | §test
# [MODULE] tests.test_time_partitioned_slo
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_time_partitioned_slo.py

from datetime import datetime
from unittest.mock import patch

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.time_partitioned_slo", reason="time_partitioned_slo not available"
)
TimePartitionedSLO = mod.TimePartitionedSLO


class TestTimePartitionedSLO:
    def test_instantiation(self):
        tps = TimePartitionedSLO()
        assert "peak" in tps.PARTITIONS
        assert "off_peak" in tps.PARTITIONS

    def test_current_partition_peak(self):
        tps = TimePartitionedSLO()
        with patch("zephyr.ops.capacity_assurance.time_partitioned_slo.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 14, 0, 0)
            assert tps.current_partition() == "peak"

    def test_current_partition_off_peak(self):
        tps = TimePartitionedSLO()
        with patch("zephyr.ops.capacity_assurance.time_partitioned_slo.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 23, 0, 0)
            assert tps.current_partition() == "off_peak"

    def test_get_target_peak(self):
        tps = TimePartitionedSLO()
        with patch("zephyr.ops.capacity_assurance.time_partitioned_slo.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 10, 0, 0)
            assert tps.get_target() == 0.999

    def test_get_target_off_peak(self):
        tps = TimePartitionedSLO()
        with patch("zephyr.ops.capacity_assurance.time_partitioned_slo.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 23, 0, 0)
            assert tps.get_target() == 0.99

    def test_get_all_partitions(self):
        tps = TimePartitionedSLO()
        all_p = tps.get_all_partitions()
        assert all_p["peak"] == 0.999
        assert all_p["off_peak"] == 0.99

    def test_partition_definitions(self):
        assert TimePartitionedSLO.PARTITIONS["peak"]["start"] == 9
        assert TimePartitionedSLO.PARTITIONS["peak"]["end"] == 22
