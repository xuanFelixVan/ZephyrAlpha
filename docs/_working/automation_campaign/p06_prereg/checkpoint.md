---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑥制卡席·游标
---

# 游标

cursor: 本班已收尾（⑥席 1015-11 班＝⑩第八单 §6 本席三件全处置：自家 9 枚 dead／44 件次内容级分诊＝真搁浅 0（正门 dead-archive 被 serializer 租约 pid=53820 拒＝09 班同型第二证，本班零 requeue 零 mv）＋缺键基线口径改判（在册"2 张"＝点名子集；全池同谓词实测 21 张＝20 可补＋1 挡道）＋本班补 20 张（逐件 plus=1/minus=0・八冻结面 parsed 对 HEAD 全等・值取本卡 window.oos 同锚）＋两枚非在册键复测 HEAD=0；零新卡、零翻态（五态 175/186/47/71/73 逐值同）、零判据改动；OD-26/OD-30 各追加复测；09 班撤键两块证据自 tmp 承接进台账正文；新立呈批 0 件、基线口径归口呈请随台账寄存）
last_run: 2026-10-15 18:16
last_batch: st-qoder-p06-1015-11（22 件一袋＝20 张补键卡面＋本台账＋游标；base 取最新 HEAD、单一逻辑改动一袋、等四态再投下一袋；本班未跑考试/正交闸/CH 探针；卡池 552 不变、带 oos_window_ref 面 343→363、全池缺键 21→1（残余＝P1-03/03 挡道件）；班中自家 cleanup 二次跑摘除 claim 后已重注册＋重 claim＋重起守护 pid=61168；本班不预填 qid、不自宣落地，落地判据＝下班用 `git show HEAD:<件>` 复量＋逐件 blob↔盘面对拍）
notes: 游标由本岗每批推进；监督员(⑩)可代修。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 216718 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。
