# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | 矩阵考试战役批0-5
# [MODULE] scripts.backtest.fexam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.factor.core.evaluation.metrics（IC内核复用）; zephyr.backtest.implementations.vectorized_engine（批2引擎复用）; zephyr.backtest.core.n_trial_ledger（DSR记账复用）
# [CONSUMERS] run_fexam.py CLI; Owner 晨报
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 四类资产全量考（策略161/因子全量/指标全量/分配器5套）；HOLDOUT选样窗与考试窗分离；verdict三态 pass/rework/retire_candidate；负结果如实入册；registry只读不回写（回写另行批）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单对象失败不阻断批；CH不可达=fail-closed报错不伪造分数
# [TESTS] tests/backtest/fexam/
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（改判据/窗口先改 roster.PREREG_V1）
# [TTL] permanent
# create-guard-not-dup: 注册表驱动考试套件包入口，无既有能力等价物（命中的'注册表驱动'为泛词）
"""fexam — 注册表驱动的全量考试套件（矩阵战役批0-5）。

批0 roster（四册机生应考名单）→ 批1因子IC考 → 批2策略整装考 → 批3指标IC考
→ 批4分配器影子考 → 批5总册+家底总表+缺口单+原问题匹配。
"""
