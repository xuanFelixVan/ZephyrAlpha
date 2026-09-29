# [BLUEPRINT] MOD-GOV-CONSUMPTIONCENSUS
# [MODULE] zephyr.governance.consumption
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.consumption.scan_scope_converged; zephyr.governance.consumption.consumption_census; zephyr.governance.consumption.consumption_census_reconciler
# [CONSUMERS] zephyr.governance.indicator_usage_audit; zephyr.governance.audit.library_new_module_reconciler; scripts.governance.d3_metadata.generate_wiring_registry; scripts.governance.d5_architecture.generators.generate_connection_matrix
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 包内三件＝波 13 消费面自动化件（单一扫描口径 / 九族普查引擎 / 事件触发对账器）；
#              包根零判定逻辑（纯命名空间，禁在本 __init__ 里再派生任何口径常量或谓词）；
#              本包是 CREATE-GUARD「governance/ 根禁新增 .py」的落位（ARCH-031 防复发）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无逻辑故无契约——导入失败=子模块自身契约生效
# [TESTS] tests/governance/test_consumption_census_redproof.py; tests/governance/test_scan_scope_convergence_equivalence.py
# [A_module] module_id=MOD-GOV-CONSUMPTIONCENSUS | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: 包根纯命名空间零判定逻辑，与死信所列 reconciler/dashboard/checker 零功能交集——命中词「自动化件的包」纯系本 docstring 措辞碰撞（q-20260928-st-zcloseout-20260926-0001 死信处方）
"""governance.consumption — 消费面（有没有人真用）自动化件的包。

大白话：一个资产登记在册不等于有人用它。本包放"怎么算有人用"这一把尺
（scan_scope_converged）、按这把尺扫全仓的普查引擎（consumption_census）、
以及落地后自动重跑并点名新孤岛的事件触发对账器（consumption_census_reconciler）。

本 __init__ 只做命名空间，不做再导出（re-export 会造出第二条导入路径＝第二真源风险）；
消费者请直连子模块全路径。

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/consumption/consumption__init__.yaml
"""

__all__: list[str] = []
