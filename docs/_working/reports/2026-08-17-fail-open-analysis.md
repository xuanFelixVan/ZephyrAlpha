---
ttl: task_bound
title: PG 离线 fail-open 敞口分析（治理批 A 包 · 只出方案不施工）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-17
---

# PG 离线 fail-open 敞口分析

> 来源：tracker #100 登记项（2026-08-16 PG 5432 停服事故次生议题）——"PG 离线时
> depgraph 类门禁静默放行（fail-open）是设计内降级还是敞口，随治理批裁定"。
> 本报告=治理批 A 包（AI-GOVA-001）交付物，**只出方案不施工**，供 Owner 裁定。
> 清单为 2026-08-17 全仓代码逐点实证（非记忆/文档转述），证据=文件:行号。

## 1. 现状清单

### 1.1 真实敞口（PG 离线 → 本该拦截的违规静默放行，共 5 个）

| # | 门禁 | 位置 | 离线行为证据 | 放行内容 |
|---|------|------|-------------|---------|
| 1 | RENAME-DEPGRAPH-SYNC（p39，硬阻断） | commit_gates/rename_depgraph_sync_gate.py L141-159/L189-191 | except→return None→continue | 重命名后 depgraph 未同步 |
| 2 | NEW-FILE-DEPGRAPH-ENFORCEMENT（p58，硬阻断） | commit_gates/new_file_depgraph_gate.py L184-199/L247-249 | except→None（注释自承 fail-open）→continue | 新文件未登记 depgraph 直接入库（L1 铁律强制失效） |
| 3 | DEPGRAPH-PRE-REGISTRATION（p113，硬阻断） | commit_gates/depgraph_pre_registration_gate.py L184-200/L221-223 | None≠"planned"→skip | planned→production 状态滞后 |
| 4 | GATE-PANORAMA-ALIGNMENT（p830，混合） | commit_gates/panorama_alignment_gate.py L178-203；align_panoramas.py L764 | except→log_gate_failure(sqlite)→return True | 三图内部 domain_id 不一致硬阻断失效（orphan/state_drift 本就 warn-only，属设计内） |
| 5 | PRE-MERGE-TOPO-CHECK（merge 链路） | rule_bridge/session_worktree.py L6414-6614；check_blueprint_code_alignment.py L102-106/L145-149 | module_ids==0/超时/exit 2/JSON 失败→全部降级放行；checker 缺失才 fail-closed | ORPHAN_MODULE_ID/MODULE_ID_DRIFT 类 HIGH drift 在 merge 前不可检出 |

注：#5 的 `depgraph_module_ids==0 → 放行` 分支（L6544-6558）本意是防"空索引误报"
（DB-down 时 checker 返回空集会误报全量 ORPHAN），客观上使 DB 离线时真实 HIGH
drift 一并放行——防护与敞口同体。

### 1.2 设计内降级（信息类，不拦截语义，共 5 个）

| 门禁/组件 | 位置 | 行为 |
|----------|------|------|
| GATE-DEPGRAPH-OPS reconciler（p130） | reconciliation_registry.py L2892-2938 | rc≠0→critical_warn 落 sqlite（下次 commit 横幅告警），不阻断 |
| GATE-CONSTRAINT-DETECT reconciler（p625） | reconciliation_registry.py L10051-10081 | rc≠0→warn |
| blueprint_frontmatter reconciler（p135） | reconciliation_registry.py L2974+ | 失败→warn |
| TRANSLATION-COVERAGE reconciler（p951） | audit/translation_coverage_reconciler.py L236-246 | DB 不可达→warn-only |
| RuleLoader（规则引擎索引缓存） | rule_engine/rule_engine.py L189-202 | PG 探测失败→回退 YAML 目录扫描（YAML=真源，PG=缓存）；未接入 commit gate |

### 1.3 反向行为（PG 离线反而阻断，误伤面，共 2 个）

| 组件 | 位置 | 行为 |
|------|------|------|
| verify_schema_health.py（GATE-C2 内含） | d11_compliance/verify_schema_health.py L324 | 连接调用在 try 块外——PG 离线=未捕获异常崩溃式 fail-closed，commit 被阻断；触发面窄（.pre-commit-config.yaml L818-826 files 过滤） |
| DEPGRAPH-FRESHNESS（p67） | commit_gates/depgraph_freshness_gate.py L8/L36-38/L74-76 | 不读 PG（读 .runtime/depgraph_scan_cache.json 的 saved_at）；但 PG 长期离线→reconciler 重建失败→saved_at 停更→>24h 阈值 fail-closed 误伤所有 commit |

### 1.4 已确认非 PG 依赖（排除项）

worktree_drift_watchdog reconciler（git hash 语义比对+文件快照，L13 的"DB 故障降级"
指 sqlite）、GATE-RULE-AUDIT reconciler（纯 YAML 扫描）、_log_reconcile_results
（sqlite governance.db，reconciliation_registry.py L1282）、SCRIPTS-IMPORT-INTEGRITY
（仅 psycopg2 包 import 依赖，无连接）、GATE-DOMAIN-FK（YAML 真源）。

## 2. 第一性分析：敞口还是设计内降级？

fail-open 的正当性根基：100% AI 施工场景下，环境故障（PG 停服）不应冻结全部
开发活动——"可用性优先"取舍。但成立前提有二：

1. **可感知**：放行必须留痕且有人/机制事后追账（现状：5 个敞口中 #4 有
   log_gate_failure 持久化，#1/#2/#3 仅 logger.warning 进程内日志，commit 成功
   后无任何追账锚点；#5 同样仅 warning）；
2. **可补偿**：放行的违规会在 PG 恢复后被后续机制捕获（现状：post-commit
   GATE-DEPGRAPH-OPS reconciler 重建 depgraph 后，alignment/topo 类违规可在下次
   commit 被拦——但"已入库的违规文件"无回溯清点机制）。

结论：**#1/#2/#3/#5 当前形态=真实敞口**（不可感知+无强制补偿窗口），
#4 = 半敞口（有持久化但当次放行），§1.2 各项=设计内降级（成立）。

## 3. 三选项对比

| 维度 | A. 保持现状 | B. 告警升级（推荐） | C. fail-closed |
|-----|------------|--------------------|----------------|
| 语义 | PG 离线=全放行 | PG 离线=放行但**强制持久化告警+下次 commit 横幅+台账登记** | PG 离线=阻断 commit/merge |
| 开发连续性 | 不受环境影响 | 不受环境影响 | PG 停服=全员冻结（2026-08-16 事故重演时施工停摆） |
| 敞口闭合 | 不闭合 | 可感知+可追账闭合（违规入库留台账，PG 恢复后 reconciler 补扫时可清点） | 硬闭合 |
| 工程量 | 零 | 中：5 个 gate 的 except 分支统一接 log_gate_failure（#4 已有先例）+ env_probe 前置（Test-NetConnection 5432 结果写 .runtime 状态文件，gate 读取区分"DB 离线"vs"真无违规"） | 小（删 except 即可），但误伤面大 |
| 风险 | 违规静默入库（已实证发生） | 告警疲劳（PG 长期离线时每次 commit 横幅）——以"同签名只告警一次/日"缓解 | 可用性事故；与"环境不满足非代码缺陷"的测试分层哲学冲突 |
| 与既有先例一致性 | — | 与 #4 panorama gate 的 log_gate_failure、#ARCH-DRIFT-AUTH-001 "fail-open 告警+自愈兜底"先例同构 | 与 GATE-C2 崩溃式阻断同款（该形态已被列为误伤面） |

## 4. 推荐（供 Owner 裁定）

**推荐 B（告警升级）**，分两档落地：

- B1（核心）：#1/#2/#3/#5 的 fail-open 分支统一改接 `log_gate_failure` 持久化
  （sqlite reconcile_execution_log，下次 commit 网关 banner 自动浮现）——
  与 #4 既有机制对齐，工程量小，敞口从"不可感知"升级为"可感知+可追账"。
- B2（增强，可延后）：PG 可用性前置探针（conftest 级/网关级 5432 TCP probe，
  结果落 .runtime 状态文件），gate 读取区分"DB 离线降级"与"真空无违规"，
  并在探针离线超 24h 时豁免 DEPGRAPH-FRESHNESS 的 saved_at 误伤（§1.3 联动修复）。

**不推荐 C**：fail-closed 把环境故障传导为开发冻结，2026-08-16 事故实证 PG
停服可由 OOM 次生——施工停摆与风控"生存底线"原则不冲突但收益为负；
verify_schema_health 的崩溃式阻断已被识别为误伤面（§1.3），C 会把该形态扩大化。
**不推荐 A**：#1/#2 是 depgraph"依赖关系先行"铁律的技术强制点，静默放行=
铁律失效无追账，140 悬案类事后取证成本会重复发生。

## 5. 联动登记

- tracker #99③（watchdog 分批限时扫描）不在本包施工范围，列后续治理批候选；
- §1.3 verify_schema_health 崩溃式阻断的优雅化（try 内移+明确错误码）属小改，
  建议随 B1 同批顺手（届时该 hook 在 PG 离线时从"崩溃阻断"转"明确告警阻断"）；
- 本报告落实后 tracker #100 的 fail-open 登记项可闭环。
