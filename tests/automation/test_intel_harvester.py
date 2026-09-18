# [BLUEPRINT] MOD-AUTO-L3-001(暂编号) | docs/_working/automation/campaign/blueprints/intel_harvester_blueprint.md | §测试
# [MODULE] tests.automation.test_intel_harvester
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] 零网络零 LLM——过滤/渲染纯函数直喷+arXiv XML fixture；tmp 隔离（宪法 §9.6）;
#   网络路径一律 monkeypatch urlopen（注册表加载/校验/采集降级矩阵，WO-①-01/03 随批）
# [TTL] permanent
"""intel_harvester 测试：arXiv 解析/关键词过滤/收件箱渲染/注册表加载/校验器/行为等价回归。"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "automation") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "automation"))

import intel_harvester as ih  # noqa: E402
import validate_intel_registry as vir  # noqa: E402

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


# ---------- WO-①-01/03：注册表化随批（加载/降级/校验器/行为等价回归；零网零 LLM） ----------

_LEGACY_PATTERN = (
    r"factor|alpha|momentum|regime|risk parit|drawdown|backtest|overfitting|"
    r"reinforcement|LLM|agent|microstructure|liquidity|volatil|hedg|portfolio|"
    r"markowitz|extreme value|option|derivative|trading|market mak|skew|tail|"
    r"sentiment|crypto|seasonality|forecast"
)


def test_default_registries_behavior_equivalent():
    """行为等价回归锚：默认注册表跑出来与改造前硬编码一致（同 3 源同词表）。"""
    assert ih.KEYWORDS.pattern == _LEGACY_PATTERN
    assert ih.KEYWORDS.flags & re.IGNORECASE
    active = [s["source_id"] for s in ih.SOURCES if s["enabled"]]
    assert active == ["arxiv-qfin-rm", "arxiv-qfin-pm", "arxiv-qfin-tr"]
    assert all(s["kind"] == "rss" for s in ih.SOURCES if s["enabled"])
    assert all(s["politeness"].startswith("Mozilla/5.0") for s in ih.SOURCES if s["enabled"])


def test_load_sources_good_bad_entries(tmp_path, capsys):
    p = tmp_path / "intel_sources.yaml"
    p.write_text(
        "source_count: 2\n"
        "sources:\n"
        "  - source_id: good\n"
        "    kind: rss\n"
        "    url: http://rss.arxiv.org/rss/q-fin.RM\n"
        "    enabled: true\n"
        "    politeness: UA/1.0\n"
        "    category: 测试\n"
        "  - source_id: bad-kind\n"
        "    kind: twitter\n"
        "    url: http://x.example/rss\n"
        "    enabled: true\n"
        "  - source_id: bad-url\n"
        "    kind: rss\n"
        "    url: ftp://nope\n"
        "    enabled: true\n"
        "  - source_id: rsshub-reserved\n"
        "    kind: rsshub\n"
        "    route: /wallstreetcn/live/global\n"
        "    enabled: false\n",
        encoding="utf-8")
    out = ih.load_sources(p)
    assert [s["source_id"] for s in out] == ["good", "rsshub-reserved"]
    assert out[0]["politeness"] == "UA/1.0"
    assert out[1]["route"] == "/wallstreetcn/live/global"
    captured = capsys.readouterr()
    assert "bad-kind" in captured.out and "bad-url" in captured.out


def test_load_sources_missing_and_corrupt_fall_back(tmp_path, capsys):
    fallback_ids = [s["source_id"] for s in ih.load_sources(tmp_path / "nope.yaml")]
    assert fallback_ids == ["arxiv-qfin-rm", "arxiv-qfin-pm", "arxiv-qfin-tr"]
    corrupt = tmp_path / "corrupt.yaml"
    corrupt.write_text("sources: [ {unclosed", encoding="utf-8")
    assert [s["source_id"] for s in ih.load_sources(corrupt)] == fallback_ids
    assert "WARN" in capsys.readouterr().out


def test_load_keyword_stems_bad_skipped_and_missing_falls_back(tmp_path, capsys):
    p = tmp_path / "intel_keywords.yaml"
    p.write_text("stem_count: 3\nflags: IGNORECASE\nstems:\n  - factor\n  - '('\n  - 42\n",
                 encoding="utf-8")
    stems = ih.load_keyword_stems(p)
    assert stems == ["factor"]
    fallback = ih.load_keyword_stems(tmp_path / "nope.yaml")
    assert ih.KEYWORDS.pattern == "|".join(fallback)
    captured = capsys.readouterr()
    assert "不可编译" in captured.out and "WARN" in captured.out


def test_fetch_all_sources_degradation_matrix(monkeypatch):
    """采集降级矩阵：disabled/rsshub 跳过+单源失败容忍+全败抛 RuntimeError。"""
    fake = [
        {"source_id": "ok", "kind": "rss", "url": "http://ok.example/rss",
         "enabled": True, "politeness": "UA/1.0"},
        {"source_id": "dead", "kind": "rss", "url": "http://dead.example/rss",
         "enabled": True, "politeness": "UA/1.0"},
        {"source_id": "off", "kind": "rss", "url": "http://off.example/rss",
         "enabled": False, "politeness": "UA/1.0"},
        {"source_id": "rsshub-x", "kind": "rsshub", "url": "", "route": "/a/b",
         "enabled": True, "politeness": "UA/1.0"},
    ]
    rss_xml = ("<rss><channel><item><title>factor test</title>"
               "<link>http://x.example/1</link></item></channel></rss>")
    seen_urls: list[str] = []

    def fake_urlopen(req, timeout=30):
        if "dead" in req.full_url:
            raise OSError("boom")
        seen_urls.append(req.full_url)
        assert req.headers.get("User-agent") == "UA/1.0"
        return io.BytesIO(rss_xml.encode("utf-8"))

    monkeypatch.setattr(ih, "SOURCES", fake)
    monkeypatch.setattr(ih.urllib.request, "urlopen", fake_urlopen)
    items = ih.fetch_all_sources()
    assert seen_urls == ["http://ok.example/rss"]
    assert [it["source"] for it in items] == ["ok"]

    monkeypatch.setattr(
        ih, "SOURCES", [{"source_id": "dead", "kind": "rss",
                         "url": "http://dead.example/rss", "enabled": True}])
    try:
        ih.fetch_all_sources()
        raise AssertionError("expect RuntimeError")
    except RuntimeError as exc:
        assert "全部源拉取失败" in str(exc)


def test_validate_intel_registry_ok(tmp_path, capsys):
    (tmp_path / "intel_sources.yaml").write_text(
        "source_count: 1\n"
        "sources:\n"
        "  - source_id: a\n"
        "    kind: rss\n"
        "    url: https://rss.arxiv.org/rss/q-fin.RM\n"
        "    enabled: true\n"
        "    politeness: UA/1.0\n",
        encoding="utf-8")
    (tmp_path / "intel_keywords.yaml").write_text(
        "stem_count: 2\nflags: IGNORECASE\nstems:\n  - factor\n  - alpha\n",
        encoding="utf-8")
    assert vir.main(["--registry-dir", str(tmp_path)]) == 0
    assert "OK" in capsys.readouterr().out


def test_validate_intel_registry_fails_on_schema_url_count(tmp_path, capsys):
    (tmp_path / "intel_sources.yaml").write_text(
        "source_count: 3\n"
        "sources:\n"
        "  - source_id: dup\n"
        "    kind: rss\n"
        "    url: notaurl\n"
        "    enabled: true\n"
        "  - source_id: dup\n"
        "    kind: rsshub\n"
        "    enabled: false\n",
        encoding="utf-8")
    (tmp_path / "intel_keywords.yaml").write_text(
        "stem_count: 9\nflags: CASEINSENSITIVE\nstems:\n  - factor\n  - '('\n",
        encoding="utf-8")
    assert vir.main(["--registry-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "计数漂移" in out and "url 格式非法" in out and "source_id 重复" in out
    assert "route" in out and "不可编译" in out and "flags" in out


def test_validate_intel_registry_missing_files(tmp_path, capsys):
    assert vir.main(["--registry-dir", str(tmp_path)]) == 1
    assert "缺失" in capsys.readouterr().out


# ---------- 红队批（REDA-20260918）：ReDoS/注册表投毒 fail-closed ----------

def test_load_keyword_stems_rejects_redos(tmp_path, capsys):
    """嵌套量词词干可编译但会灾难性回溯（feed 文本攻击者可控）——装载侧 warn 跳过。"""
    p = tmp_path / "intel_keywords.yaml"
    p.write_text("stem_count: 3\nflags: IGNORECASE\nstems:\n  - factor\n  - '(a+)+$'\n"
                 "  - '(?:\\d{1,})*$'\n", encoding="utf-8")
    stems = ih.load_keyword_stems(p)
    assert stems == ["factor"]
    out = capsys.readouterr().out
    assert "ReDoS" in out and "WARN" in out


def test_validate_intel_registry_rejects_redos_stem(tmp_path, capsys):
    """登记态 fail-closed：嵌套量词词干 -> 校验 FAIL（可编译≠安全）。"""
    (tmp_path / "intel_sources.yaml").write_text(
        "source_count: 1\n"
        "sources:\n"
        "  - source_id: a\n"
        "    kind: rss\n"
        "    url: https://rss.arxiv.org/rss/q-fin.RM\n"
        "    enabled: true\n",
        encoding="utf-8")
    (tmp_path / "intel_keywords.yaml").write_text(
        "stem_count: 2\nflags: IGNORECASE\nstems:\n  - factor\n  - '(a|b+)*$'\n",
        encoding="utf-8")
    assert vir.main(["--registry-dir", str(tmp_path)]) == 1
    assert "ReDoS" in capsys.readouterr().out


def test_validate_intel_registry_rejects_userinfo_and_unicode_host(tmp_path, capsys):
    """URL 带 user:pass@（密钥入册违规）/unicode 域名（urllib 直接炸）——登记态拒绝。"""
    (tmp_path / "intel_sources.yaml").write_text(
        "source_count: 2\n"
        "sources:\n"
        "  - source_id: cred\n"
        "    kind: rss\n"
        "    url: http://user:pass@rss.arxiv.org/rss/q-fin.RM\n"
        "    enabled: true\n"
        "  - source_id: idn\n"
        "    kind: rss\n"
        "    url: http://经济例子.测试/rss\n"
        "    enabled: true\n",
        encoding="utf-8")
    (tmp_path / "intel_keywords.yaml").write_text(
        "stem_count: 1\nflags: IGNORECASE\nstems:\n  - factor\n", encoding="utf-8")
    assert vir.main(["--registry-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "userinfo" in out and "ASCII" in out


def test_validate_intel_registry_bool_count_trap(tmp_path, capsys):
    """source_count: true 在单源清单上 isinstance(True,int) 蒙混——须判漂移。"""
    (tmp_path / "intel_sources.yaml").write_text(
        "source_count: true\n"
        "sources:\n"
        "  - source_id: a\n"
        "    kind: rss\n"
        "    url: https://rss.arxiv.org/rss/q-fin.RM\n"
        "    enabled: true\n",
        encoding="utf-8")
    (tmp_path / "intel_keywords.yaml").write_text(
        "stem_count: 1\nflags: IGNORECASE\nstems:\n  - factor\n", encoding="utf-8")
    assert vir.main(["--registry-dir", str(tmp_path)]) == 1
    assert "source_count" in capsys.readouterr().out


def test_load_sources_non_bool_enabled_skipped(tmp_path, capsys):
    """enabled: \"false\"（字符串）旧版 bool()==True 照抓（禁用源变启用）——新版 warn 跳过。"""
    p = tmp_path / "intel_sources.yaml"
    p.write_text(
        "sources:\n"
        "  - source_id: sneaky\n"
        "    kind: rss\n"
        "    url: http://x.example/rss\n"
        "    enabled: \"false\"\n"
        "  - source_id: good\n"
        "    kind: rss\n"
        "    url: http://y.example/rss\n"
        "    enabled: true\n",
        encoding="utf-8")
    out = ih.load_sources(p)
    assert [s["source_id"] for s in out] == ["good"]
    assert "enabled" in capsys.readouterr().out


def test_load_sources_duplicate_id_skipped(tmp_path, capsys):
    """source_id 重复：旧版静默双抓（违反礼貌抓取），新版 warn 跳过后者。"""
    p = tmp_path / "intel_sources.yaml"
    entry = ("  - source_id: dup\n    kind: rss\n    url: http://x.example/rss\n    enabled: true\n")
    p.write_text("sources:\n" + entry + entry, encoding="utf-8")
    out = ih.load_sources(p)
    assert [s["source_id"] for s in out] == ["dup"]
    assert "重复" in capsys.readouterr().out


def test_fetch_all_sources_zero_enabled_distinct_error(monkeypatch):
    """0 源 enabled（全禁）：报"无启用源"而非"全部源拉取失败"（排障语义分离）。"""
    monkeypatch.setattr(ih, "SOURCES", [
        {"source_id": "off", "kind": "rss", "url": "http://off.example/rss",
         "enabled": False, "politeness": "UA/1.0"}])
    try:
        ih.fetch_all_sources()
        raise AssertionError("expect RuntimeError")
    except RuntimeError as exc:
        assert "无启用源" in str(exc)
