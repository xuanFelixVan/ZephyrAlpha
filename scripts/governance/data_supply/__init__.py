# create-guard-not-dup: 包入口docstring描述供数链交叉核对动作，非第二真源（canonical 各checker职责不同域）
# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/10_wave_plan.md | 波 3.2/3.3/W-102
# [MODULE] scripts.governance.data_supply
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS] scripts.governance.data_supply.check_wave3_rulers; .github/workflows/governance.yml（待登记，见 wave3/registration_needs.yaml）
# [STARTUP] imported
# [MATURITY] testing
# [TTL] permanent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 见各子件头注
# [A_module] module_id=MOD-GOV-DS-PKG | layer=package | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 包声明件，无可执行逻辑
"""Wave-3 data-supply rulers (3.2 false-green cross-check / 3.3 supply conservation / W-102).

Built in the st-final-build-20260926 lane. Everything here is a read-only cross-check:
declarations are derived from existing SSOT hosts (tasks.yaml / data_supply_sentinel.yaml /
known_data_gaps.yaml / ProgressStore), truth is read through the strict ClickHouse channel.
Nothing in this package writes business data.
"""
