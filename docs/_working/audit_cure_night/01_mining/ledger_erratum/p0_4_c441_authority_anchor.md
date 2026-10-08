---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: 交付报告 C441 行/§八 B 段清单勘误落 HEAD 且裁定册侧（#490 C 段）落 HEAD 后归档
---

# P0-4 施工卡 · C441 授权锚断链+机制互串 → E 勘误道（裁定册侧=chief #490）

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-4 + lane_e P0-E1 + lane_g P0-5：交付报告 L135 标 `C441 | DONE | #488 B 段：词表门判据已改写（BLOCK_FLIP_CLEAN_STREAK=20）批准翻转`、L148 B 段清单含同款——但在册 #488 B 段无 C441 分项；且 BLOCK_FLIP_CLEAN_STREAK 是 C27 的 FMS-HYGIENE 判据（fms_hygiene_gate.py:119），词表门本体 tag_vocab_gate.py TAG_VOCAB_GATE_MODE="warn" 零 streak 机制；"批准翻转"预授权 flag 出厂翻转踩宪法 §5。处方=勘误裁定（补记或撤回引用改"待裁"）+机制条目按词表门真身重写；**补记前禁任何 block 翻转**。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- `git show HEAD:.../99_delivery/交付报告.md | grep -n C441` → **L135 DONE 行+L148 B 段清单行原位**（今夜未被更新）。
- `git show HEAD:.../ruling_registry.yaml` L4242-4274（#488）grep C441 → 零命中（断链仍在 HEAD）。
- **新鲜度关键发现**：裁定 **#490 已写入工作区** ruling_registry.yaml L4312（git 态 ` M` 未 staged），其 **C 段**恰为本卡处方文本："(1) 判据属 C27 的 FMS-HYGIENE 门，词表门本体无 streak 机制；(2) '批准翻转'表述撤回：mode 翻转仍=OWNER-GATE，任何 block 翻转须 Owner 单项裁定"——**裁定侧处方已由 chief 就位，落 HEAD 归 chief（M 道不代提交）**。

## ③ 上游依赖

- 裁定册侧：#490 C 段落 HEAD（chief 在途）。
- 报告侧（L135/L148 勘误）：上游=#490 落册后引用才不悬空——若 #490 未落 HEAD 前 E 道先行改报告，引用写"裁定#490（ Chief 在途落册中）"须与实际时点自洽；稳妥序=等 #490 落 HEAD 后同窗勘误报告。

## ④ 下游消费者

- G 道桌面 C441 注记更正（P0-6 附带面："已批未翻"→"翻档权明示 Owner"）。
- 晨会读数/战役树归档；C27 注记（P1⑥ 同一机制面）。

## ⑤ 冲突面

ruling_registry.yaml 是 chief 在途写面（` M`）——**禁碰、禁代提交**；交付报告今夜无他会话在途，报告侧勘误由 E 道 claim。gate 侧（fms_hygiene_gate.py/tag_vocab_gate.py）本卡零触碰（机制描述勘误只在文档面）。

## ⑥ 残余与移交

- "补记前禁任何 block 翻转"红线随 #490 C 段生效——运行时无翻转路径（lane_b §5 已证零自动翻转代码），残余=禁令登记在桌面注记+裁定册双面。
- C441 连零读数统一（册面 0/20 vs 2/20，lane_g P2）随注记更正并案。

## 自审闸三态

**GREEN（报告侧勘误，待 #490 落 HEAD 后即行）+WAIT（裁定册侧=chief 上游）**。
