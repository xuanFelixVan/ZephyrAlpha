# [BLUEPRINT] MOD-L02-002 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-01
# [MODULE] zephyr.factor.analysis.ic_ir_calc
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.core.evaluation.metrics
# [CONSUMERS] zephyr.factor.analysis.ic_ir_evaluator; zephyr.factor.analysis.multifactor_synthesis
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——所有 IC/IR 计算仅使用同期因子值与已实现前向收益
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单因子评估失败->该行指标为0，不阻断其他因子; 空输入->空DataFrame
# [TESTS] tests/factor/test_ic_ir_calc.py
# [A_module] module_id=MOD-L02-002 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-01 IC/IR 批量计算器——多因子 IC/IR 指标汇总表。

封装 evaluate_factor，对多个因子批量评估，返回含 factor_id/ic_mean/ic_std/ir/oos_rate
的 DataFrame，便于横向对比。

职责边界：
- 批量调用 evaluate_factor（复用 backtest.py 的数据加载+因子计算+IC计算全链路）
- 汇总指标为 DataFrame 表格
- 单因子失败不阻断其他因子（容错）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 已注册因子ID列表 list[str]
#   fields: 待批量计算的 factor_id
#   code: factor_ids 函数参数
# - id: I2
#   name: 评估参数组
#   fields: symbols 标的池 + start/end 回测区间 + horizon=5 + oos_ratio=0.3
#   code: compute_ic_ir_table 函数参数
# 层: 算法
# - id: A1
#   name_zh: ① IC/IR批量计算汇总
#   name_en: compute_ic_ir_table
#   intro: 循环调 evaluate_factor 全链路评估，把各因子指标汇总成一张表
#   desc: 逐因子调 core.evaluation.backtest.evaluate_factor，收集 ic_mean/ic_std/ir/oos_positive_rate/is_overfitted/sample_size 七列；单因子失败该行指标置0不阻断（L59-86）
#   inputs: I1 I2
#   outputs: IC/IR指标汇总表 DataFrame
#   invariant: INV-004 PIT铁律——IC/IR仅用同期因子值与已实现前向收益；失败行指标为0且is_overfitted=True
# 层: 输出
# - id: O1
#   name_zh: 多因子IC/IR指标表 DataFrame
#   name_en: ic_ir table DataFrame
#   intro: columns=[factor_id, ic_mean, ic_std, ir, oos_positive_rate, is_overfitted, sample_size]，便于横向对比
#   downstream: ic_ir_evaluator MOD-L02-003；multifactor_synthesis MOD-L02-011
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

import pandas as pd

from zephyr.factor.core.evaluation.backtest import evaluate_factor

log = logging.getLogger(__name__)


def compute_ic_ir_table(
    factor_ids: list[str],
    symbols: list[str],
    start: str,
    end: str,
    horizon: int = 5,
    oos_ratio: float = 0.3,
) -> pd.DataFrame:
    """批量计算多因子的 IC/IR 指标表。

    Args:
        factor_ids: 已注册的因子 ID 列表
        symbols: 评估标的池
        start: 回测起始日期 'YYYY-MM-DD'
        end: 回测结束日期 'YYYY-MM-DD'
        horizon: 前向收益周期，默认 5
        oos_ratio: 样本外比例，默认 0.3

    Returns:
        DataFrame，列=[factor_id, ic_mean, ic_std, ir, oos_positive_rate,
        is_overfitted, sample_size]。单因子失败时该行指标为 0。
    """
    rows: list[dict] = []
    for fid in factor_ids:
        try:
            result = evaluate_factor(fid, symbols, start, end, horizon, oos_ratio)
            rows.append(
                {
                    "factor_id": result.factor_id,
                    "ic_mean": result.ic_mean,
                    "ic_std": result.ic_std,
                    "ir": result.ir,
                    "oos_positive_rate": result.oos_positive_rate,
                    "is_overfitted": result.is_overfitted,
                    "sample_size": result.sample_size,
                }
            )
        except KeyError:
            log.warning("ic_ir_calc: 因子 '%s' 未注册，跳过", fid)
            rows.append(
                {
                    "factor_id": fid,
                    "ic_mean": 0.0,
                    "ic_std": 0.0,
                    "ir": 0.0,
                    "oos_positive_rate": 0.0,
                    "is_overfitted": True,
                    "sample_size": 0,
                }
            )
        except Exception:
            log.exception("ic_ir_calc: 因子 '%s' 评估失败", fid)
            rows.append(
                {
                    "factor_id": fid,
                    "ic_mean": 0.0,
                    "ic_std": 0.0,
                    "ir": 0.0,
                    "oos_positive_rate": 0.0,
                    "is_overfitted": True,
                    "sample_size": 0,
                }
            )
    return pd.DataFrame(rows)
