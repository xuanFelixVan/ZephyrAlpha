---
module_id: KE-module_blu-feedback_loop_engine_interface-001
title: Feedback Loop Engine Interface / 反馈闭环引擎接口规范
category: module_blueprint
---

# Feedback Loop Engine Interface / 反馈闭环引擎接口规范

Feedback Loop Engine Interface / 反馈闭环引擎接口规范

> **定位**：反馈闭环引擎（FLE）——**接口与真源以 YAML frontmatter `truth_source` 为准**（`MOD-INF-010` 蓝图 + `architecture-model/layers/b_feedback_loop.yaml`）。补齐 Generate → Validate → **Analyze → Evolve** 四段的后两段，使系统能从历史数据学会自我调参。演进路线历史上曾以「VG-07 反馈闭环缺口」表述纳入优先级（仅作背景，**非**文档 SSoT）。
>
> **没有 FLE 的问题**：
>
> 1. 任务完成后指标散落（CI 日志 / Agent 日志 / VMS stats）→ 没有统一基线
> 2. 质量波动无量化触发器 → "最近测试通过率下降"靠直觉发现
> 3. Context Engine 权重永远默认 → `lessons` 槽长期无用仍占 10% 预算
> 4. 幻觉事件缺关联分析 → 同类型 hallucination 反复出现无根因

---
