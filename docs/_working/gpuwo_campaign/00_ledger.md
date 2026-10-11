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
| §1 锚点重验+LaneC 体检 | 原令 §1①-④ + LaneC 产物完整性四态分诊 | 已完成 | `01_anchor_reverify_lanec.yaml` |
| P1 GPU-03 | 情绪 SFT 模型回灌 Ollama 且夜窗情绪批切换自模型验证一轮 | 在飞（转换步待 llama.cpp 批复） | 待 `02_`/`03_` |
| P2 GPU-01 | 夜窗挖矿批上线且档位 A/B 定版报备 | 待施工 | 待 `04_`/`05_` |
| P2' GPU-02 | 批量打分窗口上线且落表，或工单否决归档 | 待施工 | 待 `06_`/`07_` |
| P3 GPU-04 | RL trainer 施工完成并通过 B-007 后启动，或否决归档 | 只呈批（材料包） | 待 `08_` |

## 4. 施工分层口径校正（有据，随袋报备）

两张工单把注册脚本写作 `register_night_mining_task.ps1`／`register_kronos_scoring_task.ps1`（未给目录）。
实测本仓分层=**注册册 `scripts/tasks/register/`（在册 32 件）＋执行链 `scripts/tasks/run/`**，
`scripts/` 根只留 2 件历史注册册（`register_process_reaper_task.ps1`、`register_commit_perf_report_task.ps1`）。
样板=`scripts/tasks/register/register_factory_lane_c_task.ps1`（幂等 `Set-ScheduledTask` 就地更新，
禁 Unregister+Register；`-ExecutionTimeLimit`＋`-MultipleInstances IgnoreNew`）。
⇒ 本班新件按分层落 `scripts/tasks/register/`，执行链落 `scripts/tasks/run/`，
并同步 `scripts/script-manifest.yaml`（生成器单口 `generate_script_manifest.py`），不入 `scripts/` 根。
