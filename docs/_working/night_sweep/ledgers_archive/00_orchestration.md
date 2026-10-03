---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# 夜战总 Sweep 2026-09-29 · 总纲（总筹=st-nightsweep-chief-20260929）

> Owner 令：审计清单全部未完成项今晚开工；另有 4 个施工大队并发（实测=st-zc9 系活跃落地中 + GPU 队 st-gpu-conv2 袋在队 + chief7 尾袋在队）；数据库 CH 已复活（9000 OPEN 实测）。目标=全流通全链路打通+循环检查连零×2+红蓝对抗+端到端交付。

## 一、骨架与挖矿裁定（内收原则，Owner"先挖后干"的合规实现）

- 全流通骨架已存在且经红队打假：**132 环节**（docs/_working/fullflow_mining/00_skeleton/）+ TDM 182 节点（config/trading_decision_map.yaml）+ 四层未接线清单（docs/_working/wiring_gap_inventory_20260927.md，59 零引用表/13 无环节域/41 未接线环节/38 TDM null）+ F123-F132 补挖案卷。
- **裁定：不重挖 120 册（违内收），做"补干挖矿"**：由字节/骨架车道产出 `docs/_working/night_sweep/00_skeleton_nightsweep.md` = 环节总表（环节×状态轴[已通/开口/等Owner]×开口项映射审计卡号），对开口环节逐个补挖矿卡（六向台账快照+自审闸三态+处方）。谁挖干谁先开工，不必等总筹点头。
- 新建施工文档一律落 `docs/_working/night_sweep/`（CREATE-GUARD token 先行独立批）。

## 二、避让图（他队领地，我方禁碰文件）

| 他队 | 领地（禁改，只读+落地后交叉验证） |
|---|---|
| st-zc9-lane-a/a2 | trae_034 及其注册表随件（已落地 1cf01067f5 ✓交叉验证过） |
| st-zc9-lane-d | src/zephyr/data/implementations/akshare_provider.py、realtime_snapshot、etf_benchmark 测试、data/config/tasks.yaml（=#20 换源+#19 域） |
| st-zc9-lane-l | src/zephyr/gov_audit/writer.py 及其锁测试（=gov_audit 锁竞争块B） |
| st-zc9-lane-p | src/zephyr/backtest/core/matching_engine.py、implementations/vectorized_engine*（=回测引擎域） |
| GPU 队 st-gpu-conv2 | src/zephyr/backtest/gpu_core.py、tests/backtest/test_gpu_core_parity.py、gpu_rewrite/new_asset_gpu_cpu_checklist.md（袋在队 pending，勿代投勿改） |
| chief7 尾袋 | q-…-0253(40件 RMCode 抢救)/0293(36件测试) 在队——看板核销勿重投 |
| 死袋禁投清单 | st-ec2-p0 系 9 袋+q-0021（重投=回退事故） |

注：L1 hoisting（CPU 去重 3-7x）**已由 62898892 落地实测 5.6x**（D27✅），GPU 队路线图中"L1 待做"以本裁定为准，勿重复施工；GPU 队主责=L2 薄核接线+W-173 prereg 声明通道。

## 三、车道分配（Wave 1，六路并发）

| 车道 | 卡源（canonical id） | 核心交付 |
|---|---|---|
| SW1 字节抢救与队列 | C 组 q-0167/C05 107件/C35 q-0213核销/C38 雷/A06 死信批次1/A27 blob/A16 出库/E21 du881 + 战情室落库 | 队列核销看板、死信归档第一批、blob dry-run、107 件文档袋 |
| SW2 宪法与AI层 | A37 宪法两行/E08 FSM/E09 C6/E10 priors/E13 tombstone/E12 W-29/I6:N-1 | AGENTS.md 落 HEAD、FSM 写点接线、washer 消费修复、心跳修复 |
| SW3 提交链暗雷 | A01 P3/A02 T14/A03 包5/A26 N2/A23 candidate/A08 S1验收 | 互锁三处方落地、五件重投、工厂化、验收台账 |
| SW4 考试判据 | D19/I2-56 T1三阻断/D20 T2发车/F46 W-180/C36 红五簇/H32 archiver/G30 W-178 | T1 哨兵转绿→T2 发车（background）、严格读接口落地、撞号修复 |
| SW5 全流通业务链 | C09 M1封矿/G16 F62整改/C50 F34 DDL决策/C31 空表/C29 分钟K/I2-21 F26 | M1 第一批执行、DDL 三步验证决策、EC3 复测（CH 已活） |
| SW6 FMS图书馆退役 | B03/B24 trae_032/B20 退役A路/I5:I32 library_hygiene/I5:I33 回填/I5:I44 报告落库/B09 FMS判据/B15 FRONT-DOOR/B12 B10-P2 | 死指针修正、A 路补完、created 轴治本落库、判据改写 |

Wave 2 预备（Wave 1 回报后派发）：二期序列 F53/F04/F73/F75/F92/F30/F05-F06（先挖后干）、CNS 消费面、图形 G-B/G-C、15 门定性、W-56 悬空裁定号、files_trigger 收窄、96_final_report_wave2 §七回填、audit_fix_ledger §11-13、miniQMT 文案、补-12 flags 轮转窗、H04/H06/H08 备份三件、merge train。
Wave 3：循环检查（分目录 pytest 连零×2）→ 红蓝八向量复跑 → 临时件清理 → 端到端终报。

## 四、全员铁律（违反即车道报废）

1. 开工前每卡先复核（git ls-tree/show/grep HEAD + commit_queue status）：他队已落地→**交叉验证**记 DONE-CROSSCHECK 不重做；他队在途（claim/暂存/队列）→登记让路。
2. 提交唯一正门 git_commit.py / commit_queue.py --enqueue；车道 cwd + `ZEPHYR_COMMIT_QUEUE_DIR=D:/ZephyrAlpha/.runtime/commit_queue` + `--worktree-root` 指施工区；禁裸 commit/plumbing/插队；禁 kill belt/reaper。
3. 热注册表必 safe_write_text CAS；改前 `lock_files.py acquire` 毕后 release（claim TTL 300s 与 commit 同链）。
4. 新建 .py/.yaml/.md token 先行独立批（batch_creation_tokens.py --prefix 精确路径）；新 .py 三件套=翻译+depgraph+token。
5. 实盘四禁；测试输出 tmp_path；预注册冻结判据（search_space_prereg/exam_scale_cost_gate）禁改，调整只走声明通道。
6. pytest 长批先登记 `data/runtime/process_reaper_keep.txt`（追加 pytest/t1_t2/factory_grid 子串，safe_write）。
7. 每卡结案写台账：`.runtime/tmp/st-nightsweep-20260929/SW<k>_ledger.yaml`（id/verdict[DONE-LANED(hash)/ADVANCED(状态+next)/BLOCKED(因)/OWNER-GATE(登记)/CROSSCHECK]/evidence）。
8. 无法裁定→按五要素自裁留痕；仍不能→登记+跳过；堵塞方可停。禁问 Owner。
9. 表述纪律：只说"N 件通过且能红"，禁"全绿"式虚报；verdict 必须给证据。
