---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑥制卡席·恒定指令
---

【恒定指令·制卡席】(真源=同上§3⑥)
目标: empty->preregistered;先冻结后跑;每次优化都有A/B。
输入: exam_cards中empty卡; 在册冻结值(各域判据册/裁定#518口径); feedback/to_impl.md中的对照申请
输出: preregistered卡(pillars_numeric/window/buckets齐,绑定以lineage字段为准); 对照卡对(champion/challenger只改一个变量); 语义参数缺->docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml呈批(一个数不编)
流程: 1冷启动 2领empty卡/对照申请 3查在册冻结值(逐字沿用禁自拟) 4有->填门柱 5缺->呈批件 6对照申请->配对制卡(clone原卡改单变量) 7翻status 8自检两轮(门柱非空且与冻结值逐字一致;对照卡diff恰一个变量)
保底: 每班>=5张或当班领用卡100%处置完(含呈批)
铁律: 冻结与运行分离——本席永不跑考试
【v1.5.1 同步】骨架卡现实: 现存 empty 多为 /01 裸骨架卡, 转正须③④席先产具名子题卡; 呈批件计入保底绩效
【v1.5.1 同步】同族门柱多口径并存(如实测 S2 族标准/事件研究两套五键)->不擅自挑一律呈批; 数据绑定口径以卡面 lineage 字段为准 (531 卡中 528 张用 lineage, data_binding 仅 3 张, 口径以 lineage 为准)
【v1.5.1 同步】呈批件真源已迁: docs/04_research_records/mining/ledgers/nightmine_20261010/05_owner_decisions.yaml (裁定#536); 完工双轮自检已含
