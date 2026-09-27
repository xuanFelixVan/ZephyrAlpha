---
ttl: task_bound
title: "全流通打通战役宪章（总筹 zcode 2026-09-27 夜班）"
session: zc-chief-20260927
completes_when: "全部波次收官并交付终报后归档"
---

# 全流通打通战役宪章（00_orchestration）

> Owner 令（2026-09-27 睡前）：以上未施工内容全部施工；总筹=本会话。挖矿先行、线内先挖后干、
> 线间并行流水、谁挖干谁先开工；挖干判据=六向台账+自审闸三态；红蓝对抗至连续两轮零；
> 全袋经 GitCommitGateway；不留临时文件。无法裁定=登记+跳过；堵塞方可停。

## 一、波次计划

| 波 | 内容 | 并发 | 状态 |
|---|---|---|---|
| W0 | 环境体检（reaper/daemon/队列） | — | ✅ 绿（daemon 在跑，队列 3p/2proc） |
| W1 | 挖矿：13 矿道并发（L00 骨架定版 + L01-L12 环节带 F01-F122 全覆盖） | 13 | 在飞 |
| W1' | 施工波1：G 撞号P0 / L 图书馆清零 / P 管线数据面（三线与挖矿并行） | 3 | 在飞 |
| W2 | 挖矿产物 token 批登记 + 骨架定版 + 缺口转工单排序总表 | 总筹 | 待 |
| W3 | 施工波2：Q 入队预检+W17（依赖 G 落地解锁预检） | 1-2 | 待 |
| W4 | 红蓝对抗×2 连续零（测试面+门禁自洽面），发现问题即修即回 | — | 待 |
| W5 | 全袋落地核验（git log -1 --name-only 逐袋）+ .runtime/tmp 清理 + 终报 | — | 待 |

## 二、矿道分工（W1）

骨架真源=`docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（122 环节）+90 交叉验证普查（29 候选漏项）。
案卷落点=`docs/_working/fullconnect_campaign/<段目录>/<F号>_<语义名>.md`，每卷必含：六向台账（带实证锚点）/子模块三级枚举/接线四态独立复核/缺口清单（处置+优先级）/自审闸三态/复跑命令。

| 矿道 | F 带 | 段目录 |
|---|---|---|
| L00 | 骨架定版+29 候选甄别+映射缺口 | 00_skeleton |
| L01 | F01-F12 | a_data_foundation |
| L02 | F13-F22 | b_factory_inbound |
| L03 | F23-F29 | c_exam_pipeline |
| L04 | F30-F36 | d_l9_knowledge |
| L05 | F37-F45 | e_decision_chain |
| L06 | F46-F57 | f_exec_risk |
| L07 | F58-F69 | g_backtest_gpu |
| L08 | F70-F81 | h_sched_recovery |
| L09 | F82-F93 | i_ai_ops_gov |
| L10 | F94-F105 | j_ai_design_gates |
| L11 | F106-F115 | k_frontend_docs |
| L12 | F116-F122 | l_methodology_routing |

## 三、施工线分工（与挖矿并行，谁挖干谁开工）

- G 线（zc-lane-g）：gate_auto_registrar priority=77 撞号 FAIL-CLOSED 修复（收口卷 §四；先例=后到者让位 77→109）。**最优先——预检瘫痪解除前 Q 线不动。**
- L 线（zc-lane-l）：potential_consumers 清零取证+68 条重放（lib_events 存证）+regen reconciler 防清零守卫+回归测试；`--feeds` 复活验收。
- P 线（zc-lane-p）：str⧸date 共因一处修（C1）/l2_tick capability 登记缺陷/etf_benchmark date_col 声明/suspend·realtime 日领衔诊断/restricted_shares 前瞻值新鲜度尺。只读诊断+代码配置修复+单测；禁手工实弹写生产表。
- Q 线（zc-lane-q，W3）：入队预检封旁路（requeue+enqueue_item 直调）+W17 --base-head base_blobs 补填；参照 `.aidrafts/lane_ff_snapself` 见证层码评估同批面。

## 四、纪律（全波次生效）

1. 提交唯一正门=`scripts/git_commit.py --session <sid> --files <清单>`；锁忙自动入队；重试带 --adopt-prior-work；落地后 `git log -1 --name-only` 核归属。
2. 改前 claim（`lock_files.py acquire <file> <sid>`），毕后 release；他会在飞件不代修不覆盖。
3. 热注册表写入必经 safe_write_text；token 与文件同袋或先行。
4. 新目录/文件命名全语义、零数字后缀（R5 防呆）；tests/ 豁免 token。
5. 测试隔离：输出一律 tmp_path，禁写生产 data/；禁手工实弹写 CH/PG 业务表。
6. Owner 门位事项（§99 台账）一律登记+跳过，不代裁——宪法 §5 优先于"不留待裁"指令。
7. 本会话裁定按"第一性原理+长期战略+100% AI 开发现实+业界实践+开源对照"五要素在 90 台账留痕。

## 五、验收口径（Owner 醒后可见）

1. 全环节挖干案卷 ≥122 卷+骨架定版卷，P0/P1 缺口全部转工单（施工/挂起/Owner 三态各有序号）。
2. 施工线交付：G/L/P/Q 四线 landed 哈希在 91_progress 台账；每袋落地核验留痕。
3. 红蓝两轮零记录（含复跑命令与时间戳）。
4. 终报=91_progress §终局：已打通/已修复/已排序待施工/Owner 门位四张清单，零含糊。
