# [A_test] stability=volatile
# [MODULE] tests.governance.test_check_wiring_orphan
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.check_wiring_orphan
# [TTL] permanent
"""check_wiring_orphan 装配超期门禁单测（Owner 裁定三 Layer3）。

覆盖：结构校验（缺键/非法词表/缺文件/空台账）、超期判定（阈值边界恰等不归超期、
per-module registered_at 优先于全局 generated_at）、strict 门禁语义、当前仓台账健康。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.governance.check_wiring_orphan import check  # noqa: E402


def _write_registry(tmp_path: Path, body: str) -> Path:
    reg = tmp_path / "wiring_registry.yaml"
    reg.write_text(body, encoding="utf-8")
    return reg


_HEADER = "# wiring_registry.yaml\nversion: '1.0.0'\ngenerated_at: '2026-08-27'\nmodules:\n"


def _entry(cid: str, status: str, registered_at: str = "2026-08-27", cls: str = "eventbus_consumer") -> str:
    return (
        f"- candidate_id: {cid}\n"
        f'  name: "测试模块"\n'
        f"  path: src/zephyr/x/y.py\n"
        f"  domain: D_X\n"
        f'  registered_at: "{registered_at}"\n'
        f"  wiring_class: {cls}\n"
        f"  wiring_status: {status}\n"
    )


class TestStructure:
    def test_missing_registry(self, tmp_path: Path) -> None:
        problems, orphans = check(tmp_path / "nonexist.yaml", 90, "2026-08-27")
        assert problems and "missing" in problems[0]
        assert orphans == []

    def test_zero_modules(self, tmp_path: Path) -> None:
        reg = _write_registry(tmp_path, _HEADER)
        problems, _ = check(reg, 90, "2026-08-27")
        assert any("zero modules" in p for p in problems)

    def test_missing_required_key(self, tmp_path: Path) -> None:
        bad = "- candidate_id: CAND-X-001\n  wiring_status: unwired\n"
        reg = _write_registry(tmp_path, _HEADER + bad)
        problems, _ = check(reg, 90, "2026-08-27")
        assert any("missing key" in p for p in problems)

    def test_invalid_class_and_status(self, tmp_path: Path) -> None:
        body = _entry("CAND-X-002", "half_wired", cls="unknown_class")
        reg = _write_registry(tmp_path, _HEADER + body)
        problems, _ = check(reg, 90, "2026-08-27")
        assert any("invalid wiring_class" in p for p in problems)
        assert any("invalid wiring_status" in p for p in problems)


class TestOrphanDetection:
    def test_fresh_unwired_not_orphan(self, tmp_path: Path) -> None:
        reg = _write_registry(tmp_path, _HEADER + _entry("CAND-X-010", "unwired", "2026-08-20"))
        problems, orphans = check(reg, 90, "2026-08-27")
        assert problems == []
        assert orphans == []

    def test_stale_unwired_is_orphan(self, tmp_path: Path) -> None:
        reg = _write_registry(tmp_path, _HEADER + _entry("CAND-X-011", "unwired", "2026-01-01"))
        problems, orphans = check(reg, 90, "2026-08-27")
        assert problems == []
        assert len(orphans) == 1 and "CAND-X-011" in orphans[0]

    def test_boundary_exact_days_not_orphan(self, tmp_path: Path) -> None:
        # 恰 90 天（不 > 90）不归超期
        reg = _write_registry(tmp_path, _HEADER + _entry("CAND-X-012", "unwired", "2026-05-29"))
        _, orphans = check(reg, 90, "2026-08-27")
        assert orphans == []

    def test_wired_and_exempt_never_orphan(self, tmp_path: Path) -> None:
        body = _entry("CAND-X-013", "wired", "2020-01-01") + _entry(
            "CAND-X-014", "exempt", "2020-01-01", cls="pure_library"
        )
        reg = _write_registry(tmp_path, _HEADER + body)
        _, orphans = check(reg, 90, "2026-08-27")
        assert orphans == []

    def test_per_module_registered_at_overrides_global(self, tmp_path: Path) -> None:
        # 全局 generated_at 很旧，但模块 registered_at 很新 → 不归超期
        header = _HEADER.replace("2026-08-27", "2020-01-01")
        reg = _write_registry(tmp_path, header + _entry("CAND-X-015", "unwired", "2026-08-20"))
        _, orphans = check(reg, 90, "2026-08-27")
        assert orphans == []

    def test_fallback_to_global_generated_at(self, tmp_path: Path) -> None:
        body = _entry("CAND-X-016", "unwired").replace('  registered_at: "2026-08-27"\n', "")
        header = _HEADER.replace("2026-08-27", "2020-01-01")
        reg = _write_registry(tmp_path, header + body)
        _, orphans = check(reg, 90, "2026-08-27")
        assert len(orphans) == 1

    def test_defer_reason_does_not_exempt(self, tmp_path: Path) -> None:
        body = _entry("CAND-X-017", "unwired", "2026-01-01") + '  defer_reason: "无生产者"\n'
        reg = _write_registry(tmp_path, _HEADER + body)
        _, orphans = check(reg, 90, "2026-08-27")
        assert len(orphans) == 1


class TestCurrentRepoRegistry:
    def test_repo_registry_healthy(self) -> None:
        reg = _PROJECT_ROOT / "docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml"
        problems, orphans = check(reg, 90, None)
        assert problems == [], f"台账结构缺陷: {problems}"
        assert orphans == [], f"当前不应有超期 orphan: {orphans}"
