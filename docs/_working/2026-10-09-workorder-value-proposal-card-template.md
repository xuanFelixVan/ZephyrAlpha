---
ttl: task_bound
completes_when: 模板被实际工单持续引用；连续 90 天零引用则按墓碑制退役评估
created: 2026-10-09
---

> ## 结案报告（2026-10-14 由 st-wkcure-chief-20261013 核验）
> **总结论：役内在用·待役终（本件=Gate 0 三件套工单模板规范真源，已入能力正典册登记并被政策锚引用；completes_when 为持续性判据「被实际工单持续引用/90 天零引用才评退役」，观察窗自 2026-10-09 起仅 5 天，远未到判点，不归档）**
> **✅ 已完成（逐条，每条带可回溯证据）**
> - 模板本体交付（v1.0，Gate 0 三件套并入 TaskCard 结构词）：证据=1c5a56a85e3 | 2026-10-10 | [st-libfront-20261009] B2 价值主张立项卡模板批落地（git log -1 实测）
> - 正典册登记在册：证据=git grep 实测本件被 docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml 引用 1 处（creation_token/正典文件面）
> - 政策锚两件在盘：证据=docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md 与 docs/01_policies_and_standards/sop/construction_sop/task_card_work_order_policy.md（正文 §政策锚所指路径，git grep 命中册内）
> - 迷你实例（本轮 A 件根治单）随源批落地：证据=1c5a56a85e3 commit message 明写「A 前门再生挂链+B1 裁定先例机检 CLI+B2 模板」三件同批（实测 git log）
> **⚠️ 未完成（逐条）**
> - 无（本件为长期规范模板真源，非一次性任务；其 completes_when 本身即「持续被引用」型活体判据，除该观察窗未到期外无缺口）
> **继任与消费面**：无继任（不需）；消费面=capability_canonical_file_registry 在册引用＋政策两册（adjudication_routing_policy §2.0 Gate 0 / task_card_work_order_policy §2.4）为现行役政策真源，后续开卡工单按本件复制卡体即构成消费（截至核验日 git grep 未见其他 _working 工单件显式引用文件名，属正常早期——模板出生仅 5 天）。
> **核验方式**：读全文（frontmatter/用法/卡体/示例/版本记录）+ git log -1 本件 + git grep -ln "value-proposal-card-template|价值主张立项卡" 全仓消费面 + git grep -c 引用计数（HEAD=b05345f8e6）
> **证据等级**：A=实测可复现（落地哈希、册内引用命中）/ B=政策两册锚点存在性系 grep 命中未逐行精读
> **处置建议**：留根面（规范/模板真源不适用结案归档；90 天零引用判据到点后再评）

<!-- creation_token: 见 capability_canonical_file_registry creation_tokens 段（st-libfront-20261009 登记） -->
# 工单·价值主张立项卡模板（Gate 0 三件套版 v1.0）

> **用法**：开卡即复制下方【卡体】全文作 TaskCard `description`（或独立立项卡正文）。四机械校验词（根因/治根/施工步骤/验收标准）已内嵌勿删——删了过不了 solution_completeness 校验（task_repo required_keywords）；三件套字段缺一过不了 Gate 0。
> **政策锚**：[adjudication_routing_policy.md](../01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md) §2.0 Gate 0（G0-1 分野/G0-3 三件套/G0-4 主轴/G0-5 不劣化/G0-6 痛感证据/G0-7 证伪回路/G0-8 基线冷启动）＋ [task_card_work_order_policy.md](../01_policies_and_standards/sop/construction_sop/task_card_work_order_policy.md) §2.4 建卡质量前置。
> **净零声明**：并入既有工单格式（TaskCard 结构词 + l5 立项卡版式），零新表/零新 gate/零新字段（模板即载体，真源=政策两册）。

## 【复制起点】卡体

```markdown
- **卡号/任务**：<task_id 或工单名（TaskCard 则以 create_and_ready 返回为准）>
- **对象分野（G0-1）**：增量判立轨 / 存量判退轨（二选一，禁跨用——新工程消费者必为零，禁用存量判据否决增量）
- **主轴（G0-4，验收按主轴计）**：Δ速度 / Δ治理质量 / Δ算法质量（附表 A 三轴择一；多轴收益必须指定主轴，辅轴只做约束）
- **基线（G0-3；无基线先立测量 G0-8，带时间戳+环境戳）**：<测量方法 + 当前读数 + 何时测的>
- **目标（可测 Δ，一行写死数值）**：<基线 X → 目标 Y>
- **验收判据（G0-3）**：<测量方法 + 验收窗（默认 30 天）+ 达标线；落地后按窗对拍，未达标=证伪→自动转 D1 退役评估（G0-7）>
- **不劣化约束（G0-5）**：其余两轴各一条不劣化判据：<轴A：...>；<轴B：...>（提速不得增幻觉/漂移；算法改进不得绕门禁）
- **痛感证据（G0-6，Δ速度主轴必附）**：<队列积压/滞留时长/绕路工单数/死信率/人肉等待记录——"感觉慢"不是证据>
- **根因**：<什么病、哪次实证暴露、为何现在治>
- **治根**：<为何此方案治本不治标；临时方案必须带报废判据+期限（G3-5）>
- **施工步骤**：<1. … 2. … 3. …（每步可验证）>
- **验收标准**：<两轮预审零问题 + verify 核销安排（task_card_work_order_policy §2）+ 主轴 Δ 对拍 + 辅轴不劣化复核>
- **范围与禁区**：<做什么/明确不做什么（禁触碰面）>
- **依赖在册件（G1 内收先行）**：<引用既有资产承载；若新建必须声明"为何无既有资产可承接"并引用 G1 判据编号（G1-5）>
- **批准位**：owner_ruling_id=null（待批——未批禁施工）
```

## 填写示例（迷你实例=本轮 A 件根治单）

- **对象分野**：存量判退轨（对"手动 regen 惯例"判退，由事件链承接）
- **主轴**：Δ治理质量
- **基线**：FRONT_DOOR.md --check 漂移存续 10 天（2026-09-29→10-09，实测 DRIFT rc=1）
- **目标**：前门漂移归零且复发即随链自愈（regen 入 post-commit 事件链）
- **验收判据**：红→链→绿三段证据（人为漂移 rc=1 → reconciler action=clean → --check 绿）＋ 新步失败降 warn 单测
- **不劣化约束**：Δ速度——提交链路新增子进程 ≤120s 超时上界且 fail-soft 不阻断；Δ算法质量——零触碰（不涉考场）
- **痛感证据**：不适用（非速度主轴）
- **根因**：前门双投再生是手动单口，未挂 reconciler 事件链，馆页再生后必然漂移
- **治根**：第⑤步挂链（事件触发，禁 cron——永久系统四要素），摘步即红=load-bearing
- **施工步骤**：①症状 regen 清漂 ②reconciler 尾追加⑤步+头注更新 ③红证三段+单测
- **验收标准**：两轮检查零问题＋git log 核归属；30 天窗内观察 reconciler 触发时 --check 恒绿
- **范围与禁区**：只动 reconciler+测试；禁改 generate_front_door.py 语义；禁 cron 化
- **依赖在册件**：MOD-LIB-001 reconciler 链＋MOD-INF-005 双投生成器（零新建系统，G1-1 必并）
- **批准位**：owner_ruling_id=总统筹批准令（根治+扩容令 A 项，2026-10-09）

## 版本记录

- v1.0（2026-10-09，st-libfront-20261009）：首版——Gate 0 三件套字段并入 TaskCard 结构词与 l5 立项卡版式（Owner 总统筹批准·根治+扩容令 B2 项）。
