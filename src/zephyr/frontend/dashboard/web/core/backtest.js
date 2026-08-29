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
function btCharts(){
  var B=btGen();
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
btCharts();
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
var btrBusy=false;
function btrRun(){
  if(btrBusy)return; btrBusy=true;
  var btn=document.getElementById('btr-btn');
  var wrap=document.getElementById('btr-prog-wrap');
  var fill=document.getElementById('btr-prog-fill');
  var st=document.getElementById('btr-status');
  if(!btn||!wrap||!fill||!st){btrBusy=false;return;}
  btn.classList.remove('primary');
  btn.textContent='排队中… Queued';
  fill.style.transition='none'; fill.style.width='0%';
  wrap.style.display='block';
  st.textContent='排队中…（演示：前端配置面板+状态轮询 mock，后端执行通道待接入）';
  setTimeout(function(){
    btn.textContent='运行中 42% Running';
    st.textContent='运行中 42%（演示进度动画，非真实回测）';
    fill.style.transition=''; fill.style.width='42%';
    setTimeout(function(){ fill.style.width='100%'; },80);
  },1500);
  setTimeout(function(){
    btn.textContent='✅ 完成（演示）';
    st.innerHTML='✅ 完成（演示）——真实发起通道待接入（I-2），下方结果为既有 <b>demo-perf-001</b> 演示数据';
    var k=document.getElementById('bt-kpi');
    if(k&&k.scrollIntoView) k.scrollIntoView({behavior:'smooth',block:'start'});
    btrBusy=false;
  },4500);
}
