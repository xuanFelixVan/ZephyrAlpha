/* ══════════════════════════════════════════════════════════════
   core/backtest.js — 回测页逻辑族（2026-08-29 自 app1.js 拆出，物理隔离 K 线引擎改造区）
   含：bt Tab 切换 / btGen 数据生成 / btArea / btCharts 三图渲染（hover 卡片读数 R23b）
       / BT_DAILY 每日明细下钻 / btrRun 新建回测发起（演示）
   依赖 app1.js 全局工具（el/grid/polyline/bindHover/mkReadout/CHARTS/lcg/fmtD）——loader 保证 app1 先加载
   ══════════════════════════════════════════════════════════════ */

function bt(id, el){
  document.querySelectorAll('#p-backtest .subpage').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('#p-backtest .tabs .tab').forEach(t=>t.classList.remove('on'));
  document.getElementById('bt-'+id).classList.add('active');
  el.classList.add('on');
}
/* ==================== 回测绩效三图（demo-perf-001 确定性序列 + 三图十字光标联动） ==================== */
function btGen(){
  var n=522,r=lcg(20190102),sRet=[],bRet=[],dates=[],dt=new Date(2019,0,2);
  for(var i=0;i<n;i++){
    sRet.push((r()-0.47)*2.4);
    bRet.push((r()-0.52)*1.9);
    dates.push(fmtD(dt));
    dt.setDate(dt.getDate()+1); while(dt.getDay()===0||dt.getDay()===6) dt.setDate(dt.getDate()+1);
  }
  /* 归一化到真实页面期末值：策略 +124.82% / 基准 -23.65% */
  function scaleTo(rets,target){var cum=1;rets.forEach(function(v){cum*=1+v/100;});var adj=Math.pow((1+target)/cum,1/rets.length);return rets.map(function(v){return((1+v/100)*adj-1)*100;});}
  sRet=scaleTo(sRet,1.2482); bRet=scaleTo(bRet,-0.2365);
  var sEq=[],bEq=[],ex=[],sDD=[],bDD=[],fs=1,fb=1,pkS=1,pkB=1;
  for(var j=0;j<n;j++){
    fs*=1+sRet[j]/100; fb*=1+bRet[j]/100;
    sEq.push((fs-1)*100); bEq.push((fb-1)*100); ex.push((fs-fb)*100);
    pkS=Math.max(pkS,fs); pkB=Math.max(pkB,fb);
    sDD.push((fs/pkS-1)*100); bDD.push((fb/pkB-1)*100);
  }
  /* 回撤锚定到真实页面口径：策略最深 -15.84% / 基准最深 -38.20% */
  function scaleDD(dd,target){var mn=Math.min.apply(null,dd);var f=target/mn;return dd.map(function(v){return v*f;});}
  sDD=scaleDD(sDD,-15.84); bDD=scaleDD(bDD,-38.20);
  return{n:n,dates:dates,sRet:sRet,bRet:bRet,sEq:sEq,bEq:bEq,ex:ex,sDD:sDD,bDD:bDD};
}
function btArea(g,vals,x,cw,y0,yf,col,op){
  var pts=vals.map(function(v,i){return(x(i)+cw/2).toFixed(1)+','+yf(v).toFixed(1);}).join(' ');
  pts+=' '+(x(vals.length-1)+cw/2).toFixed(1)+','+y0.toFixed(1)+' '+(x(0)+cw/2).toFixed(1)+','+y0.toFixed(1);
  el('polygon',{points:pts,fill:col,opacity:op},g);
}
function btCharts(B){
  /* B: {n,dates,sEq,bEq,ex,sDD,bDD,sRet,bRet}——真源由 btLoadDetail 组装，演示由 btGen 兜底 */
  if(!B){ B=btGen(); btSetMode('断线'); }
  /* 收益图：策略蓝 / 基准紫 / 超额橙点线 */
  (function(){
    var svg=document.getElementById('bt-eq'); if(!svg)return; svg.innerHTML='';
    var W=1100,H=400,L=10,R=14,T=14,Bx=14;
    var lo=Math.min.apply(null,B.bEq.concat([-60])),hi=Math.max.apply(null,B.sEq.concat([150]));
    var n=B.n,cw=(W-L-R)/n*0.62;
    var x=function(i){return L+(i+0.5)*(W-L-R)/n-cw/2;};
    var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-Bx);};
    var g=el('g',{},svg); grid(g,W,L,R,H,T,Bx);
    el('line',{x1:L,x2:W-R,y1:yf(0),y2:yf(0),stroke:'#2A2F36','stroke-width':0.6},g);
    polyline(g,B.sEq.map(function(v,i){return[x(i)+cw/2,yf(v)];}),'#3D8BFF',1.5);
    polyline(g,B.bEq.map(function(v,i){return[x(i)+cw/2,yf(v)];}),'#AB47BC',1.5);
    polyline(g,B.ex.map(function(v,i){return[x(i)+cw/2,yf(v)];}),'#F0B90B',1.5,'2 4');
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:Bx,n:n,x:x,cw:cw,g:g,rd:mkReadout(svg.parentNode),readout:function(i){
      return '<div class="rd-date">'+B.dates[i]+'</div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:#3D8BFF"></span>策略收益 <b>'+B.sEq[i].toFixed(2)+'%</b></div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:#AB47BC"></span>沪深300 <b>'+B.bEq[i].toFixed(2)+'%</b></div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:#F0B90B"></span>超额收益 <b>'+B.ex[i].toFixed(2)+'%</b></div>';
    }});
  })();
  /* 回撤图：策略红面积 / 基准紫面积 */
  (function(){
    var svg=document.getElementById('bt-dd'); if(!svg)return; svg.innerHTML='';
    var W=1100,H=300,L=10,R=14,T=14,Bx=14;
    var lo=-42,hi=2;
    var n=B.n,cw=(W-L-R)/n*0.62;
    var x=function(i){return L+(i+0.5)*(W-L-R)/n-cw/2;};
    var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-Bx);};
    var g=el('g',{},svg); grid(g,W,L,R,H,T,Bx);
    btArea(g,B.bDD,x,cw,yf(0),yf,'#AB47BC',0.35);
    polyline(g,B.bDD.map(function(v,i){return[x(i)+cw/2,yf(v)];}),'#AB47BC',1);
    btArea(g,B.sDD,x,cw,yf(0),yf,'#CA3F64',0.4);
    polyline(g,B.sDD.map(function(v,i){return[x(i)+cw/2,yf(v)];}),'#CA3F64',1);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:Bx,n:n,x:x,cw:cw,g:g,rd:mkReadout(svg.parentNode),readout:function(i){
      return '<div class="rd-date">'+B.dates[i]+'</div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:#CA3F64"></span>策略回撤 <b>'+B.sDD[i].toFixed(2)+'%</b></div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:#AB47BC"></span>沪深300回撤 <b>'+B.bDD[i].toFixed(2)+'%</b></div>';
    }});
  })();
  /* 日收益率：红/绿柱 + 基准紫线 */
  (function(){
    var svg=document.getElementById('bt-dr'); if(!svg)return; svg.innerHTML='';
    var W=1100,H=300,L=10,R=14,T=14,Bx=14;
    var mx=0; B.sRet.concat(B.bRet).forEach(function(v){mx=Math.max(mx,Math.abs(v));});
    var lo=-Math.ceil(mx+0.5),hi=Math.ceil(mx+0.5);   /* Y 域按数据自适应 */
    var n=B.n,cw=(W-L-R)/n*0.62;
    var x=function(i){return L+(i+0.5)*(W-L-R)/n-cw/2;};
    var yf=function(v){return T+(1-(v-lo)/(hi-lo))*(H-T-Bx);};
    var g=el('g',{},svg); grid(g,W,L,R,H,T,Bx);
    var zero=yf(0);
    B.sRet.forEach(function(v,i){
      el('rect',{x:x(i),y:Math.min(yf(v),zero),width:cw,height:Math.max(1,Math.abs(yf(v)-zero)),fill:v>=0?'#CA3F64':'#25A750'},g);
    });
    polyline(g,B.bRet.map(function(v,i){return[x(i)+cw/2,yf(v)];}),'#AB47BC',1);
    bindHover(svg,{W:W,L:L,R:R,H:H,T:T,B:Bx,n:n,x:x,cw:cw,g:g,rd:mkReadout(svg.parentNode),readout:function(i){
      return '<div class="rd-date">'+B.dates[i]+'</div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:'+(B.sRet[i]>=0?'#CA3F64':'#25A750')+'"></span>策略日收益 <b>'+(B.sRet[i]>=0?'+':'')+B.sRet[i].toFixed(2)+'%</b></div>'
        +'<div class="rd-row"><span class="rd-dot" style="background:#AB47BC"></span>沪深300日收益 <b>'+(B.bRet[i]>=0?'+':'')+B.bRet[i].toFixed(2)+'%</b></div>';
    }});
  })();
}
/* ==================== 真源模式（#BT-PIPELINE-001）：artifacts 列表 + 详情渲染 + 页面发起回测 ==================== */
/* 数据源：/api/backtest-list + /api/backtest-detail + POST /api/backtest-run（BTRUN 强制时序落盘产物）。
 * 演示纪律：真源不可达→四态灯红（断线），btGen 演示数据兜底并明示；未启动→灰。
 * 顺序铁律：BT_STATE 必须在下方 btCharts() 调用之前赋值——btCharts 内部 btSetMode 写
 * BT_STATE.mode，var 提升不等于赋值（2026-09-01 实证：顺序颠倒→TypeError→顶层中断→
 * 发起回测炸 "Cannot set properties of undefined (setting 'taskId')"）。 */
var BT_STATE={mode:'未启动',run:null,taskId:null,timer:null};
function btApi(){return (window.ZK&&ZK.api)?ZK.api:null;}
btCharts();
function btSetMode(m,extra){
  BT_STATE.mode=m;
  var badge=document.getElementById('bt-src-badge');
  if(badge){badge.className='badge '+(m==='真源'?'b-pass':(m==='延迟'?'b-warn':(m==='断线'?'b-fail':'b-na')));
    badge.textContent='● '+m+(extra?'·'+extra:'');}
}
function btPct(v){return (v>=0?'+':'')+(v*100).toFixed(2)+'%';}
/* 详情 artifact → btCharts 数据形状（净值→累计收益率%；回撤→负%；日收益由净值差分；无基准时基准线隐藏=0） */
function btFromArtifact(d){
  var eq=d.equity_curve||[],dd=d.drawdown_curve||[];
  if(!eq.length)return null;
  var cap0=eq[0].equity||1;
  var dates=[],sEq=[],sDD=[],sRet=[],bEq=[],bDD=[],bRet=[],ex=[];
  var benchMap={};
  (d.benchmark_curve||[]).forEach(function(p){benchMap[p.timestamp]=p.value;});
  var hasBench=(d.benchmark_curve||[]).length>0,b0=hasBench?d.benchmark_curve[0].value:1;
  var prev=null;
  for(var i=0;i<eq.length;i++){
    dates.push(eq[i].timestamp);
    var cum=(eq[i].equity/cap0-1)*100; sEq.push(cum);
    var bv=hasBench?(benchMap[eq[i].timestamp]!=null?(benchMap[eq[i].timestamp]/b0-1)*100:null):0;
    bEq.push(bv==null?0:bv);
    ex.push(cum-(bv==null?0:bv));
    var ddp=(dd[i]&&dd[i].drawdown!=null)?-dd[i].drawdown*100:0;
    sDD.push(ddp); bDD.push(hasBench?0:0);
    var r=prev==null?0:(eq[i].equity/prev-1)*100; sRet.push(r); bRet.push(0); prev=eq[i].equity;
  }
  return {n:dates.length,dates:dates,sEq:sEq,bEq:bEq,ex:ex,sDD:sDD,bDD:bDD,sRet:sRet,bRet:bRet};
}
function btFillKpi(m){
  var k=document.getElementById('bt-kpi'); if(!k||!m)return;
  var vs=k.querySelectorAll('.v');
  if(vs.length>=6){
    vs[0].textContent=btPct(m.total_return||0); vs[0].className='v '+(m.total_return>=0?'up':'down');
    vs[1].textContent=btPct(m.annual_return||0); vs[1].className='v '+(m.annual_return>=0?'up':'down');
    vs[2].textContent=btPct(-(m.max_drawdown||0)); vs[2].className='v down';
    vs[3].textContent=(m.sharpe_ratio!=null?m.sharpe_ratio.toFixed(2):'--');
    vs[4].textContent=(m.win_rate!=null?(m.win_rate*100).toFixed(2)+'%':'--');
    vs[5].textContent=(m.trades_count!=null?m.trades_count+' 笔':'--');
  }
  var sh=document.querySelector('#p-backtest .strategy-head .name');
  if(sh)sh.textContent='📊 '+(m.strategy_id||'')+' · '+BT_STATE.run;
  var sub=document.querySelector('#p-backtest .strategy-head .sub');
  if(sub)sub.textContent='回测绩效分析 Backtest Performance Analysis | 真源 '+BT_STATE.run+'（'+(m.start_date||'').slice(0,10)+' ~ '+(m.end_date||'').slice(0,10)+'）';
  var ps=document.querySelectorAll('#p-backtest .param-strip span b');
  if(ps.length>=5){
    ps[0].textContent=(m.start_date||'').slice(0,10)+' ~ '+(m.end_date||'').slice(0,10);
    ps[4].textContent=(m.trades_count!=null?m.trades_count:'--');
  }
}
function btLoadDetail(runId){
  var api=btApi(); if(!api){btSetMode('断线');return;}
  BT_STATE.run=runId;
  api.fetchBacktestDetail(runId).then(function(r){
    if(!r||!r.ok||!r.data){btSetMode('断线');return;}
    var B=btFromArtifact(r.data);
    if(!B){btSetMode('断线','产物无时序');btCharts();return;}
    btCharts(B);
    btFillKpi(r.data.metrics||{});
    btFillTradeLog(r.data.trade_log||[]);
    /* 抽稀明示：tick/minute 产物展示抽稀（存储全量） */
    var tp=r.data.total_points;
    var sub=document.querySelector('#p-backtest .strategy-head .sub');
    if(sub&&tp&&tp.equity&&tp.equity>B.n){
      sub.textContent+=' · 展示抽稀 '+B.n+'/'+tp.equity+' 点（产物文件全量）';
    }
    btSetMode('真源',runId);
  }).catch(function(){btCharts();btSetMode('断线');});
}
/* Tab5 交易明细表填真源 trade_log（API 已倒序最新在前，前端 cap 200） */
function btFillTradeLog(log){
  var tab=document.querySelector('#bt-signal table');
  if(!tab)return;
  if(!log.length)return;
  var h='<tr><th>时间 Time</th><th>代码 Symbol</th><th>方向 Side</th><th>价格 Price</th><th>数量 Qty</th><th>金额 Amount</th><th>手续费 Fee</th></tr>';
  log.slice(0,200).forEach(function(t){
    var amt=(t.price*t.quantity).toFixed(0);
    h+='<tr><td>'+t.timestamp+'</td><td>'+t.symbol+'</td><td class="'+(t.side==='buy'?'up':'down')+'">'+t.side+'</td><td>'+t.price.toFixed(3)+'</td><td>'+t.quantity+'</td><td>¥'+amt+'</td><td>'+t.commission.toFixed(2)+'</td></tr>';
  });
  tab.innerHTML=h;
}
/* 产物选择条（插在策略头下方）：列出 artifacts，点选即切详情 */
function btRenderRunList(list){
  var strip=document.getElementById('bt-run-strip');
  if(!strip)return;
  if(!list.length){strip.innerHTML='<span class="dim" style="font-size:12px">无回测产物（data/backtest_artifacts/ 空）——点上方「发起回测」跑第一个</span>';return;}
  var h='';
  list.forEach(function(it){
    var ret=it.total_return!=null?(it.total_return*100).toFixed(1)+'%':'--';
    var cls=it.run_id===BT_STATE.run?'rsec-item on':'rsec-item';
    h+='<span class="'+cls+'" onclick="btLoadDetail(\''+it.run_id+'\')" title="'+it.created_at+' 等值点'+(it.equity_points||0)+'">'
      +it.run_id.replace('bt-','')+' · '+(it.strategy_id||'')+' · <b class="'+(it.total_return>=0?'up':'down')+'">'+ret+'</b></span>';
  });
  strip.innerHTML=h;
}
function btBoot(){
  btLoadStrategies();
  btrSyncDateInputs();
  var api=btApi(); if(!api){btSetMode('未启动');return;}
  api.fetchBacktestList().then(function(r){
    if(!r||!r.ok){btSetMode('未启动');return;}
    btRenderRunList(r.data||[]);
    /* 默认选最新有明细的产物 */
    var first=(r.data||[]).filter(function(x){return x.has_detail;})[0]||((r.data||[])[0]);
    if(first)btLoadDetail(first.run_id); else btSetMode('真源','无产物');
  }).catch(function(){btSetMode('未启动');});
}
/* btrRun 转真：POST /api/backtest-run → 轮询状态 → 完成后刷新列表+载入新产物
 * 参数源=配置条（BTR_CFG）：策略多选（/api/strategies 动态拉取）、时间段（快速下拉
 * 或自定义 date input）、初始资金、撮合模式（vectorized/tick 完全仿真）。 */
var BTR_CFG={strategies:['topn-momentum'],period:'m6',customStart:null,customEnd:null,capital:1000000,mode:'vectorized'};
/* 策略库动态拉取（StrategyRegistry 真源），重建多选菜单 */
function btLoadStrategies(){
  var api=btApi(); if(!api) return;
  api.fetchJson('/api/strategies').then(function(r){
    if(!r||!r.ok||!r.data||!r.data.length) return;
    var menu=document.getElementById('btr-strategy-menu'); if(!menu) return;
    var have={};
    r.data.forEach(function(s){ have[s.id]=true; });
    /* 菜单=动态策略 ∪ 既有选中（API 缺失时保留），default-equity 契约已修可放 */
    var ids=[]; r.data.forEach(function(s){ if(ids.indexOf(s.id)<0)ids.push(s.id); });
    BTR_CFG.strategies.forEach(function(sid){ if(!have[sid]&&ids.indexOf(sid)<0)ids.push(sid); });
    var h='';
    ids.forEach(function(sid){
      var on=BTR_CFG.strategies.indexOf(sid)>=0;
      h+='<span class="acct-mi'+(on?' on':'')+'" data-v="'+sid+'" onclick="btrPick(\'strategy\',\''+sid+'\',event)">'+(on?'✓ ':'')+sid+'</span>';
    });
    menu.innerHTML=h;
    btStrategyLabel();
  }).catch(function(){});
}
function btStrategyLabel(){
  var t=document.getElementById('btr-strategy-t'); if(!t)return;
  t.textContent=BTR_CFG.strategies.length===1?BTR_CFG.strategies[0]:(BTR_CFG.strategies.length+' 个策略');
}
function btrDropTgl(e){
  e.stopPropagation();
  var m=e.currentTarget.querySelector('.acct-menu');
  if(m)m.classList.toggle('open');
}
document.addEventListener('click',function(e){
  document.querySelectorAll('#btr-card .acct-menu.open').forEach(function(m){
    if(!m.parentNode.contains(e.target))m.classList.remove('open');
  });
});
function btrPick(kind,v,e){
  if(e&&e.stopPropagation)e.stopPropagation();
  var label=e?e.target.textContent.replace(/^✓ /,'').split('（')[0].trim():v;
  if(kind==='strategy'){
    /* 多选 toggle：点选/取消，至少保留 1 个 */
    var i=BTR_CFG.strategies.indexOf(v);
    if(i>=0){ if(BTR_CFG.strategies.length>1)BTR_CFG.strategies.splice(i,1); }
    else BTR_CFG.strategies.push(v);
    var mi=e?e.target:null;
    if(mi){ mi.classList.toggle('on',BTR_CFG.strategies.indexOf(v)>=0); mi.textContent=(BTR_CFG.strategies.indexOf(v)>=0?'✓ ':'')+mi.textContent.replace(/^✓ /,''); }
    btStrategyLabel();
    var m=e?e.target.closest('.acct-menu'):null; if(m)m.classList.remove('open');
    return;
  }
  if(kind==='period'){BTR_CFG.period=v;BTR_CFG.customStart=null;BTR_CFG.customEnd=null;document.getElementById('btr-period-t').textContent=label;}
  if(kind==='capital'){BTR_CFG.capital=parseInt(v,10);document.getElementById('btr-capital-t').textContent=label;}
  if(kind==='mode'){
    BTR_CFG.mode=v;
    var modeNames={vectorized:'日频向量化',minute:'分钟级',tick:'Tick 完全仿真'};
    document.getElementById('btr-mode-t').textContent=modeNames[v]||v;
    var note=document.getElementById('btr-mode-note');
    if(note)note.textContent=v==='tick'
      ?'Tick 完全仿真：c1_market.tick_data 逐tick回放（3秒粒度）+5档盘口撮合——数据量大（6个月×5票≈百万tick，跑数分钟属正常），完成后自动载入'
      :(v==='minute'
        ?'分钟级：日频信号 × kline_1min 分钟价格路径逐 bar 撮合——比日频保真（用当日真实分钟价），比 tick 快'
        :'日频向量化（快速筛选）；三档保真度：日频 < 分钟 < tick');
  }
  var sel=e?e.target.parentNode:null;
  if(sel&&sel.parentNode){sel.parentNode.querySelectorAll('.acct-mi').forEach(function(mi){mi.classList.remove('on');});sel.classList.add('on');}
  var m=e?e.target.closest('.acct-menu'):null;if(m)m.classList.remove('open');
  if(kind==='period'){ btrSyncDateInputs(); }
}
function btrCustomDate(){
  var s=document.getElementById('btr-date-start'),en=document.getElementById('btr-date-end');
  if(!s||!en)return;
  if(s.value&&en.value&&s.value<=en.value){
    BTR_CFG.customStart=s.value;BTR_CFG.customEnd=en.value;
    BTR_CFG.period='custom';
    document.getElementById('btr-period-t').textContent=s.value.slice(5)+' ~ '+en.value.slice(5);
  }
}
function btrSyncDateInputs(){
  var span=btrPeriodSpan(BTR_CFG.period);
  var s=document.getElementById('btr-date-start'),en=document.getElementById('btr-date-end');
  if(s)s.value=span.start; if(en)en.value=span.end;
}
function btrPeriodSpan(key){
  if(key==='custom'&&BTR_CFG.customStart&&BTR_CFG.customEnd){
    return {start:BTR_CFG.customStart,end:BTR_CFG.customEnd};
  }
  var end=new Date();
  var months={m3:3,m6:6,y1:12,y2:24}[key]||6;
  var start=new Date(end.getFullYear(),end.getMonth()-months,end.getDate());
  function f(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
  return {start:f(start),end:f(end)};
}
var btrBusy=false;
function btrRun(){
  if(btrBusy)return; btrBusy=true;
  var btn=document.getElementById('btr-btn');
  var wrap=document.getElementById('btr-prog-wrap');
  var fill=document.getElementById('btr-prog-fill');
  var st=document.getElementById('btr-status');
  if(!btn||!wrap||!fill||!st){btrBusy=false;return;}
  var api=btApi(); if(!api){btrBusy=false;return;}
  var span=btrPeriodSpan(BTR_CFG.period);
  var modeNames={vectorized:'日频向量化',minute:'分钟级',tick:'Tick 完全仿真'};
  var modeName=modeNames[BTR_CFG.mode]||BTR_CFG.mode;
  var body={strategies:BTR_CFG.strategies.slice(),symbols:['600519.SH','000858.SZ','601318.SH','600036.SH','000001.SZ'],start:span.start,end:span.end,top_n:3,initial_capital:BTR_CFG.capital,mode:BTR_CFG.mode};
  btn.classList.remove('primary');
  btn.textContent='提交中… Submitting';
  fill.style.transition='none'; fill.style.width='0%';
  wrap.style.display='block';
  var slow=(BTR_CFG.mode==='tick')?'（tick 数据量大，跑数分钟属正常，勿重复点击）':(BTR_CFG.mode==='minute'?'（分钟数据中等，约几十秒）':'');
  st.textContent='POST /api/backtest-run（'+BTR_CFG.strategies.join('+')+' · '+span.start+' ~ '+span.end+' · '+(BTR_CFG.capital/10000)+'万 · '+modeName+'，后台串行）…'+slow;
  var t0=Date.now();
  api.postBacktestRun(body).then(function(r){
    if(!r||!r.ok||!r.task_id){throw new Error(r&&r.error||'submit failed');}
    BT_STATE.taskId=r.task_id;
    btn.textContent='运行中… Running';
    fill.style.transition=''; fill.style.width='60%';
    st.textContent='回测运行中（引擎：因子计算→合成→权重面板→逐日撮合→落盘）…';
    var poll=function(){
      api.fetchBacktestRunStatus(BT_STATE.taskId).then(function(s){
        if(s&&s.status==='done'){
          fill.style.width='100%';
          btn.textContent='✅ 完成'; setTimeout(function(){btn.classList.add('primary');btn.textContent='▶ 发起回测';},3000);
          var runs=(s.run_ids&&s.run_ids.length)?s.run_ids:(s.run_id?[s.run_id]:[]);
          var runsTxt=runs.map(function(rid){return '<b>'+rid+'</b>';}).join('、');
          st.innerHTML='✅ 完成——产物 '+runsTxt+'（'+(s.mode==='tick'?'Tick 完全仿真':'向量化')+'，净值 '+s.equity_points+' 点 / 成交 '+s.trades+' 笔），已自动载入';
          btrBusy=false;
          api.fetchBacktestList().then(function(r2){if(r2&&r2.ok){btRenderRunList(r2.data||[]);}});
          if(runs.length)btLoadDetail(runs[0]);
          var k=document.getElementById('bt-kpi'); if(k&&k.scrollIntoView)k.scrollIntoView({behavior:'smooth',block:'start'});
        }else if(s&&s.status==='failed'){
          btn.classList.add('primary'); btn.textContent='▶ 发起回测';
          st.textContent='❌ 失败：'+(s.error||'unknown')+'（可重试）';
          fill.style.width='100%';
          btrBusy=false;
        }else{
          var el=Math.round((Date.now()-t0)/1000);
          st.textContent='回测运行中…已 '+el+'s（'+modeName+'，每 3s 轮询'+(BTR_CFG.mode==='tick'?'；tick 海量数据属正常':'')+'）';
          fill.style.width=(50+Math.min(40,el/6))+'%';   /* 缓慢爬升（时间驱动伪进度）：60% 后每 6s +1%，到 90% 封顶——完成/失败立即 100% */
          BT_STATE.timer=setTimeout(poll,3000);
        }
      }).catch(function(){
        btn.classList.add('primary'); btn.textContent='▶ 发起回测';
        st.textContent='❌ 轮询失败（API 断线）——可重试';
        btrBusy=false;
      });
    };
    BT_STATE.timer=setTimeout(poll,2000);
  }).catch(function(e){
    btn.classList.add('primary'); btn.textContent='▶ 发起回测';
    st.textContent='❌ 发起失败：'+(e&&e.message||e);
    btrBusy=false;
  });
}
btBoot();
/* ---- 交互实测修复：回测每日明细日期下钻（btDailyXxx，3 演示日） ---- */
var BT_DAILY={
 '2019-01-02':{
   cap:[['日期','2019-01-02'],['总资产 Total Asset','¥9,991,268.26'],['资金余额 Cash Balance','¥5,713,755.51'],['当日持仓 Position Value','¥4,277,512.75'],['浮动盈亏 Float PnL','<span class="up">¥+118,972.20</span>'],['当日盈亏 Daily PnL','<span class="down">¥-8,724.12</span>'],['买开金额 Buy Open','¥41,172.72'],['买平金额 Buy Close','¥0.00'],['卖开金额 Sell Open','¥0.00'],['卖平金额 Sell Close','¥0.00'],['手续费 Fee','¥191.91']],
   pos:[['000001.SZ','long','2,051','48.901','49.16','¥100,828','<span class="up">+532</span>'],['600000.SH','long','695','320.50','320.18','¥222,525','<span class="down">-224</span>'],['000300.SH','long','4,141','95.210','95.54','¥395,631','<span class="up">+1,359</span>']],
   ord:[['2019-01-02 00:00:00','000001.SZ','标的000001','<span class="up">buy</span>','48.901','5,204','5,204','48.901','76.34','<span class="badge b-pass">FILLED</span>']]},
 '2019-02-11':{
   cap:[['日期','2019-02-11'],['总资产 Total Asset','¥10,124,880.05'],['资金余额 Cash Balance','¥6,208,412.33'],['当日持仓 Position Value','¥3,916,467.72'],['浮动盈亏 Float PnL','<span class="up">¥+142,310.55</span>'],['当日盈亏 Daily PnL','<span class="up">¥+17,845.20</span>'],['买开金额 Buy Open','¥0.00'],['买平金额 Buy Close','¥0.00'],['卖开金额 Sell Open','¥272,325.00'],['卖平金额 Sell Close','¥0.00'],['手续费 Fee','¥81.70']],
   pos:[['600000.SH','long','695','320.50','321.02','¥223,064','<span class="up">+361</span>'],['000300.SH','long','4,141','95.210','96.10','¥397,950','<span class="up">+3,684</span>']],
   ord:[['2019-02-11 00:00:00','000001.SZ','标的000001','<span class="down">sell</span>','52.330','5,204','5,204','52.330','81.70','<span class="badge b-pass">FILLED</span>']]},
 '2019-03-04':{
   cap:[['日期','2019-03-04'],['总资产 Total Asset','¥10,088,312.47'],['资金余额 Cash Balance','¥5,942,676.11'],['当日持仓 Position Value','¥4,145,636.36'],['浮动盈亏 Float PnL','<span class="up">¥+128,540.18</span>'],['当日盈亏 Daily PnL','<span class="down">¥-3,112.64</span>'],['买开金额 Buy Open','¥265,636.00'],['买平金额 Buy Close','¥0.00'],['卖开金额 Sell Open','¥0.00'],['卖平金额 Sell Close','¥0.00'],['手续费 Fee','¥79.69']],
   pos:[['000001.SZ','long','5,300','50.120','50.86','¥269,558','<span class="up">+3,922</span>'],['600000.SH','long','695','320.50','319.44','¥222,013','<span class="down">-737</span>'],['000300.SH','long','4,141','95.210','95.88','¥397,001','<span class="up">+2,774</span>']],
   ord:[['2019-03-04 00:00:00','000001.SZ','标的000001','<span class="up">buy</span>','50.120','5,300','5,300','50.120','79.69','<span class="badge b-pass">FILLED</span>']]}
};
function btDailyRender(dt){
  var d=BT_DAILY[dt]; if(!d)return;
  document.getElementById('bt-cap-title').textContent='当日资金 Daily Capital ('+dt+')';
  document.getElementById('bt-pos-title').textContent='当日持仓 Daily Positions ('+dt+')';
  document.getElementById('bt-ord-title').textContent='当日委托 Daily Orders ('+dt+')';
  var h='<tr><th style="width:30%">字段 Field</th><th>值 Value</th></tr>';
  d.cap.forEach(function(r){h+='<tr><td>'+r[0]+'</td><td>'+r[1]+'</td></tr>';});
  document.getElementById('bt-cap-table').innerHTML=h;
  h='<tr><th>代码 Symbol</th><th>方向 Side</th><th>数量 Qty</th><th>均价 VWAP</th><th>当前价 Price</th><th>市值 Market Value</th><th>浮动盈亏 Float PnL</th></tr>';
  d.pos.forEach(function(r){h+='<tr><td>'+r.join('</td><td>')+'</td></tr>';});
  document.getElementById('bt-pos-table').innerHTML=h;
  h='<tr><th>委托时间 Order Time</th><th>代码 Symbol</th><th>名称 Name</th><th>方向 Side</th><th>价格 Price</th><th>数量 Qty</th><th>已成交 Filled</th><th>均价 Avg Price</th><th>手续费 Fee</th><th>状态 Status</th></tr>';
  d.ord.forEach(function(r){h+='<tr><td>'+r.join('</td><td>')+'</td></tr>';});
  document.getElementById('bt-ord-table').innerHTML=h;
}
function btDateTgl(e){e.stopPropagation();var m=document.getElementById('bt-date-menu');if(m)m.classList.toggle('open');}
function btDailySet(dt,e){
  if(e&&e.stopPropagation)e.stopPropagation();
  document.getElementById('bt-date-t').textContent=dt;
  document.querySelectorAll('#bt-date-menu .acct-mi').forEach(function(mi){mi.classList.toggle('on',mi.textContent===dt);});
  var m=document.getElementById('bt-date-menu');if(m)m.classList.remove('open');
  btDailyRender(dt);
}
document.addEventListener('click',function(e){var s=document.getElementById('bt-date-sel');var m=document.getElementById('bt-date-menu');if(s&&m&&!s.contains(e.target))m.classList.remove('open');});
btDailyRender('2019-01-02');
