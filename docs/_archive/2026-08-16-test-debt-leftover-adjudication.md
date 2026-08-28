---
ttl: permanent
title: 测试债清偿遗留项调研与裁定书（#ARCH-093~097 + 关联项）
owner: ZephyrAlpha-Owner
language: zh
status: deprecated
version: "1.0.0"
date: 2026-08-16
topic: arch_review_test_debt_leftover
scope: 07_trading_decision_architecture
session: AI-TDEBT-001
---

# [A_doc] module_id: DOC-AR-20260816-tdebt-leftover | layer=doc | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] task_bound
# 测试债清偿遗留项调研与裁定书（#ARCH-093~097 + 关联项）

- 日期：2026-08-16
- 立项：AI-TDEBT-001 收尾遗留（tracker #63 反馈五条）
- 调研会话：AI-TDEBT-001（续）
- 状态：已裁定（本文即裁定书），施工同步执行

---

## 一、调研方法

第一性原理：每项遗留先问"客观事实是什么"（证据链：git 史/DB 实测/import 静态分析/探针复现），
再问"系统应该是什么"（设计意图：commit 消息/蓝图/注册表契约），最后问"100% AI 开发场景下
哪种处置的长期熵最低"（幻觉温床最小化、契约单一真源、机器可验证优先于人工记忆）。

对标框架：
- **量化机构**：WorldQuant/Numerai alpha 工厂（Idea→Research→Production 严格分层，未达标层不出厂）；
  Two Sigma 测试债风险加权（债务按"掩盖生产事故的概率"排序，不按数量排序）；
  ValidMind/MAS 模型风险管理（本项目已对标——证据链可回溯、状态机可重放）。
- **氛围编程（vibe coding）社区**：TDD 契约先行时"xfail(strict=False)=活的规格书"是公认留痕模式
  （pytest 官方文档推荐）；trunk-based + feature seam（注入缝替代 mock 面）是 AI 生成代码
  防"mock 漂移"的主流处方；mutation testing 共识：只断言"存在"的测试（smoke）价值趋零，
  本批对 4 个假阳性通过的转正即应用此共识。
- **100% AI 开发特有**：无人工 review 窗口 → 门禁与注册表是唯一的"第二双眼睛"；
  任何"靠 AI 记住不写"的约定必然腐化 → 禁令必须机器化（gate/reconciler）或显式登记在扫描得到的真源。

---

## 二、逐项证据链与裁定

### #ARCH-093 battle_map 拓扑 25→33（裁定：合法演进，机械规整 + 锚点缺口移交 Owner）

证据链：
1. PG 实测 33 环节（11 根+22 子），新增 BM-RES-08~11 各带一个 -A 子。
2. git 史：08-04 18:11~19:09 两批插入；08-04 19:14 `848139d5af` commit 消息明示
   "research_incubation +4(子环节): RES-08-A 清洗流水线/RES-09-A 知识分类体系/
   RES-10-A 模块工厂架构/RES-11-A 采集源分类调度（学习系统S0-S3）"——**有意设计演进，非误写**。
3. 施工未完成面：①sort_order 冲突（08=8/09=9/10=10/11=11 与 01=10、01-A=11 撞值，
   且与子环节 81/91/101/111 的"父=子-1"家族模式不一致）；②16 环节无锚点
   （03 全系/04 全系/05-A~C/06-A/B/07-A/08-A~11-A）；③新根无 data_flow/trigger 边接入主链。
4. name=null 为全局形态（01-07 同样 null），非新环节特有缺陷。

裁定：
- a) **合法演进确认**，不做数据清理。
- b) sort_order 机械规整：根 08→80 / 09→90 / 10→100 / 11→110（对齐既有"父=子编号-1"
  家族模式，消冲突且不发明领域语义；若学习系统 S0-S3 要求前置排序，属领域裁定，
  由 battle_map Owner 连"主链接边"一并后续调整）。
- c) 测试常量跟进 33（11 根+22 子）：三项数量断言去 xfail 转绿；
  锚点两项（each_step_has_anchor / anchor_count_at_least_25）**保留 xfail**——
  锚点回填需领域判断（挂载什么模块），属治理批进行中工作（参 f9fa80f69a 锚点挂载 batch1），
  移交 battle_map Owner，本裁定书即为交办单。

### #ARCH-094 subprocess 裸导入模式缺口（裁定：遗漏而非有意收窄，补模式）

证据链：INJECTION_PATTERNS 含 `\bsubprocess\.`（属性调用）与 `\bfrom\s+subprocess\s+import\b`，
独缺裸导入；对称面 `\bimport\s+os\b`/`\bimport\s+sys\b` 均在册——对称性证明是遗漏。
第一性：`import subprocess` 与 `import os` 危险同级（后续 `subprocess.Popen` 全敞口），
安全规则表不应存在可证明的不对称。

裁定：补 `\bimport\s+subprocess\b`（紧邻 os/sys 族），test_check_subprocess 去 xfail 转绿。
氛围编程社区对标：安全模式表的"对称性审查"应入 reconciler 年检（候选，不本批施工）。

### #ARCH-095 MCP blueprint depends_on 分歧（裁定：测试锚定过期契约，blueprint 不动）

证据链：integration/mcp 全部 21 个 .py 的 import 静态分析——仅触达 shared/* 与 integration/*
内部，**零 orchestrator（MOD-INF-039）import、零 access_control（MOD-INF-018）import**。
现声明 3 项（MOD-TASK_SYSTEM/MOD-GATE_ENGINE/b_mcp.yaml）与 import 事实一致。
测试锚定"≥4 且含 MOD-INF-039"是早期"MCP 经编排器调度"设计假设的残留，实现已解耦。

裁定：测试跟进现事实（≥3 + 必含 MOD-GATE_ENGINE + MOD-TASK_SYSTEM），两项去 xfail 转绿；
blueprint 声明层不变更（import 实证声明正确）。第一性：声明层应反映事实依赖，
测试是声明的镜像——镜像过期则换镜像，而非改事实。

### #ARCH-096 skill 内容库（裁定：出生即桩的未实现功能，转 CAND，xfail 保留作规格书）

证据链：skill-registry.yaml 全 git 史仅 1 个 commit（09a61b7a88，2026-07-29 **new file mode**，
出生即 2 条 domain 骨架）；`src/zephyr/autonomy_core/skills/**/SKILL.md` **从未在 git 存在过**
（内容库从未建设）；role 类从未登记。测试锚定的 SKILL-DOM-DBS-001/SKILL-ROL-* 是 TDD 先行契约。

裁定：非误删、非漂移，属"测试先行的未实现功能"（与 #ARCH-076~079 桩契约同族）。
- 转 CAND 登记"skill 内容库建设（registry 补条目 + SKILL.md 内容 + role 类体系）"——
  内容编写需领域知识，不属测试债清偿批。
- 5 项 xfail(strict=False) 保留——按 vibe coding 社区共识，它们是功能规格书，
  内容库建成之日即验收标准。
- inject 静默吞异常（loaded=False 无告警）已在 #ARCH-096 记录 c) 项，随 CAND 一并施工。

### #ARCH-097 patch("os.path.join") 污染 + instance 别名（裁定：存量清零 + 别名删除 + 禁令登记）

证据链：Windows 下 `os.path.join`=`ntpath.join`=`WindowsPath._flavour.join` 同一函数对象，
patch 即全进程 pathlib 污染（探针递归实证）；全仓存量仅 2 处残留
（test_budget_shutdown.py L50 + test_budget_lifecycle_e2e.py L150 漏网 instance 赋值）。
`BudgetEngine.instance` 类定义期别名不跟踪 `_instance`（Stage 4 公共化缺陷），
全仓生产零消费者（仅测试用，且测试已全转 set/has/reset_instance）。

裁定：
- 残留 2 处清零（seam/set_instance）。
- **删除 instance 别名**（L97）——坏公共化比无私有化更危险（静默错位）；
  防回归靠 DATETIME 同款静态门禁思路，但因存量=0，暂以本裁定登记为禁令载体
  （grep 可验证），门禁化列入观察（若再出现即立 gate）。
- 量化对标：Two Sigma 式"坏 seam 立即拆除"——不可测试的公共面是测试债发生器。

### 关联项 A：注册表 dup（裁定：占位版删除 + 撞号重编 #ARCH-098）

- #ARCH-STASH-ACCUMULATION-001：L6337 正式版（P1 完整裁定）与 L6747 占位版（同日同议题，
  占位使命已被正式版满足）→ 删占位版。
- #ARCH-DI-SEAM-001：07-18 静态门禁议题（L4016，scripts 10 处引用）先占编号；
  07-27 PG DIP 议题（L9702，src 7 处引用）撞号 → L9702 重编 **#ARCH-098**，
  src 7 处引用同步改（rule_engine L161 / depgraph_schema L1596 / pg_wrapper L20+L105 /
  auto_runner L154+L342+L382）。撞号教训与 #77-79/#85-92 同族：立项前 grep 最大号。

### 关联项 B：140 外来 WIP（裁定：避让 + 取证登记，不还原）

- 81 个纯 CRLF 幻影（git diff -w 零差异）+ 51 个实质内容 WIP（含 _state-machine-registry.yaml
  +66 行等）。round3 期间被某进程 stage（已 unstage）。实质 WIP 含他人工作内容，
  还原有丢失风险——**全部避让**，本裁定登记取证，归属与处置权交用户。
- 先例对照：coord-0814-gov2 的"127 CRLF 幻影"取证模式。

### 关联项 C：GATE-RULE-AUDIT banner（裁定：旧记录，无动作）

86184ba5ec（180s 修复）已在 dev（git branch --contains 实证）；banner 读取
reconcile_execution_log 最近 24h critical_warn，2026-08-15 14:46 记录随窗口滚动自然消失。
本 worktree 分支基点早于修复，merge 回 dev 自然吸收。**无故障，无动作**。

### 关联项 D：test_governance_db 8 errors（裁定：生产库耦合缺口，xfail + #ARCH-099）

证据：fixture 用 online backup 拷贝**主仓生产 governance.db**——①锁竞争
（tick_subscriber/reconciler 活跃占用）②主仓 DB schema 缺 idempotency_key 列
（schema 迁移未在主仓执行）。单跑复现，非 xdist 环境问题。
裁定：8 项 xfail(strict=False) + #ARCH-099 登记（测试架构缺口——e2e 拷贝生产库=
锁竞争+schema 漂移双耦合；治本=测试自建最小 schema fixture，与 233 下批同施工）。

### 关联项 E：剩余 233 failed 分包方案（裁定：立项下批，按域 6 包）

画像：130+ 文件 × 1-4 项，无 ≥5 大簇；形态与本批已清簇同族（API 演进/契约漂移），
无真 bug 信号。按 Two Sigma 风险加权原则排序（安全/资金路径优先）：
1. 包①安全与权限（escalation/rbac/agent_spec/skill 域 ~30 项）
2. 包②交易与资金（trading/position/pf_core/rollback 域 ~45 项）
3. 包③治理与蓝图（blueprint/governance/orchestrator 域 ~60 项）
4. 包④数据与基础设施（data/infrastructure/zephyr 域 ~40 项）
5. 包⑤自治与生命周期（autonomy/f_lifecycle/fix 域 ~35 项）
6. 包⑥工具与其他（utils/memory/skill/config 等 ~23 项）
每包独立 worktree + 独立 commit，验收标准同本批（2 轮全绿 + 假阳性转正）。

---

## 三、治本施工方案总表

| # | 项 | 动作 | 性质 |
|---|---|---|---|
| B1 | #ARCH-094 | INJECTION_PATTERNS 补 `\bimport\s+subprocess\b` + 测试去 xfail | 生产补规则 |
| B2 | #ARCH-095 | 2 测试断言跟进现事实 + 去 xfail | 测试跟进 |
| B3 | #ARCH-093 | DB sort_order 4 行重排（psycopg2 事务+回读）+ 测试常量 33 + 3 项去 xfail | 数据规整+测试跟进 |
| B4 | #ARCH-096 | CAND 登记内容库建设；xfail 保留 | 登记 |
| B5 | #ARCH-097 | 2 处残留清零 + 删 instance 别名 | 测试跟进+生产拆坏 seam |
| B6 | dup | 删 STASH 占位版；DI-SEAM L9702→#ARCH-098 + src 7 处引用 | 注册表规整 |
| B7 | gov_db | 8 项 xfail + #ARCH-099 登记 | 留痕 |
| B8 | 台账 | round3 收口 + 本裁定书索引 + 233 分包方案 | 登记 |

验收：受影响测试两轮全绿（battle_map/gov_db 等 DB 依赖项以 xfail 留痕计）+
grep 复核（subprocess 模式在册/patch 存量=0/instance 别名=0/dup=0）。

---

## 四、终态裁定补记（2026-08-16 15:20，Owner 指派本会话深度调查后裁定）

> 触发：Owner 裁定"140 外来 WIP 归属与处置 + 本 worktree merge 排期"两项归本会话调查执行。
> 调查期间事态演进：第五统筹（coord-0815-gov3）于 13:52–15:17 执行了 11 路 merge 收口 +
> 全量 worktree 退役。本节为终态取证、追认裁定与治本方案。

### 4.1 事态时间链（reflog/文件系统/进程三层实证）

| 时刻 | 事件 | 证据 |
|---|---|---|
| 13:52:06 | coord-0815-gov3 接手登记（233 六包立项建议登记在册） | f7fb6d6bf7 |
| 14:25–14:43 | merge RCAN/SENT/SIM/FIX/MON + 注册表去重 + merge ASM | reflog 逐条 |
| 14:32:47 | 存证 main-derived-premerge-20260816.patch（17 文件） | .runtime/quarantine/ |
| 14:50:11 | merge TDEBT（本裁定书所在分支，含 140 WIP 工作区） | 16c3dcf2c9 |
| 15:06:51 | merge NORTH（87f50a5e3f，冲突块三方裁决落盘） | reflog |
| ~15:10 | JOB077 merge 冲突→reset 放弃（独有仅 2 个派生自动提交） | reflog reset 行 |
| 15:12:13–40 | 退役 8 个 worktree（SIM/FIX/MON/TDEBT/NORTH/JOB077/JOB083/JOB084） | .runtime/sessions/ 触碰时序 |
| 15:14–15:16 | 退役余下 4 个（TICK/GIT/ARCH/COMP） | worktree list 终态 |
| 15:15:52 | **AI-ARCH-001 未提交工作抢救入库**（INFRA-STORE-002 + data_retention_contract v1.1.0） | 2cdbbc80a7 |
| 15:17:39 | depgraph 重建收敛收官（6508 节点/10701 边统计块同步） | 0817f77e84 |

### 4.2 关联项 B 终态裁定：140 外来 WIP = 派生活水 + CRLF 幻影，零损失闭环

**成分终判（三重证据）**：
1. 终态 127 文件（131 − 4 项已被 merge 吸收，字节一致实证）**100% 为 .md 文档**
   （blueprint/handbook/backup_inventory），无任何代码/YAML——原"51 实质 WIP"例证
   _state-machine-registry.yaml 不在终态清单（dev canonical 版在库且近期有提交史
   09a61b7a88，round3 收口 commits 已吸收）；
2. 与 dev HEAD 的 123 处内容差 = AUTO 统计块数字（depgraph 节点/边/build_status 分布）——
   coord 存证的 main-derived-premerge patch 逐 diff 实证为纯数字派生刷新（6500→6508 节点等）；
3. tracker #85 已立 SOP：数字派生物一律丢弃不提交（丢弃零损失，depgraph 可随时再生成）；
   CRLF 幻影有 coord-0814-gov2 "127 幻影"先例。

**结论**：该批文件非任何会话的业务 WIP，系 post-commit 生成器读主仓 depgraph 回写
worktree 文档 AUTO 块所致"派生活水"+ 行尾翻转幻影。coord 退役 TDEBT worktree 时随目录
删除，**未归档但零损失成立**——canonical 源 = depgraph DB，收官 commit 0817f77e84 已从
DB 重建全仓统计块，dev 现为最新真源。**裁定：闭环，无需还原、无需追责。**

**过程瑕疵（治本靶点，非追责）**：退役未对脏工作区做 bundle/patch 存证（对照
AI-RCN-001 的 .runtime/quarantine bundle 先例），"零损失"结论依赖事后取证重建。
若成分中混入真业务 WIP，删除即不可逆。

### 4.3 Merge 排期终态裁定：#ARCH-70 通道本轮职责已履行完毕

- `git branch --no-merged dev` 终态仅剩 `main`（项目主线隔离约定，合法）；
  全部 12 个 ai/* 施工分支 merged 且已删；worktree 仅剩主仓。
- JOB077 abort **追认为正确处置**：分支独有 2 commits 皆为 reconciler/integrity
  派生自动提交，dev 管道自行再生成，零信息损失。
- 遗留 = 生命周期卫生（孤儿进程/孤儿目录/陈旧 session 分支），由本会话本批执行（§4.5）。

### 4.4 治本施工方案（防"外来 WIP"悬案复发）

| # | 缺口 | 治本动作 | 性质 |
|---|---|---|---|
| Z1 | 退役脏工作区无存证 | session_worktree retire 流程强制：脏文件 >0 时先生成<br>`.runtime/quarantine/<sid>-retire-<ts>.patch`（diff 存证）再删目录；<br>成分自动三分类（派生活水/CRLF 幻影/实质）写入退役审计 | 流程补强（登记 CAND 待立项） |
| Z2 | 派生活水反复制造"假 WIP" | tracker #85 SOP 已有认知项；补机器层：retire/merge 甄别脚本<br>内置"AUTO 块数字 diff 自动判派生"分类器（本调查探针同款逻辑：<br>EOL 归一化 + dev HEAD 比对 + AUTO-END 标记段定位） | 工具化（随 Z1 同立项） |
| Z3 | 孤儿 heartbeat_daemon 制造假活性 | 本批直接执行：直杀 2 个残留 daemon + 1 个僵尸 backup.ps1<br>（13 个随退役失锚自退）；根治=daemon 启动时注册 worktree 路径，<br>watchdog 周期核对路径存活，失锚自退（登记 CAND） | 本批执行 + CAND 登记 |
| Z4 | 孤儿 worktree 目录（未注册） | 本批直接执行：删 5 个（DC2-01 陈旧快照/DC2-09/DOCS-001/<br>WDOG-001/WRN-001 空壳）；backup 计划任务实证锚主仓路径不受影响 | 本批执行 |
| Z5 | session/* 陈旧分支（baostock-harden/ifind-retire，已 merged） | 保留候选：属数据加固历史分支，删除权交 Owner/统筹<br>（非本裁定范围，tracker 登记） | 登记 |

### 4.5 本批执行记录（2026-08-16，本会话直执）

- 孤儿进程：取证时 15 个 heartbeat_daemon 在跑（worktree/分支已无对象）；退役潮后 13 个
  失锚自退（实证进程列表消失），本批直杀 2 个两天残留（ifind-retire pid 11592 /
  baostock-harden pid 25424）+ 1 个僵尸 backup.ps1（pid 38792，脚本文件已随 DOCS-001
  空壳化丢失，进程空转两天）；
  保留：watchdog（主仓锚定）/scheduler/tick_subscriber/ch_health_probe/panel/wrapper-inject
  + 6 个 TD2 新批 daemon。
- 删孤儿目录 5 个（.worktrees/ 下未注册：AI-DC2-01/-09/AI-DOCS-001/AI-WDOG-001/AI-WRN-001）。
- 233 下批交接书落盘：docs/_working/reports/233_test_debt_batch_handover_20260816.md
  （Owner 转发统筹派单；与本批卫生执行零文件交集，可并发）。
- 台账策略：本批全链以本节 §4 为登记真源；tracker 并表移交统筹（执行窗口 coord 正活跃
  登记 233 派单，避让 tracker 并发写防 lost-update 第四实证）。
- 收尾实证：本批落笔时 coord 已自建 6 个 TD2 worktree（15:25:00–38，SEC/TRD/GOV/DATA/
  AUTO/UTIL 全并发，5a3ac40477 派单登记在册）——233 立项已由用户裁定直通，交接书作为
  施工规范备查件随批生效。
