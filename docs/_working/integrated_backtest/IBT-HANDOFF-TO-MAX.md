---
ttl: task_bound
completes_when: Max 施工方案产线落地后本件随批归档
session: st-integrated-bt-20260922
issue: IBT-HANDOFF-001
---

# 整装回测首跑 → Max 施工方案 交接包（2026-09-22 晨）

> 本件=st-integrated-bt-20260922 会话的完整交接。首跑已收官（红蓝连续两轮 0），
> 交接下来=Max 把 §2 问题清单整合成完整施工方案。

## §1 项目背景浓缩（30 秒版）

ZephyrAlpha=A 股量化系统（100% AI 开发，Owner 只拍板）。三层：治理层（门禁/宪法）/
交易业务层（TDM 四层级联：大盘 regime→板块→个股→组合）/AI 层（自动挖矿）。
本战役=项目史第一次**协议治理下**的整装回测（四层级联历史回放），按预注册协议
IBT-PROTOCOL-V1 跑完四窗+红蓝四向四轮（连续两轮 0），产出进模拟盘准入判定=
**「差什么」**：链路/正确性/披露三门过，绩效门 C 不过（保密考卷 Sharpe -1.39）。

## §2 问题清单（Max 施工方案的整合输入，按优先级）

### P0 阻断级（不修则后续一切自动搜索白跑）

| # | 问题 | 实锤证据 | 修复方向 |
|---|---|---|---|
| 1 | **#326 池污染**：C4 翻译件考卷有前视/幸存者污染（成分回灌 15 件+同 bar 7 件） | 裁定#326 在案；本次 HOLDOUT 盲窗成员 4/15 微正全 <+4.1% 互证 | 修 15 件翻译件的宇宙回灌与同 bar 逻辑（参照 lane_c PIT 修复范式），修完进 E4 重考 |
| 2 | **成本/换手未进考尺**：自动搜索会专挑"纸面亮实盘死"的勤快策略 | 本次 IS 零成本 +26.5% vs 全成本 -12.1%（拖累 38.6pct）；年换手 33-39x；4440 单跑 IS -91%（容量标定 77 万互证） | E4 考尺加成本敏感性门槛+换手上限门（E7 换手门已有位，接电）；搜索目标函数=成本后 Sharpe |
| 3 | **N_trial 记账未接自动管线**：跑越多假金子越多 | 批次B 1 万格点幸存者全被 WFA 否决；裁定#306：N=4562 下 DSR>0 数学不可过（尺子自护正确） | n_trial_ledger 接入 F06Grid/自动挖矿每次尝试；DSR 分母 N_eff 从档案自动复算（f06_e4_wfa_exam.py:345-348 手填病根治） |

### P1 高优（进模拟盘差项三件套）

| # | 问题 | 实锤证据 | 修复方向 |
|---|---|---|---|
| 4 | **HOLDOUT 新鲜重考**：池时效衰减 | IS 全负→OOS 集体正（与池选择窗重叠=自证）→HOLDOUT 近乎全灭 | 修完 P0-1/2 后以 2025-09..2026-09 为新鲜 OOS 重考一轮，产新存活名单再整装 |
| 5 | **regime 节流方向失真**：r4/r10 后 20 日前向收益为正，先验映射四窗三负 | IBT-B vs IBT-A：IS -15.6pct/OOS -5.5pct/HOLDOUT Sharpe 更差；与 S-OWNER-002 实测互证 | 丁线 regime 检测器治本同源；治本前节流脱钩（IBT-A 口径为准） |
| 6 | **降换手改造**：FACT 族日频 top20+4440 超短是换手主力 | 成本归因：佣金 27.5 万+滑点 13.9 万/百万本金/年 | FACT 拉长持有期（top_n 调仓频率参数化进 E4 网格）；4440 弃用或降资金至容量内 |

### P2 结构级（不阻断但决定上限）

| # | 问题 | 现状 | 方向 |
|---|---|---|---|
| 7 | L2 板块门 stub（恒 absent→编排器 D2 降级） | sector_gate 纯函数件在，零日触发；daily_gate_snapshot._collect_l2()=stub | BT-P1-030 立项施工 |
| 8 | 组合权重=等权 1/15，无 PP-001 配比与 regime 权重矩阵 | framework_plans.yaml 三套 Owner 已批预设+fw-tdm-current 自动生成在 | E8 装配层：QuantCombine 三算法（SFFS/NSGA-II/Pareto，收藏包#16 设计输入，禁抄代码）+7 态×成员权重矩阵 |
| 9 | 指数腿不可实盘（000300/000852/000016 用 kline_index 代理） | 本次 6 员持有指数腿，撮合按指数价成交 | 实盘化=ETF/期货替代+跟踪差建模 |
| 10 | 引擎满仓摊派语义（任意成员有信号即满仓，半仓意图被放大） | 协议 §10.1 已披露；shrinkage 层是唯一减法通道 | 引擎 v2 或 composer 层支持 Σ<1 目标权重直通 |
| 11 | G4 欠账：无棘轮/无做T配对核算 | TDMAP-001 §2 G4 未施工 | 按 backlog 排期；落地前回测结论带折扣标注 |

### P3 运维级

| # | 问题 | 说明 |
|---|---|---|
| 12 | 02:30 夜跑带推进 hfq 表→跨批数字微漂 | 长批数字必须同批产出（本次敏感性已按此纪律重跑） |
| 13 | 共享 serializer 单点：挂死进程可阻塞全队列 2.4h+ | 本次机械判死解锁一例；commit_chain R1-R7 改进已落（Owner 0922 通函令），观察生效 |
| 14 | docs/_working 禁 .json/.py（DCR）/data 子目录 gitignore 白名单 | 本战役三死后定型：机读产物=docs/_working 下 .yaml，.py 去 scripts/，或者产物进 data/ 白名单路径（需先加白名单） |

## §3 本战役完成清单（全部 done）

| 任务 | 状态 | 产物 |
|---|---|---|
| §1 冷启动（reaper/注册/心跳） | ✅ | daemon PID 见 .runtime/locks/heartbeat_st-integrated-bt-20260922.pid |
| §2 真源读序（4 并行只读代理） | ✅ | 结论浓缩进 IBT-CAMPAIGN-LEDGER.md §1 |
| 分包1 数据完备性矩阵 | ✅ | IBT-DATA-MATRIX.md + ibt_data_matrix.yaml |
| 分包1 协议 v1 冻结 | ✅ | IBT-PROTOCOL-V1.md（frozen 2026-09-22T01:05） |
| 分包2 四窗首跑+成员单跑+敏感性 | ✅ | artifacts/<四窗>/ + IBT-RUN-REPORT.md + ibt_attribution.yaml |
| 分包3 红蓝四向四轮 | ✅ | IBT-REDBLUE-REPORT.md + artifacts/*/redblue_round*.yaml（round3+4 连续两轮 0） |
| 端到端交付报告+准入判定 | ✅ | IBT-FINAL-DELIVERY.md（判定=差什么） |
| 收官提交 | 🟡 q-0006 在 serializer 处理链（见 §5） | 40 件快照袋 |
| 台账/memory/临时清理 | ✅ | MEMORY.md 已加条目；.runtime/tmp 仅余心跳 daemon |

## §4 待 Owner 裁定事项

**无门位触发项**（本战役未动注册表净删/未翻 flag/未接实盘）。Max 方案若涉及以下项需回流 Owner：
- 改进批次排序与资源排期（多线并发时写域切分）
- 4440 弃用（判死=Owner 门位）或降资金
- PP-001 配比表数值（此前 Owner 批的是演示权重，生产配比待定）

## §5 提交状态与落地核验（接手第一件事）

本战役终批=**q-20260922-st-integrated-bt-20260922-0006**（40 件快照袋，DCR/Gitignore
双预验零违规），在共享 serializer 处理链中（多会话夜班积压，非卡死）。

核验命令：
```
git log --all --oneline --grep "IBT"        # 有输出=已落地
python scripts/commit_queue.py --queue-root .runtime/commit_queue status   # 看 q-0006 状态
git log -1 --name-only | grep integrated     # 落地后核实归属未吸收他人
```
若 q-0006 死亡：读 .runtime/commit_queue/dead/q-*ibt*-*0006.json 的 dead_reason 修正后
`python scripts/commit_queue.py --queue-root .runtime/commit_queue requeue <qid>`。
历史上 q-0001 死 DCR（docs/_working 禁 .json）/q-0002 死 gitignore/q-0004 死漏网根
json/q-0005 死复现脚本 .py——q-0006 已全部规避，若仍死于 DCR 请按 dead_reason 逐条对齐。
**注意：主区工作区 docs/_working/integrated_backtest/ 为 untracked 态=与快照袋同内容，
勿手工 git add 走直连（会绕过门禁且与队列重复）；一切以队列落地为准。**

## §6 必看文件路径（全相对 D:\ZephyrAlpha）

**本战役五册+台账**（交接的知识主体）：
- docs/_working/integrated_backtest/IBT-PROTOCOL-V1.md（预注册协议，跑后禁改）
- docs/_working/integrated_backtest/IBT-DATA-MATRIX.md（数据完备性矩阵）
- docs/_working/integrated_backtest/IBT-RUN-REPORT.md（四窗绩效+归因+缺陷记录）
- docs/_working/integrated_backtest/IBT-REDBLUE-REPORT.md（红蓝四向四轮）
- docs/_working/integrated_backtest/IBT-FINAL-DELIVERY.md（交付报告+准入判定）
- docs/_working/integrated_backtest/IBT-CAMPAIGN-LEDGER.md（append-only 台账）
- docs/_working/integrated_backtest/IBT-HANDOFF-TO-MAX.md（本件）

**机读产物**：docs/_working/integrated_backtest/ibt_attribution.yaml + ibt_data_matrix.yaml
+ artifacts/<W_IS|W_OOS|W_HOLDOUT|W_POSTD>/{run_summary,sensitivity,redblue_round*}.yaml
+ artifacts/<窗>/{nav,trades}_IBT-{A,B}.csv（审计链）+ artifacts/IBT-RUN-LOGS.md（跑批日志）

**复现脚本**：scripts/backtest/ibt_first_run/{ibt_runner,ibt_redblue,ibt_attrib,ibt_mining_matrix}.py
（跑法：`python ibt_runner.py --window W_IS`；HOLDOUT 须 `--holdout-guard`；敏感性 `--sensitivity` 仅 IS/OOS）

**上游真源**（Max 方案必读）：
- docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml（142 对象，5 条 frozen plan）
- docs/01_policies_and_standards/sop/backtest_system_sop/（README+SOP-A/B/C/D+exam_policy）
- docs/_working/archive/2026-09/c_class_scattered/2026-09-07-tdm-backtest-protocol.md（TDMAP-001 母协议）
- docs/_working/archive/2026-09/sharpe2_prep/（E4 存活 17 条名单+组队台账+勘误头）
- docs/_working/archive/2026-09/collection_intake/eng_quantcombine_idea_mining.md（QuantCombine 思想=问题#8 设计输入）
- docs/_working/archive/2026-09/collection_intake/engineering/eng_benchmark_llm_quant_factory.md（LLMQF 对标件）
- config/trading_decision_map.yaml（TDM 地图）+ config/framework_plans.yaml（整装方案真源）
- src/zephyr/pf_core/strategy_engine/framework_composer.py（合成引擎，他会话在途件只读）
- src/zephyr/strategy_pipeline/fw_backtest.py（整装 CLI，他会话在途件只读）
- docs/_working/ai_layer_vision/ai_layer_vision_and_roadmap_v1.md（AI 层 GPU 三路）
- docs/_working/data_fix_campaign/final_delivery_report_20260921.md（数据地基凭证）

## §7 会话收尾清单（Max 可代执行）

- 心跳 daemon（PID 见 locks）与 SessionRegistry 注册保留至 q-0006 落地；落地后：
  `python scripts/git_commit.py --release-only --session st-integrated-bt-20260922` 释放
  claim → terminate PID → SessionRegistry.unregister('st-integrated-bt-20260922')。
- 心跳 daemon 进程=python .runtime/tmp/ibt_hb_daemon.py（reaper 白名单已登记，无需保护）。
