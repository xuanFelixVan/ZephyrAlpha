---
module_id: KE-3716
title: scaffold exit_criteria
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# scaffold exit_criteria

scaffold exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-0-01 | SSoT Validator 实现完成，对仓库执行返回 0 违规 | `scripts/governance/validate_ssot.py --all` |
| EXIT-0-02 | 11 处 SSoT 矛盾（Kimi #7 根因）已全部修复 | `scripts/governance/validate_ssot.py --check conflicts` |
| EXIT-0-03 | `ssot-authority-map.md` 已写入权威路径，无指向旧体系的链接 | `grep-scan` for `docs/02_ARCHITECTURE/` |
| EXIT-0-04 | B-E 阶段的原子事务 change_log 已完整归档到 `reference-remap-table.yaml` | 人工审核 |
| EXIT-0-05 | scaffold 验收会议纪要已写入 `docs/_working/audit/-acceptance.md` | 文件存在性 |
