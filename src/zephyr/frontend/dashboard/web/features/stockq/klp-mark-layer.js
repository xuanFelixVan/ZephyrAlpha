/* 功能模块：主图标注层（klp-mark-layer）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：overlay 分组（bs/trade/chip/evt/cost）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L6198-6357），逻辑零改动。
 * 验收单：ACC-F-STOCKQ-MARK-LAYER
 */
/* ==================== v4.4 主图标注层（量化买卖点/真实成交/筹码峰+成本线/事件图标——overlay 分组实现，与画线 draw 组隔离互不干扰） ==================== */
var klpMarks={bs:true,trade:true,chip:true,evt:true,cost:true};   /* 标注开关状态（cost=黄色成本线独立开关，与筹码峰分布模块分开控制） */
function klpTglMark(k,btn){
  klpMarks[k]=!klpMarks[k];
  if(btn) btn.classList.toggle('on',klpMarks[k]);
  klpRefreshMarks();
}
function klpRefreshMarks(){
  if(!klpChart) return;
  klpChart.removeOverlay({groupId:'marks'});
  klpChart.removeOverlay({groupId:'trades'});
  klpChart.removeOverlay({groupId:'chip'});
  klpChart.removeOverlay({groupId:'cost'});
  setTimeout(function(){   /* 等 setSymbol/setPeriod 触发的 dataLoader 回调落数 */
    if(!klpChart) return;
    var d=klpChart.getDataList?klpChart.getDataList():[];
    if(!d.length) return;
    if(klpMarks.bs) klpRenderBS(d);
    if(klpMarks.trade) klpRenderTrades(d);
    if(klpMarks.cost && window.ZK && ZK.features['cost-line']) ZK.features['cost-line'].render(d);   /* 黄色成本线独立开关（¥）——已模块化（features/cost-line.js） */
    /* 筹码峰独立模块显隐（collapsed 切换影响中栏宽度，需 resize） */
    var chipWrap=document.getElementById('klp-chip');
    if(chipWrap){
      var wasCollapsed=chipWrap.classList.contains('collapsed');
      chipWrap.classList.toggle('collapsed',!klpMarks.chip);
      if(wasCollapsed===klpMarks.chip) setTimeout(function(){ if(klpChart) klpChart.resize(); },220);
    }
    if(klpMarks.chip) klpRenderChip(d);
    /* ⚑ 事件开关=事件行整行模块收展（高度收掉让 K 线变大；时间轴不受影响常显） */
    var evtRow=document.getElementById('klp-evtrow');
    if(evtRow){
      var evWasCollapsed=evtRow.classList.contains('collapsed');
      evtRow.classList.toggle('collapsed',!klpMarks.evt);
      if(evWasCollapsed===klpMarks.evt) setTimeout(function(){ if(klpChart) klpChart.resize(); },220);
    }
    klpTimelineRender();   /* 事件图标只在事件行显示（K 线上不再铺，v4.6） */
  },0);
}
/* 量化买卖点：±3 摆动高低点（旧版 sqBS 同口径），深灰底气泡框弱提示（与真实成交红绿强提示区分） */
function klpRenderBS(d){
  for(var i=3;i<d.length-3;i++){
    var isLo=true,isHi=true;
    for(var j=i-3;j<=i+3;j++){ if(j===i)continue; if(d[j].low<d[i].low)isLo=false; if(d[j].high>d[i].high)isHi=false; }
    if(!isLo&&!isHi) continue;
    klpChart.createOverlay({
      name:'simpleAnnotation', groupId:'marks', lock:true,
      points:[{timestamp:d[i].timestamp,value:isLo?d[i].low:d[i].high}],
      extendData:isLo?'▲买':'▼卖',
      styles:{text:{color:'#EDEFF2',size:11,backgroundColor:'#3A4048',borderColor:'#4A5058',borderSize:1,borderRadius:3,paddingLeft:4,paddingRight:4,paddingTop:2,paddingBottom:2}}
    });
  }
}
/* 真实成交买卖点：演示口径确定性成交点（交替买卖），与量化买卖点同形态气泡框，B=红底买入 S=绿底卖出 */
function klpTradePoints(d){
  var r=lcg(+sqCur*7+13),n=4+Math.floor(r()*3),pts=[];
  for(var k=0;k<n;k++){ pts.push({i:10+Math.floor(r()*(d.length-20))}); }
  pts.sort(function(a,b){return a.i-b.i;});
  pts.forEach(function(p,k){ p.dir=(k%2===0)?1:-1; });   /* 按时间排序后交替：先买后卖 */
  return pts;
}
function klpRenderTrades(d){
  klpTradePoints(d).forEach(function(t){
    var k=d[t.i],isB=t.dir>0;
    klpChart.createOverlay({
      name:'simpleAnnotation', groupId:'trades', lock:true,
      points:[{timestamp:k.timestamp,value:isB?k.low:k.high}],
      extendData:isB?'B':'S',
      styles:{text:{color:'#FFFFFF',size:10,backgroundColor:isB?'#CA3F64':'#25A750',borderRadius:3,paddingLeft:5,paddingRight:5,paddingTop:2,paddingBottom:2}}
    });
  });
}
/* 成本线已迁入功能模块 features/cost-line.js（模块契约 pilot，验收单 ACC-F-STOCKQ-COSTLINE）；¥ 开关状态仍由 klpMarks.cost 持有，渲染触发见 klpRefreshMarks */
/* 筹码峰：独立模块刷新（canvas 分布图+信息面板；主图黄线已拆到 klpRenderCostLine，由 ¥ 独立开关） */
function klpRenderChip(d){
  klpChipRender(d.length-1);
}
/* 筹码分布计算（48 桶；百分位区间/集中度/重合度/POC/平均成本——演示口径） */
function klpChipCalc(d,upto){
  var lo=1e18,hi=-1e18,i;
  for(i=0;i<=upto;i++){ lo=Math.min(lo,d[i].low); hi=Math.max(hi,d[i].high); }
  if(!(hi>lo)) hi=lo+0.01;
  var NB=48,bw=(hi-lo)/NB,bins=[];
  for(i=0;i<NB;i++) bins.push(0);
  var sumPV=0,sumV=0;
  for(i=0;i<=upto;i++){
    var tp=(d[i].high+d[i].low+d[i].close)/3,v=d[i].volume||0;
    var bi=Math.floor((tp-lo)/bw); if(bi<0)bi=0; if(bi>=NB)bi=NB-1;
    bins[bi]+=v; sumPV+=tp*v; sumV+=v;
  }
  var tot=sumV||1;
  var refPx=d[upto].close,prof=0;
  for(i=0;i<NB;i++) if(lo+(i+0.5)*bw<=refPx) prof+=bins[i];
  function pct(p){ var target=tot*p,acc=0; for(var j=0;j<NB;j++){ acc+=bins[j]; if(acc>=target) return lo+(j+0.5)*bw; } return hi; }
  var p5=pct(0.05),p95=pct(0.95),p15=pct(0.15),p85=pct(0.85);
  var c90=(p95-p5)/(p95+p5)*100,c70=(p85-p15)/(p85+p15)*100;
  var in90=0,in70=0;
  for(i=0;i<NB;i++){ var mid=lo+(i+0.5)*bw; if(mid>=p5&&mid<=p95) in90+=bins[i]; if(mid>=p15&&mid<=p85) in70+=bins[i]; }
  var poc=0,bmax=0;
  for(i=0;i<NB;i++) if(bins[i]>bmax){bmax=bins[i];poc=i;}
  return {lo:lo,hi:hi,bins:bins,bw:bw,bmax:bmax,pocPx:lo+(poc+0.5)*bw,refPx:refPx,profit:prof/tot*100,avgCost:sumPV/tot,p90:[p5,p95],c90:c90,p70:[p15,p85],c70:c70,overlap:in90>0?in70/in90*100:0};
}
/* 独立筹码峰模块渲染（K 线与右栏之间：canvas 分布图 + 下方信息面板白字无框；upto=光标日，默认末日） */
function klpChipRender(upto){
  var wrap=document.getElementById('klp-chip'); if(!wrap||!klpChart) return;
  var d=klpChart.getDataList?klpChart.getDataList():[]; if(!d.length) return;
  if(upto==null) upto=d.length-1;
  upto=Math.max(0,Math.min(d.length-1,upto));
  var c=klpChipCalc(d,upto);
  /* canvas 分布图 */
  var cv=document.getElementById('klp-chip-canvas');
  if(cv){
    var box=cv.parentElement.getBoundingClientRect();
    if(box.width>0&&box.height>0){
      var dpr=window.devicePixelRatio||1;
      cv.width=Math.round(box.width*dpr); cv.height=Math.round(box.height*dpr);
      cv.style.width=box.width+'px'; cv.style.height=box.height+'px';
      var ctx=cv.getContext('2d'); ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,box.width,box.height);
      var W=box.width,H=box.height,padT=4,padB=4;
      var yf=function(px){ return padT+(1-(px-c.lo)/(c.hi-c.lo))*(H-padT-padB); };
      for(var i=0;i<48;i++){
        if(c.bins[i]<=0) continue;
        var y2=yf(c.lo+i*c.bw),y1=yf(c.lo+(i+1)*c.bw);
        var isP=c.lo+(i+0.5)*c.bw<=c.refPx;
        ctx.fillStyle=isP?'rgba(202,63,100,0.55)':'rgba(37,167,80,0.55)';
        ctx.fillRect(0,y1,Math.max(1,(c.bins[i]/c.bmax)*(W-36)),Math.max(1,y2-y1-0.5));
      }
      /* POC 成本线 + 右端价格标签（DOM，hover 显示"成本价格"） */
      var pocY=yf(c.pocPx);
      ctx.strokeStyle='#F0B90B'; ctx.lineWidth=1.2; ctx.setLineDash([5,3]);
      ctx.beginPath(); ctx.moveTo(0,pocY); ctx.lineTo(W,pocY); ctx.stroke(); ctx.setLineDash([]);
      var tag=document.getElementById('klp-chip-poc');
      if(tag){ tag.textContent=c.pocPx.toFixed(2); tag.style.top=Math.max(0,pocY-8)+'px'; }
    }
  }
  /* 信息面板（白字无框，截图口径） */
  var info=document.getElementById('klp-chip-info');
  if(info){
    var t=new Date(d[upto].timestamp);
    var ds=t.getFullYear()+'/'+String(t.getMonth()+1).padStart(2,'0')+'/'+String(t.getDate()).padStart(2,'0');
    info.innerHTML='<div class="ci-row"><span>时间</span><b>'+ds+'</b></div>'
      +'<div class="ci-row"><span>收盘获利</span><b>'+c.profit.toFixed(2)+'%</b></div>'
      +'<div class="ci-row"><span>平均成本</span><b>'+c.avgCost.toFixed(2)+'</b></div>'
      +'<div class="ci-sec"><i style="background:#8B949E"></i>90%成本</div>'
      +'<div class="ci-row2"><span>'+c.p90[0].toFixed(2)+' ~ '+c.p90[1].toFixed(2)+'</span><b>集中度 '+c.c90.toFixed(2)+'%</b></div>'
      +'<div class="ci-sec"><i style="background:#F0B90B"></i>70%成本</div>'
      +'<div class="ci-row2"><span>'+c.p70[0].toFixed(2)+' ~ '+c.p70[1].toFixed(2)+'</span><b>集中度 '+c.c70.toFixed(2)+'%</b></div>'
      +'<div class="ci-bar"><i style="width:'+Math.min(100,c.overlap).toFixed(0)+'%"></i><span>重合度 '+c.overlap.toFixed(2)+'%</span></div>'
      +'<div class="ci-row"><span>价格区间</span><b>'+c.lo.toFixed(2)+'~'+c.hi.toFixed(2)+'</b></div>';
  }
}
/* 事件图标：v4.6 起只在时间轴模块显示（K 线上不再铺），渲染逻辑见 klpTimelineRender */
function klpFindBar(d,dtStr){   /* dtStr='08-21' 或 '08-26 20:30' → 归一化取前 5 位日期匹配该日历日 K 线索引 */
  var target='2026-'+dtStr.slice(0,5);
  for(var i=d.length-1;i>=0;i--){
    var t=new Date(d[i].timestamp);
    var s=t.getFullYear()+'-'+String(t.getMonth()+1).padStart(2,'0')+'-'+String(t.getDate()).padStart(2,'0');
    if(s===target) return i;
  }
  return -1;
}
