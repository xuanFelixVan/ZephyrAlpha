---
ttl: task_bound
completes_when: 本案卷读数被总包在 dev 侧复核，且其中点名的在册缺陷被属主车道承接
generated_by: 本班只读车道（弱模型出案卷不出裁定），落地面由 st-fclean4-20261012 复核
session: st-fclean4-20261012
lane: wave4-lane_q2_dedup
role: 只读调研案卷（零删除、零 git 写、零改判据）
---
# 终清波四·车道案卷：M3-Q2 quarantine 内容寻址去重测量（面复点／索引／消费者兼容／压缩样本）

> 原稿面＝`.runtime/tmp/st-fclean4-20261012/lanes/lane_q2_dedup.md`（TTL 临时区），本件为其入册副本；
> 数值口径以该案卷自带的时刻与参照点声明为准。
# Q2 内容地址去重 · 测量册（drift_* 面）

前班基线 = `docs/_working/finalclean2_campaign/wave3/lanes/lane_quarantine.md`（2026-10-11 15:29:24Z 快照：
9,388 件 / 2,574 relpath / raw 可删 3,702 件 / 100,122,551 B）。
**注意：两面不可直接差分**——本窗内面被第三方收缩过（§1 审计留痕），基线的 10-01/10-02 族已不在今日全集。

## 1. 面复点（实测 20261012T132114Z–132117Z；out/q2_face_recount.json）

| 指标 | 基线(10-11 15:29Z) | 本测(10-12 13:21Z) | Δ |
|---|---|---|---|
| 顶层项 | 7,481 | **6,519** | −962 |
| drift_<ts> 目录 | 7,427（15:38Z 复测 7,434） | **6,468**（严格命名匹配 6,468/6,468，`other_drift_items=[]`） | −959 vs 15:29Z |
| drift 内文件 | 9,388 | **8,062** | −1,326 |
| drift apparent B | 679,859,943 | **658,070,696** | −21,789,247 |
| 全目录 apparent B | 700,794,449 | **678,053,289**（**口径=sum(os.path.getsize)，非 du 占用**） | −22.7M |
| 非 drift 项/件/B | 55 / 911 / 13.7M+7.2M(patch) | **51 / 938 / 19,982,593** | patch 族 45→**39 枚/5,942,662 B**；新族 `fclean3_safety`(32/308,020)、`finalclean2_branch_sweep_20261011T233903Z.jsonl`(1/29,030)；`branch_refs.log` 1,536→1,666 B；余族同名 |
| drift 首/末枚 | 10-01…10-11 | **`drift_20261003T160058` … `drift_20261012T112654`** | 10-01/10-02 族整段消失 |

**收缩取证（非推测）**：`.runtime/audit/worktree_drift_watchdog.jsonl` 实测 `quarantine_retention_sweep` **1,134 条，全部 kind=empty_shell**（0 条 expired），窗口 2026-10-12T00:01:43Z–00:02:08Z，retention_days=30 ⇒ 10-01/02 目录在 10-11 晚些先被**带外清掉了文件**（本车道无法归因是谁，如实陈报），余空壳由 watchdog 本家清扫在今晨删除。写入方仍在飞（末枚 11:26:54Z，state `quarantine_last_sweep=2026-10-12` 已跑）。
⇒ "增速 ~743 枚/天"本轮**不可正测**（净变化 −966/21.7h，新增与带外删除混叠）；只报净数。
复算：`python .runtime/tmp/st-fclean4-20261012/tools/q2_face_recount.py`；审计计数见 §7 命令。

## 2. 内容地址索引（**全集 8,062/8,062 件，零抽样**；13.4s；out/q2_dedup_index.csv.gz · q2_dedup_groups.csv.gz · q2_dedup_summary.json）

| 指标 | 实测 |
|---|---|
| 唯一 relpath | **1,694** |
| distinct (relpath, raw_sha) 态 | **4,693** |
| distinct (relpath, norm_sha) 态（eol 归一） | **4,321** |
| 不可读件 | 0 |
| raw 方案可删重复（每态保 1，代表=最早目录） | **3,369 件（41.8%）/ 96,850,596 B（14.7% of drift B）** |
| norm 方案可删重复 | **3,741 件 / 100,819,174 B**（比 raw 多回收 372 件/3.97 MB ⇒ 归一键多收 ~4%） |
| 去重后**整枚清空**的 drift 目录 | **2,950 / 6,468（45.6%）**（精确=代表规则"保最早"；任意代表规则上界 3,015） |

Top-20 可省字节 relpath（完整表在 q2_dedup_summary.json `top20_relpahs_by_reclaimable_bytes`）：
`capability_canonical_file_registry.yaml` 6 枚/23,663,060 B、`module_translation_registry.yaml` 4 枚/14,290,942 B、`architecture_issue_registry.yaml` 3 枚/5,011,668 B、`agent_role_based_access_control/blueprint.md` 6/2,895,091、`large_language_model_security/blueprint.md` 8/2,375,530、其余 blueprint/manifest 族 ≤1.75 MB/枚。
⇒ 与基线同形结论复现：**去重=枚数利器（−41.8% 枚、45.6% 目录壳可清），非体积利器（−14.7% B）**。
复算：`python .runtime/tmp/st-fclean4-20261012/tools/q2_dedup_index.py`（流式双 sha＋dev sha 缓存线程池，单进程）。

## 3. 重复件（将被去重丢弃枚）对 dev 现值分桶（A=磁盘字节==dev｜B=行尾归一后等｜C1=有同名 dev 但异｜C2=dev 查无）

| 桶 | raw 方案丢 3,369 枚 | norm 方案丢 3,741 枚 |
|---|---|---|
| A | 51 / 1,441,417 B | 67 / 1,852,040 B |
| B | 98 / 1,552,468 B | 161 / 2,179,516 B |
| C1 | **2,827 / 90,495,180 B** | **3,120 / 93,426,087 B** |
| C2 | 393 / 3,361,531 B | 393 / 3,361,531 B |

**读数**：去重将丢的字节里 **93.6%（raw 口径 C1+C2=93.86M/96.85M）与 dev 现值不同**（C1 为主）——即"重复"仅指**同 relpath 同态的第二份起**，其内容本身多非 dev 现值。⇒ 去重丢弃≠零信息量；"只归档不删"红线在此数据下**不是保守姿态而是必要动作**（丢件仍含异于 dev 的历史字节，惟同态组内任一份即全量信息，归档 1 份保全部字节信息）。

## 4. 兼容面（全部 file:line 实读）

### 4.1 `src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py`
- 常量：`GATE_ID`:89｜`_QUARANTINE_DIR=".runtime/quarantine"`:97｜retention 30d:98｜空壳宽限 60s:101｜`_KNOWN_QUARANTINE_CAP=500`:103。
- 写路径 `_snapshot()`:479-498：dest = `root/.runtime/quarantine/drift_<UTC %Y%m%dT%H%M%S>/<rel>`（:487-488），P2-2 先验源后建目录（源消失→返回 ""，:491-492），返回**文件路径**相对 root（:495）。
- `_sweep_quarantine()`:545-606：顶层枚举 `sorted(qdir.iterdir())`（:565）；**非目录或不以 `drift_` 开头 → 直接 skip（连 kept 都不计）**（:566）；`drift_` 前缀但名解析 `%Y%m%dT%H%M%S` 失败 → `kept++` 豁免（:569-571，人工存证不碰）；两类删除：①空壳（树内无文件）且 mtime 超 60s → kind=empty_shell（:574,:579-580）②ts < now−30d → kind=expired（:561,:581-582）；唯一删除通道 `safe_rmtree(d, allowed_prefix=qdir, ignore_errors=True)`（:590），逐条 `_audit` kind+dir.name（:594-603）。
- `_maybe_sweep_quarantine()`:609-627：日级节流（state `quarantine_last_sweep`，同日一次），清扫后按 removed 目录前缀摘除 known_quarantine 条目（:620-624），`removed` 则 `_lifecycle_log`。
- `known_quarantine` 登记：快照**文件路径**入列（:1352-1355），封顶 500（`del known_q[:-500]`:1356）。**tamper 判定**:1150-1170：对每个登记项 `d` 测 `(root/d).is_dir()`——而条目恒为文件路径 ⇒ **现码下每个登记项在下一轮扫描必判 tamper 并被摘除**（无论文件是否在场）。实测佐证：审计流 224 条 tamper，`file` 字段皆文件路径、`worktree_now=missing`；现 state.json `known_quarantine=[]`；测试注释亦自认登记的是文件路径（test:402-404）。**⇒ 对原型：把文件移走不会产生"新的" tamper 信号形态——该通道本就是常鸣假阳性，原型不得以"零 tamper 告警"自证安全。**
- 谁在枚举顶层、会把我的归档计成 drift 吗：仅 `_sweep_quarantine` :565 一处（跳过非 drift_）；`git_commit_gateway.py:4615` 锚 `non_target_unstage` 子根（现不存在）；`session_worktree.py:849,969,7749` 只写 patch 文件不枚举；`write_audit_daemon.py:84` `(".runtime/quarantine", True)`=**该区写入免审计**（原型写归档不会进 write_audit，也不被自激）。`scan_once` 的 dirty 面=git tracked 工作区，`.runtime` 不 tracked ⇒ 归档目录不会被判"漂移"。
- **空壳路径对原型的直接后果**：去重若把某 drift 目录掏空，该目录名会在**下一个 daemon 日的 sweep**被 empty_shell 通道自家删（60s 宽限后），审计只记 `file=d.name`（:600）——字节安全（同态信息已在保留份），**目录名账目会消失**；反之 `dedup_archive/`（非 drift_ 前缀）落在 qdir 顶层=清扫完全豁免。
- `safe_rmtree` 授权语义 `src/zephyr/shared/io/file_utils.py:679-716`：resolve 后必须**严格落在** `allowed_prefix` **之内**（等于前缀本身也拒 :699-703）＋逐层拒 reparse point ⇒ 前缀是 `qdir` 时，**qdir 下任何后代（含 dedup_archive）将来都可被该通道删**；"archive-only"若要连归档都不许删，须另立断言，不能指望 allowed_prefix 天然挡它。

### 4.2 `scripts/governance/evaporation_blackbox.py:349`
恢复指引仅**打印**"untracked 本体不存黑匣子——对照 .runtime/quarantine/ 漂移存证与 G:/backup 备份链"——按路径查证的读者，不枚举、不断言目录数。移动/改名使"按原 drift 路径查证"落空；**内容寻址归档+路径映射册可保住该查证性**（映射册即恢复指引的目标）。

### 4.3 `scripts/ops_guard.py:90-100`
`.runtime/quarantine` ∈ `PROTECTED_PREFIXES`（:99，注释:95-98 实证两起带外裸删事故）。**将来任何真删步骤**：人工/带外通道须 `ZEPHYR_FORCE_DELETE=1`（:98 注释），本家通道=`safe_rmtree`+留痕。原型若只"移动/复制入归档"不触删除，不撞此闸；一旦触删（含空壳）必以 safe_rmtree(allowed_prefix=qdir) 形态被允许——即红线要在流程层守，不在 guard 层自动守。

### 4.4 tests/ 断言面（tmp fixture 仓跑，**不读真实 quarantine**，今日实测零会挂；原型若改码须对照的在册断言）
`tests/gov/governance/rule_bridge/test_worktree_drift_watchdog.py`：:81-89（scan 后 `glob("drift_*/hot.txt")` 快照必在）｜:317-331（retention 清旧保新）｜:334-345（rmtree 已登记快照目录→判 tamper——**注意 :340 取目录、:1153 测 is_dir，文件路径登记形态下该测试对"移动文件"不敏感**）｜:351-357（源消失不建壳）｜:360-383（空壳过宽限清＋kind=empty_shell＋审计 `file==shell.name`）｜:386-394（60s 内在飞空壳不删）｜:397-417（自清扫后 known_quarantine 对账摘除；注释:402-404 确认条目=文件路径）｜:474 同 glob。`tests/gov/git/test_session_worktree.py:2578`（retire patch 落 quarantine 目录名断言）。宽 grep `drift_`/`quarantine` 其余命中皆异族（kill_switch/orders_quarantine/rollback 等，file:line 见 out 无必要——与本面无关）。

## 5. 归档形态事实

### 5.1 gzip（zlib level 6，流式）实测——out/q2_gzip_sample.csv.gz / q2_gzip_sample.json
样本=raw 方案重复丢枚 **n=32**（24 relpath；含两册大 YAML **全部**在面重复枚：capability 6 枚+module 4 枚，其余按尺寸步距补齐）。
样本账：**38,190,920 B → 6,299,349 B，字节加权压缩比 0.1649**；单件比 0.1232–1.4444（**存在膨胀件**——小/已压缩内容）。两册 YAML 单件比实测：capability 0.1232–0.1260、module 0.2272–0.2278。
**外推（标注：extrapolation，非实测全集）**：96,850,596 B × 0.1649 ≈ **15,974,888 B（≈15.3 MB）归档体积**。样本偏置申报：样本原始字节 38.2 MB 中大 YAML 占 22.7 MB ⇒ 加权比偏向大文本；若丢件总体小文件占比高，真实值应劣于此数（上界风险另以 per-file 最大 1.44 记）。
未测：xz/zstd、tar 头/目录结构开销、跨文件字典复用。

### 5.2 CAS（一 sha 一物+指针册）vs 逐 drift 目录 tarball——仅事实
- 跨 relpath 同内容：**4,685 个 distinct raw_sha vs 4,693 个 (relpath,sha) 组 ⇒ 仅 3 个 sha 被多 relpath 共享**（q2_dedup_summary.json `cas_facts`）——CAS 相对 per-relpath 方案的跨面去重增益≈0（本面内容形态决定）。
- 索引规模：CAS 物=4,685 对象 + 8,062 条指针（drift_dir,relpath→sha）；tarball 方案=至多 6,468 个归档 + 目录级映射行。
- 恢复粒度：CAS=按 (dir,relpath) 精确取回单件；tarball=按目录整体取回（tar 内可拆但需展开）。
- evaporation_blackbox:349 的查证键是**原路径**——两案都须另存原路径映射册（CAS 的指针册天然携带；tarball 需生成）。

## 6. 归档可住哪里——事实

- `shutil.disk_usage("D:/")` 实测（13:26Z）：**total 785,119,178,752 / used 709,964,840,960 / free 75,154,337,792 B（≈70.0 GB）**。外推归档 ~15.3 MB ⇒ D: 现空闲足够（若驻留）。
- docs/01_policies_and_standards 在册文本（grep 正对照=有命中，尺有效）：
  - `sop/construction_sop/construction_workflow_policy.md:181`——Owner 裁定"**归档不删**不再更新"先例措辞（对象=审查指令册，非 quarantine，但"归档不删"是本仓在册处置语）。
  - `_registry/catalogs/ruling_registry.yaml:3617`——补-20 磁盘案先例：`blobs_archive 7051 件 1.17G ... 归档 G:/backup/zephyr_cold_queue`、`quarantine 过期 218 目录`删除记帐 ⇒ **存证归档落 G:/backup 子树已有裁定先例**。
  - :1742（retroactive quarantine 一词，无关）、:4191（C103 OrderFileStore quarantine 语义，无关）。
  - 存储轴公理（根 AGENTS.md §7）：业务数据∈{主库, 冷库 F:/zephyr_cold}，备份总仓 G:/backup，E=纯软件——quarantine 存证非业务数据，属"取证证据"，在册文本未给专属驻留位；最近邻实践=G:/backup 子树（上引先例）。
- 未查到 `.runtime` 存证归档位置的专门政策册（检索词：只归档/归档不删/archive-only/quarantine.*归档）；若总包需成文，属新立。

## 7. 复算命令总表

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd /d/ZephyrAlpha
python .runtime/tmp/st-fclean4-20261012/tools/q2_face_recount.py   # §1
python .runtime/tmp/st-fclean4-20261012/tools/q2_dedup_index.py    # §2/§3（13.4s，单进程）
python .runtime/tmp/st-fclean4-20261012/tools/q2_gzip_sample.py    # §5/§6.1
# 审计计数（§1/§4.1）：Grep quarantine_retention_sweep|quarantine_tamper .runtime/audit/worktree_drift_watchdog.jsonl
```

## 8. 残余未覆盖面（强制申报）

1. **面在飞**：§2 索引=枚举时刻（13:22Z）的 6,468 枚/8,062 件全集内逐件跑完、零抽样；但 13:22Z 后新落 drift 枚不在账（实测末枚 11:26Z，窗口内无新增证据；下一班须以 §1 命令复点）。
2. 非 drift 族 938 件未入去重索引（裁定主体=drift_* 家族，如实分账在 §1 不判）。
3. 压缩仅测 gzip level6 流式样本 n=32；全集压缩、xz/zstd、tar 容器开销、跨文件字典**未测**；外推已显式标注。
4. **未归因** 10-01/10-02 文件带外消失的责任车道（审计流只证空壳由 watchdog 清）；未核 `.jsonl.1` 轮转段。
5. 未实测"原型真的移走文件后"的 daemon 行为（零写 quarantine——§4 结论全部来自源码+在册测试语义，非行为实验；其中 tamper 假阳性通道有 224 条自然实验读数佐证）。
6. 未验证 GENERATED 投影两册可否由 PG `registry_snapshot` 历史版本重导（写面/DB 面，未起）——只影响"HAS_UNIQUE 体积主杠杆"旧题，不影响本册去重数。
7. dev 分桶（§3）用 `git show dev:<rel>` 现值 sha 对比，未处理 git 工作树属性过滤（前班同口径，可比）。
