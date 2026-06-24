---
module_id: KE-3680
title: 一、Cursor vs Trae 分工
category: governance
---

# 一、Cursor vs Trae 分工

一、Cursor vs Trae 分工

| 任务类型 | 使用编辑器 | 原因 |
|---------|----------|------|
| 架构设计、ADR 编写 | Cursor | 需要高级推理能力 |
| 规范文档编写 | Cursor | 需要高级推理能力 |
| 代码实现（src/） | Cursor | 代码质量要求高 |
| 批量文件操作（>5 个文件） | Trae | 免费模型适合批量操作 |
| 文件消除流水线 | Trae | 免费模型适合批量操作 |
| 蓝图安全流水线 | Trae | 免费模型适合批量操作 |
| 校验脚本执行 | Trae | 简单执行任务 |
| 编码扫描 | Trae | 简单执行任务 |
