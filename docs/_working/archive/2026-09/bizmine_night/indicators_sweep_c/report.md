---
ttl: task_bound
rule_form: data
verifiability: manual
title: 指标库全扫切片C 报告——TI 第3等分 55 列 IC 大海选全落 + vol_pct 三桶条件版 + top-10 待考池
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-bizmine-indc-20260919
prereg: docs/_working/bizmine_night/indicators_sweep_c/prereg_slice3_protocol.md（frozen commit 6a439f93e7，先于取数落盘）
---

# 切片C 报告（筛≠考）

> **一句话**：technical_indicator 163 因子列升序三等分的**第 3 份 55 列全部筛完（55/55，零空列）**，
> 预注册协议（横截面 Spearman 秩 IC × 前瞻 5/10/20 日 × IS 有效窗 2021-01-04..2023-12-29 / OOS 2024-01..2026-09 只报告
> × 除权剔除 × regime_state_anchored.vol_pct T-1 三桶 0.3200/0.7040 冻结边界）下产出 1320 行统计量全量入册；
> **top-10 待考池被「低波/反转负向家族」横扫**——波动率估计器族（parkinson/yang_zhang/rogers_satchell/stddev/var/trange）
> 包揽前八中的六席，与 F 车道 ATR 低波异象、切片A「50 列负向」三方互证；重叠 20/55 列（f_screened 11 + l1_pending 9）。

## 0. 协议回执

| 条款 | 执行情况 |
|---|---|
| 切片 | 171 列−8 键/元列=163 因子列（任务书称 162，实查 163 已登记）；升序三等分 [108:163)=**55 列**，与并行切片A[0:54)/B[54:108) 无越界 |
| IS 窗 | 预注册 2019-01..2023-12；TI period='daily' 实查仅 2021-01-04 起（探针在取数前完成并写进预注册 §2.2），**有效 IS=2021-01-04..2023-12-29**，各列有效 IC 日 650-727 |
| OOS 窗 | 2024-01-01..2026-09-18 只报告，有效 IC 日 645-649（尾部前瞻自然截断） |
| 前瞻 | 5/10/20 三档全跑，单程 879 秒（年分块读表+因子秩复用），未触发降档 |
| 除权剔除 | c3_fundamental.ex_dividend_event（2019-01..2026-09 全量），(t,t+h] 窗内事件样本剔除，F 车道同款 numpy 花式索引实现（规避 03:2x 勘误的 iloc 笛卡尔坑） |
| regime 轴 | regime_state_anchored.vol_pct argMax(ingest_ts) 去重 + T-1 PIT；桶日 IS=low 274/mid 289/high 164，OOS=low 169/mid 248/high 242，无 low_power 桶；禁用 alt_regime_signal ✓ |
| 重复行 | (trade_date,symbol) 4,290,444 组重复，ingest_ts 排序 keep 最后（与 L1 车道同口径） |
| 等价性核验 | 快速路径（因子秩复用）vs f2_lib 冻结式逐日比对：obv×h10 n=1375，**exact_equal=True，max_abs_diff=0.000e+00**（c_equity_check.txt） |
| 全量入册 | screen_results.csv **1320 行**（55×3 前瞻×4 桶×2 窗口），无一删除；排名键=IS overall h=10 \|IC_IR\| |

## 1. top-10 待考池（IS overall h=10 |IC_IR| 降序；筛≠考，升池不构成 PASS）

| # | 列名 | IC 均值 | IC_IR | t | 一句话机制 |
|---|------|--------|-------|---|-----------|
| 1 | parkinson_20 | -0.1036 | -0.641 | -17.0 | 高低极差波动率：**低波异象最强档**，IS vol_high 桶 IR -0.94；OOS 全桶同号但 vol_high 衰减至 -0.11（高波状态不稳，待考时注意） |
| 2 | yang_zhang_20 | -0.0944 | -0.631 | -16.8 | YZ 隔夜跳空+日内波动：与 parkinson 同族同强度，OOS vol_low/mid IR -0.63/-0.51 挺住 |
| 3 | rogers_satchell_20 | -0.0938 | -0.614 | -16.3 | RS 漂移无关波动：同族第三，OOS vol_low IR -0.60 |
| 4 | pvi | -0.0597 | -0.577 | -15.5 | 正成交量指标（累积积分）：放量环境抬升的 PVI=后续弱；cum 口径跨股可比性注意 |
| 5 | pvt | -0.0495 | -0.534 | -14.4 | 价量趋势（累积积分）：同上负向；OOS vol_high IR -0.41 相对最稳 |
| 6 | trange | -0.0952 | -0.523 | -14.1 | 真实波幅原始值（ATR 族输入）：负向低波，**价格量纲**（横截面可比性弱于 natr，已注 factor_nature=vol_est） |
| 7 | var_20 | -0.0866 | -0.462 | -12.3 | 20 日滚动方差：低波异象；**与 stddev_20 秩全同**（sqrt 单调变换），计 1 个有效候选 |
| 8 | stddev_20 | -0.0866 | -0.462 | -12.3 | 同上（重复对披露，多重检验 N_eff 相应 -1） |
| 9 | rsi_24 | -0.0542 | -0.421 | -11.3 | 24 日 RSI 超买回落：**OOS vol_high 桶 IC -0.118 / IR -0.587=高波环境反转最强**（top-10 内 OOS 高波唯一不衰减档） |
| 10 | wvad_24 | -0.0419 | -0.418 | -11.1 | 威廉变异离散量：**OOS vol_low 桶 IR -0.877**=低波环境量能扩张最危险 |

- 未进前 10 的 45 列（含仅有的 2 个正向列 vim_14 +0.031 / wr_14 +0.016，及价格水平列 trma/tsf_14/vwap 等）全部在 screen_results.csv 在册。

## 2. regime 条件版要点（Owner「状态×因子」主纲证据面）

1. **vol_est 族=「不看状态也活」但高波状态 IS 增益大、OOS 高波衰减**：parkinson/YZ/RS 三兄弟 IS 桶序
   vol_high(-0.84~-0.94) > vol_low(-0.69~~-0.71) > vol_mid(-0.45~-0.47)，**OOS 却反转成 low/mid 挺住、high 崩到 -0.10~-0.14**
   ——IS 的「高波更强」未经 OOS 复核，升考时条件化规则只能用 OOS 稳态（low/mid 负向）。
2. **rsi_24=高波反转档**：IS vol_high IR -0.66 → OOS vol_high IR -0.587（top-10 唯一高波桶 OOS 不衰减），
   「高波状态做超买回落」是本切片最干净的状态条件化候选。
3. **wvad_24=低波量能陷阱档**：OOS vol_low IR -0.877 全表最强桶读数——低波横盘期量价背离扩张的股票后续最弱。
4. **与切片A 互证**：A 车道 HIGH 桶集体最强（adosc HIGH IR -1.56）、本切片 IS 同构（vol_high 最强 6/10），
   但两切片 OOS 高波都衰减——「HIGH 桶增益」总体是 IS 现象，MID 桶无专属形态（互证 W2.4 MID 洼地判断）。
5. 诚实边界：vol_pct 轴 IS 桶日 164-289，桶×55 因子×3 前瞻的多重检验放大照旧存在（§4）；本报告不因桶读数择优改排名（排名键预注册钉死 overall h10 IS）。

## 3. 重叠标注（prior_coverage，规则预注册 §3）

- **f_screened 11 列**：rsi_6/rsi_12/rsi_24/stochrsi→FCT-TECH-066，stoch_fastk/fastd/slowk/slowd/wr_14→FCT-TECH-063，
  ppo→FCT-TECH-067，trange→FCT-TECH-064（F 车道 OHLCV 复算同族已筛）。
- **l1_pending 9 列**：obv/pvt/pvi/vr_26/wvad_24/vwap/vwma_20/var_20/tsf_14（IND-VOLUME/IND-STAT 18 档在考映射；
  其中 pvt/pvi/var_20/vwad_24 进了本切片 top-10——**升考前必须与 L1 车道 15 组考试结果去重归并**，避免双考同源）。
- **none 35 列**（保守默认，宁漏标不冒认）。重叠合计 20/55=36%。
- 预注册预估 12/9/34 vs 实测 11/9/35：crsi 实际落切片B（预注册映射表该行失效），偏差 1 列已如实修正。

## 4. 多重检验警示

- 本切片产出 55×3×4×2=**1320 组统计量**（IS 侧 660 组）。|t|>3.29 双侧 0.1% 线下期望假阳性 ~0.7 个/660 组；
  top-10 的 |t| 11-17 远过此线但**排名经过选择**，真实有效性只能由封闭族考试（预注册卡+N_eff+Deflated Sharpe）裁决。
- N_eff 修正：var_20≡stddev_20 完全同秩，55 列有效候选 **54**；vol_est 六席高度同源（IS 两两秩相关预期 >0.9），
  实际独立族数远小于表面数——升考按族合并计账。
- 历史前科在案：宽测好看→窄测/正考大面积衰减（79 严选只活 1 条；L1 本夜 CORREL/BETA 过一关不过 E4）。

## 5. 复权暂定声明与解释边界

1. kline_daily.adj_factor 恒 1：全部结论=**暂定**，待复权链修复后复核；缓解=除权事件窗剔除（三档前瞻各自生效）。
2. **水平量列降级解读**（预注册 §4.2 预登记）：trma/tsf_14/vwap/vwma_20/wma_10/senkou_span_a/b/tenkan_sen/
   supertrend_10/sar 共 11 列 factor_nature=level，其负向 IC≈**名义价格水平效应**（低价股异象），不是该指标
   设计语义的择时信号；本筛按协议原值入算未做标准化，组队引用这些列前必须先做去水平化改造。
3. cum_integral 列（obv/pvt/pvi）：上市以来累积路径，跨股量纲不可比，负向方向可参考、幅度不可比。
4. 因子值取自 TI 物化宽表，本车道未复算物化正确性（超时间盒，登记为边界）；切片A 披露的 2026 年
   最新版去重异键 6.5% 现象同表同规则适用（2021-23 排名窗 ≤146 行/年，可忽略）。
5. 数据缺口：无。55 列全有效，零空列零跳过——「未达成清单」为空。

## 6. 偏离登记

| # | 事项 | 性质 |
|---|------|------|
| 1 | 预注册 f_screened 预估 12 列→实测 11 列（crsi 落切片B，映射行失效） | 预注册内预留修正位，已按实测修正 |
| 2 | 首次 commit 尝试（prereg+token 载体注册表同批）被 REGISTRY-MASS-DELETION 拦截：注册表 index 含他会话 staged 净删 4 条 crypto_probe token 条目 | gate 正确拦截外来净删；按 RULE-GIT-SAFE「每轮修改即 git add」重载 worktree 版（纯插入 12 行/0 删）后 requeue 队列项成功，prereg commit 6a439f93e7 归属核实无误；净删归属仍留他会话，本车道未代修未吸收 |
| 3 | token 载体注册表改随本批（最终 commit）同落 | 时序调整，非内容变更 |
| 4 | 心跳首启遇 SessionRegistry 并发写冲突（WinError 5，他会话心跳同窗写注册表），register 本身已成功 | 瞬态竞态，登记 |
| 5 | 台账行追加首 25+ 次尝试被 StaleWriteRefused 拒，**根因=本代理 base-hash 算法错**（对原始 CRLF 字节做 sha256，而 safe_write_text 参照值=content_sha256(decoded text)），非多车道竞争；改用 content_sha256 后一次写入成功，台账行已落并随本批 commit（含 PB 车道在途 bullet 一行随批落，共享台账追加语义） | 工具误用根因更正（诚实条款），初版报告误诊为并发冲突，以本条为准 |

## 7. 产物

- 本报告 + `screen_results.csv`（1320 行）+ 预注册 `prereg_slice3_protocol.md`（frozen commit 6a439f93e7）。
- 中间件（复算可用，TTL 清理前）：`.runtime/tmp/bizmine/indc/`（c_run.py 管线、c_results_long.csv 长表、
  c_equity_check.txt 等价性核验、c_regime_volpct_daily.csv T-1 vol_pct 日序、cache/ 宽表缓存）。
- 下一步（不在本车道）：top-10 待考池 → 与切片A/B 及 L1 在考池归并去重 → Owner 挑选 → 预注册卡 → 沙箱三关 → E4 正考。
