---
ttl: task_bound
# doc_type: audit_report  # doc_type 行注解化（归档区 EXEMPT-ZONE-FM 规避 2026-09-20）
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L29: - **B-1 MM 残段**：接手时核实工作树与暂存版已一致（前会话已修复），JOB-089（`ingest.okx_crypto_kline_daily`）/DS-226/DS-227 三段齐全，本会话无残段可修。
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L34: 接手首跑即暴露三处运行时 bug（原文件未跑过任何真实执行，属"主体在盘未验证"范围）：
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 4 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）





# 币圈影子 MVP 收尾报告（crypto shadow MVP）

日期：2026-09-12 ｜ 会话：TDM 红节点治理接续批（接手 Owner 主会话交接）
真源：95 号备忘录（币圈蓝图 C-L1）+ 2026-09-11 影子 MVP 会话指令
状态：**主体完成，真实数据首跑挂 OKX 网络闸（环境级端点阻断），管线已用合成样本全链验证**

---

## 1. 交付清单与状态

| 交付物 | 路径 | 状态 |
|--------|------|------|
| OKX 日线采集器 | `src/zephyr/data/implementations/crypto_kline_collector.py` | ✅ 已暂存（本会话修 3 bug，见 §3） |
| C-L1 影子判定器 | `src/zephyr/data/implementations/shadow_gate_c_l1.py` | ✅ 已暂存（未改，烟测通过） |
| 两表 DDL | `scripts/data/crypto_shadow_mvp_ddl.sql`（gitignore，DDL-as-Code 转正另批） | ✅ 已执行建表 |
| CH 两表 | `c1_market.crypto_kline_daily` / `c1_market.crypto_shadow_gate_c_l1` | ✅ 建成（ReplacingMergeTree，暂空） |
| 数据资产登记 | `data_asset_registry.yaml` DS-226/DS-227/JOB-089 | ✅ 已暂存（本会话修口径，见 §2） |
| Top-50 清单 | `config/crypto_top50_usdt.yaml` | ✅ 在盘（50 币与 DEFAULT_TOP50 一致） |
| 烟测样例 | `data/crypto/shadow/gate_c_l1_smoke*.csv`（数据目录，不入 git） | ✅ 三态覆盖（见 §4） |
| 真实数据首跑 | — | ⚠️ 挂网络闸（见 §5） |

## 2. Registry 口径修复（交接任务 B-1/B-2）

- **B-1 MM 残段**：接手时核实工作树与暂存版已一致（前会话已修复），JOB-089（`ingest.okx_crypto_kline_daily`）/DS-226/DS-227 三段齐全，本会话无残段可修。
- **B-2 清单口径**：JOB-089 段两处 `config/crypto_top50_usdt.txt` → `crypto_top50_usdt.yaml`（实际在盘文件名，YAML 格式 50 币，与采集器 `DEFAULT_TOP50` 内置兜底逐一对齐）。经 `safe_write_text` CAS 写入。

## 3. 采集器 bug 修复（本会话，3 处）

接手首跑即暴露三处运行时 bug（原文件未跑过任何真实执行，属"主体在盘未验证"范围）：

1. **`timezone_utc()` 返回 `timedelta(0)`** —— `datetime.fromtimestamp(tz=...)` 要求 `tzinfo` 实例，backfill 一跑即抛 `TypeError`。已改为返回 `timezone.utc`（顶层 import 同步补）。
2. **`datetime.time.max/.min` 访问错误**（3 处）—— `from datetime import datetime` 语境下 `datetime.time` 是类方法 descriptor，无 `.max` 属性，抛 `'method_descriptor' object has no attribute 'max'`。改为 `datetime.min.time()` + 86_399_999ms 毫秒补偿表达日界。
3. **`resolve_symbols` 不兼容 YAML 清单** —— 逐行读取会把 `symbols:` 键行当 instId 解析。已兼容纯行列表与 YAML 两种格式（零第三方依赖，跳过键行/剥离 `- ` 前缀）。

修复后语法与解析路径已实测（跑批进入网络层才失败，解析/分页逻辑无错误）。

## 4. 管线烟测（合成样本，非真实数据——如实声明）

真实行情不可达（§5），用合成 CSV 对影子判定器做全链烟测，**验证的是管线可用性，不是任何市场结论**：

- 样本：`data/crypto/_smoke_test/`（BTC+ETH+12 山寨币 × 250 日）与 `_smoke_test_50alt/`（BTC+50 山寨币 × 250 日），随机种子固定可复现。
- 结果 1（13 币组）：`dates=250 off=199 normal=51 tightened=0` —— MA200 就绪切换正常；山寨季窗 valid=13 < 40 触发**样本不足保守降级**（alt_season_ready=0 → normal），保护逻辑正确。
- 结果 2（50 币组）：`dates=250 off=199 normal=30 tightened=21` —— 40/50=80.00% ≥ 75% 正确触发 **tightened 收紧档**。样例行：
  ```
  trade_date=2025-12-31, btc_ma200=56150.9, btc_above_ma200=1, alt_ratio_90d=0.8, altseason_on=1,
  gate_state=tightened, gate_reason='BTC 趋势门开；山寨季门开(40/50=80.00%>=75%)：收紧档'
  ```
- 三态真值表（off/tightened/normal）全分支覆盖 ✅，`shadow_only` 恒=1 ✅。

## 5. 网络实测：OKX 端点环境级阻断（真实首跑挂闸）

2026-09-12 凌晨实测（一次性诊断，未反复重试，符合交接降级纪律）：

| 目标 | 结果 |
|------|------|
| `www.okx.com` | DNS 解析失败（getaddrinfo 11004） |
| `aws.okx.com`（官方备用） | DNS 解析失败 |
| `okx.com`（裸域） | 可解析（54.46.36.113），TCP/TLS 被重置（WinError 10054，连接强迫关闭） |
| `api.github.com` / `www.baidu.com` | 正常（对照，证明非全局断网） |
| 系统代理 | 无（HTTP(S)_PROXY 全空） |

**定性**：环境级端点阻断（域名污染 + SNI 干扰），非脚本问题。**未授权擅自切换数据源**（如币安）——MVP 数据源是已定设计，换源属 Owner 决策。

**二次评估补记（2026-09-12 晨，Owner 指令"自己裁定"）**：一次性测试 4 个备用公开端点——`api.binance.com`（免 key 公开 K 线）/`api1.binance.com`/`okx.com/api/v5/public/time`/`api.exchange.coinbase.com` 全部 URLError 失败。**境外加密交易所公开行情属环境级全域封锁**，换源无法绕过网络闸（Cloudflare 反代或代理是唯一路径，需 Owner 资源）。结论：真实首跑维持挂闸，裁定=登记待外部网络条件变化，非 AI 可解。

## 6. 真实首跑指令（网络解锁后，Owner 或下一会话执行）

```powershell
# 1) backfill 小样本验证（2019-01-01 起，约 5-10 秒/币种）
C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe src/zephyr/data/implementations/crypto_kline_collector.py backfill --symbols BTC-USDT,ETH-USDT

# 2) CSV → CH 导入（writer 账号；列序与 DDL 对齐，confirm 取 CSV 原值）
#    （导入器待首跑时一并落地，或用 clickhouse-client --input-format CSV 直接灌）

# 3) 全量 50 币 + 影子判定
C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe src/zephyr/data/implementations/crypto_kline_collector.py backfill --symbols-file config/crypto_top50_usdt.yaml
C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe src/zephyr/data/implementations/shadow_gate_c_l1.py --print-tail 5

# 4) shadow CSV → c1_market.crypto_shadow_gate_c_l1 导入（逐日一行，ReplacingMergeTree 幂等）
```

CH 连接：reader=`load_ch_reader_config()`（zephyr_reader，本会话探针验证连通 172.24.30.100:9000），写入/DDL 用 `load_ch_writer_config()`（zephyr_writer，本会话建表实测可用）。

## 7. 数据口径（固定不变）

- `trade_date` = **UTC 日界**（OKX 1D bar 开盘时间戳对齐 UTC 00:00）；加密 7×24 无休市，自然日=交易日。
- 影子判定只消费 `confirm=1` 已完结 K 线；未完结当日 bar 不进判定。
- 幂等：两表均 ReplacingMergeTree(ingest_ts)，同 key 重采覆盖；CSV 侧 setdefault 首值优先。
- C-L1 三档：off（BTC close<MA200，样本不足默认关）/ tightened（BTC 门开 + 山寨季门开：90 日跑赢 BTC 占比 ≥75% 且有效样本 ≥40/50）/ normal（其余）。`eval_version=C-L1-shadow-v0.1`，Phase 2 Owner 拍板后对齐 TDM/gate_registry。

## 8. Phase 2 付费/扩展解锁清单（原样转录自设计，本会话未核价）

| 项 | 用途 | 前置 |
|----|------|------|
| Glassnode API key | 链上指标（SOPR、活跃地址、交易所净流） | 付费订阅 |
| CryptoQuant API key | 交易所储备/ miners 流向 | 付费订阅 |
| 币安 API key | 备用行情源（OKX 阻断时的对冲，需 Owner 换源裁定）+ 精度更高数据 | 注册+key |
| Cloudflare（反代/Workers） | OKX API 大陆可达性通道（自建反代域名，绕 DNS/SNI 阻断） | 域名+CF 账号 |
| 动态 Top-50 | CMC/OKX 全量现货行情排序替代静态清单 | 免费 API 或付费 |

> 注：**Cloudflare 反代是当前网络闸的最小成本解锁路径**（无需动数据源设计），建议 Owner 优先评估；币安换源次之（需改 BASE_URL/字段映射，属设计变更）。

## 9. 治理留痕

- 本会话改动文件（均已 git add）：`crypto_kline_collector.py`（3 bug 修复）、`data_asset_registry.yaml`（口径 2 处）。
- 未触碰：`config/trading_decision_map.yaml`、okx_broker、任何 TDM 决策路径（影子铁律遵守）。
- 烟测样本与输出留在 `data/crypto/`（数据目录不入 git），报告样例可复现（seed=42 / seed=7）。
