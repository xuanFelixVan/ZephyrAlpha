---
module_id: KE-2905
status: active
title: Sleep-Time Protocol（睡眠时段协议）
category: module_blueprint
---

# Sleep-Time Protocol（睡眠时段协议）

Sleep-Time Protocol（睡眠时段协议）

```python
class SleepTimeProtocol:
    """Owner 睡眠时段自动管理——数据驱动的静音窗口。
    假设：23:00-07:00 local = Owner 正在睡觉。
    """
    _sleep_start: int = 23    # 23:00
    _sleep_end: int = 7       # 07:00
    _critical_suppressed: int = 0

    def is_sleep_time(self) -> bool:
        """判断当前是否在睡眠时段"""
        hour = datetime.now(tz=self._owner_tz).hour
        return hour >= self._sleep_start or hour < self._sleep_end

    async def handle_alert(self, alert: Alert) -> AlertDecision:
        """睡眠时段：CRITICAL 只触发一次→5min内无Owner响应→走自愈"""
        if not self.is_sleep_time():
            return AlertDecision.SEND_NORMAL

        if alert.level == AlertLevel.CRITICAL:
            if self._critical_suppressed >= 1:  # 已发过一次
                return AlertDecision.AUTO_HEAL  # 直接自愈
            self._critical_suppressed += 1
            return AlertDecision.SEND_SINGLE    # 只发一条

        return AlertDecision.QUEUE_FOR_MORNING  # 其余→早上推送
```
