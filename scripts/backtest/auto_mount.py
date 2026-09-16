# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.auto_mount
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.translated._c4_engine(经翻译件注入); zephyr.data.ch_reader; zephyr.trading.decision_map; scripts.governance.d5_architecture.generators.check_decision_map; zephyr.shared.io.file_utils; zephyr.strategy_pipeline.fw_backtest(挂图落地后 fw_backtest_due 事件); zephyr.factor.analysis.bhy_fdr(族级 FDR 官方件); zephyr.signal_ashare.core.environment_switch(六段词表真源); zephyr.regime.regime_feature_builder(BREADTH_INDEX 广度源，惰性导入)
# [CONSUMERS] C6 入库线（strategy_registry 新条目→自动挂图）; decay_watch 月度挂图审计
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 全自动 only-add（diff 净删行=拒）；宁漏勿误（段<=0 或样本<30 天不激活）；
#   地图写入=文本级手术（node_id 分块+块内唯一锚+count==1）；写后 38 规则校验；挂载必 verified+evidence（R6）；
#   判定窗终点=快照表最新可用日回退 PIT 尾窗（禁写死日期，SLE-3②）；激活放行=族级 BHY-FDR q=0.10
#   拒绝 H0 ∧ SR>0 ∧ OOS 不反向（SLE-3①）；微观相位（euphoria/distribution）让位 r10/r11 宏观冰点/复苏；
#   调权提案（SLE-1 真实分配语义）只读不落图——落图须先过 weight_adjust_assert 且经 Owner 门位；
#   行数豁免（GOV-010 分层裁量 301-500 档）：本文件=五步管线单抽象族高内聚（映射/归因/配比/手术/报告
#   共享同一组常量与手术原语，拆分=跨文件耦合+常量漂移风险），变更隔离面=管线五步同批演化
# [MODIFY-GUARD] tests/backtest/test_auto_mount.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(锚点不唯一/only-add 断言失败/38 规则校验未过/claim 缺失)
# [TESTS] tests/backtest/test_auto_mount.py
# [A_module] module_id=MOD-BT-171 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] auto-mount-mod-bt-171-20260915
"""auto_mount 自动挂图器——策略转正后自动挂上决策地图（节点+状态格子+PP-001 配比）。

五步管线（立项真源 docs/_working/2026-09-14-auto-mount-research.md §4，验收五条同 §4）：
  ① 映射表 strategy_class→node_id（SOP-C §6.2 五行规则表硬编码）
  ② 分状态回测判 activation_state：判定窗=锚点 IS_WIN_START + 快照表最新可用日回退尾窗
     （SLE-3② 解冻，禁写死终点）；r 态基础映射 R2SIX + 全市场微观情绪相位 overlay 补
     euphoria/distribution 盲区（SLE-3③）；段内 SR 单侧 t 检验→族级 BHY-FDR q=10% 拒绝
     H0 且 SR>0 且 OOS 不反向才激活（SLE-3①，宁漏勿误：段样本<30 天不测）
  ③ PP-001 配比：挂图路径=新 sleeve 0.05 观察期起步档/老 sleeve 等比缩水保 sum=1.0
     （only-add 语义门放行域）；真实分配语义=证据×风险预算提案 sleeve_weights +
     weight_adjust_assert 新语义门，--rebalance 只出 diff 不落图（SLE-1 Owner 门位）
  ④ 文本级手术写入+only-add 断言+38 规则校验（run_checks）
  ⑤ 报告：挂了哪/为什么/证据指针

r→六段映射依据（两轴口径，真源=地图 v1.2.2 Owner 裁定 B：宏观段状态=D_REGIME 7 态，
微观情绪相位=六段轴；冰点→capitulation/反核→accumulation+ignition/主升→expansion/
疯狂→euphoria/退潮→distribution）：
  基础映射（宏观腿）r10 CRISIS→capitulation；r4 熊市阴跌/r11 复苏→accumulation；
  r3 牛市趋势→expansion；r12 BREAKOUT→ignition；r1 低波/r2 中波无六段对应→不路由。
  相位 overlay（微观腿，补盲区）广度指数（BREADTH_INDEX，与 F4 涨跌家数同源）20 日均
  上涨占比 + 拉伸度双确认→euphoria；亢奋记忆窗内价格破 MA20 且广度转弱→distribution。
  设计迭代留痕（同 anchored_state_machine 惯例）：v1=000300 乖离+波动分位+HMM r3 门
  →2019-2026 仅命中 4 天，2020-07/2024-09 两处公认亢奋顶全漏（根因：HMM dominant 跨期
  label switching 致 r3 门不可靠，见裁定#229 语义复核；波动腿把低波 melt-up 一律否决）；
  v2（定稿）改微观情绪轴，r10/r11 保持优先（冰点/复苏不被微观相位覆盖）。

用法: --plan 预演只打印｜ --apply --strategy STR-A,STR-B 写入（先 claim+safe_write）｜
  --replay 幂等验收（已挂集合重放零 diff）｜ --audit 月度审计（只读）｜
  --explain 判定明细（只读：窗口/段证据/FDR/激活）｜ --rebalance 调权提案 diff（只读，永不写图）
判定缓存: .runtime/tmp/auto_mount_judge_cache.json（sid+code mtime+窗口+规则版本键控，改规则/数据后可删）
"""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # 类型注解占位（pandas 保持惰性导入，运行时零开销；防 get_type_hints 炸 pd 未定义）
    import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

REGISTRY = ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
MAP_YAML = ROOT / "config/trading_decision_map.yaml"
REPORT_DIR = ROOT / "docs/_working"
CACHE = ROOT / ".runtime/tmp/auto_mount_judge_cache.json"
# ---------- ② 判定窗（SLE-3② 解冻：锚点 + 快照表最新可用日，禁写死终点） ----------
IS_WIN_START = "2020-01-01"  # 起点锚=与 C4 冻结口径可比；终点由 snapshot_panel 动态派生（原 IS_WIN 终点写死致 2024+ 零判定）
PIT_TAIL_LAG = 1  # 尾窗回退行数：决策日只能用 ≤T-1 信息（宪法 PIT 纪律，尾日证据未定不入样）
OOS_TAIL_ROWS = 252  # 样本外子窗=判定窗末端最近 252 交易日（约 1 年，SLE-3① OOS 不反向门）
OOS_MIN_DAYS = 10  # OOS 门生效样本下限（低于此=该态在 OOS 窗内无足够证据，不据此否决罕见态）
MIN_SEG_DAYS = 30  # 宁漏勿误：段样本短于此不检验
PHASE_WARMUP_DAYS = 700  # 相位分位窗预热日历天（250 交易日滚动秩 + MA20 + 60 日收益所需左尾）
# ---------- ② 多重检验纪律（SLE-3①，真源=90 号 §2 裁定 + Harvey-Liu-Zhu） ----------
FDR_Q = 0.10  # BHY 族级 FDR 控制水平（判定族=本批全部 (sid×相位) 单侧 t 检验）
FDR_LARGE_FAMILY = 100  # 族内检验数 >100 时升级 t 门槛（90 号 §2 大批量条款）
T_STAR_HLZ = 2.8  # Harvey-Liu-Zhu (2017) 多重检验稳健门槛
# ---------- ② 微观情绪相位 overlay（SLE-3③ euphoria/distribution 盲区；全分位化无前视） ----------
PHASE_PCT_WINDOW = 250  # 250 日滚动经验分位（只用 t 及以前，无全局归一）
EUPH_BIAS_PCT = 0.90  # 乖离度（close/MA20-1）250 日分位 ≥90%
EUPH_BR20_PCT = 0.85  # 20 日上涨家数占比的 250 日分位 ≥85%（广度与拉伸双确认）
EUPH_RET_WINDOW = 60  # 亢奋需仍在上行（60 日收益 >0），排除高位破位
DIST_MEMORY = 60  # 亢奋记忆窗：亢奋后 60 日内才允许转退潮（防把常态震荡判成逃顶）
BR20_WINDOW = 20  # 上涨家数占比平滑窗（广度腿）
DIST_MA_WINDOW = 20  # 价格均线窗（微观相位的价格腿）
DIST_BR20_FLOOR = 0.50  # 退潮广度门槛：20 日上涨占比 <50% 且价格破 MA20
PHASE_PREEMPT = frozenset({"r10", "r11"})  # 宏观冰点/复苏优先（微观相位不得覆盖宏观态）
# ---------- ③ 分配语义（SLE-1 真实配比 + SLE-4 Σ 精确闭合） ----------
NEW_SLEEVE_WEIGHT = 0.05  # 新 sleeve 观察期起步档=挂图路径唯一允许值（only_add 放行域）；调权路径为下限
WEIGHT_STEP_LIMIT = 0.25  # 单次调权变动上限（相对上一版，机构再平衡带宽纪律，防一次性甩仓）
WEIGHT_GRID = 6  # 权重量化格 10^-6（与 round(,6) 同口径，最大余数法保 Σ 精确闭合）
DEFAULT_SINGLE_SLEEVE_CAP = 0.25  # 兜底单 sleeve 上限（真源=地图 portfolio_plan.aggregator.max_single_sleeve）
OBSERVATION_CONF_FACTOR = 0.5  # 非 verified 证据的置信折算（verified=1.0）
VOL_FLOOR = 0.02  # 年化波动下限（防逆波动除零/近零波动爆炸分配）
SNAPSHOT_TABLE = "c1_backtest.regime_snapshot_history"  # 品类未注册（注册 diff 见车道 B 报告，RULE-REGISTRY）
FAMILY_DEFAULT_ROUTE = {  # 家族兜底路由（真源=注册表 mount_route 字段，本表仅接住无显式路由的自动入库件）
    # S07-G2：derive_class 兜底类 multifactor 无显式路由时落打分链，不映射则挂图 skipped 永不落位。
    # 其余家族不设兜底：同族路由异构（value_reversal 既有个股反转也有指数择时），强制显式 mount_route 防误挂。
    "multifactor": "TDM-E-L3-07-2",
}
CLASS_CANDIDATE_STATES: dict[str, set[str] | None] = {  # 语义先行候选态，按分类家族键（数据只在态内裁决，禁全态海选）
    # 2026-09-16 车道 B（SLE-3③）：euphoria/distribution 自此可被检验，L1 防御格不再空转。
    # value_reversal=L1 总闸防御腿主体（panic_rebound 冰点抄底 / bias 修复 / bluechip_ma 破线离场），
    #   亢奋与退潮正是 MA/乖离择时的正超额主场 → 四态全候选；
    # daban=情绪顺周期链，地图 L4 euphoria 格早已预登记 daban-sleeve（打板=高潮段主战场），
    #   候选态据此补 euphoria；退潮/冰点按图注"不进"保持封闭；
    # momentum_trend=主升/点火两态（退潮段 DMI 类趋势件无正超额先验，不扩候选）。
    "value_reversal": {"capitulation", "accumulation", "euphoria", "distribution"},
    "momentum_trend": {"expansion", "ignition"},
    "daban": {"accumulation", "expansion", "euphoria"},
    "multifactor": None,  # 打分/选股链（TDM-E-L3-07-2/3）为选股类，无状态格
}
# 宏观态→六段基础映射（宏观腿）。盲区实锤：本表无 euphoria/distribution 行，且 r1/r2 不路由，
# 故改造前六段轴两态在实盘永不出现（L1 防御格恒空）；现由 phase_overlay 微观腿补齐。
# 注意真源漂移：framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE 是本表的组合期孪生件，
# 由守卫测试 test_r2six_drift_guard_vs_framework_composer 钉住（改动必同批，移交件见车道 B 报告）。
R2SIX = {"r10": "capitulation", "r4": "accumulation", "r11": "accumulation", "r3": "expansion", "r12": "ignition"}


def load_registry_entries() -> list[dict[str, Any]]:
    import yaml
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return [{"sid": e["strategy_id"], "cls": e["strategy_class"], "code_path": e["code_path"],
             "lifecycle": e.get("lifecycle_status"), "route": e.get("mount_route")} for e in data.get("strategies", [])
            if e.get("code_path") and e.get("strategy_class")]


def _load_translated_module(rel: str):
    path = Path(rel) if Path(rel).is_absolute() else ROOT / rel
    sys.path.insert(0, str(path.parent))
    sys.path.insert(0, str(ROOT / "scripts/backtest/translated"))  # _c4_engine 注入点（引擎与翻译件同目录）
    spec = importlib.util.spec_from_file_location(f"automount_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _cached_judge(e: dict[str, Any], panel) -> dict[str, Any]:
    """② 分相位归因（带缓存：sid+code mtime+判定窗+映射+规则版本键控）。"""
    code = Path(e["code_path"]) if Path(e["code_path"]).is_absolute() else ROOT / e["code_path"]
    key = f"{e['sid']}|{int(code.stat().st_mtime)}|{window_of(panel)}|{sorted(R2SIX)}|v4"
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    if cache.get(key):
        return cache[key]
    j = judge_activation_state(e["sid"], e["cls"], e["code_path"], panel)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    cache[key] = j
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return j


# ---------- ② 判定窗数据装载（只读经 ch_reader；表名走 TableRegistry 真源） ----------
def _tsv_df(tsv: str, cols: list[str]):
    import pandas as pd
    rows = [l.split("\t") for l in tsv.strip().split("\n") if l.strip()]
    return pd.DataFrame(rows, columns=cols)


def _snapshot_rows(start: str, end: str | None):
    """宏观态日快照（regime_snapshot_history.dominant），end=None=取到最新可用日。"""
    import pandas as pd
    from zephyr.data import ch_reader
    tail = f" AND trade_date <= toDate('{end}')" if end else ""
    tsv = ch_reader.query(f"SELECT trade_date, dominant FROM {SNAPSHOT_TABLE} "
                          f"WHERE trade_date >= toDate('{start}'){tail} ORDER BY trade_date")
    df = _tsv_df(tsv, ["td", "dom"])
    df["td"] = pd.to_datetime(df["td"])
    return df.set_index("td")


def _index_kline(symbol: str, start: str, end: str | None, *, calc: bool = False):
    """指数日线只读装载（close + 涨跌家数；GROUP BY 去重同 F4 读取口径）。"""
    import pandas as pd
    from zephyr.data import ch_reader
    from zephyr.data.table_registry import get_registry
    table = get_registry().table("market_kline_index_calc" if calc else "market_index_kline")
    tail = f" AND trade_date <= toDate('{end}')" if end else ""
    tsv = ch_reader.query(
        f"SELECT trade_date, toString(any(close)), toString(any(advance_count)), "
        f"toString(any(decline_count)) FROM {table} FINAL WHERE symbol = '{symbol}' "
        f"AND trade_date >= toDate('{start}'){tail} GROUP BY trade_date ORDER BY trade_date")
    df = _tsv_df(tsv, ["td", "close", "adv", "dec"])
    df["td"] = pd.to_datetime(df["td"])
    for c in ("close", "adv", "dec"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.set_index("td").sort_index()


def _breadth_frame(start: str, end: str | None):
    """微观相位输入：广度指数收盘 + 上涨/下跌家数（399106 主源，断更日 EQW_ALLA 补位）。

    399106 advance_count/decline_count 自 2026-07-03 结构性断更（known_data_gaps.yaml F4 登记，
    provider 侧另有车道在修）；本件按 RegimeFeatureBuilder._load_breadth 同门口径回退
    kline_index_calc 的 EQW_ALLA 全 A 家数——涨家数/(涨+跌) 比值自归一，深市与全 A 的规模差
    在比值里消去，两源按日混用不产生量纲跳变。补位缺失=该日无相位（NaN→False，宁漏勿误）。
    """
    from zephyr.regime.regime_feature_builder import BREADTH_INDEX  # noqa: PLC0415 惰性导入（重链 7s+）
    br = _index_kline(BREADTH_INDEX, start, end)
    dead = (br["adv"].fillna(0) <= 0) & (br["dec"].fillna(0) <= 0)
    if bool(dead.any()):
        fb = _index_kline("EQW_ALLA", start, end, calc=True)
        br.loc[dead, "adv"] = fb["adv"].reindex(br.index[dead])
        br.loc[dead, "dec"] = fb["dec"].reindex(br.index[dead])
    return br.dropna(subset=["close"])


def _rolling_pct(s, window: int = PHASE_PCT_WINDOW):
    """滚动经验分位 rank(pct=True)：只用 t 及以前 window 个观测（无前视），半窗后出值。"""
    return s.rolling(window, min_periods=window // 2).rank(pct=True)


def phase_overlay(breadth) -> "pd.DataFrame":
    """② 微观情绪相位探测器（SLE-3③ 盲区治本）→ DataFrame[euphoria, distribution] bool。

    亢奋（疯狂段）= 拉伸与广度双确认且仍在上行：乖离度(close/MA20-1) 250 日分位 ≥0.90
    ∧ 20 日上涨家数占比的 250 日分位 ≥0.85 ∧ 60 日收益 >0；
    退潮（派发段）= 亢奋记忆窗内（亢奋后 60 日内，shift(1) 不含当日）价格破 MA20
    ∧ 20 日上涨占比 <50%。全部腿为 trailing 窗，无全局归一、无前视。
    """
    import numpy as np
    import pandas as pd
    close = breadth["close"].astype(float)
    tot = (breadth["adv"].astype(float) + breadth["dec"].astype(float)).replace(0, np.nan)
    br = breadth["adv"].astype(float) / tot
    ma = close.rolling(DIST_MA_WINDOW).mean()
    bias = close / ma - 1.0
    br20 = br.rolling(BR20_WINDOW, min_periods=BR20_WINDOW // 2).mean()
    ret = close.pct_change(EUPH_RET_WINDOW)
    euph = (_rolling_pct(bias) >= EUPH_BIAS_PCT) & (_rolling_pct(br20) >= EUPH_BR20_PCT) & (ret > 0)
    memory = euph.astype(float).rolling(DIST_MEMORY, min_periods=1).max().shift(1) > 0
    dist = memory.fillna(False).astype(bool) & (close < ma) & (br20 < DIST_BR20_FLOOR)
    return pd.DataFrame({"euphoria": euph.astype(bool), "distribution": dist.astype(bool)})


def resolve_six_phase(dom, ov) -> "pd.Series":
    """两轴合成当日六段相位：R2SIX 宏观基础映射 ⊕ 微观相位 overlay（盲区补全）。

    优先级 PHASE_PREEMPT（r10 冰点/r11 复苏）> distribution > euphoria > 基础映射——
    宏观极端态不被微观读数覆盖（地图 v1.2.2 裁定 B：两轴各管各的，冰点就是冰点）。
    未映射宏观态（r1/r2 震荡等）→ NaN 不路由（宁漏勿误）。
    """
    base = dom.map(R2SIX)
    preempt = dom.isin(PHASE_PREEMPT)
    dist = ov["distribution"] & ~preempt
    euph = ov["euphoria"] & ~preempt & ~dist
    return base.mask(dist, "distribution").mask(euph, "euphoria")


def load_phase_panel(end: str | None = None) -> "pd.DataFrame":
    """判定窗相位面板：列=dom（宏观腿）/euphoria/distribution（微观腿）/six（合成相位）。

    窗口=[IS_WIN_START, 快照表最新可用日回退 PIT_TAIL_LAG 行]（SLE-3② 解冻：终点禁写死；
    PIT：尾日相位标签与行情证据未定稿，不入判定样本）。end 仅供复算/测试钉窗。
    """
    import pandas as pd
    snap = _snapshot_rows(IS_WIN_START, end)
    if len(snap) <= PIT_TAIL_LAG:
        raise RuntimeError(f"快照行数 {len(snap)} ≤ PIT 尾窗回退 {PIT_TAIL_LAG}，无判定样本")
    snap = snap.iloc[: len(snap) - PIT_TAIL_LAG]
    win_end = str(pd.Timestamp(snap.index[-1]).date())
    warm = str((pd.Timestamp(snap.index[0]) - pd.Timedelta(days=PHASE_WARMUP_DAYS)).date())
    ov = phase_overlay(_breadth_frame(warm, win_end)).reindex(snap.index)
    ov = ov.fillna(False).astype(bool)  # 广度缺失日=无微观相位（不判亢奋/退潮，保守）
    six = resolve_six_phase(snap["dom"], ov)
    return pd.concat([snap["dom"].rename("dom"), ov, six.rename("six")], axis=1)


def load_dominant():
    """判定窗相位面板（历史名保留=调用面契约：intake/CLI 把返回值直传 _plan_inserts）。

    2026-09-16 车道 B（SLE-3②③）改造前：返回冻结 2020-01-01..2023-12-31 的 dominant Series，
    2024+ 零判定且 euphoria/distribution 永不出现；现返回动态窗六段相位面板。
    """
    return load_phase_panel()


def _t_one_sided_p(t: float, n: int) -> float:
    """单侧 t 检验尾概率 P(T≥t)（H1: 均值>0），Hill(1970) t→z 近似，纯 math 零 scipy：
    z = t(1-1/(4ν))/√(1+t²/(2ν))，ν=n-1；ν≥25 时绝对误差 <1e-3（本件 ν≥29）。"""
    if n < 2:
        return 1.0
    nu = n - 1
    z = t * (1.0 - 1.0 / (4.0 * nu)) / math.sqrt(1.0 + t * t / (2.0 * nu))
    return float(0.5 * math.erfc(z / math.sqrt(2.0)))


def _seg_stats(ret) -> dict[str, float]:
    """段内日净收益统计：样本数 + 年化 SR + 年化波动 + 单侧 t/p（SR_ann·√(n/252) 同 t）。"""
    import numpy as np
    n = int(len(ret))
    sd = float(ret.std(ddof=1)) if n > 1 else 0.0
    mu = float(ret.mean()) if n else 0.0
    sr = mu / sd * np.sqrt(252.0) if sd > 0 else 0.0
    t = mu / sd * np.sqrt(float(n)) if sd > 0 and n > 1 else 0.0
    return {"n": n, "sr": round(sr, 4), "vol": round(sd * np.sqrt(252.0), 4), "t": round(t, 4),
            "p": round(_t_one_sided_p(t, n), 6)}


def judge_activation_state(sid: str, cls: str, code_path: str, panel) -> dict[str, Any]:
    """② 分相位归因（原始证据，未过 FDR 门）；选股类 candidates=None→全段（activation_state=null）。

    相位列=resolve_six_phase 合成六段（R2SIX ⊕ 微观 overlay），罕见相位自此可被检验；
    每段另算 OOS 子窗（窗末 OOS_TAIL_ROWS 交易日）SR，供 SLE-3① 不反向门；
    full=全窗 SR/年化波动，供 ③ 真实分配（风险预算）。段样本 <MIN_SEG_DAYS 不检验（宁漏勿误）。
    """
    import pandas as pd
    mod = _load_translated_module(code_path)
    import _c4_engine  # noqa: PLC0415 经 translated 目录注入
    end = str(pd.Timestamp(panel.index[-1]).date())
    weights, closes = mod.build(IS_WIN_START, end)
    net = _c4_engine.daily_net_returns(weights, closes)
    net.index = pd.to_datetime(net.index)
    joined = pd.concat([net.rename("net"), panel[["six"]]], axis=1, join="inner").dropna()
    full = _seg_stats(joined["net"]) if len(joined) >= MIN_SEG_DAYS else {}
    cands = CLASS_CANDIDATE_STATES.get(cls, set())
    if cands is None:  # 选股/打分链：无相位假设（activation_state=null），但仍出分配证据
        return {"sid": sid, "activated": None, "segments": {}, "full": full}
    oos_cut = panel.index[-OOS_TAIL_ROWS] if len(panel) >= OOS_TAIL_ROWS else panel.index[0]
    segs: dict[str, Any] = {}
    for six in sorted(cands & set(panel["six"].dropna().unique())):
        sub = joined[joined["six"] == six]["net"]
        if len(sub) < MIN_SEG_DAYS:
            continue
        st = _seg_stats(sub)
        oos = sub[sub.index >= oos_cut]
        st.update({"oos_n": int(len(oos)), "oos_sr": _seg_stats(oos)["sr"] if len(oos) >= 2 else 0.0})
        segs[six] = st
    return {"sid": sid, "activated": sorted(s for s, v in segs.items() if v["sr"] > 0),
            "segments": segs, "full": full}


def apply_multiple_testing(judgements: list[dict[str, Any]], *, q: float = FDR_Q) -> dict[str, Any]:
    """② 族级多重检验纪律（SLE-3①）：本批全部 (sid×相位) 单侧 t 检验合并成判定族。

    放行条件（四者皆真才进 activated）：
      ① BHY-FDR q 拒绝 H0（任意依赖稳健，真源=90 号 §2）——治"分段挑最优"的多重比较膨胀；
      ② SR>0（方向）；③ 族规模 >FDR_LARGE_FAMILY 时加 Harvey-Liu-Zhu t≥T_STAR_HLZ 升级门槛；
      ④ OOS 子窗样本 ≥OOS_MIN_DAYS 时不得反向（OOS SR<0 即否）——样本少到没法判时不据此
         否决罕见相位（否则等于把 SLE-3② 解冻的尾部样本又冻回去）。
    就地改写各 judgement 的 segments（补 qvalue/fdr_rejected/accepted/reason）与 activated，
    返回族级回执（报告/审计用）。纯统计零 IO。
    """
    from zephyr.factor.analysis.bhy_fdr import bh_qvalues, bhy_fdr
    judged = [j for j in judgements if isinstance(j.get("activated"), list)]  # 选股类(=null)不入族
    tests = [(j, s) for j in judged for s in sorted(j.get("segments") or {})]
    m = len(tests)
    receipt: dict[str, Any] = {"m": m, "q": q, "threshold": 0.0, "n_rejected": 0, "hlz": m > FDR_LARGE_FAMILY}
    for j in judged:
        j["activated"] = []
    if not m:
        return receipt
    res = bhy_fdr([j["segments"][s]["p"] for j, s in tests], q=q)
    qv = bh_qvalues([j["segments"][s]["p"] for j, s in tests])
    receipt.update({"threshold": round(res.threshold, 6), "n_rejected": int(res.n_rejected)})
    for (j, s), rej, qq in zip(tests, res.rejected, qv):
        st = j["segments"][s]
        st.update({"qvalue": round(float(qq), 6), "fdr_rejected": bool(rej), "accepted": False})
        why = []
        if not rej:
            why.append(f"p={st['p']:.4g}>FDR 临界 {res.threshold:.4g}(q={q},m={m})")
        if st["sr"] <= 0:
            why.append(f"SR={st['sr']:+.2f}≤0")
        if receipt["hlz"] and st["t"] < T_STAR_HLZ:
            why.append(f"大族 t={st['t']:.2f}<{T_STAR_HLZ}")
        if st["oos_n"] >= OOS_MIN_DAYS and st["oos_sr"] < 0:
            why.append(f"OOS 反向 SR={st['oos_sr']:+.2f}({st['oos_n']}d)")
        st["accepted"] = not why
        st["reject_reason"] = "; ".join(why)
        if st["accepted"]:
            j["activated"].append(s)
    for j in judgements:
        if isinstance(j.get("activated"), list):
            j["activated"] = sorted(j["activated"])
    return receipt


def _apportion(total: float, weights: dict[str, float], grid: int = WEIGHT_GRID) -> dict[str, float]:
    """最大余数法：缩放到 total 并量化到 10^-grid，Σ 精确闭合（SLE-4 round(,6) 漂移治本）。

    空/非正输入退化为等分（不抛）；份额按余数大小逐个补/扣，结果确定性可重放。
    """
    unit = 10.0 ** -grid
    refs = list(weights)
    if not refs:
        return {}
    vals = [max(0.0, float(weights[r])) for r in refs]
    s = sum(vals)
    if s <= 0:
        vals = [1.0] * len(refs)
        s = float(len(refs))
    raw = [v * total / s for v in vals]
    units = [int(math.floor(r / unit + 1e-9)) for r in raw]
    rem = int(round(total / unit)) - sum(units)
    order = sorted(range(len(refs)), key=lambda i: -(raw[i] - units[i] * unit))
    i = 0
    while rem > 0 and order:
        units[order[i % len(order)]] += 1
        rem, i = rem - 1, i + 1
    while rem < 0:
        k = max(range(len(refs)), key=lambda j_: units[j_])
        units[k] -= 1
        rem += 1
    return {refs[k]: round(units[k] * unit, grid) for k in range(len(refs))}


def sleeve_plan(new_refs: list[str], old: list[dict[str, Any]]) -> dict[str, float]:
    """③ 挂图路径配比（only-add 放行域）：新 sleeve 各 0.05 观察档，老 sleeve 等比缩水保 Σ=1。

    SLE-4 治本两点：①老权重经 round(,6) 后 Σ 不再精确=1 → 改 _apportion 最大余数法精确闭合；
    ②退化分支——老集合权重和为 0（空图首挂）时新 sleeve 等分预算（不再 scale=0 静默丢权）；
    新 sleeve 数超过观察档总预算（0.05×n≥1）时明确报错要求分批，不静默把老权重压成负。
    """
    keep = sum(float(x["weight"]) for x in old)
    budget = NEW_SLEEVE_WEIGHT * len(new_refs)
    if new_refs and budget >= 1.0:
        raise ValueError(f"新 sleeve {len(new_refs)} 条 × 观察档 {NEW_SLEEVE_WEIGHT} 总权重 {budget:.2f}≥1"
                         "——超单批预算，须分批转正（挂图侧保留老权重下限）")
    if keep <= 0:
        # 空图/全零权：无老权重可缩，候选 ref 等分全预算（Σ=1 精确；0.05 起步档规则让步）
        return _apportion(1.0, {r: 1.0 for r in (new_refs or [x["strategy_ref"] for x in old])})
    out = _apportion(1.0 - budget, {x["strategy_ref"]: float(x["weight"]) for x in old})
    out.update({r: NEW_SLEEVE_WEIGHT for r in new_refs})
    return out


def _evidence_scores(prev: dict[str, float], evidence: dict[str, dict[str, Any]]
                     ) -> tuple[list[str], dict[str, float]]:
    """证据→分配分数：score = 正超额 SR × 置信 ÷ 年化波动（风险预算口径，归一前）。

    无正超额/退役 ref 不入分数表（=不参与分配）；置信 verified=1.0，其余 OBSERVATION_CONF_FACTOR。
    返回 (参与分配的 ref 全集, score 表)。
    """
    universe = list(dict.fromkeys(list(prev) + [r for r, ev in evidence.items() if not ev.get("retired")]))
    score: dict[str, float] = {}
    for r in universe:
        ev = evidence.get(r) or {}
        sr = float(ev.get("sr") or 0.0)
        if sr <= 0 or ev.get("retired"):
            continue
        vol = max(float(ev.get("vol") or 0.0), VOL_FLOOR)
        conf = 1.0 if str(ev.get("confidence", "")) == "verified" else OBSERVATION_CONF_FACTOR
        score[r] = sr * conf / vol
    return universe, score


def sleeve_weights(old: list[dict[str, Any]], evidence: dict[str, dict[str, Any]], *,
                   cap: float = DEFAULT_SINGLE_SLEEVE_CAP, floor: float = NEW_SLEEVE_WEIGHT,
                   step: float = WEIGHT_STEP_LIMIT, grid: int = WEIGHT_GRID) -> dict[str, float]:
    """③ 真实分配语义提案（SLE-1）：w ∝ 正超额证据 × 置信 ÷ 年化波动（风险预算口径）。

    与 sleeve_plan 的分工（关键，别混）：本函数=**提案面**（--rebalance 只出 diff，落图须过
    weight_adjust_assert + Owner 门位）；sleeve_plan=**挂图面**（only-add 语义门放行域内）。
    证据来源 evidence[sid]={sr, vol, confidence, retired}（judge_activation_state 汇编）。
    约束链：观察期下限 floor → 按比例水填至单 sleeve 上限 cap → 步长带 |Δw|≤step（防一次性甩仓）
    → 无证据/未过门的老 sleeve 权重冻结，等比承接残差（Σ=1 恒等式要求，非裁量）→ _apportion 精确闭合。
    逆波动折算=风险平价分配（Maslov 等实践的 risk-budget 口径），非"谁历史收益高给谁"的收益追逐。
    """
    prev = {x["strategy_ref"]: float(x["weight"]) for x in old}
    universe, score = _evidence_scores(prev, evidence)
    eligible = sorted(score, key=lambda k: -score[k])
    frozen = {r: prev.get(r, 0.0) for r in universe if r not in score and prev.get(r, 0.0) > 0}
    pool = 1.0 - sum(frozen.values())
    if pool <= 0 or not eligible:
        return _apportion(1.0, frozen or {r: prev[r] for r in prev})
    if len(eligible) * min(floor, pool / len(eligible)) > pool + 1e-12:
        raise ValueError(f"不可行：{len(eligible)} 条证据 sleeve × 观察下限 {floor} > 可用预算 {pool:.4f}")
    alloc = {r: 0.0 for r in eligible}
    rest = pool
    for r in eligible:  # 1) 观察期下限保底（高分优先）
        g = min(floor, rest)
        alloc[r], rest = g, rest - g
    pending = list(eligible)
    while rest > 1e-12 and pending:  # 2) 按分数比例分配 + 触顶水填
        tot = sum(score[r] for r in pending)
        shares = {r: rest * score[r] / tot for r in pending}
        hit = [r for r in pending if alloc[r] + shares[r] > cap + 1e-12]
        if hit:
            for r in hit:
                rest -= cap - alloc[r]
                alloc[r] = cap
            pending = [r for r in pending if r not in hit]
        else:
            for r in pending:
                alloc[r] += shares[r]
            rest = 0.0
    for r in eligible:  # 3) 步长带（相对上一版）
        base = prev.get(r, 0.0)
        alloc[r] = min(max(alloc[r], base - step), min(cap, base + step))
    resid = 1.0 - sum(frozen.values()) - sum(alloc.values())
    if frozen and abs(resid) > 1e-12:  # 4) 残差等比落回无证据组（Σ=1 恒等式）
        s = sum(frozen.values()) or 1.0
        frozen = {r: max(0.0, w + resid * w / s) for r, w in frozen.items()}
    out = {**frozen, **alloc}
    return _apportion(1.0, out, grid)


def weight_adjust_assert(before: dict[str, float], after: dict[str, float], *,
                         cap: float = DEFAULT_SINGLE_SLEEVE_CAP, step: float = WEIGHT_STEP_LIMIT,
                         floor: float = NEW_SLEEVE_WEIGHT, tol: float = 1e-6) -> None:
    """③ 调权语义门（SLE-1 新增，不动 only_add 语义门）：分配提案的自证伪断言。

    校四件事：Σ=1（容差 1e-6）；单 sleeve ∈[0,cap]；存量 ref |Δw|≤step；新 ref ∈[floor,cap]；
    ref 只增不减（删除须先经 SLE-2 退役通道置 0，不在此门静默消失）。
    与 only_add_assert 的关系：后者管"地图写入只增不减+等比"，本门管"权重是否是有证据的分配"，
    两道门语义正交——真实调权必然过不了 only_add，这正是 SLE-1 要 Owner 开新门位的原因。
    """
    s = sum(after.values())
    assert abs(s - 1.0) <= tol, f"调权门：Σw={s:.8f}≠1（容差 {tol}）"
    for r, w in after.items():
        assert 0.0 - tol <= w <= cap + tol, f"调权门：{r} 权重 {w} 越界 [0,{cap}]"
    for r, w in before.items():
        assert r in after, f"调权门：{r} 被静默移除（退役须显式置 0 并经 SLE-2 通道）"
        assert math.isclose(after[r], w, abs_tol=tol) or abs(after[r] - w) <= step + tol, \
            f"调权门：{r} 单步变动 {after[r] - w:+.4f} 超带宽 ±{step}"
    for r, w in after.items():
        if r not in before and w > tol:
            assert w >= floor - tol, f"调权门：新 ref {r} 权重 {w} 低于观察期下限 {floor}"


# ---------- ④ 文本级手术（node_id 分块+唯一锚+count==1） ----------
def _split_blocks(text: str) -> dict[str, tuple[int, int]]:
    starts = [(m.start(), m.group(1)) for m in re.finditer(r"(?m)^- node_id: (\S+)", text)]
    return {nid: (s, starts[i + 1][0] if i + 1 < len(starts) else len(text)) for i, (s, nid) in enumerate(starts)}


def _patch_block(text: str, node_id: str, new_block: str) -> str:
    s, e = _split_blocks(text)[node_id]
    out = text[:s] + new_block.rstrip("\n") + "\n" + text[e:]
    assert len(_split_blocks(out).get(node_id, ())) == 2, f"patch 后块不唯一: {node_id}"
    return out


def insert_node_mount(text: str, node_id: str, sid: str, evidence: str) -> str:
    block = text[_split_blocks(text)[node_id][0]:_split_blocks(text)[node_id][1]]
    assert f"strategy_ref: {sid}" not in block, f"{node_id} 已挂 {sid}"
    anchor = "  strategy_mounts:\n"
    assert block.count(anchor) == 1, f"strategy_mounts 锚不唯一: {node_id}"
    lines = block.splitlines(keepends=True)
    i = lines.index(anchor) + 1
    while i < len(lines) and lines[i].lstrip().startswith("- {strategy_ref"):
        i += 1
    lines.insert(i, f"  - {{strategy_ref: {sid}, confidence: verified, evidence: '{evidence}'}}\n")
    return _patch_block(text, node_id, "".join(lines))


def insert_cell(text: str, node_id: str, state: str, sid: str) -> str:
    """原位拼接：仅在指定状态格的 mounted [] 内追加 sid（多行折行格子安全）。

    2026-09-16 复核班治本：旧实现无 state 参数、向该节点全部格子扩散插入（docstring
    自述"全部格子"），VREV-027 因此污染 ignition/euphoria/distribution 三格（其证据
    states=accumulation+capitulation）。state-aware 化后一格一插，误插由守卫测试拦截。
    """
    pat = rf"(?m)^  - \{{node_id: {re.escape(node_id)}, state: {re.escape(state)}, mounted: \["
    hits = list(re.finditer(pat, text))
    assert len(hits) == 1, f"state 格不唯一或缺失: {node_id}/{state} hits={len(hits)}"
    m = hits[0]
    # 括号配对找真闭括号（防多行折行格子把 ] 落在下一行）
    depth, i = 1, m.end()
    while depth:
        ch = text[i]
        depth += (ch == "[") - (ch == "]")
        i += 1
    close = i - 1
    inner = text[m.end():close]
    assert sid not in [x.strip() for x in inner.split(",")], f"格子已含 {sid}（op 应先查重）"
    if not inner.strip():
        ins, pos = sid, close  # 空数组：] 前直插
    else:
        ins = f", {sid}"
        j = close  # 回退到最后一个非空白字符之后插入
        while j > m.end() and text[j - 1] in " \t\r\n":
            j -= 1
        pos = j
    return text[:pos] + ins + text[pos:]


def insert_sleeve(text: str, sid: str, activation: list[str] | None) -> str:
    act = "null" if not activation else "[" + ", ".join(activation) + "]"
    line = f"  - {{strategy_ref: {sid}, weight: {NEW_SLEEVE_WEIGHT}, activation_state: {act}}}"
    anchor = "  sleeves:\n"
    assert text.count(anchor) == 1, "sleeves 锚不唯一"
    s = text.index(anchor) + len(anchor)
    seg_end = text.index("\n\n", s) if "\n\n" in text[s:] else len(text)
    hits = list(re.finditer(r"(?m)^  - \{strategy_ref: STR-", text[s:seg_end]))
    assert hits, "sleeves 无 STR- 行可锚"
    eol = text.index("\n", s + hits[-1].start()) + 1  # 最后一条 STR- sleeve 行尾=插入位（追加语义）
    return text[:eol] + line + "\n" + text[eol:]


def only_add_assert(before: str, after: str) -> None:
    """红蓝门（语义级）：挂载/格子/证据只增不减不改；sleeve 只增不减、老权重仅允许全局等比缩水
    （立项 §4③设计行为）、新 sleeve 必 0.05 起步。伪造删行/改证据/非等比改权重必被拒。"""
    import math
    import yaml
    b, a = yaml.safe_load(before), yaml.safe_load(after)

    def mounts(dm):
        return {n["node_id"]: {(m["strategy_ref"], m.get("confidence"), m.get("evidence"))
                                 for m in (n.get("strategy_mounts") or [])} for n in dm["nodes"]}

    bm, am_ = mounts(b), mounts(a)
    for nid, ms in bm.items():
        assert ms <= am_.get(nid, set()), f"only-add 违规：节点挂载被删/改 {nid}"

    def cells(dm):
        sm = dm.get("state_matrix") or {}
        return {(c["node_id"], c["state"]): (tuple(c.get("mounted") or []), c.get("confidence"))
                for c in (sm.get("cells") or [])}

    bc, ac = cells(b), cells(a)
    for k, (mounted, conf) in bc.items():
        ak = ac.get(k)
        assert ak, f"only-add 违规：格子被删 {k}"
        assert set(mounted) <= set(ak[0]), f"only-add 违规：格子挂载被删/改 {k}"
        assert conf == ak[1], f"only-add 违规：格子 confidence 被改 {k}"

    def sleeves(dm):
        return {s["strategy_ref"]: float(s["weight"]) for s in dm["portfolio_plan"]["sleeves"]}

    bs, as_ = sleeves(b), sleeves(a)
    for ref in bs:
        assert ref in as_, f"only-add 违规：sleeve 被删 {ref}"
    scales = [as_[ref] / w for ref, w in bs.items() if w > 0]
    if not scales:
        return  # 空图/全零权 bootstrap：无等比基准可比（sleeve_plan 走等分分支）；删行已在上面被拒，此路不可达伪造
    s0 = scales[0]
    assert all(math.isclose(s, s0, rel_tol=2e-3) for s in scales), "only-add 违规：老 sleeve 权重非等比变动"
    for ref, w in as_.items():
        if ref not in bs:
            assert abs(w - NEW_SLEEVE_WEIGHT) < 1e-9, f"新 sleeve 起步档违规 {ref}={w}"


def validate_map() -> list[str]:
    gdir = str(ROOT / "scripts/governance/d5_architecture/generators")
    if gdir not in sys.path:
        sys.path.insert(0, gdir)
    from check_decision_map import run_checks
    fails, _warns, _total = run_checks(map_path=MAP_YAML, registry_dir=None)  # registry_dir 缺省=仓内 _registry 真源
    return fails


# ---------- 管线编排 ----------
def mounted_sids(text: str) -> set[str]:
    return set(re.findall(r"(?m)^  - \{strategy_ref: (STR-[\w-]+), confidence:", text))


def window_of(panel) -> str:
    """判定窗可读标签（SLE-3②：终点=快照表最新可用日回退尾窗，动态派生禁写死）。"""
    import pandas as pd
    return f"{IS_WIN_START}..{pd.Timestamp(panel.index[-1]).date()}"


def _judge_batch(entries: list[dict[str, Any]], panel, only: set[str] | None
                 ) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    """② 批量判定 + 族级多重检验门（编排/报告/审计共用；判定缓存让重复调用零成本）。

    返回 (带 FDR 回执的 judgements, 族级 receipt, skipped)。BHY 的判定族=本批 (sid×相位)
    检验集合，批口径不同则阈值不同（--strategy 子集比全表宽松）——正式判定以全表
    --plan/--explain 为准，子集批仅作单条排障。
    """
    pipeline = [e for e in entries if "/translated/c4_" in e["code_path"].replace("\\", "/")]
    skipped = [f"{e['sid']}: code_path 非 C4 翻译件（无 build 契约）" for e in entries if e not in pipeline]
    if only is not None:
        pipeline = [e for e in pipeline if e["sid"] in only]
    judgements: list[dict[str, Any]] = []
    for e in pipeline:
        j = dict(_cached_judge(e, panel))
        j.update({"cls": e["cls"], "code_path": e["code_path"],
                  "node": e.get("route") or FAMILY_DEFAULT_ROUTE.get(e["cls"])})
        judgements.append(j)
    return judgements, apply_multiple_testing(judgements, q=FDR_Q), skipped


def _plan_inserts(entries: list[dict[str, Any]], panel, only: set[str] | None
                  ) -> tuple[list[dict[str, Any]], str, str, list[str]]:
    """②③④ 编排：判定（含 FDR 门）→ 待插清单 → 权重方案；返回 (ops, 地图原文, 权重 JSON, skipped)。

    签名三位参数=调用面契约（intake._auto_mount_sids 与 CLI 共用），panel 由 load_dominant 产。
    """
    text = MAP_YAML.read_text(encoding="utf-8")
    import yaml
    sleeves = yaml.safe_load(text)["portfolio_plan"]["sleeves"]
    have_sleeve = {x["strategy_ref"] for x in sleeves}
    judgements, receipt, skipped = _judge_batch(entries, panel, only)
    win = window_of(panel)
    ops: list[dict[str, Any]] = []
    for j in judgements:
        sid, node, act = j["sid"], j["node"], j["activated"]
        block = text[_split_blocks(text)[node][0]:_split_blocks(text)[node][1]] if node else ""
        if node and f"strategy_ref: {sid}" not in block:
            evidence = (f"auto_mount {win} states={'+'.join(act) or '-'} FDR q={FDR_Q}"
                        f"/m={receipt['m']}/rej={receipt['n_rejected']}; code={j['code_path']}").replace("'", "")
            ops.append({"kind": "node_mount", "node_id": node, "sid": sid, "evidence": evidence[:150]})
        if act and node:
            for st in act:
                m = re.search(rf"(?m)^  - \{{node_id: {re.escape(node)}, state: {st}, mounted: \[([^\]]*)\]", text)
                if m and sid not in [x.strip() for x in m.group(1).split(",")]:
                    ops.append({"kind": "cell", "node_id": node, "state": st, "sid": sid})
        if sid not in have_sleeve:
            # activation_state=null 语义=全段激活（地图注记③）：择时类一条相位都没过门时禁授
            # null，否则"无证据"反拿最大敞口——宁漏勿误在此落地（选股类 cands=None 才是合法 null）
            if act or CLASS_CANDIDATE_STATES.get(j["cls"]) is None:
                ops.append({"kind": "sleeve", "sid": sid, "activation": act})
            else:
                skipped.append(f"{sid}: 候选相位无一过 FDR 门→不建 sleeve（免误授全段激活）")
    new_refs = [o["sid"] for o in ops if o["kind"] == "sleeve"]
    plan = sleeve_plan(new_refs, sleeves) if new_refs else {}
    if new_refs:
        ops.append({"kind": "rescale", "plan": plan})
    return ops, text, json.dumps(plan, ensure_ascii=False), skipped


def rescale_sleeves(text: str, plan: dict[str, float]) -> str:
    """权重原位替换（逐 sleeve 改 weight 字段）。数值=固定 6 位小数去尾零（禁 %g：1e-06 类
    小权重会写成科学计数法，本函数 sleeve 行正则再也匹不上，二次 rescale 直接断言失败）。"""
    out = text
    for ref, w in plan.items():
        pat = rf"(?m)^(  - \{{strategy_ref: {re.escape(ref)}, weight: )(\d+(?:\.\d+)?)(,)"
        m = re.search(pat, out)
        assert m, f"rescale 找不到 sleeve 行: {ref}"
        out = out[:m.start(2)] + f"{w:.6f}".rstrip("0").rstrip(".") + out[m.end(2):]
    return out


def apply_ops(ops: list[dict[str, Any]], before: str) -> str:
    text = before
    for op in ops:
        if op["kind"] == "node_mount":
            text = insert_node_mount(text, op["node_id"], op["sid"], op["evidence"])
        elif op["kind"] == "cell":
            text = insert_cell(text, op["node_id"], op["state"], op["sid"])
        elif op["kind"] == "sleeve":
            text = insert_sleeve(text, op["sid"], op["activation"])
        elif op["kind"] == "rescale":
            text = rescale_sleeves(text, op["plan"])
    return text


def mount_audit(scan_frequency: str | None = "monthly") -> dict[str, Any]:
    """月度挂图审计（钩子②）：只读三件套——地图 38 规则回执+衰减巡检同口径分档结果+挂载一致性盘点。

    挂接语义（对齐 decay_watch §调度挂载裁定）：审计函数无 IO 副作用，既可手动触发，
    也可被 decay_watch 同节奏调用方复用；不新建调度器（禁 cron/Timer，宪法 §9.3）。
    挂载一致性=格子 mounted 里的 STR-* 必须也在节点挂载区（防两边漂移）。
    """
    import yaml
    text = MAP_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    fails = validate_map()
    cells = data.get("state_matrix", {}).get("cells") or []
    node_mounted = {n["node_id"]: {m["strategy_ref"] for m in (n.get("strategy_mounts") or [])}
                    for n in data.get("nodes", [])}
    drift: list[str] = []
    for c in cells:
        nid = c.get("node_id", "")
        for sid in (c.get("mounted") or []):
            if str(sid).startswith("STR-") and sid not in node_mounted.get(nid, set()):
                drift.append(f"{nid}:{c.get('state')}:{sid} 格子挂载不在节点挂载区")
    mounted = sorted(mounted_sids(text))
    out: dict[str, Any] = {
        "audit": "ok" if not fails and not drift else "fails",
        "fails": fails,
        "mounted_count": len(mounted),
        "mounted": mounted,
        "drift": drift,
    }
    if scan_frequency:
        try:
            from zephyr.trading.validation.decay_watch import run_decay_check
            out["decay"] = run_decay_check(dry_run=True, scan_frequency=scan_frequency)
        except Exception as exc:  # noqa: BLE001 衰减档巡检是增强项，失败不阻断审计
            out["decay"] = {"error": str(exc)[:120]}
    return out


def write_report(payload: dict[str, Any], sid_label: str, out_dir: Path | None = None) -> Path:
    """报告落盘（钩子③，格式 Owner 已定稿）：Markdown 一页，专属子目录 docs/_working/auto-mount-reports/
    （平铺容量治理：不占 _working 根 120 硬上限；文件名带时间戳，标题内含对象清单）。
    内容=挂了哪/为什么（判定依据）/证据指针（run+code+段表）三节。"""
    stamp = datetime.now()
    out_dir = out_dir or (REPORT_DIR / "auto-mount-reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"auto-mount-report-{stamp.strftime('%Y%m%d-%H%M')}.md"
    ids = [x for x in sid_label.split(",") if x.strip()]
    if len(ids) > 8:
        shown = ", ".join(ids[:8]) + f" …等 {len(ids)} 条"
    else:
        shown = sid_label or "（重放）"
    lines = [
        f"# auto_mount 挂图报告——{shown}",
        "",
        f"> {stamp.strftime('%Y-%m-%d %H:%M')}｜管线=MOD-BT-171｜治理边界=only-add（本次 diff 无删改）",
        "",
        f"**对象清单**：{sid_label or '（重放：全部已挂 STR-* 幂等验证）'}",
        "",
        "## 挂了哪",
        "",
        "```yaml",
        payload.get("diff") or "（零 diff——幂等重放，地图无变化）",
        "```",
        "",
        "## 为什么",
        "",
    ]
    for j in payload.get("judgements", []):
        segs = "; ".join(
            f"{s} SR={v.get('sr', 0):+.2f} t={v.get('t', 0):.2f} p={v.get('p', 1):.3g} "
            f"n={v.get('n', 0)}d OOS={v.get('oos_sr', 0):+.2f}({v.get('oos_n', 0)}d) "
            f"{'✔' if v.get('accepted') else '✘' + str(v.get('reject_reason', ''))}"
            for s, v in sorted((j.get("segments") or {}).items())) or "（选股类无状态格）"
        lines.append(f"- **{j['sid']}**（{j.get('cls', '')}）→ `{j.get('node') or '选股链'}`："
                     f"激活态={j.get('activated')}；分相位证据 {segs}")
    fdr = payload.get("fdr") or {}
    lines += ["", "## 证据指针", "",
              f"- 判定窗口：{payload.get('window') or IS_WIN_START}..最新可用日（SLE-3② 解冻，"
              f"终点=快照表尾窗回退 {PIT_TAIL_LAG} 行 PIT）",
              f"- 状态真源：{SNAPSHOT_TABLE}.dominant（宏观腿）+ 广度指数微观相位 overlay（SLE-3③ 补"
              f" euphoria/distribution 盲区）",
              f"- 多重检验：BHY-FDR q={fdr.get('q', FDR_Q)} 族 m={fdr.get('m', '-')} "
              f"拒绝={fdr.get('n_rejected', '-')} 临界 p={fdr.get('threshold', '-')}"
              f"{'（大族升级 t≥' + str(T_STAR_HLZ) + '）' if fdr.get('hlz') else ''}",
              f"- 代码真源：注册表 code_path→翻译件 build()（见各条目）",
              f"- 地图回执：38 规则校验 {'通过' if not payload.get('fails') else payload.get('fails')}；"
              f"权重方案：{payload.get('weights', '{}')}", ""]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def explain_panel(panel) -> dict[str, Any]:
    """② 相位覆盖回执（SLE-3②③ 验收面）：动态判定窗 + 六段天数改造前后对照。

    六段词表真源=zephyr.signal_ashare.core.environment_switch.SIX_STATES（封闭集，勿另立）。
    phase_before=只走 R2SIX 宏观腿（改造前口径，euphoria/distribution 恒 0=盲区实锤）；
    phase_after=叠加微观 overlay 后的合成相位（防御段自此可被真实触发）。
    """
    from zephyr.signal_ashare.core.environment_switch import SIX_STATES  # noqa: PLC0415 词表真源
    base = panel["dom"].map(R2SIX)
    return {"window": window_of(panel), "days": int(len(panel)),
            "phase_before": {s: int((base == s).sum()) for s in SIX_STATES},
            "phase_after": {s: int((panel["six"] == s).sum()) for s in SIX_STATES},
            "unmapped_days": int(panel["six"].isna().sum())}


def _mount_confidence(data: dict[str, Any]) -> dict[str, str]:
    """地图节点挂载 confidence 汇总（分配证据的置信来源，缺失=proposed）。"""
    return {str(m.get("strategy_ref")): str(m.get("confidence") or "proposed")
            for n in (data.get("nodes") or []) for m in (n.get("strategy_mounts") or []) if m.get("strategy_ref")}


def allocation_evidence(judgements: list[dict[str, Any]], confidence: dict[str, str] | None = None
                        ) -> dict[str, dict[str, Any]]:
    """② 判定 → ③ 分配证据：{sid: {sr, vol, confidence, states, selection, source, retired}}。

    sr/vol 用全窗口径（分配要的是整体风险调整表现，不是单相位段内 SR）；selection=True
    标记选股类（无相位假设但有权重诉求）。
    """
    out: dict[str, dict[str, Any]] = {}
    for j in judgements:
        full = j.get("full") or {}
        if not full:
            continue
        out[j["sid"]] = {"sr": float(full.get("sr") or 0.0), "vol": float(full.get("vol") or 0.0),
                         "confidence": (confidence or {}).get(j["sid"], "proposed"),
                         "states": list(j.get("activated") or []), "selection": j.get("activated") is None,
                         "source": j.get("code_path", ""), "retired": bool(j.get("retired"))}
    return out


def allocation_request(old: list[dict[str, Any]], evidence: dict[str, dict[str, Any]], *,
                       cap: float = DEFAULT_SINGLE_SLEEVE_CAP, floor: float = NEW_SLEEVE_WEIGHT,
                       step: float = WEIGHT_STEP_LIMIT) -> list[dict[str, Any]]:
    """③ 车道 D（pf_alloc）接口约定：本件出**权重来源**，不碰 src/zephyr/pf_alloc/**。

    每 sleeve 一行：strategy_ref／weight（归一后目标权，Σ=1）／signal_weight（归一前证据强度
    =SR×置信/波动，供分配链自行再切）／capacity（距单 sleeve 上限的剩余空间）／stage
    （proven|observation|decaying|frozen|retired）／source（证据指针）。
    MOD-PA-003 StrategyAllocationRequest(strategy_id, signal_weight, capacity) 按行消费即可，
    归一与约束已在本件闭环，分配链不需重复实现语义门。
    """
    prev = {x["strategy_ref"]: float(x["weight"]) for x in old}
    universe, score = _evidence_scores(prev, evidence)
    target = sleeve_weights(old, evidence, cap=cap, floor=floor, step=step)
    rows: list[dict[str, Any]] = []
    for r in universe:
        ev = evidence.get(r)
        w = float(target.get(r, 0.0))
        if ev is None:
            stage = "frozen"  # 无 ② 证据（底仓/遗留件）：不参与竞争，权重按恒等式承接残差
        elif ev.get("retired"):
            stage = "retired"
        elif str(ev["confidence"]) == "verified" and (ev["states"] or ev["selection"]):
            stage = "proven"
        elif ev["states"] or ev["selection"]:
            stage = "observation"
        else:
            stage = "decaying"  # 有净值证据但无一相位过 FDR 门=证据衰减中
        rows.append({"strategy_ref": r, "weight": w, "signal_weight": round(score.get(r, 0.0), 6),
                     "capacity": round(max(0.0, cap - w), 6), "stage": stage, "source": (ev or {}).get("source", "")})
    return rows


def rebalance_proposal(entries: list[dict[str, Any]], panel, only: set[str] | None = None) -> dict[str, Any]:
    """③ --rebalance 实现（SLE-1 验收面）：真实分配提案=只读 diff，永不写图（Owner 门位在后面）。

    与 --apply 的区别是本件走 weight_adjust_assert（分配门）而非 only_add_assert（写入门）——
    真实调权必然过不了 only_add（它禁任何非等比变动），所以提案只打印，落图须 Owner 开闸。
    """
    import yaml
    text = MAP_YAML.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    plan = data["portfolio_plan"] or {}
    sleeves = plan["sleeves"]
    cap = float((plan.get("aggregator") or {}).get("max_single_sleeve") or DEFAULT_SINGLE_SLEEVE_CAP)
    judgements, receipt, _ = _judge_batch(entries, panel, only)
    ev = allocation_evidence(judgements, _mount_confidence(data))
    before_w = {x["strategy_ref"]: float(x["weight"]) for x in sleeves}
    after_w = sleeve_weights(sleeves, ev, cap=cap)
    try:
        weight_adjust_assert(before_w, after_w, cap=cap)
        gate = "pass"
    except AssertionError as exc:
        gate = f"reject: {exc}"
    after_text = rescale_sleeves(text, {k: v for k, v in after_w.items() if k in before_w})
    diff = "\n".join(difflib.unified_diff(text.splitlines(), after_text.splitlines(),
                                          "map.sleeves.current", "map.sleeves.proposed", lineterm="", n=0))
    return {"window": window_of(panel), "cap": cap, "fdr": receipt, "gate": gate, "evidence": ev,
            "before": before_w, "after": after_w, "diff": diff,
            "requests": allocation_request(sleeves, ev, cap=cap)}


def main() -> None:
    ap = argparse.ArgumentParser(description="auto_mount 自动挂图器（only-add）")
    ap.add_argument("--plan", action="store_true", help="预演：只算不写")
    ap.add_argument("--apply", action="store_true", help="写入地图（需显式 --strategy；先 claim+safe_write）")
    ap.add_argument("--replay", action="store_true", help="幂等验收：已挂集合重放断言零 diff")
    ap.add_argument("--audit", action="store_true", help="月度挂图审计（只读，含 decay 同口径分档）")
    ap.add_argument("--explain", action="store_true", help="判定明细（只读：动态窗口/相位覆盖前后对照/段证据/FDR）")
    ap.add_argument("--rebalance", action="store_true", help="调权提案 diff（只读，永不写图；SLE-1 Owner 门位）")
    ap.add_argument("--strategy", default=None, help="逗号分隔 strategy_id 列表")
    ap.add_argument("--report", action="store_true", help="报告落盘 docs/_working/（--plan/--apply/--replay 均可带）")
    ap.add_argument("--scan-frequency", default="monthly", choices=["monthly", "quarterly", "semiannual"],
                    help="审计档位（默认 monthly，对齐 decay_watch 分档）")
    args = ap.parse_args()
    if args.audit:  # 审计不需判定（三件套全只读），前置分支免付全量归因成本
        print(json.dumps(mount_audit(args.scan_frequency), ensure_ascii=False, indent=1))
        return
    only = {x.strip() for x in args.strategy.split(",") if x.strip()} if args.strategy else None
    entries = load_registry_entries()
    panel = load_dominant()
    if args.replay:
        text0 = MAP_YAML.read_text(encoding="utf-8")
        only = mounted_sids(text0)  # 重放范围=地图上已挂的 STR-*（幂等验收）
        assert only, "地图上无已挂 STR-* 可重放"
    if args.explain:
        judgements, receipt, _ = _judge_batch(entries, panel, only)
        print(json.dumps({"panel": explain_panel(panel), "fdr": receipt,
                          "judgements": judgements}, ensure_ascii=False, indent=1))
        return
    if args.rebalance:
        out = rebalance_proposal(entries, panel, only)
        print(out["diff"] or "(零 diff——提案与现权一致)")
        print(json.dumps({k: out[k] for k in ("window", "cap", "fdr", "gate", "after")}, ensure_ascii=False, indent=1))
        for row in out["requests"]:
            print(f"  {row['strategy_ref']:<24} w={row['weight']:.6f} sw={row['signal_weight']:.4f} "
                  f"cap_left={row['capacity']:.4f} stage={row['stage']}")
        print("[REBALANCE] 只出提案不写图（落图须 Owner 开 weight_adjust 门位）")
        return
    ops, before, weights, skipped = _plan_inserts(entries, panel, only)
    report_payload: dict[str, Any] = {"judgements": [], "diff": None, "fails": None, "weights": weights}
    # 判定摘要（报告/重放共用）：逐条判定依据+分相位证据（已过 FDR 门口径）
    judgements, receipt, _skipped = _judge_batch(entries, panel, only)
    report_payload["judgements"] = judgements
    report_payload["fdr"] = receipt
    report_payload["window"] = window_of(panel)
    if args.replay:
        pending = [o for o in ops if o["kind"] in ("node_mount", "cell", "sleeve")]
        assert not pending, (f"重放非幂等：仍有 {len(pending)} 个待插操作 {pending[:3]}；"
                             "若全为 cell 则多为判定窗解冻/相位补全新纳入的态（--explain 看 accept 依据），"
                             "only-add 不回撤，需 --apply 补挂")
        report_payload["fails"] = validate_map()
        print(f"REPLAY OK: 已挂 {len(only)} 条零 diff（幂等）；38 规则 fails={len(report_payload['fails'])}")
        if args.report:
            rp = write_report(report_payload, ",".join(sorted(only))[:60])
            print(f"[REPORT] {rp}")
        return
    after = apply_ops(ops, before)
    only_add_assert(before, after)
    diff = "\n".join(difflib.unified_diff(before.splitlines(), after.splitlines(), "map.before", "map.after", lineterm="", n=1))
    report_payload["diff"] = diff
    print(diff or "(零 diff)")
    if skipped:
        print("[SKIPPED] " + "; ".join(skipped))
    if not args.apply:
        print(f"\n[PLAN] ops={len(ops)} weights={weights}")
        if args.report:
            rp = write_report(report_payload, args.strategy or "plan")
            print(f"[REPORT] {rp}")
        return
    assert only, "--apply 必须显式给 --strategy（挂谁=C6 线决策，工具只管怎么挂）"
    from zephyr.shared.io.file_utils import safe_write_text
    import hashlib
    r = safe_write_text(MAP_YAML, after, expected_base_sha256=hashlib.sha256(before.encode()).hexdigest(), newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError("safe_write_text 未确认写入")
    fails = validate_map()
    assert not fails, f"38 规则校验未过: {fails[:5]}"
    report_payload["fails"] = fails
    print(f"\n[APPLIED] ops={len(ops)} 校验全绿 written={getattr(r, 'written', True)}")
    # S11/C3 断桥③: 挂图落地成功 → fw_backtest_due（TDM sleeves→整装回测自动跑+证据包）；
    # 事件链任何故障不反噬挂图管线（journal 已留档，恢复=drain 重放）
    try:
        from zephyr.strategy_pipeline.fw_backtest import emit_fw_backtest_due

        fw = emit_fw_backtest_due(trigger="auto_mount", sids=sorted(only))
        tail = f" err={fw.get('error')}" if fw.get("error") else ""
        print(f"[FW-BACKTEST-DUE] event={fw.get('event')} drained={fw.get('drained')}{tail}")
    except Exception as exc:  # noqa: BLE001——事件链故障不回滚挂图
        print(f"[FW-BACKTEST-DUE] emit 失败（不影响挂图结果）: {type(exc).__name__}: {exc}")
    if args.report:
        rp = write_report(report_payload, args.strategy)
        print(f"[REPORT] {rp}")


if __name__ == "__main__":
    sys.exit(main())
