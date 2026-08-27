---
ttl: task_bound
title: 授权面收窄 + WriteAudit PID 级写删审计 调研裁定书（裁定五残留两项）
owner: ZephyrAlpha-Owner
language: zh
status: final
version: "1.0.0"
date: 2026-08-27
---

# 授权面收窄 + WriteAudit 调研裁定书

> 上游文档：docs/_working/reports/2026-08-27-mass-deletion-forensics.md（三起误删取证）、docs/_working/reports/2026-08-26-drift-writer-adjudication.md（#ARCH-264 O1~O7）、docs/_working/reports/2026-08-27-owner-leftover-adjudication.md（裁定五残留）
> 关联登记：#ARCH-277（三起误删闭环）、#ARCH-264（O3 WriteAudit 原计划）、#ARCH-257（wipe 事故判例）
> 裁定人：应 Owner 指令，以客观架构师身份调研裁定；施工按本文路线派单

---

## 一、调研范围与方法

两个议题：
1. **授权面收窄**：`ZEPHYR_COMMIT_GATEWAY` 环境变量全量子进程继承 → 改一次性令牌的提案
2. **WriteAudit**：PID 级写删审计（#ARCH-264 O3-P1，原裁定"立项待派单"）

方法：第一性原理分解 → 仓内证据链取证（全部带 file:line）→ 数据实证（审计日志全量分析）→ 业界对标（氛围编程社区 / 专业机构 / Windows 归因技术 / 量化行业）→ 裁定 → 治本施工方案。

---

## 二、现状取证（证据链）

### 2.1 授权变量全链路

**注入点（3 处）**：

| 注入点 | 方式 | 生命周期 |
|---|---|---|
| git_commit_gateway.py:2058 | `os.environ[_GATEWAY_ENV]="1"` 直接置**本进程**环境 | commit 成功后 → finally 弹出（:2105），窗口期覆盖 post-commit reconciler 触发 |
| git_commit_gateway.py:2765-2766 | `env = os.environ.copy(); env[_GATEWAY_ENV]="1"` 注入 git 子进程 | 单个子进程 |
| session_worktree.py:3938-3940 | `commit_env = os.environ.copy()` + 注入 worktree commit 子进程 | 单个子进程 |

**继承面（病灶）**：`os.environ.copy()` 是全量子进程继承——父进程被置位期间，**任何**子进程（reconciler worker、生成器、pytest、任意 shell 命令）天生携带授权标记。ops_guard.py:548-551 注释实证：「gateway 标记经 os.environ.copy() 被 reconcile worker 继承（reconcile_runner L708），若认 GATEWAY_ENV 则全部 reconciler 天然'已授权'」。

**消费方（5 处，两种语义混用同一变量）**：

| 消费方 | 用途 | 语义域 |
|---|---|---|
| ops_guard.py:511 `_is_authorized()` | **删除授权**——判"授权放行"后真删 | 删除域 |
| forged_gw_marker_gate.py:137 | GW 标记防伪逃生通道 | 提交域 |
| post_commit_guard（test_post_commit_guard_no_verify_threshold.py:33） | 未注册 session warn-only 放行 | 提交域 |
| git_guard.py:303/407/542 | stash/untracked 阻断逃生 | 提交域 |
| ops_guard.py:553 `_enforce_docs_untracked` | **已拒认 GATEWAY_ENV**（只认 FORCE_ENV） | 删除域（已收窄先例） |

**数据实证（决定性）**：对 `.runtime/gate_audit/ops_guard_delete.jsonl` 全量 39,642 条审计记录分析：

```
ALLOWED 原因分布：
  39,134  reconciler 已声明 delete（声明制直通）   ← 正道，上下文绑定
     503  白名单路径
       2  非保护区
       2  reconciler GATE-REGENERATE 已声明 delete
"授权放行"（GATEWAY_ENV 授权删除）记录：0 条
```

**结论：GATEWAY_ENV 的删除授权语义在真实运行中零合法消费方**——它只为事故服务（三起误删的 ALLOWED 记录正是它判的"授权放行"）。合法的自动化删除早已走**声明制**（I-GOV-2/T1①：reconciler 注册时显式声明 file_ops，上下文变量 `_RECONCILER_CTX` 线程级绑定，不经环境继承），39,134 条记录全是这条路。

**事故机理回放**（#ARCH-277 已闭环部分）：pytest 继承 GATEWAY_ENV → `_is_authorized()=True` → `guard_rmtree('src/zephyr')` 判"授权放行" → 真删。不变量+fixture 已治本测试上下文，但**变量本身的继承爆炸半径仍在**——下一个非常规上下文（daemon、e2e、手工 shell）仍是潜在事故面。

### 2.2 WriteAudit 与审计仪表化现状

**已落地**：
- 删除审计：ops_guard_delete.jsonl（四个硬拦入口：git_commit.py:464-469 / scripts/session_worktree.py:622 / reconcile_worker.py:509 / rule_bridge/session_worktree.py:2331 均装 in-process 补丁；guard_rmtree/guard_remove 显式 API 全量落盘）
- 热文件快扫：worktree_drift_watchdog.py:79 `_HOT_SCAN_INTERVAL = 10`（#ARCH-264 O3-P0，双频节拍已上线）
- CAS 写保护：safe_write_text（DEFAULT_HOT_FILES 热文件写前读新）
- quarantine 自管：30 天 retention + 带外删除 tamper 审计（#ARCH-264 O4①②）

**缺口（两起实证）**：
1. **带外裸删除零拦截零审计**（#ARCH-264 O4）：quarantine 快照两次被 `drift_*` 选择性清除，ops_guard 全审计窗口零命中——清除方未经任何仪表化通道（终端直删/IDE 直删），**无 PID、无进程、无身份**。
2. **秒级覆写者无法定凶**（#ARCH-264 W4）：60s 看门狗粒度下秒级写入者不留影（已靠 10s 快扫缓解观测窗，但**归因**仍缺——"内容变了"≠"谁写的"）。

**WriteAudit 原计划**（#ARCH-264 O3-B，已裁定立项 P1 未施工）：ReadDirectoryChangesW 监视热文件目录，事件落 `.runtime/audit/write_audit.jsonl`（ts/path/前后 hash/事件时刻活跃进程+open-files 句柄归因）。

**仓内独有归因资产**（原计划未利用）：`.runtime/session_registry.json` 持有 **PID → session_id** 映射（全 AI 会话心跳注册）——一旦拿到 PID，可直接回答"哪个 AI 会话"，比通用方案的"哪个进程"归因力强一级。

---

## 三、第一性原理分析

### 3.1 授权问题：一个变量两种语义，继承面即爆炸半径

**问到底：这个变量到底在证明什么？**

拆开看，`ZEPHYR_COMMIT_GATEWAY=1` 实际被用来证明两件完全不同的事：

| 语义 | 要证明的命题 | 合法载体 | 合理生命周期 |
|---|---|---|---|
| **提交域** | "这个 git commit 是网关发的"（防伪标记校验） | git commit 子进程 | 该子进程一生 |
| **删除域** | "这次删除被某个权威批准了" | 应当只有人或显式声明的上下文 | 审批动作的瞬间 |

提交域语义**现状已正确**（env 注入单个子进程，随进程消亡）。病灶全在删除域：**"被批准"的证明是一个可继承的环境变量——它证明的不是"这次删除被批准"，而是"这个进程的某个祖先进程碰过网关"**。三起误删中，pytest 进程与"审批"毫无关系，却持有"审批证明"。

**第一性原理结论**：环境变量是**进程树广播机制**，天然不具备"单次、单点、不可转发"的授权语义。用它来承载删除授权，等于把公章放在复印机旁边。业界的答案高度一致（见 §四）：授权凭证必须**短生命周期 + 绑定具体上下文 + 不可继承**。

**那要不要按原提案直接上"一次性令牌"？**

评估令牌化（token 文件 + PID 绑定 + 过期 + 单次）与更简方案的成本收益：

| 方案 | 机制成本 | 解决病灶？ | 评估 |
|---|---|---|---|
| A. 一次性令牌（原提案） | 新机制：签发/校验/过期/防重放/存储轮转 | 是 | **过度工程**：为一个"零合法消费方"的语义建签发基础设施 |
| B. 删除域语义剥离：`_is_authorized()` 删除判定只认 FORCE_ENV（人工显式），GATEWAY_ENV 退出删除域 | 改一行判定 + 影响面审计 | 是（数据实证零合法消费方） | **采纳**——docs_untracked 闸门 2026-08-26 已先行同款收窄，零事故 |
| C. 继承面收敛：网关派生非 git 子进程时显式剔除 GATEWAY_ENV | 一个 spawn 助手 + 3 处调用点 | 是（纵深防御） | **采纳**——与 B 互补，B 管"认了没用"，C 管"根本传不下去" |

数据已经替我们做了令牌化的需求验证：**39,642 条审计中 GATEWAY_ENV 授权删除零合法使用**——没有真实需求要保全，谈不上"改用更安全的机制满足需求"，正确动作是**让这条语义消亡**。

### 3.2 WriteAudit 问题：归因缺口的三层答案

**问到底：我们要回答的问题是什么？**

是「这次写/删是哪个主体干的」——归因（Attribution，#ARCH-264 裁定书三要素之一）。拆开三层：

1. **事件层**：文件变了（什么时候、哪个文件、变前变后 hash）——ReadDirectoryChangesW 零权限可得
2. **进程层**：变的那一刻谁在场（活跃进程+谁开着这个文件的句柄）——进程快照 + Restart Manager，零权限可得
3. **会话层**：这个 PID 是哪个 AI 会话——**仓内独有**：session_registry.json PID→session_id 直接映射

**为什么不能只靠现有护栏？** 护栏是"路由内仪表化"——走 guard_* 通道的删除全留痕；但 O4 quarantine 事件证明带外通道（终端直删、IDE 直写）天然绕开一切路由内机制。对带外通道，**唯一的防御是观测而非拦截**（Windows 不装内核驱动就无法拦截；而观测层 RDCW 零权限可得）。

**精确归因要不要上？** Windows 技术矩阵（§四 4.3）：SACL/4663 精确但需 Owner 管理员操作且日志量大；ETW 重量且独占；minifilter 内核开发一票否决。对本项目场景（热文件目录小、候选写者个位数、全是同用户 python 进程），**近似归因（事件+进程快照+会话映射）在工程上已够定凶**——O4 裁定书本来的判断就正确，本次补足的只是加上仓内独有的会话层。

### 3.3 长远期战略契合（100% AI 开发）

- 单写者终态（08号文提交队列）不变：授权语义剥离让"删除授权"收敛为「人工显式 FORCE_ENV + reconciler 声明制上下文」两通道，与队列元数据天然兼容（未来队列项自带声明）。
- 可追溯性基建复用：WriteAudit 的归因链（PID→session→heartbeat）全部复用既有注册表，不建新真源。
- 避免过度工程（项目记忆既定纪律）：不建令牌签发基础设施、不碰内核驱动、不做全盘监控。

---

## 四、业界对标

### 4.1 氛围编程社区（AI coding agent 安全）

- **OpenAI《Running Codex safely at OpenAI》（2026-05）**：把 coding agent 安全边界抽象为五槽位——Sandbox / Approval / Network / Credential / Rules。Codex 默认 workspace-write 沙盒（只能写工作区，越界需审批），凭据入 OS keyring。
- **Claude Code 原生沙盒**：用 OS 级原语（macOS Seatbelt / Linux bubblewrap）做文件系统+网络隔离，权限规则 deny/ask/allow 声明式配置，PreToolUse hook 自定义判定。其核心设计动机与本案同源——**审批疲劳（approval fatigue）会让"每次问人"退化为"无脑全过"**，所以用边界换审批。
- **Cursor**：`.cursorignore` 工具级读阻断，但官方明确承认**终端/MCP 可绕过**——工具级控制防不住 OS 级访问，敏感文件应移出工作区或用 OS ACL。
- **社区共识**：工具级 ignore 文件不可靠（多种绕过 CVE 实证）；有效防线 = OS 级边界 + 短生命周期凭据 + 审计。

**对本项目的印证**：我们的 PROTECTED_PREFIXES + in-process 补丁相当于 Claude Code 的声明式规则+hook 层；带外裸删零观测的缺口，业界答案是 OS 级观测（沙盒/SACL），与裁定 B 一致。

### 4.2 专业机构（授权与身份）

- **OWASP Agentic AI Top 10（2026）**：凭据暴露列为 agentic 应用核心失效模式；指南明确——**per-task 签发、运行时铸造、动作结束即吊销**，"Issue secrets per task, not per process lifetime"。
- **IETF WIMSE workload identity 草案**：环境变量投递凭证被标注为静态、初始化后不可变、易随进程树泄漏；推荐方向是 workload identity（SPIFFE/SPIRE）+ 策略引擎运行时判定。
- **CI/CD 通行实践**（GitHub Actions OIDC 等）：每个 job 铸造绑定 repo+job 上下文的短时令牌，替代长期 PAT。

**对本项目的印证**：令牌化方向本身符合业界趋势——但业界令牌化解决的是"**有合法跨进程授权需求**"的场景。仓内数据证明该需求在删除域为零（§2.1），故裁定 B+C 剥离+收敛，令牌化登记为触发式候选项（出现真实跨进程授权删除需求时再评估），这是"先静态映射、证据驱动演进"纪律的应用。

### 4.3 Windows 文件归因技术矩阵

| 技术 | 归因力 | 权限 | 成本 | 结论 |
|---|---|---|---|---|
| ReadDirectoryChangesW / FileSystemWatcher | 无（仅通知"变了"）——Raymond Chen 明示文件系统不记录"谁" | 无 | 极低 | **事件层采纳** |
| NTFS SACL 对象访问审计（Event 4663） | **精确**（PID+进程名+用户+访问掩码） | 管理员 + auditpol 启用 | 日志量大（限热目录可控） | **可选精确层**（Owner 一次性开启） |
| ETW FileIo 内核跟踪 | 精确（FileIo_Create 带全路径+PID） | 管理员 + 独占 NT Kernel Logger 会话 | API 复杂、与 PerfMon 等冲突 | 否决（过度） |
| Minifilter 内核驱动 | 可拦截+精确 | 内核开发 | 最高 | 否决 |
| Restart Manager（谁开着这文件） | 近似（句柄级） | 无 | 每文件 1~5ms | **进程层采纳** |
| 进程快照（WMI Win32_Process 同用户） | 近似（在场清单+cmdline） | 无 | 低 | **进程层采纳** |

### 4.4 量化行业

- **监管级审计追踪**（SEC/FINRA CAT、MiFID II）：全生命周期事件不可变留痕（WORM 语义）+ 精确到主体的归因——本项目 jsonl 审计族（大小轮转+只追加）已是同构实现，WriteAudit 是把同一原则补齐到"写删事件"这一格。
- **职责分离（SoD）**：量化机构铁律"提议者≠批准者≠执行者"——映射到 100% AI 开发：AI 可提议+执行，但"删除保护区"的批准通道（FORCE_ENV）应只有人能点亮，与裁定 A 语义剥离同向。

---

## 五、裁定结果

### 裁定 A：授权面收窄 = 语义剥离 + 继承收敛（替代直接令牌化）

1. **A1 删除域语义剥离（P0）**：`ops_guard._is_authorized()` 分拆——删除授权判定**只认 FORCE_ENV**（人工显式）；GATEWAY_ENV 永久退出删除域。依据：39,642 条审计零合法消费方 + docs_untracked 闸门同款收窄先例（2026-08-26 起零事故）。提交域消费方（forged_gw_marker/post_commit_guard/git_guard）**不动**——那是 GW 标记的本职语义。
2. **A2 继承面收敛（P0）**：网关/worktree 派生**非 git 子进程**时经统一助手 `sanitized_spawn_env()` 显式剔除 GATEWAY_ENV/FORCE_ENV（git commit 子进程保留注入）；reconcile worker 入口既有声明制上下文不变。纵深防御：即使未来有人误加消费方，变量物理上传不下去。
3. **A3 观测期→硬拦两阶段（沿用 CAND-GOVSEC-001 既定模式）**：A1 先以"双判记录"模式上线（仍放行但落 `would_block_if_narrowed` 审计），24h 观测零合法命中后翻硬拦。
4. **A4 令牌化登记挂起（P3 触发式候选）**：仅当未来出现真实"跨进程授权删除"需求（当前为零），再按 OWASP per-task 模式评估一次性令牌（签发/绑定 PID+过期+单次+审计）。当前**不做**——为零需求建基础设施违反 YAGNI。

### 裁定 B：WriteAudit = 三层归因守护（立项施工，P1）

1. **B1 WriteAudit 守护 MVP（P1，本批施工）**：轻量守护进程（模式同 drift watchdog daemon），ReadDirectoryChangesW 监视热目录集（DEFAULT_HOT_FILES 所在目录：`_registry/catalogs/`、`design_memos/`、仓根平铺、`.runtime/quarantine`），事件落 `.runtime/audit/write_audit.jsonl`：ts/path/op(create|write|delete|rename)/前后 hash/事件时刻进程快照（同用户 python/cmd/powershell+cmdline）/Restart Manager 句柄归因/**PID→session_id 会话归因**（查 session_registry.json，仓内独有能力）。
2. **B2 watchdog 联动**：drift 告警自动附带 write_audit 同窗口事件与嫌疑会话清单——告警从"有人动了"升级为"谁动的"。
3. **B3 SACL 精确层（P2 可选，Owner 一次性管理员操作）**：`auditpol /set /subcategory:"File System" /success:enable` + 热目录 SACL（Everyone/Write）→ 同一守护收集 4663 事件入 write_audit.jsonl（exact_attribution=true 标记）。不做也不阻塞 B1/B2。
4. **边界（防洪峰纪律）**：只监视热目录集（个位数目录），**不做全盘监控**；jsonl 走 audit_jsonl_writer 50MB 轮转；守护自身心跳入 session_registry。

### 不做清单（否定式裁定）

- 不建一次性令牌签发基础设施（零合法需求，A4 挂起候评）
- 不动提交域 GATEWAY_ENV 语义（GW 标记防伪本职，改动=新风险）
- 不上 ETW/minifilter/内核驱动（管理员依赖+复杂度 vs 近似归因已够定凶）
- 不做全盘文件系统监控（洪峰+信噪比崩盘，热目录集已覆盖全部事故面）
- 不为带外写删建"拦截"（无内核驱动不可拦截；观测+归因+既有 git restore 判例恢复链已闭环）

---

## 六、治本施工方案

### 批次规划（两批，A 先 B 后）

| 批 | 内容 | 交付物 | 验收 |
|---|---|---|---|
| **批1 授权面收窄** | A1 `_is_authorized()` 语义剥离（双判记录模式）+ A2 `sanitized_spawn_env()` 助手接入 3 处派生点 + A3 观测审计 | scripts/ops_guard.py 判定分拆；git_commit_gateway.py/session_worktree.py 派生点接入；tests 红队新测：投毒 GATEWAY_ENV 下保护区删除必 BLOCKED（不再依赖 pytest 不变量单点） | 24h `would_block_if_narrowed` 零合法命中 → 翻硬拦；红队 87+新测全绿 |
| **批2 WriteAudit MVP** | B1 守护进程（src/zephyr/gov_enforcement/rule_bridge/write_audit_daemon.py 或 scripts/governance/ 新脚本）+ B2 watchdog 告警联动 + 单测（事件捕获/hash 对比/会话归因/轮转） | write_audit_daemon + write_audit.jsonl 落盘 + watchdog 告警带嫌疑清单 | 单测全绿；手工带外删热目录文件 → 5s 内事件落盘且带 PID/session 归因 |

### 施工纪律

- 每批独立提交走 git_commit.py 网关（常态三旗标），注册表类立即单文件提交
- A1 翻硬拦前必须有 24h 观测数据（沿用 42h→24h 先例，观测期不得跳过）
- B1 守护纳入既有 daemon 治理（心跳/session_registry/IDE 健康面板可见）
- 登记链：creation_token（新文件）+ module_translation（plain_zh）+ #ARCH 新条目（本裁定施工登记）

---

## 七、大白话解释

### 问题一：授权变量是什么毛病？

**打个比方**：公司规定"删重要文件要盖章"。现在的做法是——盖章机每盖一次章，就顺手在**整层楼的空气里**喷一遍"已盖章"香水。结果这层楼里任何人（包括来打扫的、送快递的）身上都带着"已盖章"的味道，拿张纸就能去删文件。

三起误删就是这么发生的：测试程序（pytest）只是路过，身上沾了香水味，护栏一闻"有授权"，唰一下把 src 整包 3500 个文件真删了。

**裁定怎么说？** 查了近 4 万条删除记录，发现**正经干活的人从来不用这瓶香水**——他们都走"签字登记制"（reconciler 声明制：我先登记我要删什么，系统核对名单放行）。香水味唯一的服务对象就是事故。

所以裁定不是"换瓶更高级的香水"（原提案的一次性令牌），而是**把这瓶香水直接扔掉**：删除授权以后只认两样——① 人亲手按的按钮（FORCE_DELETE）；② 签字登记制的名单。同时再给网关加个规矩：派小弟出去办事时，先把小弟身上的香水味洗干净，物理上断绝传播。

令牌那套设备（签发机、防伪、过期管理）登记在案：哪天真有"跨车间授权删货"的需求再买，现在买是为一台不存在的机器配遥控器。

### 问题二：WriteAudit 要解决什么？

**打个比方**：仓库装着摄像头（ops_guard 审计），但只拍了**正门**——走正门的搬运全有录像。结果有人两次从**窗户**翻进来把证物柜清了（quarantine 事件），录像里啥都没有。更糟的是，就算发现货架被动过，也只能说"东西少了"，说不出"谁干的"。

**裁定怎么做？** 在最重要的几个货架上方装**带人脸识别的摄像头**（WriteAudit 守护）：哪个文件被写/被删，5 秒内记下——什么时间、什么文件、动前动后指纹（hash）、当时谁在仓库里、谁手里正扶着这个货架（句柄）。最妙的是仓里本来就有员工花名册（session_registry：工号→哪个 AI 班组），摄像头拍到工号，直接报出"是哪个班组"，比同行通用的"看到个人影"高一级。

再往上还有一层**可选的公安级天网**（Windows SACL 审计，事件 4663，能精确到进程名）——需要你（Owner）用管理员身份开一次总闸，开不开都不影响摄像头先用起来。

**一句话总结两个裁定**：
1. 删掉"会传染的授权"，让批准只留在人手里和登记册上；
2. 给热文件装上"能说出谁干的"的摄像头，从此带外小动作零遁形。
