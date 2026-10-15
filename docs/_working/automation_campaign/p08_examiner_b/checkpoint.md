---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑧考工B·游标
---
# 游标

cursor: 10-15 班次 04 已交账（**本岗今日首两张真分出册＝2/8**：TDM-P-P2-04/calibration/06 与 /07 均 verdict=fail 真判决，卡面已翻 examined，分数册 only-add +2 行 minus=0 自证通过）；上班"卡 07 须 ≥5,000 只"的反推被本班实测改判（卡面原文"每桶票-日 >= 500 且覆盖 >= 30 只票"，hs300 PIT 实跑＝池化十分位每桶票-日最小 55,849／每桶覆盖票数最小 500／每日每桶票-日中位 28.0，前一读法达标）
last_run: 2026-10-15 16:0x（`date` 实测；开班 15:30:29，出分 2 张）
last_batch: p08-1015-04 两卡出分＋游标＋台账（本班一袋，含分数册 2 行 only-add、卡 06/07 面、ledger、checkpoint；卡面携带 ⑥-07 未落地的 `oos_window_ref` 补键，归属已在 message 署名）
notes: |
  游标由本岗每批推进；监督员(⑩)可代修。
  **下一班开考规格（班次 04 实跑核对，覆盖班次 03 的 ①-⑦）**：
  ① 注入面不变：target=`close/close.shift(1)-1`（禁注 close 本体、禁 `pct_change()` 默认 pad）；工具 `_panel_metrics:251` 配对 signal[t]×target[t+1]。
  ② **正门已开**：卡 06/07 的 ⑥-07 ttl=90m 活锁于 15:34 前自然解除（`lock_files.py list` 零命中）；本席已把两张出分入册并翻 examined ⇒ **本族可考面从 6 张缩到 4 张**。
  ③ **余下 4 张（P1-02/02、P1-02/04、P1-04/04、P3-04/04）本席判"不可开"，勿尝试**：卡面冻结持仓池=多因子 top20（20 只/日），撞 `ic_exam.py:96 ic[valid<30]=nan` 地板；本席同帧双对照（seed=7）实测 20 列面 ⇒ `_panel_metrics` 回 `ic_mean=0.0000`（空序列被读成 0）+ judge `fails=['ic_mean 0.0000 < 0.02', ...]`＝把"截面不足"写成"信号无信息"的假红。开一张即造一条假成绩。
  ④ **且其因子集真源已断**：`scripts/backtest/fexam/exit_sim/prereg_frozen.yaml:23` 的 signal_source 指 `docs/_working/fexam/indicator_exam_scores_v1.yaml`——盘面查无＋`git ls-files docs/_working/fexam/` 零命中 ⇒ top20 列集当前不可复验。转 ⑥ 冻列集／⑤ 修指针（与 ⑤-1015-03 修的 SERIES_DIR 同族）。
  ⑤ **双臂 29 张的册面闸已解**（`card_binding.py:1927` 现值 `safe_load_all`，本班实测双文档 2 doc 无 ComposerError）；仍缺 NAV 接线（signal_b），属 ⑤/⑪ 产出面，本席不物化。
  ⑥ 分数册面值现测口径（禁引本游标当事实）：`python -c "import hashlib,pathlib;p=pathlib.Path('docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml');b=p.read_bytes();print(len(b),hashlib.sha256(b).hexdigest()[:16])"`；本班 16:0x 读数 131,320B/95 行（本席 +2）。promote 前置仍＝当场重拷＋difflib minus=0 硬闸＋`safe_write_text` CAS（本席两次 promote 均 written=True/equals_staging=True）。
  ⑦ **驱动已可复用**：`.runtime/tmp/st-qoder-p08-1015-04/shift04_land.py <runner> <卡面相对路径>` ＝ open_session＋心跳＋卡锁/册锁须本席＋当场重拷＋minus=0 硬闸＋CAS promote。runner 形态见 `shift04_run06.py`/`shift04_run07.py`（hs300 PIT 下推，向量化无逐日循环）。**必带 `sys.path.insert(0, ROOT)`**，否则 `_spawn_heartbeat_daemon` 报 `No module named 'scripts.ops_guard'` 而静默无守护（本席首版踩过）。
  ⑧ 卡面归属：卡 06/07 盘面含 ⑥-07 的 `oos_window_ref` 补键（`git show HEAD:<卡>` grep 命中 0＝未落地），本席袋=整档快照必然带出，已在 commit message 署名 ⑥-07；下一班若见该键已在 HEAD＝前置已由他席落地，勿再声明。
  ⑨ 门误报一条（给 ⑤/⑩）：`scripts/lock_files.py:585-597` 命名门仅在 `not tracked` 时跑；本席 15:5x acquire 卡 06 首报 `NAMING VIOLATION [N-01][N-13]`、立即重试即 ACQUIRED，同进程直调 `_is_git_tracked()` 实测 True ⇒ git 探针瞬时失败会把存量卡降级成"未跟踪新件"并报错误导。
  防重入两址并存期须两址同读（旧址 docs/_working、新址 docs/04_research_records/cross_domain；新址现值仍＝10-14 搬迁空壳 `cursor: 未开始`，本班 15:59 实测）。
  本班水位（现测命令＋时刻，非终值）：15:31 `commit_pct=88.79`、15:59 `88.7`、degraded=False、breached=ALERT-SYS-001；ALERT-SYS-003 未触发＝本席仍未拉全 A 与水位无关（见 ③④）。
