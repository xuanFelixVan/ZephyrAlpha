---
ttl: task_bound
---

# 战役当前态快照（防上下文压缩接力误判 · 统筹复核为准）

> 更新 2026-09-25 ~01:4x ｜ 统筹 st-commitspeed-tbl-20260924 ｜ 接手者先读此再读 decisions_log 尾。
> **凡"已落地"以 `git show HEAD:<file>` 实测为准，凡"在飞"以队列目录 + flag 为准。**

## 零、队列大局（01:4x 实测）
- 46 袋 pending，**B4 FIFO 实证在岗**（pending 按 created_at 升序，非字典序——t0-matrix 会话的"0925 前缀饥饿"判断有误，纯排队慢约 3 袋/时，无结构性饥饿）。
- 本役批次位置：**0027(W4)#10 / 0028(注册)#13 / 0029(p13重投)#43**。
- 兄弟会话实况：t0-matrix 0034/0035 在队（其格式修写经 Owner 批准、AST 等值闸流程合规；判断为对，唯饥饿论断错已勘误）。

## 一、已落地进 HEAD（真值已核，早期批次）
批一装表+D3+B4(0005)／钩 T6(0008)／D4(0010)／批六 T5/M2(0012)／0009；belt 四路并发实证。详见 decisions_log。

## 二、在飞/已备（本会话产出，全部待队列）
- **0027 = W4 止血重投**（gateway +14 纯增、红3/绿3+103 passed、A/B 判 UNRELATED 锁测试、frontmatter 3/3）。落地判据：`git show HEAD:src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py | grep prev_gateway_env` 非空。
- **0028 = replay 三件+设计文档的注册先行批**（3 token+2 翻译条目，纯插入，scratch csx-replay 净基底）。落地后投内容批：`src/zephyr/gov_enforcement/commit_gates/_tree_view.py`+`scripts/governance/replay_gate_verdicts.py`+`tests/governance/test_gate_replay_harness.py`+`docs/_working/commit_speedup_campaign/50_replay_baseline/r1_design.md`（**已备好在 csx-replay worktree**，ruff/frontmatter 净）。
- **0029 = p13-a 重投**（001 死因=测试头 `# [TTL] disposable` 非法→已改 permanent；csx-p13 重投）。
- **包3 P3 = 施工完在 `.worktrees/csx-p3b`，10/10 红绿测试绿，等 0027 落地后入队**（gateway 同文件串行纪律）。7 文件：VI head/snapshot 双态 check+A1 批读+A2 CHANGING_IN_COMMIT(MQ-2 own-scope)+A3 _GATES_DIR 真身(17→136)+A3b stderr+check() MANIFEST_DEGRADED 阈值红(MQ-3 比草案加严)+landing B1/B2 mode 分派+gateway post-flush 顶部早退+C2 per-spawn env+reconciliation head 分支+ritual 摘出+flags 新键（出厂 snapshot 零行为变化）+新模块 `derived_dirty_ledger.py`。**实弹冒烟曾抓草案 bug：cat-file --batch 应答头是 oid 非请求路径，已改按序配对**。enqueue 用 worktree-root=csx-p3b；message 可引 decisions_log 00:5x 行。⚠ 入队前重验基线：若 dev 已推进到含 0027，直接投（3-way 合并同文件已证）；若担心，re-pull scratch 重贴（W4 同法）。

## 三、后台长跑与子代理
- **重放 100 基线**（包8/9 before 照）：detached 进程跑 `scripts/governance/replay_gate_verdicts.py --since 100 --max-seconds 21600 --noise none`，输出 `.runtime/tmp/csx_replay_verify/replay100/`；01:3x 时 5/100、~310s/笔 ⇒ 6h 预算约覆盖 70 笔，到帽后按 r1_design §4 分段补跑剩余。reaper keep 已加 `replay_gate_verdicts` 令牌。
- **子代理①包13 余下**（救 csx_t14_wt：对账生成器+own_scope 机生补全，ms 块已被 0029 覆盖勿重做）：任务书含全红线，产出=qid+报告。
- **子代理②包10 attempts 退避**（commit_queue.py 毒药件退避，禁碰 gateway 门前置短路＝在飞冲突）：任务书含全红线。
- 两代理完工通知会回来；它们的 decisions_log 由统筹统一补记（防 CAS 争抢）。

## 四、后续施工序列（已定案）
1. 0027 落地→grep 验 W4→**投 P3（csx-p3b）**。
2. P3 落地→**包5**（D2 §4/§8 已读毕，真源=10_d1_d2/D2_env_flag_leak.md）：步1 internal_call 形参（run_git/_run_precommit_channel 已有注入点）→步5 sanitized_spawn_env/_trusted_git_env 显式定 C2→**最后**删 W1(landing:1577/1641)/W2/W3(gateway:3510/3557)。T2 消费者穷举+T3 真钩子端到端同批测试；T4 残留口径=W4 finally 还原块+两处 per-spawn 赋键。禁跑 test_ops_guard_red_team.py（地雷），其判据以 ops_guard.py:656 静态读+forged 测试替代验证并如实留痕。
3. 重放 100 完成→**包8**（三簇合并，判据=重放逐台 verdict 全等，前后对照）→**包9**（own-tree，15 台全索引门分道）→**包7**（缓存键）。Owner 令：只合并/降档/diff 化禁删。
4. 包11 合批去抖（commit_queue.py）→包14 红蓝 7 场景→包15 收尾（文档袋按小写+token 统一落、99_FINAL_REPORT.md 含回收测算+MQ-1/3 呈 Owner 两行、清 csx_* 脚本、`git worktree remove` 各 scratch、release claim 读 .ailocks/registry.json 判成）。
5. MQ-1/MQ-3 的"呈 Owner 项"（DB 出库、--auto-fix 通道）汇总进终报附录，目标零悬案。

## 五、坑与处方（本会话新增）
- `git cat-file --batch` 应答头=oid 非请求路径；missing 才回显请求串。按请求序配对（git 保证序一致）。
- `python -c` 内嵌多行字符串会被换行打断＋heredoc 吃反斜杠——一律 Write 成 .runtime/tmp/*.py 再跑（红线10再验证）。
- tools 的 REPO_ROOT 硬编码主仓（add_module_translation）：在 scratch 用工具副本跑才落 scratch；主区误写的自身条目留主区无害（合并器按键去重），勿冒险热改主区共享册。
- 新文件名小写 snake（N-13 拒大写）；`# [TTL]` 值只许 permanent/task_bound（0026 死因）。
- 锁家族测试（TestGlobalCommitLock*）在 worktree 环境存量红+时序脆弱＝UNRELATED 族（A/B 双证），勿误归因。
- flags.yaml 在 enqueue 用 scratch 基底（主区有他会话 MM 在途）。
- 禁改四类已解除但 gateway 串行纪律在：同文件在飞批未落地前，下一批不投同文件。

## 六、红线复述（接力勿犯）
禁 kill belt（4 路活）；不删门禁（只合并/降档/diff 化）；不改判据凑绿；`[GW:]` 不可伪造；禁插队/绕门/裸 commit/plumbing；主区禁 merge 一律 enqueue；tests/ 免 token 其余新建 7 格式必 token 先行；pytest 带 `-p no:cacheprovider -W ignore::pytest.PytestConfigWarning`、basetemp 落 .runtime/tmp/csx_*；**禁任何 worktree 跑 test_ops_guard_red_team.py**；scratch：csx-w4b(W4)／csx-replay(replay)／csx-p3b(P3)／csx-p13(p13)——分包15 按规程 `git worktree remove`。

---

## 七、双总筹合流补记（04:1x，Max 会话 sess_0e6ffec8 = 19:00 接手的续跑班）

> 发现双总筹并存（本快照作者 sess_add5455e 深夜班 + sess_0e6ffec8 续跑班）= 重复投递（S1 前置件/T7 两例）的根因。以下为续跑班的增量，已与上述序列合并：

**续跑班已落地（HEAD 实证）**：
- **3bec1e5244 = S1 前置件三源抢救+复原**（tree_view 1015 行/replay 驱动 730 行/红证测试 307 行）——**本快照 §二的 0036 内容批已由续跑班以直连完成（26 轮门禁全通实录见 decisions_log 04:1x 行），0036 若在队属重复投递，死信即弃勿 requeue**。
- **selfcheck 100 笔满分**：commits=100/files=1522/byte_mismatch=0/worktree_reads=0（.runtime/tmp/csx_replay_selfcheck100）——与 §三 的 verdict 重放 100 互补（selfcheck=安全网自证；verdict 重放=全册基线，两者都要）。
- **T7/B2 缓存键改造**：键去 staged_tree_sha/head_sha 改 own blob sha 合集，判别测试 2 例+既有 13 绿（**§四 包7 已完成，勿重做**）；直连被拦 AUTO-ENQUEUE=**q-0046 在队**。flag 出厂 OFF。
- 四工满速实证（Owner 授权 A 手工换血后 processing=4，吞吐 20 件/时）；D3 真、D4 探针全 0。

**继续有效的分工裁定**：P3（csx-p3b）归深夜班按 §四 序列投递（gateway 串行纪律）；重放 100（后台 30/100 中）归深夜班收口；续跑班不新开与 §三相重的车道，专注收口与红蓝。

---

## 八、深挖 R1 结论与行动排序（04:4x，Owner 令"挖到连续两轮无可优化"）

真源=60_deep_dive/DEEP_DIVE_R1.md（+r1_data/ 十个 YAML，脚本 csx_deep_01..09 可复跑）。

**R1 关键更正**：belt_daemon ModuleNotFoundError 仅启动期 2 次（transient，守护现健康 drain 在动）——"drain 半瘫"系旧日志误读；喂料饥饿 8553 次 claim_none 主因是熄火期（06:00-21:46）的长窗，当前四工时代需 R2 重测占比。

**行动排序（预期回收/天）**：
1. 重试环 723min 白烧链+重试占阻断 58% ⇒ T10 廉价门前置短路（BLUEPRINT-FORMAT/TTL 等文本快检排最前）+阻断快速分类。
2. precommit 1200s 超时×3+hook 成本与件数脱钩（1 件跑 346/657s）⇒ hook 挂 own-scope+超时自适应 ≈ 80-100min/天。
3. 死信分诊代理在跑（428 封四态判定；"291 封/3915 文件蒸发"论待核——requeue 换新号会造成假阳性）。
4. S1 接线（续跑班持安全网+100 笔 selfcheck 满分）⇒ 单文件链 64s→<25s。
5. residual 未解释 ~123s/笔：需落地侧锁等待插桩（全局 commit lock×32 次等待/landing_staleness 130 条/对账扇出）——R2 前置。
6. 埋点缺口："-" 无门号阻断 67 次；ms≥1 过滤已修（0026）但 R2 需复测可见率。

**R2 复测判据（连续两轮无可优化的第一轮）**：上述 1-4 落地后，重跑深挖脚本全集对照 R1 数字；连续两轮各环节无可回收分钟>5min/天即达标。

---

## 九、死信分诊定案（04:4x）

- **"3915 蒸发"证伪**：5222 条文件条目中 2554 条未蒸发（812 逐字节一致+1742 HEAD 已有更新版），真缺失 2079 条（52%），但 **5217 条有 blobs/ 内容寻址快照**（抽检 3/3 完整）＝零真实灭失，随时可恢复。
- 四态：已复活 223｜可回队 27（**其中 9 封含 head_diff 覆盖风险须裁剪至 head_missing 子集**）｜应废弃 119（留 Owner 确认）｜归还属主 59（6 存活会话：st-cmd/st-commitspeed-tbl 等）。
- **总包裁定**：不批量自动 requeue（防旧快照覆盖 HEAD 新活+门禁死信循环）；可回队清单留终报呈 Owner 圈定范围；归还需属主的 59 封由各属主会话按清单自查。全清单=60_deep_dive/dead_triage.yaml。

---

## 十、T10 排查补记（04:5x）

- **hook 冷启动税证伪**：实测单 hook（import zephyr 全家桶）0.49s × 69 hooks ≈ 34s——lazy import 已优化，不是 346/657s 极值的主因。
- **下一个待查假设**（R1 报告"hook 成本与件数脱钩"线索）：极值样本（1 件 346/657s）的 hook 明细需逐 hook 计时才能定责——pre-commit 无逐 hook 计时，需套一层 `time` wrapper 或启用 pre-commit 日志（PRE_COMMIT_DEBUG）取样。**派单前先取证，勿直接动 hook 排序**（上一假设已证伪一次）。
- 簇1 册解析缓存批（create_guard+测试 2 件）在队，落地后 CREATE-GUARD 85s 均值应显著回落——R2 复测对照点之一。

---

## 十一、续跑班第二窗口战报（20:3x，S1 接线完成待落地）

**已落地（HEAD 实测）**：
- 簇1 缓存 6e47377b8f：落地后 CREATE-GUARD **p50 4.1→0.7s、mean 197→45s**（6 链样本）——R2 对照点①已正向。
- T7 缓存键（_own_content_hash 在 dev）。W4/D2/P3/13 重投（gate stats 去 1ms）全落。

**在队**：
- **0119 = S1 接线原子袋（8 件）**：前置件四件（cherry-pick 自 3bec1e5244——**它曾落旧分支未进 dev**，"落地"判定必须 `git branch --contains <sha>` 含 dev）+接线三件（gateway 视图替身 flag immutable_tree=false/判别 4 例）+册。0118 前身死于 IMPORT-INTEGRITY（import 先行于目标——#ARCH-CROSS-COMMIT-ATOMICITY 正确拦截），改同袋原子重投。
- 落地后：flag OFF 合并完成 → **呈 Owner 翻 flag** → 重放 verdict 100 全等 → S1 生效验收（单文件链 64s→<25s 实测）。

**T10 取证补记**：pre-commit run 单文件全链实测 **>280s 未跑完**（exit 124）——R1"整链分钟级"再实证；逐 hook 计时需 PRE_COMMIT_DEBUG 后台长跑取样（前台 5 分钟窗口不够），转后台批。

**R1 行动剩余**：hook own-scope（取证后）/死信滚动分诊（+171 新增）/R2 复测对照（簇1 塌缩已正向）/红蓝 7 场景/终报。

---

## 十三、总包值守态（00:27）——全部车道状态一览

**已落 HEAD（本役代码面 100% 流通）**：批一(D3/B4/装表)/T6/T5/T7/簇1/W4/D2/P3/T14/B5/IBT-22/S1 接线 0124（flag OFF）。红蓝 token 册 0131 已落。

**在队**：0131 后续=治理内容批（chain_rb 41753 自动投：2 sh 收窄+23 测试+报告）；T13 v3 双袋待 token 册后重投（0126/0127 死信链）。

**在跑**：红蓝鲁棒组代理①②③；T10 探针完（589s+120s 样本）。

**Owner 呈报（醒后第一读=快照 §十二）**：flag immutable_tree 一键翻转命令+回滚；DB 出库；死信 119 废弃/59 归还；T14 own_scope 终裁；HMAC 归属载体待办。

**终报骨架**：99_FINAL_REPORT.md 已建（数据回填至 00:27）。

**R2 复测前置**：等治理内容批+T13 落地 → 重跑 csx_deep_01..09 脚本全集 → 对照 R1（60_deep_dive/DEEP_DIVE_R1.md）→ 连续两轮无可回收 >5min/天 = Owner 终止条件达成。

**值守循环守则（接手者必读）**：查快照尾三节→查 decisions_log 尾 10 行→查队列 status→按 §八行动排序推进→每完成一项追加 decisions_log（防 CAS 争抢=只追加不改行）。
