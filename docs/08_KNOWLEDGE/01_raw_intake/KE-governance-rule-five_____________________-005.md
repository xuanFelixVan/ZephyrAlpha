---
module_id: KE-governance-rule-five_____________________-005
title: 🔴 RULE-FIVE：临时文件零残留铁律 — 建了必清，不清不能关 session（与 RULE-ZERO / RULE-ONE / RULE-TWO / R
category: governance_rule
---

# 🔴 RULE-FIVE：临时文件零残留铁律 — 建了必清，不清不能关 session（与 RULE-ZERO / RULE-ONE / RULE-TWO / R

🔴 RULE-FIVE：临时文件零残留铁律 — 建了必清，不清不能关 session（与 RULE-ZERO / RULE-ONE / RULE-TWO / RULE-THREE / RULE-FOUR 同级）

> **触因**：2026-05-07 根目录审计发现 13 个 `_temp*` / `_check*` / `_construction*` 临时文件 + 9 个终端损坏垃圾文件 + `zephyralpha-2-0/` 僵尸目录。这些文件全为 AI session 施工过程中创建但事后未清理。<br>
> **根因**：没有强制自净机制。AI 干完活就把临时脚本/检查文件/施工产物留在根目录，下一个 AI session 永远不会主动发现和清理。
