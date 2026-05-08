---
task_id: "TASK-INF-0006"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §2g Telemetry 数据安全与合规（OWASP MCP08:2025）"

title: "实现 Telemetry 数据安全与合规：OWASP MCP08 全对齐 + AES-256 加密 + HMAC 防篡改 + PII 脱敏 + 访问控制"
description: |
  实现 OWASP MCP08:2025 九项要求全覆盖：
  1. SQLite Encryption Extension/SQLCipher AES-256 加密
  2. HMAC 链式防篡改（每条 JSONL line 含 integrity.hmac_sha256）
  3. PII 字段级脱敏扩展（email/API key/IP/路径/phone/card/SSN）
  4. 遥测数据最小权限访问控制（Telemetry/FLE/AI Agent/Owner/外部模块五级）
  5. AI 施工约定：禁止硬编码密钥/禁止绕过 MCP 读原始文件
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\logs\\__init__.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\security.py"
    description: "安全模块：encryption_at_rest / HMAC chain integrity / PII masking / access_control"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\security.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§2g——OWASP MCP08 对齐声明 + 加密策略矩阵 + HMAC 链设计 + PII 脱敏规则 + 访问控制矩阵 + AI 施工约定"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "AES-256-GCM 加密/解密函数可用（per-field）"
  - "HMAC 链计算/验证函数可用——修改任一行后续 HMAC 失效"
  - "PII 脱敏规则全覆盖（email/API key/IP/路径/phone/card/SSN）"
  - "五级访问控制矩阵可查询"
  - "所有密钥通过环境变量读取——不写入 config/"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\security.py
  2. 检查 config/flags.yaml 是否添加了 telemetry.archive_encryption flag——如有则移除

depends_on:
  - "TASK-INF-0001"
blocked_by: []
status: "created"

tags_fn:
  - "security"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-015"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# TASK-INF-0006: 实现 Telemetry 数据安全与 OWASP MCP08 合规

## 目标
实现 Telemetry 全链路数据安全，满足 OWASP MCP08:2025 九项要求，覆盖加密 at rest、HMAC 防篡改、PII 脱敏、最小权限访问控制。

## 触发条件
- TASK-INF-0001 通过

## 执行步骤

### 读
- 蓝图 §2g：OWASP MCP08 对齐声明（9 项）、加密策略矩阵（5 层）、HMAC 链设计、PII 脱敏规则、访问控制矩阵（5 级）、AI 施工约定（5 条）

### 做
1. 实现 EncryptionManager：AES-256-GCM per-field 加密/解密
2. 实现 IntegrityManager：HMAC-SHA256 链计算 + 24h 自动校验
3. 实现 PIIMasker：6 类敏感字段脱敏规则
4. 实现 AccessController：5 级访问权限矩阵

### 产
- security.py

### 检
```bash
python -c "from zephyr.l12_system_telemetry.security import PIIMasker; assert PIIMasker.mask_email('user@domain.com') == 'u***@domain.com'; print('OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | encryption | AES-256-GCM 加解密往返一致 |
| 2 | integrity | 修改日志行→HMAC chain 校验失败 |
| 3 | pii | 6 类 PII correct masking |
| 4 | access | 5 级访问权限矩阵可查询 |
