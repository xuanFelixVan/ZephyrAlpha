---
module_id: VIEW-AUDIT-DIMENSIONS
title: Audit Dimensions Checklist / 审计审查维度清单（54 维度基座）
doc_type: architecture_view
ttl: permanent
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-07-24
superseded_by: null
supersedes: null
related_rationale:
- 裁定#222
related_open_questions: []
tags:
- audit
- checklist
- dimensions
- governance
summary: 架构审计审查的维度清单基座——54 个审计维度，每维度保留抽象概念（核心问题 + 病根归属 + 防复发机制）。源自 architecture_debt_registry v2.0.0 §四（已归档）。状态列反映当前 wontfix 情况（FIXED=清零，PERMANENT-N=残留 N 项 wontfix，详见 architecture_issue_registry.yaml #ARCH-DEBT-001~006）。增量违规由架构健康度仪表盘 M01-M31 实时发现，本清单不手工维护违规数据。
date: '2026-07-24'
ttl: permanent
---

# Audit Dimensions Checklist / 审计审查维度清单

> **文档性质**：未来审计审查系统的维度基座——54 个审计维度，每维度一行抽象概念。
> **来源**：源自 `architecture_debt_registry.md` v2.0.0 §四（已归档至 [`docs/_archive/architecture_debt_registry_v2.md`](file:///d:/ZephyrAlpha/docs/_archive/architecture_debt_registry_v2.md)）。
> **状态口径**：`FIXED` = 该维度全部清零；`PERMANENT-N` = 残留 N 项 wontfix（详情见 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) #ARCH-DEBT-001~006，裁定#222）。
> **合计**：54 维度 = 48 FIXED + 6 PERMANENT（共 40 项 wontfix）。
> **增量违规**：由架构健康度仪表盘（M01-M31，post-commit 自动生成）实时发现，本清单不手工维护违规数据。

---

## 维度清单

| 维度号 | 维度名 | 核心问题 | 病根归属 | 防复发 gate/metric | 状态 |
|---|---|---|---|---|---|
| 5.1 | SSoT 真源唯一性 | 文件复制 + 词表硬编码 + 重复簇 + DB 连接真源冲突 | 根因 1/2 | GATE-VOCAB + GATE-SSOT（capability 查重）+ M01/M05 | FIXED |
| 5.31 | 构建打包 | Docker CMD 幻影模块 + 无 .dockerignore + 版本号三重真源 + 非多阶段构建 | 根因 5 | CI build-package / docker-build job | FIXED |
| 5.32 | 数据迁移策略 | 硬编码 Win 路径 + TRUNCATE 后失败全损 + 零测试 + 迁移孤儿 | 根因 4 | 迁移测试套件 | FIXED |
| 5.33 | 容灾与备份 | PG 无 pg_dump + 备份工具过时 + 无 RTO/RPO + 单机 SPOF | 根因 1 | BACKUP-RECONCILER + Restic 加密备份 + config/dr_policy.yaml | PERMANENT-2 |
| 5.34 | 环境隔离 | ZEPHYR_ENV 与枚举不匹配 + 测试 SQLite 生产 PG + is_prod() 零调用 | 根因 4 | PG 测试双轨 + is_prod() 生产写守卫 + M30 + ZEPHYR-ENV-DIRECT-ACCESS gate | FIXED |
| 5.35 | API 版本管理 | MCP 工具无 version + api_version_contract 死代码 + 无 deprecation | 根因 5 | mcp.json version 字段 + ERR_API_SUNSET + M31 + MCP-VERSION-FIELD gate | FIXED |
| 5.36 | 限流与配额 | 限流器碎片化 + 无 per-user 配额 + TokenBucket 竞态 + 配置不加载 | 根因 5 | shared/infra/limiter.py canonical + ERR_RATE_LIMITED | FIXED |
| 5.37 | 审计日志完整性 | write_to_core no-op + verify() 永返 True + Merkle stub + 裸 git commit | 根因 5 | events.jsonl hash chain + GitCommitGateway._commit_auto | FIXED |
| 5.38 | 特性开关 | 系统碎片化 + global_flag_registry 零调用 + 默认 ON 违反安全默认 | 根因 5 | shared/foundation/flags.py canonical + _feature_flag_enabled 守护点 | FIXED |
| 5.39 | 可观测性深度 | health_monitor 丢弃指标 + counter() 幻影方法 + trace 断链 + SLOManager 死代码 | 根因 5 | span_stub contextvars 统一 + SLOManager 单例 + boot 订阅 | FIXED |
| 5.40 | 幂等性与重试语义 | 重试无 Idempotency-Key + DLQ stub + webhook pass | 根因 5 | Idempotency-Key 稳定幂等键 + DLQ 真重试 + 持久化 IdempotencyStore | FIXED |
| 5.41 | 状态机正确性 | 无转换校验 + 无锁 + force_state 绕过终态 + 假实现 | 根因 5 | VALID_TRANSITIONS 转换表 + RLock + 审计 | FIXED |
| 5.42 | 代码注释与 API 文档 | 核心函数缺 docstring + baseline_manager 方法错误嵌套 | 根因 5 | M22 docstring 覆盖率监控（warn-only） | FIXED |
| 5.46 | 时间与时区处理 | time.time() 用于 TTL + naive/aware datetime 混用 | 根因 5 | now_utc() 全局统一 + DATETIME-NOW-FORBIDDEN gate | FIXED |
| 5.52 | 异步/同步边界 | asyncio.run 在 async 上下文静默绕过 + run_coroutine_threadsafe 死锁 | 根因 5 | async_utils.run_coroutine_sync canonical + LSG fail-closed | FIXED |
| 5.57 | 事件排序与因果一致性 | 事件 ID 秒级碰撞 + 异常静默吞没 + 完整性校验空操作 | 根因 5 | task_events seq + prev_hash 链（migration v32） | FIXED |
| 5.58 | 分布式锁正确性 | 锁释放不验证持有者 + 无 fencing token + 无自动续期 + TOCTOU 竞态 | 根因 5 | next_fencing_token + SyncLockRenewer | FIXED |
| 5.60 | 模块耦合度深度 | governance↔trading 循环依赖 + shared 跨层 + compliance re-export 壳 | 根因 5 | NO-UPWARD-IMPORT gate | FIXED |
| 5.61 | 事务隔离与 ACID 合规性 | batch_review 非原子 + PG autocommit + retry_count 事务外更新 + 连接池竞态 | 根因 5 | 显式事务模式 + per-role 分池 + Condition 共用锁 | FIXED |
| 5.62 | 密钥轮换与密钥管理 | HMAC 密钥硬编码 + 调用未传 hmac_key + 仅检测不轮换 | 根因 5 | SecretProvider 注入无兜底 + derive_key_hkdf（RFC5869） | FIXED |
| 5.64 | 连接池管理 | PG 无连接池 + 单连接跨线程共享 + 池耗尽无限创建 + 泄漏检测失效 | 根因 5 | ThreadedConnectionPool per-role 分池 + PoolExhaustedError | FIXED |
| 5.71 | 启动验证与 Fail-Fast | boot() 缺关键配置验证 + validate_all 仅验证 import + 失败不阻断 | 根因 5 | validate_config fail-fast 启动校验 + DISCONNECTED 阈值 | FIXED |
| 5.80 | 线程局部与 ContextVar 清理 | set_request_id 丢弃 Token + grant_allowance 用 set 非 reset + 令牌泄漏 | 根因 5 | reset(token) 栈式恢复 + 跨线程连接注册表 | FIXED |
| 5.93 | __init__.py 污染 | zephyr/__init__ 副作用 + 幻影子包 + __all__ 无 import + import * | 根因 5 | NO-IMPORT-SIDE-EFFECT gate（priority=103） | PERMANENT-1 |
| 5.94 | 类型注解准确性 | `-> Self` 系统性误用 + 裸泛型 + Any 滥用 + 公共 API 缺注解 | 根因 5 | GATE-ANY-ABUSE + mypy 加严 | FIXED |
| 5.96 | 布尔参数蔓延 | TriggerDecision 3 布尔冗余 + _calculate_trust 3 布尔 + 行为切换布尔 | 根因 5 | GATE-DEBT-BRIDGE（DEBT-1/2/3，commit + CI 双硬阻断） | FIXED |
| 5.97 | 深层嵌套与圈复杂度 | evolve 148 行 5 层 + register_boot_hooks 130 行 7 闭包 + dispatch 104 行 | 根因 5 | NO-HIGH-COMPLEXITY gate（priority=85） | FIXED |
| 5.99 | 错误消息一致性 | SQL 泄露 + 中英混用 + 异常类型不一致 + MCP 错误码不统一 | 根因 5 | MSG-EXPOSURE + MSG-STYLE + error_code_registry.yaml SSoT | FIXED |
| 5.100 | 异步资源生命周期 | limiter 锁反模式 + pipeline 死锁 + 阻塞 IO + get_event_loop 弃用 + asyncio.run 高频 | 根因 5 | M23 asyncio 调用监控 + R103 治本 + ASYNCIO-RUN-IN-CONTEXT gate | FIXED |
| 5.101 | 变量遮蔽与命名冲突 | 参数遮蔽 id + 数据类字段遮蔽内置名 + 模块名冲突标准库 | 根因 5 | M24 字段遮蔽计数监控（warn-only，R80 裁定不新增 gate） | PERMANENT-12 |
| 5.114 | Final/@final 强制 | 可变 dict 常量无 Final + 模块级常量未标 Final + @final 零使用 | 根因 5 | M25 + MUTABLE-CONST-WITHOUT-FINAL gate | FIXED |
| 5.138 | 循环引用风险 | 根 __init__ Timer 延迟规避循环 + 包内循环 + try/except ImportError 容错 | 根因 5 | —（实证无真实循环链，已改模块级直接 import） | FIXED |
| 5.139 | TODO/FIXME 技术债务标记 | 仅 1 处真实 TODO（已关联工单），代码库技术债务标记极清洁 | —（零检出维度） | M26 TODO/FIXME 计数监控（warn-only） | FIXED |
| 5.140 | 函数复杂度过高 | dispatch 461 行/7 层/30+ 分支 + integration 模块 8 个超标函数 | 根因 5 | NO-HIGH-COMPLEXITY gate + R103 治本 | FIXED |
| 5.143 | API 契约一致性 | LSP 违规 + Protocol 误用为基类 + 重复 ABC 各自独立 _registry | 根因 1/5 | ssot_redefinition_gate + cross_layer_contracts.yaml SSoT | PERMANENT-14 |
| 5.144 | 资源清理顺序 | 核心关闭路径无异常隔离 + sqlite 清理缺 finally + 子进程管道关闭顺序错 | 根因 5 | M27 + OPEN-WITHOUT-WITH gate | FIXED |
| 5.145 | 类型注解完整性 | 34 个文件 Any 滥用 >5 处 + audit_trail 三件套完全无类型 + 隐藏 NameError | 根因 5 | GATE-ANY-ABUSE（Phase 3 commit 阻断）+ mypy 加严 | FIXED |
| 5.147 | 序列化/反序列化安全 | joblib.load 无校验 + MCP Content-Length 无上限 + json.dumps(default=str) 类型丢失 | 根因 5 | UNSAFE-DICT-SPREAD gate + serialization.py SSoT | FIXED |
| 5.150 | 设计模式误用 | God Class + Shotgun Surgery + Long Parameter List + Data Class | 根因 5 | —（设计模式 AST gate 列为可选未来专项） | PERMANENT-2 |
| 5.152 | 依赖方向违规 | shared 底层向上依赖 + governance→trading shim 规模化 | 根因 5 | NO-UPWARD-IMPORT gate（priority=97） | FIXED |
| 5.153 | 命名一致性 | 幽灵 db_path 参数 + 同一动作多种命名 + CT_XX_XXX + 布尔命名不规范 | 根因 5 | —（canonical 命名规范 SSoT 先行后才设 gate） | PERMANENT-9 |
| 5.155 | 配置验证完整性 | HMAC 硬编码 + 完整性校验恒 True + int(env) 无防护 + 三层校验同时失效 | 根因 5 | is_prod() 环境感知（dev 降级/生产阻断）+ .env.example 文档化 | FIXED |
| 5.156 | 测试覆盖率盲区 | 2 处测试因路径错误从不运行 + 核心业务逻辑无测试 + merkle 无篡改测试 | 根因 5 | META-TESTS-COVERAGE meta-gate（priority=95，#ARCH-057） | FIXED |
| 5.157 | 文档与代码同步深度 | 连字符 vs 下划线路径漂移 + 函数名颠倒 + 版本漂移 + shim 缺标记 | 根因 1 | DOC-REF-BROKEN gate | FIXED |
| 5.158 | 循环复杂度 | _compute_metrics_generic 30+ + evaluate 4 路分发 + _run_once 5 阶段流水线 | 根因 5 | NO-HIGH-COMPLEXITY gate + scan_complexity.py 存量监控 | FIXED |
| 5.159 | 死代码 | governance/governance 错位包 + rollback/governance + 死重复文件 | 根因 1 | ORPHAN-MODULE gate + M07 指标 | FIXED |
| 5.160 | 魔法数字/字符串 | task_repo 裸 SQL + apply_depgraph SQL + 安全扫描器正则阈值不一致 | 根因 2 | NO-BARE-SQL gate + NO-HARDCODED-URL gate + R103 治本 | FIXED |
| 5.165 | 全局状态管理 | 模块级单例无锁 double-check + import 时启 Timer + asyncio+全局状态冲突 | 根因 5 | M28 单例无锁 double-check 监控（warn-only） | FIXED |
| 5.169 | 文件句柄/资源泄漏 | fd 泄漏 + urlopen 未 close + sqlite3 无 try/finally + os.open 泄漏 | 根因 5 | M29 资源未在 try/finally 监控（warn-only） | FIXED |
| 5.171 | 类型注解缺失或不一致 | public API 无注解 + Any 滥用 + 返回类型不符 + stub-style 无注解 | 根因 5 | GATE-ANY-ABUSE + mypy 加严 | FIXED |
| 5.174 | 导入循环/模块耦合 | shared 退化代理壳 + shared↔integration 双向耦合 + 延迟导入堆叠 | 根因 5 | NO-UPWARD-IMPORT gate（priority=97） | FIXED |
| 5.178 | 测试-源码一致性门禁缺失 | 5 种测试漂移（名称/Schema/Mock/阈值/字符串匹配） | 根因 1 | TEST-SOURCE-CONSISTENCY gate（priority=96） | FIXED |
| 5.179 | add_design_node granularity 硬编码 bug | granularity 硬编码 'directory' 致单文件模块设计态登记铁律死锁 | 根因 2 | granularity_vocabulary.yaml 词表 SSoT（PS-VOC-035） | FIXED |
| 5.180 | AI-11 审计遗留专项工程 | gate_engine 硬编码双真源 + check_types 死代码 + subprocess 绕过 _run_git | 根因 1/5 | _registry.yaml 动态加载 + _CHECK_DISPATCH 分发表 | FIXED |

---

## 硬门禁覆盖率审计（2026-07-23）

54 维度中 **26 个有 P0 硬 commit gate**（提交时强制阻断），**28 个无硬 gate**（仅 warn-only 监控 / CI / 测试 / canonical 重构 / 词表 SSoT / 无防复发）。

**无硬 gate 的 28 个维度**按防复发机制分类：

| 防复发类型 | 维度 | 说明 |
|---|---|---|
| 仅 warn-only 监控（M-xx） | 5.42 / 5.101 / 5.139 / 5.165 / 5.169 | 仪表盘发警告但不阻断提交；5.101 为 PERMANENT wontfix |
| CI / 测试 | 5.31 / 5.32 | CI pipeline 或测试套件兜底，非 commit 时阻断 |
| reconciler | 5.33 | post-commit 事件驱动兜底，非 commit 时阻断（PERMANENT wontfix） |
| canonical 重构 / 模式落地 | 5.36 / 5.37 / 5.38 / 5.39 / 5.40 / 5.41 / 5.52 / 5.57 / 5.58 / 5.61 / 5.62 / 5.64 / 5.71 / 5.80 / 5.155 / 5.180 | 存量已修复 + canonical pattern 指引，但无 commit gate 防新增 |
| 词表 SSoT | 5.179 | granularity_vocabulary.yaml 被 GATE-VOCAB 间接覆盖 |
| 无防复发 | 5.138 / 5.150 / 5.153 | 5.138 实证无真实循环链（不需 gate）；5.150/5.153 为 PERMANENT wontfix |

**建议**：canonical 重构类 16 个维度（存量已清零）如需进一步防新增，可逐步补 P0 硬 gate；warn-only 类 4 个非 PERMANENT 维度（5.42/5.139/5.165/5.169）可考虑升级为硬 gate。PERMANENT wontfix 维度（5.33/5.101/5.150/5.153）因裁定不修复，补 gate 优先级最低。

---

## wontfix 维度详情（40 项，裁定#222 确认）

6 个 PERMANENT 维度的 wontfix 详情已登记在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)：

| #ARCH-DEBT | 维度 | wontfix 项数 | 裁定真源 |
|---|---|:---:|---|
| #ARCH-DEBT-001 | 5.33 容灾与备份 | 2 | 裁定#222（R102 RATIFY） |
| #ARCH-DEBT-002 | 5.93 __init__.py 污染 | 1 | 裁定#222（R102 RATIFY） |
| #ARCH-DEBT-003 | 5.101 变量遮蔽与命名冲突 | 12 | 裁定#222（R80+R102 RATIFY） |
| #ARCH-DEBT-004 | 5.143 API 契约一致性 | 14 | 裁定#222（R82+R102 RATIFY） |
| #ARCH-DEBT-005 | 5.150 设计模式误用 | 2 | 裁定#222（R102 RATIFY） |
| #ARCH-DEBT-006 | 5.153 命名一致性 | 9 | 裁定#222（R102 RATIFY） |

**翻案条件**：MUST 经架构师新裁定（裁定#NNN）并更新 #ARCH-DEBT-NNN 条目的 related_adjudication + last_updated。
