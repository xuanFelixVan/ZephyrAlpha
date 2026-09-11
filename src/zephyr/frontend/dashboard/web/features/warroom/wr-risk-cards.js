/* 功能模块：作战室风险卡族（wr-risk-cards）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 FEED 表（相关净值/持仓状态/T1/节流/W5 日历/压力）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3452-3587），逻辑零改动。
 * 验收单：ACC-F-WR-RISK-CARDS
 */
var T0_FEED={
  symbol:'600519.SH', recommendation:'hold', recommendation_zh:'持有', overall_confidence:0, is_degraded:false,
  all_confirmations_passed:true,
  confirmations:[
    {confirmation_type:'大盘环境确认', passed:true, actual_value:58, threshold:40},
    {confirmation_type:'板块强度确认', passed:true, actual_value:72, threshold:60},
    {confirmation_type:'资金流向确认', passed:true, actual_value:320, threshold:0}],
  /* signals=图表标注适配（i=分时索引 0~240）；逻辑/置信度与下方回验表逐条一致 */
  signals:[
    {i:42, time:'10:12', direction:'buy', point_type:'回调买点', confidence:76, reference_price:1701.2, reason:'回踩均价不破+缩量止跌'},
    {i:95, time:'11:05', direction:'sell', point_type:'趋势破位止盈', confidence:71, reference_price:1718.6, reason:'冲高远离均价 1.3%+量价背离'},
    {i:145, time:'13:24', direction:'buy', point_type:'回调买点', confidence:68, reference_price:1710.3, reason:'二次回踩均价确认'},
    {i:199, time:'14:18', direction:'sell', point_type:'目标价位止盈', confidence:73, reference_price:1722.4, reason:'尾盘冲高乏力'}]
};
/* BFE-28：query_t1_sellable → position t1_sellable_weights（昨仓−今日已卖，32号§6 口径） */
var T1_FEED={
  rows:[
    {symbol:'600519.SH', last_weight:0.133, sold_today_weight:0.0, sellable_weight:0.133, sellable_shares:100},
    {symbol:'300750.SZ', last_weight:0.055, sold_today_weight:0.028, sellable_weight:0.027, sellable_shares:200},
    {symbol:'688981.SH', last_weight:0.072, sold_today_weight:0.0, sellable_weight:0.072, sellable_shares:1000}],
  position_count:3, total_sellable_weight:0.232
};
/* GAP-F-04：query_correlation_netting → 组合域相关性约束口径（MOD-PF-006 C5 阈值族，夜班 #205/#207） */
var CORR_FEED={
  threshold:0.7, as_of:'2026-08-21', gross_position_count:4, net_risk_units:3, netting_reduction:1,
  clusters:[{members:['688981.SH 中芯国际','603986.SH 兆易创新'], max_pair_rho:0.82, combined_weight:0.122}],
  singletons:['600519.SH 贵州茅台','300750.SZ 宁德时代']
};
/* BFE-25：query_position_state_snapshot → PositionStateMachine（MOD-POS-002） */
var PSTATE_FEED={
  rows:[
    {symbol:'600519.SH', state:'ACTIVE', state_zh:'持仓中', can_buy:true, can_rebuild:false, is_observing:false, is_in_cooldown:false, graduation_weight:1.0},
    {symbol:'300750.SZ', state:'OBSERVING', state_zh:'观察期', can_buy:false, can_rebuild:false, is_observing:true, observing_reason:'SOFT_STOP', is_in_cooldown:false, graduation_weight:1.0},
    {symbol:'688981.SH', state:'ACTIVE', state_zh:'持仓中', can_buy:true, can_rebuild:false, is_observing:false, is_in_cooldown:false, graduation_weight:1.0}],
  position_count:3, observing_count:1, cooldown_count:0
};
/* BFE-26：query_drawdown_throttle → DrawdownController（MOD-POS-008，系统性风险 5 级+策略止损+黑天鹅取最严） */
var THROTTLE_FEED={
  risk_level:'GREEN', position_cap:1.0, reduce_ratio:0.0, throttle_gear:'full', throttle_gear_zh:'油门全开',
  actions:['无减仓动作'], strategy_stops:[], kill_switch_advised:false, recovery_factor:1.0
};
/* BFE-27：query_calendar_position_constraints → CalendarPositionConstraint（MOD-POS-017，7 类日历事件） */
var CAL_FEED={
  check_date:'2026-08-25', overall_cap_adjustment:0.9, block_new_positions:false,
  block_new_symbols:[], force_clear_symbols:[],
  constraints:[{rule:'option_expiry_window', event_type:'OPTION_EXPIRY', action:'REDUCE_CAP', cap_adjustment:0.9,
    description:'股指期权交割日（每月第四个周三）前后窗口：仓位上限 ×0.9', affected_symbols:'ALL'}],
  constraint_count:1
};
/* BFE-30：query_liquidity_status → LiquidityMonitor（MOD-RK-048，Amihud+成交量萎缩） */
var LIQ_FEED={
  rows:[
    {symbol:'600519.SH', amihud_illiq:2.1e-9, volume_shrinkage_ratio:1.05, is_illiquid:false},
    {symbol:'300750.SZ', amihud_illiq:3.4e-9, volume_shrinkage_ratio:0.88, is_illiquid:false},
    {symbol:'688981.SH', amihud_illiq:4.2e-9, volume_shrinkage_ratio:0.42, is_illiquid:true}],
  illiquid_symbols:['688981.SH'], conclusion_zh:'监控 3 票：1 票流动性恶化（688981.SH 中芯国际，量能萎缩 0.42）'
};
/* BFE-31：query_tail_risk_status → TailRiskMonitor（MOD-RK-15，VaR/ES/POT/跳跃/FRTB） */
var TAIL_FEED={
  var:0.018, expected_shortfall:0.024, es_var_ratio:1.33, jump_count:2,
  alert_level:'none', reason:'', frtb_addon:0.0, pot_shape:0.08, pot_tail_index:12.5, pot_fallback_historical:false
};
/* BFE-32：query_stress_test_summary → StressTestEngine.run_all_historical（MOD-RK-12，2008/2015/2020 三情景） */
var STRESS_FEED={
  scenarios:[
    {scenario:'2008_financial_crisis', description:'2008 全球金融危机', portfolio_loss_pct:-0.0768, portfolio_loss_value:-98684, var_exceeded:true, is_severe:true},
    {scenario:'2015_china_stock_crash', description:'2015 A股股灾', portfolio_loss_pct:-0.0905, portfolio_loss_value:-116270, var_exceeded:true, is_severe:true},
    {scenario:'2020_covid_crash', description:'2020 新冠疫情冲击', portfolio_loss_pct:-0.0598, portfolio_loss_value:-76815, var_exceeded:true, is_severe:true}],
  worst_scenario:{scenario:'2015_china_stock_crash', description:'2015 A股股灾', portfolio_loss_pct:-0.0905, portfolio_loss_value:-116270, var_exceeded:true, is_severe:true},
  severe_count:3, conclusion_zh:'三套历史情景最大单日压力损失 -9.05%（2015 A股股灾），严重情景 3/3 套'
};

/* GAP-F-04 持仓监控页：相关性净额卡 */
function renderCorrNetting(){
  var box=document.getElementById('corr-netting-body'); if(!box)return;
  var f=CORR_FEED, html='';
  html+='<tr><td>持仓敞口（毛）</td><td>'+f.gross_position_count+' 票</td><td>聚合阈值 |ρ|≥'+f.threshold+'</td></tr>';
  html+='<tr><td>净风险单位</td><td><b>'+f.net_risk_units+' 笔</b>（净额扣减 '+f.netting_reduction+'）</td><td>高相关合并计 1 笔风险</td></tr>';
  f.clusters.forEach(function(c){
    html+='<tr><td>高相关簇</td><td colspan="2">'+c.members.join(' + ')+' <span class="up">ρ='+c.max_pair_rho+'</span> → 合并计 1 笔（合计权重 '+(c.combined_weight*100).toFixed(1)+'%）</td></tr>';
  });
  html+='<tr><td>独立敞口</td><td colspan="2" class="dim">'+f.singletons.join('、')+'</td></tr>';
  box.innerHTML=html;
}
/* 持仓监控页：BFE-25 状态列（状态机快照注入持仓明细行） */
function renderPositionStates(){
  PSTATE_FEED.rows.forEach(function(r){
    var td=document.getElementById('pstate-'+r.symbol.split('.')[0]); if(!td)return;
    var badge=r.is_observing?'b-warn':(r.is_in_cooldown?'b-na':'b-pass');
    var extra=r.is_observing?'（禁新买'+(r.observing_reason==='SOFT_STOP'?'·软止损':'')+'）':(r.is_in_cooldown?'（冷却期禁重建）':'');
    td.innerHTML='<span class="badge '+badge+'">'+r.state_zh+'</span>'+extra;
  });
}
/* T分析页：BFE-28 底仓卡（T+1 可卖额度接线） */
function renderT1Card(){
  var box=document.getElementById('t1-sellable-card'); if(!box)return;
  var main=T1_FEED.rows[0];
  box.innerHTML='<div class="l">T+0 可用底仓</div><div class="v">'+main.sellable_shares+' 股</div>'
    +'<div class="s">'+main.symbol.split('.')[0]+' 昨仓可卖（T+1 口径：昨仓−今日已卖）</div>';
}
/* 盘中实时风控区：BFE-26/30/31 各加一行（不独立成卡，Owner 边界项③裁定） */
function renderRiskExtraRows(){
  var tb=document.getElementById('risk-hard-table'); if(!tb)return;
  var gearBadge=THROTTLE_FEED.throttle_gear==='full'?'b-pass':(THROTTLE_FEED.throttle_gear==='stop'?'b-bad':'b-warn');
  tb.insertAdjacentHTML('beforeend',
    '<tr><td>回撤油门刹车</td><td><span class="badge '+gearBadge+'">'+THROTTLE_FEED.throttle_gear_zh+'</span> '+THROTTLE_FEED.risk_level+' · 仓位上限 ×'+THROTTLE_FEED.position_cap.toFixed(2)+'</td></tr>'
    +'<tr><td>流动性监控</td><td>'+(LIQ_FEED.illiquid_symbols.length?'<span class="badge b-warn">'+LIQ_FEED.illiquid_symbols.length+' 票恶化</span> '+LIQ_FEED.illiquid_symbols.join('、'):'<span class="badge b-pass">正常</span>')+'</td></tr>'
    +'<tr><td>尾部风险</td><td>'+(TAIL_FEED.alert_level==='none'?'<span class="badge b-pass">正常</span>':'<span class="badge b-warn">'+TAIL_FEED.alert_level+'</span>')+' ES '+(TAIL_FEED.expected_shortfall*100).toFixed(1)+'% · 跳跃 '+TAIL_FEED.jump_count+' 次</td></tr>');
}
/* 作战室 W5：BFE-27 日历仓位约束行 */
function renderW5Calendar(){
  var tb=document.getElementById('w5-budget-table'); if(!tb)return;
  var f=CAL_FEED, row='';
  if(f.constraint_count){
    row='<tr><td>日历仓位约束</td><td>'+f.constraints.map(function(c){
      return c.description+'（上限 ×'+c.cap_adjustment+'）';
    }).join('；')+(f.block_new_positions?' · <b>今日禁开新仓</b>':'')+'</td></tr>';
  }else{
    row='<tr><td>日历仓位约束</td><td><span class="badge b-pass">无生效约束</span>（7 类日历事件每日检查）</td></tr>';
  }
  tb.insertAdjacentHTML('beforeend',row);
}
/* 盘后复盘页：BFE-32 压力测试盘后风险验证卡（结论级） */
function renderStressCard(){
  var box=document.getElementById('stress-test-body'); if(!box)return;
  var f=STRESS_FEED, html='';
  f.scenarios.forEach(function(s){
    html+='<tr><td>'+s.description+'</td><td class="down">'+(s.portfolio_loss_pct*100).toFixed(2)+'%</td>'
      +'<td class="down">'+Math.round(s.portfolio_loss_value).toLocaleString()+'</td>'
      +'<td>'+(s.is_severe?'<span class="badge b-bad">严重</span>':'<span class="badge b-warn">承压</span>')+'</td></tr>';
  });
  html+='<tr><td><b>最坏情景</b></td><td class="down"><b>'+(f.worst_scenario.portfolio_loss_pct*100).toFixed(2)+'%</b></td><td colspan="2" class="dim">'+f.conclusion_zh+'</td></tr>';
  box.innerHTML=html;
}
renderCorrNetting(); renderPositionStates(); renderT1Card(); renderRiskExtraRows(); renderW5Calendar(); renderStressCard();
renderOverseas(); renderT0(); renderSectorContrib(); usycRender();
