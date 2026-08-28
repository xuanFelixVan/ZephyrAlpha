---
ttl: task_bound
---

# B-007 遗留五项裁定书（2026-08-28）

> 裁定人：架构治理会话（Owner 全权委托）｜方法：三路并行取证（PG 活库/代码行级/文档真源）+ 第一性原理分析
> 适用范围：B-007 rollout 收官遗留五议题（design 节点裁定 / winmgmt / 交易会话冒烟 / 锚点节点治本 / 补充批）
> 关联文档：2026-08-26-b007-rollout-plan.md（§4.7/§9）、B007_B1~B6_report.md、ARCH-MM-002（architecture_issue_registry.yaml L1851-1889）、maturity_vocabulary.yaml v2.0.0

---

## 0. 总裁定矩阵

| 议题 | 裁定 | 状态 |
|---|---|---|
| B winmgmt | 环境事故非架构问题；重启即恢复 | ✅ 已闭环（33/33 复绿） |
| A 7 个 design 节点 | **非生命周期判断题，是 ARCH-MM-002 字段真值错误**——7/7 design_maturity 修正 production；5 节点 build_status 随补充批两步法转正 | ✅ 修正已执行（7/7） |
| D 锚点节点 | 真凶非重生成器：**sync UPDATE 无条件回写 + ghost 清理无豁免**；三处修复已落地实证 | ✅ 治本已施工 |
| E 补充批 | 范围 66 节点（滞留 5 + 在飞 52 + design 转正 5 + INFRA-DB 4）；复用六批工具链 | 📋 方案就绪待执行窗 |
| C 交易会话冒烟 | 唯一 Owner 物理窗口项；SOP 见 §5 | 📋 待 Owner 窗口 |

---

## 1. 议题 B：winmgmt 瘫痪（已闭环）

**机理**：8/26 23:15 起 WMI/CIM 全瘫（Get-CimInstance 超时、Win32_Process.Create ReturnValue=9、CreateProcess WinError 5）——Windows Management Instrumentation 服务级故障，非项目代码问题。期间 sweep 验证以 Task Scheduler 分离进程 + WMI shim（platform.win32_ver 规避）绕开，验证有效性未受损（批 2-6 全部门禁在绕开态下独立完成且互相印证）。

**处置**：UAC 提升重启 winmgmt 服务 → WMI/CIM 恢复 → `test_mcp_full_lifecycle_e2e.py` **33/33 全绿（390s）**——含基线红 5 项（CreateProcess/Win32_Process 族）全部复绿。B-007 各批 sweep 台账中该族"winmgmt 环境结构性基线项"全部销账。

**裁定**：闭环。无代码改动。遗留建议：winmgmt 故障根因（仓储损坏 or 系统更新残留）属 OS 运维范畴，若复发执行 `winmgmt /verifyrepository`，项目侧不再挂账。

---

## 2. 议题 A：7 个 design 节点裁定（已执行）

### 2.1 事实勘定（三路取证交叉验证）

计划 §4.7 原文 7 节点，PG 实况分两组：

| 组 | 节点 | 取证要点 |
|---|---|---|
| 待裁定 5（testing） | intelligence/model_routing/、ml_train/{ai_operator, training_dataset_manager, training_pipeline}/、tests/ml_train/test_density_quantile_trainer.py | **全部有实质完整实现**（502 行级联路由/166 行操作员/173 行数据集管理/200 行训练编排/134 行测试），测试可收集（21/9/9/7/12 项），文件头全标 `[MATURITY] production` |
| 异常转正 2（production） | data/connectors/（MOD-L00-005）、data/normalizers/（MOD-L00-006） | 同样实质实现（220/544 行，10/14+ 测试），但 2026-08-21 备份实证转态前=planned，**planned→production 跨 4 态且不在 B-007 任何清单/快照/日志——库外通道证据链断** |

### 2.2 第一性原理分析

**§4.7 的前提不成立**。§4.7 建议"维持 testing"的理由是"蓝图/目录粒度 design 节点（非物理文件）"——但取证证实 7 节点全部有物理代码。标签与实况脱节。

**ARCH-MM-002 真值表是唯一判据**（architecture_issue_registry.yaml L1851-1889 + maturity_vocabulary.yaml v2.0.0）：
> design_maturity 只管"纸面 vs 物理"：**design=仅有蓝图无代码文件；production=有代码文件**，不区分测试覆盖（测试覆盖由 build_status 表达）。

按此真值表，7 节点的 design_maturity=design **全部是字段值错误**（标注滞后于物理实现落地），不是"待权衡的生命周期判断"。文件头 `[MATURITY] production`（ARCH-MM-002 钦定 SSoT）与库字段冲突时，以头为真——库字段应跟进。test_density_quantile_trainer.py 是 A_test 简化头（无 MATURITY 行属规格），但物理文件存在+12 用例可收集，design 标注同样直接违反真值表。

**关于"接线未完成"的潜在疑虑**（model_routing [CONSUMERS] 自注"待统筹接线"）：B-007 计划 §10.3 明确"运行时接线不在本计划范围；production 转态 ≠ 功能翻开"。design_maturity/build_status 表达的是**存在性与验证度**，接线属运行时装配批，不构成本裁定阻断项。

**关于异常转正 2 节点**：通道异常（非 B-007 机制、无留痕），但**终态正确**（实质实现+测试+同 bp 文件节点群 14/11 件已 production/generated）。取证亦排除生成器通道（全景 §12.6 reconciliation 对 design 节点只写 planned/stable）。回滚到 planned 再重走流程只会制造新的语义错误（把有代码的节点标成无代码）——**追认终态、修正字段、留痕归因**是唯一不自相矛盾的处置。

### 2.3 裁定结果

1. **7/7 design_maturity 修正为 production**——已执行（走 apply_depgraph.py `--transition-design-maturity` 官方通道，ARCH-MM-002 header 门禁全部直过无需 force，修正后 regen 复核未打回；备份 architecture_20260827_171037.json）。
2. **5 个 testing 节点 build_status 随补充批两步法转正**（testing→stable→production，复用批 1-6 工具链；mechanical 打回风险已排除——realization_detection 只动 planned、_SQL_CONVERT_DESIGN_NODE 保留 production、全景生成器只读）。
3. **2 个异常转正节点追认有效**，不回滚；库外通道（planned→production 无留痕写入者）列为治理悬案登记 ARCH 注册表，由后续审计循环排查（嫌疑面：在飞会话直接 SQL/未走工具的旧版脚本）。
4. 由此，"design_maturity=design 待裁定"事项**永久清零**——剩余 design 节点全库均为"真·无代码"规划件，各安其位。

---

## 3. 议题 D：锚点节点治本（已施工实证）

### 3.1 机理翻案（批 5/6 归因错位纠正）

批次报告把两个现象记在"重生成器"头上，行级取证证明**生成器是无辜的**：

**现象 1（4 个 ARCH-052 聚合节点 6903808~11 production→stable 翻转，两度复现）**
- 生成器快照（L3597-3603）与 DELETE（L3640-3646）对 4 聚合类型**双向排除**（裁定#218/ARCH-052，git -G 实证排除链 2026-07-01 至今完整）；node_id 跨重生成稳定（若 DELETE+INSERT 必重排）——生成器零写入。
- **真凶**：`sync_yaml_to_depgraph.py::sync_aggregate_nodes` **UPDATE 分支 L1784 `build_status='stable'` 无条件回写**；触发链=post-commit **GATE-YAML-SYNC reconciler**（任何触及 registry YAML 的 commit 后全量 sync，失败重试队列使任意后续 commit 补跑）。批 5 的"registry edit 187 在飞提交"、批 6 的"23:35 外部 regen"实为同一 reconciler 链的伴随现象。

**现象 2（4 个 INFRA-DB 锚点节点反复移除）**
- 生成器 DELETE 排除 'database' 从未被破坏（排除链完整）。
- **真凶**：`apply_depgraph.py::cmd_cleanup_orphan_nodes`（L2438-2496）对 `#` 锚点 path 裸 `exists()` → 永假 → 判幽灵删除；`diagnose_depgraph.py` L76 ORPHAN_EXEMPT_TYPES 无 database/聚合类型（计数侧同病，且 cleanup 删除面比 diagnose 计数面更宽——任何 1 个真幽灵触发清理，锚点陪葬）。触发链=**GATE-GHOST reconciler**（删文件 commit 后自动清理）。sync_database_nodes 的 UPSERT 又使其"回库"——形成振荡。

### 3.2 治本修复（3 文件 +18/-5，已实证）

| 修复 | 位置 | 改法 |
|---|---|---|
| 1. sync UPDATE 不降级 | sync_yaml_to_depgraph.py（sync_aggregate_nodes + sync_database_nodes） | UPDATE 的 SET 剔除 build_status（保留现值）；INSERT 保持 'stable' |
| 2. 幽灵判定 `#` 剥离 | apply_depgraph.py cmd_cleanup_orphan_nodes | `path.split('#')[0]` 真源文件存在→豁免；真源不存在→仍判幽灵（语义保留） |
| 3. 豁免口径对齐 | diagnose_depgraph.py ORPHAN_EXEMPT_TYPES + ghost 判定 | 补 database+4 聚合类型（对齐生成器 DELETE 排除口径）+ 同款 `#` 剥离 |

**实证**：相关测试 54/54 全绿；全量 sync 后 4 聚合节点 production 不再翻回；cleanup dry-run 旧逻辑判 4 幽灵（恰为 INFRA-DB 锚点）新逻辑 0、负面对照（假锚点）仍判幽灵；4 个 INFRA-DB 节点已经 sync 回库（id 10827416~19，stable）；ruff 零新增。改动留工作树交 Owner 统一提交。

**未采纳项**：STATUS-PRESERVE 白名单扩聚合类型（批 6 L-2 原建议）——单独用无效（翻转不在生成器内发生），纠正该预期；DB 触发器硬守作为可选加固层暂不施工（收益/复杂度不划算，sync 修复后风险已收敛）。

### 3.4 补充批实战新确诊两缺口与修复（2026-08-28 晨补记）

补充批执行中一次在飞会话外部全量 regen 暴露议题 D 未覆盖的**生成器通道**缺口（7 节点被删后已按 by-path 纪律恢复并留痕）：

**缺口 4**：目录粒度 blueprint 节点 dm=production 后跌出三重保护网——原存活机制=DELETE 谓词的 `design_maturity != 'design'` 豁免（design 族身份），§2.3 的 dm 修正（本身正确）使其失去豁免，而它们又不在 database/聚合豁免清单、不属扫描产物。**修复**：generate_project_depgraph.py 主 DELETE 谓词补 `AND NOT (node_type='blueprint' AND granularity='directory')`（+3 行含注释）——与裁定 #189"生成器不得创建"对称"不得删除"；快照扩条件方案经取证否决（design 族存活机制本来就是 DELETE 豁免而非快照恢复，扩快照会污染 design_state 语义）；边侧 6385 条边全 dep_maturity='design' 已被既有谓词保护无需动。

**缺口 5**：test_density_quantile_trainer.py 文件头 `[BLUEPRINT] ML-DENSITY-001` 不匹配 DB 格式正则（`^MOD-` 等），被生成器 Phase 2.2 永久过滤不回库。**修复**：头改 `MOD-ML-DENSITY`（与源件及 blueprint_links 在册一致）；全仓另 19 处 `ML-DENSITY-001` 命中系 model_id 命名空间不同真源，不触碰。

**验证**：ruff 零新增+生成器/sync 测试 41 绿；**两轮全量 regen 实战**——7 节点 id 稳定存活 production、4 聚合+4 INFRA-DB 全保持、density 合规回库、92 目录 blueprint 节点全在库、第二轮幂等零振荡；全库 7,796 节点与 regen 前完全一致。

**教训归档（§6.2 推论）**：议题 A 的 dm 修正触发了缺口 4 的暴露——**任何字段语义修正后必须立即跑一遍全量重生成实战**，"修正正确"≠"保护网完整"。这正是 §6.2"不变量全通道布防"的又一次实证：dm 字段本身也是一条保护条件的输入。

### 3.3 根因一句话

**#218/ARCH-052 的豁免清单只在生成器一处维护；post-commit reconciler 链（GATE-YAML-SYNC 的 sync、GATE-GHOST 的 ghost 清理）各自持有过时的、无豁免的写入口径。** P0 确立的"机械推导封顶 stable，production 唯人工 transition"不变量当时只罩住了"重生成"一条通道，本次把它扩展到 sync 与 ghost 清理两条漏守通道。剩余理论风险面：未来新增第四条机械写入通道时须遵循同一不变量（已写入 §6 战略节作为常驻原则）。

---

## 4. 议题 E：补充批施工方案（66 节点）

### 4.1 范围（PG 实况对账，2026-08-28 时点）

testing 31 + stable 31 = 62，加 INFRA-DB 回库 4 = **66**：

| 组 | 数量 | 构成 |
|---|---:|---|
| 批 1 滞留 | 5 | scripts/ch×2 + scripts/ml×1（testing，无推断测试）+ news_taxonomy + research_rating（stable，有测试） |
| design 转正 | 5 | §2.3-2（design_maturity 已修正，随本批两步法） |
| 在飞新落地 | 52 | 8 路径簇：feedback_loop 6 / system_telemetry 6 / integration 8 / orchestrator 6 / security 8（含 llm_defense）/ signal_quality 8 / intelligence 2 / simulation 2 + 散件 6；src/scripts 件 stable、tests/ 镜像件 testing |
| INFRA-DB 锚点 | 4 | sync 回库 stable（§3.2），转 production |

### 4.2 测试覆盖空洞 11 件处置（不阻断）

- 4 个 design 目录节点：inferred_tests 启发式不适用（目录粒度）——门禁一用同 bp/同目录物理文件的测试并集（test_cascade_orchestrator 21 / test_ai_operator 9 / test_training_dataset_manager 9 / test_training_pipeline 7）
- 3 个批 1 滞留 scripts + 2 个在飞 governance scripts：scripts 类节点按批 1-6 先例由 sweep scripts 专线（test_all_scripts）兜底
- 2 个 __init__.py：包级测试兜底（批 1-6 同例，§1.2 "未推断出测试由 sweep 兜底不单独阻断"）

### 4.3 执行序列（复用六批工具链，单批一次走完）

1. 清单冻结 + node_id 重锚定（`_b007_remap_live_ids_b5.py` 改 N=supp，带单向容忍护栏；既有 supp_* 清单 id 已失效作废）+ 批前快照 + 显式 PG 备份
2. 门禁一：inferred_tests 并集 + design 4 节点同 bp 测试并入，串行 pytest 全绿
3. 门禁二：全量 sweep 零新增红（winmgmt 已恢复，可撤 WMI shim 也可保留防御；bad 簇处置口径同六批）
4. 两步法转态：36 testing→stable→production + 30 stable→production（逐节点带 ARCH-056；**注意转态工具每次触发后台 regen 互斥串行，批量执行时预留 regen 冷却**）
5. 批后核验 by-path（production=66、残留 0）+ align_all + 重生成抗性 + 补验 4 聚合节点不翻回（治本修复回归）
6. tracker 登记 B007-补充批行 + 六批观察窗翻 ✅（届时批 4-6 窗已满）

**规模评估**：66 节点，约为批 4（183）的 1/3——单批一次走完，无需再拆。

---

## 5. 议题 C：交易会话冒烟 SOP（Owner 窗口唯一保留项）

不阻断任何裁定与补充批。执行窗口：非交易时段 + XtMiniQmt 模拟终端已登录。

```powershell
# 1. 登录 XtMiniQmt 模拟终端（E:\xtquant，.env.qmt 已在册）
# 2. 执行冒烟
python scripts/ex_core/smoke_test_trading_session.py   # 预期 RC 0（批4 未登录时 RC 1 正确快速失败）
# 3. 登记：把 RC/输出摘要写入 construction_progress_tracker.md 批4 行（追记）+ B007_B4_report.md L-1 销账
```

失败处置：RC≠0 且非连接类错误 → 挂 ARCH 注册表排查；连接类错误 → 检查终端登录态与 .env.qmt 配置后重跑。

---

## 6. 战略节：100% AI 开发下的架构治理第一性原理

本次五议题共享同一深层结构，对 100% AI 开发项目有三条常驻教训：

**6.1 真源必须机器可判定。** ARCH-MM-002 的成功（design_maturity=文件存在性）正在于它把语义判断换成了客观事实——AI 不会判错"文件是否存在"，但会判错"这个模块是否够成熟"。议题 A 的 7 个节点标注滞后，本质是物理实现先行、元数据未跟——**元数据不是认知的载体，而是事实的投影**；凡需要"判断"才能维护的字段，在 AI 开发流下必然滞后或漂移。后续新增治理字段应过同一道筛：能否用一条 SQL/一次文件检查机械验证？不能，就不进库。

**6.2 不变量必须全通道布防，且归因必须落到通道级。** P0 的"production 唯人工 transition"不变量只布防了重生成器一条通道，sync 与 ghost 清理两条漏守——而批 5/6 的 AI 会话把 sync 干的事记在 regen 头上（归因错位）。AI 会话的因果链是文本推断而非执行追踪，**每条自动写入通道都必须自带留痕（谁触发/谁写入/写了什么），否则下一个 AI 会话必然归因错位**。reconcile_execution_log 已有此能力（gate_id/action 可查），批次报告引用它应成为纪律。

**6.3 AI 会话并发的唯一安全网是幂等+互斥+可重锚定。** 批 6 撞 id（外部 regen 重分配 node_id 致尾部 7 件失效）、批 5/6 锚点振荡、在飞 52 件增量——全部源自多 AI 会话并发写库。已验证有效的三件法宝：by-path 权威轴（id 可重分配，path 不会）、单向容忍护栏重锚定、机械通道不降级人工态。补充批及以后一切批次沿用。

---

## 7. 登记与遗留

- [x] 议题 B 闭环（winmgmt 重启 + 33/33 复绿）
- [x] 议题 A 执行（7/7 design_maturity 修正，备份 architecture_20260827_171037.json）
- [x] 议题 D 施工（3 文件修复 + 54/54 测试 + 双实证；**+§3.4 缺口 4/5 两文件修复**，双 regen 实战验证；改动均留工作树交 Owner 统一提交）
- [x] 议题 E 补充批 **66/66 production 达成**（报告 .runtime/construction_20260825/reports/B007_SUPP_report.md；门禁 655 绿/sweep 零新增红；全库 **production=2933、testing=0、stable=1**（唯一残留=真·在飞 process_reaper.py 归所属会话）；差额 −1 归账 ide_health_daemon.py 在飞删除非回退）
- [ ] 议题 C 交易会话冒烟（Owner 窗口，§5 SOP）
- [ ] ARCH 注册表补登：库外通道悬案（§2.3-3）；治本修复五文件落账条目（§3.2+§3.4，提交时配号）
- [ ] 批 4-6 观察窗窗满翻 ✅（随 tracker 登记时一并；当前证据：批 5/6 域内在后续轮 sweep 零回退）
- [ ] 工作树五件治本修复随在飞批统一提交：sync_yaml_to_depgraph.py / apply_depgraph.py / diagnose_depgraph.py / generate_project_depgraph.py / test_density_quantile_trainer.py
