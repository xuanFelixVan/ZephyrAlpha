---
card_id: TC-05
title: 词表收编战役收尾（W6 终轮 + W8 收口 + 清理终报）
verdict: 部分存活已变形（置信度高：W8 收口批零落地；2×2h 终轮重跑已被 dataqa R3 更强证据面替代；10 域 stable_fail 使"双清=0"判据结构性不可达，需先裁定定性）
category: C类-文书收口批 + D类裁定项
priority: P1
size: 中（裁定后半天内可闭）
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 461-502 行（"五："节）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-05 词表收编战役收尾

## 0. 一句话结论

原会话 9 批战役 commit 全部落地（至 13383a70c0），但死在最后一公里：W8 收口批（纯 paperwork）在交接令写下前就没做，之后近 3 天无人接棒。原文要求的"从零重跑 A、B 两轮各 2h"已被更强的替代证据面覆盖（dataqa R3 于 09-20 全树跑齐 tests/governance 90 子域、65,311 passed），**盲跑不必再做**；真正的活=一次分钟级基线三连复跑 + 10 个词表滞后域的 stable 红定性（需 Max 裁定+Owner 门位）+ W8 封账 paperwork + 记忆文件终局态。清理项（vocabconsol_* 六目录）已被定向清除，claim 已清。

## 1. 背景与来龙去脉

词表收编战役（st-vocabconsol-20260918）完成 9 批落地后，交接令要求三件事：任务 1=W6 终轮全量扫描两轮双清（旧轮 4/轮 5 日志被外来清理吞没，无留存红证）；任务 2=W8 收口批（补记留痕+封账翻转+提交）；任务 3=清理临时件+释放 claim+更新记忆文件+唯一一次中文终报。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 骨架目录 15 件完好 | 存在，递归口径 15/15 个文件在盘，git status 该目录零漂移（历史上两次遭外来删除均已恢复） | find -type f + porcelain | A |
| w6_round1_log.md 末尾有终轮小节 | **没有**：docs/_working/2026-09-18_vocab_consolidation_campaign/w6_loop_check/w6_round1_log.md 全文 55 行仅轮 1+轮 2；grep 终轮/阵亡/重跑零命中；.runtime 无 vocabconsol_final*.log（终轮没跑过） | wc -l + grep | A |
| w8_landing/ 存在 | **不存在**（盘上与 HEAD ls-tree 均无） | ls + git ls-tree | A |
| 00_skeleton 第 2 节 W4/W6/W7/W8 翻状态 | **原样**：W4=🔨、W6/W7/W8=⬜；批次志仅 B0/B1/B2；frontmatter 第 3 行仍=完成条件"封账提交后转 archived" | Read 00_skeleton.md:3,36-40 | A |
| 近 3 天 W8 封账批 | 0 笔：该目录全部 6 笔 commit 全在 09-18，末笔=13383a70c0（轮 2 治本批） | git log --all 该目录 | A |
| 六个 vocabconsol_* 临时目录+日志 | **全没了**（.runtime/tmp 其他会话件存活=vocabconsol 件系被定向清除，非整体清扫；清理目标事实上已达成，归因无法坐实） | find .runtime | A/C |
| st-vocabconsol claim 已清 | 已清：lock_files.py list 141 锁零匹配 | python scripts/lock_files.py list | A |
| 战役记忆文件已更新终局态 | **从未更新**：mtime=2026-09-18 16:25，内容停在"轮 5 在飞、W8 收口在望" | stat + Read | A |
| 轮 2 对照真源完好 | 完好：w6_round1_log.md:29-34 完整在档（conv RC=0 79/68/66/72+ADVISORY10、validate_target_layer RC=0 62+9+10、reaper killed=0），将来复跑对照可用 | Read | A |

### 病根

1. **结构性死结**：dataqa R3 的 flaky 复跑日志实锤 test_check_vocab_domain_convergence 两轮 stable_fail，根源=10 个词表滞后域（D_ARCHIVE_SCRIPTS/D_ARCH_GUARD/D_ARCH_SCRIPTS/D_CODE_SCRIPTS/D_COMPLIANCE_SCRIPTS/D_DATA_SCRIPTS/D_META_SCRIPTS/D_SEC_SCRIPTS/D_STRUCT_SCRIPTS/D_TEST）——这是战役自己按 #335 设计声明"终局净删=Owner 门位"留给 Owner 的过渡态。战役把净删设为 Owner 门位的同时把"双清=问题 0"设为自己的完成判据，两者在旧域清理前互斥——交接令 v2 未察觉这一点。
2. 原会话死于最后一公里：9 批全落地但 W8 封账（纯 paperwork）无人做，交接令发出前 27 小时战线就已静止。
3. dataqa R3（d2d2e0eb6a，09-20，HEAD 祖先）已把 tests/governance 90 子域全部跑齐并逐域留日志（.runtime/tmp/dataqa/pytest/），比 2×2h 盲跑更严格——重跑的主要价值已被替代。

## 3. 上下游

- 前置依赖：裁定 #335（净删门位条款）；dataqa R3 报告与 flaky 日志；w6_round1_log.md 轮 2 真源。
- 下游消费方：Owner（净删门位+终报接收）；conv 校验器的全体消费方（基线数字变更需同步判读口径）；骨架 frontmatter ttl:task_bound——封账后须转 archived，否则会被当作活任务继续被考古。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 1 | 基线三连复跑（分钟级，禁跑 2h 全量）：conv 校验器 check_vocab_domain_convergence --with-db、validate_target_layer、process_reaper --status | 三条命令输出 | 与 w6_round1_log.md:32-34 轮 2 真源对照如实记录（预期 conv 挂 10 域） | Flash |
| 2 | 10 域 stable 红定性（本案活着的核心）：证据=.runtime/tmp/dataqa/pytest_flaky/ 下 r1/r2 两轮日志 + #335 + functional_domain_registry，两选一呈报：登记 known-transitional 豁免/ADVISORY 化（需裁定）或 DB 旧域净删（Owner 门位） | ruling_registry、functional_domain_registry | Max 裁定号登记；Owner 门位签署（若走净删） | Max 裁定，Owner 门位 |
| 3 | W8 收口批：w6_round1_log.md 末尾追加"轮 3/4/5 阵亡取证+终轮证据替代说明"小节（引 dataqa R3 替代证据）；新建 w8_landing/ 收口日志；00_skeleton.md 第 2 节翻 W4/W6/W7/W8（注意 W4 行停在 🔨 而记忆称已完成，一并修正）；frontmatter 落"已封账 archived"；批次志加 B3 行 | docs/_working/2026-09-18_vocab_consolidation_campaign/ 全目录 | git log -1 --name-only 归属只含本批；porcelain 回归 0；提交必经 git_commit.py --enqueue | Flash |
| 4 | 记忆文件更新终局态 + 唯一一次中文终报（含 10 域定性结论如实呈报） | C:\Users\fanzi\.qoder-cn\projects\D--ZephyrAlpha\memory\vocab-consolidation-campaign-20260918.md | mtime 更新；终局态含定性结论 | Flash |
| 5 | （仅当 Max 仍要正式终轮）单轮定向扫描而非两轮——dataqa R3 已充当第二轮证据 | tests/governance 相关子域 | 0 FAILED 或全部定性 | Flash |

## 5. 与其他任务卡的关系

- **TC-09 任务三"W6 记忆文档 A/B 班"是另一个 W6**（AGENTS.md 宪法 A/B 测试），与本卡的"W6 终轮扫描"无关——两卡都要写终态报告但落点不同不冲突。
- TC-04：dataqa R3 中 test_externalize_algo_flow_mirror stable_fail 属 TC-04 域，本卡勿顺手修。
- TC-03/TC-08：共享 .runtime/tmp 卫生经验；本卡的"清理已被定向完成"说明 tmp 有活跃清扫者——TC-01 的输入件保护更紧迫。

## 6. 风险与避让红线

1. 主区 ~780 脏条目在途：W8 批提交务必 --enqueue + 提交后核归属。
2. 战役目录历史两次遭外来删除：落批前再 porcelain 复核；热文件写必经 safe_write_text。
3. dataqa R3 数字是 09-20 时点，09-21 凌晨 HEAD 又前进数笔：基线对照勿机械等值，以"在册现象可解释"为准。
4. 封账前骨架被当作活任务：做完步骤 3 才算真正闭案，勿只做步骤 1/2 就收工。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；conv 校验器与 validate_target_layer 的调用方式见 w6_round1_log.md 轮 2 小节的命令记录；禁跑全量 pytest（要跑也只跑单文件定向）。
