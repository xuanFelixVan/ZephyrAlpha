# Phase 1 D_GOVERNANCE 域拆分基线

**记录时间**: 2026-07-12
**Session ID**: sess-44544-20260712012733
**Worktree Path**: D:\ZephyrAlpha\.aidrafts\sess-44544-20260712012733
**DB 备份**: tmp/depgraph_backup_phase1.dump

## 基线数据（production 节点）

| domain_id | domain_name | production_nodes 缓存列 | 实际 production 节点 |
|---|---|---|---|
| D_GOVERNANCE | registry_management | 506 | 506 |

## 各 subdomain 节点分布

| subdomain_id | 节点数 | 迁移目标 |
|---|---|---|
| D_GOVERNANCE（自身） | 266 | ⚠️ 不迁移（无子域分类，需二期专项） |
| D_GOVERNANCE-RULE_ENFORCEMENT | 62 | D_GOV_ENFORCEMENT |
| D_GOVERNANCE-DRIFT_DETECTION | 56 | D_GOV_DRIFT |
| D_GOVERNANCE-AUDIT_TRAIL | 56 | D_GOV_AUDIT |
| ''（空字符串） | 31 | ⚠️ 不迁移（需二期专项） |
| D_GOVERNANCE-KB | 22 | D_GOV_KB |
| D_GOVERNANCE-REGISTRY_MANAGEMENT | 5 | 保留 D_GOVERNANCE |
| D_GOVERNANCE-SCRIPT_GOVERNANCE | 4 | D_GOV_SCRIPTS |
| D_GOVERNANCE-SEMANTIC_AUDIT | 3 | ⚠️ 未在方案中明确（需确认） |
| NULL | 1 | ⚠️ 不迁移 |

## 迁移预期

- **本次迁移**：62+56+56+22+4 = 200 节点迁出
- **迁移后 D_GOVERNANCE**：506 - 200 = 306 production 节点
- **⚠️ 问题**：306 > 150 ARCH-CAP-002 上限，仍违反
- **原因**：266 个 subdomain_id='D_GOVERNANCE' 的节点无子域分类，按 subdomain_id LIKE 'D_GOVERNANCE-XXX' 策略不会被迁移
- **处理方案**：本次先完成 200 节点迁移（OPS-2026071204），306>150 问题留二期专项（方案 §3.7 已声明）

## 迁移后各域预期节点数

- D_GOVERNANCE: ~306（⚠️ 仍超限，二期专项处理）
- D_GOV_AUDIT: 56
- D_GOV_DRIFT: 56
- D_GOV_ENFORCEMENT: 62（已有 82，本次 +62 = 等待确认是否重叠）
- D_GOV_KB: 22（新建）
- D_GOV_SCRIPTS: 4
