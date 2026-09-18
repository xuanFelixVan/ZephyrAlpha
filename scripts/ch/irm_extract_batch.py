# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.ch.irm_extract_batch
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; zephyr.integration.local_model.ollama_chat; PyMuPDF(fitz)
# [CONSUMERS] C6/C9 文本抽取试点批+后续波次（altdata_line 09 清单 D7 波3）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 断点=抽取表既有 qa_id/record_id（重跑自动跳过）；
#              反幻觉=evidence/involves_product/visited_orgs 必须原文逐字（列表型字段逐部件校验；
#              空白/引号归一化后 substring 比对，fail-closed 入人工池）；supply=概括句由 evidence 锚定；
#              置信度门=<0.7 或校验不过 → review_status='manual_pool' 不入下游（approved 唯一消费态）；
#              未回答提问不抽取（无公司信号）；PDF 无文本（扫描件）→ manual_pool 留档；
#              LLM 输出 JSON schema 强校验 fail-closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH/Ollama 不可达->exit 1；单条失败不阻断（计 manual_pool 留档）
# [TESTS] 试点批次报告即验收物（--out JSON）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: LLM 抽取批处理 CLI（A 类批次运维）
"""irm_extract_batch.py — D7 文本抽取批处理（C6 互动易问答 + C9 调研纪要）。

raw 层（irm_provider 爬取入库+G盘快照）→ 本件 LLM 抽取 → 抽取表（置信度门）。

抽取字段：涉及产品 / 供应链关系 / (C9)接待机构 / 情绪极性 / 置信度 / 证据原文。
防幻觉契约（承 scripts/backtest/graph_enrich_staging.py _EXTRACT_RULES）：
    1) 所有实体名必须是原文出现的真实名称，禁止编造；
    2) evidence 必须逐字摘录原文（机械 substring 校验兜底）；
    3) 原文没有对应信号时如实输出空串/neutral；
    4) confidence 自评 0-1，<0.7 机械入人工池。

可复现：extraction_confidence / model_version / prompt_version 三列入表。

用法::

    python scripts/ch/irm_extract_batch.py --source qa --limit 50 --out .runtime/tmp/irm_pilot_qa.json
    python scripts/ch/irm_extract_batch.py --source ir --limit 40
    python scripts/ch/irm_extract_batch.py --source all
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

PROMPT_VERSION = "irm_extract_v1.1"  # v1.1: 验证器修——列表型字段逐部件逐字+引号归一；supply 概括句以 evidence 逐字锚定
MODEL_DEFAULT = "qwen3:8b"
CONFIDENCE_FLOOR = 0.7
MAX_SOURCE_CHARS = 3000  # 防超上下文（互动易问答/纪要节选足够）
_VALID_SENTIMENT = {"positive", "neutral", "negative"}

_SYSTEM = "你是A股文本信息抽取器。只输出一个合法 JSON 对象，不要输出任何其他文本。"

# 防幻觉抽取契约（_EXTRACT_RULES 同源约束，字段按 D7 清单定制）
_EXTRACT_RULES = (
    "从上述材料抽取：涉及产品/业务、供应链关系、情绪极性。规则：\n"
    "1 involves_product 只能填材料中逐字出现的公司产品/业务名，多个用逗号分隔，"
    "没有则输出空串；禁止编造材料没有的名字\n"
    "2 supply_chain_relation 只有当材料明确出现供需/上下游/客户/供应商/中标/采购等关系时"
    "才输出一句概括（主体名必须逐字来自材料），否则输出空串\n"
    "3 sentiment 是公司表态口径对公司经营前景的情绪极性：positive/neutral/negative 三选一；"
    "套话敷衍/无实质信息一律 neutral\n"
    "4 visited_orgs 仅调研纪要类材料填写（接待/参与机构名，逐字来自材料，逗号分隔，"
    "没有则空串）；其他材料一律空串\n"
    "5 evidence 必须是材料原文的逐字摘录（支撑你判断的最短片段，≤120字），禁止改写\n"
    "6 confidence 是你对本次抽取正确性的自评 0 到 1；材料含糊/信息不足时必须给低分\n\n"
    "输出单个 JSON 对象："
    '{"involves_product": "...", "supply_chain_relation": "...", "visited_orgs": "", '
    '"sentiment": "positive|neutral|negative", "confidence": 0到1, "evidence": "原文逐字摘录"}'
)


def build_prompt(material: str) -> str:
    return f"材料：{material[:MAX_SOURCE_CHARS]}\n\n" + _EXTRACT_RULES


def parse_extraction(raw: str) -> dict:
    """LLM 回复 → dict（单 JSON 对象强解析；失败返回 {} 由上层计 parse_fail）。"""
    text = (raw or "").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {}


_NORM_WS = re.compile(r"\s+")
# 逐字比对前的引号归一（LLM 摘录常把原文直角/弯引号转成直引号，词句本身未改=仍算逐字）
_QUOTE_MAP = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "「": '"', "」": '"'})


def _norm(text: str) -> str:
    """归一化空白+引号后的逐字比对基底（拒绝改写词句，容忍空白/引号形态漂移）。"""
    t = _NORM_WS.sub("", text or "")
    return t.translate(_QUOTE_MAP)


def _verbatim(field: str, source_norm: str) -> bool:
    return not field or _norm(field) in source_norm


# 列表型字段分隔符（LLM 常以逗号/顿号/分号/换行连接多个实体名）
_LIST_SEP = re.compile(r"[,，、;；/\n]+")


def pdf_text(path: str) -> str:
    """G盘 PDF 快照 → 全文（fitz，承 c4_history_repair 同款依赖）。"""
    import fitz

    doc = fitz.open(path)
    try:
        return "\n".join(pg.get_text() for pg in doc)
    finally:
        doc.close()


def _tsv_unescape(s: str) -> str:
    """ClickHouse TSV 字符串字段反转义（\\n \\t \\\\ \\'）。"""
    return (
        s.replace("\\\\", "\x00")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\\'", "'")
        .replace("\x00", "\\")
    )


def pending_rows(source: str, limit: int) -> list[dict]:
    """取未抽取的 raw 行（LEFT ANTI 抽取表；C6 只取已回答）。"""
    from zephyr.data import ch_reader

    if source == "qa":
        sql = (
            "SELECT qa_id, stock_code, question_date, answer_date, question_text, answer_text "
            "FROM c3_fundamental.irm_interactive_qa FINAL "
            "WHERE answer_text != '' AND qa_id NOT IN "
            "(SELECT qa_id FROM c3_fundamental.irm_interactive_extracted) "
            f"ORDER BY question_date DESC, qa_id LIMIT {limit}"
        )
    else:
        sql = (
            "SELECT record_id, stock_code, publish_date, snapshot_path, title "
            "FROM c3_fundamental.ir_activity_record FINAL "
            "WHERE snapshot_path != '' AND record_id NOT IN "
            "(SELECT record_id FROM c3_fundamental.ir_activity_extracted) "
            f"ORDER BY publish_date DESC, record_id LIMIT {limit}"
        )
    out = ch_reader.query(sql)
    rows = [ln.split("\t") for ln in out.strip().split("\n") if ln and "\t" in ln]
    if source == "qa":
        keys = ("qa_id", "stock_code", "question_date", "answer_date", "question_text", "answer_text")
    else:
        keys = ("record_id", "stock_code", "publish_date", "snapshot_path", "title")
    result = []
    for r in rows:
        if len(r) != len(keys):
            continue
        d = dict(zip(keys, (_tsv_unescape(x) for x in r)))
        d["answer_date"] = d["answer_date"].strip("\\N") if source == "qa" else ""
        if d["answer_date"] in ("", "N", "NULL"):
            d["answer_date"] = ""
        result.append(d)
    return result


def _list_verbatim(field: str, source_norm: str) -> bool:
    """列表型字段（产品/机构）逐部件逐字校验：每个部件都必须原文逐字出现。"""
    parts = [p.strip() for p in _LIST_SEP.split(field) if p.strip()]
    return all(_norm(p) in source_norm for p in parts)


def validate(ext: dict, source_norm: str, is_ir: bool) -> tuple[str, str, dict]:
    """schema 强校验+反幻觉门。返回 (review_status, reject_reason, clean_fields)。"""
    if not ext:
        return "manual_pool", "parse_fail", {}
    sentiment = str(ext.get("sentiment", "")).strip().lower()
    if sentiment not in _VALID_SENTIMENT:
        return "manual_pool", "sentiment_invalid", {}
    try:
        conf = float(ext.get("confidence", 0))
    except (TypeError, ValueError):
        return "manual_pool", "confidence_non_numeric", {}
    if not (0.0 <= conf <= 1.0):
        return "manual_pool", "confidence_out_of_range", {}
    product = str(ext.get("involves_product", "")).strip()
    supply = str(ext.get("supply_chain_relation", "")).strip()
    orgs = str(ext.get("visited_orgs", "")).strip() if is_ir else ""
    evidence = str(ext.get("evidence", "")).strip()
    # 反幻觉硬检查：证据/产品/机构必须原文逐字（逐部件）；supply 是概括句，
    # 逐字锚定由 evidence 承担（prompt 契约：主体名须逐字，机械锚=evidence）
    if not _verbatim(evidence, source_norm):
        return "manual_pool", "evidence_not_verbatim", {}
    if not _list_verbatim(product, source_norm):
        return "manual_pool", "product_not_verbatim", {}
    if is_ir and orgs and not _list_verbatim(orgs, source_norm):
        return "manual_pool", "orgs_not_verbatim", {}
    status = "approved" if conf >= CONFIDENCE_FLOOR else "manual_pool"
    reason = "" if status == "approved" else f"confidence {conf:.2f}<{CONFIDENCE_FLOOR}"
    return status, reason, {
        "involves_product": product,
        "supply_chain_relation": supply,
        "visited_orgs": orgs,
        "sentiment": sentiment,
        "confidence": conf,
        "evidence": evidence,
    }


def persist(table: str, columns: str, rows: list[tuple]) -> int:
    if not rows:
        return 0
    from zephyr.data import ch_writer
    from zephyr.data.provider_base import FetchResult

    fr = FetchResult(
        table=table,
        columns=[c.strip() for c in columns.strip("()").split(",")],
        rows=rows,
        last_key="",
        elapsed_sec=0.0,
    )
    ok = ch_writer.write_result(fr)
    return len(rows) if ok else 0


def _material_and_pit(source: str, row: dict, model: str) -> tuple[str, str, str, tuple | None]:
    """构造抽取材料与 PIT 锚。返回 (material, source_norm, pit, manual_row)。

    manual_row 非 None 表示材料不可抽取（PDF 无文本），已构造人工池行。
    """
    if source == "ir":
        material = pdf_text(row["snapshot_path"])
        if not material.strip():
            manual = (row["record_id"], row["stock_code"], row["publish_date"], "", "", "", "neutral",
                      0.0, "", "manual_pool", "pdf_text_empty", model, PROMPT_VERSION)
            return "", "", row["publish_date"], manual
        return material, _norm(material), row["publish_date"], None
    material = f"提问：{row['question_text']}\n公司回答：{row['answer_text']}"
    return material, _norm(row["question_text"] + row["answer_text"]), (row["answer_date"] or row["question_date"]), None


def _extract_row(chat, source: str, row: dict, model: str, stats: Counter, conf_bucket: Counter) -> tuple:
    """单条端到端：材料→LLM→校验门→插表行。异常向上抛（调用方计 error）。"""
    is_ir = source == "ir"
    rid = row["record_id"] if is_ir else row["qa_id"]
    material, source_norm, pit, manual = _material_and_pit(source, row, model)
    if manual is not None:
        stats["manual_pool"] += 1
        stats["reject:pdf_text_empty"] += 1
        return manual
    ext = parse_extraction(chat.ask(build_prompt(material), system=_SYSTEM, temperature=0.0))
    status, reason, clean = validate(ext, source_norm, is_ir)
    stats[status] += 1
    if reason:
        stats[f"reject:{reason}"] += 1
    if clean:
        b = "high" if clean["confidence"] >= 0.9 else ("mid" if clean["confidence"] >= 0.7 else "low")
        conf_bucket[b] += 1
        conf_bucket[f"sent:{clean['sentiment']}"] += 1
    tail = (clean.get("sentiment", "neutral"), clean.get("confidence", 0.0),
            clean.get("evidence", ""), status, reason, model, PROMPT_VERSION)
    if is_ir:
        return (rid, row["stock_code"], pit, clean.get("visited_orgs", ""),
                clean.get("involves_product", ""), clean.get("supply_chain_relation", ""), *tail)
    return (rid, row["stock_code"], pit,
            clean.get("involves_product", ""), clean.get("supply_chain_relation", ""), *tail)


def run_source(source: str, limit: int, model: str, workers: int) -> dict:
    from zephyr.integration.local_model.ollama_chat import OllamaChat

    chat = OllamaChat(model=model)
    chat.verify()
    is_ir = source == "ir"
    rows = pending_rows(source, limit)
    print(f"[{source}] 待抽取 {len(rows)} 条", flush=True)
    stats: Counter = Counter()
    conf_bucket: Counter = Counter()
    insert_cols = (
        "(record_id, stock_code, pit_date, visited_orgs, involves_product, supply_chain_relation, "
        "sentiment, extraction_confidence, evidence, review_status, reject_reason, model_version, prompt_version)"
        if is_ir
        else "(qa_id, stock_code, pit_date, involves_product, supply_chain_relation, "
        "sentiment, extraction_confidence, evidence, review_status, reject_reason, model_version, prompt_version)"
    )
    table = "c3_fundamental.ir_activity_extracted" if is_ir else "c3_fundamental.irm_interactive_extracted"
    out_rows: list[tuple] = []
    t0 = time.time()
    for i, row in enumerate(rows, 1):
        rid = row["record_id"] if is_ir else row["qa_id"]
        try:
            out_rows.append(_extract_row(chat, source, row, model, stats, conf_bucket))
        except Exception as exc:  # noqa: BLE001 — 单条失败不阻断
            stats["error"] += 1
            print(f"  [{i}] {rid} 异常: {exc}", flush=True)
            continue
        if i % 10 == 0:
            el = time.time() - t0
            print(f"  进度 {i}/{len(rows)} 已用 {el:.0f}s", flush=True)
        if len(out_rows) >= 20:
            n = persist(table, insert_cols, out_rows)
            stats["written"] += n
            out_rows = []
    n = persist(table, insert_cols, out_rows)
    stats["written"] += n
    return {
        "source": source,
        "pending": len(rows),
        "stats": dict(stats),
        "confidence_bucket": dict(conf_bucket),
        "elapsed_sec": round(time.time() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="D7 文本抽取批处理（C6 互动易+C9 调研纪要，置信度门 0.7）")
    ap.add_argument("--source", default="all", choices=["qa", "ir", "all"])
    ap.add_argument("--limit", type=int, default=0, help="每源最多处理条数（0=不限）")
    ap.add_argument("--model", default=MODEL_DEFAULT)
    ap.add_argument("--workers", type=int, default=1, help="预留（当前顺序抽取，GPU 单卡串行）")
    ap.add_argument("--out", default=None, help="批次报告 JSON 路径")
    args = ap.parse_args()

    sources = ["qa", "ir"] if args.source == "all" else [args.source]
    reports = []
    for s in sources:
        reports.append(run_source(s, args.limit, args.model, args.workers))

    print("\n===== 批次报告 =====")
    print(json.dumps(reports, ensure_ascii=False, indent=1))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(reports, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"WROTE {args.out}")


if __name__ == "__main__":
    main()
