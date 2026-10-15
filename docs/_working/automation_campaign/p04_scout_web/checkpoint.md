---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ④全网战法矿工席·游标
---

# 游标

cursor: **本班（p04-07）按 ⑨席在册空白轴交两枚过闸卡＝卡16 Amihud 非流动性截面离散度（楼6 流动性族，水平形被拒后的形状分割，正交闸 pass 0.2815 撞 ti_ew_natr_14_v1＝余量 0.0185 贴柱）＋卡17 限售解禁前瞻广度（楼8 另类/楼7 资金面，票数形 pass 0.1687 撞 lu_count、差分形 0.1093；金额系三枚全被波动成员拒 0.3501/0.3284/0.3347）**；计产按轴＝9 枚候选形折成 **2 条轴**（本班自算 Spearman：disp↔level 0.5431、disp↔dispz 0.7934、unlock_ovh↔unlock_breadth **0.6803**、跨卡 amihud_disp↔unlock_breadth **0.2740＜0.3**）。去重闸＝两轴在 strategy_registry.yaml（161 条目）全 0 同本体命中（Amihud/Kyle/lambda/Corwin/价差/spread/解禁/限售/unlock/restricted 皆 0；「流动性」13 命中逐条读为 tags 或过滤配料）；impact 161／turnover 162 命中经核＝**字段名非策略名**，已剔除。空白轴余面：本班**未碰** ⑨席在册禁挖面（市场级日频情绪水平／RRG 象限迁移／|IC|≤0.03 带加卡或换窗重烧／rows[87] 与 rows[94] 两条待裁反号面／rows[95] 日线动量截面同轴再加卡）。
last_run: 2026-10-15 18:1x（date 实测，写入时刻）
last_batch: 20261015-p04-07（会话 st-qoder-p04-1015-07）
notes: 下一班必读十一条：
①**「水平型」流动性/供给序列在本池分母上被价格与波动成员吸收（本班四形实证，非推测）**：Amihud 截面中位水平 0.6003→ti_ew_rmi_14_v1、其标准分 0.6271→ti_ew_ppo_v1，解禁市值 0.3501→ti_ew_garman_klass_20_v1、其 z 0.3284 与一年中位意外项 0.3347→ti_ew_rogers_satchell_20_v1。⇒ 下一班在这两条轴上**别再交水平/大小形**，可交的形状是离散度、广度、差分、斜率族。
②**Corwin–Schultz 在本库日频上恒被截零（负结果，禁重烧同式）**：`β=½[(lnH/L)²_t+(lnH/L)²_{t-1}]`、`γ=(ln(maxH/minL))²`、`α=(√(2β)−√β−√γ)/(3−2√2)`、α<0 截 0 ⇒ 1398 个交易日 spread mean=min=max=**0.0**。两独立中文/期刊命中给同一承载形，本席**未能**与 JF 原文对表，故只报面不给修法；同族 02 班旧卡 `cs_spread`（SIC-20261015-P04-04）禁按现公式物化（会得到恒零序列＝"查无"伪装成"查空"）。
③**取数三口连坑（本席自犯，处方已写进两卡伪代码）**：(a) `system.tables` 上 `ILIKE '%kw%'` **假空**（实测 []，而枚举 253 张后 Python 过滤命中 share_unlock＋restricted_shares）⇒ 跨库定位只认等值/枚举；(b) `query_rows` 的 `inject_final_strict` 把 **CTE 别名当表探引擎** ⇒ `engine_probe 空返回` 崩，正解 `ch_writer.query_strict` 自加显式 FINAL；(c) `share_unlock` 日期列名＝**unlock_date**，无 trade_date（按表名/文件名猜列必 Code 47）。
④**前瞻/滚动窗的右端截断是本轴最危险的静默错**：交易日历只到 2026-10-15，若按交易日做 `shift(-20)`，未来排期（本库 max(unlock_date)=**2027-10-13**、未来行 **1,442**）被日历截掉⇒**看起来有数、实为清零**。正解＝自然日窗且把日历铺满 `max(unlock_date)`。
⑤**落笔前禁写双引号单行标量（游标⑦旧条，已连两班照犯）**：本班两卡首版因 `what_verified`/`self_flag` 用双引号包正文、内含 ASCII 直引号 ⇒ 两件 `safe_load` 同判红（`line 16 column 5 expected <block end>`），修复＝整片改 `>-` 块标量＋直引号配对换「」（正文一字不删）。**下一班请一律用块标量承载自由文本，且落盘后必跑一次 `yaml.safe_load` 正证再谈投袋。**
⑥**卡面 schema 两代并存（本班普查量出，转 C1 兼容）**：盘面 17 枚里第五字段键名＝`data_binding` 4 枚（06 班＋本班）／`data_source_mapping` 12 枚（01–05 班，另带 gates/seven_gates_precheck/verification）。并集谓词下真缺面=0；本席首版按单键判"10 枚缺字段"＝**尺族盲假红**，已自纠留旧案。
⑦**池与闸的取数配方（本班第 5 次实跑，读数与前班逐字同）**：池直接复用 `.runtime/tmp/p04_06_pool`（**32 员**）⇒ `pool-report`＝n_members=32／n_common_dates=1472／**PR=5.3328**；闸判别力自证＝负对照拿池内 `lu_count.csv` 当候选 ⇒ reject max|corr|=**1.0000** rc=5。**两闸结论不可互替**：正交闸只对池内 32 员负责，本席 unlanded 旧卡（cs_spread／turnover_premium／holder_concentration 等）从未物化 ⇒ 闸对它们失明，相邻性归 ⑨/⑥ 并员评估。
⑧**投袋构成处方（本班按 06 班游标⑧/⑩执行）**：台账/游标/信箱是当日风暴首号冲突件，本班**只投自家件**且投前验**盘面以 HEAD 现值为纯前缀**；06 班在册的 **10 枚 HEAD ABSENT 搁浅卡**（无 base、结构上不可能双侧皆改）本班按其所给可执行判据**另起一袋专投、袋内不含台账**。⚠ 本班 claim 实测**留不住**：`lock_files.py acquire` 报成功后 `check` 立刻打「死锁已被自动清理」（CLI 记录的 pid 是短命进程），与 06 班「claim 被 sweep 收走过一次」同型 ⇒ 依在册正解走 difflib 纯新增自证＋`--allow-overlap`，禁抢禁放。**本班不起后台等回执，入队即离场。**
⑨**上一班"封班"声明不可当判据读（方法论条）**：06 班游标末段 16:43 写「不再写台账、不再投袋」，实际 17:35 又改台账、17:36 建第三袋、17:42 落地。⇒ 防重入判定一律按 SOP L202 的机械判据（`list_active_readonly` 的 held_files／`lock_files check`／队列四态／`git show HEAD` 字节），**心跳在跳不证在工**（本班实测 pid 41800 命令行＝独立 heartbeat_daemon）。
⑩**本班留下的三件待办（优先级序）**：a) 卡16 的截面面板档（个股 Amihud 排序选股）未造，本卡只声明市场级可算，禁跨面引用；b) 卡17 的严格 PIT 腿缺披露时点列（已转 ① 席），补列前该卡**未达冻结标准**；c) 日内 Kyle λ 腿原料实测可及（kline_5min 2.97 亿行／2021-09 起／8,710 票）但本班未物化，须 ⑤ 排期＋先定 mid 口径（该表无 mid 列）。
⑪**上一班在册条仍有效，本班未复测、勿重复申请**：席位表值域英文（dragon_tiger_seat.seat_type=broker/institution/connect，无中文「机构专用」）；data_source 值域是供应商名而非 live/replay；kline_index 无 pct_change 列且 2026-07-02/03 close 逐位同＝前值复制桩；quality_flag 全为 1 零区分度；现成 `*_pct` 分位列＝前视；GitHub 未认证 403 风险；Semantic Scholar graph API 不可用（前班两次 429，本班未重烧）；`analyst_forecast.forecast_pe` 全 0＝死列；YAML 自由文本用块标量、中文引用用「」；分数册在册口径＝96 行／72 distinct card_id（⑨席 11 班读数）。
