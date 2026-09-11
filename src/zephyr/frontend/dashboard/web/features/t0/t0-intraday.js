/* 功能模块：T 分析分时图+做T回验命中（t0-intraday）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟数据演示版式
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L3381-3428, L5204-5220），逻辑零改动。
 * 验收单：ACC-F-T0-INTRADAY
 */
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
