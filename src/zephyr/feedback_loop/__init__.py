"""Feedback Loop Engine (FLE)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一

职责
----
系统自调节的闭环大脑：collect_metric → detect_anomaly → dispatch_action

基础设施
--------
存储      : SQLite 时间序列（2）
           InfluxDB（Phase 4+ 升级）
异常检测  : EMA（指数移动平均）+ 阈值 + 持续时间

关键设计决策（ADR-0019）
-----------------------
FLE 单向依赖 : FLE → 其他服务通过 Protocol 适配器（fire-and-forget），
             防止循环依赖。其他服务只知道 Protocol，不知道 FLE 存在。

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理 + ADR-0019 FLE
架构真源：docs/02_enterprise_architecture/target-architecture/
         vibe-coding-infrastructure-architecture.md §3.5
"""
