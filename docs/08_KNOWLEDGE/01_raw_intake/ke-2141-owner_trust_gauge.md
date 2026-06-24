---
module_id: KE-2049
status: active
title: 3.10 #64: OwnerTrustGauge (M-46)
category: module_blueprint
---

# 3.10 #64: OwnerTrustGauge (M-46)

3.10 #64: OwnerTrustGauge (M-46)

文件：`D:\ZephyrAlpha\src\zephyr\shared\owner_trust_gauge.py`

- 三指标：alert_response_time / manual_override_rate / alert_dismissal_rate
- dismissal_rate>30%→CRITICALLY_LOW / response_time>30min→COMPLACENT
- `weekly_gauge()`: 输出信任水平+建议
