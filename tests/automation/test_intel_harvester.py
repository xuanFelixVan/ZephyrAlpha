# [BLUEPRINT] MOD-AUTO-L3-001(暂编号) | docs/_working/automation/campaign/blueprints/intel_harvester_blueprint.md | §测试
# [MODULE] tests.automation.test_intel_harvester
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] 零网络零 LLM——过滤/渲染纯函数直喷+arXiv XML fixture；tmp 隔离（宪法 §9.6）
# [TTL] permanent
"""intel_harvester 测试：arXiv 解析/关键词过滤/收件箱渲染。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "automation") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "automation"))

import intel_harvester as ih  # noqa: E402

_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2609.0001v1</id>
    <title>A factor model for
      crypto momentum</title>
    <published>2026-09-16T00:00:00Z</published>
    <summary>We study momentum factors with regime switching and overfitting controls.</summary>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2609.0002v1</id>
    <title>On the chemistry of polymers</title>
    <published>2026-09-15T00:00:00Z</published>
    <summary>Pure polymer chemistry with no finance content whatsoever.</summary>
  </entry>
</feed>
"""


def test_filter_hits_finance_and_skips_polymer():
    import xml.etree.ElementTree as ET
    root = ET.fromstring(_ARXIV_XML)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for entry in root.findall("a:entry", ns):
        items.append({
            "title": " ".join((entry.findtext("a:title", "", ns) or "").split()),
            "link": (entry.findtext("a:id", "", ns) or "").strip(),
            "date": (entry.findtext("a:published", "", ns) or "")[:10],
            "summary": (entry.findtext("a:summary", "", ns) or "").strip(),
        })
    hits = ih.filter_items(items)
    assert len(hits) == 1
    assert "momentum" in hits[0]["title"].lower()
    assert hits[0]["hit"] in ("momentum", "factor", "regime", "overfitting", "crypto")


def test_render_inbox_has_redline_and_frontmatter():
    items = [{"title": "T", "link": "http://x", "date": "2026-09-16",
              "summary": "s", "hit": "factor", "llm_summary": "概要"}]
    md = ih.render_inbox(items)
    assert md.startswith("---") and "ttl: task_bound" in md
    assert "只搜不自动入册" in md
    assert "http://x" in md and "概要" in md


def test_summarize_degrades_without_ollama(monkeypatch):
    items = [{"title": "T", "link": "u", "date": "d", "summary": "s", "hit": "f"}]
    real_import = __import__

    def broken_import(name, *a, **k):
        if name == "zephyr.integration.local_model.ollama_chat":
            raise ImportError("no ollama")
        return real_import(name, *a, **k)

    monkeypatch.setattr("builtins.__import__", broken_import)
    out = ih.summarize_with_ollama(items, None)
    assert out[0]["llm_summary"] == ""
