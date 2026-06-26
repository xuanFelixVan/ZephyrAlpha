---
module_id: KE-1238
status: active
title: Trae 假死 / 卡住
category: governance
ttl: permanent
---

# Trae 假死 / 卡住

Trae 假死 / 卡住

1. 等待 30 秒——Trae 在执行批量操作时可能出现短暂无响应
2. 如果 30 秒后仍未恢复：强制终止 Trae 进程
3. 重启 Trae 后：运行编码扫描确认无残留损坏文件
4. 记录到 Session Log：标注"TRAE-HANG-YYYYMMDD"，明确标注假死时正在执行的任务
