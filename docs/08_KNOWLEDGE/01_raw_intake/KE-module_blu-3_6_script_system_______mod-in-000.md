---
module_id: KE-module_blu-3_6_script_system_______mod-in-000
title: 3.6 Script System 集成（对接 MOD-INF-005）
category: module_blueprint
---

# 3.6 Script System 集成（对接 MOD-INF-005）

3.6 Script System 集成（对接 MOD-INF-005）

| 脚本体系 | 职责 | 关系 |
|---------|------|------|
| Skill 的 `scripts/` | 操作指南的自动化部分（如门禁执行脚本） | 独立脚本——由 Skill 触发执行 |
| Script System 的 `run_all.py` | 全局审计管线（12 维度审计 + Finding Schema + pre-commit 集成） | 全局管线——覆盖所有模块 |
| 集成点 | Skill 脚本的输出（exit code + stdout）→ 被 Script System 采集为 Finding | 统一 exit code 约定：0=pass, 1=fail, 2=warning, 3=error |
