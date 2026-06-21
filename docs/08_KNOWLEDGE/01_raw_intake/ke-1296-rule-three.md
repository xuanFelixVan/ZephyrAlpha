---
module_id: KE-1209---------------------003
status: active
title: 🔴 RULE-THREE：删除前置确认协议 — 不确认价值，不动手（与 RULE-ZERO / RULE-ONE / RULE-TWO 同级）
category: governance_rule
---

# 🔴 RULE-THREE：删除前置确认协议 — 不确认价值，不动手（与 RULE-ZERO / RULE-ONE / RULE-TWO 同级）

🔴 RULE-THREE：删除前置确认协议 — 不确认价值，不动手（与 RULE-ZERO / RULE-ONE / RULE-TWO 同级）

> **触因**：2026-05-07 session-20260507-004 误删了有价值的 `g6-ctr-compliance.yaml`（G6 CTR 契约合规门禁，含 8 条检查 + 6 个 CTR 契约注册表），仅因它与重复文件被混入同一批 DeleteFile 调用。用户指出后才恢复。<br>
> **根因**：文件未在 `_registry.yaml` 中被单独登记，且删除前未逐行验证其内容价值。
