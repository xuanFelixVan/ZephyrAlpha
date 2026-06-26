---
module_id: KE-2030
status: active
title: 3.1 #26: StartupGuard (M-31)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 #26: StartupGuard (M-31)

3.1 #26: StartupGuard (M-31)

文件：`D:\ZephyrAlpha\src\\zephyr\\shared\\startup_guard.py`

实现 `StartupGuard` 类（蓝图 L2728-2814）：
- `load_order.yaml`：声明 capacity-assurance 应在其他27个模块之前加载
- `mark_bootstrapping_start()` / `mark_bootstrapping_end()`：启动完成标记
- `check_module_protection(module_id) -> bool`：启动过程中其他模块调用ca → 返回CODE_RED（暂停调用直到ca完成启动）
- boot_SLO: "自启动起 SLO 达标时间 ≤ 30s"，Burn Rate × 2 权重
