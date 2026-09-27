# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_matrix/t0_conditional_v2_prereg_card.md | §2 双门×价轴网格（周五 GPU 矩阵输入包）
# [MODULE] t0_gpu_condition_pack（scripts 输入包生成件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] docs/_working/t0_matrix/six_phase_history_v1.csv（六段相位真源）；market_emotion_index(逻辑品类)（温度计+六成分，只读）；backtest_regime_state_anchored(逻辑品类)（vol_pct/dominant，只读）；c1_market.kline_index 000300（价轴振幅，只读）；scripts/backtest/auto_mount.py 无依赖（相位已在物化件里定形）
# [CONSUMERS] 周五 GPU 矩阵开跑前输入包验收（w3_w5_precheck §2.4·甲/§二·五同口径）；scripts/backtest/factory_grid_executor.py 侧条件维分层键（本包为 T0 条件维输入，非 run 产物）；Owner 复查窗
# [STARTUP] manual（python scripts/audit/t0_gpu_condition_pack.py）
# [MATURITY] production（GPU 点火前输入包，判据引用不自定）
# [DEPENDENCIES_NOTE] 档界来源全部为既有 frozen 件：vol_bucket3=(0.328,0.700) 承 t0_regime 卡 §3 IS 期分位；band5 边界承 emotion_index_skeleton_v0.md §展示层五档（已提交）；band3 承 sector_state_aggregator；唯 amp_bucket3（振幅三桶）为本包新轴，其边界只准用闭卷切点(2025-09-09)以前的数据算分位并写死入 meta，禁全窗反算
# [INVARIANTS] 只读查库零状态变更（DatabaseService reader + TableRegistry 真源表名，禁裸 duckdb/禁散落 SQL 字面量）；产物必为 .csv+.meta.yaml 双件（本包区禁依赖 .json；禁写 summary.json——会被 n_trial_ledger 自动计入 DSR 分母=科学污染）；negatives.csv 必须带表头（零阴性也不许空文件，下游 pd.read_csv 会得单匿名列）；closed_book_ok=0 行只可作卷外观察；条件胞 <30 交易日 usable_as_dimension=0；档界与判据一律引用既有 frozen 件，本包不自定阈值
# [MODIFY-GUARD] 改动=GPU 搜索空间输入变更，须同步 config/search_space_prereg.yaml 预注册（改空间=作废重开）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一轴真源缺失/零行=显式报错（fail-closed，禁静默降级成少一轴）；六段真源含重复日=显式报错
# [TESTS] tests/audit/test_t0_gpu_condition_pack.py（档界引用性/闭卷标记/阴性带表头/胞地板判定）
# [TTL] task_bound
"""t0_gpu_condition_pack.py — 做T 条件维度 GPU 矩阵输入包（六段双门 × 价轴，预注册闭卷口径）

格式仿 docs/_working/emotion_line/gpu_emotion_condition_matrix_v1（emoreplay 班情绪包）：
逐日矩阵 .csv + .meta.yaml（provenance/闭卷/纪律），外加 negatives.csv（不达地板胞如实入册）。
落位 data/strategy_intake/grid_t0_conditional_v1/。

用法：python scripts/audit/t0_gpu_condition_pack.py [--out-dir data/strategy_intake/grid_t0_conditional_v1]
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backtest"))

REPO = Path(__file__).resolve().parents[2]
SIX_PHASE_TRUTH = REPO / "docs/_working/t0_matrix/six_phase_history_v1.csv"

CLOSED_BOOK_START = "2019-01-04"  # 闭卷窗起点=universe 诚实下限（真源 docs/_working/e2e_integration/w3_w5_precheck_20260923.md，已提交）
CLOSED_BOOK_CUTOFF = "2025-09-09"  # 切点后禁参与阈值选择/调参/定档（同上已提交真源 §闭卷纪律）
AMP_DERIV_END = CLOSED_BOOK_CUTOFF  # 振幅档界唯一允许的推导窗终点

VOL_B3 = (0.328, 0.700)  # 引用：t0_regime 卡 §3 IS 期 vol_pct 33.33/66.67 分位（frozen，非本包自定）
EMOTION_B5_EDGES = (
    0.2,
    0.4,
    0.6,
    0.8,
)  # 引用：docs/_working/emotion_line/emotion_index_skeleton_v0.md:60（已提交，"仅展示层约定非门禁"）
EMOTION_B5_LABELS = (
    "ice",
    "cooling",
    "mild",
    "warming",
    "boiling",
)  # 引用：同上五档中文序（冰点/降温/温和/升温/沸点）英写；在途消费件 condition_package._BAND_LABELS 同值
EMOTION_B3_EDGES = (0.40, 0.70)  # 引用：sector_state_aggregator 消费口径 low/mid/high
EMOTION_GATE_ALLOW = ("ignition", "expansion", "euphoria")  # 引用：T0-CONDITIONAL §2.2 frozen 允许集
MACRO_VOL_H = 0.700  # 引用：卡 §2.1 frozen
MACRO_TREND_STATES = ("r3", "r12")  # 引用：卡 §2.1 frozen
CELL_DAY_FLOOR = 30  # 条件胞样本地板（承 emoreplay 包同口径）
PRICE_SYMBOL = "000300"  # 价轴载体：沪深300 指数日线（振幅=做T 毛边际的物理来源）

# 两表均 ReplacingMergeTree（实测 system.tables；emotion_index 现存 17 个未合并重复键）。
# 不带 FINAL 会把同一逻辑键的多个物理版本都读回来，dict 后写覆盖先写=版本选取随物理序漂移，
# 故一律 GROUP BY 取 argMax(…, ingest_ts)：显式"取最新一版"，与合并进度无关。
_SQL_EMOTION = (
    "SELECT trade_date, argMax(emotion_index, ingest_ts), argMax(components, ingest_ts), "
    "argMax(source, ingest_ts), argMax(version, ingest_ts) FROM {table} "
    "WHERE stage = 'close_final' GROUP BY trade_date ORDER BY trade_date"
)
_SQL_STATE = (
    "SELECT trade_date, argMax(dominant, ingest_ts), argMax(vol_pct, ingest_ts) "
    "FROM {table} GROUP BY trade_date ORDER BY trade_date"
)
_SQL_INDEX_K = (
    "SELECT trade_date, toString(any(open)), toString(any(high)), toString(any(low)) "
    "FROM {table} WHERE symbol = '{sym}' GROUP BY trade_date ORDER BY trade_date"
)


def _conn():
    from zephyr.infrastructure.database_service import DatabaseService

    return DatabaseService().get_clickhouse_conn()


def _reg():
    from zephyr.data.table_registry import get_registry

    return get_registry()


def closed_book_flag(day: str) -> int:
    """闭卷窗 = [CLOSED_BOOK_START, CLOSED_BOOK_CUTOFF] 两端含。

    下界守卫=红蓝⑤补：切点前但早于闭卷窗起点的日不得标 1（实测当前包零行受影响=零值变更，
    守卫是为真源往前续史时不静默扩窗）。
    """
    return int(CLOSED_BOOK_START <= day <= CLOSED_BOOK_CUTOFF)


def band5(v):
    for edge, label in zip(EMOTION_B5_EDGES, EMOTION_B5_LABELS, strict=False):
        if v <= edge:
            return label
    return EMOTION_B5_LABELS[-1]


def band3(v):
    lo, hi = EMOTION_B3_EDGES
    return "low" if v < lo else ("mid" if v < hi else "high")


def vol_bucket(v):
    if v is None:
        return ""
    lo, hi = VOL_B3
    return "L" if v <= lo else ("M" if v <= hi else "H")


def amp_bucket(v, edges):
    if v is None or not edges:
        return ""
    lo, hi = edges
    return "A1" if v <= lo else ("A2" if v <= hi else "A3")  # A1 窄幅/A2 中幅/A3 宽幅


def load_six_phase(path: Path) -> dict[str, dict]:
    if not path.exists():
        raise SystemExit(f"FAIL: 六段真源缺失 {path}——先跑 t0_six_phase_materialize.py")
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            d = r["trade_date"]
            if d in out:
                raise SystemExit(f"FAIL: 六段真源含重复日 {d}")
            out[d] = r
    if not out:
        raise SystemExit(f"FAIL: 六段真源为空 {path}")
    return out


def load_emotion(conn, table: str) -> dict[str, dict]:
    rows = conn.execute(_SQL_EMOTION.format(table=table))
    out: dict[str, dict] = {}
    for td, val, comps, source, version in rows:
        d = str(td)
        ok_n = 0
        try:
            parsed = yaml.safe_load(comps) if isinstance(comps, str) else (comps or [])
            ok_n = sum(1 for c in parsed if isinstance(c, dict) and c.get("status") == "ok")
        except Exception:  # noqa: BLE001  components 解析失败按 0 成分如实登记，禁猜
            ok_n = 0
        out[d] = {"emotion_index": float(val), "ok_n": ok_n, "source": source, "version": version}
    return out


def load_state(conn, table: str) -> dict[str, tuple]:
    out: dict[str, tuple] = {}
    for td, dom, vol in conn.execute(_SQL_STATE.format(table=table)):
        out[str(td)] = (str(dom), float(vol) if vol is not None else None)
    return out


def load_amplitude(conn, table: str, sym: str) -> dict[str, float]:
    import numpy as np

    out: dict[str, float] = {}
    for td, o, h, l in conn.execute(_SQL_INDEX_K.format(table=table, sym=sym)):
        try:
            fo, fh, fl = float(o), float(h), float(l)
        except (TypeError, ValueError):
            continue
        if fo > 0:
            out[str(td)] = float((fh - fl) / fo * 1e4)  # 振幅，单位 bp（与成本 31.2bp/前置 30bp 同量纲可直接比）
    del np
    return out


def derive_amp_edges(amp: dict[str, float]) -> tuple[tuple[float, float], int, str, str]:
    """振幅三桶边界：只用闭卷切点以前的数据算 33.33/66.67 分位（切点后禁参与定档）。

    返回含**实际所用窗首末日**——meta 描述必须报真实来路，不得把 CLOSED_BOOK_START
    当成推导窗下界写进散文（红蓝⑤实测该处描述不实，见台账 D-12）。
    """
    pre = sorted((d, v) for d, v in amp.items() if d <= AMP_DERIV_END)
    if len(pre) < 250:
        raise SystemExit(f"FAIL: 振幅档界推导窗样本 {len(pre)} <250，不足以定三桶（fail-closed）")
    vals = sorted(v for _, v in pre)  # 分位必按**值**序；日期序仅供首末日溯源

    def pct(p):
        i = min(len(vals) - 1, max(0, int(round(p * (len(vals) - 1)))))
        return vals[i]

    return (pct(1 / 3), pct(2 / 3)), len(pre), pre[0][0], pre[-1][0]


def t1_lookup(series: dict, day: str, keys: list[str]) -> object:
    """PIT=T-1 交易日读数（与考试族同构），7 自然日容差外返回 None。"""
    from datetime import date, timedelta

    d = date.fromisoformat(day)
    cands = [k for k in keys if k < day]
    if not cands:
        return None
    prev = max(cands)
    if (d - date.fromisoformat(prev)) > timedelta(days=7):
        return None
    return series.get(prev)


def load_axes():
    """四轴只读装载 + 零行 fail-closed（任一轴缺=显式报错，禁静默降级成少一轴）。"""
    reg, conn = _reg(), _conn()
    six = load_six_phase(SIX_PHASE_TRUTH)
    emo = load_emotion(conn, reg.table("market_emotion_index"))
    state = load_state(conn, reg.table("backtest_regime_state_anchored"))
    amp = load_amplitude(conn, reg.table("market_index_kline"), PRICE_SYMBOL)
    if not emo or not state or not amp:
        raise SystemExit("FAIL: 某轴真源零行（禁静默降级成少一轴）")
    return six, emo, state, amp


def _gate_states(dom, vol, six_prev):
    """两门三态：None=该轴当日不可评（禁把"不知道"编码成"禁做"，红蓝④）。"""
    state_known = bool(dom) or (vol is not None)
    macro = bool((vol is not None and vol > MACRO_VOL_H) or (dom in MACRO_TREND_STATES)) if state_known else None
    routed = bool(six_prev) and six_prev.get("routed", "0") == "1"
    phase = six_prev.get("six_phase", "") if six_prev else ""
    emo = (phase in EMOTION_GATE_ALLOW) if routed else None
    return macro, emo, routed, phase


def row_for_day(d, e, s_prev, six_prev, amp_prev, amp_edges):
    """逐日一行：温度计/灰度档/宏观态/六段相位/价轴 + 两门与闭卷标记（全窗保留，禁为凑窗删行）。"""
    dom, vol = s_prev or (None, None)
    macro, emo, routed, phase = _gate_states(dom, vol, six_prev)

    def blank(v, nd):
        return "" if v is None else round(v, nd)

    return {
        "trade_date": d,
        "emotion_index": round(e["emotion_index"], 6),
        "band5": band5(e["emotion_index"]),
        "band3_emotion": band3(e["emotion_index"]),
        "ok_n": e["ok_n"],
        "emotion_source": e["source"],
        "formula_version": e["version"],
        "t1_dominant": dom or "",
        "t1_vol_pct": blank(vol, 6),
        "t1_vol_bucket3": vol_bucket(vol),
        "t1_six_phase": phase,
        "t1_six_routed": int(routed),
        "t1_amp_bp": blank(amp_prev, 2),
        "t1_amp_bucket3": amp_bucket(amp_prev, amp_edges),
        "macro_gate_allow": "" if macro is None else int(macro),
        "emotion_gate_allow": "" if emo is None else int(emo),
        "dual_gate_allow": int(bool(macro and emo)),
        "closed_book_ok": closed_book_flag(d),
    }


def write_pack(out_dir: Path, rows, cells, negatives, meta):
    """落四件：矩阵 / 条件胞 / 阴性（表头恒写，零阴性也不许空文件）/ meta（禁 .json）。"""
    with (out_dir / "t0_condition_matrix_v1.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with (out_dir / "t0_condition_cells_v1.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cells[0].keys()))
        w.writeheader()
        w.writerows(cells)
    with (out_dir / "negatives.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh, fieldnames=["recipe_id", "death_layer", "death_reason", "values", "degraded_dimensions", "detail"]
        )
        w.writeheader()
        w.writerows(negatives)
    yaml.safe_dump(
        meta,
        (out_dir / "t0_condition_matrix_v1.meta.yaml").open("w", encoding="utf-8"),
        allow_unicode=True,
        sort_keys=False,
    )


def build_cells(rows: list[dict], amp_edges) -> tuple[list[dict], list[dict]]:
    """条件胞=六段相位×振幅桶（卡"双门条件×价轴"的字面网格）。30 日地板判可用。"""
    from collections import Counter

    all_days = Counter()
    cb_days = Counter()
    for r in rows:
        phase = r["t1_six_phase"] or "unrouted"
        ab = r["t1_amp_bucket3"] or "na"
        all_days[(phase, ab)] += 1
        if r["closed_book_ok"] == 1:
            cb_days[(phase, ab)] += 1
    cells = []
    for key in sorted(all_days, key=lambda k: (-cb_days.get(k, 0), k)):
        phase, ab = key
        n_cb = cb_days.get(key, 0)
        cells.append(
            {
                "six_phase": phase,
                "amp_bucket3": ab,
                "trading_days_all": all_days[key],
                "trading_days_closed_book": n_cb,
                "usable_as_dimension": int(n_cb >= CELL_DAY_FLOOR),
            }
        )
    negatives = []
    for c in cells:
        if c["usable_as_dimension"] == 1:
            continue
        negatives.append(
            {
                "recipe_id": f"cell|{c['six_phase']}|{c['amp_bucket3']}",
                "death_layer": "eval",
                "death_reason": "cell_below_sample_floor",
                "values": f"{{'six_phase': '{c['six_phase']}', 'amp_bucket3': '{c['amp_bucket3']}'}}",
                "degraded_dimensions": "six_phase" if c["six_phase"] == "unrouted" else "",
                "detail": f"closed_book_days={c['trading_days_closed_book']} < floor={CELL_DAY_FLOOR}",
            }
        )
    # 轴级阴性：整条相位在闭卷窗内零日 ⇒ 该格在搜索空间恒空，须如实登记禁假装存在
    seen_phases = {c["six_phase"] for c in cells if c["trading_days_closed_book"] > 0}
    for ph in EMOTION_GATE_ALLOW + ("capitulation", "accumulation", "distribution"):
        if ph not in seen_phases:
            negatives.append(
                {
                    "recipe_id": f"axis|six_phase|{ph}",
                    "death_layer": "eval",
                    "death_reason": "phase_zero_days_in_closed_book_window",
                    "values": f"{{'six_phase': '{ph}'}}",
                    "degraded_dimensions": "six_phase",
                    "detail": "闭卷窗内该相位零路由日，按该相位切的搜索维为空层",
                }
            )
    del amp_edges
    return cells, negatives


def _dual_gate_anatomy(cb: list[dict]) -> dict:
    """双门同放行日的**构成归因**（机算，禁手写散文数字——静态清单手工维护必漂移）。"""
    from collections import Counter

    dual = [r for r in cb if r["dual_gate_allow"] == 1]
    hi_vol = [r for r in dual if r["t1_vol_pct"] and float(r["t1_vol_pct"]) > MACRO_VOL_H]
    trend = [r for r in dual if r["t1_dominant"] in MACRO_TREND_STATES]
    both = [r for r in hi_vol if r["t1_dominant"] in MACRO_TREND_STATES]
    vv = sorted(float(r["t1_vol_pct"]) for r in dual if r["t1_vol_pct"])
    routed = [r for r in cb if r["t1_six_routed"] == 1]
    return {
        "days_in_window": len(cb),
        "dual_gate_allow_days": len(dual),
        "share": round(len(dual) / len(cb), 4) if cb else None,
        "macro_branch_split": {
            "via_vol_gt_0p700": len(hi_vol),
            "via_dominant_in_r3_r12": len(trend),
            "via_both": len(both),
            "note": "两支在同源数据上互斥（via_both=0），双门可达性由两支并列贡献，非单支主导",
        },
        "six_phase_within_dual": dict(Counter(r["t1_six_phase"] or "unrouted" for r in dual).most_common()),
        "t1_vol_pct_within_dual": (
            {"min": round(vv[0], 3), "median": round(vv[len(vv) // 2], 3), "max": round(vv[-1], 3)} if vv else {}
        ),
        "cross_tab_dominant_x_six": {
            f"{a}|{b}": n
            for (a, b), n in Counter(
                (r["t1_dominant"] or "na", r["t1_six_phase"] or "unrouted") for r in routed
            ).most_common(10)
        },
    }


def _table_names() -> dict:
    """meta 文案里的表名一律由 TableRegistry/auto_mount 真源解析得出，禁手抄字面量
    （TABLE-NAME-REGISTRY #ARCH-CH-024：硬编码即视为绕过真源，文档字符串也不例外）。"""
    import auto_mount as am

    reg = _reg()
    return {
        "emotion": reg.table("market_emotion_index"),
        "state": reg.table("backtest_regime_state_anchored"),
        "index_k": reg.table("market_index_kline"),
        "snapshot": am.SNAPSHOT_TABLE,  # 该品类未注册（auto_mount 内硬编码自记欠账），故取其常量
    }


def build_meta(rows, cells, negatives, amp_edges, amp_deriv_n, out_dir: Path, deriv_window: tuple[str, str]) -> dict:
    tn = _table_names()
    from collections import Counter

    from zephyr.shared.utils.time_utils import now_utc

    cb = [r for r in rows if r["closed_book_ok"] == 1]
    return {
        "generated": now_utc().isoformat(timespec="seconds"),
        "sid": "st-t0-matrix-20260924",
        "pack_version": "grid_t0_conditional_v1",
        "rows": len(rows),
        "date_span": [rows[0]["trade_date"], rows[-1]["trade_date"]],
        "axes": {
            "condition_gate": ["t1_six_phase", "macro_gate_allow", "emotion_gate_allow", "dual_gate_allow"],
            "price_axis": ["t1_amp_bp", "t1_amp_bucket3"],
            "thermometer": ["emotion_index", "band5", "band3_emotion", "ok_n"],
            "macro": ["t1_dominant", "t1_vol_pct", "t1_vol_bucket3"],
        },
        "truth_sources": {
            "six_phase": "docs/_working/t0_matrix/six_phase_history_v1.csv（映射真源=scripts/backtest/auto_mount.py R2SIX+phase_overlay+resolve_six_phase，零自定阈值）",
            "emotion_thermometer": f"{tn['emotion']}（stage=close_final；同键多版取 argMax(ingest_ts)）",
            "macro_state": tn["state"],
            "price_axis": f"{tn['index_k']} symbol={PRICE_SYMBOL}（GROUP BY trade_date 去重，振幅=(high-low)/open）",
        },
        "band_definitions": {
            "band5": "引用 docs/_working/emotion_line/emotion_index_skeleton_v0.md:60 展示层五档（≤0.2 冰点/≤0.4 降温/≤0.6 温和/≤0.8 升温/>0.8 沸点，该文档自记'仅展示层约定非门禁'）；英写标签与在途消费件 condition_package._BAND_LABELS 同值",
            "band3_emotion": "引用 sector_state_aggregator 消费口径 low<0.40≤mid<0.70≤high",
            "t1_vol_bucket3": f"引用 t0_regime 卡 §3 frozen 边界 {VOL_B3}（L≤0.328<M≤0.700<H）",
            "t1_amp_bucket3": f"本包新轴，三桶边界={([round(x, 2) for x in amp_edges])} bp，"
            f"由 {deriv_window[0]}..{deriv_window[1]}（{amp_deriv_n} 日：切点前全量可用史，"
            f"早于闭卷窗起点 {CLOSED_BOOK_START} 的历史亦参与定档）振幅的 33.33/66.67 分位定，"
            "切点后数据未参与定档",
        },
        "gpu_budget": {
            "device": "RTX 3090 24GB",
            "window_hours": 59,
            "pack_rows": len(rows),
            "pack_bytes_on_disk": sum(p.stat().st_size for p in out_dir.glob("*") if p.is_file()),
            "vram_note": "输入包为逐日单表（数千行×16 列），显存零压力；每配置查表按 trade_date 索引 O(1)，"
            "预算瓶颈在回测前向次数不在此包",
            "closed_book": {
                "start": CLOSED_BOOK_START,
                "cutoff": CLOSED_BOOK_CUTOFF,
                "rule": "trade_date>cutoff 的行 closed_book_ok=0，只可作卷外观察，禁校正/调参/定档",
                "rows_in_search_window": len(cb),
                "dual_gate_allow_days_in_window": sum(1 for r in cb if r["dual_gate_allow"] == 1),
                "emotion_gate_unrouted_days_in_window": sum(1 for r in cb if r["emotion_gate_allow"] == ""),
                "macro_gate_unevaluable_days_in_window": sum(1 for r in cb if r["macro_gate_allow"] == ""),
                "tri_state_note": "两张门列均可为空串=该轴当日不可评（跨长假 T-1 缺读、宏观态不路由）；"
                "空串既不计允许也不计禁做，双门列在任一轴不可评时恒 0",
                "six_phase_distribution_in_window": dict(
                    Counter((r["t1_six_phase"] or "unrouted") for r in cb).most_common()
                ),
                "amp_bucket_distribution_in_window": dict(
                    Counter((r["t1_amp_bucket3"] or "na") for r in cb).most_common()
                ),
            },
            "condition_cells": {
                "definition": "t1_six_phase × t1_amp_bucket3（闭卷窗内计数定可用）",
                "total": len(cells),
                "ge_floor_30d": sum(1 for c in cells if c["usable_as_dimension"] == 1),
                "sample_floor_days": CELL_DAY_FLOOR,
                "min_days": min((c["trading_days_closed_book"] for c in cells), default=0),
                "max_days": max((c["trading_days_closed_book"] for c in cells), default=0),
            },
            "negatives": {
                "rows": len(negatives),
                "schema": "recipe_id/death_layer/death_reason/values/degraded_dimensions/detail（承 factory_grid_executor NegativeRecord 契约：死亡层+死因缺失即非法）",
                "promise": "不达 30 日地板的胞与零日相位如实入 negatives.csv 并计入 N_eff，禁删改（预注册纪律）",
            },
            "discipline": [
                "公式冻结：emotion_index/六成分=v0.1.0 纯求值；六段相位=auto_mount 法定映射；搜索结果禁回改（改=作废重开新卡）",
                "closed_book_ok=0 段禁参与任何阈值选择/调参/定档，只允许事后观察披露",
                "每条件胞闭卷窗内 <30 交易日不得进搜索空间（usable_as_dimension=0），不达地板日期下沉 conditional-free（禁凑 n、禁当独立样本）",
                "emotion_gate_allow 为空=该日情绪门不可评（宏观态未映射），禁当作禁做段计入对照，亦禁并入双门格",
                "多重检验：进族格数须如实登记（裁定#325 判档表述，禁全绿）",
                "本包禁放 summary.json——n_trial_ledger 会 glob grid_*/summary.json 自动计入 DSR 分母；输入包不是试次批次",
            ],
        },
        "caveats": {
            "six_phase_floor": "宏观腿 regime_snapshot_history 首日 2019-04-01，早此六段不可判（T0-CONDITIONAL-V2 卡 §2.2 覆盖硬限制）",
            "unrouted_not_deny": "r1/r2 震荡态在 R2SIX 无六段对应⇒不路由（auto_mount'宁漏勿误'），本包以 emotion_gate_allow 空值表达，禁误读为禁做",
            "ignition_rarity": "全史仅 2 日路由到 ignition（实测）⇒'情绪上行三段'允许集实际由 expansion/euphoria 主导",
            "vol_bucket_edges_NOT_closed_book_clean": (
                "**已知越界并披露**：t1_vol_bucket3 与宏观门的 0.700 界均引用 t0_regime 卡 §3 "
                "frozen 边界，而其 IS 定档窗止于 **2026-05-31**（超本包闭卷切点 2025-09-09 约 8.5 个月）。"
                "本包无权改继承件常数（改=动判据），故如实登记为越界继承；若 GPU 侧要求严格闭卷，"
                "须由预注册线重定该组边界（实测切点前定档给 0.308/0.704，与 0.328/0.700 实质不同）"
            ),
            "dominant_is_VOL_BAND_not_trend": (
                "**卡面语义与数据源实不符（红蓝 MAJOR-2）**：宏观门写作 dominant∈{r3,r12}"
                f"（卡注'牛市趋势/突破态'），但真源 {tn['state']} 的 dominant 实测是"
                "**波动率风险四档**（r3⇔vol_pct≤0.30 最低波、r2≤0.60、r1≤0.80、r4>0.80），"
                "其模块自述明载『v2 定稿=波动率风险四档，无趋势项』，趋势双确认版已被否决；"
                "r10/r11/r12 是另一张表(regime_snapshot_history 七态 HMM)的编号，本表根本不存在。"
                "⇒ 宏观门的『趋势支』实际选的是**最低波动日**，且与 vol>0.700 支天然互斥"
                "（via_both=0 是该状态机的**构造必然**，不是经验发现——本包前述结论据此降级）。"
                "消费侧若沿用 {r3,r12} 即沿用此误标，须由预注册线裁定是否换源/换态集"
            ),
            "macro_gate_dead_branch": (
                f"卡 §2.1 宏观门 OR 支 dominant∈{{r3,r12}}，但本包状态轴真源 {tn['state'].split('.')[-1]} 的 dominant "
                "取值域实测=仅 {r1,r2,r3,r4} ⇒ **r12 分支在本数据源上永不可达**（搜索空间若按两支独立设计会得一个恒空维）"
            ),
            "dual_gate_anatomy": _dual_gate_anatomy(cb),
            "two_macro_sources_warning": (
                f"两门读的是**两张不同 HMM 表**：宏观门={tn['state']}（dominant 域实测仅 "
                "r1/r2/r3/r4），情绪门六段相位的宏观腿=" + tn["snapshot"] + "（七态，含 r10/r11/r12）"
                "经 auto_mount.R2SIX 映射 ⇒ 双门不是同一根轴数两遍（交叉表见 dual_gate_anatomy.cross_tab_dominant_x_six），"
                "但**把 dominant 与 six_phase 当作同一状态轴的两级来设计搜索格会错**"
            ),
            "amp_axis_note": "振幅取指数日线（000300）而非个股：本包答'哪些状态下市场给的振幅够不够 30bp 前置'，个股振幅属策略实现级另卡",
            "emotion_index_defect_registered": "emoreplay 报告 §5 D-1 记 C2_promotion 恒 1.0（CH join_use_nulls 伪值），daban 史达 120 观测后会抬升温度计——本包 ok_n 列如实带出成分可用性，未代修",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="做T 条件维 GPU 输入包（六段双门×价轴）")
    ap.add_argument("--out-dir", default="data/strategy_intake/grid_t0_conditional_v1")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    six, emo, state, amp = load_axes()
    amp_edges, amp_deriv_n, amp_first, amp_last = derive_amp_edges(amp)
    days = sorted(set(six) & set(emo))  # 温度计 ∩ 六段 = 可判日全集（全窗保留，闭卷由列表达）
    sk, st, ak = sorted(state), sorted(six), sorted(amp)  # T-1 查找表预排序一次
    rows = [
        row_for_day(d, emo[d], t1_lookup(state, d, sk), t1_lookup(six, d, st), t1_lookup(amp, d, ak), amp_edges)
        for d in days
    ]
    if not rows:
        raise SystemExit("FAIL: 输入包零行")

    cells, negatives = build_cells(rows, amp_edges)
    meta = build_meta(rows, cells, negatives, amp_edges, amp_deriv_n, out_dir, deriv_window=(amp_first, amp_last))
    write_pack(out_dir, rows, cells, negatives, meta)
    print(
        yaml.safe_dump(
            {
                "rows": len(rows),
                "cells": len(cells),
                "negatives": len(negatives),
                "amp_edges_bp": [round(x, 2) for x in amp_edges],
                "usable_cells": sum(1 for c in cells if c["usable_as_dimension"] == 1),
            },
            allow_unicode=True,
            sort_keys=False,
        )
    )
    print("wrote:", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
