---
ttl: task_bound
---

# P3 · integrity「每件同步 register」→ HEAD 派生基线：只读预研卷宗（施工坐标）

> 车道：提交链治本夜战 · 千问 Flash 施工队 · 分包3 预研（战役 L4 迁移阶梯 S 阶段 / B0-M1 同族）
> 性质：**只读预研 + 补丁草案**。零改生产码、零 commit、零 enqueue、未登记 creation_token（由统筹会话落地后统一处理）。
> 草案正文＝`../../../.runtime/tmp/csx_p3_patch_draft.md`（锚定断言式 before/after，20 条锚已跑逐字节 n==1 自检）
> 既有设计对齐：`../40_b0_derived_offload/b0_1_sync_sites.md`（表 B4/表 D）、`../40_b0_derived_offload/b0_3_design_and_tests.md`（§2.1/§4 M1）、
> `../20_target_arch/a4_migration_ladder.md`（S1"校验读不可变树"地基）、`../10_d1_d2/d1_d2_readme.md`（D2 per-spawn 注入范式）

## 1. 一屏结论

1. **同步 spawn 点共 5 处**，其中真正在"每件关键路径"上的只有 1 处（队列落地器），另 4 处分布在锁内/worker 内/钩内。
2. `validate_rules_integrity.py` 的**注册面读 HEAD、校验面读工作树**，两者之间靠一张**滞后的 DB 快照**搭桥；
   该快照既是判定输入又必须及时更新 ⇒ 每件同步注册成了这套不同源判定的续命手段，**不是可选优化**。
   ⇒ 只把 register 异步化 = 把"每件 46s"换成"随机阻断"。假红**已有在案实据**（不是假想，见 §4）。
3. 正解＝**把校验的参考面从"DB 快照"换成"当前 HEAD blob"**（不可变、零滞后）：
   工作树面照读（WIP 篡改检测不降级），DB 退出判定链 ⇒ 刷新义务与记账税同时失去存在理由。
   实测新参考面的成本比现状**更便宜**（17 项 0.026s / 120 项 0.110s，对比 17 次 `git show` 0.332s）。
4. 顺带挖到一个**静默保护归零**事故：`_GATES_DIR` 仍指向 `src/zephyr/governance/commit_gates`（已随
   governance→gov_enforcement 迁移改名），glob 返回空 ⇒ `RULES_MANIFEST` 只剩 17 条静态项，
   **119 台 pre-commit gate 实现整体脱离 C 层 golden hash 保护**，且零红零日志（见 §2.4）。

## 2. 精读定位（施工坐标，全部 2026-09-24 主仓 `dev` 盘实测行号）

### 2.1 五处 register/fold spawn 的分布

| # | 位置 file:line | 干什么 | 同步面 | 是否产记账件 |
|---|---------------|--------|--------|-------------|
| S1 | `scripts/governance/commit_queue_landing.py:1448-1475`（本体）→ 调用点 `:1746`（legacy 落盘）与 `:1814`（池化 CAS 重放） | `subprocess.run([python, validate_rules_integrity.py, "--register"])`，`:1468 timeout=180` | **件内同步**：在 `_pool_process_item` 的 `_item_t0`(`:2155`)→记账(`:2218`) 窗口内、且在**路径锁内**（`_item_path_locks` 于 `:2176` 取、`:2194` finally 放，包裹 `landing(item)` 全程） | 否——只把新 DB 写进主区工作区然后 `return ""` 弃之不管 ⇒ **每件在主区制造一个脏派生文件** |
| S2 | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:2106-2181`（`_post_flush_rules_integrity_re_register`）→ `_sp.run --register` 在 `:2133`，DB `_commit_auto` 在 `:2167`；调用点 `:2235`（同步链）/`:2301`（worker 链） | flush 后重注册 + 提交 DB | 默认**异步**（`run_post_commit_reconcile` `:1063-1091` 走 detached worker；`ZEPHYR_RECONCILE_SYNC=1` 或 commit_sha 缺失才回退同步） | **是**＝近 24h 10 笔 `chore(integrity): post-flush re-register…` 的唯一来源（消息字面见 `:2160`） |
| S3 | `git_commit_gateway.py:2019-2104`（`_fold_rules_integrity_into_batch`）→ `_sp.run --fold` 在 `:2065`，调用点 `:2230`/`:2297` | flush 前用工作树混合算最终态 DB，`batcher.buffer` 并入批提交 | **锁内同步**（`with self._batcher` 块内） | 折入成功时无尾笔；失败即降级回 S2（`:2077`/`:2082`/`:2104` 三处 warning 留痕） |
| S4 | `src/zephyr/governance/audit/reconciliation_registry.py:6751-6863`（`_reconcile_rules_integrity`，GATE-INTEGRITY-AUDIT 成员，组合于 `:7049`）| `--register`（`:6784`）+ DB `_commit_auto`（`:6838`，消息 `chore(integrity): auto-re-register…`） | batcher 启用时 **defer**（`:6767-6774`）⇒ 今天多半不跑 | 实测近 24h 与近 7 日均 **0 笔**（属"零触发"面，但它是第 2 个潜在税源） |
| S5 | `scripts/governance/gateway_post_commit_ritual.py:196-200`（`plan.append(("integrity_register", … "--register"))`），由 `.pre-commit-config.yaml:832-839`（`stages:[post-commit]`, `always_run:true`）驱动 | 批次触碰 rules/contracts → 三步重钉（契约生成/freeze/register），失败 `_restore_outputs` 整体回滚 | **钩内同步**（在 `git commit` 进程返回前跑完，B0_1 表 A3 同族） | 否（写 DB，靠 S2/S1 或 `commit_derived_sync.py:49` 收口） |

> 任务书预估的 `:3510/:3557/:3973/:4025` **不是** integrity 位点——那 4 行是同文件的 env 旗写点（D2 车道管辖）。已在 §1 纠偏。

### 2.2 注册面 vs 校验面到底各读哪里（判据语义核心）

真源文件 `scripts/governance/meta/validate_rules_integrity.py`（545 行）：

| 面 | 函数:行 | 读什么 | 关键细节 |
|----|--------|--------|---------|
| 注册 | `register()` `:250-295`，HEAD 读在 `:267` | **HEAD blob**（`_hash_git_head` `:205-229` = `git show HEAD:<p>`） | 文件不在 HEAD 时回退工作树（`:275-282`）；hash 全同则**不写 DB**（`:286-287`，2026-06-30 自指循环治本） |
| 折入 | `register_fold()` `:298-375` | changed_files 用**工作树**（`:343`），其余**复用旧 DB**（`:352-356`） | 混合面——它存在的唯一理由就是"S1/S2 来不及"，即不同源判定的补丁补丁 |
| 校验 | `check()` `:378-446`，工作树读在 `:401` | **工作树物理字节**（`_hash_file` `:199-202` = `Path.read_bytes()`） | 参考物取自 DB `:402-403`；严格只读、禁 `_save_db`（`:433-437`，TRAE-082 因"check 写时间戳→dirty→阻断所有提交"事故而立） |
| 归一 | `_normalize_eol()` `:180-196` | CRLF/双 CR → LF，两面同函数 ⇒ 行尾差异不误报 | head 态批量读复用同一函数（草案 A1 已保序） |
| 门禁 | `main()` `:493-516` | `--register`/`--fold` 均需 `ZEPHYR_RECONCILER_MODE=1` | 红蓝发现4："重置基线=合法化当前状态" |
| 消费 | `.pre-commit-config.yaml:252-258`（`gate-rules-integrity`，`args:["--check"]`，`files:"^(AGENTS\\.md\|scripts/governance/)"`） | 见 §4 | **不在** `git_commit_gateway.py:407` 的 SKIP 三兄弟里 ⇒ 网关通道内会跑 |

**最小改点**（草案 P3-A，三处）：
- A1 新增 `_read_head_blobs()`（一次 `git cat-file --batch` 批量取 HEAD 面，与 `_hash_git_head` 逐字节等价语义）
  ＋ `_staged_change_set()`（`git diff --cached --name-only HEAD -- <protected>`，天然继承 `GIT_INDEX_FILE` own-scope 临时索引）
  ＋ `_baseline_mode()`（env per-spawn 注入 > flags > `snapshot`，异常 fail-closed 回现状）；
- A2 `check()` 参考物从 `db["files"][rel]["hash"]` 改为 `refs[rel]`（head 态＝当前 HEAD blob），
  并在 `TAMPERED` 前插一个 `CHANGING_IN_COMMIT` 解释位；
- A2b 返回体加 `baseline_mode`/`changing_count`（纯观测）。
**判定阈值、`clean` 定义、exit code（2=阻断）、MISSING/UNTRACKED 语义全部零改动。**

### 2.3 为什么"改读 HEAD"必须配一个解释位（本包唯一不显然的地方）

`check()` 在**提交时**跑（S 表格最后一行的消费面），此刻 HEAD 还是父提交，
本提交正要合法改写 `AGENTS.md` ⇒ 工作树 ≠ HEAD ⇒ 若只换参考面不改别的，
合法提交受保护文件这件事会**永远**被判 TAMPERED。今天这条是靠"提交前先改工件基线"
（`--register`/`--fold` + 注释里写的手工流程"改受保护文件后先 --register 更新基线，再 commit"）换来的。
head 态的等价物＝"该路径正在被本提交改写 ⇒ 记 `CHANGING_IN_COMMIT`"，
判据强度不变而**不再改任何工件**。`MISSING` 分支**显式不吃**这个豁免（防"解释位变删除逃生口"）。

### 2.4 顺带发现：C 层保护面静默归零（独立于本包，建议同批修）

`validate_rules_integrity.py:164` 的 `_GATES_DIR` 仍指向 `src/zephyr/governance/commit_gates`；
实测该路径 `exists()=False`，而真身在 `src/zephyr/gov_enforcement/commit_gates`（HEAD 内 119 个 `.py`）。
后果（全部本车道实测）：`_DYNAMIC_GATE_ENTRIES=0`、`RULES_MANIFEST=17`、
盘上 `rules_integrity_db.json` 17 条且 `commit_gates` 条目 **0 条**、注册时刻 2026-09-24T11:45Z。
即："防漏登优先于防误登"的 glob 设计（`:75-81` 注释自述）在目录改名后**静默反向失效**，
而它保护的对象恰恰是最该被 golden hash 守着的 119 台门禁实现。零红、零日志、无告警——
与宪法"静态清单禁手工维护 + 每把尺先自证能红"两条红线同时相冲。草案 A3/A3b 修路径 + 加空清单 stderr 自证。
**此发现需上升**（可能是 08 域/全景图改名波的漏网，或另有一张名册当真源），已记 max_ruling_queue 一案。

## 3. 成本实测（本车道亲测，warm 态；争用放大未折算）

| 量 | 值 | 怎么量的 |
|----|-----|---------|
| `validate_rules_integrity.py --check` 端到端 | 0.13s min / 0.15s mean（n=3） | `subprocess.run` 墙钟 |
| 17× `git show HEAD:<p>`（＝现 register 的 git 成本） | 0.332s | 同法 |
| 1 次 `git cat-file --batch` n=17 | **0.026s** | 草案 A1 的原语 |
| 同上 n=120（含 119 台 gate 复权后） | **0.110s** | 同上 |
| 1 次 `git ls-tree HEAD -- <120 paths>` | 0.022s | 备选原语（只给 blob oid，不含 normalize 后 sha256，故未采用） |
| `python -c pass` 冷启 | 0.03s | 下界 |

⇒ **推论**：40–46s 的每件尾段**不是** hash 计算造成的。B0_1 表 B4 的口径是
"收敛末条 → 件结束（含 180s 超时的 integrity 基线刷新）"，med 6.2s / mean 46.1s / max 300.7s——
med 6.2s 才与"1 次 python 子进程 + 17 次 git show + 争用"量级相称，
mean/max 由该窗内一并计的 bookkeeping 与**超时白等**（上限 180s）抬起。
本包能**硬保证**的回收＝该窗内 spawn 数从 1→0、超时上限 180s→不存在；
不冒进认领"每件省 40s"（该数字属 B0 车道的段观测，非本包可独占归因）。

## 4. 假 TAMPERED 坑：在案实据 + 草案如何正面解决

**实据（不是假想）**：`.runtime/audit/commit_block_events.jsonl` 里
`hooks` 含 `gate-rules-integrity` 的记录共 8 条 =
6× `precommit_channel_blocked` + 1× `commit_blocked`（网关真被拦下，会话 `st-final3-20260919-redproof` ×4、
`st-maxexec-20260920` ×1）+ 1× `precommit_channel_global_debt_warned`。
`git_commit_gateway.py:3206-3208` 的 docstring 自己就把"GATE-INTEGRITY 金hash 记录滞后"
当"存量全局债降级 warn"的举例——即该坑被官方承认、目前靠 own-scope 归因**绕行**而非填平。

**盘面活体**：本车道跑 `--check` 得 `rc=2`、1 项 TAMPERED：
`capability_canonical_file_registry.yaml` known `b34f3e3b15ac0c56` → current `cfa79e1dc661019b`
（主区脏文件 968 个、该册含他会话 157+1 条未提交令牌）。这条在 head 态下**仍判红且更正确**：
它是"工作树 vs 当前 HEAD"的真漂移，而不是"工作树 vs 某过去 HEAD"的滞后假象。

**草案如何解**：见 §2.2/§2.3 的 A2 改点——参考面换成当前 HEAD ⇒ 滞后不可发生；
工作树面保留 ⇒ WIP 篡改检测不降级；解释位 ⇒ 在途合法改写不再需要改工件来洗。
可红判据 9 条（R-1…R-9，含"注入 HEAD 与工作区不一致的文件，门**不得**判 TAMPERED"与
"HEAD 基线被真篡改**必须**判红"两例的双态对照）全部写在草案 §9，本卷宗不重复。

## 5. 牵动面（施工侧逐条处置，禁删测试凑绿）

- 生产码：`validate_rules_integrity.py`（非红线，可直改）、`reconciliation_registry.py`（非红线）、
  `gateway_post_commit_ritual.py`（非红线）、`config/flags.yaml`（新增键，出厂态=现行为）；
  **红线四件**＝`commit_queue_landing.py`(S1)、`git_commit_gateway.py`(S2/S3) 待 0001 落地后由统筹会话改，
  本车道一行未动。
- 测试：`tests/governance/audit/test_validate_rules_integrity_fold.py`（4 例，其中
  `test_manual_db_hash_edit_reports_tampered` 语义本包变更最大）、
  `tests/governance/audit/test_integrity_audit_reconciler.py`、
  `tests/git/test_git_commit_gateway.py`（`:1972/:1986/:2001/:2056` 派生归属精确集）、
  `tests/git/test_claim_retention_derived_attribution.py`（`rules_integrity_re_register` source 名）、
  `tests/governance/test_gateway_post_commit_ritual.py`（仪式计划步骤集合）、
  `tests/governance/audit/test_workspace_hygiene_reconciler.py`（连带，本包不动）。
  `tests/governance/test_commit_queue*.py`：全仓 grep **未见**任何测试引用 `_refresh_integrity_baseline_main_repo`
  ⇒ 预计零牵动，施工侧复核后如实记"无牵动"（不臆测）。
- 文档/规则连带（落地批必须同批处理，否则文档与判据自相矛盾）：
  `.pre-commit-config.yaml:250-251` 注释的"合法修改流程：改受保护文件后先 --register 更新基线，再 commit"
  与 `validate_rules_integrity.py:511-513` 的 `--register` 阻断文案（"合法更新规则文件请通过 GitCommitGateway commit
  （post-commit 自动注册基线）"）在新语义下都需改述（HEAD 即基线，无需注册）。
  `scripts/governance/commit_derived_sync.py:24/:49`（"金标哈希 DB 还原=写入→还原死循环，必须 commit"）
  在 DB 退出判定后不再成立 ⇒ 属下一批（见 max_ruling_queue 第二案）。

## 6. 回收测算

| 项 | 数字 | 来源 |
|----|------|------|
| 每件关键路径同步 spawn | −1（S1），并消掉 180s 超时白等面 | 代码直读 |
| 每件锁内衍生 spawn | −1（S3 `--fold`，`timeout=30`） | 代码直读 |
| worker 侧 spawn | −1（S2），并失去钩内 `--register`（S5） | 代码直读 |
| 实测每件尾段 | med 6.2s 归零；mean 46.1s 中"本包可独占"部分＝spawn+hash 本体 ≈ med 量级，其余属 bookkeeping（**不冒进认领**） | B0_1 表 B4 + §3 亲测 |
| 记账件 | 近 24h dev **10 笔** `chore(integrity)` / 161 笔 ＝ **6.2%**；近 7 日 27 笔（全分支 948 笔）。第二税源（`auto-re-register`）实测 0 笔＝潜在消除 | `git log --since=… --pretty=%s dev/--all` 亲测 |
| 新增成本 | head 态 check 的 HEAD 面读取 0.026s（17 项）/ 0.110s（120 项）+ 1 次 `git diff --cached` ≈0.05s | §3 亲测 |
| 不认领 | 残差 ≈630s/件（UNKNOWN，待 A2 分段计时器）、门禁链 Σ39.8/63.7s、D1/D2、M2 再生扇出争用 | B0 表末行"本车道不猜" |
| 净零声明 | 不新增门/规则/册；退役 4 个同步 spawn 与 2 个税源；复用 B0_3 已规划的 derived_dirty ledger；1 个 flag 键出厂态=现行为 | 宪法全资产净零条款 |

## 7. 上升事项（已登记，不自行拍板）

见 `../90_verification/max_ruling_queue.md` 两条：
① GATE-RULES-INTEGRITY 的**真源归属**——基线究竟应是"登记制工件（DB 入 git）"还是"HEAD 可派生量（DB 出库）"；
② 119 台 gate 保护面清单的**真源**——glob 目录写死在脚本里 vs 应以门禁名册为准。
两条都属判据语义层，不在本车道裁量范围内。


## 附表 · MQ-3 保护面静默归零回溯（廉价版，2026-09-25 凌晨统筹会话实测）

- 盲窗定义：改名提交 ae3d1b1138（2026-07-13，commit_gates → gov_enforcement/commit_gates）起，
  至本包 A3 修复落地前——期间 _GATES_DIR 指向已改名旧路径，glob 静默返回空，
  119 台门禁实现整体无 C 层 golden hash 覆盖（保护对象裸奔，非写入绕门）。
- 盲窗内触碰提交：共 372 笔。印记分布：[GW:] 网关直提 14 笔；[st-*] 队列袋 11 笔；
  merge 7 笔；更早战役约定标记（W7/final3/ARCH-APPROVAL/allow-mass-deletion 等）340 笔。
- 带外嫌疑（GW/st/merge 三无）初筛 341 笔，全部为旧约定战役戳，逐类抽样可溯源；
  **零真正带外写入证据**。
- 结论（MQ-3 口径）：正门链自身即审计面成立，无升级立案事项。敞口定性＝保护面缺失
  （本包 A3 复权 136 条修复），非未授权变更。不做历史重放。

### 盲窗提交全列表（372 行）

```text
f53316c6f9d [st-cleanup-final-20260924][④e+f 数据源注册表入校验面+因子inputs闭包+⑥related_arch清零·Owner 全批] e)REGISTRY_SPECS 纳入 data_sources_registry（base_dir 出 catalogs 机制+spec_path 统一三消费方+23 条目补 MOD-L00-001 锚；align layer2 红测 3 例）+f)check_registry_code_anchor 加因子 inputs 闭包（field_id∪field_name 双口径+tombstone 豁免；junk inputs 不再 GREEN，红测 3 例）+⑥裁定册 related_arch 三悬空净删（#383 MOD-L00-004、#387 PS-CTR-003/MOD-INF-043 实证议题册+depgraph 皆无真身=数据错误；audit-all-0011 并非其解药，layer2 治理双向 18/18 转绿）。[ARCH-APPROVAL:ARCH-AUDIT-BLIND-08]（issue_id 映射：审计班失明清单#8/#10=AUDIT_REPORT.md，议题册登记为后续项；授权链=Owner 2026-09-24 全批收尾总包任务④e/⑥原文）
4fc2cf6d045 Merge branch 'ai/st-gpu-final-20260924/gpu-final-campaign' into dev
31ec66db343 [st-gpu-final-20260924][GPU批·代码面+ORPHAN门修] 成本门修真（哑门40bp假绿→3.83红证三修）+条件轴输入包MOD-BT-COND-PACKAGE（F4选族自纠；真库1570日/12胞/9胞达30日地板）+归因读端；SQL常量集中化；ORPHAN门pathspec=:(glob)修复（5层模块恒误判bug GT-ORPHAN-PATHSPEC-001）；双algo_flow yaml随批（含边定义，marker/link双钩子过）。18测试绿。 [GW:st-gpu-final-20260924]
909e49e41fd [st-align-dirty-20260924][自伤复原批②] TAG-VOCAB 双语闸与其测试被本包 q-0014 陈旧 index 吸收抹掉的 22+17 行原文回填
9ff96cc5c39 [st-pipeline-final-20260924][pool:池化批 v4·剥册版] k4 池化 8 文件（landing/daemon/gateway/thresholds/两测试/bare_sql_gate/preflight）+身份键随 0f08f7a06c 已在
53cdc66e062 [st-align-dirty-20260924][翻译册补 plain_zh 续批·22 条] 修尺子后新可见面（旧探针 pathspec 漏顶层 scripts/*.py）
cf536fb4a10 [st-library-final-20260924][直连·A班建设] 词汇表强制双语：TAG-VOCAB 闸双语校验维度（12 号令任务 7 延伸）
0f08f7a06c4 [st-k4-20260923] 池化终批 v3（st-cmd 代投，根因修复）：三死链根因=entry_identity_key 函数只存在于 0017 袋搬运版（registry_family/），HEAD flat 老文件从未有过——反方案把 landing.py import 改回 flat 后身份真源消失→合并器全灭→名册合并死锁连杀 0008/0009/library-final 两批。修=身份函数从 0017 袋 blob e71444cd2eb8 原文回植 flat 文件（W2 语义唯一真源归位，import 验证过：单键/复合键双态正确）。本批 10 文件自洽落地：①flat 文件（+entry_identity_key 回植）②池化五件（landing 含 resolve_pool_workers+drain_queue_pool、import 维持 flat 原位/daemon/gateway/thresholds/pool 测试 13 例）③追加令⑧三件（bare_sql_gate Final 修/preflight/对齐测试）④名册（module_path 回 flat 原位）。落地后三方自洽+身份可用+池化正式入 HEAD（daemon 盘面版已 4 件并发实证池化运行）。registry_family 迁移彻底撤案。k=1 开关 Owner 批常驻。
40957cee3a3 [st-gslim-20260923] [allow-mass-deletion:P4七簇合并15吸收条目除名 Owner E全批 C2机械依据] P4 合并批（C2 七簇 22→7，gate_audit_report_v1 §C2/Owner E 全批；L2 台数 114→99=审计 D 表终态）：合并式=「union 家工厂+吸收台闭包提级」——①7 家 union 工厂落各簇家文件（REFERENCE-INTEGRITY@dangling_reference pri70 / PERMANENT-SYSTEM-TRIGGER@perm_trigger pri82 / GATE-VOCAB@vocab_hardcode pri80 / DEPGRAPH-ENFORCEMENT@depgraph_pre_registration pri113 / MAP-ALIGNMENT@panorama pri141 / BLUEPRINT-HEADER@blueprint_amodule_consistency pri79 / COMPLEXITY-GUARD@high_complexity pri92）：聚合子检查独立判定、违规带 [源台名] 前缀聚合呈现、任一失败即阻断；COMPLEXITY-GUARD 保留 L2 快速层语义（ruff C901/PLR0913 为兜底非替代）；②15 吸收台闭包提级为模块级 _check_impl（行为逐字节保留）+薄工厂保留旧 gate_id/priority 供历史测试与引用兼容（不再注册）；③in_process 册 7 条目原地升级（新 gate_id/factory+合并史录注释）+15 条吸收条目删除+计数 114→99；统一册生成器重生成；④测试 +7 冒烟（test_p4_merged_gates）+全量 3093 passed 零回归。新台静态边/ALGO_FLOW 锚/翻译全部沿承家文件既有登记（零新文件零新 token）。
9b0c31ab125 [st-gslim-20260923] [allow-mass-deletion:P3退役三台册除名 Owner E全批 被删条目引用文件已随批A 4b8fb00a55 盘上+HEAD双消失] P3退役批B·注册表除名+库门入HEAD（C1三台退役第2/2步，接批A 4b8fb00a55 文件删除）：①in_process_gate_registry 117→114 三条目删除+total_gates 头部史录同步；统一 gate_registry 生成器重生成+MANUAL_GATES 三块 deprecated 墓碑重定向锚（GATE-SCHEMA-HEALTH 先例，gate_id 历史可追溯）；fail_open_register 移 LIBRARY-COVERAGE 行；②library/ 三门（BLOOD-FLESH/TAG-VOCAB/STATE-VOCAB-REGISTRY）随批入 HEAD=治愈 HEAD 名册指向 library.* 而文件悬空的装载隐患（unlock 批 551839c7dd 遗留），三外锚 yaml 同批互指；③__init__ 急切 import：移除 library_coverage_gate，新增 registry_family 静态边（ORPHAN-MODULE 要求，auto_registrar 动态加载之外显式引用）；④registry_family/registry_mass_deletion_gate 随批（名册指向该路径；__all__ 补 Final=MUTABLE-CONST 清偿）；⑤ALGO-FLOW-LINK bug 修复：_reverse_anchor 对 git grep tree-ish 输出未剥 <rev>: 前缀致同批退役豁免永不命中（模块+镜像合法退役被结构性误杀，34 测试全绿+实战复验）；⑥_has_call_number 迁 ledger_schema+smoke 改挂（test_library_smoke 7 passed，前笔 422012d226 已落本体）。测试：registrar 对账 42 passed。
4b8fb00a555 P3退役批A·纯文件删除（st-gslim-20260923；C1三台退役第1/2步：门文件+测试+外锚镜像删除；注册表除名随批B紧随；ALGO-FLOW 反向锚豁免依赖 staged 删除集——algo_flow_link_gate HEAD: 前缀 bug 修复随批B落地） [allow-mass-deletion:P3退役三台文件先行 Owner E全批]
99ee6b8dd33 [st-gslim-20260923] P2 own化批（C3 名单 33 台，gate_audit_report_v1 §C3/Owner E9）：①_diff_helpers 新增共享拆分原语 _split_own_foreign（_build_own_scope 求交+外来 _audit_foreign_staged 审计+warn，own_scope=None 退化全量扫描保守面不改宽；ERROR_CONTRACT 永不抛，staged=None 归一空清单保 fail-open）——31 台各自内联同款逻辑会触发 FUNCTION-DUP/CAPABILITY-OVERLAP 自身门禁，故收敛为共享原语；②C3 名单逐台改造：staged 清单获取后即与本 session 范围求交，扫描/送检面只留自家，外来违规 warn+审计不阻断（§3.1 他会话在途违规不代修）；FOREIGN-CHANGE-DETECTION 例外保持全暂存（检测对象就是 claim 混入）；特例处置：ALGO-FLOW-LINK 检测面本就是 files 提交清单（own by construction，deleted_set 全暂存读仅为放行向豁免且外来删除物理随本 commit 落地=豁免语义正确，不改行为）；CREATE-GUARD 拆分置于 ARCH-037 命名检测后（其 rename 检测面在 git R 清单须全量）且不设早退（ARCH-031 governance 根 R-rename 反绕过检测直读 git 须恒执行）；CH-FINAL-GATE 双清单（扫描面拆分+added_set own 交集）；RENAME-DEPGRAPH-SYNC 按新旧路径归属拆元组；ERRCODE 维持 files 触发+基线差分（只拦本次新增，存量 warn 归属责任人，enforcement 已 own 等价）；③各台 [INVARIANTS] 头补 own 化声明。测试：commit_gates 2602 全绿；rule_bridge+gov_enforcement 591 绿；governance 其余 29 子目录分片全绿（2 失败=ulib3 既有 scripts 违规非本批改面，§3.4 不代修）。
d9a09b27644 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] error_code_registry.yaml 为门规修账（族3 error_code 一致性同步，非结构性重大修改）+ [unified][PLAN] WO-13 测试真账32条全闭环（丙线分包2续班，六族：绿12+修账20，联验388 passed）：族1 D38三库核验在册（fail_open_register登记+standard_family生成器6p）/族2 R24 factor_refs补齐核对无编造（38p）/族3 governance 9文件全闭合（六脚本常量化+naming爷爷条款+vocab v1.2.0收编10域+depgraph TYPE_CHECKING契约bug+error_code册）/族4 全库112处AGENTS死引用改齐58文件+施工模板/族5 cron基线逐槽位溯源追认（25→26/22→24/15→17，禁恒真化）/族6 假红8+1套跑不复现闭合（零测试代码改动）/族7 A14 77表资产册生成器重建（DDL-as-Code派生+CH实测+CAS保注释，DS-276..353共78张，册264→342，ROOR同步，token+module_translation同批）；TDM map 22节点note_confirmed（WO-14归置路径注释件算法零变化）；已清CAS tmp两枚+_wt_marker+stale WIP回滚 stash保全 [allow-mass-deletion:fail_open_register 账实修正重登记，门计数器亲验条目身份集零缩水，-124 行=同义条目合并格式重写非删账]
de2d8df0664 [ulib][st-gov-closeout-20260922] 批2/2 主批A-fixed（15）：library 域 10 py+coverage gate+commit_gates/__init__ 注册对同批+两生成器+tests 冒烟
81a06f16bbe W5-2 O-2(上批): decisiongraph_adapter.py 退役——源件+测试+注册表（裁定#371）
5c1107db842 [final3][P9c3][MAXEXEC] 立项判据门禁化：CREATE-GUARD 新增 merge_evaluation 缺失 warn+审计（裁定#375）
c007caac86d W7 股权穿透底座施工: entity_graph 六表施工件+DEPGRAPH-WRITE-PATH 白名单扩展
c6c2f0a69c5 fix(gov): GW 标记伪造与登记表净删面加固——hook 只认注册表会话键、ref-tx 取消 creation 万能豁免并审分叉、mass-deletion 补第三信号条目身份；两 .sh 如实登记残余攻面（车道 st-ff-gov2）
104d417bfb6 test: 冷库救回 src/tests 簇 11 件进版本保护——含修好 HEAD 自带 6 条红（救回件落地第3批·剔 session_worktree 配对件）
f45e205fad3 fix(gov): CH-FINAL-GATE 判据②表名截断治本——FROM 尾闸改回溯不可绕过形 + import 子句辨伪，测试源加 ast 合法性自检防空转（车道 st-ff-gov2）
8a8a3f92900 [FLOWTHROUGH][FF-16] 假通道收口车道 BRK-049/047/048/046：吞异常三轴分档+7处真处置、fail-open登记册、哨兵白名单收口
d6068fcd45d 扩 DEPGRAPH-WRITE-PATH 白名单：新增 build_node_bindings.py（ig_node_binding 绑定表写入器）
e8603527fe2 chore(gates): VOCAB-CHAIN 豁免面补 d5_architecture/validators 目录（对齐"检查器本就处理 SSoT 路径"既有豁免意图，裁定#335 W4c 校验器入库被拦实证）
b0c2999b80e fix(algo-flow-link): 门禁补"退役方向"判据——不可读≠已删除，镜像退役从结构性禁删变为可证明的清偿（#ARCH-326）
2ac7d910ed7 fix(gates): 落地面锚定态假红/失明治本——worktree→主仓判定收敛唯一真源(#ARCH-324)
ba17062144e fix(commit-gates): DEPGRAPH-FRESHNESS 在 linked worktree 内以主工作树缓存副本为权威——落地面 .runtime 锚定态停更致永久假红治本(#ARCH-324 实证③，33 件死信)，主树缺失才回落本地不放松 fail-open，权威优先同时封死植入本地新鲜副本逃逸；7 条双向钉经变异证明承重(3 红/27 绿)+镜像大白话与行号同步
d3b6518f47d feat(P3-前置 R-F): 同刻共开工意图声明 co_start_intent——判据①双方声明豁免、判据②预算不豁免
95f1832aeb5 fix(algo-flow-gate): #ARCH-323 判据装载失能治本——红蓝实弹第二发打死"门还在、牙没了"
4fc6b8ebab0 feat(resource_schedule): P2-a 第四查 check_pool_concurrency——C-8 同刻跨组盲区治本（排班 v2 W3）
025bdc0a572 fix(algo-flow): 红蓝实弹暴露的 ALGO-FLOW-LINK 哑火治本——体内"载体唯一"判据 + staged blob 真源（#ARCH-322/#ARCH-321①）
11214864bf7 feat(resource_schedule): P1-a 数据统一批——C-7 幽灵池清零/C-15 schtasks 第5源/L-1 台账pid join（排班 v2 W2）
c8a688e89e0 feat(resource_schedule): P0 卫生批落地——再生排产化+闸缺席/视图新鲜度告警+ROOR 顺修（排班 v2 W1）
b7d9328db61 fix(gov): 裁定#279 同盲区门禁家族清偿（#ARCH-316）——CAP-CONSISTENCY 补 HEAD 基线差分（他人 provider 欠账不再连坐）；SCHEMA-FILE-EXISTS 存在面改 git 仓库态+基线差分（磁盘观测面治本）；DOC-REF-BROKEN 内容读 staged blob+目标仓库态探测+staged 新文档不再被磁盘过滤漏检；CONSUMERS-ACCURACY warn-only 豁免登记（无阻断权不治）；新增 _repo_state_has_file 共享观测面 helper（ls-files/ls-tree 行数布尔判别）+ 9 例机证 tests/governance/commit_gates/test_repo_state_observation.py（他会话在途删除/磁盘陈旧两场景不误伤+真违规仍拦）；回归 schema22+doc47+consumers41+capval48+errcode19 全绿
834c5ffb9cd fix(algo-flow): P2-1 双真源两态判据分家治本（体外死块 / 体内第 2+ 块）+ 门禁接线 + 测试
d19747250cc chore(algo-flow): P2-1 死块清偿+语料图修复落地 03（90 件）
7185df98801 fix(algo-flow): P2-1 图完整性治本批（解析器三判据+门禁图可达+测试）
406bd08d558 docs(ruling): 登记裁定#279~#284（门禁观测面/队列死信语义/常驻进程纪元/EXP 判据禁挪/mid 准入/DS-275 切换门位）+ 回填#279 引用
abdf2446ab3 feat(algo-flow): P2-1 出仓波次 grp6 part1/2——480 文件（gov_enforcement / intelligence / nlp / signal_fundamental / ex_sor / alt_data / knowledge / infra_runtime 域子批）（重切小批 5/6，90 件）
d510ae586ab feat(algo-flow): P2-1 出仓波次 grp6 part1/2——480 文件（gov_enforcement / intelligence / nlp / signal_fundamental / ex_sor / alt_data / knowledge / infra_runtime 域子批）（重切小批 4/6，90 件）
5a5491c46dd feat(algo-flow): P2-1 出仓波次 grp6 part1/2——480 文件（gov_enforcement / intelligence / nlp / signal_fundamental / ex_sor / alt_data / knowledge / infra_runtime 域子批）（重切小批 3/6，90 件）
787fd269d53 feat(algo-flow): ALGO_FLOW 死块双真源四态收口（转正/留内联/prose 归并/镜像件清偿）+ ALGO-FLOW-LINK 第 3 判据（裁定#276）
604f4148467 fix(gov): ERRCODE 门禁观测面改 git index + HEAD 基线差分（治 4 小时全局连坐卡死）
2ddbbdeeb98 fix(gates+gov): 裁定#273 CloneGuard「触碰税」清偿治本——CAPABILITY-OVERLAP 对去 docstring 后 AST 等价的改动 fail-closed 豁免
5736dadfc74 fix(commit-pipeline): 三新坑排查修复——Mode A gitignore 可行动死信/Mode B pathspec 自愈重试/Mode C LOOKUP 进预检+孤魂 priority 让位
e9381d33dcf feat(commit-pipeline): 维护班四项核心手术——双锁统一+rule_catalog 保育+write_audit 盲区+worktree 警告（Owner 开工令全量执行）
cc3862512ff fix(gov)+test: ALGO-NOTE-SYNC 超窗归因漂移治本——行号精确锚替代 diff 窗内锚（GW5/GW4 实证缺陷，st-btfix-p17-20260916）
6ed8b2bbe2d feat(resource-schedule): B2 闸——排班冲突检测 gate 三检查+漂移+backtest-run 端点接 E0（MOD-RESCHED-GATE）
906496b808c feat(gov): P2-1 T3 ALGO-FLOW-LINK 门禁落地——ALGO_FLOW external 锚链接校验硬阻断（own-diff，Owner 批7 认可；st-btfix-p15-20260916）
6aee30f70bf feat(commit-pipeline): 晨班重建半批A——W1 修复+W4 三门禁 own-scope（create_guard 先行 35d792c0）
35d792c0983 probe import full detail single file
7a349b0d415 fix(gov_enforcement): TEST-SOURCE-CONSISTENCY 子模块 import 误报治本——from pkg import submodule 走文件系统解析不构成漂移
9005a38a7bc fix(gov): 图形库治理上报件5销项——幽灵锚点防复发双层治本+活体现行犯清偿：①apply_battle_map.op_add_anchor 写入时强制 target 存在性校验（复用 align_battle_map._GRAPH_COLLECTORS 同一存在性真源永不漂移；header 文档 --strict-target-check 从未实装的欠账兑现；源不可用 fail-open 与 align 惯例一致；anchor 674 连坐事故病根=写入零校验）；②GATE-BATTLE-MAP-ALIGNMENT 幽灵锚点硬→软降级（第一性原理：ghost=PG 状态非 git 状态，提交时点提交人无 agency 修复，宪法 §3 own-diff 原则；防复发已前移写入端，提交时检测 warn+指路 --remove-anchor；孤儿环节/缺失叙事保持硬=修复面在 git 文件）；③活体现行犯清偿：val2 覆盖率批残留两枚幽灵锚点 692/693（连字符 id MOD-INT-IMPACT-STREAM/MOD-INT-NEWS-CHAIN 与 depgraph 下划线真身 MOD-INT_IMPACT_STREAM/MOD-INT_NEWS_CHAIN 不符）按 --remove-anchor+正确 id 重挂（新锚 710/711，BM-RES-01 联动保全，重挂走 5a 新校验实弹通过）；④红蓝测试陈旧断言修复（sleeves 8→14 币圈扩容批未同步，断言改结构不变量 ≥8+权重和=1 承重）；测试 32/32 全绿，align 复测 ghost=0/orphan=0/narrative=0
ee6bc34aa89 fix(gov): 图形库治理上报件3销项——data_asset_registry 双 datasets 根键合并+REGISTRY-YAML-PARSE 扩面硬化（他会话在途批 0ba60dd0ef 落地后解锁，双键随其入库残留）：①合并施工=删 L752 事故残留（注释+空 null datasets: 键两行，2026-09-11 币圈会话插条目误建空键、PyYAML 静默取后者致前段插条目被解析层无感忽略），safe_write_text CAS+写前后 yaml.compose 节点树对账，259 条零漂移、22 根键全唯一；②门禁扩面=_WATCH_FILE 单文件改 _WATCH_FILES 档案表（capability_registry 全量断言/data_asset_registry parse+根键唯一两档）+新增顶层根键唯一断言（yaml.compose 节点树判重——safe_load 对重复键静默覆盖，节点树才同时保留两个，PyYAML 盲区由此补上）+教学信息更新；测试 12/12（双键事故原样复现阻断/两档放行/同批双文件不短路）
a287099285a feat(gov): 裁定#252——lock_files 锁存活=会话存活（红蓝 v4 F2 上游治本）
62cb4621be9 fix(gov): 红蓝 v4 修复批——F1 worktree 语法门禁回退解析 + F2 HELD-OVERLAP .ailocks 双轨 + v4 报告修复附录
665f3ad4777 fix(gov): TABLE-NAME-REGISTRY gate own-scope 化——他会话 staged WIP 连坐阻断治本（B5-4）
29c751b5d79 fix(shared)+fix(gov): anchor_main_root 识别 git worktree 链接治审计分裂（B5-1）+ FOLDER-CAPACITY gate own-scope 化治连坐
19073262a2a feat(gov): SYNTAX-VALIDATION gate refinement+修复日志——红蓝 v3 P0-1 批 2 收尾
e9e3dd6ff1c feat(gov): SYNTAX-VALIDATION gate（priority=49）——红蓝 v3 P0-1 批 2 治本：.py 语法错误入库硬阻断
c5c7ab1f135 probe cx4
62bcecbf8d5 fix(governance): C组 SSOT-REDEFINITION blackout 修复指引去搭便车陷阱（红蓝 v3 P1-3 配套文案）——两处'（在提交中包含该文件）'改为'（由持有该文件的会话提交修复后自动恢复）'，阻断受害会话把他会话在途编辑打包提交；纯文案零逻辑
4e7cdd83343 feat(gov): REGISTRY-YAML-PARSE gate（priority=54）——capability 注册表结构硬化治本：staged 版三断言（yaml.safe_load 通过/di_seam_exemptions 存在且末位/creation_tokens 为 list）任一不过 fail-closed 阻断+教学信息随报错透出（正确追加姿势=插 creation_tokens 列表尾勿错插 L883 嵌套同名键）；同病四连尾追悬挂致全库解析炸，口头纪律升机械防线；净零声明=本 gate 替代"提交前必验 parse"口头约定与四次人工热修流程（9ca0f62b95/1edeea81b4/a5883d01/94aa4111）；in_process_gate_registry 注册+total_gates 109→110 同步补记（历史三次漏同步教训在案）；6 单测全绿+auto_register 冒烟命中+CREATE-GUARD 双 token+depgraph 文件节点 13178268
44c516c3cd2 fix(gov): 提交链治理双修——队列删除分区死穴+PURE-ASSERTION own-scope 化+ battle_map 后事议题托管
ba7fa3a133a fix(governance): P1-1 伪造 GW 标记防御治本——广义标识符正则+自身放行/外来全拦+env 逃生废除（红蓝 v3 c224e15d63 实弹闭环）
a0e262e2608 feat(governance): FOREIGN-CHANGE trust-hold 自动信任——先编辑后 claim 的 AI 自然工作流不再每笔首撞
1350fe0862f feat(governance): 堵点推模式提醒横幅+P3 双瑕疵治本（红蓝复测遗留三项收口）
d50c2613b3c refactor(governance): SPLIT-COORDINATION 协议重设计——保护拆除正门=finish，落地≠失活
7033c393345 feat(governance): 堵点总账根治批——拆分协调协议 gate 143+TRACKED-DRIFT 连坐降级+堵点溯源审计+token 批量工具
f9a18c9be7d fix(gov): FACTORY-MAP 实弹暴露触发面路径归一根因——绝对路径恒 miss 治本（连带 INDUSTRY-CHAIN-MAP 同款修复）
b88b8fec5d8 feat(governance): 策略工厂图门禁第二批——FACTORY-MAP gate 142+九图挂轴（四关验收件闭环）
ebea698cfbc docs(gov): GOV-DOC-018 前缀约定文档清偿——14 个 T_soft 资格目录全部落地（清单2 收口）
ab549ab2e31 chore(legacy): 满贯批+队列增强遗留收编——死会话 worktree 正件归库（判读器定性·夜班收编批）
00f525d3486 refactor(signal_ashare): src 平铺债拆分——120→根46+7子包74（GOV-DOC-018 清偿·全仓引用同步）
adb585dbc14 fix(data): TRAE-082 symbol 约定 8 处存量违规清偿——4 表挂 exchange+symbol_canonical MATERIALIZED（Owner 指令"登记在案后续债全部执行"）
be204db2424 feat(crypto): DDL 真源入库——schemas 拆分批落位后收编（categories/crypto/ 子目录）
7aaaf430fc9 fix(gates): 消息级陈旧章节引用更新——AGENTS.md §X→宪法 L0 锚点（#ARCH-310 认证战役 P3，st-govreform-20260912）
4eccc568f3e feat(crypto): 影子 MVP 换源 binance.vision 落地——真实数据首采+影子判定首跑完成（v1.1.0）
71db09cc223 feat(gov): 全图全库对齐满贯批收尾 A——①registry_alignment.py 第二层共享校验核心（21 段 REGISTRY_SPECS/批量 depgraph 存在性 REPLACE 归一三种 ID 风格/字典 FK/CAND 转正链/治理双向/产业链字典四边，gate+align_all+pytest 三方同源；函数拆分≤15 过 NO-HIGH-COMPLEXITY）②INDUSTRY-CHAIN-MAP gate 141（图 8 产业链 git 侧工件：字典↔DDL↔引擎三方同 commit 同步）③layer2 回归测试 15 用例（基线红线+红蓝 tmp+gate 行为）④red_blue sleeves 断言对齐权威现状 ⑤decision_map A5 豁免 risk_tier_registry ⑥field_dictionary 测试结构检查委托共享实现 [no-lookup:continuation]
9c6a4c7b9e1 perf(gates): own-scope 第四批 NOQA-VALIDATION+MSG-EXPOSURE——共享暂存区连坐治本续（#ARCH-310，st-govreform-20260912）
b743c76afe3 perf(gates): DATETIME-NOW-FORBIDDEN own-scope 第三批——全暂存区路障治本（#ARCH-310 P0-2，st-govreform-20260912）
0e4efbfa371 ops(clone-guard): R1-R4 分层归位执行——onnxscript 卸载+索引卫生探针+回位条件登记+灰度计划（st-encfix，Owner 批准）
7e0a41aebbe perf(gates): own-scope×2 + DECISION-MAP 触发收窄——共享暂存区连坐治本（st-encfix 夜班①③，2026-09-11 Owner 全批）
d88dc53714c perf(commit-gates): ENCODING-SAFETY 批量化+_shared.constants 导入链惰性化——306 文件实测 1004s→秒级（st-encfix-20260911）
4aba1e3f371 fix(industry_graph+governance): quality_fix_p2 白名单三步纳入+S4/S25 满贯批留痕（st-igbe-20260911）——①DEPGRAPH-WRITE-PATH 白名单扩展（裁定#ARCH-DEPGRAPH_ACCESS_CONTROL 2026-09-11 补登 (l)）：quality_fix_p2.py 为 ig_* 图谱质量修复写入器（S4 废弃链闭环 merged_into 落款+落位 PIT 关闭/S25 链名结构修正/S12 误挂 PIT 关闭/S17 PIT 三件套补全），写 ig_chain/ig_node_company/ig_unlisted_entity，与 apply_depgraph.py 同类受控入口；gate _WHITELIST+docstring+错误信息三处同步，architecture_issue_registry 扩展历史+裁定+impact 三段补登，file last_updated 08-11→09-11；此前该脚本以孤儿 staged 状态触发 DEPGRAPH-WRITE-PATH 硬阻断（无 noqa 通道）卡死全项目提交（gate 连坐实证），归属会话已死无法自愈；②脚本新增 SQL 集中化为 _SQL_* 模块常量（§5.160.2，NO-BARE-SQL SQL_* 常量豁免口径），pre-existing 修复函数 SQL 不动（动了反制造新增行）；③S4 满贯批（聚氨酯/环氧丙烷/节水装备/氟化工/金融消费 5 条 deprecated 链承接落款+落位 PIT 关闭）与 S25 改名批（15 缩写扩中文全称+2 括号闭合+1 悬空尾，chain_id md5 稳定键不变）DB 效果此前已落库实证（引擎 S4=0/S25=0），本批为代码留痕落地。 [no-lookup:continuation]
91d1ae4246c feat(gov): P0 开工——①--wait 锁等待参数化落地 + ③DECISION-MAP 耗时口径纠偏（st-perf-plan-20260910，方案 §7 施工清单执行）
5546da18698 fix(gates): 5 个内容扫描型 gate 只查自己推广+参数化批量用例（T5 余量批 3）
3e85c3d87d1 fix(gates): NO-BARE-SQL 只查自己推广（#ARCH-GATE-OWN-SCOPE-001，T5 余量批 2）
2be5e95752b fix(gates): NO-GOD-CLASS 只查自己推广（#ARCH-GATE-OWN-SCOPE-001，T5 余量批 1）
551b8d09993 fix(gates): UNDEFINED-NAME 只查自己推广（#ARCH-GATE-OWN-SCOPE-001，T5 步骤 3/4）
ff055b768c3 fix(gates): NO-HIGH-COMPLEXITY 只查自己推广（#ARCH-GATE-OWN-SCOPE-001，T5 步骤 2/4）
b3d80624272 refactor(gates): session-scope helpers 提取至 _diff_helpers 共享模块（T5 推广步骤 1/4）
a85729effd3 [no-lookup:gate-fix] 本次 commit 前已按 TRAE-065 调用 RuleDiscoveryServer（st-clearance-night, file_write）；施工沿用既有 gate 族惯例（protected_paths 审计样板/逃生标记先例/_diff_helpers 共享），无规则盲区。
84ebfeca3b8 fix(gov_enforcement): T4 提交门禁"只查自己"改造——并发夜他人 WIP 不再锁死所有人（#ARCH-GATE-OWN-SCOPE-001）
ce92f48e9ff fix(gov): ALGO-NOTE-SYNC 注册两处治本——懒加载 decision_map + priority 76→62（后到者让位）
47ab163cbf4 feat(gov): ALGO-NOTE-SYNC 门禁——算法锚与大白话同步绑定（Owner 2026-09-09 任务三）
b0a0aef7854 fix(governance): 词表门禁终清零——审计遗留 4 WARN+5 noqa 丢失回归修复
4a593e1f490 chore(governance): 审计期后台派生波收编⑦——solo-20260905-alignment-hardening 会话收尾残写收编（check_decision_map/business_registry_gate/decision_map，与已落地 b9c60ef24b 对齐硬化同内容族；session 已注销无认领，RULE-TWENTY 写完即提交） [no-lookup:continuation]
d4f4a89b0bd Merge branch 'ai/AI-AUDIT11-002/task-audit11-recheck' into dev
b9c60ef24bc feat(governance): 对齐体系硬化——七图对齐闭环+业务库入库门禁+作战地图三类升硬（G1-G3 全建造）
d02d3944abe fix(gov-code-quality): remove dead import is_test_exempt from arch_reference_gate (AI-AUDIT11-002 复审轮)
39de5021654 feat(gov): FRONTEND-MAP gate 落地——frontend_map 对齐接入 commit 链，六图对齐全自动闭环（Owner 2026-09-04 裁定「现在做」）——priority=137 硬阻断（确定性校验非启发式：R0 id 重复/R1 backend_ref 悬空 fail→阻断；YAML 异常 fail-closed 真源损坏须先修）；校验逻辑单一真源=check_frontend_map.py 动态复用（align_all 同模式，禁复制规则防双真源）；depgraph 全量重扫/翻译真源/创建令牌三登记；gate_registry 156 条；45 测试全绿；TRACKED-DRIFT=后台 architecture health 守护写 latest.json 非本 commit 文件（留痕） [no-lookup:continuation]
82c69c9912a [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] Owner 2026-09-04 要求补做红蓝对抗 test(gov): FRONTEND-TRUTH-SOURCE 红队 9 手法实测——R1 单行密集数组/R2 多行键值块/R3 嵌套对象行/R4 HTML 内联脚本四处真实击穿已修复锁死（花括号配平判定+密集行计数+键值块状态机+Check A 纳入 .html）；R5 widgets 伪装/R9 vendor 藏匿=接受风险文档化（目录契约+评审兜底）；R6 注释行放行/R7 XHR 异因同罚/R8 改名逃逸失败=语义边界正确；TRAE-086 门禁描述同步+SOP v1.5.1 Checklist 第 13 项（前端任务必做后端盘点）；41 测试全绿（32 蓝+9 红） [no-lookup:continuation]
a80cbb8ece6 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] Owner 2026-09-04 本会话拍板扩展 TRAE-086（三选一裁定：TRAE-086+SOP 双挂/Gate warn 起步/演示数据保留但收紧）feat(gov): 前端真源接通铁律落地——TRAE-086 v1.2.0 §truth_source_wiring（前端不许自建数据世界：施工前后端盘点四步 取数清单→后端三查→三分支决策→接线验收；演示诚实纪律收紧=只许回退态须明示+15s重试）+ FRONTEND-TRUTH-SOURCE gate（priority=136 warn 起步：内联数据数组启发式+零接线扫描，目录契约豁免，审计 jsonl，_HARD_BLOCK 一行升硬）+ SOP Step 3.5 双挂；paired_gate_id 陈旧引用修正 FRONTEND-SMOKE→FRONTEND-TRUTH-SOURCE（gate_registry 155 条再生成）+翻译真源/创建令牌补登；32 单测全绿+动态注册冒烟过 [no-lookup:continuation]
e1b6b73a62a style: ruff format 全量一次性成型 CAND-GOVTEST-002 清零 冻结窗口 零语义变更
fb90a488e3e docs(algo_flow): GOVTEST-003 第8批 244 模块补登（长城任务）
f7c951783c4 feat(governance): 08号文 Phase 1 队列联动三件套+升硬联动——级联标记/死信重入队/done TTL（MOD-GOV-046，GP1 第四波，AI-GP1-W4）
3e1e9bd7f6d feat(governance): CAND-GOVSEC-001 批5 三件——观测期收官翻硬拦+日志洪峰治本
5b54bdd3fbd feat(data): 15/17号数据治理——trading_calendar.trading_days_in_range真源helper（XSHG三级降级纯本地）接pit_manager Embargo注入位/CapabilityContract增expected_market+expected_variety/复用既有capability_symbol_gate接线CAP-CONSISTENCY门禁双检查（回滚自研重复实现）/internal_compute命名盲区收编（行为等价）/data/manual/calendar_event_manual.csv台账59行（FOMC48+两会中经10+印花税）白名单合并覆盖12类；2308测零新增红；#ARCH-203 [no-lookup:batch-treatment]
7a1ff92c986 feat(governance): CAND-GOVSEC-001 批4 四件——①ops_guard audit-only 观测模式（ZEPHYR_OPS_GUARD_AUDIT_ONLY=1 时判定应拦落 inprocess_would_block 审计+would_block 计数实际放行）+ install_inprocess_enforcement_audit_only helper 推广五治理入口（git_commit/session_worktree CLI/commit_queue drain/pytest conftest/sweep 库入口，观测期不硬拦）②sweep 删除遥测前置（_log_worktree_delete phase=begin 含调用栈，与 done 成对；修 format_stack [:-2] 误砍调用方帧为 [:-1]）③worker 并发闸门治本（launch 临界区 _acquire_launch_lock 跨进程文件锁互斥 + _count_inflight_workers 口径扩已注册 worker∪新鲜 pending/running status 按 sha8 去重，闭合 spawn 前 TOCTOU 缝隙；删除旧 _count_active_workers）④GATE-GIT-GUARD-BYPASS same-sha 自指 reset 排除（reflog 倒序链比对下一行 %H，git reset -q 等 HEAD 未移动操作不再误报，detail 留痕排除计数） [no-lookup:continuation]
67ef4de6a07 feat(governance): CAND-GOVSEC-001② HOT-FILE-BASE-FRESHNESS gate + claim_head 锚点 + file_utils CAS 补强
7a73e0499e6 feat(governance): GATE-ERRCODE-CONSISTENCY 门禁 in-process 化（#ARCH-136，堵 gateway 主通道结构洞）
f60fd24dc68 fix(gov_enforcement): CONSUMERS-ACCURACY orphan 检测补识模块级常量定义（#231①，P0-6③）
0be658f55d4 style(ruff): AI-NIGHT-001 波3 CAND-GOVTEST-002 ruff format 全量成型 4/12（src/zephyr/gov_enforcement）
58746c434f5 fix(gate): #ARCH-131 BLUEPRINT-AMODULE-CROSS-CHECK normalize 过度阻断治本
b1add31b6b5 style(governance): 循环审计 R1 杠杆#3——ruff 安全修复全量落地（1914 处：I001/F541/W292/W293/UP006/UP045 六码）
36455c1ccf0 fix(governance): B4 治本——PROTECTED-PATHS merge 场景审批转置（分支侧 [ARCH-APPROVAL] 核验，05/08 两域被拦实证）
4dd5c4a030c fix(governance): AI-00 移交两件统筹事项治本——①depgraph 重建命令文案修正（--force 裸跑不写库=假成功，正确=--output-db depgraph --force；RENAME-DEPGRAPH-SYNC 门禁提示+audit_rename_completeness 修复指引+docstring 三处）②S4 module_id 头注注入器 _archive 归档件豁免（_classify_headerless_files 路径段级豁免，归档件不再注入 [BLUEPRINT]+permanent） [no-lookup:gate-fix]
64832e019ef Merge branch 'ai/AI-AUDIT19-001/task-audit19-autofix' into dev
8f0235f7b08 Merge branch 'ai/AI-AUDIT11-001/task-audit11-autofix' into dev
a0cde45d1ff test(reorg): AI-AUDIT19-001 审计域治本——①测试目录重组（根目录散置测试按域归入 backtest/ex_core/governance 子目录）②失效重复测试清除（bridges/context/governance/infrastructure/llm_security/observability/orchestrator/trading/utils 存量孤儿）③contract_test_anchors 刷新④blueprint_registry.yaml 派生退库⑤合规/治理/体制/风控域 blueprint 与翻译注册表对齐⑥commit-gates _diff_helpers 幻影行号同胚修复（主仓 4a3d5a3b 同治本） [no-lookup:continuation]
4a3d5a3b130 fix(commit-gates): diff 行号解析幻影空行治本②——subprocess text=True（universal_newlines）将 HEAD 侧 \r\r\n 删除行翻译为 \n\n，切出裸空行落入 else 虚增行号（实证 +457/文件）；解析器跳过裸空行使 added 行号与 AST 豁免精确对齐（migrate_data.py 验证：118/119/133 全对齐） [no-lookup:continuation]
ae85cfb036e fix(commit-gates): _parse_diff_with_line_numbers 幻影行号治本——splitlines() 按 \r 再切 \r\r\n 删除行致 added 行号膨胀（实证 migrate_data.py 真 118 行报为 575），AST SQL_* 豁免与膨胀行号失配引发 NO-BARE-SQL 误报；改 split("\n") 使行号与 AST 干净解析对齐 [no-lookup:continuation]
835432f1dcf fix(governance): AI-AUDIT11 审计治本——复活 4 个死 in-process gate + priority 撞号让位 + 表头/时区/注释漂移修正
6f1c2d71b46 fix(governance): AI-AUDIT11 审计波 R1 治本——GATES_DIR 真源漂移 + log_db_failopen 契约对齐 + 40 文件 CRLF→LF 归一 [no-lookup:gate-fix]
fa25c19e491 feat(governance): fail-open 敞口治理 B1+B2 全量落地（tracker #116 / #ARCH-119） [no-lookup:gate-fix]
16c3dcf2c9a Merge branch 'ai/AI-TDEBT-001/task-test-debt-cleanup' into dev
e1c590201c5 fix(commit-gates): added 行判定统一加 --ignore-cr-at-eol（13 门禁全量清扫）——EOL 规范化提交不再误报存量违规
fc00b66ad7e fix(DATETIME-NOW-FORBIDDEN): added 行判定加 --ignore-cr-at-eol——EOL 规范化提交不再误报存量违规
d5d5cab40e7 Merge branch 'ai/AI-WDOG-001/task-worktree-write-integrity' into dev
6e3808db496 feat(governance): worktree write-layer integrity four-layer fix (#ARCH-WORKTREE-WRITE-INTEGRITY-001)
b4ecf967c62 fix(governance): REGISTRY-CODE-ANCHOR priority 106→129——UNDEFINED-NAME 撞号让位
66a90c1c8e4 feat(governance): 业务注册表↔代码双向索引门禁A/B 落地（#ARCH-BREG-002 分域真源裁定）
176199347e0 fix(tests): 清偿 SyntaxError 收集错误簇——10 文件模块 docstring 补 r 前缀（#63）[no-lookup:test-fix]
086d0e24e4d feat(governance): #ARCH-RECONCILER-AUTO-DELETE-GOV-001 T2 观测与准入闭环——SessionRegistry 锚主仓治本（worktree 内构造自动锚定主仓：消除 claim 写 worktree registry vs 三证读主仓 registry 的双 registry 分裂，合法 worker 被证3 误拦 2 例实证修复；143 session 测试无回归）+ ops_guard 审计统计（_AUDIT_STATS：judge/allow/block/audit_failed 计数，get_audit_stats 公共接口）+ worker status 落盘 ops_guard_audit_stats + RECONCILER-HEALTH 增删除审计覆盖率检查（24h audit_failed>0 即 warn——覆盖率=100% 指标化落地）+ T2② 删除/移动类动作全量落盘核实（coord WIP 已随 e63e8859 入库）+ 测试 85 全绿（新增 stats 计数自洽用例）[GW:AI-RCN-001:overlap] [GW:AI-RCN-001:multi-domain 留痕——T2 观测链原子事务]
5f81d28adfd feat(governance): #ARCH-RECONCILER-AUTO-DELETE-GOV-001 T1③ 静态扫描门禁+红队验收——新建 RECONCILER-FILE-OPS gate（priority=117 注册制：staged 治理代理代码新增裸删除/移动原语即阻断，防收敛回流；ops_guard.py/tests/# ops-guard-exempt 豁免）+ 红队验收测试 18 项全绿（注册强校验/未声明阻断+critical_warn/已声明直通+审计/reset 无泄漏/递归保护区双保险/in-process patch 幂等+裸删保护区阻断+白名单放行+Path.unlink 覆盖+阻断审计落盘/回收站容量封顶/静态扫描检出与豁免）+ depgraph 登记（MOD-GOV-044 node_id=9619955 generated）+ ORPHAN-MODULE 静态锚定 + 三登记 [GW:AI-RCN-001:overlap] [GW:AI-RCN-001:multi-domain 留痕——gate 机制+注册表+测试原子事务]
bb3a91d48a4 feat(governance): #ARCH-RECONCILER-AUTO-DELETE-GOV-001 T2-T6 全层落地——T2 worker 启动三证（锚定存活/payload 新鲜度/session 活性，缺一拒启）+删除/移动动作全量 [DELETE-AUDIT] 落盘；T3 双裁定书 ttl→permanent 且自 docs/_working 临时区迁入 02/04 永久区（FILE-PLACEMENT-TTL 对齐，doc_type=audit_report，入站引用全同步）；T4 #55 治本：flags.py 审计写迁 .runtime/audit/（51MB feature_flags.jsonl 等 5 个历史 tracked 审计文件退跟踪，data/audit_logs/ 全目录 gitignore）+#ARCH-PRECOMMIT-STASH-ADAPT-001 立项（65 号 §10）；T5 告警卫生：GATE-RUNTIME/TMP-CLEANUP 锁定跳过=clean 语义（PermissionError 不再计 errors）+RECONCILER-HEALTH 横幅 24h 内容签名 dedup；T6 I-GOV-2 对齐注记+wipe 裁定书排除项勘误；顺手修 #55 存量 blueprint_registry 158→163 漂移（sync --write）；9 新测试、关联测试主仓 107 项实证全过 [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001]（.gitignore 增 data/audit_logs/ 全目录禁跟踪——#55 治本裁定） [no-lookup:continuation] [overlap 留痕：全部改动为本会话 T2-T6 施工产物——主仓施工期间遭 base_sync reset --hard 两次抹除（#56 机制实证），自 pre-commit 存证 dangling commit c4f970ffad 三方恢复入本分支，无外来变更]
d771ec1ab6b chore(backup): merge AI-GIT-001 前 dev 工作区备份——前序会话 #ARCH-DATA-016 tqcenter 快照签名+PascalCase 键映射修复、capability_consistency_gate 增强、chart_pattern_registry/feature_flags 运行时落账全量落袋（0 活跃会话实证认领，防 wipe 类丢失）[no-lookup:continuation]
58aced8cbf7 fix(governance): worktree 环境断层治本三件套代码重打——#ARCH-WORKTREE-ENV-001 P2（并发冲稿重放）
157804a7ed3 fix(governance): depgraph 双态转换死锁治本——同身份 UPDATE 通道（#ARCH-70）
6e39c083d0d feat(algo-flow): D_GOV_CODE_QUALITY 域 6 模块补 ALGO_FLOW docstring 标记（§4.16 全量落地步骤③）
e0bbc419680 docs(gov): worktree_required_gate INVRTARIANTS + docstring 补 worker 排除说明（P3-2） [no-lookup:gate-fix]
765c28fd4f0 fix(gov): WORKTREE-REQUIRED gate 排除 reconciler worker session（#ARCH-RECONCILER-WORKTREE-RACE 治本） [no-lookup:gate-fix]
cfa276284be feat(governance): 五图对齐治本——术语统一 + align_all.py 统一入口 (ARCH-ALIGN-UNIFIED-001) [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] [no-lookup:continuation]
9f7f0835168 feat(gov_enforcement): FOREIGN-CHANGE gate 增加 post-claim 修改审计（P1 时序缺口治本）
9bf83e837ea feat(gov_enforcement): 新增 COMMIT-SCOPE gate 防跨域混合提交（13a5e1d512 治本）
996bd1d2512 chore(derived+sync): 派生产物批量同步 + 少量源码跟进——blueprint 元数据 + registry catalogs + project_handbook AUTO 段
386ccc26f32 fix(import_integrity): _extract_sys_path_dirs 模块级变量优先——函数内 global 重新赋值不覆盖模块级初始值（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 延续）
c86b0a57dfb refactor(import_integrity): 提取 _is_path_func 公共函数支持三种 Path 构造形式（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 延续）
b481f862a1e fix(import_integrity): 识别跨文件 REPO_ROOT 常量 + while 向上找 .git 仓库根模式（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 延续）
af7e2125a96 fix(import_integrity): _get_sys_path_arg 提取 sys.path.insert/append 路径参数 + 多层变量回溯 + registry_master_index 同步
b20d5f20560 fix(import_integrity): _extract_subdir_from_binop——BinOp Div 链取最左常量作为 subdir，支持 comprehension if 条件中 BinOp Div 模式（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 延续）
0674e7150e4 fix(import_integrity): _resolve_path_expr 增强——BinOp Div 路径拼接 + 嵌套 .parent 递归 + 多层变量回溯(depth≤2) + _try_resolve_next_parents_search 用 _resolve_path_expr 支持 .parent 链变量间接形式（#ARCH-IMPORT-INTEGRITY-SYSPATH-001 延续） [no-lookup:continuation] [--adopt-prior-work]
e28cda23930 feat(regime+governance): regime 特征源码实现 + import_integrity_gate 裸 Path 检测 + AGENTS.md §10.4 + 审计基线脚本
3540579c88b fix(gov_enforcement+regime): _diff_helpers 去重消费方落地 + 命名显示测试 + regime 趋势特征测试
f1a1eae6603 feat(clone_guard+regime): Phase B 并发编排器 + 筹码分布引擎蓝图 + _diff_helpers 去重 + 命名显示修复
c0d487ad4f7 feat(clone_guard+regime): 合入主干——Phase B 聚合器/ast-grep 适配器 + regime_feature_builder 蓝图 + 治理修复
191a17432fc feat(regime+integrity): regime/Kelly 5模块源码 + import_integrity_gate sys.path 注入识别
e29f64f11e7 feat(clone_guard): Phase A MVP——CloneGuard 多引擎克隆检测集成防御体系
a83cc71945a fix(arch-gate): 补全 INVARIANTS + docstring 的 L3 说明（审查遗留修复）
81c6bb2bce1 feat(arch-gate): 应用铁律#7 冻结条款 + 添加 L3 新条目数字制检测（Phase 2）
20106b11fb7 fix(audit): 审查第1-2轮治本修复（P-4/P-5/P-6/P-8）
72c0780104d fix(gate): depgraph_write_path_gate 错误信息+docstring 白名单补齐 add_acquisition_fields.py
7704f3a65c7 fix(gate): DOC-REF-BROKEN 修 file:/// 误报 + 加草稿区跳过目录
1c172fb3002 feat(data): FRED/WorldBank macro data provider (#ARCH-EDB-EXPAND) [no-lookup:continuation]
f24202ddbd1 feat(gov): Phase 3 密钥治理纵深防御——新增 NO-SECRET-HARDCODE 门禁前移密钥泄漏检测
191279e3aea feat(gov): Phase 2-S3 密钥治理硬化检测——新增 SECRET-REGISTRY-CONSISTENCY 门禁 + NO-BARE-GETENV diff-aware 增强
cc665242edd fix(governance): depgraph备份补齐+L1铁律二元化裁定 (#ARCH-L1-RULE-ENFORCEMENT-GAP) [no-lookup:continuation]
9b754eda48f fix(governance): trae_071 v1.2.0 SSoT收敛 + TEST-RESIDUE-SSOT防复发门禁 (#ARCH-TEST-RESIDUE-CLEANUP-001 #1-#5 治本) [ARCH-APPROVAL:ARCH-MODEL-LIFECYCLE-001] [no-lookup:continuation]
98c8493c5c6 [ARCH-APPROVAL:ARCH-DOC-NODE-ID-RULE-001] [no-lookup:gate-fix] refactor(gov): node_id/edge_id 硬编码检测正则三源→单源治本（#ARCH-DOC-NODE-ID-RULE-001 P3）
7891efb8d45 feat(governance): BLUEPRINT-NODE-ID-HARDCODE in-process gate 补齐 GitCommitGateway 路径 node_id 硬编码拦截
64f85b3a1fd feat(gov): WORKTREE-REQUIRED gate (#ARCH-WORKTREE-GATE-001) — worktree 隔离强制门禁治本
e0dcd562b87 refactor(governance): 删除14个纯re-export shim文件+消费者import改引canonical路径
40d5a93d07d [GW:manual] fix(depgraph): file-sync 补漏——21 文件 6 对 old→new ID 替换
c9d701e1fdb fix(ruff): 修复 8 个 ruff 错误 (BLE001/F541/无效noqa) [GW:manual]
41781ffd413 feat(gates): 新增 DERIVED-FILE-DELETION-PROTECTION 与 PROTECTED-PATHS 双 in-process gate + 修 MODULE-ID-CONSISTENCY 同模块误碰撞
e7deda8c1f3 fix: 全量文件头 module_id 对齐 depgraph — 53域分批修复完成 [GW:manual]
bda3f8912f4 fix(D_GOV_ENFORCEMENT): 文件头 module_id 对齐 depgraph (28 fix + 78 add) [GW:manual]
9c039f956be fix(D_GOV_DOCS): 文件头 module_id 对齐 depgraph (0 fix + 2 add) [GW:manual]
b1ac88468f3 fix(governance): 补登记4个ARCH议题+TRANSLATION-COVERAGE文档化+Layer编号/计数修正
d8c01738f83 feat(translation-coverage): 观察期结束转硬阻断 _OBSERVATION_PERIOD=False (#ARCH-TRANSLATION-SCOPE-NARROW)
389642bcc23 fix(translation-coverage): 收窄 gate/reconciler 范围豁免非业务脚本(#ARCH-TRANSLATION-SCOPE-NARROW)
d5d9523bfe3 feat(gov): TRANSLATION-COVERAGE 四层防御——新模块大白话简介强制写入闭环 [no-lookup:continuation]
450621f0333 fix(panorama): 清零四图对齐告警 — 删 stale dataflow 孤儿 + 补 20 蓝图 design_maturity
2a75aeba8a8 fix(audit-02): 补全 ARCH-REFERENCE commit-time 正则 S 变体 + 完成 REFERENCE_TEXT_EXTS 收敛
d940aa1ec96 feat(h1-redis): 步骤7——H1 Redis 热缓存 build_status→stable/production 终态 [no-lookup:continuation]
2586089797a fix(gov): Stage 4 公共化回归收尾——commit gate 测试 2→0 + 修 _is_session_registered .get 真 bug
3466aa4b2ed fix(gov): Stage 4 公共化回归修复——commit gate 测试 8→2 failed（A+B1+B2 共 6 个）
eb844da73e6 feat(battle_map): 第二批锚点迁移落地 + 第四全景图 + DEPGRAPH-WRITE-PATH 白名单扩展
b883925867e feat(doc-gen): plain_zh module translation SSoT + gate public alias fix [no-lookup:continuation]
388786c1bfa fix(governance): resolve 6 vocab-hardcode CI violations (#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase A/C) [no-lookup:gate-fix]
bf85be5ec81 docs(architecture): 清理原则文档体系收尾——删7份原则文档+内容迁移至YAML真源+引用同步
2bcbe74548d chore(arch): 彻底清理 generate_domain_dependency_diagram.py 残留引用 (5注册表+AGENTS.md+target_arch+panorama_registry重生)
83d31a7a6d5 R5 私有断言消除完成 + 公共模块别名创建
76ffb6634c0 refactor(r5): 公共化批次 - importlib/importorskip/factory 解析增强
2b69b08a2e6 fix(gate): BARE-SUBPROCESS gate 引用传递检测补齐 + #ARCH 引用登记 [no-lookup:gate-fix]
61c6163d5a1 [GW:R5-batch43] R5 私有断言消除: test_ssot_gate.py + 关联文件 (47 accesses)
1c188c9e8c8 [no-lookup:continuation] R5+R6: publicize foreign_change_gate/rollback_core/pipeline_orchestrator + dedup _wt_run_git
e23f74d3d39 refactor(governance): Stage 3 收尾——全量裸 subprocess 路由到 process_pool + codemod 损坏修复
9371a46e172 fix(governance+data): 治本修复5项——bare_subprocess fail-closed + DIP注入 + iFind重连复原 + 测试解耦 + datetime对齐
77c91e5d9fd fix(governance): 治本 GATE-DEPGRAPH-OPS critical_warn——SAVEPOINT 隔离备份表清理 + SyntaxWarning 修复
5f85fbff0db refactor(governance): 归档 architecture_debt_registry + TTL/EXEMPT-ZONE gate 矛盾治本
d0bfe67f5b9 feat(gov): 5 warn-only 维度升级为硬 commit gate——ASYNCIO-RUN-IN-CONTEXT/MUTABLE-CONST-WITHOUT-FINAL/OPEN-WITHOUT-WITH/ZEPHYR-ENV-DIRECT-ACCESS/MCP-VERSION-FIELD [ARCH-WARN-TO-HARD-GATE-BATCH] [no-lookup:continuation]
4ed7efae321 fix(governance): ARCH-MM-002 迁移 bug——14 个有代码文件 [MATURITY] design→production
64b2b3bc3c9 #ARCH-SSOT-REFERENCE-INTEGRITY-001 Phase 1+3 治本收尾
159625775a9 fix(blueprint): resolve all 3 residual issues from Part 2 audit [no-lookup:continuation]
44c890d8bfd ARCH-MM-002 Phase 2-9: design_maturity 两档化完整迁移
2e8b9ff78f5 ARCH-MM-002 Phase 0+1+5: design_maturity 3档→2档 + [MATURITY] header 批量迁移
2bf37002e59 fix(governance): 治本修复 [MATURITY] header/DB design_maturity 不一致 + apply_depgraph.py ARCH-MM-001 gate
fe101cb790c fix(governance): fix last [BLUEPRINT] UNDERSCORE violation (MOD-GOV_bypass_policy -> MOD-GATE_ENGINE)
dd8992b99d1 fix(governance): CONSUMERS-ACCURACY orphan fix - replace consumer func name with actual exported funcs [no-lookup:mechanical]
48e2633b1c6 refactor(blueprint): uppercase [BLUEPRINT] module_id segments to fix format violations
9ebae289d5d fix(governance): DASH->UNDERSCORE module_id fix (capability_lookup_bypass_policy) [no-lookup:mechanical]
2c7fff4c56b fix(governance): final DASH->UNDERSCORE module_id fix (2 files) [no-lookup:mechanical]
76cf77d9ed6 fix(governance): DASH->UNDERSCORE module_id format fix (48 files) - GATE-BLUEPRINT-ID-LEGACY violations to 0 [no-lookup:mechanical]
5a7192d97f0 fix(governance): convert [A_module] UNDERSCORE->DASH (v10 batch 1/1, 2 files)
1ede3a0912b fix(governance): convert [A_module] UNDERSCORE->DASH (v10 batch 1/1, 37 files)
791be3b5132 fix(governance): convert UNDERSCORE→DASH (v8 batch 1/5, 10 files)
3d7091906d8 fix(governance): fix remaining 3 test failures + prior session fixes (blueprint_amodule gate malformation regex, naming whitelist, bridge/contracts/anomaly dual API, adversarial 006-009, atomic_tx sanitizer, workspace_hygiene auto-sync, bare_sql escape) [no-lookup:test-fix-batch14]
458e57b37ce fix(governance): CAPABILITY-LOOKUP bypass 治本——gate-time 白名单检查 + 共享策略模块 (#ARCH-066)
de07b656277 fix(governance): convert [A_module]/[BLUEPRINT] UNDERSCORE→DASH (v5 batch 1/4, 100 fixer-only files)
91306fd0d0f chore(reconciler): batched auto-commit (5 reconcilers) by GitCommitGateway post-commit
de11babf954 feat(gov): #ARCH-CH-024 Phase 5 收尾——TABLE-NAME-REGISTRY gate 升级 warn-only→block
d1b3171f7d1 feat(gov): #ARCH-CH-024 Phase 5 收尾——TABLE-NAME-REGISTRY gate 升级 warn-only→block
89f21c27131 [no-lookup:arch-module-id-unify] fix(arch): unify module_id format truth source to is_valid_module_id (#ARCH-MODULE-ID-FORMAT-UNIFICATION-001)
528740c39cb fix(gov): "全部根治" 2 条 pre-existing 告警——CAPABILITY-LOOKUP 假阳性 + PANORAMA TOCTOU 竞态
31bbe521631 fix(gov_enforcement): 治本 2 条 pre-existing reconciler 告警
605c16f6cc3 feat(gov): #ARCH-CH-024 Phase 4 TABLE-NAME-REGISTRY gate + Task C g_trae_059 修复
ce271370716 fix(governance): convert [A_module]/[BLUEPRINT] UNDERSCORE→DASH format (batch 3/9, 200 files)
b6a18d29c0c fix(gov): #ARCH-CONSUMERS-ACCURACY-004 治本——CONSUMERS-ACCURACY baseline 686->0 [no-lookup:continuation-of-approved-remediation-plan-算法改进+数据修正-非新功能] 算法改进（consumers_accuracy_gate.py 8 项）： 1. _ABSTRACT_CODE_PREFIXES 新增 OPS- 2. _FILE_EXTENSIONS 扩展为 15 种文件扩展名 3. _classify_consumer_format 新增 4 种分类逻辑 4. _check_filepath_exists 新增 basename 递归搜索 5. _extract_function_names_from_parens 重写为严格标识符验证 6. dotted 分支新增连字符到下划线转换 7. orphan 检测新增 ClassDef 收集 8. scan_all_for_consumers_accuracy 新增 noqa 识别
031ccf0fa68 fix: remove non-Zephyr skip from directory_contract_gate + fix str/bytes decode (tests SSoT expects fail-closed not skip) [no-lookup:gate-skip-removal-dcr]
ae01b5fd7fe fix: remove non-Zephyr project skip from session_required_gate (12th gate) [no-lookup:gate-skip-removal-batch]
ce7e8e170b6 fix: remove non-Zephyr project skip from 12 commit gates (tests SSoT expects gates to run in tmp_path repos) [no-lookup:gate-skip-removal-batch]
54d862dee81 P1-1 consumers_accuracy_gate.py: phantom 检测按格式分类 P1-2 capability_overlap_gate.py: _STOP_WORDS 过滤 gate token 96 tests pass
af51d631e67 merge session/sess-38120-20260722021724
f897abea696 P3: [BLUEPRINT] header format unify UNDERSCORE→DASH (11 files) + apply_depgraph.py IndentationError fix
5f1f7f1399a fix(redblue): 8个红蓝极限对抗测试问题修复——noqa密度检测+快照TTL清理+线程安全+文档化 [no-lookup:红蓝对抗修复扩展现有gate/metric非新功能]
54fb26189b1 P1 gate+registry: BLUEPRINT-AMODULE-CROSS-CHECK gate + arch reference registration [no-lookup:continuation-of-approved-remediation-plan]
99c3564e551 fix(create_guard): worktree stale HEAD 误报治本 (#ARCH-CREATE-GUARD-STALE-HEAD-001) [no-lookup:fix-create-guard-stale-head-bug-investigated]
d3fa9816562 merge session/sess-66092-20260722002627
7f598f15e7f feat(gov): #ARCH-STASH-ACCUMULATION-002 5 Step 治本施工
e103912eb16 #ARCH-STASH-ACCUMULATION-001 Phase 1/4/7 + #ARCH-STASH-ACCUMULATION-002 施工路径裁定
908e9730e20 #ARCH-CONSUMERS-ACCURACY-003 Phase 2 / #ARCH-ISSUE-RESOLVED-INTEGRITY-001 治本落地
9c731465e4a fix(governance): #ARCH-ANY-GOVERNANCE-001 Phase 2 — replace 71 bare Any annotations
0ba4d04173a fix(governance): batch 4 — multi-cluster test fixes (31 tests pass)
13bd00eb172 Merge session/sess-46560-20260721162044: 12维度审计自动化 4 gate + 2 reconciler [手动解决2文件冲突]
81bb00d5afc fix(gov): #ARCH-CONSUMERS-ACCURACY-001 priority 冲突修复 113->116 [no-lookup:priority-conflict-fix-紧急修复-gate-priority-冲突-非新功能开发]
26af6ed8fec feat(gov): #ARCH-CONSUMERS-ACCURACY-001 Phase 1 治本——CONSUMERS 字段准确性 warn-only 门禁
e64c2b3c578 feat(governance): 12 维度审计自动化——4 gate + 2 reconciler + 1 shared helper [no-lookup:12-dimension-audit-automation]
a09112853e6 [no-lookup:ARCH-PRECOMMIT-OFFLINE-001 治本施工，规则已外部化到 trae_073] feat(governance): #ARCH-PRECOMMIT-OFFLINE-001 治本 - pre-commit hook 离线可运行纪律
85880bfd6c0 #ARCH-DEP-001 第三期 L1 铁律技术强制——补提交 new_file_depgraph_gate.py + test + AGENTS.md 文档更新
07fb5c3060f fix(governance): CONSUMERS-ACCURACY priority 109->110 (conflict with RULING-COMMIT-VERIFIED) [no-lookup:gate-fix]
eabb1e5a719 fix(data): #ARCH-CH-023 补丁——akshare meta.capabilities 同步 etf_nav
abf4bf92c3c feat(gov): #ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 1+2 治本 priority 撞号
b04b65f6e98 feat(rules): Phase 2.5 cross-commit君子协定治本收口 + GATE-IMPORT-INTEGRITY友好提示增强 (#ARCH-CROSS-COMMIT-ATOMICITY-002)
6835a2d975f feat(audit): P4-1b error_pattern_consumer_reconciler + register in gateway + fix ttl_gate str/bytes bug (#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b) [no-lookup:capability_token_registered]
1afb0d83c9f feat(gov): #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 Phase 3 RULING-COMMIT-VERIFIED gate 文档已完成声明硬验证
ac82e62a211 fix(gov): P8 审查问题修复 P1/P3/P5
65007b64ea1 feat(gov): P8 BARE-SUBPROCESS commit gate 治本裸 subprocess.run 闪窗反模式
2a2bc05abd9 feat(gov): #ARCH-CROSS-COMMIT-ATOMICITY-001 治本——GATE-IMPORT-INTEGRITY 悬空 import 硬阻断门禁 [no-lookup:治本方案已在裁定文档详述,详见 architecture_issue_registry.yaml #ARCH-CROSS-COMMIT-ATOMICITY-001 条目]
2ce3eac5762 feat(governance): #ARCH-PREVENTABILITY-LAYER-001 Phase 2 落地——forged_gw_marker pre-commit gate
6131fd8b7f2 feat(gov): P0 extend DATETIME-NOW-FORBIDDEN gate to src/zephyr/ full scope (5.46 anti-recurrence) [no-lookup:P0 anti-recurrence施工延续已批准设计文档,无新增capability]
663bb270d1e P3-1.1 + P3-1.2 治本落地（#ARCH-P3-FOLLOWUP-TODOS-001 裁定 A/B/C）
b8e36396e43 fix(logging): 5.20 print→logging 迁移（第3批）
27f367d4554 fix(dashboard): M03 闭环——3 处平凡 getter 与 2 处 gate 共享 helper 加 noqa: m03-duplicate 豁免（附理由） [GW:sess-29344-20260719002711:worktree]
51f46d60aca fix(gates+struct): 5.176.4 run_checker_script helper + 5.42.4 baseline_manager 嵌套 + 5.97.6 audit_trail_cli 分发表
c8b9c1ca5a7 fix(governance): P0-3/P1-1/P1-2/P1-3/P2/P3 治本 C1/C2/C3 pre-existing 系统问题
3334d27a386 feat(governance): #ARCH-GOV-CONVERGENCE-META Phase 3.6 Task 1 - 补齐 M21 3 个 enforceability gap（第1期 AST 门禁）: SNAPSHOT-DRIFT(rc1/priority=63) + VOCAB-CHAIN(rc2/priority=73) + MANUAL-ONLY-PERMANENT(rc4/priority=43); governance_convergence_map.yaml 3 cells marked covered (15/15); M21 now returns 0; 26 smoke tests pass; noqa_exempt_registry + capability_canonical_file_registry 登记 [GW:sess-30532-20260719211319] [no-lookup:phase-3.6-task1-m21-enforceability-gates]
a70633db411 fix(gates): F821存量债务清零(29条) + gate识别PEP 562惰性导出模式 + ml_experiment_pipeline向上导入importlib化
5c9b8d5a6ab feat(governance): #ARCH-GOV-CONVERGENCE-META Phase 3.5 - RULE-EXECUTION-PAIRING gate + retrofit 65 trae rules with paired_gate_id [GW:sess-19792-20260719170125] [no-lookup:phase-3.5-rule-execution-pairing-gate-retrofit-all-trae-rules] [rule-mod]
c0073259597 Ruling:100PCT-AI-GOVERNANCE P1-5: panorama_alignment_gate fail-open 持久化治本
d2819957f15 裁定#A-E 治本：session_worktree 契约机读化 + 隔离区 + 遥测 + 任务去重 + F821 治理
cd8ad7b0748 feat(governance): #ARCH-GOV-CONVERGENCE-META Phase 3.4a - CAPABILITY-LOOKUP-REQUIRED gate (病根3治本) [GW:sess-33704-20260719083720] [no-lookup:gate-itself-self-bootstrap]
81a5eefe49a fix(gov): Phase 6 follow-up — 实现 make_undefined_name_baseline_reconciler + 解锁 GitCommitGateway
1bf1ffc846c fix(gov): #ARCH-WORKTREE-002 Phase 1+3 + 议题登记 + §ARCH-GIT-CALL-BUDGET P1.3+P2.2
6711b1319fb fix(gov): #ARCH-WORKTREE-002 Phase 1+3 + 议题登记 + §ARCH-GIT-CALL-BUDGET P1.3+P2.2
f903c57a5e9 merge session/sess-33664-20260719034558
fd1af709bb0 feat(gov): #ARCH-TOOL-HEALTH-V1 Phase 3 - 补齐 scripts_import_integrity_gate helper
488f4fc7f24 fix(gov): 11 commit gates non-Zephyr project skip (tmp_path test repo exempt)
ce548107ca8 ﻿feat(gov): add reconciler_health_gate as formal CommitGateRegistry gate (#ARCH-DATAQUALITY-V1.7)
8ebb697dcbd fix(security/access_control): implement stubs + fix contracts for agent_rbac tests
3b9aa8a5f7c refactor(ssot): 5.1.2/5.1.4 重复实现收敛——shared/schema 为 canonical 删 integration 侧 6 副本+62 调用点迁移+atomic_write/parse_frontmatter 收敛; fix(gate): TEST-SOURCE-CONSISTENCY PEP 562 惰性导出盲点治本
57e6ad031a4 #ARCH-DATAQUALITY-V1.4 Task B: add scripts_import_integrity_gate + depgraph_freshness_gate pre-commit gates
7809bd7bcf5 fix(governance): #ARCH-DATAQUALITY-V1 Task A+C — 修复4个缺import文件 + 移除blueprint_format_gate的tests/豁免
a6bd8c73e8a docs(裁定#20-G): 补充遗漏的过时阶段描述修复
4e0b261fcd2 docs(裁定#20): 同步过时阶段描述为阶段2 hard block
f7498cac9c2 治本(裁定#20-E/#20-F/#20-G): RULING-REFERENCE gate 启用 hard block + 清理虚构编号
8cd11f06570 fix(gov): _reference_helpers [CONSUMERS] header同步——补登arch_reference_gate和dangling_reference_gate两个消费者(M03治本后header漂移), 同步更新docstring反映三gate消费现状
822ee10b920 M03+M07治本: arch/dangling_reference_gate迁移到_reference_helpers消除M03重复簇, 修复genesis.py语法错误恢复M07的[STARTUP]检测, M03:2->0, M07:1->0
a7aca0bd762 fix(gov): M04治本——ruling_reference_gate补登capability+creation_token, FUNCTION-DUP消除(_reference_helpers提取5个重复helper), BLUEPRINT header修正, GitCommitGateway注册gate, M04: 1->0
7c8da5b800d refactor(create_guard): Extract Method reduce cx18-><=15 (_check_creation_token/_check) [M07+complexity debt fix]
24eafc16636 feat(gov_enforcement): S4-C NO-IMPORT-SIDE-EFFECT gate implementation + tests (module import zero side-effect gate)
1ba096d115d fix(noqa): ARCH-NOQA-GOV-001 Phase 5 债务清理 - 登记MSG-EXPOSURE/MSG-STYLE标记 + 修复22处gate-vocab/文档引用违规
a0251bd6322 fix(5.135): Phase 2 stage0 quick-fix zeroing - batch add noqa:BLE001 to 1888 except Exception lines
c927bb37c97 fix(gate): ENCODING-SAFETY fail-closed->fail-open 统一subprocess gate模式 + encoding_gate.py入库修复broken HEAD import + capability登记; 修复12个gateway测试失败 (裁定ARCH-TTL-DOC-001)
d92a0a7949c fix(governance): AI-13审计治本——shim消除同步债清理(commit 0d013c0f9f后续)
e6667291f73 merge session/sess-10644-20260717151048
4479ebbb2fc fix(gate): DATA-TASK-COMPLETENESS priority 78->41 消除与GATE-DOMAIN-FK冲突 (裁定#ARCH-DRIFT-PREVENTION-001)
019926c746f feat(gov_enforcement): ARCH-NOQA-GOV-001 Phase 2 - noqa_validation_gate 门禁化
351916e1c88 feat(gov): ARCH-DRIFT-PREVENTION-001 depgraph drift防御体系 约束驱动治本 ADP-1 GATE-DOMAIN-FK p78 / ADP-2 INSERT ERROR摘要 / ADP-3 BLUEPRINT-AMODULE-CONSISTENCY p79 / Phase4存量修复 / 33测试全通过 / ARCH注册+capability登记
9565b0d59bc merge session/sess-10968-20260717131301
f93e187cbfe fix(integrity): P5 修复 reconciliation_registry.py 路径迁移遗留 gov_audit->governance/audit (7 处引用同步) [GW:sess-10968-20260717131301:worktree]
b1fde44d0c3 fix(governance): ARCH-TTL-DOC-001 循环修复——12个gate测试priority断言过期治本(同步实际priority); import_direction_gate 否定检查治本(_is_upward_import 替代 _UPWARD_PREFIXES 枚举列表, 新增域无需更新gate); test_tests_coverage_gate Windows路径 governance->gov_enforcement 修复; 982/982 pass
a14cbf3b45c fix(governance): ARCH-TTL-DOC-001 循环修复——RENAME-DEPGRAPH-SYNC priority 36->39 解冲突; MODULE-ID-CONSISTENCY gate 精确验证治本(_candidate_declares_mid 只认 [A_*] 头声明, 排除 [BLUEPRINT] 引用误报); NO-BARE-SQL 合规(常量名 _SQL_CHECK_FILE_PATH 匹配 ^_?SQL_\w+$ 豁免正则); SRC-TST-2224->2234 唯一化; blueprint.md §0.1 补齐(ARCH-055)
dae9c83c74d fix(governance): 修复 commit gates 文件句柄泄漏 + ORPHAN-MODULE gate 检测范围 (ARCH-TTL-DOC-001)
e9b3f05bea9 fix(gate_engine): 修复5个gate文件残留过时排序注释 (Edit tool未持久化补丁)
1236f3e7f4c fix(gate_engine): TEST-SOURCE-CONSISTENCY priority 96->102 + 14 gate stale comment cleanup
9bd30272633 AI-11审计修复：门禁priority冲突消除+F5永久系统启动/关闭钩子接线+路径修复
efc1bd8019a backup(depgraph): fix [DOMAIN] header D_GOV_DOC_QUALITY->D_GOV_CODE_QUALITY before depgraph rebuild (trae_054 STEP0)
2038daa2022 fix(gov-enforcement): pure_assertion_gate.py [A_module]行修正MOD-GOV-006->MOD-GATE_ENGINE（与[BLUEPRINT]头一致，MOD-GOV-006全项目仅此1处为录入错误）
0705940ac14 merge session/sess-28808-20260717031840
7b96426d03e feat(governance): extend CREATE-GUARD to cover all 7 formats (ARCH-TTL-DOC-001 phase 2)
09c1a5fa477 feat(pure_assertion_gate): GOV-DOC-016 纯陈述原则 commit gate (priority=69) + 注册
4f225166010 fix(governance): enable doc_type strict mode + add missing doc_type (ARCH-TTL-DOC-001 phase 4)
8da4e5b9f94 fix(M03): 重复簇函数516->0,过滤dunder/同名簇+豁免AI趋同演化(治本)
02916c68033 merge session/sess-36280-20260717023154
9c88b702262 fix(governance): 治本 ARCH-REFERENCE gate 多段式编号漏检 + 补登 #ARCH-GOV-SHIM-001
95a358d29d9 fix(gate): 修正 capability_consistency_gate.py [TESTS] header 指向实际测试文件
2c982312c88 feat(data): Phase 4.3-4.5 Provider 路由-meta 一致性治本——AST 校验 + 运行时 WARN + commit gate + 契约测试（裁定 #ARCH-CH-022）
b0205034b9f merge session/sess-37904-20260717000811: 修复 path_tree sync failed + TTL metadata 警告（治本遗留项）
9039a038fc6 fix(reconciler+gate): 修复 path_tree sync failed + TTL metadata 警告（治本遗留项）
8beb91d294e docs(gov): 同步 ARCH-REFERENCE 门禁 L1/L2 治本增强说明到 4 处文档（AGENTS.md/blueprint/capability registry/表头 INVARIANTS）——修复审查遗留项 1-4
cada7204b6e merge session/sess-18508-20260717000315
a8e4f29beaa fix(arch_reference_gate): L2非git仓库跳过检查避免测试误阻断
e67fe168659 refactor(test_source_consistency_gate): extract helpers from _extract_source_symbols to reduce complexity 17 to 15
012a1255a17 merge session/sess-37400-20260716230232
efda997fe8a L0+L1+L2治本：ARCH编号治理增强
27005cfbfc1 fix(gate): TEST-SOURCE-CONSISTENCY _extract_source_symbols extract ImportFrom symbols (P7b AI-15)
889a84d01fd feat(gov_enforcement): P6 pure_shim_gate in-process gate (gov_enforcement path) + TTL fix + capability + AGENTS sync
2c1ad959435 refactor(dangling_reference_gate): extract helpers from _check to reduce complexity 16 to 15
cffbb909971 merge session/sess-8832-20260716125139
a29723a5016 refactor(perm_trigger_gate): extract helpers from _detect_time_trigger to reduce complexity 17 to 15
880c66d605a merge session/sess-35148-20260716125236
522708e4ef7 merge session/sess-7172-20260716125136
0d067b9afd2 refactor(hardcoded_url_gate): extract helpers from _check to reduce complexity 17 to 15
5bad480bef8 refactor(datetime_now_forbidden_gate): extract helpers from _check to reduce complexity 17 to 15
770db6810c6 refactor(unsafe_dict_spread_gate): extract helpers from _check to reduce complexity 17 to 15
1088c3dc172 refactor(arch_reference_gate): extract helpers from _check to reduce complexity 17 to 15
35f42bf76ab merge session/sess-3040-20260716113130
9d933ca1e6f refactor(bare_getenv_gate): extract helpers to reduce _check complexity 18 to <=15 (Tier 4 Batch 10R)
c3a65fc10b7 refactor(doc_ref_broken_gate): extract helpers to reduce _check complexity 18 to <=15 (Tier 4 Batch 10R)
f9d56818f6e refactor(file_placement_ttl_gate): extract helpers to reduce _check complexity 20 to <=15 (Tier 4 Batch 5)
a3d7449ca57 merge session/sess-35956-20260716021854
77694465d63 refactor(create_guard): extract helpers to reduce _check complexity 20 to <=15 (Tier 4 Batch 5)
cd88f6f586b refactor(empty_handler_gate): extract helpers to reduce _check complexity 20 to <=15 (Tier 4 Batch 5)
874e5fea43f refactor(vocab_hardcode_gate): extract helpers to reduce _check complexity 21 to <=15 (Tier 4 Batch 4)
7d532b6454c merge session/sess-41496-20260716012014
fb3e83f8f3f refactor(file_copy_gate): extract helpers to reduce _check complexity 22 to <=15 (Tier 4 Batch 3)
bd2167cf40e refactor(function_dup_gate): extract helpers to reduce _check complexity 22 to <=15 (Tier 4 Batch 3)
8319307f9d8 refactor(import_direction_gate): extract helpers to reduce _check complexity 23 to <=15 (Tier 4 Batch 2)
812a19cee5a feat(arch-057): extend panorama gate trigger to docs/03_modules + add 4-graph onboarding to AGENTS.md
5b41e83605d feat(gate): add sync_panorama_module.py to DEPGRAPH-WRITE-PATH whitelist (ARCH-057)
0164cdd0cf7 refactor(orphan_module_gate): extract _collect_staged_new_py_files/_detect_orphans from _check complexity 27->4 (Tier3 Step10)
dc44ee32a2d refactor(perm_trigger_gate): extract 4 helpers from _check(30->13) Step2 Tier3 P1
438440864d8 refactor(gate): capability_overlap_gate._check Extract Method (31-><=15) [裁定#217 Tier2 P1]
74954f0b377 refactor(gate): msg_exposure_gate._check Extract Method (33-><=15) [裁定#217 Tier2 P1]
3365629efc9 refactor(gate): msg_style_gate._check Extract Method (35-><=15) [裁定#217 Tier2 P1]
6a77d42ef33 refactor(gate): module_id_consistency_gate._check Extract Method (35-><=15) [裁定#217 Tier2 P1]
18f1782a1a0 refactor(gate): ssot_redefinition_gate._check Extract Method (36-><=15) [裁定#217 Tier2 P1]
83c77df66f3 refactor(complexity): create_guard._check 101->20 McCabe via extract method (裁定#216 Tier1 P1)
31a6c67f7ad fix(governance): ruling-215 fix McCabe complexity calc - exclude nested function bodies (was inflating wrappers/nested helpers)
569ae79bb4a fix(gate): ruling-214 fix NO-HIGH-COMPLEXITY gate design-impl mismatch
b70021f3167 merge session/sess-30156-20260715042623
f9a3a96681d feat(governance): depgraph 访问控制治本——裁定#ARCH-DEPGRAPH_ACCESS_CONTROL
f26ee794bfd refactor(gov_enforcement): clear 21 Any-abuse violations (13 files, dim 5.145)
6b6a2dbbddd feat(gate): CH-VERSION-COL gate阻断ReplacingMergeTree非DateTime version列(裁定#ARCH-CH-009 Phase2.1)+17单测全通过+creation_token登记
b9086e6e9f4 feat(data): 数据韧性三层机制——数据源fallback+全表补下载+完整性巡检+新增表门禁 (49 tests passed)
992ab692911 fix(governance): #ARCH-CH-008 P0+P1 治本——修复 inventory drift 路径bug + 同步gate清单 + 修复ARCH-REFERENCE正则盲区
064b04ab249 feat(gov): B5 CH-FINAL-GATE 门禁 + S2 drift_fix_reconciler 注册
9f7ec3531ee fix(domain-split): update path references in YAML/MD/JSON/py string constants
f445a3b2164 fix(domain-split): update all import paths and references after governance/trading domain migration
af2ae4e2127 fix(tests): 更新 test_source_consistency_gate 测试文件 import 路径
9c9929d80f7 feat(gate): add BLUEPRINT-FORMAT commit gate (ruling #214 Phase 0)
```
