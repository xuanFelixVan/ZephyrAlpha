# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_limits
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.risk_limits
# [CONSUMERS] zephyr.trading.trading_contracts.factories(make_risk_limits); zephyr.ex_core.premarket_checker(RiskLimitsProbe 类型); zephyr.trading.trading_contracts.risk.__init__ 再导出
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim; canonical implementation at zephyr.shared.contracts.risk_limits（CTR-003 登记真源，cross_layer_contracts.yaml physical_path）；本文件原为 2026-05-19 批量导入的出生自带 CODGEN 标记副本（零管线背书零校验覆盖），B3 治本 2026-09-05 降级
# [MODIFY-GUARD] cross_layer_contracts.yaml CTR-003; scripts/governance/d5_architecture/generators/generate_contracts.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if zephyr.shared.contracts.risk_limits unavailable
# [TESTS] tests/ex_core/test_premarket_checker.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
risk_limits — re-export shim for zephyr.shared.contracts.risk_limits（CTR-003 真源）。

治本（长城审计 B3，2026-09-05）：本文件与真源曾构成双 codegen 真源——两者类体逐字
相同（RiskLimits 10 字段），但真源唯一性登记三处同向（cross_layer_contracts.yaml
CTR-003 physical_path / freeze_manifest.yaml / G6-C03 规则），本路径从未进入任何契约
登记（git -S 零命中），原 CODGEN 标记系批量导入出生自带、零生成管线背书零校验器
覆盖。双类并存导致 isinstance 跨路径失效风险（factories 构造本类 vs risk_manager
等 15 消费方使用真源类）。

收敛裁定（沿 A13 semantic_audit shim 先例，commit 2b0610aa3f 范式）：
- 唯一实现真源 = zephyr.shared.contracts.risk_limits（CTR-003）
- 本文件降级为 re-export shim，保留导入路径兼容（trading_contracts 聚合导出面不变）
- 消费方（factories/premarket_checker）改直接 import 真源
"""

from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: F401

__all__ = ["RiskLimits"]
