---
ttl: task_bound
title: 附录A 退役策略档案追凶——"~800 个/退役 600+/现役 161"口径对账
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 附录A：退役策略档案追凶

> **结论先行**：**"退役策略档案"作为单一账本不存在——它从来就没有以"退役策略大军"的形态存在过。** 实测主注册表=161 条（19 active+139 candidate+3 deprecated，与 Owner 现役口径完全吻合）；"600+ 退役"实际对应**两条入库漏斗的出局者**（聚宽 600 条源码漏斗 + 潘潘 546 条入库判定），它们被淘汰在"入册之前"，从未进过策略库；正式的退役机制（判据+工作流+归档区）三件全部建成但**一次都没触发过**。可机读的"退役/出局账本"有三处，均支持重考。

## 1. 实测对账（全部带路径）

| Owner 口径 | 实测 | 证据 |
|-----------|------|------|
| 现役 161 | ✅ 精确吻合：161 条=19 active+139 candidate+3 deprecated | `docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml`（2026-09-24 yaml 实测 Counter） |
| 退役 600+ | ❌ 无此形态：strategy_archive/ 归档区**空**（仅 README）；registry 无 retired 状态；git 史无批量退役提交 | `D:\ZephyrAlpha\strategy_archive\`（find 实测仅 README.md）；registry 状态词表=candidate/active/deprecated |
| ~800 个策略库 | ◐ 数字可由两条漏斗拼出：潘潘课程 546 条（memo29）+ 聚宽 600 条源码（SOP-C）≈1,100+ 原始量，或指"历史上所有被 exam 过的策略对象"；非某一时刻的库存快照 | 见 §2 |

3 条 deprecated 现役名单：STR-MULTIFACTOR-031（4 分钟涨速资金异动，ARCH-305 迁移留指针）、STR-MULTIFACTOR-034（空仓等主线）、STR-MULTIFACTOR-090（策略生命周期八阶段——体系知识不占业务条目）。

## 2. "退役大军"的三个真实来源（追凶结论）

1. **聚宽 600 条源码漏斗（出局者最大头）**：SOP-C 立法漏斗=600 → 粗筛出局（余 ≈240）→ 翻译适配（余 ≈150）→ 快筛批测（余 ≈60）→ 聚类去重（余 ≈20）→ 入库 ≈10（`docs/01_policies_and_standards/sop/backtest_system_sop/sop_c_strategy_library_intake.md` §0）。出局留痕：`data/strategy_intake/c4_deferrals.csv` 322 行（md5_12/年份/原名/defer_reason/note 五列机读）；翻译件 91 个存 `scripts/backtest/translated/`。**SOP-C 铁律"保留清单可追溯（不删除源文件）"**——出局≠销毁。
2. **潘潘 546 条判定（入库/并入/不建三态）**：`docs/_archive/29_factor_strategy_extraction.md`（⚠️ Owner 引用的 design_memos 路径已归档迁址，2026-08-30 greatwall 核销批迁入 _archive）结案报告：策略库全量重建 146 条+删旧 59 条 deprecated；159 条并入宿主条目（aliases+doc_ref 反链）；29 条判定不入库（逐条理由留痕）。**"并入宿主"的 159 条是最像"退役"的一批——它们没死，被吸收了**。
3. **git 史上的全量重建**：commit 62e3ae13（29 号备忘录 546 条批量入库 11 库——因子/策略全量重建）一次性删除了旧库条目（含 111 条 deprecated 因子、59 条 deprecated 策略）——如果 Owner 的记忆来自某个旧快照或某次统计脚本的旧口径，来源在此。

## 3. 退役机制现状（机制在、无人走）

| 件 | 状态 | 路径 |
|----|------|------|
| 退役判据（五骑士） | ✅ production，阈值已裁定转正（滚动 20 日跑输>5%/滚动 60 日 Sharpe<0/回撤漂移 1.5x/相关<0.5/逻辑失效） | `src/zephyr/governance/lifecycle_governance/strategy_retirement_evaluator.py`；裁定留痕 memo55 §3.5 |
| 退役工作流（5 步） | ✅ production | `src/zephyr/governance/lifecycle_governance/retirement_workflow.py` |
| 归档区（四件套第④条：manifest.json/params_snapshot.json/pnl_curve.csv） | ✅ 目录建成、❌ 空（零归档） | `D:\ZephyrAlpha\strategy_archive\README.md`；写入件 `strategy_archive.py`（归档只增不改，防路径穿越） |
| 退役原因机读词表 | ✅ 五骑士归因（crowding/regime_change/overfitting/…） | strategy_archive.py StrategyArchive 产物字段 |
| 复活机制 | ✅ 设计在册（regime change 类退役可经孵化阶段重评，须走全流程） | strategy_archive/README.md 纪律节，援引 61 号 §3.9 |

**结论**：不存在"被遗忘的退役档案"；真实状态是"正式退役通道就绪、零触发"，因为策略转正量（19 active）还小，衰减周期未到。Owner 的"退役 600+"应改记为"**漏斗出局+并入宿主 ≈600+**"——语义是"淘汰在门外"，不是"退役在册内"。

## 4. 能否重考？（三账本逐个回答）

1. **c4_deferrals.csv（322 行出局者）**：✅ 可重考——md5 可对回源文件；defer_reason 机读（fundamental_gate/数据缺窗等）；重考=按 SOP-C C4 快筛口径（D1：IS 2019-2023/OOS 2024-2026，同成本同 T+1 同引擎）+DSR 纳入全部试验次数；**新考须重开预注册**（exam_policy §1，禁拿旧分免检复活——#331 砍掉的旧形态与 #386 封死的复图救不因重考复活）。
2. **memo29 并入宿主的 159 条**：✅ 可检索重考——宿主条目 aliases+doc_ref 反链可枚举；重考语义=对宿主条目做分状态复验，而非逐条复活。
3. **strategy_archive（空）**：未来首个退役策略触发后自动成为第四账本（PnL 曲线+参数快照+五骑士归因，README 明示"新策略孵化时须对比是否优于已退役同类"）。
4. **deprecation_note 缺失**（唯一发现的小缺口）：现行 3 条 deprecated 条目无结构化退役原因字段填充——建议（不施工）给 registry 的 deprecated 语义补 `deprecation_ref`（指向判死单/裁定号），使"册内退役"也走五骑士归因，与 strategy_archive 词表对齐。净零对价：零新文件，复用五骑士词表。

## 5. 一段话结论

**现役 161 精确吻合；"退役 600+"=聚宽漏斗出局（c4_deferrals.csv 322 行+粗筛出局）+潘潘并入宿主 159 条+git 全量重建删除的旧 deprecated——淘汰发生在入册前，不在册内；正式退役三件套全 production 但零触发，strategy_archive/ 空着等第一个真退役；全部三本账可机读、可重考，重考一律重开预注册。**
