---
ttl: task_bound
owner: st-maint1-20261010
campaign: 维护一班（P0 判据修复+病灶清偿，总统统筹 2026-10-10 晚）
---

# 维护一班台账 st-maint1-20261010

> 本文件是**施工台账**（交付面），非案卷。案卷（只读车道产出）在
> `.runtime/tmp/st-maint1-20261010/`（t1_archaeology.md / t2_evaporation.md /
> t3_takeover.md / t5_smallbatch.md），该目录被 gitignore 且会被清欠，故本台账把
> **结论与复核命令搬进来**，不搬引用。

## 一、T1（P0）CAP 账本腐蚀——已解

### 1.1 病灶机理（实测，非推演）

投影册顶层根键集合 = `publish_snapshot()` 产出的 bundle 形态，两处来源拼合：

| 顶层件 | 来源 | 后果 |
|---|---|---|
| 各根键段（sections） | PG `registry_entry.family_key`（按字母序 `sorted`） | 杂散 family ⇒ 杂散根键 |
| `header_lines` + `trailing_scalars` + `unique_key_fields` | **盘面 YAML**（`_projection_context_from_disk` fail-open 降级空值） | 盘面被剥光 ⇒ 下次发布把"空"烤进快照 |

即：**账本↔投影恒 zero-drift，腐蚀自我固化，render 永不自愈**。实测
`registry_snapshot` v157→v177 连续十五版 `header_lines=[]`/`trailing_scalars=[]`/
`unique_key_fields={}`；可见征状＝顶层 `di_seam_exemptions` 消失 →
REGISTRY-YAML-PARSE「顶层 di_seam_exemptions 键缺失」→ 当日同签名熔断 6 枚死信。

### 1.2 五枚杂散根键（令卡说 4 枚，实测 5 枚）

`family_key` 被误用作 token 名（4 枚）或字面量 `file_token`（1 枚）：

| family_key | 宿主文件 | 该文件在 creation_tokens 下的正规条目 |
|---|---|---|
| chiefc-99-delivery-20261009 | docs/_working/chiefc_campaign/99_delivery.md | token=chiefc-99-delivery-99-delivery-20261009（active）|
| file_token | docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md | token=gov-adjudication-routing-adjudication-routing-policy-20261008（active）|
| t2-handover-claim-grid0926 | data/strategy_intake/grid_20260926-024947/t2_handover_claim.yaml | token=t2-subspace-t2-handover-claim-20261008（active）|
| t2-subspace-json-grid0926 | …/t2_subspace.json | token=t2-subspace-t2-subspace-20261008（active）|
| t2-subspace-meta-grid0926 | …/t2_subspace_meta.yaml | token=t2-subspace-t2-subspace-meta-20261008（active）|

**判死结论=清理，不归位**：五枚宿主**早已各有一条 active 正规 token**（含
`merge_evaluation`），杂散段是同文件的重复登记，杂散侧独有的仅 `note`/`format`
两个非承重字段 ⇒ 退役即无损。若"归位"反而会造出第二条同文件 token。

执行：`api.retire(authority_ref=本令)` 五行全 `code=OK`（18:16:25，updated_by=
st-maint1-20261010）。墓碑保留，30 天复活窗在册。

### 1.3 代码面两件（判据改动，同批带对抗测试）

**件①（治本·腐蚀自我固化）** `src/zephyr/governance/registry_ledger/baseline.py`
- 新增 `_projection_context_from_snapshot_anchor()`：只在本册**自己的历史快照**里取
  最近一份带非空 header/trailing 的 bundle 作锚（SQL 常量
  `_SQL_SNAPSHOT_CONTEXT_ANCHOR`，按 `jsonb_array_length` 筛候选，`unique_key_fields`
  是对象故不入筛条件）。查无锚＝不补，**零发明**。
- 新增 `_heal_projection_context()` 纯函数：锚只补**空洞**，盘面已有=盘面赢。
- `publish_snapshot()` 接线：三项任一为空才查锚；补洞事实以
  `action=publish_context_heal` 事件行入册，返回体新增 `context_heal` 字段。
- 与既有 `st-tclose-infracure2-20261005 件3`（repo_root=None 裸发布机械拒绝）关系：
  那一件封的是**第一向量**（repo_root 缺失），本件封**第二向量**（repo_root 在而
  盘面已剥光）。两件合起来才叫堵死。

**件③（治本·merge 跳 hooks 通道）** 判据真源单口落在门侧：
- `src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py` 新增公开函数
  `preflight_merge_terminal(run_git, target_ref, other_ref)`：用
  `git merge-tree --write-tree` 在对象库算**合并终态字节**，就地复用本门自己的
  `_structural_issues`/`_WATCH_FILES`（零判据复制）。三态：checked / unavailable /
  conflict（rc=1 交回 git，不抢判）。
- `scripts/session_worktree.py cmd_merge` 接线（此前该路径**零 gate**），红则在任何
  merge 动作之前 `return 1`；新增 `--allow-unchecked-merge` 只对"补检不可执行"态有效，
  结构性红判**永不可越**；阻断与放行均落 `.runtime/gate_audit/merge_preflight.jsonl`。
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` 新增
  `_pre_merge_registry_structure_check()` 并接在 `session_worktree_merge` 的
  gate 分支**之后**——因为 `_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True`
  （#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001，2026-07-20）把 pre-merge 的 commit gate
  **整体**跳过，连带把与 sys.path 无关的结构性判据也跳了；本检零 subprocess gate、
  零 index 写、零 reset HEAD，原治本的病根不适用，故不受该旗与 `force` 支配
  （`force` 只能越"不可执行"态）。

### 1.4 实弹与红证（已跑）

| 项 | 结果 |
|---|---|
| v178 发布（18:20:50，by st-maint1-20261010） | `context_heal={header_lines:7, trailing_scalars:[di_seam_exemptions], unique_key_fields:[capabilities]}`，sections 只剩 `['capabilities','creation_tokens']`，entry_count 15135（v177=15140，差=5 枚退役杂散） |
| render 主区 | `ok=true quadrant=stale wrote=true` **added=0 removed=0**（＝没把他人登记混进本班 commit，归属自证）|
| 门判据复跑 | `_structural_issues(盘面文本,'capability_registry')` = `[]`；`_duplicate_root_keys` = `[]`；键序 `[banner, unique_key, capabilities, creation_tokens, di_seam_exemptions]`，`di_seam_exemptions` 在位且末位 |
| 件③红证（未修码=主区） | 7 项全红；且未修码 stdout 原文打出 `[WORKTREE] 合并 ai/lane/stripped2 → dev` + `[WORKTREE] 合并成功`＝剥光册经同形 merge 长驱直入，逐字复刻 10-10 事故 |
| 件①红证（未修码=主区） | `_projection_context_from_snapshot_anchor`/`_heal_projection_context`/`_SQL_SNAPSHOT_CONTEXT_ANCHOR` 三者 `hasattr=False`；且 `snapshot_from_yaml(剥光文本)` 实测 `header=[] trailing=[]`＝旧码唯一路径就是烤空值 |
| 车道绿证 | `test_registry_ledger_context_anchor.py` + `test_session_worktree_merge_preflight.py` = **22 passed**；回归 `test_registry_yaml_parse_watch_extension.py` + `tests/gov/governance/registry_projection/` = **32 passed** |

### 1.5 复核命令（进程外可验）

```bash
# 1 顶层根键与末位键
python -c "import yaml;d=yaml.safe_load(open(r'docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml',encoding='utf-8'));k=list(d.keys());print(k, k[-1]=='di_seam_exemptions')"
# 2 门判据直调（必须 []）
python -c "import sys;sys.path[:0]=[r'src','.'];from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _structural_issues;print(_structural_issues(open(r'docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml',encoding='utf-8').read(),'capability_registry'))"
# 3 账本侧族谱（active 只应剩 capabilities/creation_tokens）
python -c "import sys;sys.path[:0]=[r'src','.'];from zephyr.governance.registry_ledger import api;c=api._conn_ctx(None);cur=c.conn.cursor();cur.execute('SELECT family_key,status,count(*) FROM registry_ledger.registry_entry WHERE registry_id=%s GROUP BY 1,2 ORDER BY 1',('REG-CAPCAN-001',));print(cur.fetchall());api._release_conn(c)"
# 4 自锚事件留痕（每次补洞一行）
python -c "import sys;sys.path[:0]=[r'src','.'];from zephyr.governance.registry_ledger import api;c=api._conn_ctx(None);cur=c.conn.cursor();cur.execute(\"SELECT event_id,action,after_version,payload_after FROM registry_ledger.registry_event WHERE registry_id=%s AND action='publish_context_heal' ORDER BY event_id\",('REG-CAPCAN-001',));print(cur.fetchall());api._release_conn(c)"
# 5 测试（车道内必带 PYTHONNOUSERSITE=1，否则导到主区包=假绿）
PYTHONNOUSERSITE=1 python -m pytest tests/gov/governance/test_registry_ledger_context_anchor.py tests/gov/governance/rule_bridge/test_session_worktree_merge_preflight.py -q
```

## 二、T1② 三枚被堵袋复投

被堵袋实测（`dead/` 内同签名 `di_seam_exemptions 键缺失` 共 6 枚，dead_reason 逐字节同文）：
nightmine-0013（26 件）/ govjudge-0005 / constland-0005/0006/0007 / finalclean2-0001。

关键机制（读码 `scripts/governance/commit_queue_landing.py:2375-2390`，
`LANDING_MATERIALIZATION_EPOCH="regsolo-b-20261009-pg-render-materialization"`）：
**已入账本册在落地时改由 PG `registry_snapshot` 现读 render 物化，袋内该文件字节整体
不再进入物化** ⇒ 只要 PG（v178+）是干净的，陈旧袋内剥光册字节**不可能**再把它带回 dev，
复投不会再死于本门。这同时封掉了考古案卷里"袋侧旧快照把修复覆掉"的担忧面。

## 三、呈批 / 移交面（本班不动，理由随条附）

| # | 事项 | 证据 | 为何不在本班动 |
|---|---|---|---|
| P-1 | **账本测试残渣 9 行**（`creation_tokens` 内，`created_by IN ('sess-A','s')`，08:03:50–08:06:23）：`docs/_working/lab/{a/seg_001,a/seg_002,b/seg_003}.md` 八条多 token + `docs/real.md`(token=real-1)。七路径**盘面与 dev 双双不存在**（实测 14 个存在性判据全 N） | entry_pk 89222/89223/89224/89228/89232/89233/89236/89237/89238 | 触根宪法 §9.6 测试隔离，属**一类病灶**而非孤立 9 行；建议由注册表车道建"孤儿 token 清扫"机械判据统一清（一次性退役 9 行会被他会话车道的 `reconcile_registry` 复活路径再灌回——`baseline.py` 复活优先分支实测存在） |
| P-2 | **REGISTRY-YAML-PARSE 零审计静默出口**：`registry_yaml_parse_gate.py:364-365` `if not watched: return True,""` 早于 `:385 _audit(...)`；own_scope 过滤（`:361`）把 watch 面对象筛掉时**既放行又不留一行审计**。10-10 09:44 那笔在主区与车道两侧 `registry_yaml_parse.jsonl` 均**查无动作行**（主区 2614 行末条 10:03:52 内 05:00 后 31 条全是 st-examchief；govjudge 车道目录压根没这文件） | 实测 + 读码到 return 行 | 改它＝改**审计面语义**（会给每次不含 watch 面的提交刷审计），且该门被多车道在飞引用；本班组已用 merge 通道补检把这个具体事故面结构性堵死，残余面交门主车道 |
| P-3 | **`_session_ghost_dead` exited 短路**（`scripts/commit_queue.py:1898-1932`，`:1921` 以末行 `status=='exited'` 判会话死）：govjudge R9（裁定#507/1d5c0d36c4）的修复文本**只存在于死车道 index**，工作树 grep=0，未落 HEAD | 实测 `git show dev:scripts/commit_queue.py` 仍原形 | `commit_queue.py` 属"死信三期"他会话在飞域（令卡红线点名）；本班禁改，移交 |
| P-4 | T5(c) **depgraph "design_note/description_cn 列缺席"前提被实测证伪**：`description_cn` 在 `nodes_metadata` 25 列中**在册**；`design_note` 全仓 scripts/src **零命中且无任何写面**，`git log --all -S design_note -- "*.py" "*.sql"` 空；在册亦无任何写工具因这两列报 UndefinedColumn 的实证 | 只读 SELECT `information_schema.columns` + grep + git log -S | 前提不成立就不施工（指令卡前提证伪须停手上报）。请总统统筹确认这条令条出处；如需继续，请给出**具体报错原文/命令**再定位 |
| P-5 | T5(a) `trae_memory` 死源：`backup.ps1:1013` 判据 + `:1019-1020` 现码**已**走 `status="warn"`（commit 48bcbd2faa，2026-10-09，HEAD 祖先）——**修复已在码上**，缺的是一轮完成跑批（10-10 无 report，`backup_state.json` last_run_outcome=lock_skipped）。改指 `.qoder-cn\memory` 还是退役摘列＝在册待裁 **O-11** | 读码 + 实测两份 report 均为修复前批 | 方向选择是 Owner 级（涉及备份覆盖面口径与 O-11 既裁），本班不代拍 |
| P-6 | `ruling_registry.yaml:3543` 裁定#436 写了 `--verify-landed`，实现只有 `--no-verify-landed`（`commit_queue.py:4601`）＝**裁定册教了不存在的参数** | 实测 --help + grep | 裁定册是热册且他会话在飞；随 T5 小件批另袋走 |

## 四、T2/T3（写码车道在飞，本节由总包续账）

T2 只读案卷已把三脸钉到 14 个代码面（★=最像今日病）：S1
`reconciliation_registry.py:9826-9875` stash drop 反向匹配无归属＋任何 commit 都触发；
S2 `git_guard.py:99-100` 把 `stash drop` 当 READONLY 无条件 passthrough；S3
`git_commit_gateway.py:4582-4619` 对"全部非目标"做 `git reset HEAD --`（与脸一
"index 被写回 HEAD 正典态"逐字对得上）；S5 `session_worktree.py:5398-5487`
pre-merge 自动清理把未 claim 的 untracked **物理删**，其唯一保护函数
`:5530-5536 return set()` 是 fail-open；S13 D12 对账尺（landing 前袋面 vs index 求差）
实测**未落地**（`grep -c '"--cached", "--name-only"' commit_queue_landing.py` = 0）。
另实测 `stash_notice.json` 全仓只有两个写点，S1/S3/S4/S7/S8 类整树动作**零登记**＝
在册教训成立。

## 五、口径更正（对令卡背景段）

令卡写"腐蚀窗口 05:47（e835c13349 尚有）→ 09:44（e0c72f63c4）"，实测**方向正确但
起点更早**：`di_seam_exemptions` 于 e0c72f63c4 一笔消失（该笔 110 hunk，首 hunk
`@@ -1,22 +1,14 @@` 同时删掉头 banner 与 `unique_key`，末 hunk 删
`di_seam_exemptions: []`）；而**五枚杂散根键**分两笔更早入库——39b6ee9f1d（10-09
06:47）入 FT/T2a/T2b/T2c，c61765bf25（10-09 21:35）入 CH。另令卡"4 杂散键"实测为
**5 枚**（多出 `file_token`，同形病理）。本台账按实测数记账。

## 六、REGISTRY-MASS-DELETION 伪影自证（提交袋实测）

预检对本袋报 `deleted=833 added=903／条目身份消失 391 条`。391 **恰等于 capabilities
条目总数**，据此判为"身份口径换人"伪影而非删除，并做双口径实证：

| 口径 | dev | disk(修后) | 仅dev | 仅disk | 内容级不等 |
|---|---|---|---|---|---|
| capabilities 按 `capability_id` | 391 | 391 | 0 | 0 | **0**（共有身份 391，字段值逐项对拍全等）|
| creation_tokens 按 `token` | 13212 | 13235 | 0 | +23 | 见下注 |

消失行全部来自同条目**字段序翻转**（`unique_key` 声明回血后身份字段归位首位：HEAD 首
条目以 `- aliases:` 起始，成品以 `- capability_id:` 起始）；render 自身记账
`added=0 removed=0`。据此按门侧处方在 commit message 落
`[allow-mass-deletion:…]` 标记永久留痕。注：内容级对拍中出现 1 个 `None` 身份是**本班
探针函数的取值口径缺陷**（条目缺 capability_id/token 时坍缩），非册面缺陷，已如实标注。

## 七、随 render 带入本 commit 的他人 token（归属留痕，不吞不藏）

Owner 禁"重打投影袋"条款的正向处置：T1① 修复必然把 PG 现值带上 dev。净增 23 枚中
**22 枚属他会话已入账登记**（`created_by` 字段仍归原主，账本可反查）：

| created_by | 枚数 |
|---|---|
| st-backfix-20261010 | 3 |
| st-constland-20261010 | 2 |
| st-datalane-20261010 | 9 |
| st-finalclean2-20261010 | 3 |
| st-govjudge-20261010 | 1 |
| st-nightmine2-20261010 | 1 |
| st-maint1-20261010（本班自持）| 1 |

明细（token ← file）实测清单已落 `.runtime/tmp/st-maint1-20261010/render_brought_in_tokens.json`。
本班**未替他方登记任何条目**，亦未从本 commit 中删除任何他方条目。

## 八、T2 已交付（写码车道 st-maint1-t2lane，总包复核前状态）

判据落点（车道行号）：治理面单一真源 `stash_owner_candidates:9835`／
`anchor_stash_drop:9890`（`update-ref refs/quarantine/stash-<sid>-<ts>-<sha8>` 后必须
`show-ref --verify` 复核可见，否则不 drop）／`govern_stash_drop:9949`（三前置判定）／
`drop_governed_stash:10062`（**全模块唯一** `git stash drop` 出口，动手与豁免均落
`.runtime/gate_audit/stash_drop_governance.jsonl` 带 `did_drop`）。活性判据**复用不改造**
（`liveness_verdict`，仅 `state=="dead"` 可动手，alive/degraded/ghost 一律豁免）。
`git_guard`：`STASH_READONLY` 摘掉 `drop`，新增 `STASH_DESTRUCTIVE={drop,clear}` +
`_handle_stash_destructive:672`，`clear` 由 warn 升默认阻断，逃生走
`ZEPHYR_STASH_DROP_ESCAPE=<白名单 reason>` 且**逃生只免归属判定、仍逐条落字节锚**。

判据口径变更（红线要求同批留痕）：`test_stash_lifecycle.py` 原 L283-303 把"drop 掉
`other-session-wip-*`"当**期望**＝把 bug 立法，已改判并在测试与车道台账 §判据口径变更
双处写明理由。

红证（车道报称，待总包进程外复跑）：RED-A 主区未修码 `dropped=1`（在场活会话在飞面被
drop）；RED-B 主区 `git_guard stash drop` → `Dropped stash@{0}` RC=0 且 `refs/quarantine/`
空＝零存证。GREEN：新件 17 passed、改过的 `test_stash_lifecycle.py` 单跑 38 passed、
两件合跑 55 passed、宽网 `tests/gov/governance/audit -n 4` = 1854 passed 1 skipped。

车道申报的移交项（总包处置）：①`scripts/governance/d1_structure/cleanup_stash.py:120`
会被新闸门拦，需带逃生 reason 或改走 `drop_governed_stash`；②`session_worktree.py:4150
_drop_session_pre_merge_stash` 仍无锚；③新建件需 `add_module_translation`／depgraph
登记面（本班集成批负责）。

## 九、本班自证的一条 T3 现场病例（写码车道开工后实测命中）

正门 `session_worktree.py create` 以 **pid=0** 注册本班会话（在册铁律），但随后每次
`lock_files.py acquire` 走 claim **懒注册**分支把条目 PID 改写为**瞬态 CLI 进程的 PID**；
CLI 退出后主区判会话死 → 提交被 `[SESSION-REQUIRED] session 未注册` 拦下。这是 T3 判据
缺陷（"注册表 PID 位陈旧 shell 把在场活会话判死"）**在总包自己身上的一次完整复现**，
与 T3 案卷钉的 `claim_file()` 懒注册行 + `_is_session_alive()` pid>0 零宽限分支逐字对得上。
当班处置=按正门重新 `register(sid, pid=0)` 后即刻提交（窗口压最小）；治本归 T3 件。

