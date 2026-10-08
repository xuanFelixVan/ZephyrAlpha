---
created: 2026-10-08
chief: st-acure-m1
ttl: task_bound
completes_when: C129 原件三 blob 捞回归位（并列+交叉注记）且交付报告 C129 行改判落 HEAD 后归档
---

# P0-8 施工卡 · C129 原件可捞回而未捞回 → E 勘误道

## ① 卡面处方（审计原文锚点）

总报告 §三 P0-8 + lane_f P0-F1：C129"考古交付报告重建"标 DONE（交付报告 L48 `| C129 | L4 | DONE | 考古交付报告重建 |`），但原 §十七..廿八 12 节实录以 3 个悬挂 blob 实存 object DB（`cat-file` 即可整卷捞回）；HEAD 831a35b30ab 重建版同号节主题完全不同（S 簿索引顶替事件实录）；重建版 §廿七自诺"考古后以原件为准替换本纲要节"未履行。处方=`git cat-file blob d5e61426e985…` 捞回原件，按 §廿七承诺以原件为准替换**或并列+交叉注记**（lane_f P1-1：原件与重建节主题不同，宜并列）；C129 行改判。

## ② HEAD 现状实证（挖矿时点新鲜复跑，HEAD=f82008eb25）

- 三悬挂 blob 现存核验：`git cat-file -e` → **d5e61426e985（634 行 52013B）/ b0c4b9e7fb52（641 行 51834B）/ e03473fff431（633 行 51820B）全部 EXISTS**——捞回处方前提完好。
- 交付报告 L48 C129 DONE 行原位未动；`docs/_working/fms_overhaul/99_delivery_report.md` HEAD=315 行重建版（831a35b30ab 落），240 行版止 §十六 系 5306c714c3d 自然终态。

## ③ 上游依赖

无外部上游（blob 在库即凭据）。捞回产物落 docs/_working/fms_overhaul/ 时注意 CREATE-GUARD（新 .md 须 token——走 batch_creation_tokens 或并入 E 道批）。

## ④ 下游消费者

- C473/C61"蒸发族"方法论面：本卡捞回是"蒸发族结论设机械前置（object DB 全量扫描必备）"P2 建议的实例面。
- fms_overhaul 战役史完整性；晨会考古移交项 4（workbook 移交清单）。

## ⑤ 冲突面

fms_overhaul/99_delivery_report.md 今夜无他会话在途（git status 干净）；并列方案=新文件（原件 §十七..廿八 单独成卷+交叉注记）优于原地拼接——原地拼接易与重建版行号/引用面冲突。

## ⑥ 残余与移交

- 采"并列+交叉注记"时在重建版 §廿七补一行"原件已捞回：见 <新件路径>（blob d5e61426e985），替换承诺履行为并列"；交付报告 C129 行 DONE 改"已完成（原件捞回归位+并列）"。
- 三 blob 中以 d5e61426e985 为准（最新、含 GATE-SELFDOC 豁免头=09-28 后产物，lane_f E1）；另两 blob 在卷注记留哈希备查。

## 自审闸三态

**GREEN（挖干）**——cat-file 即捞，字节在库实证，处方零歧义。
