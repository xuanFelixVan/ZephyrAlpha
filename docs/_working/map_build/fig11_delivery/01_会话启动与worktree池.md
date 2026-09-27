---
ttl: task_bound
completes_when: 图11 封矿且 D11-S01~S03 环节进 config/dev_delivery_map.yaml 四件套后本件转归档参考
title: 图11 作业簿01·会话启动与 worktree 池（D11-S01/S02/S03）
owner: st-mapbuild-20260924（W-A1 车道）
---

# 01_会话启动与worktree池

> 坐标纪律：本簿全部 `文件:行` 为 2026-09-24 在 worktree `.aidrafts/st-mapbuild-20260924` 实查；主区只读取证未写入。
> 引用避坑：按战役已知坑，本簿不写 `裁定#<数字>` 紧邻形态与 `宪法 §N.M` 裸挂形态（REFERENCE-INTEGRITY 自触），改用"裁定 19-B（去井号）""宪法冷启动序列第 N 条"写法。

## §0 覆盖环节

- **D11-S01** 会话冷启动与开班检查
- **D11-S02** worktree 分配与池化
- **D11-S03** 会话心跳与活性判定

族职责一句话：把"一个 AI 对话"变成仓库可治理的实体——注册 session、拿到物理隔离的 worktree、并让"它还活着"这件事有 30s 节拍的机器证据。

---

## §1 D11-S01 会话冷启动与开班检查

### 上（谁触发/输入从哪来）
- IDE 对话层触发=🌑（骨架 §6🌑-1 维持：仓库内无机生面，可观测上限=`session_worktree.py:9` CONSUMERS 头"AI 对话启动时调用（AGENTS 宪法）；scripts/governance/session_worktree_cli.py"）。
- 规范输入：宪法冷启动序列六条（RULE-ENV/GUARDIAN/WORKTREE/CAPABILITY-LOOKUP/DEPGRAPH/REGISTRY/SSOT，见 AGENTS 宪法 §0；GUARDIAN 验证件=`scripts/register_process_reaper_task.ps1` 计划任务在盘 + `python -m zephyr.trading.process_reaper --status`）。
- 代码输入：`src/zephyr/governance/ops_governance/phase_manager.py:248 session_startup(quick=True)` 自述"进入项目后 MUST 调用的第一个函数"（:249）。

### 下（输出给谁）
- 返回 dict `{ready, phase, green/yellow/red, checks[], next_action}`（:257-268 契约），ready=red==0（:344）；`ready=True` 才进 D11-S02 取 worktree。
- 反向消费上一会话遗产：`read_latest_handoff()`（`session_concurrency.py:839`，按 mtime 取最新 `handoff_*.json`，:846-850）——S09 的闭环对端。

### 内（父-子-孙全清单）
- 父：`phase_manager.session_startup`。
- 子①检查集：`_FAST_CHECKS` 10 项（:295-306，会话管理器/会话连续性/锁协议/蓝图完整性/关键路径/脚本清单/Python 环境/Pre-commit 配置/审计上下文/预算执行器）+ `_SLOW_CHECKS` 6 项（:308-315，孤儿检测/临时文件扫描/注册表一致性/编码安全/密钥泄漏/危险 Shell）；全走 `ThreadPoolExecutor(max_workers=8)` 并发（:319-338），任何 check 抛异常=RED（:330-331，fail-closed）。
- 子②真源桥梁：check 函数全部来自 `zephyr.governance.ops_governance.phase_check_registry`（import 清单 :276-293；文件头 DEPENDENCIES :4）；`PhaseGate.run_checks` 默认 `run_check`（:79-83）。
- 子③阶段模型：`PHASE_SEQUENCE` 三阶段（:96-215）；Phase 0 `gate_checks` 实数 **17** 条（:106-131）——与文件头散文"Phase 0 (15 检查)"（:25-28）**漂移**，本簿只认列表+复核命令（簿末 §实查-1），散文计数按宪法"计数用字段不写死"纪律属待修面。
- 孙：R1 防御数据流起点 `scripts/record_session_start_commit.py`（HEAD hash 写 `session_logs/<sid>/session_start_commit.txt`，:24-31；消费方=其头 CONSUMERS "project_rules 进门流程 + PostDocReviewScanner._get_session_start_commit()"，INVARIANTS 40 位十六进制校验 :7）。
- 自动化程度：全自动（一次函数调用）；但宪法六条中 GUARDIAN/ENV 两检查依赖 shell 实测，不在 session_startup 检查集内（=人机混合环节）。

### 旁（撞车面五选一）
- 撞 15 步施工流（construction_workflow_policy，图14 候选域）：其 Step0/冷启动与本环节同"进门"语义，但对象不同（施工任务 vs 会话实体）→ **引用**（骨架 §3 第 2 行判定维持，无推翻证据）。
- 撞 GOMAP：GOMAP 管运行时模块，本环节为开发时会话生命周期 → 骨架 §0 门③已实证 out_of_scope 排除（config/governance_operations_map.yaml:16-19），维持 **引用**。

### 史（退役/被取代）
- `session_claim.py`（rule_bridge）整族退役：头 INVARIANTS :8 逐字"已废弃（superseded by session_worktree_start + HELD-OVERLAP gate，FP-ISO.4C，2026-07-04）：session_claim_start/add/check/heartbeat/end 零实际调用方（死代码）"；仅 `generate_session_id`（:91-97，格式 `sess-{PID}-{yyyyMMddHHmmss}`，:47）存活被 session_worktree 调用。
- Phase 0 检查数 15→17 的扩容史：文件头 :25 记 2026-05-08 ISSUE-3 扩展"三阶段 51 检查"，现列表 17+27+16——文档层未追平（见「内」向漂移记录）。

### 新（最新演化）
- 启动健康度 smoke test：`_run_startup_health_check`（`session_worktree.py:2480`，#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S7 Phase 3.3）——3 项检查（capability_lookup gate 可 import / `.runtime/lookup_audit/` 可写 / write_lookup_audit_log 可调，:2489-2495），失败要求 [ESCALATION] 上报而非静默 workaround（:2485-2487）；由 `session_worktree.py:8459` 暴露公共入口。该检查**尚未**并入 phase_manager 检查集（两文件互 import 无，实查：`grep check _run_startup` 无命中）=两代开班面并存的当前态。

---

## §2 D11-S02 worktree 分配与池化

### 上
- 触发：S01 通过后 AI 调 `session_worktree_start`（`session_worktree.py:2607`，签名 :2607-2612 含 `breaking_change/allow_concurrent`）。
- 规范输入：宪法 RULE-WORKTREE"session_worktree_start 为默认；降级直改主区=显申请制"——申请制三件真源=`docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md:278-318`（§10，Owner 2026-09-15 采纳；登记原因经 `[GW:<sid>:non-worktree]` 自动留痕 :285-291；周审计计数命令 :293-297）。

### 下
- 产出 worktree 路径 + 注册条目 → S03 spawn daemon 传锚点（`session_worktree.py:3001 _spawn_heartbeat_daemon(sid, root, worktree_path=wt_path)`）；S04/S06 在该目录内 claim/编辑/提交；S07 merge 或 S08 abort 消费之。

### 内（本簿重心，父-子-孙）
- 父：`session_worktree.py session_worktree_start`。子链按调用序（全部实查行号）：
  1. **双向阻断** `_check_concurrency_block`（:2349，定义于注册 session 之前 :2765）：`allow_concurrent=True` 直接放行（:2356-2357）；`breaking_change=True` 且存在其他活跃 session → `BREAKING_CHANGE_CONCURRENCY_BLOCKED`（:2362-2382）；`breaking_change=False` 且他人声明 breaking_change → `BREAKING_CHANGE_AVOIDANCE_BLOCKED`（:2384-2402，经 `registry.find_breaking_change_session` `session_concurrency.py:450`）；任何异常 fail-open 放行（:2404-2407，对标 held_overlap_gate）。
  2. **任务去重** `_check_duplicate_task`（:2412，调用点 :2779）：判据 Jaccard |A∩B|/|A∪B|≥0.5（:2427），task_files=任务文件指纹（:2423），阻断+逃生通道 `allow_duplicate=True`（:2429），异常 fail-open（:2431）。
  3. **注册** `registry.register`（:2832）——SessionRegistry 恒用主仓根（头 INVARIANTS :15 末段"确保所有 session 共享一个注册表"）。
  4. **清扫四连**（全在 start 顺带、非阻断）：`_sweep_stale_worktrees`（:2861←定义 :2063，公共壳 `session_worktree_sweep` :2194 且 :2127 硬拒私有直调）；`_sweep_quarantine`（:2895←:662，72h）；`_sweep_quarantine_refs`（:2906←:1077，refs/quarantine/ 72h 过期）；`_cleanup_orphan_draft_scripts`（定义 :2263，头 INVARIANTS :15 载明"仅删 .aidrafts/ 根 age>1h 的 _* 文件不删 sess-* 目录"）。
  5. **幂等复用**：`manager.worktree_exists(sid)` 判存在（:2915-2919），已存在直接复用不重建。
  6. **池化 lease**（P3.3 优先路径 :2922-2964）：`get_pool(root)`（:2937）→ `pool.lease(sid)`（:2941←`worktree_pool.py:277`）→ 成功则 `prefetch_async(1)` 异步补池（:2958）；lease 任何异常只 warn、fall back `manager.create_session_worktree(sid)`（:2969←`worktree_manager.py:342`）——"pool 是性能优化非功能必需，永远不阻断 session 启动"（worktree_pool.py:8 INVARIANTS 逐字）。
  7. **base 新鲜度（start 档）** `_ensure_worktree_base_fresh(stage="start")`（:2981←定义 :3312，同函数 commit 档再跑一次，见 S06）。
  8. **心跳 daemon spawn**（:3001，见 S03）。
- 孙（`worktree_pool.py` 全 637 行读透）：
  - lease 原子序列（:277-384）：idle 扫描仅认 `pool-` 前缀子目录（:195-209）→ 目标路径存在即放弃（:313-320）→ 未注册即清理孤儿袋（:322-330←_cleanup_pool_worktree :227：remove --force→prune+物理删→branch -D 三步）→ `git worktree move .aidrafts_pool/<pool_id> .aidrafts/<sid>`（:338，**Windows 文件锁 3 次重试×0.5s**，杀软/索引器句柄病根 :333-335）→ `git branch -m session/pool-… session/<sid>`（:355，失败回滚 move 回池 :363-375）。
  - pool_id=`pool-{YYYYMMDDHHMMSS}-{4hex}`（:189-193，secrets.token_hex 防撞）；分支前缀复用 `session/` 避免双 pool-（:108-110 注释）。
  - `release()` **当前 NO-OP**（:490-507"worktree 由 merge/abort 删除，pool 通过 prefetch 补充"）——即池是"预创建-消耗"单向流，无回收复用（未来增强位 :496-498）。
  - `cleanup_stale(max_age_hours=24)`（:552-590）崩溃孤儿兜底；`stats()/list_idle()`（:509-550）诊断面；`warmup()` 同步预热（:592-606）。
  - 池目录独立 `.aidrafts_pool/` 的病根：若放 `.aidrafts/.pool/` 会被 `_sweep_stale_worktrees` 当 session_id 误扫（:46-49 逐字）。
  - 所有 git 调用带 `ZEPHYR_GIT_GUARD_FAST_PATH=1`（:118/:160，GIT-BUDGET-INV-003）——与 `session_worktree._trusted_git_env`（:406）同源、且 :116-117 载明"FUNCTION-DUP gate 禁止重复定义故内联构造"。
- **两代目录并存事实与差异**（骨架坐标面未含，本簿补实证）：
  - 第一代（本图主链）=`worktree_manager.py:229 _drafts_dir=.aidrafts`，`_wt_path` 恒返 `.aidrafts/<sid>`（:254-257），分支 `session/<sid>`（头 INVARIANTS :8）。本会话活体 `.aidrafts/st-mapbuild-20260924` 即此代（主区实查 `git worktree list` 共 29 条，含 `.aidrafts/st-*` 多条）。
  - 第二代=`scripts/session_worktree.py`（697 行独立 CLI，头 :10 INVARIANTS 逐字"worktree 在 .worktrees/ 下；分支前缀 ai/；merge 需用户确认"；五命令 create/exec/merge/abort/list :27；关联议题 ARCH-AICOLLAB-001 :24）→ `worktree_manager.py:231 _session_worktrees_dir=.worktrees` 即其根。主区实查 `.worktrees/` **13 项活跃**（AI-GOVA-001/st-e2e-20260924 等）、`.aidrafts/` 10 项、`.aidrafts_pool/` 0 项（idle 空，lease 当前会走 fall back 直建）。
  - 收口史：`worktree_manager.py:580-584` 逐字——"后者=第二代机制…长期盲区导致 WORKTREE-REQUIRED gate 在 .worktrees 内误判'非 worktree'，收口 ARCH-RECONCILER-WORKTREE-RACE 在新机制下的复发，ARCH-WORKTREE-ENV-001"；治后 `get_current_worktree` 双基判定 `bases=[.aidrafts, .worktrees]`（:590-604，且 repo_root 本身在 worktree 内时锚回主仓 :591-596）。
  - 第二代并非孤岛：其 cmd 注册对齐 pid=0 逻辑 session 并普及 heartbeat daemon（scripts/session_worktree.py:214-222"对齐 rule_bridge session_worktree_start…#56 子项 2"）。
- **HELD-OVERLAP 判定归属澄清**：start 阶段不判 held 重叠（重叠判定在 claim/commit 侧：`_check_held_overlap` `session_worktree.py:3074` + gateway HeldOverlapGate，见簿 02 §S04）；宪法"HELD-OVERLAP 不硬闯"落点即该 commit 硬阻断。
- 自动化程度：全链自动；申请制留痕半自动（人写原因，机打 non-worktree 标记）。

### 旁
- 撞 `worktree_lifecycle`（rule_bridge，MATURITY=production 头 :8 实查）：状态机持久化 `.runtime/worktree_lifecycle/`，转换表真源=`config/worktree_state_machine.yaml`（states: created/active/idle/quarantined…，头 implementation_status "operational — consumed by worktree_lifecycle.py"；description 自述取代死代码 session_state_machine.yaml）。处置=**吸收**（S02/S08 子环节，骨架 §3 第 8 行判定维持；坐标本簿补登）。
- 撞 `worktree_drift_watchdog`（头 MATURITY=production、INVARIANTS 全读）：只告警不阻断、quarantine 30 天、ARCH-308 A1 死会话清扫"工作树内容永不销毁"——处置=**吸收** S08 子环节（见簿 03），与 S02 是"分配 vs 分配后漂移观测"的上下游关系，**引用**不并环节。
- 撞第二代 CLI（上「内」向已列）：两代机制同职责（分配 worktree+merge），处置=**融合待裁**——本车道不裁，列入溢出条目交总包（骨架 S02/S07 真源格均未含第二代）。

### 史
- P3.3 池化 2026-07-19 立（worktree_pool.py:20 头 date；病根=Windows 14 万文件工作区 `git worktree add` 单次 2-5s，:24-28）。
- 旧案 `.aidrafts/.pool/` 被否决改独立目录（:46-49）。
- ARCH-GIT-CALL-BUDGET fast-path 授权链（session_worktree.py:391-401：alias 拦截在 14 万文件+fsmonitor 路径上放大 git.exe 0xc0000005 崩溃）。
- 第二代 `.worktrees`（#ARCH-AICOLLAB-001）先于池化出现，WORKTREE-REQUIRED 盲区事故后双基收口（ARCH-WORKTREE-ENV-001）。

### 新
- 2026-09-15 申请制（policy §10 头逐字，含 2026-09-14 单日四起共享工作树事故背景 :280-283）。
- 主区实查（只读）：`.aidrafts_pool` idle=0 → 当下每个新会话都在走 fall back 直建；k=4 队列侧落地池（`.runtime` 下 worktrees/w0..w3，骨架 C09 已证）与本文话侧 `.aidrafts_pool` 是**两套不同对象**（会话隔离 vs 落地串行），图节点命名须防混——一句话外部对标：多智能体编码业界以 per-agent worktree 为标准配置（policy §10 背景段已引，不另抄）。

---

## §3 D11-S03 会话心跳与活性判定

### 上
- spawn：`session_worktree_start` 尾步 `_spawn_heartbeat_daemon`（`session_worktree.py:1428`，DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP，`heartbeat_daemon.py:37-38`）；调用点 :3001。
- kill：merge `session_worktree.py:7161` / abort :7631（7497+135 相对行换算，调用 `_kill_heartbeat_daemon` 定义 :1560）；全量清场 `kill_all_heartbeat_daemons` :1616。

### 下
- 写 `SessionRegistry.last_heartbeat`（`registry.heartbeat` `session_concurrency.py:484`）→ 消费方①`_is_session_alive`（:266）判活决定 held_files 去留；②`lock_files._is_stale` 裁定 252 语义下复用同一判活函数（见簿 02 S04）；③salvage 双证判死（簿 03 S08）。
- 审计面：`.runtime/sessions/<sid>/heartbeat.jsonl`（`heartbeat_daemon.py:120-125`，每条 {ts,pid,status} :136-142；status 谱 started/alive/exited/interrupted/error/fatal :133）+ `heartbeat.pid`（`session_worktree.py:1355`）。

### 内
- 父：`heartbeat_daemon.run_daemon`（:275，独立进程入口，`__main__` 手调通道 :399-411）。主循环五退出闸（全实查）：
  1. 不在 registry → exited "session not in registry"（:333-335←_session_in_registry :185）；**2026-08-19 治本**：原 `.get()` 每轮 AttributeError 被吞保守返 True，daemon 存在性自退静默失效，12 僵尸 daemon 实证（:195-198 逐字，修法=改 `registry.get_session` :198）。
  2. 失锚自退：`_worktree_anchor_alive`（:236，判定 :340-346；CAND-DAEMON-001 2026-08-17，#99 族实证 2 个两天残留 daemon；锚未配置=旧 spawn 兼容不判 :249-250）。
  3. idle 超 `_MAX_IDLE_SECONDS=1800`（:112-117 top-import 自 `session_concurrency._ACTIVITY_IDLE_TIMEOUT_SECONDS` :169，判定 :354-365）——活性锚=`last_activity`（仅 register/claim_file/register_dependency 刷新，**heartbeat 绝不回退 last_heartbeat** :208-211 逐字）。
  4. registry 连续错误 >10 → fatal 退出（:376-382）；单次错误退避 5s continue（:101/:383）。
  5. signal（SIGTERM/SIGINT，Windows CTRL_BREAK）→ 写 interrupted 后 exit 0（:258-272）。
- 节拍：`_HEARTBEAT_INTERVAL=30`（:99），首跳延迟 1s 给 register 让路（:103/:327）。
- 判活双轨（session_concurrency）：pid>0=PID 死即判死+TTL 3600s 兜底（`_is_session_alive` :281-288；`_SESSION_TTL_SECONDS` :146）；pid=0 逻辑 session=90s 心跳新鲜窗（:289-292；`_HEARTBEAT_TIMEOUT_SECONDS` :152 含病根注 :147-151）。
- 生命周期文件清理：`cleanup_heartbeat_file`（:161-182，只删 jsonl 不删 session 目录，因同级 `emergency_count.json` 归 emergency_commit 管 :164-165/:49）。
- 自动化程度：全自动（daemon 自起自退自审）。

### 旁
- 撞 commit_belt_daemon（队列侧 `belt_daemon.heartbeat` 文件，骨架 C09）：同名"heartbeat"对象不同（OS 进程活性 vs 消费者存活）→ **引用**（图节点须带 domain 前缀防混）。
- 撞 process_reaper（宪法冷启动第 2 条守护）：reaper 杀进程/本环节证进程活，互不建边 → **引用**。

### 史
- v0（仅 TTL=3600）→ pid=0 session 死后 held_files 占锁 1h → HELD_OVERLAP 误阻断 → allow_overlap 62× 超阈（`session_concurrency.py:148-151` 逐字；P0 治本 ARCH-HEARTBEAT-001，2026-07-20 立 daemon `heartbeat_daemon.py:21`）。
- 活性反转 bug（v1 残留）：daemon 自保活死会话，实测 sess-39820/sess-53456 僵尸（`session_worktree.py:1428` 邻域注释；daemon 文件 :105-110 病根段，ARCH-HEARTBEAT-002 2026-07-23 以 last_activity 治）。
- 阻塞窗口叙事：1h→90s（daemon :56-60）。

### 新
- 失锚自退（2026-08-17）+ get_session 修正（2026-08-19）为本机制最近两刀；绕过权衡文档化（daemon :62-69：允许手调 `registry.heartbeat()` 一次但无法伪造持续心跳=设计内权衡，非漏洞）——外部对标一句话：与 K8s lease-renew 同型（worker 续 lease、控制面按超时驱逐），本项目多一层"锚点=目录存活"。

---

## §末-1 溢出条目（交总包落骨架，本簿未改 00_skeleton）

| # | 条目 | 建议落点 | 证据 |
|---|------|---------|------|
| O1 | S02 真源格补"第二代 `.worktrees` 机制"（scripts/session_worktree.py 697 行 CLI，分支前缀 ai/，五命令；主区 13 项活跃） | S02/S07 真源映射 | scripts/session_worktree.py:10,27；worktree_manager.py:231,580-584；主区 `ls .worktrees|wc -l`=13 |
| O2 | S02 子环节显式登记 worktree 状态机（worktree_lifecycle.py + config/worktree_state_machine.yaml，operational） | S02「内」向挂载件 | worktree_state_machine.yaml:17 implementation_status；worktree_lifecycle 头 :8 |
| O3 | S03 真源坐标精化：骨架写"heartbeat_daemon.py:39-40"实为 docstring 行；机制真源=常量 :99 与循环 :275/:330-388；session_concurrency.py:148 为注释行，真源= :146/:152/:169 + `_is_session_alive` :266 | S03 状态列坐标 | 本簿 §3 各行 |
| O4 | S01 文档漂移：phase_manager 文件头"Phase 0 (15 检查)"vs 列表 17 项；"三阶段 51 检查"vs 现 17+27+16 | 叶层（不增枝），建议生成器面消化 | phase_manager.py:25-28 vs :106-131/:141-178/:189-213 |

## §末-2 自审裁定

**干**。S01/S02/S03 六向齐；「内」向挖到 lease 重试-回滚、双向阻断四分支、daemon 五退出闸、两代目录双基收口全部带行号；两处骨架坐标修正（O3）与一代新事实（O1/O2）已溢出待包。欠账无；溢=4 条。

## §末-3 实查命令（可复跑，全部只读）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
cd D:/ZephyrAlpha   # 主区只读取证（勿写）
# 1) S01 Phase0 计数（文档漂移复核）
python -c "import sys;sys.path.insert(0,'src');from zephyr.governance.ops_governance.phase_manager import PHASE_SEQUENCE,ConstructionPhase as C;print({p.value:len(g.gate_checks) for p,g in PHASE_SEQUENCE.items()})"
# 2) 两代目录与池现态（史/新向）
ls .aidrafts | wc -l; ls .worktrees | wc -l; ls .aidrafts_pool | wc -l; git worktree list | wc -l
# 3) S02 双向阻断分支锚点
grep -n "BREAKING_CHANGE_CONCURRENCY_BLOCKED\|BREAKING_CHANGE_AVOIDANCE_BLOCKED\|Jaccard" src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
# 4) S03 daemon 三治本坐标
grep -n "_HEARTBEAT_INTERVAL = \|_MAX_IDLE_SECONDS\b\|CAND-DAEMON-001" src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py | head
grep -n "_HEARTBEAT_TIMEOUT_SECONDS: int\|_SESSION_TTL_SECONDS: int\|_ACTIVITY_IDLE_TIMEOUT_SECONDS: int" src/zephyr/security/access_control/session_concurrency.py
# 5) 第二代 CLI 头（溢出 O1 复核）
sed -n '10p;24,27p' scripts/session_worktree.py
```
