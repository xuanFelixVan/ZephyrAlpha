---
ttl: task_bound
title: "S1 账本版本号机制挖矿簿 · 世代指纹现状实测 + 无版本号时的两案设计"
created: 2026-09-28
sid: st-libram-s1
lane: lib_ram_campaign/S1
status: v2（G1 指纹计时/G2 旁路写审计已闭，自审见⑤）
---

# S1 账本版本号机制挖矿簿

## ① 职责一句话

回答"图书馆总账现在有没有可用的世代指纹"：实测 lib_assets/lib_events 两表的版本类字段与其写入方，给出若无账本级版本号时的两案设计（meta 表 vs max(built_at)/max(event_id) 派生指纹），列失效场景与选案建议——只出案卷，不代 Owner 裁定。

## ② 现状实测（2026-09-28 本线 PG 只读直查 [亲验]）

### 2.1 有没有"世代指纹"可用？——**有行级版本，无账本级指纹**

PG 实时查询（`get_depgraph_pg_connection()` reader 角色，`information_schema` 直读）[亲验]：

- `lib_` 前缀表**仅两枚**：`lib_assets`、`lib_events`——**不存在** lib_meta/ledger_version 类账本级指纹表。
- `lib_assets` 实库 **21 列**，比 S5 簿记载（20 列）多出的 1 列即 `successor_of text`（S5 B3 批已落地，与 `ledger_schema.py:80` CREATE 常量逐列一致 [亲验]）。
- 行数 **44,963**；`max(built_at)=2026-09-27 09:40:11+08`，`min(built_at)=2026-09-21 04:33:34+08`；`max(generation)=418`，generation 去重值 85 个；`lib_events` `max(event_id)=2,231,744` 且 count 与之相等（序列无空洞，至少至今无 rollback 空洞）[亲验]。

### 2.2 版本类字段与其写入方（file:line 证据）

| 字段 | 语义 | 写入方 | 证据 |
|---|---|---|---|
| `lib_assets.built_at timestamptz DEFAULT now()` | **行级**重建时刻：每次 upsert 冲突分支 `built_at = now()` 刷新 | `_SQL_UPSERT_ASSET`（采集入账/act 更新均走） | `src/zephyr/library/ledger_schema.py:74`（列定义）、`:125`（冲突刷新）；执行者 `Librarian.act`/`register_batch`（`librarian.py:171-193`、`:218-242`） |
| `lib_assets.generation integer DEFAULT 1` | **行级**世代计数器：每次 upsert `generation = lib_assets.generation + 1` | 同上冲突分支 | `ledger_schema.py:75`、`:126` |
| `lib_assets.registered_at timestamptz DEFAULT now()` | 首次入账时刻（ON CONFLICT 不更新，恒为插入值） | INSERT VALUES 默认 | `ledger_schema.py:81`（CREATE 列；`_SQL_UPSERT_ASSET` 列清单不含它→仅初插生效） |
| `lib_assets.fingerprint_sha256` | **行**内容指纹（文件哈希），非账本指纹 | 采集器携值，COALESCE 保留 | `ledger_schema.py:72`、`:123` |
| `lib_events.event_id bigserial PK` | 全账本单调追加序列：任何 `act()`/`register_batch()` 写都插一行事件 | `_SQL_INSERT_EVENT` | `ledger_schema.py:93-101`、`:155-157`；`librarian.py:168-170`（act 同事务先插事件）、`:219-221`（batch 每条插事件） |

关键结构性质（决定指纹方案的可行性）：

1. **写必留痕**：馆员 INVARIANTS"event 与 state 同事务（不登记不变更）"（`librarian.py:8`）——**lib_assets 的任何变化必然伴随 lib_events 新行**。这是"事件序列号可作账本水位"的架构前提。
2. **now() = 事务时刻**：PG `now()` 返回事务开始时间，同一 `register_batch` 单事务内全部行共享同一 `built_at`（`librarian.py:202` docstring"单事务"）→ `max(built_at)` 即"最近一次入账事务"水位，批内恒定、批间可分（微秒精度）。
3. **行级 generation 非账本级**：`generation` 逐行独立自增（max=418 是单行最老/最频繁重建行的累计，distinct=85），**不能**直接当全局世代号用——它度量"这一行被改过几次"，不度量"账本换了几代"。

### 2.3 结论判定

- **可用原料**：`max(built_at)`（全表扫描聚合，built_at 无索引 [亲验：information_schema 列清单]）与 `max(event_id)`（PK btree，O(1)）都**存在且随任何写自动推进**——即"派生指纹"零 DDL 即可得。
- **缺失件**：无账本级显式版本常量（无 meta 表、无 `ledger_version` 列），缓存层若直接语义消费"世代号"需自建读出逻辑。

## ③ 六向台账

### 3.1 真源
- 账本唯一真源=PG depgraph 库两表：`ledger_schema.py:66-102`（DDL 常量）；实库列与其逐列一致 [亲验]。
- 字段语义真源=`docs/_working/ultimate_library/08_field_dictionary_v0_1.md`（冻结 v1.0 + §6 增枝制；S5 簿 §3.1 引用在案）。
- 事件流真源=`lib_events` 只追加（`ledger_schema.py:92-103`）。

### 3.2 写者
- 唯一写路径=Librarian（`librarian.py:101-117` `ensure_schema`、`:119` `act`、`:201` `register_batch`）；DDL 常量层 `_SQL_UPSERT_ASSET` 为 built_at/generation 推进的唯一语句（`ledger_schema.py:112-133`）。
- 触发方（S5 簿 §3.2 在册）：library_regen_reconciler（post-commit 事件触发，**本战役避让件**）、`generate_library_index.py` 自登记、人工处置链。
- 若选 meta 方案：新写者必须并入 Librarian 同事务（见 §4.2 失效场景 M3）。

### 3.3 消费者（本战役拟增）
- 现状：`lookup_assets`（`lookup.py:105-144`）每查询现开现关，无版本比对消费点。
- 拟增：S2 世代缓存层的"读时版本号比对"是本簿指纹的**第一消费者**；S3 快照层的版本列同源于此。

### 3.4 漂移史
- S5 簿 §3.4 记载的三快照漂移（27,864/27,949/28,454）本质=**账本与视图无世代锚**——各读者取到不同时点快照，若有账本级指纹则可判"视图属于哪一代"。
- `potential_consumers` 回填被再采集清零事故（`ledger_schema.py:104-111` COALESCE 注释，#410②/裁-07）：证明"同事务多语句"曾有语义漂移前科——meta 表写若脱离 Librarian 同事务必然重演。
- built_at 曾被当"新鲜度"读，但 ON CONFLICT 才刷新、初插走 DEFAULT now()——两条路径同值语义（事务时刻），无分叉。
- **本簿新发现·generation 语义漂移**：08 词典 L27 定义 built_at/generation="采集时戳+**扫描代次**（无指纹的记录=不可引用）"，但代码实现为**逐行** upsert 自增（`ledger_schema.py:126`；实测 max=418/distinct=85 [亲验]）——"全局扫描代"与"行内修改计数"两种读法不符。案 B 选指纹时绕开该歧义列；语义澄清列入 08 词典修订待裁定（本簿只登记不施工）。

### 3.5 冲突面
- 避让铁律：`library_regen_reconciler.py`、`reconciliation_registry.py`、`library_new_module_reconciler.py`、project_handbook 族、capability_canonical_file_registry.yaml、module_translation_registry.yaml——**只读引用，不改**。
- `ledger_schema.py` 现为 S5 B3 批活跃文件（successor_of 已落 DDL）：meta 表方案需再改该件（新 `_SQL_*` 常量），与其后续批存在合并面；派生指纹方案零 schema 改动、冲突面=0。
- DDL 通道：任何新表=改 `_SQL_ENSURE_*` 常量 + `ensure_schema()` 执行点（`librarian.py:112-117`）+ 迁移脚本走 `depgraph_write_path_gate` 白名单（S5 簿 §4.1 先例 `scripts/governance/migrations/add_acquisition_fields.py`）。

### 3.6 净零方案
- 两案皆**零替代**（现状账本级指纹=零覆盖，非重复建设）。
- 选派生指纹（推荐）时：**不新增表、不新增列、不新增写者**——净零天然成立；未来若 meta 表被更强需求（如视图代际锚）重提，本簿 §4.2 即其设计底稿。
- 本战役内 S2/S3 消费同一指纹读出函数（单写者公理：指纹判据只允许一处实现，拟落 `src/zephyr/library/` 新件，禁两处各写各的 SQL）。

## ④ 两案设计（若无账本级版本号）

### 4.1 案 A：lib_assets 旁 meta 表（显式版本）

设计：`lib_meta(key text PK, value text, updated_at timestamptz)`，`ledger_version` 行由 Librarian 在 act/register_batch 同事务末尾 `UPDATE ... SET value = value+1`（或写 max(event_id) 快照）。读出=单行 SELECT。

- 优点：语义显式、读出最廉（索引点查）；可携带附加代际信息（如 view_stamp，供 S5 tri-checker 消费）。
- **失效场景**：
  - M1 **旁路写漂移**：任何不经 Librarian 的写（白名单迁移脚本 `add_library_successor_of.py` 类 superuser DDL/人工 UPDATE）不推版本 → 缓存读到旧代却判"版本未变"。派生指纹无此洞（max(event_id) 被直查即见）。前提"写必走馆员"是 INVARIANT（`librarian.py:8`）但迁移脚本先例证明旁路存在（S5 簿 §4.1 白名单在册件）。
  - M2 **同事务失败半提交**：版本 UPDATE 与状态写不同语句序时（放事务头/中/尾的次序 bug）读者可见新状态旧版本或反之——PG 同事务原子性可保（SERIALIZABLE/REPEATABLE READ 下单事务要么全见要么不见），但**autocommit=True 的 reader 连接**（`depgraph_schema.py:1650` reader 默认 autocommit）每条 SELECT 独立快照，事务内窗口对其不可见 → 风险低但依赖"版本+状态同事务"纪律，写错序即漂。
  - M3 **DDL 迁移成本**：新表需 superuser 迁移批 + `depgraph_write_path_gate` 白名单登记 + 08 词典增枝呈批（Owner 门位）——落地前置周期最长。
  - M4 **重置/回放**：pg_restore/备份回滚后序列与 meta 值可能不一致（event_id bigserial 的 seq 随 dump 恢复通常一致，但 TRUNCATE+replay 场景 meta 值手工维护点+1）。

### 4.2 案 B：派生指纹（max(event_id) 为主，max(built_at) 为辅）

设计：指纹 SQL=`SELECT max(event_id) FROM lib_events`（PK btree O(1)，[亲验] 该列即 PRIMARY KEY，`ledger_schema.py:93`）；任何账本写必插事件行（`act` L168 / `register_batch` L219 同事务），**指纹推进由既有写路径天然保证，零新写者**。缓存层读时执行该单行查询，与驻留代比对。

- 优点：零 DDL、零迁移、零白名单、零旁路写洞（旁路直写 lib_assets 不插事件？——见 F1）；与"写必留痕"INVARIANT 同构。
- **失效场景**：
  - F1 **无事件的写**：直接绕过馆员改 lib_assets 的语句（superuser 迁移脚本 `ALTER TABLE ... ADD COLUMN` 属 DDL 不改行内容，可接受；但 `UPDATE lib_assets SET ...` 类数据订正若不补事件行则指纹不动）。缓解=数据订正一律走 act()/register_batch（现状纪律）+ 施工批在指纹读出函数 docstring 立"订正必补事件"条款；残余风险=人工 psql 订正（低概率，宪法 RULE-DATA-OPS 本就三步验证）。
  - F2 **序列空洞方向性**：事务回滚使 event_id 跳号但账本未变 → 指纹前进、内容未变 → 缓存多做一次"版本已变→重载"（**假阳性=性能损失，非正确性损失**；世代重载幂等，无害）。今日实测 count==max 无空洞，但纪律上必须容忍。
  - F3 **max(built_at) 辅指针对时钟**：依赖 DB 服务器时钟单调（NTP 回拨理论上可致水位不变而内容已变——PG 单实例同库同事务序，F 主指针对此免疫；主用 max(event_id) 即无时钟依赖）。
  - F4 **replica 读**：若未来查询走只读副本（现无此拓扑），副本延迟使指纹滞后——现单实例 PG，标 [推断] 远期风险。

### 4.3 选案建议（供 Owner 判读，非批文）

**推荐案 B（max(event_id) 派生指纹）为 S2/S3 当期消费；案 A 留作远期增枝**。理由：
1. Owner 定版硬约束#1"版本号未变永远复用"要求指纹**不可漏报新代**——案 A 的 M1 旁路写洞恰是漏报源；案 B 的 F1 是同一风险的镜像，但现状所有已登记写路径 100% 插事件（`librarian.py` 两写入口均硬编码），旁路仅白名单迁移件且均为 DDL（列增枝不改行内容语义？——修正：UPDATE 型订正也存在，见 add_acquisition_fields 先例是否带事件 [待核：施工批读该件确认]）。
2. 案 B 零 DDL 零迁移零 Owner 门位，与本战役"最小侵入"匹配；查询成本待 §4.4 实测（预期 <5ms [推断]）。
3. 案 A 的 view_stamp 附加语义（S5 tri-checker/馆页代际锚）是它真正的远期价值——届时按 08 §6 增枝制呈批，本簿 §4.1 即底稿。

### 4.4 指纹查询成本实测（2026-09-28 本线 [亲验]，同连接热态连续三轮）

| 查询 | 耗时 | 结论 |
|---|---:|---|
| `SELECT max(event_id) FROM lib_events` | **0.0035s** | PK btree 末端点查，满足"每读前比对"频率预算 |
| `SELECT max(built_at) FROM lib_assets` | **0.0159s** | 全表聚合（无索引），可用但劣于主指纹 |
| `SELECT count(*) FROM lib_assets` | 0.0052s | 参照系 |

旁路写审计（G2 闭合）[亲验 grep 全 `scripts/governance/migrations/` 目录]：目录内对 `lib_assets/lib_events` 的引用仅 `add_library_successor_of.py` 命中，且其 INVARIANTS 头 L8 明文"**不写任何行数据**（回填走 Librarian.act delete 处置链）"——白名单迁移件全部为纯 DDL（ALTER/COMMENT），不改行内容。`add_acquisition_fields.py`（S5 簿所引先例）经同 grep 证实**根本不触碰 lib_ 两表**（属 depgraph 域）。→ **案 B F1"无事件的行写"当前零既存实例**，残余风险仅=人工 psql 订正（RULE-DATA-OPS 管辖）。

## ⑤ 自审闸三态

**判定：挖干**（施工代理拿簿可直接开工——选案建议经 Owner 勾批后即为处方；指纹 SQL/成本/写入方证据齐）。条件一项：施工批须把指纹读出实现为 `src/zephyr/library/` 共享常量/函数（单写者），S2/S3 一律 import，禁各写各的 SQL。

### 证据清单（v2 收口）

| # | 项 | 状态 |
|---|---|---|
| G1 | 指纹查询计时 | **已闭**（§4.4：max(event_id)=0.0035s [亲验]） |
| G2 | 白名单旁路写审计 | **已闭**（§4.4 末段：migrations 目录全 grep，lib 两表仅纯 DDL 命中；`add_acquisition_fields.py:86-103` 只动 nodes_metadata [亲验]） |
| G3 | reader 对 lib_events 的 SELECT 权限 | **已闭**（§2.1 max(event_id) 查询成功即证明） |
| G4 | 08 词典 §6 增枝制直读 | **已闭**（`docs/_working/ultimate_library/08_field_dictionary_v0_1.md:108-110` "v1.0 冻结→字段新增=增枝制（停止判据三问+Owner 批）"[亲验]；附带发现 generation 语义漂移已登记 §3.4） |
