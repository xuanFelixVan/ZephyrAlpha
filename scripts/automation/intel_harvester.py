# [BLUEPRINT] MOD-AUTO-L3-001(暂编号) | docs/_working/automation/campaign/blueprints/intel_harvester_blueprint.md | §
# [MODULE] scripts.automation.intel_harvester
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.integration.local_model.ollama_chat（内嵌 LSG）; urllib; xml.etree; yaml（PyYAML）
# [CONSUMERS] docs/_working/automation/inbox/（情报收件箱）; AI 层对话⑥（未来接管方）;
#   config/intel_sources.yaml + config/intel_keywords.yaml（本件消费的两注册表）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只搜不自动入册——产出=收件箱 markdown，注册/上架永远走人工确认或门控（Owner 令）;
#   LLM 摘要必经 OllamaChat（内嵌 LSG，宪法 §9.2）;
#   礼貌抓取：arXiv API 官方端点+UA 声明，单次≤20 条，日 1 班;
#   网络失败降级：单源失败跳过不阻断其他源，全败=非零退出;
#   源/词表=注册表产出（config/intel_sources.yaml + config/intel_keywords.yaml，
#   validate_intel_registry.py 班前校验）；注册表缺失/损坏→降级内置默认并 warn（班不炸）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 源全败→RuntimeError; Ollama 不可达→摘要降级为原文标题列表（不阻断收件箱产出）
# [TESTS] tests/automation/test_intel_harvester.py
# [A_module] module_id=MOD-AUTO-L3-001 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
"""intel_harvester — 搜索设备 v0（AI 层"胃"的地基件，业务层代建）。

全网情报采集→关键词过滤→本地 LLM 摘要→收件箱。定位=对话⑥三层定案的"胃"的地基：
业务层点菜（⑥号车道用它找策略线索、治理层用它搜门禁章法），设备迭代归 AI 层。

源（v0）：config/intel_sources.yaml 注册表（现役=arXiv q-fin 三源官方 RSS 免 key；
RSSHub 等扩展 kind 允许注册，enabled=false 跳过）。词表：config/intel_keywords.yaml。
用法（仓库根，Python 3.12）：
    python scripts/automation/intel_harvester.py                 # 采集+摘要+收件箱
    python scripts/automation/intel_harvester.py --no-llm        # 跳过摘要（快扫模式）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc, now_utc_str  # noqa: E402

INBOX_DIR = REPO_ROOT / "docs" / "_working" / "automation" / "inbox"

# noqa: m11-perm-manual-legitimate  M11豁免: AI/操作员按需调用的情报采集工具（v0 手动班，日班化可挂 Windows 任务），非进程内常驻服务

SOURCES_REGISTRY = REPO_ROOT / "config" / "intel_sources.yaml"
KEYWORDS_REGISTRY = REPO_ROOT / "config" / "intel_keywords.yaml"
DEFAULT_UA = "Mozilla/5.0 (compatible; ZephyrAlpha-intel/1.0; research use)"
SUPPORTED_KINDS = ("rss", "rsshub")

# 内置降级默认（注册表缺失/损坏→warn 降级，班不炸）——必须与两 YAML 现役内容一致
FALLBACK_SOURCES = [
    {"source_id": "arxiv-qfin-rm", "kind": "rss", "url": "http://rss.arxiv.org/rss/q-fin.RM",
     "enabled": True, "politeness": DEFAULT_UA, "category": "风险管理"},
    {"source_id": "arxiv-qfin-pm", "kind": "rss", "url": "http://rss.arxiv.org/rss/q-fin.PM",
     "enabled": True, "politeness": DEFAULT_UA, "category": "组合管理"},
    {"source_id": "arxiv-qfin-tr", "kind": "rss", "url": "http://rss.arxiv.org/rss/q-fin.TR",
     "enabled": True, "politeness": DEFAULT_UA, "category": "交易"},
]
# 关键词（命中=高亮标记；feed 已限定 q-fin，词表做标记不做硬剔除——未命中条目进兜底段）
FALLBACK_KEYWORD_STEMS = [
    "factor", "alpha", "momentum", "regime", "risk parit", "drawdown", "backtest",
    "overfitting", "reinforcement", "LLM", "agent", "microstructure", "liquidity",
    "volatil", "hedg", "portfolio", "markowitz", "extreme value", "option", "derivative",
    "trading", "market mak", "skew", "tail", "sentiment", "crypto", "seasonality", "forecast",
]

_SUMMARY_MAX = 600

# ReDoS 防线（与 validate_intel_registry._RE_DOS_NESTED_QUANT 保持同式）：
# 嵌套量词（组内含量词+组外再量词）在恶意 feed 标题上指数回溯——词干禁入。
# 注：仅启发式，拦 (a+)+ / (a|b+)* / (?:\d{1,})*$ 等典型灾难形态；多项式慢正则不在拦截面。
_RE_DOS_NESTED_QUANT = re.compile(r"\([^()]*[+*{][^()]*\)\s*[+*{]")


def _stem_looks_redos(stem: str) -> bool:
    """词干疑似灾难性回溯（嵌套量词）判定。"""
    return bool(_RE_DOS_NESTED_QUANT.search(stem))


def _normalize_source(e: dict, i: int, seen_ids: set[str]) -> dict | None:
    """单条目规范化为采集形态；非法/重复/非 bool enabled 一律 warn 跳过（返回 None）。

    bool(\"false\")==True 陷阱：字符串 \"false\" 会让禁用源照抓——enabled 必须显式 bool。
    """
    sid, kind = e.get("source_id"), e.get("kind")
    if not sid or not isinstance(sid, str):
        print(f"WARN: 源注册表第 {i} 条缺 source_id，跳过")
        return None
    if sid in seen_ids:
        print(f"WARN: 源注册表 source_id 重复（{sid}），跳过（重复=同源双抓，违反礼貌抓取）")
        return None
    seen_ids.add(sid)
    if kind not in SUPPORTED_KINDS:
        print(f"WARN: 源 {sid} kind 非法（{kind!r}，仅 {'/'.join(SUPPORTED_KINDS)}），跳过")
        return None
    url = e.get("url")
    if kind == "rss" and (not isinstance(url, str) or not url.startswith(("http://", "https://"))):
        print(f"WARN: 源 {sid} 缺合法 http(s) url，跳过")
        return None
    enabled = e.get("enabled", True)
    if not isinstance(enabled, bool):
        print(f"WARN: 源 {sid} enabled 须 bool（现 {enabled!r}），跳过")
        return None
    return {
        "source_id": sid,
        "kind": kind,
        "url": url if isinstance(url, str) else "",
        "route": e.get("route") if isinstance(e.get("route"), str) else "",
        "enabled": enabled,
        "politeness": e.get("politeness") if isinstance(e.get("politeness"), str) and e.get("politeness") else DEFAULT_UA,
        "category": e.get("category") if isinstance(e.get("category"), str) else "",
    }


def load_sources(path: str | Path | None = None) -> list[dict]:
    """读源注册表 → 规范化条目列表；坏条目 warn 跳过；缺失/损坏 → 降级内置默认（班不炸）。

    条目 schema：source_id*/kind*(rss|rsshub)/url(rss 必填 http s)/route(rsshub 必填)/
    enabled(缺省 true)/politeness(缺省 DEFAULT_UA)/category(可选)。
    rsshub 为预留扩展位：允许注册，抓取适配未实现——采集侧对非 rss kind 跳过。
    """
    p = Path(path) if path else SOURCES_REGISTRY
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"WARN: 源注册表缺失（{p}），降级内置默认 {len(FALLBACK_SOURCES)} 源")
        return [dict(s) for s in FALLBACK_SOURCES]
    except Exception as exc:  # noqa: BLE001 — YAML 损坏降级
        print(f"WARN: 源注册表损坏（{exc}），降级内置默认 {len(FALLBACK_SOURCES)} 源")
        return [dict(s) for s in FALLBACK_SOURCES]
    entries = raw.get("sources") if isinstance(raw, dict) else None
    if not isinstance(entries, list) or not entries:
        print("WARN: 源注册表无有效 sources 列表，降级内置默认")
        return [dict(s) for s in FALLBACK_SOURCES]
    out: list[dict] = []
    seen_ids: set[str] = set()
    for i, e in enumerate(entries, 1):
        if not isinstance(e, dict):
            print(f"WARN: 源注册表第 {i} 条非映射，跳过")
            continue
        normalized = _normalize_source(e, i, seen_ids)
        if normalized is not None:
            out.append(normalized)
    if not out:
        print("WARN: 源注册表全部条目非法，降级内置默认")
        return [dict(s) for s in FALLBACK_SOURCES]
    return out


def load_keyword_stems(path: str | Path | None = None) -> list[str]:
    """读词表注册表 → 词干列表；坏词干 warn 跳过；缺失/损坏/全坏 → 降级内置默认（班不炸）。"""
    p = Path(path) if path else KEYWORDS_REGISTRY
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"WARN: 词表缺失（{p}），降级内置默认 {len(FALLBACK_KEYWORD_STEMS)} 词干")
        return list(FALLBACK_KEYWORD_STEMS)
    except Exception as exc:  # noqa: BLE001 — YAML 损坏降级
        print(f"WARN: 词表损坏（{exc}），降级内置默认 {len(FALLBACK_KEYWORD_STEMS)} 词干")
        return list(FALLBACK_KEYWORD_STEMS)
    stems_raw = raw.get("stems") if isinstance(raw, dict) else None
    if not isinstance(stems_raw, list) or not stems_raw:
        print("WARN: 词表无有效 stems 列表，降级内置默认")
        return list(FALLBACK_KEYWORD_STEMS)
    out: list[str] = []
    for i, s in enumerate(stems_raw, 1):
        if not isinstance(s, str) or not s.strip():
            print(f"WARN: 词表第 {i} 条非非空字符串，跳过")
            continue
        try:
            re.compile(s)
        except re.error as exc:
            print(f"WARN: 词表第 {i} 条不可编译（{s!r}: {exc}），跳过")
            continue
        if _stem_looks_redos(s):
            # 可编译≠安全：嵌套量词在 feed 攻击文本上指数回溯，词干禁入（fail-closed）
            print(f"WARN: 词表第 {i} 条疑似灾难性回溯（嵌套量词，ReDoS），跳过: {s!r}")
            continue
        out.append(s)
    if not out:
        print("WARN: 词表全部词干非法，降级内置默认")
        return list(FALLBACK_KEYWORD_STEMS)
    return out


def compile_keywords(stems: list[str]) -> re.Pattern:
    """词干列表 → 命中正则（IGNORECASE，与外置前硬编码行为等价）。"""
    return re.compile("|".join(stems), re.IGNORECASE)


# 注册表加载（模块导入即消费两 YAML；缺失/损坏已降级 warn）
SOURCES: list[dict] = load_sources()
KEYWORDS: re.Pattern = compile_keywords(load_keyword_stems())


def _localfind(entry, name: str) -> str:
    """按 local-name 查找直接子节点文本（命名空间无关，Atom/RSS 通吃）。"""
    for child in entry.iter():
        if child is entry:
            continue
        if child.tag.rsplit("}", 1)[-1] == name:
            return re.sub(r"\s+", " ", child.text or "").strip()
    return ""


def _parse_feed(xml_text: str, source: str) -> list[dict]:
    """通用 RSS2.0(item)/Atom(entry) 解析 → 条目列表（命名空间无关）。"""
    root = ET.fromstring(xml_text)
    items: list[dict] = []
    for entry in root.iter():
        tag = entry.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        get = lambda t: _localfind(entry, t)  # noqa: E731
        title = get("title")
        link = get("link") or get("id")
        published = get("published")
        date = get("pubDate") or (published[:10] if published else "")
        summary = get("description") or get("summary")
        if title:
            items.append({"source": source, "title": title, "link": link,
                          "date": (date or "")[:24], "summary": summary[:800]})
    return items


def fetch_all_sources() -> list[dict]:
    """多源采集（消费源注册表）；单源失败跳过（warn），全败才抛。

    enabled=false 源登记保留不采集；非 rss kind（rsshub 等扩展位）抓取适配未实现→跳过。
    """
    items: list[dict] = []
    failures = 0
    attempts = 0
    for src in SOURCES:
        if not src.get("enabled", True):
            continue
        if src.get("kind") != "rss":
            print(f"WARN: 源 {src['source_id']} kind={src['kind']} 抓取适配未实现，跳过（扩展位）")
            continue
        name, url = src["source_id"], src["url"]
        attempts += 1
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": src.get("politeness") or DEFAULT_UA})
            with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 白名单域
                items.extend(_parse_feed(resp.read().decode("utf-8", errors="replace"), name))
        except Exception as exc:  # noqa: BLE001 — 单源失败降级
            failures += 1
            print(f"WARN: 源 {name} 失败跳过: {exc}")
    if attempts == 0:
        # 全禁用≠网络故障：语义分开，避免误导排障方向（全败↓才指向源/网络）
        raise RuntimeError("无启用源（注册表全禁用或全为未实现 kind），无可采集对象")
    if failures == attempts:
        raise RuntimeError("全部源拉取失败")
    return items


def filter_items(items: list[dict]) -> list[dict]:
    """关键词过滤（标题+摘要命中任一即收）。"""
    out = []
    for it in items:
        blob = f"{it['title']} {it['summary']}"
        if KEYWORDS.search(blob):
            it["hit"] = KEYWORDS.search(blob).group(0).lower()
            out.append(it)
    return out


def summarize_with_ollama(items: list[dict], model: str | None) -> list[dict]:
    """本地 LLM 摘要（OllamaChat 内嵌 LSG）；不可达→返回原文标记降级。"""
    if not items:
        return items
    try:
        from zephyr.integration.local_model.ollama_chat import OllamaChat

        model = model or "qwen3:8b"
        chat = OllamaChat(model=model, timeout_s=120.0)
    except Exception as exc:  # noqa: BLE001 — 降级不阻断
        print(f"WARN: Ollama 不可达，摘要降级（{exc}）")
        for it in items:
            it["llm_summary"] = ""
        return items
    for it in items:
        prompt = (
            "用不超过 120 字中文概括这篇量化研究对一家做 A 股量化的自动化工厂的"
            "可借鉴点（若无直接借鉴，说一句它属于哪个方向）：\n\n"
            f"标题：{it['title']}\n摘要：{it['summary'][:_SUMMARY_MAX]}"
        )
        try:
            it["llm_summary"] = str(chat.ask(prompt)).strip()[:400]
        except Exception as exc:  # noqa: BLE001 — 单条摘要失败降级
            it["llm_summary"] = f"（摘要失败：{exc}）"
    return items


def render_inbox(items: list[dict]) -> str:
    now = now_utc_str()
    lines = [
        "---", "ttl: task_bound",
        "completes_when: 情报被人工消费（入册/上架/归档）后可清理",
        "---", "",
        f"# 情报收件箱 {now}",
        "",
        f"> 只搜不自动入册（Owner 红线）。命中 {len(items)} 条（arXiv q-fin 近期+关键词）。",
        "",
    ]
    for i, it in enumerate(items, 1):
        lines += [f"## {i}. {it['title']}", "",
                  f"- 链接: {it['link']}  |  日期: {it['date']}  |  命中词: `{it.get('hit','')}`"]
        if it.get("llm_summary"):
            lines.append(f"- 摘要: {it['llm_summary']}")
        lines.append("")
    return "\n".join(lines)


def render_unmatched(unmatched: list[dict]) -> str:
    """未命中关键词的 q-fin 条目兜底段（feed 已限域，只标记不丢弃）。"""
    if not unmatched:
        return ""
    lines = ["## 兜底：未命中关键词的 q-fin 条目", ""]
    for it in unmatched:
        lines.append(f"- [{it['title']}]({it['link']}) ({it.get('source','')})")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="搜索设备 v0：arXiv 情报采集+Ollama 摘要+收件箱")
    ap.add_argument("--no-llm", action="store_true", help="跳过 LLM 摘要（快扫）")
    ap.add_argument("--model", type=str, default=None, help="Ollama 模型（默认 qwen3:8b）")
    args = ap.parse_args()

    try:
        all_items = fetch_all_sources()
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: 全部源拉取失败: {exc}")
        return 2
    hits = filter_items(all_items)
    hit_ids = {id(x) for x in hits}
    unmatched = [x for x in all_items if id(x) not in hit_ids]
    if not args.no_llm and hits:
        hits = summarize_with_ollama(hits, args.model)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now_utc().strftime("%Y%m%d-%H%M%S")
    out = INBOX_DIR / f"intel-{stamp}.md"
    text = render_inbox(hits) + render_unmatched(unmatched)
    out.write_text(text, encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "hits": len(hits),
                      "unmatched": len(unmatched)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
