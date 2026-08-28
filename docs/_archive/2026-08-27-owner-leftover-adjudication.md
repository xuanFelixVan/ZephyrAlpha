---
ttl: permanent
title: Owner 遗留五项架构裁定书（DIGEST 批收尾）
owner: ZephyrAlpha-Owner
language: zh
status: final
version: "1.0.0"
date: 2026-08-27
---

# Owner 遗留五项架构裁定书

依据：DIGEST 终局报告遗留清单五项 + 三路专项勘察（证据均带文件路径+行号，见各节）。
方法：第一性原理分解 → 风险实质识别 → 成本收益 → 裁定 → 治本方案。

---

## 裁定一：RLSP GPU 真训练（B-007 人工窗口）

### 分析过程

**第一性原理追问：B-007 到底在防什么？**
宪章字面（system_charter.md:106）：「禁止 AI 在无人工审批的情况下上线新策略模块」——防的是**未验证的模型影响真金白银**。但仓内实践已把 B-007 扩张到三个不同风险层（勘察证据①）：
1. torch 级真训练/真推理（xLSTM:8,22 / Kronos:8,22 / supply_chain_gnn:8 / rl_exec_env.py:42-44）
2. production 启用（testing 封顶口径，8 处「接线挂起待 Owner」）
3. flag 翻开（commit_queue 串行化等）

**风险实质**：GPU 训练本身只是算力消耗，不是风险；**「产物被生产消费」才是风险**。当前一刀切把「离线实验性训练」也锁进 Owner 窗口，造成两个实际损失：
- RLSP Phase 5（13 号 memo:1039-1049）设计上就是**带护栏的实验**（KL 惩罚 target_kl=0.1 防偏航 + 与 SFT 对比择优，不优则废），实验性质与「上线前置」被混为一谈；
- 勘察发现先例矛盾：LoRA SFT 已于 2026-08-09 实操 GPU 训练（13 号:1008-1033，产物 Macro-F1=0.7699 达标），而 sentiment_sft_entry.py:23 又写「大模型真训练 AI 不可自行触发」——**先例的审批留痕在仓内查不到**，规则与实践已脱节。

**替代路径评估**（勘察证据③）：SFT 产物+GGUF 回灌、关键词字典、numpy 占位、dry_run 计划全部在场且有 production 证据——被卡的**不是能力，是规则清晰度**。

### 裁定结果：**B-007 三分层（报 Owner 批准）**

| 层 | 定义 | 权限 |
|---|---|---|
| **Tier A 实验轨** | 离线训练（合成/历史数据），产物**无生产导入路径**，不落 models/ 生产目录 | **AI 可做**，四护栏：算力预算上限+审计日志+产物隔离区+禁生产 import 硬约束 |
| **Tier B 验证轨** | 产物为生产候选 | AI 做到 dry_run 计划+评估报告为止；**Owner 经 default_approval_gateway 审批**后方可真训练（审批物模板见施工方案） |
| **Tier C 上线轨** | production 启用 | 宪章 B-007 四阶段不变（回测→模拟盘→小资金→部署，每阶段人工审批） |

按此裁定：RLSP Phase 5、xLSTM/Kronos/GNN 的**实验性训练**归 Tier A 立即解禁（带护栏）；其产物要上线仍走 Tier B/C。
同时裁定：SFT 先例按 Tier B 补登审批留痕（追认合规）；集成架构.md:1218 的另一套 B-007 定义（参数计数）改名防双义。

---

## 裁定二：AUTPERM-001 归位迁移（11 目录）

### 分析过程

**第一性原理追问：目录位置产生什么价值？**
代码的物理位置不产生运行时价值——**域归属是元数据**。勘察证据：11 目录 ~440+ py 文件，agent_rbac 被 266 处/100 文件 import、escalation 被 137 处/70 文件 import；三个 re-export 壳（audit_trail/behavioral_auditor/red_blue_validator）已用 facade 模式让消费方与物理位置解耦；`src/zephyr/autonomy_perm/` 代码层不存在，但路由（blueprint_routing.yaml 8 处）、域模型、蓝图三层已预登记。

**成本收益**：物理迁移=改写 400+ import 点+每文件蓝图头+routing yaml+db_nodes+tests 镜像，在多会话并发期属高风险大规模重构，收益只是「目录好看」。且勘察发现登记表口径失真（orphan_judge 声明 ~2 实测 25、escalation 声明 ~100 实测 20、budget_enforcer 声明 ~40 实测 2）——**连迁移清单本身都是脏数据**。

### 裁定结果：**逻辑归位替代物理迁移（终裁建议；物理迁移降级为可选远期项）**

1. **立即做（AI，零风险）**：元数据归域——architecture_model/index.yaml 的 D_AUTONOMY_PERM 域节点补全 11 目录的 path 映射 + db_nodes 域映射刷新 + 登记表口径修正（~2→25 等三处）。消费方零感知。
2. **保留 facade 双轨**：三个 re-export 壳不拆（它们正是「位置无关」的工程实现）。
3. **物理迁移降级为 P3 可选远期项**：仅当未来出现「域边界强制门禁需要物理路径」的真需求时，在停机窗口+并发会话清零前提下按「壳→叶子包→access_control 最后」三阶段做，每阶段全量测试门禁。当前裁定：**不需要做**。

---

## 裁定三：313 模块运行时装配

### 分析过程

**第一性原理追问：装配的目的什么？**
让能力被运行时消费。勘察证据：boot_hooks.py 是唯一装配点（10 个硬编码消费方混合模式）；ServiceRegistry 封闭 7 键；**无装配台账、无 SOP、无验收门禁**；204 个蓝图写「消费方=运行时装配批」；signal_ashare 新模块当前**零运行时消费方**（符合预期——它们是策略/分析库，等需求驱动）。

**风险实质**：两个极端都有害——「全部猜测性接线」违反 YAGNI 且引入幻影消费方（接线即维护负担+故障面）；「永远不接」则 204 个蓝图承诺变成空头支票，模块沦为架上当品。

### 裁定结果：**三层装配架构（立即启动 Layer 1，拒绝猜测性全量接线）**

| 层 | 内容 | 时机 |
|---|---|---|
| **Layer 1 装配台账** | 新建 `docs/01_policies_and_standards/_registry/catalogs/wiring_registry.yaml`：313 模块逐一四分类（EventBus 消费者/启动实例化/纯库/DI 服务）+注入点+事件主题+验收状态，机器可读 SSoT | **立即（AI 可做，零运行时风险）** |
| **Layer 2 需求驱动装配** | 只接「有真实消费需求」的模块（日盘流程/runbook 驱动），每个带冒烟验收测试；不设模块数 KPI | 按需求逐批 |
| **Layer 3 上架超期门禁** | 新 orphan 检查：登记 90 天未接线模块自动亮红灯入审查（防架上当品） | 随 Layer 1 后一批 |

裁定：**不做 313 全量猜测性接线**；先做台账让债务可见、再让需求驱动接线、用门禁防烂尾。

---

## 裁定四：本机 WMI 环境异常

### 分析过程

勘察证据（process_pool.py:219-304, 340-434）：WMI 是 IDE Job Object 环境下 detached spawn 的**唯一逃逸通道**（ollama 拉起 auto_runtime_core.py:756、reconcile worker、6 处 daemon 全走此路）。本机 WMI 服务异常 → 全部退化为 60s 超时/RuntimeError（5 条 e2e 失败+1 个文件收集挂起的根因）。

**风险实质**：这是**机器环境故障，不是代码缺陷**。AI 重启 Windows 服务属系统级干预，越权。

### 裁定结果：**Owner 操作项 + 工程兜底两件**

1. **Owner 执行（唯一解）**：管理员 shell 跑 `winmgmt /verifyrepository` 诊断 → `Restart-Service Winmgmt` → 复跑 tests/infrastructure/test_mcp_full_lifecycle_e2e.py 验证 5 条转绿。
2. **工程兜底（AI 可做）**：boot 链加 WMI 健康预检（失败时给出「WMI 服务异常，请重启 Winmgmt」的明确降级文案而非裸 RuntimeError 堆栈）——auto_runtime_core._ensure_ollama_available 已部分具备，补齐诊断输出。

---

## 裁定五：两次 3500+ 文件误删 + ops_guard 红队 0%

### 分析过程

**证据链**：
- #ARCH-257 判例已治本：四件套+观测期 42h（333 万 allow/0 真伤）后**四治理入口已翻硬拦**（git_commit.py:459-471 等 4 处代码态实证）；pytest 定位=永久观测哨（tests/conftest.py:48-61，刻意设计）。
- 但 08-27 两起误删发生在翻硬拦**之后** → 删除仍绕过仪表化入口（#ARCH-264 O4 节同型实证：quarantine 带外裸删除零拦截零审计）。**此两起无专项取证，肇事通道未独立定凶**。
- 红队 0% 的勘察突破：红队测试**未消毒授权环境变量**（test_ops_guard_red_team.py 全文仅 L218-219 一处 pop），而 `ZEPHYR_COMMIT_GATEWAY=1` 会经 gateway 链路置位（session_worktree.py:3940）并全量子进程继承——**若大盘 pytest 继承了该变量，_is_authorized() 恒 True，全部攻击向量"授权放行"→ 恰好 0%，无需任何代码变更**。当前代码态静态读判定逻辑完好（应 100% 拦截）。

**第一性原理**：测不出来的防线等于没有防线。红队永久 0% 是最危险的状态——它让「护栏真坏了」和「测试环境脏了」无法区分。

### 裁定结果：**四件治本（排序即优先级）**

1. **P0 测试卫生修复（AI 可做，立即）**：红队+全部护栏测试加 autouse fixture delenv `ZEPHYR_COMMIT_GATEWAY`/`ZEPHYR_FORCE_DELETE`（先例模式 conftest.py:52 已指认）；修后干净环境单跑红队确认 100% 拦截恢复——**先证明防线没坏**。
2. **08-27 两起误删专项取证（AI 可做）**：复核事件窗 ops_guard_delete.jsonl/safe_write.jsonl/worktree_drift_watchdog.jsonl + governance.db，回答「肇事进程是否经四个硬拦入口之一」——经=硬拦失效 P0 新案；未经=证实未仪表化残留面，输出取证报告。
3. **授权面收窄（报 Owner 裁定）**：`ZEPHYR_COMMIT_GATEWAY` 的全量子进程继承面过大（任何子进程都成"授权方"），建议收窄为「仅 commit 执行瞬间+指定 PID 范围」或改为一次性令牌。
4. **WriteAudit PID 级写删审计（报 Owner 推进）**：#ARCH-264 O3 已规划——这是「未仪表化通道」的体系性答案，与取证结论合流后定案。

---

## 治本施工方案总表

| # | 事项 | 执行方 | 前置 | 交付物 |
|---|---|---|---|---|
| 1 | 红队测试卫生修复+复跑验证 | AI 立即 | 外来 ops_guard 重写批收敛后（其正在改同文件族） | fixture 补丁+100% 拦截证据 |
| 2 | 08-27 误删专项取证 | AI 立即 | 无 | docs/_working/reports/ 取证报告 |
| 3 | wiring_registry.yaml Layer 1（313 四分类台账） | AI 立即 | 无 | 台账注册表+首批分类 |
| 4 | AUTPERM-001 逻辑归位（元数据） | AI 立即 | 无 | index.yaml/db_nodes 映射+口径修正 |
| 5 | B-007 三分层裁定落地 | Owner 批准后 AI 执行 | **Owner 批准分层** | 裁定书入宪章附录+GATE 模板+审批物模板+SFT 追认留痕 |
| 6 | WMI 重启+验证 | **Owner** | 无 | 5 条 e2e 转绿证据 |
| 7 | 授权面收窄+WriteAudit 推进 | Owner 裁定后 AI 执行 | 取证报告（#2） | 裁定条目+施工批 |
| 8 | WMI 健康预检工程兜底 | AI 随手批 | 无 | boot 诊断文案 |

## 需 Owner 拍板的一句话清单

1. **B-007 三分层**（Tier A 实验轨解禁 RLSP/xLSTM 离线训练，Tier B/C 维持人工审批）——批或不批？
2. **AUTPERM-001** 逻辑归位替代物理迁移——认可，还是仍要物理迁移（需停机窗口）？
3. **313 装配** 拒绝猜测性全量接线、走台账+需求驱动——认可？
4. **WMI** 请重启 Winmgmt 服务并复跑验证。
5. **授权面收窄+WriteAudit** 两个治理项的推进优先级。

---

## 执行回填（2026-08-27 全部落地，Owner 四项裁定均批准）

> Owner 终裁口径：①B-007 改写为「仅实盘操作需人工审批，非实盘（回测/模拟/训练/研究/建设）全部放开」；②AUTPERM-001 逻辑归位立即做；③313 装配三层全做；④WMI 全做（Owner 重启 + AI 工程兜底）；⑤误删四件治本全做。

| 裁定 | 状态 | 交付物与证据 | 提交 |
|---|---|---|---|
| 一 B-007 | ✅ 已落地 | 规则改写「实盘审批唯一闸」+宪章 §4.2 同步+松绑清单登记（sentiment_sft_entry/xlstm/kronos/gnn 等 8 处）；RLSP Phase 5 真训练解禁 | e7b49d1002 / 13463a8a58（#ARCH-275） |
| 二 AUTPERM-001 | ✅ 已落地 | index.yaml D_AUTONOMY_PERM 补 11 目录 scope_paths 映射（消费方零感知）+db_nodes 刷新+口径勘定 11 项实测（orphan_judge 25/escalation 20/budget_enforcer 2 等）；物理迁移降 P3 可选远期 | 0b372191f8（#ARCH-276） |
| 三 313 装配 | ✅ 三层全落地 | Layer1 wiring_registry.yaml 313 条四分类（事件消费者 5/启动实例 4/纯库 304，含 registered_at/topics/defer_reason）；Layer2 首批=premarket_checker 核实已接线（boot_hooks.py:220 第 10 消费方）标 wired、其余 8 候选带证据 defer 拒猜测性接线，boot_hooks 冒烟 6 测全绿；Layer3 check_wiring_orphan.py 90 天超期门禁 12 单测全绿、当前仓 0 orphan；creation_token 3 枚登记 | aabcec6763（#ARCH-278） |
| 四 WMI | ✅ 已落地 | Owner 重启 Winmgmt 后探测 wmi-ok；AI 工程兜底=ollama 启动治本（shutil.which 当前进程解析绝对路径再传 WMI detached spawn，修 Win32_Process.Create ReturnValue=9）；验证 ollama 拉起+api/tags 200 | 959be0f54a |
| 五 误删四件 | ✅ 三件落地+两项报 Owner | 定凶=pytest 继承 ZEPHYR_COMMIT_GATEWAY/FORCE_DELETE 授权变量致红队测试 guard_rmtree('src/zephyr')「授权放行」真删（三起 ALLOWED 记录与三次误删一一对应，对照组干净环境全 BLOCKED）；治本=不变量（pytest 上下文保护区浅层递归永不真删，b4629e8172）+fixture 授权变量隔离（db417d1a21，投毒环境 87/87 全绿）+专项取证报告（c8a9b10bba）；残留报 Owner：授权面收窄（GATEWAY 子进程继承→令牌化）+WriteAudit PID 级审计 | b4629e8172 / db417d1a21 / c8a9b10bba / f91372534f（#ARCH-277） |

**收口确认**：施工方案总表 1~5、8 全部完成；6（WMI 重启）Owner 已执行并验证；7（授权面收窄+WriteAudit）为仅剩 Owner 裁定项，待拍板后开施工批。
