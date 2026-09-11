/* 功能模块：盘中实时权益分时（live-equity）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟（样本外包络）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L4690-4722），逻辑零改动。
 * 验收单：ACC-F-LIVE-EQUITY
 */
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
