# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.risk_ssot
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_risk_ssot | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
risk_ssot — 从 ``config/risk_params.yaml`` 加载风险真源（INV-002 等）

供 G10–G12 交易类门禁在 **Orc 任务路径** 上做参数与 SSoT 一致性校验；
不涉及组合持仓运行时数据。
"""

from pathlib import Path
from typing import Any

import yaml


def load_risk_params_ssot(project_root: Path) -> dict[str, Any]:
    path = project_root / "config" / "risk_params.yaml"
    if not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
