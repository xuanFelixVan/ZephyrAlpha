---
module_id: KE-documentat-2_11__________cl-017_021___wav-003
title: 2.11 基础设施缺口组件（CL-017~021，**Wave 1 R83/R84 增补**）
category: documentation
---

# 2.11 基础设施缺口组件（CL-017~021，**Wave 1 R83/R84 增补**）

2.11 基础设施缺口组件（CL-017~021，**Wave 1 R83/R84 增补**）

| 组件 | 路径 | 权限 | 判定理由 |
|------|------|------|---------|
| CL-017 system_snapshot() | `src/zephyr/context_engine/system_snapshot.py` | Human-Gated | snapshot 输出影响 AI 决策起点 |
| CL-018 DocCompressor | `src/zephyr/context_engine/doc_compressor.py` | Human-Gated | 压缩规则需审批 |
| **CL-018 CompressionPolicy YAML** | `config/compression/policy.yaml` | **Immutable Core**（**Wave 1 V-14 兜底**：防 Self-Modification）| 规则不可由 AI 改 |
| CL-019 ai-onboarding-guide.md 核心思想章 | `docs/01_policies_and_standards/ai-onboarding-guide.md` | Human-Gated | 文档可演进 |
| CL-020 master-registry-index| `docs/01_policies_and_standards/master-registry-index.md` | Human-Gated | 注册表 schema 演进 |
| CL-021 EditorConfigGate（同 RI-05）| 见 §2.9 | Immutable Core | 编码规则核心 |
| **Wave 1 V-14 BlueprintOverlapMergeGate** | `scripts/governance/validate_blueprint_overlap.py` | Immutable Core（**Wave 1 兜底**）| 治理门禁，自身不可被绕过 |
| **Wave 1 V-15 TruthSourceCascadeValidator** | `scripts/governance/validate_truth_source_cascade.py` | AI-Modifiable（**Wave 1 兜底**）| 追踪报告，需 Owner 审批同步 |
| **Wave 1 V-16 DraftsZoneLifecycleArchiver** | `scripts/governance/archive_drafts_zone.py` | Human-Gated（**Wave 1 兜底**）| 归档触发需 Owner 确认 |
