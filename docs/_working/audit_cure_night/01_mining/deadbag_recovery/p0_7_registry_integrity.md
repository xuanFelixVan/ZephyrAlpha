---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: 翻译册 4 幽灵条目随本体落地消除（或显式退役注记）且 token 册 3 悬空 token 处置定谳后归档
---

# P0-7 施工卡 · HEAD 注册表完整性缺陷 → R 恢复道（随 P0-1）+撤号面呈报

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-7：HEAD module_translation_registry L67723-67747 四条幽灵模块条目（tech_factor_pipeline/event_axis/swing_sequence/resonance_pair，指向不存在的 .py）+capability 册 3 条悬空 token（quant 07/08/12）。处方=随死袋清偿自然消除，或显式退役注记/撤号；**禁止 loader 全量扫描面长期带断链**。lane_c P0-1.2 补充：4 条目由 45c1f0b224（l6 docs 袋"翻译册对齐"）落地，与 TRANSLATION-COVERAGE 门"新建 .py 须登记"构成镜像漏洞（登记-本体倒挂）；lane_h H-P0-2：3 悬空 token 为纯编号美学预登（b0fe4b5940"token 先行"），撤号=内收判据②正解，主题命名/撤号=Owner。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git show HEAD:docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -n` 四 module_path → **L67723 tech_factor_pipeline / L67731 event_axis / L67739 swing_sequence / L67747 resonance_pair，行号与审计零漂移**（今夜 895b535843 G2、a92886e31d st-mx07-L3 两笔触及该册但插入在别区段）。
- `git show HEAD:docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml | grep -n placeholder` → **L45511/45516/45521 三 token 在**（审计引 L45510/45515/45520，+1 行漂移，条目本体未动）。
- 四 .py 路径 `git ls-tree -r HEAD` 零命中（同 P0-1 核查）。

## ③ 上游依赖

**P0-1 死袋清偿**：三模块+tech_factor 落地则 4 幽灵条目即时转真；C452 三册落地则 3 悬空 token 即时转真。反向（R 道改判不落地）则须显式退役注记/撤号。

## ④ 下游消费者

- 任何 loader 全量扫描/TRANSLATION-COVERAGE 复核/模块翻译三层 loader（AGENTS §8 术语三层）。
- capability 册消费方（CREATE-GUARD token 校验读该册）。

## ⑤ 冲突面

两册今夜均为他会话 stomper 在飞（git status 双 M）——**R 道写册必 safe_write_text CAS+写后进程外复核**；若 P0-1 落地袋与他会话注册表袋撞车，走队列串行。

## ⑥ 残余与移交

- 撤号路径：token 册条目撤号=Owner 门位面（lane_h 明示"撤号=Owner"）——若 C452 选择不落三册，R 道登记呈报不代裁。
- 退役注记路径：不撤号时在条目旁加 `deprecated: 本体全史未落地，见死袋 qid` 显式注记，消除静默断链。

## 自审闸三态

**GREEN（挖干，清偿面）+RED（登记，撤号面）**——清偿路径随 P0-1 即行；若 P0-1 改判不落地，撤号呈 Owner，禁静默保留断链。
