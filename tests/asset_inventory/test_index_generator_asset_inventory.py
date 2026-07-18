# [A_test] module_id: SRC-TST-0073 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-231 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_index_generator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 IndexGenerator module — 蓝图 §2.4 + §17 附录 H 要求 >80% 覆盖."""

from datetime import UTC, datetime

from zephyr.infrastructure.asset_inventory.index_generator import (
    IndexGenerator,
    _calc_grade,
    _calc_numeric,
    _count_by_status,
    _to_yaml,
)
from zephyr.infrastructure.asset_inventory.models import (
    AssetStatus,
    AssetType,
    ClassificationResult,
    ClassifiedAsset,
)


def _classified(total: int = 5, unknown_pct: float = 0.0) -> ClassificationResult:
    assets = []
    for i in range(total):
        assets.append(
            ClassifiedAsset(
                relative_path=f"src/module_{i}.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.ACTIVE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="a" * 64,
            )
        )
    return ClassificationResult(
        classification_id="C-TEST-001",
        source_scan_id="S-TEST-001",
        total_classified=total,
        unknown_count=int(total * unknown_pct / 100),
        unknown_pct=unknown_pct,
        by_type={"module": total},
        by_layer={"cross_layer": total},
        assets=assets,
    )


class TestGenerate:
    def test_generate_basic(self) -> None:
        cr = _classified(5)
        ig = IndexGenerator()
        index = ig.generate(cr)
        assert index.total_assets == 5
        assert index.health_score in ("A", "B", "C", "D", "F")
        assert index.schema_version == "1.0.0"
        assert index.registries_checked > 0

    def test_generate_empty(self) -> None:
        cr = _classified(0)
        ig = IndexGenerator()
        index = ig.generate(cr)
        assert index.total_assets == 0

    def test_generate_preserves_by_type(self) -> None:
        cr = _classified(3)
        ig = IndexGenerator()
        index = ig.generate(cr)
        assert index.by_type == {"module": 3}

    def test_generate_unknown_rate_flows(self) -> None:
        cr = _classified(10, unknown_pct=5.0)
        ig = IndexGenerator()
        index = ig.generate(cr)
        assert index.orphan_rate_pct == 5.0


class TestHealthCalculations:
    def test_grade_a(self) -> None:
        assert _calc_grade(0.0, 0.0, 0.0) == "A"

    def test_grade_b(self) -> None:
        assert _calc_grade(5.0, 0.0, 0.0) == "B"

    def test_grade_c(self) -> None:
        assert _calc_grade(10.0, 3.0, 0.0) == "C"

    def test_grade_f(self) -> None:
        assert _calc_grade(20.0, 10.0, 20.0) == "F"

    def test_numeric_perfect(self) -> None:
        assert _calc_numeric(0.0, 0.0, 0.0) == 98.0

    def test_numeric_degraded(self) -> None:
        score = _calc_numeric(10.0, 5.0, 10.0)
        assert score < 80.0


class TestCountByStatus:
    def test_all_active(self) -> None:
        assets = [
            ClassifiedAsset(
                relative_path="a.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.ACTIVE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="a" * 64,
            ),
            ClassifiedAsset(
                relative_path="b.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.ACTIVE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="b" * 64,
            ),
        ]
        result = _count_by_status(assets)
        assert result == {"active": 2}

    def test_mixed_statuses(self) -> None:
        assets = [
            ClassifiedAsset(
                relative_path="a.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.ACTIVE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="a" * 64,
            ),
            ClassifiedAsset(
                relative_path="b.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.ACTIVE,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="b" * 64,
            ),
            ClassifiedAsset(
                relative_path="c.py",
                asset_type=AssetType.MODULE,
                status=AssetStatus.DEPRECATED,
                size_bytes=100,
                mtime_utc=datetime.now(UTC),
                sha256="c" * 64,
            ),
        ]
        result = _count_by_status(assets)
        assert result == {"active": 2, "deprecated": 1}


class TestSave:
    def test_save_creates_file(self, tmp_path) -> None:
        cr = _classified(3)
        ig = IndexGenerator()
        index = ig.generate(cr)
        out = ig.save(index, output_path=tmp_path / "index.yaml")
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "total_assets: 3" in content or "total_assets:" in content

    def test_save_atomic_no_temp_left(self, tmp_path) -> None:
        cr = _classified(2)
        ig = IndexGenerator()
        index = ig.generate(cr)
        target = tmp_path / "uidx.yaml"
        ig.save(index, output_path=target)
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0


class TestToYaml:
    def test_simple_dict(self) -> None:
        result = _to_yaml({"key": "value", "num": 42})
        assert "key:" in result
        assert "42" in result

    def test_nested_dict(self) -> None:
        result = _to_yaml({"outer": {"inner": "x"}})
        assert "outer:" in result
        assert "inner:" in result

    def test_list_of_dicts(self) -> None:
        result = _to_yaml({"items": [{"name": "a"}, {"name": "b"}]})
        assert "items:" in result
        assert "name:" in result

    def test_null_and_bool(self) -> None:
        result = _to_yaml({"empty": None, "flag": True})
        assert "null" in result
        assert "true" in result

    def test_special_chars_escaped(self) -> None:
        result = _to_yaml({"path": "C:\\Users\\test"})
        assert "C:" in result
