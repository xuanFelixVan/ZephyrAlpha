# [BLUEPRINT] MOD-L02-001 | (pending)
# [MODULE] zephyr.factor.technical_indicators.statistics
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.technical_indicators.indicator_base; pandas(pip); numpy(pip)
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider（包级 autodiscover 动态接线：internal_compute_provider L545/L1113 延迟导入本包+注册表消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 统计族指标 4 个/5 输出列，纯自实现 pandas/numpy；compute→DataFrame 多列输出
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute 输入空 DataFrame→返回空 DataFrame 不抛；输入缺列→ValueError
# [TESTS] tests/zephyr/factor/technical_indicators/test_statistics.py
# [A_module] module_id=MOD-L02-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

统计族技术指标（4 个指标/5 输出列，2026-09-14 统计族批新建；TSF 与 LINEARREG 同类双列）。

指标清单：CORREL/BETA/LINEARREG(+TSF 双列)/ROLLVAR

对齐 TA-Lib Statistic Functions 组（通达信无对应函数，口径注明 TA-Lib）：
  - CORREL/BETA 为量价统计基建（默认 close×volume 对，滚动窗口）
  - LINEARREG/TSF 为滚动一元线性回归拟合值/一步外推预测（同类双列）
  - ROLLVAR 为滚动总体方差（ddof=0，与 BOLL std ddof=0 口径一致）
  - LINEARREG/TSF 用滚动矩法向量化（Σxy 恒等式拆解），不用 rolling.apply 逐窗拟合

设计文档：16_technical_indicator_catalog.md §2.6

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 行情OHLCV数据 DataFrame
#   fields: close/volume 列（各指标按 meta.input_columns 取用）
#   code: compute(data: pd.DataFrame)
# 层: 指标
# - id: CORREL
#   name_zh: 滚动相关系数CORREL 30
#   name_en: CORREL
#   intro: close×volume 滚动 Pearson 相关，量价背离/共振的统计基线
#   formula: r=Σ(x-x̄)(y-ȳ)/√(Σ(x-x̄)²Σ(y-ȳ)²)，滚动 30 窗
#   code: statistics.py CORREL 类
#   registry: 指标表: 有correl_30列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# - id: LINEARREG
#   name_zh: 线性回归线LINEARREG/TSF 14
#   name_en: LINEARREG/TSF
#   intro: 滚动一元线性回归的当前拟合值与一步外推预测，趋势斜率视角的平滑线
#   formula: b=(NΣxy−ΣxΣy)/(NΣx²−(Σx)²)，a=(Σy−bΣx)/N；LINEARREG=a+b(N−1)；TSF=a+bN
#   code: statistics.py LINEARREG 类
#   registry: 指标表: 有linearreg_14/tsf_14列 但代码未读表（本模块即指标计算实现）
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 校验+参数合并+空表短路 compute统一契约
#   name_en: TechnicalIndicatorBase.compute
#   intro: 每个指标入口先校验列、空表直接返回空 DataFrame、再合并默认参数
#   desc: validate(data) 缺列抛 ValueError → data.empty 返回空表 → get_params(**kwargs) 合并默认参数
#   inputs: I1
#   outputs: 校验通过的 data 与 params
#   invariant: 空 DataFrame 输入→空 DataFrame 输出不抛异常
# - id: A2
#   name_zh: ② 滚动回归矩法向量化
#   name_en: _rolling_linefit
#   intro: 用 Σxy=Σ(j·y)−(t−N+1)·Σy 恒等式把逐窗拟合拆成滚动和，避免 rolling.apply 慢路径
#   desc: s0=y.rolling(N).sum()；s1=(j·y).rolling(N).sum() → slope/intercept 闭式解
#   inputs: I1
#   outputs: (slope, intercept) 二元组
# 层: 输出
# - id: O1
#   name_zh: 统计族指标 DataFrame（5指标多列）
#   name_en: statistics indicators DataFrame
#   intro: CORREL/BETA/LINEARREG/TSF/VAR 共5个统计指标的多列输出，index 与输入对齐
#   invariant: 输出列严格等于各 meta.output_columns（correl_30、beta_30、linearreg_14、tsf_14、var_20）
#   downstream: zephyr.data.implementations.internal_compute_provider（批量计算写入 c1_market.technical_indicator）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# A1 -.->|断点| CORREL
# A1 -.->|断点| LINEARREG
# A2 -.->|断点| LINEARREG
# CORREL --> O1
# LINEARREG --> O1
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
)

# ---------------------------------------------------------------------------
# 模块级辅助函数
# ---------------------------------------------------------------------------


def _rolling_linefit(
    y: pd.Series, n: int
) -> tuple[pd.Series, pd.Series]:
    """滚动一元线性回归闭式解（窗口内 x=0..N-1）。

    矩法：b=(NΣxy−ΣxΣy)/(NΣx²−(Σx)²)，a=(Σy−bΣx)/N。
    Σxy 恒等式拆解：窗口 [t−N+1..t] 内 Σ(i·y_i) = Σ(j·y_j) − (t−N+1)·Σy_j（j 为全局下标），
    全部化为滚动和，O(len) 向量化，替代 rolling.apply 逐窗拟合。
    """
    j = pd.Series(np.arange(len(y), dtype=float), index=y.index)
    s0 = y.rolling(window=n).sum()
    s1 = (j * y).rolling(window=n).sum()
    # 窗口起点 t−N+1
    start = j - (n - 1)
    sum_xy = s1 - start * s0
    sum_x = n * (n - 1) / 2
    sum_x2 = n * (n - 1) * (2 * n - 1) / 6
    denom = n * sum_x2 - sum_x * sum_x
    slope = (n * sum_xy - sum_x * s0) / denom
    intercept = (s0 - slope * sum_x) / n
    return slope, intercept


@TechnicalIndicatorRegistry.register
class CORREL(TechnicalIndicatorBase):
    """滚动 Pearson 相关系数（TA-Lib CORREL，默认 close×volume 30 窗）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="correl",
        name="滚动相关系数",
        category="statistics",
        output_columns=["correl_30"],
        input_columns=["close", "volume"],
        params={"period": 30},
        version="1.0.0",
        description="r=Cov(x,y)/(σx·σy)，x=close y=volume 滚动 30 窗；量价背离/共振统计基线（TA-Lib 口径）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        correl = data["close"].rolling(window=n).corr(data["volume"])
        return pd.DataFrame({f"correl_{n}": correl}, index=data.index)


@TechnicalIndicatorRegistry.register
class BETA(TechnicalIndicatorBase):
    """滚动 beta 系数（TA-Lib BETA，默认 close 对 volume 30 窗）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="beta",
        name="滚动beta系数",
        category="statistics",
        output_columns=["beta_30"],
        input_columns=["close", "volume"],
        params={"period": 30},
        version="1.0.0",
        description="beta=Cov(x,y)/Var(y)，x=close y=volume 滚动 30 窗（TA-Lib 口径）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        y = data["volume"]
        beta = data["close"].rolling(window=n).cov(y) / y.rolling(window=n).var()
        return pd.DataFrame({f"beta_{n}": beta}, index=data.index)


@TechnicalIndicatorRegistry.register
class LINEARREG(TechnicalIndicatorBase):
    """线性回归线与一步外推预测（TA-Lib LINEARREG/TSF，14 窗）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="linearreg",
        name="线性回归线",
        category="statistics",
        output_columns=["linearreg_14", "tsf_14"],
        input_columns=["close"],
        params={"period": 14},
        version="1.0.0",
        description="滚动拟合 y=a+bx（x=0..N−1）：LINEARREG=a+b(N−1)（当前拟合值），TSF=a+bN（下一根预测）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        slope, intercept = _rolling_linefit(data["close"], n)
        linreg = intercept + slope * (n - 1)
        tsf = intercept + slope * n
        return pd.DataFrame(
            {f"linearreg_{n}": linreg, f"tsf_{n}": tsf}, index=data.index
        )


@TechnicalIndicatorRegistry.register
class ROLLVAR(TechnicalIndicatorBase):
    """滚动总体方差（TA-Lib VAR，20 窗，ddof=0 与 BOLL std 口径一致）。"""

    meta = TechnicalIndicatorMeta(
        indicator_id="rollvar",
        name="滚动方差",
        category="statistics",
        output_columns=["var_20"],
        input_columns=["close"],
        params={"period": 20},
        version="1.0.0",
        description="Var=Σ(x−x̄)²/N 滚动 20 窗，ddof=0（总体方差，与 BOLL 中轨 std 口径一致）",
    )

    def compute(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        self.validate(data)
        if data.empty:
            return pd.DataFrame(columns=self.meta.output_columns)
        params = self.get_params(**kwargs)
        n = params["period"]
        var = data["close"].rolling(window=n).var(ddof=0)
        return pd.DataFrame({f"var_{n}": var}, index=data.index)
