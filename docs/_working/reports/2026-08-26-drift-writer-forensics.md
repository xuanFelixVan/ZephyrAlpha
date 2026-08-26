---
ttl: task_bound
title: drift watchdog"未登记写入方"取证报告（并发覆写事故）
owner: ZephyrAlpha-Owner
language: zh
status: final
version: "1.0.0"
date: 2026-08-26
---

# drift watchdog"未登记写入方"取证报告（2026-08-26）

> 派单：Owner 2026-08-26（AI-DRIFT-001）——调查并处置 drift watchdog 告警的"未登记写入方"（并发覆写事故治本）。
> 原则遵守：全程只读取证，零写入他人 WIP；破坏性 git 命令零使用；结论全部可复现（证据锚点见 §7）。

---

## 1. 结论摘要（TL;DR）

**"未登记写入方"不是单一凶手，而是四类写入源的叠加，其中三类已定位并定性，一类因取证粒度不足无法唯一定凶（该能力缺口本身已登记）：**

| # | 写入源 | 定性 | 证据强度 | 处置 |
|---|--------|------|---------|------|
| W1 | post-commit reconciler 群（frontmatter 同步/EA 索引/manifest/目录注册表/资产索引重生）+ 长寿命 reconcile worker | **告警洪水与 handbook churn 的肇事方**；"设计如此"但未登记、无 claim、无 base 声明 | 实锤（3041 条告警+审计日志+worker 存活 78 分钟实证） | 见 §5 治本 R1；行为变更属 Owner 裁定（O1） |
| W2 | k3-digest 波次合并脚本（行级→块级 flip_wave 族）整文件 read-modify-write | **08-25 注册表 055bdd5a 回滚事故肇事方**；#ARCH-237 已登记 resolved | 实锤（hash 链+#ARCH-237 自供） | 已闭环；残余模式风险入 §5 R2 |
| W3 | commit_queue 落盘/着落路径（队列 worktree 旧基线 blob 回写） | 嫌疑排除为主：4 个 dead 队列项全部失败安全，landing 有 skipped_dirty 防护实证 | 强（死信解剖+sync 日志） | 残余风险建议入 §6 O5 |
| W4 | 秒级反复覆写 94号/00索引 的写入方（事故④及②③的工作区层表现） | **无法唯一定凶**：60s 看门狗粒度+无 PID 级写审计，事件在两次扫描间发生并恢复 | 证据缺口 | 登记为取证能力缺口（§6 O3） |

**AI-CRYPTO-001 已提交内容在 HEAD 完整无损（§4 三项验证全过）**。事故造成的丢失均发生在工作区层，且已被 AI-CRYPTO-001 当日补回（009 头部行、2.14.2 修订行均带"曾因并发覆写丢失，补回"注记）。

**本会话已落地处置**：①94号纳入 CAS 热文件清单（写前读新+commit base 新鲜度门禁覆盖，34/34 测试绿）；②本报告；③#ARCH-264 登记（因注册表文件含 W07 会话未提交 WIP，按纪律暂缓写入，条目全文见 §8）。

---

## 2. 告警取证（Step 1）

### 2.1 告警规模（governance.db reconcile_execution_log + watchdog 审计日志双源）

数据源：`.runtime/audit/worktree_drift_watchdog.jsonl`（17.7MB，全量逐事件）+ `data/databases/governance.db`。

最近 72h（2026-08-23T00:00Z 起）watchdog 审计统计：

| verdict | 数量 | 说明 |
|---------|------|------|
| alerted | 3041 | 未登记写入方实锤告警（含去重前重复） |
| grace_suppressed | 2871 | commit 后 600s 宽限窗内合法派生写 |
| healed | 592 | 漂移消解自愈 |

派单所述"24h 内 10 条 critical_warn"是网关 banner 去重后的可见子集；审计底账规模 300 倍于 banner 可见量——**告警疲劳本身是需要治理的问题**（§6 O6）。

### 2.2 隔离区快照状态

`.runtime/quarantine/` 当前为空目录——2026-08-25 16:55（UTC+8）批次告警的快照（drift_20260825T1655xx 等）**已被清除**，清除方未定位（retire_tmp_artifacts TTL 钩子范围不含 quarantine；疑云见 §6 O4）。**历史快照证据已灭失**，本报告以审计日志 hash 链+git 历史重建代替快照比对。

### 2.3 72h 提交时间线与活跃会话

08-23~08-26 提交全部由网关串行落盘。08-26 当日与受害文件相关的交错序列（UTC+8）：

- 12:53 `e30fd3e566` DIGEST P2 W01 注册表翻转
- 14:35 `0d101c3fe7` AI-CRYPTO-001 94号 v0.2.0 + CAND-CRYPTO-009
- 14:54 `4450cbdac8` DIGEST P2 W02 注册表翻转
- 15:28 `e97f383d18` K3-MINK8803 tdx_provider 单测（其 reconcile worker = 后文关键嫌疑进程）
- 15:39 `6a8c2a8c70` W03 / 16:34 `30efa897c8` W04
- 16:42 `100f84841f` AI-CRYPTO-001 94号 v1.0.0 + 索引 2.13.0
- 17:13 `8b878fc6e4` v1.1.0 / 17:34 `60024df662` v1.2.0 / 18:24 `ffd61dc7ec` v1.3.0
- 17:39 `91bc3de15b` W05 / 18:18 `1a87b444bd` reconciler batched auto-commit（6 reconcilers）/ 18:31 `f934046c1f` W06
- 会话心跳清单（审计日志 active_sessions）：AI-CRYPTO-001、k3-digest-p1r3/r4/r5/p2w04/w05/w06、K3-MINK8803、mink8803-20260826、bj-daily、k3-ddl-p0-0826、task:SRC-081、worker-\<commit\>-\<pid\> 系列（网关 reconcile worker）。

---

## 3. 写入方排查与定凶（Step 2/3）

### 3.1 W1：reconciler 群+长寿命 worker —— 告警洪水与 handbook churn 肇事方（实锤）

**机制链**：任何非空 commit → 网关 post-commit 轨 spawn `reconcile_worker`（worker-\<commit\>-\<pid\>）→ 顺序执行 27 个 reconciler → 其中派生写类（GATE-BLUEPRINT-FRONTMATTER-SYNC、EA index.yaml 重生、script_manifest 重生、rule_catalog/perception_index 同步、资产索引 bootstrap、panorama 同步）重写 60~200+ 个 tracked 派生文件 → batched auto-commit 落盘（如 `1a87b444bd`，单提交含 unified-asset-index.yaml 200577 行变更）。

**实证（handbook 五文件）**：`README.md`（HEAD `00c4839f` 恒定）、`01_overview.md`（HEAD `526d0e28` 恒定）、`07_dependencies.md`（HEAD `4e9e3529` 恒定）在 08-23 03:09Z 起被反复重写——每次告警 work hash 均不同、HEAD 纹丝不动，且活跃会话清一色为 worker-\*（reconcile worker）：08-23 03:09 worker-9508aba5 → 04:39 worker-fcc41099 → 06:00 worker-7a1ff92c → 09:17 worker-c0419609 → 09:54 AI-K3-GW-0823 → 17:13 worker-02e16167 → 22:32 worker-58d8613d → 08-24 01:17 worker-b86ed182 → 08-24 02:16/02:55 无活跃会话（worker 已退、心跳窗口外）。派单所列 2026-08-25 16:55 批次告警同属此模式。

**关键佐证（worker 长寿命）**：`worker-e97f383d-24796`（K3-MINK8803 会话 15:28 提交 e97f383d18 后 spawn）reconcile_status 显示 started 15:28:32、finished 16:46:54——**单个 worker 存活 78 分钟**，期间执行 27 个 reconciler、4 个 auto-commit 路径，其状态记录含 `drift watchdog: scanned=252 drifted=246 alerted=36` 与 `restored 6 auto-sync files; 235 non-auto-sync modified files detected`（GATE-WORKSPACE-HYGIENE 对 auto-sync 产物执行 `git restore`）。

**同时段 safe_write 审计**（`.runtime/audit/safe_write.jsonl`）：module_translation_registry.yaml 在 08-23~08-25 反复出现"4 个不同 PID 在 2~8 分钟内先后写入完全相同的目标内容（同 expected_base→同 after_sha256）"——多 worker 并发重算同一份派生内容整文件覆写，与 W1 机制完全吻合。

**定性**：这些写入是"设计如此"的派生重生，但它们 ①无 session claim（`.runtime/claim_snapshots/` 仅有历史 `_adopted` 文件，当前零活跃 claim）②不走 lock_files（当前零锁持有）③不声明写前 base → 正是告警字面所指的"未登记写入方"。其写入时机不可预期（worker 异步、可跨 1+ 小时），与他人编辑窗口重叠时即表现为"内容突变"。

### 3.2 W2：k3-digest 波次脚本 —— 08-25 注册表回滚事故肇事方（实锤，已闭环）

**实证链**（candidate_module_registry.yaml，全部 UTC）：

- 08-25 07:06 `∅→055bdd5a`（k3-digest-w3 波 WIP）→ 07:13 heal（`806173d85d` W3 落盘，055bdd5a 成为 HEAD）
- 08-25 08:07~08:10 三次连写 `375c4533→2f221f75→95b16206`（无活跃会话记录——会话心跳窗口间隙）→ 08:32 `0d89510c` → 08:42 heal（`6b16e05055` P1 R1 落盘）
- **08-25 10:15:06 `∅→055bdd5a`（HEAD=`0d89510c`）——工作区内容被写回 3 小时前的 W3 版本，R1 已提交内容被覆** → 10:20 `→428d9e96` → 10:29 heal（`b7c83dd84c` P1 R1 重做+R2 落盘）

**定性**：`b7c83dd84c` 提交信息自供"修复 R1 行级合并 off-by-one（19 条错位已回滚重作，块级脚本+双校验，#ARCH-237 事故留痕）"；#ARCH-237 裁决书记录"注册表回滚至 806173d8（W3 后良态），改写块级翻转脚本"。即 10:15 的 055bdd5a 回滚是 digest 团队**故意回滚+重作**的恢复动作（deliberate stale write），非流氓写入——但它实证了"以旧 blob 整文件覆写注册表"这一动作模式在多会话共享热门文件上的破坏力（若当时有第三方在 R1 后又提交，其内容将被静默吞掉）。

**残余风险**：`.runtime/digest_p2/flip_wave.py` 现行版本仍为整文件 `read_text→字符串手术→write_text`，不经过 `safe_write_text` CAS（热文件写前读新对其无强制力）；竞态窗口（读→写）为秒级，但波次密集日（08-25/26 每日 6+ 波）与 AI-CRYPTO-001 类会话交错时仍可能吞写。

### 3.3 W3：commit_queue 落盘/着落路径 —— 嫌疑基本排除，残余风险登记

**取证**：K3-MINK8803 会话 08-26 有 4 个 dead 队列项（`.runtime/commit_queue/dead/q-20260826-K3-MINK8803-0001~0004`）：

- 0001（16:30:12 创建）：batched auto-commit（4 reconcilers）reroute 自 `_commit_auto`，携带 68 个派生文件 blob（blueprint 群+EA index+manifest+目录注册表），16:36:51 死于 PROTECTED-PATHS 阻断（architecture_model/index.yaml 需 Owner 审批）
- 0002（16:30:44，80 文件）：同因死于 16:51:32
- 0003/0004（单文件）：死于 LOCK_TIMEOUT

队列 worktree（`.runtime/commit_queue/worktree/`，基线 `48f65bc5a0`）内容陈旧，但着落侧有防护实证：`main_workspace_sync.jsonl` 显示 landing 对主工作区 dirty 文件一律 `skipped_dirty`（08-26 18:19 对 k3-ddl-p0-0826 队列项 4 个文件全部跳过）。**未发现队列路径向主工作区回写旧内容的实证**；受害三文件不在任何死信文件清单内。

### 3.4 W4：秒级覆写者 —— 无法唯一定凶（取证能力缺口）

94号在 08-26 的全部 watchdog 记录（UTC）：

- 06:27:12 grace `∅→1f6c88f5`（v0.2.0 编辑，14:35 落盘）
- **08:28:12 alerted `1f6c88f5→acb63b1a`（HEAD=1f6c88f5，活跃会话仅 worker-e97f383d-24796）——文件从"==HEAD 的干净 v0.2.0"变为新内容；08:28:51/08:28:57 同签名重复告警（daemon 与网关 post-commit 扫描竞态，dedup 失效）**
- 08:32:50 alerted `acb63b1a→17f34d29`（活跃会话仅 K3-MINK8803；17f34d29 后为 v1.0.0 正式 blob，16:42 落盘）
- 09:09:16 alerted `∅→ad585d76`（v1.1.0 WIP，17:13 落盘）
- 10:17:39 alerted `8abb1ae2→bed6e416`（v1.3.0 WIP，18:24 落盘；活跃会话 worker-de601c22-23020、k3-ddl-p0-0826）

**能确认的**：①所有捕获到的迁移方向均为前进（prev==HEAD 或 WIP 递进），未捕获"回退型"迁移；②混合态（frontmatter 回滚 0.1.0+§5 丢 009 行）最可能对应 `acb63b1a`（16:28:12 出现，内容未入 git 无法复原），出现时刻系统内唯一活跃进程是 K3-MINK8803 的 reconcile worker（worker-e97f383d-24796，§3.1 实证其当时在跑 27 个 reconciler）；③AI-CRYPTO-001 报告的秒级反复覆写（事故④）与 2.14.2 行丢失（事故③）在 60s 扫描底账中**零痕迹**——写入与恢复发生在相邻两次扫描之间。

**不能确认的**：秒级覆写的具体进程/会话。watchdog 的 active_sessions 只反映"扫描时刻心跳新鲜的会话"，不等于写入方；现有体系无 PID 级文件写审计（safe_write 仅覆盖声明式调用方）。reconcile worker 的在场是强关联证据但不是定罪证据——其 27 个 reconciler 中无一的设计职责包含写 design_memos（frontmatter 同步器范围=docs/03_modules 且只写 4 个核心字段，已逐行核读排除）。

**诚实结论**：W4 定凶需要 FileSystemWatcher 级写审计或将热文件写纳入强制 CAS（§6 O3），本次不凭猜测定凶。

### 3.5 排除清单

- pre-commit 钩子群：全配置核读，纯检测无文件改写（gate-17 --fix 仅限根目录孤儿 .py，与本案无关）
- worktree 同步（`.worktrees/` 四个 worktree mtime 均为 08-16/17，休眠超一周）
- 计划任务直写：ZephyrAlpha 系任务（DataScheduler/TickSubscriber/CHHealthProbe/DeadmanSwitch/AI-Wrapper-Inject/WorktreeDriftWatchdog）均为数据面/治理面常驻，无写 docs 证据
- bj-daily：08-26 06:40Z 前后活跃（与 mink8803-20260826 同窗），其触及文件（candidate/translation 注册表、README、01_overview）均为 grace 合法窗派生写
- GATE-BLUEPRINT-FRONTMATTER-SYNC：范围 docs/03_modules、只写 module_id/responsibility_domain/design_maturity/build_status 四字段、depgraph 实时查询为真源、带 blueprint_write_lock（#ARCH-RECONCILER-TOCTOU-CLOBBER-001 止血）——与 94号/00索引 版本头回滚无关

---

## 4. 遗留确认（Step 5）：AI-CRYPTO-001 成果完整性 —— 全部通过

| 验证项 | 命令 | 结果 |
|--------|------|------|
| 94号 frontmatter | `git show HEAD:.../94_crypto_quant_expansion.md` | `status: active`、`version: "1.3.0"` ✅ |
| 00索引 frontmatter+修订行 | `git show HEAD:.../00_index_trading_decision.md` | `version: "2.14.3"`；修订表 2.14.1/2.14.2/2.14.3 三行俱在（2.14.2 行带"曾因并发覆写丢失，2026-08-26 补回"注记）✅ |
| 候选注册表 | `git show HEAD:.../candidate_module_registry.yaml` | CAND-CRYPTO-001~010 共 10 条；总条目 607 ✅（与派单预期一致）；009 头部日志行在（带"曾因并发覆写丢失，2026-08-26 补回"注记）✅ |

digest 波次提交对 crypto 内容零触碰实证：`git diff 0d101c3f..4450cbdac8` 与 `100f84841f..91bc3de15b` 对注册表的 CRYPTO 相关行 diff 均为空。**无需从锚点序列恢复任何内容。**

---

## 5. 处置与治本（Step 4）

### 5.1 立即处置（本会话已执行）

- **无需停止任何进程/会话**：W1 为设计如此的派生写（按纪律不擅改，报 Owner 裁定）；W2 已当日闭环；W3 死信已失败安全；未发现可杀的流氓进程。
- **94号纳入 CAS 热文件清单**（B 兜底第一刀）：`src/zephyr/shared/io/file_utils.py` `DEFAULT_HOT_FILES` 增加 `design_memos/94_crypto_quant_expansion.md`——即刻起：①`safe_write_text` 对其强制写前读新（无 base 拒写/base 不符拒写）；②commit 闸 HOT-FILE-BASE-FRESHNESS 将其纳入 base 新鲜度硬阻断（claim 体系内）。tests/shared/test_safe_write.py + tests/io/test_io_file_utils.py 34/34 绿。
- 本会话零触碰其他会话 WIP（含 W07/task:SRC-081 在飞的 200+ blueprint 与注册表 WIP）。

### 5.2 结构性根因与治本方案（A 源纠/B 兜底/C 预防）

- **R1（A 源纠，W1）**：派生写 reconciler 是"未登记写入方"的字面对应体——无 claim、无锁、无 base 声明、worker 长寿命（实证 78 分钟）。建议方向（属行为变更，报 Owner 裁定，见 O1）：reconcile worker 执行派生写前注册心跳+claim 其派生文件集（watchdog claimed 通道即刻消音且合规化），或将派生产物标注 auto-sync 登记免告警。
- **R2（A 源纠，W2 残余）**：整文件 read-modify-write 无 base 校验的临时脚本模式（flip_wave 族）——建议：批量注册表改写脚本一律改走 `safe_write_text(expected_base_sha256=...)`（热文件已被 CAS 拒写强制），或在脚本头部加 base 断言。属 digest 施工纪律，报 Owner 裁定是否立规。
- **R3（B 兜底，体系）**：①CAS 热文件清单当日已扩 94号，后续按"事故即扩列"原则滚动；②`--allow-overlap` 逃生通道对热文件的实际放行率建议纳入月度治理度量；③lock_files 遵守率实测≈零（当前零活跃锁、claim 快照全为历史件）——RULE-ZERO 锁纪律在 AI 工具链路径上无强制点，建议将"热文件写前锁/CAS"二选一立规（规则文件落点见 O7）。
- **R4（C 预防，取证能力）**：秒级覆写定凶需要 PID 级写审计——建议评估：对 DEFAULT_HOT_FILES 建立 FileSystemWatcher 轻量审计守护（写者 PID+时间戳+前后 hash 落 .runtime/audit/），或将 AI 编辑工具链的热文件写纳入统一拦截层。见 O3。
- **R5（C 预防，反模式登记）**："持有旧缓存/旧基线整文件覆写"反模式随 #ARCH-264 登记；规则文件正式落点（trae_001/005 均为 frozen+immutable_core，trae_027 域不符）建议 Owner 裁定（见 O7）。

### 5.3 告警疲劳治理（附带发现）

3041 条 alerted/72h（其中大量为派生写 churn 的同签名重复+daemon/网关双扫描竞态重复，实证 08:28:12/08:28:51/08:28:57 三连）——建议：①watchdog dedup 加跨进程状态锁或单扫描入口；②派生写登记后告警量预计下降两个数量级。见 O6。

---

## 6. 遗留开放问题（报 Owner 裁定）

| # | 问题 | 背景/建议 |
|---|------|----------|
| O1 | 派生写 reconciler 的合规化路径：worker 注册 claim vs auto-sync 登记豁免 vs 派生产物离库 | W1 行为变更属"设计如此"改造，须 Owner 定方向 |
| O2 | HOT-FILE-BASE-FRESHNESS 的 `--allow-overlap` 逃生通道政策 | 当前热文件提交普遍携带该旗标，硬阻断形同虚设；是否对热文件禁用或计数升级 |
| O3 | 秒级写取证能力建设（FileSystemWatcher 审计/编辑工具链拦截层） | W4 定凶的前置；建或不建、范围多大 |
| O4 | `.runtime/quarantine/` 快照清除方与保留策略 | 08-25 批次快照已灭失，清除方未定位；建议定 retention（如 30 天）并登记清除路径白名单 |
| O5 | commit_queue worktree 旧基线着落加 base 新鲜度前置校验 | 当前 skipped_dirty 防护有效（有实证），但 base 过旧的队列项着落前无显式校验 |
| O6 | watchdog 告警疲劳治理（dedup 竞态/派生写豁免/扫描入口唯一化） | 3041 条/72h，banner 已失真 |
| O7 | "旧缓存整文件覆写"反模式的规则文件正式落点 | trae_001/005 frozen+immutable_core 不可直改；建议 Owner 指定落点（新规则文件或 AGENTS.md 约定段） |

---

## 7. 证据锚点清单（可复现）

1. `.runtime/audit/worktree_drift_watchdog.jsonl`（17.7MB 全量事件底账；本报告全部 hash 链/时间戳/活跃会话出处）
2. `data/databases/governance.db` reconcile_execution_log（GATE-WORKTREE-DRIFT-WATCHDOG 行）
3. `.runtime/drift_watchdog/state.json`（alerted 状态表）
4. `.runtime/reconcile_reports/reconcile_status_e97f383d185c363c9eaa7db360d325bf4b594e7d.json`（worker 78 分钟存活+27 reconciler 实证）
5. `.runtime/commit_queue/dead/q-20260826-K3-MINK8803-0001~0004.json`（死信解剖）
6. `.runtime/commit_queue/main_workspace_sync.jsonl`（skipped_dirty 防护实证）
7. `.runtime/audit/safe_write.jsonl`（多 PID 同内容覆写实证）
8. git：`b7c83dd84c`（#ARCH-237 自供）、`1a87b444bd`（reconciler batched auto-commit 实证）、`git log -- <受害文件>` 时间线
9. architecture_issue_registry.yaml #ARCH-237（注册表事故前案）
10. 分析脚本：`.runtime/tmp/_drift001_forensics.py` + 输出 `.runtime/tmp/_drift001_out.txt`（本报告全部统计的可复算入口）

## 8. 附：#ARCH-264 登记条目（待注册表文件脱离他人 WIP 后写入）

```yaml
- issue_id: '#ARCH-264'
  title: 并发覆写事故取证与治本（drift watchdog"未登记写入方"）——reconciler 群派生写合规化+digest 脚本整文件覆写模式+CAS 热文件扩列 94号+秒级写取证能力缺口登记
  severity: P1
  category: 治理流程
  adjudication: >-
    2026-08-26 AI-CRYPTO-001 编辑 94号/00索引/候选注册表期间连遭 4 起并发覆写事故（提交后混合态/版本头回滚/
    修订行丢失/秒级反复覆写）。AI-DRIFT-001 取证（docs/_working/reports/2026-08-26-drift-writer-forensics.md）：
    ①告警洪水与 handbook churn=post-commit reconciler 群派生写（worker 存活 78 分钟实证，无 claim/无锁/无 base 声明，
    即"未登记写入方"字面对应体）；②08-25 注册表 055bdd5a 回滚=k3-digest 故意回滚重作（#ARCH-237 已闭环）；
    ③commit_queue 路径嫌疑排除（死信失败安全+skipped_dirty 防护实证）；④秒级覆写者因 60s 看门狗粒度+无 PID 级写审计
    无法唯一定凶（取证能力缺口登记）。处置：DEFAULT_HOT_FILES 扩列 94号（CAS 写前读新+commit base 新鲜度门禁，
    34/34 测试绿）；AI-CRYPTO-001 已提交内容 HEAD 验证完整（94号 v1.3.0/00索引 2.14.3 三行俱在/CAND-CRYPTO×10 总 607）。
    反模式登记："持有旧缓存/旧基线整文件覆写"列为协作反模式——热文件写前必须读新（safe_write_text CAS 或 lock_files），
    整文件 read-modify-write 脚本必须过 CAS；规则文件正式落点待 Owner 裁定（trae_001/005 frozen 不可直改）。
  impact:
    - 'src/zephyr/shared/io/file_utils.py（DEFAULT_HOT_FILES +1）'
    - 'docs/_working/reports/2026-08-26-drift-writer-forensics.md（取证报告）'
  fix_phase: '部分落地（2026-08-26，AI-DRIFT-001）；reconciler 合规化/秒级取证能力/规则落点报 Owner 裁定（O1~O7）'
  status: open
  created: '2026-08-26'
  last_updated: '2026-08-26'
```
