---
ttl: task_bound
title: "S2 Librarian 连接与世代缓存层挖矿簿 · 现状连接语义实测 + 3 次 CLI 计时 + 世代缓存设计与门禁消费面判据"
created: 2026-09-28
sid: st-libram-s2
lane: lib_ram_campaign/S2
status: v2（G1/G4 已闭合实测；自审=未干，悬案 G3 见⑤）
---

# S2 Librarian 连接与世代缓存层挖矿簿

## ① 职责一句话

实测"每次查询现开 PG 连接 + SQL 即关"的真实开销构成（含反直觉主因），给出世代缓存层（单代整表对象 + 原子指针交换 + single-flight + 2 世代常量）的实现位设计，并以逐件 file:line 判据厘清"零改动自动受益"的消费面到底是谁。

## ② 现状实测（全部 [亲验]，2026-09-28 本机直跑）

### 2.1 谁开连接、开几次、池化语义

| 事实 | 证据 |
|---|---|
| `lookup_assets()` 每调用开 1 条连接、finally 关闭 | `src/zephyr/library/lookup.py:116`（`conn = get_depgraph_pg_connection()`）、`:143-144`（`finally: conn.close()`）；CLI 主查询每次进程仅 1 调用（`:276`），`--feeds` 面另开 1 条（`:247-252`） |
| **连接池已存在**（§5.64.1 治本）：per-role `ThreadedConnectionPool`（minconn=1, maxconn=5），`pooled=True` 默认 | `src/zephyr/governance/depgraph_schema.py:1605`（参数默认）、`:1625-1629`（docstring 池语义）、`:1517-1536`（`_checkout_pooled`，PoolError 降级直连 `:1522-1525`）、`:1539-1579`（`release_depgraph_pg_connection`：rollback 归一 + RESET ALL + putconn） |
| **lookup.py 用 `conn.close()` 而非 `release_depgraph_pg_connection()`——池自愈回收槽位但失去复用收益** | `depgraph_schema.py:1626-1627` 明文："调用方 conn.close() 同样安全（池自愈回收槽位，但失去复用收益）"；`lookup.py:144` 即此反模式；`_run_feeds_query` 同款（`:252`） |
| reader 角色默认 autocommit=True；只读角色 depgraph_reader | `depgraph_schema.py:1602`、`:1648-1650` |
| `DatabaseService.get_depgraph_conn()` 是另一常驻路径：thread-local 长持连接（RealDictCursor），非本战役改造对象但同用池底座 | `src/zephyr/infrastructure/database_service.py:136-159` |
| Librarian 自身不建连接（构造注入 `PgConnection` 协议） | `src/zephyr/library/librarian.py:104-110`；`PgConnection` Protocol `:61-74` |
| 别名轴每次查询**重复读两遍词表 YAML**（CLI 主查询路径：`_run_main_query` 先 `_expand_query`(:273)，`lookup_assets` 内再 `_expand_query`(:119)；词表装载无进程缓存，`load_vocabulary_alias_map`+`yaml.safe_load` 各读一遍同一文件） | `lookup.py:51-78`（`_load_lookup_axis`）、`:81-98`（`_expand_query`）、`:119`、`:273` |

### 2.2 3 次 CLI 计时实测（`python -m zephyr.library.lookup <kw> --limit 5`，time.perf_counter，Python 3.12.8 [亲验]）

| 运行 | 墙钟 | rc | 输出行 |
|---|---:|---|---|
| `kline` | **2.4786s** | 0 | 5 |
| `ledger` | **2.5014s** | 0 | 5 |
| `reaper` | **2.7631s** | 0 | 5 |

同进程内分段分解（import→建连→查询→归还，冷池首连）[亲验]：

| 段 | 耗时 | 占 CLI 墙钟 |
|---|---:|---:|
| `import zephyr.library.lookup`（经 `zephyr.governance.__init__` → resilience_governance.offline_autonomy → infrastructure.a2a_protocol → security.access_control → adversarial_validation 链式重载，`-X importtime` 主链累计 2.789s） | **2.5976s** | **≈99%** |
| 连接建立（冷池首条：池初始化+TCP+认证） | 0.0510s | ≈2% |
| 单条查询（ILIKE 主查询） | 0.0123s | ≈0.5% |
| release（RESET ALL+putconn） | 0.0001s | ≈0 |
| 热池二次 checkout | 0.000029s | — |
| 热池第二查询全程 | 0.0074s | — |
| 指纹查询 `max(event_id)` | 0.0035s | — |
| 指纹查询 `max(built_at)`（全表扫，无索引） | 0.0159s | — |
| **世代构建全程**（8 列 SELECT 44,963 行→list[dict]，单语句） | **1.156s**，tracemalloc current **36.5MB/代**、peak 41.3MB | 旁路加载代价=1 个请求者独扛 ~1.2s（single-flight 其余等待）；**2 代常驻实测 ≈73–83MB，距 Owner 200MB 封度余量 >50%**（供倒排索引/小写拼接串扩容） |

**反直觉核心结论：CLI 2.5s 延迟的连接建立占比只有 ~2%，99% 是 Python import 链**。世代缓存**救不了冷 CLI 进程**（每次新进程必然重新装载+重载池）；它真正受益的是"同一进程内多次查账"场景（长驻 AI 会话经 capability_lookup、reconciler 刷新管线、单 commit 批多门共进程）。R4 常驻服务层若立项，必须同时做 import 减脂（`zephyr.governance.__init__` 副作用链），否则服务进程冷启动仍是秒级——此条为 Owner 判据 4"CLI 延迟仍>10ms"的**测量口径警示：>10ms 判据必须按 DB 段（≈63ms）计，而非 CLI 墙钟（2.5s）计，否则永远触发 R4**。

## ③ 六向台账

### 3.1 真源
- 账本真源=PG 两表（S1 簿 §2.1 [亲验] 44,963 行）；连接唯一入口真源=`depgraph_schema.py:1598`（"所有 depgraph 连接必须经此入口"docstring L1613）。
- 词表真源=`docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml`（`lookup.py:48`）。
- 缓存层（拟建）**非真源**：可派生镜像，版本比对恒以 PG 为准——生命周期定位=进程内物化视图，禁持久化语义（持久快照归 S3 簿）。

### 3.2 写者
- 账本写者不变=Librarian 两入口（`librarian.py:119` act / `:201` register_batch，写必插事件 S1 §2.2）。
- 缓存层写者=缓存模块自身（构建代时唯一赋值点）；**禁任何其他模块持有代指针**（单写者公理：`_current` 只在 ledger_cache 内 rebind）。

### 3.3 消费者（逐件 file:line，"零改动自动受益"判据）
受益机制=消费者在**长驻/批处理进程内**调用 `lookup_assets`/直查 lib_assets；缓存挂在 `lookup_assets` 之下（API 签名不变）则调用方零改动：

| 消费者 | 证据 file:line | 调用入口函数 | 进程形态 | 受益判定 |
|---|---|---|---|---|
| capability 反查图书馆探针（**全部 AI 会话冷启动必经 RULE-CAPABILITY-LOOKUP**） | `src/zephyr/governance/capability_lookup.py:892`（`find()` 入口）→ `:937`（`_library_dedup_probe(query)`）→ `:280-294`（探针体，`lookup_assets(:290)`） | `CapabilityLookup.find` → `_library_dedup_probe` → `lookup_assets` | **取决于宿主进程驻留性**：AI 经 Bash `python -c` 每次调 find=短命进程则缓存跨调用不存活；同一长驻 Python 宿主（AutoRuntime/import 方）内多次 find 才命中 | 条件受益（见⑤ G3——本线最大悬案）；MCP `rule_discovery_server.py` 经 grep 证实**不 import lookup_assets/capability_lookup 查询链**（仅审计文案 L162 提及）[亲验]，不在消费面 |
| 馆页生成器 | `scripts/governance/generators/generate_library_index.py:33,44` | 直查 `_SQL` 常量全表 dump（`FROM lib_assets WHERE status NOT IN...`） | 刷新管线批内 | 受益（可改读缓存代，施工批 2 期） |
| 覆盖检查器 | `scripts/governance/generators/check_library_coverage.py:32,40` | `SELECT asset_id, home, status FROM lib_assets` | 同上 | 受益（同上 2 期） |
| 退役候选探测 | `scripts/governance/d5_architecture/lifecycle/detect_retirement_candidates.py:83` | lib_assets+potential_consumers 查询 | 批处理 | 受益（2 期） |
| 退役执行器（写侧） | `scripts/governance/d5_architecture/lifecycle/retire_module.py:493,519` | `Librarian` 注入 | 批处理 | 写侧不适用 |
| CLI 总口 | `lookup.py:297-330` | `main→_run_main_query→lookup_assets` | 短命进程 | **不受益**（§2.2 结论）；受益路径=R4 常驻服务 |
| **TAG-VOCAB 门** | `src/zephyr/gov_enforcement/commit_gates/library/tag_vocab_gate.py`（全文 grep 无 lib_assets/lookup_assets 命中 [亲验]） | 读词表 YAML（`TAG_VOCAB_REGISTRY_REL_PATH` :101） | git_commit 短命进程 | **不消费 PG 账本**——"账本缓存自动受益"对它不成立，它受益的是词表装载缓存（S3 快照非其路径） |
| **BLOOD-FLESH 门** | `src/zephyr/gov_enforcement/commit_gates/library/library_blood_flesh_gate.py`（S5 簿 §4.3 实读结论：不连总账 DB，读 module_translation_registry.yaml L80 + git diff） | 同上 | 同上 | **同上，不受益** |
| depgraph 三门（非 lib 账本，但同连接底座） | `depgraph_pre_registration_gate.py:185-187,231-233`；`new_file_depgraph_gate.py:184-186`；`rename_depgraph_sync_gate.py:143-145` | `get_depgraph_pg_connection(autocommit=True, read_only=True)` 查 **nodes** 表 | commit 批内多门共进程 | 账本缓存不适用；**池归还修复**（close→release）使其互不重建 TCP——同批受益 |
| 对齐器/规则引擎 | `registry_alignment.py:252-254,299-301`；`triple_alignment.py:180-182`；`rule_engine.py:45,94` | get_depgraph_pg_connection（depgraph 域） | 常驻 AutoRuntime 内 import | 池化语义受益 |
| **library_blood_flesh / tag_vocab 之外**，`state_vocab_registry_gate.py` | commit_gates/library/state_vocab_registry_gate.py（priority=135，同读注册表文件） | 文件态 | 短命 | 不受益 |

**判据结论（诚实口径）**：真正的"零改动自动受益"面 = capability_lookup 探针链（AI 会话主力路径）+ 常驻进程内 import 调用方；**两个"已知门禁"实际不读 PG 账本**，题设词需修正为"门禁消费面中经 lookup_assets/直查 lib_assets 的子集自动受益，读 YAML 词表的门不在受益面"。commit 批内（一进程多门）若未来某门改读账本，缓存自动生效——该判据可机械复检：grep 消费面函数名 + 检查其进程驻留性。

### 3.4 漂移史
- §5.64.1 连接池治本前科：池耗尽降级直连注释（`depgraph_schema.py:1522-1525`）——"DatabaseService 常驻连接长持槽位"曾致 PoolError，设计缓存层必须避免再占死槽位（构建代=短借短还）。
- reader autocommit 历史默认（`:1620-1623` §5.61.2）：代构建 SQL 在 autocommit 下无事务快照——**整表 SELECT 单语句天然原子**，世代加载用单条 `SELECT ... FROM lib_assets` 即可（勿拆多语句拼装，防跨语句撕裂代际）。
- 27,864/27,949/28,454 三快照漂移（S5 簿 §2.2）=无世代锚的读者各取所时——本层世代版本号（S1 案 B `max(event_id)`）给每个进程内读者一个可声明的代际。
- potential_consumers 清零事故（`ledger_schema.py:104-111`）：COALESCE 语义教训——缓存读出的列集合必须与 `_SQL_LOOKUP` SELECT 列一致（8 列，`:160-166`），缺列即行为漂移。

### 3.5 冲突面
- 避让件（铁律）：`library_regen_reconciler.py`/`reconciliation_registry.py`/`library_new_module_reconciler.py`/project_handbook 族/两册 registry——刷新管线（reconciler 调 ingest_all）**不 import 本缓存**或只读消费，缓存失效靠版本号比对自动跟上，无需在 reconciler 内挂 invalidate（零改动避让）。
- `lookup.py` 现属 S5 B3 批活跃文件（墓碑显示已落 `:223-293`）：S2 改造点在 `lookup_assets` 函数体（`:105-144`）加"读缓存 or 直查"开关，与 S5 无行冲突面（S5 改的是显示层与 SQL 常量层）。
- 新文件（如 `src/zephyr/library/ledger_cache.py`）触发 CREATE-GUARD/translation/depgraph 三件套仪式（根宪法补充铁律）。

### 3.6 净零方案
- 世代缓存**不替代**任何现有件；与 S3 磁盘快照分层不重叠（内存代=进程物化视图，磁盘快照=跨进程资产，真源不同平面）。
- 零新连接入口（复用 get_depgraph_pg_connection）；零新写者；**顺手清偿**：lookup.py 的 `conn.close()` → `release_depgraph_pg_connection()`（2 处 `:144`、`:252`），使无缓存命中路径也吃池红利——此为现有反模式的收敛而非新增。
- 词表双读（§2.1 末行）可并一层进程缓存——但属 lookup 既有缺陷顺手修，不计入本战役新增面。

## ④ 世代缓存层设计（定版硬约束的落地形态）

### 4.1 数据结构：单代整表对象

```
class LedgerGeneration:            # 不可变（frozen dataclass）
    version: int                   # = max(event_id) at load 时刻（S1 案 B）
    built_ts: datetime             # 加载完成时刻（诊断用）
    rows: tuple[dict, ...]         # 44,963 行 × _SQL_LOOKUP 8 列，一次 SELECT 装入
    index_id: dict[str, dict]      # asset_id → row（精确命中轴）
    # 模糊轴（ILIKE 等价）：小写三列预拼接串列，加载期一次算好，读期 str.find
```

- 装载 SQL=单条全量 `SELECT asset_id, kind, home, status, title, built_at, disposition_authority, successor_of FROM lib_assets`（列集与 `ledger_schema.py:161` 恒等，真源经共享常量导入禁复制）。
- 内存实测口径：44,963 行 × 8 列 list[dict]=**36.5MB/代**（tracemalloc [亲验]，§2.2 末行）；2 代峰值实测 ≈83MB——距 Owner 200MB 封度余量充足，常量仍按封死值实现（行宽增长容忍带）。
- 无逐条淘汰：整表一个对象，代际整体换新。

### 4.2 原子切换点与 single-flight（threading 选型）

- **选型 threading 而非 asyncio**：现状全部消费链同步（psycopg2 + capability_lookup/generators/gates 无事件循环；`librarian.py` Protocol 为同步游标 `:31-58`）。asyncio 化=全链重构，违背"消费面零改动"。
- 实现位（新件 `src/zephyr/library/ledger_cache.py` 模块级）：

```
_GUARD = threading.Lock()          # single-flight：失效瞬间仅 1 线程去真源
_current: LedgerGeneration | None = None   # CPython 引用赋值原子（GIL）——读路径免锁：
                                           # gen = _current （本地引用快照）后无锁服务
_MAX_GENERATIONS: Final[int] = 2   # Owner 定版常量封死；峰值内存闸：构建前若
                                   # _pending 非 None 且 _current 未释放即拒绝并发第二 builder（锁保证）
```

- 读时版本比对：`SELECT max(event_id)`（0.0035s [亲验]）每代命中前查一次；等值→复用 `_current`；不等→`with _GUARD:` 内**二次校验**（double-checked：进锁后重读 version，可能前一个持锁线程已重建完）→ 仍旧才旁路加载新代。
- 切换序（RCU 式）：新代在 `_pending` 局部变量旁路构建（不触碰 `_current`）→ 构建成功 → `_current = new_gen`（一次字节码赋值原子发布）→ 旧代引用归零即时 GC；**切换点唯一**：赋值行本身。
- 版本读取失败=视为"未变"（保持服务旧代，标 stale 计数）——宁读旧代不放大真源压力。

### 4.3 失效路径（PG 不可达时行为）

| 场景 | 行为 | 依据同构件 |
|---|---|---|
| 版本比对查询失败，有旧代 | 服务旧代 + logger.warning + 返回行不标注（消费面零改动优先）；连续失败进退避——**禁 sleep-loop**：退避=按"下一次读请求"驱动（读时驱动，无 Timer，宪法 §9.3 红线），失败计数仅用于日志降噪 | 探针 fail-open 前例 `capability_lookup.py:292-294` |
| 版本比对失败，无代可服务（首查即 PG down） | 与现状逐字节一致：异常原样上抛（`lookup.py:13` ERROR_CONTRACT"DB 异常原样上抛"），CLI rc≠0 | 行为向前兼容 |
| 代构建中途失败 | 丢弃 `_pending`，`_current` 未动（切换前失败=天然无损）；下次读重试 | RCU 性质 |
| 整表加载成功但行数骤变（±>阈值） | 照常切换（账本本可暴涨暴跌，注册采集器全量入账即千行级/批 [亲验 generation max=418]）；只记 warning 审计 | 无熔断——熔断即第二裁判 |

### 4.4 峰值 2 世代常量落位

`_MAX_GENERATIONS: Final[int] = 2` 置于 `ledger_cache.py` 模块头（代码常量，宪法 RULE-SSOT：架构行为常量不入 YAML 配置面，防运行期被调大违 Owner 定版）；`# [INVARIANTS]` 头部注明"峰值≈2 代×实测代体积，禁第三代并存：single-flight 锁天然保证至多 current+pending 两代"。

### 4.5 API 消费面接入（零签名改动）

`lookup_assets`（`lookup.py:105`）体内分流：无过滤器且 limit≤阈值 → 走缓存代内存匹配；带组合过滤（kind/tags 等 5 轴）→ 同样可服务（代内 rows 预建倒排 tags 集）——统一走缓存，直查仅保留为 `LIBRAM_DIRECT=1` 逃生开关（warn 期对照）。ILIKE 与 Python `in` 语义差集（Unicode case fold/`%` 转义 `lookup.py:284-285`）用红蓝夹具回归：随机取 N 词双路 diff，零差才升默认。

## ⑤ 自审闸三态

**判定：未干**。已干面：连接全链实测、3 次计时+分段、消费面逐件 file:line（含题设修正——两已知门不读 PG 账本）、设计四要素（结构/切换/single-flight/常量位/失效）。

| # | 缺口 | 阻塞等级 |
|---|---|---|
| G1 | ~~代体积未实测~~ **已闭**：全表载入实测 36.5MB/代、构建 1.156s（§2.2 末行 [亲验]） | 已闭 |
| G2 | ILIKE-vs-Python 语义 diff 夹具未实跑（§4.5 设计已列，需施工批验证） | 中 |
| G3 | **消费面进程驻留性普查未做**：`CapabilityLookup.find` 的实际宿主（AI 每调起 `python -c` 短命进程 vs AutoRuntime 长驻 import）决定缓存收益面——世代缓存对短命进程零收益是本簿 §2.2 已证的硬事实 | **高（升格为最大悬案）** |
| G4 | ~~MCP rule_discovery server 驻留性与消费链未证~~ **已闭**：grep 全文无 lookup_assets/capability 查询链 import（`src/zephyr/integration/mcp/rule_discovery_server.py` 仅 :162 审计文案）[亲验]，MCP 通道不消费账本 | 已闭 |
| G5 | DatabaseService thread-local 常驻连接与池 maxconn=5 的槽位竞争在新缓存构建频率下的表现未测（§3.5 仅纪律性规避） | 中 |
