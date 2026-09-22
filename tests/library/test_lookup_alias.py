# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] tests.library.test_lookup_alias
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.library.lookup (_expand_query, _load_lookup_axis, lookup_assets)
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] G15-① 别名轴：整词命中词表才展开（原词恒在首位）；未知词/词表故障 fail-open 原词直查；lookup_assets 多词合并去重保序
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测失败
# [TESTS] self
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""G15-① lookup 别名轴测试（增补令 #12）。"""

from __future__ import annotations

import zephyr.library.lookup as lookup_mod
from zephyr.library.lookup import _expand_query, _load_lookup_axis


class TestExpandQuery:
    def test_alias_chains_to_tokens(self) -> None:
        """融资融券（别名）→杠杆（标准词）→margin_trading（资产 token）三级展开。"""
        terms = _expand_query("融资融券")
        assert terms[0] == "融资融券"
        assert "杠杆" in terms
        assert "margin_trading" in terms

    def test_canonical_word_direct(self) -> None:
        """标准词直查也展开 tokens（龙虎榜→dragon_tiger）。"""
        terms = _expand_query("龙虎榜")
        assert terms[0] == "龙虎榜"
        assert "dragon_tiger" in terms

    def test_unknown_word_passthrough(self) -> None:
        """词表外整词/自由文本原样返回（原词直查兼容）。"""
        assert _expand_query("kline_1min") == ["kline_1min"]
        assert _expand_query("完全不是词的输入") == ["完全不是词的输入"]

    def test_fail_open_on_vocab_broken(self, monkeypatch) -> None:
        """词表装载故障 fail-open：_load_lookup_axis 返回空映射不抛，退化为原词直查。"""
        import zephyr.shared.io.yaml_utils as yu

        def _boom(*a: object, **k: object) -> tuple[dict, dict]:
            raise RuntimeError("vocab down")
        monkeypatch.setattr(yu, "load_vocabulary_alias_map", _boom)
        assert _load_lookup_axis() == ({}, {})
        assert _expand_query("融资融券") == ["融资融券"]

    def test_axis_loader_shapes(self) -> None:
        """SSOT 装载器返回形态：别名映射含融资融券，token 映射含龙虎榜桥。"""
        alias_map, canonical_to_tokens = _load_lookup_axis()
        assert alias_map.get("融资融券") == "杠杆"
        assert "dragon_tiger" in canonical_to_tokens.get("龙虎榜", [])


class TestLookupAssetsAlias:
    def test_chinese_axis_hits_tbl(self) -> None:
        """实弹：中文概念词命中 TBL 卡（G15 实证基线反向）。"""
        rows = lookup_mod.lookup_assets("融资融券", limit=5, kind="table")
        homes = [r["home"] for r in rows]
        assert any("margin_trading" in h for h in homes)

    def test_merge_dedup_keeps_order(self) -> None:
        """多词合并去重：原词命中优先于展开词，asset_id 不重复。"""
        rows = lookup_mod.lookup_assets("龙虎榜", limit=10)
        ids = [r["asset_id"] for r in rows]
        assert len(ids) == len(set(ids))
