---
module_id: KE-4425
title: V类：氛围编程基础设施的自我修改漏洞
category: module_blueprint
---

# V类：氛围编程基础设施的自我修改漏洞

V类：氛围编程基础设施的自我修改漏洞

| # | 盲点 | 严重性 | 专业对标 | 本蓝图落位 |
|---|------|:---:|------|------|
| 158 | **Hooks自编辑漏洞**——PreToolUse/PostToolUse hooks自身可通过Edit/Write被AI修改。§2.34 工具链安全基线依赖hooks，但hooks本身是可修改的文件→AI可先改hook再执行被block的操作。需外部不可变hash store+Owner签名验证 | 🔴 P0 | Yugoge claude-code-config Issues#11226(2026-04-16)——"Hooks 自体が Edit/Write で改変可能" | §2.37-A hooks_self_edit |
