---
status: closed
title: "collection_intake 结案报告"
module_id: ""
blueprint_id: ""
version: "1.0.0"
created: "2026-09-21"
updated: "2026-09-21"
ttl: task_bound
---
```

# collection_intake 结案报告（收藏情报包拆解与内外挖矿战役）

## §〇 判定

- **战役名**：Owner 收藏情报包拆解与内外挖矿判定台账 2026-09-20（`docs/_working/collection_intake/README.md` L7 标题原文）
- **执行会话**：st-collintake-20260920（README L3 frontmatter `session: st-collintake-20260920`；L9 “Owner 授权令：先内部挖矿判‘有没有/能不能用’，再对外挖矿补缺口，分类落档”）
- **状态**：**已结案**。判定依据：
  1. 主体交付 15 件全部落地并固化为 HEAD 祖先——三笔 commit 实锤：`9d609be2a3`（2026-09-20，14 件 + registry，630 insertions）、`924c4e7376`（2026-09-21，R2）、`8f7d91fb22`（2026-09-21，R3），`git show --stat` 逐笔核实文件清单；
  2. 独立承接载体已建立——`docs/_working/recovered_task_cards/tc_10_collection_intake_followups.md` L4 verdict 原文：“主体三笔提交全部固化为 HEAD 祖先、15 件交付物零缺失；六项后续无一项开工，维持‘等 Owner 点单’合法稳态”；
  3. 唯一带时限缺口（批 10 挂接）已于 09-21 夜回写完成——`docs/_working/unified_campaign/p2_workorders_v1_0.md` L39：“【扩项 2026-09-21 tc_10 挂接批·Owner 今夜范围令第1波】……本段即回写”。
- **核心证据**：README L12 §0 一页结论原文：“**25 条中 0 条可直接照搬照抄；9 条内部已有等价物或数据已在库（A）；8 条部分有需补齐（B）；3 条是真缺口值得立项（C）；5 条证伪/存档（D/E）。**”与 commit 9d609be2a3 message “判定9A/8B/3C/5DE” 双向一致。

## §一 已完成项清单

| # | 内容 | 证据路径 + 原文关键行 | commit |
|---|------|----------------------|--------|
| 1 | **25 条判定台账全量落地**（9A/8B/3C/5DE），四路并行挖矿（内部数据面/内部工程面/外部因子/外部工具） | `docs/_working/collection_intake/README.md` L24-50 台账表 25 行；L11 方法行：“4 路并行挖矿……证据分级标注” | 9d609be2a3 |
| 2 | **14 件交付物首批落库**（README 1 + 因子规格 5 + 工程 3 + 工具 3 + security 1 + misc 1） | git show --stat 9d609be2a3：`docs/_working/collection_intake/` 下 14 文件共 630 insertions；commit message “CREATE-GUARD collection_intake 14 token 同批登记” | 9d609be2a3 |
| 3 | **CREATE-GUARD 能力登记**（15 件全部注册在册） | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` L41783-L41855 grep 实证 15 条 `file: docs/_working/collection_intake/...` + `capability: collection_intake`（14 条出自 9d609be2a3 +75 行，1 条出自 924c4e7376 +5 行） | 9d609be2a3 + 924c4e7376 |
| 4 | **最高价值发现①：期权 PCR 交易所官方免费源**（唯一值得新立项的数据批） | `README.md` L28 判定列：“C：P1 数据批立项”；`factors/factor_spec_options_pcr.md` L28-31：“交易所官方每日发布 PCR，免费……akshare `option_daily_stats_sse(date)` / `option_daily_stats_szse(date)` 直接返回官方 PCR 字段” | 9d609be2a3 |
| 5 | **最高价值发现②：筹码集中度与批 10 拼合配方** | `factors/factor_spec_chip_concentration.md` L10：“配方与批 10 筹码族天然拼合，判定 B……70% 集中度只差 cost_15/85 两列输出”；L18 通达信口径集中度公式 | 9d609be2a3 |
| 6 | **最高价值发现③：两个网红项目证伪** | `README.md` L31 eclassic：“**查无实据，判定不存在** `[外部]`”；L43 Anthropic Fast Start File：“**GitHub 全站 0 命中+黑客松名单无记录→不存在**”；`misc/misc_unverified_items.md` L11-13 Jev：“真实存在……TypeSafe AI……2026-09-15 官宣……营销性官宣——无同行评审、无公开权重” | 9d609be2a3 |
| 7 | **P0 安全行动项查证（R2 实测版）**：ZCode 静默上传事件本机取证 | `security/sec_zcode_workspace_upload.md` L14：“`"repoSnapshotIndexingEnabled": true`”实锤；L15 “开关一直开到今天……v3.14.1 后该键已消失”；L16 定性：“高度可能已上传……按已泄露处理”；L17 暴露面：“registry 合计 **100 键**”；L21-27 处置五条（轮换/等审计/关中继/月度巡检/战略结论） | 924c4e7376（重写为 R2 实测版） |
| 8 | **QuantCombine 思想挖矿（R2 追加）**：11 步组合优化管线 + AutoAlpha 五思想 + 行为聚类双身份证 + 六角色权限模型 + 审计三件套 + 从零复建 10 步蓝图 | `engineering/eng_quantcombine_idea_mining.md` L19 “约 11 步确定性管线，四种模式”；L9 法律边界：“PolyForm Noncommercial 1.0.0 = 代码一行不抄、文案不搬”；L11 定位：“FAC-E7/E8……立项时的**设计输入件**——不是 SOP，不是真源” | 924c4e7376（新增 77 行） |
| 9 | **Owner 修正案入档（R3）**：统一考尺+分卷考试 | `engineering/eng_quantcombine_idea_mining.md` L79-87 §8：“**统一的是‘考尺’，不是‘考卷’**……因子按目标状态分科……切换器换状态=换队伍……与 Owner 自上而下层级行为（大盘→板块→个股→做T）和 regime 切换器天然对齐” | 8f7d91fb22（+10 行） |
| 10 | **HL 数据面判定 A**：Hyperliquid 四表已在库+资金费 465 万行 | `README.md` L46：“**HL 四表已在库+资金费 465 万行（2023-05-12 起）** `[亲验]`……A：数据已接” | 9d609be2a3 |
| 11 | **营销话术黑名单沉淀**（防再污染） | `misc/misc_unverified_items.md` L21-26 四条：“成功率接近100%”“夏普3.95”“黑客松冠军/半小时/$1.6 一天”“快100倍便宜100倍” | 9d609be2a3 |
| 12 | **批 10 挂接回写 unified 台账**（TC-10 时限缺口关闭，登记完成） | `docs/_working/unified_campaign/p2_workorders_v1_0.md` L39：扩项 chips_cost_15/cost_85 两列 + CHIP_CONC_90/70 两指标，“真源 docs/_working/collection_intake/factors/factor_spec_chip_concentration.md……本段即回写”；`p2_backlog_master_ledger_v1_0.md` L56 同步；计数 138→145 | 非本战役 commit（tc_10 挂接批，09-21 夜） |

（注：8 件未亲读文件——`factor_spec_huanfang_ten.md`、`factor_spec_alpha101_191_158.md`、`factor_pool_comment_leads.md`、`eng_agent_lightning.md`、`eng_benchmark_llm_quant_factory.md`、`eng_factor_methodology.md`、`tools/` 三件——其存在与行数经 git show --stat 实证，判定内容以 README 台账对应行引用为准，细节内容本报告标 UNCERTAIN。）

## §二 未完成项 / 挂起项（含承接指针）

| # | 事项 | 现状证据 | 承接指针 |
|---|------|---------|---------|
| 1 | **P0 密钥轮换（Owner 亲办）** | TC-10 卡 L30（2026-09-21 实测）：“**仍未换/未登记**：.env mtime=2026-09-16 15:05（早于 09-18 曝光，曝光后从未改写）”；此前是否已轮换=**UNCERTAIN**（Owner 线下动作，范围锁内无更新证据） | TC-10 步骤 5：Owner 叫核对时 AI 待命（只报键名/mtime，绝不打印值）；基准清单=OKX（只读+IP 白名单+禁提币）/iFind/百度网盘 token 必换 |
| 2 | **P1 期权 PCR 数据批** | 未开工：本仓 grep `option_daily_stats` 于 src/、data/ 零命中；TC-10 L31 同结论“全仓零命中” | **流向数据批线**：TC-10 步骤 2，触发=**Owner 点单**；施工依据=`factors/factor_spec_options_pcr.md`（新表 `c1_market.option_daily_stats` 三口径 PCR 列 → tasks.yaml 日频任务 → MOD-SIG-059 option_sentiment 改读表扩三口径 → 历史回补 → 假设卡过 E4，施工前走 construction_workflow_policy 15 步）；顺带项 option_risk_indicator_sse 回补 greeks |
| 3 | **P1 批 10 筹码集中度扩项** | 登记已完成（见 §一#12），**施工未开始**：src/ grep chips_cost_15/cost_85/CHIP_CONC 零命中 | **流向 unified 战役甲线 W4·WO-4**（施工主权方，`p2_workorders_v1_0.md` L37-42，状态“活”，时间盒 1-2 天，红证=注册表基线+5）；前置=读裁定 #257④；峰突破/发散信号规则卡在 WO-4 范围内勿再漏（TC-10 L56） |
| 4 | **P2 三小活**（均未消费） | ①trade_when 白名单：grep `trade_when` 于 src/ 零命中，TC-10 L33 “config/factor_mining_whitelist.yaml 零命中”；②E4 拥挤度维度：TC-10 L34 “regime_validation/ 零命中，最后提交 09-16”；③pf_alloc 接电立项：TC-10 L35 “‘零生产调用方=不接线挂触发’裁定仍生效” | TC-10 步骤 4，触发=Owner 点单；③另需解除 pf_alloc 挂触发裁定；AI 层 Agent Lightning 观察项挂 AI 层路线图（`README.md` L82，详见 `engineering/eng_agent_lightning.md`——内容细节 UNCERTAIN，未亲读） |
| 5 | **月度巡检自动化** | TC-10 L36：“未挂：schtasks 六个 ZephyrAlpha 系任务无巡检项” | TC-10 步骤 6：du .zcode 体积 + repoSnapshot 键巡检，“可搭现有 IOCheck-Monthly 车辆”，触发=Owner 点头 |
| 6 | **向 Owner 报到待令**（唯一点火机制） | TC-10 L42：“交接令要求的‘向 Owner 报到待令’一步无证据显示有会话做过” | TC-10 步骤 0：读 README 第三节台账后向 Owner 呈报六项触发清单并待令——“不报到则六项后续永无人触发” |
| 7 | **未消费设计输入（待立项建议）** | ①QuantCombine 复建蓝图 10 步：定位为 FAC-E7/E8 立项设计输入（eng_quantcombine L11、L77）；②Agent Lightning C P2 AI 层候选（README L42）；③Alpha101 入库路线就绪待 E4 重考（README L29，细节在未亲读文件，UNCERTAIN） | ①与 TC-07 组合层立项互认同源（TC-10 L49/L66 “eng_quantcombine 是两边共同设计输入”）；②③各自随 TC-10 步骤 4 与后续点单流转 |

## §三 方法论范本注记

**本册为情报拆解方法论范本，随档保留防误删。**

- **A-E 判定分档口径**（`README.md` L14-20 原文，五档自含定义）：
  - “**A 已有可直接用**：内部已有实现/数据，无需外采。”
  - “**B 部分有需补齐**：有底子，列明具体缺口与补齐路径。”
  - “**C 缺失需立项**：内外确认有价值且缺失，给立项建议（P0/P1/P2）。”
  - “**D 存档不立项**：有价值但当前不排期。”
  - “**E 证伪/存疑弃用**：查无实据或营销内容，禁止作为决策依据。”
- **证据分级四档**（`README.md` L11 原文）："`[亲验]`=本会话代理实查（附路径）、`[外部]`=全网核实（附 URL）、`[记忆]`=项目记忆、`[存疑]`=未证实"。
- **范本价值佐证**：该口径已被承接方原样复用为“本线专属配方”——TC-10 卡 L78 执行冷启动提示明文记载“汇报口径：大白话+先给结论；判定分级 A 已有/B 补齐/C 立项/D 存档/E 证伪”；且"营销话术与业绩宣称分离"（配方收下、话术弃用、宣称按零先验入 E4）在本册三处落地（misc L23-24、pcr L9、chip L9），是后续任何情报包拆解线的直接可复用范式。

## §四 归档注记

- **归档目的地**：`docs/_working/archive/2026-09/`（Owner 指定；目录已存在，grep/ls 实证内有同期结案报告惯例，如 `2026-09-14-backup-handoff-closure-report.html`、`2026-09-01-ds-compliance-scan.md`）。建议落位 `docs/_working/archive/2026-09/collection_intake/` 保持子目录结构完整（15 件含 5 子目录）。
- **下游引用情况**（归档前须同步或确认可解析，共三处）：
  1. `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` L41783-L41855：15 条 `file:` 指针直指 `docs/_working/collection_intake/...`——此为 capability_lookup 检索入口，**归档改路径后须同步登记**，否则能力反查断链（REGISTRY gate 关联）；
  2. `docs/_working/unified_campaign/p2_workorders_v1_0.md` L39 与 `p2_backlog_master_ledger_v1_0.md` L56：WO-4 扩项**真源指针**明文指向 `docs/_working/collection_intake/factors/factor_spec_chip_concentration.md`——WO-4 状态“活”、时间盒 1-2 天，施工时将按此路径读配方，**归档必须保留可解析路径或先行更新两台账指针**；
  3. `docs/_working/recovered_task_cards/tc_10_collection_intake_followups.md` 步骤 0/2 依据路径指向 `README.md` 与 `factors/factor_spec_options_pcr.md`（施工依据）——TC-10 卡本体在 recovered_task_cards/ 不随本册归档，其指针需在归档后仍可解析。
- **归档后查档路径**：
  - 物理位置：`docs/_working/archive/2026-09/collection_intake/`（归档执行后）；
  - 永续 git 查档：`git log --all -- docs/_working/collection_intake/` 命中三笔 `9d609be2a3` / `924c4e7376` / `8f7d91fb22`；任意历史版本可 `git show <commit>:docs/_working/collection_intake/<file>` 读取（如 `git show 924c4e7376:docs/_working/collection_intake/engineering/eng_quantcombine_idea_mining.md`）；
  - 台账口径速查：本报告 §〇/§一 已固化 25 条判定分布（9A/8B/3C/5DE）与六项后续承接指针，随档即查。

---

**结案官附注**：本报告为只读产出，未写任何文件、未执行任何 git 写命令。全部判定基于 6 件亲读文件（README、eng_quantcombine_idea_mining、sec_zcode_workspace_upload、factor_spec_options_pcr、factor_spec_chip_concentration、misc_unverified_items）+ 全仓 grep（registry、TC-10 卡、unified 台账、src/ 消费痕迹）+ `git log`/`git show --stat` 只读核实；未亲读的 8 件内容细节已逐处标注 UNCERTAIN。
