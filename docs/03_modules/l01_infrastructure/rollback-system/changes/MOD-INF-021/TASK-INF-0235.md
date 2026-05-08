---
task_id: "TASK-INF-0235"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.4 + §6.12 B59 + §9 exit code 13"
title: "依赖漏洞复扫——回滚后 vulnerability_rescan requirements.txt / Pipfile / package.json"
description: |
  实现 vulnerability_rescanner.py：
  回滚可能恢复包含已知 CVE 的旧版依赖。
  回滚后自动对 requirements.txt / Pipfile / pyproject.toml / package.json 运行漏洞扫描。
  发现 CVE → 尝试自动升级到安全版本。
  无法自动升级 → exit code 13 (VULN_REINTRODUCED) → DEFER_TO_HUMAN 通知 Owner 手动评估。
  对标 GitHub Dependabot / Snyk / OWASP Dependency-Check。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\vulnerability_rescanner.py"
    description: "依赖漏洞复扫——回滚后 CVE 检测 + 自动升级 + 无法修复则 DEFER_TO_HUMAN"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\vulnerability_rescanner.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B59 漏洞复扫结论"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 9000
timeout_minutes: 35
acceptance_criteria:
  - "回滚后自动解析 requirements.txt / Pipfile / package.json"
  - "对每个依赖版本查 CVE 数据库 (OSV.dev / PyPA advisory)"
  - "发现 CVE → 尝试自动 pip install --upgrade"
  - "无法自动修复 → exit code 13 → DEFER_TO_HUMAN"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\vulnerability_rescanner.py
depends_on:
  - "TASK-INF-0234"
blocked_by: []
status: "done"
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
