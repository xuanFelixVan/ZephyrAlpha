# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [DOMAIN] D_TRADING
# [TESTS] tests/trading/test_decision_map_d38_adversarial.py
# [TTL] permanent
"""D38 红蓝极限对抗测试——frontend_map MOD 总线 + 新图新库必挂铁律（Owner 2026-09-07 指令）。

红队武器库（每类攻击对应蓝方断言：违规必拦 / 合法语义必放行 / 环境降级不阻断）：
  H 类 frontend_map R1 列表攻击：首元素合法后续垃圾 / 空 list / 畸形类型（数字/字典）
  I 类 R4 模块总线攻击：幽灵模块 / 悬空功能点 / 双向不闭合 / 幽灵页面 / 大小写伪装 /
       DB 不可达降级 / 合法双向闭合放行
  K 类 新库必挂门禁攻击：未登记新库 / 删轴文件 / 豁免清单腐烂 / 走豁免路径放行 / 加轴后放行
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_CHECKERS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "generators"
_TRADE_TESTS_DIR = _REPO / "tests" / "trading"
if str(_CHECKERS_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECKERS_DIR))
if str(_TRADE_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TRADE_TESTS_DIR))

import check_frontend_map as cfm  # noqa: E402
import test_decision_map as tdm  # noqa: E402


# ── H 类 frontend_map R1 列表攻击 ────────────────────────────────────────────


class TestFrontendListAttacks:
    """backend_ref 列表形态（v2.1.0 新契约）的绕过尝试。"""

    def _run(self, feat: dict) -> list[str]:
        warns: list[str] = []
        fails: list[str] = []
        cfm._check_feature(feat, set(), warns, fails)
        return fails

    def test_h1_valid_head_garbage_tail(self) -> None:
        """H1 首元素合法、后续垃圾——首元素检查绕不过逐元素校验（D38 自查真 bug 修复锚）。"""
        fails = self._run(
            {"id": "F-X", "backend_ref": ["table:CH.t1", "garbage_ref"]}
        )
        assert any("列表含非类型化元素" in f for f in fails)

    def test_h2_empty_list_is_dangling(self) -> None:
        """H2 空列表 = 悬空 → R1 fail。"""
        fails = self._run({"id": "F-X", "backend_ref": []})
        assert any("悬空" in f for f in fails)

    def test_h3_all_typed_list_passes(self) -> None:
        """H3 全类型化列表 → 放行（合法多后端场景）。"""
        fails = self._run(
            {"id": "F-X", "backend_ref": ["module:MOD-AAA-001", "table:CH.t1", "api:/api/x"]}
        )
        assert fails == []

    def test_h4_malformed_types_not_crash(self) -> None:
        """H4 数字/字典畸形 backend_ref → str 归一化后 R1 拦截，不 crash。"""
        for bad in (123, {"k": "v"}, None):
            fails = self._run({"id": "F-X", "backend_ref": bad})
            assert any("R1" in f for f in fails), f"畸形类型 {bad!r} 未被拦截"

    def test_h5_none_value_typed_ok(self) -> None:
        """H5 none: 纯前端声明（合法五前缀）→ 放行。"""
        fails = self._run({"id": "F-X", "backend_ref": "none:纯前端逻辑无后端"})
        assert fails == []


# ── I 类 R4 模块总线攻击 ──────────────────────────────────────────────────────


def _feat(fid: str, page: str, refs: list[str]) -> dict:
    return {"id": fid, "page": page, "backend_ref": refs}


class TestModuleBusAttacks:
    """R4 双向对账（monkeypatch DB 层，不依赖真实 depgraph）。"""

    @pytest.fixture()
    def bus(self, monkeypatch):
        def _run(feats: list[dict], depgraph: list[dict] | None):
            monkeypatch.setattr(cfm, "_load_depgraph_frontend", lambda: depgraph)
            warns: list[str] = []
            fails: list[str] = []
            cfm._check_module_bus(feats, warns, fails)
            return warns, fails

        return _run

    def test_i1_ghost_module_ref(self, bus) -> None:
        """I1 frontend_map 挂不存在的 module:MOD-GHOST → R4 fail。"""
        feats = [_feat("F-A", "stockq", ["module:MOD-GHOST-999"])]
        depgraph = [{"blueprint_id": "MOD-REAL-001", "has_frontend": "no", "frontend_ref": ""}]
        warns, fails = bus(feats, depgraph)
        assert any("MOD-GHOST-999" in f for f in fails)

    def test_i2_dangling_feature_ref(self, bus) -> None:
        """I2 depgraph 挂了 F-GHOST 但 frontend_map 无此功能点 → R4 fail。"""
        feats = [_feat("F-A", "stockq", ["module:MOD-A-001"])]
        depgraph = [{"blueprint_id": "MOD-A-001", "has_frontend": "yes", "frontend_ref": "F-GHOST"}]
        warns, fails = bus(feats, depgraph)
        assert any("F-GHOST" in f and "不存在" in f for f in fails)

    def test_i3_bidirectional_not_closed(self, bus) -> None:
        """I3 depgraph 挂 F-A 但 F-A 未回挂 module:MOD-A-001 → 双向不闭合 fail。"""
        feats = [_feat("F-A", "stockq", ["table:CH.t1"])]
        depgraph = [{"blueprint_id": "MOD-A-001", "has_frontend": "yes", "frontend_ref": "F-A"}]
        warns, fails = bus(feats, depgraph)
        assert any("双向不闭合" in f for f in fails)

    def test_i4_ghost_page_ref(self, bus) -> None:
        """I4 P-GHOST 页面引用不在 page 值域 → R4 fail。"""
        feats = [_feat("F-A", "stockq", ["none:纯前端"])]
        depgraph = [{"blueprint_id": "MOD-A-001", "has_frontend": "no", "frontend_ref": "P-GHOST"}]
        warns, fails = bus(feats, depgraph)
        assert any("P-GHOST" in f for f in fails)

    def test_i5_page_case_insensitive_ok(self, bus) -> None:
        """I5 P-STOCKQ 大写引用 ↔ stockq 页面值 → 大小写归一放行。"""
        feats = [_feat("F-A", "stockq", ["none:纯前端"])]
        depgraph = [{"blueprint_id": "MOD-A-001", "has_frontend": "no", "frontend_ref": "P-STOCKQ"}]
        warns, fails = bus(feats, depgraph)
        assert fails == []

    def test_i6_db_unreachable_degrades_to_warn(self, bus) -> None:
        """I6 depgraph DB 不可达 → warn 降级不产生 fail（不挡 commit 链）。"""
        feats = [_feat("F-A", "stockq", ["module:MOD-WHATEVER"])]
        warns, fails = bus(feats, None)
        assert fails == []
        assert any("降级" in w for w in warns)

    def test_i7_bidirectional_closed_ok(self, bus) -> None:
        """I7 合法双向闭合（模块挂功能点+功能点回挂模块）→ 放行。"""
        feats = [_feat("F-A", "stockq", ["module:MOD-A-001", "table:CH.t1"])]
        depgraph = [
            {"blueprint_id": "MOD-A-001", "has_frontend": "yes", "frontend_ref": "F-A"},
            {"blueprint_id": "MOD-B-002", "has_frontend": "no", "frontend_ref": "P-STOCKQ"},
        ]
        warns, fails = bus(feats, depgraph)
        assert fails == []

    def test_i8_multi_ref_partial_closure(self, bus) -> None:
        """I8 模块挂 F-A 而功能点回挂了别的模块 → 闭合校验按模块逐个比对（漏掉即 fail）。"""
        feats = [_feat("F-A", "stockq", ["module:MOD-OTHER-001"])]
        depgraph = [{"blueprint_id": "MOD-A-001", "has_frontend": "yes", "frontend_ref": "F-A"}]
        warns, fails = bus(feats, depgraph)
        assert any("MOD-A-001" in f and "双向不闭合" in f for f in fails)


# ── K 类 新库必挂门禁攻击 ────────────────────────────────────────────────────


@pytest.fixture()
def fake_catalogs(tmp_path: Path) -> Path:
    """catalogs 目录仿真（拷贝全部真实 yaml → tmp，供增删攻击）。"""
    dst = tmp_path / "catalogs"
    dst.mkdir()
    for f in (_REPO / "docs/01_policies_and_standards/_registry/catalogs").glob("*.yaml"):
        shutil.copy(f, dst / f.name)
    return dst


class TestNewRegistryGateAttacks:
    """攻击 TestNewRegistryGate 判定核心（_unregistered_libs/_missing_axis_files/_stale_exemptions）。"""

    def test_k1_new_unregistered_library_caught(self, fake_catalogs: Path) -> None:
        """K1 塞入未登记新库 → 正向守门必抓。"""
        (fake_catalogs / "brand_new_business_registry.yaml").write_text("entries: []\n", encoding="utf-8")
        caught = tdm._unregistered_libs(fake_catalogs)
        assert caught == {"brand_new_business_registry.yaml"}

    def test_k2_deleted_axis_file_caught(self, fake_catalogs: Path) -> None:
        """K2 删除已挂轴注册表 → 反向守门必抓（防轴文件删除后门禁静默失效）。"""
        (fake_catalogs / "factor_registry.yaml").unlink()
        assert "factor_registry.yaml" in tdm._missing_axis_files(fake_catalogs)

    def test_k3_stale_exemption_caught(self, fake_catalogs: Path) -> None:
        """K3 删除豁免清单内文件 → 豁免卫生检查必抓（防腐烂）。"""
        (fake_catalogs / "ruling_registry.yaml").unlink()
        assert "ruling_registry.yaml" in tdm._stale_exemptions(fake_catalogs)

    def test_k4_governance_exemption_path_ok(self, fake_catalogs: Path, monkeypatch) -> None:
        """K4 新库走豁免登记路径（模拟 AI 做对了②）→ 放行。"""
        (fake_catalogs / "brand_new_gov_registry.yaml").write_text("entries: []\n", encoding="utf-8")
        monkeypatch.setattr(
            tdm, "_GOVERNANCE_EXEMPT", tdm._GOVERNANCE_EXEMPT | {"brand_new_gov_registry.yaml"}
        )
        assert tdm._unregistered_libs(fake_catalogs) == set()

    def test_k5_axis_mount_path_ok(self, fake_catalogs: Path, monkeypatch) -> None:
        """K5 新库走挂轴路径（模拟 AI 做对了①：_XREF_SPECS 加轴）→ 放行。"""
        (fake_catalogs / "brand_new_business_registry.yaml").write_text("entries: []\n", encoding="utf-8")
        monkeypatch.setattr(
            tdm, "_AXIS_FILES", tdm._AXIS_FILES | {"brand_new_business_registry.yaml"}
        )
        assert tdm._unregistered_libs(fake_catalogs) == set()
        assert tdm._missing_axis_files(fake_catalogs) == []

    def test_k6_real_catalogs_clean(self) -> None:
        """K6 真实仓库回归锚：三守门全绿（本套件与主套件双保险）。"""
        assert tdm._unregistered_libs(tdm._REGISTRY_DIR if hasattr(tdm, "_REGISTRY_DIR") else _REPO / "docs/01_policies_and_standards/_registry/catalogs") == set()
