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
  T3（2026-09-24）: 方案①两轮制 stage-aware 成本档位（裁定#413 下一窗口升级案）:
            run_batch 新增 keyword-only cost_gate_tiers_bp——None（缺省）=现行行为
            逐位零漂移（不做 per-point 档位扫描）；传入档位集（T1 轻档 [0,5] 两档 /
            T2 全档 [0,5,10,20,40]）时每成功格点经 exam_cost_gate.run_cost_tier_scan
            做档位扫描（引擎口径唯一：daily_net_returns slippage_bp kwarg 档覆盖），
            扫描失败=gate 层阴性 fail-closed；档位子集真源分层——轻档=budget_caps.
            cost_gate_t1_tiers_bp（prereg，缺省=分层语义未启用），全档=config/
            exam_scale_cost_gate.yaml（禁双头硬编码）。manifest 新增
            cost_tier_sharpes_json/cost_adjusted_sharpe 两列、summary 新增
            cost_gate_tiers_bp/gate_dead 两键，均仅在档位扫描启用时写入。
  T4（2026-09-25）: 去重改造（st-ddup-20260925，行为逐位保持）: ①每格两连调
            run_backtest+daily_net_returns 合并为 run_backtest_full 单趟（stats/net
            逐位一致）；②档位扫描经引擎 net_returns_by_tiers 一趟派生多档 net 注入
            run_cost_tier_scan（nets_by_tier，逐档全量重算→标量成本线）；③掩码
            批级缓存向量化在引擎侧（_c4_engine），本件零语义变化只换调用面。
            实测依据=gpu_rewrite/hotspot_census.md §二（单 pass 74-95% 在掩码重建）。
  T5（2026-09-29）: gpu_rewrite P1+L1（st-gpup1-20260929，行为逐位保持）: ①批级
            张量预热——closes/rets 只依赖 (窗口,宇宙列集)，prep_px_tensor 每宇宙
            一次共享（原逐格重算），透传 pre_tensor；②成本门场景 run_backtest_full
            +net_returns_by_tiers 两连调合并为 run_backtest_full_with_tiers 单趟
            三产物（nets_by_tier 逐位一致，缺席回退原路，死亡层归因不变）；③计算
            后端开关 ZEPHYR_COMPUTE_BACKEND（缺省 auto=cupy 可用即 gpu FP64 张量核，
            env=cpu 恒原 pandas 路径零漂移），快路径资格=等形对齐（引擎侧判，
            gpu_core 零索引语义）。基准=docs/_working/gpu_rewrite/p1_wiring_benchmark.md。
  T6（2026-10-05）: T3a 开闸考 S 级五件接线（st-tclose-t3a-20261005，缺省路径逐位
            零漂移；挖矿真源=docs/_working/fullcirc_closeout_chief/t3_fullflow_exam_mining.md）:
            ①S1 J 总闸——J_regime_switch=on 格点经 owner_regime_switcher 冻结口径
            build_schedule 日级帽调度表×权重逐行乘（cap_t=max(cap_A,cap_B) 全包乘性帽），
            调度表数据缺失=eval 层整格阴性（NegativeRecord，禁静默）；manifest 条件增
            j_state 列（态分布 JSON 审计位）+批级 j_regime_schedule.csv 落盘；
            ②S2 成交价口径——exec_caliber=close|next_open|vwap 透传引擎（引擎侧实现，
            本件只做执行价宽表装载与 _vwap_from_amount_volume 量纲哨兵）；
            ③S3 估值财务因子面——factor_surface=v1_value 时 v1 三因子+f_ep/f_bp
            （load_valuation 日频 EOD）+f_np_yoy（fin 公告门 PIT，公告次一交易日生效）；
            数据缺席=eval 层整格阴性（fail-closed）；
            ④S4 护盘白名单内容登记——defensive_whitelist_assets() 引用 MOD-POS-026
            模块常量（AI 禁自填，登记≠启用，D114 休眠不破），t3 prereg defensive_leg
            对齐校验漂移=SystemExit；
            ⑤S5 归因 manifest 增列——cost_attribution_row() 冻结土规成本线精确分量
            分解（佣金/印花/滑点三份额+年化拖累；网格无订单对象，trade 级地板佣金
            效应不在网格语义内=诚实披露），cost_attribution=True 时条件并列；
            ⑥stage t3 家族（t3/t3-t1/t3-t2）——DEFAULT_CONTEXT 按 stage 参数化
            （t3 家族→phase=2 J 展开），预算钳制走 config/search_space_prereg_t3a.yaml
            （t3_points/t3_*_points/t3_per_point_seconds_measured fail-closed），
            成本档 t3=全档（exam_scale_cost_gate 真源）。

用法:
  python scripts/backtest/factory_grid_executor.py --smoke                 # 烟测（管线联通，8 格点）
  python scripts/backtest/factory_grid_executor.py --n-samples 20000       # 批次 A 普查
产出: data/strategy_intake/grid_<run_ts>/manifest.csv + negatives.csv + summary.json
  + T1 遥测件（batch_meta.json/progress.jsonl/heartbeat.jsonl/*_partial.csv，见 _GridInstruments）
"""

from __future__ import annotations

import argparse
import dataclasses
import faulthandler
import hashlib
import json
import os
import sys
import threading
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

#: 探索扫描分册开关（main 里由 --exploration-ledger 注入）：设值=批末不进 N 账本，
#: 批记录改追本路径（矿考班 GPU 深挖车道令②：不占考试试次，与 N 账本分册）
_EXPLORATION_LEDGER: str | None = None
#: eval 面上卡开关（main 里由 --eval-backend 注入）。缺省 "cpu"=本文件原 pandas 路，
#: 逐字节零漂移（判据面与数值面均不动）；"gpu"/"auto"=可移植面走 zephyr.backtest.gpu_core
#: 设备核，不可移植面按该件 eval 节头的既定 CPU 交接点回原路并计数出声。
#: 定靶凭据=docs/_working/gpufeed_campaign/01_gpux_t0_profile.md（今晚 38,956 格仪表：
#: eval=82.2% CPU-秒，其内命中路径 60.4%，all_a_ex_st 宇宙独占 74.2%）。
_EVAL_BACKEND: str = "cpu"
#: 设备面分流计数（观测面，不进 manifest 判据列；summary.eval_gpu 仅在非 cpu 时出现）
_EVAL_GPU_STATS: dict[str, int] = {
    "prefix_gpu": 0,
    "prefix_cpu_kept": 0,
    "cell_gpu": 0,
    "cell_host_continue": 0,
    "cell_cpu_kept": 0,
    "vram_refused": 0,
    "vram_unmeasured": 0,
    "host_mem_refused": 0,
    "host_mem_unmeasured": 0,
    "memory_pressure": 0,
    "resolve_not_gpu": 0,
    "dev_attempt_failed": 0,
}
#: 逐路显存预算缓存（None=未读；0=册无该键→不设闸并计数出声，见 _vram_per_path_budget_mib）
_VRAM_BUDGET_MIB: int | None = None
#: 逐路主机内存峰值预算缓存（同语义，见 _host_mem_per_path_peak_mib）
_HOST_MEM_BUDGET_MIB: int | None = None
#: 内存压力停卡旗（本格 MemoryError 后置位，本批不再上卡；见 _on_eval_memory_pressure）
_EVAL_MEM_PRESSURE: bool = False
#: 水位探针短时缓存 (采样时刻, 可用 MiB)——_dev_xp 逐格被调，禁每格一次系统调用
_HOST_MEM_PROBE: tuple[float, int] | None = None
_HOST_MEM_PROBE_TTL_S: float = 5.0
#: 册上 budget_caps 子块缓存（section→dict；读败/缺册={}，两路预算共用同一加载口）
_PREREG_BUDGET_SECTIONS: dict[str, dict] = {}
#: 批级设备面板缓存（键含入参对象身份=批轮换自然失效；容量上限逐出防显驻膨胀）
_DEV_PANEL_CACHE: dict = {}
# NO-BARE-SQL + TABLE-NAME-REGISTRY 配方: SQL 常量化+表名走 TableRegistry 真源
from zephyr.data.table_registry import get_registry as _get_table_registry

# category_id=meta_stock_basic（business_data_categories.yaml 真源），TableRegistry 解析全限定表名
_SQL_MV = (
    "SELECT trade_date, symbol, toFloat64(total_mv) AS total_mv FROM "
    + _get_table_registry().table("market_stock_indicator")
    + " WHERE trade_date >= '{start}' AND trade_date <= '{end}' AND total_mv > 0"
)
_SQL_ALL_A = (
    "SELECT DISTINCT symbol FROM "
    + _get_table_registry().table("meta_stock_basic")
    + " WHERE valid_to IS NULL AND name NOT LIKE '%ST%' AND name NOT LIKE '%退%'"
)
# T2b 行业锚: c1_market.industry_class L1 现行快照（category_id=market_industry_class 真源反查）
_SQL_INDUSTRY_MAP = (
    "SELECT symbol, industry_sw, valid_from, updated_at FROM "
    + _get_table_registry().table("market_industry_class")
    + " WHERE industry_level = 1 AND valid_to IS NULL"
)
# 行业词表真源（sws2021_l1 = schema industry_anchor.vocabulary_source；禁硬编码行业清单）
_SWS_VOCAB_SOURCE = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "io_sector_sws_map.yaml"
# v1 因子集（F-02 接线后扩展；全部从 close 现算，零额外依赖）
V1_FACTORS = ("f_mom20", "f_lowvol20", "f_ma_gap")


@dataclass(frozen=True)
class NegativeRecord:
    """阴性配方记录——死亡层+死因缺失即校验拒绝（机械可校验）。"""

    recipe_id: str
    death_layer: str  # eval / backtest / gate
    death_reason: str  # 结构化原因码（禁空串）
    values: dict[str, str]
    degraded_dimensions: str  # 逗号分隔降级维（空=无）
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
    backend: str = ""  # L2-C：实际计算后端（gpu|cpu；引擎 stats 披露透传，空=引擎旧版）
    degrade: str = ""  # L2-C：守卫/降级结构化原因码（空=未降级；=引擎 stats guard_reason）


class _GPUWaveFailure(RuntimeError):
    """L2-C：GPU 波失败（fail-closed 信号）——整波弃置并重跑 CPU，禁半成品混合后端批次。"""


#: --engine 三态（L2-C）：cpu=恒 pandas 原路；gpu=显式张量核（无视尺寸守卫，波败 fail-closed
#: 重跑 CPU）；auto=按 env/守卫逐格解析（缺省=缺省行为）。非法值=ValueError。
_VALID_ENGINES: tuple[str, ...] = ("cpu", "gpu", "auto")


def _load_engine():
    from _c4_engine import (
        daily_net_returns,
        filter_st,
        load_px,
        load_st_flags,
        net_returns_by_tiers,
        prep_px_tensor,
        run_backtest_full,
        run_backtest_full_with_tiers,
        wide,
    )

    return (
        load_px,
        wide,
        filter_st,
        load_st_flags,
        run_backtest_full,
        daily_net_returns,
        net_returns_by_tiers,
        prep_px_tensor,
        run_backtest_full_with_tiers,
    )


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


# T3a 因子面取值域（S3 接线；v1_value=v1 三因子+f_ep/f_bp+f_np_yoy，挖矿 §2-S3）
FACTOR_SURFACES: tuple[str, ...] = ("v1", "v1_value")


def compute_value_factors(val_pe: pd.DataFrame, val_pb: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """S3 估值因子面（载荷=引擎 load_valuation 在册，日频 EOD 快照 PIT 与 v1 同口径）。

    f_ep=盈利收益率 1/PE、f_bp=账面市值比 1/PB。档语义：pe/pb≤1（含亏损 pe<0 与近零
    奇异值）→NaN，不留符号噪声进截面；截面尺度交 A1 标准化（raw 档依赖该守卫）。
    """

    def _inv(df: pd.DataFrame) -> pd.DataFrame:
        return 1.0 / df.where(df > 1.0)

    return {"f_ep": _inv(val_pe), "f_bp": _inv(val_pb)}


def _fin_np_yoy_panel(hist: pd.DataFrame, trade_days: pd.DatetimeIndex, columns: pd.Index) -> pd.DataFrame:
    """S3 财务因子日频 PIT 面板：np_q_yoy 按公告门生效（公告次一交易日可见）。

    实现：(announce_date×symbol) 宽表 → reindex(trade_days, ffill)=公告日当日可见
    → 整表 shift(1) 行位=次一交易日生效（公告多为盘后，当日即用=前视防御；
    比 announce_date+1 自然日更严且对齐交易日历）。缺数据票恒 NaN。
    """
    h = hist.dropna(subset=["np_q_yoy"]).sort_values(["symbol", "report_period", "announce_date"])
    if h.empty:
        return pd.DataFrame(np.nan, index=trade_days, columns=columns)
    w = h.pivot_table(index="announce_date", columns="symbol", values="np_q_yoy", aggfunc="last").sort_index()
    panel = w.reindex(trade_days.union(w.index)).ffill().reindex(trade_days).shift(1)
    return panel.reindex(columns=columns)


def _load_fin_np_yoy_history() -> pd.DataFrame:
    """S3 财务历史全量（复用引擎 fin_history 公告门装载，整表一次入缓存）。"""
    from _c4_engine import fin_history

    return fin_history(as_of="2099-12-31", metrics=("np_q_yoy",))


def _apply_regime_caps(weights: pd.DataFrame, schedule: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """S1 J 总闸（挖矿 §2-S1）：owner_regime_switcher 日级帽调度表×权重矩阵逐行乘。

    帽语义（prereg honesty 钉定）：cap_t=max(cap_A,cap_B)——全包乘性帽（任一策略包
    获准的敞口上限即考卷组合可部署上限）；trend_down 空帽=0（总闸全关）。
    已知失真（挖矿 §4.6）：本帽≠TDM L1 六态挂载矩阵（多格 pending-owner-adoption）。
    返回 (缩放后权重, 态分布计数)。
    """
    cap = schedule[["cap_A", "cap_B"]].max(axis=1)
    cap = cap.reindex(weights.index).fillna(0.0)
    dist = schedule["state"].value_counts().to_dict()
    return weights.mul(cap, axis=0), {str(k): int(v) for k, v in dist.items()}


def _load_j_regime_schedule(trade_days: pd.DatetimeIndex) -> pd.DataFrame:
    """S1 调度表装载（owner_regime_switcher 冻结口径：PIT 翻转次日生效+置信门+滞后带
    +失败安全全在库，钉用 run_id=数据装载器真源）。数据缺失=异常上抛（调用方记
    eval 层整格阴性，fail-closed 禁静默——挖矿 §3.3.5）。"""
    from zephyr.strategy_factory.owner_regime_switcher.data_loader import load_regime_snapshots
    from zephyr.strategy_factory.owner_regime_switcher.switcher import SwitcherConfig, build_schedule

    snaps = load_regime_snapshots()
    return build_schedule(pd.DatetimeIndex(trade_days), snaps, SwitcherConfig())


def defensive_whitelist_assets() -> dict:
    """S4 护盘白名单内容登记（挖矿 §2-S4；真源引用，AI 禁自填内容）。

    内容真源=MOD-POS-026 DEFAULT_TIER1/TIER2（TDM-X-R1-03 module_ref 落码件）；
    登记≠启用：D114 休眠铁律不破（enabled=False），state_matrix euphoria/distribution
    防御格仍 pending-owner-adoption（格子内容=Owner 资金分配门位）。本件只把内容
    机读化供 T3a prereg 卡 defensive_leg 对齐校验与考卷预检消费。
    """
    from zephyr.position.core.defensive_asset_whitelist import DEFAULT_TIER1, DEFAULT_TIER2

    return {
        "tier1": list(DEFAULT_TIER1),
        "tier2": list(DEFAULT_TIER2),
        "source_module": "MOD-POS-026",
        "enabled": False,
    }


def _validate_defensive_whitelist_registration(prereg_assets: dict) -> None:
    """T3a prereg defensive_leg 与 MOD-POS-026 真源对齐校验（内容漂移=SystemExit fail-closed）。"""
    truth = defensive_whitelist_assets()
    if (
        list(prereg_assets.get("tier1") or []) != truth["tier1"]
        or list(prereg_assets.get("tier2") or []) != truth["tier2"]
    ):
        raise SystemExit("[prereg-t3a] defensive_leg 资产与 MOD-POS-026 白名单真源漂移——登记内容非法，禁开跑")


def cost_attribution_row(avg_turnover_1side: float, days: int, slippage_bp: float | None) -> dict[str, float]:
    """S5 归因 manifest 增列（挖矿 §2-S5）：冻结土规成本线的精确分量分解。

    恒等式（引擎 _backtest_core/_net_line 同式）：cost_d = turnover_d×k/1e4，
    k = 佣金2.5bp×2双边+印花10bp卖+滑点档×2双边；total = avg_turnover_1side（引擎
    stats 实测均值）×days×k/1e4——从 stats 精确还原，免重算权重路径（封板闸后
    executed 权重的 turnover 只在引擎内），分量占比为恒等式确定性分解（非估计）。
    诚实边界：网格向量化无订单对象，框架 trade 级 CostAttribution（MOD-BT-001）的
    名义相关效应（地板佣金/碎片化）不在网格语义内——本分解只覆盖平档成本线。
    """
    from _c4_engine import COMMISSION_BP, SLIPPAGE_BP, STAMP_BP  # 冻结土规常量唯一真源（引擎侧）

    slip = SLIPPAGE_BP if slippage_bp is None else float(slippage_bp)
    k_bp = COMMISSION_BP * 2.0 + STAMP_BP + slip * 2.0
    t1 = float(avg_turnover_1side)
    return {
        "cost_drag_total": t1 * float(days) * k_bp / 1e4,
        "cost_drag_annual": t1 * 244.0 * k_bp / 1e4,
        "cost_commission_share": (COMMISSION_BP * 2.0) / k_bp,
        "cost_stamp_share": STAMP_BP / k_bp,
        "cost_slippage_share": (slip * 2.0) / k_bp,
    }


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


def _normalize(
    factor: pd.DataFrame, mode: str, industry_map: dict[str, str] | None = None, mkt_cap_w: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, bool]:
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


def _ic_weight_frame(ic_all: pd.DataFrame, mode: str, names: list[str], dates) -> pd.DataFrame:
    """IC 族日权重矩阵——从 _combine 原样搬出（逐式同序同算子，纯位置挪移）。

    提取动机=eval 面上卡时设备侧只承担 (T,S) 的秩与行归约，本矩阵对象是 (T,F)（F≤8），
    上卡无收益且会造出第二实现面（漂移源）；故 CPU/GPU 两条前缀路共用本函数——
    禁复制本段（RULE-CLONEGUARD，且复制=判据分叉）。
    """
    if mode == "ic_mean":
        w = ic_all.rolling(60, min_periods=20).mean()
    elif mode == "ic_ir":
        w = ic_all.rolling(60, min_periods=20).mean() / (ic_all.rolling(60, min_periods=20).std() + 1e-12)
    else:
        span = 20 if mode == "halflife20" else 60
        w = ic_all.ewm(halflife=span, min_periods=10, adjust=False).mean()
    w = w.clip(lower=0.0).shift(1)  # ← 前视防御: d 日只用截至 d-1 的 IC
    w = w.div(w.sum(axis=1).replace(0, np.nan), axis=0)
    return w.reindex(dates).fillna(1.0 / len(names))


def _combine(
    factors: dict[str, pd.DataFrame], normalized: list[pd.DataFrame], mode: str, closes: pd.DataFrame
) -> tuple[pd.DataFrame, bool]:
    """A2 合成。返回 (合成截面, degraded)。

    IC 类权重=60 日滚动 rank-IC（ic_mean 均值 / ic_ir 均值÷std / halflife 指数衰减均值），
    **shift(1) 前视防御：第 d 日合成只用截至 d-1 的 IC**（d 日因子预测 d→d+1 收益，
    权重若含 d 日 IC 即用了未来收益——bt-fin-correctness 前视铁律）。
    """
    names = list(factors.keys())
    dates = closes.index
    # 因子面异基对齐（20261006 T0 标定实钓）: v1_value 面 val_pe/pb 挂 warm 面板行而
    # v1/f_np_yoy 挂考窗行——orth_equal 逐帧 to_numpy 广播炸、lasso/pc1 np.stack 同形炸
    # （200 格 83 死全在 A2∈{lasso,orth_equal,pc1}）。入口统一 reindex 考窗 index；
    # 同基输入 reindex 恒等=逐位零漂移。
    normalized = [nf.reindex(dates) for nf in normalized]
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
        w = _ic_weight_frame(ic_all, mode, names, dates)
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
                    mdl = Lasso(
                        alpha=1e-4, fit_intercept=False, max_iter=2000, tol=1e-4, selection="random", random_state=0
                    )
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


def _sizing(  # noqa: long-param-list  存量函数签名（E4成本门接线仅追加net_fn/config两参，重构归批F账）
    scores: pd.DataFrame,
    top_n: int,
    mode: str,
    vol20: pd.DataFrame,
    mkt_cap_w: pd.DataFrame | None = None,
    rets60_mean: pd.DataFrame | None = None,
    rets60_var: pd.DataFrame | None = None,
    rank_pre: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, bool]:
    """B 选股 + C 定尺寸。返回 (weights 截面, degraded)。

    rank_pre（T2c 缓存加速）: 同一 scores 已算好的 rank（combined 缓存随附）；
    rank 仅依赖 scores，传入时跳过重算，数值恒等。调用方保证 scores 对应关系。
    """
    # 可选输入面切列到 scores 列集（20261006 快路径诊断治本）：全 5055 列市值/rets60 面
    # × cols 秩面=列并集变形，等形守卫按列拒绝（mkt_cap/kelly 全数 CPU 的同根因；
    # 切列=额外列全 NaN 下游丢弃的逐位恒等，GPU 资格恢复）。
    if mkt_cap_w is not None:
        mkt_cap_w = mkt_cap_w.reindex(columns=scores.columns)
    if rets60_mean is not None:
        rets60_mean = rets60_mean.reindex(columns=scores.columns)
    if rets60_var is not None:
        rets60_var = rets60_var.reindex(columns=scores.columns)
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
    c = cap_map[cap]
    # cap=硬约束终态 clip，不再 renorm（renorm 会重新突破上限）：
    # 持仓数不足（等权 1/n > cap）时允许低仓位——约束优先于满仓，超额留现金
    w = w.clip(upper=c)
    l = _LAMBDA_PEN[lam] * 100.0  # λ 惩罚项放大为组合收缩系数（5bp/15bp→0.5/1.5 收缩比例）
    if l > 0:
        w = w.ewm(alpha=min(1.0, l), adjust=False).mean()
        rs = w.sum(axis=1).replace(0, np.nan)
        w = w.div(rs, axis=0).fillna(0.0)
    return w


_FREQ_STEPS: dict[str, int] = {"daily": 1, "weekly": 5, "biweekly": 10, "monthly": 21}
_LAMBDA_PEN: dict[str, float] = {"lambda_0": 0.0, "lambda_5bp": 0.0005, "lambda_15bp": 0.0015}


def _apply_freq_trigger(w: pd.DataFrame, freq: str, trigger: str) -> pd.DataFrame:
    """D1 频率 + D2 触发: 非调仓日沿用旧权重；drift_band=偏离>10% 才重平衡。

    T2c 性能（数值语义与逐日循环逐位等价）:
      periodic → 每 step 行取值: out[i] = w.iloc[(i//step)*step]，用
        iloc[::step].reindex(index, method='ffill') 一步到位（索引单调且第 0 行
        必为调仓日，ffill 语义严格等于逐日沿用旧权重）；step=1 短路直返。
      drift_band → 保持逐日循环但切 numpy 行数组（省 .loc 逐行标签查找）；
        np.nansum ≡ pandas row-sum skipna 语义，判阈 (|Δw|.sum()/2 > 0.10)。
    """
    step = _FREQ_STEPS[freq]
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


# —— eval 面上卡：设备面板/前缀核（仅 _EVAL_BACKEND 非 cpu 时启用；cpu 路径原样）——
# 分工铁律：设备只承担 (T,S) 全面板数学（秩/行归约/合成/定尺寸），算完照旧物化 pandas
# 对象交给下游——bt/成本门/manifest/台账面一行不改（判据面与算力面分离，
# docs/_working/gpu_rewrite/new_asset_gpu_cpu_checklist.md §二.4）。索引/列标签仍留 CPU
# （同件 §二.5 与 gpu_core 文件头 INVARIANTS）。
_DEV_CACHE_CAP: int = 12
_A1_DEV_PORTABLE: tuple[str, ...] = ("raw", "zscore", "rank", "industry_neutral", "size_neutral", "industsize_neutral")
_A2_DEV_PORTABLE: tuple[str, ...] = ("equal", "orth_equal", "ic_mean", "ic_ir", "halflife20", "halflife60")


def _prereg_budget_section(name: str) -> dict:
    """册上 `budget_caps.<name>` 子块（一次读盘+缓存；缺册/缺键/读败={}）。

    两路预算（显存/主机内存）共用本口，禁各写一份 yaml 加载（同段代码第二份=漂移面）。
    """
    if name not in _PREREG_BUDGET_SECTIONS:
        val: dict = {}
        try:
            import yaml

            cfg = yaml.safe_load(PREREG_PATH.read_text(encoding="utf-8")) or {}
            sec = (cfg.get("budget_caps") or {}).get(name)
            if isinstance(sec, dict):
                val = sec
        except Exception as exc:  # noqa: BLE001 — 预算读不到不得影响出分
            _instr_warn("prereg_budget_section", exc)
        _PREREG_BUDGET_SECTIONS[name] = val
    return _PREREG_BUDGET_SECTIONS[name]


def _vram_per_path_budget_mib() -> int:
    """册上逐路显存预算（`budget_caps.vram.per_path_budget_mib`）——本件是该键的**消费方**。

    为何要在代码里读：总统统筹 2026-10-11 05:3x 裁定③要求"并发数按 NVML 实测显存入册、
    禁册上写 1 实际跑 6 的漂移态"。只改 yaml 不接消费方＝又一个空转面（在册同类教训），
    故这里把预算变成准入闸：显存不足的那一路自己退回 CPU，实际并发被显存自限而非靠自觉。
    缺册/缺键/读败=返回 0（不设闸）并计入 vram_unmeasured，禁把"读不到"当成"不许跑"。
    """
    global _VRAM_BUDGET_MIB
    if _VRAM_BUDGET_MIB is None:
        try:
            val = int(_prereg_budget_section("vram").get("per_path_budget_mib") or 0)
        except (TypeError, ValueError):
            val = 0
        _VRAM_BUDGET_MIB = val
    return _VRAM_BUDGET_MIB


def _host_mem_per_path_peak_mib() -> int:
    """册上逐路主机内存峰值预算（`budget_caps.host_mem.per_path_peak_mib`）。

    第二道腿的来源=2026-10-11 N-3 实测事故：六路 × 逐路峰值 RSS 4.4GB 把主机 RAM 打到零，
    s0/s4 两路 GPU 波在 numpy 分配 (970,5058) int64（37.4MiB）时 MemoryError →
    按既定 fail-closed 整波重跑 CPU。显存够 ≠ 跑得动，册上只写显存腿就是新的"册实漂移"。
    """
    global _HOST_MEM_BUDGET_MIB
    if _HOST_MEM_BUDGET_MIB is None:
        try:
            val = int(_prereg_budget_section("host_mem").get("per_path_peak_mib") or 0)
        except (TypeError, ValueError):
            val = 0
        _HOST_MEM_BUDGET_MIB = val
    return _HOST_MEM_BUDGET_MIB


def _host_avail_mem_mib() -> int:
    """主机可用 RAM（MiB），经在册唯一水位口 host_resource_governor.probe_system_watermark。

    自造 ctypes/psutil 第二份探测＝克隆且与告警口径分家（RULE-SSOT）；本件只做 5s 短时缓存。
    返回 -1=不可测（探针失手），调用方据此计数不拦路。
    """
    global _HOST_MEM_PROBE
    now = time.perf_counter()
    if _HOST_MEM_PROBE is not None and now - _HOST_MEM_PROBE[0] < _HOST_MEM_PROBE_TTL_S:
        return _HOST_MEM_PROBE[1]
    val = -1
    try:
        from zephyr.infrastructure.capacity_assurance.host_resource_governor import (
            probe_system_watermark,
        )

        avail_gb = float(probe_system_watermark().ram_avail_gb or 0.0)
        if avail_gb > 0:
            val = int(avail_gb * 1024)
    except Exception as exc:  # noqa: BLE001 — 水位读不到不得影响出分
        _instr_warn("host_mem_probe", exc)
    _HOST_MEM_PROBE = (now, val)
    return val


def _on_eval_memory_pressure(exc: BaseException) -> None:
    """内存压力=资源态不是判据态：卸设备面板缓存 + 本批停上卡 + 计数出声。

    病案（2026-10-11 N-3 GPU 波 053559）：六路上卡后主机侧多出暂存与 cupy 上下文，RAM 打到零，
    22 格在**纯 CPU 段**（本文件既有 eval 记账口）报 MemoryError→被记成 eval 阴性。
    同参纯 CPU 基线 p2（grid_20261010-233721）25,000 格 eval 阴性 0 支——差额全是我这侧的
    资源足迹，不是这 22 格的真值，故禁把分配失败当判决（判据面零动红线）。
    """
    global _EVAL_MEM_PRESSURE
    _EVAL_GPU_STATS["memory_pressure"] += 1
    _DEV_PANEL_CACHE.clear()
    if not _EVAL_MEM_PRESSURE:
        _EVAL_MEM_PRESSURE = True
        _instr_warn("eval_mem_pressure", exc)


def _eval_cell_mem_retry(fn):
    """跑一格的 eval 调用；MemoryError 先卸资源再重试一次，二次仍败照原样上抛给既有记账口。

    只重试一次：真·耗尽（重试仍失败）必须照旧出声，禁把资源态静默成"这格没问题"。
    """
    try:
        return fn()
    except MemoryError as exc:
        _on_eval_memory_pressure(exc)
        return fn()


def _dev_xp():
    """设备模块（cupy）或 None。后端解析一律经 gpu_core.resolve_backend（禁二套守卫）；
    显式 gpu 而不可用=该件降级台账出声，本处返回 None=前缀走原 pandas 路（fail-closed 到 CPU）。

    第二道闸=显存准入（册上预算的消费方）：free < per_path_budget_mib 即本路整体走 CPU 并计数，
    宁可慢也不把卡挤爆（本地 LLM/别的分片同卡时尤其要紧）。NVML 读不到时**不拦**，只计数。
    第三道闸=主机 RAM 准入（同册 budget_caps.host_mem）：可用 < 逐路峰值预算即本路不走设备面——
    设备面另加主机侧暂存（上传源面板/codes 面板），显存够而 RAM 不够时崩的是整波（N-3 实测）。
    """
    if _EVAL_BACKEND == "cpu":
        return None
    if _EVAL_MEM_PRESSURE:
        return None  # 本批已有一次 MemoryError：卸完资源也不再上卡，全程 CPU
    try:
        from zephyr.backtest.gpu_core import resolve_backend

        if resolve_backend(_EVAL_BACKEND) != "gpu":
            _EVAL_GPU_STATS["resolve_not_gpu"] += 1
            return None
        budget = _vram_per_path_budget_mib()
        if budget > 0:
            from zephyr.backtest.gpu_core import nvml_device_memory

            m = nvml_device_memory()
            if not m.get("available"):
                _EVAL_GPU_STATS["vram_unmeasured"] += 1
            elif int(m.get("free_mib") or 0) < budget:
                _EVAL_GPU_STATS["vram_refused"] += 1
                _instr_warn(
                    "vram_admission",
                    RuntimeError(f"free_mib={m.get('free_mib')} < per_path_budget_mib={budget}，本路降级 CPU"),
                )
                return None
        host_budget = _host_mem_per_path_peak_mib()
        if host_budget > 0:
            avail = _host_avail_mem_mib()
            if avail < 0:
                _EVAL_GPU_STATS["host_mem_unmeasured"] += 1
            elif avail < host_budget:
                _EVAL_GPU_STATS["host_mem_refused"] += 1
                _instr_warn(
                    "host_mem_admission",
                    RuntimeError(
                        f"avail_mib={avail} < per_path_peak_mib={host_budget}，本路降级 CPU（N-3 六路撞零实测）"
                    ),
                )
                return None
        import cupy as cp

        return cp
    except Exception as exc:  # noqa: BLE001 — 算力面缺失不得影响出分
        # 计数是这条路的**唯一**留证面：stderr 的 _instr_warn 在长跑里会被日志轮转吃掉，
        # 而 summary.eval_gpu 全零曾被本班读成"跑了但没上卡"（2026-10-11 06:32 假配对病案，见 02 件 级 3）。
        _EVAL_GPU_STATS["dev_attempt_failed"] += 1
        _instr_warn("eval_backend_resolve", exc)
        return None


def _dev_cache_put(key: tuple, val) -> None:
    if len(_DEV_PANEL_CACHE) >= _DEV_CACHE_CAP:
        _DEV_PANEL_CACHE.clear()  # 批轮换/宇宙切换=旧键失效，整清最省（面板数≤个位数）
    _DEV_PANEL_CACHE[key] = val


def _dev_panel(key: tuple, build, xp):
    """(T,S) 设备侧 float64 面板，按（入参对象身份+列切+窗）缓存→逐格零 H2D。

    build() 产主机侧 DataFrame（须已 reindex 到考窗行，与 _combine:526 的异基对齐同序——
    A1 全是逐行算子，先行对齐后求值与先求值后对齐逐行同解，但反过来不行：因子面板可能
    挂 warm 行或考窗行，不重index 就是拿错行号做截面）。
    """
    hit = _DEV_PANEL_CACHE.get(key)
    if hit is None:
        hit = xp.asarray(build().to_numpy(dtype=np.float64))
        _dev_cache_put(key, hit)
    return hit


def _dev_col_codes(cols, industry_map: dict[str, str] | None):
    """列→组整数编码（无锚列=-1）+ 组数。与 _demean_by_group 的列标签分组同解：
    组号分配序不影响语义（只做同组聚合与回填）。"""
    if not industry_map:
        return None, 0
    gidx: dict[str, int] = {}
    codes = []
    for c in cols:
        g = industry_map.get(c)
        if g is None:
            codes.append(-1)
        else:
            if g not in gidx:
                gidx[g] = len(gidx)
            codes.append(gidx[g])
    return np.asarray(codes, dtype=np.int64), len(gidx)


def _dev_log_mv(mkt_cap_w, cols, dates, xp):
    """log(市值) 控制板——与 _normalize:497 的 `np.log(mv.where(mv>0))` 同式，先主机后上卡。"""
    return _dev_panel(
        ("logmv", id(mkt_cap_w), len(cols), cols[0], cols[-1], len(dates)),
        lambda: np.log(mkt_cap_w.where(mkt_cap_w > 0))[cols].reindex(dates),
        xp,
    )


def _dev_fwd_ranked(closes, cols, xp):
    """前向收益的截面秩（IC 族右端项）。收益本身仍由 pandas 原式 pct_change().shift(-1)
    产生（含 pad 缺省填充语义），只把 0.7s/档的秩搬上卡——禁在算力面重造 pct_change。"""
    import zephyr.backtest.gpu_core as gc

    key = ("fwdrank", id(closes), len(cols), cols[0], cols[-1])
    hit = _DEV_PANEL_CACHE.get(key)
    if hit is None:
        fwd = closes[cols].pct_change().shift(-1)
        hit = gc._rank_rows(xp, xp.asarray(fwd.to_numpy(dtype=np.float64)), ascending=True)
        _dev_cache_put(key, hit)
    return hit


def _dev_ctrl_demeaned(mkt_cap_w, cols, dates, industry_map, xp):
    """log(市值) 先在全市场列集上做组内去均值、再切到宇宙列——factory `_normalize:505` 的口径。

    顺序不可换：先切片再去均值会把组均值从"全市场该行业"改成"宇宙内该行业"，那是另一套数
    （st-gpux-20261011 的 8 格真实对拍里，两支 industsize_neutral 格因此漂到 sharpe 4.9e-2，
    超 `verification_framework.md §一·补` 的 0.005 冻结线）。size_neutral 无组步骤，切片安全。
    """
    full_cols = list(mkt_cap_w.columns)
    key = ("logmvdm", id(mkt_cap_w), len(full_cols), len(dates), len(cols), cols[0], cols[-1])
    hit = _DEV_PANEL_CACHE.get(key)
    if hit is not None:
        return hit
    import zephyr.backtest.gpu_core as gc

    codes_f, ng_f = _dev_col_codes(full_cols, industry_map)
    if codes_f is None or ng_f <= 0:
        raise ValueError("industsize 控制板需行业锚覆盖市值面板列集")
    full = xp.asarray(np.log(mkt_cap_w.where(mkt_cap_w > 0)).reindex(dates).to_numpy(dtype=np.float64))
    dm = gc.normalize_rows(xp, full, "industry_neutral", codes=xp.asarray(codes_f), n_groups=ng_f)
    pos = xp.asarray([full_cols.index(c) for c in cols], dtype=np.int64)
    hit = dm[:, pos]
    _dev_cache_put(key, hit)
    return hit


def _a1_dev_mode(mode: str, has_industry: bool, has_mv: bool) -> tuple[str, bool]:
    """A1 模式派发到降级 zscore——与 _normalize:497-508 的锚缺失判定逐支同构（禁分叉）。"""
    if mode in ("raw", "rank", "zscore"):
        return mode, False
    if mode == "industry_neutral" and has_industry:
        return mode, False
    if mode == "size_neutral" and has_mv:
        return mode, False
    if mode == "industsize_neutral" and has_industry and has_mv:
        return mode, False
    return "zscore", True


def _prefix_eval_gpu(v, factors, closes, cols, industry_map, mkt_cap_w, xp):
    """A1+A2 前缀面的设备求值 → dict(combined, rank, a1_deg, a2_deg)（设备数组）。

    不可移植（lasso/pc1 与未知模式）返回 None=调用方走原 pandas 路，禁本函数自造近似。
    IC 族的 (T,F) 权重矩阵沿用 _ic_weight_frame（CPU 共用件，非复制）。
    """
    import zephyr.backtest.gpu_core as gc

    a1_req = v["A1_factor_normalize"]
    a2 = v["A2_combine_weight"]
    if a1_req not in _A1_DEV_PORTABLE or a2 not in _A2_DEV_PORTABLE:
        return None
    dates = closes.index
    codes, ng = _dev_col_codes(cols, industry_map)
    mv_ok = mkt_cap_w is not None
    # codes 是 ndarray：禁 bool(codes)（多元素数组求真值=ValueError，实测炸考格）；判"有无组锚"
    # 用 codes is not None and ng>0 两条件齐（无锚列全 -1 时 ng=0 也算无锚=与 factory 同降级）
    a1, a1_deg = _a1_dev_mode(a1_req, codes is not None and ng > 0, mv_ok)
    codes_dev = xp.asarray(codes) if codes is not None else None
    if a1 == "industsize_neutral":
        ctrl_dm = _dev_ctrl_demeaned(mkt_cap_w, cols, dates, industry_map, xp)  # 全市场列去均值
        ctrl = None
    elif a1 == "size_neutral":
        ctrl = _dev_log_mv(mkt_cap_w, cols, dates, xp)
        ctrl_dm = None
    else:
        ctrl = ctrl_dm = None
    names = list(factors.keys())
    normed = []
    for n in names:
        # 先按考窗行 reindex 再求值：A1 全是逐行算子，"先对齐后求值"与 factory 的
        # "先求值后 reindex(dates)"（_combine:526 异基对齐修复）逐行同解；反过来会拿
        # 因子自带的 warm 行号做截面=错行。
        arr = _dev_panel(
            ("f", n, id(factors[n]), len(cols), cols[0], cols[-1], len(dates)),
            lambda nn=n: factors[nn][cols].reindex(dates),
            xp,
        )
        if a1 == "industsize_neutral":
            normed.append(gc.industsize_rows(xp, arr, codes_dev, ng, ctrl_dm))
        else:
            normed.append(gc.normalize_rows(xp, arr, a1, codes=codes_dev, n_groups=ng, ctrl=ctrl))
    if a2 == "equal":
        combined = gc._equal_combine(xp, normed)
    elif a2 == "orth_equal":
        combined = gc.orth_equal_rows(xp, normed)
    else:
        fwd_ranked = _dev_fwd_ranked(closes, cols, xp)
        with np.errstate(all="ignore"):
            ic_cols = [gc.ic_pair_rows(xp, nf, fwd_ranked) for nf in normed]
        ic_np = np.column_stack([gc._to_numpy(c) for c in ic_cols])
        ic_all = pd.DataFrame(ic_np, index=dates, columns=names)
        w = _ic_weight_frame(ic_all, a2, names, dates)
        w_dev = _dev_panel(("w", id(w), a2, len(names)), lambda: w, xp)
        combined = gc.weighted_combine(xp, normed, w_dev)
    rank = gc._rank_desc_average(xp, combined)
    return {"combined": combined, "rank": rank, "a1_deg": a1_deg, "a2_deg": False}


def _cell_device_able(v) -> bool:
    """单格可上卡判据：叠加族（X_sector/J_regime/X_stop/X_breaker）全 off/缺席。
    这些族在权重之后还有各自的主机侧语义，本批不接管（如实留 CPU，不静默近似）。"""
    return (
        str(v.get("X_sector", "off")) == "off"
        and str(v.get("J_regime_switch", "off")) != "on"
        and str(v.get("X_stop", "off")) == "off"
        and str(v.get("X_breaker", "off")) == "off"
    )


def _cell_eval_gpu(v, dev_pair, combined, effective_n, cap_val, cols, vol20, mkt_cap_w, rets60_mean, rets60_var, xp):
    """单格定尺寸链上卡（T0 实测=eval 秒数的 60.4% 落在这一面）。失败/不可用返回 None。

    串行步（drift_band / lambda>0）由核内 host_continue 出声，本函数用**原 pandas 函数**
    续跑 trigger→cap 全序；periodic 行 gather 与 cap clip 均幂等（重跑逐位同），故续跑
    统一走两步、不分叉——分叉就多一条第二实现面。
    """
    import zephyr.backtest.gpu_core as gc

    idx = len(cols)
    try:
        vp = _dev_panel(("vol", id(vol20), idx, cols[0], cols[-1]), lambda: vol20[cols], xp)
        mc = (
            None
            if mkt_cap_w is None
            else _dev_panel(("mvw", id(mkt_cap_w), idx, cols[0], cols[-1]), lambda: mkt_cap_w[cols], xp)
        )
        rm = (
            None
            if rets60_mean is None
            else _dev_panel(("r60m", id(rets60_mean), idx, cols[0], cols[-1]), lambda: rets60_mean[cols], xp)
        )
        rv = (
            None
            if rets60_var is None
            else _dev_panel(("r60v", id(rets60_var), idx, cols[0], cols[-1]), lambda: rets60_var[cols], xp)
        )
        out = gc.eval_cell_gpu(
            dev_pair[0],
            dev_pair[1],
            top_n=effective_n,
            sizing_mode=v["C_sizing"],
            freq_step=_FREQ_STEPS[v["D1_rebalance_freq"]],
            trigger=v["D2_rebalance_trigger"],
            cap=cap_val,
            lam=_LAMBDA_PEN[v["H_turnover_lambda"]] * 100.0,
            vol20=vp,
            mkt_cap=mc,
            r60_mean=rm,
            r60_var=rv,
            backend="gpu",
        )
    except Exception as exc:  # noqa: BLE001 — 算力面异常一律回原路，禁半成品出分
        _instr_warn("cell_eval_gpu", exc)
        return None
    w = pd.DataFrame(np.asarray(out["weights"]), index=combined.index, columns=combined.columns)
    _EVAL_GPU_STATS["cell_gpu"] += 1
    if out["host_continue"]:
        _EVAL_GPU_STATS["cell_host_continue"] += 1
        w = _apply_freq_trigger(w, v["D1_rebalance_freq"], v["D2_rebalance_trigger"])
        w = _apply_cap_and_lambda(w, v["E_single_cap"], v["H_turnover_lambda"])
    return w


def evaluate_recipe(  # noqa: long-param-list  存量函数签名（E4成本门接线演进为10参，参数对象重构归批F账非本批）
    recipe,
    closes: pd.DataFrame,
    factors: dict[str, pd.DataFrame],
    vol20: pd.DataFrame,
    universe_cols: list[str],
    mkt_cap_w: pd.DataFrame | None = None,
    rets60_mean: pd.DataFrame | None = None,
    rets60_var: pd.DataFrame | None = None,
    industry_map: dict[str, str] | None = None,
    combine_cache: dict | None = None,
    j_schedule: pd.DataFrame | None = None,
    sector_ctx: dict | None = None,
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """recipe → (weights 宽表, degraded 维元组)。求值失败抛 RuntimeError（fail-closed，调用方记阴性）。

    combine_cache（T2c）: 按 (G,A1,A2) prefix 复用 combined 截面+rank——同 prefix 格点
    的 normalize/combine 输入确定则输出确定（industry_map/mkt_cap_w 批内恒定），rank 仅
    依赖 combined。命中时 A1/A2 degraded 标记一并复现，manifest 口径与无缓存逐位一致。
    j_schedule（T6 S1）: J_regime_switch=on 格点必需（缺席=RuntimeError，禁静默放行全帽）；
    off/无 J 维格点忽略——缺省 None 路径与 T5 语义逐位零漂移。
    sector_ctx（矩阵战役 W5）: X_sector 非 off 格点必需（板块强度面板 sector_surface
    批级产出；缺席=RuntimeError fail-closed）；off/无 X 维格点忽略=零漂移。
    """
    v = recipe.values
    degraded: list[str] = []
    cols = universe_cols
    combined: pd.DataFrame | None = None
    rank: pd.DataFrame | None = None
    cache_key = None
    dev_pair = None  # (combined, rank) 设备数组——仅 _EVAL_BACKEND 非 cpu 且核可用时存在
    xp = _dev_xp()
    if combine_cache is not None:
        cache_key = (v["G_universe"], v["A1_factor_normalize"], v["A2_combine_weight"])
        hit = combine_cache.pop(cache_key, None)
        if hit is not None:
            combine_cache[cache_key] = hit  # LRU 续期
            combined, rank, a1_deg, a2_deg, *dev_rest = hit
            dev_pair = dev_rest[0] if dev_rest else None
            if a1_deg:
                degraded.append("A1_factor_normalize")
            if a2_deg:
                degraded.append("A2_combine_weight")
    if combined is None:
        pres = None
        if xp is not None:
            try:
                pres = _prefix_eval_gpu(v, factors, closes, cols, industry_map, mkt_cap_w, xp)
            except Exception as exc:  # noqa: BLE001 — 设备面异常必降级 CPU 并出声
                # 禁让算力面的坑变成阴性格：假阴性=把可活策略判死，比慢一万倍严重（fail-closed 方向）
                _instr_warn("prefix_eval_gpu", exc)
                pres = None
        if pres is not None:
            # 设备面只产数组，pandas 对象照旧物化=下游 bt/成本门/manifest 零改动
            import zephyr.backtest.gpu_core as gc

            _EVAL_GPU_STATS["prefix_gpu"] += 1
            combined = pd.DataFrame(np.asarray(gc._to_numpy(pres["combined"])), index=closes.index, columns=cols)
            # rank 与 combined.rank(axis=1, ascending=False) 逐位同（层1 离散量，
            # test_eval_rank_rows_bitwise_layer1 钉），故缓存路径可直接沿用上卡产物
            rank = pd.DataFrame(np.asarray(gc._to_numpy(pres["rank"])), index=combined.index, columns=cols)
            dev_pair = (pres["combined"], pres["rank"])
            if pres["a1_deg"]:
                degraded.append("A1_factor_normalize")
            if pres["a2_deg"]:
                degraded.append("A2_combine_weight")
            if combine_cache is not None:
                _combine_cache_store(
                    combine_cache, cache_key, (combined, rank, pres["a1_deg"], pres["a2_deg"], dev_pair)
                )
        else:
            if xp is not None:
                _EVAL_GPU_STATS["prefix_cpu_kept"] += 1
            cl = closes[cols]
            normalized: list[pd.DataFrame] = []
            names = list(factors.keys())
            a1_deg = False
            for n in names:
                f = factors[n][cols]
                nf, deg = _normalize(f, v["A1_factor_normalize"], industry_map=industry_map, mkt_cap_w=mkt_cap_w)
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
                entry: tuple = (combined, rank, a1_deg, bool(deg2))
                if xp is not None:
                    # 不可移植前缀（lasso/pc1 等）也上传一次，命中格仍可走设备定尺寸链
                    entry = entry + (
                        (xp.asarray(combined.to_numpy(dtype=np.float64)), xp.asarray(rank.to_numpy(dtype=np.float64))),
                    )
                _combine_cache_store(combine_cache, cache_key, entry)
    # T3b X_sector 板块族叠加（矩阵战役 W5：L2-01 强度池+L2-06 传导后处理；phase>=3
    # 展开，折叠相恒 'off'=零漂移）。插入位=A1/A2 之后、B Top-N 之前（L2-06 卡 §4
    # 引擎接法=层级隔离：只调分不重排名，禁动 Top-N 语义）。
    sector_mode = v.get("X_sector", "off")
    if sector_mode != "off":
        if sector_ctx is None:
            raise RuntimeError("X_sector 非 off 需 sector_ctx（run_batch 批级板块面板）——fail-closed")
        combined = _apply_sector_overlay(combined, sector_ctx, industry_map or {}, sector_mode)
        rank = None  # 传导改分/池掩码改变截面序，缓存预计算 rank 作废（sizing 按新序重排）
    top_n = int(v["B_top_n"].replace("top", ""))
    # E cap 约束的持仓数扩展（B×E 交互的实务语义）: 满仓+单票≤cap 要求
    # M=ceil(1/cap) 只——M>top_n 时有效持仓数扩展为 M（仍按分数序取）
    cap_val = {"cap5": 0.05, "cap10": 0.10, "cap20": 0.20}[v["E_single_cap"]]
    effective_n = max(top_n, -(-1 // cap_val) if (top_n * cap_val) < 1.0 else top_n)
    weights = None
    if (
        dev_pair is not None
        and rank is not None
        and xp is not None
        and _cell_device_able(v)
        and vol20.index.equals(combined.index)
        and (mkt_cap_w is None or mkt_cap_w.index.equals(combined.index))
        and (rets60_mean is None or rets60_mean.index.equals(combined.index))
        and (rets60_var is None or rets60_var.index.equals(combined.index))
    ):
        # 等形守卫：pandas 的 base*mkt_cap_w 会按索引/列并集扩张，索引不等形时设备逐格
        # 乘算与它不同解——不等形即整格回原路（_c4_engine 等形资格守卫同族纪律）
        weights = _cell_eval_gpu(
            v, dev_pair, combined, effective_n, cap_val, cols, vol20, mkt_cap_w, rets60_mean, rets60_var, xp
        )
        if weights is None:
            _EVAL_GPU_STATS["cell_cpu_kept"] += 1
    if weights is None:
        weights, deg3 = _sizing(
            combined,
            effective_n,
            v["C_sizing"],
            vol20[cols],
            mkt_cap_w=mkt_cap_w,
            rets60_mean=rets60_mean,
            rets60_var=rets60_var,
            rank_pre=rank,
        )
        if deg3:
            degraded.append("C_sizing")
        weights = _apply_freq_trigger(weights, v["D1_rebalance_freq"], v["D2_rebalance_trigger"])
        weights = _apply_cap_and_lambda(weights, v["E_single_cap"], v["H_turnover_lambda"])
    if v.get("J_regime_switch") == "on":
        # T6 S1: 总闸帽最后生效（信号侧缓存不受影响；帽乘性缩放=额外换手的真实语义）。
        if j_schedule is None:
            raise RuntimeError("J_regime_switch=on 需日级帽调度表（run_batch 未加载）——fail-closed")
        weights, _j_dist = _apply_regime_caps(weights, j_schedule)
    # T3b X 族离场叠加（20261007 袋B 接线；phase>=3 展开，折叠相值恒 'off'=零漂移）。
    # 序钉（T3b 卡 v2 冻结位）：J 帽 → X_stop（个股离场清仓）→ X_breaker（组合帽收口，
    # 消费 post-stop 组合权益=对真实持仓反应，最保守）。未接线相缺省 'off'=恒等。
    stop_mode = v.get("X_stop", "off")
    if stop_mode != "off":
        weights, _ = _apply_exit_overlay(weights, closes, stop_mode)
    breaker_mode = v.get("X_breaker", "off")
    if breaker_mode != "off":
        weights, _ = _apply_dd_breaker_overlay(weights, closes, breaker_mode)
    return weights, tuple(degraded)


def stratified_sample(expansion, n_samples: int, seed: int, stratify_dims: tuple[str, ...] = ()):
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
            key = "|".join(str(r.values.get(d, "?")) for d in stratify_dims)
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


def _close_atr(closes: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """close-only ATR 代理（M1）：cATR=mean(|Δclose|,window)。

    考卷数据面只有 close（load_px fields 无 high/low），真 ATR（含跳空真实波幅）不可得
    ——本代理为诚实翻译，与真 ATR 的差距=T3b 冻结卡 honesty 披露位，禁冒充真 ATR。
    """
    return closes.diff().abs().rolling(window, min_periods=window).mean()


def _apply_exit_overlay(
    weights: pd.DataFrame,
    closes: pd.DataFrame,
    stop_mode: str,
    atr_window: int = 14,
) -> tuple[pd.DataFrame, str]:
    """M1 X 族离场叠加（X-S1-02 止损族 + X-S1-03 止盈族，T3b 考维引擎语义；T3a 不接线=零漂移）。

    日级向量化（挖矿 M1）：收盘判定触发（诚实位 §4.4 已知失真：触发滞后到收盘，双向失真
    之一如实入卷）；触发日该票权重清零，次日基础权重再入选=新持仓段（entry 重置）。
    - off：原样直返（恒等）
    - atr3x：入场价−3×cATR14 硬止损带（入场=持仓 0→1 翻转日，入场价=当日收盘）
    - trail20：持仓段收盘运行峰值×(1−0.20) 移动止盈（峰值按段重置）
    - tp20：入场价×1.20 目标价止盈
    返回 (调整后权重, stop_mode)。
    """
    if stop_mode == "off":
        return weights, stop_mode
    if stop_mode not in ("atr3x", "trail20", "tp20"):
        raise ValueError(f"未知 stop_mode: {stop_mode!r}（合法=off|atr3x|trail20|tp20）")
    held = weights > 0
    entry_day = held & ~held.shift(1, fill_value=False)
    entry_px = closes.where(entry_day).ffill()
    if stop_mode == "atr3x":
        level = entry_px - 3.0 * _close_atr(closes, atr_window)
        trigger = held & (closes < level)
    elif stop_mode == "trail20":
        # 段内运行峰值：stack 后按 (票, 段号) cummax 再 unstack（段号=入场日 cumsum，列独立；
        # where(held).stack 丢未持仓行，reindex 对齐段号再分组）。unstack 会丢"从未持仓"的
        # 票列与全空仓日期行——reindex 回 closes 全标签面（NaN→trigger False=诚实缺供）。
        regime = entry_day.cumsum()
        st = closes.where(held).stack()
        reg = regime.stack().reindex(st.index)
        peak = (
            st.groupby([st.index.get_level_values(1), reg])
            .cummax()
            .unstack()
            .reindex(index=closes.index, columns=closes.columns)
        )
        trigger = held & (closes < peak * (1.0 - 0.20))
    else:  # tp20
        trigger = held & (closes >= entry_px * 1.20)
    return weights.where(~trigger, 0.0), stop_mode


def dual_pool_score_surface(
    closes: pd.DataFrame,
    pool_window: int = 20,
    n_quantile: int = 5,
) -> pd.DataFrame:
    """M8 双池评分最简版（L3-03，T3b 考卷选股面备选；T3a 不接线=零漂移）。

    语义（挖矿 M8，F 维 signal_additive 搭桥）：动量分=close.pct_change(pool_window) 截面
    分位→1..n_quantile；低波分=|日收益| rolling(pool_window).mean() 反向分位→1..n_quantile
    （波越小分越高）；合流=signal_additive 等权相加→(2, 2×n_quantile] 分面=选股面（消费方
    按 combined 高→低选）。预热窗=NaN（诚实缺供）。参数越界 ValueError fail-closed。
    """
    if pool_window < 1:
        raise ValueError(f"pool_window 须 >=1: {pool_window!r}")
    if n_quantile < 2:
        raise ValueError(f"n_quantile 须 >=2: {n_quantile!r}")
    mom = closes.pct_change(pool_window)
    vol = closes.pct_change().abs().rolling(pool_window).mean()
    mom_q = np.ceil(mom.rank(axis=1, pct=True) * n_quantile).clip(1, n_quantile)
    vol_q = np.ceil((1.0 - vol.rank(axis=1, pct=True)) * n_quantile).clip(1, n_quantile)
    return mom_q + vol_q


def _apply_participation_cap_overlay(
    weights: pd.DataFrame,
    volume: pd.DataFrame,
    closes: pd.DataFrame,
    participation: float = 0.05,
    capital: float = 1e8,
    adv_window: int = 20,
) -> pd.DataFrame:
    """M7 部分成交参与率帽（L4-11，INV-UNIT-001 口径，T3b 考维引擎语义；T3a 不接线）。

    语义（挖矿 M7 参与率近似）：单票目标名义额（w×capital）≤ participation×ADV20 名义额
    （ADV=mean(volume,adv_window)×close；min_periods=1 预热窗部分窗如实）；超帽削到帽，
    削出量不重分配（保守）。已知近似（T3b 卡 honesty 披露位）：考卷无订单对象，绑定
    目标权重（=调仓 trades 的保守包络，非真实 Δw 序列）；volume 单位=股（数据线口径），
    capital=考卷常量（T3b 卡钉定，默认 1e8）。
    """
    if not 0 < participation < 1:
        raise ValueError(f"participation 须在 (0,1): {participation!r}")
    if capital <= 0:
        raise ValueError(f"capital 须 >0: {capital!r}")
    adv_notional = volume.rolling(adv_window, min_periods=1).mean() * closes
    w_max = ((adv_notional * participation) / capital).clip(upper=1.0)
    return weights.clip(upper=w_max)


def _apply_cluster_cap_overlay(
    weights: pd.DataFrame,
    closes: pd.DataFrame,
    corr_window: int = 60,
    corr_threshold: float = 0.7,
    cap_per_cluster: int = 2,
) -> pd.DataFrame:
    """M6 相关性 cluster 上限（C2-03，T3b 考维引擎语义；T3a 不接线=零漂移）。

    语义（挖矿 M6，日频可表达子集）：分块 PIT 相关——块首=每 corr_window 交易日，块内
    相关阵恒定（块=尾随 [bs-60, bs) 窗，零前视）；块内逐日对入选票（权重>0）做
    |corr|>corr_threshold 图连通分量=簇，按当日权重降序（并列符号序=确定性）每簇保留
    前 cap_per_cluster 只，超额清零。预热窗（<corr_window）无相关面=不施加簇帽（诚实
    缺供，非全清）。O(S²) 自警（挖矿原注）：入选票通常 ≤100，逐日簇算仅在其子阵上。
    """
    if not 0 < corr_threshold < 1:
        raise ValueError(f"corr_threshold 须在 (0,1): {corr_threshold!r}")
    if cap_per_cluster < 1:
        raise ValueError(f"cap_per_cluster 须 >=1: {cap_per_cluster!r}")
    if len(weights.index) <= corr_window:
        return weights  # 预热窗：无相关面，不施加（诚实缺供）
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import connected_components

    rets = closes.pct_change()
    out = weights.copy()
    n = len(weights.index)
    for bs in range(corr_window, n, corr_window):
        corr = rets.iloc[bs - corr_window : bs].corr()
        block_end = min(bs + corr_window, n)
        for d in weights.index[bs:block_end]:
            w_day = out.loc[d]
            sel = [s for s in w_day.index if w_day[s] > 0]
            if len(sel) <= cap_per_cluster:
                continue
            sub = corr.loc[sel, sel].to_numpy()
            adj = csr_matrix((np.abs(sub) > corr_threshold).astype(int))
            _ncomp, labels = connected_components(adj, directed=False)
            order = sorted(range(len(sel)), key=lambda i: (-w_day[sel[i]], sel[i]))
            keep_count: dict[int, int] = {}
            for i in order:
                c = int(labels[i])
                if keep_count.get(c, 0) >= cap_per_cluster:
                    out.loc[d, sel[i]] = 0.0
                else:
                    keep_count[c] = keep_count.get(c, 0) + 1
    return out


def _apply_thesis_survival_overlay(
    weights: pd.DataFrame,
    combined: pd.DataFrame,
    closes: pd.DataFrame,
    thesis_decay: float = 0.30,
) -> pd.DataFrame:
    """M5 买入逻辑存活判定（P1-03 thesis_survival 回测化，T3b 考维引擎语义；T3a 不接线）。

    语义（挖矿 M5，thesis 否决权口径）：入场理由=选股因子本身——输入持仓段（held 取自
    输入权重）首日截面秩百分位（pct rank，越高越好）=段内 thesis 基准；当前秩较基准下滑
    超 thesis_decay→当日清仓（收盘判定，§4.4 同族已知失真）；秩不回升则否决持续（段基准
    不因清仓重置），秩回升即放行。秩口径与因子面无关（v1/v1_value/dual_pool 通用）。
    closes 参数=签名统一面（本判定不消费价格，预留成交价口径接线）。
    """
    if not 0 < thesis_decay < 1:
        raise ValueError(f"thesis_decay 须在 (0,1): {thesis_decay!r}")
    rank_now = combined.rank(axis=1, pct=True)
    held = weights > 0
    entry_day = held & ~held.shift(1, fill_value=False)
    rank_entry = rank_now.where(entry_day).ffill()
    thesis_exit = held & (rank_now < rank_entry - thesis_decay)
    return weights.where(~thesis_exit, 0.0)


def _apply_capital_ramp_overlay(
    weights: pd.DataFrame,
    closes: pd.DataFrame,
    ramp_mode: str,
) -> tuple[pd.DataFrame, str]:
    """M4 K 维分批建仓路径（L4-01 分批建仓+P3 金字塔+S2-05 分批止盈，T3b 考维引擎语义；T3a 不接线）。

    schema K 维自述"需 harness 支持路径依赖"——日级向量化实现即满足（挖矿 M4）：
    - lump：恒等（一次性足额=现行考卷语义）
    - linear_20d / linear_60d：持仓段内第 n 日权重×min(1, n/N)（线性爬坡；段=入场日
      cumsum 按 (票,段号) 计数，段内第 1 日=1/N，满 N 日足额）
    - pyramid：三档金字塔（P3 翻译）：入场 1/3 档，收盘≥入场价×1.03 加至 2/3 档，
      ≥×1.06 加至 1.0 档；已加仓档不因回落降档（路径依赖=金字塔语义；S2-05 分批
      止盈为其对称面，考卷以本三档近似表达，差距=T3b honesty 披露位）
    返回 (渐变后权重, ramp_mode)。
    """
    if ramp_mode == "lump":
        return weights, ramp_mode
    if ramp_mode not in ("linear_20d", "linear_60d", "pyramid"):
        raise ValueError(f"未知 ramp_mode: {ramp_mode!r}（合法=lump|linear_20d|linear_60d|pyramid）")
    if ramp_mode in ("linear_20d", "linear_60d"):
        n_days = int(ramp_mode.split("_")[1].rstrip("d"))
        held = weights > 0
        entry_day = held & ~held.shift(1, fill_value=False)
        regime = entry_day.cumsum()
        st = held.stack()
        reg = regime.stack().reindex(st.index)
        # unstack 丢空列/空行——reindex 回全标签面（同 trail20 峰值修，20261007）
        cnt = (
            st.groupby([st.index.get_level_values(1), reg])
            .cumsum()
            .unstack()
            .reindex(index=weights.index, columns=weights.columns)
        )
        ramp = (cnt / float(n_days)).clip(upper=1.0).fillna(0.0)
        return weights.mul(ramp, axis=0), ramp_mode
    # pyramid：入场价锚（同 M1 entry 语义）+ 价档乘数；armed 档段内持久化（cummax 路径依赖，
    # 已加仓档不因回落降档；段=入场日 cumsum，重入场重置）
    held = weights > 0
    entry_day = held & ~held.shift(1, fill_value=False)
    entry_px = closes.where(entry_day).ffill()
    regime = entry_day.cumsum()

    def _armed_in_segment(flag: pd.DataFrame) -> pd.DataFrame:
        st = flag.where(held).stack()
        reg = regime.stack().reindex(st.index)
        # unstack 丢空列/空行——reindex 回全标签面（同 trail20 峰值修）
        return (
            st.groupby([st.index.get_level_values(1), reg])
            .cummax()
            .unstack()
            .reindex(index=weights.index, columns=weights.columns)
        )

    armed3 = _armed_in_segment(closes >= entry_px * 1.03).fillna(False)
    armed6 = _armed_in_segment(closes >= entry_px * 1.06).fillna(False)
    tranche = (1.0 / 3.0) + (1.0 / 3.0) * armed3 + (1.0 / 3.0) * armed6
    tranche = tranche.where(held, 0.0)
    return weights.mul(tranche, axis=0), ramp_mode


def _apply_industry_topk_overlay(
    combined: pd.DataFrame,
    closes: pd.DataFrame,
    industry_map: dict[str, str],
    top_k_industries: int = 3,
    mom_window: int = 20,
) -> pd.DataFrame:
    """M3 行业动量 Top-K × 板块内个股两层排序（L2 板块主干最简版，T3b 考维引擎语义；T3a 不接线）。

    语义（挖矿 M3）：行业动量=成员等权 mean(close.pct_change(mom_window))；行业按动量
    截面 rank 取 Top-K（行业锚=industry_map/sws2021_l1，schema industry_anchor 同源）；
    非 Top-K 行业个股权重清零、缺锚票行业层直接淘汰（诚实缺供，禁静默保留）；Top-K
    行业内保留 combined 原序（第二层）。预热窗动量 NaN→当日全清（诚实缺供）。
    返回 masked combined（date × symbol）。
    """
    mom = closes.pct_change(mom_window)
    ind_of = pd.Series({s: industry_map.get(s) for s in closes.columns})
    known_syms = list(ind_of.index[ind_of.notna()])
    # 行业动量：转置 groupby（避 axis=1 弃用路），date × industry
    ind_mom = mom[known_syms].T.groupby(ind_of.loc[known_syms].to_numpy()).mean().T
    topk = ind_mom.rank(axis=1, ascending=False) <= top_k_industries  # date × industry
    # 符号面还原：keep_sym[d,s] = topk[d, ind(s)]；缺锚票=全 False
    keep = pd.DataFrame(False, index=closes.index, columns=closes.columns)
    for sym in known_syms:
        keep[sym] = topk[ind_of[sym]].reindex(closes.index).fillna(False).to_numpy()
    return combined.where(keep)


def _apply_sector_overlay(
    combined: pd.DataFrame,
    sector_ctx: dict,
    industry_map: dict[str, str],
    mode: str,
) -> pd.DataFrame:
    """L2 族板块接线（矩阵战役 W5；挖矿 m2 L2-01/L2-06 规格卡；T3a 不接线=零漂移）。

    mode=strength_top15：四路板块强度（sector_surface 四路子分合成）逐日 Top-15%
    候选池行业掩码——池外行业个股 combined 置 NaN（不进截面，同 industry_topk
    缺锚票语义=诚实缺供禁静默保留）。
    mode=conduction：先 gate 后 weight（L2-06-1 三级放行：板块强度>6 ∧ 个股自身
    强度>5 ∧ 日成交>2e8 元）→ 过闸票按查表乘数调分（L2-06-3：≥9→×1.15 / ≥6→×1.05 /
    <6→×0.90，10 分制封闭口径）；不过闸置 NaN=不进打分池（顺位 rank 天然剔除）。
    只调分不重排名=TDM 层级隔离纪律（禁在传导段内改 Top-N 语义；乘性改分的
    真实截面序由 sizing 重算承载——调用方置 rank=None）。
    返回 masked/adjusted combined（date × symbol）。
    """
    from sector_surface import (
        GATE_AMOUNT_MIN,
        GATE_SECTOR_MIN,
        GATE_STOCK_MIN,
        conduction_multiplier,
    )

    if mode not in ("strength_top15", "conduction"):
        raise ValueError(f"未知 X_sector mode: {mode!r}（合法=off|strength_top15|conduction）")
    score: pd.DataFrame = sector_ctx["sector_score"]  # date×industry 0-100
    ind_of = pd.Series({s: industry_map.get(s) for s in combined.columns})
    known_syms = list(ind_of.index[ind_of.notna()])
    if not known_syms:
        raise RuntimeError("X_sector 激活但宇宙与行业锚零交集——fail-closed")
    sym_ind = ind_of.loc[known_syms].to_numpy()

    def _broadcast(df: pd.DataFrame) -> pd.DataFrame:
        """date×industry → date×symbol（重复列标签广播+set_axis，零行循环）。"""
        return df.loc[:, list(sym_ind)].set_axis(known_syms, axis=1)

    if mode == "strength_top15":
        pool = sector_ctx.get("pool_mask")
        if pool is None:
            raise RuntimeError("X_sector=strength_top15 需 sector_ctx['pool_mask']——fail-closed")
        keep_sym = _broadcast(pool.reindex(score.index))
        keep = pd.DataFrame(False, index=combined.index, columns=combined.columns)
        keep.loc[:, known_syms] = keep_sym.reindex(combined.index).fillna(False).to_numpy()
        return combined.where(keep)
    amount = sector_ctx.get("amount")
    if amount is None:
        raise RuntimeError("X_sector=conduction 需 sector_ctx['amount']（gate 三级放行）——fail-closed")
    sec10 = _broadcast(score.reindex(combined.index)).reindex(columns=combined.columns) / 10.0
    amount_g = amount.reindex(index=combined.index, columns=combined.columns)
    stock10 = combined.rank(axis=1, pct=True) * 10.0  # 个股强度=合成因子截面百分位×10（卡 §2）
    gate = (sec10 > GATE_SECTOR_MIN) & (stock10 > GATE_STOCK_MIN) & (amount_g > GATE_AMOUNT_MIN)
    mult = conduction_multiplier(sec10.fillna(-1.0))  # 缺锚/缺日行业→弱档，但 gate 已 False 不放行
    return (combined * mult).where(gate)


def _apply_dd_breaker_overlay(
    weights: pd.DataFrame,
    closes: pd.DataFrame,
    breaker_mode: str,
) -> tuple[pd.DataFrame, pd.Series | None]:
    """M2 回撤熔断分级与减仓（X-R1-01/02，T3b 考维引擎语义；T3a 不接线=零漂移）。

    考卷可表达子集=挖矿 M2 向量化骨架：组合权益 nav（w.shift(1)×日收益，与引擎同口径）
    → running max → dd → 阈值带→帽（无记忆分带）。帽=日级乘性（同 J 帽语义家族）：
    NORMAL 1.0 / WARN(dd≤5%) 0.75 / DANGER(≤10%) 0.50 / CRISIS(≤15%) 0.25 / KILL(≤kill_dd) 0。
    已知失真（T3b 卡 honesty 披露位）：live 机 DrawdownStateMachine 的迟滞半阈恢复/持续
    确认窗/最短持有/VaR-CVaR 升级源/毕业准则/复位守卫/RECOVERY 阶梯=非日频向量化可
    表达域，不翻译（六态考卷呈现=五帽带，RECOVERY 缺席如实声明）。
    breaker_mode：off | dd20（kill_dd=0.20，T3b 卡草案枚举）；warn/danger/crisis 沿
    DrawdownStateMachineConfig memo 默认（0.05/0.10/0.15）。
    返回 (帽后权重, 日级帽序列 caps)。
    """
    if breaker_mode == "off":
        return weights, None
    if breaker_mode not in ("dd20",):
        raise ValueError(f"未知 breaker_mode: {breaker_mode!r}（合法=off|dd20）")
    kill_dd = 0.20 if breaker_mode == "dd20" else 0.25
    rets = closes.pct_change()
    port = (weights.shift(1).fillna(0.0) * rets.fillna(0.0)).sum(axis=1)
    nav = (1.0 + port).cumprod()
    dd = nav / nav.cummax() - 1.0
    caps = pd.Series(
        np.select([dd <= -kill_dd, dd <= -0.15, dd <= -0.10, dd <= -0.05], [0.0, 0.25, 0.50, 0.75], default=1.0),
        index=weights.index,
    )
    return weights.mul(caps, axis=0), caps


def _validate_j_string_semantics(recipes) -> None:
    """T0 实钓守卫（20261006）: J 维取值必须字符串 on/off，布尔化=SystemExit 禁跑。

    YAML 1.1 裸 on/off→True/False 时执行器 == "on" 永不命中——on 腿静默≡off 腿，
    regime 增益恒 0（考试失真而报告不知）。schema 已引号治本，此为消费面终检；
    折叠相（phase=1）J=baseline 'off' 字符串同过。
    """
    for r in recipes:
        j = r.values.get("J_regime_switch")
        if j is not None and j not in ("on", "off"):
            raise SystemExit(f"[guard] J_regime_switch 取值非字符串 on/off（YAML 1.1 布尔陷阱?）: {j!r}——禁跑")


def _shard_sample(picked: list, shard_idx: int | None, num_shards: int | None) -> list:
    """确定性分片（20261006 st-t3series）：同一冻结样本按 i::k 轮转切片。

    背景：T0 实测 9.96s/点 ⇒ T1 全量 7400 点 ≈20.5h，超冻卡 single_job_wall_clock_cap_hours=12
    ——按帽拆多 job。同 seed+分层抽样确定 ⇒ i::k 分片=互斥+并集=全集+可复现；各分片
    manifest/net_returns 并集=整跑语义（判决侧合并）。num_shards 缺省=零漂移。
    """
    if not num_shards:
        return picked
    if shard_idx is None or not 0 <= int(shard_idx) < int(num_shards):
        raise ValueError(f"shard_idx={shard_idx!r} 须在 [0, num_shards={num_shards}) 内")
    return list(picked[int(shard_idx) :: int(num_shards)])


# ============================================================================
# T1 网格批仪表（st-gpufeed-20261010，批A 遗产落地：grid_20261009-191707 16.7h
# 零分段落盘，进程被外部树杀后 ~1105 格成果全沉没，且死时无任何"在干什么"证据）。
# 遥测件（全部 fail-open，仪表故障绝不阻断回测批；判据面零动——不改抽样/求值/
# 回测/最终 manifest schema，只向 out_dir 增件）：
#   batch_meta.json                 批出生卡（pid/argv/参数——自报家门，验尸免拼图）
#   progress.jsonl                  每格终态一行（分段计时 fetch/eval/bt/write+combine 命中面）
#   heartbeat.jsonl                 批级心跳（GPU 采样+停滞看门狗：超阈全线程栈 dump 到 stderr）
#   manifest/negatives_partial.csv  每 N 格原子重写（被杀=已落盘成果可回收可审计；
#                                   遥测件非真源，验收仍以 manifest.csv/summary.json 为准）
# 环境变量：ZEPHYR_GRID_INSTRUMENT=0 关闭；ZEPHYR_GRID_HB_INTERVAL（秒，默认 60）；
#   ZEPHYR_GRID_STALL_S（停滞阈值秒，默认 1800）；ZEPHYR_GRID_PARTIAL_EVERY（默认 25）。
# ============================================================================
_GRID_INSTRUMENT = os.environ.get("ZEPHYR_GRID_INSTRUMENT", "1") != "0"
_GRID_HB_INTERVAL_S = float(os.environ.get("ZEPHYR_GRID_HB_INTERVAL", "60"))
_GRID_STALL_THRESHOLD_S = float(os.environ.get("ZEPHYR_GRID_STALL_S", "1800"))
_GRID_PARTIAL_EVERY = int(os.environ.get("ZEPHYR_GRID_PARTIAL_EVERY", "25"))


def _instr_warn(where: str, exc: Exception) -> None:
    print(f"[grid-instrument] fail-open {where}: {type(exc).__name__}: {str(exc)[:120]}", file=sys.stderr, flush=True)


def _instr_iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ts)) + f".{int(ts * 1000) % 1000:03d}"


def _instr_rss_mb() -> float:
    try:
        import psutil

        return round(psutil.Process().memory_info().rss / 1048576, 1)
    except Exception:  # noqa: BLE001
        return -1.0


def _instr_gpu_sample() -> tuple[float | None, float | None, dict]:
    """nvidia-smi 采样 (utilization%, memory used MB) + 本进程 NVML 归因读数。

    设备级 util 含桌面图形噪声（本机实测零算力时 8-57% 摆动），单它当"GPU 是否被喂饱"
    的验收尺必假绿；故并采 gpu_core.nvml_process_util 的逐进程 smUtil（计算上下文归因）。
    任何一路失败=(None, None, {})，禁把"读不到"写成"没占用"。
    """
    attrib: dict = {}
    try:
        # CREATE_NO_WINDOW 铁律（trae_067）：后台心跳线程禁裸 subprocess，走隐藏窗统一入口
        from zephyr.shared.infra.process_pool import run_subprocess_hidden

        out = run_subprocess_hidden(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        util_s, mem_s = out.stdout.strip().splitlines()[0].split(",")[:2]
        util, mem = float(util_s), float(mem_s)
    except Exception:  # noqa: BLE001
        util, mem = None, None
    try:
        from zephyr.backtest.gpu_core import nvml_process_util

        attrib = nvml_process_util()
    except Exception:  # noqa: BLE001 — 归因面缺失不得影响心跳本体
        attrib = {}
    return util, mem, attrib


def _instr_atomic_csv(df: pd.DataFrame, path: Path) -> None:
    tmp = path.with_name(path.name + ".tmp")
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


class _GridInstruments:
    """网格批仪表集：主线程写 progress/partial；守护线程写 heartbeat+停滞看门狗。"""

    def __init__(self, out_dir: Path, total_cells: int) -> None:
        self.out_dir = out_dir
        self.total_cells = int(total_cells)
        self._lock = threading.Lock()
        self._stop_evt = threading.Event()
        self._phase = "data_load"
        self._cells_done = 0
        self._neg_done = 0
        self._combine_hits = 0
        self._combine_misses = 0
        self._last_progress = time.time()
        self._t0 = time.time()
        self._stopped = False
        self._hb_thread: threading.Thread | None = None
        self._dump_count = 0

    def write_batch_meta(self, meta: dict) -> None:
        try:
            meta = {"ts": _instr_iso(time.time()), "pid": os.getpid(), **meta}
            (self.out_dir / "batch_meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as exc:  # noqa: BLE001
            _instr_warn("write_batch_meta", exc)

    # -- 主线程侧 ---------------------------------------------------------
    def set_phase(self, phase: str) -> None:
        with self._lock:
            self._phase = phase

    def record_cell(self, row: dict) -> None:
        """每格终态一行 progress.jsonl（主线程独占写）。"""
        try:
            now = time.time()
            with self._lock:
                self._cells_done += 1
                self._neg_done += 1 if row.get("out") == "neg" else 0
                if row.get("combine") == "hit":
                    self._combine_hits += 1
                elif row.get("combine") == "miss":
                    self._combine_misses += 1
                self._last_progress = now
            row = {"ts": _instr_iso(now), **row}
            with open(self.out_dir / "progress.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001
            _instr_warn("record_cell", exc)

    def maybe_flush(self, manifest_rows: list, negatives: list) -> float:
        """每 _GRID_PARTIAL_EVERY 格原子重写 partial 两件；返回耗时秒（计入格写盘段）。"""
        if (len(manifest_rows) + len(negatives)) % max(_GRID_PARTIAL_EVERY, 1):
            return 0.0
        return self.flush_partial(manifest_rows, negatives)

    def flush_partial(self, manifest_rows: list, negatives: list) -> float:
        started = time.perf_counter()
        try:
            m = (
                pd.DataFrame([asdict(o) | {"values_json": json.dumps(o.values, sort_keys=True)} for o in manifest_rows])
                if manifest_rows
                else pd.DataFrame(columns=[f.name for f in dataclasses.fields(GridEvalOutcome)] + ["values_json"])
            )
            _instr_atomic_csv(m, self.out_dir / "manifest_partial.csv")
            _instr_atomic_csv(pd.DataFrame([asdict(n) for n in negatives]), self.out_dir / "negatives_partial.csv")
        except Exception as exc:  # noqa: BLE001
            _instr_warn("flush_partial", exc)
        return time.perf_counter() - started

    def finalize(self, manifest_rows: list, negatives: list, note: str = "") -> None:
        """终态收口：末次 partial + kind=done 心跳行 + 停心跳线程（幂等，可进异常路径）。"""
        if self._stopped:
            return
        self._stopped = True
        try:
            self.flush_partial(manifest_rows, negatives)
        except Exception as exc:  # noqa: BLE001
            _instr_warn("finalize.flush", exc)
        try:
            with self._lock:
                rec = {
                    "ts": _instr_iso(time.time()),
                    "kind": "done",
                    "pid": os.getpid(),
                    "phase": self._phase,
                    "note": note,
                    "cells_done": self._cells_done,
                    "neg_done": self._neg_done,
                    "total": self.total_cells,
                    "elapsed_s": round(time.time() - self._t0, 3),
                }
            with open(self.out_dir / "heartbeat.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception as exc:  # noqa: BLE001
            _instr_warn("finalize.done_line", exc)
        self._stop_evt.set()

    # -- 心跳/看门狗线程 ---------------------------------------------------
    def start_heartbeat(self) -> None:
        if self._hb_thread is not None:
            return
        self._hb_thread = threading.Thread(target=self._hb_loop, name="grid-heartbeat", daemon=True)
        self._hb_thread.start()

    def _hb_loop(self) -> None:
        while not self._stop_evt.wait(_GRID_HB_INTERVAL_S):
            try:
                now = time.time()
                with self._lock:
                    phase, cells, neg = self._phase, self._cells_done, self._neg_done
                    hits, misses = self._combine_hits, self._combine_misses
                    stall = now - self._last_progress
                gpu_util, gpu_mem, attrib = _instr_gpu_sample()
                rec = {
                    "ts": _instr_iso(now),
                    "kind": "hb",
                    "pid": os.getpid(),
                    "phase": phase,
                    "cells_done": cells,
                    "neg_done": neg,
                    "total": self.total_cells,
                    "elapsed_s": round(now - self._t0, 3),
                    "stall_s": round(stall, 1),
                    "combine_hits": hits,
                    "combine_misses": misses,
                    "rss_mb": _instr_rss_mb(),
                    "gpu_util": gpu_util,
                    "gpu_mem_mb": gpu_mem,
                }
                if attrib.get("available"):
                    # 归因三键（观测面，缺 NVML 时整键不出=不冒充读数）
                    rec["gpu_self_sm_pct"] = attrib.get("sm_util_pct")
                    rec["gpu_self_in_compute"] = attrib.get("in_compute_table")
                    rec["gpu_compute_pids_n"] = attrib.get("compute_pid_count")
                if attrib.get("eval_backend"):
                    rec["eval_backend"] = attrib["eval_backend"]
                if stall > _GRID_STALL_THRESHOLD_S and cells < self.total_cells:
                    rec["stall"] = True
                    self._dump_stacks()
                with open(self.out_dir / "heartbeat.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception as exc:  # noqa: BLE001
                _instr_warn("heartbeat", exc)

    def _dump_stacks(self) -> None:
        """停滞看门狗：全线程栈 dump 到 stderr（wrapper `>>log 2>&1` 必落 f06_grid.log）——
        批A 静默窗缺的正是这份"死时在干什么"证据。"""
        try:
            self._dump_count += 1
            print(
                f"[grid-instrument] STALL>{_GRID_STALL_THRESHOLD_S:.0f}s dump#{self._dump_count} phase={self._phase}",
                file=sys.stderr,
                flush=True,
            )
            faulthandler.dump_traceback()
        except Exception as exc:  # noqa: BLE001
            _instr_warn("dump_stacks", exc)


def run_batch(  # noqa: long-param-list  L2-C engine/engine_degrade/_gpu_rerun 三参演进（存量批次主入口，参数对象重构归批F账非本批）
    n_samples: int,
    seed: int,
    start: str,
    end: str,
    smoke: bool = False,
    subspace: dict[str, list[str]] | None = None,
    stratify_dims: tuple[str, ...] = (),
    *,
    cost_gate_tiers_bp: tuple[float, ...] | None = None,
    engine: str = "auto",
    engine_degrade: str = "",
    _gpu_rerun: bool = False,
    context_overrides: dict | None = None,
    factor_surface: str = "v1",
    exec_caliber: str = "close",
    cost_attribution: bool = False,
    shard_idx: int | None = None,
    num_shards: int | None = None,
) -> dict:
    """批次 A 主入口。返回 summary dict；manifest/negatives 落 data/strategy_intake/grid_<ts>/。

    cost_gate_tiers_bp（T3 方案①）: None（缺省）=现行行为逐位零漂移；传入档位集时
    每成功格点追加 per-point 成本档位扫描（manifest 增 cost 两列/summary 增两键），
    扫描异常=gate 层阴性（fail-closed，禁静默跳过）。
    engine（L2-C 三态）: "cpu"=恒 pandas 原路；"gpu"=显式张量核（无视 auto 尺寸守卫，
    波败 fail-closed 整波重跑 CPU）；"auto"=缺省（env/逐格尺寸守卫解析，语义不变）。
    GPU 波失败=整波弃置重跑 CPU（_GPUWaveFailure，禁半成品混合后端批次），
    summary 以 engine/engine_degrade 披露；manifest 增 backend/degrade 两列。
    _gpu_rerun=内部递归护栏（重跑波不再进包装段，防无限递归）。
    context_overrides/factor_surface/exec_caliber/cost_attribution（T6，st-tclose-t3a-20261005）:
    缺省=现行语义逐位零漂移；t3 家族由 main() 按 prereg t3a 卡解析注入——
    context_overrides={"phase":2} 展开 J 维；factor_surface="v1_value" 接估值财务因子；
    exec_caliber 非 close 需执行价宽表；cost_attribution=True 增归因五列。
    """
    if engine not in _VALID_ENGINES:
        raise ValueError(f"engine 须为 {'|'.join(_VALID_ENGINES)}，得到 {engine!r}")
    if factor_surface not in FACTOR_SURFACES:
        raise ValueError(f"factor_surface 须为 {'|'.join(FACTOR_SURFACES)}，得到 {factor_surface!r}")
    if not _gpu_rerun:
        try:
            return run_batch(
                n_samples,
                seed,
                start,
                end,
                smoke=smoke,
                subspace=subspace,
                stratify_dims=stratify_dims,
                cost_gate_tiers_bp=cost_gate_tiers_bp,
                engine=engine,
                _gpu_rerun=True,
                context_overrides=context_overrides,
                factor_surface=factor_surface,
                exec_caliber=exec_caliber,
                cost_attribution=cost_attribution,
                shard_idx=shard_idx,
                num_shards=num_shards,
            )
        except _GPUWaveFailure as exc:
            import logging as _lg

            _lg.getLogger(__name__).warning("GPU 波失败 fail-closed 整波重跑 CPU（禁半成品混合后端）: %s", exc)
            return run_batch(
                n_samples,
                seed,
                start,
                end,
                smoke=smoke,
                subspace=subspace,
                stratify_dims=stratify_dims,
                cost_gate_tiers_bp=cost_gate_tiers_bp,
                engine="cpu",
                engine_degrade=f"gpu_wave_failed_rerun_cpu:{exc}",
                _gpu_rerun=True,
                context_overrides=context_overrides,
                factor_surface=factor_surface,
                exec_caliber=exec_caliber,
                cost_attribution=cost_attribution,
                shard_idx=shard_idx,
                num_shards=num_shards,
            )
    # ——以下=单波单趟主体——
    from zephyr.position.core.position_recipe_compiler import GridCompiler

    (
        load_px,
        wide,
        filter_st,
        load_st_flags,
        run_backtest_full,
        daily_net_returns,
        net_returns_by_tiers,
        prep_px_tensor,
        run_backtest_full_with_tiers,
    ) = _load_engine()
    # L2-C 波级后端面：cpu=恒 pandas；gpu=显式张量核；auto=None（逐格守卫解析，缺省语义）。
    # gpu_wave=本波实际可能驶入 GPU（显式 gpu，或 auto 解析为 gpu）——决定波败是否触发整波重跑。
    # 探测走 gpu_core.resolve_backend（与引擎 _resolve_engine_backend 同一真源委托）；
    # gpu_core 缺件=本波恒 CPU（gpu_wave=False，波败走原 per-recipe 阴性路径）。
    _wave_backend: str | None = None if engine == "auto" else engine
    try:
        from zephyr.backtest.gpu_core import resolve_backend as _gpu_resolve
    except ImportError:
        _gpu_resolve = None
    gpu_wave = _gpu_resolve is not None and _gpu_resolve(_wave_backend) == "gpu"
    compiler = GridCompiler.from_yaml(SCHEMA_PATH)
    compile_ctx = {**DEFAULT_CONTEXT, **(context_overrides or {})}
    expansion = compiler.compile(compile_ctx)
    recipes_all = list(expansion.recipes)
    _validate_j_string_semantics(recipes_all)
    if subspace:
        # 批次 B 子空间枚举（裁定: A 给出的高价值子空间全因子穷尽——过滤即全跑，非抽样）
        recipes_all = [r for r in recipes_all if all(r.values.get(k) in vs for k, vs in subspace.items())]

    class _Sub:
        pass

    sub_view = _Sub()
    sub_view.recipes = recipes_all
    sub_view.n_raw = len(recipes_all)
    picked = stratified_sample(sub_view, 8 if smoke else n_samples, seed, stratify_dims=stratify_dims)
    full_sample_n = len(picked)
    picked = _shard_sample(picked, shard_idx, num_shards)
    # T2-A prefix 顺序化执行（st-gpufeed-20261010 连夜冲刺令）：同 (G,A1,A2) prefix 格点
    # 连续执行→combine_cache LRU 命中（原 stratify 序下 A2 轴交错=T1 实测 1.5% 命中率）。
    # 排序须在 shard 之后：i::k 切片前排序会把连续 prefix 重新打散进各分片。
    # 零漂移论证：样本集=seed 冻结面不变（仅迭代序变）；格点间相互独立（批级缓存只读
    # 复用、死亡计数与序无关）；manifest 行序变化不影响下游消费者（_scan_grid_summaries
    # 只读 summary.evaluated；N 台账记 count；DSR/归因按 recipe_id 读）。N_eff 输入列序
    # 变化由影子对照对拍尺盯防（expected 数学序不变）。
    picked.sort(key=lambda r: r.prefix_key)
    run_ts = time.strftime("%Y%m%d-%H%M%S")
    # 并发分片目录名带 shard 标识（20261006 撞车教训：6 分片同秒启动，秒级时间戳目录
    # 名相撞=两进程互写同一 out_dir，产物互覆污染）——分片跑必带 _s{i}of{k} 后缀。
    shard_tag = f"_s{int(shard_idx)}of{int(num_shards)}" if num_shards else ""
    out_dir = INTAKE_DIR / f"grid_{run_ts}{shard_tag}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # T1 仪表（st-gpufeed-20261010）：批出生卡+心跳看门狗起跳（fail-open，判据面零动）
    instr: _GridInstruments | None = None
    if _GRID_INSTRUMENT:
        try:
            instr = _GridInstruments(out_dir, total_cells=len(picked))
            instr.write_batch_meta(
                {
                    "run_ts": run_ts,
                    "argv": sys.argv,
                    "n_samples": n_samples,
                    "n_picked": len(picked),
                    "seed": seed,
                    "window": [start, end],
                    "stratify_dims": list(stratify_dims),
                    "engine": engine,
                    "smoke": bool(smoke),
                    "shard": [shard_idx, num_shards],
                    "subspace": subspace,
                }
            )
            instr.start_heartbeat()
        except Exception as exc:  # noqa: BLE001
            _instr_warn("init", exc)
            instr = None

    # 数据一次拉取（窗口外多留 120 日算因子预热）
    import datetime as _dt

    warm_start = (pd.Timestamp(start) - pd.Timedelta(days=200)).date().isoformat()
    # T6 S2: 执行价口径附加字段（next_open=open；vwap=amount/volume 经量纲哨兵）
    caliber_extra: tuple[str, ...] = {"next_open": ("open",), "vwap": ("amount", "volume")}.get(exec_caliber, ())
    px = load_px(warm_start, end, fields=("close", "volume") + caliber_extra)
    closes_all = wide(px, "close")
    px_exec_all: pd.DataFrame | None = None
    if exec_caliber == "next_open":
        px_exec_all = wide(px, "open")
    elif exec_caliber == "vwap":
        from _c4_engine import _vwap_from_amount_volume

        px_exec_all = _vwap_from_amount_volume(wide(px, "amount"), wide(px, "volume"), closes_all)
    closes = closes_all.loc[(closes_all.index >= pd.Timestamp(start)) & (closes_all.index <= pd.Timestamp(end))]
    flags = load_st_flags(start, end)
    closes_eval = filter_st(closes_all, flags).loc[closes.index]
    # 矩阵战役 W5（L2-01/L2-06）: 板块强度面板批级一次构建——仅网格含非 off X_sector
    # 值时装载（缺省零开销零漂移）；want_amount=True 供 conduction gate 三级放行。
    sector_ctx: dict | None = None
    if any(r.values.get("X_sector", "off") != "off" for r in picked):
        from sector_surface import build_sector_context

        sector_ctx = build_sector_context(warm_start, end, want_amount=True)

    # T6 S3: 估值/财务因子面批级装载（factor_surface=v1_value 时；缺席=格点级 eval 阴性，
    # fail-closed 禁静默降级——估值是考卷维不是装饰）
    factor_data_fail = ""
    val_pe = val_pb = fin_hist = None
    if factor_surface == "v1_value":
        try:
            from _c4_engine import load_valuation

            _val = load_valuation(warm_start, end, fields=("pe", "pb"))
            # 对齐考窗 index（20261006 实钓修复）：warm 基面板与 v1/f_np_yoy 考窗基混挂
            # 曾致 A2 numpy 通路 83/200 死；估值=EOD 快照无预热语义，考窗基为设计真基
            val_pe = _val["pe"].reindex(closes.index).reindex(columns=closes_all.columns)
            val_pb = _val["pb"].reindex(closes.index).reindex(columns=closes_all.columns)
            fin_hist = _load_fin_np_yoy_history()
            if val_pe.empty or val_pb.empty:
                raise RuntimeError("load_valuation 空面板")
        except Exception as exc:  # noqa: BLE001
            factor_data_fail = f"factor_data_load_fail:{type(exc).__name__}:{str(exc)[:80]}"
            import logging as _lg

            _lg.getLogger(__name__).warning("S3 估值/财务因子面装载失败（v1_value 格点将记 eval 阴性）: %s", exc)

    universe_cache: dict[str, set[str]] = {}
    factors_cache: dict[str, dict[str, pd.DataFrame]] = {}
    # T2c: g → (closes_eval[cols], vol20[cols]) 切片一次复用（免每格点重切 T×S）；prefix 级 combined 缓存
    slice_cache: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}
    combine_cache: dict = {}  # (G,A1,A2) → (combined, rank, a1_deg, a2_deg)
    vol20 = closes_eval.pct_change().rolling(20).std()
    # T2a 精确实现数据面: 市值宽表 + 60 日收益矩（mkt_cap/kelly sizing 消费）
    # 考窗基对齐（20261006 Owner 并行化前置）：warm 基市值表致 mkt_cap 定尺寸权重并集
    # 变形（230 行≠考窗 120 行）→ GPU 等形守卫全数挡回 CPU（T0 实测 mkt_cap 29/29 CPU）。
    # 对齐=考窗切片逐位恒等（并集多余行全 NaN→引擎丢弃），净零漂移+快路径资格恢复。
    mkt_cap_w = _load_mkt_cap_wide(warm_start, end, closes_all.columns).reindex(closes.index)
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
    nets_archive: dict[str, pd.Series] = {}  # recipe_id → 带日期索引 net（归因读端消费，2026-09-24 st-gpu-final）
    cost_rows: dict[str, dict[float, float]] = {}  # T3 方案①: recipe_id → {bp: sharpe}（仅档位扫描启用时非空）
    j_state_rows: dict[str, dict[str, int]] = {}  # T6 S1: recipe_id → 态分布（仅 J=on 格点非空）
    attr_rows: dict[str, dict[str, float]] = {}  # T6 S5: recipe_id → 成本归因分解（仅启用时非空）
    j_schedule: pd.DataFrame | None = None
    j_load_fail = ""
    eval_dead = bt_dead = gate_dead = 0

    def _instr_neg(layer: str, reason: str) -> None:
        # T1 仪表：阴性格点统一记账（fail-open，观测不干预；体面零漂移）
        if instr is None:
            return
        instr.record_cell(
            {
                "i": _cell_i,
                "id": r.recipe_id,
                "out": "neg",
                "layer": layer,
                "reason": reason,
                "tot_s": round(time.perf_counter() - _t_cell, 4),
            }
        )
        instr.maybe_flush(manifest_rows, negatives)

    if instr is not None:
        instr.set_phase("grid_loop")
    for _cell_i, r in enumerate(picked):
        _t_cell = time.perf_counter()
        _t_fetch = _t_eval = _t_bt = 0.0
        _combine_state: str | None = None
        g = r.values["G_universe"]
        # T6 S1: J=on 格点先过调度表闸（装载失败=本格 eval 阴性，其余格点不受染）
        if r.values.get("J_regime_switch") == "on":
            if j_load_fail:
                negatives.append(
                    NegativeRecord(r.recipe_id, "eval", j_load_fail, r.values, "", "j_schedule 不可用（fail-closed）")
                )
                _instr_neg("eval", "j_load_fail")
                eval_dead += 1
                continue
            if j_schedule is None:
                try:
                    j_schedule = _load_j_regime_schedule(closes.index)
                    j_schedule.to_csv(out_dir / "j_regime_schedule.csv", encoding="utf-8")  # 批级审计件
                except Exception as exc:  # noqa: BLE001
                    j_load_fail = f"j_schedule_load_fail:{type(exc).__name__}"
                    negatives.append(NegativeRecord(r.recipe_id, "eval", j_load_fail, r.values, "", str(exc)[:120]))
                    _instr_neg("eval", j_load_fail)
                    eval_dead += 1
                    continue
        if factor_data_fail and factor_surface == "v1_value":
            # T6 S3: 因子面数据缺席=格点 eval 阴性（fail-closed，禁静默降 v1）
            negatives.append(
                NegativeRecord(r.recipe_id, "eval", factor_data_fail.split(":")[0], r.values, "", factor_data_fail)
            )
            _instr_neg("eval", factor_data_fail.split(":")[0])
            eval_dead += 1
            continue
        _t0 = time.perf_counter()
        if g not in universe_cache:
            try:
                universe_cache[g] = _load_universe(g, start, end)
            except Exception as exc:  # noqa: BLE001
                negatives.append(
                    NegativeRecord(
                        r.recipe_id, "eval", f"universe_load_fail:{type(exc).__name__}", r.values, "", str(exc)[:120]
                    )
                )
                _instr_neg("eval", f"universe_load_fail:{type(exc).__name__}")
                eval_dead += 1
                continue
        cols = [c for c in universe_cache[g] if c in closes_eval.columns]
        if len(cols) < 30:
            negatives.append(
                NegativeRecord(r.recipe_id, "eval", "universe_too_small", r.values, "", f"cols={len(cols)}")
            )
            _instr_neg("eval", "universe_too_small")
            eval_dead += 1
            continue
        if g not in factors_cache:
            closes_g = closes_eval[cols]
            factors_cache[g] = compute_v1_factors(closes_g)
            if factor_surface == "v1_value":
                # T6 S3: 估值财务因子并入考卷因子面（缺列/缺数据票=NaN 交 A1 守卫；5 因子交 A2 全模式）
                factors_cache[g].update(compute_value_factors(val_pe[cols], val_pb[cols]))
                factors_cache[g]["f_np_yoy"] = _fin_np_yoy_panel(fin_hist, closes_g.index, pd.Index(cols))[cols]
            # L1 hoist（st-gpup1-20260929）: closes/rets 张量面只依赖 (窗口, 宇宙列集)，
            # 同宇宙多格点批级预热一次共享（原逐格重算；与内联式同式同序=逐位一致）。
            slice_cache[g] = (closes_g, vol20[cols], prep_px_tensor(closes_g.index, closes_g))
        closes_g, vol20_g, pre_tensor = slice_cache[g]
        px_exec_g = None if px_exec_all is None else px_exec_all[cols]
        _t_fetch = time.perf_counter() - _t0
        _ck = (r.values["G_universe"], r.values["A1_factor_normalize"], r.values["A2_combine_weight"])
        # 仪表 combine 命中面：键构造须与 evaluate_recipe 内 cache_key 保持同步（遥测用）
        _combine_state = "hit" if _ck in combine_cache else "miss"
        _t0 = time.perf_counter()
        try:
            weights, degraded = _eval_cell_mem_retry(
                lambda: evaluate_recipe(
                    r,
                    closes_g,
                    factors_cache[g],
                    vol20_g,
                    cols,
                    mkt_cap_w=mkt_cap_w,
                    rets60_mean=rets60_mean,
                    rets60_var=rets60_var,
                    industry_map=industry_map,
                    combine_cache=combine_cache,
                    j_schedule=j_schedule,
                    sector_ctx=sector_ctx,
                )
            )
        except Exception as exc:  # noqa: BLE001
            _t_eval = time.perf_counter() - _t0
            negatives.append(
                NegativeRecord(r.recipe_id, "eval", f"eval_fail:{type(exc).__name__}", r.values, "", str(exc)[:120])
            )
            _instr_neg("eval", f"eval_fail:{type(exc).__name__}")
            eval_dead += 1
            continue
        _t_eval = time.perf_counter() - _t0
        if r.values.get("J_regime_switch") == "on" and j_schedule is not None:
            # T6 S1: 态分布审计位（调度表批级共享，格点级零冗余读取）
            j_state_rows[r.recipe_id] = {str(k): int(v) for k, v in j_schedule["state"].value_counts().items()}
        _t0 = time.perf_counter()
        try:
            # st-ddup-20260925 去重改造②: run_backtest+daily_net_returns 两连调合并为
            # run_backtest_full 单趟（stats/net 与原两调逐位一致，掩码批级缓存自动复用）。
            # st-gpup1-20260929 L1 hoist: pre_tensor（批级 closes/rets）透传免逐格重算；
            # 成本门场景升级 run_backtest_full_with_tiers 单趟三产物（同 (weights,px)
            # 原第二趟 net_returns_by_tiers 免除，三产物与两调逐位一致）。
            nets_by_tier = None
            # L2-C: engine 透传（cpu=恒 pandas / gpu=显式张量核 / auto=None 逐格守卫解析）；
            # GPU 波内调用失败=fail-closed 信号（整波弃置重跑 CPU，禁半成品混合后端批次），
            # CPU 波内失败维持原 per-recipe 阴性路径（语义零漂移）。
            try:
                if cost_gate_tiers_bp is not None:
                    stats, net, nets_by_tier = run_backtest_full_with_tiers(
                        weights,
                        closes_g,
                        tuple(cost_gate_tiers_bp),
                        backend=_wave_backend,
                        pre_tensor=pre_tensor,
                        exec_caliber=exec_caliber,
                        px_exec=px_exec_g,
                    )
                else:
                    stats, net = run_backtest_full(
                        weights,
                        closes_g,
                        backend=_wave_backend,
                        pre_tensor=pre_tensor,
                        exec_caliber=exec_caliber,
                        px_exec=px_exec_g,
                    )
            except Exception as exc:  # noqa: BLE001
                if gpu_wave:
                    raise _GPUWaveFailure(f"{r.recipe_id}: {type(exc).__name__}: {exc}") from exc
                raise
            if len(net.dropna()) < 60 or float(net.std()) == 0:
                raise RuntimeError(f"insufficient_net:{len(net)}")
            _t_bt = time.perf_counter() - _t0
            sharpe = stats["sharpe"]
            nets_for_neff[r.recipe_id] = [float(v) for v in net.values]
            nets_archive[r.recipe_id] = net  # 带日期索引归档（values-only 落盘=产物不自描述，归因读端实证缺陷）
        except _GPUWaveFailure:
            if instr is not None:
                instr.set_phase("gpu_wave_failed")
                instr.finalize(manifest_rows, negatives, note="gpu_wave_failed")
            raise  # L2-C：GPU 波败信号直通批次级 fail-closed（整波重跑 CPU）
        except Exception as exc:  # noqa: BLE001
            negatives.append(
                NegativeRecord(
                    r.recipe_id,
                    "backtest",
                    f"backtest_fail:{type(exc).__name__}",
                    r.values,
                    ",".join(degraded),
                    str(exc)[:120],
                )
            )
            _instr_neg("backtest", f"backtest_fail:{type(exc).__name__}")
            bt_dead += 1
            continue
        if cost_gate_tiers_bp is not None:
            # T3 方案① stage-aware per-point 成本档位扫描（档位集已过预算闸 validate；
            # 引擎口径唯一=daily_net_returns slippage_bp kwarg，exam_cost_gate 零重实现）。
            # st-ddup-20260925 去重改造①: 档位 net 序列经 net_returns_by_tiers 一趟
            # gross/turnover×五档标量成本线派生后注入扫描（与逐档 daily_net_returns
            # 逐位一致；exam_cost_gate nets_by_tier 注入口=其"净值序列由调用方注入"不变量）。
            # st-gpup1-20260929: 档位序列优先消费单趟三产物的 nets_by_tier（逐位一致），
            # 缺席（异常路径）回退 net_returns_by_tiers 原路——死亡层归因不变。
            try:
                from zephyr.backtest.regime_validation.exam_cost_gate import run_cost_tier_scan

                if nets_by_tier is None:
                    nets_by_tier = net_returns_by_tiers(
                        weights, closes_g, tuple(cost_gate_tiers_bp), exec_caliber=exec_caliber, px_exec=px_exec_g
                    )
                cost_rows[r.recipe_id] = run_cost_tier_scan(
                    weights, closes_g, daily_net_returns, tiers_bp=tuple(cost_gate_tiers_bp), nets_by_tier=nets_by_tier
                )
            except Exception as exc:  # noqa: BLE001 档位扫描跑不出=gate 层死（fail-closed 禁静默）
                negatives.append(
                    NegativeRecord(
                        r.recipe_id,
                        "gate",
                        f"cost_scan_fail:{type(exc).__name__}",
                        r.values,
                        ",".join(degraded),
                        str(exc)[:120],
                    )
                )
                _instr_neg("gate", f"cost_scan_fail:{type(exc).__name__}")
                gate_dead += 1
                continue
        if cost_attribution:
            # T6 S5: 从引擎 stats 精确还原的成本归因分解（主判据口径=冻结土规缺省档）
            attr_rows[r.recipe_id] = cost_attribution_row(float(stats["avg_turnover_1side"]), int(stats["days"]), None)
        manifest_rows.append(
            GridEvalOutcome(
                r.recipe_id,
                r.prefix_key,
                r.values,
                degraded,
                sharpe=sharpe,
                ann_return=stats["ann_return"],
                max_drawdown=stats["max_drawdown"],
                avg_turnover=stats["avg_turnover_1side"],
                net_days=len(net),
                backend=str(stats.get("backend", "")),  # L2-C：实际后端披露透传（引擎旧版=空串）
                degrade=str(stats.get("guard_reason") or ""),  # L2-C：守卫原因码（空=未降级）
            )
        )
        if instr is not None:
            _t_write = instr.maybe_flush(manifest_rows, negatives)
            instr.record_cell(
                {
                    "i": _cell_i,
                    "id": r.recipe_id,
                    "out": "pos",
                    "fetch_s": round(_t_fetch, 4),
                    "eval_s": round(_t_eval, 4),
                    "bt_s": round(_t_bt, 4),
                    "write_s": round(_t_write, 4),
                    "tot_s": round(time.perf_counter() - _t_cell, 4),
                    "combine": _combine_state,
                    "cache_n": len(combine_cache),
                    "backend": str(stats.get("backend", "")),
                }
            )

    # N_eff（预注册 effective_rank）——批次级双口径披露+账本披露位（非 smoke 才写账本）
    if instr is not None:
        instr.set_phase("finalize")
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
    if nets_archive:
        # dict-concat（20261006 读端实证缺陷修复）：values()-concat 丢键=列名退化 0..n，
        # 产物不自描述（归档注释预警过的读端债）——dict-concat 键=recipe_id 列名。
        nr = pd.concat(nets_archive, axis=1)  # 带 DatetimeIndex 对齐落盘（行=交易日，列=recipe_id）
        try:
            nr_path = out_dir / "net_returns.parquet"
            nr.to_parquet(nr_path)
        except (ImportError, ModuleNotFoundError):
            nr_path = out_dir / "net_returns.csv.gz"
            nr.to_csv(nr_path, index=False, compression="gzip")
        net_returns_file = nr_path.name

    if manifest_rows:
        manifest = pd.DataFrame(
            [asdict(o) | {"values_json": json.dumps(o.values, sort_keys=True)} for o in manifest_rows]
        )
    else:
        # 全员阴性批: 空表也带 schema 表头（产物可解析、gate 阴性可审计，禁崩批丢证据）
        manifest = pd.DataFrame(columns=[f.name for f in dataclasses.fields(GridEvalOutcome)] + ["values_json"])
    if cost_rows:
        # T3 方案①: 档位扫描证据随出生证落盘（仅启用时新增列，缺省路径 manifest schema 零变化）。
        # cost_adjusted_sharpe=搜索主目标（search_objective.primary）在最高已扫档的成本后口径
        # （T1 轻档=5bp；T2 全档=40bp 全成本档）。
        cost_df = pd.DataFrame(
            [
                {
                    "recipe_id": rid,
                    "cost_tier_sharpes_json": json.dumps({str(bp): sh for bp, sh in sharpes.items()}, sort_keys=True),
                    "cost_adjusted_sharpe": sharpes[max(sharpes)],
                }
                for rid, sharpes in cost_rows.items()
            ]
        )
        manifest = manifest.merge(cost_df, on="recipe_id", how="left")
    if j_state_rows:
        # T6 S1: J 总闸态分布审计列（仅 J=on 格点启用时新增列，缺省路径 schema 零变化；
        # 每日逐日调度表另落 j_regime_schedule.csv 批级审计件）
        j_df = pd.DataFrame(
            [{"recipe_id": rid, "j_state": json.dumps(dist, sort_keys=True)} for rid, dist in j_state_rows.items()]
        )
        manifest = manifest.merge(j_df, on="recipe_id", how="left")
    if attr_rows:
        # T6 S5: 成本归因分解五列（仅 cost_attribution 启用时新增列，缺省路径 schema 零变化）
        manifest = manifest.merge(
            pd.DataFrame([{"recipe_id": rid, **row} for rid, row in attr_rows.items()]), on="recipe_id", how="left"
        )
    # errors="ignore": 全员阴性批（manifest 空 DataFrame 无列）时 legacy 会 KeyError 崩批——
    # gate 阴性必须落 negatives.csv 可审计，禁崩批丢证据（非空路径输出逐位不变）
    manifest.drop(columns=["values"], errors="ignore").to_csv(out_dir / "manifest.csv", index=False)
    neg_df = pd.DataFrame([asdict(n) for n in negatives])
    neg_df.to_csv(out_dir / "negatives.csv", index=False)
    summary = {
        "run_ts": run_ts,
        "mode": "smoke" if smoke else ("batch_b_subspace" if subspace else "batch_a_census"),
        "subspace": subspace or None,
        "stratify_dims": list(stratify_dims) or None,
        "n_raw": expansion.n_raw,
        "n_sampled": len(picked),
        "evaluated": len(manifest_rows),
        "eval_dead": eval_dead,
        "backtest_dead": bt_dead,
        "degraded_recipes": int(manifest["degraded_dimensions"].apply(bool).sum()) if len(manifest) else 0,
        "window": [start, end],
        "seed": seed,
        "out_dir": str(out_dir),
        "net_returns_file": net_returns_file,
        "n_trials_effective": n_eff,
        "n_eff_meta": n_eff_meta,
        "engine": engine,  # L2-C：三态引擎披露（cpu|gpu|auto）
    }
    if _EVAL_BACKEND != "cpu":
        # 观测面键（非判据面）：eval 上卡的分流计数；缺省 cpu 路不出此键=产物零漂移
        summary["eval_gpu"] = dict(_EVAL_GPU_STATS)
    if engine_degrade:
        # L2-C：GPU 波败 fail-closed 整波重跑 CPU 的披露键（空=未发生降级）
        summary["engine_degrade"] = engine_degrade
    if num_shards:
        # 分片披露（20261006）：full_sample_n=分片前冻结样本总量；并集=整跑
        summary["shard"] = {"idx": int(shard_idx), "num": int(num_shards), "full_sample_n": full_sample_n}
    if cost_gate_tiers_bp is not None:
        # T3 方案①: 仅档位扫描启用时披露（缺省路径 summary 逐键零漂移）
        summary["cost_gate_tiers_bp"] = [float(t) for t in cost_gate_tiers_bp]
        summary["gate_dead"] = gate_dead
    if j_state_rows or j_load_fail:
        # T6 S1: 仅 J 接线启用/失败时披露（缺省路径 summary 逐键零漂移）
        summary["j_regime"] = {
            "enabled": bool(j_state_rows),
            "schedule_file": "j_regime_schedule.csv" if j_schedule is not None else None,
            "load_fail": j_load_fail or None,
            "defensive_whitelist_registered": defensive_whitelist_assets(),
        }
    if exec_caliber != "close" or factor_surface != "v1" or cost_attribution:
        # T6: 仅 t3 家族注入面启用时披露（缺省路径 summary 逐键零漂移）
        summary["t3a_wiring"] = {
            "exec_caliber": exec_caliber,
            "factor_surface": factor_surface,
            "cost_attribution": cost_attribution,
            "context": compile_ctx,
        }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    if not smoke and _EXPLORATION_LEDGER:
        # 深挖车道令②（2026-10-10）：exploration 纪律——不判 pass/fail、不进分数册、
        # 不占考试试次；批记录追探索扫描分册（与 N 账本分册），写败不阻断产物。
        try:
            _lp = Path(_EXPLORATION_LEDGER)
            _lp.parent.mkdir(parents=True, exist_ok=True)
            with _lp.open("a", encoding="utf-8") as _fh:
                _fh.write(
                    json.dumps(
                        {
                            "kind": "exploration_scan",
                            "batch_id": f"exploration:grid_{summary['run_ts']}",
                            "n_cells": int(summary.get("evaluated") or 0),
                            "out_dir": _rel_cwd(out_dir),
                            "ts": time.time(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception as exc:  # noqa: BLE001  与 N 账本钩子同款 fail-open
            import logging as _lg

            _lg.getLogger(__name__).warning("探索扫描分册写败: %s", exc)
    elif not smoke:
        # P0-6 试验台账记账治本（2026-09-28）：批末入账——17.4% 漏记的根因是没人调
        # record/sync；本批 record_run（幂等、与 sync_screen_counts 同口径 evaluated），
        # 台账失败不阻断回测产物（fail-open，warning 留痕）。
        try:
            _auto_record_and_advance(out_dir, summary)
        except Exception as exc:  # noqa: BLE001
            import logging as _lg

            _lg.getLogger(__name__).warning("批末台账记账失败（trial ledger 未入账）: %s", exc)
    if instr is not None:
        instr.finalize(manifest_rows, negatives, note="done")
    return summary


#: 方案①分层语义字段（prereg budget_caps；在场=启用，缺省=现行语义零变化）
STAGED_TIERS_KEY = "cost_gate_t1_tiers_bp"


def _auto_record_and_advance(out_dir: Path, summary: dict) -> dict:
    """P0-6 批末记账（2026-09-28）：record 本批 + 只登新批不回填历史。

    record_run 幂等（同 batch_id 跳过）；水位线 registry_record_watermark 只标记
    「自动记账从何时起覆盖」，历史缺账不静默补记（须 Owner 睁眼裁定，未回填的
    缺口由 --verify-counts 显式报红）。
    """
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    ledger = TrialLedger()
    rec = ledger.record_run(
        "factory_grid_batch_a",
        f"grid_{summary['run_ts']}",
        int(summary.get("evaluated") or 0),
        note=f"auto: {_rel_cwd(out_dir / 'summary.json')}",
        recorded_by="factory_grid_executor",
    )
    wm = ledger.set_watermark("registry_record_watermark", time.time())
    return {"record": rec, "watermark": wm}


def _rel_cwd(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(_REPO))
    except ValueError:
        return str(path)


def _scan_grid_summaries(root: Path) -> list[dict]:
    """扫描网格产物 summary（身份集口径：每批 batch_id+artifact_n+mtime）。"""
    import json as _json

    rows: list[dict] = []
    for summary_path in sorted(root.glob("grid_*/summary.json")):
        try:
            s = _json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        batch_id = f"grid_{summary_path.parent.name[len('grid_') :]}"
        n = s.get("evaluated")
        if n is None:
            n = s.get("n_sampled")
        rows.append({"batch_id": batch_id, "artifact_n": int(n or 0), "mtime": summary_path.stat().st_mtime})
    return rows


def _classify_verify_rows(rows: list[dict], records: dict[str, int], watermark: float) -> tuple[list[str], list[str]]:
    """分账：缺账（水位线后新批）/水位线前已知缺口（不回填，呈 Owner）。"""
    missing: list[str] = []
    under_wm: list[str] = []
    for r in rows:
        if r["batch_id"] in records:
            continue
        bucket = under_wm if watermark and r["mtime"] < watermark else missing
        bucket.append(r["batch_id"])
    return missing, under_wm


def _print_verify_report(rows: list[dict], records: dict[str, int], missing: list[str], under_wm: list[str]) -> None:
    ledger_only = sorted(set(records) - {r["batch_id"] for r in rows})
    for r in rows:
        flag = "OK" if r["batch_id"] in records else "MISS"
        print(f"[verify-counts] {flag} {r['batch_id']} artifact={r['artifact_n']} ledger={records.get(r['batch_id'])}")
    print(
        f"[verify-counts] 批次={len(rows)} 在账={sum(1 for r in rows if r['batch_id'] in records)} "
        f"缺账={len(missing)} 水位线前已知缺口={len(under_wm)}（不回填，呈 Owner） 台账无产物批={len(ledger_only)}"
    )
    if missing:
        print(f"[verify-counts] 缺账批清单: {', '.join(missing)}")


def _verify_counts(grid_root_override: str | None = None) -> int:
    """P0-6 只读对账尺：产物身份集 vs 台账逐批对照（禁写；缺账点名，不回填）。

    口径=身份集（每批 batch_id 一个身份，n=summary 的 evaluated/n_sampled），
    禁聚合行数。水位线前的历史批=已知缺口（显式列 under_watermark，裁定：不回填）。
    """
    from zephyr.backtest.core.n_trial_ledger import TrialLedger

    root = Path(grid_root_override) if grid_root_override else INTAKE_DIR
    if not root.exists():
        print(f"[verify-counts] grid root 不存在: {root}")
        return 1
    ledger = TrialLedger()
    data = ledger.load_registry()
    records = {str(r.get("batch_id")): int(r.get("n_trials") or 0) for r in (data.get("batch_records") or [])}
    watermark = ledger.get_watermark("registry_record_watermark")
    rows = _scan_grid_summaries(root)
    missing, under_wm = _classify_verify_rows(rows, records, watermark)
    _print_verify_report(rows, records, missing, under_wm)
    return 1 if missing else 0


#: T6: t3 家族 stage（T3a 开闸考；context phase=2+prereg t3a 卡；挖矿 §3.2）
T3_STAGES: tuple[str, ...] = ("t3", "t3-t1", "t3-t2")
PREREG_PATH = _REPO / "config" / "search_space_prereg.yaml"
PREREG_T3A_PATH = _REPO / "config" / "search_space_prereg_t3a.yaml"
#: T3b: t3b 家族 stage（T3b 加离场考；context phase=3+prereg t3b 卡；挖矿 §3.1 批次表）
T3B_STAGES: tuple[str, ...] = ("t3b", "t3b-t1", "t3b-t2")
PREREG_T3B_PATH = _REPO / "config" / "search_space_prereg_t3b.yaml"


def _load_prereg_caps(stage: str = "") -> dict:
    """prereg budget_caps 读取（缺册 fail-closed，错误文案与原 _apply_prereg_budget 逐字一致）。

    T6: stage ∈ T3_STAGES 改读 config/search_space_prereg_t3a.yaml（T3a 独立冻结卡，
    缺失=SystemExit fail-closed）；T3b: stage ∈ T3B_STAGES 改读 t3b 卡（同构）；
    其余 stage 沿用主 prereg 册（逐字零变化）。
    """
    import yaml

    if stage in T3_STAGES or stage in T3B_STAGES:
        path = PREREG_T3A_PATH if stage in T3_STAGES else PREREG_T3B_PATH
        if not path.exists():
            raise SystemExit(f"[prereg] {path.name} 缺失——预注册冻结卡缺失，禁开跑（fail-closed）")
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cfg.get("budget_caps") or {}
    prereg = PREREG_PATH
    if not prereg.exists():
        raise SystemExit("[prereg] config/search_space_prereg.yaml 缺失——预注册冻结缺失，禁开跑（fail-closed）")
    cfg = yaml.safe_load(prereg.read_text(encoding="utf-8")) or {}
    return cfg.get("budget_caps") or {}


def _load_t3a_exam_card() -> dict:
    """T6: T3a 冻结卡整卡读取（exam_definition/pass_criteria/honesty；未冻结卡 fail-closed）。"""
    import yaml

    if not PREREG_T3A_PATH.exists():
        raise SystemExit(f"[prereg] {PREREG_T3A_PATH.name} 缺失——T3a 预注册冻结卡缺失，禁开跑（fail-closed）")
    card = yaml.safe_load(PREREG_T3A_PATH.read_text(encoding="utf-8")) or {}
    if not card.get("frozen_at") or not card.get("frozen_by"):
        raise SystemExit("[prereg] T3a 冻结卡缺 frozen_at/frozen_by——未冻结卡禁开跑（fail-closed）")
    return card


def _load_t3b_exam_card() -> dict:
    """T3b: 冻结卡整卡读取（同 t3a 构造；未冻结卡 fail-closed）。"""
    import yaml

    if not PREREG_T3B_PATH.exists():
        raise SystemExit(f"[prereg] {PREREG_T3B_PATH.name} 缺失——T3b 预注册冻结卡缺失，禁开跑（fail-closed）")
    card = yaml.safe_load(PREREG_T3B_PATH.read_text(encoding="utf-8")) or {}
    if not card.get("frozen_at") or not card.get("frozen_by"):
        raise SystemExit("[prereg] T3b 冻结卡缺 frozen_at/frozen_by——未冻结卡禁开跑（fail-closed）")
    return card


def _load_cost_gate_tiers() -> list[float]:
    """全档真源（config/exam_scale_cost_gate.yaml cost_gate.tiers_bp，禁双头硬编码）。"""
    import yaml

    p = Path(__file__).resolve().parents[2] / "config" / "exam_scale_cost_gate.yaml"
    if not p.exists():
        raise SystemExit("[prereg] config/exam_scale_cost_gate.yaml 缺失——全档真源缺失，禁开跑（fail-closed）")
    cg = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("cost_gate") or {}
    tiers = cg.get("tiers_bp")
    if not tiers:
        raise SystemExit("[prereg] exam_scale_cost_gate.cost_gate.tiers_bp 缺失/为空——全档真源损坏")
    return list(tiers)


def _resolve_stage_cost_tiers(stage: str, caps: dict | None = None) -> tuple[float, ...] | None:
    """方案①两轮制（裁定#413 下一窗口升级案）: stage → per-point 成本档位集。

    返回 None = 分层语义未启用（budget_caps.cost_gate_t1_tiers_bp 缺省）或无 stage 名义
    （""：普通批次保持现行行为逐位零漂移）——调用方不做 per-point 档位扫描。启用时:
      t1 → prereg 轻档集（如 [0,5] 两档粗筛）；t0/t2 → 全档（exam_scale_cost_gate.yaml
      真源）。轻档须为全档子集（口径一致性），档位非法=SystemExit fail-closed。
    T6: t3 家族=全档（挖矿 §3.3.3 成本门不放松；caps 未传时按 stage 读对应冻结册）。
    """
    from zephyr.backtest.regime_validation.exam_cost_gate import validate_scan_tiers

    if caps is None:
        caps = _load_prereg_caps(stage)
    if stage in T3_STAGES or stage in T3B_STAGES:
        # T6: t3/t3b 家族=全档成本门（挖矿 §3.3.3 成本门不放松；卡不设分层轻档键，
        # 档位集唯一真源=exam_scale_cost_gate.yaml，禁跳门）
        return tuple(validate_scan_tiers(_load_cost_gate_tiers()))
    if STAGED_TIERS_KEY not in caps:
        return None
    raw = caps[STAGED_TIERS_KEY]
    if raw is None:
        raise SystemExit(f"[prereg] budget_caps.{STAGED_TIERS_KEY}=null——分层语义字段在场但未冻结值（fail-closed）")
    try:
        light = validate_scan_tiers(raw)
        full_tiers = tuple(validate_scan_tiers(_load_cost_gate_tiers()))
    except ValueError as exc:  # 档位非法统一转 SystemExit（执行器预算闸 fail-closed 口径）
        raise SystemExit(f"[prereg] budget_caps.{STAGED_TIERS_KEY} 分层档位非法: {exc}") from exc
    if not set(light).issubset(full_tiers):
        raise SystemExit(
            f"[prereg] budget_caps.{STAGED_TIERS_KEY}={list(light)} 非全档 {list(full_tiers)} 子集——档位口径漂移，禁开跑"
        )
    # 字段在场即校验（冻结册损坏无论哪个 stage 都 fail-closed）；但 per-point 扫描
    # 只随 stage 名义启用——t1=轻档 / t0,t2=全档 / ""（普通批次）=不启用（零漂移）；
    # t3 家族已在上方提前返回全档。
    if stage == "t1":
        return light
    if stage in ("t0", "t2"):
        return full_tiers
    return None


def _apply_prereg_budget(stage: str, n_samples: int) -> int:
    """预注册预算钳制（w3_w5_precheck §2.2/§2.5：冻结册零消费方缺口治本）。

    fail-closed：册缺失/cost_gate_in_every_tier 未冻结/T1T2 未标定单格点耗时 → 拒跑。
    钳制次序：grid_points_cap 总帽 → stage 帽（t0/t1/t2 各自点数）。
    T3 方案①（2026-09-24）: budget_caps.cost_gate_t1_tiers_bp 在场时校验分层档位语义
    （轻档合法且为全档子集，master 开关 cost_gate_in_every_tier 仍须为 true——分层只
    收窄 T1 扫描档位，不放松"每档必有成本门"）；字段缺省=现行语义逐字零变化。
    T6（st-tclose-t3a-20261005）: stage ∈ T3 家族（t3/t3-t1/t3-t2）读 t3a 冻结册——
    总帽 t3_points+分层帽 t3_calibration_points/t3_tier1_points/t3_tier2_points；
    t3-t1/t3-t2 须 t3_per_point_seconds_measured 已回填（T3a-T0 标定门槛，null=禁跑）；
    t3（标定档）不要求回填键——T0 的唯一用途就是实测回填它。
    """
    caps = _load_prereg_caps(stage)
    if not caps.get("cost_gate_in_every_tier", False):
        raise SystemExit("[prereg] budget_caps.cost_gate_in_every_tier 未冻结为 true——成本门禁跳，禁开跑")
    if stage in T3_STAGES:
        cap_total_t3 = caps.get("t3_points")
        if cap_total_t3 and n_samples > int(cap_total_t3):
            print(f"[prereg] stage={stage} 点数 {n_samples} > t3_points={cap_total_t3}，钳制")
            n_samples = int(cap_total_t3)
        stage_key_t3 = {"t3": "t3_calibration_points", "t3-t1": "t3_tier1_points", "t3-t2": "t3_tier2_points"}[stage]
        cap_stage_t3 = caps.get(stage_key_t3)
        if cap_stage_t3 and n_samples > int(cap_stage_t3):
            print(f"[prereg] stage={stage} 点数 {n_samples} > {stage_key_t3}={cap_stage_t3}，钳制")
            n_samples = int(cap_stage_t3)
        if stage in ("t3-t1", "t3-t2") and not caps.get("t3_per_point_seconds_measured"):
            raise SystemExit(
                "[prereg] budget_caps.t3_per_point_seconds_measured=null（T3a-T0 未标定回填）——t3-t1/t3-t2 禁开跑"
            )
        return n_samples
    if stage in T3B_STAGES:
        cap_total_t3b = caps.get("t3b_points")
        if cap_total_t3b and n_samples > int(cap_total_t3b):
            print(f"[prereg] stage={stage} 点数 {n_samples} > t3b_points={cap_total_t3b}，钳制")
            n_samples = int(cap_total_t3b)
        stage_key_t3b = {"t3b": "t3b_calibration_points", "t3b-t1": "t3b_tier1_points", "t3b-t2": "t3b_tier2_points"}[
            stage
        ]
        cap_stage_t3b = caps.get(stage_key_t3b)
        if cap_stage_t3b and n_samples > int(cap_stage_t3b):
            print(f"[prereg] stage={stage} 点数 {n_samples} > {stage_key_t3b}={cap_stage_t3b}，钳制")
            n_samples = int(cap_stage_t3b)
        if stage in ("t3b-t1", "t3b-t2") and not caps.get("t3b_per_point_seconds_measured"):
            raise SystemExit(
                "[prereg] budget_caps.t3b_per_point_seconds_measured=null（T3b-T0 未标定回填）——t3b-t1/t3b-t2 禁开跑"
            )
        return n_samples
    if STAGED_TIERS_KEY in caps:
        _resolve_stage_cost_tiers(stage, caps)
    cap_total = caps.get("grid_points_cap")
    if cap_total and n_samples > int(cap_total):
        print(f"[prereg] --n-samples {n_samples} > grid_points_cap {cap_total}，钳制")
        n_samples = int(cap_total)
    stage_key = {"t0": "trial0_calibration_points", "t1": "tier1_points", "t2": "tier2_points"}.get(stage)
    if stage_key:
        cap_stage = caps.get(stage_key)
        if cap_stage and n_samples > int(cap_stage):
            print(f"[prereg] stage={stage} 点数 {n_samples} > {stage_key}={cap_stage}，钳制")
            n_samples = int(cap_stage)
        if stage in ("t1", "t2") and not caps.get("per_point_seconds_measured"):
            raise SystemExit("[prereg] budget_caps.per_point_seconds_measured=null（T0 未标定回填）——T1/T2 禁开跑")
    return n_samples


def _ask_compute_window_gate(stage: str = "") -> None:
    """E0 问闸（w3_w5_precheck §2.3：F06/grid 路 0 接缺口治本）。拒=SystemExit(3)。

    stage=t2 属波12 统一跑批窗口内容 A（T2 终审 900 格）⇒ purpose 换点火类，
    闸门自动前置"五触发条件+批准卡"预检（MOD-BT-226）；t0/t1/无 stage 走原语义不变。
    """
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo

    from compute_window_gate import check_gate

    purpose = "wave12_t2_final" if stage == "t2" else "f06_grid_batch"
    decision = check_gate(purpose, "local_gpu", _dt.now(ZoneInfo("Asia/Shanghai")))
    if not decision.get("allowed"):
        raise SystemExit(
            f"[E0] 算力窗问闸拒绝: reason_code={decision.get('reason_code')}"
            f" blocking={decision.get('blocking')}"
            + (f" detail={decision.get('detail')}" if decision.get("detail") else "")
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="F-06 批次 A 普查执行器")
    ap.add_argument("--smoke", action="store_true", help="烟测：8 格点管线联通")
    ap.add_argument("--n-samples", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260915)
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default="2023-12-31")
    ap.add_argument("--stratify-dims", default="", help="逗号分隔定向分层维（批次 A 扩容）")
    ap.add_argument("--subspace-json", default="", help="子空间枚举 JSON（批次 B）")
    ap.add_argument(
        "--stage",
        default="",
        choices=["", "t0", "t1", "t2", "t3", "t3-t1", "t3-t2", "t3b", "t3b-t1", "t3b-t2"],
        help="预算阶段（t0 标定 200/t1 粗扫 17100/t2 细化 13000；t3 家族=T3a 开闸考 t3a 冻结册钳制；空=沿用 n-samples 不受 stage 帽）",
    )
    ap.add_argument(
        "--skip-compute-gate",
        action="store_true",
        help="跳过 E0 日历窗问闸（仅 --smoke 管线联通允许；正式跑批禁用；波12 点火类 stage=t2 无效）",
    )
    ap.add_argument(
        "--engine",
        default="auto",
        choices=list(_VALID_ENGINES),
        help="计算引擎三态（L2-C）：cpu=恒 pandas 原路；gpu=显式张量核（波败 fail-closed 整波重跑 CPU）；auto=env/尺寸守卫解析（缺省）",
    )
    ap.add_argument(
        "--eval-backend",
        default="cpu",
        choices=list(_VALID_ENGINES),
        help="eval 面（A1 标准化/A2 合成/B-C 定尺寸）算力后端（st-gpux-20261011）："
        "cpu=原 pandas 路（缺省=逐字节零漂移）；gpu=可移植面上卡、串行步按 gpu_core "
        "既定交接点回原路并计数出声；auto=cupy+CUDA 在位才上卡。判据面/产物 schema 零改",
    )
    ap.add_argument(
        "--verify-counts",
        action="store_true",
        help="只读对账尺：网格产物身份集计数 vs 台账逐批对照（禁任何写）；缺账批显式点名（P0-6）",
    )
    ap.add_argument(
        "--verify-grid-root",
        default="",
        help="对账尺网格根目录覆盖（默认 data/strategy_intake；测试注入 tmp）",
    )
    ap.add_argument(
        "--shard-idx",
        type=int,
        default=None,
        help="确定性分片序号（配 --num-shards；i::k 轮转切片，并集=整跑；单 job 墙钟帽合规用）",
    )
    ap.add_argument(
        "--num-shards",
        type=int,
        default=None,
        help="确定性分片总数（缺省=不分片零漂移）；分片须串行跑（vram.concurrency=1）",
    )
    ap.add_argument(
        "--exploration-ledger",
        default="",
        help="探索扫描分册路径（与 N 账本分册：设值=批末不进 N 账本，批记录追本路径；深挖车道令 2026-10-10）",
    )
    ap.add_argument(
        "--context-json",
        default="",
        help="显式 context 注入（非 stage 批次用，如 T3b-T0 标定 '{\"phase\": 3}'；缺省空=零漂移）",
    )
    args = ap.parse_args()
    global _EXPLORATION_LEDGER, _EVAL_BACKEND
    _EXPLORATION_LEDGER = args.exploration_ledger or None
    _EVAL_BACKEND = args.eval_backend
    if args.verify_counts:
        return _verify_counts(args.verify_grid_root or None)
    # 波12 点火类不可旁路——--skip-compute-gate 只关日历窗，不关触发条件与批准卡
    if (not args.smoke and not args.skip_compute_gate) or args.stage == "t2":
        _ask_compute_window_gate(args.stage)
    stage_tiers = None
    ctx_overrides: dict | None = None
    factor_surface = "v1"
    exec_caliber = "close"
    cost_attribution = False
    if args.stage and not args.smoke:
        args.n_samples = _apply_prereg_budget(args.stage, args.n_samples)
        stage_tiers = _resolve_stage_cost_tiers(args.stage)
    elif not args.smoke:
        args.n_samples = _apply_prereg_budget("", args.n_samples)
        stage_tiers = _resolve_stage_cost_tiers("")
    if args.stage in T3B_STAGES and not args.smoke:
        # T3b: t3b 家族按 t3b 冻结卡注入考卷面（phase=3 激活 X 族；同 t3a 构造）
        card = _load_t3b_exam_card()
        exam = card.get("exam_definition") or {}
        ctx_overrides = dict(exam.get("context_overrides") or {})
        factor_surface = str(exam.get("factor_surface") or "v1")
        exec_caliber = str(exam.get("exec_caliber") or "close")
        if factor_surface not in FACTOR_SURFACES:
            raise SystemExit(f"[prereg] T3b 冻结卡 factor_surface 非法: {factor_surface}")
        if exec_caliber not in ("close", "next_open", "vwap"):
            raise SystemExit(f"[prereg] T3b 冻结卡 exec_caliber 非法: {exec_caliber}")
        cost_attribution = bool(exam.get("cost_attribution", True))
        _validate_defensive_whitelist_registration(exam.get("defensive_leg") or {})
        print(
            f"[prereg-t3b] 考卷面注入: context={ctx_overrides} factor_surface={factor_surface} "
            f"exec_caliber={exec_caliber} G_universe={exam.get('G_universe')} "
            f"X={exam.get('X_stop')}×{exam.get('X_breaker')} stratify={exam.get('stratify_dims')}"
        )
        print(
            "[prereg-t3b] 护盘白名单登记（MOD-POS-026 真源，登记≠启用 D114 休眠）: "
            f"tier1={defensive_whitelist_assets()['tier1']}"
        )
    elif args.stage in T3_STAGES and not args.smoke:
        # T6: t3 家族按 t3a 冻结卡注入考卷面（context/因子面/成交价口径/白名单登记校验）
        card = _load_t3a_exam_card()
        exam = card.get("exam_definition") or {}
        ctx_overrides = dict(exam.get("context_overrides") or {})
        factor_surface = str(exam.get("factor_surface") or "v1")
        exec_caliber = str(exam.get("exec_caliber") or "close")
        if factor_surface not in FACTOR_SURFACES:
            raise SystemExit(f"[prereg] T3a 冻结卡 factor_surface 非法: {factor_surface}")
        if exec_caliber not in ("close", "next_open", "vwap"):
            raise SystemExit(f"[prereg] T3a 冻结卡 exec_caliber 非法: {exec_caliber}")
        cost_attribution = bool(exam.get("cost_attribution", True))
        _validate_defensive_whitelist_registration(exam.get("defensive_leg") or {})
        print(
            f"[prereg-t3a] 考卷面注入: context={ctx_overrides} factor_surface={factor_surface} "
            f"exec_caliber={exec_caliber} G_universe={exam.get('G_universe')} "
            f"J={exam.get('J_regime_switch')} stratify={exam.get('stratify_dims')}"
        )
        print(
            "[prereg-t3a] 护盘白名单登记（MOD-POS-026 真源，登记≠启用 D114 休眠）: "
            f"tier1={defensive_whitelist_assets()['tier1']}"
        )
    if stage_tiers is not None:
        print(
            f"[prereg] stage={args.stage or '(none)'} per-point 成本档位={list(stage_tiers)}（方案①分层语义，裁定#413）"
        )
    import json as _json

    subspace = _json.loads(args.subspace_json) if args.subspace_json else None
    stratify = tuple(d for d in args.stratify_dims.split(",") if d)
    if ctx_overrides is None and args.context_json:
        # 显式 context 注入（20261007 袋B）：非 stage 批次的 T3b-T0 标定通道（phase=3
        # 激活 X 族；缺省空=零漂移）。stage 批次仍以冻卡注入为准，本旗标不参与。
        ctx_overrides = _json.loads(args.context_json)
    s = run_batch(
        args.n_samples,
        args.seed,
        args.start,
        args.end,
        smoke=args.smoke,
        subspace=subspace,
        stratify_dims=stratify,
        cost_gate_tiers_bp=stage_tiers,
        engine=args.engine,
        context_overrides=ctx_overrides,
        factor_surface=factor_surface,
        exec_caliber=exec_caliber,
        cost_attribution=cost_attribution,
        shard_idx=args.shard_idx,
        num_shards=args.num_shards,
    )
    print(json.dumps(s, ensure_ascii=False, indent=2))
    return 0


# noqa: m11-perm-manual-legitimate  F-06 批处理跑批件: CLI 手动/计划任务触发与 c4_batch_screen 同类，
# 非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界批处理作业
if __name__ == "__main__":
    raise SystemExit(main())
