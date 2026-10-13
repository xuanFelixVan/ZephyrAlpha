---
ttl: task_bound
owner: st-maint5-20261013
campaign: 维护五班（接统筹 2026-10-13 03:0x 终版裁定＋接力令：P3 修 1a／J1 甲-0／C10-C13 sha 校对／P7 本体／死信 path 级抢救／丙 enforce 条件）
---

# 维护五班施工账 · st-maint5-20261013（2026-10-13 03:07 接令 → 当班自收，本机时间为准）

> 前任两班账＝`docs/_working/maint3_campaign/00_ledger.md`（§十一–§十三）与
> `.worktrees/st-maint4-20261013/docs/_working/maint4_campaign/00_ledger.md`（§〇–§八，未落地面＝
> 其袋被本班班账承接收口）；四案卷＝`.runtime/tmp/maint3_night/`，六提案＋逐件表＝`.runtime/tmp/maint4_night/proposals/`。
> 本班一条总账：**接力令三条前提被实测改判**（见 §一），其余五条裁定照令执行。

## 〇、工区与冷启动（逐条实跑）

1. RULE-ENV：`python --version`=3.12.8；`scripts/setup_dev_env.py --check`＝usercustomize exists+installed 指 D:\ZephyrAlpha。
2. RULE-GUARDIAN：`lock_files.py cleanup` 跑通（顺带自动 SALVAGED 两个死会话遗物 st-maint3/st-minedig2，本班未代裁）；
   `process_reaper --status` source=live、killed=0；计划任务 `ZephyrAlpha_ProcessReaper` 实测存在且"就绪"
   （⚠ 一条工具面教训：`schtasks //query //tn <名>` 不带反斜杠路径会报"找不到",按 `\\名` 或 CSV 全列表才读得到——
   在册"反斜杠/路径域"同族，本班第一把尺就差点把"任务不存在"误读成禁写）。
3. RULE-WORKTREE：本班默认隔离施工＝`session_worktree.py create st-maint5-20261013 task-maint5-handover`
   → `.worktrees/st-maint5-20261013`（分支 `ai/st-maint5-20261013/task-maint5-handover`，建时 HEAD=当时 dev 尖 a1e8866ecd），
   会话入 SessionRegistry、心跳 daemon pid 26284。未降级直改主区（主区 03:2x 实测仍带他班 1 枚受保护 WIP，见 §三.3）。
4. RULE-CAPABILITY-LOOKUP：`CapabilityLookup(scan=False).find(<kw>, session_id=...)` ×2 查询已落
   `.runtime/lookup_audit/st-maint5-20261013.jsonl`（注：审计根由 REPO_ROOT 解析＝主仓 `.runtime/`，
   不在车道内；本班第一次在车道目录 `ls` 找它＝0 命中，是尺的位置错不是没写）。
5. 提交一律 `scripts/git_commit.py --session … --files … --enqueue`（零裸 commit）。

## 一、接力令逐条对账（判据只认实测与 dev 面读回）

| 令 | 本班处置 | 实测读数 |
|---|---|---|
| 一·归因定案 | 采信并复核：主区 WIP 已清回基线 | 03:2x 复量 `thresholds.yaml` 盘面＝`aa4988d42dfb`＝dev 同值（卡片所称"aa4988d4 复量在案"独立复现）；gateway/recon/takeover 三件盘面==HEAD 全 SAME；`validate_rules_integrity.py --check`＝"全部 138 个规则文件完整[基线面=head]" |
| 一·P7 批为实施真源／J1 甲-0 先行 | 甲-0 已按零判据变更落地成 6 行注入＋两支钉，待前置袋落地后投（§三） | 两面判别探针复现四班读数（§三.2） |
| 二·① 抢救区禁删禁动 | 遵守：只读对拍，未删未改 | 抢救区 11 件 sha 逐件在册（§三.4 表） |
| 二·② 死袋 blob 第二副本／sha 必比 | **照令比对，结论＝卡片给的 sha 值错、方向对** | q-0039 五枚 blob 实测＝c4526845/f9067a9f/adebb1c6/199ce91f/5e361f6d，**查无 d589de0f**；测试件正确版＝`5e361f6dbdf9`（`parents[4]`），抢救区与 st-maint4 车道两份均＝`4ac2ddd426cc`（`parents[3]` 错版）⇒ 抢救区那份不可用于重投 |
| 二·③ 重投带 `--base-head $(git rev-parse dev)` 现值 | 本班两袋均走 `git_commit.py --enqueue`（base 由队列自动取当下 dev 尖，实测 0001 base=投袋时尖） | 0041 的 base=abeb59ffb7 逐件对拍：11/11 件 base_blob==dev 现值、两枚中间袋零触碰 ⇒ 可净落地，本班不抢其基 |
| 三·① 死信按 path 级抢救（748 path/136,375 行分批救；env 258 整批与三链超集两前提作废） | **执行完毕**（§四）；归档动作一律未做（两前提作废＝不执行） | 2,699 件／67,092,472 B 抽出，写后读回 2,699/2,699 OK；其中唯一副本面 748 件与四班普查**逐数全等** |
| 三·② P4 收盘锚（原修法会造"少跑"事故，改判成立） | 知悉，未施工（F5 涉判据面须带裁定号同批，非本班自决） | 四班 P4 案卷 §建议默认＝F5 |
| 三·③ P2 先戴帽不扩容 | 知悉，未施工（扩容＝Owner 门位花钱面） | 四班 P2 §归因改判在案 |
| 三·④ P3 修 1a 升最优先 | **本班首件，已投袋**（§二） | q-20261013-st-maint5-20261013-0001 |
| 三·⑤ 丙翻 enforce＝条件批 | **条件不可得，如实报零样本不翻**（§五） | ①丙 03:59 才落 dev；留痕面 `.runtime/gate_audit/ch_write_guard.jsonl` 至 04:0x 尚未生成＝样本 0 |
| 四·三班在途袋照飞 | 照飞：0040 已落（03:39）、0041 在途，本班未代投未改其面 | `commit_queue.py status` 逐袋读态 |
| 四·①丙已落地（q-0003 验收） | **接令时不成立，03:59 成立**——本班 03:2x 实测 dev 面守卫符号 0 命中、flags 无该旗、测试件未跟踪；03:59 复测三判据齐（20 命中／mode=shadow 在册／`tests/data/data/db/test_ch_write_guard.py` 已跟踪） | 时间线双读数都留档，防后人按单点读数互斥 |
| 四·gate-errcode 红测试＝出分诊案卷、禁修禁进关键路径 | 案卷已由四班出（`P5_errcode_window_reading.md`，33KB/9 节）；本班复测同读数并**证伪一条在册附带断言**（§五.2），未修任何东西、未把任何测试送进任何路径 | 车道 cwd 实跑＝8 collected／7 passed／1 failed，红针同为 `TestRegistryToCode::test_active_entries_have_live_definition`，4 条 stale 全指 `src/zephyr/data_eng/*` |
| 五·三班 §13.7 代补录 | **已投袋**（§六） | q-20261013-st-maint5-20261013-0002（docs-only） |

**三条被实测改判的令内前提**（另起一节留旧账，不改令文）：
①"①丙已落地"＝接令时刻不成立（03:2x），03:59 起成立；
②"C10-C13 重投（sha 校对版）"＝**不该由本班投**——该簇已由三班在途袋 0041 承载（11 件全量、含 `parents[4]` 修正版），
  按"同件只投一袋"与四班已确立的硬理由（非族件分支只有 `theirs==base／ours==base／否则真冲突`），
  本班再投＝把在途 0041 打成死信并丢其唯一增量；
③卡片所引正确版 sha `d589de0f` 在 q-0039 五枚 blob 中查无（正解＝`5e361f6dbdf9`）。

## 二、首件 P3 修 1a（creation_token 登记正门断裂）交付账

病灶（本班自建零写入探针复现，`python .runtime/tmp/maint5_20261013/p3_probe.py`）：
生产脚本形态（`python <路径>`，`sys.path[0]`=脚本目录、仓根不在 sys.path）下
`schemas.__file__=None`（site-packages 那份命名空间包）＋`import zephyr.governance.registry_ledger.api` ⇒
`ModuleNotFoundError: No module named 'schemas.categories'`；正对照＝PYTHONPATH 含仓根时 api/ddl 全 OK。
复算命令失效一条另记：四班/三班案卷写的复算腿 `python .runtime/tmp/maint3_night/probe2.py scriptmode`
**已失效**——该文件现内容是 ClickHouse 列名标定探针（被 CH 案卷调查覆写），故本班重写探针而非转录旧读数。

修法（＝令内"修 1a"，姿势同在册先例 `reconcile_worker.py:425-429` 的 ARCH-104 治本，两处按实测改造）：
1. 仓根入 `sys.path` 用**尾位**而非先例的头位：`registry_ledger_ddl` 是被队列池工与治理链在任意进程导入的库件，
   头位改写全进程包优先级；实测（探针条件 T）仓根居尾时常规包 `schemas` 仍胜过 site-packages 的命名空间份。
2. **补第二条腿**：命名空间包的 `__path__` 在首次导入时即算死，晚装配 sys.path 对它无效——
   同进程先触 `schemas` 的模块（如 `ex_core/execution_report_producer.py:61`）都造得出该次序，
   故已载命名空间份时把仓根真身直接接进它的 `__path__`。这条不是加码：本班第一版只做腿 1，
   用例 2 当场把它测红，才知遮蔽有"次序"这一维（四班案卷的炸面表也未列这一形态）。

证据面（全在车道实跑）：红证＝新用例两支在改码前 rc=1 带原文 traceback；
绿证＝改码后 `28 passed`（本文件全量）；突变自证＝摘腿 1 ⇒ 用例 1 红／摘腿 2 ⇒ 用例 2 红／复原 ⇒ 双绿；
回归面＝`tests/gov/governance/d3_metadata/` 全目录＋`test_registry_ledger_context_anchor.py` 223 passed，
`ZEPHYR_TEST_PG=1` 下 `test_registry_ledger.py`＋`test_registry_ledger_baseline.py` 31 passed；ruff check/format 全过。

端到端验收（存在性≠内容判据）＝落地后在主区以**不带 PYTHONPATH** 的
`python scripts/governance/d3_metadata/batch_creation_tokens.py` 真跑一次登记（本班班账自身即该次登记的对象，
四班班账的 token 一并代登），读数见 §六。

## 三、J1 甲-0（GATE-INTEGRITY 判定面改读落地树）施工账＝备妥待发，前置未清

1. 落点（实测定位，非猜）：`git_commit_gateway.py::_run_precommit_channel` 的 env 字典构造处
   （`root = str(self.project_root)` 之后）加一键 `"ZEPHYR_WORKTREE_ROOT": root`；
   门本体/阈值/exit code/判定式零改动。`find_repo_root()` 自带"目标树无 `src/zephyr/__init__.py` 即回退原解析"
   的闸，故无伪造根风险。diff＝+6 行（其中 5 行为注释），`git diff --stat` 可证。
2. 判别探针复现（本班亲跑，池工 w0 与序列化器工作树两面）：不设 env ⇒ `root=D:\ZephyrAlpha`；
   设 env ⇒ `root=<该树>` 且非 OK 行只剩 2 枚 `MISSING(critical=False)` 陈旧锚点。与四班 §三之补同判。
3. **卡片要求的反向对照（"主区带他人 WIP 时不含该件的袋必须放行"）本班不自造**：
   造它需在主区给金-hash 受保护件下未提交改动，而当下 12 枚在途袋正排空——那会替全仓制造一次连坐死袋。
   天然红面此刻已在位：`capability_canonical_file_registry.yaml` 主区盘面 `6bd8bb33a602` ≠ HEAD `42359606bb42`
   （属主班 st-datalane2-20261012 在途，其袋字节在 blobs/ 与 blobs_archive/ 两面查无＝唯一副本，
   本班按 §四 令不动、亦不代清）。故反向对照改由"落地实测"承担：甲-0 落地后，任一枚含
   `scripts/governance/` 而不含 CAPCAN 的袋在主区带此 WIP 期间落地成功＝正证，取数口在 §七。
4. 前置未清＝本班不硬投：甲-0 要改的 `git_commit_gateway.py` 正被三班在途袋 0041 携带（blob c4526845cf1e）。
   非族件分支只有 `theirs==base／ours==base／否则真冲突`，双投必有一死；且本班车道件现基于**旧 dev**，
   0041 落地后若直接投＝回退弹（会洗掉 0041 的超时乙改动）。
   处置＝等 0041 落地→`git show dev:<gateway>` 重基本班 6 行→复跑两支钉与突变→再投（同法适用 §二 之后任何同件袋）。
5. **P7 本体（甲-1＋own 命中精确相等）本班已施工并自证完，排队等甲-0 先落**（同两文件，故必须串行不同袋）：
   - 归因面新增 `_precommit_own_evidence_text()`：在既有样板剥离之上再剥"门自己都不计数"的状态行
     （`[CHANGING_IN_COMMIT]`/`[UNTRACKED]`/🟡 即 critical=False 的 MISSING）。
     **债务棘轮键面（`_precommit_debt_keys`）继续吃 `_precommit_evidence_text` 不动**——
     两口径有意分叉并各写理由：键面问"这笔债是谁的"、归因面问"该不该拦这个袋"；
     若一并改，棘轮基线键会随证据面变化而漂移（在册"改一处牵动另一册"族），故不让它共用。
   - `_own_hit` 改＝计数违规行里的路径 token（复用 `_DEBT_PATH_TOKEN_RE`＋同一 lstrip 归一，
     `finditer` 逐 token 判）与本袋路径集**精确相等**；提不出 token 的行**保留原子串匹配**兜底
     ＝令内"精确相等"落地而不削检出（§八.2 已把这个取舍呈明）。
   - 证据面：五支钉全绿；突变自证＝把 `_own_hit` 还原旧子串码 ⇒ **恰好**两支"非计数解释位"钉转红、
     另三支（真 own 阻断／foreign 保持／`.sql` 集外后缀走兜底）保持绿 ⇒ 腿有判别力且强度未降；
     全文件 20 passed／3 failed，那 3 支＝**车道 cwd 存量假红**（用 dev 原码在车道跑同三支照样红，
     已用"还原 dev 字节复跑"证与非本改无关，主区 cwd 跑＝16 passed 全绿）。
   - 施工卡（**持久面**，tmp 面 24h TTL 不作为唯一副本）＝
     `.runtime/quarantine/maint5_p7_workface_20261013/`（7 件与 tmp 原面逐件 sha 全等已核）：
     正典码面 `gw_both_faces.py`（＝甲-0＋P7 全量，与本班车道现件同 sha）＋`test_both_faces.py`＋
     `p7_full_vs_dev.diff`＋`jia0_patch.diff`（仅甲-0）＋`msg_jia0.txt`＋投递器 `submit_jia0.py`。
     另存 `gw_p7patched.py`＝ruff format **之前**的那一版，留作读数溯源，别拿它当重放底本。
     （在册教训同族：重基自动器 `git show dev:<件> > <件>` 会把自己未落地编辑拍回旧面——本班投递器就干这事，
     所以重放底本先抄出 tmp 才允许它动手。）


## 四、死信 path 级抢救执行账（令内三·①，P6 逐件表）

谓词沿用四班 P6 普查尺不自造：`content_state ∈ {nowhere_but_blob, path_on_disk_differs, blob_purged}`。
工具＝`.runtime/tmp/maint5_20261013/p6_salvage_exec.py`（零 git 写、零删除、零覆盖他人面）。
目的地＝`.runtime/quarantine/maint5_salvage_20261013/<qid>/<path>` ＋ `MANIFEST.csv`；
选它而非 `.runtime/tmp/`（24h TTL 面）的理由＝`worktree_drift_watchdog._sweep_quarantine` 只清 `drift_<ts>`
规范命目录（其 docstring 自述"非标准命名（人工存证等）不碰"），故本目录不受 retention 腿吃。

读数（盘上实物对拍，非自报）：manifest 2,699 行、verify 全 OK、写后读回 sha 全等；
盘面 `is_file()` 计数＝2,700（2,699＋MANIFEST，按 is_file 分层数防"空目录计入"假绿）；
按态分＝`nowhere_but_blob` **748** 件（卡片口径，与四班普查逐数全等）／`path_on_disk_differs` 1,951 件；
总字节 67,092,472（唯一副本面 9.2MB 级＋会变薄面）。本班按**超集**救，
因后者"不丢但会变薄"且同处 blob 面；748 枚口径在 MANIFEST 里用 `content_state` 可精确切出。

未做且不该做的：归档（`dead-archive`）一支未动——令内已判"env 258 整批"与"三链 superseded"两前提作废；
真时限闸是未裁的 `blob_gc` phase2，本班不代裁。

## 五、两件的当班实测（丙 enforce 条件／errcode 案卷）

1. **丙翻 enforce＝条件不成立（样本 0），本班不翻。** ①丙 于 03:59 才落 dev（landed_id 80355020745e），
   dev 面内容判据齐（`ch_writer.py` 守卫符号 20 命中；`config/flags.yaml:58` `ch_write_guard: enabled=true, mode="shadow"`；
   新测试件已跟踪）。留痕面 `.runtime/gate_audit/ch_write_guard.jsonl` 至本班收班读数仍未生成 ⇒
   shadow 样本＝0。按在册"降级态与未触发同形"教训：0 样本既不能证"只命中在册已知触库测试"也不能证其反，
   翻 enforce 属"用零样本签字"，本班不签；判据本体已写进 flags 的 description（翻案条件与回滚手柄都在册），
   由有样本的任一班执行。
2. **errcode 一支复测同读数，并证伪在册"疑似常年空跑"一条。** 本班车道 cwd 实跑
   `pytest tests/governance/test_error_code_consistency.py -q --tb=line -p no:asyncio --import-mode=importlib`
   ＝8 collected／7 passed／1 failed（同四班 P5）。⚠ 三班账 §13.6 待办②说
   "gate-errcode-consistency 的 entry 仍指扁平化前旧路径 `tests/governance/`，疑似常年空跑"——
   实测该路径**文件就在**（`tests/governance/test_error_code_consistency.py` 在 dev 面存在），
   且该 hook 的 `files` 触发式＝`^(src/zephyr/.*\.py|architecture_model/contracts/error_code_registry\.yaml)$`，
   即**每一枚含 src/zephyr/*.py 的袋它都实际执行**。红之所以没拦袋＝失败面 4 条全指 `src/zephyr/data_eng/*`
   他域、被 own-scope 归因判 foreign 而 warn 放行。⇒ "修好即让它进关键路径"的顾虑**方向对但时点已过期：它现在就在跑**；
   要动的是那 4 条 stale 注册条目（他域归属，owner 责任制），不是 entry 路径。本班未修。

## 六、本班袋账（04:0x 快照；0003-0006 的终态袋账以 §十.1/§十.2 为准，勿据此册判袋）

| 袋 | 内容 | 态 |
|---|---|---|
| q-20261013-st-maint5-20261013-0001 | P3 修 1a（`registry_ledger_ddl.py` ＋ `test_batch_creation_tokens.py`，`--allow-multi-domain` 留痕＝门＋自家测试同批） | 投袋入账，态以 dev 面读回为准 |
| q-20261013-st-maint5-20261013-0002 | 三班账 §13.7 代补录（docs-only，只增证 dev 1008 行全数在位／prefix-equal True／H3 55→56） | 同上 |
| 待投 | 甲-0（gateway 6 行＋`test_precommit_channel_out_of_lock.py` 两支钉） | 前置＝0041 落地后重基（§三.4） |

## 七、复核命令（四条本班逐条抽出原样实跑；期望值＝同次实跑所得）

```
# ① P3 修 1a 病灶复现＋正对照＋尾位对照（零 PG 零写盘）
cd /d/ZephyrAlpha && python .runtime/tmp/maint5_20261013/p3_probe.py
#    期望三读数：E_scriptmode_no_pythonpath.out 含 "No module named 'schemas.categories'"；
#                A_pythonpath_repo.out 含 ""api": "OK "；
#                T_repo_at_tail.out == "TAIL_RESOLVED=D:\\ZephyrAlpha\\schemas\\__init__.py"
#    注：修 1a 落地后 E 也会转 OK——该探针判的是"仓根不在 sys.path 时可否导入"，
#        长期判别力尺请用 ②，不要用 ①。
```
```
# ② P3 修 1a 落地判据（内容级，不看 done 目录；未落地时 0）
cd /d/ZephyrAlpha/.worktrees/st-maint5-20261013 && PYTHONNOUSERSITE=1 python -m pytest tests/gov/governance/d3_metadata/test_batch_creation_tokens.py -k write_leg
#    期望：2 passed（突变自证见 §二：摘腿 1⇒用例 1 红、摘腿 2⇒用例 2 红、复原⇒双绿）
```
```
# ③ 死信抢救面计数（manifest 与盘上实物双口径）
cd /d/ZephyrAlpha && python -c "import csv,collections,pathlib;rows=list(csv.DictReader(open('.runtime/quarantine/maint5_salvage_20261013/MANIFEST.csv',encoding='utf-8')));c=collections.Counter(r['content_state'] for r in rows);v=collections.Counter(r['verify'] for r in rows);print(c['nowhere_but_blob'],c['path_on_disk_differs'],v['OK'],sum(n for k,n in v.items() if not k.startswith('OK')),sum(1 for p in pathlib.Path('.runtime/quarantine/maint5_salvage_20261013').rglob('*') if p.is_file()))"
#    期望：748 1951 2699 0 2700
```
```
# ④ 三班在途袋 0041 可净落地判据（base_head→dev 之间其 11 件零漂移）
cd /d/ZephyrAlpha && python -c "import json,pathlib,subprocess,hashlib;R=pathlib.Path('D:/ZephyrAlpha');b=json.load(open(R/'.runtime/commit_queue/pending/q-20261013-st-maint3-20261011-0041.json',encoding='utf-8'));n=lambda s:hashlib.sha256(s.replace(b'\r\r\n',b'\n').replace(b'\r\n',b'\n')).hexdigest();q=[f['path'] for f in b['files'] if n(subprocess.run(['git','show','dev:'+f['path']],capture_output=True,cwd=str(R)).stdout)!=n(subprocess.run(['git','show',b['base_head']+':'+f['path']],capture_output=True,cwd=str(R)).stdout)];print('DEV_MOVED_FILES=',q)"
#    期望：DEV_MOVED_FILES=[]（04:0x 实跑＝[]）
```

## 八、残余与待裁（交统筹／Owner，本班一律不自决）

1. **甲-0 与 P7 本体的投袋窗口**＝0041 落地之后（同件双投必有一死，§三.4）。若 0041 在排空中被判死，
   其内容归原作者（三班已收班）＝本班需按 blob 逐件重取字节后**先复现其改动再叠加本令修法**，那一步的工作量
   与风险都远高于"等它落地"，请统筹优先保 0041 而非让本班代投。
2. **P7 本体（own 命中改路径集精确相等）有一条本班不擅自走的方向**：把 own 判定从子串改精确相等，
   在其它 hook 的证据形态上会**降低 own 检出**（绝对路径、`./` 前缀、`path:line:col` 三类形态都可能在精确比较下
   失配⇒真违规被归 foreign 而 warn 放行）。本班拟的写法＝"路径 token 归一后精确相等 ∪ 原子串匹配仅作用于
   甲-1 剥离后的计数违规行"，使检出强度只增不减；若统筹要的是**纯精确相等**（子串整条摘掉），
   请点名，本班按点名执行并把"可能漏拦"的形态清单随批呈上。
3. **①丙 enforce**：shadow 样本 0，判据与回滚手柄都在 flags 的 description 里，由有样本的班执行（§五.1）。
4. **CAPCAN 盘面唯一副本**（6bd8bb33a602，属主班 st-datalane2-20261012，队列四面查无快照）＝本班不动不代清；
   它同时是甲-0 反向对照的天然红面（§三.3）。
5. **P4/P2/死信归档**三件按令未施工（判据面/Owner 门位/两前提作废）。
6. 四班 P5 §7 自报的一条窗口期异常（其车道被"外来写手"改脏）四班自己已证伪＝其主线程从队列 blob 物化的袋字节；
   本班承接该教训：本报告内所有"他班面"读数都按 sid/袋号定位，不按目录名猜归属。

## 九、P3 端到端正证（04:2x 实跑，非存在性判据）

生产脚本形态（`python <路径>`，PYTHONPATH 不含仓根）走正门三腿真登记成功：

```
cd .worktrees/st-maint5-20261013 && PYTHONNOUSERSITE=1 PYTHONPATH=<lane>/src \
  python scripts/governance/d3_metadata/batch_creation_tokens.py \
  --prefix docs/_working/maint5_campaign --created-by st-maint5-20261013 \
  --capability maint5_shift_ledger --merge-evaluation "跨域不同对象→不并：…"
→ 计划登记 1 条 → 登记: 新增 1 幂等跳过 0 冲突WARN 0；publish_snapshot v501 (noop=False)
→ 投影重打: quadrant=armed_initial wrote=True → OK: 已登记 1 条（register→publish→render）
```
（先 `--dry-run` 预览＝1 条零写入再实跑；前缀只指本班目录，不越权登他班件。）

三条附账：
1. 同形态在改码前必炸（红证＝§二 探针与四班班账 §六.7 现场第四例），改码后走通＝修 1a 的端到端正证；
   长期判别力仍看 §七② 的用例对，不靠这一次性成功。
2. render 把 PG 现值整册重打进**车道**投影文件（`git diff --numstat`＝+545/0，含他班未落地条目）。
   本班已把该册复原成 dev 现字节（该路径 `git diff` 复测＝空），**投影册不入本班任何袋**
   （在册：随袋提交他人未落地条目＝归属篡改；且统筹已判"禁出重打投影袋"）；在册追齐归册主车道 render 袋。
3. 本班班账自身的投袋时点＝**等 q-…-0001 落地且主区磁盘追平之后**：CREATE-GUARD 的 PG 正证腿在被遮蔽环境里
   静默失明退投影（四班 P3 §炸面新增），而落地面读主区磁盘码面；主区未含修 1a 前投本班班账＝大概率假拦死信。
   "落地即生效"实测支撑＝①丙 03:59 落 dev 后，主区磁盘 `ch_writer.py` 与 dev 与交付版三面同值 `cb453a07cc92`；
   顺带一条给 C12 的判据更正：该收敛落地的 sync 动作词记的是 **`index_shadow_clear`**，不是四班 §七② 等的
   `wt_fast_forwarded`——用事件名当落地判据会误判"未收敛"。

## 十、收班账与下一班口令（本班未做的事都点名）

1. 本班袋终态（**04:57 收班时点**实测；0005/0006 见 §十.2 代投表）：

   0001 processing（通道 55 台 hook 实跑中）／0003-0006 pending／0002 dead＝本班主动让路／dev 面四把落地尺此刻全 0（未落地就是未落地，别按 done 目录判）。
   收班时本班已放锁（先例＝维护四班 §八：claim 0 条而 q-0003 在飞，其后该袋正常落地）——留 stale claim 挡他班是更坏的一面。

   | 袋 | 内容 | 态 |
   |---|---|---|
   | q-…-maint5-0001 | P3 修 1a（ddl＋d3 测试件） | pending；base 面==dev 面逐件已验（可净落） |
   | q-…-maint5-0002 | 三班账 §13.7 首投 | **主动让路撤袋**（理由与可逆配方写进 dead_reason） |
   | q-…-maint5-0003 | 甲-0（gateway 6 行＋两支钉） | pending；base 面==dev 面已验 |
   | q-…-maint5-0004 | 三班账 §13.7 重投（改钉基正门） | pending |

   让路的硬理由＝**一条在册口径差**：`git_commit.py --enqueue` 的 base_head 取自**调用方车道 HEAD**，
   而 `commit_queue.py enqueue --base-head dev` 才钉 dev（本班 0002 的 base=a1e8866ecd 而该台账已于
   099c3c043b 被同班 0040 袋演进 ⇒ 非族件仲裁只剩"双侧皆改真冲突"一支＝注定死信；该 path 今日已为此死 8 枚）。
   附带把队列口径钉死在本账里（防下班再混）：**base_blob＝git blob sha1**（`blob <len>\0` 头），
   不是文件 sha256——本班第一把尺拿 sha256 去对 base_blob 得到"全 FALSE"的假矛盾，反推 0041 已知面才定口径。
   追加型台账（同册多人接写）投袋＝一律 `--base-head dev`＋`--worktree-root <本车道>`＋在车道 cwd 跑主区脚本
   （否则 WORKTREE-REQUIRED 拦、且队列根会落车道影子根）。

2. C10-C13 代投**当班做掉两组、留两组**（承载袋 0041 于 04:3x 判死，死因＝`TimeoutExpired: git commit --no-verify … after 60.0 seconds`＝在册"git commit 60s 超时簇"，**不是** GATE-INTEGRITY；其 11 枚 blob 逐只 sha 复核健在，且逐件对拍 base==dev 现面＝11/11 True，故代投不踩他班演进）：

   | 组 | 件 | 袋 | 代投前实测 |
   |---|---|---|---|
   | C11＋C12 | takeover_pending_gate／test_session_takeover_ledger／commit_queue_landing | **q-…-0005** | 自家测试面实测 `25 passed`（与三班自报数一致） |
   | C13 | scripts/session_worktree／rule_bridge/session_worktree | **q-…-0006** | 无新测试面（遥测探针由三班实测） |
   | C10 | ops_guard／reconciliation_registry／test_file_ops_enforcement | **未投**（见下） | 代投字节面实测 **1 failed／41 passed**：
   | 超时乙丙 | thresholds／git_commit_gateway／test_timeout_tier_thresholds | **未投**（同件等 0003） | 本班 0003 袋含 gateway 的甲-0 六行，同会话同件两袋必互踩 |

   **C10 那条不是环境噪声，是 C10 双保险的真实过度拦截**：阻断原文点名
   "reconciler OK 已声明 delete 但目标在保护区（C10 双保险硬拦）"，被拦目标＝
   `<树根>/.runtime/tmp/pytest_<pid>/test_declared_delete_passes_wi0/.runtime/tmp/victim.txt`
   ＝测试自家 tmp_path 夹具件。⇒ 三班自报"45 passed"与本班实测（42 collected／41 passed／1 failed）不符，
   差在**夹具落点是否撞进扩列后的 PROTECTED_PREFIXES**。本班不改他班裁定内容（在册纪律），处置＝不投＋
   把复现尺留给属主面：`cd .worktrees/st-maint5-20261013 && PYTHONNOUSERSITE=1 python -m pytest 
   tests/gov/governance/audit/test_file_ops_enforcement.py -q --tb=short`。
   本班随后把车道这三件复原成 dev 现字节（真源仍＝dead 袋的 blob_ref；`git status` 该三路径复测＝干净）。
   要么改 C10 的保护区判定使夹具面不被吞（判据面，须裁定），要么该测试件改夹具根——两条都不由本班自决。

   超时乙丙袋的投法（下一班照此做，禁整档覆盖）：以**落地后的 dev gateway 现字节**为基，
   把 0041 blob `c4526845cf1e` 里的超时乙改动（`_resolve_git_timeout` 走 thresholds 单口）叠上去，
   与 thresholds＋test_timeout_tier_thresholds（正确版 blob `5e361f6dbdf9`）同袋投；
   ⚠ 禁取 `.runtime/tmp/maint3_night/rescue_20261013/` 那份测试件＝`4ac2ddd426cc`（parents[3] 错版）。

3. 保命抄：本班账双抄（车道 ＋ `.runtime/quarantine/maint5_ledger_copies/00_ledger.md`；
   尺＝两条命令，别在正文里写死自己的 sha——写了就立刻过期）：
   `sha256sum .worktrees/st-maint5-20261013/docs/_working/maint5_campaign/00_ledger.md .runtime/quarantine/maint5_ledger_copies/00_ledger.md`
   期望＝两值同；`wc -l` 期望 ≥ 本文件行数。
   四班七提案＋普查逐件表＋四班班账抄入 `.runtime/quarantine/maint5_tmp_promote_20261013/`（25 件 1.4MB，
   P7 抽点 sha 全等）——原址 `.runtime/tmp/maint4_night/` 受 24h TTL（约 10-14 03:0x 起清），别再只靠它。
   护令① 的抢救区补一面镜像：卡片称 `.runtime/tmp/maint3_night/rescue_20261013/`＝C10-C13"唯一持久副本"，
   而实测该路径**在 tmp 面上、受 24h TTL**（措辞与面的属性不符；本班不改护令，只补零成本保险＝
   原样镜像到免清面 `.runtime/quarantine/maint5_rescue_mirror_20261013/`，11/11 件 sha 全等，原区一字未动）。
4. 待下一班做（本班不该自决或窗口未到）：
   ① P7 本体投袋（施工卡见 §三.5；须等甲-0 落地后在**新 dev 字节**上重放，勿拿车道旧面当基）；
   ② 本班班账投袋（§九.3 前置达成后）＋四班班账 `.worktrees/st-maint4-20261013/docs/_working/maint4_campaign/00_ledger.md`
      代投（四班 §六.7 明文交统筹；同样须先登 token）；
   ③ ①丙 shadow 满样本后翻 enforce（§五.1，判据与回滚手柄都写在 flags 的 description 里）；
   ④ CAPCAN 主区唯一副本（6bd8bb33a602）归册主班 st-datalane2-20261012 自处，谁清谁毁字节；
   ⑤ 死信归档与 `blob_gc` phase2＝未裁，本班只完成抢救面（§四）。
5. claim 与收尾：本班 held_files 见 `lock_files.py list`；收班走 `git_commit.py --release-only`；
   车道 `.worktrees/st-maint5-20261013` 在 0001/0002/0003 全落地前**不 archive**
   （在册第六态：未跟踪新件被整树抹掉时 git 侧零痕迹，本班账此刻就是未跟踪件）。

## 十一、05:0x 终袋账与一条本班自犯的口径错（留旧案不改 §十 原文）
§十.1 写于 04:57，其后本班又跑了三件事（首袋落地、班账袋重投、一枚同件袋让路）。终态袋账：
| 袋 | 内容 | 态 | 基底 ||---|---|---|---|| 0001 | P3 修 1a（ddl 两腿＋d3 测试件两支钉） | **done**，landed `41c3a400db4f`（05:00） | a1e8866ecd（＝快照真源面，合规） || 0002 | 三班账 §13.7 首投 | dead＝主动让路（基站在车道旧面而该件已漂） | a1e8866ecd || 0003 | 甲-0（gateway 一键＋两支钉） | pending | a1e8866ecd（投前逐件验 laneHEAD 面==dev 面＝True） || 0004 | 班账袋第一次重投 | **dead＝主动让路**（基值传错，见下条自纠） | 字面量 `dev`（错） || 0005 | C11＋C12 代投（3 件） | pending；代投面自家测试实测 `25 passed` | a1e8866ecd（5 件逐件验无漂移） || 0006 | C13 代投（2 件） | pending | 同上 || 0008 | 班账袋终投（§13.7） | pending | **显式 dev sha** `41c3a400db4f` || C10 | ops_guard／reconciliation_registry／其测试件 | **未投**＝代投字节面实测 1 failed（真回归，非噪声，详 §十.2） | — || 超时乙丙 | thresholds／gateway／test_timeout_tier_thresholds | **未投**＝与 0003 同件，待 0003 落地后叠加投法见 §十.2 末段 | — |
**本班自犯一条口径错（另起留案，不改写 §十）**：令文写的是
`重投 --base-head $(git rev-parse dev) 现值`——要的是**现值 sha**；本班第一次投时把旗值传成了字面量 
`dev`。后果不是报错而是**静默失效**：落地侧 `git cat-file -t dev` 返回 commit（通过
`非可判 commit` 那道类型闸），随后 `anchor = merge-base(dev, dev) = dev` ⇒ `diff(base, dev)` 恒空 ⇒
快进判定结构性失明＝在册 F-AUDITFIX-STALE-01（`commit_queue_landing.py:1980-1986`）点名的同一形态，
当年那件把在册修复整文件覆掉。本班是自己复测该件`dev 现面==快照基底` 才确认没造成实际回退风险，
但这不构成把错旗值留在队里的理由 ⇒ 已按在册两步法让路 0004（袋内字节与 0008 逐件断言全等后才撤，
dead_reason 写死理由与可逆配方），只留显式 sha 基底的 0008。

**一条给下一班的正门口径（钉死在册，防再错）**：
①`git_commit.py --enqueue` 的基底取**调用方车道 HEAD**（在册 F-AUDITFIX-STALE-01 认定的正确语义）——
  用它就要**投前逐件**验 `laneHEAD:件 == dev:件`（本班 0003/0005/0006 都这么验过），漂了就会判成真冲突；
②`commit_queue.py enqueue --base-head X` 的 X 必须是**可 cat-file 的 sha**，不是分支名——
  传分支名不会报错，只会把冲突判定静默摘掉（更危险）；
③`commit_queue.py enqueue` 无 `--allow-multi-domain`，跨域袋（gate＋自家测试）仍走 `git_commit.py`；
④在车道里入队必须调**主区脚本**＋`--worktree-root <车道>`（在册 worktree-local-queue-trap：影子根静默不排）。

**修 1a 落地后的运行面复核（05:0x）**：主区磁盘 `registry_ledger_ddl.py` 已含尾位装配腿（grep=1）；
生产脚本形态零写入探针（`sys.path[0]=d3_metadata`、`PYTHONPATH` 不含仓根、主区码面）读回 
`schemas.__file__=None`（＝先落的命名空间份）**且 `api` 仍导入成功** ⇒ 第二腿（`__path__` 修补）在真环境生效；
新鲜次序（先触写腿）由 §七② 的两支用例长期把关。端到端正证（真登记三腿）见 §九，那是改码前不存在的能力。

## 十二、统筹 11:0x 两裁三新的执行账（含两条本班自犯留案）

| 裁 | 当班实况 | 读数 |
|---|---|---|
| ①提甲-0 到队首 | **无需执行**：11:02 复测 dev 面，甲-0 已落地（注入键命中 1 处、自家钉 1 处），主区磁盘同步含该键＝运行面生效 | 尺见 §七②（内容级，不看 done 目录）；本班五袋全 done（0001 修 1a／0003 甲-0／0005 C11+C12／0006 C13／0008 §13.7） |
| ②landing.py 不清 | **照令未动** | 主区该件盘面值＝0041 袋字节 `cab67c61`，与 dev `29d50c0d` 仍分叉；甲-0 落地后门读落地树，脏面已退出判定 |
| ③册主 render 袋即刻出 | **执行，但量的前提缺一步，已按正门补齐**（见下） | q-…-0010（首投 0009 死因见下第三条） |
| ④队列首两枚幽灵 processing | **到点已自愈**：maint5-0005 已 done、mineloop2-0021 已 dead；两件的 `meta.attempts` 皆 None（＝D4 族"工早退只是症状层"那一支的账没记上，可作解锁班的只读观察面） | `counts pending=0 processing=1 done=769 dead=1595`（14:32） |
| ⑤ch_write_guard 受控红证 | **定性完成＝留痕腿是通的**（见下） | 正对照落 1 行、反对照 0 行 |

### 十二.1 ③ 的缺步：retire 不进快照，render 会先把夹具垃圾首次物化

裁定③的前提（"已 retire 6 条夹具行 ⇒ 净增 7 行干净面"）在**账本面**成立、在**生成器读的那一面**不成立：`registry_projection/pg_source.load_latest_snapshot()` 读 `registry_snapshot ... ORDER BY snapshot_version DESC LIMIT 1`＝已发布快照，retire 只动 `registry_entry.status`。⇒ 直接 `--check` 的差面是 **13 行**，且含那 6 条测试夹具（`src/zephyr/{degraded,layered,lying,new_mod,orphan,with_extras}.py`），正是数据班 §卅六 明令"不再首次物化测试垃圾"要避开的形态。取证件＝`registry_drift_20261013T041436448563.diff`（13 行版）。

处置＝走同一正门补发布，而不是硬出脏袋或改判定面：`baseline.publish_snapshot("REG-MODULE-TRANSLATION-001", repo_root=..., session_id=st-maint5-20261013)` → `noop=False / content_sha256=90521ea5120527018b74c596a3cfce19873f9af9b097962ca2921f361612d645 / active 条目 8,112`；复尺 `--check` 差面＝**净增 7 行／删除 0／夹具混入 0**（取证件 `...T045705702412.diff`）后才 `--render`。7 行内容全取自 PG 账本原样（首条＝数据班件，余 6 条＝各在飞车道自己登记的件），本袋不代拟一条。

热册安全尺（在册"HEAD 为基＋断言删除集==计划内"）：render 后 `dev 独有线=0`、新增 24 行＝7 块、前 100 行逐字未动；随后把主区该件清回 dev 字节（`git status` 复测干净），袋源＝车道面。

### 十二.2 两条本班自犯（当场各自修，不留到下班）

1. **`--project-root` 缺省打到主仓**：`registry_projection_generator.py` 的 `--project-root` 默认取 `REPO_ROOT`（经 editable .pth 恒=主仓），第一次 `--render` 因此写在**主区**盘面而非车道。已在同一动作内把面搬进车道并把主区复原；后续任何 render 必须显式带 `--project-root <车道>`（或先想清楚：这是共享面）。
2. **长空档把在飞袋判成 ghost**：本班 05:10 收口话讲完后长时间无动作，车道 heartbeat daemon 于 07:59 写 `exited / idle timeout 1805s`、注册表条目随后被除名 ⇒ 14:2x 复投的 0009 被判 `ghost_session` 死，且同签名死信累计 444 次触发复发熔断拒 requeue（在册口径＝熔断只拦 requeue 不拦新袋）。复命＝`SessionRegistry.register(pid=0)` ＋重启 heartbeat daemon ＋`list_active` 复核为活 → 以**新袋** 0010 复投。留一条给下一班：**长窗口的正确姿势是先复投再歇，不是歇完再复投**；判活尺别只看 daemon 在不在，要 `list_active` 有点名。

### 十二.3 ⑤ 的定案："真没写" 与 "留痕腿没通" 已分开

判定口＝`_assert_write_allowed(op,target,sql)`（唯一口，四写入口接线实测在 `ch_writer.py:518/573/640/1235`＝http_insert／query／create_database／alter_delete）。

- 正对照（伪装测试进程：`PYTEST_CURRENT_TEST` 置位、`ZEPHYR_SESSION_ID=st-maint5-20261013-controlled-red-proof`）→ 留痕面新增 1 行 `{state:shadow, action:"would_block", op:INSERT, target:c9_meta.maint5_guard_red_proof}` ⇒ **腿通**；
- 反对照（同一句调用、不带任何测试 env）→ 0 行 ⇒ 谓词有判别力（不是"逢调用必写"的假证）；
- 因此 03:59→14:29 的 7 小时零留痕＝**这段窗口确实没有测试进程触过 CH 写口**，不是腿没通。旁证：这段窗口的落地链只跑 `pytest --collect-only`（gate-test 钩子不执行用例）＋errcode 单档（无写面）。
- ⚠ 一条附带缺陷（本班不修，呈册主）：①丙 自家 `tests/data/data/db/test_ch_write_guard.py` 9 passed 却**一行留痕都没产生**＝该测试件测的是判定口替身，没测留痕落盘面（在册"红队用例不落盘=判据没跑"同族）。⇒ enforce 计数尺（把本班合成行剔掉）：
  `python -c "import json,pathlib;rows=[json.loads(l) for l in pathlib.Path('.runtime/gate_audit/ch_write_guard.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()];real=[r for r in rows if 'maint5_guard' not in str(r.get('target')) and 'controlled-red-proof' not in str(r.get('session_id'))];print(len(rows),len(real))"`
  当前读数＝`1 0`（总 1 行全是本班探针，真样本 0）⇒ **翻 enforce 的条件仍未成就**，与 §五.1 同判。

### 十二.4 P7 本体本班不落（明确理由，非拖延）

甲-0 落地后再读 P7 本体：令内"own 命中改路径集精确相等"改的是**每一枚袋的 own/foreign 归因面**，而甲-0 已把今夜连坐的主因（门读错面）摘除——0005 含受保护件 `commit_queue_landing.py` 且主区该件仍脏，仍在甲-0 之后净落＝**连坐成本已消**。施工卡与代码面齐备（`.runtime/quarantine/maint5_p7_workface_20261013/`，含 5 支钉的 `test_both_faces.py` 与突变读数），但它牵 `_precommit_debt_keys` 的债务棘轮键面（本班已改为两口径有意分叉并写理由），该族的基线键需要一次全仓重放自证才敢上关键路径 ⇒ 交有预算的一班，勿在班尾抢跑。

# 十三、统筹追加三件落地（15:4x–17:0x）：甲案断源三袋＋sim_daily_report 清账＋留痕面现状

## 十三.1 追加③＝甲案六支 node-id 排除（三袋全落 dev，落地面复验）

- 袋与 commit：袋甲（两份 pytest 配置面）`q-…-0011`→`1a6c2064c9`；袋乙（看守项 E）`q-…-0012`→`9e992e5dad`；袋丙（两枚锚点测试）`q-…-0013`→`f85d070651`。
- 落点＝配置面而非某条脚本，理由两条（实质判断，非菜单字母）：①同一测试域有**两个入口**——默认跑法 `pyproject [tool.pytest.ini_options]` 与精简跑法 `-c py.ini`（裁定#278 定址），只在单侧排除＝"另一条跑法照写生产表"的假止血，而案卷 §二.1 实测 10-13 00:04:07/00:04:40 两笔正是队列自动轮踩的；②另立 config 册＋conftest 读取器要多造一道消费者，在册判据"判已防护必测谁调它＋能否改变行为"下，`--deselect` 由 pytest 本体消费、行为当场可量。
- 生效实测（**落地面**＝主区，非车道）：默认跑法 `collected 20 items / 6 deselected / 14 selected`；精简跑法 `14/20 tests collected (6 deselected)`；锚点套件 `12 passed`。
- 三面 grep 判据前后：考试班复现过的 `git grep test_plan_bridge_unclassified_is_pending dev -- scripts config pyproject.toml` 原＝空，现＝`dev:pyproject.toml`；`git grep -c "deselect=tests/backtest/test_sim_daily_runner.py" dev -- pyproject.toml py.ini`＝各 6。
- 判别力三条腿突变自证（各命中对应测试，非旁证；三件按 sha 逐字节复原，件存 `.runtime/quarantine/maint5_deselect_mutation_20261013/`）：py.ini 少一条⇒`test_repo_py_ini_actually_aligned` 红；两侧同改成不存在的函数名（陈旧排除形态）⇒`test_repo_deselect_roster_is_live_and_effective` 红；摘掉 E 判据⇒`test_deselect_single_side_drift_detected` 红。
- **一条把令文前提改掉的本班读数**：令文按名单整六支排除，本班逐支读码量到当前 dev 面**只有 1 支未隔离**——`tests/backtest/test_sim_daily_runner.py:111 test_plan_bridge_attack_state_is_unexecutable` 没 patch `write_report_row`，其余五支已 monkeypatch（`:92`/`:106`/`:122` patch write_report_row，`:160`/`:184` patch _write_observe）；`scripts/backtest/sim_daily_runner.py` 侧 `replay_one`（:411→:494）只经 `_write_observe`，报表写只在 `plan_bridge`（:324）与 `e4_replay`（:559）/`settle`（:836）。⇒ 排除的真实代价＝五支已隔离用例失去覆盖；一行真治本＝给那支补 monkeypatch，但该件属 sim 班资产，本班不改（他会话件不代修）。路由建议＝断源已在位 → 补那支 monkeypatch → 解除本排除，防过渡件变永久缩面（退役条件已写进两配置面注释与 E 项说明）。

## 十三.2 入队面三条事实（供统筹／维护线，本班未自改任何门）

1. `commit_queue.py enqueue` **没有** `--allow-multi-domain` 逃生旗，而入队预检 COMMIT-SCOPE 把"治理脚本"与"它的锚点测试"判 2 个域 ⇒ 根宪法 §2 第 4 条所定"gate+自家测试同批是合法的"在队列正门 structurally 走不通，只能拆袋＋`--depends-on`（多花 2 个 landing 周期，本班今夜 ③ 即因此从 1 袋变 3 袋）。
2. 主区 cwd 跑 enqueue 会被 WORKTREE-REQUIRED 挡（该 gate 判 worktree 性用 cwd，`--worktree-root` 不改它）；正解＝**车道 cwd ＋ 显式 `--queue-root` 指主队列根 ＋ 主区脚本**（否则撞 worktree-local-queue-trap 影子根）。已在册配方，本班复证。
3. RUFF-PRECLEAN 是**整文件**口径不是 diff 口径：`git show dev:scripts/governance/d7_code/compare_pytest_configs.py` 本就 `Would reformat` ⇒ 凡改此件者都得整件格式化，diff 会被放大。本班按处方 `ruff format` 整件并在袋讯里披露了 format-only 行。

## 十三.3 追加①＝c1_backtest.sim_daily_report 清账（删 1 行＋重放结算腿＋复验）

- 令文谓词与现面不符，本班未照字面删两行：令文写"两行测试污染（SIMP-…10-09… ＋ SIMP-…10-12… simwire-004441）"，在册 §38.2（考试班 13:1x）已改写为"物理面只剩 1 行"，本班 16:4x 复量 10 行候选全件见 `.runtime/quarantine/maint5_simdaily_predelete_164x/target_row.json`（19 列，sha256 前缀 `e114aa5dd50d`）。
- 三条机械判据定案"只删 09-21 那 1 行"：①该行 `asof_ts=2026-10-12T19:25:22Z` 与案卷 §二.1 的测试轮 INSERT 逐秒对上，`run_id` 已被结算腿改写为 `settle-20261013004545`（＝污染已被加工进结算面）；②`sim_daily_runner.py` 与该表 DDL 首见于 commit `fb5a7821d7f`（09-22 15:17），晚于 09-21 ⇒ 09-21 的 plan_bridge 键不可能由当日生产腿写出；③本班 16:4x 量全表 `source='plan_bridge'` 按日行数＝09-19/09-21/09-22/09-23/09-24/09-28/09-30/10-09/10-12 各 1 行，除 09-21 外各行 ingest_ts 都落在自己的生产批次时刻，唯 09-21 行 ingest=10-13 00:45:45（结算批次）。
- **10-12 两行不删**及其证据：`SIMP-2026-10-12-plan_bridge-index000300.SH`（run_id `simwire-20261013004441`，asof 00:44:41Z）与 `SIMP-2026-10-12-platform-platform`（`simwire-20261013004542`）紧随 00:45:45 的 settle 批次，形状＝生产日链 plan_bridge→platform→settle；`simwire-` 前缀由**写入时刻**生成、生产与测试两条路共用（案卷 §三 自述），故前缀不具判别力；而考试班 §37.3.2 已实测该窗 15 笔"全是生产腿…不是测试夹具面"。删它＝删一条真实晨间读数，物理不可逆且不在任何授权语义内。
- 执行与读回：`ch_writer.delete_where`（在册单口）谓词＝`report_date='2026-09-21' AND source='plan_bridge' AND subject='index:000300.SH'` ⇒ mutation_2816 `is_done=1`、`parts_to_do=0`、无失败原因；读回＝该键 FINAL 命中 0（未合并面也 0）、全表 276→275（恰 −1）、`report_date='2026-09-21' AND eval_score=1` 48→47（假读数在聚合面的贡献已消）；重放 `python scripts/backtest/sim_daily_runner.py settle --day 2026-10-13` ⇒ `{"settled": 7, "unresolvable": 0}`，10-12 七行现带 `run_id=settle-20261013084515/6`、`evaluated_by=sim_settler`（plan_bridge posture_check=1.0／platform heartbeat_check=1.0／e4_replay 4×1.0＋1×0.0），待结算面归零。
- ⚠ 本班自犯一条入账：续跑前第一版把 `system.mutations` 的列名写成 `is_finished`（本机真列名 `is_done`），查询 404 使脚本在**"删除已提交、读回未做"**的中间态中断约 2 分钟；未盲目重删，改为先 `SELECT name FROM system.columns WHERE table='mutations'` 列真列名再写轮询。处方＝任何破坏性动件的轮询/读回语句先列 system.columns 真列名，禁凭记忆写系统表列。

## 十三.4 追加②＝ch_write_guard 留痕面现状（翻 enforce 条件仍未成就）

- `.runtime/gate_audit/ch_write_guard.jsonl` 已存在（434B，2 行），两行全是本班受控探针：`06:29:09Z op=INSERT target=c9_meta.maint5_guard_red_proof`、`07:15:02Z op=http_insert target=c9_meta.maint5_synthetic_wire_probe`，皆 `state=shadow action=would_block` ⇒ 令文"应见留痕行"达成＝**留痕腿是通的**，04:00 那次"文件不存在"的正确定性是"该留痕的事件从未发生"。
- 一条读数口径提醒：本班 ① 的 `alter_delete` **不留痕**（护栏只咬测试进程，属设计使然）⇒ 今后"零留痕"不得读成"零写库"，翻 enforce 的真样本计数尺须排除本班这类维护进程写。
- 本班合成探针未在 `data/local_fallback/` 留残留（16:5x `find data/local_fallback -newermt "2026-10-13 12:00"` 空），无需清理。

## 十三.5 复核命令（本班已按原文逐条跑过，期望值＝实测所得）

```
# ① 三面 grep 判据（期望：dev:pyproject.toml；两配置面各 6 行）
cd /d/ZephyrAlpha && git grep -l "test_plan_bridge_unclassified_is_pending" dev -- scripts config pyproject.toml
cd /d/ZephyrAlpha && git grep -c "deselect=tests/backtest/test_sim_daily_runner.py" dev -- pyproject.toml py.ini
# ② 两跑法排除生效＋锚点套件（期望：14/20 (6 deselected) 两次；12 passed）
cd /d/ZephyrAlpha && python -m pytest tests/backtest/test_sim_daily_runner.py --collect-only -q 2>&1 | grep collected
cd /d/ZephyrAlpha && python -m pytest -c py.ini tests/backtest/test_sim_daily_runner.py --collect-only 2>&1 | grep collected
cd /d/ZephyrAlpha && python -m pytest tests/gov/governance/d7_code/test_compare_pytest_configs.py -q --no-header 2>&1 | tail -1
# ③ 清账终态（期望：total=275 / target_rows=0 / 09-21 eval_score=1 计数 47 / 待结算 0）
cd /d/ZephyrAlpha && python -c "import sys;sys.path.insert(0,r'D:/ZephyrAlpha/src');from zephyr.data import ch_writer as cw;T='c1_backtest.sim_daily_report';f=lambda s:[list(r) for r in cw.query_strict(s)];print('total',f('SELECT count() FROM '+T+' FINAL'));print('target',f(\"SELECT count() FROM \"+T+\" FINAL WHERE report_date='2026-09-21' AND source='plan_bridge'\"));print('score1_0921',f(\"SELECT count() FROM \"+T+\" FINAL WHERE eval_score=1 AND report_date='2026-09-21'\"));print('unsettled',f(\"SELECT count() FROM \"+T+\" FINAL WHERE report_date<'2026-10-13' AND evaluated_by=''\"))"
# ④ 留痕面（期望：rows=2 real=0）
cd /d/ZephyrAlpha && python -c "import json,pathlib;rows=[json.loads(l) for l in pathlib.Path('.runtime/gate_audit/ch_write_guard.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()];real=[r for r in rows if 'maint5' not in str(r.get('target'))];print(len(rows),len(real))"
```

# 十四、统筹批三件（17:1x–17:5x）：命中面测量修正／render 袋仍未出（附不丢字节的存证）／前端补扫零读者

## 十四.1 批①＝接管台账命中面剔除 dev-同字节跟踪件（袋 `q-…-0015` 已落 dev）

- 病根读码定性（非本班推测）：`_worktree_dirty`（session_takeover_ledger.py:165）用 `git status --porcelain` 取面，status 报的是**对自家 HEAD 之差**；车道指针落后 dev 时盘字节早已等于落地面的件照样报 `M`，经 `entry_match_surface`（:1123 只取 dirty_files）进 L3 硬阻断面＝隔空挡死无辜袋。双臂班实证件那四行读数原文照录：`M scripts/backtest/fexam/card_binding.py`／`rev-parse dev:件`=7df3696c／`hash-object 磁盘`=7df3696c／`他们HEAD:件`=3eca6f3d。
- 修法＝收清单后与落地面 `_LANDING_REF`(=dev) 批量比一次 `git diff --name-only dev --`（吃仓内 filters，与 `commit_queue_landing._worktree_matches` 同族口径），相等者移出 dirty_files 并记 `excluded_dev_identical=n`＋`excluded_dev_identical_files` 留痕。三条承重墙＝①**禁自算 blob sha**（磁盘 CRLF≠blob 归一面，本班 17:2x 就据此把 gpuwo 车道册面误判成"三面在争"，反面教训写进注释）；②未跟踪件（`??`）永不移出、比对不可用＝整批保留＋`dirty_note=dev_identical_check_unavailable`（宁多挡不误放）；③非 ASCII 路径两侧引号口径配不上＝照旧保留（要让它可剔属扩面＝判据变更，须另裁，本袋不做）。
- 同批第三件＝`docs/_working/branch_zero_takeover_20261002/t1_takeover_infra.md` 补 5 行剔除口径（该件 [MODIFY-GUARD] 明文要求收集面变更须与 gate 及设计文档同批；gate 侧零改动）。
- 判别力三条腿突变自证（每条断言"确有 1 failed"，不拿 rc≠0 当能红；基线与复原后皆 2 passed，两件 sha 逐字节复原，备份存 `.runtime/quarantine/maint5_dirtymeasure_mutation_20261013/`）：摘剔除⇒excludes 测试红；把"不可用"改成整批移出⇒keeps_all 测试红；把未跟踪件也进剔除面⇒excludes 测试红。新两支用 tmp_path 内**真 git 仓＋落后 dev 的 linked worktree**复刻假阳性形状。
- 落地面真车道路测（只读）＝`st-minedig2-20261012` dirty 30→6、`excluded_dev_identical=24`，`card_binding.py` **已不在命中面**；`st-gpuwo-20261011` dirty 52→40、`excluded=12`，`module_translation_registry.yaml` **仍在命中面**（真差异，本修不该替它洗掉）。

## 十四.2 两条本班程序错与一条系统态副作用（如实入账，未掩饰）

- ⚠ **跑完才量副作用**：在册铁律是"改系统态前先只读量副作用"，本班 17:3x 跑 `--scan` 前只做了文件快照没做影响面预算。实测后果＝open 条目 176→184，**新增 8 枚**，其中 4 枚带非零命中面（`st-cband-20261012`=10／`st-gpux4-20261013`=19／`st-mineloop-20261010`=43／`st-fclean4-20261012`=2）＝这些件现在会挡对应班的袋。可回退＝`cp .runtime/quarantine/maint5_takeover_prescan_20261013/takeover_ledger_before.jsonl .runtime/takeover_ledger.jsonl`（跑前 sha256 `ff095f5de92e`）。本班判断＝这 8 枚是判死钩子本该生成的显化（今日已有 worker-* 条目由钩子自发写入），**不回退**——回退等于把真实未落地成果藏回黑箱，比多挡更坏；但这条决定属治理面，请统筹复核后追认或另处方。
- ⚠ **批①对存量面不自愈**：`--scan` 当日死亡集里查不到 gpuwo/minedig2（早已除名），两条既存条目 ts 停在 10-12、`excluded_dev_identical=None`＝面纹丝不动。本班随后只用台账自己的幂等单口 `write_takeover_entry(root, sid)` 刷这两条（不新增、不 resolve、不改判据），实测 52→40 与 26→6。处方补一句给维护线：**凡改命中面口径，须同时给"存量条目如何刷新"的出口**，否则修只在将来生效。

## 十四.3 批②＝render 袋仍未出，本班不代签处置（附不丢字节的存证与三条路）

- 本班 C4（`q-…-0010`）的挡点是**真差异**不是假阳性：`git -C .worktrees/st-gpuwo-20261011 diff --quiet dev -- <册>` rc=1。批①不替它洗掉（本班 17:2x 一度用错口径以为可解，已在十四.1 记为反面教训）。
- 那 35 行差异是什么：相对 dev 增 35 行、删 0 行；其中 28 行在本班袋面里查无，且内容全属测试夹具形状——`- module_path: src/zephyr/degraded.py`（name_zh=降级模块／plain_zh="降级模块的大白话简介内容"）、`src/zephyr/layered.py`（改名后）、`src/zephyr/lying.py`（谎报模块）、`domain_id: D_TEST` ×5。即＝某轮测试把夹具条目直接写进了他们车道的热册，不是作者成果。
- 为什么本班不 resolve：`--resolve` 是**整条目**终态（该条目现面 40 件，本班只逐件核过其中 1 件），跨 39 件未核件替死会话下结论＝在册禁止的"代修他会话在途面"；且绕过 L3 显化会把可见性洗掉（Owner 在册认可过"不越闸"）。
- 不丢字节的存证＝`gpuwo_registry_face.yaml`（3588317B，sha256 `1af8f9e64ef6`）＋跑前台账 `takeover_ledger_before.jsonl`（`ff095f5de92e`）。三条路供裁：甲＝统筹/Owner 签 `--resolve st-gpuwo-20261011 --by <署名> --note "该件 delta=D_TEST 夹具残留，原面已存证 sha=1af8f9e64ef6"`，随后本班重投 render 袋；乙＝先由有预算的班把那 40 件逐件核成"成果/残留"二分再 resolve；丙＝维持现状（render 继续躺 dead/，解锁班与挖矿二班同类件按十四.2 的刷新处方走批①通道，不受此挡）。本班建议＝甲（面积只涉一枚册件、字节已存证、可逆），但署名不归本班。

## 十四.4 批③＝sim_daily_report 前端/散落读取面补扫：零读者（三面共证）

- 可执行读者面（`*.py/*.sql/*.ps1/*.js/*.ts/*.ipynb` 排除 src/scripts/tests）＝**只有** `schemas/categories/sim_daily_report.py`（DDL 声明件，非读者）。
- 登记面两面自证：`data/strategy_intake/matrix_inventory.yaml` DS-338 该表 `wiring` 四腿全 false、`wiring_level_max: L0_orphan`；`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml` 该表两处 `consumed_by_jobs: []`。
- 前端面：`src/zephyr/frontend/dashboard/api_server.py` 查无按表名通用读面；web/features 里 `daily_report` 命中是无关模块名（`daily_report_orchestrator` 词条），不指该表。`paper_outpost` 是**写者**（source=paper_outpost 汇总行）不是读者。
- 清账后的聚合终读数（report_date='2026-09-21'，FINAL 按来源）＝e4_replay 46 行（45 行 eval_score=1）＋plan_execute 1＋platform 1＝48 行、`plan_bridge` **0 行**；eval_score=1 合计 47（清账前 48）；全表 `source='plan_bridge'` 键数 9→8。

## 十四.5 复核命令（本班已按原文逐条跑过，期望值＝实测所得）

```
# ① 批① 落地面读数（期望：minedig2 dirty=6 excluded=24 card_binding 不在面；gpuwo dirty=40 excluded=12 册件仍在面）
cd /d/ZephyrAlpha && python -c "import sys;sys.path.insert(0,r'D:/ZephyrAlpha');sys.path.insert(0,r'D:/ZephyrAlpha/src');from pathlib import Path;from scripts.governance import session_takeover_ledger as L;R='docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml';[print(rel,(lambda i:(i['dirty_count'],i.get('excluded_dev_identical'),'scripts/backtest/fexam/card_binding.py' in i['dirty_files'],R in i['dirty_files']))(L._worktree_dirty(Path(r'D:/ZephyrAlpha'),rel))) for rel in ('.worktrees/st-minedig2-20261012','.worktrees/st-gpuwo-20261011')]"
#    期望：(6, 24, False, True) / (40, 12, False, True)
# ② 套件与格式（期望：27 passed；already formatted；All checks passed）
cd /d/ZephyrAlpha && python -m pytest tests/gov/governance/test_session_takeover_ledger.py -q --no-header 2>&1 | tail -1
cd /d/ZephyrAlpha && ruff format --check scripts/governance/session_takeover_ledger.py tests/gov/governance/test_session_takeover_ledger.py 2>&1 | tail -1
# ③ 台账副作用可核（期望：before=176 after=184，新增八枚名单见 §十四.2）
cd /d/ZephyrAlpha && python -c "import json;from pathlib import Path;b={json.loads(l)['sid'] for l in Path('.runtime/quarantine/maint5_takeover_prescan_20261013/takeover_ledger_before.jsonl').read_text(encoding='utf-8').splitlines() if l.strip() and json.loads(l).get('status','open')=='open'};a=[json.loads(l) for l in Path('.runtime/takeover_ledger.jsonl').read_text(encoding='utf-8').splitlines() if l.strip() and json.loads(l).get('status','open')=='open'];print(len(b),len(a),sorted({x['sid'] for x in a}-b))"
# ④ 批③ 聚合终读数（期望：plan_bridge 键数 8；09-21 三来源 46/1/1）
cd /d/ZephyrAlpha && python -c "import sys;sys.path.insert(0,r'D:/ZephyrAlpha/src');from zephyr.data import ch_writer as cw;T='c1_backtest.sim_daily_report';f=lambda s:[list(r) for r in cw.query_strict(s)];print('plan_bridge 键数',f('SELECT count() FROM '+T+\" FINAL WHERE source='plan_bridge'\"));print('09-21 按来源',f(\"SELECT source, count(), sum(eval_score=1) FROM \"+T+\" FINAL WHERE report_date='2026-09-21' GROUP BY source ORDER BY source\"))"
```

# 十五、收口回执对账（20:1x）：三件候裁全有结论＋两条更正归本班＋车道不自撤

## 十五.1 统筹收口三件逐条对账

- 8 枚新增接管条目＝**追认不回退**（§十四.2 请示项结案）。其中 `st-gpux4-20261013` 那枚由 GPU 五班独立逐件核验"五件跟踪件车道独有行全为零＝无成果可救"后由统筹 resolve ⇒ 与本班 §十四.2 的判断同向（不回退＝不把真实未落地成果藏回黑箱；处置须由逐件核验者签，不是扫描者签）。
- render 袋＝**甲路已由统筹执行**：`resolve st-gpuwo-20261011`，原面存证 sha `1af8f9e64ef6`＋锚点 `.runtime/quarantine/commander_takeover_resolve_20261013/`。本班 0010 袋本体被存活闸按"属主会话已死"拦下，统筹两笔 requeue 尝试 0017/0018 亦同因判死留痕；重渲染**移交维护六班**（本班 C4 就此关闭，署名与执行皆不在本班）。
- 前端补扫零读者＋清账读数＝采信入册（§十四.4 三面共证与 09-21 按来源 46/1/1、plan_bridge 键数 9→8 读数）。

## 十五.2 两条更正归本班（写清因果，防下一班踩同一坑）

- ⚠ 本班 17:0x 报"保活授权到 20:08"是**算错的**：grant 落账 09:08:28Z（UTC）＋ttl 7200 ⇒ 到期 **11:08:28Z＝本地 19:08**，不是 20:08。守护在到期 20 秒后（11:08:48Z）按合同自退（末行 `exited reason=idle timeout idle=5072.8s`），注册表条目随除名。
- ⇒ 统筹 19:25:25Z／19:27:46Z 两笔 requeue 死於 `ghost_session` 的**根因是本班保活断供**，不是存活闸误拦（闸的判定与留痕都正确，在册"CLI 手动 requeue 不受闸限，人工可强制"也属实——但强制不该由统筹代做）。教训改写成一行的处方：**长班把保活当跨空闲期的持续义务**（ttl 上限 7200，到期即死，没有"最后一次续命管到底"这回事）；班尾若把"他班 requeue 本班袋"列为外部事件，须显式写明"本班已停保活，重投请在 X 时前通知我续命"。本班此刻已复命（register＋grant ttl 7200 至 14:08:34Z＋守护 pid 38856，`list_active` 在册）仅为投完本收口袋。
- 一条只呈不改的观测面建议（不属本收口工，留给维护线）：存活闸死因文本可带"属主最后一次 grant 到期时刻"，让重投者一眼看出"叫属主续命"比"强制 requeue"更省一枚袋。

## 十五.3 车道与存证：本班不自撤

- `.worktrees/st-maint5-20261013` **不自行归档**（收口令明文）——死信班将按行集差重测后走"墓园留证＋归档"通道。本班车道现面＝§十五 追加后对 dev 严格尾追加，无未落地代码件（三枚代码袋 0011/0012/0013＋一枚修正袋 0015 全落 dev，班账 0014/0016/0017→见下）。
- claim 状态：注册表 `held_files=[]`，目标件零占锁（收班前复量）。
- 本班全部持久存证区（字节都在他道可复核）：`maint5_salvage_20261013/`（2699 件＋MANIFEST.csv）、`maint5_tmp_promote_20261013/`（25 件维护四班案卷）、`maint5_rescue_mirror_20261013/`（11 件 sha 等）、`maint5_p7_workface_20261013/`（P7 本体施工卡 26 件）、`maint5_hotreg_snapshot_1104/`、`maint5_simdaily_snapshot_143x/rows.json`（10 行）、`maint5_simdaily_predelete_164x/target_row.json`（sha `e114aa5dd50d`）、`maint5_deselect_mutation_20261013/`、`maint5_dirtymeasure_mutation_20261013/`、`maint5_takeover_prescan_20261013/`（跑前台账 `ff095f5de92e`＋gpuwo 册面 `1af8f9e64ef6`）、`maint5_ledger_copies/`（班账逐节副本）。
- 未闭事项移交清单（本班不签"无遗留"）：①P7 本体（甲-1 剥非计数行＋own 命中精确相等）施工卡在 `maint5_p7_workface_20261013/`，须按 §十二.4 的理由交有预算的一班；②超时乙丙代投（`test_timeout_tier_thresholds.py` 正版 blob `5e361f6dbdf9`，勿取抢救版 `4ac2ddd426cc`）；③甲案六支 node-id 排除的**解除**须等 ch_write_guard 翻 enforce，且真治本＝给 `test_sim_daily_runner.py:111` 补 monkeypatch（属 sim 班）；④存量接管条目刷新出口那条处方（§十四.2）无人接，属判据面。

## 十五.4 复核命令（本班已按原文跑过）

```
# ① 本班队列终态（期望：done 十一枚＝0001/0003/0005/0006/0008/0011/0012/0013/0014/0015/0016＋本次收口袋；
#    dead 六枚＝0002/0004/0009/0010/0017/0018；pending/processing 零）
cd /d/ZephyrAlpha && python -c "import glob,os;[print(st,os.path.basename(p)[-10:-5]) for st in ('pending','processing','done','dead') for p in glob.glob(r'D:/ZephyrAlpha/.runtime/commit_queue/%s/*maint5-20261013*'%st)]"
# ② 保活断供时间线（期望：grant 09:08:28Z→expires 11:08:28Z；daemon exited 11:08:48Z idle=5072.8s；0017=11:25:25Z／0018=11:27:46Z）
cd /d/ZephyrAlpha && python -c "import json,pathlib,datetime as d;f=lambda t:d.datetime.fromtimestamp(t,d.timezone.utc).strftime('%H:%M:%SZ');rows=[json.loads(l) for l in pathlib.Path('.runtime/sessions/st-maint5-20261013/keepalive.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()];print([(r['event'],f(r['granted_at']),f(r['expires_at']),r['ttl_seconds']) for r in rows[-3:]])"
# ③ claim 归零（期望：held= [] 且 target 件零占锁）
cd /d/ZephyrAlpha && python -c "import sys;sys.path.insert(0,r'D:/ZephyrAlpha/src');from zephyr.security.access_control.session_concurrency import SessionRegistry;print([ (s.session_id,s.pid,list(s.held_files or [])) for s in SessionRegistry(r'D:/ZephyrAlpha').list_active_readonly() if s.session_id=='st-maint5-20261013'])"
```
