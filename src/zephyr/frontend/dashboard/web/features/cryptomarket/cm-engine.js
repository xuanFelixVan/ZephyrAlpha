/* 功能模块：币圈组引擎（cm-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据（OKX 公开 API 待接入 I-2）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L6799-6946），逻辑零改动。
 * 验收单：ACC-F-CRYPTO-CM-ENGINE
 */
/* ==================== §C 币圈组引擎（cmXxx/cpXxx/ciXxx：盘面行情+持仓风控+档案卡；演示数据，OKX 公开 API 待接入 I-2） ==================== */
var CRYPTO_D=[
 {sym:'BTC',pair:'BTC/USDT',px:85062.4,chg:+1.24,vol24:'182.6亿',fund:+0.012,oi:'486.2亿',oiChg:+2.8,ls:[52.3,47.7],liqL:'1.24亿',liqS:'0.86亿',basis:'+0.04%',seed:8801},
 {sym:'ETH',pair:'ETH/USDT',px:3421.8,chg:+2.35,vol24:'96.4亿',fund:+0.018,oi:'152.8亿',oiChg:+4.2,ls:[54.1,45.9],liqL:'0.68亿',liqS:'0.42亿',basis:'+0.06%',seed:8802},
 {sym:'SOL',pair:'SOL/USDT',px:186.42,chg:-0.87,vol24:'28.9亿',fund:-0.006,oi:'24.6亿',oiChg:-1.6,ls:[48.2,51.8],liqL:'0.15亿',liqS:'0.22亿',basis:'-0.02%',seed:8803},
 {sym:'XRP',pair:'XRP/USDT',px:1.462,chg:+0.58,vol24:'12.4亿',fund:+0.008,oi:'9.8亿',oiChg:+0.9,ls:[50.6,49.4],liqL:'0.06亿',liqS:'0.05亿',basis:'+0.01%',seed:8804},
 {sym:'DOGE',pair:'DOGE/USDT',px:0.1624,chg:-1.86,vol24:'8.2亿',fund:-0.011,oi:'6.4亿',oiChg:-3.2,ls:[46.8,53.2],liqL:'0.09亿',liqS:'0.12亿',basis:'-0.03%',seed:8805}
];
var CP_POS=[
 {sym:'BTC/USDT',dir:1,lev:3,qty:'0.25',entry:82340,mark:85062.4,liqPx:71800,fundC:'+12.4 USDT'},
 {sym:'ETH/USDT',dir:1,lev:5,qty:'3.0',entry:3290,mark:3421.8,liqPx:2950,fundC:'+8.6 USDT'},
 {sym:'SOL/USDT',dir:-1,lev:2,qty:'80',entry:192.5,mark:186.42,liqPx:226.8,fundC:'-3.2 USDT'}
];
function cmKpis(){
  var k=[['BTC  dominance','58.2%','市值占比'],['24h 全市场爆仓','$2.94 亿','多 $1.62 / 空 $1.32'],['恐惧贪婪指数','64','贪婪区间（0-100）'],['资金费率均值','+0.009%','8h · 偏多温和']];
  var h='';
  k.forEach(function(x){ h+='<div class="card metric"><div class="l">'+x[0]+'</div><div class="v">'+x[1]+'</div><div class="s">'+x[2]+'</div></div>'; });
  document.getElementById('cm-kpis').innerHTML=h;
}
function cmTable(){
  var h='<table><tr><th>币种</th><th>最新价</th><th>24h 涨跌</th><th>24h 成交额</th><th>资金费率(8h)</th><th>持仓量 OI</th><th>OI 24h</th><th>多空比</th><th>24h 爆仓(多/空)</th><th>标记-指数</th><th>24h 走势</th></tr>';
  CRYPTO_D.forEach(function(c){
    h+='<tr><td><b>'+c.sym+'</b> <span class="dim">'+c.pair+'</span></td>'
      +'<td style="font-weight:600">'+c.px.toLocaleString('en-US',{minimumFractionDigits:2})+'</td>'
      +'<td class="'+(c.chg>=0?'up':'down')+'">'+(c.chg>=0?'+':'')+c.chg.toFixed(2)+'%</td>'
      +'<td>'+c.vol24+'</td>'
      +'<td class="'+(c.fund>=0?'up':'down')+'">'+(c.fund>=0?'+':'')+c.fund.toFixed(3)+'%</td>'
      +'<td>'+c.oi+'</td>'
      +'<td class="'+(c.oiChg>=0?'up':'down')+'">'+(c.oiChg>=0?'+':'')+c.oiChg.toFixed(1)+'%</td>'
      +'<td>'+c.ls[0]+' / '+c.ls[1]+'</td>'
      +'<td><span class="up">'+c.liqL+'</span> / <span class="down">'+c.liqS+'</span></td>'
      +'<td class="'+(c.basis.indexOf('+')===0?'up':'down')+'">'+c.basis+'</td>'
      +'<td><svg class="spark" id="cm-sp-'+c.sym+'" viewBox="0 0 120 34" preserveAspectRatio="none" style="width:110px;height:30px"></svg></td></tr>';
  });
  h+='</table><div class="note">涨跌色=A股语义（红涨绿跌）；资金费率正=多头付费（市场偏多）· 负=空头付费；结算倒计时 04:26:18（8h 周期）</div>';
  document.getElementById('cm-table').innerHTML=h;
  CRYPTO_D.forEach(function(c){
    var svg=document.getElementById('cm-sp-'+c.sym); if(!svg)return;
    var d=genCandles(c.seed,40),lo=1e18,hi=-1e18;
    d.forEach(function(k){lo=Math.min(lo,k.l);hi=Math.max(hi,k.h);});
    var pts=d.map(function(k,i){return [i*119/39,32-(k.c-lo)/(hi-lo||1)*30];});
    polyline(el('g',{},svg),pts,c.chg>=0?'#CA3F64':'#25A750',1.2);
  });
}
function cmFunding(){
  var h='';
  CRYPTO_D.forEach(function(c){
    var v=c.fund,hot=Math.abs(v)>=0.01;
    h+='<div class="bar-row"><span style="width:36px">'+c.sym+'</span><div class="bar"><i class="'+(v>=0?'r':'g')+'" style="width:'+Math.min(100,Math.abs(v)/0.02*100).toFixed(0)+'%"></i></div><span class="'+(v>=0?'up':'down')+'">'+(v>=0?'+':'')+v.toFixed(3)+'%</span>'+(hot?'<span class="badge b-warn">偏热</span>':'')+'</div>';
  });
  h+='<div class="note">|费率| ≥0.01% 标"偏热"：极端费率=反转预警（Coinglass 同位口径）</div>';
  document.getElementById('cm-funding').innerHTML=h;
}
function cmOi(){
  var svg='<svg class="spark" viewBox="0 0 520 150" preserveAspectRatio="none" style="width:100%;height:150px;background:#000;border-radius:8px">';
  var d=genCandles(8866,48),lo=1e18,hi=-1e18;
  d.forEach(function(k){lo=Math.min(lo,k.l);hi=Math.max(hi,k.h);});
  var g='<g>',pts=d.map(function(k,i){return [i*510/47,140-(k.c-lo)/(hi-lo)*125+5];});
  var path='M'+pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1);}).join(' L');
  svg+=g+'<path d="'+path+'" fill="none" stroke="#F0B90B" stroke-width="1.5"/></g>';
  svg+='<text x="10" y="20" fill="#8B949E" font-size="11">BTC OI 486.2 亿（+2.8%/24h）——价升 OI 升=多头增仓延续</text></svg>';
  document.getElementById('cm-oi').innerHTML=svg;
}
function cmLiq(){
  var lv=[[86800,'空爆 2.4亿',0.86],[86000,'空爆 1.8亿',0.62],[85200,'空爆 0.9亿',0.31],[84500,'多爆 1.1亿',0.38],[83800,'多爆 1.6亿',0.55],[82400,'多爆 2.9亿',1.0],[81200,'多爆 2.2亿',0.76]];
  var h='<div style="font-size:11px">BTC 现价 <b>85,062</b> 上下待清算簇（杠杆清算磁石）：</div>';
  lv.forEach(function(l){
    var isShort=l[1].indexOf('空')===0;
    h+='<div class="bar-row"><span style="width:52px">'+l[0].toLocaleString()+'</span><div class="bar"><i class="'+(isShort?'g':'r')+'" style="width:'+(l[2]*100).toFixed(0)+'%"></i></div><span class="'+(isShort?'down':'up')+'">'+l[1]+'</span></div>';
  });
  h+='<div class="note">上方空爆簇（86,800）=价格上行磁石；下方多爆簇（82,400）=下行磁石——做市商猎杀流动性口径（演示）</div>';
  document.getElementById('cm-liq').innerHTML=h;
}
function cmLs(){
  var h='<div class="sec-title" style="margin-top:0">全市场多空比（账户数口径）</div>';
  CRYPTO_D.forEach(function(c){
    h+='<div class="bar-row"><span style="width:36px">'+c.sym+'</span><div class="bar"><i class="r" style="width:'+c.ls[0]+'%"></i></div><span><span class="up">多 '+c.ls[0]+'%</span> / <span class="down">空 '+c.ls[1]+'%</span></span></div>';
  });
  h+='<div class="note">多空比 &gt;55% 或 &lt;45% =情绪极值反向指标（演示口径，Coinglass 同位）</div>';
  document.getElementById('cm-ls').innerHTML=h;
}
function cmInit(){ cmKpis(); cmTable(); cmFunding(); cmOi(); cmLiq(); cmLs(); }
function cpKpis(){
  var k=[['账户权益（USDT）','128,640','可用保证金 86,200'],['未实现盈亏','<span class="up">+3,214</span>','ROI 口径'],['维持保证金率','4.8%','预警线 8%'],['总杠杆','2.6x','限额 ≤3x ✅']];
  var h='';
  k.forEach(function(x){ h+='<div class="card metric"><div class="l">'+x[0]+'</div><div class="v">'+x[1]+'</div><div class="s">'+x[2]+'</div></div>'; });
  document.getElementById('cp-kpis').innerHTML=h;
}
function cpTable(){
  var h='<table><tr><th>合约</th><th>方向</th><th>杠杆</th><th>数量</th><th>开仓均价</th><th>标记价格</th><th>未实现盈亏</th><th>ROI</th><th>强平价</th><th>距强平</th><th>资金费累计</th></tr>';
  CP_POS.forEach(function(p){
    var pnl=(p.mark-p.entry)*p.dir*parseFloat(p.qty),roi=(p.mark-p.entry)*p.dir/p.entry*100*p.lev;
    var dist=(p.mark-p.liqPx)/(p.dir===1?p.mark:(p.liqPx))*100*(p.dir===1?1:1);
    var dd=p.dir===1?(p.mark-p.liqPx)/p.mark*100:(p.liqPx-p.mark)/p.mark*100;
    var dc=dd>20?'up':(dd>10?'warn':'down');
    h+='<tr><td><b>'+p.sym+'</b></td>'
      +'<td><span class="badge '+(p.dir===1?'b-buy':'b-sell')+'">'+(p.dir===1?'多':'空')+'</span></td>'
      +'<td>'+p.lev+'x</td><td>'+p.qty+'</td>'
      +'<td>'+p.entry.toLocaleString('en-US',{minimumFractionDigits:2})+'</td>'
      +'<td>'+p.mark.toLocaleString('en-US',{minimumFractionDigits:2})+'</td>'
      +'<td class="'+(pnl>=0?'up':'down')+'">'+(pnl>=0?'+':'')+pnl.toFixed(1)+' U</td>'
      +'<td class="'+(roi>=0?'up':'down')+'">'+(roi>=0?'+':'')+roi.toFixed(1)+'%</td>'
      +'<td>'+p.liqPx.toLocaleString()+'</td>'
      +'<td class="'+dc+'">'+dd.toFixed(1)+'%</td>'
      +'<td class="'+(p.fundC.indexOf('+')===0?'up':'down')+'">'+p.fundC+'</td></tr>';
  });
  h+='</table><div class="note">盈亏按标记价格计（防插针口径）；距强平&lt;10% 触发预警推送（风控同 A 股 human_gated 纪律）；减仓/加仓均需审批</div>';
  document.getElementById('cp-table').innerHTML=h;
}
function cpWarn(){
  var h='';
  CP_POS.map(function(p){   /* 与仓位表同一公式计算距强平（消灭硬编码残留不一致——自检抓出 SOL 12.6% vs 表 21.7%） */
    var dd=p.dir===1?(p.mark-p.liqPx)/p.mark*100:(p.liqPx-p.mark)/p.mark*100;
    return [p.sym+' '+(p.dir===1?'多':'空')+' '+p.lev+'x', dd];
  }).sort(function(a,b){return a[1]-b[1];}).forEach(function(r){
    var cls=r[1]>20?'g':(r[1]>10?'y':'r'),tc=r[1]>20?'up':(r[1]>10?'warn':'down');
    h+='<div class="bar-row"><span style="width:130px">'+r[0]+'</span><div class="bar"><i class="'+cls+'" style="width:'+Math.min(100,r[1]*3).toFixed(0)+'%"></i></div><span class="'+tc+'">'+r[1].toFixed(1)+'%</span></div>';
  });
  h+='<div class="note">按距强平升序——最危险仓位排最前；&lt;10% 自动推送"减仓审批"待办（演示当前无 &lt;10% 仓位）</div>';
  document.getElementById('cp-warn').innerHTML=h;
}
function cpRules(){
  var h='<div class="sec-title" style="margin-top:0">资金费累计（近 30 日）</div>'
    +'<div class="kv-mini">BTC 多 <b class="up">+12.4 U</b> ｜ ETH 多 <b class="up">+8.6 U</b> ｜ SOL 空 <b class="down">-3.2 U</b> —— 净收 <b class="up">+17.8 U</b>（多头付费期持仓成本）</div>'
    +'<div class="sec-title">风控规则（币圈域五层之一，与 A 股限额体系并列登记）</div>'
    +'<div class="kv-mini">① 单币杠杆 ≤5x（当前最大 5x ETH ✅）② 账户总杠杆 ≤3x（当前 2.6x ✅）③ 距强平 &lt;10% 强制减仓审批 ④ 资金费极端（|费率|≥0.05%）禁止开新仓 ⑤ 24/7 熔断开关与 A 股共用（系统状态页）</div>'
    +'<div class="note">差异说明：币圈风险模型=强平距离+资金费，A 股=止损距离+回撤预算——两套规则并列不混（§C-2）</div>';
  document.getElementById('cp-rules').innerHTML=h;
}
function cpInit(){ cpKpis(); cpTable(); cpWarn(); cpRules(); }
function ciRender(){
  var cards=[
   ['BTC','比特币','2100 万','1,980 万（94.3%）','1.68 万亿','PoW · 数字黄金叙事，ETF 流向为核心变量'],
   ['ETH','以太坊','无上限（EIP-1559 通缩机制）','1.204 亿','4,120 亿','PoS · 智能合约平台，质押率 28.6%'],
   ['SOL','Solana','5.88 亿（通胀递减）','4.62 亿','860 亿','PoH+PoS · 高吞吐公链，生态活跃度第二']
  ];
  var h='';
  cards.forEach(function(c){
    h+='<div class="card"><h3>'+c[0]+' <span class="dim">'+c[1]+'</span></h3><div class="sq-fin">'
      +'<span class="k">发行上限</span><span class="v">'+c[2]+'</span>'
      +'<span class="k">流通量</span><span class="v">'+c[3]+'</span>'
      +'<span class="k">市值（USD）</span><span class="v">'+c[4]+'</span></div>'
      +'<div class="sq-intro">'+c[5]+'</div><div class="note">链上数据/流通明细待接入 I-2（演示框架）</div></div>';
  });
  document.getElementById('ci-cards').innerHTML=h;
}
ciRender();

