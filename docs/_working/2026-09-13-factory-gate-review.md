---
ttl: task_bound
---

# 策略工厂门禁任务审查报告（交接指令 v2 第零段）

> 2026-09-13 夜班交接（night-sweep-20260913 撰写指令）→ 接手会话 factory-gate-b2-20260913 审查。
> 审查方法：全部结论以仓库实况证据为准（git log/git show/文件实测/代码通读），指令描述与实况的偏差逐项留痕。
> 审查时点基线：HEAD=b58b3c4d46（2026-09-13 07:37 watchdog 自动提交），此后 8 小时零提交、零活跃会话。

## 0. 审查结论：**B（通过但需修正）**

任务方向正确、样板齐备、无过度工程风险，但**指令前提有重大漂移**：五件套中三件已由更早会话
（st-zcode-c4-20260912）落地，实际剩余工作=其规划中的"第二批"两件（FACTORY-MAP gate+九图挂轴）。
另发现一处**与主任务无关但必须先修的 HEAD 断链**（上一班半截提交）。按 B 结论修正后施工，
修正清单见 §6。

## 1. 前提核实（指令引用 vs 仓库实况）

### 1.1 重大发现：五件套 3/5 已落地，指令按"未建"规划

commit `681a7fc806`（2026-09-13 05:56，st-zcode-c4-20260912）「策略工厂图门禁第一批」：

- **件1 structure validate**：已建 `scripts/governance/d5_architecture/validators/validate_strategy_production_map.py`
  （MOD-BT-080，198 行，v0.2 schema 十项结构校验：字段完整性/边闭合/E0-E9 层位/laws/产品清单/
  built 必有锚/lane 归属/未声明反馈环/自环/store_refs 三要素/decision_question 长度）
- **件2 对抗测试**：已建 `tests/backtest/test_strategy_production_map_adversarial.py`
  （MOD-BT-081，15 用例：好图通过+14 种坏图全拦），实战战果=上线即抓到 FAC-E1A built 无锚真问题
- **件5 台账联动**：已并入件1（check_stores：磁盘路径实测+CH 表 EXISTS，"待定"入库位降 warn 不阻断）
- 该 commit message 明确规划：**"第二批（FACTORY-MAP gate 注册+九图挂轴）等 commit_gates 存量测试
  修复落地后执行"**——前置 f3f6ecb86f（conftest 自愈）已落地，第二批施工条件已满足

**剩余工作即第二批：件3 FACTORY-MAP gate + 件4 九图挂轴。** 指令的"五件套施工"应读作
"第二批两件施工"；工厂图头注释"四关验收件未建"为过时陈述（批1 落地时未回写），本批顺带修正。

### 1.2 其余前提逐项核实

| 指令前提 | 实况 | 判定 |
|---|---|---|
| 工厂图真源 config/strategy_production_map.yaml v0.2 | 存在，schema_version '0.2'，15 节点/15 边/2 反馈环（E9→E2 有边、E6→E1 仅声明无边） | ✓ |
| TDM 结构校验 src/zephyr/trading/decision_map.py | 存在；且发现更直接样板：DECISION-MAP gate(138)=decision_map_gate.py（触发式收窄+懒加载单一真源模式） | ✓ |
| gate 141 样板 industry_chain_map_gate.py | 存在（触发文件交集+fail-open/fail-closed 分域设计） | ✓ |
| gate 注册双登记（gate_registry+in_process_gate_registry） | 双文件均存在于 docs/01_policies_and_standards/_registry/catalogs/；**实况细化**：in_process=真源（gate_auto_registrar 动态加载），gate_registry=派生目录缓存（最新 gate 提交 47ab163cbf ALGO-NOTE-SYNC 实证未手改它）。本批按指令双登记保自包含，无害 | ✓（细化） |
| alignment_checklist 在 docs/02_enterprise_architecture/ 下 | 实际路径 `docs/01_policies_and_standards/sop/alignment_checklist.md`（v1.4.0 八图满贯版，手维护表格无自动扩展机制） | 偏差（路径） |
| align_all 入口 scripts/governance/d5_architecture/generators/ | 存在，现有 [1/7]..[7/7] 七节（图1-4/图5/图6/图7/注册表层/文档抽查/图8），挂轴=加第八节+计数重编号 | ✓ |
| 上一班 7 项成果勿重复 | DEDUP=69bd7680✓ 14 WARN=ebea698cfb✓ 并发报告=2f786454✓ conftest=f3f6ecb86f✓ commit_gates 测试清零=89e5ebde92+f3f6ecb86f✓；千股千评 lint（含于 69bd7680 的 market_alt_stock_comment.py 变更）与 intelligence module_id 为会话内验证项无独立工件 | ✓ 5+2 判定完成 |
| 并发边界：单独执行 | session_registry.json={}、lookup_audit 最后写入 04:14、最后提交 07:37（watchdog 自动）、接手时 8h 静默、process_reaper CLEAN（trae_hits=1 非会话进程） | ✓ 单独执行成立 |

### 1.3 新发现：上一班遗留工作区状态（先处置再施工）

1. **HEAD 断链（P0，必须修复）**：DEDUP 提交 `69bd7680` 修改 15+ 文件
   `from zephyr.signal_ashare.core.analysis_utils import ...`，但该目标文件**未入库**（untracked，
   磁盘 4063 字节，BLUEPRINT 头 MOD-SIG-142/模块说明/6 组函数齐全，import 链实测通，
   creation_token 已登记=本意要提交）——fresh clone 必炸（半截提交实证）。
   修复=补提交（--adopt-prior-work，认领 night-sweep 遗留）。
2. **暂存区震荡（净零）**：11 文件 staged 回退+工作区重应用（`git diff HEAD` 实测仅
   architecture_model/index.yaml 1 行 last_updated 日期漂移=watchdog 派生域）——
   `git reset` 最小侵入清理（内容零变更），不提交 index.yaml（watchdog 自动收敛域）。
3. **18 个空 __init__.py**（tests/audit、tests/feedback、tests/pf_alloc 等新子目录，0 字节，
   创建于 05:02-06:05 测试窗口；对应拆分提交未含 __init__，fresh clone 不依赖它们）——
   判定=pytest/工具副作用，**留置不提交**（登记，防 git add -A 误收）。

## 2. 必要性审查（裁剪方案）

| 候选项 | 裁定 | 理由 |
|---|---|---|
| 1 structure validate | 已建（批1），不重复 | — |
| 2 对抗测试 | 已建（批1），gate 层补红蓝用例 | — |
| 3 FACTORY-MAP gate | **建**（priority=142 空位已验证） | 图为增长轨（E1 五车道"无限生长"/E3 极大），断链风险随增长上升；触发式设计=非地图提交零开销；学 DECISION-MAP(138) 懒加载单一真源（校验逻辑禁复制进 gate） |
| 4 九图挂轴 | **建**（轻量） | alignment_checklist 无自动扩展机制（手维护表）必须手工挂轴；align_all 加第八节顺带把台账联动纳入循环检查 |
| 5 台账联动 | 已并入批1 校验器 | align_all 第八节引用 check_stores 即纳入循环，无需独立件 |
| field_dictionary 登记（批1 message 承诺"随第二批"） | **裁剪缓办**（留痕待 Owner 追认） | REG-FLD-001 管数据层字段（16 域 FLD-* 条目），地图节点字段不入（TDM 先例：TDM 节点字段同样不在 REG-FLD-001）；工厂 store_refs 数据工件全部 build_status=pending 无实体字段可登；待首个工件实建时随其 schema 同批登记 |

**过度工程判定：不成立。** 剩余两件为最小闭环（commit 硬阻断+全图对齐清单各一件），
非"全套克隆 TDM"——批1 已按 15 节点规模缩水实现（198 行 vs TDM 全量校验体系）。

## 3. 顺序审查

- 依赖序：校验器（批1 已就位）→ gate（消费校验器）→ 九图挂轴（checklist 图 9 行需填 gate 名）
  → 循环验证。✓ 合理
- **P2-D 是否先行：否。** 批2 变更集（gate 文件/注册表/checklist/align_all/图 YAML 头注释）
  不触碰任何工厂图 module_ref 指向的 .py（MOD-BT-035/039/041..075/078 的代码文件），ALGO-NOTE
  归因交互成本与批2 无关。按指令"主任务期间 P2 只审不施"执行。
- 批0（HEAD 断链修复）必须先于批2：修复批极小（1 文件），先消除 fresh-clone 炸点再动治理基建。

## 4. 风险审查

- **全局生效半径**：触发式（触发面={图 YAML, 校验器 .py}），非触发提交走 skip 路径零开销；
  触发时纯 YAML 解析+内存校验 <1s 无外部 I/O。注册后立即全量 gate 链验证无误伤（批2 提交本身
  触发图 YAML 变更=天然实弹）。
- **自指提交循环**：无。gate 只读不写；注册提交（gate 文件+注册表+图头注释同 commit）时
  gateway 从磁盘读 in_process_gate_registry.yaml 即已加载新 gate，对同 commit 的好图放行，自洽。
- **结构 vs 仓储分域**：store_refs 存在性含 CH 连通性（环境异常域）——不入 gate（防 infra 故障
  误伤全部地图提交），归 align_all 第八节（CH 连接异常降 warn，学图 8 PG fail-open 先例）+
  CLI 校验器。gate 只管确定性结构校验（fail-closed）。
- **并发冲突面**：零活跃会话+批2 文件集与孤儿脏文件零交集（孤儿文件=tests/__init__、TDM 蓝图、
  futures_basis_monitor、script-manifest、architecture index——均不在批2 变更集）。

## 5. P2 治本核查（只审不施，真伪判定）

真源 docs/_working/2026-09-13-concurrency-commit-perf-study.md §2.3/§4 与代码实况对照：
- P2-A gate 结果缓存：真问题（check_all 全量 106 gate 无缓存无短路）——动 gate engine 语义，
  需双轮红蓝+Owner 追认，**不施**
- P2-B 子进程税 12.52s：真问题（run_checker_script 每次 spawn）——同上**不施**
- P2-D ALGO-NOTE hunk ±3 归因盲区：真问题（_collect_node_block_changes 粗粒度归因，
  上一班引号化 workaround=治标实证）——可先行但与本批无交集，**不施**（留 Owner 拍板）
- 蓝图 churn/机器伴生比：运营监控项，非本批施工项
- 结论：P2 五项全部"审讫不施"，与指令裁定一致。

## 6. 修正后施工清单（B 结论执行方案）

1. **批0 孤儿处置+HEAD 修复**：`git reset` 清震荡暂存 → 补提交
   `src/zephyr/signal_ashare/core/analysis_utils.py`（--adopt-prior-work 认领 night-sweep 遗留）
2. **批2 第二批门禁**（对照 47ab163cbf ALGO-NOTE 注册配方）：
   - 新建 `src/zephyr/gov_enforcement/commit_gates/strategy_factory_map_gate.py`（priority=142，
     触发面={图 YAML, 校验器}，结构校验 fail-closed，全套头注释+TESTS 指针+CREATION-TOKEN）
   - 新建 `tests/governance/commit_gates/test_strategy_factory_map_gate.py`（红蓝：好图过/
     非触发 skip/坏图拦/解析损坏 fail-closed/校验器变更触发）
   - 扩展 validator：check_stores 增可选 root 参数（向后兼容，align_all 传仓库根防 CWD 漂移）
   - align_all.py：第八节（结构 hard+stores hard、CH 连接异常降 warn）+[x/8] 重编号+报告
     标题/对齐轴九图化+hard_issues 纳入 fac_hard
   - alignment_checklist.md：§3 图 9 行+八图→九图（标题/数量/验证命令/硬阻断条件）+版本 1.5.0
   - strategy_production_map.yaml：头注释四关验收件齐备+状态升级（"图 9（拟）"→"图 9"）
   - 登记：in_process_gate_registry.yaml（真源）+gate_registry.yaml（目录，双登记）+
     capability_canonical_file_registry.yaml di_seam_exemptions（gate+测试两文件 token）+
     module_translation（--name-zh）+depgraph --add-design-node
3. **循环验证两轮零问题**：CLI 校验器全量（含 stores）+批1 对抗测试+gate 红蓝+align_all 全量
   +commit_gates 测试套件+实弹（批2 注册提交=好图实弹；坏图拦截=红蓝 tmp 直调 gate.check，
   先例=TestRedDecisionMap）
4. **field_dictionary 缓办+18 空 __init__.py 留置**：登记待 Owner 追认/下会话处置

## 7. 留痕

- 审查人：factory-gate-b2-20260913（接手 night-sweep-20260913 交接指令 v2）
- 重大偏差 3 项已按"仓库实况优先"处置：五件套 3/5 已建（§1.1）、HEAD 断链（§1.3）、
  checklist 路径（§1.2）
- 无 C 级前提不成立情形，无需停下汇报 Owner；field_dictionary 裁剪为 B 级修正项，
  随最终汇报提交 Owner 追认
