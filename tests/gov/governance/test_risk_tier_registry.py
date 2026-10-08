# [TTL] permanent
"""风险分级与人机门位注册表新鲜度测试（#ARCH-310 R5，2026-09-12 立；2026-10-09 随 v1.1.0 重建于 tests 新家+保留面契约断言）。

v1.1.0 契约（裁定路由政策 v2.0 修宪五件套同批）：high human_gate=Owner 保留面七条；
下放三条（治理资产净删/flag 翻转/非核心域首次转 production）不得回挂 human_gate。
能红证据：改坏 registry（human_gate 缺保留面条目/挂回下放面/版本回退）任一即红。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))  # noqa: E402

import yaml  # noqa: E402

RISK_REGISTRY = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml"
DOMAIN_REGISTRY = REPO_ROOT / "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"

LEGAL_TIERS = {"high", "medium", "low"}

# v1.1.0 保留面七条关键词锚（缺一即红）
RESERVED_FACE_KEYWORDS = (
    "资金与实盘交易",
    "首次施工转 production",
    "法律合规",
    "物理不可逆删除",
    "对外发布与资产出域",
    "业务资产",
    "宪法修订",
)

# 下放面标记（v1.1.0 起不得出现在 human_gate——回挂即红，防下放被静默回卷）
DELEGATED_FORBIDDEN_MARKERS = (
    "注册表/真源条目删除",
    "门禁 flag 出厂默认翻转",
)


@pytest.fixture(scope="module")
def risk_reg() -> dict:
    return yaml.safe_load(RISK_REGISTRY.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def known_domains() -> set[str]:
    d = yaml.safe_load(DOMAIN_REGISTRY.read_text(encoding="utf-8"))
    return {entry["domain"] for entry in d.get("entries", []) if entry.get("domain")}


def _high_human_gate(risk_reg: dict) -> list[str]:
    return list(risk_reg["tiers"]["high"]["human_gate"])


class TestRiskTierRegistryFreshness:
    def test_file_parses_with_required_top_keys(self, risk_reg: dict) -> None:
        for key in ("registry_id", "default_tier", "tiers", "domain_tiers"):
            assert key in risk_reg, f"缺少顶层键 {key}"

    def test_default_tier_is_legal(self, risk_reg: dict) -> None:
        assert risk_reg["default_tier"] in LEGAL_TIERS

    def test_entries_reference_known_domains(self, risk_reg: dict, known_domains: set[str]) -> None:
        for entry in risk_reg.get("domain_tiers", []):
            domain = entry.get("domain")
            assert domain in known_domains, f"{domain} 不在 functional_domain_registry（域改名后须同步本表）"

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


class TestRiskTierRegistryV11Contract:
    """v1.1.0 保留面契约（裁定路由政策 v2.0 同批）：缺保留面/回挂下放面/版本回退任一即红。"""

    def test_version_at_least_1_1_0(self, risk_reg: dict) -> None:
        ver = str(risk_reg.get("version", "0"))
        parts = tuple(int(p) for p in ver.split(".")[:3])
        assert parts >= (1, 1, 0), f"risk_tier_registry 版本回退: {ver} < 1.1.0（v2 门位契约丢失）"

    def test_high_human_gate_is_reserved_face_seven(self, risk_reg: dict) -> None:
        gate = _high_human_gate(risk_reg)
        assert len(gate) == 7, f"high human_gate 应为保留面七条，实际 {len(gate)} 条（下放面回挂或保留面缺失）"
        joined = "\n".join(gate)
        for kw in RESERVED_FACE_KEYWORDS:
            assert kw in joined, f"保留面缺失: human_gate 无「{kw}」条目"

    def test_delegated_not_in_human_gate(self, risk_reg: dict) -> None:
        joined = "\n".join(_high_human_gate(risk_reg))
        for marker in DELEGATED_FORBIDDEN_MARKERS:
            assert marker not in joined, f"下放面回挂 human_gate: 「{marker}」（v2 墓碑/shadow 制被回卷）"
