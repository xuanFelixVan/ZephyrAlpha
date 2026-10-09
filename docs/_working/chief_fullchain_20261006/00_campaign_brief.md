---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/00_campaign_brief.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# st-workingchief-20261006 总包战役宪章（工作区审计 + 全链挖矿 + 并发施工 + 红蓝收尾）

> **使命**（Owner 2026-10-06 夜指令）：①docs/_working 全量文档完成度审计——完成的表头写结案报告、彻底完成的归档；②按挖矿 SOP 挖全链环节骨架（环节无遗漏→分环节→分子类目），挖干封矿后按施工 SOP + 内收原则施工；③与他队（今晚另有五个施工大队）冲突回避：同文件已在编则登记让后、他队已完成的做交叉验证；④端到端收尾：测试修复循环至连续两次零问题 → 红蓝对抗 → GitCommitGateway 落地 → 临时文件清理 → 全量交付报告。

## §1 会话身份与合规登记

| 项 | 值 |
|---|---|
| 会话 | st-workingchief-20261006 |
| 角色 | 总包（统筹/协调/检验/裁定/收尾交付） |
| 冷启动 | RULE-ENV ✅(3.12.8+usercustomize 在岗) / RULE-GUARDIAN ✅(reaper last_run=2026-10-06 01:07, 白名单已登记 st-workingchief-20261006/chief_fullchain_20261006) / session_startup_check ✅(无阻断失败项；gate_blueprint_mandatory/gate_path_tree_freshness 为存量 RED，提交前重跑 path tree) |
| **工作区降级登记** | **直改主区**（非 worktree 默认）。理由：本役为跨队总包——需实时读他队施工面做冲突回避与交叉验证；全部修改走 lock_files claim + safe/Edit + `git_commit.py --enqueue` 队列串行落地，冲突面与 worktree 等效受控。此登记即显式申请记录，GW 计数与周审计照常覆盖。 |
| claim | 战役区 32 件已 acquire-batch（TTL 480min，毕后 release） |
| 提交 | 唯一入口 scripts/git_commit.py；锁忙自动改道入队 |

## §2 战场态势（2026-10-06 01:00-02:00 实查）

- 他队在役（claim 实查）：**st-fig13-bone-20261004**（config/data_supply_chain_map.yaml、config/trading_day_cycle_map.yaml、docs/_working/map_build/fig13_daycycle/*、fig13 生成器/校验器/门禁）→ 本役对其**只读借力**。
- 他队在役（文档证据）：st-datasop-20260930（fullflow_mine 七批收尾）、st-tclose-c1close-20261005（total_command_closeout 收口波）、st-gomap-*（GOMAP 车道）、commitmap 系（registry 侧）。
- active 役区禁归档清单：map_build、total_command_closeout、fullflow_mine（+审计判 ACTIVE 者）。
- docs/_working 规模：3774 文件 = live 2671 + archive 1103；live md 2586（ALREADY_CLOSED 105 / RECORD 142 / TASK 139 / OTHER 1737 / 非 md 548）。

## §3 总包裁定记录（本役自裁，按挖矿 SOP §6 三态）

| # | 裁定 | 依据 |
|---|---|---|
| R-1 | 文档审计分层：根目录 17 未盖章件逐一精审+盖章；战役文件夹按役裁定（CLOSED 四条件法），CLOSED+archive_ready 者整役归档 archive/2026-10/ 并在其终局件表头盖结案报告；MIXED/ACTIVE 不动只登记。 | 万无一失与冲突回避的平衡：1737 个 OTHER 文件逐件盖章会与他队撞车且无增益；役级终局件盖章满足"表头写结案报告"，归档即彻底封存。先例：st-fullchain-20260914 曾逐件盖、清理批自动生成章均有案。 |
| R-2 | 全链环节骨架=21 环节（五域甲乙丙丁戊），真源=九图（GOMAP/TDM/FACTORY/图11/12/13/14/15/立法流）。环节清单与分环节作业簿见 01_skeleton_environments.md + env_mining/。 | 骨架挖矿 SOP（skeleton_mining_policy）：路由表+计分板+防腐；九图为机械对账真源。 |
| R-3 | 施工范围裁定（终局全貌量尺）：本役施工面=①结构性文档/注册缺口（七图未入 ROOR 等，无人认领）；②他队已完成成果的交叉验证；③本役产出自测。**不碰**：fig13 领地、fullflow_mine 施工线（st-datasop 在跑）、Owner 门位 34 项（备料不代裁）。 | 他队正施工的不代做（冲突回避+交叉验证指令）；Owner 门位按宪法 §5 不可自裁。 |
| R-4 | audit 章自动生成与人工精审并行：脚本批量盖 RECORD 类（报告/交接/复盘无待办者），精审盖 OPEN 判定。 | 清理批自动生成章有先例（2026-09-05 审计件）。 |

## §4 冲突回避登记簿（实时更新）

| 他队 | 领地 | 本役处置 |
|---|---|---|
| st-fig13-bone-20261004 | fig13_daycycle/*、data_supply_chain_map.yaml、trading_day_cycle_map.yaml、fig13 生成器/校验器/gate | 只读；骨架引用其产出 |
| st-datasop-20260930 | fullflow_mine/*（七批收尾） | 只读+交叉验证其成果 |
| st-tclose-c1close-20261005 | total_command_closeout/* 收口波 | 只读 |
| st-gomap-* | GOMAP 车道 + scripts/governance/d5_architecture | 只读；ROOR 登记避让其提交窗 |
| （待遇）commitmap 系 | registry 侧 | ROOR 编辑前先 claim+check |

## §5 线间并行流水（线内先挖后干）

- 线1 文档审计线：root 17 件精审 + 113 役裁定（分 4 批子代理）→ 批量处置（盖章/归档）。
- 线2 骨架挖矿线：21 环节作业簿（env_mining/，六向台账+自审闸三态）。
- 线3 施工线：ROOR 七图登记等无人认领缺口。
- 线4 交叉验证线：他队成果抽验（EXEC-1/2a、T2 发车、F73/F75、净删抽查）。
- 线5 测试与红蓝线：基线→修复循环→连续两次零问题→红蓝对抗→收尾。
- 谁挖干谁先开工；不用等总包逐条点头（Owner 指令）。

## §6 产出物索引

| 件 | 内容 |
|---|---|
| 01_skeleton_environments.md | 全链 21 环节 MECE 骨架+九图真源清单 |
| 02_gap_ledger.md | 全流通缺口总账（考古 16 役合并，按归属分流） |
| 03_folder_audit_method.md | 审计方法（CLOSED 四条件等） |
| 05_folder_verdicts.md | 113 役裁定台账 |
| 06_root_sweep_ledger.md | 根目录逐件台账+结案报告草稿 |
| env_mining/env_01..21 | 分环节挖矿作业簿 |
| 90_chief_runlog.md | 执行日志 |
| 99_final_delivery.md | 端到端交付报告 |
