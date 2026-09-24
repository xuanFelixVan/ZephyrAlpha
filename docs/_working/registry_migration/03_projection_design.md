---
ttl: task_bound
title: "W-M1 车道丙·YAML 投影生成器设计矿（生成器/漂移检测/读端容灾）"
session: st-wm1-mineC-20260923
status: draft
date: 2026-09-23
version: "1.0.0"
---

# W-M1 车道丙：YAML 投影生成器设计矿（只读产出）

> **一句话**：capability_canonical_file_registry.yaml 全量降级为 PG 账本的**纯函数投影**——同一个账本状态永远渲染出同一个字节流；生成器是唯一写者；漂移=「盘上 YAML ≠ render(PG)」，用**本地投影状态文件**判别四象限（私改/陈旧/双向冲突/干净），PG 宕机时检测降级不阻塞；**读端零改动**（11 个读端继续读本地 YAML，永不触 PG）——PG 只挡写不挡读，施工永不因 PG 死而停。
> **车道**：st-wm1-mineC-20260923（只读挖矿，产出仅本文件；纪律同车道甲=挖矿 SOP，日志见 §8）。
> **读者**：W-M1 施工总图汇编人（车道甲 01 盘点矿/车道乙 02 PG schema 矿/Owner 签字窗）。
> **关联**：DISPATCH 另两矿 `01_inventory_*.md`（甲）、`02_pg_schema_*.md`（乙）；事故背景 `../registry_incident_20260922/DISPATCH_v1.md`；对标总纲=主会话 67 源调研（K8s SSA/etcd/Apollo，见 §8③）。

---

## 0. 设计支柱（三条，对应派发令①②③）

| # | 支柱 | 一句话 | 关键裁定 |
|---|------|--------|---------|
| ① | 单向生成器 | `YAML := render(PG_ledger)`，纯函数、全量重打、幂等到字节 | 生成器是**唯一写者**；渲染**零时间戳**（连 idempotent_timestamp 都不用）；写盘走 safe_write_text CAS + `newline='\n'` |
| ② | 漂移检测 | 重生成+diff，私改现形 | 判别真源=**本地投影状态文件**（.runtime，generator 维护），门禁只读本地态——**PG 宕机也能抓私改**；执法走既有 registry_yaml_parse_gate 扩展（净零，不新增 gate 文件） |
| ③ | 读端容灾 | PG 宕机不阻塞施工 | 读端**永不触 PG**（这是投影架构的第一红利：11 个读端零代码改动、零新增故障面）；写路径宕机降级=outbox 排队（wave-2），登记延后但不丢 |

**为什么是这个形态**（对标锚，详见 §8③）：Argo CD 把"期望态(Git) vs 活动态(集群)"diff 出 OutOfSync 再 selfHeal 回滚（argo-cd.readthedocs.io，Diff Strategies）；Terraform 用 `plan -refresh-only` 做只读漂移探测、`apply -refresh-only` 显式吸收带外变更（developer.hashicorp.com）。本设计同构：**PG=期望态、YAML=活动态、生成器=sync、漂移检测=OutOfSync 探针、再生成=selfHeal**——但方向相反于 GitOps：我们的"期望态"在数据库不在 git，git 里的 YAML 只是读缓存，因此**私改 YAML 永远输**（PG wins），这与事故根因"整文件覆盖拉锯"正好构成制度性终结。

---

## 1. 矿址现状（调查事实基础）

### 1.1 文件解剖（2026-09-23 盘面）

`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`，44,965 行，UTF-8/LF。四段结构：

| 段 | 行号锚 | 规模 | 语义 |
|----|--------|------|------|
| 头部元数据 | L1-12 | 9 键 | schema_version/module_id/ttl/doc_type/title/status/version/date/summary（手工散文） |
| `capabilities:` | L13 | **378 条**（≈5,000 行） | 能力索引：capability_id/aliases(374)/description(378)/canonical_override(270)/integrity_anchors(105)/duplicates_manual(7) 等 |
| `creation_tokens:` | L5018 | **9,848 条**（≈39,900 行） | 建档 token：file(9848)/token(9846)/created_by(9842)/capability(9830)/merge_evaluation(471)/note(57)/blueprint_id(4) |
| `di_seam_exemptions` | L44965 | 恒 `[]` | 3 个读端、0 个写端；registry_yaml_parse_gate:162 断言其必须存在且居末位 |

**排序现状：两段全部无序**（capabilities 首三条 mining_sop/data_ops_sop/tdm_consumption_policy；creation_tokens 按历史插入锚点聚簇）——条目顺序=插入史，不是任何规范序。

### 1.2 数据质量发现（回填清洗清单，wave-0 输入）

1. **身份口径分歧实证**：W1 验收用 `grep -c "^- file:"`=9,841，语义解析（yaml.safe_load 后含 `file` 键的条目）=**9,848**，差 7 条=首字段非 file 的异形条目。投影生成器必须定**唯一语义口径**（含 file 键即条目），杜绝 grep 口径回归。
2. **缺字段脏数据**：2 条无 `token`、6 条无 `created_by`、18 条无 `capability`——复合身份 (file, token) 下 token 缺失退化为单键。回填时保留原样+生成清洗清单呈报，**不在回填器里静默补值**。
3. **多 token 文件**：9,744 个唯一 file 中 **101 个持多条 token**——复合键 (file,token) 必要性的盘面实证（与合并器 W2 热修判据一致，`scripts/governance/commit_queue_landing.py:300` `_merge_entry_identity`）。
4. **capabilities 段异形遗留字段**：outputs(1)/canonical_file(5)/name(4)/module_id(3)/name_zh(4)/domain/maturity/blueprint_id(各1)/内嵌 creation_tokens(1)——回填进 PG 的 `extra_attributes`（jsonb），渲染时原样保序输出，不做语义迁移。

### 1.3 读端全景（普查结论，子代理全量扫描）

**11 个真实代码读端，全部读本地 YAML 文件，零 PG 依赖**：

| 读端 | 段 | 缓存 | 容错 | 形态 |
|------|----|------|------|------|
| capability_lookup.py:485 | capabilities+内嵌tokens | 实例级（进程内一次） | fail-closed（缺失 raise） | 每次门禁新实例 |
| create_guard.py:573 | creation_tokens | 无（撕裂读重试3×0.3s） | fail-closed | commit 进程内 |
| registry_yaml_parse_gate.py:40 | 全文结构 | 无 | 结构破坏 fail-closed | commit 进程内 |
| ssot_redefinition_gate.py:126 | capabilities | 无 | fail-closed（staged 修复豁免） | commit 进程内 |
| batch_creation_tokens.py:111 | creation_tokens | 无 | 解析失败=问题本体 | CLI |
| scaffold.py:1245 | creation_tokens | 无 | fail-open（commit 时 create_guard 兜底） | CLI |
| architecture_health_dashboard.py:508 | capabilities | 无 | fail-open | CLI |
| generate_project_depgraph.py:3067 | di_seam_exemptions | 无 | fail-open | CLI |
| algo_flow_reverse_orphan_reconciler.py:366 | creation_tokens | 无 | fail-closed（RetireRefused） | gateway 常驻 |
| agents_cheatsheet_drift_reconciler.py:362 | 行计数（正则） | 无 | fail-visible warn | gateway 常驻 |
| metric_count_drift_reconciler.py:216 | 文本扫描 | 无 | fail-open | gateway 常驻 |

外加 golden hash 保护（validate_rules_integrity.py:122，critical=True，防删 registry 锁死 commit 的 DoS）。**非读端**引用：file_utils.py:410 热文件 CAS 清单+`/_registry/catalogs/` 净删守卫(:431)、detect_git_dangerous 排除表、secret_hardcode 豁免集。**设计含义**：所有读端进程形态都是"每笔提交新进程/CLI 即起即弃"，**不存在需要失效通知的常驻缓存**——投影只需保证"写盘原子+读端下次进程看到新内容"，W9 式 mtime 热加载对本文件读端无必要。

### 1.4 写端全景（迁移时必须逐一改道的清单）

1. `batch_creation_tokens.py`（登记正门）：锚点式**纯插入**（段内 `capability:` 锚行后，:305 insert_block）+写前"基底 vs HEAD"缺条即拒+写后守恒闸（身份=(file,token)，:231）+CAS 5 次重试。
2. `scaffold.py:1245-1287`：新模块脚手架联动登记（复用 insert_block，fail-open）。
3. `algo_flow_reverse_orphan_reconciler.py:488`：孤儿条目退役（retire=合法净删，W4b 守卫需 allow_mass_edit=True——越界登记在案的 P0 接线）。
4. `commit_queue_landing.py` 注册表族三向合并器（W2，:221/:300）：队列落地时对 `/_registry/catalogs/*.yaml` 条目级三向合并，复合键=首标量|token。
5. W4b 质量守卫（file_utils.py:592）：`/_registry/catalogs/` 下删除行数 >0.5% 且未显式 `allow_mass_edit=True` → 拒写。
6. 外科脚本先例：W1 重建直改（e3de925d0b）等一次性通道。

### 1.5 保护网现状（投影化后的角色重定义，§3.5 详述）

- **golden hash**（validate_rules_integrity.py，`rules_integrity_db.json` 已 track 本文件，critical=True）：无阻断式 gate 调用 check()，执法面=gateway flush 前**自动 fold**（git_commit_gateway.py:2004 `_fold_rules_integrity_into_batch`，合法变更自动折入批提交）+MISSING 防删除 DoS。
- REGISTRY-MASS-DELETION gate（提交面身份消失检测，W3 机械化退役验证）。
- registry_yaml_parse_gate（staged 结构校验：根键判重/creation_tokens 为 list/di_seam_exemptions 居末）。
- SSOT-REDEFINITION gate（注册表缺失/解析失败 fail-closed 阻断全项目提交，staged 修复豁免）。
- safe_write_text CAS 热文件强制 read-before-write + 写后回读（file_utils.py:522）。

### 1.6 可继承的仓内正典（不发明新轮子）

| 正典 | 位置 | 本设计如何用 |
|------|------|------------|
| 幂等写三件套 | generate_gate_registry.py（atomic_write_if_changed+volatile 行跳写）；check_registry_consistency.py:715（safe_write CAS+段手术）；d5 generators/_common.py:56（idempotent_timestamp，有 pre-commit 门禁禁 datetime.now） | 生成器用**零 volatile 字段**方案（比 volatile 跳写更强：同账本→同字节，连比对豁免都不需要） |
| dump 参数仓约定 | `allow_unicode=True, default_flow_style=False, sort_keys=False, width=100~120`（77/105/80 处统计） | 渲染器不直接 yaml.dump 整文件（下述禁令），条目行用**模板直出**+safe_load 回读断言 |
| 整文件 dump 假 diff 禁令 | auto_sync_all_registries.py:317（"禁 yaml.dump 整写本册：load→dump round-trip 12 处折行差异造假 diff"） | 该禁令针对"手工格式化文件"；cutover 后格式归生成器所有，round-trip 天然稳定——但仍用模板直出，把引号/折行决定权收进渲染器 |
| generator_registry.yaml 编排 | `input_sources: db:` 前缀机制已在册（d5 投影族 21 脚本登记在案） | 生成器挂 `db:` 前缀输入源登记，reconcile_generators 直接管 |
| DB-SSOT 先例 | generate_project_depgraph.py:5202（YAML 输出已标 DEPRECATED，DB is now the SSoT）；flowthrough_verifier.py:348（`DatabaseService().get_depgraph_conn(read_only=True)` 只读连接） | 生成器读 PG 走 DatabaseService 只读连接（禁裸 psycopg2） |
| CAS 写 DB→YAML 先例 | dsr_recalc_backfill.py:219（safe_write_text 产 YAML 报告） | 写盘通道照抄 |
| ROOR 双介质标记 | `format: postgresql` + by_medium 机判（check_registry_consistency --refresh-summary） | cutover 时 REG-CAPCAN-001 改 format: postgresql，YAML physical_path 改标"generated projection" |

---

## 2. 设计①：投影生成器（ledger → YAML 单向输出）

### 2.1 定位与不变量

```
PG ledger（SSOT，车道乙 02 定 schema） ──只读连接──> render() ──纯函数──> 字节流
                                                              │
                                              与盘上 diff → 无差异=结束（幂等）
                                                              │ 有差异
                                              safe_write_text CAS（newline='\n'）→ 写后四自检
```

五条不变量（施工验收判据）：
1. **单向**：数据只从 PG 流向 YAML。任何从 YAML 流回 PG 的路径（除一次性 backfill）都是 bug。
2. **纯函数**：`render(ledger_state)` 无时钟、无随机、无环境依赖——**零 volatile 字段**（generated_at 之类一律不写进文件；生成元数据记 PG 审计与 .runtime 状态文件）。同账本状态重跑一亿次，字节全同。
3. **单写者**：cutover 后生成器是本文件唯一合法写者。禁手工 Edit/Write；登记走意图 API（车道乙）→ PG → 生成器。
4. **全量重打**：不做增量 patch。9,848 条全量渲染 <1s 量级，正确性 > 聪明（增量同步是漂移温床，KISS 裁定）。
5. **读端契约不变**：输出的 YAML 必须让 §1.3 全部 11 个读端零改动照常工作（四段结构、di_seam_exemptions 居末、creation_tokens 为 list——registry_yaml_parse_gate 的结构断言全保）。

### 2.2 输入契约（呈车道乙的需求单，02 矿对齐点）

生成器对 PG 账本的最低字段需求（表命名归乙，字段语义必须覆盖）：

| 逻辑实体 | 必需字段 | 备注 |
|---------|---------|------|
| token 条目行 | file, token, created_by, capability, merge_evaluation, note, blueprint_id, **extra_attributes(jsonb)**, created_at, created_by_session, entry_revision(CAS), **retired_at/retired_by（软删，审计 tombstone）** | §1.2 脏数据行原样迁入；extra 承接异形字段零丢失 |
| capability 行 | capability_id, aliases(list), description, canonical_override, duplicates_manual, removed_duplicates_manual, integrity_anchors, **extra_attributes(jsonb)**, revision | 378 行全迁；`duplicates/removed_duplicates` 派生字段照旧由 lookup 派生，不入账本（对齐 v1.1.0 治本原则） |
| 文件元行（单行） | schema_version, module_id, ttl, doc_type, title, status, version, date, summary | 头部散文进 PG，渲染时 verbatim 输出 |
| di_seam_exemptions | meta 行（恒空 list 也入账本，渲染居末） | 保 parse gate 断言语义 |
| **账本 revision 计数器** | 单调递增（每次意图提交 +1） | 漂移检测 staleness 判据（§3.1）+投影状态文件记录 |

**访问方式**：`DatabaseService` 只读连接（flowthrough_verifier 先例），禁裸 psycopg2/裸 SQL 散落（宪法 §9.1）。

### 2.3 确定性规范（字节级，施工验收逐条可测）

1. **排序**：creation_tokens 按 `(file, token or "")` 字节序（locale 无关，`sorted(key=str.encode)` 语义）；capabilities 按 `capability_id` 字节序。**与合并器身份键 (file,token) 同构**——cutover 后本文件退出三向合并器作用域（单写者化，见 §2.7），排序与身份不再有第二套口径。
2. **条目行模板直出**：字段定序 `file → token → created_by → capability → merge_evaluation → note → blueprint_id → extra_attributes 展开（键序字典序）`。标量引号规则：含特殊字符（`:`/`#`/前导空格/中文逗号句号不触发，仅 YAML 保留字）才加双引号，引号转义照 batch_creation_tokens `_yaml_quote` 语义（:115）；无特殊字符裸输出（与现文件主流形态一致，diff 噪音最小）。
3. **行尾/编码**：UTF-8 无 BOM、`newline='\n'`（.gitattributes 钉 LF，W1 实弹教训：前任写盘落 CRLF 被行尾口径打回）、文件尾单换行。
4. **头部**：元行 verbatim + 无任何生成时间戳。`version/date` 语义=账本 schema 版本（意图提交时在 PG 内 bump，渲染跟随）。
5. **渲染自校验（写盘前）**：`yaml.safe_load(rendered)` 回读 → 与输入账本行做**语义等值断言**（条目键集相等+字段级相等+段序断言+di_seam_exemptions 居末）→ 不等即拒写（fail-safe=不写，batch_creation_tokens 写后自检同款哲学）。

### 2.4 写盘管线

1. 读盘上现文件 → `content_sha256`（文本口径，W1 教训：CAS base 必须用 content_sha256 文本读，裸 rb 必假警报）作为 `expected_base_sha256`。
2. 与渲染结果比对：**字节相同 → 零写退出**（幂等重打的主形态）。
3. 有差异 → `safe_write_text(target, rendered, expected_base_sha256=…, newline='\n', allow_mass_edit=True)`。**allow_mass_edit=True 是生成器的常驻显式旗**（退役日整批净删是合法形态；W4b 守卫审计 jsonl 自动留痕 `registry_mass_edit_allowed`）。生成器自己先算净增/净删条目数写运行报告，守卫不是它该绕的东西而是第二道网。
4. 写后四自检（任一失败 → 告警行+保持现状，绝不重试覆写）：safe_load 回读 ✓ / 条目键集=账本键集 ✓ / 探针抽查（gateaudit=94 等既有探针机制沿用）✓ / 投影状态文件更新 ✓。
5. CAS 冲突（写窗口被抢——cutover 后理论只剩生成器自身并发）：退避重试 3 次 → 死信告警，**人工分诊**（两个生成器并发本身就是违规信号）。

### 2.5 幂等性与登记

- **幂等判据**：连续两次运行，第二次零写盘（字节比对）+零审计行。施工验收第一条。
- **登记**：generator_registry.yaml 增条目，`input_sources: [db:<账本表>]`（`db:` 前缀机制现成）、`output_globs: [capability_canonical_file_registry.yaml]`；ROOR 条目 cutover 时同步（format: postgresql + 投影标注 + counting_rule 改机判）。**防循环触发**：生成器自身写盘不再触发 reconciler 链对账本的反向登记（generator_registry 在册禁登清单语义照抄）。

### 2.6 触发设计（永久系统四要素对齐）

| 触发源 | 机制 | 语义 |
|--------|------|------|
| 意图 API 后置钩子 | 每笔 PG 意图提交事务成功后同步调生成器（车道乙 API 内联或紧后事件） | 主路径，新鲜度窗口≈秒级；生成失败→PG 已提交但投影陈旧，靠下行兜底 |
| belt daemon 兜底 | 既有 daemon 循环内加 staleness 探针：账本 revision > 投影状态文件记录的 revision → 触发再生成；PG 不可达→记降级观察行 | 自动维护；**事件驱动判定+既有循环**，非新增 cron/sleep-loop（宪法 §9.3 对齐，daemon 本体 W5 已复活） |
| 手动 | `--check`（零写）/ `--render`（写）CLI | 运维与施工验收通道 |

### 2.7 与既有机制的四笔交接（呈总图汇编）

1. **三向合并器单写者化**：cutover 后本文件退出 `is_registry_mergeable` 作用域（commit_queue_landing.py:208 前缀族判定给 capability_canonical 单文件开白名单排除），整文件语义恢复安全——因为只剩一个写者，W2 三向合并的历史使命对该文件终结。**合并器本体保留**，服务其余 70+ 册。
2. **batch_creation_tokens / scaffold 改道**：登记 CLI 改为意图 API client（写 PG），YAML 更新由生成器完成。过渡期（§5 影子期）两路并存时，batch_creation_tokens 的写前"基底 vs HEAD"守恒闸天然兼容（它只要求盘上不缺条目，生成器重打不会缺）。
3. **W4b 守卫与 golden hash**：§3.5。
4. **REGISTRY-MASS-DELETION gate**：投影提交里的净删=PG 侧合法退役的投影，W3 机械退役验证（被删条目路径盘上+HEAD 双不存在）语义原样适用，零改动。

---

## 3. 设计②：漂移检测（重生成 + diff，人工私改立即现形）

### 3.1 漂移定义与四象限判别

**漂移 ≡ 盘上 YAML ≠ render(当前 PG 账本)**。但"≠"有三种成因，处置完全不同，必须判别：

**判别机制 = 本地投影状态文件** `.runtime/registry_projection_state.json`（生成器每次成功写盘后原子更新，safe_write CAS）：

```json
{"content_sha256": "<最后成功渲染字节流哈希>", "ledger_revision": 12345,
 "generated_at": "...", "entry_counts": {"tokens": 9848, "capabilities": 378}}
```

四象限（R=render(PG) 哈希，S=状态文件哈希，D=盘上文件哈希）：

| 象限 | 判别 | 成因 | 处置 |
|------|------|------|------|
| 干净 | D=S=R | 无 | 通过 |
| **私改** | S=R 且 D≠S | 有人手工编辑了 YAML（PG 没动） | **告警+自动再生成**（PG wins）；私改 diff 快照留档 `.runtime/gate_audit/` 供取证；若私改含真实新登记→死信分诊（登记必须补走意图 API） |
| 陈旧 | D=S 且 R≠S | PG 前进、生成器还没跑（正常竞态窗口） | 静默/低噪再生成（主路径常态） |
| 双向冲突 | D≠S 且 R≠S | 私改与 PG 前进叠加 | 再生成后复检；仍≠→死信告警人工分诊（私改证据先行留档） |

**PG 宕机特例**：R 取不到 → 只比 D vs S。S 是上次成功渲染的锚，**私改照样现形**（这就是把判别真源放本地而不是 PG 的原因——检测能力不随 PG 存活而死亡）；"PG 前进未投影"类漂移在宕机期间不可判，daemon 记降级观察行，PG 复活后补扫。

### 3.2 检测点三层（纵深，全部复用既有通道，净零）

| 层 | 载体 | 语义 | PG 宕机行为 |
|----|------|------|------------|
| **提交时（执法层）** | **registry_yaml_parse_gate 扩展**（own-scope：仅本文件在 staged 清单才触发；不新增 gate 文件，符合事故 DISPATCH 净零红线与宪法 w5_1） | staged blob sha ≠ 状态文件 S → 阻断，文案指路"此文件是 PG 账本投影：私改无效，请走意图 API 登记+生成器重打"；生成器自身提交天然匹配 S=通过 | 读不到状态文件/状态损坏 → **fail-open**（放行+告警行）——PG 死时施工不阻塞，靠 daemon 层兜底抓 |
| **常驻观测层** | belt daemon 循环内探针（复用 W5 已建的 `record_registry_drift` 记账 kind——DISPATCH W5③ 当时就是给本设计预留的通道） | 周期跑 §3.1 四象限判别；私改/冲突象限 → 堵点本告警行（带 ±条目数） | PG 不可达 → D vs S 降级判别+降级观察行 |
| **写后自证层** | 意图 API 后置钩子（§2.6） | 生成器写后回读四自检即实时漂移自证；失败即告警 | API 层 PG 事务失败本就不产新账本状态，无漂移窗口 |

**为什么执法层不直接调 render(PG)**：门禁进程拉 PG 连接+渲染器=提交热路径新增 PG 依赖，直接违反支柱③。门禁只读本地两个便宜东西（staged blob + 状态文件），毫秒级、零网络。

### 3.3 处置 playbook（自动，无人工常态参与）

- 私改象限：`git checkout` 不用（会吃掉他人 staged）——直接**用渲染结果 safe_write CAS 覆写**（生成器本来就会这么干）；差异先存 `.runtime/gate_audit/registry_drift_<ts>.diff`。Owner 终局四类事里没有"注册表对账"——此环必须全自动，自审闸通过（§8）。
- 陈旧象限：再生成，daemon 记账行（±N 增量，喂 registry_drift kind 的身份增减量字段）。
- 冲突象限：唯一出人工的死信通道，预期频次≈0（私改在提交层已被拦，能落到冲突象限的只剩绕过门禁的直改）。

### 3.4 golden hash 的角色重定义（零改动裁定）

现状：gateway flush 前**自动 fold** 把合法变更折进 rules_integrity_db.json（git_commit_gateway.py:2004）——生成器重打属合法变更，**自动 fold 天然兼容，不会假红**；手工私改被 §3.2 执法层拦在提交之前，根本走不到 fold。golden hash 对本文件的增量价值收敛为 **MISSING/DoS 保护**（防删 registry 锁死全项目 commit，validate_rules_integrity.py:122 注释原文）。**裁定：保留现状零改动**（fold 自动化+MISSING 保护仍有真实价值），一季观察后再评估是否收窄——写入呈 Owner 决策点 #4。

---

## 4. 设计③：读端容灾（PG 宕机不阻塞施工）

### 4.1 核心原则：读端永不触 PG

YAML 投影就是读端容灾本身——**11 个读端（§1.3）继续读本地文件，一行代码不改**。PG 在架构里只有两个角色：账本真源（写路径）+渲染输入（生成器）。读路径对 PG 的依赖严格为零，这不是"宕机降级方案"而是架构不变量。

### 4.2 PG 宕机时的施工影响面（逐项）

| 施工动作 | 宕机时 | 依据 |
|---------|--------|------|
| 改代码/改文档/提交 | **完全不受影响** | 全部 commit 门禁（create_guard/ssot/parse_gate/mass_deletion…）只读本地 YAML 与 staged blob |
| 新建 .py 后 CREATE-GUARD | **受影响**：token 无法登记（意图 API 不可达）→ 新文件提交被 create_guard fail-closed 拦 | 唯一真实卡点，下行 §4.3 解 |
| capability_lookup 反查 | 不受影响（读 YAML+磁盘扫描） | §1.3 |
| 门禁注册表读取 | 不受影响 | §1.3 |
| 生成器 | 跳过（PG 连不上→零写退出+降级观察行）；**绝不阻塞任何调用方** | fail-open 纪律 |

### 4.3 写路径宕机降级（wave-2 建议，呈 Owner 决策点 #6）

意图 API 本地 outbox：PG 不可达时意图行落 `.runtime/sessions/<sid>/outbox/`（append-only jsonl，含幂等键），daemon 检测 PG 复活后按序 drain 重放（幂等键去重），随后生成器重打。语义=**登记延后但不丢、不乱序**。wave-1 先接受"登记等待 PG 恢复"（登记是低频动作，宕机窗口罕见；卡新文件提交时临时把文件挪后批提交即可）。**反面裁定：不在 outbox 存在之前给 create_guard 加 fail-open 豁免**——那会在 PG 宕机时开出"未登记文件入库"的口子，防呆倒退。

### 4.4 YAML 本体灾难恢复阶梯

1. **盘上被删/损坏**：`git show HEAD:<path>` 恢复（git 史即终极本地备份，SSOT gate 现有 staged 修复豁免通道原样可用）。
2. git 也不可用（理论）：PG 可用 → 生成器直接重打（账本在，投影可再生——**这正是投影架构的抗灾红利：YAML 任何时刻可全量重建**）。
3. 双死（PG+git）：超出本设计层级（全仓灾难），不设防。

### 4.5 新鲜度窗口

意图提交→生成器重打之间秒级窗口内，读端看到的是上一态投影：CREATE-GUARD 可能暂不见刚登记的 token（新文件提交被拦一轮）。处置：意图 API 后置钩子把窗口压到秒级；belt daemon staleness 探针兜底（revision 落后即告警+补渲染）。**不加读端缓存、不做读端直连 PG 查询回退**（单读制品原则，防两套读态）。

---

## 5. 切换 sketch（供施工总图汇编排序，非本车道施工）

```
W1 回填：YAML → PG（9,848+378+元行；语义对账验收=键集相等+字段级相等；脏数据清单另列呈报不静默修）
W2 生成器本体：render+自校验+CAS 写盘+--check/--render+状态文件（纯新增脚本，零既有行为变更）
W3 语义双跑（影子期）：生成器 --check 每日跑（daemon 或手动），判据=连续 3 天零"私改/冲突"象限+渲染语义等值
W4 cutover 单批：生成器全量重写 YAML（排序+格式归一，一次性行序噪音 diff）+ 退出合并器白名单 + ROOR 换标 + 登记 generator_registry
    回滚点=cutover 前一 commit（revert 即回手工态；PG 侧账本保留不回滚，只停用渲染）
W5 执法翻转：registry_yaml_parse_gate 扩展 arm（staged≠S 阻断）+ belt daemon 探针启用 + 意图 API 成为登记唯一正门（batch_creation_tokens/scaffold 改道）
W6 wave-2（可选）：outbox 宕机降级；golden hash 收窄评估
```

**时序硬约束**：W5 执法翻转必须晚于队列排空（在途队列项携带旧基底快照，cutover 后落地会与投影态冲突——三向合并器对本文件退出后，旧快照整文件落地会覆盖投影，故 cutover 前确认该文件无在途队列项，DISPATCH 广播里各线 requeue 完成后执行）。

---

## 6. 呈 Owner 决策点（带推荐，签字窗用）

| # | 决策 | 推荐 | 理由一句话 |
|---|------|------|-----------|
| 1 | capabilities 段（378 行散文索引）是否同波迁 PG | **同波全量迁**（账本加 capability 表+extra jsonb） | 终局直上不要中间态（Owner 既定）；capabilities 同文件同样吃并发覆盖风险，半迁=保留半个人工写入口 |
| 2 | §1.2 脏数据 26 条（2 无 token/6 无 created_by/18 无 capability） | **回填原样迁+清洗清单呈报，Owner 逐类批后 PG 内修** | 机械判定门铁律：缺失是真数据不是废数据，修法需 Owner 过目；静默补值违反宪法 §9 精神 |
| 3 | 执法翻转（W5）时点 | **影子期 3 天零私改/冲突象限+红蓝一轮后 arm** | 与事故 DISPATCH 收口判据同构（两轮零+红蓝） |
| 4 | golden hash 条目处置 | **保留现状零改动，季度合并审计再评估** | 自动 fold 已兼容，MISSING/DoS 保护仍有价值；现在动它=无收益风险 |
| 5 | ROOR 内收：REG-GEN-001（creation_tokens 子集视图）并入 REG-CAPCAN-001 | **cutover 时并条+entry_count 全部改机判** | w5_1 同真源可派生→必并；现登记 378/5520 双双陈旧（实况 378/9848）=手工计数漂移活证 |
| 6 | PG 宕机登记 outbox | **wave-2 建**，wave-1 接受登记等待 | 低频场景不预建中间件；但 create_guard 禁加 fail-open 豁免（§4.3） |

---

## 7. 净零核算（宪法 §4 对齐）

- **新增**：生成器脚本 1 个（render/check/render CLI）+ .runtime 状态文件（非 git 资产）。无新增注册表、无新增 gate 文件（执法=registry_yaml_parse_gate 扩展）、无新增记账 kind（registry_drift W5 已建）。
- **替代/退役**：本文件的手工维护语义（退役）；batch_creation_tokens/scaffold 的直写 YAML 路径（改道意图 API，函数体降级为 client）；三向合并器对本文件的作用域（退出）；ROOR REG-GEN-001（并入）。
- **禁登清单遵守**：生成器写 YAML 属"真源写入方"吗？不是——账本（PG）才是真源，生成器是投影器，按 generator_registry 在册语义登记为 `db:` 输入投影（d5 投影族同款），不触发防循环禁登。

## 8. 挖矿日志（SOP §7 纪律，六向寻路+闸记录）

**矿脉母节点**：YAML 投影生成器设计（账本→YAML 单向/漂移检测/读端容灾）。

| 向 | 动作 | 判定 | 关键产出 |
|----|------|------|---------|
| ①上游 | 写端全量反查（§1.4 六通道）+事故 DISPATCH/Lane A/B 越界登记全读 | signal | 合并器复合键身份、W4b 守卫、registry_drift 预留 kind、W5 daemon 复活——四件既有设施直接成为本设计地基 |
| ②下游 | 29 文件引用全量普查（子代理，含 tests/docs/_working）| signal | 11 真读端表+fail-open/closed 两极图谱+di_seam_exemptions 三读零写+golden hash 无阻断 gate |
| ③机制（全网） | Argo CD diff/selfHeal、Terraform plan -refresh-only 漂移语义检索；承接主会话 67 源对标（etcd 单调 revision→账本 revision 计数器；Apollo 编辑/发布分离→意图/投影分离） | signal | §0 对标锚：[Argo CD Diff Strategies](https://argo-cd.readthedocs.io)（Argo 项目/CNCF，2026 在线文档）；[Terraform health assessments/drift](https://developer.hashicorp.com/terraform/tutorials/cloud/health)、[refresh](https://developer.hashicorp.com/terraform/language/state/refresh)（HashiCorp，2026 在线文档） |
| ④后端 | 幂等三件套/整写假 diff 禁令/dump 参数统计/CAS 全体精读（file_utils.py:522-640） | signal | §1.6 正典表；safe_write_text 契约逐参核（allow_mass_edit/newline/回读校验） |
| ⑤前端 | 仪表盘只读 counts（architecture_health_dashboard），无前端诉求 | 查无 | 本设计零前端面 |
| ⑥数据字段 | 双段字段普查+缺字段/异形/多 token/排序四项机械盘点（yaml.safe_load 全量解析） | signal | §1.1/§1.2 全部计数；9841 vs 9848 口径分歧 |

**防噪音四闸过闸记录**：③向两条外部引文均 URL+发布方在案（来源可溯闸 ✓）；67 源对标主会话已交叉验证（待其归档文互证，本矿单引用处标"承接"）；无 A 股适配问题（纯治理域）；可验证性=§2.3/§2.5 全部给出机械验收判据（可回测闸 ✓）。
**noise 轮**：零（六向全 signal 或查无，无受阻轮）。
**长尾矿脉（明示未挖，防漏）**：①其余 70+ 册的分批迁移排序与优先级（归总图/车道甲盘点矿覆盖）；②gate_registry own_scope 机生字段与投影 gate 扩展的登记联动（施工时顺手项）；③tests/ 全面 fixture 改造面（test_capability_lookup 等 15 测试文件的注册表 fixture 换账本 seed——施工波次内估，非设计矿）；④意图 API 与生成器的事务边界细节（同窗 PG 提交成功但渲染进程崩——已由 daemon staleness 兜底，API 侧重试语义归车道乙矿）。
**旁支观察（不越界处置，移交）**：`scripts/governance/commit_queue_landing.py.tmp.21732.*` ×4 残尸（写盘崩溃遗留，归 .runtime 卫生通道/其 Owner 清理）；ROOR entry_count 双陈旧（§6#5 并条时顺修）。
**挖后自审闸（§6 判据）**：终局全貌=Owner 只做四类事，本设计把"注册表手工编辑/私改仲裁/计数对账"三类人工环节全部消灭（一票放行 ✓）；过度工程自查——拒绝了增量同步/读端缓存/读端直连 PG/新增独立 gate 四个更重的选项，全量重打+本地状态文件是满足三支柱的最小机制（成本实算 ✓）。三态出口=**施工**（待总图 Owner 签字）。

## 9. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-23 | 1.0.0 | 初稿：车道丙挖矿交付（生成器/漂移检测/读端容灾三设计+切换 sketch+六决策点） |
