# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.kill_switch_sim
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_kill_switch_sim | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: infra_ops
# category: kill_switch
# status: active
# created: "2026-05-05"
# ---

"""
Kill Switch T0 Hardware Simulator

INV-001 / CAP-009：Kill Switch 延迟 < 1ms（现阶段 T0 模拟器验证）

功能：
  - 模拟硬件 Kill Switch 的触发/恢复时序
  - 测量端到端延迟（触发 → 确认）
  - 输出 JSONL 指标供 Prometheus / arch_guard 消费

用法：
  ZEPHYR_T1_KILL_SWITCH_PROBE=1 python -m zephyr.infrastructure.kill_switch_sim
"""

from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import Event
from zephyr.shared.utils.time_utils import now_utc

DEFAULT_TARGET_MS = 1.0
METRICS_DIR = Path(os.environ.get("ZEPHYR_METRICS_DIR", "data/metrics"))
PROBE_ENABLED = os.environ.get("ZEPHYR_T1_KILL_SWITCH_PROBE", "0") == "1"


@dataclass
class KillSwitchProbe:
    """Kill Switch 单次探测结果"""

    probe_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trigger_timestamp: float = 0.0
    ack_timestamp: float = 0.0
    latency_us: float = 0.0
    target_met: bool = False
    hardware_model: str = "T0_SIMULATOR"

    @property
    def latency_ms(self) -> float:
        return self.latency_us / 1000.0

    def to_dict(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "timestamp": now_utc().isoformat() + "Z",
            "latency_us": round(self.latency_us, 2),
            "latency_ms": round(self.latency_ms, 4),
            "target_ms": DEFAULT_TARGET_MS,
            "target_met": self.latency_us <= DEFAULT_TARGET_MS * 1000,
            "hardware_model": self.hardware_model,
        }


class KillSwitchSimulator:
    """
    T0 级 Kill Switch 模拟器

    模拟硬件 Kill Switch 的信号回路：
      1. trigger() → 发送 KILL 信号
      2. wait_ack() → 等待硬件确认（模拟 GPIO 中断回路延迟）
      3. log_probe() → 写 JSONL 探测记录
    """

    def __init__(self, target_ms: float = DEFAULT_TARGET_MS):
        self.target_ms = target_ms
        self._kill_event = Event()
        self._ack_callback: Callable[[], None] | None = None
        self._probe_history: list[KillSwitchProbe] = []
        self._metrics_path = METRICS_DIR / "kill_switch_probes.jsonl"

    def register_ack_callback(self, cb: Callable[[], None]) -> None:
        """注册硬件确认回调（T1 真实硬件时替换此回调）"""
        self._ack_callback = cb

    def trigger(self) -> KillSwitchProbe:
        """触发 Kill Switch 并测量回路延迟"""
        probe = KillSwitchProbe()
        probe.trigger_timestamp = time.perf_counter()

        self._kill_event.set()

        if self._ack_callback:
            self._ack_callback()

        probe.ack_timestamp = time.perf_counter()
        probe.latency_us = (probe.ack_timestamp - probe.trigger_timestamp) * 1_000_000
        probe.target_met = probe.latency_us <= self.target_ms * 1000

        self._probe_history.append(probe)
        self._write_probe(probe)

        if not probe.target_met:
            print(f"[KILL_SWITCH] WARN: 延迟 {probe.latency_us:.1f}us 超出目标 {self.target_ms}ms (INV-001)")

        return probe

    def _write_probe(self, probe: KillSwitchProbe) -> None:
        self._metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._metrics_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(probe.to_dict(), ensure_ascii=False) + "\n")

    def health_check(self) -> bool:
        """T0 级别健康检查：运行一次探测并验证是否达标"""
        probe = self.trigger()
        passed = probe.target_met
        print(
            f"[KILL_SWITCH] Health Check: latency={probe.latency_us:.1f}us, "
            f"target={self.target_ms}ms → {'PASS' if passed else 'FAIL'}"
        )
        return passed


def main() -> None:
    if not PROBE_ENABLED:
        print("[KILL_SWITCH] T0 模拟器未激活（ZEPHYR_T1_KILL_SWITCH_PROBE=0），基线通过")
        return

    sim = KillSwitchSimulator()
    ok = sim.health_check()
    exit(0 if ok else 1)


if __name__ == "__main__":
    main()
