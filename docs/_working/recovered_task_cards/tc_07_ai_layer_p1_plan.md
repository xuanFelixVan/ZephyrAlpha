---
card_id: TC-07
title: AI 层进化引擎复审 + P1 施工方案编制
verdict: 存活但被并行施工侵入变形（置信度高：两交付物 0% 产出；P1 范围内的 L2 收集库已被全流通车道抢建约 8/9 项且 4 个验收测试件缺失；原任务书内容约三成已过时，必须按"复审 L2 既成事实+方案改为收尾批"重写）
category: E类-施工批（ai_layer 车道）
priority: P2
size: 中
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 550-652 行（"七："节）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-07 AI 层进化引擎复审+P1 方案

## 0. 一句话结论

两份交付物（P1_construction_review.md 复审报告、P1_construction_plan.md 施工方案）**全历史零记录**，Owner 批都没批过（无对象可批）。但 P1 范围内的 L2 收集库已被全流通战役车道（84007a1d6a，09-19）抢建落地 12 文件 2713 行——未经本任务规定的"复审+方案+Owner 批"门，且缺 test_gate/test_card_store/test_events/test_kpi 四个验收测试件。任务若重启必须按新基线重构：L2 批降格为"收尾批"，其余 10 本 DESIGN 按依赖序照编。

## 1. 背景与来龙去脉

AI 层"自我进化引擎"设计真源已 100% 完成（11 本 DESIGN 挖干+红蓝 R1-R10 两轮双队零问题+23 笔 commit），P1 施工已落第一件（OBJ_R 历史重放器 rule_replay S1+S2，17 单测+冒烟）。本任务=复审未完成清单准确性+产出 P1 施工方案交 Owner 批，批前不施工。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 两交付物待产 | **不存在**：盘上无、HEAD 无、全 refs 无 commit 触碰、全盘无草稿 | 四路查证（ls/cat-file/git log --all/find）全空 | A |
| 11 本 DESIGN 齐全 | 11/11 全齐（211-409 行），目录除 staged index.md 外无未提交改动 | 逐目录 wc -l | A |
| rule_replay S1+S2 已落地 | 在 HEAD：standards_governance/rule_replay.py（632 行）+tests（255 行/17 用例），落地 commit 3ac3af3faa；此后该路径零新增（历史仅此一件） | cat-file + git show --stat | A |
| L2 收集库 9 项未施工 | **已被抢建约 8/9**：84007a1d6a（09-19 00:27，st-ff-ailayer3-20260918）"全流通 intake 族第 3 批"12 文件 2713 行，含 L2 DESIGN 施工项 1/2/3/4/5/6/7 全部成品+测试 2 件——但 DESIGN 验收要求的 test_gate/test_card_store/test_events/test_kpi 四测试件缺失，项 2/3/4/7 验收实际未闭环 | git show --stat 84007a1d6a 对照 L2 DESIGN.md:213-219 | A |
| __init__.py CREATE-GUARD 碰撞 | **未解决**：仍未跟踪、从未入任何 ref、无豁免或 PEP420 裁定；但 HEAD 注册表:33015 已预登记该路径（账实脱节）；现靠 PEP420 隐式命名空间可导入 | git status + git log --all + 注册表 grep | A |
| 翻译注册表 warn 期条目 | 已解决：rule_replay 条目已在 HEAD（module_translation_registry.yaml:55165） | git show HEAD grep | A |
| README 第 3.5 节 31 项+治理立案 9 项 | 完好：对账=已销 17+治理立案 9+真待 Owner 5=31（标题"6 项"是 R9 改判后未刷的陈旧数字，正文 5 项无实害） | 通读 README.md:152-208 + git diff HEAD 空 | A |
| st-refscan 15 件 index.md | 原样 staged 在途，不归本线动 | git status | A |
| 执行批次开工没 | L2 后未再推进：tests/ai_layer/ 仅 conftest+test_dedup；无 OBJ_M/OBJ_L 落地 | find + grep | A |
| （新发现）注册表幽灵条目 | module_translation_registry.yaml:55581 仍有旧路径 src/zephyr/ai_layer/intake/events.py（文件已改名 intake_events.py，双条目并存）——"静态清单禁手工维护必漂移"红线实例 | grep | A |

### 病根

1. **多会话车道竞争吞掉了任务前置门**：任务书规定"复审、方案、Owner 批、才施工"，但全流通战役把 L2 整批抢建落地——接班者照原文施工会撞车/重复；P1 方案失去"首催=L2"立论基础。
2. **执行会话蒸发**：指定会话 st-ailayer-20260918 从未在 .runtime/sessions 留目录，前身的三条死信记录了 rule_replay 落地前三门连拒改道史——任务在交接链上断线无人接棒。
3. **登记与实物脱节三连**：__init__.py 登记在实物无；events.py 幽灵条目；README 标题计数差一。

## 3. 上下游

- 前置依赖：11 本 DESIGN（完好）+README 第 3.5 节（完好）+L2 既成事实盘点（本次已备齐证据）；Owner 对 __init__ 两解与 L2 越批追认的裁定。
- 下游消费方：P1 施工执行批次（本任务交付物是唯一开令依据）；OBJ_R S3/S4/S5、OBJ_M 模型线；TC-10 收藏情报的组合层立项（eng_quantcombine 思想与本层 L4/OBJ_M 重叠，两边立项须互认同源避免双份考尺）。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 1 | 重做复审：把 L2 既成事实（84007a1d6a，7.5/9 项+4 缺测试件）、__init__.py 悬置、events.py 幽灵条目、第 3.5 节标题计数差一全部纳入复审报告；追认 L2 施工授权来源疑问列 Max 裁定清单 | D:\ZephyrAlpha\docs\_working\ai_layer_vision\P1_construction_review.md（新建） | 含分级问题清单（P0 阻塞/P1 应修/P2 记录）+Max 裁定清单 | Flash |
| 2 | __init__.py 两解裁定：Owner 裁定豁免 vs 改 PEP420 布局，裁定后随批落地（404 字节成品已在盘） | src/zephyr/governance/standards_governance/__init__.py | 文件入 HEAD、working tree 零驻留 | Max 预审，Owner 门位（涉 ARCH-031 语义） |
| 3 | 编制重构版 P1 方案：L2 批改"收尾批"（补 4 测试件+施工项 8 登记补全），其余 10 本 DESIGN 按依赖序照编；六要素（分批/车道/路由/资源/红线/回滚）全齐——红线要素必须逐条写明：禁碰 docs/03_modules、TDM、AGENTS.md、他车道在飞区；五条永不触碰（实盘凭证/付费动作/宪法权限语义/审计链/验收判据自改）。两份交付 .md 落地前走 CREATE-GUARD token ceremony+网关落 HEAD+工作树零驻留（原文交付③） | D:\ZephyrAlpha\docs\_working\ai_layer_vision\P1_construction_plan.md（新建） | 六要素全齐（红线含三禁碰+五永不触碰）+第 3.5 节九项治理立案预审归纳挂钩；两交付物在 HEAD 且工作树零驻留 | Flash 起草，取舍点列 Max 清单 |
| 4 | 注册表卫生小批：清 events.py 幽灵条目、刷 README 标题计数 | docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml、docs/_working/ai_layer_vision/README.md | 路径账实一致 | Flash |
| 5 | 催批：方案落盘交 Owner 批，批前不动一行施工代码 | 会话回复 | Owner 批文在案 | Owner 门位 |

## 5. 与其他任务卡的关系

- TC-10：eng_quantcombine_idea_mining.md 是两边共同的设计输入（组合优化管线 vs L4 对比/OBJ_M）——两边立项互认，防双份考尺。
- TC-05/TC-09：无文件级交集；本卡的"会话蒸发+死信"模式与 TC-03 病根 2 同构。
- TC-11：图书馆立项批（c968ad6042）与本目录零文本交集，但终极图书馆未来可能是 L2 收集库的最大客户——方案编制时预留挂接。

## 6. 风险与避让红线

1. 15 个 staged index.md 是 st-refscan 在途件，本线提交不得吸收（提交后必核归属）。
2. 两注册表（canonical/translation）当前均为他会话 staged 热文件：改注册表条目须 claim+队列避让。
3. L2 既成事实未经本线复审，禁把它当"已验收"——4 缺测试件意味着项 2/3/4/7 验收未闭环。
4. 勿照原文任务书直接开跑：L2 段已过时。
5. governance/ 根禁新增 .py（ARCH-031）——一律进 standards_governance/ 子包。
6. 注册表防过期假净删四步压一条命令（checkout HEAD→重插行→claims→入袋）；加行被 held 用 --allow-overlap（叠加型非互斥）。
7. 提交队列死信处置：读 .runtime/commit_queue/dead/<qid>.json 的 dead_reason→修文件→requeue；serializer Apply 静默失败（四现先例）=入袋后轮询无进展即改直连重试。
8. docs/_working 新文件 frontmatter 禁带 doc_type（EXEMPT-ZONE-FM 硬拦）；新 .md 必带 ttl 字段（TTL-METADATA）。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；新 .py 三件套（depgraph+token+翻译）；15 字段文件头；时间戳用 shared.utils.time_utils.now_utc 禁 datetime.now。
