---
ttl: permanent
---

# drift_events 唯一真源裁定书（#62 治本，2026-08-21 第十统筹）

> 授权：Owner 2026-08-21 指令——"全部调研清楚，全面审查相关问题，从第一性原理思维出发，长远期战略考虑，客观专业架构师，针对项目 100% AI 开发情况，给出分析过程+裁定结果+治本施工方案"。
> 前置：第四批裁定书（fa0da050e8）#62 节已定"唯一真源=governance.db"方向；本裁定在其基础上完成全量实证复核，发现其代码层三项落地未物理生效（内容丢失同族事故），并按实证重新落地。

---

## 一、调研实证（2026-08-21 全量复核）

### 1.1 三个物理库现状（直查 sqlite_master + PRAGMA）

| 库 | drift_events schema | 行数 | 最近写入 | 状态 |
|---|---|---|---|---|
| `data/databases/governance.db`（DB_PATH SSoT，83MB） | 22 列：event_id **INTEGER AUTOINCREMENT PK** + drift_type/target/expected/actual/severity/detected_at/resolved_at/resolution（legacy 9 列）+ detector_id/module_id/state/source_file/description/details/fix_description/scan_level/auto_fixable/resolution_detail/roi_score/created_at/updated_at（后补 13 列），**无 timestamp 列** | 386（全 INTEGER id） | created_at max=2026-05-26 | 遗产数据，写入链断 |
| `data/drift_audit/drift_events.db`（gate_persistence 自建） | 12 列：event_id TEXT PK/drift_dimension/baseline_version/resolved_by/auto_fixed/rollback_verified 等 | 0 | — | 空壳 |
| `data/drift_audit/drift_audit.db`（trend_analyzer 目标，裁定#18 F5） | — | — | — | 物理不存在 |
| `data/governance.db` | — | 0 字节 | — | 空文件（垃圾） |

### 1.2 写入链仍断的实证（关键新发现）

1. drift_engine `_write_drift_events` INSERT 列含 `timestamp`——生产 schema 无此列。活体探针实证：`INSERT FAIL: table drift_events has no column named timestamp`。
2. 即使去掉 timestamp，INSERT 传 `str(uuid)` 给 INTEGER AUTOINCREMENT PK——datatype mismatch 第二重失配。
3. 每次失败被 `except Exception` 宽捕逐条吞（旧代码 logger.warning 淹没无聚合）——**生产 written=0 自 2026-05-26 起，近 3 个月无告警**。
4. **第四批裁定书落地状态三项（①INSERT 对齐 ③correlation_engine SSoT ④gate_persistence 注释标注）经 git log 实证未物理落地**（drift_engine.py 最后变更=2026-08-19 ruff 批；correlation_engine.py:48-55 仍硬编码路径）——与当夜 miniqmt/akshare 内容丢失同族；仅 ②test_ba_dashboard 改布局（bc0ffc942a）真实落地。
5. correlation_engine 查询 `SELECT scan_id/drift_dimension FROM drift_events`——生产 schema 无此两列，潜在必炸点仍在（当前无生产调用方才未爆，裁定书实证一致）。
6. 测试全部显式传 tmp db_path（CREATE 新建 schema C）——生产失配被完美掩盖（裁定书实证一致，本次复核确认）。

### 1.3 legacy 数据口径（writer 映射依据）

- drift_type 取值=detector 类名（security_policy_drift 156/contract_implementation 126/kb_triage 45/test_coverage_drift 43/...），与 detector_id 列同值；
- severity='MEDIUM'（385/386 主流）；state='DETECTED'（全部）；detected_at NOT NULL isoformat。

## 二、病根分析（结构根因三层）

1. **三 schema 分裂**：governance.db 22 列 legacy（A'）/ drift_events.db 12 列空壳（B）/ drift_engine CREATE DDL 16 列含 timestamp（C）——同一逻辑事件三个物理契约，writer 按 C 写、生产是 A'、B 无人写。
2. **静默吞错**：宽捕 except + 无聚合对账——写侧失败不可见。观测系统的写入链=系统感知自身病变的神经；神经断 3 个月无人知晓，且 Dashboard 照常读死数据无任何"数据截至"提示。
3. **测试-生产分层失配**：测试全走 tmp 新库（schema C 新建），从不触达生产 schema——100% AI 开发场景下，测试形态给了"写入正常"的系统级假阳性。

## 三、第一性原理

1. **观测事件流本质=append-only 日志**，不是实体表。主键的正确形态=自增行号（与 audit_chain/compliance_log 同族）；uuid 主键去重语义从未被生产使用（写入从未成功过），是过度设计。**追加语义与 tamper_proof 的 APPEND_ONLY trigger 天然一致**。
2. **一个事件、一类存储、一个 schema、一个写方**。drift_events 唯一真源=governance.db（paths.py DB_PATH SSoT + #ARCH-WORKTREE-DB-SPLIT-001 先例）；唯一写方=drift_engine；schema=生产 legacy 22 列（386 行遗产的最大兼容）。
3. **写侧失败必须 fail-visible，且写入量必须对账**。静默 swallow 是观测系统的头号反模式——宽捕可以留（不崩主流程），但失败必须聚合上报（数量+目标库），否则神经断了无声。
4. **schema 即契约，契约必须单点**。writer 的 CREATE DDL 必须与生产 schema 逐字一致（新库与生产同构），否则"测试过的是另一张表"。

## 四、行业实践参照

- SQLite 治理库：单库单写者 + WAL 优于多库分散（blueprint §17.2 GAP-003 同口径；Litestream/SQLite 官方运维指南）。
- 观测/审计流（OpenTelemetry/Auditd/Compliance 日志族）：append-only + 自增 id + 写入量 reconcile 是标准形态；事件去重用业务键（source+type+time）查询而非主键。
- schema 迁移纪律（Flyway/Alembic 惯例）：writer 不私建私改表结构；表结构变更走显式迁移；测试夹具必须复刻生产 schema（本仓 sqlite_schema.py SSoT 方向一致）。

## 五、裁定结果

1. **唯一真源=governance.db，终局 schema=现有 22 列 legacy 形态，零 ALTER 零迁移**——386 行遗产原样保留，新写入按 append-only 进入同一 schema。timestamp 列永不引入（created_at/detected_at 已覆盖语义）。
2. **writer 对齐**：drift_engine CREATE DDL 逐字对齐生产 schema；INSERT 改 append-only（不传 event_id，AUTOINCREMENT 分配）；drift_type/detector_id 同填 detector_id（legacy 双列同值口径）；description 承载 drift_dimension；severity='MEDIUM'（legacy 主流）；detected_at=created_at isoformat。
3. **fail-visible**：单行失败 logger.exception 留痕，函数尾写入量对账（written<len(events) → logger.error 聚合上报 db 路径+丢失数）。
4. **空壳处置**（Owner 窗口/后续批）：①data/drift_audit/drift_events.db（12 列 0 行）保留文件待 gate_persistence 改造时一并处置（其 scan_results/gate_decisions 表是否在用另案核查）；②data/governance.db 0 字节空文件删除；③trend_analyzer 独立 drift_audit.db（裁定#18 F5）维持现状——其库为测试隔离产物，物理不存在即未使用，回迁 governance.db 列子裁定项随统一批再议；④correlation_engine 硬编码路径改 DB_PATH SSoT + 列名对齐（scan_id→event_id、drift_dimension→description）另案落地（当前无生产调用方，不阻断）。
5. **Dashboard 死数据**：展示层补"数据截至 <max(created_at)>"提示（读方体验项，随前端批）。
6. **防复发**：本裁定附回归测试（生产 schema 复刻库端到端写入+读回）已随码落地；写入对账已内嵌 writer。建议后续：gate_persistence 的 drift_events 空壳 DDL 删除或改注释标注（其文件不再建该表），消除第三 schema 来源。

## 六、治本施工方案与落地状态

| 层 | 动作 | 状态 |
|---|---|---|
| A 代码止血 | drift_engine CREATE DDL 对齐 22 列 + INSERT append-only + fail-visible 对账 | ✅ 已落地（本批，e2e 4 用例绿+生产 schema 副本端到端写入/读回实证+漂移域 489 用例零新增红） |
| A 测试 | 生产 schema 复刻库写入回读（.runtime/_b7_verify_drift_write.py 实证脚本） | ✅ 已实证（written=1，readback 命中） |
| B DB 处置 | data/governance.db 0 字节删除 / drift_events.db 空壳处置 / Dashboard"数据截至"提示 / correlation_engine SSoT+列对齐 | ⏳ Owner 窗口（DB 写操作与展示层） |
| C 机制 | gate_persistence 空壳 DDL 处置（删表或注释）+ trend_analyzer 回迁子裁定 | ⏳ 随统一批 |

## 七、100% AI 开发场景特别约束（长远战略）

1. **裁定书"落地状态"必须可机器核验**：本次发现第四批三项"已落地"未物理生效——后续裁定书的落地状态栏必须附 commit hash + 实证命令输出（本项目内容丢失/双脑冲突事故已三起同族）。
2. **观测写入链是 AI 自治理的神经**：drift 事件流是审查线/红线修复线的输入，断 3 个月意味着审查体系在盲飞。写入对账（本裁定 ⑤）应推广到所有治理写入点（gate_decisions/scan_results/audit_chain）。
3. **测试夹具复刻生产 schema 应成硬约束**：drift 族测试全部 tmp 新库是本次假阳性根源；建议 schema 一致性测试（PRAGMA table_info 对比生产库）纳入测试债专项批。

---

**裁定人**：第十统筹（Owner 授权调研裁定）｜**实证脚本**：.runtime/_b7_probe_drift_dbs.py / _b7_probe_drift_rows.py / _b7_probe_drift_type.py / _b7_verify_drift_write.py
