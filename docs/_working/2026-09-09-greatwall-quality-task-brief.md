---
ttl: task_bound
---

# 长城任务指令书：产业链图谱全量质量修复（2026-09-09 启动版）

> **交付形态**：本文件是给执行 AI 的完整指令，Owner 复制正文给新对话即可启动。
> **配套真源**：SOP v1.5.0（industry_chain_data_audit_sop.md，编排+契约）｜质量标准（policies/graph_quality_standard.md，十九项合格线+修复方案）｜检查引擎（scripts/industry_graph/graph_quality_check.py）。
> **总时长**：指令时刻 + 10 小时（到次日 09:00）。

---

【长城任务——产业链图谱全量质量修复（SOP v1.5.0，执行至 2026-09-10 09:00 或指令时刻+10h，以先到者为准）】

你是 ZephyrAlpha 产业链图谱长城任务总控 AI。Owner 睡前下达本指令，你自主执行到时间盒，中途不问用户、不汇报中间态，醒后一次性大白话汇报。本指令与 SOP 冲突时以 SOP 为准。

━━━ 一、开工流程（全部完成才进 Phase 1）━━━
1. 抢总控锁：python scripts/industry_graph/websearch_ingest.py controller acquire --session <session_id>
   exit 4（BUSY）→ 静默退出不开工。
2. 通读三件真源（缺一不可）：
   - docs/01_policies_and_standards/sop/industry_chain_data_audit_sop.md（v1.5.0：总则九条+§4 契约+§12 质量循环）
   - docs/01_policies_and_standards/policies/graph_quality_standard.md（十九项合格线 S1~S19+每项修复方案）
   - scripts/industry_graph/graph_quality_check.py 头部注释（引擎用法）
3. 基线：backup 十表（superuser 通道）→ stats 基线 → 跑引擎基线：
   python scripts/industry_graph/graph_quality_check.py
   预期：总违规 ~18,160（S10 role 11,207 / S7 后缀 2,911 / S15 自环 1,874 / S8 孤岛 718 / S6 unspecified 686 / S5 382 / S1 61 / S14 44 / S16 145 / S17 114 / S19 17 / S12 1；S4/S13 因 ig_node_company 无 PIT 列 degraded）。
4. Python 环境：本机默认 3.13 缺 psycopg2——用 C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe（2026-09-08 夜班实证可用）。

━━━ 二、Phase 1 基建（先修引擎再修数据，~1h）━━━
1. ig_node_company 加 PIT 列（DDL 走 apply_industry_graph_ddl.py 增补 v4 段，幂等）：
   ALTER TABLE ig_node_company ADD COLUMN IF NOT EXISTS valid_from DATE / valid_to DATE / pit_strength TEXT;
   pit_strength 词表 {strong, weak}（graph_quality_standard.md §4 S13 口径）。
   加列后引擎 S4/S13 不再 degraded（复跑验证）。
2. 写入门禁收紧（websearch_ingest.py 校验追加，与引擎同词表同 commit 防漂移）：
   - role 白名单五值（龙头/核心/主要/参与/提及）
   - 链名标题腔正则拒绝（与引擎 TITLE_JUNK_RE 同源）
   - 节点名 -tier 后缀拒绝
   每条收紧补单测，测试 18→预期 20+。
3. 引擎 S4/S13 复跑转正（degraded→真实违规数）。

━━━ 三、Phase 2 P0 污染源清除（量化查询正在中毒，~2h）━━━
按标准 §12.3 优先级修，全部走治理脚本（幂等）或 ingest 通道，禁手写 SQL 写库：
1. S14 事故性挂链（44 家超阈值）：逐家甄别——真业务链保留、事故挂链 PIT 关闭（valid_to=修复日+source_doc="quality_fix|批次|日期"）。000591.SZ 已知挂 269 链（光伏真实其余污染）；300024 机器人/002594 比亚迪类多元化公司若甄别为真→登记豁免（quality_exemptions.yaml+reasons.md 双登记）。
2. S15 自环边 1,874 条：PIT 关闭。
3. S16 事故性双向边 145 对：保留证据强者（evidence_type/weight 优），弱者 PIT 关闭。
4. S4 废弃链落位残留：残留落位 PIT 关闭（链已 deprecated 不物理删）。
每完成一类→复跑引擎→该类违规数必须归零或进豁免。

━━━ 四、Phase 3 P1 结构垃圾清理（图谱可看，~3h）━━━
1. S10 role 归一（11,207 条，量最大）：写 role_migration 治理脚本——
   mentioned→提及、参与→参与、主要→主要 直译；长尾杂值按语义映射（含"龙头"→龙头，含"核心"→核心，其余→参与），映射表落盘留痕。
2. S7 后缀名 2,911：数据层剥离（治理脚本 UPDATE node.name 去尾部 "-tier"——改名不动 node_id 时安全；若同链同名将撞 S9 则合并处理）。前端显示剥离属 chainmap 会话职责不归本任务。
3. S6 unspecified 686：380 条机械判定落地（预审方案 r1_tier_plan.md）；306 条出清单进开放问题留 Owner。
4. S1 标题腔 61：逐条改规范名（"XX产业链"句式）或并入同义链（deprecated+merged_into）；与 90 锚点链同义者并入锚点（顺带解决 223 旧"XX行业"链撞车）。
5. S8 孤岛 718：有据补边/补落位；无据→所在链整体登记开放问题。
6. S5 version_year 382：按源文档年份补；无据开放问题。
每类完成复跑引擎对账。

━━━ 五、Phase 4 P2 合规修复（~1h）━━━
S19 编码表 17 家上市撞名：核对→标 listed+listed_symbol（须一手来源搜交易所公告，禁训练记忆）→跑 promote_unlisted_to_listed.py 换码。
S17 websearch 边 114 条补 evidence_type（有据补、无据登记）。
S13 新落位补 valid_from（THS 批次行业锚点=回填上市日 list_date、环节落位=盘点日 2026-09-08）。
S12 market 1 条机械修正。

━━━ 六、Phase 5 收敛循环（引擎驱动，直到时间盒）━━━
按 SOP §12.2 循环：跑引擎→修→复跑（严格递减）→直到零违规或时间盒。
振荡保护：违规数不降→停→开放问题。
时间盒到点：剩余按违规量降序报告，断点入 progress.json。

剩余时间才做（优先级递减）：
- 全球主干链 5~8 条（SOP §6 第4轮清单，石油/油气运输+海峡/天然气/锂/半导体/铜优先）
- R3a 环节级深度冲刺
- 事件传导闸首例推演（战略段结论 Owner 已给：美伊→霍尔木兹→中俄管道）

━━━ 七、纪律红线（违反任何一条=事故）━━━
1. 写库唯一通道=治理脚本/ingest；SELECT 诊断自由。
2. 只增不删：垃圾修复一律 PIT 关闭（valid_to=修复日），零物理 DELETE。
3. 豁免双登记：quality_exemptions.yaml+quality_exemption_reasons.md（原因+日期+裁定人），未登记=违规留存。
4. 修复批次 source_doc 三段式："quality_fix|批次号|YYYY-MM-DD"。
5. websearch 新写 confidence≤0.7+PIT 三时间戳+两端 symbol 非空；股权投资关系禁入边表。
6. 引擎判定权最高：AI 不得自行宣布"修好了"——引擎复跑零违规才算；degraded 项须当轮修好环境。
7. 单文件多编辑禁并行批（互相覆盖教训）；git 提交走 GitCommitGateway（--files 逗号分隔单参数，禁裸 commit/--no-verify）；新文件登记 creation_token+翻译真源（多会话热文件用 safe_write_text CAS）。
8. 时间盒=指令时刻+10h（旧 progress 时间盒字段无效）。
9. 拿不准的登记开放问题，不自裁。

━━━ 八、收尾（必执行）━━━
1. 引擎终跑+报告归档（.runtime/industry_graph/quality_reports/）。
2. stats 终态 vs 基线对账（每表增量=修复动作数，零偏差）。
3. 夜班报告落盘 .runtime/industry_graph/night_audit/report_YYYYMMDD.md。
4. 施工件（DDL v4/治理脚本/工具收紧/测试）全部走网关提交；progress.json 终态。
5. 总控锁 release。
6. 大白话汇报（只给结果）：
   【完成度】一句话（引擎违规 18,160→X；P0/P1/P2 各修了多少）
   【引擎终态】每项 S1~S19 的违规数终态表（含 degraded 清零声明）
   【P0 清除】污染源处置明细（000591 类清洗了多少、豁免了谁）
   【数据增量】十表基线 vs 终态
   【施工件】DDL v4/脚本/测试清单+commit hash
   【开放问题】306 unspecified/44 超阈值甄别/孤岛链等待 Owner 拍板清单
   【断点与续跑】剩余违规+下次从哪继续
