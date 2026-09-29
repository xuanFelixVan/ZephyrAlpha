---
ttl: task_bound
---
# 审计遗留修复总包 · 台账（LEDGER）

> sid=`st-audit-fix-20260924` ｜ 立项 2026-09-24 14:3x ｜ 骨架=`audit_fix_skeleton.md` ｜ 尺册=`cross/00_channels_and_rulers.md` §二
> 交付纪律：每条结论标【亲验】（本包跑过并贴读数）或【引述】（案卷/他人所记，未复算）；
> 交付必附三清单（裁定/执行/复查）——见 §3。

## 1. 五件进度（Owner 令 ①②③④⑤ 逐件）

| 件 | lane | 状态 | 落地通道 | 验收判据 | 读数 |
|---|---|---|---|---|---|
| ① 提交链基底（最急） | L1 | 施工毕+7 尺全绿 | 队列 | grep≥1 且红测检出漂移 | 修前 grep=0/C4=HARD【亲验】；worktree grep=6 |
| ② 裁定册复燃 2 行 | L2 | **已被属主批吸收**（本包同修不同抢，未投该册） | 属主 bag `st-cleanup-final-…-0009` 落地 | HEAD 侧三值 grep=0 | **实测 0**【亲验 f53316c6f9 后】 |
| ③ 三件悬空 .py | L3 | 定性+生成侧治本+图归零 | 队列（passthrough） | GOMAP 硬=0；HEAD 版图报 3 幽灵 | 双证到手【亲验】 |
| ④ 计数失真 | L4 | 施工毕，worktree GATE-21 PASS | 直提（gate/script/importlinter）+ 检测器常驻 | `--check` rc=0 | 修前 rc=1 报 5 项【亲验】 |
| ⑤ align HEAD 锚定 | L5 | 施工毕+双锚并报 | 队列 | 同函数盘 0 硬 / HEAD 3 硬 | 【亲验】 |

## 2. 心跳（实测 `date` 注入，不估算）

- 14:3x 冷启动四闸过（PATH 3.12.8 / cleanup 14 死锁 / reaper last_run=14:27:23 killed=0 / worktree `.aidrafts/st-audit-fix-20260924` 心跳 PID 27136）。
- 15:0x 四取证子代理回卷（L2/L3/L4/L5），三条案卷被本包复算改口（见 §4 自否证）。
- 15:1x L1 首袋 0001 实测 `base_head=None`（因跑的是主区未修 CLI）→ 改投 worktree 已修版 CLI → 0002 `base_head==dev`、三件带 blob、新增件 None（正确）。
- 15:2x 0002 死信＝`GATE-PRECOMMIT-RUN hook=['ruff-format']` → 按处方格式化 → requeue→0003。
- 15:3x-15:4x L3/L4/L5 施工+红绿双证；GATE-21 在 worktree 由 rc=1(5 项) 转 rc=0。

## 3. 三清单（交付面）

### 3.1 裁定清单（本包按"第一性原理+专业实践"自裁，Owner 醒后可覆）

| # | 事项 | 本包裁定 | 理由一句话 |
|---|---|---|---|
| R-1 | 基底口径取 dev HEAD 还是会话 HEAD | dev HEAD | 落地侧语义是 `diff(base,dev)`，用会话 HEAD 会把自算改动判成"他人推进"⇒系统性假冲突；且与 machine 车道同源不另立口径 |
| R-2 | 缺基底时注册表合并是否继续兜底 `old_dev^` | 否，fail-closed 死信 | 兜底已被两晚"0 增 N 删"实证为杀手；死信可见可恢复，静默吃条目不可查 |
| R-3 | 存量 47 只 `base_head=None` 袋是否另治 | 加时间基底兜底（他会话后落同路径即冲突，无证据则放行） | 正门修复救不了已入袋的存量；今晚仍会互吃 |
| R-4 | `base_blob=None` 能否当"新增件"语义用 | 否，一律按"基底不可知"死信 | JSON 里键缺失与值 null 不可分，误读会让合并器复活已删条目 |
| R-5 | GOMAP 幻影 3 是否等属主落地窗自愈 | 否，治生成侧 HEAD 基 | 案卷的"等窗重跑"只治当次；rglob 口径不改则每次脏区重跑必复发 |
| R-6 | 是否代投三件他包 .py | 否（登记归属+让属主投） | 代投=EVAP-02 搭便车；且①②依赖模块同样未跟踪，单独落地制造 HEAD 悬空 import |
| R-7 | `rule_catalog_registry.yaml` 本包是否投 | **不投** | 主区盘上已被他会话重生成到位（292/292 自洽），同修不争件；本包只留常驻检测器 |
| R-8 | GATE-21 自洽检查作用域 | 先只点尺Q 实测出的两册 | 扩全 catalogs 面会在他包在飞时打红无辜提交；扩面成本=加文件名一行 |
| R-9 | 三值 `related_arch` 置空是否丢信息 | 不丢（可追溯性外置本簿） | 案卷"真身在 affected_files"部分失真——册内指针确会丢，故本包把 id→文件行号登记进 L2 §子环节3 |
| R-10 | 主区 index 的 RR 陈旧层（含会删 第 411 号裁定/#412 的 36 行） | 不代修，登记首条风险 | 宪法第 3 章第 4 条 他会话在途违规 owner 责任制 |

### 3.2 执行清单（改了什么）

- 提交链：`scripts/git_commit.py`（+13 行：基底与 base_blobs 接线）、`scripts/commit_queue.py`（`EnqueueOptions.base_blobs`、两处 base_blob 填充、CLI enqueue/requeue 自取基底、`requeue_dead_item` 透传）、
  `scripts/governance/commit_queue_landing.py`（新增 `resolve_base_head`/`resolve_base_blobs`/`_entry_base_blob`/`_legacy_base_drift_reason`/`_GW_OWNER_RE`；`_merge_registry_file` 去 `old_dev^` 兜底；reroute 车道补 base_blobs）。
- 校验面：`src/zephyr/gov_enforcement/registry_alignment.py`（单读口 + `source` 参数 + HEAD 批量缓存）、
  `scripts/governance/d5_architecture/generators/align_all.py`（第 5 步双锚并报；第 9 步两条文案改准）。
- 生成面：`scripts/governance/generate_governance_map.py`（HEAD 树入选集）、`scripts/governance/generators/generate_script_manifest.py`（同口径）、
  `src/zephyr/governance/audit/_git_helpers.py`（共享件 `git_ls_tree_paths`，收敛口径防 FUNCTION-DUP）。
- 检测面：`scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py`（册内自洽 2 台 + `--auto-fix` 转真）。
- 派生产物：`config/governance_operations_map.yaml`（重生成，幻影 3 清零）、`scripts/governance/script_manifest.yaml`（452→448）、`.importlinter`（+`zephyr.library`）、两册标量归位。
- 数据：`ruling_registry.yaml` `#383/#387` `related_arch` → `[]`。
- 测试与案卷：`tests/governance/test_commit_queue_base_head.py`（7 例）+ `docs/_working/audit_fix/**`（骨架+5 lane+横切+本台账）。

### 3.3 复跑清单（Owner 一条命令可复核；E11 亦按此跑两轮）

```bash
grep -c "base-head\|base_head" scripts/git_commit.py                         # 期望 ≥1
python -m pytest tests/governance/test_commit_queue_base_head.py -q          # 期望 7 passed
git show HEAD:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml \
  | grep -c "MOD-L00-004\|PS-CTR-003\|MOD-INF-043"                           # 期望 0
python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py --check; echo rc=$?  # 期望 rc=0
python scripts/governance/d5_architecture/generators/align_all.py --no-report # 期望 硬=0（含新 HEAD 锚行）
python .runtime/tmp/audit_all_20260924/probe_stale_base_revalidation_inert_r9.py  # 期望生产读数转 SOFT
```

### 主区遗留字节（本包留下的未提交面，如实交代归属与用途）

| 文件 | 状态 | 内容 | 处置 |
|---|---|---|---|
| `gate_registry.yaml` | index 与盘 = 180/180，HEAD=174/180 | 本包 `--auto-fix` 产物（条目集与 HEAD 全等，只标量归位） | 由 0013/0014 之后的正门批或属主批落；**本包不 `git add` 抢落**（该册被他会话 claim 持有） |
| `rule_catalog_registry.yaml` | index 与盘 = 292/292，HEAD=274/292 | 同上（机道再生与本包复核同结论） | 同上 |
| `scripts/governance/script_manifest.yaml` | 盘=448（HEAD 基生成器产出），HEAD=503 | 本包跑已落地的新生成器产出，55 条幻影移除经逐条亲验 | 随 0013 正门落地 |
| `.importlinter` | 盘已含 `zephyr.library` | 生成器产出 | 随 0010 已落（HEAD 已含，核对无差异） |

⇒ 这四件**不是孤儿脏文件**：每一件都是"已落地生成器"的确定性输出，且都在本包待落袋的清单里；
若传送带恢复，正门落地即自动收敛主区。若长期不恢复，`apply_*.py` + 本表即完整重放依据。

## 4. 自否证与案卷改口（本包自己抓的，含对审计班三条）

- **S-1**（对审计班尺Q）：`rule_catalog total_files=274 vs 292` 复算后**条目集与 HEAD 完全一致**，
  但盘上已被他会话修到位 ⇒ 本包不改口"陈旧"定性，只改口**处置**（R-7：不投）。
- **S-2**（对案卷 §尺O 第 7 轮）：GOMAP 面积分母非 3——HEAD 版 `script_manifest.yaml` 同样带 **4 条 NOT_IN_HEAD 幻影**，
  同病灶第三例，案卷未载 ⇒ 已并入 L3 §子环节4。
- **S-3**（对案卷"处方 (i) 捆族内条目可送标量"）：实测**条目落地、标量仍留旧值** ⇒ 该处方不成立，已在横切 §一 标 ✗。
- **S-4**（本包自身）：阴性控制组首版用 pytest `tmp_path` 当"非 git 目录"，实测返回主仓 dev HEAD（它在仓内，
  `rev-parse` 向上穿透）⇒ 改 `tempfile.TemporaryDirectory()`。立法：做"非仓库"对照前先证目录不在任何仓内。
- **S-5**（本包自身）：L5 首版按主区**未提交**形态（`spec_path`/`base_dir`）写，worktree HEAD 形态下必 NameError
  ⇒ 改回 HEAD 口径并留接续注释。
- **S-6**（环境级发现，影响所有 worktree 施工）：会话工作树内 `import zephyr` **默认仍解析主仓**（可编辑安装 .pth），
  ⇒ worktree 里跑测试/工具会"测的是主区未改码"；本包所有 worktree 验证一律带 `PYTHONPATH=<worktree>/src`。
  连带后果：worktree 无 `config/.env.*`、无 DB ⇒ 集成级验证只能在主区跑。
- **S-7**（同族归因）：`TestCommitAutoFlagGating` 在 worktree 内 62s/条 LOCK_TIMEOUT，
  主区同一类 4.84s 全绿 ⇒ 归因＝S-6 使 worktree 测试撞**主区全局提交锁**（此刻多会话在提交），非本包改动。

## 5. 待窗 / 待裁（本包不能或不应自决的，全量列此，不夹带进代码）

1. 【风险·高】主区 index 的 RR 陈旧层：0 增 36 删，含删 `第 411 号裁定/#412` 与三值复燃 ⇒ 任何吸收该 index 的落地会同时带回两类倒退。属主=会话语义 owner 制（§3.4）。
2. 【待窗】`rule_catalog_registry.yaml` 标量 274→292 由在途袋落地即归零；本包检测器会持续报直到它落地。
3. 【待窗】三件他包 .py 落地后重跑 `generate_governance_map.py`（HEAD 基已就位，无需再改判据）。
4. 【门位·未触发】本包未做注册表净删：所有条目级变化均为幻影/标量（零真实资产净损，逐字段差分见各 lane）。
5. 【新立 F-AUDITFIX-DEREF-01｜派生册引用未入库文件＝clean checkout 必红】
   发现路径=静默窗内在 worktree 跑既有测试（主区同测 7 passed，worktree 1 failed，差异只可能来自"盘上有、HEAD 无"）。
   证据：`capability_canonical_file_registry.yaml:46117` 与 `module_translation_registry.yaml:56713` 均登记
   `src/zephyr/ai_layer/redline/negative_list_gates.py`，而该文件 **`git ls-files` 在册（已 add 未提交）＋ `git cat-file -e HEAD:` 不存在**；
   受影响的常驻校验＝`tests/governance/generators/test_generate_commit_guide.py::test_integration_real_repo_render_readonly`
   （指南生成器逐条验 `gate_digest.source_file` 存在性）。
   意义=这是 BLIND-02 的**镜像面**：align/门禁读盘 ⇒ "HEAD 缺文件"这类断裂在脏主区里永远读成绿，
   只有干净 checkout（新会话、CI、灾备恢复）才会红——而本仓 100% AI 施工恰恰高度依赖干净 checkout。
   处置（二选一，均非本包授权面）：① 属主批把该模块连同其依赖一起落地（正解，随 st-ailayer-final 收尾即闭）；
   ② 注册表净删相关条目＝高门位（AGENTS 第 5 章第 2 条"注册表净删→Owner"），本包不自动执行。
   本包贡献＝把该形态变成**可重放判据**（首版用 shell grep 被 YAML 引号形态污染出 245 条假阳性，
   已换 YAML 解析版并带双控制组——阴性=在册文件不误报 PASS、阳性=锚点必报 PASS【亲验】）：
   口径=只检代码面引用（`src/ scripts/ tests/ config/ schemas/ architecture_model/` 前缀），
   刻意排除 `docs/_working/**`（TTL 区合法消失，纳入即假阳性淹没，实测差异 245→160 全靠这一刀）。
   实测分母：HEAD 版 capability 册代码面引用 **2866 条，其中 160 条不在 HEAD**。
   160 条的构成（抽样判读，非全量定性）：绝大多数＝`scripts/ai_layer/*`、`schemas/categories/registry_ledger/*`
   等 st-ailayer 批在途件（随其收尾自解）；余下需逐条判"该落"还是"该从册摘除"。
   ⇒ 本包**不代裁、不代删**：逐条摘除＝注册表净删（高门位），且多数属他会话在途资产；
     但把判据与分母立此，使该面从此可复核、可缩表。判据脚本本体见
     `.runtime/tmp/audit_fix_20260924/backup/manifest.json` 同级的 `deref_probe`（会话收官前会把它的内容
     内联进本行下方，避免只活在临时区）。

```bash
python - <<'EOF'
import subprocess, yaml
def head(p): return subprocess.run(['git','show',f'HEAD:{p}'],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
def ok(p): return subprocess.run(['git','cat-file','-e',f'HEAD:{p}'],capture_output=True).returncode==0
seen=set()
def walk(o):
    if isinstance(o,dict): [walk(v) for v in o.values()]
    elif isinstance(o,list): [walk(v) for v in o]
    elif isinstance(o,str):
        s=o.strip()
        if s.endswith('.py') and s.startswith(('src/','scripts/','tests/','config/','schemas/','architecture_model/')) and ' ' not in s: seen.add(s)
walk(yaml.safe_load(head('docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml')))
ph=[s for s in sorted(seen) if not ok(s)]
print('代码面引用', len(seen), '幻影', len(ph)); print(ph[:10])
EOF
```
（控制组：`src/zephyr/governance/capability_lookup.py` 必须在册且不被报；
 `src/zephyr/ai_layer/redline/negative_list_gates.py` 必须在候选集且被报——两条本包皆实测 PASS。）

6. 【新立 F-AUDITFIX-PIDLIFE-01｜存活判据可被守护进程 pid 伪锁死】（高风险，交 Owner 定）
   实测：`SessionRegistry.get_session('st-ailayer-final-20260924')` → **pid=41380**，而 41380 正是
   `commit_belt_daemon`（05:14 起，常驻数天）；该会话心跳 740s 前刚刷新，其 `held_files=575`。
   在册判据（`session_concurrency.py` 头部 [INVARIANTS]）＝"pid>0 → PID liveness + TTL(3600s) 双判据"
   ⇒ **只要注册的 pid 恰好是常驻守护的 pid（pid 复用或gateway在守护内取 getpid），该会话就被永久判活**，
   其 575 项 claim 永不自动释放，可无限期挡住别人对这批热册的提交。
   本包实证后果：④ 的 `gate_registry`/`rule_catalog` 标量重落被该 claim 挡住（`claim_file conflict`），
   而该会话自身已无在途袋（pending/dead/processing 内零声明）⇒ "判活但不再干活"＝纯阻塞态。
   处方（本包不自动执行，理由：改存活语义＝高爆炸半径，可能在夜窗批量误判死会话→
   正在施工的 claim 被放掉，或反向把无辜会话判活；两种失败都比现在更坏）：
   ① 登记 pid 时禁止取自常驻守护（register 时 `pid` 必须是会话自身短命进程，或改记 `pid_kind`）；
   ② 判活加一条"pid 属于常驻守护白名单（belt/heartbeat/watchdog）时不得单独作为存活证据"；
   ③ 或按 `last_activity`（头部已声明它是"仅 register/claim_file/register_dependency 刷新"的独立锚点）
      作为第二轨参与 claim 释放判定——现实现只用它做 daemon idle 退出，未参与 claim 释放。
   复核命令：`python -c "import sys;sys.path[:0]=['src'];from zephyr.security.access_control.session_concurrency import SessionRegistry;import time;i=SessionRegistry().get_session('st-ailayer-final-20260924');print(i.pid, time.time()-i.last_heartbeat, len(i.held_files))"`

7. 【③ 残留三条 GOMAP 幻影的逐条归因与解法（18:4x 实测，全部可自愈或已给出口）】
   | 幻影 | 属主袋 | 现状 | 归零路径 |
   |---|---|---|---|
   | `scripts/governance/check_meta_question_audit_reconcile.py` | `st-metaq-20260923-0022` | **pending**（12:09 入袋，`base_head=None`＝存量） | 其落地后重跑 `generate_governance_map.py`；或按 T3 时间基兜底判冲突后属主 requeue |
   | `scripts/sector_line/build_gpu_input_pack.py` | `st-pipeline-final-20260924-0029` | **pending**（10:03，带基底 `602778fdef`） | 同上，且它带基底 ⇒ 已有快进保护 |
   | `src/zephyr/intelligence/budget_analyzer.py` | `st-ailayer-final` 三连死（0001 CREATE-GUARD 缺 3 件 .md token；0003 同因；0005 **修复后带基底仍死于 GATE-VOCAB 词表硬编码**） | 无在途袋 | 属主两步自解：①给其 3 个新 .md 补 creation_token（同袋投）②其新 .py 的词表改从 `*_vocabulary.yaml` 动态加载；**且该批 185 件已远超单批硬顶，须拆分**——本包不代投（代投＝把它的门禁违规搬到本包头上） |
   ⇒ 三条均**不需要本包改判据**：③ 的生成侧根因已修（HEAD 基），残余只是"属主代码尚未入库"，
     且 `align_all` 第 9 步已能把它们逐条报出（修前完全不可见）。

## 6. 并发让路实录（线间并行流水的真实代价与处置，逐条可复核）

| 时刻 | 事件 | 本包处置 | 依据 |
|---|---|---|---|
| 14:39 | `st-ailayer-final` 主区直提 ~140 件（含本包 L3 清单里的 `budget_analyzer.py`） | 继续避让；不碰其文件面 | 宪法 §3.4 + 记忆"并发施工期避让是硬约束" |
| 15:5x | 本包给 `ruff format` 传了 `scripts/` 目录，**误格式化 275 个文件** | 白名单精确还原 273 件，改动面回到 12+2；此后只对自家文件跑格式化 | 自否证 S-8（见下） |
| 15:57 | 属主批 `f53316c6f9` 落地：同时带走本包第②件（related_arch 清零）**和** `spec_path/base_dir` 重构 | ① 不投 `ruling_registry.yaml`（已被吸收，投了只会造 noop）；② worktree 复位到新 dev 后逐件重贴自家补丁，L5 改接其 `spec_path` 统一口 | 记忆 merge-relay / 让路纪律 |
| 15:5x-16:0x | 直提 `gate_registry` 被全局锁改道成"无基底袋"（exit 0＝假成功，HEAD 未变） | 只认 `git show HEAD:` 不认退出码；改为合入收官批随队列正门走 | 记忆"判据只认 git show HEAD:<file>" |
| 16:2x | 陈旧袋 0005/0006（pre-f53316c6f9 字节）仍在 pending，若落地会覆盖属主刚落的 `registry_alignment` | 收官批 0007 以同路径 compaction 自动清掉两袋（`supersedes=[0005,0006]`） | 队列 §6.2 compaction 语义 |

## 7. 自否证补记

- **S-8（本包，最严重的一次）**：对共享树给格式化工具传**目录**＝把别人/别处的文件一起改。
  275 文件中 273 个非本包面，若未被 `git status` 白名单核对即入袋，就是又一例 EVAP-02"搭便车"。
  立法：**格式化/lint/生成器类工具在本仓一律按显式文件清单调用；入袋前必做 `git status` 白名单核对并还原面外文件。**
- **S-9**：`ruff check` 报 4 处 I001，逐一对 HEAD 复算后归因＝3 处 HEAD 本有（不顺手修，避免面外扩）、
  1 处系本包把 `import subprocess` 插错位置（已修）。教训：**报红先分"我引入"还是"存量"，前者必修、后者另案**。

- **S-10（自写总闸的假红，第 1 轮就抓到）**：本包总闸 v1 的 C5 断言"尺T/尺U 生产读数应转 SOFT"——
  但那两把尺的"生产读数"分支是用 `enqueue_item(options=None)` 直接构造的，量的是**入队 API 的默认值**，
  而本包刻意保留该默认值不动（不破 `enqueue_item` 零 git 依赖不变量，测试靠它做全 tmp 隔离），
  故该读数按设计恒为 HARD ⇒ 我的检查项恒红＝假红。改法：尺T/尺U 只断言"控制组 PASS（能红能绿）"，
  生产面真信号换成 **C5b 修复后新入袋 `base_head` 非空率**（真实生产队列读数）。
  立法沿用仓内铁律：**判据要量的那个东西，必须先证明它随修复会动**。
- **S-11（第 1 轮其余 FAIL 逐条定性，防"把未完成当失败"）**：C4（tests 尚未进 HEAD）、
  C7（主区脏工作树下旧版 `generate_script_manifest` 按 rglob 算 452 vs 已修文件 448，新生成器落地后自洽）、
  C9-gate_registry（HEAD 仍 174/180，随收官批落地）——三条皆为"未落地"而非"修错"。

- **S-13（九尺总闸在我改动前后各跑一轮：8 绿 1 崩，崩的那条与我的代码无关，且是好消息）**
  静默窗内跑审计班 `redblue_ruler_suite.py` 全量＝`9/9 已跑，FAIL=1 [尺S]`（先过 `--self-test` 六条合成对照全对）。
  归因三查：①主区盘上 `registry_alignment.py` **尚不含本包 L5 改动**（在 0010 袋里未落地）⇒ 崩的那次跑的是我未碰过的码；
  ②读它的控制判据 `ok = (len(e_head) > 0 and len(e_disk) == 0 and len(e_tamp) > 0 and len(e_anchor) == 0)`
  ——把"缺陷仍在"（`e_head>0`）写进了**活性判据**，于是第②件在 HEAD 被修好（`e_head` 3→0）后它必自判"读数作废"，
  属本仓反复立法的**恒红尺**（分不清"已修"与"尺坏"）；③本包另写 v2 把"活性"与"缺陷面"解耦
  （活性只由 篡改注入必>0 ＋ 历史自洽锚点必=0 两控决定；HEAD/盘差值才作面积读数）
  ⇒ v2 实跑 `尺活性 PASS，HEAD 面读数=0 ⇒ SOFT（已修）`【亲验】。
  处方（交维护班，勿留在我区）：审计班探针第 68 行按 v2 口径改一行即可；
  本包 L5 落地后更根本的解法是**生产函数自带 `source="head"`**，探针不再需要重定向 `CATALOGS_DIR`。

- **S-14（本包自己造的耦合，抓到并补硬）**：⑤ 让 `align_all` 给五个 check 传 `source=`，而调用方与被调方
  必须同批生效——0010 落地后两册都在 HEAD 里是一致的，但**主区工作树仍挂他会话未提交的旧版
  `registry_alignment`**，实跑 `align_all` 即抛 `TypeError: unexpected keyword 'source'` →
  被外层 `except` 吞成"注册表层整层降级跳过"＝**比偏斜本身更坏的静默失明**（该层此前一直是跑的）。
  补法：`_layer2_family` 仅在 `src="worktree"` 时退回盘读并打显式 WARN（偏斜消除后 WARN 自动消失，
  不是长期兼容层）；`src="head"` 时**不拿盘读冒充 head 读**（那会把"测不到"谎报成"盘侧失明=0"），
  而是抛给既有 HEAD 锚 WARN 分支诚实呈现。立法：**改共享函数的消费方时，必须同时问"盘上/在册版本
  不一致时会怎样"，并保证失败方向是"报不出来可见"而不是"整层不报"**。

### 顺带澄清一处"看着像我改坏了"的读数（避免后人误追）

`align_all` 第 9 步在主区报 **10 条机生层幽灵**，其中只有 3 条属 HEAD 版 map
（`check_meta_question_audit_reconcile.py`／`build_gpu_input_pack.py`／`budget_analyzer.py`，即案卷原悬空 3），
另 7 条（`meta_question/wo006/*`、`wo_a2legs/*`）＝**他会话未提交的盘上 map 条目**被如实照出。
修前两侧同读盘 ⇒ 这类"盘引用、HEAD 无物"完全不可见；修后由 HEAD 基 scan() 自动显形。
⇒ 这条红**不是回归，是 ③ 生效的证据**；处置归该会话（其 map 增量落地或撤 edits）。

- **S-15（第二次因同一根因死信，教训升级）**：文档袋 0009 死于 CREATE-GUARD「无 creation_token」。
  我 15:5x 确实登记过 8 条 token，但**登记只写在 worktree 的册里，册本身没跟着进袋**（它在 0008 里，0008 死了）
  ⇒ 落地侧读 dev 上的册，当然读不到 ⇒ 死信。
  立法：**creation_token 与它保护的新文件必须同袋**——同袋时 gate 读的是暂存态，登记与新建件同时可见。
  （"登记一次就完"是错觉；登记的持久性取决于登记册是否落地。）
- **S-16（④ 的标量被回退一次，已重落）**：首笔 `052c2817f4`(16:28) 落地后 1 分钟被 `fc039cc891`(16:29，
  他会话机道袋) 回退成 174——那袋入袋时刻早于本包正门修复 ⇒ 无基底 ⇒ 快进判定无从触发。
  这是"修复有时效边界"的实物证据：**base_head 修复只保护修复之后入的袋**，存量袋另由 T3 时间基兜底。

- **S-17（仓库自有命名门把我包设计打回，一次死信学到）**：GATE-NAMING 的 **N-16 要求 basename 全局唯一**，
  我按"每 lane 一个 `00_overview.md`"的直觉做了 5 份同名文件（分目录合理，但本仓按文件名唯一性立规），
  0015 因此死信。改法＝`L<n>_<lane>_mining.md` 唯一名，并同步 token 登记册路径与骨架/文内交叉引用，
  改后做**引用一致性自检**（正则抽出全部 `docs/_working/audit_fix/...` 引用逐个 stat）＝悬空引用 0。
- **S-18（本包最重要的机制级新发现：compaction 会把内容"悬空在两袋之间"）**
  袋 0013 入袋时声明 **10 件**、`done` 且 `landed_id=5aa14c8ceb`，但该 commit 实际只含 **1 件**（script_manifest），
  且 0013 的 `files` 现只剩那 1 件——其余 9 件（登记册+8 文档）是被**后袋 0015 的同路径 compaction 抽走**的，
  而 0015 随后死于 N-16 ⇒ **9 件既不在 0013 也不在 0015 的待落集里＝悬空在两袋之间，且 0013 记着 done**。
  这是案卷在册的"同 sid 后袋静默吞没"的**加害者侧实证**：吞没本身按设计发生，但**"前袋记 done 而后袋死亡"
  这一组合没有任何告警**＝假成功的新亚种（LAND-01 的近亲）。
  本包应对（三条纪律，写给后续所有会话）：
  ① **终批一次性投足**：需要同时落地的件（尤其"登记册+被登记件"）必须在同一袋，投出后不再追加同路径袋；
  ② 每轮收尾前用 `git show HEAD:<path>` 逐件核收，**不认 done**；
  ③ 若必须追加，先查前一袋是否已被抽件（读 pending 袋的 files 与入袋时件数对比）。
  建议登记给属主包的修闸需求（本包不自修 landing，避免与在途改动叠加）：
  compaction 抽走某袋全部剩余件时，该袋应转 `dead/superseded-empty`（或至少在 done 回执里带
  `files_landed=1/10` 的数量差），而不是记 `done` 且零提示。

## 8. 落地凭据（可复核）

- 第①件落地笔＝`c58da6cb06`；`git show HEAD:scripts/git_commit.py | grep -c base_head` = **6**【亲验】。
  主区工作树已收敛同一版本 ⇒ 此后**任何会话**经 `git_commit.py --enqueue` 入袋都带基底（不只在野会话各自修）。
- 修复生效的**生产现场双证**（不是测试里的证）：
  ① 袋 0007 被新快进判定拦下——`冲突：入队基底 f53316c6f9 之后 dev 已推进且触及同路径
  [scripts/commit_queue.py, scripts/git_commit.py, scripts/governance/commit_queue_landing.py,
  tests/governance/test_commit_queue_base_head.py]`；放在修前这就是一次静默整覆盖
  （覆盖掉本包 3 秒前刚落的 L1 代码）。
  ② 袋 0004 被 §6.4 陈旧基底重校验判 `cascade_stale`——`base_blob` 此前恒空 ⇒ 该检测器结构空转，现在有数据可判。
- 让路记录：第②件由属主批 `f53316c6f9` 吸收，本包未投该册（避免制造一次 noop 假落地）。
- 激活面如实记：常驻 `commit_belt_daemon`（PID 41380，05:14 起）持旧 landing 码，
  其落地侧改动（去 `old_dev^` 兜底、存量袋时间基底兜底）随该守护下次由计划任务
  `scripts/register_belt_daemon_task.ps1` 探测重拉后生效；入队侧与进程内自举排空路径已是新码
  （0007/0004 两次判定即由新数据驱动）。本包不重启共享守护进程（属基础设施动作，非本包授权面）。
- **S-12（红蓝对抗抓到自己产品的真 bug，最重要的一条）**：`_legacy_base_drift_reason` 首版把
  `git log` 的起点写成实时 `refs/heads/dev`，而 `_conflict_reason` 的入参是**调用方传入的 dev 点位**
  （CAS 重试每轮不同：`landing()` 循环里 `old_dev = self._dev_head()` 每次重取）。
  后果=重试第 2 轮起会拿"最新 dev"去判"上一轮点位"，判定与实到点位不一致（偏保守但语义错位）。
  抓法=为兜底函数补"同一把尺在两个 dev 点位上必须给出不同答案"的阴性控制组——
  恒绿型测试（只测一个点位）永远抓不到它。已修并补 4 例对抗用例（新增册不得被 fail-closed 误杀 /
  畸形项走受控死信不崩 / 时间不可解析保守放行 / 他人落地与同会话自落的分界）。
  ⇒ 尺册 16 例（11 L1 + 5 L3-L5）全绿【亲验】。
  追注：修好版随 0008 之后的补充批落地；`c58da6cb06` 里是缺陷版（判定偏保守，不放行坏数据，
  但语义错位）——**本包不掩饰自己第一版落地了带缺陷的代码，并给出被抓路径**。

## 9. 让道令执行与断点（16:35-17:20 提交静默窗，Owner 16:35 转达）

- sid=`st-audit-fix-20260924`（凭据=① worktree 目录名 `.aidrafts/st-audit-fix-20260924`；② 自有提交尾注 `GW:st-audit-fix-20260924`）。非 st-ailayer-final ⇒ 只执行 A 段。
- A.1 静默窗内**不再** commit/enqueue/requeue（此前已投的 0009/0010 两袋留在队列由传送带自行消化，不插队不手排）。
- A.2 不动主区暂存区：窗口内零 `git add`；本包成品一律留在自己 worktree。
- A.3 成品自保双份：`.runtime/tmp/audit_fix_20260924/backup/`（23 件 + `manifest.json` 逐件 sha256）
  ＋幂等重放脚本 `.runtime/tmp/audit_fix_20260924/apply_audit_fix_20260924.py`（只装字节不碰 git；`--check` 零写入自检）。
- A.4 未做任何自救动作：未 kill 守护、未手工 drain、未插队重投、未加旗绕门、未动 `_registry/` 热册（窗口内）、未动两个 hold 目录。
- A.5 17:20 后按 pending 计数决定节奏（16:31 实测 pending=54）。

### 断点与待办（醒后可直接从这行接续）

| # | 待办 | 现状与依据 | 恢复动作（窗口后） |
|---|---|---|---|
| T1 | **④ 被回退，须重落** | 我 16:28 笔 `052c2817f4` 把 `gate_registry total_gates` 改到 180；**16:29 他包袋 `fc039cc891`（st-backup-cold q-0022，入袋早于我的修复⇒无基底）又回退成 174/180**——这是 F-AUDIT-QUEUE-04 的活体复现，也正是本包存在的理由。修复版字节现存活于主区 index+盘 与本包备份 | 走直提通道重落一次（标量经队列必被吞，实测两次）；已扫队列 pending/dead/processing 内**无任何袋再带该册** ⇒ 重落不会再被在途陈旧袋吃掉 |
| T2 | 0009/0010 两袋落地核验 | 只认 `git show HEAD:<file>`，不认退出码 | 逐件核 HEAD 字节==备份哈希；死信则读 dead_reason 对症 requeue |
| T3 | 最终文档批 | LEDGER/L1/L4/L5 在 0009 快照之后又改过（S-10/S-11/S-12、§8、§9） | 一件 docs 批走正门 |
| T5 | **机道再生会回退本包 ③**（新发现，时序级） | 本包 16:28 提交触发 post-commit reconciler，机器道袋 `…-0011`(16:36) 携 `script_manifest total_scripts=503` 且**4 条 NOT_IN_HEAD 幻影全在**。原因=再生器读"当时盘上的旧版 `generate_script_manifest.py`"，而本包的 HEAD 基改造在 0010 里尚未落地 ⇒ **修工具未落地前，工具的旧输出已在途** | 0010 落地后，用已修生成器重跑 script_manifest 再落一次；复验=`total_scripts==len(scripts)` 且逐条 `git cat-file -e HEAD:<path>` 全命中 |
| T6 | `rule_catalog total_files` 仍 274 | 机器道袋 0011 虽带 292，但该册属 `catalogs/*.yaml` ⇒ 标量必被合并器取 ours 而丢（**这是该规律的第三次独立实证**：0006 队列版/0011 机道版/本包复现实验） | 待 0011 落地使 index==HEAD 后走直提单件；GATE-21 自洽台在此期间持续报红，不会静默 |
| T1' | **④标量重落遇 HELD-OVERLAP ⇒ 裁定=不硬闯、不代释放** | 两册 claim 由 `st-ailayer-final-20260924` 持有（held=574）；**判"死会话"不成立**：该会话 14:39 那笔正是短命进程 `scripts/git_commit.py` 提交的（与本包同款形态），"查不到常驻进程"不能证明其已死 ⇒ §2.7「死会话 stale claim 精准释放」前提不满足，本包不碰他包 claim | 属主批落地即归零：其盘上字节**已经是修好的** gate_registry 180/180 与 rule_catalog 292/292（本包已复核与 HEAD 条目集全等，只差标量）；期间 GATE-21 自洽台持续报红 ⇒ 不可能静默腐化。若属主批收尾后仍留失真，则一条命令即可：`git_commit.py --session st-audit-fix-20260924 --allow-non-worktree --no-auto-enqueue --files <两册>`（先 `gateway.claim_files` 且确认无 HELD） |
| T4 | 两轮零 + 终报 | 总闸 v2 已备（11→13 项，含 C5b 生产真信号） | T1-T3 完成后连跑两轮，然后清临时/释放 claim/关 worktree |

## 10. 收官时段的外部熄火取证（18:2x 实测，不属本包五件面，交维护班）

现象：dev 自 `4442b1b4f6`(17:35) 起 45 分钟零推进；本包 3 只袋（0013/0014/0015）滞留 pending。

取证（全部 `python scripts/commit_queue.py status` / 文件系统实测）：
- lease：`{"pid": 41380, "renewed_at": ...}`，读时 age=54s ⇒ **守护活着且在续租**；`daemon.online=true`。
- `processing/` 仅一只：`q-20260923-st-stress-20260923-0053`，**age=82169s≈22.8h**（被 claim 后工线程未归位）。
- 队首（head of line）：`q-20260923-st-stress-20260923-0055`，`waiting_s=82246`，lane=interactive，files=1。
- pending 总数 71（45 分钟内从 52 涨到 71——各方仍在入队）。

两处机制叠加（都是**在册已记**病灶，本包不另立案，只补一次现场实证）：
1. **队首=sorted(qid) 且 qid 含日期** ⇒ 昨天的 `20260923-*` 天然排在今天所有 `20260924-*` 之前；
   昨天 `st-stress` 一批 ~20 只遗留袋因此长期把住队首。
2. **interactive 车道无防饿死兜底**（30min 保护只覆盖 machine 车道）⇒ 上述排序结果没有逃生阀。
3. 叠加形态＝已登记测量结论"D3：工线程早退把整波永久占住"的现场复现——
   在册恢复路径是"下一波 `_recover_orphans`"，但波次不再起（守护只剩续租心跳线程）。

本包按纪律**没有**做的三件事（都属越权自救）：kill/重启 belt 守护、手工 serializer drain 抢 lease、
插队重投或加旗绕门。做了的两件都在册命令范围内：`status`（自带一次排空尝试）、`drain --max-items 3`
（结果 `SKIPPED: Serializer lease 被活体持有`——即设计上正确的互斥行为，未强抢）。

待落清单（本包侧，恢复后一条命令即可续做，成品字节已在备份且 apply 脚本幂等）：
| 袋 | 内容 | 落地后判据 |
|---|---|---|
| 0013 | creation_token 登记册 + script_manifest(HEAD 基 448) + 8 件案卷 | `git show HEAD:docs/_working/audit_fix/audit_fix_ledger.md` 非空；`C10 幻影=0` 转绿 |
| 0014 | align_all 偏斜补硬 + 案卷终态 | `C4` 在主区不再假红（skipped 或 passed） |
| 0015 | 测试遮蔽 skip 分支 + 案卷终态 | 主区 `pytest tests/governance/test_audit_fix_lanes_rulers.py` 无 FAILED |

重放路径（断点续做，零猜测）：
`python .runtime/tmp/audit_fix_20260924/apply_audit_fix_20260924.py`（把 23 件成品按 sha256 校验装回工作树）
→ 再按本包正门口径入队（`commit_queue.py enqueue --queue-root 主区 --worktree-root 工作树`）。
- **S-19（改名 saga 的正解：本地预跑权威判据，别再拿队列试错）**：本包为案卷文件名连死 4 袋
  （TTL 超时→CREATE-GUARD→N-16→N-01/N-13）。最后 30 秒就定位了：
  `python scripts/governance/d3_metadata/check_naming_convention.py --check-new-full <文件清单>`
  ＝**网关内嵌的同一条判据**（N-01~N-17 + N-16 全量），而我先前只跑 `--check-new`（仅 N-16 增量），
  所以漏了大写违规。立法：**新建文件前用与落地侧同一入口的 `--check-new-full` 预跑**；
  本仓文件名规则＝全小写 snake_case + 全局 basename 唯一（目录名同样禁大写 N-10）。
- **S-20（Windows 大小写不敏感是改名陷阱）**：`AUDIT_FIX_LEDGER.md` 与 `audit_fix_ledger.md`
  在该文件系统上是**同一个文件**——我第一次"改名"实际让两条拼写指向同一 inode（sha 相同），
  随后按大写名的 `rm` 把台账整体删掉了。当时我从备份恢复（备份救场一次）。
  立法：**大小写转换类改名必须经临时名两步走（或先写新名再核对唯一性）**，
  且改名后必须跑"`- file:` 条目集 vs 盘上实存集"双向差分，不能只看单个文件存在。
- **S-21（本包最重要的一次自我拦阻）**：收官前想把 2 条伪 token 条目用直提清掉，
  一算差分发现**我的工作树登记册比 HEAD 少 215 条他人登记**（基线旧于 f53316c6f9 之后各批）
  ⇒ 直提整册＝抹掉他人 215 条 token＝我自己正在修的 EVAP-02 病形。
  因此：①该热册一律不再由我整件投；②**反向证明了 ① 号修复有效**——我此前那只"缺 215 条"的
  登记册袋经条目级三向合并落地后，那 215 条在 HEAD 里**完好无损**（修前 `base=None → old_dev^` 兜底
  会把"陈旧快照不含"读成"theirs 主动删除"并执行）。这一条是本包五件里最硬的成效证据。
  残留 2 条伪条目（`AUDIT_FIX_AUDIT_FIX_*`）的外科式清法已登记给维护班：
  取 **HEAD 版**该册，删掉 `- file: docs/_working/audit_fix/AUDIT_FIX_AUDIT_FIX_00_skeleton.md`
  与 `..._AUDIT_FIX_LEDGER.md` 两个 5 行块，单件直提（**禁用本包工作树版覆盖**）。


- **S-22（① 号任务的真正收口点＝基底口径，不是基底缺失）**：21:4x 复查 C4 时发现
  本包在册的 S-12 修复在 HEAD 里**已经不见了**——追袋 `q-20260924-st-commitspeed-tbl-20260924-0005`
  落地时 `base_head=e500df6dfe` 有值，但快照来自更早的工作区 ⇒ 我第一版记的"入队时看到的 dev 尖"
  比自己的字节还新 ⇒ `diff(base, dev)` 恒空 ⇒ 快进判定失明 ⇒ 整文件覆回旧版。
  判据：**修复没被吃掉的前提是"基底＝字节真源"，而不是"有没有基底"字段非空**。
  治本三改（真源 HEAD＋merge-base 度量＋同 blob 短接）＋ `reroute` 通道同源化；
  永久尺 15 例（新增 4 例含反事实组）全绿，落地/集成回归 207 例全绿（＝新口径不破既有契约）。
- **S-23（撤掉一版我自己写错的收紧，留证据不留代码）**：同一批我曾按"装表时刻之后仍无
  `base_head` ⇒ 落地侧 fail-closed 拒收"收紧（把 31 件无基底存量袋划在时刻之前以求零冲击）。
  实测把 4 个测试文件的 30 例整批打死（它们按 `enqueue_item` 契约直投、不带基底），
  且实证今晚吃人的袋**恰恰有**基底——收紧既没打中病形，又把"测试契约"当缺陷改。
  已整段撤除（`patch_stale01b.py` 留在该时刻的读数），教训立法：**缺失型 fail-closed 必须先
  证明病形属于"缺失"而不是"口径"**，否则它是又一条恒红的闸。

- **S-24（④ 号任务从"检测器"升级到"治"：派生计数标量在落地侧自愈）**：GATE-21 的自洽台
  能报红，但红了两周仍没被治好，根因是结构性的：注册表合并器对**标量/头部行恒取 ours**
  （那是防热册头部被陈旧快照吃掉的正确设计），于是 `total_gates`/`total_files` 这类派生值
  **永远无法经队列落地**——本包 052c2817f4 直提成 180，随后被陈旧袋压回 174；rule_catalog
  停在 274 而实际 292。逐册直提＝把结构缺陷转嫁给"谁的基底恰好最新"，不成立也不可持续。
  现口径：条目合并完成后按段实际长度就地重算 ⇒ 任何一只碰这两册的袋都会顺手把标量修对。
  配对表 `_DERIVED_TOTAL_PAIRS` 与 GATE-21 selfcheck 同源，一致性由永久尺
  `test_landing_pairs_agree_with_gate21_selfcheck` 断言（两份配置各写一次必漂移）。
  保守面（红队 C7 补硬）：顶层同键多行 ⇒ 一律不动（YAML 重复键取后者、改写取前者，
  会把错值写进非权威行并让检测器永红振荡）；段非集合/标量非整数/形态不认识 ⇒ 不动只 log。
  遗留约束（红队 C8，登记不自行扩面）：同一标量若同时有"生成器扫描数"与"条目列表长度"
  两个权威，今日相等（180==180）故 latent；若二者日后不等，自愈会把生成器台判红并触发
  `--auto-fix` 整册再生。真解＝registry_family 册内显式声明"该标量的唯一权威是段长度"，
  属跨包改造，已登记为后续项，不在本夜动他包在飞的生成器。
- **S-25（今晚第二次被吃：CAS 重放整树回退，病形不在袋的 files 里）**：本包 0027 于
  22:33:19 落地 deffd84640，41 秒后 `q-20260924-st-mapbuild-20260924-0017`（属主＝st-mapbuild，
  **袋内只有 2 件**：能力册 + 其自己的 02_skeleton_writeback.md）落地 9de51e673f，
  把本包 4 件在册文件（landing 模块 +97/−16、永久尺 104 行、两份案卷各 13 行）全部回退。
  根因不在那只袋的内容里，而在 k=4 池的 CAS 冲突重放分支①：`prev_commit^{tree}` 是
  「base_dev + 本袋」的**全量快照**，袋里没列的路径在树里仍是 base_dev 的旧字节；旧判据只看
  "注册表路径是否重叠"，零重叠即 re-parent 到 new_dev ⇒ 期间他人落地的一切路径被整树退回。
  这与 09-22 fb5a7821d、09-24 通宵"0 增 N 删"是同一病族的不同腿（那条在合并器，这条在重放）。
  治本：只有 `base_dev..new_dev` **零漂移**时才允许复用旧树（此时 re-parent 是恒等操作），
  否则一律在新 dev 上重建树（read-tree new_dev + prestage + write-tree）。
  永久尺 `test_cas_replay_does_not_revert_third_party_paths`：摘掉判据即红（已双向验）。
  同批红队补硬三件：①注册表族"dev 已删该件"不得被陈旧袋整文件写回（复活闸）；
  ②`base_head` 非 commit 形态走受控死信而非崩栈；③同会话连投多袋的同路径漂移若全部
  归属本会话 ⇒ 判为迭代放行（否则第二袋起系统性假死信，会把整个车队堵死）。
  属主侧无需返工：mapbuild 那两件事本身完好，回退只发生在本包的文件上。

- **S-26（④ 的诚实终态＝机制已落、数值等下一只碰该册的袋；并登记一条生成器分歧）**：
  本想在收工时把两个失真标量也一并落地，试了两条路都停手：
  ①**袋投 dev 原字节** ⇒ 合并器在 `ours==theirs` 处按 noop 短路（零合并零提交），自愈函数根本不会被调用
    ——这是它该有的行为（无内容变化不提空提交，假落地防线依赖这条不变式），不该为凑数造差异。
  ②**跑生成器**（`generate_gate_registry.py` 实测）⇒ 产出与 HEAD 差 **143 增/143 删**：除 `generated_at`
    与 `total_gates 174→180` 外，还把 `BLUEPRINT-AMODULE-CONSISTENCY`（已合并的**重定向锚点条目**，
    `entry: N/A (merged into BLUEPRINT-HEADER)`）整条替换成 BLUEPRINT-HEADER 的实体条目——
    即生成器与在册状态**本身不一致**。23:4x、在飞 40+ 袋的窗口拿它去刷热册＝会搅动他人条目，
    与 ① 号修复的目的正相反 ⇒ 不投。**登记为跨包后续项**：生成器须保留/生成重定向锚点，
    否则任何"顺手跑一下生成器"都会造成热册churn（本包 GATE-21 的 `--auto-fix` 通道同样命中此坑，
    已在此点名，交门禁属主批处理）。
  结论口径：④ 的**机制**（检测器自洽台＋落地侧派生自愈）已进 HEAD 并有永久尺；两个标量将在
  下一只合法修改这两册的袋落地时自动归零（今晚这类袋出现 5+ 次），期间 GATE-21 持续报红＝
  不可能静默腐化。**不谎称数值已归位。**

- **S-27/S-28（登记不代修：提交链"排序与存活类"偶发红，双证非本包引入）**：终验轮次里
  组合跑出现 3 例偶发红，全部落在多线程时序断言上，且**对照基座同样红**：
  ①`TestRealLanding50Commits::test_3_sessions_50_commits_zero_loss_fifo_no_piggyback`
    （:240「FIFO 破裂：dev commit 序 != qid 序」）——在 `ce0dc360b8`（`grep -c
    _drift_all_same_session|_heal_derived_totals`=0，零本包改动）新建工作树**单跑复现红**，
    配对跑（pool+integration）在对照基座也红一次；同码不同果＝间歇。
  ②`test_six_items_four_workers`、③`test_killed_worker_orphan_recovered_next_wave`、
  ④`test_renew_only_from_heartbeat_thread`：各出现一次，单跑/隔离跑在两个基座都绿（④ 连测
    2 次＋对照 1 次全绿）。④ 的构造即自带墙钟耦合（心跳间隔改 0.05s、`sleep(0.3)` 造续租窗口，
    断言"续租只来自心跳线程"），在本机 CPU 76-87% 的负载下必然有翻转概率。
  机理假设（交属主批判定）：`_pick_head` 改按 `(created_at, qid)` 后来先服务后，`created_at`
  只到**秒**粒度 ⇒ 同秒项并列，而 k=4 池门禁段并行＋dev CAS 串行使"实到序≠排序序"；这类断言
  把"qid 字典序＝落地序"当契约，与属主批自己在 `test_commit_queue.py` 里判定过的
  「旧断言 processed_qids==sorted(qids) 系把 bug 当契约」同族。建议口径（不代执行）：
  排序类断言改判"到达序集合相等＋逐件内容可追"，存活类断言把墙钟常量换成可注入时钟；
  或给同秒项加单调排队键。按 §3.4 owner 责任制本包不代改他包判据。
  轮次口径据实声明：终验轮次取"**每文件独立跑全绿**"为 PASS，组合单进程跑的上述偶发
  列入 NOTE 并逐条点名，不谎称零红、也不拿组合偶发冒充本包缺陷。

## 11. 终验轮次与收官读数（09-24 夜 → 09-25 02:3x，本包自跑，Owner 可原样复跑）

**轮次口径（据实声明，不谎称零红）**：一轮 ＝ 十台检查各跑一遍，全部读数取"在册面"
（`git show dev:<路径>` 或临时 `git worktree add --detach dev` 的净工作树），**绝不取主区工作树**
——主区当日有他会话 WIP（`registry_alignment.py` 盘上即为他包旧版），盘侧读数既会假红也会假绿。
C3 取"每文件独立跑全绿"；组合单进程跑的偶发红逐条落 NOTE 并给归因（S-27/S-28），不计本包 FAIL。

| 轮 | 结果 | 说明 |
|---|---|---|
| r1 | FAIL(5) | C4 主区假红（盘侧他包旧版遮蔽）＋C5/C7/C9 口径未收窄 ⇒ 全部转成在册面读数 |
| r2 | FAIL(1) | C3 组合跑 1 红（50 笔 FIFO 尺）⇒ 后证对照基座同样红 |
| r3 | FAIL(1) | C3 组合跑 1 红（six_items_four_workers）|
| r4 | PASS=ALL | 首张干净轮 |
| r5 | FAIL(1) | C3 单文件跑 1 红（renew_only_from_heartbeat_thread，构造自带 0.05s/0.3s 墙钟耦合）|
| r6 | PASS=ALL | 干净轮 ① |
| r7 | PASS=ALL | 干净轮 ② ⇒ 与 r6 构成"连续两轮零（本包可归因项）" |

r6/r7 共同 NOTE（收官时仍在册的两条外部项）：
1. **GATE-21 三条标量红**（`total_gates 174≠180`、磁盘-vs-生成 174≠180、`total_files 274≠292`）
   ＝ S-26 的处置：机制（检测台＋落地侧自愈）已进 HEAD，数值待下一只合法改这两册的袋自动归零；
   不谎称已归位。
2. **本包在途袋** q-20260925-st-audit-fix-20260924-0032（S-27/S-28 登记文本），
   由本号文档袋（0033）以严格超集取代入队——同 sid 同件后袋取代前袋是本仓队列既有语义（见记忆
   [[queue-same-session-later-bag-silently-supersedes]]），故本袋 message 已显式声明取代关系。

### 11.1 Owner 一条命令复核（不依赖本包任何临时件）

```bash
# ① 永久尺 27 例（① 号任务＝基底真源/快进判定/注册表合并/派生标量自愈/红队四条）
python -m pytest tests/governance/test_commit_queue_base_head.py tests/governance/test_audit_fix_lanes_rulers.py -q
# ② 提交链回归（逐文件；组合跑偶发红见 S-27/S-28，勿据此判退化）
python -m pytest tests/governance/test_commit_queue{,_landing,_integration,_pool,_landing_nightfix}.py tests/governance/test_commit_chain_campaign_20260922.py -q --timeout=600
# ③ 在册面关键符号（应为 9 处以上命中：真源 HEAD/merge-base/noop 短接/同会话豁免/复活闸/自愈/漂移判据）
git show dev:scripts/governance/commit_queue_landing.py | grep -cE '_noop_overwrite_paths|_drift_all_same_session|_heal_derived_totals|_base_had_path|if not drifted:|rev-parse\", \"HEAD\"'
# ④ ④ 号任务余红（应为 3 条，且只出现在这两册的标量上）
python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py --check
# ⑤ ⑤ 号任务 HEAD 锚读数（应 errors=0；盘侧旧版不再参与判定）
python -c "import importlib.util,sys;s=importlib.util.spec_from_file_location('ra','src/zephyr/gov_enforcement/registry_alignment.py');m=importlib.util.module_from_spec(s);sys.modules['ra']=m;s.loader.exec_module(m);print(m.run_all_registry_validations(source='head'))"
```

### 11.2 本包留下的两项"未做"（不是遗漏，是裁定后交接，均已就地写明判据）

1. 交互正门 `resolve_base_head` 在工作区 HEAD 不可解（unborn，如 session_worktree 刚建未提交）时
   仍落 None ⇒ 走时间兜底（fail-open）。正解＝**门侧拒投**并报错（目录是 git 仓但 HEAD 不可解即
   exit≠0），不在落地侧按"缺基底即拒"收紧——后者本包试过，实测打死 4 文件 30 例且没打中病形（S-23）。
2. `--allow-tracked-drift` 的清单口径仍是"工作区 vs dev 的差异"，陈旧工作区会把他人落地列入本袋；
   本包已在落地侧拦住其后果（真源基底＋CAS 不整树回退＋复活闸＋同会话豁免），门的清单本身应改成
   "只带与本会话自身 HEAD 有差异的路径"。两项均在 lane L1 子环节 5 末段与本报告 §未做 列明。
## 12. 全流通战役首批落地与两项在途（09-25 04:3x 追注）

- 两车道成品（L2 派生册＝生成器零 churn＋GATE-21 加严＋两册条目级对账；L1 门侧＝unborn-HEAD 门侧拒投三态判据
   + tracked-drift 改钉基底，其原"按 dev 取点"机理假设被车道实测**证伪**并改为"活 ref HEAD 被 Serializer 推进"）
   已由总包 `git merge-file` 三方合并同树复跑 49 passed 后入主队列 `q-20260925-st-audit-fix-20260924-0034`（14 件）。
- **在途 1（案卷未入库）**：战役 6 份作业簿（骨架 110 行＋L3 存活 135＋L5 auto-fix 150＋L6 业务全流通 150＋
   门侧 228＋派生册 347）因 CREATE-GUARD 需 creation_token；本包三次手工插热册均在 `creation_tokens` 段尾
   缩进/段尾键判定上失败并**当即回退**（复原后 YAML 可解析、tokens 10914 条），未污染在册面。
   已按"成品自保＋幂等重放"处置：案卷备份 `.runtime/tmp/chain_fullflow_20260925_dossiers/`（6 份）＋
   重放器 `.runtime/tmp/land_fullflow_dossiers.py`（五步通道：工作树内 batch_creation_tokens 登记 →
   键集"HEAD−新==空"复验 → 案卷与 token 同袋 → 只信 `git show dev:` 复验）。
- **在途 2（战役余面已挖出待施工）**：E00 普查定环节总数 N=17（七路互证枚举法），L6 业务面实跑判定
   通 3／半通 1／不通 3——不通三条为：做T矩阵双写手仍在、四张空表 0 行、CH macro_data 187 个 0 字节坏部件
   阻断 system 枚举面（⇒ CH-FINAL-GATE 类"读标度定容差"的尺会静默降级，须报红不得称全绿）。
   三条均属**破坏性数据操作或他车道常驻件**，04:3x＋实盘四禁窗口不自决，案卷内已给复现命令与处方。
- 更正一条自记：昨夜登记的"belt 守护仍旧内存码"已失效——实测 09-25 01:51:35 换血（PID 6756）且 epoch 零漂移；
   真残面是"纪元自检饿死窗"与注册工具指针悬空。
## 13. 死信闭环与拆分裁定（09-25 07:0x，本包自证两条）

- **0034 死于本包自己落地的检测器（正向证据，不是事故）**：`cascade_stale: 基底重校验不适用`
  点名 `commit_queue_landing.py`/`commit_queue.py` 等路径在 base 之后被他人推进。修前 `base_blob` 恒 None
  ⇒ 该检测结构性空转 ⇒ 陈旧快照静默整覆（昨夜两次吃掉在册修复的病根）；修后它第一次运行时拦住的
  第一个袋就是**我自己的**。重放方法＝`git merge-file` 三方（基座 77129e94b1 / 彼方 dev）：3 个文件 0 冲突、
  6 个文件 dev 未动，四套尺同树复跑全绿（door 10＋base_head 22＋derived_books 12＋gate_replay 15＝59）。
- **0035 死于 CLAIM_REQUIRED**：正解＝入队前 `gateway.claim_files`（已做），不是加旗绕门。
- **REGISTRY-MASS-DELETION 的真面目（登记给门禁属主批）**：预检对照的是**主区脏 index** 里他道未落地条目
  （报"18 条身份消失/208 增"），而本袋与 dev 逐键集差分删除集＝0（gate_registry 180↔180、
  rule_catalog files 292↔292、module_translation 只增 1、capability 只增 8）。⇒ 判定基线应取
  `<target 分支 HEAD>` 而非"当前 index/盘"，否则任何取 dev 为基的干净袋都会被主区噪声拦。
  本包走该门自声明的合法通道 `[allow-mass-deletion:<理由>]` 留永久痕，不改判据。
- **拆分裁定（预算与安全权衡，非偷懒）**：本袋只落"既有文件的修改＋tests/ 下免 token 的新尺"；
  需 creation_token 的新件（`gate_replay_selfproof.py` 与 8 份战役案卷）**继续留在备份**
  `.runtime/tmp/chain_fullflow_20260925_dossiers/` ＋ harness/尺也在 `.aidrafts/lane_ff_replay/`，
  重放通道见 `.runtime/tmp/land_fullflow_dossiers.py`。原因：登记工具 `batch_creation_tokens.py`
  的 repo 根取自身文件位置（＝主区），在工作树里跑恒"无待登记文件"；而本包三次手工插该热册均失败并
  回退（含 07:0x 一次把 T9 已登记的 8 条 token 随 `git checkout dev --` 一并丢弃，已确认删除集 0、
  重插待做）。工具应加 `--repo-root`/按 cwd 解析，属门禁属主批改造项，不在本夜动它。
