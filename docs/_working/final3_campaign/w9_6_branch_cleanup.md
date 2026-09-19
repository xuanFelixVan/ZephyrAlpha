---
ttl: task_bound
completes_when: W9-6 分支清零批全部批次落地并经⑤终态预演复核后归档（最迟 2026-10-19）
title: W9-6 分支清零批清单与终裁材料（①尸体分支/②工棚收尾/③裁定尾巴/④远端/⑤终态预演）
---

# W9-6 分支清零批（st-final3-20260919 | 2026-09-19）

> 口径声明：全部分支/工棚状态为 2026-09-19 本会话实测（`git branch --merged dev`、`git worktree list`、
> `git -C <棚> status --porcelain` 逐棚计数、SessionRegistry 活性探针），非文档转抄。
> 会话活性判定：`SessionRegistry(D:\ZephyrAlpha)`（.runtime/session_registry.json）仅 2 条存活：
> st-final3-20260919（本会话）、worker-9cf3a273-27988（pid 27988 存活，公共 worker，未触碰）。
> 其余全部会话（含 st-auditdoc-v4 / st-ruledisp / 各 bizmine / 各工棚所属会话）均不在册=已死。

## 1. ①尸体分支删除清单（基线=git branch --merged dev 共 46 条非 dev 分支）

> 删除依据：全部 `git branch -d`（仅已 merged into dev 者）；带"（-D）"标注者为 ②收尾令明确的
> 未并入分支，删前未并入 commit 已留档于 §3。工棚占用分支先移除其死会话工棚（棚内 status 计数=0 才动）。

### 1.1 批A 直删（无工棚占用）——已执行 2026-09-19

| 分支名 | 最后 commit | 删除依据 |
|---|---|---|
| ai/st-consrep-20260916/cons-repaired | 54e33612a7 2026-09-16 | merged into dev，git branch -d 成功 |
| probe_icase | 9d853bc4af 2026-09-16 | merged into dev，git branch -d 成功 |
| session/st-consrep-20260916 | f4e31d822c 2026-09-16 | merged into dev，git branch -d 成功 |

### 1.2 批B 清棚后删（死会话工棚 status=0，先 `git worktree remove` 再 `git branch -d`）——已执行 2026-09-19（26 棚全 OK、26 支全删）

| 分支名 | 最后 commit | 工棚（status 计数） | 删除依据 |
|---|---|---|---|
| ai/st-nightcoord-20260918/nightcoord-ledger | 5f97f3d724 2026-09-18 | .worktrees/st-nightcoord-20260918 (0) | merged，棚净 |
| ai/st-f06combo-20260915/task-dsr-align-fix | bad2739d77 2026-09-16 | .worktrees/st-f06combo-20260915 (2) | merged；2 件"脏"经 `diff --ignore-cr-at-eol` 复核=纯 CRLF 幻影（真实差异 0），--force 移棚 |
| session/st-ailayer-20260917 | 40401379da 2026-09-18 | .aidrafts/st-ailayer-20260917 (0) | merged，棚净 |
| session/st-auditfix-20260916 | 50944b2a00 2026-09-16 | .aidrafts/st-auditfix-20260916 (0) | merged，棚净 |
| session/st-auditkey-20260916 | d0be0e8f1a 2026-09-16 | .aidrafts/st-auditkey-20260916 (0) | merged，棚净 |
| session/st-bizmine-algo-20260919 | 7f68805b98 2026-09-19 | .aidrafts/st-bizmine-algo-20260919 (0) | merged，棚净（registry 不在册=会话死） |
| session/st-bizmine-co-20260919 | e62dc28a29 2026-09-19 | .aidrafts/st-bizmine-co-20260919 (0) | merged，棚净 |
| session/st-bizmine-pat-20260919 | e8502ace7e 2026-09-19 | .aidrafts/st-bizmine-pat-20260919 (0) | merged，棚净 |
| session/st-bizmine-pb-20260919 | 77302b5ab2 2026-09-19 | .aidrafts/st-bizmine-pb-20260919 (0) | merged，棚净 |
| session/st-cohort-ledger-20260918 | 6b6f65c0eb 2026-09-18 | .aidrafts/st-cohort-ledger-20260918 (0) | merged，棚净 |
| session/st-crisis-drill-20260918 | 6b6f65c0eb 2026-09-18 | .aidrafts/st-crisis-drill-20260918 (0) | merged，棚净 |
| session/st-crisis-gate-20260918 | 6b6f65c0eb 2026-09-18 | .aidrafts/st-crisis-gate-20260918 (0) | merged，棚净 |
| session/st-dabanre-20260917 | c0f5cc47b8 2026-09-17 | .aidrafts/st-dabanre-20260917 (0) | merged，棚净 |
| session/st-dbgap-fix-20260916 | 57bec4f652 2026-09-16 | .aidrafts/st-dbgap-fix-20260916 (0) | merged，棚净 |
| session/st-govops-20260916 | f5cab615ec 2026-09-16 | .aidrafts/st-govops-20260916 (0) | merged，棚净 |
| session/st-igalpha-20260917 | e7c9622d62 2026-09-17 | .aidrafts/st-igalpha-20260917 (0) | merged，棚净 |
| session/st-maint-20260916 | 4d2c5af505 2026-09-17 | .aidrafts/st-maint-20260916 (0) | merged，棚净 |
| session/st-mineline-rh5e | f8aed2365e 2026-09-18 | .aidrafts/st-mineline-rh5e (0) | merged，棚净 |
| session/st-qalpha-20260916 | 0e6ae5c788 2026-09-16 | .aidrafts/st-qalpha-20260916 (0) | merged，棚净 |
| session/st-redblue-night-20260918 | 34fe6de1a5 2026-09-18 | .aidrafts/st-redblue-night-20260918 (0) | merged，棚净 |
| session/st-residual-20260917 | 6b6f65c0eb 2026-09-18 | .aidrafts/st-residual-20260917 (0) | merged，棚净 |
| session/st-resource-20260916 | 71a0a92316 2026-09-16 | .aidrafts/st-resource-20260916 (0) | merged，棚净 |
| session/st-sim-attrib-20260918 | 6b6f65c0eb 2026-09-18 | .aidrafts/st-sim-attrib-20260918 (0) | merged，棚净 |
| session/st-sopfix-20260918 | b3294b7c79 2026-09-18 | .aidrafts/st-sopfix-20260918 (0) | merged，棚净 |
| session/st-tdmbe-20260909 | 57bec4f652 2026-09-16 | .aidrafts/st-tdmbe-20260909 (0) | merged，棚净 |
| session/st-tickdrain-20260916 | 45f0f440e6 2026-09-17 | .aidrafts/st-tickdrain-20260916 (0) | merged，棚净 |

### 1.3 批C（②收尾删分支 + CF1 丢弃棚）——已执行 2026-09-19

| 分支名 | 最后 commit | 删除依据 |
|---|---|---|
| ai/st-auditdoc-v4-20260918/task-auditdoc-v4 | 13eaa45abf 2026-09-18 | ②收尾令；核心产出（audit_prompts v4 纯陈述清洗，6538→486 行）已实测在 dev（dev 486 行 vs 分支 485 行同源），-D 收尸 |
| ai/st-ruledisp-20260918/task-rule-disposition-sop | 18043e6020 2026-09-19 | ②收尾令；未并入 commit 留档 §3.3，工棚净（0）先移棚再 -D |
| ai/AI-NIGHT-CF1-001/task-night-cf1 | 23ada56a0d 2026-09-19 | merged；棚内 8 件"治本 CF1 F2-F6"改动经核已在 dev（`resolve_scan_dir` 已入主区 walk.py），备份 .runtime/tmp/cf1/backup/cf1_worktree_070248.patch，按令丢弃收棚 |

## 2. 保留与阻断清单（不删，逐条原因）

### 2.1 主动保留（3 条）

| 分支名 | 最后 commit | 保留原因 |
|---|---|---|
| master | d92ea66538 2026-09-08 | branch_strategy_policy.md §2.2/§3.1：master=dev 的 **永久 FF 镜像**，外部工具/CI 语义标记，删除违 Policy。现滞后 dev 11 天，建议按 DEBT-BRANCH-001 例行走 `git branch -f master dev`（留 Owner/例行通道，本批不动） |
| serializer/commit-queue | 9cf3a2739a 2026-09-19 | 提交队列 serializer 专用 worktree（.runtime/commit_queue/worktree，locked）在用，活基础设施 |
| session/st-final3-20260919 | 0d5d223749 2026-09-19 | 本会话在用（registry 存活 + .aidrafts 工棚在用） |

### 2.2 阻断：棚内未提交内容，按"勿强拆"令只登记不拆（13 条，归 Owner 处置）

| 分支名 | 最后 commit | 工棚 | 内容计数（porcelain 总数 / 真实差异） |
|---|---|---|---|
| ai/AI-NIGHT-A2-001/task-night-a2 | 6f450c9676 2026-09-19 | .worktrees/AI-NIGHT-A2-001 | 2 脏；真实差异 2 文件 +4/-4 |
| ai/AI-NIGHT-A7-001/task-night-a7 | 6f450c9676 2026-09-19 | .worktrees/AI-NIGHT-A7-001 | 6 脏；真实差异 6 文件 +49/-37 |
| ai/st-altdatamap-20260918/task-altdataline | 513d3ba0a6 2026-09-18 | .worktrees/st-altdatamap-20260918 | 7 脏；真实差异 7 文件 +86/-23 |
| ai/st-dabanapp-20260916/daban-lue-four-engine | 92f042a8f2 2026-09-16 | .worktrees/st-dabanapp-20260916 | 233 脏+2 未跟踪；真实差异 233 文件 +366/-288 |
| ai/st-datapack-20260918/datapack-d4 | 410c4c5c5b 2026-09-18 | .worktrees/st-datapack-20260918 | 7 脏+7 未跟踪；真实差异 +1554/-61（大头为新增件） |
| ai/st-ledgerp1-20260916/task-judgment-ledger-p1 | e9023f173d 2026-09-17 | .worktrees/st-ledgerp1-20260916 | 229 脏；真实差异 229 文件 +343/-511 |
| ai/st-ledgerp2a-20260916/task-judgment-ledger-p2a | dd274dbe59 2026-09-17 | .worktrees/st-ledgerp2a-20260916 | 1 未跟踪目录 docs/_working/pipeline-research/reports/ |
| ai/st-ledgerp2b-20260916/scenario-engine | a4cb77060a 2026-09-18 | .worktrees/st-ledgerp2b-20260916 | 178 脏+1 未跟踪；真实差异 +486/-3458 |
| ai/st-orchp3-20260916/daily-orchestrator | 51437bb1b9 2026-09-17 | .worktrees/st-orchp3-20260916 | 10 脏+1 未跟踪；真实差异 +107/-267 |
| ai/st-sowner001-20260916/s-owner-001-300etf-band-t | 733f79cb9d 2026-09-17 | .worktrees/st-sowner001-20260916 | 236 脏；真实差异 223 文件 +274/-285（分支 tip 自述"分支合并待主区净窗"，裁定#293 verdict=FAIL） |
| session/st-chinfra-20260914 | 6c26071385 2026-09-15 | .aidrafts/st-chinfra-20260914 | 8017 脏；ignore-cr-at-eol 后仍 8017 文件 -1909366 行（真实巨量差异，非 CRLF 幻影） |
| session/st-orchbp-20260916 | a441495a0f 2026-09-17 | .aidrafts/st-orchbp-20260916 | 2 脏；真实差异 2 文件 +18/-18 |
| session/st-regcal-20260917 | a2ab567992 2026-09-17 | .aidrafts/st-regcal-20260917 | 2 脏；真实差异 2 文件 +7/-7 |

> 注：阻断分支均 merged into dev（除 sowner001 自述待合并外其分支 tip 亦已在 dev 祖先链），
> 分支本体零风险；阻断仅在"棚内容可能含未归档独有产出"。13 棚处置建议：Owner 逐棚判读
> （真实差异小者可人工 diff 后弃，ledgerp2a 的 reports/ 与 datapack 的 +1554 行新增件建议优先判读）。

## 3. ②工棚分支收尾三连记录（st-auditdoc-v4-20260918 / st-ruledisp-20260918）

### 3.1 st-auditdoc-v4-20260918

1. 核 PID：heartbeat.jsonl 末条 `2026-09-18T12:49:42+00:00 pid=7240 status=alive`，此后断流；
   实测 `is_pid_alive(7240)=False` → 无进程可 terminate。
2. SessionRegistry.unregister：registry 无 `st-auditdoc-v4-20260918` 条目 → 跳过（会话已死早已出册）。
3. 工棚：`git worktree list` 无此棚（此前已移除）→ 无棚可收。
4. 分支 `ai/st-auditdoc-v4-20260918/task-auditdoc-v4`：批C 已 -D（was 13eaa45abf；产出已实测在 dev，见 §3.3 留档）。
5. staging 遗留：`.runtime/sessions/st-auditdoc-v4-20260918/staging/` 有 6+ 件交付件
   （PHASE1_HANDOVER.md、referee_roster*、rules_dangling_resolution.json、rules_enforcement_census.json），
   TTL（24h）已过。**本批不动**，promote/弃置归 Owner。

### 3.2 st-ruledisp-20260918

1. 核 PID：heartbeat.jsonl 末条 `2026-09-18T15:00:17+00:00 pid=22540 status=exited (idle timeout 1810s)`
   → 进程已自退，无可 terminate。
2. SessionRegistry.unregister：registry 无条目 → 跳过。
3. 工棚 `.worktrees/st-ruledisp-20260918`：status 计数=0（净）→ 批C `git worktree remove` 成功。
4. 分支 `ai/st-ruledisp-20260918/task-rule-disposition-sop`：批C 已 -D（was 18043e6020）。
5. staging 遗留：`.runtime/sessions/st-ruledisp-20260918/staging/dossiers/` 有规则处置卷宗若干
   （branch_strategy_policy 逐条 dossiers 等），TTL 已过。**本批不动**，归 Owner。

### 3.3 删除前未并入 dev 的 commit 留档（-D 后仅 reflog 可达，GC 前可捞）

- auditdoc 分支：`13eaa45abf`、`15022bef7a`（audit_prompts v4 治本两连）——**经实测其产出已在 dev**
  （`git show dev:.../audit_prompts_20_ai.md` = 486 行 ≈ 分支 485 行），删除无实质损失。
- ruledisp 分支（docs/方案类为主）：`18043e6020`（D-18 恒真假绿条款+WP17 立项）、`68b8619e37`、
  `fde7cc19e8`、`57109341cd`（D-13~D-16 裁定批）、`5aa9568aae`（门禁身份与触发台账方案）、
  `f00a0231aa`（rule_disposition_policy 六道闸）、`c5bba14a7c`（规则与审计一条龙施工总方案）
  及若干 reconciler/integrity chore；三dot diff=8 文件 +222/-62。
  若 Owner 后续需要，`git reflog` / `git log 18043e6020` 可达。

## 4. ③裁定尾巴终裁材料（只出材料不执行，归 Owner 签字册）

### 4.1 ai/st-sowner002-20260916/s-owner-002-regime-switcher（tip 5338f109bf，--no-merged，棚 .worktrees/st-sowner002-20260916 在用）

**内容摘要**（4 commits，diff vs merge-base = 21 文件 +2404/-102）：
S-OWNER-002 Owner 域切换器全链。4376f35627 E4 冻结文档预注册（验收线/窗口/映射/成本/红蓝全写死）
→ fa5c8febaf 切换器框架验证出证 **verdict=FAIL（H 不成立）**+裁定#304 原子登记 → 89dd33dd8a（=任务书
"cp3 件"）切换器模块实现+双代理包+E4 考试器+24 用例测试（红蓝四场景全绿）→ 5338f109bf 收尾交接包
（cherry-pick 合并指引+生成器派生件，自述"分支待合并"）。核心件：
`src/zephyr/.../strategy_factory/owner_regime_switcher/{engine 187 行, exam 205, packages 74, switcher 227}` +
`tests/strategy_factory/test_s_owner_002_{engine,redblue,switcher}.py` 共 484 行。

**并入案**：利=完整测试覆盖（24 用例红蓝全绿）的工厂件入主区、交接包自带 cherry-pick 指引（落地成本低）、
生成器派生件随包齐活；弊=E4 框架验证 verdict=FAIL（H 不成立）——验证未过的策略件并入有"假资产"风险；
在册裁定#309 关联款载明"首版接入包=空集（pending-owner-adoption）"，采纳门位未开。
**废弃案**：利=不引入 FAIL 验证件、账面内收；弊=2404 行含测试实现 GC 后不可恢复，Owner 若后续采纳需重做。
**建议**：维持现行"留分支"裁定不变，待 Owner 对交接包（5338f109bf）签字：采纳→按其自带 cherry-pick 指引
并入；不采纳→`git diff dev...` 打补丁归档 docs/_working/ 后删支。**本批未执行任何动作。**

### 4.2 ai/st-tv2terrain-20260917/BT-P1-032（tip b7d8bafdde，--no-merged，棚 .worktrees/st-tv2terrain-20260917 在用）

**内容摘要**（单 commit）：做T v2 数据地形**只读勘测报告** `docs/_working/factory/t_v2/2026-09-17-data-terrain-survey.md`
（192 行：标的×级别覆盖矩阵/聚合链结论/缺口三态清单/涨跌家数断供定位）+ capability_canonical_file_registry.yaml
+4 行登记。背景：做T v2 战役已被**裁定#331**（原#304 撞号改号，2026-09-17，"立项依据无证+累计 N 口径数学
不可过+毛边际实证为负"）砍，复活路径=单假设窄考试先行；本报告=战役封存（T#304）前最后产出。

**并入案**：利=192 行勘测是"单假设窄考试"复活路径的直接输入，知识价值独立于战役存亡；纯文档单 commit，
cherry-pick 成本极低；弊=registry yaml +4 行 hunk 与主区现势易冲突（该表为高频登记通道写入面），不宜整
commit 并入。**废弃案**：利=战役已砍不留尾巴；弊=勘测知识仅 reflog 可达，复活需重勘（成本=一次只读普查）。
**建议**：Owner 签字后**单摘报告文件**copy 落 docs/_working/factory/t_v2/，registry 行不走 cherry-pick、
按现行登记通道补录；随后删支。**本批未执行任何动作。**

## 5. ④远端分支清单（只登记，禁 push 禁删远端——本批零远端操作）

| 远端 ref | 备注 |
|---|---|
| origin/HEAD -> origin/dev | 指针 |
| origin/dev | 远端主分支 |
| origin/master | 远端 master（与本地 master 同为镜像语义，处置随 §2.1 归 Owner） |
| origin/backup/pre-rebase-msgfix-8ce48cf0 | 历史备份分支（rebase 前快照） |

> 漂移项：branch_strategy_policy.md §1.1 自述"纯本地仓库（无 remote）"与实况（origin 存在且 4 ref）不符，
> 属 Policy 漂移，留 Owner 认领修订。任务书"远端 4 条"按含 HEAD 指针口径吻合。

## 6. ⑤终态预演（2026-09-19 批C 后实测）

**git branch --no-merged dev**（应只剩 2 条裁定尾巴——实测吻合）：

```
+ ai/st-sowner002-20260916/s-owner-002-regime-switcher
+ ai/st-tv2terrain-20260917/BT-P1-032
```

**git worktree list**（主仓 + 队列 worktree + 本会话棚 + 13 内容阻断棚 + 2 裁定尾巴棚 = 18 项）：

```
D:/ZephyrAlpha                                      fed3c9561a [dev]
D:/ZephyrAlpha/.aidrafts/st-chinfra-20260914        6c26071385 [session/st-chinfra-20260914]
D:/ZephyrAlpha/.aidrafts/st-final3-20260919         0d5d223749 [session/st-final3-20260919]
D:/ZephyrAlpha/.aidrafts/st-orchbp-20260916         a441495a0f [session/st-orchbp-20260916]
D:/ZephyrAlpha/.aidrafts/st-regcal-20260917         a2ab567992 [session/st-regcal-20260917]
D:/ZephyrAlpha/.runtime/commit_queue/worktree       fed3c9561a [serializer/commit-queue] locked
D:/ZephyrAlpha/.worktrees/AI-NIGHT-A2-001           6f450c9676 [ai/AI-NIGHT-A2-001/task-night-a2]
D:/ZephyrAlpha/.worktrees/AI-NIGHT-A7-001           6f450c9676 [ai/AI-NIGHT-A7-001/task-night-a7]
D:/ZephyrAlpha/.worktrees/st-altdatamap-20260918    513d3ba0a6 [ai/st-altdatamap-20260918/task-altdataline]
D:/ZephyrAlpha/.worktrees/st-dabanapp-20260916      92f042a8f2 [ai/st-dabanapp-20260916/daban-lue-four-engine]
D:/ZephyrAlpha/.worktrees/st-datapack-20260918      410c4c5c5b [ai/st-datapack-20260918/datapack-d4]
D:/ZephyrAlpha/.worktrees/st-ledgerp1-20260916      e9023f173d [ai/st-ledgerp1-20260916/task-judgment-ledger-p1]
D:/ZephyrAlpha/.worktrees/st-ledgerp2a-20260916     dd274dbe59 [ai/st-ledgerp2a-20260916/task-judgment-ledger-p2a]
D:/ZephyrAlpha/.worktrees/st-ledgerp2b-20260916     a4cb77060a [ai/st-ledgerp2b-20260916/scenario-engine]
D:/ZephyrAlpha/.worktrees/st-orchp3-20260916        51437bb1b9 [ai/st-orchp3-20260916/daily-orchestrator]
D:/ZephyrAlpha/.worktrees/st-sowner001-20260916     733f79cb9d [ai/st-sowner001-20260916/s-owner-001-300etf-band-t]
D:/ZephyrAlpha/.worktrees/st-sowner002-20260916     5338f109bf [ai/st-sowner002-20260916/s-owner-002-regime-switcher]
D:/ZephyrAlpha/.worktrees/st-tv2terrain-20260917    b7d8bafdde [ai/st-tv2terrain-20260917/BT-P1-032]
```

**收尾账**：分支 46 条非 dev merged 基线 → 已删 32（3 直删+26 清棚+3 批C）→ 剩 14 条 merged
（13 内容阻断+master 留+serializer 留+本会话留，见 §2）+ 2 条未并入裁定尾巴（§4）。

## 7. 执行批次索引

- 批A commit：fed3c9561a —— 3 直删 + 本清单建档 + creation_token（git log -1 --name-only 已核归属=仅本会话 2 件）
- 批B commit：q-20260919-st-final3-20260919-0069 —— 26 清棚删支（26 工棚 remove 全 OK，26 分支 -d 全成功；入队一度被 REGISTRY-MASS-DELETION 假红硬拦，根因=共享暂存区本文件 stale 条目幻影净删，他方会话刷新索引后同命令复跑入队）
- 批C commit：本提交 —— ②收尾三连（auditdoc/ruledisp）+ CF1 丢弃棚（备份 .runtime/tmp/cf1/backup/ 保留）
- 批D commit：本提交（与批C 同批收口）—— ③材料 + ④远端清单 + ⑤终态预演
