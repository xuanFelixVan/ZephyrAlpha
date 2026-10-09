# [MODULE] tests.gov.governance.test_roor_path_resolution
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.governance.registry_ledger.baseline.load_roor_index
# [CONSUMERS] 总统筹增补令·P1 红证：路径→registry_id 反查恒定单值（ROOR 双挂号=潜在批量蒸发通道根治）
# [INVARIANTS] 全部用例 tmp ROOR 构造（零真实仓库面）；红证判据=无论文档序/墓碑态如何翻转，
#   同一路径反查必须恒定返回正主（REG-CAPCAN-001），空壳墓碑（REG-GEN-001）永不占位
# [MODIFY-GUARD] 新建 2026-10-10 st-regsolo-20261010（P1 随批测试，tests/ 豁免 token）
# [TTL] permanent
"""ROOR 路径反查单值性守卫（总统筹 2026-10-10 增补令 P1）。

事实：ROOR 同一物理路径挂两号——REG-CAPCAN-001（正主，PG 万四条）与 REG-GEN-001
（空壳子集视图，PG 0 条）。任何反查取到空壳=持空账本覆盖上万条投影（间歇性蒸发
候选）。治本三层：①ROOR GEN 条目墓碑化（status: retired）；②load_roor_index dedup
升级 retired 感知（墓碑永不占位，正主后到夺回）；③全仓五通道（render/物化/迁移/
预检/投影 CLI）反查同源=本函数单点收紧即闭环。
"""

from __future__ import annotations

from pathlib import Path

from zephyr.governance.registry_ledger.baseline import load_roor_index

_CAP = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"


def _write_roor(tmp_path: Path, body: str) -> Path:
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "registry_of_registries.yaml").write_text(body, encoding="utf-8")
    return root


_CAP_ENTRY = """      - registry_id: REG-CAPCAN-001
        name: 正主
        physical_path: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
        status: active
"""
_GEN_ACTIVE = """      - registry_id: REG-GEN-001
        name: 空壳子集视图
        physical_path: docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
        status: active
"""
_GEN_TOMB = _GEN_ACTIVE.replace("status: active", "status: retired（墓碑）")


def test_real_world_shape_cancan_first_wins(tmp_path):
    """现世界形态：正主在前（:456）空壳在后（:472）→ 恒返 CAPCAN。"""
    root = _write_roor(tmp_path, f"registries:\n  a:\n    entries:\n{_CAP_ENTRY}\n{_GEN_ACTIVE}")
    idx = load_roor_index(root)
    assert idx[_CAP]["registry_id"] == "REG-CAPCAN-001"


def test_tombstoned_first_never_occupies(tmp_path):
    """红证 P1：墓碑排文档序首位也让位——正主后到夺回（retired 感知 dedup）。"""
    root = _write_roor(tmp_path, f"registries:\n  a:\n    entries:\n{_GEN_TOMB}\n{_CAP_ENTRY}")
    idx = load_roor_index(root)
    assert idx[_CAP]["registry_id"] == "REG-CAPCAN-001", "墓碑永不占位（空壳账本覆盖万条投影的通道封死）"


def test_active_gen_first_still_wins_by_doc_order():
    """蓝证（语义边界）：双 active 且空壳在前=文档序空壳胜——墓碑是治本手段，
    去墓碑的双挂号不在本函数静默纠偏（保守面不改宽；治本靠 ROOR 墓碑化）。"""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = _write_roor(Path(td), f"registries:\n  a:\n    entries:\n{_GEN_ACTIVE}\n{_CAP_ENTRY}")
        idx = load_roor_index(root)
        assert idx[_CAP]["registry_id"] == "REG-GEN-001"


def test_real_repo_roor_returns_cancan():
    """真仓红证：本仓 ROOR（GEN 已墓碑）反查 CAP 路径恒返 REG-CAPCAN-001。"""
    root = Path(__file__).resolve().parents[3]
    roor = root / "docs" / "registry_of_registries.yaml"
    if not roor.exists():
        import pytest

        pytest.skip("非标准检出")
    idx = load_roor_index(root)
    assert idx.get(_CAP, {}).get("registry_id") == "REG-CAPCAN-001"
