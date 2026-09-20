---
ttl: task_bound
session: st-data-fix-20260921
title: 数据正确性线分包1——估值双修（index_valuation_daily/daily_valuation）A1+A2 修复与红蓝极限对抗报告
---

# p1 估值双修报告（2026-09-20 深夜 · st-data-fix-20260921 · WO-1·P0）

裁定依据：#380 签字③（按推荐案直接修）+ #379①。CH 全程走 DatabaseService；
未用 OPTIMIZE/TRUNCATE/DROP；删除仅批文授权的 ALTER DELETE mutation（冷存先行）。

## 结论一句话

两病皆除：病-1 根因=ReplacingMergeTree **无 version 列**+双写者（后到 NULL 版本在合并
仲裁中无约束胜出），病-2 根因=百度估值能力**不产行情九列**（非 Nullable 列落 0）+writer
**无交易日 gate**。修后 FINAL cape 病理 NULL=0、重复组=0、daily_valuation close>0=99.91%、
非交易日行=0，哨兵两表腿实测绿，红蓝对抗三项全过且对抗产物净零。

## 修前/修后对照（同命令实测，[亲验]）

| # | 指标（命令口径） | 修前（22:00 复现） | 修后（23:55 实测） |
|---|---|---|---|
| 1 | index_valuation_daily cape_5y NULL | 8125/8125（100%） | 2346/8118（全部=rolling(1250,min750) 数学 warmup 区 2010~2014-11-06；**2015 后病理 NULL=0**） |
| 2 | 重复组 FINAL（GROUP BY symbol,trade_date HAVING>1） | 0（09-18 止血后被 merge 折叠，**但折叠保留的是无派生列版本**） | 0 |
| 3 | 重复组非 FINAL | 0 | 8092（compute 重写版本 merge 前共存，ReplacingMergeTree 正常语义，FINAL 视角 0） |
| 4 | 表引擎 | `ReplacingMergeTree`（无 version） | `ReplacingMergeTree(ingest_ts)`（system.tables engine_full 实读） |
| 5 | daily_valuation close>0（FINAL） | 0/271,266（0%） | 188,753/188,922（**99.91%**） |
| 6 | 周六行 | 8 个周六 43,510 行 | 0 |
| 7 | 非交易日行（trade_calendar is_open=1 判定） | **82,344 行**（周六 43,510+周日 38,834，15 个周末日；红证基线只报了周六——周日语义修正见"基线更正"） | 0 |
| 8 | data_source | 100% local_valuation | 100% local_valuation（不变，价格腿并入同行；ingest_ts=回填批次可追溯） |
| 9 | index 派生列 pe_pct NULL / erp NULL | 8125 / 8125 | **0** / 848（10Y 国债源端 2010~2012-09 稀疏，2012-09-04 起 100%） |
| 10 | 哨兵腿 daily_valuation（fill_ratio+行数地板） | close/amount/turnover 非零率 0% 必红 | **绿**（breached=False，附加腿 2 项达标） |
| 11 | 哨兵腿 index_valuation_daily（近窗非空率） | 全表 NULL 必红 | **绿**（breached=False） |

**基线更正（比批文多发现的病面）**：①污染不止周六——周日亦有 38,834 行，删除谓词按
"trade_calendar 非交易日"执行（82,344 行全清），冷存凭据同批；②compute 管道内建缺陷：
`_compute_start_date` 对非增量任务返回**月初**，既有周末 compute 腿若跑会把 expanding
分位算在 ~2.5 周窗口上（rank 样本≪1250 窗）——本次一并治本（全史读算），否则修完
CAPE/分位仍是错数。

## 修复内容（A1+A2）

**A1 index_valuation_daily（单写者语义闭合）**
1. 表重建：`ReplacingMergeTree` → `ReplacingMergeTree(ingest_ts)`（ingest_ts=version 列，
   对齐 adj_factor 等表既有惯例）。原子 RENAME 换名；旧表整体冷备
   `c1_market.index_valuation_daily_quar_20260920`（8125 行，未 DROP，净删留 Owner 门位）；
   7 行非交易日行先冷存后剔除。DDL-as-Code 真源同步（schemas/.../market_index_valuation_daily.py
   ——白名单外必要连带，见"偏离"）。
2. compute 管道全史读算（index_valuation_compute.py）：CAPE(rolling)/expanding 分位是
   全史函数，改恒从表内 symbol 首日读起、全量幂等回写；CPI/10Y 国债读窗同步修正
   （reindex+ffill 只前向不回填，短窗读会让全史 ERP 全 NaN）。
3. tasks.yaml 增 `index_valuation_daily_compute_daily`（daily_kline，DAG 依赖
   index_valuation_daily_incremental）——工作日增量落库当日重算，消除"周末才重算"的
   NULL 空窗。CLI 实跑成功（8118 行秒级）。
4. 红蓝对抗 1 实证 version 仲裁语义（见下）。

**A2 daily_valuation（价格腿+交易日 gate+0 行告警+非交易日清创）**
1. writer 价格腿真源（akshare_provider）：`_load_kline_price_leg`/`_apply_kline_price_leg`
   ——行情九列自 kline_daily 读回（任务 DAG 前置 kline_daily_incremental，当日日 K 先落库）；
   preclose=close−change 精确推导（抽 000001 五日实测与 pct_change 逐日吻合）；仅覆盖
   值为 0 的槽位（self 值优先，与 09-18 carry-forward 同仲裁方向）。
2. 交易日 gate：`_load_trade_day_set`/`_apply_trade_day_gate`（trade_calendar is_open=1，
   **fail-closed**——日历不可用整批拦截+留痕，0 行告警腿独立鸣哨）；daily_valuation 与
   index_valuation_daily 双 writer 同批接线。
3. 存量清创：82,344 非交易日行冷存
   `F:/db_dumps/zephyr_quarantine/20260920_valuation_repair/daily_valuation_nontrade_rows.parquet`
   （82,344 行 × 18 列）→ ALTER DELETE（mutations_sync=1，残留 0）。
4. 价格腿回填：INSERT SELECT 裸 JOIN kline_daily，188,922 键全量重写。
5. 哨兵收口（data_supply_sentinel.yaml）：daily 表加 7 日行数地板 2000（0 行成功告警腿）；
   index 表 fill_ratio 窗口 0→30 日（全表口径把 warmup/源稀疏结构性缺席永久计入=永久红腿，
   必被后人拔线）；daily 腿 cols [close,amount,turnover]→[close,amount]（turnover 在
   **kline_daily 源头**近窗非零率 0.9%，回填如实拷贝源零，留存理由见 yaml 同批注释）。

## 红蓝极限对抗（Owner 点名三项，全过，EXIT=0）

对抗脚本 `.runtime/tmp/st-data-fix-20260921/red_blue_adversarial.py`（注入→红→撤样→绿）：

**对抗1 注入双写竞争**（RBTEST300 假符号×2026-09-18，显式 ingest_ts 分层）
- 注入：raw 版（派生 NULL，ts=-120s）+ compute 版（cape=31.05，ts=now）同键双写。
- 红：同键 2 版本 merge 前共存（未 OPTIMIZE，靠 FINAL 仲裁）。
- 绿：FINAL cape_5y=31.05——version 列取 max(ingest_ts)，后写 compute 版胜出。
- 再注入（反向竞争红证）：raw 版最后写 → FINAL cape=NULL——**机制本身只认最新不认好
  版本**，证明单靠 version 列不够，生产由"DAG 链 compute 恒后写 + akshare carry-forward"
  双保险闭合。
- 绿：携带版（carry-forward 语义）最后写 → FINAL cape=31.05。
- 净：ALTER DELETE 撤样，RBTEST 残留=0，FINAL=8118 与修前一致、2015 后病理 NULL=0。

**对抗2 模拟周六写入**（2026-09-19）
- 红注入：3 行（周五 1+周六 2）走生产 `_apply_trade_day_gate`，trade_days 为 trade_calendar
  实读（非 mock 集合；09-18∈set、09-19∉set 实测）。
- 绿：拦截 2/3 周六行（日志"交易日 gate 拦截非交易日行 2/3"实测），周五行通过；
  fail-closed 分支：日历读空 → 整批拦截（"整批拦截 1 行"日志实测）。
- 净：gate 在写前，零 CH 写入发生，无撤样需求。

**对抗3 mock 0 行写入**（akshare 返回空）
- 绿对照：生产配置地板腿（_check_row_floor_leg 生产函数+真实 CH）rows=22,476 ≥ 2000，
  breached=False。
- 红注入：row_filter 切至不存在切片（data_source='__rb_empty__'）= 窗口真实 0 行（与
  真实停更同一 SQL 判定路径）→ rows=0 < floor 2000 → **breached=True**。
- 绿留痕：Alerter 落盘 `data/failures/20260920_data_supply_sentinel_rbtest_145817.json`
  （task_id 带 RBTEST 标记，不混入真实告警流，留作证据）。
- 净：无表数据注入。

## 偏离与自裁记录（禁虚报条款）

1. **白名单外连带改动 3 文件**：`schemas/categories/market/market_index_valuation_daily.py`
   （DDL-as-Code INVARIANT 强制与实表一致；且原文件 MATERIALIZED 双写属文件漂移——
   原 DDL 根本建不出活表，一并修正）；`docs/.../capability_canonical_file_registry.yaml`
   （新 .md creation token 登记纪律）；`tasks.yaml/data_supply_sentinel.yaml/
   known_data_gaps.yaml` 均在 src/zephyr/data/** 白名单内。
2. **验收口径裁定**："修后 FINAL NULL 率=0"按"病理 NULL=0"验收——cape 的 rolling
   min_periods=750 使 2010~2014-11 为数学 warmup 区（每符号 1173 行），任何诚实实现
   都必 NULL；绝对 NULL 率 2346/8118=28.9% 如实上报。
3. **哨兵腿两处修档**（index 窗口 0→30；daily cols 拆出 turnover）：均为"结构性缺席
   ≠管线停更"的第一性修正，非为过检降级（min_ratio 0.95 未动；turnover 缺席原因=
   源头无数据非管线写 0），理由全部落 yaml 同批注释。
4. **净零声明**：+1 任务（compute_daily，无既有条目可承载日频职能，理由落 tasks.yaml
   注释）+1 冷备表（DROP 禁用下的可逆凭据）+1 scratch 空表 index_valuation_daily_v2
   （重建脚本中间产物，空表，留待 Owner 与冷备表同批净删）。
5. **算法债登记（不属本车道）**：cape_5y 绝对值量纲=CPI 在场分支既有算法行为
   （≈100×名义 CAPE，逐点通胀调整在 /100 下相消）；全库零消费方读绝对值（唯一消费轴
   cape_5y_pct 秩不变）；改动=裁定④域，留 Owner。
6. **并行会话协同**：施工中同 session 链1 改 akshare_provider.py（socket 超时护栏，
   ~L5565 区域，与本车道编辑区不重叠）；全部文件改前 acquire/过期重 acquire。

## 停手项与遗留

- turnover 供数：需流通股本 PIT 表（栈内暂无），建 kline 侧工单（已登记 known_data_gaps
  verification 段+哨兵 yaml 注释）。
- 10Y 国债 2010~2012-09 源稀疏（erp 848 行 NULL）、CPI 止于 2025-08（CAPE 通胀调整
  ffill 降级）——macro 域缺口，非本车道。
- 169 行（0.09%）close=0：退市/停牌长尾（000016 等 kline_daily 无对应行），合法缺席。
- 399006（创业板指）估值 0 行（中证官网无此品种，既有登记在案）。
- 冷备表/scratch 表/对抗告警 JSON 的净删：Owner 门位。

## 证据等级

表数字与 SQL 输出全部[亲验]（DatabaseService reader 实测）；对抗过程[亲验]（脚本
EXIT=0，输出全文见上）；merge 后台行为[亲验]（撤样后 raw 计数随合并收缩，故 FINAL
视角断言）；09-18 前历史（132 组病历重复等）[转述]（known_data_gaps 既有 verification
段），未复现（09-18 止血后已折叠，与批文"merge 折叠"预判一致）。
