# [A_test] module_id: MOD-GOV_fix_pattern_miner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_fix_pattern_miner
# [INVARIANTS] 测试覆盖mine/get_patterns/predict_fix_type;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import os

import pytest

from zephyr.infrastructure.auto_fix_engine.fix_pattern_miner import FixPatternMiner
from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixLevel, FixStatus


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_auto_fix.db")


@pytest.fixture
def miner(tmp_db):
    return FixPatternMiner(db_path=tmp_db)


def _make_action(action_type: str, status: FixStatus, target: str = "t.py", dimension: str = "DIM-X") -> FixAction:
    return FixAction(
        action_type=action_type,
        status=status,
        target=target,
        level=FixLevel.L1_RULE,
        metadata={"dimension": dimension},
    )


class TestFixPatternMinerInstantiation:
    def test_creates_instance_with_default_path(self):
        miner = FixPatternMiner(db_path="data/auto_fix/test_instantiation.db")
        assert miner._db_path == "data/auto_fix/test_instantiation.db"

    def test_creates_db_directory(self, tmp_db):
        FixPatternMiner(db_path=tmp_db)
        assert os.path.isdir(os.path.dirname(tmp_db))

    def test_pattern_cache_initialized(self, miner):
        assert isinstance(miner._pattern_cache, dict)


class TestMine:
    def test_mine_empty_actions(self, miner):
        result = miner.mine([])
        assert result == []

    def test_mine_single_completed_action(self, miner):
        actions = [_make_action("drift_fix", FixStatus.COMPLETED)]
        result = miner.mine(actions)
        assert len(result) == 1
        assert result[0]["action_type"] == "drift_fix"
        assert result[0]["frequency"] == 1
        assert result[0]["success_rate"] == 1.0

    def test_mine_mixed_statuses(self, miner):
        actions = [
            _make_action("drift_fix", FixStatus.COMPLETED),
            _make_action("drift_fix", FixStatus.FAILED),
            _make_action("drift_fix", FixStatus.COMPLETED),
        ]
        result = miner.mine(actions)
        assert len(result) == 1
        assert result[0]["frequency"] == 3
        assert result[0]["success_rate"] == pytest.approx(2 / 3)

    def test_mine_multiple_action_types(self, miner):
        actions = [
            _make_action("drift_fix", FixStatus.COMPLETED),
            _make_action("dep_version_fix", FixStatus.FAILED),
        ]
        result = miner.mine(actions)
        assert len(result) == 2
        types = {r["action_type"] for r in result}
        assert types == {"drift_fix", "dep_version_fix"}

    def test_mine_all_failed(self, miner):
        actions = [_make_action("drift_fix", FixStatus.FAILED)]
        result = miner.mine(actions)
        assert result[0]["success_rate"] == 0.0
        assert result[0]["dimension"] == ""

    def test_mine_dimension_from_succeeded(self, miner):
        actions = [_make_action("drift_fix", FixStatus.COMPLETED, dimension="DIM-DRIFT")]
        result = miner.mine(actions)
        assert result[0]["dimension"] == "DIM-DRIFT"


class TestGetPatterns:
    def test_get_patterns_empty_db(self, miner):
        result = miner.get_patterns()
        assert result == []

    def test_get_patterns_after_mine(self, miner):
        miner.mine([_make_action("drift_fix", FixStatus.COMPLETED)])
        result = miner.get_patterns()
        assert len(result) == 1
        assert result[0]["action_type"] == "drift_fix"

    def test_get_patterns_filter_by_dimension(self, miner):
        miner.mine(
            [
                _make_action("drift_fix", FixStatus.COMPLETED, dimension="DIM-A"),
                _make_action("dep_version_fix", FixStatus.COMPLETED, dimension="DIM-B"),
            ]
        )
        result = miner.get_patterns(dimension="DIM-A")
        assert len(result) == 1
        assert result[0]["dimension"] == "DIM-A"

    def test_get_patterns_min_frequency(self, miner):
        miner.mine([_make_action("drift_fix", FixStatus.COMPLETED)])
        result = miner.get_patterns(min_frequency=5)
        assert result == []

    def test_get_patterns_handles_db_error(self, tmp_path):
        miner = FixPatternMiner(db_path=str(tmp_path / "nonexistent" / "bad.db"))
        miner._db_path = "/invalid/path/bad.db"
        result = miner.get_patterns()
        assert result == []


class TestPredictFixType:
    def test_predict_no_patterns(self, miner):
        result = miner.predict_fix_type("t.py")
        assert result is None

    def test_predict_low_success_rate(self, miner):
        actions = [_make_action("drift_fix", FixStatus.FAILED), _make_action("drift_fix", FixStatus.FAILED)]
        miner.mine(actions)
        result = miner.predict_fix_type("t.py")
        assert result is None

    def test_predict_high_success_rate(self, miner):
        actions = [
            _make_action("drift_fix", FixStatus.COMPLETED),
            _make_action("drift_fix", FixStatus.COMPLETED),
        ]
        miner.mine(actions)
        result = miner.predict_fix_type("t.py")
        assert result == "drift_fix"

    def test_predict_with_dimension_filter(self, miner):
        actions = [
            _make_action("drift_fix", FixStatus.COMPLETED, dimension="DIM-A"),
            _make_action("drift_fix", FixStatus.COMPLETED, dimension="DIM-A"),
        ]
        miner.mine(actions)
        result = miner.predict_fix_type("t.py", dimension="DIM-A")
        assert result == "drift_fix"
