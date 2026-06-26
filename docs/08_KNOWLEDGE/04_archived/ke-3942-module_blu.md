---
module_id: KE-3790
title: 10.1 已知风险
category: module_blueprint
ttl: permanent
---

# 10.1 已知风险

10.1 已知风险

| 风险 | 可能性 | 影响 | 缓解 |
|------|:--:|------|------|
| 扫描器 CPU/IO 占用过高 | 中 | 影响并行 AI session 的 IDE 性能 | max_workers=8 + 扫描间隔 ≥ 1h + 可选 `--low-priority` 模式 |
| 注册表格式不统一导致对账误报 | 高 | DRIFT 假阳性——耗尽 Owner 注意力 | 对账前先 normalize 所有注册表格式（已知 5 个注册表 entry_count 标记为 `?`） |
| 24 个注册表中部分已损坏（REG-PATHWAY-001 CORRUPTED） | 高 | 对账时读取损坏注册表崩溃 | 每个注册表读取用 try/except——损坏的不阻断，只标记 `registry_skip: [REG-PATHWAY-001]` |
| 资产膨胀到 1500+ 后扫描变慢 | 中 | 从 <30s 膨胀到 >2min | 增量扫描模式——只扫 mtime > last_scan_time 的文件 |
