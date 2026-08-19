# [BLUEPRINT] 90_methodology_open_questions.md §2（v2.0.0 裁定）
# [MODULE] zephyr.factor.analysis.bhy_fdr
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy
# [CONSUMERS] factor_pool_manager 入池门禁（abs001_gate，接线待排期，本批仅交付模块本体）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 任意依赖默认 c(m)=Σ1/i 调和因子；拒绝掩码映射回原始输入顺序；q∈(0,1)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] q 越界/NaN p 值→ValueError
# [TESTS] tests/factor/test_bhy_fdr.py
# [A_module] module_id=MOD-L02-BHY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_FACTOR — BHY FDR 多重检验校正（90 号 Phase2 项，#2 因子IC 双轨采纳）

裁定真源：90_methodology_open_questions.md §2（v2.0.0）：
  硬性统计门禁：ICIR≥0.5 + BHY 控制 FDR q=10%（单批筛选 >100 因子时
  t 门槛升 2.8，Harvey-Liu-Zhu 标准）；入池流程：
  IC/RankIC 回测 → BHY FDR 校正 → ICIR≥0.5 → 滚动分位前 50% → candidate。

算法（Benjamini-Hochberg-Yekutieli）：
  升序 p_(1)≤…≤p_(m)；c(m)=Σ_{i=1..m} 1/i（任意依赖稳健；独立/正相关取 1 即 BH）；
  k = max{i : p_(i) ≤ i·q/(m·c(m))}；拒绝 H_(1)..H_(k)；无满足则零拒绝。

注：memo 原述"statsmodels multipletests 直接可用"，但 statsmodels 非项目依赖
（requirements.txt 无）；BHY 为闭式程序，此处纯 numpy 实现等价语义。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["BHYFDRResult", "bhy_fdr"]

#: 默认 FDR 控制水平（90 号 §2 裁定③：BHY q=10%）
DEFAULT_Q: float = 0.10


@dataclass(frozen=True)
class BHYFDRResult:
    """BHY 校正结果。"""

    rejected: list[bool]   # 拒绝掩码（原始输入顺序）
    n_rejected: int
    threshold: float       # 临界 p 值阈值（k 对应阈值；零拒绝=0.0）
    q: float
    m: int


def bhy_fdr(
    p_values: list[float] | np.ndarray,
    q: float = DEFAULT_Q,
    *,
    arbitrary_dependence: bool = True,
) -> BHYFDRResult:
    """BHY FDR 校正。

    Args:
        p_values: 单批检验 p 值序列
        q: FDR 控制水平（默认 0.10，90 号 §2）
        arbitrary_dependence: True=c(m)=Σ1/i（BHY 任意依赖稳健，默认）；
            False=c(m)=1（退化为 BH，独立/正相关场景）

    Returns:
        BHYFDRResult（拒绝掩码为原始输入顺序）

    Raises:
        ValueError: q 不在 (0,1) 或 p 值含 NaN/越界
    """
    if not 0 < q < 1:
        raise ValueError(f"q 必须在 (0,1)，实际 {q}")

    p = np.asarray(list(p_values), dtype=float)
    m = p.size
    if m == 0:
        return BHYFDRResult(rejected=[], n_rejected=0, threshold=0.0, q=q, m=0)
    if np.isnan(p).any():
        raise ValueError("p 值含 NaN")
    if (p < 0).any() or (p > 1).any():
        raise ValueError("p 值必须在 [0,1]")

    c_m = float(np.sum(1.0 / np.arange(1, m + 1))) if arbitrary_dependence else 1.0

    order = np.argsort(p, kind="stable")
    p_sorted = p[order]
    ranks = np.arange(1, m + 1)
    crit = ranks * q / (m * c_m)

    passed = p_sorted <= crit
    k = int(np.max(ranks[passed])) if passed.any() else 0

    rejected_sorted = np.zeros(m, dtype=bool)
    if k > 0:
        rejected_sorted[:k] = True
    rejected = np.zeros(m, dtype=bool)
    rejected[order] = rejected_sorted

    threshold = float(crit[k - 1]) if k > 0 else 0.0
    return BHYFDRResult(
        rejected=rejected.tolist(),
        n_rejected=k,
        threshold=threshold,
        q=q,
        m=m,
    )
