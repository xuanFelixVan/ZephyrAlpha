/* 功能模块：事件日历引擎（cal-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据 CAL_EVENTS（市场过滤）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4357-4471），逻辑零改动。
 * 验收单：ACC-F-CALENDAR-ENGINE
 */
/* ==================== I-5 事件日历（calXxx 前缀） ==================== */
var CAL_CATS={
  macro:   {n:'宏观发布', c:'#A0A6AD'},
  unlock:  {n:'限售解禁', c:'#A0A6AD'},
  ipo:     {n:'新股上市', c:'#A0A6AD'},
  report:  {n:'财报披露', c:'#A0A6AD'},
  dividend:{n:'分红除权', c:'#A0A6AD'},
  crypto:  {n:'币圈事件', c:'#A0A6AD'}   /* IA 市场轴：币版事件类（青=近似族 A 功能色） */
};
var CAL_TODAY=20, CAL_SEL=20;
var CAL_FILTER={macro:true,unlock:true,ipo:true,report:true,dividend:true,crypto:true};
var CAL_HL=[
  {d:21,title:'宁德时代大额解禁',sub:'1.2 亿股定增解禁 · 约占总股本 2.7%',imp:'高'},
  {d:24,title:'中报披露高峰',sub:'高峰周开启 · 预计 2100+ 家集中披露',imp:'高'},
  {d:26,title:'英伟达财报（海外）',sub:'FY27Q2 · AI 算力链风向标',imp:'高'},
  {d:28,title:'杰克逊霍尔央行年会',sub:'鲍威尔讲话 · 降息路径预期',imp:'中'}
];
var CAL_EVENTS=[
  {d:5, cat:'macro',t:'09:45',title:'财新服务业 PMI（7 月）',tg:'大盘/服务业',imp:'中'},
  {d:10,cat:'macro',t:'09:30',title:'中国 7 月 CPI / PPI 发布',tg:'大盘/消费',imp:'高'},
  {d:12,cat:'macro',t:'20:30',title:'美国 7 月 CPI（海外）',tg:'外盘/北向',imp:'高'},
  {d:15,cat:'macro',t:'09:20',title:'央行 MLF 续作（4000 亿到期）',tg:'流动性/银行',imp:'高'},
  {d:19,cat:'macro',t:'02:00',title:'美联储 FOMC 利率决议（海外）',tg:'外盘/汇率',imp:'高'},
  {d:20,cat:'macro',t:'09:15',title:'LPR 报价（1Y / 5Y）',tg:'银行/地产',imp:'高'},
  {d:21,cat:'macro',t:'15:00',title:'股指期货 2508 合约交割（IF/IC/IM）',tg:'大盘/衍生品',imp:'中'},
  {d:27,cat:'macro',t:'09:30',title:'7 月工业企业利润',tg:'周期/制造',imp:'中'},
  {d:28,cat:'macro',t:'21:40',title:'杰克逊霍尔央行年会·鲍威尔讲话（海外）',tg:'外盘/流动性预期',imp:'高'},
  {d:31,cat:'macro',t:'09:30',title:'8 月官方 PMI（制造业/非制造业）',tg:'大盘/周期',imp:'高'},
  {d:3, cat:'unlock',t:'—',title:'中芯国际 2.1 亿股解禁（战略配售）',tg:'688981.SH/半导体',imp:'中'},
  {d:10,cat:'unlock',t:'—',title:'韦尔股份 0.8 亿股解禁（定增）',tg:'603501.SH/半导体',imp:'中'},
  {d:21,cat:'unlock',t:'—',title:'宁德时代 1.2 亿股解禁（定增）',tg:'300750.SZ/新能源',imp:'高'},
  {d:24,cat:'unlock',t:'—',title:'海光信息 3.5 亿股解禁（首发原股东）',tg:'688041.SH/算力',imp:'高'},
  {d:28,cat:'unlock',t:'—',title:'贵州茅台 0.15 亿股解禁（股权激励）',tg:'600519.SH/白酒',imp:'中'},
  {d:4, cat:'ipo',t:'—',title:'华电新能上市（沪市主板）',tg:'电力/新股',imp:'中'},
  {d:11,cat:'ipo',t:'—',title:'屹唐股份上市（科创板）',tg:'半导体设备/新股',imp:'中'},
  {d:25,cat:'ipo',t:'—',title:'珂玛科技上市（科创板）',tg:'新材料/新股',imp:'中'},
  {d:12,cat:'report',t:'盘后',title:'腾讯控股中报（港股）',tg:'0700.HK/互联网',imp:'高'},
  {d:14,cat:'report',t:'盘后',title:'贵州茅台 2026 中报',tg:'600519.SH/白酒',imp:'高'},
  {d:18,cat:'report',t:'盘后',title:'招商银行 2026 中报',tg:'600036.SH/银行',imp:'中'},
  {d:20,cat:'report',t:'盘后',title:'恒瑞医药 2026 中报',tg:'600276.SH/医药',imp:'中'},
  {d:21,cat:'report',t:'盘后',title:'美的集团 2026 中报',tg:'000333.SZ/家电',imp:'中'},
  {d:24,cat:'report',t:'—',title:'中报披露高峰周开启（2100+ 家集中披露）',tg:'全市场',imp:'高'},
  {d:26,cat:'report',t:'盘后',title:'英伟达 FY27Q2 财报（海外）',tg:'NVDA/AI 算力链',imp:'高'},
  {d:6, cat:'dividend',t:'—',title:'中国神华除权除息（10 派 22.6 元）',tg:'601088.SH/煤炭',imp:'中'},
  {d:13,cat:'dividend',t:'—',title:'长江电力除权除息（10 派 8.2 元）',tg:'600900.SH/电力',imp:'中'},
  {d:20,cat:'dividend',t:'—',title:'工商银行除权除息（中期 10 派 3.06 元）',tg:'601398.SH/银行',imp:'中'},
  {d:2, cat:'crypto',t:'—',title:'SUI 1.2 亿枚线性解锁（月度）',tg:'SUI/L1',imp:'中'},
  {d:7, cat:'crypto',t:'08:00',title:'美国现货 BTC ETF 周度资金流公布',tg:'BTC ETH/资金面',imp:'高'},
  {d:14,cat:'crypto',t:'—',title:'ARB 大额 cliff 解锁（团队+投资人份额）',tg:'ARB/L2',imp:'高'},
  {d:22,cat:'crypto',t:'21:00',title:'美参议院数字资产市场结构法案听证',tg:'监管/BTC ETH',imp:'高'},
  {d:28,cat:'crypto',t:'16:00',title:'Deribit BTC/ETH 月度期权交割',tg:'BTC ETH/衍生品',imp:'中'},
  {d:29,cat:'crypto',t:'—',title:'CME BTC 期货月度交割',tg:'BTC/衍生品',imp:'中'}
];
function calWd(d){return '日一二三四五六'.charAt((d+5)%7);}
function calEvOf(d){return CAL_EVENTS.filter(function(e){return e.d===d&&CAL_FILTER[e.cat]&&calMkOk(calMkOf(e));});}
function calImpBadge(imp){return '<span class="badge '+(imp==='高'?'b-fail':'b-warn')+'">'+imp+'</span>';}
function calRenderHl(){
  var h='';
  CAL_HL.forEach(function(x){
    var cd=x.d-CAL_TODAY;
    h+='<div class="card"><div class="dim" style="font-size:11px">08-'+x.d+' 周'+calWd(x.d)+' · <b style="color:var(--text)">'+(cd<=0?'今天':cd+' 天后')+'</b></div>'
      +'<div style="font-weight:600;margin:3px 0 4px">'+x.title+'</div>'
      +'<div style="font-size:11px;color:var(--faint);margin-bottom:6px">'+x.sub+'</div>'
      +calImpBadge(x.imp)+'</div>';
  });
  document.getElementById('cal-hl').innerHTML=h;
}
var CAL_MK='all';
var CAL_MKS=[{k:'all',n:'全部'},{k:'m',n:'宏观'},{k:'a',n:'A股'},{k:'c',n:'币圈'}];
function calMkOf(e){return e.cat==='macro'?'m':e.cat==='crypto'?'c':'a';}
function calMkOk(mk){return CAL_MK==='all'||(CAL_MK==='m'?mk==='m':CAL_MK==='a'?mk!=='c':mk!=='a');}   /* 宏观事件两市场共享（Owner 2026-08-27：日历合一页+市场过滤） */
function calMkSet(k){CAL_MK=k;calRenderLegend();calRenderGrid();calRenderList();}
function calRenderLegend(){
  var h='<span class="dim" style="font-size:11px">市场</span>';
  CAL_MKS.forEach(function(m){
    h+='<span class="cal-chip'+(CAL_MK===m.k?'':' off')+'" onclick="calMkSet(\''+m.k+'\')">'+m.n+'</span>';
  });
  h+='<span style="width:1px;height:14px;background:var(--border);margin:0 2px"></span><span class="dim" style="font-size:11px">分类</span>';
  Object.keys(CAL_CATS).forEach(function(k){
    h+='<span class="cal-chip'+(CAL_FILTER[k]?'':' off')+'" onclick="calToggle(\''+k+'\')"><i class="cal-dot" style="background:'+CAL_CATS[k].c+'"></i>'+CAL_CATS[k].n+'</span>';
  });
  h+='<span class="dim" style="font-size:11px;margin-left:auto">市场过滤：宏观事件两市场共享；分类标签隐藏/显示该类事件（月历圆点与当日清单同步过滤）</span>';
  document.getElementById('cal-legend').innerHTML=h;
}
function calRenderGrid(){
  var h='',i,d;
  '日一二三四五六'.split('').forEach(function(w){h+='<div class="cal-wd">'+w+'</div>';});
  for(i=0;i<6;i++) h+='<div class="cal-day blank"></div>';
  for(d=1;d<=31;d++){
    var evs=calEvOf(d);
    h+='<div class="cal-day'+(d===CAL_TODAY?' today':'')+(d===CAL_SEL?' sel':'')+'" onclick="calSel('+d+')"><span class="dn">'+d+'</span>';
    if(evs.length){
      h+='<span class="cal-dots">';
      evs.slice(0,3).forEach(function(e){h+='<i style="background:'+CAL_CATS[e.cat].c+'"></i>';});
      if(evs.length>3) h+='<em class="cal-more">+'+(evs.length-3)+'</em>';
      h+='</span>';
    }
    h+='</div>';
  }
  document.getElementById('cal-grid').innerHTML=h;
}
function calRenderList(){
  var evs=calEvOf(CAL_SEL).slice().sort(function(a,b){return a.t<b.t?-1:1;});
  document.getElementById('cal-selday').textContent='8 月 '+CAL_SEL+' 日（周'+calWd(CAL_SEL)+'）';
  document.getElementById('cal-count').textContent=evs.length+' 项';
  var h='<tr><th style="width:60px">时间</th><th style="width:92px">分类</th><th>事件</th><th style="width:150px">影响标的/领域</th><th style="width:60px">重要性</th></tr>';
  if(!evs.length) h+='<tr><td colspan="5" class="na">当日无（已勾选分类的）事件</td></tr>';
  evs.forEach(function(e){
    h+='<tr><td>'+e.t+'</td><td><i class="cal-dot" style="background:'+CAL_CATS[e.cat].c+'"></i>'+CAL_CATS[e.cat].n+'</td><td>'+e.title+'</td><td class="dim">'+e.tg+'</td><td>'+calImpBadge(e.imp)+'</td></tr>';
  });
  document.getElementById('cal-table').innerHTML=h;
}
function calSel(d){CAL_SEL=d;calRenderGrid();calRenderList();}
function calToggle(k){CAL_FILTER[k]=!CAL_FILTER[k];calRenderLegend();calRenderGrid();calRenderList();}
window.calInit=function(){calRenderHl();calRenderLegend();calRenderGrid();calRenderList();};
