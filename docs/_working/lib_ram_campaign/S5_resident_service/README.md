---
ttl: task_bound
title: S5 常驻服务可行性 · 图书馆内存常驻缓存战役（实测延迟拆分 + 宿主候选 + reaper 收割判定）
created: 2026-09-29
sid: st-libram-s4s7-20260929
status: 挖矿中（延迟已实测，宿主候选已取证；两处待补见 §7）
---

# S5 常驻服务可行性

**Owner 判据**：常驻服务层仅在 **CLI 延迟 > 10ms** 时做，`--max-memory-mb 512` 硬顶 + 并入 reaper RAM 水位。
本簿回答三问：(1) 实测延迟是多少、钱花在哪；(2) 10ms 这个门槛在"每次起 python"的形态下**能不能达到**；
(3) 若做常驻，宿主挂谁、reaper 会不会把它当孤儿收割。

## ① 真源（延迟数据只认实跑）

测量口径 [亲验]（本会话，Python 3.12.8，`PYTHONPATH=src`，仓库根 `D:\ZephyrAlpha`，2026-09-29）：

| 测量 | 样本 | 结果 |
|------|:---:|------|
| `python -c pass`（解释器裸启动） | 3 | **26 / 27 / 30 ms** |
| `python -c "import zephyr.library.lookup"` | 3 | **2789 / 3012 / 3051 ms** |
| `python -m zephyr.library.lookup kline 3`（全流程 CLI） | 5 | **2453 / 2568 / 2570 / 2665 / 2835 ms**（中位 **2570ms**） |
| 同 CLI 另 3 次（早批） | 3 | 2302 / 2512 / 2642 ms |

进程内拆分（同一次运行内打点，3 次）[亲验]：

| 段 | 耗时 | 占 CLI 中位比 |
|----|------|:---:|
| `import zephyr.library.lookup` | 2531 / 2653 / 2551 ms | **≈ 99%**（含 CLI 侧 psycopg 之外的全部链） |
| `get_depgraph_pg_connection()`（池化取连接） | 45 / 46 / 55 ms | ≈ 2% |
| `Librarian(conn)` 构造 | **0 ms** ×3 | 0% |
| 单条 SQL（`lib.lookup("kline",limit=3)`） | 6 / 6 / 9 ms | ≈ 0.3% |
| `lookup_assets(...)` 端到端（含别名 YAML 读 + 多词多轮 SQL + 自取连接） | **104 / 110 / 110 ms** | **≈ 4.3%** |

> 口径说明：上面两行百分比相加 >100% 是因为"import 段"与"lookup_assets 端到端"在 CLI 里串行、
> 分母同为 2570ms，而 `import` 段实测值本身已含 psycopg 驱动装载；`PGCONN 45-55ms` 与
> `one_sql 6-9ms` 之和 ≈ 51-64ms，与 `lookup_assets e2e ≈ 110ms` 的差额 =
> `_expand_query`→`_load_lookup_axis` 的词表 YAML 全量读+解析 + 展开词数的额外 SQL 轮
> （`lookup.py:89 → :51-78`，S4 §③A A4 同一条目）。此拆分 [推断]，未逐 ms 对账。

### 慢在哪：importtime 采样（`python -X importtime -m zephyr.library.lookup kline 3`）[亲验]

- 装载模块数 **1356**，累计 import **2135 ms**（≈ CLI 实测的 **83%**）。
- 累计 Top（含传递）：`zephyr.governance.depgraph_schema` **2134.9 ms**（= 全部，因 `lookup.py:35` 唯一重依赖就是它）
  → 其传递链 `zephyr.governance.resilience_governance.offline_autonomy` 507.5 / `zephyr.infrastructure.a2a_protocol` 506.8 /
  `zephyr.security.access_control` 499.6 / `zephyr.governance.persistence.database_service` 495.2 / `zephyr.data.ch_config` 491.5。
- 自身（self）Top：`gov_enforcement.rule_enforcement.gate_engine.gate_engine` **479.4 ms**、
  `behavioral_admission.admission_controller` **301.7 ms**、`data.pit_query` 246.8、
  `feedback_loop.security` 182.0、`rule_enforcement.task_types` 115.8、`data.ch_parts_monitor` 88.8、
  `lifecycle_governance.post_live_verification` 64.6、`persistence.sqlite_schema` 40.5；
  第三方仅 `charset_normalizer.api` 27.6、`pyarrow.compute` 24.6、`numpy._core._multiarray_umath` 21.3。

**结论 A（会返工的那条，先说）**：一个 CLI 查询里 **PG 侧只占 ≈4%（≈110ms）**，**import 占 ≈83-99%**，
且被 import 进来的绝大部分是**与查询无关的门禁/安全/准入模块**（gate_engine / admission_controller / a2a / adversarial_validation）。
所以：
1. "世代缓存"单独落地，对 CLI 形态的收益上限 = **≈110ms / 2570ms ≈ 4%**；
2. 真收益只有两条路：**(a) 进程常驻（免掉 import+握手，逐查询从秒级降到内存查找）**，
   **(b) import 瘦身（把 `lookup.py:35` 从 `depgraph_schema` 换成轻量连接入口）**——
   (b) 属跨域改动（depgraph_schema 是全体 depgraph 连接的统一入口，宪法 §7 与裁定#ARCH-DEPGRAPH_ACCESS_CONTROL 明令"所有 depgraph 连接必须经此入口"，
   `depgraph_schema.py:1613`），**本战役不该碰**，只登记为后续候选；
3. Owner §4 的常驻触发条件（>10ms）**已被实测满足 250 倍**，故常驻服务层**判定为做**（不是"可选"）。

**结论 B（判据本身要修）**：**`python -c pass` 裸解释器 = 26-30ms > 10ms** [亲验]。
即"**每次查询起一个 python 进程**"的任何形态（含瘦 CLI、含本地快照直读的 CLI）**在物理上不可能达到 <10ms**。
→ `<10ms` 只有在**已在跑的进程内做函数调用/进程内查找**时才成立。
建议交总筹复核：把判据写成"**常驻客户端单次查询 P50 <10ms**（宿主进程内），CLI 形态另立 <3s 口径"，
否则验收会拿一个永远达不到的数当红线（本战役最可能的返工点）。

**结论 B'（补测：H4 进程内路线的量化支撑）** [亲验，同进程连调 6 次 `lookup_assets("kline", limit=50)`]：
154.0 / 271.7 / 158.8 / 136.0 / 147.2 / **121.8 ms**——即**进程已热**时每次现读 PG 仍付 120-270ms（含别名轴 YAML 全量解析）。
对照代理量：20 万条内存 dict 子串扫 + 截断 = **7.56 ms**（构造 35.5 ms 一次性）。
→ 进程内世代缓存把 120-270ms 降到个位数 ms 是**可达的**（代理证据，非最终实现的实测），
H4 判定成立；<10ms 口径只在这一路线上可验收。

## ② 写者（世代进内存的写入路径归 S2/S3；本簿只管宿主）

本簿唯一"写"关注点：**谁付常驻进程的内存**。实测单进程 PG 侧数据面很小
（`one_sql 6-9ms`、limit=3）；200MB 峰值 ≈ 2 世代 × ~100MB 由 S3 定标 [读档]（Owner 规格）。
512MB 硬顶 vs reaper `_DANGEROUS_MEM_GB = 10.0`（`src/zephyr/trading/process_reaper.py:172`）——
512MB 远在危险线下，**reaper 的内存判据不会拦它**，反过来说：**reaper 的空转判据才是杀手**（见 §⑤）。

## ③ 消费者（谁能用上常驻）

- 高频：`capability_lookup._library_dedup_probe`（`capability_lookup.py:280-294`）→ AI 每轮施工；
- 人工：`python -m zephyr.library.lookup`（CLI）/ `--feeds`（`lookup.py:245-252`）/ `relations`（`library/relations.py:284`）；
- 生成器/对账：S4 §③A A6/A7 与写侧——**禁走常驻**（S4 §⑤ 不可缓存清单）。
常驻化收益排序与 S4 收益表一致：A1/A2/A4 前三名。

## ④ 漂移史（为什么"起个守护进程"在本仓不是自由动作）

1. **lookup.py 自己就声明了"我不是常驻系统"**：`lookup.py:17`
   `# noqa: m11-perm-manual-legitimate  M11豁免: 总目查询 CLI 人工按需调用是设计形态，非常驻系统`
   —— 一旦改成常驻服务，**这条豁免必须撤**，否则 M11（永久系统必须非 manual 启动）判定与实现背离；
   门实现在 `src/zephyr/gov_enforcement/commit_gates/manual_only_permanent_gate.py` [读档]（本会话未逐行读，见 §7 缺口 2）。
2. **连接池早就有，CLI 用不上**：`get_depgraph_pg_connection` 默认 `pooled=True`（`depgraph_schema.py:1605`），
   per-role 池 `minconn=1, maxconn=5`（`:1625-1629` 文档串），并有 `release_depgraph_pg_connection()` 归还口；
   而 `lookup.py:144` 走的是 `conn.close()`——文档串明说 close 安全但"**失去复用收益**"（`:1626-1628`）。
   → 常驻化顺带把 close 改 release 才是完整收益；这条属 S2 施工面，本簿登记不越界。
3. **M10 时间触发红线**：`api_server.py:22` 与 `heartbeat_daemon.py:18` 各自挂了 `# noqa: m10-time-trigger` 豁免，
   理由是"服务内生遥测线程/session 生命周期循环，非周期触发"。**新的常驻缓存若自带轮询刷新，直接撞根宪法 §9.3**
   （reconciler 必须事件触发、禁 cron/Timer/sleep-loop）——刷新语义只能是"读时版本比对 + single-flight"（Owner §2）。

## ⑤ 冲突面：reaper 会不会把它收割（本簿硬取证）

reaper 判据链（`src/zephyr/trading/process_reaper.py`，文件头 `:39-48` 自述优先级）[读档]：

| 规则 | 阈值/代码位 | 对"空闲常驻缓存服务"的后果 |
|------|------------|---------------------------|
| 白名单 cmdline 正则命中 = **永不杀** | `:198-208` `_DEFAULT_WHITELIST`（含 `zephyr.data.scheduler`/`tick_subscriber`/`worktree_drift_watchdog`/`write_audit_daemon`/`ch_health_probe`/前端 panel/`http.server 8010`/`process_reaper` 自保/jedi）；判定 `:273-280` | **唯一稳态护身符**；`:196-197` 声明来源=`boot_autostart_architecture.md` 永久服务清单，原则"宁宽勿窄；个案保留走 _KEEP_FILE，不加在这里" |
| keep 文件（每行一个 cmdline 子串，非正则） | `:167-169` `_KEEP_FILE = data/runtime/process_reaper_keep.txt`；`:259-269` 读取（损坏行忽略）；`:278-280` 命中→`keep_file:<sub>` 保护 | 现网已有 `zephyr.frontend.dashboard.api_server` 与 `heartbeat_daemon st-commitspeed` 两行 [亲验 读本文件去注释 30 行]——**先例可用，但语义是"个案长批"非"永久服务"** |
| 孤儿超龄杀 | `:174` `age>2h` → kill；`:337-343` `orphan_aged` / `orphan_watch` | 父进程退出即成孤儿 → **2 小时后必死**（除非白名单/keep） |
| **空转杀（最狠）** | `:176-177` `age>6h 且 CPU<0.5%` → kill（`:348`） | 常驻缓存天生"长寿 + 几乎零 CPU" → **不登记必被当僵尸杀掉**，且是静默杀（`_log_kill` `:490-502` 落 `data/runtime/reaper_kill.log`，`:166`） |
| `.runtime` 路径孤儿 | `:186` `_RUNTIME_ORPHAN_KILL_AGE_S=1800`；`:328-334`（`:42` 规则 4） | **陷阱**：若常驻脚本放在 `.runtime/`（含 `.runtime/tmp/`）下起，cmdline 命中 `\.runtime[\\/]`（`:210`）→ 30 分钟即杀。→ 常驻服务**入口必须是 src 下正式模块**，不得用 `.runtime` 临时脚本承载（同时合根宪法 §9.4 生命周期隔离） |
| 内存/子进程危险 | `:172-173` `mem>10GB` 或 `children>50` | 512MB 顶不触发 |

**判定（本簿立场）**：常驻服务**只能挂既有进程**，不得新起独立守护——理由三条，全是现仓证据：
(a) 新独立服务要活过 reaper 必须动 `_DEFAULT_WHITELIST`（`:198-208`，trading 域件，且注释要求"来源=boot 永久服务清单"→ 连带要改 boot，净零面扩大）；
(b) 根宪法 §9.3 禁 cron/Timer，新常驻系统要满足"自动触发/运行/维护/关闭"四要素（M11/M10 双门，见 §④1）；
(c) 挂既有已受护进程 = reaper 风险归零、四要素继承、无新真源。

**三条宿主候选 + 各自风险**：

| 候选 | 现状证据 | 适配度 | 风险（本簿要点） |
|------|---------|:-----:|------------------|
| **H1 `zephyr.frontend.dashboard.api_server`** | `src/zephyr/frontend/dashboard/api_server.py:1-22`：[TTL] permanent、[STARTUP] manual+面板一键重启、只读服务+四个获准写端点、[CONSUMERS] 前端 api.js；reaper keep 已含其名 | 最高（已 permanent、已受护、已有 HTTP 面） | ①**域越界**：D_FRONTEND 承载治理域真源缓存，读侧真源方向倒挂（RULE-SSOT）；②INVARIANTS "只读+四个获准写端点"是**授权留痕型条款**（Owner 2026-09-15 授权，见 `:11` 注释），新增端点=扩面，需走门位；③面板重启=缓存重启，世代易丢（可接受，快照可重载）；④它 import fastapi/uvicorn/clickhouse（`:4`），本就不轻 |
| **H2 `zephyr.gov_enforcement.rule_bridge.heartbeat_daemon`** | `heartbeat_daemon.py:1-19`：[TTL] **task_bound**、session_worktree spawn 的 detached 子进程、session 不在 registry 即退出、idle>1800s 退出、[MODIFY-GUARD] 明列"退出条件不得擅改" | **否决**（不是永久系统） | ①它按设计**自杀**（session 结束/idle 30min/锚点丢失三连，`:8`），缓存随宿主蒸发；②改它的退出条件=撞 [MODIFY-GUARD] 且涉 session_worktree 工作流核心；③[SAFETY] M、stability evolving，非缓存该挂靠的稳态件 |
| **H3 boot 永久服务族（`zephyr.data.scheduler` / `worktree_drift_watchdog` / `write_audit_daemon` / `ch_health_probe`）** | reaper `_DEFAULT_WHITELIST` `:199-203` 四者皆在册（白名单即"已在 boot 清单"的投影）；`[STARTUP]` 由 boot 拉起 | 中（reaper 免死、四要素已满足） | ①全是 **data/trading 域**，治理缓存挂上去=域越界更严重；②boot 清单是真源改动面（`boot_autostart_architecture.md`，本会话未验该文件存在，见 §7 缺口 3）；③`write_audit_daemon` 语义最接近"治理侧常驻"，可作首选子候选 |
| （备选 H4）**不常驻：in-process 化**——把缓存做成库内单例，谁 import 谁服务（CLI 仍 2.5s，但 `capability_lookup` 探针/AI 会话内多次查询直接命中内存） | `capability_lookup.py:288` 懒加载、同进程内 `find()` 可多次 | **性价比最高** | 零新真源、零 reaper 风险、零 boot 改动、无四要素义务；但**不解决 CLI 2.5s**（结论 A 的 import 才是主因） |

**建议给总筹的取舍**：分两步——先 H4（进程内世代缓存，覆盖高频 A1 探针面，零宪法冲突），
再按实测决定是否要 H1 常驻面板化。**Owner 判据"CLI>10ms 才做常驻"若按字面执行，会直接跳到 H1 并付域越界代价**；
结论 A 的实测（PG 只占 4%）说明这个跳法收益有限。

## ⑥ 净零方案

1. **不新建"lib_cache_daemon.py"**：常驻=挂既有宿主（H1/H3）或干脆 H4 in-process；新建独立守护需 boot 清单 + 白名单 + 四要素 + M11 撤豁免，
   属"新增永久系统"最高成本面，违反 §4.1 全资产净零。
2. **不新增内存水位册**：`--max-memory-mb 512` 封成代码常量（Owner §4），并入 reaper 现有观测（`mem_mb` 字段 `:428`、`ProcVerdict` `:232`），
   禁再造一份水位表。
3. **世代常量单一真源**：2 世代 / 200MB 峰值封代码常量（Owner §1），S2/S3 簿与本簿共引同一常量位，不各写一份。
4. **若最终不做 H1**：撤 `lookup.py:17` 的 M11 豁免这个动作即取消（保持现状"manual 合法"），零残留。

## ⑦ 自审闸三态

**状态：`未干`（延迟主问题已挖干并给出否决/推荐判定；宿主落地面有一处硬缺口未闭，据此可直接开工 H4，不可直接开工 H1）**

挖干部分：
- CLI 延迟三段拆分全部 [亲验]（3+3+5+3 次样本），importtime 明细 [亲验]，
  并给出两条会改判据的实测结论（PG 仅 4%；裸解释器 26-30ms ⇒ 每查询起进程永远达不到 <10ms）。
- reaper 收割判定 [读档 逐行 file:line]：白名单/keep/孤儿/空转/`.runtime` 五路判据齐全，
  其中"空转杀 age>6h & CPU<0.5%"是对常驻缓存最致命且最易漏的一条。
- 三宿主候选 + H4 备选，含 H2 的**否决证据**（task_bound + 三重自杀退出条件）。

缺口（不可视为干）：
1. **[已补代理测，仍缺终实现测] H4 的 P50**：结论 B' 给了同进程现读 120-270ms 与内存扫描代理 7.56ms
   （均 [亲验]），但**缓存命中路径本身还不存在**，故"<10ms"目前是代理证据 + [推断]，
   须在 S2 落地后由 S7 B-1 断言位实测封口。
2. **[未逐行读] M11 门的判定细节**：`manual_only_permanent_gate.py` 只经 grep 确认存在与命中口径，
   其 INVARIANTS / 触发条件（是否只看 `[STARTUP]` 字段还是也扫进程名）未读 → 撤/留豁免的影响面未定档。
3. ~~`boot_autostart_architecture.md` 未验存在~~ **已闭** [亲验 `git ls-files | grep boot_autostart`]：
   真身在 **`docs/03_modules/_domain_data/boot_autostart_architecture.md`**（tracked，`reaper:196` 只写了裸文件名未写路径）。
   → 反向加强 §⑤ H3 的否决理由：boot 永久服务清单属 **D_DATA 域**蓝图，治理缓存挂上去=跨域持真源。
4. **[未测] api_server 常驻化改造的启动耗时与端口面**：H1 若落地，需知道它当前是否在跑、
   重启代价（面板一键重启）与并发查询下 import 摊销，均未取证。
5. **[未做] 8890 端口的 HTTP 往返耗时**：H1 走网络调用，`<10ms` 判据对本机 HTTP 是否成立未测
   （若 HTTP 往返本身 5-15ms，H1 从原理上就吃不满 Owner §4 的门槛，这是选 H4 的第二条理由，但目前只是待测）。

受阻：无。
