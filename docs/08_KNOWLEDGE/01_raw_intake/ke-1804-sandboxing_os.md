---
module_id: KE-1713--------sandboxing----os---003
status: active
title: 2.14 升级引擎自身 Sandboxing —— OS 级隔离（决策 D-022-08）
category: module_blueprint
ttl: permanent
---

# 2.14 升级引擎自身 Sandboxing —— OS 级隔离（决策 D-022-08）

2.14 升级引擎自身 Sandboxing —— OS 级隔离（决策 D-022-08）

> **决策 D-022-08**：升级引擎自身运行在 OS 级 Sandbox 中——文件系统隔离（只读项目文件 + 只写审计日志）+ 网络隔离（只连内部审计存储，不连外部网络）。引擎不与Agent共享权限上下文。Agent试图访问引擎Sandbox内部→blocked。
>
> **决策依据**：MMNTM "Lethal Trifecta"——升级引擎同时满足 (1)访问私密数据 (2)接收不可信输入 (3)可改变状态→自身极危。Claude Code CVE-2025-59536——项目内代码在trust确认前就能执行。Anthropic Sandboxing——OS级filesystem+network双隔离使permission prompts减少84%且安全性保持。

```yaml
escalation_engine_sandboxing:
  # === 文件系统隔离 ===
  filesystem_isolation:
    read_access:
      - "docs/ 下所有蓝图文件（只读）"
      - "escalation_rules.yaml（只读 + hash校验）"
      - "rbac_roles.yaml（只读 + hash校验）"
    write_access:
      - "docs/09_audit/escalation_audit.jsonl（追加写——唯一写入路径）"
      - "/tmp/escalation-engine.pid（进程锁文件）"
    deny:
      - "src/ 下任何文件（引擎不写源码）"
      - "*.env / *.key / *.secret（凭证隔离）"
      - ".git/ 目录"
    enforcement: "OS级——Linux bubblewrap / macOS seatbelt（对标 Claude Code）"

  # === 网络隔离 ===
  network_isolation:
    allow:
      - "localhost:{AUDIT_SERVICE_PORT}（审计存储服务——内部）"
      - "localhost:{METRICS_PORT}（指标暴露端点——内部）"
    deny:
      - "所有出站外部连接"
      - "LLM API endpoints（引擎不直接调用LLM——通过隔离的推理服务代理）"
    enforcement: "OS级网络命名空间隔离"

  # === 引擎进程隔离 ===
  process_isolation:
    user: "zephyr-escalation（独立系统用户，非root，非owner）"
    capabilities: "无特权（no CAP_SYS_ADMIN, no sudo）"
    resource_limits: "max_memory=256MB, max_cpu_time=5s per decision"
    watchdog: "外部健康检查进程监控引擎——引擎僵死→自动重启→恢复最近checkpoint"

  # === 跨边界访问检测 ===
  boundary_violation:
    detection: "任何Agent/IP尝试连接引擎Sandbox内部端口→触发安全事件"
    action: "立即通知Owner + 源Agent升级至blocked + 安全事件写入独立审计日志"
```

---
