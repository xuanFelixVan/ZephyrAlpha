---
module_id: KE-237------3-001
status: active
title: 3.1 违规文件（3 个）
category: documentation
---

# 3.1 违规文件（3 个）

3.1 违规文件（3 个）

| 优先级 | 文件路径 | 违规类型 | 违规代码 | 当前文件名 | 建议整改 |
|--------|---------|---------|---------|-----------|---------|
| P0 | `docs/02_enterprise_architecture/target-architecture/architecture-audit-final-verdict-2026-04-21.md` | 日期后缀 | N-03 | `...verdict-2026-04-21.md` | `architecture-audit-final-verdict.md` |
| P1 | `archive/reorg-2026-04-24/one-shot-completed/working-designs/memory-system-landing-v1-checklist.md` | 版本号后缀 | N-02 | `...landing-v1-checklist.md` | `memory-system-landing-checklist.md` |
| P1 | `docs/09_audit/reports/ssot-validation-latest.md` | LATEST 格式不规范 | §2.4 | `...latest.md` | `ssot-validation-LATEST.md` |

**根因分析**：

- **违规 1**：Stage G 修复时仅将紧凑日期 `20260421` 转为 ISO 格式 `2026-04-21`，但未彻底去除日期后缀，属于 Stage G 遗留问题
- **违规 2**：Stage G 修复了 `docs/` 下的同名文件，但 `archive/` 下的变体被遗漏
- **违规 3**：自动生成脚本 `validate_ssot.py` 输出文件名时使用了小写 `latest`，未遵循 §2.4 大写 `LATEST` 约定
