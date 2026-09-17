---
ttl: task_bound
---

# QMT 文件桥模拟盘 100 股端到端取证（flash-nightbuild-20260918）

```
[1] broker_id=qmt_sim env=sim
[2] connect()=True
[3] submit_order -> flash-nightbuild-e2e-20260918-01
[4] query_order status=SUBMITTED
[5] cancel_order -> True
[6] orders_file=E:\qmt_bridge_sim\orders_sim.csv lines=5
```

== orders_sim.csv 尾 4 行 ==

```
bridge-smoke-c3-20260918,order,600000.SH,buy,100,limit,8.1
Clocal-bridge-c3-001,cancel,local-bridge-c3-001,,0,,0.0
flash-nightbuild-e2e-20260918-01,order,510300.SH,buy,100,limit,4.07
Cflash-nightbuild-e2e-20260918-01,cancel,flash-nightbuild-e2e-20260918-01,,0,,0.0
```
