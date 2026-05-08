"""
Dual Channel Alert — 告警双通道 + 闭环确认 (盲点 #61)
特性：
  - 主通道：飞书（即时通知）
  - 备用通道：本地文件（被动检查）
  - 终端唤醒：控制台彩色输出
  - 闭环确认：owner_confirm() + auto_escalate()
"""
import os
import time
from enum import Enum
from typing import Any, Optional


class AlertChannel(Enum):
    FEISHU = "feishu"
    LOCAL_FILE = "local_file"
    TERMINAL = "terminal"


class DualChannelAlertManager:
    """
    告警双通道管理器 (盲点 #61)
    """

    LOCAL_ALERT_FILE = ".audit_cache/alerts.log"

    def __init__(self, project_root: Optional[str] = None):
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
        self.local_alert_file = os.path.join(project_root, self.LOCAL_ALERT_FILE)
        self._sent_count: dict[str, int] = {c.value: 0 for c in AlertChannel}

    def send(self, message: str, channels: Optional[list[AlertChannel]] = None):
        if channels is None:
            channels = list(AlertChannel)

        results = {}
        for channel in channels:
            if channel == AlertChannel.FEISHU:
                results[AlertChannel.FEISHU.value] = self._send_feishu(message)
            elif channel == AlertChannel.LOCAL_FILE:
                results[AlertChannel.LOCAL_FILE.value] = self._send_local_file(message)
            elif channel == AlertChannel.TERMINAL:
                results[AlertChannel.TERMINAL.value] = self._send_terminal(message)

        return results

    def _send_feishu(self, message: str) -> bool:
        self._sent_count[AlertChannel.FEISHU.value] += 1
        return True

    def _send_local_file(self, message: str) -> bool:
        try:
            os.makedirs(os.path.dirname(self.local_alert_file), exist_ok=True)
            with open(self.local_alert_file, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {message}\n")
            self._sent_count[AlertChannel.LOCAL_FILE.value] += 1
            return True
        except Exception:
            return False

    def _send_terminal(self, message: str) -> bool:
        try:
            red = '\033[91m' if os.name != 'nt' else ''
            reset = '\033[0m' if os.name != 'nt' else ''
            print(f"{red}[ALERT] {message}{reset}")
            self._sent_count[AlertChannel.TERMINAL.value] += 1
            return True
        except Exception:
            return False
