---
card_id: TC-04
title: ALGO_FLOW 收口遗留（R1 防回退复审 + W2/W4 施工 + D1-D6 裁定卡）
verdict: 部分存活（置信度高：R1 使命完结 8/8 无回退；D1/D2/D4 已被裁定吸收死亡；存活核心=W4 续作（WIP 在 stash@{0}）、W2 三项去留再裁定、R2 补登记、D5 注册表回写）
category: E类-施工批（生成器车道）+ D类裁定项
priority: P1
size: 中
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 334-459 行（"四："节）
investigated_at: 2026-09-21
head_at_investigation: 83329aef38
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-04 ALGO_FLOW 收口遗留

## 0. 一句话结论

R1 防回退复审的使命已经完结（8/8 提交全为 HEAD 祖先零回退，归档 8 件齐全），D1/D2/D4 三个"待裁项"已被 #385/#338④/#333 三条裁定整体吸收而死亡。真正活着的是四件：**C2 W4 自指豁免施工**（WIP 119 行躺在 stash@{0}，作者会话已死）、**C1 W2 三项治本**（代码里客观未做，但母题 #ARCH-324 已被 #377-G03 裁 close，继续做需再裁定）、**R2 三项移交登记不实**（至今无人补登）、**D5 架构议题册回写**（337 仍 open、331 至今未登记、324 的 close 未回写）。

## 1. 背景与来龙去绪

landing-anchor-algo-flow-closeout 战役（09-18）完成 ALGO_FLOW 出仓与锚定后留下交接令：R1=前任成果防回退复审；C1=W2 提交链三项治本施工；C2=W4 自指 fixture 判据式豁免施工；D1-D6=六项待裁定题。原文特别声明归档文档已不在原路径、8/8 已入库。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| R1：8 提交防回退 | 8/8 全部 HEAD 祖先零回退（562320d091/c9008bf91e/8559bf00d7/b0c2999b80/e4df828ddc/fa39796599/2ac7d910ed/15de0d4734） | git merge-base --is-ancestor 逐一退出码全 0 | A |
| R1：归档区 8 件齐全、孤件 yaml 已出仓、#ARCH-326 仍 resolved | 全部属实 | ls 归档目录 + cat-file 128 + registry status | A |
| C1① 落地后 blob 回灌主树 index | **未落地**：全仓落地链无 update-index/主区 add；_converge_main_workspace 设计明示共享 index 不被触碰；09-18 后零相关 commit | grep 回灌/update-index + commit_queue_landing.py:582 | A |
| C1② qid 命中 done 短路返回 landed_id | **未落地**：enqueue_item（commit_queue.py:593-702）无 done 查询；已有的是 drain 侧重放幂等保护不是免重复入队 | 通读两函数源码 | A |
| C1③ claim 路径空间统一 | **未落地（无施工 commit）**：git log -S 'wt_files' --since=09-18 零命中 | git log -S + 源码 | A |
| C1 母题状态 | #377-G03（09-20）已裁 #ARCH-324 按 A 案实态 close（belt_daemon.lock mtime=09-20 12:50 证守护已拉新码），B 案留下一版不排期；registry 回写挂执行指针，status 仍 open | p7c_efgh_family_rulings.md:56,113 + architecture_issue_registry | A |
| C2 W4 谓词式豁免 | **未落地**。HEAD 两生成器无自指豁免；**WIP 实物在 stash@{0}**："WO-13续 salvage: externalize_algo_flow self-ref fixture exemption WIP"，含 externalize_algo_flow.py 119 行改动（作者会话已死） | grep 两生成器 + git stash show --stat | A |
| D1 N-5 | 已被 #385 终审替代（此子项死），台账归档在 docs/_working/archive/2026-09/n5_closure/ | ruling_registry 5127-5160 行 | A |
| D2 DS-271 | 已被 #338④ 预注册三口径闭合（IS 窗=36 月窗缩先行出证、mid 不入聚合、切换=Owner 双轨并跑 4 周起） | ruling_registry 4390-4394 行 | A |
| D3 排班 v2 残余 | 大部分吸收：蓝图×2=#377 判 a 批准（施工件 E-01/E-04 晋升 git mv 留执行指针）；L-6/C-12 仍挂注册表车道 P4 | p7c 判定册 + resource_schedule_v2_construction_plan.md:60,75 | A |
| D4 Kimi R1-R4 | 已闭合：#333 签署 S18-R1/R2/R3/R4 生效 + 四条 P0 复核通过；#320 修订 R3 前提 | ruling_registry 4215-4231 行 | A |
| D5 #ARCH-337/331/324 | 337 仍 open（registry:22149）；330=resolved；**331 至今未登记**（全文 0 命中）；324 close 未回写 | architecture_issue_registry 各 issue_id | A |
| D6 环境遗留 | security_event_bus/telemetry 已由 #255 裁定（总线保留、飞书通道退役移交）；页面文件扩容/DR 演练无处置痕迹=Owner 物理件仍开 | ruling_registry 1920-1940 行 + COORDINATION_LEDGER.md:802 | A/C |
| R2 F5_registry_debt/LEDGER.md | **仍不存在且无人补登**——"三项移交登记不实"的证伪结论本身也悬空 3 天 | ls + find + grep | A |

### 病根

1. **任务指令半衰期被多会话并行急剧压缩**：D1/D2/D4 在 48 小时内被三条裁定整体吸收，照单执行会做已死之事——接班者必须先查裁定注册表再动手。
2. **W2 三项的困境是治理态不是技术态**：代码客观未做，但登记母题已被裁 close。若 registry 回写先行，三项施工变成"对已关闭 issue 的孤儿施工"；根因=裁定收口时未对实证④附带的治本候选逐一销项。
3. **W4 的实物损耗形态**：施工做到 WIP（119 行）后作者会话死亡，被 classify_workspace_wip 判 stale_rollback 扫进 stash@{0}，且该 stash 混装大量他线文件——直接整包 pop 会重演 #ARCH-329 吸收事故。
4. **真源路径漂移**：commit_belt_daemon.py 已从 scripts/governance/ 迁到 src/zephyr/gov_enforcement/rule_bridge/——按旧路径施工会撞 CREATE-GUARD 或找不到文件。

## 3. 上下游

- 前置依赖：#377 判定册执行指针队列（总包排班）决定 W4/E-04 何时开工；stash@{0} 处置权归 WO-13续 salvage 车道，摘取按死会话遗物流程。
- 下游消费方：#ARCH-324 回写影响 own-diff 门禁与队列车道信任面；W4 谓词消费方=CloneGuard/ALGO_FLOW 出仓战役的 24 自指 fixture 误报面。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 1 | W4 自指豁免施工续作：从 stash@{0} 单独摘取 externalize/report 两件改动（git stash show -p 摘单文件补丁重放，**绝禁整包 pop**），按在册谓词 A/B 判据重验后走队列正门 | scripts/governance/d5_architecture/generators/externalize_algo_flow.py、report_algo_flow_author_debt.py（真路径以 git ls-files 为准）；判据=docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout/W4_selfref_exemption.md | 谓词命中/不误伤真克隆各一双向钉；禁路径白名单（裁定 #273）；过再生成窗 | Flash 施工（判据已在册可机判） |
| 2 | W2 三项去留再裁定案卷：呈"三项代码未做 + #377-G03 已裁母题 close + B 案不排期"三角事实，请 Max 定：随母题关闭销项 / 另立 backlog 卡 / 授权施工 | 真源 src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py、scripts/commit_queue.py、src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py（注意已迁移）、commit_queue_landing.py | Max 裁定号登记；若裁施工：收敛后主区 index 同步或等效消 MM 证据 / enqueue done 查询一钉 / 错配复现或判 moot；三项施工均**不新增第二真源** | Max 裁定（Flash 禁自裁） |
| 3 | R2 补登记：三项移交 LEDGER 补登或裁定作废 | docs/_working/flash_speedup/ 下新车道件 | LEDGER 落盘+三件可机判判据，或作废裁定号 | Flash 登记 / Max 裁作废 |
| 4 | D5 回写三件：#ARCH-337 处置推进（仍 open）、台账号 ARCH-331 补登记（注意：该编号在册缺失、注册表全文零命中——本步就是把它首次登记进册，登记完成前不存在合法的井号引用形态）、#ARCH-324 按 G-03 回写 close（附 lock mtime 证据） | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | 三条 issue_id 的 status 与裁定一致；safe_write_text CAS | Flash 施工（G-03 已有授权回写） |
| 5 | D3 残余施工：E-04 蓝图×2 晋升 git mv（#377 已裁 a 批准）+ 一次性任务删除销项核对（调查实证三处已并入 96 条批次，核对无残端即销）+ L-6/C-12 注册表车道（P4 低优先） | docs/03_modules/ 待建蓝图、resource_schedule 注册表 | 蓝图入 03_modules（N-15 豁免留痕）；一次性任务三处无残端；灌数/CONSUMERS 修正过闸 | Flash（有 #377 授权）/ P4 排班 |
| 6 | D6 物理件：页面文件扩容重启、DR 隔离演练——纯 Owner 基础设施门位，AI 只催办不执行 | 宿主机环境 | 重启后 pagefile 生效证据；演练报告落盘 | Owner 门位 |
| 7 | W3_retirement.md 登记面一致性待裁项（原文显式挂起、首次入卡）：归档正文停在"待 Owner 退役"字样而实质已终局（裁定 #336 + e4df828ddc + #ARCH-326 resolved + b6 终局段）——请 Max/Owner 定：维持"不回改归档正文"惯例、需要时另立在册说明 | docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout/W3_retirement.md | 裁定号登记或明示放弃；不回改归档正文 | Max/Owner 裁定 |

已死子项（勿再做）：R1 复审全套（本次调查即复核结论）、D1、D2 三口径决策、D4。

## 5. 与其他任务卡的关系

- TC-03：D1=N-5 同题双方销账；stash@{0} 归本卡域，TC-03/TC-08 勿动。
- TC-08：剩余工作 2/4/5 与其高度同池（执行指针、registry 回写），建议同批走。
- TC-11：stash@{0} 是 WO-13续 salvage 物，TC-11 施工若需碰 externalize 域必须先协调。
- TC-06：S18 族裁定（#333）已闭合，TC-06 引用裁定号时注意与本卡 D4 区分。
- TC-09：design_memos 归置所有权在丙线 WO-14（#384），本卡的 D3 蓝图晋升与其无冲突但同在 docs/03_modules 域，避让在途件。

## 6. 风险与避让红线

1. stash@{0} 是混装件（含 capability_cards/TDM/error_code_registry 等他线改动）——绝不可整包 pop/apply，只许 git stash show -p 摘单文件补丁重放。
2. commit_belt_daemon.py 真路径已迁移，按旧路径施工必失败。
3. #ARCH-324 回写若被别的班先行执行，步骤 2 案卷前提要同步更新。
4. R1 的 orphans=0/64 绿两条维持 09-18 数值未独立复测（调查纪律禁跑），执行时如需可复跑 reconciler --json。
5. 主区脏条目 ~780：写操作限 own-diff，提交后 git log -1 --name-only 核归属。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；生成器再生成窗内禁并发跑其他生成器；改注册表必 safe_write_text CAS + 进程外重解析核实。
