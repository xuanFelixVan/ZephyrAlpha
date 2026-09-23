---
ttl: task_bound
title: 晨报·板块线施工班 st-secbuild-20260923（批0-批3 全量交付）
created: 2026-09-23
sid: st-secbuild-20260923
lane: sector_line
report_hour: 2026-09-23 晨（通宵班）
---

# 晨报六要素（st-secbuild-20260923）

## 一、完成清单（含落点）

| 批 | 交付 | 落点 |
|---|---|---|
| 批0a | mootdx 通道诊断**收口**：TCP 通/`get_security_count`/`get_finance_info` 通，`bars`/`index_bars`/`quotes` 全 None（6 台可靠表+编号镜像）=服务端选择性断供，客户端无修；调度侧每 5min 正常打火（日志实证），非调度缺位 | 诊断证据本报告 §二 |
| 批0a 修复 | `synth_board_minute.py`（方案 J 既有件）幂等回补 09-16/17/18/21/22 五个交易日，139,780 行/日（580 板×241min），`data_source='synth_sh'` 显式标注，tdx 真值行零触碰 | c1_market.kline_sector_intraday 09-11→09-22 逐日连续 |
| 批0b 诊断 | 东财 fflow 字段面 CDN 级掐灭：`stock_market_fund_flow` 自 09-18 全灭；实测 fields2 仅 f51,f52,f53 可通，加任一字段即 RemoteDisconnected，编号镜像同灭 | 诊断证据本报告 §二 |
| 批0b 修复 | `market_fund_flow_daily` 缺失 3 交易日（09-18/21/22）混合回填落库：close/pct←kline_index（**经 09-17 源行逐位机械校准**：3875.6/-0.41/13409.91/-0.33+pct 分母=两市场成交额），layer 净额源字段被掐如实 NULL；`data_source='em_fflow_hybrid'`，quality_flag=0 | c1_market.market_fund_flow_daily；akshare_em 历史 117 行零重写 |
| 批0b 代码 | `_fetch_market_fund_flow` 混合回填兜底（akshare 失败→缺失日 gap-fill，零历史重写） | worktree 提交（本批） |
| 批1 | `sector_state_aggregator.py` 纯函数聚合器：五成分（momentum 0.4/0.3/0.3、RRG DualEma10/26+whipsaw、涨停比40/梯队30/趋势30 强度、净流入分位、5 状态市场级）**全指认 22 号 spec §3.1①④⑧⑨ 零重造** + D2 偏好映射 3×3 frozen 表（tilt 0.8-1.2、禁入象限、契约 mock 轴） | src/zephyr/signal_ashare/sector/；15 单测 |
| 批2 | `sector_state`/`sector_preference` 两表 DDL-as-Code + business_data_categories 上户 + apply 注册；`sector_state_pipeline.py` 编排器（close_final 15:10 定格 / pre_open 09:15 复制+重映射，emotion 真值 v0.1.0 消费）；scheduler 特殊双槽 + 总闸旗标 | 两表 938 行实弹（09-22 cf + 09-23 po）；schedule.yaml |
| 批2 消费端 | **供料端全绿**：`load_l2_admission()` 实测 top=5/retained=294/score=57.0/pref=OFFENSIVE tilt1.2；**消费端**因 daily_gate_snapshot.py 带他会话在途 WIP（水位桥+249 行）避让未直改，出**即贴补丁**（5 行） | docs/_working/sector_line/batch2_consumer_wiring_patch.md |
| 批3 | 两卡 frozen 化（v1.0，先于实跑落盘）+ 跑批器实跑判档 + 判档报告 | exam/prereg_exam_report_v1.md + results_v1.yaml |
| 纪律件 | 22 单测两轮零；考试数字两轮逐位一致；translation 5 条；token 10 条；depgraph 3 节点；.json→.yaml 目录契约合规 | 各注册表 |

## 二、关键发现

1. **判档（批3，裁定#325 判档制，零"全绿"表述）**：
   - **S10 = NO_EDGE（如实记 RED）**：Q5−Q1 全窗均值 −0.27%、NW t=−0.57、年度正号率 0.20（2022-2025 四年连负）。预登记证伪风险兑现——q20 权重动量在板块一日游生态下反向。**后果**：momentum_pct 排 Top-N 作"强势板块"的消费口径未获考试支持，不升待考池；本轮禁调权（frozen 预承诺），调权归下轮新卡。
   - **D2 主判 = INSUFFICIENT**（双轴真值窗 16 日 <120，预登记兑现）；**单轴降档版 = NO_MAP**（805 日，均值 −0.35%、t=−1.71、命中率 0.517<0.55）。偏好映射解释力不成立（单轴口径），preference_label/tilt 不作权重输入，banned_quadrant 保留保守过滤语义。
2. **TDX 免费行情协议栈系统性死亡**（09-10 15:15 起）：TCP 层活、元数据类调用活、行情数据类调用全灭——免费 hq 数据面加速关闭的又一实证（北向披露调整同族趋势）。kline_sector_880 日K 无恙（tqcenter 腿）。
3. **东财资金流字段面被掐**（09-18 起）：CDN 层选择性断供，akshare 修复无期。market_fund_flow_daily 无代码消费方（实测），按比例原则做 hybrid 缺失日兜底。
4. **数据面两处历史假象揭穿**：①kline_sector_intraday"数据到 09-15"实为 synth 合成行（known_data_gaps 已登记，本次延续其口径补齐）；②money_flow（tushare 腿）与东财大盘口径**不同源不同众**，逐股求和 ≠ 大盘层值——任何"个股聚合≈大盘资金流"的消费假设不成立。
5. **CH 容器内存受限**（cgroup 10GB，可用 6.8GB）：reader 配额下 DISTINCT/IN-子查询大 spool 会 500，查询须日历窗+Python 侧去重（管道已按此形态固化）。

## 三、呈批项（Owner 门位）

1. **req_sentinel_02（既有待裁）新证据**：tdx 五盘中任务真值腿已判死（证据链完整），建议裁定=切源（tqcenter 分钟待活体验证）或正式停用+synth 供给常态化；本班未代裁，任务保持原状（每 5min fail-fast 空转，日志有痕）。
2. **消费端即贴补丁批准**：batch2_consumer_wiring_patch.md（5 行，daily_gate_snapshot L2 三原料接线+编排器注记）——待水位桥 WIP 落地后贴。
3. **G7/G13 维持登记待批**（本班未擅动）：G7 资金深史回溯、G13 ETF 载体。

## 四、死信/事故

1. **st-combine-0016 误入死信（本班责任，已自愈条件在案）**：本班从 worktree 误跑主队列 drain，landing 环境错配（worktree 缺 library/registry_family 门禁子目录）致该会话项进死信。**修复=requeue 即活**（主区环境完好），交维护班/该会话执行。
2. 本班两次队列入袋进错队列（worktree 本地队列），已改直交路线；worktree 队列残留项已清理，无双落风险。

## 五、待办/明日

1. **09:30-09:35 盘中活体验证 tqcenter 1m/5m 对 880 板**（凌晨窗口返回空，须盘中复验）：命令=joiner 侧 `TQCenterProvider.connect()`+`refresh_kline(period='1m')+get_market_data(count=10)`；若出数→五分钟任务切源（tasks.yaml 5 行，随 req_sentinel_02 裁定）；若空→板块分钟K真值源立项（东财 BK 码映射方案备选）。
2. 调度器重启时机：管道/排班/provider 兜底激活须重启 data scheduler（当前进程 09-22 13:24 起）——建议今日 09:00 前或 15:05 后（避开 15:10 首跑窗口由 Owner 定）。
3. 明晚集成窗：emotion 真值已可用（v0.1.0，axis=ok 实证），D2 重考须等真值窗 ≥120 日（约 2027-03）。
4. 双基地巡检：market_fund_flow 今日 16:30 daily_capital 槽（provider 兜底激活后应自动补齐当日行）。

## 六、临时清理确认

- .runtime/tmp/secbuild_mff_backfill.py 已删；tmp/secbuild_commit*.log 已删；worktree 队列残留项已清。
- worktree 内 3 个在飞 gate 件（state_vocab/tag_vocab/blood_flesh）为主区借用副本（未跟踪、不入提交面），供 worktree 门禁链 import；主区原件属在飞会话，勿动。

## 七、晨间追加（09:00-10:00 实况）

1. **提交落地**：f44c1bfd74（worktree 分支 ai/st-secbuild-20260923/sector-line-construction，18 件，
   经 14 轮门禁链磨合全过：复杂度拆函数/参数对象化/ALGO_FLOW 卡+边/目录容量/导入序/ruff 全绿）。
   **merge 回 dev 被阻断**：主区 gate 文件（25 个 commit_gates/*.py）带他会话在途 WIP，
   merge 需更新同批文件被拒——按"他会话在途不代修"避让，**合并待该 WIP 落地窗口执行**
   （session_worktree.py merge st-secbuild-20260923，零损失，分支已固化）。
2. **tqcenter 盘中复验未成**：tdxw.exe 客户端在跑，但 tq 插件握手失败（"连接路径为空/请确认
   是否打开通达信客户端"）——分钟数据能力仍属未验证。**裁决点=今日 16:30 kline_sector_880_incremental
   日K 任务实跑**（同一 connect 链路）：成功→切源方案可行性升级；失败→tqcenter 通道本身需要修复排班。
3. 翻译/token 条目已被 oddjobs 批（5b6ee808a6）吸收落地（注册表先行模式，披露在案）——
   本班两个注册表 yaml 不再随批，避免热文件拉锯。

## 八、增补令执行实录（Owner 全批 2026-09-23：G10+G7）

### G10 = board_index_1m 空表退役执行（DROP 路径，留痕）

- **二选一裁定依据（通道诊断结果）**：批0 判死 tdx 真值腿；分钟供给重建走 synth_board_minute →
  **kline_sector_intraday**（不经 board_index_1m）——该表无重建理由 → **选 DROP**。
- **三步验证**：①必要性=0 行+零读端（唯一引用=生产者脚本 board_index_realtime.py，manual/beta 无调度挂载）
  ②真实性=count()=0 实测 ③可逆性=DDL 已存档（ReplacingMergeTree(ingest_ts)，(board_code,period,trade_time)
  键，本报告留痕可随时重建）。
- **执行**：DROP TABLE 完成（探针=0）；登记册销行=docs/library/data.md TBL 行 +
  data_inventory.md 行（该表不在 business_data_categories/table_registry，无表册行）。
- **边界**：board_index_tick（单日 5564 行试点）**不在本批授权**，维持 C 态待批；
  生产者脚本同步待 board_index_tick 处置时一并裁。

### G7 = 资金深史回溯聚合（深度实测定案）

- **接口实测**：money_flow 2026-06-01 起 ✓；**sector_constituent SCD-2 valid_from 2026-07-23 起**（880 轴
  成分映射硬约束）；limit_up_pool/daban **2026-09-01 起**（强度维度约束）。缺口单原估"可拼 ~3.5 个月"
  被实测收窄。
- **执行**：sector_state close_final 历史回补 **09-01→09-21**（全质量窗：五成分原料齐备），
  15 个交易日 × 469 板全部成功；累计 16 个交易日深史（含 09-22），net_inflow_pct/象限逐日全覆盖。
- **如实缺口**：07-23→08-31 窗资金流可算但涨停池缺史→强度维度会静默降档，按禁硬凑纪律不回补
  （涨停池深史回源后下轮新卡再补）；06-01→07-22 窗成分映射缺，同理不补。
- **净零声明**：零新表零新脚本（复用 sector_state_pipeline 幂等重放），数据落既有 sector_state 表。
