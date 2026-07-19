# 架构债务防复发体系设计文档

<!-- metadata (no frontmatter: EXEMPT-ZONE-FM forbids doc_type in _working/) -->
<!-- module_id: MOD-GOV-anti-recurrence-design | version: 1.0.0 | ttl: task_bound -->
<!-- completes_when: P0+P1+P2 全部施工完成、验证闭环通过、设计文档归档 -->
<!-- source: architecture_debt_registry.md v2.0.0 §四 + gate_registry.yaml + architecture_health_dashboard.py METRICS -->
<!-- session_id: sess-50300-20260720044049 -->

**module_id**: MOD-GOV-anti-recurrence-design | **version**: 1.0.0 | **ttl**: task_bound
**completes_when**: P0+P1+P2 全部施工完成、验证闭环通过、设计文档归档
**source**: architecture_debt_registry.md v2.0.0 §四 + gate_registry.yaml + architecture_health_dashboard.py METRICS
**session_id**: sess-50300-20260720044049

> **任务性质**：把架构债务注册表 §四 54 维度做成全自动化防犯体系（门禁/检测系统/运行时守卫），让以后所有 AI 不再犯同类问题。
> **设计原则**：先充分讨论设计、再施工。本文档是设计阶段产物，需用户评审通过后进入施工阶段。
> **真源约束**：维度清单基座 = `docs/02_enterprise_architecture/architecture_debt_registry.md` v2.0.0 §四；gate 真源 = `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（生成器自动维护）；metric 真源 = `scripts/governance/architecture_health_dashboard.py` METRICS 列表。

---

## 0. 设计目标与原则

### 0.1 目标
- 54 维度全覆盖：每维度有明确的防复发机制（gate / metric / reconciler / 文档约束），无空白。
- 防"治理自身漂移"：治理组件数 ≤ 被治理组件数（不造无用 gate）。
- 100% AI 开发场景适配："靠阻断不靠自觉"（裁定 3）—— 建议性规则必然失效，强制消费链才可靠。

### 0.2 五条架构原则（必须内化）
1. **靠阻断不靠自觉**：可静态检测的模式 → pre-commit AST gate（commit 硬阻断）；需运行时数据的 → post-commit reconciler；运行时拦截 → LSG runtime_interceptor；趋势监控非阻断 → dashboard metric；低频低后果 → 文档约束。
2. **防"治理自身漂移"**：新 gate/metric MUST 登记 capability + creation_token 到 `capability_canonical_file_registry.yaml`；新 gate MUST 注册到 `gate_registry.yaml`（生成器自动同步）；新 metric MUST 加入 `architecture_health_dashboard.py` METRICS 列表 + 同步 architecture_debt_registry.md §六；每个新 gate/metric MUST 配测试（`tests/governance/commit_gates/` 对应，A_test 头部）；MUST 带豁免机制（noqa 格式）。
3. **向内收**：能扩展现有 gate/metric 就不新建。优先扩展现有 gate 检测面（如 DATETIME-NOW-FORBIDDEN 从生成器扩展到全 src/）或新增 dashboard metric（M22+）。
4. **ROI 优先**：违规后果度 × 发生频率 × 当前覆盖缺口，三者乘积排序。低价值/已充分覆盖的明确说不做——避免"治理组件数 > 被治理组件数"反模式。
5. **SSoT 真源唯一**：检测逻辑真源唯一；词表/契约改 YAML 后 sync；架构数据用 apply_*.py 写 PG；gate 真源在 gate_registry.yaml（生成器自动维护）。

### 0.3 六种防复发形态分类
| 形态 | 代号 | 适用场景 | 阻断性 | 性能成本 |
|---|---|---|---|---|
| ① pre-commit AST gate | A | 可静态检测的模式（语法树/正则） | 硬阻断 | 低（单文件 AST） |
| ② dashboard metric | B | 趋势监控、非阻断、需全量扫描 | 非阻断（warn-only） | 中（全量扫描） |
| ③ post-commit reconciler | C | 需运行时数据、事后自动修复/告警 | 事后 | 中 |
| ④ 运行时拦截 | D | 运行时行为（LSG runtime_interceptor） | 运行时阻断 | 低 |
| ⑤ CI 检查 | E | 全量/慢速扫描、构建验证 | CI 阻断 | 高 |
| ⑥ 文档约束 | F | 低频率低后果、无法机械检测 | 无（君子协定） | 零 |

---

## 1. 覆盖度审计（54 维度分类）

> 基于 gate_registry.yaml（104 gates）+ architecture_debt_registry.md §四 54 维度逐维度判定。
> 分类口径：**A** = 已有 commit 硬阻断 gate；**CODE** = 无 gate 但有 runtime/SSoT/CI/test 强制（代码层约束）；**C** = 仅有 reconciler 事后检测；**D** = 仅有文档约束（无门禁）；**E** = 完全无覆盖。

| 维度号 | 维度名 | 现状分类 | 现有防复发机制 | 状态 |
|---|---|---|---|---|
| 5.1 | SSoT 真源唯一性 | A | GATE-VOCAB + GATE-SSOT + M01/M05 | FIXED |
| 5.31 | 构建打包 | CODE | CI build-package / docker-build job | FIXED |
| 5.32 | 数据迁移策略 | CODE | 迁移测试套件 | FIXED |
| 5.33 | 容灾与备份 | C | BACKUP-RECONCILER + Restic | PERMANENT-2 |
| 5.34 | 环境隔离 | CODE | PG 测试双轨 + is_prod() 生产写守卫 | FIXED |
| 5.35 | API 版本管理 | CODE | mcp.json version + ERR_API_SUNSET | FIXED |
| 5.36 | 限流与配额 | CODE | shared/infra/limiter.py + ERR_RATE_LIMITED | FIXED |
| 5.37 | 审计日志完整性 | CODE | events.jsonl hash chain + GitCommitGateway | FIXED |
| 5.38 | 特性开关 | CODE | shared/foundation/flags.py + _feature_flag_enabled | FIXED |
| 5.39 | 可观测性深度 | CODE | span_stub + SLOManager + boot 订阅 | FIXED |
| 5.40 | 幂等性与重试语义 | CODE | Idempotency-Key + DLQ + IdempotencyStore | FIXED |
| 5.41 | 状态机正确性 | CODE | VALID_TRANSITIONS + RLock + 审计 | FIXED |
| 5.42 | 代码注释与 API 文档 | D | — | PERMANENT-1 |
| 5.46 | 时间与时区处理 | CODE | now_utc() 全局统一（time_utils SSoT） | PERMANENT-1 |
| 5.52 | 异步/同步边界 | CODE | async_utils canonical + LSG fail-closed | FIXED |
| 5.57 | 事件排序与因果一致性 | CODE | task_events seq + prev_hash 链 | FIXED |
| 5.58 | 分布式锁正确性 | CODE | next_fencing_token + SyncLockRenewer | FIXED |
| 5.60 | 模块耦合度深度 | A | NO-UPWARD-IMPORT gate | FIXED |
| 5.61 | 事务隔离与 ACID 合规性 | CODE | 显式事务模式 + per-role 分池 | FIXED |
| 5.62 | 密钥轮换与密钥管理 | CODE | SecretProvider + derive_key_hkdf | FIXED |
| 5.64 | 连接池管理 | CODE | ThreadedConnectionPool + PoolExhaustedError | FIXED |
| 5.71 | 启动验证与 Fail-Fast | CODE | validate_config fail-fast | FIXED |
| 5.80 | 线程局部与 ContextVar 清理 | CODE | reset(token) 栈式恢复 | FIXED |
| 5.93 | __init__.py 污染 | A | NO-IMPORT-SIDE-EFFECT gate | PERMANENT-2 |
| 5.94 | 类型注解准确性 | A | GATE-ANY-ABUSE + mypy | FIXED |
| 5.96 | 布尔参数蔓延 | A | GATE-DEBT-BRIDGE | FIXED |
| 5.97 | 深层嵌套与圈复杂度 | A | NO-HIGH-COMPLEXITY gate | PERMANENT-1 |
| 5.99 | 错误消息一致性 | A | MSG-EXPOSURE + MSG-STYLE | FIXED |
| 5.100 | 异步资源生命周期 | D | —（AGENTS.md 规则约束） | PERMANENT-2 |
| 5.101 | 变量遮蔽与命名冲突 | D | —（R80 裁定不新增 gate） | PERMANENT-12 |
| 5.114 | Final/@final 强制 | D | —（已全量标注） | FIXED |
| 5.138 | 循环引用风险 | D | —（实证无真实循环） | FIXED |
| 5.139 | TODO/FIXME 技术债务标记 | D | —（零检出维度） | FIXED |
| 5.140 | 函数复杂度过高 | A | NO-HIGH-COMPLEXITY gate | PERMANENT-3 |
| 5.143 | API 契约一致性 | A | ssot_redefinition_gate + cross_layer_contracts.yaml | PERMANENT-14 |
| 5.144 | 资源清理顺序 | D | —（finally 模式已批量落地） | FIXED |
| 5.145 | 类型注解完整性 | A | GATE-ANY-ABUSE + mypy | PERMANENT-14 |
| 5.147 | 序列化/反序列化安全 | A | UNSAFE-DICT-SPREAD gate | FIXED |
| 5.150 | 设计模式误用 | D | —（R102 EXECUTE 测试先行） | PERMANENT-9 |
| 5.152 | 依赖方向违规 | A | NO-UPWARD-IMPORT gate | PERMANENT-10 |
| 5.153 | 命名一致性 | D | —（canonical 命名规范 SSoT 先行） | PERMANENT-11 |
| 5.155 | 配置验证完整性 | CODE | is_prod() + .env.example | FIXED |
| 5.156 | 测试覆盖率盲区 | A | META-TESTS-COVERAGE meta-gate | FIXED |
| 5.157 | 文档与代码同步深度 | A | DOC-REF-BROKEN gate | FIXED |
| 5.158 | 循环复杂度 | A | NO-HIGH-COMPLEXITY gate + scan_complexity.py | FIXED |
| 5.159 | 死代码 | A | ORPHAN-MODULE gate + M07 | FIXED |
| 5.160 | 魔法数字/字符串 | A | NO-BARE-SQL + NO-HARDCODED-URL gate | PERMANENT-1 |
| 5.165 | 全局状态管理 | D | —（Lock + 双重检查锁定） | FIXED |
| 5.169 | 文件句柄/资源泄漏 | D | —（try/finally 批量包装） | FIXED |
| 5.171 | 类型注解缺失或不一致 | A | GATE-ANY-ABUSE + mypy | FIXED |
| 5.174 | 导入循环/模块耦合 | A | NO-UPWARD-IMPORT gate | FIXED |
| 5.178 | 测试-源码一致性门禁缺失 | A | TEST-SOURCE-CONSISTENCY gate | FIXED |
| 5.179 | add_design_node granularity 硬编码 bug | CODE | granularity_vocabulary.yaml 词表 SSoT | FIXED |
| 5.180 | AI-11 审计遗留专项工程 | CODE | _registry.yaml 动态加载 + _CHECK_DISPATCH | PERMANENT-7 |

**审计汇总**：A 类 20 + CODE 类 22 + C 类 1 + D 类 11 + E 类 0 = 54 维度。

---

## 2. 逐维度设计决策

### 2.1 A 类（20 维度，已有硬阻断 gate）—— 不新增

**决策**：全部不新增。理由：A 类已有 commit 硬阻断 gate，违规即被阻断在 commit 阶段，零增量空间。新增 metric/gate 属冗余治理（违反原则 4 ROI 优先）。

逐维度理由：
- 5.1 / 5.179：GATE-VOCAB 已强制词表动态加载，M01/M05 监控趋势。
- 5.60 / 5.152 / 5.174：NO-UPWARD-IMPORT gate（priority=97）已防新增跨层依赖。
- 5.93：NO-IMPORT-SIDE-EFFECT gate（priority=103）已防 __init__ 副作用。
- 5.94 / 5.145 / 5.171：GATE-ANY-ABUSE 已防 Any 滥用，mypy 加严补充。
- 5.96：GATE-DEBT-BRIDGE 已防布尔参数蔓延。
- 5.97 / 5.140 / 5.158：NO-HIGH-COMPLEXITY gate（priority=85）已防高复杂度。
- 5.99：MSG-EXPOSURE（83）+ MSG-STYLE 已防错误消息泄露。
- 5.143：ssot_redefinition_gate + cross_layer_contracts.yaml SSoT 已防契约重复。
- 5.147：UNSAFE-DICT-SPREAD gate（66）已防序列化不安全。
- 5.156：META-TESTS-COVERAGE（95）已防测试盲区。
- 5.157：DOC-REF-BROKEN gate 已防文档引用断裂。
- 5.159：ORPHAN-MODULE gate + M07 已防死代码。
- 5.160：NO-BARE-SQL（87）+ NO-HARDCODED-URL（94）已防魔法数字/字符串。
- 5.178：TEST-SOURCE-CONSISTENCY gate（96）已防测试漂移。

### 2.2 CODE 类（22 维度，runtime/SSoT/CI/test 强制）—— 大部分不新增

**决策**：22 维度中 21 个不新增，仅 5.46 升级为 A 类（P0）。理由：CODE 类已有代码层强制（runtime 守卫 / SSoT 约束 / CI 检查 / 测试套件），违规要么在运行时被拦截（如 is_prod()、fail-fast），要么在 CI 被阻断（如 docker-build job），要么在测试被捕获（如迁移测试）。新增 gate 属冗余。

不新增的 21 维度：5.31 / 5.32 / 5.33（C 类，见 2.3）/ 5.34 / 5.35 / 5.36 / 5.37 / 5.38 / 5.39 / 5.40 / 5.41 / 5.52 / 5.57 / 5.58 / 5.61 / 5.62 / 5.64 / 5.71 / 5.80 / 5.155 / 5.179 / 5.180。

### 2.3 C 类（1 维度，仅 reconciler）—— 不新增

- **5.33 容灾与备份**：BACKUP-RECONCILER 已自动检测备份健康度。PERMANENT-2 项经 R102 裁定为 wontfix（单机项目 Restic 备份已覆盖，主从到 localhost 属过度工程）。不新增。

### 2.4 D 类（11 维度，仅文档约束）—— 重点设计

D 类是设计重点：无 gate、无 metric、无 reconciler，仅靠文档约束（君子协定）。按原则 1"靠阻断不靠自觉"，D 类是最高风险区。逐维度决策：

| 维度号 | 维度名 | 决策 | 形态 | ROI 理由 |
|---|---|---|---|---|
| 5.42 | 代码注释与 API 文档 | **做（P1）** | metric M22 | HIGH 严重度 + PERMANENT-1 + AI 可发现性关键。docstring 覆盖率趋势监控，warn-only 起步。 |
| 5.46 | 时间与时区处理 | **做（P0）** | 扩展 gate A | PERMANENT-1 + 100+ 处 naive/aware 混用历史。DATETIME-NOW-FORBIDDEN 已存在但仅覆盖生成器，扩展到 src/zephyr/ 全量硬阻断。 |
| 5.100 | 异步资源生命周期 | **做（P1）** | metric M23 | PERMANENT-2 + 12+ 文件 asyncio.run/get_event_loop。wontfix 但需趋势监控防增量。 |
| 5.101 | 变量遮蔽与命名冲突 | **做（P2）** | metric M24 | PERMANENT-12 + 42 处字段遮蔽。wontfix（R80 裁定实例属性不参与作用域链），但需 metric 监控趋势防增量。 |
| 5.114 | Final/@final 强制 | **做（P2）** | metric M25 | FIXED + 375 处模块级常量已标注。metric 监控回归防新增未标 Final 常量。 |
| 5.138 | 循环引用风险 | **不做** | — | FIXED + 实证无真实循环链。已改模块级直接 import，风险=0。新增 metric 属冗余。 |
| 5.139 | TODO/FIXME 技术债务标记 | **做（P1）** | metric M26 | FIXED + 零检出。metric 监控防新增 TODO/FIXME 污染（极低成本，单正则扫描）。 |
| 5.144 | 资源清理顺序 | **做（P1）** | metric M27 | FIXED + finally 模式已批量落地。metric 监控 open() 未在 with、资源未在 try/finally 防回归。 |
| 5.150 | 设计模式误用 | **不做** | — | PERMANENT-9 + R102 裁定 EXECUTE 测试先行。God Class 拆分是 29 项 EXECUTE 施工清单内容，不属防复发体系范畴（属存量修复）。 |
| 5.153 | 命名一致性 | **不做** | — | PERMANENT-11 + R102 裁定 canonical 命名规范 SSoT 先行。命名 gate 机械检测不可靠（语义问题），SSoT 先行后才设 gate（R102 裁定原则）。 |
| 5.165 | 全局状态管理 | **做（P2）** | metric M28 | FIXED 残留 2 项 LOW。metric 监控模块级单例无锁 double-check 模式防新增。 |
| 5.169 | 文件句柄/资源泄漏 | **做（P1）** | metric M29 | FIXED + try/finally 已批量包装。与 5.144 同族，metric 监控资源未在 try/finally 防回归。 |

D 类决策汇总：11 维度中 8 个做（升级为 A 或 B 类）、3 个不做（5.138 / 5.150 / 5.153）。

### 2.5 CODE 类补充设计（5.46 升级 + 4 个 metric 升级）

除 D 类外，部分 CODE 类维度虽已有 runtime 强制，但缺少增量监控，需补充 metric：

| 维度号 | 维度名 | 决策 | 形态 | ROI 理由 |
|---|---|---|---|---|
| 5.34 | 环境隔离 | **做（P2）** | metric M30 | FIXED + ZEPHYR_ENV 与枚举不匹配历史。metric 监控 ZEPHYR_ENV 值是否在枚举内防回归。 |
| 5.35 | API 版本管理 | **做（P2）** | metric M31 | FIXED + MCP 工具无 version 历史。metric 监控 mcp.json version 字段覆盖率防回归。 |

---

## 3. 架构原则内化

### 3.1 最终分布（54 维度）

| 分类 | 数量 | 说明 |
|---|---|---|
| A（硬阻断 gate） | 21 | 原 20 + P0 升级 5.46 |
| B（dashboard metric） | 10 | P1 新增 5 + P2 新增 5 |
| C（reconciler） | 1 | 5.33 维持 |
| CODE（runtime/SSoT/CI/test） | 19 | 原 22 - 5.46(P0) - 5.34(P2) - 5.35(P2) = 19 |
| D（文档约束） | 3 | 原 11 - 8(升级) = 3（5.138 / 5.150 / 5.153） |
| **合计** | **54** | |

### 3.2 原则对照

| 原则 | 落地验证 |
|---|---|
| ①靠阻断不靠自觉 | P0 扩展 gate 硬阻断 5.46；P1/P2 metric 趋势监控非阻断（warn-only 起步，未来可升级硬阻断） |
| ②防治理自身漂移 | 11 项做 / 43 项不做（治理组件数 11 ≤ 被治理维度数 54）；每项 MUST 登记 capability + creation_token + 配测试 + 带豁免 |
| ③向内收 | P0 扩展现有 DATETIME-NOW-FORBIDDEN gate（不新建）；P1/P2 扩展现有 architecture_health_dashboard METRICS（不新建系统） |
| ④ROI 优先 | 43 项不做有明确理由（已充分覆盖 / 风险=0 / 成本>收益 / R102 裁定 wontfix） |
| ⑤SSoT 真源唯一 | gate 真源 gate_registry.yaml；metric 真源 architecture_health_dashboard.py METRICS；词表动态加载不硬编码 |

---

## 4. 汇总设计表（施工总工单）

### 4.1 做的 11 项

| # | 维度号 | 维度名 | 覆盖现状 | 决策 | 形态 | 范围 | 优先级 | ROI 理由 |
|---|---|---|---|---|---|---|---|---|
| 1 | 5.46 | 时间与时区处理 | CODE | 做 | 扩展 gate A | src/zephyr/ 全量，禁止 datetime.now()/time.time() 用于 TTL，noqa 豁免 | P0 | PERMANENT-1 + 100+ 处历史 + gate 已存在仅扩展检测面 |
| 2 | 5.42 | 代码注释与 API 文档 | D | 做 | metric M22 | src/zephyr/ 公共函数 docstring 覆盖率 | P1 | HIGH 严重度 + AI 可发现性关键 |
| 3 | 5.100 | 异步资源生命周期 | D | 做 | metric M23 | asyncio.run / get_event_loop 调用计数 | P1 | PERMANENT-2 + 12+ 文件 + 防增量 |
| 4 | 5.139 | TODO/FIXME 技术债务标记 | D | 做 | metric M26 | TODO/FIXME 计数（极低成本正则扫描） | P1 | FIXED 零检出 + 极低实施成本 + 防污染 |
| 5 | 5.144 | 资源清理顺序 | D | 做 | metric M27 | open() 未在 with 语句计数 | P1 | FIXED + 防回归 |
| 6 | 5.169 | 文件句柄/资源泄漏 | D | 做 | metric M29 | 资源未在 try/finally 计数 | P1 | FIXED + 与 5.144 同族防回归 |
| 7 | 5.101 | 变量遮蔽与命名冲突 | D | 做 | metric M24 | 数据类字段遮蔽内置名计数 | P2 | PERMANENT-12 + 防增量趋势监控 |
| 8 | 5.114 | Final/@final 强制 | D | 做 | metric M25 | 模块级常量未标 Final 计数 | P2 | FIXED + 375 处已标 + 防回归 |
| 9 | 5.165 | 全局状态管理 | D | 做 | metric M28 | 模块级单例无锁 double-check 计数 | P2 | FIXED 残留 2 + 防新增 |
| 10 | 5.34 | 环境隔离 | CODE | 做 | metric M30 | ZEPHYR_ENV 值是否在枚举内 | P2 | FIXED + 防回归 |
| 11 | 5.35 | API 版本管理 | CODE | 做 | metric M31 | mcp.json version 字段覆盖率 | P2 | FIXED + 防回归 |

### 4.2 不做的 43 项

| 分类 | 维度号 | 不做理由 |
|---|---|---|
| A 类（20） | 5.1/5.60/5.93/5.94/5.96/5.97/5.99/5.140/5.143/5.145/5.147/5.152/5.156/5.157/5.158/5.159/5.160/5.171/5.174/5.178/5.179 | 已有硬阻断 gate，零增量空间，新增属冗余治理 |
| C 类（1） | 5.33 | BACKUP-RECONCILER 已覆盖，R102 wontfix |
| CODE 类（19） | 5.31/5.32/5.37/5.38/5.39/5.40/5.41/5.52/5.57/5.58/5.61/5.62/5.64/5.71/5.80/5.155/5.180 | runtime/SSoT/CI/test 强制已覆盖，新增 gate 属冗余 |
| D 类（3） | 5.138/5.150/5.153 | 5.138 风险=0；5.150 属 R102 EXECUTE 存量修复非防复发；5.153 命名 gate 机械检测不可靠需 SSoT 先行 |

---

## 5. 施工计划

### 5.1 P0：扩展 DATETIME-NOW-FORBIDDEN gate 覆盖 5.46

**目标**：把 DATETIME-NOW-FORBIDDEN gate 的检测面从"生成器"扩展到 `src/zephyr/` 全量，硬阻断 `datetime.now()` / `time.time()` 用于 TTL 的误用。

**实施步骤**：
1. ✅ 读 `src/zephyr/gov_enforcement/commit_gates/datetime_now_forbidden_gate.py` 了解现有检测逻辑。
2. ✅ 扩展检测范围：从生成器扩展到 `src/zephyr/**/*.py`。
3. ✅ 检测模式：`datetime.now()`（无 tz 参数）、`time.time()` 用于 TTL 计算（上下文启发式）。
4. ✅ 豁免机制：`# noqa: m46-time` 标记，登记到 `noqa_exempt_registry.yaml`。
5. ✅ fail-closed：违规即阻断 commit。
6. ✅ priority：维持现有（不插入新位置）。
7. ✅ 配测试：`tests/governance/commit_gates/test_datetime_now_forbidden_gate.py`，违规样本拦截 + 合法样本零误伤。
8. ✅ 登记 capability + creation_token（gate 已登记，扩展检测面无需新增）。
9. ⏳ 更新 `architecture_debt_registry.md` §四 5.46 行防复发机制为 "DATETIME-NOW-FORBIDDEN gate（扩展全量）"（待后续同步）。

**P0 完成状态**：✅ 代码+测试完成（commit c6b8b08a46 + merge 5e2d0659b8），noqa 标记从 `datetime-now` 改为 `m46-time`（与 §四 5.46 维度号对齐）。

### 5.2 P1：新增 5 个 dashboard metric（M22-M29）

**目标**：在 `architecture_health_dashboard.py` METRICS 列表新增 5 个 metric，warn-only 起步。

| metric_id | 名称 | 检测逻辑 | 对应维度 |
|---|---|---|---|
| M22 | docstring 覆盖率倒数 | AST 扫描 src/zephyr/ 公共函数（非 _ 开头）无 docstring 计数 | 5.42 |
| M23 | asyncio.run/get_event_loop 调用数 | 正则 + AST 扫描 asyncio.run( / get_event_loop( 计数 | 5.100 |
| M26 | TODO/FIXME 计数 | 正则扫描 # TODO / # FIXME 计数 | 5.139 |
| M27 | open() 未在 with 语句计数 | AST 扫描 open() 调用不在 with 上下文管理器内 | 5.144 |
| M29 | 资源未在 try/finally 计数 | AST 扫描 acquire/release 模式不在 try/finally 内 | 5.169 |

**实施步骤（每个 metric）**：
1. ✅ 在 `architecture_health_dashboard.py` 实现 `metric_NN_xxx()` 函数。
2. ✅ 加入 METRICS 列表（20→25 项）。
3. ✅ 同步 `architecture_debt_registry.md` §六 指标清单（M01-M21 → M01-M29）+ §四 5.42/5.100/5.139/5.144/5.169 防复发列。
4. ✅ 配测试：`tests/governance/test_architecture_health_dashboard_metrics.py`（31 测试全通过）。
5. ✅ 登记 capability（dashboard 已登记，新增 metric 无需新 capability_token）。
6. ✅ 豁免机制：metric 为 warn-only，无需 noqa（趋势监控非阻断）。

**P1 完成状态**：✅ 全部完成。实测读数：M22=6092, M23=19, M26=7, M27=2, M29=31。

### 5.3 P2：新增 5 个 dashboard metric（M24-M31）

| metric_id | 名称 | 检测逻辑 | 对应维度 |
|---|---|---|---|
| M24 | 字段遮蔽计数 | AST 扫描 dataclass/Pydantic 字段名与内置名相同（id/file/type/format/hash/open/input/round） | 5.101 |
| M25 | 模块级常量未标 Final 计数 | AST 扫描模块级赋值无 Final[...] 标注 | 5.114 |
| M28 | 模块级单例无锁 double-check 计数 | AST 模式匹配 `_instance = None` + 无锁赋值 | 5.165 |
| M30 | ZEPHYR_ENV 枚举一致性 | 扫描 os.environ["ZEPHYR_ENV"] 值是否在枚举集合内 | 5.34 |
| M31 | MCP version 字段覆盖率 | 扫描 mcp.json 工具定义是否含 version 字段 | 5.35 |

**实施步骤**：同 P1。

**P2 完成状态**：✅ 全部完成。实测读数：M24=40, M25=1748, M28=1, M30=5, M31=0。测试 34/34 通过。

---

## 6. 设计评审清单

### 6.1 必须满足的硬约束
- [x] 54 维度全覆盖（A 21 + B 10 + C 1 + CODE 19 + D 3 = 54）
- [x] 治理组件数（11）≤ 被治理维度数（54）
- [x] 每项"做"有明确形态、范围、优先级、ROI 理由
- [x] 每项"不做"有明确理由（已覆盖 / 风险=0 / 成本>收益 / R102 裁定）
- [x] 向内收：P0 扩展现有 gate，P1/P2 扩展现有 dashboard
- [x] SSoT：gate 真源 gate_registry.yaml，metric 真源 dashboard METRICS

### 6.2 施工前置条件
- [x] 用户评审通过本设计文档
- [x] session_worktree 启动新 session
- [x] capability_canonical_file_registry.yaml 已登记 anti_recurrence_design creation_token

### 6.3 施工后验证
- [x] P0：DATETIME-NOW-FORBIDDEN gate 违规样本拦截 + 合法样本零误伤（commit c6b8b08a46 + merge 5e2d0659b8）
- [x] P1：M22/M23/M26/M27/M29 仪表盘读数正常（M22=6092, M23=19, M26=7, M27=2, M29=31）
- [x] P2：M24/M25/M28/M30/M31 仪表盘读数正常（M24=40, M25=1748, M28=1, M30=5, M31=0）
- [ ] 全量：`PYTHONPATH=src python scripts/governance/architecture_health_dashboard.py` 无回归
- [ ] 模拟再犯：故意引入 datetime.now() / TODO / open() 不在 with 验证检测

---

> **评审请求**：请用户评审本设计文档。评审通过后进入第二步施工（P0 → P1 → P2 逐项实现）。
