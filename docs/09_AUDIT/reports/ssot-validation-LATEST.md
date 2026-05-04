---
type: generated
ttl: 7d
generated_by: scripts/governance/validate_ssot.py
scan_time: 2026-05-05 01:25:33
---

# SSoT 矛盾扫描报告

> **扫描目录**：`docs`  
> **扫描时间**：2026-05-05 01:25:33  
> **扫描文件**：274 个 .md 文件，257 个含 frontmatter  

---

## 摘要

| 严重级别 | 数量 | 处置要求 |
|---------|------|---------|
| 🔴 P0（严重）| 30 | 必须立即修复，阻塞 beta 完成门禁 |
| 🟡 P1（重要）| 64 | 需尽快修复，影响可信度 |
| 🔵 P2（建议）| 0 | 低优先级，可按计划处理 |
| **合计** | **94** | |

---

## 🔴 P0 矛盾（30 条）

### P0-1：layer 字段值 `l00_data_source` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L00_data_source/index.md`
- **矛盾值**：`l00_data_source`
- **建议**：将 `layer: l00_data_source` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-2：layer 字段值 `l02_alpha_factor` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L02_alpha_factor/index.md`
- **矛盾值**：`l02_alpha_factor`
- **建议**：将 `layer: l02_alpha_factor` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-3：layer 字段值 `l04_risk_management` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L04_risk_management/index.md`
- **矛盾值**：`l04_risk_management`
- **建议**：将 `layer: l04_risk_management` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-4：layer 字段值 `l07_post_trade_analytics` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L07_post_trade_analytics/index.md`
- **矛盾值**：`l07_post_trade_analytics`
- **建议**：将 `layer: l07_post_trade_analytics` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-5：layer 字段值 `l00_data_source` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L00_data_source/governance/data-source-connection-policy.md`
- **矛盾值**：`l00_data_source`
- **建议**：将 `layer: l00_data_source` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-6：layer 字段值 `l00_data_source` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L00_data_source/operational/connector-onboarding-runbook.md`
- **矛盾值**：`l00_data_source`
- **建议**：将 `layer: l00_data_source` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-7：layer 字段值 `l02_alpha_factor` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L02_alpha_factor/governance/factor-quality-policy.md`
- **矛盾值**：`l02_alpha_factor`
- **建议**：将 `layer: l02_alpha_factor` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-8：layer 字段值 `l02_alpha_factor` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L02_alpha_factor/operational/factor-onboarding-runbook.md`
- **矛盾值**：`l02_alpha_factor`
- **建议**：将 `layer: l02_alpha_factor` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-9：layer 字段值 `l04_risk_management` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L04_risk_management/governance/risk-limits-policy.md`
- **矛盾值**：`l04_risk_management`
- **建议**：将 `layer: l04_risk_management` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-10：layer 字段值 `l04_risk_management` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L04_risk_management/operational/stop-loss-config-runbook.md`
- **矛盾值**：`l04_risk_management`
- **建议**：将 `layer: l04_risk_management` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-11：layer 字段值 `l07_post_trade_analytics` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L07_post_trade_analytics/governance/post-trade-reporting-policy.md`
- **矛盾值**：`l07_post_trade_analytics`
- **建议**：将 `layer: l07_post_trade_analytics` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-12：layer 字段值 `l07_post_trade_analytics` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L07_post_trade_analytics/operational/analytics-pipeline-runbook.md`
- **矛盾值**：`l07_post_trade_analytics`
- **建议**：将 `layer: l07_post_trade_analytics` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-13：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/architecture/adr-protocol.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-14：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/architecture/architecture-review-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-15：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/architecture/architecture-versioning-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-16：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/compliance/audit-protocol.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-17：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/compliance/audit-trail-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-18：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/compliance/regulatory-taxonomy-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-19：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/data/data-lineage-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-20：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/data/data-quality-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-21：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/data/data-retention-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-22：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/module/ai-behavior-iron-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-23：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/module/module-admission-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-24：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/module/module-interface-contract-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-25：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/module/module-lifecycle-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-26：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/module/multi-registry-synchronization-standard.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-27：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/security/access-control-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-28：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/security/secret-management-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-29：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/security/security-incident-response-policy.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

### P0-30：layer 字段值 `l01_infrastructure` 不在有效层 ID 集合（L00-L13/cross_layer）中

- **检查 ID**：`P0-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/code-dedup-engine/blueprint.md`
- **矛盾值**：`l01_infrastructure`
- **建议**：将 `layer: l01_infrastructure` 修改为有效的层 ID（参见 ssot-authority-map.md §一）

---

## 🟡 P1 矛盾（64 条）

### P1-1：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/adr-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-2：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/blueprint-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-3：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/playbook-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-4：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/policy-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-5：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/protocol-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-6：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/register-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-7：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/runbook-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-8：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/templates/standard-template.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-9：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L00_data_source/governance/data-source-connection-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-10：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L00_data_source/operational/connector-onboarding-runbook.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-11：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L02_alpha_factor/governance/factor-quality-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-12：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L02_alpha_factor/operational/factor-onboarding-runbook.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-13：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L04_risk_management/governance/risk-limits-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-14：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L04_risk_management/operational/stop-loss-config-runbook.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-15：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L07_post_trade_analytics/governance/post-trade-reporting-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-16：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L07_post_trade_analytics/operational/analytics-pipeline-runbook.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-17：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/architecture/adr-protocol.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-18：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/architecture/architecture-versioning-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-19：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/compliance/audit-protocol.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-20：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/compliance/audit-trail-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-21：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/compliance/regulatory-taxonomy-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-22：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/data/data-lineage-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-23：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/data/data-quality-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-24：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/data/data-retention-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-25：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/security/access-control-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-26：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/security/secret-management-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-27：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/security/security-incident-response-policy.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-28：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/operational/devops/architecture-change-playbook.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-29：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/operational/vibe_coding/ai-incident-and-emergency-playbook.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-30：status 字段值 `superseded` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/02_enterprise_architecture/adr/adr-0003-dual-ai-collaboration-workflow.md`
- **矛盾值**：`superseded`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-31：status 字段值 `partially_superseded` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/02_enterprise_architecture/adr/adr-0005-kms-architecture.md`
- **矛盾值**：`partially_superseded`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-32：status 字段值 `archived` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/02_enterprise_architecture/adr/_template.md`
- **矛盾值**：`archived`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-33：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/02_enterprise_architecture/target-architecture/08-operations-architecture.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-34：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/02_enterprise_architecture/target-architecture/architecture-endgame-locked.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-35：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/_master-blueprint/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-36：status 字段值 `approved` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/_sys-master/blueprint.md`
- **矛盾值**：`approved`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-37：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-38：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-39：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/agent-spec/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-40：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/audit-trail/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-41：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-42：status 字段值 `approved` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/capacity-assurance/blueprint.md`
- **矛盾值**：`approved`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-43：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/code-dedup-engine/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-44：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/code-dedup-engine/index.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-45：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/context-engine/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-46：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/database/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-47：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/drift-detector/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-48：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-49：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/feedback-loop/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-50：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/gate-engine/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-51：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/knowledge-base/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-52：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/llm-security/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-53：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/mcp-servers/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-54：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/pipeline/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-55：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/rollback-system/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-56：status 字段值 `approved` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/runtime-integration/blueprint.md`
- **矛盾值**：`approved`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-57：status 字段值 `approved` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/script-system/blueprint.md`
- **矛盾值**：`approved`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-58：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/shared-core/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-59：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/system-telemetry/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-60：status 字段值 `retired` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/task-card-kms/blueprint.md`
- **矛盾值**：`retired`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-61：status 字段值 `approved` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/task-system/blueprint.md`
- **矛盾值**：`approved`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-62：status 字段值 `draft` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/vector-memory/blueprint.md`
- **矛盾值**：`draft`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-63：status 字段值 `retired` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/vibe-coding-pipelines/blueprint.md`
- **矛盾值**：`retired`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired

### P1-64：module_id `MOD-INF-017` 在不同文件中 layer 字段不一致：`l01_infrastructure` in ['docs/03_mod

- **检查 ID**：`P1-2`
- **涉及文件**：
  - `docs/03_modules/l01_infrastructure/code-dedup-engine/blueprint.md`
  - `docs/03_modules/l01_infrastructure/code-dedup-engine/index.md`
- **矛盾值**：`l01_infrastructure`, `L01`
- **建议**：以 docs/02_enterprise_architecture/target-architecture/architecture-model/_index.yaml + layers/l*.yaml 中的层归属为准，统一修正

---

## 下一步行动

1. **立即修复 30 条 P0 矛盾**（阻塞 beta 完成门禁）
2. 安排修复 64 条 P1 矛盾（本 sprint 内完成）