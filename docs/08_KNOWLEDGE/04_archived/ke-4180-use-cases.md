---
module_id: KE-4024------use-000
title: 2b. 资源层 USE 信号
category: module_blueprint
---

# 2b. 资源层 USE 信号

2b. 资源层 USE 信号

> 对标 Netflix/Google SRE USE Method（Utilization / Saturation / Errors）。覆盖 4 Golden Signals 达不到的资源层盲区。对 AI 生成代码场景尤其重要——内存泄漏、文件句柄泄漏只有这一层能发现。

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| **Utilization**（利用率） | CPU 使用率 / 内存占用 / 磁盘使用率 / GPU 利用率 | psutil / OS metrics / nvidia-smi | CPU > 80% 持续 5min → FLE 告警 |
| **Saturation**（饱和） | 磁盘 IO 队列深度 / 网络连接数 / 文件句柄数 / 进程数 | OS metrics / /proc / iostat | 文件句柄 > 800 → 泄漏预警 |
| **Errors**（资源错误） | OOM Kill / 磁盘满 / 网络不可达 / GPU OOM | OS events / dmesg / kernel log | 任意硬件级错误 → P0 立即通知 |

---
