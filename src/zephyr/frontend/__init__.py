# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Python 包导入请求
#   fields: 无数据字段（解释器 import 机制触发，不读任何数据表）
#   code: import zephyr.frontend
# 层: 算法
# - id: A1
#   name_zh: ① 模块命名空间声明
#   name_en: zephyr.frontend.__init__
#   intro: MOD-L08-001 包入口
#   desc: MOD-L08-001 包入口，模块命名空间声明并声明 __all__（1项）
#   inputs: I1
#   outputs: zephyr.frontend 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（1项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.frontend 包公共 API
#   name_en: __all__ 1项
#   intro: MOD-L08-001 包入口——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
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
人机交互与监控面板：Panel Dashboard（v3.0.0 #ARCH-047 起替代 Streamlit）、告警通知与可视化展现。
消费 feedback-loop/fitness_functions.py（Facade 模式封装为展示组件）。

子模块
------
- dashboard/ : Panel 监控面板 (app_panel.py + components/)

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
