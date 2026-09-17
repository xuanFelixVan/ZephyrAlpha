# [BLUEPRINT] MOD-AUTO-E1G-001 | docs/_working/automation/campaign/blueprints/lane_g_stomach_intake_blueprint.md | §
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] scripts.backtest.lane_g_stomach_intake
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; scripts.backtest.lane_b_idea_generator (parse_ideas 复用); zephyr.integration.local_model.ollama_chat
# [CONSUMERS] 策略生产全景图 FAC-E1G 车道G-全网搜索进货；scripts/backtest/factory_intake_pipeline.py（E1 编排）；
#   data/strategy_intake/lane_g_candidates.csv（进货台账）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 出生证（birth_channel/birth_batch/birth_source）由本模块代码机器写入，AI 禁手填；
#   运动员不兼任裁判——本车道只进货不打分，判定权在 E2 预审/E4 考试；
#   候选 id=CAND-md5_12('E1G:'+假说全文) 内容寻址跨批稳定去重；台账只追加；
#   LLM 调用必经 OllamaChat（内置 LSG fail-closed 闸门）；
#   收件箱条目按 url 记账（seen log），一条目多班不重复消化；LLM 失败条目不入 seen（下一班重试）；
#   只消化 intel_harvester 已产出收件箱（本件不联网、不抓取——抓取是真源 L3 的职责）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单条目 LLM 失败/解析空 → 记 failed 清单继续（不抛）；台账读写损坏 → 按空集处理宁可重写不误删
# [TESTS] tests/backtest/test_lane_g_stomach_intake.py
# [A_module] module_id=MOD-AUTO-E1G-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 进货件非常驻服务：由 E1 进货编排事件调用（接线前人工/会话触发），无常驻循环
"""FAC-E1G 车道G-全网搜索进货（⑥号车道，"从胃点菜"）——收件箱情报→策略假说卸台账（图9 FAC-E1G）。

原理（骨架 §1 工段⑥ + §4 P1"⑥号车道"工单）：AI 层胃（L3 intel_harvester，MOD-AUTO-L3-001）
只搜不入册；本车道是业务层的"点菜"动作——消化胃的收件箱摘要，经本地 LLM 抽取可检验的
A 股策略假说，带出生证（渠道 G+批次+原文链接）卸到策略进货台账，交 E2 预审把关。
警示同车道 B（QuantCode-Bench）：产出是"想法"非"代码"，构造在 E3、考试在 E4。

用法:
  python scripts/backtest/lane_g_stomach_intake.py run --limit 5 --dry-run
  python scripts/backtest/lane_g_stomach_intake.py run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # CLI 直跑（__main__）时 scripts.* 惰性导入需仓库根在径
_INBOX_DIR = _ROOT / "docs" / "_working" / "automation" / "inbox"
_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "lane_g_candidates.csv"
_SEEN_CSV = _ROOT / "data" / "strategy_intake" / "lane_g_seen_urls.csv"

MODEL = "qwen3:8b"
BIRTH_CHANNEL = "G"

EXTRACTION_SYSTEM = (
    "你是量化策略假说抽取器。输入是一篇研究的标题与摘要。"
    "只输出能落成 A 股日频信号、机制讲得通的可检验假说；"
    "该研究给不出这样的假说就输出空数组，严禁硬凑（冰淇淋销量式巧合宁可不产）。"
    "每个假说必须说清：赚的是谁的钱（机制）、什么信号、持有多久、用在什么股票域。"
    "始终输出合法 JSON，不要输出额外文本。"
)


def parse_inbox_entries(md_text: str) -> list[dict]:
    """收件箱 markdown → 条目 dict 列表（title/url/keywords/summary），纯函数零 IO。

    格式真源=intel_harvester.render_inbox：`## N. 标题` + `- 链接: <url>  |  日期: ...  |  命中词: ...`
    + `- 摘要: ...`。字段残缺（无链接）的块跳过。
    """
    entries: list[dict] = []
    for block in re.split(r"^## \d+\.\s+", md_text, flags=re.MULTILINE)[1:]:
        lines = block.splitlines()
        title = lines[0].strip() if lines else ""
        link_line = next((ln for ln in lines if ln.startswith("- 链接:")), "")
        summary_line = next((ln for ln in lines if ln.startswith("- 摘要:")), "")
        m = re.match(r"- 链接:\s*(\S+)", link_line)
        if not m:
            continue
        kw = re.findall(r"`([^`]+)`", link_line)
        entries.append({
            "title": title,
            "url": m.group(1),
            "keywords": kw,
            "summary": summary_line.removeprefix("- 摘要:").strip(),
        })
    return entries


def build_extraction_prompt(entry: dict) -> str:
    """确定性消化 prompt（同条目必同 prompt——prompt_md5 进出生证可复核）。"""
    return (
        f"研究标题：{entry['title']}\n"
        f"命中词：{'、'.join(entry['keywords']) or '（无）'}\n"
        f"摘要：{entry['summary']}\n"
        "从中抽取 0-2 条可检验的 A 股日频策略假说。\n"
        "要求：信号必须是 T 日收盘可知的信息；不涉及做空（A 股个股限制）；"
        "机制必须源自该研究的思想，不得离题发散。\n"
        '输出 JSON 数组，每条：{"hypothesis_zh": "一句话假说", "mechanism_hint": "机制提示", '
        '"horizon": "持有期如5日/20日", "universe": "适用域如沪深300/全A"}；无可提取则输出 []。'
    )


def make_candidate_id(hypothesis_zh: str) -> str:
    """候选 id：CAND-<md5_12>，对假说全文内容寻址（E1G 域前缀，跨批同假说不换 id）。"""
    digest = hashlib.md5(f"E1G:{hypothesis_zh.strip()}".encode("utf-8")).hexdigest()[:12]
    return f"CAND-{digest}"


def load_seen_urls(path: Path) -> set[str]:
    """已消化 url 指纹集（seen log；不存在/损坏返回空集）。"""
    if not path.exists():
        return set()
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        return set(df["url_md5"].astype(str))
    except Exception:  # noqa: BLE001 — 同上，损坏按空集（重消化只多花算力，不丢货）
        return set()


def collect_inbox_entries(inbox_dir: Path) -> list[dict]:
    """全部收件箱文件 → 条目列表（按文件名排序保证确定性）。"""
    entries: list[dict] = []
    for f in sorted(inbox_dir.glob("intel-*.md")):
        text = f.read_text(encoding="utf-8")
        for e in parse_inbox_entries(text):
            e["birth_file"] = f.name
            entries.append(e)
    return entries


def _build_rows(entry: dict, ideas: list[dict], batch_id: str, prompt_fp: str,
                existing: set[str]) -> tuple[list[dict], int]:
    """假说 → 台账行（内容寻址跨批去重，existing 就地更新）。返回 (行, 去重跳过数)。"""
    rows: list[dict] = []
    skipped = 0
    for x in ideas:
        hyp = str(x.get("hypothesis_zh", "")).strip()
        if not hyp:
            continue
        cid = make_candidate_id(hyp)
        if cid in existing:
            skipped += 1
            continue
        existing.add(cid)
        rows.append({
            "candidate_id": cid,
            "theme": "、".join(entry["keywords"]) or "全网搜索",
            "hypothesis_zh": hyp,
            "mechanism_hint": str(x.get("mechanism_hint", "")),
            "horizon": str(x.get("horizon", "")),
            "universe": str(x.get("universe", "")),
            "birth_channel": BIRTH_CHANNEL,
            "birth_batch": batch_id,
            "birth_source": (
                f"llm:{MODEL} src_md5={prompt_fp} url={entry['url']} title={entry['title']}"
            ),
        })
    return rows, skipped


def run_intake(limit: int | None = None, dry_run: bool = False,
               chat=None) -> dict:
    """主流程：收件箱条目（未消化过）→ LLM 抽取 → 去重 → 出生证 → 卸台账 + seen log。

    chat 参数为测试注入位（缺省现场构造 OllamaChat，经 LSG）。
    单条目失败记 failed_urls 不阻断其余；失败条目不写 seen（下一班自愈重试）。
    """
    from zephyr.shared.utils.time_utils import now_utc
    # 台账 id 读取复用 B 车道实现防双真源（CLONE-GUARD 决议=委托）
    from scripts.backtest.lane_b_idea_generator import load_existing_ids

    if chat is None:
        from zephyr.integration.local_model.ollama_chat import OllamaChat
        chat = OllamaChat(model=MODEL)

    batch_id = now_utc().strftime("E1G-%Y%m%d-%H%M%S")
    seen = load_seen_urls(_SEEN_CSV)
    existing = load_existing_ids(_INTAKE_CSV)
    rows: list[dict] = []
    seen_rows: list[dict] = []
    failed: list[str] = []
    skipped_dup = 0
    processed = 0

    for entry in collect_inbox_entries(_INBOX_DIR):
        if limit is not None and processed >= limit:
            break
        url_md5 = hashlib.md5(entry["url"].encode("utf-8")).hexdigest()[:12]
        if url_md5 in seen:
            continue
        seen.add(url_md5)  # 同批重复条目（收件箱允许同源多命中）不重考
        processed += 1
        prompt = build_extraction_prompt(entry)
        raw = ""
        try:
            raw = chat.ask(prompt, system=EXTRACTION_SYSTEM, temperature=0.3)
            ideas = _parse_ideas(raw)
        except Exception as exc:  # noqa: BLE001 — LLM 不可达/被闸：该条记失败不标 seen，下一班重试
            failed.append(entry["url"])
            print(f"WARN 消化失败 {entry['url']}: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
            continue
        if "[" not in (raw or ""):
            # 回包无 JSON 数组痕迹=截断/跑题，按失败处理（不误标 seen 吞条目）
            failed.append(entry["url"])
            continue
        prompt_fp = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:12]
        new_rows, skipped = _build_rows(entry, ideas, batch_id, prompt_fp, existing)
        skipped_dup += skipped
        rows.extend(new_rows)
        # 空数组=诚实消化过（该研究给不出假说），同样记账不重考
        seen_rows.append({
            "url_md5": url_md5, "url": entry["url"], "title": entry["title"],
            "batch": batch_id, "n_candidates": len(new_rows),
        })

    record = {
        "batch": batch_id, "processed_entries": processed, "generated": len(rows),
        "skipped_dup": skipped_dup, "failed_urls": failed,
        "items": [{k: r[k] for k in ("candidate_id", "theme", "hypothesis_zh")}
                  for r in rows],
    }
    if not dry_run and (rows or seen_rows or failed):
        _INTAKE_CSV.parent.mkdir(parents=True, exist_ok=True)
        if rows:
            header = not _INTAKE_CSV.exists()
            pd.DataFrame(rows).to_csv(_INTAKE_CSV, mode="a", header=header,
                                      index=False, encoding="utf-8-sig")
        if seen_rows:
            header = not _SEEN_CSV.exists()
            pd.DataFrame(seen_rows).to_csv(_SEEN_CSV, mode="a", header=header,
                                           index=False, encoding="utf-8-sig")
        record["written_to"] = str(_INTAKE_CSV.relative_to(_ROOT))
    return record


def _parse_ideas(raw: str) -> list[dict]:
    """JSON 数组强解析（复用 B 车道解析器防双真源；CLONE-GUARD 决议=委托）。"""
    from scripts.backtest.lane_b_idea_generator import parse_ideas
    return parse_ideas(raw)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="FAC-E1G 车道G-全网搜索进货（消化胃收件箱→策略假说，经 LSG）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("run", help="消化未读收件箱条目并卸货")
    g.add_argument("--limit", type=int, default=None, help="本班最多消化条目数")
    g.add_argument("--dry-run", action="store_true", help="只回看不写台账/seen log")
    args = ap.parse_args()
    try:
        record = run_intake(limit=args.limit, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
