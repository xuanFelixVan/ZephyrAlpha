---
ttl: task_bound
title: 终极总令全文存档——ZephyrAlpha 大升级·收尾三期（Owner 2026-09-19 下达，st-final3-20260919 承接）
note: 本件=Owner 指令原文逐字存档（战役章程，只读不改）；执行态与进度看 a1_campaign_ledger.md；working 审查明细看 w9_triage_ledger.md
---

# 【终极总令】ZephyrAlpha 大升级·收尾三期——十战线+working 清零硬门禁
# sid 建议：st-final3-20260919 ｜ 落盘：docs/_working/final3_campaign/ ｜ 执行全程=GLM 5.3 Flash

## §0 终极目标与子目标（先读，一切任务服务于它）
**终极目标**：本项目全部在册工作收尾清零——所有战役遗留执行完毕、working 任务书
全部归档、全资产内收机制化、自动化链路全通全绿，最终状态=「无未完成的在册任务书」。
**七大子目标**（每条有唯一验收）：
S1 规则审计施工落地（判决#340..#360 执行完毕，门禁体系口径干净）
S2 bizmine2 闭环（骨架挖矿封矿+P0 五件+裁定解锁项执行）
S3 工程债清偿（复权链修复=最高优先，解除一切日线结论"暂定"）
S4 全景图捋顺（TDM 唯一地图+传导链补边+门禁缺口）
S5 全项目内收（资产总量下降+机制化+SOP v5）
S6 前端自愈（8890 一体化+自启+看门狗）
S7 **working 清零（硬性门禁）**：完成一件归档一件，最终 docs/_working 只剩
   活目录（在飞）+常驻手册+资料仓+本战役目录，任务书类文档清零。

## §1 模型路由
Flash 执行全部；遇分叉默认保守处置+登记继续。Max 只在五关卡介入：翻案/门禁语义
变更/破坏性执行前/头条数字/Owner 门位（资金/生产流转/注册表净删/flag 翻转）。
禁虚报；未达成如实写原因。

## §2 冷启动（每 shell 必做）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
会话注册+心跳+提交同 shell 链（90s 活性窗）；宪法 AGENTS.md 全程有效。

## §3 真源读序（开工前，约 60 分钟）
1. docs/_working/rule_audit_campaign/2026-09-19-max-dayshift-rulings.md（判决书）
2. docs/_working/rule_audit_campaign/2026-09-19-construction-handover-prompt.md（A0-H 施工序+坑册）
3. docs/_working/bizmine_night/next_session_directive.md + owner_package.md
4. docs/_working/bizmine_chain_mining/a0_master_plan.md（在飞会话避让）
5. docs/_working/final3_campaign/w9_triage_ledger.md（W9-0 落盘的 working 审查台账）
6. docs/01_policies_and_standards/sop/audit_prompts_20_ai.md（v5 升级对象）

## §4 硬事实（实测勿重查）
st-bizmine2 在飞（挖矿骨架）；主区 132 条脏区（--files 白名单提交，禁 add -A）；
其 claim=ruling_registry+capability_registry+判决书（撞锁等 5 分钟）；队列 0 积压/
dead 1033 历史；ETF 时区已修（verify=0）；TDM 138 节点/194 边；传导链 583/873=67%；
api_server@8890 已独立进程存活；docs/_working 164 对象四态=A24/B4/C112/D20/E4
（明细=W9-0 台账）；deep_review 台账与实际疑漂移（先对账）；归档区=
docs/_working/archive/（既有）+docs/_archive/。

## §5 组织形态与自适应最大并发（Owner 定：不设人工上限，自适应探顶）
1. 总包主会话只做统筹（派单/验收/裁定登记/收口），细节读真源不复述。
2. **自适应爬坡协议**：起步 4 个并行子代理（今日实测 4 并发零死亡）→每完成一波+2
   探测→任一代理死亡/超时即降 1 档稳态→每小时重探一次（额度跨会话共享，st-bizmine2
   在飞会分走额度，额度浮动是常态非故障）。当前探到的档位写入战役台账。
3. 机械扫描（统计/grep/盘点类）一律 Python 脚本并行，不占代理额度。
4. 本机 worker≤20 红线（50 曾压死宿主）；代理任务幂等可重派（死=重派不丢）。
5. 分包指令自包含（公共纪律段整段下发，拼装协议照 audit_prompts 第 0 章）。

## §6 十战线（全局唯一编号；【M】=Max 复验关卡；【O】=Owner 门位只备料）

### W1 规则审计施工（S1）
A0→A1→B/C 并行→RA-G(#359)→D 批(等 claim 空窗)→E 批→RA-H2 机械波(B 批后开，
便宜会话承接)→A1 完即停（判案 RA-F 归 Max）。红证双向+回执六要素照交接令。
【M：#351/#357/#359 红证】

### W2 bizmine2 并轨（S2）
BM-1 活性判定；BM-2 P0 T1-T5；BM-3 X-0 登记后 P1 解锁项（CRY 重判#3/tick 矩阵#6
三条件/组队窄测#1）；BM-4 SOP 转正#5；BM-5 E 盘工单#7。

### W3 工程债清偿（S3）
X-0 裁定登记批（10 项代裁，取号 max+1）【等 claim 空窗】；
X-1 死信清账；X-2 **复权链施工**（升级为施工项：data_handler.py:335 表名+adj_factor
缺取、akshare_provider adj_factor 恒 1——原"归整改队"禁令由本战役承接解除；预注册
修复方案先【M】后施工；修完按 RB 优先序全量复核暂定结论）；X-3 flash_speedup §2.1
核验；X-5 N-6 merge 施工【M】；X-6 #ARCH-337 观察；X-7 十大股东断供修复（最新
2026-05-15 滞后 4 月，归因+补齐+登记）。

### W4 全景图捋顺（S4）
W4-1 290 条无传导边链三分法；W4-2 ig bak 90 表清理【O】；W4-3 三门禁缺口立项
（链活性卡/新图准入/排班一致性 reconciler）；W4-4 总排班视图（三表一入口，物理表
不合并=Owner 裁定）；W4-5 TDM 唯一地图裁定落地（禁建第二张流程图；"10 层架构+PDF
模型族"不立项=防幻觉锚点）；W4-6 服务自启【O】；W4-7 TDM 吸收批（十层决策点并入，
D108 决策表/状态机承载）【M：差距表】。

### W5 内收大升级（S5）
判据铁律：同真源可派生→必并｜零触发零消费→退役｜同域重复簇→收敛唯一｜跨域不同
对象→不并。
W5-0 十类资产总盘点建档（模块/脚本991/注册表75/门禁113/图10/SOP/文档/配置/DB表/
服务；Python 并行扫描）；W5-1 逐域内收审计（22 域分包，三档清单）；W5-2 合并执行批
【O 签字后】；W5-3 机制固化：宪法 §4 等长替换（全资产净零+季度合并审计+总量仪表）+
audit_prompts v4→v5（内收审查义务条+域模板节+过时数字重取）+立项判据门禁化。
【M：宪法改动】

### W6 前端自愈（S6）
W6-1 api_server 挂 StaticFiles（8890 页面+数据一体）；W6-2 壳入口切 8890+
描述同步；W6-3 自启+看门狗【O】。

### W7 股权穿透底座（S2 数据线，设计真源已 100%）
按 docs/_working/altdata_line/02_entity_graph_equity_person.md：W7-1 建表批
（node_entity/person/company+edge_holding/role/link，PG 图库同域）；W7-2 A 层灌入
（前置 X-7 修复）；W7-3 穿透查询视图 v1（804 股权边并入）；W7-4 B/C/D 层与人员
任职边登记后续波次。

### W8 working 大收尾（S7 硬门禁，基于 164 对象审查）
W8-0【P0，第一件】审查台账落盘：将本令附带的四段审查结果（散文件×3 段+目录×1 段）
整理为 final3_campaign/w9_triage_ledger.md（每对象一行：路径|态|依据|待办指针）。
W8-1 立即归档批（28 对象：A24+B4 → docs/_working/archive/2026-09/；例外：3 份
"C-3 保留至季度末"延至 09-30；clean_exam 归档前确认编排器工单已移交；git mv 走
正门+RENAME 门禁）。【O：批量移动签字】
W8-2 C 类待办消化（112 对象约 300+ 待办）：先与本令 W1-W7 去重（已覆盖≈40%），
剩余按四桶派发：①可机械执行→当班施工；②需设计→预注册卡+施工；③Owner 门位→
W8-3 签字会打包；④已被后续工作实际完成但台账未销→对账销项（deep_review 160
待审疑此症，先 git log 对账再重跑）。
W8-3 Owner 签字会材料包：把散落全部"待 Owner 拍板"项（kimi_audit S3 96 条+
szopen 28 接口地址+各文档拍板项）按主题归拢成 ≤10 页签字册，一次性送签，禁逐条打扰。
W8-4 **归档硬门禁循环（S7 本体）**：每完成一项→其载体文档表头写终局状态块（完成
日期+commit+去向）→移入 archive/→台账销项。周而复始，直至 C 类清零。终态验收=
docs/_working 仅存：活目录（bizmine 系/rule_audit/automation/ai_layer/factory/
full-auto-chain/trading_vision/fullflow 等在飞+常驻）+guides/reviews 手册+E 资料仓
+final3_campaign 本战役目录。每轮循环检查必报"working 剩余 C 类计数"趋势线。
W8-5 抢救与清淤：主区根下 2026-09-19-max-dayshift-rulings.md 的 AD staged 副本
（真源已提交易主，按三分法 git restore --staged 清除）；4 份被 09-15 交接引用的
C 类文档先消化引用再处置。

### W9 收官循环（S7 终验）
连续两轮 0 问题（commit 祖先+产物在盘+队列无新死信+**working C 类计数不增**）→
红蓝一轮（红队重点：内收误并攻击/TDM 吸收语义/归档误埋活件）→Gateway 全落地→
临时件清→终局交付报告（六要素+七大子目标逐条验收+working 清零前后对照表+资产
总量内收前后对照表）。W1 判案（RA-F）与全部 Owner 门位登记即闭环，禁代裁。

## §7 施工纪律（坑册浓缩）
提交唯一正门 git_commit.py --enqueue 配方+--files 白名单+commit 后 git log -1
--name-only 核归属（完整坑册=rule_audit 交接令，照抄勿探索）；改前 claim；新文件
token 同批；热文件 CAS；bash heredoc 吞字符→Write 落文件再跑；.md 带 ttl
frontmatter；EXEMPT-ZONE-FM 禁 doc_type；FOLDER-CAPACITY 120 超限入子目录；
禁碰清单=AGENTS.md/docs/03_modules/TDM yaml/tasks.yaml/pipeline_events.py/
apply_market_tables_ddl.py/data/strategy_intake/N-5 件/他会话 WIP；生产表只
append；测试 tmp_path；LLM 走 LSG；计数必带口径。

## §8 回执格式（每批一段，缺项=未完成）
①改动文件+commit hash（核归属）②红证双向（注入→红→撤样→绿）③验收命令与实测
数字（禁引旧数）④停手/Max 复验/Owner 门位项 ⑤证据等级[亲验]/[转报]/[推断]
⑥未完成部分+原因。每批必附：working C 类剩余计数、自适应并发当前档位。### W9 追加（并入收官循环）
- W9-6【P1】分支清零批：
  ①45 条已并入 dev 的尸体分支批量删除（git branch -d，已 merged 零风险，
    一批一提交留清单）；
  ②2 条工棚分支（auditdoc-v4/ruledisp）随工棚收尾三连（核 PID terminate
    heartbeat→unregister→abort worktree→删分支）；
  ③2 条裁定尾巴（sowner002-regime-switcher=裁定"留分支"件、tv2terrain=
    做T#304 已封存）出终裁材料并入 Owner 签字册（并入 or 废弃二选一），
    裁决后执行；
  ④远端 4 条分支清单登记，治理归 Owner 单独决定；
  ⑤终态门禁：git branch --no-merged dev 输出为空 + git worktree list 只剩
    主仓，计入 S7 终验。
