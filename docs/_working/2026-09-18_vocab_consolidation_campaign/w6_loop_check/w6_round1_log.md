---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W6 循环检查日志（判据：连续两轮 问题=0）

## 轮1（进行中，2026-09-18 晨）

| 项 | 结果 | 备注 |
|----|------|------|
| tests/governance/d5_architecture + commit_gates | 2553 passed | gate 编辑前基线 |
| tests/git + tests/governance/d3_metadata | 460 passed + 1 xpassed | 含新迁移回归 3 件 |
| test_check_vocab_hardcode | 首跑 1 红 → 治本后 23 passed | 红因=noqa 豁免表两处行号漂移（battlemap_schema 187→127 algo-flow 出仓批致移；verify_g07 64→63），非战役引入；按 W5 行号漂移跟进惯例修 |
| check_vocab_domain_convergence --with-db | RC=0 | 三源差集收敛；advisory 10 DB 脚本域在册（W8 汇报项） |
| validate_target_layer | RC=0 | |
| process_reaper --status | 存活 | last_run 00:44 killed=0 |
| --sync-layer 幂等复核 | 写入 0 / 未变 4988 | 收敛 |
| tests/governance 全量 | 待重跑 | 首跑被 `-p no:cacheprovider` 与 ini cache_dir 冲突 INTERNALERROR（操作失误，已识别非项目问题），串行惯例重跑中 |
| depgraph drift | 并入落地侧门禁观测 | 无独立 --check 入口；队列落地 commit 若漂移交回即暴露（W8 核验 name-only 归属） |

## 队列实况（轮1期间）

- 0001-0003 dead→requeue→0005-0007 再 dead（CREATE-GUARD 读落地侧 HEAD 版注册表，token 须先行入库=新坑，入 memory）；
  0007 另有 VOCAB-CHAIN 拦新增校验器（d5 validators 目录补入既有豁免面，对齐注释中"检查器"既定意图）。
- 1686 补标 12 块 = 0008-0019 全部入袋；token/issue/noqa 三注册表批 = 0020 入袋（FIFO 在 0019 后）。
- 处方：0020 落地后 requeue 0005/0006/0019；VOCAB-CHAIN gate 豁免扩展单独入袋后再 requeue 0007。

## 轮2（2026-09-18 11:0x-12:3x，全部战果批落地后逐目录全量）

基线对比（与轮1 逐项相等=零回归）：
- check_vocab_domain_convergence --with-db：RC=0，known=79/FDR=68/TR=66/在用=72，ADVISORY DB 未收编域 10（同名单）
- validate_target_layer：RC=0，合法 62+废弃 9+别名 10
- process_reaper --status：存活 killed=0，worktree_changes=31（=轮1）

落地链（本窗口）：0030→0033(死 NO-BARE-SQL，校验器:122 加 noqa)→0035(死 CAPABILITY-OVERLAP，
loader module/step 同族 6 对 100% 克隆)→ack 批 17dd193467(echo-guard.yml acknowledged 6 条)→
0038 **落地 f8aed2365e**(12 件)；0031→0034(死 NO-BARE-SQL，2 条小写 select 提为 SQL_* 模块常量)→
0036(死 NO-LONG-PARAM-LIST，复杂度重构副作用 4 函数>7 参)→参数对象重构(子代理，190+36 测试绿+
old/new 差分 ALL IDENTICAL)→0039(死 CREATE-GUARD 类名冲突 WritePolicy→BackfillWritePolicy)→
0040(死 BARE-SUBPROCESS，default_git_runner 改道 run_subprocess_hidden)→0041 **落地 fcf46a42ac**
(139 件，manifest 与 HEAD 零漂移合法省略)。

轮2 新暴露 4 红（全部滞后红，非本战役引入，锚已查）：
- governance_e2e/test_phase1_gate_check 2 红：期望 8 模块目录 agent-spec/drift-detector/
  budget-enforcer——AI-21 批 441852d976(09-05) 已删空壳，能力真身=agent_spec/gov_drift/
  integration.budget_enforcer。治本：测试改为按能力真身路径断言（注释锚=删除批）。
- security/test_security_scripts 2 红：validate_script_naming(17 件)/validate_exit_codes(26 件
  89 处)滞后红，涉事均为已落仓他域件（algo-flow 出仓波/落地面锚定批 2ac7d910ed/TDM v1.3 批）。
  治本=按 #ARCH-114 裁定路径 C 既有豁免登记机制收编存量（本战役 backfill_module_domain.py 亦
  按 backfill_* 同族先例登记）；两验证器 RC=0，security+governance_e2e 467 passed 复绿。
- tests/governance/orchestrator 轮2 首跑 Timeout=与队列 drain 的 git index 锁竞争（环境性），
  单独复跑 exit 0 全绿。

修复批：validate_script_naming.py + validate_exit_codes.py + test_phase1_gate_check.py + 本日志。
