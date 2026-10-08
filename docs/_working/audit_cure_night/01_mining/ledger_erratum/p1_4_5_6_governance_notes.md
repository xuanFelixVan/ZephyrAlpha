---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: P1④⑤⑥ 三项台账/注记勘误落 HEAD 后归档
---

# P1④⑤⑥ 合并施工卡 · 治理台账注记三修 → E 勘误道

## ① 卡面处方（审计原文锚点）

- **P1④ C61 GREEN 残留回改**（总报告 §四 P1④；lane_f P1-F2/E4）：01_skeleton/05_block_governance_gates.md L113 载 `| C61 | L4 | **GREEN** | 叶册 22 本 token 批落地（chief7_docs_staging 车道字节在 .aidrafts/st-chief7-20260928） |`，与交付报告 L47 `| C61 | L4 | OWNER | 22 本叶册字节蒸发（0/22 捞回）：重建或撤卡待 Owner 定 |` 互斥——L113 回改 OWNER 态与交付报告对齐。
- **P1⑤ C61 升 ⏳+C78 转 ❌**（总报告 §四 P1⑤/§五；lane_g 重点 13 卡表）：C61 余下动作纯 Owner（重建或撤卡）→⏳；C78 施工令已签发（#431⑤，15_evaporation_cure_plan.md EV-03/05/06 行在 HEAD）→❌ 施工。附 lane_g P2：C61 分母 qid 级清单附录化（"0/22"的 22 目前不可独立复算）。
- **P1⑥ C27/C441 注记更正**（总报告 §四 P1⑥；lane_g P0-5）：C27 注记"达标自动翻 block"失真（资格函数 block_flip_eligible 零调用零测试，翻档=Owner 手动一行）→改"翻档=Owner 手动；资格函数未接线"；C441 注记机制互串同款更正（详见 P0-4 卡）。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git show HEAD:docs/_working/master_tc_night/01_skeleton/05_block_governance_gates.md | sed -n '113p'` → **GREEN 残留原位**。
- 交付报告 L47 C61 OWNER 行原位（对齐目标有效）；C78 行/lane_g 证据链今夜未动。
- C27 判据面：fms_hygiene_gate.py 零改动今夜（资格函数零消费面不变）。

## ③ 上游依赖

- P1⑤/⑥ 无硬上游（改判依据=交付报告 L47+#431⑤ 在册）。
- C441 注记更正与 P0-4 报告侧同窗（引用 #490 C 段文本）。

## ④ 下游消费者

- G 道桌面注记（桌面 C61/C78/C27/C441 行按 E 道改判口径同步，P0-6 二波）。
- 132 表状态轴一致性（00_环节总表 C61 行如有同款残留一并查）——挖矿复核：环节总表 L97/98/101 为 G 标失真三行（C452/C107/C233，归 P0-1/E 道改判面），C61 在环节总表行无 GREEN 残留（残留仅在 05_block 文件）。

## ⑤ 冲突面

01_skeleton/ 六 block 文件缺 completes_when（lane_h E17）——本卡改 L113 时**顺带补 frontmatter completes_when**（随归档批补齐义务的前置单点）；05_block 文件今夜无他会话在途。

## ⑥ 残余与移交

- C61 分母 qid 级清单附录化（lane_f P2-5）：22 本叶册的 102 袋枚举+1651 死袋扫描读数附录入 workbook——E 道如本夜不可得，登记移交归档批。
- C27 资格函数补最小单测+读数出口（lane_b P1-3，读数进既有审计面禁 cron）——登记移交，非本卡施工面。

## 自审闸三态

**GREEN（挖干）**——三处均为单点注记/状态改判，证据链已三面互证。
