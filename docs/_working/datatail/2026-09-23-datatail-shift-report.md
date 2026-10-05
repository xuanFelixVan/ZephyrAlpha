---
ttl: task_bound
---

# 数据尾巴班·总包回执（st-datatail-20260923，2026-09-23）

> 任务书=总包·数据尾巴班五件（轻活白天档）；落盘=本目录。逐件回执如下。
> 纪律执行：全程只读优先；破坏性操作零执行；capability 册热写走 claim+safe_write CAS+进程外复核。

---

## 任务1 ✅ 磁盘知识固化收尾 A（INFRA-STORE-003 关键词入册）

三件全落地：

| 件 | 落点 | 状态 |
|---|---|---|
| permanent 手册提炼 | `docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md`（新，permanent，MOD-INF-043 家族） | 已写入（scaffold 创建+正文提炼自 a3 定案：四盘分工/关键词速查/数据第一公理五铁律/遗留指针） |
| capability 册条目级增量 | `capability_canonical_file_registry.yaml` 新增 `four_drive_storage_map` 条目，aliases=冷库/冷储/备份/backup/四盘/storage/存储地图/INFRA-STORE-003，canonical_override=上述手册 | 已 CAS 写入+YAML 验证 |
| ROOR 挂接 | `registry_of_registries.yaml` REG-INFRA-001 描述行增挂：关键词→永久手册路径+capability 册同锚 | 已 CAS 写入+YAML 验证 |

**端到端复核（进程外）**：`CapabilityLookup.find()` 实测——冷库/冷储/备份/四盘/storage/INFRA-STORE-003 六词直中 `four_drive_storage_map`；`backup` 一词命中该条目列第 6/6（英文别名多条目竞争，仍可发现）。

**诚实声明（重要）**：
1. capability 册与 ROOR 两热文件**本次不随班提交**——暂存区有他会话（st-deepclean/st-regfix-lane0b/st-wm1 族）在航 token 件且含锚点插入损伤（重复 merge_evaluation 三连、04 条目错位双生，即 st-regfix 车道正在修的伤）。随班提交=连坐吸收+把损伤固化进 HEAD。两文件修改留工作树（claim 已持），由修复批统一带飞。
2. 过程事故如实记录：首次插入锚点 `creation_tokens:` 命中条目内 2 格缩进同名子键（认子串不认顶层键），条目误插 capabilities 列表中间致 YAML 破损；已外科还原（CAS+YAML 绿）后改用"最后一条 capability 条目块尾"锚点重插成功。教训=热册插入锚点必须锚"顶层键行号+缩进校验"，与 st-stress 修的锚点缺陷同族。

---

## 任务2 ✅ 财报线任务二/三覆盖验证（只读，验毕跳过）

**结论：两项均 PASS，无需回补，跳过。**

| 项 | 预期 | 实测 | 判定 |
|---|---|---|---|
| stock_indicator 估值覆盖 | 5,823 只 | 历史去重 **5,825 只**（1167 万行，2015-01-05~2026-09-22）；末日 pe/pb/total_mv/circ_mv 非空均 5,567 只（当日实际交易面） | ✅ ≥预期 |
| financial_indicator 中报覆盖（report_period=2026-06-30） | 5,528 只 | **5,528 只**，与预期精确相等；announce_date 最晚 2026-09-12（中报披露期已闭） | ✅ 精确吻合 |

旁注（不属本任务、留观不动作）：financial_indicator 各报告期存在 announce_date=1970-01-01 纪元残留哨兵行（quality_sentinel_tables.yaml 已在册该表 epoch 维度）。

---

## 任务3 ✅ 议息日历换源调研（B2 老账，只出选型卡不接入）

**现状实证**（2026-09-23 活体探针）：
- `c1_market.rate_decision_calendar`：3,086 行 / 11 央行 / data_source 全=akshare；**max(decision_date)=2025-10-30，停更 ~328 天**（金十退役≈2025-11-04，323 天口径吻合）。
- akshare 1.18.75 的 `macro_bank_*_interest_rate` ×11 接口**全数活着但上游冻结**（usa 接口实拉 294 行止于 2025-10-30）=死水管；tasks.yaml `rate_decision_calendar_refresh` 日更任务在跑但只空转。
- 附带实测 435 行 decision_date=1970-01-01 纪元残留（boe 全窗），quality_sentinel_tables.yaml 已在册。
- 侧翼 `calendar_event.fomc_meeting` 手工台账 43 行，覆盖 2021-09-22~2026-12-09（Fed 未来日程日期在）。
- G 盘 `db_dumps/20260921|20260922` 日备含本表全量=历史快照可用，非前瞻源。

**选型卡**：

| 候选 | 通道实证 | 覆盖面 | 结构化/前瞻 | 评价 |
|---|---|---|---|---|
| A. 东财央行利率 | akshare **无**现成接口（宏观模块全金十系，grep 实证零 eastmoney）；需自研 datacenter-web 直连（外部先例：data.eastmoney.com/cjsj "央行公布利率决议"报表系列，foreign_0_22=美联储上限，CSDN 有可跑爬虫） | 疑似多央行（cjsj foreign 系列），接入时逐页核验 | 结构化+含未来场次待验 | **推荐主通道**：与现任务表结构（decision_date/rate_value/rate_forecast/rate_previous）字段同构度最高，11 行中国行外可平替；代价=自研 provider+反爬稳定性观察 |
| B. Fed FOMC 官方 + G 盘快照 | federalreserve.gov 官方日历（页面稳定，2 年前瞻）；G 盘快照补历史 | 仅 Fed 单央行；他行需逐家官网（ECB/BOE/BOJ 各自接口，维护面 ×11） | 官方权威、日期前瞻可靠但**无预测值/前值结构** | **推荐侧翼/兜底**：Fed 单行先用（侧翼台账已在跑同形态）；全 11 行不经济 |

**落地建议（待裁，未实施）**：A 为主源重建 `rate_decision_calendar` 增量任务（新建东财 provider，复用现表字段），历史 2025-11 以后缺口由 A 全量补；Fed 未来日期先由侧翼台账顶住；金十口径 ×11 任务在 A 上线后退役（净零：1 进 1 出）。另 435 行 1970 残留随换源批一并清洗。

---

## 任务4 ✅ ETF60min 深史回补工单评估（dry-run+小样本试跑完成，全量排夜窗）

**缺口现状复测**（工单 09-17 数字六天后复测）：

| 窗口 | 60min 现状 | 1min 源 | 可回补 |
|---|---|---|---|
| 2026-07-01~07-07 | **全零（0 只）**——比工单口径更重（工单记 07 窗全程 31 只） | 1,575-1,582 只/日满覆盖 | ✅ 通道C |
| 2026-07-08~07-17 | 31 只/日（考试子集） | 1,588-1,601 只/日 | ✅ 通道C |
| 2026-07-28 | 545 只（半日断） | 1,607 只 | ✅ 通道C |
| 2023-06-05 | 全零（全历史唯一零行交易日） | 759 只（当时家族 758） | ✅ 通道C |
| 2021-02-08（159915 散格） | 零 | **1min 亦无** | ❌ 仅通道D（QMT 沙箱） |
| 09-16 半根/09-17 全停 | **已愈**（09-10~09-23 十日全满 1,656-1,673 只×4，采集链重启+补跑生效） | — | 无需动作 |

**量级**：可回补 ≈ **8.9 万 bar**（与工单 ~9.0 万吻合），1min 源扫描 ~500 万行，CH 写入 <100MB——全量回补为分钟级小活，非重载。

**小样本试跑（只读对拍，零写入）**：510300+159915 × 2026-09-22，从 etf_1min 合成 4 bar 与官方存量 60min 逐字段对拍——**调整两个坑后 volume/amount 8/8 bar 全部 0.00% 误差（逐 bar 精确相等）**：
1. **bar 时刻必须窗口尾标签**：官方约定 10:30/11:30/14:00/15:00（首 bar=09:30-10:30 记 10:30）；`ch_tick_kline.SQL_SYNTH_H` 的 `toStartOfInterval` 是 epoch 对齐头标签，**现函数不能直接参数化套用**。
2. **分钟级预去重必须做**：etf_1min 原始行存在未合并双写伪影（510300 该日 295 raw 行/241 分钟，09:30-10:30 窗双写），不去重日总量虚胖 40.8%。
3. 残余 DIFF 仅 OHLC 第 4 位小数（1min 源 3 位小数 vs 官方 4 位精度）+ 边界分钟归属（11:30/15:00 分钟须尾含进对应 bar）——对缺口日（零官方数据）完全可接受。

**代码件评估**（工单移交建议的通道C CLI，今日未建——属数据线代码权限）：仿 backfill_lof_minute_history.py 先例，要点=①ETF 表对参数化+会话感知窗口（尾含）②分钟级 argMax(ingest_ts) 预去重 ③零覆盖白名单过滤+ReplacingMergeTree 同键幂等 ④分片按（日×symbol 批）写 ⑤FINAL+argMin 在此 CH 版分析器下不兼容的实证教训带入。**资源判定：可行性高、体量小，建议排今晚夜窗一次性全量（避开 15:00-16:35 收盘结算窗天然满足）**；剩余 2021-02-08 走通道D 沙箱下载。

---

## 任务5 ✅ financial_indicator 双写哨兵 35,180 行清理（三步验证后判定：不删）

**三步验证结论：DELETE 不成立，验毕跳过。**

1. **必要性（实测推翻任务基数）**：35,180 = 战役时点 raw(421,511)−FINAL(386,331) 盈余。本日复测 raw=388,849（两次测量零漂移），**未合并盈余已自愈至 2,518 行**（ReplacingMergeTree 后台 merge 持续收敛；观测期 merge 活跃数字在漂）。
2. **真实性（重复性质查明）**：现存 2,518 个重复键**全部**单源、值逐字节相同、仅 ingest_ts 不同=纯重摄入伪影（跨源冲突 0、值发散 0）——FINAL 读面早已干净（386,331 全等），无任何业务可见脏数据。
3. **可逆性（不通过）**：对生产 c3_fundamental 表做 ALTER DELETE 不可逆且是错误工具（无法表达"同键留最新"）；RMT 重复的正规清理=`OPTIMIZE TABLE ... FINAL`（幂等、无损、无 distinct 数据移除）。

**建议（待裁，未执行）**：无需任何动作（后台 merge 自愈）；若求物理回收，夜窗一次 `OPTIMIZE TABLE c3_fundamental.financial_indicator FINAL` 即可，禁 DELETE 路线。

---

## 班终清单

| 交付物 | 落点 |
|---|---|
| 永久手册（新） | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md |
| capability 册条目 four_drive_storage_map + ROOR 挂接 | 两热文件工作树（见任务1 诚实声明，随修复批提交） |
| 本回执 | docs/_working/datatail/2026-09-23-datatail-shift-report.md |

**待 Owner/后续班留意**：①热册两文件未随班提交的原因与带飞建议 ②议息换源选型卡待批（主 A 侧 B）③ETF60min 全量回补建议排今晚夜窗（代码件需数据线车道先建）④任务5 建议 OPTIMIZE 路线、禁 DELETE。
