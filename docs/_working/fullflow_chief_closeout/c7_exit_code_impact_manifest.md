---
ttl: task_bound
completes_when: "C7 受影响清单穷举完成：退出码契约真源（提交门分发表+全车道矩阵+治理脚本 rc 常量）三面全部登记 file:line 级证据，码 4=不可判定的冲突与迁移处方逐行可执行"
---

# C7 · 退出码三档受影响清单（新增 4=不可判定的契约冲突面）

## 0. 结论先行

**码 4 在提交门契约中已被占用**：`_COMMIT_RESULT_MAP` 的 `SSOT_VIOLATION: 4` 条目（全仓零生产者的在册死分支，D11-G01）。
直接"新增 4=不可判定"会造成同码双语义=契约腐坏。落地前置：先按 D11-G01 内收判据（零触发零消费→退役，处置权在总包）处置
SSOT_VIOLATION=4 条目，或改选未占用码（7、11+）。本清单=受影响面穷举，不做处置裁定。

"三档"语义基准：治理脚本 rc 约定已有 0=通过 / 1=检出违规 / 2=脚本异常 三档（`EXIT_PASS/EXIT_FINDINGS/EXIT_ERROR`）；
4=不可判定 意为**探针未落地/探测器自身失效**（fail-closed 方向：不可判定≠通过），与 1（判得违规）区分。

## 1. 受影响清单（contract | file:line | 现行码 | 加 4 影响 | 迁移处方）

| # | contract | file:line | 现行码 | 加 4=不可判定 影响 | 迁移处方 |
|---|----------|-----------|--------|-------------------|---------|
| 1 | 提交门退出码分发表 `_COMMIT_RESULT_MAP` | `scripts/git_commit.py:139`（`SSOT_VIOLATION: 4` 于 :162；D11-G01 source_anchors 同源） | 0=OK；1=COMMIT_FAILED 等 8 态；2=LOCK_TIMEOUT/STASH_CONFLICT；3=PROMOTION_BLOCKED；4=SSOT_VIOLATION（零生产者死分支）；5/6/8/9/10=专码 | **同码双语义冲突**（4 已被 SSOT_VIOLATION 契约性占用）；按码分诊的外部调用方（CI/队列脚本）会把"不可判定"误诊为 SSOT 违规 | 二选一：①按 D11-G01 判据退役 SSOT_VIOLATION=4 条目（总包处置）后登记 4=不可判定；②不可判定改用未占用码（7/11+）。改表=改契约，须同 commit 更新行 2/3/7 三面 |
| 2 | 全车道退出码矩阵（law：改分发表=改契约） | `config/dev_delivery_map.yaml:48`（`exit_codes.machine.commit_exit_map`）；码 4 矩阵行 `:100` 前后（statuses=[SSOT_VIOLATION]，处方=不可达码） | 0-4 逐码行+auto_enqueue+处方列 | 码 4 行 statuses/处方失真；machine_facts（AST 机生半边）与新语义漂移 | 按 law_zh 穷举更新矩阵行+重跑机生（AST 读 `_COMMIT_RESULT_MAP`+生产者构造计数），禁手改 machine 段 |
| 3 | 退出码死分支 gap 节点 D11-G01 | `config/dev_delivery_map.yaml:1353-1395`（`exit_codes: [2, 4]`；evidence 引 `git_commit.py:149/:162`、`git_commit_gateway.py:439/:450`） | 死分支=码 4 与 STASH_CONFLICT 支 | 4=不可判定 落地后"码 4 死分支"由死转活，节点 decision_question/evidence 过期 | 复跑簿04 §末-3 命令 2/4 刷新 producer 计数；D11-G01 销案或重扫再登记（处置权在总包） |
| 4 | 提交结果状态消费方（按枚举非按码分派） | `src/zephyr/governance/persistence/task_repo.py:2528`（`CommitStatus.STASH_CONFLICT` elif 链） | 枚举分派，无数字码耦合 | 数字码新增零直接影响 | 若行 1 选退役 SSOT_VIOLATION，同批清理该枚举引用面（`git grep CommitStatus.SSOT_VIOLATION` 全仓核销） |
| 5 | 治理脚本 rc 命名常量真源 | `scripts/governance/_shared/constants.py`（`EXIT_PASS=0 / EXIT_FINDINGS=1 / EXIT_ERROR=2`；rc 约定旁证 `docs/_working/total_command_closeout/wave3/supply_ledger_report.md:23`） | 三档 0/1/2 | 新增第四档需 `EXIT_UNDETERMINABLE=4` 常量入真源；裸数字门（validate_exit_codes.py）词表同步 | 常量加进 `_shared/constants.py` → 全仓 grep 裸 `exit(4)`/`return 4` 收敛到常量 → validate_exit_codes 复跑 exit=0 |
| 6 | CI 挂载面（逐步 rc 隐式判死） | `.github/workflows/governance.yml`（`--check` 步骤非零 rc 即红，无按码 case） | 非 0 全部=步骤失败 | 4=不可判定 隐式红（fail-loud）——方向正确但无分诊：不可判定与检出违规在 CI 眼里同红，止血动作不同（修探针 vs 修违规） | 步骤 shell 显式 `case $rc in 4)` 分诊：不可判定=红+标注"探针失效"告警通道（禁静默重试吞红） |
| 7 | fail-open 在册登记（code 字段引用 rc 约定） | `docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml:1699`（`EXIT_CLEAN=0；EXIT_FINDINGS=1；EXIT_ERROR=2` 逐字 code 记录） | 三档逐字引用 | 该条目与新增档漂移=文档矛盾（事故级，宪法 §4.4） | 新档落地同 commit 更新该 code 字段；全 register grep `EXIT_` 核其他引用节点 |

## 2. 判定顺序处方（若采纳 4=不可判定）

1. 行 1 二选一裁定（退役 SSOT_VIOLATION=4 或改码）→ Owner 门位（改契约=退出码法 law_zh 明文）。
2. 同 commit 五面同步：git_commit.py 表 + dev_delivery_map 矩阵（机生）+ D11-G01 销案 + _shared/constants.py 常量 + fail_open_register 条目。
3. CI 行 6 补 case 分诊；行 4 消费方枚举面随退役批核销。
4. 复跑簿04 §末-3 全部命令留 exec_evidence；commit_navigation_playbook 指路面（作业簿 04 §1）同批进指路。

## 3. 证据基线（本清单实查）

- `_COMMIT_RESULT_MAP` 十一条目+default=1：`scripts/git_commit.py:139-221` 实读。
- 码 4 死分支三证（枚举定义+分发表+task_repo 消费支路，零生产者）：dev_delivery_map D11-G01 机生面+exec_evidence 转录。
- 三档 rc 约定+裸数字禁令：supply_ledger_report.md:23 + check_directory_contract.py:14 等十余脚本头部 ERROR_CONTRACT 实读。
- "不可判定"域内既有语义先例：t1_t2_handover.py:954（STALE_CLAIM,1 认领损坏=不可判定归属交人）、backtest/core/metrics.py:293（DSR 退化=不可判定 fail-closed 地板）——均为值内表达，未占退出码新档，佐证 4=不可判定为**新契约**而非既有惯例追认。
