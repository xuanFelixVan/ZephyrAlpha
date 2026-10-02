---
ttl: task_bound
session: st-ffchief-20261002
date: 2026-10-02
title: 分支清零+接管显化基建作战书
completes_when: 分支清零执行完毕+接管台账三件套落地+验收两轮零
---

# 分支清零+接管显化基建 作战书（st-ffchief-20261002）

> Owner 睡前令（2026-10-02）：①dev 之外分支全面清零——价值流判断后归位，"没有任何分支"（必要功能分支除外）；②本战役处理过的所有问题类别做治本基建——核心=**显化机制**：AI 施工队中途死亡/忘清理时，下一个 AI 立刻看到受影响的暂存区/worktree/模块开发情况并马上处理，永不堆积。今晚另有五个施工大队并发——冲突纪律：不动他人成果与临时文件，同文件冲突=登记让行，他队完成=交叉验证。

## 0. 总包与授权

- 总包：st-ffchief-20261001（延续会话）。裁定权：Owner 总授自裁（架构师第一性原理/长远战略/100% AI 开发）。
- 红线不变：gateway 落地、claim 纪律、hot 册 safe_write、禁裸 git 写（worktree remove/branch -d 走裁定通道并全档案化）。

## 1. 战役一：分支清零（153 本地 + 3 远端）

价值流判据（第一性原理：分支只是指针，commit 已入 dev 的分支零信息价值）：
1. **已并入 dev**（merge-base 判 is-ancestor）→ 直删（commit 活在 dev 历史里）。
2. **未并入但有独特 commit** → `git tag archive/<原名> <sha>` 归档指针后删分支（零丢失、可随时复活、名册进台账）。
3. **未并入且无独特 commit/指向已退役 worktree 的孤儿** → 直删。
4. **活跃会话在用分支**（st-c10-*/st-c12-*/等 1h 活会话族）→ 保留不动，登记观察。
5. 终态：仅剩 dev + 活跃会话功能分支；全量台账 `branches_ledger.md`（每分支：判定/去向/归档 tag 名）。

## 2. 战役二：问题治本清单 + 接管显化基建

### 2.1 问题类别清单（本战役实修 → 治本映射，Owner 点名交付）
由 LEDGER 全账提炼十五类：死袋无主/热册并发覆盖/门超时误杀/守护堆积/幻影删除/worktree 堆积/暂存区孤儿/claim 泄漏/ghost 心跳/翻译缺词/token 缺位/R5 目录命名/DRY 违规家族/文档断链/数据产物混 git。每类：本战役实证 → 治本件（已做/本次新增）→ 防复发机制。

### 2.2 接管显化基建（Owner 核心构想落地）
**问题**：会话中途死亡 → 暂存区/worktree/claim/死袋全成无主黑箱；下一个 AI 要重新考古。
**治本=接管台账（Takeover Ledger）+ 三层显化**：
1. **L1 资源清单显化**：会话注册时即登记资源清单（worktree/staging/claims/bags）——session_worktree 启动钩子写入。
2. **L2 死亡显化**：会话判死时（registry salvage 钩子）自动生成接管条目：`{sid, 死亡证据, 资源清单, 影响模块（按文件路径→域映射）, 处方}` → `.runtime/takeover_ledger.jsonl` + 终态迁移 `.runtime/takeover/open/`→处理完 `resolved/`。
3. **L3 门禁显化**：新 gate TAKEOVER-PENDING——commit 触碰 open 接管条目内的文件 → 阻断并打印接管处方（下一个 AI 想绕都绕不过，必须先按清单接管）。
**实现**：`scripts/governance/session_takeover_ledger.py`（ledger 读写+死亡扫描）+ registry salvage 钩子接线 + gate 注册 + 测试 + 词条/token/翻译册登记 + 文档规约（施工册 frontmatter 增 `resources:` 字段惯例）。

## 3. 车道与顺序

- **B1 分支挖矿+清零**（一车道到底：census→矩阵→执行→台账）
- **T1 接管基建**（设计→实现→测试→落地）
- **T2 问题清单册**（总包亲理，LEDGER 提炼）
- 冲突纪律：T1 动 session_concurrency/session_worktree/gate 注册面——开工前查活跃施工队文件面（claim+git status 双查）；B1 只动 refs 零文件冲突。

## 4. 验收

1. 分支：dev 外仅剩活跃会话功能分支，台账 153/153 全判定。
2. 基建：接管台账三件套落地+测试绿+文档规约入册。
3. 问题清单册：15 类全映射。
4. 循环检查两轮零 + 红蓝（含"模拟会话死亡→台账条目生成→gate 拦截→按处方接管→resolved"全链红蓝）。
5. gateway 落地+临时文件清理+终报。


## 5. 终态（2026-10-02 05:4x 终验收）

- **战役一分支清零：153→15**（删 140=已并入 116+tag 归档 24；归档 tag 25 个零丢失；余 15=dev+序列器/活跃会话/今晚新产出功能分支，二轮观察=4 件 worktree 锁保护件随锁解清）
- **战役二治本基建：T1 三件套全落 HEAD**（session_takeover_ledger.py+TAKEOVER-PENDING 门+salvage 钩子；10 测+邻接 70 绿；红蓝=伪造会话注入被 V5 护栏正确拒绝）；T2 十五类治本清单册成
- 队列 0/0；幻影删除 0；接管台账 --list 实战产出首条真实信号（c10-f56ch 静默显化）
- 裁定：本战役 CR 沿用 circulation_chief 序（#461~#476 已并册），分支清零与接管基建裁定补录待下批


## 6. Owner 追加令执行：末 15 条逐条手工判定（10-02 晨）

四维全scan 后判定：13 条已并入 dev 零独特 commit（价值全在主干）；唯一未并入=chief4 的 16 行，核验=兄弟车道 chief6 已以更优注释落地同内容（_MANUAL_DERIVED_TOTAL_PAIRS+validator CHECKS 双处在案）→判 superseded。

执行（含 worktree 前置清退 9 棵，脏面全档案化 campaign_trash/worktree_salvage/）：
- 直删 12：5 条死/完节会话分支（commitfix/mapcensus/ffchief-20261001/chief7/backup-cold——全部已并入）+3 条 worktree 占用已并入分支（c7-autofix/chief7w）+chief4（tag 已在）+chief3-baseline detached 树
- 保留 8：dev｜serializer×5（belt 落地必要功能）｜session/st-chief7-20260928（收官自动机在飞，自删后二轮清）｜session/st-ffchief-20261002（现役）
- 旧会话 st-ffchief-20261001 守护停+注册除名（全部落地，会话干净关闭）


## 7. 混沌演训终判（Owner 三问实弹作答，10-02 晨）

- R1 并发：10 车道并发注册→claim→写→gateway enqueue，全落零丢失 ✓
- R2 死亡：5 车道处死模拟——慢死亡被接管台账全逮（c10 五车道 13 条死袋处方实出）；瞬时死亡揪出孤儿侦测缺口→_scan_orphan_resources 9b3359eccf 当日补齐 ✓
- R3 门禁：TAKEOVER-PENDING/幽灵闸/C-2 预检/V5 护栏全数实弹拦截在案 ✓
- R4 闭环：接管→裁定→resolve→落地全链通 ✓
- R5 清算：--sweep-absorbed 首跑 aged 708 显化/三分流自洽 ✓
- R6 基线：幻影 0/队列排空/分支 8/无主资源 0 ✓
- 红队注入（伪造会话）被 V5 护栏正确拒绝=蓝队胜 ✓
