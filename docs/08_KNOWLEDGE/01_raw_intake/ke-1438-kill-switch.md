---
module_id: KE-1348
status: active
title: 10.1 Kill Switch 全局熔断
category: module_blueprint
---

# 10.1 Kill Switch 全局熔断

10.1 Kill Switch 全局熔断

```python
class KillSwitch:
    SIGNAL_FILE = ".audit_cache/kill_switch_active"
    ENV_VAR = "ZEPHYR_KILL_SWITCH"

    def is_active(self) -> bool:
        if os.environ.get(self.ENV_VAR, "0") == "1":
            return True
        return os.path.exists(self.SIGNAL_FILE)

    def activate(self, reason: str) -> None:
        with open(self.SIGNAL_FILE, "w") as f:
            f.write(f"{datetime.now().isoformat()}|{reason}\n")

    def deactivate(self) -> None:
        if os.path.exists(self.SIGNAL_FILE):
            os.remove(self.SIGNAL_FILE)
```

触发条件：
- Error Budget Critical 持续 1 小时
- Owner 手动激活（`ZEPHYR_KILL_SWITCH=1` 或创建信号文件）
- 单日成本超限（>$100）
