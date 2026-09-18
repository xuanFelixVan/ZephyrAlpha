---
ttl: task_bound
completes_when: 全流通战役收官且本清单每一项要么被 Owner/Max 裁定、要么被明确判为不办并留痕
---

# Max/Owner 待裁定清单（A 类）

> 判据：**A 类 = 存在真实分叉、需价值判断、或属 Owner 门位（资金 / 外部账号 / flag 翻转 / 注册表净删 / PROTECTED-PATHS），Flash 无权自签。**
> 不含"只是没工时"的项——那些在 `MAX_EXECUTE_LIST.md`（B 类）。
> 每条给：案卷完整路径 → 争点 → 不点这个头会怎样 → 一条验真命令。
> 术语按 Owner 偏好：先说"这是什么"，再说"为什么要你点头"。

## A0 · 一句话背景

本战役（全流通=所有链路灌上真数据跑通）由 Flash 系模型执行。Owner 令：**执行与大部分裁定用 Flash，
只把"必须 Max/Owner"的留下**。以下 11 项是 Flash 判自己**不该判**或**无权判**的。
其中 **A1 是唯一一处"批一行就解锁一条主链"的**，其余多为方向选择。

---

## A1 ★ 受保护契约一行：`slippage_bps` 允许 NULL（解锁 R-014 全链）｜P0
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_drift_01_contract_approval.md`
- **要批的东西**：`architecture_model/contracts/cross_layer_contracts.yaml:806`
  由 `float`/`required` 改 `Optional[float]`/`false`。该目录是 **PROTECTED-PATHS，无 CLI 逃生旗**。
- **为什么要你点头**：现状实测——契约**拦得住 NULL，却放行 `-10000.0` 这个哨兵错数**（编号 ZA-SH-0054）。
  不批 → 置 NULL 永不可落地 → `execution_report_producer.py:414` 的 `f"{float(v):.6f}"` 会继续把
  "未成交滑点"写成 `±10000.0` 这种**看起来像数的错数**，下游绩效归因（TDM-F-C3-01）吃的就是它。
- **红队已实证**：R-014 至今**未真正落地**（CH 列已改 `Nullable(Float64)` 让 NULL *存得下*，但全仓没有任何一处写 NULL）。
- **不批的替代方案**（也要选）：改契约 / 或改哨兵值语义（把 `-10000.0` 换成显式 `missing` 标记位）——后者动面更大。
- **验真**：`grep -n "slippage" src/zephyr/ex_core/execution_report_producer.py | head` +
  `python -c "import yaml;c=yaml.safe_load(open('architecture_model/contracts/cross_layer_contracts.yaml',encoding='utf-8'));print(str(c)[:0])"`（人读 :806 附近）

## A2 · quality_sentinel 的排班正门形态（车道抗命已判正确，但形态要固化）
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_sentinel_01.md`
- **争点**：数据质量哨兵要不要进 `tasks.yaml` 常规任务体系。车道实测：五类特殊时段槽位
  （integrity_check / catchup_guard / data_supply_sentinel / consensus_crosscheck / nightly_sentiment）
  **无一在 tasks.yaml 有条目**，且 `src/zephyr/data/scheduler.py:_run_special_schedule` 是**硬编码白名单**；
  新开空槽位会落到 `:2110` 分支后**静默返回成功**=典型的"配了行=在跑"假通道。
- **现状**：走 L13 托管 + `sweep_cadence_days:7` 节奏闸 + `data/runtime/quality_sentinel.disabled` 总开关（四要素各自取证）。
- **要你拍的是家族问题**：特殊时段要不要改成注册表驱动（甲案）。若改，本项托管形态就是"第二个真源"须合并；若不改，固化现状并把它写进调度政策真源。
- **验真**：`grep -n "return None" -B6 src/zephyr/data/scheduler.py | sed -n '1,20p'`；
  `grep -c "schedule: integrity_check" src/zephyr/data/config/tasks.yaml`

## A3 · `intraday_sector` 五任务停档期 + 三个 disabled 事件表任务的台账归因
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_sentinel_02.md`
- **争点**：板块盘中分钟线源已死（mootdx/tdx 2026-09-11 起整体断供，BRK-037），
  五个任务还在 `*/5 9-15 * * 0-4` 档期上空转；`audit_opinion`/`rights_issue`/`dividend` 三表任务 disabled。
  这是**生产切换**（要不要停档、停哪几个、换成什么源）+ **台账归因**（记"断源"还是记"退役"）。
- **要你点头的原因**：停档期=改生产调度；换源要选型（部分需外部账号）。
- **验真**：`python -c "import yaml;t=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks'];print([x['name'] for x in t if x.get('schedule')=='disabled'])"`

## A4 · 危机闸异常码无处登记（车道已置 None，拒绝伪造编号）
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_land3_01.md` ITEM-7
- **事实**：`error_code_registry.yaml` 属 PROTECTED 件，`ZA-PA-CRISIS` 进不去 ⇒ 该腿**主动把异常码置 `None`** 并请示。
- **要你做的**：正式配一个 `ZA-PA-00NN`。
- **不点会怎样**：危机闸触发的异常在告警面上**没有分类码** ⇒ 按 error_code 分流的消费方（若有）会把它归到 unknown；
  且"宁可 None 也不伪造"这个先例要留痕，否则下一条车道就会自己编号（本役撞号病已在裁定号与模块号上各发生一次）。
- **验真**：`grep -rn "ZA-PA-CRISIS" --include=*.py --include=*.yaml src tests scripts config`

## A5 · 是否授权代修他会话在途破件（residG 的 `pipeline_events.py` 接线）
- **案卷**：`req_land3_01.md` ITEM-1 + 台账 `COORDINATION_LEDGER.md` R-044
- **事实**：residG 车道的 33 行 `_crisis_l1_check` 接线被第三次整片收割回退，现 HEAD 与磁盘 `grep -c`=0；
  曾引入的 8 条红随破件调用一起消失 ⇒ **"测试变绿"不是被修好，是缺陷的证据面消失了**。
  成品现在**只存在于 G 盘冷库** `G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/`。
- **要你拍的**：宪法 §3.4 说"他会话在途违规不代修"，但该会话已死、文件已无人 claim ⇒ **死会话遗产算不算在途**。
  （B4 已把这行接线的落回列成执行项；此处只要授权判据，不要施工。）
- **验真**：`diff src/zephyr/strategy_pipeline/pipeline_events.py "G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/src/zephyr/strategy_pipeline/pipeline_events.py" | head -40`

## A6 · `sim-memo-202609.json`（1378 行）落点撞 DIRECTORY-CONTRACT
- **案卷**：`req_land3_01.md` ITEM-4；同批还有 G3/G5 两件（见 §A10）
- **事实**：模拟盘备忘被目录契约拦在 `docs/_working/pipeline-research/sim-memos/`；
  另 `docs/_working/2026-09-18-*` 三件日报撞 `FOLDER-CAPACITY-HARD-LIMIT`（该目录 123>120）——
  **这是一条战役中途才发现的门，总包原本不知道**（已把三件日报迁入 `docs/_working/fullflow_campaign/recovered/`）。
- **要你拍的**：冷数据归档策略（`docs/_working` 容量上限该按"件数"还是"字节"；超限时新建子目录还是出仓）。

## A7 · 战役报告 §四 的"翻案"追溯效力（会改历史结论）
- **案卷**：`delivery/MAX_REVIEW_CHECKLIST.md` §1.4（考尺 OOS/IS 同口径重算，R-E1）
- **争点**：同口径重算后，若大量历史 verdict 由"通过"转红 ⇒ 涉及**已毕业策略包/已签裁定**的追溯效力。
  这是"影响历史回测结论"的判断，Flash 不该独自扛。
- **状态**：车道是否真出了"翻案清单"**尚未核**；没出则本项判未完成。
- **验真**：`git grep -l "翻案\|reexam" -- docs/_working/fullflow_campaign/ | head`

## A8 · 对账域六套实现并存 → 本轮刻意不合并
- **案卷**：`MAX_REVIEW_CHECKLIST.md` §1.6（R-015）；实现清单见 `lanes/wirerecon_*.md`
- **争点**：持仓对账/执行对账有六套实现（`position_reconciler`、`reconciliation_loop`、`blueprint_code_reconciler` 等）。
  合并=大重构、会动生产链路；不合并=六套口径长期互斥。
  Flash 判"本轮不合"（避免在建批中做结构手术），但**这是策略选择不是事实判断**。
- **已并入本役的例外**：`position_reconciler`/`reconciliation_loop` 的接线缺口由 z-wiresafe/z-wirerecon 落了（HEAD 内已有人引用）——
  **合并不等于不接线**，此判据请复核是否维持。

## A9 · 热册里 `rule_replay` 新旧路径双记（净删=Owner 门位）
- **案卷**：`COORDINATION_LEDGER.md` R-046 末节
- **事实**：ARCH-031 迁移把 `src/zephyr/governance/rule_replay.py` 移进 `standards_governance/` 子包（新位在 HEAD），
  但 `capability_canonical_file_registry.yaml:32951` 与 `module_translation_registry.yaml:54991` **仍留旧路径条目**
  ⇒ 一能力两地址。清理=注册表**净删**，属 §7 Owner 门位，Flash 只登记不删。
- **同类**：ETF 时区备份五表 `*_tz_bak_20260918` 的物理删除时机；`.runtime` 与注册表目录 18 个 `.tmp` 残留（后者已由 z-rb-gov 在清）。
- **验真**：`grep -n "rule_replay" docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`

## A10 · 三件 Wave-4 遗留（要人批的删除/调度件）
- **G3** 冒烟脚本调度片段：`scripts/construction/qmt_bridge_regression_smoke.py`（已 staged 未落地，z-switch 在办）——
  进排班=占生产时段槽位，需拍档期。
- **G5** `.bak` 文件物理删除：备份件删除属不可逆，Owner 批时机（低峰窗）。
- **B6**（原 G1 参数对象化）：`owner_regime_switcher` 的长参数重构已由 z-switch 车道接手落地，**其放行与否仍挂 #310 案底**——
  若你维持 #310"不予放行"，则该 11 件应回退，请明示。

## A11 · 全流通完成度判据本身（**最该你拍的一条**）
- **事实**：Owner 的验收语是"全部通道打通、全部管线灌水、全绿、零遗留、零待裁"。
  本役实测：六向台账 **红 13 / 黄 5 / 绿 0**（且该台账已被判"与尺子互斥、须重生成"）；
  断点 **85 条中只有 5 条被独立复跑过**（未复测 80）；§6 十二个红蓝攻击面中 **8 面首役未打**（本轮已补派）。
- **要你拍的**：**"全流通"的可验收定义到底是什么**。三种候选：
  ① 六向台账无红（最严）；② 主链路 FF-01→FF-16 端到端出真数（中）；③ 断点清零（按 R-026 十类失效重判后）。
  Flash 不拍这个，因为**这决定本战役是"已完成"还是"已完成一部分"，而这两种说法对 Owner 的意义不同**。
- **验真**：`python scripts/automation/flowthrough_verifier.py --all` 后读输出的红黄绿分布（注意先重生成，勿引用旧台账）。

---

## 附：本清单的产生方式（可复核，避免"清单本身是幻觉"）
1. 18 份 `adjudications/req_*.md` 逐份读"请办/待总包动作"原文（脚本抽取，非记忆）。
2. 台账 `COORDINATION_LEDGER.md` §7 Owner 门位 + R-039~R-046 各条的"待裁"落点。
3. `delivery/MAX_REVIEW_CHECKLIST.md` 中标 `推断`/`转报` 且 Flash 自陈"若错会影响结论"的条目。
4. **未纳入本清单的**：所有"路径明确、无分叉、只缺工时"的项（→ B 类）；所有已落地待复核项（→ C 类）。
