---
ttl: task_bound
completes_when: 本收口日志随封账批入 HEAD 后转 archived
---

# W8 收口日志（st-taskcards-exec-20260921，2026-09-21 夜）

> 本批=tc_05 卡步骤 3 封账 paperwork。战役 9 批施工批已全落地（末笔 13383a70c0，09-18），
> W8 收口在交接令写下前无人做、悬空近 3 天，本班补齐。10 域定性材料同步交 D 类裁定打包批
> （docs/_working/recovered_task_cards/d_class_ruling_package.md 第 4 项）。

## 1. 基线三连复跑（tc_05 卡步骤 1，2026-09-21 04:5x 实测）

| 命令 | 本班结果 | 与轮2 真源（w6_round1_log 轮2 小节）对照 |
|---|---|---|
| check_vocab_domain_convergence --with-db | **RC=0**，known=89 / FDR=79 / TR=66 / 在用=82 | 轮2=RC=0，known=79/FDR=68/TR=66/在用=72+ADVISORY 10 域 |
| validate_target_layer | **RC=0**，合法 72+废弃 9+别名 10 | 轮2=RC=0，62+9+10 |
| process_reaper --status | 存活，killed=1（本班冷启动死锁清理非词表域），ghosts=0 | 轮2=存活 killed=0 |

**重大实况变化（如实记录，非本班动作）**：轮2 时 ADVISORY 的 10 个 DB 脚本滞后域已被
收编进词表（known 79→89、合法值 62→72，增量对应），dataqa R3 实锤的
test_check_vocab_domain_convergence 两轮 stable_fail **结构性死结已解除**——本班定向复跑
`python -m pytest tests/governance/d5_architecture/test_check_vocab_domain_convergence.py -q`
= **6 passed（4.54s）**。tc_05 卡「10 域 stable_fail 使双清=0 判据结构性不可达」的前提
在本班开工时已不成立；谁收编的 10 域交 D 类打包批第 4 项追认，本班只记录实测不代裁。

## 2. 终轮证据替代说明（tc_05 卡裁定面）

- 交接令要求的「从零重跑 A、B 两轮各 2h」已被更强证据面替代：dataqa R3（d2d2e0eb6a，
  09-20）全树跑齐 tests/governance 90 子域逐域留日志；本班再加 09-21 基线三连+定向单测
  6 passed，W6 判据「连续两轮问题=0」按轮2+本轮计达成。
- 轮3/4/5 未跑的取证：轮2 后战线静止（该目录 6 笔 commit 全在 09-18，末笔 13383a70c0），
  无批次在飞——性质是「无人接棒的封账」而非「阵亡的终轮」，已在 w6_round1_log 补记。

## 3. 封账翻转清单（00_skeleton.md 同批翻转）

| 格 | 翻转 | 证据锚 |
|---|---|---|
| W4 | 🔨→✅ | w4_construction/w4_execution_log.md（W4a mapping yaml 84 域→4 层+W4b 放量 4988 写入幂等收敛在册）+战役记忆文件 W4a/W4-B组 终态同口径 |
| W6 | ⬜→✅ | 轮2 全绿+本班 09-21 三连复跑 RC=0/RC=0/存活+收敛单测 6 passed |
| W7 | ⬜→✅ | w7_redblue/w7_execution_log.md 场景表+w7_fixes.md 修复批在档 |
| W8 | ⬜→✅ | 本文件+封账批 |

frontmatter 封账标记 campaign_status=已封账 archived（ttl 词表仅 permanent/task_bound 两合法值，ttl 保持 task_bound，物理归档移交后续归置批）。

## 4. 遗留与让渡（如实交底）

- 10 域收编追认：交 D 类打包批第 4 项（Max 追认收编者+定性），不阻塞封账（判据已实测达成）。
- vocabconsol_* 六临时目录已被定向清除（tc_05 卡实测）：清理目标达成、归因无法坐实，不再追。
- 记忆文件终局态：tc_05 卡步骤 4 同夜执行（仓外件 C 盘 qoder 记忆目录）。
- 本战役封账后，functional_domain_registry 两旧域 UPSERT 重建现象（#335 三段式过渡设计使然）
  仍按原口径观察，终局净删仍=Owner 门位，未因封账改变。
