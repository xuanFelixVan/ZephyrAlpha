---
ttl: task_bound
title: 总筹指挥册 波1 · 通宵令执行序与已裁事项（继任棒次从本册接手）
session: st-fflead-20260925
---

# 91 总筹指挥册 波1（继任棒次第一读）

> 本册＝Owner 2026-09-25 通宵令（全流通＋挖矿封矿＋施工内收＋线间并行）的执行序与裁定索引。
> 上一棒真源：`00_orchestration.md`（编排册）＋`decision_map_campaign_20260924/HANDOVER.md`（总筹交接书）。
> 本棒＝第三棒 `st-fflead-20260925`。**所有数字均为实测，未实测的一律标"未验"**。

## 一、本棒已完成（可复核）

| 项 | 凭据 |
|---|---|
| IBT 首跑 22 件审计链复原入库 | commit `4c00b9607d`；HEAD 内 22 件 sha256 == 队列袋 `blob_sha256` 22/22；案卷 `decision_map_campaign_20260924/16_missing22_recovery.md` |
| N-16 提交面漏读真源治本＋永久尺 | 同 commit；`check_naming_convention.py` 内 `_in_n16_skip_dir` 3 处；尺 `tests/governance/d3_metadata/test_n16_skip_working.py` 3 passed；命名门禁全族 274 绿 |
| 全环节交叉验证（122 是否完备） | `00_skeleton/90_crosscheck_link_census.md`（子代理产出，四轴实证） |
| M1/M6、M5 补挖波 | `m1_data/90_backfill_wave.md`、`m6_frontend/90_backfill_wave.md`、`m5_scheduling/90_backfill_wave.md` |
| 16 案待裁已裁 | `90_chief_rulings_wave1.md`（含"不可逆删除→可逆三段式"通则；新增 10 案由子班回带，见 §四） |

## 二、骨架结论（决定后续所有派单口径）

1. **环节真源＝F 编号总册**，`L01–L09` 降级为 TDM 决策子域视图（其 135 行子块台账有强消费，**不退役**），M0 的 76 编号退役为映射附注。F 体系缺 L02 情绪／L04 传导／L06 条件共振上岗三域——是漏项证据而非"两套都好"。
2. **122 不完备**：去重后 **29 项候选漏项**，P0 四项＝DB schema 迁移(REG-MIGRATION-001)、状态词表(REG-STATE-VOCAB-001，GATE-VOCAB 真在拦、死信 0036 死于它)、`data_governance` 域、38 个 `module_ref:null` 节点无归属。建议 122→≈151。**未验**：是否全部成立需逐条二验。
3. **成册规模改阈值制**：全量子类目独立成册 ≈1061 册不可行；改"子包 py≥15 升册"（≈38 册）/宽档≥10（≈60 册），总规模 ≈160 册、现 115 册 → **新开 45–67 册**。首波 5 册＝4 个 P0 漏项＋**机生四向对账表**（同时治"手工清单必漂移"宪法 §9.5 病灶）。
4. **数值漂移四例已在册**：TDM"138 节点"过期（实 182）、F 册 entry 132 实 128、ROOR 77 vs summary 76、代码顶层域 57 vs 册称 56。凡引用这些数字前先跑对账表。

## 三、执行序（继任棒次照此推，线间并行）

**P-0 先落地，别先施工**——`fullflow_mining/` 作业簿曾长期只挂主区 index/未跟踪面（本棒 23:xx 实测：HEAD 仅 1 件，盘上 118 件）。落地未完成前，任何"再产新册"都在扩大敞口。

1. 复核本棒四批落库结果（命令见 §五），未落尽者按 §六 处方续落。
2. 补 P0 四漏项册＋机生对账表（1 波 5 册，派 5 并发子代理）。
3. 施工波（内收原则，逐条对应裁定）：
   - **接线类**（无门位）：R-M1-06 清洗三引擎（`config/cleaning_rules.yaml` 承载 DSL＋一处调用点，读侧 flag 档先行）；M6 报告链最薄一刀 `/api/reports` 只读投影；R-M2-6 `pf_alloc` 单一配比真源＋`auto_mount` 降为提名。
   - **披露类**（无门位）：R-M2-2 考尺产物加 `cost_caliber` 双口径列；R-M2-1 令文/验收册统一 T0 200/T1 3700/T2 900 并禁引"24990"。
   - **可逆隔离类**（无门位）：R-M1-01/04 影子表 `RENAME` 入 `*_retired_20260926`＋零消费探针；R-M1-02/03 只出 dry-run 清单＋读侧 `FINAL`/过滤视图，**禁夜间 DELETE**。
   - **排程约束**：R-M2-3 池基先修再放 T2（T1 完赛后立批 D 新鲜窗重考）；R-M2-5 订单语义维持只防御至池基落定。
4. 红灯抢修（本棒实测，属"静默失明"类，优先级等同 P0）：
   - **备份链**：`data/databases/backup_state.json` `last_backup_status=failed`＋`log_verified=False`；06:00 班 9.1h、任务码 267014；3 次 reconciler 被 `lock_held` 吞；可恢复性零实证。
   - **性能水位台账失明 22h**：`--status` 打 01:47 缓存快照；`ZephyrAlpha_ProcessReaper` 每 5–6min fire 却 **exit 1**。
   - **tilib 夜回填仍红**：计划任务 action 仍指旧 `.bat`（编排册记 0041 已落但未接任务面）。
   - 上述三条**先修可观测性再修因**，否则修完仍无法自证。
5. 循环检查两轮问题=0 → 红蓝极限对抗 → 修复。**本棒未做**（见 §七）。

## 四、待裁账（净增 0，但确有 3 案属 Owner 门位，不可自裁）

| 案 | 为何不能自裁 | 已给的可逆替代 |
|---|---|---|
| R-M2-4 六段词表三套映射两套冲突（同闸宽差 75%） | t0 班已正式升级 Owner；切词表＝判据语义变更，且 auto_mount 生产挂图与 GPU 条件轴必须同批 | 本棒只落"必须同词表、切换同批"的机械约束 |
| R-M1-05 宪法/骨架"16 表"vs 代码 13 轴 | 动 AGENTS.md 属修宪入口（≤300 行等长替换硬上限） | 登记为待同批修宪项，判据出处齐 |
| R-M1-07 两个 Disabled 计划任务真删／R-M1-01 真 DROP | 生产流转＋注册表净删＝宪法 §5 high 门位 | 改为禁用＋留证、RENAME 隔离＋探针，施工不等待 |
| 新增 10 案（M5 5 案＋M1/M6 5 案） | 子班按纪律未自裁 | 选项与建议已在各册 §六，待下棒总筹裁 |

## 五、复核命令

```bash
git ls-tree -r --name-only HEAD | grep -c '^docs/_working/fullflow_mining/'      # 期望 118（未达即有未落批）
git log --oneline -6 --grep st-fflead                                            # 本棒落库批
python -m pytest tests/governance/d3_metadata/test_n16_skip_working.py -q        # 3 passed
git diff --cached --numstat HEAD -- docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml   # 删除列须=0
```

## 六、本棒踩到并已在脚本里固化的处方（热册并发是今晚主敌）

1. `capability_canonical_file_registry.yaml` 今夜被 `st-commitspeed-tbl`(23:43)/`st-commitspeed-pkg8`(23:28)/`st-qmine`(23:09) 三面"先行册"重写，**我的一次注入被非 CAS 写整片抹除**（HEAD 与工作区同时归零）。
2. 唯一安全写法＝**同进程内**：读当前 HEAD→对 HEAD 重放本批块→断言"丢 HEAD 行≤30 否则回退重读"→`git add`→**立刻**调网关提交（不等下一轮对话）。分两步（先写后提、中间有 LLM 回合）必被竞态吃掉。
3. `safe_write_text` 对注册表族有双保险：未声明 `expected_base_sha256` 拒写；删除行 >max(1, 0.5%×行数) 拒写。**别用 `allow_mass_edit=True` 绕它**——那正是它要拦的东西。
4. 禁 `git checkout HEAD -- <热册>`（=第二次蒸发）。要回退只能"回 HEAD 文本＋重放本批块"。
5. 主区直提在他班活跃时：`commit_queue.py enqueue` 会被 WORKTREE-REQUIRED 拦；`git_commit.py --enqueue` 需 `commit_queue_interactive` 旗（Owner 窗口）；本棒走 `git_commit.py --allow-non-worktree`（2026-08-13 裁定 AI 可默认，留痕）。

## 七、本棒未完成（不留给明天误认为已做）

- 117 件作业簿四批落库：**执行中**（三会话抢全局提交锁），完成与否以 §五 首条命令为准。
- 循环检查两轮问题=0：**未做**。红蓝极限对抗：**未做**。故 Owner 要求的"全绿/零遗留"状态**本棒未达成**。
- 122→151 环节扩展、45–67 新册、施工波全部条目：**未开工**（按 P-0 原则排在落库之后）。
- 本棒自证边界：凡"已修/已落地"均给 commit 号或可复跑命令；未实测写"未验"。
