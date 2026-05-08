---
module_id: KE-module_blu-2_9_shared-utilities-000
title: 2.9 shared-utilities（通用工具层）
category: module_blueprint
---

# 2.9 shared-utilities（通用工具层）

2.9 shared-utilities（通用工具层）

> **盲点 #5/#14/#15/#3 修复**——类型安全 + diff/patch + 安全I/O + 配置加载四大缺口。

| 文件 | 职责 |
|------|------|
| `types.py` | **13 个语义化 NewType 别名**——TaskId / ModuleId / FilePath / SessionId / AgentId / ... |
| `diff_utils.py` | **compute_diff + apply_patch**——统一 diff 格式 + patch 干跑检测 |
| `file_utils.py` | **atomic_write + backup_and_rollback**——POSIX 原子写入 + 自动备份回滚 |
| `config/loader.py` | **load_yaml_config + Pydantic 校验**——三段式 YAML 加载（parse→merge→validate）|

---
