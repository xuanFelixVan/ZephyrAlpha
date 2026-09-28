---
ttl: task_bound
title: L12 案卷 F119 — 双引擎自动化总计划（Qoder 白班×GLM 夜班×GPU 专道 L0-L6 接线四态）
session: zc-l12-20260927
---

# F119 双引擎自动化总计划（M 段横切 X4，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | F83 自动化班底（总册 F119 行上游列）；Owner 口述愿景与免费窗硬边界（Qoder 至 09-30 / GLM 夜班至 10-08 / GPU 09-25 点火 59h→09-27 23:00 收窗） |
| 下游消费 | 排班执行：L0-L6 七 lane 全部按本册 §3 真活清单开工；在册既有自动化四件（第二链每日核验 07:15/battle_map 周一 09:00/模拟盘钱包 19:30/candle_pattern DROP 12-15）禁重复建设 |
| 自动化触发 | 本册自身=task_bound 文件桥（frontmatter completes_when: 2026-10-08 收官总报落账后归档）；其调度的自动化面=Windows 计划任务+schedule.yaml 槽（归 F76-F85/M5 车道） |
| 真源与注册表 | `docs/_working/cmd_ledger/automation_master_plan.md`（session st-autoplan-20260924，date 2026-09-24，自声明"调度唯一真源"）；方法论上游=`sop/automation_sop/automation_crew_policy.md`（班底值守 SOP 族真源） |
| 门禁与质量尺 | 追加记录必用 safe_write_text CAS+lock_files acquire（册内铁律）；提交唯一正门 git_commit.py --enqueue；§6 铁律节（并发战争教训浓缩，违者夜班仲裁回滚） |
| 当前运行状态 | **绿但临期**：册在盘、L0-L6 结构完整、§2 关键路径四件（GPU 三案裁定/prereg v2 冻结催办/W-M1 双轨观测/队列积压分诊）在轨；**GPU 收窗=今日 23:00**（frontmatter 里程碑行） |

## 二、子模块三级枚举（引擎席 → lane → 结构节）

1. 引擎三席（§0 硬边界表）：Qoder（千问 3.8 Flash 白班，15-20 子代理，至 09-30）｜ZCode 夜班（GLM-5.3 Flash，~10 异步对话，23:00-09:00，至 10-08）｜本机 GPU 3090（L3 专道唯一持有，单对话）+总指挥付费窗（ZCode 白天轻巡检，避 14:00-18:00）
2. 七 lane 分工（§1 写域互斥表）：L0 总指挥（cmd_ledger 写域）｜L1 提交优化｜L2 审计对齐（cleanup_final+audit_all 面）｜L3 GPU 专道（e2e_integration LEDGER）｜L4 原问题 283 消化（meta_question_answers 面）｜L5 数据源/因子/策略挖矿（chain_piling 面，prereg 册只读）｜L6 AI层/模拟盘/压测收尾（pipeline_final 面）；sid 规范 st-qoder-<lane>-<MMDD>-<NN> / st-night-<MMDD>-<NN>
3. 结构节：§0 引擎与时间窗｜§1 分工与写域互斥｜§2 今晚关键路径｜§3 真活清单（3.1 夜班 GLM 桶/3.2 起 Qoder 卡）｜§4 日历逐日分派｜§5 Qoder 白班任务卡｜§6 铁律｜§7 呈 Owner 裁定项｜轮次记录

## 三、接线四态独立复核

| 件 | 四态判定 | 证据 |
|---|---|---|
| 总计划册本体 | **已接线（built）** | 册在盘、七 lane 表完整、真活清单全部带锚点（本册未登记的活不开工纪律在文） |
| 与 automation_crew_policy（F116 automation 族）的关系 | **双册分工可辨但无互引行** | SOP 族=永久方法论（双引擎两班制/夜班 9 席/切碎四件套）；总计划=task_bound 战术排班；两册各为其真源但总册未引 SOP 族锚（见勘误 2） |
| GPU 专道（L3） | **临期收窗** | §0 里程碑"09-27 23:00 GPU 收窗+W-M1 72h 对账"——今日为收窗日，本卷不代裁收窗动作 |
| 生命周期（10-08 归档） | **登记在册（自愈设计）** | completes_when 字段明示"收官总报落账后归档"——册退役有触发条件，非悬空 |

## 骨架勘误

1. 总册 F119 行状态=built 无括注，但真源册 frontmatter **ttl: task_bound + completes_when 2026-10-08**——built 态的"唯一真源"是有死刑日的临时册；10-08 后 F119 的真源锚将悬空，总册行宜预注"真源归档后继任真源待 Owner 指定（候选=automation_sop 族或 cmd_ledger 收官总报）"。
2. 总册 F119 行上游只写 F83；方法论族 automation_sop（automation_crew_policy）是其恒定上游真源，建议总册行补该锚。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 真源册 10-08 归档后的 F119 真源接任 | Owner 在收官总报批文中一并指定继任真源（随 §7 呈裁项走） | P1 |
| 2 | 总册 F119 行缺 task_bound/继任括注 | 骨架侧下次修总册时补一行括注（热文件 CAS） | P2 |
| 3 | 总计划册与 SOP automation 族无互引 | automation_crew_policy 或总计划册一侧补互引行（单侧即可，净零） | P2 |
| 4 | 今日 23:00 GPU 收窗对账（W-M1 72h） | 归 L3/L0 车道本日夜执行，本卷只登记不代做 | P1（时效） |

## 五、自审闸三态

**挖干（册结构与生命周期态）**：L0-L6/引擎席/结构节全枚举 ✅ frontmatter 生命周期字段实证 ✅；**待裁**：归档后继任真源（Owner 门位，呈裁项属性）。

## 六、复跑命令

```bash
head -14 docs/_working/cmd_ledger/automation_master_plan.md       # frontmatter ttl/completes_when
sed -n '17,43p' docs/_working/cmd_ledger/automation_master_plan.md # §0 引擎窗+§1 七 lane 表
grep -n "^## " docs/_working/cmd_ledger/automation_master_plan.md  # §0-§7+轮次记录
head -8 docs/01_policies_and_standards/sop/automation_sop/automation_crew_policy.md  # 方法论族真源
```
