---
task_id: "TASK-SYS-0020"
source_blueprint: "SYS-MASTER-001"
source_section: "§28 供应链安全 + §87 SBOM + §95 API生命周期"

title: "供应链安全(SPDX SBOM/Sigstore) + SBOM依赖智能(depth≤5,CVSS≥7) + API 3阶段生命周期(Active/Deprecated/Removed+90d通知窗口)体系"
description: |
  将 SYS-MASTER-001 §28 供应链安全 + §87 SBOM生成 + §95 API生命周期三合一落地。
  §28: pip-audit/safety扫描→每次安装自动执行 / SPDX SBOM→licenses/CVEs/version_pins /
  Sigstore/TUF签名验证 / vendor lock-in监控→12个月无更新→评估迁移。
  §87: SBOM格式 CycloneDX/SPDX / 依赖深度≤5 / License合规(MIT/Apache2.0/BSD/PSF) /
  CVE CVSS≥7.0→自动Flag。
  §95: API 3阶段——Active→Deprecated→Removed。
  Deprecation通知 90天窗口 + Deprecation HTTP header + migration guide + grace period。
  本卡搭建 supply_chain_security.py + sbom_generator.py + api_lifecycle.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\supply_chain_security.py"
    description: "§28 pip-audit/SPDX SBOM/Sigstore/12mo vendor lock-in check"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\sbom_generator.py"
    description: "§87 SBOM CycloneDX/depth≤5/license/CVSS≥7.0 flag"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\api_lifecycle.py"
    description: "§95 API 3阶段 Active/Deprecated/Removed + Deprecation 90d通知+ migration guide"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\supply_chain_security.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\sbom_generator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\api_lifecycle.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§28 供应链安全(SBOM/Sigstore/12mo)+§87 SBOM(depth5/CVSS7)+§95 API 3阶段(Active→Removed 90d)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 50

acceptance_criteria:
  - "supply_chain: pip-audit scan→vulnerabilities[] CVSS≥7→ block 安装. sbom.spdx.json 导出. vendor_lockin(dt>12mo)→flag"
  - "sbom: CycloneDX JSON→dep_tree≤5→license MIT/Apache2.0/BSD/PSF only→CVE CVSS≥7.0→alert"
  - "api_lifecycle: APIState枚举3成员 Active/Deprecated/Removed. DeprecationNotice通知 90d +header+migration guide"

rollback_instructions: |
  git rm src/zephyr/governance/supply_chain_security.py sbom_generator.py api_lifecycle.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0006"
blocked_by: []
status: "done"
tags_fn:
  - "security"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
