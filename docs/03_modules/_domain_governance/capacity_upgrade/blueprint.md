---
module_id: MOD-GOV-CAP-001
activation_phase: requires_100ai
submodule_path: src/zephyr/governance
title: "Governance Domain 容量升级蓝图 — 10K脚本/1.5K模块/100AI并发"
doc_type: blueprint
status: Active
version: "0.1.0"
layer: cross_layer
layer_name: domain
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-16"
ttl: permanent
last_updated: "2026-05-16"
construction_progress: partially_implemented
actual_disk_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_governance\\capacity_upgrade\\blueprint.md"
template_for: blueprint
generation: 2
functional_domain: governance
parent_module: "MOD-GOVERNANCE"
belongs_to: "MOD-GOVERNANCE"
rule_form: structural
scope: global
stability: evolving
verifiability: automated
priority: P1
runtime_plane: warm
summary: "治理域容量升级蓝图——从MOD-023拆分。覆盖SLO/D-GAP/分层执行/熔断器/分片存储/GPU加速/施工路线图/测试矩阵。Phase C全部未完成。"
depends_on:
  - target: "MOD-GOVERNANCE"
    at: "§3"
    why: "治理域集成契约——容量升级的G-CT契约定义在MOD-023"
  - target: "MOD-DATABASE"
    at: "§9"
    why: "Database——分片存储直接依赖"
  - target: "MOD-INF-016"
    at: "§3"
    why: "Shared Core——BulkheadExecutorV2/AdmissionController等共享组件"
ssot_claims:
  - claim: "治理域容量升级架构(SLO/分片存储/GPU加速/熔断器)"
    scope: layer
  - claim: "容量升级施工路线图与测试矩阵"
    scope: layer
  - claim: "治理域容量升级D-GAP-01~12设计方案真源"
    scope: layer
---

# Governance Domain 容量升级蓝图 — 10K脚本/1.5K模块/100AI并发

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules DOM-GOV-CAP-001`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **module_id**: DOM-GOV-CAP-001 | **parent**: MOD-GOVERNANCE | **version**: 0.1.0
>
> 本蓝图从 MOD-GOVERNANCE 拆分，专注容量升级设计。未包含的章节（§3.9 脚本生命周期、§3.14 可观测性、§3.15 维度扩展等）见 MOD-GOVERNANCE 原蓝图。

### §0.1 代码文件清单

> 本蓝图为纯设计蓝图，无直接管辖代码文件。相关代码归属 MOD-GOVERNANCE（治理域集成蓝图）。

## 1. 容量升级设计与 SLO（v0.2.0 升版核心章节）

> 本章是蓝图升级的 **需求规格**，§6 是 **施工计划**。

### 1.1 升级驱动

| 维度 | v0.1.0 假设 | v0.2.0 目标 | 倍数 |
|------|------------|------------|:---:|
| 治理域模块数 | 8（MOD-INF-018~025） | 8（不变，但需适配 1,500 业务模块） | 1× |
| 被治理的业务模块数 | ~51 | 1,500 | **29×** |
| 治理脚本数 | 268 | 10,000（设计上限） | **37×** |
| 并发 AI Agent 数 | 1（单 session） | 100 | **100×** |
| 增量扫描脚本数 | 全量 268 | 15-30（日常增量） | — |
| 全量扫描耗时 | 3.5 小时 | 全量作为周检可选，不阻塞日常 | — |
| 执行模式 | 全量默认 | 增量默认，全量可选 | — |

### 1.2 容量目标与 SLO

| SLO 指标 | 目标值 | 测量窗口 | 测量方式 |
|---------|--------|:---:|------|
| **SLO-1: 增量扫描延迟** | p50 < 30s, p95 < 60s, p99 < 120s | 滚动 24h | `sla_metrics.jsonl` + `compute_sla_metrics.py` |
| **SLO-2: 增量扫描吞吐** | 100 AI 并发 × 20 脚本/AI = 2,000 脚本/min 调度能力 | 峰值 5min | BulkheadExecutor pool stats |
| **SLO-3: Phase Gate 启动延迟** | Session 冷启动检查 < 10s（含 46 gate） | 每次 session 启动 | `session_startup_check.py` |
| **SLO-4: Audit 写入延迟** | p50 < 10ms, p99 < 100ms（单条写入） | 滚动 1h | SQLite WAL + ShardRouter 分片 |
| **SLO-5: 全量扫描完成时间** | < 4 小时（10,000 脚本，40 workers） | 每次全量扫描 | `run_all.py --dimensions D1-D12` |
| **SLO-6: 可用性** | 治理系统自身故障导致扫描不可用的时间 < 5min/月（99.99%） | 滚动 30d | Kill Switch 状态 + circuit breaker trip 次数 |
| **SLO-7: Error Budget** | 月 error budget = 43,200s × (1 - 0.9999) = 259s | 日历月 | `manage_error_budget.py` |

**SLO 违反的升级策略**：
- Error budget 消耗 > 50%：自动告警 → Escalation Protocol
- Error budget 消耗 > 80%：冻结非 P0 扫描，仅保留 Quick 维度（D1-D4）
- Error budget 耗尽：Kill Switch 激活，停止所有自动扫描，等待 Owner 裁定

### 1.3 蓝图设计缺失盘点（12 项）

| # | 缺失项 | 严重级别 | 影响范围 | 新增章节/契约 |
|---|--------|:---:|------|------|
| **D-GAP-01** | 无容量/SLO/SLA 定义——蓝图未声明治理域自身的性能承诺 | P0 | 扩容没有验收标准 | → **§1.2**（本节已补） |
| **D-GAP-02** | 无脚本生命周期治理模型——10,000 脚本如何 onboarding、版本化、退役？ | P0 | 脚本腐化失控，存量脚本无人维护 | → MOD-GOVERNANCE **§3.9 脚本生命周期治理** |
| **D-GAP-03** | 无模块→脚本映射契约——业务模块和治理脚本之间没有声明式绑定 | P0 | 增量扫描只能维度级（粗粒度），无法精准到脚本级 | → **G-CT-009: Module→Script 映射契约** |
| **D-GAP-04** | 无 tiered execution model（分层执行模型）——所有脚本同等对待 | P0 | hot-path 慢脚本阻塞 quick 维度，单脚本超时拖垮整池 | → **§2 分层执行模型** |
| **D-GAP-05** | 无熔断器策略定义——CircuitBreaker 代码存在但何时熔断、如何恢复无规范 | P1 | 连锁故障无防护，熔断后无人知道怎么恢复 | → **§3 熔断器策略** |
| **D-GAP-06** | 无分片存储架构——ShardRouter 代码存在但蓝图未定义分片设计 | P1 | 1500 模块共享单 SQLite → 锁竞争吃掉所有并发收益 | → **§4 分片存储架构** |
| **D-GAP-07** | 无多 AI 协调模型——100 AI 同时运行时如何避免相互踩踏 | P0 | L0 ProcessLock 是单进程锁，100 AI 排队等锁；且去掉 L0 后需要新的文件并发写入保护方案 | → **G-CT-010: 多 Agent 协调契约 + 文件写入三层防护** |
| **D-GAP-08** | 无 GPU/异构计算策略——3090 24GB 完全闲置 | P1 | D12 AI 幻觉检测全 CPU，浪费 10-50× 加速潜力 | → **§5 GPU 加速策略** |
| **D-GAP-09** | 无可观测性/告警架构——指标采集了但无告警规则、无 dashboard | P1 | 系统出问题靠人肉发现 | → MOD-GOVERNANCE **§3.14 可观测性架构** |
| **D-GAP-10** | 12 维度模型缺 D10——性能治理 0 脚本，扩容后 D13/D14 也缺失 | P1 | 容量/依赖健康度无自动化覆盖 | → MOD-GOVERNANCE **§3.15 维度模型扩展** |
| **D-GAP-11** | 无业务模块治理适配层——蓝图只覆盖 8 个基建治理模块，不管 1,500 业务模块 | P0 | 业务模块零治理覆盖，AI 改了业务代码没人管 | → **G-CT-011: 业务模块治理适配契约** |
| **D-GAP-12** | 无 Finding 冲突仲裁模型——100 AI 同时产出冲突 Finding 如何合并/去重/仲裁 | P1 | Finding 数量爆炸，真假难辨 | → **G-CT-012: Finding 仲裁契约** |

### 1.4 新增设计章节清单

| 章节编号 | 章节名称 | 对应缺陷 | 预计篇幅 | 状态 |
|:---:|------|:---:|:---:|:---:|
| §1 | 容量升级设计与 SLO | D-GAP-01 | ~3 页 | ✅ 本章（已写） |
| MOD-GOVERNANCE §3.9 | 脚本生命周期治理 | D-GAP-02 | ~2 页 | ✅ 已施工 |
| §2 | 分层执行模型（Tiered Execution） | D-GAP-04 | ~3 页 | ✅ 已施工 |
| §3 | 熔断器策略（Circuit Breaker Policy） | D-GAP-05 | ~2 页 | ✅ 已施工 |
| §4 | 分片存储架构（Sharded Storage） | D-GAP-06 | ~3 页 | ✅ 已施工 |
| §5 | GPU 加速策略 | D-GAP-08 | ~1.5 页 | ✅ 已施工 |
| MOD-GOVERNANCE §3.14 | 可观测性与告警架构 | D-GAP-09 | ~2 页 | ✅ 已施工 |
| MOD-GOVERNANCE §3.15 | 维度模型扩展（D13 容量治理 / D14 依赖健康） | D-GAP-10 | ~1.5 页 | ✅ 已施工 |
| §6 | 施工升级路线图 | — | ~2 页 | ✅ 已施工 |
| §7 | 升级后测试矩阵（含容量压力测试） | — | ~1 页 | ✅ 已施工 |

### 1.5 新增集成契约（G-CT-009 ~ G-CT-014）

#### G-CT-009: Module → Script 映射契约

```
方向：业务模块（1,500 个）→ 治理脚本（10,000 个）
触发时机：新模块注册 / 模块变更 / 增量扫描触发
契约定义：
  每个治理脚本 MUST 在其 __manifest__ 中声明 target_modules 字段：
    - target_modules: list[str]     # 脚本覆盖的 module_id 列表
    - target_domains: list[str]     # 脚本覆盖的功能域（infra/risk/alpha/...）
    - target_layers: list[str]      # 脚本覆盖的架构层（L00~L12）
    - trigger_on: list[str]         # 触发方式（file_change/git_hook/schedule/manual）

  增量扫描时：
    变更文件 → 解析归属模块 → 查 Module→Script 反向索引 → 只跑匹配的脚本
    非增量扫描不受此契约约束。

  反向索引由 generate_script_manifest.py 自动生成并缓存到 scripts/governance/module_script_index.yaml

  解决 D-GAP-03：增量扫描从维度级精准到脚本级。
  典型效果：修改 MOD-RISK-012 时，扫描从 D6 全部 10 个脚本缩减到 2-3 个相关脚本。
```

#### G-CT-010: 多 Agent 协调契约（Multi-Agent Coordination）

```
方向：100 个 AI Agent → GovernanceServer MCP → 治理脚本调度层 + 文件写入层
触发时机：任意 AI Agent 触发治理扫描时 / 任意 AI Agent 修改代码文件写入时
契约定义：

  ═══════════════════════════════════════════════════════════
  第一部分：治理扫描的并发调度（只读文件，不修改文件）
  ═══════════════════════════════════════════════════════════

  - 每个 AI Agent 以唯一 session_id + agent_id 发起扫描请求
  - GovernanceServer 作为统一入口，负责：
      a) L1 DimensionLock: 同一维度同一时刻只有一个 Agent 运行（串行化冲突维度）
      b) L2 FileLock: 同一文件同一时刻只有一个 Agent 读写
      c) AdmissionController: P0 扫描永远准入，P1 排队，P2 限流
  - 不再需要 L0 ProcessLock（已降级为 Config Read Lock，仅保护 script-manifest.yaml 读取）
  - 100 AI 并发时，通过四池 Bulkhead 隔离 + AdmissionController 优先级排队
  - 调度策略：
      - 同一 Agent session 内的多次扫描 → merge 为一次（debounce 2s）
      - 不同 Agent 对同一维度的扫描 → L1 DimensionLock 排队
      - 不同 Agent 对不同维度的扫描 → 完全并行

  ═══════════════════════════════════════════════════════════
  第二部分：文件写入的三层防护（解决并发写入编码乱码）
  ═══════════════════════════════════════════════════════════

  背景：
    v4.0 使用 L0 ProcessLock 防止多个 AI 并发写入同一文件导致编码乱码。
    问题是锁力度太粗——100 个 AI 改 100 个不同文件也被迫排队。
    本契约用三层精防护取代一把粗锁。

  第一层：L2 FileLock（文件级互斥）
  ─────────────────────────────────────
    机制：已存在于 _concurrency.py FileLock 类（第 756 行）

    AI-A 要写 "src/risk/model.py" → file_lock.acquire("src/risk/model.py")
      → 若文件未被锁定 → 拿到锁 → 写入 → file_lock.release()
      → 若文件已被 AI-B 锁定 → 等待（最多 5 秒）→ 拿到锁或超时报错

    AI-C 要写 "src/alpha/executor.py" → 不同文件 → 立即拿到锁 → 无等待

    效果：
      - 同一文件：排队写入，绝不并发
      - 不同文件：完全并行，零等待
      - 100 个 AI 改 100 个不同文件 → 100 路并行

  第二层：原子写入（Atomic Write，防半截写入）
  ─────────────────────────────────────────
    机制：不直接写文件，写临时文件再原子重命名

    def atomic_write(filepath, content, encoding="utf-8"):
        tmp = filepath + ".tmp." + str(os.getpid())
        try:
            with open(tmp, "w", encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())       # 强制刷到磁盘
            os.replace(tmp, filepath)       # 原子重命名（Windows/Linux 通用）
        except Exception:
            os.unlink(tmp, missing_ok=True) # 失败时清理临时文件
            raise

    效果：
      - 要么写入完整成功，要么原文件毫发无伤
      - 绝对不会出现"文件写了一半编码就断了"的情况
      - os.replace() 是操作系统级原子操作，跨所有编程语言和工具

  第三层：Git 兜底（极端情况下的最后防线）
  ─────────────────────────────────────────
    机制：每个 AI 写入前 stash，写入后验证

    def safe_file_write(filepath, content):
        # 1. 写入前保存 git 状态
        subprocess.run(["git", "stash", "push", "--", filepath], check=False)

        try:
            atomic_write(filepath, content)
            # 2. 验证：git diff 检查文件是否完整可读
            result = subprocess.run(["git", "diff", filepath],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError("文件写入后 git 验证失败")
        except Exception:
            # 3. 恢复：git checkout 还原文件
            subprocess.run(["git", "checkout", "--", filepath], check=True)
            subprocess.run(["git", "stash", "pop"], check=False)
            raise

    效果：
      - 即使 L2 锁 + 原子写入都失效（极端低概率），git 能还原文件
      - 文件损坏的窗口期极短（< 1 秒，仅在 atomic_write 期间）

  ═══════════════════════════════════════════════════════════
  调用链：AI Agent 写文件的标准流程
  ═══════════════════════════════════════════════════════════

    def ai_agent_write_file(agent_id, filepath, content):
        lock_mgr = LockManager(agent_id=agent_id)

        # Step 1: 拿文件锁
        result = lock_mgr.file_lock(filepath, timeout_s=5)
        if not result.acquired:
            raise FileWriteConflictError(
                f"文件 {filepath} 正被 {result.holder_agent_id} 修改，请稍后重试"
            )

        try:
            # Step 2: Git stash 当前文件
            subprocess.run(["git", "stash", "push", "--", filepath], check=False)

            # Step 3: 原子写入
            atomic_write(filepath, content)

            # Step 4: 验证
            subprocess.run(["git", "diff", "--exit-code", filepath], check=True)

        except Exception as e:
            # Step 5：失败回滚
            subprocess.run(["git", "checkout", "--", filepath], check=True)
            raise FileWriteFailedError(f"写入失败，文件已还原: {e}")

        finally:
            # Step 6: 释放锁
            lock_mgr.file_unlock(filepath)

  解决 D-GAP-07：
    - 移除 L0 全局锁 → 治理扫描和文件读取 100 路并行
    - L2 文件锁 → 同一文件写入互斥
    - 原子写入 → 永不半截
    - Git 兜底 → 极端情况可还原
```

#### G-CT-010a: 原子写入规范（Atomic Write Specification）

```
文件位置：scripts/governance/_shared/atomic_write.py（新建）

接口：
  atomic_write(filepath: str | Path, content: str, encoding: str = "utf-8") -> None

行为：
  1. 创建 {filepath}.tmp.{pid} 临时文件
  2. 写入 content, encoding 指定编码
  3. f.flush() + os.fsync() 强制落盘
  4. os.replace(tmp, filepath) 原子重命名
  5. 异常时自动清理 tmp 文件

副作用：零——不修改 filepath 以外的任何文件

使用方：
  - AI Agent 所有文件写入入口
  - rollback/auto_fixer.py 自动修复写入
  - behavioral-auditor/repair.py 漂移修复写入
  - 任何治理脚本中需要写入文件的场景（目前不允许，但预留）

验收标准：
  - 并发 100 进程同时 atomic_write 同一文件 → 最终内容完整、编码正确
  - 写入过程中 kill -9 进程 → 原文件不变
  - 磁盘满时写入 → 不丢失原文件内容
```

---

#### G-CT-011: 业务模块治理适配契约（Business Module Governance Adapter）

```
方向：业务模块蓝图 → MOD-GOVERNANCE 治理域
触发时机：业务模块注册/变更时
契约定义：
  每个业务模块蓝图 MUST 包含 governance 声明块：
    governance:
      domain: "risk" | "alpha" | "execution" | ...
      scripts: ["d6_security/scan_secret_leak.py", ...]  # 必须运行的治理脚本
      gates: ["gate_secret_leak_scan", ...]               # 必须通过的 phase gate
      sla_class: "critical" | "standard" | "best_effort"  # 治理 SLA 等级

  MOD-GOVERNANCE 侧：
    - 读取所有业务模块的 governance 声明 → 构建全局治理覆盖矩阵
    - 新增业务模块时自动注册到 ShardRouter（分配分片）
    - 退役模块时自动从所有索引中移除

  解决 D-GAP-11：1,500 业务模块有标准化的治理接入方式。
```

#### G-CT-012: Finding 仲裁契约（Finding Arbitration）

```
方向：治理脚本 → arbitrate_findings.py → 任务系统（MOD-TASK_SYSTEM）
触发时机：多个 Agent 的扫描结果在同一文件/模块上产生冲突 Finding 时
契约定义：
  Finding 唯一键：(file_path, check_name, severity, evidence_hash)
  - 同键 Finding 自动合并，保留最早发现时间和最新更新时间
  - 冲突 Finding（同文件、不同结论）→ 仲裁器介入：
      a) 若一方为 CRITICAL → CRITICAL 胜出
      b) 若同级 → 保留两方 Finding，标记 needs_human_review
      c) 若一方来自 AI-Generated 维度（D12）→ 降权（权重 0.5）
  - 仲裁后的 Finding 写入 FindingCollection → 桥接到任务系统创建 TaskCard

  解决 D-GAP-12：100 AI 并发扫描时不产生 Finding 风暴。
```

#### G-CT-013: 脚本生命周期治理契约（Script Lifecycle Governance）

```
方向：治理脚本自身 → 脚本注册表 → 质量门禁
触发时机：脚本创建 / 修改 / 废弃时
契约定义：
  脚本生命周期状态机：
    draft → review → active → deprecated → retired → archived

  状态转换条件：
    - draft→review: 必须通过 validate_script_quality.py 全部 D-D-01~08 检查
    - review→active: 必须通过 test_all_scripts.py 冒烟测试 + Owner 审批
    - active→deprecated: superseded_by 字段非空 + depends_on 全部迁移完毕
    - deprecated→retired: 30 天冷却期 + 无活跃引用
    - retired→archived: 手动触发 migrate_to_archive.py

  自动化检查（每次 scan 运行时触发）：
    - detect_script_rot.py: 检测脚本是否静默失效（连续 30 天零 Finding）
    - detect_stale_version.py: 检测版本号是否长期未更新
    - score_script_effectiveness.py: 脚本有效性评分（Finding 密度/去重率/误报率）

  解决 D-GAP-02：防止脚本腐化，确保 10,000 脚本的存量都是活的。
```

#### G-CT-014: 容量压力测试契约（Capacity Stress Test）

```
方向：治理域自身 → 容量 SLO 验收
触发时机：每次重大升级前 / 每周自动运行
契约定义：
  压力测试场景：
    S1: 100 个模拟 AI Agent 同时触发增量扫描（每个 20 脚本）
    S2: 10,000 脚本全量扫描（40 workers）
    S3: 1,500 模块同时进行 Phase Gate 检查
    S4: 10,000 条/min Audit 写入压力（16 分片 SQLite WAL）

  通过标准：
    - S1 必须满足 SLO-1（p95 < 60s）
    - S2 必须满足 SLO-5（< 4h）
    - S3 必须满足 SLO-3（< 10s/session）
    - S4 必须满足 SLO-4（p99 < 100ms）

  实现：压力场景由 session_simulator.py 扩展产生，指标写入 sla_metrics.jsonl
```

### 1.6 蓝图自身升级路线（Phase A → B → C）

#### Phase A：容量需求规格（当前阶段，§1 即 Phase A 交付物）

- [x] **A1**: §1.1 升级驱动（已完成）
- [x] **A2**: §1.2 容量目标与 SLO（已完成）
- [x] **A3**: §1.3 设计缺失盘点（已完成）
- [x] **A4**: §1.5 新增 G-CT-009~014 契约定义（已完成）
- [ ] **A5**: 将本节内容同步到 SYS-MASTER-001 的治理域节点描述中
- [ ] **A6**: Owner 审批 Phase A → 进入 Phase B

#### Phase B：蓝图章节施工（编写 §2~§5 + §6 + §7）

- [x] **B1**: MOD-GOVERNANCE §3.9 脚本生命周期治理（含状态机、版本化规则、退役策略） ✅ 2026-05-10
- [x] **B2**: §2 分层执行模型（hot/warm/cold/frozen 四层 + 每层超时/SLA） ✅ 2026-05-10
- [x] **B3**: §3 熔断器策略（四池独立阈值 + HALF_OPEN 探测策略 + 告警升级链） ✅ 2026-05-10
- [x] **B4**: §4 分片存储架构（16 分片设计 + 一致性哈希路由 + 跨分片查询策略） ✅ 2026-05-10
- [x] **B5**: §5 GPU 加速策略（BGE-M3 ONNX→CUDA 迁移 + D12 维度 GPU 卸载计划） ✅ 2026-05-10
- [x] **B6**: MOD-GOVERNANCE §3.14 可观测性架构（指标 / 日志 / 追踪三层 + Dashboard 设计 + 告警规则） ✅ 2026-05-10
- [x] **B7**: MOD-GOVERNANCE §3.15 维度模型扩展（D13 容量治理 + D14 依赖健康 + D10 补全） ✅ 2026-05-10
- [x] **B8**: §6 施工升级路线图（蓝图→代码施工的优先级排序） ✅ 2026-05-10
- [x] **B9**: §7 升级后测试矩阵（43 项测试用例，含容量压力测试） ✅ 2026-05-10
- [x] **B10**: 更新 MOD-GOVERNANCE §2 域内模块清单（GOV-SUB-001~004 已合并至 MOD-INF-018/020/021/023） ✅ 2026-05-10
- [x] **B11**: 更新 MOD-GOVERNANCE §4 施工顺序（新增 Phase 5/Phase 6 两层 12 项施工任务） ✅ 2026-05-10
- [x] **B12**: 更新 MOD-GOVERNANCE §6 风险表（新增 6 条升级后风险） ✅ 2026-05-10
- [x] **B13**: Owner 审批 Phase B → 进入 Phase C ✅ 2026-05-10

#### Phase C：蓝图与代码对齐验证（当前阶段）

- [ ] **C1**: 逐条验证 G-CT-009~014 的代码实现已就位
- [ ] **C2**: 运行容量压力测试（G-CT-014 S1-S4 场景）
- [ ] **C3**: SLO 达标验证（SLO-1 ~ SLO-7 全部达标）
- [ ] **C4**: 代码侧 thresholds.yaml 与蓝图 SLO 对齐
- [ ] **C5**: 更新 construction_progress → phase_4_blueprint_upgrade_complete
- [ ] **C6**: 发布 v0.3.0（施工完成版）

### 1.7 施工优先级映射（蓝图设计 → 代码施工）

> 此为快速参考——详细施工计划见 §6。

| 施工优先级 | 对应蓝图设计 | 关键动作 | 依赖 |
|:---:|------|------|------|
| **P0-1** | G-CT-010 (多Agent协调) | 废弃 L0 ProcessLock，接入 LockManager L1/L2 | 无 |
| **P0-2** | G-CT-010 + thresholds §35 | run_all.py 切换 BulkheadExecutorV2，worker 8→34 | P0-1 |
| **P0-3** | G-CT-009 (Module→Script映射) | 脚本 __manifest__ 增加 target_modules，建立反向索引 | 无 |
| **P1-1** | G-CT-013 (脚本生命周期) | 实现脚本状态机 + detect_script_rot / score_script_effectiveness | P0-2 |
| **P1-2** | G-CT-012 (Finding仲裁) | 实现 Finding 去重合并 + 冲突仲裁器 | P0-2 |
| **P1-3** | §2 (分层执行) + thresholds | 区分 hot/warm/cold/frozen 四层，按层分配池 | P0-2 |
| **P1-4** | MOD-GOVERNANCE §3.14 (可观测性) | Dashboard + 告警规则 + error budget 仪表盘 | P0-2 |
| **P2-1** | G-CT-011 (业务模块适配) | 1,500 模块 governance 声明标准化 | P1-1 |
| **P2-2** | §4 (分片存储) | 16 Shard SQLite 上线 + ShardRouter 接入 AuditTrail | P0-2 |
| **P2-3** | §3 (熔断器策略) | 四池独立的熔断阈值 + 自动恢复逻辑 | P0-2 |
| **P3-1** | §5 (GPU加速) | BGE-M3 ONNX → CUDA，D12 维度加速 | P2-2 |
| **P3-2** | MOD-GOVERNANCE §3.15 (D13/D14) | 新增容量治理 + 依赖健康维度脚本 | P2-1 |
| **P3-3** | G-CT-014 (压力测试) | 100 AI 模拟并发 + 10,000 脚本全量压力测试 | P2-2 |

---

## 2. 分层执行模型（Tiered Execution）（v0.2.0 新增）

> **对应缺陷**：D-GAP-04 | **关联章节**：§1.2 SLO
>
> 10,000 个脚本不能同等对待。必须按优先级和时效性分层，确保"快速通道"不被慢脚本拖垮。

### 2.1 四层执行模型

```
┌─────────────────────────────────────────────────────────┐
│  Hot Layer（每次 git commit 触发）                        │
│  延迟目标: p95 < 10s | 脚本数: ~50（纯结构/安全核心）      │
│  维度: D1(结构), D2(DI), D6(安全)—仅 SECRET_LEAK 类      │
│  Pool: quick (16 workers), 超时: S0 (30s)               │
├─────────────────────────────────────────────────────────┤
│  Warm Layer（每次 AI Session 启动触发）                   │
│  延迟目标: p95 < 60s | 脚本数: ~200（增量常用维度）       │
│  维度: D3(标准), D4(编码), D5(架构), D8(契约), D11(配置) │
│  Pool: content_analysis (8 workers), 超时: S1 (120s)    │
├─────────────────────────────────────────────────────────┤
│  Cold Layer（每日定时触发 / 新模块注册触发）              │
│  延迟目标: p95 < 30min | 脚本数: ~3,000（深度审计维度）   │
│  维度: D7(数据), D9(审计), D12(AI)/D13(容量)/D14(依赖)   │
│  Pool: ai_generated (16 workers), 超时: S2 (600s)       │
├─────────────────────────────────────────────────────────┤
│  Frozen Layer（每周全量扫描 / 发版前门禁）                │
│  延迟目标: < 4h | 脚本数: 10,000（全部维度）              │
│  维度: D1-D14 全部 | Pool: 所有池并行                    │
│  超时: S3 (1800s), 写操作脚本走 disruptive pool(4 workers)│
└─────────────────────────────────────────────────────────┘
```

### 2.2 层间降级策略

| 场景 | 触发条件 | 降级动作 | 恢复条件 |
|------|------|------|------|
| Hot→Warm 降级 | Hot 层 p95 连续 3 次 > 30s | 将 Hot 中最慢的 top-5 脚本降级到 Warm 层 | Hot 层 p95 < 10s 连续 10min |
| Warm→Cold 降级 | Warm 层 pool 排队深度 > 200 | 新到 Warm 脚本路由到 Cold pool | Warm pool 排队深度 < 50 |
| Cold→Frozen 降级 | Cold 层超时率 > 20% / 单次 scan | 暂停 Cold 层，合并到下一次 Frozen 全量 | 人工确认 |
| 全层冻结 | Error budget > 80% | 仅保留 Hot 层（D1/D2/D6 安全核心），其余全部暂停 | Error budget < 50% |

### 2.3 TieredTimeout 参数表（对齐 thresholds.yaml）

| Tier | 超时 | 适用脚本类型 | 超时行为 | 在 _concurrency.py 中 |
|------|:---:|------|------|------|
| S0 | 30s | Hot 层结构检查（D1/D2）+ 密钥泄露扫描 | 超时 → 立即 kill，标记 TIMEOUT | TIERED_TIMEOUTS["S0"] |
| S1 | 120s | Warm 层代码分析（D3/D4/D5/D8/D11） | 超时 → 发送 SIGTERM，等 5s → SIGKILL | TIERED_TIMEOUTS["S1"] |
| S2 | 600s | Cold 层 AI 检测（D7/D9/D12/D13/D14） | 超时 → 记录 PARTIAL_RESULT，不 kill（允许慢查询完成） | TIERED_TIMEOUTS["S2"] |
| S3 | 1800s | Frozen 层全量（D1-D14）+ 写操作 | 超时 → 标记 DEFERRED，下次全量重试 | TIERED_TIMEOUTS["S3"] |

### 2.4 脚本归属层级的判定规则

```
脚本归属层级由 __manifest__.tier 字段声明：

  tier: "hot"    ← 每次 commit 必跑（变更文件路径匹配时）
  tier: "warm"   ← 每次 session 启动跑
  tier: "cold"   ← 每日定时 + 新模块注册时跑
  tier: "frozen" ← 每周全量 + 发版门禁跑

判定流程：
  1. 脚本 __manifest__ 声明 tier
  2. phase_check_registry.py 读取并分配
  3. run_all.py 按 tier 过滤（--tier hot|warm|cold|frozen|all）
  4. 增量扫描时：变更文件 → 查 target_modules → 匹配的脚本按 tier 执行

默认 tier（无声明时）：
  D1/D2/D6(密钥类) → hot
  D3/D4/D5/D8/D11  → warm
  D7/D9/D10/D12    → cold
  D13/D14 + 写操作  → frozen
```

---

## 3. 熔断器策略（Circuit Breaker Policy）（v0.2.0 新增）

> **对应缺陷**：D-GAP-05 | **现有代码**：[`_concurrency.py` CircuitBreaker](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L580)
>
> `_concurrency.py` 已有 `CircuitBreaker` 类实现但蓝图未定义策略。本节补全。

### 3.1 四池独立熔断阈值

```
每个 Bulkhead 池有独立的 CircuitBreaker 实例，失败计数基于脚本执行结果。

┌────────────────┬──────────┬──────────┬──────────────┬──────────────────────────────┐
│ Pool           │ failure  │ timeout  │ half_open_   │ 熔断后降级行为               │
│                │ threshold│ window   │ max_requests │                              │
├────────────────┼──────────┼──────────┼──────────────┼──────────────────────────────┤
│ quick          │ 5 次     │ 60s      │ 3            │ 熔断后 quick 脚本路由到       │
│ (hot)          │          │          │              │ content_analysis pool         │
├────────────────┼──────────┼──────────┼──────────────┼──────────────────────────────┤
│ content_       │ 8 次     │ 120s     │ 3            │ 熔断后维度脚本降级执行——      │
│ analysis       │          │          │              │ 跳过非关键检查，仅保留结构校验 │
├────────────────┼──────────┼──────────┼──────────────┼──────────────────────────────┤
│ ai_generated   │ 10 次    │ 300s     │ 5            │ 熔断后 AI 维度全部降级为      │
│ (cold)         │          │          │              │ heuristic-only（不用 LLM）    │
├────────────────┼──────────┼──────────┼──────────────┼──────────────────────────────┤
│ disruptive     │ 2 次     │ 30s      │ 1            │ 熔断后所有写操作暂停，         │
│ (write)        │          │          │              │ 触发 Kill Switch 警告          │
└────────────────┴──────────┴──────────┴──────────────┴──────────────────────────────┘
```

### 3.2 状态转换协议

```
    ┌─────────┐   failure_count >= threshold    ┌──────────┐
    │ CLOSED  │ ───────────────────────────────→ │  OPEN    │
    │ (正常)  │                                  │ (熔断)   │
    └────┬────┘                                  └────┬─────┘
         │                                            │
         │ 每次 success → failure_count 重置为 0       │ timeout_window 到期
         │                                            ▼
         │                                     ┌──────────────┐
         └─────────────────────────────────────│ HALF_OPEN    │
                                               │ (探测恢复)   │
                                               └──────┬───────┘
                                                      │
                                    全部 probe 成功 ──┴── 任一 probe 失败
                                    → CLOSED              → OPEN (重置窗口)
```

### 3.3 全局熔断器与告警升级链

```
disruptive pool 熔断 → 全局告警
  ↓
  ├─ 1 次 disruptive CB OPEN: 日志 WARN + sla_metrics.jsonl 记录
  ├─ 2 次 disruptive CB OPEN (24h 内): 通知 Owner（Slack/企微/邮件）
  ├─ 3 次 disruptive CB OPEN (24h 内): Kill Switch 就绪（不自动激活）
  └─ 4 次 disruptive CB OPEN (24h 内): Kill Switch 激活 + 全系统扫描冻结
     └─ 恢复需要 Owner 手动 reset + 验证 disruptive 池健康

quick/content_analysis/ai_generated 池熔断 → 局部降级
  ↓
  ├─ CB OPEN 触发: 日志 WARN + 自动降级执行（见 §3.1 表）
  ├─ CB OPEN > 5min: 通知 Owner + escalate_to_human.py
  └─ CB OPEN > 30min: 状态升级为 P1 + 创建 TaskCard
```

### 3.4 失败判定标准

```
什么算"一次失败"（计入 failure_count）：
  - 脚本返回非零 exit code
  - 脚本超时（超过 TieredTimeout 对应 S 级上限）
  - 脚本抛出未捕获异常
  - 子进程被 OOM Killer 杀死

什么不算失败：
  - 脚本返回零 exit code 但产出 WARNING 级别 Finding（这是正常产出）
  - 脚本因 L1/L2 Lock 冲突被跳过（调度层正常行为）
  - 脚本被 AdmissionController 拒绝（限流保护，非故障）
```

---

## 4. 分片存储架构（Sharded Storage）（v0.2.0 新增）

> **对应缺陷**：D-GAP-06 | **现有代码**：[`_concurrency.py` ShardRouter](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L1003)
>
> 1,500 模块 × 每模块多个 Collection（Audit/Finding/Checkpoint/GateResult）→ 单 SQLite 锁竞争成为瓶颈。
> 本节定义 16 分片架构。

### 4.1 分片拓扑

```
┌─────────────────────────────────────────────────────────────┐
│                    ShardRouter                              │
│         hash(module_id) % 16 → shard_XX                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────────┐
        ▼                  ▼                      ▼
   ┌─────────┐        ┌─────────┐           ┌─────────┐
   │ shard_00│        │ shard_01│    ...    │ shard_15│
   │ SQLite  │        │ SQLite  │           │ SQLite  │
   │ WAL ON  │        │ WAL ON  │           │ WAL ON  │
   │ ~94 mod │        │ ~94 mod │           │ ~94 mod │
   └────┬────┘        └────┬────┘           └────┬────┘
        │                  │                      │
        ▼                  ▼                      ▼
   data/governance_shards/shard_00/governance.db
   data/governance_shards/shard_01/governance.db
   ...
   data/governance_shards/shard_15/governance.db
```

### 4.2 分片内 Collection 结构

```
每个 shard 的 SQLite 包含以下表（与 VMS 8-Collection 对齐）：

  audit_entries        ← G-CT-001 (RBAC→Audit)
  finding_records      ← G-CT-009 (Module→Script), G-CT-012 (Finding 仲裁)
  checkpoint_states    ← G-CT-002 (Audit→Rollback)
  gate_results         ← Phase Gate 检查结果
  script_run_history   ← 脚本执行历史（sla_metrics 数据源）
  circuit_breaker_state← 熔断器状态持久化
  scan_cache           ← 文件→脚本映射缓存

每表按 module_id 分片——同一模块的所有数据在同一 shard 中。
跨模块查询（如 "列出所有模块的 gate_results"）走 scatter-gather。
```

### 4.3 路由算法

```python
def route(module_id: str) -> int:
    """
    一致性哈希路由——模块永久绑定分片。
    使用 SHA256 前 8 字节取模，避免 Python hash() 的跨进程不一致。
    """
    h = hashlib.sha256(module_id.encode()).digest()
    return int.from_bytes(h[:8], "big") % 16
```

### 4.4 跨分片查询策略

| 查询类型 | 策略 | 延迟特征 |
|------|------|------|
| 单模块查询（最常见） | `shard_XX.execute("SELECT ... WHERE module_id = ?")` | p50 < 5ms |
| 同维度跨模块查询 | 维度→modules→shards; 最多 16 路并发 scatter，结果 merge | p50 < 50ms |
| 全量聚合查询（Dashboard） | 16 路并发 gather; 每路 `SELECT COUNT(*) GROUP BY ...` | p50 < 200ms |
| 跨分片 JOIN | 禁止——先 gather 到内存再 pandas merge | p95 < 500ms |

### 4.5 分片再平衡

```
触发条件（自动检测，非自动执行）：
  - 单分片模块数 > 150（均值 94 + 60% 余量）
  - 单分片 DB 文件 > 10GB
  - 单分片写入延迟 p99 > 200ms 持续 1h

再平衡操作（手动 + Owner 审批）：
  1. 锁定目标分片（暂停写入）
  2. 修改 route() 的取模基数（16 → 32）
  3. 创建新分片 shard_16~shard_31
  4. 按新基数重新分配模块→分片
  5. 迁移数据（SQLite .backup 或 INSERT INTO ... SELECT）
  6. 解锁 + 验证数据完整性
  7. 退役旧的多余分片

初始设计用 16 分片，评估后再决定是否扩到 32。
1,500 模块 / 16 分片 = ~94 模块/分片，SQLite WAL 模式足以支撑。
```

### 4.6 ChromaDB / FAISS 分片

```
向量存储（目前用于 D12 AI 幻觉检测）同样需要分片：

  分片策略：与 SQLite 同——hash(module_id) % 16
  存储路径：data/governance_shards/shard_XX/chroma_db/

  每分片独立的 ChromaDB 实例（或 FAISS index 文件）：
    - BGE-M3 embedding dimension: 1024
    - 每模块平均 200 条向量记录 → 每分片 ~18,800 条
    - 单分片 FAISS 索引大小 ≈ 18,800 × 1024 × 4B ≈ 77MB
    - 16 分片总大小 ≈ 1.2GB，完全在 64GB RAM 内

  查询策略：
    - 单模块相似度查询 → 定向到对应 shard
    - 全局相似度查询 → 16 路并发 + KNN merge（top-K 再排序）
```

---

## 5. GPU 加速策略（v0.2.0 新增）

> **对应缺陷**：D-GAP-08 | **硬件**：RTX 3090 24GB
>
> 当前 BGE-M3 嵌入模型使用 ONNX Runtime CPU 推理。
> 在 10,000 脚本规模下，D12 AI 幻觉检测的全量扫描需要 45 分钟——GPU 加速可降到 5 分钟。

### 5.1 GPU 加速目标

| 指标 | 当前 CPU (ONNX) | GPU 目标 (CUDA/ORT-CUDA) | 加速比 |
|------|:---:|:---:|:---:|
| BGE-M3 单次 embedding (1024d) | ~100ms | ~5ms | **20×** |
| D12 维度全量扫描 (当前 ~50 脚本) | ~45min | ~5min | **9×** |
| D12 维度 10,000 脚本全量扫描 (预估) | ~3h | ~10min | **18×** |
| FAISS 索引构建 (per shard) | ~30s | ~2s | **15×** |
| FAISS KNN 查询 (top-100) | ~50ms | ~3ms | **17×** |

### 5.2 显存分配预算（24GB）

```
┌──────────────────────────────────────────────────┐
│ BGE-M3 模型权重 (FP16):             ~2.5 GB      │
│ BGE-M3 推理临时缓冲区:              ~2.0 GB      │
│ FAISS 索引 (16 shards, GPU):        ~1.2 GB      │
│ 推理 batch 缓冲区 (batch_size=64):  ~0.5 GB      │
│ PyTorch/CUDA 运行时开销:            ~1.5 GB      │
│ ─────────────────────────────────────────        │
│ 峰值占用:                           ~7.7 GB      │
│ 安全余量 (24GB - 7.7GB):           ~16.3 GB     │
│                                                  │
│ 结论: 24GB VRAM 绰绰有余。                       │
│ 甚至可同时跑 BGE-M3 + 一个小型 LLM (7B, Q4)。    │
└──────────────────────────────────────────────────┘
```

### 5.3 实施路径

```
Phase 1: ONNX CPU → ONNX Runtime CUDA (ORT-CUDA)
  - 安装 onnxruntime-gpu
  - 修改 BGE-M3 推理 provider: ["CUDAExecutionProvider", "CPUExecutionProvider"]
  - 保持 ONNX 模型不变，零代码改动，仅改执行 provider
  - 风险：极低（ORT 自动处理 CUDA/CPU fallback）

Phase 2: FAISS GPU index
  - faiss-cpu → faiss-gpu
  - IndexFlatIP → GpuIndexFlatIP
  - 每个 shard 独立的 GPU index（共享 CUDA 资源）

Phase 3: batch inference 优化
  - 收集同一 shard 内所有待 embedding 文本 → batch_size=64
  - GPU 利用率从 ~15% 提升到 ~80%

Phase 4: (可选) D12 维度专属小 LLM
  - 用 3090 剩余 16GB VRAM 跑 Qwen2.5-7B-Q4_K_M
  - 替代当前 D12 对云端 LLM API 的依赖（离线 AI 幻觉检测）
  - 仅在 Frozen 全量扫描时使用，日常增量仍用规则检测
```

### 5.4 GPU 不可用时的回退

```
if not torch.cuda.is_available():
    → 自动降级 ONNX CPUExecutionProvider
    → 日志 WARN: "GPU unavailable, falling back to CPU (expect 20× slower embedding)"
    → D12 维度自动从 cold 层降级为 frozen 层（仅周检，不阻塞日常）
    → sla_metrics.jsonl 记录 GPU_UNAVAILABLE 事件
```

---

## 6. 施工升级路线图（v0.2.0 代码施工计划）

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：1.代码文件存在且非空 2.pytest 通过 3.mypy 通过 4.ruff 通过

> **定位**：蓝图设计完成后（§1 Phase A），本节定义代码侧的施工计划。
> 优先级来源于 §1.7 施工优先级映射表。
> **前置条件**：§1 Phase A 审批通过后启动。

### 6.1 总体施工阶段

| 阶段 | 名称 | 工期 | 交付标准 | 依赖 |
|:---:|------|:---:|------|------|
| **I** | 基层加固（P0 核心阻塞项） | ~3 天 | run_all.py 完成 BulkheadExecutor 切换 + L0 锁废弃 | 无 |
| **II** | 精准治理（增量扫描升级） | ~3 天 | 增量扫描从维度级精确到脚本级，日常 15-30→10-20 脚本 | 阶段 I |
| **III** | 运维体系（SLO + 观测 + 熔断） | ~5 天 | 全套 SLO 达标 + 可观测性就绪 + 熔断器生效 | 阶段 I |
| **IV** | 存储扩容（分片存储 + 业务模块适配） | ~5 天 | 16 分片 SQLite 上线 + 1,500 模块 governance 声明标准化 | 阶段 II |
| **V** | 深度学习（GPU 加速 + 维度扩展） | ~5 天 | 3090 GPU 接入 + D13/D14 维度上线 + D10 补全 | 阶段 IV |
| **VI** | 全量验证（压力测试 + SLO 验收） | ~3 天 | G-CT-014 S1-S4 全部通过，error budget 零突破 | 阶段 V |

### 6.2 阶段 I: 基层加固

| 任务 | 文件 | 动作 | 检查项 |
|------|------|------|------|
| I-1 | [_concurrency.py](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L161) | 将 `ProcessLock.__init__` 改为跳过独占锁，仅保留 PID 写入用于审计；文档说明降级原因 | `run_all.py` 可并行启动 2+ 实例 |
| I-2 | [run_all.py](file:///d:/ZephyrAlpha/scripts/governance/run_all.py#L55) | 将 `ThreadPoolExecutor(max_workers=8)` 替换为 `BulkheadExecutorV2.dispatch_with_locks()` | Full scan 耗时显著下降 |
| I-3 | [_concurrency.py](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L65) | BULKHEAD_POOLS 参数从 (12/6/4/2) 对齐到 thresholds.yaml (12/8/16/4)，即 (12/8/16/4) | worker 总数 24→40 |
| I-4 | [_concurrency.py](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L141) | ADMISSION_CONTROL P0 从 4→50 | 匹配 P0 burst 需求 |
| I-5 | — | `run_all.py` 接入 `LockManager`（L1 DimensionLock + L2 FileLock） | 多 Agent 无冲突 |

### 6.3 阶段 II: 精准治理

| 任务 | 文件 | 动作 | 检查项 |
|------|------|------|------|
| II-1 | 所有治理脚本 | `__manifest__` 新增 `target_modules: [...]` 字段（按脚本分批更新） | G-CT-009 字段定义完成 |
| II-2 | [generate_script_manifest.py](file:///d:/ZephyrAlpha/scripts/governance/generate_script_manifest.py) | 扩展生成 `module_script_index.yaml` 反向索引 | 索引文件可自动生成 |
| II-3 | [run_all.py](file:///d:/ZephyrAlpha/scripts/governance/run_all.py#L816) | `_FILE_DIMENSION_MAP` 替换为从 `module_script_index.yaml` 读取的反向索引查询 | 变更单文件时只跑 ≤5 个相关脚本 |
| II-4 | [run_incremental.py](file:///d:/ZephyrAlpha/scripts/governance/run_incremental.py) | 设为默认入口，降级 `run_all.py` 为辅助工具 | 增量扫描成默认模式 |

### 6.4 阶段 III: 运维体系

| 任务 | 文件 | 动作 | 检查项 |
|------|------|------|------|
| III-1 | — | 新建 `manage_error_budget.py` | 月 error budget 仪表盘可用 |
| III-2 | [_concurrency.py](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L580) | CircuitBreaker 接入真实故障检测（维度级超时→熔断） | 某维度连续超时 5 次后自动熔断 |
| III-3 | — | 新建 `observability/manage_alert_rules.py` | SLO 违反时自动告警 |
| III-4 | — | 新建 `observability/generate_dashboard.py` | 治理域全局 Dashboard（SQLite + Grafana JSON） |
| III-5 | [_concurrency.py](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L491) | ScanCache max_entries 500→5000，增加 TTL | 缓存命中率 > 80% |

### 6.5 阶段 IV: 存储扩容

| 任务 | 文件 | 动作 | 检查项 |
|------|------|------|------|
| IV-1 | [_concurrency.py](file:///d:/ZephyrAlpha/scripts/governance/_concurrency.py#L1003) | ShardRouter 分片数 4→16，对齐 thresholds.yaml | shard_count=16 |
| IV-2 | 审计写入路径 | AuditTrail 所有 write 调用接入 `ShardRouter.route(module_id)` | 同分片零锁竞争 |
| IV-3 | — | 各业务域蓝图逐一添加 `governance:` 声明块（对齐 G-CT-011） | 1,500 模块声明覆盖率达 100% |
| IV-4 | — | MOD-GOVERNANCE 侧读取所有 governance 声明 → 构建全局治理覆盖矩阵 | 矩阵生成成功 |

### 6.6 阶段 V: 深度学习

| 任务 | 文件 | 动作 | 检查项 |
|------|------|------|------|
| V-1 | BGE-M3 推理 | ONNX CPU → ONNX CUDA / torch GPU 推理 | embedding 延迟 100ms→5ms |
| V-2 | D12 维度脚本 | embedding + similarity_search 全面走 GPU | D12 全量扫描从 45min→5min |
| V-3 | — | 新建 `d13_capacity_governance/` 目录 + 5 个初始脚本 | D13 从 0→5 脚本 |
| V-4 | — | 新建 `d14_dependency_health/` 目录 + 5 个初始脚本 | D14 从 0→5 脚本 |
| V-5 | D10 维度 | 补齐 `d10_performance/` 脚本（目标 8 个） | D10 从 0→8 脚本 |

### 6.7 阶段 VI: 全量验证

| 任务 | 动作 | 通过标准 |
|------|------|------|
| VI-1 | 扩展 `session_simulator.py`：100 模拟 AI，每个 20 脚本增量，同时触发 | SLO-1 p95 < 60s |
| VI-2 | 10,000 脚本全量扫描（40 workers） | SLO-5 < 4h |
| VI-3 | 46 gate × 100 AI session 并发检查 | SLO-3 < 10s/session |
| VI-4 | 10,000 Audit writes/min × 16 shard SQLite WAL | SLO-4 p99 < 100ms |
| VI-5 | Error budget 全月模拟 | SLO-6 / SLO-7 零突破 |
| VI-6 | 更新 `construction_progress` → `phase_4_blueprint_upgrade_complete`，发布 v0.3.0 | — |

---

## 7. 升级后测试矩阵（容量压力测试需求）

> **状态**：需求声明——测试在阶段 VI 实施。

### 7.1 Unit Test（代码逻辑层）

| 编号 | 测试项 | 覆盖组件 | 预期 |
|------|--------|------|------|
| U-CAP-01 | `BulkheadExecutorV2` pool isolation——disruptive 池故障不影响 quick 池 | BulkheadExecutor | Quick 脚本持续成功 |
| U-CAP-02 | `CircuitBreaker` HALF_OPEN→CLOSED 恢复 | CircuitBreaker | 3 次 success probe → CLOSED |
| U-CAP-03 | `AdmissionController` P0/P1/P2 排队逻辑 | AdmissionController | P0 跳过队列，P2 被限流 |
| U-CAP-04 | `ShardRouter` hash(module_id) % 16 一致性 | ShardRouter | 同 module_id → 同 shard |
| U-CAP-05 | `LockManager` L1 DimensionLock——同维度串行 | LockManager | D5 锁同时只能一个持有者 |
| U-CAP-06 | `LockManager` L2 FileLock——同文件串行 | LockManager | 同文件锁同时只能一个持有者 |
| U-CAP-07 | `ScanCache` LRU eviction + TTL expiry | ScanCache | 过期条目返回 miss |
| U-CAP-08 | `TokenBucket` refill rate + burst capacity | TokenBucket | 100 tokens/s refill, 200 burst |

### 7.2 Integration Test（跨组件交互层）

| 编号 | 测试项 | 覆盖契约 | 预期 |
|------|--------|:---:|------|
| I-CAP-01 | 2 个 Agent 同时触发同维度扫描 → L1 排队 | G-CT-010 | Agent B 等待 Agent A 完成 |
| I-CAP-02 | 10 个 Agent 触发不同维度扫描 → 完全并行 | G-CT-010 | 10 Agent 同时执行 |
| I-CAP-03 | Agent 改 MOD-RISK-012 代码 → 增量只跑 target_modules 匹配的脚本 | G-CT-009 | ≤3 个脚本触发 |
| I-CAP-04 | 新脚本 draft→review→active 全流程 | G-CT-013 | 状态流转正确 |
| I-CAP-05 | `detect_script_rot.py` 检测 30 天零 Finding 脚本 | G-CT-013 | 腐化脚本标记 deprecated |
| I-CAP-06 | 两个 Agent 对同一文件产出冲突 Finding → 仲裁 | G-CT-012 | CRITICAL 胜出 / needs_human_review |
| I-CAP-07 | 新业务模块注册 → ShardRouter 自动分配分片 | G-CT-011 | 模块分片记录正确 |
| I-CAP-08 | Audit 写入 → 16 分片路由 → 零锁竞争 | §4 | 16 分片并行写入无阻塞 |

### 7.3 Stress Test（容量压力层）

| 编号 | 场景 | 并发量 | 预期指标 | 映射 |
|------|------|:---:|------|:---:|
| S-CAP-01 | 100 AI × 20 脚本增量 | 2000 scripts/min | p95 latency < 60s, 零 crash | SLO-1, SLO-2 |
| S-CAP-02 | 10,000 脚本全量 | 40 workers | < 4h, 零维度 OOM | SLO-5 |
| S-CAP-03 | 100 AI × 46 phase gates | 4600 gates | session startup < 10s | SLO-3 |
| S-CAP-04 | 10,000 Audit writes/min | 16 shards | p99 < 100ms, 零锁竞争 | SLO-4 |
| S-CAP-05 | 100 AI 持续 30min | 稳定性 | 零 worker leak, 内存 < 32GB | SLO-6 |

### 7.4 Regression Test（回归测试——保证旧功能不退化）

| 编号 | 测试项 | 预期 |
|------|--------|------|
| R-CAP-01 | 268 现有脚本全部通过（单 Agent 全量） | 0 failure |
| R-CAP-02 | G-CT-001~008 现有 8 条契约数据流通（单 Agent） | 8/8 PASS |
| R-CAP-03 | 57 个现有测试全过（红白对抗） | 57/57 PASS |
| R-CAP-04 | GovernanceServer MCP 15 工具可用 | 15/15 PASS |
| R-CAP-05 | 原 run_all.py 全量扫描耗时 ≤ 4.5h（backward compat） | ≤ 4.5h |

### 7.5 测试执行顺序

```
Phase I:  U-CAP-01~08           (8 unit tests)       ← 每个施工 τ 后跑
Phase II: I-CAP-01~08           (8 integration tests) ← 阶段 III 完成后跑
Phase III: R-CAP-01~05          (5 regression tests)  ← 阶段 III 完成后跑
Phase IV:  S-CAP-01~05          (5 stress tests)      ← 阶段 VI 完成后跑
```

**总计**：26 项独立测试用例（8 U + 8 I + 5 R + 5 S），覆盖 L1~L4 测试金字塔。加上 v0.1.0 原有的 17 项 P0 测试，**升级后测试总数 = 43 项**（原 17 + 新增 26）。
