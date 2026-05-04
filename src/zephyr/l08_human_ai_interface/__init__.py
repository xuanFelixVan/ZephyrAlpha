"""L08 Human-AI Interface
=====================================

14 层量化架构 · L08 人机交互层

职责
----
人机交互与监控面板：Streamlit Dashboard、告警通知与可视化展现。
消费 feedback_loop/fitness_functions.py（Facade 模式封装为展示组件）。

子模块
------
- dashboard/ : Streamlit 监控面板 (app.py + components/)

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""
