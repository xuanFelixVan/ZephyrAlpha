---
module_id: KE-412----windows-ac-003
status: active
title: 5.2 experimental 实现：Windows ACL + 只读挂载
category: documentation
ttl: permanent
---

# 5.2 experimental 实现：Windows ACL + 只读挂载

5.2 experimental 实现：Windows ACL + 只读挂载

选型理由：

- **零外部依赖**：不需要 Docker Desktop，单人机器直接可用
- **可观测**：Windows Security Event Log 原生记录违规访问
- **可升级**：beta 可切到 Docker Desktop（同一接口，TECH-12 watchboard）

**沙箱规则**：

| 资源类别 | 权限 | 实现 |
|---------|:----:|------|
| `src/` | RO | ACL + FileSystemWatcher |
| `docs/` | RO | ACL |
| `.runtime/sandbox-work/` | RW | Agent 唯一写入区 |
| 其他路径（`.env` / `~/` / `C:\Windows`）| 拒绝 | ACL DENY ACE |
| 网络出口 | 仅 LLM Provider 白名单 | Windows Firewall Rule |
| 系统命令 | 白名单（`python`, `git status`, `mkdocs build`, ...）| Orc 命令解析器 |
| 环境变量 | 过滤 `SECRET_*` / `API_KEY_*` | Orc 进程派生时移除 |
