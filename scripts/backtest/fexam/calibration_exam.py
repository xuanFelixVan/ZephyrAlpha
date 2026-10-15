# [BLUEPRINT] MOD-BT-243 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.fexam.calibration_exam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; scripts/backtest/fexam/ch_data; scripts/backtest/fexam/ic_exam;
#   zephyr/backtest/core/n_trial_ledger; yaml
# [CONSUMERS] W4 校准战役出分（20 张预注册卡的执行器）；W5 writeback_exam_confidence（分数册消费方上游）;
#   人工 CLI（--card 逐卡开考）
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 只考 preregistered 卡（empty=未冻结禁考；examined=已出分，重考须 --force 且新分数行
#   only-add 追加禁改旧行）；判据门柱=卡内 pillars_numeric（裁定#501 冻结面，执行器零裁量）；
#   verdict=门柱全过才 pass（一票否决）；分数行落 exam_scores_v1.yaml only-add；试次入 n_trial_ledger；
#   信号/目标可注入（测试零 CH），缺省经 ch_data 按 signal_spec/target_spec 取数。
#   试次册路径可注入（run_card 的 ledger_registry_path，缺省=生产真源不变）：测试一律注入 tmp_path，
#   禁经单测写生产 N 账本（根宪法 §9 条目 6；10-12 实测泄漏形态=examcard:TDM-E-TEST/* 进生产册）。
#   三柱（迟滞带增益/升降往返/危机段漏触发）读数须由绑定层 arm_context 注入（run_card 的新 kwarg，
#   与 ledger_registry_path 同属"注入位"惯例）：判官零自取底座、零重写判定逻辑，缺注入即显式记败，
#   测试用合成级别序列注入零 CH（统筹裁定③ 2026-10-12 立项）。
# [MODIFY-GUARD] tests/backtest/test_calibration_exam.py
# [STABILITY] experimental
# [ERROR_CONTRACT] RuntimeError: 卡状态非法/缺 pillars_numeric/信号目标缺失/分数册 CAS 冲突
# [TESTS] tests/backtest/test_calibration_exam.py
# [A_module] module_id=MOD-BT-243 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [not-trading: 回测研究面工具（考试卡骨架/校准执行/置信度回写），不在实盘交易决策路径上；TDM 挂载随分数册集成批另办]
"""环节校准卡考试执行器（W4）——预注册卡 → 响应曲线/IC/时滞/行情段四件套 → 分数行。

两形信号：
  panel  逐符号面板：复用 ic_exam.fast_rank_ic/ic_stats/regime_ic_slice（机判同构不自研）。
  series 日度序列（广度/结果面）：分桶日→桶中位次日目标→桶秩-中位 Spearman 单调 +
         时序 Spearman 作 IC；牛/熊窗分段同号判稳。

分数行 schema 与 W5 writeback_exam_confidence 对齐（card_id/node_id/run_id/kind/verdict/
pillars_all_pass/oos_ok/regimes/date）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date as _date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from zephyr.shared.io.paths import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

from fexam.ic_exam import fast_rank_ic, ic_stats, regime_ic_slice  # noqa: E402

SCORES_PATH = REPO_ROOT / "docs" / "04_research_records" / "backtest" / "scores" / "2026" / "exam_scores_v1.yaml"


class _ToolError(RuntimeError):
    def __init__(self, msg: str, details: dict | None = None):
        super().__init__(msg)
        self.details = details or {}


_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _span_pairs(span: str) -> list[tuple[str, str]]:
    """行情段跨度解析：取串内**全部**成对日期（统筹 2026-10-13 裁修）。

    旧实现只返回前两个日期，而卡面 regime 串实测写成多段声明
    （"2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段）"，
    02/06/07/07b 与另 4 张卡同形）⇒ 第二段起被静默弃。
    裁定原文＝实现面背离冻结意图的 bug，非判据变更；单段串的解析结果与旧行为逐字同值，
    不足两个日期时 also 退回旧语义（整串当单点）。
    """
    hits = _DATE_RE.findall(str(span))
    if len(hits) < 2:
        return [(str(span), str(span))]
    return [(hits[i], hits[i + 1]) for i in range(0, len(hits) - 1, 2)]


def _in_spans(index: pd.Index, span: str) -> pd.Series:
    """regime 串的**所有**段并成一条布尔掩码（供逐日切片；单段等价于旧的 >=lo & <=hi）。"""
    ts = pd.DatetimeIndex(pd.to_datetime(index))
    mask = np.zeros(len(ts), dtype=bool)
    for a, b in _span_pairs(span):
        mask = mask | np.asarray((ts >= pd.Timestamp(a)) & (ts <= pd.Timestamp(b)))
    return pd.Series(mask, index=index)


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    s = pd.Series(a).rank()
    t = pd.Series(b).rank()
    if s.std() == 0 or t.std() == 0:
        return float("nan")
    return float(np.corrcoef(s, t)[0, 1])


def _round_trip_cost_bp(config_path=None) -> float:
    """G1 净费参数（exam_scale_cost_gate.yaml net_fee 节，禁硬编码；读败=nan 不伪造）。"""
    cp = Path(config_path) if config_path else REPO_ROOT / "config" / "exam_scale_cost_gate.yaml"
    try:
        data = yaml.safe_load(cp.read_text(encoding="utf-8"))
        return float(data["net_fee"]["round_trip_cost_bp"])
    except Exception:  # noqa: BLE001  读败=nan 不伪造（费率参数面缺 net_fee 节属合法态）
        return float("nan")


def _signal_turnover(signal: pd.Series) -> float | None:
    """G2 换手计量：相邻交易日信号值变化占比（档位翻转率，只计量不判罚）。"""
    v = signal.dropna()
    if len(v) < 2:
        return None
    changes = (v.diff().fillna(0) != 0).iloc[1:]
    return round(float(changes.mean()), 4)


#: 卡面分桶型 → 桶数（真源=exam_cards 在册 buckets.type 实测集合）。
#: 治本原因：本执行器曾硬写 n_buckets=10，而卡面有 quantile_quintile 五分位冻结——
#: 五分位卡被按十分位算 mono_spearman＝读数口径与冻结门柱不一致（非自愿挪门柱级，
#: 2026-10-11 矿考循环班实测 3 张已出分卡受此影响，见 mineloop_campaign/09_caliber_deviation_note.yaml）。
#: 词表外（双臂/臂矩阵等）沿用 10 桶缺省：那些族走 _comparison_metrics 的配对差面。
_BUCKET_TYPE_N: dict[str, int] = {
    "quantile_decile": 10,
    "quantile_quintile": 5,
    "quantile_tercile": 3,
    "quantile_quartile": 4,
    "tercile": 3,
    "quartile": 4,
    "decile": 10,
    "quintile": 5,
}


def _n_buckets_from_card(card: dict) -> int:
    """读卡面冻结的分桶型定桶数；卡面未声明分位型→缺省 10（不改既有行为）。"""
    b = card.get("buckets")
    if not isinstance(b, dict):
        return 10
    t = str(b.get("type") or "").strip().lower()
    if t in _BUCKET_TYPE_N:
        return _BUCKET_TYPE_N[t]
    m = re.fullmatch(r"quantile_(\d{1,2})", t)
    if m:
        return max(2, int(m.group(1)))
    return 10


def _bucket_response(signal: pd.Series, target: pd.Series, n_buckets: int = 10) -> dict:
    """日度序列分桶响应：按信号分位分桶 → 桶内目标中位 → 桶序-中位 Spearman。

    序数信号（唯一值 <= n_buckets，如三态档位卡）按信号值直接分桶（尊重冻结桶型）。"""
    df = pd.concat({"sig": signal, "tgt": target}, axis=1).dropna()
    if len(df) < n_buckets * 10:
        return {"n": len(df), "bucket_medians": [], "mono_spearman": float("nan"), "n_buckets_used": n_buckets}
    if df["sig"].nunique() <= n_buckets:
        df["b"] = df["sig"].rank(method="dense")
    else:
        df["b"] = pd.qcut(df["sig"].rank(method="first"), n_buckets, labels=False)
    med = df.groupby("b")["tgt"].median()
    rho = _spearman(med.index.to_numpy(float), med.to_numpy(float))
    return {
        "n": int(len(df)),
        "bucket_medians": [float(x) for x in med],
        "mono_spearman": rho,
        "n_buckets_used": n_buckets,
    }


def _forward_face(card: dict) -> tuple[int, bool]:
    """多日标的前向面申报位（挖矿二班 2026-10-13 立项，统筹署名批准）。

    缺省（两键都不在卡面）＝`(1, False)`＝现行 shift(-1) 次日语义**逐字不变**；既有 178 张
    preregistered 卡与全部已出分卡的读数面不受本函数影响。

    申报形态（两键必须成对且与目标名自洽，缺一即拒，禁"半申报"静默走次日面）：
      target_forward_face: precomputed
      target_horizon_days: <2..252 的整数>
      target.primary 内须写 `mkt_fwd<h>`（h 与 target_horizon_days 同值）
    语义：注入的 target **已是 h 日前向读数**（前向聚合在数据侧完成，真源=卡面
    data_binding.target_source 声明），故执行器不再二次位移；本函数零新增阈值、零新算法，
    只把"位移几天"这一件事从硬编码改为按卡面冻结值消费。
    """
    face = str(card.get("target_forward_face") or "").strip()
    hraw = card.get("target_horizon_days")
    if face == "" and hraw is None:
        return 1, False
    if face != "precomputed":
        raise _ToolError(
            f"卡面 target_forward_face={face!r} 非在册形态（唯一允许值=precomputed）——"
            "半申报或错拼一律拒，禁退化成次日面静默出分"
        )
    if isinstance(hraw, bool) or not isinstance(hraw, int) or not 2 <= hraw <= 252:
        raise _ToolError(f"卡面 target_horizon_days={hraw!r} 非法（须为 2..252 的整数）——拒出分，禁默认回退次日面")
    primary = str((card.get("target") or {}).get("primary") or "")
    m = re.search(r"mkt_fwd(\d+)", primary)
    if not m or int(m.group(1)) != hraw:
        raise _ToolError(
            f"卡面 horizon 自洽性不过，拒出分：target_horizon_days={hraw} 而 target.primary 里的 "
            f"mkt_fwd{{h}} 读数={m.group(1) if m else '缺失'}——两处冻结值必须同值，禁回退次日面"
        )
    return int(hraw), True


def _series_metrics(signal: pd.Series, target: pd.Series, card: dict) -> dict:
    sig = signal.sort_index()
    horizon, precomputed = _forward_face(card)
    # 次日面（缺省）：t 信号对 t+1 目标，shift(-1) 语义一字未动。
    # 前向面（卡面成对申报且自洽）：注入值已是第 horizon 日读数，禁二次位移。
    tgt = target.sort_index() if precomputed else target.sort_index().shift(-1)
    aligned = pd.concat({"s": sig, "t": tgt}, axis=1).dropna()
    ic_ts = _spearman(aligned["s"].to_numpy(), aligned["t"].to_numpy())
    resp = _bucket_response(sig, tgt, _n_buckets_from_card(card))
    regimes = card.get("window", {}).get("regimes", {})
    seg: dict[str, float] = {}
    for name, span in regimes.items():
        m = aligned[_in_spans(aligned.index, span).to_numpy()]
        seg[name] = _spearman(m["s"].to_numpy(), m["t"].to_numpy()) if len(m) >= 60 else float("nan")
    oos = card.get("oos_window_ref") or []
    oos_ic = float("nan")
    if len(oos) == 2:
        m = aligned[(aligned.index >= pd.Timestamp(oos[0])) & (aligned.index <= pd.Timestamp(oos[1]))]
        oos_ic = _spearman(m["s"].to_numpy(), m["t"].to_numpy()) if len(m) >= 60 else float("nan")
    # G1 净费读数（增补令 2026-10-10）：桶中位收益减往返成本（费率参数面 net_fee 节，禁硬编码）
    net_med = None
    if resp.get("bucket_medians"):
        rt = _round_trip_cost_bp()
        net_med = [round(x - rt / 10000.0, 6) for x in resp["bucket_medians"]]
    # G2 换手读数（只计量不判罚）：相邻交易日信号档位翻转率
    turn = _signal_turnover(signal)
    return {
        "ic_mean": ic_ts,
        "mono_spearman": resp.get("mono_spearman"),
        "n": resp.get("n"),
        "regime_ic": seg,
        "oos_ic": oos_ic,
        "ic_ir": None,
        "bucket_medians": resp.get("bucket_medians"),
        "net_bucket_medians": net_med,
        "round_trip_cost_bp": _round_trip_cost_bp(),
        "signal_turnover_daily": turn,
        "n_buckets_used": resp.get("n_buckets_used"),
    }


def _panel_metrics(signal: pd.DataFrame, target: pd.DataFrame, card: dict) -> dict:
    ret = target.shift(-1)
    ic = fast_rank_ic(signal, ret).dropna()
    st = ic_stats(ic)
    regimes = card.get("window", {}).get("regimes", {})
    seg = {}
    for name, span in regimes.items():
        part = ic[_in_spans(ic.index, span).to_numpy()]
        seg[name] = float(part.mean()) if len(part) >= 30 else float("nan")
    oos = card.get("oos_window_ref") or []
    oos_ic = float("nan")
    if len(oos) == 2:
        part = ic[(ic.index >= pd.Timestamp(oos[0])) & (ic.index <= pd.Timestamp(oos[1]))]
        oos_ic = float(part.mean()) if len(part) >= 30 else float("nan")
    return {
        "ic_mean": float(st.get("ic_mean", float("nan"))),
        # ic_stats 的回键真名是 "icir"（ic_exam.ic_stats:42），此处曾读 "ic_ir" ⇒ panel 路 ic_ir 恒 NaN，
        # 而 judge 对 NaN 的处置是"跳过加败"（只可能放行不可能记败）＝卡面冻了 ic_ir_min 却从未被评估。
        "ic_ir": float(st.get("icir", float("nan"))),
        "mono_spearman": None,
        "regime_ic": seg,
        "oos_ic": oos_ic,
        "n": int(ic.notna().sum()),
        "bucket_medians": None,
    }


def _arm_nav_metrics(exposure: pd.Series, target: pd.Series, cost_bp: float | None = None) -> dict:
    """对照/消融单臂日频回放（PIT：t 收盘敞口 → t+1 目标收益；同轴同撮合同成本）。

    maxdd=正深度（0..1）；sharpe 年化（sqrt252）已扣换手成本；turnover_annual_x=年化敞口
    翻转倍数（|Δ敞口|均值×252，无量纲 x——对齐 exam_scale_cost_gate turnover_gate.cap_annual_x 口径）。
    成本默认读 net_fee.round_trip_cost_bp（读败=0 成本并在返回面标 cost_bp=nan，禁伪造）。
    """
    if cost_bp is None:
        cost_bp = _round_trip_cost_bp()
    df = pd.concat({"e": exposure.sort_index(), "r": target.sort_index()}, axis=1).dropna()
    if len(df) < 30:
        return {
            "n": len(df),
            "maxdd": float("nan"),
            "sharpe": float("nan"),
            "turnover_annual_x": float("nan"),
            "ann_ret": float("nan"),
            "cost_bp": cost_bp,
        }
    ret = df["e"].shift(0) * df["r"].shift(-1)  # t 敞口吃 t+1 收益
    turn = df["e"].diff().abs().iloc[1:]
    cbp = cost_bp if cost_bp == cost_bp else 0.0
    ret_net = ret - turn.reindex(ret.index).fillna(0.0) * cbp / 10000.0
    nav = (1.0 + ret_net.fillna(0.0)).cumprod()
    dd = nav / nav.cummax() - 1.0
    mu, sd = ret_net.mean(), ret_net.std()
    sharpe = float(mu / sd * np.sqrt(252)) if sd and sd == sd and sd > 0 else float("nan")
    return {
        "n": int(len(df)),
        "maxdd": float(-dd.min()) if len(dd) else float("nan"),
        "sharpe": sharpe,
        "turnover_annual_x": float(turn.mean() * 252) if len(turn) else float("nan"),
        "ann_ret": float(ret_net.mean() * 252),
        "cost_bp": cost_bp,
    }


_COMPARISON_KNOWN_KEYS = frozenset(
    {
        "misfire_reduction_min",
        "maxdd_improvement_min",
        "maxdd_deterioration_max_pp",
        "sharpe_delta_min",
        "turnover_delta_annual_max",
        "cost_tier_bp_required",
        "oos_same_sign",
        # 裁定③（统筹 2026-10-12，三柱机器面立项）：以下三键自 02 族第一天就申报"词表外"，
        # 从此有判官接手——入词表**不等于**无条件放行：读数须由绑定层注入 arm_context，
        # 缺注入即显式记败（与 misfire_reduction_min 的"无机判面如实记败"同款，禁静默跳）。
        "maxdd_improvement_vs_no_hysteresis_min_pp",
        "whipsaw_roundtrip_ratio_max",
        "missed_crisis_trigger_max",
    }
)

#: 校准判官（judge()）实际读取的 pillars_numeric 键集——judge() 的读取面唯一镜像。
#: run_card 的判官分派（_cal_shaped）与未判柱观测（_unjudged_pillars）共用本常量，禁两处各抄一份。
_CALIBRATION_JUDGED_KEYS = frozenset(
    {
        "mono_spearman_min",
        "ic_mean_min",
        "ic_ir_min",
        "regime_same_sign",
        "oos_same_sign",
    }
)


def _unjudged_pillars(card: dict, m: dict, judged: frozenset) -> dict:
    """未判柱清单（纯观测面，零否决权）：分数册行 MUST 自带"这一分只代表哪些键"。

    三面各自如实：①numeric_keys_not_read=卡面冻结了但当前判官根本没读的键（历史 pass 不等于这些键过）；
    ②numeric_keys_no_machine_face=读了该键但当前 metrics 面无从评估（如 panel 路 mono 恒 None、
    ic_ir 未接时 NaN、regime 有效段不足 2）；③pillars_prose_keys=卡面文字门柱原样列表——
    prose↔numeric 的对应关系无在册真源，本件不代拍（该映射是"门柱词表立法"工单的对象，禁改键值）。"""
    p = card.get("pillars_numeric") or {}
    no_face: dict[str, str] = {}
    if "mono_spearman_min" in p:
        mono = m.get("mono_spearman")
        if mono is None or mono != mono:
            no_face["mono_spearman_min"] = "mono_spearman 无面（panel 路恒 None／分桶样本不足 NaN）"
    ir_val = m.get("ic_ir")
    if "ic_ir_min" in p and (ir_val is None or ir_val != ir_val):
        no_face["ic_ir_min"] = "ic_ir 无从评估（series 路恒 None／panel 路 NaN＝ICIR 面未接，judge 同时跳过加败）"
    if "regime_same_sign" in p:
        vals = [v for v in (m.get("regime_ic") or {}).values() if v == v]
        if len(vals) < 2:
            no_face["regime_same_sign"] = f"regime_ic 有效段 {len(vals)} <2（牛/熊同号不可判）"
    if "oos_same_sign" in p and m.get("oos_ic") != m.get("oos_ic"):
        no_face["oos_same_sign"] = "oos_ic NaN（judge 已同时记败，非静默跳过）"
    prose = card.get("pillars")
    return {
        "numeric_keys_not_read": sorted(set(p) - set(judged)),
        "numeric_keys_no_machine_face": no_face,
        "pillars_prose_keys": sorted(prose) if isinstance(prose, dict) else ([] if prose is None else [str(prose)]),
        "mapping_note": "prose↔numeric 映射无在册真源，本面不代拍（词表立法工单对象）",
    }


# ──────────────────────────────────────────────────────────────────────────────
# 裁定③（统筹 2026-10-12：三柱机器面立项，归矿考二班域）
# 纪律：三柱读数一律由绑定层注入的 `arm_context`（在册判定件 MOD-RK-049 回放的级别序列＋
#   卡面冻结的级别→仓位映射）算出——判官零重写判定逻辑、零自取底座（那是第二真源）。
#   口径选择逐条在本段声明并随班账呈批；缺注入显式记败，禁静默跳（与 misfire 柱同款）。
# ──────────────────────────────────────────────────────────────────────────────

#: 卡面原文"30 日内升降级往返"的窗位；量距用**该序列自身的交易日序号**（非自然日），读法随此声明
_WHIPSAW_WINDOW_TRADING_DAYS = 30
_CAP_EPS = 1e-12


def _cap_series(levels: pd.Series, cap_map: dict) -> pd.Series:
    """级别序列 → 卡面冻结的仓位上限序列（逐日）。出现映射没覆盖的档即抛，禁按缺省 1.0 蒙。"""
    mp = {str(k): float(v) for k, v in (cap_map or {}).items()}
    s = pd.Series(levels).astype(str)
    unknown = sorted({str(v) for v in s.dropna().unique() if str(v) not in mp})
    if unknown:
        raise _ToolError(f"级别序列含卡面映射未覆盖的档 {unknown}（禁替卡面拍档值）", {"levels": unknown})
    return s.map(mp).astype(float)


def _whipsaw_roundtrips(caps: pd.Series, window: int = _WHIPSAW_WINDOW_TRADING_DAYS) -> tuple[int, int]:
    """返回 (window 个交易日内的升降往返次数, 降档触发次数)。

    往返＝相邻两次**反向**的档位变动（先降后升或先升后降），且两腿间隔 ≤ window 交易日；
    降档（cap 变小）＝风控层"触发一次"，即卡面分母"关臂触发次数"在档位面上的读法。
    """
    chg = caps.astype(float).diff().dropna()
    chg = chg[chg.abs() > _CAP_EPS]
    dates = list(chg.index)
    dirs = [float(v) for v in np.sign(chg)]
    pos = {d: i for i, d in enumerate(caps.index)}
    rev = sum(
        1 for i in range(1, len(dates)) if dirs[i] != dirs[i - 1] and (pos[dates[i]] - pos[dates[i - 1]]) <= window
    )
    return int(rev), int(sum(1 for v in dirs if v < 0))


def _crisis_misses(caps_open: pd.Series, spans: list[tuple[str, str]]) -> tuple[int, list[dict]]:
    """危机段漏触发：逐段判开臂是否出现"风控动作发生"（当日仓位上限 < 1.0）。
    段内无读数 ⇒ 同样计一次漏触发（不可判不得当确认证据，fail-closed 同 n≥200 那条先例）。"""
    missed = 0
    detail: list[dict] = []
    for s, e in spans:
        seg = caps_open.loc[str(s) : str(e)]
        if seg.empty:
            missed += 1
            detail.append({"span": f"{s}..{e}", "n": 0, "triggered": False, "note": "段内无读数（不可判≠确认）"})
            continue
        hit = bool((seg.astype(float) < 1.0 - _CAP_EPS).any())
        if not hit:
            missed += 1
        detail.append({"span": f"{s}..{e}", "n": int(len(seg)), "triggered": hit})
    return int(missed), detail


_ARM_CONTEXT_KEYS = (
    "maxdd_improvement_vs_no_hysteresis_min_pp",
    "whipsaw_roundtrip_ratio_max",
    "missed_crisis_trigger_max",
)


def _crisis_spans(card: dict) -> list[tuple[str, str]]:
    """卡面 window.regimes 里所有 crisis 段的全段解析（统一用裁修后的 _span_pairs，禁第二把尺）。"""
    spans: list[tuple[str, str]] = []
    for seg_name, span in (card.get("window", {}).get("regimes") or {}).items():
        if "crisis" in str(seg_name).lower():
            spans.extend(_span_pairs(span))
    return spans


def _pillar_no_hysteresis_gain(p: dict, m: dict, readings: dict, owned: list, is_mid_pair: bool) -> list[str]:
    """柱一：迟滞带增益。只在"基臂＝无迟滞那档"的那跑评（裁定甲①的机读归属）。"""
    if not is_mid_pair:
        readings["maxdd_improvement_vs_no_hysteresis_pp"] = None
        owned.append("maxdd_improvement_vs_no_hysteresis_min_pp")
        return []
    thr = float(p["maxdd_improvement_vs_no_hysteresis_min_pp"])
    imp = m.get("maxdd_improvement_pp")
    if imp != imp:
        return ["maxdd_improvement_vs_no_hysteresis nan（配对 NAV 面无读数）"]
    readings["maxdd_improvement_vs_no_hysteresis_pp"] = float(imp)
    if float(imp) < thr:
        return [f"迟滞带增益 {imp:.2f}pp < {thr}"]
    return []


def _pillar_whipsaw(p: dict, readings: dict, owned: list, is_mid_pair: bool) -> list[str]:
    """柱二：30 交易日窗内升降往返 ÷ 基臂降档触发次数；分母 0 记败（不可判不得当通过）。"""
    if not is_mid_pair:
        readings["whipsaw_roundtrip_ratio"] = None
        owned.append("whipsaw_roundtrip_ratio_max")
        return []
    thr = float(p["whipsaw_roundtrip_ratio_max"])
    if readings["base_downgrades"] == 0:
        return ["whipsaw 分母为 0（基臂无降档触发＝无从比，不可判记败）"]
    ratio = float(readings["open_roundtrips_30d"]) / float(readings["base_downgrades"])
    readings["whipsaw_roundtrip_ratio"] = ratio
    if ratio > thr:
        return [f"whipsaw 往返/触发 {ratio:.3f} > {thr}"]
    return []


def _pillar_crisis_misses(p: dict, card: dict, caps_open: pd.Series, readings: dict) -> list[str]:
    """柱三：危机段漏触发。两跑共用同一条开臂级别序列，故本跑即判、不归另一跑。"""
    thr = int(p["missed_crisis_trigger_max"])
    missed, detail = _crisis_misses(caps_open, _crisis_spans(card))
    readings["crisis_spans"] = detail
    readings["missed_crisis_triggers"] = missed
    if missed > thr:
        return [f"危机段漏触发 {missed} > {thr}（段明细见 arm_face_readings.crisis_spans）"]
    return []


def _judge_arm_context_pillars(
    card: dict, m: dict, p: dict, arm_context: dict | None
) -> tuple[list[str], dict, list[str]]:
    """三柱判读的装配腿（每柱各自成函数，违 §5.158 循环复杂度反模式者不入本仓）。

    返回 (fails, readings, owned_by_other_run)。`owned_by_other_run`=本跑不判但归另一跑的键
    （裁定甲"两跑合议"的机读凭据，纯观测零否决权）；缺 arm_context 时**不**记成"归其他跑"
    而是显式记败——静默跳过就是假绿。
    """
    keys = [k for k in _ARM_CONTEXT_KEYS if k in p]
    if not keys:
        return [], {}, []
    if not isinstance(arm_context, dict) or not (arm_context.get("levels") or {}):
        reason = (
            f"三柱臂上下文未注入: {sorted(keys)}（判官不自取底座——须由绑定层 arm_context 交级别序列；"
            "缺注入如实记败，禁静默跳）"
        )
        return [reason], {"arm_context_present": False}, []
    readings: dict[str, object] = {
        "arm_context_present": True,
        "base_arm_cfg": arm_context.get("base_arm_cfg"),
    }
    try:
        caps_open = _cap_series(arm_context["levels"]["open"], arm_context["cap_map"]["open"])
        caps_base = _cap_series(arm_context["levels"]["base"], arm_context["cap_map"]["base"])
    except _ToolError as exc:  # 档位装不下＝序列与卡面映射不同源，如实记败不猜
        return [f"臂上下文档位校验失败: {exc}"], readings, []
    rev_open, downs_open = _whipsaw_roundtrips(caps_open)
    rev_base, downs_base = _whipsaw_roundtrips(caps_base)
    readings.update(
        {
            "open_roundtrips_30d": rev_open,
            "open_downgrades": downs_open,
            "base_roundtrips_30d": rev_base,
            "base_downgrades": downs_base,
            "n_days_open": int(len(caps_open)),
        }
    )
    # 迟滞对照与否＝绑定层**申报**的档位属性，不是本件按档名猜的字符串：
    # 复位档叫 levels_no_hysteresis_with_reset，按 == "levels_no_hysteresis" 匹配会读成"非无迟滞档"
    # ⇒ 三柱静默不判（假绿）。缺申报位同样如实记败，禁"没申报就当不用判"。
    if "base_is_no_hysteresis" not in arm_context:
        return (
            [
                "臂上下文未申报基臂迟滞属性（arm_context.base_is_no_hysteresis 缺位）："
                f"{sorted(keys)} 三柱无从判读，禁按档名字符串猜档，如实记败"
            ],
            readings,
            [],
        )
    is_mid_pair = bool(arm_context["base_is_no_hysteresis"])
    readings["base_is_no_hysteresis"] = is_mid_pair
    readings["open_is_no_hysteresis"] = bool(arm_context.get("open_is_no_hysteresis"))
    owned: list[str] = []
    fails: list[str] = []
    if "maxdd_improvement_vs_no_hysteresis_min_pp" in p:
        fails += _pillar_no_hysteresis_gain(p, m, readings, owned, is_mid_pair)
    if "whipsaw_roundtrip_ratio_max" in p:
        fails += _pillar_whipsaw(p, readings, owned, is_mid_pair)
    if "missed_crisis_trigger_max" in p:
        fails += _pillar_crisis_misses(p, card, caps_open, readings)
    return fails, readings, owned


def _comparison_metrics(sig_open: pd.Series, sig_base: pd.Series, target: pd.Series, card: dict) -> dict:
    """对照/消融配对面：双臂各自 IC 面（复用 _series_metrics）+ NAV 回放面 + 配对差。

    开臂/基臂共用同一目标与窗（paired_arm_protocol：仅信号处理异，零行循环差异）。"""
    mo_open = _series_metrics(sig_open, target, card)
    mo_base = _series_metrics(sig_base, target, card)
    nav_open = _arm_nav_metrics(sig_open, target)
    nav_base = _arm_nav_metrics(sig_base, target)
    rt = _round_trip_cost_bp()
    tier = card.get("pillars_numeric", {}).get("cost_tier_bp_required")
    nav_open_tier = _arm_nav_metrics(sig_open, target, cost_bp=float(tier)) if tier else None
    icd = mo_open.get("ic_mean") - mo_base.get("ic_mean")
    icd = icd if icd == icd else float("nan")
    icd_oos = mo_open.get("oos_ic") - mo_base.get("oos_ic")
    icd_oos = icd_oos if icd_oos == icd_oos else float("nan")
    return {
        "arm_open": {k: v for k, v in mo_open.items() if k != "bucket_medians"} | {"nav": nav_open},
        "arm_base": {k: v for k, v in mo_base.items() if k != "bucket_medians"} | {"nav": nav_base},
        "maxdd_improvement_pp": (nav_base["maxdd"] - nav_open["maxdd"]) * 100.0,
        "sharpe_delta": nav_open["sharpe"] - nav_base["sharpe"],
        "turnover_delta_annual_x": nav_open["turnover_annual_x"] - nav_base["turnover_annual_x"],
        "open_sharpe_at_tier_bp": nav_open_tier["sharpe"] if nav_open_tier else float("nan"),
        "ic_delta_is": icd,
        "ic_delta_oos": icd_oos,
        "round_trip_cost_bp": rt,
    }


def _judge_comparison(card: dict, m: dict, arm_context: dict | None = None) -> tuple[str, list[str]]:
    """对照/消融判（并集词表：配对侧键在配对面上评，校准侧五柱在**开臂** IC 面上评；两侧都不认＝fail-closed）。

    统筹 03:3x 裁定①扩面：混形卡（卡面同时冻了 NAV 柱与 mono/ic/regime/oos 柱）的另一侧门柱
    从此有判官接手，不再被"这族不该有这键"的偶然挡在词表外。取臂＝开臂（arm_open＝被测装置那一臂），
    该选择入册留痕，禁事后换臂。"""
    p = card.get("pillars_numeric")
    if not p:
        raise _ToolError("卡缺 pillars_numeric（冻结判据机判面）", {"card_id": card.get("card_id")})
    unknown = set(p) - _UNION_PILLAR_KEYS
    fails: list[str] = []
    if unknown:
        fails.append(f"未支持判据键（机判面待扩）: {sorted(unknown)}")
    if "misfire_reduction_min" in p:
        # 误清率面需"卖出后再创新高"笔级价格面（W4 绑定层），本核 NAV/IC 面不可判——如实记败不冒判
        fails.append(f"misfire_reduction_min 无机判面（缺笔级价格面，W4 绑定层后重考）: {p['misfire_reduction_min']}")
    imp = m.get("maxdd_improvement_pp")
    if imp == imp:
        if imp < float(p.get("maxdd_improvement_min", float("-inf"))):
            fails.append(f"maxdd_improvement {imp:.2f}pp < {p.get('maxdd_improvement_min')}")
        det = -imp
        if det > float(p.get("maxdd_deterioration_max_pp", float("inf"))):
            fails.append(f"maxdd_deterioration {det:.2f}pp > {p.get('maxdd_deterioration_max_pp')}pp")
    elif "maxdd_improvement_min" in p:
        fails.append("maxdd_improvement nan（NAV 面样本不足）")
    sd = m.get("sharpe_delta")
    if sd == sd:
        if sd < float(p.get("sharpe_delta_min", float("-inf"))):
            fails.append(f"sharpe_delta {sd:.3f} < {p.get('sharpe_delta_min')}")
    elif "sharpe_delta_min" in p:
        fails.append("sharpe_delta nan（NAV 面样本不足）")
    td = m.get("turnover_delta_annual_x")
    if td == td:
        if td > float(p.get("turnover_delta_annual_max", float("inf"))):
            fails.append(f"turnover_delta {td:.2f}x > {p.get('turnover_delta_annual_max')}x")
    tier_s = m.get("open_sharpe_at_tier_bp")
    if tier_s == tier_s and p.get("cost_tier_bp_required"):
        if tier_s < 0.0:
            fails.append(f"open_sharpe@{p['cost_tier_bp_required']}bp {tier_s:.3f} < 0.0")
    if p.get("oos_same_sign"):
        d_is, d_oos = m.get("ic_delta_is"), m.get("ic_delta_oos")
        if d_is == d_is and d_oos == d_oos and d_is != 0:
            if (d_oos > 0) != (d_is > 0):
                fails.append(f"oos_sign_flip ic_delta oos={d_oos:.4f} is={d_is:.4f}")
        else:
            fails.append("oos_sign_flip ic_delta nan（配对 IC 面样本不足）")
    # 并集词表（裁定①）：混形卡的校准侧柱子在开臂 IC 面上评。oos_same_sign 除外——
    # 它在对照卡上的冻结语义＝"配对 IC 差的 OOS 与 IS 同号"，上面那条规则就是它的真身，
    # 再按单信号语义评一遍＝同一键两套判据，禁。
    # 裁定③三柱（级别序列时序形状面）：读数与"本跑不判哪柱"一并写进 metrics，
    # 分数册行因此自带凭据（run_card 的 metrics 透传，仅剔 bucket_medians），审计可复核不靠散文。
    ac_fails, ac_readings, ac_owned = _judge_arm_context_pillars(card, m, p, arm_context)
    fails.extend(ac_fails)
    m["arm_face_readings"] = ac_readings
    m["arm_pillars_owned_by_other_run"] = ac_owned
    cal_face = {k: v for k, v in p.items() if k in _CALIBRATION_JUDGED_KEYS and k != "oos_same_sign"}
    if cal_face:
        fails.extend(_judge_calibration_face(cal_face, m.get("arm_open") or {}, sample_gate=False))
    return ("pass", []) if not fails else ("fail", fails)


#: 并集词表（统筹 03:3x 裁定①）：双臂判官现在也认校准侧五柱（在开臂 IC 面上评），
#: 混形卡的另一侧门柱从此有判官接手；两侧都不认的越表键仍由未知键 fail-closed 点名。
_UNION_PILLAR_KEYS = frozenset(_COMPARISON_KNOWN_KEYS | _CALIBRATION_JUDGED_KEYS)
#: 配对侧**专有**键（去掉两词表共有的 oos_same_sign）：路由只认这些键＝"这张卡确有只能配对算的柱子"。
#: 不减共有键的话，一张纯校准卡会因带 oos_same_sign 被误送双臂（实测由 test_calibration_* 抓住）。
_NAV_ONLY_PILLAR_KEYS = frozenset(_COMPARISON_KNOWN_KEYS - _CALIBRATION_JUDGED_KEYS)

#: 事件开关判官词表（矿考日班 T1·"判据形态换事件开关卡"；族内唯一真源，路由与普查件共用，禁第二份）
_EVENT_KNOWN_KEYS = frozenset(
    {
        "event_gap_min_bp",
        "event_t_stat_min",
        "event_gap_max_bp",
        "event_t_stat_max",
        "event_days_min",
        "event_oos_gap_same_sign",
        "event_regime_gap_same_sign",
    }
)


def pillars_route(card: dict) -> str:
    """判官路由唯一真源：只看卡面冻结的门柱键集，**不看 family**（统筹 2026-10-11 03:3x 裁定①扩面）。

    'dual_arm'＝双臂 NAV 判官（_judge_comparison）：键集⊄校准词表 **且** 至少命中一个配对侧**专有**键（_NAV_ONLY_PILLAR_KEYS）
      ——即卡面确实有只有配对面能算的柱子；两词表共有的 oos_same_sign 不算；混形卡（校准键＋NAV 键）也进本支，
      其校准侧柱子由 _judge_comparison 在**开臂** IC 面上评（开臂＝被测装置那一臂；卡面无从二选一，
      取臂选择随裁定入册留痕，禁事后换臂）。
    'event'＝事件开关判官（judge_event：事件日 vs 非事件日次日收益差＋Welch t，IS/OOS 两窗＋牛熊分列）：
      键集含事件专有键（_EVENT_KNOWN_KEYS）且不含配对侧键——含 NAV 柱者优先双臂（配对面也出 gap 类读数，
      禁两头抢判官）；
    'series'＝校准判官（judge，series/panel 两条面）：键集全韦校准词表；键集为空（缺面错由 judge()
      报准，不给它编一个"需双臂"的假错）；以及**纯越表卡**（一个配对侧键都没有，
      如 CAR t 统计/独立观测数那一类）——送去双臂只会先报"需双臂接线"这条假错，
      留在校准判官则由未知键 fail-closed 诚实点名"机判面待扩"。
    扩面前 comparison/ablation 之外带 NAV 键的卡（实测＝shadow 14＋calibration 33 张）一律走校准判官
    被未知键拦下，扩面后它们的 NAV 侧柱子改由双臂判官接手，要出分须给双臂接线（signal_b），
    缺接线＝硬报错不冒判。run_card 与词表普查共用本函数，禁抄第二份。"""
    pn = set(card.get("pillars_numeric") or {})
    if not pn:
        return "series"
    if pn <= _CALIBRATION_JUDGED_KEYS:
        return "series"
    if pn & _NAV_ONLY_PILLAR_KEYS:
        return "dual_arm"
    if pn & _EVENT_KNOWN_KEYS:
        return "event"
    return "series"


def _judge_calibration_face(p: dict, m: dict, *, sample_gate: bool = True) -> list[str]:
    """校准侧五柱的机判面＝唯一实现（judge() 的单信号面与 _judge_comparison() 的并集词表共用，禁抄第二份）。

    每柱先问"卡面冻没冻这个键"——没冻就不评（旧形态是无条件取 p[...]，卡面少给一键就抛 KeyError
    崩整批）；冻了而当前面无从评估（None/NaN）不在此处放行，由分数行 unjudged 面显形。"""
    fails: list[str] = []
    mono = m.get("mono_spearman")
    ic = m.get("ic_mean")
    if "mono_spearman_min" in p and mono is not None and mono == mono:
        if float(mono) < float(p["mono_spearman_min"]):
            fails.append(f"mono_spearman {mono:.3f} < {p['mono_spearman_min']}")
    if "ic_mean_min" in p and ic == ic:
        if float(ic) < float(p["ic_mean_min"]):
            fails.append(f"ic_mean {ic:.4f} < {p['ic_mean_min']}")
    ir = m.get("ic_ir")
    if "ic_ir_min" in p and ir is not None and ir == ir:
        if float(ir) < float(p["ic_ir_min"]):
            fails.append(f"ic_ir {ir:.3f} < {p['ic_ir_min']}")
    if p.get("regime_same_sign"):
        seg = m.get("regime_ic") or {}
        vals = [v for v in seg.values() if v == v]
        if len(vals) >= 2 and len({v > 0 for v in vals}) > 1:
            fails.append(f"regime_sign_flip {seg}")
    oos = m.get("oos_ic")
    if p.get("oos_same_sign") and oos == oos:
        base_ic = ic if (ic == ic) else 0.0
        if base_ic != 0 and (oos > 0) != (base_ic > 0):
            fails.append(f"oos_sign_flip oos={oos:.4f} is={base_ic:.4f}")
    if sample_gate:
        # 样本充分性闸（历史继承，只在单信号面用）：双臂面另有自己的配对 nan 闸
        # （ic_delta nan），混形卡再叠一层＝给卡面没冻的柱加门柱＝抬高门柱，禁。
        if oos != oos:
            fails.append("oos_ic nan（OOS 窗样本不足）")
        ic_valid = ic == ic
        mono_valid = mono is not None and mono == mono
        if not ic_valid and not mono_valid:
            fails.append("无有效主指标（ic/mono 均 nan——样本不足或信号恒定）")
    return fails


def judge(card: dict, m: dict) -> tuple[str, list[str]]:
    """pillars_numeric 机械判（执行器零裁量，一票否决）。"""
    p = card.get("pillars_numeric")
    if not p:
        raise _ToolError("卡缺 pillars_numeric（冻结判据机判面）", {"card_id": card.get("card_id")})
    unknown = set(p) - set(_CALIBRATION_JUDGED_KEYS)
    if unknown:
        # 未知冻结键=本判官机判面不覆盖该柱 ⇒ fail-closed（comparison 族 _judge_comparison 同款，
        # 统筹 01:35 批复②步骤②："还卡面冻结判据以真意，不是改门柱"）。
        # 立即定败且不再往下评估：旧形态一是该键静默跳过、pass 冒充"门柱全过"（在册假绿面），
        # 二是只有未知键的卡走到 p["mono_spearman_min"] 取数面抛 KeyError 崩整批（异常代替判决）。
        return "fail", [f"未支持判据键（机判面待扩，fail-closed）: {sorted(unknown)}"]
    fails = _judge_calibration_face(p, m)
    return ("pass", []) if not fails else ("fail", fails)


def _welch_t(a: np.ndarray, b: np.ndarray) -> float:
    """Welch 两样本 t（不等方差）＝事件面显著性唯一实现（禁第二真源）。

    仓内另有三处一次性脚本各抄了一遍 Welch/`ttest_ind`（validate_p0_discmination 等），
    本函数是考试族内的正源；一次性驱动器日后再收编（§4.2 同域重复簇→收敛唯一），本班不代改他人件。
    scipy 不引入（族内零新依赖）：t = (mean_a − mean_b) / sqrt(va/na + vb/nb)，方差的自由度不校正
    （大样本 n≥200 门槛下与 Welch 渐近同值，卡面不要求 p 值精确到小样本校正）。"""
    na, nb = int(len(a)), int(len(b))
    if na < 2 or nb < 2:
        return float("nan")
    va, vb = float(np.var(a, ddof=1)), float(np.var(b, ddof=1))
    den = (va / na + vb / nb) ** 0.5
    if den == 0.0:
        return float("nan")
    return float((float(np.mean(a)) - float(np.mean(b))) / den)


def _event_face(sig: pd.Series, nxt: pd.Series, lo: str = "", hi: str = "", *, mask=None) -> dict:
    """(窗内) 事件日 vs 非事件日的次日收益差面：gap_bp/t/n（缺窗或样本为零→nan 不冒判）。

    `mask` 给定时按掩码取段（regime 多段串用 `_in_spans` 并段，裁修 2026-10-13）；
    否则按 lo/hi 单窗，与旧行为逐字同路径。"""
    df = pd.concat({"e": sig, "r": nxt}, axis=1).dropna()
    if mask is not None:
        # 掩码按调用方的序列索引算出，而 df 是 dropna 后的对齐面（长度可差 1）——按标签重对齐再切，
        # 禁按位置硬切（实测错位＝Item wrong length 4000 instead of 3999）
        df = df[mask.reindex(df.index, fill_value=False).to_numpy(dtype=bool)]
    else:
        df = df[(df.index >= pd.Timestamp(lo)) & (df.index <= pd.Timestamp(hi))]
    ev = df.loc[df["e"] > 0, "r"].to_numpy(dtype=float)
    ne = df.loc[df["e"] <= 0, "r"].to_numpy(dtype=float)
    if len(ev) == 0 or len(ne) == 0:
        return {
            "n_event": int(len(ev)),
            "n_none": int(len(ne)),
            "mean_event": float("nan"),
            "mean_none": float("nan"),
            "gap_bp": float("nan"),
            "t_stat": float("nan"),
        }
    me, mn = float(np.mean(ev)), float(np.mean(ne))
    return {
        "n_event": int(len(ev)),
        "n_none": int(len(ne)),
        "mean_event": me,
        "mean_none": mn,
        "gap_bp": (me - mn) * 10000.0,
        "t_stat": _welch_t(ev, ne),
    }


def _event_metrics(signal: pd.Series, target: pd.Series, card: dict) -> dict:
    """事件开关面：t 日事件标记对 t+1 日目标收益（与 series 路 PIT 同口径，禁在此处换对齐）。"""
    sig = signal.sort_index()
    tgt = target.sort_index().shift(-1)
    w = card.get("window") or {}
    is_w = w.get("in_sample") or []
    oos_w = card.get("oos_window_ref") or w.get("oos") or []
    if len(is_w) != 2 or len(oos_w) != 2:
        raise _ToolError(
            "事件卡需 window.in_sample 与 oos_window_ref（或 window.oos）各两日期", {"card_id": card.get("card_id")}
        )
    full = _event_face(sig, tgt, str(sig.index.min().date()), str(sig.index.max().date()))
    seg: dict[str, dict] = {}
    for name, span in (w.get("regimes") or {}).items():
        seg[name] = _event_face(sig, tgt, mask=_in_spans(sig.index, span))
    out = {
        "gap_bp": full["gap_bp"],
        "t_stat": full["t_stat"],
        "n_event": full["n_event"],
        "n_none": full["n_none"],
        "mean_event": full["mean_event"],
        "mean_none": full["mean_none"],
        "is_gap_bp": _event_face(sig, tgt, str(is_w[0]), str(is_w[1]))["gap_bp"],
        "oos": _event_face(sig, tgt, str(oos_w[0]), str(oos_w[1])),
        "regime_gap": seg,
        "windows": {"is": [str(is_w[0]), str(is_w[1])], "oos": [str(oos_w[0]), str(oos_w[1])]},
    }
    return out


def judge_event(card: dict, m: dict) -> tuple[str, list[str]]:
    """事件开关判（族内零裁量，一票否决；未知键 fail-closed 与两族同款）。

    分母门槛（统筹日班令：事件日 n≥200）＝**族内下限**，卡面只能往严不能往松：
    卡面写了更低的 event_days_min 也按 200 拦（写进 reason，禁静默放宽）。"""
    p = card.get("pillars_numeric")
    if not p:
        raise _ToolError("卡缺 pillars_numeric（冻结判据机判面）", {"card_id": card.get("card_id")})
    unknown = set(p) - set(_EVENT_KNOWN_KEYS)
    if unknown:
        return "fail", [f"未支持判据键（事件面待扩，fail-closed）: {sorted(unknown)}"]
    fails: list[str] = []
    floor = max(200, int(p.get("event_days_min", 200)))
    n_ev = int(m.get("n_event") or 0)
    if "event_days_min" in p and n_ev < floor:
        fails.append(f"事件日样本 {n_ev} < 门槛 {floor}（族内下限 200，卡面往松不采）")
    gap_is = m.get("is_gap_bp")
    if "event_gap_min_bp" in p:
        if gap_is != gap_is:
            fails.append("is_gap_bp nan（IS 窗事件面不足）")
        elif gap_is < float(p["event_gap_min_bp"]):
            fails.append(f"is_gap_bp {gap_is:.2f}bp < {p['event_gap_min_bp']}")
    gap_max = p.get("event_gap_max_bp")
    if gap_max is not None:
        # 反向命题（事件日次日更差）用**上界**表达：要求 gap ≤ 上界，禁把方向反过来重定义键义
        if gap_is != gap_is:
            fails.append("is_gap_bp nan（IS 窗事件面不足）")
        elif gap_is > float(gap_max):
            fails.append(f"is_gap_bp {gap_is:.2f}bp > {gap_max}（负向命题要求更负）")
    ts = m.get("t_stat")
    ts_max = p.get("event_t_stat_max")
    if ts_max is not None:
        if ts != ts:
            fails.append("t_stat nan（两组方差为零或样本不足）")
        elif ts > float(ts_max):
            fails.append(f"t_stat {ts:.3f} > {ts_max}（负向命题要求更显著）")
    if "event_t_stat_min" in p:
        if ts != ts:
            fails.append("t_stat nan（两组方差为零或样本不足）")
        elif ts < float(p["event_t_stat_min"]):
            fails.append(f"t_stat {ts:.3f} < {p['event_t_stat_min']}")
    oos_n = int((m.get("oos") or {}).get("n_event") or 0)
    if p.get("event_oos_gap_same_sign") and oos_n < floor:
        # 族内下限同样套在**被用来确认的那一窗**上：OOS 只有 79-104 个事件日时，"OOS 同号"不构成确认
        fails.append(f"oos 窗事件日 {oos_n} < 门槛 {floor}（确认窗同样受族内下限约束，禁小窗冒确认）")
    oos = (m.get("oos") or {}).get("gap_bp")
    if p.get("event_oos_gap_same_sign") and oos_n >= floor:
        if oos != oos or gap_is != gap_is:
            fails.append("oos_gap nan（OOS 窗事件面不足，同号无从判）")
        elif gap_is != 0 and (oos > 0) != (gap_is > 0):
            fails.append(f"oos_gap 反号 oos={oos:.2f}bp is={gap_is:.2f}bp")
    if p.get("event_regime_gap_same_sign"):
        vals = [v.get("gap_bp") for v in (m.get("regime_gap") or {}).values() if v.get("gap_bp") == v.get("gap_bp")]
        if len(vals) < 2:
            fails.append(f"regime 有效段 {len(vals)} <2（牛熊分列无从判）")
        elif len({v > 0 for v in vals}) > 1:
            fails.append(f"regime_gap 反号 {m.get('regime_gap')}")
    return ("pass", []) if not fails else ("fail", fails)


def _declared_local_faces(card: dict) -> tuple[object, object]:
    """卡面申报的本地序列装载：data_binding.derived_series（信号侧，class D 同名）＋target_series（目标侧）。

    两键都可缺省；只申报一侧则另一侧仍为 None，由调用方按既有口径 fail-closed。
    装载口复用 card_binding.load_named_series（同一 SERIES_DIR 与同一列名规则），本函数零新读盘面。
    """
    # 导入次序＝先包内相对再包名绝对：本件被 `scripts.backtest.fexam.*` 与 `fexam.*` 两侧分别导入时，
    # 相对导入总能拿到**调用方同一个** card_binding 模块对象（在册教训：同名两导＝类身份与
    # monkeypatch 双面分裂，arm_protocol_binding 的 _arm_protocol_module 注释即此坑的既有案卷）。
    try:
        from .card_binding import load_named_series as _load
    except ImportError:
        try:
            from fexam.card_binding import load_named_series as _load  # noqa: F401
        except ImportError:
            return None, None
    b = card.get("data_binding") or {}
    return (_load(b.get("derived_series")), _load(b.get("target_series")))


def run_card(
    card_path: str | Path,
    *,
    signal=None,
    signal_b=None,
    target=None,
    arm_context: dict | None = None,
    force: bool = False,
    run_id: str | None = None,
    recorded_by: str = "calibration_exam",
    scores_path: Path = SCORES_PATH,
    ledger_registry_path: Path | None = None,
) -> dict:
    card = yaml.safe_load(Path(card_path).read_text(encoding="utf-8"))
    status = card.get("status")
    if status != "preregistered" and not force:
        raise _ToolError("卡状态非 preregistered：只考 preregistered 卡（重考带 --force）", {"status": status})
    kind = card.get("signal_kind")
    if kind not in ("panel", "series"):
        raise _ToolError("卡缺 signal_kind", {"card_id": card.get("card_id")})
    if signal is None or target is None:
        # 卡面申报了本地序列名（class D 同形制，物化件=scripts/audit/agg8_series_materialize.py）时按申报装载；
        # 未申报或件不在＝照旧抛（缺省路径与既有考卷行为逐字不变，禁"装载不到就当作零"静默出分）。
        sig2, tgt2 = _declared_local_faces(card)
        signal = sig2 if signal is None else signal
        target = tgt2 if target is None else target
    if signal is None or target is None:
        raise RuntimeError(
            "缺省 CH 取数面未接（signal_spec/target_spec 绑定属 W4 运行期配置）——"
            "请注入 signal/target 或先行落绑定册（防误绑数据面）"
        )
    family = card.get("family")
    # 判官按判据键分派（W-A 臂协议配方面 2026-10-10 三连裁③v2）：路由判据本体见 pillars_route()——
    # 该函数是 run_card 与门柱词表普查（card_binding --mode vocab-census）的唯一共用真源，禁两处各抄。
    used_nav = pillars_route(card) == "dual_arm"
    if used_nav:
        # 双臂配对分支（夜矿续战三连裁② 2026-10-10 并入本执行核；03:3x 裁定①后按门柱键集进本支，
        # 与 family 无关——calibration/shadow 族带 NAV/笔级柱的卡同样要在这里配双臂）
        if signal_b is None:
            raise _ToolError(
                "判据键含 NAV/笔级面（双臂配对面）⇒ 需双臂信号：signal=开臂（或全量臂），"
                "signal_b=基臂（或消融臂）；缺双臂接线＝不出分",
                {"card_id": card.get("card_id"), "family": family, "route": "dual_arm"},
            )
        m = _comparison_metrics(signal, signal_b, target, card)
        verdict, fails = _judge_comparison(card, m, arm_context)
    elif used_nav is False and pillars_route(card) == "event":
        m = _event_metrics(signal, target, card)
        verdict, fails = judge_event(card, m)
    else:
        m = _series_metrics(signal, target, card) if kind == "series" else _panel_metrics(signal, target, card)
        verdict, fails = judge(card, m)
    pillars_all_pass = verdict == "pass"
    if used_nav:
        oos_ok = (m.get("ic_delta_oos") == m.get("ic_delta_oos")) and not any("oos" in f for f in fails)
        seg = m.get("arm_open", {}).get("regime_ic") or {}
    elif pillars_route(card) == "event":
        oos_ok = ((m.get("oos") or {}).get("gap_bp") == (m.get("oos") or {}).get("gap_bp")) and not any(
            "oos" in f for f in fails
        )
        seg = {k: v.get("gap_bp") for k, v in (m.get("regime_gap") or {}).items()}
    else:
        oos_ok = (m.get("oos_ic") == m.get("oos_ic")) and not any("oos" in f for f in fails)
        seg = m.get("regime_ic") or {}
    regimes = [k for k, v in seg.items() if v == v]
    # 未判柱观测面（裁定②步骤①，纯观测零否决权）：每行分数自带"只代表哪些键"，禁把 4-5 键 pass 叙述成门柱全过
    _vocab = (
        _UNION_PILLAR_KEYS
        if used_nav
        else _EVENT_KNOWN_KEYS
        if pillars_route(card) == "event"
        else _CALIBRATION_JUDGED_KEYS
    )
    unjudged = _unjudged_pillars(card, m, _vocab)
    row = {
        "card_id": card["card_id"],
        "node_id": card["node_id"],
        "run_id": run_id or f"examcard-{_date.today().isoformat()}",
        "kind": "exam",
        "verdict": verdict,
        "pillars_all_pass": pillars_all_pass,
        "oos_ok": bool(oos_ok),
        "regimes": regimes,
        "date": _date.today().isoformat(),
        "metrics": {k: v for k, v in m.items() if k != "bucket_medians"},
        "unjudged": unjudged,
        "fails": fails,
    }
    # 分数册 only-add 追加
    sp = Path(scores_path)
    if sp.exists():
        # 双文档 register 兼容（裁定#536 迁移形态）：doc0=register 头，含 rows 的 doc 为账本本体
        docs = [d for d in yaml.safe_load_all(sp.read_text(encoding="utf-8")) if isinstance(d, dict)] or [{}]
        reg = next((d for d in docs if d.get("rows") is not None), docs[-1])
        rows = reg.get("rows") or []
    else:
        reg = {"schema_version": "1.0", "title": "考试卡分数册（成绩汇总面，方案 §6 D4）", "rows": []}
        docs = [reg]
        rows = reg["rows"]
    rows.append(row)
    reg["rows"] = rows
    sp.parent.mkdir(parents=True, exist_ok=True)
    dump = (
        yaml.safe_dump_all(docs, allow_unicode=True, sort_keys=False, width=140)
        if len(docs) > 1
        else yaml.safe_dump(reg, allow_unicode=True, sort_keys=False, width=140)
    )
    sp.write_text(dump, encoding="utf-8", newline="\n")
    # 卡面更新：status=examined + lineage 指针
    card["status"] = "examined"
    card.setdefault("lineage", {})
    card["lineage"]["run_id"] = row["run_id"]
    card["lineage"]["score_row"] = f"exam_scores_v1.yaml#rows[{len(rows) - 1}]"
    Path(card_path).write_text(
        yaml.safe_dump(card, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n"
    )
    # 试次记账（DSR 分母强制面）
    try:
        from zephyr.backtest.core.n_trial_ledger import TrialLedger

        TrialLedger(registry_path=ledger_registry_path).record_run(
            kind="exam_card",
            batch_id=f"examcard:{card['card_id']}:{row['date']}",
            n_trials=1,
            note=f"verdict={verdict}",
            recorded_by=recorded_by,
        )
    except Exception as e:  # noqa: BLE001 — 台账失败不吞考试结果，但必须留痕
        row["ledger_warning"] = str(e)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--card", required=True)
    ap.add_argument("--signal-csv", help="信号 csv（index=date；series 用 value 列，panel 用宽表）")
    ap.add_argument("--signal-b-csv", help="对照/消融基臂（或消融臂）信号 csv（comparison/ablation 卡必带）")
    ap.add_argument("--target-csv", help="目标 csv（index=date，value 列）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    sig = tgt = sig_b = None
    if args.signal_csv:
        s = pd.read_csv(args.signal_csv, index_col=0, parse_dates=True)
        sig = s.iloc[:, 0] if isinstance(s, pd.Series) is False and s.shape[1] == 1 else s
    if args.signal_b_csv:
        sb = pd.read_csv(args.signal_b_csv, index_col=0, parse_dates=True)
        sig_b = sb.iloc[:, 0] if sb.shape[1] == 1 else sb
    if args.target_csv:
        t = pd.read_csv(args.target_csv, index_col=0, parse_dates=True)
        tgt = t.iloc[:, 0]
    row = run_card(args.card, signal=sig, signal_b=sig_b, target=tgt, force=args.force)
    print(json.dumps(row, ensure_ascii=False, indent=2, default=str))
    return 0 if row["verdict"] == "pass" else 1


# 人工CLI设计如此（同域MOD-BT-197先例）：按TDM变更/分数册更新/逐卡开考人工触发，非永久自动系统面
if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  人工CLI（同域MOD-BT-197先例），非永久自动系统
    sys.exit(main())
