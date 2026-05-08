---
module_id: KE-module_blu-3_9_doom_loop___________v0_6_0-000
title: 3.9 Doom Loop 防护与修复升级阶梯（v0.6.0 新增 — Wave 2 落地）
category: module_blueprint
---

# 3.9 Doom Loop 防护与修复升级阶梯（v0.6.0 新增 — Wave 2 落地）

3.9 Doom Loop 防护与修复升级阶梯（v0.6.0 新增 — Wave 2 落地）

**核心问题**：Vibe Coding 项目有一个已知的"末日循环"——每次 AI 修复创造 1 个新问题 + 打碎 1 个旧功能。如果去重引擎的自动修复也触发了这个模式，后果是灾难性的。
业界研究证实了 4 个加剧因子：Context Rot（32K tokens → 50%性能下降）、Non-determinism（相同 prompt → 不同代码，方差可达 70%）、No Blast Radius（AI 改代码无依赖图）、Symptom Patching（修症状不修根源）。

**Doom Loop 在去重场景下的具体表现**：
  1. auto_fixer 提取函数到 shared
  2. verifier.py 测试失败
  3. AI 尝试修复 import/引用问题
  4. 修复导致 3 个新文件 break
  5. 尝试修复新的 breakage
  6. 原始 shared 函数又被无意改动
  7. 循环...

**修复升级阶梯（Fix Escalation Ladder）**：
去重引擎不是"修 or 不修"的二元选择——顶尖设计需要阶梯式响应。

| 阶梯 | 条件 | 动作 | 触发下一阶梯条件 |
|:---:|------|------|------|
| **L0: Direct Fix** | suitability ≥ 70 + similarity ≥ 0.95 + pure function | 自动提取→替换→行为采样验证（Stage 0.25）→通过 | — |
| **L1: Partial Fix** | L0 失败 or suitability 40-69 or 有副作用 | 只提取 LCS 公共核心（partial_extraction）→ 保留差异→验证 | 行为采样 pass + import 无循环依赖 |
| **L2: Retry Once** | L1 失败 + 失败原因为 import/引用问题 | 回滚 L1 → 分析失败原因 → 修正 → 重新尝试 partial fix | — |
| **L3: Escalate** | L2 失败 or 是第二次尝试该 DUP group | 回滚全部 → 生成详细失败分析报告 → 写入 Session Log → 标记 needs_review → **分配 TaskCard DEDUP-REVIEW-{N}** | — |
| **L4: Stop + Alert** | 任何 DUP group 在 24h 内被尝试修复 ≥3 次 | **冻结该 DUP group**（加入 `doom_loop_freeze_list.json`）→ 告警写入 Session Log → 生成"为什么修不好"的分析报告 → **需要 Owner 手动解除冻结** | Owner 手动 1 次性解除 |

```yaml
