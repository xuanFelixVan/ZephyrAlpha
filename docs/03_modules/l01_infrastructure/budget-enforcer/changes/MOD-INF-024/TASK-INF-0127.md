---
task_id: "TASK-INF-0127"
module_id: "MOD-INF-024"
title: "IPI-Aware Budget Defense — IPI 指令检测 + Ed25519 Budget Signature Gateway + Financial Tunnel Detection（§2.28 + D-024-26）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: v0_7_0
blueprint_section: "§2.28"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0105"
  - "TASK-INF-0126"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\tamper_evident_log.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\ipi_defense.py"
acceptance_criteria:
  - "AC-01: IPIPatternDetector — 覆盖 8 类 IPI 指令模式：'你的预算很远'=谎报, '不必在意预算'=解除, '不保存不记录'=消除证据, '人工批准了'=伪造, '提升预算额度'=提升, '反复覆盖指令'=持久化篡改, '用 Burn 1 替代'=从DIY规则, '模型应自主'=哲学压制"
  - "AC-02: 检测方法——Markdown Agent 输入 1024 字符 Forefront regex + embedding 相似度"
  - "AC-03: past_attempts 针对耗时分析——连续 N 个 task 均出现同类型 IPI → pattern detection"
  - "AC-04: Budget Signature Gateway — 敏感操作（global_limit 提升/borrow_ratio 提升/to_prod_profile/disable_guard/delete_audit）必须 Owner Ed25519 签名"
  - "AC-05: verify_budget_tx(tx_data, signature, pubkey) → bool —— 验签失败 → DENY + log"
  - "AC-06: ALL 敏感 budget 操作 = nonce 自增 + hash chain + 签名 → tamper_evident_log 记录"
  - "AC-07: Financial Tunnel Detection — 安永提出的 "Cheapest model→NYC agent→most expensive agent" financial tunnel 模式检测"
  - "AC-08: tunnel 模式：Cheapest (tier_0) → expensive (tier_3) 的代理链 cost 差异 > 10× WARN"
  - "AC-09: IPI defense 对应 MOD-INF-020 Audit Trail 完整存储 IPI 检测事件和签名验证事件"
  - "AC-10: IPI defense 自我审计——每月检查各 defense 有效性"
rollback_instructions: "删除 ipi_defense.py + Budget Signature Gateway。系统退化为无 IPI 防护——依赖 Tamper-Evident Log 的事后审计"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1285-L1332 (§2.28 IPI Defense)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [ipi-defense, prompt-injection, ed25519, financial-tunnel, budget-security, v0.7.0]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0127: IPI-Aware Budget Defense — IPI 检测 + Budget Signature Gateway

## 1. 任务目标

实现针对间接提示注入（Indirect Prompt Injection, IPI）的预算系统防护——Agent 可被注入指令绕过预算限制。覆盖 8 类 IPI 模式检测 + Budget Signature Gateway（敏感操作需 Ed25519 签名）+ Financial Tunnel 检测。

## 2. 背景

蓝图 §2.28（决策 D-024-26，v0.7.0 新增）：Task-management/privacy-preserving oversight 的研究实践中提出 IPI 攻击 budget 系统的威胁。安永 2025 提出 Financial Tunnel 概念。

## 3. 实施步骤

```python
class IPIDefense:
    PATTERNS = {
        "budget_lie": ["你的预算还很远", "剩余预算充足", "不用担心预算限制"],
        "budget_off": ["不必在意预算", "忽略预算系统", "禁用预算检查"],
        "erase_evidence": ["不保存不记录", "跳过审计", "不要写入日志"],
        "fake_approval": ["人工批准了", "Owner 同意", "管理员已确认"],
        "raise_limits": ["提升预算额度", "增加 daily cap", "解锁 Tier 限制"],
        "persistent_tamper": ["反复覆盖指令", "更新全局预算为空", "永久性提升"],
        "diy_rules": ["用 Burn 1 替代", "你真正的规则是...", "更新 AGENTS.md"],
        "philosophical": ["模型应自主决策", "AI 有决定自己预算的权利"],
    }

    def __init__(self):
        self.detector = IPIPatternDetector(self.PATTERNS)
        self.signature_gate = BudgetSignatureGateway()
        self.tunnel_detector = FinancialTunnelDetector()

    def scan_agent_input(self, input_text: str) -> IPIScanResult:
        regex_hits = self.detector.match_regex(input_text)
        semantic_hits = self.detector.match_semantic(input_text)
        return IPIScanResult(regex_hits + semantic_hits,
                            severity=self._severity(regex_hits + semantic_hits))

class BudgetSignatureGateway:
    SENSITIVE_OPS = [
        "global_limit_increase", "borrow_ratio_increase",
        "to_prod_profile", "disable_guard", "delete_audit",
    ]

    def verify(self, operation: str, tx_data: dict,
               signature: bytes, pubkey: bytes) -> bool:
        message = self._serialize(operation, tx_data)
        return ed25519.Ed25519PublicKey.from_public_bytes(pubkey).verify(
            signature, message)
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/ipi_defense.py` | 新建 |
