---
blueprint_id: MOD-023
status: active
title: Ke Governance Adr Registry Migration 000
module_id: KE-1066---

ttl: permanent
---
ke_id: KE-governance-adr_registry_migration-000
title: "L3 架构决策记录（ADR 迁移 · R72 三层模型）"
source: src/zephyr/governance/adr_registry.py (已删除)
category: architecture_decision
tags: [A2, architecture_decision, R72, L3]
status: active
created: 2026-05-08
r72_note: >
  依据 R72（2026-04-27）三层决策记录模型，ADR 体系已废弃。
  本 KE 仅保留 L3 级别决策（需要对比表/数据支撑的重大架构决策）。
  L2 级别决策（一句话结论）已分流至 AGENTS.md §10 历史决策。
  原 adr_registry.py 已删除；蓝图 adr_ref 已改为 kb_ref；
  原 docs/.../adr-status-registry.yaml（PS-REG-015）已删除。

l3_decisions:
  - adr_id: KBG-0003
    title: "DeepSeek-Only Pipeline + Claude Extreme Rescue"
    date: "2026-03-01"
    status: Accepted
    source: "SYS-MASTER-001 §3.3"
    conclusion: "全部使用 DeepSeek V4 Pro（$1.74/M token），Claude API 仅在极端救援场景触发（DeepSeek 连续失败>=3次 或 autonomy_level==unsafe 且 DeepSeek 已失败）。GLM 从管线中移除。"
    rationale: >
      经济最优选：DeepSeek 比 GLM 便宜且更强。Claude $5-25/M token，
      仅在所有其他模型都失败时才触发，security/experimental 标签不再直接路由 Claude。
    alternatives_considered:
      - "DeepSeek + GLM 双模型审查（原方案）：GLM 审查独立性有价值，但增加 API 复杂度和成本"
      - "DeepSeek + Qwen 审查：Qwen 72B 审查能力强，但多一个 API 供应商"
      - "全 DeepSeek + Claude 救援（选定方案）：最简单，最便宜，Claude 兜底"
    see_also: b_execution_model.yaml

  - adr_id: KBG-0011
    title: "Three-Layer Execution Model — Trae/Local/API"
    date: "2026-05-08"
    status: Accepted
    source: "b_execution_model.yaml"
    conclusion: "ZephyrAlpha 采用三层执行模型：Trae（人在旁边，零成本）→ Local（BGE-M3 嵌入，CPU 即可）→ API（DeepSeek V4 Pro，Claude 仅极端救援）。"
    rationale: >
      日常开发不需要 API 费用（Trae AI 直接执行）；
      向量嵌入必须本地运行（延迟+隐私）；
      批量/夜间任务需要无人值守能力（API 模式）。
    alternatives_considered:
      - "全 API 模式：简单但日常开发成本高"
      - "全本地模式：数据安全但代码生成质量不够"
      - "三层混合（选定方案）：按场景选最经济的执行方式"
    see_also: b_execution_model.yaml
