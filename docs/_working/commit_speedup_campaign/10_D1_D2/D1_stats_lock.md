---
ttl: task_bound
---

# D1 手术单 — `stats_lock` 停世界临界区（每落地一件在锁内重写全部 pending 文件）

> 立档：2026-09-24 ｜ 车道：`10_d1_d2`（设计-only，本文件不附代码，施工 lane 按本单写）
> 真源文件：`scripts/governance/commit_queue_landing.py`、`scripts/commit_queue.py`
> 实测环境：Python 3.12.8 / D: 盘（SSD）/ 抛袋根 `.runtime/tmp/cs-tbl/d1_probe/`（生产 `.runtime/commit_queue/` 全程零写入，仅只读统计）

## 1. 现象

k=4 落地池并发度恰为 1.000（四件 pairwise 文件集不相交的 pending 被严格首尾相接处理，零重叠）。
路径锁已被勘察 lane 排除为串行者。`_pool_process_item` 落账段是池内唯一一把**全工共享**的锁，
且其临界区内含一次「扫描并重写全部 pending 文件」的 O(N) 磁盘扇出。

## 2. 机理（file:line + 实测数字）

### 2.1 锁的构成与持有面

| 位置 | 内容 |
|------|------|
`commit_queue_landing.py:2096` | `stats_lock = threading.Lock()` —— **每波一把，四工共享** |
`commit_queue_landing.py:2105 / 2116` | `_reserve_slot()` 预扣名额 / 归还名额（短） |
`commit_queue_landing.py:2150 / 2163 / 2185` | 读项失败归还预算 / `stale_cleared` 计数 / `env_aborted` 置旗（短） |
`commit_queue_landing.py:2196-2216` | **重段（本缺陷）**：`result` 落账全程在同一把锁内 |

`:2196-2216` 临界区内实际执行的语句（逐行核实）：

- `:2198-2201` 成功支：`item["landed_at"]` → `cq._atomic_write(processing_path, …)` → `os.replace(processing_path, done/…)`
- `:2202` `stats["done"] += 1`
- `:2203` **`marked = cq._mark_cascade_stale(root, item)`** ← O(N) 扇出，本缺陷核心
- `:2204-2206` `stats["cascade_marked"] += len(marked)` + 日志
- `:2208-2212` 死支：`_atomic_write` + `os.replace` → `dead/` + `stats["dead"] += 1` + 日志
- `:2214` **`cq._notify_task_board_dead_letter(item)`** ← 锁内开 sqlite 连接（`commit_queue.py:940-972`）
- `:2215-2216` `stats["processed_qids"].append(qid)` / `shared["processed"] += 1`

昂贵调用 `landing(item, root)` 在 `:2182`（锁外）——这一段设计正确，不是本缺陷面。

### 2.2 `_mark_cascade_stale` 为什么贵（`commit_queue.py:1025` def，主体 `:1042-1063`）

- `:1042` `sorted((root / "pending").glob("q-*.json"))` → 每次落地全量枚举
- `:1043-1045` 对**每一个**候选 `read_text` + `json.loads`（无命中也要读，命中判定要看 `base_head`/`meta.depends_on`）
- `:1057-1060` 命中项经 `_retry_transient(lambda: _atomic_write(candidate, …))` 重写
- `commit_queue.py:396-403` `_atomic_write` = 写 tmp + `flush` + **`os.fsync`** + `os.replace`（每命中一件一次 fsync）
- `commit_queue.py:406-420` `_retry_transient`：Windows `PermissionError` 最多 5 次退避（0.02·k 秒，累计 ~0.3 秒/件）
  —— 这段睡眠**也发生在锁内**，是与并发 compaction/enqueue 撞窗时的乘性放大器（未复现，列为风险见 §8）

### 2.3 实测曲线（抛袋根，`enqueue_item` 真实入袋，payload 2KB/件，N=新鲜根 6 次取中位）

生产形态只读勘察：`pending` 实际 **83 件**，单件字节 min/med/max = **695 / 1240 / 15513**，
`base_head` 仅 **5 个不同值**，**同一 base_head 最多 77 件**（即一次落地的最坏重写扇出 = 77 件）。

| 场景 | N（pending 总数） | 命中数 | `_mark_cascade_stale` 首次调用 | 二次调用（已全部 stale，纯扫描） |
|------|------|------|------|------|
| 命中（同 base） | 1 → 2 件 | 2 | **14.25 ms** | — |
| 命中 | 20 → 21 件 | 21 | 194.33 ms（突发/AV 噪声上界） | 3.90 ms |
| 命中 | 60 → 61 件 | 61 | 86.23 ms | 5.90 ms |
| 命中 | **83 → 84 件（生产形态）** | 84 | **min 132.8 / med 144.3 / max 151.9 ms** | **min 6.8 / med 8.0 / max 8.8 ms** |
| 不相交 base（零命中） | 任意 | 0 | ≈ 纯扫描值 | 0.096 ms/件 |

微基准（隔离成本，用于外推）：

- `_atomic_write`（fsync+replace）：2KB 件 med **1.19 ms** / p95 **1.39 ms**；极小件 med 1.57 ms / p95 2.08 ms
- `read_text + json.loads`：单件 med **0.17 ms**（2KB）；批量口径 **0.096 ms/件**
- 拟合：**T_mark(N, h) ≈ 0.096·N ms + 1.74·h ms** —— 代 N=h=83 → 152 ms，与实测 144.3 ms 吻合

四工争用模拟（一把共享锁 + 每工各标 61 件，抛袋根）：

```
per-worker hold = 85.0 / 104.9 / 110.0 / 112.4 ms   wall = 412.8 ms   Σ = 412.3 ms
overlap ratio = Σ/wall = 1.00  ← 完全串行（零重叠），与现场并发度 1.000 同型
```

即：**单件落地让其余三工全停 ~0.1–0.4 秒**（首件最贵；后续件因 `:1048` 「已 stale 不重写」退化为纯扫描 ~8 ms）。
波内累计扇出量级：扫描 O(landings × pending) = 83×83×0.096ms ≈ **0.66 秒/波**，重写 O(pending) ≈ **0.15 秒/波**。

### 2.4 诚实结论（判据不改，但归因不越界）

D1 机理**成立且可复现**（锁内 O(N) fsync 扇出 + 锁内 sqlite 通知 + 锁内可睡眠退避），
overlap ratio 1.00 与现场 1.000 同型；但按本实测，其量级（~0.15 秒/件）
**不足以单独解释** 多分钟级件长的并发 1.000。故本单不申请「修完 D1 即并发达标」的验收。
残余嫌疑（移交勘察 lane，非本车道结论）：

- `commit_queue_landing.py:1390-1424` `_converge_main_workspace`：每件落地后对**共享主工作区**逐件 git 操作
  （主区 index/handle 争用＝天然串行点），幂等重放支 `:1513-1521` 同样调用；
- `:2203`/`:1054` 的 `PermissionError` 退避风暴（真实队列有活跃 enqueue 时才会显现）。

## 3. 影响面

| 面 | 说明 |
|---|---|
吞吐 | 每波额外 ~0.8 秒纯串行化开销；k 越大、pending 越多，停世界占比越高（O(N²) 扫描） |
正确性 | 无（当前临界区只是过宽，不缺锁） |
延迟尾票 | 单件最坏多等 ~150 ms（同 base 77 件场景）；若撞 `_retry_transient` 则上界秒级 |
可观测性 | `status` CLI 的 stale 口径、`cascade_marked` 计数语义不得变（§5 差分自证覆盖） |
不涉及 | 门禁判定、阈值、CAS 推进、路径锁、lane 优先级（本单零改动） |

## 4. 手术方案（逐处改动点，意图描述，不贴新代码）

**原则：把「必须互斥」与「顺手做了」分开——锁内只留计数与内存索引；磁盘扇出与外部服务通知出锁。**

1. **拆临界区**（`commit_queue_landing.py:2196-2216`）
   - 锁内保留：`stats["done"]/["dead"]/["cascade_marked"]/["processed_qids"]` 与 `shared["processed"]` 的读改，
     以及 §4.2 内存级联索引的写入（`qid` / `base_head`）。
   - 出锁：`cq._atomic_write(processing_path, …)` + `os.replace(processing_path, done|dead)`
     —— 依据：`processing_path` 由 `:2005` 的原子 rename 独占（认领即互斥），**不需要池级锁保护**；
     出锁后仍保持「先写带 `landed_at`/`landed_id` 的件，再 rename 到终态目录」的原顺序（幂等重放依赖此顺序）。
   - 出锁：`cq._mark_cascade_stale`（改为 §4.3 批量化）与 `cq._notify_task_board_dead_letter`（可观测性旁路，
     其自身 docstring 已声明「失败不阻断排空」`commit_queue.py:946/:972`）。
   - 意图：`with stats_lock:` 段缩为纯内存记账（微秒级），停世界窗口归零。
2. **落地侧登记级联索引**（`_pool_process_item` 成功支 + `drain_queue_pool:2022-2096` 的 `stats` 初始化处）
   - 新增 `stats["landed_index"]: list[tuple[qid, base_head]]`（锁内 append）；波内每件落地的
     `(qid, base_head)` 入索引，**不**立刻触碰 pending 盘。
3. **批量化级联标记**（`commit_queue.py:1025` 邻侧新增 `mark_cascade_stale_batch(root, landed_index) -> list[str]`）
   - 语义 = 现 `_mark_cascade_stale` 的循环合并：一次扫描 pending，对每候选判定
     「是否命中 index 中任一 qid（depends_on）或任一 base_head（相等且非空）」；
     命中且未标 → 记录**首个触发源**（`stale_by` 必须取「按落地序的第一个命中者」以保持字节级一致）→ 写出。
   - 调用点改造：
     - 池：`_run_pool_wave`（`:2088-2129`）join 四工之后、返回之前调一次（每波一遍，O(N) 而非 O(N²)）；
     - 串传送带：`commit_queue.py:1280` 现调用点改为「排空末尾用收集到的 landed_index 调 batch」，
       **单一实现，禁止新旧两版分叉**（串/并同语义是可证性的前提）。
   - `_mark_cascade_stale` 保留为 batch 的一元便捷包装或删除（若删除须同步 §7 测试清单，不得留死码）。
4. **认领时刻基底判定不再依赖盘上旗**（`commit_queue_landing.py:2157-2172`，**本条是安全的必要条件**）
   - 现状：只有 `item["meta"]["stale"]`（盘上旗）被读到才走 `_revalidate_stale_base`；旗由 §4.3 延迟写盘。
   - 改为：判定入参 = 「盘上旗 **或** 本波内存 landed_index 命中」，命中即按 stale 走
     `_revalidate_stale_base(item, _pool_head_reader(landing))`（函数不动）。
   - 不变式：**任何 base 已被本波越过的件，绝不允许未经重校验就落 dev**（否则即 09-24 热册驱逐同型的
     字段级内容净损）。§5 差分矩阵第 (6) 例专门证这条。
5. **死信通知出锁**（`:2214`）→ 移到 `with stats_lock:` 之后（同函数内，顺序不变，仅脱离临界区）。
6. **不动面（明写为不动）**：`stats_lock` 其余四处短持点（`:2105/2116/2150/2163/2185`）、
   `_pool_claim_item` 的 rename 互斥、`_item_path_locks`/`_release_path_locks`、
   `_mark_cascade_stale` 的命中判据（`:1050-1052`）、`_revalidate_stale_base`（`:1067+`）判据与阈值、
   `_SLOW_ITEM_LEDGER_SECONDS`（`:178`）、`_atomic_write` 的 fsync 语义（不降 fsync——耐久优先）。

### 施工顺位内的可选段（不在本单必做面）

- 变体 B「零重写懒标记」：pending 文件永不因级联被改写，标记完全活在内存 index，
  仅在 `status` 查询或波末按阈值 flush。省掉 144 ms 全部扇出，但**改变耐久契约**
  （进程被杀后 stale 不可见、`stale_by` 首因审计丢盘、`status` 读不到 stale）。
  → 判为需 Owner 单独裁的耐久语义变更，**本轮不做**；本轮只取变体 A（出锁 + 批量化），
  其稳态成本已降到 ~8 ms/波扫描。

## 5. 语义等价性自证方案（必须逐字段差分，不接受「不抛异常即通过」）

> 教训在册：「净删 0 但有字段级净损」。故计数相等不算证据，**键集 + 逐键值**才算。

新测试模块（建议名 `tests/governance/test_commit_queue_cascade_diff.py`）：

- 双实现同跑：旧实现从 git 对象库取基线字节（`git show HEAD:scripts/commit_queue.py` 经 importlib
  装入一次性模块命名空间），新实现从工作区盘取；两版各跑在**独立 `tmp_path` 队列根**上，
  输入完全相同（同一份 scenario dict）。
- 场景矩阵（每例都跑「串传送带」与「k=4 池」两条路径，四元对照）：
  1. 全部同 `base_head`（最坏扇出，N=20）；2. 全部不相交 base（零命中）；
  3. 分组 base（3 组，含单件组）；4. `meta.depends_on` 命中 + base 不命中；5. 二者同时命中（验 `stale_by` 首因）；
  6. **交错认领**：A 已落地、波末 flush 之前 B 被认领（专门证 §4.4）；
  7. 候选项含已 stale（验不重复标、`stale_by` 不被覆写）；
  8. 候选项 JSON 损坏（`ValueError` 跳过口径）；9. 候选项在扫描中被 compaction 移走（`FileNotFoundError`）；
  10. 超大件（15KB 生产实测 max）；11. 含 `deletes` 通道件；12. N=1（回归锚）。
- **断言（对 pending/ + processing/ + done/ + dead/ 四目录全部 JSON）**：
  - 目录文件名集合相等（qid 序列号差异按 §6 声明的 volatile 白名单处理）；
  - 每个文件 `set(old.keys() ∪ new.keys())` 递归到叶子逐键比对，输出 `path.field old=… new=…` 差异表；
  - 键集**双向**差分：`old-only` 与 `new-only` 都必须为空（只查「没少」不查「没多」是半证）；
  - 易变字段白名单（显式声明、逐条注释理由）：`meta.stale_at`、`landed_at`、`dead_at`（墙钟戳）、
    `qid` 尾部序号；白名单外的任何差异即红。
  - `stats["cascade_marked"]` / `done` / `dead` / `processed_qids` 集合与计数全等；
  - `stale_by` 首因全等（§4.3 「按落地序第一个命中者」的口径在此被机械检验）。
- 覆盖 §4.4 的专项断言：矩阵第 6 例中 B 的最终处置必须与旧实现一致（stale → `_revalidate_stale_base` 分岔），
  且不得出现「B 未重校验即落 dev」。

## 6. 红测方案（先证明能红，再谈修复）

两条确定性红测（不用计时器赌概率——见「反例说明」）：

- **R-D1-a 结构断言**：`_mark_cascade_stale`（或替换它的 batch 入口）被调用时**不得持池级锁**。
  做法：monkeypatch 该函数，在函数体内对 `stats_lock` 做非阻塞 `acquire(blocking=False)`；
  成功=已在锁外（随后 release），失败=仍在锁内。
  现码必红（`:2196` 持锁 → `:2203` 调用 → 非阻塞获取失败）。
  同时断言 `_notify_task_board_dead_letter` 同性质。
- **R-D1-b 扇出次数断言**：monkeypatch `cq._atomic_write` 计数（按目标路径过滤 `pending/q-*.json`）。
  一次「4 件落地 + 83 件 pending 同 base」的波内，pending 重写次数上限 = 83（每波一遍），
  **且 `_mark_cascade_stale`/batch 入口被调用次数 = 1/波**（现码 = 4，即落地次数）→ 现码必红。
- **R-D1-c 吞吐型辅助测（可后补，非门槛）**：fake landing 睡 1 s + `workers=4`，断言 overlap ratio > 1.5。
  按 §2.3 实测（144 ms 锁占 1 s 件长）此测**在当前码上也可能已绿**，故它不能当判据——
  写在此处即为防止施工 lane 用「并发度测不到红」误判 R-D1-a/b 失效。

反例说明（明确禁止的伪红测）：仅比较「两版跑完都成功」/仅比文件数/仅比 `stats` 计数/靠 sleep 造争用。

## 7. 必绿测试清单（一个不许改判据、不许跳）

- `tests/governance/test_commit_queue.py`：`:651 test_depends_on_hit_marked_stale_then_cleared_and_landed`、
  `:670 test_base_head_equality_marked_stale`、`:696 test_stale_revalidate_mismatch_goes_dead_cascade_stale`、
  `:721 test_stale_revalidate_match_passes`、`:736 test_stale_base_blob_without_head_reader_fail_closed`、
  `:754 test_stale_mark_persisted_on_disk_before_processing`（**本单最贴身的一条：盘上旗时机**）、
  `:311 test_compaction_vs_drain_concurrent_race`、`:368/:393` 死信支、`:451 test_dead_letter_tags_task_board`、
  `:496 test_board_unreachable_does_not_block_drain`、`:219 test_crash_mid_drain_then_idempotent_resume`、
  `:1009 test_drain_aborts_on_landing_environment_error`、`:1027`、`:951 test_dead_never_cleaned_invariant`、`:983`
- `tests/governance/test_commit_queue_pool.py`：全量（`:160/:179/:204/:229/:257/:316 test_k1_matches_legacy_byte_for_byte`
  /`:338/:380/:399/:434/:468/:481/:501`）——尤其 `:316` k=1 与旧路径**字节级全等**，是本单等价性的既有锚
- `tests/governance/test_commit_queue_landing.py`、`test_commit_queue_landing_nightfix.py`、
  `test_commit_queue_integration.py`、`test_commit_queue_base_head.py`
- `scripts/commit_queue.py` 侧的 CLI `status`/`requeue` 相关测试（`tests/governance/test_registry_ledger.py` 若触及 stale 展示亦须绿）
- 新增：`tests/governance/test_commit_queue_cascade_diff.py`（§5/§6）

## 8. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | **最大风险**：级联旗延迟写盘后，「盘上 stale 旗」不再及时驱动 §4.4 认领判定 → 基底已被本波越过却未重校验即落 dev = 兄弟件内容被无声覆写（09-24 热册驱逐同型字段级净损） | §4.4 定为必做（判定入参改为「盘旗 ∪ 内存 index」）；§5 矩阵第 6 例 + 必绿 `:754`；R-D1-b 波末 flush 断言 | 进程被杀在波末 flush 之前 → 未消费的 stale 旗丢；下波 `_recover_orphans`（`:2098`）+ 认领时的内存 index 重扫兜住**本波**，跨波由下波重算覆盖。须显式写进 docstring |
| 2 | 出锁后 `processing_path` 的 `_atomic_write`+`os.replace` 与他方交互 | rename 已提供独占（`:2005`），且 `os.replace` 本身原子；顺序不变 | 低 |
| 3 | 出锁后 pending 重写与 `enqueue`/compaction 撞窗 | `:1061-1062` 已容 `FileNotFoundError/PermissionError`（口径同旧）；`_retry_transient` 保留但移出锁 → 停世界放大反而消失 | 单件写失败=该项本轮漏标 → 由 §4.4 的 index 判定兜住（不影响正确性，只影响盘上可见性）→ 加 warn 日志 |
| 4 | 串/并两路调用点分叉 | §4.3 强制单一 batch 实现，两路共用 | 低 |
| 5 | 误判收益（把并发 1.000 记在 D1 头上） | §2.4 已按实测声明「不足以单独解释」；修完只验收「锁持有面 + 扇出次数」，吞吐另行复测 | 勘察 lane 继续查 §2.4 残余嫌疑 |

回滚：D1 全部改动局限 2 文件、无数据迁移、无格式变更 → 单 commit `git revert` 即净退。
波末 flush 不落新格式，`pending/*.json` schema 零变化（回滚后旧读器仍可读）。

## 9. 施工估时

| 步 | 内容 | 估时 |
|---|------|-----|
1 | §5 差分 harness + §6 两条红测先跑现码取红证 | 1.5 h |
2 | §4.3 batch 提取 + 两路调用点改造（串/并共用） | 1.0 h |
3 | §4.1/4.2/4.4/4.5 临界区拆分 + 内存 index + 认领判定 | 1.0 h |
4 | 必绿清单全跑 + 差分矩阵 12 例全绿 + 抛袋 N=83 复测（期望锁持有 <1 ms） | 0.5 h |
| 合计 | 一人一车道 | **4.0 h**（+1 h 缓冲：`_retry_transient` 若在真实队列撞窗需复判） |
