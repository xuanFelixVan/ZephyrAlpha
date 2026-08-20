# [BLUEPRINT] MOD-D5_ARCH_TOOLS | docs/03_modules/_domain_governance/blueprint.md | §
# [A_test] module_id: MOD-GOV_validate_yaml_summaries | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_validate_yaml_summaries.py — GATE-SUM (validate_yaml_summaries.py) 单测。

覆盖 consumer_registry 嵌套 summary 校验（audit-02 第3轮复审治本 2026-08-02 新增）：
  contracts/consumer_registry.yaml 结构为 contracts → registered_consumers 嵌套，
  不适用通用扁平 list 校验，由 validate_yaml_summaries.py 专用块校验
  total_contracts_registered / total_consumer_entries / tier_distribution 三类聚合。

测试矩阵：
  1. 当前仓库 consumer_registry 无漂移（回归守卫，仅检 consumer_registry 维度避免跨界误报）
  2. 一致数据 → 通过
  3. total_contracts_registered 漂移 → 捕获
  4. total_consumer_entries 漂移 → 捕获
  5. tier_distribution 漂移 → 捕获
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GOV_DIR = _REPO_ROOT / "scripts" / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

_VALIDATOR_PATH = _GOV_DIR / "d5_architecture" / "validators" / "yaml_md" / "validate_yaml_summaries.py"

_spec = importlib.util.spec_from_file_location("validate_yaml_summaries", _VALIDATOR_PATH)
assert _spec and _spec.loader
vys = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vys)


def _consumer_registry_yaml(contracts: int = 2, entries_per: int = 1, tier: int = 1) -> str:
    """构造最小 consumer_registry.yaml 内容（summary 与实际数据严格一致）。"""
    lines = ["consumers:"]
    for i in range(1, contracts + 1):
        lines.append(f"  - contract_id: CTR-{i:03d}")
        lines.append(f"    contract_name: Contract{i}")
        lines.append("    registered_consumers:")
        for j in range(entries_per):
            lines.append(f'      - {{domain: D_TEST, module: "m{j}", tier: {tier}, pinned_version: "1.0.0"}}')
    total_entries = contracts * entries_per
    lines.append("summary:")
    lines.append(f"  total_contracts_registered: {contracts}")
    lines.append(f"  total_consumer_entries: {total_entries}")
    lines.append("  tier_distribution:")
    lines.append(f"    tier_1_critical: {total_entries if tier == 1 else 0}")
    lines.append(f"    tier_2_secondary: {total_entries if tier == 2 else 0}")
    return "\n".join(lines) + "\n"


@pytest.fixture
def tmp_arch(tmp_path, monkeypatch):
    """临时 ARCH_MODEL，仅含 contracts/consumer_registry.yaml。

    通过 monkeypatch 覆盖模块级 ARCH_MODEL，使 validate_yaml_summaries()
    只扫描 tmp 目录（其余 SCAN_ENTRIES/module_id_registry/index 均不存在→跳过），
    隔离测试 consumer_registry 校验逻辑。
    """
    arch = tmp_path / "architecture_model"
    (arch / "contracts").mkdir(parents=True)
    monkeypatch.setattr(vys, "ARCH_MODEL", arch)
    return arch


def test_current_repo_consumer_registry_consistent():
    """回归守卫：当前仓库 consumer_registry.yaml summary 零漂移。

    仅检 consumer_registry 维度（不断言全仓库零漂移，避免与其他文件漂移跨界误报）。
    """
    passed, errors = vys.validate_yaml_summaries()
    cr_errors = [e for e in errors if "consumer_registry" in e]
    assert not cr_errors, f"consumer_registry summary 漂移: {cr_errors}"


def test_consumer_registry_passes_when_consistent(tmp_arch):
    """一致的 consumer_registry 不报错。"""
    (tmp_arch / "contracts" / "consumer_registry.yaml").write_text(
        _consumer_registry_yaml(contracts=2, entries_per=1, tier=1), encoding="utf-8"
    )
    passed, errors = vys.validate_yaml_summaries()
    assert passed, errors


def test_consumer_registry_drift_contracts(tmp_arch):
    """total_contracts_registered 漂移被捕获。"""
    content = _consumer_registry_yaml(contracts=2, entries_per=1, tier=1).replace(
        "total_contracts_registered: 2", "total_contracts_registered: 9"
    )
    (tmp_arch / "contracts" / "consumer_registry.yaml").write_text(content, encoding="utf-8")
    passed, errors = vys.validate_yaml_summaries()
    assert not passed
    assert any("total_contracts_registered" in e for e in errors)


def test_consumer_registry_drift_entries(tmp_arch):
    """total_consumer_entries 漂移被捕获。"""
    content = _consumer_registry_yaml(contracts=2, entries_per=1, tier=1).replace(
        "total_consumer_entries: 2", "total_consumer_entries: 99"
    )
    (tmp_arch / "contracts" / "consumer_registry.yaml").write_text(content, encoding="utf-8")
    passed, errors = vys.validate_yaml_summaries()
    assert not passed
    assert any("total_consumer_entries" in e for e in errors)


def test_consumer_registry_drift_tier(tmp_arch):
    """tier_distribution 漂移被捕获。"""
    content = _consumer_registry_yaml(contracts=2, entries_per=1, tier=1).replace(
        "tier_1_critical: 2", "tier_1_critical: 50"
    )
    (tmp_arch / "contracts" / "consumer_registry.yaml").write_text(content, encoding="utf-8")
    passed, errors = vys.validate_yaml_summaries()
    assert not passed
    assert any("tier_distribution" in e for e in errors)
