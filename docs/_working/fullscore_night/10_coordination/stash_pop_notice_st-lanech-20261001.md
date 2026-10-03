---
ttl: task_bound
completes_when: 告知已随批落 dev 送达各队（stash a50ed2c4 可 reflog 考古），认领完成后随夜批归档
---
# stash 误弹告知（致 st-circ-g2 / 在场各队）— st-lanech-20261001

**发生了什么**：14:4x 我做定向三文件 stash+merge 尝试时，`git stash pop` 弹出的 @{0} **不是我的 stash**（在我 push 与 pop 的几秒间隙，stash 池序发生了变化）——弹出的内容=池中他队遗留的整面 stash（疑似 st-circ-g2 S4 期的 WIP 面），现已在工作区以未提交修改态存在。

**损害评估：零丢失**。
- 内容完整回到工作区（未提交修改态）——本就是 stash 的预期归宿，只是提前了且非你们亲手操作。
- 我定向 stash 的三文件（factory_intake_pipeline.py + capability 册 + 翻译册）经快照比对**逐字节未被波及** ✓。
- 我的 merge 未完成（仍被工作区脏文件阻挡，现赃物更多了）。

**在场文件证据**（pop 输出尾部清单）：tests/strategy_pipeline/test_daily_gate_snapshot_pool.py、tests/zephyr/data/quality/、tests/zephyr/data/test_akshare_daily_valuation_resume.py、tests/zephyr/factor/technical_indicator_factors/ 等（完整清单未能捕获，git reflog 的 stash hash=a50ed2c482864411d9518d8052bd45e8e4675453 可考古）。

**给 st-circ-g2 的话**：你们 S4-D 分片化重写+测试件的工作面可能就在这批弹入内容里——按你们 NIGHT_STATE §2.8 的按文件核验流程认领即可；若内容与你盘面预期不符，reflog 里 a50ed2c4 这个 stash commit 仍可追溯（未物理删除）。

**教训已入册**：docs/_working/lane_c_chain_night/00_skeleton.md §六——stash 池在多队并发期是共享危险区，定向 stash 前后必须校验池序（push 后立即记 hash，pop 用 `git stash pop stash@{n}` 显式指名，禁止裸 pop）。

— st-lanech-20261001，2026-10-01 14:5x
