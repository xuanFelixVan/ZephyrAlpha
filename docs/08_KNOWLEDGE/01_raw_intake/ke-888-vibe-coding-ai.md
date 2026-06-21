---
module_id: KE-810
status: active
title: 2.2 Vibe Coding AI 检索策略映射
category: governance_rule
---

# 2.2 Vibe Coding AI 检索策略映射

2.2 Vibe Coding AI 检索策略映射

五维分类定义了"AI 怎么理解规则"，但 Vibe Coding AI 实际施工时需要"怎么找到规则"。以下是 Vibe Coding AI 从查询意图到分类维度的检索路径：

| AI 查询意图 | 检索路径 | 解释 |
|-----------|---------|------|
| "文件操作的禁止行为有哪些" | ① domain=document → ② stability=frozen→stable→evolving → ③ 优先读 PS-STD-003（SSoT） | 先定位领域 → 按稳定性排序（冻结文件权威性最高）→ 先读 SSoT |
| "某个模块的编码规则变更要走什么审批" | ① scope=module→domain → ② stability 维度 → ③ 查看 PS-STD-009 变更门控 | 自底向上：模块→领域→全局 |
| "AI 可以自主修改哪些文件" | ① executor=ai_modifiable → ② stability 不为 frozen → ③ layer 可写 | AI 自治权限的"可修改范围"由 Executor 维度直接筛选 |
| "当前项目所有规则文件有哪些" | ① layer=cross_layer → L1 → L2 → L3 → ② domain 分组 | 层级影响范围大头优先：全局规则 → 领域规则 → 会话规则 → 模块规则 |
| "这条规则和哪条有冲突" | ① scope 相同 → ② stability 是否矛盾 → ③ 见 §9 冲突裁决推导链 | 作用范围相同的规则最可能冲突，不同 scope 互不干扰 |

**检索原则**（按优先级排序）：
1. **SSoT 优先**：如果有 SSoT 文件声明了该领域（如 PS-STD-003 声明行为边界），先读 SSoT 再查领域规则
2. **稳定性过滤**：`frozen` 文件优先于 `stable` 优先于 `evolving`——冻结内容的权威性最高
3. **层级收敛**：`cross_layer` → `L1` → `L2` → `L3`——范围大的先读，在理解全局约束后再看局部
4. **领域隔离**：不同 `domain` 的规则互不冲突（如 `document` 领域的规则不会和 `vibe_coding` 领域的规则打架），冲突仅在同 domain 或 scope 重叠时发生


---
