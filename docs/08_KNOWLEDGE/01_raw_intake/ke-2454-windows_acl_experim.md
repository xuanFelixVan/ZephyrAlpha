---
module_id: KE-2359--------experim-003
status: active
title: 6.1 Windows ACL 沙箱实现要点（experimental 默认）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6.1 Windows ACL 沙箱实现要点（experimental 默认）

6.1 Windows ACL 沙箱实现要点（experimental 默认）

- repo 根目录整体 ACL 只读给 Agent 进程用户
- `writable_paths` 每项创建 overlay 目录，softlink 到 `.runtime/sandboxes/<sid>/writable/<path>/`
- Agent 进程以独立受限用户运行（避免继承调用者权限）
- 网络隔离通过 Windows Defender Firewall 规则在沙箱期间禁用出站（`network_access='none'`）
- `allowed_commands` 通过 AppLocker 策略或自建命令白名单 wrapper
