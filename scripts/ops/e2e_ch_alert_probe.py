#!/usr/bin/env python
# [TTL] task_bound
"""R5 端到端告警验证脚本（#ARCH-DR-CH-RESTART-001）。

启动一个 HeartbeatMonitor + Alerter 探针，指向真实 CH。
运行 90 秒，期间人工停止/启动 CH，验证：
- CH 停止后 ~6-9s 触发 CRITICAL 告警（写 failures/ 文件）
- CH 恢复后触发 INFO 恢复通知

用法：
  1. 启动本脚本（后台运行，输出到 stdout）
  2. 在另一个终端：python scripts/backup/ch_vm_ssh.py --sudo --cmd "sudo systemctl stop clickhouse-server"
  3. 等待 ~10s 看到 CRITICAL 告警
  4. python scripts/backup/ch_vm_ssh.py --sudo --cmd "sudo systemctl start clickhouse-server"
  5. 等待 ~10s 看到 INFO 恢复
  6. 脚本 90s 后自动退出
"""

from __future__ import annotations

import logging
import time

from zephyr.data.alerter import Alerter
from zephyr.data.redundant_source.heartbeat_monitor import HeartbeatMonitor, SourceState

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("e2e_ch_alert")


class TrackingAlerter(Alerter):
    """Alerter 子类，打印每次 notify 调用到 stdout（便于人工观察）。"""

    def notify(self, task_id, error, level="ERROR", source=None, extra=None):
        print(f"\n{'=' * 60}", flush=True)
        print(f"[ALERT FIRED] level={level} task={task_id} source={source}", flush=True)
        print(f"  error: {error}", flush=True)
        print(f"{'=' * 60}\n", flush=True)
        return super().notify(task_id, error, level, source, extra)


def real_ch_ping() -> bool:
    """真实 CH ping（SELECT 1 via ch_writer）。"""
    try:
        from zephyr.data import ch_writer

        result = ch_writer.health_check()
        return result.get("tcp") == "ok"
    except Exception as e:
        log.warning("CH ping 异常: %s", e)
        return False


def main() -> None:
    alerter = TrackingAlerter()
    monitor = HeartbeatMonitor(
        ch_ping_interval=3.0,  # 3 秒一次（加速测试）
        ch_fail_threshold=2,  # 连续 2 次失败即告警（~6s）
        ch_ping_fn=real_ch_ping,
        alerter=alerter,
    )
    monitor.start()
    log.info("R5 端到端告警探针已启动（90s 后自动退出）。现在请停止/启动 CH 验证告警触发。")

    prev_state = SourceState.UNKNOWN
    deadline = time.time() + 90
    while time.time() < deadline:
        status = monitor.get_status()
        if status.ch_state != prev_state:
            log.info("CH 状态变化: %s -> %s", prev_state.value, status.ch_state.value)
            prev_state = status.ch_state
        time.sleep(1)

    monitor.stop()
    log.info("探针已停止。检查 data/failures/ 目录确认告警文件已写入。")


if __name__ == "__main__":
    main()
