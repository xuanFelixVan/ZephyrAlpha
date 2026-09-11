/* 功能模块：指标设置弹窗（klp-indicator-dialog）
 * 契约：页面引擎模块——全局函数族原样迁出（页面 onclick 直接绑定全局名，零改名）；
 *       非 registerFeature 组件（Tier-2 契约化待数据源接通时逐件做，见拆件清单 2026-09-12）。
 * 数据源：纯前端交互（参数/颜色编辑）
 * 来源：2026-09-12 拆件批自 core/app1.js 原行段迁出（L6511-6798），逻辑零改动。
 * 验收单：ACC-F-STOCKQ-INDICATOR-DIALOG
 */
/* ==================== 指标设置弹窗（v4.4 欧易式：主图/副图 tab + 参数/颜色编辑 + 重置确认） ==================== */
var KLP_IND_MAIN=['MA','EMA','BOLL','SAR','AVL','VWAP'];   /* 主图叠加候选 */
var KLP_IND_SUB=['VOL','MACD','KDJ','RSI','DMI','OBV','WR','CCI','BIAS','DMA','TRIX','BRAR','EMV','ROC','MTM','PSY','AO'];   /* 副图窗格候选 */
var KLP_IND_DEF={MA:[5,10,20,30,60],EMA:[5,10,20,30,60],BOLL:[20,2],SAR:[2,2,20],AVL:[],VWAP:[],VOL:[5,10,20],MACD:[12,26,9],KDJ:[9,3,3],RSI:[6,12,24],DMI:[14,6],OBV:[30],WR:[14,6],CCI:[13],BIAS:[6,12,24],DMA:[10,50,10],TRIX:[12,9],BRAR:[26],EMV:[14,9],ROC:[12,6],MTM:[6,10],PSY:[12,6],AO:[5,34]};   /* 默认 calcParams（重置用） */
var klpIndTabMode='main',klpIndSel='MA';
/* 逐线编辑配置（v4.5：每条线=勾选+周期+线型+颜色；localStorage 记忆） */
var KLP_LINE_IND={MA:true,EMA:true};   /* 线型指标：figures=lines 且数量=calcParams 数量，支持逐线编辑 */
var KLP_LINE_COLORS=['#FFA726','#EC407A','#27C6DA','#3D8BFF','#AB47BC','#7CB342','#F0B90B'];
var KLP_IND_CFG; try{ KLP_IND_CFG=JSON.parse(localStorage.getItem('zk-klp-indcfg')||'null')||{}; }catch(e){ KLP_IND_CFG={}; }
function klpIndCfg(name){
  if(!KLP_IND_CFG[name]){
    var params=(KLP_IND_DEF[name]||[]).slice();
    KLP_IND_CFG[name]={params:params,on:params.map(function(){return true;}),colors:params.map(function(_,i){return KLP_LINE_COLORS[i%7];}),styles:params.map(function(){return 'solid';})};
  }
  var cfg=KLP_IND_CFG[name];
  while(cfg.on.length<cfg.params.length){ cfg.on.push(true); cfg.colors.push(KLP_LINE_COLORS[cfg.on.length%7]); cfg.styles.push('solid'); }   /* 兼容参数扩容 */
  return cfg;
}
function klpIndCfgSave(){ try{localStorage.setItem('zk-klp-indcfg',JSON.stringify(KLP_IND_CFG));}catch(e){} }
function klpIndSpec(name){   /* 由配置生成 createIndicator/overrideIndicator 参数（剔除未勾选线） */
  var cfg=klpIndCfg(name),params=[],lines=[];
  cfg.params.forEach(function(p,i){ if(cfg.on[i]){ params.push(p); lines.push({color:cfg.colors[i],style:cfg.styles[i]}); } });
  var spec={name:name,calcParams:params};
  if(KLP_LINE_IND[name]) spec.styles={lines:lines};
  return spec;
}
function klpIndApply(name){
  if(!klpIndActive(name)) return;
  var spec=klpIndSpec(name);
  if(!spec.calcParams.length){ sqToast(name+' 至少保留 1 条线'); return; }
  klpChart.overrideIndicator(spec);
}
function klpIndPop(){
  var pop=document.getElementById('klp-indpop'); if(!pop) return;
  document.getElementById('ip-tab-main').classList.toggle('on',klpIndTabMode==='main');   /* 同步 tab 高亮（图上齿轮直达时已定位） */
  document.getElementById('ip-tab-sub').classList.toggle('on',klpIndTabMode==='sub');
  pop.style.display='block';
  klpIndRenderList(); klpIndRenderDetail();
}
function klpIndPopClose(){ var pop=document.getElementById('klp-indpop'); if(pop) pop.style.display='none'; }
function klpIndTab(m){
  klpIndTabMode=m;
  document.getElementById('ip-tab-main').classList.toggle('on',m==='main');
  document.getElementById('ip-tab-sub').classList.toggle('on',m==='sub');
  klpIndSel=(m==='main'?KLP_IND_MAIN[0]:KLP_IND_SUB[0]);
  klpIndRenderList(); klpIndRenderDetail();
}
function klpIndActive(name){   /* 该指标当前是否已启用 */
  return klpChart?klpChart.getIndicators().some(function(i){return i.name===name;}):false;
}
function klpIndRenderList(){
  var box=document.getElementById('ip-list'); if(!box) return;
  var pool=klpIndTabMode==='main'?KLP_IND_MAIN:KLP_IND_SUB;
  box.innerHTML=pool.map(function(name){
    var on=klpIndActive(name);
    return '<div class="ip-item'+(name===klpIndSel?' sel':'')+'" onclick="klpIndSelSet(\''+name+'\')">'
      +'<span class="ip-ck'+(on?' on':'')+'" onclick="event.stopPropagation();klpToggleInd(\''+name+'\');klpIndRenderList();klpIndRenderDetail();">'+(on?'✓':'')+'</span>'
      +'<span class="nm">'+name+'</span><span class="ar">›</span></div>';
  }).join('');
}
function klpIndSelSet(name){ klpIndSel=name; klpIndRenderList(); klpIndRenderDetail(); }
function klpIndRenderDetail(){
  var box=document.getElementById('ip-detail'); if(!box) return;
  var name=klpIndSel,on=klpIndActive(name),cfg=klpIndCfg(name),isLine=KLP_LINE_IND[name]===true;
  if(!cfg.params.length){ box.innerHTML='<div class="ip-none">'+name+' 无可调参数</div>'; return; }
  var h='<div class="ip-dt">'+name+' 参数设置'+(on?'':'（未启用，勾选左侧启用后生效）')+'</div>';
  cfg.params.forEach(function(v,idx){
    h+='<div class="ip-row">'
      +'<span class="ip-ck'+(cfg.on[idx]?' on':'')+'" title="显示/隐藏该线" onclick="klpIndLineTgl('+idx+')">'+(cfg.on[idx]?'✓':'')+'</span>'
      +'<span class="k">'+(isLine?(name+(idx+1)):'参数 '+(idx+1))+'</span>'
      +'<input type="number" class="ip-num" value="'+v+'" min="1" max="500" onchange="klpIndParamSet('+idx+',this.value)">';
    if(isLine){
      h+='<select class="ip-style" onchange="klpIndStyleSet('+idx+',this.value)">'
        +'<option value="solid"'+(cfg.styles[idx]==='solid'?' selected':'')+'>实线</option>'
        +'<option value="dashed"'+(cfg.styles[idx]==='dashed'?' selected':'')+'>虚线</option></select>'
        +'<input type="color" class="ip-color" value="'+cfg.colors[idx]+'" onchange="klpIndColorSet('+idx+',this.value)">';
    }
    h+='</div>';
  });
  box.innerHTML=h;
}
function klpIndParamSet(idx,val){
  var name=klpIndSel,v=parseInt(val,10);
  if(!(v>=1)) return;
  var cfg=klpIndCfg(name); cfg.params[idx]=v; klpIndCfgSave();
  klpIndApply(name);
  sqToast(name+' 参数 '+(idx+1)+' → '+v);
}
function klpIndLineTgl(idx){ var cfg=klpIndCfg(klpIndSel); cfg.on[idx]=!cfg.on[idx]; klpIndCfgSave(); klpIndApply(klpIndSel); klpIndRenderDetail(); }
function klpIndStyleSet(idx,v){ var cfg=klpIndCfg(klpIndSel); cfg.styles[idx]=v; klpIndCfgSave(); klpIndApply(klpIndSel); }
function klpIndColorSet(idx,v){ var cfg=klpIndCfg(klpIndSel); cfg.colors[idx]=v; klpIndCfgSave(); klpIndApply(klpIndSel); }
function klpIndReset(){
  var name=klpIndSel;
  delete KLP_IND_CFG[name]; klpIndCfgSave();
  klpIndApply(name);
  klpIndRenderDetail();
  sqToast(name+' 已重置为默认参数');
}
function sqListTab(m){
  sqListMode=m;
  sqStateSave();
  document.getElementById('sq-tab-fav').classList.toggle('on',m==='fav');
  document.getElementById('sq-tab-hold').classList.toggle('on',m==='hold');
  sqRenderList();
}
function sqRenderList(){
  /* v3：搜索模式由 sq-search-box 组件接管；自选/持仓列表分别由 sq-fav-list / sq-position-list 组件接管
     （features/stockq/），组件未加载时回退本函数老代码路径（兼容旧加载链） */
  var q=((document.getElementById('sq-srch')||{}).value||'').trim();
  if(q && window.ZK && ZK.features && ZK.features['sq-search-box']){
    /* 有搜索词且组件已加载：组件已接管 input 事件，无需重复渲染 */
    return;
  }
  if(!q && window.ZK && ZK.features){
    if(sqListMode==='fav' && ZK.features['sq-fav-list']){ ZK.features['sq-fav-list'].render(); return; }
    if(sqListMode==='hold' && ZK.features['sq-position-list']){ ZK.features['sq-position-list'].render(); return; }
  }
  var items=sqListMode==='fav'?sqFav:SQ_HOLD,h='';
  items.forEach(function(sym){
    var p=sqPoolFind(sym); if(!p)return;
    if(q&&p.nm.indexOf(q)<0&&p.code.indexOf(q)<0) return;
    h+='<div class="sq-si'+(sym===sqCur?' on':'')+'" onclick="sqSel(\''+sym+'\')"><span><span class="nm">'+p.nm+'</span> <span class="cd">'+p.code+'</span></span>'
      +'<span class="rt"><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><br><span class="pc '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></span>'
      +(sqListMode==='fav'?'<span class="fav" onclick="event.stopPropagation();sqFavRm(\''+sym+'\')" title="移出自选">✕</span>':'')+'</div>';
  });
  /* 搜索模式补充：池内未入当前清单的匹配项，可一键加自选（v4.4） */
  if(q){
    SQ_POOL.forEach(function(p){
      if(items.indexOf(p.sym)>=0) return;
      if(p.nm.indexOf(q)<0&&p.code.indexOf(q)<0) return;
      h+='<div class="sq-si'+(p.sym===sqCur?' on':'')+'" onclick="sqSel(\''+p.sym+'\')"><span><span class="nm">'+p.nm+'</span> <span class="cd">'+p.code+'</span></span>'
        +'<span class="rt"><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><br><span class="pc '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></span>'
        +'<span class="fav" onclick="event.stopPropagation();sqFavAdd(\''+p.sym+'\')" title="加入自选">＋</span></div>';
    });
  }
  document.getElementById('sq-list').innerHTML=h||'<div class="sq-intro">清单为空或无匹配</div>';
}

/* 搜索组件桥接：从搜索结果选中股票（不在池内时先临时加入池） */
function sqSelFromSearch(sym){
  if(typeof sqPoolFind==='function' && !sqPoolFind(sym)){
    SQ_POOL.push({sym:sym, nm:sym, code:sym, px:'--', pc:'--', dir:0});
  }
  if(typeof sqSel==='function') sqSel(sym);
}
function sqFavAdd(sym){
  if(sqFav.indexOf(sym)<0) sqFav.push(sym);
  try{localStorage.setItem('zk-sq-fav',JSON.stringify(sqFav));}catch(e){}
  sqToast('已加入自选：'+sqPoolFind(sym).nm);
  sqRenderList();
}
function sqFavRm(sym){
  sqFav=sqFav.filter(function(s){return s!==sym;});
  try{localStorage.setItem('zk-sq-fav',JSON.stringify(sqFav));}catch(e){}
  sqRenderList();
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
  /* 组件接管判定（features/stockq/）：行业标签→sq-sector-tags、关键数据→sq-key-data、五档→sq-order-book */
  var hasTags=!!(window.ZK && ZK.features && ZK.features['sq-sector-tags']);
  var hasKv=!!(window.ZK && ZK.features && ZK.features['sq-key-data']);
  var hasOb=!!(window.ZK && ZK.features && ZK.features['sq-order-book']);
  var hasQa=!!(window.ZK && ZK.features && ZK.features['sq-quant-analysis']);
  if(!d){
    if(!p) p={nm:sqCur,code:sqCur,px:'--',pc:'--',dir:0};
    box.innerHTML='<div class="sq-qh"><span class="nm">'+p.nm+'</span><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><span class="chg '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></div>'
      +'<div class="sq-tags" id="sq-sector-tags">'+(hasTags?'':'<span class="badge b-na">行业待接入</span>')+'</div>'
      +'<div id="sq-order-book"></div>'
      +'<div id="sq-key-data">'+(hasKv?'':'<div class="sq-sec"><span>关键数据</span></div><div class="sq-intro">关键数据待接入（真源 /api/stock-header）</div>')+'</div>'
      +(hasQa?'<div id="sq-quant-analysis"></div>':'')
      +'<div class="sq-intro">「'+p.nm+'」股性/财务/新闻量化/合理估价演示数据未内置（关键数据/行业标签/五档/量化分析已接真源），K 线工作台可正常使用——其余资料待接入 I-2。</div>';
    if(hasTags) ZK.features['sq-sector-tags'].render();
    if(hasOb) ZK.features['sq-order-book'].render();
    if(hasKv) ZK.features['sq-key-data'].render();
    if(hasQa) ZK.features['sq-quant-analysis'].render();
    return;
  }
  var inFav=sqFav.indexOf(sqCur)>=0;
  var h='<div class="sq-qh"><span class="nm">'+p.nm+'</span><span class="cd" style="color:var(--faint);font-size:10px">'+p.code+'</span>'
    +'<span class="badge b-na">闭市</span>'
    +'<span class="sq-fb" style="margin-left:auto" onclick="event.stopPropagation();sqFavTgl(\''+sqCur+'\',this)">'+(inFav?'★ 删自选':'☆ 加自选')+'</span></div>'
    +'<div class="sq-qh"><span class="px '+(p.dir>=0?'up':'down')+'">'+p.px+'</span><span class="chg '+(p.dir>=0?'up':'down')+'">'+p.pc+'</span></div>'
    /* 行业标签：sq-sector-tags 组件接管（真源 stock_basic.industry/board），未加载回退演示 tags */
    +(hasTags?'<div class="sq-tags" id="sq-sector-tags"></div>':'<div class="sq-tags">'+d.tags.map(function(t){return '<span class="badge b-na">'+t+'</span>';}).join('')+'</div>')
    +'<div class="sq-intro">'+d.intro+'</div>';
  /* 五档：sq-order-book 组件接管（真源文件桥 quote.csv），未加载回退演示 l2 */
  if(hasOb){ h+='<div id="sq-order-book"></div>'; }
  else{
    h+='<div class="sq-sec"><span>五档挂单 <span class="dim" style="font-weight:400">miniQMT 五档快照口径（演示）</span></span></div><div class="sq-l2">';
    var vmax=0; d.l2.forEach(function(l){vmax=Math.max(vmax,l[1]);});
    var i;
    for(i=4;i>=0;i--){ h+='<div class="lr"><span style="color:var(--down)">卖'+(i+1)+'</span><span class="lbar"><i style="width:'+(d.l2[i][1]/vmax*100).toFixed(0)+'%;background:#25A750;opacity:.35"></i></span><span class="lp" style="color:var(--down)">'+d.l2[i][0].toFixed(2)+'</span><span class="lv">'+d.l2[i][1]+'</span></div>'; }
    for(i=5;i<10;i++){ h+='<div class="lr"><span style="color:var(--up)">买'+(i-4)+'</span><span class="lbar"><i style="width:'+(d.l2[i][1]/vmax*100).toFixed(0)+'%;background:#CA3F64;opacity:.35"></i></span><span class="lp" style="color:var(--up)">'+d.l2[i][0].toFixed(2)+'</span><span class="lv">'+d.l2[i][1]+'</span></div>'; }
    h+='</div>';
  }
  /* 关键数据：sq-key-data 组件接管（真源 kline_daily+daily_valuation），未加载回退演示 kv */
  if(hasKv){ h+='<div id="sq-key-data"></div>'; }
  else{
    h+='<div class="sq-sec"><span>关键数据</span></div><div class="sq-kv-grid">';
    d.kv.forEach(function(kv){ h+='<span class="k">'+kv[0]+'</span><span class="v" style="grid-column:span 2">'+kv[1]+'</span>'; });
    h+='</div>';
  }
  /* 量化分析：sq-quant-analysis 组件接管（真源 market_signal_history 双管道），未加载不显示 */
  if(hasQa){ h+='<div id="sq-quant-analysis"></div>'; }
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
  /* 组件接管渲染：行业标签+五档+关键数据+量化分析（容器已注入，异步取真源，失败回退上方演示标记） */
  if(hasTags) ZK.features['sq-sector-tags'].render();
  if(hasOb) ZK.features['sq-order-book'].render();
  if(hasKv) ZK.features['sq-key-data'].render();
  if(hasQa) ZK.features['sq-quant-analysis'].render();
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
function sqMAArr(d,p){   /* 简单均线数组版（页面全局 ma(d,n,i) 为逐点标量，四.A 需要全序列） */
  var r=[],s=0,i;
  for(i=0;i<d.length;i++){ s+=d[i].c; if(i>=p)s-=d[i-p].c; r.push(i>=p-1?s/p:s/(i+1)); }
  return r;
}
function sqEMA(arr,p){ var k=2/(p+1),r=[],v=arr[0]; for(var i=0;i<arr.length;i++){ v=i?arr[i]*k+v*(1-k):arr[i]; r.push(v); } return r; }
function sqMACD(d){ var c=d.map(function(x){return x.c;}),e12=sqEMA(c,12),e26=sqEMA(c,26),dif=c.map(function(v,i){return e12[i]-e26[i];}),dea=sqEMA(dif,9),h=dif.map(function(v,i){return (v-dea[i])*2;}); return {dif:dif,dea:dea,hist:h}; }
