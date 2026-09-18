---
ttl: task_bound
completes_when: 总包批准 family_registry 立案并分配裁定号（生成器落点/条目来源/计数字段三要素确认）
title: 裁定申请书 req_tdchainJ_02——#306 红队条款① family_registry 立案书
lane: st-ff-tdchainJ-20260918
date: 2026-09-18
---

# req_tdchainJ_02 · #306 红队条款① family_registry 立案书

## 背景

裁定#306（组合门尺子 v2 提案）红队三条款处置（裁定#337 随批）：③回写已完成、②#315 追认已完成、
**①族注册表=治理层立案挂单**——真源注记：`config/standards.yaml:60` reexam_evidence
"#306 红队③族N_eff含历史被毙次数已回写本文件，①族注册表=治理层立案挂单"。
总包预裁=**立案**；红队条款若无注册表载体即无可执行判据。

## 立案三要素（按总包预裁要求写明）

1. **生成器落点**：`scripts/governance/standards_governance/` 子包内新增生成器
   （ARCH-031：governance/ 根禁新增 .py）。产出物落
   `docs/01_policies_and_standards/_registry/catalogs/` 下（与既有 catalogs 同区），
   建议名 `standard_family_registry.yaml`。
2. **条目来源**（生成器输入，禁手工维护——宪法 §9.5 静态清单红线）：
   - `config/standards.yaml` 全部 STD-* 标准条目（解析其 id/family/status 字段）；
   - `docs/01_policies_and_standards/_registry/vocabularies/governance_family_vocabulary.yaml`
     词表（族名合法性校验，VOCAB-HARDCODE 同源）；
   - 历史被毙次数（#306 红队③口径，从 standards.yaml reexam_evidence/N_eff 注记字段解析）。
3. **计数字段**：注册表顶层 `total_families` / `total_standards` 由生成器写入，
   散文引用一律用字段不写死数（宪法 §4.3 文档纪律）。

## 与既有裁定的衔接

- #307（注册表门位三档统一）：family_registry 属"派生自动"档（生成器产物，重跑即再生）。
- ROOR（docs/registry_of_registries.yaml）：新册须挂 ROOR 索引（RULE-REGISTRY）。
- #316（裁定引用门禁）：注册表条目引用裁定号须已登记，生成器只引 standards.yaml 内已有注记。

## 影响面

纯治理层新增（生成器+派生册），零交易链路行为变化；施工须走 RULE-DEPGRAPH 登记+翻译登记三件套。

## 待总包动作

批准立案 + 分配裁定号（车道不得自行取号，COORDINATION_LEDGER §4）+ 指定施工车道/波次。
