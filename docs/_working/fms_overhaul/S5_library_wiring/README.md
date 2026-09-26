---
ttl: task_bound
title: "S5 图书馆接线挖矿簿：successor_of 墓碑 + lookup 单口立法 + 三层对账"
created: 2026-09-27
sid: st-fms-chief-20260927
lane: S5
status: 挖干（唯二外部依赖=Owner 增枝批文[流程固有门位]与 st-p1b 落地后 reconciler 挂接[已给绕行]）
---

# S5 图书馆接线挖矿簿

## ① 职责一句话

给 lib_assets 总账加 `successor_of` 墓碑去向指针并全线接通（DDL→馆员→lookup→馆页），立"路径禁凭记忆必经 lookup"宪法条款，另立总账↔生成视图↔盘面三层一致性检查器（独立新文件，避开 st-p1b 三件）。

## ② 现状实测（2026-09-27 本线实测，含 PG 只读直查）

### 2.1 总账真实状态（PG depgraph 库，只读查询实测）

- `lib_assets` 总行数 **44,773**；状态分布：`active=34,217 / archived=10,462 / deceased=94`，其余 4 个状态（stale/orphan/ghost/blind）**零行**（枚举有、账面未用）。
- 实库列=**20 列**，与 DDL 常量逐列一致：asset_id, kind, home, family_id, fingerprint_sha256, fingerprint_aux, built_at, generation, status, owner_domain, retention_class, disposition_authority, registered_at, registered_by, title, one_liner, ai_contract, tags, ext, potential_consumers。DDL 真源=`src/zephyr/library/ledger_schema.py:66-89`（`_SQL_ENSURE_ASSETS`）。
- **无 successor_of 列**（本线待增）。

### 2.2 馆页三快照口径漂移破案（27,864 / 27,949 / 28,454 之谜）

- HEAD 版 `docs/library/INDEX.md`：在编 34,630，代码馆 **28,454**；工作区版（已再生成未提交，`git status` 7 页 M）：在编 34,217，代码馆 **27,949**；PG 实时 active=34,217 **与工作区精确一致**。总筹测得的"INDEX 27,864 vs code.md 27,949"= 更早一次工作区快照（INDEX 与馆页属不同再生成时点）。
- 漂移机制：`generate()` 单次运行内自洽（先写七馆页 L119-122、**后**写 INDEX.md L141，馆序 code 第一）；跨运行/半途失败（馆页写完、INDEX 未写之间的崩溃窗）即产生页间互斥漂移。馆页是 git 跟踪文件但再生成不自动提交（reconciler 量不变式 L8"提交仍走人工批"），多会话各读各的快照即漂。
- **附带发现（计数失真 bug）**：`scripts/governance/generators/generate_library_index.py:88` 写"条目数（本页列出）：{len(rows)}"，但 L94 实际只写 `rows[:300]`；且 L96 截断提示条件 `total > len(rows)` 恒 False（调用处 L122 传 `items` 与 `len(items)`，二者恒等）——"本页列出"报的是馆内总数、"仅列前 N 条"提示永不触发。code.md 实测正文表格约 300 数据行，与声明 27,949 严重不符。此 bug 归 S4 计数回填机械化或本线 tri-checker 一并断言。

### 2.3 .runtime 临时件入账实测（任务 5 核心证据）

- `home LIKE '.runtime/%'` 共 **28 条，全部 status=active**。来源：fs_collector 的 `_SKIP_DIRS` 现已跳 `.runtime`（`src/zephyr/library/collectors/fs_collector.py:33-50`），即现行采集**不读** .runtime——这 28 条是早期版本采集/手工登记残留，upsert 语义下永无人把它们翻状态。
- 矛盾实证：`FILE:.runtime/audit/archive_log.jsonl` status=**active** 但 disposition_authority 已填自裁批文全文（死亡证明签了、状态没翻）——authority 与 status 脱节的活案例。
- lookup 实测：`python -m zephyr.library.lookup algo_flow_translation_sync_runs --no-alias` 命中该 .runtime/audit 临时件并照常输出——临时区件污染查询口。
- deceased 94 条中 **7 条无 disposition_authority**（死亡无证明，实测 `DECEASED_NO_AUTHORITY=7`）。
- deceased 样本显示 disposition_authority 现存内容=自裁批文长文本，**无一是后继指针**——墓碑"去了哪"信息现为零承载。

## ③ 六向台账

### 3.1 真源

| 平面 | 真源 | 证据 |
|---|---|---|
| 总账（唯一事实） | PG depgraph 库 `lib_assets`/`lib_events` 两表 | `src/zephyr/library/ledger_schema.py:66-102` |
| DDL 常量 | `ledger_schema.py`（CREATE TABLE IF NOT EXISTS，幂等） | 同上 L66-89 |
| 字段语义 | `docs/_working/ultimate_library/08_field_dictionary_v0_1.md`（冻结 v1.0，v1.1 增枝 potential_consumers；§6 L110：字段新增=增枝制） | 08 词典 L41/L110 |
| 生成视图（非真源） | `docs/library/INDEX.md` + 七馆页，页头自带"生成视图…真源在资产本体"声明 | `generate_library_index.py:86`，页 frontmatter |
| 盘面 | 仓库工作区（fs_collector 白名单 8 根：src/scripts/tests/docs/config/data/schemas/architecture_model） | `fs_collector.py:64-73` |

### 3.2 写者

- **唯一写路径=Librarian**：`act()`（`src/zephyr/library/librarian.py:119-193`，事件与状态同事务）+ `register_batch()`（L195-237，采集器批量入账）。NO-BARE-SQL 全常量。
- 触发方：① library_regen_reconciler（post-commit 事件触发，**st-p1b 在改，避让**）调 collect_all+ingest_all；② `generate_library_index.py:142-155` 自身以 act(audit/register) 把馆页自登记入账；③ 人工处置链（delete 必带死亡证明 `validate_action`，`ledger_schema.py:209-223`）。
- 采集器 6 件（fs/pg/ch/schtasks/mcp/logs）只读采集，经 ingest_all 才落库（`collectors/__init__.py`）。
- DDL 写通道：`Librarian.ensure_schema()`（`librarian.py:112-117`）是唯一 DDL 执行点；连接必经 `get_depgraph_pg_connection()`（`src/zephyr/governance/depgraph_schema.py:1598`），默认 read_only=True（depgraph_reader 只读角色，技术阻断写入），写角色仅白名单脚本可用（DEPGRAPH-WRITE-PATH 门，`src/zephyr/gov_enforcement/commit_gates/depgraph_write_path_gate.py`，白名单 `_WHITELIST` L89-140）。

### 3.3 消费者

- `lookup_assets` API + `python -m zephyr.library.lookup` CLI（只读角色连接，`lookup.py:116`）；`zephyr.library.relations`（关系树 BFS，`relations.py:303`）；`check_library_coverage.py`（盘↔账两向）；`generate_library_index.py`（视图生成）；AI 冷启动链 AGENTS.md→INDEX→七馆页（AGENTS.md AGENTS.md §6 检索序条目）；未来 FMS-HYGIENE 门（S1）为本线账面能力的消费方。

### 3.4 漂移史

1. 27,864/27,949/28,454 三快照（§2.2 破案：跨再生成时点+半途失败窗+不自动提交）。
2. 28 条 .runtime 幽灵 active（§2.3：采集器白名单改过，账面没清）。
3. 1 条 authority 已签 status 未翻（§2.3 archive_log.jsonl）。
4. 7 条 deceased 无死亡证明（§2.3）。
5. 馆页"本页列出"计数失真 + 截断提示死代码（§2.2，`generate_library_index.py:88,96`）。
6. 历史事故在案：potential_consumers 回填 31→被 reconciler 再采集清零（`ledger_schema.py:104-106` COALESCE 注释，#410②批1）。

### 3.5 冲突面（避让图执行）

- **st-p1b-libr 三件不碰**：`src/zephyr/library/library_regen_reconciler.py`（已读 HEAD 版理解其职责：触发→采集入账→馆页重生成→调 coverage，是**刷新管线**非校验器）、`src/zephyr/governance/audit/reconciliation_registry.py`、新件 `library_new_module_reconciler.py`。
- 本线只改 `ledger_schema.py`/`lookup.py`/`librarian.py`（骨架 §五确认 st-p1b 未触碰）+ 新增文件；08 词典与 project_handbook 族/capability_canonical/module_translation 两册无涉，可改。
- AGENTS.md=受保护路径（st-gateaudit 遗产提交注明"留呈 Owner"）→ 宪法替换行走 Owner/裁定通道 + safe_write_text CAS。
- 三层检查器挂 reconciliation_registry 的动作**推迟**至 st-p1b 落地后（绕行：先独立 CLI + pre-commit 面落地）。

### 3.6 净零方案

| 新增 | 替代/合并声明 |
|---|---|
| successor_of 列 | 增枝制（08 词典 §6）非新真源；08 词典加一行只增不改语义 |
| tri-consistency 检查器 | 现三层一致性**零覆盖**（regen=刷新、coverage=盘账两向，均不做账↔视图断言），非重复建设 |
| ephemeral 标记 | **零新枚举**：复用既有 `retention_class='temp'`（08 词典 §8"临时专区持二级身份证 retention_class=temp+TTL"已立法）+ 既有 status=archived/deceased |
| 宪法 lookup 条款 | §8 L114 等长替换一行换一行，零增行 |
| 不立新门 | 墓碑/死引用执法并入 S1 的 FMS-HYGIENE 门（S5 只供账面能力），避免与 S1 重复立门 |

## ④ 施工处方

### 4.1 任务 1：successor_of 增枝 DDL 五步处方（对标 potential_consumers 先例）

先例：`docs/_working/ultimate_library/ulib3b_potential_consumers_proposal.md` §四（L33-38 五步全文）+ 执行记录 `library_final_ledger.md:89,99`（"①加列 44,028 行默认空…增枝五步全通"；时为 44,028 行，今 44,773 行）。五步=①实库 ALTER ②08 词典升版 ③登记闸（librarian）同步 ④首批回填 ⑤lookup 面+测试。**呈批不施工**（proposal L53：对话内口头不构成批文，须 Owner 勾批或裁定登记；机械判定门铁律 schema 变更不可自裁）。

**DDL 全文提案**（新文件 `scripts/governance/migrations/add_library_successor_of.py`，对标白名单先例 `scripts/governance/migrations/add_acquisition_fields.py`——该件即 superuser DDL 迁移先例，`depgraph_write_path_gate.py:102` 白名单在册）：

```sql
-- 增枝①：successor_of 墓碑去向指针（08 词典 §6 增枝制；幂等可重跑）
ALTER TABLE lib_assets ADD COLUMN IF NOT EXISTS successor_of text;
COMMENT ON COLUMN lib_assets.successor_of IS
  '墓碑去向：deceased 时指向后继资产 asset_id；两态对标 potential_consumers 纪律：NULL=未评估，''=''=确认无后继';
```

- **幂等性**：`ADD COLUMN IF NOT EXISTS` 重跑零副作用（add_acquisition_fields.py 头 INVARIANTS 同款承诺）；同时把 `ledger_schema.py:87` `_SQL_ENSURE_ASSETS` CREATE 常量补 `successor_of text` 列（五步先例②第 5 步同款："CREATE TABLE 常量补列"，`library_final_ledger.md:99`）。
- **回滚**：`ALTER TABLE lib_assets DROP COLUMN IF EXISTS successor_of;`（数据非破坏性：仅丢去向指针，`lib_events` 只追加全程留痕可重建；代码侧回滚=ledger_schema/lookup/librarian 三件 git revert；更符合"只增不改语义"的选择是列保留、代码回退）。
- **应用通道**：`python scripts/governance/migrations/add_library_successor_of.py`；脚本内部 `get_depgraph_pg_connection(superuser=True)`（add_acquisition_fields 先例）；**前置**=RULE-DATA-OPS 三步验证 + `python scripts/backup/library_ledger_backup.py` 备份；**白名单**=新脚本路径加 `depgraph_write_path_gate.py` `_WHITELIST` + 错误信息段（L40-43 三步扩展规矩 + L221 错误文本同步）。
- **Owner 门位**：08 词典 §6 增枝批（呈批件=`S5_library_wiring/successor_of_ruling_request.md`，施工批新立，格式对标 ulib3b proposal §二停止判据三问——本簿 §4.7 给出三问答案）。

### 4.2 任务 2：墓碑去向显示改造点（lookup/librarian）

现状机制实测：
- `lookup_assets(query, limit=20, *, kind, owner_domain, tags, status, home_prefix) -> list[dict]`（`lookup.py:105-114`）；查询轴=asset_id/home/title 三列 ILIKE（`ledger_schema.py:148-154`）；过滤轴 5 件套常量拼接（L159-169）；别名轴 G15-① 词表归一 fail-open（`lookup.py:51-98`）；供数反查轴 --feeds（`librarian.py:239-248`）。
- **deceased 现状**：主查询 `_SQL_LOOKUP` **无 status 过滤**→deceased 资产照常出现在结果中（带 status 列但无任何去向信息）；`--status` 可显式筛。CLI 每行只打 `asset_id/kind/status/home` 四列（`lookup.py:294`）；`disposition_authority` 不在任何 SELECT 里。
- `Librarian.validate_action(action, authority)`（`ledger_schema.py:209-223`）：六动作枚举校验，delete 强制处置预授权（08 §3.1 死亡证明）。

改造点（三件，全在 st-p1b 未触碰文件）：
1. `ledger_schema.py`：`_SQL_LOOKUP`（L148-154）与 `_SQL_LOOKUP_COMPOSED`（L159-163）的 SELECT 各加 `disposition_authority, successor_of` 两列（模块级常量改法，NO-BARE-SQL 不破）；`_SQL_MARK_DECEASED`（L138-141）改 `SET status='deceased', disposition_authority=%s, successor_of=%s WHERE asset_id=%s`。
2. `librarian.py`：`act()` delete 分支（L190-191）透传 `f.get("successor_of")`（可空=None=未评估）；fields 文档串补 successor_of。
3. `lookup.py` CLI（L293-294）：`row['status']=='deceased'` 时行尾追加 `-> {successor_of}`（successor 为空串=无后继；NULL=未评估则显示 disposition_authority 前 40 字符墓碑铭）；全结果无 active 命中但有 deceased 命中时，`(no results)` 提示升级为 `(moved: <asset_id> -> <successor_of>)` 墓碑卡。API 侧返回 dict 走 `dict(zip(cols,...))` 自动带新键，零改。

### 4.3 任务 3：血肉门精读 → FMS-HYGIENE 复用模式

`src/zephyr/gov_enforcement/commit_gates/library/library_blood_flesh_gate.py` 实测结论：
- **不连总账 DB**。它的"账"=翻译册文件 `docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`（L80）+ `gateway.run_git` diff（L118-138 staged 新增 .py；L206-218 HEAD 版本对照）。
- 复用资产五件套：① `GateSpec(gate_id, check, priority)` 闭包签名 `(gateway, files, **kwargs)->(bool,str)`（L246-285）；② own-scope 剔除外来 staged（`_build_own_scope`/`_audit_foreign_staged`，L199-203，宪法 §3）；③ warn-first 模式开关环境变量（L78 `BLOOD_FLESH_GATE_MODE="warn"`，L279-283 升 block 通道，对标 STATE-VOCAB 先例）；④ fail-open ERROR_CONTRACT（L13：永不抛异常，git/yaml/IO 异常降级 warn）；⑤ 审计落盘 `.runtime/gate_audit/*.jsonl`（L155-171）。
- priority 选位法：找 gate 序空档（它占 133=TAG-VOCAB 134 前唯一空档，L43）；FMS-HYGIENE 由 S1 选位。
- 门内对 missing/deceased **零处置**（它只管血肉字段）——S1 设计死引用检查时的账面升级（报"迁往何处"而非"不存在"）直接消费本线 4.2 的 lookup/账面能力即可，无需连 PG 也可（读生成视图+调 lookup CLI 子进程）；若直连账则用 `get_depgraph_pg_connection()` 默认只读角色（lookup.py:116 同款，零白名单负担）。

### 4.4 任务 4：三层对账检查器规格（独立新文件，避开 st-p1b）

分工边界（防功能重复）：

| 件 | 职责 | 动作 |
|---|---|---|
| library_regen_reconciler（st-p1b） | 刷新管线：采集→入账→馆页重生成→调对账 | **写**（HEAD L62-112 实读确认） |
| check_library_coverage.py | 盘↔账两向差集报告（blind/ghost） | 写报告（L46-95） |
| **本线新件 tri-checker** | **账↔视图↔盘三层一致性断言** | **纯只读，不修不写不改账** |

新件规格：`scripts/governance/generators/check_library_tri_consistency.py`（check_library_coverage 同目录同款机生报告先例）：
1. **账↔视图**：`docs/library/INDEX.md` 各馆计数逐项 vs PG 按馆谓词 count（`WHERE status NOT IN ('deceased','archived')`，`generate_library_index.py:39-42`）；七馆页 rows[:300] 每行 (asset_id,status,home) 与 DB 复核；"本页列出"声明数 vs 表格实际行数（断言 §2.2 计数失真 bug，修后归零）。
2. **regen-clean 断言**（支柱 3）：子进程跑 `generate_library_index.py` 后 `git diff --exit-code docs/library/`——非零即手改/漂移。
3. **视图↔盘面抽样**：馆页 home 列 N=50 抽样 `Path.exists()`（读盘不动账）。
4. 馆谓词真源唯一：`from scripts...generate_library_index import _HALLS`（或提取共享常量），禁复制谓词。
5. 挂接：先以独立 CLI + `.pre-commit-config.yaml` 手动档落地；`reconciliation_registry.py` 挂接**待 st-p1b 落地后**经其通道追加（避让铁律）。
6. ERROR_CONTRACT：DB 不可达非零退出（对标 coverage L13）；输出机生报告带索书号 frontmatter。

### 4.5 任务 5：临时区编目口径（净零判据选定）

- 现状：fs_collector 不读 .runtime（`fs_collector.py:33-50` `_SKIP_DIRS` 硬跳，与宪法 §9.4 .runtime 卫生一致，**不改**）；28 条 .runtime active 残留入账来源=历史采集版本/手工（§2.3）；logs_collector 已有"登记册状态→总账状态"映射先例（`logs_collector.py:40` legacy→archived）。
- **选定方案：复用既有字段，零新枚举**——`retention_class='temp'`（08 词典 §8 已立法"临时专区持二级身份证 retention_class=temp+TTL"）标记 + 既有 status 表态。理由：a) 新 kind 值要双改 `ASSET_KINDS`+`_KIND_PREFIX`（`ledger_schema.py:28-64`）且破坏 derive_asset_id 稳定性；b) 新 status 违反内收判据（7 枚举中 archived/deceased 已够表达，且 stale/orphan/ghost/blind 四枚举至今零使用——先消化再增枝）；c) retention_class 列现成、零 DDL。
- 存量 28 条两步处置（随本线施工批）：①status active→archived（仍在册不写入语义，防 coverage ghost 误报口径同 logs_collector L40 注释）；②已签 authority 未翻状态的 1 条（archive_log.jsonl）同批翻正；临时件 TTL 到期→deceased+successor_of（通常=无后继）。
- 入账通道：临时件如需入账走显式登记（logs_collector 式登记册法），fs 白名单跳过不变。

### 4.6 任务 6：lookup 单口立法处方（等长替换）

- 宪法现长 140 行（≤300 硬上限余量足，但"新增必须等长替换"约束仍适用）。
- **替换行精确提案**——`AGENTS.md:114` 现文：

  `- 全图全库对齐：\`alignment_checklist.md\`（对齐键=module_id/step_id；\`align_all.py\` 单入口）。`

  等长替换为（一行换一行，零增行）：

  `- 单写者+路径禁凭记忆：每类事实一个真源，写资产路径前必经 \`python -m zephyr.library.lookup <词>\` 查真（deceased 显 successor 墓碑）；全图对齐=\`alignment_checklist.md\`（\`align_all.py\`）。`

- **单写者纪律声明落点建议：宪法 §8 替换行内承载（推荐）**，理由：a) 单写者是行为规则，其行为真源=宪法，ROOR 是"注册表发现"真源，主题不合；b) ROOR 面属 S4 手术范围（骨架 §五），本线写入即撞面；c) 零增行零新文件。若 Owner 坚持 ROOR 也要显式声明，归 S4 批次统一落（本簿只留建议不留施工）。
- 执法闭环：本条款属知识-only 层（宪法 §9 同级，门禁不拦）；硬执法由 S1 的 FMS-HYGIENE 门承接（死引用检出时经 lookup 墓碑卡报"迁往何处"）。
- 生效通道：AGENTS.md=热文件+受保护路径→走 Owner/裁定登记通道 + `safe_write_text` CAS（`src/zephyr/shared/io/file_utils.py`）+ 写后进程外复核。

### 4.7 呈批件三问预填（增枝制门槛，08 词典 §6）

1. **现有字段能否表达？** 不能——disposition_authority 实测承载的是自裁批文长文本（§2.3），非结构化后继指针；death 时问"去了哪"无处可写。
2. **是否零触发零消费（w5_1）？** 非零——消费方=FMS-HYGIENE 门（S1 死引用报去向）、lookup 墓碑卡、tri-checker 断言；触发方=delete 处置链（94 条 deceased 存量+每日新死亡）。
3. **是否同真源可派生？** 不可——lib_events 有 delete 事件但 detail 无固定 successor 键，且自然语言批文不可机械反解。

### 4.8 施工批文件清单（B3 批映射；仪式链逐条见骨架 §六）

| # | 文件 | 动作 | 说明 |
|---|---|---|---|
| 1 | `scripts/governance/migrations/add_library_successor_of.py` | 新 | 增枝①幂等 DDL；白名单登记 depgraph_write_path_gate |
| 2 | `src/zephyr/library/ledger_schema.py` | 改 | CREATE 常量补列+MARK_DECEASED 三参+两 SELECT 加两列 |
| 3 | `src/zephyr/library/librarian.py` | 改 | act() delete 透传 successor_of |
| 4 | `src/zephyr/library/lookup.py` | 改 | CLI 墓碑显示+moved 提示 |
| 5 | `docs/_working/ultimate_library/08_field_dictionary_v0_1.md` | 改 | 升 v1.2 加 successor_of 行（只增不改语义） |
| 6 | `scripts/governance/generators/check_library_tri_consistency.py` | 新 | 三层断言检查器（纯只读） |
| 7 | `tests/library/test_lookup_tombstone.py` 等 | 新 | tests/ 豁免 CREATE-GUARD |
| 8 | `docs/_working/fms_overhaul/S5_library_wiring/successor_of_ruling_request.md` | 新 | 呈批件（§4.7 三问已预填） |
| 9 | `AGENTS.md:114` | 改 | Owner 通道等长替换（§4.6） |
| 10 | 28 条 .runtime 存量处置 | DB | 单独事务批，RULE-DATA-OPS 三步验证 |

仪式链：creation_token 先行独立批（三新件）→ add_module_translation（两新 .py）→ apply_depgraph --add-design-node → 无新门（净零声明见 §3.6）→ 提交走 `scripts/git_commit.py --session st-fms-chief-20260927`。

## ⑤ 自审闸三态

**判定：挖干**（施工代理拿簿可直接开工），附两项外部依赖声明：

| 项 | 状态 | 说明 |
|---|---|---|
| 六向台账 | 完成 | 全部带 file:line + PG 实测 |
| DDL 处方 | 完成 | DDL 全文+迁移脚本先例+白名单通道+幂等+回滚齐备 |
| Owner 增枝批文 | **外部依赖（流程固有）** | 08 §6 增枝制硬门槛，呈批件三问已预填（§4.7），到号即动（先例 library_final_ledger.md:74 "到号即 DDL 五步"）；批前可先行落零 DDL 件（#3/4/6/7/8 文件与测试，mock 连接） |
| st-p1b reconciler 挂接 | **外部依赖（已给绕行）** | tri-checker 先独立 CLI 落地，registry 挂接待其落地后追加（§4.4 第 5 条） |
| 宪法替换行 | 完成 | 精确文本已给出（§4.6），走 Owner 通道生效 |
| 遗留待解释 | 无 | 27,864/27,949/28,454 已破案（§2.2）；.runtime 入账通道已实证（§2.3） |
