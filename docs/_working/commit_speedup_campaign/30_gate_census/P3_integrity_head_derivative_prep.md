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
