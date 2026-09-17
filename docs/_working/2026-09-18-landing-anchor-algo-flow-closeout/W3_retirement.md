---
ttl: task_bound
completes_when: Owner 准退役（裁定#307① 净删=Owner 永久门位）+ 注册表洁净窗到位后执行；本环节只登记退役包，不代删
title: W3 — 孤儿 model_capability_exam__init__.yaml 退役（Owner 门位 + 洁净窗）
owner: ZephyrAlpha-Owner
session: st-anchorfix-20260918
date: 2026-09-18
---

# W3 — 孤儿件退役登记

## 为何只登记不代删

1. **Owner 永久门位**：注册表条目净删（capability_canonical_file_registry.yaml 摘除）
   属裁定#307① 明示的 Owner 永久门位——对话内口头授权不构成豁免（宪法 §5/§9.11）。
2. **洁净窗前置**：`capability_canonical_file_registry.yaml` 是多会话热文件，当前频繁
   被 foreign 会话 ` M`/staged。热注册表半改窗内动删除 = #ARCH-329 整文件吸收
   （我的删除 diff 会连带吸收他人未落地内容，破坏原子性）。

## 退役包（待批准后一键执行）

- 目标：孤儿 `model_capability_exam/__init__.yaml`（模块已退役、注册表条目悬空）。
- 既有 creation_token：`btfix-p1p2-model-capability-exam--init---20260916`
  （registry ~line 22008，随退役一并摘除）。
- 操作序（Owner 准 + 洁净窗）：
  1. `git rm` 目标孤儿件；
  2. CAS `safe_write_text` 摘除 registry 中该 file 条目 + 上述 token 条目；
  3. 同 commit 原子（宪法 RULE-REGISTRY / #ARCH-329 要求 registry 与其 canonical 同批）；
  4. 经队列正门落地，`git log -1 --name-only` 核归属。

## 需 Owner 裁定

**唯一真·Owner 门位项**：是否准退役该孤儿件及其 registry 条目。批准后由持有注册表
洁净窗者（或本会话续跑）按上述序执行。
