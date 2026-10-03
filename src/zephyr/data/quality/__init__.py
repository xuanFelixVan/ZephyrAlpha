# [BLUEPRINT] MOD-DATENG-003 | docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/blueprint.md
# [MODULE] zephyr.data.quality
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.quality.sla_breach_predictor; zephyr.data.quality.archive_sla_burnrate
# [CONSUMERS] zephyr.data.supply_sentinel（同域邻接，未接线）; 运维 CLI（archive_sla_burnrate 手动巡检）
# [STARTUP] imported
# [MATURITY] trial
# [INVARIANTS] 门面零判据值（真源各件自带，RULE-SSOT）; 子件缺失走守卫式导入不断链（data_eng 在案可逆模式）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/zephyr/data/quality/
# [TTL] permanent
"""D_DATA 质量子包 — SLA 违约预测 + F08 归档链 burn-rate 消费面。

T1-B1 融合（2026-09-30，Owner 批"挖矿确定无用即可删"同批 salvaging）：
sla_breach_predictor 自 src/zephyr/data_eng/（F127 退役包）迁入本址，
archive_sla_burnrate 为其唯一消费面（读 scripts/ch/archiver.py F08 链
manifest，做归档新鲜度 SLA 违约预测）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 子件公共面（sla_breach_predictor 五符号 + archive_sla_burnrate 巡检入口）
# 层: 处理
# - id: P1
#   name: 门面 re-export（守卫式导入，判据值零持有 RULE-SSOT）
# 层: 输出
# - id: O1
#   name: zephyr.data.quality 包命名空间（__all__ 六符号）
# 边:
# I1 -> P1 -> O1
"""

from __future__ import annotations

from typing import Final

from zephyr.data.quality.sla_breach_predictor import (
    BreachForecast,
    BurnRateLevel,
    QualitySlaBreachPredictor,
    QualitySlaPredictorError,
    SloPoint,
)

try:
    from zephyr.data.quality.archive_sla_burnrate import run_archive_sla_burnrate
except ImportError:  # pragma: no cover — 守卫式导入（依赖未落地不包断链）
    run_archive_sla_burnrate = None  # type: ignore[assignment]

__all__: Final = [
    "BreachForecast",
    "BurnRateLevel",
    "QualitySlaBreachPredictor",
    "QualitySlaPredictorError",
    "SloPoint",
    "run_archive_sla_burnrate",
]
