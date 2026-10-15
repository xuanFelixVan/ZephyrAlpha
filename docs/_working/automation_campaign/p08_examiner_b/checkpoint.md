---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑧考工B·游标
---
# 游标

cursor: 10-15 班次 03 已交账（首袋 dead＝双侧皆改，判决=可销 superseded by -0002；内容三面对拍零丢失，盘面==二袋 blob）（出分 0/8 未达；**前置在本班值守内成就**＝⑥-07 已给卡 06/07 补 `oos_window_ref` 且值与冻结 `window.oos` 逐字相等，另 3 张多日卡未被补＝D3 建议被采纳；本席把上班游标④的 target 注入口径**判废**＝注 close 是价格水平机械伪影，纯噪声也得 IC 0.107）
last_run: 2026-10-15 13:05（`date` 实测；开班 09:35→收班 13:05≈3.5 小时墙钟，出分仍 0/8，本班不拿时长抵成绩）
last_batch: p08-1015-03 案卷＋收班班（正门未开：卡 06/07 锁由 ⑥-07 以 ttl=90m 持有，12:50 过期 35min 后 acquire 仍 DENIED（"会话仍活跃<30min⇒过期+静默才可回收"），与 takeover soft-expire<=7200s 同族＝**pid=0 席的可考窗口≈TTL＋7200s**；另本席 12:51 自跑 cleanup 把自家两件 claim 收了（三任守护 50080/54536/32128 皆亡）⇒ 写-入袋之间禁穿插 cleanup。案卷班（75 张逐张归属 75=30+39+5+1 加总闭合；卡 06 预跑 verdict=fail ic_mean −0.0121/ic_ir −0.0685/oos_ic −0.00835/n 1859，**未入册非成绩**；成绩册在册性＝新址 HEAD 三面查无＋5 个在途袋 base=None＋74/75 行旧快照 vs 主册现值 90 行）
notes: |
  游标由本岗每批推进；监督员(⑩)可代修。
  **下一班开考规格（覆盖上一版④，本席实跑核对，禁再猜）**：
  ① target **必须**注 `close/close.shift(1)-1`（禁注 close 本体；禁 `pct_change()` 默认 pad＝停牌旧价被读成 0 收益）。
     判据面＝`_panel_metrics:250` 配对的是 signal[t] 与 target[t+1]，故 target 须是"当日已实现收益"面；
     正/负对照三读数（60 列随机游走噪声）：注 close=0.1069（假信号）／注 pct=−0.0015（正确零）／正对齐=1.0000（配对证明）。
  ② 卡 06（hs300）走 run_card API（panel 禁 CLI）；宇宙下推谓词 `index_code='000300.SH'` ＋ `splitByChar('.',symbol)[1]`
     （两表 symbol 格式不同域，直 JOIN 返回 0 行＝伪装成"无数据"）；成员面按月末快照 ffill（2016-2025 每年 12 快照×300 只）。
     实测保留 IC 日 1,860/1,940，**首个有效日 2019-01-30 比冻结 IS 起点晚 18 交易日**（hfq 2019 前是 232-238 只 stub 面；
     hs300∩2018 有额者仅 11 只）⇒ 属披露项，勿写成"信号无信息"。
  ③ 卡 07 **仍无 `universe_note`**（本班实测两谓词零命中）；其卡面 `min_obs_per_bucket=每桶≥500`×10 桶反推宇宙须 ≥5,000 只
     ⇒ 只能全 A 面＝9,019,977 行/5,818 只，须先离开 ALERT-SYS-003（`config/alert_rules.yaml:53-59`，>90 critical，
     自述"提交流程/pytest 会静默崩"）再拉；或先请 ⑥ 冻宇宙。本班据此未拉全 A（外溢打在在飞提交与队列 drain 上）。
  ④ 卡 06/07 锁面现值＝持有者 `st-qoder-p06-1015-07`，来源=入队续期、ttl=90m（10:45 实测剩余 89.9m）。
     `run_card` 必整档重写卡面（`calibration_exam.py:1019-1024`）⇒ **他班持活锁期间本席不可开考**；不抢锁不绕行。
  ⑤ 分数册 promote 前置＝**当场重拷主册＋difflib 证 minus=0**（本班 09:5x 见 84 行/116,029B/sha 4f986ec7，
     10:48 见 90 行/123,768B/sha 009c7bbc＝面值在值守内被上游推进）。册在 HEAD **查无**（`git log --all -- <路径>` 零行、
     `git ls-tree HEAD -- .../scores/2026/` 空），旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 仍在 HEAD；
     指新址的非 done 袋 5 个 base_blob 全 None（含 scorehome 两袋 74/75 行旧快照）⇒ 今日成绩有整档覆写路径，
     本席只寄存自家台账，落地后再投。
  ⑥ pid=0 恒定班的 claim **本班 21 分钟内被外来 cleanup 收走两次**（守护 50080→54536 皆亡、session 仍在但锁面查无）⇒
     全部写动作须"重注册＋重 claim＋立即写＋立即入袋"一气完成，勿在 claim 空窗内留稿。
  ⑦ 正门驱动器已就绪可一命令跑完（含三重自证）：`python .runtime/tmp/st-qoder-p08-1015-03/shift03_land06.py`
     ＝卡锁须本席 ACQUIRED→当场重拷主册记 CAS 基线→run_card→difflib minus=0 硬闸→safe_write_text CAS promote→读回比 sha。
     13:05 现场读数：分数册 90 行/123,768B/sha16 009c7bbcf87582c2（自 10:48 未变）；卡 06/07 status 仍 preregistered、oos_window_ref 与冻结值逐字相等。
  防重入两址并存期须两址同读（旧址 docs/_working、新址 docs/04_research_records/cross_domain；新址现值仍＝10-14 搬迁空壳"未开始"）。
  本班水位：commit_pct 93.13%（09:35）→92.09%（10:18），degraded=True、ALERT-SYS-003 全程未解除；分数册零改动（本席未写主册）。
