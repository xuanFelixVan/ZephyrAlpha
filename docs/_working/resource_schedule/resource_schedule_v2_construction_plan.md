---
ttl: task_bound
completes_when: >-
  本方案 §4 各期（P0-P5）全部终态=✅（每项标注 commit 凭据），且 §6 验收判据
  逐条实测通过；红蓝对抗（§7）两轮问题=0 后结案归档。
creation_note: 新建工作文档（CREATE-GUARD token 同批登记 capability_canonical_file_registry.yaml）
---

# 资源排班表 v2 施工方案（挖净联动·双向同步·AI 重排班·覆盖强制）

> 创建：2026-09-16 ｜ 会话：st-govmap-20260915 ｜ 基线：v1 四件套已落地（aa253167d9/3cde9547da/6e67a84ec9）
> 真源方案：docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md（v1，§10 已闭环）
> 本方案 = v2：Owner 三目标（①双向自动同步零漂移 ②AI 重排班并更新模块 ③覆盖全完整+未来强制登记）

## 1. Owner 目标 → 机制映射（设计公理）

| 目标 | 公理 | 落地件 |
|------|------|--------|
| ① 不漂移不幻觉 | **单真源+派生件**：时间只活在真源（schedule.yaml/ps1 触发器），表=生成器抄来的；"双向同步"=改哪头另一头自动跟上，禁止表↔模块互抄 | P2 写回工具（排班方案→真源文件 diff 提交→再生→闸验）；再生排产化（P0）让"改真源→表跟上"零人工 |
| ② AI 重排班+反向更新模块 | 排班=对真源文件的受闸修改：AI 产方案→C-8 增强闸硬校验→gateway 提交真源→注册表/周历再生→模块下次触发即用新窗 | P3 第一轮静态重排（申报值），P5 第二轮实测校准（measured p90） |
| ③ 完整覆盖+未来强制 | 三源再生结构性覆盖一切"自动启动"；缺口补：第 4/5 真源源（drill_schedule 收编+schtasks 实测对账）、池词表校验、受闸声明反查 | P1 数据统一+词表闸，P4 覆盖收编 |

## 2. 挖矿结论（2026-09-16 全仓调研，实测非文档转述）

### 2.1 基线实况修正
- 注册表已 **72 实体×18 字段**（active 40/planned 31/retired 1）；真源分布=方案文档 31+schedule.yaml 21+ps1 20。
- **measured 回填仅 3/72**（57+ samples=0）；21 个 data_slot 实体因"共享宿主槽位归因跳过"永久 null。
- **告警链第一因断**：`.runtime/ops_notifications/` 不存在——无任何计划任务触发注册表/视图再生，"闸→告警→promotion"整条链等手动。
- 周历视图 rw-data.js 已 stale（02:29 vs 注册表 17:14），无 freshness 闸覆盖。
- ROOR REG-RESCHED-001 entry_count=60 ↔ 实 72 漂移（CR-007 会抓）。

### 2.2 联动机会清单（L，按价值排序）
| # | 机会 | 内容 | 期 |
|---|------|------|----|
| L-1 | 孵化台账×采样流 pid join | ledger.jsonl（pid/parent/owner/寿命，332 行活跃）⟷ resource_samples/*.jsonl（rss/cpu）按 pid 关联：解锁 21 槽位归因、measured 3→40、给漂移检测供"申报寿命 vs 实测寿命" | P1 |
| L-2 | 再生排产化（吃自己狗粮） | generate_resource_profile_registry --check + generate_resource_week_view --publish-alerts 立为 2 个 register_*.ps1 计划任务并自登记进注册表 | P0 |
| L-3 | 运行时准入三件合一 | capacity_budget.py（并发/WIP 配额，零引用）+ api_cost_governor（令牌桶，零引用）+ infra_runtime/resource_scheduler.admit()（准入接口，零引用）→ 由注册表 pool/est_duration 供配额，补排班表"运行时下半身" | P2-c |
| L-4 | global_state_aggregator 系统健康域绑定 | 采样器摘要+incubator 水位+gpu_monitor+reaper 战果注入其 system_health 采集器（只读零风险，域词表已闭合） | P2-d |
| L-5 | drill_schedule.yaml 收编=第 4 真源源 | 应急演练排程结构就是排班表（DOM+月列表），生成器加解析器归一 cron——白捡 3 实体+防第三种日期法野长 | P4 |
| L-6 | map_node_id 激活（表↔作战地图） | 72 实体该字段 100% null=最大未启动接口；battle_map 已挂 GATE-BATTLE-MAP-ALIGNMENT，灌数即双向受验 | P4 |
| L-7 | gguf_vram_budget period_quotas 同构合并 | 已存在的第二张时间窗资源表→并入 gpu_default 组显存天花板来源；顺带修 auto_runtime_core:774 硬编码 21.6 不读表（违反该 YAML 自订纪律） | P1 |
| L-8 | exam_trigger_scheduler 收编 | 唯一漏网"自动触发重活"（新模型入库即考试）；其盘中守卫改引 E0 classify_window（消 C-3 双实现） | P4 |
| L-9 | 资源晨报生成器 | 读注册表+台账+样本流+通知板→markdown（零新数据源） | P5 |
| L-10 | degrade_to_api→status=deferred→deferred_queue | 显存超预算运行时自适应改排（复活 deferred_queue 死件） | P5 候补 |

### 2.3 冲突/双真源风险清单（C）
| # | 冲突 | 处置 | 期 |
|---|------|------|----|
| C-1 | 压力阈值五口径（70/80/90%、0.75-0.995 比率、10GB 绝对值、incubator 硬编码 85%、alert 8GB） | ④⑤落进 resource_optimization.yaml（消硬编码）；v2 统一口径仍挂起（v1 裁定不变） | P1 |
| C-2 | VRAM 21.6 双写（YAML 真源 vs 代码抄数） | 代码改读表 | P1 |
| C-3 | 盘中判定两套（E0 vs reflexion.is_intraday） | exam_trigger 改引 E0 | P4 |
| C-4 | cron 解析三套（croniter/api_server 自写简化版"够 14 时段"实际 21/生成器 dow 归一） | api_server._next_cron_run 改读周历数据或换 croniter | P1 |
| C-5 | E0 失效向不一（闸 fail-closed vs api_server fail-open+审计） | 闸缺席时 resource_schedule_alerts 主动告警（现静默） | P0 |
| C-6 | "资源调度器"四同名认知风险 | path_ownership_map 写明"时间维（四件套）vs 空间维（准入件）"分工 | P2 |
| C-7 | **pool 词表两套：19 实体挂 `light` 幽灵池**（执行器只有 default/heavy/realtime/intraday_*，daily_crypto 事故自证） | 生成器加池词表校验+登记入 capacity_params.yaml 对账 | P1（**最高优先——19 实体在错误池上排班**） |
| C-8 | **同刻冲突结构盲区**：check_overlap_group 只查同组→F06Grid vs C4Exam 周六 14:00 同刻双重活永不报 | 补"同 pool 同窗并发"跨组检查（复用 check_mem_ceiling 累加数学） | P2（重排班前置） |
| C-9 | ROOR 条目漂移 60↔72 | registry_master_index 再生顺修 | P0 |
| C-10 | 视图无新鲜度闸 | derived-freshness 检查（rw-data.js 内 registry_sha256 字段现成） | P0 |
| C-11 | 申报受闸 vs 代码实闸脱节（lane_b 无 check_gate、sch_pattern_mining 有源无任务=幽灵登记） | "ps1 声称↔schtasks 实际"差集对账（并入 C-15 第 5 源）+声明-代码反查 | P4 |
| C-12 | 模块头 [CONSUMERS] 系统性失真（resource_optimization 写 phantom 实有 3 消费者等 6 件） | 随 CONSUMERS-ACCURACY 闸批修，本方案仅登记 | P4-c |
| C-13 | 收割职责三面重叠（reaper/start_scheduler 自清孤儿/incubator 拒生） | 注册表 notes_zh 互标+定义对账表 | P4 |
| C-14 | 考尺双模块壳（infrastructure/model_capability_exam 死壳 vs intelligence/model_profiling） | 壳退役（减法纪律，同 A5 先例） | P4 |
| C-15 | **计划任务侧无对账通道**：解析 ps1 静态文本，看不见 DISABLED/不存在/遗留测试任务重跑 | 生成器加 schtasks /query 实测=第 5 真源源，ps1 声称↔系统实际差集入 check_truth_drift 第二臂 | P1 |

## 3. 关键裁定（AI 自裁留痕，施工时登记 ruling_registry 同 commit 原子）

- **R-A 排班写回走真源不走表**：表 [GENERATED] 禁手工（红线），AI 重排班=对 schedule.yaml/ps1 的受闸 diff 提交；工具产 patch 不产表。
- **R-B measured 双轨不动**：样本流 append-only JSONL+表内快照 CAS（v1 §4.5-②裁定维持）。
- **R-C 幽灵池先治再排班**：C-7 未修前禁止执行 P3 重排班（池错→同窗求和全错）。
- **R-D planned 31 实体处置**：方案文档真源的 31 个 planned 实体保留 status=planned 不激活，但**不计入闸的内存并发和**（未排产不占预算）——防"纸面排班"挤掉真实重活。
- **R-E 排班权归 AI+闸，不归人**：人只保复核字段（peak_mem/est_duration/exclusive_group 可改），时间窗变更必须过闸——Owner 目标②的机制化表达。

## 4. 分期施工（并发波次）

### P0 卫生与闭环断点（独立，先走，~1 波）
1. L-2 再生排产化：2 个 register_resource_regen_*.ps1 + 自登记进注册表（第 21/22 个 sch_ 实体）+reaper keep 白名单登记；
2. C-5 闸缺席告警、C-9 ROOR 再生顺修、C-10 视图 freshness 检查（并入 --check 臂）；
3. 验收：`.runtime/ops_notifications/notifications.jsonl` 首次出现排班条目；rw-data.js 24h 内自动跟新。

### P1 数据统一与词表治理（P0 后，两子代理并发）
- **P1-a（L-1+C-15）**：采样器 pid↔ledger join（解 21 槽位归因）+schtasks 实测第 5 源+check_truth_drift 第二臂；目标 measured 覆盖 ≥40/40 active、幽灵登记归零；
- **P1-b（C-7+C-2+C-4+C-1④⑤）**：池词表校验收编 capacity_params.yaml+19 实体 light 池改挂真池（附 daily_crypto 事故复盘）；auto_runtime_core 读表；api_server cron 单源化；85/8GB 落 YAML；
- 验收：闸跑全量对账 pool 零违规；C-2 硬编码 grep=0；measured 断言测试绿。

### P2 双向同步闭环（依赖 P1，两子代理并发）
- **P2-a（C-8）**：闸加 check_pool_concurrency（同 pool 同窗并发内存和+同刻不同组冲突），三码→五码理由码登记同步告警桥+视图；
- **P2-b（R-A 工具化）**：apply_resource_plan.py——输入=AI 排班方案（task_id→新窗/新组），输出=schedule.yaml/ps1 受闸 diff+再生+周历重渲一竿子；经 gateway 提交；漂移检测双向化（表↔真源↔schtasks 三角对账）；
- **P2-c（L-3）/P2-d（L-4）**：运行时准入三件合一+聚合器健康域绑定（能力反查后定归口，若与 P2-b 冲突则后置）；
- 验收：改真源→10 分钟内表/视图/告警自动跟上（E2E 实测）；apply_resource_plan 产一版排班→闸 0 违规→回滚演练一次可逆。

### P3 AI 第一轮重排班（依赖 P2，Owner 目标②兑现）
- 依据：申报值+exclusive_group 先例+E0 日历+备份窗（DailyBackup vs WeeklyVMBackup 周六 06:00 同刻、F06Grid vs C4Exam 14:00 同刻必拆）→ AI 产全局错峰方案→ apply_resource_plan 写回→闸验→周历重渲；
- 产出：重排班前后对比报告（同窗峰值内存和 下降%、冲突数 N→0）入 docs/_working/resource_schedule/；
- 验收：C-8 新检查全仓零 finding；周历图肉眼可核错峰。

### P4 覆盖收编（独立可并发）
- L-5 drill 第 4 源、L-8 exam_trigger 收编+C-3 归 E0、L-6 map_node_id 灌数、C-11 声明反查、C-13 三面互标、C-14 死壳退役、C-12 随闸批修；
- 验收：真源盘点五类全收编（schedule.yaml/ps1/schtasks 实测/drill/事件种子），覆盖对账报告 100% 挂接或豁免登记。

### P5 实测校准第二轮（P3 后≈两周，攒够 samples 再做）
- measured p90 反校 est_duration_min/peak_mem_gb（申报 vs 实测偏差>30% 自动 flag）；L-9 晨报；
- 验收：偏差 flag 报告+校正批 commit。

## 5. 施工纪律（宪法挂钩）

- 每批：capability_lookup 留审计→depgraph 登记→gateway 提交→commit 后 name-only 核实；
- 新 .py 须大白话简介登记（add_module_translation）+CREATE-GUARD token 同批；
- 并发风暴存活模式：claim→幂等 patch→commit→verify 同进程（见项目记忆）；
- 涉 high 域（计划任务注册/schedule.yaml 生产窗变更）：按 R-E 裁定走闸不走人，但 **P3 写回前留一次 Owner 快闪窗口**（交易日历敏感，若 Owner 睡觉则按自裁框架放行+全量留痕，可逆设计=旧值存档一键回滚）。

## 6. 总验收（端到端）

1. 双向同步实测：a) 改 schedule.yaml 一槽位→表自动跟新；b) apply_resource_plan 改窗→真源+表+视图三处一致；c) schtasks 手停一任务→drift finding+promotion 页告警；
2. 完整度：五类真源对账 100%（幽灵/孤儿/未申报三类 finding 清零或豁免留痕）；
3. 排班质量：全仓同窗并发内存和 ≤ mem_ceiling；同刻不同组冲突=0；池词表违规=0；
4. 测试：resource_schedule 全部测试目录逐目录两轮 0 失败；align_all 相关维度 0 硬问题。

## 7. 红蓝对抗设计

- 蓝：构造 8 场景（幽灵池实体排班/ DISABLED 任务仍标 active/同刻双备份/ planned 挤预算/ ps1 改窗表未更/手改表条目/告警桥断/ 视图 stale）→ 预期全被对应闸/检查抓到；
- 红：绕过尝试（改真源不提交/绕过生成器手填 window_expr/池名私有扩展）→ 预期 fail-closed 或 drift warn；
- 通过判据：连续两轮问题=0。

## 8. 任务分解（交子代理执行的顺序波）

| 波 | 任务 | 依赖 | 车道 |
|----|------|------|------|
| W1 | P0 全四项 | 无 | 主会话或 GW-a |
| W2 | P1-a ∥ P1-b | P0 | 双子代理 |
| W3 | P2-a ∥ P2-b | P1 | 双子代理 |
| W4 | P3 | P2 | 主会话（涉生产窗） |
| W5 | P4 各项 ∥ P2-c/P2-d | P1 | 多子代理 |
| W6 | P5+§6 端到端+§7 红蓝 | 两周样本 | 收尾批 |
