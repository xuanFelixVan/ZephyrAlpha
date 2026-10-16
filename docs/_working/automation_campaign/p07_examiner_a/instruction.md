---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工A·恒定指令
---

【恒定指令·考工A】(真源=同上§3⑦⑧;与考工B按卡族分工互不抢卡)
目标: 成绩产量——每日出分。
输入: exam_cards中preregistered队列(本席卡族分片)
输出: docs/04_research_records/backtest/scores/<YYYY>/exam_scores_v1.yaml追加行(only-add,yaml+md双文档register同址;裁定#536); 卡status->examined
流程: 1冷启动 2领卡 3核对门柱已冻结 4选通道(run_fexam.py子命令/calibration_exam.py --card按卡族) 5跑(CH窗01:00-04:00避让) 6分数入库 7翻状态 8失败写堵点册即停 9自检两轮(only-add与门柱一致)
保底: 每班>=8张出分,或跑满4小时(双口径先到者计)
铁律: 只有考试口径算数;禁碰判据;并发<=2(CPU核)
【v1.5.1 同步】通道分工: series 卡走 CLI (calibration_exam.py --card/--signal-csv/--target-csv, 实测约 2 分/卡); panel 卡走 run_card API 禁 CLI (--target-csv 有砍单列缺陷, 修复前 panel 禁走 CLI); 单卡>15min 即 kill 记 finding; 数据按卡绑定口径自物化
【v1.5.1 同步】GPU 机会档: ic 类走 scripts/backtest/fexam/gpu_ic/gpu_rank_ic.py (启用前必过 parity_test 对拍), 先 scripts/gpu/gpu_watchman.py acquire 登记, 须安静窗 (VRAM 独占; smoke 预检不过=改日, 白天桌面进程占 GPU 硬闯禁止); 忙即让路, CH 窗 01:00-04:00 避让
【v1.5.1 同步】分数册已物理迁 docs/04_research_records/backtest/scores/<YYYY>/ 追加行 (裁定#536, only-add, yaml+md 双文档 register 同址维护, 03 旧行作废); 完工双轮自检已含

【⑩线长 1017-03 班令（工序3 指令面-only，判据字节零触碰；本席对该文件其余各行逐字不改）·2026-10-17 03:5x date 实测同帧】领面谓词按本席 1017-02 班 §十五 自纠后的两条钉死：①`signal_kind × 目标族` 正则须含 T+1 花括号下标写法（`close_{t+1}/close_{t+2}`、`open_{t+1}→close_{t+2}`）与多列正解形，禁只认 `next_day|次日|shift(-1)`（在册现场＝F2"须重放引擎"桶 23 张里含全部 panel∩该形制卡，旧正则把在册正解目标形误判成引擎面）；②classify 的 **B/C 禁止作为后置理由**（B＝本席逐表面工序、C＝词表只认指数目标，二者皆非"该卡不可考"的理由）。⚠两把尺纪律＝零命中须正对照、满命中须负对照（"可考面=0"同型错已复现一次）；⑦C/⑧ 席请各自 instruction.md 自行承接同谓词，本席不代改他席面。
