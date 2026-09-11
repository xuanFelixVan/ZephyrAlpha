# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.test_risk_tier_registry
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] 风险分级注册表新鲜度机械校验（#ARCH-310 R5）：条目 domain 必须存在于 functional_domain_registry；tier 合法；high 条目必有人类门位；default_tier 必须声明
# [TTL] permanent
"""风险分级与人机门位注册表新鲜度测试（#ARCH-310 R5 落地，2026-09-12）。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))  # noqa: E402

import yaml  # noqa: E402

RISK_REGISTRY = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml"
DOMAIN_REGISTRY = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"

LEGAL_TIERS = {"high", "medium", "low"}


@pytest.fixture(scope="module")
def risk_reg() -> dict:
    return yaml.safe_load(RISK_REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def known_domains() -> set[str]:
    d = yaml.safe_load(DOMAIN_REGISTRY.read_text(encoding="utf-8"))
    return {entry["domain"] for entry in d.get("entries", []) if entry.get("domain")}


class TestRiskTierRegistryFreshness:
    def test_file_parses_with_required_top_keys(self, risk_reg: dict) -> None:
        for key in ("registry_id", "default_tier", "tiers", "domain_tiers"):
            assert key in risk_reg, f"缺少顶层键 {key}"

    def test_default_tier_is_legal(self, risk_reg: dict) -> None:
        assert risk_reg["default_tier"] in LEGAL_TIERS

    def test_entries_reference_known_domains(self, risk_reg: dict, known_domains: set[str]) -> None:
        for entry in risk_reg.get("domain_tiers", []):
            domain = entry.get("domain")
            assert domain in known_domains, (
                f"{domain} 不在 functional_domain_registry（域改名后须同步本表）"
            )

    def test_tier_values_legal(self, risk_reg: dict) -> None:
        for entry in risk_reg.get("domain_tiers", []):
            assert entry.get("tier") in LEGAL_TIERS, f"{entry.get('domain')} tier 非法: {entry.get('tier')}"

    def test_high_entries_require_human_gate(self, risk_reg: dict) -> None:
        for entry in risk_reg.get("domain_tiers", []):
            if entry.get("tier") == "high":
                assert entry.get("human_gate"), f"{entry.get('domain')} 为 high 但未声明 human_gate 位"

    def test_no_duplicate_domains(self, risk_reg: dict) -> None:
        domains = [e.get("domain") for e in risk_reg.get("domain_tiers", [])]
        assert len(domains) == len(set(domains)), "domain 条目重复"

    def test_medium_low_human_gate_empty(self, risk_reg: dict) -> None:
        """medium/low 不设人类门位（门位只属 high——分级模型一致性）。"""
        for entry in risk_reg.get("domain_tiers", []):
            if entry.get("tier") in ("medium", "low"):
                assert not entry.get("human_gate"), (
                    f"{entry.get('domain')} 为 {entry.get('tier')} 却声明了 human_gate 位"
                )
