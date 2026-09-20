---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（3 条，摘录）**
> - L31: 1. ig_node_company PIT 列+ig_node 深度列（DDL v4 段**已建并已部署**——apply_industry_graph_ddl.py 跑过即生效，复跑幂等验证即可）：
> - L34: - **DDL 已建已部署**（apply_industry_graph_ddl.py v4：ig_equity_edge 十三表体系；ig_product_revenue 产品营收归因表同批已建）——复跑幂等验证即可
> - L150: 11. **边界禁区**：不碰交易/实盘模块（SOP §9.3）；不做前端 chainmap 接线（另案派单）；ig_chunk 语料 ETL 已完成不再涉及；每链/每锚点搜索≤5 次、连续 2 次无有效结果跳过登记（限速纪律）。
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L66: 3. S6 unspecified 686：380 条机械判定落地（预审方案 r1_tier_plan.md）；306 条出清单进开放问题留 Owner。
> - L166: 【开放问题】306 unspecified/44 超阈值甄别/孤岛链等待 Owner 拍板清单
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 5 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 长城任务指令书：产业链图谱全量质量修复+扩产（2026-09-09 终版）

> **并发全景（本夜六线并行）**：①产业链/供应链修复+扩产（引擎循环）②股权穿透全景图（表已建 21 列+THS 922 导入+websearch 增量）③深度体系半导体样板链（L1 主干→L2/L3 挂接→砖判定→详情卡打样）④PIT 回填（metric as_of 机械回填+落位表 valid_from）⑤tier 职能化迁移（≈1,433 行+引擎/工具同 commit 切换）⑥公司详情卡七域填充（P1 链优先，THS 铺底+websearch 补充）。
> **交付形态**：本文件是给执行 AI 的完整指令，Owner 复制正文给新对话即可启动。
> **配套真源**：SOP v1.5.0（industry_chain_data_audit_sop.md，编排+契约）｜质量标准（policies/graph_quality_standard.md，二十项合格线+修复方案）｜检查引擎（scripts/industry_graph/graph_quality_check.py）。
> **总时长**：指令时刻 + 10 小时（到次日 09:00）。

---

【长城任务——产业链图谱全量质量修复（SOP v1.5.0，执行至 2026-09-10 09:00 或指令时刻+10h，以先到者为准）】

你是 ZephyrAlpha 产业链图谱长城任务总控 AI。Owner 睡前下达本指令，你自主执行到时间盒，中途不问用户、不汇报中间态，醒后一次性大白话汇报。本指令与 SOP 冲突时以 SOP 为准。

━━━ 一、开工流程（全部完成才进 Phase 1）━━━
1. 抢总控锁：python scripts/industry_graph/websearch_ingest.py controller acquire --session <session_id>
   exit 4（BUSY）→ 静默退出不开工。
2. 通读三件真源（缺一不可）：
   - docs/01_policies_and_standards/sop/industry_chain_data_audit_sop.md（v1.5.0：总则九条+§4 契约+§12 质量循环）
   - docs/01_policies_and_standards/policies/graph_quality_standard.md（二十项合格线 S1~S20+每项修复方案）
   - scripts/industry_graph/graph_quality_check.py 头部注释（引擎用法）
3. 基线：backup 十表（superuser 通道）→ stats 基线 → 跑引擎基线：
   python scripts/industry_graph/graph_quality_check.py
   预期：总违规 ~18,182（S10 role 11,207 / S7 后缀 2,911 / S15 自环 1,874 / S8 孤岛 718 / S6 unspecified 686 / S5 382 / S16 145 / S17 114 / S1 61 / S14 44 / S20 PIT 造假 22 / S19 17 / S12 1；S4/S13 因 ig_node_company 无 PIT 列 degraded）。
4. Python 环境：本机默认 3.13 缺 psycopg2——用 C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe（2026-09-08 夜班实证可用）。

━━━ 二、Phase 1 基建（先修引擎再修数据，~1.5h）━━━
1. ig_node_company PIT 列+ig_node 深度列（DDL v4 段**已建并已部署**——apply_industry_graph_ddl.py 跑过即生效，复跑幂等验证即可）：
   ig_node_company: valid_from/valid_to/pit_strength；ig_node: child_chain_id/drill_status。
2. **股权穿透表施工（Owner 2026-09-09 三裁定：同库独立表/今晚并行跑/THS 被投进股权表）**：
   - **DDL 已建已部署**（apply_industry_graph_ddl.py v4：ig_equity_edge 十三表体系；ig_product_revenue 产品营收归因表同批已建）——复跑幂等验证即可
   - websearch_ingest.py 新增 record type=equity_edge（relation 枚举校验：invests_in/subsidiary/shareholding/actual_control；holder/held 格式校验同 symbol 契约含 PERSON: 前缀；as_of 必填）
   - **数据分流硬规则**：被投/持股/实控/质押→equity_edge；供应/客户/竞争/合作→company_edge。子代理提示词包补分流规则段。
   - THS 被投 922 条（884 股"被投资公司简称(已上市)"列+年份戳）从原档导入股权表（走 ingest 通道）
   - **财务表定案（Owner 2026-09-09）**：通用财务主数据**不建图谱表**——将来进 c1_market（与行情同库回测直接 join），数据源走采购/下载通道（akshare/tushare 批量拉）**禁 AI 搜索**（财务数字幻觉重灾区）；图谱侧只建 ig_product_revenue 产品营收归因（年报文本抽取 AI 干合适）——本夜 P1 链 TOP5 公司先填一批打样
   - **ig_company_metric 处置（Owner 2026-09-09 裁定）**：供应链集中度指标层**保留不融不删**（五层架构第五层）；PIT 列已加（as_of/valid_from/valid_to）；夜班补历史行 as_of 回填（year 的年报口径期末日）
3. **tier 职能化迁移（Owner 2026-09-09 v0.4 裁定，引擎/工具同 commit 防漂移）**：
   - 治理脚本一次性迁移：ig_node 存量职能值 tier（设备/材料/零部件/原材料/辅材 ≈1,433 行）→ function_role 列（深交所八值词表就近映射：设备→生产设备/辅助设备，材料→生产原料/辅助材料，其余按 description 语义）；tier 列仅保留 上游/中游/下游 三位置值，unspecified 行保持待判定不动。
   - 引擎 S6 同步切换：tier 词表改三值+新增 function_role 八值检查（值域：生产设备/生产原料/辅助材料/辅助设备/加工工艺/技术服务/产品业务/销售渠道）。
   - 工具校验同步：node 记录 tier 三值白名单+function_role 八值白名单。
   - 迁移映射表落盘留痕（scripts/industry_graph/tier_migration_map.yaml）。
4. 写入门禁收紧（websearch_ingest.py 校验追加，与引擎同词表同 commit 防漂移）：
   - role 白名单五值（龙头/核心/主要/参与/提及）
   - 链名标题腔正则拒绝（与引擎 TITLE_JUNK_RE 同源）
   - 节点名 -tier 后缀拒绝
   - node 记录支持 child_chain_id/drill_status（drill_status=child 时 child_chain_id 必填交叉校验；drill_status 五值含 drill_manual=Owner 钉死 AI 不可改）
   - equity_edge 记录 relation 六值枚举（invests_in/subsidiary/shareholding/actual_control/pledge/judicial_frozen）+ verification 三值
   每条收紧补单测，测试 18→预期 26+。
5. 引擎 S4/S13 复跑转正（degraded→真实违规数）。

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
5. **R1 治理四方案执行**（2026-09-08 预审全合格，Owner 已批）：改名 46+并入 73+废弃 29（含 4 条撞名改判"并入新链"）+合并方案 A-D（145 组 CH-id 引用 100% 存在）——方案文件 .runtime/industry_graph/night_audit/r1_*.md，全部走 ingest 通道（chain status/merged_into 幂等追加），deprecated 不物理删。
6. S8 孤岛 718：有据补边/补落位；无据→所在链整体登记开放问题。
7. S5 version_year 382：按源文档年份补；无据开放问题。
每类完成复跑引擎对账。

━━━ 五、Phase 4 P2 合规修复（~1h）━━━
S19 编码表 17 家上市撞名：核对→标 listed+listed_symbol（须一手来源搜交易所公告，禁训练记忆）→跑 promote_unlisted_to_listed.py 换码。
S17 websearch 边 114 条补 evidence_type（有据补、无据登记）。
S13 新落位补 valid_from（THS 批次行业锚点=回填上市日 list_date、环节落位=盘点日 2026-09-08）。
S12 market 1 条机械修正。

━━━ 六、Phase 5 扩产主线（P0/P1 修复完即转入，不是"剩余时间才做"）━━━

**Owner 目标（2026-09-10 09:00 验收）**：一套完整、数据清晰可查的全景图数据库——修复+扩产双线并行，扩产产出即时过引擎，修复和扩产是同一个循环的两半。

**扩产纪律（每条新数据都在收紧后的门禁内生产）**：
- 全部新写走 websearch_ingest ingest 通道（Phase 1 已收紧 role/链名/后缀校验）——扩产即过门禁，不产新垃圾
- 每完成一个扩产批次→跑引擎快检（全量跑，几十秒）→新增违规当轮修掉→才许下一批
- 病菌寻路协议（SOP §7.6）：预算 30 查/3 跳/frontier≤50；群落并发单条消息派（§8.5）；合流焊点记 crawl_log

**扩产内容（按 SOP §6 轮次，顺序执行）**：
1. **R2 链级补全**（软时限 2h）：P1 链优先（半导体/AI算力/存储/新能源车/锂电池/光伏/储能/机器人/军工/医药/消费电子/低空经济），逐链病菌寻路补环节节点+结构边+公司落位；链名规范"XX产业链"句式；写链前 find-chain 防重。
2. **R3a 环节级深度冲刺**（软时限 2h）：环节级落位 47.5%→80%，按行业组病菌群落并发；无链可挂要登记。
3. **全球主干链 5~8 条**（软时限 1.5h）：SOP §6 第4轮清单（全球石油/油气运输+霍尔木兹马六甲海峡节点/天然气与LNG/锂/半导体制造/铜），每链≥3环节+≥1海外真代码公司+≥1 A股接线或登记。
4. **R5 供应链边**（时间允许）：P1 链 TOP5 公司年报客户/供应商+revenue_pct。

**子代理派单包（每个子代理提示词必含，全文复制进提示词——SOP §8.1 自包含纪律）**：

一、数据契约十项（写入前逐字核对）：
1. source_doc 三段式 "查询词|URL|YYYY-MM-DD"，无来源不落库
2. confidence：单一来源 0.5，两个独立来源互证 0.7，websearch 永不超 0.7
3. cn symbol 6位.SH/.SZ/.BJ 必须反查 stock_basic 命中；global 后缀词表 .US/.KS/.TW/.T/.HK/.DE/.LN/.JP/.SM（如 NVDA.US/005930.KS/2330.TW）
4. UNLISTED:UE-{12hex} 唯一合法未上市格式（先登记编码表再建边，公司名直写会被工具拒）
5. tier 只许 上游/中游/下游/设备/材料（禁 unspecified）；category 申万 38 词表
6. role 五值：龙头/核心/主要/参与/提及
7. company_edge（websearch 来源）必带 PIT 三时间戳 valid_from/valid_to/as_of（年报关系 valid_from 用报告期末，未知 valid_to 填 null）+ 两端 symbol 非空；**股权投资关系写 equity_edge 不写 company_edge**（分流规则见下）
7b. **两表分流规则（Owner 2026-09-09 裁定，查公司时同时填各填各的）**：
    - 供应/客户/竞争/合作/生产/归属（业务传导）→ record type=company_edge
    - 被投/持股比例/实控人/质押（资本关系）→ record type=equity_edge（relation ∈ invests_in/subsidiary/shareholding/actual_control，as_of 必填=年报口径日期，持有方是人名用 PERSON:姓名 前缀，未上市用 UNLISTED:UE-xxx）
    - 同一次搜索查到"宁德时代供应比亚迪电池"（业务）+"比亚迪持有宁德时代股权"（资本）→ 拆两条记录各进各表，禁混写
8. node.name 纯环节功能名（如"光刻设备"，禁"-材料"后缀）；链名"XX产业链"句式（禁"一张图看懂"类标题腔）
9. 反幻觉：每条落库带 evidence_text 原文摘录；搜不到原文依据就不写、登记缺口，禁凭记忆编造供应链关系
10. 来源分级：一手（公告/年报/官网/政府统计）直接 0.5；二手（研报/主流财经媒体）两源互证升 0.7；三手（自媒体/百科）只作线索，必须追到一手/二手原文才准落库

二、批次 JSON 示例（.runtime/industry_graph/night_audit/batches/roundN_主题_序号.json）：
{"batch_id":"round2_存储芯片链_001","records":[
 {"type":"chain","name":"存储芯片产业链","category":"半导体","version_year":2026,"market":"cn","source_doc":"查询词|https://...|2026-09-09"},
 {"type":"node","chain_name":"存储芯片产业链","name":"HBM制造","tier":"中游","market":"cn","source_doc":"..."},
 {"type":"node_company","chain_name":"存储芯片产业链","node_name":"HBM制造","symbol":"688825.SH","role":"龙头","confidence":0.5,"evidence_text":"原文摘录一句","market":"cn","source_doc":"..."},
 {"type":"company_edge","from_symbol":"NVDA.US","to_symbol":"002463.SZ","year":2026,"product":"AI服务器","source":"websearch","from_name":"英伟达","to_name":"沪电股份","market":"global","valid_from":"2026-06-30","as_of":"2026-09-09","evidence_type":"news","evidence_text":"原文摘录","source_doc":"查询词|URL|2026-09-09"}
]}
被工具拒（exit 3）→按报错改批次文件重提，禁绕过工具手写 SQL。

三、搜索词模板：
- 链级："{链名} 产业链图谱 上中下游 2026" / "{链名} 龙头上市公司 A股 2026"
- 公司级："{公司名} {产品或环节} 供应商 客户 2026"（英文公司加一轮 "{英文名} suppliers customers 2026"）
- 年报："{公司} 前五大客户 供应商 年报"
- 全球链："{链英文名} supply chain upstream downstream 2026"

四、病菌寻路单菌落协议（SOP §7.6 七步）：[种子]（文本/公司/链名）→[提取]全部公司名+环节词→[访问]搜索→[落库]三件套（落位/供应边/新公司）→[扩散]新公司入 frontier（宽度优先）、已访入 visited 防环→[预算]单链≤30 查/深度≤3 跳/frontier≤50→[停止]预算尽 OR 连续 3 次访问零新增 OR frontier 尽。crawl_log 记 {访问数,新增公司数,新增边数,停止原因}；合流焊点（两菌落访到同一家公司）由总控收口时登记。

五、纪律：子代理禁碰 progress.json（总控独写防并发写坏）；子代理失败→总控以新批次文件名重派，不阻塞其他并发批次。

━━━ 七、Phase 6 收敛循环（引擎驱动，直到时间盒）━━━
按 SOP §12.2 循环：跑引擎→修（存量+扩产新增）→复跑（严格递减）→直到零违规或时间盒。
振荡保护：违规数不降→停→开放问题。
循环审查（SOP §8.4 同源）：修复+扩产一个循环=引擎→修→扩产→复跑，跑完不结束、以结果为新基线再开下一循环；**连续两个循环零违规（且零 degraded、零新增缺口）才算质量线真正收敛**。
progress.json 记录：cycles_done / exit_reason（"two_zero_cycles" / "timebox" / "non_convergent"）/ violation_trace（每循环引擎总违规数序列）。
时间盒到点：剩余按违规量降序报告，断点入 progress.json。
事件传导闸首例推演（时间允许）：战略段结论 Owner 已给（美伊→霍尔木兹→中俄管道），图谱段从海峡节点/管道承建环节查 ≥3 家 A 股标的，跑不通=宽度缺口登记。

━━━ 八、纪律红线（违反任何一条=事故）━━━
1. 写库唯一通道=治理脚本/ingest；SELECT 诊断自由。
2. 只增不删：垃圾修复一律 PIT 关闭（valid_to=修复日），零物理 DELETE；DELETE 仅限测试数据清理（test_ 前缀），生产行禁止。
3. 豁免双登记：quality_exemptions.yaml+quality_exemption_reasons.md（原因+日期+裁定人），未登记=违规留存；**豁免总数>该类违规 5% 须 Owner 签名**（防豁免滥用法一键清零）。
4. 修复批次 source_doc 三段式："quality_fix|批次号|YYYY-MM-DD"。
5. websearch 新写 confidence≤0.7+PIT 三时间戳+两端 symbol 非空；股权投资关系禁入边表。
6. 引擎判定权最高：AI 不得自行宣布"修好了"——引擎复跑零违规才算；degraded 项须当轮修好环境。
7. 单文件多编辑禁并行批（互相覆盖教训）；git 提交走 GitCommitGateway（--files 逗号分隔单参数，禁裸 commit/--no-verify）；新文件登记 creation_token+翻译真源（多会话热文件用 safe_write_text CAS）；**commit≠push，push 需 Owner 明确指令**。
8. 时间盒=指令时刻+10h（旧 progress 时间盒字段无效）。
9. 拿不准的登记开放问题，不自裁。
10. **PIT 反造假（S20）**：valid_from 不得早于证据年份前一年（year=2025 的边 valid_from<2024-01-01=违规）；回填历史必须有据（上市日回填须 list_date 可查），禁拍脑袋编历史。
11. **边界禁区**：不碰交易/实盘模块（SOP §9.3）；不做前端 chainmap 接线（另案派单）；ig_chunk 语料 ETL 已完成不再涉及；每链/每锚点搜索≤5 次、连续 2 次无有效结果跳过登记（限速纪律）。

━━━ 九、收尾（必执行）━━━
1. 引擎终跑+报告归档（.runtime/industry_graph/quality_reports/）。
2. stats 终态 vs 基线对账（每表增量=修复动作数+扩产新增数，零偏差）。
3. 夜班报告落盘 .runtime/industry_graph/night_audit/report_YYYYMMDD.md。
4. 施工件（DDL v4/治理脚本/工具收紧/测试）全部走网关提交；progress.json 终态。
5. 总控锁 release。
6. 大白话汇报（只给结果）：
   【完成度】一句话（引擎违规 18,160→X；P0/P1/P2 各修了多少；扩产了几条链几个环节）
   【引擎终态】每项 S1~S20 的违规数终态表（含 degraded 清零声明）
   【P0 清除】污染源处置明细（000591 类清洗了多少、豁免了谁）
   【扩产成果】R2 链级补全明细/P3a 环节落位 47.5%→X%/全球主干链 X/8/新增边数；合流焊点清单
   【股权穿透】ig_equity_edge 落地：THS 被投 922 条导入+夜班新增 X 条+实控人 X 家；两表分流零混写声明
   【数据增量】十一表基线 vs 终态（含 ig_equity_edge 新表）
   【施工件】DDL v4/脚本/测试清单+commit hash
   【开放问题】306 unspecified/44 超阈值甄别/孤岛链等待 Owner 拍板清单
   【循环审查结论】各循环引擎违规数序列（violation_trace）+退出原因（two_zero_cycles/timebox/non_convergent）
   【断点与续跑】剩余违规+剩余扩产+下次从哪继续
