---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C01
name_zh: 提交正门 CLI 与危险命令外壳
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C01
---

# D11-C01 提交正门 CLI 与危险命令外壳

## 1. 定义
提交车道第一环节（exit_codes.owner_node，全车道退出码矩阵挂本节点）：一切提交的唯一合法入口。决策问题=「这次提交走哪个入口？失败退出码能不能定位死因与拆批口径？」要点（图按实查口径加注）：**反裸提交的真担保是三拦截者而非两壳**——pre-commit hook gate-commit-gw+网关内 _run_git 守卫（in_commit_flow 非真即拒）+POST-COMMIT-GUARD 回滚；git_guard.py/git_safety_wrapper.ps1 只管删除类与 plumbing 类（危险集不含 commit）。

## 2. 六向台账

### 2.1 输入面
- 三触发源：人工 CLI（scripts/git_commit.py）、reconciler auto commit（_commit_auto）、emergency 通道——终点同归正门（laws：正门唯一）
- CLI 参数面：--session/--files/--enqueue/--claim-only/--release-only/--merge-finalize/--reconciler-verify 等

### 2.2 输出面
- CommitResult→退出码 0-10 全谱（`scripts/git_commit.py:139` `_COMMIT_RESULT_MAP`，11 专码+default 1；AST 机生半边=map exit_codes.machine）
- message-file+[GW:<sid>] 尾标 commit

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml` exit_codes 顶层矩阵（owner_node=D11-C01，机生=scripts/git_commit.py:_COMMIT_RESULT_MAP exists=true）
- 骨架：`docs/_archive/_working_cleared/map_build/fig11_delivery/04_提交正门与全局锁.md`
- 处方真源：commit_navigation_playbook.md+gate_digest_registry.yaml（C02 递送）

### 2.4 代码模块
- `scripts/git_commit.py:139` 分发表+`:18-50` 文件头唯一入口声明+ERROR_CONTRACT :13（exit 0-10 逐条）
- `scripts/git_guard.py:96` `DANGEROUS_SUBCOMMANDS = {reset, checkout, stash, revert, restore, mv, clean}`；`:100` `PLUMBING_BLOCKED_SUBCOMMANDS = {read-tree, update-index, write-tree, hash-object}`——实读二者均不含 commit（图判定维持）
- `scripts/git_safety_wrapper.ps1:19,96,170` BLOCKED/HARDBLOCKED 清单（.git 目录写永久阻断）
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1306` `self.in_commit_flow=False`+`:1451` property（红攻1治本）
- `scripts/governance/git_hooks/post_commit_guard.sh:3` POST-COMMIT-GUARD（non-GW commit 检测+自动 revert；:187 24h 同 session warn 累计阈值阻断）

### 2.5 门禁约束
- trigger_facts.gates=1（30d 触发 6 次）；consumers 含 .pre-commit-config.yaml/.trae/rules 两册
- laws：正门唯一/禁裸 git commit/禁 plumbing 绕过（宪法 §9.8：[GW:] 标记不可伪造，POST-COMMIT-GUARD reset 回滚）

### 2.6 自动化触发
- exit 2 LOCK_TIMEOUT 自动改道入队（C04/C08 交接）；近三日 [GW: 全量提交（图 exec_evidence：1382 条/3 日）持续在产

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 三触发源+参数面实存 |
| 输出面 | pass | 退出码全谱在表，AST 机生同源 |
| SSOT真源 | pass | 图矩阵=代码表逐条一致 |
| 代码模块 | pass | 五锚点实存，两壳危险集实读不含 commit |
| 门禁约束 | pass | 三拦截者+宪法 §9.8 齐 |
| 自动化触发 | pass | 改道/回滚/审计自动 |

## 4. 缺口与建议
- 【认知纠偏】骨架 C01 格把两壳与正门并列易误读为「正门拦截器」——图已按实查口径加注，建议骨架回写时采纳图口径（三拦截者）。
- 【观测建议】exit 2 的指数退避处方（5s→15s→45s）仅存于分发表 help_text，建议进 commit_navigation_playbook 正条目（C02 联动）。
