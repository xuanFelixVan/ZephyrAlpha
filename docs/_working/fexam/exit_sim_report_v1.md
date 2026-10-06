---
campaign: matrix-20261006
lane: E-exam-w2
ttl: task_bound
---

# exit_sim_report_v1 — E道离场族 ATR 止损首件对照（夜战 tmp 版）

- 判定（prereg 冻结判据）：**有增益**
- OOS MaxDD 改善：+16.5pp（止损版 vs 无止损）
- OOS Sharpe 变化：+0.619
- 无止损 OOS：Sharpe=-0.187，MaxDD=-57.56%
- 止损版 OOS：Sharpe=0.432，MaxDD=-41.02%
- 重标定：stop 臂 per_run=0.428s（0.17us/标的·日）；0.53s/格旧口径（c4 网格专用）已禁用，路径依赖网格外推≈0.4s/格（本装置实测）
- 装置：月频 top20 等权（批3 pass 24 列等权合成），T+1 开盘执行，初始止损=入场价-3×ATR14，移动止损=持仓期最高收盘-3×ATR14，日收盘 pierce 次日开盘离场
- 信号覆盖：69/105 个月有持仓（24 列指标 CH 数据 2021-01 起，2018-2020 空仓为覆盖现实）
- 无止损基线注记：nostop 臂本身为强负 alpha 装置（IS 收益 -70%），对照判据按 prereg 冻结线执行，负基线语境如实随册
- 引擎参考跑：timeout
- prereg 冻结：2026-10-06 10:10:50.146205+00:00（先于一切仿真运行）

细节=D:/ZephyrAlpha/docs/_working/fexam/exit_sim_report_v1.yaml；模块=.runtime/tmp/st-matrix-20261006/exit_sim/（正式化=日光档工单）
