# [A_module] module_id=MOD-UNK_frontend | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain-frontend/hmi-core/blueprint.md
# [MODULE] zephyr.frontend
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

"""D_FRONTEND Human-AI Interface
=====================================

域量化架构 · D_FRONTEND 人机交互层

职责
----
人机交互与监控面板：Streamlit Dashboard、告警通知与可视化展现。
消费 feedback-loop/fitness_functions.py（Facade 模式封装为展示组件）。

子模块
------
- dashboard/ : Streamlit 监控面板 (app.py + components/)

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-P1-008  RiskDashboardSnapshot      ← D_RISK
  - CTR-P1-009  PerformanceAttributionReport ← D_REPORTING

外部系统边界：
  - EXT-004  Feishu / 飞书通知接口（输出：Webhook 通知）

作为全局配置消费者（Consumer）：
  - CTR-P1-010  SystemConfiguration    ← 基础设施

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

__all__ = ["interface_base"]
