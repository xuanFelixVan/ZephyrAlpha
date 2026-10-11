---
ttl: task_bound
completes_when: 三机械面逐件证据齐且执行有批前后对账；归档器影子 7 天零异常经统筹签认；aidrafts/quarantine/untracked/gate_audit/audit 五面案卷过统筹目
gate_selfdoc: GIT-DANGEROUS
---
# 终清波三·第二袋（sid=st-fclean3-20261012）＝三机械面执行＋归档器影子点火＋五面案卷汇总裁决

> 统筹裁定（2026-10-12 01:0x，AskUserQuestion 回执全文存 `.runtime/tmp/st-fclean3-20261012/`会话面）：
> **菜单一＝C 案卷先行**（"本班自己两起未遂＋最大的面比工令大四个数量级——案卷过我一眼再动刀，是这个量级面的纪律"）；
> **例外授权**＝"69 空壳目录＋22 散件＋嵌套 `.runtime` 这三个机械面可随案卷袋附逐件证据后先行清"；
> **菜单二＝A 影子点火 7 天**（护栏：影子期只判只记；每轮点名清单与在飞三源交叉核，命中在飞即告警；7 天零异常＋统筹签认后才转真 mv；计划任务注册随转正一并定）。
> 更正纪律照 Owner 追认执行：**更正另起一节、旧案卷原样留着**（见 §2、§7，不改写 `21_wave3_p1_firstbag.md` 与四条车道案卷正文）。

## 一、三机械面：逐件证据与执行回执

证据器＝`.runtime/tmp/st-fclean3-20261012/tools/p2_mechanical.py`（只读；机生 JSON＝同目录 `out/p2_mechanical.json` @01:31:05，存活进程 cmdline 33 行）。
**判可清的合取条件**（任一不满足即态④留，不留情面）：`零文件 ∧ 无存活进程句柄落在其内 ∧ 不被 reaper keep 点名 ∧ 代码面（src/scripts/config）读者 grep＝0`。
⚑ 句柄前置是 24968 误杀教训的落地：剪任何路径前先验句柄是否在被剪路径上；进程表探不到（`probe=err`）时**一律判不可清，禁 fail-open**。

| 面 | 实测 | 判可清 | 态④留 | 留的原因（实测列） |
|---|---:|---:|---:|---|
| S1 零文件空壳目录 | 42（P1 时 43，其间有漂移） | **24** | 18 | 全部因"代码面读者 grep＞0"（多为 4 命中）⇒ 属**按需 mkdir 的在册面**，剪掉可能让写者静默失败，非零风险 |
| S2 "仅有目录无文件"树 | 26 | **22** | 4 | `construction_20260825/industry_graph/recycle_bin/pytest_cache` 读者＞0，其中 `pytest_cache` 还被 reaper keep 点名 |
| S3 `.runtime` 根散件 | 22 | **0** | 22 | 见下逐件裁决——14 件是在飞状态/锁/缓存（mtime 0.02–0.12 天），8 件虽零读者但**无写者**＝不可证"机器可再生"，判呈批不判删 |
| S4 嵌套 `.runtime/.runtime` | 3 件 | **0** | 3 | ⚑ 被内容级实测**反转**，见 §2 |

**执行回执**（真删只落 S1＋S2＝46 个零文件目录）：清单 sha256 **`0b0cae988df22cca4767662b0f01a1e882a7ababb6b03ec8868fc42008065f7a`**；
手法＝**自底向上 `os.rmdir`**（非 `rmtree`、非 shell `rm -rf`：空目录语义下"非空即失败"，构造上不可能吞内容；并避开在册的 POSIX `rm` 护栏盲区事故）；
删除前逐件再验一次 `rglob` 文件数＝0（防 TOCTOU）；结果 **deleted=46 / failed=0 / 处置后仍存在=0**；凭据＝`out/p2_delete_receipt.json`。

### S3 逐件裁决（22 件，本轮零删除，理由逐条）
- **在飞状态/锁/缓存（14 件，态④）**：`backup.lock`(49B, q=0.02d, 读者4)、`reconcile_launch.lock`(0B, q=5.95d, 读者1)、`*_last_attempt` 三枚(17B 各, q=0.03d)、`depgraph_scan_cache.json`(**11.2MB**, q=0.03d, 读者4)、`depgraph_di_seam_cache.json`(1.3MB, 读者2)、`git_performance_log.jsonl`(485KB, 读者4)、`worktree_ops_log.jsonl`(3.7MB, q=0.0d, 读者4)、`session_registry.json`(2.1KB, 读者4＝**即 P1 §五-3 的滞后兼容副本本体**，删它会把兼容读路径打断)、`task_board.db`(176KB, 读者4)、`pg_probe_state.json`、`reconciler_health_warn_dedup.json`、`archive_watchlist.json`。
- **零读者但无写者⇒不可证可再生（5 件，判呈批）**：`algoflow_progress.jsonl`(166KB, q=41.8d)、`algoflow_skipped.jsonl`(5KB)、`predictions_v1_backup_1971.jsonl`(396KB, q=47.5d，**1971 年份异常且 grep 零写者**——车道已申报"bug 还是哨兵证据不足，不臆断"，本班附议：无写者的数据文件不属"机器可再生产物"，故不落态①)、`board_idx_offset.txt`(7B, q=0.67d 太新)、`workspace_drift_warn.jsonl`(761KB, 读者3)。
- **⚑ 有独有字节（1 件，禁删并已在处置前存证）**：`takeover_ledger.jsonl.tmp.23876` → §2。
  存证 sha256 前缀：tmp＝`5dcd7d668f897351`、嵌套 heartbeat＝`ad0fa2866c179a8f`、嵌套 pid＝`56d74fda8f7ae2cf`（三份均落 `out/preserved_*`）。

## 二、⚑ 两处"看着像垃圾、实测是唯一证据"的反转（另起一节，不改 P1 结论）

1. **`takeover_ledger.jsonl.tmp.23876`（326,345 B）＝75 条死亡取证记录的唯一存活处**。逐行对拍主表 `takeover_ledger.jsonl`（169 行）：tmp 共 91 行，其中 **75 行在主表零命中**（时刻 2026-10-06 15:20Z ～ 10-07 20:17Z，样例 sid `st-cure-p09-20261006`／`st-vm12r2-20261007`）。⇒ 这是原子写（tmp+`os.replace`）中断留下的**前像超集**，不是残渣。按四态属**态②（有增量→先救后清）**，本班已存证、未删主表也未动 tmp。**升级呈报**：主表比 tmp 少 75 条 ⇒ "会话死亡台账"面存在**历史缺口**，归因（谁在何时以整表重写覆盖了追加面）不在本班权限，移交维护面（§7 T7）。
2. **嵌套 `.runtime/.runtime` 不是残缺重复，含 1 件唯一存活面**：`sessions/st-deadcure-20261009/heartbeat.jsonl`(210B) 的**正主路径不存在**；`locks/heartbeat_st-deadcure-20261009.pid` nested＝`29384` 且 mtime(1791491858) **新于**正主 `27948`(1791488753)；第三件 `sessions/st-gateaudit-20260922/heartbeat.jsonl`(364B) 才是正主(45,112B，末行 `exited reason="session not in registry"`)的早期前缀。⇒ P1 §一里"内容为残缺非重复"的登记**方向正确但结论要收紧**：这面**整体态④**，正解是修"相对路径写盘"这个根因（车道已申报精确 file:line 未钉死），不是剪面。

## 三、归档器影子点火·第一轮（统筹菜单 A，护栏全中）

`python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json` @`2026-10-11T17:31:05Z`（机生存证 `out/shadow_round1.json`）：

| 项 | 实测 |
|---|---|
| mode | **shadow**（只判只记，零 mv）✓ |
| scanned | 466 |
| would_level2_archive 点名（confirmed） | **288** |
| suspected / merge_warned / errors | 0 / 0 / **0** |
| skipped | 一组 `orphan_keep` 豁免（例 `AI-PROBE-001` age=545612s≈6.3d、`st-acure-*` age≈345k s）⇒ 白名单面在起作用，非空转 |
| ⚑ 与在飞三源交叉核 | **命中＝0**（点名集 ∩ `list_active_readonly()` 全部在册会话＝∅；今晚六班∪本班九支 sid ∩ 点名集＝∅）⇒ 本轮无告警 |
| 与 P1 手工口径的差 | 手工"孤儿 465／过 7 天门 268"vs 归档器 288：⚠ **以归档器自身口径为准**（它的 age 规则≠我的 max-mtime>7d 代理）；差 20 枚登记为口径差因，不硬合 |
| `--help` 目录 | 出现在点名集里＝P1 记的"疑似误建垃圾目录"被机制正式认孤 |

**影子期节奏**（照裁定）：每日至少一轮，逐轮存 `shadow_roundN.json`＋三源交叉核结果；**7 天零异常＋统筹签认**才转真 mv；**计划任务注册随转正一并定，影子期不注册**。

## 四、aidrafts 面（车道 `lane_aidrafts.md` 441 行）汇总裁决

1. ⚑ **结构性前置成立且是好消息**：递归 327,702 节点 **reparse point＝0**（波二 `st-mastertc-l8` 断链 JUNCTION 陷阱在本面不存在）；**但每目录 `.git` 是 gitfile→`.git/worktrees/<sid>`，`git worktree list` 实测 16 棵全部是主仓注册工作树**，各挂 `session/<sid>` 分支 ⇒ **`rm -rf` 会留孤儿管理面，真实丢失路径在后续 `prune`＋分支清扫**。裁决：本面任何后续处置**必须走 `git worktree remove`**，禁裸删目录。
2. 全集四态（**非抽样**，参照 HEAD `4ac4a602e2`，每目录守恒校验 true）：A 319,233 件/4,499.0 MiB｜B 70/2.2｜C1 3,587/184.0（其中 lag 3,561/175.2、**unique 仅 26/8.8**）｜C2 4,796/53.0 MiB。**冗余(A+B+C1_lag)＝4,676.4 MiB＝98.7%**；与主仓硬链接共享 0.0 MiB ⇒ apparent 即实占。
3. C2 的 53.0 MiB 里 **44.91 MiB 是 `.pyc`/`.ruff_cache`、7.98 MiB 是车道本地 `.runtime`** ⇒ **真不可再生仅 25 件/0.11 MiB**，含唯一"只活在车道"的交付件 `regsolo_campaign/99_delivery.md`＋`lanes/t1–t4.md`（67.8 KB，主仓查无同名）。裁决：`regsolo` 判**态②先救后清**（E3），25 件走正门存证后再谈面处置；`deadcure3/backfix-patrol/nightmine2` 三支三窗全静判**态③候选**但**证据级 E1/E2**，本班不自签。
4. ⚑⚑ **密钥告警（非本班权限，立即上报）**：`regsolo` 面 `config/.env.clickhouse|.postgres` 与主仓 **sha256 全等且 git 未跟踪**＝**第二份未纳管明文密钥副本**。违 RULE-SECRETS（密钥走 secrets.py，禁裸明文复制）。本班**只登记不呈删**（删除密钥载体属物理不可逆面，Owner 门位）。
5. 净零：`.worktrees` 6 员 vs `.aidrafts` 16 员，同名交集仅 2 且**分支/HEAD 不同**（本班 86f4c5ba6d vs 主区 ccf6d852cc）⇒ 工令设想的"同字节双存合并"**证伪，重复量＝0**；真问题是**同一会话被两套工法各开一棵树**（每轮净增 ≈297 MiB/20,540 件）。根因收敛＝**停发第二棵树**，真源定 `.worktrees`+`ai/*`，`.aidrafts` 走退役（前置三件：worktree remove／ahead>0 分支解绑（实测 `deadcure2`=2、`mineloop`=1）／25 件先存证）。

## 五、untracked＋gate_audit＋audit 面（车道 `lane_untracked_audit.md` 437 行）汇总裁决

1. 未跟踪面（口径先定：`.gitignore:265`=`/*` 根白名单⇒ 带/不带 `-uall` 两个数都"对"但后者漏判）：A 2 件｜**C2 658 件/667.09 MiB（其中 `data/` 449 件/752.48 MiB＝Owner 门位）**｜在飞留置 **353 件/415.44 MiB**（三件定窗：15 会话心跳 0.1–0.4min ∧ psutil 16 sid 令牌 ∧ mtime≤3d）｜**第六态 88 件 sha 实证同字节副本**（79 枚在 `quarantine/finalclean2_safety/inflight_20261010`，`tests/gov/**` 复活面）＋28 件同名不同容（弱信号）。
   ⚑ `scripts/tasks/{run,register}/*.ps1` 同时呈 `D `＋`??`＝**他会话已在共享 index 暂存删、盘上仍在**（09-27 事故同型微缩版）⇒ 按 §3 第 4 条**不代修**，已在册移交。另 5 枚 `factory_grid_executor.py.tmp.21772.*` 原子写残留＝热文件 CAS 失败信号，转维护面。
2. `gate_audit`/`audit`：读者实测只有 `commit_gateway_abuse_monitor_reconciler.py:488/:493-494/:502`，**全量逐行读、时间窗在内存里（`since_7d` 于 :749，调用位 :773）**⇒ 轮转段 `.1/.2/.3` **对读者已零可见**＝可归档的实测依据（这条正是"必须自己读到取值行才敢定性"的落地）。
3. ⚑ **真风险不是体积是取证窗侵蚀**：外推 `gate_audit` 净增 30d≈2.3–2.6 GiB／90d≈4.5–5.0 GiB（族上限 200 MiB，`audit_jsonl_writer.py:59-62`），而 `ops_guard_delete` 面只保 **~3.7 日**、`feature_flags` ~**0.7 日**——即出事时翻不到当时的审计行。裁决：方案优先级＝**先扩取证窗，再谈缩容**（只动带 `.<N>` 段∧静默>30d，`retention.py:46`；cp→F:/zephyr_cold/50_archive＋`drawers.jsonl` 台账＋G 侧第二验证副本→**Owner 批文**→才删源；禁动 `obj_s_ai_exposure_forbidden.jsonl` 与 `create_guard_keyword_dup_warn.jsonl` 前 50 行，后者被 `test_create_guard_token_sim_shadow.py:174-179` 锚定）。
4. 待 Owner 定档 **8 条**（逐出处见案卷 §4），其中 **S4-B 影子册"一周后 Owner 门位定档"已逾期 4 日**（首记录 10-01／末 10-10，`create_guard.py:8`）＝本班**未自判退役**。

## 六、quarantine 面归档与期限制方案（本班总裁，供统筹过目）

数据底座＝车道 `lane_quarantine.md`（全集判定跑完，零抽样零残余）：A 450 枚/10.95MB｜B 228/5.34MB｜C1 7,328/649.65MB｜C2 1,382/13.92MB；目录级 **REDUNDANT 488 枚/13.89MB＝仅占 2.0% 字节**，HAS_UNIQUE 6,939 枚/665.97MB；同内容重复可去 **3,702 枚（−39.4% 枚数）但只省 14.7% 字节**。写者＝`worktree_drift_watchdog.py:452 _snapshot()`，**自带 30 天 retention**（`:509-570`），稳态外推 **2.03 GB/22,290 枚**。现存枚**零名被台账/裁定点名**。

| # | 处置 | 对象与判据 | 动作边界 |
|---|---|---|---|
| Q1 | 短期即清（铁证态①） | REDUNDANT 488 枚（其内全部件字节==HEAD） | 保留窗从 30d 降到 **7d**：这些枚对读者零信息量，留 30d 只是占审计面；**仍由 watchdog 自己清**，不外力剪 |
| Q2 | 内容寻址去重 | 3,702 枚同 sha 重复 | 归档＝按 sha 存一份＋逐枚清单台账（收益在**枚数/目录项**不在字节，如实标价 −14.7%）；禁按目录名裸删 |
| Q3 | **待裁（车道留问①）** | GENERATED 投影件独有字节 **382.8MB＝占独有面 65%**（`capability_canonical` 270.5MB＋`module_translation` 112.2MB） | 定性取决于"投影可重导⇒算噪声"还是"漂移前像⇒算取证"。**本班不自裁**：证它需要先跑 `--render`（写面）＋查 PG `registry_snapshot.snapshot_version` 历史行，两者都越出本班只读权限；建议交册主车道出证 |
| Q4 | 字节预算制（车道留问②） | 30d retention 是按时间不是按体积 | 若采字节预算：上限建议 **1 GB**，超限按 sha 去重→再按龄清 REDUNDANT；改判据属门禁面，**呈批不自改** |
| Q5 | 禁裸删总则 | 两面（quarantine/retire patch）都是防连坐审计面 | 一切处置＝归档/压缩/期限制，且与波二 E 墓碑体系同型留 INDEX＋rollback |

## 七、呈批与移交（本班一律不代裁；累计清单）

| # | 件 | 事实与凭据 | 归属 |
|---|---|---|---|
| T2/T3/T4/T6 | only-copy 死信 1,425 袋/2.61GB、tmp C2 业务资产 49.88 GiB、波二 C 件授权原话未验、陈旧索引面归维护三班 | 见 P1 §四/§七 | 沿用，未重复呈报 |
| **T7** | ⚑ `takeover_ledger.jsonl` 主表比 tmp 前像**少 75 条**死亡取证记录 | §2-1 逐行对拍（169 vs 91/75 独有），存证 sha `5dcd7d66…` | 维护面（会话死亡台账完整性） |
| **T8** | ⚑ `.aidrafts/st-regsolo-20261010/config/.env.{clickhouse,postgres}` ＝**与主仓 sha256 全等的第二份未纳管明文密钥** | 车道实测，git 未跟踪 | **Owner 门位**（密钥载体物理处置属不可逆面）；RULE-SECRETS 违面 |
| **T9** | 4 条悬挂 creation_token（我改名 `L_*→lane_*` 留下的未落地路径条目） | 坐标见 P1 §六 | 统筹已批"转维护三班走有权道"，本班未自 retire（缺 `authority_ref`） |
| **T10** | aidrafts 面 25 件真不可再生字节（含 `regsolo_campaign/99_delivery.md`＋`lanes/t1–t4.md` 67.8KB 主仓查无同名） | 车道四态表，参照 HEAD `4ac4a602e2` | 本班当班先存证后走正门（态②），不占 Owner 门位 |
| **T11** | `scripts/tasks/**.ps1` 在共享 index 里呈 `D `＋`??` 双态（他会话已暂存删、盘上仍在） | 案卷 §五-1 | 他会话 owner 责任制，本班不代修（宪法 §3.4） |
| **T12** | ⚑ 工令 §2-P4"死信四班 A 类 257 件复活中"实测零认领、93 袋零落地 | 统筹已批："批袋在队未落，此账**以落地后的袋数为准重对**" | 本班已建待重对项，四班落地后复核 |

## 八、本班自犯第三起（append，不改写 P1 §五）

**探针用了 mutating 版 `list_active()`**。00:37 一次诊断脚本尾部残留 `S(R).list_active()`（同脚本随后抛 AttributeError 中止）。车道独立复证：**`list_active()` 会写接管台账**，只读正门是 `list_active_readonly()`。
归因实测：`takeover/resolved/` 里那个 `st-maint3-20261011` 件 mtime **00:36:33 早于**我的调用；`takeover_ledger.jsonl` 行数仍 169、末行时刻仍是 23:26Z（**零新增条目**）；但**该文件 mtime 落在我调用之后**⇒ 内容未变而面被触碰，**我不能断言"没碰过"也不能断言"是我写的"，登记为未决归因**。
维护三班自身那一次 `pid 37924 dead → 现以 pid=0 在册、心跳 7.6s 新鲜`是机制自写，非本班所致。
**立规**：本班及后续所有车道，活死判定一律 `list_active_readonly()`；已在两份后继任务书里写死。

## 九、净零申报（本袋）

- 新增永久面＝**0**（未新建门禁/规则/注册表/第二套判据）；新增文件＝本袋＋2 份车道案卷＋影子/证据机生件（均在 `wave3/` 与本班 tmp 区）。
- 三面收敛线索已入 §四-5（停发第二棵树）、§五-4（两面并尺不并目录）、§六-Q2（内容寻址去重）；**本班未自开收敛实施**（改动他班真源面须册主车道出袋）。
- ⚑ 工具债申报：本班 P1/P2 生成器与波二 27 支工具同住 24h TTL 区，且实测 **22/27 支无 argparse（`--help` 即执行主逻辑）**。收敛建议（P5）＝统一上移到 durable 面并给每支补 argparse＋`--dry-run` 默认化，一条治本同时消掉"只读探测即写盘"这类事故面。

## 十、复核命令（只读；每条本班已自测能跑）

```bash
# —— 三机械面证据与执行回执 ——
python .runtime/tmp/st-fclean3-20261012/tools/p2_mechanical.py            # 出 out/p2_mechanical.json（只读，零删除）
python -c "import json,hashlib,pathlib;P=pathlib.Path(r'D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out');d=json.loads((P/'p2_delete_receipt.json').read_text(encoding='utf-8'));m=(P/'p2_delete_manifest.txt').read_bytes();print('manifest_sha256',hashlib.sha256(m).hexdigest());print('deleted',len(d['deleted']),'failed',d['failed'],'still_present',d['still_present'])"
python -c "import pathlib;n=sum(1 for p in pathlib.Path(r'D:/ZephyrAlpha/.runtime').iterdir() if p.is_dir());print('.runtime 顶层目录现数=',n)"   # 期望 149 面口径下降 46
# —— 两处唯一证据反转的对拍 ——
python -c "import pathlib;R=pathlib.Path(r'D:/ZephyrAlpha/.runtime');m=[l for l in (R/'takeover_ledger.jsonl').read_text(encoding='utf-8',errors='replace').splitlines() if l.strip()];t=[l for l in (R/'takeover_ledger.jsonl.tmp.23876').read_text(encoding='utf-8',errors='replace').splitlines() if l.strip()];sm=set(m);print('main',len(m),'tmp',len(t),'tmp_only',len([x for x in t if x not in sm]))"   # 期望 tmp_only=75
ls -l .runtime/.runtime/sessions/st-deadcure-20261009/heartbeat.jsonl .runtime/sessions/st-deadcure-20261009/ 2>&1 | head -6                    # 期望 正主不存在／nested 存在
# —— 归档器影子轮（每日至少一轮，影子期禁加 --execute）——
python scripts/governance/_tasks/session_closeout_reconciler.py --dry-run --json > .runtime/tmp/st-fclean3-20261012/out/shadow_roundN.json
python -c "import json,sys,pathlib;sys.path.insert(0,r'D:/ZephyrAlpha/src');from pathlib import Path;from zephyr.security.access_control.session_concurrency import SessionRegistry;d=json.loads(pathlib.Path(r'D:/ZephyrAlpha/.runtime/tmp/st-fclean3-20261012/out/shadow_round1.json').read_text(encoding='utf-8'));w=[k for k,v in d['actions'].items() if v.get('would_level2_archive')];live={s.session_id for s in SessionRegistry(Path(r'D:/ZephyrAlpha')).list_active_readonly()};print('mode',d['mode'],'scanned',d['scanned'],'would',len(w),'hits_vs_live',sorted(set(w)&live),'errors',d['errors'])"   # 期望 hits_vs_live=[] 且 errors=[]
# —— aidrafts 结构前置（禁裸删的依据）——
git -C /d/ZephyrAlpha worktree list | wc -l
ls -1 .aidrafts | wc -l ; for d in .aidrafts/st-*; do [ -f "$d/.git" ] && head -c 80 "$d/.git" && echo "  <- $d"; done | head -6
# —— 活性判据（唯一正确口径；勿用单文件兼容副本、勿用 list_active）——
python -c "import sys,time;sys.path.insert(0,r'D:/ZephyrAlpha/src');from pathlib import Path;from zephyr.security.access_control.session_concurrency import SessionRegistry;a=SessionRegistry(Path(r'D:/ZephyrAlpha')).list_active_readonly();print(len(a));[print('  ',x.session_id,round(time.time()-x.last_heartbeat,1)) for x in a]"
```
