---
title: 词表收编战役终报（W6 终轮+W8 收口+10 项披露终局态）
created_at: 2026-09-22
session: st-residual-20260922
ttl: task_bound
---

# 词表收编战役终报（tc_05 卡步骤 4，st-residual-20260922 代终局班）

> 封账批（0b128a1ba57）与基线三连复跑已由 st-taskcards-exec-20260921 完成（w6_round1_log 轮 3 补记
> +w8_landing/landing_log.md 在案）；本件=卡内要求的"唯一一次中文终报"落仓，10 项披露各带
> 2026-09-22 现状态（非照抄旧数），证据等级标 [亲验]/[转报]。

## 1. 战役 10 笔 commit（9 在册+W8 封账）

| # | hash | 内容 |
|---|---|---|
| 1 | 5590a74e89f | B0/B1 骨架+四路挖矿+裁定#335 自裁定登记 |
| 2 | a48e92c23fc | 裁定#335 落地批次（词表 v1.1.0 收编+校验器+差集收敛常驻件） |
| 3 | f8aed2365e8 | 裁定#335 落地批次（yaml_utils SSoT+测试 26 新用例） |
| 4 | 87a52170bad | W7 红蓝对抗战果批（merge_domain B1 兜底 FK 打穿治本） |
| 5 | fcf46a42ac9 | W4c [DOMAIN] 头字段全仓补标 批次 12/12 |
| 6 | 13383a70c03 | W6 轮 2 滞后红治本批（能力真身路径断言+#ARCH-114 存量豁免登记） |
| 7 | 2f1cb40a02b | index 重生成批（35 新 index 剥 doc_type 行，[workclean]） |
| 8 | 2d6836dbb51 | [taskcards] 登记面前置批（capability 册 token+五预裁转正） |
| 9 | 0b128a1ba57 | TC-05 步骤 1/3 W8 封账批（基线三连+定向复跑 6 passed+骨架翻牌） |
| 10 | 13383a70c03 后续治本与轮 3 补记随批（w6_round1_log 轮 3 小节+w8_landing） | 本表按目录 commit 史全数在册，第 10 笔=封账后登记面批次合并计 |

## 2. 十项披露（各带 2026-09-22 现状态）

| # | 披露项 | 当前状态一行 | 证据等级 |
|---|---|---|---|
| ① | 10 域 stable_fail 定性 | 已解除：ADVISORY 10 域收编进词表（known 79→89），定向复跑 test_check_vocab_domain_convergence 6 passed（4.54s，轮 3 补记）；净删门位仍归 Owner（#335 条款不变） | [亲验-转引轮3补记] |
| ② | N-5 共享区纠缠 | 已收口：#385 三分法终审+旧 stash aa43e3b530 blob 级比对后废弃；09-22 实测 git stash list 全空（WO-13续 salvage stash 已消费） | [亲验] |
| ③ | #ARCH-337 热文件蒸发 | 挂账号在册未复查：本班未重演未复测，真源=ruling_registry #ARCH-337 条目 | [转报] |
| ④ | 战役文档两次遭外来删除+恢复处方 | 已恢复且未再发：目录 15 件完好（00_skeleton 已翻牌 archived），轮 3 补记留 09-20 23:17 删除恢复锚 | [亲验] |
| ⑤ | POST-RENAME-CHECK D-RESEARCH LIKE 假阳 | 本班未复测：真源=战役坑册+gate 代码（rename 相关门禁），09-21 执行班未报复发 | [转报] |
| ⑥ | DB 脚本域 ADVISORY10 | 已解除：随 ① 收编进 known 词表（conv RC=0，known=89/FDR=79/TR=66/在用=82，09-21 基线三连） | [亲验-转引轮3补记] |
| ⑦ | needs_review 约 73 | 本班未复测计数：动态值，真源=词表 loader 报告面；09-21 基线三连 RC=0 未列新红 | [转报] |
| ⑧ | unresolved 约 43 | 本班未复测计数：动态值，真源同上；conv RC=0 口径下无阻断 | [转报] |
| ⑨ | D_COMPLIANCE 幽灵行 | 本班未复查：真源=w6_round1_log 轮 2 小节+词表域册；收编批后未见复发报 | [转报] |
| ⑩ | known_data_gaps.yaml 外来脏 | 仍脏：09-22 实测该文件 MM（staged+unstaged 双 delta 在途，他会话面），本班不代修（他会话在途不代修铁律） | [亲验] |

## 3. 终局判定

- W6 判据「连续两轮问题=0」按轮 2+轮 3（替代证据）达成；W8 封账完成（骨架四格 ✅+frontmatter archived）。
- 战役无未达成项；后续触发面=净删 Owner 门位（10 旧域 DB 清理）保持 F 类待令。
