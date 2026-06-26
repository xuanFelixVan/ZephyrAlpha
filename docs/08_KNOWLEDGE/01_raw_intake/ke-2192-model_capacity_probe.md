---
module_id: KE-2099
status: active
title: 3.3 #57: ModelCapacityProbe (M-44)
category: module_blueprint
ttl: permanent
---

# 3.3 #57: ModelCapacityProbe (M-44)

3.3 #57: ModelCapacityProbe (M-44)

文件：`D:\ZephyrAlpha\src\zephyr\shared\model_capacity_probe.py`

- 标准化金丝雀任务："实现一个函数 add(a: int, b: int) -> int"
- `probe_all_active_models()`: 每天07:00对所有活跃模型发送
- 对比昨天：延迟漂移 / Token产出漂移（>30%）/ 代码行数漂移（>50%）
- 自动更新 profile（指数平滑）
