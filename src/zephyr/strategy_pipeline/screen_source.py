# [BLUEPRINT] MOD-BT-191 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.screen_source
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; scripts.backtest.strategy_screen_query(DECAY_SUSPECT 土规真源);
#   scripts.backtest.auto_mount(翻译件加载); scripts.backtest.translated._c4_engine(经 sys.path 注入)
# [CONSUMERS] zephyr.strategy_pipeline.intake（run_intake_auto 数据源）; 验收⑥历史批回放
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 台账只读（本模块禁写 strategy_screen）；两职分离（勿混）：
#   ①批次身份/可复现——哪一行的 is_sharpe 出自哪个冻结窗，是行事实、不可改：及格判定口径与
#     strategy_screen_query.cmd_bothwin 一字不差（IS 冻结批 ∧ verdict=translated_c4 联查全部
#     oos_tested，键=strategy_id+source_file）。三向 parity 只约束此职（静默延长该窗会毁配对）。
#   ②活估计/统计输入——p 值分母 n（年数）按行取被检验统计量自身的记录窗（notes 的 window=…/…，
#     缺省回退 IS 冻结窗），统计量与其样本必须同窗；禁把模块级 IS_WIN 当"当前窗"通配。
#     相关矩阵=描述今日相关结构供下游聚类/分配，窗终点随快照表最新可用日动态前移
#     （锚 IS_WIN[0]+动态末−PIT_TAIL_LAG，仿 auto_mount.build(IS_WIN_START,end)），故不受①的 parity 约束。
#   p 值=t 双侧检验解析式（SR_ann·sqrt(年数) 的渐近正态），族=当批及格全集（BH 语义）；
#   相关矩阵只算及格集两两 ρ（日净收益 inner 对齐，重叠<60 日=0 不聚类——宁漏勿误）；
#   三轴启发式只影响差异化论证与挂图类别的"新条目初值"，真源仍是注册表既有字段（只增不改）
# [MODIFY-GUARD] tests/strategy_pipeline/test_screen_source.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(台账不可达/翻译件缺 build 契约经 auto_mount 原样上抛)
# [TESTS] tests/strategy_pipeline/test_screen_source.py
# [A_module] module_id=MOD-BT-191 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] screen-source-mod-bt-191-20260915
"""screen_source——C6 管线的台账数据源：及格集/ρ 相关矩阵/p 值/三轴初值（只读）。

验收⑥回放与本班 run_intake_auto 的共同数据底座；查询语义与 strategy_screen_query.cmd_bothwin
（MOD-BT-078）完全一致，本模块只是把"人看的 JSON 报告"变成"管线消费的结构化行"。
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
IS_BATCH = "C4-translated-20260912"          # 冻结 IS 批（bothwin 真源同款，批次身份不可改）
# IS_WIN=冻结 IS 批的产生窗。仅两用途：①批次身份记录；②行无记录窗时的回退默认。
# 任何"当前估计"路径（活 ρ 矩阵终点 / 逐行 p 值 n）禁把它当"当前窗"直读（见 [INVARIANTS] 两职分离）。
IS_WIN = ("2020-01-01", "2023-12-31")
SNAP_TABLE = "c1_backtest.regime_snapshot_history"  # 交易日历/快照真源（窗口天数与 auto_mount 判定同源）
PIT_TAIL_LAG = 1                            # 活窗尾窗回退行数：尾日证据未定不入样（仿 auto_mount）
MIN_CORR_OVERLAP_DAYS = 60                   # 重叠不足不判相关（宁漏勿误）
DECAY_SUSPECT = 0.5                          # 回退值；运行时优先取 strategy_screen_query 真源

# 三轴启发式词表（信号轴）：模块源码/文件名关键词 → strategy_class（CLASS_NODE_MAP 子集，保证可挂图）
# 权重=出现次数计分；文件名锚（tsmall/bias 等专名）权重 ×3（文件名是 C3 翻译语义的最可靠摘要）
_AXIS_KEYWORDS: dict[str, tuple[str, ...]] = {
    "value_reversal": ("bias", "乖离", "超卖", "超买", "反转", "reversal", "value", "估值", "rsrs", "zulu", "slater",
                       "meanrev", "zscore", "均值回归", "pairs", "布林", "boll"),
    "momentum_trend": ("momentum", "动量", "趋势", "trend", "dmi", "ma_cross", "双均线", "突破", "breakout",
                       "timing", "择时", "kdj", "macd", "rsi"),
    "multifactor": ("small_cap", "smallcap", "tsmall", "小市值", "micro", "蛇", "snake",
                    "pb_poe", "div", "股息", "高div", "value55"),
    "daban": ("gap", "缺口", "高开", "低开", "ultrashort", "超短"),
}

# 指标级信号指纹词表（差异化门用；ASCII 短词带词边界防误命中）
_SIGNAL_VOCAB: tuple[str, ...] = (
    "BIAS", "乖离", "RSI", "KDJ", "MACD", "DMI", "ADX", "ATR", "CCI", "OBV", "BOLL", "布林",
    "EMA", "SMA", "WMA", "HMA", "均线", "金叉", "死叉", "趋势", "动量", "反转", "反弹", "超买",
    "超卖", "恐慌", "跌幅", "缺口", "高开", "低开", "打板", "涨停", "连板", "市值", "股息", "分红",
    "ROE", "估值", "RSRS", "ZSCORE", "波动", "换手", "量能", "支撑", "压力", "突破", "排名",
    "PE", "PB", "MA", "gap", "momentum", "reversal", "meanrev", "zscore", "turnover", "volume",
)
_ASCII_TOKENS = {t for t in _SIGNAL_VOCAB if t.isascii()}


def signal_tokens(text: str) -> frozenset[str]:
    """指标级信号指纹（确定性）：文本中命中的词表项集合（ASCII 带词边界）。"""
    if not text:
        return frozenset()
    out = set()
    for tok in _SIGNAL_VOCAB:
        if tok in _ASCII_TOKENS:
            if re.search(rf"\b{re.escape(tok)}\b", text, re.IGNORECASE if tok.isalpha() else 0):
                out.add(tok.lower())
        elif tok in text:
            out.add(tok)
    return frozenset(out)


def module_signal_tokens(source_file: str) -> frozenset[str]:
    """翻译件源码的信号指纹。"""
    try:
        code = (ROOT / source_file).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return frozenset()
    return signal_tokens(code)


def entry_signal_tokens(entry: dict[str, Any]) -> frozenset[str]:
    """注册表条目的信号指纹（文本字段并集）。"""
    parts = [str(entry.get(k) or "") for k in
             ("entry_logic", "exit_logic", "name", "name_zh", "code_symbol", "doc_ref")]
    parts += [str(t) for t in (entry.get("tags") or [])]
    parts += [str(a) for a in (entry.get("aliases") or [])]
    return signal_tokens(" ".join(parts))
_CLASS_FAMILY = {  # strategy_class → STR-* 家族段（缺省 AUTO）；只收词汇表在册家族（2026-09-15 复核班对齐家族法）
    "value_reversal": "VREV", "momentum_trend": "MOMTREND", "event_driven": "EVENT", "multifactor": "MULTIFACTOR",
}


def _q(sql: str) -> list[tuple]:
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)


def _decay_suspect() -> float:
    try:
        sys.path.insert(0, str(ROOT / "scripts/backtest"))
        from strategy_screen_query import DECAY_SUSPECT as v  # noqa: PLC0415 土规真源
        return float(v)
    except Exception:  # noqa: BLE001 回退常量（DDL 注释同值）
        return DECAY_SUSPECT


def fetch_bothwin() -> list[dict[str, Any]]:
    """及格集结构化行（口径=strategy_screen_query.cmd_bothwin 一字不差）。"""
    ds = _decay_suspect()
    is_rows = _q(
        f"SELECT strategy_id, is_sharpe, source_file, turnover, notes, max_drawdown FROM c1_backtest.strategy_screen "
        f"WHERE screen_batch = '{IS_BATCH}' AND verdict = 'translated_c4'")
    oos_rows = _q(
        "SELECT strategy_id, source_file, screen_batch, is_sharpe, oos_years_decay FROM c1_backtest.strategy_screen "
        "WHERE verdict = 'oos_tested' AND is_sharpe IS NOT NULL ORDER BY screen_batch")
    oos_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for sid, sf, batch, sharpe, decay in oos_rows:
        oos_map.setdefault((sid, sf), []).append({"batch": batch, "sharpe": sharpe, "decay": decay})
    items = []
    for sid, is_sharpe, sf, turnover, notes, max_dd in is_rows:
        segments = oos_map.get((sid, sf), [])
        if not segments:
            continue
        windows_ok = (is_sharpe or 0) > 0 and all(
            (s["sharpe"] or 0) > 0 and (s["decay"] is None or s["decay"] < ds) for s in segments)
        items.append({
            "key": f"{sid}@{str(sf).rsplit('/', 1)[-1]}",
            "strategy_id": sid, "source_file": sf,
            "is_sharpe": is_sharpe, "turnover": turnover, "notes": notes,
            "max_drawdown": max_dd,
            "segments": segments, "gate_bothwin_pass": windows_ok,
        })
    return [i for i in items if i["gate_bothwin_pass"]]


_WINDOW_RE = re.compile(r"window=(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})")


def window_from_notes(notes: str | None) -> tuple[str, str] | None:
    """从台账 notes 自由文本解析该行统计量的记录窗（c4_batch_screen 落 'window=start/end; kind='）。"""
    m = _WINDOW_RE.search(notes or "")
    return (m.group(1), m.group(2)) if m else None


def window_days(start: str, end: str) -> int:
    """任意窗交易日数（regime_snapshot_history 行数口径=auto_mount 判定同源）。"""
    rows = _q(f"SELECT count() FROM {SNAP_TABLE} "
              f"WHERE trade_date >= '{start}' AND trade_date <= '{end}'")
    return int(rows[0][0])


def is_window_days() -> int:
    """冻结 IS 批默认窗天数——仅当行无记录窗时回退；不再是通配"当前窗"的单一真值。"""
    return window_days(*IS_WIN)


def sample_days_for_item(item: dict[str, Any]) -> int:
    """该行被检验统计量的自样本天数：优先其记录窗（notes window=），缺省回退 IS 冻结窗。
    配对不变量——p 值分母必须=产生该 is_sharpe 的样本，禁全局猜测（见 [INVARIANTS] ②）。"""
    win = window_from_notes(item.get("notes"))
    return is_window_days() if win is None else window_days(*win)


def p_from_sharpe(sharpe: float, days: int) -> float:
    """年化 Sharpe → 双侧 p 值（t=SR·sqrt(年数) 渐近正态；纯函数）。"""
    if days <= 0 or sharpe is None:
        return 1.0
    t = float(sharpe) * math.sqrt(days / 252.0)
    return math.erfc(abs(t) / math.sqrt(2.0))


def passing_with_p(items: list[dict[str, Any]] | None = None) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """（BH 假设族={及格 key: p}，items）。族=当批及格全集（含已入库者，防选择偏差）。
    逐行按自身记录窗取 n（同窗缓存去重，避免逐行查库）。"""
    items = fetch_bothwin() if items is None else items
    cache: dict[tuple[str, str] | None, int] = {}
    out: dict[str, float] = {}
    for i in items:
        win = window_from_notes(i.get("notes"))
        if win not in cache:
            cache[win] = sample_days_for_item(i)
        out[i["key"]] = round(p_from_sharpe(i["is_sharpe"], cache[win]), 6)
    return out, items


def _module_for(source_file: str):
    sys.path.insert(0, str(ROOT / "scripts/backtest"))
    import auto_mount  # noqa: PLC0415

    return auto_mount._load_translated_module(source_file)


def live_estimation_end() -> str:
    """活估计窗终点=快照表最新可用交易日回退 PIT_TAIL_LAG 行（仿 auto_mount.build 的动态 end）。
    尾日证据未定不入样（PIT）；无数据回退 IS 冻结终点（fail-safe，禁写死 2023-12-31）。"""
    rows = _q(f"SELECT trade_date FROM {SNAP_TABLE} WHERE trade_date >= '{IS_WIN[0]}' "
              f"ORDER BY trade_date DESC LIMIT 1 OFFSET {PIT_TAIL_LAG}")
    if not rows:
        return IS_WIN[1]
    d = rows[0][0]
    return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]


def net_window() -> tuple[str, str]:
    """ρ 矩阵日净收益估计窗：锚=IS_WIN[0]（与冻结口径可比起点），终点随可用数据动态前移。"""
    return (IS_WIN[0], live_estimation_end())


def net_returns(source_file: str):
    """翻译件活窗日净收益（经 auto_mount 加载契约=build+引擎；终点随当前数据，非冻结 2023）。"""
    sys.path.insert(0, str(ROOT / "scripts/backtest/translated"))
    import _c4_engine  # noqa: PLC0415
    import pandas as pd  # noqa: PLC0415

    mod = _module_for(source_file)
    weights, closes = mod.build(*net_window())
    net = _c4_engine.daily_net_returns(weights, closes)
    net.index = pd.to_datetime(net.index)
    return net


def corr_matrix(items: list[dict[str, Any]]) -> dict[tuple[str, str], float]:
    """及格集两两 ρ（带号 Pearson，聚类按 ρ>阈值）；逐件 gc（build 全窗回测内存峰值大）。"""
    import gc

    import pandas as pd  # noqa: PLC0415

    nets: dict[str, Any] = {}
    for i in items:
        try:
            nets[i["key"]] = net_returns(i["source_file"])
        except Exception:  # noqa: BLE001 单件回测失败=不参与聚类（宁漏勿误），不阻断批
            continue
        finally:
            gc.collect()
    out: dict[tuple[str, str], float] = {}
    keys = sorted(nets)
    for a_i, a in enumerate(keys):
        for b in keys[a_i + 1:]:
            joined = pd.concat([nets[a].rename("a"), nets[b].rename("b")], axis=1, join="inner").dropna()
            if len(joined) < MIN_CORR_OVERLAP_DAYS:
                continue
            rho = float(joined["a"].corr(joined["b"]))
            if not math.isfinite(rho):
                continue
            out[(a, b)] = round(rho, 4)
    return out


def derive_class(source_file: str) -> str:
    """信号轴启发式：翻译件源码+文件名关键词 → strategy_class（命中多族=加权计数高者，全未命中=multifactor）。

    计分=关键词出现次数；文件名命中的关键词计 3 倍（文件名是 C3 翻译语义的可靠摘要）。
    """
    path = ROOT / source_file
    try:
        code = path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        code = ""
    fname = Path(source_file).name.lower()
    hay = code + " " + fname
    scores: dict[str, int] = {}
    for cls, kws in _AXIS_KEYWORDS.items():
        s = 0
        for kw in kws:
            if kw not in hay:
                continue
            s += hay.count(kw) * (3 if kw in fname else 1)
        scores[cls] = s
    best = max(scores, key=lambda c: (scores[c], c))
    return best if scores[best] > 0 else "multifactor"


def derive_axes(source_file: str, turnover: float | None = None) -> dict[str, str]:
    """三轴初值（差异化论证+挂图类别用）：信号轴=启发式类别；周期=换手+窗口种类；状态适配=alpha。"""
    cls = derive_class(source_file)
    if turnover is not None and float(turnover) >= 1.0:
        period = "日内—次日"
    else:
        period = "波段"
    return {"signal_axis": cls, "holding_period": period, "state_adaptation": "alpha"}


def family_of(cls: str) -> str:
    return _CLASS_FAMILY.get(cls, "AUTO")


_NAME_STRIP = re.compile(r"^c4_[0-9a-f]{8,16}_")


def derive_name(source_file: str) -> str:
    """条目名初值：翻译件文件名去哈希前缀（如 c4_c72318f2da1c_bias_ql.py → bias_ql）。"""
    stem = _NAME_STRIP.sub("", Path(source_file).stem).strip("_") or Path(source_file).stem
    return stem
