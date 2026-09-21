---
ttl: task_bound
completes_when: Owner 六项全部点单后转 archived
---

# TC-10 报到清单（步骤0 产出，呈 Owner 置顶；2026-09-21）

> 六项后续触发状态（tc_10 卡）；「待令」是合法稳态不是欠账。每项触发条件见卡第 4 节。

| # | 事项 | 状态 | 触发条件 |
|---|---|---|---|
| 步骤1 | 批 10 扩项挂接（cost_15/85+CHIP_CONC_90/70 → WO-4+台账 C3） | **已做**（2f247ea6df，甲线 W4 已开工=d4e89225bf 在跑） | —（时限件已闭） |
| 步骤2 | P1 期权 PCR 数据批（akshare option_daily_stats 三口径 PCR） | 待 Owner 点单 | Owner 点单 P1 |
| 步骤3 | 批 10 本体施工 | **甲线 W4 在跑**（主权在 unified，勿双开） | — |
| 步骤4 | P2 三小活：①trade_when 白名单 ②E4 拥挤度 ③组合层立项 | ③前置已解除（裁定#392（D-10） 批准解除 pf_alloc 挂触发）①②待点单 | Owner 点单 P2（③可立即开） |
| 步骤5 | 密钥轮换后核对（AI 只报键名/格式绝不打印值） | **催办 Owner**：.env 曝光（09-18 实证）后超 3 天未轮换；必换=OKX（只读+IP 白名单+禁提币）/iFind/百度网盘 token；建议换=付费 LLM key+TUSHARE_TOKEN（裁定#392 同口径） | Owner 轮换后主动叫核对 |
| 步骤6 | 月度巡检自动化（du .zcode+repoSnapshot 键巡检） | 待 Owner 点单 | Owner 点头挂自动化（可搭 IOCheck-Monthly 车辆） |

## 另呈 Owner 手办置顶（四件）

1. **D-8 五棚删除命令**：docs/_working/recovered_task_cards/d8_worktree_removal_order.md
   （五包已归档 G:\zephyr_cold\...\worktree_remnants_20260921\+SHA256，命令在手照跑即清）。
2. **废表 13 张逐表批**：waste_table_report_list.md（乙线已备，逐表批制裁定#382 口径）。
3. **vhdx 压缩点名单**（排期表族，#381④ 点名项）。
4. **TC-06 四张裁定卡点单**：docs/_working/recovered_task_cards/tc06_ruling_cards/
   （R1 已结案无须点；R2 E1C-09 三选项/R3 TradeRecord/R4 做T 各待单）。
