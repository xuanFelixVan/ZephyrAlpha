---
ttl: task_bound
---

# AI-NIGHT-001 夜班批·Owner 裁定事项 AI 调研裁定书（第十统筹，2026-08-20）

> 授权：Owner 2026-08-19 深夜补充裁定②（#61/#62/#64/#14/#83 授权 AI 调研裁定）+③通用裁定条款（§四-2 方法论：详细调研+第一性原理+长远战略+专业机构/量化社区实践参照）。
> 调研底稿：三路调研子代理行级实证报告（2026-08-20），关键证据已并入各节。

---

## #61 paths.py GATES_DIR 孤儿定义致 FLE gates 静默空转

### 调研实证（关键更正：底稿前提已过期）
1. paths.py:169 当前值已是正确的 `gov_enforcement/rule_enforcement`——**2026-08-17 AI-AUDIT11（6f1c2d71b4）已治本修复**，tracker 底稿（2026-08-15）所述孤儿值已不存在。孤儿化时间线：08622cd0ce（07-01 当时正确）→4f55ff57a4（07-13 目录搬迁未跟进，孤儿化起点）→1465ff020f（08-15 实证登记 #61）→6f1c2d71b4（08-17 治本）。
2. **运行时影响实证为零门禁变化**：真源 _registry.yaml 91 条 gate 中 `fle_self_defense` 条目=0（PyYAML 实证），dispatch 由"registry 不存在→{}"变为"加载 91 条→0 命中→{}"。空转真正根因已下沉为"注册表无 FLE 条目"（2026-05-19 7ed644a288 起丢失 3 个月）。
3. 消费链全链 fail-open（registry 缺失→{}/YAML 异常→{}/gate 异常→True），scheduler.py:627 仅 anomaly 进入 Act 阶段时触发，非 30s poll 路径。
4. **当前唯一敞口**：tests/io/test_io_paths.py:121 仍断言 governance 旧值——**当前存量 FAILED**（AI-AUDIT11 修复时测试同步漏网，与 test_shared_core.py:288 互相矛盾）。
5. 附带发现：`scripts/scaffold.py:90` 同一孤儿值的活拷贝（tooling 侧，exists() 看守护不到）；FLE 激活另有类名推导 bug（gate_id 连字符 vs 类名推导，48 个 gate 文件 0/48 可解析）——激活等于新功能上线。

### 裁定
**采纳方案 B（最小收尾+真源收敛顺手包），FLE 激活单独立项。**
1. 对齐 tests/io/test_io_paths.py:117-121 为 gov_enforcement 现状+exists()（消除存量 FAILED）。
2. 修正 scripts/scaffold.py:90-92 孤儿拷贝指向 gov_enforcement。
3. gate_engine.py:111 GATES_DIR 改 re-export paths.GATES_DIR（层级合法：gate_engine 已 import zephyr.shared.*），三处拷贝收敛为一处。
4. FLE 48 gates 激活（补注册条目+类名推导修复+逐 gate 契约评审）属生产行为实质变更，登记 CAND 专项，不夹带本批。

依据：fail-open vs fail-visible 原则——危害不是空转（调度安全网设计选择）而是"以为有防护实际没有"的认知静默；致病组织动作=让漂移在注册/测试时暴露（exists() 断言+测试对齐+真源单一定义），非运行时改 fail-closed。

### 落地状态
✅ 2026-08-20 落地（本批）：三项代码/测试对齐+回归测试+CAND 登记。复跑影响域全绿。

---

## #64 session_worktree._trusted_git_env 隔离 assert 漂移

### 调研实证（关键更正：assert 从未存在，非"演进中被移除"）
1. 双形态 `git log --all -S` 实证：该 assert **从未存在于任何已提交版本**；函数出生（1bf1ffc846，07-19）即纯副本语义。测试 4eff7f2769（08-05）超前编码了从未实现的契约，从入库起即失败，08-15 加 xfail(strict=False)。tracker"被移除"表述不实——实质=测试-实现单向漂移，修复定性从"补回"变为"新增"。
2. 误炸面实证：5 处调用点全为 git 子进程，无 Python 子进程经 fast-path env 派生→嵌套污染路径当前不存在；全仓进程级写入点=0。但部分调用点外层有 except Exception 宽捕（L6972-6978）——assert 在部分路径被吞成 warn，语义分裂；且 `python -O` 剥离 assert，安全语义不可靠。
3. 真实不变量两层：①"不污染主进程"由副本语义结构性保证（6 绿测试已覆盖）；②"检测第三方污染"是对进程全局状态的外部监控，非函数自身计算不变量。

### 裁定
**采纳方案 B（warn-only 检测+测试改写摘 xfail）；不建议新增 assert。**
1. _trusted_git_env 检测 `_FAST_PATH_ENV in os.environ` 时 logger.warning（fail-visible 不 fail-closed），仍返回安全副本。
2. xfail 用例改写为 caplog 断言 warn 后摘 xfail；docstring/测试 reason 修正"被移除"不实表述为"从未实现"。
3. tracker #64 表述同步修正。

依据：防御性 assert 适用边界=函数自身计算必须满足的内部不变量；os.environ 是共享可变全局状态，对其 assert 等于把环境配置错误升格为运行时崩溃且崩溃语义被沿途宽捕稀释（最差组合）。监控信号要响亮、执行路径要宽容（仓内 ARCH-036 同款先例）。

### 落地状态
✅ 2026-08-20 落地（本批）：warn-only 实现+测试改写摘 xfail+回归全绿。

---

## #14 DSR 双实现未统编（阈值 0.5 vs 0.95），dsr_value 语义分裂

### 调研实证
1. 两实现同属 Bailey & López de Prado (2014) DSR 公式族（E[max] 两个近似式均论文合法、大 N 渐近等价）；核心分裂=①输入接口（metrics.py 预算 Sharpe+矩 vs MOD-SIM-024 原始序列）②判定阈值（0.5 is_overfitting vs 0.95 is_significant）③metrics.py 的 Cornish-Fisher 预调整为非论文步骤且年化 Sharpe 直接配 n_samples 算 σ 量纲不严格。MOD-SIM-024 严格贴合原论文。
2. 潜伏态实证：DecisionGate DSR 判定器默认关闭（decision_gate.py:103），experiment_registry 五处 dsr_value 全 null——一旦启用/回填，0.5 口径值流入 0.95 消费方即系统性误判（0.5~0.95 区间策略两侧判定相反）。
3. **独立第二病灶**：experiment_registry.yaml:63 与 62 号 memo 的 dsr_value 文档"（>1.0 显著）/FAIL if <1.0"——两实现 DSR 均 ∈(0,1)，>1.0 永不成立，按此实现的任何 gate 100% fail。
4. 行业实践：DSR>0.95=5% 显著性放行线（类比 p<0.05，社区惯例）；DSR<0.50=运气中值否决线。分级语义是标准做法非互斥口径。
5. 测试破坏面评估：0.5 侧测试全在极端区（DSR≈1/≈0），阈值统一机械破坏面极小；decision_gate 为调用方注入阈值不受影响。

### 裁定
**采纳方案 A（实现统编到 MOD-SIM-024 内核+分级阈值 SSoT+文档修正）。**
1. metrics.calculate_dsr 改为论文口径公式（弃 Cornish-Fisher 预调整）：V[SR]=(1−γ·SR+(κ−1)/4·SR²)/(n−1)，E[max] 用 MOD-SIM-024 同款 Euler-Maclaurin 近似，DSR=Φ(SR/√V−E[max])；保留 `is_overfitting` 键，语义=`dsr < DSR_OVERFITTING_FLOOR(0.5)`（运气线否决，负向语义与 0.5 天然匹配）。
2. 阈值常量 SSoT：deflated_sharpe_calculator.py 导出 `DSR_SIGNIFICANCE_THRESHOLD=0.95`/`DSR_OVERFITTING_FLOOR=0.5`，metrics.py 引用（decision_gate 保持调用方注入不动）。
3. 文档修正：experiment_registry.yaml:63 dsr_value 描述改"∈(0,1)，≥0.95 显著（<0.5 无超出运气的证据）"；62 号 memo 两处 ">1.0" 同步勘正。

依据：López de Prado 原论文与量化社区（mlfinlab/metricgate）分级实践一致；统编消公式漂移风险；接口不变测试不破；文档错误不修则 dsr_value 回填之日即全量 fail 之时。

### 落地状态
✅ 2026-08-20 落地（本批）：统编+常量 SSoT+文档修正+影响域复跑全绿。

---

## #62 drift_events 表双库分裂+Dashboard 读方+测试三方漂移

### 调研实证（新发现超出底稿：写入链全断+读方读死数据）
1. **写入方 A（drift_engine→governance.db）静默全灭**：生产 governance.db 现存 drift_events 为历史 schema A（无 timestamp 列），drift_engine INSERT 按 schema C 必抛 OperationalError，被 :619-620 宽捕逐条吞掉——生产 written=0 无任何告警；库内 386 行遗产数据最近写入=2026-05-26。测试全部显式传 tmp db_path（自建 schema C）完美掩盖。
2. **写入方 B（gate_persistence→drift_events.db）是空壳**：全篇无 INSERT INTO drift_events（INSERT 仅到 scan_results/gate_decisions）——底稿"双写入方"实为"一写一空壳"。
3. 读方 4 处 3 种 schema 假设：Dashboard 读 governance.db schema A 语义（created_at/state）现状自洽但读的是 5-26 前死数据；trend_analyzer 迁第三库 drift_audit.db（物理不存在，裁定#18 F5）；correlation_engine 硬编码 governance.db 查 scan_id/drift_dimension 列（schema A 无此两列，无捕获必炸，当前无生产调用方才未爆）；tamper_proof_audit ORDER BY timestamp（schema C 假设，异常被吞返回空）。
4. 物理库实证：governance.db 83MB/386 行（2026-05-26）；drift_events.db 28KB/0 行；drift_audit.db 不存在；data/governance.db 0 字节空壳。
5. test_ba_dashboard 2 用例自出生（2026-06-21 a5c1a81787）即红从未绿（建 drift_audit/drift_events.db vs Dashboard 真读 governance.db）；仓内同族裁定先例（test_correlation_engine.py:82-83"生产合并进 governance.db"）。

### 裁定
**唯一真源=governance.db（方案 1 方向），本批先落止血对齐（方案 3 代码层），历史数据搬移/schema 归并/trend_analyzer 回迁留 Owner 窗口。**
1. 【本批落地】drift_engine INSERT 对齐生产 schema A（修静默零写入——任何终局方案下都不浪费的止血）。
2. 【本批落地】test_ba_dashboard 2 用例改 tmp governance.db 布局（治 HEAD 存量红）。
3. 【本批落地】correlation_engine.py:48-55 硬编码改 DB_PATH SSoT（消必炸点）。
4. 【本批落地】gate_persistence 空壳 DDL 头部注释标注（防误导，不改行为）。
5. 【Owner 窗口登记】①governance.db drift_events schema 归并（ALTER 补 schema C 列或 386 行遗产迁移）=DB DDL/数据写操作；②trend_analyzer 回迁（涉推翻裁定#18 F5，列子裁定项随统一批）；③data/governance.db 0 字节空壳清理；④Dashboard 死数据展示风险提示（展示层标"数据截至"）。

依据：仓内 SSoT 机制（paths.py:154-164 DB_PATH 仓级共享治理库唯一真源+worktree 锚定）与同族先例（test_correlation_engine.py:82-83）均围绕 governance.db；工程实践 sqlite 单库单写者+WAL 优于多库分散（blueprint §17.2 GAP-003 同口径）。止血两动作在任何终局方案下不浪费。

### 落地状态
✅ 代码对齐 2026-08-20 落地（本批）+回归全绿；Owner 窗口四项已登记 tracker。

---

## #83 AGENTS.md 速查表 18 注册表口径回填

### 调研实证（关键发现：大头已落地，tracker 状态陈旧）
1. 00646958 只代收 ROOR+62 号两文件；其 AGENTS.md 同源改动**已于 db26d6534b（2026-08-15 21:10）经 [ARCH-APPROVAL] Owner 通道落地**（4 新表行+data_asset 171→199+#41 动态化全部在 HEAD）。tracker #83/#41"⏳ 等 Owner 审批"=陈旧未翻转。
2. 剩余增量=表头"14 表体系"残留+落地后 5 天新一轮漂移：2026-08-20 逐文件实测 **15/18 行漂移**（factor 111→140/strategy 59→146/risk_limit 62→111/data_asset 199→206 等，主因 29 号 546 条入库+90 号组批，均在 db26d6534b 之后）；实测合计 1268 条。
3. patch 存证：`.runtime/pkgZ/agents_speedtable_18reg_refresh.patch`（16+/16-，仅触速查区，REG-ATH-001 行不动守 #89 裁定），`git apply --check`=exit 0；落地方案 `.runtime/pkgZ/ai00_pkgZ_83_speedtable_landing_plan_20260820.md`。

### 裁定
**①patch 存证方案批准，物理落地留 Owner 在场窗口（PROTECTED-PATHS 硬阻断不越权）；②长效裁定=动态化（不再人工周期刷新）。**
1. Owner 回来后一键批准：git apply --check→git apply→GitCommitGateway commit（message 带 [ARCH-APPROVAL:ARCH-BREG-001]，同 db26d6534b 先例）→同批翻转 tracker #83/#41。ROOR 18 个 entry_count 同步漂移建议同批刷新。
2. 长效：手写数字 5 天漂移 15/18 行已证伪人工维护——改走动态化，最优=GATE-REGISTRY-SYNC reconciler 自动重写速查区数字（post-commit 机制已存在，与"数字派生物不入 git"原则一致），其次=行级改 #41 同款动态表述。登记 CAND 承接。
3. tracker #83 状态本批先翻转为"实证大半已落地（db26d6534b）+剩余增量 patch 存证待 Owner 一键"。

依据：当前速查表数字是"错的"而非"过时"，错误口径比缺失更有害（先止血）；但 5 天 15 行漂移证伪人工维护（后动态化治本）。

### 落地状态
✅ patch+落地方案存证（.runtime/pkgZ/）；tracker 状态翻转（本批）；物理 apply 待 Owner 一键；动态化 CAND 登记。

---

## 通用裁定条款执行声明

本批五项裁定均按 §四-2 方法论执行：tracker 登记原文+代码实证+git 历史三路调研（其中 #61/#64/#83 三项实证推翻/更正了底稿前提——#61 修复已在库、#64 assert 从未存在、#83 大头已落地）；裁定方向以第一性原理（fail-open vs fail-visible、SSoT 单一定义、测试即文档）+长远战略（防第三次漂移、防回填日全量 fail、防人工维护证伪）+专业机构/量化社区实践（López de Prado DSR 分级惯例、Google 防御性 assert 边界、sqlite 单写者 WAL）为依据。执行中途无新增未裁定事项遗留。
