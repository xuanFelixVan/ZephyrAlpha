---
ttl: task_bound
title: S4 门禁消费面改造 · 图书馆内存常驻缓存战役（谁在查图书馆 / 频次 / 连接数 / 收益排序）
created: 2026-09-29
sid: st-libram-s4s7-20260929
status: 挖矿中（第一版已落，缺口见 §7 自审闸）
---

# S4 门禁消费面（穷尽式"谁在查图书馆"）

**本簿使命**：内存常驻缓存改的是读侧，改判据的前提是知道**所有读侧门在哪、多久响一次、一次开几条连接**。
本簿产出一张"改造收益排序表"+ 一条硬结论：**哪些位点永不可缓存**（写侧校验读缓存旧代=脏读，见 §5）。

> 体例循 `docs/_working/fms_overhaul/00_orchestration.md` §四：六向台账（真源/写者/消费者/漂移史/冲突面/净零方案）+ 自审闸三态。
> 数字口径：`[亲验]`=本会话实跑；`[读档]`=文档/代码声明；`[推断]`=由代码结构推导未实测。

## ① 真源（读侧唯一门在哪）

| 真源件 | 角色 | 证据 |
|--------|------|------|
| `src/zephyr/library/lookup.py` | 图书馆总口查询（API+CLI），MOD-LIB-003 | `lookup.py:2`（[MODULE]）、`lookup.py:105`（`lookup_assets`） |
| `src/zephyr/library/librarian.py` | 读+写（act）双口，封装 SQL | `librarian.py:2`、`lookup.py:36`（lookup 依赖 librarian） |
| `src/zephyr/governance/depgraph_schema.get_depgraph_pg_connection` | PG 连接唯一工厂（缓存层要包的就是这里出来的 conn） | `lookup.py:35`（import）、`lookup.py:116`（取连接） |
| 能力册（非图书馆）`capability_lookup` | 门禁主用的**能力反查**真源，经探针才落到图书馆 | `capability_lookup.py:5`（[CONSUMERS] 声明） |

**关键结构事实 [读档]**：门禁**不直接** import `zephyr.library`。对
`src/zephyr/gov_enforcement/commit_gates/` 全目录 grep
`zephyr\.library|librarian|library\.lookup|lib_assets|lib_events` **零命中**（本会话实跑，见 §③A 表尾"直连为零"行）。
门禁查图书馆的**唯一通路**是 `capability_lookup._library_dedup_probe` 的懒加载
（`capability_lookup.py:288` `from zephyr.library.lookup import lookup_assets`）。
→ 含义：本战役的读侧改造面 = "lookup 的调用者集合"，而不是"gate 的集合"；gate 侧只需保证
经探针链路行为不变（§③C）。

## ② 写者（谁让缓存失效——世代翻牌的上游）

| 写者 | 写什么 | 是否 bump 版本（本战役 R1 待接） | 证据 |
|------|--------|------|------|
| `library_regen_reconciler` | post-commit 采集→入册（collect_all/ingest_all + Librarian） | 必为最高优先挂点（读时版本比对的"写侧对家"） | `src/zephyr/library/library_regen_reconciler.py:4,127,128`；注册于 `reconciliation_registry.py:650,663` |
| `generate_library_index.py` | 生成 docs/library 馆页 + `librarian.act` 留痕 | 生成物变更=资产 home 变更 | `scripts/governance/generators/generate_library_index.py:33,118,151,159` |
| `retire_module.py` | 退役：`lib_events` 审计 + `lib_assets.successor_of` 双写 | 墓碑写入=读侧可见的状态跃迁，必须翻代 | `scripts/governance/d5_architecture/lifecycle/retire_module.py:493,496,497,519,524` |
| `add_library_successor_of.py`（迁移） | DDL 增列，不写行 | 一次性，非日常 | `scripts/governance/migrations/add_library_successor_of.py:26,145` |
| collectors 七路（fs/pg/ch/logs/mcp/schtasks） | 采登记表→总账 | 随 reconciler 触发，非独立 | `src/zephyr/library/collectors/__init__.py:29-34` |

**净结论**：写侧全部收敛在 `Librarian.act` 一族 + `ledger_schema` UPSERT，世代戳挂点唯一（详见 S1/S3 簿，本簿不重复施工面）。

## ③ 消费者台账（穷尽式，带频次与单次连接数）

### A. 读侧（缓存受益面）

| # | 消费点 file:line | 触发时机 | 频次 | 单次连接数 | 可否缓存 |
|---|------------------|---------|------|-----------|---------|
| A1 | `capability_lookup.py:280-294` `_library_dedup_probe` → `:290 lookup_assets(query, limit=5)` | AI 每次 `CapabilityLookup().find()` | 每轮施工前（人工/AI 触发，非每提交） | **1 连接 + N 次 SQL**（N=别名展开词数，`lookup.py:120-131` 逐词各查一轮） | **可（最大受益面）** |
| A2 | `library/lookup.py:105-144` `lookup_assets`（连接 `:116`，`finally conn.close()` `:144`） | CLI `python -m zephyr.library.lookup` / 被 A1 调用 | 人工 CLI + A1 下钻 | 1（开-用-关，无复用） | **可** —但注意连接口**本已池化**：`get_depgraph_pg_connection(pooled=True)`（`src/zephyr/governance/depgraph_schema.py:1605`，per-role 池 minconn=1/maxconn=5，`:1625-1629`），文档串明写"用毕应调 `release_depgraph_pg_connection()` 归还；调用方 `conn.close()` 同样安全但**失去复用收益**"（`:1626-1628`）→ 现读代码用 close 而非 release（`lookup.py:144, 252`），**常驻化后这条必须改，否则池被反复抽空** |
| A3 | `library/lookup.py:245-252` `_run_feeds_query`（连接 `:247`，close `:252`） | CLI `--feeds`（裁定#410 供数反查） | 人工按需 | 1（独立第二条连接路径，容易漏改） | **可，但须与 A2 同代**（否则 feeds 与主查询跨代错配） |
| A4 | `library/lookup.py:51-78` `_load_lookup_axis`（每次读 `library_tag_vocabulary.yaml` 全文件 + `yaml.safe_load`） | 每次 `_expand_query`（`:89`）→ 每次查询 | **每次查询 1 次磁盘读 + 1 次 YAML 解析**（无进程内缓存） | 0（非 PG，是 FS） | **可且应当并入世代快照**（别名轴与资产代同版本才自洽） |
| A5 | `library/relations.py:34,284` 关系图 CLI | 人工按需 | 低 | 独立连接 | 可（读侧同世代；本战役范围外，登记不施工） |
| A6 | `scripts/governance/generators/check_library_tri_consistency.py:253` 三层对账（总账↔视图↔盘面） | 提交/巡检 | 每轮 | — | **不可缓存**（见 §5，对账尺读缓存=自己判自己） |
| A7 | `scripts/governance/generators/check_library_coverage.py:32` 覆盖率（直调 `fs_collector.collect`） | 巡检 | 低 | — | 不可（它本身就是"盘→总账"的采集器，属写侧上游） |

**直连为零（重要负结果，本会话实跑）**：`src/zephyr/gov_enforcement/commit_gates/` 全目录 grep
`zephyr\.library|from zephyr import library|Librarian|library\.lookup` → **No matches found**；
二次 grep `library|lookup|lib_assets|lib_events` 命中全为**字符串/注释/同源 YAML 册名**，非 PG 读：
- `capability_lookup_required_gate.py:107` `LOOKUP_AUDIT_DIR_REL = ".runtime/lookup_audit"` — 读 **jsonl 审计文件**，不碰 PG；
- `capability_overlap_gate.py:139` / `create_guard.py:561` / `ssot_redefinition_gate.py:102` 读 `capability_lookup.REGISTRY_YAML`（能力册 YAML，非图书馆）；
- `create_guard.py:840-842` `CapabilityLookup().check_capability_duplicates(...)` — 扫磁盘头部+git，不碰 PG [读档]（`capability_lookup.py:32,54` 自述"初始化时自动扫磁盘头部+派生 git 历史"）；
- `library/tag_vocab_gate.py:71` / `library/state_vocab_registry_gate.py` 读词表 YAML（`docs/01_policies_and_standards/_registry/catalogs/library_tag_vocabulary.yaml`，与 A4 **同册不同读法**）；
- `depgraph_write_path_gate.py:157,158,239,240` 是把 library 写者列进**白名单清单**的字符串，非调用；
- `vocab_chain_gate.py:97,98` 是把 `library/collectors/` 当**受管路径前缀**，非调用。

### B. 提交链（每轮提交必经，缓存收益的乘数）

| # | 消费点 | 时机 | 证据 |
|---|--------|------|------|
| B1 | `GitCommitGateway` → `CapabilityLookup()` | 每次提交 | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1984` |
| B2 | `commit_preflight` 文案里给 AI 的口径"一次即可，审计按会话记账" | 每次提交（提示，非调用） | `src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py:568` |
| B3 | `check_ssot_gate.py:131,166` `CapabilityLookup()` + `check_capability_duplicates` | 独立脚本/manual 检查 | `scripts/governance/check_ssot_gate.py:131,166` |
| B4 | `scaffold.py:995` `CapabilityLookup()` | 脚手架 | `scripts/scaffold.py:995` |

> B1/B3/B4 走的是能力册（YAML+扫盘），**不产生 PG 连接**；只有 AI 主动 `find()`（A1）才落 PG。
> 所以"每提交 N 条 PG 连接"这个担忧在门禁面**当前为零** [亲验 grep + 读档声明]；真正的连接放大器是
> **A1×别名展开词数**与 **A4 每查询一次 YAML 全量解析**。

### C. 测试面（改造后必须零改动仍绿，红蓝验收蓝侧基线）

`tests/library/test_library_smoke.py:18,60,70,192,213,227`、`test_lookup_alias.py:21,22,64,70`、
`test_lookup_tombstone.py:11,18,19,143`（该文件 `:4` 自述"零 DB 依赖：fake conn/cursor，CLI 走 monkeypatch lookup_assets"——
**这条正是本战役读侧改型的既有护栏先例**）、`test_potential_consumers_guard.py:34-37`、
`tests/governance/test_capability_library_dedup.py:21`（自述"monkeypatch lookup_assets + tmp_path 审计目录，零真实 PG 依赖"）、
`tests/governance/commit_gates/test_capability_lookup_audit_log.py:83-89,159,174,201`、
`tests/governance/rule_bridge/test_ssot_gate.py:121-148` 多例。

## ④ 漂移史（消费面为什么会漂）

1. **探针 fail-open 是设计出的逃生口，也是漂移源**：`capability_lookup.py:282-283,292-294` 明写
   "PG/图书馆不可达返回 None，绝不影响 capability 反查主路径"——PG 挂了门禁**静默失明**，
   缓存版若沿用该语义会把"缓存过期"也吞成 None（S7 红侧 R-B 必测：PG 断连时缓存复用不得伪装成真源）。
2. **懒加载防循环依赖**（`capability_lookup.py:288` `# noqa: PLC0415 — 懒加载防循环依赖`）：
   library→capability 单向、capability→library 动态。常驻缓存层若在 import 期建代，会把这条环变成启动死锁 [推断]。
3. **审计目录跨区语义**：`capability_lookup_required_gate.py:122-125`（#ARCH-324）——队列落地 worktree 内读端
   必须锚 MAIN_REPO_ROOT。同理，缓存世代若落在 worktree 相对路径，会出现"每个 worktree 各一套代"的漂移 [推断]，
   世代戳/快照路径必须绝对锚定（交 S3 簿定标）。
4. **别名轴与资产代不同步**（A4）：词表 YAML 是 git 真源、资产是 PG 总账，二者各自演进；
   当前实现每次查询现读词表，所以不会错配；一旦词表进内存而资产不进（或反之）就产生新漂移 [推断]。
5. **文档口径已声明单口**：`generate_front_door.py:160,215`、`generate_library_index.py:98,142`、
   `docs/03_modules/agents.md`、`scripts/agents.md` 均把 `python -m zephyr.library.lookup` 立为唯一查询口——
   改造只允许换内部实现，改不动这个契约文本（§⑥净零）。

## ⑤ 冲突面（不可缓存位清单 + 避让）

**不可缓存位（硬结论，本簿立法）**：

| 位点 | 为什么必须现读真源 |
|------|--------------------|
| **写侧即时对账（点名条款，裁-07 事故件）**：`library_regen_reconciler.ingest_with_shrink_guard` 前后两次 `_count_nonempty_consumers`（`src/zephyr/library/library_regen_reconciler.py:53-60, 82-98`，SQL=`ledger_schema.py` 的 `_SQL_COUNT_NONEMPTY_CONSUMERS`） | 它是"入账前 vs 入账后"的**同库两次现读差值判据**——任何一次读缓存都使差值恒等、缩水事故永久隐身（09-24~27 三轮全量 ingest 悄悄清零 68 资产供数轴即此型事故，`ledger_schema.py:105-112` 注释实证） |
| **版本水位探测本身**：世代失效判定用的 `max(event_id)` 单查 | 读缓存判"缓存该不该换"=循环自证；此查询必须永远现读 PG（它是缓存层的裁判，不是缓存层的客户） |
| **写侧校验**：`Librarian.act` 前后对 `lib_assets` 行存在性/状态/`successor_of` 的校验，以及 `ledger_schema` UPSERT 的读回 | 写侧读缓存旧代 = 用已死资产判生，产生"改库不 bump 版本"型脏读；写侧唯一真源必须是 PG 当下事务（宪法 §9.3 事件触发语义的对家） |
| **tri-consistency 对账尺**：`check_library_tri_consistency.py:253` 附近"生成器自身=合法写路径；本断言只读 diff，不改不修" | 对账的三方之一是总账本身；若总账读缓存，则"总账↔视图↔盘面"退化为"缓存↔缓存↔盘面"，尺子自证 |
| **regen-clean 验证**（五支柱之生成闭环，`00_orchestration.md` §二.3） | `regenerate && diff --exit-code` 的权威是重新生成的产物，不允许从内存代取 |
| **collectors 采集源**（fs/pg/ch/logs/mcp/schtasks，`collectors/__init__.py:29-34`） | 采集器就是"盘面→总账"的真源搬运工，缓存它=搬运空气 |
| **lookup_audit jsonl**（`capability_lookup_required_gate.py:107,122-125`） | 文件系统即真源，不经 PG，与缓存无涉；勿误挂 |

**并行避让（只读引用，禁改）**：`library_regen_reconciler.py`、`reconciliation_registry.py`（`:650,663` 是其注册位）、
`library_new_module_reconciler.py`、`project_handbook` 族、`capability_canonical_file_registry.yaml`、
`module_translation_registry.yaml`——st-p1b 在途，本战役改判据在 S6 簿对齐。

**现场残渣 [亲验]**：`scripts/governance/generators/check_library_tri_consistency.py.tmp.22232.a10f663735ee`
（CAS `safe_write_text` 中断残留，内容与主件同段注释错位一行 `:221` vs `:253`）——本簿只登记，
不 claim 不删除（属他队写者面），供 S6 协调面与 S2 生命周期条款复用。

## ⑥ 净零方案（不新增第二真源）

1. **不新增"门禁缓存开关"册**：热/冷位判定就是 §⑤ 这张表，落在本簿 + S2 代码常量，
   禁再开 YAML 登记表（否则触发根宪法 §4.1 净零增长与 `registry_mass_deletion_gate.py:8` 净删风险双坑）。
2. **A4 词表读取收编**：`_load_lookup_axis`（`lookup.py:51-78`）现每次全量解析，改代后由世代快照携带
   `alias_map/canonical_to_tokens` 两个派生结构 → **删除** `load_vocabulary_alias_map` 的每查询调用（省一次磁盘+解析），
   真源方向不变（YAML→快照是派生，非第二真源，符合 RULE-SSOT 的"规则数据 YAML 同步 DB"）。
   与 `tag_vocab_gate.py:71`（写侧词表自检）**同源不同读**：写侧仍现读 YAML，禁走快照。
3. **消费点计数不写死散文**：本簿表行数随代码变化，登记口径循根宪法 §4.3（用字段/生成器，勿在散文背数）。
4. **替代关系**：本簿不替代 `docs/_working/fms_overhaul/S5_library_wiring/README.md`（那本治接线与墓碑，
   本簿治读侧性能面），二者交叉点在 §⑤ 不可缓存清单，单一真源=本簿该表，他处引用不复制。

## 改造收益排序表（本簿主交付）

| 排名 | 位点 | 现在每次的代价 | 世代缓存后的代价 | 收益等级 | 备注 |
|:---:|------|---------------|-----------------|:-------:|------|
| 1 | A2 `lookup_assets`（CLI 主查询，`lookup.py:116`） | 解释器冷启 + 1 次 PG 握手 + N 轮 SQL | 世代命中=纯内存匹配，PG 0 次 | **最高** | 唯一"人直接等"的位点；S5 常驻服务的立项目的 |
| 2 | A1 探针（`capability_lookup.py:290`） | 每次 find() 多 1 次 PG 握手（AI 每轮施工 ≥1 次） | 命中即零连接 | **高** | 收益×频次最高（频次随 AI 会话数放大）；但 fail-open 语义须保留（§④1） |
| 3 | A4 别名轴（`lookup.py:51-78`） | 每次查询 1 次全量 YAML 读+解析 | 随世代预构建，0 次 | **高（且零风险）** | 纯 CPU/IO，无 PG 语义争议，最先可做 |
| 4 | A3 `--feeds`（`lookup.py:245-252`） | 独立开第二条连接 | 与 A2 同代读内存 | 中 | 必须与 A2 同代，否则错配（§③A A3 行） |
| 5 | A5 relations CLI | 独立连接 | 世代可服务（图遍历另计） | 中低 | 本战役范围外，登记不施工 |
| — | A6 tri-consistency / A7 coverage / B1–B4 / §⑤ 全部写侧 | — | — | **禁缓存** | 见 §⑤ 不可缓存位清单 |

## ⑦ 自审闸三态

**状态：`未干`（诚实：三条硬缺口未闭合，勿据此直接开工）**

已挖实（可施工级）：
- 读侧消费点全集 A1–A7 带 file:line、频次、连接数；"门禁零直连"负结果经两次不同 grep 交叉验；
- 不可缓存位清单（§⑤）已立法，含"写侧校验不得读缓存旧代"的明确条款；
- 收益排序表 1–4 名判据来自代码结构 + 触发时机，非拍脑袋。

缺口（需下一轮补）：
1. **[待亲验] 单次连接/SQL 轮数的实测拆分**：A1/A2 说"1 连接 + N SQL"是从 `lookup.py:116-144` 与
   `librarian.py` 的调用形状推得的 [推断]；`Librarian.lookup` 内部是否再开子连接/是否走 prepared statement 未读透
   （`librarian.py:80` 起 SQL 常量簇未逐行读）。**S5 计时实测同批补**。
2. **[待亲验] 频次定量**：A1"每轮施工 ≥1 次"无计数证据。可行取证=统计
   `.runtime/lookup_audit/*.jsonl` 中 `tool=="capability_lookup.find"` 条目/会话
   （读写端口径见 `capability_lookup.py:297-334`，测试锚 `tests/governance/commit_gates/test_capability_lookup_audit_log.py:83-89`）。
   本会话未跑统计（工具预算优先给 S5 计时）。
3. ~~[未取证] MCP `rule_discovery` 通路是否也落图书馆探针~~ **已闭（结论：不落）** [亲验 grep]：
   `src/zephyr/integration/mcp/rule_discovery_server.py` 全件 grep `library|lookup`
   仅命中审计写口（`:58 __all__`、`:77 LOOKUP_AUDIT_DIR`、`:152/342 write_lookup_audit_log`），
   **无 `lookup_assets` / `zephyr.library` import** → MCP 路不产生 PG 读，消费面无需加 A8；
   图书馆的唯一入口仍是 `capability_lookup.find` 的探针（A1）。
   残余不确定：MCP server 运行期若有别的工具入口，本 grep 域外（登记不追）。
4. **[部分闭] `check_capability_duplicates` 是否纯磁盘**：本会话读得反向证据一条——
   缩水闸 `ingest_with_shrink_guard` 的计数走**显式传入的 PG conn**（`library_regen_reconciler.py:62-82`），
   即写侧对账自带现读通道、不经 `lookup_assets`；但 `check_capability_duplicates`
   （`capability_lookup.py:1167`）本体仍未逐行读，§③B 的"不产生 PG 连接"仍挂 [读档]。
5. **[新发现·待补进消费表] 读侧契约面正在被他队改**：`ledger_schema.py` 的 `_SQL_LOOKUP` 投影列
   在途新增 `disposition_authority, successor_of`（`lookup.py:223-242` 的墓碑渲染要它们）——
   世代快照行 schema 必须以改后列集为准，禁按 HEAD 写死（详见 S6 §② 第一号硬重叠）。

受阻：无（本簿纯只读取证，未遇权限/环境阻塞；`get_depgraph_pg_connection` 全仓命中集过大已落盘为
临时输出文件，未逐条读，属噪声非阻塞）。
