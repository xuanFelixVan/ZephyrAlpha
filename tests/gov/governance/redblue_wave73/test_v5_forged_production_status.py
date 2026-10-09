# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v5_forged_production_status
# [DOMAIN] D_GOV_CODE_QUALITY
"""wave7.3 V5 冒充 verified：伪造 build_status=production → BUSINESS-REGISTRY G1 硬拦。

攻击：新增业务资产库条目，其 module 在 depgraph 中实为 production 态（已实现），
攻击者借此冒充"已验证/已实现"身份入库而不挂作战锚点。
防御面：business_registry_gate G1 二期——新增条目 module build_status=production
且无 battle_map 锚点 → 硬阻断（DB 视角经 _query_one 打桩，PG/CH 停机不参与）。
对照组：design/planned 态同场景仅 warn 放行（待实现语义，非冒充面）。
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

import zephyr.gov_enforcement.commit_gates.business_registry_gate as brg
import zephyr.gov_enforcement.registry_alignment as ra_mod

_REL = "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"


def _make_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, build_status: str | None):
    catalogs = tmp_path / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    catalog = catalogs / "strategy_registry.yaml"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text(
        "strategies:\n  - strategy_id: FORGED-001\n    module_id: MOD-REAL-001\n",
        encoding="utf-8",
    )
    # 库路径重锚到 tmp（spec_path 走 ra_mod.CATALOGS_DIR 全局；brg._CATALOGS_DIR 双补）
    monkeypatch.setattr(ra_mod, "CATALOGS_DIR", catalogs)
    monkeypatch.setattr(brg, "_CATALOGS_DIR", catalogs, raising=False)
    gw = MagicMock()
    gw.project_root = tmp_path

    def _fake_query_one(sql: str, arg: object):
        if sql == brg._SQL_GET_BUILD_STATUS:
            return (False, build_status)  # skip=False, status
        if sql == brg._SQL_CHECK_BM_ANCHOR:
            return (False, None)  # skip=False, 无锚点
        return (True, None)

    monkeypatch.setattr(brg, "_added_entry_ids", lambda rel, key: ["FORGED-001"])
    monkeypatch.setattr(brg, "_query_one", _fake_query_one)
    # depgraph 存在性子检查打桩（双命名空间防御式打桩；打桩后跳过而非 fail-open 撞停机 DB）
    monkeypatch.setattr(brg, "in_flight_module_ids", lambda: [], raising=False)
    monkeypatch.setattr(brg, "missing_depgraph_module_ids", lambda mids: (set(), False), raising=False)
    monkeypatch.setattr(ra_mod, "in_flight_module_ids", lambda: [], raising=False)
    monkeypatch.setattr(ra_mod, "missing_depgraph_module_ids", lambda mids: (set(), False), raising=False)
    return gw


def test_forged_production_without_anchor_blocks(tmp_path, monkeypatch):
    gw = _make_env(tmp_path, monkeypatch, "production")
    passed, detail = brg.make_business_registry_gate().check(gw, [_REL])
    assert passed is False, "冒充 production 入库（无作战锚点）未阻断——V5 得手"
    assert "production" in detail


def test_design_status_is_warn_not_block(tmp_path, monkeypatch):
    """对照组：design 态=待实现（warn 语义），不属冒充面——放行。"""
    gw = _make_env(tmp_path, monkeypatch, "design")
    passed, detail = brg.make_business_registry_gate().check(gw, [_REL])
    assert passed is True, f"design 态被误伤阻断（应 warn）：{detail}"
