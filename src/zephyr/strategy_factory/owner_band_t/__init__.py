# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_band_t
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.backtest.core.cost_model_calibration; zephyr.backtest.core.matching_logic; zephyr.infrastructure.database_service
# [CONSUMERS] scripts/strategy_factory/run_s_owner_001_exam.py（E4 考试入口）; tests/strategy_factory/
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 策略卡 S-OWNER-001 规则转译唯一实现位点；TD 序列自实现纯 pandas 零新依赖；成本全走 H2 真源（零费率字面量）；信号 ≤t 判定、t+1 开盘成交（PIT 铁律）；做T 额度=前收盘持仓（T+1 结构）
# [MODIFY-GUARD] 考试冻结文档 docs/_working/factory/strategy_cards/e4_freeze_s_owner_001_300etf_band_t.md——冻结后本件规则语义变更=第二真源作弊
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(非法配置/数据缺失)； RuntimeError(regime 快照 run 不存在)
# [TESTS] tests/strategy_factory/test_s_owner_001_td_sequence.py; tests/strategy_factory/test_s_owner_001_engine.py; tests/strategy_factory/test_s_owner_001_costs.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""S-OWNER-001「震荡期 300ETF 波段+底仓T」策略模块（策略卡转译，E4 考试对象）。

结构：
  td_sequence   TD 序列自实现（Buy Setup/Countdown + TD 极值，纯 pandas）
  signals       波段信号面（布林上轨/前高/涨幅分位/波动率分位）
  regime_gate   regime 门（读 c1_backtest.regime_snapshot_history，翻转次日生效）
  costs         H2 真成本全套封装（佣金/标定滑点/AC 冲击/做T 加成）
  data_loader   000300 指数日线 + 510300 ETF 小时线（DatabaseService 只读 + 本地 parquet cache）
  intraday_t    日内做T 臂（日回转额度=T+1 结构约束）
  engine        波段+做T 组合引擎（金字塔三档/镜像三档减仓/回撤熔断）
  exam          E4 考试器（IS 网格全记录 + OOS 单次三臂归因）
"""

__all__: list[str] = ["costs", "data_loader", "engine", "exam", "intraday_t", "regime_gate", "signals", "td_sequence"]
