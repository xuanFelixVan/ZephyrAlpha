---
ttl: task_bound
completes_when: 波三 tmp 车道分账被 00_ledger 收账，且 Owner 对「波二预筛面已消失之追溯」「C2 业务资产面」「pytest 残留可清面」三项出批文后转终态
lane: L_tmp
sid: st-fclean3-20261012
role: 只读调研车道（案卷不出裁定；零删除；零 git add/commit）
machine_readable: .runtime/tmp/st-fclean3-20261012/out/tmp_lanes_casefile.csv
---
# L 车道案卷：`.runtime/tmp/` 全树归属＋活性＋引用＋四态分账（终清波三）

> 唯一真源口径：四态定义取 `docs/_working/finalclean2_campaign/00_ledger.md:34`
> （①hash==HEAD 铁证才删｜②有增量价值先救后清｜③判死四元联言｜④在飞/存疑零动作记表；默认动作=留）。
> 本卷**只出案卷不出裁定**；判死一律墓碑制，无一条建议裸删。
> 全集键集合＝`set(现扫 top-level) ∪ set(波二 tmp_hash.csv top-level)`＝**1632** 键；下文一切计数按此全集口径，剩余面在 §9 申报。

## 0. 规模与漂移复测（本班 2026-10-11 23:24–23:44 本地实测）

| 面 | 工令/波二基线 | 本班现测 | 漂移 |
|---|---|---|---|
| 一级条目数 | — | **1546**＝1210 目录 + 335 散件 + **1 扫不动面**（`pc_cache`，`os.scandir` EACCES 拒绝访问，非 reparse point，本卷读数 0＝**盲区**，§9 申报） | 新测 |
| 文件数 | 791,438（工令） | **791,713** | **+275** |
| 字节 | 52.2 GB（工令）／56,733,995,849 B=52.84 GiB（波二 10-10 档） | **54,756,330,334 B = 50.99 GiB** | vs 波二 **−1,977,665,515 B（−1.84 GiB）／−37,892 件** |
| `st-*` 目录数 | 149 | **149**（现存）＋**5 已消失**＝154（并集口径） | 名数**零漂移**；成员集已换血 |
| `st-*` 字节 | — | **51,635,580,463 B = 48.09 GiB**（528,144 件，占全树 94.3%） | 全树最大面确认 |
| 非 `st-*` 字节 | — | **3,120,608,816 B = 2.91 GiB**（263,560 件） | — |

复算：
```
python .runtime/tmp/st-fclean3-20261012/out/walk_tmp.py        # 59.3s 单进程全树扫 → tmp_top_entries.csv
ls .runtime/tmp | grep -c '^st-'                               # 现=150（含本班 st-fclean3-20261012，故真实 149）
python .runtime/tmp/st-fclean3-20261012/out/join_hash.py       # 流式读 138MB 旧档 → tmp_hash_join.csv
```

⚠ 工令「`st-*` 目录 149 个」名数虽零漂移，**成员已不同**：10-10 基线里的 5 个 `st-*` 目录现已不存在（§3）。

## 1. 149 个 `st-*` 车道：三件定窗分层（逐目录全表＝`tmp_lanes_casefile.csv`，149 行＋5 消失行）

属主三源实测口径（全部现测，非引用旧档）：
① SessionRegistry 在册＝`.runtime/session_registry/<sid>.json` 分片在场（主真源，`session_concurrency.py:26`）；现册共 16 片，命中 11 个现存 st 车道。
② 心跳＝`.runtime/sessions/<sid>/heartbeat.jsonl` 的 mtime＋末行 `status`（380 个会话目录中有心跳文件者 76/150）。
③ 进程表＝`Get-CimInstance Win32_Process` 快照（429 进程）cmdline 含该 sid。

| 层 | 判据 | 目录数 | 字节 | 件数 | A_b 合计 | C2_b 合计 |
|---|---|---:|---:|---:|---:|---:|
| **T1 硬在飞** | ①在册 ∨ ③进程命中 | **11** | 19,207,903,649（17.89 GiB） | 195,891 | 1,670,809,273 | 16,979,906,976 |
| **T2 心跳 7d 内非硬活** | ①③皆零 ∧ ②<10080min | **41** | 187,515,630（0.17 GiB） | 2,758 | 5,361,817 | 94,747,387 |
| **T3 三源零＋静默>7d** | ①②③ 皆零/超 7d ∧ 目录 mtime>7d | **66** | 5,721,895,108（5.33 GiB） | 12,834 | 650,621 | 5,702,283,013 |
| **T4 存疑其余** | 心跳缺失或超 7d 但静默<7d 等 | **31** | 26,518,266,076（24.70 GiB） | 316,661 | 75,698,457 | 29,156,974,931 |
| 合计 | — | **149** | **51,635,580,463** | 528,144 | 1,751,890,168 | 51,933,912,311 |

### 1.1 T1 硬在飞成员（11，一律态④零动作）

`st-datalane-20261010｜st-deadcure2-20261009｜st-deadcure3b-chief-20261011｜st-dexp-20261009｜st-final4-20261010｜st-finalclean2-20261010｜st-fullflow2-20261008｜st-gpux-20261011｜st-gpux2-20261011｜st-mineloop-20261010｜st-nightmine-20261010`

**今晚六班核对（工令 §1，实测逐一落位）**：
| 班 | sid（实测） | tmp 车道目录 | 三源读数 | 判定 |
|---|---|---|---|---|
| 矿考 | `st-mineloop-20261010` | 存在 10,111,649 B | REG∧PROC(27360)∧心跳 0.1min | 态④ |
| 追凶 | `st-backfix3-20261011` | **无 tmp 目录**（REG 在册∧心跳 23:32 新鲜） | REG∧HB | 态④（无本面资产可动） |
| GPU 化 | `st-gpux-20261011`＋`st-gpux2-20261011` | 存在（1,607,962／1,919,688 B） | REG∧PROC∧HB∧WT | 态④ |
| 数据车道 | `st-datalane-20261010` | 存在 93,943 B | REG∧PROC(6 命中)∧**心跳末行 exited** | 态④（见 §8 铁律正证） |
| 维护三班 | `st-maint3-20261011` | **无 tmp 目录**（有 `.runtime/sessions/` 目录＋worktree） | HB 23:14 | 态④（无本面资产可动） |
| GPU 工单班 | `st-gpuwo-20261011` | **无 tmp 目录**；其在飞件本体为根级散件（§3.2） | REG∧HB 23:32 | 态④ |

> 六班的**在册真名与工令俗称不同**（追凶＝`st-backfix3-*`，非 `st-maint*`；维护三班＝`st-maint3-20261011`，`st-maint2-20261011` 是其前任且已在册判死），真名出处实测＝`docs/_working/maint3_campaign/00_ledger.md:7`、`docs/_working/maint2_campaign/00_ledger.md:363`、`docs/_working/gpufeed_campaign/03_gpux_final_report.md:113`。六班资产全部态④，本卷零动作。

### 1.2 引用检查（全集，非抽样）

扫描面＝`docs/_working/**` 全 4,344 文件（228,860,117 B）＋ `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`；150 个 st 名一次性正则（长名优先防前缀互吞，实测 `st-nightmine-20261010` 是 `...20261010b` 的前缀，未排序即串判）。
结果：**被点名 119 / 149，零引用 30**；零引用∧三源零（T3）＝66 目录中经引用扣除后落 **态②＝12 目录 / 9,283,730 B**（全表 §1.3）。

复算：`python .runtime/tmp/st-fclean3-20261012/out/refscan.py` → `sid_reference.csv`（列 sid,total_occurrences,distinct_files,checkpoint_family_hits,ruling_registry_hits,sample_files）。

点名最多 top（价值面，见 §7）：`st-cure-p05-20261006` 1501 次/6 件、`st-metaq-20260923` 1342/344、`st-cure-p05b-20261006` 1163/7、`st-cure-p10-20261006` 971/7、`st-cure-p01-20261006` 708/7、`st-cure-p09-20261006` 348/5、`st-tests-chief-20261004` 285/16、`st-ailayer-final-20260924` 283/108、`st-t0-matrix-20260924` 213/66、`st-metaq-gc-20260924` 211/46。

## 2. 与波二 `tmp_hash.csv` 的 join（A/B/C1/C2 构成）

**口径修正（必须先报）**：旧档 `basename_matches_head` 列**不是布尔**，而是「HEAD 内同名 blob 的个数」值域实测 {0,1,2,568,629,1185,…}；`raw_equal`/`normalized_equal` 值域＝`{"",Y,N}`（空者 639,222 行＝同名查无）。首版按布尔解析会把 147,177 枚 A 件误判成 C1——**本班未沿用旧档默认，改正后重算**。

**对账验证（旧档可信度）**：以修正规则重算的六目录构成与波二 `11_tmp_dir_dossier.md` 表内值**逐一全等**——
`st-zc8-lane-rb-20260928` 119/0/946/9425 ✓｜`st-zc8-verify-20260928` 516/6/2650/26716 ✓｜`st-tclose-cardfix-20261004` 0/0/0/5 ✓｜`st-deadcure2-20261009` 126622/357/5211/61521 ✓｜`st-zchief8-20260928` 804/4/6832/69924 ✓｜`st-nightmine-20261010` 873/49/35/106 ✓；字节合计 56,733,995,849 与旧档 52.84 GiB 全等 ⇒ 本班解析＝波二解析，可复用。

全集构成（1632 键并集）：**A 147,177 件／1,951,071,154 B（1.82 GiB）｜B 529 件｜C1 42,677 件｜C2 639,222 件／53,559,693,769 B（49.88 GiB）**。
C2 面与 `docs/_working/finalclean2_campaign/00_ledger.md:600` 在册「C-2 49.89 GiB 已裁三档制」差 0.01 GiB（同源同尺，口径一致）。

**旧档时效的现测复核（铁律：别直接信旧档判死）**：从 T3 车道里分层抽 14 枚 A 件，现算 sha256 与 HEAD blob 对拍（`git rev-parse HEAD:<headpath>` 的 blob sha ＋ `git hash-object` ＋ 双端 sha256 三重）：**14/14 铁证成立，零漂移**。
明细＝`.runtime/tmp/st-fclean3-20261012/out/a_class_spotcheck.csv`；复算 `python .runtime/tmp/st-fclean3-20261012/out/spotcheck.py`（随机种子 20261012，可复现）。

## 3. 重大漂移申报：波二 §一 预筛可清面 **10/10 已全部消失**（工令「至今一字节未动」与实测不符）

| 波二 §一 目录 | 基线字节 | 现测 |
|---|---:|---|
| st-zc8-lane-rb-20260928 | 2,701,590,973 | **不存在** |
| st-zc8-verify-20260928 | 256,606,584 | **不存在** |
| st-tclose-cardfix-20261004 | 227,202,002 | **不存在** |
| st-zc8-lane-k2-20260928 | 204,880,511 | **不存在** |
| st-zc9-lane-sec-20260930 | 145,831,933 | **不存在** |
| rebase3w | 32,168,146 | **不存在** |
| sw18_six2 | 30,425,665 | **不存在** |
| p4_verify | 21,529,203 | **不存在** |
| st_fms_tc_l1 | 13,431,444 | **不存在** |
| zmaster2_coord | 13,407,608 | **不存在** |
| **合计** | **3,647,074,069 B = 3.40 GiB** | 全树一级条目并集里消失 87 键／3,658,678,121 B |

旁证（非本班判语）：波二自家执行器 `exec_c_second_pass.py` 现跑输出即称「[st-zc8-lane-rb-20260928] 原位已不存在，跳过」等 3 条。
**墓碑侧查无对应**：`.runtime/quarantine/`（7,489 条目）内按名匹配这 5 个消失 st 目录 **零命中**；最新 retire patch 停在 10-10 17:35。
⇒ 案卷登记两条待裁事实：①「预筛面已消失」与工令前提矛盾；②「消失而未留墓碑名」与 §2.9/裁定#375 墓碑制要求的存证面不闭合。本班不裁是谁删、也不裁合规与否，只报可复算读数。
复算：`for d in <上列10名>; do [ -e .runtime/tmp/$d ] && echo PRESENT || echo GONE; done`；`ls .runtime/quarantine | grep -E 'zc8|cardfix|zmaster2'`。

## 3.2 非 `st-*` 面族系分类（1477 键；大表在 `tmp_lanes_casefile.csv`，`is_st=0`）

| 族系 | 条目数 | 字节 | 件数 | 备注（只登记不处置） |
|---|---:|---:|---:|---|
| backfix_* 备份链演练/期刊族 | 109 | 2,068,225,390 | 3,769 | 含 `backfix_shadow`(593MB)／`backfix_reset_recovery`(326MB)，波二 §二 在册引用 2/1 |
| 其它一级目录 | 135 | 836,827,756 | 31,995 | 例 `ALL_LANE_ARTIFACTS`/`a2_census`/`qcloseout_20260928` |
| 根级日志/清单（.log/.txt） | 188 | 160,042,131 | 142 | 合法扩展名（目录册 allowed） |
| **`pytest_<PID>` 测试残留** | **789** | 25,680,095 | **227,230** | **PID 实测已死 767／仍活 22**；件数占全树 28.7% |
| 波二后新增面（基线无） | 120 | 13,613,813 | 187 | 零 HEAD 铁证，态④ |
| `st_*` 下划线旧命名车道 | 5 | 13,068,793 | 48 | 与 `st-` 连字符名不同族，勿混判 |
| 根级机读数据（.csv/.json/.yaml/.jsonl） | 20 | 2,522,302 | 15 | **违 `.runtime/tmp/` allowed 册**（见 §5.2） |
| 根级脚本（.py/.ps1/.sh） | 78 | 544,994 | 67 | 含六班在飞件本体（下行） |
| b*_ 批次残件／audit* 快照 | 22 | 83,542 | 106 | — |
| 已消失面（10-10 后） | 10 | 0 | 0 | ＝§3 预筛面 5 个非 st 目录＋5 枚散件 |
| `rescue/` 目录 | 1 | （在「其它一级目录」内） | 15 子项 | 波二 C 件救件存证面，属主 `st-finalclean2-20261010` 在册 T1 |

**在飞件本体点名（态④禁碰，实测存在）**：`.runtime/tmp/gpuwo_eval_existing_adapter.py`＝GPU 工单班（`st-gpuwo-20261011`，在册、心跳 23:32 新鲜，其 tmp 车道目录不存在，件落根级）。同类根级在飞件随 backfix/gpux 族在 §3.2 行内登记。

## 4. 波二工具链存活面（`.runtime/tmp/st-finalclean2-20261010/tools/`）＋本班自罚事故申报

清单实测＝**27 支 .py**（工令估 18，漂移 +9；复算 `ls .runtime/tmp/st-finalclean2-20261010/tools/*.py | wc -l`）。`--help` 现跑：**26 支未抛错、1 支抛 Traceback**（`scan_dev_delta.py`，其主逻辑需前置件）。带 argparse（即 `--help` 安全）者实测**仅 5 支**：`agg_tmp_a.py｜mk_ledger.py｜scan_dirs.py｜wave2_t3_restore.py｜wave2_tmp_sweep.py`；**其余 22 支**（`annotate_owner_answers｜exec_c_second_pass｜exec_c_tomb｜exec_tmp_a｜fourth_source_selfcheck｜inject_token_bridge｜mk_c_receipt_rows｜mk_closeout_block｜mk_dir_dossier｜mk_t7_block｜scan_dev_delta｜scan_orphan_vs_ref｜sweep_merged_branches｜t0_recon｜t0_rescue｜t0_triage｜t0_verify｜t7_anchor_btier｜t8_evidence｜t9_forced_close_audit｜wave2_classify｜wave2_rescue`）为 `if __name__=="__main__": main()` 且**无 dry-run 门**，`--help` 被忽略即**直接执行主逻辑**。两把尺（`scan_dirs.py`/`wave2_tmp_sweep.py`）与墓碑执行器（`exec_c_tomb.py`）均在清单内可跑，后者现跑即 REFUSE 防混批。

⚠⚠ **重大自罚申报（本班施工纪律事故，如实入卷）**：工令要求「`--help` 级别确认，不改它们」，本班照做；但**27 支里只有 7 支带 argparse**（`agg_tmp_a.py`/`mk_ledger.py`/`scan_dirs.py`/`wave2_t3_restore.py`/`wave2_tmp_sweep.py`/`scan_orphan_vs_ref.py`/`scan_dev_delta.py`），**其余 20 支 `if __name__=="__main__": main()` 且无 dry-run 门**，`--help` 被当普通参数或直接忽略即**执行主逻辑**。本班因此在 23:37–23:40 触发了以下副作用（全部非本班申报写面）：

| 工具 | 实际副作用（实测） | 后果与本班处置 |
|---|---|---|
| `sweep_merged_branches.py` | 读 10-10 陈旧 `scan/branches_all.txt` 逐支 `git branch -d`，**真删 1 支**：`ai/st-datalane-20261010/task-datalane-sixpack`（sha `15b147066e99e21fb952f0c325873669564774e3`，其 tip 已是 dev 祖先＝零字节灭失）；证据 `.runtime/quarantine/finalclean2_branch_sweep_20261011T233903Z.jsonl`（217 行：deleted 1／kept_not_ancestor 205／kept_other 11） | **本班已按存证 sha 复原该分支 ref**（`git branch <name> <sha>`，加性操作，非 add/commit/删除），现测 `git rev-parse` = 15b147066e… 与删前全等 ⇒ 盘面回到本班动手前状态；数据车道（在册六班）的分支面已无残留损伤 |
| `t0_rescue.py` | 重跑救件复制：`.runtime/quarantine/finalclean2_safety/inflight_20261010/` 788 件 mtime 刷到 23:39:21 | 同源同内容覆写（幂等），零灭失；未清理 |
| `t7_anchor_btier.py` | 重写 `t7_zmaster2_irreplaceable/` 3 件（23:39:28） | 同上幂等覆写 |
| `mk_closeout_block.py`／`mk_c_receipt_rows.py`／`t8_evidence.py`／`t9_forced_close_audit.py`／`annotate_owner_answers.py`／`wave2_rescue.py` | 生成块打到 stdout；`grep -rln "机生 2026-10-11 23:3" docs/_working/` **零命中** ⇒ docs/_working 台账正文未被改写 | 已实测排除对台账的污染 |
| `fourth_source_selfcheck.py`／`inject_token_bridge.py` | 只读打印（后者自陈 SKIP） | 无写 |

**另案免责实测**：`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` mtime 23:40:01 的改动 **非本班**——`git diff` 该文件零 `fclean3` 命中，其新增两条 creation_token 署名 `st-mineloop-20261010`／`st-dexp-20261009`（他班在飞写面，本班未碰）。

⇒ 波三复用铁律建议（判据口径未改，只是执行纪律）：**这 22 支一律「读源码＋按需 import 函数」，禁整支跑**；要跑须先看清有无 `--execute` 语义分界（`wave2_tmp_sweep.py`/`wave2_t3_restore.py` 有，`exec_c_*`/`t0_*`/`sweep_*` 没有）。

## 5. P5 收敛提案（只提案不立法）

5.1 **工具住 TTL 区的风险——精确化（工令原句需修正）**：现测 reconciler 的 `.runtime/tmp/` 24h purge 实现（`src/zephyr/governance/audit/reconciliation_registry.py:11191-11242`）用 `os.listdir(rt_tmp)` + **`if not os.path.isfile(full): continue`** ⇒ **只清根级散件，不进入目录子树**，故 `st-finalclean2-20261010/tools/` 不被这条 24h 腿扫走。真风险在三条旁腿：①整棵树 `.gitignored`（git 侧零保护，无第四态）；②`.runtime/tmp` 在 `scripts/ops_guard.py:104` 白名单内=**rmtree 可达不阻断**；③测试残留判定器 `_match_test_residue()`（:7619，真源=`trae_071 §test_residue_reclaim.covered_patterns`）按前缀删目录。⇒ 提案：波三/波四复用的尺与执行器应**收编进 `scripts/governance/finalclean/`（git 跟踪＋带 --execute 分界＋14 字段头）**，`.runtime/tmp` 版只作当轮工棚；净零口径＝收编即替代，不新建第二把尺。

5.2 **目录册冲突在册（本班写面即是一例）**：`docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml:456` 对 `.runtime/tmp/` 规定 allowed=[.ps1,.py,.sh,.txt,.log]、forbidden=[.md,.csv,.yaml,.json,.jsonl]；而波三工令明令「大表另存 `.runtime/tmp/<sid>/out/*.csv`」。现测该区已有 20 枚根级机读数据违此册（§3.2），且本班自身也落了 .csv/.json 于 `<sid>/out/`。因 `.runtime/` 整体 .gitignored、DCR-005/006/008 只在 force-add 时校验，**当下无门硬拦**，但口径确实互斥。⇒ 提案二选一并入册：要么把「机读大表」正式让位给 `.runtime/tmp/` 的 allowed 例外（改目录册一处，声明式），要么波三起大表一律落 `docs/_working/<campaign>/wave3/scan/`。本班不改判据，只登记矛盾。

## 6. 第四件判据复核（波二 §三 自罚申报的现测验证）

波二申报：「第四条判据『未被试验总账/在册裁定点名』**实测无机读读者**⇒判据空转」。本班复核结论＝**大体仍成立，但需一处精确修正**：
- `docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（317 行）现测 **`.runtime/tmp` 出现次数＝0** ⇒ 试验总账根本没有 tmp 路径字段，谈不上反查。✓ 佐证波二。
- `ruling_registry.yaml` 现测含 **19 处** `.runtime/tmp/...` 引用（如 `st-zchief8-20260928/defers/lane-dbr.md`、`st-deadcure2-20261009/common/lane_*.jsonl`、`ollama_upgrade/`），但全是裁定正文的散文引用，**无任何代码按 tmp 路径键查询**（grep 消费者：零）。⇒ 「被点名」无硬机读读者，波二「恒真」判断仍对。
- **精确修正**：存在一个**弱机读面**＝`REG-FMS-DEADREF-BASELINE`（`.../catalogs/fms_deadref_baseline.yaml`，ttl permanent，生成器 `scripts/governance/generators/generate_fms_deadref_baseline.py`，ratchet=monotonic_shrink），其 `entries:` 现册含 **3 条 `ref: .runtime/tmp/...`**（category B），由 FMS 死引用门以 **warn 不阻断＋存量豁免**模式消费（`gate_digest_registry.yaml:882`）。⇒ 第四件并非「零读者」，而是「**只有一个 warn 级棘轮读者，且它把 tmp 路径当死引用登记而非当活性护栏**」；判据仍无判力，波二自罚结论不改判，仅措辞需补此一条以免后人误以为「完全无人读」。

复算：`grep -c '\.runtime/tmp' docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（=0）；`grep -o '\.runtime/tmp[^ "_,)]*' docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | sort | uniq -c`（=19）；`grep -c 'ref: \.runtime/tmp/' docs/01_policies_and_standards/_registry/catalogs/fms_deadref_baseline.yaml`（=3）。

## 7. 被引用而有价值的目录清单（处置侧应「先救后清」，态②/态④候选，非删除候选）

| 目录 | 字节 | 引用次数/件数 | 三源 | 建议处置态（不裁） |
|---|---:|---|---|---|
| `st-cure-p05-20261006` | 877,856 | 1501/6 | 心跳 6844min exited | 态④（点名极密，先救后清） |
| `st-cure-p05b-20261006` | 35,891 | 1163/7 | 同上 | 态④ |
| `st-cure-p10-20261006` | 604,621 | 971/7 | 同上 | 态④ |
| `st-cure-p01-20261006` | 98,992 | 708/7 | 同上 | 态④ |
| `st-metaq-20260923` | 0（空目录） | 1342/344 | — | 态④（名在账而面已空，登记名实不符） |
| `st-cure-p09-20261006` | 13,677,600 | 348/5 | 心跳 4212min | 态④ |
| `st-tests-chief-20261004` | 510,205 | 285/16 | — | 态④ |
| `st-ailayer-final-20260924` | 1,087,903 | 283/108 | 三源零，静默 15.8d | **态② 先救后清**（A 12/105） |
| `st-t0-matrix-20260924` | 4,524,552 | 213/66 | 三源零，静默 17.3d | **态② 先救后清**（A 18/55） |
| `st-metaq-gc-20260924` | 11,964,432 | 211/46 | 静默 7.3d | 态④ |
| `st-deadcure2-20261009` | 18,909,968,480 | 49 | **T1 硬在飞** | 态④（六班相邻面，禁碰） |

## 8. 铁律自罚与判读纪律（本班动手面自查）

1. **在册误判防线**：`st-datalane-20261010`（在册六班·数据车道）心跳文件末行 `status=exited`、静默 1756min，**但** ①在册 ∧ ③进程表 6 枚命中 ⇒ 判活态④。这正是「心跳停更只证 daemon 死、不证会话死」的现行正证，本班未重犯。
2. **态①空集申报**：全集 1632 键里 **A∪B=100% 的整目录＝0 个**（实测 `dirs_100pct_A=[]`）。⇒ 波三在 `.runtime/tmp/` **不存在「整目录级 hash 铁证可删面」**；可证的冗余只在**文件级**（§9）。任何「按目录判死」的动议在本面都缺铁证，必须逐件。
3. 本班零删除、零 `git add`、零 commit；唯一 git ref 动作＝§4 事故复原（把误删分支加回，盘面回到动手前）。
4. `out/` 目录与同 sid 他车道共享（现测有 sibling 车道 `p1_census.json`/`quarantine_*` 产物），本班未覆写他人件。

## 9. 可清候选（含 A 类占比与铁证等级）＋剩余申报

铁证等级定义（本卷自定口径，不改判据）：**甲**＝逐件现测 sha256 等 HEAD（§2 抽样 14/14 成立）；**乙**＝旧档 `raw_equal=Y` 未逐件现测；**丙**＝仅 C1/引用级线索，不可判。

| 候选面 | 件数 | 字节 | A 占比 | 等级 | 处置框架 |
|---|---:|---:|---:|---|---|
| 文件级 A 类（全树，raw==HEAD） | 147,177 | 1,951,071,154（1.82 GiB） | 100%（定义即 A） | 乙（抽样 14 枚升甲） | 态① 逐件、**必经墓碑**（禁裸删）；不在 T1/六班会话的资产面上做 |
| └ 其中 T3（三源零＋静默>7d）内 | 75 | 650,621 | — | 甲样本取自此层 | 最干净的候批小面：仅 0.62 MiB，**不值得单开动刑面**，宜并入目录级处置 |
| └ 其中 T1 硬在飞内 | ~126,700 | 1,670,809,273（1.56 GiB） | — | 乙 | **态④禁碰**（属主活着，随其收尾序自清） |
| `pytest_<PID>` 测试残留（PID 已死） | 767 目录（227,230 件） | 25,680,095（24.5 MiB） | n/a | 丙（但 reconciler 已有在册判据：PID＋TTL 双保险） | 交 `trae_071 §test_residue_reclaim` 既有机制，**勿新造判据**；件数面 28.7% 是全树最大「件数」红利，字节红利极小 |
| 波二 §一 预筛面 | — | 0（已消失） | — | — | §3 已报：无需再批，改为**追溯存证是否闭合**一案 |
| C2 业务资产（Owner 门位，本班只登记） | 639,222 | **53,559,693,769（49.88 GiB）** | 0 | 丙 | Owner 门位；在册三档制口径（`00_ledger.md:600`）不变，本卷提供逐目录分解 CSV 供其点刀 |

**剩余申报（未跑完，禁拿抽样当全集）**：
① 全树 791,713 件**未做逐件现测 sha**，A 类现测复核仅 14 枚（等级已如实标乙）；② 波二后新增的 405 键（120 非 st＋其余散面）**无 HEAD 对拍基线**，全部停在态④；③ 非 st 面的「目录名被点名」普查已跑（1389 名，167 有名/1222 零引用，7 个 len<4 短名 `f7/p23/r2a/r2c/t1/t9/w15` 因噪声判据不足而单列排除）；④ 三源活性是 **23:24–23:31 一次快照**，波三执行班动手前必须**现扫重跑**（§0 复算三条命令），快照过期即失效；⑤ **`pc_cache` 一级目录 = 本班盲区**（`os.scandir` EACCES 拒绝访问，非 reparse point，件/字节读数 0），其归属/活性/构成全部未出，须以更高权限或属主车道复扫后补账——本卷全集对它**不完整**，禁据本卷对其处置。

## 10. 机读产物与复算命令（一页验尸刀）

| 产物 | 内容 | 生成命令 |
|---|---|---|
| `out/tmp_lanes_casefile.csv` | **1632 键全集**逐目录：现/基线字节件数、quiet、三源读数、引用数、A/B/C1/C2、态＋判语 | `python out/aggregate.py` |
| `out/tmp_top_entries.csv` | 1546 现扫一级条目（件/字节/mtime/扩展名 top5） | `python out/walk_tmp.py` |
| `out/tmp_hash_join.csv` | 波二旧档逐目录 A/B/C1/C2 重算 | `python out/join_hash.py` |
| `out/liveness.csv` | 150 st 车道三源逐源读数（含 reg_pid/held/reincarnation/hb_last/worktree） | `python out/liveness.py` |
| `out/sid_reference.csv`／`sid_reference_all.csv` | st 面／非 st 面 台账·裁定册点名普查 | `python out/refscan.py`；`python out/refscan_all.py` |
| `out/a_class_spotcheck.csv` | 14 枚 A 件 sha256↔HEAD blob 对拍 | `python out/spotcheck.py` |
| `out/tmp_path_readers.csv` | 「谁读 `.runtime/tmp/` 路径」普查（88 机读面＋12 md 面） | `python out/refscan.py` |
| `out/casefile_summary.json`／`proc_snapshot.csv` | 聚合读数／进程表原始快照（429 进程） | 同上 |

四态汇总表（st 现存 149 目录，按 §1 层归并）：

| 态 | 目录数 | 字节 | 说明 |
|---|---:|---:|---|
| 态④（在飞/受保护/被点名/无基线） | **127** | 51,613,255,025（48.07 GiB） | 含六班全部资产与 T1 全 11 目录 |
| 态④存疑（近 24h 有写等，默认留） | **10** | 13,041,708（12.4 MiB） | 同上，零动作记表 |
| 态②（三源零∧静默>7d∧零引用∧有增量面） | **12** | 9,283,730（8.85 MiB） | 全 C2（业务资产），属主零 ⇒ **Owner 门位，不判死** |
| 态①（整目录 100% hash 铁证） | **0** | 0 | §8.2 空集申报 |
| 态③（四元联言达判死级→墓碑） | **0** | 0 | 判据第四件无判力（§6），本班不自造 |
| 合计（＝现存量 st 车道全集） | **149** | **51,635,580,463（48.09 GiB）** | 复算 `python out/aggregate.py`（读数在 `casefile_summary.json`） |

一句话给统筹：**`.runtime/tmp/` 52 GB 的 94.3% 在 149 个 st 车道里，而这 149 个里没有一个是「整目录铁证可删」；铁证可删的东西只有 1.82 GiB 且 1.56 GiB 长在硬在飞车道内。真正的大面是 49.88 GiB 的 C2（Owner 门位）和 316,661 件/24.7 GiB 的「存疑无铁证」T4。工令里「预筛 10 目录候批」这一条已经不存在了——3.40 GiB 已消失且墓碑名查无，这是波三开工前该先问清的一件事。**
