# [BLUEPRINT] MOD-ALT-005 | docs/03_modules/_domain_alt_data/policy_theme_mapper/blueprint.md | §test
# [MODULE] tests.alt_data.test_policy_theme_mapper
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.alt_data.policy_theme_mapper
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_policy_theme_mapper.py
# [A_test] module_id: MOD-ALT-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-ALT-005 单元测试: PolicyThemeMapper — 政策主题映射器。

覆盖: 主题归类（各主题命中/库优先序/无命中 unmatched）、半衰期热度（age=0
→1.0/age=half_life→0.5/多条加总）、受益受损清单（加总/降序/同值字典序）、
LLM 路径（合法采纳/未知主题回落留痕/异常回落留痕）、PIT 未来新闻拒绝、
单条与主题库 Fail-Closed、确定性、frozen。
"""

from __future__ import annotations

import datetime
from dataclasses import FrozenInstanceError

import pytest

from zephyr.alt_data.policy_theme_mapper import (
    DEFAULT_THEME_LIBRARY,
    InvalidPolicyNewsError,
    InvalidPolicyThemeConfigError,
    PolicyNewsItem,
    PolicyTheme,
    PolicyThemeMapper,
)

AS_OF = datetime.date(2026, 8, 25)


def _item(news_id: str, title: str, days_ago: int = 0, text: str = "") -> PolicyNewsItem:
    return PolicyNewsItem(
        news_id=news_id,
        title=title,
        text=text,
        publish_date=AS_OF - datetime.timedelta(days=days_ago),
        source="unit",
    )


@pytest.fixture
def mapper() -> PolicyThemeMapper:
    return PolicyThemeMapper()


class TestClassify:
    def test_each_theme_hit(self, mapper):
        cases = {
            "央行降准释放流动性": "货币政策",
            "新一轮产业规划与补贴落地": "产业政策",
            "监管对违规机构开出处罚": "监管政策",
            "专项债提速基建加码": "财政政策",
            "加征关税引发贸易摩擦": "贸易政策",
        }
        for title, theme_id in cases.items():
            assert mapper.classify_one(_item("N1", title))[0] == theme_id

    def test_library_priority_first_match(self):
        lib = (
            PolicyTheme("A主题", ("共有词",), 10, ("甲",), ()),
            PolicyTheme("B主题", ("共有词",), 10, ("乙",), ()),
        )
        m = PolicyThemeMapper(theme_library=lib)
        assert m.classify_one(_item("N1", "共有词 新闻"))[0] == "A主题"

    def test_no_match_returns_none(self, mapper):
        theme_id, classifier, invalid = mapper.classify_one(_item("N1", "普通市场快讯"))
        assert theme_id is None
        assert classifier == "rule"
        assert invalid is False

    def test_keyword_in_text_also_hits(self, mapper):
        assert mapper.classify_one(_item("N1", "快讯", text="央行宣布降息"))[0] == "货币政策"

    def test_classify_one_wrong_type(self, mapper):
        with pytest.raises(InvalidPolicyNewsError):
            mapper.classify_one({"title": "x"})  # type: ignore[arg-type]


class TestHeatDecay:
    def test_age_zero_weight_one(self, mapper):
        rep = mapper.map_theme([_item("N1", "央行降准")], AS_OF)
        assert rep.themes[0].heat == pytest.approx(1.0)

    def test_half_life_weight_half(self, mapper):
        rep = mapper.map_theme([_item("N1", "央行降准", days_ago=20)], AS_OF)
        assert rep.themes[0].heat == pytest.approx(0.5)

    def test_heat_sums_multiple_items(self, mapper):
        rep = mapper.map_theme(
            [_item("N1", "央行降准", days_ago=0), _item("N2", "MLF 续作", days_ago=20)], AS_OF
        )
        assert rep.themes[0].theme_id == "货币政策"
        assert rep.themes[0].heat == pytest.approx(1.5)
        assert rep.themes[0].news_count == 2

    def test_themes_sorted_by_heat_desc(self, mapper):
        rep = mapper.map_theme(
            [
                _item("N1", "央行降准", days_ago=60),  # 货币 heat=0.125
                _item("N2", "产业规划补贴", days_ago=0),  # 产业 heat=1.0
            ],
            AS_OF,
        )
        assert [t.theme_id for t in rep.themes] == ["产业政策", "货币政策"]


class TestBeneficiaryDamaged:
    def test_beneficiary_aggregation_and_order(self, mapper):
        rep = mapper.map_theme(
            [
                _item("N1", "央行降准", days_ago=0),  # 货币 heat 1.0 → 银行/非银/地产
                _item("N2", "专项债基建", days_ago=0),  # 财政 heat 1.0 → 建筑/建材/工程机械
            ],
            AS_OF,
        )
        # 同 heat=1.0 → 行业名字典序
        names = [n for n, _ in rep.beneficiary_list]
        assert names == sorted(names)
        assert set(names) == {"银行", "非银金融", "房地产", "建筑", "建材", "工程机械"}
        assert all(h == pytest.approx(1.0) for _, h in rep.beneficiary_list)

    def test_damaged_list(self, mapper):
        rep = mapper.map_theme([_item("N1", "监管处罚立案")], AS_OF)
        assert {n for n, _ in rep.damaged_list} == {"非银金融", "房地产", "互联网"}
        assert rep.beneficiary_list == ()

    def test_unmatched_excluded_from_heat(self, mapper):
        rep = mapper.map_theme([_item("N1", "无关新闻"), _item("N2", "央行降准")], AS_OF)
        assert rep.unmatched == 1
        assert len(rep.themes) == 1
        assert rep.themes[0].theme_id == "货币政策"


class TestLlmPath:
    def test_llm_valid_adopted(self):
        m = PolicyThemeMapper(llm_classifier=lambda item: {"theme_id": "贸易政策"})
        theme_id, classifier, invalid = m.classify_one(_item("N1", "普通标题"))
        assert (theme_id, classifier, invalid) == ("贸易政策", "llm", False)

    def test_llm_none_theme_accepted_as_unmatched(self):
        m = PolicyThemeMapper(llm_classifier=lambda item: {"theme_id": None})
        theme_id, classifier, invalid = m.classify_one(_item("N1", "央行降准"))
        assert (theme_id, classifier, invalid) == (None, "llm", False)

    def test_llm_unknown_theme_fallback_rule_ledger(self):
        m = PolicyThemeMapper(llm_classifier=lambda item: {"theme_id": "外星主题"})
        theme_id, classifier, invalid = m.classify_one(_item("N1", "央行降准"))
        assert (theme_id, classifier, invalid) == ("货币政策", "rule", True)

    def test_llm_bad_structure_fallback(self):
        m = PolicyThemeMapper(llm_classifier=lambda item: "not-a-mapping")  # type: ignore[return-value]
        theme_id, classifier, invalid = m.classify_one(_item("N1", "央行降准"))
        assert (theme_id, classifier, invalid) == ("货币政策", "rule", True)

    def test_llm_exception_fallback_not_block(self):
        def _boom(item):
            raise RuntimeError("llm down")

        m = PolicyThemeMapper(llm_classifier=_boom)
        rep = m.map_theme([_item("N1", "央行降准")], AS_OF)
        assert rep.accepted == 1
        assert rep.llm_invalid == 1
        assert rep.themes[0].theme_id == "货币政策"


class TestFailClosed:
    def test_blank_fields(self):
        with pytest.raises(InvalidPolicyNewsError):
            _item(" ", "标题")
        with pytest.raises(InvalidPolicyNewsError):
            _item("N1", " ")

    def test_bad_publish_date(self):
        with pytest.raises(InvalidPolicyNewsError):
            PolicyNewsItem(news_id="N1", title="t", text="", publish_date="2026-08-25", source="")  # type: ignore[arg-type]

    def test_future_news_rejected(self, mapper):
        rep = mapper.map_theme([_item("N1", "央行降准", days_ago=-1)], AS_OF)
        assert rep.rejected == 1
        assert rep.accepted == 0

    def test_bad_as_of(self, mapper):
        with pytest.raises(InvalidPolicyNewsError):
            mapper.map_theme([], "2026-08-25")  # type: ignore[arg-type]

    def test_bad_library(self):
        with pytest.raises(InvalidPolicyThemeConfigError):
            PolicyThemeMapper(theme_library=[])
        with pytest.raises(InvalidPolicyThemeConfigError):
            PolicyThemeMapper(
                theme_library=(
                    PolicyTheme("A", ("x",), 10, (), ()),
                    PolicyTheme("A", ("y",), 10, (), ()),
                )
            )
        with pytest.raises(InvalidPolicyThemeConfigError):
            PolicyThemeMapper(theme_library=(PolicyTheme("A", (), 10, (), ()),))
        with pytest.raises(InvalidPolicyThemeConfigError):
            PolicyThemeMapper(theme_library=(PolicyTheme("A", ("x",), 0, (), ()),))
        with pytest.raises(InvalidPolicyThemeConfigError):
            PolicyThemeMapper(theme_library=("not-a-theme",))  # type: ignore[arg-type]

    def test_bad_llm_classifier(self):
        with pytest.raises(InvalidPolicyThemeConfigError):
            PolicyThemeMapper(llm_classifier="x")  # type: ignore[arg-type]

    def test_default_library_valid(self):
        assert len(DEFAULT_THEME_LIBRARY) == 5
        PolicyThemeMapper()  # 不抛即通过


class TestBatchAndDeterminism:
    def test_mixed_rows_rejected_ledger(self, mapper):
        rep = mapper.map_theme(
            [
                _item("N1", "央行降准"),
                {"news_id": "N2", "title": " ", "text": "", "publish_date": AS_OF, "source": ""},
                _item("N3", "产业补贴"),
            ],
            AS_OF,
        )
        assert rep.items_in == 3
        assert rep.accepted == 2
        assert rep.rejected == 1
        assert rep.errors[0][0] == 1

    def test_determinism(self, mapper):
        items = [
            _item("N1", "央行降准", days_ago=3),
            _item("N2", "专项债基建", days_ago=7),
            _item("N3", "监管处罚", days_ago=1),
        ]
        r1 = mapper.map_theme(items, AS_OF)
        r2 = mapper.map_theme(items, AS_OF)
        assert r1 == r2

    def test_frozen(self, mapper):
        item = _item("N1", "t")
        with pytest.raises(FrozenInstanceError):
            item.title = "x"  # type: ignore[misc]
        rep = mapper.map_theme([_item("N1", "央行降准")], AS_OF)
        with pytest.raises(FrozenInstanceError):
            rep.themes[0].heat = 9.9  # type: ignore[misc]
