---
ttl: task_bound
title: L06 策略考试与条件共振上岗 — 挖矿子模块总勾表 + 本环节穷尽性声明
created: 2026-09-25
sid: st-qmine-20260925
lane: L06_exam_alloc
status: COMPLETE（5 子模块 MINE 全落盘，六向全填，自审闸三态齐）
skeleton_source: ./SKEL.md（八子块）；../09_link_skeletons.md 环节6；判据 ../17_quantified_acceptance.md §一/§二
---

# L06 挖矿 · 子模块总勾表（本环节穷尽性声明）

> 本班把 SKEL 八子块（L06-A~H）MECE 收成 **5 个挖矿子模块**（含任务令点名的"考试结果回写面"新独立块），
> 每块产出 `<slug>/MINE.md` 六项齐全。目录名均小写下划线、不以数字结尾（R5 门禁）。

## 一、子模块切分（MECE，对 SKEL 八块的映射）

| 子模块 slug | 覆盖 SKEL 块 | 一句话职责 |
|---|---|---|
| `exam_result_writeback` | 新独立块（SKEL 仅 IBT-E01 侧提及） | 考试结果落库面：生命周期 outcome 列 vs conclusion JSONB 裁决键双写、三态桶消费、追加不改史 |
| `search_executor_prereg` | L06-A + L06-B | 网格执行器粗扫→晋级 + prereg 冻结/n_trial/DSR 预注册防线 |
| `exam_ruler_holdout` | L06-C + L06-D | E4 三阶段三线裁决 + 三道成本门 + 条件轴输入包 + HOLDOUT 四窗闭卷 |
| `onboarding_rules_matrix` | L06-E | 成绩单→上岗规则 v1（稿已备待追认）+ state_matrix 六空格填报 + 路由三级 |
| `resonance_friction_assembly` | L06-F + L06-G + L06-H | r 态→六段共振判定 + 切换摩擦（滞回/mSPRT/任职期）+ E8 组合装配 |

## 二、六向×子模块总勾表（每向内部反查+外部双动作完成度）

| 子模块 | ①上游 | ②下游 | ③算法/机制 | ④后端 | ⑤前端 | ⑥数据字段 | 自审闸三态 | 新立缺口 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|---|---|
| exam_result_writeback | ✓ | ✓（读端坐实 build_closure_ledger+redblue R2/R4） | ✓（event-sourcing 双源） | ✓ | 查无 | ✓ | 施工 C11 / 挂起 C12·E01·C13 | C11 C12 C13 |
| search_executor_prereg | ✓ | ✓ | ✓（PIT+18 号文号族） | ✓ | 查无 | ✓（成本列待核） | 施工 LK-08 / 挂起 LK-11·C16·C17 | C16 C17 |
| exam_ruler_holdout | ✓ | ✓ | ✓（PIT/WFE 双源） | ✓ | 查无 | ✓（冰点 0 日/板块 17 日） | 施工 C18·F02 / 挂起 F01·E01·C19 | C18 C19 |
| onboarding_rules_matrix | ✓ | ✓（虚挂坐实） | ✓（meta-labeling+regime 双源） | ✓ | 查无 | ✓ | 挂起 LK-10·D30·D31 / 施工 LK-16 | 无新立（沿用） |
| resonance_friction_assembly | ✓ | ✓ | ✓（regime-switching 双源） | ✓ | 查无 | ✓（euphoria/distribution 无源） | 挂起 C01·IBT-C01 / 施工 LK-16 | C14 C15 |

（✓=内部反查+外部双动作均有 ≥1 发现；"查无"=该向已查且如实记无物/边界，非未挖。）

## 三、自审闸三态总表（mining_sop §6，量尺=终局全貌）

- **无一块封矿**：五块终局皆有位置（考试→成绩单→上岗是全链咽喉）；"缺位/零样本/挂起"全部是
  **时序未到 + Owner 门位 + 数据前置**，非"现状规模小"（禁以此封矿，宪法/挖矿 SOP §6）。
- **施工级**（可起手、不等门位）：L06-C11（旁路收口）、L06-C18（WFA 补二维）、IBT-F02（窗口状态账本）、LK-16（映射常量入 plan_engine，六段分叉修复已批开工）。
- **挂起排期级**（解锁条件明确）：LK-10/D30/D31（Owner 门位 + 成绩单出档，明晚完赛）、IBT-E01/C12（考卷结构化冻结）、L06-C16（prereg 预算重排=裁定门位，只登记不擅改）、LK-11（GPU 空窗 + LANE-RB 收口，不碰其路径）、IBT-C01/C02（批 D 新名单+成绩单驱动，预注册留白非遗漏）。

## 四、本环节穷尽性声明

> **判据（挖矿 SOP §3 矿脉枯竭结构判据）**：当前母节点六向全部见底或如实"查无"，且长尾清单无未挖主脉，才算穷尽。

1. **已挖见底**：SKEL 八块全部覆盖（并入本 5 子模块），任务令点名四块事实均实测复核——
   (a) 上岗=配置矩阵非 TDM 节点（照"独立环节"挖，onboarding 块）；
   (b) 上岗规则 v1 稿已备待追认（19 号文 C3/F3 实测坐实，纠正 SKEL 旧判 LK-10"未立"）；
   (c) euphoria/distribution 无 r 态来源（framework_composer.py:151-152 逐键实证）；
   (d) **考试结果回写面**三处结构级漏洞坐实（旁路 record_exam_result / 合法入口裁决键空串 / 写时无兜底检测滞后），读端已定位。
2. **新立缺口 8 条**（均注"册内未见"）：L06-C11/C12/C13/C14/C15/C16/C17/C18/C19——
   覆盖回写旁路、裁决键空串、检测滞后、mSPRT 成交流虚挂、防御档空洞、prereg 预算 5.2× 背离、
   manifest 成本列 schema、WFA 三维仅一维、条件轴二维数据不可得。
3. **残余长尾（非未挖主脉，属施工/邻链）**：
   - T1 完赛成绩单实样验收（明晚后，随 LANE-AUTO/RB，本块不碰）；
   - Owner 批后 config/plan_engine 实际落地（施工域）；
   - mSPRT 成交流契约（属执行链 L07）；DU 数据面补冰点/板块源（属数据链）。
   以上均为**跨链/时序前置**，非 L06 环节内未探矿脉。
4. **外部纪律核**：所有外部论断带 URL+发布方+年份（arXiv 2406.09578/MDPI 2227-7390/微软 Azure event-sourcing/CODE Magazine/LdP meta-labeling/SKEL §9 件族）；判据族（Harvey-Liu 2015/Bailey-LdP 2014/Bailey 2017/Nefedov 2025）锚定 18 号文 §四在册题录，Nefedov 精确 SSRN 本轮未独立复现已如实标"未复核不伪造"；关键结论均 ≥2 源；A 股适配闸逐块过（T+1/涨跌停/成本五档/无做空）。
5. **结论**：L06 环节六向见底、长尾清空至跨链前置——**本环节挖矿判定穷尽（各子模块见底，无一封矿，缺口全立卡）**。
   深读尾差随施工消化（承 SKEL §7：f06 折切纯函数区全文 / DSR V[SR] 公式区 / mSPRT calibrate_tau）。

## 五、待落清单指针
本车道交付登记于 `../../cmd_successor_20260925/landing/lane_mine_l06.yaml`（全程禁 git，落地经 LANE-LAND 单出口）。
