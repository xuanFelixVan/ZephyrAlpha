# [BLUEPRINT] MOD-FBL-002 | docs/03_modules/_domain_feedback_loop/module_matcher/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FBL-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.feedback_loop.test_module_matcher
# [TESTS] src/zephyr/feedback_loop/module_matcher.py
"""MOD-FBL-002 单元测试：module_matcher 模块匹配器。

蓝图验收（B12-03549/CAND-FBL-004，B12）：
capability_tags 注册表搜索（tag 命中预筛）→ embedding 语义相似度（注入
embedder，余弦本地计算）→ EXACT(>0.85)/PARTIAL(0.5~0.85)/NO_MATCH(<0.5)
三档判定（阈值边界恰等归低档）。embedder 全注入内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.feedback_loop.module_matcher",
    reason="module_matcher not importable",
)

from zephyr.feedback_loop.module_matcher import (  # noqa: E402
    MatchTier,
    ModuleMatcher,
    ModuleMatcherError,
)


def _matcher(table: dict, **kwargs) -> ModuleMatcher:
    return ModuleMatcher(embedder=lambda text: table[text], **kwargs)


def _std_matcher() -> ModuleMatcher:
    """三模块标准台：alpha=1.0 / beta=0.5 / gamma=0.0（对需求向量 (1,1,1,1)）。"""
    table = {
        "alpha beta gamma": (1.0, 1.0, 1.0, 1.0),
        "need beta": (1.0, 1.0, 1.0, 1.0),
        "need gamma": (1.0, 1.0, 1.0, 1.0),
        "alpha": (1.0, 1.0, 1.0, 1.0),
        "beta": (1.0, 1.0, 1.0, -1.0),
        "gamma": (1.0, 1.0, -1.0, -1.0),
    }
    m = _matcher(table)
    m.register_module("mod_alpha", ("alpha",))
    m.register_module("mod_beta", ("beta",))
    m.register_module("mod_gamma", ("gamma",))
    return m


# ──────────────────────────────────────────────────────────────────────────────
# 装配校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_non_callable_embedder_raises(self) -> None:
        with pytest.raises(ModuleMatcherError):
            ModuleMatcher(embedder="not-callable")

    def test_invalid_thresholds_raise(self) -> None:
        for kw in (
            {"exact_threshold": 0.5, "partial_threshold": 0.5},   # 恰等非法
            {"exact_threshold": 0.85, "partial_threshold": 0.9},  # 倒置
            {"exact_threshold": 0.85, "partial_threshold": 0.0},  # 下界
            {"exact_threshold": 1.5, "partial_threshold": 0.5},   # 上界
            {"exact_threshold": True, "partial_threshold": 0.5},  # 布尔
        ):
            with pytest.raises(ModuleMatcherError):
                ModuleMatcher(embedder=lambda t: (1.0,), **kw)


# ──────────────────────────────────────────────────────────────────────────────
# capability_tags 注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_ok_and_normalized(self) -> None:
        m = _matcher({"ALPHA 需求": (1.0,), "alpha beta": (1.0,)})
        m.register_module("mod", ("Beta", " ALPHA ", "alpha"))
        result = m.match("ALPHA 需求")
        assert result.best.module_id == "mod"
        assert result.best.matched_tags == ("alpha",)  # 去重+小写规范化

    def test_empty_module_id_raises(self) -> None:
        m = _matcher({})
        for bad in ("", "   "):
            with pytest.raises(ModuleMatcherError):
                m.register_module(bad, ("alpha",))

    def test_duplicate_raises(self) -> None:
        m = _matcher({})
        m.register_module("mod", ("alpha",))
        with pytest.raises(ModuleMatcherError):
            m.register_module("mod", ("beta",))

    def test_empty_tags_raises(self) -> None:
        with pytest.raises(ModuleMatcherError):
            _matcher({}).register_module("mod", ())

    def test_blank_tags_raises(self) -> None:
        with pytest.raises(ModuleMatcherError):
            _matcher({}).register_module("mod", (" ", ""))

    def test_invalid_tag_types_raise(self) -> None:
        with pytest.raises(ModuleMatcherError):
            _matcher({}).register_module("mod", (1, 2))
        with pytest.raises(ModuleMatcherError):
            _matcher({}).register_module("mod", 123)


# ──────────────────────────────────────────────────────────────────────────────
# 匹配（tag 预筛 → 余弦 → 三档判定）
# ──────────────────────────────────────────────────────────────────────────────


class TestMatch:
    def test_exact_tier(self) -> None:
        result = _std_matcher().match("alpha beta gamma")
        assert result.tier is MatchTier.EXACT
        assert result.best.module_id == "mod_alpha"
        assert result.best.score == pytest.approx(1.0)

    def test_candidate_ordering(self) -> None:
        result = _std_matcher().match("alpha beta gamma")
        assert [c.module_id for c in result.candidates] == [
            "mod_alpha", "mod_beta", "mod_gamma",
        ]  # 按 (-score, module_id) 确定性排序

    def test_empty_requirement_raises(self) -> None:
        m = _std_matcher()
        for bad in ("", "   "):
            with pytest.raises(ModuleMatcherError):
                m.match(bad)

    def test_no_tag_overlap_no_match(self) -> None:
        result = _std_matcher().match("zzz 无命中需求")
        assert result.tier is MatchTier.NO_MATCH
        assert result.best is None
        assert result.candidates == ()

    def test_partial_boundary_half(self) -> None:
        m = _std_matcher()
        result = m.match("need beta")
        assert result.best.score == pytest.approx(0.5)
        assert result.tier is MatchTier.PARTIAL  # 恰等 0.5 归低档（非 NO_MATCH）

    def test_exact_boundary_falls_lower(self) -> None:
        table = {"req cap": (4.0, 3.0), "cap": (3.0, 4.0)}  # 余弦恰 24/25=0.96
        m = _matcher(table, exact_threshold=0.96, partial_threshold=0.5)
        m.register_module("mod", ("cap",))
        result = m.match("req cap")
        assert result.best.score == pytest.approx(0.96)
        assert result.tier is MatchTier.PARTIAL  # 恰等 0.96 归低档（非 EXACT）

    def test_mid_partial(self) -> None:
        table = {"req x": (1.0, 0.0), "x": (1.0, 1.0)}  # 余弦≈0.7071
        m = _matcher(table)
        m.register_module("mod", ("x",))
        result = m.match("req x")
        assert result.best.score == pytest.approx(2 ** -0.5)
        assert result.tier is MatchTier.PARTIAL

    def test_low_score_no_match_keeps_candidate(self) -> None:
        result = _std_matcher().match("need gamma")
        assert result.tier is MatchTier.NO_MATCH
        assert result.best.module_id == "mod_gamma"  # 低分候选保留留痕
        assert result.best.score == pytest.approx(0.0)

    def test_tie_sorted_by_module_id(self) -> None:
        table = {"shared": (1.0, 0.0)}
        m = _matcher(table)
        m.register_module("mod_b", ("shared",))
        m.register_module("mod_a", ("shared",))
        result = m.match("shared")
        assert [c.module_id for c in result.candidates] == ["mod_a", "mod_b"]

    def test_chinese_tag_substring(self) -> None:
        table = {"需要因子衰减检测能力": (1.0, 0.0), "因子衰减": (1.0, 0.0)}
        m = _matcher(table)
        m.register_module("alpha_decay", ("因子衰减",), "")
        result = m.match("需要因子衰减检测能力")
        assert result.tier is MatchTier.EXACT
        assert result.best.matched_tags == ("因子衰减",)

    def test_description_joins_cap_text(self) -> None:
        table = {"y 需求": (1.0, 0.0), "y 描述文本": (1.0, 0.0)}
        m = _matcher(table)
        m.register_module("mod", ("y",), "描述文本")
        assert m.match("y 需求").tier is MatchTier.EXACT

    def test_dim_mismatch_raises(self) -> None:
        table = {"req q": (1.0, 0.0), "q": (1.0, 0.0, 0.0)}
        m = _matcher(table)
        m.register_module("mod", ("q",))
        with pytest.raises(ModuleMatcherError):
            m.match("req q")

    def test_empty_vector_raises(self) -> None:
        table = {"req q": (), "q": (1.0,)}
        m = _matcher(table)
        m.register_module("mod", ("q",))
        with pytest.raises(ModuleMatcherError):
            m.match("req q")

    def test_zero_norm_vector_score_zero(self) -> None:
        table = {"req q": (1.0, 0.0), "q": (0.0, 0.0)}
        m = _matcher(table)
        m.register_module("mod", ("q",))
        result = m.match("req q")
        assert result.best.score == 0.0
        assert result.tier is MatchTier.NO_MATCH

    def test_embedder_exception_wrapped(self) -> None:
        m = _matcher({})  # 表缺键 -> KeyError
        m.register_module("mod", ("q",))
        with pytest.raises(ModuleMatcherError):
            m.match("req q")

    def test_non_numeric_vector_raises(self) -> None:
        table = {"req q": ("a", "b"), "q": (1.0, 0.0)}
        m = _matcher(table)
        m.register_module("mod", ("q",))
        with pytest.raises(ModuleMatcherError):
            m.match("req q")

    def test_determinism(self) -> None:
        r1 = _std_matcher().match("alpha beta gamma")
        r2 = _std_matcher().match("alpha beta gamma")
        assert r1 == r2  # 同输入必同输出
