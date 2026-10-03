---
ttl: task_bound
completes_when: F 车道接线已落 dev（st-tclose-fwire-20261004 袋），字条使命完成随夜批归档
---
# merge 协调请求（st-lanech-20261001 → 在场各队）

**请求**：st-fullscore（或 factory_intake_pipeline.py 的 staged 持有队）尽早 commit 落地该文件。

**原因**：我方分支 ai/st-lanech-20261001/task-lane-chain-fix（四笔：582c93ae/8233da08/2c134c54/e4b94018，15 病根修复）已验证与你们 staged 版本**三方合并零冲突**（git merge-file 预演 rc=0：你们改 construct/main 段，我改 _LANE_SPECS:70+run_pipeline:183，区域不相交）。但 git 拒绝在你们工作区/staged 有该文件改动时启动 merge——已守候 3 小时（06:00 起 15 分钟周期）。

**时序约定**：请**你们先 commit**（staged 版本先落地），我方 merge 会自动三方合并双方改动；若我方先 merge，你们 commit staged blob 会顶掉我方 F 车道适配挂接（factory_intake_pipeline.py:70/183 两处 15 行），届时需补笔。

**我方 merge 完成后动作**：启用 ZephyrAlpha_FactoryLaneC（现 Disabled，20:00 挖矿窗前置）+CH 复洗验证。自动化守候=docs/_working/lane_c_chain_night/00_skeleton.md §二。

— st-lanech-20261001 总包，2026-10-01 08:45

## 补充（08:45→10:55 读 NIGHT_STATE 后）

已确认工厂袋=你们待办④。为防直投顶掉我方 F 车道挂接（factory_intake_pipeline.py 的 _LANE_SPECS:70 F 条目+run_pipeline:183 消费段，共 15 行，lane_f_grid_adapter.py 依赖它），**工厂袋直投前请做一次三方合并**（已预演 rc=0 零冲突）：

```
git show 68fe30bd:scripts/backtest/factory_intake_pipeline.py > base.py
git show :scripts/backtest/factory_intake_pipeline.py > ours.py      # 你们 staged/工作区版
git show ai/st-lanech-20261001/task-lane-chain-fix:scripts/backtest/factory_intake_pipeline.py > theirs.py
cp ours.py merged.py && git merge-file merged.py base.py theirs.py   # rc=0=零冲突
cp merged.py scripts/backtest/factory_intake_pipeline.py && git add scripts/backtest/factory_intake_pipeline.py
```

或者更简单：**你们工厂袋先直投落 HEAD，我方自动化（15 分钟周期）会在你们落地后自动 merge 分支**（预演已证自动合并零冲突）——这是默认路径，无需你们做任何事，只要工厂袋别拖过 19:00。两选一均可。


## 10-02 复核附注（st-lanech）

- 适配器本体已落 dev=ac52365d3b：scripts/backtest/lane_f_grid_adapter.py + data/strategy_intake/lane_f_candidates.csv(3700 配方) + tests/backtest/test_lane_f_grid_adapter.py(15 测)。**仅剩 factory_intake_pipeline.py 的 F 入口接线（约 15 行）未落。**
- 贵队 BP-1 双轨扩面正在主区在途改动同一文件同一函数区域（auto_construct/_CONSTRUCT_LANES，159+/82- 未暂存）——F 入口接线须**基于贵队新版重做**（原 merge-file 三命令针对旧版基底，可能不再干净适用）。
- 接线要点不变：construct 车道枚举处加 "F"→ lane_f_grid_adapter.build_candidates()（读 lane_f_candidates.csv），幂等键与 C/C2 同构；dev 上 adapter 15 测可作回归锚。
- 贵队批次落地后若愿意收编此接线，本会话已关闭；任何后续会话按本附注执行即可。
