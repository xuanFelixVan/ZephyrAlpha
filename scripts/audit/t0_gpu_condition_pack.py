# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md | §2 状态选择门（双门×价轴网格；V2 已作废，其 §2.2 六段接线由 V3 §2 逐字继承）
# [MODULE] t0_gpu_condition_pack（scripts 输入包生成件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] docs/_working/t0_matrix/six_phase_history_v1.csv（六段相位真源）；docs/_working/t0_revival/t0_conditional_prereg_card.md（对账模式解析门规则，缺锚即炸）；docs/_working/emotion_line/emotion_index_skeleton_v0.md（对账模式解析五档边界）；market_emotion_index(逻辑品类)（温度计+六成分，只读）；backtest_regime_state_anchored(逻辑品类)（vol_pct/dominant，只读）；c1_market.kline_index 000300（价轴振幅，只读）；scripts/backtest/auto_mount.py 无依赖（相位已在物化件里定形）
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
# [TESTS] tests/audit/test_t0_gpu_condition_pack.py（档界引用性/闭卷标记/阴性带表头/胞地板判定
#   + 全量逐格对账：--reconcile [--offline] 产 docs/_working/t0_matrix/reconcile_pack_v1_{summary.csv,sample20.csv}）
# [TTL] task_bound
"""t0_gpu_condition_pack.py — 做T 条件维度 GPU 矩阵输入包（六段双门 × 价轴，预注册闭卷口径）

格式仿 docs/_working/emotion_line/gpu_emotion_condition_matrix_v1（emoreplay 班情绪包）：
逐日矩阵 .csv + .meta.yaml（provenance/闭卷/纪律），外加 negatives.csv（不达地板胞如实入册）。
落位 data/strategy_intake/grid_t0_conditional_v1/。

用法：生成包 python scripts/audit/t0_gpu_condition_pack.py [--out-dir data/strategy_intake/grid_t0_conditional_v1]
     逐格对账 python scripts/audit/t0_gpu_condition_pack.py --reconcile [--sample 20] [--seed 20260924] [--offline]
     （对账只读盘侧包体+已入库六段真源+frozen 卡文本，产物落 docs/_working/t0_matrix/，一格不一致即非零退出）
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
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
            "pack_bytes_note": "本项=包内各件字数之和，不含本 meta 自身（meta 最后写盘）",
            "pack_bytes_on_disk": sum(p.stat().st_size for p in out_dir.glob("*") if p.is_file()),
            "vram_note": "输入包为逐日单表（1,816 日 × 18 列），显存零压力；每配置查表按 trade_date 索引 O(1)，"
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


# ── 逐格对账（任务⑤落地件）：判据常数一律从 frozen 真源正则解析，不复用本件常量 ──
# 动机：包体按盘面惯例是再生件（data/strategy_intake 子目录在 dev 零跟踪），故对账锚在三处已入库真源
# =六段相位 csv + T0-CONDITIONAL 母本卡 + 情绪温度计骨架件；对账不查库、不起 CH、不改包体一个字节。
CARD_TRUTH = REPO / "docs/_working/t0_revival/t0_conditional_prereg_card.md"
SKELETON_TRUTH = REPO / "docs/_working/emotion_line/emotion_index_skeleton_v0.md"
PRECHECK_TRUTH = REPO / "docs/_working/e2e_integration/w3_w5_precheck_20260923.md"  # 闭卷窗唯一真源
BAND5_CN_TO_EN = ("ice", "cooling", "mild", "warming", "boiling")  # 五档英写序=骨架件中文序同位
RECON_COLUMNS = 10  # 独立重算列数（=len(RECON_DERIVED)）；其余 8 列源值直通，见 RECON_PASSTHROUGH
RECON_DERIVED = (
    "band5",
    "band3_emotion",
    "t1_vol_bucket3",
    "t1_amp_bucket3",
    "closed_book_ok",
    "macro_gate_allow",
    "emotion_gate_allow",
    "dual_gate_allow",
    "t1_six_phase",
    "t1_six_routed",
)
RECON_LEGAL = {  # 派生列值域守卫（实测域见证据件；空串只在"该轴当日不可评"时合法）
    "band5": set(BAND5_CN_TO_EN),
    "band3_emotion": {"low", "mid", "high"},
    "t1_vol_bucket3": {"L", "M", "H", ""},
    "t1_amp_bucket3": {"A1", "A2", "A3", ""},
    "closed_book_ok": {"0", "1"},
    "macro_gate_allow": {"0", "1", ""},
    "emotion_gate_allow": {"0", "1", ""},
    "dual_gate_allow": {"0", "1"},
    "t1_six_routed": {"0", "1"},
    "ok_n": {"1", "2", "3", "4", "5", "6"},  # 六成分可用数：0 与 >6 均不可能（实测域）
}
RECON_RANGE = {  # 源值列物理/口径哨兵（红蓝实证：t1_amp_bp 整列改 1.00bp 原先无人拦）
    "emotion_index": (0.0, 1.0),
    "t1_vol_pct": (0.0, 1.0),
    "t1_amp_bp": (5.0, 20000.0),  # 指数日线振幅下限哨兵：防"极值被抹平"型损坏
}
RECON_NON_BLANK = (  # 源值直通列里"任何日都不得为空"的四列（抹空即红，堵"空白冒充不可评"赢绿）
    "trade_date",
    "emotion_source",
    "formula_version",
    "ok_n",
)
RECON_PASSTHROUGH = (
    "trade_date",
    "emotion_index",
    "ok_n",
    "emotion_source",
    "formula_version",
    "t1_dominant",
    "t1_vol_pct",
    "t1_amp_bp",
)  # 源值直通列：对账不重算（须回查库才能证），如实登记为覆盖面边界而非"已核"


def _anch(text: str, pat: str, src_name: str) -> tuple:
    """frozen 真源取锚：**必须唯一命中**。

    红蓝实证：`re.search` 取"文本里第一处"，故往卡里追加一句同形措辞（例如"阈值调至 0.75 试算"）
    就能**静默劫持**判据值并仍报一致；唯一性把这类改写从"静默换阈值"变成"当场炸"。
    """
    hits = re.findall(pat, text)
    if len(hits) != 1:
        raise SystemExit(
            f"FAIL: frozen 真源锚{'缺失' if not hits else f'不唯一（命中 {len(hits)} 处）'}（{src_name}）：{pat}"
        )
    one = hits[0]
    return one if isinstance(one, tuple) else (one,)


def parse_frozen_rules(meta: dict) -> dict:
    """从**包外已提交真源**解析对账常数（缺锚/多锚即炸，禁退回本件常量=防自我证明）。

    红蓝实证：闭卷窗与 vol 边界原先取自**包体自己的 meta**——等于让被审对象出示自己的尺子：
    改一行 meta 文案即可把闭卷窗静默扩到全部样本外尾日（实测 cutoff→2026-12-31 时闭卷日
    1,566→1,816 仍报全绿）。现一律取包外真源；包 meta 里的 band3/amp 边界无外部锚，
    **如实降格为 selfdeclared_*，不参与"已对真源"的表述**。
    """
    card = CARD_TRUTH.read_text(encoding="utf-8").replace("\r", "")
    skel = SKELETON_TRUTH.read_text(encoding="utf-8").replace("\r", "")
    precheck = PRECHECK_TRUTH.read_text(encoding="utf-8").replace("\r", "")
    vol_h, trend = _anch(card, r"vol_pct\(T-1\) > ([0-9.]+)[^\n]*?dominant\(T-1\) ∈ \{([^}]*)\}", "母本卡 §2.1")
    emo_allow = _anch(card, r"做T 允许：`∈ \{([^}]*)\}`", "母本卡 §2.2")[0]
    b5_edges = tuple(
        float(x)
        for x in _anch(
            skel,
            r"≤([0-9.]+)\s*冰点\s*/\s*[0-9.]+-\s*([0-9.]+)\s*降温\s*/\s*[0-9.]+-\s*([0-9.]+)\s*温和\s*/\s*[0-9.]+-\s*([0-9.]+)\s*升温",
            "骨架件五档",
        )
    )
    b3_lo, b3_hi = _anch(
        meta["band_definitions"]["band3_emotion"],
        r"low<([0-9.]+)≤mid<([0-9.]+)≤high",
        "包 meta band3（自声明，无外部锚）",
    )
    v_lo, v_hi = _anch(card, r"承 frozen 边界 q33=([0-9.]+)/q67=([0-9.]+)", "母本卡 §2.1 vol 分位边界")
    cb_start, cb_cutoff = _anch(precheck, r"closed_book_window: \['([0-9-]+)', '([0-9-]+)'\]", "闭卷窗真源件")
    boiling = float(_anch(skel, r"≥([0-9.]+)\s*沸点", "骨架件五档上界")[0])
    _anch(card, r"情绪门不可用时：单宏观门判定", "母本卡 §2.3 单门兜底支")  # 该支被改写/删除即炸
    a_lo, a_hi = _anch(
        meta["band_definitions"]["t1_amp_bucket3"],
        r"三桶边界=\[([0-9.]+), ([0-9.]+)\]",
        "包 meta amp 桶（自声明，无外部锚）",
    )
    tol = int(_anch(card, r"asof 向后 (\d+) 自然日容差", "母本卡 §2.1 asof 容差")[0])
    return {
        "vol_h": float(vol_h),
        "asof_tol_days": tol,
        "trend": tuple(x.strip() for x in trend.split(",")),
        "emo_allow": tuple(x.strip() for x in emo_allow.split(",")),
        "b5_edges": b5_edges,
        "b3": (float(b3_lo), float(b3_hi)),
        "vol3": (float(v_lo), float(v_hi)),
        "amp3": (float(a_lo), float(a_hi)),
        "cb_start": cb_start,
        "cb_cutoff": cb_cutoff,
        "boiling_edge": boiling,
    }


def _expect_band5(v: float, rules: dict) -> str:
    for edge, label in zip(rules["b5_edges"], BAND5_CN_TO_EN, strict=False):
        if v <= edge:
            return label
    return BAND5_CN_TO_EN[-1]


def _expect_bucket3(v, edges, lo_lab, mid_lab, hi_lab, lo_closed=True) -> str:
    if v in ("", None):
        return ""
    x = float(v)
    lo, hi = edges
    if lo_closed:
        return lo_lab if x <= lo else (mid_lab if x <= hi else hi_lab)
    return lo_lab if x < lo else (mid_lab if x < hi else hi_lab)


def _expect_gates(row: dict, rules: dict) -> tuple[str, str, str]:
    """按母本卡 §2.1/§2.2/§2.3 逐字重算两门与双门（空串=该轴当日不可评，不计允许也不计禁做）。"""
    dom, vs = row["t1_dominant"], row["t1_vol_pct"]
    vol = float(vs) if vs else None
    macro = (
        "" if (not dom and vol is None) else int((vol is not None and vol > rules["vol_h"]) or dom in rules["trend"])
    )
    # 可评性以 **routed** 为准（与生成件同律；红蓝实证：按"相位非空"判会在 routed=0 而相位有值
    # 的未来数据上出假红）
    phase = row["t1_six_phase"] if row["t1_six_routed"] == "1" else ""
    emo = "" if not phase else int(phase in rules["emo_allow"])
    dual = int(macro == 1 and emo == 1)
    return ("" if macro == "" else str(macro), "" if emo == "" else str(emo), str(dual))


def reconcile_row(row: dict, six_prev: dict | None, rules: dict) -> list[str]:
    """一行逐格对账：返回不一致清单（空=全等）。six_prev=六段真源在 T-1 日的行（独立日历）。"""
    v = float(row["emotion_index"])
    exp = {
        "band5": _expect_band5(v, rules),
        "band3_emotion": _expect_bucket3(v, rules["b3"], "low", "mid", "high", lo_closed=False),
        "t1_vol_bucket3": _expect_bucket3(row["t1_vol_pct"], rules["vol3"], "L", "M", "H"),
        "t1_amp_bucket3": _expect_bucket3(row["t1_amp_bp"], rules["amp3"], "A1", "A2", "A3"),
        "closed_book_ok": str(int(rules["cb_start"] <= row["trade_date"] <= rules["cb_cutoff"])),
    }
    m, e, d = _expect_gates(row, rules)
    exp["macro_gate_allow"], exp["emotion_gate_allow"], exp["dual_gate_allow"] = m, e, d
    # 真源侧不做 `or ""` 兜底：`or` 会把"键缺失/空值"与"合法空值"糊成一格（红蓝实证：
    # routed 被抹成 '' 时 `str(None or "0")` 反造出正确答案）——缺键即 KeyError 炸出来。
    exp["t1_six_phase"] = six_prev["six_phase"] if six_prev else ""
    exp["t1_six_routed"] = six_prev["routed"] if six_prev else "0"
    bad = [
        f"{row['trade_date']}:{col} 越界={row.get(col)!r}∉[{lo},{hi}]"
        for col, (lo, hi) in RECON_RANGE.items()
        if str(row.get(col, "")).strip() and not lo <= float(row[col]) <= hi
    ] + [
        f"{row['trade_date']}:{col} 值域非法={row.get(col)!r}（允许={sorted(legal)}）"
        for col, legal in RECON_LEGAL.items()
        if col not in RECON_DERIVED and str(row.get(col, "")) not in legal
    ]
    bad_blank = [
        f"{row.get('trade_date', '?')}:{col} 源值列被抹空（禁以空值冒充不可评）"
        for col in RECON_NON_BLANK
        if not str(row.get(col, "")).strip()
    ]
    for col, want in exp.items():
        got = row.get(col, "")
        if got != want:
            bad.append(f"{row['trade_date']}:{col} 包体={got!r} 对账={want!r}")
        legal = RECON_LEGAL.get(col)
        if legal is not None and got not in legal:
            bad.append(f"{row['trade_date']}:{col} 值域非法={got!r}（允许={sorted(legal)}）")
    return bad + bad_blank


def prev_truth(six_dates: list[str], six: dict, day: str, tol_days: int) -> dict | None:
    """独立日历取 T-1 六段行=真源日序列里严格早于 day 的最大日，超 asof 容差即 None。

    对账独立性的关键：这里**自己实现**二分+容差判定，不调用生成件的 t1_lookup；
    容差天数从母本卡文本解析（下方 asof_tol_days 锚），故卡与码若漂移本对账即红。
    """
    from datetime import date, timedelta

    d = date.fromisoformat(day)
    lo, hi = 0, len(six_dates)
    while lo < hi:
        mid = (lo + hi) // 2
        if six_dates[mid] < day:
            lo = mid + 1
        else:
            hi = mid
    if not lo or (d - date.fromisoformat(six_dates[lo - 1])) > timedelta(days=tol_days):
        return None
    return six[six_dates[lo - 1]]


STRUCTURAL_CHECK_NAMES = (
    "结构守卫七项全过：日期唯一/升序/行数对 meta.rows/跨度对 meta.date_span/日集合⊆六段真源/"
    "行数=六段真源行数/非空 trade_date"
)


def _structural_checks(rows: list[dict], meta: dict, truth_days: set[str]) -> list[str]:
    """结构四项 + 两条"伪造整包也过不去"的守卫：日是真源子集、行数不超真源。

    红蓝实证：只与包内自带 meta 互校时，重生成一份自洽的坏 meta 配对即可全绿——
    故这里必须引入**包外已入库真源**的行数/日集合做上界与子集判据。
    """
    days = [r["trade_date"] for r in rows]
    bad = []
    if not set(days) <= truth_days:
        bad.append(f"包体含 {len(set(days) - truth_days)} 个不在六段真源日集合里的日期（伪造整包的指纹）")
    if len(rows) != len(truth_days):
        # 当前两轴日集合全等（温度计 ⊇ 六段），故等式成立；不等＝有日在包体里消失/多出，
        # 而"删一行 + 同步改 meta"这种自洽伪造正是只跟包内 meta 互校时的盲区。
        bad.append(f"包体行数 {len(rows)} ≠ 六段真源行数 {len(truth_days)}（可判日全集=两轴日交集）")
    if len(set(days)) != len(days):
        bad.append("包体 trade_date 有重复")
    if days != sorted(days):
        bad.append("包体 trade_date 非升序")
    if len(rows) != int(meta["rows"]):
        bad.append(f"包体行数 {len(rows)} ≠ meta.rows {meta['rows']}")
    if (days[0], days[-1]) != tuple(str(x) for x in meta["date_span"]):
        bad.append("包体日期跨度 ≠ meta.date_span")
    if not all(days):
        bad.append("存在空 trade_date")
    return bad


def db_spotcheck(rows: list[dict], picked: list[int], state: dict, amp: dict, emo: dict) -> dict:
    """抽样回查**源值直通列**（对账离线面唯一证不了的 7 列）。

    独立性声明（如实）：取数走生成件同一批 loader（同 SQL 同 argMax 版本选取），
    故本项证的是"包体落格/日对齐/轴日集合与当前真源一致"，**不**独立复核 SQL 语义本身；
    红蓝实证：把 t1_vol_pct+其桶+门三列同向改写，离线对账会全绿，只有回查能抓。
    """
    st_keys, amp_keys = sorted(state), sorted(amp)
    tol = int(
        _anch(
            CARD_TRUTH.read_text(encoding="utf-8").replace("\r", ""),
            r"asof 向后 (\d+) 自然日容差",
            "母本卡 §2.1 asof 容差",
        )[0]
    )
    bad: list[str] = []
    n = 0
    for i in picked:
        r = rows[i]
        d = r["trade_date"]
        e = emo.get(d) or {}
        sp = prev_truth(st_keys, state, d, tol) or (None, None)
        ap = prev_truth(amp_keys, amp, d, tol)
        pairs = [
            ("emotion_index", r["emotion_index"], e.get("emotion_index"), 6),
            ("ok_n", r["ok_n"], e.get("ok_n"), None),
            ("emotion_source", r["emotion_source"], e.get("source"), None),
            ("formula_version", r["formula_version"], e.get("version"), None),
            ("t1_dominant", r["t1_dominant"], sp[0], None),
            ("t1_vol_pct", r["t1_vol_pct"], sp[1], 6),
            ("t1_amp_bp", r["t1_amp_bp"], ap, 2),
        ]
        for col, got, want, eps in pairs:
            n += 1
            if want is None or want == "":
                ok = str(got) in ("", "None")
            elif eps is None:
                ok = str(got) == str(want)
            else:
                try:
                    # 与包体**同精度**比较：包体写盘时 round 过，拿未 round 真源硬比会假红
                    ok = str(round(float(want), eps)) == str(float(got))
                except ValueError:
                    ok = False
            if not ok:
                bad.append(f"{d}:{col} 包体={got!r} 真源={want!r}")
    return {"cells_compared": n, "mismatch": len(bad), "list": bad[:20]}


def _dominant_cross_source(rows: list[dict], six_dates: list[str], six: dict, rules: dict) -> tuple:
    """跨源观察（非判据）：包体宏观腿标签 vs 六段真源宏观腿标签的一致数与两侧标签域。"""
    cmp_ = [
        (
            r["t1_dominant"],
            str((prev_truth(six_dates, six, r["trade_date"], rules["asof_tol_days"]) or {}).get("dominant") or ""),
        )
        for r in rows
    ]
    agree = sum(1 for a_, bb in cmp_ if str(a_) == bb)
    return agree, "|".join(sorted({str(a_) for a_, _ in cmp_})), "|".join(sorted({str(bb) for _, bb in cmp_}))


def _write_sample_evidence(out_dir: Path, rows: list[dict], picked: list[int], per_row: list[list[str]]) -> None:
    """抽样件带**全部 18 列原值** + 本行不一致数：让审计员只凭已入库文件就能逐格复算这 20 行，
    不必再生成盘侧包体（红蓝实证：只记 (日期,列数,不一致数) 的抽样件支撑不了任何独立复算）。"""
    cols = list(rows[0].keys())
    with (out_dir / "reconcile_pack_v1_sample20.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow([*cols, "derived_columns_checked", "mismatch_cells"])
        w.writerows([[rows[i][c] for c in cols] + [RECON_COLUMNS, len(per_row[i])] for i in picked])


def _write_kv_evidence(path: Path, kv: dict) -> None:
    """证据落 .csv 而非 .yaml：docs/_working 禁 .json（DCR-005/008），而新增非 rules/ .yaml 需
    CREATE-GUARD creation_token（=申报新能力真源）；对账证据不是配置真源，故 key,value 两列 CSV 不占册。"""
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "value"])
        w.writerows([[k, v] for k, v in kv.items()])


def _sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _reconcile_disclosure(rows: list[dict], six_dates: list[str], six: dict, rules: dict) -> dict:
    """如实披露"评不了"的日数与卡 §2.3 兜底支的规模（这些不是错，但必须让下游看得见）。"""
    asof_miss = macro_nei = emo_nei = single_macro = 0
    for r in rows:
        if prev_truth(six_dates, six, r["trade_date"], rules["asof_tol_days"]) is None:
            asof_miss += 1
        if not r["macro_gate_allow"]:
            macro_nei += 1
        if not r["emotion_gate_allow"]:
            emo_nei += 1
        if r["macro_gate_allow"] == "1" and not r["emotion_gate_allow"]:
            single_macro += 1
    return {
        "asof_miss_days": asof_miss,
        "asof_miss_note": "超卡 §2.1 asof 容差而弃的日数（该日 T-1 六段读不可用）",
        "macro_unevaluable_days": macro_nei,
        "emotion_unevaluable_days": emo_nei,
        "single_macro_gate_days": single_macro,
        "single_macro_gate_note": "卡 §2.3 兜底支规模：宏观门=1 而情绪门不可评的日数；"
        "双门列把它们记 0，考试走单门时这批改可用——下游按 dual_gate_allow 搜索即静默丢弃此支",
    }


def run_reconcile(pack_dir: Path, out_dir: Path, sample: int, seed: int, offline: bool = False) -> int:
    """全量逐格对账（**默认含源值列全量回查**）+ 抽样件落盘；任一格不一致=非零退出（禁静默空对账）。

    红蓝实证：抽样 20 行的回查覆盖率只有 1.1%（140/12,712），把源值列整体错配/前视移一位
    都能全绿；故回查改为**默认全量**，`--offline` 才退回纯离线面（并在证据里写明覆盖为 0）。
    """
    matrix, meta_f = pack_dir / "t0_condition_matrix_v1.csv", pack_dir / "t0_condition_matrix_v1.meta.yaml"
    if not matrix.exists() or not meta_f.exists():
        raise SystemExit(f"FAIL: 包体缺失（{matrix}）——先跑本件生成模式，禁对不存在的包出绿")
    rows = list(csv.DictReader(matrix.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise SystemExit("FAIL: 包体零行")
    meta = yaml.safe_load(meta_f.read_text(encoding="utf-8"))
    rules = parse_frozen_rules(meta)
    six = load_six_phase(SIX_PHASE_TRUTH)
    six_dates = sorted(six)
    per_row = [
        reconcile_row(r, prev_truth(six_dates, six, r["trade_date"], rules["asof_tol_days"]), rules) for r in rows
    ]
    struct = _structural_checks(rows, meta, set(six))
    _agree, _dom_pack, _dom_six = _dominant_cross_source(rows, six_dates, six, rules)
    rng = random.Random(seed)
    picked = sorted(rng.sample(range(len(rows)), min(sample, len(rows))))
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_sample_evidence(out_dir, rows, picked, per_row)
    dbspot = None
    if not offline:
        _, emo_src, state_src, amp_src = load_axes()
        dbspot = db_spotcheck(rows, list(range(len(rows))), state_src, amp_src, emo_src)
    summary = {
        "pack_matrix_file": matrix.name,
        "rows_reconciled": len(rows),
        "derived_columns_reconciled": RECON_COLUMNS,
        "derived_column_names": "|".join(RECON_DERIVED),
        "passthrough_columns_not_covered": "|".join(RECON_PASSTHROUGH),
        "cross_source_dominant_agreement": f"{_agree}/{len(rows)}={round(_agree / len(rows), 4)}",
        "cross_source_label_domains": f"包体宏观腿={{{_dom_pack}}}；六段真源宏观腿={{{_dom_six}}}",
        "cross_source_note": "观察非判据：包体宏观腿取锚定态表（实测仅 r1-r4 四带），六段真源宏观腿取快照态表"
        "（HMM 七态含 r10/r11/r12）⇒ 标签域本不同，一致率低是**两源词表不同**的度量，"
        "并给'r12 趋势支在锚定源上永不可达'一条量化证据；此项不参与红绿判定",
        "asof_tolerance_natural_days_parsed_from_card": rules["asof_tol_days"],
        "mismatch_cells": sum(len(b) for b in per_row),
        "mismatch_rows": sum(1 for b in per_row if b),
        "structural_checks": "; ".join(struct or [STRUCTURAL_CHECK_NAMES]),
        "rule_vol_h": rules["vol_h"],
        "rule_macro_trend_states": "|".join(rules["trend"]),
        "rule_emotion_allow": "|".join(rules["emo_allow"]),
        # 第五档上界也解析并入清单（红蓝实证：只取前 4 个时改"≥0.8 沸点"文案不会报）
        "rule_band5_edges": "|".join([str(x) for x in rules["b5_edges"]] + [str(rules["boiling_edge"])]),
        "selfdeclared_band3_edges_from_pack_meta": "|".join(str(x) for x in rules["b3"]),
        "rule_vol_bucket3_edges": "|".join(str(x) for x in rules["vol3"]),
        "selfdeclared_amp3_edges_bp_from_pack_meta": "|".join(str(x) for x in rules["amp3"]),
        "rule_closed_book_window": f"{rules['cb_start']}|{rules['cb_cutoff']}",
        "sample_n": len(picked),
        "sample_seed": seed,
        "sample_days": "|".join(rows[i]["trade_date"] for i in picked),
        "mismatch_items_total": sum(len(b) for b in per_row),
        "first_mismatches": " ;; ".join(x for b in per_row if b for x in b)[:2000],
        "first_mismatches_note": "本清单按 2,000 字符截断；全量条数见 mismatch_items_total（禁把截断读作全貌）",
        "source_cells_compared": (dbspot or {}).get("cells_compared", 0),
        "source_cells_total": len(rows) * 7,
        "source_coverage_note": "离线面（--offline）时本项为 0/总数：源值直通列未经回查，不得读作已核",
        "source_spotcheck_mismatch": (dbspot or {}).get("mismatch", ""),
        "source_spotcheck_list": " ;; ".join((dbspot or {}).get("list", []))[:1500],
        **_reconcile_disclosure(rows, six_dates, six, rules),
        "fingerprint_sha256_16": "|".join(
            [
                f"matrix={_sha16(matrix)}",
                f"meta={_sha16(meta_f)}",
                f"six_phase={_sha16(SIX_PHASE_TRUTH)}",
                f"card={_sha16(CARD_TRUTH)}",
                f"skeleton={_sha16(SKELETON_TRUTH)}",
                f"precheck={_sha16(PRECHECK_TRUTH)}",
            ]
        ),
    }
    _write_kv_evidence(out_dir / "reconcile_pack_v1_summary.csv", summary)
    print(
        yaml.safe_dump(
            {
                k: summary[k]
                for k in ("rows_reconciled", "derived_columns_reconciled", "mismatch_cells", "mismatch_rows")
            },
            allow_unicode=True,
            sort_keys=False,
        )
    )
    if summary["mismatch_cells"] or struct or (dbspot and dbspot["mismatch"]):
        print("FAIL: 对账不一致/结构缺陷/回查不一致——清单见 reconcile_pack_v1_summary.csv")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="做T 条件维 GPU 输入包（六段双门×价轴）")
    ap.add_argument("--out-dir", default="data/strategy_intake/grid_t0_conditional_v1")
    ap.add_argument("--reconcile", action="store_true", help="只读逐格对账模式（不生成包、不查库）")
    ap.add_argument("--pack-dir", default="data/strategy_intake/grid_t0_conditional_v1", help="对账模式读此处的包体")
    ap.add_argument("--reconcile-out-dir", default="docs/_working/t0_matrix")
    ap.add_argument("--sample", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260924)
    ap.add_argument(
        "--offline", action="store_true", help="对账模式跳过源值列回查（默认全量回查 7 列 × 全部日，起 CH 只读）"
    )
    args = ap.parse_args()
    if args.reconcile:
        return run_reconcile(Path(args.pack_dir), Path(args.reconcile_out_dir), args.sample, args.seed, args.offline)
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
