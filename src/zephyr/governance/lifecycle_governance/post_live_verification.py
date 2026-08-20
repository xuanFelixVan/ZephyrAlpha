# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.post_live_verification
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.__init__; zephyr.shared.alerts.threshold_loader
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PLV 五项规约阈值唯一真源=alert_threshold_registry(THD-PLV-001~005,fail-closed,字符串规约不数值化)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlertThresholdConfigError(注册表缺失/畸形)
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Final

from pydantic import BaseModel

from zephyr.shared.alerts.threshold_loader import load_alert_thresholds


class PLVCheck(str, Enum):
    ORDER_COUNT_DEVIATION = "order_count_deviation"
    FILL_RATE_COMPARISON = "fill_rate_comparison"
    RISK_CONFORMANCE = "risk_conformance"
    DATA_INTEGRITY = "data_integrity"
    PNL_RECONCILIATION = "pnl_reconciliation"


class PLVSpec(BaseModel):
    check: PLVCheck
    label: str
    threshold: str
    description: str


#: PLV 检查项 ↔ 注册表条目映射（55 号 §3.3 统读：THD-PLV-001~005，字符串规约语义保持）
_PLV_THRESHOLD_SPEC: Final[dict[str, str]] = {
    "THD-PLV-001": "order_count_deviation",
    "THD-PLV-002": "fill_rate_comparison",
    "THD-PLV-003": "risk_conformance",
    "THD-PLV-004": "data_integrity",
    "THD-PLV-005": "pnl_reconciliation",
}

#: 规约文案（label/description 为代码侧展示语义，阈值才走注册表）
_PLV_TEXT: Final[dict[PLVCheck, tuple[str, str]]] = {
    PLVCheck.ORDER_COUNT_DEVIATION: (
        "Paper vs Live 订单偏差",
        "比较 paper 模拟与 live 实际订单量差异",
    ),
    PLVCheck.FILL_RATE_COMPARISON: (
        "成交率 T+1 vs T-1",
        "比较今天与昨天的 FillRate/Slippage",
    ),
    PLVCheck.RISK_CONFORMANCE: (
        "风控合规",
        "是否所有风险限额均未超限",
    ),
    PLVCheck.DATA_INTEGRITY: (
        "数据完整性校验",
        "核对 MD5/SHA256 checksum 消息完整性",
    ),
    PLVCheck.PNL_RECONCILIATION: (
        "仓位与PnL对账",
        "position + PnL reconciliation 对账阈值",
    ),
}


def build_plv_checks(registry_path: Path | None = None) -> dict[PLVCheck, PLVSpec]:
    """从告警阈值注册表构建 PLV 五项规约（fail-closed；registry_path 为测试逃生门）。

    字符串规约值（"±1%" 等）保持字符串语义加载，不强行数值化（55 号 §3.3 裁定②）。
    """
    thresholds = load_alert_thresholds(_PLV_THRESHOLD_SPEC, registry_path=registry_path, cast="str")
    return {
        check: PLVSpec(
            check=check,
            label=label,
            threshold=thresholds[check.value],
            description=description,
        )
        for check, (label, description) in _PLV_TEXT.items()
    }


#: import 期 fail-closed 构建（注册表缺失/畸形 → import 即 raise，禁止码内第二真源兜底）
PLV_CHECKS: Final[dict[PLVCheck, PLVSpec]] = build_plv_checks()


def get_plv_spec(check: PLVCheck) -> PLVSpec | None:
    return PLV_CHECKS.get(check)


PLV_CHECK_COUNT: Final[int] = 5
