---
ttl: task_bound
title: F73 A/B 联赛与分仓（champion-challenger/等风险分仓/ρ闸）——L08 复飞矿道案卷
session: zc-l08-20260927
---

# F73 · A/B 联赛与分仓

> 总册行：H 段 F73，状态 design（晋升判据执行器未写），P0。
> 本卷=09-27 复飞复测。基册=03_promotion_ab/02_ab_league.md（PR-A 09-25 挖干）。**与 g_backtest_gpu 带对表结论先行：g 带卷族实为 F58-F69（01_f58..12_f69），带内无 F73 卷**——F73 design 态的对表修正依 PR-A 册+本日复核（见骨架勘误）。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | c1_backtest.sim_pocket_daily（equity 序列，PR-A 09-25 实测 267 行）；c1_backtest.strategy_screen；config/standards.yaml 三尺（STD-SIM-ACCESS-001 frozen+suspect、002 v2 frozen 裁定#337、STD-SWITCH-001 draft）；promotion_advisories/*.json（**09-27 ls 实测：目录仍不存在=上游零流入维持**） |
| 下游消费 | F74 转正门（challenger 上位建议）；league_archive 终审证据链；Owner 6 个月终审门（due=2027-03-21） |
| 自动化触发 | **零排产维持**：config/schedule.yaml 无 league 条目；schtasks 09-27 全查零 league 命中；全件 manual CLI；月度快照纯靠人记得跑 |
| 真源与注册表 | config/league_registry.yaml（09-27 实读：**members: [] ×2 组、review_scheduled: false ×2 维持空场**）；裁定#392 D 批（09-21 TC-11 件1 施工授权）；exam_policy.md（裁定#365） |
| 门禁与质量尺 | 判定器复用 promotion_combo_gate 零修改；挂单回写 CAS（safe_write_text）；档案三指纹缺 git hash 硬失败；复原三态 faithful/restorable/unverifiable |
| 当前运行状态 | **基建绿/空场红（维持）**：09-27 ls 实测 data/backtest_artifacts/league/ **仍不存在**（月度快照从未跑过）、promotion_advisories 目录不存在、零参赛者零挂单——联赛建成至今未开赛（PR-A 判定维持） |

## 二、子模块三级枚举

1. **注册表面**：league_registry.yaml v0（组 A=champion/B=challenger 初始席位；review_policy.window_months=6+judge+judge_std_id=001（尺漂移张力点）+snapshot_dir；members/archive_path/review_scheduled 回填位）。
2. **代码面（PR-A 实测五件+判定器）**：league_registry.py（MOD-AUTO-L11-REGISTRY，201 行，schedule_review CAS）；league_monthly_snapshot.py（210 行，sim_pocket_daily 按组 equity→snapshot-YYYYMM，断供降级记缺口）；league_archive.py（284 行，三指纹打包）；league_restore.py（180 行，只核对不执行）；promotion_combo_gate.py（骨架 §7/§8 首件，被登记为终审判定器）；测试 65 passed（PR-A 09-25 实跑 1.42s）。
3. **缺位件（机制三件零代码）**：league_judge 成对判定执行器（DSR 显著性+持续 6 月+容量滑点+降级标记）；ρ>0.7 相关性闸执行器（尺上双登记、全仓零消费者）；league_allocator 等风险分仓（1000 万模拟仓跨组分配）。

## 三、接线四态独立复核

- **骨架勘误（一）**：总册 F73 标 `design（晋升判据执行器未写）`/分工册"从未立册"——**已过时**（PR-A 已证）：09-21 TC-11 件1 已建基建五件+测试绿。精确态=**基建 built/机制空场**（既非 design 未建，也非可开赛）。今日清单 §1.4 仍列 F73 于 design 5——**两处都应改 partial**。
- **骨架勘误（二）**：g_backtest_gpu 带内无 F73 卷（其 12 卷=F58-F69）；F73 状态对表唯一实源=本卷+PR-A 册，防"g 带已挖 F73"误引。
- **骨架勘误（三）**：四件 league_*.py [BLUEPRINT] 锚指向 mining/11_联赛/作业簿——文件不存在（PR-A 堵点 7，维持未修）。

## 四、缺口清单（PR-A 堵点维持+依赖序）

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | 空场：零参赛者 | 首位参赛者走通 E4 幸存者→intake sim 流转→advisory→入 A 组+archive（依赖 F74 链路） | **P0** |
| 2 | 晋升判据执行器未写（成对判定零代码） | 新写 league_judge（msprt e-process+STD-SWITCH-001 pair_decision_engine+BHY q=0.10）；前置 draft→frozen | **P0** |
| 3 | ρ>0.7 闸执行器未写（尺在闸无） | 并入堵点 2 同件 | P1 |
| 4 | 分仓 allocator 未写 | league_allocator 最小件；先对账 pf_alloc SIM_DAILY 防双建 | P1 |
| 5 | 尺-器漂移：combo gate 硬编码 v1（#306 suspect）vs v2 frozen | combo_gate 改读 standards.yaml 动态取尺（与 F74 堵点 1 同批） | **P0**（不修尺，终审用"数学不可过"v1） |
| 6 | 月度快照零排产+终审挂单无提醒 | 与 F72 月度三件合并一张月槽工单（1h） | P1 |
| 7 | 蓝图锚悬空（mining/11_联赛 不存在） | 补作业簿或改锚 08 册（半小时） | P2 |
| STALE 13/假绿 5 | **不属 F73**（归 F77 §四） | — | — |

## 五、自审闸三态

**挖干（复核维持）**：PR-A 六向全证引用+本卷四项当日活探（双目录不存在/members 空/review_scheduled false/schtasks 零命中）——空场判定 09-27 维持，无态变。三态=**待施工（基建 built/机制空场）**。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
ls data/backtest_artifacts/league 2>&1; ls data/strategy_intake/promotion_advisories 2>&1   # 双不存在=空场
grep -n "members:\|review_scheduled:" config/league_registry.yaml                           # 全空
ls scripts/backtest/league_*.py scripts/backtest/promotion_combo_gate.py
grep -rn "correlation_gate_rho\|combo_corr_max" config/standards.yaml | head -4             # 尺在
grep -rln "correlation_gate" scripts/ src/ --include="*.py" | wc -l                          # 闸执行器=0
ls docs/_working/automation/campaign/mining/ | grep 11                                      # 无=锚悬空
```
