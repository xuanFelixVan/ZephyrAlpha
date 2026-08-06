---
ttl: task_bound
---

# 描述性 ARCH ID 治理：Phase 1 清单 + 补登草案 + Phase 2 策略

> 生成日期：2026-08-05
> 扫描范围：全项目 .py/.yaml/.yml/.md/.json/.txt（排除 .git/.runtime/__pycache__ 等）
> 扫描结果：263 个唯一描述性 ARCH ID，其中 240 已登记、**23 未登记**（共 147 处引用）

---

## 一、Phase 1：23 个未登记描述性 ARCH 引用清单 + 逐条裁定

### 分类总览

| 分类 | ID 数 | 引用数 | 处理方式 |
|------|-------|--------|----------|
| A. tests/ 豁免区 | 6 | 26 | 无需处理（门禁已豁免） |
| B. 截断/简称/别名伪阳性 | 8 | 45 | 修正源文本为完整已登记 ID |
| C. 真实未登记引用 | 9 | 56 | 补登条目到 registry |
| **合计** | **23** | **147** | |

---

### A. tests/ 豁免区（6 个 ID，26 处引用）— 无需处理

门禁 `is_test_exempt()` 对 `tests/` 目录豁免，这些是测试用例中构造的伪 ARCH ID，不是真实引用。

| # | ARCH ID | 引用数 | 位置 | 裁定 |
|---|---------|--------|------|------|
| 1 | `ARCH-A-B-C-001` | 2 | test_arch_reference_gate.py | **豁免** — 测试四段式检测的构造 ID |
| 2 | `ARCH-CH-999` | 2 | test_arch_reference_gate.py | **豁免** — 测试两段式检测的构造 ID |
| 3 | `ARCH-DOC-REF-FAKE` | 3 | test_arch_reference_gate.py | **豁免** — 测试描述性 ID 阻断的构造 ID |
| 4 | `ARCH-GOV-SHIM` | 4 | test_arch_reference_gate.py | **豁免** — 测试无数字后缀检测的构造 ID（registry 有 GOV-SHIM-001，此处故意用无数字变体验证检测） |
| 5 | `ARCH-GOV-SHIM-999` | 2 | test_arch_reference_gate.py | **豁免** — 测试三段式检测的构造 ID |
| 6 | `ARCH-TEST-001` | 13 | test_issue_resolved_integrity_gate.py | **豁免** — issue_resolved_integrity_gate 单测用的桩 ID |

---

### B. 截断/简称/别名伪阳性（8 个 ID，45 处引用）— 修正源文本

这些 ID 的**完整形式已在 registry 登记**，但因行截断、简称或别名导致正则匹配到不完整的片段。

| # | 未登记 ID | 引用数 | 已登记完整 ID | 根因 | 裁定 |
|---|-----------|--------|---------------|------|------|
| 7 | `ARCH-CAPABILITY-LO` | 4 | `ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S2` | full_project_tree_{en,zh}.md 第 704 行被生成器截断（行过长） | **修正源文本** — 重新生成 full_project_tree 或手动修正截断行 |
| 8 | `ARCH-DOM` | 2 | `ARCH-DOMAIN-NNN` | registry adjudication 文本中的省略号引用 `ARCH-DOM...`（历史叙事描述截断问题） | **修正源文本** — 改为 `ARCH-DOMAIN-NNN` 或移除省略号 |
| 9 | `ARCH-GOV-CONVERGENC` | 2 | `ARCH-GOV-CONVERGENCE-META` | module_translation_registry.yaml 行截断（desc_zh 字段过长） | **修正源文本** — 截断行补全或换行 |
| 10 | `ARCH-GOV-CONVERGENCE-M` | 4 | `ARCH-GOV-CONVERGENCE-META` | 19_d_gov_code_quality.md 行截断（表格单元格过长） | **修正源文本** — 重新生成 domain doc 或手动修正 |
| 11 | `ARCH-RECONCILE-WORKER-STALE` | 2 | `ARCH-RECONCILE-WORKER-STALE-SEVERITY-001` | registry adjudication 文本截断（`ARCH-RECONCILE-WORKER-STALE-` 尾部连字符后截断） | **修正源文本** — 补全为完整 ID |
| 12 | `ARCH-STAGE4` | 30 | `ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001` | 代码/文档中使用简称 `ARCH-STAGE4` 指代完整 ID | **修正源文本** — 全部替换为完整 ID（live 代码 2 处：dead_public_wrapper_reconciler.py + capability_canonical_file_registry.yaml；其余 28 处在 tmp/.aidrafts 备份区） |
| 13 | `ARCH-README-BACKUP-POINTER` | 20 | `ARCH-README-BACKUP-001` | registry adjudication 文本用描述性别名 `POINTER` 指代数字制条目 `001` | **修正源文本** — registry adjudication 中的别名改为 `ARCH-README-BACKUP-001`（live 2 处在 registry 自身；其余 18 处在 tmp/ 备份区） |
| 14 | `ARCH-DATA-SYMBOL-0` | 1 | `ARCH-DATA-SYMBOL-001` | tmp/_plain_zh_manual.json 临时文件中文本截断 | **忽略** — tmp/ 临时文件，清理即可 |

**B 类施工方案**：
- live 代码/docs 中的截断（#7-#13 共 ~15 处 live 引用）：逐处修正为完整已登记 ID
- tmp/.aidrafts 备份区引用（~30 处）：无需修正（备份快照，非真源），但建议将 tmp/ 和 .aidrafts/ 纳入门禁 skip 列表避免未来干扰

---

### C. 真实未登记引用（9 个 ID，56 处引用）— 需补登到 registry

这些是代码/文档中真实使用的描述性 ARCH ID，registry 中无任何对应条目（包括完整形式），违反铁律#6。

| # | ARCH ID | 引用数 | 主要位置 | 主题 | 裁定 |
|---|---------|--------|----------|------|------|
| 15 | `ARCH-CH-MATERIALIZED-INSERT` | 5 | ch_writer.py, buffered_writer.py, wal_writer.py | ClickHouse MATERIALIZED/ALIAS 列写入排除 | **补登** |
| 16 | `ARCH-DEPGRAPH-OPS-TXN-ABORTED` | 3 | generate_project_depgraph.py | depgraph UPSERT 逐表 SAVEPOINT 隔离 | **补登** |
| 17 | `ARCH-EDB-EXPAND` | 15 | data_sources_registry.yaml, scheduler.py, 多处 docs | FRED/EIA/世界银行免费宏观数据扩展 | **补登** |
| 18 | `ARCH-EM-ANTIBOT-FAILOVER` | 1 | akshare_provider.py | 东财反爬封锁降级到同花顺 | **补登** |
| 19 | `ARCH-FUTURES-POSITION` | 5 | akshare_provider.py | akshare 替代 QMT 期货持仓数据 | **补登** |
| 20 | `ARCH-PRECOMMIT-INCREMENTAL` | 11 | trae_028 yaml, _working 草稿 | pre-commit 命名增量守门（--check-new） | **补登** |
| 21 | `ARCH-REALTIME-ACCUM` | 11 | data_sources_registry.yaml, tasks.yaml, 多处 docs | 时间敏感型数据每日积累（和风天气免费版无历史 API） | **补登** |
| 22 | `ARCH-RECONCILER-INDEXLOCK-RETRY` | 3 | git_commit_gateway.py, test_git_commit_gateway.py | git add index.lock 竞争重试 | **补登** |
| 23 | `ARCH-VALUATION-IFIND-PRIMARY` | 2 | akshare_provider.py, ifind_provider.py | 估值数据 ifind 主源切换 | **补登** |

---

## 二、Phase 1 补登条目草案（9 个真实未登记引用）

以下为追加到 `architecture_issue_registry.yaml` 的条目草案，每个含裁定理由。

### 1. ARCH-CH-MATERIALIZED-INSERT

```yaml
# --- ARCH-CH-MATERIALIZED-INSERT: ClickHouse MATERIALIZED/ALIAS 列写入排除（2026-08-05 补登记） ---
- issue_id: 'ARCH-CH-MATERIALIZED-INSERT'
  title: ClickHouse 写入 MATERIALIZED 列冲突——可插入列集合排除治本
  severity: P1高
  category: data
  adjudication: |-
    2026-08-03 治本，2026-08-05 补登记（违反铁律#6）。
    病根：ch_writer.py 的 _get_table_columns_set 返回含 MATERIALIZED/ALIAS 列，
    INSERT 时 ClickHouse 拒绝写入这些计算列，导致 CH 写入失败（属"CH 写入失败根因分类"
    三类之一：MATERIALIZED 列写冲突）。
    治本方案：构建可插入列集合（排除 MATERIALIZED/ALIAS），INSERT 只用可插入列。
    影响文件：ch_writer.py / buffered_writer.py / wal_writer.py。
  fix_phase: |-
    已完成（2026-08-03）：
      - ch_writer.py 新增可插入列缓存（排除 MATERIALIZED/ALIAS）
      - buffered_writer.py / wal_writer.py 复用可插入列集合
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-03'
  last_updated: '2026-08-05'
```

**裁定理由**：代码中 5 处引用描述同一治本（MATERIALIZED 列排除），属真实架构决策，必须登记。severity=P1 因数据写入层核心路径。

### 2. ARCH-DEPGRAPH-OPS-TXN-ABORTED

```yaml
# --- ARCH-DEPGRAPH-OPS-TXN-ABORTED: depgraph UPSERT 逐表 SAVEPOINT 隔离（2026-08-05 补登记） ---
- issue_id: 'ARCH-DEPGRAPH-OPS-TXN-ABORTED'
  title: depgraph 批量 UPSERT 单表失败回滚全事务——逐表 SAVEPOINT 隔离治本
  severity: P2中
  category: governance
  adjudication: |-
    2026-07-25 治本，2026-08-05 补登记（违反铁律#6）。
    病根：generate_project_depgraph.py 批量 UPSERT 多表时，单表失败导致整个事务
    ROLLBACK，已成功写入的表也被回滚，depgraph 部分更新丢失。
    治本方案：逐表 SAVEPOINT 隔离——每张表 UPSERT 前设 SAVEPOINT，失败时
    ROLLBACK TO SAVEPOINT 只回滚当前表，不影响已成功的表。
  fix_phase: |-
    已完成（2026-07-25）：
      - generate_project_depgraph.py 逐表 SAVEPOINT 隔离
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-07-25'
  last_updated: '2026-08-05'
```

**裁定理由**：scripts/ 中 3 处引用描述 depgraph 事务隔离机制，属真实架构决策。

### 3. ARCH-EDB-EXPAND

```yaml
# --- ARCH-EDB-EXPAND: FRED/EIA/世界银行免费宏观数据扩展（2026-08-05 补登记） ---
- issue_id: 'ARCH-EDB-EXPAND'
  title: EDB 宏观指标数据源扩展——FRED/EIA/世界银行免费源接入
  severity: P2中
  category: data
  adjudication: |-
    2026-08-04 治本，2026-08-05 补登记（违反铁律#6）。
    病根：EDB（经济数据库）宏观指标原依赖 ifind 试用账号，账号到期后数据断供。
    治本方案：接入 FRED（美联储经济数据库）、EIA（美国能源信息署）、世界银行
    三个免费数据源，扩展国际对比宏观数据覆盖。FRED/EIA 需注册免费 API key
    配置在 .env，海外站点直连可用无需 VPN。
    关联：与 ifind 退役（commit 62c4e3494f）同批落地。
  fix_phase: |-
    已完成（2026-08-04）：
      - 新增 FRED/世界银行/EIA provider
      - data_sources_registry.yaml / tasks.yaml / capability registry 同步登记
      - SECRETS.md 登记 FRED_API_KEY / EIA_API_KEY
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-04'
  last_updated: '2026-08-05'
```

**裁定理由**：15 处引用横跨 src/docs/architecture_model，描述重大数据源扩展决策，必须登记。

### 4. ARCH-EM-ANTIBOT-FAILOVER

```yaml
# --- ARCH-EM-ANTIBOT-FAILOVER: 东财反爬封锁降级（2026-08-05 补登记） ---
- issue_id: 'ARCH-EM-ANTIBOT-FAILOVER'
  title: 东财 push2 子域名 IP 封锁——反爬降级到同花顺治本
  severity: P2中
  category: data
  adjudication: |-
    2026-08-04 治本，2026-08-05 补登记（违反铁律#6）。
    病根：东财 push2.eastmoney.com 子域名被 IP 应用层封锁（TCP 能握手但 HTTP
    请求被 RemoteDisconnected 主动断开），逐板块重试浪费时间。
    治本方案：IP 被封锁时避免逐板块重试，直接降级到同花顺 q.10jqka.com.cn
    公开网页解析获取概念板块成分股。连续失败 3 次后标记 _em_push2_blocked，
    直接走同花顺替代路径，节省约 17 秒/板块。
    关联：与 ARCH-DOC-REF 系列、东财数据源降级策略同源。
  fix_phase: |-
    已完成（2026-08-04）：
      - akshare_provider.py 新增 _em_push2_blocked 降级逻辑
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-04'
  last_updated: '2026-08-05'
```

**裁定理由**：src/ 中 1 处引用，描述数据源反爬降级策略，属真实架构决策。

### 5. ARCH-FUTURES-POSITION

```yaml
# --- ARCH-FUTURES-POSITION: akshare 替代 QMT 期货持仓（2026-08-05 补登记） ---
- issue_id: 'ARCH-FUTURES-POSITION'
  title: QMT 期货持仓数据全0——akshare 替代治本
  severity: P2中
  category: data
  adjudication: |-
    2026-08-04 治本，2026-08-05 补登记（违反铁律#6）。
    病根：QMT get_instrument_detail 返回期货持仓全 0，数据不可用。
    治本方案：改用 akshare 期货持仓 API（futures_position 等接口）替代 QMT，
    包括各交易所排名表 API 和 pd.to_numeric 安全转换（CZCE 返回逗号拼接字符串）。
  fix_phase: |-
    已完成（2026-08-04）：
      - akshare_provider.py 新增 futures_position CapabilityContract + 实现
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-04'
  last_updated: '2026-08-05'
```

**裁定理由**：src/ 中 5 处引用，描述期货数据源替代决策，属真实架构决策。

### 6. ARCH-PRECOMMIT-INCREMENTAL

```yaml
# --- ARCH-PRECOMMIT-INCREMENTAL: pre-commit 命名增量守门（2026-08-05 补登记） ---
- issue_id: 'ARCH-PRECOMMIT-INCREMENTAL'
  title: N-16 命名门禁全量扫描阻塞——增量守门（--check-new）治本
  severity: P2中
  category: governance
  adjudication: |-
    2026-08-05 治本+补登记（同日）。
    病根：N-16 命名门禁原为全量扫描，每次 commit 扫描全仓文件名重名，耗时且
    阻塞草稿区（_working）正常使用。
    滞本方案：拆分为增量守门（GATE-NAMING --check-new，只拦 staged 新增重名）
    + 全量审计（GATE-NAMING-AUDIT --warn-only --scan，不阻断），草稿区 _working
    纳入 skip_dirs_docs 不阻断 commit。
  fix_phase: |-
    进行中（2026-08-05）：
      - trae_028_doc_structure_naming.yaml 已更新 skip_dirs 含 _working
      - _working/precommit_gate_incremental_refactor_plan.md 施工方案已起草
      - 门禁拆分实施待执行
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-05'
  last_updated: '2026-08-05'
```

**裁定理由**：11 处引用（含 docs/ 规则 YAML + _working 草稿），描述门禁架构改造决策。注意 _working 草稿区引用属设计阶段文档，补登后合规。

### 7. ARCH-REALTIME-ACCUM

```yaml
# --- ARCH-REALTIME-ACCUM: 时间敏感型数据每日积累（2026-08-05 补登记） ---
- issue_id: 'ARCH-REALTIME-ACCUM'
  title: 免费数据源无历史 API——时间敏感型数据每日快照积累治本
  severity: P2中
  category: data
  adjudication: |-
    2026-08-04 治本，2026-08-05 补登记（违反铁律#6）。
    病根：和风天气等免费数据源无历史 API，只能获取最近数据，错过即永久丢失，
    无法回填。
    治本方案：标记时间敏感型数据（incremental=false），每日快照积累存储到
    ClickHouse，成分股变动等无法回填的数据强制每日采集。
    关联：与 ARCH-EDB-EXPAND 同批落地（免费数据源接入）。
  fix_phase: |-
    已完成（2026-08-04）：
      - data_sources_registry.yaml / tasks.yaml 标记时间敏感型数据
      - business_data_categories.yaml 分类登记
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-04'
  last_updated: '2026-08-05'
```

**裁定理由**：11 处引用横跨 src/docs/architecture_model，描述数据采集策略决策，必须登记。

### 8. ARCH-RECONCILER-INDEXLOCK-RETRY

```yaml
# --- ARCH-RECONCILER-INDEXLOCK-RETRY: git add index.lock 竞争重试（2026-08-05 补登记） ---
- issue_id: 'ARCH-RECONCILER-INDEXLOCK-RETRY'
  title: git add index.lock 竞争失败——暂时性重试治本
  severity: P2中
  category: governance
  adjudication: |-
    2026-08-03 治本，2026-08-05 补登记（违反铁律#6）。
    病根：GitCommitGateway 并发执行 git add 时，多个进程争抢 index.lock，
    部分进程因 lock 占用失败，导致文件漏暂存。
    治本方案：git add 带 index.lock 暂时性竞争重试——捕获 lock 竞争异常后
    退避重试（指数退避，最多 N 次），重试全部失败才报错。
  fix_phase: |-
    已完成（2026-08-03）：
      - git_commit_gateway.py 新增 _git_add_with_retry 重试逻辑
      - test_git_commit_gateway.py 补充治本测试
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-03'
  last_updated: '2026-08-05'
```

**裁定理由**：src/ + tests/ 共 3 处引用，描述 GitCommitGateway 核心机制，属真实架构决策。

### 9. ARCH-VALUATION-IFIND-PRIMARY

```yaml
# --- ARCH-VALUATION-IFIND-PRIMARY: 估值数据 ifind 主源切换（2026-08-05 补登记） ---
- issue_id: 'ARCH-VALUATION-IFIND-PRIMARY'
  title: 估值 full_refresh symbols=null 必须 ifind 主源——主备源切换治本
  severity: P2中
  category: data
  adjudication: |-
    2026-08-04 治本，2026-08-05 补登记（违反铁律#6）。
    病根：估值数据 full_refresh 切 ifind 主源后，symbols=null（全市场）必须
    由 ifind 承载，但 akshare 备源不支持 symbols=null 全市场扫描，导致
    full_refresh 降级到 akshare 时数据缺失。
    治本方案：明确 ifind 为估值数据主源，full_refresh 的 symbols=null 路径
    强制走 ifind；akshare 仅作增量更新备源。
    关联：与 ifind 退役（commit 62c4e3494f）同批，但估值数据保留 ifind 主源。
  fix_phase: |-
    已完成（2026-08-04）：
      - ifind_provider.py / akshare_provider.py 主备源切换逻辑
      - 本条补登记满足铁律#6（2026-08-05）
  status: decided
  created: '2026-08-04'
  last_updated: '2026-08-05'
```

**裁定理由**：src/ 中 2 处引用，描述数据源主备切换决策，属真实架构决策。

---

## 三、Phase 2：描述性 ARCH ID 长期策略方案对比

### 背景

当前项目存在两种 ARCH ID 格式并存：
- **数字制**：`ARCH-008` / `ARCH-CH-007` / `ARCH-GOV-SHIM-001`（铁律#7 原要求）
- **描述制**：`ARCH-DOC-REF-FILE-URL` / `ARCH-EDB-EXPAND` / `ARCH-CH-MATERIALIZED-INSERT`（无数字后缀）

实测数据：263 个唯一描述性 ID（占全部 ARCH ID 的 46%），240 个已登记。描述制已成事实主流，铁律#7"要求数字后缀"实际已普遍逾越。

### 方案对比

| 维度 | 方案 A：全面数字制 | 方案 B：接纳双轨制 | 方案 C：冻结+渐进迁移 |
|------|-------------------|-------------------|----------------------|
| **核心做法** | 所有描述性 ID 强制迁移为数字制（如 `ARCH-EDB-EXPAND` → `ARCH-150`），铁律#7 保持不变 | 修改铁律#7 正式接纳描述性 ID 为合法格式，与数字制并存，gate 同时检测两种 | 冻结现有描述性 ID（已用者保留），新条目强制数字制，存量描述性 ID 逐步在自然修改时迁移 |
| **合规性** | ✅ 符合铁律#7 现状 | ❌ 需修改铁律#7 | ✅ 符合铁律#7（新条目） |
| **迁移工作量** | 🔴 极大：263 个 ID × 平均 3-5 处引用 = ~1000 处文本替换 + registry 全量重编号 | 🟢 零迁移：只需改铁律文本 + gate 已支持 | 🟡 中等：新条目零成本，存量自然迁移无额外工作 |
| **可读性** | 🔴 差：`ARCH-150` 无语义，需查 registry 才知道是什么 | 🟢 优：`ARCH-EDB-EXPAND` 自解释 | 🟡 混合：新条目数字制（差），旧条目描述制（优） |
| **可追溯性** | 🟡 中：数字 ID 无语义但 registry 有映射 | 🟢 优：ID 自身即语义线索 | 🟡 中：新旧混杂需注意 |
| **gate 复杂度** | 🟢 低：只需数字正则 | 🟡 中：需同时支持两种格式（已实现） | 🟡 中：需同时支持两种格式 |
| **编号冲突风险** | 🟢 低：数字递增无冲突 | 🟡 中：描述性 ID 命名冲突需规范 | 🟢 低：新条目数字递增 |
| **100% AI 开发适配** | 🔴 差：AI 新建条目需先查最大编号，易出编号空洞 | 🟢 优：AI 可直接用语义命名，降低编号管理负担 | 🟡 中：AI 需判断"新条目用数字制" |
| **历史一致性** | 🔴 差：git blame 全部打乱，历史可追溯性破坏 | 🟢 优：零改动 | 🟢 优：存量不动 |
| **二元可判性** | 🟢 优：有数字=合规，无数字=违规 | 🔴 差：需定义"什么算合法描述性 ID"（灰度） | 🟢 优：新条目有数字=合规，旧条目豁免 |

### 第一性原理分析

**铁律二元化元规则**（project_memory 2026-08-04）要求"所有铁律必须二元可判（是/否，无灰度）"。

- **方案 A（全面数字制）**：二元判定 = "ID 末段是否为纯数字？" → 是/否，无灰度。✅
- **方案 B（双轨制）**：二元判定困难——"描述性 ID 是否合法？"需要定义命名规范（必须全大写？连字符分隔？最小长度？），存在灰度空间。除非定义极简规则"任何匹配 `ARCH-[A-Z][A-Z0-9-]*[A-Z0-9]` 的均为合法"，但这等于不设规范。⚠️
- **方案 C（冻结+迁移）**：二元判定 = "条目创建日期 > 冻结日 且 ID 末段非数字？" → 违规。存量豁免需时间戳判定，略复杂但二元可判。✅

**100% AI 开发适配**：AI 新建 ARCH 条目时，数字制需要"查当前最大编号 → +1"，这个操作虽简单但在并发会话中易出编号冲突；描述性制只需"选个语义名"，无并发冲突。对 100% AI 开发项目，描述性制反而降低编号管理负担。

### 裁定建议

**推荐方案 C（冻结+渐进迁移）**，理由：

1. **治本不治标**：方案 A 的 1000 处替换是"为合规而合规"，不产生业务价值，且破坏 git 历史；方案 B 需修改铁律#7，降低编号规范严格性
2. **二元可判**：方案 C 的"新条目强制数字制 + 存量冻结豁免"可二元判定，符合铁律二元化元规则
3. **零迁移成本**：现有 240 个描述性 ID 不动，新条目用数字制，gate 已支持两种格式检测
4. **自然收敛**：存量描述性 ID 在代码自然修改时顺手迁移为数字制，无需专项清理
5. **gate 已就绪**：Phase 0 修复的正则已同时支持数字制和描述性 ID，方案 C 无需额外 gate 改造

**方案 C 落地步骤**：
1. 在铁律#7 增加冻结条款："2026-08-05 起新登记 ARCH 条目强制使用数字制（末段纯数字），此前已登记的描述性 ID 冻结保留，自然修改时逐步迁移"
2. gate 增加"新条目数字制"检测：registry 新增条目的 issue_id 末段必须为纯数字（L3 检测，WARNING 不阻断，避免影响存量修改）
3. 存量描述性 ID 不强制迁移，但在 AGENTS.md 标注"描述性 ID 为历史遗留，新条目请用数字制"

**不推荐方案 A**：1000 处文本替换工作量巨大且无业务价值，破坏 git blame 历史，100% AI 开发下并发编号冲突风险高。

**不推荐方案 B**：需修改铁律#7 降低规范严格性，且描述性 ID 合法性判定存在灰度，违反铁律二元化元规则。虽然对 AI 开发友好，但长期看命名规范松散会导致 ID 膨胀和不一致。

---

## 四、施工顺序建议

1. **Phase 1-C（补登 9 条）**：将 9 个真实未登记引用补登到 registry（本文件草案可直接使用）
2. **Phase 1-B（修正截断 ~15 处）**：修正 live 代码/docs 中的 8 个截断/简称伪阳性为完整已登记 ID
3. **Phase 1-A（无需处理）**：6 个 tests/ 豁免项无需处理
4. **Phase 2（策略落地）**：用户裁定方案后，修改铁律#7 + gate L3 检测
5. **收尾**：将 tmp/ 和 .aidrafts/ 纳入门禁 skip 列表（或 .gitignore），避免备份区引用干扰
