---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 提交链提速战役——总簿（环节全景骨架 + 战役批次志）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: active
---

# Flash 提交链提速战役·总簿（24 笔/h → 100+）

> **战役定性（Owner 令 2026-09-18）**：把 Git 提交链从 24 笔/小时提速到 100+。P2 已实证
> **24/h 是门禁常数不是锁常数**（10 worker 870/h → 20 worker 540/h、饿死 45%），故次序=
> **先修门禁（F3）再谈通道（F2）**；时间不够砍 F2 保 F3。
> **真源四件**：`docs/_working/kimi_audit/S18_提交链路根因表.md`（R-01~R-12）｜
> `S18_Flash施工包判据.md`（F1-F4 机读判据）｜`redblue_git/p2_git_chain_stress_closeout.md`（定序+本机红线）｜
> `adjudications/S18-R1~R4`（四张裁定书，均待 Owner 签）。
> **授权边界**：F1/F3/F4/F5 + F2 前置件=免签施工；F2 通道数本身、F5 白名单净增、S18-R1~R4=Owner 门位（只提案不自签）。
> **本机红线**：压测 worker ≤20，禁跑 50+ 档（P2 三度压死宿主，50/100 档正式关闭）。
> **并发纪律**：altdata 会话本机并发——改前 `lock_files.py acquire`、毕后 release；子代理禁 commit，主会话统一走 GitCommitGateway（一战场一批）；热文件 `safe_write_text`。

## 0. 提速前后对照（Owner 必交件①·实测非外推）

> 数据真源：`.runtime/audit/commit_block_events.jsonl`（`commit_ok_sample.total_ms`=全程墙钟：锁等待+门禁链+提交，n=37）+ `git log`（dev 实测提交率）+ F3 gate-chain 耗时榜。聚合脚本 `.runtime/tmp/throughput.py`。

| 指标 | 提速前（P2 基线） | 提速后（本战役实测） | 说明 |
|---|---|---|---|
| 每笔墙钟 P50 | —（基线未采样） | **39.1s** | commit_ok_sample n=37 全程墙钟 |
| 每笔墙钟 P90 | — | **115.9s** | 重试环/锁排队尾延迟（F5 预检快败正对此尾） |
| 门禁链 P50（gate-chain） | **41.6s**（全史） | **29.0s**（近段） | F3 实证 604f414846 口径推广+A1 memoization，**-30%** |
| 串行天花板 | 24/h（门禁常数） | **92/h**（3600/P50 39.1s） | 提交锁串行→全场吞吐=3600/每笔墙钟 |
| 锁容量（非瓶颈） | 870/h @10w | 870/h @10w（540/h @20w，饿死 45%） | P2 实证：**锁不是瓶颈，门禁是**（24/h=门禁常数） |
| dev 实测提交率 | ~24/h（持续） | 峰值 **18/h**、近段 11-18/h、8h 均 9.2/h | 8h 窗含 tdchain 大合并扰动（03-04h）+低活跃时段（20-22h 各 1 笔） |

**结论（诚实口径，勿粉饰）**：
1. **提交链本身已接近 100/h 串行能力**（天花板 92/h，锁容量 870/h）——24/h 的病根是**门禁链墙钟 × 串行 × 重试环**，非锁。
2. **本战役已落地杠杆**（摩擦+重试类消除，非通道扩容）：F1 派生提交折叠（R-01 派生写入簇 222 行堵点根因端掉→NOTHING_TO_COMMIT/冲突/index.lock 重试消失）；F4 架构图生成器 57.4s→28s（-51%）；F5 DC 预检快败（违规 ~2s 锁外快败 vs ~40s 烧全链，正打 P90 116s 重试尾）；F9 队列新件死信治本（免返工）。门禁链 P50 41.6→29.0s（-30%）即其合力实证。
3. **100/h 待 Owner 杠杆**（本战役禁动，只提案）：①**F2 通道扩容 k=4**（S18-R3 待签）——串行 92/h × 并行通道=破百的唯一结构性路径；②**门禁退役/解析缓存**（§4.2 退役审计=Owner 门位 AI 禁用；F3 残余 parse-cache 治本挂 harness 门）——把每笔墙钟 P50 39s 压到 <36s 以下。
4. **实测 12-18/h < 24/h 基线**之因：近 8h 是**大合并扰动窗**（tdchain 12 stash sweep+32min 合并晾置，见 B-INCIDENT）+夜间低活跃时段，非链退化；剔除扰动后活跃时段（23h/01h/03h）达 11/14/18 笔。

## 1. 环节全景骨架（施工包×状态×证据）

| 包 | 名称 | 授权 | 真源判据 | 依赖 | 状态 | 证据 commit | 子簿 |
|---|---|---|---|---|---|---|---|
| F1 | 衍生提交并入原子化 | 免签先干 | R-01 / S18-R2 / 判据书 F1 | — | ✅ 已落地 | `fe47296d` | `F1_derived_commit_merge/DESIGN.md` |
| F4 | 生成器并发化 | 免签 | R-08 / 判据书 F4 | 与 F1 同文件需协调 | ✅ 已落地 | `025df945` | `F4_generator_concurrency/DESIGN.md` |
| F3 | 头部门禁 diff 化 | 免签（通道类前置） | R-03 / S18-R3② / 判据书 F3 | 需实测耗时榜定白名单 | 🔶 挖矿封矿（命题已落地，残余治本挂 harness 门） | — | `F3_head_gate_diff/DESIGN.md` |
| F5 | DIRECTORY-CONTRACT 摩擦前置化 | 免签（白名单净增=Owner） | A2 堵点本 16 次阻断 | — | ✅ 免签代码核已落地（DC 入预检白名单+建议合规目录指引，语义零改，9 测全绿）；docs/_working/ .json 净增=Owner 裁定提案 S18-F5-①（不自签）；工作簿新件挂热注册表 token 待清 | `1fb04f6e` | `F5_dc_preflight/DESIGN.md`（已恢复·待 token 提交） |
| F6 | 堵点本全量排查修复 | 免签 | 三本全量 4325 行 | 先 F1 后 F6 | ✅ 已落地（3572 行四态归属·零无主） | —（挖矿+总账，无代码改） | `F6_bottleneck/DESIGN.md` + `lane_reports/F6_堵点总账.md` |
| F2 | 前置件（lease 续租+双通道压测+热文件单通道闸） | 免签部分（通道数=Owner 签 S18-R3） | R-02/R-04 / S18-R3 | 时间不够可砍 | ✅ 前置①②③④施工完毕全绿（①lease 续租=F9 交付；②同域同文件双通道并发压测 9 测绿；③热文件单通道闸 `channel_key_for_files` 域映射在案；④exit-burst 零丢失零双落实证）；⑤「7 天>40 车道」=观察窗件如实登记留 Owner。**「k=4 通道就绪，待 Owner 签 S18-R3」** | `727ad32a54` | `F2_prereq/DESIGN.md`（待 token 提交） |
| **F9** | **加餐缺陷包：队列 untracked 新文件落地死信治本（SerializerLease 续租+活体不抢）** | **免签（来源 st-consrep2-20260917）** | **Owner 夜令 #9 §3-§8 / 裁定#280 对齐** | **交付 F2「lease 续租」前置件** | **✅ 已落地** | **`3c853303da`（+#ARCH-330 `6ea82b9cfb`）** | **`F9_queue_newfile_deadletter/DESIGN.md`（已恢复·待 token 提交）** |
| H | 重建 harness + 改写 S18 判据书悬空验收行 | 免签 | P2 收官报告 §四 | F2 验收依赖 | ✅ 已落地（harness 自 `.runtime/tmp/closeout_residue_20260918/rb2_harness_preserved.py` 重建至 `.runtime/tmp/rb2/harness.py`，39193B，py_compile+--help 通过；判据书悬空验收行 `--channels 4` 改写为 `--workers 20 --mode enqueue`+通道维如实说明） | `727ad32a54`（判据书行同批） | （并入 F2 子簿 §6.4） |
| R | 最终报告 + 两轮循环零问题核验 | — | 通宵 SOP §6/§9 | 全部完成后 | 🔶 施工中（全部免签包已落地/封矿，报告+两轮核验进行中） | — | `90_report.md` |

## 2. 施工调度（线内先挖后干、线间并行流水）

执行序（尊重依赖）：**F1 → F4 →〔批量派分析子代理：F6 聚合 / F3 实测榜 / F5 DC 取证〕→ F3 → F5 → F6 → F2 前置 → H → R**。
- F1/F4=主会话自挖自建（地基活，付费档级别审慎，错了很久才暴露且伤全仓）。
- F6 聚合（4325 行账本）/F3 实测榜/F5 DC 取证=读密集分析，派子代理并发（有效并发 2-3，波次派发），主会话收口施工。
- 每包：挖矿（读透代码+测试）→ 子簿（六向台账+挖矿日志+自审闸三态）→ 挖干即施工 → 提交 → 写台账。

## 3. 战役批次志

| 批次 | 时间 | 内容 | 落地 commit | 备注 |
|---|---|---|---|---|
| B0 | 2026-09-18 | 冷启动+四真源读透+环节骨架封矿+lock  acquire（gateway/validate） | — | reaper 存活（killed=0），Python 3.12.8，锁区 CLEAN 起步 |
| B-F1 | 2026-09-18 | F1 衍生提交并入原子化（rules_integrity 重登记→同 commit 折叠） | `fe47296d` | 免签先干 |
| B-F4 | 2026-09-18 | F4 架构图 15 生成器依赖拓扑分 3 波并发（cap=4，钳[1,20]） | `025df945` | 墙钟 57.4s→~28s，byte-identical（serial×2 证 4 易变非并发引入） |
| B-F9 | 2026-09-18 | 加餐缺陷包：队列 untracked 新文件落地死信治本——SerializerLease 活体不抢 + renew 心跳 + drain 逐项续租 | `3c853303da`（+#ARCH-330 `6ea82b9cfb`） | 根因=租约竞态（活体超 TTL 被抢→双 drain 毁 worktree→clean -fd 删新文件）；queue 83/landing 37/integration 29 全绿；与裁定#280 对齐，未塞 _TRANSIENT_GIT_MARKERS |
| B-F3 | 2026-09-18 | F3 头部门禁 diff 化挖矿封矿：604f414846 口径**已推广**（裁定#279/#273/#214+A1，ERRCODE mean 16.09→4.75s 实证）；头部 git-内容门禁 P50 合计 **7.62s<10s 判据达标**；真天花板=113 门禁长尾墙钟（gate-chain P50 41.6s 全量/29.0s 近段，P90 123-127s） | —（挖矿，无代码改） | 残余治本=进程级内容哈希 YAML 解析缓存（1.67MB 注册表被 7+ 门禁重复解析），设计封矿挂 Task #7 replay harness 门；真 100/h 杠杆=门禁退役（§4.2）=Owner 门位 AI 禁用，出提案不自签 |
| B-F6 | 2026-09-18 | F6 堵点本全量排查：三本 **3572 行四态归属·UNCLASSIFIED=0（零无主）✓**。(a)已覆盖 1983（本战役 F1/F4/F9 已治本 ≈167：R-01 派生写入簇 222 行根因被 F1 端掉、F9 pathspec 22、F4 freshness 36；R-06 告警自激纯噪声 1095=全场 31%）/(b)净新病灶仅 26（gate_id 归因观测缺口，非吞吐阻断，登记留 Owner）/(c)门禁判对=使用摩擦 1433（全路由 F5，语义不动）/(d)残留/基线 130 | —（挖矿+总账，无代码改） | 已知疑点全消解：「空 gate_id×221」=commit_slow/ok_sample 性能采样非堵点；NOTHING_TO_COMMIT×87/git reset×48+18/冲突×30 根因=`rules_integrity_db.json` 派生写入（R-01）→F1 已治本。一页全场总账=`lane_reports/F6_堵点总账.md`（Owner 必交件）；真 100/h 杠杆=门禁退役（§4.2）=Owner 门位 |
| B-F5 | 2026-09-18 | F5 DIRECTORY-CONTRACT 摩擦前置化：DC 入 `PREFLIGHT_GATES` 白名单（输入面审计 PASS=files 清单 ∪ 磁盘内容，内联 ≤500 只检本次 files、零 git diff --cached/零共享暂存依赖，>500 退 --all-files 与锁内权威链同行为）+ `_ESCAPE_HINTS` 建议合规目录（.py→scripts/src、.json→转 .yaml/.csv 或挪 .runtime/data、余查 directory_contract.yaml）；**语义零改**（锁内 DC(30) 仍 fail-closed 权威，预检只锁外 3-5s 快败）；9 测全绿（新增 DC 白名单+指引+阻断渲染测） | `1fb04f6e` | 主簇实证=DCR-005 .py/.json 误放 docs/_working/（allowed=.csv/.html/.md/.yaml；A2 堵点本 16 次+本账 58 次 DCR-005）。**docs/_working/ allowed 净增 .json=Owner 门位**，只出裁定书提案不自签（见 F5 子簿 §Owner裁定项）。工作簿新件挂热注册表 token（外来 st-cohort-ledger 在途）待清后补登记 |
| B-INCIDENT | 2026-09-18 | **外来 pre-merge sweep 删件事故+恢复**：st-tdchain-20260917 合并前净窗 sweep（`git clean`（-fd 档）+12 个 stash）**删掉本战役全部 untracked 工作簿**（F3/F5/F6/F9 DESIGN.md + Owner 必交件 `F6_堵点总账.md`），并把 3 个 tracked-改动的 F5 代码件卷进 `stash@{1}`（tdchain-sweep8）。**恢复**：①tracked F5 代码件用 `git restore --source=stash@{1}` 外科式还原（**不 pop**——该 stash 混 26 个外来 WIP，pop=搭便车），pathspec 隔离提交 `1fb04f6e`（核实零搭便车）；②untracked 工作簿从会话 transcript jsonl 提取重写，并备份到 `.runtime/tmp/flash_speedup_workbook_backup/`（gitignored，免疫 clean -fd） | `1fb04f6e` | **教训**：共享主区 untracked 交付件对他会话 pre-merge `clean -fd` 无防御（正是 F9 缺陷类，但 tdchain 手动 sweep 走的是另一码路）；交付件未提交前 MUST 在 `.runtime`（gitignored）留备份。12 个 tdchain/nightcoord sweep stash 仍待其本人 pop 恢复，本会话未碰（§3.4 他会话在途不代修） |
| B-LEDGER | 2026-09-18 | 总簿回填批：§0 提速前后对照（Owner 必交件①）+F5/F9 hash 回填+B-INCIDENT 事故行——首次入队尝试被 BLUEPRINT-FORMAT 外来连坐挡（见 B-INCIDENT2 病灶），走队列落地 | `b5cd9ff505` | 队列正门实证：serializer worktree 只物化本项 blob，外来 staged 连坐结构性免疫 |
| B-SKIPMAP | 2026-09-18 | **预检逃生旗映射补齐**：`--allow-overlap` 已传入但 `_preflight_skip_set` 漏配 SESSION-REQUIRED 映射→带旗仍假阳性快败（本会话台账提交三连挡取证；违反 commit_preflight MODIFY-GUARD「映射与 argparse 旗标一一对应」）。修复=一行映射+4 例纯函数测试；锁内 gate 语义零变化 | `be934b079d` | 附带实证 pid=0 逻辑会话心跳 90s 新鲜度窗口竞态（enqueue 预检在注册前跑）——SESSION-REQUIRED 净新病灶面，登记 F6 附录 |
| B-F2 | 2026-09-18 | **F2 前置件施工**：①lease 续租=F9 已交付；②「同域同文件双通道并发」压测（双 drain 线程 barrier 同起跑争 lease：零丢失/零死信/零丢失更新/FIFO 定序/单写者）；③热文件单通道闸在案（`channel_key_for_files` 域映射：注册表族/ROOR/AGENTS.md/standards.yaml→单一热通道，同域同文件双项必同键，k=1 零行为变化）；④exit-burst（在途突发注入同轮消化+lease 释放瞬间双自举竞态：12 项全 done/零双落/landed_id 全唯一）。测试 F2 9/9+文件级 46/46+test_commit_queue 83/83 全绿。**「k=4 通道就绪，待 Owner 签 S18-R3」**；⑤「7 天>40 车道」=观察窗件如实登记 | `727ad32a54` | 判据书 F2 悬空验收行同批改写（harness 重建记录+--channels 维说明）；F2 子簿=`F2_prereq/DESIGN.md`（待 token） |
| B-INCIDENT2 | 2026-09-18 | **外来陈旧索引污染×2（第二次删件类事故，未遂）**：他会话 bulk `git add`（陈旧 worktree 快照）把①本簿已落地版回退 23 行 staged（q-0006 落地后索引仍是旧内容）②`tests/git/test_preflight_skip_mapping.py` staged 为 **D（删除）**+真文件留 untracked——任一非 pathspec 提交即回退总簿/删掉已落地测试。**修复**：`git restore --staged <本会话两路径>`（仅索引、不碰外来 staged 其余件），核实 worktree==HEAD、be934b079d 内容完好 | —（防御性修复无提交） | **病灶登记（净新，留 Owner/F6 附录）**：共享主区索引无「已落地 commit 路径保护」，bulk add -A 可静默回退他会话刚落地内容——与 BLUEPRINT-FORMAT own_scope=false 连坐（一个外来占位 .py 挡全场提交）同属「共享暂存区无主面」病灶族；AI 侧纪律=每次队列落地后核 `git status --porcelain <本会话路径>`，见陈旧 staged 即 restore --staged |

| B-T1BACKUP | 2026-09-21 | **T10 备份目录灭失登记+补丁重建（tc_03 卡步骤0）**：`.runtime/tmp/flash_speedup_workbook_backup/` 已消失（tc_03 卡 09-21 实测 find 全仓零命中；原存 9 件工作簿备份+原文 2.1 节 patch 64 行——工作簿本体已随 T9 入 HEAD `63802383af` 无损失，patch 面随在盘编辑存活）。原文 2.1 节在盘编辑（session_worktree.py +8 / 测试 +26，WORKTREE-BASE-CONFLICT 码2/测3）成唯一副本，本班重建补丁备份落 `docs/_working/flash_speedup/t1_worktree_base_conflict_patch_backup.md`（.md 载体，63 行 diff 从在盘实态导出可 git apply 重放） | （本批） | 原文 2.1 节落地仍须先过裁定 #369 merge 治本（X-5），禁 ack 白名单私开 |
## 4. 挖后自审闸（总簿级，三态裁定）

- 量尺=终局全貌（夜间 50-100 车道并发，提交吞吐=全项目开发速度）。
- 三态裁定：**施工**（F1/F3/F4/F5/F6/F2 前置全部进入施工；F2 通道数/F5 白名单净增/S18-R1~R4=挂起待 Owner 签，只出提案）。
- 过度工程三问：①是否消灭人工参与？是（衍生税自动并入、门禁自动 diff 化、堵点自动归类）。②是否引入第二真源？否（复用 604f414846 差分口径、复用既有 batcher/register）。③现状规模小是否成为封矿理由？否（按终局 100 车道判，非按当前 24/h）。

## 5. 待裁定清单（起床报告汇总，目标=空）

| # | 案由 | 去向 | 五级分析摘要 |
|---|---|---|---|
| P-1 | F2 serializer 通道数 k=4 | Owner 签 S18-R3（裁定#320） | 通道数=Owner 定值（S18-R3 红队复验：lease 续租先行+热文件单通道+TTL 心跳续租）；本战役只落前置件，判据全绿后写"k=4 就绪待签" |
| P-2 | F5 DIRECTORY-CONTRACT 白名单净增 | Owner 门位 | 只出裁定书提案，不自签（白名单净增=注册表门位） |
| P-3 | S18-R1~R4 四张裁定书 | Owner 签 | 均 status=待 Owner 签；F1 免签先干（判据书授权"F1 任何时候可做"） |
