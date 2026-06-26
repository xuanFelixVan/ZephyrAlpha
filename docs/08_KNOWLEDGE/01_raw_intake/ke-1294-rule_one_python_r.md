---
module_id: KE-1207--------------r-003
status: active
title: 🔴 RULE-ONE：Python 脚本并发写入安全规范（与 RULE-ZERO 同级）
category: governance_rule
ttl: permanent
---

# 🔴 RULE-ONE：Python 脚本并发写入安全规范（与 RULE-ZERO 同级）

🔴 RULE-ONE：Python 脚本并发写入安全规范（与 RULE-ZERO 同级）

**背景**：Windows 上多个 Python 进程同时对同一目录执行文件创建/写入时，Windows Defender 实时扫描 + NTFS 目录元数据锁会造成**进程级排队阻塞**——后来的进程被挂起等待，表现为"脚本卡住不动"。2026-05-07 已导致多 AI 对话同时使用生成器/同步器脚本时大面积阻塞。

**本规则适用于**：任何产出文件的 standalone Python 脚本（生成器、同步器、导出工具等）。
