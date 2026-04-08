# OpenClaw 文档整改方案（草稿）

> **状态**: 执行就绪 — **具体顺序、验收打勾、质量门**以执行手册为准（见下「必读三件套」）  
> **适用场景**: 个人仓库、单人开发、AI 辅助维护  
> **关联 run_id**: OPENCLAW_20260408_033500  
> **依据**: `docs/09_AUDIT/REPORTS/OPENCLAW_AUDIT_SUMMARY_20260408.md`、`OPENCLAW_REMEDIATION_BACKLOG.md`、`OPENCLAW_L3_CONFLICTS.md`、`OPENCLAW_INVENTORY_AUDIT_LEDGER.csv`  
> **修订日期**: 2026-04-08（v1.2：裁决已锁定，废除「自填 §8」流程）

---

## 0. 必读三件套（按此执行即可闭环）

| 顺序 | 文件 | 作用 |
|------|------|------|
| 1 | [`../STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md`](../STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md) | **裁决书**：双 YAML、`audit_state`、module_id、pre-commit、重复正文 — 已全部替你裁定 |
| 2 | [`OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`](./OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md) | **执行手册**：阶段顺序 P0-A→P0-B→P1-A→P1-B→P1-C、每阶段质量门、**Exit Criteria（什么叫整改闭环完成）** |
| 3 | [`../REPORTS/OPENCLAW_REMEDIATION_BACKLOG.md`](../REPORTS/OPENCLAW_REMEDIATION_BACKLOG.md) | **任务明细表**：与手册阶段对照逐项勾选 |

**你不必**再填「选项 → 决定」模板；**不必**把内容贴进 Cursor 规则，除非你想让 AI 长期记住——最低限度是：**每次让 AI 批量改文档时，把裁决书全文或路径发给它**。

---

## 1. 为何先做「方案草稿」

- **体量**：双 YAML、重复 `module_id`、归档与链接问题涉及数百至两千余篇，若无统一合并规则与门禁，批量脚本极易造成二次损坏。  
- **语义风险**：双 YAML 合并不是纯语法问题，需约定「以哪一块为准」「冲突字段如何裁决」，否则 `module_id` / `responsibility` 可能被静默覆盖。  
- **可追溯性**：分阶段、小批、可 diff 的整改比「一次改全库」更易回滚；Git 即你的「审计底稿」。

**结论**：合并策略与批次规则已写入**裁决书 + 执行手册**；动 `docs/` 正文时严格按手册阶段执行即可。

---

## 2. 目标与非目标

| 目标 | 非目标 |
|------|--------|
| 消除 P0：不可读编码、明确死链、阻断性结构错误 | 不重写文档技术内容、不做大规模文风统一 |
| 收敛 P1：双 YAML、`module_id` 唯一性、关键内链、缺 ID 补全策略 | 不在本阶段完成全库目录重编号（归入 P2 长期项） |
| 每次合并后可通过 Sentinel/L1 或等价检查回归 | 不强制消灭所有「伪链接」与 notebooks 非 md 目标（可标注豁免） |

---

## 3. 前置条件（整改开始前）

1. **Git**：自当前稳定点拉分支，例如 `docs/remediation-openclaw-20260408`；**不要**在直接改 `main` 上批量改两千文件。  
2. **基线（可选）**：复制一份 `OPENCLAW_INVENTORY_AUDIT_LEDGER.csv` 到 `STATE/` 或记文件哈希，便于事后对比。  
3. **工具**：每批改动后能跑 `sentinel_l1_governance_scan.py`（或等价）；`pre-commit` 处理规则见裁决书 **ADR-OC-004**。  
4. **台账**：以 Ledger 为文件全集；具体问题以 `OPENCLAW_REMEDIATION_BACKLOG.md` 与 L2/L3 报告为准。

---

## 4. 机构流程在你仓库里的落地方式（无需你再「拍板」）

专业机构依赖 **ADR + 变更批次 + 质量门 + Exit Criteria**。你已有一份**锁定的 ADR 合集**（见 §0 裁决书），相当于「架构评审委员会已签字」。后续若规则要改，应**修订裁决书并 bump 版本**，而不是口头改口径。

---

## 5. 重复 / 多版本正文怎么处理

**一律以裁决书为准**：见 `GOVERNANCE_DECISIONS_LOCKED_20260408.md` 中的 **ADR-OC-005**（合并 / supersede+归档 / 删除前提、与双 YAML 结构修复的区别）。

---

## 6. 分阶段执行与验收

**细则、顺序、每阶段跑什么命令、什么叫「闭环完成」**，已全部写入 [`OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`](./OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md)，本文不再重复，避免两处不一致。

---

## 7. 回滚与记录

- 每阶段打一个 **tag** 或在 commit 里写清「本批前 L1 报告路径」。  
- 若某批后 L1 变差：**revert 该批**，**只改裁决书或脚本**，不堆补丁。

---

## 8. 文档关系

| 文档 | 角色 |
|------|------|
| [`GOVERNANCE_DECISIONS_LOCKED_20260408.md`](../STATE/GOVERNANCE_DECISIONS_LOCKED_20260408.md) | **规则源（已裁定）** |
| [`OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md`](./OPENCLAW_REMEDIATION_EXECUTION_PLAYBOOK_20260408.md) | **执行手册与 Exit Criteria** |
| 本草稿 | 背景、目标、前置条件、与上两者关系 |
| `OPENCLAW_REMEDIATION_BACKLOG.md` | 任务明细 |
| `OPENCLAW_AUDIT_SUMMARY_20260408.md` | 审计基线数字 |
| `OPENCLAW_L3_CONFLICTS.md` | 冲突与去重依据 |
