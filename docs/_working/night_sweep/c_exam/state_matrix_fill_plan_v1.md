---
ttl: task_bound
completes_when: "C5 保守激活三件：填充方案（本件）+TDM 两格禁用标记（mounted 追加，R41 合法）+dry-run 核证；Owner 格零自填（mounted 保持空）"
session: st-nightsweep2-nc-20260930
created: '2026-09-30'
---

# C5 · state_matrix 填充方案 v1（保守激活）+ euphoria/distribution 禁用标记

> **授权链**：Owner 2026-09-30"打通 C 组前置"夜总攻裁定（总筹派发）。
> **边界（先立后行）**：TDM-E-L1 三空格（ignition/euphoria/distribution）=Owner 资金分配门位（R41 封闭词表，
> allocation_rule_v1_draft §8.3"AI 禁自填"）——本方案**不填格**（`mounted` 保持空），只做三件保守面：
> ①候选面填充方案（本件）；②两格 `mounted_reason` 追加禁用标记（R41 首词词表合法，零 schema 变更）；
> ③dry-run 核证上岗规则 v1 的条件共振机械面可运行。
> **上岗规则 v1 主体仍=DRAFT**（`docs/_working/decision_map_campaign/links/L06_exam_alloc/allocation_rule_v1_draft.md`
> §7 P5 Owner 采纳门未过）——本方案不使其生效，不产出 PackageDecision，不接生产编排。

## 1. T1 成绩单候选面（定稿态输入，裁定#436）

数据源=`data/strategy_intake/grid_20260926-024947/manifest.csv`（3700 守恒，3698 有效+2 内生阴性）。
Top-12（按考尺主口径 sharpe 排序；**J-09 纪律：考尺口径相对排名，非绝对收益承诺**）：

| # | recipe_id | sharpe | A1 归一 | A2 合成 | B | C sizing | D1 | E cap | G 宇宙 | J 状态开关 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 36388958b3d8 | 2.139 | industry_neutral | halflife60 | top20 | equal_weight | monthly | cap20 | all_a_ex_st | False |
| 2 | c820ebde36aa | 2.128 | industry_neutral | halflife60 | top20 | equal_weight | biweekly | cap5 | all_a_ex_st | False |
| 3 | a0801d6069fb | 2.094 | rank | halflife20 | top100 | equal_weight | biweekly | cap20 | all_a_ex_st | False |
| 4 | d5fbc7dad201 | 2.020 | industsize_neutral | halflife20 | top50 | signal_strength | biweekly | cap10 | all_a_ex_st | False |
| 5 | e1f0aa9caf8b | 2.014 | industsize_neutral | ic_mean | top50 | signal_strength | monthly | cap10 | all_a_ex_st | False |
| 6 | 656f219773d0 | 1.983 | size_neutral | ic_mean | top50 | signal_strength | monthly | cap10 | all_a_ex_st | False |
| 7 | d21cc1aa8268 | 1.963 | industry_neutral | ic_ir | top10 | signal_strength | daily | cap5 | all_a_ex_st | False |
| 8 | 383c0812a944 | 1.944 | industry_neutral | halflife60 | top100 | risk_parity | monthly | cap20 | all_a_ex_st | False |
| 9 | 6c1a68f28160 | 1.881 | industry_neutral | halflife20 | top20 | signal_strength | weekly | cap10 | all_a_ex_st | False |
| 10 | ef37009da78a | 1.879 | industry_neutral | ic_ir | top100 | inv_vol | daily | cap20 | all_a_ex_st | False |
| 11 | bb7369c6558c | 1.866 | size_neutral | halflife60 | top100 | signal_strength | biweekly | cap20 | all_a_ex_st | False |
| 12 | deaa040fa1b1 | 1.849 | size_neutral | halflife60 | top100 | signal_strength | daily | cap20 | all_a_ex_st | False |

**结构性事实（禁用标记的依据）**：Top-12 全部=**长仓因子轮动配方**（J_regime_switch=False，无对冲/现金/防御档；
G 宇宙全为 all_a_ex_st 多头域）。**PP-001 sleeves 现役 16 员中零防御型 sleeve**（TDM 两格 mounted_reason
在案自述）。⇒ euphoria/distribution 两态对上述全部候选（及在册 16 员中除 daban-sleeve 外全部成员）**禁用**。

## 2. 禁用标记（落 config/trading_decision_map.yaml，不删不改 mounted）

对 TDM-E-L1 的 euphoria/distribution 两格 `mounted_reason` 追加标记段（首词 pending-owner-adoption 保持，
R41 词表合法；零 schema 变更、零格填充、零删除）：

> C5 禁用标记 2026-09-30：T1 定稿 Top-12 候选全为长仓轮动（无防御 sleeve，方案件
> docs/_working/night_sweep/c_exam/state_matrix_fill_plan_v1.md §1-§2），本两态对在册候选全部禁用。

语义：**禁用=当前无合格候选可挂，非永久封禁**——防御型 sleeve 新设后由 Owner 填格解锁（资金分配门位不变）。

## 3. 分态填充建议（供 Owner 采纳时直接取用；采纳前一律保持空格）

| 态 | 现状 | 建议（pending-owner-adoption，AI 不执行） | 依据 |
|---|---|---|---|
| capitulation | STR-VREV-025/027 | 维持；可评估 T1 宇宙内 capitulation 条件分层Top（另卡，需条件轴归因件） | 现格已挂，非本卡范围 |
| accumulation | STR-VREV-026/027 | 维持 | 同上 |
| ignition | 空（pending-owner-adoption） | 候选=Top-12 中 drift_band+monthly/biweekly 低换手组（#1/#2/#5），**前提**：J-04/J-05 统计门+E4 正考 verdict+冷却期全过 | R3 证据共振未验（T2 未跑），禁只凭 T1 排名填格 |
| expansion | STR-MOMTREND-033 | 维持 | 现格已挂 |
| euphoria | 空 | **禁用维持**（无防御 sleeve；daban-sleeve 走 L4 不入 L1） | §1 结构性事实 |
| distribution | 空 | **禁用维持**（预算带 0%=禁新开仓，D98 语义） | 同上 |

## 4. dry-run 核证（2026-09-30 实测，生产码只读零改动）

```
[1] r态→六段折算（真源=framework_composer.py REGIME_STATE_TO_ACTIVATION_PHASE）：
    r1→None r2→None r3→expansion r4→accumulation r10→capitulation r11→accumulation r12→ignition None→None
    ⇒ euphoria/distribution 零 r 态来源=不可达（宁漏勿误 fail-closed，机证）
[2] fw-tdm-current（PP-001 衍生）activation_state 实测：
    声明含 euphoria 的成员=['daban-sleeve']；distribution=[]；activation=null（全段）成员=7
    ⇒ distribution 无任何在册成员声明激活；euphoria 仅打板 sleeve（L4 口径）
[3] TDM 两格实测：mounted=() 且 mounted_reason 首词=pending-owner-adoption（R41 合法在册）
[4] 条件共振判定 dry-run：R1 相位可折算 ∧ R2 两格未填格（pending-owner-adoption=残缺不路由）
    ⇒ euphoria/distribution 恒"保持现状"（机械面可运行且行为正确=上岗规则 v1 §2.1 R2 判据）
```

## 5. 验收判据对照（17号文凡例）

- 本卡验收=C5"上岗规则 v1 保守激活"：方案件✓ + 禁用标记落真源✓（DECISION-MAP gate 同批验）+ dry-run✓。
- **未做（如实）**：Owner 填格（资金门位）、上岗规则 v1 生效裁定（P5）、T2 成绩（R3 证据面）、
  IBT-D01 对照表（P3）——四者全非"我能施工"面，挂等待。
