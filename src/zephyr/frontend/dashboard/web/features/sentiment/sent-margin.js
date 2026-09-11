/* 功能模块：市场情绪·两融（sent-margin）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：演示数据（两融余额）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5148-5203），逻辑零改动。
 * 验收单：ACC-F-SENTIMENT-MARGIN
 */
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
