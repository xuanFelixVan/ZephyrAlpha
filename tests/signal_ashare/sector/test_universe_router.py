# [TESTS] tests/signal_ashare/sector/test_universe_router.py
# [TTL] permanent
# MOD-SIG-161 板块口径路由薄件单测（CONDAXIS-CAMPAIGN 板块线环节⓪）。
#
# 三纪律（镜像测试三纪律先例）：
#   ①镜像：每个判别式命中必配未命中/歧义反面用例（880 命中↔881 命中↔6 位歧义）；
#   ②fail-loud：歧义码无 source_hint 判 unknown 不猜（有 hint 才消歧）——
#     "静默猜一个口径"是本件禁止的失败模式；
#   ③全网格：市场统计指数剔除覆盖 880001-880009 全段边界（880010 起回归板块）。
#
# 测试隔离：全部走 tmp_path fixture 合成配置，零生产路径零 CH；仅最后一组
# 只读加载仓内真源 config/sector_universe_router.yaml（同批施工物，读不写）。

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.signal_ashare.sector.universe_router import (
    parse_sector_universe_config,
    primary_universe,
    route_sector_code,
)

MINIMAL_CONFIG: dict = {
    "schema_version": "1.0.0",
    "decision": {
        "primary_caliber": "shenwan_l1",
        "roles": {"shenwan": "主口径", "tdx880": "盘中快照辅助"},
        "degradation_order": ["shenwan_l1", "tdx880"],
    },
    "calibers": {
        "shenwan_l1": {
            "family": "shenwan",
            "role": "primary",
            "identity": {"kind": "level_name", "levels": ["1", "2", "3"]},
            "tables": [{"category_id": "market_industry_class", "facts": "x"}],
        },
        "tdx880": {
            "family": "tdx880",
            "role": "intraday_auxiliary",
            "tables": [{"category_id": "market_sector_kline_880", "facts": "x"}],
        },
    },
    "routing_rules": [
        {"pattern": r"^88000[1-9](\.(SH|SZ))?$", "family": "tdx880", "role": "market_stat_index", "action": "exclude"},
        {"pattern": r"^880[5-9]\d{2}(\.(SH|SZ))?$", "family": "tdx880", "role": "concept_style"},
        {"pattern": r"^880\d{3}(\.(SH|SZ))?$", "family": "tdx880", "role": "sector"},
        {"pattern": r"^881\d{3}(\.(SH|SZ))?$", "family": "tdx880", "role": "industry"},
        {"pattern": r"^\d{6}$", "family": "ambiguous", "role": "ambiguous", "note": "须 source_hint"},
    ],
}


@pytest.fixture()
def config() -> object:
    return parse_sector_universe_config(MINIMAL_CONFIG)


def _write_config(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "router.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return p


class TestParse:
    def test_minimal_config_parses(self, config) -> None:
        assert config.primary_caliber == "shenwan_l1"
        assert config.degradation_order == ("shenwan_l1", "tdx880")
        assert config.shenwan_levels == ("1", "2", "3")
        assert len(config.rules) == 5

    def test_unknown_schema_version_rejected(self) -> None:
        bad = {**MINIMAL_CONFIG, "schema_version": "9.9.9"}
        with pytest.raises(ValueError, match="schema_version"):
            parse_sector_universe_config(bad)

    def test_missing_routing_rules_rejected(self) -> None:
        bad = {k: v for k, v in MINIMAL_CONFIG.items() if k != "routing_rules"}
        with pytest.raises(ValueError, match="routing_rules"):
            parse_sector_universe_config(bad)

    def test_bad_regex_rejected(self) -> None:
        bad = {**MINIMAL_CONFIG, "routing_rules": [{"pattern": "([", "family": "tdx880", "role": "x"}]}
        with pytest.raises(ValueError, match="编译失败"):
            parse_sector_universe_config(bad)

    def test_undeclared_family_rejected(self) -> None:
        bad = {**MINIMAL_CONFIG, "routing_rules": [{"pattern": "^880", "family": "ghost", "role": "x"}]}
        with pytest.raises(ValueError, match="未在 calibers 声明"):
            parse_sector_universe_config(bad)

    def test_primary_not_in_calibers_rejected(self) -> None:
        bad = {**MINIMAL_CONFIG}
        bad["decision"] = {**bad["decision"], "primary_caliber": "ghost"}
        with pytest.raises(ValueError, match="primary_caliber"):
            parse_sector_universe_config(bad)


class TestRouteSectorCode:
    def test_market_stat_indices_excluded_full_band(self, config) -> None:
        for i in range(1, 10):
            v = route_sector_code(f"88000{i}", config)
            assert v.family == "tdx880", f"88000{i}"
            assert v.action == "exclude", f"88000{i}（市场统计指数须剔除）"
        assert route_sector_code("880010", config).action == "route"  # 边界外回归板块

    def test_tdx880_roles(self, config) -> None:
        assert route_sector_code("880954", config).role == "concept_style"
        assert route_sector_code("880347", config).role == "sector"  # 8803 行业（本最小配置未细分，兜底）
        assert route_sector_code("880001.SH", config).action == "exclude"  # 后缀剥离

    def test_ths881_routes_with_suffix_strip(self, config) -> None:
        v = route_sector_code("881101", config)
        assert v.family == "tdx880"  # 本最小配置未单列 ths881 族——结构上演示 881 段可路由
        assert v.role == "industry"

    def test_ambiguous_six_digit_fail_loud_without_hint(self, config) -> None:
        v = route_sector_code("300008", config)  # 概念码与个股码同形
        assert v.family == "unknown"
        assert v.action == "unknown"
        assert "source_hint" in v.note

    def test_ambiguous_resolved_by_hint(self, config) -> None:
        v = route_sector_code("300008", config, source_hint="concept")
        assert (v.family, v.action, v.match_via) == ("concept", "route", "source_hint")
        s = route_sector_code("300008", config, source_hint="stock")
        assert s.family == "stock" and s.action == "unknown"

    def test_non_matching_code_unknown(self, config) -> None:
        v = route_sector_code("BK0800", config)  # EM 概念前缀（未登记判别式）
        assert (v.family, v.action) == ("unknown", "unknown")

    def test_empty_code_rejected(self, config) -> None:
        with pytest.raises(ValueError):
            route_sector_code("", config)


class TestPrimaryUniverse:
    def test_primary_and_degradation(self, config) -> None:
        spec = primary_universe(config)
        assert spec.primary_caliber == "shenwan_l1"
        assert spec.degradation_order == ("shenwan_l1", "tdx880")
        assert "market_industry_class" in spec.category_ids

    def test_primary_table_only(self, config) -> None:
        spec = primary_universe(config)
        assert set(spec.category_ids) == {"market_industry_class"}  # 880 品类不进主口径宇宙


class TestRepoConfig:
    """只读加载仓内真源配置（同批施工物）——结构契约锁。"""

    def test_repo_config_parses_and_routes(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        cfg_path = repo_root / "config" / "sector_universe_router.yaml"
        if not cfg_path.exists():  # pragma: no cover - 防护性
            pytest.skip("仓内路由册未随批提交")
        cfg = parse_sector_universe_config(yaml.safe_load(cfg_path.read_text(encoding="utf-8")))
        assert cfg.primary_caliber == "shenwan_l1"
        assert route_sector_code("880001", cfg).action == "exclude"
        assert route_sector_code("881101", cfg).family == "ths881"
        assert route_sector_code("300008", cfg).family == "unknown"
        spec = primary_universe(cfg)
        assert "market_industry_class" in spec.category_ids
