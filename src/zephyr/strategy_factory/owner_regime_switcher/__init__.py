# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.backtest.core.cost_model_calibration; zephyr.backtest.core.matching_logic; zephyr.infrastructure.database_service
# [CONSUMERS] scripts/strategy_factory/run_s_owner_002_exam.py（E4 考试入口）; tests/strategy_factory/
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 策略卡 S-OWNER-002 规则转译唯一实现位点（框架验证级，代理包非可毕业策略）；切换器只做"包集合+上限系数"调度不做选股；状态映射/滞后带/置信门/失败安全全参数化；信号 ≤t 判定、t+1 开盘成交（PIT 铁律）；成本全走真源零费率字面量
# [MODIFY-GUARD] 考试冻结文档 docs/_working/factory/strategy_cards/e4_freeze_s_owner_002_regime_switcher.md——冻结后本件规则语义变更=第二真源作弊
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(非法配置)； RuntimeError(regime 快照空/数据缺失)
# [TESTS] tests/strategy_factory/test_s_owner_002_switcher.py; tests/strategy_factory/test_s_owner_002_engine.py; tests/strategy_factory/test_s_owner_002_redblue.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""S-OWNER-002「regime→策略包切换器」框架验证模块（策略卡转译，E4 考试对象）。

结构：
  switcher     切换器核心：状态集映射→(启用包集合, 上限系数)；滞后带 N 日防抖；
               置信门；检测器不可用失败安全（退全时全包×保守系数）
  packages     两个代理包信号面：包 A=300ETF 均线波段（防御）；包 B=篮子动量轮动（进攻）
  costs        成本真源封装（佣金+标定滑点+冲击，单边计费，ETF 免印花）
  data_loader  ETF 60min 聚合日线 + regime 快照（DatabaseService 只读 + .runtime/tmp cache）
  engine       组合引擎：同一代理池在"启用集合+上限"调度下逐日盯市（T+1、整数手）
  exam         E4 考试器：on/off 双跑对照 + 敞口匹配对照 + block bootstrap CI + 检测器质量描述表
"""

# re-export 考试器=包公开 API 面（唯一入口 scripts/run_s_owner_002_exam.py 消费；
# ORPHAN-MODULE 扫描口径=src/** 内部互引，scripts 消费不可见，此 re-export 即真实语义声明）
from zephyr.strategy_factory.owner_regime_switcher import exam  # noqa: F401,E402

__all__: list[str] = ["costs", "data_loader", "engine", "exam", "packages", "switcher"]
