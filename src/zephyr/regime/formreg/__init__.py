# [BLUEPRINT] MOD-REGIME-017 | 待统筹登记（CONDAXIS-CAMPAIGN 两态线 formreg 包；挖矿真源 docs/_working/condaxis/formreg/）
# [MODULE] zephyr.regime.formreg
# [DOMAIN] D_REGIME
# [TTL] permanent
# [A_module] module_id=PKG-regime-formreg | layer=package | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""D_REGIME 域 formreg 包 — 大盘两态形态识别线隔离方法实现（P2 车道 st-cdx-formreg-20261013）。

四件套（裁定#229 反转未裁——冻结面：禁 TDM 挂接/消费面接线/词表登记）：
    ps_chronology   P-S 牛熊年代学纯函数核（环节[2]规则层，离线真值段）
    jump_layer      jumpmodels 两态封装（环节[2]概率层，持久态+后验，锚定重排）
    cusum_two_sided 双边 CUSUM 拐点检测（环节[4]，单边先例对称扩展）
    bocpd_online    BOCPD 在线变点检测（AM2007 Student-t，p(r_t=0) 拐点灰度）

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/__init__.yaml
"""

from typing import Final

from zephyr.regime.formreg.bocpd_online import BOCPDParams, BOCPDResult, run_bocpd
from zephyr.regime.formreg.cusum_two_sided import (
    CusumTwoSidedParams,
    CusumTwoSidedResult,
    detect_turning_events,
)
from zephyr.regime.formreg.jump_layer import (
    TWO_STATE_SLOTS,
    TwoStateJumpLayer,
    anchored_two_state_order,
)
from zephyr.regime.formreg.ps_chronology import PSParams, build_chronology, to_monthly

__all__: Final = [
    "PSParams",
    "build_chronology",
    "to_monthly",
    "TWO_STATE_SLOTS",
    "TwoStateJumpLayer",
    "anchored_two_state_order",
    "CusumTwoSidedParams",
    "CusumTwoSidedResult",
    "detect_turning_events",
    "BOCPDParams",
    "BOCPDResult",
    "run_bocpd",
]
