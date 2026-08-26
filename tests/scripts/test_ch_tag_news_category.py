# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_ch_tag_news_category.py — category 刷标脚本单元测试（CAND-DAT-024）。

覆盖（FakeClient 零外部依赖，不触达 ClickHouse）：
  1. RULES 契约 —— 四类齐/特标排除自身/news 兜底只扫 general/全部带 region+language 过滤
  2. apply_rule —— ALTER 语句形态+mutation 轮询退出
  3. count_rule —— count 查询形态
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "tag_news_category",
    _ROOT / "scripts" / "ch" / "tag_news_category.py",
)
tnc = importlib.util.module_from_spec(_spec)
sys.modules["tag_news_category"] = tnc
_spec.loader.exec_module(tnc)


class _FakeClient:
    """记录 SQL 的伪客户端：count→给定值，mutation pending 首轮 1 次轮 0。"""

    def __init__(self, count_result: int = 0):
        self.sqls: list[str] = []
        self._count = count_result
        self._mut_calls = 0

    def execute(self, sql: str):
        self.sqls.append(sql)
        if sql.startswith("SELECT count() FROM c3_fundamental.news_data"):
            return [(self._count,)]
        if sql.startswith("SELECT count() FROM system.mutations"):
            self._mut_calls += 1
            return [(0 if self._mut_calls > 1 else 1,)]
        return []


class TestRulesContract:
    def test_four_categories_present(self):
        cats = [c for c, _ in tnc.RULES]
        assert cats == ["research_report", "announcement", "macro_data", "news"]

    def test_specials_exclude_themselves_and_news_only_general(self):
        for cat, where in tnc.RULES[:3]:
            assert f"category != '{cat}'" in where
        assert "category = 'general'" in tnc.RULES[3][1]

    def test_all_rules_scoped_region_language(self):
        for _, where in tnc.RULES:
            assert "region = 'CN'" in where and "language = 'zh'" in where


class TestApplyRule:
    def test_alter_form_and_poll(self, monkeypatch):
        monkeypatch.setattr(tnc, "_MUTATION_POLL_S", 0)
        fc = _FakeClient()
        tnc.apply_rule(fc, "research_report", "source = 'x' AND category != 'research_report'")
        alters = [s for s in fc.sqls if s.startswith("ALTER TABLE")]
        assert len(alters) == 1
        assert "UPDATE category = 'research_report'" in alters[0]
        assert "WHERE source = 'x'" in alters[0]
        assert any("system.mutations" in s for s in fc.sqls)


class TestCountRule:
    def test_count_form(self):
        fc = _FakeClient(count_result=12345)
        assert tnc.count_rule(fc, "category = 'general'") == 12345
        assert "WHERE category = 'general'" in fc.sqls[0]
