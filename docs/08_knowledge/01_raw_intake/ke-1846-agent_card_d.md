---
module_id: KE-1755------------d-02-001
status: active
title: 2.2 Agent Card 与能力注册模型（决策 D-025-02）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 Agent Card 与能力注册模型（决策 D-025-02）

2.2 Agent Card 与能力注册模型（决策 D-025-02）

> **决策 D-025-02**：Agent Card 是 A2A 的"名片"——每个 Agent 启动时注册其能力声明（对标 Google A2A §5 + Anthropic Claude Code Agent Spec）。注册入口是 AGENTS.md 的扩展 `a2a_agents:` 字段，而非独立的 `/.well-known/agent-card.json`——因为多 IDE 并发场景下 AGENTS.md 是唯一跨平台统一入口（对标准 MOD-INF-019 D-019-02）。
>
> **决策依据**：Google A2A 用 well-known URI（企业场景，可预测域名），ZephyrAlpha 是本地多 IDE 场景（无固定域名），AGENTS.md 是 TRAE/Cursor/RooCode 都读的唯一文件——A2A 发现机制必须在此统一。

```yaml
agent_card_model:
  # === Agent Card 字段定义（对标 Google A2A §5.5）===
  agent_card_fields:
    - field: "agent_id"
      type: "string"
      format: "ARCH-{uuid7} | IMPL-{uuid7} | GOV-{uuid7}"
      description: "Agent 唯一标识——前缀关联 Skill Pack 角色"

    - field: "agent_type"
      type: "enum"
      values: ["architect", "implementer", "governor"]
      description: "Agent 角色类型——对齐 3 个 Skill Pack"

    - field: "display_name"
      type: "string"
      description: "人类可读名称——如 '架构师 Agent (TRAE)'"

    - field: "provider"
      type: "string"
      description: "Agent 提供者——IDE 名称（TRAE / Cursor / RooCode）"

    - field: "version"
      type: "string (semver)"
      description: "Agent Card 版本——对标 MOD-INF-019 Skill 版本"

    - field: "capabilities"
      type: "list[AgentSkill]"
      description: "Agent 能力列表（对标 Google A2A AgentSkill）"
      example:
        - skill_id: "SKILL-ARCH-001"
          name: "蓝图解读"
          description: "读取模块蓝图 → 生成 Pydantic 接口骨架"
          input_modes: ["text", "yaml"]
          output_modes: ["python", "pydantic"]

    - field: "endpoint"
      type: "string"
      description: "Agent 通信端点——本地进程间通信（IPC/pipe/内存队列）"

    - field: "authentication"
      type: "object"
      description: "认证方式——JWT RS256 非对称签名（对标 Google A2A SecurityScheme）"
      fields:
        - "scheme: bearer"
        - "public_key_fingerprint"

    - field: "resource_limits"
      type: "object"
      description: "Agent 资源限制"
      fields:
        - "max_concurrent_tasks: int (default=3)"
        - "token_budget_per_task: int (default=50000)"
        - "heartbeat_interval_seconds: int (default=30)"

    - field: "input_modes"
      type: "list[str]"
      description: "支持的输入模态（text/file/data）"

    - field: "output_modes"
      type: "list[str]"
      description: "支持的输出模态"

    - field: "status"
      type: "enum"
      values: ["active", "idle", "degraded", "dead"]
      description: "Agent 当前运行状态"

  # === AGENTS.md 中的注册入口 ===
  agnets_md_extension:
    section: "a2a_agents"
    format: "YAML list of Agent Card references"
    example: |
      a2a_agents:
        - agent_id: "ARCH-0192a7b1"
          agent_type: "architect"
          agent_card_path: "src/zephyr/a2a/cards/architect.yaml"
        - agent_id: "IMPL-3f8e2c91"
          agent_type: "implementer"
          agent_card_path: "src/zephyr/a2a/cards/implementer.yaml"
    note: "Agent Card 物理文件存放在 src/zephyr/a2a/cards/ 目录，AGENTS.md 只引用不内联"

  # === Agent Card 完整性校验 ===
  card_integrity:
    on_register: "SHA-256 hash 校验——Agent Card 未被篡改"
    periodic: "每 5 分钟 re-hash 对比"
