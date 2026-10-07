---
created: 2026-10-08
chief: st-acure-20261008-chief
ttl: task_bound
completes_when: 审计闭合施工交付（P0 全闭+循环检查两轮零失败+红蓝对抗修复完成）并经 Owner 查收后归档
---

# 审计闭合夜战 orchestration（st-acure-20261008-chief）

> **Owner 授权**：2026-10-08 对话令——"施工以上所有内容（外部审计 findings）…全速并发…遇到问题自己裁定…至到所有任务全部完成"。本对话令经裁定 **#490** 落册生效（RULE-RULING 同 commit 原子），不再依赖"授权自述"。
> **输入**：外部审查 `docs/_working/external_audit_mastertc/`（00_audit_report.md P0×10 必修+P1×10+P2+53 卡复核改判；lane_a~h 八份证据底座）。
> **基线**：开工 HEAD `2bb9b771fcbc` 后首个稳定点（以开工时 `git rev-parse HEAD` 为准记入台账）。
> **作战环境**：今晚 G 系（st-govfix-g1/g3/g4/g6）/st-cure-p09/st-matrix/st-mx07-L5/st-t3series/st-tdm-chief 等 11 会话在飞——**锁纪律+队列提交+不碰他会话 staged** 为硬纪律。

## 一、作战范围（审计闭合，不扩面）

**干什么**：审计 P0 必修 10 项+P1 10 项+❓AI 可施工项（C312/C271/C315）+P2 择要。
**不干什么（宪法 §5 Owner 门位，登记留呈不代裁）**：flag 出厂翻转（C441/C85/C300 翻转面）、实盘资金（C63/C287）、生产流转、注册表净删执行（C24/C411 候选呈报）、物理删除（C109/C410/C267）。
**"全流通"口径**：=审计闭合面的全流通（死袋全部复活或改判、台账-HEAD-桌面三方对齐、恢复模块测试绿、循环检查两轮零失败、红蓝 own-diff 零未修复）；**不包含** G-D 考试点火（READY_NOT_FIRED=波 12 Owner 门位）、任何出厂翻转。

## 二、执行序（线内先挖后干、线间并行流水；挖干判据=六向台账+自审闸三态）

1. **W0 底座**（本文件+token 批+裁定#490 落册）——总包直办，已完成于开工窗。
2. **W1 挖矿**：审计已完成逐项挖矿（八份 lane findings 即挖矿底稿）——本役挖矿=将其编译为逐项施工卡（六向台账+自审闸三态+门禁处方），落 `01_mining/`；**对审计后漂移面（他会话新落地）做新鲜度复核**。挖矿复用既有真源（132 表/fullflow/环节总表），零重建 taxonomy（内收判据：可派生必并）。
3. **W2 并行施工车道**：审计已挖干项即时开工，不逐卡点头：
   - **R 恢复道**（P0-1/P0-7/P0-10）：死袋复活——信号三模块+tech_factor+红证尺测试+fill 写者+C122；token 补登记（map_mounts 或 no_mount_reason 引 rowvec 先例）+depgraph 设计节点+队列袋；死因=MAP-MOUNTS/CREATE-GUARD/gate-naming/ALGO-FLOW-LINK 全有已知处方。
   - **E 勘误道**（P0-2/P0-3/P0-8+P1④⑤⑥）：C129 原件 blob 捞回归位、close_lane l6-0004 行勘误、交付报告（终判定 scope 限定+rule_red_blue"已落"表述+C342/C129 行）、环节总表 C61 GREEN→OWNER、C192 三处修、C61 qid 清单附录。
   - **B 分支落地道**（P1②）：l8 分支 6 文件 +242/-1 以队列袋落 dev（内容等价落地，披露替代 merge；branch 后续归档）。
   - **G 桌面道**（P0-6/P0-9，二波）：桌面两清单 9 张回补+C61/C78 改判+注记更正+在途袋叙事改死袋台账口径+计数勘误；改前 cp 备份。
   - **Q 开口道**（三波）：❓C312/C271/C315 挖矿后择可施工者施工，其余登记。
4. **W3 循环检查**：受影响域 pytest+own-diff 门自洽，修复复跑，**连续两轮 0 失败=过**。
5. **W4 红蓝对抗**：redblue 框架对本夜 own-diff 面，问题即修。
6. **W5 收尾交付**：八卡台账终同步（交付报告/环节总表/桌面三面）、队列终态、临时文件清理、claim 释放、`99_delivery/交付报告.md`、向 Owner 端到端汇报。

## 三、硬纪律（继承审计结论+总包夜战教训）

1. 冷启动 PATH=Python312；`lock_files.py cleanup && process_reaper --status`；改前 claim、毕后 release。
2. 提交唯一正门 `git_commit.py --session <sid> --files …`；主区直改带 `--allow-non-worktree`；失败 `--adopt-prior-work`；忙则 `--enqueue`。
3. 新建 .md 必带 frontmatter（created+ttl: task_bound+completes_when——TTL-METADATA 门硬拦教训）；新目录名禁数字后缀（R5-DIGIT-SUFFIX）；文档内禁出现旧家 tests 加 unit 斜杠路径字面串（GATE-NO-TESTS-UNIT 拦截，一律拆写）；新建 .py/.yaml 先 token（map_mounts 或 no_mount_reason）；新 src 模块 depgraph 设计节点（RULE-DEPGRAPH）。
4. 热册（registry/ruling）必 safe_write_text CAS+回读核实；注册表并发 stomper 在飞——写后进程外复核。
5. 他会话 staged/modified 不碰；发现他队已完成面→**交叉验证**（本轮 Owner 令）而非代修；冲突文件登记缓行。
6. 车道无法裁→写本车道 OPEN_QUESTIONS 登记+跳过；**删除/退役类+§5 门位类=登记留呈 Owner**；三处尝试仍堵→登记+跳过，禁死磕。
7. 测试输出走 tmp_path；禁裸 reset/checkout/restore；commit 后 `git log -1 --name-only` 核归属。

## 四、车道分工与台账

| 车道 | session | 卡源 | 台账 |
|---|---|---|---|
| R 恢复 | st-acure-r1 | P0-1/P0-7/P0-10（8 卡死袋簇） | 02_lanes/R_recover_workbook.md |
| E 勘误 | st-acure-e1 | P0-2/P0-3/P0-8+P1④⑤⑥ | 02_lanes/E_erratum_workbook.md |
| B 分支 | st-acure-b1 | P1② l8 落地 | 02_lanes/B_branch_workbook.md |
| G 桌面 | st-acure-g1 | P0-6/P0-9 | 02_lanes/G_desktop_workbook.md |
| Q 开口 | st-acure-q1 | ❓C312/C271/C315+P2 择要 | 02_lanes/Q_open_workbook.md |
| M 挖矿 | st-acure-m1 | 逐项施工卡编译+漂移复核 | 01_mining/ |

## 五、交付判据

- **挖干**=施工卡六向台账齐+三态裁定。**完工**=HEAD 字节在+测试绿+台账回填。
- **全绿**=循环检查连续两轮 0 失败+红蓝 own-diff 零未修复项（外部病理失败如实登记移交，不计 own-diff）。
- **交付**=`99_delivery/交付报告.md`：车道汇总/裁定清单/Owner 保留呈报/队列锁临时文件终态/与外部审计 P0 清单逐项闭环对照。
