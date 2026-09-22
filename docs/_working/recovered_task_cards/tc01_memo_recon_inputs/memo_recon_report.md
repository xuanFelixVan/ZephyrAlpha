---
ttl: task_bound
session: st-xhs-full-20260922
topic: tc01_memo_recon_inputs
---

# 备忘录对账案卷（2026-09-20）—— 供独立复审

## 0. 元信息

| 项 | 值 |
|---|---|
| 核查执行 | Qoder 会话（本区），2026-09-20 |
| 仓库状态 | `D:\ZephyrAlpha`，分支 `dev`，HEAD=`1ad0003e36` |
| 工作方式 | **纯只读**。未 Edit/Write 任何仓库文件、未 `git add`/`git commit`、未跑生成器（`align_all.py`/`generate_project_depgraph.py`）、未跑 `commit_queue.py drain/requeue`、未连生产 DuckDB、未跑测试套件、未启停计划任务 |
| 手段 | 5 个只读子代理分簇扫描 + 本会话亲自复算 8 项关键数字（见 §3 各条"等级 A"） |
| 交付性质 | **案卷，非裁定**。本报告内所有判定都待独立复审确认或推翻 |

**证据等级定义（本报告每条判定都标了级）**
- **A**＝本会话亲自读到原文或亲自跑出计数（附可复现命令）
- **B**＝子代理回报，本会话未复算
- **C**＝由间接证据推断，未见直接实证

---

## 1. 前因：Owner 输入原文（逐字，未改写）

Owner 请求："以下是我最近大概两个星期的一些聊天记录。你可以全面看一下，这里面哪些东西是不是都已经完成了？全面地搜查一下、看一下，应该基本都完成了。只是我整理一下聊天记录，如果都已完成的，我就可以从我的备忘录里面删除。**只检查不执行**，内容如下："

```
## 二、遥测归档开关：大白话解释
它是什么：一个还没开工的工程预留的开关。类比：你家装修时电工在墙上预留了一个开关位+接线盒，
但对应的灯还没装——现在按这个开关什么也不会发生，但位置和线路都留好了。

将来装上"灯"后干什么：现在系统的监控（性能指标/日志/追踪）都是热数据——只放在内存里供实时看，
不留历史。这个开关对应的功能是"归档"：把监控数据压缩打包存档 30 天。用途是事后复盘——比如
"上周三那次提交为什么慢""上个月哪个模块报错最多"，没有历史存档这些问题就只能靠猜。当前监控靠
后台守护进程实时刷新，够用，所以它排在后面没做。

为什么确定它不是"沉睡宝藏"：它的状态字段明写 not_started（未开工）——不是"做完了没开"，是"还没做"。
真正的"宝藏没启动"长这样：代码完整、功能可用、只是开关关着。这个不是。

## 第 1 条：field_dictionary 登记缓办（一张字段登记表，我决定暂时不填）
这是什么：项目里有张"字段字典登记表"（REG-FLD-001），专门登记数据表里每个字段是什么意思。当初讨论
工厂图时说过"以后要把工厂图的字段也登记进去"。

我查了实际情况：这张表只管"数据层字段"（比如行情表里 close 字段是啥类型）。而工厂图的 15 个节点里，
那些要存数据的入库位全部还是"待定"状态（还没开工建）——皮之不存，毛将焉附，没有实体就没有字段可登记。
而且交易决策地图（TDM，先例）当年也是这么处理的：节点字段不进这张表。

我的决定：等将来第一个数据工件真建起来了，再连同它的字段一起登记。现在填=填一堆空气。
需要你做什么：不用做任何事。默认同意即可。如果你坚持"现在就要登记"，跟我说一声，我补上。

老数据全量重验：您担心得对，我抽查时已看到有"券商作者被当成产业链公司"这类误挂。验证方案：机器三重
检查（股票代码有效性 / 供货方向是否说反 / 两个独立来源互相印证），全量跑完出报告，可疑的单独清。

详情页支撑：您的设想完全可行——点一家公司，显示"谁买我的货（下游客户）/我买谁的货（上游供应商）"，
数据底座（5 万多条）已在库里。而且您说的"当上下游验证支点"也很准：客户名单里的公司必然在它的下游，
正好用来核对图谱连线方向。后端查询通道+接口规格我下一步出，前端接线可以给 chainmap 前端会话。

消费端（比如把"台风后 N 日 BDI"做成正式因子卡），或者继续第 3 批（政府采购网爬虫试点）。

dead/ 剩余 953 条门禁拦截死——属他会话产物，任务单只授权 25 条 clean 死信，已按授权边界处理完毕。

挂账给别的会话的（不是我的锅，不代修）：全图对齐还有 16 个硬报错，全部来自并行会话（st-expectation）
刚入库的预期因子族——他们预注册的因子引用了还没建的数据表字段，属于"先开菜单后进食材"的时序问题，
要他们自己决定怎么修（改菜单写法/补食材/给预注册豁免，三选一）。

等数据的（不是不想干，是不能干）：答你的问题：16 个硬报错一半是我的（8 个 FQ/GR），一半是姊妹线的
（8 个 EXP）。根因相同：注册表 inputs 字段写了自由文本描述（"某表对应列"），但门禁要求引用字段字典的
真源 ID。我的 8 个 FQ/GR 因子是我在上一批注册时写的描述性格式——是我的锅，我现在就修。姊妹线 8 个
EXP 是同样的问题，她们自己修。

需要你做的事（仅剩 2 件）
9/17 前：bdpan tick 8 天缺口手工挂载（百度云下载→导入，miniQMT 退役后无来源）
每交易日：通达信金融终端 + 大QMT 实盘终端保持盘中开着（三条数据线靠它们）

你名下现在真正剩的：零。之前列的 4+1 项全部清账。
系统侧自动运行的下一站：今晚 15:35 全量挖矿 → 17:30 双窗批考（今天日期已修正注册）→ 明早 09:25
PaperSession 首跑 → 周六起例跑常态化。对话可以关闭。

ALGO_FLOW 战役是什么：你的代码库里，每个重要算法旁边都埋着一份"机器可读的说明书"
（[ALGO_FLOW]...[/ALGO_FLOW] 格式的注释块），总共 3,302 份、约 15.4 万行。这带来两个毛病：
代码被说明书撑胖了；说明书会烂（"见第 133-153 行"这类引用代码一改就错位）。
这场战役干的事就一句话：把说明书从代码里搬出去，搬进统一的图书馆
（docs/03_modules/各域/algo_flow/ 下一份份 YAML 档案），代码原地只留一行路标写着"说明书在图书馆 X 架"。
搬完的效果：3,158 份说明书全部上架、3,158 个路标与图书一一对应、代码里一个内联说明都不剩。
而且搬出去的信息无损——工具加载时走的还是原来那套解析管线（搬运器自带"逐字节一致否则自动回滚"的保险）。

daban 链是什么：daban=打板（追涨停板）策略。"链"=从数据到仓位的一条流水线，之前它是两头断的废管子：
上游断：涨停池、连板、炸板这些数据表早就建好了，但没有任何程序往里写数据；
下游断：四个打板选股引擎（selector/youzi/quant/fusion）装好了，但没有任何东西把表里的数据喂给它们；
中间还有暗坑：周末不交易却会生成"周末数据行"（幽灵行）、涨停价阈值是拍脑袋的平阈值而不是查真实涨跌停价表。
今晚这条管子全程接通了：真实数据 936 行入表 → 四引擎真读真打分 → 产出真实仓位权重（实测某日选出 4 只、
每只 15%、单票上限截顶生效）→ 抽验涨停家数 30 只，和权威口径精确吻合。从"建了管子没通水"到"水表转了"。

车道群质量高吗——高，但有网兜底：每一笔提交都过了一百多道门禁，零绕行；他们会用预注册协议证伪自己
（WYF-3 重校跑了 160 个参数组合没有一个合格，结论是"阈值不动、这维度判据层有病"）；RSC-2 做成"默认行为
逐位零漂移"；有主动认错（decision-gate 车道自己撤回了"DSR 判定源共用"的说法）；多车道撞车不内耗
（三处工作重叠，后到的一方审计对方成果后收编+署名）。
但要说透的另一面：高速冲刺下确实出了伤——出仓器两代映射 bug、一次控制字符写坏注册表、几笔 message 不
规范的 probe 提交、28 份蓝图模板漂移。区别在于：每一处都被门禁或红蓝当场抓住、当场修、登记留痕。
一句话总评："会犯错但错不过夜"的车道。

（Owner 手输想法，2026-09-17 05:48~06:27）
资本链+自然人全网信息面 / 各路资金模拟 / 个股庄股行为模拟 / 人性推导链条 /
生日 八字 星座 性格推导 数据 行为逻辑 / 全网新闻

（恢复令附带·施工环境已升级，三条新规）
1. Kimi 深度裁定班已终局：裁定#304-#326 已入 ruling_registry，docs/_working/kimi_audit/ 下 93 份蓝图
   的裁定回写批次可能还在 staged 未落地——恢复施工前先 git status 查 staged：若蓝图批次仍未落地，
   提交走队列正门（--enqueue），别直连抢锁；落地完成后恢复常态。
2. 提交链正在提速施工（另一车道在做 F1 衍生并入/F4 生成器并发化）：未来几小时可能出现门禁行为微调
   （integrity 尾笔消失属正常与预期，不是故障）。
3. 裁定#304 已砍做T v2 战役现形态、#305 切换判据定稿、#306 尺子 v2 提案——施工若涉及策略考试/组合门/
   做T 相关设计，先读 docs/_working/kimi_audit/owner_fast_sign_20260917.md（结果总表一页读全场），
   别按旧口径施工。

交易成本模型是全项目最强且主动自我加难度的那一项：5,519 标的 / 1,312 万条五档快照自标定，滑点 ADV
五分位 2.34~7.24bp，是旧假设 1bp 的 2.3~7 倍。主动让自己更难看，这是机构尽调里的强正向信号。防前视做成
硬断言（LookaheadExecutionError）而非注释，也是真做法。
```

---

## 2. 核查方法

**子代理分簇（各 5 路，全部只读）**
| 簇 | 覆盖条目 |
|---|---|
| chk-chainmap | 老数据重验 / 详情页 / 消费端两选一 |
| chk-registry-align | field_dictionary / 16 硬报错 |
| chk-campaigns | 死信区 / ALGO_FLOW / Kimi 裁定 / F1-F4 |
| chk-ops | 遥测开关 / tick 7 日缺口 / 定时运行实证 |
| chk-ideas-daban | 六个设想 / daban 链 / 成本模型+防前视 |

**本会话明确未做的实测（复审若做，属新增面）**
1. 未跑 `align_all.py` ⇒ 全图对齐**其余八节**的硬报错数未知（本报告只覆盖 inputs 那一节）。
2. 未连 DuckDB ⇒ 一切"行数/覆盖天数"结论引自盘上日志与报告文件，非本会话直查。
3. 未查 Windows 计划任务表 ⇒ "FactoryLaneC 现 Disabled"引自 `p7a_ac_family_rulings.md:210` 的文字。
4. 未递归统计 kimi_audit 蓝图总数（只数了顶层 29 件，见 §5 第 5 条）。
5. 未跑任何测试套件。

---

## 3. 逐项判定（17 条）

> 判定口径三态：**终局**（可删）/ **仍开**（别删）/ **叙述过期**（要改写）。

---

### A1 遥测归档开关 —— 判定：**叙述过期** —— 等级 A/B 混

- Owner 原述：状态明写 `not_started`，"不是做完了没开，是还没做"，"真正的宝藏没启动长这样：代码完整、功能可用、只是开关关着。这个不是"。
- 实测：
  - 开关确实仍关着且字段仍写 not_started：`config/flags.yaml:45-50`
    ```yaml
    archive:
      enabled: false
      description: "遥测数据归档 (未实现，保留flag)"
      retention_days: 30
      compression: "gzip"
      implementation_status: "not_started"
    ```
    （**等级 A**，本会话直读）
  - 但"代码没写"这半句站不住：**等级 B→A 部分复核**——`src/zephyr/infrastructure/system_telemetry/archive/cold_stub.py` 内有 `class RetentionPolicy`(L55)、`def compress_dir`(L97)、`def rotate_by_ttl`(L118)；`facade.py:474-476` 真的 import 并调用了 `rotate_by_ttl()`（本会话 grep 亲验存在）。首提交 `787f7a6ba4`（2026-05-06）。
  - **零读者**：全仓 grep `flags.*archive` 无消费方（等级 A，但 grep 口径窄，见 §5 第 3 条）；`data\telemetry\` 下只有 `logs`，无 archive 产物。
- 改写建议：不是"预留开关位没装灯"，而是"**灯装了、线也接了一半（facade 会调 TTL 轮转），但没人读那个开关、且从未产出归档件**"。
- 复现命令：
  ```bash
  sed -n '44,51p' config/flags.yaml
  grep -n "class RetentionPolicy\|def compress_dir\|def rotate_by_ttl" src/zephyr/infrastructure/system_telemetry/archive/cold_stub.py
  grep -rn "rotate_by_ttl" src/zephyr --include=*.py
  ls data/telemetry/
  ```

---

### A2 field_dictionary 登记缓办 —— 判定：**仍开（缓办前提已被推翻）** —— 等级 B

- Owner 原述：理由＝"工厂图 15 节点的入库位全部待定，没有实体可登；等第一个数据工件建起来再连同字段登记；TDM 先例＝节点字段不进这张表"。
- 子代理实测：
  - 辖区定义未变：`docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml:21-27`（"仅管数据层字段语义"，裁定8）；条目 262，与 `docs/registry_of_registries.yaml:670-676` 的 `entry_count: 262` 一致。
  - **TDM 先例成立**。
  - **触发条件已到**：`config/strategy_production_map.yaml` 现 16 节点，"待定"仅剩 3 处（L341/L365/L388），13 处已实化，含实体表：FAC-E2→`c1_backtest.hypothesis_precheck`（L233）、FAC-E4→`c1_backtest.strategy_screen`（L284）；建表件 `scripts/ch/apply_hypothesis_precheck_ddl.py:35-37`、`apply_financial_derived_ddl.py`、`apply_consensus_daily_ddl.py`。
  - 这些表的列在字典中**全部不存在**：探针 `candidate_id`/`verdict`/`eps_consensus`/`n_reports`/`net_profit_ttm` 等 11 列。字典最后一次内容变更 `00f525d348`（2026-09-13，纯新增 4 条盘中宽度字段），schema 语义层仍停 `2026-08-15`。
  - 缓办留痕唯一记录：`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-factory-gate-review.md:101`（三条理由）+ 同文件 `:159` §6-4"登记待 Owner 追认/下会话处置"；议题 `#ARCH-FACTORY-MAP-GATE-001`（`architecture_issue_registry.yaml:21403-21410`）status=decided、fix_phase="已落地"，adjudication 仅一句"field_dictionary 登记缓办留痕"。
- 缺口：补登记 + Owner 追认双双无记录；议题已标 decided ⇒ 盘上再无机读位记着"其实还欠着"。
- 复现命令：
  ```bash
  grep -c "^- field_id:" docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml
  grep -n "待定" config/strategy_production_map.yaml
  grep -n "candidate_id\|eps_consensus\|n_reports" docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml
  git log -1 --format='%h %ad' --date=short -- docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml
  ```

---

### A3 产业链老数据全量重验 —— 判定：**仍开（约 1/7 完成）** —— 等级 B（分母口径见 §5 第 2 条）

- Owner 原述方案：机器三重检查（①股票代码有效性 ②供货方向说反 ③两独立来源互证），**全量**跑完出报告，可疑单独清。起因＝"券商作者被当成产业链公司"误挂。
- 子代理实测（报告=`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-supply483-verification-report.md`，commit `9a896219a7`/`8770bf8485`）：
  - 已跑面＝`ig_company_edge source='483_top5_customer'` 共 51,345 行中的**双边行 7,337 条**做了全量三检。结果：代码/在市 **0 错**、自环 0、金融机构混入 0、跨源方向印证 **695 对一致 / 17 对相反**、28 对双向＝合法互供保留；17 对仲裁后 **改 3 条错向**（`edge_ids [7671,10423,10639]`，批次件 `.runtime/industry_graph/night_audit/batches/supply483_dirfix_p5.json`，reason_doc 与报告 §2 一致），错率 3/7337=0.04%。
  - **未跑面**：B 组 **44,008 行（对手方仅有名称）未进三检**；同批只做了名称回填（558 名 → 1,248 行升级为双边，7,337→8,585，审计件 `.runtime/audit/name_backfill_actions.json`），**回填升级行无复跑三检记录** ⇒ 约 **42,760 行未验**。
  - 报告 §4 点名的"名单源（match_list）反向行 5 对留待名单源验证批"——该批在批次目录与 git log 中**均无记录**。
  - **三重建验无常设脚本入库**：`scripts/industry_graph/graph_quality_check.py` 的常检项只覆盖自环/双向/UNLISTED/死映射（L195 S15 / L199 S16 / L214 S18 / L309 S11），"金融机构混入"与"跨源方向印证"两项**无对应检查项**，报告 §4 只留一次性 SQL。
  - 结案状态：2026-09-15 自动结案核验已把本报告判为**未结案**。
- 复现命令：
  ```bash
  sed -n '30,90p' docs/_working/archive/2026-09/c_class_scattered/2026-09-14-supply483-verification-report.md
  grep -n "S15\|S16\|S18\|S11" scripts/industry_graph/graph_quality_check.py
  ls .runtime/industry_graph/night_audit/batches/ | grep -i match
  ```

---

### A4 详情页支撑（上游供应商/下游客户） —— 判定：**终局（带两条小尾巴）** —— 等级 B

- 后端通道：`src/zephyr/frontend/dashboard/api_server.py:4009-4110`（端点 docstring 明确 suppliers/customers 方向语义），commit `eb9f3915eb`；另有 `:3793-3802`。
- 前端接线：`src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-company-card.js:248-249`；验收断言 `docs/03_modules/_domain_frontend/acceptance/ACC-F-CHAINMAP-COMPANY-CARD.yaml:16`（revision 3）。
- 数据底座"5 万多条"＝与 A3 的 51,345 行同源，口径一致。
- 尾巴①：接口规格只写在已归档工作文档（`2026-09-14-supply483-verification-report.md` §4/§6，ttl=task_bound），**无永久契约件**；实际路径 `/api/chainmap-company?symbol=` 与规格建议的 `/api/company/{symbol}/supply_chain` 不一致。
- 尾巴②：该端点**未按已验证的 source/valid_to 过滤**，会混采未验源（与 A3 的 42,760 行未验直接相关）。

---

### A5 消费端两选一 —— 判定：**一支终局（裁定封矿）、一支未开工** —— 等级 B

- (a) 台风→BDI 因子卡：**不升级为因子卡，就地封矿**。`docs/_working/archive/2026-09/c_class_scattered/2026-09-14-typhoon-bdi-factor-mining-plan.md:117-134`（P0 全样本 217 场事件研究判定；不注册 IC 网关、不挂 TDM、策略库不登记），commit `487432f583`/`c1a962e976`。`factor_registry.yaml` 全文无 typhoon/bdi 条目。旁支落了两个 regime 信号（定位=风险日历非收益因子）：`src/zephyr/alt_data/alt_regime_signals.py:35`（F7 台风日历 + F4 BDI 动量），commit `10561f9d12`。
- (b) 政府采购网爬虫试点第 3 批：**完全没做**。全仓搜「政府采购 / ccgp」在 `src/`、`scripts/`、`data/`、`config/`、`tests/` **零命中**，仅存在于计划文档文字（`2026-09-12-alt-data-construction-plan.md:111`、`...batch1-construction-report.md:71`）；`src/zephyr/alt_data/web_scraper_engine.py` 无采购/招标 target；`data_asset_registry.yaml` 无条目；无相关 commit。⚠ git log 里的"批3"是**深圳开放数据批3**，与爬虫试点同名不同事——复审别混淆。

---

### A6 dead/ 剩余 953 条门禁拦截死信 —— 判定：**终局** —— 等级 A（本会话亲自数）

```
.runtime/commit_queue/dead_archive_20260830     61
.runtime/commit_queue/dead_archive_20260914_closeout  25   ← 恰等于"授权的 25 条 clean 死信"
.runtime/commit_queue/dead_archive_20260919_x1       912
.runtime/commit_queue/dead_archive_20260919_x1b       48   ← 912+48 = 960 ≈ 所称"剩余 953"
.runtime/commit_queue/dead_purged_20260920           113
.runtime/commit_queue/dead/  (活区)                   69
```
- "已按授权边界处理完毕"与盘上一致：25 条已归档，其余越权未修。
- 活区 69 条是 **09-19 归档之后新累积**（qid 日期 09-13~09-20），dead_reason 抽样分布（等级 B）：DIRECTORY-CONTRACT 22 / FOLDER-CAPACITY-HARD-LIMIT 11 / TTL-METADATA 7 / R5-DIGIT-SUFFIX 5 / 其余零散（CREATE-GUARD、PROTECTED-PATHS、LOCK_TIMEOUT）。**属常态运转，非本条欠账。**

---

### A7 全图对齐 16 个硬报错（8 FQ/GR + 8 EXP） —— 判定：**数字终局（16→0），但清零方式待复审裁定** —— 等级 A/B 混

- 基线实证（等级 B，子代理用 `git show b1c59c9cda^` 版 factor_registry 复算）：**恰好 16 条**＝FQ-001~006 + GR-001/002（8 条，财报消费端线）+ EXP-001~006 的 8 条悬空引用（EXP-001/004 各 2 条，st-expectation 线）。
- 现状：两库 275 条 inputs 引用 → 硬报错 **0**（只读复现判据在 `src/zephyr/gov_enforcement/registry_alignment.py:335-382`，判据＝inputs ⊆ field_name）。
- 落地提交：`b1c59c9cda`（09-14，本线 8 条清零）＋ `1d23039e90`（09-15，st-expectation，提交语："吸收在途 inputs 归一批（inputs=[] 全库惯例）"）。
- **本会话亲验的关键事实（等级 A）**：`grep -c "inputs: \[\]" factor_registry.yaml` = **171 条**，分布从 L295 起、每 74 行一条规律排列。⇒ `inputs: []` 是**全库既有惯例**，不是这 14 条独有。
- ⚠ 本会话上一轮口头报告里说过"清零方式＝把 inputs 清空来糊弄门禁"——**这个指控强度可能过头**（见 §5 第 1 条，列为复审必判点）。诚实表述应为：*报错确实清零了，但"因子→数据字段"的可追溯引用从未建立（14 个涉事条目现为 `[]`），而 `[]` 本身是 171 条共有的既有写法*。正修先例：`alignment_checklist.md:204` changelog⑦（FCT-SENT-028 走"补字典 3 字段"）。
- **未实测面**：align_all 其余八节的硬报错数（跑生成器会写文件，本次禁做）。

---

### A8 bdpan tick 8 天缺口手工挂载 —— 判定：**仍开（7 天全部 0 行），且症结不是"没下载"** —— 等级 A（本会话逐字读日志 + 数盘）

`.runtime/tmp/tilib-probe/gap7_fill.log` 全文实证：
```
[2026-09-17 00:20:59~00:25:36] 7 个 zip 全部下载成功（0703/0706/0707/0708/0709/0805/0806，各 74.0~80.4MB）
  落盘路径异常：E:\数据下载\tick 8 天缺口\2026-07\20260703.zip\20260703.zip（zip 套在同名目录里）
[00:25:38] 导入 2026-07 → zip 目录=...\2026-07  可导入日=[]  缺包日=['20260703,...,20260709']  rc=3
[00:25:40] 导入 2026-08 → 可导入日=[]  缺包日=['20260805','20260806']  rc=3
[00:25:43] CH 验证：07-03=0行 07-06=0 07-07=0 07-08=0 07-09=0 08-05=1行 08-06=0
[00:27:20] 路径整理完成：修复 7 个嵌套 zip
[00:27:23] 再次导入 → 仍然 可导入日=[]  rc=3
[00:27:28] CH 验证：六天仍 0 行，08-05 仍 1 行
```
- **实物至今仍在盘未消化**（本会话 `ls -R` 亲验）：`/e/数据下载/tick 8 天缺口/2026-07/` 下有 `20260703.zip 20260706.zip 20260707.zip 20260708.zip 20260709.zip`，`2026-08/` 下有 `20260805.zip 20260806.zip`（另含 20260701/20260702 解开的 csv 目录）。
- 09-17 之后**无任何再尝试痕迹**（`git log --since=2026-09-16` 无 tick 回补落地提交）。
- 登记表未更新：`src/zephyr/data/config/known_data_gaps.yaml:376-413` 仍 `status: "accepted"`、`last_updated: 2026-09-10`。看门狗 `scripts/data/bdpan_tick_watch.py` 任务在册但 `.runtime\bdpan_tick\` 空、无日志。
- **定性冲突（复审要判谁对）**：`docs/_working/kimi_audit/adjudications/p7c_efgh_family_rulings.md:41`（F-05 裁定"无 2026-08 文件夹、源 7/3 停更、6 日缺口 accepted"）**与上面的下载日志实证相反**——日志显示 2026-08 包确实下载成功。
- 最新令：09-20 裁定 **`#380⑩`** 撤销"永久缺口"原判、列甲线最高优先（本会话亲验该裁定在册：`grep -c "ruling_id: '裁定#380'"`=1）。
- 结论口径：**这是下载器落盘布局与导入器路径口径不匹配，重复下载无用。**

---

### A9 每交易日通达信+大QMT 保持盘中开着 —— 判定：**叙述过期（本周实际未满足，有实证）** —— 等级 A

`.runtime/logs/paper_session.log` 全文仅 4 行（本会话直读）：
```
2026-09-17 09:25:03 SKIP: XtMiniQmt (57 1 C1=Owner ) -- , 09:25
2026-09-18 09:25:05 SKIP: XtMiniQmt (57 1 C1=Owner ) -- , 09:25
2026-09-19 09:25:03 SKIP: (is_trading_day=False)
2026-09-20 12:17:12 SKIP: (is_trading_day=False)
```
⇒ 09-17、09-18 两个交易日因 **XtMiniQmt 未运行**被跳过；PaperSession **首跑从未发生**。

---

### A10 系统侧自动运行四站 —— 判定：**部分成立（两站未按那晚计划跑，常态化已成立但换了档）** —— 等级 A/B

| 计划 | 实测 | 等级 |
|---|---|---|
| 09-17 15:35 全量挖矿 | **没跑**。最后一次点火 `09-16 15:35:04`（本会话 `grep -a "fired at" .runtime/logs/factory_lane_c.log`）。任务现 Disabled 之说引自 `p7a_ac_family_rulings.md:210`（B） | A |
| 09-17 17:30 双窗批考 | **没跑**。最后一次 `c4_exam.log:896 = 2026-09-16 17:32:22`（B）；但 09-19 14:00 真跑过（本会话 grep 亲见 `==== C4 exam fired at 2026-09-19 14:00:00 ====`） | A/B |
| 09-18 09:25 PaperSession 首跑 | **从未成功**（见 A9，四行全 SKIP，等级 A） | A |
| 周六（09-19）起例跑常态化 | **成立**：09-19 FactoryLaneC 10:00（尾行 exit code 0，本会话亲见 fired 记录）、C4Exam 14:00、F06Grid 23:00；采集侧 `.runtime/tmp/scheduler.heartbeat`＝`2026-09-20T21:36:18+08:00`；`.runtime/fetch_perf/fetch_perf_20260919.jsonl`/`20260920.jsonl` 3250/2066 条 | A(挖矿/批考) B(其余) |
- 附带·09-17 停采警报：**半闭环**（等级 B）。已补：`kline_daily` 09-16/17（裁定 **`#330`**，commit `1798637596`，09-18 03:31）；tick 09-15/16 回补 19,565,360 / 19,951,867 行（`.runtime/tmp/tilib-probe/tick_backfill_0915.log`、`tick_backfill.log` 09-16 20:15:43）。仍缺：**tick 09-17 双通道 0 行**（`docs/_working/dataqa_audit/cross_findings.md:45`、`p3_db_repair_master_plan_v1_0.md` 病-9）。
- 归档提醒（等级 B）：09-17 还挂过 ETF 60min 四段结构缺口 ~9 万 bar、`tick_depth_5` 08-18~09-10 约 19 日回补窗"每晚一天少一天"、`kline_etf_15min.trade_time` 时区劈叉 14752/15405 行——这三条在 Owner 本轮输入里**没提**，但属同一战役面。

---

### A11 ALGO_FLOW 战役 —— 判定：**机械面终局；两个数已变味** —— 等级 A/B

- **成立部分**（B）：3,231 件源码挂 `# [ALGO_FLOW] external:` 单行路标 + `docs/03_modules/_domain_*/algo_flow/**` 3,232 镜像；落地 commit `481aaed065`、`7c25e8fe`。搬运器带"逐字节一致否则自动回滚"。
- **变味①（等级 A，本会话亲数）**：Owner 原文说"代码里一个内联说明都不剩"，记忆里的"残余 69 件作者欠账"现在**实测 79 个文件仍有内联多行块**（净增 10）。本会话计数方法：`grep -rl "\[ALGO_FLOW\]" src/zephyr --include=*.py`＝**3,311** 个文件，其中只含 `external:` 路标的排除后剩 **79**。样例：`pf_alloc/allocation_config.py:31`、`factor/analysis/factor_lifecycle_runner.py:29`（子代理给）。
  ⚠ 这 79 件属**作者语义欠账**（47 五段式散文缺 `- id:` / 17 零边图缺边 / 5 块不可解析，按 09-17 台账口径），补边补节点＝臆造语义，**工具不得代做**。所以"没清零"不等于"可以工具清零"。
- **变味②（等级 B）**：两份真源报告**已不在 Owner 记的 live 路径**——`docs/_working/reports/p21_algo_flow_link_findings.md` 现 MISSING，实际被 09-20 的 C 类归档批挪到 `docs/_working/archive/2026-09/reports/`；欠账台账 `algo_flow_author_debt.md` 同处，且内容仍是 09-17 生成的 **69**（未随 79 重扫）。
- **复审可打的口径问题**：79 是否真为"内联多行块"，取决于 grep 判据（我方判据＝文件内 `[ALGO_FLOW]` 出现行中无任何一行含 `external:`）。若某文件既有路标又有内联块，我方算法会**漏计**（即 79 是下界）。

---

### A12 daban 打板链 —— 判定：**终局（两处排班/面板尾巴）** —— 等级 B

- 四引擎位置：`signal_ashare/screening/short_term_stock_selector.py`、`limit_up/youzi_relay_emotion_engine.py:203`、`limit_up/quant_short_term_strength_engine.py:217`、`strategy_signal/dual_engine_fusion_decision_engine.py:189`；组装点 `pf_core/strategies/daban_sleeve_strategy.py:404-407`。
- **真读接线证据（非注释声明）**：`daban_sleeve_strategy.py:266-330`（DatabaseService reader + SQL 带 `trade_date<as_of` + 代码级双保险）、`ex_core/daban_load_producer.py:126-171`（真读 board_event/circ_mv/breadth/kline_index）、路由 `internal_compute_provider.py:115-117,760-822`。
- 幽灵行：守卫已实现 `akshare_provider.py:4442-4455` + `internal_compute_provider.py:737`；存量清理＝裁定 **`#289`**（`ruling_registry.yaml:3235`）+ `docs/_working/archive/2026-09/reports/limit_up_down_weekend_ghost_cleanup.md`。
- 涨停价查表：`daban_board_event_deriver.py:549-553` 三级链，88,445 样本 100% 验证。
- "936 行 / 4 只×15% / 涨停 30 只"逐条实证：裁定 **`#277`**（`ruling_registry.yaml:2681-2728`）；复真批＝裁定 **`#302`**（`:3680`）。
- 尾巴①：`daban_board_event_derive` 排的是**周末档不是日档**，且 09-16/17 未跑（`docs/_working/archive/2026-09/residual_construction/e4_cohort_reconciliation.md:67`）。尾巴②：composer 面板路仍 `ROUTE_NO_DAILY_SOURCE`。排班位置：`tasks.yaml:1634,1642,3387`。

---

### A13 "车道群质量"评估段 —— 判定：**评价非任务，可删** —— 等级 B

- 段内点到的"28 份蓝图模板漂移"现归蓝图门/ALGO_FLOW 面，不属 Owner 备忘录待办；"出仓器两代映射 bug / 控制字符写坏注册表 / probe 提交 message 不规范"均已在案（控制字符写坏注册表一事另见项目记忆 [[hot-file-wipe-forensics-20260918]] + #ARCH-337）。
- 唯一提示：Owner 原文说"每一处都被当场抓住、当场修"——本会话未逐处复核该全称命题（**等级 C**，属评价性陈述，不可机械证伪）。

---

### A14 Kimi 深度裁定班（含 #304-#326 / 93 份蓝图 / staged 告警） —— 判定：**裁定与回写终局；"93 份"数字待复算** —— 等级 A（在册计数）/B（其余）

- **本会话亲验（等级 A）**：`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 中 `ruling_id: '裁定#304'`、`#305`、`#320`、`#326`、`#331`、`#332`、`#377`、`#380` **各恰 1 条**；`#304` 标题实测＝"Regime r4/r10 方向失真重校准——HMM 组件锚定落地+态层方向语义退役（预注册协议判据，Owner 开工令'继续开工'）"，date 2026-09-17，status active。
  ⚠ 注意：Owner 原文第 3 条说"#304 已砍做T v2 战役现形态、#305 切换判据定稿、#306 尺子 v2 提案"，但盘上 `#304` 标题是 **Regime 方向失真重校准**，不是"砍做T v2"。子代理给的解释＝"原 #304/#305 因撞号改成 #331/#332，战役新号另立"（等级 B，**这是全案卷最需要复审的一条编号链**）。
- 裁定回写批**已落地**、非滞留 staged：`01fbfad157`（含 V-03~V-07 回写四文档 + registry +281 行）。当前仅自动生成的 `kimi_audit/*/index.md` 处于 staged（等级 B）。
- `owner_fast_sign_20260917.md` 存在，30 行总表，表头自述"全部自动裁定+登记，无需签字"，逐行带 #304-326 登记号；余留为条件性复议触发（L29 时区→移交数据线工单）。
- **"93 份蓝图"（等级 A 部分复算）**：本会话 `ls docs/_working/kimi_audit/ | wc -l` = **29 个顶层条目**。子代理称另有 `lane_reports`(21)、`adjudications`(20) 等子目录，并推断"93"来自"成交率 93.3%"的巧合、实际待裁清单是 `s3_pending_rulings_inventory.md` 的 96 条、后由裁定#377 三判定册处置（`9f9441f975`/`c5154321bd`/`cf41e79488`）。
  ⚠ **本会话未递归统计**：29（顶层）＋ 21 ＋ 20 ＋ 其他子目录，加起来**有可能接近 93**。所以"93 不实"这个说法我方**证据不足**，只能确定"顶层不是 93"。见 §5 第 5 条。

---

### A15 提交链提速 F1-F4 —— 判定：**部分完成（F2 主体卡 Owner 门位）** —— 等级 B

- 真源：`docs/_working/flash_speedup/00_master_ledger.md` §46-56。
- F1 ✅ `fe47296db5`（衍生并入）；F4 ✅ `025df45e0`（15 个生成器分 3 波并发，57.4s→28s，byte-identical）；加餐 F5/F6/F9 ✅。
- F3 🔶：无独立代码提交，靠推广 `604f414846` 的 diff 口径使门禁链 P50 41.6s→29.0s；"挖矿封矿"与 parse-cache 残余未做。
- F2 🔶：前置件 `727ad32a54`（热通道闸+双通道压测）已落；**主体 k=4 通道卡在等 Owner 签 S18-R3（裁定#320）+ "7 天>40 车道"观察窗**，未施工。

---

### A16 六个设想条目（2026-09-17 05:48~06:27 手输） —— 判定：**落地度极不齐，不可整段当完成删** —— 等级 B

| # | 条目 | 判定 | 证据 |
|---|---|---|---|
| 1 | 资本链+自然人全网信息面 | 设计+DDL+**首跑已灌**，但只到十大股东层 | 设计 `docs/_working/altdata_line/02_entity_graph_equity_person.md`；DDL `scripts/entity_graph/apply_entity_graph_ddl.py:57-160`（六表+穿透函数）；灌入 `entity_graph_ingest.py:19`（09-19：1,500,427 源行→1,500,341 边 / 140,725 节点），commit `c007caac86`。缺口＝`node_person`/`edge_role`/`edge_link` **有表无写入方**，"全网信息面"零实现 |
| 2 | 各路资金模拟 | **有实现代码** | `signal_ashare/crowd_game_simulator.py`（MOD-SIG-114 production，北向/公募/游资/散户）、`capital_behavior_orchestrator.py`（MOD-SIG-088 **testing**，七类画像+六阶段推演）、`institutional_behavior_analyzer.py`(021 production)、`capital_flow_pattern_analyzer.py`(022 production)、`data/implementations/northbound_hold_fetcher.py`；在库在跑见 `altdata_line/01_data_type_skeleton.md:34`，commit `d6353cf1bf`。缺口＝088 **无运行时消费者**（CONSUMERS 仅列"候选"） |
| 3 | 个股庄股行为模拟 | **两块未合流** | 识别在跑：`signal_ashare/screening/short_term_stock_selector.py:315-335`；专用检测器：`risk/manipulation_avoidance_detector.py`（MOD-RK-39，MATURITY=**design**），立项见 `candidate_module_registry.yaml:18272-18283`。缺口＝检测器 `wiring_status: exempt`（`wiring_registry.yaml:1722`），**无禁开仓/降权消费者** |
| 4 | 人性推导链条 | **完全无痕迹，从未立案** | 全库搜 人性/行为逻辑/推导链/偏好推导 → 零业务命中；无注册表条目、无裁定。最接近的只有注释级理论依据与 `altdata_line/04_metaphysics_data_factors.md:11` 的"行为代理变量"提法 |
| 5 | 生日/八字/星座→性格→行为 | **仅设计文档，代码零命中** | `altdata_line/04_metaphysics_data_factors.md`（六假设+预注册+E4/DSR 裁决）、`01_data_type_skeleton.md:128` G6=🔨、`90_convergence_todo.md:27`。src/schemas 无 生肖/bazi/lunar/birth_year 命中。**未被任何裁定砍掉**，是自设"预注册后由考尺裁决"的前置 |
| 6 | 全网新闻 | 四具名源在排班，"全网"名不副实 | `data/implementations/eastmoney_news_provider.py`/`rss_provider.py`/`tushare_news_connector.py`；任务 `data/config/tasks.yaml:529,1237,1253,1269`；排班 `schedule.yaml:64` news_slow、`:169` nightly_sentiment（DS-107 情绪窗）；消费 `limit_up/limit_up_reason_attribution.py`。缺口＝泛爬虫 `alt_data/web_scraper_engine.py` 仍 design |

---

### A17 交易成本模型 + 防前视硬断言 —— 判定：**终局（数字我方亲验）** —— 等级 A

- 本会话直读 `src/zephyr/backtest/core/cost_model_calibration.py`：
  - L30 文档串："窗口 2026-07-24~2026-09-16，5,519 只标的"；L115-118 `window_start="2026-07-24"`, `n_symbols=5519`, `n_tick_snapshots=13119233`；
  - L227-233 `Q1=7.24 / Q2=5.69 / Q3=4.67 / Q4=4.00 / Q5=2.34`；L147 明文对比旧 1bp 假设。
  - ⇒ Owner 原文"5,519 标的 / 1,312 万条五档快照 / 2.34~7.24bp / 旧假设 1bp 的 2.3~7 倍"**逐字对得上**（13,119,233 ≈ 1,312 万）。
- 消费方：`matching_logic.py:97,520`、`matching_engine.py:377`、`vectorized_engine.py:116`；标定提交 `35cf0eb36a`（B）。
- 防前视：`LookaheadExecutionError` 定义 `src/zephyr/backtest/core/engine_base.py:165`，**唯一抛出处** `implementations/vectorized_engine.py:247`（B）。测试 `tests/backtest/test_cost_model_calibration.py`、`tests/backtest/test_bt_financial_correctness_p0.py:90`。
- 缺口：标定产物是**代码内常量**（非可重算入库的 artifact），复算脚本未入库；硬断言目前只覆盖日频向量化引擎。

---

## 4. 需 Owner 拍板的四件（含"不点会怎样"）

| 件 | 这是什么 | 为何要你点头 | 不点的后果 |
|---|---|---|---|
| **P1 tick 7 日缺口** | 包已在 E 盘，导入器扫不到包（路径/命名口径不匹配）。要么改导入器认包逻辑，要么换入口手工喂 | 改动会碰到生产数据写入路径（RULE-DATA-OPS 破坏性面），且需一次真实回灌 | CH 里 7 个交易日继续 0 行；而你 09-20 自己刚下裁定 #380⑩ 把它列甲线最高优先——挂着 = 违自己的令 |
| **P2 老数据剩余 ~42,760 行** | 三重建验只做了"双边都有股票代码"那 7,337 行；对手方只有名字的 4.4 万行没验，且三检脚本没入库成常设项 | 要不要排一批工 + 要不要把三检写成常设门禁（后者=新增 gate，触全资产净零条款，须声明替代关系） | 已验区 0.04% 错率**不能外推**到未验区——未验的恰是最容易挂反方向的"只有名字"那批；详情页会把这些边直接显示出去（A4 尾巴②） |
| **P3 F2 k=4 并发通道签字** | 提交链提速的主体，前置件已好 | 明写等你签 S18-R3（裁定#320）+ 7 天>40 车道观察窗——Owner 门位，代理不可代签 | 提交链停在 29s P50，F2/F3 残余不动；你曾定性"提交链速度=全项目开发速度" |
| **P4 field_dictionary 补登** | 当初"没有实体所以不登"的理由已失效：13/16 节点实化、4 张实体表建成、11 列字典里不存在 | 缓办留痕写的就是"等第一个数据工件建起来再连字段登记"——条件已触发；但议题在盘上已标 decided，**再开一批需要追认** | 这条欠账在机器可读层面已经"消失"（议题=decided），未来任何扫描都查不出来，只能靠人记得 |

---

## 5. 本会话自我供状：可能翻车、复审请优先打这六点

> 按项目纪律 [[feedback-executor-cannot-sign-own-work]]：**执行方不能自证交付**。上一轮我给 Owner 的口头结论里，以下几条强度可能超出证据。

1. **"inputs 清空来糊门禁"这个说法可能过头**（我方最需要撤回风险的指控）。本会话亲测 `factor_registry.yaml` 里 `inputs: []` 有 **171 条**、等距排列 ⇒ 空数组是全库既有惯例，而那 2 笔修复提交的信息本身也写着"inputs=[] 全库惯例"。**站得住的弱表述**：报错清零方式合法且符合既有惯例，但"因子→字段"的可追溯引用从未建立。**请复审裁定这该算"欠账"还是"惯例一致的非问题"。**
2. **A3 的 42,760 / 44,008 / 51,345 全部分母引自报告散文**，本会话未连库复算。若报告本身口径有偏（例如 7,337 与 8,585 两个数并存），"约 1/7 完成"这个比例可能不准。**等级 B。**
3. **A1 的"零读者"用的是窄 grep**（`flags.*archive` / `archive.*enabled`）。若读取方是通过 dict 动态取键（例如 `flags["archive"]["enabled"]` 或配置对象属性遍历），我方会漏。请复审换判据反证：全仓搜 `"archive"` 字符串在 telemetry 相关模块的出现，并检查是否有 config 模型层自动映射。
4. **A11 的 79 是下界**：判据是"文件内 `[ALGO_FLOW]` 行无一行含 `external:`"。既有路标又有内联块的文件会被漏计，故真实数 ≥79。
5. **A14 的"93 份蓝图不实"我方证据不足**：只数了顶层 29 件，**没递归数**。子目录里 lane_reports(21)+adjudications(20)+其他，加上顶层，完全可能凑到 93 上下。请复审用 `find docs/_working/kimi_audit -name '*.md' | wc -l` 一锤定音；在此之前，"93 不实"只能记为**未决**。
6. **A14 的裁定编号链存疑**：Owner 原文说"#304 砍做T v2 / #305 切换判据 / #306 尺子 v2"，盘上 `#304` 实测标题＝"Regime r4/r10 方向失真重校准"。"撞号改 #331/#332"这个解释是子代理给的（B 级），**本会话未复核 #331/#332 的实际内容是否就是"砍做T v2/切换判据"**。若这条链错，则 A14 整条"终局"判定要重判。**这是全案卷最高价值的复审点。**

**另：本会话未做任何反向证伪测试**（即没验过"如果某条断言为假，我的命令会不会仍返回同样的输出"）。按 [[autoclaw-btfix-campaign]] 的"判通过的脚本须先证明能红"纪律，A 级判定的复现命令都应在复审中被反向喂一次。

---

## 6. 对账总表（17 条速查）

| 条 | 内容 | 判定 | 等级 |
|---|---|---|---|
| A1 | 遥测归档开关 | 叙述过期（灯在、没接开关） | A/B |
| A2 | field_dictionary 缓办 | **仍开**（前提已被推翻） | B |
| A3 | 老数据全量重验 | **仍开**（约 1/7） | B |
| A4 | 详情页上下游 | 终局（2 小尾巴） | B |
| A5 | 消费端两选一 | BDI=终局封矿；政府采购=**未开工** | B |
| A6 | dead/ 953 条 | 终局（活区 69 为新累积） | A |
| A7 | 16 硬报错 | 数字终局；清零定性**待裁** | A/B |
| A8 | tick 8 天缺口 | **仍开**（包在盘、导入器扫不到） | A |
| A9 | 交易日开终端 | 叙述过期（09-17/18 没开成） | A |
| A10 | 自动运行四站 | 部分（挖矿/批考未按那晚计划；常态化成立但换档） | A/B |
| A11 | ALGO_FLOW | 机械面终局；79 件内联 + 报告已挪路径 | A/B |
| A12 | daban 链 | 终局（周末档非日档、面板无路） | B |
| A13 | 车道群质量评价 | 非任务，可删 | B/C |
| A14 | Kimi 裁定+蓝图 | 裁定终局；"93"与编号链**未决** | A/B |
| A15 | 提交链 F1-F4 | 部分（F2 卡签字） | B |
| A16 | 六个设想 | 1 无痕迹、1 仅设计、4 有码但接线缺 | B |
| A17 | 成本模型+防前视 | 终局（数字亲验） | A |

**净口径**：可删 6 条（A4/A5(a)/A6/A12/A13/A17）＋ A10 常态化部分；仍开 6 条（A2/A3/A5(b)/A8/A15/A16 多数）；需改写 4 条（A1/A7/A9/A11）；未决待复审拍 2 条（A14 编号链与 93、A7 定性）。
