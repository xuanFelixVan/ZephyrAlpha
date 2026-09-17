# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.factory_grid_executor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.position.core.position_recipe_compiler; scripts.backtest.translated._c4_engine
# [CONSUMERS] data/strategy_intake/grid_<ts>/（出生证 manifest+阴性库）；factory_grid_ananova；E2 四车道（挂接预留）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] schema 一次定型（config/position_recipe_grid_schema.yaml 唯一真源，禁删维）；抽样完整性 100%（抽了必跑，禁截断）；每 recipe 带出生证+degraded 标记；阴性记录 MUST 带死亡层+死因否则校验拒绝；回测口径=冻结土规 T+1（引擎复用零重实现）；行业真源=sws2021_l1（schema industry_anchor）；降级取值必须标 degraded（结构知识阶段剔除，禁静默）
# [MODIFY-GUARD] tests/backtest/test_factory_grid_executor.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/求值失败)；ValueError(schema/契约非法)
# [TESTS] tests/backtest/test_factory_grid_executor.py
# [A_module] module_id=MOD-BT-196 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""F-06 组合层穷尽网格——批次 A 普查执行器（MOD-BT-196）。

编译（MOD-POS-029 GridCompiler）→ signal 侧分层抽样 → recipe→weights 求值 →
冻结土规向量化回测（复用 _c4_engine，零重实现）→ 出生证 manifest + 阴性库。

v1 求值实现边界（诚实披露，立项稿 §十二 两批次的批次 A）:
  精确实现: B_top_n 全部 / D1_rebalance_freq 全部 / D2_rebalance_trigger 全部 /
            E_single_cap 全部 / G_universe 全部 / H_turnover_lambda 全部 /
            A1(raw/rank/zscore) / A2(equal/ic_mean/ic_ir/halflife20/halflife60) /
            C(equal_weight/inv_vol/signal_strength)
  T2a（2026-09-16）: A2 orth_equal(逐日 Gram-Schmidt)/lasso(60日滚动重训)/
            pc1(滚动 PC1 载荷) 与 C mkt_cap(total_mv 宽表)/risk_parity(naive RP=inv_vol
            同形语义，Maillard 2010 术语)/kelly_025/kelly_050(fraction×μ/σ² 非满仓) 全部
            转精确实现。
  T2b（2026-09-16）: A1 行业族转精确实现，降级格点占比归零——
            industry_neutral=逐日截面按 sws2021_l1 行业分组去均值（组内 demean）；
            size_neutral=逐日对 log(total_mv) 截面 OLS 残差；industsize_neutral=
            行业组内 demean→log 市值残差。行业锚=c1_market.industry_class L1 现行快照
            （词表校验拦截数据线 'nan' 坏行，诊断见 schema industry_anchor）；市值复用
            mkt_cap 宽表。锚/市值数据缺失时 fail-closed 降级 zscore 并标 degraded。
  T2c（2026-09-16）: 性能优化（不改数值语义）: combined 截面+rank 按 (G,A1,A2) prefix
            缓存（同 prefix 格点复用，LRU 单元格预算防内存膨胀）；_apply_freq_trigger
            periodic 向量化（iloc[::step]+reindex ffill，与逐日循环逐位等价）/drift_band
            numpy 行循环（nansum=逐行 skipna 同语义）；【记录】lasso 重训参数放宽为
            Lasso(selection='random', random_state=0, tol=1e-4)——坐标下降随机序+松弛
            收敛阈，格点语义等价（60 日滚动重训节奏/alpha/前视防御不变），非逐位等价。
            收益序列档案: run_batch 成功分支 nets 落盘 net_returns.parquet（环境无
            pyarrow 兜底 net_returns.csv.gz），summary.net_returns_file=文件名——
            DSR 精确口径数据基础。

用法:
  python scripts/backtest/factory_grid_executor.py --smoke                 # 烟测（管线联通，8 格点）
  python scripts/backtest/factory_grid_executor.py --n-samples 20000       # 批次 A 普查
产出: data/strategy_intake/grid_<run_ts>/manifest.csv + negatives.csv + summary.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "backtest" / "translated"))
sys.path.insert(0, str(_REPO / "scripts" / "backtest"))

SCHEMA_PATH = _REPO / "config" / "position_recipe_grid_schema.yaml"
INTAKE_DIR = _REPO / "data" / "strategy_intake"

# 死亡层枚举（立项稿 §十三: 阴性必须带死亡层+死因，否则不计）
DEATH_LAYERS = ("eval", "backtest", "gate")

DEFAULT_CONTEXT = {"strategy_pool": ["primary"], "phase": 1, "capital_ramp_enabled": False}
# NO-BARE-SQL + TABLE-NAME-REGISTRY 配方: SQL 常量化+表名走 TableRegistry 真源
from zephyr.data.table_registry import get_registry as _get_table_registry

# category_id=meta_stock_basic（business_data_categories.yaml 真源），TableRegistry 解析全限定表名
_SQL_MV = (
    "SELECT trade_date, symbol, toFloat64(total_mv) AS total_mv FROM "
    + _get_table_registry().table("market_stock_indicator")
    + " WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND total_mv > 0"
)
_SQL_ALL_A = (
    "SELECT DISTINCT symbol FROM " + _get_table_registry().table("meta_stock_basic") +
    " WHERE valid_to IS NULL AND name NOT LIKE '%ST%' AND name NOT LIKE '%退%'"
)
# T2b 行业锚: c1_market.industry_class L1 现行快照（category_id=market_industry_class 真源反查）
_SQL_INDUSTRY_MAP = (
    "SELECT symbol, industry_sw, valid_from, updated_at FROM "
    + _get_table_registry().table("market_industry_class")
    + " WHERE industry_level = 1 AND valid_to IS NULL"
)
# 行业词表真源（sws2021_l1 = schema industry_anchor.vocabulary_source；禁硬编码行业清单）
_SWS_VOCAB_SOURCE = (
    _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "io_sector_sws_map.yaml"
)
# v1 因子集（F-02 接线后扩展；全部从 close 现算，零额外依赖）
V1_FACTORS = ("f_mom20", "f_lowvol20", "f_ma_gap")


@dataclass(frozen=True)
class NegativeRecord:
    """阴性配方记录——死亡层+死因缺失即校验拒绝（机械可校验）。"""

    recipe_id: str
    death_layer: str            # eval / backtest / gate
    death_reason: str           # 结构化原因码（禁空串）
    values: dict[str, str]
    degraded_dimensions: str    # 逗号分隔降级维（空=无）
    detail: str = ""

    def __post_init__(self) -> None:
        if self.death_layer not in DEATH_LAYERS:
            raise ValueError(f"死亡层非法: {self.death_layer}（合法 {DEATH_LAYERS}）")
        if not self.death_reason.strip():
            raise ValueError(f"阴性记录死因缺失: {self.recipe_id}")


@dataclass
class GridEvalOutcome:
    """单 recipe 求值+回测结果（manifest 行）。"""

    recipe_id: str
    prefix_key: str
    values: dict[str, str]
    degraded_dimensions: tuple[str, ...]
    sharpe: float | None = None
    ann_return: float | None = None
    max_drawdown: float | None = None
    avg_turnover: float | None = None
    net_days: int = 0


def _load_engine():
    from _c4_engine import daily_net_returns, filter_st, load_px, load_st_flags, run_backtest, wide

    return load_px, wide, filter_st, load_st_flags, run_backtest, daily_net_returns


def _load_universe(universe: str, start: str, end: str) -> set[str]:
    """G_universe → {hs300, zz500, all_a_ex_st}（成分快照，index_constituent 真源）。"""
    from _c4_engine import load_index_constituents

    if universe == "hs300":
        return load_index_constituents("000300.SH", start, end)
    if universe == "zz500":
        return load_index_constituents("000905.SH", start, end)
    if universe == "all_a_ex_st":
        rows = _engine_query_all_a()
        return rows
    raise ValueError(f"G_universe 非法取值: {universe}")


def _engine_query_all_a() -> set[str]:
    from _c4_engine import run_query

    rows = run_query(_SQL_ALL_A)
    return {(r[0] or "")[:6] for r in rows if r[0]}


def _load_sws_vocab() -> set[str]:
    """sws2021_l1 行业词表（io_sector_sws_map.yaml mappings[].sws，禁硬编码行业清单）。"""
    import yaml

    data = yaml.safe_load(_SWS_VOCAB_SOURCE.read_text(encoding="utf-8"))
    return {str(m["sws"]) for m in data["mappings"]}


def _clean_industry_rows(rows: list, vocab: set[str]) -> tuple[dict[str, str], int]:
    """(symbol, industry_sw, valid_from, updated_at) 行清洗 + 6 位化确定性去重。

    返回 ({symbol6: industry}, 非词表行数)。表内符号格式混用（2026-08-03 ifind 批=裸
    6 位，2026-09-13 批=带 .SH/.SZ 后缀），6 位化后同票多行按 (valid_from, updated_at)
    最新者胜——PIT 正确且与返回行序无关；词表外值统一拦截（含已知坏行: 688806 裸符号行
    industry_sw='nan' 字面量，其 09-13 新批 .SH 行带正常行业接管；删除属数据线职责，
    此处只做消费侧防御）。
    """
    best: dict[str, tuple] = {}
    dropped_nonvocab = 0
    for sym, ind, vf, ua in rows:
        s6 = (sym or "")[:6]
        if not s6:
            continue
        if ind not in vocab:
            dropped_nonvocab += 1
            continue
        key = (str(vf), str(ua))  # ISO 字符串序=时间序（类型稳健，兼容 NaT/None）
        if s6 not in best or key > best[s6][0]:
            best[s6] = (key, ind)
    return {s6: ind for s6, (_, ind) in best.items()}, dropped_nonvocab


def _industry_map() -> dict[str, str]:
    """行业中性锚: c1_market.industry_class L1 现行快照（valid_to IS NULL）→ {symbol: industry}。

    词表=sws2021_l1（io_sector_sws_map.yaml）。查询失败或清洗后为空抛 RuntimeError
    （fail-closed，调用方降级 zscore 并标 degraded，禁静默）。
    """
    from _c4_engine import run_query

    vocab = _load_sws_vocab()
    rows = run_query(_SQL_INDUSTRY_MAP)
    mapping, dropped_nonvocab = _clean_industry_rows(rows, vocab)
    if not mapping:
        raise RuntimeError("industry_map 清洗后为空（industry_class 数据健康异常）")
    if dropped_nonvocab:
        import logging as _lg

        _lg.getLogger(__name__).warning(
            "industry_map 剔除非词表行业 %d 行（含已知 'nan' 坏行，详见 schema industry_anchor）",
            dropped_nonvocab,
        )
    return mapping


def _load_mkt_cap_wide(start: str, end: str, columns: pd.Index) -> pd.DataFrame | None:
    """total_mv 宽表（c1_market.stock_indicator，2020-01 起覆盖）；空则 None（mkt_cap 格点将 fail-closed 记阴性）。"""
    from _c4_engine import run_query, wide

    rows = run_query(_SQL_MV.format(start=start, end=end))
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=["trade_date", "symbol", "total_mv"])
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    w = wide(df, "total_mv")
    return w.reindex(columns=columns)


def compute_v1_factors(closes: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """v1 三因子（全从 close 现算）: 动量/低波/均线乖离。列=symbol, index=date。"""
    rets = closes.pct_change()
    ma20 = closes.rolling(20).mean()
    f_mom20 = closes.pct_change(20)
    f_lowvol20 = -rets.rolling(20).std()
    f_ma_gap = closes / ma20 - 1.0
    return {"f_mom20": f_mom20, "f_lowvol20": f_lowvol20, "f_ma_gap": f_ma_gap}


def _demean_by_group(factor: pd.DataFrame, group_of_col: dict[str, str]) -> pd.DataFrame:
    """逐日截面按组去均值（组内 demean，完全向量化）。

    实现: 列→组标签 groupby mean 得 (date × group) 组均值矩阵，广播回列相减。
    NaN 语义: 组均值 skipna——组内个别缺失不影响组均值，缺失格保持 NaN（无跨票污染）；
    无组标签的列 fail-closed 置 NaN（无行业信息的票不得留在截面泄露行业效应）。
    """
    grp = factor.columns.to_series().map(group_of_col)
    valid = grp.dropna().index
    f = factor[valid]
    means = f.T.groupby(grp[valid]).mean().T  # (date × group)
    out = f - means[grp[valid]].set_axis(valid, axis=1)
    return out.reindex(columns=factor.columns)


def _regress_out(factor: pd.DataFrame, ctrl: pd.DataFrame) -> pd.DataFrame:
    """逐日截面一元 OLS 残差: factor 对 ctrl 回归取残差（无自由参数，完全向量化）。"""
    ctrl = ctrl.reindex(index=factor.index, columns=factor.columns)
    m = factor.notna() & ctrl.notna()
    fw = factor.where(m)
    xw = ctrl.where(m)
    f0 = fw.sub(fw.mean(axis=1), axis=0)
    x0 = xw.sub(xw.mean(axis=1), axis=0)
    var = (x0 * x0).mean(axis=1).replace(0, np.nan)
    beta = (f0 * x0).mean(axis=1) / var
    return f0.sub(x0.mul(beta, axis=0)).where(m)


def _normalize(factor: pd.DataFrame, mode: str, industry_map: dict[str, str] | None = None,
               mkt_cap_w: pd.DataFrame | None = None) -> tuple[pd.DataFrame, bool]:
    """A1 标准化。返回 (截面, degraded)。

    行业族精确实现（T2b 2026-09-16，数据锚经 schema industry_anchor）:
      industry_neutral   = 逐日截面按 sws2021_l1 行业分组去均值（组内 demean）
      size_neutral       = 逐日对 log(total_mv) 截面 OLS 残差
      industsize_neutral = 行业组内 demean → 对组内 demean 的 log(total_mv) OLS 残差
                           （FWL 定理下严格等价于行业虚拟变量+市值联合截面回归，
                           行业与市值效应同时精确消除；对原始市值级联回归不等价）
    行业锚/市值宽表缺失（含加载失败）时 fail-closed 降级 zscore 并标 degraded（诚实披露，禁静默）。
    """
    if mode == "raw":
        return factor, False
    if mode == "rank":
        return factor.rank(axis=1, pct=True), False
    if mode == "zscore":
        mu = factor.mean(axis=1)
        sd = factor.std(axis=1)
        return factor.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0), False

    def _degraded_zscore() -> tuple[pd.DataFrame, bool]:
        mu = factor.mean(axis=1)
        sd = factor.std(axis=1)
        return factor.sub(mu, axis=0).div(sd.replace(0, np.nan), axis=0), True

    log_mv = None if mkt_cap_w is None else np.log(mkt_cap_w.where(mkt_cap_w > 0))
    if mode == "industry_neutral" and industry_map:
        return _demean_by_group(factor, industry_map), False
    if mode == "size_neutral" and log_mv is not None:
        return _regress_out(factor, log_mv), False
    if mode == "industsize_neutral" and industry_map and log_mv is not None:
        # FWL: M_D(y) 对 M_D(x) 回归取残差 ≡ 行业虚拟变量+市值联合截面回归残差
        resid = _demean_by_group(factor, industry_map)
        x_dm = _demean_by_group(log_mv, industry_map)
        return _regress_out(resid, x_dm), False
    # 行业族锚缺失 / 未知 mode: 诚实降级
    return _degraded_zscore()


def _combine(factors: dict[str, pd.DataFrame], normalized: list[pd.DataFrame], mode: str,
             closes: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """A2 合成。返回 (合成截面, degraded)。

    IC 类权重=60 日滚动 rank-IC（ic_mean 均值 / ic_ir 均值÷std / halflife 指数衰减均值），
    **shift(1) 前视防御：第 d 日合成只用截至 d-1 的 IC**（d 日因子预测 d→d+1 收益，
    权重若含 d 日 IC 即用了未来收益——bt-fin-correctness 前视铁律）。
    """
    names = list(factors.keys())
    dates = closes.index
    if mode == "equal":
        stack = pd.concat(normalized)
        return stack.groupby(level=0).mean(), False
    if mode in ("ic_mean", "ic_ir", "halflife20", "halflife60"):
        fwd = closes.pct_change().shift(-1)  # d→d+1 前向收益
        ic_by_name = []
        for nf in normalized:
            xr = nf.rank(axis=1)
            rr = fwd.rank(axis=1)
            m = xr.notna() & rr.notna()
            x = xr.where(m)
            y = rr.where(m)
            cov = (x.sub(x.mean(axis=1), axis=0) * y.sub(y.mean(axis=1), axis=0)).mean(axis=1)
            sd = (x.std(axis=1) * y.std(axis=1)).replace(0, np.nan)
            ic_by_name.append((cov / sd).fillna(0.0))
        ic_all = pd.concat(ic_by_name, axis=1, keys=names)  # index=date, columns=names
        if mode == "ic_mean":
            w = ic_all.rolling(60, min_periods=20).mean()
        elif mode == "ic_ir":
            w = ic_all.rolling(60, min_periods=20).mean() / (ic_all.rolling(60, min_periods=20).std() + 1e-12)
        else:
            span = 20 if mode == "halflife20" else 60
            w = ic_all.ewm(halflife=span, min_periods=10, adjust=False).mean()
        w = w.clip(lower=0.0).shift(1)  # ← 前视防御: d 日只用截至 d-1 的 IC
        w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0)
        w = w.reindex(dates).fillna(1.0 / len(names))
        arr = np.zeros((len(dates), normalized[0].shape[1]))
        for j, nf in enumerate(normalized):
            arr += w[names[j]].to_numpy()[:, None] * nf.reindex(dates).fillna(0.0).to_numpy()
        combined = pd.DataFrame(arr, index=dates, columns=normalized[0].columns)
        return combined, False
    if mode == "orth_equal":
        # 逐日截面 Gram-Schmidt：f_k 对 span(f_1..f_{k-1}) 取残差并归一，正交分量等权
        # （顺序依赖=f 维声明序；正交化消除因子间共线，等权保留各正交方向信息）
        arrs = [nf.fillna(0.0).to_numpy() for nf in normalized]
        basis: list[np.ndarray] = []
        for a in arrs:
            r = a.copy()
            for b in basis:
                r = r - (r * b).sum(axis=1, keepdims=True) * b
            basis.append(r / (np.linalg.norm(r, axis=1, keepdims=True) + 1e-12))
        combined = pd.DataFrame(sum(basis) / len(basis), index=dates, columns=normalized[0].columns)
        return combined, False
    if mode in ("lasso", "pc1"):
        # 滚动重训合成（每 60 日 expanding 窗重训一次载荷，应用期内恒定——
        # 训练窗配对 X_t→y_t 均截至窗尾，应用期在窗后=零前视）
        from sklearn.linear_model import Lasso

        fwd = closes.pct_change().shift(-1)
        F = len(names)
        X_all = np.stack([nf.fillna(0.0).to_numpy() for nf in normalized], axis=2)  # T×S×F
        y_all = fwd.fillna(0.0).to_numpy()  # T×S
        w_by_date = np.full((len(dates), F), 1.0 / F)
        for start in range(60, len(dates), 60):
            lo = max(0, start - 60)
            Xtr = X_all[lo:start].reshape(-1, F)
            ytr = y_all[lo:start].reshape(-1)
            ok = np.isfinite(Xtr).all(axis=1) & np.isfinite(ytr)
            w_new = np.full(F, 1.0 / F)
            if mode == "lasso":
                if int(ok.sum()) > 500:
                    # T2c 性能【记录】: selection='random'+random_state=0（确定性）+
                    # tol=1e-4（默认 1e-4 即坐标下降收敛阈，显式化）——坐标下降随机
                    # 遍历序显著加速大窗口 fit；60 日滚动重训节奏/alpha/前视防御不变，
                    # 格点语义等价（非逐位等价，偏差在 tol 量级内）
                    mdl = Lasso(alpha=1e-4, fit_intercept=False, max_iter=2000,
                                tol=1e-4, selection="random", random_state=0)
                    mdl.fit(Xtr[ok], ytr[ok])
                    w_abs = np.abs(mdl.coef_)
                    s = float(w_abs.sum())
                    if s > 0:
                        w_new = w_abs / s
            else:  # pc1: 训练窗因子相关阵的 PC1 载荷（符号定正）
                Xw = X_all[lo:start].reshape(-1, F)
                Xw = Xw[ok]
                if Xw.shape[0] > 500:
                    cm = np.corrcoef(Xw, rowvar=False)
                    vals, vecs = np.linalg.eigh(cm)
                    load = vecs[:, int(np.argmax(vals))]
                    if load.sum() < 0:
                        load = -load
                    s = float(np.abs(load).sum())
                    if s > 0:
                        w_new = np.abs(load) / s
            w_by_date[start : start + 60] = w_new
        arr = np.zeros((len(dates), normalized[0].shape[1]))
        for j, nf in enumerate(normalized):
            arr += w_by_date[:, j : j + 1] * nf.fillna(0.0).to_numpy()
        return pd.DataFrame(arr, index=dates, columns=normalized[0].columns), False
    # 其余未知 mode：诚实降级
    stack = pd.concat(normalized)
    return stack.groupby(level=0).mean(), True


def _sizing(scores: pd.DataFrame, top_n: int, mode: str,
            vol20: pd.DataFrame, mkt_cap_w: pd.DataFrame | None = None,
            rets60_mean: pd.DataFrame | None = None,
            rets60_var: pd.DataFrame | None = None,
            rank_pre: pd.DataFrame | None = None) -> tuple[pd.DataFrame, bool]:
    """B 选股 + C 定尺寸。返回 (weights 截面, degraded)。

    rank_pre（T2c 缓存加速）: 同一 scores 已算好的 rank（combined 缓存随附）；
    rank 仅依赖 scores，传入时跳过重算，数值恒等。调用方保证 scores 对应关系。
    """
    rank = rank_pre if rank_pre is not None else scores.rank(axis=1, ascending=False)
    mask = rank <= top_n
    base = mask.astype(float)
    base[base == 0] = np.nan
    if mode == "equal_weight":
        return _norm_rows(base, top_n), False
    if mode == "inv_vol":
        iv = 1.0 / vol20.where(vol20 > 0)
        w = base * iv
        return _norm_rows(w, top_n), False
    if mode == "mkt_cap":
        if mkt_cap_w is None:
            raise RuntimeError("mkt_cap sizing 需要市值宽表（run_batch 未加载）")
        w = base * mkt_cap_w
        return _norm_rows(w, top_n), False
    if mode == "risk_parity":
        # naive risk parity（Maillard et al. 2010 术语）= 等波动贡献 = inv_vol 同形：
        # 真实 RP（含相关阵迭代）在 2 万格点向量化场景不可行，取业界标准一阶近似。
        # 与 inv_vol 结果相同是"取值语义等价"事实，由 ANOVA 自然呈现，非降级。
        iv = 1.0 / vol20.where(vol20 > 0)
        w = base * iv
        return _norm_rows(w, top_n), False
    if mode == "signal_strength":
        s = scores.where(mask)
        s = s - s.min(axis=1).min() + 1e-9
        w = base * s.abs()
        return _norm_rows(w, top_n), False
    if mode in ("kelly_025", "kelly_050"):
        if rets60_mean is None or rets60_var is None:
            raise RuntimeError("kelly sizing 需要 60 日收益均值/方差宽表（run_batch 未加载）")
        fraction = 0.25 if mode == "kelly_025" else 0.5
        kelly_raw = (fraction * (rets60_mean / rets60_var.where(rets60_var > 1e-12))).clip(lower=0.0).fillna(0.0)
        w = mask.astype(float) * kelly_raw  # 非入选=零仓（kelly 非满仓语义，不 NaN 化）
        return w, False
    raise RuntimeError(f"未知 C_sizing 取值: {mode}")


def _norm_rows(w: pd.DataFrame, top_n: int) -> pd.DataFrame:
    row_sum = w.sum(axis=1).replace(0, np.nan)
    out = w.div(row_sum, axis=0).fillna(0.0)
    return out


def _apply_cap_and_lambda(w: pd.DataFrame, cap: str, lam: str) -> pd.DataFrame:
    """E 单票上限 + H 换手惩罚 λ（λ 收缩向旧权重）。"""
    cap_map = {"cap5": 0.05, "cap10": 0.10, "cap20": 0.20}
    lam_map = {"lambda_0": 0.0, "lambda_5bp": 0.0005, "lambda_15bp": 0.0015}
    c = cap_map[cap]
    # cap=硬约束终态 clip，不再 renorm（renorm 会重新突破上限）：
    # 持仓数不足（等权 1/n > cap）时允许低仓位——约束优先于满仓，超额留现金
    w = w.clip(upper=c)
    l = lam_map[lam] * 100.0  # λ 惩罚项放大为组合收缩系数（5bp/15bp→0.5/1.5 收缩比例）
    if l > 0:
        w = w.ewm(alpha=min(1.0, l), adjust=False).mean()
        rs = w.sum(axis=1).replace(0, np.nan)
        w = w.div(rs, axis=0).fillna(0.0)
    return w


def _apply_freq_trigger(w: pd.DataFrame, freq: str, trigger: str) -> pd.DataFrame:
    """D1 频率 + D2 触发: 非调仓日沿用旧权重；drift_band=偏离>10% 才重平衡。

    T2c 性能（数值语义与逐日循环逐位等价）:
      periodic → 每 step 行取值: out[i] = w.iloc[(i//step)*step]，用
        iloc[::step].reindex(index, method='ffill') 一步到位（索引单调且第 0 行
        必为调仓日，ffill 语义严格等于逐日沿用旧权重）；step=1 短路直返。
      drift_band → 保持逐日循环但切 numpy 行数组（省 .loc 逐行标签查找）；
        np.nansum ≡ pandas row-sum skipna 语义，判阈 (|Δw|.sum()/2 > 0.10)。
    """
    step = {"daily": 1, "weekly": 5, "biweekly": 10, "monthly": 21}[freq]
    if trigger != "drift_band":
        if step == 1:
            return w.copy()
        return w.iloc[::step].reindex(w.index, method="ffill")
    vals = w.to_numpy()
    last = vals[0].copy()
    out = np.empty_like(vals)
    thr = 0.10 * 2.0  # 原语义: |Δw|.sum()/2 > 0.10（×2 免逐行除法）
    for i in range(len(vals)):
        row = vals[i]
        if i % step == 0 or np.nansum(np.abs(row - last)) > thr:
            last = row.copy()
        out[i] = last
    return pd.DataFrame(out, index=w.index, columns=w.columns)


# T2c combined 缓存单元格预算（entry=combined+rank 各 T×S float64；970×1800 级
# 单 entry≈3.5e6 cell，预算 24e6 cell ≈ 全窗口池化 <400MB，超限 FIFO 逐出最旧 prefix）
_COMBINE_CACHE_MAX_CELLS = 24_000_000


def _combine_cache_store(cache: dict, key, entry: tuple) -> None:
    """combined 缓存存入 + 单元格预算逐出（防内存膨胀；命中侧用 pop+reinsert 做 LRU 续期）。"""
    cache[key] = entry
    total = 0
    for e in cache.values():
        total += e[0].size + e[1].size
    while total > _COMBINE_CACHE_MAX_CELLS and len(cache) > 1:
        old_key, old = next(iter(cache.items()))
        total -= old[0].size + old[1].size
        cache.pop(old_key)


def evaluate_recipe(recipe, closes: pd.DataFrame, factors: dict[str, pd.DataFrame],
                    vol20: pd.DataFrame, universe_cols: list[str],
                    mkt_cap_w: pd.DataFrame | None = None,
                    rets60_mean: pd.DataFrame | None = None,
                    rets60_var: pd.DataFrame | None = None,
                    industry_map: dict[str, str] | None = None,
                    combine_cache: dict | None = None) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """recipe → (weights 宽表, degraded 维元组)。求值失败抛 RuntimeError（fail-closed，调用方记阴性）。

    combine_cache（T2c）: 按 (G,A1,A2) prefix 复用 combined 截面+rank——同 prefix 格点
    的 normalize/combine 输入确定则输出确定（industry_map/mkt_cap_w 批内恒定），rank 仅
    依赖 combined。命中时 A1/A2 degraded 标记一并复现，manifest 口径与无缓存逐位一致。
    """
    v = recipe.values
    degraded: list[str] = []
    cols = universe_cols
    combined: pd.DataFrame | None = None
    rank: pd.DataFrame | None = None
    cache_key = None
    if combine_cache is not None:
        cache_key = (v["G_universe"], v["A1_factor_normalize"], v["A2_combine_weight"])
        hit = combine_cache.pop(cache_key, None)
        if hit is not None:
            combine_cache[cache_key] = hit  # LRU 续期
            combined, rank, a1_deg, a2_deg = hit
            if a1_deg:
                degraded.append("A1_factor_normalize")
            if a2_deg:
                degraded.append("A2_combine_weight")
    if combined is None:
        cl = closes[cols]
        normalized: list[pd.DataFrame] = []
        names = list(factors.keys())
        a1_deg = False
        for n in names:
            f = factors[n][cols]
            nf, deg = _normalize(f, v["A1_factor_normalize"], industry_map=industry_map,
                                 mkt_cap_w=mkt_cap_w)
            if deg:
                a1_deg = True
            normalized.append(nf)
        if a1_deg:
            degraded.append("A1_factor_normalize")
        combined, deg2 = _combine(factors, normalized, v["A2_combine_weight"], cl)
        if deg2:
            degraded.append("A2_combine_weight")
        if combine_cache is not None:
            rank = combined.rank(axis=1, ascending=False)
            _combine_cache_store(combine_cache, cache_key, (combined, rank, a1_deg, bool(deg2)))
    top_n = int(v["B_top_n"].replace("top", ""))
    # E cap 约束的持仓数扩展（B×E 交互的实务语义）: 满仓+单票≤cap 要求
    # M=ceil(1/cap) 只——M>top_n 时有效持仓数扩展为 M（仍按分数序取）
    cap_val = {"cap5": 0.05, "cap10": 0.10, "cap20": 0.20}[v["E_single_cap"]]
    effective_n = max(top_n, -(-1 // cap_val) if (top_n * cap_val) < 1.0 else top_n)
    weights, deg3 = _sizing(combined, effective_n, v["C_sizing"], vol20[cols],
                            mkt_cap_w=mkt_cap_w, rets60_mean=rets60_mean,
                            rets60_var=rets60_var, rank_pre=rank)
    if deg3:
        degraded.append("C_sizing")
    weights = _apply_freq_trigger(weights, v["D1_rebalance_freq"], v["D2_rebalance_trigger"])
    weights = _apply_cap_and_lambda(weights, v["E_single_cap"], v["H_turnover_lambda"])
    return weights, tuple(degraded)


def stratified_sample(expansion, n_samples: int, seed: int,
                      stratify_dims: tuple[str, ...] = ()):
    """分层均匀抽样；n_samples>=N_raw 时全量直返。

    stratify_dims 空=按 signal 侧 prefix_key 分层（默认）；
    指定维度（如 G_universe,A1_factor_normalize,B_top_n）=按结构知识强轴分层
    （批次 A 定向扩容：强交互维每层加密，弱轴自然摊开）。
    """
    recipes = list(expansion.recipes)
    if n_samples >= len(recipes):
        return recipes
    rng = np.random.default_rng(seed)
    by_prefix: dict[str, list] = {}
    if stratify_dims:
        for r in recipes:
            key = "|".join(r.values.get(d, "?") for d in stratify_dims)
            by_prefix.setdefault(key, []).append(r)
    else:
        for r in recipes:
            by_prefix.setdefault(r.prefix_key, []).append(r)
    keys = sorted(by_prefix)
    picked: list = []
    if n_samples < len(keys):
        # 层数细于样本数: 随机抽层，每层 1 条（保证无重复且恰 n 条）
        layer_idx = rng.choice(len(keys), size=n_samples, replace=False)
        for i in layer_idx:
            pool = by_prefix[keys[i]]
            picked.append(pool[int(rng.integers(len(pool)))])
        return picked
    # 补齐余数（确定性: 全池洗牌后取前差值）
    if len(picked) < n_samples:
        chosen_ids = {r.recipe_id for r in picked}
        rest = [r for r in recipes if r.recipe_id not in chosen_ids]
        rest.sort(key=lambda r: r.recipe_id)
        rng.shuffle(rest)
        picked.extend(rest[: n_samples - len(picked)])
    return picked[:n_samples]


def run_batch(n_samples: int, seed: int, start: str, end: str, smoke: bool = False,
              subspace: dict[str, list[str]] | None = None,
              stratify_dims: tuple[str, ...] = ()) -> dict:
    """批次 A 主入口。返回 summary dict；manifest/negatives 落 data/strategy_intake/grid_<ts>/。"""
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    load_px, wide, filter_st, load_st_flags, run_backtest, daily_net_returns = _load_engine()
    compiler = GridCompiler.from_yaml(SCHEMA_PATH)
    expansion = compiler.compile(DEFAULT_CONTEXT)
    recipes_all = list(expansion.recipes)
    if subspace:
        # 批次 B 子空间枚举（裁定: A 给出的高价值子空间全因子穷尽——过滤即全跑，非抽样）
        recipes_all = [r for r in recipes_all
                       if all(r.values.get(k) in vs for k, vs in subspace.items())]
    class _Sub:
        pass
    sub_view = _Sub()
    sub_view.recipes = recipes_all
    sub_view.n_raw = len(recipes_all)
    picked = stratified_sample(sub_view, 8 if smoke else n_samples, seed,
                               stratify_dims=stratify_dims)
    run_ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = INTAKE_DIR / f"grid_{run_ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 数据一次拉取（窗口外多留 120 日算因子预热）
    import datetime as _dt

    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=200)).date().isoformat()
    px = load_px(warm_start, end, fields=("close", "volume"))
    closes_all = wide(px, "close")
    closes = closes_all.loc[(closes_all.index >= pd.Timestamp(start)) & (closes_all.index <= pd.Timestamp(end))]
    flags = load_st_flags(start, end)
    closes_eval = filter_st(closes_all, flags).loc[closes.index]

    universe_cache: dict[str, set[str]] = {}
    factors_cache: dict[str, dict[str, pd.DataFrame]] = {}
    # T2c: g → (closes_eval[cols], vol20[cols]) 切片一次复用（免每格点重切 T×S）；prefix 级 combined 缓存
    slice_cache: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}
    combine_cache: dict = {}  # (G,A1,A2) → (combined, rank, a1_deg, a2_deg)
    vol20 = closes_eval.pct_change().rolling(20).std()
    # T2a 精确实现数据面: 市值宽表 + 60 日收益矩（mkt_cap/kelly sizing 消费）
    mkt_cap_w = _load_mkt_cap_wide(warm_start, end, closes_all.columns)
    rets_daily = closes_eval.pct_change()
    rets60_mean = rets_daily.rolling(60).mean()
    rets60_var = rets_daily.rolling(60).var()
    # T2b 行业族数据面: 行业锚一次拉取（失败→None，行业族格点 fail-closed 降级记 degraded）
    try:
        industry_map = _industry_map()
    except Exception as exc:  # noqa: BLE001
        import logging as _lg

        _lg.getLogger(__name__).warning("行业锚加载失败，A1 行业族降级 zscore（degraded）: %s", exc)
        industry_map = None

    manifest_rows: list[GridEvalOutcome] = []
    negatives: list[NegativeRecord] = []
    nets_for_neff: dict[str, list[float]] = {}
    eval_dead = bt_dead = 0
    for r in picked:
        g = r.values["G_universe"]
        if g not in universe_cache:
            try:
                universe_cache[g] = _load_universe(g, start, end)
            except Exception as exc:  # noqa: BLE001
                negatives.append(NegativeRecord(r.recipe_id, "eval", f"universe_load_fail:{type(exc).__name__}",
                                                r.values, "", str(exc)[:120]))
                eval_dead += 1
                continue
        cols = [c for c in universe_cache[g] if c in closes_eval.columns]
        if len(cols) < 30:
            negatives.append(NegativeRecord(r.recipe_id, "eval", "universe_too_small", r.values, "", f"cols={len(cols)}"))
            eval_dead += 1
            continue
        if g not in factors_cache:
            closes_g = closes_eval[cols]
            factors_cache[g] = compute_v1_factors(closes_g)
            slice_cache[g] = (closes_g, vol20[cols])
        closes_g, vol20_g = slice_cache[g]
        try:
            weights, degraded = evaluate_recipe(r, closes_g, factors_cache[g], vol20_g, cols,
                                                mkt_cap_w=mkt_cap_w, rets60_mean=rets60_mean,
                                                rets60_var=rets60_var, industry_map=industry_map,
                                                combine_cache=combine_cache)
        except Exception as exc:  # noqa: BLE001
            negatives.append(NegativeRecord(r.recipe_id, "eval", f"eval_fail:{type(exc).__name__}",
                                            r.values, "", str(exc)[:120]))
            eval_dead += 1
            continue
        try:
            stats = run_backtest(weights, closes_g)
            net = daily_net_returns(weights, closes_g)
            if len(net.dropna()) < 60 or float(net.std()) == 0:
                raise RuntimeError(f"insufficient_net:{len(net)}")
            sharpe = stats["sharpe"]
            nets_for_neff[r.recipe_id] = [float(v) for v in net.values]
        except Exception as exc:  # noqa: BLE001
            negatives.append(NegativeRecord(r.recipe_id, "backtest", f"backtest_fail:{type(exc).__name__}",
                                            r.values, ",".join(degraded), str(exc)[:120]))
            bt_dead += 1
            continue
        manifest_rows.append(GridEvalOutcome(r.recipe_id, r.prefix_key, r.values, degraded,
                                         sharpe=sharpe, ann_return=stats["ann_return"],
                                         max_drawdown=stats["max_drawdown"],
                                         avg_turnover=stats["avg_turnover_1side"], net_days=len(net)))

    # N_eff（预注册 effective_rank）——批次级双口径披露+账本披露位（非 smoke 才写账本）
    n_eff: int | None = None
    n_eff_meta: dict = {}
    try:
        from zephyr.backtest.core.n_trial_ledger import compute_effective_rank

        if len(nets_for_neff) >= 2:
            n_eff, n_eff_meta = compute_effective_rank(nets_for_neff)
            if not smoke:
                from zephyr.backtest.core.n_trial_ledger import TrialLedger

                TrialLedger().set_effective_trials(
                    n_eff, note=f"batch:{run_ts} n={len(nets_for_neff)} meta={json.dumps(n_eff_meta)}"
                )
    except Exception as exc:  # noqa: BLE001 N_eff 失败不阻断批次产物（披露位留空诚实缺）
        import logging as _lg

        _lg.getLogger(__name__).warning("N_eff 计算失败（披露位留空）: %s", exc)

    # T2c 收益序列档案: 成功格点 net 序列落盘（行=交易日 T，列=recipe_id）——
    # DSR 精确口径数据基础；环境无 pyarrow 时兜底 csv.gz
    net_returns_file: str | None = None
    if nets_for_neff:
        nr = pd.concat([pd.Series(v, name=k) for k, v in nets_for_neff.items()], axis=1)
        try:
            nr_path = out_dir / "net_returns.parquet"
            nr.to_parquet(nr_path)
        except (ImportError, ModuleNotFoundError):
            nr_path = out_dir / "net_returns.csv.gz"
            nr.to_csv(nr_path, index=False, compression="gzip")
        net_returns_file = nr_path.name

    manifest = pd.DataFrame([asdict(o) | {"values_json": json.dumps(o.values, sort_keys=True)} for o in manifest_rows])
    manifest.drop(columns=["values"]).to_csv(out_dir / "manifest.csv", index=False)
    neg_df = pd.DataFrame([asdict(n) for n in negatives])
    neg_df.to_csv(out_dir / "negatives.csv", index=False)
    summary = {
        "run_ts": run_ts,
        "mode": "smoke" if smoke else ("batch_b_subspace" if subspace else "batch_a_census"),
        "subspace": subspace or None,
        "stratify_dims": list(stratify_dims) or None,
        "n_raw": expansion.n_raw, "n_sampled": len(picked),
        "evaluated": len(manifest_rows), "eval_dead": eval_dead, "backtest_dead": bt_dead,
        "degraded_recipes": int(manifest["degraded_dimensions"].apply(bool).sum()) if len(manifest) else 0,
        "window": [start, end], "seed": seed,
        "out_dir": str(out_dir),
        "net_returns_file": net_returns_file,
        "n_trials_effective": n_eff,
        "n_eff_meta": n_eff_meta,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="F-06 批次 A 普查执行器")
    ap.add_argument("--smoke", action="store_true", help="烟测：8 格点管线联通")
    ap.add_argument("--n-samples", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default="2023-12-31")
    ap.add_argument("--stratify-dims", default="", help="逗号分隔定向分层维（批次 A 扩容）")
    ap.add_argument("--subspace-json", default="", help='子空间枚举 JSON（批次 B）')
    args = ap.parse_args()
    import json as _json
    subspace = _json.loads(args.subspace_json) if args.subspace_json else None
    stratify = tuple(d for d in args.stratify_dims.split(",") if d)
    s = run_batch(args.n_samples, args.seed, args.start, args.end, smoke=args.smoke,
                  subspace=subspace, stratify_dims=stratify)
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


# noqa: m11-perm-manual-legitimate  F-06 批处理跑批件: CLI 手动/计划任务触发与 c4_batch_screen 同类，
# 非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界批处理作业
if __name__ == "__main__":
    raise SystemExit(main())
