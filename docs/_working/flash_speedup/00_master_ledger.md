---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 提交链提速战役——总簿（环节全景骨架 + 战役批次志）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: active
---

# Flash 提交链提速战役·总簿（24 笔/h → 100+）

> **战役定性（Owner 令 2026-09-18）**：把 Git 提交链从 24 笔/小时提速到 100+。P2 已实证
> **24/h 是门禁常数不是锁常数**（10 worker 870/h → 20 worker 540/h、饿死 45%），故次序=
> **先修门禁（F3）再谈通道（F2）**；时间不够砍 F2 保 F3。
> **真源四件**：`docs/_working/kimi_audit/S18_提交链路根因表.md`（R-01~R-12）｜
> `S18_Flash施工包判据.md`（F1-F4 机读判据）｜`redblue_git/p2_git_chain_stress_closeout.md`（定序+本机红线）｜
> `adjudications/S18-R1~R4`（四张裁定书，均待 Owner 签）。
> **授权边界**：F1/F3/F4/F5 + F2 前置件=免签施工；F2 通道数本身、F5 白名单净增、S18-R1~R4=Owner 门位（只提案不自签）。
> **本机红线**：压测 worker ≤20，禁跑 50+ 档（P2 三度压死宿主，50/100 档正式关闭）。
> **并发纪律**：altdata 会话本机并发——改前 `lock_files.py acquire`、毕后 release；子代理禁 commit，主会话统一走 GitCommitGateway（一战场一批）；热文件 `safe_write_text`。

## 1. 环节全景骨架（施工包×状态×证据）

| 包 | 名称 | 授权 | 真源判据 | 依赖 | 状态 | 证据 commit | 子簿 |
|---|---|---|---|---|---|---|---|
| F1 | 衍生提交并入原子化 | 免签先干 | R-01 / S18-R2 / 判据书 F1 | — | ⬜ 施工中 | — | `F1_derived_commit_merge/DESIGN.md` |
| F4 | 生成器并发化 | 免签 | R-08 / 判据书 F4 | 与 F1 同文件需协调 | ⬜ 待工 | — | `F4_generator_concurrency/DESIGN.md` |
| F3 | 头部门禁 diff 化 | 免签（通道类前置） | R-03 / S18-R3② / 判据书 F3 | 需实测耗时榜定白名单 | ⬜ 待工 | — | `F3_head_gate_diff/DESIGN.md` |
| F5 | DIRECTORY-CONTRACT 摩擦前置化 | 免签（白名单净增=Owner） | A2 堵点本 16 次阻断 | — | ⬜ 待工 | — | `F5_dc_preflight/DESIGN.md` |
| F6 | 堵点本全量排查修复 | 免签 | 三本全量 4325 行 | 先 F1 后 F6 | ⬜ 待工 | — | `F6_bottleneck/DESIGN.md` + `lane_reports/F6_堵点总账.md` |
| F2 | 前置件（lease 续租+双通道压测+热文件单通道闸） | 免签部分（通道数=Owner 签 S18-R3） | R-02/R-04 / S18-R3 | 时间不够可砍 | ⬜ 待工 | — | `F2_lease_prereq/DESIGN.md` |
| H | 重建 harness + 改写 S18 判据书悬空验收行 | 免签 | P2 收官报告 §四 | F2 验收依赖 | ⬜ 待工 | — | （并入 F2 子簿） |
| R | 最终报告 + 两轮循环零问题核验 | — | 通宵 SOP §6/§9 | 全部完成后 | ⬜ 待工 | — | `90_report.md` |

## 2. 施工调度（线内先挖后干、线间并行流水）

执行序（尊重依赖）：**F1 → F4 →〔批量派分析子代理：F6 聚合 / F3 实测榜 / F5 DC 取证〕→ F3 → F5 → F6 → F2 前置 → H → R**。
- F1/F4=主会话自挖自建（地基活，付费档级别审慎，错了很久才暴露且伤全仓）。
- F6 聚合（4325 行账本）/F3 实测榜/F5 DC 取证=读密集分析，派子代理并发（有效并发 2-3，波次派发），主会话收口施工。
- 每包：挖矿（读透代码+测试）→ 子簿（六向台账+挖矿日志+自审闸三态）→ 挖干即施工 → 提交 → 写台账。

## 3. 战役批次志

| 批次 | 时间 | 内容 | 落地 commit | 备注 |
|---|---|---|---|---|
| B0 | 2026-09-18 | 冷启动+四真源读透+环节骨架封矿+lock  acquire（gateway/validate） | — | reaper 存活（killed=0），Python 3.12.8，锁区 CLEAN 起步 |

## 4. 挖后自审闸（总簿级，三态裁定）

- 量尺=终局全貌（夜间 50-100 车道并发，提交吞吐=全项目开发速度）。
- 三态裁定：**施工**（F1/F3/F4/F5/F6/F2 前置全部进入施工；F2 通道数/F5 白名单净增/S18-R1~R4=挂起待 Owner 签，只出提案）。
- 过度工程三问：①是否消灭人工参与？是（衍生税自动并入、门禁自动 diff 化、堵点自动归类）。②是否引入第二真源？否（复用 604f414846 差分口径、复用既有 batcher/register）。③现状规模小是否成为封矿理由？否（按终局 100 车道判，非按当前 24/h）。

## 5. 待裁定清单（起床报告汇总，目标=空）

| # | 案由 | 去向 | 五级分析摘要 |
|---|---|---|---|
| P-1 | F2 serializer 通道数 k=4 | Owner 签 S18-R3（裁定#320） | 通道数=Owner 定值（S18-R3 红队复验：lease 续租先行+热文件单通道+TTL 心跳续租）；本战役只落前置件，判据全绿后写"k=4 就绪待签" |
| P-2 | F5 DIRECTORY-CONTRACT 白名单净增 | Owner 门位 | 只出裁定书提案，不自签（白名单净增=注册表门位） |
| P-3 | S18-R1~R4 四张裁定书 | Owner 签 | 均 status=待 Owner 签；F1 免签先干（判据书授权"F1 任何时候可做"） |
