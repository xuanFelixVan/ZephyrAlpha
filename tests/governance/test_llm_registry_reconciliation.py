# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/audit_llm_registry_reconciliation.py | §test
# [A_test] module_id: MOD-GOVERNANCE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""LLM 模型注册三向对账脚本测试（10号文 §4 Phase 3.1）。

验收口径：①真实仓库零误报跑通；②人为改一处价格能检出；
③人为删一个治理字段能检出。

覆盖：真实源零新增漂移 / 价格篡改检出 / staging 条目治理字段缺失检出 /
candidate 部分四元组检出 / 全 candidate 无治理字段不误报 / 哈希格式校验 /
tier 词表 / entry_count 账实 / 已知偏差分类与 STALE 报告。
"""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "audit_llm_registry_reconciliation",
    _REPO_ROOT / "scripts" / "governance" / "audit_llm_registry_reconciliation.py",
)
recon = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(recon)

_B_PATH = _REPO_ROOT / "config" / "model_pricing.yaml"
_D_PATH = _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "model_registry.yaml"
_HASH64 = "a" * 64


def _real_sources() -> tuple[dict, dict, dict]:
    from zephyr.orchestrator.governance.model_registry import MODELS

    raw_b = yaml.safe_load(_B_PATH.read_text(encoding="utf-8"))
    b = {k: v for k, v in raw_b.items() if k != "module_id" and isinstance(v, dict)}
    d = yaml.safe_load(_D_PATH.read_text(encoding="utf-8"))
    return dict(MODELS), b, d


def _new_drift(findings: list[dict]) -> list[dict]:
    new_drift, _known, _stale = recon.classify_findings(findings)
    return new_drift


def _staging_entry(**overrides) -> dict:
    base = {
        "model_id": "ML-T-001",
        "name": "t",
        "promotion_stage": "staging",
        "version": "1.0.0",
        "status": "active",
        "code_hash": "b" * 64,
        "param_hash": "c" * 64,
        "training_data_hash": _HASH64,
        "audit_hash_chain": ["genesis"],
    }
    base.update(overrides)
    return base


class TestRealRepoZeroDrift:
    """验收①：真实仓库零误报跑通。"""

    def test_no_new_drift_on_real_sources(self) -> None:
        a, b, d = _real_sources()
        findings = recon.collect_findings(a, b, d)
        assert _new_drift(findings) == []

    def test_known_deviations_all_hit(self) -> None:
        """已登记偏差全部命中（登记清单无 STALE 死条目）。"""
        a, b, d = _real_sources()
        findings = recon.collect_findings(a, b, d)
        _new, known, stale = recon.classify_findings(findings)
        assert len(known) == len(recon.KNOWN_DEVIATIONS)
        assert stale == []

    def test_main_exit_pass(self) -> None:
        assert recon.main([]) == 0


class TestPriceTamperDetection:
    """验收②：人为改一处价格能检出。"""

    def test_price_tamper_detected(self) -> None:
        a, b, d = _real_sources()
        b["deepseek-chat"]["input_price"] = 0.005  # 篡改：0.003 -> 0.005
        drift = _new_drift(recon.collect_findings(a, b, d))
        hits = [f for f in drift if f["check"] == "PRICE_BASELINE_DRIFT" and f["subject"] == "deepseek-chat"]
        assert len(hits) == 1
        assert "0.005" in hits[0]["detail"]

    def test_new_priced_model_without_baseline_detected(self) -> None:
        a, b, d = _real_sources()
        b["evil-model"] = {"input_price": 0.1, "output_price": 0.1, "provider": "x", "updated_at": "2026_08_30"}
        drift = _new_drift(recon.collect_findings(a, b, d))
        checks = {(f["check"], f["subject"]) for f in drift}
        assert ("B_UNKNOWN_MODEL_BASELINE", "evil-model") in checks
        assert ("B_UNREGISTERED", "evil-model") in checks

    def test_price_removed_field_detected(self) -> None:
        a, b, d = _real_sources()
        del b["qwen-flash"]["output_price"]
        drift = _new_drift(recon.collect_findings(a, b, d))
        assert any(f["check"] == "B_STRUCTURE" and f["subject"] == "qwen-flash" for f in drift)


class TestGovernanceFieldDetection:
    """验收③：人为删一个治理字段能检出（§3.4 口径）。"""

    def _d(self, entries: list[dict]) -> dict:
        return {"entry_count": len(entries), "models": entries}

    def test_staging_entry_complete_passes(self) -> None:
        findings = recon.check_d_governance(self._d([_staging_entry()]))
        assert findings == []

    @pytest.mark.parametrize("field", ["code_hash", "param_hash", "training_data_hash"])
    def test_staging_quadruple_field_deleted_detected(self, field: str) -> None:
        entry = _staging_entry()
        del entry[field]
        findings = recon.check_d_governance(self._d([entry]))
        assert any(f["check"] == "D_GOV_REQUIRED_FOR_STAGE" and field in f["detail"] for f in findings)

    def test_staging_audit_chain_deleted_detected(self) -> None:
        entry = _staging_entry()
        del entry["audit_hash_chain"]
        findings = recon.check_d_governance(self._d([entry]))
        assert any("audit_hash_chain" in f["detail"] for f in findings)

    def test_candidate_without_gov_fields_no_false_positive(self) -> None:
        entry = _staging_entry(promotion_stage="candidate")
        for f in ("code_hash", "param_hash", "training_data_hash", "audit_hash_chain"):
            del entry[f]
        assert recon.check_d_governance(self._d([entry])) == []

    def test_candidate_partial_quadruple_detected(self) -> None:
        entry = _staging_entry(promotion_stage="candidate")
        del entry["param_hash"]
        del entry["audit_hash_chain"]
        findings = recon.check_d_governance(self._d([entry]))
        assert any(f["check"] == "D_GOV_QUADRUPLE_INCOMPLETE" for f in findings)

    def test_bad_hash_format_detected(self) -> None:
        entry = _staging_entry()
        entry["training_data_hash"] = "not-a-sha256"
        findings = recon.check_d_governance(self._d([entry]))
        assert any(f["check"] == "D_GOV_HASH_FORMAT" for f in findings)

    def test_entry_count_mismatch_detected(self) -> None:
        d = {"entry_count": 99, "models": [_staging_entry()]}
        findings = recon.check_d_governance(d)
        assert any(f["check"] == "D_ENTRY_COUNT_MISMATCH" for f in findings)


class TestASideStructure:
    def test_bad_tier_detected(self) -> None:
        findings = recon.check_a_structure({"m": {"provider": "p", "tier": "gold", "token_limit": 1024}})
        assert any("tier" in f["detail"] for f in findings)

    def test_bad_token_limit_detected(self) -> None:
        findings = recon.check_a_structure({"m": {"provider": "p", "tier": "standard", "token_limit": 0}})
        assert any("token_limit" in f["detail"] for f in findings)

    def test_healthy_entry_passes(self) -> None:
        assert recon.check_a_structure({"m": {"provider": "p", "tier": "standard", "token_limit": 1024}}) == []


class TestClassification:
    def test_known_hit_not_blocking(self) -> None:
        findings = [recon._finding("A_NO_PRICING", "claude-opus-4", "x")]
        new_drift, known, stale = recon.classify_findings(findings)
        assert new_drift == []
        assert len(known) == 1
        assert ("A_NO_PRICING", "gpt-5.2") in {k for k, _ in stale}  # 未命中的登记进 STALE

    def test_unregistered_finding_blocks(self) -> None:
        findings = [recon._finding("A_NO_PRICING", "brand-new-model", "x")]
        new_drift, _known, _stale = recon.classify_findings(findings)
        assert len(new_drift) == 1
