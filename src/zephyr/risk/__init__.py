# [A_module] module_id=MOD-UNK-risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""

D_RISK Risk Management
=====================================

域量化架构 · D_RISK 风险管理层

职责
----
实时风控与止损执行：止损计算、头寸校验与风险敞口监控。
上位层 D_PORTFOLIO_CORE（组合构建）的约束提供者。

子模块
------
- stop_loss.py      : 止损兼容层（委托 default_stop_loss_engine）+ kill switch 事件记录
- risk_limits.py    : 风险限额计算器 (RiskLimitsCalculator) — Phase B 骨架已生成
- risk_validator.py : 风险校验器 (RiskValidator) — Phase B 骨架已生成

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-002  FactorSignal              ← D_FACTOR
  - CTR-006  PositionSnapshot          ← D_EXECUTION_CORE
  - CTR-ERR-003  SignalDegradationWarning ← D_SIGNAL
  - CTR-ERR-005  ExecutionRejectionError  ← D_EXECUTION_CORE/D_REPORTING
  - CTR-P1-011  RiskMetricsReport      ← D_PORTFOLIO_CORE
  - CTR-P1-012  ComplianceRule         ← D_COMPLIANCE
  - CTR-P1-013  TelemetryEmitter       ← 遥测
  - CTR-P1-015  SynthesizedSignal      ← D_SIGNAL

作为生产者（Producer）：
  - CTR-003  RiskLimits                  -> D_PORTFOLIO_CORE
  - CTR-ERR-004  RiskLimitViolationError -> D_PORTFOLIO_CORE, D_EXECUTION_CORE
  - CTR-P1-008  RiskDashboardSnapshot    -> D_FRONTEND

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 子模块属性访问请求 字符串
#   fields: 属性名 name（如 "cross_asset"）
#   code: __getattr__(name) L69
# 层: 算法
# - id: A1
#   name_zh: ① 子模块导出清单
#   name_en: __all__
#   intro: 声明本包对外暴露的 6 个风险子模块名
#   desc: __all__ = [cross_asset, risk_limits, risk_manager, risk_manager_base, risk_validator, stop_loss]，仅做符号声明不触发导入
#   inputs: I1
#   outputs: 可导入子模块名单
# - id: A2
#   name_zh: ② 懒加载导入
#   name_en: __getattr__
#   intro: 只有访问 cross_asset 时才真正 import，其他属性名直接报错
#   desc: name=="cross_asset" → importlib.import_module(".cross_asset")；否则 raise AttributeError
#   inputs: I1
#   outputs: 子模块对象
# 层: 输出
# - id: O1
#   name_zh: zephyr.risk 包命名空间
#   name_en: package namespace
#   intro: 风控域包入口，提供止损/风险限额/风险校验等子模块访问
#   downstream: 无下游/内部使用（[CONSUMERS] 头为空，子模块被 D_PORTFOLIO_CORE 等业务域直接 import）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> O1
# A2 --> O1
"""

from __future__ import annotations

import importlib as _importlib
# NOTE(2026-08-25 W1c 协调): 下行由 CAND-RSK-038 并行会话 scaffold 注册, 但其
# atr_stop_engine.py 尚为 stub(无 AtrStopEngine 类), 悬空导入使 zephyr.risk 全包不可导入。
# 按本批 copula 同款协调模式暂注释(可逆, 非删除); 请 CAND-RSK-038 施工方实现类后取消注释恢复。
# W1d(2026-08-25): AtrStopEngine 已落码(MOD-RK-35), 按上方 NOTE 恢复导入。
from zephyr.risk.atr_stop_engine import AtrStopEngine

__all__ = [
    "cross_asset",
    "risk_limits",
    "risk_manager",
    "risk_manager_base",
    "risk_validator",
    "stop_loss",
]


def __getattr__(name):
    if name == "cross_asset":
        return _importlib.import_module(".cross_asset", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# 与上方 NOTE 联动: AtrStopEngine 悬空期间不入 __all__(避免 import * 解析失败)。
# W1d(2026-08-25): 类已落码, 恢复入列。
__all__.append("AtrStopEngine")
