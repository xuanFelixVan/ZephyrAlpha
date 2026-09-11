/* 功能模块：DS-5 K 线规范图（ds-spec-chart）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：设计规范演示图（design 页）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L6947-7061），逻辑零改动。
 * 验收单：ACC-F-DESIGN-SPEC-CHART
 */
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

