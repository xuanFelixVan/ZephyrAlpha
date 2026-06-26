---
module_id: KE-1165--------spine-and-wings-006
status: active
title: 一、LPC 双轨架构总则（Spine-and-Wings）
category: governance
ttl: permanent
---

# 一、LPC 双轨架构总则（Spine-and-Wings）

一、LPC 双轨架构总则（Spine-and-Wings）

本项目按 **Layered + Platform-Capabilities (LPC) 双轨架构**（KBG-0022）治理：

| 轨道 | 语义 | 编号前缀 | docs/ 镜像 | src/zephyr/ 物理位置 |
|------|------|----------|------------|----------------------|
| **C 轨（脊柱）** | Layered 业务过程（14 层 L00-L13）| **`l<NN>_`** | `docs/03_modules/l<NN>_*/` | `src/zephyr/l<NN>_*/` |
| **B 轨（双翼）** | Bounded Context 平台能力 / 横切基础设施 | **无前缀** | 蓝图→`docs/03_modules/_domain-infra_ops/`（与C轨L01蓝图统一存放）；接口规范→`docs/03_modules/_b_track_interfaces/` | `src/zephyr/{llm_security,vector_memory,context_engine,orchestrator,feedback_loop,gates,pipeline,core,db,kb,mcp,shared}/` |

> **v3.2.0 澄清**：`07_ai_engineering/` 已废弃——其内容（5个B轨接口规范）已并入 `docs/03_modules/_b_track_interfaces/`。
> 统一理由：蓝图、接口规范、施工计划三个维度的文档统一放在 `03_modules/` 下，
> AI 冷启动只需遍历一个目录树即可获得全量模块信息——无需在两个目录间跳转。
> 对标 Google Monorepo：同一项目的所有文档在一个目录树下，不按"B轨/C轨"分裂。

两轨之间的依赖方向受 `import-linter` 规则约束：
- C 轨内部：**逐层向下依赖**（L06 可依赖 L00-L05，不得反向）
- C 轨 → B 轨：**允许**（业务层可以调用平台能力）
- B 轨 → C 轨：**禁止**（平台能力不得反向依赖业务）
- B 轨内部：受 KBG-0019 `feedback_loop` 反转规则约束（见 KBG-0019 §3）

---
