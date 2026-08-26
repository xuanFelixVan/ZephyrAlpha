---
ttl: task_bound
title: drift 写入方事故 O1~O7 架构裁定书（100% AI 开发共享工作区写层治理）
owner: ZephyrAlpha-Owner
language: zh
status: final
version: "1.0.0"
date: 2026-08-26
---

# drift 写入方事故 O1~O7 架构裁定书

> 上游文档：docs/_working/reports/2026-08-26-drift-writer-forensics.md（取证报告，#ARCH-264）
> 裁定人：AI-DRIFT-001（应 Owner 指令，以客观架构师身份裁定；落地施工按本文路线另外派单）
> 关联登记：#ARCH-264（本裁定回填）、#ARCH-WORKTREE-WRITE-INTEGRITY-001（母议题）、#ARCH-237（前案）、08_multi_ai_concurrency_governance.md（上位约束）、TRAE-079/084/041（规则约束）

---

## 0. 裁定方法论（第一性原理框架）

**问：在 100% AI 开发、共享工作区、多会话并发的项目里，一次"写文件"凭什么算合法？**

拆解到不可再分，一次合法的写必须同时满足三条：

1. **可归因（Attribution）**——系统必须能回答"这是谁写的"。AI 会话有心跳，但"写"这个动作不携带身份；OS 知道 PID，系统却把它丢弃了。
2. **基线新鲜（Base Freshness）**——写入方必须证明自己基于当前真值（CAS 校验），或者接受事后合并裁决（git merge）。AI 的"上下文缓存"天然滞后于磁盘，这是 100% AI 开发的结构性弱点——不能靠"AI 自觉重读"防御，只能靠机制使陈旧写"物理上不可能"或"立刻可检测"。
3. **分类治理（Classification）**——内容写（人的意图）与派生写（机械重生）不是同一物种。内容写不可逆、必须严保护；派生写幂等可重放，需要的不是保护而是**登记**（让检测器认识它）与**幂等**（重放无害）。

**本项目既有战略锚点（裁定不得违背）**：
- 终态=**单写者不变量**（08号文：提交队列 MVP，batched_auto_committer 是已裁定的"dev 第二写入者待改道"）。任何过渡方案必须与改道兼容，不得固化双写者。
- 混合文件不按文件级分类（#ARCH-BLUEPRINT-AUTOSYNC-MISCLASSIFY-001：blueprint.md 移出 auto-sync 的反例裁定）。
- 逃生通道"永久保留、显式声明、留审计"（TRAE-079/AGENTS.md）；滥用靠"计数升级阻断"（AGENTS.md L54 先例），不靠删通道。
- 派生文件官方清单当前三处并存（_AUTO_SYNC_PREFIXES 25 条 / DERIVED-FILE 门禁 2 条 / capability 注册表 is_derived 字段待启用），收敛到 is_derived 单真源是已登记技术债方向。

---

## 1. O1 裁定：reconciler 派生写合规化方向

### 分析

三个候选方向的评估：

| 方向 | 评估 |
|------|------|
| A. worker 注册 claim（心跳+claim 派生文件集） | 复用 watchdog 既有 claimed 通道，零新机制；worker 本就注册心跳（worker-\* 在册），只差 claim 快照一步；与队列 MVP 终态兼容（claim 元数据未来就是队列项元数据） |
| B. auto-sync 豁免（watchdog 对清单文件不告警） | **致盲风险**：豁免后真实流氓写这些文件也不告警。watchdog 无法区分"写的人是 worker 还是流氓"，豁免=撤防。否决 |
| C. 派生产物离库 | 违背既有裁定（workspace_governance_policy §3.3：被引用派生产物保留 tracked 作快照）；200k 行级资产索引迁移面巨大，收益不抵成本。否决 |

### 裁定结果

**采纳 A，附加两条约束；B/C 否决。**

1. **claim 登记（主）**：reconcile worker 在执行派生写前，把"本批将写的文件集"写入 `.runtime/claim_snapshots/worker-<id>.json`（网关 claim_files 既有持久化格式），worker 退出时释放。watchdog claimed 通道即刻把派生写从"未登记"转"合法 WIP"，告警洪水预计下降 ≥90%。
2. **派生写写前读新（辅）**：batched_auto_committer 写派生文件前必须声明 base（safe_write_text 或等价断言），base 陈旧则降级 warn 不硬写——防"worker 拿着 commit 时刻的旧模型回写已被他人推进的文件"。
3. **不固化双写者**：claim 登记是过渡期合规化动作；08号文队列 MVP 改道仍是终态，本条不替代、不拖延之。

---

## 2. O2 裁定：热文件 --allow-overlap 逃生通道政策

### 分析

TRAE-079 已完成一轮收紧（last-resort 化+显式声明+事后审计+常态化即 fail），文本为 immutable_core 不可直改。真正的缺口是：**"常态化使用"没有计量、没有升级触发器**——通道开着，谁也说不清今天被用了多少次、是不是成了主路径。AGENTS.md L54（WORKTREE-REQUIRED 计数≥5 升级阻断）提供了现成的执行范式。

### 裁定结果

**通道永久保留（不违 TRAE-079），补计量与升级机制：**

1. 网关对每次 `--allow-overlap` 提交落审计行（session、文件清单、是否命中热文件、时间戳），复用 `.runtime/gate_audit/` 落点。
2. **热文件专项升级**：同一 session 在滚动 24h 内热文件 allow_overlap ≥5 次，第 6 次起阻断并提示改走 claim/CAS 正道（`--claim-only` 或 safe_write_text）。非热文件不计数（digest 波次常态操作不误伤）。
3. 计量纳入每周治理报告（sla_weekly_report），Owner 可见趋势。
4. 本裁定为网关代码层演进（evolving），不改 TRAE-079 文本；规则引用挂 trae_085。

---

## 3. O3 裁定：秒级写取证能力建设（W4 定凶前置）

### 分析

| 方案 | 粒度 | 归因力 | 成本 | 结论 |
|------|------|--------|------|------|
| A. 热文件快扫（watchdog 对热文件 10s 级扫描） | 秒~十秒级 | 仍是"内容变了"，不知"谁" | 零新基建 | 立即做（P0） |
| B. WriteAudit 守护（ReadDirectoryChangesW 监视热文件目录，事件+前后 hash+事件时刻进程/句柄快照） | 亚秒级 | 近似归因（事件时刻进程清单+句柄扫描，热文件面小，成本可控） | 一个轻量守护进程，模式同 heartbeat_daemon | 立项（P1） |
| C. 编辑工具链强制 CAS 拦截层 | 写时 | 精确（写前拒） | 触及 AI 工具链底层，工程量大 | 终态方向，挂起（P2），等 P1 证据再评估 |

注：Windows 精确"谁写的"需 ETW FileIO（管理员+重量基建），B 的近似归因对热文件场景已够用——热文件写者候选集在任一时刻只有个位数进程。

### 裁定结果

**A 立即、B 立项、C 挂起：**

1. **P0（本周）**：watchdog 增热文件快扫通道——`DEFAULT_HOT_FILES ∪ design_memos/` 扫描间隔 10s（其余文件维持 60s），零新基建，先把"秒级覆写"压进可观测窗。
2. **P1（两周内）**：WriteAudit 守护 MVP——监视热文件目录，事件落 `.runtime/audit/write_audit.jsonl`（ts/path/前后 hash/事件时刻活跃进程+open-files 句柄归因）。W4 类事件下次发生即可定凶。
3. **P2（挂起）**：若 P1 证据坐实 AI 工具链路径陈旧写，再评估写时强制 CAS 拦截层（与 safe_write_text 合流）。

---

## 4. O4 裁定：quarantine 快照清除事件

### 分析（调研已闭环）

清除方=**带外裸删除**（某 AI 会话或人工经终端直删，按 `drift_*` 模式选择性清除、放过 08-15 人工存证目录，至少两次：08-25 批次一次、08-26 11:52Z 批次一次）。决定性证据：ops_guard 全审计窗口内（.2 段 11:18Z 起）针对 quarantine 的删除记录为零；safe_rmtree 留痕零命中；全仓代码无任何以 quarantine 为删除目标的机制。**这是 2026-08-14 wipe 事故裁定书已指认的体系缺陷复发：未经 ops_guard 路由的裸终端删除零拦截零审计。**

动机推断：3041 条告警/72h 的告警疲劳下，清快照=止警报噪音——消除动机比定凶追责更有价值。

### 裁定结果

1. **retention 自管**：watchdog 自管理 quarantine——30 天保留，过期自清理且每次清理写审计（谁清、清了什么、何时）；任何非 watchdog 的删除在下一扫描周期记 anomaly 告警。
2. **纳入 ops_guard 保护区**：`.runtime/quarantine` 加入受保护前缀，递归删除硬阻断（授权通道唯一化）。
3. **不定凶**：带外取证（Windows 对象访问审计 SACL/IDE 命令历史）成本远大于收益；清除动机由 O6（告警疲劳治理）根除。
4. **取证降级路径入 SOP**：快照灭失时的替代取证法（审计日志 hash 链+git 历史重建，本次已示范）写入运维手册。

---

## 5. O5 裁定：commit_queue 旧基线着落（附带项）

### 裁定结果

landing 前加 **base 新鲜度前置校验**：队列项 `base_head..HEAD` 区间若触及该项文件集 → 要求重算（rebase/重生 blob）后方可着落；与既有 skipped_dirty 防护互补成双闸（一个防"覆盖他人 WIP"，一个防"基于旧基线落盘"）。优先级 P2，随队列 MVP 批次施工。

---

## 6. O6 裁定：告警疲劳治理（3041 条/72h）

### 分析

疲劳三根源：①派生写 churn 未登记（O1 裁定覆盖，占量约九成）；②**双扫描竞态**——daemon 60s 周期扫与网关 post-commit 即时扫并发，同一签名告警重复写（实证：08:28:12/08:28:51/08:28:57 三连同一迁移）；③dedup 状态跨进程读写无互斥。

### 裁定结果

**唯一告警写者原则（Single Alerter）：**

1. `critical_warn` 只由 daemon 写；网关 post-commit 的 scan_once 改 **observe-only**（只写归因审计+状态，不写 critical_warn/clean）——从机制上消除双写竞态，一行开关级改动。
2. O1 claim 登记落地后，派生写 churn 退出告警面。
3. dedup 状态写前加进程间文件锁（复用 watchdog.lock 既有 msvcrt 锁模式）。
4. 预期效果：3041 条/72h → <20 条/72h，banner 重新成为真信号。治理副作用同步消解：清快照止噪音的动机消失（O4 联动）。

---

## 7. O7 裁定：反模式规则落点

### 分析

候选落点核查结论：trae_001/005 均 frozen+immutable_core（Owner+ADR 方可动）；trae_027 域不符；TRAE-079 族管提交期不管编辑期写层。按 trae_041 元规则：新规则默认 stability=stable、登记 rule_catalog_registry、冲突按推导链机械裁决。

### 裁定结果

**新建 trae_085_stale_base_overwrite.yaml**（本会话已随本裁定一并落盘）：

- stability: stable、safety_level: M、ai_autonomy: human_gated（对标 trae_084 模板；不定 frozen——反模式内容需随证据迭代，避免 immutable_core 修改成本）
- depends_on: TRAE-001（文件操作，frozen 上位）、TRAE-079（提交串行化）——声明为**细化补充**而非冲突条款（推导链合规）
- 四条铁律：
  1. 热文件写前读新——`safe_write_text` CAS 或 lock_files 二选一；持旧基线整文件覆写=违规
  2. 整文件 read-modify-write 脚本必须过 CAS（base 不符拒写）
  3. AI 会话全文件 Write 前必须本轮 Read——禁止凭上下文旧缓存整文件覆写（Edit 工具天然满足，Write 工具强制）
  4. 派生写必须登记——claim 快照在册或 auto-sync 清单在列（与 O1 裁定互锁）
- 登记链：rule_catalog_registry 由既有 reconciler 自动重生（派生通道）；related_arch 挂 #ARCH-264

---

## 8. 战略路线图（100% AI 开发写层治理三阶段）

| 阶段 | 内容 | 状态 |
|------|------|------|
| 本期（已落盘，本裁定） | 94号 CAS 热文件扩列（d16ea0f1）；取证报告+本裁定书；trae_085 新建；#ARCH-264 回填 | ✅ 本会话 |
| 近期（1 周，建议派单） | O6① 网关 scan_once observe-only（单行级改动，收益最大）；O4①② quarantine retention 自管+ops_guard 保护区；O2 计量审计落盘 | 待派单 |
| 中期（2~4 周，建议派单） | O1 worker claim 登记+派生写写前读新；O3 P0 热文件快扫+P1 WriteAudit MVP；O2 升级阻断上线 | 待派单 |
| 远期（随队列 MVP） | O1 改道入队（08号文既定路线）；O5 base 新鲜度双闸；O3 P2 写时 CAS 拦截评估 | 挂路线图 |

**不做清单（否定式裁定）**：不做 auto-sync 告警豁免（致盲）；不做派生产物离库（违背既有裁定）；不删 --allow-overlap 通道（TRAE-079 已裁定永久保留）；不对 quarantine 清除事件定凶追责（成本>收益，动机由 O6 根除）；不动 trae_001/005 frozen 文本（immutable_core 流程不为本案开启）。

---

## 9. 大白话总结（给 Owner）

把项目想成**一本多人合写的共享笔记本**：

1. **警报为什么响了几千次？** 有一支"机器人秘书队"（reconciler），每次任何人提交，它就自动重抄六十到两百个页面（蓝图、索引、目录册）。它干活是合法的（上头批准的），但它**从来不登记**——报警器看到的就是"无名氏在写字"，三天喊了 3041 次狼来了，九成是秘书队。
2. **谁真的盖掉了别人的字？** 两起实锤：① digest 施工队拿着三小时前的旧草稿整页誊写注册表，盖掉了别人新登记的内容（已立过案 #ARCH-237）；② "混合态"事故发生时，现场只有秘书队的长工（一个干了 78 分钟的 worker）——但按现有证据不能定罪，只能说嫌疑最大。
3. **为什么"秒级神秘人"抓不到？** 巡逻队（watchdog）每分钟巡一次，人家几秒钟写完就走，监控里根本不留影。裁定：给热门页面装"快闪摄像头"（热文件 10 秒快扫+写事件审计）。
4. **快照柜是谁清的？** 不是任何自动化机制——是有人嫌警报太吵，直接在终端里手动把存证柜清了（两次，专挑 drift_* 清，绕过了所有审计通道）。裁定：柜子以后由报警器自己管（30 天保留+清理留痕）并进保护区；不定凶——警报不吵了，就没人想清柜了。
5. **以后怎么防？** 三句话：① 秘书队以后**先登记再动笔**（claim 快照），登记了警报器就不喊了；② 所有人写热门文件前**必须先看最新版**（CAS，旧草稿直接拒写），94号 今天起已挂上这个门禁；③ 规矩写进了新规则 **trae_085**（旧缓存整页誊写=违规）。
6. **终局不变**：所有写入最终汇入统一的"提交队列"单写者模式（08号文既定路线），本裁定的每件过渡措施都与终局兼容，不欠新债。
