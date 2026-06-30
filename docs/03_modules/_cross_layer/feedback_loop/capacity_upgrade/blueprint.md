---
module_id: MOD-FEEDBACK_LOOP
submodule_path: src/zephyr/trading/feedback_loop
title: "FLE 容量升级附录 — 从S级到L级扩容方案"
doc_type: blueprint
template_for: blueprint
status: Draft
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
date: "2026-05-19"
valid_from: "2026-05-19"
ttl: permanent
construction_progress: design_only
actual_disk_path: ""
belongs_to: "MOD-FEEDBACK_LOOP"
parent_module: "MOD-FEEDBACK_LOOP"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: "FLE容量升级附录：S级→L级扩容D1-D14+GP1-GP5，100 AI Session并发/500 findings/cycle/240 events/s目标"

tags: ["feedback-loop", "fle", "capacity-upgrade", "scaling", "infrastructure"]
priority: P1
runtime_plane: warm
generation: 1
functional_domain: operations
depends_on:
  - {target: "MOD-FEEDBACK_LOOP", at: "all", why: "父蓝图——核心引擎设计"}
last_updated: "2026-05-19"

---

# FLE 容量升级附录 — 从S级到L级扩容方案

> belongs_to: MOD-FEEDBACK_LOOP | parent_module: MOD-FEEDBACK_LOOP
>
> **本蓝图是从 MOD-FEEDBACK_LOOP §17 拆分出的独立子蓝图。** MOD-FEEDBACK_LOOP 核心设计蓝图保留 §1-§16+§18+治理信息，容量升级内容由本蓝图独立管理。
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图模板 v3.5：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)

---

## §0 代码对齐验证

> ⚠️ 防止 construction_progress 与实际代码不符。
> 本蓝图仅包含容量升级设计方案，无独立代码文件。所有代码变更在父蓝图 MOD-FEEDBACK_LOOP 的 `src/zephyr/trading/feedback_loop/` 下。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-FEEDBACK_LOOP-CAPUP`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|
| | — | 本蓝图仅设计规格，无独立代码文件 | — | N/A | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| | 本蓝图无独立代码产出 — 所有实现由父蓝图协调 | — | — |

---

## §1 设计背景与目标

ZephyrAlpha 扩容至 100 AI 并发 Session → FLE 当前单线程 30s 轮询、67+ Detector 串行执行 → 无法满足 L 级容量需求。需将 FLE 自身检测-诊断-修复流水线并行化。

---

## §2 容量基线

| 基线 | S 级值 | L 级目标 |
|------|--------|---------|
| AI 并发 Session | 1~5 | 100 |
| Detector 并发 Worker | 1 (串行) | Quick(6)+Deep(4)+Batch(2)+Diag(6)+Actor(4)=22 |
| 轮询间隔 | 30,000ms | 5,000ms |
| 单周期 findings | 100 | 500 |
| 事件峰值 | ~5/s | 240/s |
| RingBuffer | 无 | Dual 4096 |

---

## §3 缺口分析

| 缺口 | 内容 | 状态 |
|------|------|:---:|
| D1 | Detector 并发池 | 设计完成 |
| D2 | 事件总线吞吐 | 设计完成 |
| D3 | Diagnoser 并行 | 设计完成 |
| D4 | FLE↔ScriptSystem 接口 | 设计完成 |
| D5 | Session 生命周期感知 | 设计完成 |
| D6 | 增量扫描触发 | 设计完成 |
| D7 | 存储分片 | 设计完成 |
| D8 | KG 扩展 | 设计完成 |
| D9 | 部署拓扑 | 设计完成 |
| D10 | FLE 自身 SLA | 设计完成 |
| D11 | 批处理/聚合 | 设计完成 |
| D12 | AI Session 管理 | 设计完成 |
| D13 | 自可观测性 | 设计完成 |
| D14 | 全量扫描窗口 | 设计完成 |
| GP1 | GPU/LLM VRAM 预算 | 设计完成 |
| GP2 | CPU 联合调度 (FLE+ScriptSystem) | 设计完成 |
| GP3 | E2E SLA 分解 | 设计完成 |
| GP4 | FLE 冷启动/故障恢复 | 设计完成 |
| GP5 | MOD-INF-005/010 容量契约对账 | 设计完成 |

---

## §4 升级版本矩阵

| 触发条件 | 动作 |
|---------|------|
| AI Session 数 > 10 | QuickPool 2→6, poll_interval 30s→5s |
| ScriptSystem 脚本 > 5,000 | RingBuffer B cap 4096→8192 |
| 单周期 findings > 500 | DiagnoserPool 6→10 |
| E2E MTTD > 5min | DetectorRouter 优化 + 快速通道 |

---

## §5 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 并发 AI Session | 1~5 | 100 | ThreadPoolExecutor 23 workers | ❌ | §17 三级检测池并行化 |
| ScriptSystem 脚本数 | 388 | 10,000 | RingBuffer 8192 events | ❌ | §17 D7 存储分片 |
| 模块数 | 1,623 | 1,500+ | Detector 67+ | ✅ | §17 D8 KG 扩展 |
| Detector 数量 | 67+ | 100~120 | Quick(6)+Deep(4)+Batch(2) | ❌ | §17 D1 检测池扩容 |
| 每周期 findings | 100 | 500 | FindingAggregator 去重 TTL 60s | ❌ | §17 D11 批处理聚合 |
| 事件峰值 | ~5/s | 240/s | RingBuffer Dual 4096 | ❌ | §17 D2 事件总线吞吐 |

---

## §6 施工指引

| Phase | 内容 | 优先级 | 依赖 |
|:---:|------|:---:|------|
| Phase 0 | 蓝图补全 (本文件) | — | — |
| Phase 1 | D1+D2+D3+D4: Scheduler v2 + RingBuffer + DetectorRouter + Protocol A/B | 🔴 P0 | — |
| Phase 2 | D5+D6+D7+D11: Session 感知 + Scan 追踪 + 存储分片 + 批处理 | 🟠 P1 | Phase 1 |
| Phase 3 | D8+D12+D13+D14: KG 扩展 + SLA 架构 + 自观测 + 全量窗口 | 🟡 P2 | Phase 2 |
| Phase 4 | D9+D10: 部署扩缩 + 全量扫描可选 | 🟡 P2 | Phase 3 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-FEEDBACK_LOOP Feedback Loop | 必须 | 父蓝图——核心引擎设计 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md` |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\capacity-upgrade\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\feedback-loop\` | 由父蓝图管理——容量升级组件统一在此实现 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉 |
