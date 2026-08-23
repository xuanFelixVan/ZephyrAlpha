# [BLUEPRINT] MOD-NLP-IMPACT-001 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-22 行）
# [MODULE] tests.nlp.test_news_impact_grader
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.nlp.news_impact_grader
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=新闻影响分级/热点聚类逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-NLP-IMPACT-001_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-NLP-IMPACT-001 新闻影响评估分级+热点聚类 单元测试（GAP-F-22，合成数据）。

覆盖：A/B/C 三级封闭（A=宏观政策关键词、B=题材/行业命中、C=兜底）、
热点主题计数+排序（"半导体 ×N"形态）、多源共振标注、主题样本截断、
空输入降级、非法输入 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.nlp.news_impact_grader import (
    GRADE_A,
    GRADE_B,
    GRADE_C,
    NewsImpactConfig,
    NewsItemInput,
    grade_and_cluster_news,
)


def _cfg(**kw) -> NewsImpactConfig:
    return NewsImpactConfig(**kw)


def _news(news_id: str, title: str, source: str = "eastmoney", content: str = "") -> NewsItemInput:
    return NewsItemInput(news_id=news_id, title=title, content=content, source=source, publish_time="2026-08-21 10:00")


NEWS = [
    _news("a1", "央行宣布降准0.5个百分点 释放长期资金", "cls"),
    _news("a2", "国务院关税税则委员会发布公告", "eastmoney"),
    _news("b1", "半导体国产化加速 晶圆厂密集扩产", "eastmoney"),
    _news("b2", "光刻机自主可控再进一步 芯片产业链受益", "cls"),
    _news("b3", "某公司签订重大销售合同", "eastmoney"),
    _news("c1", "今日两市主力资金流向一览", "eastmoney"),
    _news("c2", "某上市公司高管变动公告", "cls"),
]


# ------------------------------------------------------------------
# 分级
# ------------------------------------------------------------------


def test_grade_a_policy_keywords() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    grades = {g.news_id: g.grade for g in out.graded}
    assert grades["a1"] == GRADE_A  # 央行+降准
    assert grades["a2"] == GRADE_A  # 国务院+关税


def test_grade_b_theme_hits() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    grades = {g.news_id: g.grade for g in out.graded}
    assert grades["b1"] == GRADE_B  # 半导体题材
    assert grades["b2"] == GRADE_B
    assert grades["b3"] == GRADE_B  # 订单/合同（行业公司级）


def test_grade_c_fallback() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    grades = {g.news_id: g.grade for g in out.graded}
    assert grades["c1"] == GRADE_C
    assert grades["c2"] == GRADE_C


def test_grade_summary_counts() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    assert out.grade_counts[GRADE_A] == 2
    assert out.grade_counts[GRADE_B] == 3
    assert out.grade_counts[GRADE_C] == 2


def test_grade_reason_attached() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    g = next(g for g in out.graded if g.news_id == "a1")
    assert "央行" in g.reason or "降准" in g.reason


# ------------------------------------------------------------------
# 热点聚类
# ------------------------------------------------------------------


def test_hotspot_theme_counting_and_order() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    assert out.hotspots
    top = out.hotspots[0]
    assert top.theme == "半导体"
    assert top.count == 2  # b1+b2
    assert set(top.sample_news_ids) == {"b1", "b2"}


def test_hotspot_multi_source_flag() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    top = out.hotspots[0]
    assert top.multi_source is True  # eastmoney+cls 双源
    assert len(top.sources) == 2


def test_hotspot_sample_cap() -> None:
    news = [_news(f"s{i}", f"半导体新闻{i}") for i in range(10)]
    out = grade_and_cluster_news(news, config=_cfg(max_samples_per_theme=3))
    assert out.hotspots[0].count == 10
    assert len(out.hotspots[0].sample_news_ids) <= 3


def test_no_theme_no_hotspots() -> None:
    out = grade_and_cluster_news([NEWS[5], NEWS[6]], config=_cfg())
    assert out.hotspots == []


def test_empty_input_degraded() -> None:
    out = grade_and_cluster_news([], config=_cfg())
    assert out.degraded is True
    assert out.graded == []
    assert out.hotspots == []


def test_invalid_item_fail_closed() -> None:
    with pytest.raises(ValueError, match="news_items 元素非法"):
        grade_and_cluster_news([{"x": 1}], config=_cfg())  # type: ignore[list-item]


def test_theme_keywords_override() -> None:
    cfg = _cfg(theme_keywords={"军工": ("导弹", "航母")})
    news = [_news("m1", "航母编队演练 导弹试射成功")]
    out = grade_and_cluster_news(news, config=cfg)
    assert out.hotspots[0].theme == "军工"
    assert out.graded[0].grade == GRADE_B


def test_json_serializable() -> None:
    out = grade_and_cluster_news(NEWS, config=_cfg())
    json.dumps(asdict(out), ensure_ascii=False)
