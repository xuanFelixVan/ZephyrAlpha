# [BLUEPRINT] MOD-BT-193 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.graph_enrich_staging
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.integration.local_model.ollama_chat; zephyr.data.ch_config; zephyr.data.table_registry
# [CONSUMERS] 策略生产全景图 FAC-E1D 升级路线 v5.1 第一期（抽取→暂存；入图另批）；
#   data/strategy_intake/graph_enrich_staging.csv（候选关系暂存台账）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] **绝不写 ig_fact 正图**（独家数据资产，LLM 抽取=候选非事实，入图需 Owner
#   审核另批）；只产暂存 CSV；供应商≠客户；置信度<阈值丢弃；evidence 原文摘录强制
#   （无证据=丢弃，防幻觉）；抽样范围=含供应链关键词的新闻；LLM 调用必经 OllamaChat
#   （内置 LSG）；台账只追加
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(新闻源不可达); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_graph_enrich_staging.py
# [A_module] module_id=MOD-BT-193 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 抽取器非常驻服务：由夜批/会话事件调用，无常驻循环
"""FAC-E1D 升级路线 v5.1 第一期——新闻→LLM 抽取供应链关系→暂存台账（不入正图）。

原理（立项书 §七 + 裁定记录附二：图谱增补管线 P0 切片）：news_data 含供应链关键词的
新闻 → OllamaChat 结构化抽取 (supplier, product, customer, confidence, evidence) →
校验（supplier≠customer、confidence≥0.7、evidence 非空）→ 暂存 CSV。入图（写 ig_fact）
需 Owner 审核暂存台账后另批执行——候选≠事实。

用法:
  python scripts/backtest/graph_enrich_staging.py extract --sample 5
  python scripts/backtest/graph_enrich_staging.py extract --sample 20 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_STAGING_CSV = _ROOT / "data" / "strategy_intake" / "graph_enrich_staging.csv"

MODEL_DEFAULT = "qwen3:8b"
CONFIDENCE_FLOOR = 0.7
KEYWORDS = ("供应商", "供货", "上游", "下游", "客户", "订单", "采购", "中标")

SQL_NEWS_SAMPLE = (
    "SELECT id, title, content FROM {t} "
    "WHERE ({kw}) AND content IS NOT NULL AND length(content) > 50 "
    "ORDER BY publish_time DESC LIMIT {limit}"
)
STAGING_COLS = ["news_id", "supplier", "product", "customer", "confidence",
                "evidence", "model", "extracted_at", "status"]


def build_extract_prompt(title: str, content: str, features_hint: str = "") -> str:
    """确定性抽取 prompt（evidence 强制原文摘录，防幻觉边界写进事前约束）。"""
    text = content[:1200]
    return (
        f"新闻标题：{title}\n新闻正文：{text}\n\n"
        "从上述内容抽取一条供应链关系（若有多条只取最明确的一条）。规则：\n"
        "1 supplier/customer 必须是正文出现的真实主体名（公司/机构/环节名），"
        "禁止编造正文没有的名字\n"
        "2 evidence 必须是正文原文摘录（逐字），无原文支撑=不可抽取\n"
        "3 supplier 与 customer 必须不同\n"
        "4 若正文没有明确的供应链关系，如实输出 discovered=false\n\n"
        "输出单个 JSON 对象："
        '{"discovered": true, "supplier": "...", "product": "...", '
        '"customer": "...", "confidence": 0到1, "evidence": "原文摘录"} '
        '或 {"discovered": false, "reason": "..."}'
    )


def parse_extraction(raw: str) -> dict:
    """LLM 回复→抽取判定（JSON 对象强解析；解析失败=未发现）。"""
    import re

    text = (raw or "").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict) and "discovered" in data:
                data.setdefault("reason", "")
                return data
        except json.JSONDecodeError:
            pass
    return {"discovered": False, "reason": "parse_fail"}


def validate_extraction(ext: dict) -> tuple[bool, str]:
    """抽取校验（supplier≠customer、confidence 地板、evidence 非空）。"""
    if not ext.get("discovered"):
        return False, str(ext.get("reason", "not_discovered"))[:60]
    s, c = str(ext.get("supplier", "")).strip(), str(ext.get("customer", "")).strip()
    if not s or not c:
        return False, "主体空"
    if s == c:
        return False, "supplier=customer"
    try:
        conf = float(ext.get("confidence", 0))
    except (TypeError, ValueError):
        return False, "confidence 非数值"
    if conf < CONFIDENCE_FLOOR:
        return False, f"confidence {conf}<{CONFIDENCE_FLOOR}"
    if not str(ext.get("evidence", "")).strip():
        return False, "evidence 空（无原文支撑=疑似幻觉）"
    return True, ""


def fetch_news_sample(limit: int) -> pd.DataFrame:
    """新闻抽样：含供应链关键词的最新 N 条（CH news_data）。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from zephyr.data.table_registry import get_registry
    from clickhouse_driver import Client

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    kw = " OR ".join(f"content LIKE '%{k}%'" for k in KEYWORDS)
    sql = SQL_NEWS_SAMPLE.format(t=get_registry().table("fund_news_data"),
                                 kw=kw, limit=int(limit))
    rows = cli.execute(sql)
    return pd.DataFrame(rows, columns=["news_id", "title", "content"])


def run_extract(sample: int, model: str, dry_run: bool = False) -> dict:
    """主流程：抽样→LLM 抽取→校验→暂存台账。绝不写 ig_fact 正图。"""
    from zephyr.integration.local_model.ollama_chat import OllamaChat

    news = fetch_news_sample(sample)
    if news.empty:
        raise RuntimeError("新闻抽样为空（检查 news_data 通道/关键词）")
    chat = OllamaChat(model=model, timeout_s=300.0)
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    manifest_rows: list[dict] = []
    accepted = 0
    for _, nrow in news.iterrows():
        prompt = build_extract_prompt(str(nrow["title"]), str(nrow["content"]))
        try:
            raw = chat.ask(prompt, temperature=0.1)
        except Exception as exc:  # noqa: BLE001 — LSG/连接失败记因继续
            manifest_rows.append({
                "news_id": nrow["news_id"], "supplier": "", "product": "",
                "customer": "", "confidence": "", "evidence": "",
                "model": model, "extracted_at": now.isoformat(timespec="seconds"),
                "status": f"llm_error:{type(exc).__name__}"})
            continue
        ext = parse_extraction(raw)
        ok, why = validate_extraction(ext)
        if not ok:
            manifest_rows.append({
                "news_id": nrow["news_id"], "supplier": str(ext.get("supplier", ""))[:80],
                "product": str(ext.get("product", ""))[:80],
                "customer": str(ext.get("customer", ""))[:80],
                "confidence": ext.get("confidence", ""), "evidence": "",
                "model": model, "extracted_at": now.isoformat(timespec="seconds"),
                "status": f"rejected:{why}"})
            continue
        accepted += 1
        manifest_rows.append({
            "news_id": nrow["news_id"], "supplier": ext["supplier"],
            "product": str(ext.get("product", ""))[:80], "customer": ext["customer"],
            "confidence": float(ext["confidence"]),
            "evidence": str(ext["evidence"])[:300], "model": model,
            "extracted_at": now.isoformat(timespec="seconds"),
            "status": "staged" if not dry_run else "staged_dry"})
    record = {
        "batch": now.strftime("GE-%Y%m%d-%H%M%S"), "model": model,
        "sampled": len(news), "accepted": accepted,
        "staging_csv": str(_STAGING_CSV.relative_to(_ROOT)) if not dry_run else None,
        "rows": manifest_rows,
    }
    if not dry_run and manifest_rows:
        df = pd.DataFrame(manifest_rows)
        for c in STAGING_COLS:
            if c not in df.columns:
                df[c] = ""
        df = df[[c for c in STAGING_COLS if c in df.columns]]
        df.to_csv(_STAGING_CSV, mode="a", header=not _STAGING_CSV.exists(),
                  index=False, encoding="utf-8-sig")
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1D 图谱增补 P0：新闻→抽取→暂存（绝不写正图）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("extract", help="抽取供应链关系到暂存台账")
    m.add_argument("--sample", type=int, default=5, help="抽样新闻条数")
    m.add_argument("--model", default=MODEL_DEFAULT)
    m.add_argument("--dry-run", action="store_true", help="只回看不写暂存")
    args = ap.parse_args()
    try:
        record = run_extract(args.sample, args.model, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
