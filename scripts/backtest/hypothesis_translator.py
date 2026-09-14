# [BLUEPRINT] MOD-BT-190 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.hypothesis_translator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.integration.local_model.ollama_chat; scripts.backtest.factor_strategy_template; scripts.backtest.lane_c_formula_miner; schemas.categories.backtest.backtest_hypothesis_precheck
# [CONSUMERS] 策略生产全景图 FAC-E3 构造翻译（假说轨 C3 公式化子集 MVP）；
#   data/strategy_intake/translated_manifest.csv（翻译台账）；E4 考卷件（经 159 桥生成）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] MVP 边界=假说→因子表达式公式化子集（自然语言→任意代码不在此轨，防幻觉）；
#   不可公式化的假说如实记 translatable=false（阴性档案，禁硬翻）；表达式必须过 DSL
#   白名单校验+非退化 sanity；翻译台账只追加；LLM 调用必经 OllamaChat（内置 LSG）；
#   出生证字段从 E2 台账原样携带（原假说 birth 链保持），翻译行为记入 birth_source 尾注；
#   生成考卷件入 translated/ 前必须过 creation_token 登记
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(种子缺失/白名单缺失); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_hypothesis_translator.py
# [A_module] module_id=MOD-BT-190 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 翻译器非常驻服务：由 E3 排产/夜批事件调用，无常驻循环
"""FAC-E3 假说轨 C3 翻译 MVP（公式化子集）——E2 过审假说 → 因子表达式考卷件。

边界（第一性原理：100% AI 开发必须防幻觉，宁窄勿错）：
  只翻"可表达为白名单 DSL 因子表达式"的假说（如估值/动量/波动类单因子假说）；
  涉及事件窗口/财报公告/多腿组合的假说如实判 translatable=false 入阴性台账，
  等表达式空间扩展后再翻。这是 C3 翻译专项第一期；全量 NL→代码翻译为后续立项。

流程：E0 问闸（local）→ E2 台账取 D/B 过审假说 → OllamaChat 结构化翻译
（translatable/expression/description/mechanism/top_n）→ DSL 校验+非退化 sanity →
159 桥生成考卷件 → 翻译台账（含阴性记录）。

用法:
  python scripts/backtest/hypothesis_translator.py translate --seeds 3
  python scripts/backtest/hypothesis_translator.py translate --model deepseek-r1:8b --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_MANIFEST_CSV = _ROOT / "data" / "strategy_intake" / "translated_manifest.csv"

MODEL_DEFAULT = "qwen3:8b"
SQL_TRANSLATION_SEEDS = (
    "SELECT candidate_id, birth_channel, hypothesis_zh FROM {table} "
    "WHERE verdict = 'precheck_passed' AND birth_channel IN ('D', 'B') "
    "ORDER BY prechecked_at DESC LIMIT {limit}"
)
MANIFEST_COLS = ["candidate_id", "birth_channel", "hypothesis_zh", "expression",
                 "mechanism", "top_n", "translatable", "refusal_reason", "model",
                 "exam_file", "translated_at"]


def build_translation_prompt(hypothesis: str, features: list[str],
                             op_names: list[str]) -> str:
    """确定性翻译 prompt（公式化子集边界写进事前约束）。"""
    return (
        f"市场假说：{hypothesis}\n\n"
        f"把这条假说翻译成一个量化因子表达式（日频A股，多头）。\n"
        f"规则：\n"
        f"1 只准用这些算子（嵌套函数调用）：{', '.join(op_names)}\n"
        f"2 只准用这些输入变量：{', '.join(features)}\n"
        f"3 mechanism 必须回答交易对手三问：①谁在卖给你 ②他们为什么愿意亏 "
        f"③什么成本会吃掉边际；空话=不可翻译\n"
        f"4 若假说无法用上述算子+变量表达（如涉及事件窗口/财报公告/多腿组合/基本面"
        f"字段），必须如实输出 translatable=false 并给 refusal_reason——禁止硬翻\n\n"
        "输出单个 JSON 对象："
        '{"translatable": true, "expression": "op(x, y)", "description": "...", '
        '"mechanism": "①...②...③...", "top_n": 20} '
        '或 {"translatable": false, "refusal_reason": "..."}'
    )


def parse_translation(raw: str) -> dict:
    """LLM 回复→翻译判定（JSON 对象强解析；解析失败=不可翻译+解析失败原因）。"""
    text = (raw or "").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(0))
            if isinstance(data, dict) and "translatable" in data:
                data.setdefault("refusal_reason", "")
                return data
        except json.JSONDecodeError:
            pass
    return {"translatable": False, "refusal_reason": "parse_fail"}


def fetch_translation_seeds(limit: int) -> list[dict]:
    """E2 台账 D/B 过审假说（翻译种子；不可达=空→上层报缺）。"""
    from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config
    from clickhouse_driver import Client

    from schemas.categories.backtest.backtest_hypothesis_precheck import (
        DATABASE,
        TABLE_NAME,
    )

    ensure_ch_env_loaded()
    cfg = load_ch_reader_config()
    cli = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                 user=cfg.get("user", "default"), password=cfg.get("password", ""),
                 connect_timeout=5)
    rows = cli.execute(
        SQL_TRANSLATION_SEEDS.format(table=f"{DATABASE}.{TABLE_NAME}", limit=int(limit)))
    return [{"candidate_id": r[0], "birth_channel": r[1], "hypothesis_zh": r[2]}
            for r in rows]


def load_translated_ids() -> set[str]:
    """翻译台账已登记 id 集（幂等）。"""
    if not _MANIFEST_CSV.exists():
        return set()
    try:
        return set(pd.read_csv(_MANIFEST_CSV, encoding="utf-8-sig")["candidate_id"]
                   .astype(str))
    except Exception:  # noqa: BLE001 — 台账损坏重建
        return set()


def run_translate(model: str, seeds_limit: int, universe_n: int, days: int,
                  top_n: int, dry_run: bool = False) -> dict:
    """主流程：问闸→种子→LLM 翻译→校验→桥生成考卷件→翻译台账。"""
    from scripts.backtest.compute_window_gate import check_gate
    from scripts.backtest.factor_strategy_template import (
        generate_strategy_file,
        strategy_id_for,
    )
    from scripts.backtest.lane_c_formula_miner import (
        FEATURES,
        fetch_panel,
        load_whitelist,
    )
    from scripts.backtest.lane_c2_agentic_miner import (
        build_eval_ops,
        evaluate_expr,
        validate_expr,
    )
    from zephyr.integration.local_model.ollama_chat import OllamaChat

    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    gate = check_gate("lane_translate_c3", "local", now)
    seeds = fetch_translation_seeds(seeds_limit)
    if not seeds:
        raise RuntimeError("E2 台账无 D/B 过审假说可翻（先跑 hypothesis_precheck）")
    panel = fetch_panel(universe_n, days)
    ops = build_eval_ops(panel["date_codes"], panel["symbol_codes"])

    wl = load_whitelist()
    op_names = [op for grp in wl["approved"].values() for op in grp]
    op_names = [op["op"] if isinstance(op, dict) else op for op in op_names]

    chat = OllamaChat(model=model, timeout_s=300.0)
    batch_id = now.strftime("E3T-%Y%m%d-%H%M%S")
    done = load_translated_ids()
    manifest_rows: list[dict] = []
    exam_files: list[str] = []
    # 表达式级去重：同一公式只出一张考卷（不同环节假说常坍缩为同式）
    translated_exprs: set[str] = set()
    if _MANIFEST_CSV.exists():
        try:
            tr = pd.read_csv(_MANIFEST_CSV, encoding="utf-8-sig")
            translated_exprs = set(tr[tr["translatable"] == True]["expression"]  # noqa: E712
                                   .dropna().astype(str))
        except Exception:  # noqa: BLE001
            translated_exprs = set()
    for seed in seeds:
        cid = seed["candidate_id"]
        if cid in done:
            continue
        prompt = build_translation_prompt(seed["hypothesis_zh"], list(FEATURES),
                                          op_names)
        tr: dict | None = None
        expr = ""
        ok, why = False, ""
        try:
            raw = chat.ask(prompt, temperature=0.2)
        except Exception as exc:  # noqa: BLE001 — LSG/连接失败记阴性继续
            manifest_rows.append(_negative(seed, model, f"llm_error:{type(exc).__name__}"))
            continue
        tr = parse_translation(raw)
        if tr.get("translatable"):
            expr = str(tr.get("expression", "")).strip()
            ok, why = validate_expr(expr, list(FEATURES), set(op_names))
            if not ok:
                # 纠错重试一次（把 DSL 校验错误喂回去）
                retry = (prompt + "\n\n上一次输出未通过 DSL 校验：" + why +
                         "\n修正后重新输出单个 JSON 对象。")
                try:
                    tr = parse_translation(chat.ask(retry, temperature=0.2))
                    if tr.get("translatable"):
                        expr = str(tr.get("expression", "")).strip()
                        ok, why = validate_expr(expr, list(FEATURES), set(op_names))
                except Exception as exc:  # noqa: BLE001
                    manifest_rows.append(_negative(
                        seed, model, f"llm_error:{type(exc).__name__}"))
                    continue
        if not tr.get("translatable"):
            manifest_rows.append(_negative(seed, model,
                                           tr.get("refusal_reason", "model_refusal")))
            continue
        if not ok:
            manifest_rows.append(_negative(seed, model, f"dsl_{why[:40]}"))
            continue
        if expr in translated_exprs:
            manifest_rows.append(_negative(seed, model, "dup_expression"))
            continue
        translated_exprs.add(expr)
        try:
            vals = evaluate_expr(expr, list(FEATURES), ops, panel["X"])
            if not np.isfinite(vals).any() or float(np.nanstd(vals)) == 0:
                manifest_rows.append(_negative(seed, model, "degenerate_constant"))
                continue
        except Exception as exc:  # noqa: BLE001 — 求值异常记阴性
            manifest_rows.append(_negative(seed, model, f"eval_{type(exc).__name__}"))
            continue
        if dry_run:
            manifest_rows.append(_positive_dry(seed, tr, expr, model, top_n))
            continue
        exam = generate_strategy_file(expr, src_cand=cid, top_n=int(tr.get("top_n") or top_n))
        exam_files.append(str(exam))
        manifest_rows.append({
            "candidate_id": cid, "birth_channel": seed["birth_channel"],
            "hypothesis_zh": seed["hypothesis_zh"], "expression": expr,
            "mechanism": str(tr.get("mechanism", ""))[:200], "top_n": tr.get("top_n") or top_n,
            "translatable": True, "refusal_reason": "", "model": model,
            "exam_file": str(exam.relative_to(_ROOT)),
            "translated_at": now.isoformat(timespec="seconds"),
        })
    record = {
        "batch": batch_id, "gate": gate, "model": model, "seeds": len(seeds),
        "translated": sum(1 for r in manifest_rows if r.get("translatable")),
        "negative": sum(1 for r in manifest_rows if not r.get("translatable")),
        "rows": manifest_rows,
    }
    if not dry_run and manifest_rows:
        df = pd.DataFrame(manifest_rows)
        for c in MANIFEST_COLS:
            if c not in df.columns:
                df[c] = ""
        df = df[[c for c in MANIFEST_COLS if c in df.columns]]
        df.to_csv(_MANIFEST_CSV, mode="a", header=not _MANIFEST_CSV.exists(),
                  index=False, encoding="utf-8-sig")
        record["written_to"] = str(_MANIFEST_CSV.relative_to(_ROOT))
        record["exam_files"] = exam_files
    return record


def _negative(seed: dict, model: str, reason: str) -> dict:
    return {"candidate_id": seed["candidate_id"],
            "birth_channel": seed.get("birth_channel", ""),
            "hypothesis_zh": seed.get("hypothesis_zh", ""), "expression": "",
            "mechanism": "", "top_n": "", "translatable": False,
            "refusal_reason": reason[:120], "model": model, "exam_file": "",
            "translated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(
                timespec="seconds")}


def _positive_dry(seed: dict, tr: dict, expr: str, model: str, top_n: int) -> dict:
    return {"candidate_id": seed["candidate_id"],
            "birth_channel": seed.get("birth_channel", ""),
            "hypothesis_zh": seed.get("hypothesis_zh", ""), "expression": expr,
            "mechanism": str(tr.get("mechanism", ""))[:200],
            "top_n": tr.get("top_n") or top_n, "translatable": True,
            "refusal_reason": "", "model": model, "exam_file": "(dry-run)",
            "translated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(
                timespec="seconds")}


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E3 假说轨 C3 翻译 MVP（公式化子集，经 LSG）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("translate", help="翻译 E2 过审假说（公式化子集）")
    m.add_argument("--model", default=MODEL_DEFAULT)
    m.add_argument("--seeds", type=int, default=5)
    m.add_argument("--universe-n", type=int, default=40)
    m.add_argument("--days", type=int, default=250)
    m.add_argument("--top-n", type=int, default=15)
    m.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    try:
        record = run_translate(args.model, args.seeds, args.universe_n,
                               args.days, args.top_n, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
