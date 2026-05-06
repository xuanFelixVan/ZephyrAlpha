"""L01 Infrastructure
=====================================

14 层量化架构 · L01 基础设施层

职责
----
脚本系统与运行时配置管理：Finding Schema 标准化 + Runtime Config 加载与校验。

子模块
------
- script_system/ : 审计发现 (Finding) Schema 定义与输出格式化
- config.py      : 运行时配置 (AppConfig/RuntimeConfig)

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为生产者（Producer）：
  - CTR-P1-010  SystemConfiguration    → L02~L13（全系统配置分发）

作为消费者（Consumer）：
  - CTR-P1-013  TelemetryEmitter       ← L12（运行状态与配置变更上报）

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

from __future__ import annotations

from zephyr.l01_infrastructure.config import AppConfig, load_config, reload_config
from zephyr.l01_infrastructure.kill_switch_sim import KillSwitchSimulator
from zephyr.l01_infrastructure.script_system.finding import Finding

__all__ = [
    "AppConfig",
    "load_config",
    "reload_config",
    "KillSwitchSimulator",
    "Finding",
]
