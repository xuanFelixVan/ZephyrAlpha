function go(id, el){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('p-'+id).classList.add('active');
  if(el)el.classList.add('active');   /* el 可空守卫：go(id) 单参调用合法（高亮由 GRP_OF 兜底）——子代理复验建议 */
  var GRP_OF={overview:'overview',warroom:'ashare',live:'ashare',sector:'ashare',sentiment:'ashare',news:'ashare',policy:'ashare',overseas:'ashare',t0:'ashare',review:'ashare',position:'ashare',strategy:'ashare',factor:'ashare',backtest:'ashare',experiment:'ashare',screener:'ashare',index:'ashare',stockq:'ashare',stock:'ashare',macro:'ashare',chainmap:'ashare',calendar:'ashare',cryptomarket:'crypto',cryptopos:'crypto',cryptostrat:'crypto',cryptobt:'crypto',cryptoinfo:'crypto',datainfo:'data',reglib:'data',datasrc:'data',rating:'ashare',aichat:'ai',aitask:'ai',models:'sys',task:'sys',fitness:'sys',govana:'sys',modledger:'sys',sysstatus:'sys',pano:'sys',design:'sys'};   /* IA 市场轴（2026-08-27）：页→组归属唯一表，跨页跳转元素无 data-grp 时兜底；08-29 增 ai 组（aichat/aitask，R5 第六组） */
  var grp=(el&&el.getAttribute('data-grp'))||GRP_OF[id]||'';   /* F3 顶栏：一级分组高亮同步 */
  document.querySelectorAll('.tb-grp').forEach(function(g){ g.classList.toggle('on', g.getAttribute('data-grp')===grp); });
  var initFn=window[{'stock':'stockInit','stockq':'sqInit','cryptomarket':'cmInit','cryptopos':'cpInit','screener':'scrInit','calendar':'calInit','review':'revInit','news':'annInit','policy':'polInit','experiment':'expInit','position':'posInit','index':'renderIdxAll','reglib':'reglibInit','pano':'panoInit','modledger':'modInit','strategy':'fwInit'}[id]];   /* I-5/I-6/I-8 页级初始化钩子（显式映射防短名失配，幂等） */
  if(typeof initFn==='function') initFn();
}
/* 规划页灰化占位负反馈（IA 市场轴 2026-08-27 Owner 裁定）：点击不出页面，toast 说明，不造假 */
function navDis(e,name){ e.stopPropagation(); gToast('「'+name+'」规划中——币版 I-2 真源就绪后接入，结构占位不造假页面'); }
function gToast(t){
  var el=document.getElementById('g-toast'); if(!el) return;
  el.textContent=t; el.style.display='block';
  clearTimeout(window.__gtT); window.__gtT=setTimeout(function(){ el.style.display='none'; },3600);
}
/* ---- 侧边栏：组折叠 / 图标态折叠（状态 localStorage 记忆） ---- */
function foldGroup(grp,folded){
  grp.classList.toggle('fold',folded);
  var ar=grp.querySelector('.ng-ar'); if(ar) ar.textContent=folded?'▸':'▾';
  var sib=grp.nextElementSibling;
  while(sib&&!sib.classList.contains('nav-group')&&!sib.classList.contains('side-foot')){
    if(sib.classList.contains('nav-item')) sib.classList.toggle('hide',folded);
    sib=sib.nextElementSibling;
  }
}
function tg(grp){
  if(document.querySelector('.app').classList.contains('sd-coll')){ sdToggle(); return; }   /* 图标态点组图标=展开侧边 */
  var folded=!grp.classList.contains('fold');
  foldGroup(grp,folded);
  var st={}; try{st=JSON.parse(localStorage.getItem('zk-nav-fold')||'{}');}catch(e){}
  st[grp.querySelector('.ng-t').textContent]=folded?1:0;
  try{localStorage.setItem('zk-nav-fold',JSON.stringify(st));}catch(e){}
}
function sdToggle(){
  var app=document.querySelector('.app');
  var c=app.classList.toggle('sd-coll');
  document.getElementById('sd-tog').textContent=c?'»':'«';
  try{localStorage.setItem('zk-side-coll',c?'1':'');}catch(e){}
}
(function(){   /* F3 顶栏批：清理左侧栏时代遗留的折叠状态键（防止旧 sd-coll 类污染新骨架） */
  try{ localStorage.removeItem('zk-side-coll'); localStorage.removeItem('zk-nav-fold'); }catch(e){}
})();
/* ---- F3 语言选择占位（tbLangTgl：简体/CNY 默认，English 置灰待接入） ---- */
function tbLangTgl(e){
  e.stopPropagation();
  var d=document.getElementById('tb-lang-drop'); if(d) d.classList.toggle('open');
}
document.addEventListener('click',function(e){
  var l=document.getElementById('tb-lang'),d=document.getElementById('tb-lang-drop');
  if(l&&d&&d.classList.contains('open')&&!l.contains(e.target)) d.classList.remove('open');
});
/* ==================== 作战室：3×3 情景矩阵方案展开（演示数据；字段契约对齐 MOD-PLAN-005 ScenarioPlan / MOD-PLAN-001 TomorrowBoundary / MOD-SIG-061/062） ==================== */
var WR={
 '00':{t:'高开 >+2% + 高走',act:'进攻',bc:'b-buy',logic:'强势确认：高开且 30 分钟站稳 VWAP，主线延续 → 按进攻档加仓（仓位 ×1.2 缩放）',
   sec:[['半导体','72%','主线概率最高·梯队完整'],['AI 算力','58%','跟随主线']],
   stk:[['中芯国际','龙头','回踩 91.20 不破（box_lower 附近）','8%→12%（×1.2，封顶 firm 8% 单票）','96.80（no_add_price）','89.50（must_exit）','板块涨停家数 <5 即作废','2.8:1','+0.9R'],
        ['中微公司','中军','突破 188.50 放量确认（breakout_confirm：放量站稳10分钟）','6%','195.00','182.00','龙头炸板不回封','2.1:1','+0.5R']],
   bal:'0%（进攻情景不配压舱石）'},
 '01':{t:'高开 >+2% + 平走',act:'观察',bc:'b-na',logic:'高开兑现压力（新闻页双标签：可预测利好=兑现风险）→ 不追高、不开新仓，持仓按 must_exit 纪律管理',
   sec:[],stk:[],bal:'0%'},
 '02':{t:'高开 >+2% + 低走',act:'防守',bc:'b-sell',logic:'冲高回落=利好兑现信号 → 减仓至 5 成；触发=跌破 VWAP 且 30 分钟收不回',
   sec:[],stk:[],bal:'10%（沪深300ETF 底仓）'},
 '10':{t:'平开 ±2% + 高走',act:'进攻·轻仓试',bc:'b-buy',logic:'平开走强=无外盘借力下的内生强势 → 买主线龙头回踩（最可能格：W3 观察哨逐项确认后执行）',
   sec:[['半导体','72%','主线概率最高（MOD-SIG-061）'],['机器人','51%','次主线候选']],
   stk:[['中芯国际','龙头','回踩 90.10（今日 VWAP 上沿）','6%→8%（×1.0）','96.80','89.50','板块涨停家数 <5 即作废','2.5:1','+0.7R'],
        ['汇川技术','中军','突破 62.30 放量确认','5%','65.00','60.10','龙头中芯国际炸板','1.9:1','+0.4R']],
   bal:'0%'},
 '11':{t:'平开 ±2% + 平走',act:'观察',bc:'b-na',logic:'震荡延续 → 以持仓做T为主（联动 T分析页点位），10:00 后不开新仓',
   sec:[],stk:[],bal:'0%'},
 '12':{t:'平开 ±2% + 低走',act:'防守',bc:'b-sell',logic:'弱势确认 → 减仓观察；失效触发=主线跌停 >3 家 → 清进攻仓',
   sec:[],stk:[],bal:'15%（沪深300ETF+中证500ETF）'},
 '20':{t:'低开 <-2% + 高走',act:'黄金坑',bc:'b-buy',logic:'低开翻红=恐慌盘被主力接走（需 D2 竞价量 ≥1.2× 确认，D3>0.6 则信号作废）→ 重仓低吸主线',
   sec:[['半导体','68%','恐慌低吸主线龙头'],['证券','45%','护盘预期']],
   stk:[['中芯国际','龙头','翻红瞬间 89.80 附近','10%（黄金坑专项）','94.00','87.20','翻红失败回落 VWAP 下方=作废','3.2:1','+1.1R'],
        ['东方财富','中军','站稳 24.50','6%','26.00','23.80','指数二次探底破前低','2.4:1','+0.6R']],
   bal:'10%'},
 '21':{t:'低开 <-2% + 平走',act:'观察',bc:'b-na',logic:'方向不明 → 观望等 30 分钟确认；不抄底（A股社区纪律：低开不翻红不动手）',
   sec:[],stk:[],bal:'20%'},
 '22':{t:'低开 <-2% + 低走',act:'退潮',bc:'b-sell',logic:'退潮信号（空间板被核+主线跌停蔓延）→ 清进攻仓观望，压舱石顶上',
   sec:[],stk:[],bal:'40%（沪深300ETF 25%+中证500ETF 15%，防御性底仓最大化）'}
};
function warRender(k){
  var d=WR[k],h='<div style="border-top:1px solid var(--border);padding-top:10px">'
    +'<div style="font-size:13px;margin-bottom:8px">方案详情：<b>'+d.t+'</b> <span class="badge '+d.bc+'">'+d.act+'</span></div>'
    +'<div style="font-size:12px;color:var(--dim);margin-bottom:10px">'+d.logic+'</div>';
  if(d.sec.length){
    h+='<div class="sec-title" style="margin-top:0">① 买什么板块（主线概率排序，MOD-SIG-061）</div><table><tr><th>板块</th><th>主线概率</th><th>依据</th></tr>';
    d.sec.forEach(function(s){h+='<tr><td>'+s[0]+'</td><td class="up">'+s[1]+'</td><td>'+s[2]+'</td></tr>';});
    h+='</table>';
  }
  if(d.stk.length){
    h+='<div class="sec-title">② 买什么个股（龙头/中军定位，MOD-SIG-062；点位/仓位=MOD-PLAN-001 边界×档位缩放）· 点击个股名看决策卡（A4）</div><table><tr><th>个股</th><th>定位</th><th>买入点位</th><th>仓位</th><th>禁加仓价</th><th>必出价</th><th>失效条件</th><th>盈亏比</th><th>期望值</th></tr>';
    d.stk.forEach(function(s){h+='<tr><td><b style="cursor:pointer;color:var(--text);text-decoration:underline" onclick="openDecision(\''+s[0]+'\')">'+s[0]+'</b></td><td>'+s[1]+'</td><td>'+s[2]+'</td><td>'+s[3]+'</td><td>'+s[4]+'</td><td>'+s[5]+'</td><td class="down">'+s[6]+'</td><td>'+s[7]+'</td><td class="up">'+s[8]+'</td></tr>';});
    h+='</table>';
  }
  if(!d.sec.length){h+='<div style="font-size:12px;color:var(--dim);background:var(--input);border-radius:6px;padding:10px">'+d.act+'情景：不开新仓。持仓按 must_exit_price 纪律管理，触发条件全数值化（可证伪），满足即执行、不满足即等待。</div>';}
  h+='<div class="note">③ 防御压舱石（该情景宽基 ETF 配置）：'+d.bal+'；失效条件=逻辑破坏点（非止损价）——逻辑坏了方案立即作废，不等价格触发</div></div>';
  document.getElementById('wr-detail').innerHTML=h;
}
function warSel(k,el){
  document.querySelectorAll('#wr-grid .wr-cell').forEach(function(c){
    if(c.dataset.ob)c.style.border=c.dataset.ob;
  });
  if(!el.dataset.ob)el.dataset.ob=el.style.border;
  el.style.border='2px solid var(--text)';
  warRender(k);
}
warRender('10');  /* 默认展开最可能格 */
/* A4 决策卡开关 */
function openDecision(name){document.getElementById('dc-name').textContent=name;document.getElementById('decision-mask').style.display='block';}
function closeDecision(){document.getElementById('decision-mask').style.display='none';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')closeDecision();});
var expNames=['c1_mock_20260819_sector','c1_mock_20260818_multi','c1_mock_20260817_daban'];
/* 交互实测修复：实验历史净值 JS 渲染 + 勾选 2 run 双线对比（expCk/expNavRender） */
var expCk=[];
function expLine(i){
  var r=lcg(20260800+i*37),pts=[],p=145;
  for(var k=0;k<13;k++){p-=(r()*14+4);pts.push(p);}
  return pts;
}
function expNavRender(){
  var svg=document.getElementById('exp-nav-svg'); if(!svg)return;
  var lv=document.getElementById('exp-nav-lv');
  var idxs=expCk.length?expCk.slice(0,2):[(window.__expCur||0)];
  var cols=['#3D8BFF','#AB47BC'],h='';
  idxs.forEach(function(ri,k){
    var pts=expLine(ri),d='';
    pts.forEach(function(y,j){d+=(j?'L':'M')+(j*50)+','+Math.max(4,Math.min(155,y)).toFixed(0)+' ';});
    h+='<path d="'+d.trim()+'" fill="none" stroke="'+cols[k]+'" stroke-width="1.5"/>';
  });
  svg.innerHTML=h;
  if(lv)lv.innerHTML=idxs.map(function(ri,k){return '<span style="color:'+cols[k]+'">— '+expNames[ri]+'</span>';}).join(' ');
}
function expCkTgl(){
  expCk=[];
  document.querySelectorAll('.exp-ck').forEach(function(c){if(c.checked)expCk.push(+c.dataset.i);});
  if(expCk.length>2){
    var last=expCk[expCk.length-1];
    document.querySelectorAll('.exp-ck').forEach(function(c){c.checked=(+c.dataset.i===expCk[1]||+c.dataset.i===last);});
    expCk=[expCk[1],last];
  }
  expNavRender();
}
function expSel(i, el){
  document.querySelectorAll('.run-item').forEach(r=>r.classList.remove('on'));
  el.classList.add('on');
  window.__expCur=i;
  document.getElementById('exp-title').textContent=expNames[i]+' · 详情';
  expNavRender();
}

/* ==================== 指数详情页渲染引擎 v2（汇总主图+指标窗格；确定性模拟数据演示版式） ==================== */
var IDX_META={
  sh:{name:'上证指数（000001.SH）',price:'3,087.53',chg:'+0.72%',up:true,seed:101,base:3087.53,type:'index'},
  sz:{name:'深证成指（399001.SZ）',price:'9,741.20',chg:'+1.05%',up:true,seed:202,base:9741.20,type:'index'},
  cy:{name:'创业板指（399006.SZ）',price:'1,892.44',chg:'-0.31%',up:false,seed:303,base:1892.44,type:'index'},
  kc:{name:'科创综指（000680.SH）',price:'986.12',chg:'+1.48%',up:true,seed:404,base:986.12,type:'index'},
  '600519':{name:'贵州茅台（600519.SH）',price:'1,712.50',chg:'+0.86%',up:true,seed:519,base:1712.50,type:'stock'},
  '300750':{name:'宁德时代（300750.SZ）',price:'289.40',chg:'-1.24%',up:false,seed:750,base:289.40,type:'stock'},
  '688981':{name:'中芯国际（688981.SH）',price:'99.20',chg:'+2.35%',up:true,seed:981,base:99.20,type:'stock'}
};
var IDX_SHORT={sh:'上证指数',sz:'深证成指',cy:'创业板指',kc:'科创综指','600519':'贵州茅台','300750':'宁德时代','688981':'中芯国际'};
var PER_NAMES=['1分钟','5分钟','15分钟','30分钟','60分钟','120分钟','日线','周线','月线'];
var N_BARS=120;               /* 固定K线根数（Owner 裁定） */
var curIdx='sh', curPer=6;
var SVGNS='http://www.w3.org/2000/svg';
var OVL={ma:true,boll:true,frac:true,trend:true,sr:true,cost:true,volmark:true};
var PANES=['kdj'];            /* 默认一个 KDJ 窗格 */
/* 指标/形态目录：technical_indicator 注册表 41 指标（v0.9 全量接入真实计算渲染器）+ chart_pattern 注册表 256 形态（v2.0 第四批：pat 渲染器已接 206 条目/231 规则——CANDLE 77+CHART 62+TREND 13+SR 10+FIB 17+STRUCT 25+ELW 2；未接 50 条目=缠论 15[GAP-F-37]+数浪 6[wave-alpha]+ML 13+分时/订单流 16 负反馈；rsidiv 背离，目录 39 项全量接入） */
var IND_CAT=[
  {g:'趋势类',items:[
    {k:'ma',n:'简单移动平均 SMA',ok:1},{k:'ema',n:'指数移动平均 EMA',ok:1},{k:'wma',n:'加权移动平均 WMA',ok:1},{k:'dema',n:'双指数移动平均 DEMA',ok:1},{k:'macd',n:'异同移动平均 MACD',ok:1},{k:'adx',n:'平均趋向指数 ADX',ok:1},{k:'dmi',n:'趋向指标 DMI',ok:1},{k:'sar',n:'抛物线指标 SAR',ok:1},{k:'tema',n:'三重指数平滑平均 TEMA',ok:1}]},
  {g:'震荡类',items:[
    {k:'kdj',n:'随机指标 KDJ',ok:1},{k:'rsi',n:'相对强弱指标 RSI',ok:1},{k:'wr',n:'威廉指标 WR',ok:1},{k:'roc',n:'变动率 ROC',ok:1},{k:'mtm',n:'动量指标 MTM',ok:1},{k:'stochrsi',n:'随机RSI',ok:1},{k:'cmo',n:'钱德动量摆动 CMO',ok:1},{k:'uo',n:'终极指标 UO',ok:1},{k:'cci',n:'顺势指标 CCI',ok:1}]},
  {g:'波动类',items:[
    {k:'boll',n:'布林带 BOLL',ok:1},{k:'atr',n:'真实波幅 ATR',ok:1},{k:'kc',n:'肯特纳通道 KC',ok:1},{k:'dc',n:'唐奇安通道 DC',ok:1},{k:'std',n:'标准差 STD',ok:1},{k:'bollw',n:'布林带宽度',ok:1},{k:'bollb',n:'布林带%B',ok:1},{k:'hv',n:'历史波动率 HV',ok:1}]},
  {g:'量能类',items:[
    {k:'obv',n:'能量潮 OBV',ok:1},{k:'vol',n:'量价分析（天量/地量）',ok:1},{k:'mfi',n:'资金流量指标 MFI',ok:1},{k:'vwap',n:'成交量加权均价 VWAP',ok:1},{k:'vr',n:'容量比率 VR',ok:1},{k:'adl',n:'累积/派发线 ADL',ok:1},{k:'pvt',n:'价量趋势 PVT',ok:1},{k:'cmf',n:'蔡金资金流 CMF',ok:1},{k:'wvad',n:'威廉变异离散量 WVAD',ok:1}]},
  {g:'形态类',items:[
    {k:'frac',n:'顶/底分型',ok:1},{k:'candle',n:'K线形态识别（高频 20 种）',ok:1},{k:'rsidiv',n:'RSI背离',ok:1},{k:'pat',n:'经典形态库（注册表 256 · 已接 206 条目/231 规则）',ok:1}]}
];
var IND_NAME={};
IND_CAT.forEach(function(gr){gr.items.forEach(function(it){IND_NAME[it.k]=it.n;});});
var IND_INFO={
  ma:'简单移动平均 SMA20 · 价格与均线的相对位置是最基础的趋势滤镜',
  macd:'异同移动平均 MACD(12,26,9) · 快慢 EMA 差离值判断趋势动能，金叉买死叉卖',
  kdj:'随机指标 KDJ(9,3,3) · 收盘在近期高低区间的位置经平滑，J 值最灵敏；80 上超买、20 下超卖',
  rsi:'相对强弱指标 RSI(14) · 涨跌动能比率；>70 超买、<30 超卖',
  wr:'威廉指标 WR(14) · 与随机指标互补；<-80 超卖、>-20 超买',
  roc:'变动率 ROC(12) · N 日前价格变动百分比，正负切换反映动能方向',
  mtm:'动量指标 MTM(12) · N 日价格差，零轴上下定强弱',
  boll:'布林带 BOLL(20,2) · 中轨±2 倍标准差通道；触上轨警惕、触下轨关注',
  atr:'真实波幅 ATR(14) · 波动率度量，不产生方向信号（无买卖点即负反馈）',
  obv:'能量潮 OBV · 成交量随涨跌累积；量价同向健康、背离警告',
  vol:'量价分析 · 天量天价/地量地价的传统主观量价框架',
  frac:'顶/底分型 · 3 根K线定义的局部转折结构（缠论基础构件）',
  ema:'指数移动平均 EMA(20) · 近期价格权重更高的均线，比 SMA 更快反映转向；线上持多、线下持空',
  wma:'加权移动平均 WMA(20) · 线性加权均线，越近权重越大；线上偏多、线下偏空',
  dema:'双指数移动平均 DEMA(20)=2×EMA−EMA(EMA) · 削减 EMA 滞后更贴价格；线上偏多、线下偏空',
  tema:'三重指数平滑平均 TEMA(20)=3EMA−3EMA(EMA)+EMA(EMA(EMA)) · 进一步消滞后，趋势跟踪更紧；线上偏多、线下偏空',
  sar:'抛物线指标 SAR(0.02,0.2) · 止损反转点列；点在价下持多、价上持空，翻转即转向',
  adx:'平均趋向指数 ADX(14) · 只量趋势强度不分方向；>25 趋势确立、<20 无趋势',
  dmi:'趋向指标 DMI(14) · +DI/-DI 双线定方向、ADX 辅助确认；金叉买、死叉卖',
  cci:'顺势指标 CCI(14) · 典型价对均值的偏离度；+100 上超买、-100 下超卖',
  stochrsi:'随机RSI StochRSI(14,3,3) · RSI 再作随机化，对超买超卖更灵敏；80 上超买、20 下超卖',
  cmo:'钱德动量摆动 CMO(14) · 涨跌净额占涨跌总额比；-100~+100，±50 极值、零轴定多空',
  uo:'终极指标 UO(7,14,28) · 三周期买入压力加权合成；70 上超买、30 下超卖',
  kc:'肯特纳通道 KC(20,2×ATR14) · EMA 中轨±2 倍 ATR 通道；触上轨警惕、触下轨关注（叠加 K 线）',
  dc:'唐奇安通道 DC(20) · 20 根最高/最低价围成通道；突破上轨强势、跌破下轨转弱（叠加 K 线）',
  std:'标准差 STD(20) · 收盘价 20 根离散度，纯波动度量（无方向信号）',
  bollw:'布林带宽度 BOLLW(20,2) · (上轨-下轨)/中轨×100；带宽挤压至极低分位预示变盘（无方向信号）',
  bollb:'布林带%B BOLLB(20,2) · 价格在通道中的相对位置；>1 超上轨、<0 破下轨',
  hv:'历史波动率 HV(20) · 日收益对数标准差×√252 年化，纯波动度量（无方向信号）',
  mfi:'资金流量指标 MFI(14) · 典型价×量的资金流比率（量加强版 RSI）；>80 超买、<20 超卖',
  vwap:'成交量加权均价 VWAP（窗口锚定口径）· 收盘在 VWAP 上方偏多、下方偏空',
  vr:'容量比率 VR(26) · 上涨量与下跌量之比；<70 低价区、>150 警戒、>350 过热',
  adl:'累积/派发线 ADL · CLV 加权量累积；量价同向健康、背离警告',
  pvt:'价量趋势 PVT · 价格变动率×量累积；与 ADL 同做量价背离判读',
  cmf:'蔡金资金流 CMF(20) · 零轴上资金净流入、下净流出，±0.1 加强',
  wvad:'威廉变异离散量 WVAD · 实体占波幅比×量，零轴柱 + MA6 上穿零轴判多空',
  candle:'K线形态识别 · 20 种高频经典形态：锤子线/上吊线/倒锤子线/射击之星/十字星/墓碑十字/大阳线/大阴线/看涨吞没/看跌吞没/刺透线/乌云盖顶/看涨孕线/看跌孕线/镊子底/镊子顶/启明星/黄昏星/红三兵/三只乌鸦（chart_pattern 注册表子集）',
  rsidiv:'RSI背离 · RSI(14) 摆动点配对检测：价格新高而 RSI 未新高=顶背离（卖出偏向）、价格新低而 RSI 未新低=底背离（买入偏向）',
  pat:'经典形态库 · chart_pattern 注册表 256 条目已接 206/规则 231：CANDLE 77 全覆（K线 20 高频+扩展 15+持续/三根族 16+余项 49：搓揉线/天地板/地天板/一阳穿多线/关键反转日/塔形顶底 等）+ CHART 62 全覆（经典 14+西方 30：杯柄/圆弧/V形/沃尔夫浪/卡西莫多/复合头肩/缺口四型 等 + A股特色 20：反包涨停/黄金坑/连板/TD 序列/老鸭头/空中加油 等）+ TREND 13（趋势线/通道/音叉/江恩/速度线）+ SR 10（枢轴点四族/VPVR/穆雷/昨日高低）+ FIB 17（回撤/扩展/共振簇+谐波 11 种）+ STRUCT 25（威科夫 8/SMC 8/VSA 7/供需区）+ ELW 2（引导/终结楔形）；未接 50 条目=缠论 15（GAP-F-37 后端裁定）+数浪 6（wave-alpha 后端）+ML 13+分时/订单流 16——负反馈待接入；zigzag 斜率+区间收益+比率容差口径，全部出现位置同时标注'
};

function lcg(seed){var s=seed>>>0||1;return function(){s=(s*1103515245+12345)%2147483648;return s/2147483648;};}
function genCandles(seed,nb){
  var r=lcg(seed), n=nb||N_BARS, price=100, arr=[];
  var u=n/120;   /* 趋势分段按长度等比缩放（四.A 周/月 240 根可达；既有调用 genCandles(seed) 不受影响） */
  var segs=[[0,Math.round(36*u),0.55],[Math.round(36*u),Math.round(62*u),-0.5],[Math.round(62*u),Math.round(94*u),0.04],[Math.round(94*u),n,0.5]];
  for(var i=0;i<n;i++){
    var tr=0; for(var s=0;s<segs.length;s++){ if(i>=segs[s][0]&&i<segs[s][1]) tr=segs[s][2]; }
    var o=price, c=o+tr+(r()-0.5)*2.4;
    var h=Math.max(o,c)+r()*1.2, l=Math.min(o,c)-r()*1.2;
    arr.push({o:o,c:c,h:h,l:l,v:50+r()*60+Math.abs(tr)*40}); price=c;
  }
  /* 注入量能脉冲/枯竭（保证天量/地量标注路径可达；位置随 seed 确定性变化；%n 防 nb<120 时越界——币圈 sparkline genCandles(seed,40) 场景） */
  arr[(30+seed%15)%n].v*=3.1;
  arr[(75+seed%10)%n].v*=3.0;
  arr[(50+seed%8)%n].v*=0.25;
  return arr;
}
function rangeOf(d){var lo=1e9,hi=-1e9;d.forEach(function(k){lo=Math.min(lo,k.l);hi=Math.max(hi,k.h);});var pad=(hi-lo)*0.12;return[lo-pad,hi+pad];}
function ma(d,n,i){if(i<n-1)return null;var s=0;for(var j=i-n+1;j<=i;j++)s+=d[j].c;return s/n;}
function emaArr(vals,n){var a=2/(n+1),out=[],e=vals[0];for(var i=0;i<vals.length;i++){e=(i===0)?vals[i]:a*vals[i]+(1-a)*e;out.push(e);}return out;}
function kdjCalc(d){
  var K=[],D=[],J=[],k=50,dd=50;
  for(var i=0;i<d.length;i++){
    var s=Math.max(0,i-8),hh=-1e9,ll=1e9;
    for(var j=s;j<=i;j++){hh=Math.max(hh,d[j].h);ll=Math.min(ll,d[j].l);}
    var rsv=hh>ll?(d[i].c-ll)/(hh-ll)*100:50;
    k=2/3*k+1/3*rsv; dd=2/3*dd+1/3*k;
    K.push(k);D.push(dd);J.push(3*k-2*dd);
  }
  return[K,D,J];
}
function macdCalc(d){
  var c=d.map(function(k){return k.c;});
  var e12=emaArr(c,12),e26=emaArr(c,26);
  var dif=c.map(function(_,i){return e12[i]-e26[i];});
  var dea=emaArr(dif,9);
  var hist=dif.map(function(v,i){return (v-dea[i])*2;});
  return[dif,dea,hist];
}
function fractals(d){
  var tops=[],bots=[];
  for(var i=1;i<d.length-1;i++){
    if(d[i].h>d[i-1].h&&d[i].h>d[i+1].h&&d[i].l>d[i-1].l&&d[i].l>d[i+1].l) tops.push(i);
    if(d[i].l<d[i-1].l&&d[i].l<d[i+1].l&&d[i].h<d[i-1].h&&d[i].h<d[i+1].h) bots.push(i);
  }
  return{tops:tops,bots:bots};
}
/* ---- 追加指标计算（注册表常用项真实公式） ---- */
function rsiCalc(d,n){
  var up=0,dn=0,out=[];
  for(var i=0;i<d.length;i++){
    if(i===0){out.push(50);continue;}
    var ch=d[i].c-d[i-1].c;
    up=(up*(n-1)+Math.max(ch,0))/n; dn=(dn*(n-1)+Math.max(-ch,0))/n;
    out.push(dn===0?100:100-100/(1+up/dn));
  }
  return out;
}
function wrCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    var s=Math.max(0,i-n+1),hh=-1e9,ll=1e9;
    for(var j=s;j<=i;j++){hh=Math.max(hh,d[j].h);ll=Math.min(ll,d[j].l);}
    out.push(hh>ll?(hh-d[i].c)/(hh-ll)*(-100):-50);
  }
  return out;
}
function rocCalc(d,n){ return d.map(function(k,i){ return i>=n?(k.c/d[i-n].c-1)*100:0; }); }
function mtmCalc(d,n){ return d.map(function(k,i){ return i>=n?k.c-d[i-n].c:0; }); }
function obvCalc(d){
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    if(i===0){acc=d[i].v;}
    else if(d[i].c>d[i-1].c) acc+=d[i].v;
    else if(d[i].c<d[i-1].c) acc-=d[i].v;
    out.push(acc);
  }
  return out;
}
function atrCalc(d,n){
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    var tr=i===0?d[i].h-d[i].l:Math.max(d[i].h-d[i].l,Math.abs(d[i].h-d[i-1].c),Math.abs(d[i].l-d[i-1].c));
    acc=i<n?acc+tr/n:(acc*(n-1)+tr)/n;
    out.push(acc);
  }
  return out;
}
function candlePats(d){
  var found=[];
  for(var i=2;i<d.length;i++){
    var a=d[i-2],b=d[i-1],c=d[i];
    var body=Math.abs(c.c-c.o),range=c.h-c.l,upSh=c.h-Math.max(c.o,c.c),dnSh=Math.min(c.o,c.c)-c.l;
    if(range>0&&body/range<0.1) found.push({i:i,n:'十字星',dir:0});
    if(dnSh>2*body&&upSh<=body&&c.c>b.c) found.push({i:i,n:'锤子线',dir:1});
    if(b.c<b.o&&c.c>c.o&&c.c>=b.o&&c.o<=b.c) found.push({i:i,n:'看涨吞没',dir:1});
    if(b.c>b.o&&c.c<c.o&&c.c<=b.o&&c.o>=b.c) found.push({i:i,n:'看跌吞没',dir:-1});
    if(a.c<a.o&&Math.abs(b.c-b.o)<(a.o-a.c)*0.4&&c.c>c.o&&c.c>(a.o+a.c)/2) found.push({i:i,n:'启明星',dir:1});
    if(a.c>a.o&&Math.abs(b.c-b.o)<(a.c-a.o)*0.4&&c.c<c.o&&c.c<(a.o+a.c)/2) found.push({i:i,n:'黄昏星',dir:-1});
  }
  return found;
}
/* ---- I-1a 趋势类计算（7 项：wma/dema/tema/sar/dmi/adx） ---- */
function wmaArr(vals,n){
  var out=[],den=n*(n+1)/2;
  for(var i=0;i<vals.length;i++){
    if(i<n-1){out.push(null);continue;}
    var s=0; for(var j=0;j<n;j++) s+=vals[i-n+1+j]*(j+1);
    out.push(s/den);
  }
  return out;
}
function demaArr(vals,n){
  var e1=emaArr(vals,n),e2=emaArr(e1,n),out=[];
  for(var i=0;i<vals.length;i++) out.push(i<2*(n-1)?null:2*e1[i]-e2[i]);
  return out;
}
function temaArr(vals,n){
  var e1=emaArr(vals,n),e2=emaArr(e1,n),e3=emaArr(e2,n),out=[];
  for(var i=0;i<vals.length;i++) out.push(i<3*(n-1)?null:3*e1[i]-3*e2[i]+e3[i]);
  return out;
}
function sarCalc(d,step,mx){
  var out=[];
  for(var z=0;z<d.length;z++) out.push(null);
  if(d.length<3) return out;
  var up=d[2].c>=d[0].c;                                  /* 初始趋势：第3根收盘相对首根 */
  var sar=up?Math.min(d[0].l,d[1].l):Math.max(d[0].h,d[1].h);
  var ep=up?Math.max(d[0].h,d[1].h,d[2].h):Math.min(d[0].l,d[1].l,d[2].l);
  var af=step;
  out[2]=sar;
  for(var i=3;i<d.length;i++){
    sar=sar+af*(ep-sar);
    if(up){
      if(sar>d[i-1].l) sar=d[i-1].l;                      /* SAR 不得进入前两根低点之上 */
      if(sar>d[i-2].l) sar=d[i-2].l;
      if(d[i].h>ep){ep=d[i].h;af=Math.min(af+step,mx);}
      if(d[i].l<sar){up=false;sar=ep;ep=d[i].l;af=step;}  /* 下穿翻转：SAR 跳到前 EP */
    }else{
      if(sar<d[i-1].h) sar=d[i-1].h;
      if(sar<d[i-2].h) sar=d[i-2].h;
      if(d[i].l<ep){ep=d[i].l;af=Math.min(af+step,mx);}
      if(d[i].h>sar){up=true;sar=ep;ep=d[i].h;af=step;}
    }
    out[i]=sar;
  }
  return out;
}
function dmiCalc(d,n){
  /* Wilder 平滑：+DI/-DI 自第 n 根起有值，ADX 自第 2n-1 根起有值，之前填 null */
  var len=d.length,pdi=[],mdi=[],adx=[];
  for(var z=0;z<len;z++){pdi.push(null);mdi.push(null);adx.push(null);}
  var sTR=0,sP=0,sM=0,dxs=[],adxV=null;
  for(var i=1;i<len;i++){
    var up=d[i].h-d[i-1].h,dn=d[i-1].l-d[i].l;
    var pdm=(up>dn&&up>0)?up:0, mdm=(dn>up&&dn>0)?dn:0;
    var tr=Math.max(d[i].h-d[i].l,Math.abs(d[i].h-d[i-1].c),Math.abs(d[i].l-d[i-1].c));
    if(i<=n){sTR+=tr;sP+=pdm;sM+=mdm;}
    else{sTR=sTR-sTR/n+tr;sP=sP-sP/n+pdm;sM=sM-sM/n+mdm;}
    if(i>=n){
      var pi=sTR>0?100*sP/sTR:0, mi=sTR>0?100*sM/sTR:0;
      pdi[i]=pi; mdi[i]=mi;
      var dx=(pi+mi)>0?100*Math.abs(pi-mi)/(pi+mi):0;
      if(adxV===null){
        dxs.push(dx);
        if(dxs.length===n){var s=0;for(var q=0;q<n;q++)s+=dxs[q];adxV=s/n;adx[i]=adxV;}
      }else{
        adxV=(adxV*(n-1)+dx)/n; adx[i]=adxV;
      }
    }
  }
  return [pdi,mdi,adx];
}
function adxCalc(d,n){ return dmiCalc(d,n)[2]; }
/* ---- I-1b/I-1c 震荡+波动类计算（10 项） ---- */
function cciCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n-1){out.push(null);continue;}
    var s=0;
    for(var j=i-n+1;j<=i;j++) s+=(d[j].h+d[j].l+d[j].c)/3;
    var mtp=s/n, md=0;
    for(var j2=i-n+1;j2<=i;j2++) md+=Math.abs((d[j2].h+d[j2].l+d[j2].c)/3-mtp);
    md/=n;
    var tp=(d[i].h+d[i].l+d[i].c)/3;
    out.push(md===0?0:(tp-mtp)/(0.015*md));
  }
  return out;
}
function stochRsiCalc(d,n){          /* StochRSI(n,3,3)，复用 rsiCalc（自 0 起有值） */
  var RS=rsiCalc(d,n),raw=[],K=[],D=[];
  var i,j;
  for(i=0;i<d.length;i++){
    if(i<n-1){raw.push(null);continue;}
    var hh=-1e9,ll=1e9;
    for(j=i-n+1;j<=i;j++){hh=Math.max(hh,RS[j]);ll=Math.min(ll,RS[j]);}
    raw.push(hh>ll?(RS[i]-ll)/(hh-ll)*100:50);
  }
  for(i=0;i<d.length;i++){
    if(i<n+1){K.push(null);continue;}      /* %K=SMA3(raw)，需 i>=n-1+2 */
    K.push((raw[i]+raw[i-1]+raw[i-2])/3);
  }
  for(i=0;i<d.length;i++){
    if(i<n+3){D.push(null);continue;}      /* %D=SMA3(%K) */
    D.push((K[i]+K[i-1]+K[i-2])/3);
  }
  return [K,D];
}
function cmoCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n){out.push(null);continue;}
    var su=0,sd=0;
    for(var j=i-n+1;j<=i;j++){
      var ch=d[j].c-d[j-1].c;
      if(ch>0)su+=ch;else sd-=ch;
    }
    out.push(su+sd===0?0:100*(su-sd)/(su+sd));
  }
  return out;
}
function uoCalc(d){                   /* UO(7,14,28)，周期按任务裁定硬编码 */
  var bp=[],tr=[];
  for(var i=0;i<d.length;i++){
    var pc=i===0?d[i].o:d[i-1].c;
    bp.push(d[i].c-Math.min(d[i].l,pc));
    tr.push(Math.max(d[i].h,pc)-Math.min(d[i].l,pc));
  }
  var out=[];
  for(var i2=0;i2<d.length;i2++){
    if(i2<28){out.push(null);continue;}
    var b7=0,t7=0,b14=0,t14=0,b28=0,t28=0;
    for(var j2=i2-6;j2<=i2;j2++){b7+=bp[j2];t7+=tr[j2];}
    for(var j3=i2-13;j3<=i2;j3++){b14+=bp[j3];t14+=tr[j3];}
    for(var j4=i2-27;j4<=i2;j4++){b28+=bp[j4];t28+=tr[j4];}
    var r7=t7===0?0:b7/t7, r14=t14===0?0:b14/t14, r28=t28===0?0:b28/t28;
    out.push(100*(4*r7+2*r14+r28)/7);
  }
  return out;
}
function kcCalc(d){                   /* 中轨=EMA20（emaArr 自 0 起有值），轨=中轨±2×ATR(14) */
  var c=d.map(function(k){return k.c;});
  var mid=emaArr(c,20), at=atrCalc(d,14), up=[], low=[];
  for(var i=0;i<d.length;i++){up.push(mid[i]+2*at[i]);low.push(mid[i]-2*at[i]);}
  return [up,mid,low];
}
function dcCalc(d,n){                 /* 窗口含当前根（与 ma/boll 分支口径一致），短窗用部分窗口 */
  var up=[],mid=[],low=[];
  for(var i=0;i<d.length;i++){
    var s=Math.max(0,i-n+1),hh=-1e9,ll=1e9;
    for(var j=s;j<=i;j++){hh=Math.max(hh,d[j].h);ll=Math.min(ll,d[j].l);}
    up.push(hh);low.push(ll);mid.push((hh+ll)/2);
  }
  return [up,mid,low];
}
function stdCalc(d,n){
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n-1){out.push(null);continue;}
    var m=ma(d,n,i),sd=0;
    for(var j=i-n+1;j<=i;j++)sd+=(d[j].c-m)*(d[j].c-m);
    out.push(Math.sqrt(sd/n));
  }
  return out;
}
function bollBands(d,n,k){            /* bollw/bollb 共用；口径与 boll 分支一致（ma 前 19 根为 null） */
  var up=[],mid=[],low=[];
  for(var i=0;i<d.length;i++){
    var m=ma(d,n,i);
    if(m===null){up.push(null);mid.push(null);low.push(null);continue;}
    var sd=0;
    for(var j=i-n+1;j<=i;j++)sd+=(d[j].c-m)*(d[j].c-m);
    sd=Math.sqrt(sd/n);
    up.push(m+k*sd);mid.push(m);low.push(m-k*sd);
  }
  return [up,mid,low];
}
function bollwCalc(d,n,k){
  var BB=bollBands(d,n,k),out=[];
  for(var i=0;i<d.length;i++){
    out.push(BB[0][i]===null?null:(BB[0][i]-BB[2][i])/BB[1][i]*100);
  }
  return out;
}
function bollbCalc(d,n,k){
  var BB=bollBands(d,n,k),out=[];
  for(var i=0;i<d.length;i++){
    if(BB[0][i]===null){out.push(null);continue;}
    var den=BB[0][i]-BB[2][i];
    out.push(den===0?0.5:(d[i].c-BB[2][i])/den);
  }
  return out;
}
function hvCalc(d,n){                 /* 日收益对数标准差×√252 年化，输出百分数 */
  var r=[null];
  for(var i=1;i<d.length;i++) r.push(Math.log(d[i].c/d[i-1].c));
  var out=[];
  for(var i2=0;i2<d.length;i2++){
    if(i2<n){out.push(null);continue;}
    var m=0;
    for(var j=i2-n+1;j<=i2;j++)m+=r[j];
    m/=n;
    var sd=0;
    for(var j2=i2-n+1;j2<=i2;j2++)sd+=(r[j2]-m)*(r[j2]-m);
    out.push(Math.sqrt(sd/n)*Math.sqrt(252)*100);
  }
  return out;
}
/* ---- I-1d 量能类计算（7 项） ---- */
function mfiCalc(d,n){                 /* MFI(n)：典型价资金流比率，0~100；前 n 根 null */
  var tp=[],i;
  for(i=0;i<d.length;i++) tp.push((d[i].h+d[i].l+d[i].c)/3);
  var out=[];
  for(i=0;i<d.length;i++){
    if(i<n){out.push(null);continue;}
    var pos=0,neg=0;
    for(var j=i-n+1;j<=i;j++){
      var rmf=tp[j]*d[j].v;
      if(tp[j]>tp[j-1]) pos+=rmf;
      else if(tp[j]<tp[j-1]) neg+=rmf;
    }
    out.push(neg===0?100:100-100/(1+pos/neg));
  }
  return out;
}
function vwapCalc(d){                  /* 窗口锚定 VWAP：从第 0 根累计 ΣTP·V/ΣV */
  var out=[],tpv=0,sv=0;
  for(var i=0;i<d.length;i++){
    var k=d[i],tp=(k.h+k.l+k.c)/3;
    tpv+=tp*k.v; sv+=k.v;
    out.push(sv===0?tp:tpv/sv);
  }
  return out;
}
function vrCalc(d,n){                  /* VR(n)：(涨量+平量/2)/(跌量+平量/2)×100；前 n 根 null */
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n){out.push(null);continue;}
    var up=0,dn=0,fl=0;
    for(var j=i-n+1;j<=i;j++){
      if(d[j].c>d[j-1].c) up+=d[j].v;
      else if(d[j].c<d[j-1].c) dn+=d[j].v;
      else fl+=d[j].v;
    }
    var den=dn+fl/2;
    out.push(den===0?200:(up+fl/2)/den*100);
  }
  return out;
}
function adlCalc(d){                   /* ADL：累计 ΣCLV×v，h=l 时 CLV=0 */
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    var k=d[i],rg=k.h-k.l;
    var clv=rg>0?((k.c-k.l)-(k.h-k.c))/rg:0;
    acc+=clv*k.v; out.push(acc);
  }
  return out;
}
function pvtCalc(d){                   /* PVT：累计 Σ((c-c_prev)/c_prev)×v */
  var out=[],acc=0;
  for(var i=0;i<d.length;i++){
    if(i>0&&d[i-1].c!==0) acc+=(d[i].c-d[i-1].c)/d[i-1].c*d[i].v;
    out.push(acc);
  }
  return out;
}
function cmfCalc(d,n){                 /* CMF(n)：滚动 Σ(CLV×v)/Σv；前 n-1 根 null */
  var out=[];
  for(var i=0;i<d.length;i++){
    if(i<n-1){out.push(null);continue;}
    var sv=0,scv=0;
    for(var j=i-n+1;j<=i;j++){
      var k=d[j],rg=k.h-k.l;
      var clv=rg>0?((k.c-k.l)-(k.h-k.c))/rg:0;
      scv+=clv*k.v; sv+=k.v;
    }
    out.push(sv===0?0:scv/sv);
  }
  return out;
}
function wvadCalc(d,n){                /* WVAD：(c-o)/(h-l)×v（h=l 时 0）+ n 根均线；返回 [WV,MA] */
  var WV=[],WM=[];
  for(var i=0;i<d.length;i++){
    var k=d[i],rg=k.h-k.l;
    WV.push(rg>0?(k.c-k.o)/rg*k.v:0);
  }
  for(i=0;i<d.length;i++){
    if(i<n-1){WM.push(null);continue;}
    var s=0; for(var j=i-n+1;j<=i;j++) s+=WV[j];
    WM.push(s/n);
  }
  return[WV,WM];
}
/* ---- I-1e K线形态识别 20 种扩容版（chart_pattern 注册表 18 条目/20 规则；旧 candlePats 保留供回滚） ---- */
function candlePats20(d){
  var n=d.length,found=[],i;
  var avgB=0;
  for(i=0;i<n;i++) avgB+=Math.abs(d[i].c-d[i].o);
  avgB=n?avgB/n:1; if(avgB<=0) avgB=1e-9;   /* 全序列均实体：「大实体/容差」统一基准 */
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}   /* 前5根涨跌幅：区分趋势段与震荡段 */
  /* ---- 单根类 8 ---- */
  function isHammer(i){var p=an(d[i]);return r5(i)<=-0.01&&p.d>=1.8*p.b&&p.u<=p.b&&p.d>=0.45*p.r;}
  function isHangMan(i){var p=an(d[i]);return r5(i)>=0.01&&p.d>=1.8*p.b&&p.u<=p.b&&p.d>=0.45*p.r;}
  function isInvHammer(i){var p=an(d[i]);return r5(i)<=-0.01&&p.u>=1.8*p.b&&p.d<=p.b&&p.u>=0.45*p.r;}
  function isShootStar(i){var p=an(d[i]);return r5(i)>=0.01&&p.u>=1.8*p.b&&p.d<=p.b&&p.u>=0.45*p.r;}
  function isDoji(i){var p=an(d[i]);return p.b/p.r<=0.1;}
  function isGravestone(i){var p=an(d[i]);return p.b/p.r<=0.1&&p.d/p.r<=0.1&&p.u/p.r>=0.6;}
  function isBigYang(i){var p=an(d[i]);return d[i].c>d[i].o&&p.b>=avgB&&p.u<=0.2*p.r&&p.d<=0.2*p.r;}
  function isBigYin(i){var p=an(d[i]);return d[i].c<d[i].o&&p.b>=avgB&&p.u<=0.2*p.r&&p.d<=0.2*p.r;}
  /* ---- 双根类 8 ---- */
  function isBullEngulf(i){var b=d[i-1],c=d[i];return b.c<b.o&&Math.abs(b.c-b.o)>=0.4*avgB&&c.c>c.o&&c.c>=b.o&&c.o<=b.c;}
  function isBearEngulf(i){var b=d[i-1],c=d[i];return b.c>b.o&&Math.abs(b.c-b.o)>=0.4*avgB&&c.c<c.o&&c.c<=b.o&&c.o>=b.c;}
  function isPiercing(i){var b=d[i-1],c=d[i];return b.c<b.o&&Math.abs(b.c-b.o)>=0.5*avgB&&c.c>c.o&&c.o<=b.c&&c.c>(b.o+b.c)/2&&c.c<b.o;}
  function isDarkCloud(i){var b=d[i-1],c=d[i];return b.c>b.o&&Math.abs(b.c-b.o)>=0.5*avgB&&c.c<c.o&&c.o>=b.c&&c.c<(b.o+b.c)/2&&c.c>b.o;}
  function isBullHarami(i){var b=d[i-1],c=d[i],bb=Math.abs(b.c-b.o),cb=Math.abs(c.c-c.o);return r5(i)<=-0.01&&b.c<b.o&&bb>=0.8*avgB&&cb<=0.6*bb&&Math.max(c.o,c.c)<=b.o&&Math.min(c.o,c.c)>=b.c;}
  function isBearHarami(i){var b=d[i-1],c=d[i],bb=Math.abs(b.c-b.o),cb=Math.abs(c.c-c.o);return r5(i)>=0.01&&b.c>b.o&&bb>=0.8*avgB&&cb<=0.6*bb&&Math.max(c.o,c.c)<=b.c&&Math.min(c.o,c.c)>=b.o;}
  function isTweezerBot(i){
    if(r5(i)>-0.01)return false;
    var p=an(d[i]),tol=0.3*avgB;
    for(var j=Math.max(1,i-3);j<i;j++){var q=an(d[j]);if(Math.abs(d[i].l-d[j].l)<=tol&&q.d>=0.3*q.r&&p.d>=0.3*p.r)return true;}
    return false;
  }
  function isTweezerTop(i){
    if(r5(i)<0.01)return false;
    var p=an(d[i]),tol=0.3*avgB;
    for(var j=Math.max(1,i-3);j<i;j++){var q=an(d[j]);if(Math.abs(d[i].h-d[j].h)<=tol&&q.u>=0.3*q.r&&p.u>=0.3*p.r)return true;}
    return false;
  }
  /* ---- 三根类 4 ---- */
  function isMorningStar(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c<a.o&&Math.abs(b.c-b.o)<(a.o-a.c)*0.4&&c.c>c.o&&c.c>(a.o+a.c)/2;}
  function isEveningStar(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c>a.o&&Math.abs(b.c-b.o)<(a.c-a.o)*0.4&&c.c<c.o&&c.c<(a.o+a.c)/2;}
  function isThreeWhite(i){
    var a=d[i-2],b=d[i-1],c=d[i];
    return a.c>a.o&&b.c>b.o&&c.c>c.o&&b.c>a.c&&c.c>b.c
      &&Math.abs(a.c-a.o)>=0.5*avgB&&Math.abs(b.c-b.o)>=0.5*avgB&&Math.abs(c.c-c.o)>=0.5*avgB
      &&a.o>0&&(c.c-a.o)/a.o>=0.012;
  }
  function isThreeCrows(i){
    var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&c.c<c.o&&b.c<a.c&&c.c<b.c
      &&Math.abs(a.c-a.o)>=0.5*avgB&&Math.abs(b.c-b.o)>=0.5*avgB&&Math.abs(c.c-c.o)>=0.5*avgB
      &&a.o>0&&(a.o-c.c)/a.o>=0.012;
  }
  for(i=2;i<n;i++){
    if(isHammer(i)) found.push({i:i,n:'锤子线',dir:1});
    if(isHangMan(i)) found.push({i:i,n:'上吊线',dir:-1});
    if(isInvHammer(i)) found.push({i:i,n:'倒锤子线',dir:1});
    if(isShootStar(i)) found.push({i:i,n:'射击之星',dir:-1});
    if(isDoji(i)) found.push({i:i,n:'十字星',dir:0});
    if(isGravestone(i)) found.push({i:i,n:'墓碑十字',dir:-1});
    if(isBigYang(i)) found.push({i:i,n:'大阳线',dir:1});
    if(isBigYin(i)) found.push({i:i,n:'大阴线',dir:-1});
    if(isBullEngulf(i)) found.push({i:i,n:'看涨吞没',dir:1});
    if(isBearEngulf(i)) found.push({i:i,n:'看跌吞没',dir:-1});
    if(isPiercing(i)) found.push({i:i,n:'刺透线',dir:1});
    if(isDarkCloud(i)) found.push({i:i,n:'乌云盖顶',dir:-1});
    if(isBullHarami(i)) found.push({i:i,n:'看涨孕线',dir:1});
    if(isBearHarami(i)) found.push({i:i,n:'看跌孕线',dir:-1});
    if(isTweezerBot(i)) found.push({i:i,n:'镊子底',dir:1});
    if(isTweezerTop(i)) found.push({i:i,n:'镊子顶',dir:-1});
    if(isMorningStar(i)) found.push({i:i,n:'启明星',dir:1});
    if(isEveningStar(i)) found.push({i:i,n:'黄昏星',dir:-1});
    if(isThreeWhite(i)) found.push({i:i,n:'红三兵',dir:1});
    if(isThreeCrows(i)) found.push({i:i,n:'三只乌鸦',dir:-1});
  }
  return found;
}
/* ---- I-1 后续子批：RSI 背离检测（摆动点配对：价格峰谷 × RSI 峰谷） ---- */
function rsiDivergence(d,RS){
  var n=d.length,pk=[],vl=[],i,j;
  for(i=2;i<n-2;i++){   /* 窗口 2 的收盘价摆动点 */
    if(d[i].c>=d[i-1].c&&d[i].c>=d[i-2].c&&d[i].c>=d[i+1].c&&d[i].c>=d[i+2].c) pk.push(i);
    if(d[i].c<=d[i-1].c&&d[i].c<=d[i-2].c&&d[i].c<=d[i+1].c&&d[i].c<=d[i+2].c) vl.push(i);
  }
  var out=[];
  for(j=1;j<pk.length;j++){   /* 峰对峰：价格新高 + RSI 走低 = 顶背离 */
    var a=pk[j-1],b=pk[j];
    if(b-a<5) continue;
    if(d[b].c>d[a].c&&RS[b]<RS[a]-2) out.push({i1:a,i2:b,dir:-1,n:'顶背离'});
  }
  for(j=1;j<vl.length;j++){   /* 谷对谷：价格新低 + RSI 走高 = 底背离 */
    var a2=vl[j-1],b2=vl[j];
    if(b2-a2<5) continue;
    if(d[b2].c<d[a2].c&&RS[b2]>RS[a2]+2) out.push({i1:a2,i2:b2,dir:1,n:'底背离'});
  }
  return out;
}
/* ---- I-1 后续子批：经典形态库扩展批（19 规则，叠加在 candlePats20 之上；pat 渲染器=39 规则合集） ---- */
function patExt(d){
  var n=d.length,found=[],i;
  var avgB=0,avgR=0;
  for(i=0;i<n;i++){avgB+=Math.abs(d[i].c-d[i].o);avgR+=(d[i].h-d[i].l);}
  avgB=n?avgB/n:1; avgR=n?avgR/n:1; if(avgB<=0)avgB=1e-9; if(avgR<=0)avgR=1e-9;
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}
  /* ---- 单根类 7 ---- */
  function isDragonfly(i){var p=an(d[i]);return p.b/p.r<=0.1&&p.u/p.r<=0.1&&p.d/p.r>=0.6;}
  function isLongLeg(i){var p=an(d[i]);return p.b/p.r<=0.15&&p.u/p.r>=0.35&&p.d/p.r>=0.35;}
  function isSpinTop(i){var p=an(d[i]);return p.b/p.r<=0.35&&p.b<=0.6*avgB&&p.u>=0.5*p.b&&p.d>=0.5*p.b&&p.u>=0.15*p.r&&p.d>=0.15*p.r;}
  function isHighWave(i){var p=an(d[i]);return p.b/p.r<=0.2&&p.r>=1.8*avgR&&p.u>=p.b&&p.d>=p.b;}
  function isRickshaw(i){var p=an(d[i]);return p.b/p.r<=0.1&&p.u/p.r>=0.3&&p.d/p.r>=0.3;}
  function isBeltBull(i){var p=an(d[i]);return d[i].c>d[i].o&&p.d<=0.05*p.r&&p.b>=avgB&&r5(i)<=-0.01;}
  function isBeltBear(i){var p=an(d[i]);return d[i].c<d[i].o&&p.u<=0.05*p.r&&p.b>=avgB&&r5(i)>=0.01;}
  /* ---- 双根类 4 ---- */
  function isHaramiCrossBull(i){var b=d[i-1],c=d[i],bb=b.o-b.c,cp=an(c);return r5(i)<=-0.01&&b.c<b.o&&bb>=0.8*avgB&&cp.b/cp.r<=0.1&&c.h<=b.o&&c.l>=b.c;}
  function isHaramiCrossBear(i){var b=d[i-1],c=d[i],bb=b.c-b.o,cp=an(c);return r5(i)>=0.01&&b.c>b.o&&bb>=0.8*avgB&&cp.b/cp.r<=0.1&&c.h<=b.c&&c.l>=b.o;}
  function isCounterBull(i){var b=d[i-1],c=d[i];return r5(i)<=-0.01&&b.c<b.o&&c.c>c.o&&Math.abs(c.c-b.c)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  function isCounterBear(i){var b=d[i-1],c=d[i];return r5(i)>=0.01&&b.c>b.o&&c.c<c.o&&Math.abs(c.c-b.c)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  /* ---- 三根类 4 ---- */
  function isMorningDoji(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c<a.o&&(a.o-a.c)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.c<a.c&&c.c>c.o&&c.c>(a.o+a.c)/2;}
  function isEveningDoji(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c>a.o&&(a.c-a.o)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.c>a.c&&c.c<c.o&&c.c<(a.o+a.c)/2;}
  function isAbandonBaby(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c<a.o&&(a.o-a.c)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.h<a.l&&c.c>c.o&&(c.c-c.o)>=0.5*avgB&&c.l>b.h;}
  function isAbandonTop(i){var a=d[i-2],b=d[i-1],c=d[i],bp=an(b);return a.c>a.o&&(a.c-a.o)>=0.5*avgB&&bp.b/bp.r<=0.1&&b.l>a.h&&c.c<c.o&&(c.o-c.c)>=0.5*avgB&&c.h<b.l;}
  for(i=2;i<n;i++){
    if(isDragonfly(i)) found.push({i:i,n:'蜻蜓十字',dir:0});
    if(isLongLeg(i)) found.push({i:i,n:'长腿十字',dir:0});
    if(isSpinTop(i)) found.push({i:i,n:'纺锤顶',dir:0});
    if(isHighWave(i)) found.push({i:i,n:'高浪线',dir:0});
    if(isRickshaw(i)) found.push({i:i,n:'黄包车夫',dir:0});
    if(isBeltBull(i)) found.push({i:i,n:'看涨腰带线',dir:1});
    if(isBeltBear(i)) found.push({i:i,n:'看跌腰带线',dir:-1});
    if(isHaramiCrossBull(i)) found.push({i:i,n:'看涨孕线十字',dir:1});
    if(isHaramiCrossBear(i)) found.push({i:i,n:'看跌孕线十字',dir:-1});
    if(isCounterBull(i)) found.push({i:i,n:'看涨反击线',dir:1});
    if(isCounterBear(i)) found.push({i:i,n:'看跌反击线',dir:-1});
    if(isMorningDoji(i)) found.push({i:i,n:'启明十字星',dir:1});
    if(isEveningDoji(i)) found.push({i:i,n:'黄昏十字星',dir:-1});
    if(isAbandonBaby(i)) found.push({i:i,n:'弃婴（底部）',dir:1});
    if(isAbandonTop(i)) found.push({i:i,n:'弃婴（顶部）',dir:-1});
  }
  return found;
}
/* ---- I-1 第三批（2026-08-23 CWIRE）：CANDLE 持续形态/三根族余项 16 规则（对齐注册表 PAT-CANDLE-032/033/034/042/044/045/048/049/050/052/053/054） ---- */
function patExt2(d){
  var n=d.length,found=[],i;
  var avgB=0;
  for(i=0;i<n;i++) avgB+=Math.abs(d[i].c-d[i].o);
  avgB=n?avgB/n:1; if(avgB<=0)avgB=1e-9;
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}
  /* 持续五根族：上升/下降三法（PAT-CANDLE-054） */
  function isRising3(i){   /* 大阳 + 三根小实体收敛于首根实体 + 大阳创新高 */
    var a=d[i-4],e=d[i];
    if(!(a.c>a.o&&(a.c-a.o)>=avgB&&e.c>e.o&&(e.c-e.o)>=avgB&&e.c>a.c))return false;
    for(var j=i-3;j<=i-1;j++){var k=d[j];if(Math.abs(k.c-k.o)>=0.6*(a.c-a.o))return false;if(k.l<a.o||k.h>a.c*1.01)return false;}
    return true;
  }
  function isFalling3(i){
    var a=d[i-4],e=d[i];
    if(!(a.c<a.o&&(a.o-a.c)>=avgB&&e.c<e.o&&(e.o-e.c)>=avgB&&e.c<a.c))return false;
    for(var j=i-3;j<=i-1;j++){var k=d[j];if(Math.abs(k.c-k.o)>=0.6*(a.o-a.c))return false;if(k.h>a.o||k.l<a.c*0.99)return false;}
    return true;
  }
  /* 双根持续：分手线（052）/入颈线（048）/上颈线（049）/插入线（050）/并排阳线（053） */
  function isSepBull(i){var b=d[i-1],c=d[i];return r5(i-1)>=0.01&&b.c<b.o&&c.c>c.o&&Math.abs(c.o-b.o)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  function isSepBear(i){var b=d[i-1],c=d[i];return r5(i-1)<=-0.01&&b.c>b.o&&c.c<c.o&&Math.abs(c.o-b.o)<=0.3*avgB&&Math.abs(b.c-b.o)>=0.5*avgB;}
  function isInNeck(i){var b=d[i-1],c=d[i];return r5(i)<=-0.01&&(b.o-b.c)>=avgB&&c.c>c.o&&Math.abs(c.c-b.c)<=0.15*(b.o-b.c);}
  function isOnNeck(i){var b=d[i-1],c=d[i];return r5(i)<=-0.01&&(b.o-b.c)>=avgB&&c.c>c.o&&Math.abs(c.c-b.l)<=0.1*(b.o-b.c);}
  function isThrust(i){var b=d[i-1],c=d[i];var mid=(b.o+b.c)/2;return r5(i)<=-0.01&&(b.o-b.c)>=avgB&&c.c>c.o&&c.c>b.c&&c.c<mid;}   /* 插入线：收复昨收但未过实体中点 */
  function isSideWhite(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&a.c>a.o&&b.c>b.o&&c.c>c.o&&b.o>a.c*1.005&&Math.abs(c.o-b.o)<=0.3*avgB&&Math.abs((c.c-c.o)-(b.c-b.o))<=0.5*avgB;}
  /* 三根族余项：内含三线（032）/外包三线（033）/两只乌鸦（045）/跳空双鸦（044）/大敌当前（042）/三线打击（034） */
  function is3InsideUp(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)<=-0.01&&(a.o-a.c)>=0.8*avgB&&b.c>b.o&&Math.abs(b.c-b.o)<=0.6*(a.o-a.c)&&Math.max(b.o,b.c)<=a.o&&Math.min(b.o,b.c)>=a.c&&c.c>c.o&&c.c>a.o;}
  function is3InsideDn(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&(a.c-a.o)>=0.8*avgB&&b.c<b.o&&Math.abs(b.c-b.o)<=0.6*(a.c-a.o)&&Math.max(b.o,b.c)<=a.c&&Math.min(b.o,b.c)>=a.o&&c.c<c.o&&c.c<a.o;}
  function is3OutsideUp(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c<a.o&&b.c>b.o&&b.c>=a.o&&b.o<=a.c&&c.c>c.o&&c.c>b.c;}
  function is3OutsideDn(i){var a=d[i-2],b=d[i-1],c=d[i];return a.c>a.o&&b.c<b.o&&b.c<=a.o&&b.o>=a.c&&c.c<c.o&&c.c<b.c;}
  function isTwoCrows(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&a.c>a.o&&(a.c-a.o)>=0.5*avgB&&b.c<b.o&&b.o>a.c*1.003&&c.c<c.o&&c.o>b.o&&c.c<b.c&&c.c>a.c;}
  function isGap2Crows(i){var a=d[i-2],b=d[i-1],c=d[i];return r5(i)>=0.01&&a.c>a.o&&(a.c-a.o)>=0.5*avgB&&b.c<b.o&&b.l>a.c*1.003&&c.c<c.o&&c.o>b.o&&c.c<b.o&&c.c>a.c;}
  function isAdvBlock(i){
    var a=d[i-2],b=d[i-1],c=d[i];
    if(!(a.c>a.o&&b.c>b.o&&c.c>c.o&&b.c>a.c&&c.c>b.c))return false;
    var ba=a.c-a.o,bb=b.c-b.o,bc=c.c-c.o;
    return ba>=0.5*avgB&&bb<ba*0.85&&bc<bb*0.85&&an(c).u>bc*0.5;   /* 实体递减+上影拉长=推进受阻 */
  }
  function is3LineStrike(i){
    var a=d[i-3],b=d[i-2],c=d[i-1],e=d[i];
    return a.c>a.o&&b.c>b.o&&c.c>c.o&&b.c>a.c&&c.c>b.c
      &&(a.c-a.o)>=0.5*avgB&&(b.c-b.o)>=0.5*avgB&&(c.c-c.o)>=0.5*avgB
      &&e.c<e.o&&(e.o-e.c)>=avgB&&e.o>=c.c*0.99&&e.c<a.o;   /* 三连阳后大阴吞没=持续蓄势（Bulkowski 口径偏多） */
  }
  for(i=4;i<n;i++){
    if(isRising3(i)) found.push({i:i,n:'上升三法',dir:1});
    if(isFalling3(i)) found.push({i:i,n:'下降三法',dir:-1});
    if(isSepBull(i)) found.push({i:i,n:'看涨分手线',dir:1});
    if(isSepBear(i)) found.push({i:i,n:'看跌分手线',dir:-1});
    if(isInNeck(i)) found.push({i:i,n:'入颈线',dir:-1});
    if(isOnNeck(i)) found.push({i:i,n:'上颈线',dir:-1});
    if(isThrust(i)) found.push({i:i,n:'插入线',dir:-1});
    if(isSideWhite(i)) found.push({i:i,n:'并排阳线',dir:1});
    if(is3InsideUp(i)) found.push({i:i,n:'内含三线涨',dir:1});
    if(is3InsideDn(i)) found.push({i:i,n:'内含三线跌',dir:-1});
    if(is3OutsideUp(i)) found.push({i:i,n:'外包三线涨',dir:1});
    if(is3OutsideDn(i)) found.push({i:i,n:'外包三线跌',dir:-1});
    if(isTwoCrows(i)) found.push({i:i,n:'两只乌鸦',dir:-1});
    if(isGap2Crows(i)) found.push({i:i,n:'跳空双鸦',dir:-1});
    if(isAdvBlock(i)) found.push({i:i,n:'大敌当前',dir:-1});
    if(is3LineStrike(i)) found.push({i:i,n:'三线打击',dir:1});
  }
  return found;
}
/* ---- 图表形态 zigzag 公共构建（fractals 压缩：同型留更极端者，异型距离≥3 入列） ---- */
function zigzagPts(d){
  var fr=fractals(d),zz=[];
  var pts=fr.tops.map(function(t){return{i:t,tp:1};}).concat(fr.bots.map(function(b){return{i:b,tp:-1};}));
  pts.sort(function(a,b){return a.i-b.i;});
  pts.forEach(function(p){
    var L=zz[zz.length-1];
    if(!L){zz.push(p);return;}
    if(p.tp===L.tp){
      if((p.tp===1&&d[p.i].h>=d[L.i].h)||(p.tp===-1&&d[p.i].l<=d[L.i].l)) zz[zz.length-1]=p;
    }else if(p.i-L.i>=3){zz.push(p);}
  });
  return zz;
}
/* ---- I-1 第三批（2026-08-23 CWIRE）：CHART 三角/楔形/旗形/矩形/三重顶底 10 规则（对齐注册表 PAT-CHART-005~011/015/017/018） ---- */
function chartPats2(d){
  var n=d.length,found=[],i;
  var zz=zigzagPts(d);
  function slope(arr,acc){   /* 最小二乘斜率（按 zz 点位价格），acc: 取值函数 */
    var m=arr.length;if(m<3)return 0;
    var sx=0,sy=0,sxy=0,sxx=0;
    for(var k=0;k<m;k++){var v=acc(arr[k]);sx+=k;sy+=v;sxy+=k*v;sxx+=k*k;}
    var den=m*sxx-sx*sx; if(!den)return 0;
    return (m*sxy-sx*sy)/den;
  }
  function flat(arr,acc,tol){var vs=arr.map(acc),mn=Math.min.apply(null,vs),mx=Math.max.apply(null,vs);return mn>0&&(mx-mn)/mn<=tol;}
  /* 当前结构（末端 6 个 zz 点）：三角/楔形/矩形（单一标注） */
  if(zz.length>=6){
    var seg=zz.slice(-6);
    var tops=seg.filter(function(p){return p.tp===1;}),bots=seg.filter(function(p){return p.tp===-1;});
    if(tops.length>=2&&bots.length>=2){
      var tS=slope(tops,function(p){return d[p.i].h;}),bS=slope(bots,function(p){return d[p.i].l;});
      var ref=d[seg[seg.length-1].i].c, eps=ref*0.0015;   /* 斜率阈值≈每点 0.15% */
      var tFlat=flat(tops,function(p){return d[p.i].h;},0.02),bFlat=flat(bots,function(p){return d[p.i].l;},0.02);
      var end=seg[seg.length-1].i;
      if(tFlat&&bFlat&&Math.abs(tS)<=eps&&Math.abs(bS)<=eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'矩形箱体',dir:0});
      else if(tFlat&&bS>eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'上升三角形',dir:1});
      else if(bFlat&&tS<-eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'下降三角形',dir:-1});
      else if(tS<-eps&&bS>eps) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'对称三角形',dir:0});
      else if(tS>eps&&bS>tS*1.3) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'上升楔形',dir:-1});
      else if(tS<-eps&&bS<0&&bS>tS) found.push({i:end,i2:seg[0].i,mid:seg[2].i,n:'下降楔形',dir:1});
    }
  }
  /* 三重顶/底（zz 顶底交替，五点结构 T,B,T,B,T / B,T,B,T,B，全部窗口扫描逐处标注） */
  for(i=4;i<zz.length;i++){
    var u1=zz[i-4],u3=zz[i-2],u5=zz[i];
    if(u1.tp===1&&zz[i-3].tp===-1&&u3.tp===1&&zz[i-1].tp===-1&&u5.tp===1
      &&flat([u1,u3,u5],function(p){return d[p.i].h;},0.02)&&(u5.i-u1.i)>=10)
      found.push({i:u5.i,i2:u1.i,mid:u3.i,n:'三重顶',dir:-1});
    if(u1.tp===-1&&zz[i-3].tp===1&&u3.tp===-1&&zz[i-1].tp===1&&u5.tp===-1
      &&flat([u1,u3,u5],function(p){return d[p.i].l;},0.02)&&(u5.i-u1.i)>=10)
      found.push({i:u5.i,i2:u1.i,mid:u3.i,n:'三重底',dir:1});
  }
  /* 旗形（全序列扫描：旗杆 8 根内涨幅≥8% + 旗面 5+ 根窄幅反漂，防误检用区间收益口径） */
  for(i=13;i<n;i++){
    var poleEnd=i-5;
    var poleRet=d[poleEnd].c/d[i-13].o-1;
    var bodyLo=1e18,bodyHi=-1e18,drift=0;
    for(var k=poleEnd+1;k<=i;k++){bodyLo=Math.min(bodyLo,d[k].l);bodyHi=Math.max(bodyHi,d[k].h);drift+=d[k].c-d[k-1].c;}
    var range=(bodyHi-bodyLo)/d[poleEnd].c;
    if(poleRet>=0.08&&range<=0.05&&drift<0&&drift>-0.06*d[poleEnd].c) found.push({i:i,i2:i-13,mid:poleEnd,n:'多头旗形',dir:1});
    if(poleRet<=-0.08&&range<=0.05&&drift>0&&drift<0.06*d[poleEnd].c) found.push({i:i,i2:i-13,mid:poleEnd,n:'空头旗形',dir:-1});
  }
  return found;
}
/* ---- 图表形态 4 种（fractals zigzag 简化识别：双顶/双底/头肩顶/头肩底），全部匹配位置同时标注 ---- */
function chartPats(d){
  var zz=zigzagPts(d),i;
  var found=[];
  for(i=2;i<zz.length;i++){   /* 三点结构：双顶/双底 */
    var p1=zz[i-2],p2=zz[i-1],p3=zz[i];
    if(p1.tp===1&&p2.tp===-1&&p3.tp===1){
      var h1=d[p1.i].h,h3=d[p3.i].h,vl=d[p2.i].l;
      if(Math.abs(h1-h3)/h1<=0.03&&(p3.i-p1.i)>=8&&(h1-vl)/h1>=0.03)
        found.push({i:p3.i,i2:p1.i,mid:p2.i,n:'双顶',dir:-1});
    }
    if(p1.tp===-1&&p2.tp===1&&p3.tp===-1){
      var l1=d[p1.i].l,l3=d[p3.i].l,vh=d[p2.i].h;
      if(Math.abs(l1-l3)/l1<=0.03&&(p3.i-p1.i)>=8&&(vh-l1)/l1>=0.03)
        found.push({i:p3.i,i2:p1.i,mid:p2.i,n:'双底',dir:1});
    }
  }
  for(i=4;i<zz.length;i++){   /* 五点结构：头肩顶/头肩底 */
    var q1=zz[i-4],q2=zz[i-3],q3=zz[i-2],q4=zz[i-1],q5=zz[i];
    if(q1.tp===1&&q2.tp===-1&&q3.tp===1&&q4.tp===-1&&q5.tp===1){
      var s1=d[q1.i].h,hd=d[q3.i].h,s2=d[q5.i].h,n1=d[q2.i].l,n2=d[q4.i].l;
      if(hd>s1*1.015&&hd>s2*1.015&&Math.abs(s1-s2)/s1<=0.05&&Math.abs(n1-n2)/n1<=0.04&&(q5.i-q1.i)>=15)
        found.push({i:q5.i,i2:q1.i,mid:q3.i,n:'头肩顶',dir:-1});
    }
    if(q1.tp===-1&&q2.tp===1&&q3.tp===-1&&q4.tp===1&&q5.tp===-1){
      var b1=d[q1.i].l,bd=d[q3.i].l,b2=d[q5.i].l,k1=d[q2.i].h,k2=d[q4.i].h;
      if(bd<b1*0.985&&bd<b2*0.985&&Math.abs(b1-b2)/b1<=0.05&&Math.abs(k1-k2)/k1<=0.04&&(q5.i-q1.i)>=15)
        found.push({i:q5.i,i2:q1.i,mid:q3.i,n:'头肩底',dir:1});
    }
  }
  return found;
}
/* ---- I-1 第四批（2026-08-25 子代理产码主会话集成）：CANDLE 族余项 36 条目/49 规则（PAT-CANDLE-015/018/024/027/028/031/035/036/037/038/039/041/043/046/047/055/056/057/058/059/060/061/062/063/064/065/066/067/068/071/072/073/074/075/076/077） ---- */
function patExt3(d){
  var n=d.length,found=[],i,j;
  var avgB=0;
  for(i=0;i<n;i++) avgB+=Math.abs(d[i].c-d[i].o);
  avgB=n?avgB/n:1; if(avgB<=0)avgB=1e-9;
  function an(k){var b=Math.abs(k.c-k.o),r=k.h-k.l;if(r<=0)r=1e-9;return{b:b,r:r,u:k.h-Math.max(k.o,k.c),d:Math.min(k.o,k.c)-k.l};}
  function r5(i){return i>=5&&d[i-5].c>0?d[i].c/d[i-5].c-1:0;}
  var hasV=false;
  for(i=0;i<n;i++){if(typeof d[i].v=='number'){hasV=true;break;}}
  var M5=[],M10=[],M20=[],ATR=[],AV=[];
  for(i=0;i<n;i++){
    var s=0,k;
    if(i>=4){s=0;for(k=i-4;k<=i;k++)s+=d[k].c;M5.push(s/5);}else M5.push(null);
    if(i>=9){s=0;for(k=i-9;k<=i;k++)s+=d[k].c;M10.push(s/10);}else M10.push(null);
    if(i>=19){s=0;for(k=i-19;k<=i;k++)s+=d[k].c;M20.push(s/20);}else M20.push(null);
    if(i>=14){s=0;for(k=i-13;k<=i;k++){var p0=d[k-1].c;s+=Math.max(d[k].h-d[k].l,Math.abs(d[k].h-p0),Math.abs(d[k].l-p0));}ATR.push(s/14);}else ATR.push(null);
    if(hasV&&i>=20){s=0;for(k=i-20;k<i;k++)s+=d[k].v;AV.push(s/20);}else AV.push(null);
  }
  function volOK(i,m){return AV[i]!=null&&typeof d[i].v=='number'?d[i].v>=m*AV[i]:true;}
  function maru(k){var p=an(k);return p.u<=0.05*p.r&&p.d<=0.05*p.r&&p.b>=0.5*avgB;}
  function isCloseMaruY(i){var p=an(d[i]);return d[i].c>d[i].o&&p.b>=0.5*avgB&&p.u<=0.05*p.r;}
  function isCloseMaruN(i){var p=an(d[i]);return d[i].c<d[i].o&&p.b>=0.5*avgB&&p.d<=0.05*p.r;}
  function isTakuri(i){var p=an(d[i]);return r5(i)<=-0.01&&p.b<=0.3*avgB&&p.d>=3*p.b&&p.d>=0.5*p.r&&p.u<=0.1*p.r;}
  function isLongLine(i){var p=an(d[i]);return p.b/p.r>=0.8;}
  function isShortLine(i){var p=an(d[i]);return p.b/p.r<=0.25;}
  function isLimitUpFlat(i){var k=d[i],pc=d[i-1].c;return pc>0&&(k.h-k.l)<=0.001*pc&&k.c>=pc*1.098;}
  function isLimitDnFlat(i){var k=d[i],pc=d[i-1].c;return pc>0&&(k.h-k.l)<=0.001*pc&&k.c<=pc*0.902;}
  function isSkyGround(i){var k=d[i],pc=d[i-1].c;return pc>0&&k.o>=pc*1.02&&k.h>=pc*1.098&&k.c<=pc*0.902;}
  function isGroundSky(i){var k=d[i],pc=d[i-1].c;return pc>0&&k.l<=pc*0.902&&k.c>=pc*1.098&&volOK(i,3);}
  function isYangThruMA(i){
    if(i<20||M5[i-1]==null||M10[i-1]==null||M20[i-1]==null)return false;
    var k=d[i],p=an(k),lo=Math.min(M5[i-1],M10[i-1],M20[i-1]),hi=Math.max(M5[i-1],M10[i-1],M20[i-1]);
    return k.c>k.o&&p.b/p.r>=0.6&&k.o<lo&&k.c>hi;
  }
  function isNR7(i){
    if(i<7)return false;var r=d[i].h-d[i].l;
    for(j=i-6;j<i;j++){if(r>d[j].h-d[j].l)return false;}
    return r>0;
  }
  function isKeyRevTop(i){var a=d[i-1],k=d[i];return r5(i-1)>=0.01&&k.h>a.h&&k.l<a.l&&k.c<a.c&&volOK(i,1.5);}
  function isKeyRevBot(i){var a=d[i-1],k=d[i];return r5(i-1)<=-0.01&&k.h>a.h&&k.l<a.l&&k.c>a.c&&volOK(i,1.5);}
  function isWRB(i){
    if(ATR[i]==null)return false;var p=an(d[i]);
    return p.r>=2*ATR[i]&&p.b/p.r>=0.6;
  }
  function isOopsDown(i){var a=d[i-1],k=d[i];return k.o>a.h&&k.c<=a.h&&k.c>=a.l;}
  function isOopsUp(i){var a=d[i-1],k=d[i];return k.o<a.l&&k.c>=a.l&&k.c<=a.h;}
  function isDojiStarT(i){var a=d[i-1],b=d[i],pb=an(b);return r5(i-1)>=0.01&&a.c>a.o&&(a.c-a.o)>=avgB&&pb.b/pb.r<=0.1&&Math.min(b.o,b.c)>a.c;}
  function isDojiStarB(i){var a=d[i-1],b=d[i],pb=an(b);return r5(i-1)<=-0.01&&a.c<a.o&&(a.o-a.c)>=avgB&&pb.b/pb.r<=0.1&&Math.max(b.o,b.c)<a.c;}
  function isKickBull(i){var a=d[i-1],b=d[i];return a.c<a.o&&maru(a)&&b.c>b.o&&maru(b)&&b.o>a.h;}
  function isKickBear(i){var a=d[i-1],b=d[i];return a.c>a.o&&maru(a)&&b.c<b.o&&maru(b)&&b.o<a.l;}
  function isKickLenBull(i){return isKickBull(i)&&(d[i].c-d[i].o)>(d[i-1].o-d[i-1].c);}
  function isKickLenBear(i){return isKickBear(i)&&(d[i-1].c-d[i-1].o)<(d[i].o-d[i].c);}
  function isHomingPigeon(i){var a=d[i-1],b=d[i];return r5(i)<=-0.01&&a.c<a.o&&(a.o-a.c)>=0.5*avgB&&b.c<b.o&&Math.max(b.o,b.c)<=a.o&&Math.min(b.o,b.c)>=a.c;}
  function isMatchingLow(i){var a=d[i-1],b=d[i];return r5(i)<=-0.01&&a.c<a.o&&(a.o-a.c)>=0.5*avgB&&b.c<b.o&&Math.abs(b.c-a.c)<=0.005*a.c;}
  function isCuoRou(i){
    var a=d[i-1],b=d[i],pa=an(a),pb=an(b);
    if(!(pa.u>=2*pa.b&&pa.b/pa.r<=0.33&&pb.d>=2*pb.b&&pb.b/pb.r<=0.33))return false;
    if(!(Math.max(b.o,b.c)<=a.h&&Math.min(b.o,b.c)>=a.l))return false;
    return Math.abs(r5(i))>=0.01;
  }
  function isIdent3Crows(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&c.c<c.o
      &&(a.o-a.c)>=0.5*avgB&&(b.o-b.c)>=0.5*avgB&&(c.o-c.c)>=0.5*avgB
      &&b.c<a.c&&c.c<b.c&&Math.abs(b.o-a.c)<=0.2*avgB&&Math.abs(c.o-b.c)<=0.2*avgB;
  }
  function is3StarsSouth(i){var a=d[i-2],b=d[i-1],c=d[i],pa=an(a),pb=an(b),pc=an(c);
    return r5(i)<=-0.01
      &&a.c<a.o&&pa.b>=0.5*avgB&&pa.d>pa.b
      &&b.c<b.o&&pb.b<pa.b&&b.o>a.c&&b.l>a.l&&pb.d>0
      &&c.c<c.o&&pc.b<=0.5*pb.b&&c.h<=b.h&&c.l>=b.l&&pc.u<=0.2*pc.r&&pc.d<=0.2*pc.r;
  }
  function isUnique3River(i){var a=d[i-2],b=d[i-1],c=d[i];
    return r5(i)<=-0.01
      &&a.c<a.o&&(a.o-a.c)>=avgB
      &&b.c<b.o&&Math.max(b.o,b.c)<=a.o&&Math.min(b.o,b.c)>=a.c&&b.l<a.l
      &&c.c>c.o&&(c.c-c.o)<=0.6*avgB&&c.c<b.c;
  }
  function isStickSandwich(i){var a=d[i-2],b=d[i-1],c=d[i];
    return r5(i)<=-0.01&&a.c<a.o&&(a.o-a.c)>=0.5*avgB&&b.c>b.o&&c.c<c.o&&Math.abs(c.c-a.c)<=0.2*avgB;
  }
  function isTristarTop(i){var a=d[i-2],b=d[i-1],c=d[i],pa=an(a),pb=an(b),pc=an(c);
    return r5(i)>=0.01&&pa.b/pa.r<=0.1&&pb.b/pb.r<=0.1&&pc.b/pc.r<=0.1&&b.l>Math.max(a.h,c.h);
  }
  function isTristarBot(i){var a=d[i-2],b=d[i-1],c=d[i],pa=an(a),pb=an(b),pc=an(c);
    return r5(i)<=-0.01&&pa.b/pa.r<=0.1&&pb.b/pb.r<=0.1&&pc.b/pc.r<=0.1&&b.h<Math.min(a.l,c.l);
  }
  function isStalled(i){var a=d[i-2],b=d[i-1],c=d[i],pc=an(c);
    return r5(i)>=0.01&&a.c>a.o&&(a.c-a.o)>=0.5*avgB&&b.c>b.o&&(b.c-b.o)>=0.5*avgB&&b.c>a.c
      &&c.c>c.o&&(c.c-c.o)<=0.5*(b.c-b.o)&&Math.abs(c.o-b.c)<=0.3*avgB&&pc.u>=0.3*pc.r;
  }
  function isGap3Up(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c>a.o&&b.c>b.o&&b.o>a.c&&c.c<c.o&&c.o<=b.c&&c.o>=b.o&&c.c<a.c&&c.c>a.o;
  }
  function isGap3Dn(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&b.o<a.c&&c.c>c.o&&c.o>=b.c&&c.o<=b.o&&c.c>a.c&&c.c<a.o;
  }
  function isTasukiUp(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c>a.o&&b.c>b.o&&b.o>a.c&&c.c<c.o&&c.o<=b.c&&c.o>=b.o&&c.c<b.o&&c.c>a.c;
  }
  function isTasukiDn(i){var a=d[i-2],b=d[i-1],c=d[i];
    return a.c<a.o&&b.c<b.o&&b.o<a.c&&c.c>c.o&&c.o>=b.c&&c.o<=b.o&&c.c>b.o&&c.c<a.c;
  }
  function isLadderBottom(i){var a=d[i-4],b=d[i-3],c=d[i-2],e=d[i-1],f=d[i],pe=an(e);
    return r5(i-4)<=-0.01
      &&a.c<a.o&&b.c<b.o&&c.c<c.o&&b.c<a.c&&c.c<b.c&&b.o<a.o&&c.o<b.o
      &&e.c<e.o&&pe.u>=0.3*pe.r
      &&f.c>f.o&&f.o>e.o;
  }
  function isConcealBaby(i){var a=d[i-3],b=d[i-2],c=d[i-1],e=d[i];
    return r5(i-3)<=-0.01
      &&a.c<a.o&&maru(a)&&b.c<b.o&&maru(b)
      &&c.c<c.o&&c.o<b.c&&c.h>b.c
      &&e.c<e.o&&e.h>=c.h&&e.l<=c.l;
  }
  function isMatHold(i){var a=d[i-4],f=d[i],ba=a.c-a.o;
    if(!(a.c>a.o&&ba>=avgB))return false;
    if(!(f.c>f.o&&(f.c-f.o)>=avgB))return false;
    var b=d[i-3],c=d[i-2],e=d[i-1];
    if(!(f.c>Math.max(a.c,b.c,c.c,e.c)))return false;
    var ks=[b,c,e];
    for(j=0;j<3;j++){if(Math.abs(ks[j].c-ks[j].o)>=0.6*ba)return false;if(ks[j].l<a.o)return false;}
    return b.o>a.c;
  }
  function isBreakawayBot(i){var a=d[i-4],b=d[i-3],c=d[i-2],e=d[i-1],f=d[i];
    return a.c<a.o&&(a.o-a.c)>=avgB&&b.c<b.o&&b.o<a.c
      &&c.c<b.c&&e.c<c.c
      &&f.c>f.o&&(f.c-f.o)>=avgB&&f.c>b.c&&f.c<a.c;
  }
  function isBreakawayTop(i){var a=d[i-4],b=d[i-3],c=d[i-2],e=d[i-1],f=d[i];
    return a.c>a.o&&(a.c-a.o)>=avgB&&b.c>b.o&&b.o>a.c
      &&c.c>b.c&&e.c>c.c
      &&f.c<f.o&&(f.o-f.c)>=avgB&&f.c<b.c&&f.c>a.c;
  }
  function isHikkakeBull(i){
    var t,s;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      for(s=t+1;s<i;s++){if(d[s].c<d[t].l&&d[i].c>d[t].h)return true;}
    }
    return false;
  }
  function isHikkakeBear(i){
    var t,s;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      for(s=t+1;s<i;s++){if(d[s].c>d[t].h&&d[i].c<d[t].l)return true;}
    }
    return false;
  }
  function isHikkakeModBull(i){
    var t,s,mx,brk;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      mx=d[t].h;brk=false;
      for(s=t+1;s<i;s++){if(d[s].c<d[t].l)brk=true;if(d[s].h>mx)mx=d[s].h;}
      if(brk&&d[i].c>mx)return true;
    }
    return false;
  }
  function isHikkakeModBear(i){
    var t,s,mn,brk;
    for(t=i-2;t>=Math.max(1,i-4);t--){
      if(!(d[t].h<=d[t-1].h&&d[t].l>=d[t-1].l))continue;
      mn=d[t].l;brk=false;
      for(s=t+1;s<i;s++){if(d[s].c>d[t].h)brk=true;if(d[s].l<mn)mn=d[s].l;}
      if(brk&&d[i].c<mn)return true;
    }
    return false;
  }
  function isSankuUp(i){
    var g=[],m,filled;
    for(j=Math.max(1,i-8);j<=i-1;j++){
      if(d[j].l>=d[j-1].h*1.003){
        filled=false;
        for(m=j+1;m<=i-1;m++){if(d[m].l<=d[j-1].h){filled=true;break;}}
        if(!filled)g.push(j);
      }
    }
    return g.length>=3&&g[g.length-1]===(i-1)&&d[i].c<d[i].o;
  }
  function isSankuDn(i){
    var g=[],m,filled;
    for(j=Math.max(1,i-8);j<=i-1;j++){
      if(d[j].h<=d[j-1].l*0.997){
        filled=false;
        for(m=j+1;m<=i-1;m++){if(d[m].h>=d[j-1].l){filled=true;break;}}
        if(!filled)g.push(j);
      }
    }
    return g.length>=3&&g[g.length-1]===(i-1)&&d[i].c>d[i].o;
  }
  function isTowerTop(i){
    var a=d[i-4],e=d[i],pa=an(a),pe=an(e),mid=(a.o+a.c)/2;
    if(!(a.c>a.o&&pa.b>=avgB&&pa.b/pa.r>=0.7))return false;
    if(!(e.c<e.o&&pe.b>=avgB&&pe.b/pe.r>=0.6))return false;
    for(j=i-3;j<=i-1;j++){var q=d[j];if(q.h-q.l>0.5*pa.r)return false;if(q.l<mid)return false;}
    return e.c<mid&&r5(i-4)>=0;
  }
  function isTowerBot(i){
    var a=d[i-4],e=d[i],pa=an(a),pe=an(e),mid=(a.o+a.c)/2;
    if(!(a.c<a.o&&pa.b>=avgB&&pa.b/pa.r>=0.7))return false;
    if(!(e.c>e.o&&pe.b>=avgB&&pe.b/pe.r>=0.6))return false;
    for(j=i-3;j<=i-1;j++){var q=d[j];if(q.h-q.l>0.5*pa.r)return false;if(q.h>mid)return false;}
    return e.c>mid&&r5(i-4)<=0;
  }
  for(i=4;i<n;i++){
    if(isCloseMaruY(i)) found.push({i:i,n:'收盘光头光脚线',dir:1});
    if(isCloseMaruN(i)) found.push({i:i,n:'收盘光头光脚线',dir:-1});
    if(isTakuri(i)) found.push({i:i,n:'探水竿',dir:1});
    if(isDojiStarT(i)) found.push({i:i,n:'十字星组合',dir:-1});
    if(isDojiStarB(i)) found.push({i:i,n:'十字星组合',dir:1});
    if(isKickBull(i)) found.push({i:i,n:'反冲双胞胎',dir:1});
    if(isKickBear(i)) found.push({i:i,n:'反冲双胞胎',dir:-1});
    if(isKickLenBull(i)) found.push({i:i,n:'长度反冲',dir:1});
    if(isKickLenBear(i)) found.push({i:i,n:'长度反冲',dir:-1});
    if(isIdent3Crows(i)) found.push({i:i,n:'同款三乌鸦',dir:-1});
    if(is3StarsSouth(i)) found.push({i:i,n:'南方三星',dir:1});
    if(isUnique3River(i)) found.push({i:i,n:'独特三河底',dir:1});
    if(isLadderBottom(i)) found.push({i:i,n:'阶梯底',dir:1});
    if(isStickSandwich(i)) found.push({i:i,n:'条形三明治',dir:1});
    if(isTristarTop(i)) found.push({i:i,n:'三星形态',dir:-1});
    if(isTristarBot(i)) found.push({i:i,n:'三星形态',dir:1});
    if(isConcealBaby(i)) found.push({i:i,n:'藏燕吞没',dir:1});
    if(isStalled(i)) found.push({i:i,n:'停滞形态',dir:-1});
    if(isHomingPigeon(i)) found.push({i:i,n:'归鸽',dir:1});
    if(isMatchingLow(i)) found.push({i:i,n:'相抵双阳',dir:1});
    if(isMatHold(i)) found.push({i:i,n:'垫形整理',dir:1});
    if(isBreakawayBot(i)) found.push({i:i,n:'脱离形态',dir:1});
    if(isBreakawayTop(i)) found.push({i:i,n:'脱离形态',dir:-1});
    if(isGap3Up(i)) found.push({i:i,n:'跳空三法',dir:1});
    if(isGap3Dn(i)) found.push({i:i,n:'跳空三法',dir:-1});
    if(isTasukiUp(i)) found.push({i:i,n:'兔跳缺口',dir:1});
    if(isTasukiDn(i)) found.push({i:i,n:'兔跳缺口',dir:-1});
    if(isHikkakeBull(i)) found.push({i:i,n:'日垣陷阱',dir:1});
    if(isHikkakeBear(i)) found.push({i:i,n:'日垣陷阱',dir:-1});
    if(isHikkakeModBull(i)) found.push({i:i,n:'日垣修正陷阱',dir:1});
    if(isHikkakeModBear(i)) found.push({i:i,n:'日垣修正陷阱',dir:-1});
    if(isLongLine(i)) found.push({i:i,n:'长线',dir:d[i].c>=d[i].o?1:-1});
    if(isShortLine(i)) found.push({i:i,n:'短线',dir:0});
    if(isLimitUpFlat(i)) found.push({i:i,n:'一字涨停板',dir:1});
    if(isLimitDnFlat(i)) found.push({i:i,n:'一字跌停板',dir:-1});
    if(isCuoRou(i)) found.push({i:i,n:'搓揉线',dir:r5(i)>=0.01?-1:1});
    if(isSkyGround(i)) found.push({i:i,n:'天地板',dir:-1});
    if(isGroundSky(i)) found.push({i:i,n:'地天板',dir:1});
    if(isYangThruMA(i)) found.push({i:i,n:'一阳穿多线',dir:1});
    if(isNR7(i)) found.push({i:i,n:'窄幅整理日',dir:0});
    if(isKeyRevTop(i)) found.push({i:i,n:'关键反转日（外包反转）',dir:-1});
    if(isKeyRevBot(i)) found.push({i:i,n:'关键反转日（外包反转）',dir:1});
    if(isWRB(i)) found.push({i:i,n:'宽幅推进K线',dir:d[i].c>=d[i].o?1:-1});
    if(isOopsDown(i)) found.push({i:i,n:'跳空反向陷阱',dir:-1});
    if(isOopsUp(i)) found.push({i:i,n:'跳空反向陷阱',dir:1});
    if(isSankuUp(i)) found.push({i:i,n:'三空（酒田五法）',dir:-1});
    if(isSankuDn(i)) found.push({i:i,n:'三空（酒田五法）',dir:1});
    if(isTowerTop(i)) found.push({i:i,n:'塔形顶',dir:-1});
    if(isTowerBot(i)) found.push({i:i,n:'塔形底',dir:1});
  }
  return found;
}
/* ---- I-1 第四批：CHART 西方经典族 30 规则（PAT-CHART-003/012/013/014/019/020/021/022/023/024/025/026/039/040/041/042/043/044/045/046/047/048/049/050/051/057/058/059/060/061） ---- */
function chartPats3(d){
  var n=d.length,found=[],i,j,k;
  var zz=zigzagPts(d);
  function slope(arr,acc){
    var m=arr.length;if(m<3)return 0;
    var sx=0,sy=0,sxy=0,sxx=0;
    for(var q=0;q<m;q++){var v=acc(arr[q]);sx+=q;sy+=v;sxy+=q*v;sxx+=q*q;}
    var den=m*sxx-sx*sx; if(!den)return 0;
    return (m*sxy-sx*sy)/den;
  }
  function flat(arr,acc,tol){var vs=arr.map(acc),mn=Math.min.apply(null,vs),mx=Math.max.apply(null,vs);return mn>0&&(mx-mn)/mn<=tol;}
  function zpr(p){return p.tp===1?d[p.i].h:d[p.i].l;}
  function maxH(a,b){var r=-1e18;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++)r=Math.max(r,d[q].h);return r;}
  function minL(a,b){var r=1e18;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++)r=Math.min(r,d[q].l);return r;}
  function avgRg(a,b){var s=0,c=0;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++){s+=d[q].h-d[q].l;c++;}return c?s/c:0;}
  function volA(a,b){var s=0,c=0;a=Math.max(0,a);b=Math.min(n-1,b);for(var q=a;q<=b;q++){if(d[q].v===undefined)return null;s+=d[q].v;c++;}return c?s/c:null;}
  function push1(o){for(var q=0;q<found.length;q++)if(found[q].n===o.n&&found[q].i===o.i)return;found.push(o);}
  for(i=5;i<zz.length;i++){
    var seg=zz.slice(i-5,i+1);
    var tops=seg.filter(function(p){return p.tp===1;}),bots=seg.filter(function(p){return p.tp===-1;});
    if(tops.length<2||bots.length<2)continue;
    var tS=slope(tops,function(p){return d[p.i].h;}),bS=slope(bots,function(p){return d[p.i].l;});
    var ref=d[seg[5].i].c,eps=ref*0.0015;
    var bb1=bots[bots.length-2],bb2=bots[bots.length-1],tt1=tops[tops.length-2],tt2=tops[tops.length-1];
    var end=seg[5].i,lim=Math.min(n-1,end+10);
    if(tS>eps&&bS>tS*1.3){
      var railS=(d[bb2.i].l-d[bb1.i].l)/(bb2.i-bb1.i);
      for(j=end+1;j<=lim;j++){
        if(d[j].c<d[bb2.i].l+railS*(j-bb2.i)){push1({i:j,i2:seg[0].i,mid:seg[2].i,n:'楔形破位',dir:-1});break;}
      }
    }else if(tS<-eps&&bS<0&&bS>tS){
      var railS2=(d[tt2.i].h-d[tt1.i].h)/(tt2.i-tt1.i);
      for(j=end+1;j<=lim;j++){
        if(d[j].c>d[tt2.i].h+railS2*(j-tt2.i)){push1({i:j,i2:seg[0].i,mid:seg[2].i,n:'楔形破位',dir:1});break;}
      }
    }
  }
  for(i=12;i<n;i++){
    for(var fl=4;fl<=8;fl++){
      var pe=i-fl;if(pe<1)break;
      var ps=Math.max(0,pe-8);
      var pr1=d[pe].c/d[ps].o-1;
      if(Math.abs(pr1)<0.10)continue;
      var hf=Math.floor(fl/2);
      var hA=maxH(pe+1,pe+hf),hB=maxH(pe+hf+1,i);
      var lA=minL(pe+1,pe+hf),lB=minL(pe+hf+1,i);
      if(hB<hA*0.995&&lB>lA*1.005&&(hA-lA)/d[pe].c<=0.06){
        push1({i:i,i2:ps,mid:pe,n:'三角旗',dir:pr1>0?1:-1});
        break;
      }
    }
  }
  for(i=3;i<zz.length;i++){
    var c1=zz[i-3],c2=zz[i-2],c3=zz[i-1],c4=zz[i];
    if(c1.tp===1&&c2.tp===-1&&c3.tp===1&&c4.tp===-1){
      var r1=d[c1.i].h,r2=d[c3.i].h,cb=d[c2.i].l;
      var rim=(r1+r2)/2,dep=(rim-cb)/rim;
      if(Math.abs(r1-r2)/r1<=0.05&&dep>=0.08&&dep<=0.33&&(c3.i-c1.i)>=20){
        var loI=c1.i,loV=1e18;
        for(j=c1.i;j<=c3.i;j++){if(d[j].l<loV){loV=d[j].l;loI=j;}}
        var pos=(loI-c1.i)/(c3.i-c1.i);
        var hd=(r2-d[c4.i].l)/(rim-cb);
        if(pos>=0.25&&pos<=0.75&&hd>0&&hd<=0.40&&d[c4.i].l>cb)
          push1({i:c4.i,i2:c1.i,mid:c2.i,n:'杯柄形',dir:1});
      }
    }
    if(c1.tp===-1&&c2.tp===1&&c3.tp===-1&&c4.tp===1){
      var e1=d[c1.i].l,e2=d[c3.i].l,ct=d[c2.i].h;
      var rim2=(e1+e2)/2,hgt=(ct-rim2)/rim2;
      if(Math.abs(e1-e2)/e1<=0.05&&hgt>=0.08&&hgt<=0.33&&(c3.i-c1.i)>=20){
        var hiI=c1.i,hiV=-1e18;
        for(j=c1.i;j<=c3.i;j++){if(d[j].h>hiV){hiV=d[j].h;hiI=j;}}
        var pos2=(hiI-c1.i)/(c3.i-c1.i);
        var hb=(d[c4.i].h-e2)/(ct-rim2);
        if(pos2>=0.25&&pos2<=0.75&&hb>0&&hb<=0.40&&d[c4.i].h<ct)
          push1({i:c4.i,i2:c1.i,mid:c2.i,n:'倒杯柄形',dir:-1});
      }
    }
  }
  var WL=[24,36,48];
  for(var wi=0;wi<3;wi++){
    var LN=WL[wi],qp=Math.floor(LN/4);
    for(i=LN-1;i<n;i+=2){
      var st=i-LN+1,m0=0,m1=0,m2=0,m3=0,c0=0,cc1=0,cc2=0,c3=0;
      for(j=0;j<LN;j++){
        var gg=Math.min(3,Math.floor(j/qp));
        if(gg===0){m0+=d[st+j].c;c0++;}else if(gg===1){m1+=d[st+j].c;cc1++;}
        else if(gg===2){m2+=d[st+j].c;cc2++;}else{m3+=d[st+j].c;c3++;}
      }
      m0/=c0;m1/=cc1;m2/=cc2;m3/=c3;
      var rUp=(m1-m0)/m0,rDn=(m2-m3)/m2;
      if(m1>m0&&m2>=m1*0.995&&m3<m2&&rUp>=0.02&&rUp<=0.15&&rDn>0&&Math.abs(rUp-rDn)/rUp<=0.6)
        push1({i:i,i2:st,mid:st+Math.floor(LN/2),n:'圆弧顶',dir:-1});
      var bDn=(m0-m1)/m1,bUp=(m3-m2)/m3;
      if(m1<m0&&m2<=m1*1.005&&m3>m2&&bDn>=0.02&&bDn<=0.15&&bUp>0&&Math.abs(bDn-bUp)/bDn<=0.6)
        push1({i:i,i2:st,mid:st+Math.floor(LN/2),n:'圆弧底',dir:1});
    }
  }
  for(i=5;i<zz.length;i++){
    var sg6=zz.slice(i-5,i+1);
    var tp6=sg6.filter(function(p){return p.tp===1;}),bt6=sg6.filter(function(p){return p.tp===-1;});
    if(tp6.length<2||bt6.length<2)continue;
    var tS6=slope(tp6,function(p){return d[p.i].h;}),bS6=slope(bt6,function(p){return d[p.i].l;});
    var rf6=d[sg6[5].i].c,ep6=rf6*0.0015;
    if(tS6>ep6&&bS6<-ep6
      &&(d[tp6[tp6.length-1].i].h-d[tp6[0].i].h)/d[tp6[0].i].h>=0.01
      &&(d[bt6[0].i].l-d[bt6[bt6.length-1].i].l)/d[bt6[0].i].l>=0.01)
      push1({i:sg6[5].i,i2:sg6[0].i,mid:sg6[2].i,n:'扩散喇叭形',dir:0});
  }
  for(i=7;i<zz.length;i++){
    var dm=zz.slice(i-7,i+1);
    var dtp=dm.filter(function(p){return p.tp===1;}),dbt=dm.filter(function(p){return p.tp===-1;});
    if(dtp.length!==4||dbt.length!==4)continue;
    var dh0=d[dtp[0].i].h,dh1=d[dtp[1].i].h,dh2=d[dtp[2].i].h,dh3=d[dtp[3].i].h;
    var dl0=d[dbt[0].i].l,dl1=d[dbt[1].i].l,dl2=d[dbt[2].i].l,dl3=d[dbt[3].i].l;
    if(!(dh1>dh0&&dh2>=dh1*0.99&&dh3<dh2&&dl1<dl0&&dl2<=dl1*1.01&&dl3>dl2))continue;
    var wide=(Math.max(dh1,dh2)-Math.min(dl1,dl2))/d[dm[4].i].c;
    if(wide<0.04)continue;
    push1({i:dm[7].i,i2:dm[0].i,mid:dm[4].i,n:'钻石形',dir:0});
  }
  for(i=10;i<n-3;i++){
    if(d[i].h>=maxH(i-10,i-1)&&d[i].h>=maxH(i+1,Math.min(n-1,i+10))){
      var li=i,lw=1e18;for(j=Math.max(0,i-10);j<i;j++){if(d[j].l<lw){lw=d[j].l;li=j;}}
      var ri=-1,rw=1e18;for(j=i+1;j<=Math.min(n-1,i+10);j++){if(d[j].l<rw){rw=d[j].l;ri=j;}}
      if(ri>0&&i-li>=2&&ri-i>=2&&(d[i].h-lw)/lw>=0.12&&(d[i].h-rw)/d[i].h>=0.12)
        push1({i:ri,i2:li,mid:i,n:'V形顶',dir:-1});
    }
    if(d[i].l<=minL(i-10,i-1)&&d[i].l<=minL(i+1,Math.min(n-1,i+10))){
      var hi2=i,hh2=-1e18;for(j=Math.max(0,i-10);j<i;j++){if(d[j].h>hh2){hh2=d[j].h;hi2=j;}}
      var ri2=-1,rw2=-1e18;for(j=i+1;j<=Math.min(n-1,i+10);j++){if(d[j].h>rw2){rw2=d[j].h;ri2=j;}}
      if(ri2>0&&i-hi2>=2&&ri2-i>=2&&(hh2-d[i].l)/hh2>=0.12&&(rw2-d[i].l)/d[i].l>=0.12)
        push1({i:ri2,i2:hi2,mid:i,n:'V形底',dir:1});
    }
  }
  for(i=2;i<n-1;i++){
    if(d[i].l>d[i-1].h*1.005){
      var islLo=d[i].l;
      for(j=i+1;j<=Math.min(n-1,i+3);j++){
        if(d[j].h<d[j-1].l*0.995&&d[j].h<islLo&&islLo>d[i-1].h){
          push1({i:j,i2:i-1,mid:Math.floor((i+j-1)/2),n:'岛形反转',dir:-1});
          break;
        }
        islLo=Math.min(islLo,d[j].l);
      }
    }
    if(d[i].h<d[i-1].l*0.995){
      var islHi=d[i].h;
      for(j=i+1;j<=Math.min(n-1,i+3);j++){
        if(d[j].l>d[j-1].h*1.005&&d[j].l>islHi&&islHi<d[i-1].l){
          push1({i:j,i2:i-1,mid:Math.floor((i+j-1)/2),n:'岛形反转',dir:1});
          break;
        }
        islHi=Math.max(islHi,d[j].h);
      }
    }
  }
  for(i=12;i<n-3;i++){
    if(d[i].l>minL(i-3,i-1)||d[i].l>minL(i+1,i+3))continue;
    var hiA=-1e18,hiI=i;
    for(j=Math.max(0,i-12);j<i;j++){if(d[j].h>hiA){hiA=d[j].h;hiI=j;}}
    var drp=(hiA-d[i].l)/hiA;if(drp<0.15)continue;
    var bh=-1e18,bi=-1;
    for(j=i+1;j<=Math.min(n-1,i+8);j++){if(d[j].h>bh){bh=d[j].h;bi=j;}}
    var rt=(bh-d[i].l)/(hiA-d[i].l);
    if(bi>0&&rt>=0.15&&rt<=0.5)push1({i:bi,i2:hiI,mid:i,n:'死猫跳',dir:-1});
  }
  for(i=4;i<zz.length;i++){
    var w1=zz[i-4],w2=zz[i-3],w3=zz[i-2],w4=zz[i-1],w5=zz[i];
    if(w5.i-w1.i<10)continue;
    if(w1.tp===-1&&w2.tp===1&&w3.tp===-1&&w4.tp===1&&w5.tp===-1){
      var wl1=d[w1.i].l,wl3=d[w3.i].l,wl5=d[w5.i].l;
      if(wl3<wl1&&wl5<wl3){
        var v13=wl1+(wl3-wl1)*(w5.i-w1.i)/(w3.i-w1.i);
        if(wl5<=v13*1.03&&wl5>=v13*0.94&&d[w4.i].h<d[w2.i].h)
          push1({i:w5.i,i2:w1.i,mid:w3.i,n:'沃尔夫浪',dir:1});
      }
    }
    if(w1.tp===1&&w2.tp===-1&&w3.tp===1&&w4.tp===-1&&w5.tp===1){
      var wh1=d[w1.i].h,wh3=d[w3.i].h,wh5=d[w5.i].h;
      if(wh3>wh1&&wh5>wh3){
        var v13b=wh1+(wh3-wh1)*(w5.i-w1.i)/(w3.i-w1.i);
        if(wh5>=v13b*0.97&&wh5<=v13b*1.06&&d[w4.i].l>d[w2.i].l)
          push1({i:w5.i,i2:w1.i,mid:w3.i,n:'沃尔夫浪',dir:-1});
      }
    }
  }
  for(i=3;i<zz.length;i++){
    var q1=zz[i-3],q2=zz[i-2],q3=zz[i-1],q4=zz[i];
    if(q1.tp===-1&&q2.tp===1&&q3.tp===-1&&q4.tp===1
      &&d[q3.i].l>d[q1.i].l&&d[q4.i].h>d[q2.i].h){
      for(j=q4.i+1;j<Math.min(n,q4.i+21);j++){
        if(d[j].c<d[q3.i].l){push1({i:j,i2:q1.i,mid:q4.i,n:'卡西莫多反转',dir:-1});break;}
      }
    }
    if(q1.tp===1&&q2.tp===-1&&q3.tp===1&&q4.tp===-1
      &&d[q3.i].h<d[q1.i].h&&d[q4.i].l<d[q2.i].l){
      for(j=q4.i+1;j<Math.min(n,q4.i+21);j++){
        if(d[j].c>d[q3.i].h){push1({i:j,i2:q1.i,mid:q4.i,n:'卡西莫多反转',dir:1});break;}
      }
    }
  }
  for(i=5;i<zz.length;i++){
    var s1=zz[i-5],s2=zz[i-4],s3=zz[i-3],s4=zz[i-2],s5=zz[i-1],s6=zz[i];
    if(s1.tp===-1&&s2.tp===1&&s3.tp===-1&&s4.tp===1&&s5.tp===-1&&s6.tp===1){
      var L1=d[s1.i].l,H1=d[s2.i].h,L2=d[s3.i].l,H2=d[s4.i].h,L3=d[s5.i].l,H3=d[s6.i].h;
      if(L2>L1&&L3>L2&&H2>H1&&H3>H2
        &&(H1-L2)<=(H1-L1)*0.45&&(H2-L3)<=(H2-L2)*0.45)
        push1({i:s6.i,i2:s1.i,mid:s3.i,n:'上升扇贝',dir:1});
    }
    if(s1.tp===1&&s2.tp===-1&&s3.tp===1&&s4.tp===-1&&s5.tp===1&&s6.tp===-1){
      var uH1=d[s1.i].h,uL1=d[s2.i].l,uH2=d[s3.i].h,uL2=d[s4.i].l,uH3=d[s5.i].h,uL3=d[s6.i].l;
      if(uH2<uH1&&uH3<uH2&&uL2<uL1&&uL3<uL2
        &&(uH2-uL1)<=(uH1-uL1)*0.45&&(uH3-uL2)<=(uH2-uL2)*0.45)
        push1({i:s6.i,i2:s1.i,mid:s3.i,n:'下降扇贝',dir:-1});
    }
  }
  for(i=4;i<zz.length;i++){
    var g1=zz[i-4],g2=zz[i-3],g3=zz[i-2],g4=zz[i-1],g5=zz[i];
    var ar=avgRg(Math.max(0,g1.i-20),g5.i);
    if(g1.tp===1&&g2.tp===-1&&g3.tp===1&&g4.tp===-1&&g5.tp===1){
      var pH1=d[g1.i].h,pH2=d[g3.i].h,pH3=d[g5.i].h;
      if(Math.abs(pH1-pH3)/pH1<=0.02&&pH2<=pH1*0.98
        &&g3.i-g1.i>=5&&g5.i-g3.i>=5
        &&(d[g1.i].h-d[g1.i].l)>=ar*1.5&&(d[g5.i].h-d[g5.i].l)>=ar*1.5)
        push1({i:g5.i,i2:g1.i,mid:g3.i,n:'牛角顶',dir:-1});
    }
    if(g1.tp===-1&&g2.tp===1&&g3.tp===-1&&g4.tp===1&&g5.tp===-1){
      var pL1=d[g1.i].l,pL2=d[g3.i].l,pL3=d[g5.i].l;
      if(Math.abs(pL1-pL3)/pL1<=0.02&&pL2>=pL1*1.02
        &&g3.i-g1.i>=5&&g5.i-g3.i>=5
        &&(d[g1.i].h-d[g1.i].l)>=ar*1.5&&(d[g5.i].h-d[g5.i].l)>=ar*1.5)
        push1({i:g5.i,i2:g1.i,mid:g3.i,n:'牛角底',dir:1});
    }
  }
  for(i=13;i<n;i++){
    var ar2=avgRg(i-12,i-2);
    if(Math.abs(d[i].h-d[i-1].h)/d[i].h<=0.005
      &&(d[i].h-d[i].l)>=ar2*1.5&&(d[i-1].h-d[i-1].l)>=ar2*1.5
      &&d[i].h>=maxH(i-12,i-2)&&d[i].c/d[i-11].o-1>=0.10)
      push1({i:i,i2:i-11,mid:i-1,n:'管道顶',dir:-1});
    if(Math.abs(d[i].l-d[i-1].l)/d[i].l<=0.005
      &&(d[i].h-d[i].l)>=ar2*1.5&&(d[i-1].h-d[i-1].l)>=ar2*1.5
      &&d[i].l<=minL(i-12,i-2)&&d[i].c/d[i-11].o-1<=-0.10)
      push1({i:i,i2:i-11,mid:i-1,n:'管道底',dir:1});
  }
  for(i=0;i<zz.length;i++){
    var pk=zz[i];
    if(pk.i<35)continue;
    var a0=pk.i-30,b0=pk.i-15;
    if(pk.tp===1){
      var sl1=(d[b0].c-d[a0].c)/(b0-a0);
      if(sl1<=0||sl1>d[a0].c*0.003)continue;
      var bmp=d[pk.i].h-d[b0].c,ldn=d[b0].c-d[a0].c;
      if(bmp/(pk.i-b0)<sl1*1.5||bmp<ldn*2)continue;
      for(j=pk.i+1;j<Math.min(n,pk.i+21);j++){
        if(d[j].c<d[a0].c+sl1*(j-a0)){push1({i:j,i2:a0,mid:pk.i,n:'冲高回撤反转顶',dir:-1});break;}
      }
    }else{
      var sl2=(d[b0].c-d[a0].c)/(b0-a0);
      if(sl2>=0||-sl2>d[a0].c*0.003)continue;
      var bmp2=d[b0].c-d[pk.i].l,ldn2=d[a0].c-d[b0].c;
      if(bmp2/(pk.i-b0)<-sl2*1.5||bmp2<ldn2*2)continue;
      for(j=pk.i+1;j<Math.min(n,pk.i+21);j++){
        if(d[j].c>d[a0].c+sl2*(j-a0)){push1({i:j,i2:a0,mid:pk.i,n:'冲高回撤反转底',dir:1});break;}
      }
    }
  }
  for(i=4;i<zz.length;i++){
    var A1=Math.abs(zpr(zz[i-3])-zpr(zz[i-4])),A2=Math.abs(zpr(zz[i-2])-zpr(zz[i-3]));
    var A3=Math.abs(zpr(zz[i-1])-zpr(zz[i-2])),A4=Math.abs(zpr(zz[i])-zpr(zz[i-1]));
    if(!(A1>0&&A2<=A1*0.75&&A3<=A2*0.75&&A4<=A3*0.75))continue;
    if(A4/zpr(zz[i])>0.05)continue;
    var vF=volA(zz[i-4].i,zz[i-2].i),vL=volA(zz[i-2].i,zz[i].i);
    if(vF!==null&&vL!==null&&vL>=vF)continue;
    push1({i:zz[i].i,i2:zz[i-4].i,mid:zz[i-2].i,n:'波动收缩形态',dir:1});
  }
  for(i=2;i<zz.length;i++){
    var f1=zz[i-2],f2=zz[i-1],f3=zz[i];
    if(f1.tp===-1&&f2.tp===1&&f3.tp===-1){
      var lo1=d[f1.i].l,hh3=d[f2.i].h,lo3=d[f3.i].l;
      if(lo3>lo1&&(hh3-lo3)<=(hh3-lo1)*0.786&&(f3.i-f1.i)>=6){
        for(j=f3.i+1;j<Math.min(n,f3.i+21);j++){
          if(d[j].c>hh3){push1({i:j,i2:f1.i,mid:f2.i,n:'一二三反转',dir:1});break;}
          if(d[j].c<lo3)break;
        }
      }
    }
    if(f1.tp===1&&f2.tp===-1&&f3.tp===1){
      var fh1=d[f1.i].h,fl2=d[f2.i].l,fh3=d[f3.i].h;
      if(fh3<fh1&&(fh3-fl2)<=(fh1-fl2)*0.786&&(f3.i-f1.i)>=6){
        for(j=f3.i+1;j<Math.min(n,f3.i+21);j++){
          if(d[j].c<fl2){push1({i:j,i2:f1.i,mid:f2.i,n:'一二三反转',dir:-1});break;}
          if(d[j].c>fh3)break;
        }
      }
    }
  }
  for(i=4;i<zz.length;i++){
    var k1=zz[i-4],k2=zz[i-3],k3=zz[i-2],k4=zz[i-1],k5=zz[i];
    if(k5.i-k1.i>40)continue;
    if(k1.tp===-1&&k2.tp===1&&k3.tp===-1&&k4.tp===1&&k5.tp===-1){
      if(d[k3.i].l>d[k1.i].l&&d[k4.i].h>d[k2.i].h&&d[k5.i].l>d[k3.i].l*0.98)
        push1({i:k5.i,i2:k1.i,mid:k4.i,n:'罗斯钩',dir:1});
    }
    if(k1.tp===1&&k2.tp===-1&&k3.tp===1&&k4.tp===-1&&k5.tp===1){
      if(d[k3.i].h<d[k1.i].h&&d[k4.i].l<d[k2.i].l&&d[k5.i].h<d[k3.i].h*1.02)
        push1({i:k5.i,i2:k1.i,mid:k4.i,n:'罗斯钩',dir:-1});
    }
  }
  for(i=2;i<zz.length;i++){
    var W1=zz[i-2],W2=zz[i-1],W3=zz[i];
    if(W3.i-W1.i<30)continue;
    if(W1.tp===-1&&W2.tp===1&&W3.tp===-1){
      var bl1=d[W1.i].l,bl3=d[W3.i].l,bnk=d[W2.i].h;
      if(Math.abs(bl1-bl3)/bl1<=0.05&&(bnk-Math.max(bl1,bl3))/bnk>=0.05){
        var lwg=maxH(W1.i-20,W1.i-1);
        if((lwg-bl1)/lwg>=0.15){
          for(j=W3.i+1;j<Math.min(n,W3.i+26);j++){
            if(d[j].c>=bl3+(bnk-bl3)*0.5){push1({i:j,i2:W1.i,mid:W2.i,n:'大W底',dir:1});break;}
          }
        }
      }
    }
    if(W1.tp===1&&W2.tp===-1&&W3.tp===1){
      var th1=d[W1.i].h,th3=d[W3.i].h,tvl=d[W2.i].l;
      if(Math.abs(th1-th3)/th1<=0.05&&(Math.min(th1,th3)-tvl)/th1>=0.05){
        var lwl=minL(W1.i-20,W1.i-1);
        if((th1-lwl)/lwl>=0.15){
          for(j=W3.i+1;j<Math.min(n,W3.i+26);j++){
            if(d[j].c<=th3-(th3-tvl)*0.5){push1({i:j,i2:W1.i,mid:W2.i,n:'大M顶',dir:-1});break;}
          }
        }
      }
    }
  }
  for(j=1;j<n;j++){
    var gu=d[j].l>d[j-1].h*1.005,gd=d[j].h<d[j-1].l*0.995;
    if(!gu&&!gd)continue;
    var gdir=gu?1:-1,fill3=false,fill5=false;
    for(k=j+1;k<=Math.min(n-1,j+5);k++){
      var filled=gu?(d[k].l<=d[j-1].h):(d[k].h>=d[j-1].l);
      if(filled){if(k-j<=3)fill3=true;fill5=true;break;}
    }
    var nn=null,dd=gdir;
    if(fill3){
      var mv=j>20?(d[j-1].c/d[j-20].c-1):0;
      if(gdir===1&&mv>=0.12){nn='缺口·衰竭型';dd=-1;}
      else if(gdir===-1&&mv<=-0.12){nn='缺口·衰竭型';dd=1;}
      else nn='缺口·普通型';
    }else if(!fill5){
      var r0=Math.max(0,j-15);
      var rh=maxH(r0,j-1),rl=minL(r0,j-1),rr=(rh-rl)/d[j-1].c;
      var mv2=j>10?(d[j-1].c/d[j-10].c-1):0;
      var vb=volA(j-20,j-1);
      if(rr<=0.08&&((gu&&d[j].l>rh)||(gd&&d[j].h<rl))
        &&(vb===null||d[j].v===undefined||d[j].v>=vb*1.5))nn='缺口·突破型';
      else if(gdir===1&&mv2>=0.06)nn='缺口·逃逸型';
      else if(gdir===-1&&mv2<=-0.06)nn='缺口·逃逸型';
      else nn='缺口·普通型';
    }
    if(nn)push1({i:j,i2:j-1,mid:j,n:nn,dir:dd});
  }
  for(i=8;i<zz.length;i++){
    var cx=zz.slice(i-8,i+1),okT=true,okB=true;
    for(k=0;k<9;k++){
      if(cx[k].tp!==(k%2===0?1:-1))okT=false;
      if(cx[k].tp!==(k%2===0?-1:1))okB=false;
    }
    if(okT){
      var x1=d[cx[0].i].h,x2=d[cx[2].i].h,xh=d[cx[4].i].h,x3=d[cx[6].i].h,x4=d[cx[8].i].h;
      var xls=(x1+x2)/2,xrs=(x3+x4)/2;
      if(xh>x1*1.015&&xh>x2*1.015&&xh>x3*1.015&&xh>x4*1.015
        &&Math.abs(x1-x2)/x1<=0.05&&Math.abs(x3-x4)/x3<=0.05
        &&Math.abs(xls-xrs)/xls<=0.06
        &&flat([cx[1],cx[3],cx[5],cx[7]],function(p){return d[p.i].l;},0.05)
        &&cx[8].i-cx[0].i>=20)
        push1({i:cx[8].i,i2:cx[0].i,mid:cx[4].i,n:'复合头肩',dir:-1});
    }
    if(okB){
      var y1=d[cx[0].i].l,y2=d[cx[2].i].l,yh=d[cx[4].i].l,y3=d[cx[6].i].l,y4=d[cx[8].i].l;
      var yls=(y1+y2)/2,yrs=(y3+y4)/2;
      if(yh<y1*0.985&&yh<y2*0.985&&yh<y3*0.985&&yh<y4*0.985
        &&Math.abs(y1-y2)/y1<=0.05&&Math.abs(y3-y4)/y3<=0.05
        &&Math.abs(yls-yrs)/yls<=0.06
        &&flat([cx[1],cx[3],cx[5],cx[7]],function(p){return d[p.i].h;},0.05)
        &&cx[8].i-cx[0].i>=20)
        push1({i:cx[8].i,i2:cx[0].i,mid:cx[4].i,n:'复合头肩',dir:1});
    }
  }
  for(i=12;i<n;i++){
    for(var fl2=3;fl2<=5;fl2++){
      var pe2=i-fl2;
      var pr2=d[pe2].c/d[Math.max(0,pe2-8)].o-1;
      if(pr2<0.15)continue;
      var fr2=(maxH(pe2+1,i)-minL(pe2+1,i))/d[pe2].c;
      if(fr2>0.04)continue;
      var vp=volA(pe2-8,pe2),vf=volA(pe2+1,i);
      if(vp!==null&&vf!==null&&vf>=vp)continue;
      push1({i:i,i2:Math.max(0,pe2-8),mid:pe2,n:'高紧旗',dir:1});
      break;
    }
  }
  return found;
}
/* ---- I-1 第四批：CHART A股特色/打板族 12 + TD序列 2 + 民间形态 5 + 布鲁克斯 1 = 20 规则（PAT-CHART-027~038、052~056、062） ---- */
function chartPats4(d){
  var n=d.length,found=[],i,j,k;
  var zz=zigzagPts(d);
  function maAt(x,p){var s=Math.max(0,x-p+1),sum=0,cnt=0;for(var t=s;t<=x;t++){sum+=d[t].c;cnt++;}return cnt?sum/cnt:d[x].c;}
  function vok(x){return x>=0&&x<n&&typeof d[x].v==='number'&&d[x].v>0;}
  function anyV(a,b){for(var t=a;t<=b;t++){if(vok(t))return true;}return false;}
  function avgV(a,b){var sum=0,cnt=0;for(var t=a;t<=b;t++){if(vok(t)){sum+=d[t].v;cnt++;}}return cnt?sum/cnt:0;}
  function lu(x){return x>=1&&d[x].c>=d[x-1].c*1.098;}
  function ld(x){return x>=1&&d[x].c<=d[x-1].c*0.902;}
  function luP(x){return x>=1?d[x-1].c*1.098:1e18;}
  for(i=2;i<n;i++){
    if(lu(i)&&(d[i-1].c<d[i-1].o||ld(i-1)||d[i-1].c<=d[i-2].c*0.95)&&d[i].c>d[i-1].o)
      found.push({i:i,i2:i-1,mid:i,n:'反包涨停',dir:1});
  }
  for(i=3;i<n;i++){
    if(!lu(i))continue;
    for(j=Math.max(1,i-11);j<=i-2;j++){
      if(!lu(j))continue;
      var hh28=-1e18,ll28=1e18;
      for(k=j+1;k<i;k++){hh28=Math.max(hh28,d[k].h);ll28=Math.min(ll28,d[k].l);}
      if((hh28-ll28)/d[j].c>0.08)continue;
      if(anyV(j+1,i-1)&&vok(j)&&avgV(j+1,i-1)>=d[j].v)continue;
      found.push({i:i,i2:j,mid:j+1+Math.floor((i-j-1)/2),n:'涨停双响炮',dir:1});
      break;
    }
  }
  var a29=0;
  while(a29<n-3){
    var rim=d[a29].c,b29=-1,blo=1e18;
    for(k=a29+1;k<=Math.min(n-1,a29+5);k++){if(d[k].l<blo){blo=d[k].l;b29=k;}}
    if(b29>0&&rim>0&&(rim-blo)/rim>=0.10){
      var vsh=true;
      if(anyV(Math.max(0,b29-1),Math.min(n-1,b29+1))&&anyV(Math.max(0,a29-5),a29-1))
        vsh=avgV(Math.max(0,b29-1),Math.min(n-1,b29+1))<avgV(Math.max(0,a29-5),a29-1);
      var rec=-1;
      for(k=b29+1;k<=Math.min(n-1,b29+10);k++){if(d[k].c>=blo+0.8*(rim-blo)){rec=k;break;}}
      if(rec>0&&vsh){found.push({i:rec,i2:a29,mid:b29,n:'黄金坑',dir:1});a29=rec+1;continue;}
    }
    a29++;
  }
  for(i=9;i<n;i++){
    var g30=d[i-9].c>0?d[i].c/d[i-9].c-1:0;
    if(g30<0.05||g30>0.15)continue;
    var sy=0,burst=false;
    for(k=i-9;k<=i;k++){var bd=(d[k].c-d[k].o)/d[k].o;if(bd>0&&bd<0.012)sy++;}
    if(sy<7)continue;
    if(anyV(i-9,i)){var av30=avgV(i-9,i);for(k=i-9;k<=i;k++){if(vok(k)&&d[k].v>2*av30){burst=true;break;}}}
    if(!burst)found.push({i:i,i2:i-9,mid:i-4,n:'碎阳慢涨',dir:1});
  }
  for(i=59;i<n;i++){
    var hi60=-1e18,lo60=1e18;
    for(k=i-59;k<=i;k++){hi60=Math.max(hi60,d[k].h);lo60=Math.min(lo60,d[k].l);}
    if(hi60<=lo60||(d[i].c-lo60)/(hi60-lo60)>0.334)continue;
    var hh31=-1e18,ll31=1e18;
    for(k=i-14;k<=i;k++){hh31=Math.max(hh31,d[k].h);ll31=Math.min(ll31,d[k].l);}
    if((hh31-ll31)/ll31>0.12)continue;
    var m5=maAt(i,5),m10=maAt(i,10),m20=maAt(i,20);
    var mMx=Math.max(m5,Math.max(m10,m20)),mMn=Math.min(m5,Math.min(m10,m20));
    if(mMn>0&&(mMx-mMn)/mMn<=0.03)found.push({i:i,i2:i-14,mid:i-7,n:'低位箱体蓄势',dir:0});
  }
  for(i=1;i<n;i++){
    if(!lu(i))continue;
    var frst=true;
    for(j=Math.max(1,i-60);j<i;j++){if(lu(j)){frst=false;break;}}
    if(frst&&!(i<n-1&&lu(i+1)))found.push({i:i,i2:Math.max(0,i-1),mid:i,n:'首板试盘',dir:1});
  }
  for(i=2;i<n;i++){
    if(!lu(i))continue;
    var s33=i;while(s33-1>=1&&lu(s33-1))s33--;
    var cbn=i-s33+1;
    if(cbn>=2&&(i+1>=n||!lu(i+1)))
      found.push({i:i,i2:s33,mid:s33+Math.floor((cbn-1)/2),n:'连板×'+cbn,dir:1});
  }
  for(i=3;i<n;i++){
    var e34=-1;
    for(j=i-1;j>=Math.max(1,i-3);j--){if(lu(j)){e34=j;break;}}
    if(e34<0)continue;
    var s34=e34;while(s34-1>=1&&lu(s34-1))s34--;
    if(e34-s34+1<2)continue;
    var dd34=0;
    for(k=e34+1;k<=i;k++){dd34=Math.max(dd34,(d[e34].c-d[k].l)/d[e34].c);}
    if(dd34>=0.06)continue;
    if(anyV(e34+1,i)&&vok(e34)&&avgV(e34+1,i)>=d[e34].v)continue;
    found.push({i:i,i2:s34,mid:e34,n:'断板温和洗盘',dir:0});
  }
  for(i=1;i<n;i++){
    var lp35=luP(i);
    if(d[i].h>=lp35&&d[i].c>=lp35&&d[i].l<lp35)found.push({i:i,i2:i-1,mid:i,n:'烂板回封',dir:0});
  }
  for(i=1;i<n;i++){
    var lp36=luP(i);
    if(d[i].c<lp36)continue;
    var core=(d[i].o+d[i].h+d[i].l+d[i].c)/4;
    if(core>lp36*0.97)continue;
    if(anyV(Math.max(0,i-5),i-1)&&vok(i)&&d[i].v>1.2*avgV(Math.max(0,i-5),i-1))continue;
    found.push({i:i,i2:Math.max(0,i-1),mid:i,n:'尾盘偷袭板',dir:0});
  }
  var cB=0,cS=0;
  for(i=4;i<n;i++){
    cB=d[i].c<d[i-4].c?cB+1:0;
    cS=d[i].c>d[i-4].c?cS+1:0;
    if(cB===9)found.push({i:i,i2:i-8,mid:i-4,n:'TD买9',dir:1});
    if(cS===9)found.push({i:i,i2:i-8,mid:i-4,n:'TD卖9',dir:-1});
  }
  var st52=0,g52=-1,p52=-1;
  for(i=61;i<n;i++){
    var f5=maAt(i,5),mA=maAt(i,10),s60=maAt(i,60),pf5=maAt(i-1,5),pmA=maAt(i-1,10);
    if(st52===0){
      if(f5>mA&&pf5<=pmA&&f5>s60){st52=1;g52=i;}
    }else if(st52===1){
      if(f5<s60*0.98||i-g52>25){st52=0;}
      else if(i-g52>=2&&f5<=mA*1.01){st52=2;p52=i;}
    }else{
      if(f5<s60*0.98||i-p52>15){st52=0;}
      else if(f5<=mA*1.01){p52=i;}
      else if(f5>mA&&pf5<=pmA*1.01){found.push({i:i,i2:g52,mid:p52,n:'老鸭头',dir:1});st52=0;}
    }
  }
  for(i=4;i<n;i++){
    for(var b53=Math.max(1,i-5);b53<=i-3;b53++){
      var bdB=(d[b53].c-d[b53].o)/d[b53].o;
      if(bdB<0.05)continue;
      if(b53>=20&&d[b53].c<d[b53-20].c*1.08)continue;
      var hh53=-1e18,ll53=1e18;
      for(k=b53+1;k<=i;k++){hh53=Math.max(hh53,d[k].h);ll53=Math.min(ll53,d[k].l);}
      if((hh53-ll53)/d[b53].c>0.05)continue;
      if(ll53<(d[b53].o+d[b53].c)/2)continue;
      found.push({i:i,i2:b53,mid:b53+1+Math.floor((i-b53-1)/2),n:'空中加油',dir:1});
      break;
    }
  }
  for(i=4;i<zz.length;i++){
    var z1=zz[i-4],z2=zz[i-3],z3=zz[i-2],z4=zz[i-1],z5=zz[i];
    if(z1.tp===1&&z2.tp===-1&&z3.tp===1&&z4.tp===-1&&z5.tp===1&&(z5.i-z1.i)>=10){
      var hh1=d[z1.i].h,hh2=d[z3.i].h,hh3=d[z5.i].h;
      if(hh2<hh1&&hh3<hh2){
        found.push({i:z5.i,i2:z1.i,mid:z3.i,n:'三降峰',dir:-1});
        if(d[z4.i].l<d[z2.i].l)found.push({i:z5.i,i2:z1.i,mid:z3.i,n:'三峰穹顶',dir:-1});
      }
    }
    if(z1.tp===-1&&z2.tp===1&&z3.tp===-1&&z4.tp===1&&z5.tp===-1&&(z5.i-z1.i)>=10){
      var bb1=d[z1.i].l,bb2=d[z3.i].l,bb3=d[z5.i].l;
      if(bb2>bb1&&bb3>bb2)found.push({i:z5.i,i2:z1.i,mid:z3.i,n:'三升谷',dir:1});
    }
  }
  for(i=3;i<zz.length;i++){
    var wA=zz[i-3],wB=zz[i-2],wC=zz[i-1],wD=zz[i];
    if(wA.tp===1&&wB.tp===-1&&wC.tp===1&&wD.tp===-1&&(wD.i-wA.i)>=6
      &&d[wC.i].h<d[wA.i].h&&d[wD.i].l>=d[wB.i].l*0.99&&d[wA.i].c>maAt(wA.i,20))
      found.push({i:wD.i,i2:wA.i,mid:wB.i,n:'H2回调买点',dir:1});
    if(wA.tp===-1&&wB.tp===1&&wC.tp===-1&&wD.tp===1&&(wD.i-wA.i)>=6
      &&d[wC.i].l>d[wA.i].l&&d[wD.i].h<=d[wB.i].h*1.01&&d[wA.i].c<maAt(wA.i,20))
      found.push({i:wD.i,i2:wA.i,mid:wB.i,n:'L2反弹卖点',dir:-1});
  }
  return found;
}
/* ---- I-1 第四批：TREND 族 13 规则（PAT-TREND-001~013） ---- */
function trendPats(d){
  var n=d.length,found=[],i,j,k;
  if(n<2) return found;
  var zz=zigzagPts(d);
  function maAt(idx,p){
    if(idx<p-1) return null;
    var s=0; for(var q=idx-p+1;q<=idx;q++) s+=d[q].c;
    return s/p;
  }
  function linfit(pts,acc){
    var m=pts.length,sx=0,sy=0,sxy=0,sxx=0,v;
    for(var q=0;q<m;q++){ v=acc(pts[q]); sx+=pts[q].i; sy+=v; sxy+=pts[q].i*v; sxx+=pts[q].i*pts[q].i; }
    var den=m*sxx-sx*sx; if(!den) return null;
    var a=(m*sxy-sx*sy)/den;
    return [a,(sy-a*sx)/m];
  }
  function atrAvg(len){
    var s=0,c=0,q,tr;
    for(q=Math.max(1,n-len);q<n;q++){
      tr=Math.max(d[q].h-d[q].l,Math.abs(d[q].h-d[q-1].c),Math.abs(d[q].l-d[q-1].c));
      s+=tr; c++;
    }
    return c?s/c:0;
  }
  for(i=1;i<n;i++){
    var f0=maAt(i-1,5),s0=maAt(i-1,20),f1=maAt(i,5),s1=maAt(i,20);
    if(f0===null||s0===null||f1===null||s1===null) continue;
    if(f0<=s0&&f1>s1) found.push({i:i,i2:Math.max(0,i-3),mid:Math.max(0,i-1),n:'均线金叉',dir:1});
    else if(f0>=s0&&f1<s1) found.push({i:i,i2:Math.max(0,i-3),mid:Math.max(0,i-1),n:'均线死叉',dir:-1});
  }
  if(n>=60){
    var m5=maAt(n-1,5),m10=maAt(n-1,10),m20=maAt(n-1,20),m60=maAt(n-1,60);
    var an='均线缠绕',ad=0;
    if(m5>m10&&m10>m20&&m20>m60){ an='均线多头排列'; ad=1; }
    else if(m5<m10&&m10<m20&&m20<m60){ an='均线空头排列'; ad=-1; }
    found.push({i:n-1,i2:n-3,mid:n-2,n:an,dir:ad});
  }
  var bots=[],tops=[];
  for(i=0;i<zz.length;i++){ if(zz[i].tp===1) tops.push(zz[i]); else bots.push(zz[i]); }
  var upFit=null,dnFit=null;
  if(bots.length>=3){
    var bs=bots.slice(-3),fu=linfit(bs,function(p){return d[p.i].l;});
    if(fu&&fu[0]>0&&(bs[2].i-bs[0].i)>=8
      &&Math.abs(d[bs[2].i].l-(fu[0]*bs[2].i+fu[1]))/d[bs[2].i].l<0.015){
      upFit={f:fu,pts:bs};
      found.push({i:bs[2].i,i2:bs[0].i,mid:bs[1].i,n:'上升趋势线',dir:1});
    }
  }
  if(tops.length>=3){
    var ts=tops.slice(-3),fd=linfit(ts,function(p){return d[p.i].h;});
    if(fd&&fd[0]<0&&(ts[2].i-ts[0].i)>=8
      &&Math.abs(d[ts[2].i].h-(fd[0]*ts[2].i+fd[1]))/d[ts[2].i].h<0.015){
      dnFit={f:fd,pts:ts};
      found.push({i:ts[2].i,i2:ts[0].i,mid:ts[1].i,n:'下降趋势线',dir:-1});
    }
  }
  if(upFit){
    var inT=[],w=0,wi=-1;
    for(i=0;i<tops.length;i++) if(tops[i].i>=upFit.pts[0].i&&tops[i].i<=upFit.pts[2].i) inT.push(tops[i]);
    for(i=0;i<inT.length;i++){
      var dv=d[inT[i].i].h-(upFit.f[0]*inT[i].i+upFit.f[1]);
      if(dv>w){ w=dv; wi=inT[i].i; }
    }
    if(inT.length>=2&&wi>=0&&w/d[wi].h>=0.01)
      found.push({i:upFit.pts[2].i,i2:upFit.pts[0].i,mid:wi,n:'上升通道',dir:1});
  }
  if(dnFit){
    var inB=[],w2=0,wi2=-1;
    for(i=0;i<bots.length;i++) if(bots[i].i>=dnFit.pts[0].i&&bots[i].i<=dnFit.pts[2].i) inB.push(bots[i]);
    for(i=0;i<inB.length;i++){
      var dv2=(dnFit.f[0]*inB[i].i+dnFit.f[1])-d[inB[i].i].l;
      if(dv2>w2){ w2=dv2; wi2=inB[i].i; }
    }
    if(inB.length>=2&&wi2>=0&&w2/d[wi2].l>=0.01)
      found.push({i:dnFit.pts[2].i,i2:dnFit.pts[0].i,mid:wi2,n:'下降通道',dir:-1});
  }
  if(zz.length>=6){
    var seg=zz.slice(-6),st=[],sb=[];
    for(i=0;i<6;i++){ if(seg[i].tp===1) st.push(seg[i]); else sb.push(seg[i]); }
    if(st.length>=2&&sb.length>=2){
      var th=0,bl=0,ok=true;
      for(i=0;i<st.length;i++) th+=d[st[i].i].h; th/=st.length;
      for(i=0;i<sb.length;i++) bl+=d[sb[i].i].l; bl/=sb.length;
      for(i=0;i<st.length;i++) if(Math.abs(d[st[i].i].h-th)/th>0.02) ok=false;
      for(i=0;i<sb.length;i++) if(Math.abs(d[sb[i].i].l-bl)/bl>0.02) ok=false;
      if(ok&&(seg[5].i-seg[0].i)>=20&&(th-bl)/bl>=0.01)
        found.push({i:seg[5].i,n:'水平箱体通道',dir:0,zone:{i1:seg[0].i,i2:n-1,p1:th,p2:bl}});
    }
  }
  if(zz.length>=3){
    var q1=zz[zz.length-3],q2=zz[zz.length-2],q3=zz[zz.length-1];
    if(q3.i-q1.i>=10)
      found.push({i:q3.i,i2:q1.i,mid:q2.i,n:'安德鲁音叉',dir:q1.tp===-1?1:-1});
  }
  if(bots.length>=1){
    var ai=bots[bots.length-1].i,atr=atrAvg(20);
    if(atr>0&&(n-1-ai)>=4)
      found.push({i:n-1,i2:ai,mid:ai+Math.floor((n-1-ai)/2),n:'江恩1x1角度线',dir:1});
  }
  if(bots.length>=1){
    var P0=d[bots[bots.length-1].i].l,rt=Math.sqrt(P0),gl=[];
    for(k=1;k<=8;k++){ var pk=rt+k*0.125; gl.push({p:pk*pk,t:'九方R'+k,col:'#C9A227'}); }
    found.push({i:n-1,n:'江恩九方图',dir:0,lvl:gl});
  }
  if(zz.length>=2){
    var T=zz[zz.length-1],B=zz[zz.length-2];
    if(T.tp===1&&B.tp===-1&&(T.i-B.i)>=8&&(d[T.i].h-d[B.i].l)/d[B.i].l>=0.05){
      var mi=B.i+Math.floor((T.i-B.i)/2);
      found.push({i:n-1,i2:B.i,mid:mi,n:'速度阻力线1/3',dir:1});
      found.push({i:n-1,i2:B.i,mid:mi,n:'速度阻力线2/3',dir:1});
    }
  }
  if(zz.length>=3){
    var g3=zz[zz.length-1];
    found.push({i:g3.i,i2:zz[zz.length-3].i,mid:zz[zz.length-2].i,n:'江恩摆动',dir:g3.tp===1?1:-1});
  }
  return found;
}
/* ---- I-1 第四批：SR 族 10 规则（PAT-SR-001~010） ---- */
function srPats(d){
  var n=d.length,found=[],i,j,k;
  if(n<2) return found;
  var zz=zigzagPts(d),tops=[];
  for(i=0;i<zz.length;i++) if(zz[i].tp===1) tops.push(zz[i]);
  for(i=tops.length-1;i>=0;i--){
    var t=tops[i];
    if(t.i>=n-2||t.i<n-40) continue;
    var res=d[t.i].h,bk=-1,bb=-1;
    for(j=t.i+1;j<n;j++){ if(d[j].h>res){ bk=j; break; } }
    if(bk<0) continue;
    for(j=bk;j<n&&j<=bk+2;j++){ if(d[j].c<res){ bb=j; break; } }
    if(bb>=0){ found.push({i:bb,i2:t.i,mid:bk,n:'压力位突破失败',dir:-1}); break; }
  }
  for(i=tops.length-1;i>=0;i--){
    var t2=tops[i];
    if(t2.i>=n-3||t2.i<n-60) continue;
    var rs2=d[t2.i].h,bo=-1,rt2=-1;
    for(j=t2.i+1;j<n;j++){ if(d[j].c>rs2*1.01){ bo=j; break; } }
    if(bo<0) continue;
    for(j=bo+1;j<n;j++){ if(d[j].l<=rs2*1.01&&d[j].c>rs2){ rt2=j; break; } }
    if(rt2>=0){ found.push({i:rt2,i2:t2.i,mid:bo,n:'支撑压力互换',dir:1}); break; }
  }
  if(n>=8){
    var ORH=-1e18,ORL=1e18;
    for(i=0;i<5;i++){ ORH=Math.max(ORH,d[i].h); ORL=Math.min(ORL,d[i].l); }
    var boI=-1,bdI=-1,slI=-1;
    for(i=5;i<n;i++){
      if(boI<0&&d[i].c>ORH) boI=i;
      if(bdI<0&&d[i].c<ORL) bdI=i;
      if(slI<0&&d[i].c<ORL*0.995) slI=i;
    }
    if(boI>=0) found.push({i:boI,i2:0,mid:4,n:'分时突破',dir:1});
    if(bdI>=0) found.push({i:bdI,i2:0,mid:4,n:'分时破位',dir:-1});
    if(slI>=0) found.push({i:slI,i2:0,mid:4,n:'止损破位',dir:-1});
  }
  var H=d[n-1].h,L=d[n-1].l,C=d[n-1].c,R=H-L,PP=(H+L+C)/3;
  found.push({i:n-1,n:'经典枢轴点',dir:0,lvl:[
    {p:H+2*(PP-L),t:'R3',col:'#CA3F64'},{p:PP+R,t:'R2',col:'#CA3F64'},{p:2*PP-L,t:'R1',col:'#CA3F64'},
    {p:PP,t:'PP',col:'#FFD54F'},
    {p:2*PP-H,t:'S1',col:'#25A750'},{p:PP-R,t:'S2',col:'#25A750'},{p:L-2*(H-PP),t:'S3',col:'#25A750'}
  ]});
  found.push({i:n-1,n:'斐波那契枢轴点',dir:0,lvl:[
    {p:PP+R,t:'R3',col:'#CA3F64'},{p:PP+0.618*R,t:'R2',col:'#CA3F64'},{p:PP+0.382*R,t:'R1',col:'#CA3F64'},
    {p:PP,t:'PP',col:'#FFD54F'},
    {p:PP-0.382*R,t:'S1',col:'#25A750'},{p:PP-0.618*R,t:'S2',col:'#25A750'},{p:PP-R,t:'S3',col:'#25A750'}
  ]});
  found.push({i:n-1,n:'卡玛利拉枢轴',dir:0,lvl:[
    {p:C+R*1.1/2,t:'R4',col:'#CA3F64'},{p:C+R*1.1/4,t:'R3',col:'#CA3F64'},
    {p:C+R*1.1/6,t:'R2',col:'#CA3F64'},{p:C+R*1.1/12,t:'R1',col:'#CA3F64'},
    {p:C-R*1.1/12,t:'S1',col:'#25A750'},{p:C-R*1.1/6,t:'S2',col:'#25A750'},
    {p:C-R*1.1/4,t:'S3',col:'#25A750'},{p:C-R*1.1/2,t:'S4',col:'#25A750'}
  ]});
  found.push({i:n-1,n:'昨日高低点',dir:0,lvl:[
    {p:d[n-2].h,t:'昨高',col:'#CA3F64'},{p:d[n-2].l,t:'昨低',col:'#25A750'}
  ]});
  var LB=Math.min(64,n),mh=-1e18,ml=1e18;
  for(i=n-LB;i<n;i++){ mh=Math.max(mh,d[i].h); ml=Math.min(ml,d[i].l); }
  if(mh>ml){
    var mv=[];
    for(k=0;k<=8;k++) mv.push({p:ml+(mh-ml)*k/8,t:'MML '+k+'/8',col:k===4?'#FFD54F':'#8D9E63'});
    found.push({i:n-1,n:'穆雷数学线',dir:0,lvl:mv});
  }
  var vh=-1e18,vl=1e18,vs=0,vc=0;
  for(i=0;i<n;i++){ vh=Math.max(vh,d[i].h); vl=Math.min(vl,d[i].l); if(d[i].v!==undefined){ vs+=d[i].v; vc++; } }
  if(vh>vl){
    var avgV=vc>0?vs/vc:1,NB=12,bw=(vh-vl)/NB,bins=[];
    for(i=0;i<NB;i++) bins.push(0);
    for(i=0;i<n;i++){
      var bi=Math.floor(((d[i].h+d[i].l+d[i].c)/3-vl)/bw);
      if(bi<0) bi=0; if(bi>=NB) bi=NB-1;
      bins[bi]+=(d[i].v!==undefined?d[i].v:Math.abs(d[i].c-d[i].o)*avgV);
    }
    var b1=0,b2=-1;
    for(i=1;i<NB;i++) if(bins[i]>bins[b1]) b1=i;
    for(i=0;i<NB;i++){ if(i>=b1-1&&i<=b1+1) continue; if(b2<0||bins[i]>bins[b2]) b2=i; }
    var vv=[{p:vl+(b1+0.5)*bw,t:'量能密集1',col:'#7E57C2'}];
    if(b2>=0&&bins[b2]>0) vv.push({p:vl+(b2+0.5)*bw,t:'量能密集2',col:'#7E57C2'});
    found.push({i:n-1,n:'成交量分布支撑阻力',dir:0,lvl:vv});
  }
  return found;
}
/* ---- I-1 第四批：FIB 斐波那契族 17 规则（PAT-FIB-001~017） ---- */
function fibPats(d){
  var n=d.length,found=[],i,k,j;
  var zz=zigzagPts(d);
  function pv(p){return p.tp===1?d[p.i].h:d[p.i].l;}
  function near(v,t,tol){return Math.abs(v-t)<=tol*t;}
  function inR(v,lo,hi,tol){return v>=lo*(1-tol)&&v<=hi*(1+tol);}
  function hit(P,dir,nm){found.push({i:P[4].i,i2:P[0].i,mid:P[3].i,n:nm,dir:dir});}
  var TOL=0.08;
  var leg=null;
  if(zz.length>=2){
    var LA=zz[zz.length-2],LB=zz[zz.length-1];
    var pA=pv(LA),pB=pv(LB);
    if(Math.abs(pB-pA)/pA>=0.05) leg={a:LA,b:LB,pA:pA,pB:pB,up:LB.tp===1};
  }
  if(leg){
    var span=leg.pB-leg.pA,bars=leg.b.i-leg.a.i,eI=leg.b.i;
    var rr=[0.236,0.382,0.5,0.618,0.786],lv1=[];
    for(k=0;k<rr.length;k++) lv1.push({p:leg.pB-rr[k]*span,t:(rr[k]*100).toFixed(1)+'%',col:'#C9A227'});
    found.push({i:eI,n:'斐波那契回撤',dir:leg.up?1:-1,lvl:lv1});
    var er=[1.272,1.618,2.618],lv2=[];
    for(k=0;k<er.length;k++) lv2.push({p:leg.pA+er[k]*span,t:(er[k]*100).toFixed(1)+'%',col:'#7E57C2'});
    found.push({i:eI,n:'斐波那契扩展',dir:leg.up?1:-1,lvl:lv2});
    var fr=[0.382,0.5,0.618],lv3=[];
    for(k=0;k<fr.length;k++){
      var anch=leg.pB-fr[k]*span;
      lv3.push({p:leg.pA+(anch-leg.pA)*(n-1-leg.a.i)/bars,t:'扇'+(fr[k]*100).toFixed(1)+'%',col:'#25A750'});
    }
    found.push({i:n-1,n:'斐波那契扇形',dir:leg.up?1:-1,lvl:lv3});
    var kS=span/bars,lv4=[];
    for(k=0;k<fr.length;k++){
      var R=fr[k]*Math.sqrt(2)*bars,dx=n-1-leg.b.i;
      var dy=dx<R?Math.sqrt(R*R-dx*dx):0;
      lv4.push({p:leg.pB-kS*dy,t:'弧'+(fr[k]*100).toFixed(1)+'%',col:'#AB47BC'});
    }
    found.push({i:n-1,n:'斐波那契弧形',dir:leg.up?1:-1,lvl:lv4});
    var tm=[1,1.618,2.618,4.236],lv5=[];
    for(k=0;k<tm.length;k++){
      var tb=leg.a.i+Math.round(tm[k]*bars);
      if(tb<n) lv5.push({p:d[tb].c,t:'T×'+tm[k]+'@'+tb,col:'#78909C'});
    }
    if(lv5.length) found.push({i:eI,n:'斐波那契时间区间',dir:0,lvl:lv5});
  }
  if(zz.length>=3){
    var m=zz.length,levs=[];
    var legs=[[zz[m-3],zz[m-2]],[zz[m-2],zz[m-1]]];
    var r1=[0.382,0.5,0.618],e1=[1.272,1.618];
    for(k=0;k<2;k++){
      var pa=pv(legs[k][0]),pb=pv(legs[k][1]),sp=pb-pa;
      if(!sp) continue;
      for(j=0;j<r1.length;j++) levs.push(pb-r1[j]*sp);
      for(j=0;j<e1.length;j++) levs.push(pa+e1[j]*sp);
    }
    levs.sort(function(a,b){return a-b;});
    var cl=[],cur=[];
    for(k=0;k<levs.length;k++){
      if(cur.length&&Math.abs(levs[k]-cur[cur.length-1])/cur[cur.length-1]>0.008){cl.push(cur);cur=[];}
      cur.push(levs[k]);
    }
    if(cur.length) cl.push(cur);
    var lv6=[];
    for(k=0;k<cl.length;k++){
      if(cl[k].length>=2){
        var s=0;for(j=0;j<cl[k].length;j++) s+=cl[k][j];
        lv6.push({p:s/cl[k].length,t:'共振×'+cl[k].length,col:'#FF7043'});
      }
    }
    if(lv6.length) found.push({i:zz[m-1].i,n:'斐波那契共振簇',dir:0,lvl:lv6});
  }
  for(i=4;i<zz.length;i++){
    var P=[zz[i-4],zz[i-3],zz[i-2],zz[i-1],zz[i]];
    if(P[0].tp!==-P[1].tp||P[1].tp!==-P[2].tp||P[2].tp!==-P[3].tp||P[3].tp!==-P[4].tp) continue;
    var dir=P[4].tp===-1?1:-1;
    var pX=pv(P[0]),pA2=pv(P[1]),pB2=pv(P[2]),pC=pv(P[3]),pD=pv(P[4]);
    var XA=Math.abs(pA2-pX),AB=Math.abs(pB2-pA2),BC=Math.abs(pC-pB2),CD=Math.abs(pD-pC);
    var XC=Math.abs(pC-pX),XD=Math.abs(pD-pX);
    if(XA/pX<0.03) continue;
    if(!XA||!AB||!BC||!XC) continue;
    var rB=AB/XA,rC=BC/AB,rDXA=XD/XA,rDBC=CD/BC,rDXC=CD/XC,rCXA=XC/XA;
    if(near(rB,0.618,TOL)&&inR(rC,0.382,0.886,TOL)&&inR(rDBC,1.272,1.618,TOL)&&near(CD/AB,1,0.10)) hit(P,dir,'ABCD谐波形态');
    if(near(rB,0.618,TOL)&&near(rDXA,0.786,TOL)&&inR(rDBC,1.272,1.618,TOL)) hit(P,dir,'加特利形态');
    if(inR(rB,0.382,0.5,TOL)&&near(rDXA,0.886,TOL)&&inR(rDBC,1.618,2.618,TOL)) hit(P,dir,'蝙蝠形态');
    if(near(rB,0.382,TOL)&&near(rDXA,1.13,TOL)&&inR(rDBC,2.0,3.618,TOL)) hit(P,dir,'变体蝙蝠形态');
    if(near(rB,0.786,TOL)&&inR(rDXA,1.272,1.618,TOL)&&inR(rDBC,1.618,2.24,TOL)) hit(P,dir,'蝴蝶形态');
    if(inR(rB,0.382,0.618,TOL)&&near(rDXA,1.618,TOL)&&inR(rDBC,2.618,3.618,TOL)) hit(P,dir,'螃蟹形态');
    if(near(rB,0.886,TOL)&&near(rDXA,1.618,TOL)&&inR(rDBC,2.24,3.618,TOL)) hit(P,dir,'深螃蟹形态');
    if(inR(rB,1.13,1.618,TOL)&&inR(rDXC,0.886,1.13,TOL)&&inR(rDBC,1.618,2.24,TOL)) hit(P,dir,'鲨鱼形态');
    if(inR(rB,0.382,0.618,TOL)&&inR(rCXA,1.272,1.414,TOL)&&near(rDXC,0.786,TOL)) hit(P,dir,'赛弗形态');
    var g1=P[2].i-P[0].i,g2=P[4].i-P[2].i;
    var sym=Math.abs(g1-g2)/Math.max(g1,g2)<=0.3;
    var ladder=P[0].tp===1?(pB2>pX&&pD>pB2):(pB2<pX&&pD<pB2);
    if(inR(rB,1.272,1.618,TOL)&&inR(rDBC,1.272,1.618,TOL)&&sym&&ladder) hit(P,dir,'三推形态');
    if(inR(rB,1.13,1.618,TOL)&&inR(rC,1.618,2.24,TOL)&&near(rDBC,0.5,TOL)) hit(P,dir,'谐波5-0形态');
  }
  return found;
}
/* ---- I-1 第四批：STRUCT 威科夫/SMC/VSA + 供需区 + 开盘区间 + ELW 楔形 27 规则（PAT-STRUCT-001~016/019~025/037/038、PAT-ELW-007/008） ---- */
function structPats(d){
  var n=d.length,found=[],i,j;
  if(n<10)return found;
  var zz=zigzagPts(d);
  var vols=[],avgV=0,avgB=0,avgR=0;
  for(i=0;i<n;i++){
    var bd=Math.abs(d[i].c-d[i].o);
    vols.push((d[i].v!==undefined&&d[i].v!==null)?d[i].v:bd);
    avgV+=vols[i];avgB+=bd;avgR+=d[i].h-d[i].l;
  }
  avgV/=n;avgB/=n;avgR/=n;
  function body(x){return Math.abs(d[x].c-d[x].o);}
  function bmid(x){return (d[x].h+d[x].l)/2;}
  function flatZZ(pts,acc,tol){
    var mn=1e18,mx=-1e18;
    pts.forEach(function(p){var v=acc(p);if(v<mn)mn=v;if(v>mx)mx=v;});
    return mn>0&&(mx-mn)/mn<=tol;
  }
  function slopeZZ(pts,acc){
    var m=pts.length;if(m<2)return 0;
    var sx=0,sy=0,sxy=0,sxx=0;
    for(var q=0;q<m;q++){var v=acc(pts[q]);sx+=q;sy+=v;sxy+=q*v;sxx+=q*q;}
    var dn=m*sxx-sx*sx;if(!dn)return 0;
    return (m*sxy-sx*sy)/dn;
  }
  var topAt=[],botAt=[],trendAt=[],zi=0,lT=null,lB=null,tt=[],bb=[];
  for(i=0;i<n;i++){
    while(zi<zz.length&&zz[zi].i<i){
      if(zz[zi].tp===1){lT=zz[zi];tt.push(zz[zi]);}else{lB=zz[zi];bb.push(zz[zi]);}
      zi++;
    }
    topAt[i]=lT;botAt[i]=lB;
    if(tt.length>=2&&bb.length>=2){
      var tA=d[tt[tt.length-2].i].h,tB2=d[tt[tt.length-1].i].h;
      var bA=d[bb[bb.length-2].i].l,bB2=d[bb[bb.length-1].i].l;
      trendAt[i]=(tB2>tA&&bB2>bA)?1:(tB2<tA&&bB2<bA)?-1:0;
    }else trendAt[i]=0;
  }
  var lastChoch=0;
  for(i=1;i<n;i++){
    var zp=topAt[i],zb=botAt[i];
    if(zp){
      var zpP=d[zp.i].h;
      if(d[i].c>zpP&&d[i-1].c<=zpP){
        found.push({i:i,i2:zp.i,mid:zb?zb.i:zp.i,n:'结构突破BOS',dir:1});
        for(j=i-1;j>=Math.max(0,i-10);j--)
          if(d[j].c<d[j].o){found.push({i:i,n:'订单块OB',dir:1,zone:{i1:j,i2:i,p1:d[j].h,p2:d[j].l}});break;}
        if(trendAt[i]===-1&&lastChoch!==1){lastChoch=1;found.push({i:i,i2:zp.i,mid:zb?zb.i:zp.i,n:'性格转变CHoCH',dir:1});}
      }
      if(d[i].h>zpP*1.0005&&d[i-1].h<=zpP*1.0005)
        for(j=i;j<=Math.min(i+3,n-1);j++)
          if(d[j].c<zpP){found.push({i:j,i2:zp.i,mid:i,n:'流动性扫荡',dir:-1});break;}
    }
    if(zb){
      var zbP=d[zb.i].l;
      if(d[i].c<zbP&&d[i-1].c>=zbP){
        found.push({i:i,i2:zb.i,mid:zp?zp.i:zb.i,n:'结构突破BOS',dir:-1});
        for(j=i-1;j>=Math.max(0,i-10);j--)
          if(d[j].c>d[j].o){found.push({i:i,n:'订单块OB',dir:-1,zone:{i1:j,i2:i,p1:d[j].h,p2:d[j].l}});break;}
        if(trendAt[i]===1&&lastChoch!==-1){lastChoch=-1;found.push({i:i,i2:zb.i,mid:zp?zp.i:zb.i,n:'性格转变CHoCH',dir:-1});}
      }
      if(d[i].l<zbP*0.9995&&d[i-1].l>=zbP*0.9995)
        for(j=i;j<=Math.min(i+3,n-1);j++)
          if(d[j].c>zbP){found.push({i:j,i2:zb.i,mid:i,n:'流动性扫荡',dir:1});break;}
    }
  }
  var rg=null;
  if(zz.length>=6){
    var seg=zz.slice(-6);
    var st=seg.filter(function(p){return p.tp===1;}),sb=seg.filter(function(p){return p.tp===-1;});
    var span=seg[seg.length-1].i-seg[0].i;
    if(st.length>=2&&sb.length>=2&&span>=20
      &&flatZZ(st,function(p){return d[p.i].h;},0.03)&&flatZZ(sb,function(p){return d[p.i].l;},0.03)){
      var th=st.map(function(p){return d[p.i].h;}),bl=sb.map(function(p){return d[p.i].l;});
      var rTop=(Math.min.apply(null,th)+Math.max.apply(null,th))/2;
      var rBot=(Math.min.apply(null,bl)+Math.max.apply(null,bl))/2;
      var w0=Math.max(0,n-60),wHi=-1e18,wLo=1e18;
      for(i=w0;i<n;i++){wHi=Math.max(wHi,d[i].h);wLo=Math.min(wLo,d[i].l);}
      var third=(wHi-wLo)/3,pos2=(rTop+rBot)/2,kind=0;
      if(pos2<=wLo+third)kind=1;else if(pos2>=wHi-third)kind=-1;
      rg={i1:seg[0].i,i2:seg[seg.length-1].i,top:rTop,bot:rBot,kind:kind};
      if(kind===1)found.push({i:rg.i2,n:'威科夫吸筹区间',dir:1,zone:{i1:rg.i1,i2:rg.i2,p1:rTop,p2:rBot}});
      else if(kind===-1)found.push({i:rg.i2,n:'威科夫派发区间',dir:-1,zone:{i1:rg.i1,i2:rg.i2,p1:rTop,p2:rBot}});
    }
  }
  if(rg){
    var springI=-1,upI=-1,sosI=-1,sowI=-1,end2=Math.min(n-1,rg.i2+8);
    for(i=rg.i1+1;i<=end2;i++){
      if(springI<0&&d[i].l<rg.bot*0.995)
        for(j=i+1;j<=Math.min(i+5,n-1);j++)
          if(d[j].c>rg.bot){springI=j;found.push({i:j,i2:i,mid:(i+j)>>1,n:'威科夫弹簧',dir:1});break;}
      if(upI<0&&d[i].h>rg.top*1.005)
        for(j=i+1;j<=Math.min(i+5,n-1);j++)
          if(d[j].c<rg.top){upI=j;found.push({i:j,i2:i,mid:(i+j)>>1,n:'威科夫上冲',dir:-1});break;}
      if(sosI<0&&d[i].c>d[i].o&&d[i].c>rg.top&&d[i-1].c<=rg.top&&vols[i]>=1.5*avgV){
        sosI=i;found.push({i:i,i2:rg.i1,mid:(rg.i1+i)>>1,n:'威科夫强势信号SOS',dir:1});
      }
      if(sowI<0&&d[i].c<d[i].o&&d[i].c<rg.bot&&d[i-1].c>=rg.bot&&vols[i]>=1.5*avgV){
        sowI=i;found.push({i:i,i2:rg.i1,mid:(rg.i1+i)>>1,n:'威科夫弱势信号SOW',dir:-1});
      }
    }
    var ev1=Math.max(springI,sosI);
    if(ev1>0)for(i=ev1+1;i<=Math.min(ev1+15,n-1);i++)
      if(d[i].l<=rg.top*1.01&&d[i].c>rg.top){found.push({i:i,i2:ev1,mid:(ev1+i)>>1,n:'威科夫最后支撑点LPS',dir:1});break;}
    var ev2=Math.max(upI,sowI);
    if(ev2>0)for(i=ev2+1;i<=Math.min(ev2+15,n-1);i++)
      if(d[i].h>=rg.bot*0.99&&d[i].c<rg.bot){found.push({i:i,i2:ev2,mid:(ev2+i)>>1,n:'威科夫最后供给点LPSY',dir:-1});break;}
  }
  for(i=2;i<n;i++){
    if(d[i].l>d[i-2].h&&(d[i].l-d[i-2].h)/d[i-2].h>=0.001)
      found.push({i:i,n:'公允价值缺口FVG',dir:1,zone:{i1:i-2,i2:i,p1:d[i].l,p2:d[i-2].h}});
    if(d[i].h<d[i-2].l&&(d[i-2].l-d[i].h)/d[i].h>=0.001)
      found.push({i:i,n:'公允价值缺口FVG',dir:-1,zone:{i1:i-2,i2:i,p1:d[i-2].l,p2:d[i].h}});
  }
  function pool(pts,acc,nm,dir,col){
    var g=[];
    function flush(){
      if(g.length>=2){
        var pv2=0;g.forEach(function(p){pv2+=acc(p);});pv2/=g.length;
        found.push({i:g[g.length-1].i,n:nm+'×'+g.length,dir:dir,lvl:[{p:pv2,t:nm+'×'+g.length,col:col}]});
      }
    }
    for(var q=0;q<pts.length;q++){
      if(!g.length){g.push(pts[q]);continue;}
      var mn=1e18,mx=-1e18;
      g.concat([pts[q]]).forEach(function(p){var v=acc(p);if(v<mn)mn=v;if(v>mx)mx=v;});
      if((mx-mn)/mn<=0.0015)g.push(pts[q]);else{flush();g=[pts[q]];}
    }
    flush();
  }
  pool(zz.filter(function(p){return p.tp===1;}),function(p){return d[p.i].h;},'等高池',-1,'#FF8A65');
  pool(zz.filter(function(p){return p.tp===-1;}),function(p){return d[p.i].l;},'等低池',1,'#4DB6AC');
  if(zz.length>=2){
    var z1=zz[zz.length-2],z2=zz[zz.length-1];
    var pA=z1.tp===1?d[z1.i].h:d[z1.i].l,pB=z2.tp===1?d[z2.i].h:d[z2.i].l;
    found.push({i:z2.i,n:'溢价折价区',dir:0,lvl:[{p:(pA+pB)/2,t:'溢价/折价分界',col:'#FFD54F'}]});
  }
  for(i=1;i<n-1;i++){
    var rng=Math.max(d[i].h-d[i].l,1e-12),cpos=(d[i].c-d[i].l)/rng;
    if(vols[i]>=2*avgV&&body(i)>=1.5*avgB&&d[i].c<d[i].o&&cpos<=0.33&&d[i+1].c>=d[i].c)
      found.push({i:i+1,i2:i-1,mid:i,n:'VSA抛售高潮',dir:1});
    if(vols[i]>=2*avgV&&body(i)>=1.5*avgB&&d[i].c>d[i].o&&cpos>=0.67&&d[i+1].c<=d[i].c)
      found.push({i:i+1,i2:i-1,mid:i,n:'VSA买入高潮',dir:-1});
    var loS=Math.min(d[i].o,d[i].c)-d[i].l;
    if(vols[i]>=1.5*avgV&&loS>=2*body(i)&&d[i+1].c>=d[i].c)
      found.push({i:i+1,i2:i-1,mid:i,n:'VSA停止量',dir:1});
    if(vols[i]>=1.5*avgV&&d[i].c>d[i].o&&body(i)>=1.5*avgB&&d[i].c<bmid(i))
      found.push({i:i,i2:i-1,mid:i,n:'VSA伪上冲',dir:-1});
    if(i>=5){
      if(vols[i]<0.7*avgV&&body(i)<=0.5*avgB&&d[i].c<=d[i].o&&d[i-1].c<d[i-5].c)
        found.push({i:i,i2:i-2,mid:i-1,n:'VSA无供给',dir:1});
      if(vols[i]<0.7*avgV&&body(i)<=0.5*avgB&&d[i].c>=d[i].o&&d[i-1].c>d[i-5].c)
        found.push({i:i,i2:i-2,mid:i-1,n:'VSA无需求',dir:-1});
      if(vols[i]<avgV&&rng<=avgR&&d[i].c>bmid(i)&&d[i-1].c<d[i-5].c)
        found.push({i:i,i2:i-2,mid:i-1,n:'VSA测试bar',dir:1});
    }
  }
  if(n>=8){
    var oHi=-1e18,oLo=1e18,brkU=false,brkD=false;
    for(i=0;i<5;i++){oHi=Math.max(oHi,d[i].h);oLo=Math.min(oLo,d[i].l);}
    for(i=5;i<n;i++){
      if(!brkU&&d[i].c>oHi){brkU=true;found.push({i:i,i2:0,mid:4,n:'开盘区间突破(上)',dir:1});}
      if(!brkD&&d[i].c<oLo){brkD=true;found.push({i:i,i2:0,mid:4,n:'开盘区间突破(下)',dir:-1});}
      if(brkU&&brkD)break;
    }
  }
  for(i=3;i<n-1;i++){
    for(var bl2=3;bl2<=6;bl2++){
      if(i+bl2>=n)break;
      var bHi=-1e18,bLo=1e18;
      for(j=i;j<i+bl2;j++){bHi=Math.max(bHi,d[j].h);bLo=Math.min(bLo,d[j].l);}
      if((bHi-bLo)/bLo>0.03)continue;
      var dep=i+bl2,strong=body(dep)>=1.5*avgB;
      if((strong&&d[dep].c>d[dep].o&&d[dep].c>bHi)||d[dep].l>bHi){
        found.push({i:dep,n:'需求区',dir:1,zone:{i1:i,i2:dep,p1:bHi,p2:bLo}});i=dep;break;
      }
      if((strong&&d[dep].c<d[dep].o&&d[dep].c<bLo)||d[dep].h<bLo){
        found.push({i:dep,n:'供应区',dir:-1,zone:{i1:i,i2:dep,p1:bHi,p2:bLo}});i=dep;break;
      }
    }
  }
  if(zz.length>=5){
    var wg=zz.slice(-5);
    var wt=wg.filter(function(p){return p.tp===1;}),wb=wg.filter(function(p){return p.tp===-1;});
    if(wt.length>=2&&wb.length>=2){
      var tS=slopeZZ(wt,function(p){return d[p.i].h;}),bS=slopeZZ(wb,function(p){return d[p.i].l;});
      var eps=d[wg[wg.length-1].i].c*0.0015;
      var mv=d[wg[0].i].c/d[Math.max(0,wg[0].i-30)].c-1;
      if(tS>eps&&bS>tS*1.3){
        if(mv>=0.08)found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'终结楔形',dir:-1});
        else found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'引导楔形',dir:1});
      }else if(tS<-eps&&bS<0&&bS>tS){
        if(mv<=-0.08)found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'终结楔形',dir:1});
        else found.push({i:wg[4].i,i2:wg[0].i,mid:wg[2].i,n:'引导楔形',dir:-1});
      }
    }
  }
  return found;
}
function sigTag(dir){
  return dir>0?'<b style="color:var(--up)">买入</b>':dir<0?'<b style="color:var(--down)">卖出</b>':'<b style="color:var(--dim)">中性</b>';
}
function el(tag,attrs,parent){var e=document.createElementNS(SVGNS,tag);for(var k in attrs)e.setAttribute(k,attrs[k]);parent.appendChild(e);return e;}
function polyline(g,pts,col,w,dash){
  var p=pts.filter(function(q){return q;}).map(function(q){return q[0].toFixed(1)+','+q[1].toFixed(1);}).join(' ');
  el('polyline',{points:p,fill:'none',stroke:col,'stroke-width':w||1.5,'stroke-dasharray':dash||''},g);
}
function hlabel(g,tx,ty,txt,col,size){
  var t=el('text',{x:tx,y:ty,fill:col,'font-size':size||12,'font-weight':600},g);
  t.textContent=txt;
}
function drawCandles(g,d,x,yf,cw){
  d.forEach(function(k,i){
    var up=k.c>=k.o, col=up?'#CA3F64':'#25A750';   /* 红涨绿跌（色系 v5 低饱和，欧易暗色 canvas 实测） */
    /* 晕光已去除（色系 v5 平涂）+ 刻意超越包：仅最新一根蜡烛微发光（"只有最重要亮"原则，drop-shadow 3px .35） */
    var last=(i===d.length-1), glow=last?('drop-shadow(0 0 3px '+(up?'rgba(202,63,100,.35)':'rgba(37,167,80,.35)')+')'):null;
    el('line',{x1:x(i)+cw/2,x2:x(i)+cw/2,y1:yf(k.h),y2:yf(k.l),stroke:col,'stroke-width':1,filter:glow||''},g);
    el('rect',{x:x(i),y:yf(Math.max(k.o,k.c)),width:cw,height:Math.max(1.5,Math.abs(yf(k.o)-yf(k.c))),fill:col,filter:glow||''},g);
  });
}
function grid(g,W,L,R,H,T,B,n){
  /* v3 OKX 式：#171717 1px 实线横竖双线挂刻度；n 可省略（缺省=纯横线 5 条，旧签名兼容） */
  var vSteps=(n&&n>120)?7:((n&&n>60)?6:5);   /* 水平线数≈价格档数 */
  for(var vi=0;vi<=vSteps;vi++){
    var vy=T+vi*(H-T-B)/vSteps;
    el('line',{x1:L,x2:W-R,y1:vy,y2:vy,stroke:'#171717','stroke-width':1},g);
  }
  if(!n)return;   /* 未传 n=旧调用方，纯横线兼容 */
  var hSteps=Math.ceil(n/7);   /* 竖线≈时间刻度密度 */
  for(var hi=0;hi<=hSteps;hi++){
    var hx=L+hi*(W-L-R)/hSteps;
    el('line',{x1:hx,x2:hx,y1:T,y2:H-B,stroke:'#171717','stroke-width':1},g);
  }
}

/* ---- 十字光标联动：任一图 hover → 全部图同位置垂直虚线 + 各图显示当日数值 ---- */
var CHARTS={};
function fmtD(dt){return dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0');}
function barLabel(i){
  var back=N_BARS-1-i;
  if(curPer===8){ var dt=new Date(2026,7-back,1); return dt.getFullYear()+'-'+String(dt.getMonth()+1).padStart(2,'0'); }
  if(curPer===7){ var dt2=new Date(2026,7,20); dt2.setDate(dt2.getDate()-7*back); return fmtD(dt2); }
  if(curPer===6){ var dt3=new Date(2026,7,20); for(var k=0;k<back;k++){ dt3.setDate(dt3.getDate()-1); while(dt3.getDay()===0||dt3.getDay()===6) dt3.setDate(dt3.getDate()-1); } return fmtD(dt3); }
  var mins=[1,5,15,30,60,120][curPer], bpd=240/mins;
  var bd=Math.floor(back/bpd), rem=back%bpd;
  var dt=new Date(2026,7,20);
  for(var k=0;k<bd;k++){ dt.setDate(dt.getDate()-1); while(dt.getDay()===0||dt.getDay()===6) dt.setDate(dt.getDate()-1); }
  var t=15*60-rem*mins;
  if(t<690) t-=90;              /* 跨午休 11:30-13:00 跳过 */
  if(t<570) t=570;              /*  clamp 到 09:30 开盘 */
  var hh=Math.floor(t/60), mm=t%60;
  return fmtD(dt)+' '+String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0');
}
function mkReadout(chartBox){ var rd=chartBox.querySelector('.readout'); if(!rd){ rd=document.createElement('div'); rd.className='readout'; chartBox.appendChild(rd); } return rd; }
/* v4 canvas 十字光标联动：主层 canvas 绑定 mousemove，顶层 canvas 画十字线，DOM 覆盖层读数卡 */
function bindHoverCanvas(mc,cc,ov,cfg){
  var cctx=cc.getContext('2d'),dpr=window.devicePixelRatio||1;
  cctx.scale(dpr,dpr);
  mc.addEventListener('mousemove',function(e){
    var rect=mc.getBoundingClientRect();
    var sx=(e.clientX-rect.left)/rect.width*cfg.W;
    var i=Math.floor((sx-cfg.L)/((cfg.W-cfg.L-cfg.R)/cfg.n));
    if(i<0)i=0; if(i>=cfg.n)i=cfg.n-1;
    /* 顶层 canvas 清屏重绘十字线（60fps 不碰主层） */
    cctx.clearRect(0,0,cfg.W,cfg.H);
    var cx=cfg.x(i)+cfg.cw/2;
    cctx.strokeStyle='#EDEFF2'; cctx.lineWidth=0.8; cctx.setLineDash([4,3]); cctx.globalAlpha=0.75;
    cctx.beginPath(); cctx.moveTo(cx,cfg.T); cctx.lineTo(cx,cfg.H-cfg.B); cctx.stroke(); cctx.setLineDash([]); cctx.globalAlpha=1;
    /* DOM 覆盖层读数卡 */
    var rd=ov.querySelector('.readout'); if(!rd){ rd=document.createElement('div'); rd.className='readout'; ov.appendChild(rd); }
    rd.style.display='block';
    rd.innerHTML=cfg.readout(i);
    /* 筹码峰随光标重算 */
    if(mc.__sqChipRender){ var gi=cfg.w.lo+i; if(cfg.d[gi]) mc.__sqChipRender(gi,cfg.d[gi].c); }
  });
  mc.addEventListener('mouseleave',function(){
    cctx.clearRect(0,0,cfg.W,cfg.H);
    var rd=ov.querySelector('.readout'); if(rd) rd.style.display='none';
    if(mc.__sqChipBase) mc.__sqChipBase();
  });
}
function bindHover(svg,cfg){
  cfg.g0=svg; CHARTS[svg.id]=cfg;
  if(!svg._hb){
    svg._hb=true;
    svg.addEventListener('mousemove',function(e){
      var c=CHARTS[svg.id]; if(!c) return;
      var rect=svg.getBoundingClientRect();
      var sx=(e.clientX-rect.left)/rect.width*c.W;
      var i=Math.floor((sx-c.L)/((c.W-c.L-c.R)/c.n));
      if(i<0)i=0; if(i>=c.n)i=c.n-1;
      applyHover(i);
    });
    svg.addEventListener('mouseleave',function(){ applyHover(-1); });
  }
}
function applyHover(i){
  for(var id in CHARTS){
    var c=CHARTS[id];
    if(c.g0.getClientRects().length===0) continue;   /* 隐藏页面的图跳过（SVG 无 offsetParent，须用 getClientRects） */
    var ii=Math.min(i,c.n-1);             /* 不同长度序列各自钳位 */
    if(ii>=0){
      var cx=c.x(ii)+c.cw/2;
      if(!c.cross){ c.cross=el('line',{stroke:'#EDEFF2','stroke-width':0.8,'stroke-dasharray':'4 3',opacity:0.75},c.g); }
      c.cross.setAttribute('x1',cx); c.cross.setAttribute('x2',cx);
      c.cross.setAttribute('y1',c.T); c.cross.setAttribute('y2',c.H-c.B);
      c.cross.style.display='';
      c.rd.style.display='block';
      c.rd.innerHTML=c.readout(ii);   /* R23b：多行卡片读数（对齐旧版 Plotly hover），readout 返回 HTML */
      /* v3.2：个股行情主图 hover 联动筹码峰——按光标日重算（截止光标日+光标价分获利/套牢） */
      if(id==='sq-main'&&c.g0.__sqChipRender){ var dg=sqData(),gi=w2gi(c,ii); if(dg[gi]) c.g0.__sqChipRender(gi,dg[gi].c); }
    }else{
      if(c.cross) c.cross.style.display='none';
      c.rd.style.display='none';
      if(id==='sq-main'&&c.g0.__sqChipBase) c.g0.__sqChipBase();   /* 移出回窗口末现价 */
    }
  }
}
/* v3.2：sq-main hover 索引→数据索引（窗口偏移） */
function w2gi(c,ii){ var w=sqWinGet(); return w.lo+ii; }

/* ---- 汇总主图：K线+成交量+叠加层+买卖信号 ---- */
function renderMain(d){
  var svg=document.getElementById('svg-main'); svg.innerHTML='';
  var W=1100,H=520,L=46,R=64,T=16,VT=H-96,VB=H-10;  /* K线区 T..VT-8，量区 VT..VB；v3：L=46 给左%轴腾位 */
  var rg=rangeOf(d), lo=rg[0], hi=rg[1];
  var cw=(W-L-R)/d.length*0.78;   /* v3 蜡烛几何：体：隙≈7:2（OKX 实测 78%） */
  var x=function(i){return L+(i+0.5)*(W-L-R)/d.length-cw/2;};
  var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(VT-8-T);};
  var g=el('g',{},svg);
  grid(g,W,L,R,VT-8,T,0,d.length);
  /* 双轴（v3 补齐）：右=价格 5 档 #C6C6C6 12px，左=涨跌幅%（窗口首收为 0 红正绿负） */
  var base0=d[0].c;
  for(var ax=0;ax<=4;ax++){
    var av=lo+(hi-lo)*ax/4,ay=yf(av);
    hlabel(g,W-R+6,ay+3,av.toFixed(2),'#C6C6C6',12);
    var apc=(av-base0)/base0*100,apl=el('text',{x:L-6,y:ay+3,fill:apc>=0?'#CA3F64':'#25A750','font-size':10,'text-anchor':'end'},g); apl.textContent=(apc>=0?'+':'')+apc.toFixed(1)+'%';
  }
  /* 成交量（下挂，红涨绿跌随蜡烛） */
  var vmax=0; d.forEach(function(k){vmax=Math.max(vmax,k.v);});
  var vma=[]; for(var i=0;i<d.length;i++){var s=0,n=0;for(var j=Math.max(0,i-4);j<=i;j++){s+=d[j].v;n++;}vma.push(s/n);}
  d.forEach(function(k,i){
    var vh=(k.v/vmax)*(VB-VT-4);
    el('rect',{x:x(i),y:VB-vh,width:cw,height:vh,fill:k.c>=k.o?'#CA3F64':'#25A750',opacity:0.5},g);
  });
  /* 量能标注：天量（>1.8×均量且局部最大）/ 地量（<0.5×均量且局部最小） */
  var vmarks={};
  if(OVL.volmark){
    var marked=0;
    for(var m=2;m<d.length-2;m++){
      if(d[m].v>1.8*vma[m]&&d[m].v>=d[m-1].v&&d[m].v>=d[m+1].v){
        hlabel(g,x(m)-8,VT+12,'天量','#FFD54F',10); vmarks[m]='天量'; marked++;
      }else if(d[m].v<0.5*vma[m]&&d[m].v<=d[m-1].v&&d[m].v<=d[m+1].v){
        hlabel(g,x(m)-8,VB-2,'地量','#25A750',10); vmarks[m]='地量'; marked++;
      }
    }
    if(!marked) hlabel(g,L+8,VT+16,'当前时段无天量/地量（负反馈也是结果）','#59626D',11);
  }
  drawCandles(g,d,x,yf,cw);
  /* BOLL */
  var mid=[];
  if(OVL.boll){
    var up=[],low=[];
    for(var b=0;b<d.length;b++){
      var mm=ma(d,20,b); if(!mm) continue;
      var sd=0; for(var j=b-19;j<=b;j++) sd+=(d[j].c-mm)*(d[j].c-mm);
      sd=Math.sqrt(sd/20);
      up.push([x(b)+cw/2,yf(mm+2*sd)]); mid.push([x(b)+cw/2,yf(mm)]); low.push([x(b)+cw/2,yf(mm-2*sd)]);
    }
    polyline(g,up,'#FFD54F',1.2); polyline(g,mid,'#AB47BC',1.2); polyline(g,low,'#AB47BC',1.2);
  }
  /* MA20 / 主力成本线 */
  if(OVL.ma||OVL.cost){
    var m20=[],m40=[];
    for(var a=0;a<d.length;a++){
      var v20=ma(d,20,a),v40=ma(d,40,a);
      m20.push(v20?[x(a)+cw/2,yf(v20)]:null);
      m40.push(v40?[x(a)+cw/2,yf(v40)]:null);
    }
    if(OVL.cost) polyline(g,m40,'#F0B90B',1.5,'6 4');
    if(OVL.ma) polyline(g,m20,'#EC407A',1.3);
  }
  /* 趋势线（显著低点/高点连线延长） */
  if(OVL.trend){
    var lows=[],highs=[];
    for(var t=2;t<d.length-2;t++){
      if(d[t].l<d[t-1].l&&d[t].l<d[t+1].l&&d[t].l<d[t-2].l&&d[t].l<d[t+2].l) lows.push(t);
      if(d[t].h>d[t-1].h&&d[t].h>d[t+1].h&&d[t].h>d[t-2].h&&d[t].h>d[t+2].h) highs.push(t);
    }
    if(lows.length>=2){
      var p1=lows[0],p2=lows[lows.length-1],sl=(yf(d[p2].l)-yf(d[p1].l))/(p2-p1);
      polyline(g,[[x(p1)+cw/2,yf(d[p1].l)],[x(d.length-1)+cw/2,yf(d[p1].l)+sl*(d.length-1-p1)]],'#CA3F64',1.6);
      hlabel(g,x(d.length-1)-150,yf(d[p1].l)+sl*(d.length-1-p1)-8,'上升趋势线','#CA3F64',11);
    }
    if(highs.length>=2){
      var q1=highs[0],q2=highs[1],sl2=(yf(d[q2].h)-yf(d[q1].h))/(q2-q1);
      polyline(g,[[x(q1)+cw/2,yf(d[q1].h)],[x(d.length-1)+cw/2,yf(d[q1].h)+sl2*(d.length-1-q1)]],'#25A750',1.6);
      hlabel(g,x(d.length-1)-150,yf(d[q1].h)+sl2*(d.length-1-q1)-8,'下降压力线','#25A750',11);
    }
  }
  /* 水平压力/支撑 */
  if(OVL.sr){
    var recent=d.slice(-30),rHi=-1e9,rLo=1e9;
    recent.forEach(function(k){rHi=Math.max(rHi,k.h);rLo=Math.min(rLo,k.l);});
    el('line',{x1:L,x2:W-R,y1:yf(rHi),y2:yf(rHi),stroke:'#CA3F64','stroke-width':1.2,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:yf(rLo),y2:yf(rLo),stroke:'#25A750','stroke-width':1.2,'stroke-dasharray':'4 3'},g);
    hlabel(g,W-R+6,yf(rHi)+4,'压力 '+rHi.toFixed(0),'#CA3F64',11);
    hlabel(g,W-R+6,yf(rLo)+4,'支撑 '+rLo.toFixed(0),'#25A750',11);
    hlabel(g,W-R+6,yf(d[d.length-1].c)+4,'现价 '+IDX_META[curIdx].price,'#EDEFF2',11);
  }
  /* 分型全部同时标注 + 最近顶/底出买卖信号（带置信度） */
  var fr=fractals(d);
  if(OVL.frac){
    fr.tops.forEach(function(i){
      el('path',{d:'M'+(x(i)+cw/2)+','+(yf(d[i].h)-14)+' l7,11 l-14,0 Z',fill:'#25A750',stroke:'#EDEFF2','stroke-width':0.7},g);
    });
    fr.bots.forEach(function(i){
      el('path',{d:'M'+(x(i)+cw/2)+','+(yf(d[i].l)+14)+' l7,-11 l-14,0 Z',fill:'#CA3F64',stroke:'#EDEFF2','stroke-width':0.7},g);
    });
  }
  var conf=confluence(d);
  if(fr.bots.length){
    var lb=fr.bots[fr.bots.length-1];
    hlabel(g,x(lb)-26,yf(d[lb].l)+38,'▲买点 '+conf.buyConf+'%','#CA3F64',12);
  }
  if(fr.tops.length){
    var lt=fr.tops[fr.tops.length-1];
    hlabel(g,x(lt)-26,yf(d[lt].h)-28,'▼卖点 '+conf.sellConf+'%','#25A750',12);
  }
  /* 十字光标注册（主图：OHLC+量+量能标注） */
  var rdM=mkReadout(svg.parentNode);
  bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:6,n:d.length,x:x,cw:cw,g:g,rd:rdM,readout:function(i){
    var k=d[i],s=barLabel(i)+'  开 '+k.o.toFixed(1)+' 高 '+k.h.toFixed(1)+' 低 '+k.l.toFixed(1)+' 收 '+k.c.toFixed(1)+' 量 '+k.v.toFixed(0);
    if(vmarks[i]) s+='·'+vmarks[i];
    return s;
  }});
}

/* ---- 多指标共振综合观点（演示算法：从数据真实计算特征） ---- */
function confluence(d){
  var n=d.length-1;
  var m20=ma(d,20,n),m20p=ma(d,20,n-5),m40=ma(d,40,n);
  var fr=fractals(d);
  var macd=macdCalc(d),dif=macd[0],dea=macd[1];
  var lastBot=fr.bots.length?fr.bots[fr.bots.length-1]:-1;
  var lastTop=fr.tops.length?fr.tops[fr.tops.length-1]:-1;
  var v5=0,v15=0; for(var i=n-4;i<=n;i++)v5+=d[i].v; for(var j=n-19;j<=n-5;j++)v15+=d[j].v;
  var feats=[
    {n:'MA20 上方',ok:d[n].c>m20},
    {n:'MA20 上行',ok:m20>m20p},
    {n:'BOLL 中轨上方',ok:d[n].c>m20},       /* 中轨≈MA20，演示同义 */
    {n:'底分型更近',ok:lastBot>lastTop},
    {n:'MACD 金叉',ok:dif[n]>dea[n]},
    {n:'量能放大',ok:v5/5>v15/15},
    {n:'成本线上方',ok:m40?d[n].c>m40:false}
  ];
  var score=feats.filter(function(f){return f.ok;}).length;
  var buyConf=Math.min(95,42+score*8), sellConf=Math.min(95,42+(7-score)*8);
  var signal=score>=5?'买入':(score<=2?'卖出':'中性观望');
  var sigCol=score>=5?'#CA3F64':(score<=2?'#25A750':'#A0A6AD');
  var card=document.getElementById('signal-card');
  card.innerHTML='<div style="display:flex;gap:18px;align-items:baseline;flex-wrap:wrap">'
    +'<span style="font-size:15px;font-weight:700">'+(IDX_META[curIdx].type==='index'?'系统综合观点（多指标共振）· 真源=index_resonance_scorer（testing，I-2）':'个股技术观点（多指标共振）')+'</span>'
    +'<span style="font-size:20px;font-weight:700;color:'+sigCol+'">'+signal+'</span>'
    +'<span style="font-size:13px">置信度 <b style="color:'+sigCol+'">'+(score>=5?buyConf:score<=2?sellConf:50)+'%</b></span>'
    +'<span style="font-size:13px;color:var(--dim)">共振 <b>'+score+'/7</b> 指标</span></div>'
    +'<div style="font-size:12px;color:var(--dim);margin-top:8px">'
    +feats.map(function(f){return '<span style="color:'+(f.ok?'#CA3F64':'#2A2F36')+'">'+(f.ok?'✓':'✗')+' '+f.n+'</span>';}).join(' · ')
    +'</div>'
    +'<div class="note">置信度=多指标共振评分（演示算法，从上方数据真实计算 7 项特征）；指数级共振综合评分属新增能力 → §5 缺口③。「分歧点」即买卖信号的另一种叫法——本系统用「买/卖点+置信度」表达，覆盖上涨/下跌两种分歧</div>';
  return{buyConf:buyConf,sellConf:sellConf};
}

/* ---- 指标窗格（搜索选择器 +/-/增减 + 信息卡） ---- */
function renderPanes(d){
  var box=document.getElementById('panes'); box.innerHTML='';
  Object.keys(CHARTS).forEach(function(k){ if(k.indexOf('pane-svg-')===0) delete CHARTS[k]; });
  PANES.forEach(function(type,pi){
    var div=document.createElement('div'); div.className='chart-box';
    var list='';
    IND_CAT.forEach(function(gr){
      list+='<div class="pick-group">'+gr.g+'</div>';
      gr.items.forEach(function(it){
        list+='<div class="pick-item" onclick="pickChoose('+pi+',\''+it.k+'\')">'+it.n+'<span class="st'+(it.ok?' ok':'')+'">'+(it.ok?'已接入':'待接入')+'</span></div>';
      });
    });
    div.innerHTML='<div class="chart-title" style="display:flex;justify-content:space-between;align-items:center">'
      +'<span class="pick"><button class="psel pick-btn" onclick="pickToggle(this)">'+(IND_NAME[type]||type)+' ▾</button>'
      +'<span class="pick-body"><input placeholder="搜索指标/形态…（中文/英文/缩写）" oninput="pickSearch(this)"><span class="pick-list">'+list+'</span></span></span>'
      +'<span class="btn pane-del" onclick="delPane('+pi+')">−</span></div>'
      +'<svg class="spark" id="pane-svg-'+pi+'" viewBox="0 0 1100 260" preserveAspectRatio="none" style="background:#000000;border-radius:4px"></svg>'
      +'<div class="lv" id="pane-vd-'+pi+'" style="justify-content:center"></div>'
      +'<div class="ind-info" id="pane-info-'+pi+'"></div>';
    box.appendChild(div);
    renderPaneContent(d,type,pi);
  });
}
function pickToggle(btn){ btn.parentNode.querySelector('.pick-body').classList.toggle('open'); }
function pickSearch(inp){
  var q=inp.value.toLowerCase(), body=inp.parentNode;
  body.querySelectorAll('.pick-group').forEach(function(g){g.style.display='none';});
  body.querySelectorAll('.pick-item').forEach(function(it){
    var show=!q||it.textContent.toLowerCase().indexOf(q)>=0;
    it.style.display=show?'':'none';
    if(show){ var gr=it.previousElementSibling; while(gr&&!gr.classList.contains('pick-group')) gr=gr.previousElementSibling; if(gr) gr.style.display=''; }
  });
}
function pickChoose(pi,k){ PANES[pi]=k; renderIdxAll(false); }
function addPane(){ if(PANES.length>=4) return; PANES.push('boll'); renderIdxAll(false); }
function delPane(i){ PANES.splice(i,1); renderIdxAll(false); }
function paneSel(i,val){ PANES[i]=val; renderIdxAll(false); }
function ovlTgl(k,v){ OVL[k]=v; renderIdxAll(false); }
function infoFill(pi,type,sigHtml){
  var info=document.getElementById('pane-info-'+pi);
  info.innerHTML='<span class="nm">'+(IND_NAME[type]||type)+'</span><span class="ds">'+(IND_INFO[type]||'简介见注册表（全量条目同版式接入）')+'</span>'
    +'<div class="sg">当前信号：'+sigHtml+'</div>';
}

function renderPaneContent(d,type,pi){
  var svg=document.getElementById('pane-svg-'+pi), vd=document.getElementById('pane-vd-'+pi);
  svg.innerHTML='';
  var W=1100,H=260,L=10,R=86,T=14,B=14;   /* R=86 与主图一致：十字光标跨图共线 */
  var cw=(W-L-R)/d.length*0.62;
  var x=function(i){return L+(i+0.5)*(W-L-R)/d.length-cw/2;};
  var g=el('g',{},svg);
  grid(g,W,L,R,H,T,B);
  var rd=mkReadout(svg.parentNode);
  var n=d.length, last=n-1;
  function linePane(arr,lo,hi,col,refs){
    var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
    (refs||[]).forEach(function(rv){el('line',{x1:L,x2:W-R,y1:yf(rv),y2:yf(rv),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);});
    polyline(g,arr.map(function(v,i){return[x(i)+cw/2,yf(v)];}),col,1.4);
    return yf;
  }
  function maxAbs(arr){var m=0;arr.forEach(function(v){m=Math.max(m,Math.abs(v));});return m||1;}

  if(type==='boll'){
    /* 叠加型指标：BOLL 直接画在 K 线上（Owner 裁定，同形态分型） */
    var upV=[],midV=[],lowV=[],lo=1e9,hi=-1e9;
    d.forEach(function(k){lo=Math.min(lo,k.l);hi=Math.max(hi,k.h);});
    for(var i=0;i<n;i++){
      var m=ma(d,20,i);
      if(!m){upV.push(null);midV.push(null);lowV.push(null);continue;}
      var sd=0; for(var j=i-19;j<=i;j++) sd+=(d[j].c-m)*(d[j].c-m);
      sd=Math.sqrt(sd/20);
      upV.push(m+2*sd);midV.push(m);lowV.push(m-2*sd);
      hi=Math.max(hi,m+2*sd);lo=Math.min(lo,m-2*sd);
    }
    var pad=(hi-lo)*0.08; lo-=pad; hi+=pad;
    var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
    drawCandles(g,d,x,yf,cw);
    function v2p(v,i2){return v?[x(i2)+cw/2,yf(v)]:null;}
    polyline(g,upV.map(v2p),'#FFD54F',1.2);
    polyline(g,midV.map(v2p),'#3D8BFF',1.4);
    polyline(g,lowV.map(v2p),'#AB47BC',1.2);
    var mL=midV[last],sdL=(upV[last]-mL)/2,bw=(4*sdL/mL*100).toFixed(1);
    vd.innerHTML='<span style="color:var(--yellow)">— 上轨</span><span style="color:var(--blue)">— 中轨</span><span style="color:var(--purple)">— 下轨</span><span class="dim">带宽 '+bw+'% · BOLL 直接叠加 K 线（叠加型指标与主图同坐标系）</span>';
    var bs=d[last].c>=upV[last]?-1:(d[last].c<=lowV[last]?1:0);
    var btxt=bs<0?'价格 '+d[last].c.toFixed(1)+' 触上轨 '+upV[last].toFixed(1)+'（超买警戒）':bs>0?'价格 '+d[last].c.toFixed(1)+' 触下轨 '+lowV[last].toFixed(1)+'（超卖关注）':'通道内运行（%B='+(((d[last].c-lowV[last])/(upV[last]-lowV[last]))*100).toFixed(0)+'%）';
    infoFill(pi,type,sigTag(bs)+' · '+btxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      var s=barLabel(i)+'  收 '+d[i].c.toFixed(1);
      if(midV[i]) s+='  上 '+upV[i].toFixed(1)+' 中 '+midV[i].toFixed(1)+' 下 '+lowV[i].toFixed(1);
      return s;
    }});
  }else if(type==='kdj'){
    var KDJ=kdjCalc(d),K=KDJ[0],D=KDJ[1],J=KDJ[2];
    var yk=function(v){return T+(1-(Math.max(-10,Math.min(110,v))+10)/120)*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:yk(80),y2:yk(80),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:yk(20),y2:yk(20),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,K.map(function(v,i){return[x(i)+cw/2,yk(v)];}),'#3D8BFF',1.2);
    polyline(g,D.map(function(v,i){return[x(i)+cw/2,yk(v)];}),'#CA3F64',1.2);
    polyline(g,J.map(function(v,i){return[x(i)+cw/2,yk(v)];}),'#F0B90B',1.2);
    var jv=J[last];
    var ks=jv<20?1:(jv>80?-1:0);
    vd.innerHTML='<span style="color:var(--blue)">— K</span><span style="color:var(--up)">— D</span><span style="color:var(--orange)">— J</span><span class="dim">J='+jv.toFixed(0)+'（80 上超买 / 20 下超卖）</span>';
    infoFill(pi,type,sigTag(ks)+' · J='+jv.toFixed(1)+(ks>0?' 超卖区（拐头关注买入）':ks<0?' 超买区（拐头警惕卖出）':' 中性区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  K '+K[i].toFixed(1)+'  D '+D[i].toFixed(1)+'  J '+J[i].toFixed(1);
    }});
  }else if(type==='macd'){
    var MC=macdCalc(d),dif=MC[0],dea=MC[1],hist=MC[2];
    var hmax=maxAbs(hist), dm=maxAbs(dif.concat(dea));
    var ym=function(v){return T+(1-(v+dm)/(2*dm))*(H-T-B);};
    var yh=function(v){return T+(1-(v+hmax)/(2*hmax))*(H-T-B);};
    var zeroY=yh(0);
    hist.forEach(function(v,i){
      el('rect',{x:x(i),y:Math.min(yh(v),zeroY),width:cw,height:Math.max(1.5,Math.abs(yh(v)-zeroY)),fill:v>=0?'#CA3F64':'#25A750'},g);
    });
    polyline(g,dif.map(function(v,i){return[x(i)+cw/2,ym(v)];}),'#F0B90B',1.2);
    polyline(g,dea.map(function(v,i){return[x(i)+cw/2,ym(v)];}),'#CA3F64',1.2);
    var crossUp=dif[last]>dea[last]&&dif[last-1]<=dea[last-1];
    var crossDn=dif[last]<dea[last]&&dif[last-1]>=dea[last-1];
    var ms=crossUp?1:(crossDn?-1:0);
    var mtxt=crossUp?'金叉形成（DIF 上穿 DEA）':crossDn?'死叉形成（DIF 下穿 DEA）':(dif[last]>dea[last]?'多头延续':'空头延续');
    vd.innerHTML='<span style="color:var(--orange)">— DIF</span><span style="color:var(--up)">— DEA</span><span style="color:var(--up)">■ 红柱</span><span style="color:var(--down)">■ 绿柱</span><span class="dim">'+mtxt+'</span>';
    infoFill(pi,type,sigTag(ms)+' · '+mtxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  DIF '+dif[i].toFixed(2)+'  DEA '+dea[i].toFixed(2)+'  MACD '+hist[i].toFixed(2);
    }});
  }else if(type==='ma'){
    var rg=rangeOf(d),lo3=rg[0],hi3=rg[1];
    var yf3=function(v){return T+(1-(v-lo3)/(hi3-lo3))*(H-T-B);};
    drawCandles(g,d,x,yf3,cw);
    var m20=[];
    for(var a=0;a<n;a++){var v20=ma(d,20,a);m20.push(v20?[x(a)+cw/2,yf3(v20)]:null);}
    polyline(g,m20,'#3D8BFF',1.6);
    var maL=ma(d,20,last), mas=d[last].c>maL?1:-1;
    vd.innerHTML='<span style="color:var(--blue)">— MA20</span><span class="dim">价格 '+(mas>0?'上方':'下方')+'运行，偏离 '+(((d[last].c/maL)-1)*100).toFixed(1)+'%</span>';
    infoFill(pi,type,sigTag(mas)+' · 收盘 '+d[last].c.toFixed(1)+' 在 MA20（'+maL.toFixed(1)+'）'+(mas>0?'上方（趋势偏多）':'下方（趋势偏空）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      var v=ma(d,20,i); return barLabel(i)+'  收 '+d[i].c.toFixed(1)+(v?'  MA20 '+v.toFixed(1):'');
    }});
  }else if(type==='rsi'){
    var RS=rsiCalc(d,14);
    linePane(RS,0,100,'#3D8BFF',[70,30]);
    var rs=RS[last],rss=rs<30?1:(rs>70?-1:0);
    vd.innerHTML='<span style="color:var(--blue)">— RSI(14)</span><span class="dim">70 上超买 / 30 下超卖</span>';
    infoFill(pi,type,sigTag(rss)+' · RSI='+rs.toFixed(1)+(rss>0?' 超卖区':rss<0?' 超买区':' 中性区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){return barLabel(i)+'  RSI '+RS[i].toFixed(1);}});
  }else if(type==='wr'){
    var WR=wrCalc(d,14);
    linePane(WR,-100,0,'#AB47BC',[-20,-80]);
    var wv=WR[last],ws=wv<-80?1:(wv>-20?-1:0);
    vd.innerHTML='<span style="color:var(--purple)">— WR(14)</span><span class="dim">-80 下超卖 / -20 上超买</span>';
    infoFill(pi,type,sigTag(ws)+' · WR='+wv.toFixed(1)+(ws>0?' 超卖区':ws<0?' 超买区':' 中性区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){return barLabel(i)+'  WR '+WR[i].toFixed(1);}});
  }else if(type==='roc'||type==='mtm'){
    var AR=type==='roc'?rocCalc(d,12):mtmCalc(d,12);
    var mx=maxAbs(AR);
    linePane(AR,-mx,mx,'#F0B90B',[0]);
    var rv=AR[last],rs2=rv>0?1:-1;
    var unit=type==='roc'?'%':'';
    vd.innerHTML='<span style="color:var(--orange)">— '+(type==='roc'?'ROC(12)':'MTM(12)')+'</span><span class="dim">零轴上强 / 下弱</span>';
    infoFill(pi,type,sigTag(rs2)+' · 当前 '+rv.toFixed(2)+unit+'（'+(rs2>0?'零轴上方，动能偏多':'零轴下方，动能偏空')+'）');
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){return barLabel(i)+'  '+(type==='roc'?'ROC ':'MTM ')+AR[i].toFixed(2)+unit;}});
  }else if(type==='obv'){
    var OB=obvCalc(d);
    var omin=Math.min.apply(null,OB),omax=Math.max.apply(null,OB);
    linePane(OB,omin,omax,'#25A750',null);
    var oUp=OB[last]>OB[last-5], pUp=d[last].c>d[last-5].c;
    var os=oUp&&pUp?1:(pUp&&!oUp?-1:0);
    var otxt=oUp&&pUp?'量价齐升（OBV 与价格同向上行）':(pUp&&!oUp?'价升量缩，顶背离警告':(!pUp&&oUp?'价跌量增，承接显现':'量价同弱'));
    vd.innerHTML='<span style="color:var(--down)">— OBV</span><span class="dim">量价同向为健康、背离为警告</span>';
    infoFill(pi,type,sigTag(os)+' · '+otxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){return barLabel(i)+'  OBV '+OB[i].toFixed(0);}});
  }else if(type==='atr'){
    var AT=atrCalc(d,14);
    var amax=Math.max.apply(null,AT);
    linePane(AT,0,amax*1.1,'#FFD54F',null);
    var aUp=AT[last]>AT[last-5];
    vd.innerHTML='<span style="color:var(--yellow)">— ATR(14)</span><span class="dim">波动率度量</span>';
    infoFill(pi,type,'<b style="color:var(--faint)">无方向信号</b> · ATR='+AT[last].toFixed(2)+'，波动率较 5 日前'+(aUp?'上升':'下降')+'——波动指标不产生买卖点（负反馈也是结果）');
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){return barLabel(i)+'  ATR '+AT[i].toFixed(2);}});
  }else if(type==='vol'){
    var vmax=0; d.forEach(function(k){vmax=Math.max(vmax,k.v);});
    var vma=[]; for(var i2=0;i2<n;i2++){var s=0,nn=0;for(var j2=Math.max(0,i2-4);j2<=i2;j2++){s+=d[j2].v;nn++;}vma.push(s/nn);}
    var vmarkArr=[];
    d.forEach(function(k,i){
      var vh=(k.v/vmax)*(H-T-B);
      el('rect',{x:x(i),y:H-B-vh,width:cw,height:vh,fill:k.c>=k.o?'#CA3F64':'#25A750',opacity:0.75},g);
    });
    var marks=0,lastMark=-1,lastKind='';
    for(var m=2;m<n-2;m++){
      if(d[m].v>1.8*vma[m]&&d[m].v>=d[m-1].v&&d[m].v>=d[m+1].v){hlabel(g,x(m)-10,T+14,'天量','#FFD54F',11);vmarkArr[m]='天量';marks++;lastMark=m;lastKind='天量';}
      else if(d[m].v<0.5*vma[m]&&d[m].v<=d[m-1].v&&d[m].v<=d[m+1].v){hlabel(g,x(m)-10,H-B-((d[m].v/vmax)*(H-T-B))-6,'地量','#25A750',11);vmarkArr[m]='地量';marks++;lastMark=m;lastKind='地量';}
    }
    vd.innerHTML=marks
      ?'<span style="color:var(--yellow)">天量/地量 '+marks+' 处标注</span><span class="dim">天量天价（警惕见顶）/ 地量地价（关注见底）</span>'
      :'<span class="dim">当前时段未识别出天量/地量（负反馈也是结果——系统明说"没有"）</span>';
    var vs=lastKind==='天量'?-1:(lastKind==='地量'?1:0);
    var vtxt=lastKind?('最近 '+lastKind+'（'+(n-1-lastMark)+' 根前）——'+(lastKind==='天量'?'天量天价，警惕见顶':'地量地价，关注见底')):'当前时段无天量/地量';
    infoFill(pi,type,sigTag(vs)+' · '+vtxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      var s=barLabel(i)+'  量 '+d[i].v.toFixed(0)+'（5均 '+vma[i].toFixed(0)+'）';
      if(vmarkArr[i]) s+='  '+vmarkArr[i];
      return s;
    }});
  }else if(type==='frac'){
    var rg2=rangeOf(d),lo2=rg2[0],hi2=rg2[1];
    var yf2=function(v){return T+(1-(v-lo2)/(hi2-lo2))*(H-T-B);};
    drawCandles(g,d,x,yf2,cw);
    var fr=fractals(d);
    var fmap={};
    fr.tops.forEach(function(i){fmap[i]='顶分型';el('path',{d:'M'+(x(i)+cw/2)+','+(yf2(d[i].h)-12)+' l7,11 l-14,0 Z',fill:'#25A750',stroke:'#EDEFF2','stroke-width':0.7},g);});
    fr.bots.forEach(function(i){fmap[i]='底分型';el('path',{d:'M'+(x(i)+cw/2)+','+(yf2(d[i].l)+12)+' l7,-11 l-14,0 Z',fill:'#CA3F64',stroke:'#EDEFF2','stroke-width':0.7},g);});
    vd.innerHTML=(fr.tops.length+fr.bots.length)
      ?'<span style="color:var(--down)">▼ 顶分型 ×'+fr.tops.length+'</span><span style="color:var(--up)">▲ 底分型 ×'+fr.bots.length+'</span><span class="dim">全部出现位置同时标注</span>'
      :'<span class="dim">当前时段未识别出顶/底分型（负反馈也是结果——系统明说"没有"）</span>';
    var lb2=fr.bots.length?fr.bots[fr.bots.length-1]:-1, lt2=fr.tops.length?fr.tops[fr.tops.length-1]:-1;
    var fs2=lb2>lt2?1:-1;
    infoFill(pi,type,sigTag(fs2)+' · 最近'+(fs2>0?'底分型（'+(n-1-lb2)+' 根前，潜在买点）':'顶分型（'+(n-1-lt2)+' 根前，潜在卖点）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+'  形态：'+(fmap[i]||'无');
    }});
  }else if(type==='candle'){
    var rg3=rangeOf(d),lo3b=rg3[0],hi3b=rg3[1];
    var yf3b=function(v){return T+(1-(v-lo3b)/(hi3b-lo3b))*(H-T-B);};
    drawCandles(g,d,x,yf3b,cw);
    var pats=candlePats20(d), pmap={}, pstack={};
    pats.forEach(function(p){
      pmap[p.i]=pmap[p.i]?pmap[p.i]+'·'+p.n:p.n;         /* 同根多形态全部保留 */
      var col=p.dir>0?'#CA3F64':(p.dir<0?'#25A750':'#A0A6AD');
      var lv=pstack[p.i]||0; pstack[p.i]=lv+1;           /* 同位标注竖向错开防重叠 */
      hlabel(g,x(p.i)-14,yf3b(d[p.i].l)+24+lv*11,p.n,col,10);
    });
    var lastP=pats.length?pats[pats.length-1]:null;
    vd.innerHTML=pats.length
      ?'<span class="dim">识别 '+pats.length+' 处：'+pats.slice(-4).map(function(p){return p.n;}).join(' / ')+' 等</span>'
      :'<span class="dim">当前时段未识别出 K 线形态（负反馈也是结果——系统明说"没有"）</span>';
    var cs=lastP?lastP.dir:0;
    infoFill(pi,type,(lastP?sigTag(cs)+' · 最近形态「'+lastP.n+'」（'+(n-1-lastP.i)+' 根前）':'<b style="color:var(--faint)">无</b> · 当前时段未识别（负反馈）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+'  形态：'+(pmap[i]||'无');
    }});
  }else if(type==='rsidiv'){
    /* RSI 背离：RSI 线 + 背离段连线标注（顶背离=绿卖出 / 底背离=红买入），全部位置同时标注 */
    var RD=rsiCalc(d,14);
    var yfR=linePane(RD,0,100,'#3D8BFF',[70,30]);
    var divs=rsiDivergence(d,RD), dvmap={}, dvstack={};
    divs.forEach(function(dv){
      dvmap[dv.i2]=dvmap[dv.i2]?dvmap[dv.i2]+'·'+dv.n:dv.n;
      var col=dv.dir>0?'#CA3F64':'#25A750';
      el('line',{x1:x(dv.i1)+cw/2,y1:yfR(RD[dv.i1]),x2:x(dv.i2)+cw/2,y2:yfR(RD[dv.i2]),stroke:col,'stroke-width':1.2,'stroke-dasharray':'5 3'},g);
      el('circle',{cx:x(dv.i1)+cw/2,cy:yfR(RD[dv.i1]),r:2.4,fill:col},g);
      el('circle',{cx:x(dv.i2)+cw/2,cy:yfR(RD[dv.i2]),r:2.4,fill:col},g);
      var dlv=dvstack[dv.i2]||0; dvstack[dv.i2]=dlv+1;
      hlabel(g,x(dv.i2)-14,yfR(RD[dv.i2])+(dv.dir>0?18+dlv*11:-8-dlv*11),dv.n,col,10);
    });
    var lastDv=divs.length?divs[divs.length-1]:null;
    vd.innerHTML='<span style="color:var(--blue)">— RSI(14)</span>'
      +(divs.length
        ?'<span style="color:var(--up)">底背离 ×'+divs.filter(function(q){return q.dir>0;}).length+'</span><span style="color:var(--down)">顶背离 ×'+divs.filter(function(q){return q.dir<0;}).length+'</span><span class="dim">全部背离位置同时标注</span>'
        :'<span class="dim">当前时段未识别出背离（负反馈也是结果——系统明说"没有"）</span>');
    infoFill(pi,type,lastDv
      ?sigTag(lastDv.dir)+' · 最近'+lastDv.n+'（'+(n-1-lastDv.i2)+' 根前，'+barLabel(lastDv.i2)+'）：价格'+(lastDv.dir>0?'新低而 RSI 未新低，空方动能衰竭':'新高而 RSI 未新高，多方动能衰竭')
      :'<b style="color:var(--dim)">中性</b> · 当前时段无背离（RSI='+RD[last].toFixed(1)+'，负反馈）');   /* v6：中性=灰 */
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  RSI '+RD[i].toFixed(1)+'  背离：'+(dvmap[i]||'无');
    }});
  }else if(type==='pat'){
    /* 经典形态库：K线 20 高频 + 扩展 15 + 持续/三根族 16（第三批 CWIRE）+ CANDLE 余项 49（第四批）+ 图表形态 4+10+30+20 + 趋势 13+支撑压力 10+斐波 17+结构 27（第四批）= 231 规则合集，全部位置同时标注 */
    var rgP=rangeOf(d),loP=rgP[0],hiP=rgP[1];
    var yfP=function(v){return T+(1-(v-loP)/(hiP-loP))*(H-T-B);};
    drawCandles(g,d,x,yfP,cw);
    var pats2=candlePats20(d).concat(patExt(d)).concat(patExt2(d)).concat(patExt3(d))
      , chart2=chartPats(d).concat(chartPats2(d)).concat(chartPats3(d)).concat(chartPats4(d))
        .concat(trendPats(d)).concat(srPats(d)).concat(fibPats(d)).concat(structPats(d));
    var pmap2={}, pstack2={};
    chart2.forEach(function(p){   /* 图表/趋势/结构形态：骨架连线（有 i2/mid 时）+ 水平线组（lvl）+ 区间框（zone）+ 标签 */
      pmap2[p.i]=pmap2[p.i]?pmap2[p.i]+'·'+p.n:p.n;
      var col=p.dir>0?'#CA3F64':(p.dir<0?'#25A750':'#A0A6AD');
      if(p.zone){   /* 区间框：半透明矩形（p1=上沿 p2=下沿） */
        var zx1=x(Math.min(p.zone.i1,p.zone.i2))+cw/2, zx2=x(Math.max(p.zone.i1,p.zone.i2))+cw/2;
        var zy1=yfP(p.zone.p1), zy2=yfP(p.zone.p2);
        el('rect',{x:zx1,y:Math.min(zy1,zy2),width:Math.max(2,zx2-zx1),height:Math.max(2,Math.abs(zy2-zy1)),fill:col,opacity:0.13,stroke:col,'stroke-width':0.6,'stroke-dasharray':'3 2'},g);
      }
      if(p.lvl){   /* 水平线组：全宽虚线+右侧标签（越界裁剪） */
        p.lvl.forEach(function(lv){
          var y=yfP(lv.p);
          if(y<T+2||y>H-B-2)return;
          el('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:lv.col||col,'stroke-width':0.7,'stroke-dasharray':'6 3',opacity:0.75},g);
          hlabel(g,W-R-56,y-3,lv.t,lv.col||col,9);
        });
      }
      if(p.i2!==undefined&&p.mid!==undefined)
        polyline(g,[[x(p.i2)+cw/2,yfP(p.dir>0?d[p.i2].l:d[p.i2].h)],[x(p.mid)+cw/2,yfP(p.dir>0?d[p.mid].h:d[p.mid].l)],[x(p.i)+cw/2,yfP(p.dir>0?d[p.i].l:d[p.i].h)]],col,1.2,'5 3');
      var clv=pstack2[p.i]||0; pstack2[p.i]=clv+1;
      hlabel(g,x(p.i)-14,yfP(p.dir>0?d[p.i].l:d[p.i].h)+(p.dir>0?24:-12)+(p.dir>0?clv*11:-clv*11),p.n,col,10);
    });
    pats2.forEach(function(p){
      pmap2[p.i]=pmap2[p.i]?pmap2[p.i]+'·'+p.n:p.n;
      var col=p.dir>0?'#CA3F64':(p.dir<0?'#25A750':'#A0A6AD');
      var lv2=pstack2[p.i]||0; pstack2[p.i]=lv2+1;
      hlabel(g,x(p.i)-14,yfP(d[p.i].l)+24+lv2*11,p.n,col,10);
    });
    var all2=pats2.concat(chart2).sort(function(a,b){return a.i-b.i;});
    var lastP2=all2.length?all2[all2.length-1]:null;
    vd.innerHTML=all2.length
      ?'<span class="dim">识别 '+all2.length+' 处（K线 '+pats2.length+' + 图表/趋势/结构 '+chart2.length+'）：'+all2.slice(-4).map(function(p){return p.n;}).join(' / ')+' 等 · 注册表 256 条目已接 206（CANDLE 77+CHART 62+TREND 13+SR 10+FIB 17+STRUCT 25+ELW 2）；未接 50 条目=缠论 15（GAP-F-37 后端裁定）+数浪 6（wave-alpha 后端）+ML 套件 13+分时/订单流 16——负反馈待接入</span>'
      :'<span class="dim">当前时段未识别出形态（负反馈也是结果——系统明说"没有"）</span>';
    var cs2=lastP2?lastP2.dir:0;
    infoFill(pi,type,(lastP2?sigTag(cs2)+' · 最近形态「'+lastP2.n+'」（'+(n-1-lastP2.i)+' 根前）':'<b style="color:var(--faint)">无</b> · 当前时段未识别（负反馈）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+'  形态：'+(pmap2[i]||'无');
    }});
  }else if(type==='ema'||type==='wma'||type==='dema'||type==='tema'){
    /* 均线族叠加型：EMA/WMA/DEMA/TEMA 同版式（仿 ma 分支），仅算法/配色/名称不同 */
    var closes4=d.map(function(k){return k.c;});
    var RAW4=type==='ema'?emaArr(closes4,20):type==='wma'?wmaArr(closes4,20):type==='dema'?demaArr(closes4,20):temaArr(closes4,20);
    var AV4=[]; for(var i4=0;i4<n;i4++) AV4.push(RAW4[i4]===null||i4<19?null:RAW4[i4]);   /* 前 19 根统一 null */
    var COL4=type==='ema'?'#3D8BFF':type==='wma'?'#F0B90B':type==='dema'?'#AB47BC':'#FFD54F';
    var VCOL4=type==='ema'?'var(--blue)':type==='wma'?'var(--orange)':type==='dema'?'var(--purple)':'var(--yellow)';
    var NM4=type==='ema'?'EMA20':type==='wma'?'WMA20':type==='dema'?'DEMA20':'TEMA20';
    var rg4=rangeOf(d),lo4=rg4[0],hi4=rg4[1];
    var yf4=function(v){return T+(1-(v-lo4)/(hi4-lo4))*(H-T-B);};
    drawCandles(g,d,x,yf4,cw);
    polyline(g,AV4.map(function(v,i){return v===null?null:[x(i)+cw/2,yf4(v)];}),COL4,1.6);
    var aL4=AV4[last], asig4=d[last].c>aL4?1:-1;
    vd.innerHTML='<span style="color:'+VCOL4+'">— '+NM4+'</span><span class="dim">价格 '+(asig4>0?'上方':'下方')+'运行，偏离 '+(((d[last].c/aL4)-1)*100).toFixed(1)+'%</span>';
    infoFill(pi,type,sigTag(asig4)+' · 收盘 '+d[last].c.toFixed(1)+' 在 '+NM4+'（'+aL4.toFixed(1)+'）'+(asig4>0?'上方（趋势偏多）':'下方（趋势偏空）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+(AV4[i]!==null?'  '+NM4+' '+AV4[i].toFixed(1):'');
    }});
  }else if(type==='sar'){
    /* 叠加型：SAR 点列直接画在 K 线上，点在价下=多（红）、价上=空（绿） */
    var rg5=rangeOf(d),lo5=rg5[0],hi5=rg5[1];
    var yf5=function(v){return T+(1-(v-lo5)/(hi5-lo5))*(H-T-B);};
    drawCandles(g,d,x,yf5,cw);
    var SAR=sarCalc(d,0.02,0.2);
    SAR.forEach(function(v,i){
      if(v===null) return;
      el('circle',{cx:x(i)+cw/2,cy:yf5(v),r:1.6,fill:v<d[i].c?'#CA3F64':'#25A750'},g);
    });
    var sBelow=SAR[last]<d[last].c, sPrev=SAR[last-1]<d[last-1].c;
    var flipUp=sBelow&&!sPrev, flipDn=!sBelow&&sPrev;
    var ss=sBelow?1:-1;
    var stxt=flipUp?'SAR 今日上翻至价格下方（空转多，买入信号）':flipDn?'SAR 今日下翻至价格上方（多转空，卖出信号）':(sBelow?'SAR 在价格下方运行，多头持有':'SAR 在价格上方运行，空头规避');
    vd.innerHTML='<span style="color:var(--up)">● 多（价下）</span><span style="color:var(--down)">● 空（价上）</span><span class="dim">SAR(0.02,0.2) 翻转即转向/止损</span>';
    infoFill(pi,type,sigTag(ss)+' · '+stxt+'（SAR='+SAR[last].toFixed(1)+'）');
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+(SAR[i]!==null?'  SAR '+SAR[i].toFixed(1)+(SAR[i]<d[i].c?'（下/多）':'（上/空）'):'');
    }});
  }else if(type==='adx'){
    /* 独立窗格：固定域 0~60，虚线参考线 25；linePane 不过滤 null，仿 kdj 自写 yf */
    var ADX=adxCalc(d,14);
    var ya=function(v){return T+(1-v/60)*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:ya(25),y2:ya(25),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,ADX.map(function(v,i){return v===null?null:[x(i)+cw/2,ya(v)];}),'#FFD54F',1.4);
    var av=ADX[last];
    var astr=av===null?'数据不足':av>25?'趋势确立':av<20?'无趋势（震荡市）':'趋势形成中';
    vd.innerHTML='<span style="color:var(--yellow)">— ADX(14)</span><span class="dim">>25 趋势确立 / <20 无趋势（虚线 25）· 只量强度不分方向</span>';
    infoFill(pi,type,'<b style="color:var(--faint)">无方向信号</b> · ADX='+(av===null?'—':av.toFixed(1))+'，趋势强度：'+astr);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(ADX[i]!==null?'  ADX '+ADX[i].toFixed(1):'  ADX —');
    }});
  }else if(type==='dmi'){
    /* 独立窗格：+DI 蓝 / -DI 橙 双线 + ADX 紫细线，固定域 0~60（仿 kdj 自写 yf） */
    var DM=dmiCalc(d,14),PDI=DM[0],MDI=DM[1],DADX=DM[2];
    var ydm=function(v){return T+(1-v/60)*(H-T-B);};
    polyline(g,PDI.map(function(v,i){return v===null?null:[x(i)+cw/2,ydm(v)];}),'#3D8BFF',1.4);
    polyline(g,MDI.map(function(v,i){return v===null?null:[x(i)+cw/2,ydm(v)];}),'#F0B90B',1.4);
    polyline(g,DADX.map(function(v,i){return v===null?null:[x(i)+cw/2,ydm(v)];}),'#AB47BC',1.0);
    var pL=PDI[last],mL=MDI[last];
    var ds=pL>mL?1:-1;
    var cUp=pL>mL&&PDI[last-1]<=MDI[last-1], cDn=pL<mL&&PDI[last-1]>=MDI[last-1];
    var dtxt=cUp?'+DI 上穿 -DI 形成金叉（买入信号强化）':cDn?'+DI 下穿 -DI 形成死叉（卖出信号强化）':(ds>0?'+DI 在 -DI 上方运行，多头占优':'+DI 在 -DI 下方运行，空头占优');
    vd.innerHTML='<span style="color:var(--blue)">— +DI</span><span style="color:var(--orange)">— -DI</span><span style="color:var(--purple)">— ADX</span><span class="dim">+DI>-DI 多头 / 反之空头（域 0~60）</span>';
    infoFill(pi,type,sigTag(ds)+' · '+dtxt+'（+DI='+pL.toFixed(1)+'，-DI='+mL.toFixed(1)+'）');
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      var s=barLabel(i);
      if(PDI[i]!==null) s+='  +DI '+PDI[i].toFixed(1)+'  -DI '+MDI[i].toFixed(1);
      if(DADX[i]!==null) s+='  ADX '+DADX[i].toFixed(1);
      return s;
    }});
  }else if(type==='cci'){
    var CCI=cciCalc(d,14);
    var cmax=0;
    CCI.forEach(function(v){if(v!==null)cmax=Math.max(cmax,Math.abs(v));});
    cmax=Math.max(cmax,110);          /* 域自适应（对称），保底 ±110 让 ±100 参考线入画 */
    var yc=function(v){return T+(1-(v+cmax)/(2*cmax))*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:yc(100),y2:yc(100),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:yc(-100),y2:yc(-100),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,CCI.map(function(v,i){return v===null?null:[x(i)+cw/2,yc(v)];}),'#3D8BFF',1.4);
    var cv=CCI[last],cs=cv>100?-1:(cv<-100?1:0);
    vd.innerHTML='<span style="color:var(--blue)">— CCI(14)</span><span class="dim">+100 上超买 / -100 下超卖 · 当前 '+cv.toFixed(1)+'</span>';
    infoFill(pi,type,sigTag(cs)+' · CCI='+cv.toFixed(1)+(cs<0?' 上破 +100（超买区，卖出偏向）':cs>0?' 下破 -100（超卖区，买入偏向）':' 常态区间（中性）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(CCI[i]===null?'':'  CCI '+CCI[i].toFixed(1));
    }});
  }else if(type==='stochrsi'){
    var SR=stochRsiCalc(d,14),SK=SR[0],SD=SR[1];
    var ys=function(v){return T+(1-v/100)*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:ys(80),y2:ys(80),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:ys(20),y2:ys(20),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,SK.map(function(v,i){return v===null?null:[x(i)+cw/2,ys(v)];}),'#3D8BFF',1.4);
    polyline(g,SD.map(function(v,i){return v===null?null:[x(i)+cw/2,ys(v)];}),'#F0B90B',1.4);
    var kv=SK[last],dv=SD[last],ss2=kv<20?1:(kv>80?-1:0);
    vd.innerHTML='<span style="color:var(--blue)">— %K</span><span style="color:var(--orange)">— %D</span><span class="dim">StochRSI(14,3,3) · 80 上超买 / 20 下超卖</span>';
    infoFill(pi,type,sigTag(ss2)+' · %K='+kv.toFixed(1)+' / %D='+dv.toFixed(1)+(ss2>0?' 超卖区（买入偏向）':ss2<0?' 超买区（卖出偏向）':' 中性区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      var s=barLabel(i);
      if(SK[i]!==null)s+='  %K '+SK[i].toFixed(1);
      if(SD[i]!==null)s+='  %D '+SD[i].toFixed(1);
      return s;
    }});
  }else if(type==='cmo'){
    var CMO=cmoCalc(d,14);
    var ym2=function(v){return T+(1-(v+100)/200)*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:ym2(0),y2:ym2(0),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,CMO.map(function(v,i){return v===null?null:[x(i)+cw/2,ym2(v)];}),'#AB47BC',1.4);
    var cmv=CMO[last],cms=cmv>50?-1:(cmv<-50?1:0);
    var cmtxt=cmv>50?'强势区（注意过热，卖出偏向）':cmv<-50?'弱势区（超卖关注，买入偏向）':cmv>=0?'零轴上方（多头占优）':'零轴下方（空头占优）';
    vd.innerHTML='<span style="color:var(--purple)">— CMO(14)</span><span class="dim">域 -100~+100 · ±50 极值 / 零轴定多空</span>';
    infoFill(pi,type,sigTag(cms)+' · CMO='+cmv.toFixed(1)+' '+cmtxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(CMO[i]===null?'':'  CMO '+CMO[i].toFixed(1));
    }});
  }else if(type==='uo'){
    var UO=uoCalc(d);
    var yu=function(v){return T+(1-v/100)*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:yu(70),y2:yu(70),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:yu(30),y2:yu(30),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,UO.map(function(v,i){return v===null?null:[x(i)+cw/2,yu(v)];}),'#FFD54F',1.4);
    var uv=UO[last],us=uv<30?1:(uv>70?-1:0);
    vd.innerHTML='<span style="color:var(--yellow)">— UO(7,14,28)</span><span class="dim">70 上超买 / 30 下超卖</span>';
    infoFill(pi,type,sigTag(us)+' · UO='+uv.toFixed(1)+(us>0?' 低于 30（超卖区，买入偏向）':us<0?' 高于 70（超买区，卖出偏向）':' 中性区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(UO[i]===null?'':'  UO '+UO[i].toFixed(1));
    }});
  }else if(type==='kc'){
    /* 叠加型：KC 三轨直接画在 K 线上（同 boll 分支模式） */
    var KC=kcCalc(d),kup=KC[0],kmid=KC[1],klow=KC[2];
    var lo5=1e9,hi5=-1e9;
    d.forEach(function(k){lo5=Math.min(lo5,k.l);hi5=Math.max(hi5,k.h);});
    for(var i5=0;i5<n;i5++){hi5=Math.max(hi5,kup[i5]);lo5=Math.min(lo5,klow[i5]);}
    var pad5=(hi5-lo5)*0.08; lo5-=pad5; hi5+=pad5;
    var yk5=function(v){return T+(1-(v-lo5)/(hi5-lo5))*(H-T-B);};
    drawCandles(g,d,x,yk5,cw);
    polyline(g,kup.map(function(v,i){return[x(i)+cw/2,yk5(v)];}),'#FFD54F',1.2);
    polyline(g,kmid.map(function(v,i){return[x(i)+cw/2,yk5(v)];}),'#3D8BFF',1.4);
    polyline(g,klow.map(function(v,i){return[x(i)+cw/2,yk5(v)];}),'#AB47BC',1.2);
    var ks=d[last].c>=kup[last]?-1:(d[last].c<=klow[last]?1:0);
    var ktxt=ks<0?'收盘 '+d[last].c.toFixed(1)+' 触上轨 '+kup[last].toFixed(1)+'（超买警戒，卖出偏向）':ks>0?'收盘 '+d[last].c.toFixed(1)+' 触下轨 '+klow[last].toFixed(1)+'（超卖关注，买入偏向）':'通道内运行（中轨 '+kmid[last].toFixed(1)+'）';
    vd.innerHTML='<span style="color:var(--yellow)">— 上轨</span><span style="color:var(--blue)">— 中轨 EMA20</span><span style="color:var(--purple)">— 下轨</span><span class="dim">KC(20,2×ATR14) 叠加 K 线（与主图同坐标系）</span>';
    infoFill(pi,type,sigTag(ks)+' · '+ktxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+'  上 '+kup[i].toFixed(1)+' 中 '+kmid[i].toFixed(1)+' 下 '+klow[i].toFixed(1);
    }});
  }else if(type==='dc'){
    /* 叠加型：唐奇安通道三轨直接画在 K 线上 */
    var DC=dcCalc(d,20),dup=DC[0],dmid=DC[1],dlow=DC[2];
    var lo6=1e9,hi6=-1e9;
    d.forEach(function(k){lo6=Math.min(lo6,k.l);hi6=Math.max(hi6,k.h);});
    var pad6=(hi6-lo6)*0.08; lo6-=pad6; hi6+=pad6;
    var yd6=function(v){return T+(1-(v-lo6)/(hi6-lo6))*(H-T-B);};
    drawCandles(g,d,x,yd6,cw);
    polyline(g,dup.map(function(v,i){return[x(i)+cw/2,yd6(v)];}),'#F0B90B',1.2);
    polyline(g,dmid.map(function(v,i){return[x(i)+cw/2,yd6(v)];}),'#EDEFF2',1.2);
    polyline(g,dlow.map(function(v,i){return[x(i)+cw/2,yd6(v)];}),'#3D8BFF',1.2);
    var ds2=d[last].c>=dup[last]?1:(d[last].c<=dlow[last]?-1:0);
    var dtxt=ds2>0?'收盘 '+d[last].c.toFixed(1)+' 突破上轨 '+dup[last].toFixed(1)+'（20 根新高，强势买入偏向）':ds2<0?'收盘 '+d[last].c.toFixed(1)+' 跌破下轨 '+dlow[last].toFixed(1)+'（20 根新低，卖出偏向）':'通道内运行（上 '+dup[last].toFixed(1)+' / 下 '+dlow[last].toFixed(1)+'）';
    vd.innerHTML='<span style="color:var(--orange)">— 上轨(20高)</span><span style="color:var(--text)">— 中轨</span><span style="color:var(--blue)">— 下轨(20低)</span><span class="dim">DC(20) 叠加 K 线</span>';
    infoFill(pi,type,sigTag(ds2)+' · '+dtxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+'  上 '+dup[i].toFixed(1)+' 中 '+dmid[i].toFixed(1)+' 下 '+dlow[i].toFixed(1);
    }});
  }else if(type==='std'){
    var STD=stdCalc(d,20);
    var smax=0;
    STD.forEach(function(v){if(v!==null)smax=Math.max(smax,v);});
    var yd2=function(v){return T+(1-v/(smax*1.1||1))*(H-T-B);};
    polyline(g,STD.map(function(v,i){return v===null?null:[x(i)+cw/2,yd2(v)];}),'#FFD54F',1.4);
    var sv=STD[last],sUp=sv>STD[last-5];
    vd.innerHTML='<span style="color:var(--yellow)">— STD(20)</span><span class="dim">收盘价 20 根标准差 · 波动度量无方向</span>';
    infoFill(pi,type,'<b style="color:var(--faint)">无方向信号</b> · STD='+sv.toFixed(2)+'，波动较 5 日前'+(sUp?'上升':'下降'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(STD[i]===null?'':'  STD '+STD[i].toFixed(2));
    }});
  }else if(type==='bollw'){
    var BW=bollwCalc(d,20,2);
    var wmax=0,vals=[];
    BW.forEach(function(v){if(v!==null){wmax=Math.max(wmax,v);vals.push(v);}});
    var yw=function(v){return T+(1-v/(wmax*1.1||1))*(H-T-B);};
    polyline(g,BW.map(function(v,i){return v===null?null:[x(i)+cw/2,yw(v)];}),'#3D8BFF',1.4);
    vals.sort(function(a,b){return a-b;});
    var th=vals[Math.floor(0.2*(vals.length-1))];
    var wv=BW[last],sqz=wv<=th;
    vd.innerHTML='<span style="color:var(--blue)">— BOLLW(20,2)</span><span class="dim">(上轨-下轨)/中轨×100 · 当前 '+wv.toFixed(1)+'%'+(sqz?' · 挤压中':'')+'</span>';
    infoFill(pi,type,'<b style="color:var(--faint)">无方向信号</b> · 带宽='+wv.toFixed(1)+'%'+(sqz?'，处于全窗口最低 20% 分位——带宽挤压，变盘临近':'，带宽未处挤压区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(BW[i]===null?'':'  带宽 '+BW[i].toFixed(1)+'%');
    }});
  }else if(type==='bollb'){
    var PB=bollbCalc(d,20,2);
    var yb=function(v){return T+(1-(v+0.2)/1.4)*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:yb(1),y2:yb(1),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:yb(0.5),y2:yb(0.5),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    el('line',{x1:L,x2:W-R,y1:yb(0),y2:yb(0),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,PB.map(function(v,i){return v===null?null:[x(i)+cw/2,yb(v)];}),'#F0B90B',1.4);
    var bv=PB[last],bs9=bv>1?-1:(bv<0?1:0);
    vd.innerHTML='<span style="color:var(--orange)">— %B(20,2)</span><span class="dim">域 -0.2~1.2 · 参考线 1 / 0.5 / 0</span>';
    infoFill(pi,type,sigTag(bs9)+' · %B='+bv.toFixed(2)+(bs9<0?' 超上轨（>1，卖出偏向）':bs9>0?' 破下轨（<0，买入偏向）':' 带内运行（中性）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(PB[i]===null?'':'  %B '+PB[i].toFixed(2));
    }});
  }else if(type==='hv'){
    var HV=hvCalc(d,20);
    var hmax2=0;
    HV.forEach(function(v){if(v!==null)hmax2=Math.max(hmax2,v);});
    var yh2=function(v){return T+(1-v/(hmax2*1.1||1))*(H-T-B);};
    polyline(g,HV.map(function(v,i){return v===null?null:[x(i)+cw/2,yh2(v)];}),'#25A750',1.4);
    var hv2=HV[last],hUp=hv2>HV[last-5];
    vd.innerHTML='<span style="color:var(--down)">— HV(20)</span><span class="dim">日收益对数标准差×√252 年化 · 无方向</span>';
    infoFill(pi,type,'<b style="color:var(--faint)">无方向信号</b> · HV='+hv2.toFixed(1)+'%，较 5 日前'+(hUp?'上升':'下降'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(HV[i]===null?'':'  HV '+HV[i].toFixed(1)+'%');
    }});
  }else if(type==='mfi'){
    var MF=mfiCalc(d,14);
    var yfm=function(v){return T+(1-v/100)*(H-T-B);};
    [80,20].forEach(function(rv){el('line',{x1:L,x2:W-R,y1:yfm(rv),y2:yfm(rv),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);});
    polyline(g,MF.map(function(v,i){return v==null?null:[x(i)+cw/2,yfm(v)];}),'#3D8BFF',1.4);
    var mv=MF[last], ms=mv<20?1:(mv>80?-1:0);
    vd.innerHTML='<span style="color:var(--blue)">— MFI(14)</span><span class="dim">80 上超买 / 20 下超卖（量加强版 RSI）</span>';
    infoFill(pi,type,sigTag(ms)+' · MFI='+mv.toFixed(1)+(ms>0?' 超卖区，资金流出衰竭（关注买入）':ms<0?' 超买区，资金流入过热（警惕卖出）':' 中性区'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(MF[i]==null?'':'  MFI '+MF[i].toFixed(1));
    }});
  }else if(type==='vwap'){
    /* 叠加型指标：VWAP 画在 K 线上（同 boll/ma 分支模式），窗口锚定口径（第 0 根起累计） */
    var VW=vwapCalc(d);
    var lo4=1e9,hi4=-1e9;
    d.forEach(function(k){lo4=Math.min(lo4,k.l);hi4=Math.max(hi4,k.h);});
    VW.forEach(function(v){lo4=Math.min(lo4,v);hi4=Math.max(hi4,v);});
    var pad4=(hi4-lo4)*0.08; lo4-=pad4; hi4+=pad4;
    var yf4=function(v){return T+(1-(v-lo4)/(hi4-lo4))*(H-T-B);};
    drawCandles(g,d,x,yf4,cw);
    polyline(g,VW.map(function(v,i){return[x(i)+cw/2,yf4(v)];}),'#FFD54F',1.6);
    var vws=d[last].c>=VW[last]?1:-1;
    vd.innerHTML='<span style="color:var(--yellow)">— VWAP</span><span class="dim">窗口锚定口径（本图第 1 根起累计 ΣTP·V/ΣV），非日内锚定</span>';
    infoFill(pi,type,sigTag(vws)+' · 收盘 '+d[last].c.toFixed(1)+' 在 VWAP（'+VW[last].toFixed(1)+'，窗口锚定口径）'+(vws>0?'上方，持仓者整体浮盈（买入偏向）':'下方，持仓者整体浮亏（卖出偏向）'));
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  收 '+d[i].c.toFixed(1)+'  VWAP '+VW[i].toFixed(1);
    }});
  }else if(type==='vr'){
    var VR=vrCalc(d,26);
    var vrMax=0; VR.forEach(function(v){if(v!=null)vrMax=Math.max(vrMax,v);});
    var vrHi=Math.max(200,vrMax*1.1);
    var yfv=function(v){return T+(1-v/vrHi)*(H-T-B);};
    [70,150].forEach(function(rv){el('line',{x1:L,x2:W-R,y1:yfv(rv),y2:yfv(rv),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);});
    polyline(g,VR.map(function(v,i){return v==null?null:[x(i)+cw/2,yfv(v)];}),'#F0B90B',1.4);
    var vv=VR[last], vs=vv<70?1:(vv>350?-1:0);
    var vtxt=vv<70?'低价区，抛压衰竭（买入偏向）':vv>350?'过热区，获利盘蜂拥（卖出偏向）':vv>150?'获利盘警戒区（>350 转卖出）':'中性区';
    vd.innerHTML='<span style="color:var(--orange)">— VR(26)</span><span class="dim">70 下低价区 / 150 上警戒 / 350 上过热</span>';
    infoFill(pi,type,sigTag(vs)+' · VR='+vv.toFixed(0)+' '+vtxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(VR[i]==null?'':'  VR '+VR[i].toFixed(0));
    }});
  }else if(type==='adl'){
    var AD=adlCalc(d);
    var amin=Math.min.apply(null,AD),amax=Math.max.apply(null,AD);
    linePane(AD,amin,amax,'#FFD54F',null);
    var pTop=-1e9,aTop=-1e9,pBot=1e9,aBot=1e9;
    for(var j=last-5;j<last;j++){
      pTop=Math.max(pTop,d[j].c); aTop=Math.max(aTop,AD[j]);
      pBot=Math.min(pBot,d[j].c); aBot=Math.min(aBot,AD[j]);
    }
    var pNH=d[last].c>pTop, aNH=AD[last]>aTop, pNL=d[last].c<pBot, aNL=AD[last]<aBot;
    var as=pNH&&!aNH?-1:(pNL&&!aNL?1:0);
    var atxt=pNH&&!aNH?'价格 5 日新高而 ADL 未新高，顶背离警告（派发迹象）':(pNL&&!aNL?'价格 5 日新低而 ADL 未新低，底背离（承接显现）':(pNH&&aNH?'量价同创新高（累积健康）':(pNL&&aNL?'量价同创新低（同弱，未现背离）':'区间整理，量价无背离')));
    vd.innerHTML='<span style="color:var(--yellow)">— ADL</span><span class="dim">量价同向为健康、背离为警告（5 日新高/新低判读）</span>';
    infoFill(pi,type,sigTag(as)+' · '+atxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  ADL '+AD[i].toFixed(0);
    }});
  }else if(type==='pvt'){
    var PV=pvtCalc(d);
    var pmin=Math.min.apply(null,PV),pmax=Math.max.apply(null,PV);
    linePane(PV,pmin,pmax,'#AB47BC',null);
    var pTop2=-1e9,vTop2=-1e9,pBot2=1e9,vBot2=1e9;
    for(var j2=last-5;j2<last;j2++){
      pTop2=Math.max(pTop2,d[j2].c); vTop2=Math.max(vTop2,PV[j2]);
      pBot2=Math.min(pBot2,d[j2].c); vBot2=Math.min(vBot2,PV[j2]);
    }
    var pNH2=d[last].c>pTop2, vNH2=PV[last]>vTop2, pNL2=d[last].c<pBot2, vNL2=PV[last]<vBot2;
    var ps=pNH2&&!vNH2?-1:(pNL2&&!vNL2?1:0);
    var ptxt=pNH2&&!vNH2?'价格 5 日新高而 PVT 未新高，顶背离警告':(pNL2&&!vNL2?'价格 5 日新低而 PVT 未新低，底背离（关注买入）':(pNH2&&vNH2?'量价同创新高（趋势健康）':(pNL2&&vNL2?'量价同创新低（同弱，未现背离）':'区间整理，量价无背离')));
    vd.innerHTML='<span style="color:var(--purple)">— PVT</span><span class="dim">量价同向为健康、背离为警告（5 日新高/新低判读）</span>';
    infoFill(pi,type,sigTag(ps)+' · '+ptxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  PVT '+PV[i].toFixed(0);
    }});
  }else if(type==='cmf'){
    var CM=cmfCalc(d,20);
    var cmx=0; CM.forEach(function(v){if(v!=null)cmx=Math.max(cmx,Math.abs(v));});
    cmx=Math.max(cmx,0.05)*1.15;
    var yfc=function(v){return T+(1-(v+cmx)/(2*cmx))*(H-T-B);};
    el('line',{x1:L,x2:W-R,y1:yfc(0),y2:yfc(0),stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
    polyline(g,CM.map(function(v,i){return v==null?null:[x(i)+cw/2,yfc(v)];}),'#25A750',1.4);
    var cv=CM[last], cs=cv>0?1:-1;
    var ctxt=cv>0.1?'资金明显净流入（CMF>0.1，多方占优）':cv>0?'资金净流入（零轴上方）':cv<-0.1?'资金明显净流出（CMF<-0.1，空方占优）':'资金净流出（零轴下方）';
    vd.innerHTML='<span style="color:var(--down)">— CMF(20)</span><span class="dim">零轴上净流入 / 下净流出（±0.1 加强）</span>';
    infoFill(pi,type,sigTag(cs)+' · CMF='+cv.toFixed(3)+' '+ctxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+(CM[i]==null?'':'  CMF '+CM[i].toFixed(3));
    }});
  }else if(type==='wvad'){
    /* 零轴柱状图口径（非累计线）：WVAD 柱红正绿负 + 6 根均线，均线上穿零轴判信号 */
    var WVM=wvadCalc(d,6),WV=WVM[0],WM=WVM[1];
    var wmax=maxAbs(WV);
    var yw=function(v){return T+(1-(v+wmax)/(2*wmax))*(H-T-B);};
    var zeroY=yw(0);
    WV.forEach(function(v,i){
      el('rect',{x:x(i),y:Math.min(yw(v),zeroY),width:cw,height:Math.max(1.5,Math.abs(yw(v)-zeroY)),fill:v>=0?'#CA3F64':'#25A750'},g);
    });
    polyline(g,WM.map(function(v,i){return v==null?null:[x(i)+cw/2,yw(v)];}),'#F0B90B',1.4);
    var wUp=WM[last]>0&&WM[last-1]<=0, wDn=WM[last]<0&&WM[last-1]>=0;
    var ws=wUp?1:(wDn?-1:0);
    var wtxt=wUp?'MA6 上穿零轴（多方量能转强）':wDn?'MA6 下穿零轴（空方量能转强）':(WM[last]>0?'MA6 零轴上方运行（偏多延续）':'MA6 零轴下方运行（偏空延续）');
    vd.innerHTML='<span style="color:var(--up)">■ 正柱</span><span style="color:var(--down)">■ 负柱</span><span style="color:var(--orange)">— MA6</span><span class="dim">'+wtxt+'</span>';
    infoFill(pi,type,sigTag(ws)+' · '+wtxt);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){
      return barLabel(i)+'  WVAD '+WV[i].toFixed(0)+(WM[i]==null?'':'  MA6 '+WM[i].toFixed(0));
    }});
  }else{
    /* 待接入：负反馈 + 信息卡 */
    var t=el('text',{x:40,y:130,fill:'#59626D','font-size':13},g);
    t.textContent='「'+(IND_NAME[type]||type)+'」渲染器待接入——信息卡照常显示（全量接入工程见设计文档 §5 缺口④）';
    vd.innerHTML='';
    infoFill(pi,type,'<b style="color:var(--faint)">—</b> · 渲染器待接入，无信号输出（负反馈也是结果）');
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:cw,g:g,rd:rd,readout:function(i){return barLabel(i)+'  渲染器待接入';}});
  }
}

/* ---- 阶段状态带 ---- */
function renderPhase(d){
  var svg=document.getElementById('svg-phase'); svg.innerHTML='';
  var W=1100,H=240,L=10,R=86,T=30,B=14;   /* R=86 与主图一致：十字光标跨图共线 */
  var rg=rangeOf(d),lo=rg[0],hi=rg[1];
  var x=function(i){return L+(i+0.5)*(W-L-R)/d.length;};
  var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg);
  var bands=[[0,36,'上升段 · 趋势确认','#CA3F64'],[36,62,'下跌段 · 获利回吐','#25A750'],[62,94,'震荡段 · 箱体整理','#8a94a6'],[94,120,'修复段 · 当前（震荡偏强）','#FFD54F']];
  bands.forEach(function(b){
    el('rect',{x:x(b[0]),y:8,width:x(b[1])-x(b[0]),height:H-8-B,fill:b[3],opacity:0.13},g);
    el('line',{x1:x(b[0]),x2:x(b[0]),y1:8,y2:H-B,stroke:b[3],'stroke-width':1,opacity:0.6},g);
    hlabel(g,x(b[0])+8,24,b[2],b[3]);
  });
  var pts=[]; for(var i=0;i<d.length;i++) pts.push([x(i),yf(d[i].c)]);
  polyline(g,pts,'#EDEFF2',1.5);
  var rdP=mkReadout(svg.parentNode);
  bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:d.length,x:x,cw:0,g:g,rd:rdP,readout:function(i2){
    var seg=''; for(var b=0;b<bands.length;b++) if(i2>=bands[b][0]&&i2<bands[b][1]) seg=bands[b][2];
    return barLabel(i2)+'  收 '+d[i2].c.toFixed(1)+'  阶段：'+seg;
  }});
}

function renderIdxAll(){
  var meta=IDX_META[curIdx];
  document.getElementById('idx-title').textContent=meta.name;
  document.getElementById('idx-price').textContent=meta.price;
  var chgEl=document.getElementById('idx-chg');
  chgEl.textContent=meta.chg; chgEl.className=meta.up?'up':'down';
  /* I-5c 两态：指数=Regime+阶段带；个股=Regime 不适用+阶段带换负反馈 */
  var isIdx=meta.type==='index';
  document.getElementById('idx-regime').style.display=isIdx?'':'none';
  document.getElementById('idx-regime-na').style.display=isIdx?'none':'';
  document.getElementById('phase-box').style.display=isIdx?'':'none';
  document.getElementById('phase-na').style.display=isIdx?'none':'';
  var d=genCandles(meta.seed+curPer*17);
  var fScale=meta.base/d[d.length-1].c;   /* 序列锚定到真实价位量级（期末收=现价） */
  d.forEach(function(k){k.o*=fScale;k.c*=fScale;k.h*=fScale;k.l*=fScale;});
  renderMain(d); renderPhase(d); renderPanes(d);
  renderMC(meta);
  document.getElementById('per-lbl-1').textContent=PER_NAMES[curPer];
  document.getElementById('per-lbl-4').textContent=PER_NAMES[curPer];
}
/* ---- I-5c 技术分析页：标的搜索/快捷切换（指数+个股同页） ---- */
function techSwitch(sym,elm){
  if(!IDX_META[sym])return;
  curIdx=sym;
  document.querySelectorAll('.tech-sel').forEach(function(s){s.classList.toggle('on',s===elm||s.getAttribute('data-sym')===sym);});
  var inp=document.getElementById('tech-srch'); if(inp)inp.value='';
  var lst=document.getElementById('tech-srch-list'); if(lst)lst.innerHTML='';
  renderIdxAll();
}
function techSearch(q){
  var lst=document.getElementById('tech-srch-list'); if(!lst)return;
  q=(q||'').trim();
  if(!q){lst.innerHTML='';return;}
  var hits=Object.keys(IDX_SHORT).filter(function(k){
    return IDX_SHORT[k].indexOf(q)>=0||k.indexOf(q)>=0||IDX_META[k].name.indexOf(q)>=0;
  });
  if(!hits.length){
    lst.innerHTML='<span class="tech-srch-item na">「'+q+'」不在演示标的池（指数 4+个股 3）——全量标的待接入（负反馈也是结果）</span>';
    return;
  }
  lst.innerHTML=hits.map(function(k){
    return '<span class="tech-srch-item" onclick="techSwitch(\''+k+'\',null)">'+IDX_SHORT[k]+' <span class="dim">'+IDX_META[k].name.match(/（(.*?)）/)[1]+'</span></span>';
  }).join('');
}
function techSearchGo(){
  var first=document.querySelector('#tech-srch-list .tech-srch-item[onclick]');
  if(first) first.click();
}
/* A11 多周期同屏：六格迷你K线（视觉示意，复用 genCandles 不同周期种子） */
function renderMC(meta){
  var el=document.getElementById('mc-grid'); if(!el)return;
  var names=['1分钟','5分钟','15分钟','30分钟','60分钟','日线'];
  var h='';
  names.forEach(function(nm,i){
    var dd=genCandles(meta.seed+i*31).slice(-28);
    var fs=meta.base/dd[dd.length-1].c;
    var pts='',min=1e18,max=-1e18;
    dd.forEach(function(k){var c=k.c*fs;if(c<min)min=c;if(c>max)max=c;});
    var rg=(max-min)||1,W=200,H=54;
    dd.forEach(function(k,j){var x=j/(dd.length-1)*W;var y=H-((k.c*fs-min)/rg)*H;pts+=(j?'L':'M')+x.toFixed(1)+' '+y.toFixed(1)+' ';});
    var lastUp=dd[dd.length-1].c>=dd[dd.length-2].c;
    h+='<div style="background:#000000;border:1px solid var(--border);border-radius:6px;padding:6px 8px">'
      +'<div style="font-size:11px;color:var(--dim);display:flex;justify-content:space-between"><span>'+nm+'</span><span style="color:'+(lastUp?'var(--up)':'var(--down)')+'">'+(lastUp?'▲':'▼')+'</span></div>'
      +'<svg viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none" style="width:100%;height:'+H+'px;display:block"><path d="'+pts+'" fill="none" stroke="'+(lastUp?'var(--up)':'var(--down)')+'" stroke-width="1.5"/></svg></div>';
  });
  el.innerHTML=h;
}
/* goIdx 已随 I-5c 指数合并退役（原 4 导航项撤销，页内切换走 techSwitch） */
/* A2 策略看板选择 + A1 详情曲线 */
function stratSel(i,el){
  document.querySelectorAll('#p-strategy .factor-card').forEach(function(c){c.classList.remove('active');});
  el.classList.add('active');
  var nm=el.querySelector('div').textContent;
  document.getElementById('sd-name').textContent=nm;
  drawLine('sd-curve',genCandles(1000+i*7).map(function(k){return k.c;}),'var(--accent)',400,160);
}
/* A7 因子选择 + A8 详情图 */
function factorSel(name,el){
  document.getElementById('fc-name').childNodes[0].textContent=name+' · 分组净值 ';
  drawLine('fc-nav',genCandles(2000+name.length*13).map(function(k){return k.c;}),'var(--up)',400,170);
  drawLine('fc-ic',genCandles(3000+name.length*17).map(function(k){return k.c;}),'var(--accent)',400,110);
}
/* 通用折线渲染（视觉示意） */
function drawLine(id,vals,color,W,H){
  var svg=document.getElementById(id); if(!svg)return;
  var min=Math.min.apply(null,vals),max=Math.max.apply(null,vals),rg=(max-min)||1;
  var pts='';vals.forEach(function(v,i){var x=i/(vals.length-1)*W;var y=H-((v-min)/rg)*(H-10)-5;pts+=(i?'L':'M')+x.toFixed(1)+' '+y.toFixed(1)+' ';});
  /* 刻意超越包：面积渐变填充（20%→0，同色 linearGradient，id 防冲突） */
  var gid='sg-'+id;
  svg.innerHTML='<defs><linearGradient id="'+gid+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="'+color+'" stop-opacity="0.2"/><stop offset="1" stop-color="'+color+'" stop-opacity="0"/></linearGradient></defs>'
    +'<path d="'+pts+' L'+W+' '+H+' L0 '+H+' Z" fill="url(#'+gid+')" stroke="none"/>'
    +'<path d="'+pts+'" fill="none" stroke="'+color+'" stroke-width="1.6"/>';
}
function setPer(p,el){
  curPer=p;
  document.querySelectorAll('#per-tabs .tab').forEach(function(t){t.classList.remove('on');});
  el.classList.add('on');
  renderIdxAll();
}


/* ---- 日收益率柱状图 + K线蜡烛 + 成交量：程序化生成（视觉示意） ---- */
(function(){
  var NS='http://www.w3.org/2000/svg';
  // 日收益率柱：1100x300，零线 y=150
  var dr=document.getElementById('dr-bars');
  if(dr){
    var vals=[1.2,-0.8,2.1,0.5,-1.6,0.9,1.8,-0.4,2.6,-1.1,0.7,1.4,-2.0,1.1,0.3,-0.9,1.6,2.2,-0.6,1.0,-1.4,0.8,1.9,-0.2,1.3,-1.8,0.6,2.4,-1.0,0.4,1.5,-0.7,2.0,0.9,-1.2,1.7,0.2,-1.5,1.2,2.8,-0.5,1.1,-0.9,1.4,0.6,-2.2,1.8,0.4,1.0,-1.3];
    var w=1100/vals.length;
    vals.forEach(function(v,i){
      var r=document.createElementNS(NS,'rect');
      var h=Math.abs(v)*28;
      r.setAttribute('x',(i*w+1));r.setAttribute('width',(w-2));
      r.setAttribute('y',v>=0?150-h:150);r.setAttribute('height',h);
      r.setAttribute('fill',v>=0?'#CA3F64':'#25A750');
      dr.appendChild(r);
    });
  }
  // K线蜡烛：1100x620，K线区 y 60~420，量区 y 460~600
  var c=document.getElementById('candles'), v=document.getElementById('vols');
  if(c&&v){
    var o=150; // 起始价（SVG y 坐标反向）
    for(var i=0;i<24;i++){
      var x=40+i*44;
      var chg=(Math.sin(i*1.7)+Math.cos(i*0.6)*0.8)*28;
      var cl=o-chg, hi=Math.min(o,cl)-8-Math.abs(chg)*0.3, lo=Math.max(o,cl)+8+Math.abs(chg)*0.25;
      var up=cl<o, col=up?'#CA3F64':'#25A750';
      var wick=document.createElementNS(NS,'line');
      wick.setAttribute('x1',x+8);wick.setAttribute('x2',x+8);
      wick.setAttribute('y1',hi);wick.setAttribute('y2',lo);
      wick.setAttribute('stroke',col);wick.setAttribute('stroke-width','1.5');
      c.appendChild(wick);
      var body=document.createElementNS(NS,'rect');
      body.setAttribute('x',x);body.setAttribute('width',16);
      body.setAttribute('y',Math.min(o,cl));body.setAttribute('height',Math.max(3,Math.abs(chg)));
      body.setAttribute('fill',col);
      c.appendChild(body);
      // 成交量
      var vh=20+Math.abs(chg)*1.6+((i*37)%23);
      var vb=document.createElementNS(NS,'rect');
      vb.setAttribute('x',x);vb.setAttribute('width',16);
      vb.setAttribute('y',600-vh);vb.setAttribute('height',vh);
      vb.setAttribute('fill',col);vb.setAttribute('opacity','0.75');
      v.appendChild(vb);
      o=cl;
    }
  }
})();

/* ==================== 外盘迷你卡 / T分析分时图 / 板块贡献度 ==================== */
function genIntraday(seed,n){
  n=n||241; var r=lcg(seed),pts=[],p=100;
  for(var i=0;i<n;i++){ p+=(r()-0.5)*0.7; pts.push(p); }
  return pts;
}
function miniSpark(seed,up){
  var pts=genIntraday(seed,60);
  var lo=Math.min.apply(null,pts),hi=Math.max.apply(null,pts);
  var path=pts.map(function(v,i){return (i*3.4).toFixed(1)+','+(34-(v-lo)/(hi-lo)*30).toFixed(1);}).join(' ');
  return '<svg viewBox="0 0 204 38" preserveAspectRatio="none" style="width:100%;height:38px;margin-top:4px"><polyline points="'+path+'" fill="none" stroke="'+(up?'#CA3F64':'#25A750')+'" stroke-width="1.5"/></svg>';
}
function renderOverseas(){
  var grid=document.getElementById('ovs-grid'); if(!grid)return;
  var items=[
    {n:'道琼斯',v:'41,208.6',c:'-0.42%',up:0,time:'昨夜收盘',tag:'利空',tc:'b-sell',s:11},
    {n:'纳斯达克',v:'18,542.3',c:'-0.87%',up:0,time:'昨夜收盘',tag:'利空',tc:'b-sell',s:22},
    {n:'标普500',v:'5,912.4',c:'-0.55%',up:0,time:'昨夜收盘',tag:'利空',tc:'b-sell',s:33},
    {n:'恒生指数',v:'24,318',c:'+0.62%',up:1,time:'实时',tag:'利好',tc:'b-buy',s:44},
    {n:'日经225',v:'39,120',c:'+0.21%',up:1,time:'实时·早盘已收',tag:'中性',tc:'b-na',s:55},
    {n:'韩国KOSPI',v:'2,684',c:'-0.18%',up:0,time:'实时',tag:'中性',tc:'b-na',s:66},
    {n:'富时A50期货',v:'13,542',c:'+0.18%',up:1,time:'实时',tag:'弱利好',tc:'b-buy',s:77},
    {n:'美元指数',v:'104.32',c:'+0.31%',up:1,time:'实时',tag:'弱利空',tc:'b-sell',s:88},
    {n:'离岸人民币',v:'7.2412',c:'-0.12%',up:0,time:'实时',tag:'弱利空',tc:'b-sell',s:99},
    {n:'WTI原油',v:'78.42',c:'+1.20%',up:1,time:'实时',tag:'中性',tc:'b-na',s:111},
    {n:'COMEX黄金',v:'2,412.8',c:'+0.40%',up:1,time:'实时',tag:'中性',tc:'b-na',s:122},
    {n:'美债10Y收益率',v:'4.28%',c:'+3bp',up:0,time:'实时',tag:'弱利空',tc:'b-sell',s:133}
  ];
  var html='';
  items.forEach(function(it){
    html+='<div class="card metric"><div class="l">'+it.n+' <span class="dim">'+it.time+'</span></div>'
      +'<div class="v" style="font-size:17px">'+it.v+' <span style="font-size:13px" class="'+(it.up?'up':'down')+'">'+it.c+'</span></div>'
      +miniSpark(it.s,it.up)
      +'<div class="s" style="margin-top:4px">对A股：<span class="badge '+it.tc+'">'+it.tag+'</span></div></div>';
  });
  grid.innerHTML=html;
}
var T0_SYM={seed:600519,px:1712.5,nm:'600519 贵州茅台'};
function t0SymTgl(e){
  e.stopPropagation();
  var m=document.getElementById('t0-sym-menu'); if(m)m.classList.toggle('open');
}
function t0SymSet(seed,px,nm,e){
  if(e&&e.stopPropagation)e.stopPropagation();
  T0_SYM={seed:seed,px:px,nm:nm};
  document.getElementById('t0-sym-t').textContent=nm;
  document.querySelectorAll('#t0-sym-menu .acct-mi').forEach(function(mi){mi.classList.toggle('on',mi.textContent===nm);});
  var m=document.getElementById('t0-sym-menu'); if(m)m.classList.remove('open');
  renderT0();
}
document.addEventListener('click',function(e){var s=document.getElementById('t0-sym-sel');var m=document.getElementById('t0-sym-menu');if(s&&m&&!s.contains(e.target))m.classList.remove('open');});
function renderT0(){
  var svg=document.getElementById('t0-svg'); if(!svg)return; svg.innerHTML='';
  var W=1100,H=440,L=10,R=60,T=16,VB=H-10,VT=H-70;
  var pts=genIntraday(T0_SYM.seed,241);
  var f=T0_SYM.px/pts[240]; pts=pts.map(function(v){return v*f;});
  var vwap=[],acc=0; for(var i=0;i<241;i++){acc+=pts[i];vwap.push(acc/(i+1));}
  var lo=Math.min.apply(null,pts.concat(vwap)),hi=Math.max.apply(null,pts.concat(vwap));
  var pad=(hi-lo)*0.15; lo-=pad;hi+=pad;
  var x=function(i){return L+i*(W-L-R)/240;};
  var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(VT-8-T);};
  var g=el('g',{},svg); grid(g,W,L,R,VT-8,T,0);
  el('line',{x1:x(120),x2:x(120),y1:T,y2:VT-8,stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
  var r2=lcg(519),vols=[]; for(var i=0;i<241;i++)vols.push(30+r2()*70);
  var vmax=Math.max.apply(null,vols);
  vols.forEach(function(v,i){var vh=v/vmax*(VB-VT-4);el('rect',{x:x(i),y:VB-vh,width:(W-L-R)/240*0.6,height:vh,fill:pts[i]>=pts[Math.max(0,i-1)]?'#CA3F64':'#25A750',opacity:0.6},g);});
  polyline(g,vwap.map(function(v,i){return[x(i),yf(v)];}),'#FFD54F',1.6);
  polyline(g,pts.map(function(v,i){return[x(i),yf(v)];}),'#EDEFF2',1.4);
  ['09:30','10:30','11:30/13:00','14:00','15:00'].forEach(function(t,k){var xi=[0,60,120,180,240][k];hlabel(g,x(xi)-14,H-44,t,'#59626D',10);});
  /* 做T信号（数据源接口位：query_intraday_buy_sell_points → MOD-SIG-024 盘中 6 买 6 卖 prod；
     当前=FEED_MOCK 演示数据，结构与后端 dict 对齐 + i=分时索引展示适配字段） */
  T0_FEED.signals.forEach(function(s){
    if(s.direction==='buy') hlabel(g,x(s.i)-24,yf(pts[s.i])+30,'▲T买 '+s.confidence+'%','#CA3F64',12);
    else hlabel(g,x(s.i)-24,yf(pts[s.i])-22,'▼T卖 '+s.confidence+'%','#25A750',12);
  });
  var pxTxt=T0_SYM.px>=100?T0_SYM.px.toLocaleString('en-US',{minimumFractionDigits:1,maximumFractionDigits:1}):T0_SYM.px.toFixed(2);
  hlabel(g,W-R+6,yf(pts[240])+4,'现价 '+pxTxt,'#EDEFF2',11);
  /* 交互实测修复：分时图 hover 十字读数（时刻+价+VWAP） */
  bindHover(svg,{W:W,L:L,R:R,H:VT-8,T:T,B:0,n:241,x:x,cw:(W-L-R)/240*0.6,g:g,rd:mkReadout(svg.parentNode),readout:function(i){
    var t;
    if(i<=120){var m=30+i;t=(9+Math.floor(m/60))+':'+String(m%60).padStart(2,'0');}
    else{var m2=i-120;t=(13+Math.floor(m2/60))+':'+String(m2%60).padStart(2,'0');}
    return t+'  价 '+pts[i].toFixed(2)+'  VWAP '+vwap[i].toFixed(2);
  }});
}
function renderSectorContrib(){
  var svg=document.getElementById('sector-contrib'); if(!svg)return; svg.innerHTML='';
  var W=1100,H=260,L=10,R=14,T=30,B=14;
  var pts=genIntraday(880001,241); var f=3087.53/pts[240]; pts=pts.map(function(v){return v*f;});
  var lo=Math.min.apply(null,pts),hi=Math.max.apply(null,pts),pad=(hi-lo)*0.15;lo-=pad;hi+=pad;
  var x=function(i){return L+i*(W-L-R)/240;};
  var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg); grid(g,W,L,R,H,T,B);
  var segs=[[0,30,'半导体+白酒 领涨','#CA3F64'],[30,70,'新能源+地产 拖累','#25A750'],[70,120,'证券+白酒 放量','#CA3F64'],[120,150,'普跌回落','#8a94a6'],[150,240,'半导体+消费电子 强化','#CA3F64']];
  segs.forEach(function(s){
    el('rect',{x:x(s[0]),y:8,width:x(s[1])-x(s[0]),height:H-8-B,fill:s[3],opacity:0.12},g);
    hlabel(g,x(s[0])+6,22,s[2],s[3],10);
  });
  polyline(g,pts.map(function(v,i){return[x(i),yf(v)];}),'#EDEFF2',1.5);
  el('line',{x1:x(120),x2:x(120),y1:8,y2:H-B,stroke:'#2A2F36','stroke-width':0.6,'stroke-dasharray':'4 3'},g);
}
/* ════════════════════════════════════════════════════════════════════════════
   前端 mock 数据层（2026-08-23 AI-K3-GW-CWIRE，反向账 C 类通道接线）
   每条数据源接口位 ↔ 后端查询接口（src/zephyr/frontend/services/dashboard_feeds.py，
   全部包装 prod 引擎、返回结构化 dict）。当前=演示数据（badge 纪律：页内如实标注），
   真实通道落地后按同名结构替换。
   ════════════════════════════════════════════════════════════════════════════ */
/* BFE-01：query_intraday_buy_sell_points → MOD-SIG-024 盘中 6 买 6 卖（production） */
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
/* BFE-30：query_liquidity_status → LiquidityMonitor（MOD-RK-08，Amihud+成交量萎缩） */
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
/* A1/A8 默认曲线初始化（须待 N_BARS/genCandles 就绪后执行） */
drawLine('sd-curve',genCandles(1000).map(function(k){return k.c;}),'var(--accent)',400,160);
drawLine('fc-nav',genCandles(2000).map(function(k){return k.c;}),'var(--up)',400,170);
drawLine('fc-ic',genCandles(3000).map(function(k){return k.c;}),'var(--accent)',400,110);

/* ==================== I-5 功能补齐批脚本（stock/screener/calendar/overview+live/review+news/experiment+position） ==================== */
/* ---- I-5 总览增量（ovx 前缀） ---- */
function ovxGo(id, link){
  var nav = null;
  document.querySelectorAll('.nav-item').forEach(function(n){
    var oc = n.getAttribute('onclick') || '';
    if (oc.indexOf("go('" + id + "'") === 0) nav = n;
  });
  if (document.getElementById('p-' + id) && nav) { go(id, nav); return; }
  if (link) { var t = link.textContent; link.textContent = '目标页未施工（演示）'; setTimeout(function(){ link.textContent = t; }, 1500); }
}
(function ovxInitSparks(){
  var defs = [
    ['ovx-sp-sh',  4101, '#CA3F64'],
    ['ovx-sp-sz',  4202, '#CA3F64'],
    ['ovx-sp-cyb', 4303, '#25A750'],
    ['ovx-sp-kc',  4404, '#CA3F64'],
    ['ovx-sp-spx', 4505, '#CA3F64'],
    ['ovx-sp-ndx', 4606, '#CA3F64'],
    ['ovx-sp-hsi', 4707, '#25A750']
  ];
  defs.forEach(function(d){
    if (!document.getElementById(d[0])) return;
    drawLine(d[0], genCandles(d[1]).map(function(k){ return k.c; }), d[2], 180, 60);
  });
})();
/* ---- L2 资产卡折叠（Owner 2026-08-27） ---- */
function ovxFold(id,btn){
  var el=document.getElementById(id); if(!el)return;
  var open=el.style.display!=='none';
  el.style.display=open?'none':'block';
  btn.textContent=open?'账户明细 ▾':'账户明细 ▴';
}
/* ---- 全球市场排名榜：数据驱动自动排序（涨跌幅降序，待接入垫底不排；涨幅前三↑/跌幅前三↓标注） ---- */
(function ovxRank(){
  var M=[
    {n:'科创综指',c:'000680.SH',px:'986.12',chg:1.48,seed:4404},
    {n:'深证成指',c:'399001.SZ',px:'9,741.20',chg:1.05,seed:4202},
    {n:'比特币 BTC',c:'24/7',px:'85,062',chg:1.24,seed:4801},
    {n:'上证指数',c:'000001.SH',px:'3,087.53',chg:0.72,seed:4101},
    {n:'纳斯达克',c:'NDX · 昨收',px:'18,245.60',chg:0.61,seed:4606},
    {n:'标普500',c:'SPX · 昨收',px:'5,612.34',chg:0.38,seed:4505},
    {n:'创业板指',c:'399006.SZ',px:'1,892.44',chg:-0.31,seed:4303},
    {n:'恒生指数',c:'HSI',px:'17,890.22',chg:-0.42,seed:4707},
    {n:'以太坊 ETH',c:'24/7',px:'3,128.40',chg:-0.83,seed:4902},
    {n:'日经 225',c:'N225',na:1},
    {n:'韩国 KOSPI',c:'KS11',na:1},
    {n:'A股股指期货 IF',c:'IF2509',na:1},
    {n:'美股股指期货 ES',c:'CME · 盘前',na:1},
    {n:'黄金 COMEX',c:'GC',na:1},
    {n:'WTI 原油',c:'CL',na:1}
  ];
  M.sort(function(a,b){return (b.chg===undefined?-999:b.chg)-(a.chg===undefined?-999:a.chg);});
  var chgN=M.filter(function(m){return m.chg!==undefined;}).length;
  var h='<tr><th style="width:20px">#</th><th>市场</th><th style="text-align:right">最新</th><th style="text-align:right">涨跌幅</th><th style="width:104px">近 30 日</th></tr>';
  M.forEach(function(m,i){
    var tag='';
    if(m.chg!==undefined){
      if(i<3) tag=' <span style="color:var(--up);font-size:10px;font-weight:600">↑'+(i+1)+'</span>';
      else if(i>=chgN-3) tag=' <span style="color:var(--down);font-size:10px;font-weight:600">↓'+(chgN-i)+'</span>';
    }
    h+='<tr><td class="dim">'+(i+1)+'</td><td>'+m.n+' <span class="dim" style="font-size:11px">'+m.c+'</span>'+tag+'</td>';
    if(m.na){
      h+='<td style="text-align:right"><span class="badge b-na">待接入</span></td><td style="text-align:right" class="dim">—</td><td></td>';
    }else{
      var up=m.chg>=0;
      h+='<td style="text-align:right">'+m.px+'</td><td style="text-align:right" class="'+(up?'up':'down')+'">'+(up?'+':'')+m.chg.toFixed(2)+'%</td>'
        +'<td><svg class="spark" id="ovx-rk-'+i+'" viewBox="0 0 100 32" preserveAspectRatio="none" style="width:100px;height:32px"></svg></td>';
    }
    h+='</tr>';
  });
  var tb=document.getElementById('ovx-rank'); if(!tb) return;
  tb.innerHTML=h;
  M.forEach(function(m,i){
    if(m.na) return;
    drawLine('ovx-rk-'+i, genCandles(m.seed).map(function(k){return k.c;}), m.chg>=0?'#CA3F64':'#25A750', 100, 32);
  });
})();
/* ---- 交互实测修复：盘中 委托/成交 tabs + 撤单 + 下单面板（ordXxx） ---- */
function ordTab(k,el){
  document.querySelectorAll('#ord-tabs .tab').forEach(function(t){t.classList.remove('on');});
  el.classList.add('on');
  document.getElementById('ord-tab-ord').style.display=k==='ord'?'':'none';
  document.getElementById('ord-tab-fill').style.display=k==='fill'?'':'none';
}
function ordCancel(el,what){
  if(!confirm('human_gated 确认：撤销委托「'+what+'」？\n（演示——真实撤单通道待接入 I-2）'))return;
  el.textContent='已撤(演示)'; el.style.opacity=0.5; el.onclick=null;
}
function ordDirTgl(){
  var d=document.getElementById('ord-dir');
  d.textContent=d.textContent.indexOf('买入')>=0?'卖出 ▾':'买入 ▾';
}
function ordSubmit(){
  var c=document.getElementById('ord-code').value.trim()||'（空）';
  var q=document.getElementById('ord-qty').value.trim()||'0';
  var p=document.getElementById('ord-px').value.trim()||'0';
  var d=document.getElementById('ord-dir').textContent.indexOf('买入')>=0?'买':'卖';
  var fb=document.getElementById('ord-fb');
  if(!confirm('human_gated 二次确认：'+d+' '+c+' ×'+q+' @'+p+'\n提交后进入 Owner 审批队列（演示——真实下单通道未接，券商接入后转真）')){fb.textContent='已取消';return;}
  fb.textContent='已进入审批队列（演示）：'+d+' '+c+' ×'+q+' @'+p+' · 待 Owner 审批';
}
function ordEstop(){
  var fb=document.getElementById('ord-fb');
  if(!confirm('human_gated 确认：紧急停止——撤销全部待审批/挂单？\n（演示——与熔断开关联动，真实通道待接入 I-2）'))return;
  fb.textContent='紧急停止已触发（演示）：待审批 2 笔已冻结，挂单一键全撤';
}
/* ---- I-5 盘中日志流（log 前缀） ---- */
function logFilter(lv, el){

  document.querySelectorAll('#log-chips .tab').forEach(function(c){ c.classList.remove('on'); });
  el.classList.add('on');
  document.querySelectorAll('#log-stream .log-line').forEach(function(l){
    l.style.display = (lv === 'all' || l.getAttribute('data-lv') === lv) ? '' : 'none';
  });
}
/* ==================== I-5 个股档案（p-stock）：stockXxx 前缀 ==================== */
var STOCK_CUR='600519';
var STOCK_D={
  '600519':{
    code:'600519',name:'贵州茅台',industry:'白酒 · 申万食品饮料',listDate:'2001-08-27',
    mcap:'2.15 万亿',floatShares:'12.56 亿股',price:'1,712.50',chg:'+0.86%',chgUp:true,
    indices:['沪深300','上证50','中证A50'],seed:519,
    boundary:{boxLower:'1,688.00',noAdd:'1,745.00',mustExit:'1,662.00',state:'持有区（价在箱体内）',stateCls:'b-pass'},
    holders:[
      [1,'中国贵州茅台酒厂（集团）','国资','54.07','0.00'],
      [2,'香港中央结算（陆股通）','外资','6.91','+0.12'],
      [3,'中央汇金资产管理','国资','0.86','0.00'],
      [4,'中国证券金融股份','国资','0.64','0.00'],
      [5,'易方达蓝筹精选混合','基金','0.58','+0.05'],
      [6,'上证50ETF','基金','0.52','+0.02'],
      [7,'贵州国有资本运营','国资','0.45','0.00'],
      [8,'沪深300ETF','基金','0.41','+0.03'],
      [9,'社保基金一一零组合','社保','0.28','+0.01'],
      [10,'林园投资（私募）','其他','0.22','-0.01']
    ],
    instSum:{fund:'1,286 家 · 6.82%',ssf:'2 家 · 0.41%',qfii:'8 家 · 1.12%'},
    execs:[
      ['董事长','丁雄军','2021-09','—','0'],
      ['总经理','王莉','2023-08','96.3','0'],
      ['财务总监','蒋焰','2021-11','82.5','0'],
      ['董事会秘书','刘刚','2022-04','74.8','0']
    ],
    fin:{
      q:['24Q1','24Q2','24Q3','24Q4','25Q1','25Q2','25Q3','25Q4'],
      rev:[457.8,369.7,396.7,383.9,506.0,389.2,410.5,398.4],
      profit:[240.7,176.3,191.3,193.5,268.5,188.4,201.2,205.6],
      years:['2023','2024','2025 TTM'],
      revY:['1,476.9 亿','1,608.4 亿','1,652.1 亿'],
      npY:['747.3 亿','862.3 亿','886.2 亿'],
      gm:['91.9%','92.1%','92.3%'],
      roe:['34.2%','33.5%','32.8%'],
      debt:['18.1%','17.6%','17.2%'],
      ocf:['665.9 亿','782.4 亿','810.3 亿']
    },
    flow:{
      today:[['主力','+38,420'],['超大单','+21,130'],['大单','+17,290'],['中单','-8,640'],['小单','-29,780']],
      d5:['+86,240','+52,110','+34,130','-21,470','-64,770']
    },
    anns:[
      ['2026-08-08','定期报告','2026 年半年度报告全文'],
      ['2026-07-29','分红','2025 年度末期分红实施公告（10 派 276.24 元）'],
      ['2026-07-15','回购','回购股份进展公告（累计回购 0.08%）'],
      ['2026-06-20','重大事项','2025 年度股东大会决议公告'],
      ['2026-05-30','减持','董监高减持计划终止公告'],
      ['2026-04-25','定期报告','2026 年第一季度报告']
    ],
    ratings:{buy:38,add:9,neutral:3},
    chip:{
      periods:['25Q3','25Q4','26Q1','26Q2'],
      holders:[15.2,14.6,13.9,13.1],
      inst:[1286,1312,1348,1395],
      pledge:'0%（无质押）'
    },
    biz:{
      seg:[['茅台酒',86.2],['系列酒',13.8]],
      peers:[
        ['贵州茅台','24.3','8.6','32.8%','2.15 万亿',1],
        ['五粮液','14.2','3.1','22.5%','5,003 亿',0],
        ['泸州老窖','15.8','4.2','28.6%','2,590 亿',0]
      ],
      div:'2025 年度末期 10 派 276.24 元（2026-07-29 实施，股息率约 1.6%）'
    },
    sector:'白酒'
  },
  '300750':{
    code:'300750',name:'宁德时代',industry:'电池 · 申万电力设备',listDate:'2018-06-11',
    mcap:'1.28 万亿',floatShares:'43.90 亿股',price:'289.40',chg:'-1.24%',chgUp:false,
    indices:['沪深300','创业板指'],seed:750,
    boundary:{boxLower:'278.00',noAdd:'296.50',mustExit:'271.00',state:'回踩区（接近箱底，看承接）',stateCls:'b-warn'},
    holders:[
      [1,'曾毓群','个人','23.32','0.00'],
      [2,'宁波梅山保税港区瑞庭投资','其他','11.21','0.00'],
      [3,'香港中央结算（陆股通）','外资','11.85','+0.34'],
      [4,'黄世霖','个人','10.61','0.00'],
      [5,'宁波联合创新新能源','其他','6.78','0.00'],
      [6,'李平','个人','4.58','0.00'],
      [7,'易方达创业板ETF','基金','1.12','+0.06'],
      [8,'华泰柏瑞沪深300ETF','基金','0.96','+0.04'],
      [9,'社保基金四一三组合','社保','0.52','+0.02'],
      [10,'QFII·摩根士丹利国际','QFII','0.48','-0.03']
    ],
    instSum:{fund:'1,542 家 · 8.35%',ssf:'3 家 · 0.86%',qfii:'11 家 · 1.64%'},
    execs:[
      ['董事长','曾毓群','2011-12','—','1,023,654,000'],
      ['总经理','周佳','2022-08','312.6','1,850,000'],
      ['财务总监','郑舒','2017-06','186.4','120,000'],
      ['董事会秘书','蒋理','2018-04','158.2','86,000']
    ],
    fin:{
      q:['24Q1','24Q2','24Q3','24Q4','25Q1','25Q2','25Q3','25Q4'],
      rev:[797.7,869.0,922.8,1029.6,847.0,902.4,968.8,1082.3],
      profit:[105.1,123.6,131.4,148.0,118.9,139.6,147.2,162.8],
      years:['2023','2024','2025 TTM'],
      revY:['4,009.2 亿','3,620.1 亿','3,800.5 亿'],
      npY:['441.2 亿','507.4 亿','568.5 亿'],
      gm:['22.9%','24.4%','25.1%'],
      roe:['21.6%','22.8%','23.4%'],
      debt:['69.3%','67.8%','66.5%'],
      ocf:['928.3 亿','1,012.6 亿','1,086.4 亿']
    },
    flow:{
      today:[['主力','-56,230'],['超大单','-38,410'],['大单','-17,820'],['中单','+12,350'],['小单','+43,880']],
      d5:['-84,120','-51,360','-32,760','+28,540','+55,580']
    },
    anns:[
      ['2026-08-12','重大事项','H 股上市进展公告（聆讯后资料集刊载）'],
      ['2026-07-26','定期报告','2026 年半年度报告预约披露公告'],
      ['2026-06-18','分红','2025 年度权益分派实施（10 派 45.53 元）'],
      ['2026-05-22','回购','回购注销部分限制性股票公告'],
      ['2026-04-28','定期报告','2026 年第一季度报告'],
      ['2026-03-15','重大事项','换电网络战略合作协议签署公告']
    ],
    ratings:{buy:45,add:7,neutral:2},
    chip:{
      periods:['25Q3','25Q4','26Q1','26Q2'],
      holders:[22.8,23.5,24.1,23.6],
      inst:[1542,1496,1508,1533],
      pledge:'0.2%（比例极低）'
    },
    biz:{
      seg:[['动力电池',68.5],['储能',18.2],['其他',13.3]],
      peers:[
        ['宁德时代','22.5','4.9','23.4%','1.28 万亿',1],
        ['比亚迪','18.6','3.9','17.8%','7,150 亿',0],
        ['亿纬锂能','28.4','3.2','12.6%','1,020 亿',0]
      ],
      div:'2025 年度 10 派 45.53 元（2026-06-18 实施）'
    },
    sector:'锂电池'
  },
  '688981':{
    code:'688981',name:'中芯国际',industry:'半导体制造 · 申万电子',listDate:'2020-07-16',
    mcap:'7,860 亿',floatShares:'79.30 亿股（A+H）',price:'99.20',chg:'+2.35%',chgUp:true,
    indices:['沪深300','科创50'],seed:981,
    boundary:{boxLower:'94.50',noAdd:'103.80',mustExit:'91.00',state:'拉升区（近禁加仓线，禁追）',stateCls:'b-buy'},
    holders:[
      [1,'大唐控股（香港）','国资','11.02','0.00'],
      [2,'鑫芯（香港）投资（大基金）','国资','7.76','0.00'],
      [3,'香港中央结算（陆股通）','外资','4.35','+0.28'],
      [4,'国家集成电路产业基金二期','国资','1.62','0.00'],
      [5,'华夏科创50ETF','基金','1.48','+0.07'],
      [6,'易方达科创50ETF','基金','0.92','+0.05'],
      [7,'GIC Private Limited（QFII）','QFII','0.86','-0.04'],
      [8,'华夏半导体芯片ETF','基金','0.74','+0.03'],
      [9,'社保基金一一八组合','社保','0.51','+0.02'],
      [10,'中金公司（做市）','其他','0.38','0.00']
    ],
    instSum:{fund:'896 家 · 5.94%',ssf:'1 家 · 0.51%',qfii:'6 家 · 1.38%'},
    execs:[
      ['董事长','高永岗','2022-03','—','0'],
      ['联合首席执行官','赵海军','2017-05','—','186,000'],
      ['财务总监','吴俊峰','2021-06','268.4','52,000'],
      ['董事会秘书','郭光莉','2020-08','156.7','28,000']
    ],
    fin:{
      q:['24Q1','24Q2','24Q3','24Q4','25Q1','25Q2','25Q3','25Q4'],
      rev:[71.2,80.3,85.0,91.6,78.5,88.2,93.7,99.4],
      profit:[8.9,10.6,11.2,12.8,9.8,11.5,12.4,13.6],
      years:['2023','2024','2025 TTM'],
      revY:['452.5 亿','578.0 亿','642.6 亿'],
      npY:['48.2 亿','53.5 亿','58.6 亿'],
      gm:['19.8%','21.4%','22.6%'],
      roe:['3.2%','3.6%','3.9%'],
      debt:['35.4%','36.1%','36.8%'],
      ocf:['186.4 亿','224.8 亿','252.3 亿']
    },
    flow:{
      today:[['主力','+72,150'],['超大单','+46,820'],['大单','+25,330'],['中单','-14,260'],['小单','-57,890']],
      d5:['+213,400','+138,600','+74,800','-42,150','-171,250']
    },
    anns:[
      ['2026-08-14','重大事项','成熟制程产能扩建项目公告（月增 4 万片）'],
      ['2026-07-30','定期报告','2026 年半年度业绩快报'],
      ['2026-06-25','回购','H 股回购公告（回购 0.05%）'],
      ['2026-05-18','重大事项','大基金三期增资参股子公司公告'],
      ['2026-04-26','定期报告','2026 年第一季度报告'],
      ['2026-03-28','分红','2025 年度利润分配预案说明（留存投研）']
    ],
    ratings:{buy:28,add:12,neutral:6},
    chip:{
      periods:['25Q3','25Q4','26Q1','26Q2'],
      holders:[38.2,36.5,35.1,33.8],
      inst:[896,910,934,962],
      pledge:'0%（无质押）'
    },
    biz:{
      seg:[['成熟制程',72.4],['先进制程',27.6]],
      peers:[
        ['中芯国际','118.0','5.1','3.9%','7,860 亿',1],
        ['华虹公司','56.2','2.4','4.8%','1,180 亿',0],
        ['晶合集成','48.5','2.1','5.2%','620 亿',0]
      ],
      div:'留存投研不分红（2025 年度利润分配预案说明，2026-03-28 公告）'
    },
    sector:'半导体'
  }
};
function stockD(){return STOCK_D[STOCK_CUR];}
function stockSwitch(code,elm){
  STOCK_CUR=code;
  var ns=document.querySelectorAll('.stock-sel');
  for(var i=0;i<ns.length;i++){ ns[i].classList.toggle('on',ns[i]===elm); }
  stockRenderAll();
}
function navOf(id){   /* F3 顶栏适配：按 onclick 属性匹配导航节点（顶栏二级项无 title 属性）；2026-08-25 第二次补写（首次写入被并发覆写冲掉） */
  var nav=null;
  document.querySelectorAll('.nav-item').forEach(function(n){ var oc=n.getAttribute('onclick')||''; if(oc.indexOf("go('"+id+"'")===0) nav=n; });
  return nav;
}
function stockGoT0(){var n=navOf('t0');if(n)go('t0',n);}
function stockGoSector(){var n=navOf('sector');if(n)go('sector',n);}
function stockHolderBadge(t){
  var m={'国资':'b-buy','外资':'b-warn','基金':'b-pass','社保':'b-buy','QFII':'b-warn','个人':'b-na','其他':'b-na'};
  return '<span class="badge '+(m[t]||'b-na')+'">'+t+'</span>';
}
function stockAnnBadge(t){
  var m={'定期报告':'b-pass','重大事项':'b-warn','减持':'b-fail','回购':'b-buy','分红':'b-buy'};
  return '<span class="badge '+(m[t]||'b-na')+'">'+t+'</span>';
}
function stockRenderHead(){
  var s=stockD();
  var idx=s.indices.map(function(t){return '<span class="badge b-pass" style="margin-right:4px">'+t+'</span>';}).join('');
  document.getElementById('stock-head').innerHTML=
    '<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:10px">'
    +'<span style="font-size:18px;font-weight:700">'+s.name+'</span>'
    +'<span class="dim">'+s.code+'</span>'+idx
    +'<span style="margin-left:auto">最新价 <b style="font-size:20px;font-variant-numeric:tabular-nums" class="'+(s.chgUp?'up':'down')+'">'+s.price+'</b> '
    +'<b class="'+(s.chgUp?'up':'down')+'">'+s.chg+'</b></span></div>'
    +'<div class="stock-kv">'
    +'<div><div class="l">申万行业 <span class="dim">SW Industry</span></div><b>'+s.industry+'</b></div>'
    +'<div><div class="l">上市日期 <span class="dim">List Date</span></div><b>'+s.listDate+'</b></div>'
    +'<div><div class="l">总市值 <span class="dim">Market Cap</span></div><b>'+s.mcap+'</b></div>'
    +'<div><div class="l">流通股本 <span class="dim">Float Shares</span></div><b>'+s.floatShares+'</b></div>'
    +'</div>';
}
function stockRenderK(){
  var s=stockD();
  var svg=document.getElementById('stock-k'); svg.innerHTML='';
  var d=genCandles(s.seed);
  var W=520,H=220,L=10,R=10,T=12,B=18;
  var rg=rangeOf(d);
  var bw=(W-L-R)/d.length;
  var x=function(i){return L+i*bw;};
  var yf=function(v){return T+(rg[1]-v)/(rg[1]-rg[0])*(H-T-B);};
  grid(svg,W,L,R,H,T,B);
  drawCandles(svg,d,x,yf,bw*0.68);
  var pts=[];
  for(var i=0;i<d.length;i++){var m=ma(d,20,i);pts.push(m==null?null:[x(i)+bw*0.34,yf(m)]);}
  polyline(svg,pts,'#FFD54F',1.4);
  hlabel(svg,L,H-4,'120 日 · 黄=MA20 · seed='+s.seed,'#59626D',10);
}
function stockRenderBoundary(){
  var b=stockD().boundary;
  document.getElementById('stock-boundary').innerHTML=
    '<table>'
    +'<tr><th style="width:120px">箱底 <span class="dim">box_lower</span></th><td><b>'+b.boxLower+'</b> <span class="dim">跌破即弱化</span></td></tr>'
    +'<tr><th>禁加仓价 <span class="dim">no_add_price</span></th><td class="warn"><b>'+b.noAdd+'</b> <span class="dim">之上只持不加</span></td></tr>'
    +'<tr><th>必出价 <span class="dim">must_exit</span></th><td class="down"><b>'+b.mustExit+'</b> <span class="dim">跌破无条件离场</span></td></tr>'
    +'<tr><th>当前状态机</th><td><span class="badge '+b.stateCls+'">'+b.state+'</span></td></tr>'
    +'</table>'
    +'<div class="note">明日边界=作战室 L15 裁定的个股级投影，与本页 K 线同图互验；分时买卖点 <span class="stock-link" onclick="stockGoT0()">→ 去做T分析</span></div>';
}
function stockRenderHolders(){
  var s=stockD();
  var h='<tr><th style="width:46px">排名</th><th>股东名称</th><th style="width:64px">性质</th><th style="width:78px">持股比例</th><th style="width:92px">较上期变动</th></tr>';
  s.holders.forEach(function(r){
    var cls=r[4].indexOf('+')===0?'up':(r[4].indexOf('-')===0?'down':'dim');
    h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+stockHolderBadge(r[2])+'</td><td>'+r[3]+'%</td><td class="'+cls+'">'+(r[4]==='0.00'?'—':r[4]+' pct')+'</td></tr>';
  });
  var m=s.instSum;
  h+='<tr><td colspan="5" style="background:var(--panel2)" class="dim">机构持仓汇总：基金 <b>'+m.fund+'</b> ｜ 社保 <b>'+m.ssf+'</b> ｜ QFII <b>'+m.qfii+'</b></td></tr>';
  document.getElementById('stock-holders').innerHTML=h;
}
function stockRenderExecs(){
  var s=stockD();
  var h='<tr><th style="width:90px">职务</th><th>姓名</th><th style="width:90px">任期起始</th><th style="width:90px">年薪（万）</th><th>持股数（股）</th></tr>';
  s.execs.forEach(function(r){
    h+='<tr><td>'+r[0]+'</td><td><b>'+r[1]+'</b></td><td>'+r[2]+'</td><td>'+r[3]+'</td><td>'+r[4]+'</td></tr>';
  });
  document.getElementById('stock-execs').innerHTML=h;
}
function stockRenderFin(){
  var f=stockD().fin;
  var svg=document.getElementById('stock-fin-svg'); svg.innerHTML='';
  var W=520,H=200,L=8,R=8,T=10,B=22,n=f.q.length;
  var maxR=Math.max.apply(null,f.rev),maxP=Math.max.apply(null,f.profit);
  var gw=(W-L-R)/n;
  for(var i=0;i<n;i++){
    var b1=(f.rev[i]/maxR)*(H-T-B)*0.92,b2=(f.profit[i]/maxP)*(H-T-B)*0.92;
    el('rect',{x:(L+i*gw+gw*0.14).toFixed(1),y:(H-B-b1).toFixed(1),width:(gw*0.32).toFixed(1),height:b1.toFixed(1),fill:'#3D8BFF'},svg);
    el('rect',{x:(L+i*gw+gw*0.52).toFixed(1),y:(H-B-b2).toFixed(1),width:(gw*0.32).toFixed(1),height:b2.toFixed(1),fill:'#F0B90B'},svg);
    hlabel(svg,L+i*gw+gw*0.22,H-6,f.q[i],'#59626D',9);
  }
  var rows=[
    ['营业收入 <span class="dim">Revenue</span>',f.revY],
    ['归母净利 <span class="dim">Net Profit</span>',f.npY],
    ['毛利率 <span class="dim">Gross Margin</span>',f.gm],
    ['净资产收益率 <span class="dim">ROE</span>',f.roe],
    ['资产负债率 <span class="dim">Debt Ratio</span>',f.debt],
    ['经营现金流 <span class="dim">OCF</span>',f.ocf]
  ];
  var h='<tr><th>指标</th><th>'+f.years[0]+'</th><th>'+f.years[1]+'</th><th>'+f.years[2]+'</th></tr>';
  rows.forEach(function(r){h+='<tr><td>'+r[0]+'</td><td>'+r[1][0]+'</td><td>'+r[1][1]+'</td><td>'+r[1][2]+'</td></tr>';});
  document.getElementById('stock-fin-table').innerHTML=h;
}
function stockRenderFlow(){
  var s=stockD();
  var h='<tr><th>资金档位</th><th>当日净额（万元）</th><th>近 5 日累计（万元）</th></tr>';
  s.flow.today.forEach(function(r,i){
    var d5=s.flow.d5[i];
    h+='<tr><td>'+r[0]+'</td><td class="'+(r[1].indexOf('+')===0?'up':'down')+'">'+r[1]+'</td><td class="'+(d5.indexOf('+')===0?'up':'down')+'">'+d5+'</td></tr>';
  });
  document.getElementById('stock-flow').innerHTML=h;
}
function stockRenderAnns(){
  var s=stockD();
  var h='<tr><th style="width:88px">日期</th><th style="width:80px">类型</th><th>标题</th></tr>';
  s.anns.forEach(function(r){
    h+='<tr><td>'+r[0]+'</td><td>'+stockAnnBadge(r[1])+'</td><td>'+r[2]+'</td></tr>';
  });
  document.getElementById('stock-anns').innerHTML=h;
}
function stockRenderRatings(){
  var r=stockD().ratings,tot=r.buy+r.add+r.neutral;
  document.getElementById('stock-ratings').innerHTML=
    '<div class="bar-row"><span>买入 <span class="dim">Buy</span></span><div class="bar"><i class="g" style="width:'+(r.buy/tot*100).toFixed(0)+'%"></i></div><span class="up">'+r.buy+' 家</span></div>'
    +'<div class="bar-row"><span>增持 <span class="dim">Overweight</span></span><div class="bar"><i style="width:'+(r.add/tot*100).toFixed(0)+'%"></i></div><span>'+r.add+' 家</span></div>'
    +'<div class="bar-row"><span>中性 <span class="dim">Neutral</span></span><div class="bar"><i class="y" style="width:'+(r.neutral/tot*100).toFixed(0)+'%"></i></div><span class="warn">'+r.neutral+' 家</span></div>'
    +'<div class="note">研报中心待建设（S7），落地后点亮 <span class="badge b-na">待接入</span> 后端落地后点亮（I-2 流程）（负反馈也是结果——系统明说「没有」）</div>';
}
function stockRenderLinks(){
  var s=stockD();
  document.getElementById('stock-links').innerHTML=
    '所属板块：<b>'+s.sector+'</b>　<span class="stock-link" onclick="stockGoSector()">→ 去板块全景（梯队/资金证据链）</span><br>'
    +'做T点位：<span class="stock-link" onclick="stockGoT0()">→ 去做T分析（分时 ▲▼ 信号回验）</span><br>'
    +'<span class="dim">相似标的对比：<span class="badge b-na">待接入</span> 后端落地后点亮（I-2 流程）（负反馈也是结果——系统明说「没有」）</span>';
}
function stockRenderAll(){
  stockRenderHead();stockRenderK();stockRenderBoundary();stockRenderHolders();
  stockRenderExecs();stockRenderFin();stockRenderChip();stockRenderPeer();stockRenderFlow();stockRenderAnns();
  stockRenderRatings();stockRenderLinks();
}
window.stockInit=function(){stockRenderAll();};
/* ==================== I-5 条件选股（scrXxx 前缀） ==================== */
var SCR_FIELDS={
  pe:   {cat:'val',cn:'市盈率',en:'PE',ops:['<','>','介于']},
  pb:   {cat:'val',cn:'市净率',en:'PB',ops:['<','>','介于']},
  ps:   {cat:'val',cn:'市销率',en:'PS',ops:['<','>','介于']},
  div:  {cat:'val',cn:'股息率',en:'DIV',unit:'%',ops:['<','>','介于']},
  revg: {cat:'gro',cn:'营收增速',en:'RevG',unit:'%',ops:['<','>','介于']},
  npg:  {cat:'gro',cn:'净利增速',en:'NPG',unit:'%',ops:['<','>','介于']},
  roe:  {cat:'gro',cn:'净资产收益率',en:'ROE',unit:'%',ops:['<','>','介于']},
  ma20: {cat:'tec',cn:'收盘价 vs MA20',en:'MA20 Pos',ops:['上方','下方'],nov:1},
  ret20:{cat:'tec',cn:'20日涨跌幅',en:'RET20',unit:'%',ops:['<','>','介于']},
  turn: {cat:'tec',cn:'换手率',en:'TURN',unit:'%',ops:['<','>','介于']},
  mfin: {cat:'cap',cn:'主力净流入',en:'MFIN',unit:'万',ops:['<','>','介于']},
  north:{cat:'cap',cn:'北向持股变动',en:'NORTH',unit:'%',ops:['<','>','介于']},
  lg:   {cat:'emo',cn:'涨停基因',en:'LimitGene',unit:'次/60日',ops:['>','介于'],demo:1},
  cons: {cat:'emo',cn:'连板数',en:'ConsL',unit:'板',ops:['>','介于'],demo:1}
};
var SCR_UNI={all:['全A',5420],hs300:['沪深300',300],zz500:['中证500',500],zz1000:['中证1000',1000],watch:['自选股板块',36]};
var SCR_PRESETS=[
  {cn:'低估值高ROE',c:[{f:'pe',op:'<',v1:20,v2:null},{f:'roe',op:'>',v1:15,v2:null}]},
  {cn:'强势突破',c:[{f:'ma20',op:'上方',v1:null,v2:null},{f:'ret20',op:'>',v1:10,v2:null}]},
  {cn:'资金抢筹',c:[{f:'mfin',op:'>',v1:5000,v2:null},{f:'turn',op:'>',v1:3,v2:null}]}
];
var SCR_COLS=[
  {k:'code',cn:'代码',en:'Code',fixed:1},{k:'name',cn:'名称',en:'Name',fixed:1},
  {k:'price',cn:'现价',en:'Price',fixed:1},{k:'chg',cn:'涨跌幅',en:'Chg%',fixed:1},
  {k:'pe',cn:'市盈率',en:'PE',on:1},{k:'pb',cn:'市净率',en:'PB',on:0},
  {k:'div',cn:'股息率',en:'DIV',on:0},{k:'roe',cn:'净资产收益率',en:'ROE',on:1},
  {k:'revg',cn:'营收增速',en:'RevG',on:0},{k:'npg',cn:'净利增速',en:'NPG',on:0},
  {k:'ret20',cn:'20日涨幅',en:'RET20',on:0},{k:'turn',cn:'换手率',en:'TURN',on:0},
  {k:'mfin',cn:'主力净流入',en:'MFIN',on:1},{k:'north',cn:'北向变动',en:'NORTH',on:0},
  {k:'hit',cn:'命中条件数',en:'Hits',fixed:1},{k:'op',cn:'操作',en:'Op',fixed:1}
];
var SCR_STOCKS=[
  {code:'600519.SH',name:'贵州茅台',price:1688.00,chg:0.85,pe:28.5,pb:9.8,ps:15.2,div:1.8,revg:15.2,npg:16.5,roe:33.2,ma20:1,ret20:3.2,turn:0.28,mfin:12500,north:0.42},
  {code:'300750.SZ',name:'宁德时代',price:178.50,chg:2.35,pe:22.8,pb:4.6,ps:2.8,div:0.9,revg:28.5,npg:35.2,roe:21.5,ma20:1,ret20:12.6,turn:3.05,mfin:28600,north:0.85},
  {code:'688981.SH',name:'中芯国际',price:91.30,chg:3.85,pe:65.2,pb:3.2,ps:8.5,div:0,revg:22.0,npg:18.5,roe:8.5,ma20:1,ret20:15.8,turn:3.25,mfin:35200,north:0.15},
  {code:'002594.SZ',name:'比亚迪',price:245.60,chg:-1.25,pe:19.5,pb:3.8,ps:1.2,div:1.2,revg:18.5,npg:22.0,roe:18.2,ma20:-1,ret20:-5.2,turn:1.45,mfin:-8500,north:-0.32},
  {code:'000858.SZ',name:'五粮液',price:128.90,chg:0.52,pe:15.8,pb:3.5,ps:5.8,div:3.2,revg:8.5,npg:10.2,roe:22.5,ma20:-1,ret20:-2.1,turn:0.55,mfin:3200,north:0.08},
  {code:'603259.SH',name:'药明康德',price:68.50,chg:1.85,pe:18.2,pb:2.8,ps:3.2,div:1.5,revg:5.5,npg:8.8,roe:15.8,ma20:1,ret20:6.5,turn:1.25,mfin:5600,north:0.22},
  {code:'002415.SZ',name:'海康威视',price:32.80,chg:0.95,pe:21.5,pb:3.2,ps:2.5,div:2.2,revg:6.8,npg:9.5,roe:16.8,ma20:1,ret20:4.2,turn:0.85,mfin:6800,north:0.12},
  {code:'601012.SH',name:'隆基绿能',price:18.50,chg:-2.15,pe:12.5,pb:1.8,ps:0.9,div:1.8,revg:-15.2,npg:-45.5,roe:5.2,ma20:-1,ret20:-8.5,turn:1.85,mfin:-12500,north:-0.55},
  {code:'600036.SH',name:'招商银行',price:38.50,chg:0.35,pe:6.8,pb:0.95,ps:2.2,div:5.2,revg:2.5,npg:3.8,roe:15.5,ma20:-1,ret20:1.2,turn:0.35,mfin:4500,north:0.18},
  {code:'601318.SH',name:'中国平安',price:52.80,chg:0.65,pe:8.5,pb:0.88,ps:0.9,div:4.8,revg:3.2,npg:12.5,roe:12.8,ma20:1,ret20:5.5,turn:0.65,mfin:8900,north:0.28}
];
var scrConds=[],scrHits=[],scrInPool={},scrInited=false;
function scrEsc(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function scrToast(m){
  var d=document.createElement('div');
  d.className='scr-toast'; d.textContent=m;
  document.body.appendChild(d);
  setTimeout(function(){d.style.opacity='0';d.style.transition='opacity .4s';setTimeout(function(){d.remove();},400);},2200);
}
function scrCatFields(){
  var cat=document.getElementById('scr-cat').value, h='';
  Object.keys(SCR_FIELDS).forEach(function(k){
    var f=SCR_FIELDS[k];
    if(f.cat===cat) h+='<option value="'+k+'">'+f.cn+' '+f.en+'</option>';
  });
  document.getElementById('scr-field').innerHTML=h;
}
function scrAddCond(){
  var k=document.getElementById('scr-field').value;
  if(!k) return;
  scrConds.push({f:k,op:SCR_FIELDS[k].ops[0],v1:null,v2:null});
  scrRenderConds();
}
function scrDelCond(i){ scrConds.splice(i,1); scrRenderConds(); }
function scrOpSwap(i,v){ scrConds[i].op=v; scrRenderConds(); }
function scrVal(i,n,v){ scrConds[i]['v'+n]=v; }
function scrInputs(c,i,f){
  var h='<input class="scr-inp" type="number" value="'+(c.v1==null?'':c.v1)+'" oninput="scrVal('+i+',1,this.value)">';
  if(c.op==='介于') h+='<span class="dim">~</span><input class="scr-inp" type="number" value="'+(c.v2==null?'':c.v2)+'" oninput="scrVal('+i+',2,this.value)">';
  if(f.unit) h+='<span class="dim" style="font-size:11px">'+f.unit+'</span>';
  return h;
}
function scrRenderConds(){
  var box=document.getElementById('scr-conds');
  if(!scrConds.length){
    box.innerHTML='<div class="note" style="margin:2px 0 8px">暂无条件——从上方「添加条件」或点预置方案；空条件执行=样本池全量命中</div>';
    return;
  }
  var h='';
  scrConds.forEach(function(c,i){
    var f=SCR_FIELDS[c.f];
    h+='<div class="scr-cond"><div class="r1"><span>'
      +(i>0?'<span class="dim" style="font-size:10px">AND </span>':'')
      +f.cn+' <span class="dim">'+f.en+'</span>'
      +(f.demo?' <span class="badge b-warn">演示</span>':'')
      +'</span><span class="scr-del" onclick="scrDelCond('+i+')" title="删除条件">×</span></div>'
      +'<div class="r2"><select class="sel scr-op" onchange="scrOpSwap('+i+',this.value)">'
      +f.ops.map(function(o){return '<option'+(o===c.op?' selected':'')+'>'+o+'</option>';}).join('')
      +'</select>'
      +(f.nov?'<span class="dim" style="font-size:11px">无需阈值</span>':scrInputs(c,i,f))
      +'</div></div>';
  });
  box.innerHTML=h;
}
function scrPass(s,c){
  var f=SCR_FIELDS[c.f];
  if(f.demo) return true;
  var v=s[c.f];
  if(f.nov) return c.op===f.ops[0]? v>0 : v<0;
  var a=parseFloat(c.v1), b=parseFloat(c.v2);
  if(c.op==='<') return isNaN(a)||v<a;
  if(c.op==='>') return isNaN(a)||v>a;
  if(c.op==='介于'){
    if(isNaN(a)||isNaN(b)) return true;
    return v>=Math.min(a,b)&&v<=Math.max(a,b);
  }
  return true;
}
function scrRun(){
  if(!scrInited){ window.scrInit(); return; }
  var t0=new Date().getTime(), real=[], demo=[];
  scrConds.forEach(function(c){ (SCR_FIELDS[c.f].demo?demo:real).push(c); });
  scrHits=[];
  SCR_STOCKS.forEach(function(s){
    for(var i=0;i<real.length;i++) if(!scrPass(s,real[i])) return;
    var h=real.length;
    demo.forEach(function(){ if(Math.random()<0.5) h++; });
    scrHits.push({s:s,hit:h});
  });
  var ms=(new Date().getTime()-t0)+Math.round(30+Math.random()*80);
  var un=SCR_UNI[document.getElementById('scr-uni').value];
  var sh='命中 <b style="color:var(--text)">'+scrHits.length+'</b> 只 ｜ 宇宙 '+un[0]
    +' 共 <b style="color:var(--text)">'+un[1]+'</b> 只 <span class="badge b-na">演示样本池 10 只 · universe 注册表 待接入</span>'
    +' ｜ 执行 <b style="color:var(--text)">'+ms+'</b> ms <span class="dim">演示</span>';
  if(demo.length) sh+=' <span class="badge b-warn">含演示条件·命中数随机演示</span>';
  document.getElementById('scr-sum-l').innerHTML=sh;
  scrRenderTable();
}
function scrClear(){ scrConds=[]; scrRenderConds(); scrRun(); }
function scrPct(v,d){ return '<span class="'+(v>=0?'up':'down')+'">'+(v>=0?'+':'')+v.toFixed(d)+'%</span>'; }
function scrMfin(v){
  var t=Math.abs(v)>=10000? (v>=0?'+':'')+(v/10000).toFixed(2)+'亿' : (v>=0?'+':'')+Math.round(v)+'万';
  return '<span class="'+(v>=0?'up':'down')+'">'+t+'</span>';
}
function scrCell(s,k){
  switch(k){
    case 'code':  return s.code;
    case 'name':  return '<b>'+s.name+'</b>';
    case 'price': return s.price.toFixed(2);
    case 'chg':   return scrPct(s.chg,2);
    case 'pe':    return s.pe.toFixed(1);
    case 'pb':    return s.pb.toFixed(2);
    case 'div':   return s.div>0? s.div.toFixed(1)+'%':'—';
    case 'roe':   return s.roe.toFixed(1)+'%';
    case 'revg':  return scrPct(s.revg,1);
    case 'npg':   return scrPct(s.npg,1);
    case 'ret20': return scrPct(s.ret20,1);
    case 'turn':  return s.turn.toFixed(2)+'%';
    case 'mfin':  return scrMfin(s.mfin);
    case 'north': return scrPct(s.north,2);
  }
  return '—';
}
function scrGoStock(code){
  var nav=navOf('stock');
  if(!nav){scrToast('个股档案页未找到');return;}
  var short=code.split('.')[0];
  if(!STOCK_D[short]){scrToast('「'+code+'」档案演示数据未内置（仅 3 只演示标的），全量档案待接入');return;}
  go('stock',nav);
  var sels=document.querySelectorAll('.stock-sel');
  for(var i=0;i<sels.length;i++){
    if(sels[i].textContent.indexOf(short)===0){stockSwitch(short,sels[i]);break;}
  }
}
function scrOpCell(s){
  var a='<span style="color:var(--text);cursor:pointer;text-decoration:underline" onclick="scrGoStock(\''+s.code+'\')" title="去个股档案页">档案</span>';
  if(scrInPool[s.code]) return a+' <span class="badge b-pass">已加入（演示）</span>';
  return a+' <span class="btn" style="padding:2px 10px;font-size:11px" onclick="scrPool(\''+s.code+'\')">入作战池</span>';
}
/* ---- I-8 循环升级 R10：个股档案搜索（stockSrchGo——池内切换/池外待接入负反馈） ---- */
function stockSrchGo(){
  var inp=document.getElementById('stock-q'); if(!inp)return;
  var q=inp.value.trim();
  if(!q)return;
  var hit=null;
  for(var k in STOCK_D){
    var d=STOCK_D[k];
    if(k.indexOf(q)>=0||(d.name&&d.name.indexOf(q)>=0)){hit=k;break;}
  }
  if(hit){ inp.value=''; scrGoStock(hit+'.SH'); return; }
  scrToast('「'+q+'」档案演示数据未内置（仅 3 只演示标的：600519/300750/688981），全量档案待接入（负反馈也是结果——系统明说「没有」）');
}
/* ---- I-8 循环升级 R11：新闻检索（newsFilter/newsFSet——彭博 NSE 同位关键词搜索+双标签筛选） ---- */
var newsFCur='all';
function newsFilter(){
  var q=(document.getElementById('news-q')||{}).value||''; q=q.trim().toLowerCase();
  var rows=document.querySelectorAll('#news-table tr'),shown=0,total=0;
  rows.forEach(function(tr,i){
    if(i===0)return;
    total++;
    var txt=tr.textContent.toLowerCase();
    var okQ=!q||txt.indexOf(q)>=0;
    var okF=newsFCur==='all'||txt.indexOf(newsFCur)>=0;
    tr.style.display=(okQ&&okF)?'':'none';
    if(okQ&&okF)shown++;
  });
  var c=document.getElementById('news-fcount'); if(c)c.textContent=shown+' / '+total+' 条';
}
function newsFSet(f,el){
  document.querySelectorAll('#news-ftabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el)el.classList.add('on'); newsFCur=f; newsFilter();
}
function scrRenderTable(){
  var cols=[];
  SCR_COLS.forEach(function(c){ if(c.fixed||c.on) cols.push(c); });
  var h='<tr>';
  cols.forEach(function(c){ h+='<th>'+c.cn+' <span class="dim" style="font-weight:400">'+c.en+'</span></th>'; });
  h+='</tr>';
  if(!scrHits.length){
    h+='<tr><td colspan="'+cols.length+'" class="dim" style="text-align:center;padding:16px">无命中——放宽条件或更换宇宙后重新执行（空结果也是结果，负反馈不掩饰）</td></tr>';
  }
  var demoN=0;
  scrConds.forEach(function(c){ if(SCR_FIELDS[c.f].demo) demoN++; });
  scrHits.forEach(function(r){
    h+='<tr>';
    cols.forEach(function(c){
      if(c.k==='hit'){
        h+='<td>'+(scrConds.length? '<b>'+r.hit+'</b> / '+scrConds.length+(demoN?' <span class="badge b-warn">演</span>':'') : '—')+'</td>';
      }else if(c.k==='op'){
        h+='<td>'+scrOpCell(r.s)+'</td>';
      }else{
        h+='<td>'+scrCell(r.s,c.k)+'</td>';
      }
    });
    h+='</tr>';
  });
  document.getElementById('scr-table').innerHTML=h;
}
function scrToggleCol(k,on){
  SCR_COLS.forEach(function(c){ if(c.k===k) c.on=on?1:0; });
  scrRenderTable();
}
function scrPool(code){
  scrInPool[code]=1;
  scrRenderTable();
  var nm='';
  SCR_STOCKS.forEach(function(s){ if(s.code===code) nm=s.name; });
  scrToast(nm+' 已加入作战池（演示）——作战室 W1 作战池联动示意');
}
function scrPreset(i){
  var p=SCR_PRESETS[i];
  scrConds=JSON.parse(JSON.stringify(p.c));
  scrRenderConds();
  scrRun();
  scrToast('预置方案「'+p.cn+'」已载入并执行（演示）');
}
function scrPlansGet(){ try{ return JSON.parse(localStorage.getItem('zk-screener-plans')||'{}'); }catch(e){ return {}; } }
function scrRenderPlans(sel){
  sel=sel||'';
  var p=scrPlansGet(), ks=Object.keys(p);
  var h='<option value="">已存方案（'+ks.length+'）载入…</option>';
  ks.forEach(function(k){ h+='<option value="'+scrEsc(k)+'"'+(k===sel?' selected':'')+'>'+scrEsc(k)+'</option>'; });
  document.getElementById('scr-plans').innerHTML=h;
}
function scrSavePlan(){
  var n=prompt('方案名称（保存到本机 localStorage）：');
  if(!n) return;
  var p=scrPlansGet();
  p[n]={u:document.getElementById('scr-uni').value,c:JSON.parse(JSON.stringify(scrConds))};
  try{ localStorage.setItem('zk-screener-plans',JSON.stringify(p)); }catch(e){}
  scrRenderPlans(n);
  scrToast('方案「'+n+'」已保存');
}
function scrLoadPlan(){
  var elm=document.getElementById('scr-plans'), k=elm.value;
  if(!k) return;
  var p=scrPlansGet();
  if(!p[k]) return;
  document.getElementById('scr-uni').value=p[k].u||'all';
  scrConds=JSON.parse(JSON.stringify(p[k].c||[]));
  scrRenderConds();
  scrRun();
  scrToast('方案「'+k+'」已载入并执行');
}
function scrDelPlan(){
  var elm=document.getElementById('scr-plans'), k=elm.value;
  if(!k){ scrToast('请先在已存方案下拉中选择要删除的方案'); return; }
  var p=scrPlansGet();
  delete p[k];
  try{ localStorage.setItem('zk-screener-plans',JSON.stringify(p)); }catch(e){}
  scrRenderPlans();
  scrToast('方案「'+k+'」已删除');
}
window.scrInit=function(){
  if(scrInited) return;
  scrInited=true;
  scrCatFields();
  var h='';
  SCR_COLS.forEach(function(c){
    if(c.fixed) return;
    h+='<label><input type="checkbox"'+(c.on?' checked':'')+' onchange="scrToggleCol(\''+c.k+'\',this.checked)"> '+c.cn+' <span class="dim">'+c.en+'</span></label>';
  });
  document.getElementById('scr-colcfg').innerHTML=h;
  scrRenderPlans();
  scrRenderConds();
  scrRun();
};
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
/* ==================== I-5 盘后复盘：周期切换 + 交易统计（revXxx） ==================== */
var REVIEW_D={
  day:{
    execTitle:'今日执行回看', pnlTitle:'PnL 对账 + 归因',
    exec:[
      ['买 贵州茅台 ×100','<span class="up">✅ 成交 @1712.5</span>','—'],
      ['买 中国平安 ×200','<span class="badge b-warn">未执行</span>','风控拦截：行业集中度超限'],
      ['卖 宁德时代 ×400','<span class="badge b-warn">部分 200</span>','跌停附近流动性不足，剩余挂单价外']
    ],
    pnlL1:'当日已实现盈亏', rl:'+8,412', rlC:'up', df:'0（平）', dfC:'up',
    ur:'+21,308', urC:'up', corp:'今日无',
    alpha:'选股 +1.8% / 行业轮动 +0.9% / 配比 -0.3%',
    tca:'滑点 0.08% · 冲击 0.03% · 佣金 0.05%（优于 VWAP 基准 0.02%）',
    kpi:[['交易次数','14',''],['胜率','64.3%',''],['盈亏比','1.9',''],['平均持仓','3.2 天',''],['最大单笔盈利','+2.1 万','up'],['最大单笔亏损','-0.8 万','down']],
    scene:[['高开高走','5战4胜',80,'g'],['高开平走','3战2胜',67,'g'],['平开高走','4战3胜',75,'g'],['其他','2战0胜',8,'r']],
    sector:[['半导体','4战3胜',75,'g'],['白酒','3战3胜',100,'g'],['AI算力','3战1胜',33,'r'],['新能源','4战2胜',50,'y']]
  },
  week:{
    execTitle:'本周执行回看', pnlTitle:'PnL 对账 + 归因（本周）',
    exec:[
      ['计划委托 32 笔（买 14 / 卖 18）','<span class="up">✅ 成交 28 笔</span>','4 笔未执行：风控拦截 ×2 / 流动性不足 ×2'],
      ['买 贵州茅台 ×100 等买入 14 笔','<span class="up">✅ 成交 13 笔</span>','中国平安风控拦截（行业集中度超限）'],
      ['卖 宁德时代 ×400 等卖出 18 笔','<span class="badge b-warn">成交 15 笔（2 笔部分）</span>','跌停/低流动性场景 3 笔，剩余挂单价外']
    ],
    pnlL1:'本周已实现盈亏', rl:'+31,205', rlC:'up', df:'0（平）', dfC:'up',
    ur:'+18,762', urC:'up', corp:'茅台分红到账，调成本 -1,200',
    alpha:'选股 +3.1% / 行业轮动 +1.4% / 配比 -0.6%',
    tca:'滑点 0.09% · 冲击 0.04% · 佣金 0.05%（与 VWAP 基准持平）',
    kpi:[['交易次数','46',''],['胜率','60.9%',''],['盈亏比','1.7',''],['平均持仓','3.6 天',''],['最大单笔盈利','+3.4 万','up'],['最大单笔亏损','-1.5 万','down']],
    scene:[['高开高走','16战11胜',69,'g'],['高开平走','9战5胜',56,'y'],['平开高走','12战8胜',67,'g'],['其他','9战4胜',44,'r']],
    sector:[['半导体','14战9胜',64,'g'],['白酒','9战7胜',78,'g'],['AI算力','11战5胜',45,'r'],['新能源','12战7胜',58,'y']]
  },
  month:{
    execTitle:'本月执行回看', pnlTitle:'PnL 对账 + 归因（本月）',
    exec:[
      ['计划委托 131 笔（买 58 / 卖 73）','<span class="up">✅ 成交 118 笔</span>','13 笔未执行：风控 ×5 / 流动性 ×6 / 拒单 ×2'],
      ['买入 58 笔','<span class="up">✅ 成交 55 笔</span>','拦截主因：行业集中度 / 单票仓位上限'],
      ['卖出 73 笔','<span class="badge b-warn">成交 63 笔（6 笔部分）</span>','跌停/低流动性场景 8 笔，剩余挂单价外']
    ],
    pnlL1:'本月已实现盈亏', rl:'+96,540', rlC:'up', df:'-320（已查明：分红计税口径）', dfC:'down',
    ur:'+12,430', urC:'up', corp:'2 笔分红到账调成本',
    alpha:'选股 +5.6% / 行业轮动 +2.2% / 配比 -1.1%',
    tca:'滑点 0.10% · 冲击 0.04% · 佣金 0.05%（略劣于 VWAP 基准 0.01%）',
    kpi:[['交易次数','188',''],['胜率','58.5%',''],['盈亏比','1.6',''],['平均持仓','4.1 天',''],['最大单笔盈利','+6.8 万','up'],['最大单笔亏损','-2.9 万','down']],
    scene:[['高开高走','62战38胜',61,'g'],['高开平走','35战19胜',54,'y'],['平开高走','51战31胜',61,'g'],['其他','40战22胜',55,'y']],
    sector:[['半导体','55战33胜',60,'g'],['白酒','34战24胜',71,'g'],['AI算力','48战24胜',50,'y'],['新能源','51战29胜',57,'y']]
  }
};
function revBars(id,rows){
  var box=document.getElementById(id); if(!box) return;
  var h='';
  rows.forEach(function(r){
    h+='<div class="bar-row wide"><span>'+r[0]+' <span class="dim" style="font-size:10px">'+r[1]+'</span></span>'
      +'<div class="bar"><i class="'+r[3]+'" style="width:'+r[2]+'%"></i></div><span>'+r[2]+'%</span></div>';
  });
  box.innerHTML=h;
}
function revRender(p){
  var d=REVIEW_D[p]; if(!d) return;
  var et=document.getElementById('rev-exec-title'); if(et) et.textContent=d.execTitle;
  var pt=document.getElementById('rev-pnl-title'); if(pt) pt.textContent=d.pnlTitle;
  var eb=document.getElementById('rev-exec-body');
  if(eb){
    var h='<tr><th>计划</th><th>实际</th><th>偏差原因</th></tr>';
    d.exec.forEach(function(r){ h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'; });
    eb.innerHTML=h;
  }
  var pb=document.getElementById('rev-pnl-body');
  if(pb){
    pb.innerHTML='<tr><td>'+d.pnlL1+'</td><td class="'+d.rlC+'">'+d.rl+'</td><td>对账差异</td><td class="'+d.dfC+'">'+d.df+'</td></tr>'
      +'<tr><td>未实现盈亏</td><td class="'+d.urC+'">'+d.ur+'</td><td>公司行为调成本</td><td>'+d.corp+'</td></tr>'
      +'<tr><td>Alpha 拆解</td><td colspan="3">'+d.alpha+'</td></tr>'
      +'<tr><td>TCA 执行质量</td><td colspan="3">'+d.tca+'</td></tr>';
  }
  var kb=document.getElementById('rev-kpi');
  if(kb){
    var h2='';
    d.kpi.forEach(function(k){
      h2+='<div class="card metric rev-kpi"><div class="l">'+k[0]+'</div><div class="v'+(k[2]?' '+k[2]:'')+'" style="font-size:18px">'+k[1]+'</div></div>';
    });
    kb.innerHTML=h2;
  }
  revBars('rev-scene',d.scene);
  revBars('rev-sector',d.sector);
}
function revSet(p,el){
  var tabs=document.querySelectorAll('#rev-tabs .tab');
  for(var i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  if(el) el.classList.add('on');
  revRender(p);
}
window.revInit=function(){ revRender('day'); };
/* ==================== I-5 新闻舆情：公司公告（annXxx） ==================== */
var ANN_D=[
  {t:'14:32',ty:'定期报告',code:'300750',nm:'宁德时代',ti:'2026 年半年度报告'},
  {t:'14:10',ty:'重大事项',code:'688981',nm:'中芯国际',ti:'关于签订重大采购合同的公告'},
  {t:'13:48',ty:'分红',code:'600036',nm:'招商银行',ti:'2026 年中期利润分配实施公告'},
  {t:'11:05',ty:'回购',code:'600519',nm:'贵州茅台',ti:'关于回购公司股份进展公告'},
  {t:'10:52',ty:'定期报告',code:'000858',nm:'五粮液',ti:'2026 年半年度报告摘要'},
  {t:'09:58',ty:'减持',code:'002594',nm:'比亚迪',ti:'高管减持计划预披露'},
  {t:'09:31',ty:'重大事项',code:'601012',nm:'隆基绿能',ti:'关于投资建设新产能项目的公告'},
  {t:'08:47',ty:'回购',code:'000333',nm:'美的集团',ti:'回购股份注销完成公告'},
  {t:'08:15',ty:'减持',code:'603259',nm:'药明康德',ti:'股东减持股份结果公告'},
  {t:'07:55',ty:'分红',code:'601318',nm:'中国平安',ti:'2025 年年度权益分派实施公告'}
];
var ANN_BADGE={'定期报告':'b-na','重大事项':'b-warn','减持':'b-sell','回购':'b-buy','分红':'b-pass'};
var annCur='all';
function annRender(){
  var b=document.getElementById('ann-body'); if(!b) return;
  var h='<tr><th>时间</th><th>类型</th><th>代码</th><th>名称</th><th>标题</th><th>链接</th></tr>', n=0;
  ANN_D.forEach(function(a){
    if(annCur!=='all'&&a.ty!==annCur) return;
    n++;
    h+='<tr><td>'+a.t+'</td><td><span class="badge '+ANN_BADGE[a.ty]+'">'+a.ty+'</span></td>'
      +'<td>'+a.code+'</td><td>'+a.nm+'</td><td>'+a.ti+'</td>'
      +'<td><a class="ann-lnk" href="#" onclick="return false">原文</a></td></tr>';
  });
  if(!n) h+='<tr><td colspan="6" class="dim" style="text-align:center">该类型今日无公告</td></tr>';
  b.innerHTML=h;
  var c=document.getElementById('ann-count'); if(c) c.textContent='共 '+n+' 条';
}
function annSet(ty,el){
  var tabs=document.querySelectorAll('#ann-tabs .tab');
  for(var i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  if(el) el.classList.add('on');
  annCur=ty; annRender();
}
window.annInit=function(){ annRender(); };
/* ==================== I-8 政策资金（polXxx：政策流分源 tabs；政策≠新闻独立源） ==================== */
var POL_D=[
  {t:'08-24 14:00',src:'国务院',lv:'国家级',lc:'b-buy',title:'国常会：部署进一步扩大内需新一轮举措',impact:'<span class="badge b-buy">利好</span> 消费/基建链',link:1},
  {t:'08-24 09:20',src:'央行',lv:'部委级',lc:'b-na',title:'开展 3,800 亿 MLF 操作（利率持平）',impact:'<span class="badge b-na">中性偏多</span> 流动性维持·银行',link:1},
  {t:'08-23 17:30',src:'证监会',lv:'部委级',lc:'b-na',title:'程序化交易报告制度落地执行（量化监管常态化）',impact:'<span class="badge b-na">中性</span> 量化/券商',link:1},
  {t:'08-22 16:00',src:'证监会',lv:'部委级',lc:'b-buy',title:'上市公司分红指引修订公开征求意见',impact:'<span class="badge b-buy">利好</span> 红利/央企',link:1},
  {t:'08-22 02:00',src:'海外',lv:'海外·央行',lc:'b-sell',title:'美联储 FOMC 纪要：年内或仅降息一次（放鹰）',impact:'<span class="badge b-sell">利空</span> 预期差·北向/成长',link:1},
  {t:'08-21 10:00',src:'地方政府',lv:'省级',lc:'b-buy',title:'某省 2,000 亿专项债提前下达（基建加速）',impact:'<span class="badge b-buy">利好</span> 基建/区域',link:1},
  {t:'08-20 08:30',src:'地方政府',lv:'市级',lc:'b-na',title:'某市购房补贴加码（人才购房）',impact:'<span class="badge b-buy">弱利好</span> 地产链',link:1},
  {t:'08-15 21:30',src:'海外',lv:'海外·央行',lc:'b-na',title:'美联储维持联邦基金利率 4.25–4.50%（FRED DFF 序列在库口径）',impact:'<span class="badge b-na">中性</span> 符合预期·美债 10Y 4.28%',link:1}
];
var polCur='all';
function polRender(){
  var tb=document.getElementById('pol-body'); if(!tb)return;
  var rows=POL_D.filter(function(r){return polCur==='all'||r.src===polCur;});
  var h='<tr><th>时间</th><th>源</th><th>级别</th><th>标题</th><th>影响解读</th><th>原文链</th></tr>';
  rows.forEach(function(r){
    h+='<tr><td>'+r.t+'</td><td>'+r.src+'</td><td><span class="badge '+r.lc+'">'+r.lv+'</span></td><td>'+r.title+'</td><td>'+r.impact+'</td>'
      +'<td><span class="dim" style="cursor:not-allowed" title="原文链待接入（独立政策源接口 I-2）">🔗 原文</span></td></tr>';
  });
  tb.innerHTML=h;
  var c=document.getElementById('pol-count'); if(c)c.textContent=rows.length+' 条';
}
function polSet(src,el){
  document.querySelectorAll('#pol-tabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el) el.classList.add('on');
  polCur=src; polRender();
}
window.polInit=function(){ polRender(); };
/* ==================== I-8 P2 五件：板块档案下钻 / 美债收益率曲线 / 组合容忍带 ==================== */
var SECARC_D={
 '半导体':{cons:[['中芯国际','12.4%','+10.0%','+8.2 亿'],['韦尔股份','8.1%','+10.0%','+4.6 亿'],['北方华创','7.6%','+9.9%','+3.8 亿'],['中微公司','5.2%','+9.8%','+2.1 亿'],['沪硅产业','4.0%','+9.7%','+1.2 亿'],['兆易创新','3.8%','+4.2%','+0.8 亿'],['卓胜微','3.1%','+3.6%','+0.4 亿'],['长电科技','2.9%','+2.8%','+0.3 亿']],
   flow:[['08-19','+12.4 亿',1,62],['08-20','+8.1 亿',1,41],['08-21','+6.3 亿',1,32],['08-22','+15.8 亿',1,79],['08-25','+38.1 亿',1,100]],
   news:'<span class="badge b-pass">国产化率 40% ×48</span> <span class="badge b-pass">设备招标 ×21</span> <span class="badge b-warn">大基金减持 ×6</span><br>研报密度 48 篇/周（密度上升）；一致预期上修 12 家 / 下调 3 家（analyst_forecast）'},
 '白酒':{cons:[['贵州茅台','22.6%','+3.1%','+5.8 亿'],['五粮液','14.2%','+2.4%','+3.2 亿'],['泸州老窖','9.8%','+1.9%','+1.6 亿'],['山西汾酒','8.4%','+1.2%','+0.9 亿'],['酒鬼酒','5.1%','+10.0%','+0.7 亿'],['舍得酒业','4.2%','+9.9%','+0.5 亿'],['洋河股份','3.9%','+0.8%','+0.2 亿'],['古井贡酒','3.2%','+0.6%','+0.1 亿']],
   flow:[['08-19','+6.2 亿',1,32],['08-20','+9.8 亿',1,49],['08-21','+11.4 亿',1,57],['08-22','+18.6 亿',1,93],['08-25','+42.6 亿',1,100]],
   news:'<span class="badge b-pass">中秋备货 ×36</span> <span class="badge b-pass">券商上调评级 ×18</span> <span class="badge b-warn">批价波动 ×5</span><br>研报密度 32 篇/周（持平）；一致预期上修 5 家 / 下调 2 家'},
 '证券':{cons:[['东方财富','16.8%','+20.0%','+6.4 亿'],['中信证券','12.4%','+4.2%','+2.8 亿'],['华泰证券','9.6%','+3.6%','+1.4 亿'],['东方证券','7.2%','+2.8%','+0.6 亿'],['广发证券','6.8%','+2.1%','+0.4 亿'],['招商证券','6.1%','+1.8%','+0.3 亿'],['国泰君安','5.9%','+1.6%','+0.2 亿'],['海通证券','5.2%','+1.2%','+0.1 亿']],
   flow:[['08-19','-2.4 亿',0,12],['08-20','-1.1 亿',0,6],['08-21','+3.2 亿',1,16],['08-22','+8.8 亿',1,44],['08-25','+21.4 亿',1,100]],
   news:'<span class="badge b-warn">降准预期 ×14</span> <span class="badge b-pass">成交额破万亿 ×22</span> <span class="badge b-na">两融标的调整 ×3</span><br>研报密度 19 篇/周（上升）；一致预期上修 3 家 / 下调 1 家'}
};
function secArcRender(sec){
  var d=SECARC_D[sec]; if(!d)return;
  var h='<tr><th>个股</th><th>权重</th><th>今日涨幅</th><th>主力净流入</th></tr>';
  d.cons.forEach(function(r){h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td class="'+(r[2].charAt(0)==='+'?'up':'down')+'">'+r[2]+'</td><td class="'+(r[3].charAt(0)==='+'?'up':'down')+'">'+r[3]+'</td></tr>';});
  document.getElementById('secarc-cons').innerHTML=h;
  document.getElementById('secarc-flow').innerHTML=d.flow.map(function(r){
    return '<div class="bar-row"><span>'+r[0]+'</span><div class="bar"><i class="'+(r[2]?'g':'r')+'" style="width:'+r[3]+'%"></i></div><span class="'+(r[2]?'up':'down')+'">'+r[1]+'</span></div>';
  }).join('');
  document.getElementById('secarc-news').innerHTML=d.news;
}
function secArcSet(sec,el){
  document.querySelectorAll('#secarc-tabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el) el.classList.add('on');
  secArcRender(sec);
}
/* ---- 美债收益率曲线（当前 vs 一周前） ---- */
function usycRender(){
  var svg=document.getElementById('usyc-svg'); if(!svg)return; svg.innerHTML='';
  var W=520,H=220,L=40,R=20,T=16,B=30;
  var tenors=['2Y','5Y','10Y','30Y'],cur=[3.85,3.92,4.28,4.61],prev=[3.92,3.98,4.22,4.55];
  var lo=3.6,hi=4.8;
  var x=function(i){return L+i*(W-L-R)/3;},yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg); grid(g,W,L,R,H,T,B);
  [3.8,4.0,4.2,4.4,4.6].forEach(function(v){hlabel(svg,4,yf(v)+3,v.toFixed(1)+'%','#666666',9);});
  polyline(g,prev.map(function(v,i){return[x(i),yf(v)];}),'#59626D',1.2,'3 3');
  polyline(g,cur.map(function(v,i){return[x(i),yf(v)];}),'#3D8BFF',1.8);
  cur.forEach(function(v,i){
    el('circle',{cx:x(i),cy:yf(v),r:3,fill:'#3D8BFF'},g);
    hlabel(svg,x(i)-14,yf(v)-8,v.toFixed(2),'#9ec7ee',9);
    hlabel(svg,x(i)-10,H-8,tenors[i],'#999999',10);
  });
  hlabel(svg,L+8,T+12,'短端低于长端=正常化上行（衰退定价消退）','#888888',10);
}
/* ---- 组合政策容忍带（按账号渲染；real 演示，其余待接入负反馈） ---- */
function renderTolBand(key){
  var tb=document.getElementById('tol-band-body'); if(!tb)return;
  if(key&&key!=='real'){
    tb.innerHTML='<tr><td class="dim" colspan="4">'+(key==='sim'?'模拟账户口径（演示）':'分账户口径')+'——容忍带按账号输出后转真（I-2，负反馈）</td></tr>';
    return;
  }
  tb.innerHTML='<tr><th>检查项</th><th>政策基准/上限</th><th>当前</th><th>判定</th></tr>'
    +'<tr><td>单票偏离（贵州茅台）</td><td>目标 10% ±5pp</td><td>13.3%（+3.3pp）</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>单票偏离（宁德时代）</td><td>目标 8% ±5pp</td><td>5.5%（-2.5pp）</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>单票偏离（中芯国际）</td><td>目标 6% ±5pp</td><td>7.2%（+1.2pp）</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>行业集中度（新能源）</td><td>≤25%</td><td>21.4%</td><td><span class="badge b-warn">接近上限</span></td></tr>'
    +'<tr><td>行业集中度（白酒）</td><td>≤25%</td><td>18.3%</td><td><span class="badge b-pass">带内</span></td></tr>'
    +'<tr><td>单票建仓硬顶</td><td>≤8% 总资产（firm 层）</td><td>今日新买最大 6.2%</td><td><span class="badge b-pass">未触顶</span></td></tr>'
    +'<tr><td colspan="4" class="dim">越限告警：0 次/近 5 日；触发后动作=告警+禁止加仓方向委托（联动 9 限额与禁做清单）</td></tr>';
}
/* ==================== I-8 循环升级 R1：盘中实时权益分时 vs 样本外包络（liveEqRender） ==================== */
function liveEqRender(){
  var svg=document.getElementById('live-eq-svg'); if(!svg)return; svg.innerHTML='';
  var W=1100,H=180,L=10,R=14,T=12,B=16,N=241,i;
  var r=lcg(20260825),eq=[],bt=[],mid=[],sig=[];
  var p=0,pm=0;
  for(i=0;i<N;i++){
    pm+=(r()-0.48)*0.06; mid.push(pm);                    /* 回测中枢 */
    sig.push(0.10+i/N*0.12);                              /* 包络 ±1σ 渐宽 */
    p=pm+(r()-0.5)*0.05; eq.push(p);                      /* 实盘权益=中枢+小幅噪声（演示：运行在包络内，偶触带沿） */
    bt.push(pm);
  }
  var lo=1e18,hi=-1e18;
  for(i=0;i<N;i++){lo=Math.min(lo,eq[i],mid[i]-sig[i]);hi=Math.max(hi,eq[i],mid[i]+sig[i]);}
  var pad=(hi-lo)*0.12||1;lo-=pad;hi+=pad;
  var x=function(ii){return L+(ii+0.5)*(W-L-R)/N;},yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg); grid(g,W,L,R,H,T,B);
  var band=[];
  for(i=0;i<N;i++)band.push([x(i),yf(mid[i]-sig[i])]);
  for(i=N-1;i>=0;i--)band.push([x(i),yf(mid[i]+sig[i])]);
  el('polygon',{points:band.map(function(q){return q[0].toFixed(1)+','+q[1].toFixed(1);}).join(' '),fill:'#8A94A6',opacity:0.18},g);
  polyline(g,mid.map(function(v,ii){return[x(ii),yf(v)];}),'#59626D',1,'3 3');
  polyline(g,eq.map(function(v,ii){return[x(ii),yf(v)];}),'#3D8BFF',1.8);
  /* 包络外检测：09:30=0 / 13:00=120 / 15:00=240 */
  var out=0,first=-1;
  for(i=0;i<N;i++){if(Math.abs(eq[i]-mid[i])>sig[i]){out++;if(first<0)first=i;}}
  /* 午休分隔 11:30=120 */
  el('line',{x1:x(120),x2:x(120),y1:T,y2:H-B,stroke:'#2A2F36','stroke-width':0.5,'stroke-dasharray':'2 4'},g);
  hlabel(svg,x(0)+2,H-4,'09:30','#59626D',9); hlabel(svg,x(120)-16,H-4,'11:30/13:00','#59626D',9); hlabel(svg,x(240)-22,H-4,'15:00','#59626D',9);
  document.getElementById('live-eq-note').innerHTML=out===0
    ?'判定：<b class="up">权益运行在回测包络内</b>（偏离 0 分钟）——实盘与回测一致，无结构漂移；包络=回测中枢 ±1σ（QC 纸面交易必须落回测包络哲学，真源=权益/回测双序列 I-2）'
    :'判定：<b style="color:var(--yellow)">包络外 '+out+' 分钟</b>（首次 '+Math.floor(first/60+9)+':'+String(30+first%60).padStart(2,'0')+'）——实盘偏离回测，查执行滑点/信号漂移（QC 包络哲学，真源 I-2）';
}
/* ==================== I-8 循环升级 R7：任务进度下钻/重跑/全量清单（taskXxx） ==================== */
function taskDrill(row,id){
  var b=document.getElementById(id); if(!b)return;
  var open=b.style.display==='none';
  b.style.display=open?'':'none';
  var c=row.cells[0]; c.textContent=c.textContent.replace(open?'▸':'▾',open?'▾':'▸');
}
function taskRerun(name,el){
  if(el.__busy)return;
  if(!confirm('human_gated 确认：重跑任务「'+name+'」？\n（演示——真实执行通道待接入 I-2；操作将留痕）'))return;
  el.__busy=1; var old=el.textContent; el.textContent='排队中…';
  setTimeout(function(){el.textContent='已触发(演示)';setTimeout(function(){el.textContent=old;el.__busy=0;},1500);},800);
}
var TASK_LIST=[
  ['kline_daily_incremental','数据采集','08-25 06:31','4m12s','g','成功'],
  ['tick_data_record','数据采集','实时常驻','—','g','运行中'],
  ['tick 回补 08-14','数据采集','08-19 06:40','12m','r','失败'],
  ['macro_fred_incremental','数据采集','08-24 21:05','1m48s','g','成功'],
  ['qweather_now_incremental','数据采集','08-25 08:00','22s','g','成功'],
  ['factor_alpha_pipeline','因子计算','08-25 06:45','18m','g','成功'],
  ['ic_ir_daily','因子计算','08-25 07:02','6m33s','g','成功'],
  ['ic_decay_watch','因子计算','08-22 07:10','3m05s','y','久未运行'],
  ['backfill_checker_daily','治理','08-25 06:35','9m','g','成功'],
  ['architecture_fitness','治理','08-25 06:50','2m40s','g','成功'],
  ['backup_daily_trigger','运维','08-25 02:00','14m','g','成功'],
  ['ch_health_probe','运维','常驻 5min','8s','g','成功']
];
var taskStage='all';
function taskListRender(){
  var q=(document.getElementById('task-q')||{}).value||''; q=q.trim().toLowerCase();
  var rows=TASK_LIST.filter(function(r){
    return (taskStage==='all'||r[1]===taskStage)&&(!q||r[0].toLowerCase().indexOf(q)>=0);
  });
  var h='<tr><th>任务</th><th>阶段</th><th>上次运行</th><th>耗时</th><th>状态</th></tr>';
  rows.forEach(function(r){
    var lamp=r[4]==='g'?'<span class="dot g"></span>':(r[4]==='y'?'<span class="dot y"></span>':'<span class="dot r"></span>');
    h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td>'+r[3]+'</td><td>'+lamp+' '+r[5]+'</td></tr>';
  });
  if(!rows.length) h+='<tr><td colspan="5" class="dim">无匹配任务</td></tr>';
  document.getElementById('task-list-body').innerHTML=h;
  document.getElementById('task-list-count').textContent=rows.length+' / 演示 12 行（全量 167 I-2）';
}
function taskStageSet(st,el){
  document.querySelectorAll('#task-stage-tabs .tab').forEach(function(t){t.classList.remove('on');});
  if(el)el.classList.add('on'); taskStage=st; taskListRender();
}
/* ==================== I-8 S1 全局搜索先行版（srchXxx：静态索引表——页面/功能/指标/库条目；AI 问答属后端待接入） ==================== */
var SRCH_IDX=[
 {ty:'页面',t:'首页',p:'home',k:'首页 落地 默认 待建设'},
 {ty:'页面',t:'全景总览',p:'overview',k:'总览 决策 资金 持仓 简报 告警 天气 日历'},
 {ty:'页面',t:'项目地图',p:'projmap',k:'项目地图 模块 依赖 全景 depgraph 域 树'},
 {ty:'页面',t:'作战指挥',p:'warroom',k:'作战室 预案 情景矩阵 观察哨 辩论 风险预算 纪律'},
 {ty:'页面',t:'盘中实时',p:'live',k:'盘中 四指数 regime 决策链 风控 下单 日志 逐笔'},
 {ty:'页面',t:'板块全景',p:'sector',k:'板块 主线 梯队 贡献度 逆势榜 板块档案'},
 {ty:'页面',t:'市场情绪',p:'sentiment',k:'情绪 温度计 涨跌停 连板 两融 宽度 异动'},
 {ty:'页面',t:'新闻舆情',p:'news',k:'新闻 双标签 情绪 公告 热点'},
 {ty:'页面',t:'政策资金',p:'policy',k:'政策 国务院 央行 证监会 地方政府 美联储 国家队 社保 汇金 ETF 地缘'},
 {ty:'页面',t:'外盘速览',p:'overseas',k:'外盘 美股 港股 A50 美元 美债 收益率曲线'},
 {ty:'页面',t:'做T分析',p:'t0',k:'做T 分时 点位 回验 T买 T卖'},
 {ty:'页面',t:'盘后复盘',p:'review',k:'复盘 执行 PnL 归因 打板 龙虎榜 战报 因子'},
 {ty:'页面',t:'持仓监控',p:'position',k:'持仓 账号 盈亏日历 收益分析 阶段盈亏 容忍带 相关性'},
 {ty:'页面',t:'回测结果',p:'backtest',k:'回测 绩效 净值 回撤 交易统计 信号'},
 {ty:'页面',t:'实验历史',p:'experiment',k:'实验 runs 门控 对比 元数据'},
 {ty:'页面',t:'策略档案',p:'strategy',k:'策略 看板 框架状态 权重 regime'},
 {ty:'页面',t:'因子档案',p:'factor',k:'因子 IC IR 分组 衰减 聚类'},
 {ty:'页面',t:'个股档案',p:'stock',k:'个股 F9 股东 财务 筹码 主营 同行'},
 {ty:'页面',t:'条件选股',p:'screener',k:'选股 筛选 条件 方案 宇宙'},
 {ty:'页面',t:'事件日历',p:'calendar',k:'日历 解禁 新股 财报 宏观 倒计时'},
 {ty:'页面',t:'注册表库',p:'reglib',k:'注册表 18 库 条目 factor strategy'},
 {ty:'页面',t:'研评级',p:'rating',k:'研报 评级 目标价 金股 上调 下调'},
 {ty:'页面',t:'数据源监管',p:'datasrc',k:'数据源 SLA 熔断 测速 告警 provider'},
 {ty:'页面',t:'模型页',p:'models',k:'模型 注册 训练 漂移 影子部署'},
 {ty:'页面',t:'AI 对话',p:'aichat',k:'AI 对话 聊天 指挥 qwen ollama 本地大模型 助手'},
 {ty:'页面',t:'AI 任务队列',p:'aitask',k:'AI 任务 队列 agent 智能体 研究助手 审计'},
 {ty:'页面',t:'技术分析',p:'index',k:'技术分析 K线 指标 形态 叠加 时段 多周期'},
 {ty:'页面',t:'宏观分析',p:'macro',k:'宏观 流动性 周期 天气 FRED'},
 {ty:'页面',t:'产业地图',p:'chainmap',k:'产业链 图谱 上下游'},
 {ty:'页面',t:'任务进度',p:'task',k:'任务 进度 失败 调度'},
 {ty:'页面',t:'适应评估',p:'fitness',k:'fitness 适应 度量 PASS FAIL'},
 {ty:'页面',t:'治理分析',p:'govana',k:'治理 门禁 OLAP'},
 {ty:'页面',t:'模块总账',p:'modledger',k:'模块 总账 域 状态 最近使用'},
 {ty:'页面',t:'系统状态',p:'sysstatus',k:'系统 数据管线 券商 熔断 备份'},
 {ty:'页面',t:'架构全景',p:'pano',k:'架构 全景 域 iframe'},
 {ty:'功能',t:'3×3 情景矩阵',p:'warroom',k:'情景 矩阵 方案 点位 失效',a:'W2'},
 {ty:'功能',t:'多空辩论台+历史辩论',p:'warroom',k:'辩论 多头 空头 风控 veto 历史',a:'W4'},
 {ty:'功能',t:'打板复盘（晋级率/收益）',p:'review',k:'打板 晋级率 炸板率 封板 连板',a:'打板复盘'},
 {ty:'功能',t:'因子级归因（Brinson+因子暴露）',p:'review',k:'归因 Brinson 因子暴露 选股 行业',a:'因子级归因'},
 {ty:'功能',t:'盈亏日历',p:'position',k:'盈亏 日历 日收益 月收益',a:'盈亏日历'},
 {ty:'功能',t:'阶段盈亏表',p:'position',k:'阶段盈亏 本周 本月 近三月 上证指数',a:'阶段盈亏'},
 {ty:'功能',t:'收益分析（多账户曲线）',p:'position',k:'收益分析 跑赢指数 收益率 盈亏金额 总资产',a:'收益分析'},
 {ty:'功能',t:'组合政策容忍带',p:'position',k:'容忍带 偏离 集中度 越限 N3',a:'组合政策容忍带'},
 {ty:'功能',t:'板块档案下钻',p:'sector',k:'板块档案 成分股 资金流历史 舆情',a:'板块档案下钻'},
 {ty:'功能',t:'政策流（分源）',p:'policy',k:'政策流 国务院 央行 证监会 美联储',a:'政策流'},
 {ty:'功能',t:'国家队持仓变动',p:'policy',k:'国家队 社保 汇金 增持 减持',a:'国家队持仓变动'},
 {ty:'功能',t:'美债利率深区',p:'overseas',k:'美债 收益率曲线 利差 TIPS 美元指数',a:'美债利率深区'},
 {ty:'功能',t:'两融情绪',p:'sentiment',k:'两融 融资 融券 余额',a:'两融'},
 {ty:'功能',t:'龙虎榜席位',p:'review',k:'龙虎榜 席位 谁在买',a:'龙虎榜'},
 {ty:'功能',t:'新建回测配置条',p:'backtest',k:'新建回测 发起 配置',a:'新建回测'},
 {ty:'功能',t:'框架状态卡',p:'strategy',k:'框架 状态 regime 权重 切换',a:'当前框架状态'}
];
/* 指标/形态条目=IND_CAT 程序化生成；注册表条目=REGLIB_D 程序化生成（单一事实源） */
IND_CAT.forEach(function(gr){gr.items.forEach(function(it){
  SRCH_IDX.push({ty:'指标',t:it.n,p:'index',k:it.k+' '+gr.g+(it.ok?' 已接入':' 待接入')});
});});
var srchHot=-1;
function srchFilter(){
  var inp=document.getElementById('srch-inp'),drop=document.getElementById('srch-drop');
  var q=inp.value.trim().toLowerCase(); srchHot=-1;
  if(!q){drop.classList.remove('open');drop.innerHTML='';return;}
  var hits=SRCH_IDX.filter(function(e){return (e.t+' '+e.k).toLowerCase().indexOf(q)>=0;}).slice(0,14);
  var h='';
  hits.forEach(function(e,i){
    h+='<div class="srch-it" data-i="'+i+'" onclick="srchGo(+'+i+')"><span class="ty">'+e.ty+'</span><span class="tt">'+e.t+'</span><span class="kw">'+e.k.split(' ').slice(0,3).join(' ')+'</span></div>';
  });
  if(!hits.length) h='<div class="srch-it dis"><span class="tt">无匹配条目</span><span class="kw">试试"板块/指标名/库名"</span></div>';
  h+='<div class="srch-it dis" title="自然语言问功能/问数据——LLM 网关已在治理域 prod，交易域实例化走 CAND"><span class="ty">AI</span><span class="tt">AI 问答（"'+inp.value.trim()+'"）</span><span class="kw">待接入 CAND</span></div>';
  drop.innerHTML=h; drop.classList.add('open');
  window.__srchHits=hits;
}
function srchGo(i){
  var e=(window.__srchHits||[])[i]; if(!e)return;
  var drop=document.getElementById('srch-drop'); drop.classList.remove('open');
  document.getElementById('srch-inp').value='';
  var nav=document.querySelector('.nav-item[onclick^="go(\''+e.p+'\'"]');
  if(nav) nav.click();
  if(e.reg&&typeof regSel==='function'){ setTimeout(function(){regSel(e.reg);},80); }
  if(e.a){ setTimeout(function(){
    var hs=document.querySelectorAll('#p-'+e.p+' h3, #p-'+e.p+' summary, #p-'+e.p+' .sec-title');
    for(var j=0;j<hs.length;j++){ if(hs[j].textContent.indexOf(e.a)>=0){ hs[j].scrollIntoView({behavior:'smooth',block:'center'}); break; } }
  },120); }
}
function srchLate(){   /* REGLIB_D 定义在脚本后段——库条目生成与事件绑定延迟调用（脚本尾 srchLate()） */
  Object.keys(REGLIB_D).forEach(function(rk){
    var rd=REGLIB_D[rk]; SRCH_IDX.push({ty:'库',t:rd.cn+'（'+rd.en+'）',p:'reglib',k:rd.en+' 注册表 '+rd.cn,reg:rk});
  });
  var inp=document.getElementById('srch-inp'); if(!inp)return;
  inp.addEventListener('input',srchFilter);
  inp.addEventListener('keydown',function(e){
    var drop=document.getElementById('srch-drop');
    if(e.key==='Enter'){
      e.preventDefault();
      if(srchHot>=0){var its=drop.querySelectorAll('.srch-it:not(.dis)'); if(its[srchHot]){its[srchHot].click(); return;}}
      if((window.__srchHits||[]).length) srchGo(0);
    }
    else if(e.key==='Escape'){ drop.classList.remove('open'); inp.blur(); }
    else if(e.key==='ArrowDown'||e.key==='ArrowUp'){
      e.preventDefault();
      var items=drop.querySelectorAll('.srch-it:not(.dis)'); if(!items.length)return;
      srchHot+=e.key==='ArrowDown'?1:-1;
      if(srchHot<0)srchHot=items.length-1; if(srchHot>=items.length)srchHot=0;
      items.forEach(function(it,j){it.classList.toggle('hot',j===srchHot);});
    }
  });
  document.addEventListener('click',function(e){
    var box=document.querySelector('.side-srch');
    if(box&&!box.contains(e.target)){var d=document.getElementById('srch-drop'); if(d)d.classList.remove('open');}
  });
}
/* ==================== I-5 experiment+position：阶段门控 / 盈亏归因 ==================== */
window.expInit=function(){
  if(window.__expInited)return; window.__expInited=1;
  if(window.expNames&&expNames.length<5){
    expNames.push('c1_mock_20260815_sector_v2','c1_mock_20260814_defensive');
  }
  expNavRender();
};
var POS_ATTR={
  stocks:[['中芯国际','+1.82 万',1.82,100],['贵州茅台','+1.05 万',1.05,58],['中微公司','+0.46 万',0.46,25],
          ['宁德时代','-0.64 万',-0.64,35],['隆基绿能','-0.38 万',-0.38,21]],
  sector:[['白酒','+2.31 万',2.31,100],['半导体','+1.12 万',1.12,48],['新能源','-0.88 万',-0.88,38]],
  factor:[['动量','+1.65 万',1.65,100],['质量','+1.20 万',1.20,73],['残差','+1.12 万',1.12,68],['反转','-0.42 万',-0.42,25]],
  total:'合计 +4.55 万 = 当日持仓盈亏（对账闭合）'
};
function posBarRow(label,amt,val,w){
  var cls=val>=0?'g':'r', tc=val>=0?'up':'down';
  return '<div class="bar-row pos-bar-row"><span>'+label+'</span>'
    +'<div class="bar"><i class="'+cls+'" style="width:'+w+'%"></i></div>'
    +'<span class="'+tc+'">'+amt+'</span></div>';
}
function posRenderAttr(){
  var s=document.getElementById('pos-attr-stocks'); if(!s)return;
  s.innerHTML=POS_ATTR.stocks.map(function(r){return posBarRow(r[0],r[1],r[2],r[3]);}).join('');
  document.getElementById('pos-attr-sector').innerHTML=POS_ATTR.sector.map(function(r){return posBarRow(r[0],r[1],r[2],r[3]);}).join('');
  document.getElementById('pos-attr-factor').innerHTML=POS_ATTR.factor.map(function(r){return posBarRow(r[0],r[1],r[2],r[3]);}).join('');
  document.getElementById('pos-attr-total').textContent=POS_ATTR.total;
}
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
/* ==================== I-8 收益分析区（perfXxx：多账户收益曲线对比，投资账本「收益汇总」同位） ==================== */
var PERF_SERIES=[
  {k:'sum', n:'汇总', c:'#CA3F64', base:1720000},
  {k:'real',n:'实盘账户 1', c:'#9AA3B2', base:965000},
  {k:'real2',n:'实盘账户 2', c:'#6E7889', base:452000},
  {k:'sim', n:'miniQMT 模拟', c:'#AB47BC', base:321500},
  {k:'sh',  n:'上证指数', c:'#3D8BFF', base:0}
];
var PERF_PERIOD={
  m1:{label:'本月区间（26.08.01–26.08.25）',seed:11,n:17,end:{sum:-0.08,real:-0.21,real2:-0.06,sim:0.26,sh:-1.20}},
  m3:{label:'近三月区间（26.05.26–26.08.25）',seed:22,n:63,end:{sum:-1.86,real:-2.57,real2:-4.65,sim:2.41,sh:3.78}},
  y1:{label:'今年区间（26.01.01–26.08.25）',seed:33,n:160,end:{sum:2.42,real:1.86,real2:-3.12,sim:6.85,sh:4.12}},
  all:{label:'全部区间（24.03 建仓–26.08.25）',seed:44,n:250,end:{sum:8.65,real:9.42,real2:-1.86,sim:12.30,sh:11.85}}
};
var perfPer='m1',perfMode='pct',perfHide={},perfData=null;
function perfGenSeries(key,n,seed,endPct){   /* 确定性随机游走，末端锚定区间收益率 */
  if(key==='sum'&&perfPer==='m1'){   /* 本月汇总=盈亏日历序列对账闭合 */
    var out=[],acc=0;
    for(var j=0;j<PNLCAL_D.length;j++){acc+=PNLCAL_D[j][1];out.push(acc/PNLCAL_BASE*100);}
    return out;
  }
  var r=lcg(seed*7919+key.length*131+key.charCodeAt(0)),rets=[],i;
  for(i=0;i<n;i++) rets.push((r()-0.5)*1.6);
  var cum=1; rets.forEach(function(v){cum*=1+v/100;});
  var adj=Math.pow((1+endPct/100)/cum,1/n),out2=[],f=1;
  for(i=0;i<n;i++){f*=(1+rets[i]/100)*adj;out2.push((f-1)*100);}
  out2[n-1]=endPct;
  return out2;
}
function perfBuild(){
  var P=PERF_PERIOD[perfPer],d={n:P.n,series:{},dates:[]};
  PERF_SERIES.forEach(function(s){ d.series[s.k]=perfGenSeries(s.k,P.n,P.seed,P.end[s.k]); });
  var dt=new Date(2026,7,25),cnt=P.n;
  while(cnt>0){ if(dt.getDay()!==0&&dt.getDay()!==6){ d.dates.unshift(fmtD(dt)); cnt--; } dt.setDate(dt.getDate()-1); }
  perfData=d;
}
function perfSeriesOf(k){ for(var i=0;i<PERF_SERIES.length;i++) if(PERF_SERIES[i].k===k) return PERF_SERIES[i]; return null; }
function perfVal(k,i){
  var pct=perfData.series[k][i],s=perfSeriesOf(k);
  if(perfMode==='pct') return pct;
  if(perfMode==='amt') return pct/100*s.base;
  return (s.base+pct/100*s.base)/10000;
}
function perfFmt(k,i){
  var v=perfVal(k,i);
  if(perfMode==='pct') return (v>=0?'+':'')+v.toFixed(2)+'%';
  if(perfMode==='amt') return (v>=0?'+':'-')+Math.abs(Math.round(v)).toLocaleString('en-US');
  return v.toFixed(1)+' 万';
}
function perfRender(){
  perfBuild();
  var svg=document.getElementById('perf-svg'); if(!svg)return; svg.innerHTML='';
  var W=1100,H=320,L=10,R=14,T=14,B=18,n=perfData.n,i;
  var vis=PERF_SERIES.filter(function(s){return !perfHide[s.k]&&!(perfMode!=='pct'&&s.k==='sh');});
  if(!vis.length) vis=[PERF_SERIES[0]];
  var all=[]; vis.forEach(function(s){for(i=0;i<n;i++)all.push(perfVal(s.k,i));});
  var lo=Math.min.apply(null,all),hi=Math.max.apply(null,all),pad=(hi-lo)*0.08||1; lo-=pad; hi+=pad;
  var x=function(ii){return L+(ii+0.5)*(W-L-R)/n;};
  var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-B);};
  var g=el('g',{},svg); grid(g,W,L,R,H,T,B);
  if(lo<0&&hi>0) el('line',{x1:L,x2:W-R,y1:yf(0),y2:yf(0),stroke:'#2A2F36','stroke-width':0.6},g);
  vis.forEach(function(s){
    var pts=[]; for(i=0;i<n;i++) pts.push([x(i),yf(perfVal(s.k,i))]);
    polyline(g,pts,s.c,s.k==='sum'?2:1.2);
  });
  bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:B,n:n,x:x,cw:0,g:g,rd:mkReadout(svg.parentNode),readout:function(ii){
    var t=perfData.dates[ii];
    vis.forEach(function(s){ t+='  '+s.n+' '+perfFmt(s.k,ii); });
    return t;
  }});
  var P=PERF_PERIOD[perfPer],endSum=P.end.sum,endSh=P.end.sh,beat=endSum-endSh;
  var amtSum=(perfPer==='m1')?-1451:Math.round(endSum/100*1720000);
  document.getElementById('perf-head').innerHTML=P.label+'：区间盈亏 <b class="'+(amtSum>=0?'up':'down')+'">'+(amtSum>=0?'+':'')+amtSum.toLocaleString('en-US')+'（'+(endSum>=0?'+':'')+endSum.toFixed(2)+'%）</b> ｜ 同期上证 <span class="'+(endSh>=0?'up':'down')+'">'+(endSh>=0?'+':'')+endSh.toFixed(2)+'%</span> ｜ 跑赢指数 <b class="'+(beat>=0?'up':'down')+'">'+(beat>=0?'+':'')+beat.toFixed(2)+'%</b>';
  document.getElementById('perf-legend').innerHTML=PERF_SERIES.map(function(s){
    var off=perfHide[s.k]||(perfMode!=='pct'&&s.k==='sh');
    return '<span style="color:'+s.c+';cursor:pointer;opacity:'+(off?0.35:1)+'" onclick="perfToggle(\''+s.k+'\')">■ '+s.n+(s.k==='sh'&&perfMode!=='pct'?'（仅收益率口径）':'')+'</span>';
  }).join('');
}
function perfToggle(k){perfHide[k]=!perfHide[k];perfRender();}
function perfTabOn(id,el){document.querySelectorAll('#'+id+' .tab').forEach(function(t){t.classList.remove('on');});el.classList.add('on');}
function perfSetPeriod(p,el){perfPer=p;perfTabOn('perf-period-tabs',el);perfRender();}
function perfSetMode(m,el){perfMode=m;perfTabOn('perf-mode-tabs',el);perfRender();}
window.posInit=function(){
  if(window.__posInited)return; window.__posInited=1;
  posRenderAttr();
  acctRender();
  perfRender();
};
/* I-5/I-8 预渲染（幂等）：隐藏页容器提前填充，进入时 go() 钩子再次触发亦无碍 */
window.revInit(); window.annInit(); window.polInit(); window.expInit(); window.posInit();
secArcRender('半导体'); renderTolBand('real'); liveEqRender(); taskListRender(); fitTrendRender();
/* 交互实测修复：适应评估近 30 次趋势 30 根（确定性序列，末 3 根=当前 FAIL 态） */
function fitTrendRender(){
  var box=document.getElementById('fit-trend'); if(!box)return;
  var r=lcg(20260819),h='';
  for(var i=0;i<30;i++){
    var fail=i>=27?true:(r()<0.18);
    var pc=fail?55+Math.floor(r()*15):62+Math.floor(r()*26);
    h+='<div style="width:12px;height:'+pc+'%;background:'+(fail?'var(--down)':'var(--up)')+'" title="近 30 次评估 · 第 '+(i+1)+' 次：'+(fail?'有 FAIL':'全过')+'（'+pc+'%）"></div>';
  }
  box.innerHTML=h;
}

/* ==================== I-5b 市场情绪·两融（sentXxx） ==================== */
var SENT_MARGIN_BAL=[14520,14546,14531,14558,14572,14560,14589,14615,14602,14631,14648,14633,14657,14682,14670,14695,14712,14738,14758,14820];
function sentRenderMargin(){
  var svg=document.getElementById('sent-margin-svg'); if(!svg) return; svg.innerHTML='';
  var W=520,H=170,L=8,R=8,T=10,B=18,n=SENT_MARGIN_BAL.length;
  var lo=Math.min.apply(null,SENT_MARGIN_BAL),hi=Math.max.apply(null,SENT_MARGIN_BAL);
  var pad=(hi-lo)*0.15; lo-=pad; hi+=pad;
  var bw=(W-L-R)/n;
  grid(svg,W,L,R,H,T,B);
  for(var i=0;i<n;i++){
    var chg=i===0?18:SENT_MARGIN_BAL[i]-SENT_MARGIN_BAL[i-1];
    var bh=(SENT_MARGIN_BAL[i]-lo)/(hi-lo)*(H-T-B);
    el('rect',{x:(L+i*bw+bw*0.18).toFixed(1),y:(H-B-bh).toFixed(1),width:(bw*0.64).toFixed(1),height:bh.toFixed(1),fill:chg>=0?'#CA3F64':'#25A750'},svg);
  }
  hlabel(svg,L,H-4,'近 20 日 · 末值 14,820 亿（较昨 +62 亿 · 连续 3 日净流入）','#59626D',9);
}
window.sentInit=function(){sentRenderMargin();};
(function sentInitMargin(){ sentRenderMargin(); })();
/* ---- I-8 循环升级 R3：情绪温度/市场宽度 20 日时序（sentRenderTrend） ---- */
function sentRenderTrend(){
  var svg=document.getElementById('sent-temp-svg'); if(svg){
    svg.innerHTML='';
    var W=520,H=170,L=8,R=8,T=10,B=18,N=20,i;
    var r=lcg(620825),tmp=[],p=48;
    for(i=0;i<N;i++){p+=(r()-0.44)*9;p=Math.max(18,Math.min(84,p));tmp.push(p);}
    tmp[N-1]=62;
    var yf=function(v){return T+(1-v/100)*(H-T-B);},xf=function(ii){return L+ii*(W-L-R)/(N-1);};
    var g=el('g',{},svg); grid(svg,W,L,R,H,T,B);
    el('rect',{x:L,y:yf(100),width:W-L-R,height:Math.abs(yf(100)-yf(80)),fill:'#CA3F64',opacity:0.07},g);  /* 修复：狂热区色带原 y=yf(80) 错位到 60~80 区间，正确应从 yf(100) 顶起 */
    el('rect',{x:L,y:yf(20),width:W-L-R,height:Math.abs(yf(0)-yf(20)),fill:'#25A750',opacity:0.07},g);
    el('line',{x1:L,x2:W-R,y1:yf(80),y2:yf(80),stroke:'#CA3F64','stroke-width':0.6,'stroke-dasharray':'4 3',opacity:0.6},g);
    el('line',{x1:L,x2:W-R,y1:yf(20),y2:yf(20),stroke:'#25A750','stroke-width':0.6,'stroke-dasharray':'4 3',opacity:0.6},g);
    hlabel(svg,W-R-46,yf(80)+10,'狂热 80','#AA0066',8); hlabel(svg,W-R-46,yf(20)+10,'冰点 20','#44AA88',8);
    polyline(g,tmp.map(function(v,ii){return[xf(ii),yf(v)];}),'#F0B90B',1.8);
    el('circle',{cx:xf(N-1),cy:yf(62),r:3.2,fill:'#F0B90B'},g);
    hlabel(svg,xf(N-1)-40,yf(62)-8,'今 62','#F0B90B',9);
    hlabel(svg,L,H-4,'近 20 日 · 78 分位（偏热未极热）','#59626D',9);
  }
  var svg2=document.getElementById('sent-breadth-svg'); if(svg2){
    svg2.innerHTML='';
    var W2=520,H2=170,L2=8,R2=8,T2=10,B2=18,N2=20,i2;
    var r2=lcg(620826),adv=[],nh=[],pa=1.15,pn=30;
    for(i2=0;i2<N2;i2++){pa+=(r2()-0.42)*0.22;pa=Math.max(0.6,Math.min(2.1,pa));adv.push(pa);pn+=(r2()-0.40)*26;pn=Math.max(-80,Math.min(160,pn));nh.push(pn);}
    adv[N2-1]=1.54; nh[N2-1]=96;
    var loB=-100,hiB=180,yf2=function(v){return T2+(1-(v-loB)/(hiB-loB))*(H2-T2-B2);},xf2=function(ii){return L2+ii*(W2-L2-R2)/(N2-1);};
    var g2=el('g',{},svg2); grid(svg2,W2,L2,R2,H2,T2,B2);
    var yfA=function(v){return T2+(1-(v-0.4)/(2.2-0.4))*(H2-T2-B2);};
    el('line',{x1:L2,x2:W2-R2,y1:yf2(0),y2:yf2(0),stroke:'#2A2F36','stroke-width':0.6},g2);
    polyline(g2,adv.map(function(v,ii){return[xf2(ii),yfA(v)];}),'#3D8BFF',1.8);
    polyline(g2,nh.map(function(v,ii){return[xf2(ii),yf2(v)];}),'#F0B90B',1.4);
    hlabel(svg2,L2+4,yfA(1.54)-8,'涨跌比 1.54','#3D8BFF',9);
    hlabel(svg2,L2+4,yf2(96)+12,'新高−新低 +96','#F0B90B',9);
    hlabel(svg2,L2,H2-4,'近 20 日 · 蓝=涨跌家数比（左轴 0.4~2.2） 橙=新高−新低差（右轴）','#59626D',9);
  }
}
(function sentInitTrend(){ sentRenderTrend(); })();
/* ---- I-8 循环升级 R4：做T 回验命中趋势（t0HitRender） ---- */
function t0HitRender(){
  var svg=document.getElementById('t0-hit-svg'); if(!svg)return; svg.innerHTML='';
  var W=480,H=150,L=8,R=8,T=10,B=16,N=20,i;
  var r=lcg(50825),v=[],p=0.68;
  for(i=0;i<N;i++){p+=(r()-0.46)*0.09;p=Math.max(0.5,Math.min(0.86,p));v.push(p);}
  v[N-1]=0.75;
  var yf=function(x){return T+(1-(x-0.4)/(0.95-0.4))*(H-T-B);},xf=function(ii){return L+ii*(W-L-R)/(N-1);};
  var g=el('g',{},svg); grid(svg,W,L,R,H,T,B);
  el('line',{x1:L,x2:W-R,y1:yf(0.6),y2:yf(0.6),stroke:'#AA0066','stroke-width':0.6,'stroke-dasharray':'4 3',opacity:0.7},g);
  hlabel(svg,W-R-64,yf(0.6)+10,'预警线 60%','#AA0066',8);
  polyline(g,v.map(function(x,ii){return[xf(ii),yf(x)];}),'#3D8BFF',1.8);
  el('circle',{cx:xf(N-1),cy:yf(0.75),r:3.2,fill:'#3D8BFF'},g);
  hlabel(svg,xf(N-1)-44,yf(0.75)-8,'今 75%','#3D8BFF',9);
  hlabel(svg,L,H-4,'7 日滚动命中率 · 均值 71% · 最低 58%（08-11）','#59626D',9);
}
(function t0InitHit(){ t0HitRender(); })();
/* ==================== I-5b F9 补强（并入 stockXxx 族） ==================== */
function stockRenderChip(){
  var c=stockD().chip; if(!c){var e0=document.getElementById('stock-chip');if(e0)e0.innerHTML='<tr><td class="dim">筹码数据缺省（演示口径未内置本标的）</td></tr>';return;}
  var h='<tr><th style="width:64px">报告期</th><th>股东户数（万户） <span class="dim">Holders</span></th><th style="width:82px">环比 <span class="dim">QoQ</span></th><th>主力持仓机构（家） <span class="dim">Institutions</span></th></tr>';
  for(var i=0;i<c.periods.length;i++){
    var qoq=i===0?null:(c.holders[i]-c.holders[i-1])/c.holders[i-1]*100;
    var ins=i===0?null:c.inst[i]-c.inst[i-1];
    h+='<tr><td>'+c.periods[i]+'</td>'
      +'<td><b>'+c.holders[i].toFixed(1)+'</b></td>'
      +'<td class="'+(qoq==null?'dim':(qoq<0?'down':'up'))+'">'+(qoq==null?'—':(qoq>0?'+':'')+qoq.toFixed(1)+'%')+'</td>'
      +'<td>'+c.inst[i]+(ins==null?'':' <span class="'+(ins>=0?'up':'down')+'" style="font-size:10px">'+(ins>=0?'+':'')+ins+'</span>')+'</td></tr>';
  }
  h+='<tr><td colspan="4" style="background:var(--panel2)">股权质押比例 <span class="dim">Pledge Ratio</span>：<b>'+c.pledge+'</b></td></tr>';
  document.getElementById('stock-chip').innerHTML=h;
}
function stockRenderPeer(){
  var b=stockD().biz; if(!b){var e1=document.getElementById('stock-peer');if(e1)e1.innerHTML='<span class="dim">主营/同行数据缺省（演示口径未内置本标的）</span>';return;}
  var seg='';
  b.seg.forEach(function(r){
    seg+='<div class="bar-row"><span>'+r[0]+'</span><div class="bar"><i style="width:'+r[1]+'%"></i></div><span>'+r[1].toFixed(1)+'%</span></div>';
  });
  var t='<tr><th>公司</th><th>PE TTM</th><th>PB</th><th>ROE</th><th>市值</th></tr>';
  b.peers.forEach(function(r){
    t+='<tr'+(r[5]?' class="stock-peer-self"':'')+'><td><b>'+r[0]+'</b>'+(r[5]?' <span class="badge b-pass">本公司</span>':'')+'</td><td>'+r[1]+'</td><td>'+r[2]+'</td><td>'+r[3]+'</td><td>'+r[4]+'</td></tr>';
  });
  document.getElementById('stock-peer').innerHTML=
    '<div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start">'
    +'<div style="flex:1;min-width:220px"><div class="sec-title" style="margin-top:0">主营构成 <span class="dim">Main Business · 营收占比</span></div>'+seg+'</div>'
    +'<div style="flex:1.2;min-width:300px"><div class="sec-title" style="margin-top:0">同行比较 <span class="dim">Peer Comparison</span></div><table>'+t+'</table></div>'
    +'</div>'
    +'<div style="margin-top:10px;font-size:12px">分红送转 <span class="dim">Dividend</span>：<b>'+b.div+'</b></div>';
}
/* ==================== I-6a 注册表库（regXxx） ==================== */
var REGLIB_D={
  factor:{cn:'因子库',en:'factor',n:140,upd:'2026-08-22',
    desc:'量化因子注册中心：每个因子=可复用研究资产，登记方向/计算口径/IC 口径与聚类分组，因子看板（A7/A8）与选股条件均由此供数。',
    fields:['factor_id 因子标识','direction 多空方向','formula 计算口径','ic_window IC 统计窗','cluster 相似组','status 状态'],
    head:['条目ID','名称','类别','方向','IC 均值','状态','更新日期'],
    rows:[
      ['F-0041','行业动量','动量','做多强势行业','0.048','stable','2026-08-20'],
      ['F-0057','北向增持','资金流','做多增持','0.055','stable','2026-08-21'],
      ['F-0009','估值下限','价值','做多低估值','0.031','testing','2026-08-18'],
      ['F-0003','反转因子','反转','做空高涨幅','0.062','stable','2026-08-22'],
      ['F-0112','质量因子','质量','做多高ROE','0.039','candidate','2026-08-15']],
    dist:{stable:96,testing:18,candidate:10}},
  strategy:{cn:'策略库',en:'strategy',n:146,upd:'2026-08-21',
    desc:'策略注册表：每个策略一份档案（说明/绩效/适用环境/离场说明）——策略是资产不是黑箱，作战室方案与回测实验均引用此库 strategy_id。',
    fields:['strategy_id 策略标识','family 策略族','universe_ref 股票池引用','entry/exit 出入场规则','risk_ref 限额引用','status 状态'],
    head:['条目ID','名称','策略族','适用环境','近一年收益','状态','更新日期'],
    rows:[
      ['S-0007','主线龙头回踩','趋势','强主线行情','+32.4%','stable','2026-08-20'],
      ['S-0012','行业轮动','轮动','风格切换期','+18.6%','stable','2026-08-19'],
      ['S-0003','打板策略','情绪','高赚钱效应','+41.2%','testing','2026-08-17'],
      ['S-0015','低估值防御','价值','弱市防御','+9.8%','stable','2026-08-14'],
      ['S-0019','做T增强','T+0','震荡持仓','+6.3%','candidate','2026-08-11']],
    dist:{stable:15,testing:5,candidate:3}},
  technical_indicator:{cn:'技术指标库',en:'technical_indicator',n:41,upd:'2026-08-18',
    desc:'技术指标注册表：技术分析页 39 指标窗格的数据源——每指标登记参数默认值/信号方向/适用周期，指标增删改走注册表而非硬编码。',
    fields:['ind_id 指标标识','params 默认参数','signal_rule 信号规则','period_fit 适用周期','pane_default 默认窗格','status 状态'],
    head:['条目ID','名称','类别','默认参数','信号口径','状态','更新日期'],
    rows:[
      ['I-001','MA 移动平均线','趋势','5/10/20/60','金叉多/死叉空','stable','2026-08-10'],
      ['I-004','MACD','趋势','12/26/9','DIF/DEA 交叉+柱','stable','2026-08-10'],
      ['I-007','RSI 相对强弱','摆动','6/14/24','>70 超买 <30 超卖','stable','2026-08-12'],
      ['I-009','KDJ','摆动','9/3/3','J 值钝化提示','stable','2026-08-12'],
      ['I-012','BOLL 布林线','通道','20/2','触轨回归','stable','2026-08-15'],
      ['I-015','ATR 真实波幅','波动','14','止损间距参考','testing','2026-08-16']],
    dist:{stable:35,testing:4,candidate:2}},
  universe:{cn:'股票池库',en:'universe',n:18,upd:'2026-08-20',
    desc:'股票池注册表：全A/指数成分/自选板块等选股宇宙的统一定义——条件选股与策略回测的 universe 参数只允许引用在册池，杜绝口径漂移。',
    fields:['universe_id 池标识','members_rule 成分规则','rebalance_freq 调样频率','pit_flag PIT 截断','size 当前规模','status 状态'],
    head:['条目ID','名称','成分规则','调样频率','当前规模','状态','更新日期'],
    rows:[
      ['U-001','全A','全部上市A股','日','5420','stable','2026-08-20'],
      ['U-002','沪深300','指数成分','半年','300','stable','2026-08-20'],
      ['U-003','中证500','指数成分','半年','500','stable','2026-08-20'],
      ['U-004','中证1000','指数成分','半年','1000','stable','2026-08-20'],
      ['U-006','创业板50','指数成分','季度','50','stable','2026-08-19'],
      ['U-011','自选股板块','人工维护','手动','36','testing','2026-08-18']],
    dist:{stable:14,testing:3,candidate:1}},
  benchmark:{cn:'基准库',en:'benchmark',n:9,upd:'2026-08-17',
    desc:'业绩比较基准注册表：回测与复盘的超额收益口径基准——每策略档案必须声明 benchmark_ref，防止「换基准美化业绩」。',
    fields:['bench_id 基准标识','index_code 指数代码','weight_rule 加权口径','daily_src 日行情源','status 状态'],
    head:['条目ID','名称','指数代码','加权口径','用途','状态','更新日期'],
    rows:[
      ['B-001','沪深300','000300.SH','自由流通市值','大盘策略基准','stable','2026-08-17'],
      ['B-002','中证500','000905.SH','自由流通市值','中盘策略基准','stable','2026-08-17'],
      ['B-003','中证1000','000852.SH','自由流通市值','小盘策略基准','stable','2026-08-17'],
      ['B-004','万得全A','881001.WI','总市值','全市场基准','stable','2026-08-16'],
      ['B-006','偏股基金指数','885001.WI','等权','相对排名基准','testing','2026-08-12']],
    dist:{stable:8,testing:1,candidate:0}},
  cost_model:{cn:'成本模型库',en:'cost_model',n:6,upd:'2026-08-15',
    desc:'交易成本模型注册表：佣金/印花税/滑点/冲击成本的显式登记——回测必须引用在册成本模型，禁止「零成本回测」虚增业绩。',
    fields:['cost_id 模型标识','commission 佣金','stamp_tax 印花税','slippage 滑点规则','impact 冲击成本','status 状态'],
    head:['条目ID','名称','佣金','印花税','滑点','状态','更新日期'],
    rows:[
      ['C-001','标准零售','万2.5','卖出千1','固定 2bp','stable','2026-08-10'],
      ['C-002','机构低佣','万1.2','卖出千1','固定 1bp','stable','2026-08-10'],
      ['C-003','冲击成本平方根','万1.5','卖出千1','√参与度','testing','2026-08-14'],
      ['C-004','压力成本','万3','卖出千1','固定 5bp','stable','2026-08-15'],
      ['C-005','零成本(禁用)','0','0','0','candidate','2026-08-01']],
    dist:{stable:5,testing:1,candidate:0}},
  execution_algo:{cn:'执行算法库',en:'execution_algo',n:7,upd:'2026-08-14',
    desc:'执行算法注册表：TWAP/VWAP/POV 等拆单执行规则的登记处——「怎么买」与「买什么」分离，执行损耗可归因可复盘。',
    fields:['algo_id 算法标识','schedule 时间切片规则','participation 参与度上限','venue 通道','status 状态'],
    head:['条目ID','名称','切片规则','参与度上限','适用场景','状态','更新日期'],
    rows:[
      ['E-001','TWAP 时间加权','等时间间隔','—','流动性好中小单','stable','2026-08-10'],
      ['E-002','VWAP 量加权','按历史量能','≤10%','大单拆单','stable','2026-08-10'],
      ['E-003','POV 参与度','跟随实时量','≤8%','隐蔽建仓','testing','2026-08-12'],
      ['E-004','冰山单','显小隐大','—','挂单执行','candidate','2026-08-09'],
      ['E-005','收盘集合竞价','尾盘撮合','—','调仓日执行','stable','2026-08-14']],
    dist:{stable:5,testing:1,candidate:1}},
  risk_limit:{cn:'风险限额库',en:'risk_limit',n:12,upd:'2026-08-19',
    desc:'风险限额注册表：单票/行业/换手/回撤/杠杆等硬约束的集中登记——方案生成与回测门控共用同一套限额，违规即拒单。',
    fields:['limit_id 限额标识','scope 作用域','threshold 阈值','breach_action 触发动作','status 状态'],
    head:['条目ID','名称','作用域','阈值','触发动作','状态','更新日期'],
    rows:[
      ['R-001','单票硬顶','组合','8%','拒单','stable','2026-08-10'],
      ['R-002','行业上限','组合','25%','告警+降档','stable','2026-08-10'],
      ['R-003','单日换手上限','组合','15%','拒单','stable','2026-08-12'],
      ['R-004','最大回撤线','组合','12%','降杠杆','stable','2026-08-15'],
      ['R-005','杠杆上限','组合','1.0x','拒单','stable','2026-08-15'],
      ['R-008','单票集中度预警','组合','6%','告警','testing','2026-08-18']],
    dist:{stable:10,testing:1,candidate:1}},
  data_asset:{cn:'数据资产库',en:'data_asset',n:121,upd:'2026-08-22',
    desc:'数据资产注册表：行情/资金/财报/公告等数据集的全量目录——每张表登记粒度/更新频率/PIT 口径，个股档案各卡即按此目录取数。',
    fields:['asset_id 资产标识','granularity 粒度','freq 更新频率','pit_rule PIT 口径','owner 责任管线','status 状态'],
    head:['条目ID','名称','粒度','更新频率','PIT 口径','状态','更新日期'],
    rows:[
      ['D-0001','kline_daily 日K线','股票×日','日','不复权/前复权双存','stable','2026-08-22'],
      ['D-0012','money_flow 资金流向','股票×日','日','当日收盘后','stable','2026-08-22'],
      ['D-0023','top10_holders 前十大股东','股票×报告期','季','披露日入库','stable','2026-08-20'],
      ['D-0031','income_statement 利润表','股票×季','季','披露日入库','stable','2026-08-20'],
      ['D-0044','announcements 公告','股票×篇','实时','发布时间戳','testing','2026-08-21'],
      ['D-0052','index_daily 指数日行情','指数×日','日','收盘后','stable','2026-08-22']],
    dist:{stable:90,testing:21,candidate:10}},
  chart_pattern:{cn:'K线形态库',en:'chart_pattern',n:256,upd:'2026-08-21',
    desc:'K线形态注册表：单根/组合/经典形态的识别规则与统计胜率——形态信号全部可溯源到在册条目，识别引擎按 registry 驱动。',
    fields:['pattern_id 形态标识','bar_count K线根数','detect_rule 识别规则','win_rate 统计胜率','status 状态'],
    head:['条目ID','名称','类别','K线根数','近5年胜率','状态','更新日期'],
    rows:[
      ['P-0012','锤子线','反转·底','1','58.3%','stable','2026-08-20'],
      ['P-0018','看涨吞没','反转·底','2','56.1%','stable','2026-08-20'],
      ['P-0024','启明星','反转·底','3','59.7%','stable','2026-08-21'],
      ['P-0089','双顶','反转·顶','复合','54.2%','stable','2026-08-19'],
      ['P-0103','头肩底','反转·底','复合','61.5%','testing','2026-08-18']],
    dist:{stable:200,testing:36,candidate:20}},
  field_dictionary:{cn:'字段词典',en:'field_dictionary',n:86,upd:'2026-08-16',
    desc:'字段词典：跨表字段的统一中文名/单位/口径定义——所有页面表格列名必须出自词典，杜绝「同一字段三种叫法」。',
    fields:['field_id 字段标识','cn_name 中文名','unit 单位','definition 口径定义','src_tables 来源表','status 状态'],
    head:['条目ID','字段','中文名','单位','口径','状态','更新日期'],
    rows:[
      ['FD-001','close','收盘价','元','不复权原始收盘','stable','2026-08-10'],
      ['FD-007','adj_factor','复权因子','倍','前复权基准','stable','2026-08-10'],
      ['FD-015','turnover_rate','换手率','%','自由流通股本口径','stable','2026-08-12'],
      ['FD-021','pe_ttm','市盈率TTM','倍','滚动四季净利','stable','2026-08-14'],
      ['FD-034','np_parent','归母净利','亿元','归属母公司股东','testing','2026-08-15']],
    dist:{stable:70,testing:10,candidate:6}},
  experiment:{cn:'实验库',en:'experiment',n:34,upd:'2026-08-22',
    desc:'回测实验注册表：每次回测=一条实验记录（参数快照/数据切片/门控结果）——实验可复现、可对比、可审计，复盘页按 exp_id 回溯。',
    fields:['exp_id 实验标识','strategy_ref 策略引用','param_snapshot 参数快照','gate_result 门控结果','metrics 绩效指标','status 状态'],
    head:['条目ID','名称','策略','区间','门控','年化','状态','更新日期'],
    rows:[
      ['EXP-20260820-03','动量v3·中证500','行业动量','2023-01~2026-06','通过','+18.2%','stable','2026-08-20'],
      ['EXP-20260819-01','反转·全A','反转因子','2022-01~2026-06','通过','+14.7%','stable','2026-08-19'],
      ['EXP-20260817-02','打板·情绪增强','打板策略','2024-01~2026-06','未过','+38.1%','testing','2026-08-17'],
      ['EXP-20260815-04','低波防御·300','低估值防御','2023-01~2026-06','通过','+8.9%','stable','2026-08-15'],
      ['EXP-20260812-01','轮动双因子','行业轮动','2022-01~2026-06','未过','+11.3%','candidate','2026-08-12']],
    dist:{stable:20,testing:9,candidate:5}},
  seat:{cn:'龙虎榜席位库',en:'seat',n:58,upd:'2026-08-19',
    desc:'龙虎榜席位注册表：「谁在买」——知名游资/机构席位画像（风格/成功率/常出没题材），情绪面复盘与打板策略的席位归因数据源。',
    fields:['seat_id 席位标识','alias 市场俗称','style 操作风格','hit_rate 上榜成功率','theme_pref 题材偏好','status 状态'],
    head:['条目ID','席位','俗称','风格','上榜成功率','状态','更新日期'],
    rows:[
      ['SE-003','国泰君安上海江苏路','章盟主','趋势龙头','62.4%','stable','2026-08-18'],
      ['SE-011','国泰君安南京太平南路','作手新一','首板挖掘','57.8%','stable','2026-08-18'],
      ['SE-017','兴业证券陕西分公司','方新侠','主线接力','59.2%','stable','2026-08-19'],
      ['SE-024','深南东路营业部','深南哥','题材轮动','51.6%','testing','2026-08-17'],
      ['SE-030','机构专用','机构席位','价投/调仓','—','stable','2026-08-19']],
    dist:{stable:45,testing:8,candidate:5}},
  regime_cycle:{cn:'周期规则库',en:'regime_cycle',n:15,upd:'2026-08-13',
    desc:'周期规则注册表：规则性时间窗口的显式登记（财报季/月末再平衡/节前效应等）——「什么时候容易发生什么」变成可回测的规则条目而非经验口诀。',
    fields:['cycle_id 规则标识','window 时间窗口','trigger 触发条件','action_hint 策略提示','evidence 历史验证','status 状态'],
    head:['条目ID','名称','时间窗口','策略提示','历史验证','状态','更新日期'],
    rows:[
      ['RC-001','财报披露季','1/4/8/10月末','披露前降题材仓','近5季胜率68%','stable','2026-08-10'],
      ['RC-002','两会窗口','3月上旬','政策题材活跃','近10年7次有效','stable','2026-08-10'],
      ['RC-003','月末再平衡','每月末3日','被动资金尾盘异动','—','stable','2026-08-11'],
      ['RC-004','节前效应','长假前5日','缩量降波动','近5年4次有效','testing','2026-08-12'],
      ['RC-005','解禁高峰窗口','解禁日±5日','回避高解禁占比','—','stable','2026-08-13']],
    dist:{stable:11,testing:3,candidate:1}},
  model:{cn:'模型库',en:'model',n:8,upd:'2026-08-16',
    desc:'ML 模型注册表：模型产物的版本化登记（训练集/特征清单/评估指标）——模型是产物不是黑箱，线上引用必须指向在册版本。',
    fields:['model_id 模型标识','algo 算法','feature_set 特征清单','train_window 训练窗','metric 评估指标','status 状态'],
    head:['条目ID','名称','算法','训练窗','关键指标','状态','更新日期'],
    rows:[
      ['M-002','lgbm_alpha_v2','LightGBM','2020-01~2025-12','IC 0.071','stable','2026-08-15'],
      ['M-003','xgb_sector_cls','XGBoost','2021-01~2025-12','Acc 63.2%','testing','2026-08-14'],
      ['M-004','lstm_regime','LSTM','2018-01~2025-12','F1 0.58','candidate','2026-08-12']],
    dist:{stable:2,testing:2,candidate:1}},
  event_calendar:{cn:'事件日历库',en:'event_calendar',n:42,upd:'2026-08-22',
    desc:'事件日历注册表：离散事件类型（宏观发布/解禁/新股/财报/分红）+ PIT 纪律——只登记「当时已知」的排期，事件日历页（I-5）即由本库供数。',
    fields:['event_id 事件标识','type 事件类型','knowledge_date 最早可知日','occur_date 发生日','importance 重要性','status 状态'],
    head:['条目ID','事件类型','发生日','最早可知日','重要性','状态','更新日期'],
    rows:[
      ['EV-0812','宏观发布·CPI','2026-09-09','2026-08-22','高','stable','2026-08-22'],
      ['EV-0823','限售解禁·某300成分','2026-08-28','2026-08-01','中','stable','2026-08-21'],
      ['EV-0831','新股上市·科创板','2026-08-26','2026-08-20','低','stable','2026-08-20'],
      ['EV-0845','财报披露·中报截止','2026-08-31','2026-01-01','高','stable','2026-08-15'],
      ['EV-0852','分红除权·沪深300成分','2026-08-27','2026-07-30','中','testing','2026-08-19']],
    dist:{stable:30,testing:8,candidate:4}},
  macro_indicator:{cn:'宏观指标库',en:'macro_indicator',n:67,upd:'2026-08-20',
    desc:'宏观指标注册表：CPI/PMI/M2/LPR/社融等指标的发布纪律（发布时间/修订规则/滞后期）——宏观分析页取数口径，回测引用按 knowledge_date 截断防未来函数。',
    fields:['macro_id 指标标识','release_rule 发布规则','revision 修订规则','lag_days 滞后天数','impact 影响面','status 状态'],
    head:['条目ID','指标','发布规则','修订','滞后','状态','更新日期'],
    rows:[
      ['MI-001','CPI 同比','每月9日 9:30','修订入次月','T+0','stable','2026-08-20'],
      ['MI-004','官方制造业PMI','每月最后日 9:00','不修订','T+0','stable','2026-08-20'],
      ['MI-009','M2 同比','每月10~15日','可修订','T+0','stable','2026-08-18'],
      ['MI-012','LPR 报价','每月20日 9:15','不修订','T+0','stable','2026-08-20'],
      ['MI-015','社融存量同比','每月10~15日','可修订','T+0','stable','2026-08-18'],
      ['MI-031','美债10Y收益率','日频','不修订','T+1','testing','2026-08-19']],
    dist:{stable:52,testing:10,candidate:5}},
  portfolio_model:{cn:'组合模型库',en:'portfolio_model',n:8,upd:'2026-08-15',
    desc:'组合构建模型注册表：「买多少」——等权/风险平价/均值方差/目标波动等配权规则的登记处，方案页的推荐仓位即由在册模型计算。',
    fields:['pm_id 模型标识','objective 优化目标','constraints 约束引用','lookback 估计窗','turnover_cap 换手上限','status 状态'],
    head:['条目ID','名称','优化目标','估计窗','换手上限','状态','更新日期'],
    rows:[
      ['PM-001','等权配置','分散','—','—','stable','2026-08-10'],
      ['PM-002','风险平价','风险贡献均衡','250日','月 20%','stable','2026-08-12'],
      ['PM-003','均值方差','夏普最大化','250日','月 30%','testing','2026-08-13'],
      ['PM-004','目标波动率','波动率钉住10%','60日','月 25%','stable','2026-08-14'],
      ['PM-005','核心卫星','核心稳+卫星攻','—','—','candidate','2026-08-15']],
    dist:{stable:5,testing:2,candidate:1}}
};
var REGLIB_ORDER=['factor','strategy','technical_indicator','universe','benchmark','cost_model','execution_algo','risk_limit','data_asset','chart_pattern','field_dictionary','experiment','seat','regime_cycle','model','event_calendar','macro_indicator','portfolio_model'];
var regState={sel:'factor'};
function regEsc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function regDistBadge(s){
  if(s==='stable') return '<span class="badge b-pass">stable</span>';
  if(s==='testing') return '<span class="badge b-warn">testing</span>';
  return '<span class="badge b-na">candidate</span>';
}
function regRenderCards(){
  var q=(document.getElementById('reg-srch').value||'').trim().toLowerCase(), shown=0;
  var html=REGLIB_ORDER.map(function(k){
    var d=REGLIB_D[k];
    var hit=!q||d.cn.toLowerCase().indexOf(q)>=0||d.en.toLowerCase().indexOf(q)>=0;
    if(hit) shown++;
    return '<div class="card factor-card reg-card'+(regState.sel===k?' active':'')+'" data-reg="'+k+'" style="'+(hit?'':'display:none')+'" onclick="regSel(\''+k+'\')">'
      +'<div class="reg-card-top"><i class="reg-dot"></i><b>'+d.cn+'</b><span class="dim reg-en">'+d.en+'</span></div>'
      +'<div class="reg-meta"><span><b class="reg-n">'+d.n+'</b> 条目</span><span class="dim">更新 '+d.upd+'</span></div>'
      +'</div>';
  }).join('');
  document.getElementById('reg-grid').innerHTML=html;
  document.getElementById('reg-cnt').textContent=shown+' / 18 库'+(q?' · 过滤中':' · 点击卡片查看详情');
}
function regRenderDetail(){
  var k=regState.sel, d=REGLIB_D[k];
  var tot=d.dist.stable+d.dist.testing+d.dist.candidate;
  var pct=function(v){return (v/tot*100).toFixed(1)};
  var rows=d.rows.map(function(r){
    var tds='<td class="dim">'+regEsc(r[0])+'</td><td><b>'+regEsc(r[1])+'</b></td>';
    for(var i=2;i<r.length-2;i++) tds+='<td>'+regEsc(r[i])+'</td>';
    tds+='<td>'+regDistBadge(r[r.length-2])+'</td><td class="dim">'+r[r.length-1]+'</td>';
    return '<tr>'+tds+'</tr>';
  }).join('');
  var head='<tr>'+d.head.map(function(h){return '<th>'+h+'</th>'}).join('')+'</tr>';
  document.getElementById('reg-detail').innerHTML=
    '<div class="card">'
    +'<h3>'+d.cn+' <span class="dim">'+d.en+' · '+d.n+' 条目 · 最近更新 '+d.upd+'</span> <span class="badge b-na">演示数据</span> <span class="badge b-fail">完整条目 JSON 导出供数后转真（I-2 流程）</span></h3>'
    +'<div style="font-size:12px;color:var(--dim);margin-bottom:10px">'+d.desc+'</div>'
    +'<div class="sec-title" style="margin-top:0">关键字段 <span class="dim">Key Fields</span></div>'
    +'<div style="margin-bottom:12px">'+d.fields.map(function(f){return '<span class="reg-chip">'+regEsc(f)+'</span>'}).join('')+'</div>'
    +'<div class="sec-title" style="margin-top:0">条目样例 <span class="dim">Sample Entries · '+d.rows.length+' / '+d.n+' 行</span></div>'
    +'<table>'+head+rows+'</table>'
    +'<div class="sec-title">状态分布 <span class="dim">stable '+d.dist.stable+' / testing '+d.dist.testing+' / candidate '+d.dist.candidate+'</span></div>'
    +'<div class="reg-dist">'
      +'<i style="width:'+pct(d.dist.stable)+'%;background:var(--down)" title="stable '+d.dist.stable+'"></i>'
      +'<i style="width:'+pct(d.dist.testing)+'%;background:var(--yellow)" title="testing '+d.dist.testing+'"></i>'
      +'<i style="width:'+pct(d.dist.candidate)+'%;background:var(--faint)" title="candidate '+d.dist.candidate+'"></i>'
    +'</div>'
    +'<div class="lv" style="margin-top:6px"><span><i class="reg-lg" style="background:var(--down)"></i>stable '+d.dist.stable+'</span><span><i class="reg-lg" style="background:var(--yellow)"></i>testing '+d.dist.testing+'</span><span><i class="reg-lg" style="background:var(--faint)"></i>candidate '+d.dist.candidate+'</span></div>'
    +'<div class="note">负反馈也是结果：本卡仅展示 '+d.rows.length+' 条样例，完整 '+d.n+' 条目的 JSON 导出属 I-2 供数流程，转真前系统明说「没有」；PIT 类注册表（event_calendar/macro_indicator）引用须按 knowledge_date 截断</div>'
    +'</div>';
}
function regSel(k){
  regState.sel=k;
  document.querySelectorAll('#reg-grid .reg-card').forEach(function(c){c.classList.toggle('active',c.getAttribute('data-reg')===k)});
  regRenderDetail();
}
function regFilter(){regRenderCards()}
window.reglibInit=function(){ regRenderCards(); regRenderDetail(); };
/* ==================== I-6a 架构全景（panoXxx） ==================== */
var PANO_BASE='http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/';
var PANO_DOMAINS=[
 ['01_d_contracts','契约'],['02_d_infrastructure','基础设施'],['03_d_infra_a2a',''],['04_d_infra_ops',''],
 ['05_d_infra_recovery','容灾'],['06_d_infra_runtime',''],['07_d_infra_telemetry','遥测'],['08_d_shared','共享'],
 ['09_d_alt_data','另类数据'],['10_d_autonomy_core','自治核心'],['11_d_data','数据'],['12_d_data_eng','数据工程'],
 ['13_d_data_gov','数据治理'],['14_d_data_sec','数据安全'],['15_d_fbl_detectors','探测器'],['16_d_fbl_diagnosers','诊断器'],
 ['17_d_fbl_verification','验证'],['18_d_feedback_loop','反馈环'],['19_d_gov_code_quality','代码质量'],['20_d_gov_ops_resilience','运维韧性'],
 ['21_d_integration','集成'],['22_d_integration_gateway','网关'],['23_d_mkt_data','行情数据'],['24_d_ops','运维'],
 ['25_d_orchestrator','编排器'],['26_d_reporting','报告'],['27_d_security','安全'],['28_d_security_llm','LLM安全'],
 ['29_d_archive_scripts',''],['30_d_arch_guard','架构守卫'],['31_d_arch_scripts',''],['32_d_ashare_signal','A股信号'],
 ['33_d_audittest',''],['34_d_autonomy_perm','自治权限'],['35_d_backtest','回测'],['36_d_code_scripts',''],
 ['37_d_compliance','合规'],['38_d_compliance_scripts',''],['39_d_cross_asset','跨资产'],['40_d_data_scripts',''],
 ['41_d_digital_twin','数字孪生'],['42_d_exec_sim','执行仿真'],['43_d_ex_core','执行核心'],['44_d_ex_sor','智能路由'],
 ['45_d_factor','因子'],['46_d_frontend','前端'],['47_d_fundamental_signal','基本面信号'],['48_d_governance','治理'],
 ['49_d_gov_audit','审计'],['50_d_gov_docs','文档'],['51_d_gov_drift','漂移'],['52_d_gov_enforcement','执行'],
 ['53_d_gov_repair','修复'],['54_d_gov_rule','规则'],['55_d_gov_scripts',''],['56_d_intelligence','情报'],
 ['57_d_knowledge','知识'],['58_d_meta_scripts',''],['59_d_ml_serve','模型服务'],['60_d_ml_train','模型训练'],
 ['61_d_pf_alloc','组合配置'],['62_d_pf_core','组合核心'],['63_d_plan','计划'],['64_d_position','持仓'],
 ['65_d_regime','市场状态'],['66_d_risk','风险'],['67_d_sec_scripts',''],['68_d_sell_decision','卖出决策'],
 ['70_d_sigqc','信号质量'],['71_d_simulation','仿真'],['72_d_struct_scripts',''],['73_d_trading','交易']
];
var panoInited=false, panoCur='01_d_contracts', panoProbeTimer=null;
function panoUrl(k){ return PANO_BASE+(k||panoCur)+'.html'; }
function panoCn(k){
  for(var i=0;i<PANO_DOMAINS.length;i++) if(PANO_DOMAINS[i][0]===k) return PANO_DOMAINS[i][1];
  return '';
}
function panoRenderGrid(){
  var h='';
  for(var i=0;i<PANO_DOMAINS.length;i++){
    var d=PANO_DOMAINS[i];
    h+='<div class="pano-dom" data-k="'+d[0]+'" onclick="panoSelect(\''+d[0]+'\')">'
      +'<div class="pd-num">'+d[0].slice(0,2)+'</div>'
      +'<div class="pd-nm" title="'+d[0]+'">'+d[0].slice(3)+'</div>'
      +'<div class="pd-cn">'+(d[1]||'&nbsp;')+'</div>'
      +'</div>';
  }
  document.getElementById('pano-grid').innerHTML=h;
  document.getElementById('pano-count').textContent='共 '+PANO_DOMAINS.length+' 域';
}
function panoFilter(){
  var q=(document.getElementById('pano-srch').value||'').trim().toLowerCase(), shown=0;
  document.querySelectorAll('#pano-grid .pano-dom').forEach(function(el){
    var k=el.getAttribute('data-k'), cn=panoCn(k);
    var hit=!q || k.toLowerCase().indexOf(q)>=0 || (cn && cn.toLowerCase().indexOf(q)>=0);
    el.style.display=hit?'':'none';
    if(hit) shown++;
  });
  document.getElementById('pano-none').style.display=shown?'none':'';
  document.getElementById('pano-count').textContent='显示 '+shown+' / '+PANO_DOMAINS.length+' 域';
}
function panoSelect(k){
  panoCur=k;
  document.querySelectorAll('#pano-grid .pano-dom').forEach(function(el){
    el.classList.toggle('on', el.getAttribute('data-k')===k);
  });
  var url=panoUrl(k), cn=panoCn(k);
  document.getElementById('pano-url').value=url;
  document.getElementById('pano-cur-cn').textContent=k+(cn?' · '+cn:'');
  var fr=document.getElementById('pano-frame');
  fr.style.display=''; fr.src=url;
  document.getElementById('pano-off').style.display='none';
  panoProbe(url);
}
function panoProbe(url){
  if(panoProbeTimer) clearTimeout(panoProbeTimer);
  panoProbeTimer=setTimeout(function(){
    if(url!==panoUrl()) return;
    fetch(url,{method:'GET',mode:'no-cors',cache:'no-store'})   /* GET 替代 HEAD：消除 python http.server 下 Chrome ERR_ABORTED 噪音 */
      .then(function(){})
      .catch(function(){
        document.getElementById('pano-frame').style.display='none';
        document.getElementById('pano-off').style.display='';
      });
  },800);
}
function panoOpenNew(){ window.open(panoUrl(),'_blank'); }
window.panoInit=function(){
  if(panoInited){ panoProbe(panoUrl()); return; }
  panoInited=true;
  panoRenderGrid();
  panoSelect('01_d_contracts');
};
/* ==================== I-6b 模块总账（modXxx） ==================== */
var MOD_DOMS=[
  ['D_REGIME','市场状态'],['D_FACTOR','因子'],['D_BACKTEST','回测'],['D_RISK','风险'],
  ['D_PLAN','计划'],['D_POSITION','持仓'],['D_DATA','数据'],['D_GOVERNANCE','治理'],
  ['D_FRONTEND','前端'],['D_ML_TRAIN','模型训练'],['D_TRADING','交易'],['D_ORCHESTRATOR','编排']
];
var MOD_ST={stable:['stable','b-pass'],testing:['testing','b-test'],planned:['planned','b-warn'],cand:['cand','b-na']};
var MOD_SRC={'学术报告':'b-src-aca','GitHub':'b-src-git','项目报告':'b-src-prj','社区实践':'b-src-com'};
var MOD_D=[
 ['D_REGIME','市场状态检测器','regime_detector','学术报告','Hamilton 区制转换','stable','盘中实时页','日频 regime 判定 + 4 态输出','g','08-23'],
 ['D_REGIME','体制转换检测器','regime_shift_detector','学术报告','CUSUM 变点检测','testing','盘中实时页','分钟级体制切换预警','g','08-22'],
 ['D_REGIME','BM-SEL-04 次日 8 态预测','nextday_8state_forecast','项目报告','90 号 §7 裁定暂缓','planned','作战指挥页 · 待接入','次日开盘形态概率分布','w','—'],
 ['D_REGIME','波动率状态分类器','vol_regime_classifier','学术报告','GARCH(1,1)','stable','盘中实时页','波动三态（低/中/高）标注','g','08-23'],
 ['D_REGIME','趋势强度计','trend_strength_meter','GitHub','ADX 改造','stable','技术分析页','趋势/震荡二分类 + 强度分','y','07-18'],
 ['D_REGIME','市场宽度监视','market_breadth_watch','社区实践','涨跌家数比','stable','全景总览页','涨跌家数 / 新高新低汇总','g','08-23'],
 ['D_REGIME','情绪状态聚合器','sentiment_regime_agg','社区实践','CAND-117 登记','cand','—','新闻情绪 → 状态层输入','w','—'],
 ['D_FACTOR','行业动量因子','industry_momentum_factor','项目报告','','stable','因子档案页','申万一级 20 日动量排名','g','08-23'],
 ['D_FACTOR','北向增持因子','northbound_holding_factor','项目报告','','stable','因子档案页','北向持仓变动日频因子','g','08-23'],
 ['D_FACTOR','GAP-F-38 因子聚类','factor_cluster_engine','社区实践','CAND-038 登记','cand','因子档案页 · 待接入','因子相关谱系聚类去重','w','—'],
 ['D_FACTOR','反转因子（5 日）','reversal_5d_factor','学术报告','Jegadeesh 短期反转','stable','因子档案页','5 日反转 IC 跟踪','g','08-21'],
 ['D_FACTOR','换手率稳定度因子','turnover_stability_factor','社区实践','','stable','因子档案页','换手变异系数反向因子','y','06-30'],
 ['D_FACTOR','财报超预期因子','earnings_surprise_factor','学术报告','PEAD 漂移','testing','因子档案页','公告后漂移窗口收益','g','08-20'],
 ['D_FACTOR','拥挤度合成因子','crowding_composite','项目报告','软拥挤约束（夜班 #205）','stable','风险仪表盘','交易拥挤度 0-100 合成','g','08-23'],
 ['D_FACTOR','量价背离因子','price_volume_diverge_factor','GitHub','CAND-052 登记','cand','—','量价相关系数滚动窗口','w','—'],
 ['D_BACKTEST','回测引擎内核','backtest_engine_core','项目报告','rqalpha 二次封装','stable','回测结果页','事件驱动日/分钟双频','g','08-23'],
 ['D_BACKTEST','绩效归因器','performance_attributor','学术报告','Brinson 分解','stable','回测结果页','行业配置/选股双维归因','g','08-22'],
 ['D_BACKTEST','滑点模型','slippage_model','社区实践','冲击成本平方根律','stable','回测结果页','分档滑点 + 冲击成本','g','08-20'],
 ['D_BACKTEST','成交模拟器','fill_simulator','项目报告','','stable','回测结果页','涨跌停不可成交规则','g','08-23'],
 ['D_BACKTEST','参数扫描器','param_sweep_runner','GitHub','网格/贝叶斯','testing','实验门控页','批量参数组合并行','y','07-02'],
 ['D_BACKTEST','过拟合检验器','overfit_detector','学术报告','Deflated Sharpe','planned','实验门控页 · 待接入','DSR / PBO 双指标门禁','w','—'],
 ['D_BACKTEST','走步前进验证器','walk_forward_validator','学术报告','','testing','回测结果页','滚动样本外一致性','g','08-19'],
 ['D_RISK','回撤守门员','drawdown_guardian','项目报告','','stable','持仓页','组合回撤阈值硬拦截','g','08-23'],
 ['D_RISK','行业集中度约束','industry_concentration_cap','项目报告','夜班 #205/#207','stable','风险仪表盘','单行业暴露上限校验','g','08-23'],
 ['D_RISK','相关性净额器','correlation_netting','学术报告','GAP-F-04','testing','持仓页','高相关持仓合并计风险','g','08-21'],
 ['D_RISK','压力测试引擎','StressTestEngine（MOD-RK-12）','项目报告','BFE-32','stable','盘后复盘页','历史三情景重放','g','08-18'],
 ['D_RISK','流动性风险计','liquidity_risk_meter','学术报告','Amihud 非流动性','stable','风险仪表盘','冲击成本口径流动性分','y','06-12'],
 ['D_RISK','熔断开关','kill_switch','项目报告','','stable','系统状态页','极端行情一键切断交易','g','08-23'],
 ['D_RISK','尾部风险预期缺口','expected_shortfall_es','学术报告','CVaR 97.5% · CAND-044','cand','—','ES 日频估计','w','—'],
 ['D_PLAN','明日边界生成器','TomorrowBoundary（MOD-PLAN-001）','项目报告','','stable','作战指挥页','次日价格边界三件套','g','08-23'],
 ['D_PLAN','情景计划器','ScenarioPlan（MOD-PLAN-005）','项目报告','','stable','作战指挥页','3×3 情景矩阵方案','g','08-23'],
 ['D_PLAN','仓位缩放器','position_scaler','项目报告','','stable','作战指挥页','进攻/防守档仓位系数','g','08-22'],
 ['D_PLAN','信号聚合器','signal_aggregator（MOD-SIG-061/062）','项目报告','','testing','作战指挥页','主线概率 + 梯队完整度','g','08-23'],
 ['D_PLAN','交易计划持久化','plan_persistence','项目报告','','stable','盘后复盘页','计划-执行留痕对照','g','08-20'],
 ['D_PLAN','计划合规审计','plan_compliance_audit','项目报告','CAND-072 登记','cand','—','偏离计划自动标注','w','—'],
 ['D_POSITION','持仓台账','position_ledger','项目报告','','stable','持仓页','实盘/模拟双账簿','g','08-23'],
 ['D_POSITION','盈亏归因器','pnl_attribution','学术报告','逐票→板块→因子','stable','持仓页','三层盈亏拆解','g','08-23'],
 ['D_POSITION','做T辅助器','intraday_t_helper','社区实践','','stable','T分析页','日内点位 + 回补提示','y','07-25'],
 ['D_POSITION','保证金监视器','margin_monitor','项目报告','','planned','持仓页 · 待接入','两融维持担保比例','w','—'],
 ['D_POSITION','红利再投资器','dividend_reinvest','社区实践','','stable','持仓页','除权现金流自动记账','g','08-15'],
 ['D_POSITION','持仓快照同步','position_snapshot_sync','GitHub','','testing','—','券商接口对账快照','g','08-23'],
 ['D_DATA','数据清单生成器','generate_data_inventory','项目报告','121 表扫描','stable','系统状态页','全表扫描 + 异常标注','g','08-23'],
 ['D_DATA','分钟K线构建器','minute_bar_builder','项目报告','','stable','数据管理页','1/5/15/30/60min 聚合','g','08-23'],
 ['D_DATA','复权因子链路','adj_factor_pipeline','项目报告','夜班 #196/#197/#198','testing','数据管理页','前复权因子持续生产','g','08-22'],
 ['D_DATA','北向资金采集器','northbound_collector','项目报告','','stable','数据管理页','港交所持股日频','g','08-23'],
 ['D_DATA','新闻事件抽取器','news_event_extractor','GitHub','FinNLP 改造','testing','新闻公告页','事件标签 + 情绪打分','g','08-21'],
 ['D_DATA','财报下载器','financial_report_fetcher','社区实践','tushare 主源','stable','数据管理页','三大报表季度同步','y','06-28'],
 ['D_DATA','盘口快照存档器','snapshot_archiver','项目报告','','stable','—','五档快照 3 秒落盘','g','08-23'],
 ['D_DATA','宏观指标注册表','macro_indicator_registry','项目报告','CAND-091 登记','cand','宏观分析页 · 待接入','指标发布纪律登记','w','—'],
 ['D_GOVERNANCE','任务调度内核','task_scheduler','项目报告','tasks.yaml 167 任务','stable','任务进度页','156 启用任务节拍','g','08-23'],
 ['D_GOVERNANCE','适应度函数评估','fitness_function_eval','学术报告','演进式架构','stable','适应评估页','5 项度量门禁','g','08-20'],
 ['D_GOVERNANCE','门禁统计器','gate_stats','项目报告','','planned','治理分析页 · 待接入','通过/拦截率 OLAP','w','—'],
 ['D_GOVERNANCE','幻觉拦截器','hallucination_interceptor','项目报告','','stable','适应评估页','生成内容事实校验','g','08-19'],
 ['D_GOVERNANCE','审计日志器','audit_logger','项目报告','','stable','任务进度页','操作全留痕回放','g','08-23'],
 ['D_GOVERNANCE','缺口总账','gap_ledger','项目报告','CAND-005 登记','cand','—','已知缺口登记 + 闭环','w','—'],
 ['D_FRONTEND','仪表盘原型','dashboard_mockup','项目报告','v1.3','stable','本页','单文件全页原型','g','08-23'],
 ['D_FRONTEND','回测面板','app_panel.py','项目报告','Streamlit','stable','回测结果页','绩效看板','g','08-22'],
 ['D_FRONTEND','图表渲染器','chart_renderer','社区实践','轻量 canvas','stable','技术分析页','K线 + 指标多窗格','g','08-21'],
 ['D_FRONTEND','页面-模块映射表','page_module_mapping','项目报告','人工种子+生成器','testing','本页','前端显示列供数','g','08-23'],
 ['D_FRONTEND','主题令牌库','theme_tokens','项目报告','','stable','全局','色板/字号统一令牌','g','08-20'],
 ['D_FRONTEND','实时推送网关','realtime_push_gateway','GitHub','WebSocket · CAND-077','cand','—','行情秒级推前端','w','—'],
 ['D_FRONTEND','移动端适配层','mobile_adapter','社区实践','','planned','待接入','小屏断点重排','w','—'],
 ['D_ML_TRAIN','训练数据装配器','train_dataset_builder','项目报告','','stable','实验门控页','样本/标签/切分三件套','g','08-21'],
 ['D_ML_TRAIN','特征选择器','feature_selector','学术报告','LGBM 重要性','testing','因子档案页','因子池逐轮淘汰','g','08-18'],
 ['D_ML_TRAIN','元标签器','meta_labeler','学术报告','López de Prado','planned','实验门控页 · 待接入','次级信号过滤','w','—'],
 ['D_ML_TRAIN','模型登记处','model_registry','社区实践','MLflow 风格','stable','实验门控页','版本/指标/工件索引','g','08-20'],
 ['D_ML_TRAIN','在线学习管线','online_learning_pipe','GitHub','CAND-063 登记','cand','—','日频增量更新','w','—'],
 ['D_ML_TRAIN','超参优化器','hyperparam_optimizer','GitHub','Optuna','stable','实验门控页','贝叶斯搜索预算控制','y','07-09'],
 ['D_TRADING','订单路由器','order_router','项目报告','','stable','交易执行页','QMT/模拟双通道分发','g','08-23'],
 ['D_TRADING','委托频率哨兵','order_rate_sentinel','项目报告','','stable','系统状态页','异常委托频率熔断前置','g','08-23'],
 ['D_TRADING','智能拆单器','smart_order_splitter','学术报告','TWAP / VWAP','testing','交易执行页','大单切片执行','g','08-22'],
 ['D_TRADING','竞价量分析器','auction_volume_analyzer','项目报告','D2 确认口径','stable','作战指挥页','竞价量比监测','g','08-23'],
 ['D_TRADING','回执对账器','execution_reconciler','项目报告','','stable','盘后复盘页','委托-成交-持仓三对照','g','08-23'],
 ['D_TRADING','算法交易引擎','algo_trading_engine','GitHub','CAND-084 登记','cand','—','策略化执行算法库','w','—'],
 ['D_ORCHESTRATOR','全景图生成器','depgraph_generator','项目报告','6,869 节点','stable','本页','依赖全景 + build_status','g','08-23'],
 ['D_ORCHESTRATOR','日报编排器','daily_report_orchestrator','项目报告','','stable','全景总览页','盘后报告串行编排','g','08-22'],
 ['D_ORCHESTRATOR','夜班工作流','night_shift_workflow','项目报告','','stable','任务进度页','缺陷修复批次执行','g','08-23'],
 ['D_ORCHESTRATOR','数据质量看门','data_quality_watchdog','社区实践','','testing','系统状态页','时间戳/空表异常扫描','g','08-23'],
 ['D_ORCHESTRATOR','跨层血缘解析器','lineage_resolver','学术报告','CAND-029 登记','cand','—','L1-L10 表级血缘','w','—'],
 ['D_ORCHESTRATOR','发布列车','release_train','项目报告','','planned','待接入','版本窗口 + 回滚预案','w','—']
];
var modDom='all',modSt='all',modQ='';
function modRenderTabs(){
  var h='<span class="tab'+(modDom==='all'?' on':'')+'" onclick="modSetDom(\'all\')">全部</span>';
  MOD_DOMS.forEach(function(dk){
    h+='<span class="tab'+(modDom===dk[0]?' on':'')+'" onclick="modSetDom(\''+dk[0]+'\')">'+dk[1]+'</span>';
  });
  document.getElementById('mod-domtabs').innerHTML=h;
}
function modRenderTable(){
  var q=modQ.toLowerCase(),shown=0;
  var h='<tr><th style="width:230px">模块</th><th style="width:150px">来源</th><th style="width:78px">状态</th><th style="width:150px">前端显示</th><th>功能说明</th><th style="width:96px">最近使用</th></tr>';
  MOD_DOMS.forEach(function(dk){
    if(modDom!=='all'&&modDom!==dk[0]) return;
    var rows=MOD_D.filter(function(r){
      if(r[0]!==dk[0]) return false;
      if(modSt!=='all'&&r[5]!==modSt) return false;
      if(q&&r[1].toLowerCase().indexOf(q)<0&&r[2].toLowerCase().indexOf(q)<0) return false;
      return true;
    });
    if(!rows.length) return;
    var nB=rows.filter(function(r){return r[5]==='stable'||r[5]==='testing';}).length;
    var nP=rows.filter(function(r){return r[5]==='planned';}).length;
    var nC=rows.filter(function(r){return r[5]==='cand';}).length;
    h+='<tr class="mod-dom"><td colspan="6">'+dk[0]+' '+dk[1]
      +' <span class="dim" style="font-weight:400">· '+rows.length+' 模块（已建 '+nB+' · 设计 '+nP+' · 候选 '+nC+'）</span></td></tr>';
    rows.forEach(function(r){
      shown++;
      var lamp=r[8]==='g'?'<span class="dot ok"></span>'+r[9]
        :(r[8]==='y'?'<span class="dot y"></span>'+r[9]:'<span class="dot w"></span>—');
      h+='<tr><td>'+r[1]+'<div class="mod-en">'+r[2]+'</div></td>'
        +'<td><span class="badge '+MOD_SRC[r[3]]+'">'+r[3]+'</span>'+(r[4]?'<div class="mod-en">'+r[4]+'</div>':'')+'</td>'
        +'<td><span class="badge '+MOD_ST[r[5]][1]+'">'+MOD_ST[r[5]][0]+'</span></td>'
        +'<td>'+(r[6]==='—'?'<span class="na">—</span>':r[6])+'</td>'
        +'<td class="dim">'+r[7]+'</td>'
        +'<td>'+lamp+'</td></tr>';
    });
  });
  if(!shown) h+='<tr><td colspan="6" class="na">无匹配模块——请调整域筛选 / 状态筛选或搜索词</td></tr>';
  document.getElementById('mod-table').innerHTML=h;
  document.getElementById('mod-count').textContent='显示 '+shown+' / 演示 '+MOD_D.length+' 行（全量 6,912 行 I-2 转真）';
}
function modSetDom(k){modDom=k;modRenderTabs();modRenderTable();}
function modSetSt(v){modSt=v;modRenderTable();}
function modSetQ(v){modQ=v;modRenderTable();}
window.modInit=function(){ modRenderTabs(); modRenderTable(); };
/* ==================== I-6c backtest+strategy（btrXxx / fwXxx） ==================== */
var FW_W=[
  {n:'主线龙头回踩',w:35,c:'var(--up)'},
  {n:'行业轮动',w:25,c:'var(--blue)'},
  {n:'低估值防御',w:25,c:'var(--purple)'},
  {n:'打板策略',w:10,c:'var(--orange)'},
  {n:'做T增强',w:5,c:'var(--yellow)'}
];
var FW_H=[
  ['08-21','震荡→震荡偏强','主线龙头 30→35%'],
  ['08-14','偏弱→震荡','低估值防御 20→25%'],
  ['08-07','震荡→偏弱','打板策略 15→10%'],
  ['07-31','偏强→震荡','行业轮动 30→25%'],
  ['07-24','震荡→偏强','主线龙头 25→30%']
];
function fwRender(){
  var w=document.getElementById('fw-weights'); if(!w)return;
  w.innerHTML=FW_W.map(function(r){
    return '<div class="bar-row"><span>'+r.n+'</span><div class="bar"><i style="width:'+r.w+'%;background:'+r.c+'"></i></div><span>'+r.w+'%</span></div>';
  }).join('');
  var h=document.getElementById('fw-hist'); if(!h)return;
  h.innerHTML=FW_H.map(function(r){
    return '<div><b>'+r[0]+'</b> '+r[1]+'：<b>'+r[2]+'</b></div>';
  }).join('');
}
window.fwInit=function(){
  if(window.__fwInited)return; window.__fwInited=1;
  fwRender();
};
/* I-5/I-6 预渲染补充（幂等） */
window.fwInit();
/* ==================== G-一 底部 ticker 横条（tkXxx：自定义增减/双击跳转/秒级时钟/折叠/localStorage） ==================== */
var TK_POOL=[
 {sym:'sh',nm:'上证指数',code:'000001.SH',px:'3,087.53',chg:'+0.72%',dir:1,tgt:'index'},
 {sym:'sz',nm:'深证成指',code:'399001.SZ',px:'9,741.20',chg:'+1.05%',dir:1,tgt:'index'},
 {sym:'cy',nm:'创业板指',code:'399006.SZ',px:'1,892.44',chg:'-0.31%',dir:-1,tgt:'index'},
 {sym:'kc',nm:'科创综指',code:'000680.SH',px:'986.12',chg:'+1.48%',dir:1,tgt:'index'},
 {sym:'spx',nm:'标普500',code:'SPX · 昨收',px:'5,612.34',chg:'+0.38%',dir:1,tgt:'overseas'},
 {sym:'ndx',nm:'纳斯达克',code:'NDX · 昨收',px:'18,245.60',chg:'+0.61%',dir:1,tgt:'overseas'},
 {sym:'hsi',nm:'恒生指数',code:'HSI',px:'17,890.22',chg:'-0.42%',dir:-1,tgt:'overseas'},
 {sym:'600519',nm:'贵州茅台',code:'600519.SH',px:'1,712.50',chg:'+0.86%',dir:1,tgt:'stock'},
 {sym:'300750',nm:'宁德时代',code:'300750.SZ',px:'289.40',chg:'-1.24%',dir:-1,tgt:'stock'},
 {sym:'688981',nm:'中芯国际',code:'688981.SH',px:'99.20',chg:'+2.10%',dir:1,tgt:'stock'},
 {sym:'if',nm:'沪深300股指期货',code:'IF',px:'—',chg:'待接入',dir:0,tgt:'none',na:1},
 {sym:'nq',nm:'纳指期货CFD',code:'NQ',px:'—',chg:'待接入',dir:0,tgt:'none',na:1}
];
var TK_DEF=['sh','sz','cy','kc','spx','ndx','hsi'];
var tkList;
try{ tkList=JSON.parse(localStorage.getItem('zk-tk')||'null')||TK_DEF.slice(); }catch(e){ tkList=TK_DEF.slice(); }
var tkEdit=false;
function tkSave(){ try{localStorage.setItem('zk-tk',JSON.stringify(tkList));}catch(e){} }
function tkFind(sym){ for(var i=0;i<TK_POOL.length;i++) if(TK_POOL[i].sym===sym) return TK_POOL[i]; return null; }
function tkRender(){
  var box=document.getElementById('tk-items'); if(!box)return;
  box.className='tk-items'+(tkEdit?' editing':'');
  var h='';
  tkList.forEach(function(sym){
    var it=tkFind(sym); if(!it)return;
    var cls=it.dir>0?'up':(it.dir<0?'down':'na');
    h+='<span class="tk-item '+cls+'" ondblclick="tkJump(\''+it.sym+'\')" title="'+it.nm+' '+it.code+(it.na?'（库内无数据·待接入负反馈）':' · 双击跳转')+'">'
      +'<span class="nm">'+it.nm+'</span><span class="cd">'+it.code+'</span>'
      +'<span class="px">'+it.px+'</span><span class="pc">'+it.chg+'</span>'
      +'<span class="rm" onclick="event.stopPropagation();tkRm(\''+it.sym+'\')" title="从横条移除">−</span></span>';
  });
  box.innerHTML=h||'<span class="tk-item na"><span class="nm">清单为空——点右侧 ＋ 添加</span></span>';
}
function tkTglEdit(){
  tkEdit=!tkEdit;
  var b=document.getElementById('tk-edit-btn');
  b.textContent=tkEdit?'完成':'＋';
  b.classList.toggle('on',tkEdit);
  tkSrchShow(tkEdit);
  tkRender();
}
function tkRm(sym){
  tkList=tkList.filter(function(s){return s!==sym;});
  tkSave(); tkRender();
}
function tkAdd(sym){
  if(tkList.indexOf(sym)<0){ tkList.push(sym); tkSave(); tkRender(); }
  tkSrchRender();
}
function tkSrchShow(open){
  var l=document.getElementById('tk-slist'); if(!l)return;
  l.classList.toggle('open',open);
  if(open){ var inp=document.getElementById('tk-srch'); inp.value=''; tkSrchRender(); setTimeout(function(){inp.focus();},50); }
}
function tkSrchRender(){
  var q=(document.getElementById('tk-srch')||{}).value||''; q=q.trim().toLowerCase();
  var res=document.getElementById('tk-sres'); if(!res)return;
  var h='',cnt=0;
  TK_POOL.forEach(function(it){
    if(q&&it.nm.toLowerCase().indexOf(q)<0&&it.code.toLowerCase().indexOf(q)<0&&it.sym.toLowerCase().indexOf(q)<0) return;
    var inList=tkList.indexOf(it.sym)>=0;
    h+='<div class="tk-si'+(it.na?' na':'')+'"><span>'+it.nm+'<span class="mt">'+it.code+(it.na?' · 待接入':'')+'</span></span>'
      +(inList?'<span class="mt">已在横条</span>':'<span class="add" onclick="tkAdd(\''+it.sym+'\')">＋ 添加</span>')+'</div>';
    cnt++;
  });
  res.innerHTML=h||'<div class="tk-si"><span class="mt">无匹配（演示池 12 项；全市场搜索 I-2）</span></div>';
}
document.addEventListener('click',function(e){
  var l=document.getElementById('tk-slist');
  if(l&&l.classList.contains('open')&&!l.contains(e.target)&&e.target.id!=='tk-edit-btn') tkSrchShow(false);
});
function tkJump(sym){
  if(tkEdit) return;   /* 编辑态不跳转 */
  var it=tkFind(sym); if(!it||it.tgt==='none')return;
  if(it.tgt==='overseas'){ ovxGo('overseas',null); return; }
  if(it.tgt==='index'){
    var nav=null;
    document.querySelectorAll('.nav-item').forEach(function(n){ var oc=n.getAttribute('onclick')||''; if(oc.indexOf("go('index'")===0) nav=n; });
    if(nav) go('index',nav);
    var sels=document.querySelectorAll('.tech-sel');
    for(var i=0;i<sels.length;i++){ if(sels[i].getAttribute('data-sym')===it.sym){ techSwitch(it.sym,sels[i]); return; } }
    techSwitch(it.sym,null); return;
  }
  if(it.tgt==='stock'){ scrGoStock(it.code); return; }
}
function tkTglColl(){
  document.body.classList.toggle('tk-coll');
  var c=document.body.classList.contains('tk-coll');
  document.getElementById('tk-coll-btn').textContent=c?'▴':'▾';
  document.getElementById('tk-coll-btn').title=c?'展开横条':'折叠横条（只留时间）';
  try{localStorage.setItem('zk-tk-coll',c?'1':'0');}catch(e){}
}
function tkClockTick(){
  var d=new Date(),p=function(n){return String(n).padStart(2,'0');};
  var elc=document.getElementById('tk-clock'); if(elc) elc.textContent=p(d.getHours())+':'+p(d.getMinutes())+':'+p(d.getSeconds());
}
setInterval(tkClockTick,1000); tkClockTick();
if(localStorage.getItem('zk-tk-coll')==='1'){ document.body.classList.add('tk-coll'); var cb=document.getElementById('tk-coll-btn'); if(cb){cb.textContent='▴';cb.title='展开横条';} }
tkRender();
/* ==================== G-四.A 个股行情二级页引擎（sqXxx：左列表+K线滚轮缩放+指标窗格+筹码峰+事件时间线+报错+右资料面板） ==================== */
var SQ_POOL=[
 {sym:'600519',code:'600519.SH',nm:'贵州茅台',px:'1,712.50',pc:'+0.86%',dir:1},
 {sym:'300750',code:'300750.SZ',nm:'宁德时代',px:'289.40',pc:'-1.24%',dir:-1},
 {sym:'688981',code:'688981.SH',nm:'中芯国际',px:'99.20',pc:'+2.10%',dir:1},
 {sym:'600276',code:'600276.SH',nm:'恒瑞医药',px:'61.20',pc:'+0.45%',dir:1},
 {sym:'002594',code:'002594.SZ',nm:'比亚迪',px:'252.00',pc:'-0.62%',dir:-1},
 {sym:'601318',code:'601318.SH',nm:'中国平安',px:'48.35',pc:'+0.18%',dir:1}
];
var SQ_HOLD=['600519','300750','688981','600276','002594','601318'];   /* 与汇总持仓 3 账户同源 */
var STOCKQ_D={
 '600519':{nm:'贵州茅台',tags:['白酒','沪深300','上证50','中证A50'],intro:'中国白酒绝对龙头，飞天茅台为高端白酒定价锚；渠道库存去化节奏与批价韧性是核心跟踪变量。',
  l2:[[1720.00,12],[1718.50,8],[1716.00,21],[1714.50,15],[1713.00,33],[1712.00,42],[1711.50,26],[1710.00,51],[1708.50,18],[1706.00,29]],
  kv:[['最高','1,725.00'],['最低','1,698.00'],['开盘','1,701.00'],['昨收','1,698.00'],['量比','0.86'],['成交量','2.41 万手'],['成交额','41.2 亿'],['振幅','1.59%'],['换手','0.19%'],['涨停','1,867.80'],['跌停','1,528.20'],['市盈(静)','22.6'],['市盈TTM','21.8'],['总市值','2.15 万亿'],['总股本','12.56 亿'],['流通值','2.15 万亿'],['流通股','12.56 亿'],['外盘','1.28 万手'],['内盘','1.13 万手']],
  guxing:[['涨停成功次数(近一年)','1'],['涨停被砸次数','0'],['封板成功率','100%（1/1）'],['次日高开概率','62%'],['次日平均涨幅','+1.4%']],
  fin:[['ROE(TTM)','26.4%'],['毛利率','91.8%'],['净利率','52.1%'],['资产负债率','18.2%'],['商誉/净资产','0.00%'],['营收(一季)','514.4 亿 +10.7%'],['净利(一季)','268.5 亿 +11.6%'],['经营现金流','286.3 亿']],
  news:[['<b>白酒景气上行</b>：中秋备货批价企稳 2,300 元，渠道信心修复','正面 · 行业轮动信号同源'],['茅台 8 月配额投放节奏放缓，挺价意图明确','正面'],['北向连续 5 日增持茅台，累计 +18.6 亿','正面']],
  val:{t:'2,150.00',n:32,up:'+25.5%',note:'32 家机构一致预期（analyst_forecast 在库 1,628 行）'}},
 '300750':{nm:'宁德时代',tags:['新能源','创业板50','电池龙头'],intro:'全球动力电池市占率第一，麒麟/神行电池技术代差领先；跟踪排产、碳酸锂价格与海外产能落地。',
  l2:[[290.00,45],[289.80,62],[289.60,38],[289.40,74],[289.20,29],[289.00,88],[288.80,53],[288.50,41],[288.00,66],[287.50,37]],
  kv:[['最高','293.80'],['最低','286.20'],['开盘','292.50'],['昨收','293.00'],['量比','1.12'],['成交量','18.6 万手'],['成交额','53.8 亿'],['振幅','2.59%'],['换手','0.48%'],['涨停','351.60'],['跌停','234.40'],['市盈(静)','19.4'],['市盈TTM','18.1'],['总市值','1.27 万亿'],['总股本','44.0 亿'],['流通值','1.13 万亿'],['流通股','39.2 亿'],['外盘','9.2 万手'],['内盘','9.4 万手']],
  guxing:[['涨停成功次数(近一年)','2'],['涨停被砸次数','1'],['封板成功率','67%（2/3）'],['次日高开概率','55%'],['次日平均涨幅','+0.9%']],
  fin:[['ROE(TTM)','21.8%'],['毛利率','25.6%'],['净利率','12.4%'],['资产负债率','62.3%'],['商誉/净资产','0.8%'],['营收(一季)','797.7 亿 -10.4%'],['净利(一季)','105.1 亿 +7.0%'],['经营现金流','212.6 亿']],
  news:[['<b>触发移动止损线</b>：距止损 1.8%，风控已推送审批','风险 · 风控事件'],['神行 Pro 电池发布，4C 快充下放量','正面'],['碳酸锂价格再探 9 万/吨，成本端改善','正面']],
  val:{t:'328.00',n:28,up:'+13.3%',note:'28 家机构一致预期'}},
 '688981':{nm:'中芯国际',tags:['半导体','科创50','国产替代'],intro:'大陆晶圆代工龙头，成熟制程满载、先进制程爬坡；国产化率提升与设备招标是核心催化。',
  l2:[[99.50,120],[99.40,86],[99.30,95],[99.20,140],[99.10,72],[99.00,165],[98.90,98],[98.80,110],[98.60,88],[98.40,76]],
  kv:[['最高','100.20'],['最低','96.80'],['开盘','97.10'],['昨收','97.16'],['量比','1.45'],['成交量','96.2 万手'],['成交额','94.8 亿'],['振幅','3.50%'],['换手','1.21%'],['涨停','116.60'],['跌停','77.72'],['市盈(静)','88.2'],['市盈TTM','76.5'],['总市值','7,902 亿'],['总股本','79.6 亿'],['流通值','3,961 亿'],['流通股','39.9 亿'],['外盘','51.1 万手'],['内盘','45.1 万手']],
  guxing:[['涨停成功次数(近一年)','4'],['涨停被砸次数','2'],['封板成功率','67%（4/6）'],['次日高开概率','68%'],['次日平均涨幅','+2.1%']],
  fin:[['ROE(TTM)','4.2%'],['毛利率','21.5%'],['净利率','8.6%'],['资产负债率','35.1%'],['商誉/净资产','0.00%'],['营收(一季)','125.9 亿 +23.4%'],['净利(一季)','10.8 亿 +12.6%'],['经营现金流','48.2 亿']],
  news:[['<b>半导体设备国产化突破 40%</b>：招标放量，代工产能利用率 95%+','正面 · 主线候选'],['大基金三期拟减持 0.5 亿股','偏空 · 已在政策资金页登记'],['美实体清单新规影响有限（成熟制程为主）','中性']],
  val:{t:'112.00',n:25,up:'+12.9%',note:'25 家机构一致预期'}}
};
var SQ_EVENTS=[
 {dt:'08-26 20:30',tt:'核心PCE物价指数环比（美国）',ic:'📅',pub:'—',exp:'0.2%',prev:'0.1%',imp:'中性偏空',sec:'成长/科技承压，防御相对占优',ana:'预期高于前值=通胀黏性→美元偏强、北向风偏受抑；对 A 股中性偏空。对当前标的影响：外资重仓白马（茅台）受北向变量直接传导，成长股估值边际压制。'},
 {dt:'08-28 09:30',tt:'8 月官方制造业 PMI',ic:'📊',pub:'—',exp:'49.8',prev:'49.5',imp:'中性偏多',sec:'若重回荣枯线附近→顺周期/白酒消费链受益',ana:'预期小幅回升但仍处收缩区间；若超预期→复苏交易升温利好顺周期；不及预期→政策加码预期升温。对当前标的：消费白马看需求端验证。'},
 {dt:'09-01',tt:'宁德时代解禁 1.2 亿股',ic:'🔓',pub:'—',exp:'—',prev:'—',imp:'利空个股/中性板块',sec:'新能源链情绪承压，关注承接力度',ana:'解禁规模约 340 亿元（占流通 3.1%），历史规律：大额解禁前 5 日承压、落地日利空出尽概率高。对当前标的：若为宁德=直接利空；同板块其他标的情绪传导有限。'},
 {dt:'10-31',tt:'三季报披露截止',ic:'📑',pub:'—',exp:'—',prev:'—',imp:'个股分化',sec:'业绩兑现行情，警惕商誉/减值雷',ana:'三季报窗口=业绩验证期：白酒看渠道回款、新能源看排产、半导体看产能利用率。对当前标的：关注毛利率与现金流两个先行指标。'}
];
var sqCur='600519',sqListMode='fav',sqTf='日',sqWin=null,sqTogs={bs:true,cost:true,chip:true,grid:true},sqPanes=['vol','macd'];
var sqFav; try{ sqFav=JSON.parse(localStorage.getItem('zk-sq-fav')||'null')||['600519','300750','688981']; }catch(e){ sqFav=['600519','300750','688981']; }
var SQ_TFS=['分时','1分','5分','15分','30分','60分','日','周','月'];
var SQ_TFN={'分时':240,'1分':90,'5分':90,'15分':90,'30分':64,'60分':64,'日':120,'周':240,'月':240};
var SQ_PANE_NM={vol:'成交量 VOL',macd:'MACD(12,26,9)',kdj:'KDJ(9,3,3)'};
function sqPoolFind(sym){ for(var i=0;i<SQ_POOL.length;i++) if(SQ_POOL[i].sym===sym) return SQ_POOL[i]; return null; }
function sqData(){ return genCandles(+sqCur,240); }
function sqInit(){
  sqRenderList(); sqRenderAll();
  var mc=document.getElementById('sq-main-canvas');
  if(mc&&!mc.__sqBound){
    mc.__sqBound=1;
    mc.addEventListener('wheel',sqWheel,{passive:false});
    mc.addEventListener('mousedown',sqDragStart);   /* v3 拖拽平移 */
    window.addEventListener('mousemove',sqDragMove);
    window.addEventListener('mouseup',sqDragEnd);
    mc.addEventListener('dblclick',sqDblReset);   /* v3 双击复位 */
    mc.addEventListener('click',sqDrawClickCanvas,true);   /* v4 画线点击（capture=画线优先于事件弹层） */
  }
  sqDrawLoad();   /* v3.1：按股票+周期加载画线（localStorage 持久化，刷新不丢） */
  sqRenderMain();   /* v3.1：加载后补渲染（修复刷新后线条不上屏） */
}
function sqListTab(m){
  sqListMode=m;
  document.getElementById('sq-tab-fav').classList.toggle('on',m==='fav');
  document.getElementById('sq-tab-hold').classList.toggle('on',m==='hold');
  sqRenderList();
}
function sqRenderList(){
  var q=((document.getElementById('sq-srch')||{}).value||'').trim();
  var items=sqListMode==='fav'?sqFav:SQ_HOLD,h='';
  items.forEach(function(sym){
    var p=sqPoolFind(sym); if(!p)return;
    if(q&&p.nm.indexOf(q)<0&&p.code.indexOf(q)<0) return;
    h+='<div class="sq-si'+(sym===sqCur?' on':'')+'" onclick="sqSel(\''+sym+'\')"><span><span class="nm">'+p.nm+'</span> <span class="cd">'+p.code+'</span></span>'
      +'<span class="rt"><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><br><span class="pc '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></span>'
      +(sqListMode==='fav'?'<span class="fav" onclick="event.stopPropagation();sqFavRm(\''+sym+'\')" title="移出自选">★</span>':'')+'</div>';
  });
  document.getElementById('sq-list').innerHTML=h||'<div class="sq-intro">清单为空或无匹配</div>';
}
function sqFavRm(sym){
  sqFav=sqFav.filter(function(s){return s!==sym;});
  try{localStorage.setItem('zk-sq-fav',JSON.stringify(sqFav));}catch(e){}
  sqRenderList();
}
function sqSel(sym){ sqCur=sym; sqWin=null; sqRenderList(); sqRenderAll(); }
function sqTfSet(tf,elm){
  sqTf=tf; sqWin=null; sqDrawLoad();   /* v3.1：切周期重载画线 */
  document.querySelectorAll('#sq-head .sq-tfs .tab').forEach(function(t){t.classList.remove('on');});
  if(elm)elm.classList.add('on');
  sqRenderMain(); sqRenderPanes();
}
function sqTogTgl(k){ sqTogs[k]=!sqTogs[k]; sqRenderHead(); sqRenderMain(); sqRenderPanes(); }
function sqRenderAll(){ sqRenderHead(); sqRenderMain(); sqRenderPanes(); sqRenderEvents(); sqRenderInfo(); }
function sqRenderHead(){
  var p=sqPoolFind(sqCur),d=STOCKQ_D[sqCur];
  var h='<span class="nm">'+(d?d.nm:p.nm)+'</span><span class="cd">'+p.code+(d?'':'（资料待接入）')+'</span>'
    +'<span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><span class="chg '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span>'
    +'<span class="sq-tfs">'+SQ_TFS.map(function(t){return '<span class="tab'+(t===sqTf?' on':'')+'" onclick="sqTfSet(\''+t+'\',this)">'+t+'</span>';}).join('')+'</span>'
    +'<span class="sq-togs">'
    +'<span class="sq-tog'+(sqTogs.bs?' on':'')+'" onclick="sqTogTgl(\'bs\')">买卖点</span>'
    +'<span class="sq-tog'+(sqTogs.cost?' on':'')+'" onclick="sqTogTgl(\'cost\')">成本线</span>'
    +'<span class="sq-tog'+(sqTogs.chip?' on':'')+'" onclick="sqTogTgl(\'chip\')">筹码峰</span>'
    +'<span class="sq-tog'+(sqTogs.grid?' on':'')+'" onclick="sqTogTgl(\'grid\')">网格</span>'
    +'<span class="sq-tog" style="border-left:1px solid var(--border);margin-left:2px;padding-left:6px"></span>'
    +'<span class="sq-tog sq-draw-tog'+(sqDraw.mode==='trend'?' on':'')+'" title="趋势线：点两点拉一条线" onclick="sqDrawSet(\'trend\')">╱趋势线</span>'
    +'<span class="sq-tog sq-draw-tog'+(sqDraw.mode==='hline'?' on':'')+'" title="水平线：点一下定价位" onclick="sqDrawSet(\'hline\')">─水平</span>'
    +'<span class="sq-tog sq-draw-tog'+(sqDraw.mode==='rect'?' on':'')+'" title="矩形区间：点两角画框" onclick="sqDrawSet(\'rect\')">▭矩形</span>'
    +(sqDraw.items.length?'<span class="sq-tog" title="清空全部画线" onclick="sqDrawClear()">🗑</span>':'')
    +'<span class="sq-fb" onclick="fbReport(\'bs\',\'买卖点信号（'+p.nm+'）\',this)">⚑报错</span></span>';
  document.getElementById('sq-head').innerHTML=h;
}
function sqWinGet(){
  var d=sqData(),n=SQ_TFN[sqTf]||120;
  if(!sqWin) sqWin={hi:d.length,lo:Math.max(0,d.length-n)};
  var cnt=sqWin.hi-sqWin.lo;
  if(cnt>240) sqWin.lo=sqWin.hi-240;
  if(cnt<20) sqWin.lo=Math.max(0,sqWin.hi-20);
  /* v3.1：右边界放开至 d.length+FS_MAX（允许拖进未来空白区看未来事件/画线），左边界仍≥0 */
  var FS_MAX=120;
  if(sqWin.hi>d.length+FS_MAX){ sqWin.hi=d.length+FS_MAX; sqWin.lo=sqWin.hi-cnt; }
  return sqWin;
}
function sqWheel(e){
  e.preventDefault();
  var d=sqData(),w=sqWinGet(),cnt=w.hi-w.lo;
  var mc=document.getElementById('sq-main-canvas'),r=mc.getBoundingClientRect();
  if(!r.width)return;   /* v4：canvas 防御（隐藏页 rect.width=0） */
  var fx=Math.max(0.02,Math.min(0.98,(e.clientX-r.left)/r.width));
  var dir=e.deltaY>0?1:-1;
  var ncnt=Math.round(cnt*(dir>0?0.8:1.25));   /* 滚轮下=放大（窗口变窄）、上=缩小（窗口变宽），OKX 方向 */
  ncnt=Math.max(20,Math.min(240,ncnt));
  var anchor=w.lo+fx*cnt,nlo=Math.round(anchor-fx*ncnt);
  nlo=Math.max(0,Math.min(d.length-ncnt,nlo));
  sqWin={lo:nlo,hi:nlo+ncnt};
  sqRenderMain(); sqRenderPanes();
}
/* v3 缩放交互全套补件：拖拽平移（按住图表区左右拖）+双击复位——OKX 式无过渡动画 */
var sqDrag=null;
function sqDragStart(e){
  if(e.button!==0)return;
  sqDrag={x:e.clientX,w:sqWinGet()};
  e.preventDefault();
}
function sqDragMove(e){
  if(!sqDrag)return;
  var mc=document.getElementById('sq-main-canvas'),r=mc.getBoundingClientRect();
  if(!r.width)return;   /* v4：canvas 防御 */
  var d=sqData(),cnt=sqDrag.w.hi-sqDrag.w.lo;
  var perPx=cnt/Math.max(1,r.width);   /* 每像素对应 K 线根数 */
  var dj=-Math.round((e.clientX-sqDrag.x)*perPx);   /* 右拖=看历史（窗口左移），OKX 方向 */
  var nlo=Math.max(0,Math.min(d.length-cnt+120,sqDrag.w.lo+dj));   /* v3.1：右边界放开至数据末+120（未来空白区可拖入） */
  if(nlo!==sqWin.lo){ sqWin={lo:nlo,hi:nlo+cnt}; sqRenderMain(); sqRenderPanes(); }
}
function sqDragEnd(){ sqDrag=null; }
function sqDblReset(e){
  var d=sqData(),n=SQ_TFN[sqTf]||120;
  sqWin={hi:d.length,lo:Math.max(0,d.length-n)};
  sqRenderMain(); sqRenderPanes();
}
/* ==================== v3.1 画线工具（趋势线/水平线/矩形，localStorage 按股票持久化，刷新不丢） ==================== */
var sqDraw={mode:null,items:[],pend:null};   /* pend=第一点待定 */
function sqDrawKey(){ return 'zk-draw-'+sqCur+'-'+sqTf; }
function sqDrawLoad(){
  try{ sqDraw.items=JSON.parse(localStorage.getItem(sqDrawKey())||'[]'); }catch(e){ sqDraw.items=[]; }
  sqDraw.pend=null;
}
function sqDrawSave(){ try{ localStorage.setItem(sqDrawKey(),JSON.stringify(sqDraw.items)); }catch(e){} }
function sqDrawSet(m){
  sqDraw.mode=(sqDraw.mode===m)?null:m; sqDraw.pend=null;
  sqRenderHead();   /* 刷新按钮高亮 */
}
function sqDrawClear(){ sqDraw.items=[]; sqDraw.pend=null; sqDrawSave(); sqRenderHead(); sqRenderMain(); }
/* v4 画线渲染（canvas 主层）：数据坐标→像素，随窗口/缩放联动 */
function sqDrawRenderCanvas(ctx,x,yf,slotW,n,w,d,L2,R2){
  sqDraw.items.forEach(function(it){
    var pts=it.pts;
    if(it.type==='hline'){
      var y=yf(pts[0][1]);
      ctx.strokeStyle='#F0B90B'; ctx.lineWidth=1; ctx.setLineDash([6,4]);
      ctx.beginPath(); ctx.moveTo(L2,y); ctx.lineTo(R2,y); ctx.stroke(); ctx.setLineDash([]);
    }else if(it.type==='trend'){
      var x1=x(pts[0][0]-w.lo)+slotW*0.31, y1=yf(pts[0][1]), x2=x(pts[1][0]-w.lo)+slotW*0.31, y2=yf(pts[1][1]);
      ctx.strokeStyle='#3D8BFF'; ctx.lineWidth=1.2;
      ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    }else if(it.type==='rect'){
      var rx1=x(pts[0][0]-w.lo)+slotW*0.31, ry1=yf(pts[0][1]), rx2=x(pts[1][0]-w.lo)+slotW*0.31, ry2=yf(pts[1][1]);
      ctx.fillStyle='rgba(61,139,255,0.08)'; ctx.fillRect(Math.min(rx1,rx2),Math.min(ry1,ry2),Math.abs(rx2-rx1),Math.abs(ry2-ry1));
      ctx.strokeStyle='#3D8BFF'; ctx.lineWidth=1; ctx.setLineDash([4,3]);
      ctx.strokeRect(Math.min(rx1,rx2),Math.min(ry1,ry2),Math.abs(rx2-rx1),Math.abs(ry2-ry1)); ctx.setLineDash([]);
    }
  });
}
/* v4 画线点击（canvas 坐标拾取）：canvas 无节点，用 getBoundingClientRect 换算 */
function sqDrawClickCanvas(e){
  if(!sqDraw.mode) return;
  e.stopPropagation(); e.preventDefault();
  var mc=document.getElementById('sq-main-canvas'),r=mc.getBoundingClientRect();
  var W=1100,L=46,R=sqTogs.chip?150:64;
  var d=sqData(),w=sqWinGet(),n=w.hi-w.lo,slotW=(W-L-R)/(n+12);
  var m20=sqMAArr(d,20),lo=1e18,hi=-1e18,i;
  var hiEff2=Math.min(w.hi,d.length);
  for(i=w.lo;i<hiEff2;i++){ lo=Math.min(lo,d[i].l,m20[i]); hi=Math.max(hi,d[i].h,m20[i]); }
  var pad=(hi-lo)*0.08; lo-=pad; hi+=pad;
  var T=14,H=460,B=30;
  var fx=(e.clientX-r.left)/r.width*W, fy=(e.clientY-r.top)/r.height*H;
  var gi=Math.max(0,Math.min(d.length-1+12,Math.round((fx-L)/slotW+w.lo)));
  var px=lo+(1-(fy-T)/(H-T-B))*(hi-lo);
  var pt=[gi,Math.round(px*100)/100];
  if(sqDraw.mode==='hline'){ sqDraw.items.push({type:'hline',pts:[pt]}); sqDrawSave(); sqDraw.pend=null; }
  else if(sqDraw.mode==='trend'||sqDraw.mode==='rect'){
    if(!sqDraw.pend){ sqDraw.pend=pt; }
    else{ sqDraw.items.push({type:sqDraw.mode,pts:[sqDraw.pend,pt]}); sqDrawSave(); sqDraw.pend=null; }
  }
  sqRenderMain();
}
/* 渲染已存画线（数据坐标→像素，随窗口/缩放联动）；L2/R2=蜡烛区左右界（显式传入，不依赖外部作用域） */
function sqDrawRender(g,x,yf,slotW,n,w,d,L2,R2){
  sqDraw.items.forEach(function(it){
    var pts=it.pts;
    if(it.type==='hline'){
      var y=yf(pts[0][1]);
      el('line',{x1:L2,x2:R2,y1:y,y2:y,stroke:'#F0B90B','stroke-width':1,'stroke-dasharray':'6 4'},g);
    }else if(it.type==='trend'){
      var x1=x(pts[0][0]-w.lo)+slotW*0.31, y1=yf(pts[0][1]), x2=x(pts[1][0]-w.lo)+slotW*0.31, y2=yf(pts[1][1]);
      el('line',{x1:x1,y1:y1,x2:x2,y2:y2,stroke:'#3D8BFF','stroke-width':1.2},g);
    }else if(it.type==='rect'){
      var rx1=x(pts[0][0]-w.lo)+slotW*0.31, ry1=yf(pts[0][1]), rx2=x(pts[1][0]-w.lo)+slotW*0.31, ry2=yf(pts[1][1]);
      el('rect',{x:Math.min(rx1,rx2),y:Math.min(ry1,ry2),width:Math.abs(rx2-rx1),height:Math.abs(ry2-ry1),fill:'rgba(61,139,255,0.08)',stroke:'#3D8BFF','stroke-width':1,'stroke-dasharray':'4 3'},g);
    }
  });
}
/* 画线点击（蜡烛模式下）：数据坐标拾取 */
function sqDrawClick(e){
  if(!sqDraw.mode) return;
  e.stopPropagation(); e.preventDefault();
  var svg=document.getElementById('sq-main'),r=svg.getBoundingClientRect();
  var W=1100,L=46,R=sqTogs.chip?150:64;
  var d=sqData(),w=sqWinGet(),n=w.hi-w.lo,slotW=(W-L-R)/(n+12);
  var m20=sqMAArr(d,20),lo=1e18,hi=-1e18,i;
  var hiEff2=Math.min(w.hi,d.length);   /* v3.1：画线拾取 lo/hi 只算有效数据段 */
  for(i=w.lo;i<hiEff2;i++){ lo=Math.min(lo,d[i].l,m20[i]); hi=Math.max(hi,d[i].h,m20[i]); }
  var pad=(hi-lo)*0.08; lo-=pad; hi+=pad;
  var T=14,H=460,B=30;
  var fx=(e.clientX-r.left)/r.width*W, fy=(e.clientY-r.top)/r.height*H;
  var gi=Math.max(0,Math.min(d.length-1+12,Math.round((fx-L)/slotW+w.lo)));   /* 允许未来空槽索引 */
  var px=lo+(1-(fy-T)/(H-T-B))*(hi-lo);
  var pt=[gi,Math.round(px*100)/100];
  if(sqDraw.mode==='hline'){ sqDraw.items.push({type:'hline',pts:[pt]}); sqDrawSave(); sqDraw.pend=null; }
  else if(sqDraw.mode==='trend'||sqDraw.mode==='rect'){
    if(!sqDraw.pend){ sqDraw.pend=pt; }
    else{ sqDraw.items.push({type:sqDraw.mode,pts:[sqDraw.pend,pt]}); sqDrawSave(); sqDraw.pend=null; }
  }
  sqRenderMain();
}
function sqMAArr(d,p){   /* 简单均线数组版（页面全局 ma(d,n,i) 为逐点标量，四.A 需要全序列） */
  var r=[],s=0,i;
  for(i=0;i<d.length;i++){ s+=d[i].c; if(i>=p)s-=d[i-p].c; r.push(i>=p-1?s/p:s/(i+1)); }
  return r;
}
function sqEMA(arr,p){ var k=2/(p+1),r=[],v=arr[0]; for(var i=0;i<arr.length;i++){ v=i?arr[i]*k+v*(1-k):arr[i]; r.push(v); } return r; }
function sqMACD(d){ var c=d.map(function(x){return x.c;}),e12=sqEMA(c,12),e26=sqEMA(c,26),dif=c.map(function(v,i){return e12[i]-e26[i];}),dea=sqEMA(dif,9),h=dif.map(function(v,i){return (v-dea[i])*2;}); return {dif:dif,dea:dea,hist:h}; }
function sqKDJ(d){ var n=9,K=[],D=[],J=[],k=50,dd=50; for(var i=0;i<d.length;i++){ var lo=1e18,hi=-1e18; for(var j=Math.max(0,i-n+1);j<=i;j++){ lo=Math.min(lo,d[j].l); hi=Math.max(hi,d[j].h); } var rsv=hi>lo?(d[i].c-lo)/(hi-lo)*100:50; k=2/3*k+1/3*rsv; dd=2/3*dd+1/3*k; K.push(k); D.push(dd); J.push(3*k-2*dd); } return {K:K,D:D,J:J}; }
function sqBS(d){   /* 买卖点（演示口径：±3 根摆动高低点；与技术分析页信号族同构，真源 I-2） */
  var r=[],i,j;
  for(i=3;i<d.length-3;i++){
    var isLo=true,isHi=true;
    for(j=i-3;j<=i+3;j++){ if(j===i)continue; if(d[j].l<d[i].l)isLo=false; if(d[j].h>d[i].h)isHi=false; }
    if(isLo) r.push({i:i,dir:1});
    else if(isHi) r.push({i:i,dir:-1});
  }
  return r;
}
/* ==================== K线工作台 v2（Owner 2026-08-27 拍板一批全做：OKX 审美骨架+同花顺功能增量） ====================
   双轴（左%右价）/日期轴事件图标+OKX 弹层/新闻双日期（披露日📰+兑现日📅）/高低点标注/量均线/分时模式/筹码峰美化 */
var SQ_EVX=[   /* 事件数据（演示口径；pub=披露日 evt=兑现日——新闻双日期规则：pub 与 evt 都出图标） */
  {pub:'08-21',evt:'08-21',ti:'宁德时代 2026 三季报',type:'fin',a:'净利润 148 亿',f:'预期 135 亿',p:'前值 122 亿'},
  {pub:'08-22',evt:'08-28',ti:'美联储议息纪要（外盘）',type:'macro',a:'待公布',f:'预期 偏鹰',p:'前值 维持利率'},
  {pub:'07-28',evt:'08-01',ti:'华为发布新车（智界 R7 增程版 · 宁德电池供应）',type:'news',a:'已兑现',f:'-',p:'-'},
  {pub:'08-25',evt:'08-25',ti:'限售解禁 1.2 亿股（占总股本 3.1%）',type:'funds',a:'已解禁',f:'-',p:'-'},
  {pub:'08-26',evt:'09-04',ti:'美国 8 月非农就业人数',type:'macro',a:'待公布',f:'预期 +75K',p:'前值 -23K'}
];
var SQ_EVIC={fin:'📑',macro:'📅',news:'📰',funds:'💲'};
function sqDates(d){   /* 合成日期轴（演示口径：以 2026-08-27 为末日向前推日历日，格式 MM-DD） */
  var end=new Date(2026,7,27),r=[];
  for(var i=0;i<d.length;i++){ var dt=new Date(end); dt.setDate(end.getDate()-(d.length-1-i)); r.push(String(dt.getMonth()+1).padStart(2,'0')+'-'+String(dt.getDate()).padStart(2,'0')); }
  return r;
}
function sqTickData(){   /* 分时 240 分钟合成序列（种子确定性；演示口径） */
  if(sqTickData.__c&&sqTickData.__c.k===sqCur) return sqTickData.__c;
  var r=lcg(+sqCur*31+7),px=[],vol=[],p=sqPoolFind(sqCur);
  var pxNum=parseFloat(String(p.px).replace(/,/g,'')),pcNum=parseFloat(String(p.pc))||0;   /* px 为千分位字符串须先数字化（v2 复验抓出 NaN 连锁崩溃） */
  var v=pxNum*(1-pcNum/100*0.4);
  for(var i=0;i<240;i++){ v+=(r()-0.49)*v*0.0035; px.push(v); vol.push(120+Math.floor(r()*680)); }
  px[239]=pxNum;
  var out={px:px,vol:vol,k:sqCur}; sqTickData.__c=out; return out;
}
function sqRenderMain(){
  /* v4 canvas 分层：主层 canvas=数据图形，DOM 覆盖层=tooltip/事件轴/画线 */
  var stack=document.getElementById('sq-canvas-stack'); if(!stack)return;
  var mc=document.getElementById('sq-main-canvas'), cc=document.getElementById('sq-cross-canvas'), ov=document.getElementById('sq-dom-overlay');
  if(!mc||!cc||!ov) return;
  var W=1100,H=460,L=46,R=sqTogs.chip?150:64,T=14,B=30;
  var dpr=window.devicePixelRatio||1;
  mc.width=W*dpr; mc.height=H*dpr; mc.style.width='100%'; mc.style.height='100%';
  cc.width=W*dpr; cc.height=H*dpr; cc.style.width='100%'; cc.style.height='100%';
  var ctx=mc.getContext('2d'); ctx.scale(dpr,dpr); ctx.clearRect(0,0,W,H);
  var CW_RATIO=0.78, CW_MIN=2.5, CW_MAX=26, FS_MAX=120;   /* v3.1：蜡烛体宽绝对像素夹紧（缩放不变形）+ 未来空槽上限 */
  var d=sqData(),w=sqWinGet(),n=w.hi-w.lo,win=d.slice(w.lo,w.hi);
  /* v3.2：FS 动态化——窗口右缘贴数据末时未来空槽=12，右拖进未来区时空槽随 hi 扩展；滚轮缩放时收窄到 2 格（放大不留白） */
  var FSeff=Math.max(2, Math.min(FS_MAX, w.hi-d.length+12));
  var slotW=(W-L-R)/(n+FSeff);
  var x=function(j){ return L+j*slotW; };
  var cwEff=Math.max(CW_MIN,Math.min(CW_MAX,slotW*CW_RATIO));   /* v3.1：体宽绝对夹紧——放大不再变细 */
  var dates=sqDates(d);
  /* ---------- 分时模式（v4 canvas：同花顺功能增量） ---------- */
  if(sqTf==='分时'){
    var tk=sqTickData(),tp=tk.px,tn=240;
    var p0=sqPoolFind(sqCur),prev=tp[0],tlo=Math.min.apply(null,tp),thi=Math.max.apply(null,tp),tpd=(thi-tlo)*0.12; tlo-=tpd; thi+=tpd;
    var ty=function(v){ return T+(1-(v-tlo)/(thi-tlo))*(H-T-B); };
    var tx=function(j){ return L+j*(W-L-R)/(tn-1); };
    /* 网格（v4 canvas） */
    if(sqTogs.grid){
      ctx.strokeStyle='#171717'; ctx.lineWidth=1;
      var vSteps=5;
      for(var vi=0;vi<=vSteps;vi++){ var vy=T+vi*(H-T-B)/vSteps; ctx.beginPath(); ctx.moveTo(L,vy); ctx.lineTo(W-R,vy); ctx.stroke(); }
      var hSteps=Math.ceil(tn/7);
      for(var hi2=0;hi2<=hSteps;hi2++){ var hx=L+hi2*(W-L-R)/hSteps; ctx.beginPath(); ctx.moveTo(hx,T); ctx.lineTo(hx,H-B); ctx.stroke(); }
    }
    /* 昨收参考线 */
    ctx.strokeStyle='#59626D'; ctx.lineWidth=0.8; ctx.setLineDash([4,3]);
    ctx.beginPath(); ctx.moveTo(L,ty(prev)); ctx.lineTo(W-R,ty(prev)); ctx.stroke(); ctx.setLineDash([]);
    var avg=[],asum=0; for(var ai=0;ai<tn;ai++){ asum+=tp[ai]; avg.push(asum/(ai+1)); }
    /* 面积微渐变（刻意超越包） */
    var grad=ctx.createLinearGradient(0,T,0,H-B);
    grad.addColorStop(0,'rgba(237,239,242,0.12)'); grad.addColorStop(1,'rgba(237,239,242,0)');
    ctx.fillStyle=grad; ctx.beginPath();
    ctx.moveTo(tx(0),ty(tlo));
    for(var ai2=0;ai2<tn;ai2++) ctx.lineTo(tx(ai2),ty(tp[ai2]));
    ctx.lineTo(tx(tn-1),ty(tlo)); ctx.closePath(); ctx.fill();
    /* 白线价+黄均价 */
    ctx.strokeStyle='#EDEFF2'; ctx.lineWidth=1.5; ctx.beginPath();
    for(var ai3=0;ai3<tn;ai3++){ var px3=tx(ai3),py3=ty(tp[ai3]); if(ai3===0)ctx.moveTo(px3,py3);else ctx.lineTo(px3,py3); }
    ctx.stroke();
    ctx.strokeStyle='#F0B90B'; ctx.lineWidth=1.2; ctx.beginPath();
    for(var ai4=0;ai4<tn;ai4++){ var px4=tx(ai4),py4=ty(avg[ai4]); if(ai4===0)ctx.moveTo(px4,py4);else ctx.lineTo(px4,py4); }
    ctx.stroke();
    /* 双轴：右价左%（v4 canvas fillText） */
    ctx.font='12px OKXSans'; ctx.textAlign='left';
    for(var ti2=0;ti2<=4;ti2++){
      var tv=tlo+(thi-tlo)*ti2/4,tyy=ty(tv);
      ctx.fillStyle='#C6C6C6'; ctx.fillText(tv.toFixed(2),W-R+6,tyy+3);
      var pc2=(tv-prev)/prev*100;
      ctx.fillStyle=pc2>=0?'#CA3F64':'#25A750'; ctx.textAlign='right'; ctx.fillText((pc2>=0?'+':'')+pc2.toFixed(2)+'%',L-5,tyy+3); ctx.textAlign='left';
    }
    /* 当前价色签（v4 canvas） */
    var lc=tp[tn-1],lup=lc>=prev;
    ctx.fillStyle=lup?'#CA3F64':'#25A750'; ctx.fillRect(W-R+2,ty(lc)-9,58,17);
    ctx.fillStyle='#000000'; ctx.font='11px OKXSans'; ctx.fillText(lc.toFixed(2),W-R+7,ty(lc)+3);
    /* 时间轴（09:30/10:30/11:30/13:00/14:00/15:00） */
    ctx.fillStyle='#59626D'; ctx.font='10px OKXSans';
    ['09:30','10:30','11:30/13:00','14:00','15:00'].forEach(function(tk2,k2){
      var xi=[0,60,120,180,239][k2];
      ctx.fillText(tk2,Math.max(L,tx(xi)-14),H-8);
    });
    /* 高低点标注 */
    var hiI=tp.indexOf(thi-tpd),loI=tp.indexOf(tlo+tpd);
    ctx.fillStyle='#A0A6AD'; ctx.font='10px OKXSans';
    ctx.fillText((thi-tpd).toFixed(2)+' →',Math.min(tx(hiI)+6,W-R-64),ty(thi-tpd)-4);
    ctx.fillText((tlo+tpd).toFixed(2)+' →',Math.min(tx(loI)+6,W-R-64),ty(tlo+tpd)+12);
    /* hover 十字读数（v4 canvas） */
    bindHoverCanvas(mc,cc,ov,{W:W,L:L,R:R,H:H-B,T:T,B:0,n:tn,x:tx,cw:(W-L-R)/tn,d:null,w:null,dates:null,m20:null,readout:function(j){
      return '分时  价 '+tp[j].toFixed(2)+'  均 '+avg[j].toFixed(2)+'  量 '+tk.vol[j];
    }});
    return;
  }
  /* ---------- 蜡烛模式（v4 canvas 主层） ---------- */
  var m20=sqMAArr(d,20),lo=1e18,hi=-1e18,i;
  var hiEff=Math.min(w.hi,d.length);   /* v3.1：窗口越未来区时，lo/hi 只算有效数据段 */
  for(i=w.lo;i<hiEff;i++){ lo=Math.min(lo,d[i].l,m20[i]); hi=Math.max(hi,d[i].h,m20[i]); }
  var pad=(hi-lo)*0.08; lo-=pad; hi+=pad;
  var yf=function(v){ return T+(1-(v-lo)/(hi-lo))*(H-T-B); };
  /* 网格（v4 canvas） */
  if(sqTogs.grid){
    ctx.strokeStyle='#171717'; ctx.lineWidth=1;
    var vSteps=(n+FSeff)>120?7:((n+FSeff)>60?6:5);
    for(var vi=0;vi<=vSteps;vi++){ var vy=T+vi*(H-T-B)/vSteps; ctx.beginPath(); ctx.moveTo(L,vy); ctx.lineTo(W-R,vy); ctx.stroke(); }
    var hSteps=Math.ceil((n+FSeff)/7);
    for(var hi2=0;hi2<=hSteps;hi2++){ var hx=L+hi2*(W-L-R)/hSteps; ctx.beginPath(); ctx.moveTo(hx,T); ctx.lineTo(hx,H-B); ctx.stroke(); }
  }
  /* 蜡烛（v4 canvas） */
  win.forEach(function(k,j){
    var up=k.c>=k.o, col=up?'#CA3F64':'#25A750';
    var cx=x(j)+cwEff/2;
    ctx.strokeStyle=col; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(cx,yf(k.h)); ctx.lineTo(cx,yf(k.l)); ctx.stroke();
    ctx.fillStyle=col; ctx.fillRect(x(j),yf(Math.max(k.o,k.c)),cwEff,Math.max(1.5,Math.abs(yf(k.o)-yf(k.c))));
  });
  /* MA 三线（v4 canvas） */
  var mset=[[5,'#FFA726'],[10,'#EC407A'],[20,'#27C6DA']];
  mset.forEach(function(m){
    var arr=sqMAArr(d,m[0]);
    ctx.strokeStyle=m[1]; ctx.lineWidth=1.3; ctx.beginPath();
    var first=true;
    for(var j=0;j<n;j++){ var gi3=w.lo+j; if(gi3>=d.length) continue; var px=x(j)+slotW*0.31,py=yf(arr[gi3]); if(first){ctx.moveTo(px,py);first=false;}else ctx.lineTo(px,py); }
    ctx.stroke();
  });
  /* 成本线（v4 canvas） */
  if(sqTogs.cost){
    var avg2=0; for(i=w.lo;i<hiEff;i++) avg2+=d[i].c; avg2/=Math.max(1,hiEff-w.lo);
    ctx.strokeStyle='#F0B90B'; ctx.lineWidth=1.2; ctx.setLineDash([6,4]);
    ctx.beginPath(); ctx.moveTo(L,yf(avg2)); ctx.lineTo(W-R,yf(avg2)); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle='#F0B90B'; ctx.font='11px OKXSans'; ctx.fillText('成本 '+avg2.toFixed(2),W-R-58,yf(avg2)-6);
  }
  /* 买卖点（v4 canvas） */
  if(sqTogs.bs){
    sqBS(d).forEach(function(s){
      if(s.i<w.lo||s.i>=hiEff) return;
      var j=s.i-w.lo;
      ctx.font='12px OKXSans'; ctx.fillStyle=s.dir===1?'#CA3F64':'#25A750';
      ctx.fillText(s.dir===1?'▲买':'▼卖',x(j)-16,s.dir===1?yf(d[s.i].l)+26:yf(d[s.i].h)-20);
    });
  }
  /* 高低点标注（v4 canvas） */
  var i0=Math.min(w.lo,d.length-1),hiK=d[i0],loK=d[i0],hiJ=0,loJ=0;
  for(i=0;i<hiEff-w.lo;i++){ var kk=d[w.lo+i]; if(kk.h>hiK.h){hiK=kk;hiJ=i;} if(kk.l<loK.l){loK=kk;loJ=i;} }
  ctx.fillStyle='#A0A6AD'; ctx.beginPath(); ctx.arc(x(hiJ)+slotW*0.31,yf(hiK.h),2,0,7); ctx.fill();
  ctx.font='10px OKXSans'; ctx.fillText(hiK.h.toFixed(2)+' →',Math.min(x(hiJ)+slotW*0.62+4,W-R-64),yf(hiK.h)+3);
  ctx.beginPath(); ctx.arc(x(loJ)+slotW*0.31,yf(loK.l),2,0,7); ctx.fill();
  ctx.fillText(loK.l.toFixed(2)+' →',Math.min(x(loJ)+slotW*0.62+4,W-R-64),yf(loK.l)+3);
  /* 双轴（v4 canvas fillText） */
  var base=d[Math.min(w.lo,d.length-1)].c;
  ctx.font='12px OKXSans'; ctx.textAlign='left';
  for(var tk3=0;tk3<=4;tk3++){
    var tv3=lo+(hi-lo)*tk3/4,ty3=yf(tv3);
    ctx.fillStyle='#C6C6C6'; ctx.fillText(tv3.toFixed(2),W-R+6,ty3+3);
    var pc3=(tv3-base)/base*100;
    ctx.fillStyle=pc3>=0?'#CA3F64':'#25A750'; ctx.textAlign='right'; ctx.fillText((pc3>=0?'+':'')+pc3.toFixed(1)+'%',L-6,ty3+3); ctx.textAlign='left';
  }
  /* 当前价色签（v4 canvas） */
  var lastC2=d[Math.min(w.hi,d.length)-1].c,p2=sqPoolFind(sqCur),lup2=p2.dir>=0;
  ctx.strokeStyle=lup2?'#CA3F64':'#25A750'; ctx.lineWidth=1.2; ctx.setLineDash([2,3]); ctx.globalAlpha=0.5;
  ctx.beginPath(); ctx.moveTo(L,yf(lastC2)); ctx.lineTo(W-R,yf(lastC2)); ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha=1;
  ctx.fillStyle=lup2?'#CA3F64':'#25A750'; ctx.fillRect(W-R+2,yf(lastC2)-9,58,17);
  ctx.fillStyle='#000000'; ctx.font='11px OKXSans'; ctx.fillText(lastC2.toFixed(2),W-R+7,yf(lastC2)+3);
  ctx.fillStyle='#59626D'; ctx.font='9px OKXSans'; ctx.fillText('--:--',W-R+7,yf(lastC2)+20);
  /* 筹码峰 v4 canvas 主层绘制：60 桶、每价位一根柱单色（现价下获利红/上套牢绿）、成本线=琥珀、随光标重算 */
  if(sqTogs.chip){
    var NB=60,bw2=(hi-lo)/NB;
    var chipX=W-R+66,chipW=Math.min(64,(W-R)*0.5);
    function renderChip(uptoGi,refPx){
      ctx.save();
      var binsD=[],bi;
      for(i=0;i<NB;i++) binsD.push(0);
      var st=Math.max(0,Math.min(uptoGi,d.length-1));
      for(i=w.lo;i<=st;i++){ if(i>=d.length)break; var tp3=(d[i].h+d[i].l+d[i].c)/3; bi=Math.floor((tp3-lo)/bw2); if(bi<0)bi=0; if(bi>=NB)bi=NB-1; binsD[bi]+=d[i].v; }
      var bins=binsD, bmax2=Math.max.apply(null,bins),poc2=0;
      for(i=0;i<NB;i++) if(bins[i]>bins[poc2]) poc2=i;
      var pocPx=lo+(poc2+0.5)*bw2,prof=0;
      for(i=poc2;i<NB;i++) prof+=bins[i];
      var totV=bins.reduce(function(a2,b2){return a2+b2;},0);
      for(i=0;i<NB;i++){
        if(bins[i]<=0) continue;
        var binPx=lo+(i+0.5)*bw2, isProfit=binPx<=refPx;
        var bwW3=(bins[i]/bmax2)*chipW, yy2=yf(lo+(i+1)*bw2), hh2=Math.max(1.2,(H-T-B)/NB-0.5);
        ctx.fillStyle=isProfit?'#CA3F64':'#25A750'; ctx.globalAlpha=0.5;
        ctx.fillRect(chipX,yy2,Math.max(1,bwW3),hh2);
      }
      ctx.globalAlpha=1;
      ctx.strokeStyle='#F0B90B'; ctx.lineWidth=1.2;
      ctx.beginPath(); ctx.moveTo(chipX-2,yf(pocPx)); ctx.lineTo(chipX+chipW,yf(pocPx)); ctx.stroke();
      ctx.fillStyle='#8B949E'; ctx.font='9px OKXSans';
      ctx.fillText(totV>0?('获利 '+(prof/totV*100).toFixed(0)+'%'):'获利 —',chipX,T+2);
      ctx.fillStyle='#F0B90B'; ctx.fillText('成本 '+pocPx.toFixed(2),chipX,T+14);
      ctx.restore();
    }
    renderChip(Math.min(w.hi,d.length)-1, lastC2);
    /* v4：canvas 无节点，光标联动改由 sq-main-canvas 的 mousemove 触发 renderChip 重绘 */
    mc.__sqChipRender=renderChip;
    mc.__sqChipBase=function(){ renderChip(Math.min(w.hi,d.length)-1, lastC2); };
  }
  /* 日期轴（v4 canvas fillText） */
  var dStep=Math.ceil((n+FSeff)/7);
  ctx.fillStyle='#59626D'; ctx.font='10px OKXSans'; ctx.textAlign='left';
  for(i=0;i<n+FSeff;i+=dStep){
    var di=w.lo+i,dstr=di<d.length?dates[di]:null;
    if(!dstr){ var fdt=new Date(2026,7,27); fdt.setDate(fdt.getDate()+(di-d.length+1)); dstr=String(fdt.getMonth()+1).padStart(2,'0')+'-'+String(fdt.getDate()).padStart(2,'0'); }
    ctx.fillText(dstr,x(i)-12,H-8);
  }
  /* 事件轴图标（v4 DOM 覆盖层：保留免费交互） */
  ov.innerHTML='';
  var evByDate={};
  SQ_EVX.forEach(function(ev){
    [{dt:ev.pub,ic:SQ_EVIC[ev.type]||'📑'},{dt:ev.evt,ic:ev.pub===ev.evt?null:'📅'}].forEach(function(oc){
      if(!oc.ic)return;
      if(!evByDate[oc.dt])evByDate[oc.dt]={ics:[],evs:[]};
      evByDate[oc.dt].ics.push(oc.ic); evByDate[oc.dt].evs.push(ev);
    });
  });
  Object.keys(evByDate).forEach(function(dt){
    var gi=-1;
    for(i=0;i<d.length;i++) if(dates[i]===dt){ gi=i-w.lo; break; }
    var ex;
    if(gi>=0&&gi<n) ex=x(gi)+slotW*0.31;
    else {
      var fdt2=new Date(2026,7,27),tgt=new Date(2026,parseInt(dt.slice(0,2))-1,parseInt(dt.slice(3)));
      var fdiff=Math.round((tgt-fdt2)/86400000);
      if(fdiff>0&&fdiff<=FSeff) ex=x(n+fdiff-1)+slotW*0.31; else return;
    }
    var bx=(ex/W)*100, by=((H-26)/H)*100;
    var evEl=document.createElement('div');
    evEl.style.cssText='position:absolute;left:'+bx+'%;top:'+by+'%;width:18px;height:16px;background:#1A1C1E;border:1px solid #2E2E2E;border-radius:4px;font-size:10px;text-align:center;line-height:14px;cursor:pointer;pointer-events:auto;z-index:5';
    evEl.textContent=evByDate[dt].ics[0];
    evEl.setAttribute('data-ev',dt);
    if(evByDate[dt].ics.length>1){
      var badge=document.createElement('span');
      badge.style.cssText='position:absolute;right:-4px;top:-4px;width:11px;height:11px;background:#3D8BFF;border-radius:50%;font-size:8px;color:#fff;line-height:11px;text-align:center';
      badge.textContent=evByDate[dt].ics.length;
      evEl.appendChild(badge);
    }
    evEl.onclick=function(e){ sqEvPopV2(dt,e); };
    ov.appendChild(evEl);
  });
  /* v4 画线层（canvas 主层绘制，数据坐标→像素映射） */
  if(sqTf!=='分时'){
    sqDrawRenderCanvas(ctx,x,yf,slotW,n,w,d,L,W-R);
  }
  /* hover 十字读数（v4：canvas 主层绑定 mousemove，顶层 canvas 画十字线，DOM 覆盖层读数卡） */
  bindHoverCanvas(mc,cc,ov,{W:W,L:L,R:R,H:H-B,T:T,B:0,n:n,x:function(j){return x(j)+slotW*0.31;},cw:cwEff,d:d,w:w,dates:dates,m20:m20,readout:function(j){
    var gi=w.lo+j,k=d[gi]; if(!k)return '';
    return dates[gi]+'  开 '+k.o.toFixed(2)+'  高 '+k.h.toFixed(2)+'  低 '+k.l.toFixed(2)+'  收 '+k.c.toFixed(2)+'  MA20 '+m20[gi].toFixed(2);
  }});
}
/* OKX 式事件弹层（日期标题+事件列表：名称/时间/公布/预期/前值） */
function sqEvPopV2(dt,e){
  var old=document.getElementById('sq-evpop2'); if(old)old.remove();
  var evs=SQ_EVX.filter(function(ev){return ev.pub===dt||ev.evt===dt;});
  if(!evs.length)return;
  var box=document.getElementById('sq-canvas-stack'); if(!box)return;   /* v4：canvas 化后 svg#sq-main 已删，改取 stack 容器 */
  var pop=document.createElement('div'); pop.id='sq-evpop2'; pop.className='sq-evpop2';
  var h='<div class="tt">2026/'+dt.replace('-','/')+'</div>';
  evs.forEach(function(ev){
    h+='<div class="ev"><div class="nm">'+(SQ_EVIC[ev.type]||'📑')+' '+ev.ti+(ev.evt===dt&&ev.pub!==ev.evt?' <span class="tag">兑现日</span>':ev.pub===dt&&ev.pub!==ev.evt?' <span class="tag">披露日</span>':'')+'</div>'
      +'<div class="rw"><span>公布</span><b>'+ev.a+'</b></div><div class="rw"><span>预期</span><b>'+ev.f+'</b></div><div class="rw"><span>前值</span><b>'+ev.p+'</b></div></div>';
  });
  h+='<div class="x" onclick="document.getElementById(\'sq-evpop2\').remove()">✕ 关闭</div>';
  pop.innerHTML=h; box.appendChild(pop);
  var r=box.getBoundingClientRect(),px2=Math.min(e.clientX-r.left+14,r.width-268),py2=Math.min(e.clientY-r.top+10,r.height-190);
  pop.style.left=Math.max(8,px2)+'px'; pop.style.top=Math.max(8,py2)+'px';
  setTimeout(function(){ document.addEventListener('click',function h2(ev2){ if(!pop.contains(ev2.target)){ pop.remove(); document.removeEventListener('click',h2); } }); },0);
}
function svgBoxOf(id){ var s=document.getElementById(id); return s?s.parentNode:null; }
function sqRenderPanes(){
  var box=document.getElementById('sq-panes'); if(!box)return;
  var h='';
  sqPanes.forEach(function(kind,idx){
    h+='<div class="sq-panebox"><div class="sq-pane-t"><span>'+SQ_PANE_NM[kind]+'</span><span class="x" onclick="sqDelPane('+idx+')" title="移除该指标">✕</span></div>'
      +'<svg class="spark" id="sq-pane-'+idx+'" viewBox="0 0 1100 120" preserveAspectRatio="none" style="display:block;width:100%;height:96px"></svg></div>';
  });
  box.innerHTML=h;
  sqPanes.forEach(function(kind,idx){ sqDrawPane(kind,'sq-pane-'+idx); });
}
function sqDelPane(idx){ sqPanes.splice(idx,1); sqRenderPanes(); }
function sqAddPaneTgl(e){ e.stopPropagation(); var m=document.getElementById('sq-add-menu'); if(m)m.classList.toggle('open'); }
function sqAddPane(kind,e){
  if(e&&e.stopPropagation)e.stopPropagation();
  if(sqPanes.indexOf(kind)<0){ sqPanes.push(kind); sqRenderPanes(); }
  var m=document.getElementById('sq-add-menu'); if(m)m.classList.remove('open');
}
document.addEventListener('click',function(e){ var m=document.getElementById('sq-add-menu'),s=document.getElementById('sq-add-sel'); if(m&&m.classList.contains('open')&&s&&!s.contains(e.target)&&!m.contains(e.target)) m.classList.remove('open'); });
function sqDrawPane(kind,id){
  var svg=document.getElementById(id); if(!svg)return;
  var W=1100,H=120,L=46,R=sqTogs.chip?150:64,T=6,B=10;   /* 边距与主图对齐（v2 双轴） */
  var d=sqData(),w=sqWinGet(),n=w.hi-w.lo;
  var hiE=Math.min(w.hi,d.length);   /* v3.1：副图窗口越未来区夹紧 */
  var x=function(j){ return L+j*(W-L-R)/Math.max(1,n-1); };
  var g=el('g',{},svg),j;
  if(kind==='vol'){
    var vmax=0; for(j=w.lo;j<hiE;j++) vmax=Math.max(vmax,d[j].v);
    for(j=0;j<n;j++){ var gi4=w.lo+j; if(gi4>=d.length) continue; var k=d[gi4],vh=k.v/vmax*(H-T-B);
      el('rect',{x:x(j),y:H-B-vh,width:(W-L-R)/n*0.62,height:vh,fill:k.c>=k.o?'#CA3F64':'#25A750',opacity:0.5},g);
    }
    /* 量均线 MA5 白/MA10 琥珀（v2 同花顺功能增量） */
    var vma5=[],vma10=[];
    for(j=0;j<n;j++){
      var gi2=w.lo+j; if(gi2>=d.length) continue;
      var s5=0,c5=0,s10=0,c10=0,bk;
      for(bk=Math.max(0,gi2-4);bk<=Math.min(gi2,d.length-1);bk++){s5+=d[bk].v;c5++;}
      for(bk=Math.max(0,gi2-9);bk<=Math.min(gi2,d.length-1);bk++){s10+=d[bk].v;c10++;}
      vma5.push([x(j)+(W-L-R)/n*0.31,H-B-(s5/c5)/vmax*(H-T-B)]);
      vma10.push([x(j)+(W-L-R)/n*0.31,H-B-(s10/c10)/vmax*(H-T-B)]);
    }
    polyline(g,vma5,'#EDEFF2',1);
    polyline(g,vma10,'#F0B90B',1);
  }else if(kind==='macd'){
    var m=sqMACD(d),hmax=0;
    for(j=w.lo;j<hiE;j++) hmax=Math.max(hmax,Math.abs(m.hist[j]),Math.abs(m.dif[j]),Math.abs(m.dea[j]));
    hmax=hmax||1;
    var yf=function(v){ return T+(0.5-v/(hmax*2.2))*(H-T-B); };
    el('line',{x1:L,x2:W-R,y1:yf(0),y2:yf(0),stroke:'#2A2F36','stroke-width':0.5},g);
    for(j=0;j<n;j++){ var gi=w.lo+j; if(gi>=d.length) continue; var hv=m.hist[gi];
      el('rect',{x:x(j),y:hv>=0?yf(hv):yf(0),width:(W-L-R)/n*0.62,height:Math.abs(yf(hv)-yf(0)),fill:hv>=0?'#CA3F64':'#25A750',opacity:0.8},g);
    }
    polyline(g,m.dif.slice(w.lo,hiE).map(function(v,j2){return[x(j2),yf(v)];}),'#F0B90B',1.2);
    polyline(g,m.dea.slice(w.lo,hiE).map(function(v,j2){return[x(j2),yf(v)];}),'#CA3F64',1.2);
  }else if(kind==='kdj'){
    var kd=sqKDJ(d),ymin=0,ymax=100;
    var y2=function(v){ return T+(1-(v-ymin)/(ymax-ymin))*(H-T-B); };
    polyline(g,kd.K.slice(w.lo,hiE).map(function(v,j2){return[x(j2),y2(v)];}),'#3D8BFF',1.2);
    polyline(g,kd.D.slice(w.lo,w.hi).map(function(v,j2){return[x(j2),y2(v)];}),'#CA3F64',1.2);
    polyline(g,kd.J.slice(w.lo,w.hi).map(function(v,j2){return[x(j2),y2(v)];}),'#F0B90B',1.2);
    el('line',{x1:L,x2:W-R,y1:y2(80),y2:y2(80),stroke:'#2A2F36','stroke-width':0.5,'stroke-dasharray':'3 3'},g);
    el('line',{x1:L,x2:W-R,y1:y2(20),y2:y2(20),stroke:'#2A2F36','stroke-width':0.5,'stroke-dasharray':'3 3'},g);
  }
}
function sqRenderEvents(){
  var strip=document.getElementById('sq-evt-strip'); if(!strip)return;
  var h='<span style="font-size:11px;color:var(--faint);flex:none;padding-right:8px">大事件<br>时间线</span>';
  SQ_EVENTS.forEach(function(ev,i){
    h+='<span class="sq-evt" onclick="sqEvtPop('+i+',event)"><span class="ic">'+ev.ic+'</span><span class="tt">'+ev.tt+'</span><span class="dt">'+ev.dt+'</span></span>';
  });
  strip.innerHTML=h;
}
function sqEvtPop(i,ev){
  ev.stopPropagation();
  var e=SQ_EVENTS[i],pop=document.getElementById('sq-evtpop');
  pop.innerHTML='<h4>'+e.ic+' '+e.tt+'</h4>'
    +'<div class="kv"><span>时间</span><b>2026/'+e.dt+'</b></div>'
    +'<div class="kv"><span>公布</span><b>'+e.pub+'</b></div>'
    +'<div class="kv"><span>预期</span><b>'+e.exp+'</b></div>'
    +'<div class="kv"><span>前值</span><b>'+e.prev+'</b></div>'
    +'<div class="kv"><span>影响判定</span><b>'+e.imp+'</b></div>'
    +'<div class="kv"><span>影响板块</span><b>'+e.sec+'</b></div>'
    +'<div class="ana">'+e.ana+'</div>'
    +'<div class="row-end"><span class="sq-fb" onclick="fbReport(\'evt\',\'事件影响分析：'+e.tt+'\',this)">⚑报错</span> <span class="sq-fb" onclick="document.getElementById(\'sq-evtpop\').style.display=\'none\'">关闭</span></div>';
  var px=Math.min(ev.clientX+10,window.innerWidth-360),py=Math.min(ev.clientY+10,window.innerHeight-330);
  pop.style.left=px+'px'; pop.style.top=Math.max(50,py)+'px'; pop.style.display='block';
  setTimeout(function(){ document.addEventListener('click',sqEvtPopClose,{once:true}); },0);
}
function sqEvtPopClose(e){
  var pop=document.getElementById('sq-evtpop');
  if(!pop) return;
  if(pop.contains(e.target)){ document.addEventListener('click',sqEvtPopClose,{once:true}); return; }   /* 弹层内点击（如⚑报错）消耗 once 监听后重新武装 */
  pop.style.display='none';
}
function sqRenderInfo(){
  var box=document.getElementById('sq-info'),d=STOCKQ_D[sqCur],p=sqPoolFind(sqCur);
  if(!d){
    box.innerHTML='<div class="sq-qh"><span class="nm">'+p.nm+'</span><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><span class="chg '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></div>'
      +'<div class="sq-intro">「'+p.nm+'」资料演示数据未内置（全量资料仅 3 只演示标的：600519/300750/688981），K 线工作台可正常使用——五档/关键数据/股性/财务/新闻量化/合理估价全量待接入 I-2。</div>';
    return;
  }
  var inFav=sqFav.indexOf(sqCur)>=0;
  var h='<div class="sq-qh"><span class="nm">'+p.nm+'</span><span class="cd" style="color:var(--faint);font-size:10px">'+p.code+'</span>'
    +'<span class="badge b-na">闭市</span>'
    +'<span class="sq-fb" style="margin-left:auto" onclick="event.stopPropagation();sqFavTgl(\''+sqCur+'\',this)">'+(inFav?'★ 删自选':'☆ 加自选')+'</span></div>'
    +'<div class="sq-qh"><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><span class="chg '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></div>'
    +'<div class="sq-tags">'+d.tags.map(function(t){return '<span class="badge b-na">'+t+'</span>';}).join('')+'</div>'
    +'<div class="sq-intro">'+d.intro+'</div>';
  /* 五档 */
  h+='<div class="sq-sec"><span>五档挂单 <span class="dim" style="font-weight:400">miniQMT 五档快照口径（演示）</span></span></div><div class="sq-l2">';
  var vmax=0; d.l2.forEach(function(l){vmax=Math.max(vmax,l[1]);});
  var i;
  for(i=4;i>=0;i--){ h+='<div class="lr"><span style="color:var(--down)">卖'+(i+1)+'</span><span class="lbar"><i style="width:'+(d.l2[i][1]/vmax*100).toFixed(0)+'%;background:#25A750;opacity:.35"></i></span><span class="lp" style="color:var(--down)">'+d.l2[i][0].toFixed(2)+'</span><span class="lv">'+d.l2[i][1]+'</span></div>'; }
  for(i=5;i<10;i++){ h+='<div class="lr"><span style="color:var(--up)">买'+(i-4)+'</span><span class="lbar"><i style="width:'+(d.l2[i][1]/vmax*100).toFixed(0)+'%;background:#CA3F64;opacity:.35"></i></span><span class="lp" style="color:var(--up)">'+d.l2[i][0].toFixed(2)+'</span><span class="lv">'+d.l2[i][1]+'</span></div>'; }
  h+='</div>';
  /* 关键数据 */
  h+='<div class="sq-sec"><span>关键数据</span></div><div class="sq-kv-grid">';
  d.kv.forEach(function(kv){ h+='<span class="k">'+kv[0]+'</span><span class="v" style="grid-column:span 2">'+kv[1]+'</span>'; });
  h+='</div>';
  /* 个股股性 */
  h+='<div class="sq-sec"><span>个股股性 · 涨停基因（近一年）</span><span class="sq-fb" onclick="fbReport(\'guxing\',\'股性统计（'+p.nm+'）\',this)">⚑报错</span></div><div class="sq-fin">';
  d.guxing.forEach(function(kv){ h+='<span class="k">'+kv[0]+'</span><span class="v">'+kv[1]+'</span>'; });
  h+='</div>';
  /* 涨停基因·次日表现（R16 同花顺完整口径：封板成功率+次日四指标+近一年触及表） */
  h+='<div class="sq-fin"><span class="k">封板成功率(非一字)</span><span class="v">86.36%</span><span class="k">涨停成功/被砸</span><span class="v">20 / 3 次</span>'
    +'<span class="k">次日高开概率</span><span class="v">60.00%</span><span class="k">次日平均高开</span><span class="v up">+1.97%</span>'
    +'<span class="k">次日上涨概率</span><span class="v">60.00%</span><span class="k">次日平均涨幅</span><span class="v up">+1.66%</span></div>'
    +'<div class="note">涨停基因=近一年涨停历史统计（同花顺口径：封板成功率+次日表现）——真源 daban_board_event_deriver 全史推导（I-2）；演示口径</div>';
  /* 财务 */
  h+='<div class="sq-sec"><span>财务解读 · 2026 一季报</span></div><div class="sq-fin">';
  d.fin.forEach(function(kv){ h+='<span class="k">'+kv[0]+'</span><span class="v">'+kv[1]+'</span>'; });
  h+='</div>';
  /* 新闻量化 */
  h+='<div class="sq-sec"><span>相关新闻量化分析</span><span class="sq-fb" onclick="fbReport(\'news\',\'新闻量化（'+p.nm+'）\',this)">⚑报错</span></div>';
  d.news.forEach(function(nw){ h+='<div class="sq-news-item">'+nw[0]+'<br><span class="badge '+(nw[1].indexOf('正面')===0?'b-pass':(nw[1].indexOf('风险')===0||nw[1].indexOf('偏空')===0?'b-warn':'b-na'))+'">'+nw[1]+'</span></div>'; });
  /* 合理估价 */
  h+='<div class="sq-sec"><span>合理估价 · 一致预期</span><span class="sq-fb" onclick="fbReport(\'val\',\'合理估价（'+p.nm+'）\',this)">⚑报错</span></div>'
    +'<div class="sq-fin"><span class="k">目标价（'+d.val.n+' 家）</span><span class="v" style="color:var(--up);font-weight:600">'+d.val.t+'</span>'
    +'<span class="k">上行空间</span><span class="v" style="color:var(--up)">'+d.val.up+'</span></div>'
    +'<div class="note">'+d.val.note+'；估值模型演示口径，真源 I-2</div>';
  box.innerHTML=h;
}
function sqFavTgl(sym,btn){
  var i=sqFav.indexOf(sym);
  if(i>=0) sqFav.splice(i,1); else sqFav.push(sym);
  try{localStorage.setItem('zk-sq-fav',JSON.stringify(sqFav));}catch(e){}
  if(btn) btn.textContent=i>=0?'☆ 加自选':'★ 删自选';
  sqRenderList();
}
function fbReport(kind,label,btn){
  if(btn){ btn.classList.add('done'); btn.textContent='⚑已记录'; }
  window.__fbQueue=window.__fbQueue||[];
  window.__fbQueue.push({kind:kind,label:label,ts:Date.now()});
  sqToast('已记录纠错（演示）：'+label+'——后台日志+纠错样本库 I-2（四.C 学习管道）');
}
function sqToast(t){
  var el2=document.getElementById('sq-toast'); if(!el2)return;
  el2.textContent=t; el2.style.display='block';
  clearTimeout(window.__sqToastT);
  window.__sqToastT=setTimeout(function(){ el2.style.display='none'; },2600);
}
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

/* ==================== DS-5 K线规范图 v2（dsSpecChart：OKX 布局标准蓝图——四边信息+双轴+事件轴+标注层；xMidYMid meet 等比防 4K 变形） ==================== */
function dsSpecChart(){
  var svg=document.getElementById('ds-spec-chart'); if(!svg)return;
  var W=1160,H=560,L=64,R=170,MT=26,VB=386,VT=330,MB=470,BT=408,FS=8;
  var d=genCandles(8888,90), win=d.slice(-54), n=win.length, slotW=(W-L-R)/(n+FS);
  var lo=1e18,hi=-1e18; win.forEach(function(k){lo=Math.min(lo,k.l);hi=Math.max(hi,k.h);}); var pad=(hi-lo)*0.12; lo-=pad; hi+=pad;
  var yf=function(v){return MT+(1-(v-lo)/(hi-lo))*(VT-MT);};
  var x=function(j){return L+j*slotW;};
  var g=el('g',{},svg);
  grid(g,W,L,R,VT,MT,20,n+FS);
  drawCandles(g,win,x,yf,slotW*0.62);
  /* MA 三色（v3 规范色序：OKX 实测） */
  var mset=[[5,'#FFA726'],[10,'#EC407A'],[20,'#27C6DA']];
  mset.forEach(function(m){
    var arr=sqMAArr(d,m[0]),pts=[];
    for(var j=0;j<n;j++) pts.push([x(j)+slotW*0.31,yf(arr[36+j])]);
    polyline(g,pts,m[1],1.3);
  });
  /* 成本线 */
  var m40=sqMAArr(d,40),cpts=[]; for(var j2=0;j2<n;j2++) cpts.push([x(j2)+slotW*0.31,yf(m40[36+j2])]);
  polyline(g,cpts,'#F0B90B',1.5,'6 4');
  /* 买卖点 */
  for(var i=2;i<n-2;i++){
    if(win[i].l<win[i-1].l&&win[i].l<win[i+1].l&&win[i].l<win[i-2].l&&win[i].l<win[i+2].l){ var b=el('text',{x:x(i)+slotW*0.31,y:yf(win[i].l)+24,fill:'#CA3F64','font-size':12,'text-anchor':'middle'},g); b.textContent='▲'; }
    if(win[i].h>win[i-1].h&&win[i].h>win[i+1].h&&win[i].h>win[i-2].h&&win[i].h>win[i+2].h){ var s=el('text',{x:x(i)+slotW*0.31,y:yf(win[i].h)-12,fill:'#25A750','font-size':12,'text-anchor':'middle'},g); s.textContent='▼'; }
  }
  /* 双轴 v3：右=价格 5 档 #C6C6C6 12px，左=涨跌幅%（首收为 0，红正绿负） */
  var base=win[0].c;
  for(var t=0;t<=4;t++){
    var tv=lo+(hi-lo)*t/4,ty=yf(tv);
    hlabel(g,W-R+6,ty+3,tv.toFixed(2),'#C6C6C6',12);
    var pc=(tv-base)/base*100,pl=el('text',{x:L-6,y:ty+3,fill:pc>=0?'#CA3F64':'#25A750','font-size':10,'text-anchor':'end'},g); pl.textContent=(pc>=0?'+':'')+pc.toFixed(1)+'%';
  }
  /* 高低点标注 */
  var hiK=win[0],loK=win[0],hiJ=0,loJ=0;
  for(i=0;i<n;i++){ if(win[i].h>hiK.h){hiK=win[i];hiJ=i;} if(win[i].l<loK.l){loK=win[i];loJ=i;} }
  hlabel(g,Math.min(x(hiJ)+slotW+2,W-R-64),yf(hiK.h)+3,hiK.h.toFixed(2)+' →','#A0A6AD',10);
  hlabel(g,Math.min(x(loJ)+slotW+2,W-R-64),yf(loK.l)+3,loK.l.toFixed(2)+' →','#A0A6AD',10);
  /* 现价线 v3：点线 2px点+3px隔 alpha.5 + 色底黑字签 */
  var lastC=win[n-1].c,ly=yf(lastC),lup=lastC>=win[n-1].o;
  el('line',{x1:L,x2:W-R,y1:ly,y2:ly,stroke:lup?'#CA3F64':'#25A750','stroke-width':1.2,'stroke-dasharray':'2 3',opacity:0.5},g);
  el('rect',{x:W-R+2,y:ly-9,width:58,height:17,rx:2,fill:lup?'#CA3F64':'#25A750'},g);
  var pt=el('text',{x:W-R+7,y:ly+4,fill:'#000000','font-size':11,'font-weight':600},g); pt.textContent=lastC.toFixed(2);
  /* 筹码峰 v3.1 同花顺单色：60 桶、每价位一根柱单色（现价下=获利红/现价上=套牢绿）、成本线=琥珀 */
  var NB=60,bw=(hi-lo)/NB,bins=[],bi2;
  for(bi2=0;bi2<NB;bi2++)bins.push(0);
  win.forEach(function(k){ var t2=(k.o+k.c+k.h+k.l)/4,ix=Math.min(NB-1,Math.max(0,Math.floor((t2-lo)/bw))); bins[ix]+=k.v; });
  var bmax=Math.max.apply(null,bins),poc=0;
  bins.forEach(function(b2,ix){ if(bins[ix]>bins[poc])poc=ix; });
  var chipX=W-R+96,chipW=44;
  var lastC3=win[n-1].c;
  bins.forEach(function(b2,ix){
    if(b2<=0)return;
    var binPx2=lo+(ix+0.5)*bw, isPf=binPx2<=lastC3;
    el('rect',{x:chipX,y:yf(lo+(ix+1)*bw),width:Math.max(1,(b2/bmax)*chipW),height:Math.max(1,(VT-MT)/NB-0.5),fill:isPf?'#CA3F64':'#25A750',opacity:0.5},g);
  });
  var pocPx=lo+(poc+0.5)*bw;
  el('line',{x1:chipX-2,x2:chipX+chipW,y1:yf(pocPx),y2:yf(pocPx),stroke:'#F0B90B','stroke-width':1.2},g);
  hlabel(g,chipX,MT+0,'获利 62%','#8B949E',9);
  /* VOL 副图（50% 透明+量均线白/琥珀） */
  var vmax=0; win.forEach(function(k){vmax=Math.max(vmax,k.v);});
  win.forEach(function(k,i2){
    var vh=k.v/vmax*(VB-VT-6);
    el('rect',{x:x(i2),y:VB-vh,width:slotW*0.62,height:vh,fill:k.c>=k.o?'#CA3F64':'#25A750',opacity:0.5},g);
  });
  var vm5=[],vm10=[];
  for(var j3=0;j3<n;j3++){ var s5=0,s10=0,c5=0,c10=0,bk;
    for(bk=Math.max(0,j3-4);bk<=j3;bk++){s5+=win[bk].v;c5++;}
    for(bk=Math.max(0,j3-9);bk<=j3;bk++){s10+=win[bk].v;c10++;}
    vm5.push([x(j3)+slotW*0.31,VB-(s5/c5)/vmax*(VB-VT-6)]);
    vm10.push([x(j3)+slotW*0.31,VB-(s10/c10)/vmax*(VB-VT-6)]);
  }
  polyline(g,vm5,'#EDEFF2',1); polyline(g,vm10,'#F0B90B',1);
  /* MACD 副图 */
  var mc=sqMACD(d),hmax=0;
  for(var j4=36;j4<90;j4++) hmax=Math.max(hmax,Math.abs(mc.hist[j4]),Math.abs(mc.dif[j4]),Math.abs(mc.dea[j4]));
  var ym=function(v){return BT+((hmax-v)/(2*hmax))*(MB-BT);}, zy=ym(0);
  for(var j5=0;j5<n;j5++){ var hv=mc.hist[36+j5],ry=ym(hv);
    el('rect',{x:x(j5),y:Math.min(zy,ry),width:slotW*0.62,height:Math.max(1.2,Math.abs(ry-zy)),fill:hv>=0?'#CA3F64':'#25A750'},g);
  }
  var dp=[],ep=[];
  for(var j6=0;j6<n;j6++){ dp.push([x(j6)+slotW*0.31,ym(mc.dif[36+j6])]); ep.push([x(j6)+slotW*0.31,ym(mc.dea[36+j6])]); }
  polyline(g,dp,'#F0B90B',1.2); polyline(g,ep,'#CA3F64',1.2);
  /* 日期轴+事件图标（含未来空槽） */
  var dl=['07/21','07/28','08/04','08/11','08/18','08/25','09/01','09/08'];
  for(var dli=0;dli<8;dli++) hlabel(g,x(Math.round(dli*(n+FS-1)/7))-12,VT+16,dl[dli],'#59626D',10);
  var evMarks=[[8,'📅',2],[22,'📰',1],[31,'💲',1],[44,'📑',1],[n+3,'📅',3]];
  evMarks.forEach(function(em){
    var ex=x(em[0])+slotW*0.31;
    el('rect',{x:ex-9,y:VT+22,width:18,height:16,rx:4,fill:'#1A1C1E',stroke:'#2E2E2E','stroke-width':1},g);
    var it=el('text',{x:ex,y:VT+34,'font-size':10,'text-anchor':'middle'},g); it.textContent=em[1];
    el('circle',{cx:ex+8,cy:VT+22,r:5.5,fill:'#3D8BFF'},g);
    var cb=el('text',{x:ex+8,y:VT+25,'font-size':8,fill:'#fff','text-anchor':'middle'},g); cb.textContent=em[2];
  });
  /* ===== 标注层（引线+规范说明） ===== */
  function anno(ax,ay,tx2,ty2,txt,col,anchorEnd){
    el('line',{x1:ax,y1:ay,x2:anchorEnd?tx2+150:tx2-6,y2:ty2+3,stroke:col,'stroke-width':0.8,'stroke-dasharray':'2 2',opacity:0.8},g);
    el('circle',{cx:ax,cy:ay,r:2.4,fill:col},g);
    var t3=el('text',{x:tx2,y:ty2+7,fill:col,'font-size':11,'text-anchor':anchorEnd?'end':'start'},g); t3.textContent=txt;
  }
  anno(x(10)+slotW*0.31,yf(win[10].h)-4,8,yf(win[10].h)-8,'蜡烛平涂 #CA3F64/#25A750，仅最新一根微光','#EDEFF2');
  anno(x(24)+slotW*0.31,yf(sqMAArr(d,5)[60])-6,x(24)-120,MT+4,'MA5 #FFA726 橙','#FFA726');
  anno(x(38)+slotW*0.31,yf(sqMAArr(d,10)[74])+16,x(38)-110,MT+4,'MA10 #EC407A 品红','#EC407A');
  anno(x(48)+slotW*0.31,yf(sqMAArr(d,20)[84])+28,x(48)-116,MT+18,'MA20 #27C6DA 青','#27C6DA');
  anno(x(30)+slotW*0.31,yf(sqMAArr(d,40)[66])+4,x(30)-150,VT-28,'成本线 #F0B90B 虚线 dash 6 4','#F0B90B');
  anno(W-R+140,yf(pocPx),W-R+150,yf(pocPx)-20,'筹码峰 v3.1 同花顺单色：60 桶 现价下获利红/上套牢绿+成本线琥珀','#F0B90B');
  anno(x(44),ly,W-R+66,ly+26,'现价点线 alpha.5+色底黑字签（右轴=价格 #C6C6C6 12px）','#A0A6AD');
  anno(L-24,yf(base),64,VT-8,'左轴=涨跌幅%（红正绿负）','#A0A6AD');
  var volT=el('text',{x:L,y:VT-6,fill:'#A0A6AD','font-size':11},g); volT.textContent='VOL：柱×50% 透明（v3 量均线转可选，OKX 实测无量均线）';
  var macT=el('text',{x:L,y:BT-6,fill:'#A0A6AD','font-size':11},g); macT.textContent='MACD：DIF #F0B90B · DEA #CA3F64 · 柱正红负绿';
  anno(x(n+3)+slotW*0.31,VT+30,x(n-24),VT+52,'日期轴事件图标+数量 badge（未来空槽给未来事件），点击出 OKX 式弹层','#8B9BD5');
  var gt=el('text',{x:W-R+4,y:MT+8,fill:'#59626D','font-size':10},g); gt.textContent='网格 #171717 横竖挂刻度 · 图表底 #000 · 高低点 "值 →"';
}
dsSpecChart();

/* ==================== 模块缩放 A 案（DS-10）：卡片 ⛶ 全屏聚焦（通用，零逐页改动）+ 主图容器纵向拖拽柄 ==================== */
function fsToggle(card){
  var mask=document.getElementById('fs-mask');
  if(!mask){ mask=document.createElement('div'); mask.id='fs-mask'; mask.className='fs-mask'; mask.innerHTML='<span class="fs-tip">ESC / 点击空白 关闭</span>'; document.body.appendChild(mask);
    mask.addEventListener('click',function(e){ if(e.target===mask||e.target.classList.contains('fs-tip')) fsClose(); });
    document.addEventListener('keydown',function(e){ if(e.key==='Escape') fsClose(); });
  }
  if(card){ card.__fsHome={p:card.parentNode,n:card.nextSibling}; mask.appendChild(card); var b=card.querySelector('.fs-btn'); if(b) b.textContent='✕'; mask.classList.add('open'); }   /* 顺序修复（复验抓出真 bug）：先记原位再移入 mask，否则 ESC 后卡片丢失原位 */
}
function fsClose(){
  var mask=document.getElementById('fs-mask'); if(!mask||!mask.classList.contains('open'))return;
  var card=mask.querySelector('.card');
  if(card&&card.__fsHome){ card.__fsHome.p.insertBefore(card,card.__fsHome.n); var b=card.querySelector('.fs-btn'); if(b) b.textContent='⛶'; }
  mask.classList.remove('open');
}
function fsArm(){
  document.querySelectorAll('.main .card > h3').forEach(function(h){
    if(h.querySelector('.fs-btn'))return;
    h.style.display='flex'; h.style.alignItems='baseline'; h.style.gap='6px';
    var b=document.createElement('span'); b.className='fs-btn'; b.textContent='⛶'; b.title='全屏聚焦（DS-10 模块缩放 A 案）';
    b.onclick=function(e){ e.stopPropagation(); fsToggle(h.parentNode); };
    h.appendChild(b);
  });
  /* 主图容器加纵向拖拽柄（sq 个股行情主图 + 技术分析主图盒） */
  var sq=document.querySelector('.sq-mainbox'); if(sq) sq.classList.add('rsz-y');
}
fsArm();
/* ==================== 注解收敛 slimAnnot（Owner 2026-08-26 方向：版面简洁化——核心字保留，副注解收 ⓘ 悬浮；通用转换零逐页改动） ==================== */
function slimAnnot(){
  /* A. page-sub：以「——」为界，前=核心句保留可见，后=注解入 data-tip（无——的短 sub 不动） */
  document.querySelectorAll('.page-sub').forEach(function(s){
    if(s.__slimmed) return; s.__slimmed=1;
    var h=s.innerHTML, cut=h.indexOf('——');
    if(cut>10){
      var core=h.slice(0,cut), tip=h.slice(cut).replace(/<[^>]+>/g,'').trim();
      s.innerHTML=core+' <i class="info-ic" data-tip="'+tip.replace(/"/g,'&quot;')+'">!</i>';
    }
  });
  /* B. 卡标题 h3 内的长 dim 注解（>14 字）→ ⓘ 悬浮（badge 保留可见——演示数据标注纪律不动） */
  document.querySelectorAll('.card h3 .dim').forEach(function(d){
    var t=(d.textContent||'').trim();
    if(t.length>14){
      var i=document.createElement('i');
      i.className='info-ic';
      i.setAttribute('data-tip',t.replace(/"/g,'&quot;'));
      i.textContent='!';
      d.replaceWith(i);
    }
  });
}
slimAnnot();

/* I-8 S1 全局搜索：REGLIB_D 就绪后补全库条目+绑定（防 var 赋值未提升时序缺陷） */
srchLate();
