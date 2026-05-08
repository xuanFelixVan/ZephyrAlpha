---
module_id: KE-module_blu-4_4-005
title: 4.4 入库验证矩阵
category: module_blueprint
---

# 4.4 入库验证矩阵

4.4 入库验证矩阵

> 对标 K8s/CNCF 一致性认证 15 项自动验证检查——新脚本入库前必须通过以下矩阵中的所有强制性检查。

| # | 检查项 | 类型 | 验证方法 | 不通过后果 |
|---|--------|:---:|---------|----------|
| V1 | 文件存在于正确维度目录 | MUST | 文件系统检查 | 拒绝入库 |
| V2 | 文件名遵循前缀约定（validate_/detect_/audit_/check_/register_） | MUST | 正则匹配 | 拒绝入库 |
| V3 | manifest 条目完整（dimensions + priority + timeout + args + description） | MUST | `check_registry_consistency.py` | 拒绝入库 |
| V4 | `sys.stdout.reconfigure(encoding='utf-8')` 已添加 | MUST | 源码正则扫描 | 拒绝入库 |
| V5 | 脚本可独立运行（exit ≤ 1） | MUST | `python script.py --warn-only` | 拒绝入库 |
| V6 | 全量回归不破坏（run_all.py 全维度通过） | MUST | `python run_all.py` | 拒绝入库 |
| V7 | docstring 覆盖"参数/返回值/副作用" | SHOULD | AST 解析 | 警告 |
| V8 | shebang 已添加（`#!/usr/bin/env python3`） | SHOULD | 文件头检查 | 警告 |
| V9 | 退出码约定遵守（0/1/2/3 四档） | MUST | 运行后检查 `$?` | 拒绝入库 |
| V10 | `--warn-only` 参数已实现 | MUST | `python script.py --warn-only --help` 含该参数 | 拒绝入库 |
| V11 | 绝对路径使用（无相对路径引用） | MUST | 源码正则扫描 | 拒绝入库 |
| V12 | 异常全捕获（顶层 try/except → exit 3） | MUST | AST 检查 | 拒绝入库 |
| V13 | 与已有脚本无功能重叠（A0 查重通过） | MUST | 人工/AI 审查 | 拒绝入库 |

> **自动化执行**：V1-V12 由 `validate_script_onboarding.py` 自动检查；V13 需 AI 判断。
