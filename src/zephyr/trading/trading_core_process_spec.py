# [BLUEPRINT] MOD-INF-064 | docs/03_modules/_domain_infrastructure_runtime/trading_core_process/blueprint.md | §
# [MODULE] zephyr.trading.trading_core_process_spec
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.redis_state_layer_ssot
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] P3 进程规格唯一真源=A9 运维架构 §1.1/§2.2; 畸形规格 Fail-Closed; HC-01 任何时段不自动重启不可放宽; 配置就绪件仅声明不执行
# [MODIFY-GUARD] tests/trading/test_trading_core_process_spec.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TradingCoreSpecError(未登记错误码-申请中)
# [TESTS] tests/trading/test_trading_core_process_spec.py
# [A_module] module_id=MOD-INF-064 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P3 交易核心进程规格 SSOT（MOD-INF-064）——trading_core 独立进程参数唯一真源。

真源：A9 运维架构 §1.1 进程矩阵（P3 行）+ §2.2 Hot 平面资源表 + CAND-H1FS-003（B14-04524）。

职责边界：交易运行时散件（MOD-INF-035 auto_runtime_core / 订单 / 执行）不变；
本模块只收口 P3 独立进程规格声明：
  - 四职责：风控检查 / 订单构建 / miniQMT 下单 / 持仓同步
  - 核 8-11 独占绑定（避免其他进程 CPU 抖动）
  - 内存 8GB 峰值上限 + 禁止 swap（避免 GC 停顿与页面换入）
  - 风控 NN 常驻显存 2GB（GPU OOM 紧急卸载时保留不卸载）
  - 分级心跳 hb:trading_core 2s/10s（TTL=超时+30s 缓冲，规则复用 MOD-INF-063）
  - HC-01：任何时段不自动重启，仅告警 + 人工介入（不可降级）

硬边界：核亲和（SetProcessAffinityMask）/ 禁 swap / 显存常驻等系统级设置
属 Owner 窗口，本模块只产出配置声明，AI 不执行。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from zephyr.infrastructure.redis_state_layer_ssot import get_namespace

__all__: Final = [
    "TRADING_CORE_SPEC",
    "TradingCoreProcessSpec",
    "TradingCoreSpecError",
    "heartbeat_key",
    "heartbeat_ttl_seconds",
    "render_process_spec_declaration",
]


class TradingCoreSpecError(RuntimeError):
    """P3 进程规格畸形或 HC-01 放宽尝试（Fail-Closed）。"""


@dataclass(frozen=True)
class TradingCoreProcessSpec:
    """P3 trading_core 进程规格（A9 §1.1/§2.2 唯一真源，frozen 不可变）。

    HC-01 约束：hc01_no_auto_restart=True 时 restart_policy 必须为
    "alert_only_always"——任何时段不自动重启，仅告警 + 人工介入。
    """

    process_id: str = "P3"
    process_name: str = "trading_core"
    priority: int = 15  # 数值越小优先级越高（A9 §1.1）
    duties: tuple[str, ...] = ("风控检查", "订单构建", "miniQMT下单", "持仓同步")
    cpu_cores: tuple[int, ...] = (8, 9, 10, 11)
    cpu_exclusive: bool = True
    memory_budget_gb: int = 8
    swap_forbidden: bool = True
    risk_nn_vram_gb: int = 2
    heartbeat_interval_s: int = 2
    heartbeat_timeout_s: int = 10
    hc01_no_auto_restart: bool = True
    restart_policy: str = "alert_only_always"

    def __post_init__(self) -> None:
        if not self.duties:
            raise TradingCoreSpecError("P3 职责列表为空（四职责缺项属畸形规格）")
        if self.heartbeat_interval_s >= self.heartbeat_timeout_s:
            raise TradingCoreSpecError(
                f"心跳间隔 {self.heartbeat_interval_s}s 必须小于超时 {self.heartbeat_timeout_s}s"
            )
        if len(set(self.cpu_cores)) != len(self.cpu_cores):
            raise TradingCoreSpecError(f"CPU 核号重复: {self.cpu_cores}")
        if any(core < 0 for core in self.cpu_cores):
            raise TradingCoreSpecError(f"CPU 核号越界: {self.cpu_cores}")
        if self.memory_budget_gb <= 0:
            raise TradingCoreSpecError(f"内存预算非正: {self.memory_budget_gb}GB")
        if self.hc01_no_auto_restart and self.restart_policy != "alert_only_always":
            raise TradingCoreSpecError(
                "HC-01 不可放宽：hc01_no_auto_restart=True 时 restart_policy 必须 "
                f"alert_only_always（收到 {self.restart_policy!r}）"
            )


TRADING_CORE_SPEC: Final[TradingCoreProcessSpec] = TradingCoreProcessSpec()


def heartbeat_key() -> str:
    """P3 心跳键：hb:trading_core（A9 §1.1.3）。"""
    return f"hb:{TRADING_CORE_SPEC.process_name}"


def heartbeat_ttl_seconds() -> int:
    """P3 心跳 TTL = 超时阈值 + 30s 缓冲（规则复用 MOD-INF-063 hb dynamic_ttl，不重造）。"""
    hb_spec = get_namespace("hb")
    assert hb_spec.dynamic_ttl is not None  # MOD-INF-063 一致性自检保证
    return hb_spec.dynamic_ttl(TRADING_CORE_SPEC.heartbeat_timeout_s)


def render_process_spec_declaration() -> dict[str, object]:
    """产出 P3 进程配置就绪件声明 dict（YAML 可序列化；仅声明不执行）。

    硬边界：核亲和/禁 swap/显存常驻等系统级应用属 Owner 窗口（applied_by_ai=False）。
    """
    spec = TRADING_CORE_SPEC
    return {
        "process_id": spec.process_id,
        "process_name": spec.process_name,
        "priority": spec.priority,
        "duties": list(spec.duties),
        "cpu": {
            "cores": list(spec.cpu_cores),
            "exclusive": spec.cpu_exclusive,
        },
        "memory": {
            "budget_gb": spec.memory_budget_gb,
            "swap_forbidden": spec.swap_forbidden,
        },
        "gpu": {"risk_nn_vram_gb": spec.risk_nn_vram_gb},
        "heartbeat": {
            "key": heartbeat_key(),
            "interval_s": spec.heartbeat_interval_s,
            "timeout_s": spec.heartbeat_timeout_s,
            "ttl_seconds": heartbeat_ttl_seconds(),
        },
        "restart_policy": spec.restart_policy,
        "hc01_no_auto_restart": spec.hc01_no_auto_restart,
        "applied_by_ai": False,
        "apply_boundary": "核亲和/禁 swap/显存常驻等系统级设置属 Owner 窗口执行，本声明仅供审阅应用",
    }
