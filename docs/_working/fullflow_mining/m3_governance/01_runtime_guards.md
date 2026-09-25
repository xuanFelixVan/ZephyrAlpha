---
ttl: task_bound
---

# M3 分册 01 · 运行时拦截器与护栏（非 commit 链侧）

> 挖掘 2026-09-25 ｜ 车道 M3 ｜ 会话 st-commitspeed-tbl-20260924 ｜ 只读挖矿，零 commit。
> 边界：提交链侧（queue/landing/gateway/belt/门禁链本身）不重挖，引用 commit_speedup 战役
> `docs/_working/commit_speedup_campaign/00_skeleton/`（23环节/115子环节）与 `30_gate_census/C1_gate_dossier.md`。

## 一、环节定义与边界

一句话：commit 门禁之外、进程运行时仍在工作的拦截器与护栏族——LSG 及其运行时裸调拦截、
KillSwitch、ops_guard（删除原语/授权环境面）、git_guard（git alias 拦截面）、
SessionRegistry/lock_files（并发 claim 面）、emergency_commit（紧急通道自身的护栏）。
上游=规则 YAML（trae_*/宪法）；下游=全部运行中的 Python 进程与 git 调用。

## 二、六向台账

| 向 | 内容 |
|---|---|
| 上游输入 | 宪法硬规则（RULE-SECRETS/§9 红线）、env 授权变量、red_team_corpus.yaml、usercustomize/sitecustomize 引导 |
| 下游消费 | 所有 LLM 调用点、reconciler/worker/git_commit/commit_queue 四个 ops_guard 安装点、git alias 用户、多会话 claim |
| 自动化触发 | sitecustomize/usercustomize 解释器启动引导；git_guard 靠 alias 包装；**无 cron**（worktree_drift_watchdog daemon 是唯一常跑运行时面，M10 豁免在案） |
| 真源与注册表 | 本册即清单；各 guard 入口 file:line 见 §三 |
| 门禁与质量尺 | GATE-20（静态 AST 门）拦裸调写码；NO-SECRET-HARDCODE/NO-BARE-GETENV 等 C1 卷宗"不建议删"清单 |
| 当前运行状态 | 绿（本会话冷启动 reaper status 正常；runtime_interceptor 可导入；git_guard 972 行完好） |

## 三、子模块清单（逐个：是什么/入口/状态）

### 3.1 LSG（zephyr.security.llm_defense.llm_security）
- **是什么**：L0-L8 十层纵深防御统一编排入口（L0 供应链/L1 输入/L2 提示词/L2a 进程沙箱/L3 输出/L4 Agent/L5 资源/L6 可观测/L7 自保护/L8 多Agent）。
  入口 `src/zephyr/security/llm_defense/llm_security/gateway.py:139`（LSGSecurityGateway）。
- **语义**：fail-closed——任一非 fail-open 层 DENY 即整体 DENY（gateway.py:316 `_evaluate_chain` 顺序链式，不可并行）；层缺失/超时(10s)/异常→非 fail-open 层一律 DENY。
- **fail-open 集合外部化**（#353②）：出厂默认 `{l6_observability, l7_validation}`（gateway.py:95），
  Owner 可经 `config/llm_security_gateway.yaml` 的 `fail_open_layers` 收紧；加载异常回退出厂默认、构造零抛出（gateway.py:99-119）。
- **放行令牌握手**：scan_input/full_scan/scan_agent_action 且 ALLOW → `grant_allowance`（TTL 30s，gateway.py:122-136）；
  scan_output 不颁发（输出扫描在调用后，不应放行后续裸调）。请求边界预防性重置防线程池令牌残留（gateway.py:329，5.131）。

### 3.2 运行时裸调拦截器（runtime_interceptor.py，GATE-20 的后备防线）
- **是什么**：sitecustomize 自动引导 + `sys.meta_path` finder 拦截 openai/anthropic/litellm/langchain 导入，
  monkey-patch `chat.completions.create`/`messages.create`/`litellm.completion`/`ChatOpenAI.invoke` 等核心方法。
  入口 `src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py:494`（install）。
- **令牌双存储**：contextvar（异步隔离）+ threading.local（同步跨 asyncio.run 兜底）（runtime_interceptor.py:106-108）；
  `allow_llm_call` 上下文管理器栈式恢复+进入清理（5.80.3/5.80.5 治本，runtime_interceptor.py:207-266）。
- **kill-switch**：`ZEPHYR_RUNTIME_GATE=0` 双重尊重（sitecustomize.py:47 短路 + install() 内部再查，runtime_interceptor.py:505）。
- **引导盲区（实测在案）**：`sitecustomize.py` 在 Python 3.11+ 的 `python -c` 模式下**不加载**（site 模块 sys.path 无 cwd，
  sitecustomize.py:17-30 docstring 引裁定 #ARCH-PYTHON-SITECUSTOMIZE）；`python -c` 依赖仓外 usercustomize.py（**不入版本控制**，每机器手工配置）。
- **patch 防御式**：patch 失败 no-op 不阻断导入（"宁可漏拦也不破坏导入链"，runtime_interceptor.py:449-451）。

### 3.3 KillSwitch（zephyr.security.access_control.kill_switch）
- **是什么**：AI Agent 行为风控熔断器（**非交易熔断**，P1-2 边界澄清 kill_switch.py:27-33；交易真源=trading_kill_switch 五级+ex_core risk_layer）。
  入口 `kill_switch.py:138`（KillSwitch）+ `get_kill_switch()` 单例。
- **触发器 9 个**：rapid_file_deletion(3)/permission_boundary_probe(3)/suspicious_sequence(3)/off_hours_destructive(2)/
  config_file_blitz(4)/signal_noise_attack(5)/sensitivity_label_blitz(3)/agent_spawn_storm(5)/audit_log_tamper(1)（kill_switch.py:125-135）。
  单 agent 事件达阈值→BLOCK_AGENT；≥3 个 agent 被阻→全局 TRIPPED（kill_switch.py:219-225）。
- **Owner 手柄**：owner_release_global（覆盖模式+owner_override 标记）/owner_revoke_override（恢复原熔断态）/reset（全清）。
- **已知局限（自认）**：**纯进程内存态，进程崩溃即归零**，禁作交易资金安全依赖（kill_switch.py:32-33）；
  无持久化、无跨进程共享——每个 Python 进程各一个独立单例。

### 3.4 ops_guard（scripts/ops_guard.py，1610 行）
- **是什么**：删除原语守卫+授权环境面收敛。三层：命令分析（analyze_delete_command 识别 PS Remove-Item/CMD del/rd/python rmtree/git clean，
  ops_guard.py:683）、guard_* API（guard_rmtree/guard_remove/guard_move/guard_recycle，ops_guard.py:760-975）、
  in-process 补丁（patch os.remove/unlink/rmdir/rename + shutil.rmtree/move，ops_guard.py:1408-1443）。
- **授权面收敛**（#ARCH-279 裁定 A1/A2）：删除授权只认 `ZEPHYR_FORCE_DELETE=1`，GATEWAY_ENV 语义剥离退出删除域
  （ops_guard.py:603-617，39,642 条审计零合法消费方的观测收尾后转硬拦）；
  `sanitized_spawn_env`（ops_guard.py:586）从派生子进程 env 剔除 GATEWAY_ENV/FORCE_ENV——授权标记物理上无法经进程树广播。
- **docs/ untracked 三重无保护治本**（T3②）：docs/ 下 git 未跟踪文件的删除/移动需人工确认（ops_guard.py:624-681）；
  git 不可达时降级按 tracked 对待（fail-open 松约束，ops_guard.py:644-648）。
- **file_ops 声明制**（T1①）：`set_reconciler_context(gate_id, file_ops)` contextvar——reconciler 执行未声明的删除/移动→DeleteBlockedError
  （ops_guard.py:1099-1112）；reconcile_for 捕获后升 critical_warn（reconciliation_registry.py:966-981）。
- **in-process 补丁安装点（仅 5 处，非全局默认）**：reconcile_worker.py:472、session_worktree.py:2245（src 版）、
  scripts/session_worktree.py:638、commit_queue.py:2355、git_commit.py:967。普通 python 进程**不装**。

### 3.5 git_guard（scripts/git_guard.py，972 行）+ git_safety_wrapper.ps1
- **是什么**：git 危险命令拦截（alias 包装面）。plumbing 子命令（read-tree/update-index/write-tree 等）默认阻断，
  白名单 `ZEPHYR_SERIALIZER_MODE=1` 放行（git_guard.py:872-881，66 号 §4 裁定 7）；
  fast-path `ZEPHYR_GIT_GUARD_FAST_PATH=1` 仅对 checkout/reset/restore/revert 透传（git_guard.py:903）。
- **自残检测**：reset --hard/checkout -- files/clean 的 self-harm 判定（git_guard.py:403/464/533）+ stash 处理（git_guard.py:602）+ mv 策略（git_guard.py:806）。
- **_trusted_git_env**（可信内部调用 env）：session_worktree.py:406 与 commit_queue_landing.py:727 **两处同型定义**
  （worktree_pool.py:115-116 注明 FUNCTION-DUP gate 约束、同源 GIT-BUDGET-INV-003）；注入 FAST_PATH_ENV；
  检测到外部预置 FAST_PATH_ENV 时 **warn 不阻塞**（#64 裁定：fail-visible 不 fail-closed，session_worktree.py:419-431）。
- **前提**：alias 已安装（`Get-Command git` 显示 Function）。未安装期间靠 ops_guard 网关/工具层兜（project_rules.md:377）。

### 3.6 SessionRegistry / session_concurrency.py（902 行）
- **是什么**：多会话注册+文件 claim 真源。`SessionRegistry`（session_concurrency.py:295）：
  register/heartbeat/unregister、claim_file/claim_files_batch/release_files/release_files_batch、
  other_held_files、staleness 判活（`_is_session_alive`，:266）、依赖登记（register_dependency/find_breaking_change_session）。
- **配套**：SessionHandoff（交接包，:786）、SessionConflictDetector（:861）、ConcurrencyManager/pre_allocate（:108）。
- **锁文件族 lock_files.py（1659 行）**：claim/acquire/release/cleanup/salvage + TTL + stale 判定
  （`_is_stale`:161、`_claim_expired_and_idle`:225 死会话回收+审计）、registry mutex（:116）、批量 acquire/release（:674/:722）。
- **运行态**：本会话冷启动 `lock_files.py cleanup` 返回 CLEAN；reaper status scanned=20 whitelist_hits=13 killed=0。

### 3.7 emergency_commit（src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py，831 行）
- **是什么**：锁死/POST-COMMIT-GUARD 反复 reset/P0 场景的合法紧急通道——git commit-tree plumbing 绕过全部 hook
  （emergency_commit.py:427）。
- **自 built 护栏五件**：① 成本递增门禁（按 agent_id 分桶跨 session 持久：N≥3 需显式 reason、N≥5 阻断，
  emergency_commit.py:234-306 `_check_emergency_escalation`）；② `[GW:{sid}:emergency]` 标记（POST-COMMIT-GUARD 防伪语义仍覆盖）；
  ③ `[SCENARIO:{production|dogfood|test|governance_fix}]` 标记——abuse_monitor 只计 production（P1-3 治本）；
  ④ reconcile_execution_log 落库 + `.runtime/reconcile_reports/emergency_commit_*.json` 审计；
  ⑤ `trigger_reconcilers=True` 默认手动补齐 post-commit reconciler 链（hook 不触发的补偿，:789 `_trigger_reconcilers_safely`）。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|------|------|---------|--------|-----------|
| B1 | `python -c` 模式运行时拦截器不装（sitecustomize 死代码路径） | Python 3.11+ site 模块安全机制；usercustomize 仓外手工 | 把 install() 调用下沉到 `zephyr.__init__` 或 conftest；或注册 usercustomize 安装脚本入 setup_dev_env | S | 是（施工须另走流程） |
| B2 | KillSwitch 无持久化，进程崩溃归零 | 设计自认（kill_switch.py:32） | 落盘状态文件+启动恢复（对齐 SessionRegistry 模式）；需裁定是否值得（当前仅 9 触发器风控面） | M | 待裁 |
| B3 | ops_guard in-process 补丁仅 5 入口安装 | opt-in 设计，普通脚本裸奔 | 收敛入口或提供 audit-only 全局安装钩子（usercustomize） | S-M | 是 |
| B4 | _trusted_git_env 双定义漂移风险 | commit_queue_landing 独立实现（历史） | 按 FUNCTION-DUP 约束收敛单一真源+re-export | S | 是 |
| B5 | FAST_PATH_ENV/SERIALIZER_MODE/FORCE_DELETE 全是单因子 env 信任 | 无身份绑定 | 至少加"仅网关进程可设"的审计对账（git_guard_bypass_reconciler 已有 reflog 对账，扩到 env 面） | M | 待裁 |

## 五、提速与合并机会
1. `scripts/session_worktree.py`（638 行处）与 `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` 双版本并存——ops_guard 安装点重复，合并候选。
2. ops_guard.py 1610 行单文件承载命令分析/API/补丁/CLI 四职责，可拆但**非必须**（内聚度尚可，动它触碰税高，只登记不建议）。

## 六、自审闸三态
**挖干可施工**（B1/B3/B4 有根因+修法+file:line 实证；B2/B5 列待裁）。

## 七、复核命令
```bash
python -c "from zephyr.security.llm_defense.llm_security.runtime_interceptor import is_installed; print(is_installed())"
grep -n "sanitized_spawn_env\|_trusted_git_env" scripts/ops_guard.py src/zephyr/gov_enforcement/rule_bridge/session_worktree.py | head
sed -n '125,135p' src/zephyr/security/access_control/kill_switch.py   # 9 触发器
grep -c "registry_id:" docs/registry_of_registries.yaml              # ROOR 底数（对照 02/03 分册）
```
