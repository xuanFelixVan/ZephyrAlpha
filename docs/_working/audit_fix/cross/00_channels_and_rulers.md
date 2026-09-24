---
ttl: task_bound
---
# 横切件：落地通道选型 + 尺册（本包所有判据的单一登记表）

> 覆盖骨架 E04/E10/E11 三个环节的横切知识面（不属任一 lane，故不入 lanes/）

## 一、通道矩阵（本包实测，含"哪条通道送得动哪类改动"）

| 通道 | 适用 | 本包实测/复证结论 |
|---|---|---|
| 队列 `--enqueue`（正门） | 非 catalogs 文件＝passthrough 整件；`catalogs/*.yaml`＝条目级三向合并 | 袋必带 `base_head` 后才受快进保护（L1）；`config/governance_operations_map.yaml` 走 passthrough；`ruling_registry.yaml` 走条目合并（改条目内标量送得动） |
| 队列 + **只改标量** | ✗ 永远送不进 | `merged==ours` → `_merge_registry_file` 返 None → noop/"ok"＝**假落地（LAND-01 形）**；尺R 复证 |
| 队列 + 标量捆族内条目 | ✗ 也不行 | **本包新证**：条目落地、标量仍留 ours 旧值 ⇒ 案卷处方 (i) 不成立 |
| 网关直提（无 `--enqueue`） | 标量/头部行的唯一在册可审计通道 | 先例 `21c1aa5d61`（`in_process_gate_registry` 99→102，numstat `19 1`，尾注 `[GW:sid]` 无 `:q-`）；本包据此落 gate_registry/script_manifest/.importlinter 三件（主区三件皆 CLEAN，零外来叠层） |
| 会话工作树 commit + merge 回 dev | ✗ 本窗不用 | 主区 914 脏文件（他包在途），`session_worktree merge` 实为主区直连 merge＝连坐源（在册判例） |
| 裸 `git merge` / plumbing | ✗ 禁用 | 宪法第 9 章第 8 条 提交工具红线 |

**件级让路实录**（同修不同抢）：`rule_catalog_registry.yaml` 主区盘上已被他会话重生成到位
（盘 292/292 自洽 vs HEAD 274/292），与本包 `--auto-fix` 产物同一修法 ⇒ **本包不投该册**，
避免同文件双写手互吃；由在途袋落地 + 本包新立的自洽检测器共同保证归零。

## 二、尺册（判据登记表；E11 逐条复跑，两轮零才算过）

| 尺 | 命令 | 修前读数 | 期望修后 | 永久化位置 |
|---|---|---|---|---|
| 尺U-正门（审计班） | `python .runtime/tmp/audit_all_20260924/probe_maindoor_base_missing_r9.py` | C4=HARD | C4=SOFT（生产入口带基底） | 审计班临时件，收编进下行 |
| **本包 L1 尺** | `python -m pytest tests/governance/test_commit_queue_base_head.py -q` | — | 7 passed（含 1 阳性主案 + 4 阴性控制） | `tests/governance/test_commit_queue_base_head.py` |
| 判据 grep | `grep -c "base-head\|base_head" scripts/git_commit.py` | 0 | ≥1（实测 6） | 上表第 3 例断言化 |
| 尺S/BLIND（审计班） | `probe_headside_governance_bidirectional.py` | HEAD 3 硬 / 盘 0 | L5 落地后生产函数自身双锚可判 | `align_all [5/9]` 新增 HEAD 锚行 |
| **本包 L5 尺** | `check_governance_bidirectional()` vs `(source="head")` | 0 / 3 | L2 落地后 0 / 0 | 待补 pytest（E11 若发现缺位则本包补） |
| 尺O/幻影 | `_check_gomap_alignment(HEAD 版图, scan())` | 修前对 HEAD 版图报 0（失明） | 报 **3 幽灵**；重生成版报 0 | 生成器 HEAD 基＝判据本身 |
| 尺Q 自洽 | `validate_static_manifest_drift.py --check` | rc=1，5 项（含新立 2 项） | rc=0 GATE-21 PASS（worktree 实测） | 该 CHECKS 条目（常驻闸） |
| 尺R 通道 | `three_way_merge_registry_yaml` 纯函数重放 | 标量必被吞 | 不改合并器（改通道选型），复跑仍应=吞 | 本文档 §一 两行（防后人再踩） |
| 净零/净损 | 逐字段差分（条目集 + 字段级） | — | gate 180/180 变化 0 净损 0；rule 292/292 同；script_manifest 仅 4 条 NOT_IN_HEAD 幻影移出 | 各 lane 文档 §判据 |

> 立法沿用审计班总闸三条判据并全部满足：①控制组的**成功侧必须显式留痕**（尺O/尺H2 教训）；
> ②探针"零生产污染"必须是判据的一条（尺U R57 教训——本包 L1 尺全部走 tmp 仓 + tmp 队列根，
> 且 E11 复跑后须扫生产 pending 内 `probe` 命中=0）；③引用他轮登记的 hash/计数前先双口径复算
> （三套哈希口径不可互换，本包 `base_blob` 明确声明为 git blob id 空间）。
