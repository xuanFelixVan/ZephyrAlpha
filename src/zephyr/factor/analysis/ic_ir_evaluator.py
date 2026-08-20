# [BLUEPRINT] MOD-L02-003 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-02
# [MODULE] zephyr.factor.analysis.ic_ir_evaluator
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.factor.core.evaluation.metrics
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——评估仅使用已实现前向收益
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单因子失败->该因子结果缺失，不阻断其他因子; 空输入->空dict
# [TESTS] tests/factor/test_ic_ir_evaluator.py
# [A_module] module_id=MOD-L02-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D-FACTOR-ANA-02 多因子评估报告器——批量评估+格式化报告。

封装 evaluate_factor，返回结构化 EvaluationResult 字典，并提供格式化报告输出。
与 ic_ir_calc 的区别：ic_ir_calc 返回 DataFrame 表格，本模块返回结构化结果+文本报告。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 已注册因子ID列表 list[str]
#   fields: 待批量评估的 factor_id
#   code: factor_ids 函数参数
# - id: I2
#   name: 评估参数组
#   fields: symbols 标的池 + start/end 回测区间 + horizon=5 + oos_ratio=0.3
#   code: evaluate_multiple 函数参数
# 层: 算法
# - id: A1
#   name_zh: ① 多因子批量评估
#   name_en: evaluate_multiple
#   intro: 逐个因子调 evaluate_factor 做全链路评估，单因子失败跳过不阻断
#   desc: 循环 factor_ids 调 core.evaluation.backtest.evaluate_factor；KeyError记warning跳过，其他异常记日志继续（L51-59）
#   inputs: I1 I2
#   outputs: dict[factor_id, EvaluationResult]
#   invariant: INV-004 PIT铁律——评估仅用已实现前向收益
# - id: A2
#   name_zh: ② 评估报告格式化
#   name_en: format_report
#   intro: 把评估结果排成78列宽的可读文本表格
#   desc: 按 factor_id 排序输出 ic_mean/ic_std/ir/oos%/overfit/n 六列（L62-84）；空结果返回占位文本
#   inputs: A1
#   outputs: 多行文本报告 str
# 层: 输出
# - id: O1
#   name_zh: 结构化评估结果映射
#   name_en: dict[str, EvaluationResult]
#   intro: factor_id→评估结果（含IC/IR/OOS正率/过拟合标记/样本数）
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 多因子评估文本报告
#   name_en: formatted report str
#   intro: 横向对比各因子IC/IR指标的格式化报告
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A1 --> O1
# A2 --> O2
"""

from __future__ import annotations

import logging

from zephyr.factor.core.evaluation.backtest import EvaluationResult, evaluate_factor

log = logging.getLogger(__name__)


def evaluate_multiple(
    factor_ids: list[str],
    symbols: list[str],
    start: str,
    end: str,
    horizon: int = 5,
    oos_ratio: float = 0.3,
) -> dict[str, EvaluationResult]:
    """批量评估多因子，返回 factor_id → EvaluationResult 映射。

    Args:
        factor_ids: 已注册的因子 ID 列表
        symbols: 评估标的池
        start: 回测起始日期 'YYYY-MM-DD'
        end: 回测结束日期 'YYYY-MM-DD'
        horizon: 前向收益周期，默认 5
        oos_ratio: 样本外比例，默认 0.3

    Returns:
        dict[str, EvaluationResult]。单因子失败时该因子不在结果中。
    """
    results: dict[str, EvaluationResult] = {}
    for fid in factor_ids:
        try:
            results[fid] = evaluate_factor(fid, symbols, start, end, horizon, oos_ratio)
        except KeyError:
            log.warning("ic_ir_evaluator: 因子 '%s' 未注册，跳过", fid)
        except Exception:
            log.exception("ic_ir_evaluator: 因子 '%s' 评估失败", fid)
    return results


def format_report(results: dict[str, EvaluationResult]) -> str:
    """将评估结果格式化为可读文本报告。

    Args:
        results: evaluate_multiple 返回的结果

    Returns:
        格式化的多行文本报告
    """
    if not results:
        return "（无评估结果）"
    lines = ["=" * 78, "多因子评估报告", "=" * 78]
    header = f"{'factor_id':<20} {'ic_mean':>8} {'ic_std':>8} {'ir':>8} {'oos%':>8} {'overfit':>8} {'n':>6}"
    lines.append(header)
    lines.append("-" * 78)
    for fid, r in sorted(results.items()):
        overfit_str = "是" if r.is_overfitted else "否"
        lines.append(
            f"{fid:<20} {r.ic_mean:>8.4f} {r.ic_std:>8.4f} {r.ir:>8.4f} "
            f"{r.oos_positive_rate:>7.2%} {overfit_str:>8} {r.sample_size:>6}"
        )
    lines.append("=" * 78)
    return "\n".join(lines)
