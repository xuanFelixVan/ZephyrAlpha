---
ttl: task_bound
session: st-construct-20261002
date: 2026-10-02
title: 施工总包五批战役台账
completes_when: 五批全落地+红蓝对抗+终报交付
---

# 施工总包台账（st-construct-20261002）— 承接 st-ffchief 三夜战役收尾

> 开工令：五批施工清单（分支终态/scripts 拆簇/看门加固/config 错峰/零散闭案）
> 环境变量：belt 两度楔死→杀净重拉复活；chaos2 复测+redblue 审查会话全程并发落件

## 第一批：分支终态清零 ✅

- 基线 18 条（dev+serializer×5+chaos×10+chief7+ffchief）→ **终态 6 条**（dev+serializer×5）
- chief7 worktree 66 脏面档案化（`.runtime/campaign_trash_20261001/worktree_salvage/st-chief7-20260928_increment/`：108KB patch+30 文件 sha256 manifest）后 remove；分支 tag `archive/session__st-chief7-20260928` 后删
- chaos×10 worktree+分支由并发 actor（st-redblue-review-20261002）先行清退，我方复核确认零丢失（全 dirty=0/全并入 dev）
- ghost 心跳 10 件清理（chaos-st-01..10）；注册表注销 chief7/ffchief-20261001/ffchief-20261002 三死会话
- 接管台账：chaos 条目已由 redblue resolve；本批物理清退完成其处方

## 第四批（提前执行）：RESOURCE-SCHEDULE 错峰 ✅（q-0001=514e94a6a9）

- 实测冲突（非令文口径）：23:30-23:45 窗五槽数据槽+factory_lane_c 同窗，峰值和 13.5GB>10GB（四笔 block）
- 裁定：cross_validation 23:15→00:15、consensus_crosscheck 23:30→00:30（+1h 跨午夜，同 dow 平移；保 ECB 发布后窗/ integrity_check 后错峰/晚间重建依赖）——机械 -2h 会砍断 ECB 依赖，故不采
- 二次冲突（q-0003 落地闸现形）：22:00 窗 10.5GB（research_nightly 20:30+2h 跨 22:00 叠加）→ research_nightly 20:30→20:00（22:00 准点退场；与 daily_event 同池保 15min 间隙；lane_g 22:30 槽依赖不变）
- 闸三查终态：mem_ceiling=0 / pool_concurrency=0 / overlap_group=0；调度器 17:21 实弹重启吃新配置（32 槽装载+四数据源健康绿）
- 前总包三件 config 在途再生面随批补投（governance_operations_map/resource_profile/tool_inventory）

## 第二批：scripts/ 五簇拆分 ✅（C1=a4b503a163；C2-C5=q-0012）

- C1：register_*×32 → scripts/tasks/register/（register_process_reaper_task.ps1 因宪法 RULE-GUARDIAN 真源直引+AGENTS.md 保护路径留位）；C1 落地缺带 31 条老路径删除边（HEAD 双副本缺陷）→ 并入 C2-C5 批补齐
- C2-C5：run_*×11→tasks/run、check_*×6→checks、杂散 8→installers、一次性取证 14→_archive；check_naming_convention.py 原位保留
- **scripts/ 顶层 148 → 80**（≤120 达标，GOV-DOC-018 双口径合规）
- 引用改写三形态（正斜杠/单反斜杠/拼接）+生成器 glob 双目录五处+测试常量同步； inadvertent 906 文件 ruff format 事故=纯格式无语义（详见事故录）
- 计划任务动作重注册：11 任务经创建者正门+XML 补丁；8/10 已正；2 个 Owner 门位件（TradingWatchdog SID 断裂+OneShot0915×2 ACL）留 pending_owner
- 机械修补：ensure_ai_wrapper 邻居查找双位兼容（git_safety_wrapper 宪法锚定 scripts/ 根）、guard_tasks 拼接点、run_boot_sla_probe 存量 lint（I001+BLE001×3）
- depgraph --output-db --force 重扫（1778 模块 0 失败）；manifest 再生

## 第三批：BeltDaemon 看门加固 ✅（件落 q-0012）

- 病灶实弹取证：belt 两度楔死（租约 18:24 取得后 70+ 分钟零续租、工人 18:29 全停；seq 楔死重演）——杀净重拉配方复活（36228→4336）
- 治本件 scripts/installers/belt_watchdog.ps1（裁定七两段判活：心跳文件 O(1) 先行（pid 活+wall_ts<600s）→ CIM 兜底；双证死才 spawn）
- 任务动作已改指新脚本；验证（杀守护→60s 内拉起且仅一只→观察期无堆积）在终验段执行
- 序列器 worktree 暂存残渣（前代袋半程暂存）按台账域三 #20 scratch 配方清零（五树 0 dirty）——落地扫描面污染源消除

## 第五批：零散闭案

| # | 项 | 终态 |
|---|---|---|
| 5.1 | 估值 v2 退役 | ✅ 并发执行者已 RENAME quar_20261002（0 行+零写入方+零消费方复核）；本包更新 known_data_gaps→retired_quarantine，**10-09 隔离期满 DROP**；建腿=Owner 门 |
| 5.2 | mark_logical 核验 | ✅ register(logical=True) 形态核验补丁（chief 词形 OR 活心跳守护，fail-open 降级+审计；session_concurrency.py）+ tests/security/test_session_registry_chief_form.py 五测全绿 |
| 5.3 | migration 13 pending | ⚠️ 定性=从未执行的拆分计划（老文件在/新路径无），冻结册只许 pending→done → **Owner 项**（执行拆分 or 修守卫），pending_owner.md |
| 5.4 | tmp.18376 CAS 残件 | ✅ PID 复用判定（现主=ZCode 桌面）+内容=独有中间态→归档 campaign_trash_20261001/cas_residue/；scripts/ 顶层污染消除 |
| 5.5 | PROTECTED 溯源 | 📋 登记项：ruling 册一行路径修复留手待载体 + [ARCH-APPROVAL] 读数分歧（裁定八不紧急）→ pending_owner.md |
| 5.6 | 计数漂移回写 | ✅ registry_master_index 重生成（62→61，生成器权威口径+REG-DATAFLOW-001 双物理文件告警留痕）；ROOR 结构化字段核验通过 |

## 事故与学费录

1. **906 文件 ruff format 误扫**：sed 转义失败→ruff format 空参跑全仓。定性=纯格式零语义；回退反而有吞他会在途面风险→理性止损保留，如实入账。学费：危险命令参数构造必须先 echo 展开。
2. **tmp 清单链污染**：c1_final.txt 内容漂移致 q-0002 袋错装。学费：提交清单永远从 git 现状重建，禁 tmp 文件接力。
3. **共享索引竞争**：porcelain 采样瞬态+chaos2/redblue 并发落件交错。学费：袋在途时不动索引；批量动作后重读现场。
4. **rename 对断带**：git mv 的 R 对在袋化时只带 A 半边（网关按 --files 快照）——所有搬迁批必须显式验证 HEAD 无双副本。
5. **requeue 快照通道缺陷**：requeue 重快照把主区脏面卷入落地临时索引（连坐域二 #10 未根治的实锤）——同清单全新 enqueue 即过；requeue 只适用于无脏面干扰场景，已登记议题。
6. **ALGO-FLOW 锚位置**：external 锚必须在 module docstring 内部，头部注释区无效。
7. **GATE-SELFDOC 无实现**：宪法条款全仓无对应检测器逻辑（legacy_v1 豁免验证失败实证）——登记 P2 债。

## 红蓝对抗

（终验段回填）
