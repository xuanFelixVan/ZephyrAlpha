---
module_id: KE-990---ssot-validator-scaffo-008
status: active
title: 6.4 T0 — SSoT Validator（scaffold 唯一治理任务）
category: governance
ttl: permanent
---

# 6.4 T0 — SSoT Validator（scaffold 唯一治理任务）

6.4 T0 — SSoT Validator（scaffold 唯一治理任务）

**定位**：KBG-0021 定义，是 scaffold → experimental 的**强制门禁**。没有 SSoT Validator 通过，任何 experimental 核心服务（LSG/CE/VMS/Orc/FLE）落地任务都被阻塞。

**治理归属**：

| 层 | 产物 | 物理位置 |
|---|------|---------|
| **Policy** | SSoT 一致性规则集 | `docs/01_policies_and_standards/ssot-validation-rules.md`（Stage J 待建） |
| **Factory** | Validator 实现 | `scripts/governance/d5_architecture/validate_ssot.py`（复用 11 维审计器骨架）|
| **Runtime** | 每日/每 PR 扫描 | CI `ci_audit/ssot_daily.py` + pre-commit hook |

**检查清单（scaffold 出口必须 100% 通过）**：

- [ ] 所有 frontmatter schema 符合 KBG-0002
- [ ] 所有跨文档引用链接 Valid（无死链）
- [ ] 所有 `module_id` 在全库唯一（无重复）
- [ ] 所有文件在 `directory-keep-whitelist.yaml` 或有明确 owner
- [ ] `reference-remap-table.yaml` 审计日志完整（本次重组的 10+ 条 change_log）
- [ ] 14 层分层无越界引用（L02 不得 import L05）
- [ ] 6 大核心服务接口规范已全部在 `docs/03_modules/_b_track_interfaces/` 就位
