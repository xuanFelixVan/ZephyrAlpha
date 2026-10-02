---
ttl: task_bound
session: st-ffchief-20261002
date: 2026-10-02
title: 十五类问题治本清单册
completes_when: 十五类全映射+接管显化基建落地
---

# 问题类别治本清单册（st-ffchief-20261002 · T2）

> Owner 令：把本战役处理过的问题罗列成册，深度挖矿做治本，未来不再出现。每类三段：本战役实证 → 已做治本 → 防复发机制（含内收原则判断）。来源账本=docs/_working/circulation_chief/LEDGER.md 全账。

## 判总纲（内收三问）

每类问题先问：①这问题的**产生机制**是什么（不是谁干的）？②现有机制缺了哪一环？③补这一环是**加新规则**还是**修旧环节**？——凡能修旧环节的绝不加新规则（内收）。下表「防复发」列只写净增动作。

## 十五类问题治本映射

| # | 问题类 | 本战役实证 | 已做治本 | 防复发机制 |
|---|---|---|---|---|
| 1 | **死袋无主**（会话死了袋还在队里循环） | 4 个昨夜死袋+ghost 闸连环死 | 重投挂活会话 sid（CR-1）；死袋逐袋手术救活 6 族 | **T1 接管台账**：会话判死自动生成接管条目（含在途袋），gate 拦截相关文件提交直到接管 |
| 2 | **ghost 心跳伪造/僵尸守护** | 3 只心跳守护给死对话续命+keeper 伪造 activity | 实杀 6 守护+清 129 死 pid 文件；V5 register() 频率护栏（79eeda72） | 护栏在册常驻；mark_logical 核验待 Owner（已登记） |
| 3 | **热册并发覆盖**（module_translation/capability 两册被多袋争抢蒸发条目） | 袋快照丢册两轮死+CCR 蒸发闸两次 | 携册直投配方（袋内必含注册册）；serializer 三向合并吸收 | 配方已入手册；**T1 接管条目含热册基线指纹**，接管者一眼看到基线漂移 |
| 4 | **落地门超时误杀合法长链** | k4 池门禁 1571s>900s 上限→全队退避风暴 | **CR-16**：900→2400（9503d222） | 阈值已抬；w0 landing_phase_stats 常驻审计可观测 |
| 5 | **守护进程堆积**（看门 CIM 探测竞态 6-8 只并存） | 两波堆积实证 | 杀净重拉配方 | 看门探测加固=遗留待办（已登记 Owner 项） |
| 6 | **共享索引幻影删除** | 44 条 staged-D 全盘面在盘 | restore --staged 复位（00:1x） | **S8 新增红蓝向量**常驻；接管台账 L3 gate 会拦带幻影面的提交 |
| 7 | **worktree 堆积**（200 个/57 锁，多为死会话残区） | 退役 180 个，抢救 24484 blob 档案化 | 退役批+档案化配方（宁留勿删的档案化变体） | **T1 接管台账含 worktree 资源**：死会话 worktree 自动入 open 条目，gate 拦截+处方指引；本战役后新 worktree 全部经 session_worktree 正门（自带生命周期） |
| 8 | **暂存区孤儿**（会话死了 staging 无人认领） | 多会话 staging 目录考古 | 考古方法论（staging 母本对拍） | **T1 接管条目含 staging 清单**；L1 显化=启动即登记 |
| 9 | **claim 泄漏**（死会话 held_files 永锁） | 8+10 条孤儿 claim 释放；27 held_files 随僵尸清杀 | release_files 手术+V4 清扫 | registry salvage 判死时 **T1 钩子自动写台账**，claims 进条目可见 |
| 10 | **翻译缺词/token 缺位** | TRANSLATION-COVERAGE/CREATE-GUARD 死因 30+ 次 | add_module_translation+batch_creation_tokens 正道配方（ASCII slug/携册直投） | 配方在 commit_navigation_playbook（机生）；gate 拦截即给出修复命令（已验证） |
| 11 | **R5 目录命名违规** | 战役目录数字后缀两袋连死 | 改名 circulation_chief（CR-13） | gate 拦截+命名规约在 DCR 册 |
| 12 | **门禁触发面超宽/死模式** | 15 台超宽+4 台死模式（9169 文件 always-fire） | 触发面收窄+死模式删除（0e97a567） | 生成器真源已修，对账报表常驻 |
| 13 | **文档断链**（ALGO_FLOW 锚/index 死引用） | 0114 四断锚+L27 _audit 断链 | external 锚单载体+收标记配方；死条目清除（5aa2b07cb0） | ALGO-FLOW-LINK/DOC-REF 门常驻拦截 |
| 14 | **数据产物混 git** | grid 65 件+metaq .rda R5 冲突 | CR-7 政策：小语义件入库/二进制留盘 | gitignore 政策件（CR-7 批随 S9 落）+gate R5 侧防 |
| 15 | **分支堆积**（153 条本地分支，多为已并入/已退役会话） | 本次战役一（B1 车道执行中） | 价值流三判据：并入删/独特 tag 归档删/孤儿删 | 归档 tag 惯例（archive/ 前缀）+台账；后续会话收尾 SOP 增「分支处置」步骤 |

## 接管显化基建（Owner 构想 → T1 落地中）

**问题本质**：以上 1/7/8/9 四类的共同根因=**会话死亡时资源状态不显化**——暂存区/worktree/claim/死袋散落各处，下一个 AI 必须重新考古。

**治本结构（三层显化，T1 车道施工中）**：
- L1 资源清单显化：会话启动即登记资源清单（worktree/staging/claims/bags）
- L2 死亡显化：判死钩子自动生成接管条目 `.runtime/takeover_ledger.jsonl`——含影响模块映射（文件路径→域）与处置处方
- L3 门禁显化：TAKEOVER-PENDING gate——触碰 open 条目文件的提交被拦，错误消息即接管处方

**设计哲学（内收）**：不新增流程仪式——资源清单全部**复用既有信号**（registry held_files/worktree 目录/staging 目录/队列袋匹配），只加一个「死亡时把散落信号聚合成一张纸」的钩子+一个「动他之前先看这张纸」的门。下一个 AI 的体验：撞 gate → 读处方 → 按 --resolve 接管 → 继续施工。零考古。

## 遗留观察项（不属本次十五类，已登记）

- 守护看门 CIM 探测加固（Owner 项）
- mark_logical 授予核验（W-29 扩权面）
- config 内存天花板/GOV-DOC-018 拆簇/.rda 契约/估值 v2/F87 收敛/F72 cadence/migration 退役/计数漂移（Owner 门位十项，见 circulation_chief/99_final_report.md §七）


## 第 16 类：死信无预防+无及时清算（Owner 追问补录，机制已建）

- **实证**：dead 池 1192→1223 条持续膨胀，仅靠人工手术消化；无老化显化、无吸收自动销账、无常驻清算。
- **已做治本**：`session_takeover_ledger.py --sweep-absorbed`（本机制）：三分流=①HEAD 吸收的死信自动销账（档案化 dead_archive/absorbed/，零删除）②超 48h 未吸收自动升级清单（处方已在 dead_reason，供维护班/AI 优先处理）③新鲜保留等属主/处方循环。首跑实证：aged 696 升级显化/absorbed 0/fresh 523 保留，账本 sweep_log.jsonl。
- **预防腿（已在位，此处收口登记）**：C-2 入队预检（注定死的重投当场拒收+处方）、dead_reason 内嵌修复命令（拦截即教学）、TAKEOVER-PENDING 门（未接管资源面禁提交）、接管台账（死会话资源显化）。
- **防复发**：sweep 幂等可重跑；仓库锚定设计（判定只依赖 git HEAD+袋内 sha256）=任何平台/编译器/agent 施工流跑同一命令同结果，施工本身不产生幻觉漂移；建议会话收尾 SOP 增一步 `--sweep-absorbed`（ AI 收班顺手清自己产生的死信）。
