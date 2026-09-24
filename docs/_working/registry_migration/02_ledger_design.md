---
title: "W-M1 车道乙 · 注册表 PG 行级账本设计 v1.0"
ttl: task_bound
date: '2026-09-23'
session: st-wm1-mineB-20260923
status: draft_pending_owner
---

# 注册表 PG 行级账本设计（W-M1 车道乙·只读矿交付物）

> **一句话**：把注册表族从"共享 YAML 文件+整文件覆盖"迁到 PostgreSQL 行级账本（条目表+事件表+快照表三表），意图 API 按条目声明写、禁整文件接口；YAML 降级为生成器输出视图。设计同构复用终极图书馆 06/08 号文馆员账本（六道保障/死亡证明/四层强制），身份键沿用 W2 合并器与门禁的既有定义，权限制沿用 depgraph PG 角色分级既有件。**本文件只设计不施工**；呈 Owner 决策点见 §7。

## §0 挖矿范围与真源清单

- **车道**：st-wm1-mineB-20260923（W-M1 三车道之一，纪律同车道甲：只读矿，零代码零注册表改动，产出仅本文件）。
- **输入真源**：
  - 立项与根因：`docs/_working/registry_incident_20260922/DISPATCH_v1.md`（六层根因+车道卡）、`HANDOFF_v1.md` §5（治本查证任务书：对标 trunk-based/merge queue/CAB/配置中心/ulib 馆员账本）。
  - 同构复用：`docs/_working/ultimate_library/08_field_dictionary_v0_1.md` §3/§3.1/§3.3（事件流水/死亡证明九字段/并发六道保障）、`06_librarian_system_blueprint_v0_1.md` §1-§4（六权/六流程/四层强制）、`03_endgame_blueprint_v1_0.md` §3-§4（户籍 schema/存储分工）、`04_night_ops_plan_v1_0.md` B1 包（assets/fingerprints/events 三表+`librarian.act()`）。
  - 既有代码事实：身份键=`src/zephyr/governance/commit_gates/registry_mass_deletion_gate.py` `entry_identity_key`（:152，首标量字段）+`scripts/governance/commit_queue_landing.py` `_merge_entry_identity`（:300，复合键 `首标量|token=值`）与 `_split_registry_entries`（:221，族=顶层 list 键）；PG 角色制=`src/zephyr/governance/depgraph_schema.py` `get_depgraph_pg_connection`（:1594，reader/writer/superuser+白名单 gate+连接池）；DDL 惯例=同文件 `CREATE TABLE IF NOT EXISTS`+`_schema_version` 表；token 工具防呆先例=`scripts/governance/d3_metadata/batch_creation_tokens.py`（写前 HEAD 缺条目拒写/写后净减回滚/CAS）。
  - 现状锚点：W1 重建后 HEAD=9841 file 键（e3de925d0b，Lane 0b 验收口径）；`docs/01_policies_and_standards/_registry/catalogs/` 75 个 .yaml（机械可数；含 safe_write 残留 `.tmp.*`/`.bak` 若干——迁移盘点剔除清单，见 §4 Phase 0）；注册表发现唯一入口=ROOR（`docs/registry_of_registries.yaml`，含 maintenance 手工/派生字段）。

## §1 设计目标：从六层根因倒推

账本不是"把 YAML 搬进数据库"，而是让 2026-09-22 事故的六层根因**每一层都失去存在的物理条件**：

| # | 事故根因（DISPATCH 总则） | 账本机制 | 消灭方式 |
|---|---|---|---|
| 1 | 落地器整文件覆盖（`_apply_snapshot` write_bytes） | 意图 API 按条目声明写 | 系统不存在"整册写"接口，整文件覆盖无从发生（§3） |
| 2 | FIFO 陈旧快照放大（13.5h 旧基底抹 103 条） | 条目级版本 CAS | 基线版本不匹配=显式 409 拒绝+返回当前行，陈旧写永不静默生效 |
| 3 | 信任型逃生旗（旗文=人话非证据） | retire 强制 authority_ref+证据引用 | 退役无批件号机械拒绝；旗降级为审计注记（W3 同方向） |
| 4 | 登记工具无防呆（481 误插/4772 误删） | API 层 schema 校验+批量阈值+幂等判重 | batch_creation_tokens 守恒闸同构下沉 API（>N 拒绝、同内容 no-op、净减拒绝） |
| 5 | belt daemon 死=观测盲 | 事件表+快照表=天然审计面 | "谁/何时/改了什么/基线是什么"逐行可查，观测不再依赖单一活进程 |
| 6 | 无写窗口制度（靠静窗令人肉协调） | PG MVCC 行级并发 | 多会话并行写不同条目零协调；同条目并发=行级串行+CAS 显式冲突 |

**账本五不变式**（施工验收以此红蓝）：
- I1 已发布状态永不因并发写静默丢失——任何冲突必显式（409），无 last-silent-writer。
- I2 每一条状态变化有且仅有一行事件（谁/何时/基线版本/理由）。
- I3 任意历史时点全册可完整重建（快照直接读+事件回放等价）。
- I4 注销不是消失：retire=tombstone+死亡证明字段组（08 §3.1 同构），永不物理删除。
- I5 写路径物理唯一：app 角色无表直写权（08 §3.3 保障#2，depgraph 角色制同款）。

## §2 三表 Schema 草案（PostgreSQL）

### 2.0 命名空间与权限（沿用 depgraph 既有件）

- 独立 PG schema `registry_ledger`（与 depgraph 同实例同 DatabaseService 入口；连接经 `get_depgraph_conn` 同款 per-thread/RealDictCursor 惯例，新增 `get_registry_ledger_conn` 薄封装或直接复用+`SET search_path`）。
- 角色三级（`get_depgraph_pg_connection` 裁定#ARCH-DEPGRAPH_ACCESS_CONTROL 同构）：
  - `registry_ledger_reader`：默认只读角色（消费方/门禁/generator 读快照与条目）；
  - `registry_ledger_writer`：白名单脚本可用（API 模块+导入器+落地器 hook），DEPGRAPH-WRITE-PATH 式 pre-commit gate 查 `read_only=False` 调用点白名单（**既有 gate 语义扩面，非新检测器**）；
  - `ledger_admin`：DDL 与一次性迁移（superuser 路径既有）。
- DDL 纪律：幂等 `CREATE TABLE IF NOT EXISTS` + `_schema_version` 版本表（depgraph_schema.py 同款，可重跑）；所有时戳 `timestamptz` 全 UTC（RULE-SCHEMA-TZ 的 PG 形态）。

### 2.1 registry_catalog（册级登记表，小表，ROOR 派生）

```sql
CREATE TABLE IF NOT EXISTS registry_ledger.registry_catalog (
  registry_id        text PRIMARY KEY,      -- = YAML 头 registry_id（如 REG-RULING-001）
  physical_path      text NOT NULL UNIQUE,  -- catalogs/ 相对路径
  family_key         text,                  -- 条目族=顶层 list 键（entries/thresholds/…；NULL=根序列文件）
  identity_mode      text NOT NULL,         -- first_scalar | first_scalar_token | declared
  unique_key_fields  jsonb,                 -- YAML 头 unique_key 声明（机械可扫，不人工填）
  maintenance        text NOT NULL,         -- manual | derived | hybrid（ROOR 同名字段对齐）
  entry_schema       jsonb,                 -- YAML 头 entry_schema（API 层校验钩子的依据）
  status             text NOT NULL DEFAULT 'active',  -- active | switched(已切主) | retired
  ledger_version     integer NOT NULL DEFAULT 0,      -- = 最新 snapshot_version，发布时推进
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
```

- 种子=Phase 0 机械扫描（ROOR ∪ 文件头元数据），**零人工填写**（运维红线 5：清单必须生成器产出）。
- `family_key` 与 `_split_registry_entries` 的族定义同一真源：一册多族（如 THD-ALERT-007 形态：unique_key 元数据族+thresholds 条目族同文件）时按族分行或 family_key 存主族+`extra_families jsonb`（Phase 0 扫描报告定夺，两案呈施工令）。

### 2.2 registry_entry（条目表=状态表，last-writer-wins 的唯一一层）

```sql
CREATE TABLE IF NOT EXISTS registry_ledger.registry_entry (
  entry_pk        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  registry_id     text NOT NULL REFERENCES registry_ledger.registry_catalog(registry_id),
  family_key      text NOT NULL,
  entry_key       text NOT NULL,     -- 身份键字符串 = entry_identity_key(+_merge_entry_identity 复合) 原样输出
  payload         jsonb NOT NULL,    -- 条目声明段全文（派生段不入账本，决策点 D-1）
  payload_sha256  char(64) NOT NULL, -- 规范形内容指纹（幂等判重/死亡证明 final_fingerprint 复用）
  version         integer NOT NULL DEFAULT 1,      -- 条目级单调，CAS 基线
  status          text NOT NULL DEFAULT 'active',  -- active | retired（tombstone，永不物理删）
  held_by_session text,                            -- 持条会话（条目级租约，见 §3 租约）
  held_at         timestamptz,
  lease_expires_at timestamptz,
  created_by text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  updated_by text NOT NULL, updated_at timestamptz NOT NULL DEFAULT now(),
  last_event_id  bigint,             -- 指向产生当前状态的事件（冗余，追溯免扫描）
  UNIQUE (registry_id, family_key, entry_key)     -- 六道保障#5：唯一约束幂等
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_registry_entry
  ON registry_ledger.registry_entry(registry_id, family_key, entry_key);
CREATE INDEX IF NOT EXISTS idx_registry_entry_status
  ON registry_ledger.registry_entry(registry_id, status);
```

- **entry_key 语义唯一真源**：直接 `import entry_identity_key`（gate）与 `_merge_entry_identity`（合并器）同函数产出，**不复制逻辑**——账本、门禁、合并器三方身份永不各说各话（W2 落地器 docstring 明文要求"落地侧与门禁侧必须用同一份身份定义"）。格式示例：`ruling_id=402`、`file=src/zephyr/data/alerter.py|token=night-gw-20260901`。
- **CAS 语义**：`UPDATE ... SET version=version+1, payload=:new, updated_*=:... WHERE entry_pk=:pk AND version=:expected`——影响 0 行=版本冲突，返回当前行（409）。这是 K8s SSA resourceVersion 的同构；乐观锁由 PG 行级锁保证判定原子。
- **tombstone 纪律**：retired 行保留 payload+version 继续占坑（UNIQUE 不放开）——同键退役后复活=新事件 `reopen` 走版本推进，不是删除重插（裁定撞号 tombstone/死信留档同法系；08 §3.1"注销不是消失"原文收编）。
- 租约三列与施工层 claim 系统三层分工（08 §3.3 末段原文）：claim 管**文件**（施工互斥，`session_concurrency.claim_file` 既有）、队列管**落盘**（慢资源串行，既有）、条目租约管**账本条目**（新增，TTL 默认 30min 过期可接管）。两层互不替代：改文件要 claim，改账本条目要租约（或直写 API 由 CAS 兜底）。

### 2.3 registry_event（事件表，只增不改）

```sql
CREATE TABLE IF NOT EXISTS registry_ledger.registry_event (
  event_id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- 全局单调序
  registry_id   text NOT NULL,
  family_key    text NOT NULL,
  entry_key     text NOT NULL,      -- 三列冗余：追溯免 join
  action        text NOT NULL,      -- register|update|retire|reopen|takeover|
                                    -- lease_acquire|lease_release|publish|import|reconcile_drift
  actor_session text NOT NULL,
  actor_kind    text NOT NULL,      -- agent | human | generator | system
  base_version  integer,            -- 写者所见基线（register=NULL）；与 after_version 构成 CAS 证据链
  after_version integer NOT NULL,
  payload_after jsonb NOT NULL,     -- 全量（回放真源）；before 用指纹链式引用，不存双份全文
  before_sha256 char(64),
  reason        text,               -- ≥10 字纪律（NOQA 同款）；update/retire/takeover 必填
  authority_ref text,               -- 退役必填：裁定/批件号（死亡证明字段6）
  detail        jsonb,              -- 死亡证明九字段映射/接管审计等扩展位
  created_at    timestamptz NOT NULL DEFAULT now()
);
```

- **不可变的机械保障**（不止约定）：`REVOKE UPDATE, DELETE ON registry_event FROM PUBLIC`（writer 角色同样无权）+ `BEFORE UPDATE OR DELETE` 触发器 `RAISE EXCEPTION`——即使未来误授 write 权也删不动。快照表同款。
- **事件与 git 的关联不回填**（只增不改的代价设计）：事件表零 UPDATE 列；commit 关联放快照表 `git_commit_ref`（发布必在注册表 commit 落地之后，时序天然满足，无需回填）。
- 并发竞跑语义（08 §3.3 保障#4 原文）：同条目并发双写时，败者 CAS 拒绝但**拒绝本身也记一行**（action=update、detail.conflict=true）——两条事件全留，ts+event_id 排序可回放真实交错；状态行只有一行 last-committed-wins，历史永不丢。
- 容量：事件行均 <2KB，年增估 10^5 量级（现状注册表日均变更两位数条），单表无压力；v1 不分区，DDL 留按月分区钩子。

### 2.4 registry_snapshot（快照表，发布=不可变全量+单调版本）

```sql
CREATE TABLE IF NOT EXISTS registry_ledger.registry_snapshot (
  snapshot_pk     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  registry_id     text NOT NULL,
  snapshot_version integer NOT NULL,          -- 每册单调，发布序（Apollo release/etcd revision 同构）
  parent_snapshot_version integer,             -- 链式父版本
  manifest        jsonb NOT NULL,              -- {entry_key: payload_sha256} 全量清单（点查免解包）
  bundle          jsonb NOT NULL,              -- 全条目 payload 打包（PG TOAST 自动外置；v1 不引对象存储=内收）
  content_sha256  char(64) NOT NULL,           -- 整册规范形哈希（幂等发布判据）
  entry_count     integer NOT NULL,
  git_commit_ref  char(40),                    -- 对应 YAML 产物提交哈希（发布时已知，非回填）
  published_by    text NOT NULL,
  published_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (registry_id, snapshot_version)
);
```

- **发布的定义**：`publish(registry_id)` 仅在注册表 git commit 落地后由落地器事件触发（运维红线 3：事件驱动，禁 cron/Timer/sleep-loop）。同 content_sha256 重复发布=noop 幂等。
- **四个消费面**：①门禁/消费方读快照=MVCC 一致性读，免文件缓存竞态（noqa `_REGISTRY_CACHE` mtime 热加载那一族问题整类消失）；②YAML 生成器唯一输入（§3 render_yaml）；③回滚锚点（§4 Phase 3）；④审计"某时点册长什么样"（事故取证从 29 版本身份并集人肉考古降为一条 SELECT）。
- 与"静态清单禁手工维护"红线的咬合：快照表本身就是生成器产出物（publish 流程机械写入），YAML 视图又是快照的生成物——真源唯一层=条目表+事件表。

### 2.5 死亡证明字段组（08 §3.1 同构收编，不另建表）

retire 动作的事件行即死亡证明载体，九字段映射：death_cert_id→`event_id` 衍生（`DC-<registry_id>-<event_id>`）；asset_id→`entry_key`；final_fingerprint→`before_sha256`；disposition_action/cause_of_death→`detail` 枚举；authority→`authority_ref`（**缺失机械拒绝**）；evidence_path→`detail.evidence`；executed_by/at→`actor_session/created_at`；resurrection→`detail.resurrection`（封矿≠死亡条款同构）。保管级=permanent，与事件表整体不可变一致。

## §3 意图 API 契约（`registry_ledger.act()`，馆员 `librarian.act()` 同构）

### 3.1 接口面（按条目声明，禁止整文件读写）

```python
# 落点建议：src/zephyr/governance/registry_ledger/（api.py + schema.py + render.py）
# 命名空间规矩：governance/ 根禁新增 .py（CREATE-GUARD 既有令），入子目录天然合规

register(registry_id, family_key, payload: dict, *, reason, session_id) -> Result
update(registry_id, family_key, entry_key, expected_version, payload, *, reason, session_id) -> Result
retire(registry_id, family_key, entry_key, *, authority_ref, evidence, reason, session_id) -> Result
acquire_lease(registry_id, entry_keys: list, *, ttl="30min", session_id) -> Result
release_lease(registry_id, entry_keys: list, *, session_id) -> Result
takeover(registry_id, entry_key, *, force: bool, reason, session_id) -> Result      # 见 3.3
publish(registry_id, *, git_commit_ref, session_id) -> Result                        # 落地器事件触发
import_baseline(*, dry_run: bool, session_id) -> Report                              # Phase 0 一次性
render_yaml(registry_id, *, snapshot_version=None) -> str                            # 唯一全册出口
```

- **接口面负面清单**（宪法式一行一条）：不提供 `write_whole_registry`/`set_entries(list)`/任何接受"整册内容"的写接口；`render_yaml` 是唯一全册视图且**方向=输出**（产物，永不作为输入回收）；批量场景=batch 接口逐条调用逐条事件，条目级原子（部分成功=部分落+失败清单，禁单大事务——与 W2 落地器条目级三向合并同粒度）。
- 退役即"按条目声明"的最强形态：退役请求必须点名条目并附 authority_ref，系统**不存在**"把册里少掉的条目解释为删除"的路径——缺失即缺失，永不推断为意图（与 W2"快照侧删除不镇压现役"同向）。

### 3.2 结果契约（错误码机械可判）

| 结果 | 语义 | 对齐既有 |
|---|---|---|
| OK / OK_NOOP | 成功 / 幂等命中（同键同 payload_sha256 重复登记=no-op 返回现条目） | DUPLICATE_TASK_BLOCKED 语义、altdata"幂等可重插"教训 |
| CONFLICT_VERSION | CAS 基线不匹配，附当前行；**强制重读重放**（git rebase 语义） | 08 §3.3 保障#3 |
| CONFLICT_DUPLICATE | 同键异内容（真冲突），拒绝不覆盖 | W2 合并器"同键内容异→死信"同判据 |
| LEASE_HELD | 条目被他方活租约持有（未过期） | 死会话 stale claim 挡道教训的账本层对应物 |
| AUTHORITY_REQUIRED | retire 缺 authority_ref | 死亡证明"无授权不得签发" |
| SCHEMA_INVALID | payload 违反该册 entry_schema 声明 | YAML 头 entry_schema 既有声明机械可扫 |

### 3.3 双写拒绝与强制接管（任务书②的硬要求）

- **同条目双写=拒绝**：两会话并发 update 同条目，后到者 CAS 必败（version 已推进）→ CONFLICT_VERSION，**不存在合并或覆盖的第三种结局**。想继续=重读当前行重放自己的修改（合并是调用方的显式决策，不是系统的静默行为）。
- **强制接管=显式参数+审计**：`takeover(..., force=True, reason≥10字)` 仅两情形合法：①目标租约已过期（lease_expires_at < now）；②force 显式置位。两者都记 `action=takeover` 事件行（含被顶会话 id+reason），接管 Face 周审计（宪法 §3 own-scope 精神：别人的在途违规不代修，但死会话的租约必须可清——对应 gateway `release_files('<死sid>', files)` 的账本层同构）。
- 写路径收口分两档（决策点 D-3）：v1=Python API 物理唯一入口+writer 白名单 gate（DEPGRAPH-WRITE-PATH 既有件扩面，落地快）；v2=收口到 PG `EXECUTE`-only 账本函数（08 §3.3 保障#2 完全体，app 角色表直写权全数收回）。

## §4 切换方案（双轨并行对账 → 切主 → 回滚预案）

### Phase 0：基线导入（只读扫描，零冻结窗口）

1. 机械扫 catalogs/ 75 册（ROOR ∪ 文件头；**剔除** `_archive/`、`.tmp.*`/`.bak` 残留、`_index.yaml`）→ 每册抽 registry_id/family_key/unique_key/entry_schema/maintenance。
2. 条目切分复用 `_split_registry_entries`（yaml.compose 行号法已实战），身份键复用复合键函数；纯标量族（unique_key 元数据 list 等非 dict 条目）passthrough 标记不入条目表（W2 同款判据，防 THD-ALERT-007 形态死信）。
3. `import_baseline --dry-run` 报告：每册条目数/复合键退化清单/同键冲突清单/派生册清单 → **Owner 验收门**（对账 W1 口径：capability 册 9841 file 键逐册一致）→ 落库，全部记 `action=import` 事件。

### Phase 1：双轨并行对账（YAML 仍是 commit 真源）

- 写路径：会话照旧改 YAML→网关/队列→落地器；**新增落地后 hook**：逐条对账 PG（W2 合并器已在落地侧有条目级切分，hook 挂同一点，一行调用）——PG 缺=补登记，PG 多=drift 事件，同键异内容=drift 事件。
- 记账：drift 走 belt daemon 既有三 kind 通道（registry_drift 等，Lane B W5 已建），堵点本可见——**观测不再依赖人盯文件**。
- 对账器事件触发（landing/publish 后），幂等可重跑，禁 cron。
- **出口判据**（呈 Owner，D-5）：连续 7 天零未解释 drift + 消费方读取改造清单全绿 + 演练一次快照 render 与盘上 YAML 逐字节一致。

### Phase 2：按册切主（灰度节奏，非渐进条件）

- 试点册推荐 `ruling_registry.yaml`（决策点 D-4）：单键干净（ruling_id）、写入频率全族最高、消费方集中（RULING-REFERENCE gate 一处）——最小面验证全链。
- 每册切主动作三件套：①`render_yaml` 接管该册文件（此后 YAML=构建产物，人不再手改，改动只经 API）；②该册消费方加载器切 PG 快照（门禁 mtime 缓存机制保留为 fallback 读路径）；③ROOR 该册 `maintenance` 置 `pg_ledger`。
- 守卫：已切册的 YAML 若出现 ≠ 生成器输出的 diff，既有 SSOT 族 gate 语义扩面拦截（**候选登记，是否新门归 Owner 净零评估**）。
- 与 ulib 03 蓝图"漂移率×消费频率超阈值逐个搬"条款的关系：W-M1 治本直上令已覆盖该渐进条款（Owner 令：跳中间态）——本阶段按册推进是**发布节奏**（每册三件套可独立回滚），不是迁移门槛。

### Phase 3：回滚预案

| 阶段 | 回滚动作 | 代价 |
|---|---|---|
| Phase 1 双轨期 | 无需回滚：YAML 本就是真源，停记账 hook 即可 | 零 |
| Phase 2/3 切主后 | 触发条件（三选一）：PG 不可用超阈值 / 对账暴雷 / 消费方回切失败 → 末次快照 `render_yaml` 重生成全册 YAML → ROOR `maintenance` 翻回 manual → 门禁走文件读路径原状 | ≤1 个发布周期；数据零丢失（事件表是全历史超集，恢复后可重放） |
| 演练 | 切主宣告前必须红蓝实弹回滚一次（造 PG 不可用→走全流程→对账闭合） | 出口判据之一 |

## §5 与既有件的收编关系（宪法 w5_1 内收判据逐条过）

| 既有件 | 双轨期角色 | 切主后去向 |
|---|---|---|
| W2 三向合并器（commit_queue_landing） | 主力保护（队列落地零丢失） | 退役或降级为"render 一致性核对器"（比对代替合并） |
| `entry_identity_key`+复合键扩展 | 唯一身份真源，API 直接 import | 同左（永不复制逻辑） |
| safe_write_text CAS | 施工文件继续用；注册表族仍走 | 注册表族写路径由 API 取代；文件 CAS 保留给非账本文件 |
| 门禁 mtime 热加载（noqa 等） | 保留（读文件路径还在） | 读快照天然免缓存竞态，逐册退役 |
| batch_creation_tokens 守恒闸 | 保留 | 批量防呆语义下沉 API（>N 拒绝/幂等/净减拒绝同构保留） |
| 馆员 B1 三表（assets/fingerprints/events） | **视图引用不重建**（D-2）：registry_ledger 是 kind=registry 的账本实现，B1 落地时以视图引用本账本，复用同一三表模式 | 同左 |
| claim 系统（session_concurrency） | 施工层不动 | 同左；条目租约=账本层新增，两层各管一段 |
| belt daemon 三记账 kind | 订阅 drift/publish 事件记账 | 同左（观测通道现成） |

## §6 对标锚点（一句话各归各位；详标归门禁大审计车道 67 源对标，不重复挖）

K8s SSA resourceVersion=expected_version CAS；etcd revision+watch=全局 event_id 单调序+事件流；Apollo Release=registry_snapshot 不可变发布制；Gerrit/ GitHub merge queue=提交队列+行级合并（W2 现役雏形+账本补行级）；银行 CAB=retire authority_ref 审批留痕。本设计的增量不在单点机制（全部有业界成熟先例），在**六道保障与既有 claim/队列/门禁链的咬合**（08 §3.3 三层分工原文）。

## §7 呈 Owner 决策点

| # | 决策 | 推荐 | 理由一句话 |
|---|---|---|---|
| D-1 | 账本 payload 存声明段还是全条目 | 声明段（派生段如 capability 册 canonical_file 由派生器 render 时现算） | 保住"账本=意图真源、文件=派生视图"纯度，派生漂移永不再进真源 |
| D-2 | 与馆员 B1 账本合并还是视图引用 | 视图引用（registry_ledger 先行） | 同构不重复建；B1 未开工，先落者定义模式 |
| D-3 | v1 写路径收口档位 | v1=Python API+白名单 gate，v2=PG EXECUTE-only 函数 | 白名单 gate 既有件实证在役，先堵住 95% 面；PG 函数完全体随后收口 |
| D-4 | Phase 2 试点册 | ruling_registry | 单键/高频/消费方集中，最小面验全链 |
| D-5 | 双轨出口判据 | 连续 7 天零未解释 drift | 与现有静窗/广播节奏兼容 |
| D-6 | PG 备份链挂账 | depgraph 同实例，备份链并入 G 总仓双链（INFRA-STORE-003 地图） | 事件表=permanent 保管级，备份等级须对齐 CH 双链标准 |

## §8 挖矿边界与诚实声明

- 本设计**零施工零红蓝**：三表 DDL/API 契约未经实弹；对抗用例面（三写者交错/接管滥用/陈旧 CAS 重放）归车道丙红蓝用例矿交叉覆盖，两文件需对读。
- 身份键对"非 dict 纯标量族"不可判（`entry_identity_key` 返回 None）→ 账本侧 passthrough 标记不入条目表，与 W2 判据同源同边界。
- 未覆盖：PG 高可用/容量上限熔断（现状单实例与 depgraph 同水位）、事件表归档策略（permanent 全留，容量呈 D-6 一并裁）、册级多族形态的 family_key 终形（§2.1 两案留施工令）。
- YAML 历史损失不追溯（Owner 令），账本起点=W1 重建后 HEAD（e3de925d0b 口径）——账本不背历史账，只管未来不重演。
