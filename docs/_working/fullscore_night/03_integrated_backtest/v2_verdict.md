---
ttl: task_bound
campaign: fullscore_night/03_integrated_backtest
exam: IBT-v2 HOLDOUT 二次复考（此卷最后一考）
created: '2026-10-01'
session: st-fullscore-20260930
prereg: prereg_v2.md（LOCKED 2026-10-01 10:2x，附录 A sha256=38ee5ada3834e99279f76eb2ec2c455aa28af94ca611b0fb84668ccdbafd47cd）
verdict: FAIL
---

# IBT-v2 裁决书（HOLDOUT 已烧毁，FAIL 如实落档，禁改参重跑）

> 判据唯一真源=prereg_v2.md §2（跑前锁定）。本裁决零参数变更、零重跑；
> W_HOLDOUT 一次性 `--holdout-guard` 已消耗（§3 烧毁证书）。

## §1 四窗总表（IBT-A 静态等权，成本=决定档 CalibratedSlippage 逐笔标定）

| 窗 | 窗口 | 净夏普 | 年化换手 | 最大回撤 | 收益 | 成交笔数 | 参与成员 |
|----|------|--------|----------|----------|------|----------|----------|
| W_IS | 2019-04-01..2023-12-31 | **-0.308** | 21.04x | 26.57% | -12.75% | 31,601 | 14/14 |
| W_OOS | 2024-01-01..2025-09-08 | **+0.457** | 22.75x | 19.31% | +17.34% | 13,134 | 14/14 |
| **W_HOLDOUT** | 2025-09-09..2026-09-08 | **-0.938** | **20.85x** | **14.10%** | -8.33% | 5,897 | 14/14 |
| W_POSTD（披露窗） | 2026-09-09..2026-09-18 | 0.0（披露） | —（8 日窗不年化） | 2.21% | -0.55% | 133 | 14 组合参与；成员单跑 3 员窗内零信号短路 |

换手口径=双边成交额合计÷2÷窗口平均净值，按 244 交易日/年年化（prereg §2.1 冻结定义，从 trades_IBT-A.csv/nav_IBT-A.csv 精算）。
敏感性（W_OOS）：slip 0/5/10/20/40bp → Sharpe 0.537/0.417/0.297/-0.014/-0.489，零成本 0.827——单调衰减，成本主导成立。

### v1 对照（漂移披露，不进判据——prereg §2.3）

| 窗 | v1 净夏普（LegacyFlat 面） | v2 净夏普（标定面） | v1 成员数 | 备注 |
|----|---------------------------|---------------------|-----------|------|
| W_IS | -0.286 | -0.308 | 15 | 池换血 15→14+成本口径换代，IS 同向更负 |
| W_OOS | +0.336 | +0.457 | 15 | v2 池 OOS 更优 |
| W_HOLDOUT | -1.389 | -0.938 | 15 | 两代池 HOLDOUT 皆深负（±结构行情段） |
| W_POSTD | 0.0 | 0.0 | 15 | — |

v1 数字不可由 HEAD 复现（R-022 实证：legacy 1bp 重放亦 61 处漂移；根因=成本标定落地+数据面演进，
详见 prereg 附录 B-3）——v1 列仅作漂移披露。

## §2 完整性门（先判）:PASS（附一项审计观察披露）

- 四窗产物齐：各窗 run_summary.yaml + nav_IBT-A.csv + trades_IBT-A.csv + composed_panel.pkl 在盘
  （artifacts_v2/），成员=14、skipped=[]、alpha_total=0.999999994（等权归一）；W_OOS 为 v2 覆写后新产物
  （成员名单无 4440d07f973f，与被覆盖的 v1 池重放残留机械可分）。
- ibt_redblue 抽查 W_OOS（round1，产物流 artifacts_v2/W_OOS/redblue_round1.yaml）：
  - 全部前视不变量 PASS：engine_lag0_raise（引擎拒绝 T+0）、fill_audit_no_same_day（13,134 fills/0 违例）、
    same_bar_disabled、pit/regime_schedule_keys（1,565 键全部=快照日+1）、pit/delisted_injection（退市股剔除实证）、
    cost/slippage_monotonic、zero_cost_dominates。
  - **披露（唯一 RED，非本跑污染）**：shift_injection_material ΔSharpe=+0.012 < 0.05 判红线——
    该项=金丝雀（阳性对照，验证审计器能侦测前视注入），非前视证据；v2 池面板稀疏（低换手/1 列指数腿成员多），
    1 日信号平移对本池组合 Sharpe 影响量级天然小于 v1 稠密池（v1 同项 Δ=+0.072 判绿）。
    直接前视不变量全部 PASS，判完整性门 PASS；Owner 如按最严字面（"无红旗"含金丝雀）翻此判定，
    结论仍为 FAIL 不变（HOLDOUT 已烧，无重考）。

## §3 W_HOLDOUT 烧毁证书

- 时序：锁箱（prereg 附录 A 填写=2026-10-01 10:2x）→ W_IS（11:02 IBT-A 落）→ W_OOS+sensitivity（11:40 落）
  → 三窗完整性核对 PASS → **W_HOLDOUT 单次发车（--holdout-guard，11:48:57 IBT-A 落，11:51:52 run_summary 落盘）**
  → W_POSTD（11:52 披露窗）。此前 HOLDOUT 零消耗（v1 产物为协议 v1 历史，未被触碰）。
- 参数：--variants A --pool-file fresh_pool_v2.yaml（sha256=38ee5ada...）--holdout-guard；零窗口参数变更、零重跑；
  引擎全确定性（A/B 双跑实证 core+members 逐位相等，见 prereg 附录 B-3）。
- **此卷最后一考已执行完毕：W_HOLDOUT 保密性已终止，不得再以任何口径复考。**

## §4 主判裁决：FAIL

| 判据（prereg §2.1） | 线 | 实测 | 判 |
|---------------------|-----|------|-----|
| HOLDOUT 净夏普 | ≥ 0.5 | **-0.938** | **FAIL** |
| HOLDOUT 年化换手 | ≤ 10x | **20.85x** | **FAIL** |
| HOLDOUT 最大回撤 | ≤ 20% | 14.10% | PASS |

三条须同时过：**IBT-v2 裁决=FAIL。** 全流程零参数变更、零重跑、基础设施零崩（无 errata）。

## §5 池级归因（披露，非判据）

HOLDOUT 段 14 员中 13 员净夏普为负：拖累最深=CAND-8664521af1a0（-1.963，dd 45.5%）、
CAND-dc5b80aa3614（-1.045，dd 34.1%）——恰为 OOS 段最强两员（0.989/1.375），OOS→HOLDOUT 正
夏普不可延续；唯一正员=CAND-e3da6fa71af1（+0.218，低换手危机闪避）。IS 段全池负（-0.308）与
OOS 段正（+0.457）并存，说明选择窗（批 D 新鲜窗=2024-01..2026-09）与 HOLDOUT 段（2025-09 起）
重叠度高（blocked_v2_pool_missing.md §5 路径乙预警的"选择窗与考窗同段"问题实际发生）——
池选择已部分消费 HOLDOUT 段信息，本 FAIL 与该结构性混杂一致，交 Owner 连同批 D 收口一并裁定。

## §6 落地与 defer 状态

- 本裁决书+fresh_pool_v2.yaml+notes+BLOCKED 报告：capability 册 token×4 已登记册面（主树+worktree），
  册 claim 在 st-menu-w3h-20260930（活会话）→ 按 deferred_claims.md 2026-10-01 IBT-v2 条目 defer，
  册落地后随批二收口。预检仿真面（HEAD+袋）需 token 先落 HEAD，故本夜 git 落地仅能伴随 w3h 批次收口。
- 四窗产物目录：docs/_working/integrated_backtest/artifacts_v2/{W_IS,W_OOS,W_HOLDOUT,W_POSTD}/
  + _regression/（重定向 A/B 实证物）。v1 artifacts/ 只读未触碰。
