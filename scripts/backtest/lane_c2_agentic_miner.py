# [BLUEPRINT] MOD-BT-158 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.lane_c2_agentic_miner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.integration.local_model.ollama_chat; scripts.backtest.lane_c_formula_miner; scripts.backtest.compute_window_gate; schemas.categories.backtest_hypothesis_precheck
# [CONSUMERS] 策略生产全景图 FAC-E1C 车道C 二轨（LLM 智能体挖矿，立项书 P1）；FAC-E2 预审（下游）；
#   data/strategy_intake/lane_c2_candidates.csv（进货台账）；P2 赛马（与 gplearn 轨同卷）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] DSL 只准白名单算子+已知特征（AST 校验 fail-closed）；求值=日期主序面板契约；
#   验收=增量 IC>阈值 且 AST 相似度对既有池 <阈值（原创性，AlphaAgent 公式6 思路）；
#   种子=E2 已过审假说反哺（闭环）；出生证机器写入；运动员不兼裁判——incr_ic 是描述性
#   证据，判定权在 E2/E4；LLM 调用必经 OllamaChat（内置 LSG）；台账只追加
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(白名单/面板/种子缺失); SystemExit(2)(参数错)
# [TESTS] tests/backtest/test_lane_c2_agentic_miner.py
# [A_module] module_id=MOD-BT-158 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 挖矿器非常驻服务：由进货编排/夜批事件调用，无常驻循环
"""FAC-E1C 车道C 二轨——LLM 智能体挖矿 MVP（立项书 P1，AlphaAgent 方法借监不引码）。

流程：E0 问闸（local 轻档）→ 白名单加载 → 面板（复用 MOD-BT-155 fetch_panel，日期主序
完整面板契约）→ 种子=E2 台账已过审假说（反哺闭环）→ OllamaChat 按种子产 DSL 表达式
（三正则写进生成 prompt：对齐三段自述/原创声明/长度上限）→ DSL AST 校验（白名单算子+
已知特征，fail-closed）→ 面板求值 → 增量 IC 验收 + AST 原创性门（vs gplearn 存货与已收
候选）→ 出生证卸 data/strategy_intake/lane_c2_candidates.csv → E2 预审消费。
P2 赛马计分板见 factory_intake_pipeline race 子命令（同一考试自动可比）。

用法:
  python scripts/backtest/lane_c2_agentic_miner.py mine --seeds 3 --per-seed 2 --dry-run
  python scripts/backtest/lane_c2_agentic_miner.py mine --model deepseek-r1:8b  # 消融档
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))  # scripts.* 命名空间导入（CLI 直跑场景）
_INTAKE_CSV = _ROOT / "data" / "strategy_intake" / "lane_c2_candidates.csv"

BIRTH_CHANNEL = "C2"
MODEL_DEFAULT = "qwen3:8b"
MODEL_ABLATION = "deepseek-r1:8b"
ORIGINALITY_MAX_SIM = 0.8   # AST 节点多重集 Jaccard 对既有池最大相似度上限
MIN_INCR_IC = 0.0           # 增量 IC 验收线（描述性证据，终审在 E2/E4）
MAX_NODES = 14              # 单表达式 AST 节点上限（简洁性）
SQL_PASSED_SEEDS = (
    "SELECT candidate_id, hypothesis_zh FROM {table} "
    "WHERE verdict = 'precheck_passed' ORDER BY prechecked_at DESC LIMIT {limit}"
)


def build_eval_ops(date_codes: np.ndarray, symbol_codes: np.ndarray) -> dict:
    """白名单算子求值表（groupby 分组语义，与 MOD-BT-155 自定义算子同源）。"""
    from scripts.backtest.lane_c_formula_miner import CUSTOM_OPS, make_panel_operators

    customs = {f.name: f for f in make_panel_operators(
        date_codes, symbol_codes, list(CUSTOM_OPS))}

    def _div(a, b):
        return np.asarray(a, float) / np.where(np.abs(np.asarray(b, float)) < 1e-12, 1e-12, b)

    def _sqrt(a):
        return np.sign(a) * np.sqrt(np.abs(a))

    def _log(a):
        return np.log(np.abs(a) + 1e-12)

    return {
        "add": lambda a, b: np.asarray(a, float) + np.asarray(b, float),
        "sub": lambda a, b: np.asarray(a, float) - np.asarray(b, float),
        "mul": lambda a, b: np.asarray(a, float) * np.asarray(b, float),
        "div": _div, "sqrt": _sqrt, "log": _log,
        "abs": lambda a: np.abs(a), "neg": lambda a: -np.asarray(a, float),
        "max": lambda a, b: np.maximum(a, b), "min": lambda a, b: np.minimum(a, b),
        **customs,
    }


OP_ARITY = {"add": 2, "sub": 2, "mul": 2, "div": 2, "max": 2, "min": 2,
            "sqrt": 1, "log": 1, "abs": 1, "neg": 1,
            "rank_cs": 1, "ts_delta_5": 1, "ts_zscore_20": 1, "ts_corr_20": 2}


def validate_expr(expr: str, features: list[str], op_names: set[str]) -> tuple[bool, str]:
    """DSL AST 校验（fail-closed）：只准 Call(白名单算子+参数个数正确)/Name(已知特征)/数值。"""
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as exc:
        return False, f"syntax: {exc}"

    def _walk(node: ast.AST) -> tuple[bool, str]:
        if isinstance(node, ast.Expression):
            return _walk(node.body)
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                return False, f"非常量类型: {type(node.value).__name__}"
            return True, ""
        if isinstance(node, ast.Name):
            if node.id not in features:
                return False, f"未知特征: {node.id}"
            return True, ""
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in op_names:
                return False, f"非白名单算子: {getattr(node.func, 'id', '?')}"
            arity = OP_ARITY.get(node.func.id)
            if arity is not None and len(node.args) != arity:
                return False, f"{node.func.id} 参数数 {len(node.args)}!={arity}"
            for arg in node.args:
                ok, why = _walk(arg)
                if not ok:
                    return False, why
            return True, ""
        return False, f"非法节点: {type(node).__name__}"

    return _walk(tree)


def evaluate_expr(expr: str, features: list[str], ops: dict, panel_x: np.ndarray) -> np.ndarray:
    """DSL 求值（列语义：每个特征=面板一列）。"""
    tree = ast.parse(expr.strip(), mode="eval")
    col = {f: panel_x[:, i] for i, f in enumerate(features)}

    def _ev(node: ast.AST) -> np.ndarray:
        if isinstance(node, ast.Constant):
            return np.full(len(panel_x), float(node.value))
        if isinstance(node, ast.Name):
            return col[node.id]
        if isinstance(node, ast.Call):
            args = [_ev(a) for a in node.args]
            return np.asarray(ops[node.func.id](*args), dtype=float)
        raise ValueError(f"非法节点 {type(node).__name__}")

    return _ev(tree.body)


def ast_nodes(expr: str, features: list[str]) -> Counter:
    """归一化 AST 节点多重集（特征名→V，常数→C）：结构相似度基底。"""

    def _norm(node: ast.AST) -> str:
        if isinstance(node, ast.Constant):
            return "C"
        if isinstance(node, ast.Name):
            return "V" if node.id in features else node.id
        if isinstance(node, ast.Call):
            return f"call:{node.func.id}"
        return type(node).__name__

    tree = ast.parse(expr.strip(), mode="eval")
    c: Counter = Counter()
    for node in ast.walk(tree):
        c[_norm(node)] += 1
    return c


def ast_similarity(expr_a: str, expr_b: str, features: list[str]) -> float:
    """结构相似度=归一化节点多重集 Jaccard（AlphaAgent 公式6 的轻量等价，v1 口径）。"""
    ca, cb = ast_nodes(expr_a, features), ast_nodes(expr_b, features)
    if not ca or not cb:
        return 0.0
    inter = sum((ca & cb).values())
    union = sum((ca | cb).values())
    return inter / union if union else 0.0


def originality_max(expr: str, pool: list[str], features: list[str]) -> float:
    """对既有公式池的最大结构相似度（空池=0=全原创）。"""
    return max((ast_similarity(expr, p, features) for p in pool), default=0.0)


def build_generation_prompt(hypothesis: str, features: list[str], op_names: list[str],
                            existing: list[str], k: int) -> str:
    """确定性生成 prompt v2（三正则事前约束 + 交易对手三问逼问，治机制自述套话）。

    v2 升级（E2 三杀根因=机制自述套话）：mechanism 必须回答交易对手三问——
    ①谁在卖给你 ②他们为什么愿意亏 ③什么成本/摩擦可能吃掉边际；
    答不出具体对手（如只说"利用风险溢价"）=机制不清晰，预审必拒。
    """
    return (
        f"市场假设：{hypothesis}\n\n"
        f"生成 {k} 条量化因子表达式，规则：\n"
        f"1 只准用这些算子（嵌套函数调用形式）：{', '.join(op_names)}\n"
        f"2 只准用这些输入变量：{', '.join(features)}\n"
        f"3 每条必须附 description（它在算什么）与 mechanism。mechanism 必须回答"
        f"交易对手三问：①谁在卖给你/谁在亏（具体到行为：追涨杀跌？被迫平仓？流动性"
        f" withdrawal？）②他们为什么愿意亏（哪种行为偏差或约束，说人话）③什么成本或"
        f"摩擦可能吃掉你的边际。禁止空话（如只写'利用风险溢价''统计显著'=机制不清晰，"
        f"必被拒）；\n"
        f"4 简洁：整个表达式不超过 {MAX_NODES} 个节点，禁无用嵌套\n"
        f"5 原创禁重复，以下既有公式禁止同义变形：{'; '.join(existing[:5]) or '（空）'}\n\n"
        "输出 JSON 数组恰好 " + str(k) + " 条："
        '[{"expression": "op(x, y)", "description": "...", "mechanism": '
        '"①对手=...②为何亏=...③成本=..."}]'
    )


def parse_candidates(raw: str) -> list[dict]:
    """LLM 回复→候选列表（JSON 数组优先，逐对象兜底；字段不全丢弃）。"""
    import re

    text = (raw or "").strip()
    items: list[dict] = []
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if m:
        try:
            arr = json.loads(m.group(0))
            items = [x for x in arr if isinstance(x, dict) and x.get("expression")]
        except json.JSONDecodeError:
            items = []
    if not items:
        for m2 in re.finditer(r"\{[^{}]*\}", text, re.DOTALL):
            try:
                x = json.loads(m2.group(0))
                if isinstance(x, dict) and x.get("expression"):
                    items.append(x)
            except json.JSONDecodeError:
                continue
    return items


def make_candidate_id(expr: str) -> str:
    digest = hashlib.md5(f"E1C2:{expr.strip()}".encode("utf-8")).hexdigest()[:12]
    return f"CAND-{digest}"


def attach_birth_certificate(rows: list[dict], batch_id: str, model: str,
                             wl_sha: str, seeds: int) -> list[dict]:
    out = []
    for r in rows:
        row = dict(r)
        row["birth_channel"] = BIRTH_CHANNEL
        row["birth_batch"] = batch_id
        row["birth_source"] = (f"agentic-llm:{model} seeds=E2passed:{seeds} "
                               f"wl={wl_sha} regularized=AST+align+complexity")
        out.append(row)
    return out


def load_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        return set(pd.read_csv(path, encoding="utf-8-sig")["candidate_id"].astype(str))
    except Exception:  # noqa: BLE001 — 台账损坏不阻断
        return set()


def fetch_passed_seeds(limit: int) -> list[str]:
    """E2 台账已过审假说（种子反哺闭环；不可达返回空→上层报缺）。"""
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
        SQL_PASSED_SEEDS.format(table=f"{DATABASE}.{TABLE_NAME}", limit=int(limit)))
    return [r[1] for r in rows]


def run_agentic_mine(model: str, seeds_limit: int, per_seed: int, universe_n: int,
                     days: int, top: int, dry_run: bool = False) -> dict:
    """主流程：问闸→白名单→面板→种子→LLM 产 DSL→三道验收→卸货。"""
    from scripts.backtest.compute_window_gate import check_gate
    from scripts.backtest.lane_c_formula_miner import (
        fetch_panel,
        load_whitelist,
        make_incremental_ic_fitness,
    )
    from zephyr.integration.local_model.ollama_chat import OllamaChat

    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    gate = check_gate("lane_c2_agentic_mine", "local", now)

    whitelist = load_whitelist()
    cons = whitelist["constraints"]
    op_names = [op for group in whitelist["approved"].values() for op in group]
    op_names = [op["op"] if isinstance(op, dict) else op for op in op_names]

    seeds = fetch_passed_seeds(seeds_limit)
    if not seeds:
        raise RuntimeError("E2 台账无已过审假说可作种子（先跑 hypothesis_precheck）")
    panel = fetch_panel(universe_n, days)
    features = panel["features"]
    ops = build_eval_ops(panel["date_codes"], panel["symbol_codes"])
    op_set = set(ops)
    fitness = make_incremental_ic_fitness(panel["baseline"], panel["y"])
    existing = load_existing_ids(_INTAKE_CSV)
    pool_exprs: list[str] = []
    pool_path = _ROOT / "data" / "strategy_intake" / "lane_c_candidates.csv"
    if pool_path.exists():
        pool_exprs = pd.read_csv(pool_path, encoding="utf-8-sig")["formula"].dropna().tolist()

    chat = OllamaChat(model=model, timeout_s=300.0)  # 容纳冷启动模型加载（>60s 默认超时）
    batch_id = now.strftime("E1C2-%Y%m%d-%H%M%S")
    rows: list[dict] = []
    rejected = Counter()
    rejected_samples: dict[str, list[str]] = {}

    def _rej(reason: str, expr: str) -> None:
        rejected[reason] += 1
        rejected_samples.setdefault(reason, [])
        if len(rejected_samples[reason]) < 3:
            rejected_samples[reason].append(expr[:120])

    for h in seeds:
        prompt = build_generation_prompt(h, features, sorted(op_set), pool_exprs, per_seed)
        try:
            raw = chat.ask(prompt, temperature=0.3)
        except Exception as exc:  # noqa: BLE001 — LSG/连接类失败记因继续
            _rej(f"llm_error:{type(exc).__name__}", str(exc)[:120])
            continue
        for cand in parse_candidates(raw):
            expr = str(cand["expression"]).strip()
            ok, why = validate_expr(expr, features, op_set)
            if not ok:
                _rej(f"dsl_{why[:24]}", expr)
                continue
            try:
                vals = evaluate_expr(expr, features, ops, panel["X"])
            except Exception as exc:  # noqa: BLE001 — 求值异常按形状类拒绝
                _rej(f"eval_{type(exc).__name__}", expr)
                continue
            if not np.isfinite(vals).any() or float(np.nanstd(vals)) == 0:
                _rej("degenerate_constant", expr)
                continue
            sim = originality_max(expr, pool_exprs, features)
            if sim >= ORIGINALITY_MAX_SIM:
                _rej("originality_duplicate", expr)
                continue
            ic = float(fitness(panel["y"], vals, np.ones(panel["n"])))
            if ic <= MIN_INCR_IC:
                _rej("incr_ic_nonpositive", f"{expr} (ic={ic:.4f})")
                continue
            cid = make_candidate_id(expr)
            if cid in existing:
                _rej("dup_known", expr)
                continue
            existing.add(cid)
            pool_exprs.append(expr)
            hypothesis = str(cand.get("description") or h)
            rows.append({
                "candidate_id": cid, "seed_hypothesis": h, "expression": expr,
                "incr_ic": round(ic, 6), "ast_sim_max": round(sim, 4),
                "hypothesis_zh": (
                    f"做多[公式因子]：{expr}——市场假设：{hypothesis}；机制自述："
                    f"{cand.get('mechanism', '')}；在 REG-IND-001 基座上增量 rank IC={ic:.4f}"
                    f"（AST 原创性 {sim:.2f}<{ORIGINALITY_MAX_SIM}）。"
                    "机制自述要求：复核上述机制是否成立，讲不通即 reject。"),
            })
    rows = sorted(rows, key=lambda r: -r["incr_ic"])[:top]
    wl_sha = hashlib.md5(json.dumps(whitelist, sort_keys=True, ensure_ascii=False,
                                    default=str).encode("utf-8")).hexdigest()[:12]
    rows = attach_birth_certificate(rows, batch_id, model, wl_sha, len(seeds))
    record = {
        "batch": batch_id, "gate": gate, "model": model,
        "seeds": len(seeds), "mined": len(rows), "rejected": dict(rejected),
        "rejected_samples": rejected_samples,
        "items": [{k: r[k] for k in ("candidate_id", "incr_ic", "ast_sim_max",
                                     "expression")} for r in rows],
    }
    if not dry_run and rows:
        cols = ["candidate_id", "seed_hypothesis", "expression", "incr_ic", "ast_sim_max",
                "hypothesis_zh", "birth_channel", "birth_batch", "birth_source"]
        header = not _INTAKE_CSV.exists()
        _INTAKE_CSV.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows)[cols].to_csv(_INTAKE_CSV, mode="a", header=header,
                                        index=False, encoding="utf-8-sig")
        record["written_to"] = str(_INTAKE_CSV.relative_to(_ROOT))
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E1C 二轨：LLM 智能体挖矿（经 LSG，零 API 成本）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mine", help="按 E2 过审种子挖一轮表达式")
    m.add_argument("--model", default=MODEL_DEFAULT)
    m.add_argument("--seeds", type=int, default=3, help="取 E2 过审假说前 N 条作种子")
    m.add_argument("--per-seed", type=int, default=2, help="每种子生成条数")
    m.add_argument("--universe-n", type=int, default=100)
    m.add_argument("--days", type=int, default=250)
    m.add_argument("--top", type=int, default=10)
    m.add_argument("--dry-run", action="store_true", help="只回看不写台账")
    args = ap.parse_args()
    try:
        record = run_agentic_mine(args.model, args.seeds, args.per_seed,
                                  args.universe_n, args.days, args.top, args.dry_run)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
