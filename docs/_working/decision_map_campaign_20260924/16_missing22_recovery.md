---
ttl: task_bound
title: 16 整装回测首跑 22 件审计链尾件 找尸与抢救结案（IBT-B03/G02）
doc_type: log
---

# 16 · 首跑 22 件审计链尾件：下落追查与抢救结案

> 追查对象=11 号文 IBT-B03/G02 记录的「整装回测首跑（2026-09-22，audit-all-0011 批）22 件
> 逐笔审计链尾件在主区盘面消失」。执行班=st-ibt22-recovery-20260925，2026-09-25 00:47 起。
> 结论先行：**22/22 全部找回，字节级完整，零重建、零死亡**；根因除 10 号文蒸发链外，
> 另查明这批件在蒸发之前已经**带着 14 个死袋投过两次队**，最后 3 次判死同源于一条门禁
> 缺陷——产物本身从头到尾没有问题。

## §1 清单重建（11 号文未逐件列名，按盘上目录索引复原）

`IBT-HANDOFF-TO-MAX.md` §5 给出的是构成（run_summary.yaml×4 + sensitivity.yaml×2 +
nav/trades csv×16），未列全名。逐件清单取自四窗目录自带的 `index.md`
（`generate_missing_index_md.py` 于 2026-09-22 生成，本身在 HEAD），与构成描述完全吻合：

| 窗口 | 应有件数 | 件名 |
|---|---|---|
| W_IS | 6 | run_summary.yaml、sensitivity.yaml、nav_IBT-{A,B}.csv、trades_IBT-{A,B}.csv |
| W_OOS | 6 | 同上 |
| W_HOLDOUT | 5 | run_summary.yaml、nav_IBT-{A,B}.csv、trades_IBT-{A,B}.csv（本窗无敏感性） |
| W_POSTD | 5 | 同上 |
| 合计 | **22** | 前缀均为 `docs/_working/integrated_backtest/artifacts/` |

同窗的 `redblue_round*.yaml`（4 件）与 `IBT-RUN-LOGS.md`、五册报告在 HEAD 未受影响——
蒸发面精确落在「未入 HEAD 的 22 件」，与 10 号文「untracked 全灭、tracked 无恙」的判据一致。

## §2 五处找尸结果（+一处指令清单外的生路）

| # | 找尸处 | 实测口径 | 命中 |
|---|---|---|---|
| ① | 原路径 `docs/_working/integrated_backtest/artifacts/<窗>/` | 22 次 `-f` 判定 | **0/22**（仅剩各窗 index.md 与 redblue yaml） |
| ② | `.worktrees/st-e2e-20260924/` 全树 | 整树 find（该树只有 HEAD 面 22 件在册件） | **0/22** |
| ②扩 | 指令未点名但同类：`.worktrees/` 全部 41 树 + `.aidrafts/` 全部 12 个会话草稿树 + `.runtime/` 全树 | 按 6 个 basename 全量 find；positive control（同路径 redblue_round2.yaml 命中 5 树）证明检索面确实生效 | **0/22** |
| ③ | `git fsck --lost-found` 悬垂对象 | 9962 个对象落 `.git/lost-found/other`，逐件算 CRLF/LF 两形态 git blob SHA-1 比对 | **0/22**（首跑从未 `git add` 进主对象库） |
| ④ | `.runtime/quarantine/`（10 号文 §7 真源=`worktree_drift_watchdog.py` MODIFY-GUARD，命名 `drift_<ts>/`，按原相对路径存快照） | 353 个 drift 目录：按路径 find + 按内容 grep（IBT-A/integrated_backtest/W_HOLDOUT） | **0/22**（quarantine 里只有热册与 LEDGER，本批 untracked 产物不在其扫描面） |
| ⑤ | `git stash list` | 全量枚举 | **0 条 stash**（与 reaper 侧 `drift.stash_count=0` 互证） |
| ⑥ | **`.runtime/commit_queue/blobs/` 内容寻址袋**（指令清单外，本案唯一生路） | 3068 个袋清单逐件比对 path+blob_sha256 | **22/22** |

第⑥处的两代字节：

| 代 | 生产者会话 | 袋数 | 时间戳 | 行尾 |
|---|---|---|---|---|
| 首跑 | `st-integrated-bt-20260922` | 7（q-0001/0002/0004/0006/0009/0026/0027） | 09-22 05:48–16:48 | CRLF |
| 整改批 A 重投 | `st-ibt-remedy-a-20260923` | 7（q-0003/0007/0008/0011/0012/0013/0014） | 09-23 03:34–04:52 | LF |

两代 **EOL 归一后 22 件逐字节相同**（同一份产物的两次入袋，非两次不同数字）——
因此不存在「该恢复哪一版」的裁量问题，统一按 LF 落盘（`.gitattributes` `* text=auto eol=lf`）。

## §3 内容完整性核验（34 项对账 + 双向红证）

恢复口径=袋内 `blob_sha256` 与落盘字节的 sha256 逐件相等（22/22 相等，非"看起来对"）。
对账尺把 csv 明细与 yaml 汇总互为对手（一次性暂存脚本，结案时已删；下表每行即完整判据，
容差与比对对象都写死，任何班次可照表重实现）：

| 核验项 | 口径 | 结果 |
|---|---|---|
| 净值收益率 | nav csv 末点/首点-1 vs `variants.<IBT-A\|B>.core.total_return`，容差 1e-6 | 8/8 相符 |
| 最大回撤 | nav csv 峰值回撤 vs `core.max_drawdown`，容差 1e-6 | 8/8 相符 |
| 成交笔数 | trades csv 数据行数 vs `core.trades_count`（整数相等） | 8/8 相符（IS 35212/31903，OOS 13935/13113，HOLDOUT 7567/6738，POSTD 194/194） |
| 净值区间 | nav csv 首末日期 vs `core.start_date`/`end_date` | 8/8 相符 |
| 敏感性册可解析 | sensitivity.yaml 各档含 sharpe | 2/2 通过 |
| 规模 | 22 件合计 15,008,932 字节（W_IS 9,242,575 / W_OOS 3,726,441 / W_HOLDOUT 1,975,533 / W_POSTD 64,383） | 与袋登记逐件相等 |

**红证（尺子能红）**：把 IBT-A 净值末点扰动 5% 并删一笔成交后，同一把尺 34 项中 8 项转红
（四窗 total_return 与 trades_rows 全红），撤扰后复绿。首轮还试过"整条序列等比放大"作扰动——
尺子不红，因为收益率与回撤是尺度不变量；该扰动方案作废，换成只动末点。
附带自纠：第一版尺把 nav csv 首行的盘前现金标记（空日期行）当日期用，误报 8 项，属脚本缺陷非产物缺陷。

结果：**找回 22 件 / 重建 0 件 / 死亡 0 件**。11 号文 IBT-B03 担心的「逐笔审计链永久灭失」解除。

## §4 根因：两条独立死因叠加（蒸发只是补刀）

**死因一（本案主因，已在 10 号文定性）**：主区未入库件被落地链穿透清除。
时间线相容——09-24 凌晨 `_sync_worktree` 穿透（10 号文头号嫌疑，置信度 ~65%/复合 ~80%）
+ `_pre_merge_auto_clean` 物理删除面。判据：同窗 tracked 件（redblue yaml/五册）无一受损，
只有 untracked 面全灭，与该链的作用面特征一致。

**死因二（本次新查明，是它让 22 件在蒸发前就无法入库）**：GATE-NAMING/N-16 增量面缺陷。
死袋谱系完整可读——携带这 22 件的袋共 **14 个，全部为死袋**（`dead_archive_w8_20260923/` 内
首跑 7 + 整改批 A 7，逐袋 `dead_reason` 实测），按时间序：

| 袋 | 时刻 | 死因门禁 |
|---|---|---|
| 首跑 q-0001 | 09-22 05:48 | DIRECTORY-CONTRACT（DCR：`run_summary.json` 扩展名不入 docs/_working 白名单） |
| 首跑 q-0002 | 05:55 | landing 异常：prestage 拒绝（`data/backtest_artifacts/` 被 .gitignore，再生产物区禁入） |
| 首跑 q-0004 | 07:09 | DIRECTORY-CONTRACT（DCR：`ibt_attribution.json`） |
| 首跑 q-0006 | 14:31 | R5-DIGIT-SUFFIX（`scripts/backtest/ibt_20260922/` 数字后缀） |
| 首跑 q-0009 | 15:00 | **GATE-PRECOMMIT-RUN / hook=gate-naming（N-16）** |
| 首跑 q-0026 | 16:46 | CREATE-GUARD（无 creation_token） |
| 首跑 q-0027 | 16:48 | **gate-naming（N-16）** |
| 整改A q-0003/0007 | 09-23 03:34/03:54 | TRANSLATION-COVERAGE（同袋搭的 4 个新 .py 缺大白话） |
| 整改A q-0008 | 04:10 | FUNCTION-DUP |
| 整改A q-0011 | 04:19 | NO-SECRET-HARDCODE（`ibt_remedy_a_acceptance.yaml:10` 硬编码 token） |
| 整改A q-0012 | 04:30 | **gate-naming（N-16）** |
| 整改A q-0013 | 04:43 | PROTECTED-PATHS（rules/ 下 YAML 被扫进袋） |
| 整改A q-0014 | 04:52 | GATE-PRECOMMIT-RUN / hook=gate-protected-paths |

即：DCR 两修、gitignore 一修、R5 一修、CREATE-GUARD 一修之后，**首跑与整改批 A 各自独立撞在
同一条 N-16 上，共 3 次**（q-0009/q-0027/q-0012）；此后整改批 A 又因把工具件与 rules/ 搭进同袋
连死 3 次。台账 §3 自记「13 轮死因谱系」与本表同族（本表按 22 件实际携带面核到 14 袋）。

N-16 判死的机理：`run_summary.yaml`/`sensitivity.yaml` 在四窗各一份（协议冻结的按窗产物命名），
撞上「全仓文件名唯一」。这不是产物违规，是门禁两条代码路径对同一份真源不一致——

- 真源 `rules/trae_028_doc_structure_naming.yaml §n16_config.skip_dirs_docs` 含 `_working`，
  立法记录见 `tests/governance/d3_metadata/test_n16_skip_working.py` 头注
  （#ARCH-PRECOMMIT-INCREMENTAL，2026-08-05，立法的原话目的就是「使草稿区重名不阻断 commit」）；
- 全扫面 `_check_basename_uniqueness` 确实按 skip_dirs 剪枝；
- **但提交面 `check_new_files_naming` 从不消费 skip_dirs**，只消费 exempt 名单 + 一条
  `/_working/archive/` 特例（后者恰好证明前者被遗漏：若 `_working` 生效，该特例是多余的）。

后果：2026-08-05 那次治本只修了审计面，提交面照旧硬阻断，于是首跑 22 件在 09-22/09-23
两轮共 4 次死在同一处，最终留在 `.runtime` 未入库面上等被蒸发。

## §5 本批处置（Owner 2026-09-25 交互裁定：豁免补丁→原位入库）

Owner 选项原话=「豁免补丁→原位入库」，取向是写成通则而非本批特批。实施中查明
**不需要扩白名单、不需要动受保护路径 rules/**：把提交面接回它本该消费的那份真源即可，
语义与原立法一致，故按治本落地：

1. `scripts/governance/d3_metadata/check_naming_convention.py` 新增 `_in_n16_skip_dir()`，
   在 `check_new_files_naming` 的两处生效：候选新增件、`git ls-files` 已跟踪基线
   （后者防"归档/草稿区既有件反过来拦正式区新增"）。豁免集合仍动态取自 YAML，零新增硬编码。
2. `tests/governance/d3_metadata/test_n16_skip_working.py` 增第三尺
   `test_incremental_path_honours_skip_dirs`：双向——`_working` 内按窗同名不得阻断（本案回归），
   正式区同名必须仍阻断（防豁免扩成 N-16 静默失效）。
   红证：内存中把 `_in_n16_skip_dir` 摘掉，同一把尺立刻回到 3 项违规。
3. 22 件按 LF 落回**原位**（`docs/_working/integrated_backtest/artifacts/<窗>/`），
   四窗 index.md 自带链接随之复通，五册正文指路无需改字。
4. CREATE-GUARD token **零新增**：22 件的 capability 册条目早在 09-22 收口批已入 HEAD
   （`capability_canonical_file_registry.yaml` 内 22/22 在册），`batch_creation_tokens.py`
   实测回报「无待登记文件」。
5. 回归面：命名门禁全族测试 274 项全绿
   （`tests/governance/d3_metadata/` + `tests/gate/test_gate11_naming_convention_unit.py` +
   `tests/governance/code_quality/test_n16_exemption_loader.py` +
   `tests/governance/governance_e2e/test_naming_e2e.py`），`--validate-ssot` YAML↔代码双轨一致。

入队=唯一正门 `scripts/commit_queue.py enqueue`（禁裸 git commit），门禁改动与其解锁的
22 件产物**同袋原子投**（分袋会踩「册先行/代码后继」跨袋依赖崩，且 N-16 判据必须先于产物生效）。

## §6 预防建议（三条，按性价比排序）

1. **产物类件不得长期只在 `.runtime` 存活**：本案唯一生路是 commit_queue 袋，而袋在
   `.runtime`（gitignore + 有清理前例 `dead_purged_20260920`，30 天级）。这次是运气——
   09-24 蒸发链没顺手清 dead_archive。**建议**：10 号文补一条「未入库案卷的存活时长上限
   =袋清理周期」，并把「袋内仍有未落地件」纳入队列侧健康告警面（与 15 号文 EV-01 黑匣子同族）。
2. **门禁两条路径必须共吃一份真源**：本案病灶是「YAML 改了、只有一处代码消费」。
   **建议**：凡 `n16_config` 这类"真源在 YAML、代码动态加载"的结构，配一把
   全扫面/提交面**同判据**的永久尺（本次已为 skip_dirs 补上第一把），
   并纳入 GATE-21 派生标量自愈同源思路（机制能红，不靠谁记得直提）。
3. **死信要聚类归因，否则同一死因会被反复重投**：同一条 N-16 在 3 个袋里各死一次
   （q-0009/q-0027/q-0012，跨两个会话），
   每次都是新的 40 件快照袋、新的一次 claim/落地成本。**建议**：`dead_reason` 按
   （门禁 ID × 命中文件集）指纹聚合，第 2 次同指纹即升告警——这正是 15 号文「把静默变有声」
   在队列侧的对应件。

## §7 遗留与边界（不谎称已全绿）

- 本批**未**做 Owner 门位项：未退役任何门禁、未动 rules/ 任何 YAML、未翻任何 flag。
- `11_integrated_backtest_audit.md` IBT-B03 的「两规则冲突」叙述需相应更正：实测不是
  「N-16 与协议冻结命名相撞后必须二选一」，而是提交面漏读真源。**建议** IBT-B03 由 OPEN
  改为「治本已投，待落地复核」，判据=本件 §5 第 2 条的永久尺 + 22 件在 HEAD。
- W_POSTD 窗 IBT-A 与 IBT-B 的 nav/trades **逐字节相同**（249B/26.7KB 两两相等），
  且该窗净值只有 8 个交易日；两变体在该窗无差异是否合法，属回测语义问题非本案取证问题，
  已登记为 IBT-B03 复核线索，不在抢救批内裁。

## §8 落地终态复核（本件成稿于 01:3x，当时状态=已入队；04:09 已落 HEAD，此处记终态）

| 项 | 实测 |
|---|---|
| 队列项 | `q-20260925-st-ibt22-recovery-20260925-0001` → done |
| 落地 commit | `4c00b9607d`（09-25 04:09） |
| 归属 | 该 commit 实带 **24 文件**，与本批清单逐一对齐，**零连坐**（`git show --name-only 4c00b9607d` 减去本批 24 件＝空集） |
| 字节闭环 | HEAD 内 22 件 sha256 与当初袋内登记 `blob_sha256` **22/22 相等**——落地链未改一个字节 |
| 门禁治本 | `git show HEAD:scripts/governance/d3_metadata/check_naming_convention.py` 内 `_in_n16_skip_dir` 3 处命中；永久尺随批在 HEAD |
| 工作区 | `git status --porcelain docs/_working/integrated_backtest/ <两码件>` 除 `artifacts_v2/`（IBT-F01 旧悬案，非本批）外为空＝无未提交、无回退 |
| 案卷 token | capability 册 HEAD 面 `16_missing22_recovery.md` 命中 1 条（随他批次册变更同窗落地，本袋未夹带他人未落地条目） |

任何人可重放的三命令（不需要本批脚本）：

```bash
git ls-tree -r --name-only HEAD \
  | grep -cE "integrated_backtest/artifacts/W_.*(run_summary|sensitivity|nav_IBT|trades_IBT)"   # 期望 22
git show HEAD:docs/_working/integrated_backtest/artifacts/W_IS/run_summary.yaml | sha256sum
#   期望 640e584d803f280230e1606aaf2f8b5fe9eee44e3305e22e23e4cef692d260c0（＝袋登记值）
python -m pytest tests/governance/d3_metadata/test_n16_skip_working.py -q                        # 期望 3 passed
```

## §9 运维自纠（本批踩到并当场修好的两处，写下来给后续班次）

1. **主区临时注册会话必须 `register(pid=0)`**。默认 `pid=os.getpid()` 会把注册绑到那条短命
   命令；命令一退，心跳 daemon 判"session not in registry"直接退出，而 registry 里条目看着
   仍在（`_load()` 查得到）——极易误判成 daemon 另有问题。本批第一次就是这么错的。
2. **心跳断 >90 秒＝会话判死＝本会话全部 claim 被系统自动收回**（`pid=0` 轨的判据是心跳
   新鲜度，不是 TTL；本批 02:0x 实测锁数掉到 0，已按上述口径重注册＋二次 claim 24/24）。
   判活只看一件事：隔 >30s 复算 `time.time()-last_heartbeat` 是否回落，别信 pid 文件存在与否。
   **实测修正（勿传播未经检验的推断）**：本批袋最终落地的 04:09 时点，生产者会话早已随
   daemon `idle timeout=1800s`（02:34）判死、claim 亦已释放——队列落地侧并未因此报
   SESSION-REQUIRED，袋照常落账 24 件零连坐。所以"会话判死必致袋死信"是**本批曾写下但未成立
   的判断**；claim 的真正价值在落地前的防连坐/防搭便车窗口，不在于落地时点必须存活。
   深队列（本批 29→41 袋、约 2.5 小时）若依赖 claim 守护，须自行按 idle 周期续心跳。

—— st-ibt22-recovery-20260925，2026-09-25（取证只读；写盘面=22 件复原 + 1 处门禁治本 + 1 把永久尺 + 本件）


