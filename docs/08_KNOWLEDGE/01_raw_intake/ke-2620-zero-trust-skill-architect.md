---
module_id: KE-2525
status: active
title: 9.5 Zero-Trust Skill Architecture
category: module_blueprint
---

# 9.5 Zero-Trust Skill Architecture

9.5 Zero-Trust Skill Architecture

```yaml
skill_zero_trust:
  description: "每个 Skill 加载都视为不受信任的负载——对标 Cisco Zero Trust for Agentic AI + Symbiont Trust Stack + SPIFFE 加密身份"

  principles:
    P1_never_trust_always_verify: "Skill 在每一次加载时都重新验证——不信任缓存版本"
    P2_least_privilege_by_default: "Skill 的 allowed-tools 默认为 read_only——需要 Write/Execute 的必须显式声明 + human 批准"
    P3_continuous_verification: "Skill 执行过程中每 N 个工具调用重新验证一次——防止会话中间 Skill 被篡改"
    P4_assume_breach: "假设任何 Skill 文件都可能被污染——只信任经过沙箱验证的执行结果"

  verification_chain:
    step1_identity: "Skill 文件的 SHA256 哈希 vs registry 记录的已知良性哈希"
    step2_schema: "YAML frontmatter 结构完整性检查"
    step3_sandbox: "隔离环境中加载 Skill → 验证不会触发已知恶意模式"
    step4_behavior: "Skill 执行时实时监控——工具调用模式 vs 该 Skill 的历史正常模式基线（行为异常检测）"

  non_human_identity_governance:
    description: "每个 Skill 执行实例 = 一个非人类身份（NHI）——对标 Cisco NHI Lifecycle"
    nhi_lifecycle:
      creation: "Skill 加载 → 生成临时 NHI Token（TTL = session 时长）"
      rotation: "Token 过期 → 自动续期（但需重新验证 Skill 完整性）"
      decommission: "Session 结束 → NHI 标记为 terminated → Audit Trail 记录完整执行链"
      revocation: "检测到异常 → 立即撤销 NHI Token → Skill 执行终止 → 阻止后续一切操作"
    identity_provider_integration: "对接 MOD-INF-018（Agent RBAC）——Skill NHI 的权限从 RBAC 策略中继承"

  skill_kill_switch:
    description: "每个 Skill 必须有一个紧急停止机制——对标 Amazon Kiro 事故（13h outage 因无法立即停止 Agent）"
    kill_switch_types:
      instant_termination: "立即停止当前 Skill 执行 → 撤销 NHI Token → 阻止任何新的工具调用"
      conditional_termination: "满足条件时自动触发（e.g. 连续 3 次门禁 FAIL / 访问了不在 allowed-tools 中的 API）"
      manual_override: "Owner 可通过 CLI or dashboard 对任何 running Skill 执行 kill"
    implementation: "对接 MOD-INF-020（Audit Trail）——kill_switch 事件作为最高优先级的 ANOMALY 记录"

  skill_slo:
    description: "每个 Skill 的服务等级目标——质量基线可量化"
    slo_by_type:
      Domain_implementer:
        max_latency_ms: 30000
        max_retries: 3
        min_success_rate: 0.95
        min_gate_pass_rate: 0.90
      Domain_governor:
        max_latency_ms: 60000
        max_retries: 1
        min_success_rate: 0.98
        min_gate_pass_rate: 0.95
      Role_architect:
        max_latency_ms: 45000
        max_retries: 2
        min_success_rate: 0.92
      Role_implementer:
        max_latency_ms: 20000
        max_retries: 3
        min_success_rate: 0.93
    violation_response: "SLO 连续 3 个评估周期 breach → 降级 Skill（从 stable → canary → dev）→ 人工审查根因"
```
