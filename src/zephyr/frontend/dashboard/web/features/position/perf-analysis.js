/* 功能模块：收益分析区（perf-analysis）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：确定性模拟（多账户收益曲线）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L5045-5147），逻辑零改动。
 * 验收单：ACC-F-POS-PERF-ANALYSIS
 */
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

