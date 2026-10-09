# [BLUEPRINT] MOD-DATSEC-001 | docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md | §F128 接线复活
# [MODULE] zephyr.data_security.wiring
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] zephyr.data_security.ai_masking_pipeline；zephyr.data_security.data_access_auditor；zephyr.data_security.data_masking_engine
# [CONSUMERS] zephyr.frontend.dashboard.api_server（数据出口挂载）；LLM 调用面装配点（LSG l1 前置）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 零侵入（不改 LSGSecurityGateway 与各出口端点数据生产逻辑一行——组合/边界挂载）；
#   出厂角色/缺省 purpose=现行为保持（dashboard_local 全 none、L1 放行）；翻转=Owner 配置门位
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS] tests/data_security/test_wiring_lsg_masking_front.py；tests/data_security/test_wiring_data_exit_guard.py；tests/data_security/test_wiring_audit_sink.py
# [A_module] module_id=MOD-DATSEC-WIRING | layer=package | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""F128 data_security 接线复活包（st-menu-t1b2-20260930，Owner 2026-09-30 夜批）。

三实体接线（known-gap→接线复活，撤销 794f16569b 的包级 [DEPRECATED]）：
  接点① LSG l1 前置 = lsg_masking_front.LSGMaskingFront（AiMaskingPipeline 消费者）
  接点② 数据出口   = data_exit_guard.DataExitGuard（DataMaskingEngine+DataAccessAuditor 消费者）
  审计统一落盘     = audit_sink.JsonlAuditSink（F128 缺口②真源=规则册 audit.jsonl_sink）
规则册真源 = config/data_masking_policy.yaml（缺口①落位）。

# [ALGO_FLOW] external: docs/03_modules/_domain_data_security/algo_flow/wiring__init__.yaml
"""

from typing import Final

from zephyr.data_security.wiring.audit_sink import DEFAULT_SINK_RELPATH, JsonlAuditSink
from zephyr.data_security.wiring.data_exit_guard import (
    MASK_KIND_VOCABULARY,
    RULEBOOK_RELPATH,
    DataExitGuard,
    load_rulebook,
)
from zephyr.data_security.wiring.lsg_masking_front import LSGMaskingFront

__all__: Final = [
    "DEFAULT_SINK_RELPATH",
    "DataExitGuard",
    "JsonlAuditSink",
    "LSGMaskingFront",
    "MASK_KIND_VOCABULARY",
    "RULEBOOK_RELPATH",
    "load_rulebook",
]
