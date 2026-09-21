---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# Hyperliquid——数据源现状、补缺渠道与风险清单 2026-09-20

> 剪报两条：风险结构分析 + "数据源下载"线索。核实结果：**数据面我们已领先——HL 四表已在库**；风险分析合理，入交易对手风险清单。

## 内部现状 `[亲验]`（判定 A：数据已接）

- 四表在库：`c1_market.hl_perp_snapshot_daily` / `hl_oi_snapshot_daily` / `hl_funding_history` / `hl_liquidation_raw`；provider=`src/zephyr/data/implementations/hyperliquid_provider.py`（2026-09-18 夜班 D5 波2 建成）。
- **资金费深回溯 100%：4,655,619 行、234/234 币、直抵 2023-05-12**（落 `hl_funding_history`；见 docs/_working/archive/2026-09/altdata_night/01_morning_report.md）。
- 注意：snapshot 两表 2026-09-18 起自积，**不可回补**。
- 周边配套已齐：crypto_kline_daily（binance.vision 换源 7×24）、sentiment_panel（恐贪 ingest active）、crypto_shadow_gate。

## 外部补缺渠道 `[外部]`

| 需求 | 渠道 | 边界 |
|------|------|------|
| L2 订单簿快照/资产上下文历史 | 官方 S3 桶 `hyperliquid-archive`（requester-pays） | **约每月一批、仅此两类、官方明示不保证及时完整** |
| K 线历史 | 官方 info API `candleSnapshot` 自行分页（单次上限 ~5000 根）或官方 python SDK `hyperliquid-python-sdk` | 无官方批量下载 |
| 逐笔/深度事件史 | 第三方：Tardis.dev（官方支持 HL，**月度免费 CSV**）、CoinAPI（HYPERLIQUID，L4 订单事件/资金费）、社区归档 Hydromancer | 付费/三方可靠性自担 |
| 区块级原始数据 | S3 `hl-mainnet-node-data`（fills/explorer/events by block） | 粒度原始，需自加工 |

- 基本事实核对：Hyperliquid=链上永续+现货 DEX，HyperCore（链上订单簿引擎）+HyperEVM 同受 HyperBFT 共识保护（HyperEVM 非独立链）。

## 风险清单条目（剪报观点+核实）

- 链上清算解决的是**平台卷款跑路/挪用客户资产**风险（FTX 式灾难）——已消除。
- **未消除：撮合环节道德风险**——订单匹配、价格、滑点仍可被平台侧做手脚。行动：币圈轴若以 HL 为交易对手/信号源，在策略风险清单登记此条；信号源用途不受影响（我们只取数据不托管资产）。

## 缺口与行动（判定 B）

1. 币圈 K 线深史若需 HL 口径：优先 Tardis 月度免费 CSV；次选自建 candleSnapshot 分页采集器（挂数据集成器，注意速率）。
2. funding/OI/清算三条我们已自积且深回溯完成——**无需外采**。
