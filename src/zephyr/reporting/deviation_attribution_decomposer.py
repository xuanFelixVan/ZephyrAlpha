# [BLUEPRINT] MOD-RPT-031 | 待统筹登记（battle_map BM-BT-05-H 四因子汇总点，55 号 §6 行）
# [MODULE] zephyr.reporting.deviation_attribution_decomposer
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-23(偏离告警触发后按需分解, 55号§6重评条件) ; MOD-RPT-009(周复盘"偏离与告警事件"段) ; decision_gate(四因子归因报警汇总点 BM-BT-05-H)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 四因子封闭集 {H-A 滑点偏差/H-B 数据滞后偏差/H-C 前瞻偏差残留/H-D 延迟差异偏差}(battle_map BM-BT-05-H 口径); 加性恒等 Σ已测量因子+未解释残差==总偏差(残差轧差定义保证); 因子测量归调用方(本模块纯计算不越界取数); 子维度分解须闭合到因子偏差(合计容差 1e-6, fail-closed); measured=False 因子禁携带数值(防误读, fail-closed); 降级口径=因子未就绪仅总值偏差不抛(battle_map ⑥); 输入必须有限实数(NaN/inf 拒绝); 只读不发射事件不改策略状态; frozen dataclass JSON 可序列化
# [MODIFY-GUARD] 55_monitoring_review.md §6; battle_map_03_backtest_validation.md BM-BT-05-H
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDeviationAttributionError(ZA-RPT-0033, fail-closed)
# [TESTS] tests/reporting/test_deviation_attribution_decomposer.py
# [A_module] module_id=MOD-RPT-031 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
MOD-RPT-031 — 回测-实盘偏离归因分解器（battle_map BM-BT-05-H 四因子汇总点）。

55 号 §6 暂缓项"偏离度量两口径之外加归因分解（H-A~D 四因子）"施工。
**口径裁定（派单纪律"源文档口径不同以源文档为准"）**：55 号 §6 的 H-A~D 指向
battle_map_03_backtest_validation.md BM-BT-05-H 四孙环节，本模块按其口径实现
四因子归因汇总点（回测预期+实盘实际→总偏差→4 因子归因→汇总→四因子归因报警）：

  | 因子 | 含义（battle_map 大白话） | 子维度（battle_map 归因维） | 数据获取（归调用方） |
  |---|---|---|---|
  | H-A 滑点偏差 | 回测假设 1bp 滑点 vs 实盘时变滑点的差 | 模型简化偏差/流动性误判/时机漂移/价差变化 | slippage_analyzer（EX_SOR） |
  | H-B 数据滞后偏差 | "数据即时可得"假设 vs 实盘到达延迟 | 数据源延迟/特征管线延迟/PIT 可得性延迟 | data_handler 插桩（设计态） |
  | H-C 前瞻偏差残留 | 执行时序/参数拟合/regime 标签三层偷看未来 | 执行时序/参数拟合/regime 标签 | look_ahead_bias_detector 残留层（设计态） |
  | H-D 延迟差异偏差 | 回测下单即成交 vs 实盘信号→成交回报延迟漂移 | 算法拆单/下单提交/限价单等待/成交回报 | execution_quality_scorer/algo_trading_engine |

与 risk/core/deviation_attribution.py（MOD-RK-23 伴随件，已在码）边界：
  彼=累计收益口径加性恒等分解（H-A 执行成本/H-B 时滞未成交/H-C 仓位权重/H-D 残差，
  工程裁定口径，因子字母局部于该件）；本件=battle_map BM-BT-05-H 四因子归因
  汇总点（偏差预算口径，字母口径=battle_map）。两者并存不互替——彼回答"收益
  差怎么 additive 拆"，本件回答"回测-实盘偏差预算被哪类偏差吃掉"。

工程裁定（battle_map 设计态无字段级契约，本模块定义最小口径）：
  - 偏差符号约定：负=使实盘劣于回测（拖累），正=使实盘优于回测；
  - 加性恒等：未解释残差=总偏差−Σ已测量因子（轧差定义，不丢信息）；
  - 降级（battle_map ⑥）：因子 measured=False（测量未就绪）→ 不参与分解，
    unmeasured_factors+notes 留痕，仅总值偏差——不抛不阻断；
  - 子维度闭合：dimensions 合计须等于因子偏差（容差 1e-6），保证
    "归因到子维度"是划分不是罗列；
  - 本模块不做告警阈值判定（>30% 告警/>50% 退役归 decision_gate/MOD-RK-23），
    只产分解快照；|残差|>|已解释| 时 notes 提示"四因子解释力不足"（复盘口径）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: total_deviation 参数
#   fields: 参数 total_deviation，类型注解 float
#   code: deviation_attribution_decomposer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: factors 参数
#   fields: 参数 factors，类型注解 Sequence[FactorBias]
#   code: deviation_attribution_decomposer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DeviationAttribution
#   name_en: DeviationAttribution
#   intro: 四因子归因分解快照（BM-BT-05-H 汇总点产出，JSON 可序列化）。
#   desc: 四因子归因分解快照（BM-BT-05-H 汇总点产出，JSON 可序列化）。；公共方法（定义序）: to_dict；源码 L163-L176
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② decompose_deviation_attribution
#   name_en: decompose_deviation_attribution
#   intro: 回测 vs 实盘总偏差的 BM-BT-05-H 四因子归因分解。
#   desc: 回测 vs 实盘总偏差的 BM-BT-05-H 四因子归因分解。 Args: total_deviation: 总偏差（实盘−回测，收益口径带符号；供给方=MOD-RK-23 偏…；源码 L218-L287
#   inputs: total_deviation factors
#   outputs: DeviationAttribution
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: DeviationAttribution
#   name_en: DeviationAttribution
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-RK-23(偏离告警触发后按需分解, 55号§6重评条件) ; MOD-RPT-009(周复盘"偏离与告警事件"段) ; decision_gate(…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "FACTOR_H_A",
    "FACTOR_H_B",
    "FACTOR_H_C",
    "FACTOR_H_D",
    "FACTOR_IDS",
    "DeviationAttribution",
    "DimensionBias",
    "FactorAttribution",
    "FactorBias",
    "InvalidDeviationAttributionError",
    "decompose_deviation_attribution",
]

#: 四因子封闭集（battle_map BM-BT-05-H-A~D 口径）
FACTOR_H_A: Final[str] = "H-A"  # 滑点偏差
FACTOR_H_B: Final[str] = "H-B"  # 数据滞后偏差
FACTOR_H_C: Final[str] = "H-C"  # 前瞻偏差残留
FACTOR_H_D: Final[str] = "H-D"  # 延迟差异偏差
FACTOR_IDS: Final[tuple[str, ...]] = (FACTOR_H_A, FACTOR_H_B, FACTOR_H_C, FACTOR_H_D)

#: 子维度合计闭合容差（浮点尾差）
_DIM_SUM_TOLERANCE: Final[float] = 1e-6
#: 加性恒等审计容差
_SUM_TOLERANCE: Final[float] = 1e-9


class InvalidDeviationAttributionError(ZephyrBaseError):
    """偏离归因分解输入非法——未知/重复因子、非有限数值、子维度不闭合、未就绪因子携带数值。"""

    error_code = "ZA-RPT-0033"


@dataclass(frozen=True, slots=True)
class DimensionBias:
    """因子子维度偏差（battle_map 归因维，如 H-A 的"流动性误判"）。"""

    name: str
    bias: float  # 带符号（负=拖累实盘 vs 回测）


@dataclass(frozen=True, slots=True)
class FactorBias:
    """单因子偏差测量输入（调用方预计算供给，本模块纯计算）。

    measured=False 表示该因子测量未就绪（battle_map ⑥ 降级口径）——
    此时 bias 须为 0.0 且 dimensions 为空（禁携带数值防误读，fail-closed）。
    """

    factor: str  # 封闭集 FACTOR_IDS
    bias: float = 0.0
    dimensions: tuple[DimensionBias, ...] = ()
    measured: bool = True


@dataclass(frozen=True, slots=True)
class FactorAttribution:
    """单因子归因产出（已测量因子）。"""

    factor: str
    bias: float
    share_of_total: float  # bias/total（带符号；total≈0 时为 0）
    dimensions: tuple[DimensionBias, ...] = ()


@dataclass(frozen=True, slots=True)
class DeviationAttribution:
    """四因子归因分解快照（BM-BT-05-H 汇总点产出，JSON 可序列化）。"""

    total_deviation: float
    explained_deviation: float
    unexplained_residual: float
    factors: tuple[FactorAttribution, ...]
    unmeasured_factors: tuple[str, ...]
    dominant_factor: str | None  # |bias| 最大的已测量因子；全未就绪=None
    invariant_status: str  # PASS/FAIL（Σ已测量+残差==总偏差 审计位）
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise InvalidDeviationAttributionError(
            f"{name} 必须为有限实数",
            details={"field": name, "value": str(value)},
        )
    return v


def _validate_factor(item: FactorBias) -> None:
    if item.factor not in FACTOR_IDS:
        raise InvalidDeviationAttributionError(
            f"未知偏离因子: {item.factor}（封闭集 H-A/H-B/H-C/H-D，battle_map BM-BT-05-H 口径）",
            details={"factor": str(item.factor)},
        )
    bias = _require_finite(f"factor[{item.factor}].bias", item.bias)
    if not item.measured:
        if bias != 0.0 or item.dimensions:
            raise InvalidDeviationAttributionError(
                f"因子 {item.factor} 未就绪（measured=False）禁止携带数值",
                details={"factor": item.factor, "bias": str(item.bias)},
            )
        return
    dim_sum = 0.0
    for dim in item.dimensions:
        if not isinstance(dim.name, str) or not dim.name.strip():
            raise InvalidDeviationAttributionError(
                f"因子 {item.factor} 子维度名不允许为空",
                details={"factor": item.factor},
            )
        dim_sum += _require_finite(f"factor[{item.factor}].dimension[{dim.name}].bias", dim.bias)
    if item.dimensions and abs(dim_sum - bias) > _DIM_SUM_TOLERANCE:
        raise InvalidDeviationAttributionError(
            f"因子 {item.factor} 子维度合计不闭合（{dim_sum} != {bias}，须划分到因子偏差）",
            details={"factor": item.factor, "dim_sum": str(dim_sum), "bias": str(bias)},
        )


def decompose_deviation_attribution(
    total_deviation: float,
    factors: Sequence[FactorBias],
) -> DeviationAttribution:
    """回测 vs 实盘总偏差的 BM-BT-05-H 四因子归因分解。

    Args:
        total_deviation: 总偏差（实盘−回测，收益口径带符号；供给方=MOD-RK-23
            偏离监控/调用方）。
        factors: 四因子测量输入（FactorBias 序列；未供给/未就绪因子按
            battle_map ⑥ 降级——仅总值偏差+留痕）。

    Returns:
        DeviationAttribution（explained/residual/dominant/shares + 审计位）。

    Raises:
        InvalidDeviationAttributionError: 未知/重复因子、非有限数值、
            子维度不闭合、未就绪因子携带数值。
    """
    total = _require_finite("total_deviation", total_deviation)

    seen: set[str] = set()
    measured: list[FactorBias] = []
    for item in factors:
        _validate_factor(item)
        if item.factor in seen:
            raise InvalidDeviationAttributionError(
                f"因子重复供给: {item.factor}",
                details={"factor": item.factor},
            )
        seen.add(item.factor)
        if item.measured:
            measured.append(item)

    measured_ids = {f.factor for f in measured}
    unmeasured = tuple(fid for fid in FACTOR_IDS if fid not in measured_ids)

    explained = math.fsum(f.bias for f in measured)
    residual = total - explained
    abs_total = abs(total)
    attributions = tuple(
        FactorAttribution(
            factor=f.factor,
            bias=f.bias,
            share_of_total=(f.bias / total if abs_total > 1e-12 else 0.0),
            dimensions=f.dimensions,
        )
        for f in measured
    )
    dominant = max(measured, key=lambda f: abs(f.bias)).factor if measured else None

    notes: list[str] = []
    if unmeasured:
        notes.append(f"因子未就绪/未供给：{'、'.join(unmeasured)}（降级不参与分解）")
    if not measured:
        notes.append("四因子均未就绪：仅总值偏差（battle_map ⑥ 降级口径）")
    elif abs(residual) > abs(explained):
        notes.append("未解释残差大于已解释部分（四因子解释力不足，复盘口径提示）")

    invariant = "PASS" if abs(explained + residual - total) <= _SUM_TOLERANCE else "FAIL"
    return DeviationAttribution(
        total_deviation=total,
        explained_deviation=explained,
        unexplained_residual=residual,
        factors=attributions,
        unmeasured_factors=unmeasured,
        dominant_factor=dominant,
        invariant_status=invariant,
        notes=tuple(notes),
    )
