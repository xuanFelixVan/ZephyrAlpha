---
ttl: task_bound
completes_when: "drift_* 全集字节三态判定（A/B/C1/C2）跑完或如实申报残余＋引用面与产出代码面均有 file:line 实测证据"
lane: lane_quarantine
session: st-fclean3-20261012
campaign: finalclean2_wave3
status: COMPLETE（判定全集 9388/9388，零抽样）
role: 只读调研车道——出案卷不出裁定；零删除、零 git add/commit、除本卷与 tmp 出件外零写面
---

# L 车道案卷：`.runtime/quarantine/` 分账 + drift_* 字节判据取证

> **口径声明**：本卷不另立判据。字节对拍原语 100% 复用波二"第二把尺"
> `D:/ZephyrAlpha/.runtime/tmp/st-finalclean2-20261010/tools/scan_dev_delta.py` 的
> `dev_blob_sha`/`disk_sha`/`norm_dev_sha`/`norm_disk_sha` 语义（行尾归一＝`\r\n`→`\n` 后 sha256），
> 落地实现见 `D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/tools/quarantine_byte_audit.py`。
> 桶：**A**=隔离件磁盘字节==dev blob 字节｜**B**=仅行尾归一后等｜**C1**=有同名 dev 件但字节不等｜
> **C2**=dev 查无同名件｜**X**=不可读（实测 0 枚）。
> §3 的"git 历史成员判定"是**口径外附注**（不改 A/B/C1/C2），仅供总包估"字节可否由 git 再生"。

## 0. 复算命令（可复制，全部实测过）

```bash
cd /d/ZephyrAlpha
# 0.1 分账
ls .runtime/quarantine | wc -l                 # 7482（测量期间 7481→7482，写入方在飞）
ls -d .runtime/quarantine/drift_*/ | wc -l      # 7427
find .runtime/quarantine -type f | wc -l        # 10299（drift 内 9388 + 非 drift 911）
du -sk .runtime/quarantine                      # 708120 KB（磁盘占用口径，非字节和）
# 0.2 字节三态全集判定（单进程＋8 线程；git show dev:<rel> 按 relpath 缓存；2000 件/批）
python .runtime/tmp/st-fclean3-20261012/tools/quarantine_byte_audit.py     # 40s
# 0.3 口径外附注：C1/C2 枚的字节是否在全仓任意 revision 出现过（含首控防空证词）
python .runtime/tmp/st-fclean3-20261012/tools/c1_history_membership.py     # 20s
# 0.4 产出/消费代码面
grep -rn "quarantine/drift\|_QUARANTINE_DIR\|known_quarantine" src/ scripts/ | head
```

机读出件（大表，csv/json）：
`D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/`
`quarantine_drift_byte_audit.csv`（9388 行逐件：drift_dir/relpath/bytes/bucket/q_sha256）·
`quarantine_drift_dir_class.csv`（7427 行逐目录：class/nfiles/bytes/buckets/rels）·
`quarantine_relpath_dedup.csv`（2574 行逐 relpath 去重账）·
`quarantine_audit_summary.yaml.json` · `quarantine_c1_git_history_membership.csv` ·
`quarantine_c1_hist_summary.yaml.json` · 运行日志 `audit_run.log` / `hist_check2.log`。

## 1. 分账实测 + 对总包 2026-10-11 23:2x 数的漂移申报

| 面 | 总包数（10-11 23:2x） | 本车道复测（10-11 23:2x–23:5x） | 差因 |
|---|---|---|---|
| 顶层项 | 7471 | **7482**（两次采样 7481→7482） | drift_* 在飞新增＋9；非 drift 项 55（总包估 "~53 patches＋零星"） |
| drift_* 目录 | 7418 | **7427** | 同上；命名 `drift_YYYYMMDDTHHMMSS` 严格匹配 7427/7427（`other_drift_items=[]`，无畸形命名 drift 件） |
| 文件总数 | 10,290 | **10,299**（drift 内 9,388＋非 drift 911） | 新增快照带文件 |
| 体积 | 684 MB | **700,794,449 B**（字节和；du 占用 708,120 KB） | 同上 |

**家族构成（实测，含工令 §1 差因申报）**：

- `drift_*` 目录 **7427 枚 / 679,859,943 B（占 97.0%）** ← 主体。
- `st-<sid>-retire-*.patch` **45 枚 / 7,230,406 B**（总包 "~53" 未复现；45 为 `*.patch` 实测计数）。
- 其余 **10 项 / 13,704,506 B**：`finalclean2_safety`（目录，839 文件 / 11,597,297 B）、
  `maint1_refresh_safety`（9/1,214,001）、`maint1_t2_safety`（5/551,446）、
  `maint1_t3_deliverable`（6/258,547）、`finalclean2_branch_sweep_20261010T125335Z.jsonl`（1/36,303）、
  `maint1_safety`（1/25,702）、`maint1_constland_safety`（2/16,750）、
  `dead_db_20261005`（1/1,716）、`branch_refs.log`（1,536 B）、`ahead_branches.log`（802 B）。
- ⚠ **工令 §1 预判的 `non_target_unstage` 族：目录不存在**（`ls -d .runtime/quarantine/non_target_unstage`
  → 空），且其留痕册 `.runtime/gate_audit/non_target_unstage.jsonl` 亦不存在；该族的锚定根仅作为常量声明在
  `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:4615`。**差因定论：本仓当前 drift_* 一家独大
  （97.0% 字节），`non_target_unstage` 族零存在（锚定代码在位但本窗口零产出）**——工令主体预判需据此改写。

### 1.1 在飞增速实测（同一次测量会话内三次采样，证写入方此刻仍在产出）

| 时刻（UTC） | 顶层项 | drift_* 枚 | 备注 |
|---|---|---|---|
| 20261011T152924Z 前 | 7481 | 7427 | 字节判定快照口径（本卷 §2/§3/§4 全部以 7,427 枚/9,388 件为准） |
| 20261011T153444Z | 7482 | 7427 | 顶层项 +1 |
| 20261011T153844Z | 7489 | 7434 | drift 枚 **+7 / 9.3 分钟**（≈45 枚/小时，突发式；最新 `drift_20261011T153444`） |

复算：`date -u +%Y%m%dT%H%M%SZ && ls .runtime/quarantine | wc -l && ls -d .runtime/quarantine/drift_*/ | wc -l`
（本车道连测三次，值即上表；非 drift 项恒 55 ⇒ 7434＋55=7489 自洽）。
⇒ **§2 的 9,388 件判定是 15:29Z 快照口径，其后新增的 7 枚未纳入判定**（如实申报，非抽样冒充全集：
判定对象全集=判定时刻存在的 7,427 枚，逐枚跑完，零残余）；态④ 建议对这些在飞枚零动作。

**按日分布（复测 vs 总包）**：10-01=103/32.3MB、10-02=802/88.6、10-03=554/36.1、10-04=1399/55.2、
10-05=856/77.0、10-06=458/47.8、10-07=1179/118.0、10-08=418/81.5、10-09=1007/55.5、10-10=601/56.5、
**10-11=50/31.4（总包 41，＋9）**。10-01…10-10 逐日枚数与总包**完全一致**；最早一枚
`drift_20261001T141656`、最新 `drift_20261011T152656`（UTC 命名）→ 家族窗口实测 10.0 天。
按 7427/10.0=**743 枚/天、67.7 MB/天** 外推，现行 retention（30 天）稳态≈**22,290 枚 / 2.03 GB**。

## 2. drift_* 字节三态判定（**全集 9,388/9,388 枚，零抽样、零残余**）

单进程＋8 线程、`git show dev:<rel>` 按 relpath 缓存（2,574 个唯一 relpath，仅 2,574 次 git 调用）、
5 批×2000 件、40.0s 跑完；未起任何并发 python 子进程跑 git（内存红线合规）。

| 桶 | 枚数（文件） | 字节 | 目录级含义 |
|---|---|---|---|
| A（磁盘字节==dev blob，纯冗余） | **450** | 10,953,802 | — |
| B（仅行尾归一后等） | **228** | 5,338,012 | — |
| C1（有同名 dev 件但字节不等＝独有历史字节） | **7,328** | **649,649,309** | — |
| C2（dev 查无同名件） | **1,382** | 13,918,820 | — |
| X（不可读） | 0 | 0 | — |
| 合计 | 9,388 | 679,859,943 | — |

**按 drift 目录聚合（判"整枚可清"的最小操作单元）**：

| 目录级类 | 枚数 | 内含文件 | 字节 |
|---|---|---|---|
| `REDUNDANT`（其内文件全落 A/B ⇒ 隔离零信息量） | **488**（6.6%） | 589 | **13,893,319（2.0%）** |
| `HAS_UNIQUE`（含 ≥1 枚 C1/C2 ⇒ 存独有字节） | **6,939**（93.4%） | 8,799 | 665,966,624（98.0%） |
| `EMPTY`（空壳） | **0** | 0 | 0 |

> 关键读数：**"看起来是垃圾"与"按字节是垃圾"差 50 倍**——488 枚可判纯冗余只值 13.9 MB（2.0%），
> 而 98.0% 字节（666 MB）载有与当前 dev 值不同的独有字节。任何按枚数比例（6.6%）折算的体积承诺都不成立。
> 附带：2026-09-14 案卷记载的"11843 目录中 10571 空壳"病理**今日已消失**（空壳实测 0，
> 系 `_snapshot` P2-2 修复"先验源再建目录"的效果，`worktree_drift_watchdog.py:443-462`）。

## 3. 口径外附注：C1/C2 独有字节能否由 git 历史再生（全集 8,710 枚，含首控）

方法：`git -c core.abbrev=40 log --format= --raw --all` 一次通扫全 ref，收集历史 blob sha1 全集
（实测 raw_lines=458,527、**distinct_blobs=332,514**），逐枚算 git-blob sha1（raw＋`\r\n`→`\n` 两把）判成员。
**首控（防空证词）**：`src/zephyr/shared/io/file_utils.py` 的 dev 现值 blob 必须落在集合内——实测 True。
（本车道第一版实现因 `core.abbrev` 把 sha 缩到 11 位而集合恒空、误出"全 NOT_in_history"假结论；
首控暴露后已修正重跑，旧出件作废——在册教训"判'已防护'要测'谁调它'"的直接复现。）

| 附注桶 | 枚数 | 字节 | 语义 |
|---|---|---|---|
| `C1/NOT_in_any_git_revision` | 6,886 | 575,175,126 | dev 有同名件、字节异、且全仓任意 revision 从未出现此字节 |
| `C1/in_git_history_raw` | 293 | 65,093,255 | 字节可由 git 历史某 revision 重新导出 |
| `C1/in_git_history_eolnorm_only` | 149 | 9,380,928 | 仅归一后可导出 |
| `C2/NOT_in_any_git_revision` | 995 | 10,632,342 | dev 无同名件且历史无此字节 |
| `C2/in_git_history_raw`／`_eolnorm_only` | 382／5 | 3,176,247／110,231 | 路径已不在 dev，但字节在历史某处 |

**净结论**：C1+C2 合计 663.6 MB 中，**585.8 MB（88.3%）是"git 也再生不出"的真·独有字节**；
仅 77.8 MB（11.7%）可自 git 历史重新导出。
独有字节集中面极窄：`2,001` 个 relpath 含独有字节，但前 2 个就占 65%——
`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`
（73 枚独有 / **270,543,036 B**）＋
`docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`
（31 枚独有 / **112,240,597 B**）；再次要 `data/strategy_intake/lane_f_candidates.csv`（3 枚 / 29,033,709 B）、
`scripts/governance/oneoff/data_domain_audit_report_db.md`（6/7,720,790）、
`architecture_issue_registry.yaml`（5/8,353,968）。

**这两册的定性关键证据（实测，不改判据）**：隔离件文件头第一行＝
`<!-- GENERATED FILE — regenerate: python scripts/governance/registry_projection/registry_projection_generator.py --render --registry-id REG-CAPCAN-0… -->`；
dev 现值 4,100,821 B vs 80 枚快照 3,340,471–4,128,807 B（同形制、不同发布态整册重打）。
→ 这 382.8 MB 独有字节**极可能是 PG 账本投影的"陈旧已发布态"，而非人写工作成果**；
能否逐枚重导，取决于 `registry_snapshot` 表的历史版本可读性——该表**确有版本轴**
（`schemas/categories/registry_ledger/registry_snapshot.py:26-37`：`snapshot_version`、
`parent_snapshot_version`、`uq_registry_snapshot UNIQUE (registry_id, snapshot_version)`），
但消费侧只取最新发布态——`src/zephyr/governance/registry_projection/pg_source.py:45`
`__all__ = ["ProjectionUnavailable", "load_latest_snapshot", "snapshot_from_bundle"]`
（:19 注释自陈"生成器是 registry_snapshot 的只读消费方"）。
**逐枚重导需跑 render（写面），本车道只读未测 → 待总包裁/另开取证道**。

## 4. 同域去重收敛潜力（实测，全集非抽样）

| 指标 | 实测值 |
|---|---|
| drift 内唯一 relpath | 2,574 |
| 被隔离 ≥2 次的 relpath | **1,217**（覆盖 8,031 枚，占全集 85.5%） |
| 全等重复 relpath（≥2 枚且字节全同） | **440**（883 枚） |
| 不同字节态 (relpath × sha256) | **5,686** |
| **可删重复枚数**（同 relpath 同字节态仅保 1） | **3,702 枚（占 39.4%）** |
| **可省字节**（同口径） | **100,122,551 B ≈ 100.1 MB（占 14.7%）** |
| 收敛后残留 | 5,686 枚 / 579,737,392 B |

单 relpath 最大重复面（字节账）：`capability_canonical_file_registry.yaml` 80 枚 / 296,509,459 B，
其中 75 个不同字节态 ⇒ 仅 5 枚是逐字节重复 ⇒ 可省 19,413,432 B；
`module_translation_registry.yaml` 35 枚 / 126,619,314 B，31 态 ⇒ 可省 14,290,942 B。
**⇒ 去重是"枚数收敛"利器（−39.4% 枚），但不是体积利器（−14.7% 字节）**；
体积主杠杆只剩"期限制/压缩/独有字节是否可再生"三条，均归总包裁。

## 5. 引用检查（判死前置；命中面已核存在性）

点名 drift_* 具体名/路径的台账、裁定册、案卷（`grep -rn "drift_2026\d{4}T\d{6}|quarantine/drift_" docs/ src/`）：

| 引用位点（file:line） | 点名对象 | 该存证今在否（实测） |
|---|---|---|
| `D:/ZephyrAlpha/docs/_working/archive/2026-10/t0_matrix/LEDGER.md:405` | `drift_20260923T193551` | **否** |
| `D:/ZephyrAlpha/docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources/death_cases_registry.yaml:163` | `.runtime/quarantine/drift_20260923T*` | **否** |
| `D:/ZephyrAlpha/docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md:1356` | `drift_20260923T*` | **否** |
| `D:/ZephyrAlpha/docs/_working/archive/2026-09/reports/2026-09-02-freeze-window-completion-report.md:44` | `drift_20260902T*` | **否** |
| `D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/10_evaporation_forensics.md:26,29`（同名件亦存 `decision_map_campaign/`） | `drift_20260923T194105`、`drift_20260923T194121`、`drift_20260924T042550…` | **否** |
| `D:/ZephyrAlpha/docs/03_modules/_domain_frontend/frontend_handbook/project_conventions.md:222` | `drift_20260908T143802`（曾据此移植 chainmap 段） | **否** |
| `D:/ZephyrAlpha/docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/EV_root_cause_and_cure.md:24` | `drift_<ts>` 命名＝UTC 口径 | 语义引用（不依赖实体） |
| `D:/ZephyrAlpha/docs/_working/master_tc_night/lanes/L0_channel/00_workbook.md:21` | `.runtime/gate_audit/registry_drift_20261007T…diff`（投影漂移探针证据） | 另一族（非本次判据对象） |
| `D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_085_stale_base_overwrite.yaml:77,121,132` | watchdog 为该规则的检测面 | 制度引用（不点名实体枚） |
| `D:/ZephyrAlpha/docs/_working/archive/2026-09/implementation_plans/02_design_asset_inventory.md:462` | `drift_*` 多份快照（Q7，"待裁定"） | 通指 |

**读法结论**：现存台账点名的都是 **2026-09 及更早**的快照，而现存家族最早为 `drift_20261001T141656` ⇒
**今日 7,427 枚（判定快照口径；复测已至 7,434，见 §1.1）无一名被台账/裁定册点名**
（`ls .runtime/quarantine | grep -c '^drift_202609'` = **0**，即 9 月枚全部不在；
`drift_20260902T*`/`drift_20260908T143802`/`drift_20260923T193551`/`drift_20260923T194105`/
`drift_20260923T194121`/`drift_20260924T042550` 逐一实测=0）。反向风险成立：**这批字节一旦被清，未来再有点名即成空引用**
（本案卷的 §5 即为此预留的引用锚）。裁定册精确核 `grep -cE "drift_2026[0-9]{4}T[0-9]{6}"`：
`D:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 点名具体枚 **0 行**
（该册另有 4 行含 "quarantine"／"drift" 字样，均为泛词——"retroactive quarantine"、守护名
`worktree_drift_watchdog` 等，不指任何快照实体）；`_registry/catalogs/` 全目录点名具体枚 **0 册**；
`docs/_working/` 点名具体 `drift_<ts>` 枚的文件 **5 件**（即上表所列，全部指向已不存在的 9 月存证）。

## 6. 谁在写 / 谁在读（实测 file:line，非推测）

**写（产出 drift_*）**：
- `src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py:443-462`
  `_snapshot()` → `root / _QUARANTINE_DIR / f"drift_{ts}" / rel`（:452；ts 为 UTC `%Y%m%dT%H%M%S`，:451）；
  `_QUARANTINE_DIR = ".runtime/quarantine"`（:97）、`GATE_ID = "GATE-WORKTREE-DRIFT-WATCHDOG"`（:89）。
- 触发面：`scan_once()`（:1029）由常驻守护 `run_daemon()`（:1423）按 `_SCAN_INTERVAL` 周期调用。
- **在飞实证**：计划任务 `ZephyrAlpha_WorktreeDriftWatchdog` State=Running（`Get-ScheduledTask -TaskName '*rift*'`），
  注册脚本 `scripts/tasks/register/register_drift_watchdog_task.ps1:58`；
  进程面 `Get-CimInstance Win32_Process` 命中 `*worktree_drift_watchdog*`（PID 6148 起于 2026/10/5 16:05）；
  白名单 `src/zephyr/trading/process_reaper.py:226`（reaper 豁免，boot 永久服务）；
  仪表盘探活 `src/zephyr/frontend/dashboard/services_registry.py:283`。
  本车道测量期间顶层项 7481→7482 ⇒ **写入方此刻仍在产出**（态④适用最新若干枚）。

**读/清（消费 drift_*）**：
- 同模块自管 retention：`worktree_drift_watchdog.py:509-570` `_sweep_quarantine()`
  （`_QUARANTINE_RETENTION_DAYS = 30`，:98；只碰 `drift_<ts>` 规范命名，命名不符 :533-536 记 kept 豁免；
  空壳宽限清理 :543-544；删除唯一经 `safe_rmtree(d, allowed_prefix=qdir)` :554；逐条审计 :558-567）。
  日级节流入口 `_maybe_sweep_quarantine()`（:573-588，state `quarantine_last_sweep` 同日只跑一次）。
- 带外删除告警：`known_quarantine` 登记（上限 `_KNOWN_QUARANTINE_CAP = 500`，:103）＋
  `quarantine_tamper` 判定；测试面 `tests/gov/governance/rule_bridge/test_worktree_drift_watchdog.py:334-345,397-417`。
- 审计取证引用：`scripts/governance/evaporation_blackbox.py:349`（"对照 .runtime/quarantine/ 漂移存证"）；
  sha 取证的审计侧 `_quarantine_content_sha()`（watchdog :432-440，`sha256:` 前 16 位入 jsonl）。
- 删除保护：`scripts/ops_guard.py:92-99` 把 `.runtime/quarantine` 列入**保护区**，
  注释实证原因："2026-08-25/26 两起带外裸删（drift_* 选择性清除、零审计）"⇒ 人工处置须走
  `ZEPHYR_FORCE_DELETE=1`，本家清扫须走 `safe_rmtree` 授权通道。
- 写审计豁免（避免自激）：`src/zephyr/gov_enforcement/rule_bridge/write_audit_daemon.py:84`
  `(".runtime/quarantine", True)`。
- 非 drift 族的产出方（顺带定位，供分账归口）：`scripts/session_worktree.py:541-558`
  写 `branch_refs.log`（分支 tip SHA 存证）、`:732` `_AHEAD_LEDGER = .runtime/quarantine/ahead_branches.log`；
  retire patch 落该目录由 `tests/gov/git/test_session_worktree.py:2578` 断言（`patch_path.parent.name == "quarantine"`）。
- 另有独立同名不同根件（**勿混**）：`src/zephyr/data/quarantine_manifest.py:74` 的
  `DEFAULT_QUARANTINE_DIR = data/local_fallback_quarantine`，与本目录无关。

**retention 现状实测（防误判"清扫坏了"）**：`.runtime/audit/worktree_drift_watchdog.jsonl`
中 `quarantine_retention_sweep` 记录 **0 条**。现存最早枚为 2026-10-01，而 cutoff=now−30d=2026-09-11 ⇒
**今日无任何枚到期，0 清除是与政策一致的期望行为，不是故障**；
同时 2026-09 及更早枚已全部不在（§5 实测=0），说明到期后的清理链路此前确实生效过
（历史段证据在轮转件 `.runtime/audit/worktree_drift_watchdog.jsonl.1`，本车道未逐行核——**待总包裁**是否补证）。
⇒ 结构性后果：**"743 枚/天 × 30 天"稳态≈2.0 GB，retention 政策本身不构成体积上限**。

## 7. 四态框架处置建议（仅建议，裁定归总包；禁裸删）

| 态 | 对象（实测数） | 铁证 | 建议动作 |
|---|---|---|---|
| **态①** 纯冗余可删 | drift 目录级 `REDUNDANT` **488 枚 / 13,893,319 B**（其内文件 100% 落 A/B 桶，即与当前 dev 值逐字节等或仅行尾异）；另 C1/C2 中 `in_git_history_raw/_eolnorm_only` 共 **829 枚 / 77,760,661 B** 可由 git 历史重导 | `quarantine_drift_dir_class.csv`（class=REDUNDANT 行）＋`quarantine_c1_git_history_membership.csv`（hist_check≠NOT_in_*） | 建议走 watchdog 本家授权通道（`safe_rmtree`＋逐条审计）**提前收**，或并入去重批次；不建议人工裸删（ops_guard 保护区） |
| **态②** 有增量 | `HAS_UNIQUE` **6,939 枚 / 665,966,624 B**；其中 **585.8 MB 为 git 也再生不出的独有字节** | §2 §3 表＋`quarantine_drift_byte_audit.csv` | 建议：①同 relpath 同字节态去重（−3,702 枚/−100.1 MB）；②剩余按 relpath 打包压缩归档＋期限制（gzip 对 3.7MB 级 YAML 整册重打预期数量级压缩，**本车道未实测压缩率，不承诺数字**）；③两册 GENERATED 投影件（382.8 MB）单独成子案，待"能否由 PG `snapshot_version` 重导"取证后再判 |
| **态③** 判死→墓碑制 | 本车道**不指认任何一枚为死**（无一枚满足"零触发零消费"：写入方此刻在飞、消费方=retention/tamper/黑匣子在册） | §6 在飞实证（PID 6148＋任务 Running＋测量期计数 7481→7482） | 无建议；若总包判死，须按根宪法 §5.2 墓碑制（30 天复活窗）且走 `ZEPHYR_FORCE_DELETE=1`/授权通道 |
| **态④** 在飞/存疑→零动作记表 | 测量窗口内 mtime 最新的 **9 枚**（10-11 增量 50−41，其中新增于总包测后）＋全部 UTC 命名合规枚 | 0.1 命令两次采样差 | 零动作，记表；下轮复测再判 |

**明确申报未做/不做**：未跑 render 重导验证（写面）；未测压缩率；未查 PG `registry_snapshot` 历史行可读性
（需 DB 只读查询，涉 DatabaseService 单口，本车道未起）；未对 `.jsonl.1` 轮转审计段逐行核；
未动任何删除/git 操作。

## 8. 待总包裁清单（本车道不自裁）

1. `HAS_UNIQUE` 666 MB 的独有字节里， GENERATED 投影件（两册 382.8 MB，占独有字节 65%）究竟算
   "有取证价值的历史字节"还是"可重导的机器噪声"——取决于是否开一条允许跑 `registry_projection_generator.py
   --render`（写面）的取证道。
2. 30 天 retention 是否需按实测增速（743 枚/67.7 MB 每天）改判为"字节预算制"或"relpath×态 去重后保留"。
3. 488 枚态①与 829 枚可自 git 重导枚，是否并入本波清扫批次（须走 watchdog 授权通道以保审计连续）。
4. `st-*-retire-*.patch` 45 枚（7.2 MB）与 `*_safety` 5 目录（13.7 MB）归属非本车道判据范围，仅分账陈报。
