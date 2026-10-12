---
ttl: task_bound
title: 四 GPU 工单施工班·班台账（st-gpuwo-20261011）
created: '2026-10-11T22:20:00+08:00'
sid: st-gpuwo-20261011
family_id: GPUWO-CAMPAIGN
---

# 四 GPU 工单施工班 班台账

令源：Owner《施工指令·四 GPU 工单调查与派工》2026-10-11 → 总指挥调查复核 §1 → 本单派工。
工单真源四张：`docs/_working/automation/20260917_wo_gpu01_night_mining_ollama.md`／
`..._wo_gpu02_kronos_batch_scoring.md`／`..._wo_gpu03_sft_gguf_ollama_chain.md`／`..._wo_gpu04_rl_execution_training.md`。

## 1. 角色与并发权限（按令自决）

- 本班=施工队总包：只读类（诊断/对账/考古）多车道全并行；写盘与入队按文件/域分区，同文件跨车道禁并发。
- 车道：`.worktrees/st-gpuwo-20261011`（分支 `ai/st-gpuwo-20261011/task-gpuwo-four-orders`，建车基线 a0e27b1ac3，
  心跳 daemon PID 39592）。提交唯一入口 `python scripts/git_commit.py --session st-gpuwo-20261011 --files <清单>`。
- 只呈批不代拍三类：B-007 消费/训练批复、软件安装（llama.cpp）、任何上实盘或消费接线。

## 2. 进场现场信号（已核，非本班引入）

1. **冷启动 cleanup 清了 7 枚死锁**，其中 4 枚落在本单禁碰面：
   `scripts/backtest/factory_grid_executor.py`／`src/zephyr/backtest/gpu_core.py`／
   `tests/research/backtest/test_factory_grid_executor.py`／`tests/research/backtest/test_l2_gpu_landing.py`，
   另 3 枚在 `docs/_working/mineloop_campaign/`（29、32 号件）与 `docs/_working/backfix_campaign/00_ledger.md`。
   清完后锁面=CLEAN（零 claim），而 GPU 化两车道
   `.worktrees/st-gpux-20261011`／`.worktrees/st-gpux2-20261011` 仍在册，
   reaper 现算仍报 PID 22656 心跳新鲜（cmdline 含 st-mineloop-20261010）。
   ⇒ **并发避让前提受损**：在册车道可能继续写盘但已无 claim 保护。本班不碰上述任何一件，
     并把它列入呈批面请统筹复核是否需令相关车道重新 claim。
2. **主区池面 657 条脏**（reaper 自报 worktree_changes=660>50），含本班要用的
   `config/resource_profile_registry.yaml`。按在册纪律：需要该册变更的施工**另起袋**，绝不随袋提交他人未落地条目。
3. **Ollama 现在可达**（v0.34.1，127.0.0.1:11434，8 模型在册）——但 10-08 那夜 LaneC 翻译腿全数
   `llm_error:ConnectionError`，见 `01_anchor_reverify_lanec.yaml` 新发现 N-1。

## 3. 四单进度（三态之一登记）

| 单 | completes_when 摘要 | 态 | 产物位 |
|----|--------------------|----|--------|
| §1 锚点重验+LaneC 体检 | 原令 §1①-④ + LaneC 产物完整性四态分诊 | 已完成（q-0003 落地 ccf6d852cc） | `01_anchor_reverify_lanec.yaml` |
| P1 GPU-03 | 情绪 SFT 模型回灌 Ollama 且夜窗情绪批切换自模型验证一轮 | **部分完成＋呈批**（步骤 1/2 完；步骤 3 三重实测拦路；现 adapter 实测 0.6290 vs 基线 0.7869） | `02_gpu03_dataset_and_f1_evidence.yaml`＋两件套 .ps1 |
| P2 GPU-01 | 夜窗挖矿批上线且档位 A/B 定版报备 | **受阻**（夜窗两件套＋lane_b 档位参已落码；A/B 未出数＝今夜起跑不进 23:00 窗） | `03_gpu01_gpu02_construction.yaml`＋`05_`(待) |
| P2' GPU-02 | 批量打分窗口上线且落表，或工单否决归档 | **受阻**（三缺件全落码＋10 支守卫测；表未建、任务未注册；令文 00:30 与 CH 让路窗算术冲突已呈） | `03_gpu01_gpu02_construction.yaml`＋`06_`(待) |
| P3 GPU-04 | RL trainer 施工完成并通过 B-007 后启动，或否决归档 | **只呈批**（premise 过期：TD3 trainer 早在位，缺的是影子对拍腿＋replay 数据腿＋窗登记） | `04_gpu04_b007_material.yaml` |

## 4. 施工分层口径校正（有据，随袋报备）

两张工单把注册脚本写作 `register_night_mining_task.ps1`／`register_kronos_scoring_task.ps1`（未给目录）。
实测本仓分层=**注册册 `scripts/tasks/register/`（在册 32 件）＋执行链 `scripts/tasks/run/`**，
`scripts/` 根只留 2 件历史注册册（`register_process_reaper_task.ps1`、`register_commit_perf_report_task.ps1`）。
样板=`scripts/tasks/register/register_factory_lane_c_task.ps1`（幂等 `Set-ScheduledTask` 就地更新，
禁 Unregister+Register；`-ExecutionTimeLimit`＋`-MultipleInstances IgnoreNew`）。
⇒ 本班新件按分层落 `scripts/tasks/register/`，执行链落 `scripts/tasks/run/`，
并同步 `scripts/script-manifest.yaml`（生成器单口 `generate_script_manifest.py`），不入 `scripts/` 根。


## 5. 本班撞开并对症修好的落地链死法（三条，都是"机制面"不是"我这单"）

1. **心跳守护自退 → 队列把活会话判幽灵**（q-0001 死）。建车 14 分钟后
   `.runtime/sessions/<sid>/heartbeat.jsonl` 末行写 `status=exited reason=session not in registry`，
   注册表条目同时消失；此后入队能过（它认 BRANCH-WRITE-TRACE 旁证），**落地侧存活闸不认**，袋直接进 dead/。
   修法＝按今日维护二班刚立的**保活正门**：`register_heartbeat_keepalive(root, sid, reason=..., requested_by=..., ttl_seconds=7200)`
   ＋ `SessionRegistry(root).register(sid, pid=0)` ＋ 重起 daemon。**且每投一袋前现注册现投，不沿用上轮**；
   注意 `logical=True` 会被"非 chief 形态"降级拒绝（MARK_LOGICAL_DENIED），长班唯一合法通道就是具名保活授权。
2. **新建件"先 commit 到车道再入队"必死**（q-0002 死）。enqueue 把 `base_head` 记成**车道自己的 HEAD**；
   新文件已在车道 HEAD 里 ⇒ 落地侧 `_merge_registry_file` 判"在本袋基底存在而 dev 已删＝陈旧快照复活"直接拒写
   （`scripts/governance/commit_queue_landing.py:2367` 那条 P0 红队补齐）。
   正解＝新文件**先入队、后落车道 commit**（工作树留原字节，车道 HEAD 不含它即可）。
3. **预检扫的是整个暂存区不是本袋清单**（03B 被 TABLE-NAME-REGISTRY 拦）。我把已属另一袋（03A）的
   DDL 件一直留在 index 里，`schemas/**/market_*.py` 的 DDL 常量按规则是豁免的，但它作为"别人袋"的件
   混在我的暂存面上仍被算进来。正解＝**一袋一暂存面**：投前 `git restore --staged .` 再只 add 本袋文件。
   同族另一条：`COMMIT-SCOPE` 正当拦跨域 ⇒ 按域切两袋＋后继袋 `--depends-on` 先行袋，别拿 `--allow-multi-domain` 糊。

另两条**测量口径**教训（不是门，是尺）：
- 资源册再生**只能在主区根跑**：从车道根跑 `generate_resource_profile_registry.py` 只产出 69/103 实体，
  丢的恰好是全部 `sch_*` 家族——从车道拿它当绿＝假绿。
- `--score-only` 的 help 文案里写全限定表名，被 TABLE-NAME-REGISTRY 正当拦下：表名连说明文字都不该埋，
  因为它会被复制成第二真源。
