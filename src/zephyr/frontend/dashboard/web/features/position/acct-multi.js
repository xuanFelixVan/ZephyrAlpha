/* 功能模块：多账号持仓视图（acct-multi）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 ACCOUNT_D
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4909-5044），逻辑零改动。
 * 验收单：ACC-F-POS-ACCT-MULTI
 */
/* ==================== I-7 position-multi：多账号持仓视图（acctXxx / pnlCalXxx） ==================== */
var ACCOUNT_D={
  real:{name:'实盘账户 1',note:'（实盘账户经上方「实盘账户 ▾」下拉切换；该账号演示数据与现状一致）',
    kpi:['1,284,530','388,360','896,170','+3,845'],
    rows:[
      {code:'600519.SH',nm:'贵州茅台',qty:'100',cost:'1680.0',px:'1712.5',pct:1.9,wt:'13.3%',sec:'白酒（#1 主线）',ctb:'<span class="up">+1.05 万</span> <span class="dim">/+22%</span>',sl:'-2.9%',tp:'+4.8%',risk:'<span class="badge b-pass">正常</span>'},
      {code:'300750.SZ',nm:'宁德时代',qty:'400',cost:'182.0',px:'175.3',pct:-3.7,wt:'5.5%',sec:'新能源（#9 退潮）',ctb:'<span class="down">-0.64 万</span> <span class="dim">/-13%</span>',sl:'-1.8%',tp:'+9.2%',risk:'<span class="badge b-warn">接近止损</span>'},
      {code:'688981.SH',nm:'中芯国际',qty:'1000',cost:'88.2',px:'92.6',pct:5.0,wt:'7.2%',sec:'半导体（#2 转强）',ctb:'<span class="up">+1.82 万</span> <span class="dim">/+38%</span>',sl:'-4.6%',tp:'+6.1%',risk:'<span class="badge b-pass">正常</span>'}],
    alerts:'<div class="alert-row warn">🟡 宁德时代 距止损线 1.8% · 所属板块新能源处退潮期（双重不利）<span class="t">实时</span></div>'},
  real2:{name:'实盘账户 2',note:'（实盘账户经上方「实盘账户 ▾」下拉切换；该账号演示数据）',
    kpi:['452,000','156,800','295,200','-512'],
    attrNA:'分账户归因演示口径仅内置实盘账户 1——本账号盈亏归因待接入（负反馈也是结果——系统明说「没有」）',
    rows:[
      {code:'600276.SH',nm:'恒瑞医药',qty:'800',cost:'45.20',px:'45.38',pct:0.4,wt:'8.0%',sec:'医药（#5 震荡）',ctb:'<span class="up">+0.01 万</span> <span class="dim">/+1%</span>',sl:'-3.4%',tp:'+7.5%',risk:'<span class="badge b-pass">正常</span>'},
      {code:'002594.SZ',nm:'比亚迪',qty:'300',cost:'242.0',px:'239.85',pct:-0.9,wt:'15.9%',sec:'新能源（#9 退潮）',ctb:'<span class="down">-0.06 万</span> <span class="dim">/-2%</span>',sl:'-2.2%',tp:'+8.8%',risk:'<span class="badge b-warn">接近止损</span>'}],
    alerts:'<div class="alert-row info">🔵 实盘账户 2 当前无实时风险告警（演示）<span class="t">实时</span></div>'},
  sim:{name:'miniQMT 模拟',note:'（切换账号见上方 tabs；模拟账户口径演示数据）',
    kpi:['321,500','46,380','275,120','+1,767'],
    attrNA:'模拟账户口径（演示）——分账户盈亏归因待接入（负反馈）',
    rows:[
      {code:'601318.SH',nm:'中国平安',qty:'1000',cost:'47.80',px:'48.35',pct:1.2,wt:'15.0%',sec:'保险（#6 震荡）',ctb:'<span class="up">+0.06 万</span> <span class="dim">/+3%</span>',sl:'-3.1%',tp:'+6.4%',risk:'<span class="badge b-pass">正常</span>'},
      {code:'000858.SZ',nm:'五粮液',qty:'200',cost:'126.50',px:'128.90',pct:1.9,wt:'8.0%',sec:'白酒（#1 主线）',ctb:'<span class="up">+0.05 万</span> <span class="dim">/+2%</span>',sl:'-2.6%',tp:'+5.9%',risk:'<span class="badge b-pass">正常</span>'},
      {code:'588000.SH',nm:'科创50ETF',qty:'200000',cost:'1.085',px:'1.066',pct:-1.8,wt:'66.3%',sec:'宽基ETF（—）',ctb:'<span class="down">-0.38 万</span> <span class="dim">/-19%</span>',sl:'-5.0%',tp:'+4.2%',risk:'<span class="badge b-pass">正常</span>'}],
    alerts:'<div class="alert-row info">🔵 模拟账户当前无实时风险告警（模拟口径演示）<span class="t">实时</span></div>'}
};
function acctPosRow(r){
  var pc=r.pct>=0?'up':'down';
  return '<tr><td><span style="color:var(--text);cursor:pointer;text-decoration:underline" onclick="scrGoStock(\''+r.code+'\')" title="去个股档案页">'+r.code+'</span></td><td>'+r.nm+'</td><td>'+r.qty+'</td><td>'+r.cost+'</td><td>'+r.px+'</td>'
    +'<td class="'+pc+'">'+(r.pct>=0?'+':'')+r.pct.toFixed(1)+'%</td><td>'+r.wt+'</td><td>'+r.sec+'</td>'
    +'<td id="pstate-'+r.code.split('.')[0]+'"><span class="badge b-na">—</span></td>'
    +'<td>'+r.ctb+'</td><td class="'+(r.sl&&r.sl.charAt(0)==='-'?'down':'dim')+'">'+(r.sl||'—')+'</td><td class="dim">'+(r.tp||'—')+'</td><td>'+r.risk+'</td></tr>';
}
function acctSwitch(key,el){
  var tabs=document.querySelectorAll('#pos-acct-tabs .tab'),i;
  for(i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  if(el) el.classList.add('on');
  acctCloseMenu();
  var sum=document.getElementById('pos-sum-view'),av=document.getElementById('pos-acct-view');
  if(key==='sum'){ if(sum)sum.style.display=''; if(av)av.style.display='none'; return; }
  if(sum)sum.style.display='none'; if(av)av.style.display='';
  acctSetAccount(key);
}
function acctCloseMenu(){var m=document.getElementById('acct-real-menu'); if(m)m.classList.remove('open');}
function acctRealTabClick(e){   /* 点「实盘账户 ▾」tab：未激活则先切到当前实盘账号（内部会合拢菜单），再切换菜单开态——修复"首点一闪即关需二次点击"瑕疵 */
  if(e&&e.stopPropagation)e.stopPropagation();
  var t=document.getElementById('acct-real-tab');
  if(t&&!t.classList.contains('on')) acctSetRealTab(window.__acctRealCur||'real');
  var m=document.getElementById('acct-real-menu');
  if(m) m.classList.toggle('open');
}
function acctPick(key,e){   /* 下拉选择实盘账号：tab 文本联动 + 账号视图数据联动 */
  if(e&&e.stopPropagation)e.stopPropagation();
  acctSetRealTab(key);
}
function acctSetRealTab(key){
  if(!ACCOUNT_D[key])return;
  window.__acctRealCur=key;
  var tt=document.getElementById('acct-real-tab-t'); if(tt)tt.textContent=ACCOUNT_D[key].name;
  document.querySelectorAll('#acct-real-menu .acct-mi').forEach(function(mi){mi.classList.toggle('on',mi.dataset.key===key);});
  acctSwitch(key,document.getElementById('acct-real-tab'));
}
function acctGo(key){   /* 汇总视图账户卡跳转：实盘账号走下拉联动，模拟直切 */
  if(key==='real'||key==='real2'){ acctSetRealTab(key); return; }
  var tabs=document.querySelectorAll('#pos-acct-tabs .tab');
  acctSwitch('sim',tabs[tabs.length-1]||null);
}
document.addEventListener('click',function(e){   /* 点击他处收起账号下拉 */
  var t=document.getElementById('acct-real-tab');
  if(t&&!t.contains(e.target)) acctCloseMenu();
});
function acctSetAccount(key){
  var d=ACCOUNT_D[key]; if(!d)return;
  var nm=document.getElementById('pos-acct-name'); if(nm)nm.textContent=d.name;
  var nt=document.getElementById('pos-acct-note'); if(nt)nt.textContent=d.note;
  var pnlCls=d.kpi[3].charAt(0)==='-'?'down':'up';
  var k=document.getElementById('pos-kpi-row');
  if(k) k.innerHTML='<div class="card metric"><div class="l">总资产</div><div class="v">'+d.kpi[0]+'</div></div>'
    +'<div class="card metric"><div class="l">可用资金</div><div class="v">'+d.kpi[1]+'</div></div>'
    +'<div class="card metric"><div class="l">持仓市值</div><div class="v">'+d.kpi[2]+'</div></div>'
    +'<div class="card metric"><div class="l">当日盈亏</div><div class="v '+pnlCls+'">'+d.kpi[3]+'</div></div>';
  var tb=document.getElementById('pos-detail-body');
  if(tb) tb.innerHTML=d.rows.map(acctPosRow).join('');
  if(key==='real'){
    posRenderAttr(); renderCorrNetting(); renderPositionStates(); renderTolBand('real');
  }else{
    var na='<div class="dim" style="font-size:12px;padding:6px 0">'+(d.attrNA||'分账户盈亏归因待接入（负反馈）')+'</div>';
    var s1=document.getElementById('pos-attr-stocks'); if(s1)s1.innerHTML=na;
    var s2=document.getElementById('pos-attr-sector'); if(s2)s2.innerHTML=na;
    var s3=document.getElementById('pos-attr-factor'); if(s3)s3.innerHTML=na;
    var tt=document.getElementById('pos-attr-total'); if(tt)tt.textContent='分账户盈亏归因待接入——真实归因管线按账号口径输出后转真（I-2）';
    var cn=document.getElementById('corr-netting-body'); if(cn)cn.innerHTML='<tr><td>相关性净额</td><td colspan="2" class="dim">'+(key==='sim'?'模拟账户口径（演示）':'分账户口径')+'——待接入</td></tr>';
    renderTolBand(key);
  }
  var al=document.getElementById('pos-alerts'); if(al)al.innerHTML=d.alerts;
}
/* ---- 盈亏日历（金额/收益率双口径；期初 172.0 万换算） ---- */
var PNLCAL_D=[[3,-2227],[4,10644],[5,3166],[6,-96],[7,1398],[10,-391],[11,-523],[12,-297],[13,-3341],[14,203],[17,6080],[18,-2382],[19,-13543],[20,1605],[21,1508],[24,-3271],[25,16]];
var PNLCAL_BASE=1720000;
var PNLCAL_TODAY=25;
var pnlCalMode='amt';
function pnlCalSetMode(m,el){
  pnlCalMode=m;
  var tabs=document.querySelectorAll('#pnlcal-tabs .tab'),i;
  for(i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  if(el)el.classList.add('on');
  pnlCalRender();
}
function pnlCalFmt(v){
  if(pnlCalMode==='pct'){var p=v/PNLCAL_BASE*100;return (p>=0?'+':'')+p.toFixed(2)+'%';}
  return (v>=0?'+':'-')+Math.abs(v).toLocaleString('en-US');
}
function pnlCalRender(){
  var g=document.getElementById('pnlcal-grid'); if(!g)return;
  var map={},sum=0,i,d;
  for(i=0;i<PNLCAL_D.length;i++){map[PNLCAL_D[i][0]]=PNLCAL_D[i][1];sum+=PNLCAL_D[i][1];}
  var h='';
  '日一二三四五六'.split('').forEach(function(w){h+='<div class="cal-wd">'+w+'</div>';});
  for(i=0;i<6;i++) h+='<div class="cal-day blank"></div>';
  for(d=1;d<=31;d++){
    var wd=(5+d)%7;
    if(wd===0||wd===6){h+='<div class="cal-day blank"></div>';continue;}
    if(map[d]===undefined){h+='<div class="cal-day"><span class="dn">'+d+'</span></div>';continue;}
    var v=map[d];
    h+='<div class="cal-day pnl-day'+(d===PNLCAL_TODAY?' today':'')+'" style="background:'+(v>=0?'rgba(202,63,100,.85)':'rgba(37,167,80,.85)')+'">'
      +'<span class="dn">'+d+(d===PNLCAL_TODAY?' 今':'')+'</span><span class="pv">'+pnlCalFmt(v)+'</span></div>';
  }
  g.innerHTML=h;
  var t=document.getElementById('pnlcal-sum');
  if(t){t.className=sum>=0?'up':'down';t.textContent=(sum>=0?'+':'-')+Math.abs(sum).toLocaleString('en-US');}
}
function acctRender(){
  drawLine('acct-spark-real',genCandles(96).map(function(k){return k.c;}),'#CA3F64',220,60);
  drawLine('acct-spark-real2',genCandles(128).map(function(k){return k.c;}),'#25A750',220,60);
  drawLine('acct-spark-sim',genCandles(32).map(function(k){return k.c;}),'#CA3F64',220,60);
  pnlCalRender();
}
