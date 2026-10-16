---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑪整装回测席·游标
---

# 游标

cursor: 2026-10-16 整装#1 已收班（装配盘点班·未硬跑，见 ledger「2026-10-16 整装#1」）
last_run: 2026-10-16 21:49 +0800（班内实测钟）

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 2108 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。

<!-- P11-1016-01-CURSOR -->
> **⑪1016-01 班末游标补记（追加，未动上方 ⑩ 提醒块，实测计数前后均 1）**
> 下夜起班三查：①分数册 verdict=pass 集合是否新增可执行件（当前 2 条均为 calibration IC 卡，装配交集 0）；②`p11_assembler/*.yaml` 是否已由⑤交付 pool 桥接件（交付前 dispatch 在册令＝不硬跑，硬跑＝假成绩）；③21:30 排班线机器面是否已注册（config/trading_day_cycle_map.yaml 现零命中）。
> 本班零触碰面：W_HOLDOUT 产物只读未跑；`config/exam_scale_cost_gate.yaml` 与 IBT 协议冻结窗一字未改；治理图/流程五族面未动。
