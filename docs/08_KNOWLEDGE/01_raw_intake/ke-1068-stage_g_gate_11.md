---
module_id: KE-984--------gate-11-----006
status: active
title: 6.2 Stage G 漏网清理 + GATE-11 引擎落地（2026-04-25）
category: governance
ttl: permanent
---

# 6.2 Stage G 漏网清理 + GATE-11 引擎落地（2026-04-25）

6.2 Stage G 漏网清理 + GATE-11 引擎落地（2026-04-25）

**GATE-06 → GATE-11 编号纠偏**：Stage F 预占的 `GATE-06` 与 Architecture-as-Code 已有 `GATE-06 事件 publisher 层检查`（`check_architecture_gates.py v2.0.0`）冲突，本门禁续号为 `GATE-11`，AaC 编号空间 append-only 不动（对标 KBG-0006 跳号治理精神）。

**Stage F 漏网扫尾**：
- **8 个 KE 文件**：`KE-NNN-*.md` → `ke-NNN-*.md` 全体小写化（`docs/08_knowledge/best-practices/`）
- **1 个索引**：`docs/08_knowledge/index.md` → `index.md`
- **29 处视图 module_id**：`target_architecture/` 系列 `EA-ARCH-*` / `EA-VIBE-*` / `EA-AUDIT-*` / `EA-SESSION-*` / `EA-PHASE-*` → `VIEW-*` / `STD-*` / `POL-*` 三族合法命名空间
- **2 个文件名真违规**：
  - `memory-system-landing-v1-task-draft.md` → 去 `-v1`（作者版本后缀，不属于技术产品版本）
  - `architecture-audit-final-verdict-20260421.md` → `-2026-04-21.md`（ISO 日期格式）
- **pydantic-v2 等技术产品版本**：加入 `TECH_VERSION_TOKENS` 豁免白名单（§2.8）

**GATE-11 引擎上线**：`scripts/governance/check_naming_convention.py` + `.pre-commit-config.yaml` 注册，7 条违规规则（N-01 ~ N-07）+ 技术栈豁免机制；全库扫描收敛到 **0 violation**。

**snapshot 保留**：`_reorg_snapshots/snapshot-stage-G-pre`（可回滚）

---
