---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 外部审查报告交付并经 Owner 查收后归档
---

# 外部审查计划 — st-mastertc 夜战建设全面审计（2026-10-07）

> 审查机构会话 `st-extaudit-20261007`（独立/对抗性/只读）。被审对象=总包会话 st-mastertc
> 于 2026-10-06 夜~10-07 对桌面 126 张未关闭卡的建设。本计划为开工前先交件（指令§五.1）。

## 〇、审查姿态与合规自述

1. 全程只读：仓库代码/门禁/数据面零改动；唯一可写产出=`docs/_working/external_audit_mastertc/`（10 文件，
   creation_token 已登记 capability `ext_audit_20261007`，提交走 `git_commit.py` 正门）。
2. 主区直改属宪法 RULE-WORKTREE 降级场景：依据=外部审查指令明令产出路径+正门提交流程，
   提交带 `--allow-non-worktree` 留痕（Owner 已授权通道），GW 计数进周审计。
   【路径更名披露】指令原定路径 `docs/_working/external_audit_20261007/` 被 R5-DIGIT-SUFFIX 门
   正确拦截（数字后缀目录名违反 SSoT 定名纪律，批1 提交实测被硬拦），按 L0 同款治本先例
   （master_tc_20261006→master_tc_night，600abe9991）更名 `external_audit_mastertc/`；
   capability 册内本会话 10 条 token 随批0b 同步重指新路径（零增零删条目）。
3. 不采信任何一方自述（作业簿/台账/交付报告），一切结论以 git HEAD 实证为准；
   引用台账处注明"自述，未采信/已实证"。
4. 他会在途面（st-tests-chief/st-cure-p01/st-vm12final/st-mx07 等，工作区 177 处漂移）不计入被审对象；
   审查自身不碰他会话锁与 staged。

## 一、被审集锚定（开工时点 HEAD）

- 匹配 `git log --grep=st-mastertc` = **46 提交**（含 2 条他队提交仅在正文提及 st-mastertc：
  7e6f66d055/e5118cd455 属 [GW:st-mx07-L4]，剔出被审面→**44 条为被审主体**）。
- 会话分支 23 条（session/st-mastertc-*）：21 条已并入 dev；**`st-mastertc-l8`（tip cf5b6ddcf7）
  与 `st-mastertc-mine`（tip f73bf8714d，W1 挖矿初版、疑被 mine2 取代）未合并**。
- 关键哈希锚：裁定#488=6555113e56（ruling_registry.yaml +33 行，HEAD 在册已实证）；
  自告重点批=90d8e3b33c/abed5f7a1f/f95c1cd784/02fc4d72a4/b20899c870/44f445c47e/e5f0f9a5ee/
  4e43d191a3/bb6a03f5c1/d2fb212a22/6bb3c7e940/0e6a76bbcb/739b6fe466/831a35b30a/eb358e0cfd/
  a621b97765/ccbe57e6f3/fa165c56a1/7e4a2949f0/01bf541fbb/0b38f7ca7c/65e48209a4/24635c2309/
  3f752debdf/6072df11ef/54ad7021e9/0d1d6d29a6/600abe9991/45c1f0b224/cdd1246dc6/de50314561 等。

### 预检硬事实（审查 kickoff 即已实证，各车道复核展开）

| # | 事实 | 证据 |
|---|------|------|
| F1 | 信号三模块 event_axis/swing_sequence/resonance_pair 在 HEAD 全树**零命中**（自告"袋 recover-0005 完成"） | `git ls-tree -r HEAD --name-only \| grep -E "event_axis\|swing_sequence\|resonance_pair"` =空；event_axis.py 仅 staged 未提交 |
| F2 | L8_retire_ai 作业簿目录在 HEAD 缺席，仅存在于未合并分支 | `git ls-tree HEAD docs/_working/master_tc_night/lanes/` 无 L8；`session/st-mastertc-l8` 树有 |
| F3 | l8 未合并（merge 自述被主区脏面拒，"待清偿后 merge"至今未执行）；mine 同 | `git merge-base --is-ancestor session/st-mastertc-l8 dev` =非祖先；mine 同 |
| F4 | chart_resonance_prereg.yaml/search_space_prereg_t3b.yaml 均在 HEAD（工作区 D+?? 态属他会话在途） | `git ls-tree HEAD` 两路径各 1 blob |
| F5 | 交付报告自述循环检查终判定曾为 ISSUES(3 项移交)，后经 final2 班闭账改判"连续两轮零失败成立" | 交付报告.md §W3/W4/终版判定（自述，待 B 车道实证） |

## 二、车道编成与全景图映射

| 车道 | 审计类型 | 对照全景图 | 被审重点 |
|------|---------|-----------|---------|
| A 纵向主链 | 链路真实性 | 图12 data_supply_chain_map / 图9 strategy_production_map / TDM / 132 环节总表 | 三信号模块、tech_factor、grid_stats/lead_lag、fill 写者、reaper 现算化——图上挂点/[CONSUMERS] 可达性；F1 疑点定谳 |
| B 治理横向 | 门禁执法实证 | 图10 治理地图 / 图16 立法流图 / gate_registry | C97/C157/C128/C443/C338/C304 真执法（触发路径实测）；C27"待自动翻转"机制真伪；循环检查两轮零失败自告复核 |
| C 提交链/队列 | 基础设施闭环 | 提交队列+裁定册 | C02 死信 45 分诊抽 10 复核；恢复班 6 袋落地件逐文件 HEAD 核实；死信 1548+ 官方归档子命令闭环；C152/C300 |
| D 回测考试 | 规格符合性 | 图9 工厂 / ext_01 规格 | G-D 引擎四件套 vs ext_01；prereg 冻结 diff==0 复测；READY_NOT_FIRED 未点火；C216 剪发夏普口径 |
| E 退役+AI | 纪律与落地面 | 图16 立法流 / lifecycle | 退役批零删除纪律；C84/C85 消费实证；l8/mine 未合并面内容清单与"完成"定性 |
| F 文档台账 | 考古真实性 | 图14 construction_workflow / alignment_checklist | C129/C473/C61"原件蒸发"声明逐一考古；C192 57 行/C266 抽 10 行对真源 |
| G 未完成 53 卡 | 分类合理性 | 环节总表 120 卡挂接 / 132 总表 | 桌面两清单逐条三分类复核；#488 A/B 段越权审查；重点卡 C02/C33/C34/C11/C61/C84/C136/C314/C394/C27/C441/C78/C205 |
| H 过渡/不必要工程 | 内收判据 | ROOR / 环节总表 10 条新立卡 | 今晚全部产出跑四判据；第二真源清查；占位骨架；新模块消费面 |

## 三、判据（指令§四原文，全车道统一）

- 真完成 = HEAD 字节在 + 消费/执法链可达 + 与全景图挂点一致。
- 假完成 = 台账称完成但 HEAD 缺/无消费/挂点错。
- 过渡工程 = 临时方案未声明"过渡"或有永久化义务未履行。
- 不必要工程 = 违反内收四判据之一（重复真源/零消费/可派生未并/跨域误并）。
- 遗漏 = 全景图环节有义务、施工无卡、Owner 门位无遮挡。
- 证据规范：每条 verdict 附命令原文+读数或 commit 哈希；P0（假完成/断链/违宪）单列必修清单。

## 四、产出与提交通道

1. 本计划（先交）→ 八车道 findings（lane_a~h）→ 00_audit_report.md（挂点矩阵+五问+P0/P1/P2+53 卡复核改判）。
2. 提交三批：批0=token 注册表（已就绪）→批1=本计划→批2=findings+总报告；均
   `git_commit.py --session st-extaudit-20261007 --files … --allow-non-worktree --enqueue`，批后
   `git log -1 --name-only` 核归属。
3. 审查红线：只读；发现只登记不代修；结论存疑降级"待证"。
