---
ttl: task_bound
title: S2 生命周期与临时区 · 挖矿簿（根目录净化 / CAS 残渣 / _working 陈化 / 永久-临时隔离）
created: 2026-09-27
sid: st-fms-chief-20260927
lane: S2
status: 挖干（3 项 Owner 门位外呼已标注，不阻塞无主件净化批）
---

# S2 生命周期与临时区 · 挖矿簿

> 迁址注：本簿原写于 fms_overhaul_20260927 旧战役区，现遵总筹迁址令落位于 `docs/_working/fms_overhaul/`；数据附件引用已同步新路径与 csv 格式。

## ① 职责一句话

把"永久/临时隔离"从口号变成机械可判定的事实：根目录 19 项残留逐一定性并给出经验证的删除处方、CAS 中断残渣全仓普查并挂防复发机制、docs/_working 2,827 件给出陈化处置与批量工具方案、为 FMS-HYGIENE 门供给"永久引临时"第三查的精确判定规则与棘轮基线数。

## ② 现状实测（2026-09-27，本会话实测）

### 2.1 基础盘面

- `git worktree list` = **106** 个注册 worktree（总筹口径"~90"为低估）：.aidrafts 29、.aidrafts_pool 1、.qoder/worktrees 9、.runtime/commit_queue 6、.runtime/tmp 7、.worktrees 54。
- 根目录全部可疑项 `git ls-files` = 0 或仅白名单件（见 2.2 表），`git check-ignore -v` 证明全部被忽略：绝大多数命中 `.gitignore:262` 的 `/*` 根白名单兜底规则，`meta` 命中 `.gitignore:466` `/meta/`，`models` 命中 `.gitignore:402` `/models/`。
- **修正总筹两处**：`tmp/` 与 `vendor/` 实际存在（总筹初测清单误报缺失）；根目录定性后的"垃圾"总量比预估小，但 `models/` 15G 超预期。

### 2.2 根目录 19 项逐项定性表

| 项 | 内容抽样 | tracked | 归属判定 | 删除裁定 |
|----|---------|:---:|---------|---------|
| `nul` | 771 B 文件（cmd `dir /a` 验证实存）；内容=[pool] 落地环境失败日志、qid=q-dbg-0001 | 0 | 2026-09-25 22:27 commit_queue debug 会话用 `> nul` 丢弃输出，MSYS bash 下 `nul` 非设备、落成真文件（现版 `scripts/commit_queue.py:1736` 已改 `[drain]` 前缀且 grep `[pool]`=0，仅 pid 22232 的 .tmp 残渣副本含 `[pool]` → 写的是改造前版本） | **删**（专用方法，见 2.3） |
| `30` | 仅 `.runtime/sessions/st-bizmine-etft0-20260919/heartbeat.jsonl`（2 行：started→exited "session not in registry"，2026-09-18） | 0 | heartbeat 写者被传入 cwd 派生的 project_root，落在 `<root>/30/`；目录名 `30` 来源为参数泄漏事故 | **删** `rm -rf 30` |
| `test_dir` | 完全空目录 | 0 | 测试残留 | **删** `rmdir test_dir` |
| `tmp/` | 1.1G：`pg_backups/` 912M（architecture JSON 77MB×多份，最新 2026-09-25）、tick_subscriber/scheduler 轮转日志 10M×10、`scheduler.heartbeat`/`process_reaper.log`/`ch_health_probe.heartbeat` 等 **28 件近 24h 有写**；仅 `tmp/.gitkeep` tracked=1 | 1 | **活跃运行区**：reaper/scheduler/CH 探针/备份流的输出地，`.gitignore:302` `!tmp/` 显式白名单 | **保留**；`pg_backups` retention 另立（Owner 门位） |
| `vendor/` | 339M：Kronos 克隆 + kronos_weights | 0 | 消费者=占位预测器 `src/zephyr/signal_ashare/ml_forecast/kronos_tsfm_predictor.py:19-21`（MOD-SIG-050 远期候选、"轻量占位实现"、重启三条件未满足）→ 权重当前零消费 | **可删**（Owner 门位：可重新下载；或移 G:/backup） |
| `ZephyrAlpha/` | 嵌套目录，`.runtime/sessions/` 下 3 个会话 heartbeat（st-sim-launch-20260923 / st-ibt22-recovery-20260925 / st-backup-cold-20260925-audit），全部 "session not in registry" 即退 | 0 | 会话以 `D:\ZephyrAlpha\ZephyrAlpha` 为 cwd 启动的双拼路径事故 | **删** `rm -rf ZephyrAlpha` |
| `st-audit-fix-20260924/` | 仅 `.runtime/sessions/--session/heartbeat.jsonl`（sid 字面量 `--session`=CLI 参数解析 bug；2026-09-24 即退） | 0 | 同名真 worktree 在 `.aidrafts/st-audit-fix-20260924`（worktree list 有登记、locked）；根目录这份是 heartbeat cwd 事故残渣 | **删** `rm -rf st-audit-fix-20260924` |
| `st-ff-last-20260918/` | 完全空目录 | 0 | 会话残壳 | **删** `rmdir st-ff-last-20260918` |
| `st-stkind-20260916/` | 仅 `.runtime/sessions/--session/heartbeat.jsonl`（2026-09-16 即退） | 0 | 同上，`--session` bug 事故件 | **删** `rm -rf st-stkind-20260916` |
| `_diag/` | 80K：Windows 自启动项诊断（Adobe/QMT/iFinD/Edge txt + cleanup ps1，2026-08-06） | 0 | **机器级诊断垃圾**，与项目无关，被塞进仓根 | **删** `rm -rf _diag` |
| `_journals/` | skill_events.jsonl / skill_transitions.jsonl | 0 | **活跃系统输出区**：写者=`src/zephyr/autonomy_core/skills/skill_observability.py:79` `_EVENT_LOG = Path("_journals/skill_events.jsonl")`（相对 cwd） | **保留**（迁移=代码改动，列 B7 可选治本） |
| `logs/` | 63M：backup_report_2026-07 批量 JSON + auto_fix/ | 0 | **活跃**（96 件近 7 天有写）；library_hygiene 已管辖（`_LOGS_DAYS=30`） | **保留** + 月批滚动清理 |
| `runtime/` | 248K：phase2_reports（2026-08 回测报告） | 0 | **陈旧**（近 7 天 0 写入）；生成物、非真源 | **归档后删**（移 G:/backup 或入 hygiene 月批候选） |
| `meta/` | locks/dim_D5.lock（CH metadata 泄落物） | 0 | `.gitignore:462-466` 显式锚定的已知泄落区 | **保留**目录约定（1K，无行动） |
| `models/` | **15G**：qwen25-7b-base + qwen25-7b-sft-v1 | 0 | `.gitignore:398-402` 注释声称"旧已删除的ML模型目录"——**与盘面矛盾**（目录在且 15G），疑 SFT 工作复建 | **Owner 门位**：确认消费者后移 `data/models/` 或 F: 盘，再删根副本 |
| `acceptance/` | 5.2M：screenshots | 0 | 陈旧（近 7 天无写） | **引用核查后删** |
| `strategy_archive/` | 仅 README.md（4K） | 0 | **合法常驻**：README 自证写者=`zephyr.governance.lifecycle_governance.strategy_archive.archive_strategy()`（61_lifecycle §3.9 归档四件套物理终点） | **保留**（空置系统区，勿当垃圾） |
| `session_logs/` | 33 tracked（2026/04-05，会话复盘 YAML） | **33** | 死约定：2026-05 后零新增；tracked 件禁工作树直删 | **退役走 git 流**（归档 docs/_archive/ 或保留为历史，禁 rm） |
| `__pycache__/` | 2 个 .pyc（sitecustomize 等） | 0 | Python 字节码缓存，可再生 | **删** `rm -rf __pycache__` |

### 2.3 `nul` 保留名删除方法（已验证，未对真件执行）

实测结论（本会话逐一试错）：

| 方法 | 结果 |
|------|------|
| Git Bash `ls/stat` | 能显示（MSYS NT 直通），但**不可作为删除手段验证** |
| `cmd /c dir D:\ZephyrAlpha\nul` | 失败（解析为 NUL 设备）；`dir` 也不支持 `\\?\` 前缀 |
| PowerShell 5.1 `Get-Item -LiteralPath "\\?\D:\..."` | 失败：`找不到驱动器 "\?\D"`（provider 层不支持设备路径） |
| **Python `os.stat/open/os.remove` + `\\?\` 扩展路径前缀** | **成功**：真件读取成功（size=771, mtime=2026-09-25 22:27:11） |

删除法已在沙箱 `D:/ZephyrAlpha/.runtime/tmp/s2_nul_probe/` 端到端验证（创建同名件→`os.remove` 扩展路径删除→成功→目录清零）：

```bash
/c/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe -c "import os; os.remove(chr(92)*2+'?'+chr(92)+'D:'+chr(92)+'ZephyrAlpha'+chr(92)+'nul'); print('removed')"
```

（`chr(92)` 构造反斜杠是为免疫 bash/JSON 多层转义；等价 Python 脚本写法 `os.remove(r'\\?\D:\ZephyrAlpha\nul')`。备选 `cmd /c del "\\?\D:\ZephyrAlpha\nul"` 文档可行但本次未独立验证。**禁用** explorer/裸 `rm nul`。）

### 2.4 CAS 残渣普查（.tmp.<pid>.<hash> 族）

- 全仓（scripts/src/docs/data/config/tests/tools/.github/architecture_model/schemas 十区）`*.tmp.*` = **17 枚**：scripts/ 15（backtest 5、commit_queue 2、governance 5、ch 1）+ catalogs 2（alert_threshold_registry.yaml.tmp.21732.70ad97c19748、infrastructure_registry.yaml.tmp.45444.0611b7de7ae2）。另 catalogs 有 2 枚手抄 `.bak`（capability_canonical_file_registry.yaml.bak 2.4M/09-21、candidate_module_registry.yaml.bak_pre_one_question 1.0M/09-26 23:43）。总筹口径 5 枚只覆盖 catalogs，漏 scripts/ 15 枚；总筹提到的 `.ruling_registry.yaml_et0ow618.tmp` 确已消失。
- **机制判定**：残渣命名 `<name>.tmp.<pid>.<12hex>` **不是** `file_utils.py` 的 CAS 写——`atomic_write` 临时件命名真源=`src/zephyr/shared/io/file_utils.py:107-111`（`.{name}_` + 8 位随机 + `.tmp`），`safe_write_text`（file_utils.py:527）第 632 行委托 atomic_write。仓内 grep 此命名零命中 → 写者是**外部编辑器/工具的 CAS 写**（pid 戳+hash 戳，进程中断即残留）。治理层已认识此模式：`scripts/governance/registry_dedup_audit.py:57` 扫描时显式过滤 `.tmp.`/`.bak` 名。
- **tracked 判定**：catalogs 全部残渣/bak `git ls-files` = 0（rc=1），`git status` 均为 `??` untracked——删除不影响任何 git 状态。
- **禁删例外**：`candidate_module_registry.yaml.bak_pre_one_question`（09-26 23:43）是对**在途脏文件**（`git status` MM）的术前快照，归属会话未落地前可能是唯一未提交副本——**禁删至归属会话落地**。`capability_canonical_file_registry.yaml.bak` 同理降级为"缓删"（其正本亦在途 MM）。
- 已有清扫器：`scripts/ops/cleanup_runtime_tmp_residue.py`（MOD-INF-046，dry-run 缺省/--execute/PID 存活+TTL 双判定）只覆盖 `.{name}_XXXXXXXX.tmp` 族且限 .runtime/tmp 作用域——**不覆盖** `.tmp.<pid>` 族。

### 2.5 docs/_working 普查

- tracked = **2,827**（总筹口径 2,822）；盘面 2,820 件、71MB、盘面无主 3 件。
- **mtime 分桶：&lt;7 天 = 2,290（81.2%）｜7-30 天 = 530（18.8%）｜&gt;30 天 = 0**。>30d 桶为零说明 mtime 被 git 操作（checkout/merge/stash）频繁触碰，**mtime 不可作寿命判据**——陈化判定必须改用 frontmatter `created`/`ttl`。
- ttl 覆盖率抽样（30 件均匀抽样）：**30/30 = 100% 有 frontmatter 且有 ttl**；取值 task_bound 27、`"task_bound"`（带引号变体）3 → 机器判读必须 yaml-parse 而非正则裸匹配（引号变体是现成陷阱）。
- 死引用：`docs/_working/fms_overhaul/_data/deadref_missing_2498.csv`（2,498 条，原 .txt 已转 .csv 并随迁址改路径）中 `_working/` 目标 = **630** 条（总筹口径 631，±1 为计数口径差）。
- 归档目的地已存在：`docs/_archive/` tracked 131 件。

### 2.6 永久区→临时区引用普查（FMS-HYGIENE 第三查基线）

- 永久区（tracked `docs/` 去除 `_working/`、`_archive/`）= **5,135** 件；ttl 分布：`permanent` 4,200 + `"permanent"`（带引号）810 + 无 ttl 125（覆盖率 97.6%）。
- 引用 `_working/` 或 `.runtime` 的永久区文档 = **235** 件，其中 ttl=permanent = **224** 件 → **支柱-4 违规种群 = 224，即棘轮基线**。重灾区是 `_registry/catalogs/` 各册（alert_threshold_registry.yaml、architecture_issue_registry.yaml、candidate_module_registry.yaml、capability_canonical_file_registry.yaml、directory_registry.yaml 等正文引用 _working 工作文）。

## ③ 六向台账

| 向 | 内容（证据） |
|----|----|
| 真源 | 生命周期语义唯一候选真源=frontmatter `ttl` 字段（.md）与 `[TTL]` 头（.py，如 scripts/governance/generators/library_hygiene.py:19）；**目录级生命周期默认从未立法**（.gitignore:262 `/*` 白名单是"tracked 合法性"名单，不是生命周期法）；.runtime 卫生真源=AGENTS.md 根宪法 §9 运维红线第 4 条；资产退役真源先例=zephyr.governance.lifecycle_governance（strategy_archive README 自证）；heartbeat 路径格式真源=`src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py:47-49,124-126` |
| 写者 | 根残留写者=三类事故：①heartbeat 调用方传 cwd 派生 project_root（6 处残骸实证，写者本体 heartbeat_daemon.py:126 参数正确）②MSYS bash 下 `> nul` 落真文件（nul 实件）③外部编辑器 CAS 中断（17 枚 .tmp.<pid>）+ 手工 .bak（2 枚）；_working 写者=各会话 staging/promote；tmp//logs/ 写者=reaper、scheduler、CH 探针、pg 备份流（28 件/日活） |
| 消费者 | `scripts/governance/generators/library_hygiene.py`（月度卫生四类扫描，只读零删除，INVARIANTS 见其 :8）；`scripts/ops/cleanup_runtime_tmp_residue.py`（.runtime/tmp 一次性清扫，:1-14 头注）；`scripts/governance/registry_dedup_audit.py:57`（残渣名过滤）；process_reaper keep 名单（data/runtime/process_reaper_keep.txt）；strategy_archive 消费者=lifecycle_governance.archive_strategy |
| 漂移史 | `.gitignore:398-402` 注释"旧已删除的ML模型目录" vs 盘面 15G 实存（模型复建未回写文档=文档矛盾实例）；总筹三处计数漂移（worktree ~90→106、_working 2,822→2,827/2,820、死引用 631→630）——印证"计数必须机械生成"（宪法 §4.2）；`[pool]`→`[drain]` 日志前缀漂移留在 nul 与 .tmp 残渣中成为断代证据 |
| 冲突面 | **他会话在途禁碰**（见 ④.3）；catalogs 目录 4+ 件 MM 在途、state_vocabulary_registry.yaml 有 `D`+`??` 成对状态（结构性中途态）；.runtime/commit_queue/** 6 个 serializer worktree 活跃；.bak_pre_one_question 归属会话未落地 |
| 净零方案 | 零新工具：检测挂 `library_hygiene.py` 既有月批（+1 扫描类：CAS 残渣；+1 升级：class① 改 ttl/created 判龄）；删除处置沿用其"候选清单+Owner 月批"既有语义；`cleanup_runtime_tmp_residue.py` 保持 one-off 不扩面；FMS-HYGIENE 新门由 S1 立法承载（本簿只供给判定规则与基线数 224）；根目录净化是纯删除零新增；heartbeat cwd 治本=调用方改锚 REPO_ROOT（每处 1 行，非新模块） |

## ④ 施工处方

### 4.1 B7 根目录净化批（可执行，全 untracked+ignored，不动 git 索引）

前置：RULE-GUARDIAN（reaper 存活）→ 逐条执行 → `git status` 复核零变化（被删项均不在索引）。

1. 无主小件（立即，零风险）：
   ```bash
   rm -rf 30 test_dir ZephyrAlpha st-audit-fix-20260924 st-ff-last-20260918 st-stkind-20260916 _diag __pycache__
   ```
2. `nul`：用 2.3 已验证的 Python 扩展路径命令（禁裸 rm）。
3. `acceptance/`：先 `grep -r "acceptance/" docs/01_policies_and_standards docs/03_modules --include=*.yaml` 引用核查 → 无引用则 `rm -rf acceptance`。
4. `runtime/`：248K phase2 报告 → 移 `G:/backup/zephyr_phase2_reports_202608/` 存档后 `rm -rf runtime`（生成物不进 docs/_archive，免污染文档区）。
5. `models/` 15G、`vendor/` 339M、`tmp/pg_backups` 912M：**Owner 门位**（磁盘资产+可能复用的权重/备份），给 Owner 三选一：原地保留+登记 / 移数据盘（F:）/ 确认后删。不阻塞 1-4。
6. `session_logs/`：tracked，退役须走 `scripts/git_commit.py --session st-fms-chief-20260927 --files ...`（git rm 流），建议移 `docs/_archive/session_logs_2026H1/` 并留 successor 指针；本批可不做。
7. 治本（防复发，各 1 行级改动，B7 可选）：heartbeat/skill_observability 等以 cwd 推导项目根的调用方统一锚 `zephyr.shared.io.paths.REPO_ROOT`（涉及 `src/zephyr/gov_enforcement/rule_bridge/` 调用链与 `src/zephyr/autonomy_core/skills/skill_observability.py:79`）；bash 脚本禁 `> nul` 惯用语（改 `> /dev/null`，入施工 SOP 检查项）。

### 4.2 B8 _working 陈化与 CAS 清零批

1. CAS 残渣：`git ls-files` 复核全 untracked 后删 17 枚 `.tmp.<pid>` 件；catalogs 2 枚 `.bak` **缓删**（归属会话落地后随 B8 尾批删）。
2. 防复发（净零挂接）：`library_hygiene.py` 增第⑤扫描类 `cas_residue`（匹配 `*.tmp.<pid>.<hex>` 模式常量+`*_pre_*.bak` 手抄备份，全 tracked 区，只读候选入 HYGIENE.md 报告）；同批把 class①（docs/_working 30 天）判龄依据从 mtime 改为 frontmatter `created`/`ttl`（mtime 已证不可靠，见 2.5）。
3. _working 处置策略三类：
   - **活跃保留**：<7 天（2,290 件）或被活跃战役引用——不动。
   - **到期归档**：7-30 天（530 件）且 ttl=task_bound 无活跃会话 → promote 到永久真源位或移 `docs/_archive/`（先例 131 件）。
   - **过期删除**：S1 治愈后的 630 条死引用目标件 + 归档后仍无引用件 → hygiene 月批 Owner 机械判定删除。
4. 批量工具：**无现成 promote/archive 命令**（grep scripts/ 无 promote 工具，本簿实测缺口）——B8 以 `library_hygiene.py` 升级版为唯一入口出候选清单，处置动作用 `git_commit.py` 逐批落地；若需 promote 语义，B7/B8 二选一地补一条子命令进 library_hygiene（不另立新脚本）。

### 4.3 他会话在途禁碰清单（硬约束）

- `docs/01_policies_and_standards/_registry/catalogs/` 全部 tracked 在途件（candidate_module_registry / capability_canonical_file_registry / module_translation_registry / rule_catalog_registry / trial_ledger_registry 均 MM；state_vocabulary_registry D+?? 对）——B8 只删无主残渣，不触正本。
- `candidate_module_registry.yaml.bak_pre_one_question`、`capability_canonical_file_registry.yaml.bak`（在途术前快照）。
- `.runtime/commit_queue/**`、`.runtime/tmp/*_wt`、`.aidrafts/**`、`.worktrees/**`、`.qoder/**` 全部 106 个注册 worktree。
- `data/runtime/process_reaper_keep.txt`、`.runtime/workspace_alerts/`、`_journals/`（活跃写者）、`tmp/` 与 `logs/` 中 7 天内活跃日志（只走月批滚动）。
- `strategy_archive/`（合法空置系统区）。

### 4.4 FMS-HYGIENE 第三查判定规则（供 S1 立法引用）

- **"永久区文件"机械定义**：满足任一即永久件——(a) frontmatter `ttl` yaml-parse 后 ∈ {permanent}；(b) 无 ttl 但 tracked 路径属于永久默认集 = `docs/` 去除 `_working/`、`_archive/` + `src/` + `scripts/` + `config/` + `schemas/` + `.github/` + 根 tracked 文件。临时默认集 = `_working/`、`_workspace/`、`.runtime/`、`tmp/`、`logs/`、`*_working` 同族。
- **判定规则**：永久件正文不得引用临时默认集路径（匹配 `_working/`、`_workspace/`、`.runtime`、`/tmp/`）；豁免三类——① successor_of/墓碑去向指针（S5 落地前先按路径字段识别）②卫生报告自身行（HYGIENE.md 类清单的扫描目标路径）③棘轮基线白名单（存量 224 件入生成基线，只减不增）。
- **基线数**：永久引临时 = **224 件**（2.6 实测）；CAS 残渣 = **17+2 件**（清零后基线=0）；ttl 引号变体 = 810+3 件（判读器双兼容，规范化不做硬性期）。
- **新写逃生**：确需引用临时件的新增永久写，必须先 promote（临时真源升格为永久副本再引用副本路径）——与宪法 §2.9 "staging 成果 promote 才算交付"同构，不需新通道。

## ⑤ 自审闸三态

**状态：挖干**（施工代理拿簿可直接开工 B7 无主件净化 + B8 残渣清零 + library_hygiene 挂接；判定规则与基线数已可直接交 S1 立法）。

缺口外呼（不阻塞开工）：

1. `models/` 15G / `vendor/` 339M / `tmp/pg_backups` 912M 处置需 **Owner 门位**三选一（4.1.5）。
2. promote 子命令语义缺失（4.2.4）——B7/B8 需择一挂接或声明手工 promote 仪式。
3. `cmd del \\?\` 备选删除法未独立验证（Python 法已端到端验证，为主处方，无碍）。

证据复现口径：本簿全部数字由本会话 2026-09-27 实测（git worktree list / git ls-files / git check-ignore -v / git status / os.walk+stat / 全文 grep）；总筹口径差异已在 2.1、2.4、2.5 逐条标注。
