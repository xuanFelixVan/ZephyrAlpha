# [BLUEPRINT] MOD-BT-091 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.hypothesis_precheck
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; zephyr.integration.local_model.ollama_chat; zephyr.data.ch_config;
#   schemas.categories.backtest.backtest_hypothesis_precheck; scripts.backtest.intake_ledger_recon
# [CONSUMERS] 策略生产全景图 FAC-E2 假说预审逻辑门；E3 构造排产（只消费 precheck_passed）；
#   c1_backtest.hypothesis_precheck（判定记录台账）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] verdict/verdict_reason 由本模块代码生成禁手填；LLM 调用必经 OllamaChat（内置
#   LSG 闸门 fail-closed，MOD-INF-042/052）；运动员不兼任裁判——本门只做经济学预审，
#   考试权仍在 E4；deferred 不是拒绝（基础设施类失败不冤枉想法）⇒幂等集只认终局结论
#   （passed/rejected），deferred 必须留在重审通道（F21 治本，SQL_ALREADY 兑现）；
#   出生证原样携带不重导出；判定台账只追加；E2 前置台账对账 fail-open 但必须显式出声
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账不可写/进货源缺失); LSGBlockedError(prompt 被安全闸拒绝)
# [TESTS] tests/backtest/test_hypothesis_precheck.py
# [A_module] module_id=MOD-BT-091 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 预审器非常驻服务：由 E1 进货编排事件调用（接线前人工/会话触发），无常驻循环
"""FAC-E2 假说预审逻辑门——经济学是非题预审，讲不通的想法在此死，不花回测算力。

原理（讨论稿 v4/v5：FaVOR 回测前机制验证同构；Owner 原则"主观经验是先验过滤器，
AI 无中生有=冰淇淋销量式巧合"）：候选想法 → 本地 qwen3:8b 是非题预审（机制/前视/
成本/可证伪性/同义反复/边界六问）→ verdict 三态落 c1_backtest.hypothesis_precheck。

verdict 三态（学 strategy_screen）：precheck_passed / precheck_rejected / precheck_deferred
理由码（代码生成禁手填）：pass_mechanism_clear；reject_no_mechanism/reject_lookahead/
reject_cost_prohibitive/reject_unfalsifiable/reject_tautology/reject_out_of_scope；
defer_llm_unreachable/defer_parse_fail/defer_low_confidence。

用法:
  python scripts/backtest/hypothesis_precheck.py run --source data/strategy_intake/three_high_candidates.csv --limit 10
  python scripts/backtest/hypothesis_precheck.py run --source <csv> --dry-run
  python scripts/backtest/hypothesis_precheck.py status
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # schemas.* 在仓库根（CLI 直跑场景）

VERDICT_PASS = "precheck_passed"
VERDICT_REJECT = "precheck_rejected"
VERDICT_DEFER = "precheck_deferred"

REASON_PASS = "pass_mechanism_clear"
REJECT_REASONS = (
    "reject_no_mechanism",
    "reject_lookahead",
    "reject_cost_prohibitive",
    "reject_unfalsifiable",
    "reject_tautology",
    "reject_out_of_scope",
)
DEFER_REASONS = ("defer_llm_unreachable", "defer_parse_fail", "defer_low_confidence")
LOW_CONFIDENCE = 0.6

MODEL = "qwen3:8b"
SYSTEM_PROMPT = "你是量化策略假说预审员。只做经济学逻辑判断，不做回测。始终输出合法 JSON，不要输出额外文本。"

SQL_INSERT = "INSERT INTO {table} {cols} VALUES"  # INSERT_COLUMNS 自带括号
# F21 治本（2026-09-27，案卷 b_factory_inbound/09 卷缺口1）：幂等集**必须排除 deferred**——
# deferred 是基础设施类失败（LLM 断供/解析失败/低置信），不是结论；全表 DISTINCT 把 24 条
# defer 永久锁在"已审"集里=滞留死坑（:214 注释自认"deferred 可重跑"语义此前未被 SQL 兑现）。
# passed/rejected 才是终局结论（reject 不重审=省算力设计）。
SQL_ALREADY = f"SELECT DISTINCT candidate_id FROM {{table}} WHERE verdict != '{VERDICT_DEFER}'"


def _table() -> str:
    """台账全限定表名（SSOT=DDL-as-Code schema 常量，学 strategy_screen_query 先例）。"""
    from schemas.categories.backtest.backtest_hypothesis_precheck import DATABASE, TABLE_NAME

    return f"{DATABASE}.{TABLE_NAME}"


def build_prompt(hypothesis_zh: str, birth_channel: str = "", prior_note: str = "") -> str:
    """确定性预审 prompt（六问框架，同一输入必同一 prompt）。

    prior_note=法定回灌边 FL1/E9+FL2/E6 的先验注记（feedback_prior.precheck_prior_note
    产出；空串=零注入零干扰，prompt 保持字节级确定性回溯）。
    """
    prior_block = f"\n[回灌先验（只作背景不作判据）]\n{prior_note}\n" if prior_note else ""
    return (
        f"待审策略想法（出生车道 {birth_channel or '未知'}）：\n{hypothesis_zh}\n"
        f"{prior_block}\n"
        "按六问预审：\n"
        "1 机制：谁在和你交易？超额收益从谁的口袋来（行为偏差/风险溢价/结构性摩擦）？\n"
        "2 前视：是否隐含用到未来才知道的信息？\n"
        "3 成本：换手+冲击成本会不会吃掉全部边际？\n"
        "4 可证伪：能否被历史数据检验证伪？\n"
        "5 同义反复：是否只是同义反复或数据挖掘巧合（冰淇淋销量式）？\n"
        "6 边界：是否超出日频A股工厂边界（高频/做市/无法交易）？\n\n"
        '输出 JSON：{"verdict": "pass|reject|defer", "reason_code": "'
        "pass_mechanism_clear|reject_no_mechanism|reject_lookahead|reject_cost_prohibitive|"
        'reject_unfalsifiable|reject_tautology|reject_out_of_scope|defer_low_confidence", '
        '"confidence": 0到1的小数, "rationale": "一句话中文理由(40字内)"}'
    )


def parse_reply(raw: str) -> dict:
    """模型回复 → 判定 dict（确定性强解析：JSON 优先，关键词兜底，失败转 deferred）。

    Returns:
        {verdict, reason_code, confidence, rationale}，verdict ∈ 三态常量。
    """
    text = (raw or "").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            v = str(data.get("verdict", "")).lower()
            conf = data.get("confidence")
            conf_f = float(conf) if isinstance(conf, (int, float)) else None
            rc = str(data.get("reason_code", ""))
            rationale = str(data.get("rationale", ""))[:120]
            if v == "pass":
                return {
                    "verdict": VERDICT_PASS,
                    "reason_code": REASON_PASS,
                    "confidence": conf_f,
                    "rationale": rationale,
                }
            if v == "reject":
                if rc in REJECT_REASONS:
                    return {"verdict": VERDICT_REJECT, "reason_code": rc, "confidence": conf_f, "rationale": rationale}
                # 模型判 reject 但理由码不可映射：不落脏码，转低置信 defer 待重审
                return {
                    "verdict": VERDICT_DEFER,
                    "reason_code": "defer_low_confidence",
                    "confidence": conf_f,
                    "rationale": rationale,
                }
            if v == "defer":
                rc2 = rc if rc in DEFER_REASONS else "defer_low_confidence"
                return {"verdict": VERDICT_DEFER, "reason_code": rc2, "confidence": conf_f, "rationale": rationale}
            return _keyword_fallback(text)
        except (json.JSONDecodeError, ValueError):
            return _keyword_fallback(text)
    return _keyword_fallback(text)


def _keyword_fallback(text: str) -> dict:
    """关键词兜底（模型输出漂移时的确定性映射；无信号→defer_parse_fail）。"""
    t = text.lower()
    if "pass_mechanism_clear" in t or ("pass" in t and "reject" not in t):
        return {"verdict": VERDICT_PASS, "reason_code": REASON_PASS, "confidence": None, "rationale": text[:120]}
    for rc in REJECT_REASONS:
        if rc in t:
            return {"verdict": VERDICT_REJECT, "reason_code": rc, "confidence": None, "rationale": text[:120]}
    return {"verdict": VERDICT_DEFER, "reason_code": "defer_parse_fail", "confidence": None, "rationale": text[:120]}


def parse_reply_to_row(raw: str, base: dict) -> dict:
    """解析结果并入台账行（verdict/verdict_reason 代码生成；出生证原样携带）。"""
    v = parse_reply(raw)
    row = dict(base)
    row.update(v)
    return row


def precheck_one(chat, hypothesis_zh: str, birth_channel: str = "", prior_note: str = "") -> tuple[dict, int]:
    """单想法预审（返回 (判定dict, 耗时ms)；LLM 异常→defer_llm_unreachable）。

    prior_note=回灌先验注记（FL1/E9+FL2/E6 消费端，feedback_prior 产出；空串=不注入）。
    """
    prompt = build_prompt(hypothesis_zh, birth_channel, prior_note=prior_note)
    t0 = time.perf_counter()
    try:
        raw = chat.ask(prompt, system=SYSTEM_PROMPT, temperature=0.0)
    except Exception as exc:  # noqa: BLE001 — 含 LSGBlockedError/连接失败，均转 deferred 不冤枉想法
        return (
            {
                "verdict": VERDICT_DEFER,
                "reason_code": "defer_llm_unreachable",
                "confidence": None,
                "rationale": f"{type(exc).__name__}: {exc}"[:120],
            },
            int((time.perf_counter() - t0) * 1000),
        )
    ms = int((time.perf_counter() - t0) * 1000)
    return parse_reply(raw), ms


def load_candidates(source: str, limit: int | None = None) -> pd.DataFrame:
    """进货台账读取（CSV；birth 三件套原样携带；同 id 多行去重保首行）。

    F21 缺口2：limit 截断语义已移出本函数（见 select_pending）——在读取端截文件头
    会让已审行挤占名额，文件尾新增永远排不上。limit 参数仅为既有外部调用兼容保留。
    """
    path = Path(source)
    if not path.exists():
        raise RuntimeError(f"进货源不存在: {source}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    need = {"candidate_id", "hypothesis_zh", "birth_channel", "birth_batch"}
    missing = need - set(df.columns)
    if missing:
        raise RuntimeError(f"进货源缺列: {missing}")
    df = df.drop_duplicates(subset="candidate_id", keep="first")
    return df.head(limit) if limit else df


def select_pending(cands: pd.DataFrame, done: set[str], limit: int | None = None) -> pd.DataFrame:
    """幂等过滤后再截断（F21 缺口2 顺序对调）。

    原实现 load_candidates(source, limit) 先截文件头再过滤——台账头部堆积的已终判行
    挤占 limit 名额，文件尾部新增候选永远进不了当批。现语义：先剔除已终判 id，
    剩余（新增+待重审 deferred）才参与名额截断。
    """
    if done:
        cands = cands[~cands["candidate_id"].astype(str).isin(done)]
    return cands.head(limit) if limit else cands


def fetch_prechecked_ids() -> set[str]:
    """台账已预审 id 集（幂等跳过；CH 不可达返回空集不阻断）。"""
    try:
        from zephyr.data.ch_writer import get_client_strict

        cli = get_client_strict()
        return {r[0] for r in cli.execute(SQL_ALREADY.format(table=_table()))}
    except Exception:  # noqa: BLE001 — 幂等查询失败降级为全量重审（deferred 可重跑语义）
        return set()


def insert_verdicts(rows: list[dict]) -> int:
    """判定行写台账（writer 通道；返回写入行数）。"""
    if not rows:
        return 0
    from schemas.categories.backtest.backtest_hypothesis_precheck import INSERT_COLUMNS
    from zephyr.data.ch_writer import get_client_strict

    cli = get_client_strict()
    table = _table()
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    tuples = [
        (
            r["precheck_batch"],
            r["candidate_id"],
            str(r["birth_channel"]),
            r["birth_batch"],
            r["hypothesis_zh"],
            r.get("model", MODEL),
            r["verdict"],
            r["reason_code"],
            r.get("confidence"),
            r.get("rationale", ""),
            r.get("latency_ms"),
            now,
            r.get("notes", ""),
        )
        for r in rows
    ]
    cli.execute(SQL_INSERT.format(table=table, cols=INSERT_COLUMNS), tuples)
    return len(tuples)


def ledger_preflight(source: str) -> dict:
    """E2 前置对账（F16 治本，MOD-BT-231）：进货台账 ↔ CH 判定台账漂移报告。

    fail-open：对账故障不阻断预审主链；但故障必须显式出声（status=probe_failed），
    禁静默归零判全绿。drift 只报不拦——E2 消费的是 csv 现有行，重建是独立动作。
    """
    try:
        from scripts.backtest.intake_ledger_recon import STATUS_DRIFT, STATUS_PROBE_FAILED, preflight

        report = preflight(source)
    except Exception as exc:  # noqa: BLE001 — 对账器自身异常降级为显式探针失败
        return {"status": "probe_failed", "error": f"{type(exc).__name__}: {exc}"[:200]}
    if report.get("status") in (STATUS_DRIFT, STATUS_PROBE_FAILED):
        loud = {k: v for k, v in report.items() if k != "detail"}
        print(f"[E2-PREFLIGHT] 台账对账 {report['status']}: {json.dumps(loud, ensure_ascii=False)}", file=sys.stderr)
    return report


def run(source: str, limit: int | None = None, dry_run: bool = False) -> dict:
    """主流程：前置对账→读进货→幂等过滤→名额截断→逐条预审→落台账→汇总。"""
    recon = ledger_preflight(source)
    cands = load_candidates(source)
    done = fetch_prechecked_ids()
    cands = select_pending(cands, done, limit)  # F21 缺口2：先幂等过滤后截断，名额只给真新增
    if cands.empty:
        return {"batch": None, "message": "无新增候选（全部已预审或源为空）", "ledger_recon": recon}

    from zephyr.integration.local_model.ollama_chat import OllamaChat

    # 回灌先验（FL1/E9+FL2/E6 消费端，st-ec2-p0）：fail-open——读数失败=空注记，
    # 预审主链零依赖（先验是增益不是依赖）；prompt 背景注入+判定行 notes 审计留痕。
    prior_note = ""
    try:
        from scripts.backtest import feedback_prior

        prior_note = feedback_prior.precheck_prior_note(
            feedback_prior.decay_prior_digest(),
            feedback_prior.attribution_prior_digest(),
        )
    except Exception:  # noqa: BLE001 — 先验失败不阻断预审（fail-open）
        prior_note = ""

    chat = OllamaChat(model=MODEL)
    batch_id = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("E2-%Y%m%d-%H%M%S")
    rows: list[dict] = []
    for _, c in cands.iterrows():
        verdict, ms = precheck_one(chat, str(c["hypothesis_zh"]), str(c["birth_channel"]), prior_note=prior_note)
        rows.append(
            {
                "precheck_batch": batch_id,
                "candidate_id": c["candidate_id"],
                "birth_channel": c["birth_channel"],
                "birth_batch": c["birth_batch"],
                "hypothesis_zh": str(c["hypothesis_zh"]),
                "model": MODEL,
                "latency_ms": ms,
                "notes": prior_note,
                **verdict,
            }
        )
    summary = {
        "batch": batch_id,
        "prechecked": len(rows),
        "passed": sum(1 for r in rows if r["verdict"] == VERDICT_PASS),
        "rejected": sum(1 for r in rows if r["verdict"] == VERDICT_REJECT),
        "deferred": sum(1 for r in rows if r["verdict"] == VERDICT_DEFER),
        "ledger_recon": recon,
        "reason_codes": {rc: sum(1 for r in rows if r["reason_code"] == rc) for rc in {r["reason_code"] for r in rows}},
    }
    if not dry_run:
        summary["written"] = insert_verdicts(rows)
    summary["items"] = [
        {k: r[k] for k in ("candidate_id", "verdict", "reason_code", "confidence", "rationale")} for r in rows
    ]
    return summary


def cmd_status() -> int:
    """台账判定×理由码分布（只读）。"""
    from zephyr.data.ch_writer import get_client_strict

    cli = get_client_strict()
    table = _table()
    total = cli.execute(f"SELECT count() FROM {table}")[0][0]
    dist = cli.execute(f"SELECT verdict, verdict_reason, count() FROM {table} GROUP BY 1,2 ORDER BY 1,2")  # noqa: bare-sql  存量参数化状态查询（表名经 _table() 派生），本批行号漂移伪新增豁免
    print(
        json.dumps(
            {"total": total, "distribution": [{"verdict": v, "reason": r, "rows": n} for v, r, n in dist]},
            ensure_ascii=False,
            indent=1,
        )
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E2 假说预审逻辑门（本地 qwen3:8b，经 LSG）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="预审进货台账新增候选")
    r.add_argument("--source", default="data/strategy_intake/three_high_candidates.csv")
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--dry-run", action="store_true", help="只审不落库")
    sub.add_parser("status", help="判定台账分布（只读）")
    args = ap.parse_args()
    if args.cmd == "status":
        return cmd_status()
    try:
        record = run(args.source, args.limit, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
