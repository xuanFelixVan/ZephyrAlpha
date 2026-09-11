/* 功能模块：指数详情页渲染引擎（idx-engine）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟数据演示版式（真源待接入）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L177-250, L2268-3343），逻辑零改动。
 * 验收单：ACC-F-IDX-ENGINE
 */
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
    }else{
      if(c.cross) c.cross.style.display='none';
      c.rd.style.display='none';
    }
  }
}

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
/* stratSel/sd-curve 已随 Owner 2026-09-01 裁定退役：策略看板宫格+档案详情并入回测页（backtest.js btRenderStratGrid/btRenderProfile 真源版） */
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

