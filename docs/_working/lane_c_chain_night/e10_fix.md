---
ttl: task_bound
title: e10_fix (20261001 删除事故后重建)
note: 重建件
---

# E10 数据健康修复环节簿（e10_fix）

> 注记（20261001 删除事故后重建）：本簿原落于主区 docs/_working/lane_c_chain_night_20261001/e10_fix.md，
> 因他队清理事故连目录删除，按上下文原文重建于本 worktree 落点；内容与原版一致（含 backtest 归属补充行）。
> e10_data_health.md（普查簿）非本代理产出，未重建，需其产出方自行恢复。

- 会话: st-lanech-20261001（E10 施工代理）| 日期: 2026-10-01
- 施工区: .worktrees/st-lanech-20261001（worktree 隔离，未 commit——提交走总包 GitCommitGateway）
- 真源输入: docs/_working/lane_c_chain_night_20261001/e10_data_health.md（§1 病列清单 / §6 处方）
- 红证据存档: worktree .runtime/tmp/e10_red_evidence.txt（修前 pytest 21 failed / 11 passed）

## §1 逐列修复表（12 列；修法模式对齐已落 MCGINLEY 重置播种+终防护）

| # | 列 | 类(文件) | 病型 | 修法 | 红证据（修前实测 Inf） | 绿证据 |
|---|----|---------|------|------|----------------------|--------|
| 1 | pvt | PVT(volume.py) | cumsum 无防护，单点毒化尾链（普查 256.9 万行） | cumsum 前步进 isfinite 过滤（非有限→0）+ 输出终防护 | close=[10,11,0,12,...] → 尾链 4 格 inf | 同输入全有限 |
| 2 | pvi | PVI(volume.py) | cumprod 混入非有限因子（688291 964 行） | 因子非有限/≤0→中性元 1.0 + 终防护 | close 前收 0+放量 bar → 3 格 inf | 同输入全有限 |
| 3 | nvi | NVI(volume.py) | 与 pvi 同型雷（census §3 点名"同一颗雷"） | 同 pvi | 缩量 bar 分支 → 3 格 inf | 同输入全有限 |
| 4 | vr_26 | VR(volume.py) | 分母 2×down+flat=0（26 窗全涨） | 分母 >0 掩码 → NaN + 终防护 | 全涨窗(period=3) → 8 格 inf | 同输入 NaN 且全有限 |
| 5 | roc_12 | ROC(momentum.py) | 前收 0 → C/0 | 基座 isfinite 且 ≠0 掩码 → NaN + 终防护 | close[0..11]=0 → 6 格 inf | 同输入全有限 |
| 6 | trix | TRIX(trend.py) | TR 链种子 0 → pct_change 除 0 | prev_tr isfinite≠0 掩码 → NaN + 终防护 | close 前段 0 → 1 格 inf | 同输入全有限 |
| 7 | cvi | CVI(volatility.py) | EMA 基期 0 → shift 比值除 0 | 基期 >0 掩码 → NaN + 终防护 | 前段 H=L 零区间 → 4 格 inf | 同输入全有限 |
| 8 | vip_14/vim_14 | VORTEX(trend.py) | ΣTR=0（close 缺失停牌段 TR skipna=H−L=0 + H=L 窗） | tr_sum>0 掩码 → NaN + 终防护 | close=NaN+H=L 变价 → vip 6 格/vim 同 inf | 同输入全有限 |
| 9 | cti_12 | CTI(momentum.py) | 零方差窗 den=0+浮点尘（daily 12,880 行） | den>0 掩码 → NaN + 终防护 | 常数 close c=0.1 → 7 格 inf（真实低价即可触发） | 同输入全有限；正常趋势值域 [-1,1] 不变 |
| 10 | correl_30 | CORREL(statistics.py) | 零方差窗浮点尘（78,220 行） | 输出 isfinite 清扫 → NaN | 常数 close c=0.3+ramp vol → 4 格 inf | 同输入全有限 |
| 11 | boll_pctb | PercentB(volatility.py) | 零带宽（一字板，002916 实证 2 行） | 带宽 >0 掩码 → NaN + 终防护（防御锁定） | 白盒构造 inf 不可复现（pandas 常数窗 mean/std 一致精确 → 0/0=NaN）；census 2 行=历史遗留 | 零带宽窗→NaN 断言 + 全有限 |
| 12 | md_14 | MCGINLEY(trend.py) | 断层发散（已由同会话他代理落重置播种修复） | 未触碰（勿回退） | （他代理红证据） | 本批新增回归锚：44→12.6 断层输入全有限 |

## §2 写链 isfinite 闸（治本的治本）

- 函数: `sanitize_indicator_matrix(df) -> (df, n_fixed)`，internal_compute_provider.py 模块级（ALL_PERIODS 之后）；浮点列逐格 `np.isinf` → NaN，NaN=Nullable 合法值保留；零拦截零拷贝快路径。
- 收口点: `_compute_all_indicators` 出口（pd.concat 之后、返回之前），拦截数 >0 时 warning 留痕。
- 标量兜底: `_build_row` 值过滤 `pd.isna` → `not np.isfinite`（NaN/±Inf 一律 None，防绕过矩阵闸的路径）。
- 测试: TestWriteChainIsfiniteGate 6 例（闸函数 3 + _build_row 1 + 集成 2，含 InfSpitter 替身与全注册指标端到端）。
- 红证据: 修前 _build_row 对 ±Inf 原样入行（assert inf is None 失败）；闸函数不存在（ImportError）。
- 定性: 闸是兜底不是豁免——12 列算法面照修（巨值 garbage 非 inf 仍会穿透，故算法修不可省）。

## §3 附带防御（非 12 列清单，语义保持）

- stderr_14（statistics.py）: SSR 闭式消去浮点尘负值 → sqrt RuntimeWarning（filterwarnings=error 下炸测试/未来 pandas 炸生产）→ `ssr.where(ssr>=0)` 保 NaN 语义。端到端全注册指标跑断层序列时暴露。
- pct_change(fill_method=None)（pvt/pvi/nvi/trix 四处）: NaN close 不再 pad（pandas 弃用默认；NaN bar 步进=NaN → 防护过滤，语义=跳过无效 bar）。既有测试全绿证明有限输入行为不变。

## §4 测试读数

- 新例: tests/zephyr/factor/technical_indicators/test_numeric_guards.py = 32 passed（逐列红→绿 14 + 写链闸 6 + 边界冒烟 11 + md 回归锚 1）。
- 回归: tests/zephyr/factor/technical_indicators/ = 1152 passed, 5 skipped（修前既有断言全保持）；provider 三套件 = 32 passed；tests/factor/ = 826 passed；tests/backtest/ 见下方补充行。
- 红留痕: 修前 21 failed / 11 passed（e10_red_evidence.txt）；其中 pctb 两例修前即绿（防御性锁定，红证据以 census 2 行实证 + 0/0 平台依赖语义记档，未虚构造红）。

## §5 真数据一发验证（只读 SELECT，query_strict 通道，零写库）

- 920729（断层 44→12.6, 1560 根 daily, 断层>50% 共 1 日）: 12 列输出全有限 PASS
- 300650（19.71→9.77, 1881 根, 1 日）: PASS
- 920821（79→10.03, 1119 根, 3 日）: PASS
- 脚本: worktree .runtime/tmp/e10_real_verify.py
- 复发闸验证: §2 集成测试构造含 ±Inf 的指标输出行 → 闸转 NaN（出口 isinf=0）。

## §6 六向台账

| 方向 | 状态 |
|------|------|
| ① 算法修面 12 列 | 完成（11 列本批修 + md_14 他代理已修+本批回归锚）；11/12 红证据可复现，1/12（boll_pctb）防御锁定如实记档 |
| ② 写链 isfinite 闸 | 完成（矩阵收口+标量兜底双保险，6 测试） |
| ③ 红绿留痕 | 完成（红 21F/11P 存档，绿 32/32） |
| ④ 现有回归 | 完成（1152+32+826 provider/factor 域全绿；backtest 补记见下） |
| ⑤ 真数据验证 | 完成（三断层股 12 列全有限） |
| ⑥ DB 洗数 | **移交**：现存 Inf 行由修后 weekend full_refresh 重写自愈（含 md_14 ~28 根巨值发散带重算）；定点 delete_where 重填未做（属破坏性 DB 操作，归 Owner 门位，census §6 pvt 处方含此步） |

补充: tests/backtest/ 全量 = 2217 passed, 8 failed, 9 errors——8F/9E 全部落在 kronos_finetune_pkl_prep（qlib 环境夹具）/n_trial_ledger（台账数据态，fails-closed 设计）/strategy_production_map_adversarial（数据引用态）/weight_ssot_single_authority（他车道 WIP 域），四文件经 grep 核证零引用 technical_indicators/internal_compute_provider——非本批引入；引用指标模块的 test_mine_numerics.py（同会话他车道新文件）在通过之列。

## §7 自审闸三态

- 完成: 算法修面 12/12 列（含防御锁定 1）、写链闸、红绿留痕、真数据验证、同域回归（指标+provider+factor 2103 例绿）。
- 移交: DB 存量 Inf 洗数（依赖修后 full_refresh 或 Owner 门位 delete_where）；candle_pattern/周期覆盖缺口（他车道跟踪中）。
- 未竟: 无（本批范围内）。

## §8 触碰文件清单（worktree，均未 commit）

1. src/zephyr/factor/technical_indicators/volume.py（PVT/PVI/NVI/VR 四处防护 + fill_method）
2. src/zephyr/factor/technical_indicators/momentum.py（ROC/CTI）
3. src/zephyr/factor/technical_indicators/trend.py（TRIX/VORTEX；MCGINLEY 段系同会话他代理既有改动，未触碰）
4. src/zephyr/factor/technical_indicators/statistics.py（CORREL + stderr 附防）
5. src/zephyr/factor/technical_indicators/volatility.py（PercentB/CVI）
6. src/zephyr/data/implementations/internal_compute_provider.py（sanitize_indicator_matrix + _compute_all_indicators 收口 + _build_row 兜底）
7. tests/zephyr/factor/technical_indicators/test_numeric_guards.py（新建，tests/ 项 CREATE-GUARD 豁免）

注: 本 .md 新建之 CREATE-GUARD creation_token 由总包会话提交侧登记（同 census 先例）。
