---
ttl: task_bound
completes_when: 待批清单全部获 Owner 批复处置完毕
---

# 自动化联动线会话纪要（st-autolnk-20260917，大白话存档）

> Owner 指令："你全部先落盘吧，不然以后忘了"——本件=对话大白话版的书面存档+状态账本。

## 一、查出来的三个真相

**1. "把挖矿从云 API 切到本地 Ollama"——早就做完了。**
翻了代码：周六挖矿、假设翻译这些环节，调的本来就是本机 Ollama（qwen3:8b），没花云 API 的钱。剩余工作不是"切换"，而是：①挖矿从每周六一次扩成每晚也跑（GPU 闲着）；②试 14b 大模型是否比 8b 挖得好，一次对比定版。

**2. GPU 为什么闲着：从来没给它安排过活。**
整条工厂流水线（挖矿→考试→入库）全是 CPU 工种。唯一用 GPU 的活（Kronos 训练）是一次性任务，2026-09-16 完工后就没了。

**3. 排班系统曾漏看 12 个天天在跑的任务。**
备份、CH 数据库合并、指标库夜补、看门狗……不走标准注册流程的任务系统看不见。后果实例：CH 周六 03:30 大合并与排班表周六 03:00 校准任务撞车，系统此前无法发现。

## 二、已干的事（commit fe8fce25，8 文件）

1. **补注册 12 个任务进排班系统**（走生成器正门，未手改文件）：60→72 条，--check 零漂移，模块测试 8/8 绿。顺带修正 F06Grid 身份（实为 cpu_heavy 重活）。
2. **5 份文档落盘 docs/_working/automation/**：总方案 v1 + 4 张 GPU 施工单（夜间挖矿/Kronos 全市场打分/SFT 回灌链/RL 训练）。
3. **后继增补**：业务层全自动骨架 v1、决策骨架挖矿报告（见同目录）。

## 三、抓到的家务事（待 Owner 一句话）

> **4 个测试遗留任务（9/15、9/16 建）没关，每天 15:35/17:30 把整条工厂流水线原样重跑一遍**——纯烧机器。删除/禁用/转正 = Owner 拍板，AI 未动。

## 四、待批清单（全量）

| # | 项 | 等谁 |
|---|----|------|
| 1 | 4 个测试遗留任务处置 | Owner |
| 2 | F06Grid/C4Exam 周六 14:00 同刻错窗 | Owner/资源线 |
| 3 | CH-OptimizeMerge 立 register ps1+任务名规范化 | Owner（改活任务） |
| 4 | GPU-01 夜窗挖矿批+档位 A/B | 等收工施工 |
| 5 | GPU-02 Kronos 批量打分（含预测表+B-007） | 施工+B-007 |
| 6 | GPU-03 SFT→GGUF 回灌首跑 | 走冲突闸随时 |
| 7 | GPU-04 RL trainer 施工+真训练 | B-007 |
| 8 | 外网论文/策略搜索 agent 启用 | Owner |
| 9 | 全链晨报生成器施工 | 等收工 |
| 10 | tilib 积压池排程化 | 传值 tilib 线 |
| 11 | WeeklyRest 周日休息窗 | Owner（涉关机） |
| 12 | 搜索设备 v0 开工 | Owner 已口头令"先把所有设备建起来"（见骨架 v1 §4） |

## 五、审计六发现（登记不代修）

①F06Grid/C4Exam 周六 14:00 同刻双重活 ②CH 周六凌晨同窗（补注册后闸可见）③nightly_sentiment 双真源（槽位 08:20 vs 任务 22:30）④见"三" ⑤sch_pattern_mining 有源无任务 ⑥周六 06:00 双备份同刻。

## 六、拍板落地处置记录（2026-09-17，Owner"全部拍板"批）

| 处置 | 证据 | 状态 |
|------|------|------|
| 禁用 4 个测试遗留任务（C4Exam_Full0916 / C4Exam_OneShot0915 / FactoryLaneC_Full0916 / FactoryLaneC_OneShot0915） | State: Ready→Disabled（逐一经 Get-ScheduledTask 复核） | ✅ 已执行（禁用未删，可逆） |
| 退役 22:30 NightlySentiment（双真源归一，Owner"这个同意"） | Ready→Disabled；08:20 调度器槽位保留（当日窗口+近 7 日补漏，覆盖更全） | ✅ 已执行 |
| 注册 ZephyrAlpha_WeeklyRest 周日休息窗（Owner"全部拍板"批） | state=Ready，trigger=Sunday@05:00；保险丝=`.runtime/weekly_rest_skip.flag`（通宵班写入即跳过当周）；120 秒宽限，abort=`shutdown /a`；日志=`.runtime/logs/weekly_rest.log` | ✅ 已执行 |
| 时间修正：04:00→05:00 | 原定 04:00 撞 tilib 02:30 夜批（申报 120 分钟≈04:30 完），顺延一小时 | ✅ 修正后注册 |
| 已知代价备案 | 周日 06:00 DailyBackup 跳过一次（机器已关，周一 06:00 照常）；周六 06:00 VHDX 备份不受影响；周日 catchup_guard/采样器回写各停一班 | 备案 |

新件：`scripts/ops/weekly_rest_guard.ps1`（新建，纯 ASCII，skip 保险丝设计）。
