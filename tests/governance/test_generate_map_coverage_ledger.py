# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md | §coverage ledger tests
# [MODULE] tests.governance.test_generate_map_coverage_ledger
# [DOMAIN] D_TRADING
# [DEPENDENCIES] pytest; scripts.generate_map_coverage_ledger
# [CONSUMERS] 覆盖账本生成器质量守卫（三分类判据+折算两级+人口扫描+确定性渲染）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 单元用例全部构造于 tmp_path 假仓（monkeypatch 模块常量，零生产写）；分类核为纯函数直测；输出禁 datetime（确定性=字节对拍）
# [MODIFY-GUARD] 与生成器同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-TRADING-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_map_coverage_ledger 机生守卫——三分类判据/路径折算/人口扫描/确定性渲染全直测。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import generate_map_coverage_ledger as g  # noqa: E402


class TestBuildLedger:
    """三分类判据：已挂/未挂孤儿红/跨域挂载 + 无主附录 + 计数字段守恒。"""

    POPULATION = [
        {
            "module_id": "MOD-SIG-001",
            "blueprint": "docs/03_modules/_domain_signal/a/blueprint.md",
            "domain_dir": "_domain_signal",
            "blueprint_domain": "D_ASHARE_SIGNAL",
            "blueprint_id": "MOD-SIG-001",
        },
        {
            "module_id": "MOD-SIG-002",
            "blueprint": "docs/03_modules/_domain_signal/b/blueprint.md",
            "domain_dir": "_domain_signal",
            "blueprint_domain": "D_ASHARE_SIGNAL",
            "blueprint_id": "MOD-SIG-002",
        },
        {
            "module_id": "MOD-RISK-001",
            "blueprint": "docs/03_modules/_domain_risk/c/blueprint.md",
            "domain_dir": "_domain_risk",
            "blueprint_domain": "D_RISK",
            "blueprint_id": "MOD-RISK-001",
        },
    ]
    MODULE_DOMAIN = {
        "MOD-SIG-001": "D_ASHARE_SIGNAL",
        "MOD-SIG-002": "D_ASHARE_SIGNAL",
        "MOD-RISK-001": "D_RISK",
        "MOD-NEWS-001": "D_INTELLIGENCE",  # 外域=伸手进交易流程
    }
    TRADING_DOMAINS = {"D_ASHARE_SIGNAL", "D_RISK"}

    def _build(self, tdm_ids, ref_modules, ref_unresolved=()):
        return g.build_ledger(
            self.POPULATION,
            set(tdm_ids),
            set(ref_modules),
            list(ref_unresolved),
            self.MODULE_DOMAIN,
            self.TRADING_DOMAINS,
        )

    def test_three_way_classification(self):
        ledger = self._build({"MOD-SIG-001"}, {"MOD-SIG-002"})
        assert ledger["mounted"] == ["MOD-SIG-001", "MOD-SIG-002"]
        assert ledger["unmounted_orphan"] == ["MOD-RISK-001"]
        assert ledger["cross_domain_mount"] == []
        assert ledger["mounted_unresolved"] == []

    def test_cross_domain_mount_when_module_outside_trading_domains(self):
        ledger = self._build(set(), {"MOD-NEWS-001"})
        assert ledger["cross_domain_mount"] == ["MOD-NEWS-001"]
        assert "MOD-NEWS-001" not in ledger["mounted"]

    def test_mounted_unresolved_when_domain_unknown(self):
        ledger = self._build({"MOD-GHOST-999"}, set())
        assert ledger["mounted_unresolved"] == ["MOD-GHOST-999"]
        assert ledger["cross_domain_mount"] == []

    def test_counts_fields_consistent(self):
        ledger = self._build({"MOD-SIG-001"}, {"MOD-NEWS-001"}, ["lost.py"])
        c = ledger["counts"]
        assert c["population_with_id"] == 3
        assert c["mounted"] == 1
        assert c["unmounted_orphan"] == 2
        assert c["cross_domain_mount"] == 1
        assert c["ref_unresolved"] == 1
        assert c["ref_folded_to_module"] == 1
        assert c["tdm_module_ref_unique"] == 2  # folded 1 + unresolved 1

    def test_ref_unresolved_reported_verbatim(self):
        ledger = self._build(set(), set(), ["src/zephyr/nope/ghost.py"])
        assert ledger["ref_unresolved"] == ["src/zephyr/nope/ghost.py"]


class TestFoldRef:
    """module_ref 折算两级：精确路径 → 包名前缀；反斜杠归一；未命中 None。"""

    PATH_MAP = {"src/zephyr/plan_engine/daily_trade_plan.py": "MOD-PLAN-011"}
    PKG_MAP = {"plan_engine": "MOD-PLAN-011", "regime": "MOD-REG-001"}

    def test_exact_path_hit(self):
        assert g.fold_ref("src/zephyr/plan_engine/daily_trade_plan.py", self.PATH_MAP, self.PKG_MAP) == "MOD-PLAN-011"

    def test_package_fallback(self):
        assert g.fold_ref("src/zephyr/regime/core/regime_detector.py", self.PATH_MAP, self.PKG_MAP) == "MOD-REG-001"

    def test_backslash_normalized(self):
        assert (
            g.fold_ref("src\\zephyr\\plan_engine\\daily_trade_plan.py", self.PATH_MAP, self.PKG_MAP) == "MOD-PLAN-011"
        )

    def test_outside_src_zephyr_returns_none(self):
        assert g.fold_ref("scripts/foo.py", self.PATH_MAP, self.PKG_MAP) is None

    def test_unknown_package_returns_none(self):
        assert g.fold_ref("src/zephyr/ghost_pkg/x.py", self.PATH_MAP, self.PKG_MAP) is None


class TestScanPopulation:
    """人口扫描：tmp 假仓 monkeypatch MODULES_ROOT；module_id/blueprint_id 分流。"""

    def _make_repo(self, tmp_path: Path) -> None:
        dird = tmp_path / "docs" / "03_modules" / "_domain_signal"
        (dird / "with_id").mkdir(parents=True)
        (dird / "with_id" / "blueprint.md").write_text(
            "---\nmodule_id: MOD-SIG-001\nblueprint_id: MOD-SIG-001\ndomain: D_ASHARE_SIGNAL\n---\nbody\n",
            encoding="utf-8",
        )
        (dird / "without_id").mkdir(parents=True)
        (dird / "without_id" / "blueprint.md").write_text(
            "---\nblueprint_id: MOD-SIG-089\ndomain: D_ASHARE_SIGNAL\n---\nbody\n",
            encoding="utf-8",
        )

    def test_split_and_fields(self, tmp_path, monkeypatch):
        self._make_repo(tmp_path)
        monkeypatch.setattr(g, "MODULES_ROOT", tmp_path / "docs" / "03_modules")
        monkeypatch.setattr(g, "DOMAIN_DIRS", ("signal",))
        with_id, without_id = g.scan_population()
        assert [p["module_id"] for p in with_id] == ["MOD-SIG-001"]
        assert [p["blueprint_id"] for p in without_id] == ["MOD-SIG-089"]
        assert all(p["blueprint_domain"] == "D_ASHARE_SIGNAL" for p in with_id + without_id)

    def test_missing_domain_dir_fails_closed(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "MODULES_ROOT", tmp_path / "nonexistent")
        monkeypatch.setattr(g, "DOMAIN_DIRS", ("signal",))
        with pytest.raises(FileNotFoundError):
            g.scan_population()


class TestRenderDeterminism:
    """渲染确定性：同输入两次渲染字节相等（禁 datetime 注入）。"""

    def test_yaml_render_byte_stable(self):
        ledger = g.build_ledger(
            [
                {
                    "module_id": "MOD-SIG-001",
                    "blueprint": "x",
                    "domain_dir": "_domain_signal",
                    "blueprint_domain": "D_ASHARE_SIGNAL",
                    "blueprint_id": "MOD-SIG-001",
                }
            ],
            {"MOD-SIG-001"},
            set(),
            [],
            {"MOD-SIG-001": "D_ASHARE_SIGNAL"},
            {"D_ASHARE_SIGNAL"},
        )
        without_id = [
            {"blueprint": "docs/x/blueprint.md", "blueprint_id": "MOD-SIG-089", "blueprint_domain": "D_ASHARE_SIGNAL"}
        ]
        assert g.render_yaml(ledger, without_id, "anchor-1") == g.render_yaml(ledger, without_id, "anchor-1")

    def test_md_render_contains_count_fields(self):
        ledger = g.build_ledger([], set(), set(), [], {}, set())
        md = g.render_markdown(ledger, [], [], {"mounted": "已挂(mounted)"}, "anchor-1")
        assert "- population_with_id: 0" in md
        assert "anchor-1" in md
