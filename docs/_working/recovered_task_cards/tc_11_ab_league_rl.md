---
card_id: TC-11
title: st-autolnk 战役第五棒（A/B 联赛 + 模拟盘卖出测试 + RL 训练器）
verdict: 存活、无人认领、零施工（置信度高：四件开工项在盘上/git 全量清单/今日提交中零踪迹；但交接面真实存在且交接簿 staged 未提交有丢失风险；交接簿"residual 已收工"声称不成立）
category: E类-施工批（automation 车道）
priority: P0（第一动作=护住交接簿）其余 P2
size: 中
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 847-870 行与第 871-896 行——**同一指令逐字重复登记两次**（重复挂账，执行按一条处理）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-11 st-autolnk 第五棒（A/B 联赛+卖出测试+RL 训练器）

## 0. 一句话结论

第五棒在多会话生态里被"漏排班"：交接簿 09-21 00:45 写完即 staged，此后无人认领、四件开工项零踪迹。任务本身原封未动且可执行——件 1（A/B 联赛五件套+测试，全新文件无冲突）、件 2（模拟盘卖 100 股 510300，持仓与 T+1 条件实测成立，但交接簿的限价参考 4.66 元是成本价、市价已 5.04，照抄会挂单失败）、件 3（RL 训练器，ex_sor 有骨架无训练器，开工前要先按 H-04 新口径登记裁定）。**第一动作是把 staged 未提交的交接簿落袋防丢**。

## 1. 背景与来龙去脉

st-autolnk 自动化战役前四棒交付：六线设备（上架流水线/ECB 首源实弹/转正组合门/情报采集器/骨架体检/标准库/红线引擎）、挖矿文档树封矿、QMT 桥 100 股买测、R1 调度器激活。Owner 已裁定：除实盘外全部可做。第五棒三件事：件 1 建 A/B 联赛（联赛注册表+参赛档案百分百复原口径+月度快照，判定器复用 promotion_combo_gate，6 个月终审挂单）；件 2 模拟盘卖出测试（510300 卖 100 股，证据 yaml 落 evidence/）；件 3 RL 训练器（TD3 起步+历史 replay 预热+checkpoint，产物只进模拟盘对拍）。件 4 数据源维持自动无需动作。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 交接总簿 HANDOFF_20260921_ab_league.md 存在 | 在盘（09-21 00:45，6749B）且 staged，**未进 HEAD、从未被提交**——无 commit 保护，共享区回滚链有吞文件前科 | ls + git status + git ls-tree | A |
| CAMPAIGN_LEDGER.md 运营真源 | 在盘但最后更新停在 09-18 04:14 第三棒终局态——交接事件未回写台账 | Read 全文 143 行 | A |
| 件 1 联赛五件套+作业簿 | **全部不存在**：mining/ 只有 00-10 十工段；config/、scripts/backtest/ 无任何 league 文件；git 近 3 天 grep league/联赛 零提交 | ls + git ls-files + git log | A |
| 件 2 卖出证据 yaml | **不存在**：evidence/ 仅 4 件，最新实物=09-18 买入 smoke；今日零新增 | ls -lt evidence/ | A |
| 持仓 510300×1100 股 T+1 已过 | **属实**：PositionStatics.csv（09-19 20:50）拥股 1100、成本 4.6595、备注"零售10测试"；按 T+1 今日 09-21 全额可卖。**两处折扣**：交接簿建议限价"约 4.66 元"实为成本价，快照最新价 5.04（价参过期约 8%）；需盘前刷新实时价 | Read E:\qmt_bridge_sim\Stock\PositionStatics.csv（只读） | A |
| 件 3 RL 训练器 | 未施工：src/zephyr/ex_sor/ 存在但是 algo_flow 域旧资产；唯一 RL 件=core/rl_exec_env.py 骨架（自述不含任何训练逻辑，B-007 留痕）；无 TD3/trainer/checkpoint；交接簿写路径漏了 core/ 层 | ls + Read rl_exec_env.py:42-44 | A |
| 件 4 数据源 4 天绿 | 台账与交接簿口径一致（R2 打卡 66 行 09-17 到 69 行 09-18，Windows 任务 23:30 自动）；行数未连库复核 | CAMPAIGN_LEDGER | B |
| "residual 战役已收工归档（C1 解除）"（交接簿第 14 行） | **证伪（与 TC-08 独立互证）**：物理归档发生了，但总簿 frontmatter 仍 campaign_running、九节点七个空框；"C1 解除"无留痕佐证且自相矛盾 | Read archive 总簿 + TC-08 交叉 | A |
| 有会话认领第五棒 | **无**：.runtime/sessions 无第五棒；今日 00:00 后提交全落 ulib/intake/data-fix/unified 域，零 league/ex_sor/sell 内容 | ls -lt .runtime/sessions + git log --since | A |
| ReadSessionContext 恢复面 | 可读且信息量超交接簿：Owner 四条裁定细目（联赛立即开赛/卖出腿需实测/RL 只做执行训练 L5/永不回答"买什么"）+2 个持久测试失败（test_generate_resource_profile_registry.py 计数 25!=24、22!=21） | ReadSessionContext(sess_526a209c-3f12-4535-95c6-25cc197ab05e, strategy=handoff) | B |

### 病根

1. **漏排班**：交接簿写完 50 分钟内 HEAD 又前进 5 笔全属其他车道——第五棒不是被打断，是根本无人接班。
2. **交接簿是未落袋的高价值资产**：staged 未提交无 commit 保护；台账（运营真源）未回写交接事件，违背台账自身"每完成一个有意义步骤就更新"的持久规则。
3. **"收工归档"话术污染状态恢复面**（与 TC-08 同病灶）：把目录搬运写成战役收工——照单全收会错误绕开 residual C1 三共享文件约束。
4. **指令层重复登记**：源文件同指令出现两次，若两个会话各认领一段会双开同一战场。
5. 小史实漂移累积：rl_exec_env 路径漏 core/、限价用成本价——交接簿"00:4x 实测"部分内容是转抄非实测。

## 3. 上下游

- 前置：交接簿+原始会话胶囊（均可读）；件 2 依赖大 QMT 模拟端进程与交易时段；件 3 依赖 torch 环境（交接簿称曾实测可用，B 级）与 H-04 口径登记。
- 下游：CAMPAIGN_LEDGER 状态回写、晨报、promotion_combo_gate 6 个月终审挂单、sim_pocket_daily 月度快照消费链、H-04 Owner 门。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 0（先行，半小时级） | 恢复+护住交接面：读 HANDOFF 全文+ReadSessionContext；把交接簿与台账回写（第五棒接班记录）经 GitCommitGateway 落袋防丢。状态恢复另三源：docs/_working/automation/20260917_fullauto_skeleton_v1.md 第 4/5 节（件 1 作业簿格式参照）；记忆键 automation-campaign-night-20260917 与 night-shift-autolnk-landed-20260917（自动加载）；原始记录 C:\Users\fanzi\.zcode\cli\rollout\model-io-sess_526a209c-3f12-4535-95c6-25cc197ab05e.jsonl（一般不用） | docs/_working/automation/campaign/HANDOFF_20260921_ab_league.md、CAMPAIGN_LEDGER.md | 两文件在 HEAD 有 commit hash | Flash |
| 1（件 1 主体） | A/B 联赛：先写 mining/11_联赛/工段作业簿.md（十节封矿），再施工 config/league_registry.yaml + scripts/backtest/league_registry.py + league_archive.py（参赛档案：git hash+因子清单+数据截止日指纹+整装产物指针，百分百复原口径）+ league_restore.py + league_monthly_snapshot.py（sim_pocket_daily 按组对比月快照，只留档不判定）+ 全套测试；判定器复用 scripts/backtest/promotion_combo_gate.py（实物已在）挂 6 个月终审单 | 上述新文件+tests/backtest/test_league_*.py | 全套测试绿+GitCommitGateway 落地 | Flash（全新文件无热文件冲突） |
| 2（件 2） | 卖出测试：QmtFileBridgeBroker(env="sim")（真类名，src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py——勿写成 QmtFileBroker，该类不存在）卖 510300 中 100 股；**限价必须按盘前实时价刷新（参考区 5.0+，勿用交接簿 4.66）**；证据 yaml 落 evidence/；夜间提交+晨间复核成交腿（第三棒先例 runbook 在 docs/_working/automation/campaign/qmt_e2e_runbook.md） | docs/_working/full-auto-chain/evidence/qmt-bridge-sell-20260921-c4.yaml | 证据 yaml 落盘+成交腿复核 | Flash（模拟户授权 Owner 已批）；成交腿异常升 Owner |
| 3（件 3） | RL 训练器：src/zephyr/ex_sor/ 下（建议 services/ 或独立 trainer 子包）搭 TD3 起步+历史 replay 预热+checkpoint；产物只进模拟盘对拍。**开工前按交接簿 H-04 新口径登记裁定或更新 rl_exec_env.py 留痕**（该文件自称真训练属 B-007 Owner 闸门，与新口径冲突） | src/zephyr/ex_sor/（新 trainer 子包）、core/rl_exec_env.py 留痕 | 训练器成型+checkpoint 可恢复；模型只进模拟盘 | 施工 Flash；真训练触发 H-04=Owner 门位 |
| 4（件 4） | 零动作：晨报带一句连绿天数 | — | 晨报在案 | Flash |
| 5（收尾） | 循环检查两轮零问题+红蓝+Gateway 落地+清理临时文件+晨报；顺带复跑 test_generate_resource_profile_registry.py 的两处计数断言（25!=24、22!=21）——原会话已追认两轮 72/72 绿，仅复现才修，勿盲修 | tests/ 相应文件 | 两轮零问题记录+晨报落盘 | Flash |

## 5. 与其他任务卡的关系

- **TC-08：直接重叠的证伪对象**——本卡交接簿"residual 已收工"正是 TC-08 调查对象，两卡记录已统一为"未收工"。第五棒施工不碰 residual 遗产（pipeline_events/tasks.yaml/apply_ddl 三文件），若确需动则先 acquire 并在台账留痕。
- TC-04：stash@{0}（WO-13续）归其域，本卡零交集已避让。
- TC-07：终极图书馆/unified 批与本卡零文本交集；联赛的月度快照未来可接 TC-07 的 L5 排产轴。

## 6. 风险与避让红线

1. **绝不触碰交易面红线**：QMT_REAL_*/enable_real/ZEPHYR_ENV=live 全禁；MiniQMT 已下线禁拉（一切走大 QMT 文件桥）；kill_switch 持久态禁下单。
2. 勿照抄交接簿 4.66 限价（成本价残留，市价 5.04+），卖出前刷新实时价。
3. 交接簿未落袋是最高丢失风险：开工第一动作先落袋。
4. 件 1 全新文件无冲突，但避开 docs/03_modules/**、TDM、AGENTS.md 三禁写区；新 .py 遵守 REPO_ROOT+now_utc()+CREATE-GUARD 登记。
5. 源指令重复登记两次：只认领一次。
6. 更多硬拦（原文红线残余，条件触发才炸但炸了就返工）：TRAE-079 限 overlap 24h5 次（热文件用 lock_files acquire）；CREATE-GUARD 引用的 token catalog 必须同批入袋；新 .py 的 [BLUEPRINT] MOD-ID 禁括号；m11 豁免=noqa+理由≥10 字；ch_reader.query 返回 TSV 字符串。
7. 遇问题自裁（架构师框架），无法裁定登记+跳过——不停不问继续下一件，不要事事升 Owner。
8. 改后即 git add（共享区回滚链吃未 add 文件）；staged 外来内容连坐时一律 --enqueue 队列。mining/ 简写歧义说明：实树=docs/_working/automation/campaign/mining/（00-10 十工段在册）。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；ReadSessionContext(sessionId=sess_526a209c-3f12-4535-95c6-25cc197ab05e, strategy=handoff, query=A/B 联赛开工清单/卖出测试/战场状态)；pid=0 会话 90s 过期（注册+提交同一命令）；文档禁"第 N.N 节"点号写法（DANGLING-REFERENCE 拦，写"第 N 节"）。
