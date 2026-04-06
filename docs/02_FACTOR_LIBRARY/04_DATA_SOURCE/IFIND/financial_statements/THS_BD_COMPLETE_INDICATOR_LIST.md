---
module_id: DATA_IFIND_INDICATORS_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
responsibility: 同花顺完整指标列表与数据字典
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---


# iFind THS_BD 完整指标清单

## 文档职责说明

**本文档职责**: iFind财务指标清单
- 提供完整的THS_BD函数支持的指标列表
- 分类管理季频和年频指标
- 说明指标含义和用途

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 财务API | [FINANCIAL_STATEMENTS_API.md](./FINANCIAL_STATEMENTS_API.md) | 使用指南 | API调用方法 |
| 财务索引 | [INDEX.md](./INDEX.md) | 上级索引 | 财务数据模块索引 |

**职责边界**:
- ✅ 本文档负责: 指标清单和分类说明
- ❌ 本文档不负责: API调用方法（由 FINANCIAL_STATEMENTS_API.md 负责）

> 本文档包含同花顺iFind THS_BD函数支持的完整指标列表
> 数据来源：因子.txt - THS_BD('920000.BJ', ...) 调用

---

## 指标统计总览

| 类别 | 数量 | 说明 |
|------|------|------|
| **季频指标** | 183 | ths_sq_开头，季度财务报表 |
| **年频指标** | 760 | 非ths_sq_开�?|
| 利润表相�?| 59 | 营收/成本/利润/所得税 |
| 资产负债表相关 | 126 | 资产/负�?所有者权�?|
| 现金流量表相�?| 50 | 经营/投资/筹资现金�?|
| 股东权益相关 | 31 | 股东/股权 |
| 高管信息相关 | 55 | 董监高薪�?持股 |
| 股份变动相关 | 78 | 限售�?质押/浮动 |
| 行业分类相关 | 26 | 申万/证监�?同花顺行�?|
| 上市发行相关 | 21 | IPO/配股/增发 |
| 员工信息相关 | 66 | 员工数量/教育程度 |
| 处罚诉讼相关 | 9 | 违规/诉讼 |
| 其他指标 | 239 | 未分�?|
| **合计** | **943** | |

---

## 一、季频指�?(183�?

> 季度财务报表数据，ths_sq_开�?

| ths_sq_amort_cost_fnncl_ast_income_derec_stock | amort cost fnncl ast income derec | 季频 |
| ths_sq_asset_chg_due_to_remeasure_stock | asset chg due to remeasure | 季频 |
| ths_sq_asset_disposal_income_stock | asset disposal income | 季频 |
| ths_sq_asset_impairment_loss_publish_stock | asset impairment loss publish | 季频 |
| ths_sq_asset_impairment_loss_stock | asset impairment loss | 季频 |
| ths_sq_asset_impairment_reserve_stock | asset impairment reserve | 季频 |
| ths_sq_basic_eps_stock | basic eps | 季频 |
| ths_sq_borrowing_net_increase_amt_stock | borrowing net increase amt | 季频 |
| ths_sq_cannt_reclass_gal_stock | cannt reclass gal | 季频 |
| ths_sq_cannt_reclass_to_gal_stock | cannt reclass to gal | 季频 |
| ths_sq_cash_paid_for_assets_stock | cash paid for assets | 季频 |
| ths_sq_cash_pay_for_goods_etc_stock | cash pay for goods etc | 季频 |
| ths_sq_cash_repay_of_amt_borrowed_stock | cash repay of amt borrowed | 季频 |
| ths_sq_cb_due_within1year_stock | cb due within1year | 季频 |
| ths_sq_cce_net_add_amt_diff_sri_dm_stock | cce net add amt diff sri dm | 季频 |
| ths_sq_cce_net_add_amt_diff_tbi_dm_stock | cce net add amt diff tbi dm | 季频 |
| ths_sq_cf_hedging_gal_valid_part_stock | cf hedging gal valid part | 季频 |
| ths_sq_charge_and_commi_expenses_stock | charge and commi expenses | 季频 |
| ths_sq_commi_on_insurance_policy_stock | commi on insurance policy | 季频 |
| ths_sq_continued_operating_np_stock | continued operating np | 季频 |
| ths_sq_corp_credit_risk_fvc_stock | corp credit risk fvc | 季频 |
| ths_sq_cp_for_indemnity_of_orig_ic_stock | cp for indemnity of orig ic | 季频 |
| ths_sq_cp_for_interests_etc_stock | cp for interests etc | 季频 |
| ths_sq_cp_for_policy_dividends_stock | cp for policy dividends | 季频 |
| ths_sq_cr_from_absorb_invest_stock | cr from absorb invest | 季频 |
| ths_sq_cr_from_bond_issue_stock | cr from bond issue | 季频 |
| ths_sq_cr_from_borrowings_stock | cr from borrowings | 季频 |
| ths_sq_cr_from_disposal_of_invest_stock | cr from disposal of invest | 季频 |
| ths_sq_cr_from_minority_holders_stock | cr from minority holders | 季频 |
| ths_sq_cr_from_return_of_invest_stock | cr from return of invest | 季频 |
| ths_sq_cr_from_sale_of_goods_etc_stock | cr from sale of goods etc | 季频 |
| ths_sq_credit_impairment_loss_publish_stock | credit impairment loss publish | 季频 |
| ths_sq_credit_impairment_loss_stock | credit impairment loss | 季频 |
| ths_sq_dap_paid_to_minority_holder_stock | dap paid to minority holder | 季频 |
| ths_sq_debt_tranfer_to_capital_stock | debt tranfer to capital | 季频 |
| ths_sq_deposit_net_add_etc_stock | deposit net add etc | 季频 |
| ths_sq_deposits_etc_net_add_amt_stock | deposits etc net add amt | 季频 |
| ths_sq_depreciation_stock | depreciation | 季频 |
| ths_sq_disposal_net_add_etc_stock | disposal net add etc | 季频 |
| ths_sq_dit_assets_decrease_stock | dit assets decrease | 季频 |
| ths_sq_dit_liab_increase_stock | dit liab increase | 季频 |
| ths_sq_dividend_etc_cp_stock | dividend etc cp | 季频 |
| ths_sq_dltd_earnings_per_share_stock | dltd earnings per share | 季频 |
| ths_sq_earned_premium_stock | earned premium | 季频 |
| ths_sq_effect_of_erc_on_cce_stock | effect of erc on cce | 季频 |
| ths_sq_ending_balance_of_cash_stock | ending balance of cash | 季频 |
| ths_sq_ending_balance_of_cce_stock | ending balance of cce | 季频 |
| ths_sq_exchange_gain_stock | exchange gain | 季频 |
| ths_sq_extract_ic_reserve_net_amt_stock | extract ic reserve net amt | 季频 |
| ths_sq_fa_cash_in_flow_diff_sri_stock | fa cash in flow diff sri | 季频 |
| ths_sq_fa_cash_in_flow_diff_tbi_stock | fa cash in flow diff tbi | 季频 |
| ths_sq_fa_cash_out_flow_diff_sri_stock | fa cash out flow diff sri | 季频 |
| ths_sq_fa_cash_out_flow_diff_tbi_stock | fa cash out flow diff tbi | 季频 |
| ths_sq_fa_of_finance_lease_stock | fa of finance lease | 季频 |
| ths_sq_fa_reclassi_amt_stock | fa reclassi amt | 季频 |
| ths_sq_fc_convert_diff_stock | fc convert diff | 季频 |
| ths_sq_fc_interest_income_stock | fc interest income | 季频 |
| ths_sq_fee_and_commi_income_stock | fee and commi income | 季频 |
| ths_sq_final_balance_of_cce_stock | final balance of cce | 季频 |
| ths_sq_final_cce_balance_stock | final cce balance | 季频 |
| ths_sq_finance_cost_cfs_stock | finance cost cfs | 季频 |
| ths_sq_finance_cost_stock | finance cost | 季频 |
| ths_sq_fv_change_income_stock | fv change income | 季频 |
| ths_sq_ia_cash_inflow_diff_sri_stock | ia cash inflow diff sri | 季频 |
| ths_sq_ia_cash_inflow_diff_tbi_stock | ia cash inflow diff tbi | 季频 |
| ths_sq_ia_cash_outflow_diff_sri_stock | ia cash outflow diff sri | 季频 |
| ths_sq_ia_cash_outflow_diff_tbi_stock | ia cash outflow diff tbi | 季频 |
| ths_sq_ii_from_jc_etc_stock | ii from jc etc | 季频 |
| ths_sq_income_tax_cost_stock | income tax cost | 季频 |
| ths_sq_increase_of_operating_items_stock | increase of operating items | 季频 |
| ths_sq_initial_balance_of_cash_stock | initial balance of cash | 季频 |
| ths_sq_initial_balance_of_cce_stock | initial balance of cce | 季频 |
| ths_sq_initial_cce_balance_stock | initial cce balance | 季频 |
| ths_sq_intangible_assets_amortized_stock | intangible assets amortized | 季频 |
| ths_sq_interest_and_commi_cr_stock | interest and commi cr | 季频 |
| ths_sq_interest_fee_stock | interest fee | 季频 |
| ths_sq_interest_income_stock | interest income | 季频 |
| ths_sq_interest_payout_stock | interest payout | 季频 |
| ths_sq_inventory_decrease_stock | inventory decrease | 季频 |
| ths_sq_invest_income_stock | invest income | 季频 |
| ths_sq_invest_loss_stock | invest loss | 季频 |
| ths_sq_invest_paid_cash_stock | invest paid cash | 季频 |
| ths_sq_loss_from_fv_change_stock | loss from fv change | 季频 |
| ths_sq_loss_of_disposal_assets_stock | loss of disposal assets | 季频 |
| ths_sq_loss_on_scrapping_of_fa_stock | loss on scrapping of fa | 季频 |
| ths_sq_lt_deferred_cost_amortize_stock | lt deferred cost amortize | 季频 |
| ths_sq_manage_fee_stock | manage fee | 季频 |
| ths_sq_minority_gal_stock | minority gal | 季频 |
| ths_sq_nc_of_branch_etc_stock | nc of branch etc | 季频 |
| ths_sq_nca_dispose_gain_stock | nca dispose gain | 季频 |
| ths_sq_nca_dispose_loss_stock | nca dispose loss | 季频 |
| ths_sq_ncf_diff_from_fa_sri_stock | ncf diff from fa sri | 季频 |
| ths_sq_ncf_diff_from_fa_tbi_stock | ncf diff from fa tbi | 季频 |
| ths_sq_ncf_diff_from_ia_sri_stock | ncf diff from ia sri | 季频 |
| ths_sq_ncf_diff_from_ia_tbi_stock | ncf diff from ia tbi | 季频 |
| ths_sq_ncf_diff_from_oa_by_im_sri_stock | ncf diff from oa by im sri | 季频 |
| ths_sq_ncf_diff_from_oa_by_im_tbi_stock | ncf diff from oa by im tbi | 季频 |
| ths_sq_ncf_diff_of_oa_sri_stock | ncf diff of oa sri | 季频 |
| ths_sq_ncf_diff_of_oa_tbi_stock | ncf diff of oa tbi | 季频 |
| ths_sq_ncf_from_fa_stock | ncf from fa | 季频 |
| ths_sq_ncf_from_ia_stock | ncf from ia | 季频 |
| ths_sq_ncf_from_oa_by_im_stock | ncf from oa by im | 季频 |
| ths_sq_ncf_from_oa_stock | ncf from oa | 季频 |
| ths_sq_net_add_central_bank_stock | net add central bank | 季频 |
| ths_sq_net_add_diff_in_cce_im_tbi_stock | net add diff in cce im tbi | 季频 |
| ths_sq_net_add_finan_org_stock | net add finan org | 季频 |
| ths_sq_net_add_in_deposits_etc_stock | net add in deposits etc | 季频 |
| ths_sq_net_add_in_loans_etc_stock | net add in loans etc | 季频 |
| ths_sq_net_add_in_pledge_loans_stock | net add in pledge loans | 季频 |
| ths_sq_net_add_in_repur_stock | net add in repur | 季频 |
| ths_sq_net_cash_received_from_rein_stock | net cash received from rein | 季频 |
| ths_sq_net_cr_from_disposal_assets_stock | net cr from disposal assets | 季频 |
| ths_sq_net_cr_from_disposal_stock | net cr from disposal | 季频 |
| ths_sq_net_dd_diff_in_cce_im_sri_stock | net dd diff in cce im sri | 季频 |
| ths_sq_net_increase_in_cce_by_im_stock | net increase in cce by im | 季频 |
| ths_sq_net_increase_in_cce_stock | net increase in cce | 季频 |
| ths_sq_net_open_hedge_income_stock | net open hedge income | 季频 |
| ths_sq_non_operating_cost_stock | non operating cost | 季频 |
| ths_sq_non_operating_income_stock | non operating income | 季频 |
| ths_sq_np_atoopc_stock | np atoopc | 季频 |
| ths_sq_np_cfs_stock | np cfs | 季频 |
| ths_sq_np_diff_sri_stock | np diff sri | 季频 |
| ths_sq_np_diff_tbi_stock | np diff tbi | 季频 |
| ths_sq_np_stock | np | 季频 |
| ths_sq_oa_cash_inflow_diff_sri_stock | oa cash inflow diff sri | 季频 |
| ths_sq_oa_cash_inflow_diff_tbi_stock | oa cash inflow diff tbi | 季频 |
| ths_sq_oa_cash_outflow_diff_sri_stock | oa cash outflow diff sri | 季频 |
| ths_sq_oa_cash_outflow_diff_tbi_stock | oa cash outflow diff tbi | 季频 |
| ths_sq_op_diff_sri_stock | op diff sri | 季频 |
| ths_sq_op_diff_tbi_stock | op diff tbi | 季频 |
| ths_sq_op_stock | op | 季频 |
| ths_sq_operate_tax_and_surcharge_stock | operate tax and surcharge | 季频 |
| ths_sq_operating_cost_stock | operating cost | 季频 |
| ths_sq_operating_items_decrease_stock | operating items decrease | 季频 |
| ths_sq_operating_total_cost_2_stock | operating total cost 2 | 季频 |
| ths_sq_operating_total_cost_stock | operating total cost | 季频 |
| ths_sq_operating_total_revenue_stock | operating total revenue | 季频 |
| ths_sq_otc_diff_sri_stock | otc diff sri | 季频 |
| ths_sq_otc_diff_tbi_stock | otc diff tbi | 季频 |
| ths_sq_other_compre_income_atms_stock | other compre income atms | 季频 |
| ths_sq_other_compre_income_atoopc_stock | other compre income atoopc | 季频 |
| ths_sq_other_compre_income_stock | other compre income | 季频 |
| ths_sq_other_cr_related_to_fa_stock | other cr related to fa | 季频 |
| ths_sq_other_cr_related_to_ia_stock | other cr related to ia | 季频 |
| ths_sq_other_cr_related_to_oa_stock | other cr related to oa | 季频 |
| ths_sq_other_debt_right_invest_fvc_stock | other debt right invest fvc | 季频 |
| ths_sq_other_debt_right_invest_ir_stock | other debt right invest ir | 季频 |
| ths_sq_other_equity_invest_fvc_stock | other equity invest fvc | 季频 |
| ths_sq_other_income_stock | other income | 季频 |
| ths_sq_other_not_reclass_to_gal_stock | other not reclass to gal | 季频 |
| ths_sq_othercp_related_to_fa_stock | othercp related to fa | 季频 |
| ths_sq_othercp_related_to_ia_stock | othercp related to ia | 季频 |
| ths_sq_othercp_related_to_oa_stock | othercp related to oa | 季频 |
| ths_sq_others_reclass_to_gal_stock | others reclass to gal | 季频 |
| ths_sq_otr_diff_sri_stock | otr diff sri | 季频 |
| ths_sq_otr_diff_tbi_stock | otr diff tbi | 季频 |
| ths_sq_payments_of_all_taxes_stock | payments of all taxes | 季频 |
| ths_sq_pr_of_orig_ic_old_stock | pr of orig ic old | 季频 |
| ths_sq_rad_cost_sum_stock | rad cost sum | 季频 |
| ths_sq_reclass_and_salable_gal_stock | reclass and salable gal | 季频 |
| ths_sq_reclass_togal_in_equity_law_stock | reclass togal in equity law | 季频 |
| ths_sq_reclass_togal_stock | reclass togal | 季频 |
| ths_sq_refund_of_tax_and_levies_stock | refund of tax and levies | 季频 |
| ths_sq_refunded_premiums_stock | refunded premiums | 季频 |
| ths_sq_rein_expenditure_stock | rein expenditure | 季频 |
| ths_sq_revenue_stock | revenue | 季频 |
| ths_sq_salable_fv_change_gal_stock | salable fv change gal | 季频 |
| ths_sq_sales_fee_stock | sales fee | 季频 |
| ths_sq_si_others_stock | si others | 季频 |
| ths_sq_staff_cp_stock | staff cp | 季频 |
| ths_sq_stop_operating_np_stock | stop operating np | 季频 |
| ths_sq_sub_total_of_ci_from_fa_stock | sub total of ci from fa | 季频 |
| ths_sq_sub_total_of_cis_from_ia_stock | sub total of cis from ia | 季频 |
| ths_sq_sub_total_of_cis_from_oa_stock | sub total of cis from oa | 季频 |
| ths_sq_sub_total_of_co_from_fa_stock | sub total of co from fa | 季频 |
| ths_sq_sub_total_of_cos_from_ia_stock | sub total of cos from ia | 季频 |
| ths_sq_sub_total_of_cos_from_oa_stock | sub total of cos from oa | 季频 |
| ths_sq_total_compre_income_atms_stock | total compre income atms | 季频 |
| ths_sq_total_compre_income_atsopc_stock | total compre income atsopc | 季频 |
| ths_sq_total_compre_income_stock | total compre income | 季频 |
| ths_sq_total_profit_diff_sri_stock | total profit diff sri | 季频 |
| ths_sq_total_profit_diff_tbi_stock | total profit diff tbi | 季频 |
| ths_sq_total_profit_stock | total profit | 季频 |

---

## 二、年频指�?(760�?

### 2.1 利润表相�?(59�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_amortized_cost_fnncl_ass_cfrm_stock | amortized cost fnncl ass cfrm |
| ths_basic_eps_stock | basic eps |
| ths_bs_other_compre_income_stock | bs other compre income |
| ths_charge_and_commi_expenses_stock | charge and commi expenses |
| ths_continued_operating_np_stock | continued operating np |
| ths_deferred_expense_reduce_stock | deferred expense reduce |
| ths_differed_income_current_liab_stock | differed income current liab |
| ths_differed_incomencl_stock | differed incomencl |
| ths_dlt_earnings_per_share_stock | dlt earnings per share |
| ths_domenstic_np_held_ls_stock | domenstic np held ls |
| ths_fc_interest_income_stock | fc interest income |
| ths_fee_and_commi_income_stock | fee and commi income |
| ths_finance_cost_cfs_stock | finance cost cfs |
| ths_finance_cost_interest_fee_stock | finance cost interest fee |
| ths_financing_expenses_stock | financing expenses |
| ths_fv_chg_income_stock | fv chg income |
| ths_income_tax_cost_stock | income tax cost |
| ths_increase_in_accrued_expenses_stock | increase in accrued expenses |
| ths_interest_income_stock | interest income |
| ths_invest_income_cash_received_stock | invest income cash received |
| ths_invest_income_stock | invest income |
| ths_lt_deferred_expense_stock | lt deferred expense |
| ths_lt_deferred_expenses_amrtzt_stock | lt deferred expenses amrtzt |
| ths_net_open_hedge_income_stock | net open hedge income |
| ths_non_operating_income_stock | non operating income |
| ths_nonoperating_cost_stock | nonoperating cost |
| ths_np_atoopc_stock | np atoopc |
| ths_np_cfs_stock | np cfs |
| ths_np_diff_sri_stock | np diff sri |
| ths_np_diff_tbi_stock | np diff tbi |
| ths_np_stock | np |
| ths_operating_cost_2_stock | operating cost 2 |
| ths_operating_cost_diff_sri_stock | operating cost diff sri |
| ths_operating_cost_diff_tbi_stock | operating cost diff tbi |
| ths_operating_cost_stock | operating cost |
| ths_operating_revenuediff_sri_stock | operating revenuediff sri |
| ths_operating_revenuediff_tbi_stock | operating revenuediff tbi |
| ths_operating_taxes_and_surcharge_stock | operating taxes and surcharge |
| ths_operating_total_cost_stock | operating total cost |
| ths_operating_total_revenue_stock | operating total revenue |
| ths_other_income_stock | other income |
| ths_othrcompre_income_atms_stock | othrcompre income atms |
| ths_othrcompre_income_atoopc_stock | othrcompre income atoopc |
| ths_payments_of_all_taxes_stock | payments of all taxes |
| ths_profit_or_lose_stock | profit or lose |
| ths_profit_rfy_stock | profit rfy |
| ths_r3_avg_profit_30_stock | r3 avg profit 30 |
| ths_rad_cost_sum_stock | rad cost sum |
| ths_refund_of_tax_and_levies_stock | refund of tax and levies |
| ths_revenue_stock | revenue |
| ths_stop_operating_np_stock | stop operating np |
| ths_tax_payable_stock | tax payable |
| ths_total_compre_income_atms_stock | total compre income atms |
| ths_total_compre_income_atsopc_stock | total compre income atsopc |
| ths_total_compre_income_stock | total compre income |
| ths_total_profit_diff_sri_stock | total profit diff sri |
| ths_total_profit_diff_tbi_stock | total profit diff tbi |
| ths_total_profit_stock | total profit |
| ths_undstrbtd_profit_stock | undstrbtd profit |

### 2.2 资产负债表相关 (126�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_account_receivable_stock | account receivable |
| ths_accounts_payable_stock | accounts payable |
| ths_actual_received_capital_stock | actual received capital |
| ths_appropriative_reserve_stock | appropriative reserve |
| ths_asset_change_due_to_remeasure_stock | asset change due to remeasure |
| ths_asset_diff_sri_stock | asset diff sri |
| ths_asset_diff_tbi_stock | asset diff tbi |
| ths_asset_disposal_gain_stock | asset disposal gain |
| ths_asset_evaluate_org_stock | asset evaluate org |
| ths_asset_impairment_loss_publish_stock | asset impairment loss publish |
| ths_asset_impairment_loss_stock | asset impairment loss |
| ths_asset_impairment_reserve_stock | asset impairment reserve |
| ths_bill_and_account_payable_stock | bill and account payable |
| ths_bill_and_account_receivable_stock | bill and account receivable |
| ths_bill_payable_stock | bill payable |
| ths_bill_receivable_stock | bill receivable |
| ths_bond_payable_stock | bond payable |
| ths_borrowing_funds_stock | borrowing funds |
| ths_borrowing_net_add_central_bank_stock | borrowing net add central bank |
| ths_borrowing_net_increase_amt_stock | borrowing net increase amt |
| ths_buy_resale_fnncl_assets_stock | buy resale fnncl assets |
| ths_cannt_reclass_gal_equity_law_stock | cannt reclass gal equity law |
| ths_capital_reserve_stock | capital reserve |
| ths_cash_paid_for_assets_stock | cash paid for assets |
| ths_cash_received_of_borrowing_stock | cash received of borrowing |
| ths_charge_and_commi_payable_stock | charge and commi payable |
| ths_contract_asset_stock | contract asset |
| ths_contract_liab_stock | contract liab |
| ths_currency_registered_capital_stock | currency registered capital |
| ths_debt_tranfer_to_capital_stock | debt tranfer to capital |
| ths_derivative_fnncl_assets_stock | derivative fnncl assets |
| ths_derivative_fnncl_liab_stock | derivative fnncl liab |
| ths_dev_expenditure_data_assets_stock | dev expenditure data assets |
| ths_divided_into_asset_for_sale_stock | divided into asset for sale |
| ths_divided_into_liab_for_sale_stock | divided into liab for sale |
| ths_dividend_payable_stock | dividend payable |
| ths_dividend_receivable_stock | dividend receivable |
| ths_dt_assets_decrease_stock | dt assets decrease |
| ths_dt_assets_stock | dt assets |
| ths_dt_liab_increase_stock | dt liab increase |
| ths_dt_liab_stock | dt liab |
| ths_earned_surplus_stock | earned surplus |
| ths_equity_accum_pledge_num_stock | equity accum pledge num |
| ths_equity_pledge_ad_stock | equity pledge ad |
| ths_equity_right_diff_tbi_stock | equity right diff tbi |
| ths_estimated_liab_stock | estimated liab |
| ths_extract_ic_reserve_net_amt_stock | extract ic reserve net amt |
| ths_finance_lease_fixed_assets_stock | finance lease fixed assets |
| ths_fixed_asset_stock | fixed asset |
| ths_fixed_asset_sum_stock | fixed asset sum |
| ths_fixed_assets_disposal_stock | fixed assets disposal |
| ths_fixed_assets_scrap_loss_stock | fixed assets scrap loss |
| ths_flow_assets_diff_sri_stock | flow assets diff sri |
| ths_flow_assets_diff_tbi_stock | flow assets diff tbi |
| ths_fnncl_assets_sold_for_repur_stock | fnncl assets sold for repur |
| ths_holder_equity_diff_sri_stock | holder equity diff sri |
| ths_insurance_contract_reserve_stock | insurance contract reserve |
| ths_intangible_asset_data_assets_stock | intangible asset data assets |
| ths_intangible_assets_amortized_stock | intangible assets amortized |
| ths_intangible_assets_stock | intangible assets |
| ths_interest_payable_stock | interest payable |
| ths_interest_receivable_stock | interest receivable |
| ths_inventory_data_assets_stock | inventory data assets |
| ths_liab_and_equity_diff_sri_stock | liab and equity diff sri |
| ths_liab_and_equity_diff_tbi_stock | liab and equity diff tbi |
| ths_liab_diff_sri_stock | liab diff sri |
| ths_liab_diff_tbi_stock | liab diff tbi |
| ths_loss_of_disposal_assets_stock | loss of disposal assets |
| ths_lt_equity_invest_stock | lt equity invest |
| ths_lt_payable_stock | lt payable |
| ths_lt_payable_sum_stock | lt payable sum |
| ths_lt_receivable_stock | lt receivable |
| ths_lt_staff_salary_payable_stock | lt staff salary payable |
| ths_minority_equity_stock | minority equity |
| ths_naa_of_disposal_fnncl_assets_stock | naa of disposal fnncl assets |
| ths_net_add_in_repur_capital_stock | net add in repur capital |
| ths_net_cash_of_disposal_assets_stock | net cash of disposal assets |
| ths_noncurrent_asset_dispose_gain_stock | noncurrent asset dispose gain |
| ths_noncurrent_asset_dispose_loss_stock | noncurrent asset dispose loss |
| ths_noncurrent_asset_due_within1y_stock | noncurrent asset due within1y |
| ths_noncurrent_assets_diff_sri_stock | noncurrent assets diff sri |
| ths_noncurrent_assets_diff_tbi_stock | noncurrent assets diff tbi |
| ths_noncurrent_liab_diff_sbi_stock | noncurrent liab diff sbi |
| ths_noncurrent_liab_diff_sri_stock | noncurrent liab diff sri |
| ths_noncurrent_liab_due_in1y_stock | noncurrent liab due in1y |
| ths_oil_and_gas_asset_stock | oil and gas asset |
| ths_other_cunrren_assets_stock | other cunrren assets |
| ths_other_current_liab_stock | other current liab |
| ths_other_equity_instruments_stock | other equity instruments |
| ths_other_equity_invest_fvc_stock | other equity invest fvc |
| ths_other_payables_stock | other payables |
| ths_other_payables_sum_stock | other payables sum |
| ths_other_receivables_stock | other receivables |
| ths_other_receivables_sum_stock | other receivables sum |
| ths_othr_noncurrent_assets_stock | othr noncurrent assets |
| ths_othr_noncurrent_liab_stock | othr noncurrent liab |
| ths_payroll_payable_stock | payroll payable |
| ths_perpetual_capital_sec_shares_stock | perpetual capital sec shares |
| ths_perpetual_capital_sec_stock | perpetual capital sec |
| ths_premium_receivable_stock | premium receivable |
| ths_productive_biological_assets_stock | productive biological assets |
| ths_receivable_financing_stock | receivable financing |
| ths_reclass_togal_in_equity_law_stock | reclass togal in equity law |
| ths_reg_capital_stock | reg capital |
| ths_rein_account_receivable_stock | rein account receivable |
| ths_rein_contract_reserve_stock | rein contract reserve |
| ths_rein_payable_stock | rein payable |
| ths_right_of_use_assets_stock | right of use assets |
| ths_saleable_finacial_assets_stock | saleable finacial assets |
| ths_settle_reserves_stock | settle reserves |
| ths_special_payable_stock | special payable |
| ths_st_bond_payable_new_stock | st bond payable new |
| ths_st_borrow_stock | st borrow |
| ths_total_assets_stock | total assets |
| ths_total_current_assets_stock | total current assets |
| ths_total_current_liab_stock | total current liab |
| ths_total_equity_atoopc_diff_spe_stock | total equity atoopc diff spe |
| ths_total_equity_atoopc_diff_sri_stock | total equity atoopc diff sri |
| ths_total_equity_atoopc_stock | total equity atoopc |
| ths_total_liab_and_owner_equity_stock | total liab and owner equity |
| ths_total_liab_stock | total liab |
| ths_total_noncurrent_assets_stock | total noncurrent assets |
| ths_total_noncurrent_liab_stock | total noncurrent liab |
| ths_total_owner_equity_stock | total owner equity |
| ths_tradable_fnncl_assets_stock | tradable fnncl assets |
| ths_tradable_fnncl_liab_stock | tradable fnncl liab |

### 2.3 现金流量表相�?(50�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_cash_of_orig_ic_indemnity_stock | cash of orig ic indemnity |
| ths_cash_paid_for_interests_etc_stock | cash paid for interests etc |
| ths_cash_paid_for_pd_stock | cash paid for pd |
| ths_cash_paid_of_distribution_stock | cash paid of distribution |
| ths_cash_paid_to_staff_etc_stock | cash paid to staff etc |
| ths_cash_pay_for_debt_stock | cash pay for debt |
| ths_cash_received_from_bond_issue_stock | cash received from bond issue |
| ths_cash_received_from_orig_ic_stock | cash received from orig ic |
| ths_cash_received_of_absorb_invest_stock | cash received of absorb invest |
| ths_cash_received_of_dspsl_invest_stock | cash received of dspsl invest |
| ths_cash_received_of_interest_etc_stock | cash received of interest etc |
| ths_cash_received_of_other_fa_stock | cash received of other fa |
| ths_cash_received_of_other_oa_stock | cash received of other oa |
| ths_cash_received_of_othr_fa_stock | cash received of othr fa |
| ths_cash_received_of_sales_service_stock | cash received of sales service |
| ths_cf_hedging_gal_valid_part_stock | cf hedging gal valid part |
| ths_ending_balance_of_cash_stock | ending balance of cash |
| ths_fa_cash_in_flow_diff_sri_stock | fa cash in flow diff sri |
| ths_fa_cash_in_flow_diff_tbi_stock | fa cash in flow diff tbi |
| ths_fa_cash_out_flow_diff_sri_stock | fa cash out flow diff sri |
| ths_fa_cash_out_flow_diff_tbi_stock | fa cash out flow diff tbi |
| ths_goods_buy_and_service_cash_pay_stock | goods buy and service cash pay |
| ths_ia_cash_inflow_diff_sri_stock | ia cash inflow diff sri |
| ths_ia_cash_inflow_diff_tbi_stock | ia cash inflow diff tbi |
| ths_ia_cash_outflow_diff_sri_stock | ia cash outflow diff sri |
| ths_ia_cash_outflow_diff_tbi_stock | ia cash outflow diff tbi |
| ths_initial_balance_of_cash_stock | initial balance of cash |
| ths_invest_paid_cash_stock | invest paid cash |
| ths_ncf_diff_from_fa_sri_stock | ncf diff from fa sri |
| ths_ncf_diff_from_fa_tbi_stock | ncf diff from fa tbi |
| ths_ncf_diff_from_ia_sri_stock | ncf diff from ia sri |
| ths_ncf_diff_from_ia_tbi_stock | ncf diff from ia tbi |
| ths_ncf_diff_from_oa_im_sri_stock | ncf diff from oa im sri |
| ths_ncf_diff_from_oa_im_tbi_stock | ncf diff from oa im tbi |
| ths_ncf_diff_of_oa_sri_stock | ncf diff of oa sri |
| ths_ncf_diff_of_oa_tbi_stock | ncf diff of oa tbi |
| ths_ncf_from_fa_stock | ncf from fa |
| ths_ncf_from_ia_stock | ncf from ia |
| ths_ncf_from_oa_im_stock | ncf from oa im |
| ths_ncf_from_oa_stock | ncf from oa |
| ths_net_cash_amt_from_branch_stock | net cash amt from branch |
| ths_net_cash_of_disposal_branch_stock | net cash of disposal branch |
| ths_net_cash_received_from_rein_stock | net cash received from rein |
| ths_oa_cash_inflow_diff_sri_stock | oa cash inflow diff sri |
| ths_oa_cash_inflow_diff_tbi_stock | oa cash inflow diff tbi |
| ths_oa_cash_outflow_diff_sri_stock | oa cash outflow diff sri |
| ths_oa_cash_outflow_diff_tbi_stock | oa cash outflow diff tbi |
| ths_other_cash_paid_related_to_ia_stock | other cash paid related to ia |
| ths_other_cash_paid_related_to_oa_stock | other cash paid related to oa |
| ths_othrcash_paid_relating_to_fa_stock | othrcash paid relating to fa |

### 2.4 股东权益相关 (31�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_control_holder_name_stock | control holder name |
| ths_controlling_holder_held_ratio_stock | controlling holder held ratio |
| ths_controlling_holder_stock | controlling holder |
| ths_cr_from_minority_holders_stock | cr from minority holders |
| ths_dap_paid_to_minority_holder_stock | dap paid to minority holder |
| ths_float_holder_held_mv_stock | float holder held mv |
| ths_float_holder_held_num_stock | float holder held num |
| ths_float_holder_held_ratio_stock | float holder held ratio |
| ths_float_holder_held_share_nature_stock | float holder held share nature |
| ths_float_holder_name_stock | float holder name |
| ths_holder_freeze_stock | holder freeze |
| ths_holder_freeze_to_held_stock | holder freeze to held |
| ths_holder_held_ls_num_stock | holder held ls num |
| ths_holder_held_num_stock | holder held num |
| ths_holder_held_ratio_stock | holder held ratio |
| ths_holder_held_shares_nature_stock | holder held shares nature |
| ths_holder_name_stock | holder name |
| ths_holder_nature_stock | holder nature |
| ths_ma_holder_increase_held_price_stock | ma holder increase held price |
| ths_ma_holder_pledge_stock | ma holder pledge |
| ths_ma_holder_pledge_to_held_stock | ma holder pledge to held |
| ths_major_holder_accum_pledge_num_stock | major holder accum pledge num |
| ths_major_holder_latest_pledge_num_stock | major holder latest pledge num |
| ths_major_holder_pledge_ad_stock | major holder pledge ad |
| ths_org_holder_name_stock | org holder name |
| ths_org_holder_type_stock | org holder type |
| ths_shareholders_change_enddate_stock | shareholders change enddate |
| ths_shareholders_numbers_byr_stock | shareholders numbers byr |
| ths_shareholders_numbers_enddate_stock | shareholders numbers enddate |
| ths_shareholders_qoq_change_byr_stock | shareholders qoq change byr |
| ths_shareholders_yoy_change_byr_stock | shareholders yoy change byr |

### 2.5 高管信息相关 (55�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_cfo_current_stock | cfo current |
| ths_cfo_held_num_stock | cfo held num |
| ths_cfo_his_stock | cfo his |
| ths_cfo_salary_stock | cfo salary |
| ths_cfo_stock | cfo |
| ths_chairman_current_stock | chairman current |
| ths_chairman_held_num_stock | chairman held num |
| ths_chairman_his_stock | chairman his |
| ths_chairman_of_committee_stock | chairman of committee |
| ths_chairman_salary_stock | chairman salary |
| ths_chairman_stock | chairman |
| ths_chief_supervisor_current_stock | chief supervisor current |
| ths_chief_supervisor_his_stock | chief supervisor his |
| ths_csrc_chairman_salary_stock | csrc chairman salary |
| ths_director_current_stock | director current |
| ths_director_his_stock | director his |
| ths_executive_staff_num_new_stock | executive staff num new |
| ths_executive_staff_ratio_new_stock | executive staff ratio new |
| ths_general_manager_his_stock | general manager his |
| ths_general_manager_salary_stock | general manager salary |
| ths_general_manager_stock | general manager |
| ths_general_managercurrent_stock | general managercurrent |
| ths_independent_director_current_stock | independent director current |
| ths_independent_director_his_stock | independent director his |
| ths_independent_director_salary_stock | independent director salary |
| ths_indp_director_num_stock | indp director num |
| ths_is_not_board_of_supervisors_stock | is not board of supervisors |
| ths_non_indp_director_num_stock | non indp director num |
| ths_secretary_current_stock | secretary current |
| ths_secretary_held_num_stock | secretary held num |
| ths_secretary_his_stock | secretary his |
| ths_secretary_of_bod_stock | secretary of bod |
| ths_secretary_salary_stock | secretary salary |
| ths_sm_annual_total_salary_stock | sm annual total salary |
| ths_sm_edu_current_stock | sm edu current |
| ths_sm_edu_his_stock | sm edu his |
| ths_sm_held_ls_stock | sm held ls |
| ths_sm_name_current_stock | sm name current |
| ths_sm_name_his_stock | sm name his |
| ths_sm_nationality_current_stock | sm nationality current |
| ths_sm_nationality_his_stock | sm nationality his |
| ths_sm_num_stock | sm num |
| ths_sm_sex_current_stock | sm sex current |
| ths_sm_sex_his_stock | sm sex his |
| ths_staff_supervisor_current_stock | staff supervisor current |
| ths_staff_supervisor_his_stock | staff supervisor his |
| ths_supervisor_current_stock | supervisor current |
| ths_supervisor_his_stock | supervisor his |
| ths_supervisory_held_num_stock | supervisory held num |
| ths_total_top3_directors_salary_stock | total top3 directors salary |
| ths_total_top3_sm_salary_stock | total top3 sm salary |
| ths_vice_chairman_current_stock | vice chairman current |
| ths_vice_chairman_his_stock | vice chairman his |
| ths_vice_general_manager_current_stock | vice general manager current |
| ths_vice_general_manager_his_stock | vice general manager his |

### 2.6 股份变动相关 (78�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_accum_pledge_num_ratio_stock | accum pledge num ratio |
| ths_accum_pledge_num_to_held_stock | accum pledge num to held |
| ths_ashare_mm_detail_stock | ashare mm detail |
| ths_ashare_mm_num_stock | ashare mm num |
| ths_ashare_mm_on_debut_stock | ashare mm on debut |
| ths_ashare_mm_sd_stock | ashare mm sd |
| ths_corp_bshare_code_stock | corp bshare code |
| ths_corp_bshare_short_name_stock | corp bshare short name |
| ths_corp_hshare_code_stock | corp hshare code |
| ths_corp_hshare_short_name_stock | corp hshare short name |
| ths_domestic_sponsor_shares_stock | domestic sponsor shares |
| ths_employee_shares_stock | employee shares |
| ths_float_ashare_exright_stock | float ashare exright |
| ths_float_ashare_stock | float ashare |
| ths_float_ashare_to_total_shares_stock | float ashare to total shares |
| ths_float_bshare_stock | float bshare |
| ths_float_bshare_to_total_shares_stock | float bshare to total shares |
| ths_float_neeq_stock | float neeq |
| ths_float_shares_num_fwd_stock | float shares num fwd |
| ths_float_shares_num_int_stock | float shares num int |
| ths_float_shares_type_fwd_stock | float shares type fwd |
| ths_floatedsharesvol_stock | floatedsharesvol |
| ths_floatsharestype_stock | floatsharestype |
| ths_floatsharesvol_stock | floatsharesvol |
| ths_free_float_shares_ratio_stock | free float shares ratio |
| ths_free_float_shares_stock | free float shares |
| ths_fund_place_shares_stock | fund place shares |
| ths_general_legal_person_shares_stock | general legal person shares |
| ths_limited_ashare_ratio_stock | limited ashare ratio |
| ths_limited_ashare_stock | limited ashare |
| ths_limited_bshare_ratio_stock | limited bshare ratio |
| ths_limited_bshare_stock | limited bshare |
| ths_limited_neeq_stock | limited neeq |
| ths_limited_pledge_num_stock | limited pledge num |
| ths_limited_pledge_ratio_stock | limited pledge ratio |
| ths_limited_shares_lifted_date_fwd_stock | limited shares lifted date fwd |
| ths_limited_shares_lifted_date_int_stock | limited shares lifted date int |
| ths_natural_promoter_shares_stock | natural promoter shares |
| ths_neeq_ashare_stock | neeq ashare |
| ths_neeq_ashare_to_total_shares_stock | neeq ashare to total shares |
| ths_neeq_bshare_stock | neeq bshare |
| ths_neeq_bshare_to_total_shares_stock | neeq bshare to total shares |
| ths_neeq_sum_to_total_shares_stock | neeq sum to total shares |
| ths_net_add_in_pledge_loans_stock | net add in pledge loans |
| ths_other_preferred_shares_stock | other preferred shares |
| ths_overseas_listed_shares_ratio_stock | overseas listed shares ratio |
| ths_overseas_listed_shares_stock | overseas listed shares |
| ths_pledge_ratio_stock | pledge ratio |
| ths_ppshare_lifted_date_stock | ppshare lifted date |
| ths_preferred_shares_stock | preferred shares |
| ths_publish_float_num_fwd_stock | publish float num fwd |
| ths_publish_float_num_int_stock | publish float num int |
| ths_raised_legal_person_shares_stock | raised legal person shares |
| ths_shhk_to_float_shares_stock | shhk to float shares |
| ths_state_owned_lp_shares_stock | state owned lp shares |
| ths_state_owned_shares_ratio_stock | state owned shares ratio |
| ths_state_owned_shares_stock | state owned shares |
| ths_top10_float_hlolder_held_num_stock | top10 float hlolder held num |
| ths_top10_float_hlolder_held_ratio_stock | top10 float hlolder held ratio |
| ths_total_ashare_stock | total ashare |
| ths_total_ashare_to_total_shares_stock | total ashare to total shares |
| ths_total_bshare_stock | total bshare |
| ths_total_bshare_to_total_shares_stock | total bshare to total shares |
| ths_total_domestic_lp_shares_stock | total domestic lp shares |
| ths_total_float_shares_ratio_stock | total float shares ratio |
| ths_total_float_shares_stock | total float shares |
| ths_total_limited_shares_ratio_stock | total limited shares ratio |
| ths_total_limited_shares_stock | total limited shares |
| ths_total_pledge_share_num_stock | total pledge share num |
| ths_total_shares_before_listed_stock | total shares before listed |
| ths_total_shares_stock | total shares |
| ths_trust_corp_share_held_num_stock | trust corp share held num |
| ths_trust_corp_share_held_ratio_stock | trust corp share held ratio |
| ths_unfloat_share_pre_reform_ratio_stock | unfloat share pre reform ratio |
| ths_unfloat_shares_before_reform_stock | unfloat shares before reform |
| ths_unfloatsharesvol_stock | unfloatsharesvol |
| ths_unlimited_pledge_num_stock | unlimited pledge num |
| ths_unlimited_pledge_ratio_stock | unlimited pledge ratio |

### 2.7 行业分类相关 (26�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_china_securities_industry_stock | china securities industry |
| ths_cj_industry_index_code_stock | cj industry index code |
| ths_royalflush_industry_index_code_stock | royalflush industry index code |
| ths_sw_industry_index_code_2014_stock | sw industry index code 2014 |
| ths_the_alc_industry_code_stock | the alc industry code |
| ths_the_alc_industry_stock | the alc industry |
| ths_the_citic_industry_code_stock | the citic industry code |
| ths_the_citic_industry_index_code_stock | the citic industry index code |
| ths_the_citic_industry_stock | the citic industry |
| ths_the_csrc_industry_code_stock | the csrc industry code |
| ths_the_csrc_industry_stock | the csrc industry |
| ths_the_hrfg_industry_code_stock | the hrfg industry code |
| ths_the_hrfg_industry_stock | the hrfg industry |
| ths_the_national_eco_industry_code_stock | the national eco industry code |
| ths_the_national_eco_industry_stock | the national eco industry |
| ths_the_new_csrc_industry_code_stock | the new csrc industry code |
| ths_the_new_csrc_industry_stock | the new csrc industry |
| ths_the_sw_industry_2014_stock | the sw industry 2014 |
| ths_the_sw_industry_code_2014_stock | the sw industry code 2014 |
| ths_the_sw_industry_code_stock | the sw industry code |
| ths_the_sw_industry_index_code_stock | the sw industry index code |
| ths_the_sw_industry_stock | the sw industry |
| ths_the_ths_industry_code_stock | the industry code |
| ths_the_ths_industry_stock | the industry |
| ths_yangtze_industry_code_stock | yangtze industry code |
| ths_yangtze_industry_stock | yangtze industry |

### 2.8 上市发行相关 (21�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_backdoor_listing_date_stock | backdoor listing date |
| ths_break_ipo_price_stock | break ipo price |
| ths_corp_issue_sec_list_stock | corp issue sec list |
| ths_delist_date_stock | delist date |
| ths_delisting_strart_date_stock | delisting strart date |
| ths_hk_listed_stock_ratio_stock | hk listed ratio |
| ths_hk_listed_stock_stock | hk listed |
| ths_ipo_date_stock | ipo date |
| ths_ipo_price_stock | ipo price |
| ths_is_issue_cb_stock | is issue cb |
| ths_is_listing_stock | is listing |
| ths_is_restrict_ipo_days_stock | is restrict ipo days |
| ths_issue_system_stock | issue system |
| ths_issuer_corp_nature_stock | issuer corp nature |
| ths_listed_date_stock | listed date |
| ths_listed_days_stock | listed days |
| ths_listed_status_stock | listed status |
| ths_listedsector_stock | listedsector |
| ths_listing_exchange_stock | listing exchange |
| ths_reg_company_ipo_standard_stock | reg company ipo standard |
| ths_unlisted_foreign_stock_stock | unlisted foreign |

### 2.9 员工信息相关 (66�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_admin_num_new_stock | admin num new |
| ths_admin_num_ratio_new_stock | admin num ratio new |
| ths_avg_held_num_growth_6m_stock | avg held num growth 6m |
| ths_avg_held_num_growth_q_stock | avg held num growth q |
| ths_avg_held_num_stock | avg held num |
| ths_bank_held_num_stock | bank held num |
| ths_bod_num_stock | bod num |
| ths_broker_held_num_stock | broker held num |
| ths_business_reg_num_stock | business reg num |
| ths_committee_num_stock | committee num |
| ths_corp_annuity_held_num_stock | corp annuity held num |
| ths_doctor_num_new_stock | doctor num new |
| ths_doctor_num_ratio_new_stock | doctor num ratio new |
| ths_financial_corp_held_num_stock | financial corp held num |
| ths_financial_num_new_stock | financial num new |
| ths_financial_num_ratio_new_stock | financial num ratio new |
| ths_fund_held_num_stock | fund held num |
| ths_fund_manage_corp_held_num_stock | fund manage corp held num |
| ths_general_corp_held_num_stock | general corp held num |
| ths_gm_held_num_stock | gm held num |
| ths_held_num_fund_stock | held num fund |
| ths_held_num_insurance_corp_stock | held num insurance corp |
| ths_held_num_org_stock | held num org |
| ths_held_num_qfii_stock | held num qfii |
| ths_held_num_sif_stock | held num sif |
| ths_high_school_num_new_stock | high school num new |
| ths_highschool_num_ratio_new_stock | highschool num ratio new |
| ths_hr_num_new_stock | hr num new |
| ths_hr_num_ratio_new_stock | hr num ratio new |
| ths_insurance_corp_held_num_stock | insurance corp held num |
| ths_int_illegality_num_stock | int illegality num |
| ths_int_litigation_num_stock | int litigation num |
| ths_junior_college_num_new_stock | junior college num new |
| ths_onboard_staff_num_main_sub_stock | onboard staff num main sub |
| ths_onboard_staff_num_parent_co_stock | onboard staff num parent co |
| ths_other_edu_num_new_stock | other edu num new |
| ths_other_edu_num_ratio_new_stock | other edu num ratio new |
| ths_other_marjor_num_new_stock | other marjor num new |
| ths_other_marjor_num_ratio_new_stock | other marjor num ratio new |
| ths_postgraduate_num_new_stock | postgraduate num new |
| ths_postgraduate_num_ratio_new_stock | postgraduate num ratio new |
| ths_production_num_ratio_new_stock | production num ratio new |
| ths_production_staff_num_new_stock | production staff num new |
| ths_publish_flow_num_the_term_stock | publish flow num the term |
| ths_pur_num_new_stock | pur num new |
| ths_pur_num_ratio_new_stock | pur num ratio new |
| ths_qfii_held_num_stock | qfii held num |
| ths_rc_num_new_stock | rc num new |
| ths_rc_num_ratio_new_stock | rc num ratio new |
| ths_representative_held_num_stock | representative held num |
| ths_salaried_staff_num_stock | salaried staff num |
| ths_sales_num_ratio_new_stock | sales num ratio new |
| ths_sales_staff_num_new_stock | sales staff num new |
| ths_server_num_new_stock | server num new |
| ths_server_num_ratio_new_stock | server num ratio new |
| ths_sif_held_num_stock | sif held num |
| ths_sp_holding_num_stock | sp holding num |
| ths_staff_held_plan_buy_price_stock | staff held plan buy price |
| ths_tech_num_new_stock | tech num new |
| ths_tech_num_ratio_new_stock | tech num ratio new |
| ths_techcore_num_stock | techcore num |
| ths_top10_hlolder_held_num_stock | top10 hlolder held num |
| ths_total_org_held_num_stock | total org held num |
| ths_undergraduate_num_new_stock | undergraduate num new |
| ths_undergraduate_num_ratio_new_stock | undergraduate num ratio new |
| ths_wm_product_held_num_stock | wm product held num |

### 2.10 处罚诉讼相关 (9�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_illegleaction_stock | illegleaction |
| ths_illeglesubject_stock | illeglesubject |
| ths_illeglesubjecttype_stock | illeglesubjecttype |
| ths_illegletype_stock | illegletype |
| ths_int_illegality_amt_stock | int illegality amt |
| ths_int_litigation_amt_stock | int litigation amt |
| ths_litigationinfo_stock | litigationinfo |
| ths_punish_amt_stock | punish amt |
| ths_punishmenttype_stock | punishmenttype |

### 2.11 其他指标 (239�?

| THS代码 | 指标名称 |
|----------|----------|
| ths_act_underwriting_sec_stock | act underwriting sec |
| ths_acting_td_sec_stock | acting td sec |
| ths_actual_controller_held_ratio_stock | actual controller held ratio |
| ths_actual_controller_stock | actual controller |
| ths_actual_controller_type_stock | actual controller type |
| ths_advance_payment_stock | advance payment |
| ths_audit_office_stock | audit office |
| ths_avg_held_ratio_chg_lrr_stock | avg held ratio chg lrr |
| ths_avg_held_ratio_growth_6m_stock | avg held ratio growth 6m |
| ths_avg_held_ratio_growth_q_stock | avg held ratio growth q |
| ths_avg_held_ratio_stock | avg held ratio |
| ths_bank_held_ratio_stock | bank held ratio |
| ths_birth_year_current_stock | birth year current |
| ths_birth_year_his_stock | birth year his |
| ths_broker_held_ratio_stock | broker held ratio |
| ths_cannt_reclass_to_gal_stock | cannt reclass to gal |
| ths_cb_due_within1y_stock | cb due within1y |
| ths_cce_net_add_amt_diff_sri_dm_stock | cce net add amt diff sri dm |
| ths_cce_net_add_amt_diff_tbi_dm_stock | cce net add amt diff tbi dm |
| ths_cce_net_add_diff_im_sri_stock | cce net add diff im sri |
| ths_cce_net_add_diff_im_tbi_stock | cce net add diff im tbi |
| ths_charged_accountant_stock | charged accountant |
| ths_charged_evaluator_stock | charged evaluator |
| ths_charged_lawyer_stock | charged lawyer |
| ths_china_securities_indus_code_stock | china securities indus code |
| ths_commi_on_insurance_policy_stock | commi on insurance policy |
| ths_company_saclle_type_stock | company saclle type |
| ths_comparing_company_stock | comparing company |
| ths_compensate_net_pay_stock | compensate net pay |
| ths_construction_in_process_stock | construction in process |
| ths_construction_in_process_sum_stock | construction in process sum |
| ths_corp_annuity_held_ratio_stock | corp annuity held ratio |
| ths_corp_cb_stock | corp cb |
| ths_corp_cn_name_stock | corp cn name |
| ths_corp_credit_risk_fvc_stock | corp credit risk fvc |
| ths_corp_email_stock | corp email |
| ths_corp_fax_stock | corp fax |
| ths_corp_info_disclosure_news_stock | corp info disclosure news |
| ths_corp_info_disclosure_website_stock | corp info disclosure website |
| ths_corp_name_en_stock | corp name en |
| ths_corp_nature_stock | corp nature |
| ths_corp_profile_stock | corp profile |
| ths_corp_tel_stock | corp tel |
| ths_corp_website_stock | corp website |
| ths_county_level_city_stock | county level city |
| ths_credit_impairment_loss_publish_stock | credit impairment loss publish |
| ths_credit_impairment_loss_stock | credit impairment loss |
| ths_credit_rating_org_stock | credit rating org |
| ths_csrc_district_stock | csrc district |
| ths_currency_fund_stock | currency fund |
| ths_cycle_stock | cycle |
| ths_date_of_cancel_bos_stock | date of cancel bos |
| ths_debt_right_invest_stock | debt right invest |
| ths_deposit_and_interbank_net_add_stock | deposit and interbank net add |
| ths_depository_receipt_ratio_stock | depository receipt ratio |
| ths_depreciation_etc_stock | depreciation etc |
| ths_depreciation_ire_stock | depreciation ire |
| ths_dev_expenditure_stock | dev expenditure |
| ths_disciplinary_measures_stock | disciplinary measures |
| ths_domen_legal_person_held_ls_stock | domen legal person held ls |
| ths_earned_premium_stock | earned premium |
| ths_effect_of_exchange_chg_on_cce_stock | effect of exchange chg on cce |
| ths_ei_strike_price_stock | ei strike price |
| ths_en_short_name_stock | en short name |
| ths_established_date_stock | established date |
| ths_exchange_gain_stock | exchange gain |
| ths_fa_reclassi_amt_stock | fa reclassi amt |
| ths_fc_convert_diff_stock | fc convert diff |
| ths_final_balance_of_cce_stock | final balance of cce |
| ths_financial_corp_held_ratio_stock | financial corp held ratio |
| ths_flow_debt_diff_sri_stock | flow debt diff sri |
| ths_flow_debt_diff_tbi_stock | flow debt diff tbi |
| ths_foreign_legal_person_held_ls_stock | foreign legal person held ls |
| ths_foreign_mp_held_ls_stock | foreign mp held ls |
| ths_frgn_currency_convert_diff_stock | frgn currency convert diff |
| ths_fund_held_ratio_stock | fund held ratio |
| ths_fund_manage_corp_held_ratio_stock | fund manage corp held ratio |
| ths_fund_value_stock | fund value |
| ths_general_corp_held_ratio_stock | general corp held ratio |
| ths_general_risk_provision_stock | general risk provision |
| ths_goodwill_stock | goodwill |
| ths_held_to_maturity_invest_stock | held to maturity invest |
| ths_his_subject_rating_stock | his subject rating |
| ths_hsgt_account_stock | hsgt account |
| ths_hsgt_ratio_stock | hsgt ratio |
| ths_ii_from_jc_etc_stock | ii from jc etc |
| ths_increase_of_operating_item_stock | increase of operating item |
| ths_index_weight_stock | index weight |
| ths_info_banktype_stock | info banktype |
| ths_info_discloser_stock | info discloser |
| ths_initial_balance_of_cce_stock | initial balance of cce |
| ths_initial_cce_balance_stock | initial cce balance |
| ths_insurance_corp_held_ratio_stock | insurance corp held ratio |
| ths_interest_payout_stock | interest payout |
| ths_inventory_decrease_stock | inventory decrease |
| ths_inventory_stock | inventory |
| ths_invest_loss_stock | invest loss |
| ths_invest_property_stock | invest property |
| ths_is_break_bps_stock | is break bps |
| ths_is_break_ip_stock | is break ip |
| ths_is_dividend_below30_exbb_stock | is dividend below30 exbb |
| ths_is_dividend_below30_stock | is dividend below30 |
| ths_is_dividend_r3_exbb_stock | is dividend r3 exbb |
| ths_is_dividend_r3_stock | is dividend r3 |
| ths_is_important_index_constituent_stock | is important index constituent |
| ths_is_mt_ss_underlying_stock | is mt ss underlying |
| ths_is_risk_warning_board_stock | is risk warning board |
| ths_is_sell_restrict_stock | is sell restrict |
| ths_is_shhk_buy_underlying_stock | is shhk buy underlying |
| ths_is_srdi_stock | is srdi |
| ths_is_subnew_stock_stock | is subnew |
| ths_is_szhk_buy_underlying_stock | is szhk buy underlying |
| ths_isin_code_stock | isin code |
| ths_junior_college_ratio_new_stock | junior college ratio new |
| ths_latest_subject_rating_stock | latest subject rating |
| ths_lc_info_disclosure_evaluation_stock | lc info disclosure evaluation |
| ths_lease_libilities_stock | lease libilities |
| ths_legal_counsel_stock | legal counsel |
| ths_legal_representative_stock | legal representative |
| ths_lend_to_other_finins_net_incre_sq_stock | lend to other finins net incre sq |
| ths_lend_to_other_finins_net_incre_stock | lend to other finins net incre |
| ths_lending_fund_stock | lending fund |
| ths_lending_funds_net_increase_sq_stock | lending funds net increase sq |
| ths_lending_funds_net_increase_stock | lending funds net increase |
| ths_lending_net_add_other_org_stock | lending net add other org |
| ths_liftingdate_stock | liftingdate |
| ths_loan_and_advancenet_add_stock | loan and advancenet add |
| ths_loan_from_central_bank_stock | loan from central bank |
| ths_loans_and_payments_stock | loans and payments |
| ths_loss_from_fv_chg_stock | loss from fv chg |
| ths_lt_loan_stock | lt loan |
| ths_main_businuess_stock | main businuess |
| ths_manage_fee_stock | manage fee |
| ths_manage_increase_held_price_stock | manage increase held price |
| ths_minority_gal_stock | minority gal |
| ths_mo_product_name_stock | mo product name |
| ths_mo_product_type_stock | mo product type |
| ths_naa_of_cb_and_interbank_stock | naa of cb and interbank |
| ths_naaassured_saving_and_invest_stock | naaassured saving and invest |
| ths_neeq_sum_stock | neeq sum |
| ths_net_increase_in_cce_im_stock | net increase in cce im |
| ths_net_increase_in_cce_stock | net increase in cce |
| ths_number_of_bos_members_stock | number of bos members |
| ths_office_address_stock | office address |
| ths_op_diff_sri_stock | op diff sri |
| ths_op_diff_tbi_stock | op diff tbi |
| ths_op_stock | op |
| ths_operating_items_decrease_stock | operating items decrease |
| ths_operating_scope_stock | operating scope |
| ths_opponent_company_stock | opponent company |
| ths_org_allot_ls_stock | org allot ls |
| ths_orig_td_vol_stock | orig td vol |
| ths_other_debt_right_invest_fvc_stock | other debt right invest fvc |
| ths_other_debt_right_invest_ir_stock | other debt right invest ir |
| ths_other_debt_right_invest_stock | other debt right invest |
| ths_other_domenstic_invest_held_ls_stock | other domenstic invest held ls |
| ths_other_ei_invest_stock | other ei invest |
| ths_other_not_reclass_to_gal_stock | other not reclass to gal |
| ths_other_reclass_to_gal_stock | other reclass to gal |
| ths_other_uncurrent_fa_stock | other uncurrent fa |
| ths_p20_lowest_close_price_baf_stock | p20 lowest close price baf |
| ths_p20_lowest_pb_cp_stock | p20 lowest pb cp |
| ths_p20_lowest_pb_cy_stock | p20 lowest pb cy |
| ths_periodic_report_fore_dd_stock | periodic report fore dd |
| ths_phonetic_short_name_stock | phonetic short name |
| ths_pp_price_stock | pp price |
| ths_prefecture_level_city_stock | prefecture level city |
| ths_preferred_stock | preferred |
| ths_prepays_stock | prepays |
| ths_processing_unit_stock | processing unit |
| ths_project_goods_and_material_stock | project goods and material |
| ths_province_stock | province |
| ths_qfii_held_ratio_stock | qfii held ratio |
| ths_r3_accum_dividend_amt_exbb_stock | r3 accum dividend amt exbb |
| ths_r3_accum_dividend_amt_stock | r3 accum dividend amt |
| ths_reclass_and_salable_gal_stock | reclass and salable gal |
| ths_reclass_to_gal_stock | reclass to gal |
| ths_redemp_td_vol_stock | redemp td vol |
| ths_refunded_premium_stock | refunded premium |
| ths_reg_address_stock | reg address |
| ths_regular_report_actual_dd_stock | regular report actual dd |
| ths_regular_report_latest_rp_stock | regular report latest rp |
| ths_regulatory_evaluation_c_stock | regulatory evaluation c |
| ths_rein_expenditure_stock | rein expenditure |
| ths_rou_depreciation_stock | rou depreciation |
| ths_saleable_fv_chg_gal_stock | saleable fv chg gal |
| ths_sales_fee_stock | sales fee |
| ths_saving_and_interbank_deposit_stock | saving and interbank deposit |
| ths_sec_name_used_before_stock | sec name used before |
| ths_sec_representative_current_stock | sec representative current |
| ths_sec_representative_his_stock | sec representative his |
| ths_sec_representative_salary_stock | sec representative salary |
| ths_securities_affairs_representative_stock | securities affairs representative |
| ths_sedol_stock | sedol |
| ths_si_final_balance_of_cce_stock | si final balance of cce |
| ths_si_other_stock | si other |
| ths_sif_held_ratio_stock | sif held ratio |
| ths_soap_held_ls_stock | soap held ls |
| ths_sp_holding_ratio_stock | sp holding ratio |
| ths_special_treatment_time_stock | special treatment time |
| ths_state_held_ls_stock | state held ls |
| ths_statement_format_stock | statement format |
| ths_stock_code_stock | stock code |
| ths_stock_short_name_quote_client_stock | stock short name quote client |
| ths_stock_short_name_stock | stock short name |
| ths_stock_varieties_stock | stock varieties |
| ths_strategic_investors_held_stock | strategic investors held |
| ths_strategy_emerg_ind_clas_code_stock | strategy emerg ind clas code |
| ths_strategy_emerg_ind_clas_stock | strategy emerg ind clas |
| ths_sub_total_of_ci_from_fa_stock | sub total of ci from fa |
| ths_sub_total_of_ci_from_ia_stock | sub total of ci from ia |
| ths_sub_total_of_ci_from_oa_stock | sub total of ci from oa |
| ths_sub_total_of_cos_from_fa_stock | sub total of cos from fa |
| ths_sub_total_of_cos_from_ia_stock | sub total of cos from ia |
| ths_sub_total_of_cos_from_oa_stock | sub total of cos from oa |
| ths_the_amac_code_stock | the amac code |
| ths_the_amac_index_stock | the amac index |
| ths_the_concept_stock | the concept |
| ths_the_high_tech_park_stock | the high tech park |
| ths_the_ths_concept_index_code_stock | the concept index code |
| ths_the_ths_concept_index_stock | the concept index |
| ths_thscode_stock | thscode |
| ths_to_repurchase_margin_stock | to repurchase margin |
| ths_top10_fund_holded_name_stock | top10 fund holded name |
| ths_top10_hlolder_held_ratio_stock | top10 hlolder held ratio |
| ths_total_invest_held_ls_stock | total invest held ls |
| ths_total_org_held_ratio_stock | total org held ratio |
| ths_trade_currency_stock | trade currency |
| ths_treasury_stock_stock | treasury |
| ths_turn_allot_stock | turn allot |
| ths_unified_social_credit_code_stock | unified social credit code |
| ths_upcom_periodic_report_fore_dd_stock | upcom periodic report fore dd |
| ths_us_stock_code_stock | us code |
| ths_us_ticker_stock | us ticker |
| ths_wm_product_held_ratio_stock | wm product held ratio |
| ths_ygzs_new_stock | ygzs new |
| ths_zip_code_stock | zip code |
| unconfirmed_invest_loss_bs | unconfirmed invest loss bs |
| unconfirmed_invest_loss_is | unconfirmed invest loss is |

---

> **数据来源**: 同花顺iFind THS_BD函数
> **更新时间**: 2026-03-28
> **总指标数**: 943个（季频183 + 年频760�?

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
