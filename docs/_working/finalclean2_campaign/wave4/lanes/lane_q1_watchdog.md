---
ttl: task_bound
completes_when: 本案卷读数被总包在 dev 侧复核，且其中点名的在册缺陷被属主车道承接
generated_by: 本班只读车道（弱模型出案卷不出裁定），落地面由 st-fclean4-20261012 复核
session: st-fclean4-20261012
lane: wave4-lane_q1_watchdog
role: 只读调研案卷（零删除、零 git 写、零改判据）
---
# 终清波四·车道案卷：M3-Q1 watchdog 保留窗前置调研（通道证伪／选项／破面／风险）

> 原稿面＝`.runtime/tmp/st-fclean4-20261012/lanes/lane_q1_watchdog.md`（TTL 临时区），本件为其入册副本；
> 数值口径以该案卷自带的时刻与参照点声明为准。
# lane_q1_watchdog — 案卷（Q1：drift quarantine REDUNDANT 保留窗 30d→7d 的属主通道）

- 会话：st-fclean4-20261012 ｜ 战役：终清波四 ｜ 性质：只读研究，零删除/零写 tracked 文件
- 对象模块：`src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py`
- 状态：进行中（骨架先行，随查随补）

## 1. 模块身份与归属（头部 14 字段，实测行号）

文件：`src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py`（头部块 :1-19）

| 字段 | 行 | 值（逐字） |
|---|---|---|
| `[BLUEPRINT]` | :1 | `MOD-GOV_DRIFT_WATCHDOG \| docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml \| §#ARCH-WORKTREE-WRITE-INTEGRITY-001` |
| `[MODULE]` | :2 | `zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog` |
| `[DOMAIN]` | :3 | `D_GOV_ENFORCEMENT` |
| `[CONSUMERS]` | :5 | `git_commit_gateway (_register_default_reconcilers: make_worktree_drift_watchdog_reconciler); CLI python -m ... [--once\|--daemon\|--status]` |
| `[MATURITY]` | :7 | `production` |
| `[INVARIANTS]` | :8 | 含逐句子句 **“quarantine 30 天 retention 自管+带外删除 tamper 审计”**（#ARCH-264 O4） |
| `[MODIFY-GUARD]` | :9 | 点名 `_sweep_quarantine 只清理 drift_<ts> 规范命名目录` |
| `[STABILITY]` | :10 | **`evolving`** |
| `[SAFETY]` | :11 | `M` |
| `[AI_AUTONOMY]` | :12 | **`ai_modifiable`** |
| `[ERROR_CONTRACT]` | :13 | git 不可达/DB 故障→降级 skip；daemon 循环异常写 lifecycle 后 continue |
| `[TESTS]` | :14 | `tests/governance/rule_bridge/test_worktree_drift_watchdog.py`（**注：此路径与实际测试目录不符**，实测在 `tests/gov/governance/rule_bridge/test_worktree_drift_watchdog.py`） |
| `[A_module]` | :15 | `module_id=MOD-GOV_DRIFT_WATCHDOG \| layer=module \| stability=evolving \| safety=M \| ai_autonomy=ai_modifiable` |
| `[TTL]` | :16 | `task_bound` |

归属读数：`stability=evolving` + `ai_autonomy=ai_modifiable`（:10/:12/:15）⇒ **代码面本身允许 AI 直改**（非 human_gated/frozen）；
但 :8 `[INVARIANTS]` 把“30 天”写成了机读不变量句 ⇒ 改数值必须同批改 `[INVARIANTS]` 那句，否则不变量与实现漂移。
`[BLUEPRINT]` :1 指向 `architecture_issue_registry.yaml`；该册头部 `# [A_config] … ai_autonomy=human_gated`
（`architecture_issue_registry.yaml:1`，`registry_id: REG-ARCH-ISSUE-001`，:5 “架构议题（#ARCH-XXX）唯一真源（SSoT）”）
⇒ **母议题文本面是 human_gated，代码面是 ai_modifiable，两面不同权属**（这是“参数面走属主通道”的结构性张力，见 §4）。

## 2. `_QUARANTINE_RETENTION_DAYS` 定义与全部读点（实测行号，与旧案卷行号已漂移）

- 定义：`:98 _QUARANTINE_RETENTION_DAYS = 30  # 快照保留天数（#ARCH-264 O4：watchdog 自管 retention）`
- **唯一定值读点**：`:545 def _sweep_quarantine(root: Path, retention_days: int = _QUARANTINE_RETENTION_DAYS) -> dict:`
  （形参默认值绑定＝import 时求值；此后模块内**无任何其它引用**——全模块 grep 命中仅 :98/:545/:598 三处 + 头部散文 :9 无关联）
- 节流入口：`:609 _maybe_sweep_quarantine(root)` → `:612 today = datetime.now(timezone.utc).date().isoformat()`；
  `:613 if state.get("quarantine_last_sweep") == today: return`（**UTC 日历日**只跑一次）；`:615 swept = _sweep_quarantine(root)`
  （**不传 retention_days ⇒ 吃模块默认**）；`:616 state["quarantine_last_sweep"] = today`
- 调用节拍：`:1551 if tick % full_every == 0:` → `:1552 scan_once(root)`、`:1553 _maybe_sweep_quarantine(root)`
  （只在全量周期跑；热扫 10s 支路 :1558 `hot_only=True` 不清扫）
- 清扫语义（`_sweep_quarantine` 体 :556-606）：
  - 作用面：`:557 qdir = root / _QUARANTINE_DIR`（`_QUARANTINE_DIR = ".runtime/quarantine"`，:97）；`:565 for d in sorted(qdir.iterdir())`；
    `:566 if not d.is_dir() or not d.name.startswith("drift_"): continue` ⇒ **只碰 drift_* 目录，非 drift_* 与文件形态永不碰**
  - 命名判据：`:569 ts = datetime.strptime(d.name[len("drift_"):], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)`；
    `:570-571 except ValueError: result["kept"] += 1`（人工存证豁免）⇒ **到期判据=目录名字节里的 UTC 时间戳，不是 mtime**
  - 到期线：`:560-561 cutoff = now - timedelta(days=retention_days)`；`:581 elif ts < cutoff: kind = "expired"`
  - 空壳支路：`:574 is_empty = not _dir_has_files(d)`（`_dir_has_files` :534-542，OSError 按非空=保守不删）；
    `:562 empty_cutoff = now.timestamp() - _QUARANTINE_EMPTY_GRACE_SECONDS`（常量 :101 = 60s，判 `:575 mtime`）；
    `:579-580 if is_empty and mtime < empty_cutoff: kind = "empty_shell"`（**空壳与 retention_days 无关，改窗口不影响空壳**）
  - 不可判定：`:576-577 except OSError: kept += 1`（保守不删）
  - 删除唯一通道：`:589-590 safe_rmtree(d, allowed_prefix=qdir, ignore_errors=True)`；`:591-593` 异常 ⇒ kept（本轮不删，下轮再试）
  - 逐条审计：`:594-603 _audit(root, {"ts":…, "verdict": "quarantine_retention_sweep", "kind": kind, "file": d.name, "retention_days": retention_days})`
  - 对账防误报：`:619-624` 把本轮 removed 前缀从 `state["known_quarantine"]` 摘除（防自清扫被 :1150-1170 判成 `quarantine_tamper`）；
    `:626-627 if swept["removed"]: _lifecycle_log(root, "quarantine_swept", swept)`
  - **单轮无限量**：循环无 removed 上限/无分批 ⇒ 首轮到期件数=全部超期目录（见 §7 实测体积）

## 3. “REDUNDANT vs HAS_UNIQUE” 在代码里存不存在？——不存在（已做正对照）

- 实测：`grep -n "REDUNDANT|HAS_UNIQUE|redundant"` on the module ⇒ **0 命中**；同一次 grep 的正对照命中
  `:446 def _audit`、`:468 def _quarantine_content_sha`、`:1427 _lifecycle_log` ⇒ 尺子完好，0 命中为真。
- 模块内唯一 sha 用途=`_quarantine_content_sha(root, d)`（:468，供 tamper 记录取证，:1166），**不做与 dev 的字节比对**；
  漂移比对（`_work_hash`/`_head_blob`/`_real_drift`，:1185-1186/:1181）只在“工作区 vs HEAD”层面，**与 quarantine 内容无关**。
- 结论：Q1 的 “REDUNDANT 保留 7d” 语义在本模块**没有输入**。任何类感知方案都需要外部/内部先算 A/B 字节类
  （旧案卷 `docs/_working/finalclean2_campaign/wave3/lanes/lane_quarantine.md:88-113` 用 8 线程 + `git show dev:<rel>` 缓存
  全集测得 REDUNDANT=488 枚 / 13,893,319 B，HAS_UNIQUE=6,939 枚 / 665,966,624 B）。

### 三个最小改面选项（只陈列，不择一）

| 选项 | 改动行 | 类别由谁算 | 代价 | 失败模式 |
|---|---|---|---|---|
| **(a) 全量 30d→7d**（对一切 drift_* 一刀切） | 仅 `:98` 数值 `30→7`（+ `[INVARIANTS]` :8 那句“30 天”同步改，防不变量漂移）；可选 `:546` docstring | 无人（不分类） | 最小（1-2 行）；测试零改（§6） | **误删 6,939 枚/666 MB 独有字节**（旧案卷 §3：其中 585.8 MB git 历史也再生不出）＝真实工作成果蒸发；与“REDUNDANT 才收”裁定文本不符＝执行越界 |
| **(b) 类感知 retention：sweep 内置 A/B 字节测试** | `:545` 增 `redundant_days` 形参；`:560-561` 分双线 cutoff；`:573-585` 判定前插“逐文件 vs `git show dev:<rel>`（含 `\r\n`→`\n` 归一）”归类；`:594-603` 审计加 `dir_class` 字段 | sweep 自己（每目录逐文件 `_git(root,["show",f"dev:{rel}"])` + hashlib 比对） | 单轮目录数×文件数 次 git 子进程（现量级 6,468 目录 / 9,388 件，旧案卷实测 40s@8 线程；守护是单线程串行 ⇒ 数量级放大），且 `:1553` 在全量节拍内同步跑 ⇒ 拖慢 60s 扫描；克隆风险（比对逻辑与旧案卷/`clone_guard` 面重叠） | 归类判据错=**把 HAS_UNIQUE 误判 REDUNDANT 直接删**（编码/EOL/子目录 relpath 复原三处口径易错）；git 不可达时的降级方向（保守不删 vs 照 30d 处理）需显式定；单轮无限流＋无 mtime 判据 |
| **(c) 外部落类清单，watchdog 只消费** | 新增读清单（形如 `_load_*` 家族：`_load_allowlist_b_class` :636-658 的 mtime 缓存 + fail-closed 空返回是仓内现成范式）；`:545` 增 `early_sweep_manifest` 读取；`:579-585` 命中清单且名 ts 超 `7d` ⇒ kind=`"redundant_expired"`（新 verdict 值域需登记）；其余零改 | 外部按 relpath 全集算（本战役已有 out/ 机生表能力），守护只读不判 | 中：需新通道契约（清单落点须避开 §9.4 生命周期隔离：`.runtime/sessions/<sid>/staging` 有 24h TTL、永久守护不能引临时区）⇒ **清单落点本身要先裁**；须防“清单陈旧/被篡改即成免死金牌或屠刀” | 清单与实际目录漂移（新名不在册＝不提前收，退化为 30d，安全侧）；清单错列 HAS_UNIQUE＝借合法通道删（审计记 `redundant_expired` 可归因，但字节已失）；通道契约未立=属主面更复杂（要登记新注册表/新 token） |

共性（三选项皆然）：`:569` 到期判据用**目录名 UTC 时间戳**，7d 窗口下“老目录被续写新快照”会整目录一起到期——
现 `_snapshot`（旧案卷记 :443-462，现函数行号未复核）按 ts 建新目录，未见向既有旧目录续写的路径，但**未逐行证实**（§9）。

## 4. 属主通道判定（SSOT：规则=YAML、架构=DB；数值不在业务规则册里）

实测“30 天 retention / 该参数”在册声明面：

1. **唯一在册文字声明 = 架构册**：`docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml:3159`
   （`- issue_id: "#ARCH-264"` 起于 :3147）裁定 O4 原文：**“O4 quarantine 带外裸删除实证（定凶豁免），watchdog 自管 30 天 retention+ops_guard 保护区”**；
   母议题 `#ARCH-WORKTREE-WRITE-INTEGRITY-001` 在 :10247（watchdog `[BLUEPRINT]` :1 所指）。
   该册 `registry_id: REG-ARCH-ISSUE-001`，自称“架构议题唯一真源（SSoT）”，头部 `[A_config] … stability=stable … ai_autonomy=human_gated`（:1）。
   ⇒ 架构面：**30 这个数只在该 YAML 的 O4 裁定散文里出现过一次，且是叙述文字、不是可派生机读字段**。
2. **业务规则面无数值**：`docs/01_policies_and_standards/rules/trae_085_stale_base_overwrite.yaml`（144 行）把 watchdog 列为**检测面**
   （:51/:77/:82/:107/:121/:132），**无任何 retention 天数**（grep `retention|30` 于该册 ⇒ 0 命中；正对照=同 grep 命中 :51/:77 等行 ⇒ 尺子完好）。
3. **门禁册无该门条目**：`_registry/catalogs/gate_registry.yaml`（222 行含 `gate_id`，正对照）grep `GATE-WORKTREE-DRIFT-WATCHDOG` ⇒ **0 命中**；
   该 id 只出现在实现侧 `worktree_drift_watchdog.py:89`、`:1578` 与 `architecture_issue_registry.yaml:1288` 的 `related_rules` 散文。
   ⇒ **gate_registry.yaml 不是本参数的属主面**（该门是 reconciler/守护，非 commit 门，故不进门册）。
4. **数据保留契约不覆盖**：`_registry/contracts/data_retention_contract.yaml` grep `quarantine|watchdog|\.runtime|drift` ⇒ **0 命中**
   （正对照：同册 `grep -c "INV-RET"` = **18** 命中 ⇒ 尺子完好）⇒ 该契约只管业务数据（CH/冷储），**不是本参数的通道**。
5. **计划任务不传参**：`scripts/tasks/register/register_drift_watchdog_task.ps1:58`
   `$argString = '-m zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog "' + $RepoRoot + '" --daemon'`
   ⇒ 任务只提供 `--daemon`，**无 retention 旗**；`main()`/`run_daemon()` 亦无 `--retention` 参数（模块 grep 未见 argparse 级 retention 选项）。
6. **模块无配置读取面**：全模块 `os.environ|getenv|yaml.safe_load|_load_config` 命中仅 :658（读 B 类白名单）与 :1448（PYTEST_CURRENT_TEST）
   ⇒ **参数没有 env/config-file 逃生口，唯一真面=模块常量 :98 + `_sweep_quarantine` 形参 :545**。

**通道结论（供总包裁，非自裁）**：本参数**不存在“YAML 参数册→代码”的既有属主通道**（不同于回测护栏那种
`ruling_registry.yaml:1742` 明立“单一真源常量 + 禁复述数值”的案例）。因此“参数面走属主通道改”的**属主面=该模块自身**
（`[AI_AUTONOMY] ai_modifiable` :12 + `[TESTS]` :14 在册自证），而**同步义务面=两处架构/身份文本**：
(a) `worktree_drift_watchdog.py:8` `[INVARIANTS]` 的“30 天”句；
(b) `architecture_issue_registry.yaml:3159` O4 文本的“30 天 retention”（或新立一条 #ARCH/裁定条目收编该变更）。
按 RULE-SSOT（架构数据 apply_*.py 直写 DB）与 RULE-RULING（裁定须先登记、同 commit 原子），
若把 30→7 视作**政策变更**（保留窗属 Owner 面“数据驻留/资产退役”邻域），合规改动面=
`worktree_drift_watchdog.py:98`(+`:8` 不变量句) + 新裁定条目入 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` +
`architecture_issue_registry.yaml` #ARCH-264/母议题 O4 文本更正（同批）；测试面见 §6。
**未证实**：`architecture_issue_registry.yaml` 是否为 PG 投影（若为投影则须走 apply_*.py 而非直改）——见 §9。

## 5. 谁动过这个参数 + 裁定先例

- `git log --oneline -8 -- src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py`（近 8 次，新→旧）：
  `d69abf35230`（维护二班 P0+P1 袋，26 件同域）、`e910cae9acc`（G1G2 治本：tamper 补 pid/隔离区 sha）、
  `a6939367c08`（kimi-audit R-05 watchdog 状态机化）、`abdf2446ab3`（algo-flow 出仓）、`6044c47fc67`（治理战役 M1-M3 进程孵化）、
  `59e5d875e3e`（外审遗留 P1-4/P2-2/P2-3＝空壳宽限+known_quarantine 对账的来头）、`0314d205dab`（B2 auto-stage 盾）、
  `68d64742e37`（删除型漂移硬化）。
- `git log -S"_QUARANTINE_RETENTION_DAYS" --` ⇒ **仅 1 支**：`3429157b779`
  （“AI-DRIFT-001 裁定近期三件+O3-P0 落地（#ARCH-264）…… ③O4 quarantine 自管：**30 天 retention** 日级清扫逐条审计+known_quarantine 登记带外删除 tamper 审计”。
- `git log --oneline -L98,98:<file>` ⇒ 同样**只有 3429157b779** ⇒ **该数值自 2026-08-26 引入后从未被改过**（本次 Q1 是首次改动）。
- 裁定在册面：**`ruling_registry.yaml` 无 #ARCH-264 条目**（grep `ARCH-264|worktree_drift_watchdog|DRIFT-WATCHDOG`
  ⇒ 仅 `:1627`（裁定#266/#267 收口批）散文里顺带点名 `worktree_drift_watchdog` 为“不持核心链 AuditWriter 的三个守护之一”，与 retention 无关）。
  ⇒ 先例形态=**参数决策记在 `architecture_issue_registry.yaml` 的 O4 裁定散文（:3159），未进 `ruling_registry.yaml`**（当时尚无 RULE-RULING 同 commit 原子约束的适用范围/或被豁免，未考）。
- 相邻先例（供类比，非直接同题）：
  - `ruling_registry.yaml:1742`（回测护栏收益带）立“**单一真源常量 + 机读 [INVARIANTS] 条款**，下游四落点一律引常量、禁复述数值；再动须另立裁定” ⇒ 本仓对“数字改一处”的合规范本。
  - `ruling_registry.yaml:3617`（**裁定#441**，E13/补-20）明记执行过 “**quarantine 过期 218 目录**” 的磁盘清账 ⇒ 历史上“过期隔离目录”被战役批量收过，且走裁定批文。
  - `ruling_registry.yaml:2065`（**裁定#318**）=watchdog 噪声型提醒改制（状态不落盘/心跳），非 retention 面。
  - `docs/_working/maint3_campaign/00_ledger.md` grep `retention|quarantine|watchdog|drift` ⇒ 命中 `:158/:342/:345/:356/:374/:386/:503/:528`
    全部是 **L2 池面回退方向分量/known_quarantine 快照面**（`:342` “快照沿用在册 `known_quarantine` 面”），**无 retention 天数先例**。

## 6. 钉住该值的测试（结论：**没有任何测试断言常量=30**）

全 `tests/` grep `_QUARANTINE_RETENTION_DAYS` ⇒ **0 命中**（正对照：同型 grep 命中 `_sweep_quarantine` 12 处，见下 ⇒ 尺子完好）。
grep `retention_days` 的其它命中（`tests/backup/test_retention_derived.py:18-19`、`tests/data/.../test_data_volume_growth_monitor.py`、
`tests/gov/capacity/test_batch3_integration.py:72` `assert instance.retention_days == 30`）经核属**备份/容量 sink/契约 CT-DR-001 默认值**，
与 quarantine 无关（`test_batch3_integration.py:70-72` 读的是 `BATCH3_CONTRACTS["CT-DR-001"]` 备份契约模型）。

会跑到的 sweep 测试（`tests/gov/governance/rule_bridge/`，注意 `[TESTS]` 头 :14 写的路径少了 `gov/` 段）：

| 位点 | 调用 | 30→7 的影响 |
|---|---|---|
| `test_worktree_drift_watchdog.py:317-331` `test_quarantine_retention_sweep` | `wd._sweep_quarantine(git_repo, retention_days=30)`（:327，**显式传 30**），件=`drift_20200101T000000`(删)/`drift_29990101T000000`(留) | **不破**（显式传参，不吃模块默认） |
| `:360-383` `test_sweep_removes_empty_shells_after_grace` | 同上 :376 `retention_days=30`；空壳靠 mtime+60s 宽限 | **不破**（空壳支路 :579 与 retention_days 无关） |
| `:386-394` `test_sweep_keeps_fresh_empty_shell_inflight` | :392 `retention_days=30` | **不破** |
| `:397-417` `test_maybe_sweep_reconciles_known_quarantine` | :414 `wd._maybe_sweep_quarantine(git_repo)` **吃模块默认**；fixture 名 `drift_20200101T000000`（2020 年，远超 30d 也远超 7d） | **不破**（7d 下照样到期） |
| `test_worktree_drift_watchdog_redteam_edge.py:280-311`（1000 目录洪峰） | `retention_days=0`（:295）；断言 `kept==2`（非法名+未来名）、诱饵零误伤、`len(sweeps)==n` 逐条审计 | **不破**（0 注入） |
| `:313-335` `test_r4_4_maybe_sweep_quarantine_throttled_entry` | monkeypatch 注 `retention_days=0`（:319），验日级节流 | **不破** |

⇒ **纯 (a) 数值改动零测试红**；同时意味着**测试面无法为 7d 提供任何回归保护**（钉的是显式传参，不是政策值）。
**(b)/(c) 则必破/必补**：类感知需要 A/B 输入，而上述 fixture 内容与 `dev` 值毫不相干
（`x.txt/y.txt/a.txt/blob.bin` 在 dev 查无同名件 ⇒ 按旧案卷口径全部落 **C2=HAS_UNIQUE**，7d 早收分支打不到它们），
`test_quarantine_retention_sweep` 等 4 支会由“删 1 留 1”变“删 0 留 2”——需同步改写 fixture 或补类参数默认值语义（这是成本，不是否决理由）。
门面无涉：`gate_registry.yaml` 无该门条目（§4 第 3 条），改值不触发门禁册对齐。

## 7. 短窗运维风险实测（首轮blast 尺寸 + tamper 语义）

**首轮 blast（本车道实测，只读 `os.listdir`）**：`.runtime/quarantine` 现顶层项 **6,519**，其中 `drift_*` 目录 **6,468**
（注：今日早班案卷记 7,434 ⇒ 期间已 −966 枚，见 §8）；按目录名 UTC 时间戳对 `now=2026-10-12T13:30Z` 分龄：

| 龄 | 枚数 | 30d 下 | 7d 下 |
|---|---|---|---|
| ≥30d | **0** | 到期 | 到期 |
| 7–29d | **1,966** | 留 | **首轮即到期** |
| <7d | 4,502 | 留 | 留 |
| 命名不可解析 | 0 | kept 豁免 | kept 豁免 |

⇒ **(a) 一刀切 7d 的单轮 blast=1,966 目录**，其中按早班字节判定含 **≈1,478 枚 HAS_UNIQUE（666 MB 独有字节的主体）**——
这正是 Q1 语义（只收 REDUNDANT 488 枚/13.9 MB）所不允许的越界面。

**tamper 判定与删除的关系（机制逐点）**：
1. 登记面：`scan_once` 告警时把 `_snapshot` 返回的**文件路径**追加进 `state["known_quarantine"]`，
   并 `del known_q[:-_KNOWN_QUARANTINE_CAP]`（`:1354-1356`，cap=500 定义 :103）⇒ **在册可观测面 ≤500 条**，
   与 6,468 目录体量差一个数量级以上 ⇒ 绝大多数目录天生不在 tamper 监视集内（早班 §7 亦据此判“人工裸删不可见”）。
2. 判定面：`:1150-1170`（仅 daemon `alert_enabled`）遍历 `known_q`，`(root/d).is_dir()` 为假 ⇒
   写 `_audit(verdict="quarantine_tamper", pid, process, quarantine_content_sha256, worktree="missing")` 后 `known_q.remove(d)`。
   **只落 jsonl，不调 `_log_results`** ⇒ 不进 `reconcile_execution_log`、不出 banner、不阻断任何东西。
3. 消费面：全仓 grep `quarantine_tamper` ⇒ 命中仅 `worktree_drift_watchdog.py:618/:1159`、
   `tests/gov/governance/rule_bridge/test_worktree_drift_watchdog.py:334-345`、
   以及叙事件 `sop/governance_sop/commit_guide_sources/death_cases_registry.yaml:160`（把 tamper 列为 09-24 蒸发案根因的一环）。
   **无任何 commit gate 读该 verdict ⇒ 不会因删除而阻断他人提交**（正对照：同 grep 命中上述 4 位点 ⇒ 尺子完好）。
4. 自清扫不误报：`:619-624` 用 removed 前缀摘登记 ⇒ 走合法通道的 1,966 目录**不会**被判 tamper（这是好性质）；
   副作用=**tamper 面无法反向证明“谁删的”**，删除证明只依赖 (i) watchdog `quarantine_retention_sweep` 记录（`_audit`，:594-603）
   与 (ii) `safe_rmtree` 留痕 `.runtime/gate_audit/safe_rmtree.jsonl`（`src/zephyr/shared/io/file_utils.py:749,753-763`，
   经 `append_audit_jsonl`，**注释自陈“50MB 轮转”**）。
5. 保护区与授权：`scripts/ops_guard.py:90` `PROTECTED_PREFIXES`（含 :99 `".runtime/quarantine"`，注释 :96-98 实证
   “2026-08-25/26 两起带外裸删”），人工删需 `FORCE_ENV="ZEPHYR_FORCE_DELETE"`（:140，:1374 未授权即拦）；
   守护自家通道经 `safe_rmtree`→`ops_guard.bulk_delete_approved()`（:741-744）置 `_BULK_APPROVED`，
   **in-process 判定在 :1318 直接 return** ⇒ sweep 不写 `ops_guard_delete.jsonl`，删除证据只剩上面 (i)(ii) 两条。
6. 洪峰风险已有先例：`ops_guard.py:388-397` 明文记载“主审计池 50MB 大小轮转，高频 in-process 记录会把治理动作关键段
   **物理挤出**（09-06 实证：08:58 关键审计被 14:21 pytest 洪峰挤出）”，并为此另立永不轮转的
   `governance_actions.jsonl`（:390）。**watchdog 的 sweep 记录未接入该不可挤出通道** ⇒ 1,966 条/轮的 `expired` 证据
   落在会轮转的 `safe_rmtree.jsonl`（现 33 MB / 97,629 行，其中 82,000 行是 pytest 噪声）⇒ 证据存续有硬风险。
7. 节拍风险：日级节流按 **UTC 日历日**（:612-613），且只在全量周期调用（:1551-1553）；daemon 空闲
   `_IDLE_EXIT_SECONDS = 1800`（:94）会自退（:1562）⇒ 若守护在日内未起或重启（`quarantine_last_sweep` 已置今日），
   **当日不再清扫**；7d 窗下到期件数会累积成“隔日大批”，与 §7.6 的洪峰叠加。

**治理门位提示**：`risk_tier_registry.yaml:134-135` 记 `domain: D_GOV_ENFORCEMENT` → **`tier: high`**，
human_gate 列表含“**物理不可逆删除（生产盘/无备份生产数据）**”（:141）。retention 缩短本身是代码改动，
但其后果是让 666 MB 无第二副本的证据进入可删面 ⇒ 是否触发 Owner 门位归总包裁，本车道只如实报表。

## 8. 红旗复核：sweep 审计留痕真的缺吗？——早班“0 条”读数今日已不成立（含更正）

本车道实测（只读；正对照=同一脚本能解析出全部 verdict 分布）：

| 对象 | 读数 |
|---|---|
| `.runtime/audit/worktree_drift_watchdog.jsonl`（1.8 MB，ts 跨 `2026-10-10T23:56:00Z → 2026-10-12T13:22:31Z`，3,550 行） | `quarantine_retention_sweep` **1,134 条**（全 `kind=empty_shell`，集中于 `2026-10-12T00:01:43→00:02:08Z`）；`quarantine_tamper` 224；`grace_suppressed` 1,340；`healed` 408；`alerted` 224 |
| `.runtime/audit/worktree_drift_watchdog.jsonl.1`（58 MB，ts 跨 `2026-09-23T06:41:55Z → 2026-10-10T23:54:55Z`，94,072 行） | `quarantine_retention_sweep` **2,359 条**（亦全 `kind=empty_shell`，日分布 10-02:214 / 10-03:57 / 10-04:623 / 10-05:35 / 10-06:355 / 10-07:349 / 10-08:634 / 10-09:92） |
| **`kind="expired"` 记录** | **现存两代审计里 0 条**（与“现存最老 `drift_*` 名字时间戳>2026-10-01，而 30d cutoff=09-11 之后从未有件到期”自洽） |
| `.runtime/gate_audit/safe_rmtree.jsonl`（33 MB，97,629 行，跨 `2026-08-26T06:40:30Z → 2026-10-12T12:37:03Z`） | 主仓根 `.runtime/quarantine/drift_*` 真删 **15,629 条**；按日：09-14:**10,583** / 09-16:156 / 09-17:173 / 09-18:231 / 09-19:165 / 09-20:187 / 09-21:161 / 09-23:480 / 10-02:214 / 10-03:57 / 10-04:623 / 10-05:35 / 10-06:355 / 10-07:349 / 10-08:634 / 10-09:92 / 10-12:1,134 |
| 两通道对账 | 10-02 起**每日 1:1 全等**（9 个重叠日 `safe_rmtree ∩ sweep 审计 = 100%`，集合差=0 与 0）；**9 月段（09-14/16/17/18/19/20/21/23）只有 safe_rmtree 记录、无 watchdog 审计**（其 jsonl 现存最老仅回溯到 09-23，早段已轮转丢失） |

**对本车道自身尺子的更正申报**：
- 早班 §6 的“`quarantine_retention_sweep` **0 条**”读数**今日不成立**（实测 1,134+2,359 条）。本车道第一版用
  转义正则匹配 `D:\\ZephyrAlpha\\.runtime\\quarantine\\drift_` 判“生产真删 0 条”——**那是坏尺**（改 JSON 解码后
  `target.startswith(main_root)` 正测得 15,629 条）。教训同在册“0 命中必先正对照”。
- “9 月快照为何消失”现已有正向证据：**2026-09-14 17:04Z 单轮 10,583 条 safe_rmtree 授权删除**（样本 pid 34280），
  即**经授权通道、非带外裸删**；但其 watchdog 侧审计已随轮转丢失 ⇒ **“删除有痕”在 9 月段只剩半边痕**。
- 9 月段并非“从无审计”：归档案卷 `docs/_working/archive/2026-09/kimi_audit/lane_reports/A3.md:97`
  实测过当时全量 verdict 分布里 **`quarantine_retention_sweep` = 10,912 条**（同期 `quarantine_tamper` 4,646 条）
  ⇒ 审计**曾经存在、后被体积轮转挤出**，与 `ops_guard.py:392-397` 自陈的“洪峰把关键段物理挤出”同一病灶；
  早班读到的“0 条”是该失痕瞬间的读数，不是政策故障。

**对 Q1 的直接含义**：7d 窗会让 **`expired` 分支在生产里第一次被实测触发**（现存 0 条 expired 是“从未到期”而非“坏了”），，
证据链双通道（watchdog jsonl + safe_rmtree jsonl）在 10-02 以后已被证明**逐日 1:1 可配对**；
但 (i) 两通道都会轮转挤出（watchdog 保留 .1/.2/.3、safe_rmtree 50MB），(ii) 9 月段已发生“半边痕”，
所以 7d 本身**不会继承盲目**，**前提是**首批到期不撞轮转洪峰——建议总包把首批落地的核对窗口压在
落地当日（读 `safe_rmtree.jsonl` 与 watchdog jsonl 配对数），别指望事后翻账。

## 9. 残余未覆盖面（如实申报，未测=未知）

1. **未跑守护实测**：未以 `--once/--status` 触发 `scan_once`/`_maybe_sweep_quarantine`（读源码+读在册审计替代）；
   故 7d 语义在**真生产仓根**的行为是推断，非观测。
2. `_snapshot`（早班记 `:443-462`）的**现行号与“是否会向既有旧目录续写”未逐行读**；若会续写，7d 下老目录被续写仍整目录到期删（§3 共性风险未证伪）。
3. `architecture_issue_registry.yaml` **是磁盘真源还是 PG 投影未证**（只读到其自称 SSoT + `ai_autonomy=human_gated` 头）
   ⇒ 若为投影，O4 文本更正须经 apply_*.py/generator，改动面比 §4 所列更大；`generate_project_depgraph` 之外是否有该册的 render 通道未查。
4. `depgraph`/PG 侧 `MOD-GOV_DRIFT_WATCHDOG` 的 `[INVARIANTS]` 投影是否需同步再生未查（改 :8 那句后投影漂移风险面未测）。
5. **未读 `main()`/`run_daemon()` 全参面**：只据 `[CONSUMERS]` :5 与 ps1:58 判“无 retention 旗”，未逐行读 CLI 解析块
   ⇒ 若 CLI 其实有隐藏 `--retention-days` 旗，§4 第 5 条结论要降级。
6. **未测 pytest 真实回归**：§6 的“零测试红”是**静态读断言**推得，未跑 `tests/gov/governance/rule_bridge/test_worktree_drift_watchdog*.py`。
7. `quarantine_tamper` 是否被任何**报表/周审/hook_drift 消费方**读取未穷尽（只 grep `src/ scripts/ docs/01... tests/`，未扫 `data/`、`docs/_working/` 全量、PG 侧）。
8. REDUNDANT/HAS_UNIQUE 的**逐目录龄分布未交叉**：§7 分龄是目录名口径，早班 §2 分类是字节口径，
   两者叠加后“7d 下到期且属 REDUNDANT 的究竟几枚”**未测**（Q1 若走 (b)/(c) 需要这张表，本车道未产出）。
9. `.runtime/quarantine` 非 drift_* 的 **51 个顶层项**内容/属主未清点（`branch_refs.log`、`ahead_branches.log` 等按早班 §6 存在，未实测在册）。
10. `safe_rmtree` 的 50MB 轮转具体触发阈值与保留代数未在源码中核数（只取 ops_guard :392 注释自陈 + `file_utils.py:758` 注释）。
11. 未核 `_sweep_dead_sessions` / `_auto_commit_derived`（同节拍 :1554-1555）与 retention 的相互扰动（尤其 A1 的 7 天常量 `_DEAD_SWEPT_RETENTION_DAYS = 7`（:126）与 Q1 数值巧合，**语义不同**，易混）。
12. 未测 Windows 文件句柄占用（在飞目录）下 `ignore_errors=True` 的**半删残留**形态（空壳判据 :574 会把半删目录当空壳下轮再删，推断未实测）。

## 10. 机生出件与本节补注

- `D:/ZephyrAlpha/.runtime/tmp/st-fclean4-20261012/out/q1_drift_age_distribution.csv`
  （drift 目录总数 6,468；age 分箱 ≥30d:**0** / 7–29d:**1,966** / <7d:4,502 / 不可解析:0；
  现存最老目录名时间戳=`2026-10-03T16:00:58Z`（≈9 天，故“7–29d 箱”＝命名 10-03~10-05 那批）；最新=`2026-10-12T11:26:54Z`）
- `D:/ZephyrAlpha/.runtime/tmp/st-fclean4-20261012/out/q1_sweep_evidence_pairing.csv`
  （逐日 `safe_rmtree` 主仓根删除数 vs watchdog `quarantine_retention_sweep` 记录数 + 集合交差；
  10-02~10-12 九天**全等/交集 100%/仅安全通道独有=0**；09-14~09-23 八天**仅 safe_rmtree 有、watchdog 侧 0**＝轮转失痕；
  合计 15,629 vs 3,493；`kind` 分布 `{empty_shell: 3493}`，**expired 0 条**）

补注（§7 测试面补全，已实测）：`known_quarantine` 的测试消费面只有
`tests/gov/governance/rule_bridge/test_worktree_drift_watchdog.py:339`（`scan_once` 产快照即登记）与
`:397-417`（对账摘除）两处；同名 redteam 系列其余 5 支（`_redteam_audit/_concurrent/_daemon/_injection/_timing`）
grep `known_quarantine|_sweep_quarantine` ⇒ **0 命中**（正对照：同 grep 在 `_edge` 命中 :295/:313-335 ⇒ 尺子完好），
故 (b)/(c) 方案若改 sweep 语义，回归面集中在 `test_worktree_drift_watchdog.py` + `_redteam_edge.py` 两册。
另证：模块头 `[TESTS]` :14 声明的 `tests/governance/rule_bridge/test_worktree_drift_watchdog.py`
经 `ls` 实测**不存在**（真路径含 `gov/` 段）⇒ 该字段本身是漂移在册，改动时可顺手更正（属同一文件的头块，不额外扩面）。

## 11. 落地前必须知道的现场态（本车道观测，非本车道造成）

1. **门侧再澄清**：`in_process_gate_registry.yaml`（111 个 `gate_id` 条目，正对照）grep `GATE-WORKTREE-DRIFT-WATCHDOG` ⇒ **0 命中**；
   全册仅出现 `worktree_drift_watchdog` **1 次**（在 `POOL-REGRESSION-DIRECTION` 条目 :755 的说明里，
   作为“四面同批”之一的快照层引用，非注册该门）⇒ **两份门册（gate_registry/in_process_gate_registry）都不是本参数的属主面**，
   §4 第 3 条结论加固。
2. **暂存区现在不干净（会连坐本次改动）**：`git status --porcelain -- src tests docs scripts` 于 `2026-10-12T13:30Z` 实测
   有**已 staged 的他人改动**（含 `architecture_issue_registry.yaml`、`gate_registry.yaml`、
   `in_process_gate_registry.yaml`、`capability_canonical_file_registry.yaml` 等；`git diff --cached --name-only | wc -l` = **77**）。
   本车道**未做任何 `git add`/写 tracked 文件**（这些是别班在飞工作）。
   ⇒ 总包落地 Q1 时：若走 GitCommitGateway 的 `--files` 清单，须防 §2/§3 所述“暂存区吸收他会话内容”；
   尤其 `architecture_issue_registry.yaml` 与 `gate_registry.yaml` **本身就是热文件**（根宪法 §1 第 13 条
   `safe_write_text` CAS 面 + 当前已 dirty），改 O4 文本那一步**必然与他会话撞车**——建议先 claim、
   并把“改 O4 文本”和“改 :98 数值”分袋，或等该册落地后再动。
3. **写入方此刻仍在产出**：`.runtime/quarantine` 最新目录名时间戳=`2026-10-12T11:26:54Z`（§10 表），
   今日 00:01Z 已有一轮 1,134 空壳清扫 ⇒ 改窗口的落地时点会直接影响首轮 blast 落在哪个 UTC 日历日
   （日级节流 `:613` 以 UTC 日为准，改动后**当日可能已置 `quarantine_last_sweep`，最早次日 00:0x 才生效**）。
4. **⚑ 本车道读的是“未落地的在飞版本”**（决定性口径提示）：
   `git diff --cached --numstat` 实测 **`worktree_drift_watchdog.py` 与 `test_worktree_drift_watchdog.py` 都已被他会话 staged**
   （模块 `+99/-6`；工作树与索引**无差异**＝我已核 `git diff` 为空）。
   - `_QUARANTINE_RETENTION_DAYS = 30` 在 **HEAD:98 / index:98 / 工作树:98 三态同值同行**（`git show HEAD:` 与 `git show :` 双测）⇒ **数值结论不受版本差影响**。
   - 但**函数行号受版本差影响**：HEAD 里 `_sweep_quarantine` 在 **:509**（＝旧案卷 §6 所记 :509-570 的出处），
     index/工作树里在 **:545**（本车道 §2 全部行号按此态书写）。
     ⇒ 总包落地时须**先让该在飞袋落地或与之同袋**（根宪法 §2.4 `--allow-multi-domain` 留痕 / §3 连坐规则），
     否则 `:98` 之外的任何行号级补丁（如 `[INVARIANTS]` :8、sweep 体内判定）都可能打在 99 行外来增量上。
5. 未覆盖面补充：未查他会话 staged 的 `test_worktree_drift_watchdog.py` 具体改了哪些断言（只测得该文件被 staged），
   故 §6 的“零测试红”结论对**该在飞测试版**成立与否未逐行核。

**本车道不改任何 tracked 文件、不删任何东西**；以上仅为案卷与机生表，裁定归总包。
