---
ttl: task_bound
completes_when: 战役收官时本件条目清零（或全部转为 Owner 已裁）则使命完成
title: 六图战役·待裁项登记（Owner 睡眠期跳过继续）
owner: st-mapbuild-20260924（总包）
---

# 99 待裁项（一句话 + 两选项 + 总包推荐）

> 登记规则：自裁模板（第一性原理+对标机构实践+查既有裁定）仍无法定的才进本件；进本件后**跳过继续下一任务**，不停工等待。
> 例外：**破坏性/资金类**条目即便总包能判，也必须经 Owner 门位（宪法 §5 第 2 条 high 域），本类条目**不执行只上报**。

## P0（有死线，优先看）

| # | 图 | 一句话 | 选项A | 选项B | 推荐 | 状态 |
|---|----|--------|-------|-------|------|------|
| P0-1 | 图12 | 备份镜像 `g_mirror` 的 `ch_vm_backup` 目标：e3cff4e6fc 已摘除（防 robocopy /MIR 回删），但被 6b7749d4a8 反向复活，dev HEAD 至今仍含该目标，主区只有一条未提交的 M；F 侧已瘦身为配置级 ⇒ **下一次 /MIR 会删掉 G 侧唯一 `data.vhdx`（实测 591.57 GiB），且 robocopy 退出码仍记 ok、无红字**。图12 W-F 车道实测判读，Owner 早执轮 7c06425bee 记的"摘除"事实成立但落地态被回退 | 立即再摘一次并同批补防回退锚（在 depgraph/契约面钉住"该目标不得回加"，让回加即触门禁） | 只恢复主区那条未提交 M 后走正门落地（快但同样无防回退锚，下次仍可被反向复活） | **A**——本件已发生一次"修好被反向复活"，只修不防=第三次踩同一坑；防回退锚属注册表/契约面净增，Owner 门位放行后再动 | **待 Owner（死线 2026-09-25 06:00，即下一次 DailyBackup 触发前）**；本战役全程未碰 backup 配置与盘侧 |

## 一般待裁（挖矿期累计）

| # | 图 | 一句话 | 选项A | 选项B | 推荐 | 状态 |
|---|----|--------|-------|-------|------|------|
| （暂无） | | 其余裁定项已按自裁模板自行判定并执行，登记在 `01_lane_workplan.md`（自裁 A 粒度律 / 自裁 B 封矿单元律）与后续施工卷 | | | | |

## 已知会 Owner 但不需决策的实测红条目（供晨读，不占门位）

1. **图12 终点不可证**：`recon_runner.run_daily_reconciliation`（日终三账）**未接线**——15:40 槽无分派 + 零调用方 + `reconciliation_differences` 0 行。图12 的域终点"对账 PASS"因此今天无法机械证明。（`reconcile_execution_log` 8.7 万行属图11 自愈环，误当对账证据=假绿）
2. **缺口回补器 `auto_backfiller` 建好未接线**：仅 `__init__` re-export + 测试；`wiring_registry.yaml:549-555` 以 `pure_library/exempt` 合法绕过接线门，而 SOP:138 写"常态在岗"。后果=因子/公式升级/源修复三类历史回填无人补。
3. **OPTIMIZE 周维护"开工了但没登记"**：计划任务 LastRun 09-20 03:30 / Result=0 / 日志 659 分区，但 `resource_samples` 零 `ops_*` 样本（册上 `planned/samples:0` 是测量缺失而非未跑）。且"失败 0"**不可信**：ch_reader 失败返空串不抛，`optimize_merge.py:145-148` 记为成功（同帧实测有 500 错误）。
4. **判重器不可用**：`check_tick_duplication` 的 `_SQL_TOTAL_ROW` 平铺 14 列在 `tick_data` 恒抛 Code 42，被静默吞成 0；真重复实测 2 组 4 行。RULE-DATA-OPS 点名的判重工具本身现在是坏的。
5. **图11 precommit 通道的回滚旗失效**：flag 名 `gate_precommit_run_enabled` 未在 flags 册注册且 default=True ⇒ 册上写的"回滚=flag OFF"恒不可达。
6. **图11 死分支**：`git_commit.py` 退出码实 11 种（0-10），码 4（STASH_CONFLICT 支）无生产者=死分支，码 8 双义。
7. **多表断供/滞后实测**（图12）：`l2_tick` 0 行（L2 权限+降级腿已删）、`suspend` 0 行（停复牌子源断链）、`hk_kline`/`futures_kline_qmt` 停 09-16、`kline_sector_intraday` 停 2 交易日、周/月线停 9 日、`consensus_daily` 停 10 日（上游 `research_report` 停 6 日）、`sector_state` 两 stage trade_date 倒挂、`sector_preference` 全表仅 1 行。
8. **CLI `pause <source>` 名义化**：`policies.yaml` 无 `enabled` 键、热重载即复位、不跨进程——停源动作今天不真生效。
9. **图14 政策与实码背离 9 处**：`construction_workflow_policy` 声称的件里 `scripts/ide_health_service.py`（5 份文档共引、全仓不存在）、`session_worktree.py` 四子命令、`apply_depgraph --query-production` flag 等**不存在**；且裁定#384（2026-09-20）把该政策上游 49 件 design_memos 整体归档，造成政策内 12 处链接全断、行号锚 7/7 全偏。
10. **L-INTEG 收口撞号重编（知会，非决策件）**：任务书预设收口裁=裁定#412，实扫发现主区已落地 #411（翻译册 dedupe）/#412（akshare 克隆退役）/#413（GPU 点火三件套），且本战役未落地首波三图准入裁原编 #411 与已落地 #411 撞号。处置=战役侧让号重编 #411→#414、收口总裁取 #415（取号器在册面+手工核对 pending 袋，在途无新声明）；已落地条目零改动，册面删除集=∅。选项A=维持 414/415（推荐，键唯一已实证）；选项B=若 Owner 认为战役条目应回到 411 位则需对已落地条目做历史改写（不推荐，违"已落地不回改"）。
    **【2026-09-30 二次重编执行（F 组补完车道 st-nightsweep2-nf2-20260930）】**：上项重编所取 #414/#415 已被主区于 2026-09-28 抢先落地（#414=四盘一盘一责终裁定/#415=唯一在任总包+热册单写者，见 ruling_registry）——战役两裁编号二次撞号作废，经取号器重占 **首波三图准入裁=#451、收口总裁=#452**（claim_451/452.json 在案，整合批落地时须与 ruling_registry 新条目同 commit 原子登记，裁定#20-B）；已落地条目依旧零改动。

## SW13 终态段（夜战 2026-09-29 · 图14/15 图本体+词表收口）

> 车道 st-nightsweep-sw13-20260929（总筹 st-nightsweep-chief-20260929）。审计卡 I4:I453 组缺口「图14/15 图本体 yaml=0/2 proposal+词表缺+红蓝对抗缺」的**图本体面**于本段落地收口。

**落地件（收编自本战役 st-mapbuild-20260924 终版成品，非重造；sha256 前 16 位锚定）**：

| 件 | sha16 | 状态 |
|---|---|---|
| config/construction_workflow_map.yaml | 254732370135ad20 | 新落 HEAD（2221 行；29 节点/34 边/7 反馈环；anchor_source=proposal，pending_anchors 17 诚实开账） |
| config/strategy_card_lifecycle_map.yaml | 3297a22f83934c81 | 新落 HEAD（与 91 提案件 §10 idempotency.sha16 逐字一致；13 状态+17 迁移+13 禁边+56 条 card_ledger；anchor_source=registry） |
| docs/.../vocabularies/card_state_vocabulary.yaml | 288ef273321f89df | 新落 HEAD（REG-CARDSTATE-VOCAB-001，13 值闭集） |
| docs/.../catalogs/experiment_registry.yaml | 迁移批整拷 | 2.1→2.2（L-HOST15 已按总包裁执行的迁移落地主区；+56 CARD-* 条目，unique_key 不动，零新枚举） |
| docs/registry_of_registries.yaml | 增量重放 | +REG-CARDSTATE-VOCAB-001 行；REG-EXP-001 entry_count 11→67；summary 由 check_registry_consistency.py --refresh-summary 机生（total 80，broken 0） |
| docs/.../vocabularies/index.md | +1 行 | card_state_vocabulary 行（照 mapbuild 同款 diff） |

**验证留痕**：SW13 自含结构对抗测试 tests/governance/d5_architecture/test_fig14_fig15_map_bodies_adversarial.py 18/18 过（3 绿控制组+15 红案：杀节点/断边/伪造计数/坏枚举/封卡就地复活/悬空 revives 全部先证能红）；chief7 预放校验器 validate_strategy_card_lifecycle_map.py 只读复跑=结构 0 错+8 实例红账，逐条等于 91 提案件 §10 red_state_after_migration 已登记真实数据缺陷（F-05/F-07/X09/F-03×2/族账×3），零新增红。规格卡=docs/_working/night_sweep/fig14_fig15_spec.md。

**仍未收口（非本车道，登记待整合）**：
1. chief7 两袋在飞（q-…-0329/0369）：validate_construction_steps.py、两图 adversarial 测试、fig14 簿 00/01——其 _GOOD 控制组读 config/construction_workflow_map.yaml，本段落地后其缺图前置已解除。
2. 战役整合批（272 件）：alignment_checklist 图14/15 行、construction policy 17 锚块、三 gate、五生成器、ruling #414/#415（战役编号，与主区已占用 #414（存储终裁）/#415（总包单写者）撞号，需按其 §10 让号机制再重编）。
3. fig15 两判据口径待总包：CV-10 第四腿终态绑法 / CV-08C FPOOL/MIDVAL 两族成员轴（91 提案件 §10 留痕，SW13 未动阈值）。
