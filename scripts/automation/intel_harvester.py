# [BLUEPRINT] MOD-AUTO-L3-001(暂编号) | docs/_working/automation/campaign/blueprints/intel_harvester_blueprint.md | §
# [MODULE] scripts.automation.intel_harvester
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.integration.local_model.ollama_chat（内嵌 LSG）; urllib; xml.etree
# [CONSUMERS] docs/_working/automation/inbox/（情报收件箱）; AI 层对话⑥（未来接管方）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只搜不自动入册——产出=收件箱 markdown，注册/上架永远走人工确认或门控（Owner 令）;
#   LLM 摘要必经 OllamaChat（内嵌 LSG，宪法 §9.2）;
#   礼貌抓取：arXiv API 官方端点+UA 声明，单次≤20 条，日 1 班;
#   网络失败降级：单源失败跳过不阻断其他源，全败=非零退出
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

源（v0）：arXiv q-fin 分类（官方 API，免 key）。
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc, now_utc_str  # noqa: E402

INBOX_DIR = REPO_ROOT / "docs" / "_working" / "automation" / "inbox"

# noqa: m11-perm-manual-legitimate  M11豁免: AI/操作员按需调用的情报采集工具（v0 手动班，日班化可挂 Windows 任务），非进程内常驻服务
SOURCES = [
    ("arxiv-qfin-rm", "http://rss.arxiv.org/rss/q-fin.RM"),   # 风险管理
    ("arxiv-qfin-pm", "http://rss.arxiv.org/rss/q-fin.PM"),   # 组合管理
    ("arxiv-qfin-tr", "http://rss.arxiv.org/rss/q-fin.TR"),   # 交易
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ZephyrAlpha-intel/1.0; research use)"}
# 关键词（命中=高亮标记；feed 已限定 q-fin，词表做标记不做硬剔除——未命中条目进兜底段）
KEYWORDS = re.compile(
    r"factor|alpha|momentum|regime|risk parit|drawdown|backtest|overfitting|"
    r"reinforcement|LLM|agent|microstructure|liquidity|volatil|hedg|portfolio|"
    r"markowitz|extreme value|option|derivative|trading|market mak|skew|tail|"
    r"sentiment|crypto|seasonality|forecast", re.IGNORECASE)

_SUMMARY_MAX = 600


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
    """多源采集；单源失败跳过（warn），全败才抛。"""
    items: list[dict] = []
    failures = 0
    for name, url in SOURCES:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 白名单域
                items.extend(_parse_feed(resp.read().decode("utf-8", errors="replace"), name))
        except Exception as exc:  # noqa: BLE001 — 单源失败降级
            failures += 1
            print(f"WARN: 源 {name} 失败跳过: {exc}")
    if failures == len(SOURCES):
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
