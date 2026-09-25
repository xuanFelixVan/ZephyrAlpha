---
ttl: task_bound
---

# 交接指令 · 提交链治本夜战（开新对话即贴此卡续跑）

## A. 项目背景（1 段）
D:\ZephyrAlpha＝100% AI 开发的 A 股量化系统，夜间多 AI 施工队并发，全部经唯一提交门（GitCommitGateway + 提交队列 + belt 守护）落地。Owner 定性：**提交链吞吐＝全项目开发速度**。本役＝治本提交链：实测等待 p50 5.5 分/p99 3 小时、单文件门禁链 64 秒（5 台全仓扫描门占 83%、读共享暂存区）、slow_item 均值 755 秒。工作目录 D:\ZephyrAlpha（Windows / Git Bash / Python 3.12）。编制：Flash 施工（本卡执行者＝总包），Max 只裁判据语义。

## B. 冷启动（新对话第一件事，逐条）
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version   # 必须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status   # reaper 不在=禁写
grep -E "csx_|commit_speedup_campaign" data/runtime/process_reaper_keep.txt   # 两令牌须在，缺则补
python -c "from zephyr.security.access_control.session_concurrency import SessionRegistry; from pathlib import Path; SessionRegistry(Path('D:/ZephyrAlpha')).register('st-commitspeed-tbl-20260924', pid=0)"   # pid=0 必带，与后续同命令链
```

## C. 必读文件（全路径；按此序读，勿全背，用锚点检索）
1. `D:\ZephyrAlpha\AGENTS.md`（宪法 L0，唯一必读；≤300 行）
2. `D:\ZephyrAlpha\docs\_working\commit_speedup_campaign\90_verification\CAMPAIGN_STATE_SNAPSHOT.md`（本役当前态快照，先读这个对齐）
3. `D:\ZephyrAlpha\docs\_working\commit_speedup_campaign\90_verification\decisions_log.md`（逐事件裁定志，读末 15 行）
4. `D:\ZephyrAlpha\docs\_working\commit_speedup_campaign\90_verification\MAX_RULINGS.md`（**Max 已裁 MQ-1~4，包3 据此执行**）
5. `D:\ZephyrAlpha\docs\_working\commit_speedup_campaign\90_verification\MAX_RULING_QUEUE.md`（MQ-5 已自解/MQ-6 备查）
6. `D:\ZephyrAlpha\docs\_working\commit_speedup_campaign\20_target_arch\A4_migration_ladder.md`（S0–S7 迁移阶梯＝总路线）
7. `D:\ZephyrAlpha\docs\_working\commit_speedup_campaign\00_HANDOFF.md` + `00_MASTER_PLAN.md`
8. 各包设计真源：`30_gate_census\C1_gate_dossier.md`、`30_gate_census\P3_integrity_head_derivative_prep.md`、`40_b0_derived_offload\B0_3_design_and_tests.md`、`10_d1_d2\D2_env_flag_leak.md`、`20_target_arch\A3_gate_repointing_matrix.yaml`

## D. 上下文浓缩（截至 2026-09-24 ~23:4x；落地状态以 `git show HEAD:<file>` 实测为准）

**已落地进 HEAD（真值已核）**
- 批一 装表(A1 pre-commit真实计费/A2 八段+residual_ms/A3 pool_wave)+D3 熄火真身+B4 先来先服务（队列项 0005）。
- 钩 T6 reference-transaction 子进程 5→1（0008）。
- D4 幽灵 pending 双落地治本（回写收窄+写后清扫 / 认领终止性复查+吞 FileExistsError）（0010，HEAD grep 已证）。
- 批六 T5/M2 衍生再生出窗（根钉定+意图账+卡死检测；含 reconcile_generators.py 主区钉定）（0012）。
- 0009＝前上下文某单件（逐件 `git show HEAD` 自证，勿臆断）。
- belt 守护 21:46 由 `_check_and_reexec` 自换血→**D3 四路并发实证生效**（四工 landing_phase_stats 全产出）。

**在队待落**
- p13-a gate stats 去 1ms 盲区 = **0026 pending**（`commit_gate_registry.py:111` 单行；红测1绿/lint净）。

**死件需处理（非循环、无 rogue 自动重投）**
- **W4 止血（0025 dead）**：内容正确（gateway `_commit_auto` 两分支 finally 还原 prev-snapshot + 加牙 test_commit_sets_gateway_env + 新测 test_w4_env_no_residual），但**死因＝陈旧基底**：csx-w4 从 7d8271c128 拉，dev 已推进，`gateway.py:123 import zephyr.governance.audit.reconciliation_registry` 现被判 IMPORT-INTEGRITY 悬空。**修法＝从当前 dev 新拉 scratch，把 W4 那 2 处还原重贴（只加还原不删置位/不动判据），复跑红/绿 + ruff/format/check_frontmatter 净后重投。** 补丁锚见 `D:\ZephyrAlpha\.runtime\tmp\csx_msg_w4.txt`（描述）与 `csx-w4` worktree diff。
- 文档袋（0002/0006/0013/0014… 一串 dead）：战役卷宗改名已部分做成小写（见 `10_d1_d2/d1_d2_readme.md`、`20_target_arch/target_arch_readme.md`、`40_b0_derived_offload/b0_readme.md`），但仍死在 capability 册同键 token 三向合并 + CREATE-GUARD 缺 token + gate-naming。**裁定＝推迟到收尾批，按"整册回 HEAD 只注入本批条目 + 补 creation_token"统一落。**

**前上下文遗留、本会话未复核的**
- 批七 T14 名册同步（0023 dead）死于"注册表项基底不可知(base_head/base_blob 皆无)"；其 ms 部分已被更干净的 0026 覆盖，**对账生成器 + own_scope 机生补全两块仍未落**。

## E. 剩余施工清单（按依赖；括号内=前置/判据）

1. **W4 重投**（无前置，先做）：见 D 段修法。落地后验 `git show HEAD:...git_commit_gateway.py | grep prev_gateway_env` 非空。
2. **包3 完整性基线 HEAD 派生**（**Max 已裁 MQ-1/2/3/4，直接据 MAX_RULINGS.md 执行**）：草案 `D:\ZephyrAlpha\.runtime\tmp\csx_p3_patch_draft.md`；设计 `P3_integrity_head_derivative_prep.md`。要点：check() 读 HEAD blob 非滞后 json；CHANGING_IN_COMMIT 解释位**仅 own-scope**+R-2/R-5 双哨兵同批；_GATES_DIR 指真身 + 空清单 stderr + 低于阈值即红；DB 出库**暂缓**（终报呈 Owner）；MQ-3 回溯＝`git log --oneline <改名提交>..HEAD -- src/zephyr/gov_enforcement/commit_gates/` 列表入卷宗附表，不重放历史。触 landing/gateway（已解锁）。
3. **包5 步2/3（删全局 env 写）**（前置=W4 落地并验生产）：顺序铁律见 `D2_env_flag_leak.md` §4/§8——先补 per-spawn 注入面（internal_call 形参 / sanitized_spawn_env / _trusted_git_env 显式决定 C2）→ **最后**才删 W1(landing:1577/1641)/W2/W3(gateway:3510/3557)/W4 已做。**逆序＝POST-COMMIT-GUARD 判 forged 吃掉已落提交。**
4. **重放基线基建收口 → 包8 → 包9 → 包7**（最大杠杆，链式）：replay 子代理**已停、未收口**——它写了 3 件（`src\zephyr\gov_enforcement\commit_gates\_tree_view.py`、`scripts\governance\replay_gate_verdicts.py`、`tests\governance\test_gate_replay_harness.py`）但 `50_replay_baseline\R1_design.md` 未出、无完成通知。**先独立验这 3 件能红/能绿（CommitTreeView 复现＝实际 diff 逐字节对得上；投毒注册表须判失；不读工作树绊线）→ 再用它做包8 三簇合并"重放 100→1000 笔逐台 verdict 全等"出厂判据 → 包9 门禁 own-tree（15 台故意读全索引者分道，禁 own-tree）→ 包7 缓存键去 HEAD/共享暂存树。** Owner 令：门禁只合并/降档/diff 化，**禁删**。
5. **包10 止血（B5）**：门前置短路（红件 3 秒判死而非 218 秒）+ attempts 退避移毒药队首；commit_queue.py（已解锁）。
6. **包11 合批去抖 / 包13 余下（对账生成器+own_scope）**：判据见 00_MASTER_PLAN。
7. **包14 红蓝极限对抗（7 场景每把尺先证能红）**（前置=各功能包完工）。
8. **包15 收尾**：文档袋按命名规范+token 落；`99_FINAL_REPORT.md`（每分包三清单[裁定/执行/复查]+复核命令+证据等级+回收测算）；清 csx_* 脚本、scratch worktree（`git worktree remove`，OPS-GUARD 拒 in-process 删是正常，勿 --force-skip-checks）、release claim（读 `.ailocks/registry.json` locks 段判成，勿信 stdout）。

## F. 本会话踩过的坑（务必复用药方）
- **入队后、落地前，对实际 blob 复验**：批一 0001 死于入队快照含 stale B905/B009；0011(W4) 死于快照 blob 顶上缺 `# [TTL] permanent` 行。→ 用 `python scripts/governance/d3_metadata/check_frontmatter_metadata.py <从袋抽出的 blob>` 校 TTL，别只信工作树文件。
- **ruff 会重排**：`ruff check --fix`(I001)/`ruff format` 可能把 import 提到 `# [TTL]` 头之前 → TTL 判缺。改完先 `head -1` 确认元数据头仍在顶。
- **requeue 取工作树现字节**：`commit_queue.py requeue <dead_qid> --worktree-root <scratch> --base-head $(git rev-parse dev)`。死信先读 dead_reason 现值。
- **陈旧基底会带悬空 import**：scratch 拉太早，dev 前移后他人改过的 import 会被你带回 → 从**当前 dev** 重拉 scratch 再重贴改动。
- **队列按位置重编号**：qid 后缀不稳（会挪），监视落地用**按 HEAD 内容探针**而非盯 qid。
- **字典序/持续投件饿死**：勿插队（红线2）；等待窗做不依赖落地的预备。
- **禁在任何 worktree 跑 `tests/governance/test_ops_guard_red_team.py`**：本环境它真删 src/zephyr 数千文件（地雷）。派子代理时任务书 MUST 列此禁跑清单。
- **字符≠字节**：`len()` 是字符、`wc -c` 是字节，中文 3 字节/字，别据此误判文件"蒸发"。
- **热文件（decisions_log/注册表）写前 claim + `safe_write_text` CAS（base 用 `content_sha256`）+ 写后进程外读回**。

## G. 红线（违反＝该批作废回滚）
不删门禁/退役（Owner 令，只合并/降档/diff 化）；不改判据阈值凑绿；未达如实报；提交必经 `scripts/git_commit.py`/`commit_queue.py` 正门，禁裸 git commit / plumbing / 插队 / 硬闯 HELD-OVERLAP；`[GW:]` 不可伪造；禁 kill belt 守护；新建 .py/.yaml/.md 须 creation_token（tests/ 免）；docs/_working 禁 .json（用 .yaml）；案卷禁 `裁定#<未登记号>` 与裸 `AGENTS.md §N.M`；.ps1 纯 ASCII；测试输出走 `.runtime/tmp/csx_*`，`pytest -p no:cacheprovider -W ignore::pytest.PytestConfigWarning`；**主区工作树混他会话数百文件，今晚禁走 merge 正门，一律 enqueue**。

## H. enqueue 配方（照抄，改清单与 message）
```bash
cd /d/ZephyrAlpha
printf '%s\n' "<相对路径1>" "<相对路径2>" > .runtime/tmp/csx_files_N.txt
# message 写 .runtime/tmp/csx_msg_N.txt，首行 [st-commitspeed-tbl-20260924][批·任务] 
python scripts/commit_queue.py enqueue --session st-commitspeed-tbl-20260924 \
  --files-file .runtime/tmp/csx_files_N.txt --message-file .runtime/tmp/csx_msg_N.txt \
  --worktree-root .worktrees/<scratch> --base-head $(git rev-parse dev)
```

## I. 工作文件全路径清单
- 补丁草案：`D:\ZephyrAlpha\.runtime\tmp\csx_d4_patch_draft.md`、`csx_p3_patch_draft.md`
- D4 机械应用：`D:\ZephyrAlpha\.runtime\tmp\csx_d4_apply.py`（锚定断言式，已双证 4/4 红→绿）
- 已入队件清单/消息：`csx_files_d4.txt`/`csx_msg_d4.txt`(0010 已落)、`csx_files_w4.txt`/`csx_msg_w4.txt`(0025 死待重投)、`csx_files_p13.txt`/`csx_msg_p13.txt`(0026 在队)
- 监视器：`csx_watch_w4.py`（按 HEAD 内容探针）；追加志脚本 `csx_append_dlog.py`
- 取证（保留勿删）：`D:\ZephyrAlpha\.runtime\tmp\cs-tbl\`（`ghost_chain_demo.py`＝D4 闭链 4/4 证明等）
- scratch worktree：`.worktrees\csx-d4`(D4，0010 已落可弃)、`.worktrees\csx-w4`(W4，待 rebase)、`.worktrees\csx-p13`(p13-a，0026 在队)；本役主 worktree `.worktrees\st-commitspeed-tbl-20260924`

## J. Owner 终止判据（未达不算完）
全量回归连续两轮问题=0 → 红蓝 7 场景全过 → 临时件清零 → 零待裁定 → 端到端交付。回收测算须实测：单文件链 64s→<15s、件数/日 158→<60、p99 183→<30 分（**当前均未测得，须包7/8/9 落地后测**）。
