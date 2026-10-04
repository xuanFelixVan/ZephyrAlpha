---
ttl: task_bound
completes_when: fullscore_night 战役文档随 F8 家族处置批B 归档
---
# deferred_claims — st-fullscore-20260930 勘误/清理批暂缓项（2026-10-01）

## CAS 临时残留不删（删除前置失败：内容未被正式文件覆盖）

1. `scripts/backtest/translated/_c4_engine.py.tmp.18376.0778f70f85b8`（02:16，pid 18376 已死）
   - diff 实证：含 `_cost_model_adapter()` + `_net_line(cost_model=...)` W1-4 可插拔成本档引擎侧接线，正式件（=HEAD cf16fa43fdd）grep `cost_model` 计 0——**tmp 是该接线唯一副本**。
   - 配套：`scripts/backtest/cost_model.py`（untracked，W1-4，本会话夜战件）在等工作树接线落地。
   - 处置：待 campaign 首脑决定（恢复接线→与 cost_model.py 同批入队，或明示废弃后删）。
2. `scripts/backtest/f06_e4_wfa_exam.py.tmp.18376.ef6844d6fa56`（04:32，同 pid）
   - 正式件 06:41 新写且工作树在途（+94 vs HEAD），tmp=TTL task_bound 中间态，正式件已走 permanent 化路线；非本批清理清单内，同 pid 顺手留观不越界删。

## 已执行清理

- `.runtime/tmp/fullscore_recovery/`（空目录）已删。

## mod_translation dedupe defer（claim 冲突，铁律不抢）

- `add_module_translation.py --dedupe` 已执行（10 组重复清偿，entries 7954→7944，loader 复核零 WARN，复检 0 重复组），但 `module_translation_registry.yaml` claim 被**在世会话 `st-menu-w3h-20260930` 持有**（心跳 0.1min 前实证）。按并行协调铁律：活→登记 defer 勿抢。
- 处置：dedupe 结果留在主工作树面（不 revert——防误伤他会话在途编辑；不提交——无 claim）。st-menu-w3h 落地时自然吸收，或其落地后任一会话重跑 `--dedupe` 收口（幂等）。

## GPU L2 重建批 defer（2026-10-01，册被占分开批）

- `scripts/backtest/l2_bench_probe.py`（探针正件，已暂存 `.runtime/sessions/st-fullscore-20260930/staging/scripts_backtest/l2_bench_probe.py`）：
  CREATE-GUARD 需 capability 册 token 行——册被 st-datasop（staged +5 行）/st-menu-w3h 在途，按令分开批。
  落地配方：从 staging 物化正件→add_module_translation.py 登记→capability 册同批带 token 行（merge_evaluation=战报转正件）→直投。
- `docs/_working/fullscore_night/06_gpu_compute/04_L2_landing_benchmark.md`（终验表，已暂存 `.../staging/06_gpu_compute/04_L2_landing_benchmark.md`）：
  新 .md 同受 CREATE-GUARD——与探针正件同批带册落地（数据已实测在案：gpu/hoisted=6.81x/10.64x/15.42x、parity≤7.6e-13、auto 三选三准、eval 0.09s=24.8x）。
- L2 代码四件+测试三件本体已直投（不含上两件，见当日 commit）。

## IBT-v2 池复原批 defer（2026-10-01，同上例：capability 册被活会话持有）

- `docs/_working/fullscore_night/03_integrated_backtest/fresh_pool_v2.yaml`（考卷，sha256=38ee5ada3834e99279f76eb2ec2c455aa28af94ca611b0fb84668ccdbafd47cd，已在盘且 prereg 附录 A 锁箱）+
  `fresh_pool_v2_notes.md` + `blocked_v2_pool_missing.md`（前班产物）：
  CREATE-GUARD 预检仿真面=HEAD+袋，capability 册 token×3 未落 HEAD 即拦；册 claim 被
  st-menu-w3h-20260930（活，心跳秒级）持有，按铁律"活→defer"分开批。token×3 已写入主树册面
  （w3h 10:43 重写实测吸收）+本会话 worktree 册面；w3h 落地吸收后任一会话补批三件直投即收口。
- 考试不等待：池文件在盘+指纹入 prereg 附录 A 即满足锁箱时序，四窗已发已裁（v2_verdict.md=FAIL，
  HOLDOUT 已烧）。prereg_v2.md/deferred_claims.md 本体亦未落 HEAD（战役文档全树均为新文件同受 CREATE-GUARD），
  与上三件同属批二。
- 已落地：scripts/backtest/ibt/ibt_runner.py ART_ROOT 重定向（commit 75ac9432）。
- 批二清单（册落 HEAD 后任一会话可收口）：fresh_pool_v2.yaml / fresh_pool_v2_notes.md /
  blocked_v2_pool_missing.md / v2_verdict.md / prereg_v2.md / 10_coordination/deferred_claims.md
  （token×4 已在册面，主树+worktree 双面同布）。
