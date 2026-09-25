# [MODULE] tests.ai_layer.perceive.test_source_registry
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""施工项 1 验收机检面：源注册表 12 源全字段齐 + 结构校验（缺字段/坏枚举/quota/重复 slug）。"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.ai_layer.perceive.source_registry import (
    SourceRegistryError,
    load_source_registry,
)

MINIMAL_SOURCE = {
    "slug": "test-src",
    "track": "github",
    "url": "https://example.com/test-src",
    "fetch": "Releases 监视",
    "frequency": "weekly",
    "daily_quota": 5,
    "health": "active",
    "last_verified": "2026-09-17",
    "basis": "测试桩源",
}


def _write_registry(tmp_path: Path, **overrides: object) -> Path:
    """组装最小合规注册表 fixture（overrides 注入坏值做反例）。"""
    import yaml

    body: dict = {
        "schema_version": "1.0",
        "sources": [dict(MINIMAL_SOURCE)],
        "longtail_candidates": [],
        "quota_governance": {"total_daily_cap": 40, "per_source_floor": 1, "demotion": {}},
    }
    body.update(overrides)
    path = tmp_path / "registry_fixture.yaml"
    path.write_text(yaml.safe_dump(body, allow_unicode=True), encoding="utf-8")
    return path


def test_real_registry_12_sources_full_fields() -> None:
    """验收原文：12 源 URL/频率/配额/健康度/核验日齐；结构校验过。"""
    registry = load_source_registry()
    assert len(registry.sources) == 12
    for source in registry.sources:
        assert all(str(getattr(source, f)).strip() for f in (
            "slug", "track", "url", "fetch", "frequency", "health", "last_verified", "basis"
        ))
        assert source.url.startswith("https://")
        assert source.daily_quota >= 1
        assert source.frequency in {"daily", "weekly", "monthly", "semiannual"}
        assert source.health in {"active", "degraded", "blocked", "retired"}
        assert source.track in {"github", "academic", "chinese_community", "baseline", "governance"}
    assert registry.total_daily_cap == 40
    assert len(registry.active_slugs()) == 12
    expected = {
        "awesome-quant", "qlib", "rd-agent", "alphagen", "arxiv-qfin", "ssrn-qf",
        "joinquant", "myquant", "bigquant", "kronos-baseline", "hf-papers", "gcloud-mlops",
    }
    assert set(registry.by_slug()) == expected


def test_longtail_not_in_quota_sources() -> None:
    """长尾待核验不入 v1：不占 sources、不占配额（DESIGN §2.1）。"""
    registry = load_source_registry()
    assert len(registry.longtail) >= 2
    source_slugs = set(registry.by_slug())
    for candidate in registry.longtail:
        assert candidate.slug not in source_slugs
        assert candidate.url.startswith("https://")


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SourceRegistryError, match="缺文件"):
        load_source_registry(tmp_path / "nope.yaml")


def test_missing_field_error_names_source(tmp_path: Path) -> None:
    broken = dict(MINIMAL_SOURCE)
    del broken["basis"]
    path = _write_registry(tmp_path, sources=[broken])
    with pytest.raises(SourceRegistryError, match="test-src"):
        load_source_registry(path)


def test_bad_enum_rejected(tmp_path: Path) -> None:
    bad = dict(MINIMAL_SOURCE, health="zombie")
    path = _write_registry(tmp_path, sources=[bad])
    with pytest.raises(SourceRegistryError, match="非法 health"):
        load_source_registry(path)


def test_quota_zero_rejected(tmp_path: Path) -> None:
    """配额禁清零（多样性保底）：quota=0 / quota=1.5 都拒。"""
    for bad_quota in (0, 1.5):
        bad = dict(MINIMAL_SOURCE, daily_quota=bad_quota)
        path = _write_registry(tmp_path, sources=[bad])
        with pytest.raises(SourceRegistryError, match="daily_quota"):
            load_source_registry(path)


def test_bad_url_rejected(tmp_path: Path) -> None:
    bad = dict(MINIMAL_SOURCE, url="ftp://example.com/x")
    path = _write_registry(tmp_path, sources=[bad])
    with pytest.raises(SourceRegistryError, match="http"):
        load_source_registry(path)


def test_duplicate_slug_rejected(tmp_path: Path) -> None:
    path = _write_registry(tmp_path, sources=[dict(MINIMAL_SOURCE), dict(MINIMAL_SOURCE)])
    with pytest.raises(SourceRegistryError, match="重复"):
        load_source_registry(path)


def test_quota_governance_required(tmp_path: Path) -> None:
    path = _write_registry(tmp_path, quota_governance={"total_daily_cap": 40})
    with pytest.raises(SourceRegistryError, match="quota_governance"):
        load_source_registry(path)


def test_quota_of_and_missing_slug(tmp_path: Path) -> None:
    path = _write_registry(tmp_path)
    registry = load_source_registry(path)
    assert registry.quota_of("test-src") == 5
    assert registry.quota_of("ghost") is None
