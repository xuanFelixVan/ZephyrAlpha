---
ttl: task_bound
---
completes_when: 每条 GAP 有 instrumentation 落地或缺陷关闭记录，或经裁决显式出圈；S1/S2 中所有 evidence: MISSING 节点清零
title: S3 清单薄弱点与盲区（封矿判据：每项给出可关闭它的插桩方案）
owner: ZephyrAlpha-Owner
session: st-commitspeed-skeleton
date: "2026-09-24"
---

# S3 盲区账（GAP 台账）

> 规则：S1/S2 中任何 `evidence: MISSING` 必须映射到本表一条 GAP；本表清空 = 阶段骨架封矿成立。
> 每条给：现状 → 需要什么插桩才能关闭 → 归属建议（车道）。

| GAP | 盲区 | 现状证据 | 关闭所需插桩 | 建议归属 |
|-----|------|---------|-------------|---------|
| G-01 | **锁内相位计时缺失**：ST-06~09 全程混在一个总时长里，无法回答"门禁链 vs hook vs git add 各吃多少" | `.runtime/audit/commit_block_events.jsonl` 只有 gate_chain_ms 与 total_ms 两级；commit_slow 事件 threshold_s=60 但无相位分解 | 在 `_GlobalCommitLock` 获取/释放与 `_run_precommit_channel`/`_commit_locked` 进出四点位插 phase timer，写新 jsonl 账（含 lock_hold_ms/hook_ms/git_op_ms） | 骨架车道自留（下游全依赖它） |
| G-02 | **68+ pre-commit hook 无逐 hook 计时**：ST-08 是黑盒，链内慢 hook 无法点名 | `.pre-commit-config.yaml` 无 verbose 账；hook_tracked_drift.jsonl 只记漂移不记时长 | pre-commit `--verbose` 输出解析入 `hook_timing.jsonl`，或换 in-proc 计时垫片 | 门合并车道 |
| G-03 | **队列/落地路径无 worker 归因与分段计时**：ST-13~15 每件耗时、serializer vs pool 代际实际启用哪条，不可从账面判定；ST-14.6 每路径锁仅有战役记忆、无本轮代码行锚 | `drain_queue`/`drain_queue_pool` 无 per-item 时长落账（本轮审计目录未见对应 jsonl） | 落地结果对象加 `worker_id + phase_ms{sync,apply,merge,cas,converge}` 字段并落 jsonl；每路径锁定义处 grep 重锚 | 队列车道 |
| G-04 | **post-commit 同步钩链四件套无分段计时**（git lfs / regen_yaml spawn / POST-COMMIT-GUARD / Qoder tracker），且 Qoder tracker 是外部绝对路径 node runtime，成本不受本仓控制 | `.git/hooks/post-commit` 全文静默（`>/dev/null 2>&1 || true`），失败与慢皆无痕 | 钩内各段 `date +%s%3N` 差分写 `.runtime/audit/postcommit_hook_ms.jsonl`；tracker 单独打点评估去留 | 封矿收口 |
| G-05 | **记账回灌放大系数无度量**：一次业务提交引发多少追加提交（tokens/翻译/depgraph/再生件）不可测 | ST-20/ST-21 机制在案，无比值账 | 以 session 为单位给 commit 打 lineage 标签（如 `[LIN:qid]`），统计 commit/业务件 比值 | 骨架车道 |
| G-06 | **ST-01 会话建立成本未计时**（worktree add + 骨架同步） | 无账 | cmd_create 内两段计时落 creation 账 | 低优先 |
| G-07 | **worktree 本地袋陷阱无代码拦截**：在 worktree 里 `git_commit.py --enqueue` 投进无守护本地袋=假成功（历史坑，前轮记忆在案） | 本轮未在任何入口发现防御性检测 | enqueue 入口断言 queue_root 属于主区或存在守护心跳，否则拒绝并指路 `--worktree-root` | 队列车道（快赢） |
| G-08 | emergency_commit 旁路在骨架内只挂了 ST-04.5，其触发条件/审计链与 POST-COMMIT-GUARD forged 判定的完整闭环未逐行核 | `emergency_commit.py:342` 已锚，闭环段未读 | 专项走读一遍并回填 S2；确认它是否也应入 per-domain 队列设计 | 骨架车道 |
| G-09 | **batched_auto_committer 无归位**：不知道现在还有没有活的调用方；若有，它是隐藏的第二提交入口 | `batched_auto_committer.py:107` 存在，本轮未发现调用点 | 全仓 grep 消费方 + write_audit 观察一周；零消费则按内收判据退役 | 封矿收口 |
| G-10 | **计划任务面未逐条打开**：`register_gate_fulltree_audit_task.ps1`、`record_session_start_commit.py`、`start_paper_session*.ps1`、reaper 任务与提交链的相互作用只有 reaper 一条被证实 | `scripts/` 清单可见，内容未读 | 每个 schtasks 实体一次 `--status` 实测 + 触发日志挂接；产出一张"任务→触碰的提交链阶段"映射 | 骨架车道 |
| G-11 | **池并发系数无持续遥测**：曾实测并发恰 1.000（名义 k 未兑现），但当前无字段可持续复测，守护熄火亦曾零证据 | 前轮战役结论 + `_pool_heartbeat_loop:1975` 存在但消费方未锚 | 心跳账本加 effective_concurrency = Δ落地数/波次时长，周报警 | 队列车道 |
| G-12 | pre-push / post-checkout / post-merge 钩与提交链关系未核（`.git/hooks/` 实际存在这三个） | 仅列目录未见内容 | 逐一读 20 行判定是否触碰 dev/queue；触碰则入 S2 新子环节 | 骨架车道 |
| G-13 | **reaper×submitter 竞态无专账**：reaper 可杀提交进程（keep 清单是人工防御），杀在半程的 index/锁残留由谁收未证实 | `process_reaper.py` keep 机制在案；无 kill 事件与提交事件的 join 账 | reaper 落 kill 事件 jsonl（cmdline+pid），与 commit_block_events join | 运维收口 |
| G-14 | staging promote/TTL 执行点未锚定（收尾序列第 3 步只有宪法约定） | `.runtime/sessions/<sid>/staging/` 24h TTL 未见代码行 | grep TTL 清扫器落点；若无执行器=纪律空转，登记缺陷 | 收尾车道 |
| G-15 | ST-02.2 clone_guard 在提交链的调用拍点未锚（写前查发生在编辑器侧还是 gate 侧存疑） | CREATE-GUARD gate 在 ST-07 有账（单门数十秒级，见 gate_execution_stats ms 字典），但 `check_before_write` 入口未读 | 读 clone_guard 模块头 + 两处调用点回填 | 门合并车道 |

## 完备性自陈（置信度与证伪条件）

- **置信度：中高（对"阶段不漏"约 85%，对"阶段内子环节不漏"约 60%）**。阶段级已对五张外源清单（rule_bridge 全 20 模块、scripts 关键词全清单、pre-commit hook 全集、reconciler 注册表、守护/计划任务存在性）做过交叉归位，未归位者全部进了本表（G-08/09/10/12）。
- **证伪条件（任一命中即骨架不完备，回炉）**：
  1. 在 S1/S2 之外找到任何会移动 dev/HEAD ref、或写 `.runtime/commit_queue/`、或 spawn 提交进程的代码路径；
  2. G-01 插桩上线后，锁内相位之和显著不等于现有 gate_chain_ms+残差（说明锁内还有未清点环节）；
  3. G-09/G-10 走读发现第二个活着的提交入口；
  4. 任一定时任务实测在提交窗口内触碰 index/worktree（ST-22 清单漏项）。
- **已知取舍**：hook 内部逻辑（68 个各自）不单列子环节——它们是门不是阶段；`.runtime/commit_queue/` 活体目录本轮零接触（守护在消费），队列文件锁粒度从代码推断，待 G-03 插桩后用实账替换。
