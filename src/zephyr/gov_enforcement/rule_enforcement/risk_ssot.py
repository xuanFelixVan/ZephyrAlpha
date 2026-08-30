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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
risk_ssot — 从 ``config/risk_params.yaml`` 加载风险真源（INV-002 等）

供 G10–G12 交易类门禁在 **Orc 任务路径** 上做参数与 SSoT 一致性校验；
不涉及组合持仓运行时数据。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path
#   code: risk_ssot.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① load_risk_params_ssot
#   name_en: load_risk_params_ssot
#   intro: load_risk_params_ssot(project_root) 源码 L57-L64
#   desc: 源码 L57-L64
#   inputs: project_root
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {}
