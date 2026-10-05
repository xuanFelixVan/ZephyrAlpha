---
ttl: task_bound
session: st-circ-a6-20260930
batch: 第4批/A6 挖矿簿 3/6
---

# S4-C 手术单 — CREATE-GUARD p90 缓存尾（热册并发写 cache-miss → 单例/分片/预热）

> 立档：2026-09-30 ｜ 车道：A6（design-only，不附代码）
> 真源文件：`src/zephyr/gov_enforcement/commit_gates/create_guard.py`、`src/zephyr/governance/capability_lookup.py`、`src/zephyr/gov_enforcement/rule_bridge/gate_cache_preflight.py`
> 遥测真源：`.runtime/audit/gate_execution_stats.jsonl`（2406 链次，本会话只读量取）

## 1. 现象量级（遥测实证）

- CREATE-GUARD 门级时延（本窗量取）：**n=1831、p50=0.2s、p90=55.3s、max=162.0s**——全场第一慢门（第二名 BLUEPRINT-HEADER p90 23.3s 且 cache reused=139；CREATE-GUARD **reused=0**）。Owner 立档口径 44.8s，同量级（窗口漂移）。
- 双峰形态：p50 0.2s=无新建文件早退链（`create_guard.py:1392-1401` return True）；p90 55s=**有新建 .py 时 `_build_capability_lookup()` 全量构造**（模块头自证「实测一次构造 ~86s」:1012）。
- P2⑧ 结果缓存对它无效：head_dependent 门被排除出 `CONTENT_SCAN_CACHE_WHITELIST`（`gate_cache_preflight.py:44-47` 明文）——故 reused=0 是**结构性**的，不是没开缓存。

## 2. 机理锚点

| 位置 | 内容 |
|------|------|
| `create_guard.py:1009-1018` | `_build_capability_lookup()` 构造缝：**每次 commit 新构造，无跨 commit 复用**；注释明示 ~86s/实例 |
| `capability_lookup.py:422-427` | 构造体：`_load_yaml`（40k 行 registry）+ `scan_disk_headers()`（:500，双根 src/zephyr+scripts/governance 全量头部扫描）+ `_derive_all`(:570) + `_reconcile`(:860) |
| `create_guard.py:705-754` | `_load_capability_registry`：registry **解析**缓存键=normcase+mtime_ns+size（:734、:245 注释「写后失效」）——热册并发写即失效重解析（40k 行 YAML） |
| `create_guard.py:1330-1342` | 有新 .py 才构造（p50/p90 双峰的分岔点）；basename 与关键词两检测共享单实例 |
| `gate_cache_preflight.py:44-47` | CREATE-GUARD 属 head_dependent → 白名单不准入（T7/B2 键收敛论证，本单不改此判据） |
| `gate_cache_preflight.py:102-122` | 白名单=实测 top15 准入（依据 gate_execution_stats）——「实测准入」纪律样板 |

**因果链**：夜战多会话并发写能力册（capability_cards / capability_canonical_file_registry 等）→ registry mtime_ns 变 → 解析缓存与磁盘扫描结果全失效 → 下一个带新 .py 的 commit 全量重构造 lookup（~45-86s）→ 该 commit 的 CREATE-GUARD 吃满 p90 尾。

## 3. 设计（意图，不附码）

**原则：判定语义零变化，只动构造时机与失效粒度。**

1. **进程级 lookup 单例**：`_build_capability_lookup` 改为模块级缓存实例，失效键=（registry yaml mtime_ns+size）∪（双根扫描概要指纹：根目录下 .py 文件数+max mtime 的廉价概要）。未失效→复用实例（0.2s 档）；失效→重建。gateway / commit_belt_daemon / 队列 serializer 均为常驻进程，跨 commit 复用成立。
2. **分片扫描**：`scan_disk_headers` 双根拆片（src/zephyr 一片、scripts/governance 一片），每片维护（文件数+max mtime_ns）概要清单——只有概要变化的片才重扫。热夜改 docs/scripts 不会把 src 片拖进重扫。
3. **预热**：常驻进程在空闲期（如 enqueue 入队后 / belt 心跳间隙）后台预建 lookup 实例；commit 到达即命中——把 55s 尾从「提交关键路径」搬走。预热线程与 commit 抢构造用既有 `_lock` 模式收敛为单次（双线程同抢只建一次）。
4. **fail-safe 对齐既有契约**：任何失效判定设施异常→回退现行为（每次新构造），绝不因缓存错而放行/阻断（对齐 gate_cache_preflight `[ERROR_CONTRACT]`）。
5. **不动面**：lookup 检索语义、#456 两档判据、白名单准入判据（CREATE-GUARD 仍不进 P2⑧——本单与 P2⑧ 正交，动的是构造成本不是结果缓存）。

## 4. 红测两针

- **R-C1 复用断言**：同一进程连续两次 `_build_capability_lookup`（registry 与扫描根未变）→ monkeypatch `scan_disk_headers` 计数必须=1 且第二次返回同实例——**现码每次全量扫描（计数=2），必红**。
- **R-C2 失效判别（红证隔离测试，对标 test_gate_cache_key_isolation）**：touch registry yaml（mtime_ns 变）→ 下次构造必须重建（计数=2）；反向：touch 无关文件 → 仍复用（计数=1）。分片变体：只变 scripts 概要 → src 片不重扫（分片重扫计数=1）。现码无失效键机制，判别测试在实现前不可表达、实现后红-绿双向可验。

## 5. 差分矩阵

1. registry 未变→复用；2. registry mtime 变→重建；3. registry 撕读/解析失败→不缓存、重建（:734 既有语义）；4. src 片概要变→只重扫 src 片；5. scripts 片概要变→只重扫 scripts 片；6. 片内新增文件→概要变→重扫该片；7. 进程重启→冷建一次；8. 双线程同抢构造→锁收敛单次；9. 预热线程与 commit 竞争→互等不双建；10. canonical 磁盘文件删除→概要变→重扫；11. pytest 每测隔离（单例不跨测试泄漏——monkeypatch 缝保留 :1014）；12. 失效判定设施异常→回退每次新构造（现行为）。

## 6. 风险与回滚

| # | 风险 | 缓解 | 残余 |
|---|------|------|------|
| 1 | **单例陈旧**：registry 改了但失效键漏判→判重用旧册=漏拦第二真源 | 键含 mtime_ns+size 双分量（mtime_ns 精度足够，Windows NTFS 100ns）；R-C2 红证；概要含 max mtime+文件数双面 | 同秒内同尺寸改写（理论窗口，max mtime 概要可加抽样字节哈希补强，暂不做） |
| 2 | 预热线程与 commit 线程竞态 | 进程内锁收敛（既有 `_lock` 模式）；预热线程为 daemon 线程不阻塞退出 | 低 |
| 3 | 内存驻留：lookup 实例常驻（实测构造数据量级：capabilities+disk_headers） | 双根头部数据 MB 级；超阈值可 LRU（暂不做，登记即可） | 低 |

回滚：改动集中于 `_build_capability_lookup` 缝内+scan 分片，env `ZEPHYR_CG_LOOKUP_SINGLETON=0` 一键回退每次新构造；单 commit revert 净退。

## 7. 估时

| 步 | 内容 | 估时 |
|---|------|-----|
| 1 | R-C1/R-C2 红测先跑取红证 | 0.5 h |
| 2 | 单例+失效键 | 1.0 h |
| 3 | scan 分片概要 | 1.0 h |
| 4 | 预热线程 + 差分矩阵 12 例全绿 + 真实 commit 复测（p90 期望 <5s） | 0.5 h |
| 合计 | | **3.0 h** |

## 8. 执行留痕（G3 车道 st-circ-g3-20260930 施工，2026-10-01 夜）

**红证先行**：`tests/gov_enforcement/test_create_guard_lookup_singleton.py` 共 10 测（R-C1 复用断言/R-C2 失效判别两针+矩阵抽样）。实现前跑得红证 **7 红 3 平**——红点全部落在复用/kill-switch/fail-safe/锁收敛/预热面（重建型断言被现码"每次全量构造"平凡满足），与 §4 预测红一致；实现后 10/10 绿。

**实现面**（判定语义零变化）：
- `create_guard._build_capability_lookup` 进程级单例：失效键=`_lookup_invalidation_key()`=registry(normcase+mtime_ns+size)∪`scan_root_summary` 双根概要（.py 文件数+max mtime_ns，stat-only）；未变复用/变即重建；设施异常→键=None→回退现行为每次新构造（fail-safe 对齐 [ERROR_CONTRACT]）。
- `warm_capability_lookup_async`：判重链完成后 daemon 预热/刷新（挂点=`_run_file_registration_checks` 尾）；与 commit 线程经 `_LOOKUP_LOCK` 双检收敛不双建；spawn 后全局态变键不匹配即弃轮（防测试线程误建）。
- `capability_lookup.scan_disk_headers` 分片缓存：`_DISK_HEADER_SHARD_CACHE` 键=(normcase root, normcase base_root)（防单/多根 rel 基准错位）；概要未变整片复用；概要不可得回退全扫不缓存。
- 一键回退：env `ZEPHYR_CG_LOOKUP_SINGLETON=0`。monkeypatch 注入缝（:1014 原缝）保留。gateway/commit_queue 有他会话 staged 改动，预热挂点收敛进 create_guard 自身缝内（不动 contested 文件）。

**真实进程实证**（生产注册表+双根，夜战写风暴环境）：
- 冷建 **81.5s**（辅助读数 108.8s/91.1s——他会话持续写册时更高，坐实 §1 量级）；
- 稳定窗单例命中 **133ms**（同实例）；仅注册表变的重建 **64.1s**（双分片全复用生效，vs 全冷 81.5s）；
- 失效键翻转率实测：夜战窗口 **15-30s/次**（他会话并发写 src .py 与注册表）——风暴期跨 commit 复用命中率受限=环境病理非机制缺陷，预热即为此设计（构造尾后台化，belt 常驻进程跨袋受益）。

**测试与净检**：单例 10/10 绿；回归 create_guard/capability_lookup 相关 7 文件 **77 测全绿**（含 canary 重型真实注册表条）；ruff check+format 双净。

**落地**：create_guard.py 面随 S4-B 袋 **01849a3d5d** 先行（队列 requeue"快照=当前工作区"语义所致归因交叉，`git log -1 --name-only` 已核）；capability_lookup.py 分片面+单例红测袋=**q-20261001-st-circ-g3-20260930-0008**（requeue 链 0001 幽灵误判→0003/0004 Popen 在途 bug 殉→0006 WinError233 环境死→0007/0008 同键顶替；hash 见该 qid done 记录/本簿入账袋）。

**让位与观察（三条，均已按专人专事让位）**：
1. 能力册三度 YAML 断裂（锚点 57788/57863，他会话追加工具把新 token 条目写到尾键 `di_seam_exemptions: []` 之后）——本车道 claim 后自愈让位未代修；**该追加工具尾键下移缺陷建议 Owner 立案**（复发即阻断全仓 CapabilityLookup 与带新文件的 commit）。
2. 落地通道 `Popen.__init__() unexpected keyword 'timeout'`（G2 车道 process_pool.py S4-F meta_out 在途 bug）致全仓队列袋连死（本车道 0002/0003/0004 三袋殉）——按堵点专人专事让位，G2 工作树修因（timeout pop→communicate）落地后 requeue 恢复。
3. 提交队列 4 次改道/死信/requeue 的处置链全录于 `.runtime/commit_queue/`（0001 幽灵误判死于本会话未注册 session registry——已补 `session_worktree_start` 注册+心跳守护后 force requeue 恢复；裁定#459 幽灵闸对"未注册活会话"的误伤面建议 Owner 知悉）。
